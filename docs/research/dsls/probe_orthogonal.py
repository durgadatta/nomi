"""Original finite-model research probes; no foreign DSL engine is invoked."""

import argparse
from datetime import date
from decimal import Decimal
from fractions import Fraction
from itertools import product
import json
import platform


def relation_multiplicity():
    left = ["a", "a", "b"]
    right = ["a", "a"]
    bag = [(x, y) for x in left for y in right if x == y]
    relation = {(x, y) for x in set(left) for y in set(right) if x == y}
    assert len(bag) == 4 and len(relation) == 1
    return {"left": left, "right": right, "bag_join": bag,
            "set_join": sorted(relation)}


def closure(edges):
    reached = set(edges)
    rounds = 0
    while True:
        expanded = reached | {(a, d) for a, b in reached
                              for c, d in reached if b == c}
        if expanded == reached:
            return reached, rounds
        reached = expanded
        rounds += 1


def finite_deduction():
    edges = [("a", "b"), ("b", "c"), ("c", "a"), ("c", "d")]
    one_pass = set(edges) | {(a, d) for a, b in edges
                             for c, d in edges if b == c}
    reached, rounds = closure(edges)
    reordered, _ = closure(reversed(edges))
    idempotent, _ = closure(reached)
    assert one_pass != reached and reached == reordered == idempotent
    assert len(reached) == 12
    return {"edges": edges, "one_pass": sorted(one_pass),
            "fixed_point": sorted(reached), "expanding_rounds": rounds,
            "reordering_preserved": reached == reordered,
            "idempotent": reached == idempotent,
            "fragment": "positive reachability over four finite nodes"}


def knowledge_assumptions():
    facts = {"employee(Ada)"}
    query = "clearance(Ada)"
    compatible_worlds = [facts, facts | {query}]
    possible = sorted({query in world for world in compatible_worlds})
    assert possible == [False, True] and query not in facts
    return {"facts": sorted(facts), "query": query,
            "closed_world_lookup": query in facts,
            "compatible_worlds": [sorted(w) for w in compatible_worlds],
            "possible_truth_values": possible,
            "open_world_entailment_status": "undetermined",
            "limit": "two explicit worlds; not an OWL implementation"}


def constraint_evidence():
    candidates = list(product(range(2), repeat=2))
    feasible = [assignment for assignment in candidates
                if assignment[0] != assignment[1]]
    costs = [(2 * x + y, (x, y)) for x, y in feasible]
    optimum_cost, optimum = min(costs)
    checked_prefix = candidates[:1]
    prefix_answers = [a for a in checked_prefix if a[0] != a[1]]
    impossible = [a for a in candidates
                  if a[0] != a[1] and a == (0, 0)]
    assert feasible == [(0, 1), (1, 0)]
    assert not prefix_answers and len(checked_prefix) < len(candidates)
    assert not impossible
    return {"domain": [0, 1], "constraint": "job slots differ",
            "check_assignment_0_0": False, "feasible_assignments": feasible,
            "objective": "2 * slot_a + slot_b", "optimal_assignment": optimum,
            "optimal_cost": optimum_cost,
            "budgeted_search": {"checked": checked_prefix, "answers": prefix_answers,
                                "status": "unknown", "unexplored": 3},
            "fully_enumerated_contradiction": "unsatisfiable"}


def grouped_windows(events, clock):
    windows = {}
    for event in events:
        start = event[clock] // 10 * 10
        windows.setdefault(f"[{start},{start + 10})", []).append(event["id"])
    return {key: sorted(ids) for key, ids in sorted(windows.items())}


def temporal_windows():
    events = [{"id": "e1", "event_time": 2, "arrival_time": 2},
              {"id": "e2", "event_time": 8, "arrival_time": 12},
              {"id": "e3", "event_time": 12, "arrival_time": 13}]
    event_windows = grouped_windows(events, "event_time")
    arrival_windows = grouped_windows(events, "arrival_time")
    late = [e["id"] for e in events
            if e["event_time"] < 10 and e["arrival_time"] >= 10]
    retained = [e for e in events if e["id"] not in late]
    assert event_windows != arrival_windows and late == ["e2"]
    assert event_windows == grouped_windows(reversed(events), "event_time")
    return {"events": events, "endpoints": "left-closed, right-open",
            "event_time_windows": event_windows,
            "arrival_time_windows": arrival_windows,
            "imposed_close_rule": "first window closes at arrival time 10",
            "late_ids": late, "drop_late": grouped_windows(retained, "event_time"),
            "update_late": event_windows,
            "limit": "fixed imposed policy; not a Beam runner/watermark test"}


def arithmetic_theory():
    float_left = (1e16 + -1e16) + 1.0
    float_right = 1e16 + (-1e16 + 1.0)
    a, b, c = Decimal("1e16"), Decimal("-1e16"), Decimal("1")
    decimal_left, decimal_right = (a + b) + c, a + (b + c)
    assert float_left == 1.0 and float_right == 0.0
    assert decimal_left == decimal_right == 1
    return {"inputs": ["1e16", "-1e16", "1"],
            "float_left_association": float_left,
            "float_right_association": float_right,
            "decimal_left_association": str(decimal_left),
            "decimal_right_association": str(decimal_right),
            "limit": "one host arithmetic fixture, not all numeric laws"}


def token_exclusion():
    transitions = {"A": "active_a", "B": "active_b"}
    initial = {"free": 1, "active_a": 0, "active_b": 0}

    def enabled(marking):
        return sorted(transitions) if marking["free"] >= 1 else []

    def fire(marking, transition):
        assert transition in enabled(marking)
        result = dict(marking)
        result["free"] -= 1
        result[transitions[transition]] += 1
        return result

    after_a = fire(initial, "A")
    released = {"free": 1, "active_a": 0, "active_b": 0}
    assert enabled(initial) == ["A", "B"] and enabled(after_a) == []
    assert sum(initial.values()) == sum(after_a.values()) == 1
    return {"initial_marking": initial, "initially_enabled": enabled(initial),
            "after_A": after_a, "enabled_after_A": enabled(after_a),
            "after_A_releases_token": released, "enabled_after_release": enabled(released),
            "dependency_only_ready_jobs": ["A", "B"],
            "limit": "original one-token model; not PNML/BPMN conformance"}


def probability_conditioning():
    prior = {"A": Fraction(1, 2), "B": Fraction(1, 2)}
    likelihood = {"A": Fraction(3, 4), "B": Fraction(1, 4)}
    weights = {state: prior[state] * likelihood[state] for state in prior}
    evidence = sum(weights.values())
    posterior = {state: weight / evidence for state, weight in weights.items()}
    assert evidence == Fraction(1, 2)
    assert posterior == {"A": Fraction(3, 4), "B": Fraction(1, 4)}
    return {"prior": {k: str(v) for k, v in prior.items()},
            "observation_likelihood": {k: str(v) for k, v in likelihood.items()},
            "unnormalized_weights": {k: str(v) for k, v in weights.items()},
            "evidence_probability": str(evidence),
            "posterior": {k: str(v) for k, v in posterior.items()},
            "random_draws_performed": 0,
            "limit": "exact finite enumeration; not Stan inference or PRISM checking"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--observed-on", type=date.fromisoformat, default=date.today())
    args = parser.parse_args()
    probes = [relation_multiplicity, finite_deduction, knowledge_assumptions,
              constraint_evidence, temporal_windows, arithmetic_theory,
              token_exclusion, probability_conditioning]
    report = {"observed_on": args.observed_on.isoformat(),
              "python_version": platform.python_version(),
              "evidence_kind": "original finite models and host arithmetic",
              "foreign_runtime_tests": [],
              "probes": {probe.__name__: probe() for probe in probes}}
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
