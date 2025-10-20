'''
This is a basic smoke-testing; 
later systematic regression test (that compare ast from Python's ast and implementation here will be compared)
and unit test (similar comparison on small chunks) will be added

also all will be hooked-up via pytest
'''

from pathlib import Path
import ast
from lark import Lark
from prototype.parser.python.utils import generate_ast




if __name__ == "__main__":
    script_path = Path(__file__).resolve()
    sample_file = script_path.parents[1].joinpath('data', 'sample_sources', 'parser', 'context_managers.py')
    source_code = sample_file.read_text(encoding="utf-8")

    # Also parse Python's built-in AST
    python_module = ast.parse(source_code)

    # Convert ASTs to strings (pretty-print)
    lark_module = generate_ast(code=source_code)
    lark_module = ast.fix_missing_locations(lark_module)

    lark_ast_str = ast.dump(lark_module, indent=2)
    python_ast_str = ast.dump(python_module, indent=2)


    local_folder = script_path.parents[3].joinpath('local')
    (local_folder / "lark.ast").write_text(lark_ast_str, encoding="utf-8")
    (local_folder / "python.ast").write_text(python_ast_str, encoding="utf-8")

    print("Lark -> AST:")
    print(lark_ast_str)
    print("\nPython ast.parse -> AST:")
    print(python_ast_str)

