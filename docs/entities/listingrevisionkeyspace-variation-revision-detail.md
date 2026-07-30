# ListingVariationRevisionDetail LDM

[<- Back to LDM Catalog](../index.md)

## Overview

**LDM Name:** `ListingVariationRevisionDetail LDM`

**Description:** Historical old and new values for a changed variation property.

**NuDocument Docset:** `VariationRevisionDetail`

**Keyspace:** `ListingRevisionKeyspace`

**Source Class:** `com.ebay.app.cls.nudata.listingrevisionhistorykeyspace.VariationRevisionDetail`

**Key / Ancestor:** Revision-history listing and revision ancestor; the schema class has no persisted key field

**Relationship Type:** Historical variation-property-change detail document

---

## Fields

| Field | Type | Description |
| --- | --- | --- |
| `varId` | `String` | Identifier of the changed variation. |
| `rvsdPrptyGrp` | `RevisedPropertyGroupEnum` | Group containing the changed variation property. |
| `rvsdVarPrpty` | `RevisedVariationPropertyEnum` | Variation-specific property that changed. |
| `chgTp` | `ChangeTypeEnum` | Kind of change recorded. |
| `newVal` | `String` | Value after the change. |
| `oldVal` | `String` | Value before the change. |
| `varTraitVals` | `String` | Serialized variation trait values associated with the change. |

## Write and Read Behavior

Revision insertion adds zero or more variation-detail documents for changed
variation properties. The document is historical and does not replace the
current item or item-group document families.

## Relationships

This document is associated with a `ListingRevision` under the
revision-history listing ancestor. It describes a variation-specific property
change.
