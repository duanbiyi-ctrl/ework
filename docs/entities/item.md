# Item LDM

[← Back to LDM Catalog](../index.md)

## Overview

**LDM Name:** `item`

**Description:** The core listing entity in the Item Domain. Each record represents one eBay listing, containing comprehensive information about title, pricing, category, seller, listing lifecycle, and more.

**Primary Key:** `item_id`

**Relationship Type:** Base entity — can be queried independently or joined to other LDMs.

---

## Field Reference

!!! note ""
    Fields are grouped by functional area. Click a tab to explore. The **Feature Flags** tab contains boolean indicator fields derived from bitmap columns in the physical source.

=== "Core Identity"

    {{ read_table('docs/assets/ldm-schemas/item-fields/01-core.tsv', sep='\t') }}

=== "Listing Details"

    !!! warning "Date field gotchas"
        - Use **`auct_start_dt`** as the listing go-live date — not `site_create_date`. Scheduled listings are inserted into the table before they go live.
        - **`auct_end_dt`** rolls forward every 30 days for GTC listings and reflects the end of the current period, not the original planned end date. Always use this field for partition-filtered queries.
        - **`lstg_status_id = 0`** (Live) does **not** mean the listing is visible — on-hold listings also have status 0. Always check the `onhold` flag in the Feature Flags tab.

    {{ read_table('docs/assets/ldm-schemas/item-fields/02-listing.tsv', sep='\t') }}

=== "Pricing"

    {{ read_table('docs/assets/ldm-schemas/item-fields/03-pricing.tsv', sep='\t') }}

=== "Category"

    !!! tip ""
        To get the full category hierarchy (L1 → L2 → SAP → meta), join on `(item_site_id, leaf_categ_id)` against the `DW_CATEGORY_GROUPINGS` reference table.

    {{ read_table('docs/assets/ldm-schemas/item-fields/04-category.tsv', sep='\t') }}

=== "Seller"

    !!! warning "PII"
        `paypal_seller_email` is a PII field. Use `hash_paypal_seller_email` for all analytical workloads.

    {{ read_table('docs/assets/ldm-schemas/item-fields/05-seller.tsv', sep='\t') }}

=== "Shipping"

    {{ read_table('docs/assets/ldm-schemas/item-fields/06-shipping.tsv', sep='\t') }}

=== "Condition"

    {{ read_table('docs/assets/ldm-schemas/item-fields/07-condition.tsv', sep='\t') }}

=== "Feature Flags"

    All fields in this tab are **boolean** (`true` / `false`). They are derived from bitmap columns in the physical source tables (`flags`, `flags2`–`flags12`, `sale_status`, `visitcount`, `passwordex`).

    !!! note "Duplicates"
        Some flags are exposed under multiple names for historical reasons (e.g., `gtc` and `eItemGoodTillCancelled` are equivalent). Prefer the shorter, more readable name where both exist.

    {{ read_table('docs/assets/ldm-schemas/item-fields/08-flags.tsv', sep='\t') }}

---

## Sample Queries

### Get Active Listings in a Category

```sql
SELECT
    item_id,
    auct_titl             AS title,
    bin_price_lstg_curncy AS price,
    qty_avail,
    ITEM_CNDTN_ID         AS condition_id,
    slr_id
FROM gds.item
WHERE item_site_id = 0          -- US site
  AND leaf_categ_id = 9355      -- Cell Phones & Accessories
  AND lstg_status_id = 0        -- Live listings
  AND onhold = false            -- Exclude on-hold listings
LIMIT 100;
```

### Filter by Condition and Price Range

```sql
-- New items within a price range
SELECT item_id, auct_titl, bin_price_lstg_curncy, ITEM_CNDTN_ID
FROM gds.item
WHERE item_site_id = 0
  AND ITEM_CNDTN_ID = 1000      -- 1000 = New
  AND bin_price_lstg_curncy BETWEEN 100 AND 500
  AND lstg_status_id = 0
ORDER BY bin_price_lstg_curncy ASC
LIMIT 100;
```

### Join with Attributes

```sql
-- Get brand attribute (attr_id = 1000) for items in a category
SELECT
    i.item_id,
    i.auct_titl,
    m.attr_id,
    m.value_desc AS brand
FROM gds.item i
JOIN gds.item_common_attribute_value_mapping m ON i.item_id = m.item_id
WHERE i.item_site_id = 0
  AND i.leaf_categ_id = 9355
  AND m.attr_id = 1000
LIMIT 100;
```

[More query examples →](../guides/query-examples.md)

---

## Relationships

| Target LDM | Type | How to Join |
|------------|------|-------------|
| `variation` | 1:N | `gds.variation.item_id = gds.item.item_id` |
| `product` | N:1 | `gds.product.prod_ref_id = gds.item.PRODUCT_ID` |
| `transaction` | 1:N | `gds.transaction.item_id = gds.item.item_id` |
| `item_common_attribute_value_mapping` | M:N | `m.item_id = i.item_id` |
| `item_aspect_value_mapping` | M:N | `m.item_id = i.item_id` |
| `item_business_program_mapping` | M:N | `m.item_id = i.item_id` |
| `item_picture_mapping` | M:N | `m.item_id = i.item_id` |
| `item_listing_attribute_value_mapping` | M:N | `m.item_id = i.item_id` |
| `item_shipment_attribute_value_mapping` | M:N | `m.item_id = i.item_id` |

[View full entity relationship diagram →](../index.md#entity-relationships)

---

!!! tip "Useful Links"
    - :material-swap-horizontal: [Migrating from legacy tables (DW_LSTG_ITEM, etc.)?](../guides/migration-guide.md)
    - :material-table: [Logical → Physical field mapping](../reference/ldm-design.md#ldm-schemas)
    - :material-magnify: [More query examples](../guides/query-examples.md)
