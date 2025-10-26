import ast
from typing import Any, List, Callable


class Annotation:
    '''
    x: (name of function or class) or expression
    expression: any expr involving "x"
    '''
    def __init__(self, var_name, ann, interpreter):
        self.var_name = var_name
        self.ann = ann
        self.interpreter = interpreter

    @property
    def predicate(self) -> Callable[[Any], bool]:
        """Normalize a single constraint to a predicate function."""
        annotation, var_name = self.ann, self.var_name

        # Case 1: Simple name (could be class or function)
        if isinstance(annotation, ast.Name):
            return self._create_name_predicate(annotation, var_name)
        
        # Case 2: Any other expression
        else:
            return self._create_expression_predicate(annotation, var_name)

    def _create_name_predicate(self, name_node: ast.Name, var_name: str) -> Callable[[Any], bool]:
        """Create predicate from a name (class or function)."""
        try:
            name_value = self.interpreter.eval(name_node)
            
            if isinstance(name_value, type):
                # Class -> isinstance check
                def type_predicate(value):
                    if not isinstance(value, name_value):
                        raise TypeError(f"Expected {name_value.__name__}, got {type(value).__name__}")
                    return True
                return type_predicate
                
            elif callable(name_value):
                # Function -> call with value
                def callable_predicate(value):
                    result = name_value(value)
                    if not result:
                        raise TypeError(f"Callable constraint {name_node.id} failed for value {value!r}")
                    return True
                return callable_predicate
                
        except NameError:
            pass
        
        # Fallback: treat as expression with the variable
        return self._create_expression_predicate(name_node, var_name)

    def _create_expression_predicate(self, expr_node: ast.expr, var_name: str) -> Callable[[Any], bool]:
        """Create predicate from any expression."""
        # Convert expression to function
        constraint_func = self._expr_to_function(expr_node, var_name)
        
        def expr_predicate(value):
            result = constraint_func(value)
            if not result:
                expr_str = ast.unparse(expr_node) if hasattr(ast, 'unparse') else str(expr_node)
                raise TypeError(f"Constraint '{expr_str}' failed for value {value!r}")
            return True
        
        return expr_predicate

    def _expr_to_function(self, expr: ast.expr, param_name: str) -> Callable[[Any], bool]:
        """Convert any expression to a function."""
        # Create function dynamically
        if hasattr(ast, 'unparse'):
            expr_str = ast.unparse(expr)
        else:
            expr_str = str(expr)
        
        import uuid
        func_name = f"_constraint_{uuid.uuid4().hex[:8]}"
        func_def = f"def {func_name}({param_name}):\n    return {expr_str}\n"
        
        exec_globals = self.interpreter.current_env.bindings.copy()
        try:
            exec(func_def, exec_globals)
            return exec_globals[func_name]
        except Exception:
            # Fallback: evaluate in context
            def fallback_func(value):
                original_value = self.current_env.bindings.get(param_name)
                self.current_env.bindings[param_name] = value
                try:
                    return bool(self.eval(expr))
                finally:
                    if original_value is not None:
                        self.current_env.bindings[param_name] = original_value
                    elif param_name in self.current_env.bindings:
                        del self.current_env.bindings[param_name]
            return fallback_func



class Annotations:
    def __init__(self, items:List[Annotation]):
        self.items = items 

    @classmethod
    def from_node(cls, node:ast.AnnAssign, interpreter):
        '''
        directly from the parser
        '''
        annotations = node.annotation
        name = node.target.id 

        #normalize to collection
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
        annotation_strs = [
            ast.unparse(ann.ann) if hasattr(ast, 'unparse') else str(ann.ann)
            for ann in self.items
        ]

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


class BindingMixin:

    def eval_AnnAssign(self, node: ast.AnnAssign) -> None:
        """ add the constraints and delegate to Python's handler"""
        # Always set constraints from the annotation
        if isinstance(node.target, ast.Name):
            predicate = Annotations.from_node(node, self).predicate
            self.current_env.set_constraint(node.target.id, predicate)
        
        # If there's a value, assign it (constraints will be checked in Environment.set)
        super().eval_AnnAssign(node)
