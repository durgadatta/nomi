"""Pipeline metadata for the public runtime facade."""

from __future__ import annotations

import os
from dataclasses import dataclass

from prototype.parser.nomi.frontend import DEFAULT_FRONTEND, get_parser_frontend
from prototype.runtime.backends import get_eval_backend
from prototype.runtime.modes import ModeSpec, get_mode_spec


@dataclass(frozen=True)
class PipelineSpec:
    """Resolved execution/inspection pipeline metadata."""

    mode: str
    profile: str
    mode_spec: ModeSpec
    parser_frontend: str = DEFAULT_FRONTEND
    eval_backend: str = "python-ast"
    # TODO(NOMI-ARCH-021): Split host from backend target once Python AST,
    # Core IR, MLIR/LLVM, and Wasm become selectable execution artifacts.
    host: str = "python"

    @property
    def parser(self) -> str:
        return self.mode_spec.parser

    @property
    def lowering(self) -> str:
        return self.mode_spec.lowering

    @property
    def interpreter(self) -> str:
        return self.mode_spec.interpreter


@dataclass(frozen=True)
class ResolvedPipeline:
    """Named pipeline answer for user-facing hosts and contract tests."""

    name: str
    host: str
    parser_frontend: str
    lowerer: str
    eval_backend: str
    default: bool = False
    notes: str = ""


RESOLVED_PIPELINES: tuple[ResolvedPipeline, ...] = (
    ResolvedPipeline(
        name="python-session-default",
        host="python",
        parser_frontend=DEFAULT_FRONTEND,
        lowerer="mode session lowerer",
        eval_backend="python-ast",
        default=True,
        notes="CLI, notebook, tests, and runtime facade default",
    ),
    ResolvedPipeline(
        name="browser-playground-default",
        host="browser",
        parser_frontend="rust-fast-ast-wasm",
        lowerer="prototype/runtime/js/lower_to_core_ir.js",
        eval_backend="js-core-runtime",
        default=True,
        notes="web playground worker path",
    ),
    ResolvedPipeline(
        name="node-core-test",
        host="node",
        parser_frontend="lark-lalr",
        lowerer="Python session Core IR JSON",
        eval_backend="js-core-runtime",
        notes="Node wrapper parity tests",
    ),
)


def render_resolved_pipeline_table() -> str:
    rows = [
        "| pipeline | host | parser frontend | lowerer | eval backend | default | notes |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for pipeline in RESOLVED_PIPELINES:
        rows.append(
            "| {name} | {host} | {parser} | {lowerer} | {backend} | {default} | {notes} |".format(
                name=pipeline.name,
                host=pipeline.host,
                parser=pipeline.parser_frontend,
                lowerer=pipeline.lowerer,
                backend=pipeline.eval_backend,
                default="yes" if pipeline.default else "no",
                notes=pipeline.notes,
            )
        )
    return "\n".join(rows)


def build_pipeline_spec(
    *,
    mode: str = "nomi",
    profile: str = "default",
    parser_frontend: str = DEFAULT_FRONTEND,
    eval_backend: str | None = None,
    host: str = "python",
) -> PipelineSpec:
    if profile != "default":
        # TODO(NOMI-ARCH-002): Route named feature profiles through mode
        # metadata once the parser supports feature-selected pipelines.
        raise ValueError(f"Unsupported runtime profile: {profile!r}")
    get_parser_frontend(parser_frontend)
    mode_spec = get_mode_spec(mode)
    resolved_backend = (
        eval_backend
        if eval_backend is not None
        else os.environ.get("NOMI_EVAL_BACKEND", mode_spec.eval_backend)
    )
    get_eval_backend(resolved_backend)

    return PipelineSpec(
        mode=mode,
        profile=profile,
        mode_spec=mode_spec,
        parser_frontend=parser_frontend,
        eval_backend=resolved_backend,
        host=host,
    )
