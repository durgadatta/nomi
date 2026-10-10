"""Engine-free obligation states and required preconditions before execution."""

from pathlib import Path

import pytest

from tools.object_interface import ContractError, Graph, Requirements, load_document
from tools.object_interface.__main__ import main
from tools.object_interface.backend import Backend
from tools.object_interface.examples import lab_vocabulary, python_backend

ROOT = Path(__file__).resolve().parents[4]
EXAMPLE = ROOT / "docs/research/object_framework"


def graph():
    return Graph.from_document(
        load_document(EXAMPLE / "composition.json"), lab_vocabulary()
    )


def requirements(checked, subject="quantity", rule="exact.positive-v1"):
    return Requirements.from_document(
        {
            "version": 1,
            "graph": checked.context,
            "owner": "test",
            "revision": "v1",
            "requirements": [{"id": "required", "rule": rule, "subject": subject}],
        },
        checked,
    )


def test_numeric_and_text_input_conditions_stay_pending_without_inputs():
    checked = graph()
    conditions = Requirements.from_document(
        load_document(EXAMPLE / "requirements.json"), checked
    )
    assert conditions.check()["status"] == "pending"
    assert conditions.inspect("name_has_content")["basis"] == "unresolved expression"
    assert conditions.check({"quantity": 3, "name": "Ada"})["status"] == "satisfied"
    assert conditions.check({"quantity": 0, "name": ""})["status"] == "refuted"
    assert conditions.check({"quantity": 3})["status"] == "pending"


@pytest.mark.parametrize(
    "value,expected", [(0, "refuted"), (-1, "refuted"), (1, "satisfied")]
)
def test_literal_positive_condition_checks_without_engine(value, expected):
    original = graph()
    checked = original.compose("literal", "exact.literal", {}, {"value": value})
    conditions = requirements(checked, "literal")
    assert conditions.check()["status"] == expected
    assert conditions.check()["requirements"][0]["basis"] == "declared literal"


def test_alias_literal_evidence_and_no_hidden_whitespace_normalization():
    original = graph()
    literal = original.compose("blank", "text.literal", {}, {"value": " "})
    alias = literal.compose("aliased", "text.alias", {"target": literal.ref("blank")})
    assert (
        requirements(alias, "aliased", "text.nonempty-v1").check()["status"]
        == "satisfied"
    )


def test_computed_expression_remains_pending_even_with_all_input_bindings():
    checked = graph()
    conditions = requirements(checked, "squared")
    assert conditions.check({"quantity": 3})["status"] == "pending"
    with pytest.raises(ContractError, match="computed preconditions"):
        python_backend(checked.vocabulary).compile(checked).require(conditions)
    with pytest.raises(ContractError, match="only abstract input slots"):
        conditions.check({"squared": 9})


def test_required_refuted_input_stops_before_backend_callbacks():
    checked, calls = graph(), []

    def multiply(ports, attributes):
        calls.append("multiply")
        return ports["left"] * ports["right"]

    backend = Backend(
        "observed",
        "v1",
        checked.vocabulary.fingerprint,
        {"exact.multiply": multiply, "exact.add": lambda p, a: p["left"] + p["right"]},
    )
    compiled = backend.compile(checked, [checked.ref("doubled")]).require(
        requirements(checked)
    )
    assert compiled.inspect()["requirements"]["status"] == "pending"
    with pytest.raises(ContractError, match="required.*not satisfied"):
        compiled.bind({"quantity": -3})
    assert calls == []
    bound = compiled.bind({"quantity": 3})
    assert calls == []
    result = bound.execute()
    assert result.values == {"doubled": 18}
    assert result.receipt["requirement_evidence"]["status"] == "satisfied"
    assert result.receipt["requirement_evidence"]["evidence_phase"] == "binding"
    assert calls == ["multiply"]


def test_text_requirement_and_unrelated_subject_are_explicit():
    checked = graph()
    compiled = python_backend(checked.vocabulary).compile(
        checked, [checked.ref("greeting")]
    )
    with pytest.raises(ContractError, match="outside selected realization"):
        compiled.require(requirements(checked))
    constrained = compiled.require(requirements(checked, "name", "text.nonempty-v1"))
    with pytest.raises(ContractError, match="not satisfied"):
        constrained.bind({"name": ""})
    assert constrained.bind({"name": "Ada"}).execute().values == {
        "greeting": "Hello, Ada"
    }


def test_refuted_literal_cannot_be_accepted_by_a_different_engine():
    original = graph()
    checked = original.compose("zero", "exact.literal", {}, {"value": 0})
    compiled = python_backend(checked.vocabulary).compile(
        checked, [checked.ref("zero")]
    )
    with pytest.raises(ContractError, match="literal condition is refuted"):
        compiled.require(requirements(checked, "zero"))


def test_requirement_contexts_and_receipts_cannot_be_forged_or_reused():
    checked = graph()
    conditions = requirements(checked)
    receipt = conditions.check({"quantity": 3})
    assert conditions.verify(receipt, {"quantity": 3})["status"] == "verified"
    with pytest.raises(ContractError, match="does not replay"):
        conditions.verify(receipt, {"quantity": 4})
    receipt["status"] = "satisfied"
    receipt["requirements"][0]["basis"] = "user assertion"
    with pytest.raises(ContractError, match="does not replay"):
        conditions.verify(receipt, {"quantity": 3})
    revised = checked.compose(
        "later", "exact.double", {"value": checked.ref("quantity")}
    )
    with pytest.raises(ContractError, match="different graph context"):
        Requirements.from_document(conditions.document, revised)
    with pytest.raises(ContractError, match="exact graph revision"):
        python_backend(checked.vocabulary).compile(checked).require(
            requirements(graph())
        )


def test_obligations_are_inert_detached_and_not_supplied_truth_values():
    checked = graph()
    source = requirements(checked).document
    conditions = Requirements.from_document(source, checked)
    source["requirements"][0]["rule"] = "user.says-true"
    exported = conditions.document
    exported["requirements"].clear()
    assert conditions.inspect("required")["status"] == "pending"
    with pytest.raises(AttributeError):
        conditions._context = "mutated"
    document = conditions.document
    document["requirements"][0]["status"] = "satisfied"
    with pytest.raises(ContractError, match="expected exactly"):
        Requirements.from_document(document, checked)


@pytest.mark.parametrize(
    "subject,rule",
    [
        ("name", "exact.positive-v1"),
        ("quantity", "text.nonempty-v1"),
        ("quantity", "unknown.rule"),
    ],
)
def test_wrong_nominal_family_and_unknown_predicates_are_refused(subject, rule):
    with pytest.raises(ContractError):
        requirements(graph(), subject, rule)


@pytest.mark.parametrize(
    "bindings",
    [{"quantity": True}, {"quantity": 3.0}, {"quantity": None}, {"missing": 3}],
)
def test_refinement_binding_checks_the_same_input_value_boundary(bindings):
    with pytest.raises(ContractError):
        requirements(graph()).check(bindings)


def test_cli_passive_requirements_and_explicit_required_execution(capsys):
    source = str(EXAMPLE / "composition.json")
    conditions = str(EXAMPLE / "requirements.json")
    bindings = str(EXAMPLE / "bindings.json")
    assert main(["requirements", source, conditions]) == 1
    assert '"pending"' in capsys.readouterr().out
    assert main(["requirements", source, conditions, "--bindings", bindings]) == 0
    assert '"satisfied"' in capsys.readouterr().out
    assert (
        main(
            [
                "run",
                source,
                bindings,
                "--requirements",
                conditions,
                "--backend",
                "python-exact-text",
            ]
        )
        == 0
    )
    assert '"requirement_evidence"' in capsys.readouterr().out
