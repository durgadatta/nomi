"""Small public facade over today's interpreter runners.

This module is the first top-down architecture step from
``docs/language/architecture_refactoring_plan.md``.  It intentionally wraps the
existing runners instead of moving parser or interpreter internals yet.
"""

from __future__ import annotations

import ast
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
from prototype.syntax.core import (
    core_to_python_ast,
    dump_core,
    lower_python_ast_to_core,
    verify_core,
)
from prototype.syntax.features import (
    DEFAULT_DESUGAR_PROFILE,
    render_feature_capability_table,
    render_feature_layer_table,
)
from prototype.parser.nomi.frontend import (
    DEFAULT_FRONTEND,
    get_parser_frontend,
    render_parser_frontend_table,
)


_NOMI_PARSER = "prototype.parser.nomi.usage.generate_ast"


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
    parser_frontend: str = DEFAULT_FRONTEND,
    eval_backend: str | None = None,
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

    pipeline = build_pipeline_spec(
        mode=mode,
        profile=profile,
        parser_frontend=parser_frontend,
        eval_backend=eval_backend,
    )
    collector = event_collector or RuntimeEventCollector(
        diagnostics=list(diagnostics),
        events=list(events),
    )

    if pipeline.eval_backend != "python-ast":
        session = create_session(
            mode=mode,
            profile=profile,
            parser_frontend=parser_frontend,
            eval_backend=pipeline.eval_backend,
        )
        return session.run(
            source=source,
            filename=filename,
            tree=tree,
            raise_on_error=raise_on_error,
            capture_output=capture_output,
            event_collector=collector,
        )

    runner = pipeline.mode_spec.load_runner()
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
            frontend_tree = _parse_with_frontend(
                pipeline=pipeline,
                source=source,
                filename=filename,
                tree=tree,
            )
            if tree is None and frontend_tree is not None:
                tree = frontend_tree
                source = None
                filename = None
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
    parser_frontend: str = DEFAULT_FRONTEND,
    eval_backend: str | None = None,
    stage: str = "python_ast",
) -> InspectionResult:
    """Inspect one read-only pipeline artifact for the selected mode."""

    pipeline = build_pipeline_spec(
        mode=mode,
        profile=profile,
        parser_frontend=parser_frontend,
        eval_backend=eval_backend,
    )
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

    if stage in {"capabilities", "capability_matrix"}:
        output = render_feature_capability_table()
        timings = {"total": perf_counter() - started}
        return InspectionResult(
            mode=mode,
            profile=profile,
            pipeline=pipeline,
            stage=stage,
            output=output,
            timings=timings,
        )

    if stage in {"parser_frontends", "parser-frontends", "frontends"}:
        output = render_parser_frontend_table()
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

        desugar_profile = DEFAULT_DESUGAR_PROFILE if mode == "nomi" else None
        output = render_desugar_pass_table(profile=desugar_profile)
        timings = {"total": perf_counter() - started}
        return InspectionResult(
            mode=mode,
            profile=profile,
            pipeline=pipeline,
            stage=stage,
            output=output,
            timings=timings,
        )

    if stage in {"eval_backends", "eval-backends"}:
        from prototype.runtime.backends import render_eval_backend_table

        output = render_eval_backend_table()
        timings = {"total": perf_counter() - started}
        return InspectionResult(
            mode=mode,
            profile=profile,
            pipeline=pipeline,
            stage=stage,
            output=output,
            timings=timings,
        )

    if stage in {"host_capabilities", "host-capabilities"}:
        from prototype.runtime.host_capabilities import render_host_capability_table

        output = render_host_capability_table()
        timings = {"total": perf_counter() - started}
        return InspectionResult(
            mode=mode,
            profile=profile,
            pipeline=pipeline,
            stage=stage,
            output=output,
            timings=timings,
        )

    if stage in {"resolved_pipelines", "resolved-pipelines", "pipelines"}:
        from prototype.runtime.pipeline import render_resolved_pipeline_table

        output = render_resolved_pipeline_table()
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

        tree = _parse_or_load_default(pipeline=pipeline, source=source, filename=filename)
        desugar_profile = DEFAULT_DESUGAR_PROFILE if mode == "nomi" else None
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
        tree = _parse_or_load_default(pipeline=pipeline, source=source, filename=filename)
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

    if stage in {"core_json", "core-json"}:
        session = create_session(
            mode=mode,
            profile=profile,
            parser_frontend=parser_frontend,
            eval_backend=eval_backend,
        )
        output = session.core_json(source=source, filename=filename)
        timings = {"total": perf_counter() - started}
        return InspectionResult(
            mode=mode,
            profile=profile,
            pipeline=pipeline,
            stage=stage,
            output=output,
            timings=timings,
        )

    if stage in {"core_verify", "core-verify"}:
        tree = _parse_or_load_default(pipeline=pipeline, source=source, filename=filename)
        core = lower_python_ast_to_core(tree)
        try:
            verify_core(core, strict=True)
            output = f"Core IR verification: PASS\n{dump_core(core)}"
        except Exception as exc:
            output = f"Core IR verification: FAIL\n{exc}"
        timings = {"total": perf_counter() - started}
        return InspectionResult(
            mode=mode,
            profile=profile,
            pipeline=pipeline,
            stage=stage,
            output=output,
            timings=timings,
        )

    if stage in {"core_to_python", "core-to-python"}:
        tree = _parse_or_load_default(pipeline=pipeline, source=source, filename=filename)
        core = lower_python_ast_to_core(tree)
        py_tree = core_to_python_ast(core)
        output = ast.dump(py_tree, include_attributes=False, indent=2)
        timings = {"total": perf_counter() - started}
        return InspectionResult(
            mode=mode,
            profile=profile,
            pipeline=pipeline,
            stage=stage,
            output=output,
            timings=timings,
        )

    if stage in {"backend_lowered", "backend-lowered"}:
        from prototype.runtime.backends.python_ast import make_python_ast_backend_for_mode

        tree = _parse_or_load_default(pipeline=pipeline, source=source, filename=filename)
        core = lower_python_ast_to_core(tree)
        backend = make_python_ast_backend_for_mode(pipeline.mode_spec)
        output = backend.render_lowered(core)
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

    tree = _parse_with_frontend(
        pipeline=pipeline,
        source=source,
        filename=filename,
        tree=None,
    )
    if tree is None:
        parser = pipeline.mode_spec.load_parser()
        output = parser(filename=filename, code=source, dump=True)
    else:
        output = ast.dump(tree, include_attributes=False, indent=2)
    timings = {"total": perf_counter() - started}
    return InspectionResult(
        mode=mode,
        profile=profile,
        pipeline=pipeline,
        stage=stage,
        output=output,
        timings=timings,
    )


def _parse_or_load_default(
    *,
    pipeline: PipelineSpec,
    source: str | None,
    filename: str | Path | None,
) -> Any:
    tree = _parse_with_frontend(
        pipeline=pipeline,
        source=source,
        filename=filename,
        tree=None,
    )
    if tree is not None:
        return tree
    parser = pipeline.mode_spec.load_parser()
    return parser(filename=filename, code=source)


def _parse_with_frontend(
    *,
    pipeline: PipelineSpec,
    source: str | None,
    filename: str | Path | None,
    tree: Any | None,
) -> Any | None:
    """Return a selected frontend AST, or run it as a parse-only gate."""
    if tree is not None or pipeline.parser_frontend == DEFAULT_FRONTEND:
        return None
    if pipeline.parser != _NOMI_PARSER:
        raise ValueError(
            "parser_frontend selection is currently supported only for "
            "Nomi parser modes"
        )
    frontend = get_parser_frontend(pipeline.parser_frontend)
    capabilities = getattr(getattr(frontend, "spec", None), "capabilities", None)
    if getattr(capabilities, "lower_to_python_ast", False):
        return frontend.generate_python_ast(code=source, filename=filename)
    frontend.parse_accepts(code=source, filename=filename)
    return None


def create_session(
    *,
    mode: str = "nomi",
    profile: str = "default",
    parser_frontend: str = DEFAULT_FRONTEND,
    eval_backend: str | None = None,
    cache_size: int = 0,
):
    """Create a persistent runtime session for cells, notebooks, and REPLs."""

    # Local import avoids a module cycle: RuntimeSession returns ExecutionResult.
    from prototype.runtime.session import RuntimeSession

    return RuntimeSession(
        mode=mode,
        profile=profile,
        parser_frontend=parser_frontend,
        eval_backend=eval_backend,
        cache_size=cache_size,
    )
