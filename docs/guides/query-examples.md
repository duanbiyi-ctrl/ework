# Query Examples

This page provides practical, scenario-based query examples for common use cases.

## Quick Navigation

- [Query Item Basics](#query-item-basics)
**Others to be added.** for example, how to query different types of views, frequencies.
---

## Query Item Basics

### Example 1: Basic Item Query

Get basic information for items in a specific category:

```sql
SELECT 
    item_id,
    item_title,
    item_price,
    item_quantity,
    seller_id
FROM gds.item
WHERE item_site_id = 0           -- US site
  AND item_cndtn_id = 1000       -- New condition
LIMIT 100;
```

