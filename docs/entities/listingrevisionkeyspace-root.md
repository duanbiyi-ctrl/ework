# ListingRevisionRoot LDM

[<- Back to LDM Catalog](../index.md)

## Overview

**LDM Name:** `ListingRevisionRoot LDM`

**Description:** Conditional revision-history root used for listing retention and expiry maintenance.

**NuDocument Docset:** `__ROOT__`

**Keyspace:** `ListingRevisionKeyspace`

**Source Class:** `com.ebay.app.cls.nudata.listingrevisionhistorykeyspace.__ROOT__`

**Key / Ancestor:** Revision-history listing ancestor; `lstgId` identifies the listing

**Relationship Type:** Root document for revision-history retention state

---

## Fields

| Field | Type | Description |
| --- | --- | --- |
| `lstgId` | `String` | Identifier of the listing whose revision history is stored. |
| `expiredDate` | `Date` | Date when revision-history retention expires. |

## Write and Read Behavior

The normal revision insert creates revision documents rather than this root.
TTL maintenance upserts the root to manage revision-history retention state.

## Relationships

This root has the revision-history listing ancestor. The associated
`ListingRevision`, `ListingRevisionDetail`, and `VariationRevisionDetail`
documents represent historical changes rather than current item state.
