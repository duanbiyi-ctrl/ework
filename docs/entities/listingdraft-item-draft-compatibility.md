# ListingDraftItemCompatibility LDM

[<- Back to LDM Catalog](../index.md)

## Overview

**LDM Name:** `ListingDraftItemCompatibility LDM`

**Description:** Optional fitment and compatibility payload for an item draft.

**NuDocument Docset:** `ItemDraftCompatibility`

**Keyspace:** `ListingDraft`

**Source Class:** `com.ebay.app.cls.nudata.listingdraftkeyspace.ItemDraftCompatibility`

**Primary Key:** `DraftCompID`

**Relationship Type:** Optional child document for item-draft compatibility

---

## Fields

`ItemDraftCompatibility` extends `BaseDraftCompatibility` and declares no
additional fields.

| Field | Type | Description |
| --- | --- | --- |
| `DraftCompID` | `String` | Draft compatibility document identifier. |
| `compat` | `List<com.ebay.cls.v2.entities.ItemCompatibility>` | Compatibility entries for the item draft. |
| `cmpCompat` | `byte[]` | Compressed compatibility representation. |

## Write and Read Behavior

Draft updates upsert or delete this optional child according to the current
draft compatibility payload. The expanded and compressed fields are alternative
representations.

## Relationships

This child belongs to an item draft under the `ListingDraft` ancestor. It has
the same inherited field shape as `ItemGroupDraftCompatibility`, but a
different collection name and role.
