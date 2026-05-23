---
name: nomi-interp
description: Modify the Nomi interpreter — add/change runtime behavior, evaluation, environment, control flow.
compatibility: deepseek
---

For semantic design rationale behind interpreter behavior, see the
`nomi-language-design` skill and the research corpus
(`docs/research/language_family_coverage_map.md`). Each Nomi runtime
departure from Python should trace to a normal form and a design
decision grounded in cross-language research.

For core/sugar/eval separation, read
`docs/language/core_layer_separation_plan.md` before adding evaluator behavior.
Classify the form as L0-L7. L4 sugar must reduce before eval; L2/L3 semantic
core belongs in the future core evaluator; L7 backend special cases belong in
backend code, not language semantics.

## Eval backend registry
`prototype/runtime/backends/` mirrors the parser frontend/backend pattern:
- `__init__.py` — `EvalBackendSpec`, `EvalBackendCapabilities`, registry
- `python_ast.py` — wraps existing interpreter behind Core IR adapter
- `core_direct.py` — dispatches on CoreNode types directly (no Python AST)
- `core_runtime.py` — **next**: reference runtime with Nomi-owned values,
  scoped frames, explicit control flow (see design doc)

Opt-in gates (env vars):
- `NOMI_VERIFY_CORE=1` — lower to Core IR and verify after parsing
- `NOMI_USE_CORE_IR=1` — route execution through Core IR + backend

Inspect with: `python3 -m tools.syntax.inspect --stage eval-backends`
Inspect backend-neutral Core IR JSON with:
`python3 -m tools.syntax.inspect FILE --stage core-json`

## Adding a new eval backend

Read `docs/language/core_runtime_backend_design.md` before writing a new backend.
Every backend must:

1. Define a `spec: EvalBackendSpec` with capability flags.
2. Implement `evaluate(core_ir: Module) -> EvalBackendResult`.
3. Dispatch on every registered CoreNode type (or explicitly reject unsupported ones).
4. Register via `register_backend(name, instance)`.

The `core_runtime.py` design is the Python reference pattern — Nomi-owned Value
types, scoped Frame environments, explicit ControlFlow signals, and fenced host
interop. Non-Python backends should consume serialized Core IR from
`prototype/syntax/core_json.py`; `web/core_runtime.js` is the first JavaScript
runtime over that JSON contract and dispatches every currently registered
CoreNode. `prototype/runtime/backends/js_core.py` registers it as
`js-core-runtime` for opt-in session execution, and the browser worker can opt
into it with `web/?backend=js-core-runtime` while Pyodide still supplies
parsing/lowering. Future Rust/Wasm/LLVM backends implement the same
abstractions in their host language. The Python reference stays as the test
oracle.

## Key files
- `prototype/interpreter/python/interpreter.py` — Central dispatch, exception handling, environment setup
- `prototype/interpreter/python/binding.py` — Assignment, augmented assignment, annotated assignment
- `prototype/interpreter/python/function.py` — Function definition, argument binding, closures
- `prototype/interpreter/python/function_call.py` — Resumable call evaluation
- `prototype/interpreter/python/control.py` — If, For, While, Break, Continue, Assert
- `prototype/interpreter/python/expressions.py` — Binary/unary/boolean/comparison operators
- `prototype/interpreter/python/ds.py` — Collections, comprehensions, f-strings
- `prototype/interpreter/python/class_.py` — Class definition, attribute/subscript access
- `prototype/interpreter/python/patterns.py` — Match/case pattern matching
- `prototype/interpreter/python/exceptions.py` — Try/except/finally, raise
- `prototype/interpreter/python/context_managers.py` — With statement
- `prototype/interpreter/python/others.py` — Yield, yield-from, import, async
- `prototype/interpreter/python/env.py` — Scoped environment (get/set/delete/parent chain)
- `prototype/interpreter/python/generator_state.py` — CoroutineState (pause/resume/send/throw)
- `prototype/interpreter/python/signals.py` — ControlException hierarchy

## Nomi overrides (python/ → nomi/)
- `prototype/interpreter/nomi/binding.py` — ConstraintBindingMixin: eval_AnnAssign adds predicate checking
- `prototype/interpreter/nomi/functions.py` — BlockFunctionMixin: eval_FunctionDef adds param constraints, eval_generator_obj adds block support
- `prototype/interpreter/nomi/env.py` — Environment: adds constraints dict, overrides set() to enforce
- `prototype/interpreter/nomi/generator_state.py` — CoroutineState: adds block attribute, _handle_yield_to_block
- `prototype/syntax/core_json.py` — serialized Core IR JSON contract for non-Python backends
- `prototype/runtime/backends/js_core.py` — Node wrapper registered as `js-core-runtime`
- `web/core_runtime.js` — first JavaScript Core Runtime over Core IR JSON

## Reduced interpreter
- `prototype/interpreter/reduced/interpreter.py` — Inherits from NomiInterpreter, overrides removed eval_* methods with NotImplementedError
- `prototype/interpreter/runner.py` — make_runner() factory, shared by all three usage.py files

## Semantic substrate direction
- Treat eval as the last place a surface feature should appear. Before adding
  an `eval_*` method, ask whether the construct is L4 sugar that should lower
  away, L2/L3 semantic core that needs a core operation, or an L7 backend
  workaround.
- Prefer a shared semantic representation before adding another one-off
  `eval_*` path. Binding, function call, block call, pattern match, decode,
  pipeline, and rewrite should eventually emit consistent semantic events.
- New Nomi runtime behavior should name its feature owner, normal form,
  diagnostics, trace/explain fields, and reduced-interpreter invariant.
- Keep Python-compatible behavior in `prototype/interpreter/python/`; place
  deliberate Nomi departures in `prototype/interpreter/nomi/`.
- If a runtime change depends on new syntax, make sure the parser/lowering path
  is visible in `docs/language/syntax_substrate_todo_audit.md` or a feature
  spec before implementing.
- For broad runtime/API/tooling refactors, read
  `docs/language/architecture_refactoring_plan.md` and prefer facade-first
  changes that keep existing `run_eval_loop` imports working.
- For the layer hierarchy and preparatory Core IR work, read
  `docs/language/core_layer_separation_plan.md`. Keep reduced-mode guardrails
  aligned with declared L4 reductions and future L1 verifier behavior.
- For Python-independence, native backend, MLIR, LLVM, Wasm, or ABI questions,
  read `docs/language/python_independence_and_compiler_backend_plan.md`.
  Treat Python as the bootstrap/backend path while Core IR and direct runtime
  semantics are being introduced.
- For semantic design decisions (e.g., how pattern matching exhaustiveness
  should work, how absence should propagate, how data boundaries should handle
  errors), consult the relevant deep dive in `docs/research/` — the
  cross-language synthesis already compares 10-16 languages on these topics.

## Interpreter dispatch (eval method)
```
eval(node, state, generator_state):
  1. If node is list → iterate
  2. If None → return None
  3. Look up eval_<NodeClassName>
  4. If resumable → method(node, state=state, generator_state=generator_state)
  5. Else → method(node)
  6. If error → pass through _PASS_THROUGH_EXCEPTIONS, else wrap in RuntimeError
```

## Exceptions
- ControlException (BaseException): ReturnException, BreakException, ContinueException
- YieldException, YieldFromException propagate through resumable nodes
- _PASS_THROUGH_EXCEPTIONS = (StopIteration, ZeroDivisionError, StopAsyncIteration, RuntimeError, TypeError, ValueError, NameError, AttributeError, SyntaxError, IndexError, KeyError, AssertionError)
- Everything else wrapped in RuntimeError("Error evaluating <Node> at line <n>: <msg>")

## Testing interpreters
```bash
pytest                                  # all three (python, nomi, reduced)
pytest --interpreter-modes reduced      # only reduced
NOMI_INTERPRETER_MODE=reduced pytest   # env var alternative
NOMI_VERIFY_CORE=1 pytest              # enable Core IR verification gate
NOMI_USE_CORE_IR=1 pytest             # route eval through Core IR + backend
```

For feature experiments, add focused runtime tests only after parse and
lowering behavior are inspectable. Keep reduced-interpreter tests aligned with
declared desugar or core-lowering invariants.
