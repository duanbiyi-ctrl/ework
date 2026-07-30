# ItemUUIDMapping LDM

[<- Back to LDM Catalog](../index.md)

## Overview

**LDM Name:** `ItemUUIDMapping LDM`

**Description:** Seller and UUID lookup mapping to an item and listing application.

**NuDocument Docset:** `UuidMap`

**Keyspace:** `ItemKeyspace`

**Source Class:** `com.ebay.app.cls.nudata.itemkeyspace.UuidMap`

**Primary Key:** Seller ID and UUID

**Relationship Type:** Auxiliary item lookup document

---

## Fields

| Field | Type | Description |
| --- | --- | --- |
| `listingId` | `String` | Listing identifier resolved from the seller-and-UUID key. |
| `listingAppId` | `String` | Application identifier for the resolved listing. |

The seller ID and UUID are part of the key shape, not fields in this document.

## Write and Read Behavior

UUID-specific item operations use this auxiliary document to resolve listing
identity. It is not one of the six docsets written by the normal item
create-or-replace converter path.

## Relationships

This docset belongs to the item keyspace but is a lookup structure rather than
a child payload built from the standard `Item` converter.
