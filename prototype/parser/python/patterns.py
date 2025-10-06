import ast 
from prototype.parser.python import ensure_expr, ensure_stmt_list


class PatternMixin:
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
