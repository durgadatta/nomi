"""Passive diagnostic and semantic-event records for runtime results."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from lark.exceptions import UnexpectedInput


SEMANTIC_EVENT_KINDS = (
    "binding",
    "call",
    "block",
    "match",
    "decode",
    "pipeline",
    "query",
    "example",
    "capability",
    "rewrite",
)


@dataclass(frozen=True, slots=True)
class Diagnostic:
    """Structured diagnostic placeholder shared by runtime adapters."""

    message: str
    severity: str = "error"
    phase: str | None = None
    code: str | None = None
    span: Any | None = None
    source_excerpt: str | None = None
    node_type: str | None = None
    capability: str | None = None
    frontend: str | None = None
    backend: str | None = None
    details: dict[str, Any] = field(default_factory=dict)

    def to_record(self) -> dict[str, Any]:
        """Return the shared diagnostic JSON shape used by browser/runtime APIs."""
        return {
            "phase": self.phase,
            "severity": self.severity,
            "message": self.message,
            "span": self.span,
            "source_excerpt": self.source_excerpt,
            "node_type": self.node_type,
            "capability": self.capability,
            "frontend": self.frontend,
            "backend": self.backend,
            "code": self.code,
            "details": dict(self.details),
        }


@dataclass(frozen=True, slots=True)
class RuntimeEvent:
    """Structured event record for future explain/trace output.

    ``name``, ``payload``, and ``span`` are kept for compatibility with the
    first passive event shape.  New fields form the stable V1 record consumed by
    diagnostics, trace, frontend, and agent surfaces.
    """

    name: str
    payload: dict[str, Any] = field(default_factory=dict)
    span: Any | None = None
    id: str | None = None
    parent_id: str | None = None
    phase: str | None = None
    kind: str | None = None
    action: str | None = None
    feature: str | None = None
    operation: str | None = None
    source_span: Any | None = None
    subject: str | None = None
    value_summary: str | None = None
    capability: str | None = None
    failure_kind: str | None = None
    redaction: dict[str, Any] = field(default_factory=dict)
    next_step: str | None = None

    def to_record(self) -> dict[str, Any]:
        """Return the shared event JSON shape used by runtime/frontends."""
        return {
            "id": self.id,
            "parent_id": self.parent_id,
            "name": self.name,
            "phase": self.phase,
            "kind": self.kind,
            "action": self.action,
            "feature": self.feature,
            "operation": self.operation,
            "span": self.source_span if self.source_span is not None else self.span,
            "subject": self.subject,
            "value_summary": self.value_summary,
            "capability": self.capability,
            "failure_kind": self.failure_kind,
            "redaction": dict(self.redaction),
            "next_step": self.next_step,
            "payload": dict(self.payload),
        }


EMPTY_DIAGNOSTICS: tuple[Diagnostic, ...] = ()
EMPTY_EVENTS: tuple[RuntimeEvent, ...] = ()


@dataclass(slots=True)
class RuntimeEventCollector:
    """Mutable no-op sink that can be passed through future runtime stages."""

    diagnostics: list[Diagnostic] = field(default_factory=list)
    events: list[RuntimeEvent] = field(default_factory=list)
    _next_event_index: int = 1

    def add_diagnostic(self, diagnostic: Diagnostic) -> None:
        self.diagnostics.append(diagnostic)

    def add_event(self, event: RuntimeEvent) -> None:
        self.events.append(event)

    def diagnostic(
        self,
        message: str,
        *,
        severity: str = "error",
        phase: str | None = None,
        code: str | None = None,
        span: Any | None = None,
        source_excerpt: str | None = None,
        node_type: str | None = None,
        capability: str | None = None,
        frontend: str | None = None,
        backend: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> Diagnostic:
        diagnostic = Diagnostic(
            message=message,
            severity=severity,
            phase=phase,
            code=code,
            span=span,
            source_excerpt=source_excerpt,
            node_type=node_type,
            capability=capability,
            frontend=frontend,
            backend=backend,
            details=details or {},
        )
        self.add_diagnostic(diagnostic)
        return diagnostic

    def event(
        self,
        name: str,
        *,
        payload: dict[str, Any] | None = None,
        span: Any | None = None,
        id: str | None = None,
        parent_id: str | None = None,
        phase: str | None = None,
        kind: str | None = None,
        action: str | None = None,
        feature: str | None = None,
        operation: str | None = None,
        source_span: Any | None = None,
        subject: str | None = None,
        value_summary: str | None = None,
        capability: str | None = None,
        failure_kind: str | None = None,
        redaction: dict[str, Any] | None = None,
        next_step: str | None = None,
    ) -> RuntimeEvent:
        event_id = id or self._allocate_event_id()
        event = RuntimeEvent(
            name=name,
            payload=payload or {},
            span=span,
            id=event_id,
            parent_id=parent_id,
            phase=phase,
            kind=kind,
            action=action,
            feature=feature,
            operation=operation,
            source_span=source_span,
            subject=subject,
            value_summary=value_summary,
            capability=capability,
            failure_kind=failure_kind,
            redaction=redaction or {},
            next_step=next_step,
        )
        self.add_event(event)
        return event

    def semantic_event(
        self,
        kind: str,
        action: str = "observe",
        *,
        payload: dict[str, Any] | None = None,
        span: Any | None = None,
        feature: str | None = None,
        phase: str | None = None,
        subject: str | None = None,
        value_summary: str | None = None,
        capability: str | None = None,
        failure_kind: str | None = None,
        redaction: dict[str, Any] | None = None,
        next_step: str | None = None,
        parent_id: str | None = None,
    ) -> RuntimeEvent:
        """Record a no-op semantic event in the shared explanation vocabulary."""
        if kind not in SEMANTIC_EVENT_KINDS:
            allowed = ", ".join(SEMANTIC_EVENT_KINDS)
            raise ValueError(
                f"Unknown semantic event kind {kind!r}; expected one of: {allowed}"
            )

        event_payload = {
            "kind": kind,
            "action": action,
            "feature": feature,
            **(payload or {}),
        }
        return self.event(
            f"semantic.{kind}.{action}",
            payload=event_payload,
            span=span,
            parent_id=parent_id,
            phase=phase,
            kind=kind,
            action=action,
            feature=feature,
            operation=action,
            subject=subject,
            value_summary=value_summary,
            capability=capability,
            failure_kind=failure_kind,
            redaction=redaction,
            next_step=next_step,
        )

    def snapshot(self) -> tuple[tuple[Diagnostic, ...], tuple[RuntimeEvent, ...]]:
        return tuple(self.diagnostics), tuple(self.events)

    def _allocate_event_id(self) -> str:
        event_id = f"event-{self._next_event_index}"
        self._next_event_index += 1
        return event_id


def record_decode_event(
    collector: RuntimeEventCollector,
    action: str,
    *,
    phase: str = "eval",
    feature: str = "data-decode",
    subject: str | None = None,
    value_summary: str | None = None,
    capability: str = "data.decode",
    failure_kind: str | None = None,
    redaction: dict[str, Any] | None = None,
    next_step: str | None = None,
    payload: dict[str, Any] | None = None,
    parent_id: str | None = None,
) -> RuntimeEvent:
    """Record a decode semantic event using the shared explanation shape."""
    return collector.semantic_event(
        "decode",
        action,
        phase=phase,
        feature=feature,
        subject=subject,
        value_summary=value_summary,
        capability=capability,
        failure_kind=failure_kind,
        redaction=redaction,
        next_step=next_step,
        payload=payload,
        parent_id=parent_id,
    )


def record_match_event(
    collector: RuntimeEventCollector,
    action: str,
    *,
    phase: str = "eval",
    feature: str = "pattern-matching",
    subject: str | None = None,
    value_summary: str | None = None,
    capability: str = "pattern.match",
    failure_kind: str | None = None,
    redaction: dict[str, Any] | None = None,
    next_step: str | None = None,
    payload: dict[str, Any] | None = None,
    parent_id: str | None = None,
) -> RuntimeEvent:
    """Record a match semantic event using the shared explanation shape."""
    return collector.semantic_event(
        "match",
        action,
        phase=phase,
        feature=feature,
        subject=subject,
        value_summary=value_summary,
        capability=capability,
        failure_kind=failure_kind,
        redaction=redaction,
        next_step=next_step,
        payload=payload,
        parent_id=parent_id,
    )


def record_pipeline_event(
    collector: RuntimeEventCollector,
    action: str,
    *,
    phase: str = "eval",
    feature: str = "collection-flow",
    subject: str | None = None,
    value_summary: str | None = None,
    capability: str = "flow.pipeline",
    failure_kind: str | None = None,
    redaction: dict[str, Any] | None = None,
    next_step: str | None = None,
    payload: dict[str, Any] | None = None,
    parent_id: str | None = None,
) -> RuntimeEvent:
    """Record a pipeline semantic event using the shared explanation shape."""
    return collector.semantic_event(
        "pipeline",
        action,
        phase=phase,
        feature=feature,
        subject=subject,
        value_summary=value_summary,
        capability=capability,
        failure_kind=failure_kind,
        redaction=redaction,
        next_step=next_step,
        payload=payload,
        parent_id=parent_id,
    )


def record_block_policy_event(
    collector: RuntimeEventCollector,
    action: str,
    *,
    phase: str = "eval",
    feature: str = "block-policy",
    subject: str | None = None,
    value_summary: str | None = None,
    capability: str = "block.policy",
    failure_kind: str | None = None,
    redaction: dict[str, Any] | None = None,
    next_step: str | None = None,
    payload: dict[str, Any] | None = None,
    parent_id: str | None = None,
) -> RuntimeEvent:
    """Record a block-policy semantic event using the shared explanation shape."""
    return collector.semantic_event(
        "block",
        action,
        phase=phase,
        feature=feature,
        subject=subject,
        value_summary=value_summary,
        capability=capability,
        failure_kind=failure_kind,
        redaction=redaction,
        next_step=next_step,
        payload=payload,
        parent_id=parent_id,
    )


def record_capability_event(
    collector: RuntimeEventCollector,
    action: str,
    *,
    phase: str = "eval",
    feature: str = "state-capability",
    subject: str | None = None,
    value_summary: str | None = None,
    capability: str = "host.capability",
    failure_kind: str | None = None,
    redaction: dict[str, Any] | None = None,
    next_step: str | None = None,
    payload: dict[str, Any] | None = None,
    parent_id: str | None = None,
) -> RuntimeEvent:
    """Record a capability semantic event using the shared explanation shape."""
    return collector.semantic_event(
        "capability",
        action,
        phase=phase,
        feature=feature,
        subject=subject,
        value_summary=value_summary,
        capability=capability,
        failure_kind=failure_kind,
        redaction=redaction,
        next_step=next_step,
        payload=payload,
        parent_id=parent_id,
    )


def record_binding_error(
    collector: RuntimeEventCollector,
    error: Exception,
    *,
    phase: str = "eval",
    frontend: str | None = None,
    backend: str | None = None,
) -> None:
    """Record the first real structured runtime diagnostic/event family."""
    details = {
        "name": error.name,
        "value_repr": repr(error.value),
        "binding_kind": error.binding_kind,
        "constraint_expr": error.constraint_expr,
    }
    collector.diagnostic(
        str(error),
        phase=phase,
        code="NOMI-BINDING-CONSTRAINT",
        node_type="BindingError",
        capability="binding.constraints",
        frontend=frontend,
        backend=backend,
        details=details,
    )
    collector.semantic_event(
        "binding",
        "constraint_failed",
        phase=phase,
        feature="binding-constraints",
        subject=error.name,
        value_summary=repr(error.value),
        capability="binding.constraints",
        failure_kind="constraint",
        next_step="Adjust the value or constraint before committing the binding.",
        payload=details,
    )


def record_runtime_exception(
    collector: RuntimeEventCollector,
    error: Exception,
    *,
    phase: str = "eval",
    frontend: str | None = None,
    backend: str | None = None,
    source: str | None = None,
    filename: str | Path | None = None,
) -> None:
    """Prefer semantic diagnostics, otherwise preserve the failing phase/source."""
    known_error = _known_semantic_error(error)
    if _is_binding_error(known_error):
        record_binding_error(
            collector,
            known_error,
            phase=phase,
            frontend=frontend,
            backend=backend,
        )
        return

    chain = list(_exception_chain(error))
    parse_error = next(
        (item for item in chain if isinstance(item, (UnexpectedInput, SyntaxError))),
        None,
    )
    cause = parse_error or chain[-1]
    actual_phase = "parse" if parse_error is not None else phase
    if source is None and filename is not None:
        try:
            source = Path(filename).read_text(encoding="utf-8")
        except (OSError, UnicodeError):
            pass
    line = getattr(cause, "line", None) or getattr(cause, "lineno", None)
    column = getattr(cause, "column", None) or getattr(cause, "offset", None)
    # Lark's EOF token uses -1 rather than a source position.
    if parse_error is not None and source is not None and (not line or line < 1):
        lines = source.split("\n")
        line, column = len(lines), len(lines[-1]) + 1
    span = None
    excerpt = None
    if isinstance(line, int) and line > 0:
        column = column if isinstance(column, int) and column > 0 else 1
        span = {"line": line, "column": column, "coordinate_unit": "unicode-code-point"}
        if filename is not None:
            span["filename"] = str(filename)
        lines = source.splitlines() if source is not None else []
        if line <= len(lines):
            excerpt = lines[line - 1]
    collector.diagnostic(
        str(error),
        phase=actual_phase,
        code="NOMI-PARSE" if parse_error is not None else "NOMI-RUNTIME",
        span=span,
        source_excerpt=excerpt,
        node_type=type(cause).__name__,
        frontend=frontend,
        backend=backend,
        details={"exception_type": type(cause).__name__},
    )


def _exception_chain(error: Exception):
    seen: set[int] = set()
    current: BaseException | None = error
    while isinstance(current, Exception) and id(current) not in seen:
        seen.add(id(current))
        yield current
        current = current.__cause__ or current.__context__


def _known_semantic_error(error: Exception) -> Exception:
    """Return the first known Nomi semantic error in an exception chain."""
    seen: set[int] = set()
    current: BaseException | None = error
    while isinstance(current, Exception) and id(current) not in seen:
        seen.add(id(current))
        if _is_binding_error(current):
            return current
        current = current.__cause__ or current.__context__
    return error


def _is_binding_error(error: Exception) -> bool:
    return (
        type(error).__name__ == "BindingError"
        and hasattr(error, "name")
        and hasattr(error, "value")
        and hasattr(error, "binding_kind")
        and hasattr(error, "constraint_expr")
    )
