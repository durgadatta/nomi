import pytest

from prototype.parser.nomi.frontend import get_parser_frontend


RUST_FAST_AST_SNIPPETS = {
    "assignment": "x = 1\n",
    "expression-call": 'print("x")\n',
    "precedence": "x = 1 + 2 * 3\n",
    "parenthesized-precedence": "x = (1 + 2) * 3\n",
    "function-equation": "add(a, b) = a + b\n",
    "arrow-assignment": "double = x => x * 2\n",
    "parenthesized-arrow-assignment": "add = (a, b) => a + b\n",
}


def _python_ast_text(frontend, code):
    try:
        return frontend.python_ast_text(code=code)
    except RuntimeError as exc:
        if "cargo is required" in str(exc):
            pytest.skip(str(exc))
        raise


@pytest.mark.parametrize(
    "name",
    tuple(RUST_FAST_AST_SNIPPETS),
    ids=tuple(RUST_FAST_AST_SNIPPETS),
)
def test_rust_fast_ast_first_slice_matches_lark_exactly(name):
    rust = get_parser_frontend("rust-fast-ast")
    lark = get_parser_frontend("lark-lalr")
    code = RUST_FAST_AST_SNIPPETS[name]

    assert _python_ast_text(rust, code) == lark.python_ast_text(code=code)


def test_rust_fast_ast_is_not_enrolled_as_full_replacement_yet():
    rust = get_parser_frontend("rust-fast-ast")

    assert rust.spec.status == "ast-slice"
    assert rust.spec.capabilities.parse_current_grammar is False
    assert rust.spec.capabilities.lower_to_python_ast is False
    assert rust.spec.capabilities.selectable_for_execution is False
