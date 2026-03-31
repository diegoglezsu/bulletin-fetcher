# bulletin.doue

DOUE support is split into two layers:

- API layer: high-level client and typed parsing models.
- Repository layer: connector for query construction and endpoint communication.

## Recommended Imports

```python
from bulletin.doue.api.client import DoueBulletinClient
from bulletin.doue.api.models import DoueOfficialAct
```

## Client

::: bulletin.doue.api.client.DoueBulletinClient
    options:
      heading_level: 3
      show_root_heading: true
      show_root_toc_entry: true

## Models

::: bulletin.doue.api.models.DoueOfficialAct
    options:
      heading_level: 3
      show_root_heading: true
      show_root_toc_entry: true

## Constants

::: bulletin.doue.constants.LANGUAGE_CODE_MAP
    options:
      heading_level: 3
      show_root_heading: true
      show_root_toc_entry: true
