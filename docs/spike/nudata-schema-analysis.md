# Why Selling's NuData Schema Is a Producer Model

## Executive conclusion

Core Listing Service stores listing data in NuData to operate the Selling
workflow: create and revise listings, update price and quantity, manage
variation groups, find active drafts, reserve inventory, and retain revision
history. It is a **producer-side operational model**, not a consumer-ready
record for analytics, reporting, or general self-service use.

The five live logical keyspaces and 22 declared docsets preserve the
producer's identity, lifecycle, ownership, payload, and mutation boundaries.
As a result, a downstream consumer does not receive one complete, flat
`listing` record. To create an easy-to-read data product, downstream
processing must assemble the necessary documents, choose the intended
lifecycle state, decode alternative representations, normalize nested or
repeated values, and publish governed consumer entities.

This is not a criticism of the NuData design. The design is appropriate for
the service that owns and changes listing state. The conclusion is that its
storage shape should not be exposed as the default consumption shape.

## Scope and terminology

This analysis covers the five active logical keyspace families:

1. `ItemKeyspace`
2. `ItemGroupKeyspace`
3. `ListingDraft`
4. `UserListingDraft`
5. `ListingRevisionKeyspace`

A **keyspace** is an operational storage family. A **docset** is a named
stored-document type within that family. Neither is automatically a
consumer-facing entity or relational table.

`ItemKeyspaceArchive` and `ItemGroupKeyspaceArchive` are physical archive
write targets that reuse live item or group root schemas. They are not
additional live logical families and are out of scope here.

## Why Selling uses five keyspaces

The split is primarily about **business identity and lifecycle**, not about
creating five alternative copies of the same listing.

| Keyspace | Identity and lifecycle | Producer-side purpose | Consumer implication |
| --- | --- | --- | --- |
| `ItemKeyspace` | One current sellable item: an SSKU listing or one MSKU variation, keyed by item ID. | Holds state that is changed and read at an individual sellable-item level. | It is not always the complete customer-visible listing; an MSKU item needs group context. |
| `ItemGroupKeyspace` | One current MSKU group, keyed by group ID. | Holds state shared by a variation set and the links to its member items. | Consumers must assemble group and variation records deliberately. |
| `ListingDraft` | One working draft, keyed by draft ID, before or during publication. | Separates editable, incomplete work from published state. | Draft data is not proof that a live item or group exists. |
| `UserListingDraft` | A user-and-draft active-draft index. | Finds a user's active draft summaries without reading complete draft content. | It is a discovery index, not a duplicate of the draft payload. |
| `ListingRevisionKeyspace` | History for an item or group listing, keyed by listing ID. | Retains revision summaries and changed-property details separately from latest state. | It must not be mixed with current-state fields when producing a current listing view. |

The lifecycle is therefore:

```text
UserListingDraft (find active draft)
          |
          v
ListingDraft (working state) ---- publish ----> ItemKeyspace (current item state)
                                                     ^
                                                     |
                                   ItemGroupKeyspace (shared MSKU state)

ItemKeyspace and ItemGroupKeyspace changes ----> ListingRevisionKeyspace (history)
```

The arrows describe business relationships and service flows. They are not
relational joins supplied by NuData.

### The five families and 22 declared logical docsets

| Keyspace | Logical docsets | Count |
| --- | --- | ---: |
| `ItemKeyspace` | `__ROOT__`, `ItemCompatibility`, `ItemDescription`, `ItemQtyPrice`, `ItemDetails`, `BusinessPolicies`, `UuidMap`, `ItemLock` | 8 |
| `ItemGroupKeyspace` | `__ROOT__`, `GroupDescription`, `GroupBusinessPolicies` | 3 |
| `ListingDraft` | `__ROOT__`, `ItemDraft`, `ItemDraftCompatibility`, `ItemGroupDraft`, `ItemGroupDraftCompatibility`, `ItemGroupDraftDesc` | 6 |
| `UserListingDraft` | `UserItemDraftMap` | 1 |
| `ListingRevisionKeyspace` | `__ROOT__`, `ListingRevision`, `ListingRevisionDetail`, `VariationRevisionDetail` | 4 |
| **Total** |  | **22** |

This is a schema-declaration count. A single producer operation writes only
the docsets needed for that operation; it does not write all 22 documents.

## Why Item and Item Group are separate

The distinction is clearest for SSKU and MSKU listings.

### SSKU: one sellable item

An SSKU has no variation parent. Its current state is held in one
`ItemKeyspace` document family.

```text
ItemKeyspace / itemId
├── __ROOT__                 broad current item state
├── ItemQtyPrice             sellable price and quantity
├── ItemDescription          seller description
└── other optional or operational item docsets
```

### MSKU: one shared group and many sellable variations

An MSKU has data with two different ownership boundaries:

```text
ItemGroupKeyspace / groupId
├── __ROOT__                 group title, itemIds, variation dimensions, shared images
├── GroupDescription         shared description
└── GroupBusinessPolicies    shared policies

ItemKeyspace / itemId-1      first sellable variation
ItemKeyspace / itemId-2      second sellable variation
...
ItemKeyspace / itemId-N      Nth sellable variation
```

The `ItemGroupKeyspace.__ROOT__.itemIds` value identifies the member
variations. Each member item has `isVariation=true`, but it remains its own
sellable item with an item-level lifecycle and price/quantity state.

| Concern | MSKU group owns it once | Variation item owns it per sellable SKU |
| --- | --- | --- |
| Listing structure | Group identity, member item IDs, variation traits, trait-driven images | The variation's selected trait values |
| Shared seller content | Group title, description, business policies, shared images | Item-specific content when applicable |
| Commercial operations | Not the price or inventory counter for every variation | Price, available quantity, sold quantity, locks, and item lifecycle |

Storing shared data once avoids copying group-owned content to every
variation. Storing commercial state per variation allows a price or inventory
change to address only the sellable SKU that changed. This is a producer
ownership and mutation design, not a ready-made parent/child reporting table.

## Why ItemKeyspace has many docsets

`ItemKeyspace` is the current-state family with the broadest set of Selling
operations. Its docsets split state by update behavior, payload character,
specialization, and lookup or reservation purpose.

| Docset | Producer boundary | Why it is separate |
| --- | --- | --- |
| `__ROOT__` | Broad item identity, seller/location, category, lifecycle, flags, media references, and other item state. | A price update or description-only read should not require rebuilding or fetching the broad item payload. |
| `ItemQtyPrice` | Available quantity, quantity sold, remnant rules, and price variants. | This is the focused commercial state used by price and inventory operations. |
| `ItemDescription` | Seller description and description revision time. | Description can be large, has its own revision, and can be stored expanded or compressed. |
| `ItemCompatibility` | Parts fitment or compatibility content. | This is specialized, potentially large content that common item reads need not carry. |
| `BusinessPolicies` | Return, payment, and shipping policy content. | Policies are a cohesive policy payload with a different access and update boundary from core item identity. |
| `ItemDetails` | High-precision prices, relaxed-rule state, and supporting seller documents. | Specialized details do not belong on every common item path. |
| `ItemLock` | Inventory reservation and lock-summary state. | Lock flows have a dedicated operational lifecycle and should not rewrite broad item state. |
| `UuidMap` | Seller-and-UUID lookup to listing and application identifiers. | UUID-specific lookup avoids treating a broad item document as a lookup index. |

The first six are the normal current-item document family. `ItemLock` and
`UuidMap` are auxiliary operational branches in the same keyspace, not fields
that every item create or full-item read must use.

### Design principle: partition by producer access pattern

Selling does not start with the question, “What fields should a consumer see
in one listing record?” It starts with, “Which part of listing state does this
service own, change, or need for this operation?” A docset is created when
that part of the item has a meaningfully different mutation, retrieval,
payload, or operational-identity boundary.

| Producer question | Docset design response | ItemKeyspace example |
| --- | --- | --- |
| Does this state change on a focused commercial operation? | Keep it independently addressable from broad listing state. | Purchases and price updates address hot `ItemQtyPrice`, rather than rewriting category, media, lifecycle, and other root fields. |
| Is this content large, irregular, or unnecessary for many reads? | Put it in an optional payload that readers request only when needed. | `ItemDescription` and `ItemCompatibility` hold seller text and fitment; each can use an expanded or compressed representation. |
| Does the operation have specialized or infrequent behavior? | Keep its data out of the common item path. | `ItemDetails` holds high-precision prices and seller documents; `ItemCompatibility` supports fitment-specific behavior. |
| Does the operation need its own key and lifecycle? | Use a purpose-specific document shape instead of overloading the item root. | `ItemLock` manages reservations and a lock summary; `UuidMap` supports seller-and-UUID lookup. |

This principle makes docsets **selective retrieval and targeted-update
boundaries**. The performance consequence is that a known operation can avoid
unrelated payload and a consumer-like full-item assembly when it is not
needed. It does not, by itself, guarantee a particular latency, throughput,
storage, or concurrency result; those depend on the NuData implementation,
payload sizes, request composition, caching, and service behavior.

### Item hierarchy is a storage and mutation hierarchy

The conceptual key layout is:

```text
ItemKeyspace
├── itemId
│   ├── __ROOT__ / itemId
│   ├── ItemQtyPrice / QTY_PRICE_<itemId>
│   ├── ItemDescription / DESC_<itemId>
│   ├── ItemCompatibility / COMPAT_<itemId>
│   ├── BusinessPolicies / BIZ_POL_<itemId>
│   ├── ItemDetails / ITEM_DETAILS_<itemId>
│   └── ItemLock / LOCK_<lockId> or lock-summary key
└── sellerId + uuid
    └── UuidMap
```

The hierarchy tells the service which document it can read, update, or create
for an item operation. It does **not** mean every item reader must traverse
every branch, nor that every child is a relational row to join without
business rules.

### Examples: price/quantity and description

`ItemQtyPrice` is intentionally narrower than the item root. It groups
available and sold quantity with the listing's price variants. A price update
can address this commercial branch rather than rebuilding category, media,
seller, lifecycle, and policy-reference fields in `__ROOT__`.

`ItemDescription` is intentionally separated because seller-authored content
can be large and irregular. The service writes either `desc` or compressed
`compDesc`, together with `descRevsnDt`, and can read the description without
requesting the full item. A downstream consumer must therefore decide whether
to decompress content and must not treat the two representations as two
independent descriptions.

## Hierarchical POJOs are different from docset hierarchy

Two kinds of hierarchy exist in this design, and they solve different
problems.

| Hierarchy | Example | What it preserves |
| --- | --- | --- |
| **Document hierarchy** | `itemId` ancestor with `ItemQtyPrice` and `ItemDescription` child docsets. | Separate producer access, mutation, payload, and lifecycle boundaries. |
| **Embedded object hierarchy** | `price.fixedPrice.currency`, `lifecycle.startDate`, `category.primaryCategoryId`, `aspects[]`. | Cohesive Selling concepts and their internal cardinality. |

The producer POJOs are composed objects, not a single flat bag of fields.
For example, `BaseItem` uses `Amount` for price values, lists for aspects,
images, identifiers, and compatibility, and objects such as
`BusinessPolicies`, `Lifecycle`, `Format`, and `TermsAndPolicies`.

The document converter preserves that cohesion while deciding which document
owns each producer concern:

```text
Item / BaseItem POJO
├── broad identity, lifecycle, category, images  -> ItemKeyspace.__ROOT__
├── available quantity and Amount price variants -> ItemQtyPrice
├── seller description                            -> ItemDescription
├── compatibility list                            -> ItemCompatibility
├── return, payment, and shipping policies        -> BusinessPolicies
└── precision prices and seller documents         -> ItemDetails
```

Within a docset, nesting prevents related values from being separated. For
example, each price amount keeps its `value` and `currency` together, and
`price` groups fixed-price, auction, marketing, and reference-price concepts.
Not every listing format uses every price variant.

A flat raw schema would instead create many nullable, format-specific fields,
such as `fixed_price_value`, `fixed_price_currency`,
`auction_reserve_value`, and `auction_reserve_currency`. It would also force
the schema to grow when a producer object gains another optional nested
concept. Flattening may be appropriate in a downstream model, but it is a
consumer transformation decision, not evidence that the producer document
shape is incorrect.

## Code evidence: `crlstngsv` POJOs to NuDocs

The source code makes the producer orientation explicit. The Selling-domain
objects in `crlstngsvLib` are converted into NuData-specific classes in the
service layer; the mapping is not a direct persistence of a universal
consumer record.

| Producer aggregate or payload | Write-side mapper | NuData target | Read-side reconstruction |
| --- | --- | --- | --- |
| `Item` and its `BaseItem` composition | `DocumentConverter.getRoot`, `getQtyPrice`, `getDescription`, `getItemCompatibility`, `getBusinessPolicies`, and `getItemDetails` | `ItemKeyspace.__ROOT__` and the corresponding item child docsets | `GetItemDocumentConverter` offers status, summary, description-only, full-without-description, and full assembly methods. |
| `NormalizedLockRequest` and UUID-specific lookup flows | `DocumentConverter.getItemLock` and dedicated lookup processing | `ItemLock` and `UuidMap` in `ItemKeyspace` | Locks and UUID mappings are operational lookups, not a projection of every `Item` field. |
| `ItemGroup` with member item IDs and variation attributes | `ItemGroupDocumentConverter.getRoot` and `getDescription`; shared policies use `DocumentConverter.getBusinessPolicies` | `ItemGroupKeyspace.__ROOT__`, `GroupDescription`, and `GroupBusinessPolicies` | `ItemGroupDocumentConverter` reconstructs status, summary, full-without-description, full, and description-only group payloads. |
| `ListingDraft`, `DraftSession`, `ItemDraft`, and `GroupDraft` | `DraftDocumentConverter.getRoot`, `getGroup`, `getGroupDescription`, compatibility creation, and `getItems` | `ListingDraft.__ROOT__`, item-draft, group-draft, compatibility, and group-description docsets | `GetDraftDocumentConverter.getListingDraft` combines root, group, description, compatibility, and item documents into a `ListingDraft`. |
| `ActiveListingDraft` plus user ID | `UserListingDraftDocumentConverter.getUserListingDraftDoc` | `UserListingDraft.UserItemDraftMap` | `getActiveListingDraft` recreates the active-draft summary, not the full `ListingDraft`. |
| `RevisionHistoryDataContainer` and derived revision records | `RevisionHistoryProcessor` delegates to listing, property-detail, and variation-detail processors before the NuData client insert | `ListingRevisionKeyspace.ListingRevision`, `ListingRevisionDetail`, and `VariationRevisionDetail`; `__ROOT__` is conditional retention state | Revision records are generated history payloads, intentionally separate from reconstruction of the latest `Item` or `ItemGroup`. |

Two concrete examples demonstrate why this matters:

- `DocumentConverter.getQtyPrice(Item, ...)` creates a NuData `Price` object
  from several `Item` `Amount` values, while description and compatibility
  converters choose a compressed representation only when compression
  produces a value.
- `CoreItemProcessor` explicitly creates root, description, quantity/price,
  details, policies, and compatibility documents for item writes. Conversely,
  `GetItemDocumentConverter` selects and assembles only the documents needed
  by the requested status, summary, description-only, or full read.

The converter layer is therefore a producer-owned persistence mapping layer.
It encodes how Core Listing Service operates on NuData; it does not remove the
need for a consumer-oriented contract.

## What downstream consumers need

A consumer-ready listing model should be produced from NuData rather than
using raw docsets as if they were complete business tables.

| Downstream responsibility | Why the raw producer model does not do it automatically |
| --- | --- |
| Select the intended state | Current item/group state, draft state, user draft index, and revision history have different business meanings. |
| Discover and assemble source documents | An MSKU requires a group plus selected member items; an item can require selected child docsets. |
| Decode and canonicalize content | Description and compatibility may be expanded or compressed; optional variants and abbreviated fields need common rules. |
| Normalize nested and repeated data | Price envelopes, aspects, images, compatibility, policies, and variation traits need a deliberate entity, column, or child-record design. |
| Define consumer business keys and grain | Storage keys and generated child keys do not by themselves define a reporting, analytical, or ML entity grain. |
| Apply quality rules and retain lineage | Consumers need rules for nulls, duplicates, lifecycle filters, type conversion, and traceability back to keyspace/docset/field. |

For the Item domain, the existing governed `item` and `variation` LDMs are
the right direction: they provide a consumer-facing logical interface above
the raw document families. The required ETL or rearrangement is the boundary
that turns producer-operational data into readable, stable downstream data.

## Evidence and limits

- [NuData write-flow research](item-nudata-write-flow.md) documents the five
  live keyspaces, all 22 declared docsets, their key shapes, and observed
  write behavior.
- [Listing NuData Design](../wiki/Listing_NuData_Design.md) documents live,
  draft, revision, and archive storage categories and the SSKU/MSKU split.
- [Core Listing Service NuData V2 database schema](../wiki/Core_Listing_Service-NuData_V2_Database_Schema.md)
  documents docset roles and frequency tiers.
- The `crlstngsv` source evidence comes from the V2 entity POJOs and the
  service converter and processor classes named in the mapping table. Those
  classes show the producer-to-NuDoc transformation and selected read
  reconstruction paths.

The original schema-design ADR is not present in this documentation set.
Accordingly, this page explains the design from observed key hierarchy,
payload shape, and service conversion/read-write behavior. It does not assert
undocumented latency targets, cross-document transaction guarantees, or
historical intent.
