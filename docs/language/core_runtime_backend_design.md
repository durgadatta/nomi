# Core Runtime Backend Design

> Status: implementation plan for the next backend after `core_direct.py`.
>
> Scope: a Python-independent-in-design reference runtime that dispatches on all
> registered Core IR node types using Nomi-owned values, scoped environments, explicit
> control flow, and a single eval loop. This is Stage 3 of
> [`python_independence_and_compiler_backend_plan.md`](python_independence_and_compiler_backend_plan.md).

## Motivation

`core_direct.py` proved Core IR dispatch works but is still Python-through-and-through:
flat `dict` environment, Python callables for functions, Python exceptions for
control flow, Python objects for values. A Rust/Wasm/LLVM backend can't use any
of those.

The Core Runtime Backend (`core_runtime.py`) is the reference implementation that
defines Nomi-owned abstractions for every runtime concept. Future native backends
implement the same abstractions in their host language. The Python implementation
serves as the executable spec.

## Architecture

```
Core IR (Module with registered node types)
        |
        v
+-------------------+
| CoreRuntime       |
|                   |
|  eval(node) -> Value | ControlFlow
|                   |
|  +-- Value system  (Int, Float, Bool, Str, Function, Data, Native, Nil)
|  +-- Environment   (linked Frame with capture sets)
|  +-- Control flow  (Return, Break, Continue, Yield — never Python exceptions)
|  +-- Host interop  (explicit Native wrapper, not raw Python objects)
+-------------------+
        |
        v
EvalBackendResult { bindings, value, has_value, diagnostics }
```

### Design Principles

1. **Every abstraction is Nomi-owned.** No raw Python `dict`, `list`, `int`, or
   callable crosses the eval boundary as a semantic value. Python types are
   implementation detail inside the reference, not the interface.

2. **Control flow is explicit.** `Return`, `Break`, `Continue`, `Yield` are
   values, not Python exceptions. A Rust backend can implement them as `enum`
   variants without exception machinery.

3. **Environment is scoped and inspectable.** Linked-list frames with explicit
   capture sets. No `global`/`nonlocal` Python semantics leak through.

4. **Host interop is fenced.** Calling `print`, `len`, or any Python builtin goes
   through an explicit `Native` value wrapper and a `HostCall` capability.
   Backends declare whether they support host calls.

5. **One eval loop, one dispatch table.** The eval method is a single
   `type(node)` dispatch. Backend authors can read it in one screen.

## Value System

```python
# All Nomi runtime values are instances of these types.
# Python int/str/bool/etc. are wrapped, never exposed directly.

@dataclass(frozen=True, slots=True)
class Value:
    """Base for all Nomi runtime values."""

@dataclass(frozen=True, slots=True)
class IntValue(Value):
    value: int

@dataclass(frozen=True, slots=True)
class FloatValue(Value):
    value: float

@dataclass(frozen=True, slots=True)
class BoolValue(Value):
    value: bool

@dataclass(frozen=True, slots=True)
class StrValue(Value):
    value: str

@dataclass(frozen=True, slots=True)
class NilValue(Value):
    """Nomi's unit/absence value. Distinct from Python None."""

@dataclass(frozen=True, slots=True)
class FunctionValue(Value):
    """User-defined function: params + body + closure environment."""
    params: tuple[str, ...]
    body: Module  # Core IR Module
    closure: Frame

@dataclass(frozen=True, slots=True)
class DataValue(Value):
    """Constructed data instance."""
    name: str
    fields: dict[str, Value]

@dataclass(frozen=True, slots=True)
class NativeValue(Value):
    """Wrapped Python callable for host interop. Backend-gated capability."""
    callable: Any  # Python callable, but typed as Any to keep the door open
```

In Rust, these become:
```rust
enum Value {
    Int(i64),
    Float(f64),
    Bool(bool),
    Str(String),
    Function { params: Vec<String>, body: Module, closure: Rc<Frame> },
    Data { name: String, fields: HashMap<String, Value> },
    Native(Box<dyn HostCall>),
    Nil,
}
```

## Environment Model

```python
@dataclass(slots=True)
class Frame:
    """One scope frame. Linked list via parent pointer."""
    bindings: dict[str, Value] = field(default_factory=dict)
    parent: Frame | None = None
    # Which names this frame captures from enclosing scopes.
    # Set at function-creation time; checked at lookup time.
    captures: set[str] = field(default_factory=set)

    def lookup(self, name: str) -> Value | None:
        if name in self.bindings:
            return self.bindings[name]
        if self.parent is not None:
            return self.parent.lookup(name)
        return None

    def assign(self, name: str, value: Value) -> None:
        """Assign in the nearest frame that has this name, or current."""
        if name in self.bindings:
            self.bindings[name] = value
        elif self.parent is not None and self.parent.lookup(name) is not None:
            self.parent.assign(name, value)
        else:
            self.bindings[name] = value

    def extend(self, params: tuple[str, ...], args: list[Value]) -> 'Frame':
        """Create a child frame with params bound to args."""
        child = Frame(parent=self)
        for param, arg in zip(params, args):
            child.bindings[param] = arg
        return child
```

Key properties:
- No `global`/`nonlocal` declarations — those are Python semantics.
- Closure capture is explicit: when a `Function` is evaluated, the current frame
  is snapshotted as the closure.
- Assignment walks the parent chain to find the existing binding, matching
  lexical-scope expectations without Python's declaration model.

## Control Flow

```python
@dataclass(frozen=True, slots=True)
class ControlFlow:
    """Explicit control-flow signal. Never a Python exception."""

@dataclass(frozen=True, slots=True)
class ReturnSignal(ControlFlow):
    value: Value

@dataclass(frozen=True, slots=True)
class BreakSignal(ControlFlow):
    pass

@dataclass(frozen=True, slots=True)
class ContinueSignal(ControlFlow):
    pass

@dataclass(frozen=True, slots=True)
class YieldSignal(ControlFlow):
    value: Value
```

These are returned from `eval()`, not raised. The eval loop checks
`isinstance(result, ControlFlow)` after each sub-evaluation. This maps directly
to `Result<T, ControlFlow>` in Rust or a tagged union in C.

Exception handling (`Raise` / `Handle` nodes) uses `RuntimeError` as a Value
subtype, not Python exceptions:

```python
@dataclass(frozen=True, slots=True)
class ErrorValue(Value):
    message: str
    payload: Value | None = None
```

## Evaluation Loop

The backend class implements:

```python
class CoreRuntime:
    """Reference Nomi runtime. Dispatches registered Core IR node types."""

    spec = CORE_RUNTIME_SPEC  # selectable_for_execution=False initially

    def __init__(self, host_calls: dict[str, Callable] | None = None):
        self._global_frame = Frame()
        self._host_calls = host_calls or {}
        self._resume_stack: list[GeneratorState] = []

    def evaluate(self, core_ir: Module, *, display_last_expr: bool = False
                ) -> EvalBackendResult:
        verify_core(core_ir, strict=True)
        self._current_frame = self._global_frame
        last_value = NilValue()
        for node in core_ir.body:
            result = self.eval(node)
            if isinstance(result, ControlFlow):
                raise RuntimeError(f"Unexpected {type(result).__name__} at module level")
            last_value = result if result is not None else NilValue()
        bindings = {k: self._unbox(v) for k, v in self._global_frame.bindings.items()}
        has_value = display_last_expr and not isinstance(last_value, NilValue)
        return EvalBackendResult(
            bindings=bindings,
            value=self._unbox(last_value) if has_value else None,
            has_value=has_value,
        )

    def eval(self, node: CoreNode) -> Value | ControlFlow:
        """Single dispatch on CoreNode type."""
        ...
```

### Dispatch Table

| Node | eval behavior |
|------|--------------|
| `Module` | Evaluate each body node in sequence. Last expression becomes module value. |
| `Literal` | Wrap Python constant in the matching Value subtype. |
| `Load` | `frame.lookup(name)`. Error if missing. |
| `Bind` | Evaluate `node.value`, then `frame.assign(node.name, result)`. |
| `Function` | Capture current frame as closure. Return `FunctionValue(params, body, closure)`. |
| `Call` | Evaluate `node.func`, evaluate `node.args`. If `NativeValue`, call with unboxed args. If `FunctionValue`, extend frame, eval body, catch `ReturnSignal`. |
| `Return` | Evaluate `node.value`, wrap in `ReturnSignal`. |
| `Yield` | Evaluate optional value and wrap in `YieldSignal`; block/resume semantics are a later capability gate. |
| `Branch` | Evaluate `test`. If truthy, eval `then_body`; else eval `else_body`. |
| `NoOp` | Return `NilValue`; lowers to Python `pass`. |
| `Break` | Return `BreakSignal` for loop dispatch. |
| `Continue` | Return `ContinueSignal` for loop dispatch. |
| `UnaryOp` | Evaluate operand and apply portable unary operator token (`-`, `+`, `~`, `not`). |
| `BinaryOp` | Evaluate operands and apply portable binary operator token (`+`, `-`, `*`, etc.). |
| `BooleanOp` | Short-circuit `and` / `or`, returning the selected operand value. |
| `CompareOp` | Evaluate chained comparisons and return `BoolValue`. |
| `ConditionalExpr` | Evaluate `test`, then one expression branch. |
| `MappingLiteral` | Evaluate key/value entries into `MappingValue`. |
| `GetItem` | Evaluate object and key, then index sequence/mapping/native host value. |
| `Spread` | Expand iterable values inside `Sequence`; reject outside sequence context. |
| `Loop` | Repeatedly eval `test` then `body`. `BreakSignal` exits. `ContinueSignal` skips to next iteration. |
| `Match` | Evaluate `subject`. For each `PatternTest` case, check pattern match + guard. First match wins. |
| `PatternTest` | Match `pattern` against a value. If `guard` is present and falsy, skip. Eval `body`. |
| `ConstructData` | Evaluate each field value. Return `DataValue(name, fields)`. |
| `GetField` | Evaluate `object_`. Return `object_.fields[field]`. Error if not DataValue. |
| `Raise` | Evaluate `exception`. Return `ErrorValue`. If inside `Handle`, transfer to handler. |
| `Handle` | Eval `body`. If `ErrorValue` emerges, match against handlers. Always eval `finalbody`. |
| `Sequence` | Evaluate each element. Return as Python list (or `ListValue` later). |
| `Diagnostic` | Rejected by `verify_core(strict=True)` before eval. If reached, raise. |

### Unboxing Convention

`_unbox(value: Value) -> Any` unwraps Nomi values back to Python objects for
`EvalBackendResult.bindings`. This is the **only** place Python objects leak
out — the public API boundary. Backends that don't target Python can skip this.

```python
def _unbox(self, value: Value) -> Any:
    if isinstance(value, IntValue):    return value.value
    if isinstance(value, FloatValue):  return value.value
    if isinstance(value, BoolValue):   return value.value
    if isinstance(value, StrValue):    return value.value
    if isinstance(value, NilValue):    return None
    if isinstance(value, FunctionValue): return f"<function {value.params}>"
    if isinstance(value, DataValue):   return {value.name: {k: self._unbox(v) for k, v in value.fields.items()}}
    if isinstance(value, NativeValue): return value.callable
    if isinstance(value, ErrorValue):  raise RuntimeError(value.message)
    return value
```

## Capability Graduation Path

The Core Runtime starts with `selectable_for_execution=False` (like `core_direct.py`).
It graduates through capability promotion:

| Gate | Capability | What it unlocks |
|------|-----------|----------------|
| **G1** | `evaluates_native_ir=True` | Runs without Python AST roundtrip (satisfied from day one). |
| **G2** | `supports_full_language=True` | Registered node types dispatch cleanly. Parity tests pass against Python AST backend for covered constructs. |
| **G3** | `supports_blocks=True` | Block calls, yield, resume work. |
| **G4** | `supports_exceptions=True` | Raise/Handle dispatch works. |
| **G5** | `supports_python_interop=True` | NativeValue wrapping and host-call dispatch work. |
| **G6** | `selectable_for_execution=True` | Listed in `eval-backends` table. Usable as `pipeline.eval_backend`. |
| **G7** | `supports_source_maps=True` | Source spans preserved through eval for diagnostics. |

## Implementation Sequence

### Slice 1: Value system + basic eval (7 node types)
`Literal`, `Load`, `Bind`, `Function`, `Call`, `Return`, `Branch`
— same subset as `core_direct.py`, but with Nomi-owned values and scoped frames.

### Slice 2: Data and fields (2 node types)
`ConstructData`, `GetField`
— introduces `DataValue`, the foundation for user-defined types.

### Slice 3: Expression operations (4 node types)
`UnaryOp`, `BinaryOp`, `BooleanOp`, `CompareOp`
— introduces portable operator tokens before ordinary programs can run outside
the Python AST backend.

### Slice 4: Data access expressions (4 node types)
`ConditionalExpr`, `MappingLiteral`, `GetItem`, `Spread`
— introduces portable mapping/subscript and sequence-spread support.

### Slice 5: Statement control (3 node types)
`NoOp`, `Break`, `Continue`
— introduces small statement-control nodes needed by match and loops.

### Slice 6: Annotated binding projection
`AnnAssign` currently projects to `Bind` so backend reduction can proceed.
Annotation/constraint metadata must be preserved later when constrained binding
moves into Core IR proper.

### Slice 7: Yield representation
`Yield`
— represents yield in Core IR and lowers back to Python AST; full block/resume
semantics remain a later capability gate.

### Slice 8: Control flow (2 node types)
`Loop`, `Sequence`
— introduces `BreakSignal`, `ContinueSignal`, and collection values.

### Slice 9: Pattern matching
`Match`, `PatternTest`, plus Core pattern shapes (`Literal`, `Load`,
`Sequence`, `MappingLiteral`, `Spread`)
— introduces value, capture, sequence, mapping, rest-pattern, and guard
evaluation.

### Slice 10: Exception handling (2 node types)
`Raise`, `Handle`
— introduces `ErrorValue` and handler dispatch.

### Slice 11: Host interop + unboxing
`NativeValue` wrapping, host-call dispatch table, `_unbox` for public API.

### Slice 12: Blocks and resume (capability promotion)
Block calls, yield, resume — the most complex capability. May need `GeneratorState`.

## Testing Strategy

Each slice adds tests that compare Core Runtime output against Python AST backend
output for the same Core IR:

```python
def test_parity(core_ir_module):
    py_result = python_ast_backend.evaluate(core_ir_module)
    rt_result = core_runtime.evaluate(core_ir_module)
    assert rt_result.bindings == py_result.bindings
```

Additionally:
- **Contract tests** per node type: does `eval(Literal(42))` produce `IntValue(42)`?
- **Negative tests**: does `verify_core(strict=True)` reject unsupported constructs?
- **Roundtrip tests**: Python AST -> Core IR -> Core Runtime == Python AST -> Python interpreter

## Relationship to Other Backends

```
                  Core IR (registered node types)
                       |
          +------------+------------+
          |            |            |
    python_ast.py  core_runtime.py  core_direct.py
    (adapter)      (reference)      (prototype proof)
          |            |
    Python AST    Future backends
    interpreter   follow this pattern:
                  +-- wasm_backend (Rust, same Value enum)
                  +-- mlir_backend (lowers to MLIR ops)
                  +-- llvm_backend (JIT via ORC)
                  +-- native_backend (AOT compiled)
```

`core_runtime.py` is the **reference implementation**. Its Value system,
Frame model, and ControlFlow types become the spec that Rust/Wasm/LLVM
backends implement in their host language. The Python implementation stays
as the test oracle.

## Files to Create/Modify

| File | Action |
|------|--------|
| `prototype/runtime/backends/core_runtime.py` | New — the reference runtime |
| `prototype/runtime/backends/values.py` | New — Value system types |
| `prototype/runtime/backends/environment.py` | New — Frame model |
| `prototype/runtime/backends/control_flow.py` | New — ControlFlow types |
| `prototype/tests/unit/runtime/test_core_runtime.py` | New — parity + contract tests |
| `prototype/tests/unit/runtime/test_values.py` | New — value boxing/unboxing tests |
| `prototype/tests/unit/runtime/test_environment.py` | New — frame scoping tests |

## Design Decisions

1. **Values are frozen dataclasses, not Python primitives.** The overhead is
   negligible for a reference implementation, and the 1:1 mapping to Rust enums
   is worth it.

2. **Control flow is a return value, not an exception.** Python exceptions for
   control flow are fast but non-portable. Returning `ControlFlow` values is
   slightly slower in Python but directly translatable to `Result` in Rust.

3. **Frames are mutable during eval, frozen at function-creation time.**
   This matches how closures actually work — capture by reference during
   evaluation, snapshot at function-creation boundary.

4. **Host interop is explicit and capability-gated.** A backend that declares
   `supports_python_interop=False` must not call Python code. This keeps the
   Wasm path honest.

5. **The reference implementation stays in Python.** It is not the fast path.
   It is the correct path. Native backends optimize; the reference verifies.
