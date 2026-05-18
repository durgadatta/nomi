import pytest

from prototype.syntax.features import (
    ALLOWED_DESUGAR_PROFILES,
    BUILTIN_FEATURES,
    DEFAULT_DESUGAR_PROFILE,
    REDUCED_DESUGAR_PROFILE,
    SUGAR_LAYER,
    get_desugar_passes,
)
from prototype.utils import resolve_dotted


def test_desugar_pass_profiles_are_declared_manifest_data():
    for feature in BUILTIN_FEATURES:
        unknown = set(feature.desugar_profiles) - set(ALLOWED_DESUGAR_PROFILES)
        assert not unknown, (
            f"{feature.name} declares unknown desugar profile(s): {unknown}"
        )

        if feature.desugar_passes:
            assert feature.layer == SUGAR_LAYER
            assert REDUCED_DESUGAR_PROFILE in feature.desugar_profiles


def test_default_desugar_profile_is_manifest_derived():
    default_passes = get_desugar_passes(profile=DEFAULT_DESUGAR_PROFILE)

    assert [pass_cls.__name__ for pass_cls in default_passes] == [
        "PiecewiseFunction",
        "WhereClause",
        "UnderscoreLambda",
        "PositionalHole",
    ]


def test_reduced_desugar_profile_includes_all_declared_passes():
    all_passes = get_desugar_passes()
    reduced_passes = get_desugar_passes(profile=REDUCED_DESUGAR_PROFILE)

    assert reduced_passes == all_passes


def test_get_desugar_passes_rejects_unknown_profile():
    with pytest.raises(ValueError, match="Unknown desugar profile"):
        get_desugar_passes(profile="lab")


def test_conditional_flow_sugar_is_manifested():
    features = {feature.name: feature for feature in BUILTIN_FEATURES}

    unless_feature = features["unless-lowering"]
    assert unless_feature.layer == SUGAR_LAYER
    assert unless_feature.reduces_to == ("branch", "boolean-negation")

    postfix_feature = features["postfix-conditionals-lowering"]
    assert postfix_feature.layer == SUGAR_LAYER
    assert postfix_feature.reduces_to == ("branch",)


def test_declared_desugar_passes_resolve():
    for feature in BUILTIN_FEATURES:
        for ref in feature.desugar_passes:
            assert resolve_dotted(ref) in get_desugar_passes()
