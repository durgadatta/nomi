import pytest

from prototype.interpreter.python.env import Environment
import pytest

class MockInterpreter:
    def __init__(self):
        self.global_env = None

class TestEnvironment:
    """Tests for Environment class."""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        self.mock_interpreter = MockInterpreter()
        self.global_env = Environment(self.mock_interpreter)
        self.mock_interpreter.global_env = self.global_env
    
    def test_initialization(self):
        env = Environment(self.mock_interpreter)
        assert env.interpreter == self.mock_interpreter
        assert env.parent is None
        assert env.bindings == {}
    
    def test_get_local_and_parent_variables(self):
        parent = Environment(self.mock_interpreter)
        parent.bindings["x"] = 10
        parent.bindings["y"] = 20
        
        child = Environment(self.mock_interpreter, parent)
        child.bindings["y"] = 30
        
        assert child.get("x") == 10
        assert child.get("y") == 30
    
    def test_get_from_deeply_nested_scope(self):
        level1 = Environment(self.mock_interpreter)
        level1.bindings["var"] = 1
        
        level2 = Environment(self.mock_interpreter, level1)
        level3 = Environment(self.mock_interpreter, level2)
        
        assert level3.get("var") == 1
    
    def test_get_nonexistent_variable_raises_error(self):
        env = Environment(self.mock_interpreter)
        with pytest.raises(NameError):
            env.get("missing")
    
    def test_set_creates_local_by_default(self):
        env = Environment(self.mock_interpreter)
        env.set("x", 100)
        assert env.bindings["x"] == 100
    
    def test_set_updates_existing_variable(self):
        env = Environment(self.mock_interpreter)
        env.bindings["counter"] = 5
        env.set("counter", 6)
        assert env.bindings["counter"] == 6
    
    def test_global_declaration_sets_global_scope(self):
        env = Environment(self.mock_interpreter)
        env.declared_globals.add("config")
        
        env.set("config", {"mode": "debug"})
        assert self.global_env.bindings["config"] == {"mode": "debug"}
        assert "config" not in env.bindings
    
    def test_nonlocal_declaration_sets_parent_scope(self):
        parent = Environment(self.mock_interpreter)
        parent.bindings["counter"] = 0
        
        child = Environment(self.mock_interpreter, parent)
        child.declared_nonlocals.add("counter")
        
        child.set("counter", 1)
        assert parent.bindings["counter"] == 1
        assert "counter" not in child.bindings
    
    def test_nonlocal_finds_nearest_enclosing_binding(self):
        outer = Environment(self.mock_interpreter)
        outer.bindings["x"] = 1
        
        middle = Environment(self.mock_interpreter, outer)
        middle.bindings["x"] = 2
        
        inner = Environment(self.mock_interpreter, middle)
        inner.declared_nonlocals.add("x")
        
        inner.set("x", 3)
        assert middle.bindings["x"] == 3
        assert outer.bindings["x"] == 1
    
    def test_nonlocal_without_binding_raises_error(self):
        parent = Environment(self.mock_interpreter)
        child = Environment(self.mock_interpreter, parent)
        child.declared_nonlocals.add("missing")
        
        with pytest.raises(NameError):
            child.set("missing", "value")
    
    def test_delete_removes_local_variable(self):
        env = Environment(self.mock_interpreter)
        env.bindings["temp"] = "data"
        env.delete("temp")
        assert "temp" not in env.bindings
    
    def test_delete_from_parent_scope(self):
        parent = Environment(self.mock_interpreter)
        parent.bindings["shared"] = True
        
        child = Environment(self.mock_interpreter, parent)
        child.delete("shared")
        assert "shared" not in parent.bindings
    
    def test_delete_missing_variable_raises_error(self):
        env = Environment(self.mock_interpreter)
        with pytest.raises(NameError):
            env.delete("nonexistent")
    
    def test_copy_creates_independent_environment(self):
        original = Environment(self.mock_interpreter)
        original.bindings["a"] = 1
        original.declared_globals.add("g")
        
        copied = original.copy()
        
        assert copied.bindings == original.bindings
        assert copied.declared_globals == original.declared_globals
        
        copied.bindings["b"] = 2
        assert "b" not in original.bindings
    
    def test_copy_preserves_parent_reference(self):
        parent = Environment(self.mock_interpreter)
        child = Environment(self.mock_interpreter, parent)
        
        copied = child.copy()
        assert copied.parent == parent
    
    def test_global_declaration_overrides_local_lookup(self):
        parent = Environment(self.mock_interpreter)
        parent.bindings["setting"] = "parent_value"
        
        child = Environment(self.mock_interpreter, parent)
        child.declared_globals.add("setting")
        
        self.global_env.bindings["setting"] = "global_default"
        child.set("setting", "global_updated")
        
        assert self.global_env.bindings["setting"] == "global_updated"
        assert child.get("setting") == "global_updated"
    
    def test_shadowing_creates_separate_variables(self):
        parent = Environment(self.mock_interpreter)
        parent.bindings["name"] = "parent"
        
        child = Environment(self.mock_interpreter, parent)
        child.bindings["name"] = "child"
        
        assert parent.get("name") == "parent"
        assert child.get("name") == "child"