"""Source bridge conformance: actual frontend, qualified terms, no execution."""

from fractions import Fraction as F

import pytest

from tools import nomi_terms as n
from tools import scoped_terms as t


@pytest.mark.parametrize("code", ["(x) => x * x", "func square(x):\n    return x * x\n"])
def test_nomi_and_constructor_share_checked_meaning(code):
    source = t.Source("square", "1", code)
    term = n.parse(source)
    expected = t.parse(t.Source("independent-expression", "1", "lambda z: z * z"))
    assert t.alpha_equivalent(term, expected)
    for x in (F(-2), F(0), F(3, 2)):
        assert t.realize(term, (x,)) == x * x


def test_utf8_source_correspondence_and_content_invalidation():
    source = t.Source("unicode", "1", "(α) => α + 1")
    term = n.parse(source)
    assert t.source_slice(term.origin, source) == source.text
    assert t.source_slice(term.body.arguments[0].origin, source) == "α"
    assert t.source_slice(term.body.arguments[1].origin, source) == "1"
    changed = t.Source("unicode", "1", "(α) => α + 2")
    assert t.describe(term)["fingerprint"] != n.describe(changed)["artifact"]["fingerprint"]
    with pytest.raises(t.Refused, match="stale"):
        t.source_slice(term.origin, changed)


def test_lexical_shadowing_and_captured_contracts():
    captured = t.Binding(t.Identity("offset", "1", "value"), "offset")
    source = t.Source("nested", "1", "(x) => (x) => x + offset")
    term = n.parse(source, (captured,))
    assert t.free_references(term) == frozenset({captured.identity})
    assert term.parameters[0].identity != term.body.parameters[0].identity
    assert t.infer(term, (captured,)) == t.FunctionType(("Rational",), t.FunctionType(("Rational",), "Rational"))


@pytest.mark.parametrize("code", [
    "x => x + 1", "(x) => 2x", "(x) => x / 2", "(x) => print(x)",
    "(x: Int) => x", "(x=1) => x", "(x) => x.attr", "(x) => x[0]",
    "func f(x):\n    print(x)\n    return x\n", "func f(x):\n    return f(x)\n",
    "(x) => 1.5", "(x) => x\n(y) => y\n", "(x) => true",
])
def test_unsupported_source_is_refused_before_any_realization(code):
    with pytest.raises(t.Refused):
        n.parse(t.Source("refused", "1", code))


def test_passive_description_is_detached():
    source = t.Source("description", "1", "(x) => -x + 2 * x")
    report = n.describe(source)
    report["artifact"]["nodes"].clear()
    assert n.describe(source)["artifact"]["nodes"]
    assert t.realize(n.parse(source), (F(3),)) == 3
