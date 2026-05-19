"""Passive diagnostic and semantic-event records for runtime results."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True, slots=True)
class Diagnostic:
    """Structured diagnostic placeholder shared by runtime adapters."""

    message: str
    severity: str = "error"
    code: str | None = None
    span: Any | None = None
    details: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class RuntimeEvent:
    """Semantic event placeholder for future explain/trace output."""

    name: str
    payload: dict[str, Any] = field(default_factory=dict)
    span: Any | None = None


EMPTY_DIAGNOSTICS: tuple[Diagnostic, ...] = ()
EMPTY_EVENTS: tuple[RuntimeEvent, ...] = ()


@dataclass(slots=True)
class RuntimeEventCollector:
    """Mutable no-op sink that can be passed through future runtime stages."""

    diagnostics: list[Diagnostic] = field(default_factory=list)
    events: list[RuntimeEvent] = field(default_factory=list)

    def add_diagnostic(self, diagnostic: Diagnostic) -> None:
        self.diagnostics.append(diagnostic)

    def add_event(self, event: RuntimeEvent) -> None:
        self.events.append(event)

    def diagnostic(
        self,
        message: str,
        *,
        severity: str = "error",
        code: str | None = None,
        span: Any | None = None,
        details: dict[str, Any] | None = None,
    ) -> Diagnostic:
        diagnostic = Diagnostic(
            message=message,
            severity=severity,
            code=code,
            span=span,
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
    ) -> RuntimeEvent:
        event = RuntimeEvent(name=name, payload=payload or {}, span=span)
        self.add_event(event)
        return event

    def snapshot(self) -> tuple[tuple[Diagnostic, ...], tuple[RuntimeEvent, ...]]:
        return tuple(self.diagnostics), tuple(self.events)
