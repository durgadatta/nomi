import ast
from typing import Dict, Any, List, Iterator, Callable
from typing import Tuple, Set, Callable, List, Dict, Any, Iterator


class DataStructMixin:
    def eval_Dict(self, node: ast.Dict) -> Dict[Any, Any]:
        result = {}
        for key, value in zip(node.keys, node.values):
            if key is None:
                result.update(self.eval(value))
            else:
                result[self.eval(key)] = self.eval(value)
        return result
   
    def eval_SetComp(self, node: ast.SetComp) -> Set[Any]:
        result = set(self._eval_comp(node.elt, node.generators, set))
        #NOTE: Convert to sorted list for consistent output in tests
        return set(sorted(result))

    def eval_ListComp(self, node: ast.ListComp) -> List[Any]:
        return list(self._eval_comp(node.elt, node.generators, list))

    def eval_GeneratorExp(self, node: ast.GeneratorExp) -> Iterator[Any]:
        return self._eval_comp(node.elt, node.generators, (lambda x: (yield x)))


    def eval_DictComp(self, node: ast.DictComp) -> Dict[Any, Any]:
        result = {}
        self._eval_dict_comp(node.key, node.value, node.generators, result)
        return result

    def _eval_comp(self, elt: ast.expr, generators: List[ast.comprehension], collector: Callable) -> Any:
        def recurse(gens, index=0):
            if index >= len(generators):
                # Base case: evaluate the element
                value = self.eval(elt)
                if collector is set:
                    return {value}
                elif collector is list:
                    return [value]
                else:
                    # Only use yield for actual generator expressions
                    return collector(value)
            
            gen = gens[index]
            
            # Create the appropriate result container
            if collector is set:
                result = set()
            elif collector is list:
                result = []
            else:
                # For generator expressions, we need to yield values
                def gen_func():
                    for item in self.eval(gen.iter):
                        with self.this_env(self.env_class(self, self.current_env)):
                            self.assign_target(gen.target, item)
                            if all(self.eval(test) for test in gen.ifs):
                                inner = recurse(gens, index + 1)
                                yield from inner
                return gen_func()
            
            # Handle set and list comprehensions (non-generator cases)
            for item in self.eval(gen.iter):
                with self.this_env(self.env_class(self, self.current_env)):
                    self.assign_target(gen.target, item)
                    if all(self.eval(test) for test in gen.ifs):
                        inner = recurse(gens, index + 1)
                        
                        if collector is set:
                            if isinstance(inner, set):
                                result |= inner
                            else:
                                result.add(inner)
                        elif collector is list:
                            if isinstance(inner, list):
                                result.extend(inner)
                            else:
                                result.append(inner)
            return result
        
        return recurse(generators)

    def _eval_dict_comp(self, key: ast.expr, value: ast.expr, generators: List[ast.comprehension], result: Dict) -> None:
        def recurse(gens, index=0):
            if index >= len(generators):
                result[self.eval(key)] = self.eval(value)
                return
            gen = gens[index]
            try:
                for item in self.eval(gen.iter):
                    with self.this_env(self.env_class(self,  self.current_env)):
                        self.assign_target(gen.target, item)
                        if all(self.eval(test) for test in gen.ifs):
                            recurse(gens, index + 1)
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
        result = []
        for elt in node.elts:
            if isinstance(elt, ast.Starred):
                result.extend(self.eval(elt))
            else:
                result.append(self.eval(elt))
        return result

    def eval_Tuple(self, node: ast.Tuple) -> Tuple[Any, ...]:
        result = []
        for elt in node.elts:
            if isinstance(elt, ast.Starred):
                result.extend(self.eval(elt))
            else:
                result.append(self.eval(elt))
        return tuple(result)

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
                parts.append(self.eval_FormattedValue(value_node))
            else:
                # Handle other node types if needed
                value = self.eval(value_node)
                parts.append(str(value))
        
        return ''.join(parts)
