"""Original bounded interaction models; no Nomi, browser, or device execution."""

import argparse
from datetime import date
from decimal import Decimal, ROUND_HALF_UP
from itertools import permutations, product
import json
from pathlib import Path
import platform
import unicodedata


def domain_identity():
    rows = [
        {"id": "tea", "label": "Tea", "quantity": 2},
        {"id": "cup", "label": "Cup", "quantity": 1},
    ]
    selected_position = 0
    selected_id = rows[selected_position]["id"]
    sorted_rows = sorted(rows, key=lambda row: row["label"])
    positional_target = sorted_rows[selected_position]["id"]
    identity_target = next(row["id"] for row in sorted_rows if row["id"] == selected_id)
    assert positional_target == "cup" and identity_target == "tea"
    return {
        "inputs": rows,
        "sorted_ids": [row["id"] for row in sorted_rows],
        "counterexample": {"position_target": positional_target},
        "candidate": {"identity_target": identity_target},
        "limit": "two unique rows; no grid, source rename, or duplicate-ID decoder",
    }


def incarnation_revision():
    old = {"model": "invoice", "incarnation": "session-a", "revision": 1}
    current = {"model": "invoice", "incarnation": "session-b", "revision": 1}
    number_only = old["revision"] == current["revision"]
    same_context = old == current
    assert number_only and not same_context
    return {
        "inputs": {"prepared_for": old, "current": current},
        "counterexample": {"revision_only_accepts": number_only},
        "candidate": {
            "full_identity_accepts": same_context,
            "outcome": "wrong_incarnation",
        },
        "limit": "explicit two-incarnation model; no UUID generation or production revision protocol",
    }


def draft_commit():
    drafts = ["", "-", "3x", "-1", "3"]
    quantity = 2
    revision = 7
    history = []
    for raw in drafts:
        # This imposed codec intentionally accepts only an ASCII unsigned integer.
        valid = raw.isascii() and raw.isdecimal()
        if valid:
            quantity = int(raw)
            revision += 1
        history.append(
            {
                "raw_draft": raw,
                "decode": "ok" if valid else "error",
                "committed_quantity": quantity,
                "revision": revision,
            }
        )
    assert [step["committed_quantity"] for step in history] == [2, 2, 2, 2, 3]
    assert [step["revision"] for step in history] == [7, 7, 7, 7, 8]
    return {
        "inputs": {"initial_quantity": 2, "initial_revision": 7},
        "candidate": history,
        "counterexample": {"filter_invalid_text": "loses the useful minus-sign draft"},
        "limit": "toy input codec, not Nomi Int.parse/decode or an IME/form test",
    }


def inverse_projection():
    domain = list(product(range(4), repeat=2))
    inverses = {
        str(total): [list(pair) for pair in domain if pair[0] * pair[1] == total]
        for total in (0, 3, 7)
    }
    assert len(inverses["0"]) == 7
    assert inverses["3"] == [[1, 3], [3, 1]] and inverses["7"] == []
    return {
        "inputs": {"quantity_domain": [0, 1, 2, 3], "price_domain": [0, 1, 2, 3]},
        "counterexample": {"unique_inverse_from_total": False},
        "candidate": {"inverse_candidates": inverses},
        "limit": "exhaustive 16-pair integer model; no general inverse, solver, or source editing",
    }


def value_law_effect_trace():
    traces = {}
    values = {}
    for order in ("false_first", "effect_first"):
        calls = []

        def observe():
            calls.append("external_observation")
            return True

        value = (
            (False and observe()) if order == "false_first" else (observe() and False)
        )
        traces[order] = calls
        values[order] = value
    assert values["false_first"] == values["effect_first"] is False
    assert traces["false_first"] == [] and len(traces["effect_first"]) == 1
    return {
        "inputs": "false conjunction with a counted predicate",
        "counterexample": {"same_values": values, "different_traces": traces},
        "candidate": "preserve short-circuit order unless resolved side conditions permit rewriting",
        "limit": "Python short circuit with an in-memory counter, not a real effect or Nomi optimizer",
    }


def domain_and_evidence():
    universe_a = {"tea", "cup"}
    universe_b = universe_a | {"book"}
    selected = {"tea"}
    complements = [sorted(universe_a - selected), sorted(universe_b - selected)]
    evidence = {
        "neither": (False, False),
        "supported": (True, False),
        "refuted": (False, True),
        "conflicting": (True, True),
    }
    collapsed = {key: bits[0] for key, bits in evidence.items()}
    assert complements == [["cup"], ["book", "cup"]]
    assert len(set(evidence.values())) == 4 and len(set(collapsed.values())) == 2
    return {
        "inputs": {
            "universes": [sorted(universe_a), sorted(universe_b)],
            "selected": sorted(selected),
            "support_refutation": evidence,
        },
        "counterexample": {
            "unqualified_complements": complements,
            "support_bit_loses_information": collapsed,
        },
        "candidate": "name the universe and preserve evidence status separately from core Bool",
        "limit": "original four evidence records, no universal truth algebra or epistemic reasoner",
    }


def guarded_preconditions():
    states = list(range(5))
    outcomes = {state: [state - 1, state + 1] for state in states}
    existential = [
        state for state in states if any(value >= 0 for value in outcomes[state])
    ]
    universal = [
        state for state in states if all(value >= 0 for value in outcomes[state])
    ]
    assert existential == states and universal == [1, 2, 3, 4]
    return {
        "inputs": {
            "initial_states": states,
            "branches": "decrement or increment once",
            "postcondition": "result >= 0",
        },
        "counterexample": {"some_branch_safe": existential, "unsafe_path": [0, -1]},
        "candidate": {"every_branch_safe": universal},
        "limit": "two terminating transitions over five states; no predicate-transformer engine or unordered Nomi match",
    }


def invariant_and_progress():
    decreasing = [3, 2, 1, 0]
    stuttering = [3, 3, 3, 3]

    def invariant(trace):
        return all(state >= 0 for state in trace)

    assert invariant(decreasing) and invariant(stuttering)
    assert decreasing[-1] == 0 and stuttering[-1] != 0
    return {
        "inputs": {
            "invariant": "remaining >= 0",
            "completion": "remaining == 0",
            "trace_budget": 4,
        },
        "counterexample": {
            "stutter_trace": stuttering,
            "invariant_holds": True,
            "completed_within_budget": False,
        },
        "candidate": {"decreasing_trace": decreasing, "variant": "remaining"},
        "limit": "two supplied traces; no unbounded termination or fairness proof",
    }


def run_epoch_order():
    replies = [(4, "old"), (5, "current")]
    captures = []
    for order in permutations(replies):
        current_run = 5
        visible = None
        archived = []
        naive = None
        for run_id, value in order:
            naive = value
            archived.append({"run_id": run_id, "value": value})
            if run_id == current_run:
                visible = value
        captures.append(
            {
                "arrival_run_ids": [run_id for run_id, _ in order],
                "arrival_only_visible": naive,
                "epoch_visible": visible,
                "archived": archived,
            }
        )
    assert all(capture["epoch_visible"] == "current" for capture in captures)
    assert any(capture["arrival_only_visible"] == "old" for capture in captures)
    return {
        "inputs": {"current_run": 5, "replies": replies},
        "candidate_and_counterexample": captures,
        "limit": "both permutations of two supplied completions, no worker or async scheduler",
    }


def cached_authority():
    checked_artifact = {"source_digest": "source-a", "requires": ["publish"]}
    prepared_grants = {"publish"}
    current_grants = set()
    cached_allowed = set(checked_artifact["requires"]) <= prepared_grants
    allowed_now = set(checked_artifact["requires"]) <= current_grants
    assert cached_allowed and not allowed_now
    return {
        "inputs": {
            "artifact": checked_artifact,
            "prepared_grants": sorted(prepared_grants),
            "current_grants": sorted(current_grants),
        },
        "counterexample": {"cached_allowed": cached_allowed},
        "candidate": {"allowed_now": allowed_now, "outcome": "denied", "actions": 0},
        "limit": "set-membership policy model; no capability handles, revocation race, or actual authorization",
    }


def uncertain_action():
    ledger = {}
    actions = 0

    def send(key, payload, lose_ack=False):
        nonlocal actions
        if key in ledger:
            if ledger[key] != payload:
                return "payload_conflict"
            return "acknowledged_existing"
        ledger[key] = payload
        actions += 1
        return "outcome_unknown" if lose_ack else "acknowledged_new"

    first = send("publication-1", {"quantity": 2}, lose_ack=True)
    same = send("publication-1", {"quantity": 2})
    changed = send("publication-1", {"quantity": 3})
    assert first == "outcome_unknown" and same == "acknowledged_existing"
    assert changed == "payload_conflict" and actions == 1
    return {
        "inputs": {
            "operation_id": "publication-1",
            "original": {"quantity": 2},
            "changed": {"quantity": 3},
        },
        "counterexample": {
            "unknown_does_not_mean_no_action": first,
            "blind_new_key_resend_would_add_an_action": True,
        },
        "candidate": {
            "same_key_same_payload": same,
            "same_key_new_payload": changed,
            "external_action_count_in_model": actions,
            "local_stop": "requested",
            "remote_outcome_after_lost_ack": "unknown",
        },
        "limit": "fake ledger imposes stable-key rules; no provider exactly-once or cancellation guarantee",
    }


def merged_invariant():
    base = {"minimum": 0, "maximum": 10}
    left = {**base, "minimum": 8}
    right = {**base, "maximum": 5}
    merged = {**left, "maximum": right["maximum"]}

    def valid(value):
        return value["minimum"] <= value["maximum"]

    assert valid(base) and valid(left) and valid(right) and not valid(merged)
    return {
        "inputs": {"base": base, "left": left, "right": right},
        "counterexample": {"converged_merge": merged, "valid": False},
        "candidate": {
            "committed": base,
            "retained_invalid_draft": merged,
            "error": "minimum must not exceed maximum",
        },
        "limit": "original two-property merge, not Git/Automerge or a CRDT algorithm",
    }


def lossy_projection():
    exact = [Decimal("1.001"), Decimal("1.004")]
    displayed = [
        str(value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)) for value in exact
    ]
    source_rules = {"minimum >= 0", "maximum <= 10", "minimum <= maximum"}
    projected_rules = {"minimum >= 0", "maximum <= 10"}
    omitted = sorted(source_rules - projected_rules)
    assert exact[0] != exact[1] and displayed[0] == displayed[1] == "1.00"
    assert omitted == ["minimum <= maximum"]
    return {
        "inputs": {
            "exact_values": [str(value) for value in exact],
            "source_rules": sorted(source_rules),
        },
        "counterexample": {"same_display": displayed, "omitted_rule": omitted},
        "candidate": {
            "codec": "exact decimal text under a named policy",
            "schema_projection_status": "partial",
            "commit": "use actual rules",
        },
        "limit": "two decimals and supplied rule sets; no schema exporter, codec, or confidentiality theorem",
    }


def passive_bounded_inspection():
    getter_calls = 0

    def host_display_getter():
        nonlocal getter_calls
        getter_calls += 1
        return "fresh host observation"

    host_display_getter()
    naive_calls = getter_calls
    events = [
        {"id": "e1", "kind": "input", "secret": "fixture-secret"},
        {"id": "e2", "kind": "decode"},
        {"id": "e3", "kind": "compute"},
        {"id": "e4", "kind": "commit"},
        {"id": "e5", "kind": "completion"},
    ]
    snapshot = [
        {key: value for key, value in event.items() if key != "secret"}
        for event in events
    ]
    before = getter_calls
    views = [snapshot[:3] for _ in range(4)]
    extra_calls = getter_calls - before
    raw_export = json.dumps(events)
    exported = json.dumps(views)
    assert naive_calls == 1 and extra_calls == 0
    assert "fixture-secret" in raw_export and "fixture-secret" not in exported
    return {
        "inputs": {"events": 5, "budget": 3, "view_opens": 4},
        "counterexample": {
            "naive_getter_calls": naive_calls,
            "raw_payload_export_leaks_fixture": True,
        },
        "candidate": {
            "inspection_getter_calls": extra_calls,
            "projection": views[0],
            "shown": 3,
            "omitted": 2,
            "complete_trace": False,
            "fixture_secret_in_export": False,
        },
        "limit": "one imposed redaction key and supplied snapshot; no host renderer or information-flow proof",
    }


def source_offset_units():
    prefix = "a\U0001f600e\u0301"
    offset = {
        "utf8_bytes": len(prefix.encode("utf-8")),
        "utf16_units": len(prefix.encode("utf-16-le")) // 2,
        "unicode_scalars": len(prefix),
    }
    composed = "\u00e9"
    decomposed = "e\u0301"
    assert offset == {"utf8_bytes": 8, "utf16_units": 5, "unicode_scalars": 4}
    assert composed != decomposed
    assert unicodedata.normalize("NFC", composed) == unicodedata.normalize(
        "NFC", decomposed
    )
    return {
        "inputs": {"prefix": prefix, "source_revision": "source-a"},
        "counterexample": {
            "unqualified_offset_is_ambiguous": offset,
            "visually_similar_sequences_have_different_codepoints": True,
        },
        "candidate": {
            "offset_unit": "utf8_bytes",
            "offset": 8,
            "source_revision": "source-a",
            "converted_utf16_offset": 5,
        },
        "limit": "Python encodings/NFC observation; no grapheme count, bidi renderer, identifier policy, or Nomi parser",
    }


def command_adapters():
    command = {"id": "set_quantity", "target": "tea", "base_revision": 7, "quantity": 3}
    adapters = {
        name: dict(command) for name in ("keyboard", "pointer", "palette", "agent")
    }
    events = [
        {"kind": "enter", "composing": True},
        {"kind": "pointer_cancel", "composing": False},
        {"kind": "activate", "composing": False},
    ]
    dispatched = [
        dict(command)
        for event in events
        if not event["composing"] and event["kind"] == "activate"
    ]
    naive_enter_run_count = sum(event["kind"] == "enter" for event in events)
    assert all(value == command for value in adapters.values())
    assert dispatched == [command] and naive_enter_run_count == 1
    return {
        "inputs": {"events": events, "command": command},
        "counterexample": {
            "naive_enter_runs_during_composition": naive_enter_run_count
        },
        "candidate": {"adapter_commands": adapters, "dispatched": dispatched},
        "limit": "supplied adapter/event records; no browser, IME, key-repeat, focus, or accessibility test",
    }


def reference_frame_change():
    prepared = {"frame": "room", "epoch": 1, "offset": 0, "local_x": 2}
    current = {"frame": "room", "epoch": 2, "offset": 10}
    intended_world_x = prepared["offset"] + prepared["local_x"]
    naive_world_x = current["offset"] + prepared["local_x"]
    reprojected_local_x = intended_world_x - current["offset"]
    assert intended_world_x == 2 and naive_world_x == 12 and reprojected_local_x == -8
    return {
        "inputs": {"prepared": prepared, "current_frame": current},
        "counterexample": {"apply_old_coordinates_in_new_frame": naive_world_x},
        "candidate": {
            "stale_frame_outcome": "reject_or_explicitly_reproject_and_revalidate",
            "preserved_world_x": intended_world_x,
            "new_local_x": reprojected_local_x,
        },
        "limit": "one-dimensional translation with known transform; no WebXR, rotations, uncertainty, or real device",
    }


def control_context():
    samples = [
        {"id": "old", "observed_at": 2, "value": 5},
        {"id": "fresh", "observed_at": 9, "value": 5},
    ]
    now = 10
    max_age = 2
    outcomes = []
    for sample, mode in product(samples, ("auto", "manual")):
        in_range = 0 <= sample["value"] <= 10
        fresh = 0 <= now - sample["observed_at"] <= max_age
        mode_matches = mode == "auto"
        allowed = in_range and fresh and mode_matches
        outcomes.append(
            {
                "sample": sample["id"],
                "mode": mode,
                "range_only_accepts": in_range,
                "context_accepts": allowed,
            }
        )
    assert all(outcome["range_only_accepts"] for outcome in outcomes)
    assert sum(outcome["context_accepts"] for outcome in outcomes) == 1
    return {
        "inputs": {
            "samples": samples,
            "clock_now": now,
            "max_age": max_age,
            "prepared_mode": "auto",
        },
        "candidate_and_counterexample": outcomes,
        "limit": "imposed same-clock freshness/mode model; no clock drift, physics, actuator, or safety guarantee",
    }


def checked_publish_interleavings():
    base = {"incarnation": "invoice-a", "revision": 7, "quantity": 2}
    requests = {"a": 3, "b": 4}
    events = [(actor, phase) for actor in requests for phase in ("prepare", "publish")]
    orders = [
        order
        for order in permutations(events)
        if all(
            order.index((actor, "prepare")) < order.index((actor, "publish"))
            for actor in requests
        )
    ]

    def run(order, guarded):
        current = dict(base)
        prepared = {}
        accepted = []
        outcomes = {}
        for actor, phase in order:
            same_base = all(
                current[field] == base[field] for field in ("incarnation", "revision")
            )
            if phase == "prepare":
                prepared[actor] = (
                    {**base, "revision": 8, "quantity": requests[actor]}
                    if same_base
                    else None
                )
            elif prepared[actor] is None:
                outcomes[actor] = "stale_at_prepare"
            elif guarded and not same_base:
                outcomes[actor] = "stale_at_publish"
            else:
                # The guarded branch imposes one indivisible compare-and-publish step.
                current = prepared[actor]
                accepted.append(actor)
                outcomes[actor] = "accepted"
        return {"accepted": accepted, "outcomes": outcomes, "final_model": current}

    histories = [
        {
            "events": [f"{actor}_{phase}" for actor, phase in order],
            "prepare_then_unconditional_publish": run(order, guarded=False),
            "guarded_publish": run(order, guarded=True),
        }
        for order in orders
    ]
    unsafe = sum(
        len(history["prepare_then_unconditional_publish"]["accepted"]) == 2
        for history in histories
    )
    assert len(histories) == 6 and unsafe == 4
    assert all(
        len(history["guarded_publish"]["accepted"]) == 1 for history in histories
    )
    assert all(
        history["guarded_publish"]["final_model"]["revision"] == 8
        for history in histories
    )
    return {
        "inputs": {"base": base, "requests": requests},
        "histories": histories,
        "counterexample": {"two_same_base_commits_in_unconditional_histories": unsafe},
        "candidate": {"guarded_histories_with_exactly_one_commit": len(histories)},
        "limit": "six two-command histories with an imposed atomic publication step; no threads, locks, database, crash recovery, ABA handling, or linearizability proof",
    }


def review_scope_and_authority():
    reviewed = {
        "action": "publish",
        "recipient": "team-a",
        "payload_digest": "payload-a",
        "model_incarnation": "invoice-a",
        "model_revision": 7,
    }
    cases = [
        ("reviewed_action", reviewed, True, reviewed),
        (
            "changed_payload",
            {**reviewed, "payload_digest": "payload-b"},
            True,
            reviewed,
        ),
        ("changed_recipient", {**reviewed, "recipient": "team-b"}, True, reviewed),
        ("changed_model", {**reviewed, "model_revision": 8}, True, reviewed),
        ("revoked_grant", reviewed, False, reviewed),
        ("missing_review", reviewed, True, None),
    ]
    outcomes = [
        {
            "case": label,
            "current_action": current,
            "current_grant_allows": granted,
            "review_scope_matches": approval == current,
            "execute_under_imposed_policy": granted and approval == current,
        }
        for label, current, granted, approval in cases
    ]
    grant_only = sum(outcome["current_grant_allows"] for outcome in outcomes)
    review_only = sum(outcome["review_scope_matches"] for outcome in outcomes)
    accepted = [
        outcome["case"]
        for outcome in outcomes
        if outcome["execute_under_imposed_policy"]
    ]
    assert grant_only == 5 and review_only == 2 and accepted == ["reviewed_action"]
    return {
        "inputs": {"review_scope": reviewed},
        "outcomes": outcomes,
        "counterexample": {
            "grant_only_accepts": grant_only,
            "review_only_accepts": review_only,
        },
        "candidate": {"current_grant_and_exact_review_accepts": accepted},
        "limit": "six supplied records under an exact-review policy; no human comprehension, authentic approval, cryptography, capability executor, one-shot consumption, or in-flight revocation",
    }


def history_identity_reuse():
    initial = {"incarnation": "invoice-a", "revision": 7, "commit": "c7", "quantity": 2}
    changed = {**initial, "revision": 8, "commit": "c8", "quantity": 3}
    rewound = {**initial, "commit": "c9"}
    restored_as_new = {**rewound, "revision": 9}
    other_branch = {**changed, "commit": "branch-b8", "quantity": 4}
    cases = [
        ("undo_rewinds_counter", initial, rewound),
        ("copied_fork", changed, other_branch),
        ("unchanged", initial, initial),
    ]
    outcomes = [
        {
            "case": label,
            "prepared_for": prepared,
            "current": current,
            "incarnation_revision_accepts": all(
                prepared[field] == current[field]
                for field in ("incarnation", "revision")
            ),
            "commit_identity_accepts": all(
                prepared[field] == current[field] for field in ("incarnation", "commit")
            ),
        }
        for label, prepared, current in cases
    ]
    assert initial["quantity"] == rewound["quantity"]
    assert all(outcome["incarnation_revision_accepts"] for outcome in outcomes)
    assert [outcome["commit_identity_accepts"] for outcome in outcomes] == [
        False,
        False,
        True,
    ]
    assert initial["revision"] != restored_as_new["revision"]
    return {
        "inputs": {
            "undo_values": [initial, changed, rewound],
            "restore_as_new_commit": restored_as_new,
        },
        "outcomes": outcomes,
        "counterexample": {
            "rewound_value_matches_original": True,
            "context_pair_can_recur": True,
        },
        "candidate": "keep a non-reused committed-history identity; undo can restore values under a new revision, forks need distinct commit/branch context",
        "limit": "three explicit comparisons with supplied commit tokens; no identity generation, persisted history, distributed clock, hash guarantees, or universal prohibition on pure-result reuse",
    }


def clock_domain_freshness():
    clock = {"id": "controller", "incarnation": "boot-a", "tick": 100}
    samples = [
        {
            "case": "fresh",
            "clock": "controller",
            "incarnation": "boot-a",
            "observed_at": 99,
        },
        {
            "case": "old",
            "clock": "controller",
            "incarnation": "boot-a",
            "observed_at": 90,
        },
        {
            "case": "other_clock",
            "clock": "sensor",
            "incarnation": "boot-a",
            "observed_at": 99,
        },
        {
            "case": "previous_boot",
            "clock": "controller",
            "incarnation": "boot-before",
            "observed_at": 99,
        },
        {
            "case": "future_same_clock",
            "clock": "controller",
            "incarnation": "boot-a",
            "observed_at": 101,
        },
    ]
    outcomes = []
    for sample in samples:
        age = clock["tick"] - sample["observed_at"]
        comparable = (
            sample["clock"] == clock["id"]
            and sample["incarnation"] == clock["incarnation"]
        )
        status = (
            "incomparable"
            if not comparable
            else "invalid_future"
            if age < 0
            else "fresh"
            if age <= 2
            else "stale"
        )
        outcomes.append(
            {
                "sample": sample,
                "number_only_fresh": 0 <= age <= 2,
                "clock_aware_status": status,
            }
        )
    assert sum(outcome["number_only_fresh"] for outcome in outcomes) == 3
    assert [outcome["clock_aware_status"] for outcome in outcomes] == [
        "fresh",
        "stale",
        "incomparable",
        "incomparable",
        "invalid_future",
    ]
    return {
        "inputs": {
            "current_clock": clock,
            "maximum_age": 2,
            "cross_clock_mapping": None,
        },
        "outcomes": outcomes,
        "counterexample": {"number_only_fresh_count": 3},
        "candidate": {
            "fresh_in_declared_clock_count": 1,
            "incomparable_is_not_known_stale": True,
        },
        "limit": "five supplied clock records with no cross-clock mapping or skew allowance; no real monotonic clock, synchronization, suspend handling, sensor trust, or physical safety",
    }


PROBES = [
    ("P01", domain_identity, ["H01"]),
    ("P02", incarnation_revision, ["H70"]),
    ("P03", draft_commit, ["H41"]),
    ("P04", inverse_projection, ["H15", "H51"]),
    ("P05", value_law_effect_trace, ["H66"]),
    ("P06", domain_and_evidence, ["H25", "H27"]),
    ("P07", guarded_preconditions, ["H52"]),
    ("P08", invariant_and_progress, ["H29", "H87"]),
    ("P09", run_epoch_order, ["H04", "H33"]),
    ("P10", cached_authority, ["H47", "H90"]),
    ("P11", uncertain_action, ["H69", "H72", "H87"]),
    ("P12", merged_invariant, ["H45"]),
    ("P13", lossy_projection, ["H16", "H40", "H44"]),
    ("P14", passive_bounded_inspection, ["H36", "H64", "H89"]),
    ("P15", source_offset_units, ["H77", "H78"]),
    ("P16", command_adapters, ["H09", "H13", "H76"]),
    ("P17", reference_frame_change, ["H81"]),
    ("P18", control_context, ["H85", "H86"]),
    ("P19", checked_publish_interleavings, ["H14", "H30", "H45"]),
    ("P20", review_scope_and_authority, ["H47", "H62", "H72", "H90"]),
    ("P21", history_identity_reuse, ["H14", "H46", "H70", "H71"]),
    ("P22", clock_domain_freshness, ["H53", "H55", "H85"]),
]


def report(observed_on):
    return {
        "schema": "nomi.research.interaction-probes.v1",
        "observed_on": observed_on.isoformat(),
        "python_version": platform.python_version(),
        "unicode_version": unicodedata.unidata_version,
        "evidence_kind": "original finite models and named host observations",
        "nomi_execution": False,
        "browser_execution": False,
        "device_execution": False,
        "foreign_service_execution": False,
        "probes": [
            {"id": probe_id, "name": probe.__name__, "atlas_cases": cases, **probe()}
            for probe_id, probe, cases in PROBES
        ],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--observed-on", type=date.fromisoformat)
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument("--output", type=Path, help="write a generated research capture")
    modes.add_argument(
        "--check", type=Path, help="verify an existing capture without rewriting it"
    )
    args = parser.parse_args()
    if not __debug__:
        parser.error("Run without Python's -O option; probe assertions are required.")
    if args.check:
        if args.observed_on:
            parser.error("--observed-on is only used when producing a capture")
        try:
            captured = json.loads(args.check.read_text(encoding="utf-8"))
            current = report(date.fromisoformat(captured["observed_on"]))
            for field in ("python_version", "unicode_version"):
                if not isinstance(captured[field], str) or not captured[field]:
                    raise ValueError(f"missing reported {field}")
        except (OSError, ValueError, KeyError, TypeError) as error:
            parser.error(f"Cannot read capture: {error}")

        # Preserve historical host metadata; compare every other field and its JSON type.
        versions = {"python_version", "unicode_version"}
        expected = json.dumps(
            {key: value for key, value in captured.items() if key not in versions},
            sort_keys=True,
        )
        actual = json.dumps(
            {key: value for key, value in current.items() if key not in versions},
            sort_keys=True,
        )
        if expected != actual:
            parser.error(
                "Capture differs from current probes; review changed outcomes before updating it."
            )
        print(
            f"Verified {len(PROBES)} local probes against {args.check}; "
            f"captured Python {captured['python_version']}, Unicode {captured['unicode_version']}; "
            f"current Python {current['python_version']}, Unicode {current['unicode_version']}"
        )
        return

    payload = (
        json.dumps(
            report(args.observed_on or date.today()), indent=2, ensure_ascii=True
        )
        + "\n"
    )
    if args.output:
        args.output.write_text(payload, encoding="utf-8")
        print(f"Captured {len(PROBES)} local probes in {args.output}")
    else:
        print(payload, end="")


if __name__ == "__main__":
    main()
