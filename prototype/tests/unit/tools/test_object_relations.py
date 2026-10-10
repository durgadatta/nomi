"""Relations connect declared operands without executing their computations."""

from copy import deepcopy
from pathlib import Path

import pytest

from tools.object_interface import (
    ContractError,
    Graph,
    Requirements,
    Workflow,
    load_document,
)
from tools.object_interface.backend import Backend
from tools.object_interface.documentary import document_vocabulary
from tools.object_interface.examples import lab_vocabulary, python_backend

ROOT = Path(__file__).resolve().parents[4]
EXAMPLE = ROOT / "docs/research/object_framework"


def graph():
    vocabulary = lab_vocabulary()
    return Graph.from_document(
        {
            "version": 1,
            "vocabulary": vocabulary.fingerprint,
            "objects": [
                {
                    "id": "lower",
                    "op": "exact.input",
                    "ports": {},
                    "attributes": {},
                },
                {
                    "id": "upper",
                    "op": "exact.input",
                    "ports": {},
                    "attributes": {},
                },
                {
                    "id": "total",
                    "op": "exact.add",
                    "ports": {"left": "lower", "right": "upper"},
                    "attributes": {},
                },
            ],
            "outputs": ["total"],
        },
        vocabulary,
    )


def condition(checked, rule="exact.le-v1", operands=None):
    return Requirements.from_document(
        {
            "version": 3,
            "graph": checked.context,
            "owner": "test.relations",
            "revision": "v1",
            "requirements": [
                {
                    "id": "ordered",
                    "rule": rule,
                    "operands": operands
                    or [
                        {"subject": "lower", "path": []},
                        {"subject": "upper", "path": []},
                    ],
                }
            ],
        },
        checked,
    )


@pytest.mark.parametrize(
    "bindings,status",
    [
        (None, "pending"),
        ({}, "pending"),
        ({"lower": 1}, "pending"),
        ({"upper": 0}, "pending"),
        ({"lower": 1, "upper": 2}, "satisfied"),
        ({"lower": 2, "upper": 2}, "satisfied"),
        ({"lower": 3, "upper": 2}, "refuted"),
        ({"lower": -4, "upper": -3}, "satisfied"),
    ],
)
def test_ordered_integer_relation_has_explicit_three_way_evidence(bindings, status):
    checked = graph()
    required = condition(checked)
    receipt = required.check(bindings)
    assert receipt["status"] == status
    assert receipt["evidence_phase"] == ("static" if bindings is None else "binding")
    assert required.verify(receipt, bindings)["verdict"] == status
    assert "value" not in repr(receipt["requirements"])


def test_operand_order_and_repetition_are_semantic():
    checked = graph()
    reversed_condition = condition(
        checked,
        operands=[
            {"subject": "upper", "path": []},
            {"subject": "lower", "path": []},
        ],
    )
    assert reversed_condition.check({"lower": 1, "upper": 2})["status"] == "refuted"
    repeated = condition(checked, operands=[{"subject": "lower", "path": []}] * 2)
    assert repeated.check()["status"] == "pending"
    assert repeated.check({"lower": -10})["status"] == "satisfied"


def test_declared_literal_and_alias_supply_static_operand_evidence():
    checked = graph().compose("limit", "exact.literal", {}, {"value": 10})
    checked = checked.compose("alias", "exact.alias", {"target": checked.ref("limit")})
    required = condition(
        checked,
        operands=[{"subject": "limit", "path": []}, {"subject": "alias", "path": []}],
    )
    receipt = required.check()
    assert receipt["status"] == "satisfied"
    assert all(
        o["basis"] == "declared literal" for o in receipt["requirements"][0]["operands"]
    )


@pytest.mark.parametrize(
    "title,expected,status",
    [
        ("Plan", "Plan", "satisfied"),
        ("Plan", "plan", "refuted"),
        (" Plan", "Plan", "refuted"),
        ("", "", "satisfied"),
        ("é", "e\u0301", "refuted"),
    ],
)
def test_document_title_relation_preserves_exact_text_representation(
    title, expected, status
):
    checked = Graph.from_document(
        load_document(EXAMPLE / "document.json"), document_vocabulary()
    )
    checked = checked.compose("requested", "text.input", {})
    required = condition(
        checked,
        "text.equal-v1",
        [
            {"subject": "draft", "path": ["title"]},
            {"subject": "requested", "path": []},
        ],
    )
    assert (
        required.check(
            {"draft": {"title": title, "sections": []}, "requested": expected}
        )["status"]
        == status
    )


def test_missing_declared_array_item_refutes_even_with_an_unbound_peer():
    checked = Graph.from_document(
        load_document(EXAMPLE / "document.json"), document_vocabulary()
    )
    checked = checked.compose("requested", "text.input", {})
    required = condition(
        checked,
        "text.equal-v1",
        [
            {"subject": "draft", "path": ["sections", 0, "heading"]},
            {"subject": "requested", "path": []},
        ],
    )
    receipt = required.check({"draft": {"title": "Plan", "sections": []}})
    assert receipt["status"] == "refuted"
    assert [o["status"] for o in receipt["requirements"][0]["operands"]] == [
        "missing",
        "pending",
    ]


@pytest.mark.parametrize(
    "rule,subject",
    [
        ("exact.positive-v1", "lower"),
        ("text.nonempty-v1", "prefix"),
        ("array.nonempty-v1", "draft"),
    ],
)
def test_unary_rules_use_the_same_operand_envelope(rule, subject):
    if subject == "draft":
        checked = Graph.from_document(
            load_document(EXAMPLE / "document.json"), document_vocabulary()
        )
        operand, bindings = (
            {"subject": subject, "path": ["sections"]},
            {"draft": {"title": "", "sections": []}},
        )
    elif subject == "prefix":
        checked = Graph.from_document(
            load_document(EXAMPLE / "composition.json"), lab_vocabulary()
        )
        operand, bindings = {"subject": subject, "path": []}, None
    else:
        checked, operand, bindings = (
            graph(),
            {"subject": subject, "path": []},
            {"lower": 1},
        )
    required = condition(checked, rule, [operand])
    assert required.check(bindings)["status"] == (
        "refuted" if subject == "draft" else "satisfied"
    )


@pytest.mark.parametrize(
    "mutate",
    [
        lambda r: r.update(rule="unknown.rule"),
        lambda r: r.update(operands=[]),
        lambda r: r["operands"].pop(),
        lambda r: r["operands"].append(r["operands"][0]),
        lambda r: r["operands"][1].update(subject="missing"),
        lambda r: r["operands"][1].update(path=[True]),
        lambda r: r["operands"][1].update(path=["undeclared"]),
        lambda r: r["operands"][1].update(status="known"),
        lambda r: r.update(subject="lower"),
    ],
)
def test_closed_relation_shapes_refuse_forged_truth_and_wrong_references(mutate):
    checked = graph()
    document = condition(checked).document
    mutate(document["requirements"][0])
    with pytest.raises(ContractError):
        Requirements.from_document(document, checked)


def test_wrong_codec_and_computed_operand_do_not_become_evidence():
    checked = graph()
    with pytest.raises(ContractError, match="operand kind"):
        condition(checked, "text.equal-v1")
    required = condition(
        checked,
        operands=[{"subject": "lower", "path": []}, {"subject": "total", "path": []}],
    )
    assert required.check({"lower": 1, "upper": 2})["status"] == "pending"
    with pytest.raises(ContractError, match="computed preconditions"):
        python_backend(checked.vocabulary).compile(checked).require(required)


def test_all_required_operands_are_checked_before_any_backend_callback():
    checked, calls = graph(), []

    def add(ports, attrs):
        calls.append("add")
        return ports["left"] + ports["right"]

    compiled = (
        Backend("observed", "v1", checked.vocabulary.fingerprint, {"exact.add": add})
        .compile(checked)
        .require(condition(checked))
    )
    with pytest.raises(ContractError, match="not satisfied"):
        compiled.bind({"lower": 3, "upper": 2})
    assert calls == []
    assert compiled.bind({"lower": 1, "upper": 2}).execute().values == {"total": 3}
    assert calls == ["add"]
    selected = python_backend(checked.vocabulary).compile(
        checked, [checked.ref("lower")]
    )
    with pytest.raises(ContractError, match="outside selected realization"):
        selected.require(condition(checked))


def test_workflow_substitution_retains_both_relation_operands_and_mixed_versions():
    checked = graph()
    template = {
        "version": 1,
        "id": "ordered-sum",
        "revision": "v1",
        "graph": checked.document,
        "inputs": {"low": "lower", "high": "upper"},
        "outputs": {"sum": "total"},
        "requirements": condition(checked).document,
    }
    workflow = Workflow.from_document(template, checked.vocabulary)
    first = workflow.compose(
        checked, "first", {"low": checked.ref("lower"), "high": checked.ref("upper")}
    )
    assert first.requirements.document["version"] == 3
    assert first.requirements.document["requirements"][0]["operands"] == [
        {"subject": "lower", "path": []},
        {"subject": "upper", "path": []},
    ]
    legacy = deepcopy(template)
    legacy["id"] = "positive-sum"
    legacy["requirements"] = {
        **condition(checked).document,
        "version": 2,
        "requirements": [
            {
                "id": "positive",
                "rule": "exact.positive-v1",
                "subject": "lower",
                "path": [],
            },
        ],
    }
    legacy_workflow = Workflow.from_document(legacy, checked.vocabulary)
    second = legacy_workflow.compose(
        first,
        "second",
        {"low": first.graph.ref("lower"), "high": first.graph.ref("upper")},
    )
    assert [r["id"] for r in second.requirements.document["requirements"]] == [
        "first.ordered",
        "second.positive",
    ]
    assert (
        second.compile(python_backend(checked.vocabulary))
        .bind({"lower": 1, "upper": 2})
        .execute()
        .values["second.total"]
        == 3
    )
    old_first = legacy_workflow.compose(
        checked, "old", {"low": checked.ref("lower"), "high": checked.ref("upper")}
    )
    assert old_first.requirements.document["version"] == 2
    mixed = workflow.compose(
        old_first,
        "new",
        {"low": old_first.graph.ref("lower"), "high": old_first.graph.ref("upper")},
    )
    assert mixed.requirements.document["version"] == 3
    assert mixed.requirements.check({"lower": 0, "upper": 2})["status"] == "refuted"


def test_operand_receipts_and_artifacts_are_detached_and_context_bound():
    checked = graph()
    required = condition(checked)
    receipt = required.check({"lower": 1, "upper": 2})
    receipt["requirements"][0]["operands"][1]["subject"] = "lower"
    with pytest.raises(ContractError, match="does not replay"):
        required.verify(receipt, {"lower": 1, "upper": 2})
    exported = required.document
    exported["requirements"][0]["operands"].clear()
    assert len(required.document["requirements"][0]["operands"]) == 2
