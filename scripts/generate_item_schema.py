#!/usr/bin/env python3
"""Generate the Item LDM schema section from a TSV source file.

The TSV is expected to include these columns:
- Entity Field
- Field Type
- Enhanced Entity Field description

If a `Category` column is present, it is used as the source of truth for
grouping. Otherwise, the script falls back to deterministic field rules.
"""

from __future__ import annotations

import argparse
import csv
import html
import re
from pathlib import Path


BEGIN_MARKER = "<!-- BEGIN GENERATED ITEM FIELDS -->"
END_MARKER = "<!-- END GENERATED ITEM FIELDS -->"

CATEGORY_ORDER = [
    "Item Basics",
    "Item Aspects",
    "Listing Basics",
    "Payment & Shipping",
]

CATEGORY_DESCRIPTIONS = {
    "Item Basics": (
        "Core attributes that describe what the listed item is, including its "
        "identity, title, category, condition, price, quantity, location, and "
        "other buyer-facing item facts."
    ),
    "Item Aspects": (
        "Structured product attributes and eBay-derived catalog/classifier "
        "signals, such as brand, MPN, GTIN, aspect values, ePID adoption, "
        "and product coverage."
    ),
    "Listing Basics": (
        "Attributes that describe how the listing was created, presented, "
        "and managed, including listing status, format, lifecycle dates, "
        "seller context, listing tool/channel, media, and operational flags."
    ),
    "Payment & Shipping": (
        "Attributes that describe how buyers can pay for and receive the item, "
        "including payment methods, shipping costs, package details, tax, "
        "shipping programs, and related policies."
    ),
}

PAYMENT_SHIPPING_DW_FIELDS = {
    "package_size",
    "payment_cash",
    "payment_cc",
    "payment_moneyxfer",
    "return_policy_yn",
    "shipping_fee",
    "shipping_type",
    "shipping_xfee",
    "tax_new",
    "tax_new_state",
    "weight",
    "weight_unit_type",
    "amex",
    "aplcbltoshp",
    "cashinperson",
    "cod",
    "codprepaydelivery",
    "dgtdlvlgsplsprt",
    "discover",
    "domestic_international",
    "ebaymgdshpng",
    "gsplgstcplnsprtd",
    "immpay",
    "irregularpackage",
    "isbuyerresponsibleforshipping",
    "loancheck",
    "mfulfillmentsprt",
    "mgdshpngoptin",
    "mocc",
    "onfreeshipprtopromo",
    "onfreeshipsale",
    "other",
    "otheronlinepayments",
    "paisapayaccepted",
    "paisapayescrow",
    "paisapayescrowemi",
    "paymentseedescription",
    "paypal",
    "personalcheck",
    "postaltransfer",
    "prepaydelivery",
    "prgspprtd_ebayplus",
    "promoshp_domestic",
    "visamc",
}

ITEM_DW_FIELDS = {
    "item_id",
    "bin_price_lstg_curncy",
    "leaf_categ_id",
    "leaf_categ_id2",
    "item_cntry_id",
    "lstg_curncy_id",
    "auct_titl",
    "item_loc",
    "lot_size",
    "orgnl_price_amt",
    "qty_avail",
    "qty_sold",
    "rsrv_price_list_crncy",
    "slr_prdct_id_txt",
    "item_site_id",
    "sku_num",
    "start_price_lstg_curncy",
    "subtitle",
    "item_zip",
    "categ_key",
    "categ_key2",
}

ITEM_DIM_FIELDS = {
    "item_id",
    "bsns_vrtcl_name",
    "leaf_categ_name",
    "meta_categ_name",
    "categ_lvl4_id",
    "categ_lvl5_id",
    "meta_categ_id",
    "categ_lvl2_id",
    "categ_lvl2_name",
    "categ_lvl3_id",
    "categ_lvl3_name",
    "categ_lvl4_name",
    "categ_lvl5_name",
    "categ_lvl6_id",
    "categ_lvl6_name",
    "categ_move_to_id",
    "lcl_sap_categ_name",
    "glb_sap_categ_name",
}


def normalize_header(row: dict[str, str]) -> dict[str, str]:
    return {key.strip(): value.strip() for key, value in row.items() if key is not None}


def normalize_description(value: str) -> str:
    return re.sub(r"\s+", " ", value.replace("\u00a0", " ")).strip()


def classify(row: dict[str, str]) -> str:
    explicit_category = row.get("Category", "").strip()
    if explicit_category:
        return explicit_category

    table_name = row.get("Table_names", "")
    table_field = row.get("Table Field", "").lower()

    if table_name == "dw_lstg_item_gds":
        if table_field in PAYMENT_SHIPPING_DW_FIELDS:
            return "Payment & Shipping"
        if table_field in ITEM_DW_FIELDS:
            return "Item Basics"
        return "Listing Basics"

    if table_name == "LSTG_ITEM_CNDTN":
        return "Item Basics"

    if table_name == "SLNG_LSTG_SUPER_FACT":
        if table_field in {"item_id", "sap_category_id"}:
            return "Item Basics"
        if table_field == "attr_brand_txt":
            return "Item Aspects"
        return "Listing Basics"

    if table_name == "dim_item":
        if table_field == "eplus_elgbl_ind":
            return "Payment & Shipping"
        if table_field in ITEM_DIM_FIELDS:
            return "Item Basics"
        return "Listing Basics"

    if table_name == "CTLG_ITEM_FACT":
        if table_field == "item_id":
            return "Item Basics"
        return "Item Aspects"

    if table_name == "lstg_item_desc_dim":
        return "Item Basics"

    return "Listing Basics"


def read_fields(input_path: Path) -> list[dict[str, str]]:
    with input_path.open(newline="", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file, delimiter="\t")
        rows = []
        has_item_id = False
        for raw_row in reader:
            row = normalize_header(raw_row)
            if row.get("Entity") != "item" or not row.get("Entity Field"):
                continue

            if row["Entity Field"] == "item_id":
                if has_item_id:
                    continue
                has_item_id = True

            description = row.get("Enhanced Entity Field description", "")
            if not description:
                description = row.get("Entity Field description", "")

            rows.append(
                {
                    "category": classify(row),
                    "field": row["Entity Field"],
                    "type": row.get("Field Type", ""),
                    "description": normalize_description(description),
                }
            )
        return rows


def render_field_list(rows: list[dict[str, str]]) -> str:
    grouped = {category: [] for category in CATEGORY_ORDER}
    for row in rows:
        grouped.setdefault(row["category"], []).append(row)

    def append_field(lines: list[str], field: dict[str, str]) -> None:
        field_name = html.escape(field["field"])
        field_type = html.escape(field["type"])
        description = html.escape(field["description"])
        lines.append(f"- **`{field_name}`** <span class=\"field-type\">{field_type}</span>  ")
        lines.append(f"  {description}")

    lines = [
        "## Fields",
        "",
        BEGIN_MARKER,
        "",
    ]

    for category in CATEGORY_ORDER:
        fields = grouped.get(category, [])
        lines.append(f"### {category} ({len(fields)})")
        lines.append("")
        lines.append(CATEGORY_DESCRIPTIONS[category])
        lines.append("")

        for field in fields:
            append_field(lines, field)

        lines.append("")

    extra_categories = [
        category for category in grouped if category not in CATEGORY_ORDER and grouped[category]
    ]
    for category in extra_categories:
        fields = grouped[category]
        lines.append(f"### {category} ({len(fields)})")
        lines.append("")
        for field in fields:
            append_field(lines, field)
        lines.append("")

    lines.extend([END_MARKER, ""])
    return "\n".join(lines)


def replace_fields_section(markdown: str, generated_section: str) -> str:
    if BEGIN_MARKER in markdown and END_MARKER in markdown:
        pattern = re.compile(
            rf"## Fields\n\n{re.escape(BEGIN_MARKER)}.*?{re.escape(END_MARKER)}\n?",
            flags=re.DOTALL,
        )
        return pattern.sub(generated_section, markdown)

    pattern = re.compile(r"## Fields\n.*?\n---\n\n## Sample Queries", flags=re.DOTALL)
    replacement = generated_section + "\n---\n\n## Sample Queries"
    if not pattern.search(markdown):
        raise ValueError("Could not find the Fields section to replace.")

    return pattern.sub(replacement, markdown)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input",
        required=True,
        type=Path,
        help="Path to the Item LDM schema TSV.",
    )
    parser.add_argument(
        "--output",
        default=Path("docs/entities/item.md"),
        type=Path,
        help="Path to the item.md file to update.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    fields = read_fields(args.input)
    generated_section = render_field_list(fields)
    markdown = args.output.read_text(encoding="utf-8")
    args.output.write_text(replace_fields_section(markdown, generated_section), encoding="utf-8")
    print(f"Updated {args.output} with {len(fields)} item fields.")


if __name__ == "__main__":
    main()
