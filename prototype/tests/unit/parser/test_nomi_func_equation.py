import ast

from prototype.parser.nomi.usage import generate_ast
from prototype.interpreter.helpers import get_run_eval_loop


def test_func_equation_produces_function_def():
    tree = generate_ast(code="add(a, b) = a + b\n")
    stmt = tree.body[0]
    assert isinstance(stmt, ast.FunctionDef)
    assert stmt.name == "add"
    assert len(stmt.args.args) == 2
    assert isinstance(stmt.body[0], ast.Return)


def test_func_equation_no_params():
    tree = generate_ast(code="pi() = 3.14\n")
    stmt = tree.body[0]
    assert isinstance(stmt, ast.FunctionDef)
    assert stmt.name == "pi"
    assert len(stmt.args.args) == 0


def test_func_equation_with_default():
    tree = generate_ast(code='greet(name="world") = "Hello, " + name\n')
    stmt = tree.body[0]
    assert stmt.args.defaults[0].value == "world"


def test_func_equation_executes(interpreter_mode):
    if interpreter_mode == "python":
        return  # Nomi-specific syntax
    run = get_run_eval_loop(interpreter_mode)
    bindings = run(code="add(a, b) = a + b\nresult = add(3, 4)\n")
    assert bindings["result"] == 7


def test_func_equation_can_be_called(interpreter_mode):
    if interpreter_mode == "python":
        return
    run = get_run_eval_loop(interpreter_mode)
    bindings = run(code='greet() = "hi"\nr = greet()\n')
    assert bindings["r"] == "hi"


def test_func_equation_closure(interpreter_mode):
    if interpreter_mode == "python":
        return
    run = get_run_eval_loop(interpreter_mode)
    bindings = run(code="x = 10\nadder(n) = x + n\nr = adder(5)\n")
    assert bindings["r"] == 15
