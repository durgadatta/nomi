import pytest

from prototype.interpreter.helpers import INTERPRETER_MODES, get_run_eval_loop
from prototype.runtime.modes import MODE_SPECS, get_mode_spec


def test_mode_specs_cover_public_interpreter_modes():
    assert INTERPRETER_MODES == ("python", "nomi", "reduced")
    assert tuple(MODE_SPECS) == INTERPRETER_MODES


def test_mode_spec_describes_current_nomi_pipeline():
    spec = get_mode_spec("nomi")

    assert spec.runner_module == "prototype.interpreter.nomi.usage"
    assert spec.parser == "prototype.parser.nomi.usage.generate_ast"
    assert spec.interpreter == "prototype.interpreter.nomi.interpreter.Interpreter"
    assert (
        spec.session_lowerer
        == "prototype.parser.nomi.desugar.pipeline.desugar_module_for_nomi_interpreter"
    )


def test_legacy_helper_uses_mode_registry():
    run = get_run_eval_loop("reduced")
    bindings = run(code="x = 2 + 3\n")

    assert bindings["x"] == 5


def test_unknown_mode_has_clear_error():
    with pytest.raises(ValueError, match="Unknown interpreter mode"):
        get_mode_spec("missing")
