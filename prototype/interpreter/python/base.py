from typing import Dict, Any, Iterator
class GeneratorState:
    """Manages state for generator functions."""
    def __init__(self, interpreter: 'Interpreter', body: List[ast.stmt], env: 'Environment'):
        self.interpreter = interpreter
        self.body = body
        self.env = env
        self.index = 0
        self.active = True
        self.return_value = None

    def __iter__(self):
        return self

    def __next__(self):
        if not self.active:
            raise StopIteration(self.return_value)
        
        old_env = self.interpreter.current_env
        self.interpreter.current_env = self.env
        try:
            while self.index < len(self.body):
                try:
                    self.interpreter.eval(self.body[self.index])
                    self.index += 1
                except YieldException as ye:
                    self.index += 1  # Move to next statement after yield
                    return ye.value
                except YieldFromException as yfe:
                    try:
                        return next(yfe.iterator)
                    except StopIteration as si:
                        if si.value is not None:
                            self.return_value = si.value
                        continue
                except ReturnException as re:
                    self.active = False
                    self.return_value = re.value
                    raise StopIteration(self.return_value)
            self.active = False
            raise StopIteration(self.return_value)
        finally:
            self.interpreter.current_env = old_env

    def get_lineno(self) -> int:
        if self.index < len(self.body):
            return getattr(self.body[self.index], 'lineno', 1)
        return 1
    
class Environment:
    """Manages variable scopes and bindings."""
    def __init__(self, interpreter: 'Interpreter', parent: Optional['Environment'] = None):
        self.interpreter = interpreter
        self.parent = parent
        self.bindings: Dict[str, Any] = {}
        self.declared_globals: Set[str] = set()
        self.declared_nonlocals: Set[str] = set()

    def get(self, name: str) -> Any:
        if name in self.bindings:
            return self.bindings[name]
        if self.parent:
            return self.parent.get(name)
        raise NameError(f"name '{name}' is not defined")

    def set(self, name: str, value: Any):
        if name in self.declared_globals:
            self.interpreter.global_env.bindings[name] = value
        elif name in self.declared_nonlocals:
            env = self.parent
            while env and name not in env.bindings:
                env = env.parent
            if env:
                env.bindings[name] = value
            else:
                raise NameError(f"nonlocal name '{name}' not found")
        else:
            self.bindings[name] = value

    def delete(self, name: str):
        if name in self.bindings:
            del self.bindings[name]
        elif self.parent:
            self.parent.delete(name)
        else:
            raise NameError(f"name '{name}' is not defined")
        
class ControlException(Exception):
    pass

class ReturnException(ControlException):
    def __init__(self, value: Any):
        self.value = value

class BreakException(ControlException):
    pass

class ContinueException(ControlException):
    pass

class YieldException(ControlException):
    def __init__(self, value: Any):
        self.value = value

class YieldFromException(ControlException):
    def __init__(self, iterator: Iterator):
        self.iterator = iterator
