# Getting Started

## Requirements

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

## First Query

```python
from bulletin.doue.api.client import DoueBulletinClient

client = DoueBulletinClient()
acts = client.get_acts("2025-03-27", language="ENG")

for act in acts[:3]:
 print(act.celex_uri)
 print(act.title)
 print(act.date)
```

## Language Codes

`DoueBulletinClient.get_acts` accepts EU authority language codes such as:

- `ENG`, `SPA`, `FRA`, `DEU`, `ITA`, `POR`, `NLD`, `POL`
- and others defined in `bulletin.doue.constants.EuLanguageCode`

## Run the Example Script

The repository includes an executable helper script:

```bash
python scripts/run_doue.py 2025-03-27 --language ENG --limit 5
```
