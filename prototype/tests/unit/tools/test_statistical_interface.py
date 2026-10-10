"""Schema-only contracts and exact laws, independent of a dataframe engine."""

from copy import deepcopy
from fractions import Fraction
from itertools import product
import json
import math
from pathlib import Path
import subprocess
import sys

import pytest

from tools.statistical_interface import Plan, PlanError, load_document
from tools.statistical_interface.model import catalog


EXAMPLE = Path("docs/research/data_workflows/statistical_plan.json")


@pytest.fixture
def document():
    return load_document(EXAMPLE)


def node(document, name):
    return next(item for item in document["nodes"] if item["id"] == name)


def test_filtered_nullable_workflow_has_a_replayable_exact_mean_proof(document):
    plan = Plan.from_document(document)
    proof = plan.prove("average", "decomposed")
    assert proof["status"] == "equivalent"
    assert {step["rule"] for step in proof["steps"]} == {"mean-valid-exact-v1"}
    assert plan.verify(json.loads(json.dumps(proof)))
    assert plan.check()["data_access"] == "none"
    assert plan.inspect("difference")["type"]["nullable"] is True


def test_independent_online_exact_mean_agrees_with_count_sum_definition():
    # A finite soundness discriminator for the trusted definition, not a proof
    # inferred from testing data or an evaluation path in the checker.
    for length in range(4):
        for values in product((None, -2, 0, 3), repeat=length):
            average, count = Fraction(0), 0
            for value in values:
                if value is not None:
                    count += 1
                    average += (Fraction(value) - average) / count
            expected = (
                None
                if count == 0
                else sum(Fraction(v) for v in values if v is not None) / count
            )
            actual = None if count == 0 else average
            assert actual == expected


def test_literal_countermodels_explain_refused_mean_generalizations():
    assert Fraction(2, 1) != Fraction(2, 2)  # [2, null]: valid versus row count
    assert Fraction(0 + 10, 2) != Fraction(0 + 10 + 10 + 10, 4)
    values = [1e16, 1.0, -1e16]
    left_fold = 0.0
    for value in values:
        left_fold += value
    assert left_fold == 0.0
    assert math.fsum(values) == 1.0


def test_row_count_does_not_prove_nullable_mean(document):
    proof = Plan.from_document(document).prove("average", "wrong_denominator")
    assert proof["status"] == "unknown"


def test_alias_preserves_reference_without_losing_named_intermediates(document):
    plan = Plan.from_document(document)
    assert plan.prove("average", "published_average")["status"] == "equivalent"
    inspected = {item["id"]: item for item in plan.check()["nodes"]}
    assert set(inspected) == {item["id"] for item in document["nodes"]}
    assert inspected["published_average"]["inputs"] == ["average"]


def test_plan_and_inspection_snapshots_cannot_be_accidentally_mutated(document):
    plan = Plan.from_document(document)
    document["nodes"].clear()
    plan.document["nodes"].clear()
    inspected = plan.inspect("difference")
    inspected["inputs"].clear()
    assert plan.inspect("difference")["inputs"] == ["reading", "baseline"]
    with pytest.raises(AttributeError):
        plan._profile = "float64-opaque-v1"
    with pytest.raises(AttributeError):
        del plan._sealed


@pytest.mark.parametrize(
    "profile,dtype",
    [
        ("float64-opaque-v1", "Float64"),
        ("exact-rational-v1", "Float64"),
        ("float64-opaque-v1", "ExactRational"),
    ],
)
def test_mean_law_refuses_unspecified_or_floating_arithmetic(document, profile, dtype):
    document["profile"] = profile
    for field in node(document, "observations")["schema"][:2]:
        field["dtype"] = dtype
    proof = Plan.from_document(document).prove("average", "decomposed")
    assert proof["status"] == "unknown"
    assert not proof["steps"]


def test_source_identity_is_not_schema_or_display_name(document):
    other = deepcopy(node(document, "observations"))
    other["id"] = "other_observations"
    document["nodes"].extend(
        [
            other,
            {
                "id": "other_reading",
                "op": "column",
                "args": [other["id"]],
                "field": "reading",
            },
        ]
    )
    node(document, "difference")["args"] = ["reading", "other_reading"]
    with pytest.raises(PlanError, match="different observation domains"):
        Plan.from_document(document)


def test_filter_mask_must_belong_to_the_input_relation(document):
    node(document, "eligibility")["args"] = ["selected"]
    with pytest.raises(PlanError, match="cyclic"):
        Plan.from_document(document)


def test_nullable_filter_requires_an_explicit_policy_not_an_engine_default(document):
    node(document, "observations")["schema"][2]["nullable"] = True
    with pytest.raises(PlanError, match="nullable mask policy"):
        Plan.from_document(document)


@pytest.mark.parametrize("dtype", ["Bool", "Text"])
def test_sum_excludes_boolean_and_text_implicit_numeric_coercion(document, dtype):
    node(document, "total")["args"] = ["eligibility"]
    node(document, "observations")["schema"][2]["dtype"] = dtype
    if dtype == "Text":
        # Keep the filter valid so the rejection concerns aggregation.
        document["nodes"].append(
            {"id": "text", "op": "column", "args": ["observations"], "field": "reading"}
        )
        node(document, "observations")["schema"][0]["dtype"] = "Text"
        node(document, "observations")["schema"][2]["dtype"] = "Bool"
        node(document, "total")["args"] = ["text"]
        node(document, "difference")["op"] = "alias"
        node(document, "difference")["args"] = ["baseline"]
    with pytest.raises(PlanError, match="numeric aggregation excludes"):
        Plan.from_document(document)


@pytest.mark.parametrize(
    "mutation,message",
    [
        (lambda d: d["nodes"].append(deepcopy(d["nodes"][0])), "duplicate node"),
        (
            lambda d: node(d, "reading")["args"].__setitem__(0, "missing"),
            "unknown reference",
        ),
        (lambda d: node(d, "reading").__setitem__("field", "absent"), "unknown field"),
        (
            lambda d: node(d, "observations").__setitem__("uri", "file:///never-open"),
            "unknown",
        ),
        (
            lambda d: node(d, "reading").__setitem__("op", "execute_callback"),
            "unsupported operation",
        ),
        (lambda d: d.__setitem__("version", True), "unsupported plan version"),
        (
            lambda d: node(d, "observations")["schema"][0].__setitem__("nullable", 1),
            "nullable must be Bool",
        ),
        (lambda d: d.__setitem__("outputs", ["absent"]), "unknown output"),
    ],
)
def test_invalid_or_unsupported_contracts_fail_locally(document, mutation, message):
    mutation(document)
    with pytest.raises(PlanError, match=message):
        Plan.from_document(document)


def test_foreign_host_objects_are_refused_without_invoking_them(document):
    class Callback:
        def __call__(self):
            pytest.fail("schema checking invoked a host callback")

        def __repr__(self):
            pytest.fail("schema checking inspected a host callback")

    document["callback"] = Callback()
    with pytest.raises(PlanError, match="only inert JSON"):
        Plan.from_document(document)


def test_topological_check_does_not_depend_on_manifest_order(document):
    document["nodes"].reverse()
    assert (
        Plan.from_document(document).prove("average", "decomposed")["status"]
        == "equivalent"
    )


@pytest.mark.parametrize(
    "part", ["context", "steps", "normal_forms", "version", "status"]
)
def test_tampered_certificates_are_refused(document, part):
    plan = Plan.from_document(document)
    proof = plan.prove("average", "decomposed")
    proof[part] = {
        "version": True,
        "steps": [],
        "normal_forms": ["forged"],
        "status": "unknown",
        "context": "forged",
    }[part]
    assert not plan.verify(proof)


def test_certificate_does_not_survive_a_schema_or_profile_revision(document):
    proof = Plan.from_document(document).prove("average", "decomposed")
    node(document, "observations")["schema"][0]["nullable"] = False
    assert not Plan.from_document(document).verify(proof)


def test_duplicate_json_keys_are_not_silently_replaced(tmp_path):
    path = tmp_path / "duplicate.json"
    path.write_text('{"version":1,"version":2}')
    with pytest.raises(PlanError, match="duplicate JSON key"):
        load_document(path)


def test_deep_graph_is_refused_without_recursion_failure(document):
    previous = "average"
    for index in range(70):
        name = f"alias_{index}"
        document["nodes"].append({"id": name, "op": "alias", "args": [previous]})
        previous = name
    with pytest.raises(PlanError, match="depth budget"):
        Plan.from_document(document)


def test_catalog_keeps_statistical_families_separate_from_executable_ports():
    description = catalog()
    by_name = {family["id"]: family for family in description["families"]}
    assert by_name["estimand"]["status"] == "catalog-only"
    assert "identification_assumptions" in by_name["estimand"]["contract_fields"]
    assert by_name["distribution"]["status"] == "catalog-only"
    assert "fit" not in description["operations"]


@pytest.mark.parametrize(
    "right,status,code",
    [
        ("decomposed", "equivalent", 0),
        ("wrong_denominator", "unknown", 1),
        ("absent", "invalid", 2),
    ],
)
def test_cli_distinguishes_proven_unknown_and_invalid(right, status, code):
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "tools.statistical_interface",
            "prove",
            str(EXAMPLE),
            "average",
            right,
        ],
        capture_output=True,
        text=True,
    )
    assert result.returncode == code
    assert json.loads(result.stdout)["status"] == status
