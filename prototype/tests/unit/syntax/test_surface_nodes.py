import ast

from prototype.parser.nomi.usage import generate_ast
from prototype.syntax.surface import BindingTarget, Constraint, DataDecl


def test_data_decl_surface_node_preserves_binding_targets():
    tree = generate_ast(
        code="\n".join(
            [
                "data Person:",
                "    name: str",
                "    age where age >= 0",
                "",
            ]
        ),
        keep_surface=True,
    )

    decl = tree.body[0]
    assert isinstance(decl, DataDecl)
    assert decl.name == "Person"

    name_field, age_field = decl.fields
    assert isinstance(name_field.target, BindingTarget)
    assert name_field.target.name == "name"
    assert name_field.target.role == "data-field"
    assert name_field.target.target_kind == "name"
    assert name_field.target.capture_names == ()
    assert name_field.target.constraints == ()
    assert isinstance(name_field.target.annotation, ast.Name)
    assert name_field.target.annotation.id == "str"
    assert name_field.target.constraint is None

    assert age_field.target.name == "age"
    assert age_field.target.annotation is None
    assert len(age_field.target.constraints) == 1
    assert isinstance(age_field.target.constraints[0], Constraint)
    assert age_field.target.constraints[0].source == "age >= 0"
    assert age_field.target.constraints[0].subject == "age"
    assert isinstance(age_field.target.constraint, ast.Compare)


def test_binding_target_normalizes_constraint_metadata():
    target = BindingTarget(
        name="age",
        role="assignment",
        annotation=ast.Name(id="int", ctx=ast.Load()),
        constraint=ast.Compare(
            left=ast.Name(id="age", ctx=ast.Load()),
            ops=[ast.GtE()],
            comparators=[ast.Constant(value=13)],
        ),
        message="Must be at least 13",
        redaction={"paths": ["payload.age"]},
    )

    assert target.role == "assignment"
    assert target.annotation.id == "int"
    assert target.constraint is target.constraints[0].expression
    assert target.constraints[0].source == "age >= 13"
    assert target.constraints[0].message == "Must be at least 13"
    assert target.constraints[0].redaction == {"paths": ["payload.age"]}


def test_data_decl_surface_node_lowers_to_current_classdef_shape():
    tree = generate_ast(
        code="\n".join(
            [
                "data Point:",
                "    x: int",
                "    y: int",
                "",
            ]
        )
    )

    decl = tree.body[0]
    assert isinstance(decl, ast.ClassDef)
    assert decl.name == "Point"
    assert [stmt.name for stmt in decl.body] == ["__init__", "__repr__", "__eq__"]

    init = decl.body[0]
    assert isinstance(init, ast.FunctionDef)
    assert [arg.arg for arg in init.args.args] == ["self", "x", "y"]
