import json
import tempfile
import unittest
from pathlib import Path

from scripts.nudoc_sample_audit import audit_docsets, discover_docsets, render_markdown


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = REPOSITORY_ROOT / "data"
SAMPLE_DIR = DATA_DIR / "sample-data" / "item-raw-ldm-samples"
DOCS_DIR = REPOSITORY_ROOT / "docs" / "entities"


class NuDocSampleAuditTests(unittest.TestCase):
    def test_discovers_all_schema_sample_and_documentation_pairs(self):
        docsets = discover_docsets(DATA_DIR, SAMPLE_DIR, DOCS_DIR)

        self.assertEqual(len(docsets), 22)
        by_docset = {
            (docset.keyspace, docset.docset): docset
            for docset in docsets
        }
        self.assertEqual(
            by_docset[("ItemKeyspace", "__ROOT__")].sample_path.name,
            "ItemKeyspace_ROOT_.json",
        )
        self.assertEqual(
            by_docset[("UserListingDraft", "UserListingDraftMap")].doc_path.name,
            "userlistingdraft-user-item-draft-map.md",
        )

    def test_reports_schema_sample_and_documentation_contract_gaps(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            data_dir = root / "data" / "itemkeyspace"
            sample_dir = root / "samples" / "ItemKeyspace"
            docs_dir = root / "docs"
            data_dir.mkdir(parents=True)
            sample_dir.mkdir(parents=True)
            docs_dir.mkdir()

            (data_dir / "Item_schema.json").write_text(
                json.dumps(
                    {
                        "DataStoreName": "ItemKeyspace",
                        "DataTableName": "__ROOT__.Item",
                        "Columns": [
                            {
                                "name": "title",
                                "type": "string",
                                "comment": "Listing title.",
                            },
                            {
                                "name": "quantity",
                                "type": "numberInt",
                                "comment": None,
                            },
                        ],
                    }
                ),
                encoding="utf-8",
            )
            (sample_dir / "Item.json").write_text(
                json.dumps(
                    {
                        "title": "Sample title",
                        "quantity": "1",
                        "details": {"brand": "Acme"},
                        "optional": None,
                        "tags": [],
                    }
                ),
                encoding="utf-8",
            )
            (docs_dir / "item.md").write_text(
                "\n".join(
                    [
                        "# Item LDM",
                        "",
                        "**NuDocument Docset:** `Item`",
                        "",
                        "**Keyspace:** `ItemKeyspace`",
                        "",
                        "| Field | Type | Description |",
                        "| --- | --- | --- |",
                        "| `title` | `String` | Listing title. |",
                        "| `details` | `Details` | Item details. |",
                    ]
                ),
                encoding="utf-8",
            )

            result = audit_docsets(
                discover_docsets(root / "data", root / "samples", docs_dir)
            )[0]

            self.assertEqual(result.sample_only_paths, ("details.brand",))
            self.assertEqual(result.type_mismatches, ("quantity",))
            self.assertEqual(result.missing_descriptions, ("quantity",))
            self.assertEqual(result.undocumented_paths, ("details.brand", "quantity"))
            self.assertEqual(result.unobservable_paths, ("optional", "tags"))

    def test_renders_one_markdown_section_per_docset_with_findings(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            data_dir = root / "data" / "itemkeyspace"
            sample_dir = root / "samples" / "ItemKeyspace"
            docs_dir = root / "docs"
            data_dir.mkdir(parents=True)
            sample_dir.mkdir(parents=True)
            docs_dir.mkdir()

            (data_dir / "Item_schema.json").write_text(
                json.dumps(
                    {
                        "DataStoreName": "ItemKeyspace",
                        "DataTableName": "__ROOT__.Item",
                        "Columns": [],
                    }
                ),
                encoding="utf-8",
            )
            (sample_dir / "Item.json").write_text(
                json.dumps({"title": "Sample title"}),
                encoding="utf-8",
            )
            (docs_dir / "item.md").write_text(
                "\n".join(
                    [
                        "# Item LDM",
                        "",
                        "**NuDocument Docset:** `Item`",
                        "",
                        "**Keyspace:** `ItemKeyspace`",
                    ]
                ),
                encoding="utf-8",
            )

            markdown = render_markdown(
                audit_docsets(
                    discover_docsets(root / "data", root / "samples", docs_dir)
                )
            )

            self.assertIn("# NuDocument schema/sample audit", markdown)
            self.assertIn("## ItemKeyspace / Item", markdown)
            self.assertIn("`title`", markdown)

    def test_merges_observed_paths_from_a_top_level_sample_array(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            data_dir = root / "data" / "itemkeyspace"
            sample_dir = root / "samples" / "ItemKeyspace"
            docs_dir = root / "docs"
            data_dir.mkdir(parents=True)
            sample_dir.mkdir(parents=True)
            docs_dir.mkdir()

            (data_dir / "Item_schema.json").write_text(
                json.dumps(
                    {
                        "DataStoreName": "ItemKeyspace",
                        "DataTableName": "__ROOT__.Item",
                        "Columns": [
                            {
                                "name": "title",
                                "type": "string",
                                "comment": "Listing title.",
                            },
                            {
                                "name": "quantity",
                                "type": "numberInt",
                                "comment": "Available quantity.",
                            },
                        ],
                    }
                ),
                encoding="utf-8",
            )
            (sample_dir / "Item.json").write_text(
                json.dumps(
                    [
                        {"title": "First sample"},
                        {"title": "Second sample", "quantity": 2},
                    ]
                ),
                encoding="utf-8",
            )
            (docs_dir / "item.md").write_text(
                "\n".join(
                    [
                        "# Item LDM",
                        "",
                        "**NuDocument Docset:** `Item`",
                        "",
                        "**Keyspace:** `ItemKeyspace`",
                        "",
                        "| Field | Type | Description |",
                        "| --- | --- | --- |",
                        "| `title` | `String` | Listing title. |",
                        "| `quantity` | `Integer` | Available quantity. |",
                    ]
                ),
                encoding="utf-8",
            )

            result = audit_docsets(
                discover_docsets(root / "data", root / "samples", docs_dir)
            )[0]

            self.assertEqual(result.observed_paths, ("quantity", "title"))
            self.assertEqual(result.sample_only_paths, ())
            self.assertEqual(result.type_mismatches, ())

    def test_ignores_nudocument_envelope_and_normalizes_extended_json_types(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            data_dir = root / "data" / "itemkeyspace"
            sample_dir = root / "samples" / "ItemKeyspace"
            docs_dir = root / "docs"
            data_dir.mkdir(parents=True)
            sample_dir.mkdir(parents=True)
            docs_dir.mkdir()

            (data_dir / "Item_schema.json").write_text(
                json.dumps(
                    {
                        "DataStoreName": "ItemKeyspace",
                        "DataTableName": "__ROOT__.Item",
                        "Columns": [
                            {
                                "name": "quantity",
                                "type": "numberInt",
                                "comment": "Available quantity.",
                            },
                            {
                                "name": "payload",
                                "type": "binary",
                                "comment": "Serialized payload.",
                            },
                        ],
                    }
                ),
                encoding="utf-8",
            )
            (sample_dir / "Item.json").write_text(
                json.dumps(
                    {
                        "__key": {"collection": "Item", "string": "item-1"},
                        "__meta": {
                            "creation_date": 1,
                            "modification_date": 2,
                            "revision": 3,
                        },
                        "quantity": {"$numberLong": "2"},
                        "payload": {"$binary": "Ynl0ZXM=", "$type": "00"},
                    }
                ),
                encoding="utf-8",
            )
            (docs_dir / "item.md").write_text(
                "\n".join(
                    [
                        "# Item LDM",
                        "",
                        "**NuDocument Docset:** `Item`",
                        "",
                        "**Keyspace:** `ItemKeyspace`",
                        "",
                        "| Field | Type | Description |",
                        "| --- | --- | --- |",
                        "| `quantity` | `Integer` | Available quantity. |",
                        "| `payload` | `Binary` | Serialized payload. |",
                    ]
                ),
                encoding="utf-8",
            )

            result = audit_docsets(
                discover_docsets(root / "data", root / "samples", docs_dir)
            )[0]

            self.assertEqual(result.observed_paths, ("payload", "quantity"))
            self.assertEqual(result.sample_only_paths, ())
            self.assertEqual(result.type_mismatches, ())


if __name__ == "__main__":
    unittest.main()
