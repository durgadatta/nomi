import pytest

from prototype.runtime import PipelineSpec, build_pipeline_spec


def test_build_pipeline_spec_resolves_mode_metadata():
    spec = build_pipeline_spec(mode="reduced")

    assert isinstance(spec, PipelineSpec)
    assert spec.mode == "reduced"
    assert spec.profile == "default"
    assert spec.host == "python"
    assert spec.parser_frontend == "lark-lalr"
    assert spec.parser == "prototype.parser.nomi.usage.generate_ast"
    assert spec.lowering == "prototype.parser.nomi.desugar.pipeline.desugar_module"


def test_pipeline_spec_rejects_unknown_profile():
    with pytest.raises(ValueError, match="Unsupported runtime profile"):
        build_pipeline_spec(profile="lab")


def test_pipeline_spec_rejects_unknown_parser_frontend():
    with pytest.raises(ValueError, match="Unknown parser frontend"):
        build_pipeline_spec(parser_frontend="missing-parser")


def test_pipeline_spec_can_select_core_runtime_backend():
    spec = build_pipeline_spec(eval_backend="core-runtime")

    assert spec.eval_backend == "core-runtime"


def test_pipeline_spec_can_read_eval_backend_from_environment(monkeypatch):
    monkeypatch.setenv("NOMI_EVAL_BACKEND", "core-runtime")

    spec = build_pipeline_spec()

    assert spec.eval_backend == "core-runtime"
