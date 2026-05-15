"""Custom postlexer: PythonIndenter + implicit multiplication token insertion.

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


class NomiPostLexer:
    """Postlexer that wraps PythonIndenter and inserts implicit ``*`` tokens."""

    def __init__(self):
        self._indenter = PythonIndenter()

    @property
    def always_accept(self):
        return self._indenter.always_accept

    def process(self, stream):
        processed = self._indenter.process(stream)
        prev = None
        for token in processed:
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
