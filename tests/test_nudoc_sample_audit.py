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

    def test_item_root_markdown_revision_uses_the_sample_string_type(self):
        item_root = next(
            docset
            for docset in discover_docsets(DATA_DIR, SAMPLE_DIR, DOCS_DIR)
            if docset.keyspace == "ItemKeyspace" and docset.docset == "__ROOT__"
        )
        schema = json.loads(item_root.schema_path.read_text(encoding="utf-8"))
        field = next(
            column
            for column in schema["Columns"]
            if column["name"] == "PrmnlDtls.mrkdnItmPrcRvsn"
        )
        result = audit_docsets((item_root,))[0]

        self.assertEqual(field["type"], "string")
        self.assertNotIn("PrmnlDtls.mrkdnItmPrcRvsn", result.type_mismatches)

    def test_item_root_sample_keeps_the_canonical_primary_key_only(self):
        sample = json.loads(
            (
                SAMPLE_DIR
                / "ItemKeyspace"
                / "ItemKeyspace_ROOT_.json"
            ).read_text(encoding="utf-8")
        )
        records = sample if isinstance(sample, list) else [sample]

        self.assertTrue(
            all("PK" in record and "pk" not in record for record in records)
        )

    def test_item_qty_price_lifecycle_descriptions_are_source_backed(self):
        item_qty_price = next(
            docset
            for docset in discover_docsets(DATA_DIR, SAMPLE_DIR, DOCS_DIR)
            if docset.keyspace == "ItemKeyspace"
            and docset.docset == "ItemQtyPrice"
        )
        schema = json.loads(
            item_qty_price.schema_path.read_text(encoding="utf-8")
        )
        comments = {
            column["name"]: column["comment"] for column in schema["Columns"]
        }
        entity_page = item_qty_price.doc_path.read_text(encoding="utf-8")
        result = audit_docsets((item_qty_price,))[0]

        self.assertEqual(
            comments["crLstgDtVrs"], "Core listing data version."
        )
        self.assertEqual(comments["lifecycle.endDt"], "Listing end date.")
        self.assertEqual(
            comments["lifecycle.schdldEndDt"], "Scheduled listing end date."
        )
        self.assertIn(
            "| `crLstgDtVrs` | `String` | Core listing data version. |",
            entity_page,
        )
        self.assertIn(
            "| `lifecycle` | `Lifecycle` | "
            "Scheduled and end dates for the listing lifecycle. |",
            entity_page,
        )
        self.assertNotIn("`lifecycle.endDt`", entity_page)
        self.assertNotIn("`lifecycle.schdldEndDt`", entity_page)
        self.assertNotIn("crLstgDtVrs", result.undocumented_paths)
        self.assertNotIn("lifecycle", result.undocumented_paths)

    def test_listing_revision_root_expiration_is_documented(self):
        listing_revision_root = next(
            docset
            for docset in discover_docsets(DATA_DIR, SAMPLE_DIR, DOCS_DIR)
            if docset.keyspace == "ListingRevisionKeyspace"
            and docset.docset == "__ROOT__"
        )
        schema = json.loads(
            listing_revision_root.schema_path.read_text(encoding="utf-8")
        )
        expired_date = next(
            column
            for column in schema["Columns"]
            if column["name"] == "expiredDate"
        )
        entity_page = listing_revision_root.doc_path.read_text(encoding="utf-8")
        result = audit_docsets((listing_revision_root,))[0]

        self.assertEqual(
            expired_date["comment"],
            "Revision-history expiration date maintained by TTL maintenance.",
        )
        self.assertIn(
            "| `expiredDate` | `Date` | Revision-history expiration date "
            "maintained by TTL maintenance. |",
            entity_page,
        )
        self.assertNotIn("expiredDate", result.missing_descriptions)
        self.assertNotIn("expiredDate", result.undocumented_paths)

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
            self.assertEqual(result.undocumented_paths, ("details", "quantity"))
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
