import subprocess
import sys
from dataclasses import FrozenInstanceError, replace
from pathlib import Path

import pytest

from prototype.runtime import InspectionResult, inspect
from prototype.syntax import features as registry
from prototype.syntax.features import (
    BUILTIN_FEATURES,
    SyntaxFeature,
    TargetDirection,
    get_feature_capabilities,
    render_feature_target_table,
)

RETIRED_SOURCE_FEATURES = {
    "piecewise-functions",
    "where-clauses",
    "underscore-lambdas",
    "positional-holes",
    "aug-assign-desugar",
    "decorator-desugar",
    "unless-lowering",
    "postfix-conditionals-lowering",
    "implicit-multiplication",
    "range-expressions",
    "if-let-lowering",
    "try-expr-lowering",
    "where-clause-lowering",
    "positional-hole-lowering",
    "compose-lowering",
    "func-equation-lowering",
    "sections-lowering",
    "block-call-lowering",
}


def test_rejected_target_forms_keep_their_current_runtime_coverage():
    by_name = {feature.name: feature for feature in BUILTIN_FEATURES}
    assert RETIRED_SOURCE_FEATURES <= by_name.keys()
    for name in RETIRED_SOURCE_FEATURES:
        feature = by_name[name]
        assert feature.target_direction.disposition == "retire", name
        assert feature.status == "implemented", name
        assert get_feature_capabilities(feature).run, name


def test_conformance_is_not_inferred_from_a_retained_target_concept():
    by_name = {feature.name: feature for feature in BUILTIN_FEATURES}
    fragment = by_name["pattern-surface-schema"]
    assert fragment.target_direction.disposition == "retain"
    assert get_feature_capabilities(fragment).parse
    assert not get_feature_capabilities(fragment).run
    assert by_name["match-expr-lowering"].target_direction.disposition == "rework"
    assert by_name["defer-lowering"].target_direction.disposition == "rework"
    assert (
        by_name["collection-table-rank-integration"].target_direction.disposition
        == "open"
    )


def test_target_directions_link_existing_canonical_design_contracts():
    for feature in BUILTIN_FEATURES:
        target = feature.target_direction
        if target is not None:
            assert Path(target.contract.split("#", 1)[0]).is_file(), feature.name
            assert target.normal_form.strip(), feature.name
            assert target.reason.strip(), feature.name


def test_absent_direction_is_unreviewed_not_accepted():
    feature = SyntaxFeature(name="unclassified", description="fixture")
    table = render_feature_target_table([feature])
    assert "| unclassified | implemented | unreviewed | - | - |" in table
    assert "No target direction recorded." in table


def test_an_explicit_empty_feature_list_stays_empty():
    table = render_feature_target_table([])
    assert len(table.splitlines()) == 2
    assert "piecewise-functions" not in table


def test_target_direction_is_immutable():
    direction = TargetDirection(
        "retain", "docs/design/syntax.md", "ordinary call", "fixture"
    )
    with pytest.raises(FrozenInstanceError):
        direction.disposition = "retire"


def test_normal_form_punctuation_and_multiline_notes_keep_table_structure():
    direction = TargetDirection(
        "retain", "docs/design/syntax.md", "value |> f()", "first line\nsecond line"
    )
    feature = SyntaxFeature(
        name="fixture", description="fixture", target_direction=direction
    )
    table = render_feature_target_table([feature])
    assert len(table.splitlines()) == 3
    assert "value \\|> f()" in table
    assert "first line<br>second line" in table


@pytest.mark.parametrize("disposition", ["accepted", "implemented", "", "unknown"])
def test_invalid_target_direction_is_rejected(disposition):
    with pytest.raises(ValueError, match="Unknown target disposition"):
        TargetDirection(
            disposition=disposition,
            contract="docs/design/syntax.md",
            normal_form="ordinary call",
            reason="fixture",
        )


@pytest.mark.parametrize("field", ["contract", "normal_form", "reason"])
@pytest.mark.parametrize("missing", ["", "  ", None])
def test_target_direction_requires_a_contract_and_explanation(field, missing):
    values = {
        "disposition": "retain",
        "contract": "docs/design/syntax.md",
        "normal_form": "ordinary call",
        "reason": "fixture",
    }
    values[field] = missing
    with pytest.raises(ValueError, match="must be non-empty text"):
        TargetDirection(**values)


@pytest.mark.parametrize(
    "contract",
    [
        "docs/research/families.md",
        "/tmp/design.md",
        "docs/design/../../README.md",
        "docs/design/schemas/pattern_surface.schema.json",
    ],
)
def test_target_direction_cannot_treat_evidence_or_host_paths_as_authority(contract):
    with pytest.raises(ValueError, match="docs/design Markdown path"):
        TargetDirection("retain", contract, "ordinary call", "fixture")


def test_target_direction_does_not_select_grammar_lowering_or_desugar(monkeypatch):
    def selected():
        return (
            registry.get_extra_grammar_layers(),
            registry.get_lowering_mixins(),
            registry.get_desugar_passes("default"),
            registry.get_desugar_passes("reduced"),
            [type(item) for item in registry.get_layer_transforms()],
            registry.get_declared_soft_keywords(),
            [get_feature_capabilities(item) for item in registry.BUILTIN_FEATURES],
        )

    before = selected()
    direction = TargetDirection(
        "retire", "docs/design/decisions.md", "fixture", "fixture"
    )
    changed = [replace(item, target_direction=direction) for item in BUILTIN_FEATURES]
    monkeypatch.setattr(registry, "BUILTIN_FEATURES", changed)
    assert selected() == before


@pytest.mark.parametrize("stage", ["target_alignment", "target-alignment"])
def test_runtime_inspection_needs_no_source_parsing_or_execution(stage):
    result = inspect(stage=stage, source="not valid Nomi source (((")
    assert isinstance(result, InspectionResult)
    assert result.output == render_feature_target_table()
    assert "| piecewise-functions | implemented | retire |" in result.output
    assert result.stage == stage
    assert result.timings["total"] >= 0


def test_cli_target_inspection_uses_the_same_feature_metadata():
    completed = subprocess.run(
        [sys.executable, "-m", "tools.syntax.inspect", "--stage", "target-alignment"],
        text=True,
        capture_output=True,
        check=True,
    )
    assert completed.stdout.rstrip() == render_feature_target_table()
