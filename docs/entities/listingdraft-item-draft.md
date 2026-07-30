# ListingDraftItem LDM

[<- Back to LDM Catalog](../index.md)

## Overview

**LDM Name:** `ListingDraftItem LDM`

**Description:** Draft content for an SSKU listing or one MSKU variation.

**NuDocument Docset:** `ItemDraft`

**Keyspace:** `ListingDraft`

**Source Class:** `com.ebay.app.cls.nudata.listingdraftkeyspace.ItemDraft`

**Primary Key:** `PK`

**Relationship Type:** Child document for a draft item or MSKU variation

---

## Fields

`ItemDraft` stores item or variation content, price, inventory, seller, policy
identifiers, and listing metadata.

| Field | Type | Description |
| --- | --- | --- |
| `PK` | `String` | Item draft document identifier. |
| `aspct` | `List<Aspects>` | Item aspect entries, each containing an aspect name and values. |
| `auctRsvPrc` | `Amount` | Auction reserve price, including currency and value. |
| `autoRlsTrm` | `AutoRelistTerms` | Auto-relist settings, including its enablement and relist count. |
| `avlQty` | `Integer` | Available quantity. |
| `bstOfrTrm` | `BestOfferTerms` | Best-offer settings, including offer flags and automatic threshold prices. |
| `bizPol` | `BusinessPolicies` | Business-policy set and embedded return, payment, and shipping terms. |
| `brnd` | `String` | Brand. |
| `buyrRst` | `BuyerRestrictions` | Buyer restriction settings, including purchase-rate and unpaid-transaction thresholds. |
| `buyrRstDsbld` | `Boolean` | Buyer-restrictions-disabled indicator. |
| `chrty` | `Charity` | Charity identifier and donation percentage. |
| `cndDesc` | `String` | Condition description. |
| `cndDescriptors` | `List<ConditionDescriptor>` | Condition descriptor entries. |
| `cndId` | `String` | Condition identifier. |
| `cndIdNum` | `Integer` | Numeric condition identifier. |
| `crtDt` | `Long` | Creation date/time value. |
| `crtMd` | `CreationMode` | Creation-mode classification. |
| `currPrc` | `Amount` | Current price, including currency and value. |
| `desc` | `String` | Expanded item description. |
| `cmpDesc` | `byte[]` | Compressed item description. |
| `drtn` | `Duration` | Listing duration. |
| `eBGenTtl` | `String` | eBay-generated title. |
| `endDt` | `Long` | Listing end date/time value. |
| `epid` | `String` | eBay product identifier. |
| `ftmtId` | `String` | Fulfillment identifier. |
| `fxdPrc` | `Amount` | Fixed price, including currency and value. |
| `fxdPrcHP` | `Amount` | High-precision fixed price, including currency and value. |
| `fl01` | `Long` | Source-declared `fl01` flag/value field. |
| `fmt` | `Format` | Listing format classification. |
| `ffTrm` | `FulfillmentTerms` | Fulfillment settings, including shipping options, package specifications, and delivery-related flags. |
| `glbId` | `List<NameValuesPair>` | Global identifier name/value entries. |
| `hidePrt` | `Boolean` | Source-declared hide-part indicator. |
| `img` | `List<ImageMap>` | Image mappings, including external and eBay image URLs and display order. |
| `eBProdDtls` | `Boolean` | Source-declared eBay-product-details indicator. |
| `prodDtls` | `Boolean` | Source-declared product-details indicator. |
| `stckPhtUrl` | `Boolean` | Source-declared stock-photo-URL indicator. |
| `invTrkMth` | `InventoryTrackingMethod` | Inventory tracking method. |
| `itmId` | `String` | Item identifier. |
| `itmLoc` | `String` | Item location. |
| `itmLocCtry` | `CountryEnum` | Item-location country. |
| `itmLocPstCd` | `String` | Item-location postal code. |
| `lstModDt` | `Long` | Last-modified date/time value. |
| `lstgAppId` | `String` | Listing application identifier. |
| `lstCrtClntIp` | `String` | Listing-creation client IP value. |
| `lotSz` | `Integer` | Lot size. |
| `mktPrc` | `MarketingPrice` | Marketing-price data, including comparison, advertised, retail, and pricing-treatment values. |
| `mktPlLstdOn` | `String` | Marketplace on which the item is listed. |
| `minRmntSet` | `Integer` | Source-declared minimum-remaining setting. |
| `mpn` | `String` | Manufacturer part number. |
| `notes` | `String` | Draft notes. |
| `origItmId` | `String` | Original item identifier. |
| `origItmPrc` | `Amount` | Original item price, including currency and value. |
| `origPstCd` | `String` | Origin postal code. |
| `oosDt` | `Long` | Out-of-stock date/time value. |
| `pymtPlcyId` | `BusinessPolicyIdentifier` | Payment-policy identifier and version. |
| `primCatId` | `String` | Primary category identifier. |
| `prdSpptd` | `List<ProgramsSupported>` | Supported-program entries. |
| `qtySold` | `Integer` | Quantity sold. |
| `rlstId` | `String` | Relist identifier. |
| `rlstPrntId` | `String` | Parent relist identifier. |
| `rtrnsPlcyId` | `BusinessPolicyIdentifier` | Return-policy identifier and version. |
| `schdEndDt` | `Long` | Scheduled end date/time value. |
| `scndCatId` | `String` | Secondary category identifier. |
| `scndChncItm` | `Boolean` | Second-chance-item indicator. |
| `eBayVlt` | `Boolean` | Source-declared eBay Vault indicator. |
| `slr` | `Seller` | Seller identity, contact, and support-hours data. |
| `slrAppData` | `String` | Seller application data. |
| `slrItmKey` | `String` | Seller item key. |
| `shipPlcyId` | `BusinessPolicyIdentifier` | Shipping-policy identifier and version. |
| `sigRevCnt` | `Integer` | Significant revision count. |
| `strtDt` | `Long` | Listing start date/time value. |
| `strtBidPrc` | `Amount` | Starting-bid price, including currency and value. |
| `strtBidPrcHP` | `Amount` | High-precision starting-bid price, including currency and value. |
| `stPrimCatId` | `String` | Store primary category identifier. |
| `stScndCatId` | `String` | Store secondary category identifier. |
| `tax` | `Tax` | Tax applicability, jurisdiction, category, rate, and VAT data. |
| `COGs` | `Amount` | Cost of goods, including currency and value. |
| `ttl` | `String` | Item title. |
| `trdScp` | `TradingScope` | Trading-scope data, including international visibility and local distribution. |
| `uuid` | `String` | Universally unique identifier. |
| `itmOrd` | `Long` | Item order value. |
| `vehId` | `List<NameValuesPair>` | Vehicle identifier name/value entries. |
| `vrsId` | `String` | Variation or version identifier. |
| `visEnh` | `VisualEnhancements` | Visual-enhancement settings, such as title, gallery, photo-display, subtitle, and visitor-counter options. |
| `vehPkgId` | `String` | Vehicle package identifier. |
| `videos` | `List<String>` | Video values associated with the item. |
| `ebayCmnty` | `EbayCommunity` | eBay community identifiers and marketplace-visibility setting. |
| `lotId` | `String` | Lot identifier. |
| `ftExempt` | `Integer` | Source-declared fulfillment-tax exemption value. |
| `itmOnSale` | `Boolean` | Item-on-sale indicator. |
| `itmRevsnDt` | `Long` | Item revision date/time value. |
| `descRevsnDt` | `Long` | Description revision date/time value. |
| `epr` | `ExtendedProducerResponsibility` | Extended producer responsibility identifiers, document references, and eco-fee data. |
| `cstmPol` | `CustomPolicies` | Custom take-back and product-compliance policy identifiers, including regional policy associations. |
| `rgltryInfo` | `RegulatoryInfo` | Regulatory data for hazardous materials, product safety, repairability, responsible parties, documents, and energy labels. |
| `docs` | `Documents` | Vehicle document data, including title, VIN, and odometer values. |
| `srcLstId` | `String` | Source listing identifier. |

## Write and Read Behavior

Draft updates upsert current item children and delete removed variation
children. An SSKU draft writes one item draft; an MSKU draft writes one item
draft per variation.

## Relationships

This docset is a child of the `ListingDraft` ancestor. It can coexist with
group, group-description, and compatibility children when the draft represents
an MSKU listing.
