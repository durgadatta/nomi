"""Public runtime facade for Nomi execution."""

from .api import ExecutionResult, execute

__all__ = [
    "ExecutionResult",
    "execute",
]
