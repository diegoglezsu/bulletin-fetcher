# bulletin-fetcher

[![Tests](https://github.com/diegoglezsu/bulletin-fetcher/actions/workflows/tests.yml/badge.svg)](https://github.com/diegoglezsu/bulletin-fetcher/actions/workflows/tests.yml)
[![CodeQL](https://github.com/diegoglezsu/bulletin-fetcher/actions/workflows/github-code-scanning/codeql/badge.svg)](https://github.com/diegoglezsu/bulletin-fetcher/actions/workflows/github-code-scanning/codeql)
[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=diegoglezsu_bulletin-fetcher&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=diegoglezsu_bulletin-fetcher)
[![Codecov status](https://codecov.io/github/diegoglezsu/bulletin-fetcher/badge.svg?branch=main&service=github)](https://app.codecov.io/gh/diegoglezsu/bulletin-fetcher)
[![PyPI version](https://img.shields.io/pypi/v/bulletin-fetcher.svg)](https://pypi.org/project/bulletin-fetcher/)
[![Documentation](https://img.shields.io/badge/docs-latest-blue.svg)](https://diegoglezsu.github.io/bulletin-fetcher/)

## Description

**bulletin-fetcher** is a Python library to query and parse official bulletins,
starting with the Official Journal of the European Union (DOUE) via EUR-Lex
and the Cellar SPARQL endpoint.

## Key Features

- Python models for bulletin entries.
- High-level client API for date-based DOUE queries.
- Built-in parsing from raw SPARQL JSON to dataclasses.
- Custom exception hierarchy for query and endpoint failures.
- Test suite with unit and integration coverage.

## Installation

Install from PyPI:

```bash
pip install bulletin-fetcher
```

## Usage

### Quick Example

Fetch acts for a publication date:

```python
from bulletin.doue.api.client import DoueBulletinClient

client = DoueBulletinClient()
acts = client.get_acts("2025-03-27", language="ENG")

print(f"Total acts: {len(acts)}")
if acts:
 first = acts[0]
 print(first.celex_uri)
 print(first.title)
 print(first.date)
```

### Standalone Script

The repository includes a runnable script:

```bash
python scripts/run_doue.py 2025-03-27 --language ENG
```

## Contributing

Contributions are welcome! Please follow the standard steps:

1. Fork the project.
2. Create a branch for your feature (`git checkout -b feature/AmazingFeature`).
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`).
4. Push to the branch (`git push origin feature/AmazingFeature`).
5. Open a Pull Request.

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.

## Contact

For any questions or suggestions, feel free to reach out to the author:

- **Author**: Diego González Suárez
- **Email**: <gonzalezsdiego@uniovi.es>

## Acknowledgements

- EUR-Lex / Cellar SPARQL endpoint
- MkDocs and Material for MkDocs

---
