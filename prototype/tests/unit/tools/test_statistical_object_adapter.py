"""Statistical metadata is a domain adapter, not the generic object model."""

from pathlib import Path

import pytest

from tools.object_interface import ContractError, load_document
from tools.object_interface.backend import Backend
from tools.statistical_interface.engine_free import (
    adapt_descriptions,
    descriptor_vocabulary,
)
from tools.statistical_interface.model import PlanError

ROOT = Path(__file__).resolve().parents[4]


def example():
    return load_document(ROOT / "docs/research/data_workflows/statistical_objects.json")


def test_all_35_statistical_families_use_generic_description_ports():
    vocabulary = descriptor_vocabulary().document
    assert len(vocabulary["types"]) == 35
    assert all(
        contract["role"] == "description"
        for contract in vocabulary["operations"].values()
    )
    assert all(contract["value"] is None for contract in vocabulary["types"].values())


def test_statistics_adapter_preserves_references_and_unresolved_parameters():
    document = example()
    checked = adapt_descriptions(document)
    assert checked.check()["status"] == "composition-checked"
    for original in document["objects"]:
        adapted = checked.inspect(original["id"])
        assert adapted["type"] == original["family"]
        assert adapted["attributes"] == original["parameters"]
        assert adapted["role"] == "description"
        contract = checked.vocabulary.document["operations"][adapted["operation"]]
        for port, value in original["ports"].items():
            expected = (
                [value] if contract["ports"][port]["multiplicity"] == "one" else value
            )
            assert adapted["ports"][port] == expected
    assert checked.check()["domain_validity"] == "not established"


def test_statistics_domain_validator_remains_in_front_of_generic_envelope():
    document = example()
    document["objects"][0]["family"] = "made-up-science"
    with pytest.raises(PlanError, match="unknown statistical family"):
        adapt_descriptions(document)


def test_adapted_fitted_description_cannot_be_executed_just_by_adding_backend():
    checked = adapt_descriptions(example())
    backend = Backend(
        "statistics-placeholder", "v1", checked.vocabulary.fingerprint, {}
    )
    with pytest.raises(ContractError, match="description has no realization"):
        backend.compile(checked)
