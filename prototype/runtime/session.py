"""Persistent runtime session facade.

This is a small wrapper around today's parser/lowering/interpreter pieces.  It
does not replace web or notebook execution yet; it gives them a shared target
for a later migration.
"""

from __future__ import annotations

import ast
import copy
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
    cache_size: int = 0
    pipeline: PipelineSpec = field(init=False)
    interpreter: Any = field(init=False)
    _ast_cache: dict[str, Any] = field(default_factory=dict, init=False)

    def __post_init__(self) -> None:
        self.pipeline = build_pipeline_spec(mode=self.mode, profile=self.profile)
        self.reset()

    @property
    def bindings(self) -> dict[str, Any]:
        return self.interpreter.global_env.bindings

    def reset(self, *, clear_cache: bool = False) -> None:
        interpreter_cls = self.pipeline.mode_spec.load_interpreter_class()
        self.interpreter = interpreter_cls()
        if clear_cache:
            self._ast_cache.clear()

    def run(
        self,
        *,
        source: str | None = None,
        filename: str | Path | None = None,
        tree: Any | None = None,
        raise_on_error: bool = True,
        display_last_expr: bool = False,
    ) -> ExecutionResult:
        started = perf_counter()
        timings: dict[str, float] = {}
        try:
            if tree is None:
                cached_tree = self._get_cached_tree(source)
                if cached_tree is not None:
                    cache_started = perf_counter()
                    tree = copy.deepcopy(cached_tree)
                    timings["cache"] = perf_counter() - cache_started
                else:
                    tree = self._parse_and_lower(
                        source=source,
                        filename=filename,
                        timings=timings,
                    )
                    self._cache_tree(source, tree)

            tree = ast.fix_missing_locations(tree)
            eval_started = perf_counter()
            has_value, value = self._eval_tree(
                tree,
                display_last_expr=display_last_expr,
            )
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
            value=value,
            has_value=has_value,
        )

    def _eval_tree(self, tree: Any, *, display_last_expr: bool) -> tuple[bool, Any]:
        if not display_last_expr or not isinstance(tree, ast.Module):
            return False, self.interpreter.eval(tree)

        body = list(tree.body)
        if len(body) <= 1:
            return False, self.interpreter.eval(tree)

        last = body[-1]
        if not isinstance(last, ast.Expr) or self._is_block_call_expr(last):
            return False, self.interpreter.eval(tree)

        leading = ast.Module(body=body[:-1], type_ignores=[])
        leading = ast.fix_missing_locations(leading)
        self.interpreter.eval(leading)
        return True, self.interpreter.eval(last)

    def _parse_and_lower(
        self,
        *,
        source: str | None,
        filename: str | Path | None,
        timings: dict[str, float],
    ) -> Any:
        parse_started = perf_counter()
        parser = self.pipeline.mode_spec.load_parser()
        tree = parser(filename=filename, code=source, dump=False)
        timings["parse"] = perf_counter() - parse_started

        lowerer = self.pipeline.mode_spec.load_session_lowerer()
        if lowerer is not None:
            lower_started = perf_counter()
            tree = lowerer(tree)
            timings["lower"] = perf_counter() - lower_started
        return tree

    def _get_cached_tree(self, source: str | None) -> Any | None:
        if self.cache_size <= 0 or source is None:
            return None
        return self._ast_cache.get(source)

    def _cache_tree(self, source: str | None, tree: Any) -> None:
        if self.cache_size <= 0 or source is None:
            return
        if source in self._ast_cache:
            self._ast_cache[source] = copy.deepcopy(tree)
            return
        if len(self._ast_cache) >= self.cache_size:
            oldest = next(iter(self._ast_cache))
            del self._ast_cache[oldest]
        self._ast_cache[source] = copy.deepcopy(tree)

    @staticmethod
    def _is_block_call_expr(node: ast.Expr) -> bool:
        value = node.value
        return (
            isinstance(value, ast.Call)
            and any(keyword.arg == "__block__" for keyword in value.keywords)
        )
