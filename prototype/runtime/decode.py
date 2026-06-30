"""Passive value shapes for future data-boundary decode failures."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


FieldPathSegment = str | int


@dataclass(frozen=True, slots=True)
class DecodeError:
    """Structured evidence for one failed external-data field decode."""

    field_path: tuple[FieldPathSegment, ...] = ()
    source_identity: str | None = None
    expected: str | None = None
    raw_value_summary: str | None = None
    rule: str | None = None
    message: str | None = None
    redaction: dict[str, Any] = field(default_factory=dict)
    next_step: str | None = None
    span: Any | None = None

    def path_text(self) -> str:
        """Return a user-readable field path such as ``users[2].age``."""
        if not self.field_path:
            return ""

        text = ""
        for segment in self.field_path:
            if isinstance(segment, int):
                text += f"[{segment}]"
            elif not text:
                text = segment
            else:
                text += f".{segment}"
        return text

    def to_record(self) -> dict[str, Any]:
        return {
            "kind": "decode-error",
            "source_identity": self.source_identity,
            "field_path": list(self.field_path),
            "field_path_text": self.path_text(),
            "expected": self.expected,
            "raw_value_summary": self.raw_value_summary,
            "rule": self.rule,
            "message": self.message,
            "redaction": dict(self.redaction),
            "next_step": self.next_step,
            "span": self.span,
        }

    def to_event_payload(self) -> dict[str, Any]:
        return {
            "source_identity": self.source_identity,
            "field_path": list(self.field_path),
            "field_path_text": self.path_text(),
            "expected": self.expected,
            "rule": self.rule,
            "message": self.message,
        }


@dataclass(frozen=True, slots=True)
class DecodeErrorList:
    """Accumulated decode failures for one boundary crossing."""

    errors: tuple[DecodeError, ...] = ()
    source_identity: str | None = None

    def __bool__(self) -> bool:
        return False

    def add(self, error: DecodeError) -> "DecodeErrorList":
        source_identity = self.source_identity or error.source_identity
        return DecodeErrorList(
            errors=(*self.errors, error),
            source_identity=source_identity,
        )

    def to_record(self) -> dict[str, Any]:
        return {
            "kind": "decode-error-list",
            "source_identity": self.source_identity,
            "error_count": len(self.errors),
            "errors": [error.to_record() for error in self.errors],
        }
