"""End-to-end tests for all function definition styles."""

from prototype.interpreter.helpers import get_run_eval_loop


# ── underscore hole-filling ───────────────────────────────────────

def test_hole_attribute_upper(nomi_mode):
    run = get_run_eval_loop(nomi_mode)
    bindings = run(code='up = _.upper()\nresult = up("hello")\n')
    assert bindings["result"] == "HELLO"


def test_hole_binop_add(nomi_mode):
    run = get_run_eval_loop(nomi_mode)
    bindings = run(code="inc = _ + 1\nresult = inc(5)\n")
    assert bindings["result"] == 6


def test_hole_binop_subscript(nomi_mode):
    run = get_run_eval_loop(nomi_mode)
    bindings = run(code='get = _["k"]\nresult = get({"k": 99})\n')
    assert bindings["result"] == 99


def test_hole_two_params(nomi_mode):
    run = get_run_eval_loop(nomi_mode)
    bindings = run(code="add = _ + _\nresult = add(3, 4)\n")
    assert bindings["result"] == 7


def test_hole_larger_expression(nomi_mode):
    run = get_run_eval_loop(nomi_mode)
    bindings = run(code="f = _ * 2 + 1\nresult = f(3)\n")
    assert bindings["result"] == 7


def test_hole_not_wrapped_when_underscore_bound(nomi_mode):
    run = get_run_eval_loop(nomi_mode)
    bindings = run(code="_ = 3\nvalue = _ + 4\n")
    assert bindings["value"] == 7


def test_hole_for_loop_target_not_hole(nomi_mode):
    run = get_run_eval_loop(nomi_mode)
    bindings = run(code="total = 0\nfor _ in range(3):\n    total = total + _\n")
    assert bindings["total"] == 3


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


# ── where clause ──────────────────────────────────────────────────

def test_where_simple_binding(nomi_mode):
    run = get_run_eval_loop(nomi_mode)
    bindings = run(code="result = x + y where:\n    x = 10\n    y = 20\n")
    assert bindings["result"] == 30


def test_where_local_function(nomi_mode):
    run = get_run_eval_loop(nomi_mode)
    bindings = run(code="result = double(x) where:\n    double(n) = n * 2\n    x = 5\n")
    assert bindings["result"] == 10


def test_where_on_func_equation(nomi_mode):
    run = get_run_eval_loop(nomi_mode)
    bindings = run(code='greet(name) = prefix + name where:\n    prefix = "Hi, "\nr = greet("Nomi")\n')
    assert bindings["r"] == "Hi, Nomi"


def test_where_not_leak_bindings(nomi_mode):
    run = get_run_eval_loop(nomi_mode)
    bindings = run(code="result = x where:\n    x = 42\n")
    assert bindings["result"] == 42
    assert "x" not in bindings


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

def test_where_with_hole(nomi_mode):
    run = get_run_eval_loop(nomi_mode)
    bindings = run(code="result = scaled where:\n    scale = _ * 3\n    scaled = scale(7)\n")
    assert bindings["result"] == 21


def test_piecewise_standalone_equation(nomi_mode):
    run = get_run_eval_loop(nomi_mode)
    bindings = run(code="square(x) = x * x\nresult = square(9)\n")
    assert bindings["result"] == 81


def test_hole_two_params_reversed(nomi_mode):
    run = get_run_eval_loop(nomi_mode)
    bindings = run(code="sub = _ - _\nresult = sub(10, 3)\n")
    assert bindings["result"] == 7


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


def test_where_not_pollute_namespace(nomi_mode):
    run = get_run_eval_loop(nomi_mode)
    bindings = run(code="result = x + y where:\n    x = 10\n    y = 20\n")
    assert bindings["result"] == 30
    assert "x" not in bindings
    assert "y" not in bindings


def test_where_inline(nomi_mode):
    run = get_run_eval_loop(nomi_mode)
    bindings = run(code="ss(x, y) = s(x) + s(y) where s(n) = n * n\nr = ss(3, 4)\n")
    assert bindings["r"] == 25


def test_where_inline_assign(nomi_mode):
    run = get_run_eval_loop(nomi_mode)
    bindings = run(code="result = x * 2 where x = 10\nr = result\n")
    assert bindings["r"] == 20
    assert "x" not in bindings


# ── where clause: chaining and recursion ──────────────────────────

def test_where_later_uses_earlier_binding(nomi_mode):
    run = get_run_eval_loop(nomi_mode)
    bindings = run(code="result = z where:\n    x = 10\n    y = x * 2\n    z = y + 5\n")
    assert bindings["result"] == 25


def test_where_mutual_recursion(nomi_mode):
    run = get_run_eval_loop(nomi_mode)
    bindings = run(code="\n".join([
        "result = is_even(4) where:",
        "    is_even(0) = True",
        "    is_even(n) = is_odd(n - 1)",
        "    is_odd(0) = False",
        "    is_odd(n) = is_even(n - 1)",
        "",
    ]))
    assert bindings["result"] is True

def test_where_mutual_recursion_odd(nomi_mode):
    run = get_run_eval_loop(nomi_mode)
    bindings = run(code="\n".join([
        "result = is_odd(3) where:",
        "    is_even(0) = True",
        "    is_even(n) = is_odd(n - 1)",
        "    is_odd(0) = False",
        "    is_odd(n) = is_even(n - 1)",
        "",
    ]))
    assert bindings["result"] is True


# ═══════════════════════════════════════════════════════════════════
# New features
# ═══════════════════════════════════════════════════════════════════

# ── positional holes $1, $2 ────────────────────────────────────────

def test_dollar_hole_single(nomi_mode):
    run = get_run_eval_loop(nomi_mode)
    bindings = run(code="double = $1 * 2\nresult = double(5)\n")
    assert bindings["result"] == 10


def test_dollar_hole_two_params(nomi_mode):
    run = get_run_eval_loop(nomi_mode)
    bindings = run(code="adder = $1 + $2\nresult = adder(3, 4)\n")
    assert bindings["result"] == 7


def test_dollar_hole_attribute(nomi_mode):
    run = get_run_eval_loop(nomi_mode)
    bindings = run(code='get_name = $1.name\nclass P: pass\np = P()\np.name = "alice"\nresult = get_name(p)\n')
    assert bindings["result"] == "alice"


def test_dollar_hole_three_params(nomi_mode):
    run = get_run_eval_loop(nomi_mode)
    bindings = run(code="fmt = $1 + $2 + $3\nresult = fmt('a', 'b', 'c')\n")
    assert bindings["result"] == "abc"


def test_dollar_hole_where_clause(nomi_mode):
    run = get_run_eval_loop(nomi_mode)
    bindings = run(code="result = scale(10) where:\n    scale = $1 * 3\n")
    assert bindings["result"] == 30


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


# ── Python match guards ────────────────────────────────────────────

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


# ── named dollar holes $name ────────────────────────────────────────

def test_named_dollar_basic(nomi_mode):
    run = get_run_eval_loop(nomi_mode)
    bindings = run(code="add = $x + $y\nresult = add(3, 4)\n")
    assert bindings["result"] == 7


def test_named_dollar_duplicate(nomi_mode):
    run = get_run_eval_loop(nomi_mode)
    bindings = run(code="dup = $x + $x\nresult = dup(5)\n")
    assert bindings["result"] == 10


def test_named_dollar_mixed_positional(nomi_mode):
    run = get_run_eval_loop(nomi_mode)
    bindings = run(code="mix = $name + $1\nresult = mix('alice', '_suf')\n")
    assert bindings["result"] == "alice_suf"


def test_named_dollar_order(nomi_mode):
    run = get_run_eval_loop(nomi_mode)
    bindings = run(code="order = $b + $a\nresult = order(2, 1)\n")
    assert bindings["result"] == 3


def test_named_dollar_three(nomi_mode):
    run = get_run_eval_loop(nomi_mode)
    bindings = run(code="fmt = $a + $b + $c\nresult = fmt('x', 'y', 'z')\n")
    assert bindings["result"] == "xyz"


def test_named_dollar_where_clause(nomi_mode):
    run = get_run_eval_loop(nomi_mode)
    bindings = run(code="result = greet('dolly') where:\n    greet = 'Hello ' + $name\n")
    assert bindings["result"] == "Hello dolly"


def test_named_dollar_meaningful_names(nomi_mode):
    run = get_run_eval_loop(nomi_mode)
    bindings = run(code="full = $first + ' ' + $last\nresult = full('Alice', 'Smith')\n")
    assert bindings["result"] == "Alice Smith"


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

