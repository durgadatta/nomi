"""
Constraint annotation system: converts type annotations into runtime
predicate functions that are checked at binding time.

See ``binding_error.py`` for the diagnostic type raised on failure.
"""

import ast
from functools import cached_property
from typing import Any, List, Callable
from .binding_error import BindingError


class Annotation:
    '''
    x: (name of function or class) or expression
    expression: any expr involving "x"
    '''
    def __init__(self, var_name, ann, interpreter):
        self.var_name = var_name
        self.ann, self.message = self._unwrap_message(ann)
        self.interpreter = interpreter
        self._source = ast.unparse(self.ann)

    @staticmethod
    def _unwrap_message(ann):
        if (
            isinstance(ann, ast.Call)
            and isinstance(ann.func, ast.Name)
            and ann.func.id == "__constraint_message__"
            and len(ann.args) == 2
            and isinstance(ann.args[1], ast.Constant)
            and isinstance(ann.args[1].value, str)
        ):
            return ann.args[0], ann.args[1].value
        return ann, None

    @property
    def source(self) -> str:
        return self._source

    @cached_property
    def predicate(self) -> Callable[[Any], bool]:
        """Normalize a single constraint to a predicate function."""
        annotation, var_name = self.ann, self.var_name

        # Case 1: Simple name (could be class or function)
        if isinstance(annotation, ast.Name):
            name_value = self.interpreter.eval(annotation)
            name = annotation.id
            return self._with_message(self._predicate_from_name(name_value, name))

        # Case 2: Any other expression
        else:
            return self._with_message(self._predicate_from_expression(annotation, var_name))

    def _with_message(self, predicate: Callable[[Any], bool]) -> Callable[[Any], bool]:
        if self.message is None:
            return predicate

        def messaged_predicate(value):
            try:
                return predicate(value)
            except BindingError as error:
                raise BindingError(
                    error.name, error.value,
                    message=f"{self.message} ({error.message})" if error.message else self.message,
                    binding_kind=error.binding_kind,
                    constraint_expr=error.constraint_expr,
                ) from error
            except TypeError as error:
                raise BindingError(
                    self.var_name, value,
                    message=f"{self.message} ({error})",
                    constraint_expr=self.source,
                ) from error
        return messaged_predicate

    def _predicate_from_name(self, name_value, name) -> Callable[[Any], bool]:
        """Create predicate from a name (class or function)."""
        if isinstance(name_value, type):
            # Class -> isinstance check
            def type_predicate(value):
                if not isinstance(value, name_value):
                    raise BindingError(
                        name, value,
                        message=f"Expected {name}, got {type(value).__name__}",
                        constraint_expr=name,
                    )
                return True
            return type_predicate

        elif callable(name_value):
            # Function -> call with value
            def callable_predicate(value):
                result = name_value(value)
                if not result:
                    raise BindingError(
                        name, value,
                        message=f"Callable constraint {name} failed",
                        constraint_expr=name,
                    )
                return True
            return callable_predicate

    def _predicate_from_expression(self, expr_node: ast.expr, var_name: str) -> Callable[[Any], bool]:
        """Create predicate from any expression by converting to function definition."""
        # Create a function definition node with the expression as body
        return_node = ast.Return(value=expr_node)
        func_body = [return_node]

        # Create function definition
        func_def = ast.FunctionDef(
            name='_constraint_predicate',
            args=ast.arguments(
                posonlyargs=[], args=[ast.arg(arg=var_name)], kwonlyargs=[],
                kw_defaults=[], defaults=[], vararg=None, kwarg=None,
            ),
            body=func_body,
            decorator_list=[], returns=None,
        )

        # Evaluate the function definition in current environment
        self.interpreter.eval(func_def)
        constraint_func = self.interpreter.current_env.bindings['_constraint_predicate']

        # Clean up
        del self.interpreter.current_env.bindings['_constraint_predicate']

        expr_str = ast.unparse(expr_node)

        # Wrap with error handling
        def expr_predicate(value):
            result = constraint_func(value)
            if not result:
                raise BindingError(
                    var_name, value,
                    message=f"Constraint '{expr_str}' failed",
                    constraint_expr=expr_str,
                )
            return True

        return expr_predicate


class Annotations:
    def __init__(self, items: List[Annotation]):
        self.items = items

    @classmethod
    def from_node(cls, node: ast.AnnAssign, interpreter):
        '''
        directly from the parser
        '''
        annotations = node.annotation
        name = node.target.id

        # normalize to collection
        if isinstance(annotations, ast.Tuple):
            annotations = annotations.elts
        else:
            annotations = (annotations,)
        annotations = [Annotation(name, ann, interpreter) for ann in annotations]
        return cls(annotations)

    @property
    def predicate(self) -> Callable[[Any], bool]:
        """Combine multiple predicates into one that accumulates errors."""
        # Get string representations
        annotation_strs = [ann.source for ann in self.items]

        predicates = [ann.predicate for ann in self.items]

        def combined_predicate(value):
            errors = []
            for predicate, annotation_str in zip(predicates, annotation_strs):
                try:
                    if not predicate(value):
                        errors.append(f"Constraint '{annotation_str}' failed for value {value!r}")
                except BindingError as error:
                    errors.append(error.message)

            if errors:
                raise BindingError(
                    self.items[0].var_name,
                    value,
                    message="Constraint violations:\n  " + "\n  ".join(errors),
                    binding_kind="assignment",
                )

            return True

        return combined_predicate


class ConstraintBindingMixin:
    def eval_AnnAssign(self, node: ast.AnnAssign) -> None:
        """Add the constraints and delegate to Python's handler"""
        # TODO(NOMI-SUBSTRATE-011): Route this through a shared BindingTarget
        # model so assignments, parameters, data fields, pattern captures,
        # imports, and block params use one constraint/diagnostic path.
        # Always set constraints from the annotation
        if isinstance(node.target, ast.Name):
            predicate = Annotations.from_node(node, self).predicate
            self.current_env.set_constraint(node.target.id, predicate)

        # If there's a value, assign it (constraints will be checked in Environment.set)
        super().eval_AnnAssign(node)
