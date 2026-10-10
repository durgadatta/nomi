"""Contract dependencies bind explicitly without extending value execution."""

import json
from pathlib import Path

import pytest

from tools.object_interface import (
    ContractError,
    Graph,
    Requirements,
    Workflow,
    load_document,
)
from tools.object_interface.__main__ import main
from tools.object_interface.backend import Backend
from tools.object_interface.documentary import document_backend, document_vocabulary
from tools.object_replay import replay_requirements

ROOT = Path(__file__).resolve().parents[4]
EXAMPLE = ROOT / "docs/research/object_framework"


def artifacts():
    checked = Graph.from_document(
        load_document(EXAMPLE / "document.json"), document_vocabulary()
    )
    checked = checked.compose("requested", "text.input", {})
    required = Requirements.from_document(
        {
            "version": 3,
            "graph": checked.context,
            "owner": "test.publication",
            "revision": "v1",
            "requirements": [
                {
                    "id": "title_matches",
                    "rule": "text.equal-v1",
                    "operands": [
                        {"subject": "draft", "path": ["title"]},
                        {"subject": "requested", "path": []},
                    ],
                }
            ],
        },
        checked,
    )
    return checked, required


def test_condition_only_input_inclusion_is_explicit_and_inspectable():
    checked, required = artifacts()
    compiled = document_backend(checked.vocabulary).compile(
        checked, [checked.ref("published")]
    )
    before = compiled.inspect()
    with pytest.raises(ContractError, match="outside selected realization"):
        compiled.require(required)
    gated = compiled.require(required, include_condition_inputs=True)
    view = gated.inspect()
    assert view["outputs"] == ["published"]
    assert view["required_inputs"] == ["draft", "requested"]
    assert view["computation_inputs"] == ["draft"]
    assert view["condition_inputs"] == ["requested"]
    assert view["condition_subjects"] == ["requested"]
    assert view["logical_to_physical"] == before["logical_to_physical"]
    assert compiled.inspect() == before
    assert required.check()["status"] == "pending"


def test_mismatching_condition_only_input_stops_before_computation():
    checked, required = artifacts()
    calls = []

    def title(ports, attributes):
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
        .require(required, include_condition_inputs=True)
    )
    with pytest.raises(ContractError, match="not satisfied"):
        compiled.bind({"draft": {"title": "A", "sections": []}, "requested": "B"})
    assert calls == []
    result = compiled.bind(
        {"draft": {"title": "A", "sections": []}, "requested": "A"}
    ).execute()
    assert result.values == {"title": "A"}
    assert calls == ["title"]
    with pytest.raises(ContractError, match="not requested"):
        result.get(checked.ref("requested"))
    receipt = result.receipt
    assert receipt["condition_inputs"] == ["requested"]
    assert (
        replay_requirements(
            checked.vocabulary.document,
            checked.document,
            required.document,
            receipt["requirement_evidence"],
            {"draft": {"title": "A", "sections": []}, "requested": "A"},
        )["verdict"]
        == "satisfied"
    )


@pytest.mark.parametrize(
    "values",
    [
        {"draft": {"title": "A", "sections": []}},
        {"draft": {"title": "A", "sections": []}, "requested": 1},
        {"draft": {"title": "A", "sections": []}, "requested": "A", "extra": "A"},
    ],
)
def test_all_condition_inputs_need_exact_typed_bindings(values):
    checked, required = artifacts()
    compiled = (
        document_backend(checked.vocabulary)
        .compile(checked, [checked.ref("published")])
        .require(required, include_condition_inputs=True)
    )
    with pytest.raises(ContractError):
        compiled.bind(values)


def test_aliases_and_repeated_operands_bind_one_underlying_slot():
    checked, required = artifacts()
    checked = checked.compose(
        "alias", "text.alias", {"target": checked.ref("requested")}
    )
    source = required.document
    source["graph"] = checked.context
    source["requirements"].append(
        {
            "id": "repeated",
            "rule": "text.equal-v1",
            "operands": [
                {"subject": "alias", "path": []},
                {"subject": "requested", "path": []},
            ],
        }
    )
    source["requirements"][0]["operands"][1]["subject"] = "alias"
    required = Requirements.from_document(source, checked)
    compiled = (
        document_backend(checked.vocabulary)
        .compile(checked, [checked.ref("published")])
        .require(required, include_condition_inputs=True)
    )
    assert compiled.inspect()["condition_inputs"] == ["requested"]
    assert compiled.inspect()["condition_subjects"] == ["requested", "alias"]
    assert compiled.bind(
        {"draft": {"title": "A", "sections": []}, "requested": "A"}
    ).execute().values == {"published": "A\n"}


def test_static_condition_only_literal_needs_no_binding_or_backend_support():
    checked, required = artifacts()
    checked = checked.compose("literal", "text.literal", {}, {"value": "A"})
    source = required.document
    source["graph"] = checked.context
    source["requirements"][0]["operands"][1]["subject"] = "literal"
    required = Requirements.from_document(source, checked)
    compiled = (
        document_backend(checked.vocabulary)
        .compile(checked, [checked.ref("draft")])
        .require(required, include_condition_inputs=True)
    )
    assert compiled.inspect()["condition_inputs"] == []
    assert compiled.inspect()["condition_subjects"] == ["literal"]
    assert compiled.inspect()["required_inputs"] == ["draft"]
    assert compiled.bind(
        {"draft": {"title": "A", "sections": []}}
    ).execute().values == {"draft": {"title": "A", "sections": []}}


def test_inclusion_never_executes_computed_condition_dependencies():
    checked, required = artifacts()
    source = required.document
    source["requirements"][0]["operands"][1]["subject"] = "title"
    required = Requirements.from_document(source, checked)
    compiled = document_backend(checked.vocabulary).compile(
        checked, [checked.ref("draft")]
    )
    with pytest.raises(ContractError, match="computed preconditions"):
        compiled.require(required, include_condition_inputs=True)


@pytest.mark.parametrize("flag", [1, None, "yes", []])
def test_condition_input_inclusion_is_not_an_implicit_truthy_flag(flag):
    checked, required = artifacts()
    with pytest.raises(ContractError, match="explicit boolean"):
        document_backend(checked.vocabulary).compile(checked).require(
            required, include_condition_inputs=flag
        )


def test_workflow_exports_can_omit_condition_only_inputs_without_dropping_conditions():
    checked, required = artifacts()
    document = checked.document
    document["outputs"] = ["published"]
    template_graph = Graph.from_document(document, checked.vocabulary)
    source = required.document
    source["graph"] = template_graph.context
    workflow = Workflow.from_document(
        {
            "version": 1,
            "id": "publication",
            "revision": "v1",
            "graph": document,
            "inputs": {"content": "draft", "requested_title": "requested"},
            "outputs": {"text": "published"},
            "requirements": source,
        },
        checked.vocabulary,
    )
    instance = workflow.compose(
        checked,
        "copy",
        {"content": checked.ref("draft"), "requested_title": checked.ref("requested")},
    )
    with pytest.raises(ContractError, match="outside selected realization"):
        instance.compile(
            document_backend(checked.vocabulary), [instance.outputs["text"]]
        )
    compiled = instance.compile(
        document_backend(checked.vocabulary),
        [instance.outputs["text"]],
        include_condition_inputs=True,
    )
    assert compiled.inspect()["required_inputs"] == ["draft", "requested"]
    assert compiled.bind(
        {"draft": {"title": "A", "sections": []}, "requested": "A"}
    ).execute().values == {"copy.published": "A\n"}


def test_cli_condition_input_inclusion_requires_a_contract_and_runs_it(
    tmp_path, capsys
):
    checked, required = artifacts()
    files = {}
    for label, document in {
        "graph": checked.document,
        "required": required.document,
        "bindings": {"draft": {"title": "A", "sections": []}, "requested": "A"},
    }.items():
        path = tmp_path / (label + ".json")
        path.write_text(json.dumps(document))
        files[label] = str(path)
    args = [
        "--vocabulary",
        str(ROOT / "config/document_interface.json"),
        "run",
        files["graph"],
        files["bindings"],
        "--backend",
        "document-blocks",
        "--output",
        "published",
        "--include-condition-inputs",
    ]
    assert main(args) == 2
    assert "requires an explicit requirement artifact" in capsys.readouterr().err
    assert main(args + ["--requirements", files["required"]]) == 0
    result = json.loads(capsys.readouterr().out)
    assert result["values"] == {"published": "A\n"}
    assert result["receipt"]["condition_inputs"] == ["requested"]
