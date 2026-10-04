"""Bounded Python-host and original generic-operation counterexamples.

No Nomi typechecker, foreign engine, remote cache, scheduler or human execution.
"""

import argparse
from datetime import date
from functools import cache, reduce
from itertools import accumulate, repeat
import json
from pathlib import Path
import platform


def map_trace(*, fused, fail_at=None):
    events = []

    def first(value):
        events.append(f"f:{value}")
        if value == fail_at:
            raise ValueError("first_failed")
        return value * 2

    def second(value):
        events.append(f"g:{value}")
        return value + 1

    try:
        if fused:
            values = [second(first(value)) for value in [1, 2, 3]]
        else:
            intermediate = [first(value) for value in [1, 2, 3]]
            values = [second(value) for value in intermediate]
        return {"values": values, "events": events}
    except ValueError as error:
        return {"error": str(error), "events": events}


def map_fusion():
    strict = map_trace(fused=False)
    fused = map_trace(fused=True)
    assert strict["values"] == fused["values"] == [3, 5, 7]
    assert strict["events"] != fused["events"]
    strict_failure = map_trace(fused=False, fail_at=2)
    fused_failure = map_trace(fused=True, fail_at=2)
    assert strict_failure["events"] == ["f:1", "f:2"]
    assert fused_failure["events"] == ["f:1", "g:2", "f:2"]
    return {
        "strict": strict,
        "fused": fused,
        "strict_failure": strict_failure,
        "fused_failure": fused_failure,
        "limit": "three integer inputs and observable callback trace/failure models; not Nomi fusion or a pure-callback proof",
    }


def fold_and_scan():
    def subtract(left, right):
        return left - right

    left = reduce(subtract, [1, 2], 10)
    right = 10
    for value in reversed([1, 2]):
        right = subtract(value, right)
    empty_error = None
    try:
        reduce(subtract, [])
    except TypeError as error:
        empty_error = type(error).__name__
    states = list(accumulate([1, 2], initial=0))
    assert (left, right, empty_error, states) == (7, 9, "TypeError", [0, 1, 3])
    assert reduce(subtract, [], 10) == 10
    return {
        "left_subtract": left,
        "right_subtract": right,
        "empty_unseeded_error": empty_error,
        "empty_seeded": 10,
        "seeded_scan": states,
        "empty_seeded_scan": list(accumulate([], initial=0)),
        "limit": "functools/itertools and an explicit finite right fold; not Common Lisp, Haskell, Wolfram or Nomi execution",
    }


def reassociation():
    subtraction = [(8 - 3) - 1, 8 - (3 - 1)]
    floating = [(1e16 + -1e16) + 1.0, 1e16 + (-1e16 + 1.0)]
    assert subtraction == [4, 6] and floating == [1.0, 0.0]
    return {
        "subtraction": subtraction,
        "floating_addition": floating,
        "limit": "two chosen Python arithmetic examples; no parallel engine, portable numeric profile or general algebra proof",
    }


def assess_rows(*, fail_fast):
    invoked = []
    rows = []
    for value in [1, -1, 3]:
        invoked.append(value)
        result = ("err", value) if value < 0 else ("ok", value * 2)
        if fail_fast and result[0] == "err":
            return {"outcome": result, "invoked": invoked}
        rows.append(result)
    return {"outcome": ("ok", rows) if fail_fast else rows, "invoked": invoked}


def row_outcomes():
    independent = assess_rows(fail_fast=False)
    fail_fast = assess_rows(fail_fast=True)
    assert independent["invoked"] == [1, -1, 3]
    assert fail_fast["invoked"] == [1, -1]
    return {
        "independent": independent,
        "fail_fast": fail_fast,
        "limit": "original tuple-tagged result and finite traversal policy; not Nomi Result, generic typing or rollback",
    }


def tap(value, observer):
    observer(value)
    return value


def tap_outcomes():
    value = [1, 2]
    returned = tap(value, lambda item: item.append(3))
    events = []

    def fail(item):
        events.append("observer")
        raise ValueError("observer_failed")

    try:
        tap(value, fail)
        events.append("downstream")
    except ValueError as error:
        failure = str(error)
    assert returned is value and value == [1, 2, 3]
    assert events == ["observer"]
    return {
        "same_reference": returned is value,
        "after_mutation": value,
        "failure": failure,
        "events": events,
        "limit": "original immediate tap with a mutable List and Python exception; no logging/RxJS/Lodash library or Nomi effect enforcement",
    }


def lazy_demand():
    invoked = []

    def double(value):
        invoked.append(value)
        return value * 2

    iterator = map(double, [1, 2, 3])
    construction = invoked.copy()
    first = next(iterator)
    partial = invoked.copy()
    remainder = list(iterator)
    assert construction == [] and partial == [1] and invoked == [1, 2, 3]
    return {
        "construction_calls": construction,
        "first": first,
        "partial_calls": partial,
        "remainder": remainder,
        "all_calls": invoked,
        "limit": "Python map demand only; not Nomi Stream, callback retention typing, Rust adapters or Java stage elision",
    }


def repetition():
    value = []
    repeated = list(repeat(value, 3))
    repeated[0].append(1)
    fresh = [[] for _ in range(3)]
    state = 1
    history = [state]
    for _ in range(3):
        state *= 2
        history.append(state)
    assert repeated == [[1], [1], [1]] and history == [1, 2, 4, 8]
    return {
        "repeated_share_reference": all(item is value for item in repeated),
        "repeated_after_mutation": repeated,
        "fresh_share_reference": fresh[0] is fresh[1],
        "iteration_history": history,
        "zero_repeat": list(repeat(value, 0)),
        "limit": "itertools.repeat and three original finite constructions; no remote effects, retry policy or freshness type proof",
    }


def iterate_bounded(step, seed, budget, *, same=None):
    if type(budget) is not int or budget < 0:
        raise ValueError("budget must be a nonnegative integer")
    if type(seed) is not int:
        raise ValueError("this model requires integer states")
    compare = (lambda old, new: old == new) if same is None else same
    history = [seed]
    current = seed
    for count in range(1, budget + 1):
        updated = step(current)
        if type(updated) is not int:
            raise ValueError("this model requires integer states")
        stopped = compare(current, updated)
        if type(stopped) is not bool:
            raise ValueError("stopping test must return Bool")
        if stopped:
            return {"reason": "criterion_satisfied", "value": updated, "steps": count}
        if updated in history:
            return {"reason": "cycle", "value": updated, "steps": count}
        history.append(updated)
        current = updated
    return {"reason": "budget_exhausted", "value": current, "steps": budget}


def stopping_policies():
    stable = iterate_bounded(lambda value: min(value + 1, 3), 0, 8)
    cycle = iterate_bounded(lambda value: 1 - value, 0, 8)
    growth = iterate_bounded(lambda value: value + 1, 0, 3)
    loose_test = iterate_bounded(
        lambda value: value + 1, 0, 3, same=lambda old, new: abs(old - new) <= 1
    )
    assert stable == {"reason": "criterion_satisfied", "value": 3, "steps": 4}
    assert cycle == {"reason": "cycle", "value": 0, "steps": 2}
    assert growth == {"reason": "budget_exhausted", "value": 3, "steps": 3}
    assert loose_test == {"reason": "criterion_satisfied", "value": 1, "steps": 1}
    return {
        "stable": stable,
        "cycle": cycle,
        "growth": growth,
        "loose_test": loose_test,
        "zero_budget": iterate_bounded(lambda value: value + 1, 0, 0),
        "limit": "bounded integer model, equality-based finite history and supplied comparison; no convergence proof, numerical solver, cancellation or termination checker",
    }


def caching_context():
    context = {"factor": 2}

    def computation(value):
        return value * context["factor"]

    cached = cache(computation)
    first = cached(2)
    context["factor"] = 10
    stale = cached(2)
    direct = computation(2)
    outside_events = []
    inside_events = []
    cached_value = cache(lambda value: value * 2)
    cached_observation = cache(
        lambda value: tap(value * 2, lambda item: inside_events.append(item))
    )
    for _ in range(2):
        tap(cached_value(2), lambda item: outside_events.append(item))
        cached_observation(2)
    assert [first, stale, direct] == [4, 4, 20]
    assert outside_events == [4, 4] and inside_events == [4]
    return {
        "initial_stale_direct": [first, stale, direct],
        "tap_outside_cache": outside_events,
        "tap_inside_cache": inside_events,
        "limit": "sequential functools.cache and original observer composition; no complete dependency inference, current capability check or concurrent single-flight",
    }


def hash_eligibility():
    class Colliding:
        def __hash__(self):
            return 7

    first, second = Colliding(), Colliding()
    table = {first: "a", second: "b"}
    error = None
    try:
        hash([])
    except TypeError as failure:
        error = type(failure).__name__
    assert first != second and hash(first) == hash(second) and len(table) == 2
    assert error == "TypeError"
    return {
        "equal_hashes": hash(first) == hash(second),
        "equal_objects": first == second,
        "distinct_entries": len(table),
        "list_hash_error": error,
        "limit": "Python identity-equal objects with imposed collision and one unhashable List; no Java VM, cryptography or portable Nomi Hash algorithm",
    }


def encoding_profiles():
    first = {"a": 1, "b": 2}
    second = {"b": 2, "a": 1}
    ordinary = [json.dumps(item) for item in (first, second)]
    sorted_keys = [json.dumps(item, sort_keys=True) for item in (first, second)]
    list_roundtrip = json.loads(json.dumps([1, 2])) == [1, 2]
    tuple_roundtrip = json.loads(json.dumps((1, 2))) == (1, 2)
    assert first == second and ordinary[0] != ordinary[1]
    assert sorted_keys[0] == sorted_keys[1]
    assert list_roundtrip and not tuple_roundtrip
    return {
        "equal_mappings": first == second,
        "ordinary_encodings": ordinary,
        "sorted_key_encodings": sorted_keys,
        "list_roundtrip_equal": list_roundtrip,
        "tuple_roundtrip_equal": tuple_roundtrip,
        "limit": "chosen Python JSON subset and key ordering; not canonical JSON for every type, schema migration or safe executable-object serialization",
    }


def accumulated_state():
    state = []
    aliases = [state]
    copies = [state.copy()]
    for value in [1, 2]:
        state.append(value)
        aliases.append(state)
        copies.append(state.copy())
    running = 0
    emitted = []
    for value in [1, 2]:
        running += value
        emitted.append(f"total:{running}")
    assert aliases == [[1, 2], [1, 2], [1, 2]]
    assert copies == [[], [1], [1, 2]] and emitted == ["total:1", "total:3"]
    return {
        "aliased_history": aliases,
        "copied_history": copies,
        "map_accum": {"final_state": running, "emitted": emitted},
        "limit": "original mutable-state and finite map_accum models; no Nomi immutability, snapshot derivation or encapsulated-mutation checking",
    }


PROBES = [
    ("GP01", map_fusion, ["GA2"]),
    ("GP02", fold_and_scan, ["GA3", "GA4"]),
    ("GP03", reassociation, ["GA4"]),
    ("GP04", row_outcomes, ["GA1", "GA2"]),
    ("GP05", tap_outcomes, ["GA5"]),
    ("GP06", lazy_demand, ["GA2", "GA5"]),
    ("GP07", repetition, ["GA7"]),
    ("GP08", stopping_policies, ["GA7"]),
    ("GP09", caching_context, ["GA5", "GA6"]),
    ("GP10", hash_eligibility, ["GA8"]),
    ("GP11", encoding_profiles, ["GA8"]),
    ("GP12", accumulated_state, ["GA3"]),
]


def report(observed_on):
    return {
        "schema": "nomi.research.generic-operations.v1",
        "observed_on": observed_on.isoformat(),
        "environment": {"python": platform.python_version()},
        "evidence_kind": "Python-host/library observations and original bounded models",
        "execution": {
            "nomi": False,
            "foreign_library": False,
            "parallel_executor": False,
            "remote_service": False,
            "human": False,
        },
        "probes": [
            {"id": name, "name": probe.__name__, "experiments": experiments, **probe()}
            for name, probe, experiments in PROBES
        ],
    }


def capture_object(pairs):
    fields = {}
    for key, value in pairs:
        if key in fields:
            raise ValueError(f"Duplicate capture field: {key!r}")
        fields[key] = value
    return fields


def read_capture(path):
    captured = json.loads(
        path.read_text(encoding="utf-8"), object_pairs_hook=capture_object
    )
    if not isinstance(captured, dict):
        raise ValueError("capture must be an object")
    environment = captured.get("environment")
    if not isinstance(environment, dict) or set(environment) != {"python"}:
        raise ValueError("environment must contain exactly the python version")
    if not isinstance(environment["python"], str) or not environment["python"]:
        raise ValueError("invalid historical Python version")
    observed_on = date.fromisoformat(captured["observed_on"])
    return captured, report(observed_on)


def comparable(payload):
    return json.dumps(
        {key: value for key, value in payload.items() if key != "environment"},
        sort_keys=True,
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--observed-on", type=date.fromisoformat)
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument("--output", type=Path)
    modes.add_argument("--check", type=Path)
    args = parser.parse_args()
    if not __debug__:
        parser.error("Run without -O; probe assertions are required.")
    if args.check:
        if args.observed_on:
            parser.error("--observed-on is only for producing a capture")
        try:
            captured, current = read_capture(args.check)
        except (OSError, ValueError, KeyError, TypeError) as error:
            parser.error(f"Cannot read capture: {error}")
        if comparable(captured) != comparable(current):
            parser.error("Capture differs from current outcomes or execution scope.")
        print(
            f"Verified {len(PROBES)} local generic-operation probes against {args.check}"
        )
        return
    payload = json.dumps(report(args.observed_on or date.today()), indent=2) + "\n"
    if args.output:
        args.output.write_text(payload, encoding="utf-8")
        print(f"Captured {len(PROBES)} local generic-operation probes in {args.output}")
    else:
        print(payload, end="")


if __name__ == "__main__":
    main()
