"""Universal evidence and workflow promotion have a separately reviewed checker."""

from copy import deepcopy
import json
from pathlib import Path
import subprocess
import sys

import pytest

from tools.object_interface import Graph, Requirements, Workflow, load_document
from tools.object_interface.__main__ import main as producer_main
from tools.object_interface.documentary import document_vocabulary
from tools.object_replay import ReplayError, replay_requirements, replay_workflows

ROOT = Path(__file__).resolve().parents[4]
EXAMPLE = ROOT / "docs/research/object_framework"


def artifacts():
    vocabulary = document_vocabulary()
    graph = Graph.from_document(load_document(EXAMPLE / "publication.json"), vocabulary)
    required = Requirements.from_document(
        load_document(EXAMPLE / "publication_requirements_v4.json"), graph
    )
    return vocabulary, graph, required


def only_every(required, **updates):
    document = required.document
    document["requirements"] = [deepcopy(document["requirements"][2])]
    document["requirements"][0]["condition"].update(updates)
    return Requirements.from_document(document, required._graph)


@pytest.mark.parametrize(
    "headings,status",
    [([], "satisfied"), (["A", "B"], "satisfied"), (["", "B", ""], "refuted")],
)
def test_independent_finite_universal_truth_and_counterexample_paths(headings, status):
    vocabulary, graph, required = artifacts()
    required = only_every(required)
    bindings = {
        "draft": {
            "title": "A",
            "sections": [{"heading": h, "paragraphs": []} for h in headings],
        }
    }
    result = replay_requirements(
        vocabulary.document,
        graph.document,
        required.document,
        required.check(bindings),
        bindings,
    )
    assert result["verdict"] == status
    assert result["independent_checker"] is True
    assert (
        replay_requirements(
            vocabulary.document, graph.document, required.document, required.check()
        )["verdict"]
        == "pending"
    )


@pytest.mark.parametrize(
    "updates,bindings",
    [
        (
            {"path": ["sections", 0, "paragraphs"], "item_path": []},
            {"draft": {"title": "A", "sections": []}},
        ),
        (
            {"item_path": ["paragraphs", 0]},
            {"draft": {"title": "A", "sections": [{"heading": "A", "paragraphs": []}]}},
        ),
    ],
)
def test_independent_missing_collection_and_missing_item_paths(updates, bindings):
    vocabulary, graph, required = artifacts()
    required = only_every(required, **updates)
    assert (
        replay_requirements(
            vocabulary.document,
            graph.document,
            required.document,
            required.check(bindings),
            bindings,
        )["verdict"]
        == "refuted"
    )


@pytest.mark.parametrize(
    "mutate",
    [
        lambda r: r.update(status="satisfied"),
        lambda r: r["requirements"][0]["condition"].update(checked_items=0),
        lambda r: r["requirements"][0]["condition"].update(total_items=0),
        lambda r: r["requirements"][0]["condition"].update(failures=[]),
        lambda r: r["requirements"][0]["condition"]["failures"][0].update(
            path=["sections", 1, "heading"]
        ),
        lambda r: r["requirements"][0]["condition"].update(basis="user assertion"),
        lambda r: r["requirements"][0]["condition"].update(failures_complete=False),
    ],
)
def test_independent_consumer_refuses_forged_universal_evidence(mutate):
    vocabulary, graph, required = artifacts()
    required = only_every(required)
    bindings = {
        "draft": {"title": "A", "sections": [{"heading": "", "paragraphs": []}]}
    }
    receipt = required.check(bindings)
    mutate(receipt)
    with pytest.raises(ReplayError):
        replay_requirements(
            vocabulary.document, graph.document, required.document, receipt, bindings
        )


@pytest.mark.parametrize(
    "mutate",
    [
        lambda c: c.update(kind="any"),
        lambda c: c.update(rule="callback"),
        lambda c: c.update(path=["title"]),
        lambda c: c.update(item_path=["missing"]),
        lambda c: c.update(item_path=["paragraphs", True]),
        lambda c: c.update(item_path=["paragraphs"]),
        lambda c: c.update(subject="missing"),
        lambda c: c.update(satisfied=True),
    ],
)
def test_independent_admission_checks_every_body_with_no_items_available(mutate):
    vocabulary, graph, required = artifacts()
    required = only_every(required)
    document = required.document
    mutate(document["requirements"][0]["condition"])
    bindings = {"draft": {"title": "A", "sections": []}}
    with pytest.raises(ReplayError):
        replay_requirements(
            vocabulary.document,
            graph.document,
            document,
            required.check(bindings),
            bindings,
        )


def test_independent_failure_projection_and_shared_capacity_are_bounded():
    vocabulary, graph, required = artifacts()
    required = only_every(required)
    bindings = {
        "draft": {"title": "A", "sections": [{"heading": "", "paragraphs": []}] * 129}
    }
    assert (
        replay_requirements(
            vocabulary.document,
            graph.document,
            required.document,
            required.check(bindings),
            bindings,
        )["verdict"]
        == "refuted"
    )
    bindings["draft"]["sections"] = [{"heading": "A", "paragraphs": []}] * 4096
    receipt = required.check(bindings)
    assert (
        replay_requirements(
            vocabulary.document, graph.document, required.document, receipt, bindings
        )["verdict"]
        == "satisfied"
    )
    bindings["draft"]["sections"].append({"heading": "A", "paragraphs": []})
    with pytest.raises(ReplayError, match="item-check budget"):
        replay_requirements(
            vocabulary.document, graph.document, required.document, receipt, bindings
        )
    doubled = required.document
    doubled["requirements"].append(
        {**deepcopy(doubled["requirements"][0]), "id": "again"}
    )
    bindings["draft"]["sections"] = bindings["draft"]["sections"][:2049]
    with pytest.raises(ReplayError, match="item-check budget"):
        replay_requirements(
            vocabulary.document, graph.document, doubled, receipt, bindings
        )


@pytest.mark.parametrize("reverse", [False, True])
def test_independent_workflow_rewires_every_subject_and_promotes_relations(reverse):
    vocabulary, graph, required = artifacts()
    template = {
        "version": 1,
        "id": "publication",
        "revision": "v1",
        "graph": graph.document,
        "inputs": {"draft": "draft", "request": "requested"},
        "outputs": {"text": "published", "count": "paragraph_count"},
        "requirements": required.document,
    }
    old = {
        **deepcopy(template),
        "id": "title-only",
        "requirements": load_document(EXAMPLE / "publication_requirements.json"),
    }
    templates = [
        Workflow.from_document(d, vocabulary)
        for d in ([old, template] if reverse else [template, old])
    ]
    base = graph.compose("second_draft", "document.spec.input", {})
    base = base.compose("second_request", "text.input", {})
    first = templates[0].compose(
        base, "first", {"draft": base.ref("draft"), "request": base.ref("requested")}
    )
    second = templates[1].compose(
        first,
        "second",
        {
            "draft": first.graph.ref("second_draft"),
            "request": first.graph.ref("second_request"),
        },
    )
    definitions = [t.document for t in templates]
    result = replay_workflows(
        vocabulary.document, base.document, definitions, second.document
    )
    assert result["verdict"] == "pending"
    bundle = second.document
    universal = next(
        r
        for r in bundle["requirements"]["requirements"]
        if r["condition"]["kind"] == "every"
    )
    universal["condition"]["subject"] = "draft" if reverse else "second_draft"
    with pytest.raises(ReplayError, match="substitution"):
        replay_workflows(vocabulary.document, base.document, definitions, bundle)


def test_publication_cli_binds_all_conditions_and_passive_consumer_stays_isolated(
    tmp_path, capsys
):
    graph = str(EXAMPLE / "publication.json")
    requirements = str(EXAMPLE / "publication_requirements_v4.json")
    bindings = str(EXAMPLE / "publication_bindings.json")
    vocabulary = str(ROOT / "config/document_interface.json")
    assert (
        producer_main(
            [
                "--vocabulary",
                vocabulary,
                "run",
                graph,
                bindings,
                "--backend",
                "document-stream",
                "--requirements",
                requirements,
                "--include-condition-inputs",
            ]
        )
        == 0
    )
    result = json.loads(capsys.readouterr().out)
    assert result["receipt"]["requirement_evidence"]["version"] == 4
    assert result["values"]["paragraph_count"] == 3
    receipt = tmp_path / "receipt.json"
    receipt.write_text(json.dumps(result["receipt"]["requirement_evidence"]))
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
    checked = subprocess.run(
        [
            sys.executable,
            "-I",
            "-c",
            script,
            str(ROOT / "tools/object_replay.py"),
            vocabulary,
            graph,
            str(receipt),
            "--requirements",
            requirements,
            "--bindings",
            bindings,
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    assert checked.returncode == 0, checked.stderr
    assert json.loads(checked.stdout)["independent_checker"] is True
