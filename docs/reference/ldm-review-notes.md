# LDM Documentation Review Notes

This page captures open review comments collected from the Slack design review thread.
Each item is an action needed to improve the corresponding entity doc page.

---

## ItemKeyspace

### ItemRoot

| # | Comment | Action Needed |
|---|---------|---------------|
| 1 | **Key fields & field weights** — the current field table lists all fields with equal weight but some (e.g. `PK`, `sellerId`, `title`, `grpId`) are more critical than others | Add a "Key Fields" summary section that highlights the most-important fields and annotates each field row with an importance indicator (Primary / Core / Supporting) |
| 2 | **Docset ↔ related-docset mapping** — readers cannot easily see which sibling docsets belong to the same keyspace ancestor | Add a "Related LDMs in ItemKeyspace" table showing every sibling docset and the join key |
| 3 | **Keyspace link** — no deep-link to the ItemKeyspace keyspace definition | Add a "Keyspace" reference link in the Overview block |
| 4 | **Snapshot vs SCD** — `vrsnId` / `sigRevCnt` imply revision tracking; unclear whether this LDM uses snapshot or SCD2 | Clarify data-model pattern: is this a current-state snapshot (point-in-time) or SCD2? Add a note in Overview |

### ItemDescription

| # | Comment | Action Needed |
|---|---------|---------------|
| 1 | **PK generation example** — `ItemDescID` is generated as `DESC_<itemId>` but there is no worked example | Add an "ID Generation" sub-section: `ItemDescID = "DESC_" + itemId` with a concrete example (e.g. `DESC_123456789`) |
| 2 | **Join example with ItemRoot** — no SQL/query example showing how to join `ItemDescription` back to `ItemRoot` | Add a "Join Example" section: join on `DESC_<itemId>` ↔ `ItemRoot.PK` |

### ItemPriceAndQuantity

| # | Comment | Action Needed |
|---|---------|---------------|
| 1 | **PK generation example** — `ItemQtyPriceID` is generated as `QTY_PRICE_<itemId>` but no worked example | Add an "ID Generation" sub-section with a concrete example |
| 2 | **Join example with other LDMs** — no example showing how to join this LDM to ItemRoot or other sibling docsets | Add a "Join Example" section |
| 3 | **Quantity field explanations** — `availQty`, `qtySold`, `minRmntSet`, `qtySldByPickpStre` all track different quantities; their distinctions are unclear | Add a "Quantity Fields" explainer table clarifying what each qty field represents and when each is used |

### ItemDetails

| # | Comment | Action Needed |
|---|---------|---------------|
| 1 | **PK generation example** — `itemDetailsID` is generated as `ITEM_DETAILS_<itemId>` but no worked example | Add an "ID Generation" sub-section with a concrete example |
| 2 | **Join example with other LDMs** — no query showing how to join ItemDetails to ItemRoot or ItemPriceAndQuantity | Add a "Join Example" section |

### ItemCompatibility

| # | Comment | Action Needed |
|---|---------|---------------|
| 1 | **What is fitment?** — `ftmtId` in ItemRoot and `ftExempt` here reference "fitment" with no definition | Add a "Concepts" section explaining fitment: vehicle-parts compatibility data that maps items to specific vehicle year/make/model combinations |
| 2 | **PK generation example** — `ItemCompID` is generated as `COMPAT_<itemId>` but no worked example | Add an "ID Generation" sub-section with a concrete example |
| 3 | **Join example** — no query showing how to join ItemCompatibility to ItemRoot | Add a "Join Example" section |

### ItemBusinessPolicies

| # | Comment | Action Needed |
|---|---------|---------------|
| 1 | **PK clarification** — `plcsId` is listed as PK but its generation pattern is `BIZ_POL_<itemId>`; make this consistent with the other child docs | Add an "ID Generation" sub-section making the `BIZ_POL_<itemId>` pattern explicit |
| 2 | **`type` field is not a String** — a review comment flagged that the policy `type` is an enum, not a free-form string | Audit `retTrms`, `pmtTrms`, `shipTrms` sub-fields; update any incorrectly typed `String` fields to their actual enum types |

### ItemUUIDMapping

| # | Comment | Action Needed |
|---|---------|---------------|
| 1 | **Lookup semantics underexplained** — the doc says it's a "lookup structure" but does not explain when or why a consumer would query it vs. ItemRoot | Add a "Usage Pattern" section explaining: UUID is a seller-provided idempotency key; this table lets callers resolve a seller+UUID pair to the canonical `listingId` without scanning ItemRoot |

### ItemLock

| # | Comment | Action Needed |
|---|---------|---------------|
| 1 | **Lock state lifecycle** — the `st` field values (`A`, `C`, `X`) are listed but the state-transition lifecycle is not explained | Add a "Lock State Machine" section: `A` (Active) → `C` (Committed) or `X` (Cancelled); include what triggers each transition |

---

## ItemGroupKeyspace

### ItemGroupRoot

| # | Comment | Action Needed |
|---|---------|---------------|
| 1 | **PK has no business meaning** — `PK` is just "Identifier for the item group" with no indication of how it is generated or what it represents | Clarify: Is `PK` a system-generated UUID, a seller-provided key, or derived from a member item ID? Add generation details |
| 2 | **Join with ItemRoot** — no example showing how to join `ItemGroupRoot` (via `itemIds`) to `ItemKeyspace/ItemRoot` | Add a "Join Example" section: joining `ItemGroupRoot.itemIds` → `ItemRoot.PK` |
| 3 | **Join with Trait LDM** — group trait LDM (not yet documented) is mentioned as a future join partner | Add a placeholder note: "A Trait LDM is planned; it will join via `PK`" |

### ItemGroupDescription

| # | Comment | Action Needed |
|---|---------|---------------|
| 1 | **Join example with ItemGroupRoot** — no query showing how to join ItemGroupDescription to ItemGroupRoot | Add a "Join Example" section: join on `groupDescId` pattern ↔ `ItemGroupRoot.PK` |

### ItemGroupBusinessPolicies

| # | Comment | Action Needed |
|---|---------|---------------|
| 1 | **Comparison with ItemBusinessPolicies** — the doc says this inherits the same field shape but does not highlight what is the same vs. different | Add a "Comparison with ItemBusinessPolicies" table: same schema, different keyspace/ancestor, group-level scope vs. item-level scope |

---

## ListingDraft Keyspace

### ListingDraftRoot

| # | Comment | Action Needed |
|---|---------|---------------|
| 1 | **What is a "draft"?** — the business process behind listing drafts is not explained; readers don't know when a draft is created or when it gets promoted to a live listing | Add a "Business Context" section: a draft is a work-in-progress listing saved by the seller before publishing; it becomes a live item after the seller submits it |
| 2 | **PK business meaning** — `PK` is labeled "Draft root document identifier" with no explanation of its composition | Clarify: how is the draft `PK` generated? Is it a UUID assigned at draft-creation time? |
| 3 | **Many opaque flag fields** — `fl` through `fl12`, `scrtchFl` through `scrtchFl4` have no business semantics documented | Document what each flag/scratch field represents, or group them as "internal system flags — do not use for analytics" |

### ListingDraftItem

| # | Comment | Action Needed |
|---|---------|---------------|
| 1 | **Relationship with ListingDraftRoot** — the doc says this is a "child document" but the parent-child relationship (shared ancestor key) is not shown concretely | Add a diagram or table showing: `ListingDraftRoot.PK` = ancestor key shared by `ListingDraftItem.PK`; explain that PK for child docs is derived from the draft root key |
| 2 | **SSKU vs MSKU distinction** — mentioned in passing; how does the child set differ? | Add a "SSKU vs MSKU Draft Structure" table: SSKU = 1 `ItemDraft`; MSKU = N `ItemDraft` (one per variation) + `ItemGroupDraft` + `ItemGroupDraftDesc` |

### ListingDraftItemCompatibility

| # | Comment | Action Needed |
|---|---------|---------------|
| 1 | **Concrete data needed** — reviewers flagged that the compatibility structure (`compat` list) needs a data example to be meaningful | Add a "Data Example" section showing a sample `compat` list entry (year/make/model fitment row) |

### ListingDraftGroup

| # | Comment | Action Needed |
|---|---------|---------------|
| 1 | **SSKU vs MSKU** — the doc says SSKU drafts don't need this, but it's not explained why or what MSKU means in this context | Add an "MSKU vs SSKU" concept box: MSKU = Multi-SKU (variation listing with shared group + per-variation items); SSKU = Single-SKU (one item, no group) |
| 2 | **Relationship to ListingDraftRoot** — the parent-child link is not concretely shown | Add "Join / Ancestor" section clarifying the shared draft ancestor key |

### ListingDraftGroupCompatibility

| # | Comment | Action Needed |
|---|---------|---------------|
| 1 | **Relationship to ListingDraftItemCompatibility** — the two have identical schemas but different roles; the distinction is unclear | Add a "vs. ListingDraftItemCompatibility" comparison note: item-level compat = per-variation fitment; group-level compat = shared fitment for the whole MSKU group |
| 2 | **Concrete data needed** — same as ListingDraftItemCompatibility | Add a "Data Example" section |

### ListingDraftGroupDescription

| # | Comment | Action Needed |
|---|---------|---------------|
| 1 | **Join example with ListingDraftRoot and ListingDraftGroup** | Add a "Join Example" section showing how to retrieve the group description for a given draft |

### UserListingDraftMap

| # | Comment | Action Needed |
|---|---------|---------------|
| 1 | **Cross-LDM query example** — this is where the User LDM intersects with the Draft LDM; no example query shows how to look up all drafts for a user | Add a "Query Example" section: given a `userId`, join `UserListingDraftMap` → `ListingDraftRoot` → `ListingDraftItem` to retrieve full draft data |

---

## ListingRevisionKeyspace

### ListingRevisionRoot

| # | Comment | Action Needed |
|---|---------|---------------|
| 1 | **`listingId` is the PK** — the doc says "Key / Ancestor: `lstgId` identifies the listing" but the Overview PK field is blank; this should be consistent | Set `Primary Key: lstgId` in the Overview block |

### ListingRevision (previously called listingReviewDetails)

| # | Comment | Action Needed |
|---|---------|---------------|
| 1 | **No PK defined** — the schema class has no persisted key field; this is confusing for readers expecting a PK | Add an explicit note in Overview: "No persisted PK field — documents are addressed via the revision-history listing ancestor + `vrsnId`" |

### ListingVariationRevisionDetail

| # | Comment | Action Needed |
|---|---------|---------------|
| 1 | **Concrete data needed** — the `rvsdVarPrpty` and `varTraitVals` fields are opaque without examples | Add a "Data Example" section showing a before/after price change for a variation, including `varTraitVals` |

---

## Cross-Cutting Action Items

| # | Comment | Action Needed |
|---|---------|---------------|
| 1 | **Snapshot vs. SCD2 clarification** — `vrsnId` / `sigRevCnt` exist in ItemRoot; the LDM uses revision history (ListingRevisionKeyspace) separately; make the pattern explicit | Add a global note in the LDM Design Principle page (or ItemRoot): "ItemRoot is a **current-state snapshot**; historical changes are stored in ListingRevisionKeyspace as an append-only revision log — not SCD2 in the traditional sense" |
| 2 | **Docset ↔ Docset mapping table** — a single reference table showing all docsets, their keyspace, PK generation pattern, and sibling docsets is missing | Create or extend `reference/table-mappings.md` with a comprehensive cross-reference table |
| 3 | **Field importance weighting** — reviewers noted that not all fields carry equal weight for analytics consumers | Define a field-tier convention (Primary Key / Core Business / Supporting / Internal/Flag) and apply it across all entity pages |
