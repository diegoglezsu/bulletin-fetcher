"""Constants used by the DOUE client and repository layers."""

#: EUR-Lex / Cellar SPARQL endpoint used for DOUE queries.
SPARQL_ENDPOINT = "https://publications.europa.eu/webapi/rdf/sparql"

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

# Keep a single source of truth for available language codes.
#: Tuple with all supported EU authority language codes.
SUPPORTED_LANGUAGE_CODES = tuple(LANGUAGE_CODE_MAP)

#: Default language code used by the client when no language is provided.
DEFAULT_LANGUAGE = "ENG"
