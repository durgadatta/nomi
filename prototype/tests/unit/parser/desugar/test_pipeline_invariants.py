import ast
import pytest

from prototype.parser.nomi.desugar.pipeline import _find_forbidden_nodes, _check_pass_invariants
from prototype.parser.nomi.desugar.base import BaseDesugarer, Phase


class _PassThatRemovesBreak(BaseDesugarer):
    phase = Phase.syntax
    removed_node_types = (ast.Break,)

    def visit_Break(self, node):
        return ast.Pass()


class _PassThatLies(BaseDesugarer):
    """Claims to remove Break but doesn't actually."""
    phase = Phase.syntax
    removed_node_types = (ast.Break,)


def test_find_forbidden_nodes_finds_survivors():
    tree = ast.Module(body=[
        ast.For(target=ast.Name(id='x', ctx=ast.Store()),
                iter=ast.Name(id='xs', ctx=ast.Load()),
                body=[ast.Break()],
                orelse=[]),
    ], type_ignores=[])
    survivors = list(_find_forbidden_nodes(tree, {ast.Break}))
    assert len(survivors) == 1
    assert isinstance(survivors[0], ast.Break)


def test_find_forbidden_nodes_empty_when_none():
    tree = ast.Module(body=[ast.Pass()], type_ignores=[])
    survivors = list(_find_forbidden_nodes(tree, {ast.Break}))
    assert survivors == []


def test_pass_invariants_raises_on_liar_pass():
    tree = ast.Module(body=[ast.Break()], type_ignores=[])
    with pytest.raises(AssertionError, match="Desugar invariant violation"):
        _check_pass_invariants(tree, _PassThatLies, "PassThatLies")


def test_pass_invariants_passes_on_honest_pass():
    tree = ast.Module(body=[ast.Break()], type_ignores=[])
    honest = _PassThatRemovesBreak()
    honest_tree = honest.visit(tree)
    _check_pass_invariants(honest_tree, _PassThatRemovesBreak, "PassThatRemovesBreak")


def test_pass_invariants_skips_when_no_removed_types():
    tree = ast.Module(body=[ast.Break()], type_ignores=[])
    _check_pass_invariants(tree, BaseDesugarer, "BaseDesugarer")
