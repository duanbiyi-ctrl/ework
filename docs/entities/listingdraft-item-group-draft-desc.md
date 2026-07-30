# ListingDraftGroupDescription LDM

[<- Back to LDM Catalog](../index.md)

## Overview

**LDM Name:** `ListingDraftGroupDescription LDM`

**Description:** Expanded or compressed shared group description for an MSKU listing draft.

**NuDocument Docset:** `ItemGroupDraftDesc`

**Keyspace:** `ListingDraft`

**Source Class:** `com.ebay.app.cls.nudata.listingdraftkeyspace.ItemGroupDraftDesc`

**Primary Key:** `PK`

**Relationship Type:** Child document for MSKU draft group description

---

## Fields

| Field | Type | Description |
| --- | --- | --- |
| `groupDesc` | `String` | Expanded group description. |
| `cmpDesc` | `byte[]` | Compressed group description. |
| `PK` | `String` | Group-description document identifier. |
| `grpDescRevsnDt` | `Long` | Group-description revision date/time value. |

## Write and Read Behavior

MSKU draft updates write this group-description child with the group and
current item drafts. The expanded and compressed description fields are
alternative representations.

## Relationships

This docset is a child of the `ListingDraft` ancestor and is associated with
`ItemGroupDraft`; it is not written for an SSKU draft.
