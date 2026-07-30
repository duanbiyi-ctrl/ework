# ListingDraftGroup LDM

[<- Back to LDM Catalog](../index.md)

## Overview

**LDM Name:** `ListingDraftGroup LDM`

**Description:** Draft group content for an MSKU listing, including shared traits and policies.

**NuDocument Docset:** `ItemGroupDraft`

**Keyspace:** `ListingDraft`

**Source Class:** `com.ebay.app.cls.nudata.listingdraftkeyspace.ItemGroupDraft`

**Primary Key:** `PK`

**Relationship Type:** Child document for MSKU draft group data

---

## Fields

| Field | Type | Description |
| --- | --- | --- |
| `PK` | `String` | Draft group document identifier. |
| `grpTtl` | `String` | Group title. |
| `imgsVryBy` | `ImagesVaryBy` | Image-variation configuration, including the variation trait and its image associations. |
| `img` | `List<ImageMap>` | Image mappings for the group. |
| `itmsVryBy` | `List<NameValuesPair>` | Item variation trait name/value entries. |
| `slrGrpKey` | `String` | Seller group key. |
| `bizPol` | `BusinessPolicies` | Business-policy set and its embedded policy terms. |
| `grpId` | `String` | Group identifier. |

## Write and Read Behavior

Draft updates create or upsert this child when the draft represents an MSKU
group. An SSKU draft does not require this group child.

## Relationships

This docset shares a `ListingDraft` ancestor with the draft root, group
description, group compatibility, and one item draft per variation.
