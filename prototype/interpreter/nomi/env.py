from typing import Any, Dict, Callable, Optional

from prototype.syntax.surface import BindingTarget

from ..python.env import Environment as PyEnvironment
from .binding_error import BindingError


class Environment(PyEnvironment):
    __slots__ = ('constraints', 'constraint_targets')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.constraints: Dict[str, Callable[[Any], bool]] = {}
        self.constraint_targets: Dict[str, BindingTarget] = {}

    def get_constraints(self, name: str) -> Optional[Callable[[Any], bool]]:
        if name in self.constraints:
            return self.constraints[name]
        if self.parent:
            return self.parent.get_constraints(name)
        return None

    def get_constraint_target(self, name: str) -> Optional[BindingTarget]:
        if name in self.constraint_targets:
            return self.constraint_targets[name]
        if self.parent and hasattr(self.parent, "get_constraint_target"):
            return self.parent.get_constraint_target(name)
        return None

    def set_constraint(
        self,
        name: str,
        predicate: Callable[[Any], bool],
        *,
        target: BindingTarget | None = None,
    ):
        self.constraints[name] = predicate
        if target is not None:
            self.constraint_targets[name] = target
        else:
            self.constraint_targets.pop(name, None)

    def delete_constraint(self, name: str):
        if name in self.constraints:
            del self.constraints[name]
        self.constraint_targets.pop(name, None)

    def copy(self) -> 'Environment':
        new_env = super().copy()
        new_env.constraints = self.constraints.copy()
        new_env.constraint_targets = self.constraint_targets.copy()
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
