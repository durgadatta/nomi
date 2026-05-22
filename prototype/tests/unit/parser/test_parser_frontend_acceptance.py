from pathlib import Path

import pytest

from prototype.parser.nomi.frontend import (
    get_parse_acceptance_frontends,
    get_parser_frontend,
    get_python_ast_frontends,
)


REPO_ROOT = Path(__file__).resolve().parents[4]

PARSER_SAMPLE_FILES = (
    REPO_ROOT / "samples" / "block.nomi",
    REPO_ROOT / "samples" / "collections.nomi",
    REPO_ROOT / "samples" / "constraint.nomi",
    REPO_ROOT / "samples" / "demo.nomi",
    REPO_ROOT / "samples" / "demo_terse.nomi",
    REPO_ROOT / "samples" / "demo_verbose.nomi",
    REPO_ROOT / "samples" / "notebook_intro.nomi.nb",
    REPO_ROOT / "samples" / "others.nomi",
)

PARSER_SNIPPETS = {
    "func-def": "func add(a, b=2):\n    return a + b\n",
    "arrow-func": "inc = (x) => x + 1\n",
    "constraint": 'age: int, age >= 13 else "Too young" = 12\n',
    "block-call": "retry(3):\n    value = 1\n",
    "match-stmt": (
        "match value:\n"
        "    case 1:\n"
        "        result = 'one'\n"
        "    case _:\n"
        "        result = 'any'\n"
    ),
    "inline-match": "result = match value: case 1 => 'one'; case _ => 'many'\n",
    "while-let": "while [head, *tail] = items:\n    items = tail\n",
    "guard-let": "guard [head, *tail] = items:\n    return None\n",
    "where": "result = x + y where:\n    x = 10\n    y = 20\n",
    "operator-section": "f = (+2)\n",
    "safe-navigation": 'first_char = data?.get("name")?.[0]\n',
    "range-pipeline": "squares_sum = 1..5 |> list |> sum\n",
    "data-decl": "data Point:\n    x: float\n    y: float\n",
}


def _acceptance_frontend_params():
    return [
        pytest.param(frontend, id=frontend.spec.name)
        for frontend in get_parse_acceptance_frontends()
    ]


def _python_ast_frontend_params():
    return [
        pytest.param(frontend, id=frontend.spec.name)
        for frontend in get_python_ast_frontends()
    ]


def _parse_accepts(frontend, *, code=None, filename=None):
    try:
        frontend.parse_accepts(code=code, filename=filename)
    except RuntimeError as exc:
        if frontend.spec.name == "tree-sitter-cst" and "tree-sitter CLI" in str(exc):
            pytest.skip(str(exc))
        raise


@pytest.mark.parametrize("frontend", _acceptance_frontend_params())
@pytest.mark.parametrize("path", PARSER_SAMPLE_FILES, ids=lambda path: path.name)
def test_parser_frontends_accept_sample_files(frontend, path):
    _parse_accepts(frontend, filename=path)


@pytest.mark.parametrize("frontend", _acceptance_frontend_params())
@pytest.mark.parametrize("name", tuple(PARSER_SNIPPETS), ids=tuple(PARSER_SNIPPETS))
def test_parser_frontends_accept_feature_snippets(frontend, name):
    _parse_accepts(frontend, code=PARSER_SNIPPETS[name])


@pytest.mark.parametrize("frontend", _python_ast_frontend_params())
@pytest.mark.parametrize("path", PARSER_SAMPLE_FILES, ids=lambda path: path.name)
def test_python_ast_frontends_match_lark_for_sample_files(frontend, path):
    lark = get_parser_frontend("lark-lalr")

    assert frontend.python_ast_text(filename=path) == lark.python_ast_text(filename=path)


@pytest.mark.parametrize("frontend", _python_ast_frontend_params())
@pytest.mark.parametrize("name", tuple(PARSER_SNIPPETS), ids=tuple(PARSER_SNIPPETS))
def test_python_ast_frontends_match_lark_for_feature_snippets(frontend, name):
    lark = get_parser_frontend("lark-lalr")
    code = PARSER_SNIPPETS[name]

    assert frontend.python_ast_text(code=code) == lark.python_ast_text(code=code)
