# ItemKeyspace

Source wiki: <https://wiki.corp.ebay.com/spaces/LS/pages/2269026410/ItemKeyspace>

## Overview

This page describes the document collections in the ItemKeyspace, including their fields, data types, and descriptions. Each section represents a distinct document/collection in the keyspace.

Production keyspace: <https://cloud.ebay.com/cloud-data/databases/nudocument/keyspaces/ItemKeyspace?tab=overview&environment=production>

## Documents in ItemKeyspace

| Collection | Description |
| --- | --- |
| `__ROOT__` | The main item document containing static/core listing data |
| `ItemQtyPrice` | Stores quantity and pricing information (frequently updated data) |
| `ItemDescription` | Stores the item description (separated for performance) |
| `ItemCompatibility` | Stores parts compatibility/fitment data |
| `BusinessPolicies` | Stores detailed business policy information |
| `ItemDetailsDoc` | Additional listing details like relaxed rules and high precision prices |
| `UuidMap` | Maps UUID to Item ID for uniqueness validation |
| `ItemLock` | Provides locking mechanism for concurrent updates |

## 1. `__ROOT__`

The main item document containing static/core listing data.

### Core Identification Fields

| Field | Type | Description |
| --- | --- | --- |
| `PK` | String | Item ID (Primary Key) |
| `title` | String | Item title |
| `sellerId` | String | Seller user ID |
| `uuid` | String | Unique constraint tag |
| `vrsnId` | String | Version ID |
| `crLstgDtVrs` | String | Core listing data version |
| `drftId` | String | Draft ID this item was created from |

### Category, Catalog, etc.

| Field | Type | Description |
| --- | --- | --- |
| `category` | Category | Primary and secondary category IDs |
| `epid` | String | eBay Product ID |
| `gblIdentifiers` | `List<NameValuesPair>` | UPC, EAN, ISBN |
| `aspects` | `List<Aspects>` | Item specifics/attributes |
| `IncEbyPrdtDtail` | Boolean | Include eBay product details |
| `IncStkPhtoUrl` | Boolean | Include stock photo URL |
| `prdGallryFallbckURL` | String | Product gallery fallback URL |
| `PrmnlDtls` | PromotionalDetails | Promotional details |

### Format, Condition, etc.

| Field | Type | Description |
| --- | --- | --- |
| `format` | Format | Auction, fixed price, etc. |
| `lifecycle` | Lifecycle | Duration, start/end dates |
| `vehPkgId` | String | Vehicle package ID |
| `vhclIdentifiers` | `List<NameValuesPair>` | Vehicle identifiers |
| `ftmtId` | String | Fitment ID |
| `conditionId` | String | Condition enum value |
| `cndIdNum` | Integer | Condition numeric ID |
| `conditionDesc` | String | Condition description |
| `cndDescriptors` | `List<ConditionDescriptor>` | Additional condition info |
| `images` | `List<ImageMap>` | Item images |
| `videos` | `List<String>` | Video URLs |
| `eBayGenTitle` | String | eBay-generated title for vehicles |
| `itmLocn` | String | Item location |
| `itmLocnCntry` | CountryEnum | Item location country |
| `itmLocnPostlCd` | String | Item postal code |
| `slrItemKey` | String | Seller's custom SKU |
| `invntryTrkMthd` | InventoryTrackingMethod | SKU vs ItemID tracking |
| `trmsAndPolicies` | TermsAndPolicies | Business policies container |
| `tax` | Tax | Tax information |
| `charity` | Charity | Charity donation info |
| `sprtCntct` | SupportContact | Support contact information |

### Listing Lifecycle

| Field | Type | Description |
| --- | --- | --- |
| `crtDate` | Long | Creation timestamp |
| `lastModDate` | Long | Last modified timestamp |
| `itmRevsnDt` | Long | Item revision date |
| `outOfStockDt` | Long | Out of stock date |
| `admEndDt` | Long | Admin-ended date |
| `endRsn` | EndReason | Reason for ending |

### Relist, App Data, Regulatory, etc.

| Field | Type | Description |
| --- | --- | --- |
| `crtMode` | CreationMode | Relist, sell similar, etc. |
| `rlstId` | String | Relist item ID |
| `rlstPrntId` | String | Relist parent ID |
| `sigRevCnt` | Integer | Significant revision count |
| `vslEncmt` | VisualEnhancements | Bold, featured, etc. |
| `prgSpprtd` | `List<ProgramsSupported>` | Programs like eBay Plus |
| `ebayCmnty` | EbayCommunity | eBay community listing info |
| `listingAppId` | String | Application identifier |
| `autoRlstOrigAppId` | String | Auto-relist original app ID |
| `slrAppData` | String | Seller application data |
| `lstgCrtCltIp` | String | Listing creation client IP |
| `notes` | String | Internal notes |
| `epr` | ExtendedProducerResponsibility | EPR information |
| `cstmPol` | CustomPolicies | Custom policies |
| `rgltryInfo` | RegulatoryInfo | Regulatory information |
| `httpsCmplt` | Integer | HTTPS compliance |
| `lotSize` | Integer | Lot size for lot listings |
| `lotId` | String | Lot identifier |
| `autoRlstTerms` | AutoRelistTerms | Auto-relist settings |
| `mktplcLstdOn` | String | Marketplace site ID |

### Listing Flags

| Field | Type | Description |
| --- | --- | --- |
| `mngByInv` | Boolean | Manage by inventory |
| `buyerRstDsbld` | Boolean | Buyer restrictions disabled |
| `scndChncItm` | Boolean | Second chance item |
| `eBayVlt` | Boolean | eBay Vault item |
| `onHold` | Boolean | On hold status |
| `itmOnSale` | Boolean | Item on sale |
| `isScheduled` | Boolean | Scheduled listing |
| `isSellerOnVacation` | Boolean | Seller on vacation |
| `isRestrictedToBusinessUser` | Boolean | B2B only |
| `isBuyerResponsibleForShipping` | Boolean | Motors shipping |
| `isListedWithNoContactViaEmailSupport` | Boolean | No email contact |
| `isBusinessPolicyItem` | Boolean | Uses business policies |
| `isRestrictedBidding` | Boolean | Pre-approved bidders |
| `isSCOStatusIndicator` | Boolean | SCO status |
| `isCreatedBySellSimilar` | Boolean | Created via sell similar |
| `isVariation` | Boolean | Is this a variation/child item (MSKU) |
| `isSemiPrsBin` | Boolean | Semi-persistent BIN |
| `prtnrLstdAutoDlrItm` | Boolean | Partner dealer item |
| `isVhclSbscrpItm` | Boolean | Vehicle subscription |
| `bidsFl` | Boolean | Bids finalized |
| `sellerPOverridn` | Boolean | Seller profile overridden |
| `hidePrtcptn` | Boolean | Private listing |

## 2. `ItemQtyPrice`

Stores quantity and pricing information (frequently updated data).

| Field | Type | Description |
| --- | --- | --- |
| `ItemQtyPriceID` | String | Collection document ID |
| `availQty` | Integer | Available quantity |
| `qtySold` | Integer | Quantity sold |
| `qtySldByPickpStre` | Integer | Quantity sold by pickup store |
| `minRmntSet` | Integer | Minimum remnant set |
| `price` | Price | Container for all pricing fields |
| `price.fixedPrice` | Amount | Fixed/BIN price |
| `price.auctnRsrvPrc` | Amount | Auction reserve price |
| `price.strtBidPrice` | Amount | Starting bid price |
| `price.mrktngPrc` | MarketingPrice | Marketing/original price |
| `price.orgnRetailPrice` | Amount | Original retail price |
| `price.COGs` | Amount | Cost of goods sold |
| `price.prcGuarantee` | Boolean | Enrolled in price guarantee |

## 3. `ItemDescription`

Stores the item description (separated for performance).

| Field | Type | Description |
| --- | --- | --- |
| `ItemDescID` | String | Collection document ID |
| `desc` | String | Item description text/HTML |
| `compDesc` | `byte[]` | Compressed description |
| `descRevsnDt` | Long | Description revision date |

## 4. `ItemCompatibility`

Stores parts compatibility/fitment data.

| Field | Type | Description |
| --- | --- | --- |
| `ItemCompID` | String | Collection document ID |
| `compat` | `List<ItemCompatibility>` | Compatibility entries |
| `cmpCompat` | `byte[]` | Compressed compatibilities |
| `ftExempt` | Integer | Fitment threshold exempt |

## 5. `BusinessPolicies`

Stores detailed business policy information.

| Field | Type | Description |
| --- | --- | --- |
| `plcsId` | String | Policies document ID |
| `retTrms` | ReturnTerms | Return policy details |
| `pmtTrms` | PaymentTerms | Payment terms |
| `shipTrms` | ShippingTerms | Shipping terms |

## 6. `ItemDetailsDoc`

Additional listing details like relaxed rules and high precision prices.

| Field | Type | Description |
| --- | --- | --- |
| `itemDetailsID` | String | Collection document ID |
| `hasRlxdRls` | Boolean | Indicates if the listing has relaxed rules applied |
| `fixedPriceHP` | Amount | Fixed price with high precision |
| `strtBidPriceHP` | Amount | Starting bid price with high precision |
| `docs` | Documents | Vehicle-related documents container |
| `docs.vhclTtlFrnt` | String | Vehicle title front document reference |
| `docs.vhclTtlBck` | String | Vehicle title back document reference |
| `docs.vin` | String | Vehicle Identification Number document reference |
| `docs.odometer` | String | Odometer reading document reference |

## 7. `UuidMap`

Maps UUID to Item ID for uniqueness validation. The document is keyed by the UUID itself (primary key); the following fields are stored within the document.

| Field | Type | Description |
| --- | --- | --- |
| `listingId` | String | Listing ID mapped to the UUID |
| `listingAppId` | String | Listing application ID associated with the UUID |

## 8. `ItemLock`

Provides locking mechanism for concurrent updates.

| Field | Type | Description |
| --- | --- | --- |
| `pk` | String | Lock ID (Primary Key) |
| `st` | ItemLockStatus | Lock status: A (ACTIVE), C (COMMITTED), X (CANCELLED) |
| `qty` | Long | Quantity being locked |
| `expDt` | Long | Lock expiration timestamp |
| `cmtDt` | Long | Committed timestamp (nullable) |
| `cnclDt` | Long | Cancelled timestamp (nullable) |
| `extDt` | Long | Extended timestamp (nullable) |
| `extCnt` | Long | Number of times the lock has been extended (nullable) |
| `crtDt` | Long | Creation timestamp |
| `modDt` | Long | Last modified timestamp (nullable) |
| `uuid` | String | UUID associated with the lock |
