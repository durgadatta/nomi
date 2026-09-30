"""Symbolic resource-design experiment; not a Nomi evaluator or type checker."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from prototype.runtime.diagnostics import Diagnostic

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "docs/design/fixtures/resource_scope_cases.json"
NORMAL = {"ok", "return", "break", "continue"}
PRIORITY = {"err": 1, "cancel": 2, "panic": 3}


def validate_case(case: dict[str, Any]) -> None:
    def validate_outcome(outcome: dict[str, Any]) -> None:
        if outcome.get("kind") not in NORMAL | PRIORITY.keys():
            raise ValueError("unknown outcome kind")
        if outcome["kind"] in PRIORITY and not isinstance(outcome.get("cause"), str):
            raise ValueError("failure needs a symbolic cause id")

    if not isinstance(case.get("id"), str) or not case["id"]:
        raise ValueError("case needs an id")
    validate_outcome(case["body"])
    resources = case.get("resources", [])
    defers = case.get("defers", [])
    names = [item["name"] for item in resources + defers]
    if len(names) != len(set(names)) or any(
        not isinstance(n, str) or not n for n in names
    ):
        raise ValueError("resource and defer names must be unique nonempty strings")
    for item in resources + defers:
        validate_outcome(item.get("exit", {"kind": "ok"}))
        if "enter" in item:
            validate_outcome(item["enter"])
    if not set(case.get("cancel_during", [])) <= set(names):
        raise ValueError("cancellation target is not a resource or defer")


def load_cases(path: Path = FIXTURES) -> dict[str, Any]:
    packet = json.loads(path.read_text(encoding="utf-8"))
    if packet.get("schema_version") != 1:
        raise ValueError("unsupported resource experiment schema version")
    cases = packet["cases"]
    if not cases or len({case["id"] for case in cases}) != len(cases):
        raise ValueError("case ids must be nonempty and unique")
    for case in cases:
        validate_case(case)
    for escape in packet["escapes"]:
        if escape["lifetime"] not in {"inside", "outside"}:
            raise ValueError("unknown supplied lifetime fact")
        if not isinstance(escape["checked"], bool):
            raise TypeError("checked must be Bool")
    return packet


def run_case(case: dict[str, Any], candidate: str = "typed") -> dict[str, Any]:
    if candidate not in {"typed", "envelope"}:
        raise ValueError("unknown cleanup candidate")
    validate_case(case)
    trace: list[str] = []
    issues: list[dict[str, str]] = []
    acquired: list[dict[str, Any]] = []
    actions: list[tuple[str, dict[str, Any]]] = []
    leases: dict[str, bool] = {}
    pending = case["body"]["kind"]

    def record(outcome: dict[str, Any], phase: str) -> None:
        kind = outcome["kind"]
        if kind not in PRIORITY:
            return
        # Repeated cancellation is observable in the trace, not a new root cause.
        if kind == "cancel" and any(issue["kind"] == "cancel" for issue in issues):
            return
        issues.append({"kind": kind, "cause": outcome["cause"], "phase": phase})

    for resource in case.get("resources", []):
        name = resource["name"]
        trace.append(f"enter:{name}")
        entered = resource.get("enter", {"kind": "ok"})
        if entered["kind"] in PRIORITY:
            trace.append(f"enter-failed:{name}")
            pending = entered["kind"]
            record(entered, "enter")
            break
        leases[name] = True
        acquired.append(resource)
        actions.append(("close", resource))
        trace.append(f"ready:{name}")
    else:
        for deferred in case.get("defers", []):
            trace.append(f"register:{deferred['name']}")
            actions.append(("defer", deferred))
        trace.append(f"body:{pending}")
        record(case["body"], "body")

    for action, item in reversed(actions):
        name = item["name"]
        if action == "close":
            leases[name] = False
            trace.append(f"revoke:{name}")
        trace.append(f"{action}:{name}")
        if name in case.get("cancel_during", []):
            trace.append(f"cancel-request:{name}")
            record({"kind": "cancel", "cause": "cancel"}, "cleanup")
        outcome = item.get("exit", {"kind": "ok"})
        record(outcome, "cleanup")
        trace.append(f"{action}-done:{name}:{outcome['kind']}")

    primary_index = (
        max(range(len(issues)), key=lambda i: PRIORITY[issues[i]["kind"]])
        if issues
        else None
    )
    primary = issues[primary_index] if primary_index is not None else None
    kind = primary["kind"] if primary else pending
    channel = (
        "result" if kind == "err" else kind if kind in {"panic", "cancel"} else "normal"
    )
    if (
        candidate == "envelope"
        and channel == "result"
        and any(i["phase"] == "cleanup" for i in issues)
    ):
        channel = "scope-failure"
    trace.append(f"observe:{channel}:{kind}")
    record_outcome = {
        "channel": channel,
        "kind": kind,
        "pending_transfer": pending,
        "primary": primary,
        "secondary": [issue for i, issue in enumerate(issues) if i != primary_index],
    }
    diagnostic = None
    if primary:
        diagnostic = Diagnostic(
            message="Scope completion failed; all registered cleanup was attempted.",
            code="NOMI-RESOURCE-OUTCOME-CANDIDATE",
            phase="design-experiment",
            span=case.get("span"),
            details=record_outcome,
        ).to_record()
    return {
        "id": case["id"],
        "candidate": candidate,
        "trace": trace,
        "outcome": record_outcome,
        "acquired": [item["name"] for item in acquired],
        "leases_after": leases,
        "diagnostic": diagnostic,
    }


def assess_escape(case: dict[str, Any], policy: str) -> dict[str, str]:
    """Compare policies given a supplied lifetime fact; do not infer lifetimes."""
    if policy not in {"static", "dynamic"}:
        raise ValueError("unknown escape policy")
    outside = case["lifetime"] == "outside"
    rejected = outside and case["checked"] and policy == "static"
    return {
        "id": case["id"],
        "check": "reject" if rejected else "allow",
        "use": "not-run" if rejected else "closed-handle" if outside else "allowed",
    }


def check_packet(packet: dict[str, Any]) -> tuple[list[dict[str, Any]], list[str]]:
    results = []
    failures = []
    for case in packet["cases"]:
        for candidate in ("typed", "envelope"):
            result = run_case(case, candidate)
            results.append(result)
            expected = case["expected"]
            actual = result["outcome"]
            if (
                actual["kind"] != expected["kind"]
                or actual["channel"] != expected[candidate]
            ):
                failures.append(f"{case['id']}:{candidate}: completion mismatch")
            causes = ([actual["primary"]["cause"]] if actual["primary"] else []) + [
                i["cause"] for i in actual["secondary"]
            ]
            if causes != expected["causes"]:
                failures.append(f"{case['id']}:{candidate}: cause mismatch")
            if (
                candidate == "typed"
                and "trace" in expected
                and result["trace"] != expected["trace"]
            ):
                failures.append(f"{case['id']}: trace mismatch")
            for name in result["acquired"]:
                if (
                    result["trace"].count(f"close:{name}") != 1
                    or result["leases_after"][name]
                ):
                    failures.append(f"{case['id']}:{name}: release/lease mismatch")
    for case in packet["escapes"]:
        for policy in ("static", "dynamic"):
            result = assess_escape(case, policy)
            if [result["check"], result["use"]] != case["expected"][policy]:
                failures.append(f"{case['id']}:{policy}: escape mismatch")
    return results, failures


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit candidate traces and diagnostic records.",
    )
    args = parser.parse_args(argv)
    packet = load_cases()
    results, failures = check_packet(packet)
    if args.json:
        escapes = [
            {"policy": policy, **assess_escape(case, policy)}
            for case in packet["escapes"]
            for policy in ("static", "dynamic")
        ]
        print(
            json.dumps(
                {
                    "schema_version": 1,
                    "results": results,
                    "escapes": escapes,
                    "failures": failures,
                },
                indent=2,
            )
        )
    else:
        print(
            f"{'FAIL' if failures else 'PASS'} {len(results)} candidate traces, {len(packet['escapes']) * 2} supplied-fact escape comparisons."
        )
        for failure in failures:
            print(failure)
        print(
            "Symbolic design evidence only; no Nomi parsing, lifetime analysis, or async runtime was exercised."
        )
    return int(bool(failures))


if __name__ == "__main__":
    raise SystemExit(main())
