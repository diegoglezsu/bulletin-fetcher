# bulletin-fetcher

[![Tests](https://github.com/diegoglezsu/bulletin-fetcher/actions/workflows/tests.yml/badge.svg)](https://github.com/diegoglezsu/bulletin-fetcher/actions/workflows/tests.yml)
[![CodeQL](https://github.com/diegoglezsu/bulletin-fetcher/actions/workflows/github-code-scanning/codeql/badge.svg)](https://github.com/diegoglezsu/bulletin-fetcher/actions/workflows/github-code-scanning/codeql)
[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=diegoglezsu_bulletin-fetcher&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=diegoglezsu_bulletin-fetcher)
[![Codecov status](https://codecov.io/github/diegoglezsu/bulletin-fetcher/badge.svg?branch=main&service=github)](https://app.codecov.io/github/diegoglezsu/bulletin-fetcher)
[![PyPI version](https://img.shields.io/pypi/v/bulletin-fetcher.svg)](https://pypi.org/project/bulletin-fetcher/)
[![Documentation](https://img.shields.io/badge/docs-latest-blue.svg)](https://diegoglezsu.github.io/bulletin-fetcher/)

## Description

![Bulletin Fetcher Logo](https://raw.githubusercontent.com/diegoglezsu/bulletin-fetcher/main/docs/assets/logo.jpg)

**bulletin-fetcher** is a Python library for programmatic access to legal acts published in official bulletins, with current support for the **Official Journal of the European Union** through the [EUR-Lex / Cellar SPARQL endpoint](https://publications.europa.eu/webapi/rdf/sparql).

The library provides a high-level Python API that allows developers, researchers and legal-domain experts to search EU legal acts without writing SPARQL queries directly.

## Why bulletin-fetcher?

EU legal acts can be queried through public semantic web infrastructure, but using the underlying SPARQL endpoint requires knowledge of RDF vocabularies, query structure and EUR-Lex metadata conventions and ontologies.

`bulletin-fetcher` abstracts this complexity behind a simple Python interface. Users can retrieve legal acts by publication date, date ranges, act type, publishing institution and textual content, while receiving Python objects, JSON-compatible dictionaries or CSV outputs suitable for further analysis.

## Main features

- Search EU legal acts from the Official Journal of the European Union.
- Filter acts by date or date range, act type, publishing institution, text contained in the act title, language.
- Retrieve available act types and publishing institutions.
- Return act search results as Python objects, JSON-compatible dictionaries or CSV.
- Work with Python instead of raw SPARQL queries.
- Integrate easily with notebooks, data pipelines and legal analytics workflows.

## Use Cases

bulletin-fetcher can be used for:

- Legal analytics
- Public policy research
- Regulatory monitoring
- Reproducible studies based on legal acts
- Data collection pipelines

## Quick Start

### Installation

Install from PyPI:

```bash
pip install bulletin-fetcher
```

### Basic Usage Example

Fetch acts for a publication date:

```python
from bulletin.eurlex.api.client import EurlexBulletinClient

client = EurlexBulletinClient()
acts = client.get_acts( 
    date="2025-01-01",
    date_end="2025-03-31",
    title_contains="artificial intelligence",
    language="ENG"
)

acts_csv = client.get_acts(
    date="2025-01-01",
    date_end="2025-03-31",
    title_contains="artificial intelligence",
    language="ENG",
    output_format="csv",
)

print(f"Total acts: {len(acts)}")
if acts:
    first = acts[0]
    print(first.celex_uri)
    print(first.title)
```

### Example scripts

The repository includes runnable scripts and notebooks with examples and use cases of the library. These scripts can be found in the `scripts/` directory.

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.

## Contact

For any questions or suggestions, feel free to reach out to the author:

- **Author**: Diego González Suárez
- **Email**: <gonzalezsdiego@uniovi.es>

## Acknowledgements

TODO: Add acknowledgements here.

## Citation

If you use `bulletin-fetcher` in academic work, please cite the project.

A `CITATION.cff` file will be added in a future release.

---
