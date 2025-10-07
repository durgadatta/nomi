import pytest
from pathlib import Path
import ast

from prototype.parser.python.utils import generate_ast



PYTHON_SOURCES = (
    Path(__file__).resolve().parents[1]
    .joinpath("data", "sample_sources")
    .glob('*.py')
)


@pytest.mark.parametrize("source_file", PYTHON_SOURCES, ids=lambda p: p.name)
def test_python_ast_regression(source_file):
    code = source_file.read_text()

    # AST from custom parser
    custom_ast = generate_ast(code=code)

    # AST from Python's ast module → this is the baseline
    python_ast = ast.dump(ast.parse(code), include_attributes=False, indent=2)

    assert custom_ast == python_ast