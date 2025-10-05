# lark_to_python_ast.py
# Mixin-style Lark -> Python ast Transformer for the official python.lark grammar.
# Designed as a pragmatic, extensible converter covering major language constructs.
#
# Usage:
#   from lark import Lark
#   from lark.indenter import PythonIndenter
#   from lark_to_python_ast import PythonASTTransformer
#
#   parser = Lark.open_from_package('lark', 'python.lark', ['grammars'],
#                                  parser='lalr', postlex=PythonIndenter(), start='file_input')
#   tree = parser.parse(source_code)
#   module_node = PythonASTTransformer().transform(tree)
#   module_node = ast.fix_missing_locations(module_node)
#   exec(compile(module_node, '<string>', 'exec'), globals_dict)
#
# Note: This is a pragmatic implementation — many complex corners are handled
# defensively (using ast.parse fallback) and mixins are separated for clarity.

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





# fucntional test
if __name__ == "__main__":
    # path relative to this script
    script_path = Path(__file__).resolve()
    script_dir = script_path.parent
    sample_file = script_dir.parent.parent.joinpath('sample_sources', 'dummy').with_name("sample.py")

    if not sample_file.exists():
        raise FileNotFoundError(f"Sample file not found: {sample_file}")

    # read source from file
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
