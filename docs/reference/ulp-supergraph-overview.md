# ULP Supergraph & Stream Data — High-Level Overview

This document synthesizes the 26 subgraph schemas in `data/ulp/supergraph/` and
the 22 Kafka stream samples in `data/ulp/ulp-sample-data/` into a single
reference for consumers of ULP listing data.

---

## 1. What Is ULP?

The **Unified Listing Platform (ULP)** is eBay's federated GraphQL API for
buyer-context-independent listing data. It assembles a composite `ListingV2`
(or `Item`) response from:

- **Core listing state** — written by sellers through CLS (Core Listing Service)
  and stored in NuDoc document families
- **Post-listing enrichment** — derived, computed, or domain-owned data
  contributed by 25+ independent provider subgraphs

The gateway is **FGQL** (Federated GraphQL Gateway), which uses Apollo
Federation v2.3 to compose all provider schemas into a single supergraph and
route queries across subgraphs.

---

## 2. The Stream Format

Every change to a listing or its provider data produces a Kafka message with
four fields:

| Field | Description |
|---|---|
| `metadata` | Listing ID, operation type (`Insert`/`Update`), ULP version counter, marketplace/format/category routing hints |
| `beforeChangePatch` | RFC 6902 JSON Patch describing **exactly what changed** — the relevance filter for consumers |
| `afterchangeDocument` | Gzip + Base64 compressed full listing snapshot |
| `afterchangeDocumentPlain` | Decoded JSON of the same snapshot — ready to consume |

The `afterchangeDocumentPlain.listing` object is the **composite ULP
projection**: it merges core CLS data with all enabled provider fields into one
denormalized document.

### 2.1 Operation Types

| Operation | Meaning | Sample evidence |
|---|---|---|
| `Insert` | Brand-new listing, first ULP event ever (`ulpListingVersionId: "1"`) | offset-1063363648 |
| `Update` | Any change — seller revision, provider refresh, or system event | All other 21 samples |

### 2.2 What Triggers an Update

The `beforeChangePatch` identifies the trigger category:

| Patch path contains | Trigger | Schema owner |
|---|---|---|
| `coreListingVersionId` | Seller revised listing or CLS processed state change | `svls.graphql` |
| `itemEstimatorDataVersion` | GSP ML model version bumped (no seller action) | `mpls.graphql` |
| `visibilitySummary` (remove/add) | Visibility cache cleared or recomputed | `itmvzblit.graphql` |
| `amount` / `quantityAvailable` | Price or quantity change | `svls.graphql` |
| `listingStatus` / `endDate` | Listing ended or renewed | `svls.graphql` |
| `ebayImageUrl` (add) | Seller added photos | `svls.graphql` |
| `excludeShipToLocations` | Seller changed ship-to exclusion list | `svls.graphql` |
| `markdownDiscountDuration` (remove) | Markdown sale ended, price reset | `mdmlusvcio.graphql` |
| `(empty)` | New listing — full document is the initial state | Insert operation |

---

## 3. The Supergraph Architecture

### 3.1 26 Subgraphs — Three Functional Layers

```
┌─────────────────────────────────────────────────────────┐
│  LAYER 1 — CORE LISTING (svls.graphql)                  │
│  Owns: SingleSkuListing, VariationListing, Item,        │
│  FulfillmentTerms, and 50+ listing fields.              │
│  Storage: CLS NuDoc families (ItemKeyspace, etc.)       │
└─────────────────────────────────────────────────────────┘
          ↓ All other subgraphs extend these types
┌─────────────────────────────────────────────────────────┐
│  LAYER 2 — SHIPPING & FULFILLMENT ENRICHMENT            │
│  mpls          → Global Shipping Program eligibility    │
│  ebaypluseligibility → eBay Plus eligibility (AU)       │
│  egdsellermgmt → eBay Guaranteed Delivery eligibility   │
│  pickupeligibility → PUDO eligibility                   │
│  slrinvsvc     → Inventory API hide/ship-to-home flags  │
│  locnmappingsvc → Warehouse location mapping            │
└─────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────┐
│  LAYER 3 — DOMAIN ENRICHMENT                            │
│  basiclistingdata   → Watch counts, expert insight      │
│  itmvzblit          → Visibility (search/site blocking) │
│  itemcompatibilitysvc → Vehicle/parts fitment           │
│  vehentsvc          → Vehicle history reports, VIN      │
│  lclistingprovider  → eBay Live commerce state          │
│  dealsgraph         → Daily deal state                  │
│  purchaseviewgraphsvc → Purchase history metrics        │
│  sapsvc             → Auto-tagged product, df aspects   │
│  cmplregulatorysvc  → Country of origin, energy labels  │
│  sellerriskentitysvc → Risk holds, searchability        │
│  sellerportalsvc    → Consignment/hub-fulfillment flags │
│  mdmlusvcio         → Markdown promotion data           │
│  seocorelabsvc      → Image alt text (accessibility)    │
│  seodatasvc         → SEO meta description, Wikidata    │
│  taxcategoryentity  → Tax category prediction           │
│  dalasproxysourcesvc → DALAS phase 1 (plugin compute)  │
│  dalasproxysinksvc  → DALAS phase 2 (storage manifest) │
│  dalasuuidprovidersvc → DALAS evaluation UUID          │
│  defaultulpprovider → Developer scaffold (not real)     │
└─────────────────────────────────────────────────────────┘
```

### 3.2 Entity Keys — How Federation Composes

Most subgraphs extend existing entities using Federation `@key` directives:

| Entity | Key field | Owned by | Extended by |
|---|---|---|---|
| `SingleSkuListing` / `VariationListing` | `listingId` | `svls` | All 25 other subgraphs |
| `Item` | `itemId` | `svls` | basiclistingdata, sapsvc, sellerportalsvc, locnmappingsvc, mdmlusvcio, taxcategoryentity, itemcompatibilitysvc, seocorelabsvc |
| `FulfillmentTerms` | `listingId` | `svls` | mpls, ebaypluseligibility, egdsellermgmt, pickupeligibility |
| `ShippingProgramEligibility` | `listingId` | mpls/egdsellermgmt | ebaypluseligibility |
| `DalasEvaluation` | `listingId` | dalasproxysourcesvc | dalasproxysinksvc |
| `VehicleListingDetails` | `listingId` | vehentsvc | — |
| `MarkdownSellerPromotion` | `id` / `offerCheckSumId` | mdmlusvcio | — |

### 3.3 `@requires` — The Dependency Graph

Some subgraphs need fields from other subgraphs before they can resolve.
This creates a multi-step query plan inside FGQL:

| Subgraph | Requires from core | Why |
|---|---|---|
| `cmplregulatorysvc` | seller, category, aspects, marketplaceId, sellerProduct | COO determination needs product attributes |
| `itemcompatibilitysvc` | marketplaceId, category.primaryCategory.id | Fitment is marketplace+category specific |
| `taxcategoryentity` | listing.category.primaryCategory.id, listing.marketplace | Tax prediction needs category+market |
| `pickupeligibility` | 15+ fields (marketplace, format, location, seller, fulfillment, items) | PUDO eligibility is a full listing computation |
| `purchaseviewgraphsvc` | seller.legacyUserId | Purchase history scoped per seller |
| `dalasproxysourcesvc` | Entire listing context (30+ fields) | DALAS plugins need full listing snapshot |
| `seocorelabsvc` | photos.ebayPictureUrl | Alt text looked up by photo GUID |
| `seodatasvc` | marketplaceId, sellerProduct.title, category | Wikidata aspect associations need taxonomy context |
| `sellerportalsvc` | sku, listing.listingId | Inventory storage keyed by SKU+listing |
| `locnmappingsvc` | sku, listing.listingId, seller.legacyUserId | Warehouse location keyed by seller+listing+SKU |

### 3.4 Gateway Access Control

The supergraph enforces field visibility through two mechanisms:

**`@exclude(gateways: ["publicapi"])`** — hides fields from the public API:
- All visibility data (ITMVZBLIT)
- All risk/searchability data (SELLERRISKENTITYSVC)
- Country of origin and energy efficiency (CMPLREGULATORYSVC)
- GSP eligibility (MPLS), eBay Plus (EBAYPLUSELIGIBILITY), EGD (EGDSELLERMGMT)
- eBay Live (LCLISTINGPROVIDER)
- Daily deals (DEALSGRAPH)
- Inventory metadata (SELLERPORTALSVC, LOCNMAPPINGSVC, SLRINVSVC)
- Vehicle history details (VEHENTSVC)
- DALAS evaluation (DALASPROXYSOURCESVC)

**Publicly visible** (6 of 26 subgraphs expose anything):
- `svls` — core listing fields, sellerProduct, listingTerms, items
- `basiclistingdata` — watchCount
- `cmplregulatorysvc` — energyEfficiencyInfo (EU label data)
- `mdmlusvcio` — markdown promotion management
- `seodatasvc` — metaDescription
- `taxcategoryentity` — itemTaxCategoryDetails

---

## 4. Provider Field Coverage in Sample Data

Across 22 stream samples (6 marketplaces, 3 Kafka partitions):

| Provider field | Schema source | Present in | Condition |
|---|---|---|---|
| `__typename = SingleSkuListing` | `svls` | 22/22 | All sampled listings are SSKU |
| `schemaVersion = "2.1.0"` | Stream envelope | 22/22 | Current stream schema version |
| `autoRelistTerms` | `svls` | 22/22 | SVLS default field |
| `eligibleForPudo` | `pickupeligibility` | 22/22 | Default group, always computed |
| `visibilitySummary` | `itmvzblit` | 21/22 | Absent only on brand-new Insert |
| `itemCountryOfOrigin` | `cmplregulatorysvc` | 10/22 | After COO determination runs |
| `autoTagProduct` (item) | `sapsvc` | 7/22 | ML product tagging available |
| `watchCount` (item) | `basiclistingdata` | 6/22 | Provider enabled and selected |
| `shippingProgramEligibility` | `mpls` | 5/22 | UK/AU markets (GSP-eligible) |
| `listingCompatibilities` | `itemcompatibilitysvc` | 3/22 | Motors/parts categories |
| `markdownDiscountDuration` (item) | `mdmlusvcio` | 2/22 | During active markdown sale |
| `photosWithAltText` | `seocorelabsvc` | 2/22 | On-demand, SEO-enabled |
| `ebayPlus` eligibility | `ebaypluseligibility` | 1/22 | AU marketplace only |
| `hideFromSearch` / `availableForShipToHome` | `slrinvsvc` | 1/22 | Inventory API listings only |

### 4.1 Notable Observed Events

**Visibility cache cleared** (partition-1, offset-1751):
```
beforeChangePatch: remove /listing/visibilitySummary
→ ITMVZBLIT provider cache invalidated; listing emitted without visibilitySummary
```

**GSP estimator bumped** (partition-1, offset-1752 and partition-23, offset-1063363646):
```
beforeChangePatch: replace /listing/fulfillmentTerms/.../itemEstimatorDataVersion
→ Pitney Bowes ML model updated; seller did nothing; two duplicate path patches
  confirming denormalization (same data in fulfillmentTerms and listingTerms)
```

**Seller revision** (partition-1, offset-1753):
```
beforeChangePatch: replace /listing/coreListingVersionId
→ CLS processed a core listing change; ulpListingVersionId=153018 (153K events total)
```

**Listing ended** (partition-2, offset-1062673273):
```
beforeChangePatch: replace listingStatus → ENDED, replace endDate, remove endListingReason
→ lifecycle state transition captured across both listingLifecycle and listingTerms.lifecycleTerms paths
```

**Markdown sale ended** (partition-2, offset-1062673277 and partition-23, offset-1063363642):
```
beforeChangePatch: remove markdownDiscountDuration, replace amount, remove originalPrice, replace isItemOnSale
→ price reset to base, sale flags cleared across Item and ListingV2 level
```

**Photos added** (partition-2, offset-1062673274 and partition-23, offset-1063363643):
```
beforeChangePatch: add /listing/sellerProduct/images/N/ebayImageUrl (multiple)
→ also patches items[0].itemSellerProduct.images and photos (3 denormalized paths)
```

**Brand-new listing** (partition-23, offset-1063363648):
```
operation: Insert, ulpListingVersionId: "1", beforeChangePatch: []
→ No visibilitySummary (not yet computed); eligibleForPudo=false present immediately
```

---

## 5. Key Structural Patterns

### 5.1 Denormalization Is Intentional

The same data appears in multiple paths within one document. Shipping data
is a clear example:

```
listing.fulfillmentTerms.shippingTerms          ← top-level (deprecated alias)
listing.listingTerms.listingFulfillmentTerms    ← canonical location
listing.listingTerms.listingFulfillmentTerms.shippingProgramEligibility  ← provider data here too
```

This is by design — `svls.graphql` explicitly marks many top-level fields as
`@deprecated(reason: "use listingTerms.x")` while keeping both paths active
for backward compatibility. When `beforeChangePatch` shows two `replace`
operations on identical leaf values, it confirms the denormalization.

### 5.2 Version Layering — Three Clocks

| Version | Field | What it tracks |
|---|---|---|
| ULP version | `metadata.ulpListingVersionId` | Every ULP event (seller + all providers) |
| CLS version | `listing.coreListingVersionId` | Seller/CLS mutations only |
| Item version | `listing.items[0].versionId` | Per-item commercial state |

When `ulpListingVersionId` increments but `coreListingVersionId` is unchanged
(as in the GSP estimator patch), the event was **provider-only** — no seller
action involved. Consumer workflows that only care about seller changes should
filter on `coreListingVersionId` delta.

### 5.3 DALAS Three-Subgraph Pipeline

Three subgraphs collaborate for asynchronous attribute computation:

```
dalasuuidprovidersvc  → generates dalasUuid per resolution (in-memory, not stable)
        ↓
dalasproxysourcesvc   → calls DALAS plugin orchestration with full listing snapshot
                        produces DalasSourceEvaluation { dalasEntityContainerSource }
        ↓
dalasproxysinksvc     → takes source output, produces:
                        dalasStorageManifest (for persistent storage lookup)
                        dalasEntityContainerSink (merged final result, @inaccessible)
```

None of the 22 stream samples contain `dalasEvaluation` — consistent with
`dalasproxysourcesvc.graphql`'s `@exclude(gateways: ["publicapi"])` and its
on-demand nature. DALAS is triggered asynchronously by BES events, not inline.

### 5.4 `ShippingProgramEligibility` — Three Subgraphs, One Path

Three distinct subgraphs all contribute to the same nested path:

```
FulfillmentTerms.shippingProgramEligibility
  .ebayPlus              ← ebaypluseligibility.graphql (AU only)
  .globalShippingProgram ← mpls.graphql (UK only, sunset 2026)
  .ebayGuaranteedDelivery ← egdsellermgmt.graphql (AU + US)
```

In the samples, records with `shippingProgramEligibility` always contain
`globalShippingProgram` (UK/AU listings). The AUD listing (offset-1063363641)
additionally shows `ebayPlus`, the only AU-specific field observed.

### 5.5 Storage Is Invisible to the Schema

NuDoc, NuKV, Monstor, and Oracle appear **zero times** in the 26 GraphQL
schema files as type names or field names. They appear once in a comment URL
in `svls.graphql`. The schema layer is entirely storage-agnostic — the
mapping from GraphQL field to NuDoc family only exists in provider source code
(documented in `docs/reference/ulp-listing-data.md`).

---

## 6. Consumer Decision Guide

### "I need to know if the seller changed something"

Check `beforeChangePatch` for `coreListingVersionId`. If it changed, CLS
processed a seller (or authorized workflow) mutation. If only provider fields
changed (e.g. `itemEstimatorDataVersion`), the seller did nothing.

### "I need the current price and quantity"

Read `listing.items[0].itemTerms.pricingTerms.fixedPrice.original` and
`listing.items[0].itemTerms.availability.quantityAvailable`. These are
`ItemKeyspace.ItemQtyPrice` projected through SVLS. Do **not** use these
as checkout prices — quantity can change outside seller revisions via CAS.

### "I need to know if a listing is searchable"

`listing.visibilitySummary.defaultVisibleSites` (from ITMVZBLIT) tells you
which sites have default visibility. Absence means not yet computed (new
listing) or explicitly cleared. `packedVisibilityString` is for Search/Reco
backends only.

### "I need to know if this listing is part of a deal"

`listing.dealDetails` (from DEALSGRAPH) — null means not a deal. Not
available in public API. `isDailyDeal: false` means an expired past deal.

### "I need to process vehicle listings differently"

Check `listing.vehicleListingDetails` (from VEHENTSVC) — null if not a
vehicle listing. Contains VIN, vehicle history report, and Caramel
verification status.

### "I'm migrating from BES1 events"

Use `beforeChangePatch` to determine which fields changed instead of
processing the full snapshot on every event. The ULP BES2 events
(`ULP.LISTING.NEW`, `ULP.LISTING.UPDATED`, etc.) are not payload-compatible
with legacy BES1 events — implement deduplication logic.

---

## 7. Deprecations and Migrations in Progress

| What | Current state | Target | Deadline |
|---|---|---|---|
| `Item.compatibilities` | Deprecated in schema | `ListingV2.listingCompatibilities` | 2026-09-30 |
| Global Shipping Program (GSP) | Active but schema notes sunset | eBay International Shipping | End of 2026 |
| Top-level `svls` fields (`aspects`, `photos`, `itemCondition`, etc.) | `@deprecated`, `@tag_directive(add: "inaccessible", gateway: "publicapi")` | `sellerProduct.*` equivalents | Active migration |
| `uniqueBuyerCount` in `listingPurchaseView` | `@deprecated` in schema | (field removed in future version) | Unspecified |
| BES1 listing events | Legacy | ULP BES2 events | Active migration |
| Oracle table reads | Being migrated | ULP / NuDoc | Active (H1 2024+) |

---

## 8. Subgraph Quick Reference

| Schema file | Fields added | Entity | Public? | Mutation? |
|---|---|---|---|---|
| `svls` | Core listing (50+ fields), sellerProduct, listingTerms, items | SingleSkuListing, VariationListing, Item, FulfillmentTerms | Partial | No |
| `basiclistingdata` | watchCount, certifiedExpertInsight | Item, Listing | watchCount only | Yes |
| `cmplregulatorysvc` | energyEfficiencyInfo, itemCountryOfOrigin | Listing | energyEfficiency only | No |
| `dalasproxysourcesvc` | dalasEvaluation → DalasSourceEvaluation | Listing | No | No |
| `dalasproxysinksvc` | dalasStorageManifest | DalasEvaluation | No | No |
| `dalasuuidprovidersvc` | dalasUuid | Listing | No | No |
| `dealsgraph` | dealDetails | Listing | No | No |
| `defaultulpprovider` | (scaffold only) | — | No | No |
| `ebaypluseligibility` | shippingProgramEligibility.ebayPlus | FulfillmentTerms | No | No |
| `egdsellermgmt` | shippingProgramEligibility.ebayGuaranteedDelivery | ShippingProgramEligibility | No | No |
| `itemcompatibilitysvc` | listingCompatibilities, Item.compatibilities† | Listing, Item | No | Yes (internal) |
| `itmvzblit` | visibility, visibilitySummary | Listing | No | No |
| `lclistingprovider` | ebayLive | Listing | No | No |
| `locnmappingsvc` | Item.inventoryLocations | Item | No | No |
| `mdmlusvcio` | Item.markdownDiscountDuration, MarkdownSellerPromotion | Item | Yes | Yes |
| `mpls` | shippingProgramEligibility.globalShippingProgram | FulfillmentTerms | No | No |
| `pickupeligibility` | eligibleForPudo | Listing | No | No |
| `purchaseviewgraphsvc` | listingPurchaseView | Listing | No | No |
| `sapsvc` | Item.autoTagProduct, Item.dfAnnotatedAspects | Item | No | No |
| `sellerportalsvc` | Item.ebayInventoryStorageMetadata | Item | No | No |
| `sellerriskentitysvc` | listingSearchabilityInfo | Listing | No | No |
| `seocorelabsvc` | photosWithAltText | Listing, Item | No | No |
| `seodatasvc` | metaDescription, wikidataTaxonomyAspectValueAssociations | Listing | metaDescription | Yes (internal) |
| `slrinvsvc` | hideFromSearch, availableForShipToHome | Listing | No | No |
| `taxcategoryentity` | Item.itemTaxCategoryDetails | Item | Yes | No |
| `vehentsvc` | vehicleListingDetails (VHR, VIN, verification) | Listing | No | No |

† `Item.compatibilities` deprecated 2026-09-30; use `listingCompatibilities`
