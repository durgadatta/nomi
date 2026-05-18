"""Runtime tests for Nomi hole-lambda forms."""

from prototype.interpreter.helpers import get_run_eval_loop


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


def test_hole_two_params_reversed(nomi_mode):
    run = get_run_eval_loop(nomi_mode)
    bindings = run(code="sub = _ - _\nresult = sub(10, 3)\n")
    assert bindings["result"] == 7


def test_where_with_hole(nomi_mode):
    run = get_run_eval_loop(nomi_mode)
    bindings = run(code="result = scaled where:\n    scale = _ * 3\n    scaled = scale(7)\n")
    assert bindings["result"] == 21


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
