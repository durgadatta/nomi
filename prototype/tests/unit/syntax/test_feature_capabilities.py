from pathlib import Path

from prototype.syntax.features import (
    BUILTIN_FEATURES,
    FeatureCapabilityAxes,
    get_feature_capabilities,
    render_feature_capability_table,
)


FEATURES_REQUIRING_EXPLICIT_COVERAGE = {
    "piecewise-functions",
    "where-clauses",
    "underscore-lambdas",
    "positional-holes",
    "unless-lowering",
    "postfix-conditionals-lowering",
    "implicit-multiplication",
    "type-alias-lowering",
    "range-expressions",
    "if-let-lowering",
    "try-expr-lowering",
    "match-expr-lowering",
    "where-clause-lowering",
    "positional-hole-lowering",
    "compose-lowering",
    "defer-lowering",
    "func-equation-lowering",
    "sections-lowering",
    "func-expr-lowering",
    "block-call-lowering",
    "data-decl-lowering",
}

TARGET_ONLY_INTEGRATION_PACKETS = {
    "binding-data-pattern-integration",
    "collection-table-rank-integration",
    "block-policy-prelude",
}


def test_builtin_feature_capabilities_have_separate_axes():
    feature_by_name = {feature.name: feature for feature in BUILTIN_FEATURES}

    piecewise = get_feature_capabilities(feature_by_name["piecewise-functions"])
    implicit_mul = get_feature_capabilities(feature_by_name["implicit-multiplication"])
    block_call = get_feature_capabilities(feature_by_name["block-call-lowering"])

    assert isinstance(piecewise, FeatureCapabilityAxes)
    assert piecewise.parse
    assert piecewise.lower
    assert piecewise.run
    assert piecewise.reduce
    assert piecewise.docs
    assert piecewise.tests
    assert piecewise.samples
    assert not implicit_mul.samples

    assert block_call.parse
    assert block_call.lower
    assert block_call.run
    assert block_call.docs
    assert feature_by_name["piecewise-functions"].coverage is not None
    assert feature_by_name["block-call-lowering"].coverage is not None


def test_user_facing_features_declare_explicit_capabilities():
    feature_by_name = {feature.name: feature for feature in BUILTIN_FEATURES}

    assert FEATURES_REQUIRING_EXPLICIT_COVERAGE <= set(feature_by_name)
    for name in FEATURES_REQUIRING_EXPLICIT_COVERAGE:
        feature = feature_by_name[name]
        assert feature.coverage is not None, name
        assert feature.coverage.parse, name
        assert feature.coverage.lower, name
        assert feature.coverage.run, name
        assert feature.coverage.reduce, name


def test_integration_packets_are_target_only_capability_rows():
    feature_by_name = {feature.name: feature for feature in BUILTIN_FEATURES}

    assert TARGET_ONLY_INTEGRATION_PACKETS <= set(feature_by_name)
    for name in TARGET_ONLY_INTEGRATION_PACKETS:
        feature = feature_by_name[name]
        capabilities = get_feature_capabilities(feature)

        assert feature.coverage is not None, name
        assert capabilities.target_only, name
        assert capabilities.docs, name
        assert not capabilities.parse, name
        assert not capabilities.lower, name
        assert not capabilities.run, name
        assert not capabilities.reduce, name
        assert not capabilities.explain, name
        assert not capabilities.web, name
        assert not capabilities.notebook, name


def test_explicit_capabilities_do_not_overstate_explanation_or_frontends():
    feature_by_name = {feature.name: feature for feature in BUILTIN_FEATURES}

    for name in FEATURES_REQUIRING_EXPLICIT_COVERAGE:
        coverage = feature_by_name[name].coverage
        assert coverage is not None
        assert not coverage.explain, name
        assert not coverage.web, name
        assert not coverage.notebook, name


def test_feature_capability_table_is_stable_and_human_readable():
    table = render_feature_capability_table()

    assert table.startswith("| feature | target-only | parse | lower |")
    assert "| piecewise-functions | no | yes | yes | yes | yes | no | yes | yes | yes |" in table
    assert "| block-call-lowering | no | yes | yes | yes | yes | no | yes | yes | yes |" in table
    assert "| binding-data-pattern-integration | yes | no | no | no | no | no | yes | no | no | no | no |" in table
    assert "| collection-table-rank-integration | yes | no | no | no | no | no | yes | no | no | no | no |" in table
    assert "| block-policy-prelude | yes | no | no | no | no | no | yes | no | no | no | no |" in table


def test_feature_declared_docs_and_tests_exist():
    for feature in BUILTIN_FEATURES:
        for doc_path in feature.docs:
            assert Path(doc_path).exists(), f"{feature.name} doc missing: {doc_path}"
        for test_path in feature.tests:
            assert Path(test_path).exists(), f"{feature.name} test missing: {test_path}"


def test_feature_declared_samples_exist_and_drive_sample_axis():
    sampled_features = []
    for feature in BUILTIN_FEATURES:
        capabilities = get_feature_capabilities(feature)
        assert capabilities.samples == bool(feature.sample_files), feature.name
        for sample_path in feature.sample_files:
            sampled_features.append(feature.name)
            assert Path(sample_path).exists(), f"{feature.name} sample missing: {sample_path}"

    assert "piecewise-functions" in sampled_features
    assert "block-call-lowering" in sampled_features
