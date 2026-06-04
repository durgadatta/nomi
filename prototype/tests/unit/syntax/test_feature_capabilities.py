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


def test_builtin_feature_capabilities_have_separate_axes():
    feature_by_name = {feature.name: feature for feature in BUILTIN_FEATURES}

    piecewise = get_feature_capabilities(feature_by_name["piecewise-functions"])
    block_call = get_feature_capabilities(feature_by_name["block-call-lowering"])

    assert isinstance(piecewise, FeatureCapabilityAxes)
    assert piecewise.parse
    assert piecewise.lower
    assert piecewise.run
    assert piecewise.reduce
    assert piecewise.docs
    assert piecewise.tests

    assert block_call.parse
    assert block_call.lower
    assert block_call.run
    assert block_call.docs
    assert feature_by_name["piecewise-functions"].coverage == piecewise
    assert feature_by_name["block-call-lowering"].coverage == block_call


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
    assert "| piecewise-functions | no | yes | yes | yes | yes | no | yes | yes |" in table
    assert "| block-call-lowering | no | yes | yes | yes | yes | no | yes | yes |" in table


def test_feature_declared_docs_and_tests_exist():
    for feature in BUILTIN_FEATURES:
        for doc_path in feature.docs:
            assert Path(doc_path).exists(), f"{feature.name} doc missing: {doc_path}"
        for test_path in feature.tests:
            assert Path(test_path).exists(), f"{feature.name} test missing: {test_path}"
