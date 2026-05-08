# Language Feature Todos

> Status: staged backlog for the forward-looking language design.

This backlog turns [Cognitive Language Vision](cognitive_language_vision.md)
and [Binding Constraints Feature](binding_constraints_feature.md) into
implementation-sized work. The current prototype is a bootstrap path, not a
limit on what should be designed.

## Track 0: Language Vision And Design Fixtures

- [ ] Maintain one canonical cognitive-language vision document and keep it
  ahead of the implementation.
- [ ] Maintain the language coherence model as a blocking design review for new
  features.
- [ ] Extract promising ideas from `documentation/design_review_archive/` into
  active feature specs only when they can share the same semantic spine.
- [ ] For each promoted idea, document what Nomi keeps from the source language
  and what it deliberately refuses to copy.
- [ ] Add target Nomi programs that intentionally use not-yet-implemented
  features: shape binding, algebraic data, pipelines, block policies, symbolic
  rewrite, table queries, and examples.
- [ ] Add executable examples for the accepted surface forms under
  `prototype/tests/data/sample_sources/interpreter/`.
- [ ] Add a small design-fixture file that contains desired future syntax even
  before all examples parse.
- [ ] Add a test matrix that distinguishes currently supported, planned, and
  intentionally rejected syntax.

## Track 1: Binding, Constraints, And Shape

- [ ] Introduce a runtime `BindingError` type with fields for name, value,
  failed constraint, source span when available, binding kind, and optional
  human message.
- [ ] Replace plain `TypeError` constraint failures with `BindingError`, while
  keeping compatibility where existing tests expect `TypeError`.
- [ ] Add a `Constraint` representation instead of storing bare predicate
  callables only. It should preserve the original expression/name and support
  diagnostics.
- [ ] Add a `BindingTarget` abstraction for name binding, tuple/list
  destructuring, mapping destructuring, and later pattern captures.
- [ ] Implement tentative binding and commit/rollback so failed constraints do
  not leak partially bound names.

### Parser And AST Shape

- [ ] Keep current assignment syntax working:
  `x:int, x > 0 = value`.
- [ ] Decide whether bare declaration syntax is accepted now:
  `x:int, x > 0`.
- [ ] Parse grouped parameter constraints:
  `func f(x:(int, x > 0)): ...`.
- [ ] Parse constrained block parameters:
  `each(xs) -> x:int: ...` and `pairs(xs) -> k:str, v:int: ...`.
- [ ] Parse constrained destructuring targets:
  `(x:int, y:int) = point`.
- [ ] Parse constrained match captures:
  `case {"age": age:(int, age >= 13)}:`.
- [ ] Preserve enough source location data for useful diagnostics.

### Parameter Binding

- [ ] Route function call argument mapping through the same binding-validation
  path used by assignment.
- [ ] Validate defaulted parameters after defaults are applied.
- [ ] Define how constraints apply to `*args` and `**kwargs`.
- [ ] Add tests for positional-only, keyword-only, defaults, varargs, and
  keyword arguments.
- [ ] Ensure arrow functions either support constrained parameters or reject
  them with a clear parse/runtime error.

### Block Parameter Binding

- [ ] Replace one-to-one yielded-value mapping with the shared binding engine.
- [ ] Support constrained single block parameters:
  `each(xs) -> item:int: ...`.
- [ ] Support constrained multi-value block parameters:
  `pairs(xs) -> key:str, value:int: ...`.
- [ ] Define behavior when the callee yields the wrong number of values.
- [ ] Add tests that failed block-parameter constraints prevent block body
  execution.

### Pattern And Destructuring Binding

- [ ] Reuse `BindingTarget` for tuple/list destructuring assignment.
- [ ] Reuse `BindingTarget` for mapping destructuring assignment.
- [ ] Add constrained pattern captures in `match`.
- [ ] Define direct assignment failure as `BindingError`.
- [ ] Define match-case constraint failure as case non-match before body entry.
- [ ] Add tests that partial pattern bindings do not leak on failure.

### Human Diagnostics

- [ ] Add `else "message"` syntax for individual constraints.
- [ ] Carry messages through `Constraint`.
- [ ] Produce diagnostics that name the binding kind: assignment, parameter,
  block parameter, destructuring target, or match capture.
- [ ] Include the failing source expression when available.
- [ ] Add regression tests for multi-constraint failures.

### Shape Binding

- [ ] Add a minimal `shape` declaration grammar.
- [ ] Implement shape validation over mappings first.
- [ ] Support optional fields with `?`.
- [ ] Support defaulted fields.
- [ ] Reuse binding constraints for each field.
- [ ] Add examples for request JSON, config, form data, and CLI args.

## Track 2: Blocks As Control Values

- [ ] Use `block_calls_feature.md` as the canonical focused feature spec.
- [ ] Specify block calls as calls with attached caller-side code and explicit
  `yield` points.
- [ ] Define block scoping: which names are read, rebound, shadowed, and
  captured.
- [ ] Implement block parameters through the shared binding engine.
- [ ] Add standard block policies: `using`, `retry`, `timeout`, `transaction`,
  `trace`, and `test`.
- [ ] Add diagnostics that show when and why a block was entered, yielded,
  resumed, retried, or cancelled.

## Track 3: Expression Flow, Pipelines, And Composition

- [ ] Specify `|>` pipeline semantics, including placeholder `_` and simple
  single-argument shorthand.
- [ ] Specify `>>` function composition separately from pipeline application.
- [ ] Add final-expression return for selected expression-oriented blocks.
- [ ] Add scoped intermediate bindings for calculational expressions.
- [ ] Add trace output for pipeline stages so the programmer can inspect value
  flow.

## Track 4: Algebraic Data, Results, And Pattern Matching

- [ ] Specify `data` declarations for product and sum types.
- [ ] Define constructor, field access, equality, display, and destructuring
  behavior.
- [ ] Add `Result[T, E]` and optional-value conventions.
- [ ] Extend `match` to cover algebraic variants, guards, constraints, and
  expression results.
- [ ] Add exhaustiveness diagnostics as an eventual goal, even if runtime-only
  checking comes first.

## Track 5: Collections, Arrays, Tables, And Queries

- [ ] Specify a collection transform vocabulary: `map`, `where`, `select`,
  `group`, `join`, `sort`, `fold`, and `window`.
- [ ] Decide which operations are syntax and which remain library-led block
  calls.
- [ ] Add table/row/column shape concepts that reuse binding and constraints.
- [ ] Explore APL-style rank and whole-array operations with readable spelling.
- [ ] Add examples for ordinary lists, records, dataframes, and time-indexed
  data.

## Track 6: Symbolic Expressions And Rewrite Rules

- [ ] Specify `quote:` as the explicit boundary where code-shaped syntax becomes
  data.
- [ ] Specify rewrite rules such as `expr /. pattern -> replacement`.
- [ ] Define evaluation boundaries so ordinary runtime code is not implicitly
  symbolic.
- [ ] Add a small expression AST model independent of Python's AST where needed.
- [ ] Add examples for algebra simplification, code transformation, and
  teaching/debugging tools.

## Track 7: Effects, Worlds, Capabilities, And Policies

- [ ] Specify capability scopes for filesystem, network, time, randomness,
  subprocesses, and environment access.
- [ ] Explore `world` values for simulation, test isolation, and replay.
- [ ] Define how block policies interact with capabilities.
- [ ] Add effect-aware diagnostics: what did this code touch, and under what
  authority?
- [ ] Keep this cognitive and inspectable rather than making it a resource
  optimization project.

## Track 8: Examples, Tests, Explanation, And Trace

- [ ] Specify `examples:` blocks inside functions and data/shape declarations.
- [ ] Let examples serve as tests, documentation, and behavioral anchors.
- [ ] Add `explain(expr)` or equivalent runtime explanation hooks.
- [ ] Add trace objects for constraints, matches, pipelines, block control, and
  rewrites.
- [ ] Make diagnostics speak in feature terms, not interpreter internals.

## Track 9: Scoped Notation And Language Growth

- [ ] Specify `use` scopes for enabling extension syntax or domain notation.
- [ ] Require every notation extension to provide a desugaring.
- [ ] Add guardrails against global syntax mutation.
- [ ] Prototype one small notation domain, such as units or symbolic algebra.
- [ ] Ensure tooling can show the expanded form on demand.

## Track 10: Cleanups And Coherence Checks

- [ ] Before implementing a feature, answer the coherence questions from
  `language_coherence_model.md`.
- [ ] Reject or redesign any feature that adds a second unrelated story for
  binding, blocks, patterns, expression flow, symbolic code, effects, or
  diagnostics.
- [ ] Remove duplicate ad hoc validation paths after the shared binding engine
  covers assignment, parameters, blocks, and patterns.
- [ ] Update `documentation/delta_on_python.md` to point to the canonical
  constrained-binding spec.
- [ ] Update `documentation/yield_to_block.md` with the block-parameter binding
  decision once implemented.
- [ ] Add a conformance-style test file containing the design tests from the
  feature spec.
- [ ] Mark archived design-review docs as background source material only.

## Milestone Sequence

The first milestone should still be coherent, but it should point beyond the
current prototype:

```python
func signup(age:(int, age >= 13), email:(str, contains(email, "@"))):
    return email

payload_age:int, payload_age >= 13 = 18
payload_email:str, contains(payload_email, "@") = "a@b.com"
result = signup(payload_age, payload_email)
```

Milestone 1 means:

- assignment constraints still work,
- parameter constraints work through real argument mapping,
- failures produce `BindingError`,
- tests cover success and failure,
- docs and implementation use the same vocabulary.

Milestone 2 should make blocks and shape binding real:

```python
shape SignupPayload:
    email:str, contains(email, "@")
    age:int, age >= 13

payload:SignupPayload = request.json

transaction(db):
    db.users.insert(payload.email)
```

Milestone 3 should make data flow readable:

```python
names =
    users
    |> where(_.active)
    |> select(_.name)
    |> sort
```

Milestone 4 should make algebraic data and match central:

```python
data Result[T, E]:
    Ok(value:T)
    Err(error:E)

match fetch_user(id):
    case Ok(user):
        user.name
    case Err(error):
        explain(error)
```

Milestone 5 should open explicit symbolic power:

```python
expr = quote:
    x + 0

simple = expr /. a + 0 -> a
```
