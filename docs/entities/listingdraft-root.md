# ListingDraftRoot LDM

[<- Back to LDM Catalog](../index.md)

## Overview

**LDM Name:** `ListingDraftRoot LDM`

**Description:** Working listing-draft session state, flags, scratch data, and variation identifiers.

**NuDocument Docset:** `__ROOT__`

**Keyspace:** `ListingDraft`

**Source Class:** `com.ebay.app.cls.nudata.listingdraftkeyspace.__ROOT__`

**Primary Key:** `PK`

**Relationship Type:** Root document for listing-draft session and state

---

## Fields

The source groups draft root fields into draft session, draft-session flags,
item flags, and scratch details.

| Field | Type | Description |
| --- | --- | --- |
| `PK` | `String` | Draft root document identifier. |
| `itmId` | `List<String>` | Item identifiers associated with this draft root. |
| `lstgTm` | `Long` | Source-declared listing-time value. |
| `origItmId` | `String` | Original item identifier. |
| `lstdItmId` | `String` | Listed-item identifier. |
| `prgDt` | `Long` | Source-declared progress-date value. |
| `totCumLstgs` | `Long` | Cumulative-listings count. |
| `lstgTmpltFls` | `Integer` | Source-declared listing-template flags value. |
| `mnMxFls` | `Integer` | Source-declared minimum/maximum flags value. |
| `ryiStat` | `Integer` | Source-declared `ryi` status value. |
| `scrtchFl` | `Integer` | Source-declared scratch flag value. |
| `scrtchFl2` | `Integer` | Source-declared scratch flag value 2. |
| `scrtchFl3` | `Integer` | Source-declared scratch flag value 3. |
| `scrtchFl4` | `Integer` | Source-declared scratch flag value 4. |
| `fl` | `Long` | Source-declared flag/value field. |
| `fl2` | `Long` | Source-declared flag/value field 2. |
| `fl3` | `Long` | Source-declared flag/value field 3. |
| `fl4` | `Long` | Source-declared flag/value field 4. |
| `fl5` | `Long` | Source-declared flag/value field 5. |
| `fl6` | `Long` | Source-declared flag/value field 6. |
| `fl7` | `Long` | Source-declared flag/value field 7. |
| `fl8` | `Long` | Source-declared flag/value field 8. |
| `fl9` | `Long` | Source-declared flag/value field 9. |
| `fl10` | `Long` | Source-declared flag/value field 10. |
| `fl11` | `Long` | Source-declared flag/value field 11. |
| `fl12` | `Long` | Source-declared flag/value field 12. |
| `pwdEx` | `Long` | Source-declared password-expiration value. |
| `props` | `Long` | Source-declared properties value. |
| `saleStat` | `Long` | Source-declared sale-status value. |
| `visitCnt` | `Long` | Visit count. |
| `shipRgn` | `Long` | Source-declared shipping-region value. |
| `appCstmInfo` | `String` | Application custom-information value. |
| `autoRlstOrigAppId` | `String` | Original application identifier for auto-relist. |
| `bidCnt` | `Long` | Bid count. |
| `usgHistDtl` | `List<NameValuePair>` | Usage-history detail name/value entries. |
| `ftmtCnt` | `Integer` | Fulfillment count. |
| `galPicMd5Hsh` | `String` | Gallery-picture MD5 hash. |
| `galUrl` | `String` | Gallery URL. |
| `strdFixdPrc` | `Boolean` | Source-declared stored-fixed-price indicator. |
| `itmVisOpt` | `String` | Item visibility option. |
| `lstgMthd` | `ListingMethodType` | Listing method classification. |
| `mkdnSaleItmPrcRev` | `Long` | Markdown-sale item-price revision value. |
| `pplIcnTp` | `PaypalIconType` | PayPal icon type. |
| `pbpElig` | `Long` | Source-declared `pbp` eligibility value. |
| `prmSaleEndDt` | `Long` | Promotion-sale end date/time value. |
| `prmSaleStrtDt` | `Long` | Promotion-sale start date/time value. |
| `slfHstdPic` | `String` | Self-hosted picture value. |
| `slfHstdPicMap` | `String` | Self-hosted picture mapping value. |
| `strCatIds` | `List<String>` | Store category identifiers. |
| `thFl` | `Long` | Source-declared `th` flag value. |
| `lastModDate` | `Long` | Last-modified date/time value. |
| `crtDate` | `Long` | Creation date/time value. |
| `usrItmPrpKey` | `Long` | User-item-property key. |
| `qtySold` | `Integer` | Quantity sold. |
| `itmRevsnDt` | `Long` | Item revision date/time value. |
| `descRevsnDt` | `Long` | Description revision date/time value. |

## Write and Read Behavior

Draft writes batch the root with the applicable item, group,
group-description, and compatibility children. The exact child set differs
between SSKU and MSKU drafts. Draft summary reads can project selected fields
from the root and current child documents.

## Relationships

This root shares a draft ancestor with `ItemDraft`, `ItemGroupDraft`,
`ItemGroupDraftDesc`, `ItemDraftCompatibility`, and
`ItemGroupDraftCompatibility`.
