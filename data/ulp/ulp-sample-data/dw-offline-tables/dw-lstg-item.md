# DW_LSTG_ITEM — Listing Item Table Reference

## Table Basics

| Property | Value |
|---|---|
| **Platform** | Hercules, Apollo |
| **DB** | GDW_TABLES |
| **Table name** | DW_LSTG_ITEM |
| **Access views** | `ACCESS_VIEWS.DW_LSTG_ITEM`, `BATCH_VIEWS.DW_LSTG_ITEM`, `PRS_SECURE_V.DW_LSTG_ITEM`, `PRS_CORE_EX_PII_V.DW_LSTG_ITEM` |
| **Data frequency** | Daily |
| **Data latency** | T-1 |
| **Primary key** | `ITEM_ID` |
| **Primary index** | `ITEM_ID` (PI), `SLR_ID` (NUSI), `AUCT_START_DT` (NUSI) |
| **Partition** | None |
| **Owner** | Zhang, Minghua (AWF) |
| **Latency priority** | P1 |
| **SLA time** | 7:00 AM |
| **Quality priority** | P1 |
| **DR enabled** | Y |
| **Source tables** | `EBAY_ITEMS`, `EBAY_ITEMS_ARC` |
| **Source teams** | DL-eBay-ListingRedesign@ebay.com, DL-eBay-CSPlatform-PD@ebay.com |
| **Related process** | Seller Listing |

**ETL code:**
- [dw_lstg.stg_items_freq_i_adpo.spark.sql](https://github.ebay.com/APD/DINT-CORE/blob/master/etl/sql/dw_lstg/dw_lstg.stg_items_freq_i_adpo.spark.sql)
- [Main logic](https://github.ebay.com/APD/DINT-CORE/blob/master/etl/sql/dw_lstg/dw_lstg.dw_lstg_item_w_combine_adpo_proc.spark.sql)

---

## Overview

In **Teradata**, this is the *hot* listing table containing the most frequently-used fields. Note: not all columns are here — flag columns (FLAGS\*) are in `DW_LSTG_ITEM_COLD`.

In **Hadoop/Apollo**, this table has **ALL** listing items.

### Related Tables

| Asset | Notes |
|---|---|
| `DW_LSTG_ITEM_COLD` | Cold listing data — flag columns, lot size, listing method, etc. |
| `DW_LSTG_ITEM_PROD_REF` | PROD_REF_ID and AT_PROD_REF_ID (ePID) — required since 2024/Feb/16 |
| `DW_LSTG_ITEM_MERGE` | View merging DW_LSTG_ITEM + DW_LSTG_ITEM_PROD_REF |
| `DW_CHECKOUT_TRANS` | Source of truth for quantity sold and GMV |
| `DW_LSTG_ITEM_PROP_LKP` | Item property lookups via ITEM_PRPTY_KEY_TXT |
| `DW_CATEGORY_GROUPINGS` | Category hierarchy joins |
| `DW_SITES` | Site ID lookup |
| `DW_CURRENCIES` | Currency ID lookup |
| `DW_DAILY_EXCHANGE_RATES` | Exchange rate joins |
| `DW_USERS` | Seller/buyer user info |
| `DW_AUCTION_CODES` | Auction type code lookup |
| `DW_SHPMT_OPTN` | Shipping option lookup |
| Listing Descriptions | Hive: `ebay_item_desc_live` at `/sys/edw/ebay_item_desc_live/snapshot` |

---

## Column Descriptions

### Identity & Lifecycle

#### `ITEM_ID`
Primary key. Uniquely identifies a listing (also called LISTING_ID).

To view a listing: `https://ebay.com/itm/<ITEM_ID>`

> **Note:** Item IDs were reused before ~2001. Be cautious with very old data.

#### `SLR_ID`
Oracle ID of the seller. Joins to `DW_USERS.USER_ID`. **Not updated after item creation.**

#### `SLR_SITE_ID`
Seller's site ID.

#### `SLR_CNTRY_ID`
Seller's country ID.

#### `ITEM_SITE_ID`
Site ID where the listing was listed. Lookup: `DW_SITES`.

> **Known issue:** ~5k items have mismatched site_id between DW_LSTG tables and DW_CHECKOUT_TRANS (Jira: XOSVC-7669).

#### `LSTG_STATUS_ID`
Item activity status. DW-derived (not in source table).

| Value | Meaning |
|---|---|
| `0` | Live — active and searchable (GTC out-of-stock items also have 0) |
| `1` | Ended — no longer active |
| `2` | Admin ended — ended by CS |
| `3` | Deleted — physically removed |
| `4` | Scheduled — not yet live |

> **On-hold listings:** Still have `LSTG_STATUS_ID = 0`. Check FLAGS5 `0x00000400` (1024) for on-hold status:
> `CASE WHEN CAST(flags5 AS BIGINT) & 1024 = 1024 THEN 'Y' ELSE 'N' END`

#### `LSTG_STATUS_UPD_DATE`
Only updated when a listing transitions from live (0) to ended (1).

---

### Dates & Timing

#### `AUCT_START_DT`
Date the listing becomes live. Use this (not creation date) for when a listing goes live. Scheduled listings exist in the table before they are live.

#### `AUCT_END_DT`
Date the listing ended or is scheduled to end.

- **GTC listings:** Rolling 30-day end date — overwritten each period.
- **Scheduled listings:** End date is set but start may be far in the future.
- **Half listings:** End date ~25 years from start.
- **Use for query partition filtering** — this column drives disk partitioning.

> Daylight Saving Time can cause discrepancies between site timestamps and DW timestamps.

#### `AUCT_END_DATE`
Timestamp version of the end time. See `AUCT_END_DT`.

#### `SALE_SCHED_END_DT`
Scheduled end date set at listing creation (`sale_start + duration`). Not updated on sale or checkout. Archived items: set to `1969-12-31`. Half listings: far future (e.g. `2034-01-01`).

#### `LAST_MODFD_DT` / `LAST_MODFD_DATE`
Date this item was last modified.

#### `LAST_TRANSACTION_DATE`
Date of last purchase.

#### `NOTICE_DATE`
Time EOA (End of Auction) notification was sent.

---

### Listing Format & Type

#### `AUCT_TYPE_CODE`
Format of the listing.

| Code | Format |
|---|---|
| `1` | Chinese Auction (normal auction, or auction with BIN) |
| `2` | Dutch Auction |
| `7` | Store Fixed Price (SIF) |
| `8` | Auction Personal Offer / Second Chance Offer |
| `9` | Fixed Price |
| `10` | Want it Now (WIN) |
| `12` | Half.com Listings |
| `13` | Lead Generation / Classified Ads / Best Offer Only |
| `6` | Ad Format (added by DW) |
| `-5` | StubHub |
| `-99` / `0` | Unknown |

> Types 3, 10, 11, -1, -2, -3, -4, -5 do **not** flow into DW_LSTG_ITEM.

**Format classification logic:**
```sql
CASE
  WHEN AUCT_TYPE_CODE IN (1,2) AND BIN_PRICE_USD > 0 THEN 'ABIN'
  WHEN AUCT_TYPE_CODE IN (1,2) THEN 'AUCTION'
  WHEN AUCT_TYPE_CODE IN (7,9) THEN 'FP'
  ELSE 'Other'
END
```

Lookup: `DW_AUCTION_CODES`

#### `GTC_UP_FLAG`
Indicates GTC (Good Till Cancelled) listing. Currently applicable to SIF and FP listings on US site.

#### `OFRD_SLNG_CHNL_ID`
Selling channel where the item is offered.

| Value | Channel |
|---|---|
| `1` | eBay |
| `2` | eBay Express |
| `4` | Half.com |
| `5` | eBay + eBay Express |
| `7` | eBay + Half.com |

#### `LSTG_MTHD_ID`
Method used for the most recent list or revise. Lookup: `DW_LSTG_MTHD`.

| Value | Method |
|---|---|
| `1` | SYI2 |
| `5` | API |
| `19` | SYI 3 API (includes C2C Web Next) |
| `21` | EasyLister |
| `23` | Listing Draft Service |

As of 2023-09-07, most active listings have `19` or `23`.

---

### Pricing

#### `START_PRICE_USD` / `START_PRICE_LSTG_CURNCY`
Start price in USD / listing currency.
- **For SIF/FP items:** use this (not BIN or CURNT price).
- **Auctions:** Starting bid price.
- **Fixed Price:** The BIN price.

#### `BIN_PRICE_USD` / `BIN_PRICE_LSTG_CURNCY`
Buy It Now price.
- Auction/BIN and Dutch/BIN: > 0
- SIF, FP, Half, Express: Always 0. Use CURNT_PRICE instead.

#### `CURNT_PRICE_USD` / `CURNT_PRICE_LSTG_CURNCY`
Current price.
- **Auctions:** Current bid (0 if no bids placed).
- **SIF / FP:** Current BIN price regardless of sales.
- **Second Chance Offer:** Only non-zero if purchase occurred.

> **Note:** Current price may be zero for SIF/FP. Prefer `START_PRICE_USD` for those formats.

#### `RSRV_PRICE_USD` / `RSRV_PRICE_LIST_CRNCY`
Reserve price (auctions only; mostly zero for FP).

#### `LSTG_CURNCY_ID`
Currency the listing was listed in. Joins to `DW_CURRENCIES`, `DW_DAILY_EXCHANGE_RATES`.

> Not a 1:1 mapping with ITEM_SITE_ID — Canadian listings can use USD or CAD.

#### `ORGNL_PRICE_AMT`
Original BIN price before a Markdown Manager (MDM) promotion. Price is in listing currency.

#### `PRMTN_SALE_START_DT` / `PRMTN_SALE_END_DT`
Start/end dates of a promotional sale.

---

### Quantity & Sales

#### `QTY_AVAIL`
Initial quantity available. Set at listing start, only updated by seller inventory changes — **NOT updated on sale**.

Available inventory remaining = `(QTY_AVAIL - QTY_SOLD) * LOT_SIZE` (LOT_SIZE from DW_LSTG_ITEM_COLD).

#### `QTY_SOLD`
Quantity sold from this listing.

> **Warning:** Multi-quantity listing data can be out of sync. Use `DW_CHECKOUT_TRANS` for authoritative quantity sold and GMV.

> **MSKU listings:** Use `DW_CHECKOUT_TRANS` to avoid under/over-reporting due to per-variation price differences.

#### `BIDCOUNT`
Count of bids received. Direct pull from site — **not** a reliable source for bid counts. Does not include BINs.

---

### GMV & Revenue

#### `GMS_USD` / `GMS_LSTG_CURNCY`
DW-calculated GMV field, captured once at listing end. Good for listing-level estimates, but does not track *timing* of GMV for multi-quantity listings.

- For GTC listings: shows 0 until listing ends, even if items have sold.
- Not populated for Ad Format 1.0.

> **Always use `DW_CHECKOUT_TRANS` for accurate GMV reporting.**

---

### Product & Catalog

#### `PRODUCT_ID`
Mapping between listing and Product ID. For active ePID associations, use `PROD_REF_ID` instead via `DW_LSTG_ITEM_PROD_REF`.

#### `PROD_REF_ID`
Seller-tagged (active) Product Reference ID (ePID). Added 2017-09-03.

> **Not available in `ACCESS_VIEWS.DW_LSTG_ITEM` on Hermes since 2024/Feb/16** — join against `DW_LSTG_ITEM_PROD_REF` directly.

Joins to `CTLG_PROD_FACT.PROD_REF_ID`.

#### `AT_PROD_REF_ID`
Auto-tagged (passive) Product Reference ID. Added by the Structured Data Adoption team.

> Also not in ACCESS_VIEWS since 2024/Feb/16 — use `DW_LSTG_ITEM_PROD_REF`.

---

### Seller & Application

#### `APPLICATION_ID`
Application used to create the listing. Joins to `DW_APPLICATIONS`.

Common values:

| Value | Application |
|---|---|
| `0` (LSTG_MTHD_ID ≠ 21) | SYI |
| `0` (LSTG_MTHD_ID = 21) | EasyLister |
| `219527` | BOLT |
| `290356` | BOLT B2C |
| `384352` | HELIX |
| Mobile | See DW_API_MBL_APP |

> For draft-based flows (CUB, Bolt, HELIX, BEAR): this is the app that **created the draft**, not the one that published it. Item revisions never change APPLICATION_ID.

#### `SLR_PRDCT_ID_TXT`
Custom label or SKU set by the seller (their internal SKU identifier).

---

### Listing Content

#### `AUCT_TITL`
Item title shown in Search and at the top of View Item.

#### `SUBTITLE`
Subtitle text for the listing (null if not provided).

#### `ITEM_CNTRY_ID`
Country where the seller says the item is located.

#### `ITEM_LOC`
Seller's item location.

#### `ITEM_ZIP`
Item zip code.

#### `PHOTO_YN`
`Y` if PICTURE_URL is non-blank; `N` otherwise.

#### `PHOTO_COUNT`
Number of images (self-hosted + EPS). Does not include stock photos or description-embedded images. For MSKU, only counts main image.

#### `GALLERY_URL`
Gallery image URL shown on search results pages.

#### `PICTURE_URL`
Semicolon-delimited list of all image URLs (max 4000 chars). Empty for catalog-adopted items with no seller images.

#### `STOCK_PHOTO_USED_YN`
`Y` if the gallery image comes from the product catalog. Most authoritative flag for stock photo usage.

---

### Shipping

#### `SHIPPING_FEE`
First domestic shipping service cost in listing currency. Shows $0 if shipping calculator used.

#### `SHIPPING_XFEE`
"Each Additional Item" shipping fee.

#### `SHIPPING_TYPE`
Type of shipping specified.

| Value | Type |
|---|---|
| `0` | Not specified |
| `1` | Flat Rate |
| `2` | Calculated Rate |
| `3` | Freight |
| `5` | Flat domestic + Calculated international |
| `6` | Calculated domestic + Flat international |

#### `SHIP_OPTION_CODE`
Shipping options offered.

| Value | Option |
|---|---|
| `0` | Site Only |
| `1` | Site + Regions |
| `2` | Worldwide |
| `3` | Will Not Ship |

#### `SHIP_REGN_FLAGS`
Bitmask of shipping regions. `0x01` = North America, `0x02` = Europe, `0x04` = Australasia, etc.

#### `WEIGHT_UNIT_TYPE`
`1` = Ounces, `2` = Grams.

---

### Relisting

#### `RELISTID`
Item ID of the listing this was relisted into.

#### `RELIST_PARENT_ITEM_ID`
Item ID of the parent if created via relist or sell-similar.

#### `RELIST_UP_FLAG`
Set if item was relisted (or flagged by 3rd party tool). Does NOT mean relist credit was given.

#### `AUCTION_END_REASON_CODE`
Why the listing ended.

| Value | Reason |
|---|---|
| `0` | Not ended early (natural end) |
| `1` | Lost or broken |
| `2` | No longer available |
| `3` | Error in minimum bid/reserve |
| `4` | Error in listing |
| `5` | EndAuctionAndSell |
| `11` | EndItemOnZeroQuantity |
| `99` | GTC renewal failure (check `LSTG_ITEM_GTC_NON_RNWD`) |

#### `SUCCESS_YN`
DW-calculated flag indicating whether the item sold.

> **Known issue:** Not reliable. For accurate success determination, use `DW_CHECKOUT_TRANS`.

---

### Status Flags

#### `BIN_SOLD_UP_FLAG`
`1` = Sold via Buy It Now. Unreliable for BIN-only formats (SIF, FP, Half, etc.) — use `AUCT_TYPE_CODE` instead.

| AUCT_TYPE_CODE | BIN_SOLD_UP_FLAG | Event type |
|---|---|---|
| 1 | 1 | Chinese auction + BIN → BIN |
| 1 | 0 | Chinese auction → Bid |
| 7, 9 | — | Store FP / Fixed Price → BIN |

#### `WACKO_YN`
Wacko listing flag. **Not the source of record** — use `RPRTD_WACKO_YN` in `DW_CHECKOUT_TRANS`.

#### `LISTED_WITH_AUTOPAY_UP_FLAG`
Immediate Pay / AutoPay listing. Note: also applies to Auction+BIN and SCO listings — check transaction flag to confirm buyer used Immediate Pay flow.

---

### Flag Columns (Bitmasks)

All flag columns use bitmask encoding. Decode with:
```sql
CAST(<flag_column> AS BIGINT) & <bit_value> = <bit_value>
```

#### `PASSWORDEX` (selected key bits)
| Bit | Value | Meaning |
|---|---|---|
| `0x00004000` | 16384 | ClosedAsBin |
| `0x00008000` | 32768 | RestrictedBidding |
| `0x01000000` | 16777216 | PersonalOfferRNM |

#### `FLAGS` (selected key bits)
| Bit | Value | Meaning |
|---|---|---|
| `0x00000010` | 16 | IsItemAuthenticated |
| `0x00080000` | 524288 | ScheduledListingCharged |
| `0x00100000` | 1048576 | ScheduledListing |

#### `FLAGS2` (selected key bits)
| Bit | Value | Meaning |
|---|---|---|
| `0x00000080` | 128 | IsCharityListing |
| `0x00400000` | 4194304 | CreatedByRelist |

#### `FLAGS4` (selected key bits)
| Bit | Value | Meaning |
|---|---|---|
| `0x00000010` | 16 | ItemListedOrRevisedByAPI |
| `0x00000040` | 64 | StockPhotoUsed |
| `0x00020000` | 131072 | BestOfferEnabled |

#### `FLAGS5` (selected key bits)
| Bit | Value | Meaning |
|---|---|---|
| `0x00000001` | 1 | EligibleForPickupInStore |
| `0x00000002` | 2 | AvailableForPickupInStore |
| `0x00000400` | 1024 | ItemOnHold |
| `0x02000000` | 33554432 | IsAutoDeclineEnabled |
| `0x04000000` | 67108864 | vehicleSubscriptionItem |

#### `FLAGS9` (selected key bits)
| Bit | Value | Meaning |
|---|---|---|
| `0x02000000` | 33554432 | MSKUFlag |

#### `FLAGS10` (selected key bits)
| Bit | Value | Meaning |
|---|---|---|
| `0x00000040` | 64 | ItemCompatibilitySpecified (fitment) |
| `0x00000080` | 128 | ItemInCompatibilityEnabledCategory |
| `0x00004000` | 16384 | KeepAliveWhenOutOfStock |
| `0x00008000` | 32768 | AvailableForShipToHome |
| `0x00020000` | 131072 | ManagedByInventory (SKUBI/MIP — DW quantities not authoritative) |
| `0x00100000` | 1048576 | DealItem |

#### `FLAGS12` (selected key bits)
| Bit | Value | Meaning |
|---|---|---|
| `0x00000004` | 4 | PUDORequestedItem |
| `0x00000008` | 8 | PUDOEligibleItem |
| `0x00020000` | 131072 | DailyDealsPermanent |
| `0x00800000` | 8388608 | IsIntermediatedShippingListing (GSP) |

#### `VISITCOUNT` (selected key bits)
| Bit | Value | Meaning |
|---|---|---|
| `0x01000000` | 16777216 | eItemGoodTillCancelled |
| `0x00040000` | 262144 | IsItemEMSEligible (eBay Managed Shipping) |

#### `SALE_STATUS` (selected key bits)
| Bit | Value | Meaning |
|---|---|---|
| `0x00000040` | 64 | EBAYPLUS_REQUESTED_ITEM |
| `0x00000080` | 128 | EBAYPLUS_ELIGIBLE_ITEM |
| `0x00000100` | 256 | Digitally Delivered Goods (DDG) |

---

### Miscellaneous

#### `HIGH_BDR_ID`
Highest bidder user ID. `-998` = multi-quantity listing. `-999` = unknown.

#### `ITEM_PRPTY_KEY_TXT`
Keys for joins into `DW_LSTG_ITEM_PROP_LKP` and `DW_LSTG_ITEM_PROP_CONTENT_VAL`.

#### `LEAF_CATEG_ID`
Leaf category ID chosen by seller. Join `DW_CATEGORY_GROUPINGS` on `ITEM_SITE_ID` + `LEAF_CATEG_ID`.

#### `LEAF_CATEG_ID2`
Second category ID (0 = not chosen).

#### `CATEG_KEY` / `CATEG_KEY2`
Joins to `DW_CATEGORY_HIERARCHY.CATEG_KEY`.

#### `WATCH_CNT`
Number of unique users watching this item. Not updated after listing ends.

> **Note:** Backfilled 2010-07-25. Listings with DW Update Date before that have WATCH_CNT = -999.

#### `ITEM_VRSN_ID`
Version ID of the listing. A new version is not created on every revision — rules are complex.

#### `SGNFCNT_RVSN_CNT`
Number of significant revisions. Only meaningful for AUCT_TYPE_CODE 7 & 9.

#### `PBP_ELIGIBILITY`
PayPal Buyer Protection eligibility. `0` = Ineligible, `1` = Eligible.

#### `PAYPAL_SELLER_EMAIL`
Seller's PayPal email. **PII** — only available in `PRS_SECURE_V`, not `ACCESS_VIEWS`.

---

## Support

| Channel | Link |
|---|---|
| Jira | http://go/velvet-support |
| Slack | #hadoop-support, #zeta-support, #selfserviceanalytics |
| eNotify | http://go/hermes-subscribe |
