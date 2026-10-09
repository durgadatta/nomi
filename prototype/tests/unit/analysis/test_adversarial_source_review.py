"""Independent review cases: accepted facts need scope and source evidence."""

import ast

import pytest

from prototype.analysis import AnalysisPolicy, analyze_ast


def analyze(source, requirements=("known-types", "pure")):
    return analyze_ast(ast.parse(source), source=source,
                       policy=AnalysisPolicy(requirements=requirements))


@pytest.mark.parametrize("source", [
    "def price():\n    return 12\nmutate_everything()\ntotal = price()\n",
    "price = 12\nprice = external()\ntotal = price * 3\n",
    "def price():\n    if external():\n        return 'twelve'\n    return 12\ntotal = price()\n",
    "def price():\n    yield 12\ntotal = price()\n",
    "class Number:\n    def __mul__(self, other):\n        print('effect')\n        return 12\ntotal = Number() * 3\n",
    "def price():\n    return 12\ntotal = price(mutate_everything())\n",
    "def price():\n    return price()\ntotal = price()\n",
])
def test_unknown_call_state_and_conventions_never_pass_restrictions(source):
    result = analyze(source)
    assert not result.admitted
    assert result.obligations


def test_unchecked_control_does_not_fabricate_return_type_even_in_preview():
    result = analyze("def price():\n    if flag:\n        return 'twelve'\n    return 12\ntotal = price()\n", ())
    total = next(f for f in result.facts if f["name"] == "total")
    assert total["type"] is None


def test_inferred_call_context_is_not_a_polymorphic_public_contract():
    result = analyze("def identity(value):\n    return value\na = identity(1)\nb = identity('text')\n")
    assert result.admitted
    facts = {f["name"]: f for f in result.facts if f["kind"] == "binding"}
    assert facts["a"]["type"] == "Int"
    assert facts["b"]["type"] == "Text"
    assert all(f["public_contract"] == "unproved" for f in result.latent_functions)


def test_python_diagnostic_columns_account_for_multibyte_prefix():
    result = analyze("é = 1; external()\n")
    call = next(o for o in result.obligations if o["code"] == "call-unproved")
    assert call["span"]["column"] == 8
    assert call["span"]["coordinate_unit"] == "unicode-code-point"


def test_identical_facts_under_all_policy_selections():
    source = "amount = 12 * 3\nprint(amount)\n"
    records = [analyze(source, requirements).to_dict() for requirements in
               [(), ("pure",), ("known-types",), ("known-types", "pure")]]
    for record in records[1:]:
        assert record["facts"] == records[0]["facts"]
        assert record["effects"] == records[0]["effects"]
        assert record["obligations"] == records[0]["obligations"]
