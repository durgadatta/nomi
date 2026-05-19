"""Small public facade over today's interpreter runners.

This module is the first top-down architecture step from
``docs/language/architecture_refactoring_plan.md``.  It intentionally wraps the
existing runners instead of moving parser or interpreter internals yet.
"""

from __future__ import annotations

import contextlib
import io
from dataclasses import dataclass, field
from pathlib import Path
from time import perf_counter
from typing import Any

from prototype.runtime.diagnostics import (
    Diagnostic,
    RuntimeEvent,
    RuntimeEventCollector,
)
from prototype.runtime.pipeline import PipelineSpec, build_pipeline_spec
from prototype.syntax.core import dump_core, lower_python_ast_to_core
from prototype.syntax.features import render_feature_layer_table


@dataclass(frozen=True)
class ExecutionResult:
    """Structured result for callers that want an API instead of raw bindings."""

    mode: str
    profile: str
    pipeline: PipelineSpec
    bindings: dict[str, Any] = field(default_factory=dict)
    exception: Exception | None = None
    timings: dict[str, float] = field(default_factory=dict)
    value: Any = None
    has_value: bool = False
    stdout: str = ""
    stderr: str = ""
    diagnostics: tuple[Diagnostic, ...] = ()
    events: tuple[RuntimeEvent, ...] = ()

    @property
    def ok(self) -> bool:
        return self.exception is None


@dataclass(frozen=True)
class InspectionResult:
    """Structured result for read-only pipeline inspection."""

    mode: str
    profile: str
    pipeline: PipelineSpec
    stage: str
    output: str
    timings: dict[str, float] = field(default_factory=dict)


def execute(
    *,
    source: str | None = None,
    filename: str | Path | None = None,
    tree: Any | None = None,
    mode: str = "nomi",
    profile: str = "default",
    raise_on_error: bool = True,
    capture_output: bool = True,
    diagnostics: tuple[Diagnostic, ...] = (),
    events: tuple[RuntimeEvent, ...] = (),
    event_collector: RuntimeEventCollector | None = None,
) -> ExecutionResult:
    """Run source through the selected current interpreter mode.

    This is deliberately a facade over ``run_eval_loop``.  Later architecture
    slices can attach pipeline artifacts, diagnostics, events, timings, and
    sessions here without forcing every frontend to know parser internals.
    """

    pipeline = build_pipeline_spec(mode=mode, profile=profile)

    runner = pipeline.mode_spec.load_runner()
    collector = event_collector or RuntimeEventCollector(
        diagnostics=list(diagnostics),
        events=list(events),
    )
    started = perf_counter()
    stdout = io.StringIO()
    stderr = io.StringIO()
    stdout_context = (
        contextlib.redirect_stdout(stdout)
        if capture_output
        else contextlib.nullcontext()
    )
    stderr_context = (
        contextlib.redirect_stderr(stderr)
        if capture_output
        else contextlib.nullcontext()
    )
    try:
        with stdout_context, stderr_context:
            bindings = runner(code=source, file_name=filename, tree=tree)
    except Exception as exc:
        timings = {"total": perf_counter() - started}
        if raise_on_error:
            raise
        result_diagnostics, result_events = collector.snapshot()
        return ExecutionResult(
            mode=mode,
            profile=profile,
            pipeline=pipeline,
            exception=exc,
            timings=timings,
            stdout=stdout.getvalue(),
            stderr=stderr.getvalue(),
            diagnostics=result_diagnostics,
            events=result_events,
        )
    timings = {"total": perf_counter() - started}
    result_diagnostics, result_events = collector.snapshot()

    # TODO(NOMI-ARCH-004): Add detailed stage timings once frontends migrate to
    # this structured result.
    return ExecutionResult(
        mode=mode,
        profile=profile,
        pipeline=pipeline,
        bindings=bindings,
        timings=timings,
        stdout=stdout.getvalue(),
        stderr=stderr.getvalue(),
        diagnostics=result_diagnostics,
        events=result_events,
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

    pipeline = build_pipeline_spec(mode=mode, profile=profile)
    started = perf_counter()
    if stage == "features":
        output = render_feature_layer_table()
        timings = {"total": perf_counter() - started}
        return InspectionResult(
            mode=mode,
            profile=profile,
            pipeline=pipeline,
            stage=stage,
            output=output,
            timings=timings,
        )

    if stage in {"passes", "desugar_passes"}:
        from prototype.parser.nomi.desugar.pipeline import render_desugar_pass_table

        # TODO(NOMI-SUBSTRATE-033): Route runtime/parser feature profiles into
        # this inspection path so it shows the passes that this mode/profile
        # would actually execute, not only the global or default registry view.
        output = render_desugar_pass_table()
        timings = {"total": perf_counter() - started}
        return InspectionResult(
            mode=mode,
            profile=profile,
            pipeline=pipeline,
            stage=stage,
            output=output,
            timings=timings,
        )

    if stage in {"expansions", "desugar_expansions"}:
        from prototype.parser.nomi.desugar.pipeline import render_desugar_expansion

        parser = pipeline.mode_spec.load_parser()
        tree = parser(filename=filename, code=source)
        desugar_profile = "default" if mode == "nomi" else None
        output = render_desugar_expansion(tree, profile=desugar_profile)
        timings = {"total": perf_counter() - started}
        return InspectionResult(
            mode=mode,
            profile=profile,
            pipeline=pipeline,
            stage=stage,
            output=output,
            timings=timings,
        )

    if stage in {"core", "implementation_core"}:
        parser = pipeline.mode_spec.load_parser()
        tree = parser(filename=filename, code=source)
        core = lower_python_ast_to_core(tree)
        output = dump_core(core)
        timings = {"total": perf_counter() - started}
        return InspectionResult(
            mode=mode,
            profile=profile,
            pipeline=pipeline,
            stage=stage,
            output=output,
            timings=timings,
        )

    if stage != "python_ast":
        # TODO(NOMI-ARCH-001): Add raw tree, transformed tree, surface AST,
        # core AST, and backend-lowered stages as PipelineSpec grows.
        raise ValueError(f"Unsupported inspection stage: {stage!r}")

    parser = pipeline.mode_spec.load_parser()
    output = parser(filename=filename, code=source, dump=True)
    timings = {"total": perf_counter() - started}
    return InspectionResult(
        mode=mode,
        profile=profile,
        pipeline=pipeline,
        stage=stage,
        output=output,
        timings=timings,
    )


def create_session(
    *,
    mode: str = "nomi",
    profile: str = "default",
    cache_size: int = 0,
):
    """Create a persistent runtime session for cells, notebooks, and REPLs."""

    # Local import avoids a module cycle: RuntimeSession returns ExecutionResult.
    from prototype.runtime.session import RuntimeSession

    return RuntimeSession(mode=mode, profile=profile, cache_size=cache_size)
