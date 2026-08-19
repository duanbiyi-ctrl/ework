#!/usr/bin/env python3
"""Audit NuDocument schemas against their paired production samples."""

from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
DOCSET_ALIASES = {
    ("UserListingDraft", "UserListingDraftMap"): "UserItemDraftMap",
}
INTERNAL_SAMPLE_PATHS = {"__KEY", "__key", "__meta"}
EXTENDED_JSON_TYPES = {
    "$binary": "binary",
    "$date": "date",
    "$numberDecimal": "number",
    "$numberDouble": "number",
    "$numberInt": "integer",
    "$numberLong": "integer",
    "$oid": "string",
    "$uuid": "string",
}


@dataclass(frozen=True)
class Docset:
    """The source, sample, and documentation inputs for one NuDocument docset."""

    keyspace: str
    docset: str
    schema_path: Path
    sample_path: Path
    doc_path: Path


@dataclass(frozen=True)
class AuditResult:
    """The observed contract result for one NuDocument docset."""

    docset: Docset
    observed_paths: tuple[str, ...]
    sample_only_paths: tuple[str, ...]
    schema_only_paths: tuple[str, ...]
    type_mismatches: tuple[str, ...]
    missing_descriptions: tuple[str, ...]
    undocumented_paths: tuple[str, ...]
    unobservable_paths: tuple[str, ...]


def _document_value(markdown: str, label: str) -> str | None:
    match = re.search(
        rf"^\*\*{re.escape(label)}:\*\*\s*(.+?)\s*$",
        markdown,
        flags=re.MULTILINE,
    )
    return match.group(1).strip().strip("`") if match else None


def _source_docset(schema: dict[str, Any]) -> str:
    table_name = schema.get("DataTableName")
    if not isinstance(table_name, str):
        raise ValueError("Schema is missing a DataTableName")
    return table_name.rsplit(".", maxsplit=1)[-1]


def _document_docset(keyspace: str, docset: str) -> str:
    return DOCSET_ALIASES.get((keyspace, docset), docset)


def _load_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as file:
        return json.load(file)


def _load_object(path: Path) -> dict[str, Any]:
    value = _load_json(path)
    if not isinstance(value, dict):
        raise ValueError(f"Expected a JSON object: {path}")
    return value


def _documentation_index(docs_dir: Path) -> dict[tuple[str, str], Path]:
    documents: dict[tuple[str, str], Path] = {}
    for path in sorted(docs_dir.glob("*.md")):
        markdown = path.read_text(encoding="utf-8")
        keyspace = _document_value(markdown, "Keyspace")
        docset = _document_value(markdown, "NuDocument Docset")
        if not keyspace or not docset:
            continue
        key = (keyspace, docset)
        if key in documents:
            raise ValueError(f"Multiple documentation pages describe {keyspace}/{docset}")
        documents[key] = path
    return documents


def _sample_path(samples_dir: Path, keyspace: str, docset: str) -> Path:
    filename = f"{keyspace}_ROOT_.json" if docset == "__ROOT__" else f"{docset}.json"
    return samples_dir / keyspace / filename


def discover_docsets(data_dir: Path, samples_dir: Path, docs_dir: Path) -> tuple[Docset, ...]:
    """Discover every source schema and require its sample and entity page."""
    documentation = _documentation_index(docs_dir)
    docsets: list[Docset] = []

    for schema_path in sorted(data_dir.rglob("*_schema.json")):
        schema = _load_object(schema_path)
        keyspace = schema.get("DataStoreName")
        if not isinstance(keyspace, str) or not keyspace:
            raise ValueError(f"Schema is missing DataStoreName: {schema_path}")
        docset = _source_docset(schema)
        sample_path = _sample_path(samples_dir, keyspace, docset)
        if not sample_path.is_file():
            raise ValueError(f"Missing production sample for {keyspace}/{docset}: {sample_path}")
        documented_docset = _document_docset(keyspace, docset)
        try:
            doc_path = documentation[(keyspace, documented_docset)]
        except KeyError as error:
            raise ValueError(
                f"Missing entity page for {keyspace}/{documented_docset}"
            ) from error
        docsets.append(
            Docset(
                keyspace=keyspace,
                docset=docset,
                schema_path=schema_path,
                sample_path=sample_path,
                doc_path=doc_path,
            )
        )

    if not docsets:
        raise ValueError(f"No NuDocument schemas found under {data_dir}")
    return tuple(docsets)


def _record_observed_value(
    values: dict[str, set[str]],
    unobservable: set[str],
    path: str,
    value: Any,
) -> None:
    if value is None:
        unobservable.add(path)
    elif isinstance(value, bool):
        values[path].add("boolean")
    elif isinstance(value, int):
        values[path].add("integer")
    elif isinstance(value, float):
        values[path].add("number")
    elif isinstance(value, str):
        values[path].add("string")
    else:
        raise ValueError(f"Unexpected scalar at {path}: {type(value).__name__}")


def _extended_json_type(value: dict[str, Any]) -> str | None:
    type_keys = set(value) & set(EXTENDED_JSON_TYPES)
    if len(type_keys) != 1:
        return None
    type_key = type_keys.pop()
    allowed_keys = {type_key}
    if type_key == "$binary":
        allowed_keys.add("$type")
    return EXTENDED_JSON_TYPES[type_key] if set(value) <= allowed_keys else None


def _observe(
    value: Any,
    path: str,
    values: dict[str, set[str]],
    unobservable: set[str],
) -> None:
    if isinstance(value, dict):
        extended_type = _extended_json_type(value)
        if extended_type:
            values[path].add(extended_type)
            return
        if not value:
            unobservable.add(path)
        for name, child in value.items():
            child_path = f"{path}.{name}" if path else name
            _observe(child, child_path, values, unobservable)
        return

    if isinstance(value, list):
        if not value:
            unobservable.add(path)
            return
        if all(not isinstance(item, (dict, list)) for item in value):
            if all(isinstance(item, str) for item in value):
                values[path].add("string[]")
            else:
                values[path].add("array")
            return
        for item in value:
            _observe(item, path, values, unobservable)
        return

    _record_observed_value(values, unobservable, path, value)


def _observed_paths(sample: Any) -> tuple[dict[str, set[str]], set[str]]:
    values: dict[str, set[str]] = defaultdict(set)
    unobservable: set[str] = set()
    documents = [sample] if isinstance(sample, dict) else sample
    if not isinstance(documents, list) or not all(
        isinstance(document, dict) for document in documents
    ):
        raise ValueError("A production sample must be an object or an array of objects")
    for document in documents:
        for name, value in document.items():
            if name in INTERNAL_SAMPLE_PATHS:
                continue
            _observe(value, name, values, unobservable)
    return values, unobservable


def _is_type_compatible(expected_type: str, observed_types: set[str]) -> bool:
    compatibility = {
        "string": {"string"},
        "boolean": {"boolean"},
        "number": {"integer", "number"},
        "numberDouble": {"integer", "number"},
        "numberInt": {"integer"},
        "numberLong": {"integer"},
        "binary": {"binary", "string"},
        "string[]": {"string[]"},
        "date": {"date", "string"},
    }
    return observed_types <= compatibility.get(expected_type, set())


def _documented_fields(doc_path: Path) -> set[str]:
    fields: set[str] = set()
    for line in doc_path.read_text(encoding="utf-8").splitlines():
        match = re.match(r"^\| `([^`]+)` \|", line)
        if match:
            fields.add(match.group(1))
    return fields


def _is_documented(path: str, fields: set[str]) -> bool:
    return path in fields


def audit_docsets(docsets: tuple[Docset, ...]) -> tuple[AuditResult, ...]:
    """Compare schema field paths, types, descriptions, and docs to samples."""
    results: list[AuditResult] = []
    for docset in docsets:
        schema = _load_object(docset.schema_path)
        columns = [
            column
            for column in schema.get("Columns", [])
            if column.get("name") != "__KEY"
        ]
        schema_columns = {
            column["name"]: column
            for column in columns
            if isinstance(column.get("name"), str)
        }
        observed, unobservable = _observed_paths(_load_json(docset.sample_path))
        documented_fields = _documented_fields(docset.doc_path)

        sample_only = sorted(set(observed) - set(schema_columns))
        schema_only = sorted(set(schema_columns) - set(observed) - unobservable)
        type_mismatches = sorted(
            path
            for path, observed_types in observed.items()
            if path in schema_columns
            and not _is_type_compatible(
                str(schema_columns[path].get("type", "")),
                observed_types,
            )
        )
        missing_descriptions = sorted(
            path
            for path, column in schema_columns.items()
            if not isinstance(column.get("comment"), str)
            or not column["comment"].strip()
        )
        undocumented = sorted(
            path for path in observed if not _is_documented(path, documented_fields)
        )

        results.append(
            AuditResult(
                docset=docset,
                observed_paths=tuple(sorted(observed)),
                sample_only_paths=tuple(sample_only),
                schema_only_paths=tuple(schema_only),
                type_mismatches=tuple(type_mismatches),
                missing_descriptions=tuple(missing_descriptions),
                undocumented_paths=tuple(undocumented),
                unobservable_paths=tuple(sorted(unobservable)),
            )
        )
    return tuple(results)


def _markdown_list(paths: tuple[str, ...]) -> str:
    return ", ".join(f"`{path}`" for path in paths) if paths else "None."


def render_markdown(results: tuple[AuditResult, ...]) -> str:
    """Render a standalone, per-docset Markdown audit report."""
    lines = [
        "# NuDocument schema/sample audit",
        "",
        f"Reviewed **{len(results)}** source-schema, production-sample, and entity-page triples.",
        "",
        "| Keyspace | Docset | Observed fields | Sample-only | Type mismatches | Missing descriptions | Undocumented |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for result in results:
        lines.append(
            "| "
            f"{result.docset.keyspace} | {result.docset.docset} | "
            f"{len(result.observed_paths)} | {len(result.sample_only_paths)} | "
            f"{len(result.type_mismatches)} | {len(result.missing_descriptions)} | "
            f"{len(result.undocumented_paths)} |"
        )

    for result in results:
        lines.extend(
            [
                "",
                f"## {result.docset.keyspace} / {result.docset.docset}",
                "",
                f"- **Schema:** `{result.docset.schema_path}`",
                f"- **Sample:** `{result.docset.sample_path}`",
                f"- **Entity page:** `{result.docset.doc_path}`",
                f"- **Sample-only paths:** {_markdown_list(result.sample_only_paths)}",
                f"- **Schema-only paths:** {_markdown_list(result.schema_only_paths)}",
                f"- **Type mismatches:** {_markdown_list(result.type_mismatches)}",
                f"- **Missing schema descriptions:** {_markdown_list(result.missing_descriptions)}",
                f"- **Undocumented observed paths:** {_markdown_list(result.undocumented_paths)}",
                f"- **Unobservable paths:** {_markdown_list(result.unobservable_paths)}",
            ]
        )
    return "\n".join(lines) + "\n"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, default=REPOSITORY_ROOT / "data")
    parser.add_argument(
        "--samples-dir",
        type=Path,
        default=REPOSITORY_ROOT / "data" / "sample-data" / "item-raw-ldm-samples",
    )
    parser.add_argument(
        "--docs-dir",
        type=Path,
        default=REPOSITORY_ROOT / "docs" / "entities",
    )
    parser.add_argument("--output", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report = render_markdown(
        audit_docsets(discover_docsets(args.data_dir, args.samples_dir, args.docs_dir))
    )
    if args.output:
        args.output.write_text(report, encoding="utf-8")
    else:
        print(report, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
