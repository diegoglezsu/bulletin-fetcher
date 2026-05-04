# Getting Started

## Requirements 🐍

- Python 3.7+
- Internet access for live EUR-Lex queries

## Installation

Install from PyPI:

```bash
pip install bulletin-fetcher
```

Install with all dependencies:

```bash
pip install bulletin-fetcher[all]
```

Install development dependencies (project clone):

```bash
pip install -e .[dev]
```

## First Query 🚀

```python
from bulletin.eurlex.api.client import EurlexBulletinClient

client = EurlexBulletinClient()
acts = client.get_acts( 
    date="2025-01-01",
    date_end="2025-03-31",
    title_contains="artificial intelligence",
    language="ENG"
)

acts_json = client.get_acts(
    date="2025-01-01",
    date_end="2025-03-31",
    title_contains="artificial intelligence",
    language="ENG",
    output_format="json",
)

acts_xml = client.get_acts(
    date="2025-01-01",
    date_end="2025-03-31",
    title_contains="artificial intelligence",
    language="ENG",
    output_format="xml",
)

acts_df = client.get_acts(
    date="2025-01-01",
    date_end="2025-03-31",
    title_contains="artificial intelligence",
    language="ENG",
    output_format="df",
)

print(f"Total acts: {len(acts)}")
if acts:
    first = acts[0]
    print(first.celex_uri)
    print(first.title)
```

### Run Example Scripts

The repository includes runnable scripts and notebooks with examples and use cases of the library. These scripts can be found in the [`scripts`](https://github.com/diegoglezsu/bulletin-fetcher/tree/main/scripts) directory.
