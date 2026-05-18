"""End-to-end tests for all function definition styles."""

from prototype.interpreter.helpers import get_run_eval_loop


# ═══════════════════════════════════════════════════════════════════
# New features
# ═══════════════════════════════════════════════════════════════════

# ── implicit multiplication ─────────────────────────────────────────

def test_implicit_mul_name(nomi_mode):
    run = get_run_eval_loop(nomi_mode)
    bindings = run(code="x = 5\nresult = 2x + 1\n")
    assert bindings["result"] == 11


def test_implicit_mul_float(nomi_mode):
    run = get_run_eval_loop(nomi_mode)
    bindings = run(code="r = 2\nresult = 3.14r + 1\n")
    assert abs(bindings["result"] - 7.28) < 0.01


def test_implicit_mul_power_binds_tighter(nomi_mode):
    run = get_run_eval_loop(nomi_mode)
    bindings = run(code="x = 3\nresult = 2x**2\n")
    assert bindings["result"] == 18  # 2 * 9, not (2*3)**2 = 36


def test_implicit_mul_parens(nomi_mode):
    run = get_run_eval_loop(nomi_mode)
    bindings = run(code="x = 3\ny = 4\nresult = 2(x + y)\n")
    assert bindings["result"] == 14  # 2 * 7


def test_implicit_mul_negation(nomi_mode):
    run = get_run_eval_loop(nomi_mode)
    bindings = run(code="x = 5\nresult = -2x\n")
    assert bindings["result"] == -10


def test_implicit_mul_no_break_regular(nomi_mode):
    run = get_run_eval_loop(nomi_mode)
    bindings = run(code="result = x + y where:\n    x = 10\n    y = 20\n")
    assert bindings["result"] == 30


# ── type aliases ────────────────────────────────────────────────────

def test_type_alias_basic(nomi_mode):
    run = get_run_eval_loop(nomi_mode)
    bindings = run(code="type UserId = str\n")
    assert bindings["UserId"] == str


def test_type_alias_multiple(nomi_mode):
    run = get_run_eval_loop(nomi_mode)
    bindings = run(code="type Age = int\ntype Name = str\nresult = Name('hello') + ' ' + str(Age(42))\n")
    assert bindings["result"] == "hello 42"


# ── try as expression ────────────────────────────────────────────────

def test_try_expr_success(nomi_mode):
    run = get_run_eval_loop(nomi_mode)
    bindings = run(code="result = try 42 except ValueError: 0\n")
    assert bindings["result"] == 42


def test_try_expr_catch(nomi_mode):
    run = get_run_eval_loop(nomi_mode)
    bindings = run(code="result = try int('abc') except ValueError: 0\n")
    assert bindings["result"] == 0


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
