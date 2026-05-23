"""JSON serialization for Nomi Core IR.

This is the backend-neutral Core IR boundary.  Python dataclasses are the
reference in-memory shape, but non-Python evaluators should consume the JSON
payload emitted here.
"""

from __future__ import annotations

import json
from dataclasses import fields, is_dataclass
from typing import Any

from prototype.syntax.core import (
    CORE_NODE_TYPES,
    CoreNode,
    CoreVerificationError,
    Literal,
    verify_core,
)


CORE_IR_JSON_SCHEMA = "nomi.core-ir"
CORE_IR_JSON_VERSION = 1

_CORE_NODE_BY_NAME = {
    node_type.__name__: node_type
    for node_type in CORE_NODE_TYPES
}


def core_to_json_payload(node: CoreNode) -> dict[str, Any]:
    """Return a JSON-compatible payload for a verified Core IR tree."""
    verify_core(node)
    return {
        "schema": CORE_IR_JSON_SCHEMA,
        "version": CORE_IR_JSON_VERSION,
        "root": _node_to_json(node),
    }


def core_to_json(node: CoreNode, *, indent: int | None = 2) -> str:
    """Serialize Core IR to a stable JSON string."""
    return json.dumps(core_to_json_payload(node), indent=indent, sort_keys=True)


def core_from_json_payload(payload: dict[str, Any]) -> CoreNode:
    """Load Core IR from a JSON-compatible payload."""
    if payload.get("schema") != CORE_IR_JSON_SCHEMA:
        raise CoreVerificationError(
            f"Unknown Core IR JSON schema {payload.get('schema')!r}"
        )
    if payload.get("version") != CORE_IR_JSON_VERSION:
        raise CoreVerificationError(
            f"Unsupported Core IR JSON version {payload.get('version')!r}"
        )
    root = _node_from_json(payload.get("root"))
    verify_core(root)
    return root


def core_from_json(source: str) -> CoreNode:
    """Deserialize a Core IR JSON string."""
    payload = json.loads(source)
    if not isinstance(payload, dict):
        raise CoreVerificationError("Core IR JSON payload must be an object")
    return core_from_json_payload(payload)


def _node_to_json(node: CoreNode) -> dict[str, Any]:
    if not is_dataclass(node):
        raise CoreVerificationError(
            f"Cannot serialize non-dataclass CoreNode {type(node).__name__}"
        )
    result: dict[str, Any] = {"type": type(node).__name__}
    for field in fields(node):
        if field.name == "span":
            continue
        result[field.name] = _value_to_json(getattr(node, field.name))
    if isinstance(node, Literal):
        result["value_type"] = _literal_value_type(node.value)
    return result


def _value_to_json(value: Any) -> Any:
    if value is None:
        return None
    if isinstance(value, CoreNode):
        return _node_to_json(value)
    if isinstance(value, tuple):
        return [_value_to_json(item) for item in value]
    if isinstance(value, list):
        return [_value_to_json(item) for item in value]
    if isinstance(value, (str, int, float, bool)):
        return value
    raise CoreVerificationError(
        f"Cannot serialize {type(value).__name__} in Core IR JSON"
    )


def _node_from_json(value: Any) -> CoreNode:
    if not isinstance(value, dict):
        raise CoreVerificationError(
            f"Core IR node must be an object, got {type(value).__name__}"
        )
    node_type_name = value.get("type")
    try:
        node_type = _CORE_NODE_BY_NAME[node_type_name]
    except KeyError as exc:
        raise CoreVerificationError(
            f"Unknown Core IR JSON node type {node_type_name!r}"
        ) from exc
    kwargs = {}
    for field in fields(node_type):
        if field.name == "span":
            continue
        if field.name in value:
            kwargs[field.name] = _value_from_json(value[field.name])
    return node_type(**kwargs)


def _value_from_json(value: Any) -> Any:
    if value is None:
        return None
    if isinstance(value, dict) and "type" in value:
        return _node_from_json(value)
    if isinstance(value, list):
        return tuple(_value_from_json(item) for item in value)
    if isinstance(value, (str, int, float, bool)):
        return value
    raise CoreVerificationError(
        f"Cannot deserialize {type(value).__name__} from Core IR JSON"
    )


def _literal_value_type(value: Any) -> str:
    if value is None:
        return "nil"
    if isinstance(value, bool):
        return "bool"
    if isinstance(value, int):
        return "int"
    if isinstance(value, float):
        return "float"
    if isinstance(value, str):
        return "str"
    return type(value).__name__
