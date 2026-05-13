from prototype.interpreter.helpers import get_run_eval_loop


# ── match guards and sequence patterns ───────────────────────────────

def test_match_guard_in_statement(nomi_mode):
    run = get_run_eval_loop(nomi_mode)
    bindings = run(code="\n".join([
        "result = 'none'",
        "match 42:",
        "    case n if n > 100: result = 'big'",
        "    case n if n > 0: result = 'small'",
        "    case _: result = 'zero'",
        "",
    ]))
    assert bindings["result"] == "small"


def test_match_guard_falls_through(nomi_mode):
    run = get_run_eval_loop(nomi_mode)
    bindings = run(code="\n".join([
        "result = 'none'",
        "match -1:",
        "    case n if n > 100: result = 'big'",
        "    case n if n > 0: result = 'small'",
        "    case _: result = 'zero'",
        "",
    ]))
    assert bindings["result"] == "zero"


def test_sequence_star_pattern_captures_rest(nomi_mode):
    run = get_run_eval_loop(nomi_mode)
    bindings = run(
        code=(
            "match [1, 2, 3, 4]:\n"
            "    case [head, *middle, tail]:\n"
            "        result = [head, middle, tail]\n"
            "    case _:\n"
            "        result = 'no'\n"
        )
    )
    assert bindings["result"] == [1, [2, 3], 4]


# ── if-let / while-let ───────────────────────────────────────────────

def test_if_let_literal_match(nomi_mode):
    run = get_run_eval_loop(nomi_mode)
    bindings = run(code="x = 42\nresult = 'none'\nif 42 = x:\n    result = 'yes'\n")
    assert bindings["result"] == "yes"


def test_if_let_literal_no_match(nomi_mode):
    run = get_run_eval_loop(nomi_mode)
    bindings = run(code="x = 5\nresult = 'none'\nif 42 = x:\n    result = 'yes'\n")
    assert bindings["result"] == "none"


def test_if_let_with_else(nomi_mode):
    run = get_run_eval_loop(nomi_mode)
    bindings = run(code="x = 5\nresult = 'none'\nif 42 = x:\n    result = 'yes'\nelse:\n    result = 'no'\n")
    assert bindings["result"] == "no"


def test_if_let_capture(nomi_mode):
    run = get_run_eval_loop(nomi_mode)
    bindings = run(code="x = 99\nresult = 'none'\nif val = x:\n    result = val\n")
    assert bindings["result"] == 99


def test_while_let_sequence_consumes_until_no_match(nomi_mode):
    run = get_run_eval_loop(nomi_mode)
    bindings = run(
        code=(
            "items = [1, 2, 3]\n"
            "total = 0\n"
            "while [head, *tail] = items:\n"
            "    total += head\n"
            "    items = tail\n"
        )
    )
    assert bindings["total"] == 6
    assert bindings["items"] == []


def test_while_let_no_initial_match_skips_body(nomi_mode):
    run = get_run_eval_loop(nomi_mode)
    bindings = run(
        code=(
            "items = []\n"
            "result = 'skipped'\n"
            "while [head, *tail] = items:\n"
            "    result = head\n"
        )
    )
    assert bindings["result"] == "skipped"


def test_guard_let_binds_on_match_and_continues(nomi_mode):
    run = get_run_eval_loop(nomi_mode)
    bindings = run(
        code=(
            "guard [head, *tail] = [1, 2, 3]:\n"
            "    result = 'failed'\n"
            "result = [head, tail]\n"
        )
    )
    assert bindings["result"] == [1, [2, 3]]


def test_guard_let_runs_body_on_no_match(nomi_mode):
    run = get_run_eval_loop(nomi_mode)
    bindings = run(
        code=(
            "result = 'start'\n"
            "guard [head, *tail] = []:\n"
            "    result = 'empty'\n"
        )
    )
    assert bindings["result"] == "empty"


def test_guard_let_can_return_from_function_on_no_match(nomi_mode):
    run = get_run_eval_loop(nomi_mode)
    bindings = run(
        code=(
            "func first(items):\n"
            "    guard [head, *tail] = items:\n"
            "        return 'empty'\n"
            "    return head\n"
            "r1 = first([10, 20])\n"
            "r2 = first([])\n"
        )
    )
    assert bindings["r1"] == 10
    assert bindings["r2"] == "empty"


# ── match as expression ──────────────────────────────────────────────

def test_inline_match_expr_assignment(nomi_mode):
    run = get_run_eval_loop(nomi_mode)
    bindings = run(code="result = match 2: case 1 => 'one'; case 2 => 'two'; case _ => 'many'\n")
    assert bindings["result"] == "two"


def test_inline_match_expr_return(nomi_mode):
    run = get_run_eval_loop(nomi_mode)
    bindings = run(
        code=(
            "func describe(n):\n"
            "    return match n: case 0 => 'zero'; case _ => 'nonzero'\n"
            "result = describe(5)\n"
        )
    )
    assert bindings["result"] == "nonzero"


def test_inline_match_expr_argument(nomi_mode):
    run = get_run_eval_loop(nomi_mode)
    bindings = run(code="result = len(match 1: case 1 => 'one'; case _ => 'many')\n")
    assert bindings["result"] == 3


def test_inline_match_expr_capture_and_guard(nomi_mode):
    run = get_run_eval_loop(nomi_mode)
    bindings = run(code="result = match 4: case n if n > 3 => n * 10; case _ => 0\n")
    assert bindings["result"] == 40


def test_indented_match_expr_assignment(nomi_mode):
    run = get_run_eval_loop(nomi_mode)
    bindings = run(
        code=(
            "result = match 2:\n"
            "    case 1: 'one'\n"
            "    case 2: 'two'\n"
            "    case _: 'many'\n"
        )
    )
    assert bindings["result"] == "two"


def test_indented_match_expr_return(nomi_mode):
    run = get_run_eval_loop(nomi_mode)
    bindings = run(
        code=(
            "func describe(n):\n"
            "    return match n:\n"
            "        case 0: 'zero'\n"
            "        case _: 'nonzero'\n"
            "result = describe(5)\n"
        )
    )
    assert bindings["result"] == "nonzero"


def test_indented_match_expr_capture_and_guard(nomi_mode):
    run = get_run_eval_loop(nomi_mode)
    bindings = run(
        code=(
            "result = match 4:\n"
            "    case n if n > 3: n * 10\n"
            "    case _: 0\n"
        )
    )
    assert bindings["result"] == 40


def test_indented_match_expr_nested_inline_match_value(nomi_mode):
    run = get_run_eval_loop(nomi_mode)
    bindings = run(
        code=(
            "result = match 'json':\n"
            "    case 'json': match 200: case 200 => 'ok'; case _ => 'bad'\n"
            "    case _: 'unknown'\n"
        )
    )
    assert bindings["result"] == "ok"


def test_indented_match_expr_nested_indented_match_value(nomi_mode):
    run = get_run_eval_loop(nomi_mode)
    bindings = run(
        code=(
            "result = match 'json':\n"
            "    case 'json': match 200:\n"
            "        case 200: 'ok'\n"
            "        case _: 'bad'\n"
            "    case _: 'unknown'\n"
        )
    )
    assert bindings["result"] == "ok"
