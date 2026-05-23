"""Eval backend boundary for Nomi.

Mirrors the parser frontend registry pattern in
``prototype/parser/nomi/frontend.py``.  Each eval backend declares capabilities
and consumes Core IR (or a compatible artifact) to produce an
``EvalBackendResult``.

The Python AST backend is the first registered backend and preserves the
existing interpreter path without changes.  Future backends (core-direct,
Wasm, native) can register here and graduate through capability promotion.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True, slots=True)
class EvalBackendCapabilities:
    """Current support level for one eval backend."""

    evaluates_native_ir: bool = False
    lowers_to_python_ast: bool = False
    supports_full_language: bool = False
    supports_blocks: bool = False
    supports_exceptions: bool = False
    supports_resume: bool = False
    supports_python_interop: bool = False
    supports_source_maps: bool = False
    selectable_for_execution: bool = False


@dataclass(frozen=True, slots=True)
class EvalBackendSpec:
    """Describes an eval backend target."""

    name: str
    status: str
    ir_contract: str
    implementation: str
    output_contract: str
    capabilities: EvalBackendCapabilities = field(default_factory=EvalBackendCapabilities)
    notes: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class EvalBackendResult:
    """Structured result from an eval backend after evaluation."""

    bindings: dict[str, Any]
    value: Any = None
    has_value: bool = False
    diagnostics: tuple[str, ...] = ()
    stdout: str = ""
    stderr: str = ""


# Registry of backend implementations.
# python-ast entries are constructed per-mode via ``make_python_ast_backend_for_mode``.
_BACKENDS: dict[str, Any] = {}


def register_backend(name: str, backend: Any) -> None:
    _BACKENDS[name] = backend


def get_eval_backend(name: str) -> Any:
    try:
        return _BACKENDS[name]
    except KeyError as exc:
        available = ", ".join(sorted(_BACKENDS))
        raise ValueError(
            f"Unknown eval backend: {name!r}. "
            f"Available: {available or '(none)'}"
        ) from exc


def get_selectable_eval_backends() -> tuple[str, ...]:
    return tuple(
        name
        for name, backend in _BACKENDS.items()
        if backend is not None
        and getattr(backend, "spec", None) is not None
        and backend.spec.capabilities.selectable_for_execution
    )


def render_eval_backend_table() -> str:
    rows: list[str] = []
    header = f"| {'backend':<24} | {'status':<22} | {'IR contract':<24} | {'selectable':<10} |"
    rows.append(header)
    rows.append("|" + "-" * (len(header) - 2) + "|")
    for name, backend in sorted(_BACKENDS.items()):
        if backend is None:
            rows.append(
                f"| {name:<24} | {'(mode-constructed)':<22} | {'N/A':<24} | {'no':<10} |"
            )
            continue
        spec = getattr(backend, "spec", None)
        if spec is None:
            rows.append(
                f"| {name:<24} | {'(no spec)':<22} | {'N/A':<24} | {'no':<10} |"
            )
            continue
        selectable = "yes" if spec.capabilities.selectable_for_execution else "no"
        rows.append(
            f"| {name:<24} | {spec.status:<22} | {spec.ir_contract:<24} | {selectable:<10} |"
        )
    return "\n".join(rows)


def _load_builtin_backends() -> None:
    """Import built-in backends so their registry entries are available."""
    from prototype.runtime.backends import core_direct  # noqa: F401
    from prototype.runtime.backends import core_runtime  # noqa: F401
    from prototype.runtime.backends import js_core  # noqa: F401
    from prototype.runtime.backends import python_ast  # noqa: F401


_load_builtin_backends()
