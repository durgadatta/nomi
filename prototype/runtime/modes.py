"""Runtime mode registry.

The current implementation still runs through the existing interpreter
``usage.py`` modules.  This registry makes those choices visible as data so the
next architecture slices can add feature profiles and pipeline metadata without
changing every caller again.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from prototype.utils import resolve_dotted


@dataclass(frozen=True)
class ModeSpec:
    name: str
    runner_module: str
    status: str
    parser: str
    lowering: str
    interpreter: str
    session_lowerer: str | None = None
    eval_backend: str = "python-ast"

    def load_runner(self) -> Callable:
        return resolve_dotted(f"{self.runner_module}.run_eval_loop")

    def load_parser(self) -> Callable:
        return resolve_dotted(self.parser)

    def load_interpreter_class(self) -> Callable:
        return resolve_dotted(self.interpreter)

    def load_session_lowerer(self) -> Callable | None:
        if self.session_lowerer is None:
            return None
        return resolve_dotted(self.session_lowerer)


MODE_SPECS: dict[str, ModeSpec] = {
    "python": ModeSpec(
        name="python",
        runner_module="prototype.interpreter.python.usage",
        status="parity-reference",
        parser="prototype.parser.python.utils.generate_ast",
        lowering="python-ast-direct",
        interpreter="prototype.interpreter.python.interpreter.Interpreter",
    ),
    "nomi": ModeSpec(
        name="nomi",
        runner_module="prototype.interpreter.nomi.usage",
        status="current-default",
        parser="prototype.parser.nomi.usage.generate_ast",
        lowering="prototype.parser.nomi.desugar.pipeline.desugar_module_for_nomi_interpreter",
        interpreter="prototype.interpreter.nomi.interpreter.Interpreter",
        session_lowerer="prototype.parser.nomi.desugar.pipeline.desugar_module_for_nomi_interpreter",
    ),
    "reduced": ModeSpec(
        name="reduced",
        runner_module="prototype.interpreter.reduced.usage",
        status="normal-form-checking",
        parser="prototype.parser.nomi.usage.generate_ast",
        lowering="prototype.parser.nomi.desugar.pipeline.desugar_module",
        interpreter="prototype.interpreter.reduced.interpreter.Interpreter",
        session_lowerer="prototype.parser.nomi.desugar.pipeline.desugar_module",
    ),
}

INTERPRETER_MODES = tuple(MODE_SPECS)


def get_mode_spec(mode: str) -> ModeSpec:
    try:
        return MODE_SPECS[mode]
    except KeyError as exc:
        raise ValueError(
            f"Unknown interpreter mode: {mode!r}. "
            f"Valid modes: {INTERPRETER_MODES}"
        ) from exc


def get_runner(mode: str) -> Callable:
    return get_mode_spec(mode).load_runner()
