# bulletin-fetcher

bulletin-fetcher is a Python library for searching and managing official bulletins,
currently focused on the Official Journal of the European Union (DOUE).

## Why This Project

- Query official acts from EUR-Lex/Cellar.
- Work with Python objects instead of raw SPARQL JSON.
- Keep a clean architecture with a public API layer and a data connector layer.

## Quick Links

- Getting Started: installation and first query flow.
- API Reference: generated docs from source code docstrings.

## Example

```python
from bulletin.doue.api.client import DoueBulletinClient

client = DoueBulletinClient()
acts = client.get_acts("2025-03-27", language="ENG")
print(len(acts))
```
