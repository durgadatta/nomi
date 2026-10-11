"""Executable induction → prediction → inquiry → supplied observation → revision.

An original exact finite discovery workflow, not a world-interacting agent.
The CLI captures a teaching observation only when explicitly supplied.
"""

import argparse
from fractions import Fraction as F
import json

from tools import adaptive_inquiry as a
from tools import adaptive_inquiry_replay as replay
from tools import finite_inquiry as q
from tools import program_search as p
from tools import program_search_replay
from tools import reasoning_structures as s
from tools import scoped_terms as t


def _wire(value):
    if type(value) is F:
        return {"numerator": value.numerator, "denominator": value.denominator}
    if hasattr(value, "__dataclass_fields__"):
        return {"kind": type(value).__name__, **value.__dict__}
    raise TypeError("unsupported inspection value")


def describe(journal, questions, objective, plan):
    """Passive, detached projection. Verification is a separate operation."""
    return json.loads(json.dumps({
        "profile": a.PROFILE, "journal": journal, "questions": questions,
        "objective": objective, "plan": plan,
    }, default=_wire))


def run(*, observed=None, at=F(2)):
    if type(at) is not F or (observed is not None and type(observed) is not F):
        raise t.Refused("workflow requires supplied exact rationals")
    task = p.example()
    learned = p.search(task)
    program_search_replay.verify(task, learned)
    family = s.ProgramFamily(learned.proposals)
    revision = family.space.identity.revision
    prior = q.Measure(
        t.Identity("discovery", revision, "prior"), family.space,
        tuple(F(1, len(family.programs)) for _ in family.programs),
    )
    objective = q.Objective(
        t.Identity("discovery", revision, "classification-loss"), family.space, family.space,
        tuple(tuple(F(i != j) for j in range(len(family.programs))) for i in range(len(family.programs))),
    )
    journal = a.Journal(t.Identity("discovery", "1", "journal"), prior, a.DEPENDENCE)
    inputs = tuple(dict.fromkeys((F(1), F(2), F(3), at)))
    predictions = tuple(s.predict(family, (x,), include_other=True) for x in inputs)
    questions = tuple(a.Question(
        t.Identity("discovery-query", q.fingerprint(prediction.kernel), f"input:{i}"),
        prediction.kernel, F(1, 8),
    ) for i, prediction in enumerate(predictions))
    before = a.plan(journal, questions, objective)
    replay.verify_plan(journal, questions, objective, before)
    result = {
        "search": p.describe(learned),
        "assumptions": {
            "prior": "uniform-over-retained-program-artifacts",
            "objective": "zero-one-loss-for-program-identity",
            "prediction": "exact-deterministic-pure-program",
            "dependence": a.DEPENDENCE,
            "world_actions": [],
        },
        "predictions": [
            {"question": question.identity, "input": x, "outcomes": prediction.outcomes}
            for question, x, prediction in zip(questions, inputs, predictions, strict=True)
        ],
        "before": describe(journal, questions, objective, before),
    }
    if observed is not None:
        index = inputs.index(at)
        question, prediction = questions[index], predictions[index]
        slot = prediction.outcomes.index(observed) if observed in prediction.outcomes else prediction.outcomes.index(None)
        origin = t.Identity("supplied-teaching-observation", q.fingerprint(at, observed), "input")
        journal = a.observe(
            journal, question, question.kernel.destination.members[slot],
            occurrence=t.Identity("discovery-observation", origin.revision, "occurrence"),
            identity=t.Identity("discovery-observation", origin.revision, "report"),
            origin=origin, endorse=True,
        )
        after = a.plan(journal, questions, objective)
        replay.verify_plan(journal, questions, objective, after)
        revised_task = p.Task(task.grammar, task.examples + (
            p.Example(origin, (at,), observed),
        ), task.budget, task.retain)
        revised_search = p.search(revised_task)
        program_search_replay.verify(revised_task, revised_search)
        result.update({
            "supplied_observation": {"origin": origin, "at": at, "value": observed},
            "after": describe(journal, questions, objective, after),
            "revised_search": p.describe(revised_search),
            "posterior_transport_to_new_family": "not-performed",
        })
    return json.loads(json.dumps(result, default=_wire))


def summary(report):
    """Readable projection of the same captured artifacts."""
    def number(value):
        return str(F(value["numerator"], value["denominator"]))

    search = report["search"]
    lines = [f"Search: {search['matches']} example-fitting proposals; {search['coverage']} within the grammar."]
    for prediction, assessment in zip(report["predictions"], report["before"]["plan"]["assessments"], strict=True):
        lines.append(f"Query at {number(prediction['input'])}: expected net value {number(assessment['inquiry']['net_value'])}.")
    selected = report["before"]["plan"]["alternatives"]
    inputs = [number(x["input"]) for x in report["predictions"] if x["question"] in selected]
    lines.append("Proposed queries: " + (", ".join(inputs) if inputs else "stop"))
    if "after" in report:
        supplied = report["supplied_observation"]
        lines.append(f"Supplied teaching observation: {number(supplied['value'])} at {number(supplied['at'])}.")
        estimate = report["after"]["plan"]["estimate"]
        if estimate["posterior"] is not None:
            lines.append("Posterior under the declared model: [" + ", ".join(number(x) for x in estimate["posterior"]["masses"]) + "].")
        status = report["after"]["plan"]["status"]
        lines.append("Next step: " + {
            "stop": "stop", "propose-inquiry": "ask another useful question",
            "needs-model-or-evidence-repair": "repair the model or evidence; no supported posterior",
            "stop-or-tied-inquiry": "stop or choose a tied query",
        }[status] + ".")
        lines.append(f"Revised search: {report['revised_search']['matches']} example-fitting proposals.")
    lines.append("No measurement or external action was executed. Use --json for named artifacts and assumptions.")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--observe", type=F, help="supplied teaching output; no measurement is executed")
    parser.add_argument("--at", type=F, default=F(2), help="input for that observation (default: 2)")
    parser.add_argument("--json", action="store_true", help="full named artifacts, assumptions and checked intermediates")
    args = parser.parse_args()
    try:
        report = run(observed=args.observe, at=args.at)
        print(json.dumps(report, indent=2) if args.json else summary(report))
    except (t.Refused, q.Refused) as error:
        parser.error(str(error))


if __name__ == "__main__":
    main()
