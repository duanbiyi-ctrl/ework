# LDM Design

This page provides detailed schema information for each LDM (Logical Data Model) in the Item Domain.

---

## LDM Overview

In current phase, following the [LDM Design Principles](./ldm-modeling-principle.md) strategy of modeling entities as LDMs and relationship data as separate LDMs, the Item Domain LDM design is structured as follows:

### Entity LDMs

| LDM Name | Primary Keys | Description | Physical Sources | Priority |
|----------|-------------|-------------|------------------|----------|
| **item** | `item_id` | Core listing entity | 11 sources:<br>- DIM_ITEM(P1)<br>- SLNG_LSTG_SUPER_FACT(P1)<br>- DW_LSTG_ITEM(P1)<br>- LSTG_ITEM_CNDTN(P1)<br>- CTLG_ITEM_FACT(P2)<br>- LSTG_ITEM_DESC_DIM(P2)<br>- CTLG_PROD_ITEM_FACT(P2)<br>- LSTG_ITEM_VIEW_CNTR(P2)<br>- DW_LSTG_ITEM_PROD_REF(P2)<br>- DW_ITEM_REVISIONS(P2)<br>- ITEM360_SRCH_EMBEDDING(P2)<br>*field-level mapping, one latency per field*<br>**Note:** DW_ITEM_REVISIONS → Maps to `item_raw` view for revision history tracking | P1 |
| **variation** | `item_vrtn_id` | Multi-SKU variations of a listing | 2 sources:<br>- LSTG_ITEM_VRTN(P1)<br>- ITEM360_SRCH_EMBEDDING_VRTN(P2) | P1 |
| **product** | `prod_ref_id` | Product catalog reference (ePID) | CTLG_PROD_FACT | P2 |
| **transaction** | `item_id`, `transaction_id` | Purchase transactions | ITEM360_DEALS_TRANS_FACT | P2 |

### Mapping LDMs

| LDM Name | Primary Keys | Description | Physical Sources                                | Priority | Note |
|----------|-------------|-------------|-------------------------------------------------|----------|------|
| **item_common_attribute_value_mapping** | `item_id`, `attr_id`, `value_id` | Item ↔ Attribute Value (Common Attributes) | DW_ATTR_DETAIL_VALUES                           | P1 | Structure may change significantly after caty migration |
| **item_listing_attribute_value_mapping** | `item_id`, `gcs_id`, `vcs_id`, `lstg_attr_id`, `value_id`, `value_desc` | Item ↔ Attribute Value (Listing) | DW_ATTR_LSTG_DTL                                | P1 | Structure may change significantly after caty migration |
| **item_shipment_attribute_value_mapping** | `item_id`, `gcs_id`, `vcs_id`, `shpmt_attr_id`, `value_id`, `value_desc` | Item ↔ Attribute Value (Shipment) | DW_ATTR_SHPMT_DTL </br> DW_ATTR_SHPMT_DTL_COLD  | P1 | Structure may change significantly after caty migration |
| **item_picture_mapping** | `item_id`, `trait_name` | Item ↔ Picture | LSTG_ITEM_PIC                                   | P1 | |
| **item_aspect_value_mapping** | `item_id`, `aspect_name` | Item ↔ Aspect | ITEM_ASPCT_CLSSFCTN_SAP                         | P1 | |
| **variation_trait_mapping** | `variation_id`, `trait_name` | Variation ↔ Trait | LSTG_ITEM_VRTN_TRAIT                            | P1 | |
| **item_fitment_attribute_value_mapping** | `item_id`, `auct_end_dt`, `ftmnt_grp_id`, `ftmnt_name`, `ftmnt_value_text`, `src_ind`, `cmbntn_grp_id` | Item ↔ Attribute Value (Fitment) | DW_LSTG_ITEM_FTMNT                              | P2 | Structure may change significantly after caty migration |
| **item_tag_attribute_value_mapping** | `item_id`, `gcs_id`, `vcs_id`, `lstg_attr_id`, `tag_name`, `tag_value_txt` | Item ↔ Attribute Value (Tags) | DW_ATTR_LSTG_TAG_DTL                            | P2 | Structure may change significantly after caty migration |
| **item_tax_attribute_value_mapping** | `item_id`, `sale_tax_rate`, `jrsdctn_cntry_id`, `jrsdctn_tx` | Item ↔ Attribute Value (Tax) | LSTG_SALE_TAX                                   | P2 | Structure may change significantly after caty migration |
| **variation_aspect_value_mapping** | `variation_id`, `aspect_name` | Variation ↔ Aspect | VRTN_ASPCT_CLSSFCTN_SAP                         | P2 | |
| **item_business_program_mapping** | `item_id`, `biz_prgrm_id` | Item ↔ Business Program (current state) | DW_PES_ELGBLT_HIST                              | P2 | SCD2 table - requires pre-processing to create current state view (filter: vrtn_id = -999) |
| **variation_business_program_mapping** | `item_vrtn_id`, `biz_prgrm_id` | Variation ↔ Business Program (current state) | DW_PES_ELGBLT_HIST                              | P2 | SCD2 table - requires pre-processing to create current state view (filter: vrtn_id != -999) |


---

## LDM Schemas

=== "item"

    **Pre-processing:**
    
    - **ITEM360_SRCH_EMBEDDING** → `embeddings` field: Aggregation by `item_id` required to consolidate embedding vectors

    {{ read_table('docs/assets/ldm-schemas/item.tsv', sep='\t') }}

=== "variation"

    **Pre-processing:**
    
    - **ITEM360_SRCH_EMBEDDING_VRTN** → `embeddings` field: Aggregation by `item_id` + `item_vrtn_id` required to consolidate embedding vectors

    {{ read_table('docs/assets/ldm-schemas/variation.tsv', sep='\t') }}

=== "product"

    {{ read_table('docs/assets/ldm-schemas/product.tsv', sep='\t') }}

=== "transaction"

    {{ read_table('docs/assets/ldm-schemas/transaction.tsv', sep='\t') }}

=== "item_common_attribute_value_mapping"

    {{ read_table('docs/assets/ldm-schemas/item_common_attribute_value_mapping.tsv', sep='\t') }}

=== "item_listing_attribute_value_mapping"

    {{ read_table('docs/assets/ldm-schemas/item_listing_attribute_value_mapping.tsv', sep='\t') }}

=== "item_shipment_attribute_value_mapping"

    **Pre-processing:**
    
    - Merge with **dw_attr_shpmt_dtl_cold** table [to be confirmed]

    {{ read_table('docs/assets/ldm-schemas/item_shipment_attribute_value_mapping.tsv', sep='\t') }}

=== "item_picture_mapping"

    {{ read_table('docs/assets/ldm-schemas/item_picture_mapping.tsv', sep='\t') }}

=== "item_aspect_value_mapping"

    {{ read_table('docs/assets/ldm-schemas/item_aspect_value_mapping.tsv', sep='\t') }}

=== "variation_trait_mapping"

    {{ read_table('docs/assets/ldm-schemas/variation_trait_mapping.tsv', sep='\t') }}

=== "item_fitment_attribute_value_mapping"

    {{ read_table('docs/assets/ldm-schemas/item_fitment_attribute_value_mapping.tsv', sep='\t') }}

=== "item_tag_attribute_value_mapping"

    {{ read_table('docs/assets/ldm-schemas/item_tag_attribute_value_mapping.tsv', sep='\t') }}

=== "item_tax_attribute_value_mapping"

    {{ read_table('docs/assets/ldm-schemas/item_tax_attribute_value_mapping.tsv', sep='\t') }}

=== "variation_aspect_value_mapping"

    {{ read_table('docs/assets/ldm-schemas/variation_aspect_value_mapping.tsv', sep='\t') }}

=== "item_business_program_mapping"

    **Pre-processing:**
    
    - **DW_PES_ELGBLT_HIST** is a SCD2 (Slowly Changing Dimension Type 2) table that tracks historical changes in business program eligibility
    - **Required**: Create a current state view for item-level eligibility:
        - Filter: `evltn_end_ts = '2099-12-31 00:00:00'` (current active record)
        - Filter: `vrtn_id = -999` (item-level records, Single SKU)
        - This view represents the current eligibility state for each item and business program
    - The LDM exposes only the current state, not the full history

    {{ read_table('docs/assets/ldm-schemas/item_business_program_mapping.tsv', sep='\t') }}

=== "variation_business_program_mapping"

    **Pre-processing:**
    
    - **DW_PES_ELGBLT_HIST** is a SCD2 (Slowly Changing Dimension Type 2) table that tracks historical changes in business program eligibility
    - **Required**: Create a current state view for variation-level eligibility:
        - Filter: `evltn_end_ts = '2099-12-31 00:00:00'` (current active record)
        - Filter: `vrtn_id != -999` (variation-level records)
        - This view represents the current eligibility state for each variation and business program
    - The LDM exposes only the current state, not the full history

    {{ read_table('docs/assets/ldm-schemas/variation_business_program_mapping.tsv', sep='\t') }}
