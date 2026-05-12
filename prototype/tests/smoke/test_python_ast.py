"""
Smoke test: Python AST parser parity.

Compares the custom Lark-based parser output with Python's built-in
``ast.parse()`` for a sample source file.  Writes AST dumps to the
``local/`` directory for manual inspection.

Run manually::

    python3 prototype/tests/smoke/test_python_ast.py
"""

from pathlib import Path
import ast
from prototype.parser.python.utils import generate_ast

SAMPLE_FILE = (
    Path(__file__).resolve().parents[1]
    / "data" / "sample_sources" / "parser" / "sample.py"
)
LOCAL_DIR = Path(__file__).resolve().parents[4] / "local"


def main():
    source = SAMPLE_FILE.read_text(encoding="utf-8")
    python_ast = ast.parse(source)
    lark_ast = generate_ast(code=source)
    lark_ast = ast.fix_missing_locations(lark_ast)

    python_dump = ast.dump(python_ast, indent=2)
    lark_dump = ast.dump(lark_ast, indent=2)

    LOCAL_DIR.mkdir(exist_ok=True)
    (LOCAL_DIR / "lark.ast").write_text(lark_dump, encoding="utf-8")
    (LOCAL_DIR / "python.ast").write_text(python_dump, encoding="utf-8")

    match = python_dump == lark_dump
    print(f"AST match: {match}")
    if not match:
        print("--- Python AST ---")
        print(python_dump)
        print("--- Lark AST ---")
        print(lark_dump)


if __name__ == "__main__":
    main()
