"""Resolve NuDocument field descriptions from Java source and curated evidence."""

from __future__ import annotations

import copy
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any


DOCSET_ALIASES = {
    ("UserListingDraft", "UserListingDraftMap"): "UserItemDraftMap",
}


class DescriptionResolutionError(ValueError):
    """Raised when an emitted NuDocument field has no source-backed description."""


@dataclass(frozen=True)
class JavaField:
    name: str
    json_name: str
    type_name: str
    description: str | None


@dataclass(frozen=True)
class JavaModel:
    qualified_name: str
    parent_name: str | None
    fields: tuple[JavaField, ...]


@dataclass(frozen=True)
class DocumentSource:
    source_class: str
    field_descriptions: dict[str, str]


FIELD_PATTERN = re.compile(
    r"(?P<annotations>(?:\s*@\w+(?:\s*\([^;]*?\))?\s*)*)"
    r"(?:private|protected|public)\s+(?:static\s+)?(?:final\s+)?"
    r"(?P<type>[\w<>, ?\[\].]+?)\s+(?P<name>\w+)\s*;",
    flags=re.DOTALL,
)


def _annotation_value(annotations: str, annotation: str) -> str | None:
    match = re.search(
        rf"@{annotation}\s*\(\s*(?:value\s*=\s*)?\"(?P<value>(?:\\.|[^\"\\])*)\"",
        annotations,
        flags=re.DOTALL,
    )
    if not match:
        return None
    return bytes(match.group("value"), "utf-8").decode("unicode_escape").strip()


def _annotation_json_name(annotations: str, fallback: str) -> str:
    return _annotation_value(annotations, "JsonProperty") or fallback


def _simple_type_name(type_name: str) -> str | None:
    normalized = re.sub(r"@\w+(?:\([^)]*\))?\s*", "", type_name)
    normalized = normalized.replace("[]", "").strip()
    generic = re.search(r"<\s*(?:\?\s*(?:extends|super)\s+)?([\w.]+)", normalized)
    candidate = generic.group(1) if generic else normalized.split()[-1]
    candidate = candidate.rsplit(".", maxsplit=1)[-1]
    if candidate in {
        "Boolean",
        "Byte",
        "Character",
        "Double",
        "Float",
        "Integer",
        "Long",
        "Short",
        "String",
        "Object",
    }:
        return None
    return candidate


def index_java_models(source_root: Path) -> dict[str, JavaModel]:
    """Index Java models and their field annotations by qualified class name."""
    models: dict[str, JavaModel] = {}
    for path in source_root.rglob("*.java"):
        source = path.read_text(encoding="utf-8")
        package_match = re.search(r"^\s*package\s+([\w.]+)\s*;", source, re.MULTILINE)
        class_match = re.search(
            r"\bclass\s+(\w+)(?:\s+extends\s+([\w.]+))?",
            source,
        )
        if not package_match or not class_match:
            continue

        package = package_match.group(1)
        class_name = class_match.group(1)
        parent_name = class_match.group(2)
        if parent_name and "." not in parent_name:
            parent_name = f"{package}.{parent_name}"
        fields = []
        for match in FIELD_PATTERN.finditer(source):
            annotations = match.group("annotations")
            name = match.group("name")
            fields.append(
                JavaField(
                    name=name,
                    json_name=_annotation_json_name(annotations, name),
                    type_name=match.group("type").strip(),
                    description=_annotation_value(annotations, "ApiDescription"),
                )
            )
        qualified_name = f"{package}.{class_name}"
        models[qualified_name] = JavaModel(
            qualified_name=qualified_name,
            parent_name=parent_name,
            fields=tuple(fields),
        )
    return models


def _model_by_simple_name(
    type_name: str,
    current_model: JavaModel,
    models: dict[str, JavaModel],
) -> JavaModel | None:
    simple_name = _simple_type_name(type_name)
    if not simple_name:
        return None
    same_package = f"{current_model.qualified_name.rsplit('.', maxsplit=1)[0]}.{simple_name}"
    if same_package in models:
        return models[same_package]
    matches = [
        model
        for qualified_name, model in models.items()
        if qualified_name.endswith(f".{simple_name}")
    ]
    return matches[0] if len(matches) == 1 else None


def _find_field(
    model: JavaModel,
    segment: str,
    models: dict[str, JavaModel],
) -> JavaField | None:
    for field in model.fields:
        if segment in {field.name, field.json_name}:
            return field
    if model.parent_name and model.parent_name in models:
        return _find_field(models[model.parent_name], segment, models)
    return None


def _source_description(
    model_name: str,
    field_path: str,
    models: dict[str, JavaModel],
) -> str | None:
    model = models.get(model_name)
    if not model:
        return None

    segments = field_path.split(".")
    for index, segment in enumerate(segments):
        field = _find_field(model, segment, models)
        if not field:
            return None
        if index == len(segments) - 1:
            return field.description
        model = _model_by_simple_name(field.type_name, model, models)
        if not model:
            return None
    return None


def resolve_descriptions(
    model_name: str,
    field_paths: list[str],
    models: dict[str, JavaModel],
    documentation_descriptions: dict[str, str],
    overrides: dict[str, str],
) -> dict[str, str]:
    """Resolve source-backed descriptions, rejecting any unresolved field."""
    descriptions: dict[str, str] = {}
    unresolved: list[str] = []
    for field_path in field_paths:
        description = (
            _source_description(model_name, field_path, models)
            or documentation_descriptions.get(field_path)
            or overrides.get(field_path)
        )
        if description and description.strip():
            descriptions[field_path] = description.strip()
        else:
            unresolved.append(field_path)
    if unresolved:
        raise DescriptionResolutionError(
            f"Missing source-backed descriptions for: {', '.join(unresolved)}"
        )
    return descriptions


def apply_descriptions(
    schema: dict[str, Any],
    descriptions: dict[str, str],
) -> dict[str, Any]:
    """Return a schema copy with descriptions written to column comments."""
    enriched = copy.deepcopy(schema)
    for column in enriched.get("Columns", []):
        name = column.get("name")
        if name in descriptions:
            column["comment"] = descriptions[name]
    return enriched


def _document_value(markdown: str, label: str) -> str | None:
    match = re.search(
        rf"^\*\*{re.escape(label)}:\*\*\s*(.+?)\s*$",
        markdown,
        flags=re.MULTILINE,
    )
    return match.group(1).strip().strip("`") if match else None


def index_document_sources(docs_dir: Path) -> dict[tuple[str, str], DocumentSource]:
    """Read Java source-class and direct field descriptions from raw LDM pages."""
    sources: dict[tuple[str, str], DocumentSource] = {}
    for path in docs_dir.glob("*.md"):
        markdown = path.read_text(encoding="utf-8")
        keyspace = _document_value(markdown, "Keyspace")
        docset = _document_value(markdown, "NuDocument Docset")
        source_class = _document_value(markdown, "Source Class")
        if not all((keyspace, docset, source_class)):
            continue
        descriptions = {
            match.group(1): match.group(2).strip()
            for match in re.finditer(
                r"^\| `([^`]+)` \| [^|]* \| (.+) \|$",
                markdown,
                flags=re.MULTILINE,
            )
        }
        sources[(keyspace, docset)] = DocumentSource(
            source_class=source_class,
            field_descriptions=descriptions,
        )
    return sources


def _schema_key(schema: dict[str, Any]) -> tuple[str, str]:
    keyspace = schema.get("DataStoreName")
    table_name = schema.get("DataTableName")
    if not isinstance(keyspace, str) or not isinstance(table_name, str):
        raise DescriptionResolutionError("Schema is missing DataStoreName or DataTableName")
    docset = table_name.rsplit(".", maxsplit=1)[-1]
    return keyspace, DOCSET_ALIASES.get((keyspace, docset), docset)


def load_overrides(path: Path) -> dict[str, dict[str, str]]:
    """Load a schema-keyed, reviewed field-description override map."""
    if not path.exists():
        return {}
    raw = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise DescriptionResolutionError("Description overrides must be a JSON object")
    overrides: dict[str, dict[str, str]] = {}
    for schema_key, fields in raw.items():
        if not isinstance(fields, dict):
            raise DescriptionResolutionError(f"Override entry must be an object: {schema_key}")
        overrides[schema_key] = {}
        for field_name, entry in fields.items():
            if not isinstance(entry, dict) or not isinstance(entry.get("description"), str):
                raise DescriptionResolutionError(
                    f"Override requires a description: {schema_key}/{field_name}"
                )
            if not isinstance(entry.get("source"), str) or not entry["source"].strip():
                raise DescriptionResolutionError(
                    f"Override requires source evidence: {schema_key}/{field_name}"
                )
            overrides[schema_key][field_name] = entry["description"]
    return overrides


def enrich_schema_file(
    schema_path: Path,
    docs_dir: Path,
    models: dict[str, JavaModel],
    overrides: dict[str, dict[str, str]],
) -> dict[str, Any]:
    """Resolve and apply comments to one NuDocument schema."""
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    keyspace, docset = _schema_key(schema)
    document = index_document_sources(docs_dir).get((keyspace, docset))
    if not document:
        raise DescriptionResolutionError(
            f"No raw LDM documentation maps {keyspace}/{docset}"
        )
    field_paths = [
        column["name"]
        for column in schema.get("Columns", [])
        if column.get("name") != "__KEY"
    ]
    source_key = f"{keyspace}/{docset}"
    descriptions = resolve_descriptions(
        document.source_class,
        field_paths,
        models,
        document.field_descriptions,
        overrides.get(source_key, {}),
    )
    return apply_descriptions(schema, descriptions)
