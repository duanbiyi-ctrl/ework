# ItemPriceAndQuantity LDM

[<- Back to LDM Catalog](../index.md)

## Overview

**LDM Name:** `ItemPriceAndQuantity LDM`

**Description:** Current item inventory, sold quantity, price, and minimum-remnant state.

**NuDocument Docset:** `ItemQtyPrice`

**Keyspace:** `ItemKeyspace`

**Source Class:** `com.ebay.app.cls.nudata.itemkeyspace.ItemQtyPrice`

**Primary Key:** `ItemQtyPriceID`

**Relationship Type:** Child document for item price and quantity state

---

## Fields

| Field | Type | Description |
| --- | --- | --- |
| `availQty` | `Integer` | Available item quantity. |
| `ItemQtyPriceID` | `String` | Identifier for this price-and-quantity child document, generated as `QTY_PRICE_<itemId>`. |
| `crLstgDtVrs` | `String` | Core listing data version. |
| `lifecycle` | `Lifecycle` | Scheduled and end dates for the listing lifecycle. |
| `price` | `Price` | Pricing details, including reserve, fixed, marketing, starting-bid, original retail, and cost-of-goods prices, plus price-guarantee enrollment. |
| `qtySold` | `Integer` | Item quantity sold. |
| `minRmntSet` | `Integer` | Minimum remnant-set quantity. |
| `qtySldByPickpStre` | `Integer` | Quantity sold through the legacy pickup-store flow. |

## Write and Read Behavior

Create and replace convert item price and inventory values into this child
document. Price, quantity, and lock lifecycle operations can update it without
replacing the item root.

## Relationships

This docset is a child of the `ItemKeyspace` item ancestor. Item locks affect
reserved inventory and can therefore mutate this document as a side effect.
