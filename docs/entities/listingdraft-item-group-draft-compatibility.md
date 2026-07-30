# ListingDraftGroupCompatibility LDM

[<- Back to LDM Catalog](../index.md)

## Overview

**LDM Name:** `ListingDraftGroupCompatibility LDM`

**Description:** Optional group-level compatibility payload for an MSKU listing draft.

**NuDocument Docset:** `ItemGroupDraftCompatibility`

**Keyspace:** `ListingDraft`

**Source Class:** `com.ebay.app.cls.nudata.listingdraftkeyspace.ItemGroupDraftCompatibility`

**Primary Key:** `DraftCompID`

**Relationship Type:** Optional child document for MSKU draft compatibility

---

## Fields

`ItemGroupDraftCompatibility` extends `BaseDraftCompatibility` and declares no
additional fields.

| Field | Type | Description |
| --- | --- | --- |
| `DraftCompID` | `String` | Draft compatibility document identifier. |
| `compat` | `List<com.ebay.cls.v2.entities.ItemCompatibility>` | Compatibility entries for the item group draft. |
| `cmpCompat` | `byte[]` | Compressed compatibility representation. |

## Write and Read Behavior

MSKU draft updates upsert or delete this optional child according to the group
compatibility payload. The expanded and compressed fields are alternative
representations.

## Relationships

This child belongs to the group portion of a `ListingDraft`. It has the same
inherited schema as `ItemDraftCompatibility`, but uses the
`ItemGroupDraftCompatibility` collection name.
