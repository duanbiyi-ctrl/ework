# ItemGroupDescription LDM

[<- Back to LDM Catalog](../index.md)

## Overview

**LDM Name:** `ItemGroupDescription LDM`

**Description:** Expanded or compressed shared description for an item group.

**NuDocument Docset:** `GroupDescription`

**Keyspace:** `ItemGroupKeyspace`

**Source Class:** `com.ebay.app.cls.nudata.itemgroupkeyspace.GroupDescription`

**Primary Key:** `groupDescId`

**Relationship Type:** Child document for the shared item-group description

---

## Fields

| Field | Type | Description |
| --- | --- | --- |
| `groupDesc` | `String` | Expanded shared description for the item group. |
| `compDesc` | `byte[]` | Compressed representation of the shared group description. |
| `groupDescId` | `String` | Identifier for this group-description document. |
| `grpDescRevsnDt` | `Long` | Timestamp of the group-description revision. |

## Write and Read Behavior

The item-group converter writes this child with the group root. The compressed
and expanded fields are alternative representations of the group description,
allowing description updates independently of shared group identity.

## Relationships

This is a child of the `ItemGroupKeyspace` group ancestor. It stores the
shared description for an item group rather than repeating that description in
every individual item document.
