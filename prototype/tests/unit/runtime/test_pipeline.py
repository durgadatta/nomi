import pytest

from prototype.runtime import PipelineSpec, build_pipeline_spec


def test_build_pipeline_spec_resolves_mode_metadata():
    spec = build_pipeline_spec(mode="reduced")

    assert isinstance(spec, PipelineSpec)
    assert spec.mode == "reduced"
    assert spec.profile == "default"
    assert spec.host == "python"
    assert spec.parser == "prototype.parser.nomi.usage.generate_ast"
    assert spec.lowering == "prototype.parser.nomi.desugar.pipeline.desugar_module"


def test_pipeline_spec_rejects_unknown_profile():
    with pytest.raises(ValueError, match="Unsupported runtime profile"):
        build_pipeline_spec(profile="lab")
