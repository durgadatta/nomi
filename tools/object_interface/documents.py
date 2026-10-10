"""Bounded inert artifacts. No host objects, discovery, or executable attributes."""

import hashlib
import json
from pathlib import Path
import re

MAX_BYTES = 1_000_000
MAX_NODES = 512
MAX_DEPTH = 64
IDENTIFIER = re.compile(r"[A-Za-z_][A-Za-z_0-9.-]{0,127}\Z")


class ContractError(ValueError):
    """A description, binding, or capability does not meet its contract."""


class Frozen:
    __slots__ = ("_sealed",)

    def __setattr__(self, name, value):
        if getattr(self, "_sealed", False):
            raise AttributeError("construct a new immutable revision")
        object.__setattr__(self, name, value)

    def __delattr__(self, name):
        raise AttributeError("construct a new immutable revision")


def encode(value):
    try:
        return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)
    except (ValueError, TypeError, RecursionError) as exc:
        raise ContractError(f"invalid artifact: {exc}") from exc


def digest(value):
    return hashlib.sha256(encode(value).encode()).hexdigest()


def inert(value, depth=0):
    if depth > MAX_DEPTH:
        raise ContractError("artifact exceeds nesting budget")
    if type(value) is dict:
        for key, child in value.items():
            if type(key) is not str:
                raise ContractError("record keys must be strings")
            inert(child, depth + 1)
    elif type(value) is list:
        for child in value:
            inert(child, depth + 1)
    elif type(value) not in (str, int, bool, type(None)):
        raise ContractError(
            "expected inert JSON; floats and host objects are unsupported"
        )


def snapshot(value):
    inert(value)
    text = encode(value)
    if len(text.encode()) > MAX_BYTES:
        raise ContractError("artifact exceeds byte budget")
    return text


def keys(value, required, where="artifact"):
    if type(value) is not dict or set(value) != set(required):
        raise ContractError(f"{where}: expected exactly {list(required)}")


def name(value, where="identity"):
    if type(value) is not str or not IDENTIFIER.fullmatch(value):
        raise ContractError(f"{where}: expected bounded identifier")
    return value


def names(values, where, nonempty=False):
    if type(values) is not list or (nonempty and not values):
        raise ContractError(f"{where}: expected reference list")
    for value in values:
        name(value, where)
    if len(values) != len(set(values)):
        raise ContractError(f"{where}: duplicate reference")
    return tuple(values)


def ordered(dependencies):
    """Bounded topological order, including disconnected named intermediates."""
    result, done = [], set()
    depths = {}
    while len(done) < len(dependencies):
        ready = [
            key
            for key, refs in dependencies.items()
            if key not in done and set(refs) <= done
        ]
        if not ready:
            missing = (
                set().union(*(set(refs) for refs in dependencies.values()))
                - dependencies.keys()
            )
            raise ContractError(
                f"unknown references {sorted(missing)}"
                if missing
                else "cyclic composition"
            )
        for key in ready:
            depths[key] = 1 + max((depths[ref] for ref in dependencies[key]), default=0)
            if depths[key] > MAX_DEPTH:
                raise ContractError("composition exceeds depth budget")
            result.append(key)
            done.add(key)
    return tuple(result)


SCHEMA_KINDS = {
    "text",
    "bool",
    "int",
    "positive_int",
    "record",
    "array",
    "text_list",
    "enum",
    "json",
    "null",
}


def schema(contract):
    if type(contract) is not dict or type(contract.get("kind")) is not str:
        raise ContractError("invalid value schema")
    kind = contract["kind"]
    keys(contract, ("kind", "values") if kind == "enum" else ("kind",), "value schema")
    if kind not in SCHEMA_KINDS:
        raise ContractError("unknown value schema kind")
    if kind == "enum" and (
        type(contract["values"]) is not list
        or not contract["values"]
        or any(type(item) is not str for item in contract["values"])
        or len(contract["values"]) != len(set(contract["values"]))
    ):
        raise ContractError("invalid enum values")


def value_check(value, contract, where):
    kind = contract["kind"]
    valid = {
        "text": lambda: type(value) is str,
        "bool": lambda: type(value) is bool,
        "int": lambda: type(value) is int,
        "positive_int": lambda: type(value) is int and value > 0,
        "record": lambda: type(value) is dict,
        "array": lambda: type(value) is list,
        "text_list": lambda: (
            type(value) is list and all(type(item) is str for item in value)
        ),
        "enum": lambda: type(value) is str and value in contract["values"],
        "json": lambda: True,
        "null": lambda: value is None,
    }
    if not valid[kind]():
        raise ContractError(f"{where}: expected {kind}")


def _pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ContractError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def load_document(path):
    with Path(path).open("rb") as stream:
        data = stream.read(MAX_BYTES + 1)
    if len(data) > MAX_BYTES:
        raise ContractError("artifact exceeds byte budget")
    try:
        document = json.loads(data, object_pairs_hook=_pairs)
        snapshot(document)
        return document
    except (ValueError, UnicodeError, RecursionError) as exc:
        raise ContractError(f"invalid JSON artifact: {exc}") from exc
