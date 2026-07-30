# UserListingDraftMap LDM

[<- Back to LDM Catalog](../index.md)

## Overview

**LDM Name:** `UserListingDraftMap LDM`

**Description:** User-scoped index of active listing drafts and their summary metadata.

**NuDocument Docset:** `UserItemDraftMap`

**Keyspace:** `UserListingDraft`

**Source Class:** `com.ebay.app.cls.nudata.userlistingdraftkeyspace.UserListingDraftMap`

**Key / Ancestor:** User and listing-draft key shape; the schema class has no persisted key field

**Relationship Type:** Active-draft index document for a user

---

## Fields

| Field | Type | Description |
| --- | --- | --- |
| `draftId` | `String` | Listing draft identifier. |
| `mktPlLstdOn` | `String` | Marketplace on which the draft is listed. |
| `lstgAppId` | `String` | Listing application identifier. |
| `primCatId` | `String` | Primary category identifier. |
| `crtMd` | `DraftCreationModeEnum` | Draft creation-mode classification. |
| `eBGenTtl` | `String` | eBay-generated title. |
| `ttl` | `String` | Draft title. |
| `imgUrl` | `String` | Image URL. |
| `stockImgUrl` | `String` | Stock-image URL. |
| `crtDt` | `Long` | Creation date/time value. |
| `userId` | `String` | User identifier. |
| `lastModifiedDate` | `Long` | Last-modified date/time value. |

## Write and Read Behavior

The service maintains this index for active user listing drafts. User draft
reads use it to find draft summaries; draft creation, update, and deletion
change the index according to the current active-draft state.

## Relationships

This is an index in the `UserListingDraft` keyspace, separate from the full
draft document family in `ListingDraft`. It associates a user with a listing
draft ID and summary data.
