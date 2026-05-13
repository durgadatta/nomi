
import ast
from lark import Tree, Token
from . import ensure_store

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
    def if_stmt(self, items):
        """
        if_stmt: "if" test ":" suite elifs ["else" ":" suite]
        """
        # items: [test, suite, elifs, else_suite]
        test = items[0]
        body = items[1]
        elifs = items[2] if len(items) > 2 else []
        else_suite = items[3] if len(items) > 3 else []
        
        # Build the if-elif-else chain from the bottom up
        # Start with the innermost (last elif or else)
        current_orelse = else_suite if else_suite is not None else []
        
        # Process elifs in reverse order to build the nested structure correctly
        for elif_test, elif_body in reversed(elifs):
            current_orelse = [ast.If(test=elif_test, body=elif_body, orelse=current_orelse)]
        
        # Create the main if statement
        return ast.If(test=test, body=body, orelse=current_orelse)

    def elifs(self, items):
        """
        elifs: elif_*
        Returns: list of (test, body) tuples for each elif
        """
        # items is a list of elif AST nodes, each is (test, body)
        return items

    def elif_(self, items):
        """
        elif_: "elif" test ":" suite
        Returns: (test, body) tuple
        """
        return (items[0], items[1])

    def unless_stmt(self, items):
        """unless_stmt: 'unless' test ':' suite
        Desugars to: if not test: suite"""
        test_expr, body = items
        return ast.If(
            test=ast.UnaryOp(op=ast.Not(), operand=test_expr),
            body=body,
            orelse=[],
        )

    def postfix_if(self, items):
        """return x if cond  →  if cond: return x"""
        stmt, condition = items
        return ast.If(test=condition, body=[stmt], orelse=[])

    def postfix_unless(self, items):
        """return x unless cond  →  if not cond: return x"""
        stmt, condition = items
        return ast.If(
            test=ast.UnaryOp(op=ast.Not(), operand=condition),
            body=[stmt],
            orelse=[],
        )

    def postfix_if_expr(self, items):
        """x = compute() if flag  →  if flag: x = compute()"""
        stmt, condition = items
        return ast.If(test=condition, body=[stmt], orelse=[])

    def postfix_unless_expr(self, items):
        """x = compute() unless flag  →  if not flag: x = compute()"""
        stmt, condition = items
        return ast.If(
            test=ast.UnaryOp(op=ast.Not(), operand=condition),
            body=[stmt],
            orelse=[],
        )

    def while_stmt(self, items):
        test, body, orelse = items 
        orelse = orelse or []
        return ast.While(test=test, body=body, orelse=orelse)

    def exprlist(self, items):
        """
        exprlist: (expr|star_expr) ("," (expr|star_expr))* [","]
        Handle assignment targets - ensure Store context
        """       
        # If we get a single AST node (not a list), wrap it
        if not isinstance(items, list):
            items = [items]
        
        # Apply Store context to all items
        processed_items = [ensure_store(item) for item in items]
        
        # Return single item or Tuple
        if len(processed_items) == 1:
            return processed_items[0]
        return ast.Tuple(elts=processed_items, ctx=ast.Store())
    
    def for_stmt(self, items):
        """
        for_stmt: "for" exprlist "in" testlist ":" suite ["else" ":" suite]
        """
        target, iterable, body, else_body = items 
        else_body = else_body or []
        
        return ast.For(
            target=ensure_store(target),
            iter=iterable,
            body=body,
            orelse=else_body
        )