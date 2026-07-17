"""Gated Lark producer for the target Pattern Surface v1 artifact."""

from __future__ import annotations

import ast
from pathlib import Path
from typing import Any

from lark import Lark, Token, Tree, UnexpectedInput

from ...syntax.pattern_surface import (
    INVALID_PATTERN_SYNTAX,
    MAP_PATTERN_REST_NOT_LAST,
    MULTIPLE_PATTERN_REMAINDERS,
    AsPattern,
    CapturePattern,
    ListPattern,
    LiteralPattern,
    MapPattern,
    MapPatternEntry,
    NominalPattern,
    OrPattern,
    Pattern,
    PatternRest,
    PatternSpan,
    PatternSurfaceDocument,
    PatternSurfaceSyntaxError,
    TuplePattern,
    WildcardPattern,
    pattern_surface_document,
    pattern_surface_error,
    with_pattern_span,
)


_GRAMMAR_PATH = Path(__file__).resolve().parents[2] / "grammar" / "pattern_surface.lark"
_PARSER: Lark | None = None


def parse_pattern_surface(source: str) -> PatternSurfaceDocument:
    """Parse one target pattern fragment without changing runnable syntax."""

    try:
        tree = _get_parser().parse(source)
        root = _PatternBuilder(source).build(tree)
        if not isinstance(root, Pattern):
            raise TypeError("Pattern Surface root is not a pattern")
    except PatternSurfaceSyntaxError as error:
        return pattern_surface_error(
            source,
            error.code,
            error.span,
            subject=error.subject,
        )
    except (UnexpectedInput, SyntaxError, TypeError, ValueError):
        return pattern_surface_error(source, INVALID_PATTERN_SYNTAX)
    return pattern_surface_document(source, root)


def pattern_surface_payload(source: str) -> dict[str, Any]:
    """Return the stable JSON-compatible Pattern Surface envelope."""

    return parse_pattern_surface(source).to_dict()


def _get_parser() -> Lark:
    global _PARSER
    if _PARSER is None:
        _PARSER = Lark(
            _GRAMMAR_PATH.read_text(encoding="utf-8"),
            parser="lalr",
            start="start",
            propagate_positions=True,
            maybe_placeholders=False,
        )
    return _PARSER


class _PatternBuilder:
    def __init__(self, source: str) -> None:
        self.source = source

    def build(self, value):
        if isinstance(value, Token):
            return str(value)
        if not isinstance(value, Tree):
            return value
        children = [self.build(child) for child in value.children]
        handler = getattr(self, f"build_{value.data}")
        return handler(value, children)

    def build_as_pattern(self, tree: Tree, children: list[Any]) -> Pattern:
        pattern = _require_pattern(children[0])
        if len(children) == 1:
            return pattern
        token = _require_token(tree.children[-1])
        return AsPattern(
            pattern=pattern,
            capture=str(token),
            capture_span=self._token_span(token),
            span=self._tree_span(tree),
        )

    def build_or_pattern(self, tree: Tree, children: list[Any]) -> Pattern:
        alternatives = tuple(_require_pattern(child) for child in children)
        if len(alternatives) == 1:
            return alternatives[0]
        return OrPattern(alternatives, self._tree_span(tree))

    def build_wildcard_pattern(self, tree: Tree, children: list[Any]) -> Pattern:
        return WildcardPattern(self._tree_span(tree))

    def build_capture_pattern(self, tree: Tree, children: list[Any]) -> Pattern:
        return CapturePattern(str(children[0]), self._tree_span(tree))

    def build_none_pattern(self, tree: Tree, children: list[Any]) -> Pattern:
        return self._literal(tree, "none", None)

    def build_true_pattern(self, tree: Tree, children: list[Any]) -> Pattern:
        return self._literal(tree, "boolean", True)

    def build_false_pattern(self, tree: Tree, children: list[Any]) -> Pattern:
        return self._literal(tree, "boolean", False)

    def build_integer_pattern(self, tree: Tree, children: list[Any]) -> Pattern:
        lexeme = self._source_for(tree)
        return LiteralPattern(
            "integer",
            lexeme.replace("_", ""),
            lexeme,
            self._tree_span(tree),
        )

    def build_text_pattern(self, tree: Tree, children: list[Any]) -> Pattern:
        lexeme = self._source_for(tree)
        # Transitional fenced subset; schema promotion requires a Nomi-owned
        # scalar literal codec shared with the Rust producer.
        value = ast.literal_eval(lexeme)
        if not isinstance(value, str):
            raise ValueError("text pattern did not decode to text")
        return LiteralPattern("text", value, lexeme, self._tree_span(tree))

    def build_bytes_pattern(self, tree: Tree, children: list[Any]) -> Pattern:
        lexeme = self._source_for(tree)
        value = ast.literal_eval(lexeme)
        if not isinstance(value, bytes):
            raise ValueError("bytes pattern did not decode to bytes")
        return LiteralPattern("bytes", value.hex(), lexeme, self._tree_span(tree))

    def build_nominal_path(self, tree: Tree, children: list[Any]) -> tuple[str, ...]:
        return tuple(str(child) for child in children)

    def build_nominal_name_pattern(
        self, tree: Tree, children: list[Any]
    ) -> Pattern:
        return NominalPattern(
            path=_require_path(children[0]),
            arguments=(),
            payload_syntax=False,
            span=self._tree_span(tree),
        )

    def build_nominal_call_pattern(
        self, tree: Tree, children: list[Any]
    ) -> Pattern:
        return NominalPattern(
            path=_require_path(children[0]),
            arguments=tuple(_require_pattern(child) for child in children[1:]),
            payload_syntax=True,
            span=self._tree_span(tree),
        )

    def build_empty_tuple_pattern(
        self, tree: Tree, children: list[Any]
    ) -> Pattern:
        return TuplePattern((), self._tree_span(tree))

    def build_tuple_pattern(self, tree: Tree, children: list[Any]) -> Pattern:
        return TuplePattern(
            tuple(_require_pattern(child) for child in children),
            self._tree_span(tree),
        )

    def build_grouped_pattern(self, tree: Tree, children: list[Any]) -> Pattern:
        return with_pattern_span(
            _require_pattern(children[0]), self._tree_span(tree)
        )

    def build_rest_pattern(self, tree: Tree, children: list[Any]) -> PatternRest:
        capture = str(children[0]) if children else None
        return PatternRest(capture, self._tree_span(tree))

    def build_list_pattern(self, tree: Tree, children: list[Any]) -> Pattern:
        rest_indexes = [
            index for index, child in enumerate(children) if isinstance(child, PatternRest)
        ]
        if len(rest_indexes) > 1:
            second = _require_rest(children[rest_indexes[1]])
            raise PatternSurfaceSyntaxError(
                MULTIPLE_PATTERN_REMAINDERS, second.span
            )
        if not rest_indexes:
            return ListPattern(
                tuple(_require_pattern(child) for child in children),
                None,
                (),
                self._tree_span(tree),
            )
        rest_index = rest_indexes[0]
        return ListPattern(
            tuple(_require_pattern(child) for child in children[:rest_index]),
            _require_rest(children[rest_index]),
            tuple(_require_pattern(child) for child in children[rest_index + 1 :]),
            self._tree_span(tree),
        )

    def build_map_entry(self, tree: Tree, children: list[Any]) -> MapPatternEntry:
        key = _require_literal(children[0])
        return MapPatternEntry(
            key=key,
            pattern=_require_pattern(children[1]),
            span=self._tree_span(tree),
        )

    def build_map_pattern(self, tree: Tree, children: list[Any]) -> Pattern:
        rest_indexes = [
            index for index, child in enumerate(children) if isinstance(child, PatternRest)
        ]
        if len(rest_indexes) > 1:
            second = _require_rest(children[rest_indexes[1]])
            raise PatternSurfaceSyntaxError(
                MULTIPLE_PATTERN_REMAINDERS, second.span
            )
        if rest_indexes and rest_indexes[0] != len(children) - 1:
            rest = _require_rest(children[rest_indexes[0]])
            raise PatternSurfaceSyntaxError(MAP_PATTERN_REST_NOT_LAST, rest.span)
        rest = _require_rest(children[-1]) if rest_indexes else None
        entry_children = children[:-1] if rest is not None else children
        return MapPattern(
            entries=tuple(_require_map_entry(child) for child in entry_children),
            openness="open" if rest is not None else "exact",
            rest=rest,
            span=self._tree_span(tree),
        )

    def _literal(
        self,
        tree: Tree,
        literal_kind: str,
        value: str | bool | None,
    ) -> LiteralPattern:
        return LiteralPattern(
            literal_kind, value, self._source_for(tree), self._tree_span(tree)
        )

    def _tree_span(self, tree: Tree) -> PatternSpan:
        return PatternSpan(
            self._byte_offset(tree.meta.start_pos),
            self._byte_offset(tree.meta.end_pos),
        )

    def _token_span(self, token: Token) -> PatternSpan:
        return PatternSpan(
            self._byte_offset(token.start_pos),
            self._byte_offset(token.end_pos),
        )

    def _source_for(self, tree: Tree) -> str:
        return self.source[tree.meta.start_pos : tree.meta.end_pos]

    def _byte_offset(self, character_offset: int) -> int:
        return len(self.source[:character_offset].encode("utf-8"))


def _require_pattern(value: Any) -> Pattern:
    if not isinstance(value, Pattern):
        raise TypeError(f"expected Pattern Surface node, got {type(value).__name__}")
    return value


def _require_literal(value: Any) -> LiteralPattern:
    if not isinstance(value, LiteralPattern):
        raise TypeError("map key is not a literal pattern")
    return value


def _require_rest(value: Any) -> PatternRest:
    if not isinstance(value, PatternRest):
        raise TypeError("expected Pattern Surface remainder")
    return value


def _require_map_entry(value: Any) -> MapPatternEntry:
    if not isinstance(value, MapPatternEntry):
        raise TypeError("expected Pattern Surface map entry")
    return value


def _require_path(value: Any) -> tuple[str, ...]:
    if not isinstance(value, tuple) or not all(isinstance(item, str) for item in value):
        raise TypeError("expected nominal path")
    return value


def _require_token(value: Any) -> Token:
    if not isinstance(value, Token):
        raise TypeError("expected source token")
    return value
