"""End-to-end tests for all function definition styles."""

from prototype.interpreter.helpers import get_run_eval_loop


# ── piecewise functions ───────────────────────────────────────────

def test_piecewise_factorial(nomi_mode):
    run = get_run_eval_loop(nomi_mode)
    bindings = run(code="\n".join([
        "fact(1) = 1",
        "fact(n) = fact(n - 1) * n",
        "r5 = fact(5)",
        "",
    ]))
    assert bindings["r5"] == 120


def test_piecewise_fibonacci(nomi_mode):
    run = get_run_eval_loop(nomi_mode)
    bindings = run(code="\n".join([
        "fib(0) = 0",
        "fib(1) = 1",
        "fib(n) = fib(n - 1) + fib(n - 2)",
        "r6 = fib(6)",
        "",
    ]))
    assert bindings["r6"] == 8


def test_piecewise_first_match_wins(nomi_mode):
    run = get_run_eval_loop(nomi_mode)
    bindings = run(code="\n".join([
        "f(1) = 10",
        "f(n) = n",
        "r = f(1)",
        "",
    ]))
    assert bindings["r"] == 10


def test_piecewise_three_cases(nomi_mode):
    run = get_run_eval_loop(nomi_mode)
    bindings = run(code="\n".join([
        "sign(0) = 0",
        "sign(n) = 1 if n > 0 else -1",
        "neg = sign(-5)",
        "zer = sign(0)",
        "pos = sign(5)",
        "",
    ]))
    assert bindings["neg"] == -1
    assert bindings["zer"] == 0
    assert bindings["pos"] == 1


def test_piecewise_capture_name(nomi_mode):
    run = get_run_eval_loop(nomi_mode)
    bindings = run(code="\n".join([
        "f(1) = 1",
        "f(n) = n",
        "r = f(99)",
        "",
    ]))
    assert bindings["r"] == 99


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


# ── cross-feature interactions ────────────────────────────────────

def test_piecewise_standalone_equation(nomi_mode):
    run = get_run_eval_loop(nomi_mode)
    bindings = run(code="square(x) = x * x\nresult = square(9)\n")
    assert bindings["result"] == 81


def test_piecewise_not_merged_when_not_contiguous(nomi_mode):
    run = get_run_eval_loop(nomi_mode)
    bindings = run(code="\n".join([
        "f(1) = 1",
        "g() = 0",
        "f(n) = n",
        "r1 = f(1)",
        "r2 = f(99)",
        "",
    ]))
    assert bindings["r1"] == 1
    assert bindings["r2"] == 99


# ═══════════════════════════════════════════════════════════════════
# New features
# ═══════════════════════════════════════════════════════════════════

# ── single-arg equations without parens ─────────────────────────────

def test_no_parens_equation(nomi_mode):
    run = get_run_eval_loop(nomi_mode)
    bindings = run(code="double x = x * 2\nresult = double(5)\n")
    assert bindings["result"] == 10


def test_no_parens_equation_method_call(nomi_mode):
    run = get_run_eval_loop(nomi_mode)
    bindings = run(code='upcase s = s.upper()\nresult = upcase("hello")\n')
    assert bindings["result"] == "HELLO"


def test_no_parens_mixed_styles(nomi_mode):
    run = get_run_eval_loop(nomi_mode)
    bindings = run(code="sq x = x * x\ndbl(x) = x + x\nr1 = sq(4)\nr2 = dbl(4)\n")
    assert bindings["r1"] == 16
    assert bindings["r2"] == 8


def test_no_parens_with_where(nomi_mode):
    run = get_run_eval_loop(nomi_mode)
    bindings = run(code="area r = pi * r * r where:\n    pi = 3.14\nresult = area(2)\n")
    assert abs(bindings["result"] - 12.56) < 0.01


def test_no_parens_piecewise_mixed(nomi_mode):
    run = get_run_eval_loop(nomi_mode)
    bindings = run(code="\n".join([
        "fib(1) = 1",
        "fib(2) = 1",
        "fib n = fib(n - 1) + fib(n - 2)",
        "result = fib(6)",
        "",
    ]))
    assert bindings["result"] == 8


# ── guards in piecewise equations ───────────────────────────────────

def test_guards_sign_function(nomi_mode):
    run = get_run_eval_loop(nomi_mode)
    bindings = run(code="\n".join([
        "sign(n) when n > 0 = 1",
        "sign(n) when n < 0 = -1",
        "sign(n) = 0",
        "pos = sign(10)",
        "neg = sign(-5)",
        "zero = sign(0)",
        "",
    ]))
    assert bindings["pos"] == 1
    assert bindings["neg"] == -1
    assert bindings["zero"] == 0


def test_guards_no_parens_form(nomi_mode):
    run = get_run_eval_loop(nomi_mode)
    bindings = run(code="\n".join([
        "classify n when n > 0 = 'positive'",
        "classify n = 'non-positive'",
        "r1 = classify(5)",
        "r2 = classify(-3)",
        "",
    ]))
    assert bindings["r1"] == "positive"
    assert bindings["r2"] == "non-positive"


def test_guards_fallthrough(nomi_mode):
    run = get_run_eval_loop(nomi_mode)
    bindings = run(code="\n".join([
        "describe(n) when n > 100 = 'huge'",
        "describe(n) when n > 10 = 'big'",
        "describe(n) = 'small'",
        "r1 = describe(200)",
        "r2 = describe(50)",
        "r3 = describe(5)",
        "",
    ]))
    assert bindings["r1"] == "huge"
    assert bindings["r2"] == "big"
    assert bindings["r3"] == "small"


def test_guards_single_equation(nomi_mode):
    run = get_run_eval_loop(nomi_mode)
    bindings = run(code="\n".join([
        "is_even(n) when n % 2 == 0 = True",
        "r1 = is_even(4)",
        "",
    ]))
    assert bindings["r1"] == True


def test_guards_is_positive_piecewise(nomi_mode):
    run = get_run_eval_loop(nomi_mode)
    bindings = run(code="\n".join([
        "abs_desc(n) when n >= 0 = 'non_negative'",
        "abs_desc(n) when n < 0 = 'negative'",
        "r1 = abs_desc(42)",
        "r2 = abs_desc(-7)",
        "",
    ]))
    assert bindings["r1"] == "non_negative"
    assert bindings["r2"] == "negative"


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


# ── defaults in equation args ────────────────────────────────────────

def test_eq_defaults_basic(nomi_mode):
    run = get_run_eval_loop(nomi_mode)
    bindings = run(code="add(a, b=1) = a + b\nresult = add(5)\n")
    assert bindings["result"] == 6


def test_eq_defaults_override(nomi_mode):
    run = get_run_eval_loop(nomi_mode)
    bindings = run(code="add(a, b=1) = a + b\nresult = add(5, 3)\n")
    assert bindings["result"] == 8


def test_eq_defaults_string(nomi_mode):
    run = get_run_eval_loop(nomi_mode)
    bindings = run(code="greet(name, greeting='Hello') = greeting + ', ' + name\nresult = greet('World')\n")
    assert bindings["result"] == "Hello, World"


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


# ── return type annotations on equations ──────────────────────────────

def test_eq_returns_plain(nomi_mode):
    run = get_run_eval_loop(nomi_mode)
    bindings = run(code="double(x) = x * 2 -> int\nresult = double(5)\n")
    assert bindings["result"] == 10


def test_eq_returns_no_parens(nomi_mode):
    run = get_run_eval_loop(nomi_mode)
    bindings = run(code="double x = x * 2 -> int\nresult = double(5)\n")
    assert bindings["result"] == 10


def test_eq_returns_guarded(nomi_mode):
    run = get_run_eval_loop(nomi_mode)
    bindings = run(code="\n".join([
        "classify(n) when n > 0 = 'positive' -> str",
        "classify(n) = 'non-positive' -> str",
        "result = classify(5)",
        "",
    ]))
    assert bindings["result"] == "positive"


def test_eq_returns_no_parens_guarded(nomi_mode):
    run = get_run_eval_loop(nomi_mode)
    bindings = run(code="\n".join([
        "classify n when n > 0 = 'positive' -> str",
        "classify n = 'non-positive' -> str",
        "r1 = classify(5)",
        "r2 = classify(-3)",
        "",
    ]))
    assert bindings["r1"] == "positive"
    assert bindings["r2"] == "non-positive"


def test_eq_returns_mixed_styles(nomi_mode):
    run = get_run_eval_loop(nomi_mode)
    bindings = run(code="\n".join([
        "sq x = x * x -> int",
        "dbl(x) = x + x -> int",
        "r1 = sq(4)",
        "r2 = dbl(4)",
        "",
    ]))
    assert bindings["r1"] == 16
    assert bindings["r2"] == 8


# ── return type annotations on arrows ─────────────────────────────────

def test_arrow_returns_single_param(nomi_mode):
    run = get_run_eval_loop(nomi_mode)
    bindings = run(code="f = x => x * 2 -> int\nresult = f(5)\n")
    assert bindings["result"] == 10


def test_arrow_returns_multi_param(nomi_mode):
    run = get_run_eval_loop(nomi_mode)
    bindings = run(code="f = (x, y) => x + y -> int\nresult = f(3, 4)\n")
    assert bindings["result"] == 7


def test_arrow_mixed_with_without_returns(nomi_mode):
    run = get_run_eval_loop(nomi_mode)
    bindings = run(code="\n".join([
        "f = x => x + 1 -> int",
        "g = x => x + 1",
        "result = f(3) + g(3)",
        "",
    ]))
    assert bindings["result"] == 8
