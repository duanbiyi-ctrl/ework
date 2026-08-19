import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from scripts.nudoc_schema_reconciliation import (
    main,
    reconcile_schema,
)


class NuDocSchemaReconciliationTests(unittest.TestCase):
    def test_prefers_exact_descriptions_and_derives_documented_children(self):
        schema = {
            "Columns": [
                {
                    "name": "title",
                    "type": "string",
                    "comment": None,
                    "nullable": None,
                },
                {
                    "name": "details.count",
                    "type": "string",
                    "comment": "Item detail values. Nested property: `count`.",
                    "nullable": None,
                },
            ]
        }

        reconciled = reconcile_schema(
            schema,
            {
                "title": {"string"},
                "details.count": {"integer"},
                "details.enabled": {"boolean"},
            },
            {
                "title": "Listing title.",
                "details": "Item detail values.",
                "details.count": "Exact count description.",
            },
        )

        self.assertEqual(
            reconciled["Columns"],
            [
                {
                    "name": "title",
                    "type": "string",
                    "comment": "Listing title.",
                    "nullable": None,
                },
                {
                    "name": "details.count",
                    "type": "numberLong",
                    "comment": "Exact count description.",
                    "nullable": None,
                },
                {
                    "name": "details.enabled",
                    "type": "boolean",
                    "comment": (
                        "Item detail values. "
                        "Inferred nested field: enabled."
                    ),
                    "nullable": None,
                },
            ],
        )
        self.assertIsNone(schema["Columns"][0]["comment"])

    def test_derives_parentless_field_descriptions_from_docset_metadata(self):
        reconciled = reconcile_schema(
            {
                "Columns": [
                    {
                        "name": "unreferencedValue",
                        "type": "string",
                        "comment": None,
                    }
                ]
            },
            {"unreferencedValue": {"string"}},
            {},
            "Item detail document.",
        )

        self.assertEqual(
            reconciled["Columns"][0]["comment"],
            "Item detail document. Inferred field: unreferenced value.",
        )

    def test_leaves_fields_without_documentation_evidence_empty(self):
        reconciled = reconcile_schema(
            {
                "Columns": [
                    {
                        "name": "unknown",
                        "type": "string",
                        "comment": None,
                    }
                ]
            },
            {"unknown": {"string"}},
            {},
        )

        self.assertIsNone(reconciled["Columns"][0]["comment"])

    def test_uses_double_for_mixed_integer_and_decimal_observations(self):
        reconciled = reconcile_schema(
            {"Columns": []},
            {"score": {"integer", "number"}},
            {"score": "Listing score."},
        )

        self.assertEqual(
            reconciled["Columns"],
            [
                {
                    "name": "score",
                    "type": "numberDouble",
                    "comment": "Listing score.",
                    "nullable": None,
                }
            ],
        )

    def test_preserves_existing_type_for_incompatible_sample_observations(self):
        reconciled = reconcile_schema(
            {
                "Columns": [
                    {
                        "name": "revision",
                        "type": "numberInt",
                        "comment": "Revision number.",
                    }
                ]
            },
            {"revision": {"integer", "string"}},
            {"revision": "Revision number."},
        )

        self.assertEqual(reconciled["Columns"][0]["type"], "numberInt")

    def test_rejects_unsupported_observed_type(self):
        with self.assertRaisesRegex(ValueError, "Unsupported observed sample type"):
            reconcile_schema(
                {"Columns": []},
                {"values": {"array"}},
                {"values": "Values."},
            )

    def test_check_and_apply_reconciliation_commands(self):
        with TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            data_dir = root / "data" / "itemkeyspace"
            samples_dir = root / "samples" / "ItemKeyspace"
            docs_dir = root / "docs"
            data_dir.mkdir(parents=True)
            samples_dir.mkdir(parents=True)
            docs_dir.mkdir()

            schema_path = data_dir / "Item_schema.json"
            schema_path.write_text(
                """{
    "DataStoreName": "ItemKeyspace",
    "DataTableName": "__ROOT__.Item",
    "Columns": [
        {
            "name": "title",
            "type": "string",
            "comment": null,
            "nullable": null
        }
    ]
}
""",
                encoding="utf-8",
            )
            (samples_dir / "Item.json").write_text(
                '{"title": "Sample title"}\n',
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
            base_arguments = [
                "nudoc_schema_reconciliation.py",
                "--data-dir",
                str(root / "data"),
                "--samples-dir",
                str(root / "samples"),
                "--docs-dir",
                str(docs_dir),
            ]

            with patch("sys.argv", [*base_arguments, "--check"]):
                self.assertEqual(main(), 1)
            with patch("sys.argv", [*base_arguments, "--apply"]):
                self.assertEqual(main(), 0)
            with patch("sys.argv", [*base_arguments, "--check"]):
                self.assertEqual(main(), 0)

            self.assertIn('"comment": "Listing title."', schema_path.read_text())


if __name__ == "__main__":
    unittest.main()
