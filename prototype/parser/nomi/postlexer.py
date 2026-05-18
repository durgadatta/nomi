"""Custom postlexer: PythonIndenter + LALR disambiguation tokens.

Inserting STAR tokens at the lexer level removes the need for the
``implicit_mul`` grammar rule, which was a major source of Earley
ambiguity (NUMBER could start either ``power`` or ``implicit_mul``).
"""

from lark.indenter import PythonIndenter
from lark.lexer import Token

# Terminal types for number tokens — any of these followed by an adjacent
# NAME or LPAR implies implicit multiplication.
_NUMBER_TYPES = frozenset({
    "DEC_NUMBER", "HEX_NUMBER", "BIN_NUMBER", "OCT_NUMBER",
    "FLOAT_NUMBER", "IMAG_NUMBER",
})

_SECTION_OPERATOR_TYPES = frozenset({
    "VBAR", "CIRCUMFLEX", "AMPER", "LSHIFT", "RSHIFT", "PLUS", "MINUS",
    "STAR", "AT", "SLASH", "PERCENT", "DOUBLESLASH",
})


class NomiPostLexer:
    """Postlexer that wraps PythonIndenter and inserts parser-aid tokens."""

    def __init__(self):
        self._indenter = PythonIndenter()

    @property
    def always_accept(self):
        return self._indenter.always_accept

    def process(self, stream):
        # TODO(NOMI-SUBSTRATE-032): Keep this postlexer as a declared
        # disambiguation layer with token-stream snapshots and perf budgets.
        # New syntax should add fixture-backed rewrite rules, not ad hoc scans.
        processed = list(self._indenter.process(stream))
        paren_pairs = self._paren_pairs(processed)
        arrow_parens = self._arrow_paren_indexes(processed, paren_pairs)
        case_colons = self._case_colon_indexes(processed)
        case_ifs = self._case_if_indexes(processed, case_colons)
        postfix_keywords = self._postfix_keyword_indexes(processed)
        prev = None
        for index, _ in enumerate(processed):
            token = self._rewrite_token(
                processed, index, paren_pairs, arrow_parens, case_colons, case_ifs,
                postfix_keywords,
            )
            if prev is not None and self._should_insert_star(prev, token):
                star = Token.new_borrow_pos("STAR", "*", prev)
                yield star
            yield token
            prev = token

    @staticmethod
    def _should_insert_star(prev, current):
        if prev.type not in _NUMBER_TYPES:
            return False
        if current.type not in ("NAME", "LPAR"):
            return False
        return prev.line == current.line and prev.end_column == current.column

    @classmethod
    def _rewrite_token(
        cls, tokens, index, paren_pairs, arrow_parens, case_colons,
        case_ifs, postfix_keywords,
    ):
        token = tokens[index]
        if index in arrow_parens:
            token_type = "_ARROW_LPAR" if token.type == "LPAR" else "_ARROW_RPAR"
            return Token.new_borrow_pos(token_type, token.value, token)
        if index in case_colons:
            return Token.new_borrow_pos("_CASE_COLON", token.value, token)
        if index in case_ifs:
            return Token.new_borrow_pos("_CASE_IF", token.value, token)
        if index in postfix_keywords:
            token_type = "_POSTFIX_IF" if token.type == "IF" else "_POSTFIX_UNLESS"
            return Token.new_borrow_pos(token_type, token.value, token)
        if cls._is_block_colon(tokens, index):
            return Token.new_borrow_pos("_BLOCK_COLON", token.value, token)
        if cls._is_section_operator(tokens, index, paren_pairs):
            return Token.new_borrow_pos("SECTION_OP", token.value, token)
        return token

    @staticmethod
    def _is_block_colon(tokens, index):
        token = tokens[index]
        return token.type == "COLON" and index + 1 < len(tokens) and tokens[index + 1].type == "_NEWLINE"

    @classmethod
    def _is_section_operator(cls, tokens, index, paren_pairs):
        token = tokens[index]
        if token.type not in _SECTION_OPERATOR_TYPES:
            return False
        if index > 0 and tokens[index - 1].type == "LPAR":
            return not cls._is_call_lpar(tokens, index - 1)
        if index + 1 < len(tokens) and tokens[index + 1].type == "RPAR":
            lpar = paren_pairs.get(index + 1)
            return lpar is not None and not cls._is_call_lpar(tokens, lpar)
        return False

    @staticmethod
    def _is_call_lpar(tokens, index):
        if index <= 0:
            return False
        return tokens[index - 1].type in {
            "NAME", "RPAR", "RSQB", "DOLLAR_NAME", "DOLLAR_HOLE",
            "DEC_NUMBER", "HEX_NUMBER", "BIN_NUMBER", "OCT_NUMBER",
            "FLOAT_NUMBER", "IMAG_NUMBER", "STRING", "LONG_STRING",
        }

    @staticmethod
    def _paren_pairs(tokens):
        stack = []
        pairs = {}
        for index, token in enumerate(tokens):
            if token.type == "LPAR":
                stack.append(index)
            elif token.type == "RPAR" and stack:
                start = stack.pop()
                pairs[start] = index
                pairs[index] = start
        return pairs

    @staticmethod
    def _arrow_paren_indexes(tokens, paren_pairs):
        pairs = set()
        for index, token in enumerate(tokens):
            if token.type != "RPAR":
                continue
            start = paren_pairs.get(index)
            next_type = tokens[index + 1].type if index + 1 < len(tokens) else None
            if start is not None and next_type == "_FAT_ARROW":
                pairs.add(start)
                pairs.add(index)
        return pairs

    @staticmethod
    def _case_colon_indexes(tokens):
        indexes = set()
        in_case = False
        depth = 0
        candidates = []
        for index, token in enumerate(tokens):
            if token.type in {"_NEWLINE", "_INDENT", "_DEDENT"}:
                if candidates:
                    indexes.add(NomiPostLexer._choose_case_colon(tokens, candidates))
                in_case = False
                depth = 0
                candidates = []
                continue
            if token.type == "CASE":
                in_case = True
                depth = 0
                candidates = []
                continue
            if not in_case:
                continue
            if token.type in {"LPAR", "LSQB", "LBRACE"}:
                depth += 1
            elif token.type in {"RPAR", "RSQB", "RBRACE"} and depth > 0:
                depth -= 1
            elif token.type == "COLON" and depth == 0:
                candidates.append(index)
        if candidates:
            indexes.add(NomiPostLexer._choose_case_colon(tokens, candidates))
        return indexes

    @staticmethod
    def _choose_case_colon(tokens, candidates):
        for index in candidates:
            next_type = tokens[index + 1].type if index + 1 < len(tokens) else None
            if next_type == "MATCH":
                return index
        return candidates[-1]

    @staticmethod
    def _postfix_keyword_indexes(tokens):
        indexes = set()
        flow_seen = False
        depth = 0
        candidate = None
        else_seen = False
        for index, token in enumerate(tokens):
            if token.type in {"_NEWLINE", "_INDENT", "_DEDENT"}:
                if flow_seen and candidate is not None and not else_seen:
                    indexes.add(candidate)
                flow_seen = False
                depth = 0
                candidate = None
                else_seen = False
                continue
            if token.type in {"RETURN", "RAISE", "BREAK", "CONTINUE"} and not flow_seen:
                flow_seen = True
                continue
            if not flow_seen:
                continue
            if token.type in {"LPAR", "LSQB", "LBRACE"}:
                depth += 1
            elif token.type in {"RPAR", "RSQB", "RBRACE"} and depth > 0:
                depth -= 1
            elif token.type in {"IF", "UNLESS"} and depth == 0 and candidate is None:
                candidate = index
            elif token.type == "ELSE" and depth == 0:
                else_seen = True
        if flow_seen and candidate is not None and not else_seen:
            indexes.add(candidate)
        return indexes

    @staticmethod
    def _case_if_indexes(tokens, case_colons):
        indexes = set()
        case_start = None
        depth = 0
        candidate = None
        else_seen = False
        for index, token in enumerate(tokens):
            if token.type in {"_NEWLINE", "_INDENT", "_DEDENT"}:
                case_start = None
                depth = 0
                candidate = None
                else_seen = False
                continue
            if token.type == "CASE":
                case_start = index
                depth = 0
                candidate = None
                else_seen = False
                continue
            if case_start is None:
                continue
            if index in case_colons:
                if candidate is not None and not else_seen:
                    indexes.add(candidate)
                case_start = None
                depth = 0
                candidate = None
                else_seen = False
                continue
            if token.type in {"LPAR", "LSQB", "LBRACE"}:
                depth += 1
            elif token.type in {"RPAR", "RSQB", "RBRACE"} and depth > 0:
                depth -= 1
            elif token.type == "IF" and depth == 0:
                candidate = index
            elif token.type == "ELSE" and depth == 0:
                else_seen = True
        return indexes
