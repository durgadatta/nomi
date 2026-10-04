"""Original bounded domain models plus graphlib/SQLite observations.

No Nomi, scheduler service, ML engine, device, cloud, or human execution.
"""

import argparse
from collections import Counter
from datetime import date
from fractions import Fraction
from graphlib import CycleError, TopologicalSorter
import hashlib
from itertools import permutations, product
import json
from pathlib import Path
import platform
import sqlite3


def dependency_order():
    graph = {
        "source": (),
        "left": ("source",),
        "right": ("source",),
        "join": ("left", "right"),
    }
    valid_orders = []
    for order in permutations(graph):
        sorter = TopologicalSorter(graph)
        sorter.prepare()
        ready = set()
        for node in order:
            ready.update(sorter.get_ready())
            if node not in ready:
                break
            ready.remove(node)
            sorter.done(node)
        else:
            valid_orders.append(list(order))
    cycle_rejected = False
    try:
        TopologicalSorter({"a": ("b",), "b": ("a",)}).prepare()
    except CycleError:
        cycle_rejected = True
    assert len(valid_orders) == 2 and cycle_rejected
    return {
        "inputs": graph,
        "permutations_checked": 24,
        "valid_orders": valid_orders,
        "cycle_rejected": cycle_rejected,
        "limit": "graphlib readiness only; no scheduler, task body, fairness or effect conflict execution",
    }


def edge_roles():
    edges = [
        {"source": "a", "target": "b", "role": "task_prerequisite"},
        {"source": "a", "target": "b", "role": "attribution"},
    ]
    accepted = [edge["role"] == "task_prerequisite" for edge in edges]
    assert accepted == [True, False]
    return {
        "inputs": edges,
        "untyped_drawing_equal": True,
        "task_owner_accepts": accepted,
        "limit": "two supplied role tags under an imposed checker policy; not Nomi edge typing or a universal relation algebra",
    }


def temporal_amount(valid_at, known_at):
    connection = sqlite3.connect(":memory:")
    try:
        connection.execute(
            "CREATE TABLE amounts (amount INTEGER, valid_from INTEGER, "
            "valid_to INTEGER, known_from INTEGER, known_to INTEGER)"
        )
        connection.executemany(
            "INSERT INTO amounts VALUES (?, ?, ?, ?, ?)",
            [(100, 10, 20, 1, 3), (120, 10, 20, 3, None)],
        )
        return [
            row[0]
            for row in connection.execute(
                "SELECT amount FROM amounts WHERE valid_from <= ? AND ? < valid_to "
                "AND known_from <= ? AND (known_to IS NULL OR ? < known_to) "
                "ORDER BY amount",
                (valid_at, valid_at, known_at, known_at),
            )
        ]
    finally:
        connection.close()


def bitemporal_correction():
    questions = [(15, 2), (15, 3), (15, 4), (20, 4), (9, 4), (15, 0)]
    answers = [temporal_amount(valid, known) for valid, known in questions]
    assert answers == [[100], [120], [120], [], [], []]
    return {
        "inputs": {"questions_valid_known": questions, "intervals": "half-open"},
        "answers": answers,
        "limit": "SQLite on two original interval records and integer time domains; no temporal database engine or concurrent consistency guarantee",
    }


def read_snapshot(manifests, blobs, version):
    if version not in manifests:
        raise ValueError("unknown_version")
    content = manifests[version]
    if content not in blobs:
        raise ValueError("expired_content")
    return blobs[content]


def snapshot_retention():
    manifests = {"v1": "blob-old", "v2": "blob-new"}
    blobs = {"blob-new": [120]}
    outcomes = {}
    for version in ("v1", "v2", "v3"):
        try:
            outcomes[version] = {"value": read_snapshot(manifests, blobs, version)}
        except ValueError as error:
            outcomes[version] = {"error": str(error)}
    assert outcomes == {
        "v1": {"error": "expired_content"},
        "v2": {"value": [120]},
        "v3": {"error": "unknown_version"},
    }
    return {
        "inputs": {"manifests": manifests, "retained_blobs": sorted(blobs)},
        "outcomes": outcomes,
        "limit": "in-memory manifest/store with imposed errors; no lakehouse, lease, privacy policy or durable storage integration",
    }


def independent_snapshots():
    sources = [
        {"store": "orders", "version": "v7", "basis": "cut-a"},
        {"store": "payments", "version": "v9", "basis": "cut-b"},
    ]
    shared_basis = len({source["basis"] for source in sources}) == 1
    assert not shared_basis
    return {
        "inputs": sources,
        "individually_pinned": True,
        "shared_transaction_basis_established": shared_basis,
        "consistent_in_real_world": "unknown",
        "limit": "supplied basis labels show missing shared-cut evidence, not actual inconsistency or a distributed snapshot protocol",
    }


def change_algebra():
    before = Counter({2: 1, 5: 1})
    changes = Counter({2: -1})
    after = before.copy()
    after.update(changes)
    assert all(count >= 0 for count in after.values())
    sum_before = sum(value * count for value, count in before.items())
    sum_delta = sum(value * count for value, count in changes.items())
    sum_after = sum(value * count for value, count in after.items())
    minimum_after = min(value for value, count in after.items() if count > 0)
    assert sum_before + sum_delta == sum_after == 5
    assert min(before) - 2 == 0 != minimum_after == 5
    return {
        "inputs": {"values": [2, 5], "delete": 2},
        "sum": {"before": sum_before, "delta": sum_delta, "after": sum_after},
        "minimum": {"naive_subtraction": 0, "retained_alternatives": minimum_after},
        "limit": "finite nonempty integer bag with retained counts; no incremental query engine, Float law or general deletion algebra",
    }


def computation_key(context):
    # Only this fixture's JSON-compatible integer/text records are admitted.
    encoded = json.dumps(
        context, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def read_cached(cache, key, *, current_read_allowed):
    if not current_read_allowed:
        raise ValueError("read_denied")
    return cache[key]


def cache_context():
    context = {
        "operation": "sum-v1",
        "inputs": ["orders:v7"],
        "schema": "sales-v2",
        "profile": "exact-int-v1",
    }
    key = computation_key(context)
    changed = {**context, "inputs": ["orders:v8"]}
    profile_changed = {**context, "profile": "checked-int-v2"}
    assert key != computation_key(changed) != computation_key(profile_changed)
    cache = {key: "private-result"}
    read_denied = False
    try:
        read_cached(cache, key, current_read_allowed=False)
    except ValueError as error:
        read_denied = str(error) == "read_denied"
    assert (
        read_denied
        and read_cached(cache, key, current_read_allowed=True) == "private-result"
    )
    return {
        "inputs": context,
        "input_change_changes_key": key != computation_key(changed),
        "profile_change_changes_key": key != computation_key(profile_changed),
        "cache_available_after_read_revocation": key in cache,
        "current_read_allowed": False,
        "candidate_returns_cached_secret": not read_denied,
        "limit": "supplied contexts/permission flag; no complete read-set inference, canonical JSON, real authorization or cryptographic authenticity",
    }


def train_only_mean(training):
    return sum(Fraction(value) for value in training) / len(training)


def train_only_preprocessing():
    training = [1, 3]
    held_out = [100, 200]
    learned = train_only_mean(training)
    leaked = [train_only_mean(training + [value]) for value in held_out]
    assert learned == 2 and leaked == [Fraction(104, 3), Fraction(68)]
    return {
        "inputs": {"training": training, "held_out_alternatives": held_out},
        "training_only_mean": str(learned),
        "leaked_means": [str(value) for value in leaked],
        "limit": "exact Fraction arithmetic for a mean; no fitted estimator, model-quality evaluation or complete leakage detector",
    }


def feature_availability():
    measurement = {"valid_at": 12, "known_from": 4, "value": 120}
    prediction = {"valid_at": 15, "known_at": 2}
    hindsight = {**prediction, "known_at": 5}
    event_only = measurement["valid_at"] <= prediction["valid_at"]
    available_then = event_only and measurement["known_from"] <= prediction["known_at"]
    available_later = event_only and measurement["known_from"] <= hindsight["known_at"]
    assert event_only and not available_then and available_later
    return {
        "inputs": {"measurement": measurement, "prediction": prediction},
        "event_time_only_includes_future_information": event_only,
        "available_at_original_prediction": available_then,
        "available_in_hindsight": available_later,
        "limit": "single supplied fact and availability rule; no feature store, clock mapping, label horizon or causal/statistical validity",
    }


def axis_identity():
    expected = [("sample", 2), ("feature", 2)]
    actual = [("feature", 2), ("sample", 2)]
    extents_match = [size for _, size in expected] == [size for _, size in actual]
    assert extents_match and expected != actual
    return {
        "inputs": {"expected_axes": expected, "actual_axes": actual},
        "extent_only_accepts": extents_match,
        "named_axis_contract_accepts": expected == actual,
        "limit": "two supplied axis descriptors; no tensor/shape checker, contraction, AD engine or device execution",
    }


TRAINING_FIELDS = frozenset({"parameters", "optimizer", "rng", "data_position", "step"})


def missing_training_fields(checkpoint):
    return sorted(TRAINING_FIELDS - checkpoint.keys())


def checkpoint_scope():
    weights = {"parameters": {"weight": 2}}
    complete = {
        **weights,
        "optimizer": {"momentum": 3},
        "rng": "key-v1",
        "data_position": 7,
        "step": 4,
    }
    missing = missing_training_fields(weights)
    assert missing == ["data_position", "optimizer", "rng", "step"]
    assert missing_training_fields(complete) == []
    return {
        "inputs": {"weights_only": weights, "training_record": complete},
        "weights_contain_inference_parameters": True,
        "weights_missing_for_training": missing,
        "record_missing_for_training": [],
        "exact_resume_established": False,
        "limit": "imposed field-presence contract; no semantic state validation, model loading, safe deserialization or actual training resume",
    }


def reference_identity():
    aliases = {"champion": "model-v1"}
    pinned = aliases["champion"]
    aliases["champion"] = "model-v2"
    catalog = [
        {"work_id": "work-a", "title": "Methods"},
        {"work_id": "work-b", "title": "Methods"},
    ]
    assert pinned != aliases["champion"]
    assert catalog[0]["title"] == catalog[1]["title"]
    assert catalog[0]["work_id"] != catalog[1]["work_id"]
    return {
        "inputs": {"alias": "champion", "catalog": catalog},
        "resolved_before": pinned,
        "resolved_after": aliases["champion"],
        "same_title_different_work_ids": True,
        "limit": "supplied alias and work records; no registry authentication, bibliographic resolution or universal ID generation",
    }


def publication_review():
    outcomes = [
        {
            "payload_matches": payload,
            "model_matches": model,
            "recipient_matches": recipient,
            "current_grant": grant,
            "candidate_accepts": payload and model and recipient and grant,
        }
        for payload, model, recipient, grant in product((False, True), repeat=4)
    ]
    accepted = [outcome for outcome in outcomes if outcome["candidate_accepts"]]
    assert len(outcomes) == 16 and len(accepted) == 1
    return {
        "inputs": "four independent supplied booleans; exact-scope review policy",
        "outcomes": outcomes,
        "accepted_count": len(accepted),
        "limit": "finite matching-policy truth table; no authenticated review, actual capability enforcement, human understanding or remote publication",
    }


PROBES = [
    ("CP01", dependency_order, ["DT1"]),
    ("CP02", edge_roles, ["DT1", "DC1"]),
    ("CP03", bitemporal_correction, ["DT2"]),
    ("CP04", snapshot_retention, ["DT2"]),
    ("CP05", independent_snapshots, ["DT2"]),
    ("CP06", change_algebra, ["DT3"]),
    ("CP07", cache_context, ["DT4"]),
    ("CP08", train_only_preprocessing, ["ML1"]),
    ("CP09", feature_availability, ["DT2", "ML1"]),
    ("CP10", axis_identity, ["ML2"]),
    ("CP11", checkpoint_scope, ["ML4"]),
    ("CP12", reference_identity, ["ML5", "DC3"]),
    ("CP13", publication_review, ["DT4", "ML5", "DC5"]),
]


def report(observed_on):
    return {
        "schema": "nomi.research.domain-composition.v1",
        "observed_on": observed_on.isoformat(),
        "environment": {
            "python": platform.python_version(),
            "sqlite": sqlite3.sqlite_version,
        },
        "evidence_kind": "original bounded models plus named graphlib/SQLite host observations",
        "execution": {
            "nomi": False,
            "foreign_framework": False,
            "ml_engine": False,
            "device": False,
            "cloud": False,
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
            captured = json.loads(
                args.check.read_text(encoding="utf-8"), object_pairs_hook=capture_object
            )
            if not isinstance(captured, dict):
                raise ValueError("capture must be an object")
            if not isinstance(captured.get("environment"), dict):
                raise ValueError("environment must be an object")
            current = report(date.fromisoformat(captured["observed_on"]))
            if set(captured["environment"]) != set(current["environment"]):
                raise ValueError("missing or unexpected environment field")
            if any(
                not isinstance(value, str) or not value
                for value in captured["environment"].values()
            ):
                raise ValueError("invalid historical environment version")
        except (OSError, ValueError, KeyError, TypeError) as error:
            parser.error(f"Cannot read capture: {error}")
        versions = "environment"
        expected = json.dumps(
            {key: value for key, value in captured.items() if key != versions},
            sort_keys=True,
        )
        actual = json.dumps(
            {key: value for key, value in current.items() if key != versions},
            sort_keys=True,
        )
        if expected != actual:
            parser.error("Capture differs from current outcomes or execution scope.")
        print(f"Verified {len(PROBES)} local composition probes against {args.check}")
        return
    payload = json.dumps(report(args.observed_on or date.today()), indent=2) + "\n"
    if args.output:
        args.output.write_text(payload, encoding="utf-8")
        print(f"Captured {len(PROBES)} local composition probes in {args.output}")
    else:
        print(payload, end="")


if __name__ == "__main__":
    main()
