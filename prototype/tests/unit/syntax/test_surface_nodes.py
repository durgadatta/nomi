import ast

from prototype.parser.nomi.usage import generate_ast
from prototype.syntax.surface import BindingTarget, DataDecl


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
    assert isinstance(name_field.target.annotation, ast.Name)
    assert name_field.target.annotation.id == "str"
    assert name_field.target.constraint is None

    assert age_field.target.name == "age"
    assert age_field.target.annotation is None
    assert isinstance(age_field.target.constraint, ast.Compare)


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
