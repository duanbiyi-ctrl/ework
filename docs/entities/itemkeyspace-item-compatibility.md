# ItemCompatibility LDM

[<- Back to LDM Catalog](../index.md)

## Overview

**LDM Name:** `ItemCompatibility LDM`

**Description:** Fitment and compatibility payload for an item.

**NuDocument Docset:** `ItemCompatibility`

**Keyspace:** `ItemKeyspace`

**Source Class:** `com.ebay.app.cls.nudata.itemkeyspace.ItemCompatibility`

**Primary Key:** `ItemCompID`

**Relationship Type:** Child document for an item's compatibility payload

---

## Fields

| Field | Type | Description |
| --- | --- | --- |
| `ItemCompID` | `String` | Identifier for this compatibility child document, generated as `COMPAT_<itemId>`. |
| `compat` | `List<com.ebay.cls.v2.entities.ItemCompatibility>` | Expanded list of the item's compatibility entries. |
| `cmpCompat` | `byte[]` | Compressed representation of the item's compatibility entries. |
| `ftExempt` | `Integer` | Item fitment-threshold exemption value. |

## Write and Read Behavior

The item converter creates this child document during create or replace when
compatibility data is applicable. Item readers request it with the item root;
partial compatibility mutations can target this document without replacing the
root.

## Relationships

This docset is a child of the `ItemKeyspace` item ancestor and is associated
with the `__ROOT__` document through the item ID used to generate its key.
