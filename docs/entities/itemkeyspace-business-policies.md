# ItemBusinessPolicies LDM

[<- Back to LDM Catalog](../index.md)

## Overview

**LDM Name:** `ItemBusinessPolicies LDM`

**Description:** Return, payment, and shipping policy terms for an item.

**NuDocument Docset:** `BusinessPolicies`

**Keyspace:** `ItemKeyspace`

**Source Class:** `com.ebay.app.cls.nudata.itemkeyspace.BusinessPolicies`

**Primary Key:** `plcsId`

**Relationship Type:** Child document for item policy terms

---

## Fields

| Field | Type | Description |
| --- | --- | --- |
| `plcsId` | `String` | Identifier for this policy-set child document, generated as `BIZ_POL_<itemId>`. |
| `retTrms` | `ReturnTerms` | Return-policy terms, including acceptance, refund, duration, instructions, shipping payer, and domestic or international terms. |
| `pmtTrms` | `PaymentTerms` | Payment-policy terms, including payment timing, deposit requirements and amount, payment methods, instructions, and PayPal email. |
| `shipTrms` | `ShippingTerms` | Shipping-policy terms, including destinations and exclusions, handling time, buyer responsibility, shipping options, services, and costs. |

## Write and Read Behavior

The item converter creates this child document from the item's business policy
terms as part of the item document family. Readers request it with the root
when policy data is needed.

## Relationships

This is the item-level policy docset. `GroupBusinessPolicies` is a distinct
group-level docset that inherits this same top-level field shape.
