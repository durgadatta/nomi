"""
Dispatch helper for selecting an interpreter at runtime.

Test files import `get_run_eval_loop` instead of a hardcoded interpreter
import. The conftest fixture controls which interpreter(s) are tested via
the --interpreter-modes CLI flag or NOMI_INTERPRETER_MODE env var.
"""

from typing import Callable, Dict, Any

from prototype.runtime.modes import INTERPRETER_MODES, get_runner


_REGISTRY: Dict[str, Callable] = {}


def get_run_eval_loop(mode: str) -> Callable[..., Dict[str, Any]]:
    if mode not in _REGISTRY:
        _REGISTRY[mode] = get_runner(mode)
    return _REGISTRY[mode]
