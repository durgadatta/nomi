"""Pipeline metadata for the public runtime facade."""

from __future__ import annotations

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
    resolved_backend = eval_backend if eval_backend is not None else mode_spec.eval_backend
    get_eval_backend(resolved_backend)

    return PipelineSpec(
        mode=mode,
        profile=profile,
        mode_spec=mode_spec,
        parser_frontend=parser_frontend,
        eval_backend=resolved_backend,
        host=host,
    )
