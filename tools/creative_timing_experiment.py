"""Finite supplied-model experiment; neither a Nomi evaluator nor an audio host."""

from __future__ import annotations

import argparse
from dataclasses import dataclass, replace
from fractions import Fraction
import json
from pathlib import Path
import platform


FIXTURES = (
    Path(__file__).resolve().parents[1] / "docs/research/interfaces/timing_cases.json"
)
SCOPE = "finite supplied models; no Nomi, device, concurrency or human evidence"


def ratio(value, *, positive=False):
    if (
        not isinstance(value, list)
        or len(value) != 2
        or any(type(part) is not int for part in value)
        or value[1] <= 0
    ):
        raise ValueError("expected [integer numerator, positive integer denominator]")
    result = Fraction(*value)
    if result < 0 or (positive and result == 0):
        raise ValueError("value is outside the declared domain")
    return result


def label(value):
    if not isinstance(value, str) or not value:
        raise ValueError("identity must be nonempty text")
    return value


def revision(value):
    if type(value) is not int or value < 0:
        raise ValueError("revision must be a nonnegative integer")
    return value


@dataclass(frozen=True)
class Note:
    identity: str
    onset: Fraction
    duration: Fraction


@dataclass(frozen=True)
class Score:
    incarnation: str
    revision: int
    basis: str
    tempo: Fraction
    notes: tuple[Note, ...]

    @classmethod
    def from_record(cls, record):
        basis = record["basis"]
        if basis not in ("beats", "milliseconds"):
            raise ValueError("unknown coordinate basis")
        notes = tuple(
            Note(
                label(note["id"]),
                ratio(note["onset"]),
                ratio(note["duration"], positive=True),
            )
            for note in record["notes"]
        )
        if len({note.identity for note in notes}) != len(notes):
            raise ValueError("duplicate note identity")
        return cls(
            label(record["incarnation"]),
            revision(record["revision"]),
            basis,
            ratio(record["tempo"], positive=True),
            notes,
        )

    def schedule(self):
        scale = Fraction(60000) / self.tempo if self.basis == "beats" else Fraction(1)
        events = []
        for note in self.notes:
            events.append((note.onset * scale, "on", note.identity))
            events.append(((note.onset + note.duration) * scale, "off", note.identity))
        # This tie policy belongs to the experiment, not to Nomi or a device.
        return sorted(events, key=lambda event: (event[0], event[1] != "off", event[2]))

    def describe(self):
        return {
            "incarnation": self.incarnation,
            "revision": self.revision,
            "basis": self.basis,
            "tempo": str(self.tempo),
            "notes": [
                {
                    "id": note.identity,
                    "onset": str(note.onset),
                    "duration": str(note.duration),
                }
                for note in self.notes
            ],
        }


def change_note(score, proposal):
    if label(proposal["base_incarnation"]) != score.incarnation:
        return score, "wrong_incarnation"
    if revision(proposal["base_revision"]) != score.revision:
        return score, "stale_revision"
    if proposal["basis"] != score.basis:
        return score, "wrong_basis"
    identity = label(proposal["note_id"])
    if identity not in {note.identity for note in score.notes}:
        return score, "unknown_note"
    field = proposal["field"]
    if field not in ("onset", "duration"):
        return score, "unknown_note_field"
    try:
        value = ratio(proposal["value"], positive=field == "duration")
    except ValueError:
        return score, "invalid_draft"
    notes = tuple(
        replace(note, **{field: value}) if note.identity == identity else note
        for note in score.notes
    )
    return replace(score, revision=score.revision + 1, notes=notes), "committed"


def wire(events):
    return [[str(instant), kind, identity] for instant, kind, identity in events]


class Run:
    def __init__(self, score):
        self.score = score
        self.events = score.schedule()
        self.clock = Fraction(0)
        self.cursor = 0
        self.stopped = False
        self.delivered = []

    def advance(self, instant):
        if instant < self.clock:
            return "time_reversal_refused"
        self.clock = instant
        if self.stopped:
            return "delivery_stopped"
        while self.cursor < len(self.events):
            event = self.events[self.cursor]
            if event[0] > instant:
                break
            self.delivered.append(event)
            self.cursor += 1
        return "advanced"

    def describe(self, current):
        if self.score.incarnation != current.incarnation:
            relation = "different_incarnation"
        elif self.score.revision != current.revision:
            relation = "older_revision"
        else:
            relation = "current"
        unclosed = set()
        for _, kind, identity in self.delivered:
            if kind == "on":
                unclosed.add(identity)
            else:
                unclosed.discard(identity)
        return {
            "incarnation": self.score.incarnation,
            "revision": self.score.revision,
            "clock": str(self.clock),
            "delivery_stopped": self.stopped,
            "all_planned_events_delivered": self.cursor == len(self.events),
            "delivered": wire(self.delivered),
            "unclosed_note_ids": sorted(unclosed),
            "relation_to_current": relation,
            "external_outcome": "unobserved",
        }


def run_case(models, case):
    current = models[case["model"]]
    incarnations = {current.incarnation}
    runs = {}
    statuses = []
    drafts = []
    inspections = []
    for step in case["steps"]:
        operation = step["op"]
        if operation == "tempo":
            try:
                tempo = ratio(step["value"], positive=True)
            except ValueError:
                statuses.append("invalid_tempo")
                continue
            current = replace(current, revision=current.revision + 1, tempo=tempo)
            status = "committed"
        elif operation == "note_change":
            current, status = change_note(current, step)
            if status == "invalid_draft":
                drafts.append(
                    {
                        "note_id": step["note_id"],
                        "field": step["field"],
                        "value": step["value"],
                    }
                )
        elif operation == "ambiguous":
            status = "needs_clarification"
        elif operation == "reset":
            replacement = models[step["model"]]
            if replacement.incarnation in incarnations:
                status = "reused_incarnation"
            else:
                current = replacement
                incarnations.add(current.incarnation)
                status = "reset"
        elif operation == "run":
            identity = label(step["run_id"])
            if identity in runs:
                raise ValueError("run identity cannot be reused")
            runs[identity] = Run(current)
            status = "run_snapshot_created"
        elif operation == "advance":
            status = runs[step["run_id"]].advance(ratio(step["milliseconds"]))
        elif operation == "stop":
            runs[step["run_id"]].stopped = True
            status = "delivery_stopped"
        elif operation == "inspect":
            inspections.append(wire(current.schedule()))
            status = "inspected"
        else:
            raise ValueError(f"unknown experiment operation: {operation}")
        statuses.append(status)
    return {
        "model": current.describe(),
        "schedule": wire(current.schedule()),
        "statuses": statuses,
        "drafts": drafts,
        "inspections": inspections,
        "runs": {identity: run.describe(current) for identity, run in runs.items()},
    }


def distinct_keys(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def load_fixtures(path=FIXTURES):
    with path.open("rb") as stream:
        payload = stream.read(65537)
    if len(payload) > 65536:
        raise ValueError("experiment fixture exceeds 64 KiB")
    document = json.loads(payload, object_pairs_hook=distinct_keys)
    if type(document["schema_version"]) is not int or document["schema_version"] != 1:
        raise ValueError("unsupported fixture version")
    models = {
        name: Score.from_record(record) for name, record in document["models"].items()
    }
    cases = document["cases"]
    if not models or not cases:
        raise ValueError("experiment needs models and cases")
    identities = [label(case["id"]) for case in cases]
    if len(set(identities)) != len(identities):
        raise ValueError("duplicate case identity")
    for case in cases:
        if case["model"] not in models or not case["expect"]:
            raise ValueError("case needs a known model and nonempty expectations")
    return models, cases


def same_value(actual, expected):
    if type(actual) is not type(expected):
        return False
    if isinstance(actual, list):
        return len(actual) == len(expected) and all(
            same_value(left, right) for left, right in zip(actual, expected)
        )
    if isinstance(actual, dict):
        return actual.keys() == expected.keys() and all(
            same_value(value, expected[key]) for key, value in actual.items()
        )
    return actual == expected


def differences(observation, expectations):
    result = {}
    for path, expected in expectations.items():
        actual = observation
        for part in path.split("."):
            if not isinstance(actual, dict) or part not in actual:
                raise ValueError(f"unknown expectation path: {path}")
            actual = actual[part]
        if not same_value(actual, expected):
            result[path] = {"expected": expected, "actual": actual}
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fixtures", type=Path, default=FIXTURES)
    parser.add_argument("--case", help="inspect or check one named case")
    parser.add_argument(
        "--check", action="store_true", help="compare literal expectations"
    )
    arguments = parser.parse_args(argv)
    try:
        models, cases = load_fixtures(arguments.fixtures)
        if arguments.case:
            cases = [case for case in cases if case["id"] == arguments.case]
            if not cases:
                raise ValueError(f"unknown case: {arguments.case}")
        observations = []
        failed = False
        for case in cases:
            observation = run_case(models, case)
            mismatch = differences(observation, case["expect"])
            failed = failed or bool(mismatch)
            if arguments.check:
                print(f"{'FAIL' if mismatch else 'PASS'} {case['id']}")
                if mismatch:
                    print(json.dumps(mismatch, indent=2))
            observations.append({"id": case["id"], "observation": observation})
    except (OSError, ValueError, KeyError, TypeError, RecursionError) as error:
        parser.error(str(error))
    if arguments.check:
        print(
            f"Checked {len(cases)} finite cases on Python {platform.python_version()}; {SCOPE}."
        )
    else:
        print(
            json.dumps(
                {
                    "scope": SCOPE,
                    "host": {"python": platform.python_version()},
                    "execution": {
                        "nomi": False,
                        "device": False,
                        "concurrency": False,
                        "human": False,
                    },
                    "cases": observations,
                },
                indent=2,
            )
        )
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
