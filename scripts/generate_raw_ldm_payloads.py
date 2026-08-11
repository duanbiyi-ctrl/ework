#!/usr/bin/env python3
"""Generate or verify MDM RAW LDM requests from NuDocument schemas."""

from __future__ import annotations

import argparse
from pathlib import Path

try:
    from scripts.raw_ldm_payloads import check_artifacts, generate_artifacts
except ModuleNotFoundError:
    from raw_ldm_payloads import check_artifacts, generate_artifacts


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, default=REPOSITORY_ROOT / "data")
    parser.add_argument(
        "--docs-dir",
        type=Path,
        default=REPOSITORY_ROOT / "docs" / "entities",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Fail if any generated request is missing or stale.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.check:
        stale_paths = check_artifacts(args.data_dir, args.docs_dir)
        if stale_paths:
            for path in stale_paths:
                print(f"Stale raw LDM request: {path}")
            return 1
        print("All raw LDM requests are current.")
        return 0

    output_paths = generate_artifacts(args.data_dir, args.docs_dir)
    for path in output_paths:
        print(f"Generated {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
