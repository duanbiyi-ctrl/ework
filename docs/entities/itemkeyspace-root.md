# ItemRoot LDM

[<- Back to LDM Catalog](../index.md)

## Overview

**LDM Name:** `ItemRoot LDM`

**Description:** Current-state identity and broad listing data for one item or variation.

**NuDocument Docset:** `__ROOT__`

**Keyspace:** `ItemKeyspace`

**Source Class:** `com.ebay.app.cls.nudata.itemkeyspace.__ROOT__`

**Primary Key:** `PK`

**Relationship Type:** Root document for current-state item data

---

## Fields

The item root is the broadest item document. It combines listing identity,
seller and location, lifecycle, category, policy references, flags, and item
features. Fields inside embedded value objects are not separate NuDocument
docsets.

| Field | Type | Description |
| --- | --- | --- |
| `aspects` | `List<Aspects>` | Item aspects, each with an aspect name and its values. |
| `autoRlstTerms` | `AutoRelistTerms` | Auto-relisting setting and relist count. |
| `category` | `Category` | Primary and secondary marketplace and store category identifiers. |
| `charity` | `Charity` | Charity identifier and donation percentage. |
| `conditionDesc` | `String` | Seller-provided description of the item condition. |
| `conditionId` | `String` | Item condition identifier. |
| `eBayGenTitle` | `String` | eBay-generated item title. |
| `itmLocn` | `String` | Item location. |
| `itmLocnPostlCd` | `String` | Postal code of the item location. |
| `listingAppId` | `String` | Identifier of the application that created the listing. |
| `autoRlstOrigAppId` | `String` | Identifier of the application for the original auto-relisted item. |
| `slrAppData` | `String` | Seller application data. |
| `mktplcLstdOn` | `String` | Marketplace on which the item is listed. |
| `notes` | `String` | Item notes. |
| `PK` | `String` | Item identifier and root document primary key. |
| `pk` | `String` | Lower-case item key carried by the current-state document payload. |
| `sellerId` | `String` | Seller identifier. |
| `slrItemKey` | `String` | Seller's item key. |
| `title` | `String` | Item title. |
| `uuid` | `String` | Universally unique item identifier. |
| `epid` | `String` | eBay product identifier. |
| `drftId` | `String` | Draft identifier. |
| `crLstgDtVrs` | `String` | Core listing data version. |
| `vrsnId` | `String` | Item version identifier. |
| `ftmtId` | `String` | Fitment identifier. |
| `vehPkgId` | `String` | Vehicle package identifier. |
| `lotId` | `String` | Lot identifier. |
| `prdGallryFallbckURL` | `String` | Fallback URL for the product gallery. |
| `grpId` | `String` | Item group identifier. |
| `lstgCrtCltIp` | `String` | Client IP address used to create the listing. |
| `cndIdNum` | `Integer` | Numeric item condition identifier. |
| `lotSize` | `Integer` | Number of items in the lot. |
| `sigRevCnt` | `Integer` | Count of significant item revisions. |
| `httpsCmplt` | `Integer` | HTTPS-compliance indicator. |
| `cndDescriptors` | `List<ConditionDescriptor>` | Condition descriptors that further characterize the item's condition. |
| `images` | `List<ImageMap>` | Item images with external and eBay URLs and display order. |
| `gblIdentifiers` | `List<NameValuesPair>` | Global item identifiers represented as name-value pairs. |
| `vhclIdentifiers` | `List<NameValuesPair>` | Vehicle identifiers represented as name-value pairs. |
| `videos` | `List<String>` | Item video values. |
| `creationMode` | `CreationMode` | How the item was created. |
| `format` | `Format` | Listing format. |
| `itmLocnCntry` | `CountryEnum` | Country of the item location. |
| `invntryTrkMthd` | `InventoryTrackingMethod` | Inventory-tracking method. |
| `endRsn` | `EndReason` | Reason the listing ended. |
| `scndChncItm` | `Boolean` | Whether this is a second-chance item. |
| `eBayVlt` | `Boolean` | Whether the item is associated with eBay Vault. |
| `hidePrtcptn` | `Boolean` | Whether participation is hidden. |
| `mngByInv` | `Boolean` | Whether the item is managed by inventory. |
| `buyerRstDsbld` | `Boolean` | Whether buyer restrictions are disabled. |
| `prtnrLstdAutoDlrItm` | `Boolean` | Whether the item was partner-listed as an autos dealer item. |
| `isVhclSbscrpItm` | `Boolean` | Whether this is a vehicle subscription item. |
| `IncEbyPrdtDtail` | `Boolean` | Whether eBay product details are included. |
| `IncStkPhtoUrl` | `Boolean` | Whether a stock photo URL is included. |
| `itmOnSale` | `Boolean` | Whether the item is on sale. |
| `onHold` | `Boolean` | Whether the item is on hold. |
| `bidsFl` | `Boolean` | Whether bidding has been finalized. |
| `sellerPOverridn` | `Boolean` | Whether the seller profile has been overridden. |
| `isScheduled` | `Boolean` | Whether the listing is scheduled. |
| `isSellerOnVacation` | `Boolean` | Whether the seller is on vacation. |
| `isRestrictedToBusinessUser` | `Boolean` | Whether the listing is restricted to business users. |
| `isBuyerResponsibleForShipping` | `Boolean` | Whether the buyer is responsible for shipping. |
| `isListedWithNoContactViaEmailSupport` | `Boolean` | Whether the listing disallows contact through email support. |
| `isBusinessPolicyItem` | `Boolean` | Whether the item uses business policies. |
| `isRestrictedBidding` | `Boolean` | Whether bidding is restricted. |
| `isSCOStatusIndicator` | `Boolean` | Self-checkout status indicator. |
| `isCreatedBySellSimilar` | `Boolean` | Whether the item was created with Sell Similar. |
| `isVariation` | `Boolean` | Whether the item is a variation. |
| `isSemiPrsBin` | `Boolean` | Whether this is a semi-persistent Buy It Now listing. |
| `lifecycle` | `Lifecycle` | Listing duration, start and end times, and scheduled-listing and duplicate-auction status. |
| `sprtCntct` | `SupportContact` | Support company, contact details, availability, hours, and supported days. |
| `trmsAndPolicies` | `TermsAndPolicies` | Best-offer, buyer-restriction, fulfillment, policy, and warranty terms. |
| `trdScp` | `TradingScope` | International visibility and local listing distribution settings. |
| `vslEncmt` | `VisualEnhancements` | Title, gallery, photo-display, visitor-counter, and subtitle enhancements. |
| `tax` | `Tax` | Sales-tax and VAT applicability, location, category, and rate details. |
| `ebayCmnty` | `EbayCommunity` | Community identifiers and marketplace visibility. |
| `epr` | `ExtendedProducerResponsibility` | Producer-responsibility identifiers and eco fee. |
| `cstmPol` | `CustomPolicies` | Take-back and product-compliance policy identifiers, including regional policies. |
| `rgltryInfo` | `RegulatoryInfo` | Hazardous-material, product-safety, repairability, operator, manufacturer, responsible-person, document, and energy-label information. |
| `PrmnlDtls` | `PromotionalDetails` | Promotional pricing revision and free-shipping promotion settings. |
| `outOfStockDt` | `Long` | Timestamp when the item became out of stock. |
| `lastModDate` | `Long` | Timestamp of the last item modification. |
| `crtDate` | `Long` | Timestamp when the item was created. |
| `itmRevsnDt` | `Long` | Timestamp of the item revision. |
| `admEndDt` | `Long` | Administrative listing-end timestamp. |
| `rlstPrntId` | `String` | Parent identifier for a relisted item. |
| `rlstId` | `String` | Relist identifier. |
| `prgSpprtd` | `List<ProgramsSupported>` | Programs supported by the item. |

## Write and Read Behavior

Create and replace operations build this root with
`DocumentConverter.getRoot(...)` and write it with the item child docsets in
one transactional request. Partial category, price and quantity, hold, and
media operations can update selected root fields without rebuilding the full
document. `CoreItemProcessor` reads the root with multi-docset item requests.

## Relationships

The root shares an item ancestor with `ItemCompatibility`, `ItemDescription`,
`ItemQtyPrice`, `ItemDetails`, `BusinessPolicies`, and `ItemLock`. It is a
current-state item document, not a relational parent table.
