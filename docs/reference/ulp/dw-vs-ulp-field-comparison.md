# DW_LSTG_ITEM vs ULP JSON Stream — Field Comparison

This document compares the 47 shared fields between `DW_LSTG_ITEM` (offline
data warehouse table, T-1 daily snapshot) and the ULP listing stream
(`afterchangeDocumentPlain.listing`, point-in-time event snapshot).

Analysis is based on 22 matched listing IDs across both datasets.

---

## Coverage

| Source | Total fields | Shared with other source | Exclusive |
|---|---|---|---|
| `DW_LSTG_ITEM` (TSV) | 155 | 47 | 108 |
| ULP JSON stream (listing) | ~80 top-level concepts (~504 nested paths) | 47 | ~33+ |

The 47 shared fields represent the **intersection of business concepts**
both surfaces expose. The remaining fields are either DW-only (bitmask flags,
GMV, auction mechanics, ETL audit columns) or ULP-only (provider-enriched
data: visibility, COO, compatibility, GSP detail, SEO alt text, etc.).

---

## Summary Scorecard

| Category | Count | Fields |
|---|---|---|
| ✅ Perfect match (22/22) | 19 | Primary keys, identifiers, seller, category, content |
| 🟡 Minor differences (latency, ≤3 mismatches) | 7 | Status, price, quantity, revision count, promo dates |
| 🔴 Structural differences (always or mostly differ) | 12 | Encoding, timezone, unit scale, semantic scope |

---

## Part 1 — Perfect Match Fields (19 fields, 100%)

These fields are **identical** in both sources for all 22 listings.
They are stable, slow-changing, and set at listing creation.

| DW column | ULP JSON path | Example value |
|---|---|---|
| `item_id` | `listingId` | `800617448894` |
| `auct_titl` | `sellerProduct.title` | `"Panini 2025 Mosaic Football..."` |
| `auct_type_code` | `listingFormat` (mapped: BIN/FIXED_PRICE→9) | `9` |
| `leaf_categ_id` | `category.primaryCategory.id` | `261328` |
| `leaf_categ_id2` | `category.secondaryCategory.id` (absent→`0`) | `0` |
| `slr_id` | `seller.legacyUserId` | `2839192318` |
| `item_loc` | `itemLocation.location` | `"Springfield, West Virginia"` |
| `item_zip` | `itemLocation.postalCode` | `"26763"` |
| `application_id` | `applicationId` | `557284` |
| `photo_count` | `len(photos[])` | `2` |
| `slr_prdct_id_txt` | `items[0].sku` | seller SKU string |
| `orgnl_price_amt` | `items[0].sellerPrice.originalPrice.original.amount` | pre-markdown price |
| `watch_cnt` | `items[0].watchCount` (BASICLISTINGDATA provider) | `0` |
| `gtc_up_flag` | `listingLifecycle.listingDuration == "GTC"` → `1/0` | `1` |
| `item_vrsn_id` | `sellerListingVersionId` | `7381570253025` |
| `relist_parent_item_id` | `relistParentListingId` | (empty or parent ID) |
| `shipping_fee` | `fulfillmentTerms.shippingTerms.shippingOptions[0].shippingServices[0].shippingCost.original.amount` | `3.0` |
| `weight_unit_type` | `fulfillmentTerms.packageSpec.unitOfMeasure` (mapped: English→1, Metric→2) | `1` |
| `qty_sold` | `items[0].quantitySold` | `0` |

**Key insight:** All identifiers (item, seller, category, application),
all content fields (title, location, SKU), and all structural flags (GTC,
version) match perfectly. These can be joined or compared with full confidence.

---

## Part 2 — Minor Differences (7 fields, data latency)

These fields hold the **same concept** but differ in a small number of records
because the ULP stream captures state at **event time** (point-in-time) while
the DW captures state at **end of business day** (T-1 snapshot).

Pattern: DW value = more recent state; ULP value = state when the event fired.

### 2.1 `lstg_status_id` / `listingLifecycle.listingStatus` — 86% match

| DW encodes | ULP encodes |
|---|---|
| `0` | `ACTIVE` |
| `1` | `ENDED` |
| `4` | `SCHEDULED` |

**Mismatches (3/22):**

| item_id | DW | ULP | Explanation |
|---|---|---|---|
| `198518997592` | `1` (Ended) | `ACTIVE` | Listing ended after ULP event was emitted; DW snapshot captured the end |
| `358739250407` | `1` (Ended) | `ACTIVE` | Same |
| `366458079528` | `1` (Ended) | `ACTIVE` | Same |

> **Rule:** ULP stream events for ended listings may show `ACTIVE` in the
> `afterchangeDocumentPlain` if the event was a provider update (e.g., markdown
> change) that fired before the listing naturally ended. DW always reflects
> the final state of the day.

---

### 2.2 `start_price_lstg_curncy` / `items[0].sellerPrice.fixedPrice.original.amount` — 86% match

**Mismatches (3/22):**

| item_id | DW | ULP | Delta |
|---|---|---|---|
| `317811882364` | `9.59` | `9.61` | +0.02 (price revised up after event) |
| `358216954270` | `24.28` | `23.25` | -1.03 (price revised down after event) |
| `407154196519` | `13.34` | `13.51` | +0.17 (price revised up after event) |

> **Rule:** The ULP stream event captures price at event-fire time. If the
> seller revised the price after the event but before EOD, DW reflects the
> newer price. The `beforeChangePatch` for these files confirms
> `replace: /listing/items/0/sellerPrice/fixedPrice/original/amount`.
>
> **Never assume price parity between DW and ULP stream for the same day.**
> Use `DW_CHECKOUT_TRANS` for authoritative transaction prices.

---

### 2.3 `qty_avail` / `items[0].quantityAvailable` — 86% match

**Mismatches (3/22):**

| item_id | DW | ULP | Delta | Implied sales |
|---|---|---|---|---|
| `188739475974` | `2` | `4` | -2 | 2 units sold after event |
| `206544283190` | `56` | `58` | -2 | 2 units sold after event |
| `257569090674` | `16` | `6` | -10 | 10 units sold after event |

> **Rule:** ULP stream `quantityAvailable` = quantity at event time.
> DW `qty_avail` = quantity at T-1 snapshot. DW ≤ ULP when sales occur
> between event and EOD.
>
> **Warning (from DW docs):** Even DW `qty_avail` is not always authoritative
> for multi-quantity listings. Use `DW_CHECKOUT_TRANS` for precise sold counts.

---

### 2.4 `sgnfcnt_rvsn_cnt` / `significantRevisionCount` — 73% match

**Mismatches (6/22):**

| item_id | DW | ULP | Delta |
|---|---|---|---|
| `188739475974` | `9` | `7` | +2 revisions in DW |
| `206544283190` | `1` | `0` | +1 revision in DW |
| `298656581435` | `3` | `2` | +1 revision in DW |
| `188317757623` | `6` | `4` | +2 revisions in DW |
| `236969063618` | `1` | `0` | +1 revision in DW |
| `257569090674` | `0` | `0` | match |

> **Rule:** DW always has a count ≥ ULP for this field. Each revision between
> the ULP event and the DW snapshot increments the DW count but is invisible
> to the ULP event that was already emitted.

---

### 2.5 `prmtn_sale_start_dt` / `markdownDiscountDuration.promoSaleStartDateTime` — 95% match

### 2.6 `prmtn_sale_end_dt` / `markdownDiscountDuration.promoSaleEndDateTime` — 95% match

**Mismatch (1/22 each):**

| item_id | DW start | ULP start | DW end | ULP end |
|---|---|---|---|---|
| `366458079528` | `2026-09-11` | `2026-09-08` | `2026-09-14` | `2026-09-11` |

> **Rule:** Promotion dates were extended after the ULP event. DW reflects
> the updated schedule; ULP stream reflects the original promotion window
> at the time the markdown event fired. A +3 day extension is visible in DW
> but not in the stream event.

---

## Part 3 — Structural Differences (12 fields)

These fields differ not because of latency but because of **fundamental
representational or semantic differences** between the two systems.

### 3.1 Encoding Differences — Integer vs String Enum

DW was designed for relational joins (integer lookup IDs).
ULP was designed for direct consumption (human-readable string enums).

#### `lstg_curncy_id` / `items[0].sellerPrice.fixedPrice.original.currency` — 0% match

| DW integer | ULP ISO string | Currency |
|---|---|---|
| `1` | `USD` | US Dollar |
| `3` | `GBP` | British Pound |
| `5` | `AUD` | Australian Dollar |
| `7` | `EUR` | Euro |

DW requires a join to `DW_CURRENCIES`. ULP is self-describing.
**Data is identical; representation differs.**

#### `shipping_type` / `fulfillmentTerms.shippingTerms.shippingOptions[0].costType` — 0% match

| DW integer | ULP string |
|---|---|
| `0` | `NOT_SPECIFIED` |
| `1` | `FLAT` |
| `2` | `CALCULATED` |
| `3` | `FREIGHT` |

Same data, integer vs string. Conversion is a simple lookup.

#### `package_size` / `fulfillmentTerms.packageSpec.packageType` — 91% match (2 mismatches)

| DW integer | ULP string |
|---|---|
| `4` | `PackageThickEnvelope` |
| `1` | `Letter` |
| `9` | `PackageThickEnvelope` |

The 2 apparent "mismatches" (`DW=4`, `ULP=PackageThickEnvelope`) are actually
the **same value** — the numeric comparison treats them as different. Semantically identical.

---

### 3.2 Unit and Scale Differences

#### `weight` / `fulfillmentTerms.packageSpec.majorWeight` — 73% match (6 mismatches)

| item_id | DW | ULP | Ratio | Explanation |
|---|---|---|---|---|
| `227214012314` | `597000` | `597` | 1000× | DW=grams, ULP=kg (Metric listing) |
| `257569090674` | `6200` | `6` | ~1000× | DW=grams, ULP=kg |
| `236969063618` | `23` | `1` | ~23× | DW=ounces total, ULP=lb major unit |

**DW** stores weight as a single integer in the smallest applicable unit
(grams for Metric listings, ounces for English listings).

**ULP** stores weight split into `majorWeight` + `minorWeight`
(e.g., `majorWeight=597, minorWeight=0` for 597 kg).

> **Conversion formula:**
> - Metric: `ULP_kg = DW_weight_grams / 1000`
> - English: `ULP_lb = DW_weight_oz / 16` (major), `DW_weight_oz % 16` (minor)

---

### 3.3 Granularity Loss

#### `lstg_mthd_id` / `creationMode` — 0% match (22/22 differ)

| DW code | DW meaning | ULP value |
|---|---|---|
| `19` | SYI 3 API / Listing Draft Service | `Add` |
| `23` | Listing Draft Service (LDS) | `Add` |
| `21` | EasyLister | `Add` |
| `5` | API (Trading API direct) | `Add` |
| `10` | Relist as SIF | `Relist` |
| `11` | Sell Like Item (sell similar) | `SellSimilar` |

DW has **20+ specific method codes** identifying the exact listing tool.
ULP collapses these into **4 coarse creation modes**: Add, Relist, SellSimilar, SellOneLikeThis.

All 22 samples have `creationMode=Add` in ULP regardless of whether DW shows
`19` (SYI3 API), `23` (LDS), or another Add-type method.

> **Consumer impact:** You cannot distinguish EasyLister from SYI3 API
> from Trading API using ULP alone. Use DW if tool-specific analysis is needed.

---

### 3.4 Timezone Differences

#### `auct_start_dt` / `listingLifecycle.startDate` — 73% match (6 mismatches)

| item_id | DW | ULP | Diff |
|---|---|---|---|
| `188317757623` | `2026-04-25` | `2026-04-26` | +1 day |
| `188739475974` | `2026-08-03` | `2026-08-04` | +1 day |
| `236230020203` | `2025-07-26` | `2025-07-27` | +1 day |

#### `auct_end_dt` / `listingLifecycle.endDate` — 50% match (11 mismatches)

| item_id | DW | ULP | Type |
|---|---|---|---|
| `188317757623` | `2026-09-25` | `2026-09-26` | +1 day (timezone) |
| `198518997592` | `2026-09-10` | `2026-09-23` | Large gap (semantic) |
| `358739250407` | `2026-09-09` | `2026-09-30` | Large gap (semantic) |

**Two root causes for end date:**

1. **Timezone (off-by-one-day, 6 listings):**
   DW stores dates in **PST/PDT** (eBay's US timezone). ULP stores timestamps
   in **UTC**. A listing ending at 22:00 PST = 06:00 UTC next day — ULP date
   is one day later than DW date.

2. **Semantic difference (5 listings):**
   - `DW.auct_end_dt` = **actual end date** (when the listing terminated)
   - `ULP.listingLifecycle.endDate` = **scheduled end date** (when it was planned to end)
   For listings ended early (e.g., manual seller end, admin action), DW shows
   the actual termination date; ULP shows the original schedule. These are
   conceptually different fields.

---

### 3.5 Semantic Scope Differences

#### `sale_sched_end_dt` / `listingLifecycle.scheduledEndDate` — 64% match (8 mismatches)

| item_id | DW | ULP | Explanation |
|---|---|---|---|
| `227214012314` | `2026-10-12` | `2026-09-12` | DW=original creation schedule, ULP=current GTC period |
| `188317757623` | `2026-09-25` | `2026-09-26` | Timezone only |

For **GTC listings**, DW `sale_sched_end_dt` was set at listing creation
(`sale_start + duration`) and is **never updated on GTC renewal**.
ULP `scheduledEndDate` reflects the **current 30-day GTC period end**,
which rolls forward each renewal cycle.

These fields measure different things for GTC listings.

---

#### `auction_end_reason_code` / `endReason` — 82% match (4 mismatches)

| DW int | DW meaning | ULP string |
|---|---|---|
| `0` | Natural end | `NONE` |
| `1` | Item lost/broken | `LOST_OR_BROKEN` |
| `2` | No longer available | `NOT_AVAILABLE` |
| `4` | Error in listing | `INCORRECT_LISTING` |

**Mismatches (3/22):**

| item_id | DW | ULP | Explanation |
|---|---|---|---|
| `178055817599` | `2` | `NOT_AVAILABLE` | These actually match — conversion bug in comparison |
| `198518997592` | `2` | `NONE` | Listing not yet ended in ULP event; end reason not propagated |
| `358739250407` | `2` | `NONE` | Same |

The true mismatch is ULP showing `NONE` for listings DW marks as manually
ended (`code=2`). The ULP stream event fired before the end reason was set.

---

#### `last_modfd_dt` / `itemRevisionDate` — 14% match (19 mismatches) ⚠️

This is the **most divergent field** — only 3 of 22 match.

| item_id | DW | ULP | Type |
|---|---|---|---|
| `177818514911` | `2026-08-29` | *(absent)* | ULP has no revision date |
| `178055817599` | `2026-09-08` | `2026-08-17` | DW is 22 days newer |
| `188739475974` | `2026-09-11` | `2026-09-08` | DW is 3 days newer |

**Three root causes:**

1. **ULP `itemRevisionDate` is absent for many listings** — it is only set when
   the ULP event was triggered by a CLS core revision. Provider-only updates
   (GSP estimator bump, visibility refresh, SEO alt text) do not set it.

2. **DW `last_modfd_dt` = DW ETL pipeline update time**, not a seller revision.
   It changes whenever the DW row was touched for any operational reason,
   including non-seller events.

3. **Different semantic scope:**
   - DW: any write to the DW row
   - ULP: seller-initiated or CLS-driven core listing revision only

> **Do not use these fields interchangeably.** They answer different questions:
> DW answers "when was this DW row last updated?";
> ULP answers "when did the seller last significantly revise this listing?".

---

## Part 4 — Root Cause Classification

| Root cause | Fields affected | Fix |
|---|---|---|
| ⏱ **T-1 latency** | `lstg_status_id`, `start_price`, `qty_avail`, `sgnfcnt_rvsn_cnt`, promo dates | Accept divergence; use ULP for near-real-time, DW for end-of-day state |
| 🔡 **Encoding** (int→string) | `lstg_curncy_id`, `shipping_type`, `package_size`, `auction_end_reason_code` | Apply lookup table translation; data is semantically identical |
| 📐 **Unit/scale** | `weight` | Apply unit conversion formula (÷1000 for Metric, ÷16 for English) |
| 📉 **Granularity loss** | `lstg_mthd_id` → `creationMode` | Cannot recover; use DW if fine-grained tool analysis needed |
| 🕐 **Timezone** | `auct_start_dt`, `auct_end_dt` | DW=PST/PDT local date; ULP=UTC date; off-by-one for late-night listings |
| 📋 **Semantic scope** | `auct_end_dt` (actual vs scheduled), `sale_sched_end_dt` (original vs rolling GTC), `last_modfd_dt` (ETL update vs seller revision) | Cannot be reconciled; they measure different things |

---

## Part 5 — Consumer Guidance

### When to use DW_LSTG_ITEM

- Historical daily aggregates and trend analysis
- Final end-of-day listing state
- Fields only in DW: GMV (`gms_lstg_curncy`), bid mechanics (`bidcount`,
  `high_bdr_id`), flag bitmasks (FLAGS1–FLAGS12), auction-specific data
- Fine-grained listing method (`lstg_mthd_id = 19` vs `21` vs `23`)
- Cross-table joins to `DW_CHECKOUT_TRANS`, `DW_USERS`, `DW_CATEGORY_GROUPINGS`

### When to use ULP JSON stream

- Near-real-time listing state (event-time snapshot)
- Provider-enriched data not in DW: visibility (`visibilitySummary`),
  COO (`itemCountryOfOrigin`), fitment (`listingCompatibilities`),
  GSP detail (`shippingProgramEligibility`), SEO alt text (`photosWithAltText`),
  eBay Live (`ebayLive`), deal state (`dealDetails`)
- Structured condition descriptors (`itemCondition.conditionDescriptors`)
- Global identifiers (UPC/EAN/ISBN) at item level
- High-precision prices (`fixedPriceWithHighPrecision`)
- Marketing price treatment (`marketingPrice.pricingTreatment`)

### Fields safe to join on (always match)

```
item_id = listingId
slr_id  = seller.legacyUserId
application_id = applicationId
leaf_categ_id  = category.primaryCategory.id
item_vrsn_id   = sellerListingVersionId
```

### Fields requiring translation before joining

```
lstg_curncy_id (int) → currency (ISO string)   -- lookup table
shipping_type (int)  → costType (string)        -- lookup table
weight (minor units) → majorWeight + minorWeight -- unit conversion
package_size (int)   → packageType (string)     -- lookup table
auct_type_code (int) → listingFormat (string)   -- lookup table
item_site_id (int)   → marketplaceId (string)   -- lookup table
```

### Fields that cannot be reliably joined

```
last_modfd_dt  ≠ itemRevisionDate   (different semantic scope)
auct_end_dt    ≠ endDate            (actual end vs scheduled + timezone)
sale_sched_end_dt ≠ scheduledEndDate (original schedule vs rolling GTC)
lstg_mthd_id   ≠ creationMode       (granularity loss: 20+ codes → 4 modes)
```

---

## Appendix — Field Match Results Table

| Field (DW → ULP) | Match | Mismatch | % | Root cause |
|---|---|---|---|---|
| `item_id` → `listingId` | 22 | 0 | 100% | ✅ |
| `auct_titl` → `sellerProduct.title` | 22 | 0 | 100% | ✅ |
| `auct_type_code` → `listingFormat` | 22 | 0 | 100% | 🔡 enum (mapped) |
| `leaf_categ_id` → `primaryCategory.id` | 22 | 0 | 100% | ✅ |
| `leaf_categ_id2` → `secondaryCategory.id` | 22 | 0 | 100% | ✅ |
| `slr_id` → `seller.legacyUserId` | 22 | 0 | 100% | ✅ |
| `item_loc` → `itemLocation.location` | 22 | 0 | 100% | ✅ |
| `item_zip` → `itemLocation.postalCode` | 22 | 0 | 100% | ✅ |
| `application_id` → `applicationId` | 22 | 0 | 100% | ✅ |
| `photo_count` → `len(photos)` | 22 | 0 | 100% | ✅ |
| `slr_prdct_id_txt` → `items[0].sku` | 22 | 0 | 100% | ✅ |
| `orgnl_price_amt` → `originalPrice.amount` | 22 | 0 | 100% | ✅ |
| `watch_cnt` → `items[0].watchCount` | 22 | 0 | 100% | ✅ |
| `gtc_up_flag` → `listingDuration=GTC` | 22 | 0 | 100% | ✅ |
| `item_vrsn_id` → `sellerListingVersionId` | 22 | 0 | 100% | ✅ |
| `relist_parent_item_id` → `relistParentListingId` | 22 | 0 | 100% | ✅ |
| `shipping_fee` → `shippingCost.amount` | 22 | 0 | 100% | ✅ |
| `weight_unit_type` → `unitOfMeasure` | 22 | 0 | 100% | 🔡 enum (mapped) |
| `qty_sold` → `quantitySold` | 22 | 0 | 100% | ✅ |
| `lstg_status_id` → `listingStatus` | 19 | 3 | 86% | ⏱ latency |
| `start_price_lstg_curncy` → `fixedPrice.amount` | 19 | 3 | 86% | ⏱ latency |
| `qty_avail` → `quantityAvailable` | 19 | 3 | 86% | ⏱ latency |
| `sgnfcnt_rvsn_cnt` → `significantRevisionCount` | 16 | 6 | 73% | ⏱ latency |
| `prmtn_sale_start_dt` → `promoSaleStartDateTime` | 21 | 1 | 95% | ⏱ latency |
| `prmtn_sale_end_dt` → `promoSaleEndDateTime` | 21 | 1 | 95% | ⏱ latency |
| `package_size` → `packageType` | 20 | 2 | 91% | 🔡 encoding (same value) |
| `lstg_curncy_id` → `currency` | 0 | 22 | 0% | 🔡 int→ISO string |
| `shipping_type` → `costType` | 0 | 22 | 0% | 🔡 int→string enum |
| `lstg_mthd_id` → `creationMode` | 0 | 22 | 0% | 📉 granularity loss |
| `auction_end_reason_code` → `endReason` | 18 | 4 | 82% | 🔡 encoding + ⏱ |
| `weight` → `packageSpec.majorWeight` | 16 | 6 | 73% | 📐 unit scale |
| `auct_start_dt` → `startDate` | 16 | 6 | 73% | 🕐 timezone (UTC vs PST) |
| `sale_sched_end_dt` → `scheduledEndDate` | 14 | 8 | 64% | 🕐 timezone + 📋 semantics |
| `auct_end_dt` → `endDate` | 11 | 11 | 50% | 🕐 timezone + 📋 semantics |
| `last_modfd_dt` → `itemRevisionDate` | 3 | 19 | 14% | 📋 semantic scope |
