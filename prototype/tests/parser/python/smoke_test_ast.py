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
    ExpressionMixin, StatementMixin, CallMixin, 
)


class ModuleMixin(
    ExpressionMixin, 
    StatementMixin,
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

    parser = Lark.open_from_package(
        'lark',
        'python.lark',
        ['grammars'],
        parser='lalr',
        postlex=PythonIndenter(),
        start='file_input'
    )

    # parse Lark tree
    tree = parser.parse(source_code)

    # transform to Python AST
    tr = PythonASTTransformer()
    module = tr.transform(tree)
    module = ast.fix_missing_locations(module)

    # print ASTs for comparison
    print("Lark -> AST:")
    print(ast.dump(module, indent=4))
    print("\nPython ast.parse -> AST:")
    print(ast.dump(ast.parse(source_code), indent=4))

    # execute the compiled AST
    globals_for_exec = {'xyx': int}  # optional: supply any annotations needed
    codeobj = compile(module, "<string>", "exec")
    print("\n====== EXEC OUTPUT ======")
    exec(codeobj, globals_for_exec)
