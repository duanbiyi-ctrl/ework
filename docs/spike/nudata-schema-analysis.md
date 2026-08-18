# Why Core Listing Service Uses Four NuData Keyspaces and 21 Docsets

## Purpose and scope

Core Listing Service organizes active listing data into four NuData keyspaces
and 21 documented application docsets. This is a producer-side design: the
storage layout follows listing lifecycle, ownership, payload shape, and the
service's read/write operations. It is not intended to be a universal,
single-record representation of a listing.

This spike explains the split and then examines two contrasting `ItemKeyspace`
docsets in detail:

- `ItemQtyPrice`, a focused inventory and standard-price branch; and
- `ItemDescription`, a large seller-content payload with expanded and
  compressed representations.

This spike covers the four primary listing keyspaces:
`ItemKeyspace`, `ItemGroupKeyspace`, `ListingDraft`, and
`ListingRevisionKeyspace`. Archive keyspaces are out of scope.

## The four keyspaces

| Keyspace | Identity and lifecycle boundary | Why it is separate |
| --- | --- | --- |
| `ItemKeyspace` | One current single-SKU item or one current MSKU variation, keyed by item ID. | Live sellable state changes independently for each item/variation. |
| `ItemGroupKeyspace` | One current MSKU parent, keyed by group ID. | Holds group-owned variation structure and shared state; it must not be duplicated into every variation item. |
| `ListingDraft` | One pre-publication listing draft. | Draft state has a different lifecycle from live listing state and can exist before a published item or group exists. |
| `ListingRevisionKeyspace` | History for one item or group listing, keyed by listing ID. | Append-oriented revision records must not be mixed with the current-state documents. |

The first split is therefore about **business identity and lifecycle**, not
only physical storage: live item state, shared MSKU state, work-in-progress
draft state, and historical revisions are different things with different
access patterns.

## The 21 docsets

Within each keyspace, docsets split further by update behavior, payload shape,
specialization, and cardinality.

| Keyspace | Docsets | Count | Producer-side purpose |
| --- | --- | ---: | --- |
| `ItemKeyspace` | `__ROOT__`, `ItemQtyPrice`, `ItemDescription`, `ItemCompatibility`, `BusinessPolicies`, `ItemDetails`, `ItemLock`, `UuidMap` | 8 | Current item state plus separately addressable inventory, description, fitment, policies, details, locking, and UUID lookup data. |
| `ItemGroupKeyspace` | `__ROOT__`, `GroupDescription`, `GroupBusinessPolicies` | 3 | Current group state plus shared large description and policy data. |
| `ListingDraft` | `__ROOT__`, `ItemDraft`, `ItemDraftCompatibility`, `ItemGroupDraft`, `ItemGroupDraftCompatibility`, `ItemGroupDraftDesc` | 6 | Draft session state, item or group work-in-progress, and draft-specific large or optional payloads. |
| `ListingRevisionKeyspace` | `__ROOT__`, `ListingRevision`, `ListingRevisionDetail`, `VariationRevisionDetail` | 4 | History container, revision summary, item-property changes, and variation-property changes. |
| **Total** |  | **21** |  |

### Why split a keyspace into docsets?

| Split driver | Examples | What the split enables |
| --- | --- | --- |
| Hot, narrowly mutable state | `ItemQtyPrice`, `ItemLock` | Targeted inventory and price updates without rebuilding broad item state. |
| Large or alternative representation | `ItemDescription`, `GroupDescription`, compatibility docsets | A reader can avoid large payloads; a producer can choose expanded or compressed content. |
| Optional or specialized data | `ItemCompatibility`, `BusinessPolicies`, `ItemDetails` | Common reads do not need to carry fitment, detailed policies, vehicle documents, or high-precision prices. |
| Different ownership or cardinality | `ItemGroupKeyspace`, `ItemGroupDraft`, `ItemDraft` | Shared MSKU data is stored once at group scope; variations keep item-specific state. |
| Current state versus work in progress versus history | Item, draft, and revision keyspaces | Consumers and producer operations can address the correct lifecycle state explicitly. |
| Lookup and discovery | `UuidMap` | Common UUID lookups do not require scanning full current-state documents. |

These are evidence-backed access and payload boundaries. They do **not** by
themselves prove a storage-engine latency target, a throughput target, or a
cross-document transaction guarantee.

## Document family and key hierarchy

An item has a root key and child docset keys:

```text
__ROOT__ / <item-id>
├── ItemQtyPrice / QTYPRICE_<item-id>
│   └── ItemLock / <lock-id>
├── ItemDescription / DESC_<item-id>
├── ItemCompatibility / COMPAT_<item-id>
├── BusinessPolicies / BIZPOL_<item-id>
└── ItemDetails / ITEMDET_<item-id>
```

Raw samples expose this hierarchy in `__key` and include NuData-managed
`__meta` creation, modification, and revision metadata. These are source
storage details; they are not the complete business key or a business measure.

## Deep dive: `ItemQtyPrice`

### What it contains

`ItemQtyPrice` is the current item branch for standard inventory and price
state:

| Field group | Fields | Role |
| --- | --- | --- |
| Document identity | `ItemQtyPriceID` | Identifies the child document; observed IDs use `QTYPRICE_<item-id>`. |
| Inventory counters | `availQty`, `qtySold`, `minRmntSet`, `qtySldByPickpStre` | Available/sold quantity and related inventory state. |
| Standard price envelope | `price.fixedPrice`, `price.strtBidPrice`, `price.auctnRsrvPrc`, `price.mrktngPrc`, `price.orgnRetailPrice`, `price.COGs`, `price.prcGuarantee` | Fixed-price, auction, marketing, reference, cost, and price-guarantee concepts. |

Every monetary member is an `Amount` with its own `currency` and `value`.
The price envelope supports different listing formats: a fixed-price listing
does not necessarily have an auction reserve or starting bid, and an auction
does not require every fixed-price concept.

### Why it is split from `__ROOT__`

The Core Listing Service price-and-quantity operation updates
`ItemQtyPrice` directly and updates root revision/modification fields
separately. Lock flows also adjust quantity counters on this branch. This
matches the source wiki's hot-path description of `ItemQtyPrice`.

Reads are similarly selective:

| Read intent | Documents used | Design implication |
| --- | --- | --- |
| Status | Root only | A status reader need not fetch price or quantity. |
| Listing status | Root plus `ItemQtyPrice.availQty` | A lightweight status read adds only the needed inventory field. |
| Inventory or summary | Root, `ItemQtyPrice`, `ItemDetails`, and lock summary | The reader adds standard price/quantity, high-precision prices, and reservation context only when required. |
| Full item | Root and the relevant child docsets | Full reads assemble the family only for callers that need it. |

This is the direct reason to separate `ItemQtyPrice`: standard sellability
state has a more frequent and more focused read/write path than broad listing
identity, category, media, lifecycle, and policy-reference state in root.

### Why the price shape is nested

`price` is a logical aggregate, not a presentation choice:

```text
price.<price-kind>.currency
price.<price-kind>.value
```

It groups related but format-dependent price variants beneath one stable
extension point and keeps each value coupled with its currency. A flat model
would require a growing set of unrelated top-level names such as
`fixedPriceValue`, `fixedPriceCurrency`, `startingBidValue`, and
`startingBidCurrency`. The nested shape also allows a raw document to show
non-applicable price variants as `null`.

`ItemQtyPrice` is intentionally not the entire pricing model. High-precision
fixed and starting-bid prices are in `ItemDetails`, while root owns listing
format and lifecycle. A consumer that needs a business price must select the
appropriate source fields and rules rather than assuming one raw field is
universally authoritative.

## Deep dive: `ItemDescription`

### What it contains

`ItemDescription` is the item child document for seller-provided description
content:

| Field | Role |
| --- | --- |
| `ItemDescID` | Child document ID; observed IDs use `DESC_<item-id>`. |
| `desc` | Expanded seller-provided description text. |
| `compDesc` | Compressed representation of the same description payload. |
| `descRevsnDt` | Description-specific revision timestamp. |

`desc` and `compDesc` are alternative representations. The producer converter
chooses the compressed representation when compression produces a value;
otherwise it writes expanded text. Samples demonstrate that the expanded
payload can contain long, seller-authored markup. The document intentionally
does not reproduce that content here.

### Why it is split from `__ROOT__`

Description content has a different payload and access profile from the broad
item root:

- It can be substantially larger and less structurally regular than item
  identity, category, or lifecycle fields.
- It has its own revision timestamp and its own compressed representation.
- The service supports a description-only read that requests this document
  without the root.
- A full-without-description read requests only `descRevsnDt`, while a full
  item read requests the complete description document.

This lets common item, status, inventory, and summary reads avoid transferring
the full seller description. It also lets the producer update or read
description state independently of unrelated item state.

## What this means for downstream consumers

The 21-docset layout preserves producer semantics but is not a ready-made
warehouse table. A downstream consumer must otherwise reconstruct document
relationships, determine the correct lifecycle state, interpret nested and
nullable price variants, decide whether a description is compressed, and
avoid confusing system metadata with business fields.

The appropriate consumer layer is a governed domain model that assembles the
necessary source state, assigns business keys and definitions, normalizes
price and quantity semantics, and preserves lineage to these docsets.

## Evidence and limits

- [Listing NuData Design](../wiki/Listing_NuData_Design.md) establishes the
  live, draft, revision, and archive keyspace categories.
- [Core Listing Service NuData V2 Database Schema](../wiki/Core_Listing_Service-NuData_V2_Database_Schema.md)
  documents the primary keyspaces, collection roles, and frequency tiers.
- [ItemQtyPrice sample](../../data/sample-data/item-raw-ldm-samples/ItemKeyspace/ItemQtyPrice.json)
  and [ItemDescription sample](../../data/sample-data/item-raw-ldm-samples/ItemKeyspace/ItemDescription.json)
  establish observed key and payload shapes.
- [Item quantity and price LDM](../entities/itemkeyspace-item-qty-price.md)
  and [item description LDM](../entities/itemkeyspace-item-description.md)
  provide the current field dictionaries.

The original schema-design ADR is not present in these materials. The
explanations above are therefore based on current key hierarchy, documented
frequency tiers, raw document shape, and observed implementation read/write
paths rather than an asserted historical design intent.
