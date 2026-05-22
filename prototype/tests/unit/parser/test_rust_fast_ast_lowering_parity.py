from pathlib import Path

import pytest

from prototype.parser.nomi.frontend import get_parser_frontend


REPO_ROOT = Path(__file__).resolve().parents[4]

RUST_FAST_AST_LOWERING_SNIPPETS = {
    "constant-none": "x = None\n",
    "constant-true": "x = True\n",
    "constant-false": "x = False\n",
    "unary-plus": "x = +y\n",
    "unary-minus": "x = -y\n",
    "unary-not": "x = not y\n",
    "floor-div": "x = 5 // 2\n",
    "mod": "x = 5 % 2\n",
    "matmul": "x = a @ b\n",
    "single-compare": "x = a < b\n",
    "chained-compare": "x = 0 <= score <= 100\n",
    "bool-and": "x = a and b\n",
    "bool-or-chain": "x = a or b or c\n",
    "conditional-expression": "x = 1 if ok else 2\n",
    "list": "x = [1, 2]\n",
    "tuple": "x = (1, 2)\n",
    "empty-tuple": "x = ()\n",
    "empty-dict": "x = {}\n",
    "dict": 'x = {"a": 1, "b": 2}\n',
    "attribute": "x = obj.name\n",
    "subscript": "x = items[0]\n",
    "augassign": "x += 1\n",
    "pass": "pass\n",
    "func-return": "func f():\n    return 1\n",
    "func-yield": "func f():\n    yield item\n",
    "raise": "raise ValueError(1)\n",
    "f-string": 'x = f"Hello, {name}!"\n',
    "annassign-constraint": "age:int, is_positive = 25\n",
    "annassign-constraint-message": 'age: int, age >= 13 else "Too young" = 12\n',
    "func-param-constraint-message": (
        'func signup(age: (int, age >= 13 else "Signup requires age 13+")):\n'
        "    return age\n"
    ),
    "type-alias": "type UserId = int\n",
    "for-suite": "for i in range(n):\n    yield i\n",
    "if-suite": "if attempts < 3:\n    raise ValueError(attempts)\n",
    "try-except-suite": (
        "try:\n"
        "    yield\n"
        "except Exception as e:\n"
        "    raise\n"
    ),
    "try-finally-suite": (
        "try:\n"
        "    yield\n"
        "finally:\n"
        '    print("done")\n'
    ),
    "block-call": "times(3):\n    counter += 1\n",
    "block-call-param": "each(items) -> item:\n    print(item)\n",
    "data-decl": "data Point:\n    x: float\n    y: float\n",
    "data-decl-constrained": (
        "data PositivePoint:\n"
        "    x: float where x > 0\n"
        "    y: float where y > 0\n"
    ),
    "match-stmt": (
        "match value:\n"
        "    case 1:\n"
        "        result = 'one'\n"
        "    case _:\n"
        "        result = 'any'\n"
    ),
    "match-assign-block": (
        "result = match score:\n"
        "    case 100: 'perfect'\n"
        "    case s if s >= 90: 'excellent'\n"
        "    case _: 'regular'\n"
    ),
    "inline-match": "label = match score: case 100 => 'perfect'; case _ => 'ok'\n",
    "if-let": 'if {"theme": t, "scale": s} = config:\n    print(t)\n',
    "guard-let": (
        "func first(sequence):\n"
        "    guard [head, *tail] = sequence:\n"
        "        return None\n"
        "    return head\n"
    ),
    "while-let": (
        "while [h, *rest] = items:\n"
        "    total = total + h\n"
        "    items = rest\n"
    ),
    "where": "result = x + y where:\n    x = 10\n    y = 20\n",
    "range-inclusive": "x = list(1..5)\n",
    "range-exclusive": "x = list(1..<5)\n",
    "range-step": "x = list(1..20 by 3)\n",
    "range-pipeline": "squares_sum = 1..5 |> list |> sum\n",
    "safe-navigation": 'first_char = data?.get("name")?.[0]\n',
    "nullish-safe-navigation": 'fallback = config?.get("scale") ?? 1.0\n',
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
    tuple(RUST_FAST_AST_LOWERING_SNIPPETS),
    ids=tuple(RUST_FAST_AST_LOWERING_SNIPPETS),
)
def test_rust_fast_ast_lowering_slice_matches_lark_exactly(name):
    rust = get_parser_frontend("rust-fast-ast")
    lark = get_parser_frontend("lark-lalr")
    code = RUST_FAST_AST_LOWERING_SNIPPETS[name]

    assert _python_ast_text(rust, code) == lark.python_ast_text(code=code)


def test_rust_fast_ast_lowers_core_demo_to_lark_python_ast_exactly():
    rust = get_parser_frontend("rust-fast-ast")
    lark = get_parser_frontend("lark-lalr")
    path = REPO_ROOT / "scripts" / "demo.nomi"

    assert rust.python_ast_text(filename=path) == lark.python_ast_text(filename=path)


def test_rust_fast_ast_lowers_block_sample_to_lark_python_ast_exactly():
    rust = get_parser_frontend("rust-fast-ast")
    lark = get_parser_frontend("lark-lalr")
    path = REPO_ROOT / "samples" / "block.nomi"

    assert rust.python_ast_text(filename=path) == lark.python_ast_text(filename=path)
