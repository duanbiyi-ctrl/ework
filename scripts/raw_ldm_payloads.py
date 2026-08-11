"""Build deterministic MDM RAW LDM requests from NuDocument schemas."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any


MDM_METADATA = {
    "namespaceId": 114,
    "owners": "jiajsun",
    "domain": "GDS",
    "jiraProject": "GDS",
    "team": "GDS",
    "teamDl": "DL-eBay-GDS@ebay.com",
    "environment": "UNSTAGED",
    "status": "DRAFT",
}

COMPOSITE_PRIMARY_KEYS = {
    ("ItemKeyspace", "UuidMap"): "sellerId,uuid",
    ("UserListingDraft", "UserItemDraftMap"): "userId,draftId",
}

DOCSET_ALIASES = {
    ("UserListingDraft", "UserListingDraftMap"): "UserItemDraftMap",
}

AVRO_TYPE_MAPPING = {
    "STR": {"type": "string", "avro.java.string": "String", "default": None},
    "string": {"type": "string", "avro.java.string": "String", "default": None},
    "boolean": {"type": "boolean", "default": None},
    "number": {"type": "double", "default": None},
    "numberDouble": {"type": "double", "default": None},
    "numberInt": {"type": "int", "default": None},
    "numberLong": {"type": "long", "default": None},
    "binary": {"type": "bytes", "default": None},
    "string[]": {"type": "array", "items": "string", "default": None},
    "date": {"type": "int", "logicalType": "date", "default": None},
}


class MetadataResolutionError(ValueError):
    """Raised when a raw schema cannot be mapped to a documented LDM."""


@dataclass(frozen=True)
class DocumentMetadata:
    keyspace: str
    docset: str
    name: str
    description: str
    primary_key: str | None


@dataclass(frozen=True)
class PayloadArtifact:
    schema_path: Path | None
    output_path: Path | None
    payload: dict[str, Any]


def encode_avro_type(nudocument_type: str) -> str:
    """Return the PyDEC-compatible serialized Avro schema for a source type."""
    try:
        avro_schema = AVRO_TYPE_MAPPING[nudocument_type]
    except KeyError as error:
        raise ValueError(
            f"Unsupported NuDocument field type: {nudocument_type}"
        ) from error
    return json.dumps(avro_schema, separators=(",", ":"))


def _read_document_value(markdown: str, label: str) -> str | None:
    match = re.search(
        rf"^\*\*{re.escape(label)}:\*\*\s*(.+?)\s*$",
        markdown,
        flags=re.MULTILINE,
    )
    if not match:
        return None
    return match.group(1).strip().strip("`")


def _to_snake_case(value: str) -> str:
    without_suffix = re.sub(r"\s+LDM$", "", value).strip()
    first_pass = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1_\2", without_suffix)
    second_pass = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", first_pass)
    return second_pass.replace("-", "_").replace(" ", "_").lower()


def _document_primary_key(
    keyspace: str,
    docset: str,
    documented_primary_key: str | None,
) -> str | None:
    composite_key = COMPOSITE_PRIMARY_KEYS.get((keyspace, docset))
    if composite_key:
        return composite_key
    if documented_primary_key:
        return documented_primary_key
    return None


def index_documentation(docs_dir: Path) -> dict[tuple[str, str], DocumentMetadata]:
    """Index raw LDM documentation by its physical keyspace and docset."""
    documents: dict[tuple[str, str], DocumentMetadata] = {}

    for path in sorted(docs_dir.glob("*.md")):
        markdown = path.read_text(encoding="utf-8")
        keyspace = _read_document_value(markdown, "Keyspace")
        docset = _read_document_value(markdown, "NuDocument Docset")
        ldm_name = _read_document_value(markdown, "LDM Name")
        description = _read_document_value(markdown, "Description")
        if not all((keyspace, docset, ldm_name, description)):
            continue

        key = (keyspace, docset)
        if key in documents:
            raise MetadataResolutionError(
                f"Multiple LDM pages describe {keyspace}/{docset}"
            )

        documents[key] = DocumentMetadata(
            keyspace=keyspace,
            docset=docset,
            name=_to_snake_case(ldm_name),
            description=description,
            primary_key=_document_primary_key(
                keyspace,
                docset,
                _read_document_value(markdown, "Primary Key"),
            ),
        )

    return documents


def _source_docset(data_table_name: str) -> str:
    return data_table_name.rsplit(".", maxsplit=1)[-1]


def _artifact_path(schema_path: Path) -> Path:
    schema_stem = schema_path.stem.removesuffix("_schema")
    return schema_path.with_name(f"{schema_stem}_ldm_request.json")


def _build_field(column: dict[str, Any], ordinal: int) -> dict[str, Any]:
    name = column.get("name")
    source_type = column.get("type")
    if not isinstance(name, str) or not name:
        raise MetadataResolutionError("NuDocument columns must have a non-empty name")
    if not isinstance(source_type, str) or not source_type:
        raise MetadataResolutionError(
            f"NuDocument column {name} must have a non-empty type"
        )

    field = {
        "name": name,
        "hierarchicalName": name,
        "dataType": encode_avro_type(source_type),
        "ordinal": ordinal,
        "signalFilter": [],
        "signalMapping": [],
        "physicalStorageMapping": [],
    }
    if column.get("comment"):
        field["description"] = str(column["comment"])
    if column.get("nullable") is not None:
        field["dataSchema"] = {"nullable": bool(column["nullable"])}
    return field


def _read_schema(path: Path) -> dict[str, Any]:
    try:
        schema = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise MetadataResolutionError(f"Invalid JSON schema: {path}") from error
    if not isinstance(schema, dict):
        raise MetadataResolutionError(f"Schema must be a JSON object: {path}")
    return schema


def build_payloads(data_dir: Path, docs_dir: Path) -> list[PayloadArtifact]:
    """Create MDM requests for every raw NuDocument schema without writing them."""
    documentation = index_documentation(docs_dir)
    artifacts: list[PayloadArtifact] = []

    for schema_path in sorted(data_dir.rglob("*_schema.json")):
        schema = _read_schema(schema_path)
        keyspace = schema.get("DataStoreName")
        data_table_name = schema.get("DataTableName")
        columns = schema.get("Columns")
        if not isinstance(keyspace, str) or not isinstance(data_table_name, str):
            raise MetadataResolutionError(
                f"Schema must contain DataStoreName and DataTableName: {schema_path}"
            )
        if not isinstance(columns, list):
            raise MetadataResolutionError(
                f"Schema must contain a Columns array: {schema_path}"
            )

        docset = _source_docset(data_table_name)
        documented_docset = DOCSET_ALIASES.get((keyspace, docset), docset)
        try:
            document = documentation[(keyspace, documented_docset)]
        except KeyError as error:
            raise MetadataResolutionError(
                f"No raw LDM page maps {keyspace}/{documented_docset} from {schema_path}"
            ) from error

        fields = [_build_field(column, ordinal) for ordinal, column in enumerate(columns, 1)]
        if len({field["name"] for field in fields}) != len(fields):
            raise MetadataResolutionError(
                f"Schema contains duplicate column names: {schema_path}"
            )

        payload = {
            "name": document.name,
            "viewType": "RAW",
            "description": document.description,
            **MDM_METADATA,
            "udfs": [],
            "dcsFields": [],
            "fields": fields,
            "errorHandlingStorageMappings": [],
        }
        if document.primary_key:
            payload["pk"] = document.primary_key

        artifacts.append(
            PayloadArtifact(
                schema_path=schema_path,
                output_path=_artifact_path(schema_path),
                payload=payload,
            )
        )

    if not artifacts:
        raise MetadataResolutionError(f"No NuDocument schemas found in {data_dir}")

    names = [artifact.payload["name"] for artifact in artifacts]
    if len(set(names)) != len(names):
        raise MetadataResolutionError("Multiple schemas resolve to the same LDM name")

    return artifacts


def serialize_payload(payload: dict[str, Any]) -> str:
    return json.dumps(payload, indent=2, sort_keys=True) + "\n"


def generate_artifacts(data_dir: Path, docs_dir: Path) -> list[Path]:
    """Write each generated LDM request alongside its NuDocument schema."""
    output_paths: list[Path] = []
    for artifact in build_payloads(data_dir, docs_dir):
        if artifact.output_path is None:
            raise MetadataResolutionError("Generated payload is missing an output path")
        artifact.output_path.write_text(
            serialize_payload(artifact.payload),
            encoding="utf-8",
        )
        output_paths.append(artifact.output_path)
    return output_paths


def check_artifacts(data_dir: Path, docs_dir: Path) -> list[Path]:
    """Return missing, stale, or orphaned generated request artifact paths."""
    artifacts = build_payloads(data_dir, docs_dir)
    expected = {
        artifact.output_path: serialize_payload(artifact.payload)
        for artifact in artifacts
        if artifact.output_path is not None
    }
    stale = [
        path
        for path, expected_content in expected.items()
        if not path.exists() or path.read_text(encoding="utf-8") != expected_content
    ]
    orphaned = set(data_dir.rglob("*_ldm_request.json")) - set(expected)
    return sorted(stale + list(orphaned))
