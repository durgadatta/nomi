"""Predicate evidence has an independent consumer and an unchanged verdict."""

from pathlib import Path
import json

import pytest

from tools.object_interface import Graph, Requirements, load_document
from tools.object_interface.examples import lab_vocabulary
from tools import object_replay

ROOT = Path(__file__).resolve().parents[4]
EXAMPLE = ROOT / "docs/research/object_framework"


def evidence(bindings=None):
    vocabulary = lab_vocabulary()
    source = load_document(EXAMPLE / "composition.json")
    graph = Graph.from_document(source, vocabulary)
    requirements = Requirements.from_document(
        load_document(EXAMPLE / "requirements.json"), graph
    )
    return (
        vocabulary.document,
        source,
        requirements.document,
        requirements.check(bindings),
    )


@pytest.mark.parametrize(
    "bindings,verdict",
    [
        (None, "pending"),
        ({}, "pending"),
        ({"quantity": 3}, "pending"),
        ({"quantity": 3, "name": "Ada"}, "satisfied"),
        ({"quantity": -3, "name": "Ada"}, "refuted"),
        ({"quantity": 3, "name": ""}, "refuted"),
    ],
)
def test_independent_replay_preserves_pending_satisfied_and_refuted_states(
    bindings, verdict
):
    assert (
        object_replay.replay_requirements(*evidence(bindings), bindings)["verdict"]
        == verdict
    )


def test_replay_does_not_call_planner_or_predicate_producer(monkeypatch):
    artifacts = evidence({"quantity": 3, "name": "Ada"})

    def forbidden(*args, **kwargs):
        raise AssertionError("producer was called")

    monkeypatch.setattr(Graph, "from_document", forbidden)
    monkeypatch.setattr(Requirements, "check", forbidden)
    assert (
        object_replay.replay_requirements(*artifacts, {"quantity": 3, "name": "Ada"})[
            "independent_checker"
        ]
        is True
    )


@pytest.mark.parametrize(
    "mutation",
    [
        lambda r: r.update(status="satisfied"),
        lambda r: r.update(binding_digest="forged"),
        lambda r: r.update(evidence_phase="binding"),
        lambda r: r.update(version=True),
        lambda r: r["requirements"][0].update(status="satisfied"),
        lambda r: r["requirements"][0].update(basis="user assertion"),
    ],
)
def test_pending_evidence_cannot_be_upgraded_or_forged(mutation):
    vocabulary, graph, requirements, receipt = evidence()
    mutation(receipt)
    with pytest.raises(object_replay.ReplayError):
        object_replay.replay_requirements(vocabulary, graph, requirements, receipt)


@pytest.mark.parametrize(
    "mutation",
    [
        lambda r: r.update(graph="stale"),
        lambda r: r["requirements"][0].update(rule="user-says-true"),
        lambda r: r["requirements"][0].update(subject="name"),
        lambda r: r["requirements"][0].update(status="satisfied"),
        lambda r: r.update(version=True),
    ],
)
def test_changed_requirement_definition_is_refused(mutation):
    vocabulary, graph, requirements, receipt = evidence()
    mutation(requirements)
    with pytest.raises(object_replay.ReplayError):
        object_replay.replay_requirements(vocabulary, graph, requirements, receipt)


@pytest.mark.parametrize(
    "bindings", [{"quantity": True}, {"name": 3}, {"squared": 9}, {"other": 3}]
)
def test_bad_binding_evidence_cannot_bypass_independent_types_or_source_identity(
    bindings,
):
    with pytest.raises(object_replay.ReplayError):
        object_replay.replay_requirements(*evidence(), bindings)


def test_alias_literal_evidence_and_computed_subject_remain_distinct():
    vocabulary = lab_vocabulary()
    graph = Graph.from_document(load_document(EXAMPLE / "composition.json"), vocabulary)
    literal = graph.compose("literal", "exact.literal", {}, {"value": 1})
    alias = literal.compose("alias", "exact.alias", {"target": literal.ref("literal")})
    for subject, expected in (("alias", "satisfied"), ("squared", "pending")):
        requirements = Requirements.from_document(
            {
                "version": 1,
                "graph": alias.context,
                "owner": "test",
                "revision": "v1",
                "requirements": [
                    {"id": "condition", "rule": "exact.positive-v1", "subject": subject}
                ],
            },
            alias,
        )
        verdict = object_replay.replay_requirements(
            vocabulary.document,
            alias.document,
            requirements.document,
            requirements.check(),
        )
        assert verdict["verdict"] == expected


def test_cli_requirement_replay_and_unscoped_binding_refusal(tmp_path, capsys):
    vocabulary, graph, requirements, receipt = evidence({"quantity": 3, "name": "Ada"})
    paths = {}
    for identity, value in (
        ("vocabulary", vocabulary),
        ("graph", graph),
        ("requirements", requirements),
        ("receipt", receipt),
        ("bindings", {"quantity": 3, "name": "Ada"}),
    ):
        path = tmp_path / (identity + ".json")
        path.write_text(json.dumps(value))
        paths[identity] = str(path)
    args = [
        paths["vocabulary"],
        paths["graph"],
        paths["receipt"],
        "--bindings",
        paths["bindings"],
    ]
    assert object_replay.main(args + ["--requirements", paths["requirements"]]) == 0
    assert '"verdict": "satisfied"' in capsys.readouterr().out
    assert object_replay.main(args) == 2
