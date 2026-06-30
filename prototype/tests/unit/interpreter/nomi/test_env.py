import pytest
from typing import Any, Callable

from prototype.interpreter.nomi.env import Environment
from prototype.syntax.surface import BindingTarget

class MockInterpreter:
    def __init__(self):
        self.global_env = Environment(self)

class TestEnvironmentConstraints:
    """Tests for Environment class constraint functionality."""
    
    @pytest.fixture
    def interpreter(self):
        """Create interpreter with proper global environment."""
        interpreter = MockInterpreter()
        return interpreter
    
    @pytest.fixture
    def env(self, interpreter):
        """Create a basic environment."""
        return Environment(interpreter)
    
    def test_constraint_enforced_on_set(self, env):
        """Constraint is checked when setting a value."""
        env.set_constraint("x", lambda v: isinstance(v, int))
        
        env.set("x", 42)
        assert env.get("x") == 42
        
        with pytest.raises(TypeError, match="does not satisfy constraint"):
            env.set("x", "not an int")
        assert env.get("x") == 42

    def test_binding_commit_prepares_without_mutating(self, env):
        """Preparing a checked binding does not write until commit."""
        target = BindingTarget(name="x", role="assignment")
        env.set_constraint("x", lambda v: isinstance(v, int), target=target)

        commit = env._prepare_binding_commit("x", 42)

        assert "x" not in env.bindings
        assert commit.name == "x"
        assert commit.value == 42
        assert commit.target is target

        env._commit_binding(commit)
        assert env.get("x") == 42
    
    def test_new_type_annotation_replaces_constraint(self, env):
        """New type annotation completely replaces old constraint."""
        env.set_constraint("x", lambda v: isinstance(v, int))
        env.set("x", 10)
        
        env.set_constraint("x", lambda v: isinstance(v, str))
        
        env.set("x", "hello")
        assert env.get("x") == "hello"
        
        with pytest.raises(TypeError):
            env.set("x", 20)
        assert env.get("x") == "hello"
    
    def test_constraints_only_checked_in_local_scope(self, interpreter):
        """Constraints are only checked in the scope where set() is called."""
        parent = Environment(interpreter)
        
        parent.set_constraint("data", lambda v: isinstance(v, int))
        parent.set("data", 100)
        
        child = Environment(interpreter, parent)
        
        child.set("data", "string")
        assert child.get("data") == "string"
        assert parent.get("data") == 100
    
    def test_global_variables_check_global_constraints(self, interpreter):
        """Global variables use constraints from the global environment."""
        global_env = interpreter.global_env
        
        global_env.set_constraint("CONFIG", lambda v: isinstance(v, dict))
        global_env.set("CONFIG", {"debug": True})
        
        child = Environment(interpreter, global_env)
        child.declared_globals.add("CONFIG")
        
        child.set("CONFIG", {"debug": False})
        assert global_env.get("CONFIG") == {"debug": False}
        
        with pytest.raises(TypeError):
            child.set("CONFIG", "not a dict")
    
    def test_nonlocal_finds_nearest_binding_for_constraint(self, interpreter):
        """Nonlocal looks for constraint in the nearest scope with the variable."""
        outer = Environment(interpreter)
        outer.set_constraint("counter", lambda v: isinstance(v, int))
        outer.set("counter", 0)
        
        inner = Environment(interpreter, outer)
        inner.declared_nonlocals.add("counter")
        
        inner.set("counter", 5)
        assert outer.get("counter") == 5
        
        with pytest.raises(TypeError):
            inner.set("counter", "not an int")
    
    def test_deleting_constraint_removes_restrictions(self, env):
        """After deleting constraint, any value can be set."""
        env.set_constraint("value", lambda v: isinstance(v, int))
        env.set("value", 42)
        
        env.delete_constraint("value")
        
        env.set("value", "now a string")
        env.set("value", {"nested": "object"})
        
        assert env.get("value") == {"nested": "object"}
        assert env.get_constraint_target("value") is None
    
    def test_shadowed_variables_can_have_different_constraints(self, interpreter):
        """Child can shadow a parent variable with a different constraint."""
        parent = Environment(interpreter)
        
        parent.set_constraint("id", lambda v: isinstance(v, int))
        parent.set("id", 1)
        
        child = Environment(interpreter, parent)
        child.set_constraint("id", lambda v: isinstance(v, str))
        child.set("id", "user_1")
        
        assert child.get("id") == "user_1"
        assert parent.get("id") == 1

    def test_constraint_target_metadata_is_preserved(self, env):
        """Constraint metadata is stored beside the runtime predicate."""
        target = BindingTarget(
            name="age",
            role="assignment",
            constraint=None,
        )

        env.set_constraint("age", lambda v: isinstance(v, int), target=target)

        assert env.get_constraint_target("age") is target
        assert env.copy().get_constraint_target("age") is target

    def test_child_environment_can_read_parent_constraint_target(self, interpreter):
        """Inherited constraints expose inherited target metadata too."""
        parent = Environment(interpreter)
        target = BindingTarget(name="port", role="assignment")
        parent.set_constraint("port", lambda v: isinstance(v, int), target=target)

        child = Environment(interpreter, parent)

        assert child.get_constraint_target("port") is target
