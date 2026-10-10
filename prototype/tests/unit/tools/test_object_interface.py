"""Domain-neutral composition conformance; no source/runtime admission."""

from copy import deepcopy
import json
from pathlib import Path

import pytest

from tools.object_interface import (
    ContractError,
    Graph,
    Reference,
    Vocabulary,
    load_document,
)
from tools.object_interface.documents import MAX_BYTES
from tools.object_interface.examples import lab_vocabulary

ROOT = Path(__file__).resolve().parents[4]


def fixture_graph():
    return load_document(ROOT / "docs/research/object_framework/composition.json")


def graph(document=None, vocabulary=None):
    vocabulary = vocabulary or lab_vocabulary()
    document = fixture_graph() if document is None else document
    document["vocabulary"] = vocabulary.fingerprint
    return Graph.from_document(document, vocabulary)


def obj(document, identity):
    return next(item for item in document["objects"] if item["id"] == identity)


def test_arithmetic_and_document_descriptions_exist_without_bindings():
    checked = graph()
    assert checked.check()["status"] == "composition-checked"
    assert checked.check()["execution"] == "not performed"
    assert checked.ref("document").inspect()["role"] == "description"
    assert checked.ref("quantity").inspect()["realization"] == "unbound"
    assert checked.check()["domain_validity"] == "not established"


def test_closed_composition_replays_without_evaluating_unknown_input():
    checked = graph()
    receipt = checked.compare("squared", "expanded_square")
    assert receipt["status"] == "equivalent"
    assert checked.verify(receipt)["independent_checker"] is False
    assert checked.compare("published", "greeting")["status"] == "equivalent"
    assert checked.compare("quantity", "squared")["status"] == "unknown"


def test_input_identity_survives_equal_type_and_shape():
    document = fixture_graph()
    document["objects"].append(
        {"id": "other_quantity", "op": "exact.input", "ports": {}, "attributes": {}}
    )
    assert graph(document).compare("quantity", "other_quantity")["status"] == "unknown"


def test_description_identity_does_not_assert_semantic_or_scientific_equivalence():
    document = fixture_graph()
    other = deepcopy(obj(document, "document"))
    other["id"] = "other_document"
    document["objects"].append(other)
    assert graph(document).compare("document", "other_document")["status"] == "unknown"


def test_immutable_graph_detaches_all_public_snapshots():
    document = fixture_graph()
    checked = graph(document)
    document["objects"].clear()
    exported = checked.document
    exported["objects"].clear()
    inspection = checked.inspect("prefix")
    inspection["attributes"]["value"] = "mutated"
    assert checked.inspect("prefix")["attributes"]["value"] == "Hello, "
    for target, key in ((checked, "_context"), (checked.vocabulary, "_document")):
        with pytest.raises(AttributeError):
            setattr(target, key, "mutated")
        with pytest.raises(AttributeError):
            delattr(target, key)
    with pytest.raises(AttributeError):
        checked.ref("quantity").id = "other"


def test_functional_composition_creates_new_context_and_preserves_old_reference():
    original = graph()
    ref = original.ref("quantity")
    revised = original.compose("more", "exact.double", {"value": ref})
    assert ref.context == original.context
    assert revised.context != original.context
    assert revised.ref("more").inspect()["type"] == "ExactInt"
    with pytest.raises(ContractError, match="exact graph revision"):
        revised.compose("mixed", "exact.double", {"value": ref})
    with pytest.raises(ContractError):
        Reference(original, "missing")


@pytest.mark.parametrize(
    "mutation, message",
    [
        (lambda d: obj(d, "squared")["ports"].update(value="name"), "received Text"),
        (
            lambda d: obj(d, "squared")["ports"].update(value="missing"),
            "unknown references",
        ),
        (lambda d: obj(d, "squared")["ports"].update(value="doubled"), "cyclic"),
        (lambda d: obj(d, "prefix")["attributes"].update(value=True), "expected text"),
        (
            lambda d: obj(d, "quantity")["attributes"].update(data=[]),
            "expected exactly",
        ),
        (
            lambda d: d["objects"].append(deepcopy(d["objects"][0])),
            "duplicate identity",
        ),
        (lambda d: d.update(outputs=["missing"]), "unknown output"),
        (lambda d: d.update(outputs=["quantity", "quantity"]), "duplicate reference"),
        (lambda d: d.update(version=True), "unsupported graph"),
        (
            lambda d: obj(d, "squared").update(op="unknown.operation"),
            "unknown operation",
        ),
    ],
)
def test_invalid_composition_is_refused_without_engine(mutation, message):
    document = fixture_graph()
    mutation(document)
    with pytest.raises(ContractError, match=message):
        graph(document)


def test_vocabulary_revision_is_content_pinned():
    vocabulary = lab_vocabulary()
    manifest = vocabulary.document
    manifest["revision"] = "v2"
    changed = Vocabulary.from_document(manifest)
    assert changed.fingerprint != vocabulary.fingerprint
    with pytest.raises(ContractError, match="fingerprint"):
        Graph.from_document(fixture_graph(), changed)


@pytest.mark.parametrize(
    "mutation, message",
    [
        (
            lambda d: d["operations"]["exact.double"]["definition"]["objects"][
                0
            ].update(op="exact.double", ports={"value": "$value"}),
            "cyclic",
        ),
        (
            lambda d: d["operations"]["exact.double"]["definition"].update(
                output="missing"
            ),
            "output",
        ),
        (
            lambda d: d["operations"]["exact.double"]["definition"]["objects"][
                0
            ].update(op="text.concat"),
            "received ExactInt",
        ),
        (
            lambda d: d["operations"]["exact.double"]["definition"]["objects"][
                0
            ].update(op="exact.input", ports={}),
            "pure realizable",
        ),
        (
            lambda d: d["operations"]["exact.add"].update(effects=["File"]),
            "pure realizable",
        ),
        (
            lambda d: d["operations"]["exact.alias"]["ports"]["target"].update(
                accepts=["Text"]
            ),
            "alias",
        ),
        (
            lambda d: d["operations"]["exact.literal"]["attributes"].update(
                value={"kind": "bool"}
            ),
            "literal",
        ),
    ],
)
def test_vocabulary_checks_definitions_and_preserves_purity(mutation, message):
    manifest = lab_vocabulary().document
    mutation(manifest)
    with pytest.raises(ContractError, match=message):
        Vocabulary.from_document(manifest)


def test_diamond_definitions_share_terms_without_exponential_expansion():
    manifest = lab_vocabulary().document
    for index in range(35):
        child_op = "exact.double" if index == 0 else f"nested.d{index - 1}"
        operation = deepcopy(manifest["operations"]["exact.double"])
        operation["definition"]["objects"] = [
            {"id": "a", "op": child_op, "ports": {"value": "$value"}, "attributes": {}},
            {"id": "b", "op": child_op, "ports": {"value": "$value"}, "attributes": {}},
            {
                "id": "c",
                "op": "exact.add",
                "ports": {"left": "a", "right": "b"},
                "attributes": {},
            },
        ]
        operation["definition"]["output"] = "c"
        manifest["operations"][f"nested.d{index}"] = operation
    vocabulary = Vocabulary.from_document(manifest)
    document = fixture_graph()
    obj(document, "squared")["op"] = "nested.d34"
    checked = graph(document, vocabulary)
    assert len(checked.normal_form("squared")["terms"]) == 37


def test_effectful_objects_keep_distinct_normal_identity():
    manifest = lab_vocabulary().document
    effectful = deepcopy(manifest["operations"]["text.concat"])
    effectful["effects"] = ["Console"]
    manifest["operations"]["text.print"] = effectful
    vocabulary = Vocabulary.from_document(manifest)
    document = fixture_graph()
    for identity in ("print_a", "print_b"):
        document["objects"].append(
            {
                "id": identity,
                "op": "text.print",
                "ports": {"left": "prefix", "right": "name"},
                "attributes": {},
            }
        )
    assert (
        graph(document, vocabulary).compare("print_a", "print_b")["status"] == "unknown"
    )


def test_receipts_cannot_cross_changed_graph_or_be_forged():
    checked = graph()
    receipt = checked.compare("squared", "expanded_square")
    receipt["basis"] = "guessed"
    with pytest.raises(ContractError, match="replay"):
        checked.verify(receipt)
    receipt = checked.compare("squared", "expanded_square")
    changed = checked.compose(
        "later", "exact.double", {"value": checked.ref("quantity")}
    )
    with pytest.raises(ContractError, match="replay"):
        changed.verify(receipt)


@pytest.mark.parametrize("value", [1.5, float("nan"), object(), lambda: None])
def test_no_host_values_or_callbacks_in_descriptions(value):
    document = fixture_graph()
    obj(document, "prefix")["attributes"]["value"] = value
    with pytest.raises(ContractError, match="inert JSON"):
        graph(document)


def test_document_loader_rejects_duplicates_and_oversized_artifacts(tmp_path):
    path = tmp_path / "description.json"
    path.write_text('{"version":1,"version":2}')
    with pytest.raises(ContractError, match="duplicate JSON key"):
        load_document(path)
    path.write_text(json.dumps("x" * MAX_BYTES))
    with pytest.raises(ContractError, match="byte budget"):
        load_document(path)
