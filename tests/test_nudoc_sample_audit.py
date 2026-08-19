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


if __name__ == "__main__":
    unittest.main()
