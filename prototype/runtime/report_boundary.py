"""Closed report boundary library; target laws live in docs/design/synthesis.md.

The scanner never converts JSON numbers. Structural validation and the writer
charge occurrences, scalar inspections and emitted bytes before doing work.
The provisional allowance is owned by a run, not by a trusted-tree marker.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import cmp_to_key
import re
import sys
from typing import Any


JSON_NUMBER = re.compile(r"-?(?:0|[1-9][0-9]*)(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?\Z")
JSON_INTEGER = re.compile(r"-?(?:0|[1-9][0-9]*)\Z")
TRIM_SCALARS = " \t\n\v\f\r"
SCHEMAS = {
    "report-options": (("minimum_age", "integer", 13),),
    "report-batch": (("customers", "rows", None),),
    "report-row": (
        ("id", "nonblank", None),
        ("name", "nonblank", None),
        ("age", "integer", None),
    ),
}


@dataclass
class BoundaryBudget:
    input_bytes: int = 0
    work: int = 0
    output_bytes: int = 0
    input_limit: int = 256 * 1024
    aggregate_input_limit: int = 256 * 1024
    work_limit: int = 1_000_000
    output_limit: int = 64 * 1024
    depth_limit: int = 32
    node_limit: int = 8192
    diagnostic_limit: int = 16 * 1024
    error_limit: int = 64
    numeric_digit_limit: int = 4300

    def __post_init__(self):
        ceilings = {
            "input_limit": 256 * 1024,
            "aggregate_input_limit": 256 * 1024,
            "work_limit": 1_000_000,
            "output_limit": 64 * 1024,
            "depth_limit": 32,
            "node_limit": 8192,
            "diagnostic_limit": 16 * 1024,
            "error_limit": 64,
            "numeric_digit_limit": 4300,
        }
        for name, ceiling in ceilings.items():
            value = getattr(self, name)
            if type(value) is not int or value < 0:
                raise ValueError(f"{name} must be a non-negative Int")
            setattr(self, name, min(value, ceiling))
        self.diagnostic_limit = max(256, self.diagnostic_limit)
        host_digits = sys.get_int_max_str_digits()
        if host_digits:
            self.numeric_digit_limit = min(self.numeric_digit_limit, host_digits)

    def charge(self, amount: int, *, category: str) -> bool:
        field, limit = {
            "input": ("input_bytes", self.aggregate_input_limit),
            "work": ("work", self.work_limit),
            "output": ("output_bytes", self.output_limit),
        }[category]
        setattr(self, field, getattr(self, field) + amount)
        return getattr(self, field) <= limit

    def receipt(self) -> dict[str, Any]:
        return {
            "profile": "python-exact-int",
            "input_bytes": self.input_bytes,
            "work": self.work,
            "encoded_bytes": self.output_bytes,
            "numeric_digit_limit": self.numeric_digit_limit,
        }


class BoundaryRefusal(Exception):
    def __init__(self, code: str, expected: str, message: str, path=()):
        super().__init__(message)
        self.code, self.expected, self.message, self.path = (
            code,
            expected,
            message,
            list(path),
        )


class _DecodeStopped(Exception):
    pass


@dataclass(frozen=True)
class _Number:
    token: str


class UnsupportedValue:
    """Adapter refusal marker; cannot borrow structural map/list status."""


UNSUPPORTED = UnsupportedValue()


def _refuse(code, expected, message, path=()):
    raise BoundaryRefusal(code, expected, message, path)


def _limit(expected, message):
    _refuse("NOMI-BOUNDARY-LIMIT", expected, message)


def _work(budget: BoundaryBudget, amount=1):
    if not budget.charge(amount, category="work"):
        _limit(
            "bounded boundary work",
            "Boundary processing exceeds the configured work budget.",
        )


def _scalar(char: str, budget: BoundaryBudget, path=()):
    _work(budget)
    number = ord(char)
    if 0xD800 <= number <= 0xDFFF:
        _refuse(
            "NOMI-TEXT-INVALID",
            "Unicode scalar Text",
            "Replace the lone surrogate with valid Unicode text.",
            path,
        )
    return 1 if number < 0x80 else 2 if number < 0x800 else 3 if number < 0x10000 else 4


def _escape(char):
    escapes = {
        "\b": "\\b",
        "\t": "\\t",
        "\n": "\\n",
        "\f": "\\f",
        "\r": "\\r",
        '"': '\\"',
        "\\": "\\\\",
    }
    return escapes.get(char, f"\\u{ord(char):04x}" if ord(char) < 32 else char)


def _path_text(path):
    result = "$"
    for part in path:
        if type(part) is int:
            result += f"[{part}]"
        elif re.fullmatch(r"[A-Za-z_][A-Za-z_0-9]*", part):
            result += "." + part
        else:
            result += '["' + "".join(_escape(char) for char in part) + '"]'
    return result


def _error(code, path, expected, message):
    return {
        "code": code,
        "path": list(path),
        "path_text": _path_text(path),
        "expected": expected,
        "message": message,
    }


class _Sink:
    def __init__(self, budget, category, limit, collect=True):
        self.budget, self.category, self.limit = budget, category, limit
        self.size, self.parts = 0, [] if collect else None

    def put(self, text):
        size = sum(_scalar(char, self.budget) for char in text)
        _work(self.budget, size)
        self.size += size
        if self.size > self.limit:
            if self.category == "input":
                _limit(
                    "bounded input bytes", "Input exceeds the configured byte budget."
                )
            _limit(
                "bounded encoded output",
                "Encoded output exceeds the configured byte budget.",
            )
        if self.category and not self.budget.charge(size, category=self.category):
            if self.category == "input":
                _limit(
                    "bounded input bytes", "Input exceeds the configured byte budget."
                )
            _limit(
                "bounded encoded output",
                "Encoded output exceeds the configured byte budget.",
            )
        if self.parts is not None:
            self.parts.append(text)

    def quote(self, text, path=()):
        self.put('"')
        for char in text:
            _scalar(char, self.budget, path)
            self.put(_escape(char))
        self.put('"')


def _ordered_keys(keys, budget):
    def compare(left, right):
        for a, b in zip(left, right):
            _work(budget, 2)
            if a != b:
                return -1 if ord(a) < ord(b) else 1
        return (len(left) > len(right)) - (len(left) < len(right))

    return sorted(keys, key=cmp_to_key(compare))


def _write(value, sink, path=(), depth=0, active=None, nodes=None):
    active = set() if active is None else active
    nodes = [0] if nodes is None else nodes
    _work(sink.budget)
    nodes[0] += 1
    if nodes[0] > sink.budget.node_limit:
        _limit("bounded value tree", "Input exceeds a structural boundary limit.")
    kind = type(value)
    if value is None:
        sink.put("null")
    elif kind is bool:
        sink.put("true" if value else "false")
    elif kind is int:
        # Avoid asking the host to format an integer outside its declared capacity.
        digits = sink.budget.numeric_digit_limit
        if (
            digits == 0
            or value.bit_length() > digits * 3322 // 1000 + 1
            or abs(value) >= 10**digits
        ):
            _refuse(
                "NOMI-NUMERIC-CAPACITY",
                "Int within backend capacity",
                "Use a backend that supports this exact integer.",
                path,
            )
        try:
            token = str(value)
        except ValueError:
            _refuse(
                "NOMI-NUMERIC-CAPACITY",
                "Int within backend capacity",
                "Use a backend that supports this exact integer.",
                path,
            )
        if len(token.lstrip("-")) > sink.budget.numeric_digit_limit:
            _refuse(
                "NOMI-NUMERIC-CAPACITY",
                "Int within backend capacity",
                "Use a backend that supports this exact integer.",
                path,
            )
        _work(sink.budget, len(token))
        sink.put(token)
    elif kind is str:
        sink.quote(value, path)
    elif kind in (list, dict):
        if id(value) in active:
            _refuse(
                "NOMI-ENCODE-CYCLE",
                "acyclic structural value",
                "Remove the cycle from this value.",
                path,
            )
        if depth + 1 > sink.budget.depth_limit:
            _limit("bounded value tree", "Input exceeds a structural boundary limit.")
        active.add(id(value))
        try:
            if kind is list:
                sink.put("[")
                for index, item in enumerate(value):
                    if index:
                        sink.put(",")
                    _write(item, sink, (*path, index), depth + 1, active, nodes)
                sink.put("]")
            else:
                for key in value:
                    _work(sink.budget)
                    if type(key) is not str:
                        _refuse(
                            "NOMI-ENCODE-TYPE",
                            "JSON structural value",
                            "Provide only null, Bool, Int, Text, List, and text-keyed Map values.",
                            path,
                        )
                    for char in key:
                        _scalar(char, sink.budget, (*path, key))
                sink.put("{")
                for index, key in enumerate(_ordered_keys(value, sink.budget)):
                    if index:
                        sink.put(",")
                    sink.quote(key, (*path, key))
                    sink.put(":")
                    _write(value[key], sink, (*path, key), depth + 1, active, nodes)
                sink.put("}")
        finally:
            active.remove(id(value))
    else:
        _refuse(
            "NOMI-ENCODE-TYPE",
            "JSON structural value",
            "Provide only null, Bool, Int, Text, List, and text-keyed Map values.",
            path,
        )


def failure(kind, refusal=None, *, errors=None, complete=False, budget=None):
    budget = budget or BoundaryBudget()
    if errors is None:
        errors = [_error(refusal.code, refusal.path, refusal.expected, refusal.message)]
    result = {"ok": False, "kind": kind, "errors": errors, "complete": complete}
    # Diagnostic serialization has its own allowance and never spends export bytes.
    diagnostic_budget = BoundaryBudget(depth_limit=32, node_limit=8192)
    sink = _Sink(diagnostic_budget, None, budget.diagnostic_limit, collect=False)
    try:
        _write(result, sink)
    except BoundaryRefusal:
        return {
            "ok": False,
            "kind": kind,
            "errors": [
                _error(
                    "NOMI-BOUNDARY-LIMIT",
                    [],
                    "bounded diagnostic output",
                    "Validation stopped at the diagnostic budget.",
                )
            ],
            "complete": False,
        }
    return result


class _Scanner:
    def __init__(self, text, budget):
        self.text, self.budget, self.index, self.nodes = text, budget, 0, 0

    def peek(self):
        return self.text[self.index] if self.index < len(self.text) else ""

    def take(self):
        if self.index == len(self.text):
            self.syntax()
        _work(self.budget)
        char = self.text[self.index]
        self.index += 1
        return char

    def whitespace(self):
        while self.peek() and self.peek() in " \t\r\n":
            self.take()

    def syntax(self, message="Correct the JSON syntax."):
        _refuse("NOMI-JSON-SYNTAX", "one JSON value", message)

    def hexadecimal(self):
        chars = [self.take() for _ in range(4)]
        if any(char not in "0123456789abcdefABCDEF" for char in chars):
            self.syntax()
        return int("".join(chars), 16)

    def string(self, path):
        if self.take() != '"':
            self.syntax()
        chars = []
        escapes = {
            '"': '"',
            "\\": "\\",
            "/": "/",
            "b": "\b",
            "f": "\f",
            "n": "\n",
            "r": "\r",
            "t": "\t",
        }
        while True:
            char = self.take()
            if char == '"':
                return "".join(chars)
            if ord(char) < 32:
                self.syntax()
            if char != "\\":
                chars.append(char)
                continue
            escape = self.take()
            if escape in escapes:
                chars.append(escapes[escape])
            elif escape == "u":
                number = self.hexadecimal()
                if 0xD800 <= number <= 0xDBFF:
                    if self.peek() != "\\":
                        _refuse(
                            "NOMI-TEXT-INVALID",
                            "Unicode scalar Text",
                            "Replace the lone surrogate with valid Unicode text.",
                            path,
                        )
                    self.take()
                    if self.take() != "u":
                        _refuse(
                            "NOMI-TEXT-INVALID",
                            "Unicode scalar Text",
                            "Replace the lone surrogate with valid Unicode text.",
                            path,
                        )
                    low = self.hexadecimal()
                    if not 0xDC00 <= low <= 0xDFFF:
                        _refuse(
                            "NOMI-TEXT-INVALID",
                            "Unicode scalar Text",
                            "Replace the lone surrogate with valid Unicode text.",
                            path,
                        )
                    number = 0x10000 + ((number - 0xD800) << 10) + low - 0xDC00
                elif 0xDC00 <= number <= 0xDFFF:
                    _refuse(
                        "NOMI-TEXT-INVALID",
                        "Unicode scalar Text",
                        "Replace the lone surrogate with valid Unicode text.",
                        path,
                    )
                chars.append(chr(number))
            else:
                self.syntax()

    def value(self, path=(), depth=0):
        self.whitespace()
        self.nodes += 1
        _work(self.budget)
        if self.nodes > self.budget.node_limit:
            _limit("bounded value tree", "Input exceeds a structural boundary limit.")
        char = self.peek()
        if char == '"':
            return {"kind": "text", "value": self.string(path)}
        if char in ("[", "{"):
            if depth + 1 > self.budget.depth_limit:
                _limit(
                    "bounded value tree", "Input exceeds a structural boundary limit."
                )
            self.take()
            self.whitespace()
            closing = "]" if char == "[" else "}"
            values, seen = [], set()
            if self.peek() == closing:
                self.take()
                return (
                    {"kind": "list", "items": values}
                    if char == "["
                    else {"kind": "map", "entries": values}
                )
            while True:
                if char == "[":
                    values.append(self.value((*path, len(values)), depth + 1))
                else:
                    self.whitespace()
                    if self.peek() != '"':
                        self.syntax()
                    key = self.string(path)
                    _work(self.budget, len(key) + 1)
                    if key in seen:
                        _refuse(
                            "NOMI-JSON-DUPLICATE-KEY",
                            "unique object key",
                            "Remove the duplicate object key.",
                            (*path, key),
                        )
                    seen.add(key)
                    self.whitespace()
                    if self.take() != ":":
                        self.syntax()
                    values.append([key, self.value((*path, key), depth + 1)])
                self.whitespace()
                separator = self.take()
                if separator == closing:
                    break
                if separator != ",":
                    self.syntax()
            return (
                {"kind": "list", "items": values}
                if char == "["
                else {"kind": "map", "entries": values}
            )
        for token, node in (
            ("null", {"kind": "null"}),
            ("true", {"kind": "bool", "value": True}),
            ("false", {"kind": "bool", "value": False}),
        ):
            if self.text.startswith(token, self.index):
                for _ in token:
                    self.take()
                return node
        if char and char in "-0123456789":
            start = self.index
            while self.peek() and self.peek() in "-+0123456789.eE":
                self.take()
            token = self.text[start : self.index]
            _work(self.budget, len(token))
            if not JSON_NUMBER.fullmatch(token):
                self.syntax()
            return {"kind": "number", "token": token}
        self.syntax()


def parse_json(text: Any, budget: BoundaryBudget | None = None) -> dict[str, Any]:
    if type(text) is not str:
        raise TypeError("parse_json expects Text")
    budget = budget or BoundaryBudget()
    try:
        size = 0
        for char in text:
            amount = _scalar(char, budget)
            size += amount
            if size > budget.input_limit or not budget.charge(amount, category="input"):
                _limit(
                    "bounded input bytes", "Input exceeds the configured byte budget."
                )
        scanner = _Scanner(text, budget)
        root = scanner.value()
        scanner.whitespace()
        if scanner.index != len(text):
            scanner.syntax("Remove trailing content after the JSON value.")
        return {
            "ok": True,
            "value": {"schema": "nomi.json-value", "version": 1, "root": root},
        }
    except BoundaryRefusal as refusal:
        return failure("input-format", refusal, budget=budget)


def _validate_tree(tree, budget):
    def invalid(path=()):
        _refuse(
            "NOMI-VALUE-TREE",
            "nomi.json-value version 1",
            "Provide a supported structural Value tree.",
            path,
        )

    _work(budget)
    if (
        type(tree) is not dict
        or set(tree) != {"schema", "version", "root"}
        or tree["schema"] != "nomi.json-value"
        or type(tree["version"]) is not int
        or tree["version"] != 1
    ):
        invalid()
    sink = _Sink(budget, "input", budget.input_limit, collect=False)
    active, nodes = set(), [0]

    def visit(node, path, depth):
        _work(budget)
        nodes[0] += 1
        if nodes[0] > budget.node_limit:
            _limit("bounded value tree", "Input exceeds a structural boundary limit.")
        if type(node) is not dict or id(node) in active:
            invalid(path)
        _work(budget, len(node))
        kind = node.get("kind")
        fields = {
            "null": {"kind"},
            "bool": {"kind", "value"},
            "text": {"kind", "value"},
            "number": {"kind", "token"},
            "list": {"kind", "items"},
            "map": {"kind", "entries"},
        }
        if type(kind) is not str or kind not in fields or set(node) != fields[kind]:
            invalid(path)
        if kind in ("list", "map") and depth + 1 > budget.depth_limit:
            _limit("bounded value tree", "Input exceeds a structural boundary limit.")
        active.add(id(node))
        try:
            if kind == "null":
                sink.put("null")
                return None
            if kind == "bool":
                if type(node["value"]) is not bool:
                    invalid(path)
                sink.put("true" if node["value"] else "false")
                return node["value"]
            if kind == "text":
                if type(node["value"]) is not str:
                    invalid(path)
                sink.quote(node["value"], path)
                return node["value"]
            if kind == "number":
                token = node["token"]
                if type(token) is not str:
                    invalid(path)
                sink.put(token)
                _work(budget, len(token))
                if not JSON_NUMBER.fullmatch(token):
                    invalid(path)
                return _Number(token)
            if kind == "list":
                if type(node["items"]) is not list:
                    invalid(path)
                sink.put("[")
                output = []
                for index, child in enumerate(node["items"]):
                    if index:
                        sink.put(",")
                    output.append(visit(child, (*path, index), depth + 1))
                sink.put("]")
                return output
            if type(node["entries"]) is not list:
                invalid(path)
            sink.put("{")
            output = {}
            for index, entry in enumerate(node["entries"]):
                _work(budget)
                if (
                    type(entry) is not list
                    or len(entry) != 2
                    or type(entry[0]) is not str
                ):
                    invalid(path)
                key, child = entry
                for char in key:
                    _scalar(char, budget, (*path, key))
                _work(budget, len(key) + 1)
                if key in output:
                    invalid((*path, key))
                if index:
                    sink.put(",")
                sink.quote(key, (*path, key))
                sink.put(":")
                output[key] = visit(child, (*path, key), depth + 1)
            sink.put("}")
            return output
        finally:
            active.remove(id(node))

    return visit(tree["root"], (), 0)


def decode_data(
    tree: Any, schema_name: Any, budget: BoundaryBudget | None = None
) -> dict[str, Any]:
    if type(schema_name) is not str:
        raise TypeError("decode_data schema name must be Text")
    if schema_name not in ("report-options", "report-batch"):
        raise ValueError("Choose a supported report schema.")
    budget = budget or BoundaryBudget()
    errors, defaults = [], []

    def add(code, path, expected, message):
        if len(errors) == budget.error_limit:
            raise _DecodeStopped
        errors.append(_error(code, path, expected, message))

    def field(value, shape, path):
        _work(budget)
        if shape == "integer":
            if type(value) is not _Number:
                add(
                    "NOMI-DECODE-TYPE",
                    path,
                    "integer-form JSON number",
                    "Use an integer-form JSON number for this field.",
                )
                return None
            _work(budget, len(value.token))
            if not JSON_INTEGER.fullmatch(value.token):
                add(
                    "NOMI-DECODE-TYPE",
                    path,
                    "integer-form JSON number",
                    "Use an integer-form JSON number for this field.",
                )
                return None
            if len(value.token.lstrip("-")) > budget.numeric_digit_limit:
                _refuse(
                    "NOMI-NUMERIC-CAPACITY",
                    "Int within backend capacity",
                    "Use a backend that supports this exact integer.",
                    path,
                )
            _work(budget, len(value.token))
            number = int(value.token)
            if number < 0:
                add(
                    "NOMI-DECODE-CONSTRAINT",
                    path,
                    "non-negative Int",
                    "Use an integer greater than or equal to zero.",
                )
            return number
        if shape == "nonblank":
            if type(value) is not str:
                add("NOMI-DECODE-TYPE", path, "Text", "Use Text for this field.")
                return None
            for char in value:
                _scalar(char, budget, path)
            if not trim_text(value, budget):
                add(
                    "NOMI-DECODE-CONSTRAINT",
                    path,
                    "nonblank Text",
                    "Provide text that is nonblank after the declared trim.",
                )
            return value
        if type(value) is not list:
            add("NOMI-DECODE-TYPE", path, "list", "Use a list for customers.")
            return None
        if len(value) > 128:
            add(
                "NOMI-DECODE-CONSTRAINT",
                path,
                "at most 128 customers",
                "Reduce the number of customers.",
            )
            return None
        return [
            record(row, "report-row", (*path, index)) for index, row in enumerate(value)
        ]

    def record(value, descriptor, path):
        _work(budget)
        if type(value) is not dict:
            add(
                "NOMI-DECODE-TYPE",
                path,
                "object",
                "Use an object at this boundary."
                if not path
                else "Use an object for each customer.",
            )
            return None
        output, fields = {}, SCHEMAS[descriptor]
        names = {name for name, _, _ in fields}
        for name, shape, default in fields:
            _work(budget)
            child_path = (*path, name)
            if name not in value:
                if default is None:
                    add(
                        "NOMI-DECODE-MISSING",
                        child_path,
                        "required field",
                        "Provide the required field.",
                    )
                else:
                    output[name] = default
                    defaults.append(list(child_path))
            else:
                output[name] = field(value[name], shape, child_path)
        for key in _ordered_keys(value, budget):
            _work(budget, len(key) + 1)
            if key not in names:
                add(
                    "NOMI-DECODE-EXTRA",
                    (*path, key),
                    "declared field",
                    "Remove the unexpected field.",
                )
        return output

    try:
        value = _validate_tree(tree, budget)
        output = record(value, schema_name, ())
        if errors:
            return failure("decode", errors=errors, complete=True, budget=budget)
        return {"ok": True, "value": output, "defaults_applied": defaults}
    except _DecodeStopped:
        return failure("decode", errors=errors, complete=False, budget=budget)
    except BoundaryRefusal as refusal:
        return failure("decode", refusal, budget=budget)


def trim_text(text: Any, budget: BoundaryBudget | None = None) -> str:
    if type(text) is not str:
        raise TypeError("trim_text expects Text")
    budget = budget or BoundaryBudget()
    for char in text:
        _scalar(char, budget)
    first, last = 0, len(text)
    while first < last:
        _work(budget)
        if text[first] not in TRIM_SCALARS:
            break
        first += 1
    while first < last:
        _work(budget)
        if text[last - 1] not in TRIM_SCALARS:
            break
        last -= 1
    return text[first:last]


def encode_json(value: Any, budget: BoundaryBudget | None = None) -> dict[str, Any]:
    budget = budget or BoundaryBudget()
    sink = _Sink(budget, "output", budget.output_limit)
    try:
        _write(value, sink)
        return {"ok": True, "text": "".join(sink.parts)}
    except BoundaryRefusal as refusal:
        return failure("encode", refusal, budget=budget)


class ReportBoundaryProvider:
    """Ordinary hosted Nomi calls with a private allowance per source run."""

    def __init__(self):
        self.begin_run()

    def begin_run(self):
        self.budget = BoundaryBudget()

    def calls(self):
        return {
            "parse_json": lambda text: parse_json(text, self.budget),
            "decode_data": lambda tree, schema: decode_data(tree, schema, self.budget),
            "encode_json": lambda value: encode_json(value, self.budget),
            "trim_text": lambda text: trim_text(text, self.budget),
        }
