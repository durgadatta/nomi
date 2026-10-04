"""Original finite messaging countermodels; no broker, Nomi or scheduler execution."""

import argparse
from datetime import date
from itertools import combinations, permutations
import json
from pathlib import Path
import platform


def frontier(delivered, completed, end):
    """First unresolved delivered obligation, or a supplied end position."""
    if any(type(position) is not int for position in [*delivered, *completed, end]):
        raise ValueError("positions must be integers")
    if list(delivered) != sorted(set(delivered)) or any(p < 0 for p in delivered):
        raise ValueError("delivered positions must be ordered, unique and nonnegative")
    if end < 0 or (delivered and end <= delivered[-1]):
        raise ValueError("end must follow the delivered positions")
    if not set(completed) <= set(delivered):
        raise ValueError("completion must belong to delivered obligations")
    return next((p for p in delivered if p not in completed), end)


def inbox_attempt(state, source, identity, payload, owner, expected_owner):
    """Imposed atomic arbitration; not a transaction/storage implementation."""
    if owner != expected_owner:
        return "stale_owner"
    key = (source, identity)
    if key in state["inbox"]:
        return "duplicate" if state["inbox"][key] == payload else "payload_conflict"
    state["inbox"][key] = payload
    state["effects"] += 1
    state["outbox"].append(key)
    return "committed"


def frontier_holes():
    delivered = [10, 12, 13]
    cases = []
    for count in range(len(delivered) + 1):
        for completed in combinations(delivered, count):
            safe = frontier(delivered, completed, 14)
            cases.append({"completed": list(completed), "frontier": safe})
    assert frontier(delivered, [12, 13], 14) == 10
    assert frontier(delivered, [10, 12], 14) == 13
    return {
        "delivered": delivered,
        "end": 14,
        "cases": cases,
        "limit": "supplied ordered delivery obligations; no isolation, offset fetch, rebalance or broker commit",
    }


def atomic_inbox():
    state = {"inbox": {}, "effects": 0, "outbox": []}
    outcomes = [inbox_attempt(state, "orders", "e1", "reserve", 8, 8) for _ in range(2)]
    assert outcomes == ["committed", "duplicate"] and state["effects"] == 1
    return {
        "attempts": outcomes,
        "local_effects": state["effects"],
        "outbox_intents": len(state["outbox"]),
        "assumption": "one indivisible local arbitration step",
        "limit": "imposed atomicity, not crash-safe storage, concurrent arbitration or remote-effect deduplication",
    }


def crash_cuts():
    steps = ["effect", "record_inbox", "ack"]
    cases = []
    for cut in range(4):
        completed = steps[:cut]
        replay_effect = "ack" not in completed and "record_inbox" not in completed
        effects = int("effect" in completed) + int(replay_effect)
        cases.append({"crash_after": completed, "effects_after_retry": effects})
    assert cases[1]["effects_after_retry"] == 2
    return {
        "non_atomic_effect_first": cases,
        "ack_first_crash": {"delivery_removed": True, "effect_done": False},
        "mark_first_crash": {"duplicate_suppressed": True, "effect_done": False},
        "limit": "enumerated instruction-boundary crashes with one eventual retry; no torn writes, actual recovery or availability proof",
    }


def identities_and_fencing():
    state = {"inbox": {}, "effects": 0, "outbox": []}
    inputs = [
        ("a", "1", "reserve", 7),
        ("a", "1", "reserve", 8),
        ("a", "1", "reserve", 8),
        ("a", "1", "release", 8),
        ("b", "1", "reserve", 8),
    ]
    outcomes = [inbox_attempt(state, *args, expected_owner=8) for args in inputs]
    assert outcomes == [
        "stale_owner",
        "committed",
        "duplicate",
        "payload_conflict",
        "committed",
    ]
    return {
        "inputs": inputs,
        "outcomes": outcomes,
        "effects": state["effects"],
        "limit": "supplied trusted source/owner labels and exact payload comparison, not authentication, hashing or real distributed fencing",
    }


def dedup_expiry():
    expiry = 5
    times = [1, 4, 5, 6]
    effects = [1 if now < expiry else 2 for now in times]
    assert effects == [1, 1, 2, 2]
    return {
        "original_commit_at": 0,
        "expires_at": expiry,
        "retry_times": times,
        "total_effects": effects,
        "limit": "imposed half-open retention window and one retry; not any vendor's dedup policy",
    }


def outbox_response_loss():
    publications = ["event-1", "event-1"]
    assert len(publications) == 2 and len(set(publications)) == 1
    return {
        "local_intents": 1,
        "accepted_publications": publications,
        "trace": [
            "publish accepted",
            "response lost before sent marker",
            "relay retries same identity",
        ],
        "limit": "one supplied lost-response trace; stable ID alone supplies no remote dedup or observation service",
    }


def partition_order():
    # Two independent partitions; each contains one noncommuting transition.
    outcomes = []
    for order in permutations(("add_1", "set_0")):
        value = 0
        for operation in order:
            value = value + 1 if operation == "add_1" else 0
        outcomes.append({"order": list(order), "value": value})
    assert {item["value"] for item in outcomes} == {0, 1}
    return {
        "outcomes": outcomes,
        "limit": "two legal single-record partition interleavings; not total-order service or a general commutativity checker",
    }


def replay_and_edition():
    events = [3, -1, 2]
    first = sum(events)
    replay = sum(events)
    assert first == replay == 4
    return {
        "events": events,
        "pure_projection": [first, replay],
        "effectful_notifications_after_two_runs": 6,
        "checkpoint_edition": "sum.v1",
        "requested_edition": "absolute-sum.v2",
        "compatible": False,
        "limit": "integer fold and supplied edition-equality policy; no event store, migration or workflow replay engine",
    }


def budget_admits(active, queued, payload_bytes, count_limit, byte_limit):
    if any(
        type(n) is not int or n < 0
        for n in [active, queued, *payload_bytes, count_limit, byte_limit]
    ):
        raise ValueError("budgets and usage must be nonnegative integers")
    if len(payload_bytes) != active + queued:
        raise ValueError("one payload byte count is required per admitted item")
    return active + queued <= count_limit and sum(payload_bytes) <= byte_limit


def budgets_and_feedback():
    cases = [
        {"active": 1, "queued": 2, "payload_bytes": [2, 2, 2]},
        {"active": 1, "queued": 3, "payload_bytes": [1, 1, 1, 1]},
        {"active": 1, "queued": 1, "payload_bytes": [1, 9]},
    ]
    accepted = [budget_admits(**case, count_limit=3, byte_limit=6) for case in cases]
    assert accepted == [True, False, False]
    return {
        "cases": cases,
        "count_limit": 3,
        "byte_limit": 6,
        "accepted": accepted,
        "feedback": {
            "a_to_b_full": True,
            "b_to_a_full": True,
            "both_next_actions": "blocking send",
            "enabled_next_actions": 0,
        },
        "limit": "supplied admission predicates and deadlocked configuration; bytes omit overhead/fanout and no scheduler/fairness execution occurs",
    }


def observation_and_authority():
    return {
        "remote_truth": "accepted",
        "local_observation_after_cancel": "unknown",
        "safe_retry_conclusion": "not established",
        "historical_grant": True,
        "current_grant": False,
        "replayed_command_authorized": False,
        "limit": "supplied counterexample and current-grant predicate, not remote reconciliation, authentication or capability enforcement",
    }


PROBES = [
    ("MP01", frontier_holes, ["MSG2"]),
    ("MP02", atomic_inbox, ["MSG3"]),
    ("MP03", crash_cuts, ["MSG3"]),
    ("MP04", identities_and_fencing, ["MSG1", "MSG3"]),
    ("MP05", dedup_expiry, ["MSG3"]),
    ("MP06", outbox_response_loss, ["MSG3"]),
    ("MP07", partition_order, ["MSG2"]),
    ("MP08", replay_and_edition, ["MSG5"]),
    ("MP09", budgets_and_feedback, ["MSG4"]),
    ("MP10", observation_and_authority, ["MSG6"]),
]


def report(observed_on):
    return {
        "schema": "nomi.research.messaging.v1",
        "observed_on": observed_on.isoformat(),
        "environment": {"python": platform.python_version()},
        "evidence_kind": "original finite countermodels",
        "execution": {
            "nomi": False,
            "broker": False,
            "network": False,
            "durable_storage": False,
            "async_scheduler": False,
            "authenticated_authority": False,
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


def verify_capture(path):
    captured = json.loads(
        path.read_text(encoding="utf-8"), object_pairs_hook=capture_object
    )
    if not isinstance(captured, dict):
        raise ValueError("capture must be an object")
    environment = captured.get("environment")
    if not isinstance(environment, dict) or set(environment) != {"python"}:
        raise ValueError("missing or unexpected environment field")
    if not isinstance(environment["python"], str) or not environment["python"].strip():
        raise ValueError("invalid historical environment version")
    current = report(date.fromisoformat(captured["observed_on"]))
    expected = {key: value for key, value in captured.items() if key != "environment"}
    actual = {key: value for key, value in current.items() if key != "environment"}
    if json.dumps(expected, sort_keys=True) != json.dumps(actual, sort_keys=True):
        raise ValueError("Capture differs from current outcomes or execution scope.")


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
            verify_capture(args.check)
        except (OSError, ValueError, KeyError, TypeError) as error:
            parser.error(f"Cannot verify capture: {error}")
        print(f"Verified {len(PROBES)} finite messaging probes against {args.check}")
        return
    payload = json.dumps(report(args.observed_on or date.today()), indent=2) + "\n"
    if args.output:
        args.output.write_text(payload, encoding="utf-8")
        print(f"Captured {len(PROBES)} finite messaging probes in {args.output}")
    else:
        print(payload, end="")


if __name__ == "__main__":
    main()
