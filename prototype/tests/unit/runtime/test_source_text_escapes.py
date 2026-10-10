"""Current prototype literal values must not change across execution routes."""

import pytest

from prototype.runtime import execute
from prototype.tests.unit.runtime.test_text_strip_compatibility import ROUTES, run_source

VECTORS = [
    (r'"\x41\u00e9\U0001f600"', "Aé😀"),
    (r'"\a\b\f\v\n\r\t"', "\a\b\f\v\n\r\t"),
    (r'"\101\0"', "A\0"),
    (r'"\q\z"', "\\q\\z"),
    (r'r"\x41\n"', "\\x41\\n"),
    (r'r"a\"b"', 'a\\"b'),
    ('"""line\\\ncontinued"""', "linecontinued"),
    (r'"\\\"\'"', '\\"\''),
]


@pytest.mark.parametrize("route", ROUTES)
@pytest.mark.parametrize("literal,expected", VECTORS)
def test_literal_value_agrees_on_the_declared_prototype_routes(route, literal, expected):
    assert run_source(f"print('[' + {literal} + ']')\n", route) == "[" + expected + "]\n"


@pytest.mark.parametrize("literal,expected", VECTORS)
def test_rust_frontend_keeps_hosted_literal_value(literal, expected):
    result = execute(source=f"print('[' + {literal} + ']')\n", parser_frontend="rust-fast-ast", capture_output=True)
    assert result.stdout == "[" + expected + "]\n"


@pytest.mark.parametrize("literal", [r'"\xG1"', r'"\x1"', r'"\u123"', r'"\uD800"', r'"\U00110000"', r'"\N{LATIN CAPITAL LETTER A}"'])
def test_browser_refuses_invalid_scalar_or_unimplemented_named_escape(literal):
    with pytest.raises(RuntimeError, match="escape"):
        run_source(f"print({literal})\n", "wasm-js")
