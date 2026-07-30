# ItemLock LDM

[<- Back to LDM Catalog](../index.md)

## Overview

**LDM Name:** `ItemLock LDM`

**Description:** Inventory reservation and lock state for an item.

**NuDocument Docset:** `ItemLock`

**Keyspace:** `ItemKeyspace`

**Source Class:** `com.ebay.app.cls.nudata.itemkeyspace.ItemLock`

**Primary Key:** `pk`

**Relationship Type:** Auxiliary child document for inventory locks

---

## Fields

| Field | Type | Description |
| --- | --- | --- |
| `pk` | `String` | Lock identifier. |
| `st` | `ItemLockStatus` | Lock status: `A` active, `C` committed, or `X` cancelled. |
| `qty` | `long` | Locked or reserved quantity. |
| `expDt` | `long` | Lock expiration timestamp. |
| `cmtDt` | `Long` | Timestamp when the lock was committed. |
| `cnclDt` | `Long` | Timestamp when the lock was cancelled. |
| `extDt` | `Long` | Timestamp when the lock was extended. |
| `extCnt` | `Long` | Number of times the lock was extended. |
| `crtDt` | `long` | Lock creation timestamp. |
| `modDt` | `Long` | Last-modified timestamp, initialized from the creation timestamp. |
| `uuid` | `String` | Reservation UUID. |

The summary lock uses the same schema with the reserved lock ID
`LOCK_$$$SUMMARY$$$`; its quantity is the aggregate reserved quantity.

## Write and Read Behavior

Lock create, reactivate, commit, cancel, and extend operations write or update
this docset. These operations can also update `ItemQtyPrice` to reflect the
inventory reservation.

## Relationships

This docset is an auxiliary child under the `ItemKeyspace` item ancestor. It
uses the same schema for individual locks and the aggregate summary lock.
