# bulletin-fetcher

[![Tests](https://github.com/diegoglezsu/bulletin-fetcher/actions/workflows/tests.yml/badge.svg)](https://github.com/diegoglezsu/bulletin-fetcher/actions/workflows/tests.yml)
[![CodeQL](https://github.com/diegoglezsu/bulletin-fetcher/actions/workflows/github-code-scanning/codeql/badge.svg)](https://github.com/diegoglezsu/bulletin-fetcher/actions/workflows/github-code-scanning/codeql)
[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=diegoglezsu_bulletin-fetcher&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=diegoglezsu_bulletin-fetcher)
[![Codecov status](https://codecov.io/github/diegoglezsu/bulletin-fetcher/badge.svg?branch=main&service=github)](https://app.codecov.io/github/diegoglezsu/bulletin-fetcher)
[![PyPI version](https://img.shields.io/pypi/v/bulletin-fetcher.svg)](https://pypi.org/project/bulletin-fetcher/)
[![Documentation](https://img.shields.io/badge/docs-latest-blue.svg)](https://diegoglezsu.github.io/bulletin-fetcher/)
[![DOI](https://zenodo.org/badge/1193786609.svg)](https://doi.org/10.5281/zenodo.20156191)

## Description

![Bulletin Fetcher Logo](https://raw.githubusercontent.com/diegoglezsu/bulletin-fetcher/main/docs/assets/logo.png)

**bulletin-fetcher** is a Python library for programmatic access to European Union acts published in official bulletins, with current support for the **Official Journal of the European Union** through the [EUR-Lex / Cellar SPARQL endpoint](https://publications.europa.eu/webapi/rdf/sparql).

The library provides a high-level Python API that allows developers, researchers and legal-domain experts to search EU acts without writing SPARQL queries directly.

## Why bulletin-fetcher?

EU Official Journal acts can be queried through public semantic web infrastructure, but using the underlying SPARQL endpoint requires knowledge of RDF vocabularies, query structure and EUR-Lex metadata conventions and ontologies.

`bulletin-fetcher` abstracts this complexity behind a simple Python interface. Users can retrieve EU acts by publication date, date ranges, act type, publishing institution and textual content, while receiving Python objects, JSON-compatible dictionaries, XML, CSV outputs or pandas DataFrames suitable for further analysis.

## Main features

- Search EU acts from the Official Journal of the European Union.
- Filter acts by date or date range, act type, publishing institution, text contained in the act title, language.
- Fetch the content stream of an act by CELEX id or by the URI returned in search results.
- Retrieve available act types and publishing institutions.
- Return act search results as Python objects, JSON-compatible dictionaries, XML, CSV or pandas DataFrames.
- Work with Python instead of raw SPARQL queries.
- Integrate easily with notebooks, data pipelines and legal analytics workflows.

## Use Cases

bulletin-fetcher can be used for:

- Legal analytics
- Public policy research
- Regulatory monitoring
- Reproducible studies based on EU acts
- Data collection pipelines

## Quick Start

### Installation

Install from PyPI:

```bash
pip install bulletin-fetcher
```

Install with all dependencies:

```bash
pip install bulletin-fetcher[all]
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

print(f"Total acts: {len(acts)}")
if acts:
    first = acts[0]
    print(first.title)

    first_content = client.get_act_content(
        first.celex_uri,
        language="ENG",
    )
    print(first_content[:500])

    content_from_celex_id = client.get_act_content(
        "52025M12135",
        language="ENG",
    )
    print(content_from_celex_id[:500])
```

### Use Case Examples

The repository includes runnable scripts and notebooks with examples and use cases of the library. These scripts can be found in the `scripts/` directory.

- [Case 1: Evolution of AI Legislation in the EU](./scripts/use_cases/case_1_ai_evolution.ipynb)
- [Case 2: Comparison of EU Institutions](./scripts/use_cases/case_2_institution_comparison.ipynb)
- [Case 3: Dataset Analysis](./scripts/use_cases/case_3_reproducible_dataset.py)
- [Case 4: Tariff Analysis](./scripts/use_cases/case_4_tariff_analysis.ipynb)

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.

## Contact

For any questions or suggestions, feel free to reach out to the corresponding author:

- **Corresponding Author**: Diego González Suárez
- **Email**: <gonzalezsdiego@uniovi.es>
- **Collaborators**: Noelia Rico, Irene Díaz

## Acknowledgements

The authors gratefully acknowledge the financial support of the Asturian Agency for Science, Business Competitiveness and Innovation (SEKUENS) under Grant Agreement No. SEK-25-GRU-GIC-24-018. Noelia Rico and Irene Díaz also acknowledge support from the European project SCIMIN-CRM (Grant Agreement No. 101177746) and the funding from the Spanish Ministry of Science and Innovation through project PID2022-139886NB-I00.

## Citation

If you use `bulletin-fetcher` in your research, please cite it. Citation information is available in the [`CITATION.cff`](https://github.com/diegoglezsu/bulletin-fetcher/blob/main/CITATION.cff) file.
