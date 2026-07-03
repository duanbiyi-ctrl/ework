# Item Domain Logical Data Model (LDM)

## Overview

Item LDM is the **standard, governed logical interface** for eBay item-domain data, abstracting fragmented underlying physical sources to enable self-service consumption on GDS platform to support business use cases such as data engineering, analytics, and ML feature engineering.

---

## Core Concepts

Understanding Item domain fundamentals:

<div class="grid cards" markdown>

- :material-cube-outline: **Item, Variation, Product**

    ---
    
    Core entity hierarchy: listings (item), SKUs (variation), and catalog references (product/ePID)

- :material-tag-text-outline: **Attributes vs Aspects**

    ---
    
    Two ways to describe items: seller-provided attributes vs SAP-processed aspects with higher quality

- :material-palette-outline: **Variation Traits**

    ---
    
    SKU-level differentiators like Color, Size, Network that distinguish variations

</div>

[Learn core concepts in detail →](concepts/core-concepts.md)

---

## Item Domain LDM Map

Here're the main LDM entities in the Item domain:

<img src="assets/item-domain-entity-relationship.png" alt="Item Domain LDM Entity Map" width="700"/>


!!! tip "New to Item LDM?"
    Start with **item**, **variation**, and **attribute** entities - they cover most common use cases.

---

## LDM Catalog

| LDM Name | Type | Description | Primary Key(s) | Details |
|----------|------|-------------|----------------|---------|
| **item** | Core entity | Core listing entity | `item_id` | [Details →](entities/item.md) |
| **variation** | Core entity | Multi-SKU variations of a listing | `variation_id` | |
| **product** | Core entity | Product catalog reference (ePID) | `prod_ref_id` | |
| **attribute** | Core entity | Item attributes such as brand, model, color, and material | `attribute_id` | |
| **attribute_value** | Core entity | Attribute values such as Nike, red, or leather | `attribute_value_id` | |
| **trait** | Core entity | Variation-level traits such as color, size, and material | `trait_name` | |
| **aspect** | Core entity | SAP-generated classification aspects | `aspect_name`, `namespace_id`, `classifier_id` | |
| **aspect_value** | Core entity | Aspect value definitions | `aspect_value_name` | |
| **msku** | Core entity | Multi-SKU listing representation | `msku_id` | |
| **ssku** | Core entity | Single-SKU listing representation | `ssku_id` | |
| **site** | Lookup entity | eBay marketplace/site lookup for listing, seller, and bidder site IDs | `site_id` | |
| **category** | Lookup entity | eBay category hierarchy lookup, including meta, intermediate, and leaf categories | `site_id`, `leaf_categ_id` | |
| **country** | Lookup entity | Country lookup for item location, seller registration, and bidder registration country IDs | `country_id` | |


---

## Entity Relationships

| Relationship | Type | Description |
|--------------|------|-------------|
| **Item → Variation** | 1:N | One item has multiple variations (e.g., different sizes/colors) |
| **Item → Product** | N:1 | Items can reference product catalog/ePID records |
| **Item → MSKU** | 1:1 | Multi-SKU item representation for variation listings |
| **Item → SSKU** | 1:1 | Single-SKU item representation for non-variation listings |
| **Item ↔ Attribute** | M:N | Items have multiple attributes such as brand, model, and color |
| **Item ↔ Attribute Value** | M:N | Items are associated with specific attribute values through mapping entities |
| **Attribute ↔ Attribute Value** | M:N | One attribute can have multiple values |
| **Item ↔ Aspect** | M:N | Items have SAP-generated classification aspects |
| **Aspect ↔ Aspect Value** | M:N | One aspect can have multiple values |
| **Item ↔ Aspect Value** | M:N | Items are associated with classifier-derived aspect values |
| **Variation ↔ Aspect** | M:N | Variations have SAP aspects at variation level |
| **Variation ↔ Aspect Value** | M:N | Variations are associated with specific aspect values |
| **Variation ↔ Trait** | M:N | Variations have traits like Color, Size, Material |
| **Item ↔ Trait** | M:N | MSKU items have traits like Color, Size, Material |

---

## Quick Start

### Access Methods

=== "Spark SQL"
    Query via Spark SQL on DLS:
    
    ```sql
    -- Example: Query active US listings in a specific category
    SELECT 
        item_id,
        auct_titl             AS title,
        bin_price_lstg_curncy AS price,
        leaf_categ_id,
        slr_id
    FROM gds.item
    WHERE item_site_id = 0
      AND leaf_categ_id = 9355
      AND bin_price_lstg_curncy > 100
    LIMIT 100;
    ```

=== "DDF Python"
    Programmatic access via Declarative Data Flow (DDF): Examples to be added.

!!! tip "Migrating from Legacy Hive Tables?"
    Currently using `DW_LSTG_ITEM`, `DW_ATTR_DETAIL_VALUES`, or other legacy tables? See the [Migration Guide](guides/migration-guide.md) for step-by-step instructions to migrate your queries to Item Domain LDM.

---

## Resources

- [Query examples](guides/query-examples.md)
- [LDM modeling principles](reference/ldm-modeling-principle.md)
- [FAQ](faq.md)
