import ast
import pytest
from pathlib import Path
from lark import Lark
from lark.indenter import PythonIndenter
from prototype.parser.python.ast_ import PythonASTTransformer

# Directory containing test source files
SAMPLE_DIR = Path(__file__).resolve().parent / "sample_sources"

# Map file extension → (parser instance, transformer class)

python_parser = Lark.open_from_package(
        "lark",
        "python.lark",
        ["grammars"],
        parser="lalr",
        postlex=PythonIndenter(),
        start="file_input",
)

PARSERS = {
    ".py": (
        python_parser,
        PythonASTTransformer,
    ),
    # Example: ".nomi": (NomiParser(), NomiASTTransformer)
}

def generate_ast_from_code(parser, transformer_cls, code: str):
    """Transform code into AST string using parser + transformer"""
    tree = parser.parse(code)
    transformer = transformer_cls()
    node = transformer.transform(tree)
    return ast.dump(node, include_attributes=False, indent=2)

# Collect all test files for registered extensions
ALL_SOURCES = []
for ext in PARSERS:
    ALL_SOURCES.extend(SAMPLE_DIR.glob(f"*{ext}"))

@pytest.mark.parametrize("source_file", ALL_SOURCES, ids=lambda p: p.name)
def test_ast_regressions(source_file, file_regression):
    """Regression test: parses source file and compares AST dump"""
    ext = source_file.suffix
    if ext not in PARSERS:
        pytest.skip(f"No parser registered for {ext}")

    parser, transformer_cls = PARSERS[ext]
    code = source_file.read_text()
    ast_dump = generate_ast_from_code(parser, transformer_cls, code)
    file_regression.check(ast_dump)
