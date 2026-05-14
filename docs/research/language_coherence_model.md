# Language Coherence Model

> Status: active design constraint.
>
> Nomi must not become a collection of admired syntax from other languages.
> Every feature must first be justified from the
> [First-Principles Programming Model](first_principles_programming_model.md),
> then translated into one coherent language model before it is allowed to
> become Nomi syntax.

## Central Claim

Nomi is not Python plus Haskell plus Mathematica plus Kotlin plus Ruby plus
Scheme plus APL plus ALGOL.

Nomi is one language whose surface should feel Python-readable, whose semantics
should be regular like Scheme and ALGOL, whose modeling should learn from
Haskell and Kotlin, whose symbolic layer should learn from Mathematica, whose
control abstraction should learn from Ruby, and whose data transformation style
should learn from APL.

The source languages are teachers, not ingredients. First principles are the
spine.

## The Whole-Language Shape

The unifying picture is:

```text
program
  = scoped declarations
  + expressions that produce values
  + bindings that name and constrain values
  + blocks that pass control-shaped code to calls
  + patterns that inspect and bind structure
  + explicit quoted forms that treat code as data
  + effects/capabilities that bound contact with the outside world
  + examples/traces/diagnostics that explain behavior
```

This is the conceptual grammar. Every feature should occupy one of these roles
or explain why the core needs a new role.

For the companion question of what Nomi must make easy, teachable, and
trustworthy for broad everyday use, see
[Language Direction And Gap Map](../language/language_direction_and_gap_map.md).

## Translation, Not Collection

Borrowed features must be translated into Nomi's semantic vocabulary. The order
is always:

```text
primitive programming need
  -> existing language references
  -> extracted idea
  -> Nomi semantic role
  -> Nomi syntax
```

| Source idea | Do not copy | Nomi translation |
| --- | --- | --- |
| Python decorators/context managers | More special-purpose function wrapping and resource protocols | Block policies and function policies with explicit desugaring. |
| Haskell monads/effects | Abstract ceremony as the daily style | Scoped effects, result values, and capability boundaries that explain what code can touch. |
| Mathematica rewrite rules | Global magical rewriting | Explicit quoted expressions and scoped rewrite application. |
| Kotlin null-safety | A separate null mini-language | Absence as constrained binding, optional shape fields, safe access, and result/option data. |
| Ruby blocks | Implicit receiver-heavy DSLs | Caller-side blocks with visible block parameters and explicit `yield`. |
| Scheme macros | Unbounded compile-time language mutation | Scoped code-as-data transforms with inspectable expanded forms. |
| APL array density | Glyph-heavy tacit code as default | Whole-collection operations with readable rank/shape concepts and traceable stages. |
| ALGOL blocks | Old procedural ceremony | Lexical block structure as the visual skeleton for scope, control, and policy. |

An idea enters Nomi only after this translation. If it cannot be translated, it
remains background inspiration.

## Coherence Invariants

These invariants protect the language from becoming a feature pile.

### One Binding Story

Names are introduced by binding. Assignment, parameters, block parameters, loop
variables, destructuring, match captures, shape fields, imports, and exception
aliases should share the same conceptual operation.

```python
age:int, age >= 0 = payload.age

func signup(age:(int, age >= 13)):
    ...

each(users) -> user:User:
    ...

match payload:
    case {"age": age:(int, age >= 13)}:
        ...
```

If these need four validation systems, the language is incoherent.

### One Block Story

A block is caller-side code attached to a call. The callee can invoke it with
`yield`, possibly with values.

```python
retry(3):
    send(request)

transaction(db) -> tx:
    tx.insert(user)
```

Context managers, retries, tests, cleanup, tracing, and structured concurrency
should be library-visible uses of the same block idea, not separate control
languages.

### One Pattern Story

Patterns test structure and bind names. Pattern binding, match cases,
destructuring assignment, algebraic data variants, and shape matching should
reuse one pattern model.

```python
(x, y) = point

match result:
    case Ok(value):
        value
    case Err(error):
        explain(error)
```

### One Expression Flow Story

Nested calls, pipelines, composition, collection transforms, table queries, and
calculational blocks should be different views of value flow.

```python
clean = strip >> lower >> normalize_space

name =
    raw
    |> strip
    |> lower
    |> normalize_space
```

Pipeline applies a value now. Composition builds a function for later. Query and
array operations are structured transformations in the same family.

### One Symbolic Boundary

Ordinary code runs. Quoted code is data.

```python
expr = quote:
    x + 0

simple = expr /. a + 0 -> a
```

Symbolic rules, macros, code transformations, and notation definitions must
cross an explicit boundary. This lets Nomi learn from Mathematica and Scheme
without making ordinary code unpredictable.

### One Effect Boundary

Effects are not shameful, but they should be cognitively visible when they
matter.

```python
with world(fs, network) as w:
    page = w.network.get(url)
    w.fs.write(path, page)
```

This can start as runtime convention and become stronger over time. The
coherence requirement is that IO, time, randomness, subprocesses, database
transactions, and simulation eventually speak in compatible terms of worlds,
capabilities, and block policies.

### One Explanation Story

Every major feature should produce explanations in its own semantic vocabulary:

- binding explains failed constraints,
- block control explains yield/resume/retry/cancel,
- pattern matching explains why a case matched or failed,
- pipelines explain intermediate values,
- symbolic rewrite explains which rule fired,
- effects explain what authority was used,
- examples explain intended behavior.

Diagnostics are not afterthoughts. They are part of the language's cognitive
contract.

## Surface Design Rules

### Prefer A Shared Shape Over A Famous Spelling

If a borrowed spelling does not fit Nomi's shared grammar, use a different
spelling.

For example, Haskell's `>>=` is powerful, but Nomi should not import it merely
because it is canonical. The Nomi question is: does this become a block policy,
a pipeline stage, a result combinator, or a capability boundary?

### Prefer Visible Boundaries

Advanced power is welcome when its boundary is visible:

- `quote:` for symbolic/code-as-data,
- `use name:` for scoped notation,
- `world(...)` for capability scopes,
- explicit `Data.decode(...)` and structural patterns for external data
  boundaries,
- block calls for control policies.

Invisible ambient behavior should be treated as design debt.

### Prefer One Good Spelling

When two syntax forms express the same cognitive operation, one should usually
win. Aliases are expensive because they split the programmer's mental model.

### Prefer Desugaring That Teaches

A desugaring is not only an implementation trick. It is a way to teach the
feature.

Good desugaring says:

```text
this feature is really binding plus constraints
this feature is really a call plus a block
this feature is really a quoted expression plus a rewrite rule
```

Bad desugaring says:

```text
the compiler has a secret special case here
```

## A Coherent Target Example

This example intentionally combines ideas from several traditions while making
them pass through one Nomi shape.

```python
data SignupPayload:
    email:str, contains(email, "@") else "Invalid email"
    age:int, age >= 13 else "Must be at least 13"
    plan:Plan = Plan.Free

data SignupResult:
    Created(user:User)
    Rejected(reason:SignupError)

func signup(raw:dict, services:SignupServices) -> SignupResult:
    examples:
        {"email": "a@b.com", "age": 18} => Created(...)

    payload = SignupPayload.decode(raw)

    user =
        payload
        |> normalize_signup
        |> build_user

    transaction(services.db):
        services.db.users.insert(user)
        audit("signup", user.id)

    return Created(user)
```

This is not syntax collage:

- `decode` makes the external-data boundary explicit.
- `data` uses binding and constraints for owned values and variants.
- `examples` attach behavior to a function.
- `|>` expresses value flow.
- `transaction` is a block policy.
- diagnostics can explain each boundary.

The language feels larger than Python, but the mental model is smaller than a
bag of unrelated features.

## Rejection Tests

Reject or redesign a feature when:

- it only exists because another language has it,
- it introduces a second meaning for binding, blocks, patterns, effects, or
  symbolic code,
- it requires global magic to be useful,
- it cannot produce a meaningful explanation when it fails,
- it makes common code read like expert-only notation,
- it cannot be scoped, desugared, or inspected,
- it competes with an existing Nomi spelling for the same operation.

## Design Review Questions

Every feature proposal should answer:

1. Which Nomi primitive does this extend?
2. Which cognitive operation does it improve?
3. Which borrowed tradition inspired it?
4. What did we deliberately not copy from that tradition?
5. How does it compose with binding, blocks, patterns, expression flow, symbolic
   boundaries, and diagnostics?
6. What is the smallest example where it makes the whole language feel more
   coherent?

If these answers are weak, the feature is not ready.
