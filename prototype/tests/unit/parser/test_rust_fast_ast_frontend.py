from pathlib import Path

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

RUST_FAST_AST_EXTRA_ACCEPTED_FIXTURES = (
    "PLAY/debug/blocks.nomi",
    "PLAY/debug/fix.nomi",
    "PLAY/debug/functions.nomi",
    "prototype/tests/data/sample_sources/interpreter/blocks.nomi",
    "prototype/tests/data/sample_sources/interpreter/func_styles.nomi",
    "prototype/tests/data/sample_sources/interpreter/functions.nomi",
    "prototype/tests/data/sample_sources/interpreter/sample.nomi",
    "scripts/demo.nomi",
)


def _python_ast_text(frontend, code):
    try:
        return frontend.python_ast_text(code=code)
    except RuntimeError as exc:
        if "cargo is required" in str(exc):
            pytest.skip(str(exc))
        raise


def _rust_payload(frontend, filename):
    try:
        return frontend.parse_raw_tree(filename=filename)
    except RuntimeError as exc:
        if "cargo is required" in str(exc):
            pytest.skip(str(exc))
        raise


def _walk_statements(statements):
    for statement in statements:
        yield statement
        body = statement.get("body", ())
        if isinstance(body, list):
            yield from _walk_statements(body)
        for clause in statement.get("clauses", ()):
            yield from _walk_statements(clause.get("body", ()))


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

    assert rust.spec.status == "parse-acceptance"
    assert rust.spec.capabilities.parse_current_grammar is True
    assert rust.spec.capabilities.lower_to_python_ast is False
    assert rust.spec.capabilities.selectable_for_execution is False


def test_rust_fast_ast_accepts_demo_nomi_payload():
    rust = get_parser_frontend("rust-fast-ast")
    repo_root = Path(__file__).resolve().parents[4]

    payload = _rust_payload(rust, repo_root / "scripts" / "demo.nomi")
    statements = tuple(_walk_statements(payload["body"]))

    assert payload["type"] == "Module"
    assert len(payload["body"]) >= 30
    assert any(
        statement.get("kind") == "Func" and statement.get("head") == "greet(name)"
        for statement in statements
    )
    assert any(statement.get("kind") == "Try" for statement in statements)
    assert any(
        statement.get("kind") == "BlockCall" and "-> item" in statement.get("head", "")
        for statement in statements
    )
    assert any(
        statement.get("type") == "Assign"
        and statement.get("target") == "age : int , is_positive"
        for statement in statements
    )


def test_rust_fast_ast_accepts_guided_tour_demo_payload():
    rust = get_parser_frontend("rust-fast-ast")
    repo_root = Path(__file__).resolve().parents[4]

    payload = _rust_payload(rust, repo_root / "samples" / "demo.nomi")
    statements = tuple(_walk_statements(payload["body"]))

    assert payload["type"] == "Module"
    assert len(payload["body"]) >= 80
    assert any(statement.get("kind") == "WhereAssign" for statement in statements)
    assert any(
        statement.get("kind") == "Data" and statement.get("head") == "Point"
        for statement in statements
    )
    assert any(statement.get("kind") == "Match" for statement in statements)
    assert any(statement.get("kind") == "Unless" for statement in statements)
    assert any(
        statement.get("type") == "Assign" and statement.get("target") == "data"
        for statement in statements
    )


def test_rust_fast_ast_accepts_relative_source_path(monkeypatch):
    rust = get_parser_frontend("rust-fast-ast")
    repo_root = Path(__file__).resolve().parents[4]
    monkeypatch.chdir(repo_root)

    payload = _rust_payload(rust, Path("samples/demo.nomi"))

    assert payload["type"] == "Module"
    assert len(payload["body"]) >= 80


@pytest.mark.parametrize(
    "relative_path",
    RUST_FAST_AST_EXTRA_ACCEPTED_FIXTURES,
    ids=RUST_FAST_AST_EXTRA_ACCEPTED_FIXTURES,
)
def test_rust_fast_ast_accepts_lark_accepted_extra_fixtures(relative_path):
    rust = get_parser_frontend("rust-fast-ast")
    repo_root = Path(__file__).resolve().parents[4]

    payload = _rust_payload(rust, repo_root / relative_path)

    assert payload["type"] == "Module"
