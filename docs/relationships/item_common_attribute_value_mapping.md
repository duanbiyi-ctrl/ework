# Item - Attribute Value Mapping

[← Back to Home](../index.md)

## Overview

**Mapping LDM Name:** `item_common_attribute_value_mapping`

**Description:** Many-to-many relationship between Items and Attribute Values using the EAV (Entity-Attribute-Value) pattern for basic item attributes.

**Primary Keys:** `item_id`, `attr_id`, `value_id`

---

## Schema Structure

```
item_id        BIGINT      FK to Item
attr_id        BIGINT      Attribute identifier
attr_name      VARCHAR     Attribute name (denormalized)
value_id       BIGINT      Value identifier
value_desc     VARCHAR     Attribute value (denormalized)
```

---

## Sample Queries

### Get All Attributes for an Item

```sql
SELECT 
    item_id,
    attr_name,
    value_desc
FROM gds.item_common_attribute_value_mapping
WHERE item_id = 123456789;
```

### Filter by Specific Attribute

```sql
-- Get brand information for items
SELECT 
    item_id,
    attr_name,
    value_desc
FROM gds.item_common_attribute_value_mapping
WHERE item_id IN (123456789, 987654321)
  AND attr_name = 'Brand';
```

### Join with Item Entity

```sql
-- Get items with specific attribute value
SELECT 
    i.item_id,
    i.item_title,
    i.item_price,
    m.attr_name,
    m.value_desc
FROM gds.item i
JOIN gds.item_common_attribute_value_mapping m ON i.item_id = m.item_id
WHERE i.item_site_id = 0
  AND m.attr_name = 'Brand'
  AND m.value_desc = 'Apple'
LIMIT 100;
```

### Multiple Attributes Filter

```sql
-- Get items matching multiple attribute criteria
SELECT 
    i.item_id,
    i.item_title,
    MAX(CASE WHEN m.attr_name = 'Brand' THEN m.value_desc END) AS brand,
    MAX(CASE WHEN m.attr_name = 'Model' THEN m.value_desc END) AS model,
    MAX(CASE WHEN m.attr_name = 'Color' THEN m.value_desc END) AS color
FROM gds.item i
JOIN gds.item_common_attribute_value_mapping m ON i.item_id = m.item_id
WHERE i.item_site_id = 0
  AND m.attr_name IN ('Brand', 'Model', 'Color')
GROUP BY i.item_id, i.item_title
HAVING MAX(CASE WHEN m.attr_name = 'Brand' THEN m.value_desc END) = 'Apple'
LIMIT 100;
```
---

## Physical Source

| Physical Table | Description | Update Frequency |
|----------------|-------------|------------------|
| DW_ATTR_DETAIL_VALUES | Basic item attributes (majority of attributes) | Daily |


