# ULP Listing Data Reference

This reference explains how Unified Listing Platform (ULP) data relates to
Core Listing Service (CLS) NuDoc data. It helps consumers choose the correct
listing-data surface and records the provider-local storage and lifecycle
facts established by the checked-out source.

## Scope and evidence

The analysis is based on the shared services and provider repositories linked
locally under `.link/`:

| Repository | Role proven by source | Not proven by source |
| --- | --- | --- |
| `crlstngsv` | CLS accepts, persists, reconstructs, and changes core listing state. Its converters map V2 listing objects to NuDoc document families. | A complete public ULP API contract or post-listing provider calculations. |
| `unilistingsvc` | The ULP listing-read service supplies `ListingV2` and `Item`, maps fields to groups, gates provider queries, reads cached group data, and refreshes groups from provider events. | A provider's storage, calculation, or deployment enablement. |
| `fgql` | The Federated GraphQL Gateway composes the graph, validates and routes requests, and provides local schema snapshots. | NuDoc writes, provider business logic, or a guarantee that a snapshot is the deployed graph. |
| `ulp_providers` | The 25 direct provider repositories establish each provider's output schema, local resolver and storage behavior, and any local write or refresh path. | External-store schema, runtime provider enablement, source-system ownership, event delivery, or a production freshness guarantee unless provider code proves it. |

The sources establish a set of related, but different, layers:

```text
Seller or authorized listing workflow
  -> CLS V2 listing aggregate
  -> CLS NuDoc document families
  -> ULP current-listing projection and provider-group cache
  -> FGQL federated GraphQL response

Domain providers and derived-data jobs
  -> ULP provider groups
  -> FGQL federated GraphQL response
```

Provider storage means the provider-local persistence or request-time source
seen in code. A NuKV cache, an external service request, a CLS NuDoc document,
and the ULP provider-group cache are separate boundaries. Use the following
evidence labels throughout this page:

| Label | Meaning |
| --- | --- |
| **Directly mapped** | A CLS converter/reconstructor and a ULP field or generated mapping establish the relationship. |
| **Family correspondence** | The sources establish the same business concept at a document-family and API-family level, but not a safe one-to-one leaf-field mapping. |
| **NuDoc-only** | CLS persists or operates on the state, but the normal ULP current-listing contract does not establish an equivalent field. |
| **ULP-only** | ULP exposes the state through a provider or GraphQL contract, but CLS core NuDoc source does not establish it as core listing state. |
| **Conditional** | Availability depends on authorization, gateway exposure, requested group, runtime configuration, or data readiness. |
| **Unverified** | The repositories do not prove exact cross-system lineage or behavior. |

!!! warning "Do not equate a GraphQL field with a NuDoc field"
    Similar names are not sufficient evidence of physical lineage. A ULP
    response may assemble multiple NuDoc documents, use cached state, add a
    provider result, transform a nested object, or omit an authorized field.
    Use the [field-tracing procedure](#tracing-a-specific-field) before
    recording an exact mapping.

## 1. Core listing data

### What CLS owns

CLS is the entity service for core listing data. It accepts seller or
authorized-workflow state and records it in a producer-oriented NuDoc model.
The model is organized by identity, lifecycle, mutation, payload, and lookup
needs. It is not designed as a single consumer-facing listing row.

| Core business action | CLS-recorded state | What a consumer must not infer |
| --- | --- | --- |
| Create listing | Initial identity, seller context, product content, terms, price/quantity, and lifecycle configuration. | That the item is buyer-visible, purchasable, or sold. |
| Revise listing | Seller-configured content and terms, including category, condition, media, policies, shipping, payment, and returns. | That every derived, search, risk, or fulfillment value was recomputed synchronously. |
| Change offer or availability | Price, quantity, auction/offer state, promotions, locks, or other commercial state. | A final buyer price, checkout quote, or fulfilled quantity. |
| Change lifecycle or control state | Scheduling, activation, renewal, ending, relisting, holds, administrative actions, and supported privacy controls. | Search visibility, fraud outcome, buyer eligibility, or settlement. |
| Save or change a draft | Seller working state before or during publication. | That a live item or group exists. |
| Record revision history or reconcile state | Historical change data, migration/repair, or consistency coordination. | That the record is the current listing state or a seller revision. |

CLS may dual-write during migration and has reconciliation paths. A
reconciliation or failure signal is an operational coordination event, not a
complete listing snapshot.

### Federated write and read boundary

The composed graph exposes seller-authorized `createListing`, `updateListing`,
`relistListing`, and `endListing` mutations. The FGQL schema snapshot assigns
those fields to the `LISTAPI` subgraph, not to FGQL or `unilistingsvc`. FGQL
validates and routes the mutation; CLS source establishes the core
listing-to-NuDoc persistence model, but neither boundary alone proves which
storage path a particular deployed mutation completed.

ULP lookup operations are read contracts. `listingV2ById`, `listingsV2ByIds`,
`itemsByIds`, and `sellerListings` expose accepted current state; they do not
create or revise a listing. During the Oracle migration, core seller-managed
data can be dual-written to NuData and Oracle. Availability is a notable
cross-domain exception: quantity can change outside a seller revision, such
as through a checkout flow moving to Central Availability Service (CAS).

### SSKU and MSKU data grain

ULP and NuDoc must both be interpreted at the correct grain.

| Listing shape | NuDoc owner | Meaning |
| --- | --- | --- |
| Single SKU (SSKU) | One `ItemKeyspace` item family, keyed by item ID. | One sellable item holds its current item-level state. |
| Multi-SKU (MSKU) shared state | One `ItemGroupKeyspace` group family, keyed by group ID. | Holds variation-group identity, member item IDs, variation dimensions, shared content, and shared policies. |
| Multi-SKU sellable state | One `ItemKeyspace` family for each member item, keyed by item ID. | Each variation remains a separate sellable item with its own commercial and lifecycle state. |

An MSKU ULP response is therefore not evidence that all shared and
variation-level state originates in one document. In CLS, the group identifies
the member item IDs; consumers must preserve the group-to-variation
relationship rather than flatten it into duplicate listing facts.

### CLS NuDoc current-state families

CLS converters and reconstructors show these producer-side boundaries for live
listing state:

| NuDoc family | Producer responsibility | Consumer interpretation |
| --- | --- | --- |
| `ItemKeyspace.__ROOT__` | Broad item identity, seller/location, category, format, lifecycle, flags, media references, and listing metadata. | Current broad item state; it is not necessarily the full customer-facing listing. |
| `ItemKeyspace.ItemQtyPrice` | Available and sold quantity, remnant rules, and price variants. | Commercial state for one sellable item or variation. |
| `ItemKeyspace.ItemDescription` | Seller description and description revision time; stored expanded or compressed when beneficial. | One description representation must be selected and decoded deliberately. |
| `ItemKeyspace.ItemCompatibility` | Vehicle/parts fitment and other compatibility payload. | Optional, potentially large specialized content. |
| `ItemKeyspace.BusinessPolicies` | Payment, fulfillment, return, tax, and related policy content. | Seller-selected terms, not a final buyer-specific decision. |
| `ItemKeyspace.ItemDetails` | High-precision prices, seller documents, and specialized item details. | Optional supporting item state. |
| `ItemKeyspace.ItemLock` | Inventory reservations and lock-summary state. | Operational reservation state, not a standard listing attribute. |
| `ItemKeyspace.UuidMap` | Seller-and-UUID lookup to item/listing/application identifiers. | Operational lookup index, not a listing projection. |
| `ItemGroupKeyspace.__ROOT__` | Group identity, member item IDs, variation traits, shared images, and group metadata. | Shared MSKU state that must be combined with member items. |
| `ItemGroupKeyspace.GroupDescription` | Shared group description. | Shared MSKU description, separate from each variation's content. |
| `ItemGroupKeyspace.GroupBusinessPolicies` | Shared group policies. | Shared policy state for the variation group. |

`DocumentConverter`, `ItemGroupDocumentConverter`, and
`GetItemDocumentConverter` provide the core evidence for the write and
reconstruction boundaries. Their methods create or reassemble root,
description, compatibility, quantity/price, policy, detail, and group
documents rather than serializing one universal listing object.

For the full NuDoc hierarchy, primary-key shapes, and draft/history families,
see [NuData write-flow research](../spike/item-nudata-write-flow.md) and
[Listing NuData Design](../wiki/Listing_NuData_Design.md).

### ULP current-listing read contract

The ULP schema defines `ListingV2` as the listing entity and `Item` as the
sellable-item entity. The federated schema exposes these normal lookup
operations:

| Operation | Use |
| --- | --- |
| `listingV2ById` | Retrieve one listing by listing ID. |
| `listingsV2ByIds` | Retrieve multiple listings by listing ID; the schema documentation sets a maximum of 100 IDs. |
| `itemsByIds` | Retrieve sellable item state by item ID. |
| `sellerListings` | Retrieve a seller-authorized listing view when the documented scopes are met. |

`itemsByVariationIds` is deprecated in favor of item-ID lookup. ULP source
also contains internal versioned and archived fallback calls; those
implementation paths do not, by themselves, extend the normal public
current-listing contract.

`ListingV2` and `Item` organize core information into consumer-oriented
families:

| ULP family | Examples in the GraphQL contract | Consumer meaning |
| --- | --- | --- |
| Identity and lineage | Listing, item, variation, seller-listing, and core-listing IDs; creation mode; source/relist relationships. | Identifies a listing or sellable item and, when populated, its lineage. |
| Seller product | Title, description, categories, aspects, condition, images, videos, vehicle identifiers, seller SKU, and variation traits. | Seller-defined offer content; it is not a guarantee of buyer-visible rendering. |
| Listing terms | Format, duration, buyer restrictions, fulfillment, payment, returns, tax, charity, regulatory content, and seller application data. | Accepted or selected terms that may require marketplace and buyer context. |
| Item commercial state | Item price, quantity, sold quantity, item-level terms, and variation-specific product state. | Recorded sellable-item state, not a checkout quote. |
| Lifecycle state | Created/revised times, listing dates and status, end reason, hold state, and relist information. | Current or recorded lifecycle state, not a search, risk, or payment decision. |

GraphQL type metadata also restricts fields by gateway and, for some fields,
by the seller's principal. A field can be part of the source schema while
being unavailable in a particular gateway or caller context.

### Federated response boundary

In normal gateway mode, FGQL validates an incoming request, creates a
Federation query plan from the loaded supergraph, makes authenticated subgraph
requests, and records the plan and participating subgraphs. The response is
therefore a federated API result, not a physical NuDoc record or a
transactionally current decision.

FGQL can also proxy requests to a router under static configuration or
dynamic ramp rules. That routing mode changes how a federated request is
executed; it does not change ownership of listing writes, CLS NuDoc state, or
provider business logic.

### Core coverage: ULP projection versus NuDoc families

This matrix is deliberately at the documented business-family level. It
identifies the required NuDoc assembly work and the ULP projection boundary
without inventing leaf-field parity.

| Business concept | ULP surface | CLS NuDoc source | Coverage | Important difference |
| --- | --- | --- | --- | --- |
| Listing/item identity, seller, category, format, lifecycle, broad metadata | `ListingV2` and `Item` identity, seller-product, term, and lifecycle families | `ItemKeyspace.__ROOT__`; `ItemGroupKeyspace.__ROOT__` for shared MSKU state | Family correspondence | ULP is a graph projection; NuDoc divides current item and group state by key. |
| SSKU and MSKU membership | Listing/item/variation fields and identifiers | Group root member `itemIds` plus member `ItemKeyspace` records | Family correspondence | Group and variation values have different grains and must not be duplicated. |
| Seller description | Seller-product/listing description and revision fields | `ItemDescription` or `GroupDescription` | Directly mapped at document purpose; leaf mappings are conditional | NuDoc can use compressed content and has separate SSKU/group ownership. |
| Price, quantity, and remnant rules | Item commercial fields and seller-price objects | `ItemQtyPrice` | Directly mapped at document purpose; leaf mappings are conditional | ULP presentation can nest amount/currency and aggregate listing/item context. |
| Compatibility | Listing/item compatibility fields | `ItemCompatibility`; draft compatibility families | Family correspondence | Compatibility is optional and may be excluded from a default cache read until selected. |
| Seller policies and terms | Listing and item term/policy objects | Item or group business-policy documents; root term fields | Family correspondence | ULP can restrict fields; API terms are not a buyer-specific outcome. |
| Details, high-precision prices, and seller documents | Specialized listing/item fields when exposed | `ItemDetails` | Family correspondence | The ULP contract does not prove that every optional NuDoc detail is exposed. |
| Locks and reservations | No normal current-listing field established | `ItemLock` | NuDoc-only | Reservation lifecycle is operational and may affect available quantity without being a listing attribute. |
| UUID lookup | No normal current-listing field established | `UuidMap` | NuDoc-only | Lookup key and application association are operational indexes. |

!!! note "Current state is not a transaction"
    Price and available quantity can change outside a seller revision. ULP and
    its provider content may be cached and eventually consistent. For
    checkout, buyer eligibility, payment, delivery, or settlement, use the
    appropriate owning service rather than treating a listing read as the
    decision.

### Listing-event migration

ULP listing events identify a state change, not a full listing snapshot.
Consumers should retrieve the current fields they need after receiving an
event.

| ULP BES2 event | Meaning |
| --- | --- |
| `ULP.LISTING.NEW` | A listing was newly created for the corresponding ULP use case. |
| `ULP.LISTING.UPDATED` | Listing state changed. |
| `ULP.LISTING.ENDED` | The listing entered an ended state; this does not establish a sale or settlement outcome. |
| `ULP.LISTING.HOLDSTATUS.UPDATED` | Hold state changed; interpret detailed hold data only when authorized and available. |
| `ULP.LISTING.CATEGORY.UPDATED` | Listing category state changed. |

Legacy BES1 item creation, revision, extension, closure, sale,
scheduled-to-active, category, hold-status, and draft events are not
payload-compatible with these ULP BES2 events even when they represent the
same use case. A migration therefore needs deduplication and loss-avoidance
logic rather than one-to-one field substitution. NuData CDC is described as
an in-progress alternative for consumers whose need is change capture rather
than one of the ULP event families; its delivery semantics must be confirmed
with the owning platform.

## 2. Post-listing data and providers

### Why provider data is separate

Post-listing data is supplied, derived, or computed by a domain after core
listing state exists. It can be updated by domain events or asynchronous jobs,
and it does not necessarily share the seller mutation lifecycle or CLS
storage.

Examples visible in the schema include derived listing attributes, visibility
and searchability, deal state, inventory and shipping-program information,
product tagging, regulatory enrichment, SEO image metadata, engagement, and
purchase-view metrics. `dalasEvaluation`, for example, is documented as
asynchronous plugin output triggered by backend events; it should not be
treated as seller-written core state.

### Post-listing data families and freshness

The provider schemas complement the following wider post-listing categories.
They are business groupings, not a physical-table mapping or a guarantee that
every field is available to every client.

| Data family | Contract examples | Consumer boundary |
| --- | --- | --- |
| Derived attributes and product enrichment | `dalasEvaluation`, `autoTagProduct`, dynamic aspects, and calculated compatibility. | Derived state can be absent or change without a seller revision. |
| Policy, trust, and regulatory state | Hold policies/details, regulatory content, country of origin, and energy-efficiency information. | A returned value does not alone make the final policy decision for every buyer or marketplace. |
| Search and visibility | `listingSearchabilityInfo`, `visibilitySummary`, search suppression, and visibility flags. | Search can have recovery behavior beyond a default-visible-site value; do not reduce this data to universal availability. |
| Commercial and engagement | Promotion state, purchase view, watch count, auction outcome, and deal data. | Observed or derived commercial state is not payment, checkout, fulfillment, or settlement data. |
| Inventory and fulfillment enrichment | Warehouse locations, shipping-program eligibility, and seller-inventory flags. | Mutable availability and fulfillment inputs can change outside a seller's listing revision. |

ULP reads and provider state can be cached and eventually consistent. A
missing field can mean an unavailable or disabled provider, authorization or
gateway exclusion, asynchronous calculation, cache state, connection failure,
or an actual empty value. Inspect field-specific GraphQL errors and the
provider contract rather than treating absence as a general data-loss signal.

### Field-group retrieval model

ULP uses named field groups as an internal loading and cache boundary. A field
group is not a public GraphQL type and is not proof that all of its fields have
one physical store.

```text
Requested ULP field path
  -> generated field-to-group mapping
  -> group-to-subgraph mapping
  -> enabled-provider check
  -> generated FGQL query section guarded by @include
  -> group-level cached response / current provider response
```

The ULP implementation applies the following rules:

1. `FieldOnDemandFieldGroupLookup` loads generated field-to-group,
   group-to-subgraph, and group-classification JSON files. If an exact field
   path is not found, it walks upward through parent paths to find a group.
2. At lookup construction, `unilistingcfg.defaultFieldGroup` classifies a
   declared group as default; otherwise ULP treats it as on-demand. The
   checked-in query-template refresh listener does not rebuild those lookup
   sets, so a changed value is not by itself evidence of an immediate
   reclassification in a running process.
3. `ListingGraphQLQueryBuilder` enables a group only when its mapped provider
   has `queryEnabled=true` in external configuration. Default groups are
   requested whenever enabled; on-demand groups require both enablement and
   selection.
4. `MonstorFieldMapper` converts selected API paths to cache paths, requests
   an entire provider-group container rather than an independently cached
   provider leaf, and adds the minimum listing identity/lifecycle/seller
   context needed for the response.
5. Provider-event handling requires a listing ID and application-name header,
   maps the application name through external configuration, and refreshes
   that singleton provider group for the listing. The provider-consumer dedupe
   key is listing ID + application name + event type. Exhausted retries create
   a DLQ record. The source does not establish every production
   event-producer mapping, tenant/caller cache isolation, or delivery
   guarantee.

The schema-level `@onDemand` directive is useful snapshot metadata, but it
does not on its own prove default/on-demand behavior in a deployment.
Similarly, `@excludeGroupsInQuery` describes exclusions, while the inspected
ULP code consumes generated templates and lookup files rather than the
directive abstract syntax tree.

### Snapshot scope and runtime enablement

The local schema snapshot declares 16 `@onDemand` field groups. The generated
ULP lookup files map 24 service groups: 15 classified as `onDemand` and nine
as `default`. `CONNECTEDPRODUCTSULP` is the difference: it is annotated
on-demand in the schema but has no local generated field-to-group or
group-to-service mapping. Therefore, 25 distinct provider-group identities
are visible across these committed schema and mapping artifacts. The linked
source set currently contains a corresponding repository for all 25. The
schema also names 24 field groups in `@excludeGroupsInQuery`, while the FGQL
supergraph snapshot contains 233 Federation subgraphs. These are
schema-snapshot inventories, not production provider counts.

Provider query inclusion depends on external configuration:
`unilistingcfg.provider.<group>.queryEnabled` determines whether a mapped
group is requested, and the lookup's construction-time
`unilistingcfg.defaultFieldGroup` determines its default/on-demand set.
Confirm a provider's deployment status from the active configuration and
generated environment-specific query template, not from a schema declaration
alone.

### Declared provider-group catalog

The local ULP schema declares the following 16 on-demand groups. All 16 have
a corresponding linked provider repository under `.link/ulp_providers`, and
this catalog and the detailed analyses cover those on-demand providers. It
reconciles the generated production selection with provider-local core logic
and distinguishes an observed source path from deployment-time enablement,
which remains external configuration.

| Declared group | Mapped service | Returned data family | Provider core logic | Provider data source and update behavior | ULP contract status |
| --- | --- | --- | --- | --- | --- |
| `PURCHASEVIEWGRAPHSVC` | `purchaseviewgraphsvc` | Last purchase time, unique buyer count, and last-purchase amounts/currencies. | Runs only tasks for selected fields: count unique buyers and find the latest qualifying purchase. | Request-time COMS aggregation with a 90-day default lookback; no provider cache. | Production selection present; see [analysis](#purchaseviewgraphsvc). |
| `EBAYPLUSELIGIBILITY` | `ebaypluseligibility` | eBay Plus shipping-program eligibility in fulfillment terms. | Batches `FulfillmentTerms` and maps a precomputed eligibility flag. | NuKV listing-eligibility entity with no configured TTL; evaluation writes can synchronously refresh ULP. | Production selection present; see [analysis](#ebaypluseligibilitysvc). |
| `LCLISTINGPROVIDER` | `lclistingprovider` | eBay Live buy-spot eligibility, intent, purchasability, visibility, and live-event state. | Batches listings, reads `EbayLive`, selects the first live event as primary, and normalizes time values. | NuKV cache read with up to four attempts; primary-event data is documented as eventually consistent. | Production selection present; see [analysis](#lc-listingprovider). |
| `BASICLISTINGDATA` | `basiclistingdata` | Listing/item watch counts and certified-expert-insight asset/classification. | Validates and merges app-owned listing/item JSON; federation reads return the stored projection. | Provider-owned NuData/Monstor; changed writes emit `ITEM_REVISED`; refresh send failures are logged. | Production selection present; see [analysis](#basiclistingdata). |
| `ITMVZBLIT` | `itmvzblit` | Default-visible sites, explicitly suppressed sites, and packed visibility. | Batches visibility reads, merges NuData and SaleBo, then checks discrepancies before mapping. | Caty remains source of truth during dual-write; eventual NuData reads; changed visibility can emit refresh. | Production selection present; see [analysis](#itemvisibility-itmvzblit). |
| `SAPSVC` | `sapsvc` | Auto-tagged product ID and dynamic annotated search aspects. | Converts Monstor classifier/annotator results into a product reference and deduplicated aspects. | SAP classifier data through Monstor; aspect configuration refreshes dynamically; no local TTL or event publisher found. | Production selection present; see [analysis](#sapsvc). |
| `CMPLREGULATORYSVC` | `cmplregulatorysvc` | Country of origin and confidence score. | Selects cache, vendor, seller-cleared, vector-search, or non-production mock COO paths. | `CountryOfOrigin` NuDoc plus vendor/vector inputs; COO clearing emits `ITEM_REVISED`; cache entries expire after three days. | Production selection present; see [analysis](#cmplregulatorysvc). |
| `SEOCORELABSVC` | `seocorelabsvc` | Listing/item image alt text, image URLs, and image order. | Maps each photo image GUID to optional cached alt text; preserves original photos when lookup fails. | NuKV SEO cache; protected refresh endpoint can emit `ITEM_REVISED` after an upstream write. | Production selection present; see [analysis](#seocorelabsvc). |
| `DEFAULTULPPROVIDER` | `defaultulpprovider` | No production `ListingV2` selection is present; local mappings show only type-level/test-oriented fields. | Static illustrative query resolver; no listing entity logic. | No provider data store, cache, or event flow is implemented. | Scaffold/example provider; see [analysis](#defaultulpprovider). |
| `DEALSGRAPH` | `dealsgraph` | Daily-deal state, timing, item quantity, permanence, purchase restrictions, and deal flag. | Batches listing IDs and chooses a NuDoc fetcher or fake fetcher from refreshable configuration. | `DealsULP` NuDoc `__ROOT__`; not-found means not a daily deal; no local TTL or event publisher found. | Production selection present; see [analysis](#dealsgraph). |
| `SELLERPORTALSVC` | `sellerportalsvc` | Consigned, hub-fulfilled, and pre-authenticated inventory-storage flags. | Batches listing/SKU lookups to item-group data and maps inventory-storage metadata. | Provider DAO plus inventory/catalog clients; ULP refresh supports sync/async retry after provider writes. | Production selection present; see [analysis](#sellerportalsvc). |
| `CONNECTEDPRODUCTSULP` | Not mapped locally | No field-to-group mapping, group-to-service mapping, or production selection is present. | Batches item/listing lookups and maps persisted connected-product modules to `Item.connectedProduct`. | Provider-owned NuDocument; REST changes synchronously emit `ITEM_REVISED`. | Provider source exposes a real field, but the generated ULP mapping is absent; see [analysis](#connectedproductsulp). |
| `MPLS` | `mpls` | Global Shipping Program eligibility, dimensions/weight sources, domestic-leg data, tariffs, restrictions, and estimator metadata. | Strongly reads listing data and normalizes GSP fields, costs, and country codes for GraphQL. | `GlobalShippingProgram` Monstor/NuData records; no provider-local cache, TTL, or event publisher found. | Production selection present; see [analysis](#marketplace-logistic-service-mpls). |
| `SLRINVSVC` | `slrinvsvc` | Seller-inventory ship-to-home availability and search-hiding flag. | Groups requests by seller, reads SKU status, decodes flags, and merges duplicate results. | Read-through `SKUStatusDAO`; write paths may send feature-gated, fire-and-forget `ITEM_REVISED` refreshes. | Production selection present; see [analysis](#slrinvsvc). |
| `LOCNMAPPINGSVC` | `locnmappingsvc` | Inventory warehouse merchant-location keys. | Uses seller + listing + normalized SKU to read locations and map merchant-location keys. | `ListingLocations` NuData; REST writes/deletes retry, publish BES updates, and optionally refresh ULP. | Production selection present; see [analysis](#locnmappingsvc). |
| `SELLERRISKENTITYSVC` | `sellerriskentitysvc` | Searchability timestamps/reason and risk-hold timing, usage, and log values. | Maps `DelayedItem` index and delay fields into the risk/searchability GraphQL projection. | `DELAYED_ITEM_KEYSPACE` NuDocument; REST upserts emit `ITEM_REVISED` refresh events. | Production selection present; see [analysis](#sellerriskentitysvc). |

Fourteen declared groups have a local generated production-query path.
`DEFAULTULPPROVIDER` and `CONNECTEDPRODUCTSULP` are discrepancies between
schema declarations and locally generated artifacts. They are **not** evidence
that a provider is disabled, unavailable, or stale in every deployment.

### Additional mapped default/direct provider groups

Nine further groups are mapped by ULP as `default`. When enabled, ULP requests
a default group without an on-demand field-group selection. All nine have a
corresponding repository under `.link/ulp_providers`. The sections below add
their provider-owned output schemas and source-backed implementation analyses.

| ULP group/subgraph label | ULP data scope | Example mapped data | Source-analysis status |
| --- | --- | --- | --- |
| `svls` | Broad core-listing contract. | Aspect images, auto-relist terms, and best-offer settings. | Default baseline group; no dedicated generated `@include` selection. See [analysis](#svls). |
| `itemcompatibilitysvc` | Vehicle/item compatibility. | Listing and item compatibility, including computed compatibility by marketplace. | Generated selection present; see [analysis](#itemcompatibilitysvc). |
| `vehentsvc` | Vehicle-listing enrichment. | Vehicle details and vehicle-history-report content. | Generated selection present; see [analysis](#vehentsvc). |
| `pickupeligibility` | Pickup and fulfillment eligibility. | Pickup eligibility, in-store-pickup logistics, and package specifications. | Generated selection present; see [analysis](#pickupeligibility). |
| `egdsellermgmt` | eBay Guaranteed Delivery eligibility. | Shipping-program eligibility under fulfillment and listing terms. | Generated selection present; see [analysis](#egdsellermgmt). |
| `mdmlusvcio` | Markdown-promotion data. | Markdown discount duration and promotion start/end dates. | Generated selection present; see [analysis](#mdmlusvcio). |
| `dalasproxysourcesvc` | DALAS source evaluation. | Source-evaluation metadata and source entity containers. | Generated selection present; see [analysis](#dalasproxysourcesvc). |
| `dalasproxysinksvc` | DALAS sink evaluation. | Sink entity containers and DALAS storage manifests. | Generated selection present; see [analysis](#dalasproxysinksvc). |
| `dalasuuidprovidersvc` | DALAS identity data. | Fresh `dalasUuid` generated during federation resolution. | Generated selection present; see [analysis](#dalasuuidprovidersvc). |

### Provider storage and lifecycle catalog

This catalog records the provider-local backend boundary that the checked-out
code establishes. A named NuData, Monstor, or NuKV store is not automatically
the enterprise-wide source of truth; an external provider's backing database,
runtime configuration, and event delivery remain unverified unless stated in
the detailed analysis.

| Provider group | Provider-local storage or resolution source | Storage / resolution grain | Write and ULP-refresh boundary |
| --- | --- | --- | --- |
| `BASICLISTINGDATA` | NuData/Monstor `BasicListingData`, `__ROOT__`. | Listing ID root; contained item data is keyed by item ID. | Revision-aware listing and counter writes emit asynchronous `ITEM_REVISED`; send failures are logged without a local retry. |
| `CMPLREGULATORYSVC` | NuDocument `CountryOfOrigin`; external vendor/vector paths exist outside federated reads. | Base64 of `identifierType|identifierValue`; audit records use `audit`, vector search uses `__ROOT__`. | COO cache changes and seller clearing can emit refresh. The three-day expiry applies to soft-deleted records, not all active COO data. |
| `CONNECTEDPRODUCTSULP` | NuDocument/Monstor `ConnectedProductsULPData`, `__ROOT__`. | Item ID root; listing ID supplies federation and refresh context. | Changed REST module writes/deletes synchronously emit `ITEM_REVISED` only when `shouldPublishToULP` is enabled. |
| `DEALSGRAPH` | Read-only NuDocument/Monstor `DealsULP`, `__ROOT__`, or configured fake fetcher. | Numeric listing ID. | No provider write, event, cache, TTL, or read-retry path is established. |
| `DEFAULTULPPROVIDER` | Static example resolver. | No listing or item identity. | No persistence, event, cache, or refresh implementation. |
| `EBAYPLUSELIGIBILITY` | NuKV `ebaypluslistingeligibilitynukvhost`. | Decimal listing ID. | Evaluation writes upsert the entity and send `ITEM_REVISED` up to three times; refresh-send failures are logged. |
| `ITMVZBLIT` | NuData/Monstor `LvfVisibilityStorage`, `__ROOT__`, alongside SaleBo/Caty during migration. | Decimal item/listing ID. | Visibility writes can asynchronously refresh ULP; Caty remains the code-documented source of truth during this dual-write path. |
| `LCLISTINGPROVIDER` | NuKV `cplivecommercenukvhost` cache holding `EbayLive` JSON. | `i:<listingId>`. | No local writer, refresh publisher, invalidator, or entry TTL is established; reads retry at most four times with 100 ms waits. |
| `LOCNMAPPINGSVC` | NuData `ListingLocations`, `__ROOT__`. | Concatenated seller ID, listing ID, and normalized SKU. | REST upsert/delete retries NuData up to five times, emits BES, and can emit default-disabled, fire-and-forget ULP refresh. |
| `MPLS` | Monstor/NuData `GlobalShippingProgram`. | `KeyFactory(listingId)`. | GraphQL has no local write, event, TTL, or cache path; strong reads allow Monstor retry, whose policy is unproven here. |
| `PURCHASEVIEWGRAPHSVC` | Request-time COMS aggregation. | Listing ID and seller ID. | No provider persistence, refresh publisher, or cache for `listingPurchaseView`; its default lookback is 90 days. |
| `SAPSVC` | External Monstor bulk endpoint with `SAP_INTERNAL` key type. | Normalized item ID. | No provider-local storage, write, event, TTL, or retry path; dynamic-aspect configuration is refreshable. |
| `SELLERPORTALSVC` | Provider `ItemGroupDataObject` DAO; physical store is unproven. | Listing ID and SKU. | Listing workflows update provider records and refresh ULP: synchronous sends have three total attempts; async sends have an initial attempt plus up to three retries. |
| `SELLERRISKENTITYSVC` | NuDocument/Monstor `DelayedItem`, `__ROOT__`. | Listing ID. | REST upsert asynchronously emits `ITEM_REVISED`; no local retry, TTL, or cache is established. |
| `SEOCORELABSVC` | NuKV `seocorelabcachenukvhost` cache. | Listing ID, including parent listing ID for `Item`. | No local cache writer; a protected endpoint only emits feature-gated refresh and has no retry. |
| `SLRINVSVC` | `SKUStatusDAO` / `SKUStatus` DAL entity; physical database is unproven. | Seller legacy user ID and listing ID. | Inventory write paths can send default-disabled, asynchronous `ITEM_REVISED`; callback failures are logged without retry. |
| `SVLS` | Authenticated CLS HTTP read. | Listing ID; a separate item path is also available. | No provider-local store, ULP refresh publisher, or DataLoader cache; the CLS client config sets `maxRetryCount=2`. |
| `ITEMCOMPATIBILITYSVC` | NuData/Monstor `ItemCompatibility`; history uses separately configured `FPAListingHistory`. | Item/listing ID with marketplace-specific rows. | Refresh/mutation paths can persist Fitment-derived data and emit `ITEM.REVISED` or backfill; broker retry is runtime-configured and disabled in checked-in configuration. |
| `VEHENTSVC` | NuData `MotorsVehicleHistoryReports` and `MotorsPartnerData`, with CATY fallback for history. | History key is `vin + sellerId + siteId + attrId`; verification uses listing ID. | Vehicle writes can refresh ULP; verification records have a 90-day TTL. Callback delivery failures are logged. |
| `PICKUPELIGIBILITY` | Request-time ULOS seller-offer state and legacy listing conversion; optional `PickupEligibility` NuDocument comparison. | Listing context plus seller/program-commitment identity. | Event-driven flows can refresh ULP; a separate commitment cache has a 3,600-second lifetime but is not proven to serve the GraphQL evaluation path. |
| `EGDSELLERMGMT` | Monstor/NuData `EbayGuaranteedDelivery`, `__ROOT__`. | Listing ID. | REST create/update/delete changes synchronously refresh ULP; store calls use strong consistency with client retry enabled and a 5,000 ms configured timeout. |
| `MDMLUSVCIO` | NuKV `ItemSellerDiscount`; selected MSKU recovery reads SaleBo and SME markdown data. | Listing ID, including for variation items. | Backfill can write NuKV; succeeded markdown/markup changes can synchronously refresh ULP when the default-disabled flag is enabled. |
| `DALASPROXYSOURCESVC` | Request-time external `POST /dalas/v3/plugin-orchestrations/{listingId}`. | Listing ID and external `dalasUuid`. | No local persistence, event, cache, or retry loop; null-status and 5xx failures are classified retryable. |
| `DALASPROXYSINKSVC` | Request-time external `POST /dalas/v3/immutable-append/{listingId}`. | Listing ID, source container, base GUID, and external UUID. | No local persistence, event, cache, or retry loop; null-status and 5xx failures are classified retryable. |
| `DALASUUIDPROVIDERSVC` | Locally generated `GuidGenerator` value. | Federation listing ID is validated but not used to generate the GUID. | No database, external source, cache, event, or retry path; values are not stable across separate resolutions. |

The detailed provider analyses below contain output-schema facts and the
source artifacts supporting this catalog. Their storage statements are scoped
to the checked-out implementation and do not replace an owning service's
operational database or event contract.

### Provider output schemas

This reference lists fields **resolved by each provider**. Federation keys and
`@external` fields are prerequisites supplied by another subgraph, so they are
not repeated as provider data. Where a provider adds the same field to
`ListingV2`, `SingleSkuListing`, and `VariationListing`, one path represents
all three types. Input and mutation schemas are intentionally excluded.

#### BASICLISTINGDATA

| Provider output field | Type | Description |
| --- | --- | --- |
| `[ListingV2, SingleSkuListing, VariationListing].watchCount` | `Int` | Watch count for the listing. |
| `Item.watchCount` | `Int` | Watch count for the item. |
| `Item.certifiedExpertInsight` | `CertifiedExpertInsight` | Certified-expert-insight data associated with the item. |
| `Item.certifiedExpertInsight.certifiedExpertInsightClassification` | `String!` | Classification of the certified-expert asset data, represented as an enum string of up to 20 characters. |
| `Item.certifiedExpertInsight.certifiedExpertInsightAssetId` | `ID!` | Identifier of certified-expert data defined by the official data provider. |

The provider schema has no listing-data query root. `watchCount` has no
provider-output authorization or deprecation directive in the checked-in
schema.

#### CMPLREGULATORYSVC

`itemCountryOfOrigin` is excluded from `publicapi` and `sandbox`; its
single-SKU and variation implementations require core seller-product,
aspect, and marketplace data. The energy-efficiency containers are
public-tagged in this provider schema, but the checked-out ULP mappings do not
establish them as `CMPLREGULATORYSVC` current-listing group output.

| Provider output field | Type | Description |
| --- | --- | --- |
| `[ListingV2, SingleSkuListing, VariationListing].itemCountryOfOrigin` | `ItemCountryOfOrigin` | Standardized country-of-origin information used for regulatory compliance, customs processing, and buyer transparency. |
| `itemCountryOfOrigin.countryOfOrigin` | `CountryCode` | Country where the product was manufactured or produced. |
| `itemCountryOfOrigin.confidenceScore` | `Float` | Confidence in the country-of-origin result. |
| `[ListingV2, SingleSkuListing, VariationListing].energyEfficiencyInfo` | `EnergyEfficiencyInfo` | Seller- or vendor-provided energy-efficiency information for the listing. |
| `[ListingV2, SingleSkuListing, VariationListing].energyEfficiencyCombinedInfo` | `EnergyEfficiencyCombinedInfo` | Aggregated seller and vendor/external energy-efficiency information for the listing. |
| `[ListingV2, SingleSkuListing, VariationListing].energyEfficiencyCombinedInfo.sellerEnergyEfficiencyInfo` | `SellerEnergyEfficiencyInfo` | Seller-provided energy-efficiency subset; null when seller data is unavailable. |
| `SellerEnergyEfficiencyInfo.listing.listingId` | `ID!` | Identifier of the listing associated with the seller-provided energy-efficiency data. |
| `SellerEnergyEfficiencyInfo.documents` | `[EnergyEfficiencyDocument!]!` | Seller-provided energy labels or product-fiche documents; empty when absent. |
| `SellerEnergyEfficiencyInfo.energyClassRange` | `String` | Energy-class range, such as `A_G`. |
| `SellerEnergyEfficiencyInfo.energyClass` | `String` | Energy-efficiency class, such as `A`, `B`, or `C`. |
| `SellerEnergyEfficiencyInfo.dataCompleteness` | `DataCompleteness!` | Completeness of seller data: `COMPLETE`, `PARTIAL`, or `NONE`. |
| `[ListingV2, SingleSkuListing, VariationListing].energyEfficiencyCombinedInfo.vendorEnergyEfficiencyInfo` | `EnergyEfficiencyInfo` | Vendor/external energy-efficiency information, such as EPREL data; null when unavailable. |
| `EnergyEfficiencyInfo.id` | `ID!` | Unique energy-efficiency product-model identifier, such as an EPREL or seller identifier. |
| `EnergyEfficiencyInfo.source` | `EEKDataSource!` | Source of energy-efficiency data: seller or external EPREL vendor. |
| `EnergyEfficiencyInfo.documents` | `[EnergyEfficiencyDocument!]!` | Energy-label and product-fiche documents; empty when no source documents exist. |
| `EnergyEfficiencyInfo.modelIdentifier` | `String` | Product model identifier, such as an MPN. |
| `EnergyEfficiencyInfo.supplierOrTrademark` | `String` | Product brand or supplier trademark. |
| `EnergyEfficiencyInfo.productGroup` | `String` | Product group, such as tyres or washing machines. |
| `EnergyEfficiencyInfo.registrantNature` | `String` | Supplier's registered role: manufacturer, importer, or authorized representative. |
| `EnergyEfficiencyInfo.category` | `String` | Product category, such as monitor. |
| `EnergyEfficiencyInfo.energyClassRange` | `String` | Energy-class range. |
| `EnergyEfficiencyInfo.energyClass` | `String` | Energy-efficiency class. |
| `EnergyEfficiencyInfo.energyClassImageName` | `String` | Energy-class arrow image name. |
| `EnergyEfficiencyInfo.iceTyre` | `Boolean` | Whether a tyre can be used in severe ice conditions; null when not applicable. |
| `EnergyEfficiencyInfo.tyreDesignation` | `String` | Tyre designation; null when not applicable. |
| `EnergyEfficiencyInfo.wetGripClass` | `String` | Tyre wet-grip class; null when not applicable. |
| `EnergyEfficiencyInfo.tyreClass` | `String` | Tyre class; null when not applicable. |
| `EnergyEfficiencyInfo.sizeDesignation` | `String` | Tyre size designation; null when not applicable. |
| `EnergyEfficiencyInfo.eprelRegistrationNumber` | `String` | EPREL registration number. |
| `EnergyEfficiencyInfo.severeSnowTyre` | `Boolean` | Whether a tyre has severe-snow grip; null when not applicable. |
| `EnergyEfficiencyInfo.externalRollingNoiseValue` | `String` | External rolling-noise level in decibels. |
| `EnergyEfficiencyInfo.externalRollingNoiseClass` | `String` | Rolling-noise class rating, such as `A`, `B`, or `C`. |
| `EnergyEfficiencyInfo.dateStartProductionYear` | `String` | Production start year. |
| `EnergyEfficiencyInfo.dateStartProductionWeek` | `String` | Production start week. |
| `EnergyEfficiencyInfo.dateEndProductionYear` | `String` | Production end year. |
| `EnergyEfficiencyInfo.dateEndProductionWeek` | `String` | Production end week. |
| `EnergyEfficiencyDocument.type` | `EEKDocumentType!` | Document kind: energy label, product fiche, or energy class. |
| `EnergyEfficiencyDocument.values` | `[EEKDocument!]!` | Document instances of the declared type. |
| `EEKDocument.url` | `String!` | URL of the document or image. |
| `EEKDocument.guid` | `String` | Document or image identifier. |
| `EEKDocument.format` | `EEKDocumentFormat` | Document format, such as PDF, PNG, or JPG. |
| `EEKDocument.language` | `EEKDocumentLanguage` | Document language. |

The provider also exposes a direct `itemCountryOfOrigin` query whose output
has the same `countryOfOrigin` and `confidenceScore` fields. Its input schema
is not included here.

#### CONNECTEDPRODUCTSULP

`Item.connectedProduct` requires the parent listing ID and is inaccessible to
`publicapi`.

| Provider output field | Type | Description |
| --- | --- | --- |
| `Item.connectedProduct` | `ConnectedProduct` | Connected-product data for the item; null when no data is available. |
| `Item.connectedProduct.provider` | `ConnectedProductProvider` | Source or authority of the digital product representation. |
| `Item.connectedProduct.provider.name` | `String!` | Provider name. |
| `Item.connectedProduct.provider.assetId` | `String!` | Digital asset identifier. |
| `Item.connectedProduct.warranty` | `ConnectedProductWarranty` | Warranty data associated with the connected product. |
| `Item.connectedProduct.warranty.activationDateTime` | `DateTime!` | Warranty activation timestamp. |
| `Item.connectedProduct.warranty.expirationDateTime` | `DateTime` | Warranty expiration timestamp; null when unknown. |
| `Item.connectedProduct.digitalAuthenticity` | `DigitalAuthenticity` | Authenticity-verification information. |
| `Item.connectedProduct.digitalAuthenticity.authenticityStatus` | `String!` | Authenticity verdict. |
| `Item.connectedProduct.digitalAuthenticity.imageUrl` | `String!` | URL of the authenticated QR image. |

#### DEALSGRAPH

`dealDetails` is inaccessible to `publicapi` and sandbox. It is null when a
listing is not a deal; the required `isDailyDeal` leaf is `false` for
inactive or expired deals.

| Provider output field | Type | Description |
| --- | --- | --- |
| `[ListingV2, SingleSkuListing, VariationListing].dealDetails` | `ListingDailyDealDetails` | Daily-deal information for the listing. |
| `dealDetails.isDailyDeal` | `Boolean!` | Whether the listing is an active daily deal. |
| `dealDetails.isDailyDealPermanent` | `Boolean` | Whether the deal was created as permanent; null when not a deal. |
| `dealDetails.isQuantityRestrictedToBuy` | `Boolean` | Whether purchase quantity is restricted per buyer; null when not a deal. |
| `dealDetails.dailyDealsItemQuantity` | `Int` | Quantity available per buyer; `0` means no restriction and null means not applicable. |
| `dealDetails.dealStartDateTime` | `DateTime` | Deal start time; null when not a deal. |
| `dealDetails.dealEndDateTime` | `DateTime` | Deal end time; null when not a deal. |
| `Query.dealDetailsByListingId[].listing.listingId` | `ID!` | Listing identifier for a direct multi-listing deal lookup. |
| `Query.dealDetailsByListingId[].dealDetails` | `ListingDailyDealDetails` | Daily-deal details for that listing. |

#### DEFAULTULPPROVIDER

This scaffold does not extend a listing entity. Its only output is the
gateway-excluded `Query.defaultUlpProvider`; it is not a listing-data
contract.

| Provider output field | Type | Description |
| --- | --- | --- |
| `Query.defaultUlpProvider.id` | `ID!` | Identifier of the illustrative default-provider output. |
| `Query.defaultUlpProvider.description` | `String` | Illustrative description field. |
| `Query.defaultUlpProvider.otherGroupField` | `String` | Example alternative field-group value. |
| `Query.defaultUlpProvider.stagingTestField` | `String` | Test-only field available in staging. |
| `Query.defaultUlpProvider.featureTestField` | `String` | Test-only field available in feature. |
| `Query.defaultUlpProvider.prodAndPreprodTestField` | `String` | Test-only field available in production and preproduction. |

#### EBAYPLUSELIGIBILITY

The provider extends `FulfillmentTerms`, rather than a listing or item entity.
The nested eligibility field is inaccessible to `publicapi`.

| Provider output field | Type | Description |
| --- | --- | --- |
| `FulfillmentTerms.shippingProgramEligibility` | `ShippingProgramEligibility` | eBay Plus shipping-program eligibility for the listing. |
| `FulfillmentTerms.shippingProgramEligibility.ebayPlus` | `Boolean` | `true` when eligible for eBay Plus, `false` when ineligible, and null when unavailable or not applicable. |

#### ITMVZBLIT

Visibility data is inaccessible to `publicapi`. `visibilitySummary` can be
null while calculation is incomplete; `visibility` is non-null.

| Provider output field | Type | Description |
| --- | --- | --- |
| `[ListingV2, SingleSkuListing, VariationListing].visibilitySummary` | `ListingVisibilitySummary` | All-sites listing-visibility result. |
| `visibilitySummary.packedVisibilityString` | `String!` | Internal comma-separated `<site-id>=<bit-mask>` representation for Search and Recommendation backends. |
| `visibilitySummary.explicitlySuppressedSites` | `[Int!]!` | Sites explicitly blocked by systems such as GCX, eBay Live, VeRO, or regulatory controls. |
| `visibilitySummary.defaultVisibleSites` | `[Int!]!` | Sites where default listing visibility is enabled; recovery flows can still use packed bits. |
| `[ListingV2, SingleSkuListing, VariationListing].visibility` | `ListingVisibility!` | Current-site listing-visibility result. |
| `visibility.hasNativeBlock` | `Boolean!` | Whether the listing should be blocked in a native app. |

#### LCLISTINGPROVIDER

All eBay Live fields are inaccessible to `publicapi`. The provider supports
single-SKU and variation listing entities, not `Item`.

| Provider output field | Type | Description |
| --- | --- | --- |
| `[ListingV2, SingleSkuListing, VariationListing].ebayLive` | `EbayLive` | Properties specific to listings associated with eBay Live events. |
| `ebayLive.liveEvents` | `[LiveEvent]!` | All associated events ordered by priority; the first is the next/current event, or most recently ended event. |
| `ebayLive.liveEvents[].id` | `ID!` | Unique event identifier used to associate the listing with an eBay Live event. |
| `ebayLive.primaryEvent` | `LiveEventSnapshot` | Next/current event, or most recently ended event; null when no event is published and sourced from an eventually consistent cache. |
| `ebayLive.primaryEvent.id` | `ID!` | Unique eBay Live event identifier. |
| `ebayLive.primaryEvent.state` | `LiveEventState!` | Event state: `UPCOMING`, `RECORDED`, or `LIVE`. |
| `ebayLive.primaryEvent.startTime` | `DateTime!` | Event start time. |
| `ebayLive.intent` | `LiveListingIntent` | Seller-defined Core/Live listing strategy. |
| `ebayLive.purchasable` | `Boolean!` | Whether the listing is purchasable; interpretation depends on listing intent. |
| `ebayLive.visible` | `Boolean!` | Whether the listing is discoverable or visible; interpretation depends on listing intent. |
| `ebayLive.buyspotEligible` | `Boolean` | Whether View Item should show the Buy More Spot button; optional for backward compatibility. |

#### LOCNMAPPINGSVC

`Item.inventoryLocations` requires the item's SKU, listing ID, and seller ID,
and is inaccessible to `publicapi`.

| Provider output field | Type | Description |
| --- | --- | --- |
| `Item.inventoryLocations` | `ItemInventoryLocationDetails` | Warehouse-location details for the item/SKU; its array is empty when no location exists. |
| `Item.inventoryLocations.warehouseLocations` | `[ItemWarehouseLocationDetails!]!` | Warehouse-location entries for the item/SKU. |
| `Item.inventoryLocations.warehouseLocations[].merchantLocationKey` | `String!` | Merchant or warehouse location key. |

#### MPLS

MPLS extends `FulfillmentTerms`; all of the following
shipping-program-eligibility fields are inaccessible to `publicapi`.

| Provider output field | Type | Description |
| --- | --- | --- |
| `FulfillmentTerms.shippingProgramEligibility.globalShippingProgram` | `GlobalShippingProgramEligibility` | Consolidated Global Shipping Program eligibility; UK-only and null for non-UK listings. |
| `globalShippingProgram.eligible` | `Boolean!` | Whether the listing is eligible for the Global Shipping Program. |
| `globalShippingProgram.estimatedWeight` | `Float` | Weight used to calculate eligibility. |
| `globalShippingProgram.estimatedWeightSource` | `String` | Source of the estimated weight. |
| `globalShippingProgram.itemAttributeEstimatorVersion` | `Int` | Partner estimator model version. |
| `globalShippingProgram.harmonizedSystemCode` | `String` | Harmonized System code used for eligibility. |
| `globalShippingProgram.harmonizedSystemCodeSource` | `String` | Source of the Harmonized System code. |
| `globalShippingProgram.itemEstimatorModelMode` | `String` | Partner estimator tracking metadata. |
| `globalShippingProgram.itemEstimatorDataVersion` | `Int` | Partner estimator data-set version. |
| `globalShippingProgram.dimensionSource` | `String` | Source of the item dimensions. |
| `globalShippingProgram.domesticShippingServiceId` | `String` | UK domestic shipping-service code. |
| `globalShippingProgram.domesticLegCost` | `Amount` | Domestic-leg shipping cost. |
| `globalShippingProgram.domesticLegCost.value` | `Decimal!` | Monetary amount of the domestic-leg cost. |
| `globalShippingProgram.domesticLegCost.currency` | `CurrencyAlpha3Code` | Currency of the domestic-leg cost. |
| `globalShippingProgram.partnerRestrictedCountries` | `[CountryAlpha2Code!]` | Destination countries restricted by the partner. |
| `globalShippingProgram.partnerHubPostalCode` | `String` | Postal code of the partner hub. |

#### PURCHASEVIEWGRAPHSVC

Purchase View is excluded from `publicapi`; its concrete listing fields
require the seller's legacy user ID.

| Provider output field | Type | Description |
| --- | --- | --- |
| `[ListingV2, SingleSkuListing, VariationListing].listingPurchaseView` | `ListingPurchaseView` | View of purchase activity for a listing. |
| `listingPurchaseView.lastPurchasedDateTime` | `DateTime` | Most recent purchase time; null when no purchase exists. |
| `listingPurchaseView.uniqueBuyerCount` | `Int` | Count of unique buyers; deprecated and scheduled for removal. |
| `listingPurchaseView.lastPurchasedUnitCost` | `ConvertedPrice` | Unit cost of the latest purchase; null when unavailable. |
| `listingPurchaseView.lastPurchasedUnitCost.converted` | `Price` | Converted price representation. |
| `listingPurchaseView.lastPurchasedUnitCost.converted.amount` | `Decimal` | Converted monetary amount. |
| `listingPurchaseView.lastPurchasedUnitCost.converted.currency` | `CurrencyCode!` | Converted price currency. |
| `listingPurchaseView.lastPurchasedUnitCost.original` | `Price` | Original price representation. |
| `listingPurchaseView.lastPurchasedUnitCost.original.amount` | `Decimal` | Original monetary amount. |
| `listingPurchaseView.lastPurchasedUnitCost.original.currency` | `CurrencyCode!` | Original price currency. |
| `AuctionData.purchasedAsBin` | `Boolean` | Whether the latest purchase used Buy It Now; `false` means auction and null means no purchase. |

#### SAPSVC

Both SAP fields are inaccessible to `publicapi`. The provider has no listing
entity extension; it enriches `Item`.

| Provider output field | Type | Description |
| --- | --- | --- |
| `Item.autoTagProduct` | `Product` | Seller-chosen product when active adoption applies; otherwise a passive-adoption auto-tagged product when confidence and data permit. |
| `Item.autoTagProduct.id` | `ID!` | Identifier of the auto-tagged product reference. |
| `Item.dfAnnotatedAspects` | `[NameValuesPair!]` | SAP-annotated dynamic aspects derived from item data in the Cassini DF indexing zone. |
| `Item.dfAnnotatedAspects[].name` | `String` | Dynamic aspect name. |
| `Item.dfAnnotatedAspects[].values` | `[String!]` | Dynamic aspect values. |

#### SELLERPORTALSVC

The provider extends `Item`; its inventory-storage metadata requires the
item's SKU and listing ID and is inaccessible to `publicapi`.

| Provider output field | Type | Description |
| --- | --- | --- |
| `Item.ebayInventoryStorageMetadata` | `EbayInventoryStorageMetadata` | eBay Inventory Storage metadata; null when not applicable. |
| `Item.ebayInventoryStorageMetadata.isPreAuthenticated` | `Boolean!` | Whether the item was pre-authenticated before fulfillment. |
| `Item.ebayInventoryStorageMetadata.isConsigned` | `Boolean!` | Whether the item was listed through the Consignment program. |
| `Item.ebayInventoryStorageMetadata.isHubFulfilled` | `Boolean!` | Whether the item is fulfilled by an eBay-associated hub. |

#### SELLERRISKENTITYSVC

Searchability fields are inaccessible to `publicapi`. The provider returns
the common `ListingSearchabilityInfo` interface and can resolve its
risk-hold form, `ListingSearchabilityRiskHold`.

| Provider output field | Type | Description |
| --- | --- | --- |
| `[ListingV2, SingleSkuListing, VariationListing].listingSearchabilityInfo` | `ListingSearchabilityInfo` | Searchability state for the listing. |
| `listingSearchabilityInfo.searchabilityStartTime` | `DateTime!` | Time at which the listing becomes searchable. |
| `listingSearchabilityInfo.lastModifiedTime` | `DateTime!` | Most recent searchability update time. |
| `listingSearchabilityInfo.nonSearchableReason` | `NonSearchableListingBusinessReason!` | Reason for a searchability constraint. |
| `listingSearchabilityInfo.nonSearchableReason.id` | `ID!` | Machine-readable reason code. |
| `listingSearchabilityInfo.nonSearchableReason.reasonDisplayString` | `String` | Human-readable reason. |
| `ListingSearchabilityRiskHold.originalSearchabilityStartTime` | `DateTime!` | Original baseline time for becoming searchable. |
| `ListingSearchabilityRiskHold.searchabilityRiskHoldLog` | `ListingSearchabilityRiskHoldLog!` | Reference to the risk-hold log. |
| `ListingSearchabilityRiskHold.searchabilityRiskHoldLog.listingSearchabilityRiskHoldLogId` | `ID!` | Unique risk-hold log identifier. |
| `ListingSearchabilityRiskHold.riskHoldAllowance10DayWindowStartTime` | `DateTime` | Start of the current 10-day allowance window. |
| `ListingSearchabilityRiskHold.riskHoldAllowance10DayWindowEndTime` | `DateTime` | End of the current 10-day allowance window. |
| `ListingSearchabilityRiskHold.riskHoldAllowanceUsedHours` | `Int` | Hours used in the current allowance window. |
| `ListingSearchabilityRiskHold.totalRiskHoldHours` | `Int!` | Total hours held across all risk-hold periods. |

#### SEOCORELABSVC

`photosWithAltText` is inaccessible to `publicapi`. It wraps core listing or
item photos; the provider-owned value is `imageAltText`, while the nested
`Photo` fields are supplied by the parent graph.

| Provider output field | Type | Description |
| --- | --- | --- |
| `[ListingV2, SingleSkuListing, VariationListing, Item].photosWithAltText` | `[PhotoWithAltText!]` | Listing or item photos with optional alt-text descriptions. |
| `photosWithAltText[].imageAltText` | `String` | Accessibility-oriented alternative text; null when no mapping is available. |

#### SLRINVSVC

The provider's listing flags are inaccessible to `publicapi`. Concrete
single-SKU and variation fields require the seller's legacy user ID.

| Provider output field | Type | Description |
| --- | --- | --- |
| `[ListingV2, SingleSkuListing, VariationListing].hideFromSearch` | `Boolean` | Whether an Inventory API-created listing is hidden from search results. |
| `[ListingV2, SingleSkuListing, VariationListing].availableForShipToHome` | `Boolean` | Whether an Inventory API-created listing is available for ship-to-home. |

#### SVLS

SVLS is the broad core-listing read provider, rather than a narrow
post-listing enrichment. Its broad schema and ULP's default `svls` group are
separate inventories whose counts must be regenerated from the current source.
The root-level inventory below keeps this page readable;
the core-listing section and
`svls/svlsService/src/main/resources/schema/SvlsGraphQLSchema.graphqls`
remain the authoritative detail for the nested contract.

| Provider output field family | Type and representative fields | Description |
| --- | --- | --- |
| `[ListingV2, SingleSkuListing, VariationListing]` presentation | `photos: [Photo!]`, `sellerProduct: SellerProduct`, `videos: [Video!]`, `productGalleryFallbackURL: String`, `documents: ListingDocuments`, `promotionalDetails: PromotionalDetails` | Seller product and listing presentation data. |
| Listing classification | `category: ListingCategory`, `itemCondition: ItemCondition`, `listingFormat: ListingFormat`, `listingLifecycle: ListingLifecycle`, `marketplaceId: ID`, `marketplace: ListingMarketplace` | Category, condition, selling format, lifecycle, and marketplace. |
| Commercial and policy terms | `listingTerms: ListingTerms`, `totalQuantity: Int`, `lotSize: Int`, `autoRelistTerms: AutoRelistTerms`, `bestOfferTerms: BestOfferTerms`, `paymentTerms: PaymentTerms`, `taxInfo: TaxInfo`, `returnTerms: ReturnTerms`, `warrantyTerms: WarrantyTerms`, `buyerRestrictions: BuyerRestrictions`, `customPolicies: CustomPolicies` | Listing-level commercial, payment, tax, return, warranty, and buyer-policy data. |
| Fulfillment and location | `fulfillmentTerms: FulfillmentTerms`, `itemLocation: ItemLocation`, `supportContact: SupportContact`, `tradingScope: TradingScope` | Shipping, pickup, logistics-plan, location, support, and trading-region data. |
| Lifecycle, relisting, and inventory state | `draftId: ID`, `sellerListingVersionId: ID`, `coreListingVersionId: ID`, `relistId: ID`, `sourceListingId: ID`, `relistParentListingId: ID`, `endReason: EndReasonEnum`, `outOfStockDate: DateTime`, `inventoryTrackingMethod: InventoryTrackingMethod`, `managedByInventory: Boolean` | Current listing state, version/relist lineage, and inventory-management metadata. |
| Specialized listing data | `regulatoryInfo: RegulatoryInfo`, `vehicleIdentifiers: [NameValuesPair]`, `itemCompatibilities: [ItemCompatibility]`, `visualEnhancements: VisualEnhancements`, `charity: Charity`, `ebayCommunity: EbayCommunity` | Regulatory, vehicle, compatibility, visual, charity, and community data. |
| Item and variation structure | `items: [Item!]!`; variation-only `sku: String`, `minPrice: ConvertedPrice!`, `maxPrice: ConvertedPrice!`, `imagesVaryByAspect: ImagesVaryBy`, `itemsVaryByAspect: [NameValuesPair!]!`, `listingVariations: ListingVariations` | Sellable-item state and MSKU variation/group data. |
| `Item` fields | `itemIdRestReference: ID`, `sku: String`, `itemTerms: ItemTerms`, `creationDate: DateTime`, `sellerPrice: ListingItemPrice`, `itemSellerProduct: ItemSellerProduct`, `quantityAvailable: Int`, `quantitySold: Int`, `extendedProducerResponsibility: ExtendedProducerResponsibility`, `documents: ListingDocuments` | Item-specific identity, price, quantity, terms, seller-product, EPR, and document data. |
| Major nested families | `SellerProduct`, `ListingTerms`, `FulfillmentTerms`, `ShippingTerms`, `PaymentTerms`, `ReturnTerms`, `ListingLifecycle`, `ItemTerms`, `ListingItemPricingTerms`, `ListingCategory`, `ItemCondition`, `TaxInfo`, `RegulatoryInfo`, `ListingDocuments`, and monetary/product types | Nested fields provide the detailed product, price, shipping, payment, return, lifecycle, tax, regulatory, document, and identifier contract. |

SVLS schema directives explicitly transform several source names and shapes:
`price` to `sellerPrice`, `tax` to `taxInfo`, `compatibilities` to
`itemCompatibilities`, `versionId` to `sellerListingVersionId`, and
`primaryCategoryId` to `ListingCategory.primaryCategory`.

#### ITEMCOMPATIBILITYSVC

| Provider output field | Type | Description |
| --- | --- | --- |
| `[ListingV2, SingleSkuListing, VariationListing].listingCompatibilities` | `ListingCompatibilities` | Final compatibility data for a listing; defined once at listing level to avoid MSKU per-item fan-out. |
| `listingCompatibilities.listingId` | `ID!` | Listing associated with the compatibility result. |
| `listingCompatibilities.computedCompatibilitiesByMarketplace` | `[CompatibilitiesByMarketplace!]!` | Final compatibility rows by marketplace. |
| `CompatibilitiesByMarketplace.marketplaceId` | `ID!` | Marketplace to which the compatibility row applies. |
| `CompatibilitiesByMarketplace.compatibilityNotionalProfileGrouping` | `NotionalProfileGrouping!` | Final notional-profile grouping for the marketplace. |
| `CompatibilitiesByMarketplace.searchConfig` | `CompatibilitiesSearchConfig` | Optional search-index configuration for the compatibility result. |
| `Item.compatibilities` | `ItemCompatibilities` | Deprecated item-level compatibility path. |
| `Item.compatibilityCatalogProduct` | `CompatibilityCatalogProduct` | Optional catalog-product reference; not populated by the current ULP item resolver. |

`ItemCompatibilities` and its nested marketplace/search-config types remain
in the schema for compatibility, but are deprecated in favor of
`listingCompatibilities`.

#### VEHENTSVC

| Provider output field | Type | Description |
| --- | --- | --- |
| `[ListingV2, SingleSkuListing, VariationListing].vehicleListingDetails` | `VehicleListingDetails` | Vehicle-listing enrichment. The resolver can return an object containing the listing ID even when nested vehicle data is absent. |
| `vehicleListingDetails.vehicleHistoryReport` | `VehicleHistoryReport` | Available, purchasable, or unavailable vehicle-history-report information. |
| `vehicleListingDetails.vehicleIdentifiers` | `[VehicleIdentifier!]` | Vehicle identifiers, such as a VIN, when available. |
| `vehicleListingDetails.vehicleVerification.verified` | `Boolean!` | Whether uploaded seller vehicle documents passed verification. |
| `vehicleHistoryReport.pastHistory` | `VehicleHistoryReportPastHistory` | Flattened ownership/title, damage, usage, odometer, and status history. |
| `vehicleHistoryReport.reportProvider` | `VehicleHistoryReportProviderInformation` | Provider name, logo, score range, disclaimers, glossary, and report links. |
| `vehicleHistoryReport.fullReportWebUrl`, `totalVehicleEvents`, `reportPurchaseTerms` | `String`, `Int`, `[VehicleHistoryReportPurchaseTerms!]` | Full-report access, available-event count, and paid-report terms. |
| `vehicleHistoryReport.scoreContent` | `ScoreContent` | Buyer-display score/title, summary labels, content, and provider information. |
| `VehicleHistoryReportPastHistory` statuses | Nullable title, ownership, accident/damage, usage, odometer, and deprecated compatibility-alias fields | Source report history flattened for the GraphQL contract; availability determines which fields are populated. |

Most vehicle-report types are excluded from `publicapi`. The schema keeps
deprecated aliases such as `accidentStatus`, `odometerStatus`, and
`reportRunDate`; consumers should use `scoreContent.summaryLabels` instead.

#### PICKUPELIGIBILITY

| Provider output field | Type | Description |
| --- | --- | --- |
| `[ListingV2, SingleSkuListing, VariationListing].eligibleForPudo` | `Boolean` | Whether the listing is eligible for a Pick Up/Drop Off (PUDO) program. The schema documents `null` for a service/connection failure. |

All seller, category, fulfillment, shipping, package, location, price, and
marketplace fields in the provider's `@requires` contract are external
prerequisites rather than pickup-provider output.

#### EGDSELLERMGMT

| Provider output field | Type | Description |
| --- | --- | --- |
| `ShippingProgramEligibility.ebayGuaranteedDelivery` | `EbayGuaranteedDelivery` | eBay Guaranteed Delivery eligibility information for a listing. |
| `ebayGuaranteedDelivery.policy` | `EbayGuaranteedDeliveryPolicy!` | Applied policy, including end-to-end delivery, handling-time, auto-rate-table, or ineligible policy. |
| `ebayGuaranteedDelivery.eligibilityType` | `EbayGuaranteedDeliveryEligibilityType` | US or Australia eligibility type; the schema documents `null` as ineligible. |

`ShippingProgramEligibility.listingId` is the federation key and is not
provider-owned data.

#### MDMLUSVCIO

| Provider output field | Type | Description |
| --- | --- | --- |
| `Item.markdownDiscountDuration` | `ItemMarkdownDiscountDuration` | Promotion duration associated with the item. |
| `markdownDiscountDuration.promoSaleStartDateTime` | `DateTime!` | Markdown-promotion start time. |
| `markdownDiscountDuration.promoSaleEndDateTime` | `DateTime!` | Markdown-promotion end time. |

The provider also exposes seller-promotion status, listing reports, and
markdown-removal mutation outputs. They are promotion-management contracts,
not fields in ULP's mapped current-listing selection.

#### DALASPROXYSOURCESVC

| Provider output field | Type | Description |
| --- | --- | --- |
| `[ListingV2, SingleSkuListing, VariationListing].dalasEvaluation` | `DalasEvaluation` | Parent for the asynchronous DALAS evaluation result; excluded from `publicapi`. |
| `dalasEvaluation.dalasUuid` | `String!` | Evaluation UUID passed through the source evaluation; it is generated by `dalasuuidprovidersvc`, not this provider. |
| `dalasEvaluation.dalasSource` | `DalasSourceEvaluation!` | First-phase plugin evaluation output; inaccessible because it is intended for DALAS plugins. |
| `dalasSource.baseGuid` | `String` | Identifier supporting sequential evaluation, garbage collection, and ULP synchronization. |
| `dalasSource.dalasEntityContainerSource` | `String!` | Base64-encoded first plugin-evaluation entity container. |
| `dalasSource.dalasEntityContainerPreExisting` | `String` | Declared container for a prior evaluation. The checked-in successful source path does not populate it. |

The concrete listing `dalasUuid` prerequisite is `@external`; source-provider
ownership is limited to `dalasEvaluation` and its source-phase fields.

#### DALASPROXYSINKSVC

| Provider output field | Type | Description |
| --- | --- | --- |
| `DalasEvaluation.dalasEntityContainerSink` | `String!` | Base64-encoded final DALAS evaluation container; inaccessible to normal consumers. |
| `DalasEvaluation.dalasStorageManifest` | `String!` | Base64-encoded manifest carrying schema/compression, manifest ID, and garbage-collection metadata. |

The sink consumes `dalasUuid`, `dalasSource`, and source-container fields as
`@external` prerequisites.

#### DALASUUIDPROVIDERSVC

| Provider output field | Type | Description |
| --- | --- | --- |
| `[ListingV2, SingleSkuListing, VariationListing].dalasUuid` | `String!` | DALAS evaluation UUID generated at resolution time. The generator does not derive it from the listing ID; excluded from `publicapi`. |

### Provider implementation analyses

The following analyses trace all 25 linked provider repositories. They
describe provider-local behavior; ULP's group selection, cache container, and
deployment-time enablement remain the responsibility of `unilistingsvc`
configuration.

#### basiclistingdata { #basiclistingdata }

**Purpose and fields.** `basiclistingdata` is a generic store for small
application-owned listing and item attributes, not CLS seller-authored core
state. Its checked-in federation schema adds `watchCount` to `ListingV2`,
`SingleSkuListing`, `VariationListing`, and `Item`; it also offers
`basicListingData` and counter mutations. The ULP generated query includes
additional basic-listing fields, but their implementation is not established
by this checkout.

**Core logic and lifecycle.** The write mutation validates a `ListingV2Input`,
normalizes it to JSON, then invokes `ListingDataService.upsertListingData`.
The service reads the existing NuData document, skips no-op updates, merges
changes, persists through `ListingDataDao`, and emits an `ITEM_REVISED` ULP
refresh event. Federation entity fetchers read the listing document; item
lookup derives a listing ID and finds the requested entry in `items`.

**Storage, errors, and boundary.** The provider stores its owned document in
NuData/Monstor `BasicListingData`, `__ROOT__`, keyed by listing ID. Items are
stored within that document by item ID. Single reads request strong
consistency, while multi-get does not use that option. Database exceptions are
mapped to typed provider errors; both listing and counter changes can emit
asynchronous refresh, whose send failures are logged without a local retry.
Its data is ULP-only relative to CLS core NuDoc, even though this provider also
uses NuData.

**Evidence.** `basiclistingdata/src/main/resources/schema/basiclistingdata.graphqls`,
`schema/watchcount.graphqls`, `graphql/mutation/ListingDataMutation.java`,
`graphql/fetcher/ListingDataFetcher.java`, `service/impl/ListingDataServiceImpl.java`,
`nudata/dao/ListingDataDaoImpl.java`, and `helper/ULPRefreshEventHelper.java`.

#### cmplregulatorysvc { #cmplregulatorysvc }

**Purpose and fields.** `cmplregulatorysvc` provides country-of-origin (COO)
and related compliance state. It exposes
`ListingV2.itemCountryOfOrigin.countryOfOrigin` and `confidenceScore`, plus
an `itemCountryOfOrigin` query that accepts listing/product/category/site and
seller-cleared COO inputs.

**Core logic and lifecycle.** Federated listing reads are cache-only through
`COOEntityHandler`. The direct query defaults to cache-only mode; its vendor
mode emits a Zonos request event rather than calling VMP synchronously.
Vector search is an optional REST vendor-fetch path, not a federated listing
read. Clearing COO writes an event and emits ULP `ITEM_REVISED`.

**Storage, errors, and boundary.** COO records are stored in the
`CountryOfOrigin` NuDoc keyspace under a Base64
`identifierType|identifierValue` root key; audit entries use the `audit`
docset. The three-day expiry applies to soft-deleted records rather than all
active COO values. Vendor rate-limit and authorization failures are explicitly
handled. This is provider-owned enrichment, not CLS core listing NuDoc; the
source does not establish external VMP, vector-index, or single-system
ownership behavior.

**Evidence.** `cmplregulatorysvc/src/main/resources/schema/countryOfOrigin.graphqls`,
`schema/listing.graphqls`, `graphql/countryoforigin/CountryOfOriginDataFetcher.java`,
`COOQueryHandler.java`, `COOEntityHandler.java`, `service/COOVendorService.java`,
`service/COOVectorService.java`, `service/COOCacheService.java`, and
`util/NuDocHelper.java`.

#### connectedproductsulp { #connectedproductsulp }

**Purpose and fields.** `connectedproductsulp` exposes
`Item.connectedProduct`, which contains provider identity, warranty dates, and
digital-authenticity status/image information. The field requires the parent
item's listing ID.

**Core logic and lifecycle.** The entity fetcher validates item and listing
identifiers and batches them through `ConnectedProductItemLoader`. `ItemService`
reads `connectedProduct.*` from its NuDocument representation, maps it to
`ConnectedProductModel`, and uses MapStruct to build the ULP response. REST
`POST`, `GET`, and `DELETE /v1/listing/{listingId}/item/{itemId}` operations
update, retrieve, or remove provider-owned modules. Modified updates and
deletes synchronously send `ITEM_REVISED` through the ULP event producer.

**Storage, errors, and boundary.** The repository stores provider-owned data
in `ConnectedProductsULPData`, `__ROOT__`, keyed by item ID; the listing ID is
federation and refresh context, not part of the persistence key. It supports
partial module updates and no-op detection before it persists the full
document. Changed REST writes/deletes send synchronous `ITEM_REVISED` only
when `shouldPublishToULP` is enabled; no retry, TTL, or local cache is shown.
It normalizes provider failures into typed GraphQL errors. This is
provider-owned NuDocument data, not a CLS core docset. Its checked-in
build-time GraphQL generation and runtime mapping explain that the source can
expose the field even though the `unilistingsvc` generated mapping has no
local `CONNECTEDPRODUCTSULP` entry; deployed availability still requires
schema/configuration confirmation.

**Evidence.** `connectedproductsulp/src/main/resources/schema/schema.graphqls`,
`graphql/ConnectedProductItemFetcher.kt`, `graphql/ConnectedProductItemLoader.kt`,
`service/ItemService.kt`, `database/ItemRepository.kt`,
`database/utils/ConnectedProductModelMapper.kt`, and
`ulp/cache/ULPCacheRefreshEventGenerator.kt`.

#### dealsgraph { #dealsgraph }

**Purpose and fields.** `dealsgraph` contributes
`dealDetails` to `ListingV2`, `SingleSkuListing`, and `VariationListing`.
The output includes daily-deal status, permanence, quantity restrictions and
quantity, plus deal start/end timestamps. It also provides a direct
`dealDetailsByListingId` query with a 100-ID limit.

**Core logic and lifecycle.** Entity and direct-query resolvers load through
`DealFlagsDataLoader`. When `NuDocIntegrationEnabled` is true, the loader
reads `__ROOT__` documents in the `DealsULP` Monstor/NuDocument keyspace and
maps stored values, including epoch milliseconds, to GraphQL. When disabled,
it uses `FakeDealFetcher`.

**Storage, errors, and boundary.** A missing document becomes
`isDailyDeal=false`; invalid numeric IDs and omitted results do as well.
Other Monstor errors become typed, non-retryable provider errors with listing
and service context. The provider refreshes configuration from
`dealsgraphcfg`; the inspected read path has no local write, retry, TTL, event
publisher, or provider-local cache. Deal state is separate from CLS core
listing NuDoc, although it is keyed by the core listing ID.

**Evidence.** `dealsgraph/src/main/resources/schema/listingDailyDealDetails.graphqls`,
`resource/DealsResource.java`, `dataloader/DealFlagsDataLoader.java`,
`fetcher/NuDocFetcher.java`, `MonstorConfig.java`, and
`exception/ProviderExceptionHandler.java`.

#### defaultulpprovider { #defaultulpprovider }

**Purpose and fields.** `defaultulpprovider` is a provider scaffold and ULP
directive/schema example, rather than a listing-data backend. It exposes the
gateway-excluded `defaultUlpProvider` query and an illustrative
`DefaultULPProviderOutput` with `id`, `description`, and test/example fields.
`otherGroupField` demonstrates `@fieldGroup`; the repository also defines a
shared `Photo` type.

**Core logic and lifecycle.** Its sole data fetcher returns a hard-coded
string, despite the schema declaring an object output. There is no listing
entity resolver, data service, persistence adapter, cache, or event-generation
implementation in the inspected path. A test verifies normal GraphQL
subselection validation only; it does not prove a valid object-subselection
response.

**Storage, errors, and boundary.** The schema defines general directives such
as principal authorization, fallback, and event-generation controls, but this
repository does not implement those behaviors for a listing field. It has no
NuDoc relationship. The scaffold nature and lack of a `ListingV2` field
explain why it cannot establish a generated production selection, without
proving anything about deployment configuration.

**Evidence.** `defaultulpprovider/src/main/resources/schema/schema.graphqls`,
`src/main/java/com/ebay/app/DefaultULPProviderDataFetcher.java`, and
`src/main/java/com/ebay/app/ResourceConfig.java`.

#### ebaypluseligibilitysvc { #ebaypluseligibilitysvc }

**Purpose and fields.** `ebaypluseligibilitysvc` adds
`FulfillmentTerms.shippingProgramEligibility.ebayPlus`, an internal
eligibility flag excluded from `publicapi`.

**Core logic and lifecycle.** The federation fetcher validates `listingId`,
then a DGS loader batches `FulfillmentTerms` keys. For each listing it reads
a precomputed `NuKVListingEntity` and maps `isEligible()` to `ebayPlus`; this
layer does not calculate eligibility. A separate
`EligibilityListingProcessor` can read the same entity for configured
public-namespace program properties.

**Storage, errors, and boundary.** The provider reads the
`ebaypluslistingeligibilitynukvhost` keyspace by decimal listing ID, warming
up and cleaning up NuKV client state at application start/stop. Missing IDs
and NuKV failures become `ListingLogisticsDataFetcherException` and emit
monitoring counters. The DAO configures no expiry. Although the GraphQL path
does not publish events, evaluation writes upsert the same entity and send
`ITEM_REVISED` up to three times; refresh-send failures are logged. This is
shipping-program enrichment, not a CLS NuDoc mapping.

**Evidence.** `ebaypluseligibilitysvc/ebaypluseligibility-lib/src/main/resources/schema/ebaypluseligibility.graphqls`,
`EbayPlusDataFetcher.java`, `EbayPlusDataLoader.java`,
`NuKVListingEntityService.java`, `NuKVInitializer.java`, and
`EligibilityListingProcessor.java`.

#### ItemVisibility (`itmvzblit`) { #itemvisibility-itmvzblit }

**Purpose and fields.** Item Visibility (IVF) provides cross-site listing
visibility. `ListingV2` exposes `visibilitySummary` with packed visibility,
explicitly suppressed sites, and default-visible sites, as well as
`visibility.hasNativeBlock`. The same extension applies to single-SKU and
variation listings.

**Core logic and lifecycle.** Federation fetchers construct listing stubs and
batch-load the two outputs using request-scoped user/site context.
`BatchAsyncVisibilityDataReader` reads NuData and SaleBo, checks
discrepancies, and maps the result to GraphQL DTOs. This establishes a
consumer view of a visibility calculation, not a binary checkout decision.

**Storage, errors, and boundary.** IVF stores the `LvfVisibilityStorage`
`__ROOT__` document by decimal item/listing ID. It dual-writes Caty and NuData
while Caty remains its source of truth during the checked-in migration. It uses
eventual NuData read consistency, retries storage operations, handles not-found
as empty, and can recover an optimistic-lock conflict when a reread matches.
A visibility change, or a missing incoming ULP summary, can asynchronously
publish an `ITEM_REVISED` cache refresh. The source proves ULP core-data
enrichment but does not identify a CLS NuDoc docset, a Caty physical schema, or
a provider-document TTL.

**Evidence.** `ItemVisibility/ItemVisibilityService/src/main/resources/api-graphql/schema.graphql`,
`graphql/DataFetchers.java`, `BatchVisibilityLoader.java`,
`BatchAsyncVisibilityDataReader.java`, `IVFDataUpdateProcessor.java`,
`UlpCacheRefreshEventGenerator.java`, and `NuDataStorageGateway.java`.

#### LC-ListingProvider (`lclistingprovider`) { #lc-listingprovider }

**Purpose and fields.** The Live Commerce provider adds
`ListingV2.ebayLive`. Its output includes live event IDs, a primary-event
snapshot, listing intent, and `purchasable`, `visible`, and
`buyspotEligible` flags for single-SKU and variation listings.

**Core logic and lifecycle.** Entity fetchers validate `listingId`, batch via
`LiveListingDataLoader`, and read `EbayLive` JSON from NuKV using a configured
key prefix. `EbayLiveMapper` makes the first live event the primary event,
converts epoch milliseconds to UTC, and applies an orphan-listing
compatibility rule to `purchasable`.

**Storage, errors, and boundary.** The provider reads `EbayLive` JSON from
the `cplivecommercenukvhost` cache under `i:<listingId>`. Reads make at most
four attempts with 100 ms waits for configured retryable failures; not-found
and terminal failures degrade to null provider data. `primaryEvent` is
documented as eventually consistent cache data suited to high-throughput
buyer-facing reads. The provider supports only single-SKU and variation
listing types, and it has no local writer, refresh publisher, invalidator, or
entry TTL in the inspected source. It also has no CLS/NuDoc reference.

**Evidence.** `LC-ListingProvider/schema/ebayLive_provider.graphqls`,
`ListingDataFetcher.java`, `ListingDataLoader.java`, `NuKvClient.java`,
`EbayLiveMapper.java`, and `ProviderExceptionHandler.java`.

#### locnmappingsvc { #locnmappingsvc }

**Purpose and fields.** `locnmappingsvc` associates a listing or SKU with
warehouse locations. It adds `Item.inventoryLocations.warehouseLocations`,
where each location has a `merchantLocationKey`; the field requires SKU,
listing ID, and seller ID context.

**Core logic and lifecycle.** The entity fetcher validates the item/listing/
seller context and batches items through `LocationMappingDataLoader`.
`LocationMappingService` constructs a seller + listing + normalized-SKU key,
reads `ListingLocations` from NuData, removes deleted documents, and maps
each stored location to the GraphQL output. Batch reads are chunked at 100
keys on a dedicated executor.

**Storage, errors, and boundary.** REST writes and deletes upsert/delete the
`ListingLocations` `__ROOT__` NuData document keyed by concatenated seller ID,
listing ID, and normalized SKU. They pass a `-1` TTL argument, retry NuData up
to five times, publish an item-location BES event, and can publish
default-disabled, fire-and-forget `ITEM_REVISED` ULP refreshes. If a write
fails, it rolls back the listing-extension flag; cache-refresh failures do not
retry. This is provider-owned inventory-topology data keyed by ULP core
identifiers; no CLS docset or NuData retention meaning for `-1` is identified.

**Evidence.** `locnmappingsvc/src/main/resources/schema/locationMapping.graphqls`,
`LocationMappingDataFetcher.java`, `LocationMappingDataLoader.java`,
`LocationMappingServiceImpl.java`, `LocationMappingController.java`,
`NuDataUtils.java`, and `UlpCacheRefreshPublisher.java`.

#### Marketplace Logistic Service (`mpls`) { #marketplace-logistic-service-mpls }

**Purpose and fields.** MPLS adds
`FulfillmentTerms.shippingProgramEligibility.globalShippingProgram`.
The output contains Global Shipping Program eligibility, estimated
weight/dimension sources, estimator version/mode, tariff information,
domestic-leg cost/service, partner restrictions, and partner-hub postal code.

**Core logic and lifecycle.** The federation fetcher builds
`FulfillmentTerms` from the listing entity; `MplsDataLoader` batches keys and
uses `DBFacade` to strongly read `ItemData` from the `GlobalShippingProgram`
Monstor keyspace. It normalizes the response for GraphQL, including a default
GBP currency, two-decimal domestic-leg cost, and pipe-separated restricted
country codes.

**Storage, errors, and boundary.** The provider reads
`GlobalShippingProgram` through `KeyFactory(listingId)` with strong
consistency. Missing store data returns a `ShippingProgramEligibility` object
with a null GSP payload. Exceptions are logged and surfaced through the
GraphQL exception handler; the Monstor read allows retries, but this source
does not set their count or backoff. The inspected GraphQL path has no
provider-local cache, TTL, or event publisher. It reads NuData keyed by core
listing ID but does not identify a CLS NuDoc document or the upstream writer.

**Evidence.** `MarketplaceLogisticService/src/main/resources/schema/mpls.graphqls`,
`graphql/MplsDataFetcher.java`, `graphql/MplsDataLoader.java`,
`client/db/DBFacade.java`, `client/db/impl/DefaultDBFacade.java`,
`client/db/impl/DefaultDbClient.java`, and `graphql/GraphqlExceptionHandler.java`.

#### purchaseviewgraphsvc { #purchaseviewgraphsvc }

**Purpose and fields.** Purchase View adds
`ListingV2.listingPurchaseView` to single-SKU and variation listings. It
returns last-purchase time, a deprecated unique-buyer count, and last
purchased unit cost; it requires the seller's legacy user ID and is excluded
from `publicapi`.

**Core logic and lifecycle.** `SaleSummaryDetailsDataFetcher` creates a
request context from the selected GraphQL subfields and delegates to
`SaleSummaryDetailsApplicationHandler`. The handler executes only the needed
COMS tasks: one counts unique counterparties over the configured lookback and
another pages orders to find the latest qualifying purchase or a
commitment-date fallback. The default lookback is 90 days, batch size is five,
and the local COMS-contract retry limit is zero. The separate
`AuctionData.purchasedAsBin` handler uses Cosmos and is not evidence that
`listingPurchaseView` does.

**Storage, errors, and boundary.** This is a request-time COMS aggregation
keyed by listing and seller ID, rather than a provider cache or database.
COMS timeouts/failures become sentinel responses, and retryable cases become
typed GraphQL provider errors. No CLS/NuDoc implementation is referenced in
the provider source; QA test synchronization with other stores is not evidence
of a production data path.

**Evidence.** `purchaseviewgraphsvc/PurchaseViewGraphLib/src/main/resources/schema/schema.graphqls`,
`PurchaseViewGraphService/.../SaleSummaryDetailsDataFetcher.java`,
`SaleSummaryDetailsApplicationHandler.java`, `FetchUniqueBuyerCountTask.java`,
`AggregateSaleSummaryDateTask.java`, `ComsContractErrorUtil.java`, and
`PurchaseViewExceptionHandler.java`.

#### sapsvc { #sapsvc }

**Purpose and fields.** `sapsvc` extends `Item` with `autoTagProduct` and
`dfAnnotatedAspects`, both excluded from `publicapi`. The provider turns
search/classifier output into an auto-tagged product reference and a deduped
set of dynamically annotated name/value aspects.

**Core logic and lifecycle.** `SapItemDataFetcher` validates and normalizes
the item ID, then batches through `SapItemDataLoader`. `SapMonstorClient`
calls `/v1/monstorGetBulk`, reads the `ClassifierResult` payload, obtains
`AutotagProdRefId` from the adoption annotator, and reads configured
dynamic-aspect names from the `df` namespace across annotators. The aspect
configuration is refreshable through `sapeventprocessorcfg`.

**Storage, errors, and boundary.** The provider uses a DGS batch loader and
reads the external `/v1/monstorGetBulk` endpoint with `SAP_INTERNAL` key type;
the checked-out source does not establish the physical Monstor store as a
provider-owned source of truth. It has no provider-local write, TTL, cache
invalidation, retry, or event publisher. Invalid item IDs produce typed
bad-request errors; client/parse failures are logged and return null or an
empty map. It contains no CLS/NuDoc lineage.

**Evidence.** `sapsvc/src/main/resources/schema/sapitemdata.graphqls`,
`graphql/datafetcher/SapItemDataFetcher.java`,
`graphql/dataloader/SapItemDataLoader.java`, `client/SapMonstorClient.java`,
`config/GlobalDependentLibConfig.java`, and `util/RequestValidatorUtil.java`.

#### sellerportalsvc { #sellerportalsvc }

**Purpose and fields.** `sellerportalsvc` supplies
`Item.ebayInventoryStorageMetadata`, derived from item-group authentication,
consignment, and hub-fulfillment state. Its federated item resolver requires
item ID, listing ID, and SKU.

**Core logic and lifecycle.** `SellerListingDataFetcher` batches
listing/SKU pairs through `ItemGroupDataLoader` and `ItemGroupDAO`. The
provider's REST listing workflows validate seller listing state, optionally
enrich from catalog, create or synchronize inventory/offers, and map
item-group data to listing responses. Its DAO has batch reads and atomic
item-group/item updates.

**Storage, errors, and boundary.** The ULP field is resolved from
`ItemGroupDataObject` records keyed by listing ID and SKU; the checked-out DAO
does not establish its physical store. Creation and synchronization update
provider-owned state; creation rolls back offers, variation groups, and
inventory items if it fails. Synchronous ULP refresh makes three total send
attempts. Asynchronous refresh makes its initial attempt plus up to three
retries; cache/IMS failures are logged and do not fail a completed creation.
The checkout contains no explicit CLS or NuDoc reference, so its exact
physical store and core-field lineage remain unverified.

**Evidence.** `sellerportalsvc/src/main/java/com/ebay/sellerportal/app/graphql/SellerListingDataFetcher.java`,
`ItemGroupDataLoader.java`, `dal/dao/ItemGroupDAO.java`,
`resources/ListingResource.java`, `services/ListingService.java`, and
`producer/CacheRefreshEventGenerator.java`.

#### sellerriskentitysvc { #sellerriskentitysvc }

**Purpose and fields.** `sellerriskentitysvc` exposes the internal-only
`listingSearchabilityInfo` on `ListingV2`, `SingleSkuListing`, and
`VariationListing`. The risk-hold form supplies searchability start and
modification times, a non-searchable reason, original start time, hold-log ID,
allowance-window timings, used hours, and total hold hours.

**Core logic and lifecycle.** Federation entity fetchers validate `listingId`
and invoke `ListingSearchabilityRiskHoldDataLoader`. The loader reads
`DelayedItem` through `DelayedItemEntityService` and maps its index, modified,
original-index, log, and delay-period fields into the GraphQL projection.

**Storage, errors, and boundary.** REST update paths whitelist the
`DELAYED_ITEM_KEYSPACE` API, upsert `DelayedItem` `__ROOT__` documents by
listing ID through Monstor, and asynchronously emit `ITEM_REVISED` for ULP
refresh without a local retry. Deserialization and upsert errors are logged
and surfaced, while the REST get path converts retrieval errors to HTTP 204.
A null epoch is mapped to the loader's current time, so it must not be read as
a source timestamp. This is provider-owned NuDocument risk state, not CLS core
NuDoc.

**Evidence.** `sellerriskentitysvc/src/main/resources/schema/schema.graphqls`,
`ListingSearchabilityRiskHoldDataFetcher.java`,
`ListingSearchabilityRiskHoldDataLoader.java`, `DelayedItemResource.java`,
`DelayedItemEntityServiceImpl.java`, and `DelayedItemConstants.java`.

#### seocorelabsvc { #seocorelabsvc }

**Purpose and fields.** `seocorelabsvc` adds `photosWithAltText` to
`ListingV2`, `SingleSkuListing`, `VariationListing`, and `Item`. Each output
contains the source `Photo` plus optional `imageAltText`, and is excluded from
`publicapi`.

**Core logic and lifecycle.** Federation entity hydration creates listing/item
stubs; `PhotoAltTextFetcher` batches listing IDs and maps each input photo's
image GUID to cached alt text. `PhotoAltTextLoader` bulk-reads the NuKV SEO
cache. The mapper retains the first alt-text value for a GUID collision and
returns the original photos without alt text when mapping/data load fails.

**Storage, errors, and boundary.** The provider reads the
`seocorelabcachenukvhost` NuKV cache by listing ID with a three-second loader
timeout. A protected REST refresh endpoint emits `ITEM_REVISED` when the
refresh feature and client allowlist permit it; the source does not establish
that an upstream NuKV write precedes the request. The provider has no local
NuKV writer, explicit retry, or persistence implementation beyond reads, and
does not establish a CLS/NuDoc source for the photo itself.

**Evidence.** `seocorelabsvc/src/main/resources/schema/photo-alt-text-schema.graphqls`,
`graphql/EntityFetcher.java`, `graphql/PhotoAltTextFetcher.java`,
`graphql/PhotoAltTextLoader.java`, `cache/NuKVSeoCoreLabCacheImpl.java`,
`cache/PhotoAltTextMappingMapper.java`, and
`cache/CacheRefreshService.java`.

#### slrinvsvc { #slrinvsvc }

**Purpose and fields.** `slrinvsvc` supplies the internal
`ListingV2.hideFromSearch` and `availableForShipToHome` flags for single-SKU
and variation listings. The fields require seller context and are excluded
from `publicapi`.

**Core logic and lifecycle.** The entity fetcher validates `listingId` and
`seller.legacyUserId`; its DGS loader batches requests on a dedicated
executor. `ListingFlagsService` groups requests by seller, reads
`SKUStatusDAO`, decodes stored flags, merges duplicate rows using OR for
ship-to-home and AND for search hiding, then fills absent listings with null
flags.

**Storage, errors, and boundary.** The GraphQL path is read-through from
`SKUStatusDAO`/`SKUStatus` by seller legacy user ID and listing ID; the
physical database is not established. When aggregated ship-to-home is false,
the provider forces `hideFromSearch=true`; an absent row remains null for both
flags. Invalid context and DAO errors become typed provider GraphQL errors.
Separate inventory write paths can emit default-disabled, asynchronous,
fire-and-forget `ITEM_REVISED` cache refreshes; send failures are ignored
after logging and do not retry. The source has no CLS/NuDoc references, so
only the federation relationship is established.

**Evidence.** `slrinvsvc/src/main/resources/schema/listingflags.graphqls`,
`ListingFlagsDataFetcher.java`, `ListingFlagsDataLoader.java`,
`ListingFlagsServiceImpl.java`, `DefaultSKUStatusRepository.java`,
`UlpCacheRefreshPublisher.java`, and `AppInventoryResource.java`.

#### svls { #svls }

**Purpose and fields.** SVLS is the broad, read-only seller-view/core-listing
provider. It reconstructs listing, item, seller-product, category, price,
quantity, terms, fulfillment, lifecycle, variation, tax, regulatory, vehicle,
and document data. It is the source-backed listing-ID read boundary for the
large default `svls` group, rather than a narrow provider enrichment.

**Core logic and lifecycle.** Listing and federation fetchers batch IDs using
a DataLoader with caching disabled, then call `ItemAndGroupProcessor` and
`CLSClient.getItemsAndGroupForListing` with the `FULL` field group. CLS
responses are converted through item/group adapters and `GraphQLConverter`,
which chooses `SingleSkuListing` or `VariationListing` based on whether CLS
returns an item group. Separate loaders support archived and versioned reads.
SVLS has no listing write path or ULP refresh publisher; its CLS clients have
a configured maximum retry count of two.

**Storage, errors, and boundary.** SVLS reads CLS over authenticated HTTP and
does not directly access a NuData/NuDocument DAO. Its DataLoader cache is
disabled. Failed ordinary batch records can be omitted, while bulk reads retain
typed GraphQL error data, including listing identity and retryability. The CLS
client config sets `maxRetryCount=2`, but this does not prove an effective
downstream retry policy. The source proves a direct service-level CLS
relationship, but it does not identify the individual CLS NuDoc document that
supplies each GraphQL field. The lack of a dedicated `_svls` query branch is
expected for this baseline group.

**Evidence.** `svls/svlsService/src/main/resources/schema/SvlsGraphQLSchema.graphqls`,
`dgsgraphql/datafetcher/ListingDataFetcher.java`,
`dgsgraphql/dataloader/ListingDataLoader.java`,
`processors/ItemAndGroupProcessor.java`, `gingerclients/CLSClient.java`,
`dgsgraphql/converter/GraphQLConverter.java`, and
`service/SellerViewListingService.java`.

#### itemcompatibilitysvc { #itemcompatibilitysvc }

**Purpose and fields.** `itemcompatibilitysvc` supplies final motors
compatibility data by marketplace, including notional-profile grouping and
optional search configuration. `listingCompatibilities` is the preferred
listing-level contract; the legacy `Item.compatibilities` path remains
deprecated so MSKU compatibility does not fan out to every variation.

**Core logic and lifecycle.** The federation resolver reads the listing ID,
marketplace, and primary category. The query service checks marketplace/category
allowance, obtains cached or remotely fetched category compatibility, then
reads the `ItemCompatibility` Monstor/NuData record. It filters rows to the
listing marketplace, adds a configured search-config ID, and returns no
object when no compatible row remains. Fitment refreshes can call Fitment
Service, construct or update notional-profile groupings, and persist the
result. The current item-entity ULP path intentionally returns an empty
compatibility item; it does not populate `compatibilityCatalogProduct`.

**Storage, errors, and boundary.** Provider compatibility documents use the
`ItemCompatibility` NuData/Monstor keyspace, while listing history is
separately configured as `FPAListingHistory`; both are distinct from CLS core
NuDoc. Category data uses an in-memory cache refreshed at the configured
24-hour interval; the compatibility documents have no local TTL. Successful
changed fitment data can publish `ITEM.REVISED` or backfill events, with
configurable sync/async send behavior and a two-second refresh timeout. The
consumer requests broker retry on processing errors, but checked-in
configuration disables message retries, so delivery behavior is runtime
dependent. Fitment timeout, throttle, and 5xx responses are retryable; an
invalid compatibility type is retried only by mutation/refresh paths, not
normal ULP reads.

**Evidence.** `itemcompatibilitysvc/src/main/resources/schema/schema.graphqls`,
`resolver/ItemCompatibilityResolver.kt`,
`service/ItemCompatibilityQueryService.kt`,
`service/CategoryServiceUtil.kt`, `service/ItemCompatibilityFromFitSvcUtil.kt`,
`repository/ItemCompatibilityRepositoryImpl.kt`, `nudata/ItemCompatibilityDAO.kt`,
`util/ULPCacheRefreshEventGenerator.kt`, and `task/RefreshItemConsumerTask.kt`.

#### vehentsvc { #vehentsvc }

**Purpose and fields.** `vehentsvc` enriches vehicle listings with vehicle
history, report-provider and purchase data, vehicle identifiers, and seller
document-verification status. Report content can represent free, paid, or
unavailable vehicle history, so a returned object does not guarantee every
history subfield is available.

**Core logic and lifecycle.** The listing field fetcher batches selected
vehicle history/identifier fields by listing ID and marketplace. It calls
FGQL `listingsV2ByIds` to obtain seller ID, VIN, and year/make/model context,
then reads the vehicle-history data by VIN, seller, site, and attribute ID.
It prefers the `MotorsVehicleHistoryReport` NuDocument path when enabled and
falls back to Oracle CATY for missing, unparsable, or `NO_VHR` data. The
independently selected `vehicleVerification` field reads a
`VehicleVerificationDetails` NuDocument child record by listing ID.

**Storage, errors, and boundary.** Vehicle-history data uses
`MotorsVehicleHistoryReports`, keyed by the concatenation of VIN, seller ID,
site ID, and attribute ID; vehicle verification uses `MotorsPartnerData` and
a `VehicleVerificationDetails` child record keyed by listing ID with a
90-day TTL. Vehicle-history writes can dual-write NuDocument and CATY, while
vehicle-verification writes NuDocument. Both changed-write paths publish ULP
refresh events. `UlpCacheRefreshPublisher` has `maxRetries=2` with a 500 ms
delay for thrown `ULPException`, but asynchronous producer-callback failures
are logged rather than rethrown. The core-context FGQL client retries only
transport failures three times before returning no result. This is
provider-owned vehicle data keyed from ULP core context, not a CLS document
family. The source establishes the CATY fallback but not its physical-store
or external service semantics.

**Evidence.** `vehentsvcService/src/main/resources/schema/VehicleHistoryReport.graphqls`,
`graphql/VehicleHistoryReportDataFetcher.java`,
`graphql/VehicleListingDetailsDataLoader.java`,
`graphql/service/VehicleListingDetailsService.java`,
`vehentsvcLib/.../helper/VehicleHistorySummaryHelper.java`,
`fgql/FGQLServiceInvoker.java`,
`dal/ebayvehicleattrinfo/MotorsVehicleHistoryReportNuDataServiceDao.java`,
`dal/vehicleverification/VehicleVerificationNuDataDao.java`, and
`events/UlpCacheRefreshPublisher.java`.

#### pickupeligibility { #pickupeligibility }

**Purpose and fields.** `pickupeligibility` computes whether a listing is
eligible for a Pick Up/Drop Off (PUDO) program. It consumes seller offer
status and a substantial federated listing context, but owns only the
`eligibleForPudo` result.

**Core logic and lifecycle.** The entity fetcher converts ULP listing data
to the legacy sale representation, reads seller pickup offer
intent/eligibility through ULOS, builds listing details, and applies the
configured pickup rules. Category, format, location, handling time, price,
returns, shipping service, package dimensions, and weight can participate in
the rules. The result is true if any PUDO program is eligible; configured
filtered sites return false.

**Storage, errors, and boundary.** The GraphQL path is a request-time
evaluation and does not write the Sale PUDO bit. ULOS persistence code
establishes `USER_PROG_COMMITMENT` and `USER_PROG_ELIGIBILITY`, keyed by user
ID and program-commitment ID; an optional `PickupEligibility` NuDocument
client uses user/program-commitment keys. Other event-driven listing flows can
update the legacy `Sale.Flags12` bit and refresh ULP. A separate commitment
cache has a 3,600-second lifetime, but this source does not establish that it
serves the GraphQL path or which store is authoritative during migration.
Despite the schema documenting null for service failure, the loader maps many
conversion and calculation failures to false; downstream consumers must not
equate false with a definitive business ineligibility without error context.

**Evidence.** `PickupEligibilityService/upcsService/.../schema/pickupeligibility.graphqls`,
`graphql/datafetcher/EligibleForPudoDataFetcher.java`,
`EligibleForPudoDataLoader.java`, `UPCSProcessor.java`,
`PickUpServiceListingOfferPlugin.java`, `PickupListingServiceClient.java`,
`PickUpRuleEngineImp.java`, `CacheRefreshEventGenerator.java`, and
`ULOSDalUtilProxy.java`.

#### egdsellermgmt { #egdsellermgmt }

**Purpose and fields.** `egdsellermgmt` adds eBay Guaranteed Delivery policy
and regional eligibility type to the federated `ShippingProgramEligibility`
entity. A present object has a policy; a missing eligibility type represents
an ineligible regional result.

**Core logic and lifecycle.** The entity resolver validates the listing ID,
then its DGS loader reads the provider's
`EbayGuaranteedDelivery` document through a strong-consistency
Monstor/NuData GET. The result is mapped to policy and US/Australia
eligibility type. Separate listing-logistics operations create, merge, and
delete these provider records; successful writes synchronously send an
`ITEM_REVISED` ULP refresh.

**Storage, errors, and boundary.** The provider stores
`EbayGuaranteedDelivery` `__ROOT__` documents by listing ID. A missing
document produces a null `ebayGuaranteedDelivery` object, while async loader
failures also collapse to null. Write requests use strong-consistency Monstor
calls, enable client retry, and set a 5,000 ms timeout; the source does not
prove the retry count or backoff. Refresh-send failures are logged rather than
rethrown, and no GraphQL-path cache or TTL is defined. This is provider-owned
Monstor/NuData enrichment keyed by core listing ID, not a named CLS core NuDoc
family.

**Evidence.** `GuaranteedDeliverySellerManagement/egdsellermgmtService/.../schema/egd.graphqls`,
`graphql/datafetcher/EbayGuaranteedDeliveryResolver.java`,
`EbayGuaranteedDeliveryDataLoader.java`,
`GuaranteedDeliveryLib/.../dao/EbayGuaranteedDeliveryMonstorDAO.java`,
`listinglogistics/ListingLogisticsOperations.java`, and
`util/ULPCacheRefresher.java`.

#### mdmlusvcio { #mdmlusvcio }

**Purpose and fields.** `mdmlusvcio` supplies markdown-promotion start and
end times on an item. Its additional seller-promotion reports and mutations
support markdown management but are outside ULP's current-listing field
selection.

**Core logic and lifecycle.** The item entity fetcher validates item and
listing identity, batches listing IDs, and reads an `ItemSellerDiscount`
record from NuKV. For a selected MSKU backfill, missing NuKV dates cause a
SaleBo lookup and SME markdown-item-detail lookup; recovered promotion ID and
dates are written back to NuKV. SSKU items with no usable NuKV data return
null. Other report/summary paths read SME markdown database data.

**Storage, errors, and boundary.** Markdown detail/log/history data is
provider-owned SME database state, while duration data is primarily the NuKV
`ItemSellerDiscount` record looked up by listing ID; NuKV is not NuDoc. The
ULP listing field disables DataLoader caching and limits batches to 10; no
NuKV namespace or TTL is established. Per-item lookup or backfill failures
become null. Markdown operations can publish `ITEM_REVISED`, but publication
is feature-gated and disabled by the checked-in default. Listing Processing
Service calls retry failed-system responses up to the configured limit. The
SaleBo fallback is a legacy recovery path, not proof of CLS NuDoc ownership.

**Evidence.** `mdmlusvcioLib/src/main/resources/schema/markdown.graphqls`,
`graphql/datafetcher/PromoSaleDateDataFetcher.java`,
`MarkdownDiscountOnItemDataLoader.java`, `accessor/db/NukvDataAccessor.java`,
`ListingDBAccessor.java`, `SMEMarkdownDBAccessor.java`,
`accessor/service/ListingProcessServiceAccessor.java`, and
`mdmlusvcioApi/.../CacheRefreshEventGenerator.java`.

#### dalasproxysourcesvc { #dalasproxysourcesvc }

**Purpose and fields.** `dalasproxysourcesvc` starts the DALAS plugin
evaluation stage. It owns the parent `dalasEvaluation` and source-phase
container/base-GUID data. The nested UUID is passed through; the concrete
listing UUID prerequisite is external and originates from
`dalasuuidprovidersvc`.

**Core logic and lifecycle.** The `SingleSkuListing` and
`VariationListing` entity resolvers batch a converted ULP listing and its
UUID to DALAS `/v3/plugin-orchestrations/{listingId}`. The provider encodes
the returned entity container and emits a `DalasSourceEvaluation`. Listings
outside the configured traffic ramp return an empty source without the DALAS
request. DataLoader caching is disabled, no local DAO/cache or TTL exists,
and the result is request-time DALAS behavior. The implementation does not
populate the schema's optional `dalasEntityContainerPreExisting` field on its
successful source path.

**Storage, errors, and boundary.** The repository proves an external DALAS
POST, not DALAS persistence, event delivery, or source freshness. It has no
local HTTP retry loop; null-status and HTTP 5xx failures are classified
retryable, while 4xx and validation failures are not. Per-listing batch
failures retain status/error information and are mapped to typed GraphQL
errors. It consumes ULP core listing context but has no CLS client or NuDoc
DAO.

**Evidence.** `dalasproxysourcesvc/src/main/resources/schema/schema.graphqls`,
`resolver/DalasSourceEvaluationEntityResolver.java`,
`loader/PluginOrchestrationsBatchLoader.java`,
`service/PluginOrchestrationsService.java`, `util/DalasResponseBuilder.java`,
and `error/DalasGraphQLExceptionHandler.java`.

#### dalasproxysinksvc { #dalasproxysinksvc }

**Purpose and fields.** `dalasproxysinksvc` performs the second DALAS stage
for a source evaluation. It owns the inaccessible sink container and the
storage manifest; UUID and source-stage values are external prerequisites.

**Core logic and lifecycle.** The `DalasEvaluation` entity resolver batches
the source container, base GUID, and UUID to DALAS
`/v3/immutable-append/{listingId}`. It encodes the response as a storage
manifest. An empty source short-circuits to empty sink/manifest values.
DataLoader caching is disabled and no provider-local persistence, TTL, or
domain-event path is implemented. The checked-in response builder assigns
the incoming source container to `dalasEntityContainerSink`, despite the
schema describing the field as the final container.

**Storage, errors, and boundary.** This is a request-time DALAS pipeline
stage, not a CLS/NuDoc owner. It has no local HTTP retry loop; null-status and
HTTP 5xx failures are classified retryable, while 4xx or malformed input are
non-retryable. It then surfaces typed GraphQL errors with per-listing status.
The generated ULP branches for both DALAS groups intentionally include the
composed nested
`{ dalasStorageManifest listingId }` selection: aliases control generated
query inclusion, not field ownership. `dalasproxysourcesvc` owns the
listing-level parent, `dalasproxysinksvc` owns the manifest, `listingId` is
the federation key, and `dalasuuidprovidersvc` owns the UUID.

**Evidence.** `dalasproxysinksvc/src/main/resources/schema/schema.graphqls`,
`resolver/DalasEvaluationEntityResolver.java`,
`loader/ImmutableAppendBatchLoader.java`,
`service/ImmutableAppendService.java`, `util/DalasResponseBuilder.java`,
and `error/DalasGraphQLExceptionHandler.java`.

#### dalasuuidprovidersvc { #dalasuuidprovidersvc }

**Purpose and fields.** `dalasuuidprovidersvc` owns and generates the
internal `dalasUuid` listing field used by the DALAS source and sink stages.
It is excluded from `publicapi`.

**Core logic and lifecycle.** The listing entity fetchers batch listing IDs
through a non-caching DataLoader and submit one task per listing to
`EvaluationUuidService`, which calls `GuidGenerator.nextGuid()`. A missing
DataLoader falls back to direct UUID generation. The value is built into the
single-SKU or variation entity response; it is not read from a database or
external service.

**Storage, errors, and boundary.** The service has no writes, event flow,
provider-local cache, TTL, persistence, or retryable downstream request. It
generates a fresh GUID at resolution time and ignores the validated listing ID
when generating it, so the source does not establish UUID stability across
separate ULP requests. Validation failures are non-retryable bad-input errors;
generic runtime errors become structured internal errors. It has no CLS/NuDoc
data lineage.

**Evidence.** `dalasuuidprovidersvc/src/main/resources/schema/schema.graphqls`,
`README.md`, `resolver/DalasUuidEvaluationEntityResolver.java`,
`loader/EvaluationUuidBatchLoader.java`,
`service/EvaluationUuidService.java`,
`util/DalasUuidProviderSvcResponseBuilder.java`, and
`error/DalasGraphQLExceptionHandler.java`.

### Provider-to-NuDoc relationship summary

Provider repositories show that "post-listing" does not imply a single
storage technology. The matrix below narrows the data-gap statement to what
the inspected source proves.

| Provider group | Provider-local source | Relationship to CLS core NuDoc |
| --- | --- | --- |
| `BASICLISTINGDATA` | Provider-owned NuData/Monstor document. | Separate application attributes layered on listing/item keys. |
| `CMPLREGULATORYSVC` | `CountryOfOrigin` NuDoc, vendor calls, and vector search. | Separate compliance enrichment. |
| `CONNECTEDPRODUCTSULP` | Provider-owned NuDocument under `connectedProduct.*`. | Separate connected-product modules keyed by item/listing. |
| `DEALSGRAPH` | `DealsULP` NuDoc `__ROOT__`, or a configured fake fetcher. | Separate deal state keyed by listing ID. |
| `DEFAULTULPPROVIDER` | Static example resolver only. | No core or provider data relationship is established. |
| `EBAYPLUSELIGIBILITY` | Precomputed NuKV eligibility entity. | Separate shipping-program result. |
| `ITMVZBLIT` | NuData plus SaleBo; Caty remains source of truth during dual-write. | ULP-enriched visibility, without a CLS docset identified. |
| `LCLISTINGPROVIDER` | NuKV `EbayLive` JSON cache. | Separate eventually consistent live-commerce state. |
| `LOCNMAPPINGSVC` | NuData `ListingLocations` documents. | Separate inventory-topology data keyed by listing/SKU/seller. |
| `MPLS` | `GlobalShippingProgram` Monstor/NuData records. | Separate shipping-program result keyed by listing ID. |
| `PURCHASEVIEWGRAPHSVC` | Request-time COMS aggregation for `listingPurchaseView`. | Separate purchase-view computation; no CLS/NuDoc path shown. |
| `SAPSVC` | SAP classifier results read through Monstor. | Separate derived product/aspect enrichment. |
| `SELLERPORTALSVC` | Provider item-group/item DAO and external inventory/catalog clients. | Core-field or physical-store lineage is not established. |
| `SELLERRISKENTITYSVC` | `DelayedItem` NuDocument in `DELAYED_ITEM_KEYSPACE`. | Separate risk/searchability state. |
| `SEOCORELABSVC` | NuKV SEO cache. | Separate derived image-alt-text lookup. |
| `SLRINVSVC` | Seller-inventory `SKUStatusDAO` read-through. | Separate inventory flags; no CLS/NuDoc path shown. |
| `SVLS` | Request-time CLS read through the SVLS CLS client. | Direct CLS core-listing reconstruction; no field-level NuDoc document lineage is established by SVLS. |
| `ITEMCOMPATIBILITYSVC` | Provider-owned `ItemCompatibility` Monstor/NuData keyspace. | Separate compatibility enrichment keyed by listing ID and core marketplace/category context. |
| `VEHENTSVC` | Provider `MotorsVehicleHistoryReport` and verification NuDocuments, with a CATY fallback for history data. | Separate vehicle-history and verification data, using core listing data to obtain VIN and seller context. |
| `PICKUPELIGIBILITY` | Request-time ULP/Sale conversion and ULOS seller intent/eligibility data; optional ULOS NuDoc comparison. | Computed pickup-program result, not CLS core-listing NuDoc state. |
| `EGDSELLERMGMT` | Provider-owned `EbayGuaranteedDelivery` Monstor/NuData document. | Separate shipping-program enrichment keyed by listing ID. |
| `MDMLUSVCIO` | NuKV item discounts, SME markdown database data, and optional SaleBo backfill. | Separate promotion state; NuKV and SaleBo fallback do not establish CLS NuDoc ownership. |
| `DALASPROXYSOURCESVC` | Request-time external DALAS plugin-orchestration response. | Pipeline enrichment consuming a federated core-listing representation; no provider NuDoc or CLS client. |
| `DALASPROXYSINKSVC` | Request-time external DALAS immutable-append response. | Pipeline enrichment consuming DALAS source/UUID state; no provider NuDoc or CLS client. |
| `DALASUUIDPROVIDERSVC` | Locally generated UUID at federation-resolution time. | Internal DALAS pipeline identity; no persisted source or CLS/NuDoc lineage. |

### Provider-data consumer rules

| Situation | Required interpretation |
| --- | --- |
| A requested provider field is absent or `null` | It can reflect authorization, disabled configuration, environment exclusion, a cache miss, asynchronous calculation, an unavailable provider, or a genuine empty value. Inspect GraphQL errors and the field contract. |
| A core listing is revised | Do not assume all provider groups immediately refresh. Provider data can have an independent event and cache lifecycle. |
| A visibility, risk, availability, or shipping-program field is returned | Use it only for its documented domain use. It is not a universal buyer-eligibility or checkout decision. |
| A provider group appears in schema | Verify the active gateway, provider enablement, generated query template, and source owner before depending on it. |
| A consumer needs provider freshness | Confirm the owning provider's freshness and event contract. The local repositories establish grouping and refresh mechanics, not an end-to-end latency or delivery SLO. |

## 3. ULP and NuDoc data gaps

### The comparison in one view

ULP is a consumer-facing, federated current-listing surface. NuDoc is a
producer-side CLS persistence model. A data gap is therefore often a
difference in purpose rather than a missing field.

| Difference class | What exists | Gap or migration implication |
| --- | --- | --- |
| Shared core-state projection | CLS persists core listing state across NuDoc document families; ULP exposes listing and item concepts through GraphQL. | Assemble the right NuDoc families when using raw data, or use ULP when the GraphQL current-state contract fits. Do not assume one ULP field has one NuDoc storage field. |
| NuDoc-only producer operations | Drafts, history, locks, UUID maps, document keys, compression, archival paths, and targeted write/read boundaries exist in CLS. | Use CLS/NuDoc-oriented interfaces for operational workflows. These states are not established as normal ULP current-listing fields. |
| ULP-only enrichment | Provider groups add derived, domain-owned, and extended data to the ULP response. | Core NuDoc alone cannot reproduce these fields. Locate the mapped provider and confirm its source/freshness contract. |
| Contract and access | GraphQL authorization, gateway tags, group selection, configuration, cache state, and response errors affect ULP availability. | A stored NuDoc value does not imply an API caller can read an equivalent ULP field. |
| Representation and freshness | NuDoc has documents, document IDs, compressed payloads, nested models, and current/history splits; ULP has graph projections and provider caches. | Normalize shape deliberately and handle eventual consistency or delayed enrichment. |

### NuDoc coverage matrix

CLS declares 22 logical document families across current, draft, index, and
revision-history data. The following matrix makes the resulting ULP gaps
explicit.

| NuDoc family | ULP equivalent established by source | Coverage | Reason or constraint |
| --- | --- | --- | --- |
| `ItemKeyspace.__ROOT__` | `ListingV2`/`Item` identity, seller-product, listing-term, and lifecycle families | Family correspondence | ULP may transform, restrict, or assemble fields; exact leaf lineage varies. |
| `ItemKeyspace.ItemQtyPrice` | Item price, quantity, sold quantity, and commercial fields | Directly mapped at document purpose | Monetary nesting and consumer representation can differ. |
| `ItemKeyspace.ItemDescription` | Seller-product/listing description fields | Directly mapped at document purpose | ULP does not expose NuDoc compression as a consumer contract. |
| `ItemKeyspace.ItemCompatibility` | Listing/item compatibility fields | Family correspondence | Optional fields can be excluded from default cache reads until selected. |
| `ItemKeyspace.BusinessPolicies` | Listing/item terms and policy objects | Family correspondence | Field authorization and group/shared ownership can differ. |
| `ItemKeyspace.ItemDetails` | Specialized listing/item details when exposed | Family correspondence | No source proof of complete leaf coverage. |
| `ItemKeyspace.ItemLock` | No normal ULP field established | NuDoc-only | Reservation and lock lifecycle is an operational model. |
| `ItemKeyspace.UuidMap` | No normal ULP field established | NuDoc-only | Seller/UUID lookup is an operational index. |
| `ItemGroupKeyspace.__ROOT__` | MSKU listing/item/variation relationship and shared seller-product state | Family correspondence | Group and variation remain separate business grains. |
| `ItemGroupKeyspace.GroupDescription` | Shared MSKU description | Directly mapped at document purpose | Must not be treated as a duplicated variation description. |
| `ItemGroupKeyspace.GroupBusinessPolicies` | Shared MSKU term/policy state | Family correspondence | Exact ULP field and access depend on the selected contract. |
| `ListingDraft.__ROOT__` | A live `ListingV2` can expose a related `draftId`, but no full draft read is established | NuDoc-only for draft state | A draft is working state, not published current listing data. |
| `ListingDraft.ItemDraft` | No normal ULP current-listing equivalent established | NuDoc-only | Draft SSKU/variation content precedes or differs from live item state. |
| `ListingDraft.ItemDraftCompatibility` | No normal ULP current-listing equivalent established | NuDoc-only | Draft compatibility is not proof of live compatibility. |
| `ListingDraft.ItemGroupDraft` | No normal ULP current-listing equivalent established | NuDoc-only | Draft group structure is not a published MSKU group. |
| `ListingDraft.ItemGroupDraftCompatibility` | No normal ULP current-listing equivalent established | NuDoc-only | Draft-only specialized payload. |
| `ListingDraft.ItemGroupDraftDesc` | No normal ULP current-listing equivalent established | NuDoc-only | Draft-only shared description. |
| `UserListingDraft.UserItemDraftMap` | No normal ULP current-listing equivalent established | NuDoc-only | User-scoped active-draft discovery index. |
| `ListingRevisionKeyspace.__ROOT__` | No normal ULP current-listing equivalent established | NuDoc-only | Revision retention state differs from current state. |
| `ListingRevisionKeyspace.ListingRevision` | No normal ULP current-listing equivalent established | NuDoc-only | Historical summary must not be merged into latest fields without business rules. |
| `ListingRevisionKeyspace.ListingRevisionDetail` | No normal ULP current-listing equivalent established | NuDoc-only | Historical non-variation property detail. |
| `ListingRevisionKeyspace.VariationRevisionDetail` | No normal ULP current-listing equivalent established | NuDoc-only | Historical variation property detail. |

### ULP enrichment absent from CLS core NuDoc evidence

The groups below are ULP-only **relative to the CLS core NuDoc source**. This
does not imply the data is absent from eBay systems; it means the supplied CLS
repository does not establish it as core listing document state.

| ULP enrichment family | Examples | Data-gap conclusion |
| --- | --- | --- |
| Search and visibility | Visible/suppressed sites, searchability times/reasons, risk holds, search hiding. | Requires the visibility/risk provider path; a live NuDoc listing does not establish search visibility. |
| Deals and engagement | Daily-deal data, watch counts, purchase-view metrics. | Requires deal, basic-listing-data, and purchase-view providers. |
| Inventory topology | Warehouse merchant-location keys, consignment, hub fulfillment, pre-authentication. | Requires location-mapping and seller-portal providers. |
| Shipping-program enrichment | eBay Plus and Global Shipping Program eligibility, restricted countries, tariffs, shipment estimation metadata. | Requires eBay Plus and MPLS providers; not a substitute for fulfillment execution. |
| Product and SEO enrichment | Search tagging/aspects, image alt text, derived image metadata. | Requires SAP and SEO providers; do not assume it was seller-authored core content. |
| Compliance and live-commerce enrichment | Country-of-origin confidence and eBay Live event/eligibility state. | Requires regulatory and live-commerce providers. |

### Semantic and operational gaps

Even where ULP and NuDoc represent the same business concept, consumers need
to account for the following differences.

| Topic | NuDoc behavior | ULP behavior | Consumer action |
| --- | --- | --- | --- |
| Storage shape | Separate docsets with service-specific keys and retrieval boundaries. | Nested GraphQL types selected by the client. | Model a consumer entity intentionally; do not expose raw document keys as business fields. |
| SSKU/MSKU | Group data and member variation state are separate. | Listing/item graph can present both concepts. | Preserve group-versus-variation grain in joins, aggregations, and metrics. |
| Optional large data | Description and compatibility can be isolated or compressed. | Fields can be selectively requested and may be excluded from default cached reads. | Request needed fields explicitly and define null/absence handling. |
| History and drafts | Independent families with different identities and lifecycles. | Normal listing reads establish current-state access, not a history/draft API. | Do not replace current listing values with draft or revision data. |
| Provider state | CLS source does not own provider enrichments. | Field groups may be asynchronous, conditional, cached, or unavailable. | Confirm owner, configuration, freshness, and error behavior for each provider field. |
| Authorization | CLS service operations have their own authorization and operational paths. | Schema fields can be gateway- or principal-restricted. | Validate the caller context and inspect GraphQL errors instead of interpreting absence as data loss. |
| Freshness | Core state is written through CLS operational flows. | Cached current-state and provider refresh behavior can be eventually consistent. | Use an owning transactional service for checkout, buyer eligibility, payment, fulfillment, or settlement decisions. |

### Migration guidance

1. **Start from the business question.** Use ULP for a buyer-context-independent
   current listing view plus requested enrichments. Use CLS/NuDoc-oriented
   interfaces for producer operations, drafts, revision history, locks, and
   raw lineage.
2. **Request provider fields deliberately.** Identify the field group and
   mapped provider; then verify the caller's gateway/authorization, enabled
   configuration, and freshness requirements.
3. **Treat a ULP event as a state-change signal.** Retrieve needed current
   fields after an event; do not assume any event carries a complete listing
   snapshot or has legacy BES1 payload parity.
4. **Keep grain and time explicit.** Distinguish listing, sellable item,
   variation group, draft, current state, and revision history. Avoid joins
   that multiply shared MSKU values across sellable variations.
5. **Record unknown lineage as unknown.** An exact ULP-to-NuDoc field map
   requires a field path, relevant CLS converter/reconstructor, ULP mapping or
   response conversion, and any provider evidence. Do not promote a
   name-based guess to documentation.

## Tracing a specific field

Use this sequence when a field needs an exact source or gap classification:

1. **Find its federated contract.** Locate the field in
   `fgql/ext/superSchema` and inspect its `@join__field(graph: ...)`
   ownership. `UNILISTINGSVC` means ULP exposes the field; it does not by
   itself identify the underlying provider or NuDoc docset.
2. **Inspect the ULP schema.** Read the matching type and directives in
   `unilistingsvc/src/main/resources/schema/schema.graphqls` or the FGQL
   `ext/unilistingsvc.graphqls` snapshot. Record deprecation, gateway
   exclusion, authorization, and field documentation.
3. **Resolve a ULP provider group.** Search
   `FieldToFieldGroupMapping.json` for the field path and
   `FieldGroupToSubgraphMapping.json` for the service. Then inspect the
   production `ListingV2ById-onDemandFieldGroup.graphql` template to confirm
   the selected field block and `@include` guard.
4. **Trace core state in CLS.** Search the V2 entity, its use in
   `DocumentConverter` or `ItemGroupDocumentConverter`, and the matching
   reconstruction code such as `GetItemDocumentConverter`. Record the
   NuDoc docset and any transformations such as compression.
5. **Classify the result.** Mark it directly mapped only when the above
   evidence proves the path. Otherwise choose family correspondence,
   ULP-only, NuDoc-only, conditional, or unverified and state what
   repository/configuration is still required.

## Evidence references and limits

| Evidence area | Source artifacts |
| --- | --- |
| CLS core writes and reads | `crlstngsvService/.../processor/DocumentConverter.java`, `ItemGroupDocumentConverter.java`, `GetItemDocumentConverter.java`, `CoreItemProcessor.java`, `CoreItemGroupProcessor.java`, and `nudata/Docset.java`. |
| CLS lifecycle and NuDoc families | `crlstngsv/doc/repository-business-process-walkthrough.md`; [NuData write-flow research](../spike/item-nudata-write-flow.md); [Listing NuData Design](../wiki/Listing_NuData_Design.md). |
| ULP schema and provider grouping | `unilistingsvc/src/main/resources/schema/schema.graphqls`; `onDemand/FieldGroups.json`; `FieldToFieldGroupMapping.json`; `FieldGroupToSubgraphMapping.json`; and the production on-demand query template. |
| ULP selection, caching, and refresh | `FieldOnDemandFieldGroupLookup.java`, `ListingGraphQLQueryBuilder.java`, `MonstorFieldMapper.java`, `FGQLListingDataSource.java`, and `ULPProviderEventConsumer.java`. |
| Federation contract and routing | `fgql/ext/unilistingsvc.graphqls`, `fgql/ext/superSchema`, `src/gateway.ts`, `src/authenticatedDataSource.ts`, and `src/plugin/queryPlanHandler.ts`. |
| Provider output contracts and local behavior | The provider-specific schema, resolver, service, source-client, persistence, and event paths listed in each [provider implementation analysis](#provider-implementation-analyses). |
| Oracle migration and event boundary | [Oracle Caty Item Tables Migration Guide](../wiki/Oracle_Caty_Item_Tables_Migration_Guide.md), together with the FGQL schema and gateway source artifacts above. |

The original NuDoc schema inputs, deployed supergraph, active provider
configuration, physical provider stores, external provider dependencies, event
delivery guarantees, and end-to-end freshness guarantees are outside the
checked-out sources. The linked provider repositories establish their local
implementation behavior, but they do not prove those external or
deployment-time conditions. Confirm them with the owning service before making
an operational, availability, or field-level lineage commitment.
