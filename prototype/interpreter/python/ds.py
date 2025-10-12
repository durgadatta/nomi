import ast
from typing import Dict, Any, List

from prototype.interpreter.python.base import Environment

class DataStructMixin:
    def eval_Dict(self, node: ast.Dict) -> Dict[Any, Any]:
        result = {}
        for key, value in zip(node.keys, node.values):
            if key is None:
                result.update(self.eval(value))
            else:
                result[self.eval(key)] = self.eval(value)
        return result

    def eval_Set(self, node: ast.Set) -> Set[Any]:
        return {self.eval(elt) for elt in node.elts}

    def eval_ListComp(self, node: ast.ListComp) -> List[Any]:
        result = []
        comp_env = Environment(self, parent=self.current_env)
        old_env = self.current_env
        self.current_env = comp_env
        try:
            for gen in node.generators:
                iterable = self.eval(gen.iter)
                try:
                    for item in iterable:
                        if isinstance(gen.target, ast.Name):
                            comp_env.set(gen.target.id, item)
                        elif isinstance(gen.target, (ast.Tuple, ast.List)):
                            self.assign_target(gen.target, item)
                        else:
                            raise TypeError(f"Unsupported comprehension target {gen.target.__class__.__name__} at line {self.get_lineno(node)}")
                        for if_clause in gen.ifs:
                            if not self.eval(if_clause):
                                break
                        else:
                            if isinstance(node.elt, ast.ListComp):
                                # Evaluate nested comprehension in current environment
                                result.append(self.eval(node.elt))
                            else:
                                result.append(self.eval(node.elt))
                except TypeError as e:
                    raise TypeError(f"'{type(iterable).__name__}' object is not iterable at line {self.get_lineno(gen.iter)}: {str(e)}") from e
        finally:
            self.current_env = old_env
        return result

    def eval_SetComp(self, node: ast.SetComp) -> Set[Any]:
        return set(self._eval_comp(node.elt, node.generators, set))

    def eval_DictComp(self, node: ast.DictComp) -> Dict[Any, Any]:
        result = {}
        self._eval_dict_comp(node.key, node.value, node.generators, result)
        return result

    def eval_GeneratorExp(self, node: ast.GeneratorExp) -> Iterator[Any]:
        def gen():
            yield from self._eval_comp(node.elt, node.generators, (lambda x: (yield x)))
        return gen()

    def _eval_comp(self, elt: ast.expr, generators: List[ast.comprehension], collector: Callable) -> Any:
        def recurse(gens, index=0):
            if index >= len(generators):
                return collector(self.eval(elt))
            gen = gens[index]
            result = collector()
            try:
                for item in self.eval(gen.iter):
                    old_env = self.current_env
                    self.current_env = Environment(self, old_env)
                    self.assign_target(gen.target, item)
                    if all(self.eval(test) for test in gen.ifs):
                        inner = recurse(gens, index + 1)
                        if callable(collector) and collector.__name__ == '<lambda>':
                            yield from inner
                        elif isinstance(result, list):
                            result.extend(inner if isinstance(inner, list) else [inner])
                        elif isinstance(result, set):
                            result.update(inner if isinstance(inner, set) else {inner})
                    self.current_env = old_env
                return result
            except TypeError as e:
                raise TypeError(f"'{type(self.eval(gen.iter)).__name__}' object is not iterable at line {self.get_lineno(gen.iter)}") from e
        return recurse(generators)

    def _eval_dict_comp(self, key: ast.expr, value: ast.expr, generators: List[ast.comprehension], result: Dict) -> None:
        def recurse(gens, index=0):
            if index >= len(generators):
                result[self.eval(key)] = self.eval(value)
                return
            gen = gens[index]
            try:
                for item in self.eval(gen.iter):
                    old_env = self.current_env
                    self.current_env = Environment(self, old_env)
                    self.assign_target(gen.target, item)
                    if all(self.eval(test) for test in gen.ifs):
                        recurse(gens, index + 1)
                    self.current_env = old_env
            except TypeError as e:
                raise TypeError(f"'{type(self.eval(gen.iter)).__name__}' object is not iterable at line {self.get_lineno(gen.iter)}") from e
        recurse(gens=generators)

    def apply_cmp_operator(self, left: Any, op: ast.cmpop, right: Any) -> bool:
        op_map = {
            ast.Eq: lambda l, r: l == r,
            ast.NotEq: lambda l, r: l != r,
            ast.Lt: lambda l, r: l < r,
            ast.LtE: lambda l, r: l <= r,
            ast.Gt: lambda l, r: l > r,
            ast.GtE: lambda l, r: l >= r,
            ast.Is: lambda l, r: l is r,
            ast.IsNot: lambda l, r: l is not r,
            ast.In: lambda l, r: l in r,
            ast.NotIn: lambda l, r: l not in r,
        }
        func = op_map.get(type(op))
        if func is None:
            raise NotImplementedError(f"Comparison {type(op).__name__} not supported at line {self.get_lineno(node)}")
        try:
            return func(left, right)
        except Exception as e:
            raise TypeError(f"Unsupported comparison {type(op).__name__} between '{type(left).__name__}' and '{type(right).__name__}' at line {self.get_lineno(node)}") from e

    def eval_FormattedValue(self, node: ast.FormattedValue) -> str:
        value = self.eval(node.value)
        if node.conversion != -1:
            conv = chr(node.conversion)
            if conv == 's':
                value = str(value)
            elif conv == 'r':
                value = repr(value)
            elif conv == 'a':
                value = ascii(value)
        spec = self.eval(node.format_spec) if node.format_spec else ''
        try:
            return format(value, spec)
        except ValueError as e:
            raise ValueError(f"Invalid format specification at line {self.get_lineno(node)}: {str(e)}") from e

    def eval_Constant(self, node: ast.Constant) -> Any:
        return node.value
    
    def eval_List(self, node: ast.List) -> List[Any]:
        return [self.eval(elt) for elt in node.elts]

    def eval_Tuple(self, node: ast.Tuple) -> Tuple[Any, ...]:
        return tuple(self.eval(elt) for elt in node.elts)

    def eval_Slice(self, node: ast.Slice) -> slice:
        lower = self.eval(node.lower) if node.lower else None
        upper = self.eval(node.upper) if node.upper else None
        step = self.eval(node.step) if node.step else None
        return slice(lower, upper, step)
    
    def eval_JoinedStr(self, node: ast.JoinedStr):
        """Evaluate f-strings and joined strings."""
        parts = []
        for value_node in node.values:
            if isinstance(value_node, ast.Constant):
                parts.append(str(value_node.value))
            elif isinstance(value_node, ast.FormattedValue):
                # Evaluate the expression inside {}
                value = self.eval(value_node.value)
                # Apply formatting if specified
                if value_node.format_spec:
                    format_spec = self._eval_format_spec(value_node.format_spec)
                    parts.append(format(value, format_spec))
                else:
                    parts.append(str(value))
            else:
                # Handle other node types if needed
                value = self.eval(value_node)
                parts.append(str(value))
        
        return ''.join(parts)
