# ListingRevision LDM

[<- Back to LDM Catalog](../index.md)

## Overview

**LDM Name:** `ListingRevision LDM`

**Description:** Historical summary of a listing revision and its changed property groups.

**NuDocument Docset:** `ListingRevision`

**Keyspace:** `ListingRevisionKeyspace`

**Source Class:** `com.ebay.app.cls.nudata.listingrevisionhistorykeyspace.ListingRevision`

**Key / Ancestor:** Revision-history listing ancestor; the schema class has no persisted key field

**Relationship Type:** Historical listing-revision document

---

## Fields

| Field | Type | Description |
| --- | --- | --- |
| `rvsdPrptyGrps` | `List<RevisedPropertyGroupEnum>` | Property groups changed by this revision. |
| `vrsnId` | `Long` | Listing revision version identifier. |
| `appId` | `Long` | Identifier of the application that produced the revision. |
| `sigRevCnt` | `Integer` | Count of significant revisions. |
| `vrsnCrtd` | `Boolean` | Indicates whether the revision created a version. |
| `rvsdDate` | `Long` | Timestamp when the revision was recorded. |
| `updCrLstgVrs` | `String` | Core-listing version after the update. |

## Write and Read Behavior

Revision insertion writes one `ListingRevision` document and can add detail
documents in the same revision-history operation. Backfill uses the same
logical document family.

## Relationships

This document records a listing revision under the revision-history ancestor.
`ListingRevisionDetail` and `VariationRevisionDetail` record the property
changes associated with a revision.
