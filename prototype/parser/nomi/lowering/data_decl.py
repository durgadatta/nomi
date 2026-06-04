"""Data declarations: ``data Name: fields...`` → ``DataDecl`` surface node."""

from prototype.syntax.surface import BindingTarget, DataDecl, DataField


class DataDeclMixin:
    def data_decl(self, items):
        class_name = str(items[0])
        fields = items[1:]

        return DataDecl(
            name=class_name,
            fields=[self._data_field_spec(f) for f in fields],
        )

    def _data_field_spec(self, field_node):
        """Extract a passive ``DataField`` from a field node."""
        if field_node.data == "data_field_bare":
            name, annotation, constraint = str(field_node.children[0]), None, None
        elif field_node.data == "data_field_typed":
            name, annotation, constraint = (
                str(field_node.children[0]),
                field_node.children[1],
                None,
            )
        elif field_node.data == "data_field_where":
            name, annotation, constraint = (
                str(field_node.children[0]),
                None,
                field_node.children[1],
            )
        elif field_node.data == "data_field_constrained":
            name, annotation, constraint = (
                str(field_node.children[0]),
                field_node.children[1],
                field_node.children[2],
            )
        else:
            raise ValueError(f"Unknown field type: {field_node.data}")

        return DataField(
            target=BindingTarget(
                name=name,
                role="data-field",
                annotation=annotation,
                constraint=constraint,
            )
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
