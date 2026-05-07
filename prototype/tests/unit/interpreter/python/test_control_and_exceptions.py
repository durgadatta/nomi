from prototype.interpreter.python.usage import run_eval_loop


def test_if_elif_else_selects_matching_branch():
    bindings = run_eval_loop(
        code=(
            "value = 2\n"
            "if value == 1:\n"
            "    result = 'one'\n"
            "elif value == 2:\n"
            "    result = 'two'\n"
            "else:\n"
            "    result = 'other'\n"
        )
    )

    assert bindings["result"] == "two"


def test_for_loop_continue_and_else():
    bindings = run_eval_loop(
        code=(
            "total = 0\n"
            "for i in range(5):\n"
            "    if i == 3:\n"
            "        continue\n"
            "    total += i\n"
            "else:\n"
            "    finished = True\n"
        )
    )

    assert bindings["total"] == 7
    assert bindings["finished"] is True


def test_for_loop_break_skips_else():
    bindings = run_eval_loop(
        code=(
            "seen_else = False\n"
            "for i in range(5):\n"
            "    if i == 2:\n"
            "        break\n"
            "else:\n"
            "    seen_else = True\n"
        )
    )

    assert bindings["i"] == 2
    assert bindings["seen_else"] is False


def test_while_loop_runs_until_condition_false():
    bindings = run_eval_loop(code="i = 0\ntotal = 0\nwhile i < 3:\n    total += i\n    i += 1\n")

    assert bindings["i"] == 3
    assert bindings["total"] == 3


def test_try_except_finally_handles_exception_and_runs_cleanup():
    bindings = run_eval_loop(
        code=(
            "try:\n"
            "    1 / 0\n"
            "except ZeroDivisionError as exc:\n"
            "    handled = isinstance(exc, ZeroDivisionError)\n"
            "finally:\n"
            "    cleaned = True\n"
        )
    )

    assert bindings["handled"] is True
    assert bindings["cleaned"] is True
