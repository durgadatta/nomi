'''
This is a basic smoke-testing; 
later systematic regression test (that compare ast from Python's ast and implementation here will be compared)
and unit test (similar comparison on small chunks) will be added

also all will be hooked-up via pytest
'''

from pathlib import Path
import ast
from lark import Transformer, Lark
from lark.indenter import PythonIndenter

from prototype.parser.python import (
    ensure_expr, 
    ExpressionMixin, StatementMixin, CallMixin, ControlMixin
)


class ModuleMixin(
    ExpressionMixin, 
    StatementMixin,
    ControlMixin,
    CallMixin,   
):
    def file_input(self, items):
        body = []
        for it in items:
            if isinstance(it, list):
                for s in it:
                    if isinstance(s, ast.stmt): body.append(s)
            elif isinstance(it, ast.stmt): body.append(it)
        return ast.Module(body=body, type_ignores=[])

    def single_input(self, items): return self.file_input(items)
    def eval_input(self, items):
        if items: return ensure_expr(items[0])
        return ast.Expression(body=ast.Constant(None))


class PythonASTTransformer(
    ModuleMixin,
    Transformer):
    pass
    def __default__(self, data, children, meta):
        # collapse single-child wrappers
        if len(children) == 1:
            return children[0]
        return children


if __name__ == "__main__":
    script_path = Path(__file__).resolve()
    sample_file = script_path.parents[3].joinpath('sample_sources', 'dummy').with_name("sample.py")
    source_code = sample_file.read_text(encoding="utf-8")

    # Load Lark parser
    parser = Lark.open_from_package(
        'lark',
        'python.lark',
        ['grammars'],
        parser='lalr',
        postlex=PythonIndenter(),
        start='file_input'
    )

    # Parse Lark tree
    tree = parser.parse(source_code)

    # Transform to Python AST using your transformer
    tr = PythonASTTransformer()
    lark_module = tr.transform(tree)

    # Fix line numbers globally
    lark_module = ast.fix_missing_locations(lark_module)

    # Also parse Python's built-in AST
    python_module = ast.parse(source_code)

    # Convert ASTs to strings (pretty-print)
    lark_ast_str = ast.dump(lark_module, indent=4)
    python_ast_str = ast.dump(python_module, indent=4)


    local_folder = script_path.parents[4].joinpath('local')
    (local_folder / "lark.ast").write_text(lark_ast_str, encoding="utf-8")
    (local_folder / "python.ast").write_text(python_ast_str, encoding="utf-8")

    print("Lark -> AST:")
    print(lark_ast_str)
    print("\nPython ast.parse -> AST:")
    print(python_ast_str)

    # --- Execute compiled AST ---
    globals_for_exec = {}  # supply any annotations if needed
    codeobj = compile(lark_module, "<string>", "exec")
    print("\n====== EXEC OUTPUT ======")
    exec(codeobj, globals_for_exec)
