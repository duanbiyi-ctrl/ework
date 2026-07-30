# ItemDetails LDM

[<- Back to LDM Catalog](../index.md)

## Overview

**LDM Name:** `ItemDetails LDM`

**Description:** Additional item details, including high-precision prices and supporting documents.

**NuDocument Docset:** `ItemDetails`

**Keyspace:** `ItemKeyspace`

**Source Class:** `com.ebay.app.cls.nudata.itemkeyspace.ItemDetailsDoc`

**Primary Key:** `itemDetailsID`

**Relationship Type:** Child document for item detail extensions

---

## Fields

| Field | Type | Description |
| --- | --- | --- |
| `itemDetailsID` | `String` | Identifier for this item-details child document, generated as `ITEM_DETAILS_<itemId>`. |
| `hasRlxdRls` | `Boolean` | Indicates whether the item uses relaxed rules. |
| `fixedPriceHP` | `Amount` | High-precision fixed-price amount. |
| `strtBidPriceHP` | `Amount` | High-precision starting-bid amount. |
| `docs` | `Documents` | Item document details, including vehicle-title, VIN, and odometer information when available. |
| `srcLstId` | `String` | Source listing identifier. |

## Write and Read Behavior

The item converter writes this child during create or replace when its
content is available. Item read paths can request it independently from the
root and price/quantity document.

## Relationships

This docset is a child of the `ItemKeyspace` item ancestor and uses the
collection name `ItemDetails`, even though its Java class is `ItemDetailsDoc`.
