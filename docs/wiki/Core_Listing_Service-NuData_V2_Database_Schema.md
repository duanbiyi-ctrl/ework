# Core Listing Service - NuData V2 Database Schema

Source wiki: <https://wiki.corp.ebay.com/spaces/LS/pages/2269021212/Core+Listing+Service+-+NuData+V2+Database+Schema>

## Overview

This page documents the NuData (NoSQL) database schema used by the Core Listing Service V2 APIs. The service uses four primary keyspaces to store item data, item groups (MSKU/variations), listing drafts, and revision history.

!!! note
	This documentation covers V2 API entities only. V1 legacy entities are not included.

## Architecture Overview

### High-Level Keyspace Relationships

The four keyspaces and their interactions:

- `listingdraftkeyspace` (PK: `draftId`) - Contains draft data before publishing
	- `__ROOT__` - Draft metadata
	- `ItemDraft` (N) - Individual item drafts
	- `ItemGroupDraft` - MSKU group drafts
	- Referenced by: `itemkeyspace.__ROOT__.drftId` and `itemgroupkeyspace.__ROOT__.grpDrftId`
- `itemkeyspace` (PK: `itemId`) - Stores individual items (both single SKU and MSKU variations)
	- `__ROOT__` - Core item data (`isVariation=false` for single SKU, `true` for MSKU child)
	- `ItemQtyPrice` - Quantity and pricing (HOT path)
	- `ItemDescription` - Item description text
	- `BusinessPolicies`, `ItemCompatibility`, `ItemLock`, `UuidMap`, `ItemDetailsDoc`
- `itemgroupkeyspace` (PK: `groupId`) - Stores MSKU parent/group information
	- `__ROOT__` - Group metadata with `itemIds[]` array referencing variations in `itemkeyspace`
	- `GroupDescription` - Group-level description
	- Contains `itmsVryBy[]` defining variation structure (e.g., Color, Size)
- `listingrevisionhistorykeyspace` (PK: `lstgId`) - Revision tracking
	- `__ROOT__` - Container (`lstgId` can be `itemId` or `groupId`)
	- `ListingRevision` (N) - High-level revision info
	- `ListingRevisionDetail` (N) - Field-level changes
	- `VariationRevisionDetail` (N) - MSKU variation changes

### Data Flow Patterns

#### Single SKU Listing Flow

- Create draft: `POST /v2/listing_draft` -> `listingdraftkeyspace` (`__ROOT__` + `ItemDraft`)
- Publish listing: `POST /v2/item` -> `itemkeyspace` (`__ROOT__` + `ItemQtyPrice` + `ItemDescription` + `BusinessPolicies`)
- Revise listing: `PUT /v2/item/{itemId}` -> `itemkeyspace` (update `__ROOT__`, increment `vrsnId`) + `listingrevisionhistorykeyspace` (`ListingRevision` + `ListingRevisionDetail`)

#### MSKU/Multi-Variation Listing Flow

- Create MSKU draft: `POST /v2/listing_draft` (with variations) -> `listingdraftkeyspace` (`__ROOT__` + `ItemGroupDraft` + N `ItemDrafts`)
- Publish MSKU: `POST /v2/item_group` -> `itemgroupkeyspace` (`__ROOT__` + `GroupDescription`) + `itemkeyspace` (N variation documents, each with `isVariation=true`)
- Revise MSKU: `PUT /v2/item_group/{groupId}` -> updates group and/or specific variations + records revision history (`ListingRevision` + `ListingRevisionDetail` + `VariationRevisionDetail`)

#### Example: T-Shirt MSKU with 2 Colors x 3 Sizes = 6 Variations

- 1 document in `itemgroupkeyspace`: `groupId="G100"`, `itemIds=["200001","200002","200003","200004","200005","200006"]`, `itmsVryBy=[{name:"Color", values:["Red","Blue"]}, {name:"Size", values:["S","M","L"]}]`
- 6 documents in `itemkeyspace`: `itemIds` 200001-200006, each with `isVariation=true` and specific aspect values (e.g., `Color=Red`, `Size=S`)

### Access Patterns by Frequency

High Frequency (Hot Path):

- `ItemQtyPrice` - Read/Write on every purchase, price update
- Item `__ROOT__` - Read for item display, write for revisions
- `ItemGroup` `__ROOT__` - Read for MSKU display

Medium Frequency:

- `ItemDescription` - Read for item display (cached), rarely updated
- `GroupDescription` - Read for MSKU display (cached), rarely updated
- `BusinessPolicies` - Read when policies referenced, updated occasionally

Low Frequency (Cold Path):

- `ItemCompatibility` - Read only for parts fitment, rarely updated
- `ListingRevision*` - Write on every revision, read only for history queries
- `ItemLock` - Read/Write only during concurrent update conflicts
- `UuidMap` - Read only during draft validation
- `ItemDetailsDoc` - Read only when seller documents attached

## Keyspace Architecture

The Core Listing Service uses the following NuData keyspaces:

- `itemkeyspace` - Stores individual item/listing data (single SKU and variations)
- `itemgroupkeyspace` - Stores item group data for MSKU/multi-variation listings
- `listingdraftkeyspace` - Stores listing draft data before publishing
- `listingrevisionhistorykeyspace` - Stores revision history for listing changes

## 1. Item Keyspace (`itemkeyspace`)

The itemkeyspace stores all individual item data. Each item is stored as a document family with multiple document types (collections) for different aspects of the item.

Primary Key: `PK = itemId` (eBay item ID)

### `__ROOT__` Collection [HOT - Read/Write]

- Core item data (static/slowly changing): `itemId` (PK), `sellerId`, `uuid`, `vrsnId`, `drftId`, `title`, `category`, `epid`, `conditionId`, `format`, `lifecycle`
- Media and classification: `aspects[]`, `images[]`, `videos[]`, `location`, `policies`
- `isVariation` flag: `false` = single SKU, `true` = MSKU child variation
- Foreign keys: `drftId` -> `listingdraftkeyspace.__ROOT__.draftId`
- Implicitly referenced by: `itemgroupkeyspace.__ROOT__.itemIds[]` (if `isVariation=true`)

Child Collections:

- `ItemQtyPrice` [HOT - Read/Write]: Frequently updated data - `availQty`, `qtySold`, `fixedPrice`, `mrktngPrc`
- `ItemDescription` [WARM - Read]: Large text data - `desc`, `compDesc`, `descRevsnDt`
- `BusinessPolicies` [WARM - Read]: Policy details - `retTrms`, `pmtTrms`, `shipTrms`
- `ItemCompatibility` [COLD - Read]: Parts fitment - `compat[]`, `cmpCompat`
- `ItemLock` [COLD - Read/Write]: Concurrency control
- `UuidMap` [COLD - Read]: UUID to ItemId mapping
- `ItemDetailsDoc` [COLD - Read]: Seller documents

Read Patterns:

- Get Item by ID: PK lookup on `__ROOT__` + parallel fetch `ItemQtyPrice`, `ItemDescription`
- Get MSKU Variations: Batch PK lookup for all `itemIds` from `ItemGroup.itemIds[]`
- Update Price/Qty: Direct write to `ItemQtyPrice` collection

Write Patterns:

- Create Item: Write `__ROOT__`, `ItemQtyPrice`, `ItemDescription`, `BusinessPolicies` atomically
- Update Item: Write `__ROOT__` (increment `vrsnId`), update specific collections
- End Item: Update `__ROOT__.endRsn`, `__ROOT__.admEndDt`

## 2. Item Group Keyspace (`itemgroupkeyspace`)

The itemgroupkeyspace stores multi-variation listings (MSKU). Each item group contains metadata about the variation structure and references to individual variation items.

Primary Key: `PK = groupID`

### Collection Structure

#### `__ROOT__` Collection [HOT - Read/Write]

- Group metadata: `groupId` (PK), `groupTitle`, `groupType`, `owner`, `grpVrs`, `grpDrftId`
- `itemIds[]`: Array of variation item IDs (references to `itemkeyspace` documents where `isVariation=true`)
- `itmsVryBy[]`: Variation structure definition - Example: `[{name:"Color", values:["Red","Blue"]}, {name:"Size", values:["S","M","L"]}]`
- Image rules: `imgVryBy` (which traits control images), `images[]` (group-level images)
- Seller references: `sellerGroupKey` (seller's custom group SKU)
- Foreign keys: `grpDrftId` -> `listingdraftkeyspace.__ROOT__.draftId`

Child Collections:

- `GroupDescription` [WARM - Read]: Large text data - `groupDesc`, `compDesc`, `grpDescRevsnDt`

MSKU Variation Relationship:

`ItemGroup.__ROOT__` with `groupId="G100"` and `itemIds=["200001","200002","200003"]` references 3 variation documents in `itemkeyspace`, each with `isVariation=true`. The `itmsVryBy[]` field defines the variation structure (e.g., Color, Size), and each variation's `aspects[]` field contains the specific trait values (e.g., `Color=Red`, `Size=S`).

Read Patterns:

- Get MSKU:
	1. PK lookup on `ItemGroup` `__ROOT__` to get `itemIds[]` and `itmsVryBy[]`
	2. Batch PK lookup on `itemkeyspace` for all `itemIds[]`
	3. Fetch `GroupDescription`
- Display Variation Matrix: Parse `itmsVryBy[]` and match `aspects[]` from each variation

Write Patterns:

- Create MSKU:
	1. Write `ItemGroup` `__ROOT__` + `GroupDescription`
	2. Write N variation documents in `itemkeyspace` (all with `isVariation=true`)
- Add Variation:
	1. Create new item in `itemkeyspace`
	2. Append `itemId` to `ItemGroup.itemIds[]`
- Update Group Title: Update `ItemGroup.__ROOT__.groupTitle`
- Update Variation Price: Update specific item's `ItemQtyPrice` in `itemkeyspace`

### Relationship: Item Group -> Items

Parent-Child Relationship:

- `ItemGroup` `__ROOT__` contains `itemIds` array with all variation item IDs
- Each variation is stored as a separate document in `itemkeyspace`
- Variations have `isVariation=true` flag in their item `__ROOT__` document
- The `itmsVryBy` field defines variation traits (e.g., Color, Size)
- Individual variations store their specific trait values in their `aspects` field

Example MSKU Structure:

A t-shirt with Color (Red, Blue) and Size (S, M, L) variations:

- 1 `ItemGroup` document with `groupId="100001"`
- `itemIds = ["200001", "200002", "200003", "200004", "200005", "200006"]`
- `itmsVryBy = [{"name":"Color","values":["Red","Blue"]}, {"name":"Size","values":["S","M","L"]}]`
- 6 `Item` documents in `itemkeyspace` (one per variation combination)

## 3. Listing Draft Keyspace (`listingdraftkeyspace`)

The listingdraftkeyspace stores draft listings before publication. Drafts can be for single items or item groups (MSKU).

Primary Key: `PK = draftId`

### Collection Structure

#### `__ROOT__` Collection [WARM - Read/Write]

- Draft metadata: `draftId` (PK), `itmId[]` (published item IDs after publish), `lstdItmId` (published listing ID), `origItmId` (original item ID for relist/revise)
- Lifecycle: `crtDate`, `lastModDate`, `prgDt` (purge date), `lstgTm` (listing time)
- Referenced by: `itemkeyspace.__ROOT__.drftId` and `itemgroupkeyspace.__ROOT__.grpDrftId`

Child Collections:

- `ItemDraft` (N) [WARM - Read/Write]: Individual item drafts - Similar structure to Item `__ROOT__`, with `desc` inline (not separate). For Single SKU: 1 `ItemDraft`. For MSKU: N `ItemDrafts` (one per variation)
- `ItemGroupDraft` [WARM - Read/Write]: MSKU group draft - `grpTtl`, `itmsVryBy[]`, `imgsVryBy`, `slrGrpKey`, `bizPol`
- `ItemGroupDraftDesc` [WARM - Read]: Group description for draft

Draft to Published Item Flow:

- Single SKU: `listingdraftkeyspace` (`__ROOT__` + `ItemDraft`) -> `itemkeyspace` (`__ROOT__` + collections)
- MSKU: `listingdraftkeyspace` (`__ROOT__` + `ItemGroupDraft` + N `ItemDrafts`) -> `itemgroupkeyspace` (`__ROOT__`) + `itemkeyspace` (N variations)

### 3.1. `__ROOT__` Collection

The main draft document containing draft session metadata and flags.

- `PK`: String - Draft ID (Primary Key)
- `itmId`: `List<String>` - Item IDs if draft was published
- `lstgTm`: Long - Listing time
- `origItmId`: String - Original item ID for relist/revise
- `lstdItmId`: String - Published listing ID
- `prgDt`: Long - Purge date
- `totCumLstgs`: Long - Total cumulative listings
- `crtDate`: Long - Creation date
- `lastModDate`: Long - Last modified date
- `qtySold`: Integer - Quantity sold
- `itmRevsnDt`: Long - Item revision date
- `descRevsnDt`: Long - Description revision date

- Draft Session Flags: `lstgTmpltFls`, `mnMxFls`, `ryiStat`, `scrtchFl` (1-4)

- Item Flags (Bitmap): `fl` (1-12), `pwdEx`, `props`, `saleStat`, `visitCnt`, `shipRgn`

- Scratch Details: Various legacy fields for draft management

### 3.2. `ItemDraft` Collection

Stores draft data for individual items or variations.

PK: `itemDraftId`

Contains similar fields to Item __ROOT__ collection plus:

- `currPrc`: Amount - Current price (for auction items)
- `fl01`: Long - Variation-specific flags
- `prodDtls`: Boolean - Product details selection
- `brnd`: String - Brand
- `desc`: String - Description (inline in draft)
- `cmpDesc`: `byte[]` - Compressed description

### 3.3. `ItemGroupDraft` Collection

Stores draft data for item groups (MSKU).

- `PK`: String - Group draft primary key
- `grpId`: String - Published group ID if exists
- `grpTtl`: String - Group title
- `itmsVryBy`: `List<NameValuesPair>` - Items vary by traits
- `imgsVryBy`: ImagesVaryBy - Images vary by
- `img`: `List<ImageMap>` - Group images
- `slrGrpKey`: String - Seller group key
- `bizPol`: BusinessPolicies - Business policies

### 3.4. `ItemGroupDraftDesc` Collection

Stores group description for draft item groups.

## 4. Listing Revision History Keyspace (`listingrevisionhistorykeyspace`)

The listingrevisionhistorykeyspace stores revision history tracking for listing changes.

Primary Key: `lstgId` (Listing ID - can be `itemId` or `groupId`)

### Collection Structure

#### `__ROOT__` Collection [COLD - Read/Write]

- Container: `lstgId` (PK) - Can be `itemId` (single SKU) or `groupId` (MSKU)
- Referenced by: `itemkeyspace.__ROOT__.itemId` and `itemgroupkeyspace.__ROOT__.groupId`

Child Collections:

- `ListingRevision` (N) [COLD - Read/Write]: High-level revision info - `vrsnId` (version number), `rvsdDate` (revision timestamp), `rvsdPrptyGrps[]` (changed property groups like `PRICE_QUANTITY`, `DESCRIPTION`, `TITLE`), `appId`, `sigRevCnt`, `vrsnCrtd`
- `ListingRevisionDetail` (N) [COLD - Read/Write]: Field-level change details - `rvsdPrptyGrp`, `rvsdPrpty` (specific field like `TITLE`, `FIXED_PRICE`), `chgTp` (`ADDED`/`MODIFIED`/`DELETED`), `newVal`, `oldVal`. One record per changed field in the revision
- `VariationRevisionDetail` (N) [COLD - Read/Write]: Variation-specific changes (MSKU only) - `varId` (variation item ID), `rvsdVarPrpty` (`VAR_FIXED_PRICE`, `VAR_AVAILABLE_QUANTITY`, etc.), `chgTp`, `newVal`, `oldVal`, `varTraitVals` (e.g., `"Color=Red,Size=Large"`). One record per variation per changed field

Revision History Examples:

Single SKU Revision (Change title and price):

```text
ListingRevision: vrsnId=2, rvsdPrptyGrps=[TITLE, PRICE_QUANTITY]
ListingRevisionDetail #1: rvsdPrpty=TITLE, chgTp=MODIFIED, oldVal="Nike Shoes Size 10", newVal="Nike Air Max Shoes Size 10"
ListingRevisionDetail #2: rvsdPrpty=FIXED_PRICE, chgTp=MODIFIED, oldVal="99.99 USD", newVal="89.99 USD"
```

MSKU Revision (Change group title + Red-Large variation price):

```text
ListingRevision: vrsnId=3, rvsdPrptyGrps=[GROUP_TITLE, PRICE_QUANTITY]
ListingRevisionDetail: rvsdPrpty=GROUP_TITLE, chgTp=MODIFIED, oldVal="T-Shirt Collection", newVal="Premium T-Shirt Collection"
VariationRevisionDetail: varId="200006", rvsdVarPrpty=VAR_FIXED_PRICE, chgTp=MODIFIED, oldVal="19.99 USD", newVal="17.99 USD", varTraitVals="Color=Red,Size=Large"
```

### 4.1. `__ROOT__` Collection

- `lstgId`: String - Listing ID (Primary Key)

### 4.2. `ListingRevision` Collection

Stores high-level revision information.

- `vrsnId`: Long - Version ID
- `rvsdDate`: Long - Revised date timestamp
- `rvsdPrptyGrps`: `List<RevisedPropertyGroupEnum>` - Revised property groups
- Examples: `PRICE_QUANTITY`, `DESCRIPTION`, `TITLE`, `CATEGORY`, etc.
- `appId`: Long - Application ID that made the revision
- `sigRevCnt`: Integer - Significant revision count
- `vrsnCrtd`: Boolean - Version created flag
- `updCrLstgVrs`: String - Updated core listing version

### 4.3. `ListingRevisionDetail` Collection

Stores detailed field-level changes for each revision.

- `rvsdPrptyGrp`: RevisedPropertyGroupEnum - Property group
- `rvsdPrpty`: RevisedPropertyEnum - Specific property changed
- Examples: `TITLE`, `FIXED_PRICE`, `AVAILABLE_QUANTITY`, `DESCRIPTION`, etc.
- `chgTp`: ChangeTypeEnum - Type of change: `ADDED`, `MODIFIED`, `DELETED`
- `newVal`: String - New value
- `oldVal`: String - Old value
- `lbl`: String - Label/display name

### 4.4. `VariationRevisionDetail` Collection

Stores detailed variation-level changes for MSKU revisions.

- `varId`: String - Variation ID (the item ID of the variation)
- `rvsdPrptyGrp`: RevisedPropertyGroupEnum - Property group
- `rvsdVarPrpty`: RevisedVariationPropertyEnum - Variation property changed
- Examples: `VAR_FIXED_PRICE`, `VAR_AVAILABLE_QUANTITY`, `VAR_SKU`, etc.
- `chgTp`: ChangeTypeEnum - Type of change
- `newVal`: String - New value
- `oldVal`: String - Old value
- `varTraitVals`: String - Variation trait values for identification
- Example: `"Color=Red,Size=Large"`

## Key Data Relationships

### Single SKU Listing Flow

- Draft created -> Document in `listingdraftkeyspace` with `ItemDraft` collection
- Draft published -> Document in `itemkeyspace` with `__ROOT__`, `ItemQtyPrice`, `ItemDescription` collections
- Item revised -> New `ListingRevision` and `ListingRevisionDetail` documents in `listingrevisionhistorykeyspace`

### MSKU/Multi-Variation Listing Flow

- Draft created -> Document in `listingdraftkeyspace` with `ItemGroupDraft` + multiple `ItemDraft` collections
- Draft published:
	- One document in `itemgroupkeyspace` (`__ROOT__`, `GroupDescription`)
	- N documents in `itemkeyspace` (one per variation, each with `isVariation=true`)
- MSKU revised -> `ListingRevision` + `ListingRevisionDetail` (for group changes) + `VariationRevisionDetail` (for variation changes)

### Foreign Key Relationships

- Item -> Draft: `Item.drftId` references `ListingDraft.draftId`
- ItemGroup -> Draft: `ItemGroup.grpDrftId` references `ListingDraft.draftId`
- ItemGroup -> Items: `ItemGroup.itemIds` contains array of `Item.itemId`
- Item -> Variation Flag: `Item.isVariation=true` indicates this item belongs to an `ItemGroup`
- Revision History -> Item: `ListingRevision.lstgId` can be either `Item.itemId` or `ItemGroup.groupId`
- VariationRevisionDetail -> Item: `VariationRevisionDetail.varId` references `Item.itemId`

## Data Storage Patterns

### Compression Strategy

Large text fields are often stored in compressed format:

- `ItemDescription.compDesc` - Compressed description
- `ItemCompatibility.cmpCompat` - Compressed compatibility data
- `GroupDescription.compDesc` - Compressed group description

### Separation of Concerns

The schema separates frequently-updated data from static data:

- Static data: `__ROOT__` collections (title, category, creation info)
- Dynamic data: `ItemQtyPrice` (quantity, price changes)
- Large data: `ItemDescription`, `GroupDescription` (separated for performance)
- Complex data: `ItemCompatibility`, `BusinessPolicies` (policy details)

### Denormalization

Some data is intentionally denormalized for query performance:

- Core item fields are stored in `__ROOT__` even though they could be references
- Draft data duplicates published item structure for independent draft management
- Revision history stores both old and new values for complete audit trail

## Query Patterns

- Get Item by ID: Primary key lookup in `itemkeyspace` using `itemId`
- Get Item Group (MSKU) by ID: Primary key lookup in `itemgroupkeyspace` using `groupId`, then batch fetch all variations from `itemkeyspace` using `itemIds` array
- Get Revision History: Primary key lookup in `listingrevisionhistorykeyspace` using `itemId` or `groupId`
- UUID Uniqueness Check: Lookup in `itemkeyspace` `UuidMap` collection

## Additional Notes

### Field Name Abbreviations

NuData field names use abbreviations to reduce storage size. Examples:

- `aspct` = `aspects`
- `avlQty` = `availableQuantity`
- `bizPol` = `businessPolicies`
- `cndDesc` = `conditionDescription`
- `itmLocn` = `itemLocation`
- `lstgAppId` = `listingApplicationId`

### Type Definitions

Complex types (Amount, Duration, Format, etc.) are defined in the sellingDomainCommonLib module and shared across the application.

## Related Documentation

- Core Listing Service V2
- Listing Services Overview

Last Updated: May 31, 2026

Author: Core Listing Service Team