# Raw NuDocument LDM requests

Each `*_schema.json` file is a source NuDocument schema. Its adjacent
`*_ldm_request.json` file is the generated MDM `LdmEntityRequest` used to
create the corresponding RAW LDM. Do not edit generated request files by
hand.

Generate all requests after changing a schema or its raw LDM documentation:

```bash
python3 scripts/generate_raw_ldm_payloads.py
```

Verify that every generated request is current:

```bash
python3 scripts/generate_raw_ldm_payloads.py --check
```

Generated RAW LDM requests expose first-level NuDocument fields only. A
first-level field with dotted source-schema descendants is emitted as an Avro
`string`; producers must serialize the complete object, struct, or array of
objects as a JSON string value. Direct first-level arrays are also emitted as
Avro `string` fields containing JSON array values. Only direct first-level
scalar fields retain their source types.

Audit every source schema against its paired production NuDocument sample and
emit a standalone Markdown report:

```bash
python3 scripts/nudoc_sample_audit.py --output /tmp/nudoc-sample-audit.md
```

Entity pages document first-level fields only. The audit therefore evaluates
entity-page coverage at that level, while schema comments still require direct
evidence for their exact field paths.

Reconcile observed sample fields and compatible types. Exact entity-page field
descriptions take precedence. When a required nested field has no exact
description, its comment is inferred from the nearest documented parent and
the child field name. For a field without a documented parent, reconciliation
uses the docset description and field name. These inferred comments are
explicitly labeled in the generated metadata; entity pages remain limited to
first-level fields. Review with `--check` first, then use `--apply`.

```bash
python3 scripts/nudoc_schema_reconciliation.py --check
python3 scripts/nudoc_schema_reconciliation.py --apply
```

Review the MDM creation plan without making network calls:

```bash
python3 scripts/create_raw_ldms.py
```

Preview one LDM, or repeat `--ldm` to select several:

```bash
python3 scripts/create_raw_ldms.py --ldm item_root --ldm item_details
```

To create missing LDMs, explicitly opt in and provide credentials through the
environment. `MDM_BASE_URL` must include the MDM API version path.

```bash
MDM_BASE_URL="https://mdm.example/gds/dec/api/v1" \
MDM_TOKEN="$MDM_TOKEN" \
MDM_TOKEN_PROVIDER="KEYSTONE" \
python3 scripts/create_raw_ldms.py --apply
```

Add `--ldm <name>` to `--apply` to create only selected LDMs. The submission
command rejects an unknown name before contacting MDM, preflights each selected
request by name and namespace, skips an existing matching LDM, and stops at
the first MDM error.
