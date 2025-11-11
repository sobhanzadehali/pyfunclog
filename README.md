# PyFuncLog

Comprehensive function logging with automatic sensitive data protection.

## Features

- 🕵️‍♂️ **Automatic Variable Capture**: Captures all local variables and function arguments
- 🔒 **Sensitive Data Protection**: Automatically masks passwords, tokens, API keys, etc.
- 🎯 **Flexible Decorators**: Choose what to log - everything, returns, or just locals
- 📝 **Structured Logging**: JSON-formatted logs with clear structure
- 🚀 **Easy Integration**: Simple decorator-based approach

## Installation

```bash
pip install pyfunclog
```

## usage example:
```python
import asyncio
from pyfunclog import async_secure_log_function

@async_secure_log_function()
async def fetch_data(api_key: str, user_id: int):
    # api_key will be automatically masked
    await asyncio.sleep(0.1)
    result = {"user_id": user_id, "data": "sample"}
    return result

# Or use universal decorator for both sync and async
from pyfunclog import universal_log

@universal_log
async def async_function(x):
    return x * 2

@universal_log
def sync_function(x):
    return x * 2
```

## fastapi integration
```python
from fastapi import FastAPI
from pyfunclog import FastAPILoggingSupport, async_secure_log_function

app = FastAPI()
logging_support = FastAPILoggingSupport()
logging_support.middleware(app)  # Add request/response logging

@app.get("/users/{user_id}")
@async_secure_log_function()
async def get_user(user_id: int, token: str):
    # token will be automatically masked
    return {"user_id": user_id, "name": "John Doe"}
```
