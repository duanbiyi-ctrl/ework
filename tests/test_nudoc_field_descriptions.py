import json
import tempfile
import unittest
from pathlib import Path

from scripts.nudoc_field_descriptions import (
    DescriptionResolutionError,
    apply_descriptions,
    index_java_models,
    resolve_descriptions,
)


class NuDocFieldDescriptionTests(unittest.TestCase):
    def test_resolves_json_property_and_nested_field_annotations(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            source_root = Path(temporary_directory)
            package_dir = source_root / "com/example/entities"
            package_dir.mkdir(parents=True)
            (package_dir / "Item.java").write_text(
                """
                package com.example.entities;

                public class Item {
                    @ApiDescription("Seller-provided listing title.")
                    @JsonProperty("ttl")
                    private String title;

                    @ApiDescription("Fixed-price details for the listing.")
                    private Price fixedPrice;
                }
                """,
                encoding="utf-8",
            )
            (package_dir / "Price.java").write_text(
                """
                package com.example.entities;

                public class Price {
                    @ApiDescription(value = "Currency code for the price.")
                    private String currency;
                }
                """,
                encoding="utf-8",
            )

            models = index_java_models(source_root)
            descriptions = resolve_descriptions(
                "com.example.entities.Item",
                ["ttl", "fixedPrice.currency"],
                models,
                {},
                {},
            )

            self.assertEqual(
                descriptions["ttl"],
                "Seller-provided listing title.",
            )
            self.assertEqual(
                descriptions["fixedPrice.currency"],
                "Currency code for the price.",
            )

    def test_uses_curated_override_only_when_source_and_docs_have_no_description(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            source_root = Path(temporary_directory)
            package_dir = source_root / "com/example/entities"
            package_dir.mkdir(parents=True)
            (package_dir / "Item.java").write_text(
                """
                package com.example.entities;

                public class Item {
                    @JsonProperty("fl")
                    private Integer flag;
                }
                """,
                encoding="utf-8",
            )

            descriptions = resolve_descriptions(
                "com.example.entities.Item",
                ["fl"],
                index_java_models(source_root),
                {},
                {"fl": "Source-defined listing flag."},
            )

            self.assertEqual(descriptions, {"fl": "Source-defined listing flag."})

    def test_rejects_unresolved_field_descriptions(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            source_root = Path(temporary_directory)
            package_dir = source_root / "com/example/entities"
            package_dir.mkdir(parents=True)
            (package_dir / "Item.java").write_text(
                """
                package com.example.entities;

                public class Item {
                    @JsonProperty("fl")
                    private Integer flag;
                }
                """,
                encoding="utf-8",
            )

            with self.assertRaisesRegex(DescriptionResolutionError, "fl"):
                resolve_descriptions(
                    "com.example.entities.Item",
                    ["fl"],
                    index_java_models(source_root),
                    {},
                    {},
                )

    def test_applies_descriptions_without_changing_other_schema_values(self):
        schema = {
            "DataStoreName": "ItemKeyspace",
            "Columns": [
                {
                    "name": "ttl",
                    "type": "string",
                    "comment": None,
                    "nullable": None,
                }
            ],
        }

        enriched = apply_descriptions(
            schema,
            {"ttl": "Seller-provided listing title."},
        )

        self.assertEqual(
            enriched["Columns"][0],
            {
                "name": "ttl",
                "type": "string",
                "comment": "Seller-provided listing title.",
                "nullable": None,
            },
        )
        self.assertEqual(schema["Columns"][0]["comment"], None)


if __name__ == "__main__":
    unittest.main()
