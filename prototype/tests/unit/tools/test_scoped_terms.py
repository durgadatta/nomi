"""Independent binder semantics, hygiene and source-revision discriminators."""

from dataclasses import FrozenInstanceError
from fractions import Fraction
import random

import pytest

from tools import scoped_terms as terms


def parsed(text, revision="1", context=()):
    return terms.parse(terms.Source("example", revision, text), context)


def nominal_value(term, environment):
    """Independent owner-keyed interpreter; never uses bound indices or lowering."""
    if type(term) is terms.Reference:
        return environment[term.identity]
    if type(term) is terms.Literal:
        return term.value
    if type(term) is terms.Lambda:
        return lambda *args: nominal_value(
            term.body,
            environment | dict(zip((x.identity for x in term.parameters), args)),
        )
    if type(term) is terms.Application:
        return nominal_value(term.function, environment)(
            *(nominal_value(x, environment) for x in term.arguments)
        )
    operands = [nominal_value(x, environment) for x in term.arguments]
    operations = {
        "add": lambda a, b: a + b,
        "sub": lambda a, b: a - b,
        "mul": lambda a, b: a * b,
        "neg": lambda a: -a,
    }
    return operations[term.name](*operands)


def test_report_and_scientific_map_match_independent_vectors():
    report = parsed("lambda quantity, price: quantity * price + 5")
    square = parsed("lambda x: x * x")
    rng = random.Random(1011)
    for _ in range(32):
        quantity = Fraction(rng.randint(-8, 8), 3)
        price = Fraction(rng.randint(-8, 8), 5)
        assert terms.realize(report, (quantity, price)) == quantity * price + 5
        assert terms.realize(square, (quantity,)) == quantity**2
        assert terms.realize(report, (quantity, price)) == nominal_value(report, {})(
            quantity, price
        )


def test_alpha_equivalence_ignores_bound_labels_and_retains_free_owners():
    left = parsed("lambda x: (lambda x: x + 1)(x)")
    right = parsed("lambda outer: (lambda inner: inner + 1)(outer)", "2")
    assert terms.alpha_equivalent(left, right)
    assert terms.realize(left, (7,)) == 8
    assert terms.realize(right, (7,)) == 8
    first = terms.Binding(terms.Identity("import-a", "1", "value"), "x")
    second = terms.Binding(terms.Identity("import-b", "1", "value"), "x")
    assert not terms.alpha_equivalent(
        parsed("x", context=(first,)), parsed("x", context=(second,))
    )


def test_nested_lambda_retains_the_outer_capture_after_shadowing():
    term = parsed("lambda x: (lambda y: (lambda x: x + y)(3))(x)")
    for value in range(-5, 6):
        assert terms.realize(term, (value,)) == value + 3
        assert nominal_value(term, {})(value) == value + 3


def test_simultaneous_substitution_does_not_rewrite_inserted_terms():
    x = terms.Identity("free", "1", "x")
    y = terms.Identity("free", "1", "y")
    original = terms.Operation("sub", (terms.Reference(x), terms.Reference(y)))
    swapped = terms.substitute(original, {x: terms.Reference(y), y: terms.Reference(x)})
    context = (terms.Binding(x, "x"), terms.Binding(y, "y"))
    assert terms.realize(swapped, context=context, bindings={x: 3, y: 10}) == 7


def test_substitution_freshens_a_binder_that_would_capture_a_free_reference():
    x = terms.Binding(terms.Identity("free", "1", "x"), "x")
    original = parsed("lambda y: x + y", context=(x,))
    y = original.parameters[0]
    replacement = terms.Reference(y.identity)
    changed = terms.substitute(original, {x.identity: replacement})
    assert changed.parameters[0].identity != y.identity
    assert terms.free_references(changed) == {y.identity}
    assert terms.realize(changed, (3,), context=(y,), bindings={y.identity: 10}) == 13
    assert original.parameters[0] == y


def test_substitution_does_not_replace_a_shadowing_bound_owner():
    original = parsed("lambda x: x + 1")
    identity = original.parameters[0].identity
    changed = terms.substitute(original, {identity: terms.literal(100)})
    assert terms.alpha_equivalent(original, changed)


def test_beta_preserves_types_and_the_value_for_nested_capture():
    term = parsed("(lambda x: (lambda y: x * y)(3))(7)")
    reduced = terms.beta(term)
    assert terms.infer(reduced) == terms.RATIONAL
    assert terms.realize(reduced) == terms.realize(term) == 21


def test_multi_parameter_beta_is_simultaneous():
    x = terms.Binding(terms.Identity("free", "1", "x"), "x")
    y = terms.Binding(terms.Identity("free", "1", "y"), "y")
    term = parsed("(lambda x, y: x - y)(y, x)", context=(x, y))
    reduced = terms.beta(term, (x, y))
    assert (
        terms.realize(reduced, context=(x, y), bindings={x.identity: 3, y.identity: 10})
        == 7
    )


def test_wrong_types_arity_and_duplicate_owners_are_refused():
    with pytest.raises(terms.Refused, match="call contract"):
        parsed("(lambda x: x)(1, 2)")
    with pytest.raises(terms.Refused, match="scalar operands"):
        parsed("(lambda x: x) + 2")
    binder = terms.Binding(terms.Identity("same", "1", "x"), "x")
    with pytest.raises(terms.Refused, match="reused"):
        terms.infer(
            terms.Lambda(
                (binder,), terms.Lambda((binder,), terms.Reference(binder.identity))
            )
        )


def test_old_import_does_not_resolve_against_a_same_spelled_new_revision():
    old = terms.Binding(terms.Identity("module", "1", "constant"), "constant")
    new = terms.Binding(terms.Identity("module", "2", "constant"), "constant")
    term = parsed("lambda x: x + constant", context=(old,))
    with pytest.raises(terms.Refused, match="stale"):
        terms.infer(term, (new,))
    assert terms.infer(term, (old,)) == terms.FunctionType(
        (terms.RATIONAL,), terms.RATIONAL
    )


def test_utf8_origins_and_same_revision_changed_content_are_checked():
    source = terms.Source("unicode", "1", "lambda α: α + 1")
    term = terms.parse(source)
    reference = term.body.arguments[0]
    assert terms.source_slice(reference.origin, source) == "α"
    changed = terms.Source("unicode", "1", "lambda α: α + 2")
    with pytest.raises(terms.Refused, match="stale source"):
        terms.source_slice(reference.origin, changed)
    split = terms.Origin(
        source.identity,
        source.revision,
        source.digest,
        reference.origin.start_byte + 1,
        reference.origin.end_byte,
    )
    with pytest.raises(terms.Refused, match="UTF-8"):
        terms.source_slice(split, source)


def test_description_checking_and_substitution_do_not_realize(monkeypatch):
    monkeypatch.setattr(
        terms, "realize", lambda *args, **kwargs: pytest.fail("implicit execution")
    )
    term = parsed("(lambda x: x * x)(3)")
    assert terms.infer(terms.beta(term)) == terms.RATIONAL
    assert terms.lower(term)[0] == "application"


def test_inspection_is_detached_and_source_revision_sensitive():
    old = parsed("lambda x: x + 1")
    new = parsed("lambda x: x + 1", "2")
    assert terms.alpha_equivalent(old, new)
    assert terms.describe(old)["fingerprint"] != terms.describe(new)["fingerprint"]
    record = terms.describe(old)
    record["nodes"][0]["parameters"][0]["label"] = "changed-view"
    assert terms.describe(old)["nodes"][0]["parameters"][0]["label"] == "x"


def test_higher_order_manual_terms_preserve_the_callable_contract():
    f = terms.Binding(
        terms.Identity("manual", "1", "f"),
        "f",
        terms.FunctionType((terms.RATIONAL,), terms.RATIONAL),
    )
    function = terms.Lambda(
        (f,), terms.Application(terms.Reference(f.identity), (terms.literal(3),))
    )
    application = terms.Application(function, (parsed("lambda x: x * x"),))
    assert terms.realize(application) == 9
    assert terms.realize(terms.beta(application)) == 9


@pytest.mark.parametrize(
    "source",
    [
        "True",
        "1.5",
        "f()",
        "x.y",
        "[1]",
        "1 / 2",
        "lambda x=1: x",
        "lambda *x: 1",
        "(lambda x: x)(x=1)",
    ],
)
def test_host_access_and_unadmitted_forms_are_refused(source):
    with pytest.raises(terms.Refused):
        parsed(source)


def test_description_and_budget_boundaries_are_explicit():
    term = parsed("lambda x: x + 1")
    with pytest.raises(FrozenInstanceError):
        term.body = terms.literal(9)
    with pytest.raises(terms.Refused, match="capacity"):
        terms.Source("large", "1", " " * 8193)
    with pytest.raises(terms.Refused, match="capacity"):
        parsed("+".join("1" for _ in range(150)))
    with pytest.raises(terms.Refused, match="canonical"):
        terms.infer(terms.Literal(1))
