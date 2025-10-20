import ast 
from prototype.parser.python import ensure_expr
from lark import Token, Tree


class PatternMixin:
    def MATCH(self, token):
        return "match"
    
    def CASE(self, token):
        return "case"

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

    def literal_pattern(self, items):
        """
        Handle literal pattern, e.g., '0', '"hello"', 'None', 'True', 'False'.
        Grammar: literal_pattern (assumed as NUMBER | STRING | "None" | "True" | "False")
        Returns: ast.MatchValue or ast.MatchSingleton.
        """
        if not items or len(items) != 1:
            raise ValueError(f"Expected exactly one item for literal_pattern, got {len(items)}")
        item = items[0]
        if isinstance(item, ast.Constant):
            return ast.MatchValue(value=item)
        if isinstance(item, Token):
            if item.type == "NUMBER":
                return ast.MatchValue(value=ensure_expr(item))
            if item.type == "STRING":
                return ast.MatchValue(value=ensure_expr(item))
            if item.type == "NONE":
                return ast.MatchSingleton(value=None)
            if item.type == "TRUE":
                return ast.MatchSingleton(value=True)
            if item.type == "FALSE":
                return ast.MatchSingleton(value=False)
        raise ValueError(f"Invalid literal pattern: {item}")

    def capture_pattern(self, items):
        if not items or len(items) != 1:
            raise ValueError(f"Expected exactly one item for capture pattern, got {len(items)}")
        name = items[0]
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
        pattern, name = items
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
        body_node = items[-1]

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

    def star_pattern(self, items):
        """
        Handle star pattern, e.g., '*rest'.
        Grammar: "*" NAME -> star_pattern
        Returns: ast.MatchStar node.
        """
        if not items or len(items) != 1:
            raise ValueError(f"Expected exactly one item for star_pattern, got {len(items)}")
        name = items[0]
        if not isinstance(name, str):
            raise ValueError(f"Expected a string name for star_pattern, got {type(name)}")
        return ast.MatchStar(name=name)

    def class_pattern(self, items):
        """
        Handle class pattern, e.g., 'int(n)', 'Point(x=n)'.
        Grammar: name_or_attr_pattern "(" [arguments_pattern ","?] ")"
        Returns: ast.MatchClass node.
        """
        cls = ast.Name(id=items[0], ctx=ast.Load())
        patterns = []
        kwd_attrs = []
        kwd_patterns = []
        if len(items) > 1 and items[1] is not None:  # Check for non-empty arguments
            arg_items = items[1]
            if isinstance(arg_items, list):
                # Filter out None or empty items (e.g., from trailing comma)
                arg_items = [item for item in arg_items if item is not None]
                for item in arg_items:
                    if isinstance(item, Tree) and item.data == "mapping_item_pattern":
                        # Keyword pattern, e.g., x=n
                        key, pattern = item.children
                        kwd_attrs.append(key)
                        kwd_patterns.append(self.as_pattern([pattern]) if isinstance(pattern, Tree) and pattern.data == "as_pattern" else self.capture_pattern([pattern]))
                    elif isinstance(item, Tree) and item.data in ("capture_pattern", "as_pattern"):
                        # Positional pattern, e.g., n
                        patterns.append(self.as_pattern(item.children) if item.data == "as_pattern" else self.capture_pattern(item.children))
                    elif isinstance(item, ast.AST):
                        patterns.append(item)
                    else:
                        raise ValueError(f"Invalid pattern in arguments_pattern: {item}")
            else:
                # Single positional pattern
                if isinstance(arg_items, Tree) and arg_items.data in ("capture_pattern", "as_pattern"):
                    patterns.append(self.as_pattern([arg_items]) if arg_items.data == "as_pattern" else self.capture_pattern(arg_items.children))
                elif isinstance(arg_items, ast.AST):
                    patterns.append(arg_items)
                else:
                    raise ValueError(f"Invalid single pattern in arguments_pattern: {arg_items}")
        return ast.MatchClass(
            cls=cls,
            patterns=patterns,
            kwd_attrs=kwd_attrs,
            kwd_patterns=kwd_patterns
        )