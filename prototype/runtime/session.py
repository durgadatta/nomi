"""Persistent runtime session facade.

This is a small wrapper around today's parser/lowering/interpreter pieces.  It
does not replace web or notebook execution yet; it gives them a shared target
for a later migration.
"""

from __future__ import annotations

import ast
from dataclasses import dataclass, field
from pathlib import Path
from time import perf_counter
from typing import Any

from prototype.runtime.api import ExecutionResult
from prototype.runtime.pipeline import PipelineSpec, build_pipeline_spec


@dataclass
class RuntimeSession:
    mode: str = "nomi"
    profile: str = "default"
    pipeline: PipelineSpec = field(init=False)
    interpreter: Any = field(init=False)

    def __post_init__(self) -> None:
        self.pipeline = build_pipeline_spec(mode=self.mode, profile=self.profile)
        self.reset()

    @property
    def bindings(self) -> dict[str, Any]:
        return self.interpreter.global_env.bindings

    def reset(self) -> None:
        interpreter_cls = self.pipeline.mode_spec.load_interpreter_class()
        self.interpreter = interpreter_cls()

    def run(
        self,
        *,
        source: str | None = None,
        filename: str | Path | None = None,
        tree: Any | None = None,
        raise_on_error: bool = True,
    ) -> ExecutionResult:
        started = perf_counter()
        timings: dict[str, float] = {}
        try:
            if tree is None:
                parse_started = perf_counter()
                parser = self.pipeline.mode_spec.load_parser()
                tree = parser(filename=filename, code=source, dump=False)
                timings["parse"] = perf_counter() - parse_started

                lowerer = self.pipeline.mode_spec.load_session_lowerer()
                if lowerer is not None:
                    lower_started = perf_counter()
                    tree = lowerer(tree)
                    timings["lower"] = perf_counter() - lower_started

            tree = ast.fix_missing_locations(tree)
            eval_started = perf_counter()
            self.interpreter.eval(tree)
            timings["eval"] = perf_counter() - eval_started
        except Exception as exc:
            timings["total"] = perf_counter() - started
            if raise_on_error:
                raise
            return ExecutionResult(
                mode=self.mode,
                profile=self.profile,
                pipeline=self.pipeline,
                bindings={},
                exception=exc,
                timings=timings,
            )

        timings["total"] = perf_counter() - started
        return ExecutionResult(
            mode=self.mode,
            profile=self.profile,
            pipeline=self.pipeline,
            bindings=self.bindings,
            timings=timings,
        )
