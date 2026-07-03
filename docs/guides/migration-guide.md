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
| `DW_ATTR_DETAIL_VALUES` | `gds.item_common_attribute_value_mapping` | Low - Direct mapping |
| `DW_ATTR_LSTG_DTL` | `gds.item_listing_attribute_value_mapping` | Low - Direct mapping |
| `ITEM_ASPCT_CLSSFCTN_SAP` | `gds.item_aspect_value_mapping` | Low - Direct mapping |

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
        auct_titl             AS title,
        bin_price_lstg_curncy AS price,
        leaf_categ_id,
        slr_id,
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
        auct_titl             AS title,
        bin_price_lstg_curncy AS price,
        leaf_categ_id,
        slr_id,
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
        i.auct_titl AS title,
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
        i.auct_titl AS title,
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

Migrate attribute queries to `gds.item_common_attribute_value_mapping`.

=== "Before (Legacy)"
    ```sql
    SELECT 
        i.item_id,
        i.auct_titl AS title,
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
        i.auct_titl AS title,
        a.attr_id,
        a.value_desc
    FROM gds.item i
    JOIN gds.item_common_attribute_value_mapping a ON i.item_id = a.item_id
    WHERE i.item_site_id = 0
      AND a.attr_id = 1000  -- Brand
    LIMIT 100;
    ```

**Changes:**
- ✅ Replace `DW_LSTG_ITEM` → `gds.item`
- ✅ Replace `DW_ATTR_DETAIL_VALUES` → `gds.item_common_attribute_value_mapping`
- ✅ JOIN logic unchanged

---

### Scenario 4: Item with Product Reference (ePID)

Migrate product reference queries.

=== "Before (Legacy)"
    ```sql
    SELECT 
        i.item_id,
        i.auct_titl AS title,
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
        auct_titl AS title,
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

### Scenario 5: Migrating Flag Fields

In legacy DW tables, many item indicator attributes were packed into bit-level flag columns such as `flags`, `flags2`, `flags09`, `flags12`, `passwrd`, `passwordex`, `sale_status`, and `visitcount`. In Item LDM, these decoded flags are exposed directly as individual 0/1 integer columns, so consumers should select the LDM column instead of repeating bitwise logic in every query.

=== "Before (Legacy)"
    ```sql
    SELECT
        item_id,
        CASE WHEN (CAST(flags AS BIGINT) & 262144) = 262144 THEN 1 ELSE 0 END AS is_seller_on_vacation
    FROM DW_LSTG_ITEM;
    ```

=== "After (LDM)"
    ```sql
    SELECT
        item_id,
        is_seller_on_vacation
    FROM gds.item;
    ```

**Migration rule:** replace each legacy bit extraction expression with the corresponding Item LDM 0/1 indicator column. If your downstream query needs boolean semantics, compare the LDM column to `1` (for example, `is_seller_on_vacation = 1`).

| Legacy source field | Legacy flag logic | Item LDM column |
|---|---|---|
| `passwrd` | `CASE WHEN (CAST(passwrd AS BIGINT) & 4096) = 4096 THEN 1 ELSE 0 END` | `is_amex_accepted` |
| `flags` | `CASE WHEN (CAST(flags AS BIGINT) & 4) = 4 THEN 1 ELSE 0 END` | `is_tax_applied_to_shipping` |
| `flags7` | `CASE WHEN (CAST(flags7 AS BIGINT) & 16777216) = 16777216 THEN 1 ELSE 0 END` | `is_best_offer_auto_accept_enabled` |
| `flags5` | `CASE WHEN (CAST(flags5 AS BIGINT) & 33554432) = 33554432 THEN 1 ELSE 0 END` | `is_best_offer_auto_decline_enabled` |
| `sale_status` | `CASE WHEN (CAST(sale_status AS BIGINT) & 134217728) = 134217728 THEN 1 ELSE 0 END` | `is_auto_relist_enabled` |
| `flags4` | `CASE WHEN (CAST(flags4 AS BIGINT) & 131072) = 131072 THEN 1 ELSE 0 END` | `is_best_offer_enabled` |
| `sale_status` | `CASE WHEN (CAST(sale_status AS BIGINT) & 4) = 4 THEN 1 ELSE 0 END` | `is_bids_finalized` |
| `flags4` | `CASE WHEN (CAST(flags4 AS BIGINT) & 268435456) = 268435456 THEN 1 ELSE 0 END` | `is_cash_in_person_accepted` |
| `passwrd` | `CASE WHEN (CAST(passwrd AS BIGINT) & 65536) = 65536 THEN 1 ELSE 0 END` | `is_cod_accepted` |
| `flags3` | `CASE WHEN (CAST(flags3 AS BIGINT) & 4096) = 4096 THEN 1 ELSE 0 END` | `is_cod_prepay_delivery_accepted` |
| `sale_status` | `CASE WHEN (CAST(sale_status AS BIGINT) & 256) = 256 THEN 1 ELSE 0 END` | `is_digital_delivery_supported` |
| `passwrd` | `CASE WHEN (CAST(passwrd AS BIGINT) & 8192) = 8192 THEN 1 ELSE 0 END` | `is_discover_accepted` |
| `flags7` | `CASE WHEN (CAST(flags7 AS BIGINT) & 16) = 16 THEN 1 ELSE 0 END` | `is_intl_shipping_promotion` |
| `flags12` | `CASE WHEN (CAST(flags12 AS BIGINT) & 524288) = 524288 THEN 1 ELSE 0 END` | `is_duplicate_auction` |
| `visitcount` | `CASE WHEN (CAST(visitcount AS BIGINT) & 262144) = 262144 THEN 1 ELSE 0 END` | `is_ebay_managed_shipping_eligible` |
| `flags2` | `CASE WHEN (CAST(flags2 AS BIGINT) & 65536) = 65536 THEN 1 ELSE 0 END` | `is_ebay_vault_listing` |
| `flags12` | `CASE WHEN (CAST(flags12 AS BIGINT) & 268435456) = 268435456 THEN 1 ELSE 0 END` | `is_gsp_shipping_enabled` |
| `visitcount` | `CASE WHEN (CAST(visitcount AS BIGINT) & 16777216) = 16777216 THEN 1 ELSE 0 END` | `is_gtc` |
| `visitcount` | `CASE WHEN (CAST(visitcount AS BIGINT) & 268435456) = 268435456 THEN 1 ELSE 0 END` | `is_immediate_payment_required` |
| `visitcount` | `CASE WHEN (CAST(visitcount AS BIGINT) & 8192) = 8192 THEN 1 ELSE 0 END` | `is_irregular_package` |
| `flags11` | `CASE WHEN (CAST(flags11 AS BIGINT) & 16384) = 16384 THEN 1 ELSE 0 END` | `is_business_policy_item` |
| `flags4` | `CASE WHEN (CAST(flags4 AS BIGINT) & 4194304) = 4194304 THEN 1 ELSE 0 END` | `is_buyer_responsible_for_shipping` |
| `flags7` | `CASE WHEN (CAST(flags7 AS BIGINT) & 131072) = 131072 THEN 1 ELSE 0 END` | `is_no_email_contact_supported` |
| `flags5` | `CASE WHEN (CAST(flags5 AS BIGINT) & 1) = 1 THEN 1 ELSE 0 END` | `is_instore_pickup_eligible` |
| `passwordex` | `CASE WHEN (CAST(passwordex AS BIGINT) & 32768) = 32768 THEN 1 ELSE 0 END` | `is_restricted_bidding` |
| `flags2` | `CASE WHEN (CAST(flags2 AS BIGINT) & 256) = 256 THEN 1 ELSE 0 END` | `is_restricted_to_business_user` |
| `flags` | `CASE WHEN (CAST(flags AS BIGINT) & 262144) = 262144 THEN 1 ELSE 0 END` | `is_seller_on_vacation` |
| `flags09` | `CASE WHEN (CAST(flags09 AS BIGINT) & 33554432) = 33554432 THEN 1 ELSE 0 END` | `is_variation` |
| `flags7` | `CASE WHEN (CAST(flags7 AS BIGINT) & 1024) = 1024 THEN 1 ELSE 0 END` | `is_on_promotional_sale` |
| `flags4` | `CASE WHEN (CAST(flags4 AS BIGINT) & 67108864) = 67108864 THEN 1 ELSE 0 END` | `is_loan_check_accepted` |
| `flags09` | `CASE WHEN (CAST(flags09 AS BIGINT) & 1073741824) = 1073741824 THEN 1 ELSE 0 END` | `is_merchant_fulfillment_supported` |
| `flags` | `CASE WHEN (CAST(flags AS BIGINT) & 512) = 512 THEN 1 ELSE 0 END` | `is_managed_shipping_opted_in` |
| `flags09` | `CASE WHEN (CAST(flags09 AS BIGINT) & 2) = 2 THEN 1 ELSE 0 END` | `is_marketplace_visible` |
| `flags10` | `CASE WHEN (CAST(flags10 AS BIGINT) & 131072) = 131072 THEN 1 ELSE 0 END` | `is_managed_by_inventory` |
| `passwrd` | `CASE WHEN (CAST(passwrd AS BIGINT) & 512) = 512 THEN 1 ELSE 0 END` | `is_money_order_accepted` |
| `flags09` | `CASE WHEN (CAST(flags09 AS BIGINT) & 4) = 4 THEN 1 ELSE 0 END` | `has_free_shipping_pre_promo` |
| `flags09` | `CASE WHEN (CAST(flags09 AS BIGINT) & 1) = 1 THEN 1 ELSE 0 END` | `is_free_shipping_sale` |
| `flags5` | `CASE WHEN (CAST(flags5 AS BIGINT) & 1024) = 1024 THEN 1 ELSE 0 END` | `is_on_hold` |
| `passwrd` | `CASE WHEN (CAST(passwrd AS BIGINT) & 16384) = 16384 THEN 1 ELSE 0 END` | `is_other_payment_accepted` |
| `passwordex` | `CASE WHEN (CAST(passwordex AS BIGINT) & 2147483648) = 2147483648 THEN 1 ELSE 0 END` | `is_other_online_payment_accepted` |
| `flags4` | `CASE WHEN (CAST(flags4 AS BIGINT) & 1048576) = 1048576 THEN 1 ELSE 0 END` | `is_paisapay_accepted` |
| `flags08` | `CASE WHEN (CAST(flags08 AS BIGINT) & 4194304) = 4194304 THEN 1 ELSE 0 END` | `is_paisapay_escrow_enabled` |
| `flags08` | `CASE WHEN (CAST(flags08 AS BIGINT) & 8388608) = 8388608 THEN 1 ELSE 0 END` | `is_paisapay_escrow_emi_enabled` |
| `passwrd` | `CASE WHEN (CAST(passwrd AS BIGINT) & 131072) = 131072 THEN 1 ELSE 0 END` | `is_payment_in_description` |
| `visitcount` | `CASE WHEN (CAST(visitcount AS BIGINT) & 2097152) = 2097152 THEN 1 ELSE 0 END` | `is_paypal_accepted` |
| `passwrd` | `CASE WHEN (CAST(passwrd AS BIGINT) & 1024) = 1024 THEN 1 ELSE 0 END` | `is_personal_check_accepted` |
| `flags3` | `CASE WHEN (CAST(flags3 AS BIGINT) & 8192) = 8192 THEN 1 ELSE 0 END` | `is_postal_transfer_accepted` |
| `sale_status` | `CASE WHEN (CAST(sale_status AS BIGINT) & 512) = 512 THEN 1 ELSE 0 END` | `is_price_guarantee` |
| `flags3` | `CASE WHEN (CAST(flags3 AS BIGINT) & 2048) = 2048 THEN 1 ELSE 0 END` | `is_prepay_delivery_accepted` |
| `sale_status` | `CASE WHEN (CAST(sale_status AS BIGINT) & 64) = 64 THEN 1 ELSE 0 END` | `is_ebay_plus_supported` |
| `flags7` | `CASE WHEN (CAST(flags7 AS BIGINT) & 8) = 8 THEN 1 ELSE 0 END` | `is_domestic_shipping_promotion` |
| `flags5` | `CASE WHEN (CAST(flags5 AS BIGINT) & 262144) = 262144 THEN 1 ELSE 0 END` | `is_partner_dealer_auto_listing` |
| `flags2` | `CASE WHEN (CAST(flags2 AS BIGINT) & 4194304) = 4194304 THEN 1 ELSE 0 END` | `is_relisted` |
| `flags` | `CASE WHEN (CAST(flags AS BIGINT) & 1048576) = 1048576 THEN 1 ELSE 0 END` | `is_scheduled_listing` |
| `flags11` | `CASE WHEN (CAST(flags11 AS BIGINT) & 32768) = 32768 THEN 1 ELSE 0 END` | `is_seller_policy_overridden` |
| `flags2` | `CASE WHEN (CAST(flags2 AS BIGINT) & 262144) = 262144 THEN 1 ELSE 0 END` | `is_sell_similar` |
| `passwrd` | `CASE WHEN (CAST(passwrd AS BIGINT) & 2048) = 2048 THEN 1 ELSE 0 END` | `is_visa_mc_accepted` |

---

## Table Mapping Reference

Detailed mapping from legacy tables to LDM entities:

| Legacy Table | LDM Entity | Key Columns | Notes |
|--------------|------------|-------------|-------|
| **DW_LSTG_ITEM** | `gds.item` | `item_id` | Core item entity |
| **LSTG_ITEM_VRTN** | `gds.variation` | `variation_id`, `item_id` | Multi-SKU variations |
| **DW_LSTG_ITEM_PROD_REF** | `gds.product` | `item_id`, `prod_ref_id` | Product catalog reference |
| **DW_ATTR_DETAIL_VALUES** | `gds.item_common_attribute_value_mapping` | `item_id`, `attr_id` | Common attributes |
| **DW_ATTR_LSTG_DTL** | `gds.item_listing_attribute_value_mapping` | `item_id`, `lstg_attr_id` | Listing attributes |
| **DW_ATTR_SHPMT_DTL** | `gds.item_shipment_attribute_value_mapping` | `item_id`, `shpmt_attr_id` | Shipment attributes |
| **ITEM_ASPCT_CLSSFCTN_SAP** | `gds.item_aspect_value_mapping` | `item_id`, `aspect_name` | SAP aspects |
| **VRTN_ASPCT_CLSSFCTN_SAP** | `gds.variation_aspect_value_mapping` | `variation_id`, `aspect_name` | Variation aspects |
| **LSTG_ITEM_VRTN_TRAIT** | `gds.variation_trait_mapping` | `variation_id`, `trait_name` | Variation traits |

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
