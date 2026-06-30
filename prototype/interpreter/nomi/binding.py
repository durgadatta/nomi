"""
Constraint annotation system: converts type annotations into runtime
predicate functions that are checked at binding time.

See ``binding_error.py`` for the diagnostic type raised on failure.
"""

import ast
from functools import cached_property
from typing import Any, List, Callable

from prototype.syntax.surface import BindingTarget, Constraint

from .binding_error import BindingError


class Annotation:
    '''
    x: (name of function or class) or expression
    expression: any expr involving "x"
    '''
    def __init__(self, var_name, ann, interpreter):
        self.var_name = var_name
        self.constraint = Constraint.from_expr(ann, subject=var_name)
        self.ann = self.constraint.expression
        self.message = self.constraint.message
        self.interpreter = interpreter
        if not isinstance(self.ann, ast.AST):
            raise TypeError(
                f"Annotation for '{var_name}' is a {type(self.ann).__name__}, "
                f"not an ast.AST node. This indicates an incomplete lowering step "
                f"in the parser — a Lark Tree leaked into the annotation AST. "
                f"Raw annotation: {ann!r}"
            )
        self._source = self.constraint.source or ast.unparse(self.ann)

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
    def __init__(self, name: str, items: List[Annotation], *, role: str):
        self.name = name
        self.items = items
        self.role = role

    @classmethod
    def from_node(cls, node: ast.AnnAssign, interpreter, *, role: str = "assignment"):
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
        return cls(name, annotations, role=role)

    @property
    def binding_target(self) -> BindingTarget:
        return BindingTarget(
            name=self.name,
            role=self.role,
            constraints=tuple(annotation.constraint for annotation in self.items),
        )

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
        # Marker for first implementation slice:
        #   - define BindingTarget as passive metadata before changing eval;
        #   - start with AnnAssign(name, annotations, kind="assignment");
        #   - keep Environment.set_constraint as the backend adapter;
        #   - add tests that failed constraints still raise BindingError with
        #     the same public message before broadening to params/data fields.
        # Always set constraints from the annotation
        if isinstance(node.target, ast.Name):
            role = getattr(node, "_nomi_binding_role", "assignment")
            annotations = Annotations.from_node(node, self, role=role)
            self.current_env.set_constraint(
                node.target.id,
                annotations.predicate,
                target=annotations.binding_target,
            )

        # If there's a value, assign it (constraints will be checked in Environment.set)
        super().eval_AnnAssign(node)
