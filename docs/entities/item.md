# Item LDM

[← Back to Entity Catalog](../index.md)

## Overview

**LDM Name:** `item`

**Description:** The core listing entity representing an item/product listing on the platform. Contains comprehensive information about items including title, pricing, category, seller, and listing lifecycle.

**Primary Key:** `item_id`

**Relationship Type:** Base Entity (can be queried independently)

---

## Key Fields

### Identifiers
- `item_id` - Unique item identifier (Primary Key)
- `item_site_id` - Site ID (0=US, 3=UK, 15=Australia, etc.)
- `seller_id` - Seller user ID

### Item Information
- `item_title` - Item title/name
- `item_subtitle` - Item subtitle (optional)
- `item_price` - Current item price
- `item_quantity` - Available quantity
- `item_cndtn_id` - Item condition ID
  - 1000 = New
  - 3000 = Used
  - 1500 = New other
  - 2000 = Manufacturer refurbished

### Category & Classification
- `leaf_categ_id` - Leaf category ID
- `meta_categ_id` - Meta category ID
- `l1_categ_id` - Level 1 category ID
- `l2_categ_id` - Level 2 category ID

### Listing Lifecycle
- `item_start_dt` - Listing start date/time
- `item_end_dt` - Listing end date/time
- `listing_type` - Listing format (Auction, Fixed Price, etc.)
- `listing_status` - Current status (Active, Ended, etc.)

### Product Reference
- `prod_ref_id` - Product reference ID (ePID) - Links to Product catalog

### Metrics
- `view_count` - Number of views
- `watch_count` - Number of watchers
- `sold_quantity` - Quantity sold

### Additional Attributes
- `shipping_type` - Shipping method
- `returns_accepted` - Whether returns are accepted
- `item_location` - Item location (city, state, country)
- Plus 80+ additional fields...

**Note:** The complete field list contains 100+ fields. Contact the GDS team for the full schema definition.

---

## Sample Queries

### Basic Item Query

```sql
-- Get items in a specific category
SELECT 
    item_id,
    item_title,
    item_price,
    item_quantity,
    seller_id,
    item_cndtn_id
FROM item
WHERE item_site_id = 0
  AND leaf_categ_id = 58058  -- Cell Phones & Accessories
  AND item_cndtn_id = 1000   -- New condition
LIMIT 100;
```

### Filter by Price Range

```sql
-- Find items within price range
SELECT 
    item_id,
    item_title,
    item_price,
    item_start_dt
FROM item
WHERE item_site_id = 0
  AND leaf_categ_id = 58058
  AND item_price BETWEEN 100 AND 500
  AND item_quantity > 0
ORDER BY item_price ASC
LIMIT 100;
```

### Recently Listed Items

```sql
-- Get recently listed items
SELECT 
    item_id,
    item_title,
    item_price,
    item_start_dt,
    seller_id
FROM item
WHERE item_site_id = 0
  AND leaf_categ_id = 58058
  AND item_start_dt >= CURRENT_DATE - INTERVAL '7' DAY
ORDER BY item_start_dt DESC
LIMIT 100;
```

### Join with Product Catalog

```sql
-- Items with product catalog information
SELECT 
    i.item_id,
    i.item_title,
    i.item_price,
    p.prod_ref_id,
    p.product_name,
    p.product_brand
FROM item i
LEFT JOIN product p ON i.prod_ref_id = p.prod_ref_id
WHERE i.item_site_id = 0
  AND i.leaf_categ_id = 58058
LIMIT 100;
```

[More query examples →](../guides/query-examples.md#query-item-basics)

---

## Relationships

### Outgoing Relationships (Item →)

| Target Entity | Type | Description | Mapping Table |
|---------------|------|-------------|---------------|
| Variation | 1:N | Item has multiple variations | `variation` |
| Product | N:1 | Item references a product catalog | Join on `prod_ref_id` |
| Attribute | M:N | Item has multiple attributes | `item_attribute_mapping` |
| Aspect | M:N | Item has SAP aspects | `item_aspect_mapping` |
| Business Program | M:N | Item eligibility in programs | `item_business_program_mapping` |
| Picture | M:N | Item pictures by trait | `item_picture_mapping` |
| Transaction | 1:N | Item has transactions | `transaction` |

[View complete relationship diagram →](../index.md#entity-relationship-diagram)

---

## Physical Sources

The Item LDM integrates data from **11 physical Hive tables**:

| Physical Table | Content | Update Frequency |
|----------------|---------|------------------|
| DIM_ITEM | Core item dimensions | Daily |
| SLNG_LSTG_SUPER_FACT | Selling listing super fact | Daily |
| DW_LSTG_ITEM | Listing item data warehouse | Daily |
| DW_LSTG_ITEM_FREQ | High-frequency item updates | Hourly |
| CTLG_ITEM_FACT | Catalog item fact | Daily |
| LSTG_ITEM_DESC_DIM | Item description dimension | Daily |
| LSTG_ITEM_CNDTN | Item condition | Daily |
| LSTG_ITEM_VIEW_CNTR | Item view counter | Hourly |
| DW_LSTG_ITEM_PROD_REF | Item product reference | Daily |
| CTLG_PROD_ITEM_FACT | Product-item mapping | Daily |
| DW_ITEM_REVISIONS | Item change log (raw) | Real-time |
| ITEM360_SRCH_EMBEDDING | Item search embeddings | Daily |

**Partitioning:** `item_site_id`, `snapshot_date` (varies by source table)

**Key Principle:** For any given field, there is exactly one source table for a given update frequency.

[View complete physical mappings →](../reference/table-mappings.md#item)

---

## Performance Considerations

### Always Use Partition Filters

Item tables are partitioned by `item_site_id`. Always include this in your WHERE clause:

```sql
-- Good
WHERE item_site_id = 0  -- Filters to single partition

-- Bad
WHERE item_title LIKE '%iPhone%'  -- Scans all partitions
```

### Limit Result Sets

Use `LIMIT` for exploratory queries:

```sql
SELECT * FROM item
WHERE item_site_id = 0
LIMIT 100;  -- Prevents scanning millions of rows
```

### Select Specific Columns

Avoid `SELECT *` - only select columns you need:

```sql
-- Good
SELECT item_id, item_title, item_price
FROM item;

-- Bad
SELECT *  -- Returns 100+ columns
FROM item;
```

---

## Related Documentation

- [Entity Catalog](../index.md) - All LDM entities
- [Query Examples](../guides/query-examples.md) - More item query examples
- [Modeling Strategy](../reference/ldm-modeling-principle.md) - How entities are defined
- [Physical Table Mappings](../reference/table-mappings.md#item) - Detailed source information
