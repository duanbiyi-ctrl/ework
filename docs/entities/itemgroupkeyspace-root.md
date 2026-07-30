# ItemGroupRoot LDM

[<- Back to LDM Catalog](../index.md)

## Overview

**LDM Name:** `ItemGroupRoot LDM`

**Description:** Current shared identity, membership, and variation context for an item group.

**NuDocument Docset:** `__ROOT__`

**Keyspace:** `ItemGroupKeyspace`

**Source Class:** `com.ebay.app.cls.nudata.itemgroupkeyspace.__ROOT__`

**Primary Key:** `PK`

**Relationship Type:** Root document for current-state item-group data

---

## Fields

| Field | Type | Description |
| --- | --- | --- |
| `PK` | `String` | Identifier for the item group. |
| `createdDt` | `Long` | Timestamp when the group was created. |
| `lastmodifiedDt` | `Long` | Timestamp of the latest group update. |
| `admEndDt` | `Long` | Timestamp when the group was administratively ended. |
| `owner` | `String` | Owner of the item group. |
| `groupTitle` | `String` | Shared title for the group. |
| `groupType` | `String` | Classification of the item group. |
| `sellerGroupKey` | `String` | Seller-provided group key. |
| `grpVrs` | `String` | Version of the group. |
| `grpDrftId` | `String` | Draft identifier associated with the group. |
| `images` | `List<ImageMap>` | Shared group images, including image URLs and display order. |
| `itemIds` | `List<String>` | Identifiers of the individual items in the group. |
| `itmsVryBy` | `List<NameValuesPair>` | Traits by which the group's items vary. |
| `imgVryBy` | `ImagesVaryBy` | Trait-driven image variation configuration. |
| `compat` | `List<ItemCompatibility>` | Expanded compatibility data for the group. |
| `cmpCompat` | `byte[]` | Compressed compatibility data for the group. |
| `mFulfillmentSprt` | `Boolean` | Indicates whether managed fulfillment is supported. |
| `globalIdentifiers` | `List<NameValuesPair>` | Global product identifiers for the group. |
| `httpsCmplt` | `Integer` | HTTPS compliance indicator. |

## Write and Read Behavior

Item-group create and upsert operations build this root with
`ItemGroupDocumentConverter.getRoot(...)` and write it with the group
description and group business-policy children. Partial group updates can
change selected fields without reconstructing all group data.

## Relationships

This root represents group identity and shared variation context. It references
individual item IDs but is in a separate keyspace from their
`ItemKeyspace` document families.
