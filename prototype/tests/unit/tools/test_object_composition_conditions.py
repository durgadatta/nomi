"""Named law obligations carry structural evidence separately from value predicates."""

from copy import deepcopy
import json
from pathlib import Path
import subprocess
import sys

import pytest

from tools.object_interface import (
    ContractError,
    Graph,
    RequirementContractError,
    Requirements,
    Revision,
    Workflow,
    load_document,
)
from tools.object_interface.__main__ import main as producer_main
from tools.object_interface.backend import Backend
from tools.object_interface.documentary import document_vocabulary
from tools.object_interface.examples import lab_vocabulary, python_backend
from tools.object_replay import ReplayError, replay_requirements, replay_workflows

ROOT = Path(__file__).resolve().parents[4]
EXAMPLE = ROOT / "docs/research/object_framework"


def graph():
    return Graph.from_document(
        load_document(EXAMPLE / "composition.json"), lab_vocabulary()
    )


def conditions(checked, left="squared", right="expanded_square"):
    return Requirements.from_document(
        {
            "version": 5,
            "graph": checked.context,
            "owner": "test.composition",
            "revision": "v1",
            "requirements": [
                {
                    "id": "law",
                    "condition": {"kind": "composition", "left": left, "right": right},
                }
            ],
        },
        checked,
    )


def verify(checked, required, bindings=None):
    return replay_requirements(
        checked.vocabulary.document,
        checked.document,
        required.document,
        required.check(bindings),
        bindings,
    )


def test_definition_identity_discharges_with_no_values_or_engine():
    checked = graph()
    required = conditions(checked)
    receipt = required.check()
    assert receipt["status"] == "satisfied"
    assert (
        receipt["requirements"][0]["condition"]["evidence_origin"]
        == "declared composition"
    )
    assert verify(checked, required)["independent_checker"] is True
    assert required.verify(receipt)["independent_checker"] is False


def test_mixed_contract_separates_symbolic_truth_and_input_evidence():
    checked = graph()
    required = Requirements.from_document(
        load_document(EXAMPLE / "computation_requirements_v5.json"), checked
    )
    receipt = required.check()
    assert [r["status"] for r in receipt["requirements"]] == [
        "satisfied",
        "pending",
        "pending",
    ]
    assert receipt["status"] == "pending"
    assert verify(checked, required)["verdict"] == "pending"
    bindings = {"quantity": 3, "name": "Ada"}
    compiled = python_backend(checked.vocabulary).compile(checked).require(required)
    assert (
        compiled.explain_input("quantity")["conditions"][0]["id"] == "positive_quantity"
    )
    assert all(
        c["id"] != "square_definition"
        for c in compiled.explain_input("quantity")["conditions"]
    )
    result = compiled.bind(bindings).execute()
    assert result.values == {"doubled": 18, "published": "Hello, Ada"}
    assert verify(checked, required, bindings)["verdict"] == "satisfied"
    assert (
        result.receipt["requirement_evidence"]["requirements"][0]["condition"][
            "evidence_origin"
        ]
        == "declared composition"
    )


@pytest.mark.parametrize(
    "left,right,status",
    [
        ("published", "greeting", "satisfied"),
        ("quantity", "quantity", "satisfied"),
        ("quantity", "squared", "pending"),
        ("squared", "doubled", "pending"),
        ("document", "document", "satisfied"),
    ],
)
def test_identity_and_unknown_are_distinct_from_representation_validity(
    left, right, status
):
    checked = graph()
    required = conditions(checked, left, right)
    assert required.check()["status"] == status
    assert verify(checked, required, {"quantity": 0, "name": ""})["verdict"] == status


def test_input_alias_identity_does_not_discharge_a_value_predicate():
    checked = graph()
    checked = checked.compose(
        "alias", "exact.alias", {"target": checked.ref("quantity")}
    )
    required = conditions(checked, "quantity", "alias")
    source = required.document
    source["requirements"].append(
        {
            "id": "positive",
            "condition": {
                "kind": "relation",
                "rule": "exact.positive-v1",
                "operands": [{"subject": "quantity", "path": []}],
            },
        }
    )
    required = Requirements.from_document(source, checked)
    assert [r["status"] for r in required.check()["requirements"]] == [
        "satisfied",
        "pending",
    ]
    assert verify(checked, required, {"quantity": 0})["verdict"] == "refuted"


def test_unknown_composition_is_not_refuted_or_resolved_by_execution():
    checked = graph()
    required = conditions(checked, "quantity", "squared")
    with pytest.raises(
        RequirementContractError, match="composition conditions"
    ) as failure:
        python_backend(checked.vocabulary).compile(checked).require(required)
    assert failure.value.report["status"] == "pending"
    assert failure.value.report["evidence_phase"] == "static"
    assert verify(checked, required, {"quantity": 1})["verdict"] == "pending"


def test_equal_literal_results_do_not_install_an_arithmetic_theory():
    checked = graph().compose("two", "exact.literal", {}, {"value": 2})
    checked = checked.compose("four", "exact.literal", {}, {"value": 4})
    checked = checked.compose(
        "sum", "exact.add", {"left": checked.ref("two"), "right": checked.ref("two")}
    )
    required = conditions(checked, "sum", "four")
    assert required.check()["status"] == "pending"
    assert verify(checked, required)["verdict"] == "pending"


def test_composition_law_does_not_certify_backend_implementations():
    checked, calls = graph(), []

    def faulty_multiply(ports, attrs):
        calls.append("multiply")
        return 42

    backend = Backend(
        "faulty",
        "v1",
        checked.vocabulary.fingerprint,
        {
            "exact.multiply": faulty_multiply,
            "exact.add": lambda p, a: p["left"] + p["right"],
        },
    )
    compiled = backend.compile(checked, [checked.ref("doubled")]).require(
        conditions(checked)
    )
    assert calls == []
    result = compiled.bind({"quantity": 3}).execute()
    assert result.values == {"doubled": 84}
    assert result.receipt["requirement_evidence"]["status"] == "satisfied"
    assert result.receipt["domain_validity"] == "not established"


def test_unselected_structural_subjects_never_become_implicit_computation():
    checked = graph()
    compiled = python_backend(checked.vocabulary).compile(
        checked, [checked.ref("published")]
    )
    for include in (False, True):
        with pytest.raises(ContractError, match="outside selected realization"):
            compiled.require(conditions(checked), include_condition_inputs=include)


@pytest.mark.parametrize(
    "mutate",
    [
        lambda c: c.update(left="missing"),
        lambda c: c.update(right="name"),
        lambda c: c.update(kind="scientific-proof"),
        lambda c: c.update(status="satisfied"),
        lambda c: c.update(normal_references=[0, 0]),
        lambda c: c.update(rule="user.asserts"),
    ],
)
def test_composition_admission_requires_closed_same_family_references(mutate):
    checked = graph()
    source = conditions(checked).document
    mutate(source["requirements"][0]["condition"])
    with pytest.raises(ContractError):
        Requirements.from_document(source, checked)
    with pytest.raises(ReplayError):
        replay_requirements(
            checked.vocabulary.document,
            checked.document,
            source,
            conditions(checked).check(),
        )


@pytest.mark.parametrize(
    "mutate",
    [
        lambda r: r["requirements"][0].update(status="refuted"),
        lambda r: r["requirements"][0]["condition"].update(normal_references=[0, 0]),
        lambda r: r["requirements"][0]["condition"].update(basis="assertion"),
        lambda r: r["requirements"][0]["condition"].update(
            evidence_origin="backend execution"
        ),
    ],
)
def test_independent_consumer_refuses_forged_symbolic_evidence(mutate):
    checked = graph()
    required = conditions(checked)
    receipt = required.check()
    mutate(receipt)
    with pytest.raises(ReplayError):
        replay_requirements(
            checked.vocabulary.document, checked.document, required.document, receipt
        )


def test_earlier_v4_does_not_silently_admit_v5_composition_form():
    checked = graph()
    source = conditions(checked).document
    source["version"] = 4
    with pytest.raises(ContractError):
        Requirements.from_document(source, checked)
    with pytest.raises(ReplayError):
        replay_requirements(
            checked.vocabulary.document,
            checked.document,
            source,
            conditions(checked).check(),
        )


@pytest.mark.parametrize("version", [1, 2, 3, 4])
@pytest.mark.parametrize("reverse", [False, True])
def test_workflow_composition_promotes_all_earlier_condition_versions(version, reverse):
    checked = graph()
    template = {
        "version": 1,
        "id": "law",
        "revision": "v1",
        "graph": checked.document,
        "inputs": {"quantity": "quantity", "name": "name"},
        "outputs": {"numeric": "doubled", "text": "published"},
        "requirements": conditions(checked).document,
    }
    old = deepcopy(template)
    old["id"] = "positive"
    if version == 1:
        record = {"id": "positive", "rule": "exact.positive-v1", "subject": "quantity"}
    elif version == 2:
        record = {
            "id": "positive",
            "rule": "exact.positive-v1",
            "subject": "quantity",
            "path": [],
        }
    else:
        record = {
            "id": "positive",
            "rule": "exact.positive-v1",
            "operands": [{"subject": "quantity", "path": []}],
        }
        if version == 4:
            record = {
                "id": "positive",
                "condition": {
                    "kind": "relation",
                    "rule": record["rule"],
                    "operands": record["operands"],
                },
            }
    old["requirements"] = {
        **conditions(checked).document,
        "version": version,
        "requirements": [record],
    }
    templates = [
        Workflow.from_document(d, checked.vocabulary)
        for d in ([old, template] if reverse else [template, old])
    ]
    first = templates[0].compose(
        checked,
        "first",
        {"quantity": checked.ref("quantity"), "name": checked.ref("name")},
    )
    second = templates[1].compose(
        first,
        "second",
        {"quantity": first.graph.ref("quantity"), "name": first.graph.ref("name")},
    )
    assert second.requirements.document["version"] == 5
    result = replay_workflows(
        checked.vocabulary.document,
        checked.document,
        [t.document for t in templates],
        second.document,
    )
    assert result["verdict"] == "pending"
    assert (
        second.compile(python_backend(checked.vocabulary))
        .bind({"quantity": 3, "name": "Ada"})
        .execute()
        .receipt["requirement_evidence"]["status"]
        == "satisfied"
    )


def test_documentary_universal_and_composition_evidence_share_one_envelope():
    checked = Graph.from_document(
        load_document(EXAMPLE / "publication.json"), document_vocabulary()
    )
    source = load_document(EXAMPLE / "publication_requirements_v4.json")
    source["version"] = 5
    source["requirements"].append(
        {
            "id": "alias_law",
            "condition": {
                "kind": "composition",
                "left": "published",
                "right": "content",
            },
        }
    )
    required = Requirements.from_document(source, checked)
    assert required.check()["requirements"][-1]["status"] == "satisfied"
    assert (
        verify(checked, required, load_document(EXAMPLE / "publication_bindings.json"))[
            "verdict"
        ]
        == "satisfied"
    )


def test_source_revision_invalidates_a_named_law_even_when_the_definition_looks_unchanged():
    checked = graph()
    required = conditions(checked)
    edit = Revision.from_document(
        load_document(EXAMPLE / "greeting_revision.json"), checked
    )
    with pytest.raises(ContractError, match="different graph context"):
        Requirements.from_document(required.document, edit.graph)
    with pytest.raises(ReplayError):
        replay_requirements(
            checked.vocabulary.document,
            edit.graph.document,
            required.document,
            required.check(),
        )


def test_cli_mixed_evidence_replays_in_an_isolated_process(tmp_path, capsys):
    assert (
        producer_main(
            [
                "requirements",
                str(EXAMPLE / "composition.json"),
                str(EXAMPLE / "computation_requirements_v5.json"),
            ]
        )
        == 1
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
            "--requirements",
            str(EXAMPLE / "computation_requirements_v5.json"),
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout)["verdict"] == "pending"
