from prototype.interpreter.helpers import get_run_eval_loop


def test_underscore_assignment_and_read_at_runtime(interpreter_mode):
    run_eval_loop = get_run_eval_loop(interpreter_mode)
    bindings = run_eval_loop(code="_ = 3\nvalue = _ + 4\n")

    assert bindings["_"] == 3
    assert bindings["value"] == 7


def test_underscore_loop_target_binds_like_regular_name_at_runtime(interpreter_mode):
    run_eval_loop = get_run_eval_loop(interpreter_mode)
    bindings = run_eval_loop(code="total = 0\nfor _ in range(3):\n    total += _\n")

    assert bindings["_"] == 2
    assert bindings["total"] == 3


def test_single_underscore_match_wildcard_does_not_rebind_runtime_name(interpreter_mode):
    run_eval_loop = get_run_eval_loop(interpreter_mode)
    bindings = run_eval_loop(code="_ = 'sentinel'\nmatch 10:\n    case _:\n        value = _\n")

    assert bindings["_"] == "sentinel"
    assert bindings["value"] == "sentinel"


def test_double_underscore_match_capture_binds_runtime_name(interpreter_mode):
    run_eval_loop = get_run_eval_loop(interpreter_mode)
    bindings = run_eval_loop(code="match 10:\n    case __:\n        value = __\n")

    assert bindings["__"] == 10
    assert bindings["value"] == 10
