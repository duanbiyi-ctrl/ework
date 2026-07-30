# ListingRevisionDetail LDM

[<- Back to LDM Catalog](../index.md)

## Overview

**LDM Name:** `ListingRevisionDetail LDM`

**Description:** Historical old and new values for a changed listing property.

**NuDocument Docset:** `ListingRevisionDetail`

**Keyspace:** `ListingRevisionKeyspace`

**Source Class:** `com.ebay.app.cls.nudata.listingrevisionhistorykeyspace.ListingRevisionDetail`

**Key / Ancestor:** Revision-history listing and revision ancestor; the schema class has no persisted key field

**Relationship Type:** Historical property-change detail document

---

## Fields

| Field | Type | Description |
| --- | --- | --- |
| `rvsdPrptyGrp` | `RevisedPropertyGroupEnum` | Group containing the changed listing property. |
| `rvsdPrpty` | `RevisedPropertyEnum` | Listing property that changed. |
| `chgTp` | `ChangeTypeEnum` | Kind of change recorded. |
| `newVal` | `String` | Value after the change. |
| `oldVal` | `String` | Value before the change. |
| `lbl` | `String` | Display label for the changed property. |

## Write and Read Behavior

Revision insertion adds zero or more detail documents for changed listing
properties. The document is read as historical revision detail, not as a
replacement for current item data.

## Relationships

This document is associated with a `ListingRevision` under the
revision-history listing ancestor. It describes a non-variation property
change.
