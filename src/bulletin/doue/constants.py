from typing import Literal

SPARQL_ENDPOINT = "https://publications.europa.eu/webapi/rdf/sparql"

DEFAULT_LANGUAGE = "ENG"

EuLanguageCode = Literal[
    "SPA", "ENG", "FRA", "DEU", "ITA", "POR", "NLD", "POL", "RON", 
    "BUL", "CES", "DAN", "ELL", "EST", "FIN", "GAE", "HRV", "HUN", 
    "LIT", "LAV", "MLT", "SLK", "SLV", "SWE"
]

# Mapping from EU authority language codes to ISO 639-1 codes
# used in SPARQL FILTER(LANG(...)) clauses
LANGUAGE_CODE_MAP = {
    "SPA": "es",
    "ENG": "en",
    "FRA": "fr",
    "DEU": "de",
    "ITA": "it",
    "POR": "pt",
    "NLD": "nl",
    "POL": "pl",
    "RON": "ro",
    "BUL": "bg",
    "CES": "cs",
    "DAN": "da",
    "ELL": "el",
    "EST": "et",
    "FIN": "fi",
    "GAE": "ga",
    "HRV": "hr",
    "HUN": "hu",
    "LIT": "lt",
    "LAV": "lv",
    "MLT": "mt",
    "SLK": "sk",
    "SLV": "sl",
    "SWE": "sv",
}
