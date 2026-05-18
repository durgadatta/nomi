"""Runtime tests for Nomi where clauses."""

from prototype.interpreter.helpers import get_run_eval_loop


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
