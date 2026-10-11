"""A formal reasoning fragment: no measurements, solver, or analytic theorem."""

import copy
from fractions import Fraction
import json
from pathlib import Path
import random
import subprocess
import sys

import pytest

from tools.object_interface.documents import ContractError
from tools.scientific_probe import Model, envelope_graph
from tools.scientific_replay import ReplayError, expected_receipt, replay

ROOT = Path(__file__).resolve().parents[4]
FIXTURES = ROOT / "docs/research/scientific_models"


def oscillator(damped=False):
    name = "damped_oscillator.json" if damped else "oscillator.json"
    return json.loads((FIXTURES / name).read_text())


def node(document, identity):
    return next(row for row in document["objects"] if row["id"] == identity)


def test_conservation_is_conditional_on_named_formal_premises_without_inputs():
    source = oscillator()
    receipt = Model(source).check()
    assert receipt["claims"][0]["status"] == "conditional-identity"
    assert receipt["claims"][0]["residual"] == []
    assert receipt["objects"][-1]["dimension"] == {"Mass": 1, "Length": 2, "Time": -3}
    assert receipt["scope"]["inputs"] == "none"
    assert receipt["scope"]["physical_validity"] == "not-established"
    assert receipt["scope"]["premise_consistency"] == "not-checked"
    assert replay(source, receipt)["independent"] is True


def test_damping_changes_the_consequence_and_keeps_conservation_unresolved():
    source = oscillator(True)
    receipt = Model(source).check()
    conservation, balance = receipt["claims"]
    assert conservation["status"] == "unknown"
    assert conservation["residual"] == [
        {"coefficient": [-1, 1], "powers": {"c": 1, "v": 2}}
    ]
    assert balance["status"] == "conditional-identity"
    assert replay(source, receipt)["status"] == "replayed"
    with pytest.raises(ReplayError):
        replay(source, Model(oscillator()).check())


def test_structural_description_cannot_discharge_mathematical_dimension_checks():
    source = oscillator()
    node(source, "energy_twice")["args"] = ["x", "m"]
    graph = envelope_graph(source)
    assert graph.inspect("energy_twice")["role"] == "description"
    assert graph.inspect("energy_twice")["attributes"]["authored"]["args"] == ["x", "m"]
    with pytest.raises(ContractError, match="incompatible dimensions"):
        Model(source)
    with pytest.raises(ReplayError):
        expected_receipt(source)


def test_equal_labels_do_not_merge_formal_generator_identity():
    source = oscillator()
    node(source, "v")["label"] = "reading"
    node(source, "x")["label"] = "reading"
    source["objects"].append(
        {
            "id": "x_other",
            "op": "symbol",
            "label": "reading",
            "dimension": {"Length": 1},
        }
    )
    source["claims"].append(
        {"id": "same_reading", "left": "x", "right": "x_other", "witness": []}
    )
    receipt = Model(source).check()
    assert receipt["claims"][-1]["status"] == "unknown"
    assert len(receipt["claims"][-1]["residual"]) == 2
    assert replay(source, receipt)["status"] == "replayed"


def test_changing_constant_mass_to_a_declared_variable_changes_the_derivation():
    source = oscillator()
    source["objects"].append(
        {
            "id": "mass_rate",
            "op": "symbol",
            "label": "mass rate",
            "dimension": {"Mass": 1, "Time": -1},
        }
    )
    source["derivation"]["images"]["m"] = "mass_rate"
    receipt = Model(source).check()
    assert receipt["claims"][0]["status"] == "unknown"
    assert receipt["claims"][0]["residual"] == [
        {"coefficient": [1, 2], "powers": {"mass_rate": 1, "v": 2}}
    ]
    assert replay(source, receipt)["status"] == "replayed"


def test_equations_may_share_cyclic_unknowns_without_cyclic_expression_nodes():
    source = oscillator()
    source["relations"].extend(
        [
            {"id": "left_constraint", "left": "inertia", "right": "restoring"},
            {"id": "right_constraint", "left": "restoring", "right": "inertia"},
        ]
    )
    receipt = Model(source).check()
    assert len(receipt["relations"]) == 3
    assert receipt["scope"]["premise_consistency"] == "not-checked"
    assert replay(source, receipt)["status"] == "replayed"


def test_a_direct_contradiction_blocks_claims_without_promising_general_consistency():
    source = oscillator()
    source["objects"].append(
        {
            "id": "unit_force",
            "op": "rational",
            "numerator": 1,
            "denominator": 1,
            "dimension": node(source, "zero_force")["dimension"],
        }
    )
    source["relations"].append(
        {"id": "impossible", "left": "unit_force", "right": "zero_force"}
    )
    receipt = Model(source).check()
    assert receipt["claims"][0]["status"] == "inconsistent-premises"
    assert receipt["scope"]["premise_consistency"] == "direct-contradiction"
    assert receipt["scope"]["direct_contradictions"] == ["impossible"]
    assert replay(source, receipt)["status"] == "replayed"


def test_snapshot_and_receipts_do_not_share_mutable_authored_state():
    source = oscillator()
    model = Model(source)
    before = model.check()
    node(source, "x")["dimension"] = {"Time": 1}
    model.document["claims"].clear()
    model.check()["scope"]["physical_validity"] = "established"
    assert model.check() == before
    with pytest.raises(AttributeError):
        model._source = "{}"


BAD_SOURCE = [
    lambda s: s.update(version=True),
    lambda s: s.update(profile="noncommutative-v1"),
    lambda s: s.update(extra=True),
    lambda s: s["objects"].append(copy.deepcopy(s["objects"][0])),
    lambda s: node(s, "half").update(numerator=True),
    lambda s: node(s, "half").update(denominator=0),
    lambda s: node(s, "half").update(numerator=1.5),
    lambda s: node(s, "half").update(numerator=1 << 4096),
    lambda s: node(s, "x").update(dimension={"Length": True}),
    lambda s: node(s, "x").update(dimension={"Length": 0}),
    lambda s: node(s, "x").update(dimension={"Length": 129}),
    lambda s: node(s, "x").update(label=""),
    lambda s: node(s, "energy").update(args=["missing", "half"]),
    lambda s: node(s, "energy").update(args=["energy", "half"]),
    lambda s: node(s, "energy").update(args=["half"]),
    lambda s: node(s, "energy").update(op="divide"),
    lambda s: s["derivation"]["images"].pop("m"),
    lambda s: s["derivation"]["images"].update(x="m"),
    lambda s: s["derivation"]["images"].update(x="energy_rate"),
    lambda s: s["derivation"]["images"].update(unknown=None),
    lambda s: s["derivation"]["images"].update(x="missing"),
    lambda s: s["relations"][0].update(right="zero_power"),
    lambda s: s["relations"][0].update(left=["inertia"]),
    lambda s: s["relations"][0].update(id="x"),
    lambda s: s["claims"][0].update(id="dynamics"),
    lambda s: s["claims"][0]["witness"][0].update(multiplier="m"),
    lambda s: s["claims"][0]["witness"][0].update(relation="missing"),
    lambda s: s["claims"][0]["witness"][0].update(multiplier=False),
]


@pytest.mark.parametrize("mutation", BAD_SOURCE)
def test_both_admission_paths_refuse_unsupported_or_invalid_facts(mutation):
    source = oscillator()
    mutation(source)
    with pytest.raises(ContractError):
        Model(source)
    with pytest.raises(ReplayError):
        expected_receipt(source)


@pytest.mark.parametrize(
    "field,value",
    [("status", "refuted"), ("status", "proved"), ("residual", []), ("witness", [])],
)
def test_replay_does_not_accept_edited_unknown_evidence(field, value):
    source = oscillator(True)
    receipt = Model(source).check()
    receipt["claims"][0][field] = value
    with pytest.raises(ReplayError):
        replay(source, receipt)


@pytest.mark.parametrize(
    "field,value",
    [
        ("version", True),
        ("context", "stale"),
        ("profile", "float64"),
        ("objects", []),
        ("scope", {"independent": True}),
    ],
)
def test_replay_rejects_forged_receipt_scope_identity_or_source_facts(field, value):
    source = oscillator()
    receipt = Model(source).check()
    receipt[field] = value
    with pytest.raises(ReplayError):
        replay(source, receipt)


def test_numeric_counterexamples_crosscheck_the_formal_derivative_without_proving_it():
    receipt = Model(oscillator(True)).check()
    derivative = next(
        row["normal"] for row in receipt["objects"] if row["id"] == "energy_rate"
    )
    rng = random.Random(20261010)
    for _ in range(32):
        values = {
            key: Fraction(rng.randint(-7, 7), rng.randint(1, 7))
            for key in ("m", "k", "x", "v", "a", "c")
        }
        actual = Fraction(0)
        for term in derivative:
            value = Fraction(*term["coefficient"])
            for key, power in term["powers"].items():
                value *= values[key] ** power
            actual += value
        assert (
            actual
            == values["m"] * values["v"] * values["a"]
            + values["k"] * values["x"] * values["v"]
        )


def test_replay_runs_in_an_isolated_process_without_producer_or_framework_imports(
    tmp_path,
):
    source = oscillator()
    receipt = Model(source).check()
    (tmp_path / "source.json").write_text(json.dumps(source))
    (tmp_path / "receipt.json").write_text(json.dumps(receipt))
    script = """
import importlib.abc, runpy, sys
class Block(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if fullname.split('.')[0] in ('tools', 'prototype'):
            raise AssertionError('producer/framework import: ' + fullname)
sys.meta_path.insert(0, Block())
sys.argv = [sys.argv[1], sys.argv[2], sys.argv[3]]
runpy.run_path(sys.argv[0], run_name='__main__')
"""
    result = subprocess.run(
        [
            sys.executable,
            "-I",
            "-c",
            script,
            str(ROOT / "tools/scientific_replay.py"),
            str(tmp_path / "source.json"),
            str(tmp_path / "receipt.json"),
        ],
        text=True,
        capture_output=True,
    )
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout)["independent"] is True


def test_cli_exits_distinguish_checked_unresolved_and_refused(tmp_path):
    command = [sys.executable, "-m", "tools.scientific_probe"]
    good = subprocess.run(
        [*command, str(FIXTURES / "oscillator.json")], text=True, capture_output=True
    )
    unresolved = subprocess.run(
        [*command, str(FIXTURES / "damped_oscillator.json")],
        text=True,
        capture_output=True,
    )
    assert good.returncode == 0
    assert unresolved.returncode == 1
    bad = oscillator()
    node(bad, "half")["denominator"] = 0
    path = tmp_path / "bad.json"
    path.write_text(json.dumps(bad))
    refused = subprocess.run([*command, str(path)], text=True, capture_output=True)
    assert refused.returncode == 2
    assert json.loads(refused.stdout)["status"] == "refused"


def test_a_nonphysical_space_vocabulary_reuses_formal_reasoning_without_importing_physics():
    source = oscillator()
    source["id"] = "quadratic-state-model"
    renaming = {"Length": "Stock", "Mass": "Weight", "Time": "Tick"}
    for row in source["objects"]:
        if "dimension" in row:
            row["dimension"] = {
                renaming[key]: value for key, value in row["dimension"].items()
            }
        if row["op"] == "symbol":
            row["label"] = "model term " + row["id"]
    source["derivation"]["dimension"] = {"Tick": 1}
    receipt = Model(source).check()
    assert receipt["claims"][0]["status"] == "conditional-identity"
    assert receipt["scope"]["physical_validity"] == "not-established"
    assert replay(source, receipt)["status"] == "replayed"


def test_a_missing_witness_is_unknown_even_if_a_different_witness_would_work():
    source = oscillator()
    source["claims"][0]["witness"] = []
    receipt = Model(source).check()
    assert receipt["claims"][0]["status"] == "unknown"
    assert replay(source, receipt)["status"] == "replayed"


def test_a_derivative_image_can_be_a_named_polynomial_without_recursive_image_expansion():
    source = oscillator()
    source["objects"].append({"id": "twice_velocity", "op": "add", "args": ["v", "v"]})
    source["derivation"]["images"]["x"] = "twice_velocity"
    receipt = Model(source).check()
    assert receipt["claims"][0]["status"] == "unknown"
    assert replay(source, receipt)["status"] == "replayed"


@pytest.mark.parametrize("kind", ["depth", "degree", "coefficient", "dimension"])
def test_capacity_is_refused_instead_of_becoming_a_wrong_formal_result(kind):
    source = oscillator()
    if kind == "depth":
        source["objects"].append(
            {
                "id": "zero",
                "op": "rational",
                "numerator": 0,
                "denominator": 1,
                "dimension": {},
            }
        )
        previous = "zero"
        for index in range(64):
            identity = "chain_" + str(index)
            source["objects"].append(
                {"id": identity, "op": "add", "args": [previous, "zero"]}
            )
            previous = identity
    elif kind == "degree":
        previous = "x"
        for index in range(6):
            identity = "power_" + str(index)
            source["objects"].append(
                {"id": identity, "op": "multiply", "args": [previous, previous]}
            )
            previous = identity
    elif kind == "coefficient":
        node(source, "half")["numerator"] = 1 << 4095
        source["objects"].append(
            {"id": "coefficient_square", "op": "multiply", "args": ["half", "half"]}
        )
    else:
        source["objects"].append(
            {
                "id": "too_many_dimensions",
                "op": "symbol",
                "label": "unsupported",
                "dimension": {f"Dimension_{i}": 1 for i in range(17)},
            }
        )
    with pytest.raises(ContractError):
        Model(source)
    with pytest.raises(ReplayError):
        expected_receipt(source)


def test_monomial_capacity_refuses_an_expanding_expression():
    source = oscillator()
    source["objects"] = [
        {"id": f"s_{i}", "op": "symbol", "label": "formal generator", "dimension": {}}
        for i in range(16)
    ]
    source["objects"].extend(
        [
            {"id": "sum", "op": "add", "args": [f"s_{i}" for i in range(16)]},
            {"id": "square", "op": "multiply", "args": ["sum", "sum"]},
            {"id": "quartic", "op": "multiply", "args": ["square", "square"]},
        ]
    )
    source["derivation"]["images"] = {}
    source["relations"], source["claims"] = [], []
    with pytest.raises(ContractError, match="monomial budget"):
        Model(source)
    with pytest.raises(ReplayError, match="monomial capacity"):
        expected_receipt(source)


def test_consistency_is_not_inferred_from_the_absence_of_a_direct_contradiction():
    source = oscillator()
    source["objects"].append(
        {
            "id": "one_force",
            "op": "rational",
            "numerator": 1,
            "denominator": 1,
            "dimension": node(source, "zero_force")["dimension"],
        }
    )
    source["relations"].extend(
        [
            {"id": "x_zero", "left": "inertia", "right": "zero_force"},
            {"id": "x_one", "left": "inertia", "right": "one_force"},
        ]
    )
    receipt = Model(source).check()
    assert receipt["scope"]["premise_consistency"] == "not-checked"
    assert receipt["scope"]["direct_contradictions"] == []
    assert replay(source, receipt)["status"] == "replayed"


def test_standalone_loader_refuses_duplicate_keys_and_noninert_receipts(tmp_path):
    from tools.scientific_replay import load

    path = tmp_path / "duplicate.json"
    path.write_text('{"version": 1, "version": 2}')
    with pytest.raises(ReplayError, match="duplicate JSON key"):
        load(path)
    source = oscillator()
    receipt = Model(source).check()
    receipt["scope"]["float"] = float("nan")
    with pytest.raises(ReplayError):
        replay(source, receipt)


@pytest.mark.parametrize("damped", [False, True])
def test_tracked_evidence_stays_fresh_and_replays_independently(damped):
    source = oscillator(damped)
    name = "damped_oscillator_receipt.json" if damped else "oscillator_receipt.json"
    receipt = json.loads((FIXTURES / name).read_text())
    assert receipt == Model(source).check()
    assert replay(source, receipt)["status"] == "replayed"


def test_explanation_exposes_the_supplied_basis_and_preserves_unresolved_status():
    model = Model(oscillator(True))
    explanation = model.explain_claim("energy_conserved")
    assert explanation["status"] == "unknown"
    assert "another witness may work" in explanation["explanation"]
    assert explanation["supplied_witness"] == [
        {"relation": "dynamics", "multiplier": "v"}
    ]
    assert explanation["declared_derivation"]["images"]["m"] is None
    assert "not established" in explanation["premise_usage"]
    explanation["residual"].clear()
    assert model.explain_claim("energy_conserved")["residual"]
    with pytest.raises(ContractError, match="unknown claim"):
        model.explain_claim("missing")


def test_cli_can_explain_a_checked_claim_in_a_model_with_another_unknown_claim():
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "tools.scientific_probe",
            str(FIXTURES / "damped_oscillator.json"),
            "--claim",
            "energy_dissipation",
        ],
        text=True,
        capture_output=True,
    )
    assert result.returncode == 0
    assert json.loads(result.stdout)["status"] == "conditional-identity"
