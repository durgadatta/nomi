"""Workflow expansion and condition carry-forward need their own passive proof."""

import json
from pathlib import Path
import subprocess
import sys

import pytest

from tools.object_interface import Graph, Workflow, load_document
from tools.object_interface.documentary import document_vocabulary
from tools.object_interface.examples import lab_vocabulary
from tools.object_replay import ReplayError, main, replay_workflows

ROOT = Path(__file__).resolve().parents[4]
EXAMPLE = ROOT / "docs/research/object_framework"


def artifacts():
    vocabulary = lab_vocabulary()
    base = Graph.from_document(load_document(EXAMPLE / "composition.json"), vocabulary)
    base = base.compose("other_quantity", "exact.input", {})
    base = base.compose("other_name", "text.input", {})
    template = Workflow.from_document(
        load_document(EXAMPLE / "workflow.json"), vocabulary
    )
    first = template.compose(
        base, "first", {"quantity": base.ref("quantity"), "name": base.ref("name")}
    )
    second = template.compose(
        first,
        "second",
        {
            "quantity": first.graph.ref("other_quantity"),
            "name": first.graph.ref("other_name"),
        },
    )
    return vocabulary.document, base.document, [template.document], second.document


def test_independent_substitution_preserves_both_instances_and_pending_conditions():
    vocabulary, base, templates, receipt = artifacts()
    result = replay_workflows(vocabulary, base, templates, receipt)
    assert result["status"] == "verified"
    assert result["components"] == 2
    assert result["verdict"] == "pending"
    assert result["independent_checker"] is True
    assert len(receipt["requirements"]["requirements"]) == 4


@pytest.mark.parametrize(
    "mutation",
    [
        lambda r: r["requirements"]["requirements"].pop(0),
        lambda r: r["requirements"].update(owner="approved"),
        lambda r: r["inspection"]["requirements"].update(status="satisfied"),
        lambda r: r["inspection"].update(realization="complete"),
        lambda r: r["inspection"]["outputs"].update(square="first.squared"),
        lambda r: r["inspection"]["components"][0]["requirement_source"].update(
            owner="trusted"
        ),
        lambda r: r["inspection"]["components"][0].update(revision="v2"),
        lambda r: r["inspection"]["components"][0]["outputs"].update(
            square="first.doubled"
        ),
        lambda r: r["inspection"]["components"][1].update(namespace="first"),
        lambda r: r["inspection"]["components"][1]["inputs"].update(
            quantity="first.published"
        ),
        lambda r: r["inspection"]["components"][1]["inputs"].update(
            quantity="future.input"
        ),
        lambda r: r["inspection"]["components"][1].update(
            workflow="unprovided-definition"
        ),
    ],
)
def test_forged_workflow_and_condition_claims_are_refused(mutation):
    vocabulary, base, templates, receipt = artifacts()
    mutation(receipt)
    with pytest.raises(ReplayError):
        replay_workflows(vocabulary, base, templates, receipt)


def test_valid_expanded_graph_is_insufficient_if_substitution_is_wrong():
    vocabulary, base, templates, receipt = artifacts()
    for obj in receipt["graph"]["objects"]:
        if obj["id"] == "second.expanded_square":
            obj["ports"]["left"] = "quantity"
    # The altered graph is still a legal ExactInt computation, but it does not
    # implement the supplied second workflow instantiation.
    Graph.from_document(receipt["graph"], lab_vocabulary())
    with pytest.raises(ReplayError, match="independent substitution"):
        replay_workflows(vocabulary, base, templates, receipt)


@pytest.mark.parametrize(
    "mutation",
    [
        lambda t: t.update(version=True),
        lambda t: t.update(inputs={"quantity": "quantity"}),
        lambda t: t.update(outputs={"square": "quantity"}),
        lambda t: t["requirements"].update(graph="stale"),
        lambda t: t["graph"]["objects"][0].update(op="new.trusted-law"),
    ],
)
def test_unchecked_source_templates_cannot_install_semantics(mutation):
    vocabulary, base, templates, receipt = artifacts()
    mutation(templates[0])
    with pytest.raises(ReplayError):
        replay_workflows(vocabulary, base, templates, receipt)


def test_explicitly_shared_arguments_and_requirement_free_definitions_replay():
    vocabulary = lab_vocabulary()
    base = Graph.from_document(load_document(EXAMPLE / "composition.json"), vocabulary)
    document = load_document(EXAMPLE / "workflow.json")
    document["requirements"] = None
    template = Workflow.from_document(document, vocabulary)
    first = template.compose(
        base, "first", {"quantity": base.ref("quantity"), "name": base.ref("name")}
    )
    second = template.compose(
        first,
        "second",
        {"quantity": first.graph.ref("quantity"), "name": first.graph.ref("name")},
    )
    result = replay_workflows(
        vocabulary.document, base.document, [template.document], second.document
    )
    assert result["verdict"] is None
    assert (
        second.graph.compare("first.squared", "second.squared")["status"]
        == "equivalent"
    )


def test_documentary_template_paths_replay_without_a_renderer():
    vocabulary = document_vocabulary()
    base = Graph.from_document(load_document(EXAMPLE / "document.json"), vocabulary)
    template = Workflow.from_document(
        {
            "version": 1,
            "id": "document",
            "revision": "v1",
            "graph": base.document,
            "inputs": {"draft": "draft"},
            "outputs": {"content": "published", "count": "paragraph_count"},
            "requirements": load_document(EXAMPLE / "document_requirements.json"),
        },
        vocabulary,
    )
    instance = template.compose(base, "copy", {"draft": base.ref("draft")})
    assert (
        replay_workflows(
            vocabulary.document, base.document, [template.document], instance.document
        )["verdict"]
        == "pending"
    )


def test_bounded_explicit_definitions_and_unambiguous_cli_modes(tmp_path, capsys):
    vocabulary, base, templates, receipt = artifacts()
    for invalid in ([], templates + templates):
        with pytest.raises(ReplayError):
            replay_workflows(vocabulary, base, invalid, receipt)
    args = []
    for name, value in (
        ("vocabulary", vocabulary),
        ("base", base),
        ("receipt", receipt),
    ):
        path = tmp_path / (name + ".json")
        path.write_text(json.dumps(value))
        args.append(str(path))
    assert main(args + ["--workflow", str(EXAMPLE / "workflow.json")]) == 0
    assert '"verified"' in capsys.readouterr().out
    assert (
        main(
            args
            + [
                "--workflow",
                str(EXAMPLE / "workflow.json"),
                "--bindings",
                "ignored.json",
            ]
        )
        == 2
    )
    assert "separate from binding" in capsys.readouterr().err


def test_workflow_replay_runs_without_any_producer_imports(tmp_path):
    vocabulary, base, templates, receipt = artifacts()
    paths = []
    for name, value in (
        ("vocabulary", vocabulary),
        ("base", base),
        ("receipt", receipt),
        ("workflow", templates[0]),
    ):
        path = tmp_path / (name + ".json")
        path.write_text(json.dumps(value))
        paths.append(str(path))
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
            *paths[:3],
            "--workflow",
            paths[3],
        ],
        capture_output=True,
        text=True,
        check=False,
        cwd=tmp_path,
    )
    assert result.returncode == 0, result.stderr
    assert '"verdict": "pending"' in result.stdout
