"""End-to-end tests for all function definition styles."""

from prototype.interpreter.helpers import get_run_eval_loop


# ═══════════════════════════════════════════════════════════════════
# New features
# ═══════════════════════════════════════════════════════════════════

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
