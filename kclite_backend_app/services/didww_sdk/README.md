# README.md

"""

# didww_sdk

A lightweight Python SDK for the DIDWW API v3. It provides methods to list and reserve DIDs, send SMS, initiate calls, and configure callbacks.

## Installation

```bash
pip install didww_sdk
```

## Usage

```python
from didww_sdk import DidwwClient

client = DidwwClient(api_key="xxx", api_secret="yyy", sandbox=True)
numbers = client.list_available_dids("US")
report = client.reserve_did(numbers[0])
"""
```
