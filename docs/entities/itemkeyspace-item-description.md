# ItemDescription LDM

[<- Back to LDM Catalog](../index.md)

## Overview

**LDM Name:** `ItemDescription LDM`

**Description:** Expanded or compressed seller-provided item description.

**NuDocument Docset:** `ItemDescription`

**Keyspace:** `ItemKeyspace`

**Source Class:** `com.ebay.app.cls.nudata.itemkeyspace.ItemDescription`

**Primary Key:** `ItemDescID`

**Relationship Type:** Child document for an item's description payload

---

## Fields

| Field | Type | Description |
| --- | --- | --- |
| `desc` | `String` | Expanded item description text. |
| `ItemDescID` | `String` | Identifier for this description child document, generated as `DESC_<itemId>`. |
| `compDesc` | `byte[]` | Compressed representation of the item description. |
| `descRevsnDt` | `Long` | Item description revision timestamp. |

## Write and Read Behavior

The item converter chooses the expanded or compressed description
representation and writes this child with the item document family. Item
readers request it separately from the root so description data can be read or
updated independently.

## Relationships

This docset is a child of the `ItemKeyspace` item ancestor. `desc` and
`compDesc` are alternative forms of the same description payload.
