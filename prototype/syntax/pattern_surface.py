"""Versioned, frontend-neutral Pattern Surface contract.

Pattern Surface describes target Nomi patterns before Python AST or Core
lowering. The envelope retains the exact source, while every structural span
uses half-open UTF-8 byte offsets into that source.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Any, TypeAlias


PATTERN_SURFACE_SCHEMA = "nomi.pattern-surface"
PATTERN_SURFACE_VERSION = 1

INVALID_PATTERN_SYNTAX = "InvalidPatternSyntax"
DUPLICATE_PATTERN_CAPTURE = "DuplicatePatternCapture"
ALTERNATIVE_BINDING_MISMATCH = "AlternativeBindingMismatch"
MULTIPLE_PATTERN_REMAINDERS = "MultiplePatternRemainders"
MAP_PATTERN_REST_NOT_LAST = "MapPatternRestNotLast"
DUPLICATE_MAP_PATTERN_KEY = "DuplicateMapPatternKey"

RESERVED_PATTERN_NAMES = frozenset(
    {
        "actor",
        "and",
        "as",
        "async",
        "await",
        "break",
        "catch",
        "check",
        "class",
        "continue",
        "data",
        "defer",
        "effect",
        "else",
        "example",
        "extend",
        "false",
        "for",
        "from",
        "func",
        "generator",
        "if",
        "import",
        "in",
        "interface",
        "macro",
        "match",
        "none",
        "not",
        "note",
        "or",
        "panic",
        "protocol",
        "pub",
        "raise",
        "return",
        "set",
        "then",
        "trait",
        "true",
        "type",
        "uses",
        "var",
        "when",
        "where",
        "while",
        "with",
        "yield",
    }
)


@dataclass(frozen=True, slots=True)
class PatternSpan:
    """Half-open UTF-8 byte offsets into a Pattern Surface document."""

    start: int
    end: int

    def __post_init__(self) -> None:
        if self.start < 0 or self.end < self.start:
            raise ValueError(f"invalid pattern span: {self.start}..{self.end}")

    def to_dict(self) -> dict[str, int]:
        return {"start": self.start, "end": self.end}

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> PatternSpan:
        return cls(start=payload["start"], end=payload["end"])


class PatternSurfaceNode:
    """Marker base for the dedicated target pattern syntax category."""

    span: PatternSpan

    def to_dict(self) -> dict[str, Any]:
        raise NotImplementedError


@dataclass(frozen=True, slots=True)
class WildcardPattern(PatternSurfaceNode):
    span: PatternSpan

    def to_dict(self) -> dict[str, Any]:
        return {"kind": "WildcardPattern", "span": self.span.to_dict()}


@dataclass(frozen=True, slots=True)
class CapturePattern(PatternSurfaceNode):
    name: str
    span: PatternSpan

    def to_dict(self) -> dict[str, Any]:
        return {
            "kind": "CapturePattern",
            "name": self.name,
            "span": self.span.to_dict(),
        }


@dataclass(frozen=True, slots=True)
class LiteralPattern(PatternSurfaceNode):
    literal_kind: str
    value: str | bool | None
    lexeme: str
    span: PatternSpan

    def to_dict(self) -> dict[str, Any]:
        return {
            "kind": "LiteralPattern",
            "literal_kind": self.literal_kind,
            "value": self.value,
            "lexeme": self.lexeme,
            "span": self.span.to_dict(),
        }


@dataclass(frozen=True, slots=True)
class NominalPattern(PatternSurfaceNode):
    path: tuple[str, ...]
    arguments: tuple[Pattern, ...]
    payload_syntax: bool
    span: PatternSpan

    def to_dict(self) -> dict[str, Any]:
        return {
            "kind": "NominalPattern",
            "path": list(self.path),
            "arguments": [argument.to_dict() for argument in self.arguments],
            "payload_syntax": self.payload_syntax,
            "span": self.span.to_dict(),
        }


@dataclass(frozen=True, slots=True)
class TuplePattern(PatternSurfaceNode):
    items: tuple[Pattern, ...]
    span: PatternSpan

    def to_dict(self) -> dict[str, Any]:
        return {
            "kind": "TuplePattern",
            "items": [item.to_dict() for item in self.items],
            "span": self.span.to_dict(),
        }


@dataclass(frozen=True, slots=True)
class PatternRest:
    capture: str | None
    span: PatternSpan

    def to_dict(self) -> dict[str, Any]:
        return {"capture": self.capture, "span": self.span.to_dict()}


@dataclass(frozen=True, slots=True)
class ListPattern(PatternSurfaceNode):
    prefix: tuple[Pattern, ...]
    rest: PatternRest | None
    suffix: tuple[Pattern, ...]
    span: PatternSpan

    def to_dict(self) -> dict[str, Any]:
        return {
            "kind": "ListPattern",
            "prefix": [item.to_dict() for item in self.prefix],
            "rest": self.rest.to_dict() if self.rest is not None else None,
            "suffix": [item.to_dict() for item in self.suffix],
            "span": self.span.to_dict(),
        }


@dataclass(frozen=True, slots=True)
class MapPatternEntry:
    key: LiteralPattern
    pattern: Pattern
    span: PatternSpan

    def to_dict(self) -> dict[str, Any]:
        return {
            "key": self.key.to_dict(),
            "pattern": self.pattern.to_dict(),
            "span": self.span.to_dict(),
        }


@dataclass(frozen=True, slots=True)
class MapPattern(PatternSurfaceNode):
    entries: tuple[MapPatternEntry, ...]
    openness: str
    rest: PatternRest | None
    span: PatternSpan

    def to_dict(self) -> dict[str, Any]:
        return {
            "kind": "MapPattern",
            "entries": [entry.to_dict() for entry in self.entries],
            "openness": self.openness,
            "rest": self.rest.to_dict() if self.rest is not None else None,
            "span": self.span.to_dict(),
        }


@dataclass(frozen=True, slots=True)
class OrPattern(PatternSurfaceNode):
    alternatives: tuple[Pattern, ...]
    span: PatternSpan

    def to_dict(self) -> dict[str, Any]:
        return {
            "kind": "OrPattern",
            "alternatives": [item.to_dict() for item in self.alternatives],
            "span": self.span.to_dict(),
        }


@dataclass(frozen=True, slots=True)
class AsPattern(PatternSurfaceNode):
    pattern: Pattern
    capture: str
    capture_span: PatternSpan
    span: PatternSpan

    def to_dict(self) -> dict[str, Any]:
        return {
            "kind": "AsPattern",
            "pattern": self.pattern.to_dict(),
            "capture": self.capture,
            "capture_span": self.capture_span.to_dict(),
            "span": self.span.to_dict(),
        }


Pattern: TypeAlias = (
    WildcardPattern
    | CapturePattern
    | LiteralPattern
    | NominalPattern
    | TuplePattern
    | ListPattern
    | MapPattern
    | OrPattern
    | AsPattern
)


@dataclass(frozen=True, slots=True)
class PatternDiagnostic:
    code: str
    message: str
    span: PatternSpan

    def to_dict(self) -> dict[str, Any]:
        return {
            "code": self.code,
            "message": self.message,
            "span": self.span.to_dict(),
        }

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> PatternDiagnostic:
        return cls(
            code=payload["code"],
            message=payload["message"],
            span=PatternSpan.from_dict(payload["span"]),
        )


@dataclass(frozen=True, slots=True)
class PatternSurfaceDocument:
    source: str
    root: Pattern | None
    diagnostics: tuple[PatternDiagnostic, ...] = ()

    def __post_init__(self) -> None:
        if (self.root is None) == (not self.diagnostics):
            raise ValueError(
                "Pattern Surface requires either a root or at least one diagnostic"
            )
        byte_length = len(self.source.encode("utf-8"))
        spans = _all_spans(self.root) if self.root is not None else ()
        spans += tuple(diagnostic.span for diagnostic in self.diagnostics)
        if any(span.end > byte_length for span in spans):
            raise ValueError("Pattern Surface span extends beyond source")

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema": PATTERN_SURFACE_SCHEMA,
            "version": PATTERN_SURFACE_VERSION,
            "source": self.source,
            "root": self.root.to_dict() if self.root is not None else None,
            "diagnostics": [item.to_dict() for item in self.diagnostics],
        }

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> PatternSurfaceDocument:
        if payload.get("schema") != PATTERN_SURFACE_SCHEMA:
            raise ValueError("unknown Pattern Surface schema")
        if payload.get("version") != PATTERN_SURFACE_VERSION:
            raise ValueError("unsupported Pattern Surface version")
        root_payload = payload.get("root")
        return cls(
            source=payload["source"],
            root=pattern_from_dict(root_payload) if root_payload is not None else None,
            diagnostics=tuple(
                PatternDiagnostic.from_dict(item)
                for item in payload.get("diagnostics", ())
            ),
        )


class PatternSurfaceSyntaxError(SyntaxError):
    """Internal structured failure shared by Pattern Surface producers."""

    def __init__(
        self,
        code: str,
        span: PatternSpan,
        *,
        subject: str | None = None,
    ) -> None:
        self.code = code
        self.span = span
        self.subject = subject
        super().__init__(pattern_diagnostic_message(code, subject))

    def diagnostic(self) -> PatternDiagnostic:
        return PatternDiagnostic(self.code, str(self), self.span)


def pattern_diagnostic_message(code: str, subject: str | None = None) -> str:
    """Return the stable v1 text for a Pattern Surface diagnostic code."""

    if code == INVALID_PATTERN_SYNTAX:
        return "Pattern source does not conform to Pattern Surface v1."
    if code == DUPLICATE_PATTERN_CAPTURE:
        return f"Pattern capture `{subject}` appears more than once."
    if code == ALTERNATIVE_BINDING_MISMATCH:
        return "Or-pattern alternatives must capture the same names."
    if code == MULTIPLE_PATTERN_REMAINDERS:
        return "A collection pattern can contain at most one `..` remainder."
    if code == MAP_PATTERN_REST_NOT_LAST:
        return "A map `..` remainder must be the final entry."
    if code == DUPLICATE_MAP_PATTERN_KEY:
        return f"Map pattern key {subject} appears more than once."
    raise ValueError(f"unknown Pattern Surface diagnostic code: {code}")


def pattern_surface_document(
    source: str,
    root: Pattern,
) -> PatternSurfaceDocument:
    """Validate and package a successful frontend-produced pattern."""

    diagnostic = validate_pattern(root)
    if diagnostic is not None:
        return PatternSurfaceDocument(source, None, (diagnostic,))
    return PatternSurfaceDocument(source, root)


def pattern_surface_error(
    source: str,
    code: str,
    span: PatternSpan | None = None,
    *,
    subject: str | None = None,
) -> PatternSurfaceDocument:
    span = span or PatternSpan(0, len(source.encode("utf-8")))
    diagnostic = PatternDiagnostic(
        code=code,
        message=pattern_diagnostic_message(code, subject),
        span=span,
    )
    return PatternSurfaceDocument(source, None, (diagnostic,))


def validate_pattern(root: Pattern) -> PatternDiagnostic | None:
    """Validate capture and map-key invariants owned by the Surface contract."""

    try:
        _validate_capture_names(root)
        _binding_map(root)
        _validate_map_keys(root)
    except PatternSurfaceSyntaxError as error:
        return error.diagnostic()
    return None


def _validate_capture_names(root: Pattern) -> None:
    for node in _walk_patterns(root):
        if (
            isinstance(node, CapturePattern)
            and node.name in RESERVED_PATTERN_NAMES
        ):
            raise PatternSurfaceSyntaxError(INVALID_PATTERN_SYNTAX, node.span)
        if isinstance(node, AsPattern) and node.capture in RESERVED_PATTERN_NAMES:
            raise PatternSurfaceSyntaxError(
                INVALID_PATTERN_SYNTAX, node.capture_span
            )
        if (
            isinstance(node, (ListPattern, MapPattern))
            and node.rest is not None
            and node.rest.capture in RESERVED_PATTERN_NAMES
        ):
            raise PatternSurfaceSyntaxError(
                INVALID_PATTERN_SYNTAX, node.rest.span
            )


def capture_names(root: Pattern) -> tuple[str, ...]:
    """Return the deterministic capture set exposed by a valid pattern."""

    return tuple(sorted(_binding_map(root)))


def node_kinds(root: Pattern) -> tuple[str, ...]:
    """Return preorder node kinds for compact conformance expectations."""

    return tuple(type(node).__name__ for node in _walk_patterns(root))


def with_pattern_span(pattern: Pattern, span: PatternSpan) -> Pattern:
    """Widen a grouped pattern without introducing a semantic group node."""

    return replace(pattern, span=span)


def pattern_from_dict(payload: dict[str, Any]) -> Pattern:
    kind = payload["kind"]
    span = PatternSpan.from_dict(payload["span"])
    if kind == "WildcardPattern":
        return WildcardPattern(span)
    if kind == "CapturePattern":
        return CapturePattern(payload["name"], span)
    if kind == "LiteralPattern":
        return LiteralPattern(
            payload["literal_kind"], payload["value"], payload["lexeme"], span
        )
    if kind == "NominalPattern":
        return NominalPattern(
            tuple(payload["path"]),
            tuple(pattern_from_dict(item) for item in payload["arguments"]),
            payload["payload_syntax"],
            span,
        )
    if kind == "TuplePattern":
        return TuplePattern(
            tuple(pattern_from_dict(item) for item in payload["items"]), span
        )
    if kind == "ListPattern":
        rest = payload["rest"]
        return ListPattern(
            tuple(pattern_from_dict(item) for item in payload["prefix"]),
            _rest_from_dict(rest) if rest is not None else None,
            tuple(pattern_from_dict(item) for item in payload["suffix"]),
            span,
        )
    if kind == "MapPattern":
        rest = payload["rest"]
        return MapPattern(
            tuple(_map_entry_from_dict(item) for item in payload["entries"]),
            payload["openness"],
            _rest_from_dict(rest) if rest is not None else None,
            span,
        )
    if kind == "OrPattern":
        return OrPattern(
            tuple(pattern_from_dict(item) for item in payload["alternatives"]),
            span,
        )
    if kind == "AsPattern":
        return AsPattern(
            pattern_from_dict(payload["pattern"]),
            payload["capture"],
            PatternSpan.from_dict(payload["capture_span"]),
            span,
        )
    raise ValueError(f"unknown Pattern Surface node: {kind}")


def _rest_from_dict(payload: dict[str, Any]) -> PatternRest:
    return PatternRest(payload["capture"], PatternSpan.from_dict(payload["span"]))


def _map_entry_from_dict(payload: dict[str, Any]) -> MapPatternEntry:
    key = pattern_from_dict(payload["key"])
    if not isinstance(key, LiteralPattern):
        raise ValueError("map pattern key must be a LiteralPattern")
    return MapPatternEntry(
        key,
        pattern_from_dict(payload["pattern"]),
        PatternSpan.from_dict(payload["span"]),
    )


def _binding_map(root: Pattern) -> dict[str, PatternSpan]:
    if isinstance(root, CapturePattern):
        return {root.name: root.span}
    if isinstance(root, (WildcardPattern, LiteralPattern)):
        return {}
    if isinstance(root, OrPattern):
        alternatives = [_binding_map(item) for item in root.alternatives]
        expected = set(alternatives[0])
        if any(set(item) != expected for item in alternatives[1:]):
            raise PatternSurfaceSyntaxError(
                ALTERNATIVE_BINDING_MISMATCH, root.span
            )
        return alternatives[0]
    if isinstance(root, AsPattern):
        bindings = _binding_map(root.pattern)
        _merge_capture(bindings, root.capture, root.capture_span)
        return bindings

    bindings: dict[str, PatternSpan] = {}
    for child in _direct_children(root):
        for name, span in _binding_map(child).items():
            _merge_capture(bindings, name, span)
    rest = root.rest if isinstance(root, (ListPattern, MapPattern)) else None
    if rest is not None and rest.capture is not None:
        _merge_capture(bindings, rest.capture, rest.span)
    return bindings


def _merge_capture(
    bindings: dict[str, PatternSpan],
    name: str,
    span: PatternSpan,
) -> None:
    if name in bindings:
        raise PatternSurfaceSyntaxError(
            DUPLICATE_PATTERN_CAPTURE, span, subject=name
        )
    bindings[name] = span


def _validate_map_keys(root: Pattern) -> None:
    for node in _walk_patterns(root):
        if not isinstance(node, MapPattern):
            continue
        seen: set[tuple[str, str]] = set()
        for entry in node.entries:
            identity = (entry.key.literal_kind, repr(entry.key.value))
            if identity in seen:
                raise PatternSurfaceSyntaxError(
                    DUPLICATE_MAP_PATTERN_KEY,
                    entry.key.span,
                    subject=entry.key.lexeme,
                )
            seen.add(identity)


def _direct_children(root: Pattern) -> tuple[Pattern, ...]:
    if isinstance(root, NominalPattern):
        return root.arguments
    if isinstance(root, TuplePattern):
        return root.items
    if isinstance(root, ListPattern):
        return root.prefix + root.suffix
    if isinstance(root, MapPattern):
        return tuple(entry.pattern for entry in root.entries)
    if isinstance(root, OrPattern):
        return root.alternatives
    if isinstance(root, AsPattern):
        return (root.pattern,)
    return ()


def _walk_patterns(root: Pattern):
    yield root
    for child in _direct_children(root):
        yield from _walk_patterns(child)
    if isinstance(root, MapPattern):
        for entry in root.entries:
            yield entry.key


def _all_spans(root: Pattern) -> tuple[PatternSpan, ...]:
    spans: list[PatternSpan] = []
    for node in _walk_patterns(root):
        spans.append(node.span)
        if isinstance(node, AsPattern):
            spans.append(node.capture_span)
        if isinstance(node, (ListPattern, MapPattern)) and node.rest is not None:
            spans.append(node.rest.span)
        if isinstance(node, MapPattern):
            spans.extend(entry.span for entry in node.entries)
    return tuple(spans)
