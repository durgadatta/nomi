"""Finite universal conditions compose a declared collection with unary rules."""

from copy import deepcopy
from pathlib import Path

import pytest

from tools.object_interface import (
    ContractError,
    Graph,
    Requirements,
    Vocabulary,
    Workflow,
    load_document,
)
from tools.object_interface.backend import Backend
from tools.object_interface.documentary import document_vocabulary

ROOT = Path(__file__).resolve().parents[4]
EXAMPLE = ROOT / "docs/research/object_framework"


def graph():
    return Graph.from_document(
        load_document(EXAMPLE / "document.json"), document_vocabulary()
    )


def conditions(
    checked, *, path=None, item_path=None, rule="text.nonempty-v1", subject="draft"
):
    return Requirements.from_document(
        {
            "version": 4,
            "graph": checked.context,
            "owner": "test.all-sections",
            "revision": "v1",
            "requirements": [
                {
                    "id": "headings",
                    "condition": {
                        "kind": "every",
                        "rule": rule,
                        "subject": subject,
                        "path": ["sections"] if path is None else path,
                        "item_path": ["heading"] if item_path is None else item_path,
                    },
                }
            ],
        },
        checked,
    )


def spec(headings):
    return {
        "draft": {
            "title": "A",
            "sections": [{"heading": h, "paragraphs": []} for h in headings],
        }
    }


@pytest.mark.parametrize(
    "bindings,status,count",
    [
        (None, "pending", 0),
        ({}, "pending", 0),
        (spec([]), "satisfied", 0),
        (spec(["A"]), "satisfied", 1),
        (spec(["A", "B"]), "satisfied", 2),
        (spec(["A", ""]), "refuted", 2),
        (spec(["", "A", ""]), "refuted", 3),
        (spec([" "]), "satisfied", 1),
    ],
)
def test_universal_truth_is_finite_and_empty_collections_are_vacuous(
    bindings, status, count
):
    required = conditions(graph())
    receipt = required.check(bindings)
    assert receipt["status"] == status
    condition = receipt["requirements"][0]["condition"]
    assert condition["checked_items"] == count
    assert condition["total_items"] == (
        None if bindings is None or bindings == {} else count
    )
    assert condition["failures_complete"] is True
    assert required.verify(receipt, bindings)["verdict"] == status


def test_counterexamples_retain_all_paths_without_echoing_input_values():
    receipt = conditions(graph()).check(spec(["", "A", ""]))
    assert receipt["requirements"][0]["condition"]["failures"] == [
        {"path": ["sections", 0, "heading"], "code": "predicate-refuted"},
        {"path": ["sections", 2, "heading"], "code": "predicate-refuted"},
    ]
    assert "value" not in repr(receipt["requirements"])


def test_array_nonemptiness_is_separate_from_all_items_satisfying():
    checked = graph()
    source = conditions(checked).document
    source["requirements"].append(
        {
            "id": "has_sections",
            "condition": {
                "kind": "relation",
                "rule": "array.nonempty-v1",
                "operands": [{"subject": "draft", "path": ["sections"]}],
            },
        }
    )
    receipt = Requirements.from_document(source, checked).check(spec([]))
    assert [r["status"] for r in receipt["requirements"]] == ["satisfied", "refuted"]
    assert receipt["status"] == "refuted"


def test_every_declared_paragraph_array_can_be_required_to_have_content():
    checked = graph()
    required = conditions(checked, rule="array.nonempty-v1", item_path=["paragraphs"])
    value = spec(["A", "B"])
    value["draft"]["sections"][0]["paragraphs"] = [""]
    receipt = required.check(value)
    assert receipt["status"] == "refuted"
    assert receipt["requirements"][0]["condition"]["failures"] == [
        {"path": ["sections", 1, "paragraphs"], "code": "predicate-refuted"}
    ]


def test_missing_inner_index_refutes_one_item_and_missing_collection_refutes_root():
    checked = graph()
    required = conditions(checked, item_path=["paragraphs", 0])
    value = spec(["A", "B"])
    value["draft"]["sections"][1]["paragraphs"] = ["body"]
    receipt = required.check(value)
    assert receipt["requirements"][0]["condition"]["failures"] == [
        {"path": ["sections", 0, "paragraphs", 0], "code": "missing-item-path"}
    ]
    root = conditions(checked, path=["sections", 0, "paragraphs"], item_path=[])
    receipt = root.check(spec([]))
    assert receipt["status"] == "refuted"
    assert receipt["requirements"][0]["condition"]["failures"] == [
        {"path": ["sections", 0, "paragraphs"], "code": "missing-collection-path"}
    ]


def test_literal_and_alias_collections_discharge_without_backend():
    checked = graph().compose(
        "literal", "document.spec.literal", {}, {"value": spec(["A", "B"])["draft"]}
    )
    checked = checked.compose(
        "alias", "document.spec.alias", {"target": checked.ref("literal")}
    )
    receipt = conditions(checked, subject="alias").check()
    assert receipt["status"] == "satisfied"
    assert receipt["requirements"][0]["condition"]["basis"] == "declared literal"


@pytest.mark.parametrize(
    "mutate",
    [
        lambda c: c.update(kind="some"),
        lambda c: c.update(rule="text.equal-v1"),
        lambda c: c.update(path=["title"]),
        lambda c: c.update(item_path=["undeclared"]),
        lambda c: c.update(item_path=["paragraphs", True]),
        lambda c: c.update(item_path=["paragraphs"]),
        lambda c: c.update(subject="unknown"),
        lambda c: c.update(status="satisfied"),
        lambda c: c.update(predicate="callback"),
    ],
)
def test_universal_body_is_fully_admitted_before_values_even_when_empty(mutate):
    checked = graph()
    document = conditions(checked).document
    mutate(document["requirements"][0]["condition"])
    with pytest.raises(ContractError):
        Requirements.from_document(document, checked)


def test_failure_paths_are_bounded_but_the_verdict_still_checks_every_item():
    required = conditions(graph())
    condition = required.check(spec([""] * 129))["requirements"][0]["condition"]
    assert condition["checked_items"] == 129
    assert len(condition["failures"]) == 128
    assert condition["failures_complete"] is False
    assert condition["failures"][-1]["path"] == ["sections", 127, "heading"]


def test_item_check_capacity_refuses_instead_of_manufacturing_truth():
    checked = graph()
    required = conditions(checked)
    assert required.check(spec(["A"] * 4096))["status"] == "satisfied"
    with pytest.raises(ContractError, match="item-check budget"):
        required.check(spec(["A"] * 4097))
    source = required.document
    source["requirements"].append(
        {**deepcopy(source["requirements"][0]), "id": "again"}
    )
    with pytest.raises(ContractError, match="item-check budget"):
        Requirements.from_document(source, checked).check(spec(["A"] * 2049))


def test_universal_binding_gate_refuses_any_failing_item_before_callbacks():
    checked, calls = graph(), []

    def title(ports, attrs):
        calls.append("title")
        return ports["spec"]["title"]

    compiled = (
        Backend(
            "observed", "v1", checked.vocabulary.fingerprint, {"document.title": title}
        )
        .compile(
            checked,
            [checked.ref("title")],
        )
        .require(conditions(checked))
    )
    with pytest.raises(ContractError, match="not satisfied"):
        compiled.bind(spec(["A", ""]))
    assert calls == []
    assert compiled.bind(spec(["A", "B"])).execute().values == {"title": "A"}
    assert calls == ["title"]


@pytest.mark.parametrize("legacy_version", [1, 2, 3])
@pytest.mark.parametrize("reverse", [False, True])
def test_workflow_promotes_and_rewires_universal_and_older_conditions(
    legacy_version, reverse
):
    checked = graph()
    template = {
        "version": 1,
        "id": "all-headings",
        "revision": "v1",
        "graph": checked.document,
        "inputs": {"content": "draft"},
        "outputs": {"text": "published", "count": "paragraph_count"},
        "requirements": conditions(checked).document,
    }
    old = deepcopy(template)
    old["id"] = "nonempty-title"
    # v1 needs a Text subject; the template exposes a separate abstract title request.
    old_graph = checked.compose("request", "text.input", {})
    old["graph"] = old_graph.document
    old["inputs"]["request"] = "request"
    old["outputs"]["request"] = "request"
    condition = {"id": "title", "rule": "text.nonempty-v1", "subject": "request"}
    if legacy_version == 2:
        condition["path"] = []
    if legacy_version == 3:
        condition = {
            "id": "title",
            "rule": "text.nonempty-v1",
            "operands": [{"subject": "request", "path": []}],
        }
    old["requirements"] = {
        **conditions(checked).document,
        "version": legacy_version,
        "graph": old_graph.context,
        "requirements": [condition],
    }
    templates = [
        Workflow.from_document(d, checked.vocabulary)
        for d in ([old, template] if reverse else [template, old])
    ]
    base = old_graph
    instance = base
    for index, workflow in enumerate(templates):
        current = instance if type(instance) is Graph else instance.graph
        args = {"content": current.ref("draft")}
        if "request" in workflow.document["inputs"]:
            args["request"] = current.ref("request")
        instance = workflow.compose(instance, "stage" + str(index), args)
    assert instance.requirements.document["version"] == 4
    assert {
        r["condition"]["kind"] for r in instance.requirements.document["requirements"]
    } == {"relation", "every"}
    assert (
        instance.requirements.check({**spec(["A"]), "request": "A"})["status"]
        == "satisfied"
    )


def collection_graph(codec):
    manifest = document_vocabulary().document
    manifest["types"]["Collection"] = {"value": codec}
    manifest["operations"]["collection.input"] = {
        "role": "input",
        "ports": {},
        "attributes": {},
        "result": "Collection",
        "effects": [],
        "definition": None,
    }
    manifest["operations"]["collection.copy"] = {
        "role": "apply",
        "ports": {"value": {"accepts": ["Collection"], "multiplicity": "one"}},
        "attributes": {},
        "result": "Collection",
        "effects": [],
        "definition": None,
    }
    vocabulary = Vocabulary.from_document(manifest)
    return Graph.from_document(
        {
            "version": 1,
            "vocabulary": vocabulary.fingerprint,
            "objects": [
                {"id": "items", "op": "collection.input", "ports": {}, "attributes": {}}
            ],
            "outputs": ["items"],
        },
        vocabulary,
    )


@pytest.mark.parametrize(
    "codec,rule,value,status",
    [
        ({"kind": "text_list"}, "text.nonempty-v1", ["A", "B"], "satisfied"),
        ({"kind": "text_list"}, "text.nonempty-v1", ["A", ""], "refuted"),
        (
            {"kind": "array", "items": {"kind": "int"}},
            "exact.positive-v1",
            [1, 2],
            "satisfied",
        ),
        (
            {"kind": "array", "items": {"kind": "int"}},
            "exact.positive-v1",
            [1, 0],
            "refuted",
        ),
    ],
)
def test_universal_composition_depends_on_codec_without_a_domain_or_engine(
    codec, rule, value, status
):
    checked = collection_graph(codec)
    required = conditions(checked, subject="items", path=[], item_path=[], rule=rule)
    assert required.check({"items": value})["status"] == status


def test_shallow_collection_contract_cannot_supply_an_item_theory():
    checked = collection_graph({"kind": "array"})
    with pytest.raises(ContractError, match="declared collection items"):
        conditions(checked, subject="items", path=[], item_path=[])


def test_computed_collection_never_acquires_static_or_binding_evidence():
    checked = collection_graph({"kind": "text_list"})
    checked = checked.compose(
        "copy", "collection.copy", {"value": checked.ref("items")}
    )
    required = conditions(checked, subject="copy", path=[], item_path=[])
    assert required.check({"items": ["A"]})["status"] == "pending"
    backend = Backend(
        "observed",
        "v1",
        checked.vocabulary.fingerprint,
        {"collection.copy": lambda ports, attributes: ports["value"]},
    )
    with pytest.raises(ContractError, match="computed preconditions"):
        backend.compile(checked).require(required)


def test_aggregate_receipt_capacity_bounds_deep_failure_paths():
    field = "f" * 128
    codec, value = {"kind": "text"}, ""
    for _ in range(5):
        codec, value = {"kind": "record", "fields": {field: codec}}, {field: value}
    checked = collection_graph({"kind": "array", "items": codec})
    required = conditions(checked, subject="items", path=[], item_path=[field] * 5)
    source = required.document
    source["requirements"] = [
        {**deepcopy(source["requirements"][0]), "id": "all" + str(index)}
        for index in range(32)
    ]
    with pytest.raises(ContractError, match="byte budget"):
        Requirements.from_document(source, checked).check({"items": [value] * 128})
