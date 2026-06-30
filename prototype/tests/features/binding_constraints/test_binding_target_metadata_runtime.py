import ast

import pytest

from prototype.interpreter.nomi.binding_error import BindingError
from prototype.interpreter.nomi.interpreter import Interpreter
from prototype.parser.nomi.usage import generate_ast


def _eval_nomi(code: str) -> Interpreter:
    tree = ast.fix_missing_locations(generate_ast(code=code))
    interpreter = Interpreter()
    interpreter.eval(tree)
    return interpreter


def test_assignment_constraints_preserve_binding_target_metadata():
    interpreter = _eval_nomi(
        'age:int, age >= 13 else "Must be at least 13" = 14\n'
    )

    target = interpreter.global_env.get_constraint_target("age")

    assert target.name == "age"
    assert target.role == "assignment"
    assert len(target.constraints) == 2
    assert [constraint.source for constraint in target.constraints] == [
        "int",
        "age >= 13",
    ]
    assert target.constraints[0].message is None
    assert target.constraints[1].message == "Must be at least 13"


def test_failed_assignment_constraint_does_not_commit_new_value():
    interpreter = _eval_nomi("age:int, age >= 0 = 10\n")
    failed_tree = ast.fix_missing_locations(generate_ast(code="age = -1\n"))

    with pytest.raises(BindingError):
        interpreter.eval(failed_tree)

    assert interpreter.global_env.get("age") == 10
