"""Data declarations: ``data Name: fields...`` → ClassDef with __init__,
__repr__, __eq__, and constraint checks."""

import ast


class DataDeclMixin:
    def data_decl(self, items):
        class_name = str(items[0])
        fields = items[1:]

        field_specs = [self._data_field_spec(f) for f in fields]

        body = []
        body.append(self._make_init(class_name, field_specs))
        if field_specs:
            body.append(self._make_repr(class_name, field_specs))
            body.append(self._make_eq(class_name, field_specs))

        return ast.ClassDef(
            name=class_name,
            bases=[],
            keywords=[],
            body=body,
            decorator_list=[],
        )

    def _data_field_spec(self, field_node):
        """Extract (name, type_annotation, constraint) from a field node."""
        if field_node.data == "data_field_bare":
            return (str(field_node.children[0]), None, None)
        elif field_node.data == "data_field_typed":
            return (str(field_node.children[0]), field_node.children[1], None)
        elif field_node.data == "data_field_where":
            return (str(field_node.children[0]), None, field_node.children[1])
        elif field_node.data == "data_field_constrained":
            return (str(field_node.children[0]), field_node.children[1], field_node.children[2])
        raise ValueError(f"Unknown field type: {field_node.data}")

    # ── generated methods ──────────────────────────────────────────

    def _make_init(self, class_name, field_specs):
        args = [ast.arg(arg="self")]
        body = []
        checks = []

        for field_name, field_type, constraint in field_specs:
            ann = field_type
            args.append(ast.arg(arg=field_name, annotation=ann))
            body.append(
                ast.Assign(
                    targets=[
                        ast.Attribute(
                            value=ast.Name(id="self", ctx=ast.Load()),
                            attr=field_name,
                            ctx=ast.Store(),
                        )
                    ],
                    value=ast.Name(id=field_name, ctx=ast.Load()),
                )
            )
            if constraint is not None:
                checks.append((field_name, constraint))

        for field_name, constraint in checks:
            constraint_src = ast.unparse(constraint) if hasattr(ast, 'unparse') else str(constraint)
            body.append(
                ast.If(
                    test=ast.UnaryOp(op=ast.Not(), operand=constraint),
                    body=[
                        ast.Raise(
                            exc=ast.Call(
                                func=ast.Name(id="TypeError", ctx=ast.Load()),
                                args=[
                                    ast.Constant(
                                        value=f"Constraint violation for field {field_name!r}"
                                              f" of {class_name!r}: {constraint_src}"
                                    )
                                ],
                                keywords=[],
                            ),
                            cause=None,
                        )
                    ],
                    orelse=[],
                )
            )

        return ast.FunctionDef(
            name="__init__",
            args=ast.arguments(
                posonlyargs=[],
                args=args,
                kwonlyargs=[],
                kw_defaults=[],
                defaults=[],
            ),
            body=body,
            decorator_list=[],
            returns=None,
        )

    def _make_repr(self, class_name, field_specs):
        field_names = [f[0] for f in field_specs]
        parts = [f"{name}={{0.{name}!r}}" for name in field_names]
        fmt = f"{class_name}({', '.join(parts)})"

        return ast.FunctionDef(
            name="__repr__",
            args=ast.arguments(
                posonlyargs=[], args=[ast.arg(arg="self")],
                kwonlyargs=[], kw_defaults=[], defaults=[],
            ),
            body=[
                ast.Return(
                    value=ast.Call(
                        func=ast.Attribute(
                            value=ast.Constant(value=fmt),
                            attr="format",
                            ctx=ast.Load(),
                        ),
                        args=[ast.Name(id="self", ctx=ast.Load())],
                        keywords=[],
                    )
                )
            ],
            decorator_list=[],
            returns=None,
        )

    def _make_eq(self, class_name, field_specs):
        field_names = [f[0] for f in field_specs]

        comparisons = []
        for name in field_names:
            comparisons.append(
                ast.Compare(
                    left=ast.Attribute(
                        value=ast.Name(id="self", ctx=ast.Load()), attr=name, ctx=ast.Load()
                    ),
                    ops=[ast.Eq()],
                    comparators=[
                        ast.Attribute(
                            value=ast.Name(id="other", ctx=ast.Load()), attr=name, ctx=ast.Load()
                        )
                    ],
                )
            )

        if len(comparisons) == 1:
            combined = comparisons[0]
        else:
            combined = ast.BoolOp(op=ast.And(), values=comparisons)

        return ast.FunctionDef(
            name="__eq__",
            args=ast.arguments(
                posonlyargs=[],
                args=[ast.arg(arg="self"), ast.arg(arg="other")],
                kwonlyargs=[], kw_defaults=[], defaults=[],
            ),
            body=[
                ast.If(
                    test=ast.Call(
                        func=ast.Name(id="isinstance", ctx=ast.Load()),
                        args=[
                            ast.Name(id="other", ctx=ast.Load()),
                            ast.Name(id=class_name, ctx=ast.Load()),
                        ],
                        keywords=[],
                    ),
                    body=[ast.Return(value=combined)],
                    orelse=[ast.Return(value=ast.Constant(value=NotImplemented))],
                )
            ],
            decorator_list=[],
            returns=None,
        )

    # ── field lowering ─────────────────────────────────────────────

    def data_field_typed(self, items):
        return self._field_node("data_field_typed", items)

    def data_field_constrained(self, items):
        return self._field_node("data_field_constrained", items)

    def data_field_where(self, items):
        return self._field_node("data_field_where", items)

    def data_field_bare(self, items):
        return self._field_node("data_field_bare", items)

    def _field_node(self, kind, items):
        """Wrap field data so data_decl can introspect it.

        Since Lark lowering happens AFTER the parse-tree transform and the
        items are already Python AST nodes, we can't return a Lark Tree with
        .data and .children.  Instead we return a lightweight container.
        """
        return _Field(kind, list(items))


class _Field:
    __slots__ = ("data", "children")
    def __init__(self, data, children):
        self.data = data
        self.children = children
