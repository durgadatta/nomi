"""Whitelist conversion at the tagged Core/library seam; preserves graph shape."""

from collections import deque

from prototype.runtime.backends.values import (
    BoolValue,
    IntValue,
    MappingValue,
    NilValue,
    SequenceValue,
    StrValue,
)
from prototype.runtime.report_boundary import (
    BoundaryRefusal,
    UNSUPPORTED,
    decode_data,
    encode_json,
    failure,
    parse_json,
    trim_text,
)


def structural_value(value, budget):
    copies, pending = {}, deque()

    def convert(item):
        if not budget.charge(1, category="work"):
            raise BoundaryRefusal(
                "NOMI-BOUNDARY-LIMIT",
                "bounded boundary work",
                "Boundary processing exceeds the configured work budget.",
            )
        kind = type(item)
        if kind is NilValue:
            return None
        if kind is BoolValue and type(item.value) is bool:
            return item.value
        if kind is IntValue and type(item.value) is int:
            return item.value
        if kind is StrValue and type(item.value) is str:
            return item.value
        if kind is SequenceValue and type(item.elements) is tuple:
            result = []
        elif kind is MappingValue and type(item.entries) is dict:
            result = {}
        else:
            return UNSUPPORTED
        if id(item) in copies:
            return copies[id(item)]
        copies[id(item)] = result
        pending.append((item, result))
        return result

    result = convert(value)
    while pending:
        item, target = pending.popleft()
        if type(item) is SequenceValue:
            for child in item.elements:
                target.append(convert(child))
        else:
            for key, child in item.entries.items():
                target[key] = convert(child)
    return result


ARITIES = {"parse_json": 1, "decode_data": 2, "encode_json": 1, "trim_text": 1}


def invoke(operation, args, budget):
    if len(args) != ARITIES[operation]:
        raise TypeError(f"{operation} expects {ARITIES[operation]} arguments")
    if operation in {"parse_json", "trim_text"}:
        if type(args[0]) is not StrValue or type(args[0].value) is not str:
            raise TypeError(f"{operation} expects Text")
        function = parse_json if operation == "parse_json" else trim_text
        return function(args[0].value, budget)
    if operation == "decode_data":
        if type(args[1]) is not StrValue or type(args[1].value) is not str:
            raise TypeError("decode_data schema name must be Text")
        if args[1].value not in {"report-options", "report-batch"}:
            raise ValueError("Choose a supported report schema.")
    try:
        value = structural_value(args[0], budget)
    except BoundaryRefusal as refusal:
        return failure(
            "decode" if operation == "decode_data" else "encode", refusal, budget=budget
        )
    if operation == "decode_data":
        return decode_data(value, args[1].value, budget)
    return encode_json(value, budget)
