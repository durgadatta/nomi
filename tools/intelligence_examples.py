"""Source-linked hypotheses, inquiry and causal/learning counterexamples.

This composes existing scoped-term and finite-inquiry labs. The source producer
uses explicit Nomi/Python-expression adapters, not admitted quotation syntax.
Measurement likelihoods are explicit assumptions, not derived physics.
"""

from fractions import Fraction as F
import json

from tools import finite_inquiry as q
from tools import scoped_terms as terms
from tools import nomi_terms
from tools import reasoning_structures as structures


def hypothesis_family(sources, *, producer="python-expression"):
    """Capture checked terms as finite alternatives through content-bound owners."""
    if type(sources) is not tuple or not 1 <= len(sources) <= 8:
        raise q.Refused("expected a bounded immutable source family")
    producers = {"python-expression": terms.parse, "nomi": nomi_terms.parse}
    if producer not in producers:
        raise q.Refused("unsupported source producer")
    transformations = tuple(structures.rational(producers[producer](source)) for source in sources)
    artifacts = tuple(terms.describe(x.description) for x in transformations)
    members = tuple(
        terms.Identity(source.identity, artifact["fingerprint"], "hypothesis")
        for source, artifact in zip(sources, artifacts, strict=True)
    )
    if len(set(members)) != len(members):
        raise q.Refused("duplicate captured hypothesis")
    sorts = [artifact["type"] for artifact in artifacts]
    if any(sort != sorts[0] for sort in sorts):
        raise q.Refused("hypotheses require one shared checked callable contract")
    space = q.Space(
        terms.Identity("source-hypotheses", q.fingerprint(members), "space"), members
    )
    return space, artifacts


def scientific_inquiry(sources=None, *, producer="python-expression"):
    sources = (
        (
            terms.Source(
                "damped-mechanism",
                "1",
                ("(position, velocity) => -2 * position - velocity"
                 if producer == "nomi" else "lambda position, velocity: -2 * position - velocity"),
            ),
            terms.Source(
                "undamped-mechanism", "1",
                ("(position, velocity) => -2 * position"
                 if producer == "nomi" else "lambda position, velocity: -2 * position")
            ),
        )
        if sources is None
        else sources
    )
    if len(sources) != 2:
        raise q.Refused("this inquiry comparison expects two hypotheses")
    family, artifacts = hypothesis_family(sources, producer=producer)
    prior, experiment, objective = q.example()
    # Transport only declared model/loss tables, rebinding their source space.
    # No original assessment or claim is transferred to the new family.
    prior = q.Measure(
        terms.Identity("hypothesis-model", family.identity.revision, "prior"),
        family,
        prior.masses,
    )
    experiment = q.Kernel(
        terms.Identity("hypothesis-model", family.identity.revision, "measurement-law"),
        family,
        experiment.destination,
        experiment.rows,
    )
    objective = q.Objective(
        terms.Identity("hypothesis-policy", family.identity.revision, "loss"),
        family,
        objective.decisions,
        objective.losses,
    )
    result = q.query_value(prior, experiment, objective, cost=F(1, 8))
    q.verify_inquiry(prior, experiment, objective, result)
    return prior, experiment, objective, result, artifacts


def causal_comparison():
    """Two supplied binary mechanisms: equal observations, different do(X=0)."""

    def key(name):
        return terms.Identity("causal-comparison", "1", name)

    exogenous = q.Space(key("exogenous"), (key("U=0"), key("U=1")))
    world = q.Space(
        key("world"), tuple(key(f"X={x},Y={y}") for x in (0, 1) for y in (0, 1))
    )
    observed = ((F(1), F(0), F(0), F(0)), (F(0), F(0), F(0), F(1)))
    forward = q.Kernel(key("X=U;Y=X"), exogenous, world, observed)
    reverse = q.Kernel(key("Y=U;X=Y"), exogenous, world, observed)
    changed_forward = q.Kernel(
        key("do-X0-forward"), exogenous, world, (observed[0], observed[0])
    )
    changed_reverse = q.Kernel(
        key("do-X0-reverse"), exogenous, world, (observed[0], (F(0), F(1), F(0), F(0)))
    )
    prior = q.Measure(key("fair-U"), exogenous, (F(1, 2), F(1, 2)))
    return {
        "forward_observed": q.pushforward(prior, forward).masses,
        "reverse_observed": q.pushforward(prior, reverse).masses,
        "forward_intervened": q.pushforward(prior, changed_forward).masses,
        "reverse_intervened": q.pushforward(prior, changed_reverse).masses,
    }


def abstraction_comparison():
    """Finite fit is weaker than preservation; checked beta extraction is separate."""
    original = terms.parse(terms.Source("original", "1", "lambda x: x * x"))
    proposed = terms.parse(terms.Source("proposed", "1", "lambda x: x"))
    on_examples = all(
        terms.realize(original, (x,)) == terms.realize(proposed, (x,)) for x in (0, 1)
    )
    counterexample = terms.realize(original, (2,)), terms.realize(proposed, (2,))
    constructor = terms.parse(
        terms.Source("extraction", "1", "lambda offset: lambda x: x + offset")
    )
    extracted = terms.beta(terms.Application(constructor, (terms.Literal(F(5)),)))
    long_form = terms.parse(terms.Source("long-form", "1", "lambda x: x + 5"))
    return {
        "fits_declared_examples": on_examples,
        "counterexample_at_2": counterexample,
        "replacement_refuted": counterexample[0] != counterexample[1],
        "checked_beta_extraction": terms.alpha_equivalent(extracted, long_form),
    }


def main():
    prior, experiment, objective, result, artifacts = scientific_inquiry(producer="nomi")
    record = {
        "status": "bounded source-linked comparison, not Nomi source admission",
        "hypotheses": [
            {"identity": str(member), "description": artifact}
            for member, artifact in zip(prior.space.members, artifacts, strict=True)
        ],
        "inquiry": {
            "assessment": q.describe(result),
            "claim": "exact under supplied measurement and loss assumptions",
            "replay": q.verify_inquiry(prior, experiment, objective, result),
        },
        "causal": {
            key: [str(x) for x in value] for key, value in causal_comparison().items()
        },
        "abstraction": abstraction_comparison(),
        "world_actions": "none",
    }
    print(json.dumps(record, default=str, indent=2))


if __name__ == "__main__":
    main()
