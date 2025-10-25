import ast
from .base import  YieldException, YieldFromException
from typing import Optional
class AsyncMixin:
    def eval_AsyncWith(self, node: ast.AsyncWith) -> None:
        exits = []
        try:
            for item in node.items:
                mgr = self.eval(item.context_expr)
                exit_ = getattr(mgr, '__aexit__', getattr(mgr, '__exit__', None))
                if exit_ is None:
                    raise AttributeError(f"Async context manager missing __aexit__ at line {self.get_lineno(item)}")
                enter = getattr(mgr, '__aenter__', getattr(mgr, '__enter__', lambda: None))
                value = enter()
                exits.append(exit_)
                if item.optional_vars:
                    self.assign_target(item.optional_vars, value)
            for stmt in node.body:
                self.eval(stmt)
        except Exception as e:
            exc_info = (type(e), e, e.__traceback__)
            for exit_ in reversed(exits):
                exit_(exc_info[0], exc_info[1], exc_info[2])
            raise
        else:
            for exit_ in reversed(exits):
                exit_(None, None, None)


    def eval_Await(self, node: ast.Await) -> Any:
        value = self.eval(node.value)
        if hasattr(value, '__await__'):
            try:
                return value.__await__().__next__()
            except StopIteration as e:
                return e.value
        return value

    def eval_Yield(self, node: ast.Yield) -> Any:
        raise YieldException(self.eval(node.value) if node.value else None)

    def eval_YieldFrom(self, node: ast.YieldFrom) -> Any:
        try:
            iterator = iter(self.eval(node.value))
            raise YieldFromException(iterator)
        except TypeError as e:
            raise TypeError(f"'{type(self.eval(node.value)).__name__}' object is not iterable at line {self.get_lineno(node)}") from e

    def eval_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self.eval_FunctionDef(node)



class OthersMixin(AsyncMixin):
    def eval_Import(self, node: ast.Import) -> None:
        for alias in node.names:
            module_name = alias.name
            try:
                module = __import__(module_name)
                name = alias.asname or module_name.split('.')[0]
                self.current_env.set(name, module)
            except ImportError as e:
                raise ImportError(f"Cannot import module '{module_name}' at line {self.get_lineno(node)}: {str(e)}") from e

    def eval_ImportFrom(self, node: ast.ImportFrom) -> None:
        try:
            module = __import__(node.module, level=node.level)
            for alias in node.names:
                name = alias.name
                if name == '*':
                    for n in dir(module):
                        if not n.startswith('_'):
                            self.current_env.set(n, getattr(module, n))
                else:
                    try:
                        obj = getattr(module, name)
                        asname = alias.asname or name
                        self.current_env.set(asname, obj)
                    except AttributeError as e:
                        raise ImportError(f"Cannot import name '{name}' from '{node.module}' at line {self.get_lineno(node)}: {str(e)}") from e
        except ImportError as e:
            raise ImportError(f"Cannot import from module '{node.module}' at line {self.get_lineno(node)}: {str(e)}") from e

    def get_lineno(self, node: Optional[ast.AST]) -> int:
        """Get line number from node, with a default if missing."""
        return getattr(node, 'lineno', 1)
    
    
    def eval_Delete(self, node: ast.Delete) -> None:
        for target in node.targets:
            self.del_target(target)

    def eval_TypeIgnore(self, node: ast.TypeIgnore) -> None:
        pass

    def eval_TypeAlias(self, node: ast.TypeAlias) -> None:
        pass

    def eval_TypeVar(self, node: ast.TypeVar) -> None:
        pass

    def eval_ParamSpec(self, node: ast.ParamSpec) -> None:
        pass

    def eval_TypeVarTuple(self, node: ast.TypeVarTuple) -> None:
        pass