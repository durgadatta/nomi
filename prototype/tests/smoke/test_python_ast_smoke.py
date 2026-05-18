import ast

import pytest

from prototype.parser.python.utils import generate_ast

pytestmark = pytest.mark.smoke


def test_python_ast_smoke_matches_builtin_for_tiny_program():
    source = "def add(a, b=1):\n    return a + b\nresult = add(4)\n"
    python_ast = ast.parse(source)
    lark_ast = ast.fix_missing_locations(generate_ast(code=source))
    assert ast.dump(lark_ast) == ast.dump(python_ast)
