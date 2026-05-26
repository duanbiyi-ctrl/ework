# Migration Guide

How to migrate from legacy Hive tables to Item Domain LDM.

---

## Overview

Item Domain LDM consolidates 30+ fragmented Hive tables into unified logical entities. This guide helps you migrate existing queries to the new LDM interface.

**Benefits of migrating:**

- **Simpler queries**: Query by business concepts instead of physical table names
- **Better performance**: Optimized materialized views on DLS
- **Unified interface**: Consistent access pattern across all item-related data
- **Governed data**: Standardized, quality-controlled data models

---

## Quick Migration Path

### Step 1: Identify Your Legacy Table

Find your current table in the mapping below:

| Legacy Table | LDM Entity | Migration Complexity |
|--------------|------------|---------------------|
| `DW_LSTG_ITEM` | `gds.item` | Low - Direct mapping |
| `LSTG_ITEM_VRTN` | `gds.variation` | Low - Direct mapping |
| `DW_LSTG_ITEM_PROD_REF` | `gds.product` | Low - Join with item |
| `DW_ATTR_DETAIL_VALUES` | `gds.dw_attr_detail_values` | Low - Direct mapping |
| `DW_ATTR_LSTG_DTL` | `gds.dw_attr_lstg_dtl` | Low - Direct mapping |
| `ITEM_ASPCT_CLSSFCTN_SAP` | `gds.item_aspct_clssfctn_sap` | Low - Direct mapping |

### Step 2: Update Your Query

Replace the table name and schema. Most queries require minimal changes.

### Step 3: Test and Validate

Compare results between legacy and LDM queries to ensure correctness.

---

## Common Migration Scenarios

### Scenario 1: Basic Item Query

Migrate from `DW_LSTG_ITEM` to `gds.item`.

=== "Before (Legacy)"
    ```sql
    SELECT 
        item_id,
        item_title,
        item_price,
        leaf_categ_id,
        seller_id,
        item_site_id
    FROM DW_LSTG_ITEM
    WHERE item_site_id = 0
      AND leaf_categ_id = 58058
      AND auct_end_dt >= CURRENT_DATE
    LIMIT 100;
    ```

=== "After (LDM)"
    ```sql
    SELECT 
        item_id,
        item_title,
        item_price,
        leaf_categ_id,
        seller_id,
        item_site_id
    FROM gds.item
    WHERE item_site_id = 0
      AND leaf_categ_id = 58058
      AND auct_end_dt >= CURRENT_DATE
    LIMIT 100;
    ```

**Changes:**
- ✅ Replace `DW_LSTG_ITEM` → `gds.item`
- ✅ Column names remain the same
- ✅ WHERE clause unchanged

---

### Scenario 2: Item with Variations

Migrate variation queries to `gds.variation`.

=== "Before (Legacy)"
    ```sql
    SELECT 
        i.item_id,
        i.item_title,
        v.variation_id,
        v.variation_sku
    FROM DW_LSTG_ITEM i
    JOIN LSTG_ITEM_VRTN v ON i.item_id = v.item_id
    WHERE i.item_site_id = 0
      AND i.leaf_categ_id = 11450
    LIMIT 100;
    ```

=== "After (LDM)"
    ```sql
    SELECT 
        i.item_id,
        i.item_title,
        v.variation_id,
        v.variation_sku
    FROM gds.item i
    JOIN gds.variation v ON i.item_id = v.item_id
    WHERE i.item_site_id = 0
      AND i.leaf_categ_id = 11450
    LIMIT 100;
    ```

**Changes:**
- ✅ Replace `DW_LSTG_ITEM` → `gds.item`
- ✅ Replace `LSTG_ITEM_VRTN` → `gds.variation`
- ✅ JOIN logic unchanged

---

### Scenario 3: Item with Attributes

Migrate attribute queries to `gds.dw_attr_detail_values`.

=== "Before (Legacy)"
    ```sql
    SELECT 
        i.item_id,
        i.item_title,
        a.attr_id,
        a.value_desc
    FROM DW_LSTG_ITEM i
    JOIN DW_ATTR_DETAIL_VALUES a ON i.item_id = a.item_id
    WHERE i.item_site_id = 0
      AND a.attr_id = 1000  -- Brand
    LIMIT 100;
    ```

=== "After (LDM)"
    ```sql
    SELECT 
        i.item_id,
        i.item_title,
        a.attr_id,
        a.value_desc
    FROM gds.item i
    JOIN gds.dw_attr_detail_values a ON i.item_id = a.item_id
    WHERE i.item_site_id = 0
      AND a.attr_id = 1000  -- Brand
    LIMIT 100;
    ```

**Changes:**
- ✅ Replace `DW_LSTG_ITEM` → `gds.item`
- ✅ Replace `DW_ATTR_DETAIL_VALUES` → `gds.dw_attr_detail_values`
- ✅ JOIN logic unchanged

---

### Scenario 4: Item with Product Reference (ePID)

Migrate product reference queries.

=== "Before (Legacy)"
    ```sql
    SELECT 
        i.item_id,
        i.item_title,
        p.prod_ref_id,
        p.at_prod_ref_id
    FROM DW_LSTG_ITEM i
    JOIN DW_LSTG_ITEM_PROD_REF p ON i.item_id = p.item_id
    WHERE i.item_site_id = 0
      AND p.prod_ref_id IS NOT NULL
    LIMIT 100;
    ```

=== "After (LDM)"
    ```sql
    SELECT 
        item_id,
        item_title,
        prod_ref_id,
        at_prod_ref_id
    FROM gds.product
    WHERE item_site_id = 0
      AND prod_ref_id IS NOT NULL
    LIMIT 100;
    ```

**Changes:**
- ✅ Use `gds.product` entity (contains both item and product reference data)
- ✅ Simplified - no JOIN needed

---

## Table Mapping Reference

Detailed mapping from legacy tables to LDM entities:

| Legacy Table | LDM Entity | Key Columns | Notes |
|--------------|------------|-------------|-------|
| **DW_LSTG_ITEM** | `gds.item` | `item_id` | Core item entity |
| **LSTG_ITEM_VRTN** | `gds.variation` | `variation_id`, `item_id` | Multi-SKU variations |
| **DW_LSTG_ITEM_PROD_REF** | `gds.product` | `item_id`, `prod_ref_id` | Product catalog reference |
| **DW_ATTR_DETAIL_VALUES** | `gds.dw_attr_detail_values` | `item_id`, `attr_id` | Common attributes |
| **DW_ATTR_LSTG_DTL** | `gds.dw_attr_lstg_dtl` | `item_id`, `lstg_attr_id` | Listing attributes |
| **DW_ATTR_SHPMT_DTL** | `gds.dw_attr_shpmt_dtl` | `item_id`, `shpmt_attr_id` | Shipment attributes |
| **ITEM_ASPCT_CLSSFCTN_SAP** | `gds.item_aspct_clssfctn_sap` | `item_id`, `aspect_name` | SAP aspects |
| **VRTN_ASPCT_CLSSFCTN_SAP** | `gds.vrtn_aspct_clssfctn_sap` | `variation_id`, `aspect_name` | Variation aspects |
| **LSTG_ITEM_VRTN_TRAIT** | `gds.lstg_item_vrtn_trait` | `variation_id`, `trait_name` | Variation traits |

---

## Migration Checklist

Before migrating your queries:

- [ ] Identify all legacy tables used in your current queries
- [ ] Map each legacy table to its corresponding LDM entity
- [ ] Update table references from legacy to `gds.*` schema
- [ ] Test queries in development environment
- [ ] Validate results match legacy query output
- [ ] Update downstream dependencies (dashboards, reports, pipelines)
- [ ] Document migration for your team

---

## Need Help?

- **Query Examples**: See [Query Examples](query-examples.md) for more scenarios
- **Entity Details**: Check [LDM Catalog](../index.md#ldm-catalog) for full entity specifications
- **Questions**: Contact the GDS team or check [FAQ](../faq.md)

---

## Feedback

This migration guide is a living document. If you encounter migration scenarios not covered here, please share your use case so we can expand this guide.
