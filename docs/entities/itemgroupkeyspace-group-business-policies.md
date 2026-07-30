# ItemGroupBusinessPolicies LDM

[<- Back to LDM Catalog](../index.md)

## Overview

**LDM Name:** `ItemGroupBusinessPolicies LDM`

**Description:** Return, payment, and shipping policy terms shared by an item group.

**NuDocument Docset:** `GroupBusinessPolicies`

**Keyspace:** `ItemGroupKeyspace`

**Source Class:** `com.ebay.app.cls.nudata.itemgroupkeyspace.GroupBusinessPolicies`

**Primary Key:** `plcsId`

**Relationship Type:** Child document for group-level policy terms

---

## Fields

`GroupBusinessPolicies` extends `ItemKeyspace/BusinessPolicies` and declares
no additional fields. It uses its own `GroupBusinessPolicies` collection name.

| Field | Type | Description |
| --- | --- | --- |
| `plcsId` | `String` | Identifier for the group policy set. |
| `retTrms` | `ReturnTerms` | Embedded return-policy terms, including acceptance, refund, timing, and return-shipping responsibility. |
| `pmtTrms` | `PaymentTerms` | Embedded payment terms, including payment methods, deposit requirements, and payment instructions. |
| `shipTrms` | `ShippingTerms` | Embedded shipping terms, including destinations, excluded locations, handling time, and service options. |

## Write and Read Behavior

Item-group create and upsert operations build this document from the group
business policies and write it with the group root and description child.

## Relationships

This is the group-level counterpart to `ItemKeyspace/BusinessPolicies`. The
field shape is inherited, but the docset is separate because it belongs to the
item-group keyspace and group ancestor.
