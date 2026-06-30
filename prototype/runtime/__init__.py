"""Public runtime facade for Nomi execution, inspection, and sessions."""

from .api import ExecutionResult, InspectionResult, create_session, execute, inspect
from .decode import DecodeError, DecodeErrorList
from .diagnostics import (
    SEMANTIC_EVENT_KINDS,
    Diagnostic,
    RuntimeEvent,
    RuntimeEventCollector,
    record_block_policy_event,
    record_capability_event,
    record_decode_event,
    record_match_event,
    record_pipeline_event,
)
from .pipeline import PipelineSpec, build_pipeline_spec
from .session import RuntimeCacheKey, RuntimeSession

__all__ = [
    "Diagnostic",
    "DecodeError",
    "DecodeErrorList",
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
    "record_block_policy_event",
    "record_capability_event",
    "record_decode_event",
    "record_match_event",
    "record_pipeline_event",
]
