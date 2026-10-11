"""Finite signed-rule support, revision and independent certificate replay.

This is a non-explosive supplied-rule profile, not classical entailment, Bayesian
belief, AGM revision or truth about the world. Quoted reports are inert by default.
"""

from dataclasses import asdict, dataclass, replace
import hashlib
from itertools import product
import json

from tools.scoped_terms import Identity

PROFILE = "finite-signed-rule-support-v1"
MAX_ATOMS = 16
MAX_RULES = 32
MAX_REPORTS = 32
MAX_ATTEMPTS = 50000


class Refused(ValueError):
    """Malformed, stale or outside the finite profile."""


@dataclass(frozen=True, order=True)
class SignedAtom:
    atom: Identity
    positive: bool = True

    def __post_init__(self):
        if type(self.atom) is not Identity or type(self.positive) is not bool:
            raise Refused("signed atom requires qualified identity and Boolean sign")

    def opposite(self):
        return SignedAtom(self.atom, not self.positive)


@dataclass(frozen=True)
class Rule:
    identity: Identity
    premises: tuple[SignedAtom, ...]
    conclusion: SignedAtom

    def __post_init__(self):
        if type(self.identity) is not Identity or type(self.premises) is not tuple:
            raise Refused("rule requires identity and immutable premises")
        if len(self.premises) > 8 or any(
            type(x) is not SignedAtom for x in self.premises
        ):
            raise Refused("rule premises outside capacity/profile")
        if (
            len(set(self.premises)) != len(self.premises)
            or type(self.conclusion) is not SignedAtom
        ):
            raise Refused("duplicate or invalid rule literal")


@dataclass(frozen=True)
class Report:
    identity: Identity
    claim: SignedAtom
    origin: Identity

    def __post_init__(self):
        if (
            type(self.identity) is not Identity
            or type(self.origin) is not Identity
            or type(self.claim) is not SignedAtom
        ):
            raise Refused("report requires claim and qualified source identities")


@dataclass(frozen=True)
class Ledger:
    owner: str
    revision: int
    atoms: tuple[Identity, ...]
    rules: tuple[Rule, ...] = ()
    reports: tuple[Report, ...] = ()
    endorsed: tuple[Identity, ...] = ()
    parent: str | None = None

    def __post_init__(self):
        Identity(self.owner, "ledger", "context")
        if type(self.revision) is not int or not 0 <= self.revision < 2**63:
            raise Refused("invalid ledger revision")
        for values, kind, cap in (
            (self.atoms, Identity, MAX_ATOMS),
            (self.rules, Rule, MAX_RULES),
            (self.reports, Report, MAX_REPORTS),
            (self.endorsed, Identity, MAX_REPORTS),
        ):
            if (
                type(values) is not tuple
                or len(values) > cap
                or any(type(x) is not kind for x in values)
            ):
                raise Refused(
                    "immutable profile values exceed capacity or have wrong type"
                )
        if len(set(self.atoms)) != len(self.atoms):
            raise Refused("duplicate atom identity")
        for values in (self.rules, self.reports):
            if len({x.identity for x in values}) != len(values):
                raise Refused("duplicate declaration identity")
        if len(set(self.endorsed)) != len(self.endorsed) or not set(self.endorsed) <= {
            x.identity for x in self.reports
        }:
            raise Refused("endorsement does not name distinct captured reports")
        literals = [x.claim for x in self.reports]
        literals += [
            literal
            for rule in self.rules
            for literal in (*rule.premises, rule.conclusion)
        ]
        if any(x.atom not in self.atoms for x in literals):
            raise Refused("literal outside exact atom signature/revision")
        if self.parent is not None and (
            type(self.parent) is not str
            or len(self.parent) != 64
            or any(c not in "0123456789abcdef" for c in self.parent)
        ):
            raise Refused("invalid parent fingerprint")


def fingerprint(ledger):
    if type(ledger) is not Ledger:
        raise Refused("expected ledger")
    record = asdict(ledger)
    for name in ("atoms", "rules", "reports", "endorsed"):
        record[name] = sorted(record[name], key=lambda x: json.dumps(x, sort_keys=True))
    return hashlib.sha256(
        json.dumps({"profile": PROFILE, "ledger": record}, sort_keys=True).encode()
    ).hexdigest()


def revise(ledger, *, endorsed=None, rules=None, reports=None):
    """New immutable context; old conditional evidence remains in its old context."""
    return replace(
        ledger,
        revision=ledger.revision + 1,
        parent=fingerprint(ledger),
        endorsed=ledger.endorsed if endorsed is None else endorsed,
        rules=ledger.rules if rules is None else rules,
        reports=ledger.reports if reports is None else reports,
    )


@dataclass(frozen=True)
class Support:
    reports: frozenset[Identity]
    rules: frozenset[Identity]

    def __post_init__(self):
        if any(
            type(values) is not frozenset
            or any(type(x) is not Identity for x in values)
            for values in (self.reports, self.rules)
        ):
            raise Refused("support requires immutable qualified dependencies")


@dataclass(frozen=True)
class Derivation:
    context: str
    profile: str
    status: str
    attempts: int
    facts: tuple[tuple[SignedAtom, tuple[Support, ...]], ...]


def _support_key(support):
    return tuple(sorted(support.reports)), tuple(sorted(support.rules))


def derive(ledger, budget=MAX_ATTEMPTS):
    context = fingerprint(ledger)
    if type(budget) is not int or not 1 <= budget <= MAX_ATTEMPTS:
        raise Refused("invalid derivation budget")
    facts = {}
    for report in sorted(ledger.reports, key=lambda x: x.identity):
        if report.identity in ledger.endorsed:
            facts.setdefault(report.claim, set()).add(
                Support(frozenset((report.identity,)), frozenset())
            )
    attempts = 0

    def result(status):
        return Derivation(
            context,
            PROFILE,
            status,
            attempts,
            tuple(
                (literal, tuple(sorted(supports, key=_support_key)))
                for literal, supports in sorted(facts.items())
            ),
        )

    changed = True
    while changed:
        changed = False
        for rule in sorted(ledger.rules, key=lambda x: x.identity):
            choices = [
                tuple(sorted(facts.get(x, ()), key=_support_key)) for x in rule.premises
            ]
            for combination in product(*choices):
                if attempts == budget:
                    return result("incomplete")
                attempts += 1
                candidate = Support(
                    frozenset().union(*(x.reports for x in combination)),
                    frozenset((rule.identity,)).union(*(x.rules for x in combination)),
                )
                existing = facts.setdefault(rule.conclusion, set())
                if any(
                    x.reports <= candidate.reports and x.rules <= candidate.rules
                    for x in existing
                ):
                    continue
                dominated = {
                    x
                    for x in existing
                    if candidate.reports <= x.reports and candidate.rules <= x.rules
                }
                existing.difference_update(dominated)
                existing.add(candidate)
                changed = True
    return result("complete")


def _reachable(ledger, reports, rules):
    """Independent set-only replay; does not enumerate derivations/support sets."""
    facts = {x.claim for x in ledger.reports if x.identity in reports}
    pending = [x for x in ledger.rules if x.identity in rules]
    while pending:
        fired = [x for x in pending if set(x.premises) <= facts]
        if not fired:
            break
        facts.update(x.conclusion for x in fired)
        pending = [x for x in pending if x not in fired]
    return facts


def verify(ledger, derivation):
    if (
        type(derivation) is not Derivation
        or derivation.profile != PROFILE
        or derivation.context != fingerprint(ledger)
    ):
        raise Refused("stale context or different reasoning profile")
    if (
        derivation.status not in ("complete", "incomplete")
        or type(derivation.attempts) is not int
        or not 0 <= derivation.attempts <= MAX_ATTEMPTS
    ):
        raise Refused("invalid derivation coverage")
    if type(derivation.facts) is not tuple or len(derivation.facts) > 2 * MAX_ATOMS:
        raise Refused("invalid derivation facts")
    observed = set()
    total_supports = 0
    rule_ids = frozenset(x.identity for x in ledger.rules)
    for entry in derivation.facts:
        if type(entry) is not tuple or len(entry) != 2:
            raise Refused("invalid fact entry")
        literal, supports = entry
        if (
            type(literal) is not SignedAtom
            or literal.atom not in ledger.atoms
            or literal in observed
        ):
            raise Refused("duplicate or out-of-context derived literal")
        observed.add(literal)
        if (
            type(supports) is not tuple
            or not supports
            or len(supports) > MAX_ATTEMPTS
            or any(type(x) is not Support for x in supports)
        ):
            raise Refused("missing or invalid support")
        total_supports += len(supports)
        if total_supports > MAX_ATTEMPTS + MAX_REPORTS:
            raise Refused("certificate exceeds support capacity")
        for support in supports:
            if (
                not support.reports <= set(ledger.endorsed)
                or not support.rules <= rule_ids
            ):
                raise Refused("support names unendorsed or foreign declarations")
            if literal not in _reachable(ledger, support.reports, support.rules):
                raise Refused("support does not replay to its claimed literal")
    if derivation.status == "complete" and observed != _reachable(
        ledger, set(ledger.endorsed), rule_ids
    ):
        raise Refused("claimed complete closure omits or invents facts")
    return True


def assess(ledger, derivation, question):
    verify(ledger, derivation)
    if type(question) is not SignedAtom or question.atom not in ledger.atoms:
        raise Refused("question outside signature")
    facts = dict(derivation.facts)
    yes, no = facts.get(question, ()), facts.get(question.opposite(), ())
    if yes and no:
        status = "conflict"
    elif yes:
        status = "supported"
    elif no:
        status = "opposed"
    else:
        status = (
            "not-established"
            if derivation.status == "complete"
            else "search-incomplete"
        )
    sources = {x.identity: x.origin for x in ledger.reports}

    def describe(support):
        return {
            "reports": [asdict(x) for x in sorted(support.reports)],
            "rules": [asdict(x) for x in sorted(support.rules)],
            "origins": [
                asdict(x) for x in sorted({sources[x] for x in support.reports})
            ],
        }

    return {
        "profile": PROFILE,
        "context": derivation.context,
        "question": asdict(question),
        "status": status,
        "coverage": derivation.status,
        "support": [describe(x) for x in yes],
        "opposition": [describe(x) for x in no],
        "scope": "supplied-rule support only; no world truth or probability",
    }


def example():
    a, b, c = (Identity("example-theory", "1", x) for x in ("a", "b", "c"))
    p, q = Identity("reports", "1", "p"), Identity("reports", "1", "q")
    reports = (
        Report(p, SignedAtom(a), Identity("source", "1", "first")),
        Report(q, SignedAtom(a), Identity("source", "1", "second")),
    )
    rule = Rule(Identity("rules", "1", "a-to-b"), (SignedAtom(a),), SignedAtom(b))
    ledger = Ledger("example", 0, (a, b, c), (rule,), reports)
    endorsed = revise(ledger, endorsed=(p, q))
    withdrawn = revise(endorsed, endorsed=(q,))
    return {
        "quoted": assess(ledger, derive(ledger), SignedAtom(b)),
        "endorsed": assess(endorsed, derive(endorsed), SignedAtom(b)),
        "one-support-withdrawn": assess(withdrawn, derive(withdrawn), SignedAtom(b)),
    }


def main():
    print(json.dumps(example(), indent=2))


if __name__ == "__main__":
    main()
