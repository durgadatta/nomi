from functools import lru_cache
from importlib import import_module
from typing import Any


@lru_cache(maxsize=128)
def resolve_dotted(path: str) -> Any:
    """Import and return an object from a dotted path like 'pkg.mod.Thing'."""
    module_name, attr_name = path.rsplit(".", 1)
    module = import_module(module_name)
    return getattr(module, attr_name)
