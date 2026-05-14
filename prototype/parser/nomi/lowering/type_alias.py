"""Type alias: ``type UserId = str`` → simple assignment."""

import ast


class TypeAliasMixin:
    def type_alias(self, items):
        name, value = items
        return ast.Assign(
            targets=[ast.Name(id=name, ctx=ast.Store())],
            value=value,
        )
