# NuData write-flow research

## Scope and answer

This is a repository-scoped walkthrough of `crlstngsv`. In this document,
“NuDoc” means the NuData/MonStor document classes and docsets represented by
this repository. The repository does not use SQL DDL for these stores; it
builds JSON documents and sends MonStor `RequestFactory` insert, upsert, update,
and delete mutations.

There are **22 declared logical docsets** in the source:

| Keyspace family | Logical docsets | Count |
| --- | --- | ---: |
| `ItemKeyspace` | `__ROOT__`, `ItemCompatibility`, `ItemDescription`, `ItemQtyPrice`, `ItemDetails`, `BusinessPolicies`, `UuidMap`, `ItemLock` | 8 |
| `ItemGroupKeyspace` | `__ROOT__`, `GroupDescription`, `GroupBusinessPolicies` | 3 |
| `ListingDraft` | `__ROOT__`, `ItemDraft`, `ItemGroupDraft`, `ItemDraftCompatibility`, `ItemGroupDraftCompatibility`, `ItemGroupDraftDesc` | 6 |
| `UserListingDraft` | `UserItemDraftMap` | 1 |
| `ListingRevisionKeyspace` | `__ROOT__`, `ListingRevision`, `ListingRevisionDetail`, `VariationRevisionDetail` | 4 |
| **Total** |  | **22** |

For ordinary live data writes, the item create/replace family writes six
docsets, item-group create/replace writes three, an SSKU draft writes two or
three documents and an MSKU draft writes three plus one `ItemDraft` per
variation, or four plus one when group compatibility is present, active
user-draft indexing writes one, and a revision insert writes one to three
document types. `UuidMap` and `ItemLock` are auxiliary item
docsets. Archive hold/version fallback writes the root docset in an archive
keyspace. Therefore, “22 tables” is the schema declaration count, not the
number of documents written by every request.

If a keyspace-qualified sink is counted only when a write is proven in code,
there are **24 sink pairs**:

* 8 in live `ItemKeyspace`;
* 3 in live `ItemGroupKeyspace`;
* 6 in `ListingDraft`;
* 1 in `UserListingDraft`;
* 4 in `ListingRevisionKeyspace`;
* 1 archive pair, `ItemKeyspaceArchive/__ROOT__`;
* 1 archive pair, `ItemGroupKeyspaceArchive/__ROOT__`.

The archive keyspaces reuse the item and group schema classes, so they add two
physical keyspace/docset sinks but no new logical docset class. The count does
not claim that all 24 sinks are touched by one business operation.

## 1. End-to-end producer flow

The common path is:

```text
REST resource or V1 dual-write trigger
  -> validation and processor selection
  -> V2 model-to-NuData document converter
  -> ancestor/child key construction
  -> transactional MonStor mutation
  -> later multi-docset get/query response
```

The V2 resources call processors directly. V1 listing and draft resources
first pass through `DualWriteProcessor` or `DraftDualWriteProcessor`; those
processors convert legacy payloads to V2 models and decide whether the NuData
write is asynchronous, synchronous, parallel, or disabled by a ramp/config
gate. A successful V2 write is not evidence that Oracle/Caty was or was not
also written; those systems are outside this document's count.

The persistence boundary is a set of documents under an item, group, draft,
user, or listing-revision ancestor. `DocumentConverter`,
`ItemGroupDocumentConverter`, and `DraftDocumentConverter` construct the
content. The processors then use MonStor `InsertRequest`,
`BatchMutateRequest`, `UpdateRequest`, or `DeleteRequest`, generally with
transactional options for multi-document operations. Consumers read current
item and group state with multi-docset gets, read drafts through draft
queries/gets, read active drafts through `UserItemDraftMap`, and read revision
history through ancestor queries.

## 2. Schema, key layout, field inventory, and model lineage

`Docset` is the repository's schema abstraction: a Java class represents a
NuData collection and `getCollectionName()` returns the collection name
(`crlstngsvService/src/main/java/com/ebay/app/cls/nudata/Docset.java`).
Nested helper classes such as `Price`, `Lifecycle`, `TermsAndPolicies`, and
`ShippingTerms` are fields inside a document; they are **not separate
docsets**.

### Item family: `ItemKeyspace`

The root key is `KeyFactory.create(itemId)`. The child documents are descendants
of that root:

```text
itemId
├── ItemCompatibility / COMPAT_<itemId>
├── ItemDescription / DESC_<itemId>
├── ItemQtyPrice / QTY_PRICE_<itemId>
├── BusinessPolicies / BIZ_POL_<itemId>
├── ItemDetails / ITEM_DETAILS_<itemId>
└── ItemQtyPrice / ItemLock / LOCK_<lockId>
```

The lock-summary document is also in `ItemLock`, beneath the item quantity and
price key, with the reserved summary identifier
`LOCK_$$$SUMMARY$$$`. `UuidMap` uses a different key shape:
`UUID_<sellerId>/<uuid>` with a `UUID_MAP` child.

| Docset | Document role and representative fields |
| --- | --- |
| `__ROOT__` | Core listing state: `PK`, title, category, lifecycle, seller/listing identifiers, location, images, policies/terms references, version/revision fields, `onHold`, `endRsn`, and other item-level state. `DocumentConverter.getRoot()` maps the V2 `Item` into this document. |
| `ItemCompatibility` | Fitment/compatibility payload: `ItemCompID`, `compat` or compressed `cmpCompat`, and `ftExempt`. |
| `ItemDescription` | Description payload: `ItemDescID`, `desc` or compressed `compDesc`, and `descRevsnDt`. |
| `ItemQtyPrice` | Inventory and commercial values: `availQty`, `qtySold`, `price`, and `minRmntSet`; price contains fixed, auction, marketing, original-retail, cost-of-goods, and price-guarantee data. |
| `ItemDetails` | Additional item details such as `hasRlxdRls`, high-precision fixed/start prices, source listing, and supporting documents. |
| `BusinessPolicies` | Policy content: policy identifiers plus return, payment, and shipping terms. |
| `UuidMap` | UUID/seller lookup value containing `listingId` and `listingAppId`; used to resolve or anonymize a listing mapping. |
| `ItemLock` | Reservation/lock documents with `pk`, status (`A`, `C`, `X`), quantity, expiration, timestamps, and UUID; the summary record stores aggregate reserved quantity. |

The six-document item create/replace set is:
`__ROOT__`, `ItemCompatibility`, `ItemDescription`, `ItemQtyPrice`,
`ItemDetails`, and `BusinessPolicies`. The `UuidMap` and `ItemLock` documents
are not part of the normal item payload mutation.

#### ItemKeyspace elaboration

`ItemKeyspace` is the current-state store for one individual listing item.
`__ROOT__` holds the broad item state, while the child docsets isolate
compatibility, description, quantity/price, details, and business-policy
content that can be updated independently. `UuidMap` and `ItemLock` support
lookup and reservation workflows rather than representing additional
top-level item payloads. Consumers should use the item root as the identity
anchor and treat child documents as parts of the same item state, not as
independent listings.

### Relationship between `ItemKeyspace` and `ItemGroupKeyspace`

These are separate keyspace families with separate ancestors and separate
root documents. `ItemKeyspace` stores the individual item or variation
records; `ItemGroupKeyspace` stores the multi-variation group identity,
membership, shared traits, group description, and group-level policies. For an
MSKU group, the group root's `itemIds` identifies its member item roots, and
the item root's `grpId` points back to the group. This is a logical
relationship, not a parent-child key relationship across keyspaces.

The two families therefore have different write responsibilities: item
operations write variation/listing state such as quantity, price, lifecycle,
description, and item compatibility, while group operations write membership,
variation traits, group description, and group policies. A consumer must read
both families to reconstruct a complete MSKU listing; a group document alone
does not contain the full variation-level commercial state, and an item
document alone does not establish the complete group membership.

#### Single-SKU versus one-variation MSKU

The repository distinguishes SSKU versus MSKU by the listing's MSKU flag, not
by counting variation records:

| Listing condition | `ItemKeyspace` result | `ItemGroupKeyspace` result |
| --- | --- | --- |
| SSKU (`saleBo.isMsku()` is false) | One ordinary item document family is created or updated. | No `ItemGroup` record is created; `getItemGroupFromListing(...)` returns null. |
| MSKU with one active/non-deleted variation | One item record is created for that variation. Its `groupId` points to the parent listing/group ID. | The MSKU group is still created with `__ROOT__`, `GroupDescription`, and `GroupBusinessPolicies`; the group root's `itemIds` contains exactly that one variation item ID. |
| MSKU with multiple active/non-deleted variations | One item record is created per active variation. | The same group docsets are created, and `itemIds` contains all active variation item IDs. |

For the one-variation MSKU case, the group record is therefore not omitted or
collapsed into the item record. The group ID is the parent listing ID, while
the sole `itemIds` value is the separate variation item ID. A consumer should
not infer “SSKU” merely because `itemIds` has length one; it must use the
listing's MSKU classification and the presence of the group record.

### Item-group family: `ItemGroupKeyspace`

The group root is `KeyFactory.create(groupId)`. Child keys are descendants:

```text
groupId
├── GroupDescription / GROUP_DESC_<groupId>
└── GroupBusinessPolicies / BIZ_POL_<groupId>
```

| Docset | Document role and representative fields |
| --- | --- |
| `__ROOT__` | Group identity and membership: `PK`, title, `itemIds`, seller/group key, variation traits, images, group version, group draft ID, and administrative/lifecycle fields. |
| `GroupDescription` | Group description, optionally compressed, with `groupDescId` and `grpDescRevsnDt`. |
| `GroupBusinessPolicies` | Group-level business policies. It extends the business-policy model but returns the group-specific collection name. |

`CoreItemGroupProcessor` creates or upserts all three documents
transactionally. Group shipping updates touch the root and
`GroupBusinessPolicies`; description updates touch the root and
`GroupDescription`.

#### ItemGroupKeyspace elaboration

`ItemGroupKeyspace` is the current-state store for an item group, most notably
the shared structure of an MSKU listing. Its root describes the group and its
member IDs; `GroupDescription` and `GroupBusinessPolicies` hold independently
addressable group content. `GroupBusinessPolicies` uses the group collection
name even though its fields inherit the item policy schema, so it must not be
counted as the item `BusinessPolicies` docset. Group-level state also does not
replace the item-level documents for the group's variations.

### Listing-draft family: `ListingDraft`

The draft root is keyed by `draftId`. The processor uses prefixes such as
`GROUP_`, `GROUPDESC_`, `GROUPCOMPAT_`, `ITEM_`, and `COMPAT_`. The key
relationship is:

```text
draftId
├── ItemDraft / ITEM_<draftId>                 (SSKU)
├── ItemDraftCompatibility / COMPAT_<draftId>  (optional SSKU)
├── ItemGroupDraft / GROUP_<draftId>            (MSKU)
├── ItemGroupDraftDesc / GROUPDESC_<draftId>   (MSKU)
├── ItemGroupDraftCompatibility / GROUPCOMPAT_<draftId> (optional MSKU)
└── ItemDraft / ITEM_<draftId>_<variationId>   (MSKU variations)
```

| Docset | Document role and representative fields |
| --- | --- |
| `__ROOT__` | Draft session, flags, scratch details, draft/creation/revision dates, and the list of MSKU variation IDs. |
| `ItemDraft` | SSKU or variation content including title, description, price, quantity, seller, listing terms, categories, images, and revision fields. |
| `ItemGroupDraft` | MSKU group title, images, variation traits, seller group key, business policies, and group ID. |
| `ItemDraftCompatibility` | Optional SSKU compatibility payload, compressed when configured. |
| `ItemGroupDraftCompatibility` | Optional MSKU group compatibility payload, compressed when configured. |
| `ItemGroupDraftDesc` | MSKU group description, optionally compressed, plus description revision date. |

An SSKU draft normally writes two or three docsets: root, item, and optional
item compatibility. An MSKU draft writes root, group, group description,
optional group compatibility, and one or more `ItemDraft` variation documents.
The variation count changes the number of documents, not the number of logical
docsets.

#### ListingDraft elaboration

`ListingDraft` is a working-state store for listing construction before or
during publication. SSKU drafts use item documents, while MSKU drafts add a
group root, group description, optional group compatibility, and one item
document per variation. Draft documents are not proof that a live
`ItemKeyspace` or `ItemGroupKeyspace` listing exists; they are a separate
content model and lifecycle.

### User active-draft family: `UserListingDraft`

`UserItemDraftMap` is keyed below a user root and draft identifier. Its
representative fields are `draftId`, marketplace/application identifiers,
category, title, image URLs, creation mode/date, user ID, and
`lastModifiedDate`. It is a separate index/map from the content in
`ListingDraft`; updating or deleting one does not imply that the other is
automatically changed unless the caller invokes both flows.

#### UserListingDraft elaboration

`UserListingDraft` is an index for finding active drafts by user. Its
`UserItemDraftMap` document contains summary metadata and lookup identifiers,
not the complete draft payload. It can therefore be created, updated, or
deleted independently of the corresponding `ListingDraft` content, subject to
the caller's dual-write behavior.

### Revision-history family: `ListingRevisionKeyspace`

The listing ID is the ancestor. A normal insert creates a generated child key
for `ListingRevision`, then generated child keys for optional details:

```text
listingId
└── ListingRevision / generated-guid
    ├── ListingRevisionDetail / generated-guid (zero or more)
    └── VariationRevisionDetail / generated-guid (zero or more)
```

`ListingRevision` contains revised property groups, version/application
identifiers, significant revision count, revised date, and updated core-listing
version. Detail documents contain revised group/property, change type, old/new
values, and (for variation details) variation traits/ID.

The declared revision root class exists as a schema class and is queried by
the revision-history code, but `RevisionHistoryNudataClient.addForInsert()`
explicitly does not create a root document in the normal insert path. A
separate expired-date upsert path can create/update that root, so it remains a
declared and conditional write target rather than a normal revision-insert
target.

#### ListingRevisionKeyspace elaboration

`ListingRevisionKeyspace` is historical rather than current-state storage.
`ListingRevision` records a revision summary under a listing ancestor, and
detail children record property-level changes, including variation-specific
changes. A revision document should be interpreted as an event/history record,
not as a replacement for the latest `ItemKeyspace` or `ItemGroupKeyspace`
state. The declared revision root is an exception: it participates in
expired-date maintenance but is intentionally omitted from ordinary revision
inserts.

### Detailed field schema and source-model lineage

The following inventory lists the JSON properties declared directly on each
docset class. Java types are included where they clarify whether a field is a
scalar, list, enum, or embedded object. Fields inside embedded objects are not
repeated as docsets: for example, `ItemKeyspace/__ROOT__.category` is a
`Category` value containing category fields, but `Category` is not another
NuData collection. The source classes use Jackson annotations, so the JSON
property names below are the persisted names, not necessarily the Java member
names. For item and item-group docsets, each table also includes the
write-side source property or expression.

#### `ItemKeyspace/__ROOT__`

The item root is the broadest item document. It combines listing identity,
seller/location, lifecycle, category, policy references, flags, and item
features.

| JSON field | Java type | Source `Item` property or write-side mapping |
| --- | --- | --- |
| `aspects` | `List<Aspects>` | `Item.aspects` -> `getDbAspects(...)` |
| `autoRlstTerms` | `AutoRelistTerms` | `Item.autoRelistTerms` -> `getDbAutoRelistTerms(...)` |
| `category` | `Category` | Derived from `Item.primaryCategoryId`, `secondaryCategoryId`, `storePrimaryCategoryId`, and `storeSecondaryCategoryId` through `getDbCategory(...)` |
| `charity` | `Charity` | `Item.charity` -> `getDbCharity(...)` |
| `conditionDesc` | `String` | `Item.conditionDescription` |
| `conditionId` | `String` | `Item.conditionId` |
| `eBayGenTitle` | `String` | `Item.eBayGeneratedTitle` |
| `itmLocn` | `String` | `Item.itemLocation` |
| `itmLocnPostlCd` | `String` | `Item.itemLocationPostalCode` |
| `listingAppId` | `String` | `Item.listingApplicationId` |
| `autoRlstOrigAppId` | `String` | `Item.autoRelistOriginalAppId` |
| `slrAppData` | `String` | `Item.sellerApplicationData`; empty values are normalized to null |
| `mktplcLstdOn` | `String` | `Item.marketplaceListedOn` |
| `notes` | `String` | `Item.notes` |
| `PK` | `String` | `Item.itemId` |
| `sellerId` | `String` | `Item.sellerId` |
| `slrItemKey` | `String` | `Item.sellerItemKey` |
| `title` | `String` | `Item.title` |
| `uuid` | `String` | `Item.uuid` |
| `epid` | `String` | `Item.epid` |
| `drftId` | `String` | `Item.draftId` |
| `crLstgDtVrs` | `String` | `Item.coreListingDataVersion` |
| `vrsnId` | `String` | `Item.versionId` |
| `ftmtId` | `String` | `Item.fitmentId` |
| `vehPkgId` | `String` | `Item.vehiclePackageId` |
| `lotId` | `String` | `Item.lotId` |
| `prdGallryFallbckURL` | `String` | `Item.productGalleryFallbackURL` |
| `grpId` | `String` | `Item.groupId` |
| `lstgCrtCltIp` | `String` | `Item.listingCreationClientIp` |
| `cndIdNum` | `Integer` | `Item.conditionIdNumber` |
| `lotSize` | `Integer` | `Item.lotSize` |
| `sigRevCnt` | `Integer` | `Item.significantRevisionCount` |
| `httpsCmplt` | `Integer` | `Item.httpsCompliant` |
| `cndDescriptors` | `List<ConditionDescriptor>` | `Item.conditionDescriptors` |
| `images` | `List<ImageMap>` | `Item.images` -> `ImageMapConverter.getDbImageMapList(...)` |
| `gblIdentifiers` | `List<NameValuesPair>` | `Item.globalIdentifiers` |
| `vhclIdentifiers` | `List<NameValuesPair>` | `Item.vehicleIdentifiers` |
| `videos` | `List<String>` | `Item.videos` |
| `creationMode` | `CreationMode` | `Item.creationMode` |
| `format` | `Format` | `Item.format` |
| `itmLocnCntry` | `CountryEnum` | `Item.itemLocationCountry` |
| `invntryTrkMthd` | `InventoryTrackingMethod` | `Item.inventoryTrackingMethod` |
| `endRsn` | `EndReason` | `Item.endReason` |
| `scndChncItm` | `Boolean` | `Item.secondChanceItem` |
| `eBayVlt` | `Boolean` | `Item.ebayVault` |
| `hidePrtcptn` | `Boolean` | `Item.hideParticipation` |
| `mngByInv` | `Boolean` | `Item.manageByInventory` |
| `buyerRstDsbld` | `Boolean` | `Item.buyerRestrictionsDisabled` |
| `prtnrLstdAutoDlrItm` | `Boolean` | `Item.partnerListedAutosDealerItem` |
| `isVhclSbscrpItm` | `Boolean` | `Item.isVehicleSubscriptionItem` |
| `IncEbyPrdtDtail` | `Boolean` | `Item.includeeBayProductDetails` |
| `IncStkPhtoUrl` | `Boolean` | `Item.includeStockPhotoUrl` |
| `itmOnSale` | `Boolean` | `Item.isItemOnSale` |
| `onHold` | `Boolean` | `Item.isOnHold()`; also changed by `CoreItemProcessor.updateHoldStatus(...)` |
| `bidsFl` | `Boolean` | `Item.getBidsFinalized()` |
| `sellerPOverridn` | `Boolean` | `Item.getSellerProfileOverridden()` |
| `isScheduled` | `Boolean` | `Item.getIsScheduled()` |
| `isSellerOnVacation` | `Boolean` | `Item.getSellerOnVacation()` |
| `isRestrictedToBusinessUser` | `Boolean` | `Item.getRestrictedToBusinessUser()` |
| `isBuyerResponsibleForShipping` | `Boolean` | `Item.getBuyerResponsibleForShipping()` |
| `isListedWithNoContactViaEmailSupport` | `Boolean` | `Item.getListedWithNoContactViaEmailSupport()` |
| `isBusinessPolicyItem` | `Boolean` | `Item.getBusinessPolicyItem()` |
| `isRestrictedBidding` | `Boolean` | `Item.getRestrictedBidding()` |
| `isSCOStatusIndicator` | `Boolean` | `Item.getIsSCOStatusIndicator()` |
| `isCreatedBySellSimilar` | `Boolean` | `Item.getIsCreatedBySellSimilar()` |
| `isVariation` | `Boolean` | `Item.getIsVariation()` |
| `isSemiPrsBin` | `Boolean` | `Item.getIsSemiPersistentBin()` |
| `lifecycle` | `Lifecycle` | Derived from `Item.duration`, `endDate`, `scheduledEndDate`, `isScheduled`, `startDate`, and `duplicateAuction` through `getDbLifecycle(...)` |
| `sprtCntct` | `SupportContact` | `Item.supportContact` -> `getDbSupportContact(...)` |
| `trmsAndPolicies` | `TermsAndPolicies` | Derived from best-offer, buyer-restriction, fulfillment, minimum-remnant, policy-identifier, and warranty properties |
| `trdScp` | `TradingScope` | `Item.tradingScope` -> `getDbTradingScope(...)` |
| `vslEncmt` | `VisualEnhancements` | `Item.visualEnhancements` -> `getDbVisualEnhancements(...)` |
| `tax` | `Tax` | `Item.tax` -> `getDbTax(...)` |
| `ebayCmnty` | `EbayCommunity` | `Item.ebayCommunity` -> `getDbEbayCommunity(...)` |
| `epr` | `ExtendedProducerResponsibility` | `Item.extendedProducerResponsibility` -> `getDbExtendedProducerResponsibility(...)` |
| `cstmPol` | `CustomPolicies` | `Item.customPolicies` -> `getDbCustomPolicies(...)` |
| `rgltryInfo` | `RegulatoryInfo` | `Item.regulatoryInfo` -> `getDbRegulatoryInfo(...)` |
| `PrmnlDtls` | `PromotionalDetails` | `Item.promotionalDetails` -> `getDbPromotionalDetails(...)` |
| `outOfStockDt` | `Long` timestamp | `Item.outOfStockDate` -> `DateUtil.getTimeWithoutMilliSec(...)` |
| `lastModDate` | `Long` timestamp | `Item.lastModifiedDate` |
| `crtDate` | `Long` timestamp | `Item.creationDate` |
| `itmRevsnDt` | `Long` timestamp | `Item.itemRevisionDate` -> `DateUtil.getTimeWithoutMilliSec(...)` |
| `admEndDt` | `Long` timestamp | Update-only administrative end timestamp; not assigned by `DocumentConverter.getRoot(...)` |
| `rlstPrntId` | `String` relist identifier | `Item.relistParentId` |
| `rlstId` | `String` relist identifier | `Item.relistId` |
| `prgSpprtd` | `List<ProgramsSupported>` | `Item.programsSupported` |

#### `ItemKeyspace/ItemCompatibility`

| JSON field | Java type | Role and source mapping |
| --- | --- | --- |
| `ItemCompID` | `String` | Child document identifier; generated as `COMPAT_<itemId>` |
| `compat` | `List<com.ebay.cls.v2.entities.ItemCompatibility>` | Expanded compatibility values from `Item.compatibilities` |
| `cmpCompat` | `byte[]` | Compressed `Item.compatibilities` payload selected by `CompressionHelper` |
| `ftExempt` | `Integer` | `Item.fitmentThresholdExempt` |

`compat` and `cmpCompat` are alternative representations selected by the
compression helper; they are not normally both populated for the same payload.

#### `ItemKeyspace/ItemDescription`

| JSON field | Java type | Role and source mapping |
| --- | --- | --- |
| `desc` | `String` | Expanded description from `Item.description` |
| `ItemDescID` | `String` | Child document identifier; generated as `DESC_<itemId>` |
| `compDesc` | `byte[]` | Compressed `Item.description` payload selected by `CompressionHelper` |
| `descRevsnDt` | `Long` | `Item.descriptionRevisionDate` |

#### `ItemKeyspace/ItemQtyPrice`

| JSON field | Java type | Role and source mapping |
| --- | --- | --- |
| `availQty` | `Integer` | `Item.availableQuantity` |
| `ItemQtyPriceID` | `String` | Child document identifier; generated as `QTY_PRICE_<itemId>` |
| `price` | `Price` | Derived from `Item.auctionReservePrice`, `fixedPrice`, `marketingPrice`, `startingBidPrice`, `originalItemPrice`, `costOfGoods`, and `enrolledInPriceGuarantee` |
| `qtySold` | `Integer` | `Item.quantitySold` |
| `minRmntSet` | `Integer` | `Item.minimumRemnantSet` |
| `qtySldByPickpStre` | `Integer` | Legacy pickup-store quantity flow updates this directly from `SaleBo`/variation data; it is not assigned by `DocumentConverter.getQtyPrice(...)` |

#### `ItemKeyspace/ItemDetails`

The Java schema class is `ItemDetailsDoc`, whose collection name is
`ItemDetails`.

| JSON field | Java type | Role and source mapping |
| --- | --- | --- |
| `itemDetailsID` | `String` | Child document identifier; generated as `ITEM_DETAILS_<itemId>` |
| `hasRlxdRls` | `Boolean` | `Item.hasRelaxedRules` |
| `fixedPriceHP` | `Amount` | `Item.fixedPriceWithHighPrecision` |
| `strtBidPriceHP` | `Amount` | `Item.startingBidPriceWithHighPrecision` |
| `docs` | `Documents` | `Item.documents` -> `getV2Documents(...)` |
| `srcLstId` | `String` | `Item.sourceListingId` |

#### `ItemKeyspace/BusinessPolicies`

| JSON field | Java type | Role and source mapping |
| --- | --- | --- |
| `plcsId` | `String` | Policy-set identifier; generated as `BIZ_POL_<itemId>` |
| `retTrms` | `ReturnTerms` | `Item.businessPolicies.returnTerms` -> `getReturnTerms(...)` |
| `pmtTrms` | `PaymentTerms` | `Item.businessPolicies.paymentTerms` -> `getPaymentTerms(...)` |
| `shipTrms` | `ShippingTerms` | `Item.businessPolicies.shippingTerms` -> `getShippingTerms(...)` |

#### `ItemKeyspace/UuidMap`

| JSON field | Java type | Role and source mapping |
| --- | --- | --- |
| `listingId` | `String` | Listing resolved from a seller/UUID key; explicit UUID operation argument |
| `listingAppId` | `String` | Listing application identifier; explicit UUID operation argument |

The seller ID and UUID are part of the key shape, not fields in this document.

#### `ItemKeyspace/ItemLock`

| JSON field | Java type | Role and source mapping |
| --- | --- | --- |
| `pk` | `String` | Lock identifier from `NormalizedLockRequest.lockId` |
| `st` | `ItemLockStatus` | `A` active, `C` committed, `X` cancelled; created as `ACTIVE` and changed by lock lifecycle operations |
| `qty` | `long` | Locked/reserved quantity from `NormalizedLockRequest.quantity` |
| `expDt` | `long` | Expiration timestamp from `NormalizedLockRequest.expirationDate` |
| `cmtDt` | `Long` | Commit timestamp set by lock commit lifecycle |
| `cnclDt` | `Long` | Cancellation timestamp set by lock cancel lifecycle |
| `extDt` | `Long` | Extension timestamp set by lock extension lifecycle |
| `extCnt` | `Long` | Extension count set by lock extension lifecycle |
| `crtDt` | `long` | Creation timestamp from `NormalizedLockRequest.creationDate` |
| `modDt` | `Long` | Last-modified timestamp from `NormalizedLockRequest.creationDate` on create |
| `uuid` | `String` | Reservation UUID from `NormalizedLockRequest.uuid` |

The summary lock uses the same schema with the reserved lock ID
`LOCK_$$$SUMMARY$$$`; its quantity is the aggregate reserved quantity.

#### `ItemGroupKeyspace/__ROOT__`

| JSON field | Java type | Source `ItemGroup` property or write-side mapping |
| --- | --- | --- |
| `PK` | `String` group identifier | `ItemGroup.groupId` |
| `createdDt` | `Long` timestamp | `ItemGroup.creationDate` |
| `lastmodifiedDt` | `Long` timestamp | Processor-supplied `lastModifiedDate` argument; create/upsert currently passes the current time |
| `admEndDt` | `Long` timestamp | Update-only administrative end timestamp; read back into `ItemGroup.adminEndedDate` but not assigned by the create root converter |
| `owner` | `String` | `ItemGroup.groupOwner` |
| `groupTitle` | `String` | `ItemGroup.groupTitle` |
| `groupType` | `String` | `ItemGroup.groupType` |
| `sellerGroupKey` | `String` | `ItemGroup.sellerGroupKey` |
| `grpVrs` | `String` | `ItemGroup.groupVersion` |
| `grpDrftId` | `String` | `ItemGroup.groupDraftId` |
| `images` | `List<ImageMap>` | `ItemGroup.images` -> `ImageMapConverter.getDbImageMapList(...)` |
| `itemIds` | `List<String>` | `ItemGroup.itemIds` |
| `itmsVryBy` | `List<NameValuesPair>` | `ItemGroup.itemsVaryBy` |
| `imgVryBy` | `ImagesVaryBy` | `ItemGroup.imagesVaryBy` -> `getImagesVaryBy(...)` |
| `compat` | `List<ItemCompatibility>` | Expanded `ItemGroup.compatibilities` |
| `cmpCompat` | `byte[]` | Compressed `ItemGroup.compatibilities` payload selected by `CompressionHelper` |
| `mFulfillmentSprt` | `Boolean` | `ItemGroup.managedFulfillmentSupported` |
| `globalIdentifiers` | `List<NameValuesPair>` | `ItemGroup.globalIdentifiers` |
| `httpsCmplt` | `Integer` | `ItemGroup.httpsCompliant` |

#### `ItemGroupKeyspace/GroupDescription`

| JSON field | Java type | Role and source mapping |
| --- | --- | --- |
| `groupDesc` | `String` | Expanded group description from `ItemGroup.groupDescription` |
| `compDesc` | `byte[]` | Compressed `ItemGroup.groupDescription` payload selected by `CompressionHelper` |
| `groupDescId` | `String` | Child document identifier; generated as `GROUP_DESC_<groupId>` |
| `grpDescRevsnDt` | `Long` | `ItemGroup.groupDescriptionRevisionDate` |

#### `ItemGroupKeyspace/GroupBusinessPolicies`

`GroupBusinessPolicies` extends `ItemKeyspace/BusinessPolicies`; it declares no
new fields. It therefore has `plcsId`, `retTrms`, `pmtTrms`, and `shipTrms`,
but uses the collection name `GroupBusinessPolicies`.

| JSON field | Java type | Source `ItemGroup` property or write-side mapping |
| --- | --- | --- |
| `plcsId` | `String` | Policy-set identifier; generated as `BIZ_POL_<groupId>` |
| `retTrms` | `ReturnTerms` | `ItemGroup.businessPolicies.returnTerms` -> `getReturnTerms(...)` |
| `pmtTrms` | `PaymentTerms` | `ItemGroup.businessPolicies.paymentTerms` -> `getPaymentTerms(...)` |
| `shipTrms` | `ShippingTerms` | `ItemGroup.businessPolicies.shippingTerms` -> `getShippingTerms(...)` |

#### `ListingDraft/__ROOT__`

Draft root fields are grouped in the source as draft session, draft-session
flags, item flags, and scratch details.

| JSON field | Java type |
| --- | --- |
| `PK` | `String` draft identifier |
| `itmId` | `List<String>` item/variation identifiers |
| `lstgTm`, `prgDt`, `totCumLstgs`, `lastModDate`, `crtDate`, `qtySold`, `itmRevsnDt`, `descRevsnDt` | `Long` |
| `origItmId`, `lstdItmId`, `appCstmInfo`, `autoRlstOrigAppId`, `galPicMd5Hsh`, `galUrl`, `itmVisOpt`, `slfHstdPic`, `slfHstdPicMap` | `String` |
| `usrItmPrpKey` | `Long` |
| `lstgTmpltFls`, `mnMxFls`, `ryiStat`, `scrtchFl`, `scrtchFl2`, `scrtchFl3`, `scrtchFl4`, `ftmtCnt` | `Integer` |
| `fl`, `fl2`, `fl3`, `fl4`, `fl5`, `fl6`, `fl7`, `fl8`, `fl9`, `fl10`, `fl11`, `fl12`, `pwdEx`, `props`, `saleStat`, `visitCnt`, `shipRgn`, `bidCnt`, `mkdnSaleItmPrcRev`, `pbpElig`, `prmSaleEndDt`, `prmSaleStrtDt`, `thFl` | `Long` |
| `usgHistDtl`, `strCatIds` | `List<NameValuePair>` / `List<String>` |
| `strdFixdPrc` | `Boolean` |
| `lstgMthd` | `ListingMethodType` |
| `pplIcnTp` | `PaypalIconType` |

`lastModDate`, `crtDate`, `qtySold`, `itmRevsnDt`, and `descRevsnDt` are
explicitly declared in addition to the session/scratch fields; they are not
derived solely from the child documents.

#### `ListingDraft/ItemDraft`

`ItemDraft` is the largest draft child schema. It stores the item or one MSKU
variation, including content, price, inventory, seller, policy identifiers,
and listing metadata.

| JSON field | Java type |
| --- | --- |
| `PK`, `brnd`, `eBGenTtl`, `epid`, `ftmtId`, `itmId`, `itmLoc`, `itmLocPstCd`, `lstgAppId`, `lstCrtClntIp`, `mpn`, `notes`, `origItmId`, `origPstCd`, `rlstId`, `rlstPrntId`, `slrAppData`, `slrItmKey`, `ttl`, `uuid`, `vrsId`, `vehPkgId`, `lotId`, `srcLstId` | `String` |
| `aspct` | `List<Aspects>` |
| `auctRsvPrc`, `currPrc`, `fxdPrc`, `fxdPrcHP`, `origItmPrc`, `strtBidPrc`, `strtBidPrcHP`, `COGs` | `Amount` |
| `autoRlsTrm`, `bstOfrTrm`, `buyrRst`, `bizPol`, `chrty`, `ffTrm`, `mktPrc`, `slr`, `tax`, `trdScp`, `visEnh`, `epr`, `cstmPol`, `rgltryInfo`, `docs` | Embedded objects (`AutoRelistTerms`, `BestOfferTerms`, `BuyerRestrictions`, `BusinessPolicies`, `Charity`, `FulfillmentTerms`, `MarketingPrice`, `Seller`, `Tax`, `TradingScope`, `VisualEnhancements`, `ExtendedProducerResponsibility`, `CustomPolicies`, `RegulatoryInfo`, `Documents`) |
| `avlQty`, `buyrRstDsbld`, `cndIdNum`, `lotSz`, `minRmntSet`, `qtySold`, `sigRevCnt`, `ftExempt` | `Integer` |
| `fl01` | `Long` variation flag |
| `itmOrd` | `Long` variation order |
| `cndDesc`, `desc`, `cmpDesc`, `cndDescriptors`, `cndId`, `crtDt`, `crtMd`, `endDt`, `drtn`, `eBayVlt`, `fmt`, `glbId`, `hidePrt`, `img`, `eBProdDtls`, `prodDtls`, `stckPhtUrl`, `invTrkMth`, `itmLocCtry`, `lstModDt`, `mktPlLstdOn`, `oosDt`, `pymtPlcyId`, `primCatId`, `prdSpptd`, `rtrnsPlcyId`, `schdEndDt`, `scndCatId`, `scndChncItm`, `shipPlcyId`, `strtDt`, `stPrimCatId`, `stScndCatId`, `itmOnSale`, `itmRevsnDt`, `descRevsnDt`, `videos`, `ebayCmnty`, `vehId` | See source types below |

For the final grouped row, the source types are: `cndDesc`, `desc`,
`cndId`, `itmLoc`, and similar text values are `String`; `cmpDesc` is
`byte[]`; dates are `Long`; `drtn` is `Duration`; `fmt`, `invTrkMth`, and
`crtMd` are enums; `glbId`, `prdSpptd`, `vehId`, `videos`, and `img` are
lists; `pymtPlcyId`, `rtrnsPlcyId`, and `shipPlcyId` are
`BusinessPolicyIdentifier`; and the Boolean flags retain their Boolean
types. This grouping keeps the table readable without changing the declared
JSON field names.

#### `ListingDraft/ItemDraftCompatibility`

`ItemDraftCompatibility` extends `BaseDraftCompatibility` and declares no
additional fields. Its inherited schema is:

| JSON field | Java type |
| --- | --- |
| `DraftCompID` | `String` |
| `compat` | `List<com.ebay.cls.v2.entities.ItemCompatibility>` |
| `cmpCompat` | `byte[]` |

#### `ListingDraft/ItemGroupDraft`

| JSON field | Java type |
| --- | --- |
| `PK` | `String` |
| `grpTtl` | `String` |
| `imgsVryBy` | `ImagesVaryBy` |
| `img` | `List<ImageMap>` |
| `itmsVryBy` | `List<NameValuesPair>` |
| `slrGrpKey`, `grpId` | `String` |
| `bizPol` | `BusinessPolicies` |

#### `ListingDraft/ItemGroupDraftCompatibility`

`ItemGroupDraftCompatibility` also extends `BaseDraftCompatibility` and
declares no additional fields. It has the same `DraftCompID`, `compat`, and
`cmpCompat` schema as `ItemDraftCompatibility`, but uses the collection name
`ItemGroupDraftCompatibility`.

#### `ListingDraft/ItemGroupDraftDesc`

| JSON field | Java type | Role |
| --- | --- | --- |
| `groupDesc` | `String` | Expanded group description |
| `cmpDesc` | `byte[]` | Compressed group description |
| `PK` | `String` | Group-description document identifier |
| `grpDescRevsnDt` | `Long` | Group-description revision timestamp |

#### `UserListingDraft/UserItemDraftMap`

The Java class is `UserListingDraftMap`; its collection name is
`UserItemDraftMap`.

| JSON field | Java type |
| --- | --- |
| `draftId`, `mktPlLstdOn`, `lstgAppId`, `primCatId`, `eBGenTtl`, `ttl`, `imgUrl`, `stockImgUrl`, `userId` | `String` |
| `crtMd` | `DraftCreationModeEnum` |
| `crtDt`, `lastModifiedDate` | `Long` |

#### `ListingRevisionKeyspace/__ROOT__`

| JSON field | Java type | Role |
| --- | --- | --- |
| `lstgId` | `String` | Listing identifier on the revision root |

The normal revision insert does not create this root document; the TTL
maintenance operation upserts it with `expiredDate`, which is an operational
field written by that path even though it is not declared as a Java property on
the root schema class.

#### `ListingRevisionKeyspace/ListingRevision`

| JSON field | Java type | Role |
| --- | --- | --- |
| `rvsdPrptyGrps` | `List<RevisedPropertyGroupEnum>` | Revised property groups |
| `vrsnId` | `Long` | Listing revision version |
| `appId` | `Long` | Application identifier |
| `sigRevCnt` | `Integer` | Significant revision count |
| `vrsnCrtd` | `Boolean` | Whether the version was created |
| `rvsdDate` | `Long` | Revision timestamp |
| `updCrLstgVrs` | `String` | Updated core-listing version |

#### `ListingRevisionKeyspace/ListingRevisionDetail`

| JSON field | Java type | Role |
| --- | --- | --- |
| `rvsdPrptyGrp` | `RevisedPropertyGroupEnum` | Revised property group |
| `rvsdPrpty` | `RevisedPropertyEnum` | Revised property |
| `chgTp` | `ChangeTypeEnum` | Change type |
| `newVal`, `oldVal`, `lbl` | `String` | New value, old value, and display label |

#### `ListingRevisionKeyspace/VariationRevisionDetail`

| JSON field | Java type | Role |
| --- | --- | --- |
| `varId` | `String` | Variation identifier |
| `rvsdPrptyGrp` | `RevisedPropertyGroupEnum` | Revised property group |
| `rvsdVarPrpty` | `RevisedVariationPropertyEnum` | Revised variation property |
| `chgTp` | `ChangeTypeEnum` | Change type |
| `newVal`, `oldVal`, `varTraitVals` | `String` | New value, old value, and variation trait values |

#### Field-schema interpretation

* The lists above are **top-level persisted properties** from the repository's
  Java schema classes. They are not a promise that every property is present
  on every document; converters may omit null values, and update paths may
  set or unset only a subset.
* `compat`/`cmpCompat` and `desc`/`compDesc` show the repository's expanded
  versus compressed representation choice.
* `BusinessPolicies` is reused by item, group, and draft models as an
  embedded object, while `GroupBusinessPolicies` is the separate group
  docset that inherits the same four top-level policy fields.
* The four classes named `__ROOT__` are different schemas in different
  packages. Their matching class names do not make them one shared
  collection across keyspaces.
* `getCollectionName()` is the authoritative logical collection name in the
  source. The revision classes return their fully qualified Java class name,
  while the revision constants and mutation code use the short docset names
  `ListingRevision`, `ListingRevisionDetail`, and
  `VariationRevisionDetail`.

#### Write-side lineage notes

The mappings in these tables follow the write-side converters, not just
matching names by convention. A derived mapping means the JSON field is
assembled from multiple model properties or converted to a NuData-specific
embedded type. An update-only mapping is not populated by the standard
create/replace converter; it is changed by a separate processor mutation.

The item root also has direct update methods that bypass full model conversion.
For example, category updates set the nested category fields, price/quantity
updates set selected root and child fields, and media updates set
`images`/`prdGallryFallbckURL`-related root state. Therefore, the tables describe
the full-document source model while partial operations may update only a
subset.

The group root and child documents also have partial update paths that can
change selected fields without reconstructing the entire `ItemGroup` payload.

## 3. Operation-to-docset write matrix

The matrix describes docset families, not individual documents. “Optional”
means the request shape or operation determines whether the mutation is
included.

| Business operation | NuData mutation and docsets |
| --- | --- |
| Create/replace V2 item | Insert or upsert six item docsets: `__ROOT__`, `ItemCompatibility`, `ItemDescription`, `ItemQtyPrice`, `ItemDetails`, `BusinessPolicies`. Reconcile variants can omit `ItemDetails` or gate compatibility updates. |
| Bulk replace items | Calls the same item upsert path independently/asynchronously per item, so the same six-docset family is possible for each item. |
| Item compatibility update | Upsert `ItemCompatibility` only. |
| Item description/revision update | Update item `__ROOT__` revision/version fields and `ItemDescription`. |
| Item price/quantity/inventory update | Update `ItemQtyPrice` and usually `__ROOT__`; may also update `BusinessPolicies` for payment fields and upsert `ItemDetails` for high-precision/detail state. |
| Quantity/lifecycle inventory update | Update `ItemQtyPrice` and `__ROOT__` for quantities, scheduled/end dates, end reason, and core-listing version. |
| Shipping/policy update | Update item `__ROOT__` and `BusinessPolicies`; group equivalent updates touch group `__ROOT__` and `GroupBusinessPolicies`. |
| Category/media/version/administrative item update | Usually update item `__ROOT__`; category, media, hold, duplicate, relist, HTTPS, and related fields are root fields. MSKU variants use batch root updates. |
| Item lock create/reactivate/commit/cancel/extend | Write/update/delete `ItemLock`, plus update the item `ItemQtyPrice` quantities and the `ItemLock` summary. A lock operation therefore can touch two logical docsets, with `ItemQtyPrice` as the inventory side effect. |
| UUID mapping create/delete/anonymize | Insert/delete `UuidMap`. PII deletion anonymizes the UUID mapping and clears supported PII fields in item root/business-policy documents. |
| Delete item variations | Delete item root, compatibility, description, quantity/price, business-policy, details, and lock-summary keys. Individual lock children are handled by lock lifecycle operations; this delete list is not a blanket delete of every descendant. |
| Create/replace item group | Insert or upsert group `__ROOT__`, `GroupDescription`, and `GroupBusinessPolicies`. |
| Delete item group | Delete group `__ROOT__`, `GroupDescription`, and `GroupBusinessPolicies`. |
| Create SSKU listing draft | Insert root and `ItemDraft`; insert `ItemDraftCompatibility` only when compatibility exists. |
| Create MSKU listing draft | Insert root, `ItemGroupDraft`, `ItemGroupDraftDesc`, optional `ItemGroupDraftCompatibility`, and one `ItemDraft` per variation. |
| Update listing draft | Batch upsert root and current item documents, delete removed variation items, upsert/delete the applicable compatibility docset, and upsert/delete group/group-description documents as the draft changes between MSKU and SSKU. |
| Delete listing draft | Delete root, group/group-description/group-compatibility, item compatibility, and all descendant `ItemDraft` documents found by ancestor query. |
| Create/update active user draft | Insert, update, or upsert one `UserItemDraftMap` document. |
| Delete active user drafts | Delete the selected `UserItemDraftMap` documents. |
| Insert revision history | Insert one `ListingRevision` plus zero or more `ListingRevisionDetail` and `VariationRevisionDetail` children. Bulk backfill uses the same three docsets in one accumulated request. |
| Revision expired-date maintenance | Upsert the revision-history `__ROOT__` document when that maintenance path is invoked. |
| Archive hold update | `ArchiveItemProcessor` inherits item update logic but overrides the hold-update keyspace; the proven archive write is `ItemKeyspaceArchive/__ROOT__`. |
| Archive group version update | `ArchiveItemGroupProcessor` overrides the group-version keyspace; the proven archive write is `ItemGroupKeyspaceArchive/__ROOT__`. |

## 4. V1 dual-write and feature-gated behavior

V1 listing operations do not have a second, independent NuData schema. They
flow through `DualWriteProcessor`, which dispatches operations such as add,
relist, revise inventory, end, finalize, description, shipping, media,
markdown-sale, second-chance, hold, and HTTPS updates to the V2 item/group
processors. The resulting docsets are therefore the same item and group
families described above.

`DraftDualWriteProcessor` similarly converts V1 drafts into V2
`ListingDraft` content and can maintain the active `UserItemDraftMap` index.
These writes may be asynchronous fire-and-forget tasks, and reconciliation
or failure events can cause retries or alternate paths.

Whether a V1 request writes NuData depends on runtime configuration and ramps.
The code contains controls for disabling NuData, V2-primary migration,
parallel update, create/update/end dual-write, and draft dual-write behavior.
Consequently, the matrix describes code-proven targets, not a guarantee that
every production request reaches every target.

## 5. Counting methodology and caveats

### Counts

| Count type | Result | Meaning |
| --- | ---: | --- |
| Declared logical docsets | **22** | Distinct docset classes/collection names represented in the live schema packages. Nested Java value objects are excluded. |
| Normal item create/replace targets | **6** | The six item documents built by `CoreItemProcessor` for the standard payload path. |
| Normal item-group create/replace targets | **3** | Group root, group description, and group business policies. |
| Listing-draft logical targets | **6** | Six declared draft docsets; one SSKU request writes root plus item and optional compatibility (2–3 documents), while an MSKU request writes root, group, description, optional compatibility, and one item document per variation (3+N or 4+N documents). |
| User active-draft target | **1** | `UserItemDraftMap`. |
| Normal revision insert targets | **1–3** | Revision plus optional listing and variation detail children; the revision root is not in this normal insert. |
| Proven keyspace-qualified write sinks | **24** | The 22 live logical pairs plus two archive root pairs. |

### Important boundaries

* The counts are for NuData/MonStor structures visible in this repository.
  They exclude Oracle, Caty, SaleBO, and any downstream physical stores.
* A docset count is not a row/document count. MSKU drafts and revisions can
  create many documents in one logical docset.
* A class in the package is not proof that every path writes it. For example,
  revision `__ROOT__` is declared and read but omitted from the ordinary
  revision insert; `UuidMap` and `ItemLock` are auxiliary flows.
* Archive processors mostly read archive keyspaces. Only the overridden hold
  and group-version methods prove archive writes in this repository.
* Deletes are key-specific. A delete request may remove a known set of child
  keys and may use an ancestor query for variation documents; it should not be
  interpreted as a schema drop or a physical table drop.
* The document classes expose JSON property names, but this repository does
  not show a complete MonStor index/partition/replication DDL. The inventory
  therefore describes document shape and key ancestry, not every physical
  storage-engine index.
* Dual-write order, async execution, retry, rollback, and ramps affect when a
  write is observed and whether it is attempted. They do not create additional
  logical NuData docsets.

## 6. Q&A for Item and ItemGroup readers

This section answers questions a reader familiar with eBay shopping concepts
may ask when first encountering the Java entities and NuData docsets. The
answers are limited to behavior shown by this repository.

### What is an `Item` in this service?

`Item` is the Java V2 entity for one listing-level or variation-level
sellable record. For an SSKU listing, it represents the single sellable item.
For an MSKU listing, the service creates one `Item` for each active variation,
with variation-specific quantity, price, identifiers, and other item state.

### What is an `ItemGroup`?

`ItemGroup` is the Java V2 entity for the shared parent of an MSKU listing. It
stores the group identity, title, membership, variation traits, shared images,
group description, and group-level business policies. It is not a second copy
of every variation's commercial state.

### Does every `Item` have an `ItemGroup`?

No. An SSKU item has an `ItemKeyspace` record family and no corresponding
`ItemGroupKeyspace` record. An MSKU item has an `ItemGroupKeyspace` group, and
its item root contains `grpId` pointing to that group.

### If an MSKU has only one active variation, is the `ItemGroup` still created?

Yes. The repository uses the MSKU classification flag, not the number of
active variations, to decide whether a group exists. An MSKU with one active
variation has one item record and an item-group root whose `itemIds` list
contains exactly that one variation item ID.

### Is a one-item `itemIds` list evidence that the listing is SSKU?

No. A one-entry `itemIds` list can be a valid one-variation MSKU group. To
classify the listing, use the MSKU/SSKU behavior and the presence of the
`ItemGroupKeyspace` group, not the list length alone.

### Is the eBay seller SKU the same as the NuData item ID?

No. The NuData item ID (`Item.itemId`, persisted as `PK`) identifies the
service record. The seller-provided SKU is represented separately by
`Item.sellerItemKey` and persisted as `slrItemKey`. For a group, the seller's
group key is stored on `ItemGroup.sellerGroupKey`.

### Does one Java `Item` object map to one NuData document?

No. The Java `Item` is converted into an item document family. The root
`ItemKeyspace/__ROOT__` contains broad item state, while child docsets hold
compatibility, description, quantity/price, details, and business-policy
state. A full create/replace can therefore write six item docsets for one
Java `Item`.

### Does one Java `ItemGroup` object map to one NuData document?

No. A full group write creates or upserts three documents under the group
ancestor: `__ROOT__`, `GroupDescription`, and `GroupBusinessPolicies`.
`ItemGroup` is the source entity; the docsets are the persistence
representation.

### Are `ItemKeyspace` and `ItemGroupKeyspace` SQL tables?

They are logical NuData/MonStor keyspace families, not SQL tables shown by
this repository. Each docset class defines a persisted document shape and
each ancestor/child key defines where that document belongs. The counts in
this document are logical docset and proven sink counts, not relational table
DDL counts.

### Which fields belong to the item and which belong to the group?

Variation-specific commercial state belongs to `Item`, especially quantity and
price in `ItemQtyPrice`, along with variation identifiers and lifecycle state.
Shared MSKU state belongs to `ItemGroup`, including membership, variation
traits, group description, shared images, and group policies. The converter
explicitly clears description, business policies, compatibilities, and
global identifiers from MSKU variation `Item` objects when those values are
stored at group level.

### Where is the description stored for SSKU versus MSKU?

For SSKU, the description is written to the item's `ItemDescription` docset.
For MSKU, the shared description is written to the group's
`GroupDescription` docset rather than repeated on every variation item.

### Where are business policies stored for SSKU versus MSKU?

For SSKU, return, payment, and shipping terms are written to the item's
`BusinessPolicies` docset and related root policy fields. For MSKU, the shared
terms are written to `GroupBusinessPolicies`; the group collection name is
different even though the policy field schema is inherited from the item
business-policy model.

### Where are price and quantity stored?

Price and quantity are variation/item-level state. They are primarily written
to `ItemQtyPrice`, whose `price` object contains fixed, auction, marketing,
original-retail, cost-of-goods, and price-guarantee values, while
`availQty`, `qtySold`, and `minRmntSet` hold inventory-related values. They
are not represented by the group root merely because the item belongs to an
MSKU group.

### Are `Price`, `Lifecycle`, and `BusinessPolicies` separate docsets?

No. In the item root, `Price` and `Lifecycle` are embedded Java value objects.
The policy terms inside the item root are also embedded. `BusinessPolicies`
is a separate docset only when referring to the item policy document; the
group equivalent is the separate `GroupBusinessPolicies` docset.

### Why do several keyspaces have a `__ROOT__` class?

The class name is reused across different Java packages, but the schemas and
collections are different. `ItemKeyspace/__ROOT__` is an item root,
`ItemGroupKeyspace/__ROOT__` is a group root, and the draft and revision
roots have their own meanings. They must be identified by keyspace and
docset, not by the class name alone.

### Can a consumer reconstruct a complete MSKU listing from the group alone?

No. The group provides shared structure and the list of variation item IDs.
The consumer must fetch the corresponding `ItemKeyspace` item families to
obtain each variation's price, quantity, lifecycle, and other item-level
state. Conversely, an item alone does not establish the complete group
membership.

## 7. Evidence map

The primary source locations for the walkthrough are:

* [`Docset.java`](../crlstngsvService/src/main/java/com/ebay/app/cls/nudata/Docset.java) -
  document-set schema abstraction.
* [`CoreItemProcessor.java`](../crlstngsvService/src/main/java/com/ebay/app/cls/processor/CoreItemProcessor.java) -
  item keys, six-document insert/upsert, partial mutations, locks, UUID map,
  PII, and delete paths.
* [`DocumentConverter.java`](../crlstngsvService/src/main/java/com/ebay/app/cls/processor/DocumentConverter.java) -
  item root and child document construction.
* [`ListingConverter.java`](../crlstngsvService/src/main/java/com/ebay/app/cls/processor/ListingConverter.java) -
  SSKU/MSKU classification, variation item creation, and group `itemIds`
  construction.
* [`CoreItemGroupProcessor.java`](../crlstngsvService/src/main/java/com/ebay/app/cls/processor/CoreItemGroupProcessor.java) -
  group keys and three-document mutations.
* [`ItemGroupDocumentConverter.java`](../crlstngsvService/src/main/java/com/ebay/app/cls/processor/ItemGroupDocumentConverter.java) -
  group document construction.
* [`CoreListingDraftProcessor.java`](../crlstngsvService/src/main/java/com/ebay/app/cls/processor/CoreListingDraftProcessor.java) -
  SSKU/MSKU draft insert, upsert, and delete behavior.
* [`DraftDocumentConverter.java`](../crlstngsvService/src/main/java/com/ebay/app/cls/processor/DraftDocumentConverter.java) -
  draft root, item, group, description, and compatibility documents.
* [`UserListingDraftProcessor.java`](../crlstngsvService/src/main/java/com/ebay/app/cls/processor/UserListingDraftProcessor.java) -
  active-draft map insert/update/delete.
* [`RevisionHistoryNudataClient.java`](../crlstngsvService/src/main/java/com/ebay/app/cls/nudata/repository/revisionhistory/RevisionHistoryNudataClient.java) -
  revision and optional child inserts.
* [`RevisionHistoryConstants.java`](../crlstngsvService/src/main/java/com/ebay/app/cls/nudata/repository/revisionhistory/RevisionHistoryConstants.java) -
  revision keyspace and docset names.
* [`DualWriteProcessor.java`](../crlstngsvService/src/main/java/com/ebay/app/cls/processor/DualWriteProcessor.java) and
  [`DraftDualWriteProcessor.java`](../crlstngsvService/src/main/java/com/ebay/app/cls/processor/DraftDualWriteProcessor.java) -
  V1-to-V2 routing and asynchronous/ramped behavior.
* [`ArchiveItemProcessor.java`](../crlstngsvService/src/main/java/com/ebay/app/cls/processor/ArchiveItemProcessor.java) and
  [`ArchiveItemGroupProcessor.java`](../crlstngsvService/src/main/java/com/ebay/app/cls/processor/ArchiveItemGroupProcessor.java) -
  archive keyspace overrides.
