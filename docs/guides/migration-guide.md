# Migration Guide

How to migrate from legacy Hive tables to Item Domain LDM.

---

## Overview

Item Domain LDM consolidates multiple fragmented Hive tables into unified logical entities. This guide helps you migrate existing queries to the new LDM interface.

**Benefits of migrating:**

- **Simpler queries**: Query by business concepts instead of physical table names
- **Better performance**: Optimized materialized views on DLS
- **Unified interface**: Consistent access pattern across all item-related data
- **Governed data**: Standardized, quality-controlled data models

---

## Quick Migration Path

### Step 1: Identify Your Legacy Sources

List the legacy Hive tables and fields used by your current query. Use the reference below to find the corresponding Item Domain LDM entity.

### Step 2: Check Fields and Replace with LDM Entities

Confirm the required fields exist in the target LDM entity, then replace legacy table and field references with the corresponding `gds.*` LDM entity and LDM fields. Most migrations are table or field substitutions.

### Step 3: Test and Validate

Compare results between legacy and LDM queries to ensure row counts, filters, and key business metrics remain consistent.

---

## Common Migration Patterns

### Basic Item Query

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

### Migrating Flag Fields

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

??? abstract "Full legacy flag mapping"

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
| **LSTG_ITEM_CNDTN** | `gds.item` | `item_id` | Item condition attributes |
| **DIM_ITEM** | `gds.item` | `item_id` | Item dimension attributes |
| **SLNG_LSTG_SUPER_FACT** | `gds.item` | `item_id` | Selling listing fact fields |
| **CTLG_ITEM_FACT** | `gds.item` | `item_id` | Catalog-linked item facts |
| **LSTG_ITEM_DESC_DIM** | `gds.item` | `item_id` | Listing description fields |
| **LSTG_ITEM_VRTN** | `gds.variation` | `variation_id`, `item_id` | Multi-SKU variations |
| **DW_LSTG_ITEM_PROD_REF** | `gds.product` | `item_id`, `prod_ref_id` | Product catalog reference |

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
- **Feedback**: Share uncovered migration scenarios so this guide can be expanded.

---
