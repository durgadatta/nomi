from typing import Any, List, Dict, Callable
from ..python.env import Environment as PyEnvironment

class Environment(PyEnvironment):
    def __init__(self, *args, **kwargs):
        '''
        add optional constraint for each binding based
        on the variable annotation; enforced during set()
        '''
        super().__init__(*args, **kwargs)
        self.constraints: Dict[str, Callable[[Any], bool]] = {}

    def get_constraints(self, name: str) -> List[Callable[[Any], bool]]:
        """Get constraints for a variable, checking parent scopes."""
        if name in self.constraints:
            return self.constraints[name]
        if self.parent:
            return self.parent.get_constraints(name)
        return []

    def set_constraint(self, name: str, predicate: Callable[[Any], bool]):
        """Set constraint predicate for a variable."""
        self.constraints[name] = predicate

    def delete_constraint(self, name: str):
        """Delete constraint for a variable."""
        if name in self.constraints:
            del self.constraints[name]

    def copy(self) -> 'Environment':
        """Create a shallow copy of this environment."""
        new_env = super().copy()
        new_env.constraints = self.constraints.copy()
        return new_env
    
    def set(self, name: str, value: Any):
        #TODO: for global/non-local we should get constraints the same way 
        # we get the binding; get/set should be in sync with regards 
        # to scope
        # Check constraints before setting the value
        if name in self.constraints:
            predicate = self.constraints[name]
            if not predicate(value):
                # this likely is shadowed; p(v) either is True or raise e
                # refactor alter
                raise TypeError(f"Constraint violation for '{name}': value {value!r} does not satisfy constraint")
        super().set(name, value)