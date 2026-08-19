#!/usr/bin/env python3
"""Create generated RAW LDM requests in MDM only when --apply is specified."""

from __future__ import annotations

import argparse
import json
import os
from collections.abc import Callable
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

try:
    from scripts.raw_ldm_payloads import (
        PayloadArtifact,
        check_artifacts,
    )
except ModuleNotFoundError:
    from raw_ldm_payloads import PayloadArtifact, check_artifacts


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
RequestFunction = Callable[[str, str, dict[str, str], bytes | None], tuple[int, Any]]


class MdmRequestError(RuntimeError):
    """Raised when MDM rejects a preflight or creation request."""


def _decode_response(payload: bytes) -> Any:
    text = payload.decode("utf-8")
    if not text:
        return None
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return text


def request_json(
    method: str,
    url: str,
    headers: dict[str, str],
    body: bytes | None = None,
) -> tuple[int, Any]:
    request = Request(url, data=body, headers=headers, method=method)
    try:
        with urlopen(request) as response:
            return response.status, _decode_response(response.read())
    except HTTPError as error:
        return error.code, _decode_response(error.read())
    except URLError as error:
        raise MdmRequestError(f"Unable to contact MDM at {url}: {error.reason}") from error


def _mdm_headers(token: str, token_provider: str) -> dict[str, str]:
    return {
        "Accept": "application/json",
        "Authorization": token,
        "Content-Type": "application/json",
        "GDS-TOKEN-PROVIDER": token_provider,
    }


def _entities_from_response(response: Any) -> list[dict[str, Any]]:
    if isinstance(response, list):
        return [entity for entity in response if isinstance(entity, dict)]
    if isinstance(response, dict):
        content = response.get("content")
        if isinstance(content, list):
            return [entity for entity in content if isinstance(entity, dict)]
        if "name" in response:
            return [response]
    return []


def _response_detail(response: Any) -> str:
    if isinstance(response, str):
        return response
    return json.dumps(response, sort_keys=True)


def _find_existing_entity(
    base_url: str,
    payload: dict[str, Any],
    headers: dict[str, str],
    request: RequestFunction,
) -> dict[str, Any] | None:
    query = urlencode({"name": payload["name"], "pageSize": 10000})
    status, response = request("GET", f"{base_url}/ldms?{query}", headers)
    if not 200 <= status < 300:
        raise MdmRequestError(
            f"MDM preflight for {payload['name']} failed with {status}: "
            f"{_response_detail(response)}"
        )

    for entity in _entities_from_response(response):
        if (
            entity.get("name") == payload["name"]
            and entity.get("namespaceId") == payload["namespaceId"]
        ):
            return entity
    return None


def create_entities(
    artifacts: list[PayloadArtifact],
    base_url: str,
    token: str,
    token_provider: str,
    *,
    apply: bool,
    request: RequestFunction = request_json,
) -> list[dict[str, Any]]:
    """Dry-run or create generated LDM entities in stable artifact order."""
    ordered_artifacts = sorted(artifacts, key=lambda artifact: artifact.payload["name"])
    if not apply:
        return [
            {"name": artifact.payload["name"], "status": "dry-run"}
            for artifact in ordered_artifacts
        ]

    normalized_base_url = base_url.rstrip("/")
    headers = _mdm_headers(token, token_provider)
    results: list[dict[str, Any]] = []
    for artifact in ordered_artifacts:
        payload = artifact.payload
        existing = _find_existing_entity(
            normalized_base_url,
            payload,
            headers,
            request,
        )
        if existing:
            results.append(
                {
                    "name": payload["name"],
                    "status": "skipped",
                    "id": existing.get("id"),
                }
            )
            continue

        body = json.dumps(payload, separators=(",", ":")).encode("utf-8")
        status, response = request(
            "POST",
            f"{normalized_base_url}/ldms",
            headers,
            body,
        )
        if not 200 <= status < 300:
            raise MdmRequestError(
                f"MDM creation for {payload['name']} failed with {status}: "
                f"{_response_detail(response)}"
            )

        result = {"name": payload["name"], "status": "created"}
        if isinstance(response, dict) and response.get("id") is not None:
            result["id"] = response["id"]
        results.append(result)

    return results


def read_artifacts(data_dir: Path) -> list[PayloadArtifact]:
    artifacts: list[PayloadArtifact] = []
    names: set[str] = set()
    for path in sorted(data_dir.rglob("*_ldm_request.json")):
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as error:
            raise MdmRequestError(f"Invalid generated request: {path}") from error
        if not isinstance(payload, dict):
            raise MdmRequestError(f"Generated request must be a JSON object: {path}")
        name = payload.get("name")
        namespace_id = payload.get("namespaceId")
        if not isinstance(name, str) or not name or not isinstance(namespace_id, int):
            raise MdmRequestError(
                f"Generated request is missing name or namespaceId: {path}"
            )
        if name in names:
            raise MdmRequestError(f"Multiple generated requests have name {name}")
        names.add(name)
        artifacts.append(PayloadArtifact(None, path, payload))
    if not artifacts:
        raise MdmRequestError(f"No generated requests found in {data_dir}")
    return artifacts


def validate_artifacts(data_dir: Path, docs_dir: Path) -> None:
    """Reject stale artifacts and unresolved source-schema metadata."""
    try:
        stale_paths = check_artifacts(data_dir, docs_dir)
    except ValueError as error:
        raise MdmRequestError(
            f"Cannot use generated requests until source schemas are resolved: {error}"
        ) from error
    if stale_paths:
        stale = ", ".join(str(path) for path in stale_paths)
        raise MdmRequestError(
            f"Generated requests are stale; regenerate them before use: {stale}"
        )


def select_artifacts(
    artifacts: list[PayloadArtifact],
    requested_names: list[str] | None,
) -> list[PayloadArtifact]:
    """Return only explicitly requested LDMs, rejecting unknown names."""
    if not requested_names:
        return artifacts

    available_names = {artifact.payload["name"] for artifact in artifacts}
    unknown_names = sorted(set(requested_names) - available_names)
    if unknown_names:
        raise MdmRequestError(
            f"Unknown generated LDM: {', '.join(unknown_names)}"
        )
    requested_name_set = set(requested_names)
    return [
        artifact
        for artifact in artifacts
        if artifact.payload["name"] in requested_name_set
    ]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, default=REPOSITORY_ROOT / "data")
    parser.add_argument(
        "--docs-dir",
        type=Path,
        default=REPOSITORY_ROOT / "docs" / "entities",
    )
    parser.add_argument(
        "--ldm",
        action="append",
        metavar="NAME",
        help="Create or preview only this LDM. Repeat to select multiple LDMs.",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Create missing LDMs in MDM. Without this flag, only print the plan.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    validate_artifacts(args.data_dir, args.docs_dir)
    artifacts = select_artifacts(read_artifacts(args.data_dir), args.ldm)
    if not args.apply:
        for result in create_entities(artifacts, "", "", "", apply=False):
            print(f"{result['status']}: {result['name']}")
        return 0

    base_url = os.environ.get("MDM_BASE_URL")
    token = os.environ.get("MDM_TOKEN")
    token_provider = os.environ.get("MDM_TOKEN_PROVIDER", "KEYSTONE")
    if not base_url or not token:
        raise MdmRequestError(
            "MDM_BASE_URL and MDM_TOKEN must be set when using --apply"
        )

    for result in create_entities(
        artifacts,
        base_url,
        token,
        token_provider,
        apply=True,
    ):
        print(f"{result['status']}: {result['name']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
