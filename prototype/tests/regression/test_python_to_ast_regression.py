import ast
import pytest
from pathlib import Path
from lark import Lark
from lark.indenter import PythonIndenter
from prototype.parser.python.ast_ import PythonASTTransformer
from prototype.parser.python.utils import generate_ast

# Directory containing test source files
SAMPLE_DIR = Path(__file__).resolve().parents[1]/'data/sample_sources/parser'
ALL_SOURCES = SAMPLE_DIR.glob('*.py')


@pytest.mark.parametrize("source_file", ALL_SOURCES, ids=lambda p: p.name)
def test_ast_regressions(source_file, file_regression):
    code = source_file.read_text()
    ast_dump = generate_ast(code=code)
    file_regression.check(ast_dump)
