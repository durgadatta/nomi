"""An independent consumer checks pinned vocabulary, source and derivation."""

import ast
from copy import deepcopy
import inspect
import json
from pathlib import Path

import pytest

from tools.object_interface import Graph, load_document
from tools.object_interface.examples import lab_vocabulary
from tools import object_replay

ROOT = Path(__file__).resolve().parents[4]


def evidence():
    vocabulary = lab_vocabulary()
    source = load_document(ROOT / "docs/research/object_framework/composition.json")
    graph = Graph.from_document(source, vocabulary)
    return vocabulary.document, source, graph.compare("squared", "expanded_square")


def test_separate_consumer_reconstructs_composition_without_planner(monkeypatch):
    vocabulary, source, receipt = evidence()

    def forbidden(*args, **kwargs):
        raise AssertionError("planner invoked by independent consumer")

    monkeypatch.setattr(Graph, "from_document", forbidden)
    monkeypatch.setattr(Graph, "compare", forbidden)
    assert (
        object_replay.replay(vocabulary, source, receipt)["independent_checker"] is True
    )


def test_consumer_imports_only_standard_library():
    module = ast.parse(inspect.getsource(object_replay))
    roots = set()
    for node in ast.walk(module):
        if isinstance(node, ast.Import):
            roots.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            roots.add(node.module.split(".")[0])
    assert roots <= {"argparse", "hashlib", "json", "pathlib", "re", "sys"}


@pytest.mark.parametrize(
    "left,right",
    [
        ("published", "greeting"),
        ("quantity", "quantity"),
        ("squared", "expanded_square"),
    ],
)
def test_independent_alias_input_and_definition_evidence(left, right):
    vocabulary, source, _ = evidence()
    receipt = Graph.from_document(source, lab_vocabulary()).compare(left, right)
    assert object_replay.replay(vocabulary, source, receipt)["status"] == "verified"


@pytest.mark.parametrize(
    "mutation",
    [
        lambda r: r.update(context="forged"),
        lambda r: r.update(version=True),
        lambda r: r.update(status="unknown"),
        lambda r: r.update(right="quantity"),
        lambda r: r.update(vocabulary="unreviewed"),
        lambda r: r.update(basis="arbitrary algebra"),
        lambda r: r.update(extra="trusted"),
        lambda r: r["normal_forms"][0]["terms"][0].update(identity="other_input"),
        lambda r: r["normal_forms"][0]["terms"][-1]["ports"].update(right=[0, 0]),
    ],
)
def test_changed_receipt_is_refused(mutation):
    vocabulary, source, receipt = evidence()
    mutation(receipt)
    with pytest.raises(object_replay.ReplayError):
        object_replay.replay(vocabulary, source, receipt)


@pytest.mark.parametrize(
    "mutation",
    [
        lambda g: g.update(version=True),
        lambda g: g.update(outputs=["missing"]),
        lambda g: g["objects"].append(deepcopy(g["objects"][0])),
        lambda g: g["objects"][0].update(op="unreviewed"),
        lambda g: g["objects"][1]["ports"].update(value="name"),
        lambda g: g["objects"][1]["ports"].update(value="missing"),
        lambda g: g["objects"][1]["ports"].update(value="doubled"),
        lambda g: g["objects"][4]["attributes"].update(value=True),
        lambda g: g["objects"][4]["attributes"].update(value="new context"),
        lambda g: g["objects"][0]["attributes"].update(engine="hidden engine"),
    ],
)
def test_whole_graph_is_rechecked_even_outside_comparison_ancestry(mutation):
    vocabulary, source, receipt = evidence()
    mutation(source)
    with pytest.raises(object_replay.ReplayError):
        object_replay.replay(vocabulary, source, receipt)


def test_new_vocabulary_requires_independent_admission():
    vocabulary, source, receipt = evidence()
    vocabulary["operations"]["exact.square"]["definition"]["objects"][0]["op"] = (
        "exact.add"
    )
    with pytest.raises(object_replay.ReplayError, match="does not admit"):
        object_replay.replay(vocabulary, source, receipt)


def test_cli_replays_exported_receipt_and_refuses_malformed_json(tmp_path, capsys):
    vocabulary, source, receipt = evidence()
    paths = []
    for filename, document in (
        ("vocabulary", vocabulary),
        ("graph", source),
        ("receipt", receipt),
    ):
        path = tmp_path / (filename + ".json")
        path.write_text(json.dumps(document))
        paths.append(str(path))
    assert object_replay.main(paths) == 0
    assert '"independent_checker": true' in capsys.readouterr().out
    Path(paths[-1]).write_text('{"status":"equivalent","status":"unknown"}')
    assert object_replay.main(paths) == 2
    assert '"refused"' in capsys.readouterr().err
