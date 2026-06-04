"""Public runtime facade for Nomi execution, inspection, and sessions."""

from .api import ExecutionResult, InspectionResult, create_session, execute, inspect
from .diagnostics import (
    SEMANTIC_EVENT_KINDS,
    Diagnostic,
    RuntimeEvent,
    RuntimeEventCollector,
)
from .pipeline import PipelineSpec, build_pipeline_spec
from .session import RuntimeCacheKey, RuntimeSession

__all__ = [
    "Diagnostic",
    "ExecutionResult",
    "InspectionResult",
    "PipelineSpec",
    "RuntimeEvent",
    "RuntimeEventCollector",
    "RuntimeCacheKey",
    "RuntimeSession",
    "SEMANTIC_EVENT_KINDS",
    "build_pipeline_spec",
    "create_session",
    "execute",
    "inspect",
]
