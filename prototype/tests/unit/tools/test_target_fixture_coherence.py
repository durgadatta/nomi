"""Narrow positive-fixture integrity checks, not parsing or target typechecking."""

import json
from pathlib import Path
import re

import pytest


ROOT = Path(__file__).resolve().parents[4]
DESIGN = ROOT / "docs/design"
ACTIVE_TARGETS = (
    "function_contracts_target.nomi",
    "interaction_model_target.nomi",
    "pattern_matching_target.nomi",
    "resource_lifetime_target.nomi",
    "targets/binding.nomi",
    "targets/boundaries.nomi",
    "targets/collections.nomi",
    "targets/concurrency.nomi",
    "targets/data.nomi",
    "targets/effects.nomi",
    "targets/failure.nomi",
    "targets/functions.nomi",
    "targets/modules.nomi",
    "targets/numerics.nomi",
    "targets/overall.nomi",
    "targets/patterns.nomi",
    "targets/resources.nomi",
    "targets/tooling.nomi",
    "targets/research/data_collections.nomi",
    "targets/research/domain_layers.nomi",
    "targets/research/generic_operations.nomi",
    "targets/research/messaging.nomi",
    "targets/research/natural_language.nomi",
    "targets/research/notation.nomi",
    "targets/research/overall.nomi",
    "targets/research/scientific_model.nomi",
    "targets/research/table_plan.nomi",
    "targets/research/text_boundaries.nomi",
    "targets/research/workflow.nomi",
)


def uncommented_lines(source):
    """Skip wholly commented rejection fixtures; do not interpret Nomi source."""
    return [line for line in source.splitlines() if not line.lstrip().startswith("#")]


def example_level_propagations(source):
    # Current positive examples have no nested func declarations. Only guard
    # their statement-level terminal '?', not all legal expression spellings.
    in_example = False
    violations = []
    for line in uncommented_lines(source):
        if line and not line[0].isspace():
            in_example = line.startswith("example ")
        if in_example and re.search(r"\?\s*(?:#.*)?$", line):
            violations.append(line.strip())
    return violations


def test_guard_inventory_covers_active_suite_and_registered_focused_targets():
    discovered = {
        path.relative_to(DESIGN).as_posix()
        for path in (DESIGN / "targets").rglob("*.nomi")
    }
    discovered.update(
        path.relative_to(DESIGN).as_posix() for path in DESIGN.glob("*_target.nomi")
    )
    assert discovered == set(ACTIVE_TARGETS)
    packets = json.loads((ROOT / "config/design_passes.json").read_text())["passes"]
    for packet in packets:
        target = Path(packet["artifacts"]["target"]).relative_to("docs/design")
        assert target.as_posix() in ACTIVE_TARGETS
    assert "target.nomi" not in ACTIVE_TARGETS  # Superseded historical fixture.


@pytest.mark.parametrize("target", ACTIVE_TARGETS)
def test_active_positive_fixtures_keep_direct_match_arms(target):
    lines = uncommented_lines((DESIGN / target).read_text(encoding="utf-8"))
    assert not any(re.match(r"\s*case\s+", line) for line in lines), target


@pytest.mark.parametrize("target", ACTIVE_TARGETS)
def test_positive_examples_do_not_invent_function_propagation(target):
    source = (DESIGN / target).read_text(encoding="utf-8")
    assert example_level_propagations(source) == [], target


def test_guard_distinguishes_commented_negative_cases_and_function_propagation():
    source = (
        "# case Ok(value):\n"
        "func checked() -> Result[Int, Error]:\n"
        "    value = operation()?\n"
        "    return Ok(value)\n"
        'example "explicit result handling":\n'
        "    # rejected = operation()?\n"
        "    check operation() == Ok(1)\n"
    )
    assert not any(re.match(r"\s*case\s+", line) for line in uncommented_lines(source))
    assert example_level_propagations(source) == []
    assert example_level_propagations('example "invalid":\n    value = operation()?\n')


def test_linguistic_role_example_uses_named_product_fields():
    source = (DESIGN / "targets/research/natural_language.nomi").read_text()
    for product in ("ReportId", "RecipientId"):
        calls = re.findall(rf"\b{product}\(([^)]*)\)", source)
        assert calls and all(call.startswith("value=") for call in calls)


def test_workflow_candidate_names_multi_field_construction_roles():
    source = (DESIGN / "targets/research/workflow.nomi").read_text()
    assert (
        "PublicationObservation.Uncertain(operation_key=key, attempt=attempt)" in source
    )
    bundle = (DESIGN / "targets/research/domain_layers.nomi").read_text()
    assert "Bundle(report=report, training=training, workflow=checked)" in bundle
    assert "fields are proposed facade metadata" in bundle


def test_interchange_patterns_and_text_fixture_use_the_declared_value_variants():
    source = (DESIGN / "pattern_matching.md").read_text()
    for version in (1, 2):
        assert f'Value.Map({{"version": Value.Number({version}), ..}})' in source
        assert f'Value.Map({{"version": {version}, ..}})' not in source
    text_fixture = (DESIGN / "targets/research/text_boundaries.nomi").read_text()
    assert '"port": Value.Number(config.port)' in text_fixture
    assert '"message": Value.Text(config.message)' in text_fixture
    assert "value = Value.Map({" in text_fixture
    assert not re.search(r"\bValue\.(?:object|text|int)\(", text_fixture)


@pytest.mark.parametrize(
    ("target", "required_imports"),
    [
        ("function_contracts_target.nomi", ["Network"]),
        ("interaction_model_target.nomi", ["DecodeErrors", "Value"]),
        (
            "targets/research/generic_operations.nomi",
            ["ConsoleWrite", "FileRead", "FileWrite"],
        ),
    ],
)
def test_selected_nonprelude_contract_names_are_explicitly_imported(
    target, required_imports
):
    source = (DESIGN / target).read_text()
    imported = set()
    for names in re.findall(r"^from [\w.]+ import ([^\n]+)$", source, re.MULTILINE):
        imported.update(name.strip() for name in names.split(","))
    assert set(required_imports) <= imported
