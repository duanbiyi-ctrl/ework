# Sample Data vs. Schema Alignment Report

This page documents the findings from cross-checking all 22 raw LDM JSON sample
files (under `data/sample-data/item-raw-ldm-samples/`) against their corresponding
schema definition pages in `docs/entities/`.

Each schema is rated:

- **🟢 Aligned** — data matches schema; no corrections needed
- **🟡 Partially aligned** — content matches but schema documentation has gaps or
  omissions
- **🔴 Misaligned** — documented field format or name is factually wrong in the schema

---

## Critical Corrections (🔴 Must Fix)

Three schemas document primary-key ID generation patterns that do not match actual
data. The prefixes are condensed in production; underscores documented in the schema
are absent in reality.

| Schema | Field | Documented Format | Actual Format |
|---|---|---|---|
| `itemkeyspace-business-policies.md` | `plcsId` | `BIZ_POL_<itemId>` | `BIZPOL_<itemId>` |
| `itemkeyspace-item-details.md` | `itemDetailsID` | `ITEM_DETAILS_<itemId>` | `ITEMDET_<itemId>` |
| `itemkeyspace-item-qty-price.md` | `ItemQtyPriceID` | `QTY_PRICE_<itemId>` | `QTYPRICE_<itemId>` |

**Action:** Update the "ID Generation" examples (and the existing review-notes table
in `ldm-review-notes.md`) for these three pages to use the correct prefix strings.

Note: the `GroupBusinessPolicies` schema inherits its field shape from
`ItemBusinessPolicies`; its `plcsId` values in sample data use `BIZPOL_<groupId>`,
confirming the same prefix convention applies to the group-level counterpart.

---

## Findings by Schema (All 22)

### 1 — ItemGroupKeyspace / GroupBusinessPolicies

**File:** `ItemGroupKeyspace/GroupBusinessPolicies.json`
**Schema:** `itemgroupkeyspace-group-business-policies.md`
**Rating:** 🟢 Aligned

All documented fields (`plcsId`, `retTrms`, `pmtTrms`, `shipTrms`) are present and
correctly structured. The `BIZPOL_<groupId>` prefix convention used in `plcsId` is
consistent but not explicitly stated in the schema text.

**Gap:** Schema does not document the `BIZPOL_` prefix convention for `plcsId`.

---

### 2 — ItemGroupKeyspace / GroupDescription

**File:** `ItemGroupKeyspace/GroupDescription.json`
**Schema:** `itemgroupkeyspace-group-description.md`
**Rating:** 🟢 Aligned

`groupDescId`, `groupDesc`, `compDesc`, and `grpDescRevsnDt` are all present in
samples. Some records omit `compDesc` entirely (not present, not `null`); some
records omit `grpDescRevsnDt`. Both are valid optional states.

**Gap:** Schema does not note that `compDesc` and `grpDescRevsnDt` can be absent
when no compressed form or revision timestamp exists.

---

### 3 — ItemGroupKeyspace / ItemGroupKeyspace\_ROOT\_

**File:** `ItemGroupKeyspace/ItemGroupKeyspace_ROOT_.json`
**Schema:** `itemgroupkeyspace-root.md`
**Rating:** 🟢 Aligned

All documented fields (`PK`, `owner`, `groupTitle`, `itemIds`, `itmsVryBy`,
`imgVryBy`, `images`, `grpVrs`, `grpDrftId`, `mFulfillmentSprt`,
`globalIdentifiers`, `httpsCmplt`, `createdDt`, `lastmodifiedDt`, `admEndDt`,
`groupType`, `sellerGroupKey`, `compat`, `cmpCompat`) are present and correctly typed.

**Observation:** Within `imgVryBy.trtImg`, some trait image entries contain only
`trtVal` with no `img` key — meaning certain variation trait values have no associated
images. This is valid but not called out in the schema description of `ImagesVaryBy`.

---

### 4 — ItemKeyspace / BusinessPolicies

**File:** `ItemKeyspace/BusinessPolicies.json`
**Schema:** `itemkeyspace-business-policies.md`
**Rating:** 🟡 Partially aligned — `plcsId` prefix is wrong in docs (see Critical Corrections above)

Content fields (`retTrms`, `pmtTrms`, `shipTrms`) are fully aligned. Calculated
shipping records correctly carry `null` for `shpCost` / `addUnitCost` with a
non-null `pkgHndlgCost` — this pattern is not explained in the schema.

---

### 5 — ItemKeyspace / ItemCompatibility

**File:** `ItemKeyspace/ItemCompatibility.json`
**Schema:** `itemkeyspace-item-compatibility.md`
**Rating:** 🟢 Aligned

All 10 sample records show `compat`, `cmpCompat`, and `ftExempt` as `null`. This is
correct for non-automotive items that carry no fitment data. The `ItemCompID` prefix
`COMPAT_<itemId>` is confirmed by the data.

---

### 6 — ItemKeyspace / ItemDescription

**File:** `ItemKeyspace/ItemDescription.json`
**Schema:** `itemkeyspace-item-description.md`
**Rating:** 🟢 Aligned

`ItemDescID`, `desc`, `compDesc`, and `descRevsnDt` are all present. Some records
omit `compDesc` entirely; one record has `descRevsnDt: null`. Both are expected
optional states.

**Gap:** Schema should note that `compDesc` and `descRevsnDt` are nullable/optional.

---

### 7 — ItemKeyspace / ItemDetails

**File:** `ItemKeyspace/ItemDetails.json`
**Schema:** `itemkeyspace-item-details.md`
**Rating:** 🔴 Misaligned — see Critical Corrections above

Content-wise, `itemDetailsID` and `hasRlxdRls` match. Optional fields
(`fixedPriceHP`, `strtBidPriceHP`, `docs`, `srcLstId`) are absent from all samples
because the sample items do not require them — this is expected.

---

### 8 — ItemKeyspace / ItemKeyspace\_ROOT\_

**File:** `ItemKeyspace/ItemKeyspace_ROOT_.json`
**Schema:** `itemkeyspace-root.md`
**Rating:** 🟢 Aligned

The rich schema (50+ fields) is well-represented in sample data. All major embedded
objects (`lifecycle`, `trmsAndPolicies`, `tax`, `category`, `rgltryInfo`, `vslEncmt`,
`images`, `aspects`, `gblIdentifiers`) are present and correctly structured.

**Undocumented fields found in sample data:**

| Field in Data | Notes |
|---|---|
| `pk` (lowercase) | Appears alongside `PK` (uppercase) in some records; appears to be a lowercase alias or legacy duplicate |
| `images[].extPicUrl` | External picture URL present in some image entries alongside `eBayPicUrl`; not in the schema's `ImageMap` description |

---

### 9 — ItemKeyspace / ItemLock

**File:** `ItemKeyspace/ItemLock.json`
**Schema:** `itemkeyspace-item-lock.md`
**Rating:** 🟢 Aligned

All documented fields (`pk`, `st`, `qty`, `expDt`, `cmtDt`, `cnclDt`, `extDt`,
`extCnt`, `crtDt`, `modDt`, `uuid`) are present. The summary lock record
(`LOCK_$$$SUMMARY$$$`) uses the same schema with only the aggregate fields
populated — consistent with schema documentation.

**Observation:** The `qty` field is encoded inconsistently across records: some use
`{"$numberLong": "1"}` (MongoDB extended JSON), others use plain integer `1`. Both
represent the same value; the schema declares `long` which is correct in both forms.

---

### 10 — ItemKeyspace / ItemQtyPrice

**File:** `ItemKeyspace/ItemQtyPrice.json`
**Schema:** `itemkeyspace-item-qty-price.md`
**Rating:** 🔴 Misaligned — see Critical Corrections above, plus undocumented fields

Beyond the prefix error, two additional fields appear in sample data that are not
documented in the schema:

| Undocumented Field | Observed In | Notes |
|---|---|---|
| `lifecycle` | Ended items (e.g., `QTYPRICE_110833294592`) | Contains `endDt` and `schdldEndDt`; represents lifecycle data on items that have ended |
| `crLstgDtVrs` | Some records | Core listing data version string; documented in `ItemRoot` but not in this docset |

---

### 11 — ItemKeyspace / UuidMap

**File:** `ItemKeyspace/UuidMap.json`
**Schema:** `itemkeyspace-uuid-map.md`
**Rating:** 🟢 Aligned

`listingId` and `listingAppId` are present and correctly typed. The key shape
(`$UUIDMAP$_<sellerId>/<uuid>` encoded in `__key[0].string`) matches the schema
statement that seller ID and UUID are part of the key shape, not document fields.

---

### 12 — ListingDraft / ItemDraft

**File:** `ListingDraft/ItemDraft.json`
**Schema:** `listingdraft-item-draft.md`
**Rating:** 🟡 Partially aligned — undocumented fields

Content is broadly correct across the rich schema. Two fields present in sample data
are absent from the schema's field table:

| Undocumented Field | Notes |
|---|---|
| `origItmId` | Original item ID from which a Relist or SellSimilar draft was created; critical provenance field |
| `invTrkMth` | Abbreviated form of `invntryTrkMthd` (inventory tracking method); same semantics as `invntryTrkMthd` in `ItemRoot` but with a shortened field name |

---

### 13 — ListingDraft / ItemDraftCompatibility

**File:** `ListingDraft/ItemDraftCompatibility.json`
**Schema:** `listingdraft-item-draft-compatibility.md`
**Rating:** 🟢 Aligned

`DraftCompID`, `compat` (full `propertiesList` entries with `Car Make`, `Model`,
`Variant`, `BodyStyle`, `Plat_Gen`, `Cars Type`, `Cars Year`, `Engine`), and
`cmpCompat` (absent when no compressed form) are all consistent with schema.

---

### 14 — ListingDraft / ItemGroupDraft

**File:** `ListingDraft/ItemGroupDraft.json`
**Schema:** `listingdraft-item-group-draft.md`
**Rating:** 🟢 Aligned

All documented fields (`PK`, `grpTtl`, `imgsVryBy`, `img`, `itmsVryBy`,
`slrGrpKey`, `bizPol`, `grpId`) are present. The `grpId` value of `"0"` for
unpublished drafts is a valid sentinel value. The embedded `bizPol.plcsId` is `null`
for drafts that have not yet been assigned a policy ID.

---

### 15 — ListingDraft / ItemGroupDraftCompatibility

**File:** `ListingDraft/ItemGroupDraftCompatibility.json`
**Schema:** `listingdraft-item-group-draft-compatibility.md`
**Rating:** 🟢 Aligned

`DraftCompID` and `compat` (vehicle fitment entries) are present and correct.
`cmpCompat` is absent in samples (expected when no compressed form is written).

---

### 16 — ListingDraft / ItemGroupDraftDesc

**File:** `ListingDraft/ItemGroupDraftDesc.json`
**Schema:** `listingdraft-item-group-draft-desc.md`
**Rating:** 🟢 Aligned

`PK`, `groupDesc` are consistently present. `cmpDesc` and `grpDescRevsnDt` are
absent in several records — valid when no compressed description or revision
timestamp is stored.

---

### 17 — ListingDraft / ListingDraft\_ROOT\_

**File:** `ListingDraft/ListingDraft_ROOT_.json`
**Schema:** `listingdraft-root.md`
**Rating:** 🟢 Aligned

All documented fields are present. `usgHistDtl` correctly carries an array of
`{name: "CREATE"/"UPDATE"/"PUBLISH", value: "<appId>"}` entries. `appCstmInfo`
carries an XML string. Flag fields (`fl` through `fl12`, `scrtchFl` through
`scrtchFl4`) are present as documented.

**Observation:** `itmId` is typed `List<String>` in the schema but appears as `null`
at the root level in some records (rather than an empty list). This is a nullable
distinction the schema does not mention.

---

### 18 — ListingRevisionKeyspace / ListingRevision

**File:** `ListingRevisionKeyspace/ListingRevision.json`
**Schema:** `listingrevisionkeyspace-listing-revision.md`
**Rating:** 🟢 Aligned

All documented fields (`rvsdPrptyGrps`, `vrsnId`, `appId`, `sigRevCnt`, `vrsnCrtd`,
`rvsdDate`, `updCrLstgVrs`) are present and correctly typed. The GUID-style key
(`"guid": "AAdcK/x3..."`) for the `ListingRevision` collection is the NuDocument
internal multi-key format, consistent with the schema note that no persisted key
field exists on this class. `updCrLstgVrs` is absent on older revisions where no
version was created — expected.

---

### 19 — ListingRevisionKeyspace / ListingRevisionDetail

**File:** `ListingRevisionKeyspace/ListingRevisionDetail.json`
**Schema:** `listingrevisionkeyspace-listing-revision-detail.md`
**Rating:** 🟡 Partially aligned — one undocumented field

All core fields (`rvsdPrptyGrp`, `rvsdPrpty`, `chgTp`, `newVal`, `oldVal`) are
present. `lbl` is never observed in samples (optional and rarely populated).

**Undocumented field:**

| Field | Notes |
|---|---|
| `lstRvsnDtlId` | Appears as `{"reference": "<id>"}` in some records; appears to be a reference pointer used internally, not exposed as a Java property |

---

### 20 — ListingRevisionKeyspace / ListingRevisionKeyspace\_ROOT\_

**File:** `ListingRevisionKeyspace/ListingRevisionKeyspace_ROOT_.json`
**Schema:** `listingrevisionkeyspace-root.md`
**Rating:** 🟢 Aligned

`lstgId` and the TTL-maintenance `expiredDate` field (`{"$date": ...}`) are both
present. The schema explicitly acknowledges `expiredDate` as an operational field
not declared as a Java property, so its presence in sample data is expected.

---

### 21 — ListingRevisionKeyspace / VariationRevisionDetail

**File:** `ListingRevisionKeyspace/VariationRevisionDetail.json`
**Schema:** `listingrevisionkeyspace-variation-revision-detail.md`
**Rating:** 🟢 Aligned

`varId`, `rvsdPrptyGrp`, `rvsdVarPrpty`, `chgTp`, and `varTraitVals` are all
present and correctly structured. `newVal` and `oldVal` are absent for
`itmVarChg`/`add` change-type records — expected, since an addition has no prior
value. They are also absent for some `binPrc`/`rvsd` records, suggesting these
fields are conditionally populated.

---

### 22 — UserListingDraft / UserListingDraftMap

**File:** `UserListingDraft/UserListingDraftMap.json`
**Schema:** `userlistingdraft-user-item-draft-map.md`
**Rating:** 🟢 Aligned

All documented fields (`draftId`, `mktPlLstdOn`, `lstgAppId`, `primCatId`, `crtMd`,
`eBGenTtl`, `ttl`, `imgUrl`, `stockImgUrl`, `crtDt`, `userId`,
`lastModifiedDate`) are present and correctly typed.

**Undocumented field:**

| Field | Notes |
|---|---|
| `ebayGeneratedTitle` | Appears alongside `eBGenTtl` in some records as an expanded-name alias (value is always `null` when present); not documented in the schema field table |

---

## All Undocumented Fields Across the 22 Schemas

The table below consolidates every field observed in sample data that has no
corresponding entry in the schema documentation.

| Schema | Field | Type | Notes |
|---|---|---|---|
| `itemkeyspace-root.md` | `pk` (lowercase) | `String` | Lowercase alias of `PK`; appears in same records as the uppercase `PK` field |
| `itemkeyspace-root.md` | `images[].extPicUrl` | `String` | External (non-eBay) picture URL inside `ImageMap`; present on some listings |
| `itemkeyspace-item-qty-price.md` | `lifecycle` | Object | `endDt` + `schdldEndDt`; appears on ended/expired items in the `ItemQtyPrice` docset |
| `itemkeyspace-item-qty-price.md` | `crLstgDtVrs` | `String` | Core listing data version; documented in `ItemRoot` but also written to `ItemQtyPrice` on some paths |
| `listingdraft-item-draft.md` | `origItmId` | `String` | Original item ID for Relist / SellSimilar drafts |
| `listingdraft-item-draft.md` | `invTrkMth` | `String` (enum) | Abbreviated inventory tracking method; same semantics as `invntryTrkMthd` in `ItemRoot` |
| `listingrevisionkeyspace-listing-revision-detail.md` | `lstRvsnDtlId` | Object (`{reference}`) | Internal reference pointer; not declared as a Java property |
| `userlistingdraft-user-item-draft-map.md` | `ebayGeneratedTitle` | `String` | Expanded-name alias for `eBGenTtl`; always `null` in observed samples |

---

## Optional Fields That Should Be Called Out as Nullable

Several schemas describe fields without noting that they can be absent or `null` in
practice. The following table lists these, grouped by schema.

| Schema | Field | Observed as null/absent |
|---|---|---|
| `itemgroupkeyspace-group-description.md` | `compDesc` | Absent when no compressed form |
| `itemgroupkeyspace-group-description.md` | `grpDescRevsnDt` | Absent when no revision timestamp |
| `itemkeyspace-item-description.md` | `compDesc` | Absent or `null` when no compressed form |
| `itemkeyspace-item-description.md` | `descRevsnDt` | `null` on some records |
| `itemkeyspace-item-details.md` | `fixedPriceHP`, `strtBidPriceHP`, `docs`, `srcLstId` | Absent when not applicable |
| `itemkeyspace-item-qty-price.md` | `minRmntSet`, `qtySldByPickpStre` | Never observed; presumed absent when not set |
| `listingdraft-item-draft.md` | `docs`, `srcLstId` | Absent when not applicable |
| `listingdraft-item-group-draft-desc.md` | `cmpDesc`, `grpDescRevsnDt` | Absent in multiple records |
| `listingdraft-root.md` | `itmId` | `null` at root level rather than empty list |
| `listingrevisionkeyspace-listing-revision-detail.md` | `lbl` | Never observed in samples |
| `listingrevisionkeyspace-variation-revision-detail.md` | `newVal`, `oldVal` | Absent for `add`-type changes |
| `userlistingdraft-user-item-draft-map.md` | `eBGenTtl`, `stockImgUrl` | `null` or absent when not generated |

---

## Relationship to Existing Review Notes

Several findings here overlap with or extend the open items already tracked in
`ldm-review-notes.md`:

| Review Note | Related Finding Here |
|---|---|
| `ItemPriceAndQuantity` #1 — PK generation example | Corrects the prefix: `QTYPRICE_` not `QTY_PRICE_` |
| `ItemDetails` #1 — PK generation example | Corrects the prefix: `ITEMDET_` not `ITEM_DETAILS_` |
| `ItemBusinessPolicies` #1 — PK clarification | Corrects the prefix: `BIZPOL_` not `BIZ_POL_` |
| `ListingDraftItem` #2 — SSKU vs MSKU distinction | `origItmId` is the Relist/SellSimilar provenance field missing from the field table |
| Cross-cutting #2 — Docset ↔ docset mapping table | The undocumented-fields table above should feed into the comprehensive cross-reference table |
