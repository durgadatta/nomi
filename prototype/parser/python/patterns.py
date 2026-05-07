import ast 
from lark import Token, Tree


class PatternMixin:
    def MATCH(self, token): return "match"
    def CASE(self, token): return "case"

    def literal_pattern(self, items):
        item = items[0]
        if isinstance(item, ast.Constant):
            # NOTE:  a simple in check is too broad, matches 1/0 as well; 'is' is required
            if any(item.value is v for v in [True, False, None]):
                return ast.MatchSingleton(value=item.value)
            return ast.MatchValue(value=item)
        return item

    def inner_literal_pattern(self, items):
        return items[0]

    def capture_pattern(self, items):
        if items[0] == "_":
            return ast.MatchAs(name=None, pattern=None)
        return ast.MatchAs(name=items[0], pattern=None)

    def any_pattern(self, items):
        return ast.MatchAs(name=None, pattern=None)

    def star_pattern(self, items):
        return ast.MatchStar(name=items[0])
 
    def value(self, items):
        """attr_pattern/name_or_attr_pattern: Create pattern node"""
        attr_chain = ".".join(items)
        name_node = ast.Name(id=attr_chain, ctx=ast.Load())
        return ast.MatchValue(value=ast.Constant(value=name_node))

    def mapping_item_pattern(self, items):
        """Keys need values, patterns need patterns"""
        key_node, pattern_node = items
        
        # Extract value from pattern node for keys
        if isinstance(key_node, ast.MatchValue):
            key = key_node.value
        elif isinstance(key_node, ast.MatchSingleton):
            key = ast.Constant(value=key_node.value)
        else:
            key = key_node
            
        return (key, pattern_node)

    def mapping_pattern(self, items):
        keys, patterns = zip(*items) if items else ([], [])
        return ast.MatchMapping(keys=list(keys), patterns=list(patterns), rest=None)

    def mapping_star_pattern(self, items):
        pairs = [item for item in items if isinstance(item, tuple)]
        rest = next((item for item in items if isinstance(item, str)), None)
        keys, patterns = zip(*pairs) if pairs else ([], [])
        return ast.MatchMapping(keys=list(keys), patterns=list(patterns), rest=rest)

    def or_pattern(self, items):
        return items[0] if len(items) == 1 else ast.MatchOr(patterns=items)

    def as_pattern(self, items):
        return items[0] if len(items) == 1 else ast.MatchAs(pattern=items[0], name=items[1])

    def closed_pattern(self, items):
        return items[0]

    def _sequence_pattern(self, items):
        return items

    def sequence_item_pattern(self, items):
        return items[0]

    def sequence_pattern(self, items):
        patterns = []
        for item in items:
            if isinstance(item, list):
                patterns.extend(item)
            else:
                patterns.append(item)
        return ast.MatchSequence(patterns=patterns)

    def class_pattern(self, items):
        """Class names need Name nodes"""
        cls_node = items[0]
        
        # Extract Name from pattern wrapper
        if isinstance(cls_node, ast.MatchValue):
            if isinstance(cls_node.value, ast.Constant) and isinstance(cls_node.value.value, ast.Name):
                cls = cls_node.value.value
            elif isinstance(cls_node.value, ast.Name):
                cls = cls_node.value
            else:
                cls = ast.Name(id=".".join(getattr(cls_node, 'children', []) or ["unknown"]), ctx=ast.Load())
        elif isinstance(cls_node, ast.Name):
            cls = cls_node
        else:
            cls = ast.Name(id=str(cls_node), ctx=ast.Load())
        
        patterns, kwd_attrs, kwd_patterns = [], [], []
        if len(items) > 1 and items[1]:
            for item in items[1]:
                if item is None: continue
                if isinstance(item, tuple):
                    kwd_attrs.append(item[0])
                    kwd_patterns.append(item[1])
                elif isinstance(item, ast.AST):
                    patterns.append(item)
        
        return ast.MatchClass(cls=cls, patterns=patterns, 
                            kwd_attrs=kwd_attrs, kwd_patterns=kwd_patterns)

    def arguments_pattern(self, items):
        result = []
        for item in items:
            if item is None: continue
            result.extend(item) if isinstance(item, list) else result.append(item)
        return result

    def pos_arg_pattern(self, items):
        return items

    def keyws_arg_pattern(self, items):
        return items

    def keyw_arg_pattern(self, items):
        return items

    def case(self, items):
        pattern, body = items[0], items[-1]
        guard = items[1] if len(items) > 2 else None
        return ast.match_case(pattern=pattern, guard=guard, body=body)

    def match_stmt(self, items):
        subject, *cases = items
        case_nodes = [case if isinstance(case, ast.match_case) else self.case(case) 
                     for case in cases]
        return ast.Match(subject=subject, cases=case_nodes)