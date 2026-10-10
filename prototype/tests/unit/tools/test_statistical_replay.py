"""Independent consumer, malformed receipts and revisioned trusted theory."""

from copy import deepcopy
import json
from pathlib import Path
import subprocess
import sys

import pytest

from tools.statistical_interface import Plan, PlanError, load_document
from tools.statistical_interface.model import catalog
from tools import statistical_replay


EXAMPLE = Path("docs/research/data_workflows/statistical_plan.json")


@pytest.fixture
def artifacts():
    document = load_document(EXAMPLE)
    description = catalog()
    proof = Plan.from_document(document).prove("average", "decomposed")
    return document, proof, description


def test_independent_exact_consumer_accepts_a_named_filtered_mean(artifacts):
    assert statistical_replay.verify(*artifacts)["status"] == "verified"


@pytest.mark.parametrize(
    "mutation",
    [
        lambda receipt: receipt.__setitem__("normal_forms", ["forged", "forged"]),
        lambda receipt: receipt.__setitem__("right", "wrong_denominator"),
        lambda receipt: receipt.__setitem__("steps", []),
        lambda receipt: receipt["steps"].append(deepcopy(receipt["steps"][0])),
        lambda receipt: receipt.__setitem__("version", True),
        lambda receipt: receipt.__setitem__("context", "forged"),
    ],
)
def test_independent_consumer_refuses_forged_receipts(artifacts, mutation):
    document, receipt, description = artifacts
    mutation(receipt)
    assert (
        statistical_replay.verify(document, receipt, description)["status"] == "refused"
    )


def test_independent_consumer_rechecks_schema_and_not_only_fingerprints(artifacts):
    document, receipt, description = artifacts
    document["nodes"][0]["schema"][0]["dtype"] = "Bool"
    assert (
        statistical_replay.verify(document, receipt, description)["status"] == "refused"
    )


def test_duplicate_id_in_an_unreachable_node_is_still_invalid(artifacts):
    document, receipt, description = artifacts
    document["nodes"].append(deepcopy(document["nodes"][0]))
    assert (
        statistical_replay.verify(document, receipt, description)["status"] == "refused"
    )


def test_full_dag_rechecks_aliases_and_manifest_order(artifacts):
    document, _, description = artifacts
    document["nodes"].reverse()
    receipt = Plan.from_document(document).prove("average", "published_average")
    assert (
        statistical_replay.verify(document, receipt, description)["status"]
        == "verified"
    )


def test_changed_numeric_definition_requires_a_theory_revision(
    artifacts, tmp_path, monkeypatch
):
    document, receipt, description = artifacts
    description["profiles"]["exact-rational-v1"]["sum_empty"] = "Missing"
    assert (
        statistical_replay.verify(document, receipt, description)["status"] == "refused"
    )
    path = tmp_path / "changed-catalog.json"
    path.write_text(json.dumps(description))
    from tools.statistical_interface import model

    monkeypatch.setattr(model, "CATALOG_PATH", path)
    with pytest.raises(PlanError, match="theory revision"):
        Plan.from_document(document)


def test_unknown_is_not_accepted_as_an_equality_proof(artifacts):
    document, _, description = artifacts
    receipt = Plan.from_document(document).prove("average", "wrong_denominator")
    assert (
        statistical_replay.verify(document, receipt, description)["status"] == "refused"
    )


def test_consumer_does_not_import_the_planner_or_shared_inference():
    path = Path(statistical_replay.__file__)
    import ast

    tree = ast.parse(path.read_text())
    modules = []
    for item in ast.walk(tree):
        if isinstance(item, ast.Import):
            modules.extend(alias.name for alias in item.names)
        elif isinstance(item, ast.ImportFrom):
            modules.append(item.module)
    assert set(modules) <= {
        "argparse",
        "dataclasses",
        "hashlib",
        "json",
        "pathlib",
        "re",
        "sys",
    }


def test_independent_cli_replays_proof_as_json(artifacts, tmp_path):
    _, receipt, _ = artifacts
    proof = tmp_path / "mean-proof.json"
    proof.write_text(json.dumps(receipt))
    result = subprocess.run(
        [sys.executable, "-m", "tools.statistical_replay", str(EXAMPLE), str(proof)],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert json.loads(result.stdout)["status"] == "verified"


def test_invalid_inspection_reference_does_not_execute_host_string_conversion(
    artifacts,
):
    class Foreign:
        def __str__(self):
            pytest.fail("passive inspection invoked a host conversion")

    plan = Plan.from_document(artifacts[0])
    with pytest.raises(PlanError, match="unknown node reference"):
        plan.inspect(Foreign())
