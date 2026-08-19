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


if __name__ == "__main__":
    unittest.main()
