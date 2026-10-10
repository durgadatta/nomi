"""Typed description families do not fabricate fitted state or scientific truth."""

from copy import deepcopy
import json
from pathlib import Path
import subprocess
import sys

import pytest

from tools.statistical_interface import ObjectGraph, PlanError, load_document
from tools.statistical_interface.model import catalog


EXAMPLE = Path("docs/research/data_workflows/statistical_objects.json")


@pytest.fixture
def document():
    return load_document(EXAMPLE)


def test_model_can_be_described_before_inputs_and_scale_assumptions_are_resolved(
    document,
):
    graph = ObjectGraph.from_document(document)
    checked = graph.check()
    assert checked["status"] == "description-checked"
    assert checked["scientific_validity"] == "not established"
    assert checked["execution"] == "not implemented"
    assert graph.inspect("planned_fit")["family"] == "fit_plan"
    assert (
        graph.inspect("positive_scale")["parameters"]["evidence_status"] == "unresolved"
    )
    assert graph.inspect("normal_likelihood")["ports"]["parameters"] == ["mu", "sigma"]


def test_distribution_parameters_cannot_be_replaced_by_columns(document):
    distribution = next(
        obj for obj in document["objects"] if obj["id"] == "normal_likelihood"
    )
    distribution["ports"]["parameters"] = ["reading"]
    with pytest.raises(PlanError, match="expected family.*parameter"):
        ObjectGraph.from_document(document)


def test_missing_obligations_are_not_filled_by_defaults(document):
    del document["objects"][-1]["parameters"]["randomness_owner"]
    with pytest.raises(PlanError, match="missing.*randomness_owner"):
        ObjectGraph.from_document(document)


def test_assumption_has_a_declared_evidence_status_not_a_boolean_proof(document):
    assumption = next(
        obj for obj in document["objects"] if obj["id"] == "positive_scale"
    )
    assumption["parameters"]["evidence_status"] = True
    with pytest.raises(PlanError, match="enum"):
        ObjectGraph.from_document(document)


def test_cycle_in_an_algorithm_dependency_is_refused(document):
    transform = next(obj for obj in document["objects"] if obj["id"] == "transform")
    transform["ports"]["inputs"] = ["planned_fit"]
    with pytest.raises(PlanError, match="cyclic"):
        ObjectGraph.from_document(document)


def test_immutable_descriptions_and_detached_inspection(document):
    graph = ObjectGraph.from_document(document)
    document["objects"].clear()
    graph.document["objects"].clear()
    graph.inspect("normal_likelihood")["ports"]["parameters"].clear()
    assert graph.inspect("normal_likelihood")["ports"]["parameters"] == ["mu", "sigma"]
    with pytest.raises(AttributeError):
        graph._outputs = ()


def test_catalog_has_complete_disjoint_slots_and_known_port_families():
    families = catalog()["families"]
    names = {family["id"] for family in families}
    assert len(names) == len(families)
    for family in families:
        assert set(family["ports"]).isdisjoint(family["parameters"])
        assert set(family["ports"]) | set(family["parameters"]) == set(
            family["contract_fields"]
        )
        for port in family["ports"].values():
            assert set(port["families"]) <= names
            assert port["multiplicity"] in ("one", "many")


def test_all_catalog_families_can_name_contracts_without_realizing_objects():
    families = catalog()["families"]
    defaults = {
        "text": "declared",
        "bool": False,
        "positive_int": 1,
        "record": {},
        "array": [],
        "text_list": [],
    }
    objects = []
    for family in families:
        ports = {
            name: [] if slot["multiplicity"] == "many" else slot["families"][0]
            for name, slot in family["ports"].items()
        }
        parameters = {
            name: slot["values"][0]
            if slot["kind"] == "enum"
            else deepcopy(defaults[slot["kind"]])
            for name, slot in family["parameters"].items()
        }
        objects.append(
            {
                "id": family["id"],
                "family": family["id"],
                "ports": ports,
                "parameters": parameters,
            }
        )
    document = {
        "version": 1,
        "objects": objects,
        "outputs": [obj["id"] for obj in objects],
    }
    graph = ObjectGraph.from_document(document)
    assert {obj["family"] for obj in graph.check()["objects"]} == {
        family["id"] for family in families
    }
    assert all(
        obj["realization"] == "description only" for obj in graph.check()["objects"]
    )


def test_catalog_only_objects_do_not_become_executable_dataframe_operations(document):
    from tools.statistical_interface import Plan

    with pytest.raises(PlanError):
        Plan.from_document(document)


def test_object_cli_inspects_a_named_distribution_without_sampling():
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "tools.statistical_interface",
            "objects",
            str(EXAMPLE),
            "normal_likelihood",
        ],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    value = json.loads(result.stdout)
    assert value["family"] == "distribution"
    assert value["realization"] == "description only"


@pytest.mark.parametrize(
    "mutation,message",
    [
        (
            lambda d: d["objects"][0].__setitem__("family", "unknown"),
            "unknown statistical family",
        ),
        (lambda d: d["objects"].append(deepcopy(d["objects"][0])), "duplicate object"),
        (
            lambda d: d["objects"][1]["ports"].__setitem__("schema", ["schema"]),
            "bounded identifier",
        ),
        (
            lambda d: d["objects"][1]["ports"].__setitem__("schema", "absent"),
            "unknown reference",
        ),
        (lambda d: d.__setitem__("version", True), "envelope version"),
        (lambda d: d.__setitem__("outputs", ["absent"]), "unknown object output"),
    ],
)
def test_invalid_statistical_descriptions_fail_at_the_named_boundary(
    document, mutation, message
):
    mutation(document)
    with pytest.raises(PlanError, match=message):
        ObjectGraph.from_document(document)


def test_descriptions_do_not_execute_foreign_parameter_objects(document):
    class Callback:
        def __call__(self):
            pytest.fail("description checker called a host object")

    document["objects"][0]["parameters"]["ordered_fields"] = Callback()
    with pytest.raises(PlanError, match="only inert JSON"):
        ObjectGraph.from_document(document)


def test_description_references_are_qualified_by_document_and_catalog_context(document):
    first = ObjectGraph.from_document(document).inspect("sigma")
    parameter = next(obj for obj in document["objects"] if obj["id"] == "sigma")
    parameter["parameters"]["constraint"] = "nonnegative; boundary law is unresolved"
    second = ObjectGraph.from_document(document).inspect("sigma")
    assert first["id"] == second["id"]
    assert first["context"] != second["context"]
