"""Small public facade over today's interpreter runners.

This module is the first top-down architecture step from
``docs/language/architecture_refactoring_plan.md``.  It intentionally wraps the
existing runners instead of moving parser or interpreter internals yet.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from prototype.runtime.modes import get_mode_spec, get_runner


@dataclass(frozen=True)
class ExecutionResult:
    """Structured result for callers that want an API instead of raw bindings."""

    mode: str
    profile: str
    bindings: dict[str, Any] = field(default_factory=dict)
    exception: Exception | None = None

    @property
    def ok(self) -> bool:
        return self.exception is None


@dataclass(frozen=True)
class InspectionResult:
    """Structured result for read-only pipeline inspection."""

    mode: str
    profile: str
    stage: str
    output: str


def _ensure_default_profile(profile: str) -> None:
    if profile != "default":
        # TODO(NOMI-ARCH-002): Route named feature profiles through mode
        # metadata once the parser supports feature-selected pipelines.
        raise ValueError(f"Unsupported runtime profile: {profile!r}")


def execute(
    *,
    source: str | None = None,
    filename: str | Path | None = None,
    tree: Any | None = None,
    mode: str = "nomi",
    profile: str = "default",
    raise_on_error: bool = True,
) -> ExecutionResult:
    """Run source through the selected current interpreter mode.

    This is deliberately a facade over ``run_eval_loop``.  Later architecture
    slices can attach pipeline artifacts, diagnostics, events, timings, and
    sessions here without forcing every frontend to know parser internals.
    """

    _ensure_default_profile(profile)

    runner = get_runner(mode)
    try:
        bindings = runner(code=source, file_name=filename, tree=tree)
    except Exception as exc:
        if raise_on_error:
            raise
        return ExecutionResult(
            mode=mode,
            profile=profile,
            exception=exc,
        )

    # TODO(NOMI-ARCH-004): Add stdout/stderr, diagnostics, events, and stage
    # timings once frontends migrate to this structured result.
    return ExecutionResult(
        mode=mode,
        profile=profile,
        bindings=bindings,
    )


def inspect(
    *,
    source: str | None = None,
    filename: str | Path | None = None,
    mode: str = "nomi",
    profile: str = "default",
    stage: str = "python_ast",
) -> InspectionResult:
    """Inspect one read-only pipeline artifact for the selected mode."""

    _ensure_default_profile(profile)
    if stage != "python_ast":
        # TODO(NOMI-ARCH-001): Add raw tree, transformed tree, surface AST,
        # core AST, and backend-lowered stages as PipelineSpec grows.
        raise ValueError(f"Unsupported inspection stage: {stage!r}")

    parser = get_mode_spec(mode).load_parser()
    output = parser(filename=filename, code=source, dump=True)
    return InspectionResult(
        mode=mode,
        profile=profile,
        stage=stage,
        output=output,
    )
