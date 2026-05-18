from prototype.syntax.features import ALLOWED_LAYERS, BUILTIN_FEATURES, SUGAR_LAYER


def test_builtin_features_declare_core_layer_metadata():
    for feature in BUILTIN_FEATURES:
        assert feature.layer in ALLOWED_LAYERS, (
            f"{feature.name} must declare one of {ALLOWED_LAYERS}"
        )


def test_sugar_features_declare_reduction_targets_without_permanent_eval_hooks():
    sugar_features = [feature for feature in BUILTIN_FEATURES if feature.layer == SUGAR_LAYER]

    assert sugar_features
    for feature in sugar_features:
        assert feature.reduces_to, f"{feature.name} must declare what it reduces to"
        assert feature.runtime_hooks_allowed in {"none", "temporary"}, (
            f"{feature.name} is L4 sugar and must not claim permanent eval semantics"
        )


def test_semantic_surface_features_declare_semantic_forms():
    for feature in BUILTIN_FEATURES:
        if feature.layer in {"L2", "L3"}:
            assert feature.semantic_forms, (
                f"{feature.name} must declare the semantic core concepts it exposes"
            )
