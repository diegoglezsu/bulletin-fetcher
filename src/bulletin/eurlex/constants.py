"""Constants used by the EUR-Lex client and repository layers."""

#: Base domain for EU publications resources.
CELLAR_DOMAIN = "publications.europa.eu"

#: EUR-Lex / Cellar SPARQL endpoint used for queries.
SPARQL_ENDPOINT = f"https://{CELLAR_DOMAIN}/webapi/rdf/sparql"

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
    "GLE": "ga",
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

#: Available acts output formats
ACTS_OUTPUT_FORMAT_OBJECTS = "objects"
ACTS_OUTPUT_FORMAT_JSON = "json"
ACTS_OUTPUT_FORMAT_CSV = "csv"
ACTS_OUTPUT_FORMAT_XML = "xml"
ACTS_OUTPUT_FORMAT_PANDASDF = "df"
SUPPORTED_ACTS_OUTPUT_FORMATS = frozenset(
    {
        ACTS_OUTPUT_FORMAT_OBJECTS,
        ACTS_OUTPUT_FORMAT_JSON,
        ACTS_OUTPUT_FORMAT_CSV,
        ACTS_OUTPUT_FORMAT_XML,
        ACTS_OUTPUT_FORMAT_PANDASDF,
    }
)

#: Available act content formats retrieved through Cellar content negotiation.
ACT_CONTENT_FORMAT_HTML = "html"
ACT_CONTENT_FORMAT_PDF = "pdf"
SUPPORTED_ACT_CONTENT_FORMATS = frozenset(
    {
        ACT_CONTENT_FORMAT_HTML,
        ACT_CONTENT_FORMAT_PDF,
    }
)
