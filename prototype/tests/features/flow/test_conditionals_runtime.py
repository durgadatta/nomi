from prototype.interpreter.helpers import get_run_eval_loop


# ── unless statement ─────────────────────────────────────────────────

def test_unless_executes_when_condition_false(nomi_mode):
    run = get_run_eval_loop(nomi_mode)
    bindings = run(code="\n".join([
        "x = 5",
        "result = 'unchanged'",
        "unless x > 10:",
        "    result = 'body-ran'",
        "",
    ]))
    assert bindings["result"] == "body-ran"


def test_unless_skips_when_condition_true(nomi_mode):
    run = get_run_eval_loop(nomi_mode)
    bindings = run(code="\n".join([
        "x = 15",
        "result = 'unchanged'",
        "unless x > 10:",
        "    result = 'body-ran'",
        "",
    ]))
    assert bindings["result"] == "unchanged"


def test_unless_with_truthy_condition_skips(nomi_mode):
    run = get_run_eval_loop(nomi_mode)
    bindings = run(code="\n".join([
        "result = 'unchanged'",
        "unless True:",
        "    result = 'body-ran'",
        "",
    ]))
    assert bindings["result"] == "unchanged"


def test_unless_with_falsy_condition_executes(nomi_mode):
    run = get_run_eval_loop(nomi_mode)
    bindings = run(code="\n".join([
        "result = 'unchanged'",
        "unless False:",
        "    result = 'body-ran'",
        "",
    ]))
    assert bindings["result"] == "body-ran"


def test_unless_multi_line_body(nomi_mode):
    run = get_run_eval_loop(nomi_mode)
    bindings = run(code="\n".join([
        "counter = 0",
        "unless True:",
        "    a = 1",
        "    b = 2",
        "    counter = a + b",
        "",
    ]))
    assert bindings["counter"] == 0


def test_unless_nested(nomi_mode):
    run = get_run_eval_loop(nomi_mode)
    bindings = run(code="\n".join([
        "result = 'none'",
        "x = 5",
        "unless x > 10:",
        "    y = 3",
        "    unless y > 5:",
        "        result = 'inner'",
        "",
    ]))
    assert bindings["result"] == "inner"


# ── postfix return/flow if ───────────────────────────────────────────

def test_postfix_return_if_true(nomi_mode):
    run = get_run_eval_loop(nomi_mode)
    bindings = run(code="\n".join([
        "func early(flag):",
        "    return 'yes' if flag",
        "    return 'no'",
        "result = early(True)",
        "",
    ]))
    assert bindings["result"] == "yes"


def test_postfix_return_if_false_falls_through(nomi_mode):
    run = get_run_eval_loop(nomi_mode)
    bindings = run(code="\n".join([
        "func early(flag):",
        "    return 'yes' if flag",
        "    return 'no'",
        "result = early(False)",
        "",
    ]))
    assert bindings["result"] == "no"


def test_postfix_return_if_with_expression(nomi_mode):
    run = get_run_eval_loop(nomi_mode)
    bindings = run(code="\n".join([
        "func check(n):",
        "    return 'big' if n > 100",
        "    return 'small'",
        "result1 = check(200)",
        "result2 = check(50)",
        "",
    ]))
    assert bindings["result1"] == "big"
    assert bindings["result2"] == "small"


# ── postfix return/flow unless ───────────────────────────────────────

def test_postfix_return_unless_true_skips(nomi_mode):
    run = get_run_eval_loop(nomi_mode)
    bindings = run(code="\n".join([
        "func early(flag):",
        "    return 'yes' unless flag",
        "    return 'no'",
        "result = early(True)",
        "",
    ]))
    assert bindings["result"] == "no"


def test_postfix_return_unless_false_returns(nomi_mode):
    run = get_run_eval_loop(nomi_mode)
    bindings = run(code="\n".join([
        "func early(flag):",
        "    return 'yes' unless flag",
        "    return 'no'",
        "result = early(False)",
        "",
    ]))
    assert bindings["result"] == "yes"


def test_postfix_return_unless_with_expression(nomi_mode):
    run = get_run_eval_loop(nomi_mode)
    bindings = run(code="\n".join([
        "func check(n):",
        "    return 'small' unless n > 100",
        "    return 'big'",
        "result1 = check(200)",
        "result2 = check(50)",
        "",
    ]))
    assert bindings["result1"] == "big"
    assert bindings["result2"] == "small"


# ── postfix raise if/unless ──────────────────────────────────────────

def test_postfix_raise_if(nomi_mode):
    run = get_run_eval_loop(nomi_mode)
    bindings = run(code="\n".join([
        "func validate(n):",
        "    raise ValueError('bad') if n < 0",
        "    return 'ok'",
        "result = 'ok'",
        "try:",
        "    result = validate(5)",
        "except ValueError:",
        "    result = 'error'",
        "",
    ]))
    assert bindings["result"] == "ok"


def test_postfix_raise_unless(nomi_mode):
    run = get_run_eval_loop(nomi_mode)
    bindings = run(code="\n".join([
        "func validate(n):",
        "    raise ValueError('bad') unless n >= 0",
        "    return 'ok'",
        "result = 'ok'",
        "try:",
        "    result = validate(-5)",
        "except ValueError:",
        "    result = 'error'",
        "",
    ]))
    assert bindings["result"] == "error"
