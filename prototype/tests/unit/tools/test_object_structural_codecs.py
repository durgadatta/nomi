"""Domain contracts compose structurally and report independent input paths."""

from copy import deepcopy

import pytest

from tools.object_interface import ContractError, Graph, Vocabulary
from tools.object_interface.backend import Backend
from tools.object_interface.documents import ValueContractError, schema, value_report
from tools.object_interface.examples import lab_vocabulary

DOCUMENT = {
    "kind": "record",
    "fields": {
        "title": {"kind": "text"},
        "sections": {
            "kind": "array",
            "items": {
                "kind": "record",
                "fields": {
                    "heading": {"kind": "text"},
                    "paragraphs": {"kind": "array", "items": {"kind": "text"}},
                },
            },
        },
    },
}


def structured_graph():
    document = lab_vocabulary().document
    document["types"]["Draft"] = {"value": DOCUMENT}
    document["operations"]["draft.input"] = {
        "role": "input",
        "ports": {},
        "attributes": {},
        "result": "Draft",
        "effects": [],
        "definition": None,
    }
    vocabulary = Vocabulary.from_document(document)
    graph = Graph.from_document(
        {
            "version": 1,
            "vocabulary": vocabulary.fingerprint,
            "objects": [
                {"id": "draft", "op": "draft.input", "ports": {}, "attributes": {}},
            ],
            "outputs": ["draft"],
        },
        vocabulary,
    )
    return graph


def test_closed_records_and_arrays_compose_without_values_or_engines():
    graph = structured_graph()
    assert graph.check()["status"] == "composition-checked"
    assert graph.inspect("draft")["realization"] == "unbound"
    value = {
        "title": "Plan",
        "sections": [{"heading": "Start", "paragraphs": ["First.", "Second."]}],
    }
    result = (
        Backend("inert", "v1", graph.vocabulary.fingerprint, {})
        .compile(graph)
        .bind({"draft": value})
        .execute()
    )
    assert result.values == {"draft": value}


def test_independent_nested_failures_accumulate_with_original_paths():
    report = value_report(
        {
            "title": 1,
            "sections": [
                {"heading": False, "paragraphs": ["ok", 7], "extra": "private"}
            ],
        },
        DOCUMENT,
    )
    assert report == {
        "status": "invalid",
        "complete": True,
        "errors": [
            {
                "path": ["sections", 0, "heading"],
                "code": "wrong-value-kind",
                "expected": "text",
            },
            {
                "path": ["sections", 0, "paragraphs", 1],
                "code": "wrong-value-kind",
                "expected": "text",
            },
            {
                "path": ["sections", 0, "extra"],
                "code": "unexpected-field",
                "expected": "absent field",
            },
            {"path": ["title"], "code": "wrong-value-kind", "expected": "text"},
        ],
    }
    assert "private" not in str(report)


def test_missing_null_and_empty_remain_distinct_and_no_defaults_are_added():
    assert value_report({}, DOCUMENT)["errors"] == [
        {"path": ["sections"], "code": "missing-field", "expected": "array"},
        {"path": ["title"], "code": "missing-field", "expected": "text"},
    ]
    assert (
        value_report({"title": None, "sections": []}, DOCUMENT)["status"] == "invalid"
    )
    assert value_report({"title": "", "sections": []}, DOCUMENT)["status"] == "valid"
    assert (
        value_report(
            {"title": "x", "sections": [{"heading": "x", "paragraphs": []}]}, DOCUMENT
        )["status"]
        == "valid"
    )


def test_binding_errors_retain_detached_accumulated_report():
    graph = structured_graph()
    with pytest.raises(ValueContractError) as caught:
        Backend("inert", "v1", graph.vocabulary.fingerprint, {}).compile(graph).bind(
            {"draft": {"title": False, "sections": None}}
        )
    report = caught.value.report
    assert len(report["errors"]) == 2
    report["errors"].clear()
    assert len(caught.value.report["errors"]) == 2


@pytest.mark.parametrize(
    "contract",
    [
        {"kind": "record", "fields": []},
        {"kind": "record", "fields": {"x": {"kind": "unknown"}}},
        {"kind": "array", "items": None},
        {"kind": "array", "items": {"kind": "text"}, "default": []},
        {"kind": "record", "fields": {}, "extra": "allow"},
    ],
)
def test_unadmitted_schema_forms_are_refused(contract):
    with pytest.raises(ContractError):
        schema(contract)


def test_recursive_schema_is_refused_and_errors_are_bounded():
    contract = {"kind": "array"}
    contract["items"] = contract
    with pytest.raises(ContractError, match="nesting budget"):
        schema(contract)
    report = value_report([False] * 129, {"kind": "array", "items": {"kind": "int"}})
    assert len(report["errors"]) == 128
    assert report["complete"] is False


def test_existing_bare_container_codecs_keep_shallow_meaning():
    assert (
        value_report({"anything": [1, None, False]}, {"kind": "record"})["status"]
        == "valid"
    )
    assert value_report([{}, "x", 1], {"kind": "array"})["status"] == "valid"
    assert value_report(True, {"kind": "int"})["status"] == "invalid"


def test_codec_payload_and_nominal_families_survive_round_trip():
    graph = structured_graph()
    document = deepcopy(graph.vocabulary.document)
    restored = Vocabulary.from_document(document)
    assert restored.document["types"]["Draft"]["value"] == DOCUMENT
    assert restored.fingerprint == graph.vocabulary.fingerprint
