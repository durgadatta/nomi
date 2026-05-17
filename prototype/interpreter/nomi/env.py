from typing import Any, Dict, Callable, Optional
from ..python.env import Environment as PyEnvironment
from .binding_error import BindingError


class Environment(PyEnvironment):
    __slots__ = ('constraints',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.constraints: Dict[str, Callable[[Any], bool]] = {}

    def get_constraints(self, name: str) -> Optional[Callable[[Any], bool]]:
        if name in self.constraints:
            return self.constraints[name]
        if self.parent:
            return self.parent.get_constraints(name)
        return None

    def set_constraint(self, name: str, predicate: Callable[[Any], bool]):
        self.constraints[name] = predicate

    def delete_constraint(self, name: str):
        if name in self.constraints:
            del self.constraints[name]

    def copy(self) -> 'Environment':
        new_env = super().copy()
        new_env.constraints = self.constraints.copy()
        return new_env

    def _assignment_constraint(self, name: str):
        env = self._assignment_env(name)
        return env.constraints.get(name)

    def set(self, name: str, value: Any):
        constraint = self._assignment_constraint(name)
        if constraint is not None and not constraint(value):
            raise BindingError(
                name, value,
                message=f"value {value!r} does not satisfy constraint",
                binding_kind="assignment",
            )
        super().set(name, value)
