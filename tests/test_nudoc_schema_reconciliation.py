import unittest

from scripts.nudoc_schema_reconciliation import (
    DescriptionResolutionError,
    reconcile_schema,
)


class NuDocSchemaReconciliationTests(unittest.TestCase):
    def test_adds_sample_fields_corrects_types_and_backfills_descriptions(self):
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
                    "comment": None,
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
                    "comment": "Item detail values. Nested property: `count`.",
                    "nullable": None,
                },
                {
                    "name": "details.enabled",
                    "type": "boolean",
                    "comment": "Item detail values. Nested property: `enabled`.",
                    "nullable": None,
                },
            ],
        )
        self.assertIsNone(schema["Columns"][0]["comment"])

    def test_rejects_fields_without_documentation_evidence(self):
        with self.assertRaisesRegex(DescriptionResolutionError, "unknown"):
            reconcile_schema(
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


if __name__ == "__main__":
    unittest.main()
