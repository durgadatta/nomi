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

## Reduced interpreter
- `prototype/interpreter/reduced/interpreter.py` — Inherits from NomiInterpreter, overrides removed eval_* methods with NotImplementedError
- `prototype/interpreter/runner.py` — make_runner() factory, shared by all three usage.py files

## Semantic substrate direction
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
```

For feature experiments, add focused runtime tests only after parse and
lowering behavior are inspectable. Keep reduced-interpreter tests aligned with
declared desugar or core-lowering invariants.
