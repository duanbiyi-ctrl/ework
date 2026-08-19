import json
import tempfile
import unittest
from pathlib import Path

from scripts.raw_ldm_payloads import (
    MetadataResolutionError,
    build_payloads,
    check_artifacts,
    encode_avro_type,
    generate_artifacts,
)


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = REPOSITORY_ROOT / "data"
DOCS_DIR = REPOSITORY_ROOT / "docs" / "entities"


class RawLdmPayloadTests(unittest.TestCase):
    def test_encode_nudocument_types_as_avro_schemas(self):
        self.assertEqual(
            json.loads(encode_avro_type("string")),
            {
                "type": "string",
                "avro.java.string": "String",
                "default": None,
            },
        )
        self.assertEqual(
            json.loads(encode_avro_type("numberLong")),
            {"type": "long", "default": None},
        )
        self.assertEqual(
            json.loads(encode_avro_type("string[]")),
            {"type": "array", "items": "string", "default": None},
        )
        self.assertEqual(
            json.loads(encode_avro_type("date")),
            {"type": "int", "logicalType": "date", "default": None},
        )

    def test_rejects_unsupported_nudocument_type(self):
        with self.assertRaises(ValueError):
            encode_avro_type("object")

    def test_builds_all_repository_raw_payloads_after_reconciliation(self):
        artifacts = build_payloads(DATA_DIR, DOCS_DIR)

        self.assertEqual(len(artifacts), 22)
        self.assertTrue(
            all(
                field["description"].strip()
                for artifact in artifacts
                for field in artifact.payload["fields"]
            )
        )

    def test_writes_payload_beside_each_source_schema_and_checks_staleness(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            data_dir = root / "data" / "itemkeyspace"
            docs_dir = root / "docs" / "entities"
            data_dir.mkdir(parents=True)
            docs_dir.mkdir(parents=True)

            (data_dir / "ItemDescription_schema.json").write_text(
                json.dumps(
                    {
                        "DataStoreName": "ItemKeyspace",
                        "DataTableName": "__ROOT__.ItemDescription",
                        "Columns": [
                            {
                                "name": "ItemDescID",
                                "type": "string",
                                "comment": "Description identifier",
                                "nullable": False,
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )
            (docs_dir / "itemkeyspace-item-description.md").write_text(
                "\n".join(
                    [
                        "# ItemDescription LDM",
                        "",
                        "**LDM Name:** `ItemDescription LDM`",
                        "",
                        "**Description:** Item description payload.",
                        "",
                        "**NuDocument Docset:** `ItemDescription`",
                        "",
                        "**Keyspace:** `ItemKeyspace`",
                        "",
                        "**Primary Key:** `ItemDescID`",
                    ]
                ),
                encoding="utf-8",
            )

            generated = generate_artifacts(root / "data", docs_dir)
            request_path = data_dir / "ItemDescription_ldm_request.json"

            self.assertEqual(generated, [request_path])
            self.assertTrue(request_path.exists())
            self.assertEqual(check_artifacts(root / "data", docs_dir), [])

            request_path.write_text("{}\n", encoding="utf-8")
            self.assertEqual(check_artifacts(root / "data", docs_dir), [request_path])

    def test_rejects_schema_without_documented_raw_ldm(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            data_dir = Path(temporary_directory) / "data"
            docs_dir = Path(temporary_directory) / "docs"
            data_dir.mkdir()
            docs_dir.mkdir()
            (data_dir / "Unknown_schema.json").write_text(
                json.dumps(
                    {
                        "DataStoreName": "UnknownKeyspace",
                        "DataTableName": "__ROOT__.Unknown",
                        "Columns": [],
                    }
                ),
                encoding="utf-8",
            )

            with self.assertRaises(MetadataResolutionError):
                build_payloads(data_dir, docs_dir)

    def test_rejects_emitted_column_without_schema_description(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            data_dir = root / "data"
            docs_dir = root / "docs"
            data_dir.mkdir()
            docs_dir.mkdir()
            (data_dir / "ItemDescription_schema.json").write_text(
                json.dumps(
                    {
                        "DataStoreName": "ItemKeyspace",
                        "DataTableName": "__ROOT__.ItemDescription",
                        "Columns": [
                            {
                                "name": "desc",
                                "type": "string",
                                "comment": None,
                                "nullable": None,
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )
            (docs_dir / "item-description.md").write_text(
                "\n".join(
                    [
                        "# ItemDescription LDM",
                        "",
                        "**LDM Name:** `ItemDescription LDM`",
                        "",
                        "**Description:** Item description payload.",
                        "",
                        "**NuDocument Docset:** `ItemDescription`",
                        "",
                        "**Keyspace:** `ItemKeyspace`",
                    ]
                ),
                encoding="utf-8",
            )

            with self.assertRaisesRegex(MetadataResolutionError, "desc"):
                build_payloads(data_dir, docs_dir)


if __name__ == "__main__":
    unittest.main()
