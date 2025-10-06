
import ast
from lark import Tree, Token
from prototype.parser.python import ensure_expr, storeify

def ensure_stmt_list(stmts):
    out = []
    for n in stmts:
        if isinstance(n, ast.stmt):
            out.append(n)
        elif isinstance(n, list):
            out.extend(ensure_stmt_list(n))
        elif isinstance(n, ast.expr):
            # Only wrap true expression statements
            out.append(ast.Expr(value=n))
        else:
            raise TypeError(f"Unknown node in statement list: {type(n)}")
    return out

class CompMixin:
    """Mixin for handling Python comprehensions in Lark AST transformer."""

    # --- Entry points for comprehension nodes ---
    def comprehension(self, items):
        """
        Handle comprehension{comp_result}: comp_result comp_fors [comp_if].
        Returns a tuple: (comp_result, list of ast.comprehension)
        """
        if not items or len(items) < 2:
            raise ValueError(f"Expected at least 2 items in comprehension, got {items}")
        comp_result = items[0]
        comp_fors = items[1]
        comp_if = items[2] if len(items) > 2 else None

        if not isinstance(comp_fors, list):
            comp_fors = [comp_fors]

        # Attach comp_if to the last generator
        if comp_if:
            if not comp_fors:
                raise ValueError("comp_if provided but no comp_for available")
            comp_fors[-1].ifs.append(self._to_expr(comp_if))

        return comp_result, comp_fors

    def comp_fors(self, items):
        """Handle comp_fors: comp_for+"""
        # items: list of ast.comprehension
        return items

    def comp_for(self, items):
        """
        Handle comp_for: [ASYNC] 'for' exprlist 'in' or_test
        Robustly ignores literal tokens ('for', 'in') and None placeholders.
        """
        # Filter out literal tokens and None
        nodes = [x for x in items if isinstance(x, (ast.AST, list))]

        if len(nodes) == 2:
            # Normal: exprlist, iterable
            exprlist, iter_ = nodes
            is_async = False
        elif len(nodes) == 3:
            # Async: async token, exprlist, iterable
            exprlist, iter_ = nodes[1:]
            is_async = True
        else:
            raise ValueError(f"Cannot parse comp_for items: {items}")

        if exprlist is None:
            raise ValueError(f"Comprehension loop target cannot be None: items={items}")

        exprlist = self._ensure_store(exprlist)

        return ast.comprehension(
            target=exprlist,
            iter=self._to_expr(iter_),
            ifs=[],
            is_async=1 if is_async else 0
        )


    def comp_if(self, items):
        """Handle comp_if: 'if' test_nocond"""
        return self._to_expr(items[1])  # skip 'if' token

    # --- Comprehension AST constructors ---
    def list_comprehension(self, items):
        comp_result, comp_fors = items[0]
        return ast.ListComp(
            elt=self._to_expr(comp_result),
            generators=comp_fors,
            lineno=1,
            col_offset=0
        )

    def set_comprehension(self, items):
        comp_result, comp_fors = items[0]
        return ast.SetComp(
            elt=self._to_expr(comp_result),
            generators=comp_fors,
            lineno=1,
            col_offset=0
        )

    def tuple_comprehension(self, items):
        comp_result, comp_fors = items[0]
        return ast.GeneratorExp(
            elt=self._to_expr(comp_result),
            generators=comp_fors,
            lineno=1,
            col_offset=0
        )

    def dict_comprehension(self, items):
        comp_result, comp_fors = items[0]
        if not (isinstance(comp_result, (list, tuple)) and len(comp_result) == 2):
            raise ValueError(f"Invalid dict comprehension element: {comp_result}")
        key_expr, value_expr = comp_result
        return ast.DictComp(
            key=self._to_expr(key_expr),
            value=self._to_expr(value_expr),
            generators=comp_fors,
            lineno=1,
            col_offset=0
        )

    # --- Utilities ---
    def _to_expr(self, node):
        """Ensure a proper AST expression node."""
        if isinstance(node, ast.AST):
            return node
        elif isinstance(node, (list, tuple)):
            return ast.Tuple(elts=[self._to_expr(n) for n in node], ctx=ast.Load())
        else:
            return ast.Constant(value=node)

    def _ensure_store(self, node):
        if node is None:
            raise ValueError("Target for comprehension cannot be None")
        elif isinstance(node, ast.Name):
            return ast.Name(id=node.id, ctx=ast.Store(),
                            lineno=getattr(node, 'lineno', 0),
                            col_offset=getattr(node, 'col_offset', 0))
        elif isinstance(node, ast.Tuple):
            return ast.Tuple(
                elts=[self._ensure_store(n) for n in node.elts],
                ctx=ast.Store(),
                lineno=getattr(node, 'lineno', 0),
                col_offset=getattr(node, 'col_offset', 0)
            )
        elif isinstance(node, list) and all(n is not None for n in node):
            return ast.Tuple(
                elts=[self._ensure_store(n) for n in node],
                ctx=ast.Store()
            )
        else:
            raise ValueError(f"Invalid target for comprehension: {node}")

class ControlMixin(CompMixin):
    def elif_(self, items):
        # items[0] = test (ast.expr), items[1] = suite (list or nodes)
        test_node = items[0]
        if not isinstance(test_node, ast.expr):
            raise TypeError(f"Elif test must be an expression, got {type(test_node)}")
        body_list = ensure_stmt_list(items[1])
        return (test_node, body_list)

    def elifs(self, items):
        # items is a list of elif_ results (each a (test, body) tuple)
        return items  # Return the list of (test, body) tuples as-is

    def if_stmt(self, items):
        """
        items[0] = test
        items[1] = suite (body)
        items[2] = elifs (list of (test, body) tuples)
        items[3] = else_suite (optional)
        """
        test = items[0]
        if not isinstance(test, ast.expr):
            raise TypeError(f"If test must be an expression, got {type(test)}")

        body = ensure_stmt_list(items[1])

        # Ensure elifs is a list of tuples
        elifs = items[2] if len(items) > 2 else []

        # Ensure else_suite is always a list
        else_suite = ensure_stmt_list(items[3]) if len(items) > 3 else []

        # Start with orelse being the else suite (always a list)
        orelse_node = else_suite

        # Process elifs in reverse to nest If nodes
        for elif_item in reversed(elifs):
            if not (isinstance(elif_item, tuple) and len(elif_item) == 2):
                raise TypeError(f"Elif item must be a (test, body) tuple, got {type(elif_item)}")
            elif_test, elif_body = elif_item
            elif_body_list = ensure_stmt_list(elif_body)
            nested_if = ast.If(
                test=elif_test,
                body=elif_body_list,
                orelse=orelse_node   # Always a list
            )
            orelse_node = [nested_if]

        # orelse_node is now guaranteed to be a list
        return ast.If(test=test, body=body, orelse=orelse_node)

    def while_stmt(self, items):
        test = items[0]; body = items[1] if len(items) > 1 else []; orelse = items[2] if len(items) > 2 else []
        return ast.While(test=ensure_expr(test), body=body, orelse=orelse)

    def for_stmt(self, items):
        target = items[0]; iter_expr = items[1]; body = items[2] if len(items) > 2 else []; 
        orelse = items[3] if len(items) > 3 else []
        if orelse is None:
            # ast complains othewise; thse might be handled at single place
            # where statemetns are normalized
            orelse = []

        targ = storeify(target) if isinstance(target, (ast.Name, ast.Tuple, ast.List)) else target
        return ast.For(target=targ, iter=ensure_expr(iter_expr), body=body, orelse=orelse, type_comment=None)
