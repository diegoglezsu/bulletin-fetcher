"""Small script to query DOUE acts using bulletin-fetcher."""

import argparse
import sys

from bulletin.doue.api.client import DoueBulletinClient


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Fetch Official Journal (DOUE) acts by publication date."
    )
    parser.add_argument(
        "date",
        help="Publication date in YYYY-MM-DD format, e.g. 2025-03-27",
    )
    parser.add_argument(
        "--language",
        default="ENG",
        help="EU language code (default: ENG)",
    )
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    client = DoueBulletinClient()

    try:
        acts = client.get_acts(args.date, language=args.language)
    except Exception as exc:
        print(f"Error while fetching acts: {exc}", file=sys.stderr)
        return 1

    print(f"Total acts: {len(acts)}")
    print("-" * 60)

    for act in acts:
        print(f"CELEX URI: {act.celex_uri}")
        print(f"Title: {act.title}")
        print(f"Date: {act.date}")
        if act.category_label:
            print(f"Category: {act.category_label}")
        if act.institution_label:
            print(f"Institution: {act.institution_label}")
        print("-" * 60)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
