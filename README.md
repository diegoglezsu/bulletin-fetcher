# bulletin-fetcher

[![Tests](https://github.com/diegoglezsu/bulletin-fetcher/actions/workflows/tests.yml/badge.svg)](https://github.com/diegoglezsu/bulletin-fetcher/actions/workflows/tests.yml)
[![CodeQL](https://github.com/diegoglezsu/bulletin-fetcher/actions/workflows/github-code-scanning/codeql/badge.svg)](https://github.com/diegoglezsu/bulletin-fetcher/actions/workflows/github-code-scanning/codeql)
[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=diegoglezsu_bulletin-fetcher&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=diegoglezsu_bulletin-fetcher)
[![Codecov status](https://codecov.io/github/diegoglezsu/bulletin-fetcher/badge.svg?branch=main&service=github)](https://app.codecov.io/github/diegoglezsu/bulletin-fetcher)
[![PyPI version](https://img.shields.io/pypi/v/bulletin-fetcher.svg)](https://pypi.org/project/bulletin-fetcher/)
[![Documentation](https://img.shields.io/badge/docs-latest-blue.svg)](https://diegoglezsu.github.io/bulletin-fetcher/)

## Description

![Bulletin Fetcher Logo](https://raw.githubusercontent.com/diegoglezsu/bulletin-fetcher/main/docs/assets/logo.jpg)

**bulletin-fetcher** is a Python library to query and fetch official bulletins. It makes easier to work with the Official Journal Data in python, providing a high-level API and data models. Current support:

- Official Journal of the European Union (DOUE) via EUR-Lex / Cellar SPARQL endpoint.

## Key Features

- Query official acts from Legal Institutions.
- Works with Python objects instead of raw JSON and gets away from Web Services.
- Easier for data manipulation and integration in notebooks through Python models.
- Keep a clean architecture with a public API layer and a data connector layer.

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
acts = client.get_acts(date="2025-03-31")

print(f"Total acts: {len(acts)}")
if acts:
 first = acts[0]
 print(first.celex_uri)
 print(first.title)
```

### Standalone Script

The repository includes a runnable script:

```bash
python scripts/run_doue.py
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
- **GitHub**: [diegoglezsu](https://github.com/diegoglezsu)

---
