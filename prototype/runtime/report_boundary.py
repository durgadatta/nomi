"""Closed, bounded structural boundary operations for the first report lab."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any


@dataclass
class BoundaryBudget:
    input_bytes: int = 0
    work: int = 0
    output_bytes: int = 0
    input_limit: int = 256 * 1024
    aggregate_input_limit: int = 256 * 1024
    work_limit: int = 1_000_000
    output_limit: int = 64 * 1024

    def charge(self, amount: int, *, category: str) -> bool:
        if category == "input":
            self.input_bytes += amount
            return self.input_bytes <= self.aggregate_input_limit
        if category == "work":
            self.work += amount
            return self.work <= self.work_limit
        if category == "output":
            self.output_bytes += amount
            return self.output_bytes <= self.output_limit
        raise ValueError(f"unknown boundary budget category: {category}")


def _path_text(path: list[str | int]) -> str:
    result = "$"
    for part in path:
        if isinstance(part, int):
            result += f"[{part}]"
        elif re.fullmatch(r"[A-Za-z_][A-Za-z_0-9]*", part):
            result += f".{part}"
        else:
            result += f"[{json.dumps(part, ensure_ascii=False, separators=(',', ':'))}]"
    return result


def _error(code: str, path: list[str | int], expected: str, message: str) -> dict[str, Any]:
    return {"code": code, "path": path, "path_text": _path_text(path), "expected": expected, "message": message}


def _failure(kind: str, error: dict[str, Any], complete: bool) -> dict[str, Any]:
    return {"ok": False, "kind": kind, "errors": [error], "complete": complete}


def _valid_text(text: str) -> bool:
    return not any(0xD800 <= ord(char) <= 0xDFFF for char in text)


class _DuplicateKey(Exception):
    def __init__(self, key: str):
        self.key = key


def _pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise _DuplicateKey(key)
        result[key] = value
    return result


def _tree(
    value: Any, path: list[str | int], budget: BoundaryBudget,
    nodes: list[int], depth: int = 0,
) -> dict[str, Any]:
    nodes[0] += 1
    if nodes[0] > 8192 or not budget.charge(1, category="work"):
        raise OverflowError("work")
    if value is None:
        return {"kind": "null"}
    if isinstance(value, bool):
        return {"kind": "bool", "value": value}
    if isinstance(value, str):
        if not _valid_text(value):
            raise UnicodeError
        if not budget.charge(len(value), category="work"):
            raise OverflowError("work")
        return {"kind": "text", "value": value}
    if isinstance(value, _Number):
        return {"kind": "number", "token": value.token}
    if isinstance(value, list):
        if depth >= 32:
            raise OverflowError("depth")
        return {"kind": "list", "items": [_tree(item, path + [i], budget, nodes, depth + 1) for i, item in enumerate(value)]}
    if isinstance(value, dict):
        if depth >= 32:
            raise OverflowError("depth")
        entries = []
        for key, item in value.items():
            if not _valid_text(key):
                raise UnicodeError
            if not budget.charge(len(key) + 1, category="work"):
                raise OverflowError("work")
            entries.append([key, _tree(item, path + [key], budget, nodes, depth + 1)])
        return {"kind": "map", "entries": entries}
    raise TypeError


@dataclass(frozen=True)
class _Number:
    token: str


def parse_json(text: Any, budget: BoundaryBudget | None = None) -> dict[str, Any]:
    budget = budget or BoundaryBudget()
    if not isinstance(text, str):
        return _failure("input-format", _error("NOMI-DECODE-TYPE", [], "Text", "Provide JSON as Text."), False)
    try:
        raw = text.encode("utf-8", "strict")
    except UnicodeEncodeError:
        return _failure("input-format", _error("NOMI-TEXT-INVALID", [], "Unicode scalar Text", "Replace the lone surrogate with valid Unicode text."), False)
    if len(raw) > 256 * 1024 or len(raw) > budget.input_limit or not budget.charge(len(raw), category="input"):
        return _failure("input-format", _error("NOMI-BOUNDARY-LIMIT", [], "bounded input bytes", "Input exceeds the configured byte budget."), False)
    if not budget.charge(len(text), category="work"):
        return _failure("input-format", _error("NOMI-BOUNDARY-LIMIT", [], "bounded boundary work", "Boundary processing exceeds the configured work budget."), False)
    try:
        value = json.loads(text, parse_int=_Number, parse_float=_Number, parse_constant=lambda _: (_ for _ in ()).throw(ValueError()), object_pairs_hook=_pairs)
    except _DuplicateKey as duplicate:
        path = [duplicate.key]
        return _failure("input-format", _error("NOMI-JSON-DUPLICATE-KEY", path, "unique object key", "Remove the duplicate object key."), False)
    except (json.JSONDecodeError, ValueError):
        trailing = False
        try:
            decoder = json.JSONDecoder()
            _, end = decoder.raw_decode(text.lstrip(" \t\r\n"))
            trailing = bool(text.lstrip(" \t\r\n")[end:].strip(" \t\r\n"))
        except (json.JSONDecodeError, ValueError):
            pass
        error = _error("NOMI-JSON-SYNTAX", [], "one JSON value", "Remove trailing content after the JSON value." if trailing else "Correct the JSON syntax.")
        return _failure("input-format", error, False)
    try:
        root = _tree(value, [], budget, [0])
    except UnicodeError:
        return _failure("input-format", _error("NOMI-TEXT-INVALID", [], "Unicode scalar Text", "Replace the lone surrogate with valid Unicode text."), False)
    except OverflowError:
        return _failure("input-format", _error("NOMI-BOUNDARY-LIMIT", [], "bounded value tree", "Input exceeds a structural boundary limit."), False)
    return {"ok": True, "value": {"schema": "nomi.json-value", "version": 1, "root": root}}


def _validate_tree(tree: Any, budget: BoundaryBudget, nodes: list[int], depth: int = 0) -> Any:
    if (
        depth > 32
        or not isinstance(tree, dict)
        or set(tree) != {"schema", "version", "root"}
        or tree.get("schema") != "nomi.json-value"
        or type(tree.get("version")) is not int
        or tree.get("version") != 1
    ):
        raise ValueError("tree")
    def visit(node: Any, level: int) -> Any:
        nodes[0] += 1
        if nodes[0] > 8192 or level > 32 or not budget.charge(1, category="work"):
            raise OverflowError
        if not isinstance(node, dict): raise ValueError("tree")
        kind = node.get("kind")
        if kind == "null" and set(node) == {"kind"}: return None
        if kind == "bool" and set(node) == {"kind", "value"} and isinstance(node["value"], bool): return node["value"]
        if kind == "text" and set(node) == {"kind", "value"} and isinstance(node["value"], str) and _valid_text(node["value"]): return node["value"]
        if kind == "number" and set(node) == {"kind", "token"} and isinstance(node["token"], str) and re.fullmatch(r"-?(?:0|[1-9][0-9]*)(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?", node["token"]): return _Number(node["token"])
        if kind == "list" and set(node) == {"kind", "items"} and isinstance(node["items"], list): return [visit(item, level + 1) for item in node["items"]]
        if kind == "map" and set(node) == {"kind", "entries"} and isinstance(node["entries"], list):
            result = {}
            for entry in node["entries"]:
                if not isinstance(entry, list) or len(entry) != 2 or not isinstance(entry[0], str) or not _valid_text(entry[0]) or entry[0] in result: raise ValueError("tree")
                result[entry[0]] = visit(entry[1], level + 1)
            return result
        raise ValueError("tree")
    return visit(tree["root"], depth)


def _tree_source(tree: Any) -> str:
    def source(node: dict[str, Any]) -> str:
        kind = node["kind"]
        if kind == "null": return "null"
        if kind == "bool": return "true" if node["value"] else "false"
        if kind == "text": return json.dumps(node["value"], ensure_ascii=False, separators=(",", ":"))
        if kind == "number": return node["token"]
        if kind == "list": return "[" + ",".join(source(item) for item in node["items"]) + "]"
        return "{" + ",".join(
            json.dumps(key, ensure_ascii=False, separators=(",", ":")) + ":" + source(value)
            for key, value in node["entries"]
        ) + "}"
    return source(tree["root"])


def _native_number(number: _Number) -> int | None:
    token = number.token
    if not re.fullmatch(r"-?(?:0|[1-9][0-9]*)", token):
        return None
    result = int(token)
    if result < 0 or result > 2**63 - 1:
        return result
    return result


def decode_data(tree: Any, schema_name: Any, budget: BoundaryBudget | None = None) -> dict[str, Any]:
    budget = budget or BoundaryBudget()
    try:
        value = _validate_tree(tree, budget, [0])
    except OverflowError:
        return _failure("decode", _error("NOMI-BOUNDARY-LIMIT", [], "bounded value tree", "Input exceeds a structural boundary limit."), False)
    except (ValueError, TypeError, KeyError):
        return _failure("decode", _error("NOMI-VALUE-TREE", [], "nomi.json-value version 1", "Provide a supported structural Value tree."), False)
    try:
        tree_bytes = len(_tree_source(tree).encode("utf-8", "strict"))
    except (UnicodeError, TypeError, KeyError):
        return _failure("decode", _error("NOMI-VALUE-TREE", [], "nomi.json-value version 1", "Provide a supported structural Value tree."), False)
    if tree_bytes > 256 * 1024 or tree_bytes > budget.input_limit or not budget.charge(tree_bytes, category="input"):
        return _failure("decode", _error("NOMI-BOUNDARY-LIMIT", [], "bounded input bytes", "Input exceeds the configured byte budget."), False)
    if schema_name not in {"report-options", "report-batch"}:
        return _failure("decode", _error("NOMI-DECODE-TYPE", [], "known schema name", "Choose a supported report schema."), False)
    errors: list[dict[str, Any]] = []
    defaults: list[list[str | int]] = []
    truncated = [False]
    def add(code: str, path: list[str | int], expected: str, message: str):
        if len(errors) < 64:
            errors.append(_error(code, path, expected, message))
        else:
            truncated[0] = True
    if not isinstance(value, dict):
        add("NOMI-DECODE-TYPE", [], "object", "Use an object at this boundary.")
    else:
        allowed = ("minimum_age",) if schema_name == "report-options" else ("customers",)
        for key in value:
            if key not in allowed: add("NOMI-DECODE-EXTRA", [key], "declared field", "Remove the unexpected field.")
        for key in allowed:
            if key not in value:
                if schema_name == "report-options" and key == "minimum_age":
                    value[key] = _Number("13"); defaults.append([key])
                else: add("NOMI-DECODE-MISSING", [key], "required field", "Provide the required field.")
        def integer(item: Any, path: list[str | int], expected: str) -> int | None:
            if not isinstance(item, _Number):
                add("NOMI-DECODE-TYPE", path, expected, "Use an integer-form JSON number for this field."); return None
            if not re.fullmatch(r"-?(?:0|[1-9][0-9]*)", item.token):
                add("NOMI-DECODE-TYPE", path, expected, "Use an integer-form JSON number for this field."); return None
            number = int(item.token)
            if number < 0:
                add("NOMI-DECODE-CONSTRAINT", path, "non-negative Int", "Use an integer greater than or equal to zero."); return None
            return number
        if schema_name == "report-options":
            age = integer(value.get("minimum_age", _Number("13")), ["minimum_age"], "integer-form JSON number")
            output = {"minimum_age": age} if age is not None else None
        else:
            rows = value.get("customers")
            output_rows = []
            if rows is not None and not isinstance(rows, list): add("NOMI-DECODE-TYPE", ["customers"], "list", "Use a list for customers.")
            elif isinstance(rows, list):
                if len(rows) > 128: add("NOMI-BOUNDARY-LIMIT", ["customers"], "at most 128 customers", "Reduce the number of customers.")
                for index, row in enumerate(rows[:128]):
                    path = ["customers", index]
                    if not isinstance(row, dict):
                        add("NOMI-DECODE-TYPE", path, "object", "Use an object for each customer."); continue
                    for key in row:
                        if key not in {"id", "name", "age"}: add("NOMI-DECODE-EXTRA", path + [key], "declared field", "Remove the unexpected field.")
                    record = {}
                    for key in ("id", "name"):
                        field = row.get(key)
                        if key not in row: add("NOMI-DECODE-MISSING", path + [key], "required field", "Provide the required field.")
                        elif not isinstance(field, str): add("NOMI-DECODE-TYPE", path + [key], "Text", "Use Text for this field.")
                        elif not field.strip(" \t\r\n") or not _valid_text(field): add("NOMI-DECODE-CONSTRAINT" if _valid_text(field) else "NOMI-TEXT-INVALID", path + [key], "nonblank Text", "Provide text that is nonblank after the declared trim.")
                        else: record[key] = field
                    if "age" not in row: add("NOMI-DECODE-MISSING", path + ["age"], "required field", "Provide the required field.")
                    else:
                        age = integer(row["age"], path + ["age"], "integer-form JSON number")
                        if age is not None: record["age"] = age
                    if len(record) == 3: output_rows.append(record)
            output = {"customers": output_rows} if not errors else None
    if errors:
        complete = not truncated[0] and not any(
            item["code"] in {"NOMI-BOUNDARY-LIMIT", "NOMI-NUMERIC-CAPACITY"}
            for item in errors
        )
        return {"ok": False, "kind": "decode", "errors": errors[:64], "complete": complete}
    return {"ok": True, "value": output, "defaults_applied": defaults}


def trim_text(text: Any) -> str:
    if not isinstance(text, str): raise TypeError("trim_text expects Text")
    if not _valid_text(text): raise ValueError("NOMI-TEXT-INVALID")
    return text.strip(" \t\r\n\v\f")


def encode_json(value: Any, budget: BoundaryBudget | None = None) -> dict[str, Any]:
    budget = budget or BoundaryBudget()
    active: set[int] = set()
    def emit(item: Any, path: list[str | int]) -> str:
        if not budget.charge(1, category="work"): raise OverflowError
        if item is None: return "null"
        if item is True: return "true"
        if item is False: return "false"
        if isinstance(item, int): return str(item)
        if isinstance(item, str):
            if not _valid_text(item): raise UnicodeError
            return json.dumps(item, ensure_ascii=False, separators=(",", ":"))
        if isinstance(item, (list, dict)):
            identity = id(item)
            if identity in active: raise RecursionError
            active.add(identity)
            try:
                if isinstance(item, list): result = "[" + ",".join(emit(v, path + [i]) for i, v in enumerate(item)) + "]"
                else:
                    if any(not isinstance(key, str) for key in item): raise TypeError
                    keys = sorted(item, key=lambda key: tuple(map(ord, key)))
                    result = "{" + ",".join(emit(key, path + [key]) + ":" + emit(item[key], path + [key]) for key in keys) + "}"
                return result
            finally: active.remove(identity)
        raise TypeError
    try:
        text = emit(value, [])
    except RecursionError:
        return _failure("encode", _error("NOMI-ENCODE-CYCLE", [], "acyclic structural value", "Remove the cycle from this value."), False)
    except UnicodeError:
        return _failure("encode", _error("NOMI-TEXT-INVALID", [], "Unicode scalar Text", "Replace the lone surrogate with valid Unicode text."), False)
    except OverflowError:
        return _failure("encode", _error("NOMI-BOUNDARY-LIMIT", [], "bounded boundary work", "Boundary processing exceeds the configured work budget."), False)
    except (TypeError, ValueError):
        return _failure("encode", _error("NOMI-ENCODE-TYPE", [], "JSON structural value", "Provide only null, Bool, Int, Text, List, and text-keyed Map values."), False)
    size = len(text.encode("utf-8"))
    if size > 64 * 1024 or not budget.charge(size, category="output"):
        return _failure("encode", _error("NOMI-BOUNDARY-LIMIT", [], "bounded encoded output", "Encoded output exceeds the configured byte budget."), False)
    return {"ok": True, "text": text}
