"""Bounded contingent inquiry with conservative bounds and explicit stopping.

Reuses captured journals, conditional beliefs, kernels and losses. Fresh trials
follow the journal's declared conditional-independence assumption. Policies are
prospective values; they do not execute measurements or grant authority.
"""

import argparse
from dataclasses import dataclass
from fractions import Fraction as F
import json

from tools import adaptive_inquiry as a
from tools import finite_inquiry as q
from tools import scoped_terms as t

PROFILE = "finite-contingent-inquiry-policy-v1"


@dataclass(frozen=True)
class Option:
    question: t.Identity
    inquiry: q.Inquiry
    children: tuple["Node | None", ...]
    lower: F
    upper: F


@dataclass(frozen=True)
class Node:
    identity: t.Identity
    belief: q.Measure
    remaining: int
    expanded: bool
    complete: bool
    lower: F
    upper: F
    stop: q.Decision
    options: tuple[Option, ...]
    incumbents: tuple[t.Identity, ...]


@dataclass(frozen=True)
class Policy:
    context: str
    coverage: str
    expanded: int
    estimate: a.Estimate
    root: Node | None


def context(journal, questions, objective, horizon, budget):
    base = a.plan_context(journal, questions, objective)
    if len(questions) > 3:
        raise t.Refused("contingent profile admits up to three query methods")
    if type(horizon) is not int or not 0 <= horizon <= 3:
        raise t.Refused("contingent horizon must be zero to three queries")
    if type(budget) is not int or not 1 <= budget <= 256:
        raise t.Refused("policy budget must be one to 256 internal expansions")
    return q.fingerprint(PROFILE, base, horizon, budget)


def solve(journal, questions, objective, *, horizon=2, budget=256):
    captured = context(journal, questions, objective, horizon, budget)
    estimate = a.infer(journal)
    if estimate.posterior is None:
        return Policy(captured, "no-supported-model", 0, estimate, None)
    expanded = 0
    stop_id = t.Identity(PROFILE, captured, "stop")

    def visit(belief, remaining, path):
        nonlocal expanded
        identity = t.Identity(PROFILE, q.fingerprint(captured, path, belief), "node")
        stop = q.decide(belief, objective)
        if remaining == 0:
            return Node(identity, belief, remaining, False, True, stop.expected_loss, stop.expected_loss, stop, (), (stop_id,))
        if expanded == budget:
            # Stop is a feasible incumbent. Nonnegative costs/losses give zero
            # as a conservative lower bound, never a claimed optimal answer.
            return Node(identity, belief, remaining, False, False, F(0), stop.expected_loss, stop, (), (stop_id,))
        expanded += 1
        options = []
        complete = True
        for i, question in enumerate(questions):
            inquiry = q.query_value(belief, question.kernel, objective, cost=question.cost)
            children = []
            lower = upper = question.cost
            for j, branch in enumerate(inquiry.branches):
                child = None if branch.posterior is None else visit(branch.posterior, remaining - 1, path + (i, j))
                children.append(child)
                if child is not None:
                    lower += branch.mass * child.lower
                    upper += branch.mass * child.upper
                    complete &= child.complete
            options.append(Option(question.identity, inquiry, tuple(children), lower, upper))
        lower = min((stop.expected_loss, *(x.lower for x in options)))
        upper = min((stop.expected_loss, *(x.upper for x in options)))
        incumbents = ((stop_id,) if stop.expected_loss == upper else ()) + tuple(x.question for x in options if x.upper == upper)
        return Node(identity, belief, remaining, True, complete, lower, upper, stop, tuple(options), incumbents)

    root = visit(estimate.posterior, horizon, ())
    return Policy(captured, "complete" if root.complete else "incomplete", expanded, estimate, root)


def example():
    """Each bit alone is useless for parity; both together answer the question."""
    def key(name):
        return t.Identity("parity-inquiry", "1", name)

    states = q.Space(key("worlds"), tuple(key(f"{x}{y}") for x in (0, 1) for y in (0, 1)))
    bits = q.Space(key("bits"), (key("zero"), key("one")))
    decisions = q.Space(key("decisions"), (key("even"), key("odd")))
    prior = q.Measure(key("prior"), states, (F(1, 4),) * 4)
    journal = a.Journal(key("journal"), prior, a.DEPENDENCE)
    questions = tuple(a.Question(
        key(f"bit:{axis}"),
        q.Kernel(key(f"law:{axis}"), states, bits, tuple(tuple(F(pair[axis] == value) for value in (0, 1)) for pair in ((0, 0), (0, 1), (1, 0), (1, 1)))),
        F(1, 16),
    ) for axis in (0, 1))
    objective = q.Objective(key("parity-loss"), states, decisions, tuple(tuple(F(decision != (x ^ y)) for x, y in ((0, 0), (0, 1), (1, 0), (1, 1))) for decision in (0, 1)))
    return journal, questions, objective


def main():
    from tools.inquiry_policy_replay import verify

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--horizon", type=int, default=2)
    parser.add_argument("--budget", type=int, default=256)
    parser.add_argument("--json", action="store_true", help="all named prospective policy branches")
    args = parser.parse_args()
    try:
        journal, questions, objective = example()
        policy = solve(journal, questions, objective, horizon=args.horizon, budget=args.budget)
        verify(journal, questions, objective, policy, horizon=args.horizon, budget=args.budget)
        if args.json:
            from tools.intelligence_loop import _wire

            print(json.dumps(policy, default=_wire, indent=2))
        else:
            print(f"Coverage: {policy.coverage}; expanded {policy.expanded} internal nodes.")
            print(f"Expected loss plus query costs: [{policy.root.lower}, {policy.root.upper}].")
            print("Proposed first choices: " + ", ".join(x.slot for x in policy.root.incumbents))
            print("Both bits determine parity; each alone has no decision benefit. No measurement was executed.")
    except (t.Refused, q.Refused) as error:
        parser.error(str(error))


if __name__ == "__main__":
    # Validators import the canonical module; keep one receipt type identity.
    from tools.inquiry_policy import main as _main

    _main()
