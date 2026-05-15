"""BindingError: structured diagnostic for constraint violations."""


class BindingError(TypeError):
    """Raised when a binding constraint fails.

    Subclasses TypeError for backward compatibility with existing
    exception handlers.  New code should catch BindingError directly
    to access structured diagnostic fields.
    """

    def __init__(self, name, value, *, message=None, binding_kind="assignment",
                 constraint_expr=None):
        self.name = name
        self.value = value
        self.message = message
        self.binding_kind = binding_kind
        self.constraint_expr = constraint_expr
        super().__init__(self._format())

    def _format(self):
        kind_label = {
            "assignment": "assignment",
            "parameter": "parameter",
            "block_parameter": "block parameter",
            "pattern_capture": "pattern capture",
            "destructure_target": "destructure target",
        }.get(self.binding_kind, self.binding_kind)

        if self.message:
            return f"BindingError for '{self.name}' ({kind_label}): {self.message}"
        if self.constraint_expr:
            return (f"BindingError for '{self.name}' ({kind_label}): "
                    f"value {self.value!r} failed constraint '{self.constraint_expr}'")
        return (f"BindingError for '{self.name}' ({kind_label}): "
                f"value {self.value!r} does not satisfy constraint")
