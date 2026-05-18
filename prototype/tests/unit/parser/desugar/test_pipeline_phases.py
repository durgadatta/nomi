import ast

from prototype.parser.nomi.desugar.base import BaseDesugarer, Phase
from prototype.parser.nomi.desugar.pipeline import (
    DESUGAR_PASSES,
    NOMI_INTERPRETER_DESUGAR_PASSES,
    _order_passes_by_phase,
)


class _CleanupPass(BaseDesugarer):
    phase = Phase.cleanup


class _SemanticPass(BaseDesugarer):
    phase = Phase.semantic


class _SyntaxPass(BaseDesugarer):
    phase = Phase.syntax


class _ReplaceBreakInWhereBody(BaseDesugarer):
    phase = Phase.syntax

    def visit_Break(self, node):
        return ast.Pass()


def test_pipeline_orders_passes_by_phase_without_losing_manifest_order_inside_phase():
    ordered = _order_passes_by_phase([
        _SemanticPass,
        _CleanupPass,
        _SyntaxPass,
    ])

    assert ordered == (_SyntaxPass, _SemanticPass, _CleanupPass)


def test_active_pipelines_run_syntax_before_semantic_before_cleanup():
    for passes in (DESUGAR_PASSES, NOMI_INTERPRETER_DESUGAR_PASSES):
        phases = [pass_cls.phase for pass_cls in passes]
        phase_indexes = [list(Phase).index(phase) for phase in phases]
        assert phase_indexes == sorted(phase_indexes)


def test_base_desugarer_visits_where_body_custom_attribute():
    tree = ast.Module(
        body=[
            ast.Assign(
                targets=[ast.Name(id="result", ctx=ast.Store())],
                value=ast.Name(id="x", ctx=ast.Load()),
            )
        ],
        type_ignores=[],
    )
    tree.body[0]._nomi_where_body = [ast.Break()]

    transformed = _ReplaceBreakInWhereBody().visit(tree)

    assert isinstance(transformed.body[0]._nomi_where_body[0], ast.Pass)
