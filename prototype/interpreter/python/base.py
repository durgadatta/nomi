import ast
from typing import Dict, Any, Iterator

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
        
class GeneratorState:
    """Manages state for generator functions."""
    
    def __init__(self, interpreter: 'Interpreter', body: List[ast.stmt], env: 'Environment'):
        self.interpreter = interpreter
        self.body = body
        self.env = env
        self.index = 0
        self.active = True
        self.return_value = None
        self.compound_state = None

    def __iter__(self):
        return self

    def __next__(self):
        if not self.active:
            raise StopIteration(self.return_value)
        
        old_env = self.interpreter.current_env
        self.interpreter.current_env = self.env
        try:
            # Check for compound state to resume
            if self.compound_state:
                return self._resume_compound_statement()

            # Execute statements sequentially
            while self.index < len(self.body):
                stmt = self.body[self.index]
                
                try:
                    if isinstance(stmt, ast.For):
                        self.interpreter.eval_For(stmt, self)
                    elif isinstance(stmt, ast.While): 
                        self.interpreter.eval_While(stmt, self)
                    else:
                        self.interpreter.eval(stmt)
                    self.index += 1
                
                except YieldException as ye:
                    if not self.compound_state:
                        self.index += 1
                    return ye.value

                except ReturnException as re:
                    self.active = False
                    self.return_value = re.value
                    raise StopIteration(self.return_value)
                    
            self.active = False
            raise StopIteration(self.return_value)
        finally:
            self.interpreter.current_env = old_env

    def _resume_compound_statement(self):
        """Resumes a paused compound statement."""
        state = self.compound_state
        if not state:
            return self.__next__()
            
        node = state['node']
        
        try:
            if isinstance(node, ast.For):
                self.interpreter.resume_For(node, self)
            elif isinstance(node, ast.While):  # ADD THIS
                self.interpreter.resume_While(node, self)  # ADD THIS
            # Add other compound statement types here
            
        except YieldException as ye:
            return ye.value
            
        except Exception:
            self.compound_state = None
            raise

        # Compound statement finished
        self.compound_state = None
        self.index += 1
        return self.__next__()

    def get_lineno(self) -> int:
        if self.compound_state:
            node = self.compound_state['node']
            if self.compound_state['type'] == 'For':
                idx = self.compound_state['body_index']
                if idx < len(node.body):
                    return getattr(node.body[idx], 'lineno', 1)
            elif self.compound_state['type'] == 'While':  # ADD THIS
                idx = self.compound_state['body_index']  # ADD THIS
                if idx < len(node.body):  # ADD THIS
                    return getattr(node.body[idx], 'lineno', 1)  # ADD THIS
            return getattr(node, 'lineno', 1)

        if self.index < len(self.body):
            return getattr(self.body[self.index], 'lineno', 1)
        return 1