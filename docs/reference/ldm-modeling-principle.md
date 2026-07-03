# Modeling Strategy

This document explains the unified strategy for identifying entities, attributes, and relationships in Logical Data Model Design.

---

## Step 1: Object Identification

### 1. Entity

A business object that satisfies the following identification principles:

#### Principle 1: Unique Identifier

Has unique identifier that represents individual instance.

#### Principle 2: Independent Lifecycle

Can be created, updated, or deleted independently of other entities.

#### Principle 3: Referenced by Multiple Entities

Participates in relationships with multiple entities.

**Examples:**
- ✅ **Item** - has `item_id`, independent lifecycle, relates to Variation/Product
- ✅ **Product** - has `product_id` (ePID), exists independently, referenced by multiple items
- ✅ **Trait** - individual instance referenced by multiple entities

---

### 2. Entity Attribute

A property that belongs to and describes a single entity. It has no independent existence outside the entity.

**Examples:**
- `item_title` - describes Item

---

### 3. Relationship

A connection between two or more entities. Relationships can be one-to-many (1:N), many-to-one (N:1), or many-to-many (M:N).

#### 1:N (One-to-Many) / N:1 (Many-to-One)

One entity instance can be associated with multiple instances of another entity. Foreign key resides in the "many" side.

**Example: Item → Variation**
```
Item (1) ─────< Variation (N)

One item has multiple variations
```

#### M:N (Many-to-Many)

Multiple instances on both sides can be associated with each other.

**Example: Item ↔ Attribute**
```
Item (M) >─────< Attribute (N)

An Item can have multiple Attributes
An Attribute can be used by multiple Items

```
---

### 4. Relationship Attribute

A property that belongs to the **relationship between two entities**, not to either entity alone. It describes the connection, not the entities themselves.

**Examples:**
- `photo_count` - in Item ↔ Trait mapping, describes how many photos this item has for this trait


--- 

## Step 2: LDM Definition

Based on Step 1 identification, define logical data models:

### Entity → LDM
- Create dedicated LDM for each entity
- Primary key: entity's unique identifier  
- Fields: entity attributes

### Relationship → LDM Structure
- **1:N / N:1**: Foreign key in the "many" side's LDM
- **M:N**: 
  - **Long-term vision**: Query entity LDMs directly, system auto-materializes joins
  - **Short-term approach**: Create mapping LDM (see Step 3 for details)

## Relationship Modeling and Querying

**1. For 1:N / N:1 Relationships**

Query from the "many" side entity:

```sql
-- Example: Get variations for an item (1:N)
SELECT 
    v.item_id,
    v.variation_id,
    v.variation_sku,
    v.variation_price
FROM gds.variation v
WHERE v.item_id = 123456789;
```

**2. For M:N Relationships**

**Current Approach** - Pre-joined denormalized mapping tables are modeled as LDM entities for direct consumption:

| Relationship | Mapping LDM Name                           | Primary Keys                                                                                           | Physical Sources         | Details                                                  |
|--------------|--------------------------------------------|--------------------------------------------------------------------------------------------------------|--------------------------|----------------------------------------------------------|
| Item ↔ Attribute Value (Common Attributes) | **item_common_attribute_value_mapping**                  | `item_id`, `attr_id`, `value_id`                                                                       | DW_ATTR_DETAIL_VALUES    | [View Details →](../relationships/item_common_attribute_value_mapping.md) |
| Item ↔ Attribute Value (Listing) | **item_listing_attribute_value_mapping**                       | `item_id`, `gcs_id`, `vcs_id`, `lstg_attr_id`, `value_id`, `value_desc`                                | DW_ATTR_LSTG_DTL         |                                                          |
| Item ↔ Attribute Value (Shipment) | **item_shipment_attribute_value_mapping**                 | `item_id`, `gcs_id`, `vcs_id`, `shpmt_attr_id`, `value_id`, `value_desc`                               | DW_ATTR_SHPMT_DTL </br> DW_ATTR_SHPMT_DTL_COLD |                                                          |
| Item ↔ Attribute Value (Fitment) | **item_fitment_attribute_value_mapping**                     | `item_id`, `auct_end_dt`, `ftmnt_grp_id`, `ftmnt_name`, `ftmnt_value_text`, `src_ind`, `cmbntn_grp_id` | DW_LSTG_ITEM_FTMNT       |                                                          |
| Item ↔ Attribute Value (Tags) | **item_tag_attribute_value_mapping**                   | `item_id`, `gcs_id`, `vcs_id`, `lstg_attr_id`, `tag_name`, `tag_value_txt`                             | DW_ATTR_LSTG_TAG_DTL     |                                                          |
| Item ↔ Attribute Value (Tax) | **item_tax_attribute_value_mapping**                          | `item_id`, `sale_tax_rate`, `jrsdctn_cntry_id`, `jrsdctn_tx`                                           | LSTG_SALE_TAX            |                                                          |
| Item ↔ Picture | **item_picture_mapping**                          | `item_id`, `trait_name`                                                                                | LSTG_ITEM_PIC            |                                                          |
| Item ↔ Aspect Value | **item_aspect_value_mapping**                | `item_id`, `aspect_name`, `aspect_value_name`                                                          | ITEM_ASPCT_CLSSFCTN_SAP  |                                                          |
| Variation ↔ Aspect Value | **variation_aspect_value_mapping**                | `variation_id`, `aspect_name`, `aspect_value_name`                                                     | VRTN_ASPCT_CLSSFCTN_SAP  |                                                          |
| Variation ↔ Trait | **variation_trait_mapping**                   | `variation_id`, `trait_name`                                                                           | LSTG_ITEM_VRTN_TRAIT     |                                                          |

```sql
-- Example: Get item attributes using mapping table
SELECT 
    i.item_id,
    i.auct_titl AS title,
    m.attr_id,
    m.value_desc
FROM gds.item i
JOIN gds.item_common_attribute_value_mapping m ON i.item_id = m.item_id
WHERE i.item_site_id = 0
  AND m.attr_id = 1000
LIMIT 100;
```

**Future Vision** - The long-term vision is to abstract M:N relationships into more intuitive entity-relationship models with dynamic materialization on DDF. This follows the modeling strategy described in this document.

---

---

---

## Step 3: Physical Source Mapping

Map physical Hive tables to LDMs based on table granularity and type.

### 1. Granularity Analysis

Analyze physical table primary key structure to determine granularity:

- **Single entity key** (e.g., `item_id`) → Entity table
- **Composite key with two entity FKs** (e.g., `item_id + attr_id`) → Relationship table (M:N)
- **Composite key with entity FK + dimensions** (e.g., `item_id + snapshot_date`) → Historical/SCD table
- **Aggregated dimensions** (e.g., `category_id + date`) → Summary table

### 2. Mapping Strategy by Table Type

#### Entity Tables → Entity LDM

Physical tables with entity-level granularity map to entity LDMs.

- **Single source**: One physical table → One LDM (e.g., `CTLG_PROD_FACT` → `product`)
- **Multi-source**: Multiple physical tables → One LDM (e.g., 11 tables → `item`)
  - Principle: One field has one source table (for given update frequency)
  - Merge complementary attributes from different sources

#### Relationship Tables → Mapping LDM (M:N)

**Short-term Approach**: Physical M:N tables map directly to mapping LDMs with pre-denormalized attributes.

Mapping LDMs include not just foreign keys, but also denormalized entity attributes and relationship attributes.

**Example**: `dw_attr_detail_values` (physical table) → `item_common_attribute_value_mapping` (mapping LDM)
```sql
-- Physical table structure
item_id, attr_id, value_id, attr_name, value_desc

-- Maps to: Item (M) ↔ Attribute (N)
-- Denormalized: attr_name, value_desc
-- Relationship attributes: none in this case
```

**Benefits**: Faster queries, simpler SQL (2-table join instead of 3-table join)

#### SCD2 Tables → Entity/Relationship LDM with Temporal Filtering

Physical SCD2 tables track historical changes over time.

**Mapping approach**:
- Map to corresponding entity or relationship LDM
- Add temporal filtering logic in queries

**Example**: an entity history table with effective start/end timestamps
```sql
-- Current state query
WHERE eff_end_dt IS NULL

-- Point-in-time query  
WHERE snapshot_date BETWEEN eff_start_dt AND eff_end_dt
```

#### Summary Tables → Typically Not Modeled

Aggregated summary tables contain pre-computed metrics and typically are **not** modeled as LDMs.

**Rationale**: 
- Different granularity (aggregated vs entity-level)
- Pre-computed views, not source of truth
- Query directly from physical table when needed

**Example**: `CTLG_BRWS_NODE_SD` (browse node summary by date) - used as-is, not abstracted into LDM

### 3. Long-term Vision: DDF Dynamic Materialization

In the future, the platform's **Declarative Data Flow (DDF)** capability will enable:

- **Dynamic Materialization**: Automatically optimize M:N joins based on query patterns
- **Transparent Performance**: No manual denormalization needed
- **Simplified Queries**: Users query entity LDMs directly, system auto-generates mapping tables

**Note:** DDF is a long-term roadmap item. For now, use the pre-denormalized mapping LDMs provided.

