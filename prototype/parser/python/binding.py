'''
Binding constructs; this will be one of the most complex aspect to play with
'''
import ast 

from prototype.parser.python import ensure_store

class BindingMixin:
    def assign_stmt(self, items):
        """
        assign_stmt: annassign | augassign | assign
        """
        # Just return the processed assignment node
        return items[0]

    def assign(self, items):
        """
        Build a full Python AST Assign node with correct semantics.

        Parameters:
        - items: [lhs_nodes..., rhs_node]
            lhs_nodes: single AST node or list/nested lists of AST nodes (targets)
            rhs_node: AST expression node (already fully built by transformer)
        """
        if len(items) == 2:
            lhs_nodes = [items[0]]
            rhs_node = items[1]
        else:
            lhs_nodes = items[:-1]
            rhs_node = items[-1]

        # Flatten any nested lists in lhs_nodes
        flattened_lhs = []
        for node in lhs_nodes:
            if isinstance(node, list):
                flattened_lhs.extend(node)
            else:
                flattened_lhs.append(node)
        
        lhs_nodes = [ensure_store(n) for n in flattened_lhs]

        # --- Wrap multiple top-level targets in a Tuple if needed ---
        if len(lhs_nodes) == 1:
            target_node = lhs_nodes[0]
        else:
            target_node = ast.Tuple(elts=lhs_nodes, ctx=ast.Store())

        # --- RHS: convert Python list to AST Tuple if needed ---
        def ensure_rhs(node):
            if isinstance(node, list):
                # recursively convert lists to AST Tuple nodes
                return ast.Tuple(elts=[ensure_rhs(e) for e in node], ctx=ast.Load())
            elif isinstance(node, ast.AST):
                return node  # already an AST node
            else:
                # raw constant
                return ast.Constant(value=node)

        rhs_node = ensure_rhs(rhs_node)

        # --- Build final Assign node ---
        return ast.Assign(targets=[target_node], value=rhs_node)

    def _normalize_value_for_expr(self, value):
        """Convert a list of expressions from testlist to proper AST expression or tuple."""
        if isinstance(value, list):
            if len(value) == 0:
                return ast.Tuple(elts=[], ctx=ast.Load())
            if len(value) == 1:
                return value[0]
            return ast.Tuple(elts=value, ctx=ast.Load())
        return value

    def _to_store_target(self, node):
        """
        Convert node to a valid AugAssign target.
        Acceptable types: ast.Name, ast.Attribute, ast.Subscript.
        """
        if isinstance(node, ast.Name):
            return ast.Name(id=node.id, ctx=ast.Store())
        if isinstance(node, ast.Attribute):
            return ast.Attribute(value=node.value, attr=node.attr, ctx=ast.Store())
        if isinstance(node, ast.Subscript):
            return node
        raise TypeError(f"Invalid target for augmented assignment: {type(node)}")

    def augassign(self, items):
        """
        Lark signature for augmented assignment:
            items[0] = testlist_star_expr  (target)
            items[1] = augassign_op token   (e.g. '+=')
            items[2] = yield_expr | testlist  (value)
        Returns: ast.AugAssign
        """
        AUGASSIGN_OPERATORS = {
            '+=': ast.Add,
            '-=': ast.Sub,
            '*=': ast.Mult,
            '@=': ast.MatMult,
            '/=': ast.Div,
            '%=': ast.Mod,
            '&=': ast.BitAnd,
            '|=': ast.BitOr,
            '^=': ast.BitXor,
            '<<=': ast.LShift,
            '>>=': ast.RShift,
            '**=': ast.Pow,
            '//=': ast.FloorDiv,
        }

        if len(items) < 3:
            raise TypeError(f"augassign: expected 3 children, got {len(items)}")

        raw_target, raw_op, raw_value = items[0], items[1], items[2]

        # Normalize target: testlist_star_expr can yield a single-element list
        if isinstance(raw_target, list):
            if len(raw_target) == 0:
                raise TypeError("AugAssign: empty target list")
            if len(raw_target) > 1:
                raise TypeError("AugAssign target must be a single assignable (not a tuple/list)")
            target_node = raw_target[0]
        else:
            target_node = raw_target

        target_node = self._to_store_target(target_node)

        # Normalize value
        value_node = self._normalize_value_for_expr(raw_value)
        if not isinstance(value_node, ast.expr):
            raise TypeError(f"AugAssign value must be an expression, got {type(value_node)}")

        # Operator
        op_sym = raw_op.children[0].value
        if op_sym not in AUGASSIGN_OPERATORS:
            raise ValueError(f"Unknown augassign operator: {op_sym!r}")
        op_node = AUGASSIGN_OPERATORS[op_sym]()

        # Build AST node
        return ast.AugAssign(target=target_node, op=op_node, value=value_node)
    
    def assign_expr(self, items):
        ''' a := 2'''
        name, value = items
        return ast.NamedExpr(
            target=ast.Name(id=name, ctx=ast.Store()),
            value=value
        )
    

    def annassign(self, items):
        """
        NOTE: Why is the grammar for annassign nd assign not same
        on the rhs part?

        Handle annotated assignment:
            testlist_star_expr ":" test ["=" test]
        
        Examples:
            x: int
            x: int = 42
            self.x: List[int] = []
        """
        if len(items) not in (2, 3):
            raise TypeError(f"annassign: expected 2 or 3 items, got {len(items)}")

        target_node = items[0]
        annotation_node = items[1]
        value_node = items[2] if len(items) == 3 else None

        # --- Normalize target ---
        if isinstance(target_node, list):
            if len(target_node) != 1:
                raise SyntaxError("Annotated assignment target must be a single name/attribute/subscript")
            target_node = target_node[0]

        target_node = self._to_store_target(target_node)
        if value_node is not None:
            value_node = self._normalize_value_for_expr(value_node)

        simple_flag = isinstance(target_node, ast.Name)

        return ast.AnnAssign(
            target=target_node,
            annotation=annotation_node,
            value=value_node,
            simple=int(simple_flag)
        )
