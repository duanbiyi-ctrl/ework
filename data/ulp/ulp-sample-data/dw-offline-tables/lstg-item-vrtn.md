# LSTG_ITEM_VRTN — Listing Item Variation Table Reference

## Table Basics

| Property | Value |
|---|---|
| **Platform** | Hercules, Apollo |
| **DB** | GDW_TABLES |
| **Table name** | LSTG_ITEM_VRTN |
| **Access views** | `ACCESS_VIEWS.LSTG_ITEM_VRTN`, `BATCH_VIEWS.LSTG_ITEM_VRTN` |
| **Data frequency** | Daily |
| **Data latency** | T-1 |
| **Primary key** | `ITEM_ID`, `ITEM_VRTN_ID` |
| **Partition** | None |
| **Owner** | Ding, Shan (AWF)(CCC) |
| **Latency priority** | P1 |
| **SLA time** | 17:00 PST |
| **Quality priority** | P1 |
| **DR enabled** | Y |
| **Related process** | Seller Listing |

---

## Overview

This table contains all information about **variations (SKUs) within a Multi-SKU (MSKU) listing**. One row is inserted for each SKU/variation on the parent item.

Joins to the parent listing via `ITEM_ID → DW_LSTG_ITEM.ITEM_ID`.

**Always filter** `DLT_STS_YN_IND = 'N'` to get the current live set of variations.

### Business Impact

- Public Feed API depends on this table to serve item feeds to third-party partners.
- GMB impact when data is delayed by 1 day: **~$1M/day** (DECO team estimate).

---

## Column Descriptions

### Identity

#### `ITEM_VRTN_ID`
Unique SKU identifier within the listing.

#### `ITEM_ID`
Parent listing identifier. Joins to `DW_LSTG_ITEM.ITEM_ID`.

#### `SLR_PRDCT_ID_TXT`
Seller-defined SKU (stock-keeping unit) label. This is the seller's internal identifier for the variation.

#### `DLT_STS_YN_IND`
Deletion flag for the SKU.

| Value | Meaning |
|---|---|
| `N` | Active (current) variation |
| `Y` | Deleted variation |

> **Always apply `DLT_STS_YN_IND = 'N'`** to get the current live set of SKUs.

---

### Pricing

#### `PRICE_AMT`
Price for this SKU in listing currency.

> **Important:** Individual SKUs **can have different prices** from the parent listing price. Always use variation-level price for per-SKU analysis.

#### `ORGNL_PRICE_AMT`
Original price before a Markdown Manager (MDM) sale. Populated when a markdown is in effect.

#### `MFO_PRICE_LC_AMT`
Discount price for "Made For Outlet" items.

#### `MAP_PRICE_LC_AMT`
Discount price for "Minimum Advertised Price" items.

#### `STP_PRICE_LC_AMT`
Discount price for "Strike Through Price" items.

#### `PRICE_TRTMNT_CD`
Price treatment type for promotional pricing.

| Value | Treatment |
|---|---|
| `0` | None |
| `1` | Strike Through Price (STP) |
| `2` | Minimum Advertised Price (MAP) |
| `3` | Made For Outlet (MFO) |

---

### Quantity

#### `QTY`
Number of units available for this SKU.

#### `SOLD_QTY`
Quantity sold for this SKU.

#### `RSRVD_QTY`
Quantity in reserved state. Changes frequently; not typically useful for reporting.

---

### Dates & Timestamps

#### `AUCT_END_DT`
PPI (Partition Predicate Index) enabling fast joins to listing tables.

#### `VRTN_END_DT`
End date for this SKU. **Always NULL since at least 2020-01-01.**

#### `VRTN_END_RSN_CD`
Reason the SKU was ended. **Always 0 since at least 2020-01-01.**

#### `LAST_RSTCK_DT`
Date when the SKU was restocked (quantity changed) by the seller.

#### `LAST_RSTCK_TM`
Timestamp when the SKU was restocked.

#### `SRC_CRTN_DT` / `SRC_CRTN_TM`
Date and time the row was created.

#### `LAST_MDFD_DT` / `LAST_MDFD_TM`
Date and time the row was last updated.

---

### Gallery / Images

#### `GLRY_URL_TXT`
URL of the gallery image for this variation.

#### `GLRY_OFST_TXT`
Gallery URL offset used to generate the gallery image.

#### `GLRY_IMAGE_SRC_TXT`
Source of the gallery image (from `EBAY_ITEMS.GALLERY_IMAGE_SOURCE`).

#### `GLRY_VRSN_NUM`
Revision number of the gallery image.

#### `GLRY_STATE_CD`
State of the gallery image.

| Value | State |
|---|---|
| `0` | NotProcessed |
| `1` | Success |
| `2` | BadURL |
| `3` | BadProtocol |
| `4` | PermanentBadImage |
| `5` | HostNameDoesNotExist |
| `6` | ServerNotAvailable |
| `7` | ItemNotFound |
| `8` | FailedDownload |
| `9` | ImageFormat |
| `10` | BadImage |
| `11` | InternalError |
| `12` | Removed |
| `13` | MailError |
| `14` | MaxResultCode |

---

### Global Product Identifiers

#### `UPC_NUM`
UPC number of the item.

#### `ISBN_NUM`
ISBN number of the item.

#### `EAN_NUM`
EAN number of the item.

#### `GTIN_NUM`
GTIN number of the item.

> These columns (`UPC_NUM`, `ISBN_NUM`, `EAN_NUM`, `GTIN_NUM`) were added by the "Landing New Column" project in LSTG_ITEM_VRTN.

---

### Other

#### `VRTN_ORDER_NUM`
Display order of this SKU within the variation list.

#### `WATCH_CNT`
Number of eBay users watching this item.

#### `FLGS01_BMAP`
SKU-level flags bitmask.

---

## Sample SQL

### Multi-SKU Listing Quantity Rollup

```sql
SELECT
  l.auct_type_code,
  l.item_site_id,
  CASE WHEN item_rollups.available_quantity > 0 THEN 'Y' ELSE 'N' END AS multi_sku,
  COUNT(*) AS listings,
  SUM(COALESCE(item_rollups.available_quantity, l.qty_avail)) AS total_qty_available,
  SUM(COALESCE(item_rollups.variations, 1)) AS variations_plus_items,
  SUM(COALESCE(item_rollups.sold_quantity, 0)) AS sold_from_live_lists
FROM
  access_views.dw_lstg_item l
  LEFT JOIN (
    SELECT
      v.item_id,
      COUNT(*) AS variations,
      SUM(qty - sold_qty) AS available_quantity,
      SUM(sold_qty) AS sold_quantity
    FROM
      access_views.lstg_item_vrtn v
    WHERE
      v.auct_end_dt >= '2011-10-11'
      AND v.dlt_sts_yn_ind = 'N'  -- current (non-deleted) variations only
    GROUP BY
      v.item_id
  ) item_rollups ON (l.item_id = item_rollups.item_id)
WHERE
  l.auct_end_dt >= '2011-10-11'
GROUP BY
  l.auct_type_code,
  l.item_site_id,
  CASE WHEN item_rollups.available_quantity > 0 THEN 'Y' ELSE 'N' END
```

**What this query does:**
- Joins all listings to their variations (if any)
- Uses `DLT_STS_YN_IND = 'N'` to filter to live variations
- Calculates available quantity at the variation level
- Falls back to `DW_LSTG_ITEM.QTY_AVAIL` for non-MSKU listings

---

## Relationship to DW_LSTG_ITEM

| | `DW_LSTG_ITEM` | `LSTG_ITEM_VRTN` |
|---|---|---|
| Grain | One row per listing | One row per SKU variation per listing |
| Price | Listing-level price | Per-SKU price (can differ per variation) |
| Quantity | Listing total quantity | Per-SKU quantity |
| Sold | Listing total sold | Per-SKU sold |
| Key | `ITEM_ID` | `ITEM_ID` + `ITEM_VRTN_ID` |
| Use for MSKU | Parent listing metadata | Variation-level detail |

For MSKU quantity calculations:
- **Available per SKU:** `QTY - SOLD_QTY` (where `DLT_STS_YN_IND = 'N'`)
- **Total listing available:** `SUM(QTY - SOLD_QTY)` across all active variations

> **Do not rely on `DW_LSTG_ITEM.QTY_AVAIL` or `QTY_SOLD` for MSKU listings.** Use `LSTG_ITEM_VRTN` for per-variation accuracy and `DW_CHECKOUT_TRANS` for authoritative GMV.
