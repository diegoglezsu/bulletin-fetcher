# Getting Started

## Requirements 🐍

- Python 3.7+
- Internet access for live DOUE queries

## Installation

Install from PyPI:

```bash
pip install bulletin-fetcher
```

Install development dependencies (project clone):

```bash
pip install -e .[dev]
```

## First Query 🚀

```python
from bulletin.doue.api.client import DoueBulletinClient

client = DoueBulletinClient()
acts = client.get_acts("2025-03-27", language="ENG")

for act in acts[:3]:
 print(act.celex_uri)
 print(act.title)
 print(act.date)
```

### Run the Example Script

The [repository](https://github.com/diegoglezsu/bulletin-fetcher/tree/main/scripts) includes an executable helper script:

```bash
python scripts/run_doue.py 2025-03-27 --language ENG
```
