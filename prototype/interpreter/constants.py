"""
Constants and shared structures for the interpreter and parser layers.
"""

from dataclasses import dataclass, field
from typing import Any, List, Optional
import ast


BLOCK_KWARG = "__block__"


@dataclass(slots=True)
class Block:
    """Represents a caller-side block attached to a function call.

    Replaces the ad-hoc tuple packing ``(body, params, env)`` that
    was smuggled through ``ast.keyword.value``.
    """

    body: List[ast.stmt]
    """Statements forming the block body (suite)."""

    params: Optional[ast.expr] = None
    """Optional parameter target for yielded values (testlist_star_expr)."""

    env: Any = None
    """The environment captured at the call site.  Populated at eval time."""

    def __bool__(self):
        return bool(self.body)

