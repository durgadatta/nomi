"""
Dispatch helper for selecting an interpreter at runtime.

Test files import `get_run_eval_loop` instead of a hardcoded interpreter
import. The conftest fixture controls which interpreter(s) are tested via
the --interpreter-modes CLI flag or NOMI_INTERPRETER_MODE env var.
"""

from typing import Callable, Dict, Any

INTERPRETER_MODES = ("python", "nomi", "reduced")
_REGISTRY: Dict[str, Callable] = {}


def _load():
    if _REGISTRY:
        return
    from prototype.interpreter.python.usage import run_eval_loop as py
    from prototype.interpreter.nomi.usage import run_eval_loop as nomi
    from prototype.interpreter.reduced.usage import run_eval_loop as reduced
    _REGISTRY.update(python=py, nomi=nomi, reduced=reduced)


def get_run_eval_loop(mode: str) -> Callable[..., Dict[str, Any]]:
    _load()
    if mode not in _REGISTRY:
        raise ValueError(f"Unknown interpreter mode: {mode!r}. "
                         f"Valid modes: {tuple(_REGISTRY.keys())}")
    return _REGISTRY[mode]
