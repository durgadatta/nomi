"""Readable existing syntax must behave alike through Lark and Rust."""

import pytest

from prototype.runtime import execute


@pytest.mark.parametrize("source", [
    'items = [\n    {"x": 1},\n  {"x": 2}, # a comment\n]\nprint(items[1]["x"])\n',
    'func value():\n    items = [\n        (1 +\n             2),\n        4\n    ]\n    return sum(items)\nprint(value())\n',
    'func add(a, b):\n    return a + b\nprint(add(\n  2,\n  3\n))\n',
    'items = [\n    "[not a delimiter]",\n    "(also not)"\n]\nprint(len(items))\n',
    'func add(state, item):\n    return state + item\nprint([1, 2] |> fold(10, add))\n',
])
def test_multiline_collections_preserve_execution(source, nomi_parser_frontend):
    reference = execute(source=source, parser_frontend="lark-lalr")
    result = execute(source=source, parser_frontend=nomi_parser_frontend)
    assert result.stdout == reference.stdout


@pytest.mark.parametrize("source", ["x = [1, 2)\n", "x = (1 + 2\n"])
def test_invalid_delimiters_remain_non_executable(source, nomi_parser_frontend):
    result = execute(source=source, parser_frontend=nomi_parser_frontend, raise_on_error=False)
    assert not result.ok
    assert result.diagnostics
