"""Small script to query DOUE acts using bulletin-fetcher."""

import sys

from bulletin.doue.api.client import DoueBulletinClient

def main() -> int:

    client = DoueBulletinClient()

    date = "2026-01-01"
    date_end = "2026-03-31"
    title_contains = "euronest"
    language = "SPA"

    try:
        acts = client.get_acts(date=date, language=language, date_end=date_end, title_contains=title_contains)
    except Exception as exc:
        print(f"Error while fetching acts: {exc}", file=sys.stderr)
        return 1

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

    print(f"Total acts: {len(acts)}")
    print("Done.")
    #csv_output = client.get_acts_csv(date=date, date_end=date_end, language=language)  # Example of fetching CSV output
    #print("CSV Output:")
    #print(csv_output)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
