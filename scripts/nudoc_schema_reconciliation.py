#!/usr/bin/env python3
"""Reconcile NuDocument source schemas with production sample observations."""

from __future__ import annotations

import argparse
import copy
import json
import re
from pathlib import Path
from typing import Any

try:
    from scripts.nudoc_sample_audit import (
        Docset,
        _load_json,
        _observed_paths,
        discover_docsets,
    )
except ModuleNotFoundError:
    from nudoc_sample_audit import Docset, _load_json, _observed_paths, discover_docsets


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]


class DescriptionResolutionError(ValueError):
    """Raised when an observed field is not supported by entity documentation."""


def _source_type(observed_types: set[str]) -> str:
    type_mapping = {
        "binary": "binary",
        "boolean": "boolean",
        "date": "date",
        "integer": "numberLong",
        "number": "numberDouble",
        "string": "string",
        "string[]": "string[]",
    }
    if observed_types == {"integer", "number"}:
        return "numberDouble"
    if len(observed_types) != 1:
        raise ValueError(
            "An observed field must have one compatible sample type: "
            f"{', '.join(sorted(observed_types))}"
        )
    try:
        return type_mapping[next(iter(observed_types))]
    except KeyError as error:
        raise ValueError(
            f"Unsupported observed sample type: {next(iter(observed_types))}"
        ) from error


def _is_type_compatible(source_type: str, observed_types: set[str]) -> bool:
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
    return observed_types <= compatibility.get(source_type, set())


def _documentation_descriptions(doc_path: Path) -> dict[str, str]:
    return {
        match.group(1): match.group(2).strip()
        for match in re.finditer(
            r"^\| `([^`]+)` \| [^|]* \| (.+) \|$",
            doc_path.read_text(encoding="utf-8"),
            flags=re.MULTILINE,
        )
    }


def _description_for_path(path: str, descriptions: dict[str, str]) -> str:
    if path in descriptions:
        return descriptions[path]

    segments = path.split(".")
    for index in range(len(segments) - 1, 0, -1):
        parent = ".".join(segments[:index])
        parent_description = descriptions.get(parent)
        if parent_description:
            remainder = ".".join(segments[index:])
            return f"{parent_description} Nested property: `{remainder}`."
    raise DescriptionResolutionError(
        f"No entity-page description supports observed field: {path}"
    )


def reconcile_schema(
    schema: dict[str, Any],
    observed_types: dict[str, set[str]],
    descriptions: dict[str, str],
) -> dict[str, Any]:
    """Return a schema with observed fields, types, and descriptions reconciled."""
    reconciled = copy.deepcopy(schema)
    columns = reconciled.get("Columns")
    if not isinstance(columns, list):
        raise ValueError("Schema must contain a Columns array")

    by_name = {
        column["name"]: column
        for column in columns
        if isinstance(column, dict) and isinstance(column.get("name"), str)
    }
    for name, column in by_name.items():
        if name == "__KEY":
            continue
        if name in observed_types and not _is_type_compatible(
            str(column.get("type", "")),
            observed_types[name],
        ):
            column["type"] = _source_type(observed_types[name])
        if not isinstance(column.get("comment"), str) or not column["comment"].strip():
            column["comment"] = _description_for_path(name, descriptions)

    for name in sorted(set(observed_types) - set(by_name)):
        columns.append(
            {
                "name": name,
                "type": _source_type(observed_types[name]),
                "comment": _description_for_path(name, descriptions),
                "nullable": None,
            }
        )
    return reconciled


def reconcile_docsets(docsets: tuple[Docset, ...]) -> dict[Path, dict[str, Any]]:
    """Build reconciled schemas for every documented production sample."""
    reconciled: dict[Path, dict[str, Any]] = {}
    for docset in docsets:
        schema = _load_json(docset.schema_path)
        if not isinstance(schema, dict):
            raise ValueError(f"Schema must be a JSON object: {docset.schema_path}")
        observed_types, _ = _observed_paths(_load_json(docset.sample_path))
        reconciled[docset.schema_path] = reconcile_schema(
            schema,
            observed_types,
            _documentation_descriptions(docset.doc_path),
        )
    return reconciled


def _serialize_schema(schema: dict[str, Any]) -> str:
    return json.dumps(schema, indent=4) + "\n"


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
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--check", action="store_true")
    action.add_argument("--apply", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    reconciled = reconcile_docsets(
        discover_docsets(args.data_dir, args.samples_dir, args.docs_dir)
    )
    changed_paths = [
        path
        for path, schema in reconciled.items()
        if path.read_text(encoding="utf-8") != _serialize_schema(schema)
    ]
    if args.apply:
        for path in changed_paths:
            path.write_text(_serialize_schema(reconciled[path]), encoding="utf-8")
            print(f"Reconciled {path}")
        return 0

    for path in changed_paths:
        print(f"Schema requires reconciliation: {path}")
    return 1 if changed_paths else 0


if __name__ == "__main__":
    raise SystemExit(main())
