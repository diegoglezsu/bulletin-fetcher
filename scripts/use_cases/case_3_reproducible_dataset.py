"""
Case 3: Generator of Reproducible Dataset

This script downloads a specific dataset and exports it to CSV with fixed parameters.
The objective is that any researcher can run this script and obtain
exactly the same dataset to reproduce a study.

Example: "Official acts of the EU mentioning 'agriculture' (2020-2025)"
"""

import sys
from pathlib import Path
from bulletin.eurlex.api.client import EurlexBulletinClient


def main() -> int:
    client = EurlexBulletinClient()

    DATE_START = "2017-01-01"
    DATE_END = "2023-12-31"
    # We want to find all acts that mention "disease" in the title, in English language.
    TITLE_KEYWORD = "disease"
    LANGUAGE = "ENG"
    # Code Ocean provides /results; locally use a results folder next to this script
    # Both /code and /results exist only in a Code Ocean capsule
    if Path("/code").is_dir() and Path("/results").is_dir():
        RESULTS_DIR = Path("/results")
    else:
        RESULTS_DIR = Path(__file__).resolve().parent / "results"
    OUTPUT_FILE = RESULTS_DIR / "dataset_eu_disease_acts_2017_2023.csv"

    print("=" * 60)
    print("Generator of Reproducible Dataset: EU Disease Acts")
    print("=" * 60)
    print("Parameters:")
    print(f"- Start date : {DATE_START}")
    print(f"- End date    : {DATE_END}")
    print(f"- Title keyword: '{TITLE_KEYWORD}'")
    print(f"- Language       : {LANGUAGE}")
    print(f"- File      : {OUTPUT_FILE}")
    print("-" * 60)

    try:
        print("Consulting the EUR-Lex SPARQL endpoint... (this may take a few seconds)")

        # Ask get_acts to extract all metadata directly as a DataFrame.
        acts_df = client.get_acts(
            date=DATE_START,
            date_end=DATE_END,
            title_contains=TITLE_KEYWORD,
            language=LANGUAGE,
            output_format="df",
        )

    except Exception as exc:
        print(
            f"\n[ERROR] An error occurred while downloading the data:\n{exc}",
            file=sys.stderr,
        )
        return 1

    # Save file in this directory, so that it can be easily found by the user
    try:
        RESULTS_DIR.mkdir(parents=True, exist_ok=True)
        acts_df.to_csv(OUTPUT_FILE, index=False)
        print(f"\n[SUCCESS] Dataset generated correctly and saved in: {OUTPUT_FILE}")
    except Exception as exc:
        print(
            f"\n[ERROR] Error occurred while saving the CSV file:\n{exc}",
            file=sys.stderr,
        )
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
