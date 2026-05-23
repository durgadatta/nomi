"""Tests for Python match-pattern projection into Core IR."""

import ast as py_ast

from prototype.syntax.core import (
    Load,
    MappingLiteral,
    Match,
    Module,
    PatternTest,
    Sequence,
    Spread,
    core_to_python_ast,
    lower_python_ast_to_core,
    verify_core,
)


def test_lower_python_ast_to_core_value_and_capture_patterns():
    core = lower_python_ast_to_core(
        py_ast.parse("match x:\n case 1: y = 'one'\n case name: y = name")
    )
    match = core.body[0]

    assert isinstance(match, Match)
    assert len(match.cases) == 2
    assert isinstance(match.cases[0], PatternTest)
    assert match.cases[0].guard is None
    assert isinstance(match.cases[1].pattern, Load)
    assert match.cases[1].pattern.name == "name"


def test_lower_python_ast_to_core_sequence_and_mapping_patterns():
    seq = lower_python_ast_to_core(
        py_ast.parse("match x:\n case [head, tail]: y = head")
    ).body[0]
    mapping = lower_python_ast_to_core(
        py_ast.parse("match x:\n case {'theme': t}: y = t")
    ).body[0]

    assert isinstance(seq.cases[0].pattern, Sequence)
    assert isinstance(mapping.cases[0].pattern, MappingLiteral)


def test_lower_python_ast_to_core_star_pattern():
    core = lower_python_ast_to_core(
        py_ast.parse("match x:\n case [head, *rest]: y = rest")
    )
    pattern = core.body[0].cases[0].pattern

    assert isinstance(pattern, Sequence)
    assert isinstance(pattern.elements[1], Spread)


def test_core_patterns_verify_and_roundtrip_to_python_ast():
    core = lower_python_ast_to_core(
        py_ast.parse("match x:\n case {'theme': t}: y = t\n case _: y = None")
    )

    verify_core(core, strict=True)

    tree = core_to_python_ast(core)
    dumped = py_ast.dump(tree, include_attributes=False, indent=2)
    assert "MatchMapping" in dumped
    assert "MatchAs" in dumped
