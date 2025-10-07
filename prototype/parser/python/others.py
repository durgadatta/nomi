import ast

from prototype.parser.python import ensure_stmt_list, ensure_expr, tokval, ensure_store

class ImportMixin:
    def import_stmt(self, items):
        """
        import_stmt: import_name | import_from
        """

        # Case 1: Already a list of aliases (preprocessed by import_name)
        if isinstance(items[0], list):
            return ast.Import(names=items[0])

        # Case 2: Already an AST node
        if isinstance(items[0], (ast.Import, ast.ImportFrom)):
            return items[0]

        # Case 3: Lark Tree (import_name or import_from)
        child = items[0]

        # -------------------
        # import_name
        # -------------------
        if getattr(child, "data", None) == "import_name":
            names_node = child.children[0]
            names = []
            for dotted_as in names_node.children:
                # dotted_as: dotted_name ["as" NAME]
                name_node = dotted_as.children[0]
                if hasattr(name_node, "children"):
                    # dotted_name -> join all parts
                    name = ".".join(n.value for n in name_node.children)
                else:
                    name = name_node.value
                asname = dotted_as.children[1].value if len(dotted_as.children) > 1 else None
                names.append(ast.alias(name=name, asname=asname))
            return ast.Import(names=names)

        # -------------------
        # import_from
        # -------------------
        elif getattr(child, "data", None) == "import_from":
            import_names_node = child.children[-1]

            # Count dots (level)
            level = 0
            if getattr(child.children[0], "data", None) == "dots":
                dots_node = child.children[0]
                level = sum(len(d.value) for d in dots_node.children)

            # Module name
            module = None
            if len(child.children) > 2:
                module_node = child.children[1]
                if getattr(module_node, "data", None) == "dotted_name":
                    module = ".".join(n.value for n in module_node.children)
                else:
                    module = module_node.value

            # Parse imported names
            names = []
            for dotted_as in import_names_node.children:
                name_node = dotted_as.children[0]
                if hasattr(name_node, "children"):
                    name = ".".join(n.value for n in name_node.children)
                else:
                    name = name_node.value
                asname = dotted_as.children[1].value if len(dotted_as.children) > 1 else None
                names.append(ast.alias(name=name, asname=asname))

            return ast.ImportFrom(module=module, names=names, level=level)

        else:
            raise TypeError(f"Unknown import_stmt child: {items[0]}")

class AsyncMixin:
    def await_expr(self, items):
        """
        await_expr: "await" test
        items: [expression]
        """
        expr_node = ensure_expr(items[0])
        return ast.Await(value=expr_node)

class ContextManagerMixin:
    def with_stmt(self, items):
        """
        with_stmt: "with" with_item ("," with_item)* ":" suite
        items: [with_item1, with_item2, ..., body_suite]
        """
        *with_items, body = items

        # Convert suite to statements
        body_stmts = ensure_stmt_list(body)

        # Convert each with_item to ast.withitem
        ast_with_items = []
        for wi in with_items:
            # wi: tuple (context_expr, optional_vars)
            context_expr, optional_vars = wi
            ast_with_items.append(
                ast.withitem(
                    context_expr=ensure_expr(context_expr),
                    optional_vars=ensure_store(ensure_expr(optional_vars)) if optional_vars is not None else None
                )
            )

        return ast.With(body=body_stmts, items=ast_with_items, type_comment=None)

    def with_item(self, items):
        """
        with_item: test ["as" expr]
        items: [context_expr] or [context_expr, optional_vars]
        """
        if len(items) == 1:
            return (items[0], None)
        return (items[0], items[1])



class MatchMixin:
    '''
    This is incomplete; there are so many cases
    '''

import ast
from prototype.parser.python import ensure_expr, ensure_stmt_list, tokval

class MatchMixin:
    # --- Pattern nodes ---
    def const_none(self, items):
        return ast.MatchSingleton(value=None)

    def const_true(self, items):
        return ast.MatchSingleton(value=True)

    def const_false(self, items):
        return ast.MatchSingleton(value=False)

    def number(self, items):
        if not items or len(items) != 1:
            raise ValueError(f"Expected exactly one item for number pattern, got {len(items)}")
        return ast.MatchValue(value=ensure_expr(items[0]))

    def string(self, items):
        if not items or len(items) != 1:
            raise ValueError(f"Expected exactly one item for string pattern, got {len(items)}")
        return ast.MatchValue(value=ensure_expr(items[0]))

    def capture_pattern(self, items):
        if not items or len(items) != 1:
            raise ValueError(f"Expected exactly one item for capture pattern, got {len(items)}")
        name = tokval(items[0])
        if not isinstance(name, str):
            raise ValueError(f"Expected a string name for capture pattern, got {type(name)}")
        return ast.MatchAs(name=name, pattern=None)

    def any_pattern(self, items):
        return ast.MatchAs(name=None, pattern=None)

    def match_or(self, items):
        if not items:
            raise ValueError("Expected at least one pattern for MatchOr")
        patterns = []
        for item in items:
            if isinstance(item, ast.Constant):
                patterns.append(ast.MatchValue(value=ensure_expr(item)))
            elif isinstance(item, ast.AST):
                patterns.append(item)
            else:
                raise ValueError(f"Invalid pattern in MatchOr: {type(item)}")
        return ast.MatchOr(patterns=patterns)

    def sequence_pattern(self, items):
        patterns = [item for item in items if isinstance(item, ast.AST)] if items else []
        return ast.MatchSequence(patterns=patterns)

    def mapping_pattern(self, items):
        keys, patterns = [], []
        if items:
            for item in items:
                if not isinstance(item, (tuple, list)) or len(item) != 2:
                    raise ValueError(f"Expected (key, pattern) pair, got {item}")
                key, pattern = item
                keys.append(ensure_expr(key))
                patterns.append(pattern)
        return ast.MatchMapping(keys=keys, patterns=patterns, rest=None)

    def as_pattern(self, items):
        if not items:
            raise ValueError("Expected at least one item for as_pattern")
        if len(items) == 1:
            return items[0]
        if len(items) != 2:
            raise ValueError(f"Expected one or two items for as_pattern, got {len(items)}")
        pattern = items[0]
        name = tokval(items[1])
        if not isinstance(name, str):
            raise ValueError(f"Expected a string name for as_pattern, got {type(name)}")
        return ast.MatchAs(pattern=pattern, name=name)

    # --- Match case ---
    def match_case(self, items):
        """
        items = [pattern_node(s), optional guard, suite]
        """
        if not items or len(items) < 2:
            raise ValueError(f"Expected at least pattern and body for match_case, got {len(items)}")

        # 1. Pattern: Handle single pattern or list of patterns
        pattern_node = items[0]
        if isinstance(pattern_node, list):
            if not pattern_node:
                raise ValueError("Pattern list cannot be empty")
            if len(pattern_node) == 1:
                pattern_node = pattern_node[0]
                # Wrap Constant in MatchValue if needed
                if isinstance(pattern_node, ast.Constant):
                    pattern_node = ast.MatchValue(value=ensure_expr(pattern_node))
            else:
                # Convert list of patterns to MatchOr, wrapping Constants in MatchValue
                patterns = []
                for p in pattern_node:
                    if isinstance(p, ast.Constant):
                        patterns.append(ast.MatchValue(value=ensure_expr(p)))
                    elif isinstance(p, ast.AST):
                        patterns.append(p)
                    else:
                        raise ValueError(f"Invalid pattern in list: {type(p)}")
                pattern_node = ast.MatchOr(patterns=patterns)
        else:
            # Single pattern: Wrap Constant in MatchValue if needed
            if isinstance(pattern_node, ast.Constant):
                pattern_node = ast.MatchValue(value=ensure_expr(pattern_node))
            elif not isinstance(pattern_node, (ast.MatchValue, ast.MatchAs, ast.MatchOr,
                                            ast.MatchSequence, ast.MatchMapping,
                                            ast.MatchSingleton, ast.MatchClass)):
                raise ValueError(f"Expected a valid pattern node, got {type(pattern_node)}")

        # 2. Optional guard
        guard_node = None
        if len(items) > 2 and items[1] is not None:
            guard_node = ensure_expr(items[1])

        # 3. Body
        body_node = ensure_stmt_list(items[-1])

        return ast.match_case(pattern=pattern_node, guard=guard_node, body=body_node)

    # --- Match statement ---
    def match_stmt(self, items):
        """
        items[0] = subject
        items[1:] = match_case nodes
        """
        if not items or len(items) < 2:
            raise ValueError(f"Expected subject and at least one case for match_stmt, got {len(items)}")
        subject_node = ensure_expr(items[0])
        case_nodes = [self.match_case(case) if not isinstance(case, ast.match_case) else case
                      for case in items[1:]]
        return ast.Match(subject=subject_node, cases=case_nodes)

    def class_pattern(self, items):
        """
        items[0] = class name or attr pattern
        items[1] = arguments pattern (positional + keywords)
        """
        if not items:
            raise ValueError("Expected at least class name for class_pattern")
        class_name_node = ensure_expr(items[0])
        pos_args, kw_args = [], []
        if len(items) > 1:
            args_node = items[1]
            if not isinstance(args_node, (tuple, list)) or len(args_node) != 2:
                raise ValueError(f"Expected (pos_args, kw_args) tuple for class_pattern, got {args_node}")
            pos_args, kw_args = args_node
            pos_args = pos_args if isinstance(pos_args, list) else []
            kw_args = kw_args if isinstance(kw_args, list) else []
            for kw in kw_args:
                if not isinstance(kw, (tuple, list)) or len(kw) != 2:
                    raise ValueError(f"Expected (key, pattern) pair in kw_args, got {kw}")

        return ast.MatchClass(
            cls=class_name_node,
            patterns=pos_args,
            kwd_attrs=[tokval(kw[0]) for kw in kw_args],
            kwd_patterns=[kw[1] for kw in kw_args]
        )

class OthersMixin(ImportMixin, ContextManagerMixin, AsyncMixin, MatchMixin):
    def assert_stmt(self, items):
        """
        assert_stmt: "assert" test ["," test]
        items:
        - items[0] = test expression
        - items[1] = optional message expression
        """
        test_node = ensure_expr(items[0])
        msg_node = ensure_expr(items[1]) if len(items) > 1 else None
        if msg_node.value is None:
            msg_node = None
        return ast.Assert(test=test_node, msg=msg_node)
    
    def del_stmt(self, items):
        """
        items: list of expressions / targets to delete
        Returns ast.Delete node.
        """
        targets = []
        for it in items:
            # Convert Name / Attribute / Subscript appropriately
            if isinstance(it, ast.Name):
                targets.append(ast.Name(id=it.id, ctx=ast.Del()))
            elif isinstance(it, ast.Attribute):
                # Attribute can be del target; the value stays the same
                targets.append(ast.Attribute(
                    value=it.value,
                    attr=it.attr,
                    ctx=ast.Del()
                ))
            elif isinstance(it, ast.Subscript):
                targets.append(ast.Subscript(
                    value=it.value,
                    slice=it.slice,
                    ctx=ast.Del()
                ))
            else:
                # Possibly other complex targets (Tuple, List)
                if isinstance(it, (ast.Tuple, ast.List)):
                    # recursively set ctx=Del for all elements
                    targets.append(self._del_target(it))
                else:
                    raise TypeError(f"Unsupported del target: {it!r}")
        return ast.Delete(targets=targets)

    def _del_target(self, node):
        """
        Recursively set ctx=Del for Tuple/List elements.
        """
        if isinstance(node, ast.Tuple):
            return ast.Tuple(
                elts=[self._del_target(e) for e in node.elts],
                ctx=ast.Del()
            )
        elif isinstance(node, ast.List):
            return ast.List(
                elts=[self._del_target(e) for e in node.elts],
                ctx=ast.Del()
            )
        elif isinstance(node, ast.Name):
            return ast.Name(id=node.id, ctx=ast.Del())
        elif isinstance(node, ast.Attribute):
            return ast.Attribute(value=node.value, attr=node.attr, ctx=ast.Del())
        elif isinstance(node, ast.Subscript):
            return ast.Subscript(value=node.value, slice=node.slice, ctx=ast.Del())
        else:
            raise TypeError(f"Unsupported del target in _del_target: {node!r}")