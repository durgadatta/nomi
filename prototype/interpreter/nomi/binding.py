'''
NOTE:Creating a function from an expression from different context 
might be a generic feature later. Here the context is just the variable
that is annotated; we might have more elaborate context involving
multiple parameters - abstract and move the generic functionality into
interpreter itself.
'''

import ast
from typing import Any, List, Callable

class Annotation:
    '''
    x: (name of function or class) or expression
    expression: any expr involving "x"
    '''
    def __init__(self, var_name, ann, interpreter):
        self.var_name = var_name
        self.ann, self.message = self._unwrap_message(ann)

        self.interpreter = interpreter

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
        return ast.unparse(self.ann) if hasattr(ast, 'unparse') else str(self.ann)

    @property
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
            except TypeError as error:
                raise TypeError(f"{self.message} ({error})") from error
        return messaged_predicate

    def _predicate_from_name(self, name_value, name) -> Callable[[Any], bool]:
        """Create predicate from a name (class or function)."""
        if isinstance(name_value, type):
            # Class -> isinstance check
            def type_predicate(value):
                if not isinstance(value, name_value):
                    raise TypeError(f"Expected {name}, got {type(value).__name__}")
                return True
            return type_predicate
            
        elif callable(name_value):
            # Function -> call with value
            def callable_predicate(value):
                result = name_value(value)
                if not result:
                    raise TypeError(f"Callable constraint {name} failed for value {value!r}")
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
        
        # Wrap with error handling
        def expr_predicate(value):
            result = constraint_func(value)
            if not result:
                expr_str = ast.unparse(expr_node) if hasattr(ast, 'unparse') else str(expr_node)
                raise TypeError(f"Constraint '{expr_str}' failed for value {value!r}")
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
                except TypeError as error:
                    errors.append(str(error))
            
            if errors:
                error_msg = "Constraint violations:\n  " + "\n  ".join(errors)
                raise TypeError(error_msg)
            
            return True
        
        return combined_predicate


class ConstraintBindingMixin:
    def eval_AnnAssign(self, node: ast.AnnAssign) -> None:
        """Add the constraints and delegate to Python's handler"""
        # Always set constraints from the annotation
        if isinstance(node.target, ast.Name):
            predicate = Annotations.from_node(node, self).predicate
            self.current_env.set_constraint(node.target.id, predicate)
        
        # If there's a value, assign it (constraints will be checked in Environment.set)
        super().eval_AnnAssign(node)
