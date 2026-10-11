"""Refused realizations preserve evidence a caller can inspect and replay."""

import json
from pathlib import Path

import pytest

from tools.object_interface import (
    Graph,
    RequirementContractError,
    Requirements,
    load_document,
)
from tools.object_interface.__main__ import main
from tools.object_interface.documentary import document_backend, document_vocabulary
from tools.object_interface.examples import lab_vocabulary, python_backend
from tools.object_replay import replay_requirements

ROOT = Path(__file__).resolve().parents[4]
EXAMPLE = ROOT / "docs/research/object_framework"


@pytest.mark.parametrize("version", [1, 2, 3, 4])
def test_required_binding_failure_retains_a_detached_replayable_report(version):
    if version == 1:
        graph = Graph.from_document(
            load_document(EXAMPLE / "composition.json"), lab_vocabulary()
        )
        source = load_document(EXAMPLE / "requirements.json")
        bindings, backend = (
            {"quantity": 0, "name": "Ada"},
            python_backend(graph.vocabulary),
        )
    else:
        graph = Graph.from_document(
            load_document(EXAMPLE / "publication.json"), document_vocabulary()
        )
        if version == 2:
            source = {
                **load_document(EXAMPLE / "document_requirements.json"),
                "graph": graph.context,
            }
            bindings = {"draft": {"title": "", "sections": []}}
        else:
            source = load_document(
                EXAMPLE
                / (
                    "publication_requirements.json"
                    if version == 3
                    else "publication_requirements_v4.json"
                )
            )
            bindings = {
                "draft": {"title": "private supplied title", "sections": []},
                "requested": "different private request",
            }
        backend = document_backend(graph.vocabulary)
    required = Requirements.from_document(source, graph)
    compiled = backend.compile(graph).require(required, include_condition_inputs=True)
    with pytest.raises(RequirementContractError) as failure:
        compiled.bind(bindings)
    report = failure.value.report
    assert report == required.check(bindings)
    assert report["status"] == "refuted"
    assert report["evidence_phase"] == "binding"
    assert (
        replay_requirements(
            graph.vocabulary.document, graph.document, source, report, bindings
        )["verdict"]
        == "refuted"
    )
    report["requirements"].clear()
    assert failure.value.report["requirements"]
    assert "private" not in json.dumps(failure.value.report)


def test_static_literal_refusal_retains_static_evidence():
    graph = Graph.from_document(
        load_document(EXAMPLE / "publication.json"), document_vocabulary()
    )
    graph = graph.compose("first", "text.literal", {}, {"value": "A"})
    graph = graph.compose("second", "text.literal", {}, {"value": "B"})
    source = {
        "version": 3,
        "graph": graph.context,
        "owner": "test.literal",
        "revision": "v1",
        "requirements": [
            {
                "id": "same",
                "rule": "text.equal-v1",
                "operands": [
                    {"subject": "first", "path": []},
                    {"subject": "second", "path": []},
                ],
            }
        ],
    }
    required = Requirements.from_document(source, graph)
    with pytest.raises(RequirementContractError) as failure:
        document_backend(graph.vocabulary).compile(graph, [graph.ref("first")]).require(
            required, include_condition_inputs=True
        )
    assert failure.value.report["evidence_phase"] == "static"
    assert (
        replay_requirements(
            graph.vocabulary.document, graph.document, source, failure.value.report
        )["verdict"]
        == "refuted"
    )


@pytest.mark.parametrize(
    "rule,changed,indexed",
    [
        ("publication_requirements.json", "request", False),
        ("publication_requirements_v4.json", "heading", True),
    ],
)
def test_cli_refusal_returns_relation_or_indexed_counterexample_evidence(
    rule, changed, indexed, tmp_path, capsys
):
    bindings = load_document(EXAMPLE / "publication_bindings.json")
    if changed == "request":
        bindings["requested"] = "private changed request"
    else:
        bindings["draft"]["sections"][1]["heading"] = ""
    path = tmp_path / "bindings.json"
    path.write_text(json.dumps(bindings))
    assert (
        main(
            [
                "--vocabulary",
                str(ROOT / "config/document_interface.json"),
                "run",
                str(EXAMPLE / "publication.json"),
                str(path),
                "--backend",
                "document-blocks",
                "--requirements",
                str(EXAMPLE / rule),
                "--include-condition-inputs",
            ]
        )
        == 2
    )
    captured = capsys.readouterr()
    assert captured.out == ""
    error = json.loads(captured.err)
    assert error["kind"] == "requirement-contract"
    assert error["evidence"]["status"] == "refuted"
    assert "private" not in captured.err
    refuted = [r for r in error["evidence"]["requirements"] if r["status"] == "refuted"]
    if indexed:
        assert refuted[0]["condition"]["failures"] == [
            {"path": ["sections", 1, "heading"], "code": "predicate-refuted"}
        ]
    else:
        assert [o["subject"] for o in refuted[0]["operands"]] == ["draft", "requested"]
