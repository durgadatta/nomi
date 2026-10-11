"""Named repairs are atomic context-qualified descriptions, never executions."""

from copy import deepcopy
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
    load_document,
)
from tools.object_interface.__main__ import main as producer_main
from tools.object_interface.documents import MAX_BYTES, encode
from tools.object_interface.examples import lab_vocabulary, python_backend
from tools.object_interface.documentary import document_vocabulary
from tools.object_replay import ReplayError, main, replay, replay_revision

ROOT = Path(__file__).resolve().parents[4]
EXAMPLE = ROOT / "docs/research/object_framework"


def artifacts():
    vocabulary = lab_vocabulary()
    base = Graph.from_document(load_document(EXAMPLE / "composition.json"), vocabulary)
    revision = Revision.from_document(
        load_document(EXAMPLE / "greeting_revision.json"), base
    )
    return vocabulary, base, revision


def test_named_repair_changes_one_revision_and_preserves_original_plan_and_outputs():
    vocabulary, base, revision = artifacts()
    revised = revision.graph
    assert base.inspect("prefix")["attributes"]["value"] == "Hello, "
    assert revised.inspect("prefix")["attributes"]["value"] == "Welcome, "
    assert revised.document["outputs"] == base.document["outputs"]
    assert revision.inspect()["changed_objects"] == ["prefix"]
    assert revision.inspect()["realization"] == "unbound"
    assert revised.context != base.context
    for graph, expected in [(base, "Hello, Ada"), (revised, "Welcome, Ada")]:
        result = (
            python_backend(vocabulary)
            .compile(graph, [graph.ref("published")])
            .bind({"name": "Ada"})
            .execute()
        )
        assert result.values == {"published": expected}
    assert (
        replay_revision(
            vocabulary.document, base.document, revision.document, revision.receipt
        )["status"]
        == "verified"
    )


def test_repair_invalidates_old_evidence_and_handles_without_migrating_conditions():
    vocabulary, base, revision = artifacts()
    receipt = base.compare("squared", "expanded_square")
    with pytest.raises(ContractError, match="does not replay"):
        revision.graph.verify(receipt)
    with pytest.raises(ReplayError):
        replay(vocabulary.document, revision.graph.document, receipt)
    with pytest.raises(ContractError, match="exact graph revision"):
        python_backend(vocabulary).compile(revision.graph, [base.ref("published")])
    with pytest.raises(ContractError, match="different graph context"):
        Requirements.from_document(
            load_document(EXAMPLE / "requirements.json"), revision.graph
        )
    assert revision.inspect()["contracts"] == "not migrated"


def test_atomic_replacements_admit_a_coherent_nominal_migration_not_an_invalid_intermediate():
    vocabulary = lab_vocabulary()
    base = Graph.from_document(
        {
            "version": 1,
            "vocabulary": vocabulary.fingerprint,
            "objects": [
                {"id": "left", "op": "exact.input", "ports": {}, "attributes": {}},
                {"id": "right", "op": "exact.input", "ports": {}, "attributes": {}},
                {
                    "id": "combine",
                    "op": "exact.add",
                    "ports": {"left": "left", "right": "right"},
                    "attributes": {},
                },
            ],
            "outputs": ["combine"],
        },
        vocabulary,
    )
    changes = [
        {"id": "left", "op": "text.input", "ports": {}, "attributes": {}},
        {"id": "right", "op": "text.input", "ports": {}, "attributes": {}},
        {
            "id": "combine",
            "op": "text.concat",
            "ports": {"left": "left", "right": "right"},
            "attributes": {},
        },
    ]
    source = {"version": 1, "graph": base.context, "replacements": changes[:1]}
    with pytest.raises(ContractError, match="received Text"):
        Revision.from_document(source, base)
    source["replacements"] = changes
    revision = Revision.from_document(source, base)
    assert revision.graph.inspect("combine")["type"] == "Text"
    assert python_backend(vocabulary).compile(revision.graph).bind(
        {"left": "a", "right": "b"}
    ).execute().values == {"combine": "ab"}
    assert (
        replay_revision(vocabulary.document, base.document, source, revision.receipt)[
            "status"
        ]
        == "verified"
    )
    assert base.inspect("combine")["type"] == "ExactInt"


def test_noop_replacement_retains_source_instance_but_records_requested_objects():
    vocabulary, base, _ = artifacts()
    replacement = next(o for o in base.document["objects"] if o["id"] == "prefix")
    revision = Revision.from_document(
        {"version": 1, "graph": base.context, "replacements": [replacement]}, base
    )
    assert revision.graph is base
    assert revision.inspect()["changed_objects"] == []
    assert revision.inspect()["requested_objects"] == ["prefix"]
    assert (
        replay_revision(
            vocabulary.document, base.document, revision.document, revision.receipt
        )["status"]
        == "verified"
    )


def test_documentary_revision_replays_without_rendering_or_binding():
    vocabulary = document_vocabulary()
    base = Graph.from_document(load_document(EXAMPLE / "publication.json"), vocabulary)
    source = {
        "version": 1,
        "graph": base.context,
        "replacements": [
            {
                "id": "requested",
                "op": "text.literal",
                "ports": {},
                "attributes": {"value": "Research plan"},
            },
        ],
    }
    revision = Revision.from_document(source, base)
    assert revision.graph.inspect("requested")["role"] == "literal"
    assert revision.inspect()["realization"] == "unbound"
    assert (
        replay_revision(vocabulary.document, base.document, source, revision.receipt)[
            "status"
        ]
        == "verified"
    )
    with pytest.raises(ContractError, match="different graph context"):
        Requirements.from_document(
            load_document(EXAMPLE / "publication_requirements_v4.json"), revision.graph
        )


def test_atomic_request_order_does_not_change_preserved_object_order():
    vocabulary, base, _ = artifacts()
    original = base.document
    replacements = [
        deepcopy(next(o for o in original["objects"] if o["id"] == identity))
        for identity in ("prefix", "name")
    ]
    replacements[0]["attributes"]["value"] = "Goodbye, "
    replacements[1].update(op="text.literal", attributes={"value": "Ada"})
    original_order = [o["id"] for o in original["objects"]]
    source = {
        "version": 1,
        "graph": base.context,
        "replacements": list(reversed(replacements)),
    }
    revision = Revision.from_document(source, base)
    assert [o["id"] for o in revision.graph.document["objects"]] == original_order
    assert revision.inspect()["requested_objects"] == ["name", "prefix"]
    assert revision.inspect()["changed_objects"] == [
        i for i in original_order if i in ("prefix", "name")
    ]
    assert (
        replay_revision(vocabulary.document, base.document, source, revision.receipt)[
            "status"
        ]
        == "verified"
    )


def test_detached_revision_exports_and_literal_strings_do_not_rewire_references():
    vocabulary, base, revision = artifacts()
    source = revision.document
    source["replacements"][0]["attributes"]["value"] = "quantity"
    edited = Revision.from_document(source, base)
    assert edited.graph.inspect("prefix")["attributes"]["value"] == "quantity"
    source["replacements"].clear()
    exported = edited.receipt
    exported["graph"]["objects"].clear()
    assert edited.graph.inspect("prefix")["attributes"]["value"] == "quantity"
    with pytest.raises(AttributeError):
        edited._graph = base
    with pytest.raises(AttributeError):
        del edited._document


@pytest.mark.parametrize(
    "mutate",
    [
        lambda d: d.update(version=True),
        lambda d: d.update(graph="stale"),
        lambda d: d.update(replacements=[]),
        lambda d: d.update(outputs=["prefix"]),
        lambda d: d["replacements"].append(d["replacements"][0]),
        lambda d: d["replacements"][0].update(id="not_present"),
        lambda d: d["replacements"][0].update(op="unknown.operation"),
        lambda d: d["replacements"][0].update(attributes={"value": True}),
        lambda d: d["replacements"][0].update(ports={"callback": "name"}),
        lambda d: d["replacements"][0].update(type="Text"),
    ],
)
def test_revision_admission_refuses_stale_unknown_and_unscoped_changes(mutate):
    vocabulary, base, revision = artifacts()
    document = revision.document
    mutate(document)
    with pytest.raises(ContractError):
        Revision.from_document(document, base)
    with pytest.raises(ReplayError):
        replay_revision(vocabulary.document, base.document, document, revision.receipt)


def test_revision_rechecks_disconnected_objects_and_cycles_atomically():
    vocabulary, base, revision = artifacts()
    document = revision.document
    document["replacements"] = [
        {
            "id": "quantity",
            "op": "exact.double",
            "ports": {"value": "doubled"},
            "attributes": {},
        }
    ]
    with pytest.raises(ContractError, match="cyclic"):
        Revision.from_document(document, base)
    with pytest.raises(ReplayError):
        replay_revision(vocabulary.document, base.document, document, revision.receipt)
    disconnected = next(o for o in base.document["objects"] if o["id"] == "document")
    disconnected["ports"]["body"] = "missing"
    document["replacements"] = [disconnected]
    with pytest.raises(ContractError, match="unknown references"):
        Revision.from_document(document, base)


@pytest.mark.parametrize(
    "mutate",
    [
        lambda r: r.update(revision="forged"),
        lambda r: r["inspection"].update(changed_objects=[]),
        lambda r: r["inspection"].update(source="forged"),
        lambda r: r["inspection"].update(contracts="migrated"),
        lambda r: r["inspection"].update(realization="completed"),
        lambda r: r["graph"].update(outputs=["prefix"]),
        lambda r: r["graph"]["objects"].pop(),
        lambda r: r["graph"]["objects"][0]["attributes"].update(extra="hidden change"),
    ],
)
def test_independent_replay_refuses_hidden_changes_and_forged_revision_evidence(mutate):
    vocabulary, base, revision = artifacts()
    receipt = revision.receipt
    mutate(receipt)
    with pytest.raises(ReplayError):
        replay_revision(vocabulary.document, base.document, revision.document, receipt)


def test_duplicate_replacements_and_edited_outputs_cannot_hide_in_a_revision():
    vocabulary, base, revision = artifacts()
    document = revision.document
    document["replacements"] *= 513
    with pytest.raises(ContractError, match="bounded nonempty"):
        Revision.from_document(document, base)
    with pytest.raises(ReplayError, match="replacement count"):
        replay_revision(vocabulary.document, base.document, document, revision.receipt)


def test_receipt_budget_is_checked_as_a_whole():
    _, base, revision = artifacts()
    raw = base.document
    next(o for o in raw["objects"] if o["id"] == "prefix")["attributes"]["value"] = ""
    overhead = len(encode(raw).encode())
    replacement = deepcopy(revision.document["replacements"][0])
    replacement["attributes"]["value"] = "x" * (MAX_BYTES - overhead - 20)
    edited = Revision.from_document(
        {"version": 1, "graph": base.context, "replacements": [replacement]}, base
    )
    assert edited.graph.context != base.context
    with pytest.raises(ContractError, match="byte budget"):
        edited.receipt


@pytest.mark.parametrize("extra", ["--bindings", "--workflow", "--requirements"])
def test_revision_consumer_refuses_unrelated_mode_arguments(extra, tmp_path, capsys):
    _, _, revision = artifacts()
    receipt = tmp_path / "receipt.json"
    receipt.write_text(json.dumps(revision.receipt))
    assert (
        main(
            [
                str(ROOT / "config/object_interface.json"),
                str(EXAMPLE / "composition.json"),
                str(receipt),
                "--revision",
                str(EXAMPLE / "greeting_revision.json"),
                extra,
                "unrelated.json",
            ]
        )
        == 2
    )
    assert "separate" in capsys.readouterr().err


def test_revision_cli_receipt_replays_in_an_isolated_consumer(tmp_path, capsys):
    assert (
        producer_main(
            [
                "revise",
                str(EXAMPLE / "composition.json"),
                str(EXAMPLE / "greeting_revision.json"),
            ]
        )
        == 0
    )
    receipt = tmp_path / "receipt.json"
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
            "--revision",
            str(EXAMPLE / "greeting_revision.json"),
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout)["independent_checker"] is True
