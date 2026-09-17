---
name: evidence-backed-raw-ldm-docs
description: Update RAW LDM entity documentation from production NuDocument evidence.
disable-model-invocation: true
---

# Evidence-Backed RAW LDM Documentation

Update Item-domain RAW LDM entity pages from their paired production
NuDocument samples and source schemas. Make documentation facts traceable to
the observed data and report limitations the available sample cannot resolve.

## Paired refresh

Use this as the first step after a developer changes RAW evidence under
`data/`. When the entity pages reflect that evidence, the user manually
invokes `/mdm-raw-ldm-requests` to reconcile source schemas and generate the
MDM request artifacts. This skill changes documentation only.

## Boundary

- **Inputs:** `data/**/*_schema.json`, paired samples under
  `data/sample-data/item-raw-ldm-samples/`, and mapped
  `docs/entities/*.md` pages.
- **Output:** evidence-backed edits to RAW entity Markdown pages only.
- **Scope:** RAW NuDocument LDMs only. Governed LDMs are outside this skill.
- **Excluded work:** source-schema JSON, generated MDM request JSON, MDM
  operations, source scripts, and MkDocs generation.

## Evidence workflow

1. Determine the affected RAW docsets. Use a requested docset when one is
   provided; otherwise inspect changed evidence:

   ```bash
   git status --short -- data
   ```

   Scope documentation updates to changed `*_schema.json` files and paired
   production samples. Map each source docset to the entity page reported by
   the audit. The source `UserListingDraft/UserListingDraftMap` maps to the
   documented `UserItemDraftMap` docset.

2. Audit the repository evidence:

   ```bash
   python3 scripts/nudoc_sample_audit.py --output /tmp/nudoc-sample-audit.md
   ```

   Read the affected docset section before editing. Use it to identify
   observed paths and types, sample-only paths, type mismatches, missing
   descriptions, undocumented top-level fields, and unobservable paths.

3. Compare the audit findings with the paired `*_schema.json` and current
   entity page. Production samples establish observed representations; the
   source schema provides the current declared field metadata. When they
   conflict, correct the page only for the observed fact and report the
   schema discrepancy. Keep the source schema unchanged.

4. Update every relevant, evidence-backed entity-page statement.
   - Add or correct observed top-level field-table entries, types, and
     descriptions.
   - Update overview text, key-shape examples, nullable/optional behavior,
     and other factual notes only when the evidence supports the change.
   - Express a recurring sample pattern as an observation unless evidence
     establishes it as a universal contract.
   - Keep fields at the first level. Explain nested properties through their
     top-level field's description; never add flattened nested-path rows.
   - Retain a documented field that is absent from the sample and report it
     as an evidence coverage gap. Absence from a finite sample is not grounds
     to remove it.

5. Prefer direct source or existing page descriptions. If none exists, use
   the repository's labeled inference from a documented parent or docset
   description. Keep inferred wording clearly distinguishable from observed
   facts, and surface any remaining unresolved evidence.

6. Rerun the audit after editing:

   ```bash
   python3 scripts/nudoc_sample_audit.py --output /tmp/nudoc-sample-audit.md
   ```

   Verify that the entity page documents every observed top-level field and
   that the report accurately preserves any unobserved coverage gaps.

## Completion

Finish when all requested RAW entity-page corrections are evidence-backed and
reported with their entity-page, schema, and sample paths. Report the exact
documentation changes and unresolved coverage gaps.

Keep schema reconciliation, generated request artifacts, MDM submission, and
site builds outside this workflow. Do not run generation or freshness checks
for generated request artifacts; the user invokes `/mdm-raw-ldm-requests`
after this documentation step.

## Validation

Run the repository's existing unit suite after completing page updates:

```bash
python3 -m unittest discover -s tests -v
```

`data/README.md` remains the source of truth for source-schema reconciliation
and MDM request generation.
