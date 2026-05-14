# Cognitive Language Vision

> Status: active long-horizon design.
>
> This document defines the forward-looking language target. It is not bounded
> by the current Python-hosted prototype. Implementation exists to test and
> refine the design, not to decide the ambition.

## Thesis

Nomi is a general-purpose programming language optimized for cognition.

The scarce resource is not CPU cycles, memory, or parser convenience. The scarce
resource is the programmer's ability to hold a program in mind, reshape it,
trust it, explain it, and compose it with other ideas.

Nomi should feel locally readable like Python, but it should not be "Python plus
features." More importantly, it should not begin by collecting features from
other languages. The main design spine is the
[First-Principles Programming Model](first_principles_programming_model.md):
build upward from primitive cognitive acts, then use existing languages as
reference experiments.

Several language families illuminate the design:

- Python's indentation, names, calls, libraries, and everyday readability,
- Haskell's algebraic modeling, purity boundaries, compositional functions, and
  type-shaped thinking,
- Mathematica's symbolic expressions, rules, rewrite systems, and calculational
  style,
- Kotlin's null-safety, data modeling, extension-oriented ergonomics, and
  pragmatic defaults,
- Ruby's caller-side blocks and humane internal DSLs,
- Scheme's small core, lexical clarity, code-as-data, and scoped abstraction,
- APL's whole-collection thinking, rank awareness, and transformation density,
- ALGOL's block structure, lexical scope, and procedural clarity.

The goal is not eclectic syntax. The goal is a language where references from
other languages are translated into one first-principles semantic grammar. The
active coherence rules are defined in
[Language Coherence Model](language_coherence_model.md).

For the adoption-oriented gap map that turns this aspiration into concrete
documentation and design targets, see
[Language Direction And Gap Map](../language/language_direction_and_gap_map.md).

## Not A Syntax Collage

Nomi should not collect language features because they are famous, elegant, or
historically important. A feature belongs only when it becomes part of the same
whole.

That means:

- Haskell contributes algebraic modeling and effect thinking, not necessarily
  Haskell's visual style.
- Mathematica contributes explicit symbolic transformation, not ambient magical
  rewriting of ordinary code.
- Ruby contributes caller-side blocks, not uncontrolled implicit receivers.
- Scheme contributes regularity and code-as-data boundaries, not a separate
  parenthesized sublanguage.
- APL contributes whole-data thinking, not default glyph density.

The source languages are teachers. Nomi must still have one grammar of thought.

## Cognitive Priorities

Nomi should optimize for these human operations:

- reading a small fragment without global context,
- naming a concept exactly once and reusing it everywhere,
- turning informal invariants into executable constraints,
- moving between concrete examples and general rules,
- transforming data left-to-right without nesting noise,
- representing structure without ceremony,
- making hidden control explicit enough to inspect,
- treating code-shaped ideas as values when explicitly requested,
- asking the runtime why a value, branch, or result happened,
- letting advanced notation exist inside a controlled scope.

Performance matters eventually, but it is not the design north star. A slower
language that helps the programmer think better can later be optimized. A
confusing language made fast has already lost the central battle.

## The Semantic Spine

The language should reduce many surface features to a small set of ideas:

```text
value
binding
constraint
function
call
block
yield
pattern
data
shape
collection
table
quote
rewrite
effect
world
capability
example
trace
diagnostic
module
use
```

This is not a minimal machine core. It is a cognitive core: the concepts a
programmer should be able to learn once and recognize everywhere.

## Source-Language Synthesis

| Source | Durable idea | Nomi direction |
| --- | --- | --- |
| Python | Local readability, ordinary calls, indentation, practical libraries | Keep as surface baseline and migration bridge. |
| Haskell | Types as structure, pure functions, algebraic data, pattern matching | Use algebraic modeling and effect boundaries without making daily code feel scholastic. |
| Mathematica | Expressions as data, symbolic rules, rewrite-driven thinking | Add explicit quoted expressions and scoped rewrite systems. |
| Kotlin | Nullable values, data classes, extension functions, ergonomic defaults | Make absence, data, and local extension predictable and lightweight. |
| Ruby | Blocks as caller-side behavior, expressive internal DSLs | Generalize block calls with inspectable `yield` semantics. |
| Scheme | Small regular core, lexical scope, macros as transformation | Keep regularity and explicit code-as-data boundaries. |
| APL | Whole-array operations, rank, shape, tacit composition | Make collection and table transformations dense but still readable. |
| ALGOL | Blocks, scope, structured control | Preserve block clarity as the visual and semantic skeleton. |

Borrowing should happen at the idea level. If a feature imports visual clutter,
implicit magic, or several equivalent spellings, it has probably imported the
wrong layer.

## Feature Pillars

### 1. Binding, Constraints, And Data Boundaries

Binding is the act of receiving a value into a name or structure. Constraints
turn that act into a semantic boundary.

```python
payload = SignupPayload.decode(request.json)
user = User(id=new_id(), email=payload.email)
```

This pillar covers assignment, parameters, destructuring, pattern captures,
external data, forms, CLI arguments, config, and diagnostics.

### 2. Blocks As Control Values

Caller-side blocks let libraries define control forms without adding a keyword
for every policy.

```python
retry(3, on=NetworkError):
    send(request)

transaction(db) -> tx:
    tx.insert(user)
```

This pillar covers resource scopes, retry, timeout, transactions, tests,
cleanup, logging, tracing, permissions, structured concurrency, and local
policies.

### 3. Expression Orientation And Transformation Flow

Programs should support direct expression of value flow without turning simple
steps into nested calls.

```python
summary =
    text
    |> parse
    |> normalize
    |> summarize
```

This pillar covers pipelines, function composition, final-expression return,
`match` expressions, scoped intermediate bindings, and calculation blocks.

### 4. Algebraic Data And Pattern Thinking

Programs should model alternatives directly.

```python
data Result[T, E]:
    Ok(value:T)
    Err(error:E)

match response:
    case Ok(user):
        render(user)
    case Err(error):
        explain(error)
```

This pillar brings Haskell/ML-style modeling into a Python-readable surface.

### 5. Collections, Arrays, Tables, And Queries

Nomi should make whole-data transformations first-class without forcing a
separate string language.

```python
active_names =
    users
    |> where(_.active)
    |> select(_.name)
    |> sort
```

Future array and table work should learn from APL, SQL, KDB/q, dataframes, and
Mathematica while preserving inspectable desugaring.

### 6. Symbolic Expressions And Rewrite Rules

Code-shaped syntax should become data only at explicit boundaries.

```python
expr = quote:
    x + 0

simplified = expr /. a + 0 -> a
```

This pillar enables algebra, program transformation, macros, optimizer passes,
teaching tools, and AI-assisted refactoring without making ordinary runtime code
magically symbolic.

### 7. Effects, Worlds, And Capabilities

Side effects should be understandable as scoped capabilities rather than ambient
global permission.

```python
with world(fs, network) as w:
    page = w.network.get(url)
    w.fs.write(path, page)
```

This does not need to become Haskell's IO model. The point is cognitive
explicitness: what can this code touch, and under which policy?

### 8. Examples, Tests, Proofs, And Explanation

The language should let examples become executable semantic anchors.

```python
func normalize_email(email:str) -> str:
    examples:
        " A@B.COM " => "a@b.com"
    return email.strip().lower()
```

The runtime should eventually answer questions such as:

- why did this constraint fail?
- why did this match case win?
- which values flowed through this pipeline?
- which examples define the intended behavior?

### 9. Scoped Notation And Local Language Growth

Nomi should permit domain notation only inside explicit scopes.

```python
use units:
    speed = 30 km / hour
```

This is a dangerous feature unless scoped, inspectable, and desugarable. Used
carefully, it lets the language grow toward the user's problem rather than
forcing every problem into generic syntax.

## Target Daily Example

```python
data SignupPayload:
    email:str, contains(email, "@") else "Invalid email"
    age:int, age >= 13 else "Must be at least 13"
    plan:Plan = Plan.Free

data User(id:UserId, email:str, plan:Plan)

func signup(raw:dict) -> Result[User, SignupError]:
    examples:
        {"email": "a@b.com", "age": 18} => Ok(User(...))

    payload = SignupPayload.decode(raw)

    user =
        payload
        |> validate
        |> build_user

    transaction(db):
        db.users.insert(user)
        audit("signup", user.id)

    return Ok(user)
```

This example combines explicit data decoding, data modeling, result values,
examples, pipelines, transactions, and audit policy. The ambition is not to
implement all of this immediately. The ambition is to keep every implemented
feature pointed toward code like this.

## Design Discipline

New features should pass these questions:

1. What cognitive operation does this make easier?
2. What source-language idea is being borrowed, and at what abstraction level?
3. What primitive does it reduce to?
4. What boundary keeps it from becoming implicit magic?
5. How will diagnostics explain it when it fails?
6. Can this feature compose with binding, blocks, patterns, and examples?

If a feature is powerful but not explainable, it stays in the archive. If it is
explainable and cognitively useful, implementation difficulty is not a reason to
drop it.
