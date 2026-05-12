"""
Shared test utilities for Nomi tests.

Import from here when you need helpers that are used across multiple
test files, such as value stabilization for snapshots or AST parsing
helpers.
"""

import ast
from typing import Mapping, Sequence, Set, Generator, Dict, Any
import types


def stabilize_value(value):
    """Convert unstable objects to short stable string form.

    Callables, generators, and modules are converted to descriptive
    name:class strings.  Collections are traversed recursively.
    """
    if isinstance(value, Mapping):
        return type(value)({k: stabilize_value(v) for k, v in value.items()})
    if isinstance(value, Set):
        return str(type(value)({stabilize_value(v) for v in value}))
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        return type(value)(stabilize_value(v) for v in value)
    if callable(value) or isinstance(value, (Generator, types.ModuleType)):
        name = getattr(value, '__name__', 'un-named')
        return f'{name}:class={type(value)}'
    if hasattr(value, '__dict__'):
        return f'instance of:{stabilize_value(type(value))}'
    return value


def stabilize_locals(local_vars, exclude_private=True):
    """Convert local variables dict to stable k:v pairs."""
    return {
        name: stabilize_value(value)
        for name, value in local_vars.items()
        if not (exclude_private and name.startswith('_'))
    }


def parse_stmt(generate_ast, code):
    """Parse source code and return the first top-level statement."""
    return generate_ast(code=code).body[0]
