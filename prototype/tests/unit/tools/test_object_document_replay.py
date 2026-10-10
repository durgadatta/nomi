"""Independent admission of a richer shape never upgrades pending evidence."""

import copy
from pathlib import Path
import subprocess
import sys

import pytest

from tools.object_interface import Graph, Requirements, load_document
from tools.object_interface.documentary import document_vocabulary
from tools.object_replay import ReplayError, replay, replay_requirements

ROOT = Path(__file__).resolve().parents[4]
EXAMPLE = ROOT / "docs/research/object_framework"


def artifacts():
    vocabulary = document_vocabulary()
    graph = Graph.from_document(load_document(EXAMPLE / "document.json"), vocabulary)
    requirements = Requirements.from_document(
        load_document(EXAMPLE / "document_requirements.json"), graph
    )
    return vocabulary, graph, requirements


@pytest.mark.parametrize(
    "bindings,verdict",
    [
        (None, "pending"),
        ({"draft": {"title": "", "sections": []}}, "refuted"),
        (load_document(EXAMPLE / "document_bindings.json"), "satisfied"),
    ],
)
def test_documentary_predicate_receipts_replay_without_upgrading_verdict(
    bindings, verdict
):
    vocabulary, graph, requirements = artifacts()
    receipt = requirements.check(bindings)
    result = replay_requirements(
        vocabulary.document, graph.document, requirements.document, receipt, bindings
    )
    assert result["verdict"] == verdict
    assert result["independent_checker"] is True


def test_documentary_alias_comparison_replays_separately_from_rendering():
    vocabulary, graph, _ = artifacts()
    result = replay(
        vocabulary.document, graph.document, graph.compare("content", "published")
    )
    assert result["status"] == "verified"
    assert result["vocabulary"] == vocabulary.fingerprint


@pytest.mark.parametrize(
    "field,value",
    [
        ("status", "satisfied"),
        ("version", 1),
        ("evidence_phase", "binding"),
        ("binding_digest", "claimed"),
        ("scope", "all headings are nonempty"),
    ],
)
def test_forged_documentary_evidence_is_refused(field, value):
    vocabulary, graph, requirements = artifacts()
    receipt = requirements.check()
    receipt[field] = value
    with pytest.raises(ReplayError):
        replay_requirements(
            vocabulary.document, graph.document, requirements.document, receipt
        )


@pytest.mark.parametrize(
    "path,rule",
    [
        (["missing"], "text.nonempty-v1"),
        (["sections", True, "heading"], "text.nonempty-v1"),
        (["sections", -1, "heading"], "text.nonempty-v1"),
        (["sections", 1_000_001, "heading"], "text.nonempty-v1"),
        (["title"], "array.nonempty-v1"),
        (["title"], "all.nonempty-v1"),
    ],
)
def test_independent_consumer_refuses_invalid_paths_and_unadmitted_rules(path, rule):
    vocabulary, graph, requirements = artifacts()
    document = requirements.document
    document["requirements"][0].update(path=path, rule=rule)
    with pytest.raises(ReplayError):
        replay_requirements(
            vocabulary.document, graph.document, document, requirements.check()
        )


def test_changed_contracts_and_invalid_unselected_nodes_cannot_hide_behind_receipts():
    vocabulary, graph, _ = artifacts()
    receipt = graph.compare("content", "published")
    changed = vocabulary.document
    changed["types"]["DocumentSpec"]["value"]["fields"]["title"] = {"kind": "int"}
    with pytest.raises(ReplayError, match="does not admit"):
        replay(changed, graph.document, receipt)
    changed = graph.document
    changed["objects"][1]["ports"]["spec"] = "content"
    with pytest.raises(ReplayError, match="incompatible nominal"):
        replay(vocabulary.document, changed, receipt)


def test_deep_binding_shape_and_claimed_computed_values_are_not_evidence():
    vocabulary, graph, requirements = artifacts()
    bindings = load_document(EXAMPLE / "document_bindings.json")
    receipt = requirements.check(bindings)
    changed = copy.deepcopy(bindings)
    changed["draft"]["sections"][0]["paragraphs"][0] = False
    for invalid in (changed, {"title": "Research plan"}):
        with pytest.raises(ReplayError):
            replay_requirements(
                vocabulary.document,
                graph.document,
                requirements.document,
                receipt,
                invalid,
            )
    document = requirements.document
    document["requirements"] = [
        {"id": "computed", "subject": "title", "path": [], "rule": "text.nonempty-v1"}
    ]
    computed = Requirements.from_document(document, graph)
    assert (
        replay_requirements(
            vocabulary.document,
            graph.document,
            document,
            computed.check(bindings),
            bindings,
        )["verdict"]
        == "pending"
    )


def test_nested_literal_alias_has_independent_static_evidence():
    vocabulary, graph, _ = artifacts()
    graph = graph.compose(
        "literal",
        "document.spec.literal",
        {},
        {"value": {"title": " ", "sections": []}},
    )
    graph = graph.compose(
        "aliased", "document.spec.alias", {"target": graph.ref("literal")}
    )
    document = {
        "version": 2,
        "graph": graph.context,
        "owner": "test",
        "revision": "v1",
        "requirements": [
            {
                "id": "content",
                "subject": "aliased",
                "path": ["title"],
                "rule": "text.nonempty-v1",
            },
        ],
    }
    requirements = Requirements.from_document(document, graph)
    assert (
        replay_requirements(
            vocabulary.document, graph.document, document, requirements.check()
        )["verdict"]
        == "satisfied"
    )


def test_replay_runs_in_a_process_that_cannot_import_the_producer(tmp_path):
    _, graph, requirements = artifacts()
    # Invoke the independently executable file while actively refusing imports
    # from producer/checker/backend packages rather than relying on test imports.
    receipt = tmp_path / "receipt.json"
    import json

    receipt.write_text(json.dumps(requirements.check()))
    script = """
import importlib.abc, runpy, sys
class DenyProducer(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if fullname.startswith(('tools', 'prototype')):
            raise RuntimeError('producer import attempted')
sys.meta_path.insert(0, DenyProducer())
sys.argv = sys.argv[1:]
runpy.run_path(sys.argv[0], run_name='__main__')
"""
    result = subprocess.run(
        [
            sys.executable,
            "-I",
            "-c",
            script,
            str(ROOT / "tools/object_replay.py"),
            str(ROOT / "config/document_interface.json"),
            str(EXAMPLE / "document.json"),
            str(receipt),
            "--requirements",
            str(EXAMPLE / "document_requirements.json"),
        ],
        capture_output=True,
        text=True,
        check=False,
        cwd=tmp_path,
    )
    assert result.returncode == 0, result.stderr
    assert '"verdict": "pending"' in result.stdout
    assert graph.context in result.stdout
