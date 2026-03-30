# bulletin.doue

DOUE support is split into two layers:

- API layer: high-level client and typed parsing models.
- Repository layer: connector for query construction and endpoint communication.

## Recommended Imports

```python
from bulletin.doue.api.client import DoueBulletinClient
from bulletin.doue.api.models import DoueOfficialAct
```

## Public API Layer

::: bulletin.doue.api.client
::: bulletin.doue.api.models

## Exceptions

::: bulletin.doue.exceptions

## Repository Layer (Internal)

The connector is primarily intended for internal use and testing:

::: bulletin.doue.repository._connector
