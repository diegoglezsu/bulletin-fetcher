from collections.abc import Mapping
import csv
import io
from typing import Any

from .api.models import DoueOfficialAct


def parse_results(results: Mapping[str, Any]) -> list[DoueOfficialAct]:
    """Parse SPARQL results into a list of DoueOfficialAct objects."""
    try:
        bindings = results["results"]["bindings"]
    except KeyError as exc:
        raise KeyError("Invalid SPARQL response: missing 'results.bindings'") from exc

    if not isinstance(bindings, list):
        raise TypeError("Invalid SPARQL response: 'bindings' must be a list")

    acts: list[DoueOfficialAct] = []
    for binding in bindings:
        if not isinstance(binding, Mapping):
            raise TypeError("Invalid SPARQL response: each binding must be a mapping")
        acts.append(DoueOfficialAct._from_binding(binding))

    return acts


def acts_to_csv(acts: list[DoueOfficialAct]) -> str:
    """Serialize a list of acts to CSV format."""
    fieldnames = [
        "celex_uri",
        "act_number",
        "title",
        "date",
        "section_code",
        "subsection_code",
        "category_code",
        "category_uri",
        "category_label",
        "institution_code",
        "institution_uri",
        "institution_label",
    ]
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=fieldnames, quoting=csv.QUOTE_ALL)
    writer.writeheader()
    for act in acts:
        writer.writerow(act._to_dict())
    return buffer.getvalue()
