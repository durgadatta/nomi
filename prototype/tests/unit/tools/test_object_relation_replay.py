"""A passive consumer separately checks operands and carried relation ownership."""

from copy import deepcopy
import json
from pathlib import Path
import subprocess
import sys

import pytest

from tools.object_interface import Graph, Requirements, Workflow, load_document
from tools.object_interface.__main__ import main as producer_main
from tools.object_interface.documentary import document_vocabulary
from tools.object_interface.examples import lab_vocabulary
from tools.object_replay import ReplayError, main, replay_requirements, replay_workflows

ROOT = Path(__file__).resolve().parents[4]
EXAMPLE = ROOT / "docs/research/object_framework"


def artifacts():
    vocabulary = lab_vocabulary()
    graph = Graph.from_document(
        load_document(EXAMPLE / "ordered_bounds.json"), vocabulary
    )
    required = Requirements.from_document(
        load_document(EXAMPLE / "ordered_bounds_requirements.json"), graph
    )
    return vocabulary, graph, required


@pytest.mark.parametrize(
    "bindings,status",
    [
        (None, "pending"),
        ({}, "pending"),
        ({"upper": 1}, "pending"),
        ({"lower": 1, "upper": 1}, "satisfied"),
        ({"lower": 2, "upper": 1}, "refuted"),
    ],
)
def test_independent_relations_reproduce_all_evidence_states(bindings, status):
    vocabulary, graph, required = artifacts()
    replayed = replay_requirements(
        vocabulary.document,
        graph.document,
        required.document,
        required.check(bindings),
        bindings,
    )
    assert replayed["verdict"] == status
    assert replayed["independent_checker"] is True


@pytest.mark.parametrize(
    "mutate",
    [
        lambda r: r.update(status="satisfied"),
        lambda r: r.update(binding_digest="forged"),
        lambda r: r["requirements"][0]["operands"][1].update(status="known"),
        lambda r: r["requirements"][0]["operands"][1].update(subject="lower"),
        lambda r: r["requirements"][0]["operands"][1].update(basis="user assertion"),
        lambda r: r["requirements"][0]["operands"].reverse(),
        lambda r: r["requirements"][0].update(rule="text.equal-v1"),
    ],
)
def test_independent_consumer_refuses_forged_relation_evidence(mutate):
    vocabulary, graph, required = artifacts()
    receipt = required.check({"lower": 2})
    mutate(receipt)
    with pytest.raises(ReplayError):
        replay_requirements(
            vocabulary.document,
            graph.document,
            required.document,
            receipt,
            {"lower": 2},
        )


@pytest.mark.parametrize(
    "mutate",
    [
        lambda r: r["requirements"][0].update(rule="user.truth"),
        lambda r: r["requirements"][0]["operands"].pop(),
        lambda r: r["requirements"][0]["operands"][0].update(path=[True]),
        lambda r: r["requirements"][0]["operands"][0].update(subject="unknown"),
        lambda r: r["requirements"][0]["operands"][0].update(status="known"),
        lambda r: r["requirements"].append(r["requirements"][0]),
    ],
)
def test_independent_admission_checks_source_instead_of_trusting_a_receipt(mutate):
    vocabulary, graph, required = artifacts()
    document = required.document
    mutate(document)
    with pytest.raises(ReplayError):
        replay_requirements(
            vocabulary.document, graph.document, document, required.check()
        )


@pytest.mark.parametrize(
    "bindings,status",
    [
        ({"draft": {"title": "", "sections": []}}, "refuted"),
        (
            {"draft": {"title": "", "sections": [{"heading": "A", "paragraphs": []}]}},
            "pending",
        ),
        (
            {
                "draft": {
                    "title": "",
                    "sections": [{"heading": "A", "paragraphs": []}],
                },
                "requested": "A",
            },
            "satisfied",
        ),
        (
            {
                "draft": {
                    "title": "",
                    "sections": [{"heading": "A", "paragraphs": []}],
                },
                "requested": "a",
            },
            "refuted",
        ),
    ],
)
def test_nested_text_operands_replay_without_loading_a_renderer(bindings, status):
    vocabulary = document_vocabulary()
    graph = Graph.from_document(load_document(EXAMPLE / "document.json"), vocabulary)
    graph = graph.compose("requested", "text.input", {})
    required = Requirements.from_document(
        {
            "version": 3,
            "graph": graph.context,
            "owner": "test.title",
            "revision": "v1",
            "requirements": [
                {
                    "id": "title",
                    "rule": "text.equal-v1",
                    "operands": [
                        {"subject": "draft", "path": ["sections", 0, "heading"]},
                        {"subject": "requested", "path": []},
                    ],
                }
            ],
        },
        graph,
    )
    assert (
        replay_requirements(
            vocabulary.document,
            graph.document,
            required.document,
            required.check(bindings),
            bindings,
        )["verdict"]
        == status
    )


@pytest.mark.parametrize("reverse", [False, True])
def test_mixed_workflow_condition_versions_replay_in_both_orders(reverse):
    vocabulary, graph, required = artifacts()
    relational = {
        "version": 1,
        "id": "ordered",
        "revision": "v1",
        "graph": graph.document,
        "inputs": {"low": "lower", "high": "upper"},
        "outputs": {"sum": "total"},
        "requirements": required.document,
    }
    legacy = deepcopy(relational)
    legacy["id"] = "positive"
    legacy["requirements"] = {
        **required.document,
        "version": 1,
        "requirements": [
            {"id": "positive", "rule": "exact.positive-v1", "subject": "lower"},
        ],
    }
    templates = [
        Workflow.from_document(document, vocabulary)
        for document in ([legacy, relational] if reverse else [relational, legacy])
    ]
    instance = templates[0].compose(
        graph, "first", {"low": graph.ref("lower"), "high": graph.ref("upper")}
    )
    instance = templates[1].compose(
        instance,
        "second",
        {"low": instance.graph.ref("lower"), "high": instance.graph.ref("upper")},
    )
    definitions = [t.document for t in templates]
    assert (
        replay_workflows(
            vocabulary.document, graph.document, definitions, instance.document
        )["verdict"]
        == "pending"
    )
    bundle = instance.document
    bundle["requirements"]["requirements"][0]["operands"][0]["subject"] = "upper"
    with pytest.raises(ReplayError, match="substitution"):
        replay_workflows(vocabulary.document, graph.document, definitions, bundle)


def test_computed_relation_operand_stays_pending_in_independent_consumer():
    vocabulary, graph, required = artifacts()
    source = required.document
    source["requirements"][0]["operands"][1]["subject"] = "total"
    required = Requirements.from_document(source, graph)
    bindings = {"lower": 1, "upper": 2}
    assert (
        replay_requirements(
            vocabulary.document,
            graph.document,
            required.document,
            required.check(bindings),
            bindings,
        )["verdict"]
        == "pending"
    )


def test_relation_cli_example_and_isolated_consumer(tmp_path, capsys):
    args = [
        "requirements",
        str(EXAMPLE / "ordered_bounds.json"),
        str(EXAMPLE / "ordered_bounds_requirements.json"),
    ]
    assert producer_main(args) == 1
    capsys.readouterr()
    assert (
        producer_main(
            args + ["--bindings", str(EXAMPLE / "ordered_bounds_bindings.json")]
        )
        == 0
    )
    receipt = tmp_path / "receipt.json"
    receipt.write_text(capsys.readouterr().out)
    consumer_args = [
        str(ROOT / "config/object_interface.json"),
        str(EXAMPLE / "ordered_bounds.json"),
        str(receipt),
        "--requirements",
        str(EXAMPLE / "ordered_bounds_requirements.json"),
        "--bindings",
        str(EXAMPLE / "ordered_bounds_bindings.json"),
    ]
    assert main(consumer_args) == 0
    assert json.loads(capsys.readouterr().out)["independent_checker"] is True
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
            *consumer_args,
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout)["verdict"] == "satisfied"
