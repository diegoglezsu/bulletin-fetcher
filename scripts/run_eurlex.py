"""Small script to query EUR-Lex acts using bulletin-fetcher."""

import datetime
import sys

from bulletin.eurlex.api.client import EurlexBulletinClient


def main() -> int:

    client = EurlexBulletinClient()

    date = "2025-01-01"
    date_end = "2026-03-31"
    title_contains = "science"
    category_type = "ANNOUNC"
    institution_type = "COM"
    language = "ENG"
    # Examples of filtering:
    # - Pass category_type="ANNOUNC" to filter by category type (e.g., announcements)
    # - Pass institution_type="COM" to filter by institution type (e.g., European Commission)

    try:
        acts = client.get_acts(
            date=date,
            date_end=date_end,
            language=language,
            title_contains=title_contains,
            category_type=category_type,
            institution_type=institution_type,
        )
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

    if acts:
        first_act = acts[0]
        print("\n" + "=" * 60 + "\n")
        print("Fetching content for the first act:")
        print(first_act.celex_uri)

        try:
            content = client.get_act_content(
                "52025M12135",
                language=language,
                content_format="pdf",
            )
            # Save the pdf content to a file
            with open("./scripts/act_content.pdf", "wb") as f:
                f.write(content)
        except Exception as exc:
            print(f"Error while fetching act content: {exc}", file=sys.stderr)
        else:
            print(content)

    print("\n" + "=" * 60 + "\n")

    formats = ["objects", "json", "csv", "xml", "df"]

    for fmt in formats:
        print(f"Testing output format: {fmt}")
        output = client.get_acts(
            date=date,
            date_end=date_end,
            title_contains=title_contains,
            language=language,
            category_type=category_type,
            institution_type=institution_type,
            output_format=fmt,
        )
        print(output)
        print("-" * 60)

    today_acts = client.get_acts(date=datetime.date.today().isoformat())
    print(f"Acts published on {datetime.date.today().isoformat()}: {len(today_acts)}")
    for act in today_acts:
        print(f"- {act.title} ({act.celex_uri}) {act.institution_label}")
    print("Today documents can be checked at https://eur-lex.europa.eu/oj/direct-access.html")
    
    '''
    # Testing institution types with a search filter
    institution_types = client.get_institution_types(language=language, search="environment")
    print(f"Institution types containing 'environment': {len(institution_types)}")
    for inst_type in institution_types:
        print(f"- {inst_type.label} ({inst_type.code})")
    
    # Testing category types with a search filter
    category_types = client.get_category_types(language=language, search="communication")
    print(f"Category types containing 'communication': {len(category_types)}")
    for cat_type in category_types:
        print(f"- {cat_type.label} ({cat_type.code})")
    '''

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
