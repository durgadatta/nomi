'''
essentially all expression are function call or var ref, so most changes will concentrate here
thus, separating this into a new file
'''
import ast
from typing import Any

class FunctionCallMixin:
    def eval_Call(self, node: ast.Call) -> Any:
        func = self.eval(node.func)
        # Evaluate arguments
        posargs = []
        for arg in node.args:
            if isinstance(arg, ast.Starred):
                posargs.extend(self.eval(arg.value))
            else:
                posargs.append(self.eval(arg))

        kwargs = {}
        for kw in node.keywords:
            if kw.arg is None:
                kw_val = self.eval(kw.value)
                if not isinstance(kw_val, dict):
                    raise TypeError(f"argument after ** must be a mapping at line {self.get_lineno(node)}")
                kwargs.update(kw_val)
            else:
                value = kw.value
                # if it is a block arg; don't eval it
                # generator state will eval it in the caller's env
                if kw.arg == '__block__':
                    value = (*value, self.current_env)
                else:
                    value = self.eval(kw.value)
                kwargs[kw.arg] = value

        return func(*posargs, **kwargs)