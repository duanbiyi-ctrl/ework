# NuData Schema Analysis

## Scope and evidence

This is a cross-keyspace analysis of the NuData document families represented
in this repository:

- `ItemKeyspace`
- `ItemGroupKeyspace`
- `ListingDraft`
- `ListingRevisionKeyspace`
- `UserListingDraft`

It complements the individual LDM pages; it does not replace their field
reference tables. The two `ItemKeyspace` documents, `__ROOT__` and
`ItemQtyPrice`, are examined in more detail because they show the main
document-family and hot-state design patterns.

### Evidence hierarchy

| Evidence | What it establishes | Important limitation |
| --- | --- | --- |
| `data/*/*_schema.json` | The exported physical column registry, including dotted paths and storage-oriented types where populated. | Some exports are incomplete. In particular, `ItemQtyPrice` and `BusinessPolicies` have no `Columns` entries. An empty export is not evidence of an empty runtime document. |
| `data/sample-data/.../*.json` | Observed serialized shape, NuData metadata, key hierarchy, nulls, and example field presence. | A sample proves observation, not requiredness, completeness, or universal semantics. |
| `docs/entities/*.md` | The repository's current LDM names, logical field descriptions, and documented read/write behavior. | These pages can lag physical exports or implementation naming. |
| `docs/wiki/*.md` | Architectural intent, collection grouping, access tiers, and lifecycle descriptions. | Wiki content is explanatory evidence, not a versioned physical schema contract. |
| Core Listing Service implementation analysis | Converter mappings, deterministic child IDs, multi-docset reads, and targeted updates. | The implementation repository is separate; behavior can evolve independently of these artifacts. |

Terms used below:

- **Root**: the `__ROOT__` document at a keyspace ancestor.
- **Docset / collection**: a named child document type, such as
  `ItemQtyPrice`.
- **Logical field**: a domain-level name and meaning used in the LDM pages.
- **Physical path**: an exported or serialized field name, including a dotted
  path such as `category.prmryCtgrId`.
- **Observed**: present in a supplied raw sample, not a required-field claim.

## NuDocument shape and cross-keyspace topology

### Key hierarchy

Samples represent a root key as a `__key` array containing one
`__ROOT__` segment. A child document appends a segment for its docset:

```json
[
  { "collection": "__ROOT__", "string": "<ancestor-id>" },
  { "collection": "<ChildDocset>", "string": "<child-document-id>" }
]
```

`__key` and `__meta` are observed NuData system metadata, not business fields.
`__meta` records document creation and modification timestamps and a revision.
The exported catalog's `__KEY` column is a related storage representation, but
it should not be treated as a user-authored JSON property. A root's domain
identifier (`PK`, `lstgId`, or user ID depending on the keyspace) and a child
document's payload ID are distinct from this system key path.

The following relationships are documented application relationships, not
database-enforced foreign keys established by these exports:

```text
UserListingDraft user -> active ListingDraft IDs
ListingDraft -> published Item and/or ItemGroup
ItemGroup -> variation Item IDs
Item or ItemGroup -> ListingRevision history
Item __ROOT__ -> ItemQtyPrice -> ItemLock documents
```

### Keyspace inventory

| Keyspace | Root identity | Document-family purpose | Detailed pages |
| --- | --- | --- | --- |
| `ItemKeyspace` | Item `PK` | Current state of a single-SKU item or an MSKU variation. | [Item root](itemkeyspace-root.md), [quantity and price](itemkeyspace-item-qty-price.md) |
| `ItemGroupKeyspace` | Group `PK` | Current state and variation structure for an MSKU parent. | [Item group root](itemgroupkeyspace-root.md) |
| `ListingDraft` | Draft root identity | Pre-publication state for a single item or a group and its variations. | [Listing draft root](listingdraft-root.md) |
| `ListingRevisionKeyspace` | `lstgId` | Historical revisions for an item or item group. | [Revision root](listingrevisionkeyspace-root.md) |
| `UserListingDraft` | User ancestor plus draft child | Per-user active-draft index and summary. | [User draft map](userlistingdraft-user-item-draft-map.md) |

## ItemKeyspace deep dive: `__ROOT__`

### Role and identity

`ItemKeyspace.__ROOT__` is the broad, current-state item document. The current
catalog calls its domain identifier `PK`; the raw samples show that `PK`
matches the root key segment's item identifier. It is the ancestor for the
item's related documents, but it does not embed all of their data.

The root export contains both scalar fields and flattened physical paths:

| Physical pattern | Interpretation |
| --- | --- |
| `PK`, `sellerId`, `uuid`, `drftId`, `grpId` | Identity and cross-domain references. |
| `category.*`, `charity.*`, `lifecycle.*`, `trmsAndPolicies.*` | Embedded domain objects exported as dotted paths. |
| `PrmnlDtls.*`, `cstmPol.*`, `rgltryInfo.*` | Optional complex product, promotional, policy, and regulatory state. |
| `__KEY` | Storage-key representation in the catalog export, not a replacement for `PK`. |

The raw root sample confirms `__key`, `__meta`, `PK`, embedded `lifecycle`,
and embedded `trmsAndPolicies` objects. It also contains both `null` fields
and empty arrays. Therefore, absence from a particular sample must not be
read as a statement that the field is unsupported, while `null` must not be
read as a field-level prohibition.

### Logical field families

The root is intentionally broad. Its field families clarify what belongs here
and what must be fetched from another docset.

| Field family | Representative physical fields | Role |
| --- | --- | --- |
| Identity and provenance | `PK`, `uuid`, `sellerId`, `slrItemKey`, `drftId`, `grpId`, `listingAppId`, `crLstgDtVrs`, `vrsnId` | Identifies the item, seller context, source draft or group, and revision/version context. |
| Listing state and lifecycle | `format`, `lifecycle`, `crtDate`, `lastModDate`, `itmRevsnDt`, `outOfStockDt`, `admEndDt`, `endRsn`, `rlstId`, `rlstPrntId` | Records current listing lifecycle and revision state. |
| Classification and catalog | `title`, `category.*`, `aspects`, `epid`, `gblIdentifiers`, `conditionId`, `cndIdNum`, `conditionDesc`, `cndDescriptors` | Describes what is listed and how it is categorized or conditioned. |
| Seller, location, and media | `itmLocn*`, `images`, `videos`, `mktplcLstdOn`, `notes`, `sprtCntct` | Captures listing presentation and seller/location context. |
| Terms, references, and compliance | `trmsAndPolicies`, `tax`, `charity`, `epr`, `cstmPol`, `rgltryInfo`, `prgSpprtd` | Stores embedded policy references and related terms. Detailed payment, return, and shipping policy content is in `BusinessPolicies`. |
| Feature and behavior flags | `isVariation`, `mngByInv`, `onHold`, `itmOnSale`, `isScheduled`, `isBusinessPolicyItem`, `isSCOStatusIndicator`, and related flags | Represents current behavior, eligibility, and listing-feature state. |

The sample contains `isVariation: false` for the observed records. This only
demonstrates the supplied examples are non-variation items; it does not alter
the documented meaning that `isVariation` identifies an MSKU child item.

### Root versus related document boundary

| Data concern | Stored at root | Stored outside root | Why the distinction matters |
| --- | --- | --- | --- |
| Item identity and listing state | Yes | No | Root is the current-state anchor. |
| Available/sold quantity and standard prices | No | `ItemQtyPrice` | Inventory and price state can be read and updated independently. |
| High-precision fixed or starting-bid prices | No | `ItemDetails` | They are not aliases for the standard price fields. |
| Detailed payment, return, and shipping terms | Policy references remain under `trmsAndPolicies` | `BusinessPolicies` | A consumer needs the detailed policy doc for the policy content. |
| Description text | No | `ItemDescription` | Keeps large or compressed text separate. |
| Compatibility or fitment payload | No | `ItemCompatibility` | Keeps expanded or compressed compatibility data separate. |
| Reservations and lock lifecycle | No | `ItemLock`, below the quantity/price branch | Lock state is operational inventory state, not root listing state. |

The supplied wiki and existing entity pages describe root reads as part of
status and full-item reads, while multi-docset reads add only the documents
needed by a field group. This supports an access-pattern interpretation of the
split. It does **not** prove a particular storage-engine partitioning,
transaction, or throughput guarantee.

### Design rationale: direct answers

#### 1. Why separate `ItemQtyPrice` from `ItemKeyspace.__ROOT__`?

Because they have different access and update lifecycles.

`__ROOT__` is the broad current-state item record: identity, listing
lifecycle, classification, media, policy references, and many feature flags.
`ItemQtyPrice` is a narrower child document holding inventory and standard
pricing state. The supplied [ItemKeyspace wiki](../wiki/ItemKeyspace.md)
explicitly describes it as frequently updated. The Core Listing Service
price-and-quantity operation also directly updates the `ItemQtyPrice` child,
while separately updating root revision and modification fields. Inventory
reads can therefore include price/quantity without fetching the entire root
document family, and a root/status read need not fetch price state.

The quantity/price branch is also the parent of `ItemLock` records. Keeping
available and sold quantities adjacent to reservation state gives the lock
workflow a focused data boundary instead of mixing operational inventory
records with broad listing metadata.

This does **not** mean `__ROOT__` is immutable or `ItemQtyPrice` is the only
mutable data. For example, a price-and-quantity update can also revise selected
root fields, and detailed policies, descriptions, compatibility, and
high-precision prices have their own docsets. The supported conclusion is
therefore **update/read locality**, not a claim of independently guaranteed
performance or transaction behavior.

#### 2. Why are these fields in `ItemQtyPrice`?

They answer one coherent operational question: **what quantity of this item is
available or sold, and what standard price configuration applies to that
sellable unit?**

| Field group | Why it belongs with quantity/price state |
| --- | --- |
| `availQty`, `qtySold` | They are the two core inventory counters read and written by quantity-related flows. `qtySold` is system-managed in the implementation, which further distinguishes it from descriptive item attributes. |
| `minRmntSet`, `qtySldByPickpStre` | They are inventory adjustments or inventory-history counters, not product identity, category, media, or listing lifecycle attributes. |
| `price.*` | Fixed-price, auction, marketing, original-retail, cost-of-goods, and price-guarantee values describe the item's price state; they are consumed alongside the quantity counters in inventory-oriented reads. |
| `ItemQtyPriceID` | It identifies this child document within the item's document family; it is document identity, not an item business attribute. |

The boundary is deliberately narrower than "all fields changed during an item
update." `lastModDate`, versions, lifecycle, category, hold state, and other
listing metadata remain at root. High-precision fixed and starting-bid prices
remain in `ItemDetails`. This tells consumers not to assume that
`ItemQtyPrice` is a complete pricing or state snapshot; it is the
standard-price and inventory slice.

The repository contains no design ADR that assigns an individual historical
reason to every selected field. The field grouping above is the evidence-based
rationale from the update paths, read groups, raw shape, and documented field
roles.

#### 3. Why is `ItemQtyPrice` nested instead of flat?

The nested `price` object is a logical aggregate, not merely formatting. It
groups alternative or related price concepts below one field:
fixed-price, auction reserve, starting bid, marketing price, original retail
price, cost of goods, and price-guarantee enrollment. A listing format can
need only a subset, so the raw samples can represent inapplicable variants as
`null` without inventing separate top-level state categories.

Each monetary price is nested one level further as an `Amount`:

```text
price.<price-kind>.currency
price.<price-kind>.value
```

That keeps a currency coupled to the amount it qualifies. A flat alternative
would require a larger, less cohesive namespace such as
`fixedPriceValue`, `fixedPriceCurrency`, `startingBidValue`, and
`startingBidCurrency`; it would make the association between an amount and its
currency a naming convention rather than part of the data shape.

The nested form also leaves one stable extension point for new price concepts
and matches the converter's mapping from the item price model to one
`ItemQtyPrice.price` value. It does **not** make individual price members
indivisible: the implementation addresses nested physical paths during
targeted updates, and the schema export can flatten nested paths for catalog
purposes. Nor does nesting itself supply validation, pricing rules, or
transactional guarantees.

## ItemKeyspace deep dive: `ItemQtyPrice`

### Key path and document identity

An observed `ItemQtyPrice` record has:

```text
__ROOT__/<item-id>/ItemQtyPrice/QTYPRICE_<item-id>
```

The payload's `ItemQtyPriceID` repeats the deterministic child ID. This is
useful as a self-identifying payload field, but it is not the parent item
identifier and it does not replace the complete NuData `__key` path.

The current `ItemPriceAndQuantity` page says `QTY_PRICE_<itemId>`, while the
raw samples consistently use `QTYPRICE_<itemId>`. Core Listing Service
implementation analysis also uses `QTYPRICE_`. The sample and implementation
form are therefore the documented observed/current form; the older entity-page
prefix is a terminology discrepancy, not an alternative inferred key.

### Top-level fields

| Physical field | Logical type | Meaning | Sample behavior |
| --- | --- | --- | --- |
| `ItemQtyPriceID` | String | Child document identifier. | Observed and matches the child key segment. |
| `availQty` | Integer | Available item quantity. | Observed. It is not the root's lifecycle state. |
| `qtySold` | Integer | Quantity sold. | Observed. Current implementation analysis treats it as system-managed rather than a free-form client field. |
| `minRmntSet` | Integer | Minimum remnant-set quantity. | Defined by the LDM page; not present in the supplied excerpted records. |
| `qtySldByPickpStre` | Integer | Quantity sold through the legacy pickup-store flow. | Defined by the LDM page; sample presence varies and no requiredness is implied. |
| `price` | `Price` object | Standard-price envelope for the item. | Observed. Its members may be populated or `null` independently. |

The `ItemQtyPrice` export has an empty `Columns` array. Consequently, the
table above is derived from the raw document shape, the existing LDM page, and
implementation model analysis rather than from a populated physical-column
export.

### `price` envelope

`price` contains price concepts for different listing and pricing modes rather
than a single universally applicable selling-price field.

| Physical path | Logical type | Role | Observed null behavior |
| --- | --- | --- | --- |
| `price.fixedPrice` | `Amount` | Fixed-price / Buy It Now amount. | Populated in the supplied fixed-price examples. |
| `price.auctnRsrvPrc` | `Amount` | Auction reserve amount. | `null` in the supplied fixed-price examples. |
| `price.strtBidPrice` | `Amount` | Auction starting-bid amount. | `null` in the supplied fixed-price examples. |
| `price.mrktngPrc` | `MarketingPrice` | Marketing and comparison-pricing information. | `null` in the supplied fixed-price examples. |
| `price.orgnRetailPrice` | `Amount` | Original retail/reference price. | Observed as a value in the supplied examples; it is not evidence that it is the active selling price. |
| `price.COGs` | `Amount` | Cost of goods. | `null` in the supplied fixed-price examples. |
| `price.prcGuarantee` | Boolean | Price-guarantee enrollment indicator. | Observed as `false` in the supplied fixed-price examples. |

An `Amount` is represented as an object with `currency` and `value`. The
currency is therefore carried by each monetary value rather than inferred from
the item root or another price field. No precision, rounding, or currency
conversion policy should be inferred from the JSON shape alone.

The sample's distinction between omitted top-level fields and `null` nested
price members is material:

- `minRmntSet` and `qtySldByPickpStre` are absent from the shown records.
- The `price` object remains present and shows non-applicable variants as
  explicit `null` values.

This is an observed serializer shape, not an API promise that every producer
will emit every optional nested price property.

### Price placement, locks, and access paths

The standard price and inventory state are grouped in `ItemQtyPrice`. Existing
documentation and implementation analysis show targeted price/quantity
updates addressing this child document while touching root revision metadata
as needed. Item reads use field-group/multi-docset selection: status can use
root state, while inventory-oriented reads include quantity/price state.

Two fields intentionally sit outside this envelope:

| Concern | Location | Consequence |
| --- | --- | --- |
| High-precision fixed and starting-bid prices | `ItemDetails.fixedPriceHP` and `ItemDetails.strtBidPriceHP` | Do not assume `ItemQtyPrice.price.fixedPrice` preserves high-precision values. |
| Reservation/lock records | `ItemLock` descendants of the quantity/price key branch | Available/sold quantities must be interpreted with the lock workflow when the consuming operation requires reservation state. |

The root comment, field-group reads, targeted updates, and lock adjacency
support the inference that this is a hot operational branch separated from
the broad root document. They do not establish an independently measured
performance characteristic or a cross-document atomicity guarantee.

## Remaining ItemKeyspace docsets

| Docset | Main field roles | Relationship and behavior evidence | Detailed page |
| --- | --- | --- | --- |
| `ItemDescription` | `ItemDescID`, `desc`, `compDesc`, `descRevsnDt` | Large description has expanded and compressed representations; documented as independently readable/updatable. | [Item description](itemkeyspace-item-description.md) |
| `ItemCompatibility` | `ItemCompID`, `compat`, `cmpCompat`, `ftExempt` | Stores fitment/compatibility in expanded or compressed form. Export emphasizes compressed fields; LDM adds the logical list. | [Item compatibility](itemkeyspace-item-compatibility.md) |
| `BusinessPolicies` | `plcsId`, `retTrms`, `pmtTrms`, `shipTrms` | Detailed return, payment, and shipping terms; root contains related policy identifiers/references. | [Item business policies](itemkeyspace-business-policies.md) |
| `ItemDetails` | `itemDetailsID`, relaxed-rule indicator, high-precision prices, `docs`, source listing ID | Houses fields intentionally excluded from the quantity/price envelope; the export flattens document paths. | [Item details](itemkeyspace-item-details.md) |
| `ItemLock` | Lock ID/status, quantity, expiration and lifecycle timestamps, UUID | Operational records associated with inventory locking. Existing docs state lock transitions can affect quantity/price state. | [Item lock](itemkeyspace-item-lock.md) |
| `UuidMap` | `listingId`, `listingAppId` | Auxiliary UUID-to-listing lookup, not an item-content projection. | [Item UUID mapping](itemkeyspace-uuid-map.md) |

`ItemDetails` is called both `ItemDetails` and `ItemDetailsDoc` across current
documents. This analysis uses the physical docset form `ItemDetails` where the
schema/export path uses it, while preserving the existing page's link.

## ItemGroupKeyspace

`ItemGroupKeyspace` is the current-state parent for an MSKU group. Its root
documents the variation structure and the IDs of member item documents; the
variations themselves remain `ItemKeyspace` items.

| Docset | Field-role summary | Relationship |
| --- | --- | --- |
| `__ROOT__` | Group identity, group draft reference, group title/type/version, owner, `itemIds`, `itmsVryBy`, image variation configuration, group images, seller group key, and group-level identifiers. | `itemIds` is the documented link to variation items; `itmsVryBy` describes the variation axes. |
| `GroupDescription` | Group description ID, expanded/compressed description, revision timestamp. | Separate large-text representation for the group. |
| `GroupBusinessPolicies` | Policy document ID and detailed return, payment, and shipping terms. | Reuses the item policy shape at group scope. |

The raw group samples show nested group images and variation structures that
are not all represented in the flattened export columns. Conversely, a
`null` `groupType` appears in a sample and does not change the LDM's logical
field definition. Creation/upsert behavior is documented as writing the root
with applicable description and policy children; it should not be generalized
to all partial-update semantics without implementation evidence.

Detailed references: [group root](itemgroupkeyspace-root.md),
[group description](itemgroupkeyspace-group-description.md), and
[group business policies](itemgroupkeyspace-group-business-policies.md).

## ListingDraft keyspace

`ListingDraft` holds pre-publication state. A draft root groups the shared
session/lifecycle data with an item draft for a single-SKU listing or group and
variation draft documents for an MSKU listing.

| Docset | Field-role summary | Cardinality or relationship |
| --- | --- | --- |
| `__ROOT__` | Draft identity, published-item references, original/relist references, dates, draft flags, and shared terms/history. | One root per draft. |
| `ItemDraft` | Item-level listing content, pricing, policies, media, product data, and revision state. | One for a single-SKU draft; one per variation for an MSKU draft. |
| `ItemDraftCompatibility` | Draft-item compatibility ID plus expanded/compressed compatibility. | Optional child for item-draft fitment. |
| `ItemGroupDraft` | Group title, group ID, variation axes, images, seller group key, and business policies. | MSKU group child. |
| `ItemGroupDraftCompatibility` | Group-draft compatibility ID plus expanded/compressed compatibility. | Optional group child. |
| `ItemGroupDraftDesc` | Expanded/compressed group description and revision timestamp. | Separate group-description child. |

Schema exports often list flattened physical columns while raw samples show
their nested objects, including policy, fulfillment, best-offer, and
auto-relist shapes. This is a representation difference, not proof that the
sample has undocumented logical fields. Existing pages document batch writes
of the root and applicable child set; the selected child set differs by
single-SKU versus MSKU draft.

Detailed references: [draft root](listingdraft-root.md),
[item draft](listingdraft-item-draft.md),
[item draft compatibility](listingdraft-item-draft-compatibility.md),
[group draft](listingdraft-item-group-draft.md),
[group draft compatibility](listingdraft-item-group-draft-compatibility.md),
and [group draft description](listingdraft-item-group-draft-desc.md).

## ListingRevisionKeyspace

`ListingRevisionKeyspace` is an append-oriented history family. Its root
uses `lstgId`, which can represent an item or group listing; revision and
detail child documents record what changed.

| Docset | Field-role summary | Relationship |
| --- | --- | ---|
| `__ROOT__` | Listing/history ancestor identity. An `expiredDate` is observed in raw samples but is not part of the generated root-model field table. | One history root per item or group listing identity. |
| `ListingRevision` | Revision ID, revised date, application ID, significant revision count, changed property groups, version-created indicator, and core-listing version. | One or more revisions below the history root. |
| `ListingRevisionDetail` | Changed property group/property, change type, old/new value, optional label. | Field-level details for a revision. |
| `VariationRevisionDetail` | Variation item ID, variation property and group, change type, old/new values, and variation trait values. | Variation-level detail for MSKU changes. |

Samples show that optional detail fields are not present in every record:
`lbl` is not observed in the examined listing-detail records, and `newVal` or
`oldVal` is not observed in every variation-detail record. These absences are
not requiredness statements. The wiki describes variation detail as MSKU
specific and gives property-group examples; it is supplementary semantic
evidence, not a physical enum declaration.

Detailed references: [revision root](listingrevisionkeyspace-root.md),
[revision](listingrevisionkeyspace-listing-revision.md),
[revision detail](listingrevisionkeyspace-listing-revision-detail.md), and
[variation revision detail](listingrevisionkeyspace-variation-revision-detail.md).

## UserListingDraft keyspace

`UserListingDraft` is a per-user active-draft index, separate from the
draft-content keyspace. The raw key path shows a user ancestor with a
draft-specific child mapping.

| Docset | Field-role summary | Relationship |
| --- | --- | --- |
| `UserItemDraftMap` | Draft ID, marketplace, application, primary category, creation mode, title/image summary, creation date, user ID, and last-modified date. | Maps a user to an active-draft summary rather than duplicating the complete `ListingDraft` content. |

The samples show multiple creation-mode values. Those examples demonstrate the
stored field's use but do not define a closed enum. The current wiki material
mentions this keyspace only at a high level, so the entity page is the primary
repository-local reference for its field roles.

Detailed reference: [user item draft map](userlistingdraft-user-item-draft-map.md).

## Cross-keyspace lifecycle and access matrix

| Lifecycle concern | Primary family | Related family | Evidence-qualified interpretation |
| --- | --- | --- | --- |
| Drafting an item or group | `ListingDraft` | `UserListingDraft` | Draft content is held in the draft family; the user map is an active-draft index. |
| Publishing a single item | `ItemKeyspace` | `ListingDraft`, `ListingRevisionKeyspace` | Wiki documents a draft-to-current-state flow; history behavior depends on the publishing/revision operation. |
| Publishing an MSKU group | `ItemGroupKeyspace` and `ItemKeyspace` | `ListingDraft`, `ListingRevisionKeyspace` | Group root describes the variation structure and member item IDs; each variation is an item document. |
| Updating price or quantity | `ItemKeyspace.ItemQtyPrice` | `ItemKeyspace.__ROOT__`, `ItemLock`, `ItemDetails` | Standard quantity/price state is isolated in `ItemQtyPrice`; root version metadata and lock workflow can also matter. |
| Reviewing history | `ListingRevisionKeyspace` | Item or item group | Revision root is addressed by item or group listing identity. |

## Delta register and open questions

| Area | Observed difference | Treatment in this analysis |
| --- | --- | --- |
| `ItemQtyPrice` key prefix | Existing entity page says `QTY_PRICE_`; raw samples and implementation analysis use `QTYPRICE_`. | Use `QTYPRICE_` as observed/current; retain the existing-page link and call out the discrepancy. |
| `ItemQtyPrice` and `BusinessPolicies` exports | Both exports have an empty `Columns` list. | Do not claim their LDM field list is export-derived; identify sample/model/document sources. |
| Key representation | Exports use `__KEY`; raw documents use `__key` plus `__meta`. | Treat these as storage/runtime representations, not interchangeable logical fields. |
| `ItemDetails` naming | Current material uses `ItemDetails` and `ItemDetailsDoc`. | Use the physical/export docset name and flag the alias. |
| Flattened paths | Exports contain dotted nested fields; samples contain nested JSON objects. | Treat as two representations of the same candidate structure only when names align; do not invent unexported child fields. |
| `ItemLock` types | Entity pages use `long`/`Long`; export types use `number`/`numberInt`. | Preserve each source's representation; no exact width/nullable contract is inferred. |
| Revision root expiration | `expiredDate` appears in raw samples but not the generated root field table. | Record it as an operational sample field pending schema ownership confirmation. |
| User draft coverage | The user-map entity page is more detailed than the supplied wiki. | Prefer the entity page for field roles and identify the limited wiki coverage. |

## Source index

### Schema exports and samples

- [ItemKeyspace exports](../../data/itemkeyspace/) and
  [raw ItemKeyspace samples](../../data/sample-data/item-raw-ldm-samples/ItemKeyspace/)
- [ItemGroupKeyspace exports](../../data/itemgroupkeyspace/) and
  [raw group samples](../../data/sample-data/item-raw-ldm-samples/ItemGroupKeyspace/)
- [ListingDraft exports](../../data/listingdraftkeyspace/) and
  [raw draft samples](../../data/sample-data/item-raw-ldm-samples/ListingDraft/)
- [ListingRevisionKeyspace exports](../../data/listingrevisionhistorykeyspace/)
  and [raw revision samples](../../data/sample-data/item-raw-ldm-samples/ListingRevisionKeyspace/)
- [UserListingDraft export](../../data/userlistingdraftkeyspace/) and
  [raw user-draft sample](../../data/sample-data/item-raw-ldm-samples/UserListingDraft/)

### Supplied wiki material

- [ItemKeyspace](../wiki/ItemKeyspace.md)
- [Core Listing Service NuData V2 Database Schema](../wiki/Core_Listing_Service-NuData_V2_Database_Schema.md)
- [Listing NuData Design](../wiki/Listing_NuData_Design.md)

### Related LDM pages

All per-docset LDM pages remain under [the entities directory](./). Use them
for the detailed field dictionaries; use this page to understand document
boundaries, evidence quality, and cross-keyspace relationships.
