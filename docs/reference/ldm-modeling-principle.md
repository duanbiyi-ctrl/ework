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
- ✅ **Item** - has `item_id`, independent lifecycle, relates to Variation/Product/Deal
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

**Example**: `DW_PES_ELGBLT_HIST` → `dw_pes_elgblt_hist` (Item ↔ Business Program mapping)
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


