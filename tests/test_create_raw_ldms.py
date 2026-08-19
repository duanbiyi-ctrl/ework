import json
import tempfile
import unittest
from pathlib import Path

from scripts.create_raw_ldms import (
    MdmRequestError,
    create_entities,
    select_artifacts,
    validate_artifacts,
)
from scripts.raw_ldm_payloads import PayloadArtifact


def payload_artifact(name: str) -> PayloadArtifact:
    return PayloadArtifact(
        schema_path=None,
        output_path=None,
        payload={
            "name": name,
            "namespaceId": 114,
            "viewType": "RAW",
            "fields": [],
        },
    )


class CreateRawLdmsTests(unittest.TestCase):
    def test_selects_only_requested_ldms(self):
        selected = select_artifacts(
            [
                payload_artifact("item_root"),
                payload_artifact("item_details"),
                payload_artifact("listing_draft_root"),
            ],
            ["listing_draft_root", "item_root"],
        )

        self.assertEqual(
            [artifact.payload["name"] for artifact in selected],
            ["item_root", "listing_draft_root"],
        )

    def test_rejects_unknown_ldm_before_requesting_mdm(self):
        with self.assertRaisesRegex(MdmRequestError, "Unknown generated LDM: missing_ldm"):
            select_artifacts([payload_artifact("item_root")], ["missing_ldm"])

    def test_dry_run_does_not_make_network_requests(self):
        def unexpected_request(*_args):
            raise AssertionError("dry-run must not call MDM")

        result = create_entities(
            [payload_artifact("item_root")],
            "https://mdm.example/v1",
            "token",
            "KEYSTONE",
            apply=False,
            request=unexpected_request,
        )

        self.assertEqual(result, [{"name": "item_root", "status": "dry-run"}])

    def test_apply_creates_missing_ldm_with_required_headers(self):
        calls = []

        def request(method, url, headers, body=None):
            calls.append((method, url, headers, body))
            if method == "GET":
                return 200, []
            return 201, {"id": 100}

        result = create_entities(
            [payload_artifact("item_root")],
            "https://mdm.example/v1/",
            "token",
            "KEYSTONE",
            apply=True,
            request=request,
        )

        self.assertEqual(
            [call[0] for call in calls],
            ["GET", "POST"],
        )
        self.assertEqual(calls[1][2]["Authorization"], "token")
        self.assertEqual(calls[1][2]["GDS-TOKEN-PROVIDER"], "KEYSTONE")
        self.assertEqual(
            json.loads(calls[1][3].decode("utf-8"))["name"],
            "item_root",
        )
        self.assertEqual(result, [{"name": "item_root", "status": "created", "id": 100}])

    def test_apply_skips_ldm_already_in_the_target_namespace(self):
        calls = []

        def request(method, url, headers, body=None):
            calls.append(method)
            return 200, [{"name": "item_root", "namespaceId": 114, "id": 77}]

        result = create_entities(
            [payload_artifact("item_root")],
            "https://mdm.example/v1",
            "token",
            "KEYSTONE",
            apply=True,
            request=request,
        )

        self.assertEqual(calls, ["GET"])
        self.assertEqual(result, [{"name": "item_root", "status": "skipped", "id": 77}])

    def test_apply_fails_fast_when_mdm_rejects_a_create_request(self):
        def request(method, url, headers, body=None):
            if method == "GET":
                return 200, {"content": []}
            return 400, {"message": "invalid payload"}

        with self.assertRaisesRegex(MdmRequestError, "item_root.*400.*invalid payload"):
            create_entities(
                [payload_artifact("item_root")],
                "https://mdm.example/v1",
                "token",
                "KEYSTONE",
                apply=True,
                request=request,
            )

    def test_rejects_generated_requests_without_direct_description_evidence(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            data_dir = root / "data" / "itemkeyspace"
            docs_dir = root / "docs" / "entities"
            data_dir.mkdir(parents=True)
            docs_dir.mkdir(parents=True)
            (data_dir / "Item_schema.json").write_text(
                json.dumps(
                    {
                        "DataStoreName": "ItemKeyspace",
                        "DataTableName": "__ROOT__.Item",
                        "Columns": [
                            {
                                "name": "title",
                                "type": "string",
                                "comment": None,
                                "nullable": None,
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )
            (docs_dir / "item.md").write_text(
                "\n".join(
                    [
                        "# Item LDM",
                        "",
                        "**LDM Name:** `Item LDM`",
                        "",
                        "**Description:** Item data.",
                        "",
                        "**NuDocument Docset:** `Item`",
                        "",
                        "**Keyspace:** `ItemKeyspace`",
                    ]
                ),
                encoding="utf-8",
            )

            with self.assertRaisesRegex(MdmRequestError, "title.*description"):
                validate_artifacts(root / "data", docs_dir)


if __name__ == "__main__":
    unittest.main()
