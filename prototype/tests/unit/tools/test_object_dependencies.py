"""Dependency explanation distinguishes source references, normalized reuse and gates."""

import json
from pathlib import Path
import subprocess
import sys

import pytest

from tools.object_interface import (
    ContractError,
    Graph,
    Requirements,
    Revision,
    Vocabulary,
    load_document,
)
from tools.object_interface.__main__ import main as producer_main
from tools.object_interface.backend import Backend
from tools.object_interface.documentary import document_vocabulary
from tools.object_interface.examples import lab_vocabulary, python_backend
from tools.object_replay import ReplayError, main, replay_dependencies

ROOT = Path(__file__).resolve().parents[4]
EXAMPLE = ROOT / "docs/research/object_framework"


def graph():
    return Graph.from_document(
        load_document(EXAMPLE / "composition.json"), lab_vocabulary()
    )


@pytest.mark.parametrize(
    "identity",
    [
        "quantity",
        "squared",
        "expanded_square",
        "doubled",
        "prefix",
        "name",
        "greeting",
        "published",
        "document",
    ],
)
def test_dependencies_replay_for_each_named_object_without_inputs(identity):
    checked = graph()
    receipt = checked.ref(identity).dependencies()
    assert receipt["execution"] == "not performed"
    assert receipt["context"] == checked.context
    assert (
        replay_dependencies(
            checked.vocabulary.document, checked.document, identity, receipt
        )["independent_checker"]
        is True
    )


def test_logical_dependents_do_not_confuse_shared_physical_terms_with_edit_targets():
    checked = graph()
    assert checked.compare("squared", "expanded_square")["status"] == "equivalent"
    assert checked.dependencies("squared")["logical_dependents"] == ["doubled"]
    assert checked.dependencies("expanded_square")["logical_dependents"] == []
    assert checked.dependencies("squared")["logical_outputs"] == ["doubled"]
    assert checked.dependencies("expanded_square")["logical_outputs"] == []
    assert checked.dependencies("published")["logical_dependents"] == ["document"]
    assert checked.dependencies("published")["normalized_inputs"] == ["name"]
    revision = Revision.from_document(
        {
            "version": 1,
            "graph": checked.context,
            "replacements": [
                {
                    "id": "expanded_square",
                    "op": "exact.add",
                    "ports": {"left": "quantity", "right": "quantity"},
                    "attributes": {},
                },
            ],
        },
        checked,
    )
    assert revision.graph.compare("squared", "expanded_square")["status"] == "unknown"
    assert python_backend(checked.vocabulary).compile(
        revision.graph, [revision.graph.ref("doubled")]
    ).bind({"quantity": 3}).execute().values == {"doubled": 18}


def test_declared_but_unused_definition_parameters_are_separate_from_normalized_inputs():
    vocabulary = lab_vocabulary().document
    vocabulary["operations"]["exact.first"] = {
        "role": "derived",
        "ports": {
            port: {"accepts": ["ExactInt"], "multiplicity": "one"}
            for port in ("left", "right")
        },
        "attributes": {},
        "result": "ExactInt",
        "effects": [],
        "definition": {
            "objects": [
                {
                    "id": "first",
                    "op": "exact.alias",
                    "ports": {"target": "$left"},
                    "attributes": {},
                }
            ],
            "output": "first",
        },
    }
    vocabulary = Vocabulary.from_document(vocabulary)
    checked = Graph.from_document(
        {
            "version": 1,
            "vocabulary": vocabulary.fingerprint,
            "objects": [
                {"id": "a", "op": "exact.input", "ports": {}, "attributes": {}},
                {"id": "b", "op": "exact.input", "ports": {}, "attributes": {}},
                {
                    "id": "first",
                    "op": "exact.first",
                    "ports": {"left": "a", "right": "b"},
                    "attributes": {},
                },
            ],
            "outputs": ["first"],
        },
        vocabulary,
    )
    receipt = checked.dependencies("first")
    assert receipt["logical_inputs"] == ["a", "b"]
    assert receipt["normalized_inputs"] == ["a"]
    compiled = Backend("empty", "v1", vocabulary.fingerprint, {}).compile(checked)
    assert compiled.explain_input("a")["computation_outputs"] == ["first"]
    with pytest.raises(ContractError, match="unknown required input"):
        compiled.explain_input("b")
    assert compiled.bind({"a": 2}).execute().values == {"first": 2}
    with pytest.raises(ReplayError, match="vocabulary"):
        replay_dependencies(vocabulary.document, checked.document, "first", receipt)


def test_arithmetic_input_explanation_preserves_selected_output_names_and_condition_usage():
    checked = graph()
    required = Requirements.from_document(
        load_document(EXAMPLE / "requirements.json"), checked
    )
    compiled = python_backend(checked.vocabulary).compile(checked).require(required)
    quantity = compiled.explain_input("quantity")
    assert quantity["role"] == "both"
    assert quantity["computation_outputs"] == ["doubled"]
    assert quantity["conditions"] == [
        {
            "id": "positive_quantity",
            "rule": "exact.positive-v1",
            "kind": "relation",
            "operands": [{"index": 0, "subject": "quantity", "path": []}],
        }
    ]
    assert compiled.explain_input("name")["computation_outputs"] == ["published"]
    assert (
        python_backend(checked.vocabulary)
        .compile(checked)
        .explain_input("quantity")["role"]
        == "computation"
    )


def test_condition_only_request_explanation_and_all_item_paths_need_no_execution():
    checked = Graph.from_document(
        load_document(EXAMPLE / "publication.json"), document_vocabulary()
    )
    required = Requirements.from_document(
        load_document(EXAMPLE / "publication_requirements_v4.json"), checked
    )
    calls = []
    backend = Backend(
        "observed",
        "v1",
        checked.vocabulary.fingerprint,
        {
            "document.title": lambda ports, attrs: (
                calls.append("title") or ports["spec"]["title"]
            ),
        },
    )
    compiled = backend.compile(checked, [checked.ref("title")]).require(
        required, include_condition_inputs=True
    )
    requested = compiled.explain_input("requested")
    assert requested["role"] == "condition"
    assert requested["computation_outputs"] == []
    assert requested["conditions"] == [
        {
            "id": "title_matches",
            "rule": "text.equal-v1",
            "kind": "relation",
            "operands": [{"index": 1, "subject": "requested", "path": []}],
        }
    ]
    draft = compiled.explain_input("draft")
    assert draft["role"] == "both"
    assert [c["id"] for c in draft["conditions"]] == [
        "title_matches",
        "has_sections",
        "all_headings",
        "all_sections_have_paragraphs",
    ]
    assert draft["conditions"][2]["kind"] == "every"
    assert draft["conditions"][2]["item_path"] == ["heading"]
    assert calls == []
    assert checked.dependencies("requested")["logical_outputs"] == []


def test_alias_and_repeated_condition_operands_remain_explainable_without_duplicate_bindings():
    checked = graph()
    checked = checked.compose(
        "other_name", "text.alias", {"target": checked.ref("name")}
    )
    required = Requirements.from_document(
        {
            "version": 3,
            "graph": checked.context,
            "owner": "test.explanation",
            "revision": "v1",
            "requirements": [
                {
                    "id": "same",
                    "rule": "text.equal-v1",
                    "operands": [
                        {"subject": "name", "path": []},
                        {"subject": "other_name", "path": []},
                    ],
                }
            ],
        },
        checked,
    )
    compiled = (
        python_backend(checked.vocabulary)
        .compile(checked, [checked.ref("published")])
        .require(required)
    )
    assert compiled.inspect()["required_inputs"] == ["name"]
    assert compiled.explain_input("name")["conditions"][0]["operands"] == [
        {"index": 0, "subject": "name", "path": []},
        {"index": 1, "subject": "other_name", "path": []},
    ]


def test_dependencies_are_dag_reachability_not_path_enumeration_or_multiplicity():
    vocabulary = lab_vocabulary()
    objects = [{"id": "input", "op": "exact.input", "ports": {}, "attributes": {}}]
    previous = "input"
    for index in range(32):
        identity = "layer" + str(index)
        objects.append(
            {
                "id": identity,
                "op": "exact.add",
                "ports": {"left": previous, "right": previous},
                "attributes": {},
            }
        )
        previous = identity
    checked = Graph.from_document(
        {
            "version": 1,
            "vocabulary": vocabulary.fingerprint,
            "objects": objects,
            "outputs": [previous],
        },
        vocabulary,
    )
    receipt = checked.dependencies(previous)
    assert len(receipt["logical_dependencies"]) == 32
    assert receipt["logical_inputs"] == receipt["normalized_inputs"] == ["input"]
    assert len(checked.dependencies("input")["logical_dependents"]) == 32
    assert (
        replay_dependencies(vocabulary.document, checked.document, previous, receipt)[
            "status"
        ]
        == "verified"
    )


def test_dependency_order_is_source_layer_order_and_exports_preserve_detachment():
    checked = graph()
    raw = checked.document
    raw["objects"] = list(reversed(raw["objects"]))
    checked = Graph.from_document(raw, checked.vocabulary)
    receipt = checked.dependencies("document")
    assert (
        replay_dependencies(
            checked.vocabulary.document, checked.document, "document", receipt
        )["status"]
        == "verified"
    )
    receipt["logical_inputs"].clear()
    assert checked.dependencies("document")["logical_inputs"] == ["name"]
    compiled = python_backend(checked.vocabulary).compile(checked)
    explanation = compiled.explain_input("name")
    explanation["computation_outputs"].clear()
    assert compiled.explain_input("name")["computation_outputs"] == ["published"]


@pytest.mark.parametrize(
    "mutate",
    [
        lambda r: r.update(context="forged"),
        lambda r: r.update(subject="quantity"),
        lambda r: r.update(logical_inputs=[]),
        lambda r: r.update(normalized_inputs=[]),
        lambda r: r.update(logical_dependencies=[]),
        lambda r: r.update(logical_dependents=[]),
        lambda r: r.update(logical_outputs=[]),
        lambda r: r.update(execution="completed"),
        lambda r: r.update(scope="causal proof"),
    ],
)
def test_independent_dependency_replay_refuses_edited_reach_and_claims(mutate):
    checked = graph()
    receipt = checked.dependencies("greeting")
    mutate(receipt)
    with pytest.raises(ReplayError):
        replay_dependencies(
            checked.vocabulary.document, checked.document, "greeting", receipt
        )


def test_dependency_receipt_does_not_survive_graph_revision():
    checked = graph()
    receipt = checked.dependencies("greeting")
    revision = Revision.from_document(
        load_document(EXAMPLE / "greeting_revision.json"), checked
    )
    with pytest.raises(ReplayError):
        replay_dependencies(
            checked.vocabulary.document, revision.graph.document, "greeting", receipt
        )


@pytest.mark.parametrize("identity", ["missing", "prefix", None, True, []])
def test_input_explanation_refuses_literals_unknown_and_non_required_slots(identity):
    checked = graph()
    compiled = python_backend(checked.vocabulary).compile(
        checked, [checked.ref("doubled")]
    )
    with pytest.raises(ContractError, match="unknown required input"):
        compiled.explain_input(identity)


@pytest.mark.parametrize(
    "extra", ["--bindings", "--revision", "--workflow", "--requirements"]
)
def test_dependency_replay_refuses_unrelated_operation_flags(extra, capsys):
    assert (
        main(
            [
                str(ROOT / "config/object_interface.json"),
                str(EXAMPLE / "composition.json"),
                "unused.json",
                "--dependencies",
                "quantity",
                extra,
                "unused.json",
            ]
        )
        == 2
    )
    assert "separate" in capsys.readouterr().err


def test_cli_dependency_receipt_replays_without_importing_framework(tmp_path, capsys):
    assert (
        producer_main(["dependencies", str(EXAMPLE / "composition.json"), "greeting"])
        == 0
    )
    receipt = tmp_path / "dependencies.json"
    receipt.write_text(capsys.readouterr().out)
    script = """import importlib.abc, runpy, sys
class DenyProducer(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if fullname.split('.')[0] in ('tools', 'prototype'):
            raise RuntimeError('producer import forbidden')
sys.meta_path.insert(0, DenyProducer())
consumer = sys.argv.pop(1)
sys.argv[0] = consumer
runpy.run_path(consumer, run_name='__main__')
"""
    result = subprocess.run(
        [
            sys.executable,
            "-I",
            "-c",
            script,
            str(ROOT / "tools/object_replay.py"),
            str(ROOT / "config/object_interface.json"),
            str(EXAMPLE / "composition.json"),
            str(receipt),
            "--dependencies",
            "greeting",
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout)["independent_checker"] is True


def test_cli_why_input_reports_condition_only_request_without_binding(capsys):
    assert (
        producer_main(
            [
                "--vocabulary",
                str(ROOT / "config/document_interface.json"),
                "why-input",
                str(EXAMPLE / "publication.json"),
                "requested",
                "--backend",
                "document-blocks",
                "--requirements",
                str(EXAMPLE / "publication_requirements_v4.json"),
                "--include-condition-inputs",
            ]
        )
        == 0
    )
    result = json.loads(capsys.readouterr().out)
    assert result["role"] == "condition"
    assert result["computation_outputs"] == []
    assert result["conditions"][0]["id"] == "title_matches"
    assert result["execution"] == "not performed"
