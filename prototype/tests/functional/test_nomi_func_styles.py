"""End-to-end tests for all function definition styles."""

from prototype.interpreter.helpers import get_run_eval_loop


# ── operator sections ─────────────────────────────────────────────

def test_section_left(nomi_mode):
    run = get_run_eval_loop(nomi_mode)
    bindings = run(code="add2 = (+2)\nresult = add2(5)\n")
    assert bindings["result"] == 7


def test_section_right(nomi_mode):
    run = get_run_eval_loop(nomi_mode)
    bindings = run(code="double = (2*)\nresult = double(5)\n")
    assert bindings["result"] == 10


def test_section_operator_value(nomi_mode):
    run = get_run_eval_loop(nomi_mode)
    bindings = run(code="plus = (+)\nresult = plus(3, 4)\n")
    assert bindings["result"] == 7


def test_section_nested_in_call(nomi_mode):
    run = get_run_eval_loop(nomi_mode)
    bindings = run(code="result = list(map((+2), [1, 2, 3]))\n")
    assert bindings["result"] == [3, 4, 5]


def test_section_regular_parens_still_work(nomi_mode):
    run = get_run_eval_loop(nomi_mode)
    bindings = run(code="result = (3 + 4) * 2\n")
    assert bindings["result"] == 14


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


# ── function composition >>> / <<< ──────────────────────────────────

def test_compose_forward(nomi_mode):
    run = get_run_eval_loop(nomi_mode)
    bindings = run(code="dbl(x) = x * 2\ninc(x) = x + 1\nf = dbl >>> inc\nresult = f(5)\n")
    assert bindings["result"] == 11


def test_compose_backward(nomi_mode):
    run = get_run_eval_loop(nomi_mode)
    bindings = run(code="dbl(x) = x * 2\ninc(x) = x + 1\nf = inc <<< dbl\nresult = f(5)\n")
    assert bindings["result"] == 11


def test_compose_chain(nomi_mode):
    run = get_run_eval_loop(nomi_mode)
    bindings = run(code="inc(x) = x + 1\ndbl(x) = x * 2\nsq(x) = x * x\nf = inc >>> dbl >>> sq\nresult = f(3)\n")
    assert bindings["result"] == 64


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

