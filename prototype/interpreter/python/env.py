from typing import Dict, Any, Optional, Set

class Environment:
    """Manages variable scopes and bindings."""

    __slots__ = ('interpreter', 'parent', 'bindings', 'declared_globals', 'declared_nonlocals')

    def __init__(self, interpreter: 'Interpreter', parent: Optional['Environment'] = None):
        self.interpreter = interpreter
        self.parent = parent
        self.bindings: Dict[str, Any] = {}
        self.declared_globals: Set[str] = set()
        self.declared_nonlocals: Set[str] = set()

    def _find_nonlocal_env(self, name: str) -> 'Environment':
        env = self.parent
        while env and name not in env.bindings:
            env = env.parent
        if env is None:
            raise NameError(f"nonlocal name '{name}' not found")
        return env

    def _assignment_env(self, name: str) -> 'Environment':
        if name in self.declared_globals:
            return self.interpreter.global_env
        if name in self.declared_nonlocals:
            return self._find_nonlocal_env(name)
        return self

    def get(self, name: str) -> Any:
        if name in self.declared_globals:
            return self.interpreter.global_env.get(name)
        if name in self.bindings:
            return self.bindings[name]
        if self.parent:
            return self.parent.get(name)
        raise NameError(f"name '{name}' is not defined")

    def set(self, name: str, value: Any):
        self._assignment_env(name).bindings[name] = value

    def delete(self, name: str):
        if name in self.bindings:
            del self.bindings[name]
        elif self.parent:
            self.parent.delete(name)
        else:
            raise NameError(f"name '{name}' is not defined")
        
    def copy(self) -> 'Environment':
        """Create a shallow copy of this environment."""
        new_env = type(self)(self.interpreter, self.parent)
        new_env.bindings = self.bindings.copy()
        new_env.declared_globals = self.declared_globals.copy()
        new_env.declared_nonlocals = self.declared_nonlocals.copy()
        return new_env
        
