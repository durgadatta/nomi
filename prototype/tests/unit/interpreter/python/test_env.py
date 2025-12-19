'''
Later move env-specific part to a separate module (now they are in base.py)
'''
import pytest

from prototype.interpreter.python.base import Environment

# Test double for Interpreter
class MockInterpreter:
    def __init__(self):
        self.global_env = None

class TestEnvironment:
    """Unit tests for Environment class using pytest."""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup before each test."""
        self.mock_interpreter = MockInterpreter()
        self.global_env = Environment(self.mock_interpreter)
        self.mock_interpreter.global_env = self.global_env
    
    def test_initialization(self):
        """Test environment initialization."""
        env = Environment(self.mock_interpreter)
        assert env.interpreter == self.mock_interpreter
        assert env.parent is None
        assert env.bindings == {}
        assert env.declared_globals == set()
        assert env.declared_nonlocals == set()
        
    def test_initialization_with_parent(self):
        """Test environment initialization with parent."""
        parent_env = Environment(self.mock_interpreter)
        child_env = Environment(self.mock_interpreter, parent_env)
        assert child_env.parent == parent_env
    
    def test_get_local_variable(self):
        """Test getting a variable from local scope."""
        env = Environment(self.mock_interpreter)
        env.bindings["x"] = 42
        assert env.get("x") == 42
    
    def test_get_from_parent_scope(self):
        """Test getting a variable from parent scope."""
        parent = Environment(self.mock_interpreter)
        parent.bindings["x"] = 42
        
        child = Environment(self.mock_interpreter, parent)
        assert child.get("x") == 42
    
    def test_get_from_multiple_levels(self):
        """Test getting a variable from nested scopes."""
        grandparent = Environment(self.mock_interpreter)
        grandparent.bindings["x"] = 42
        
        parent = Environment(self.mock_interpreter, grandparent)
        child = Environment(self.mock_interpreter, parent)
        
        assert child.get("x") == 42
    
    def test_get_nonexistent_variable_raises(self):
        """Test getting a nonexistent variable raises NameError."""
        env = Environment(self.mock_interpreter)
        with pytest.raises(NameError, match="name 'nonexistent' is not defined"):
            env.get("nonexistent")
    
    def test_set_local_variable(self):
        """Test setting a local variable."""
        env = Environment(self.mock_interpreter)
        env.set("x", 42)
        assert env.bindings["x"] == 42
    
    def test_set_overwrites_existing(self):
        """Test setting overwrites existing variable."""
        env = Environment(self.mock_interpreter)
        env.bindings["x"] = 10
        env.set("x", 20)
        assert env.bindings["x"] == 20
    
    def test_set_global_variable(self):
        """Test setting a declared global variable."""
        env = Environment(self.mock_interpreter)
        env.declared_globals.add("x")
        
        env.set("x", 42)
        assert self.global_env.bindings["x"] == 42
        assert "x" not in env.bindings
    
    def test_set_nonlocal_variable(self):
        """Test setting a declared nonlocal variable in parent scope."""
        parent = Environment(self.mock_interpreter)
        parent.bindings["x"] = 10
        
        child = Environment(self.mock_interpreter, parent)
        child.declared_nonlocals.add("x")
        
        child.set("x", 20)
        assert parent.bindings["x"] == 20
        assert "x" not in child.bindings
    
    def test_set_nonlocal_variable_multiple_levels(self):
        """Test setting a nonlocal variable through multiple scopes."""
        grandparent = Environment(self.mock_interpreter)
        grandparent.bindings["x"] = 10
        
        parent = Environment(self.mock_interpreter, grandparent)
        child = Environment(self.mock_interpreter, parent)
        child.declared_nonlocals.add("x")
        
        child.set("x", 20)
        assert grandparent.bindings["x"] == 20
    
    def test_set_nonlocal_not_found_raises(self):
        """Test setting a nonlocal variable that doesn't exist raises NameError."""
        parent = Environment(self.mock_interpreter)
        child = Environment(self.mock_interpreter, parent)
        child.declared_nonlocals.add("x")
        
        with pytest.raises(NameError, match="nonlocal name 'x' not found"):
            child.set("x", 20)
    
    def test_set_nonlocal_variable_prefers_nearest_scope(self):
        """Test that nonlocal assignment finds the nearest enclosing scope with the variable."""
        outer = Environment(self.mock_interpreter)
        outer.bindings["x"] = 10
        
        middle = Environment(self.mock_interpreter, outer)
        middle.bindings["x"] = 20  # Shadows outer x
        
        inner = Environment(self.mock_interpreter, middle)
        inner.declared_nonlocals.add("x")
        
        inner.set("x", 30)
        assert middle.bindings["x"] == 30  # Updates middle's x, not outer's
        assert outer.bindings["x"] == 10
    
    def test_delete_local_variable(self):
        """Test deleting a local variable."""
        env = Environment(self.mock_interpreter)
        env.bindings["x"] = 42
        env.delete("x")
        assert "x" not in env.bindings
    
    def test_delete_from_parent(self):
        """Test deleting a variable from parent scope."""
        parent = Environment(self.mock_interpreter)
        parent.bindings["x"] = 42
        
        child = Environment(self.mock_interpreter, parent)
        child.delete("x")
        assert "x" not in parent.bindings
    
    def test_delete_nonexistent_raises(self):
        """Test deleting a nonexistent variable raises NameError."""
        env = Environment(self.mock_interpreter)
        with pytest.raises(NameError, match="name 'nonexistent' is not defined"):
            env.delete("nonexistent")
    
    def test_copy_creates_shallow_copy(self):
        """Test that copy creates a shallow copy of the environment."""
        parent = Environment(self.mock_interpreter)
        parent.bindings["parent_var"] = 1
        parent.declared_globals.add("global_var")
        
        env = Environment(self.mock_interpreter, parent)
        env.bindings["local_var"] = 2
        env.declared_nonlocals.add("nonlocal_var")
        
        copy = env.copy()
        
        # Check basic attributes
        assert copy.interpreter == env.interpreter
        assert copy.parent == env.parent
        
        # Check copies are separate
        assert copy.bindings == env.bindings
        assert copy.declared_globals == env.declared_globals
        assert copy.declared_nonlocals == env.declared_nonlocals
        
        # Modifying copy shouldn't affect original
        copy.bindings["new_var"] = 3
        assert "new_var" not in env.bindings
        
        # Shallow copy means nested objects are shared
        mutable_obj = [1, 2, 3]
        env.bindings["mutable"] = mutable_obj
        copy = env.copy()
        copy.bindings["mutable"].append(4)
        assert env.bindings["mutable"] == [1, 2, 3, 4]
    
    def test_copy_without_parent(self):
        """Test copying an environment without parent."""
        env = Environment(self.mock_interpreter)
        env.bindings["x"] = 42
        copy = env.copy()
        assert copy.parent is None
        assert copy.bindings["x"] == 42
    
    def test_variable_shadowing(self):
        """Test that variables can shadow parent variables."""
        parent = Environment(self.mock_interpreter)
        parent.bindings["x"] = 10
        
        child = Environment(self.mock_interpreter, parent)
        child.bindings["x"] = 20  # Shadows parent's x
        
        assert child.get("x") == 20
        assert parent.get("x") == 10
    
    def test_global_overrides_parent(self):
        """Test that global declaration overrides parent lookups."""
        grandparent = Environment(self.mock_interpreter)
        grandparent.bindings["x"] = 10
        
        parent = Environment(self.mock_interpreter, grandparent)
        parent.bindings["x"] = 20
        
        child = Environment(self.mock_interpreter, parent)
        child.declared_globals.add("x")
        
        # Setting should go to global
        child.set("x", 30)
        assert self.global_env.bindings["x"] == 30
        assert parent.bindings["x"] == 20
        assert grandparent.bindings["x"] == 10
        
        # Getting should come from global
        assert child.get("x") == 30
    
    def test_empty_environment_operations(self):
        """Test operations on empty environment."""
        env = Environment(self.mock_interpreter)
        
        # Getting should fail
        with pytest.raises(NameError):
            env.get("anything")
        
        # Setting should work
        env.set("new", "value")
        assert env.bindings["new"] == "value"
        
        # Deleting should fail
        with pytest.raises(NameError):
            env.delete("nonexistent")
    
    def test_interpreter_reference(self):
        """Test that interpreter reference is properly maintained."""
        interpreter = MockInterpreter()
        env = Environment(interpreter)
        assert env.interpreter == interpreter
        
        # Test in child environment
        child = Environment(interpreter, env)
        assert child.interpreter == interpreter
    
    def test_set_without_declarations(self):
        """Test setting without any global/nonlocal declarations behaves as local."""
        parent = Environment(self.mock_interpreter)
        parent.bindings["x"] = 10
        
        child = Environment(self.mock_interpreter, parent)
        
        # This should create a local variable, not modify parent
        child.set("y", 20)
        assert child.bindings["y"] == 20
        assert "y" not in parent.bindings
        
        # This should create a local variable, shadowing parent
        child.set("x", 30)
        assert child.bindings["x"] == 30
        assert parent.bindings["x"] == 10  # Parent unchanged
    
    @pytest.mark.parametrize("method_name,value", [
        ("get", None),
        ("set", 42),
        ("delete", None),
    ])
    def test_methods_accept_string_names(self, method_name, value):
        """Test that all methods accept string names."""
        env = Environment(self.mock_interpreter)
        env.bindings["test_var"] = 10
        
        method = getattr(env, method_name)
        
        if value is None:
            if method_name == "get":
                result = method("test_var")
                assert result == 10
            elif method_name == "delete":
                method("test_var")
                assert "test_var" not in env.bindings
        else:
            method("test_var", value)
            if method_name == "set":
                assert env.bindings["test_var"] == value