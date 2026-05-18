"""End-to-end tests for all function definition styles."""

from prototype.interpreter.helpers import get_run_eval_loop


# ═══════════════════════════════════════════════════════════════════
# New features
# ═══════════════════════════════════════════════════════════════════

# ── spread in literals ───────────────────────────────────────────────

def test_spread_list(nomi_mode):
    run = get_run_eval_loop(nomi_mode)
    bindings = run(code="a = [1, 2]\nresult = [0, *a, 3]\n")
    assert bindings["result"] == [0, 1, 2, 3]


def test_spread_tuple(nomi_mode):
    run = get_run_eval_loop(nomi_mode)
    bindings = run(code="a = (3, 4)\nresult = (1, 2, *a)\n")
    assert bindings["result"] == (1, 2, 3, 4)


# ── defer ────────────────────────────────────────────────────────────

def test_defer_basic(nomi_mode):
    run = get_run_eval_loop(nomi_mode)
    bindings = run(code="func test():\n    defer x = 1\n    x = 2\n    return x\nresult = test()\n")
    assert bindings["result"] == 2


def test_defer_lifo_order(nomi_mode):
    run = get_run_eval_loop(nomi_mode)
    bindings = run(code="result = []\nfunc test():\n    defer result.append('third')\n    defer result.append('second')\n    result.append('first')\ntest()\n")
    assert bindings["result"] == ["first", "second", "third"]


def test_defer_with_return(nomi_mode):
    run = get_run_eval_loop(nomi_mode)
    bindings = run(code="func test():\n    defer x = 1\n    return 99\nresult = test()\n")
    assert bindings["result"] == 99
