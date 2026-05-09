# First-Principles Programming Model

> Status: active foundation.
>
> This is the main spine for Nomi language design. Other languages are useful
> references, but the language should be built upward from the nature of
> programming itself: how a mind turns intention into executable structure.

## Starting Point

Programming is not primarily the act of writing instructions for a machine.

Programming is the act of externalizing thought into an executable model:

```text
intention
  -> distinction
  -> representation
  -> transformation
  -> consequence
  -> explanation
```

A program lets a person say:

- what kinds of things exist,
- what names matter,
- what must be true,
- how values change or produce other values,
- what alternatives are possible,
- what happens over time,
- what parts of the outside world are touched,
- why a result, failure, or action occurred.

The machine executes the program. The language should serve the mind that has
to form, inspect, revise, and trust it.

## The First Question

The first design question is not:

> What syntax should Nomi borrow?

The first design question is:

> What are the primitive cognitive acts of programming?

Only after answering that should Nomi ask which existing languages have useful
precedents.

## Primitive Cognitive Acts

### 1. Distinguish

Before computation, there is distinction: this value rather than that value,
this case rather than that case, this concept rather than noise.

Language role:

```text
value
literal
identity
equality
variant
```

Examples:

```python
42
"Ada"
True
Plan.Free
```

Design consequence:

Nomi needs clear values before it needs clever syntax. Every advanced feature
must eventually say what values it introduces or transforms.

### 2. Name

The mind cannot work with everything at once. It names.

Language role:

```text
binding
scope
context
```

Example:

```python
email = payload.email
```

Design consequence:

Binding is foundational because it connects a value to a concept inside a
scope. Assignment, parameters, imports, pattern captures, block parameters, and
shape fields should all be understood as naming acts.

### 3. Judge

Programs need boundaries where values are accepted, rejected, refined, or
explained.

Language role:

```text
constraint
predicate
type
shape
invariant
diagnostic
```

Example:

```python
age:int, age >= 13 else "Must be at least 13" = payload.age
```

Design consequence:

Types, predicates, validation, contracts, examples, and tests are all forms of
judgement. They should not become unrelated subsystems.

### 4. Transform

A program relates values to values.

Language role:

```text
function
call
expression
rule
pipeline
composition
```

Examples:

```python
normalize(email)

clean =
    raw
    |> strip
    |> lower
```

Design consequence:

Functions, pipelines, symbolic rules, queries, and array transforms are all
forms of transformation. Their surface forms may differ, but their reduction
should be compatible.

### 5. Choose

Programs branch because values have structure and situations differ.

Language role:

```text
condition
pattern
match
guard
variant
```

Example:

```python
match result:
    case Ok(value):
        value
    case Err(error):
        explain(error)
```

Design consequence:

Conditionals, pattern matching, exception handling, result handling, and shape
matching are forms of choosing. Nomi should prefer structural choice over
stringly or ad hoc branching.

### 6. Group

Thought groups things into records, variants, lists, tables, modules, and
domains.

Language role:

```text
data
shape
collection
table
module
namespace
```

Example:

```python
data User(id:UserId, email:str, plan:Plan)
```

Design consequence:

Data structures are not storage details first. They are conceptual groupings.
The language should make owned data, external shape, collection, and table
structure feel related.

### 7. Repeat And Accumulate

Many programs apply a thought across many values and collect the consequences.

Language role:

```text
iteration
map
filter
fold
rank
query
stream
```

Example:

```python
active_names =
    users
    |> where(_.active)
    |> select(_.name)
    |> sort
```

Design consequence:

Loops, comprehensions, pipelines, APL-style array thinking, table queries, and
streams should be views of repeated transformation, not separate worlds.

### 8. Sequence In Time

Some computations are timeless transformations. Others happen in time: acquire,
try, wait, retry, cancel, clean up.

Language role:

```text
block
yield
policy
transaction
resource
concurrency
```

Example:

```python
retry(3):
    send(request)
```

Design consequence:

Control constructs should be understood as policies over time. Block calls are
Nomi's candidate primitive for caller-side control.

### 9. Touch The World

Programs read files, talk to networks, use clocks, generate randomness, launch
processes, mutate databases, and affect people.

Language role:

```text
effect
world
capability
permission
boundary
```

Example:

```python
with world(fs, network) as w:
    page = w.network.get(url)
```

Design consequence:

Effects should not disappear into ambient global power. The language should
make contact with the world visible enough to reason about, test, replay, and
explain.

### 10. Explain

A program that cannot explain itself is cognitively incomplete.

Language role:

```text
example
trace
diagnostic
proof
counterexample
history
```

Example:

```python
func normalize_email(email:str) -> str:
    examples:
        " A@B.COM " => "a@b.com"
    return email.strip().lower()
```

Design consequence:

Examples, tests, traces, proofs, and diagnostics are not external accessories.
They are part of making programs thinkable.

### 11. Reflect And Rewrite

Sometimes the program must talk about program-shaped structure.

Language role:

```text
quote
syntax value
rewrite
macro
notation
expansion
```

Example:

```python
expr = quote:
    x + 0

simple = expr /. a + 0 -> a
```

Design consequence:

Reflection is powerful only when bounded. Ordinary code should run normally.
Code becomes data through explicit quotation or scoped notation.

## The Build-Up Ladder

Nomi should be designed upward in this order:

```text
1. values: what can be distinguished
2. bindings: how values become named concepts
3. constraints: how concepts are judged and refined
4. functions/calls: how values transform
5. data/shapes: how values group into structure
6. patterns/match: how structure is inspected
7. collections/tables: how transformation scales across many values
8. blocks/yield: how time-shaped control is abstracted
9. effects/worlds/capabilities: how programs touch reality
10. examples/traces/diagnostics: how behavior explains itself
11. quote/rewrite/notation: how programs transform program-shaped ideas
```

This is not an implementation order. It is a conceptual dependency order. A
later feature may be prototyped early, but its design should reduce back down
this ladder.

## Small Core Candidate

The first-principles ladder suggests a small semantic core:

```text
Value
Context
Binding
Constraint
Function
Call
Data
Pattern
Block
Yield
Effect
Quote
Rewrite
Trace
```

Surface syntax should reduce into this core.

Examples:

```text
parameter       -> binding in function-call context
shape field     -> binding plus constraint over external structure
pipeline        -> ordered calls over a flowing value
block call      -> call plus attached block value
match case      -> pattern plus conditional binding
transaction     -> block policy plus effect boundary
rewrite rule    -> pattern transform over quoted values
example         -> executable judgement plus trace expectation
```

The core may change, but changes should be justified from first principles, not
because another language has a feature.

## Role Of Other Languages

Other languages are reference experiments. They show possible answers to
first-principles questions:

| First-principles need | Useful references |
| --- | --- |
| Local readability and ordinary work | Python |
| Algebraic structure and pure transformation | Haskell, ML, Scala |
| Symbolic representation and rewrite | Mathematica, Lisp, Scheme |
| Caller-side control | Ruby, Kotlin, Python generators/context managers |
| Whole-data transformation | APL, KDB/q, SQL, dataframe systems |
| Blocks and lexical structure | ALGOL, Python, Scheme |
| Absence and practical data modeling | Kotlin, Swift, Rust |
| Effects and authority | Haskell, Rust, capability systems |

The design process is:

```text
first-principles need
  -> study existing language answers
  -> extract the durable idea
  -> translate into Nomi's core
  -> choose syntax that makes the idea locally readable
```

The process is not:

```text
admired syntax
  -> copy into Nomi
```

## Design Review Questions

Every feature proposal should answer:

1. Which primitive cognitive act does this support?
2. Which rung of the build-up ladder does it depend on?
3. What new value, binding, transformation, choice, effect, or explanation does
   it introduce?
4. How does it reduce to the small core candidate?
5. Which existing languages illuminate the problem?
6. What does Nomi deliberately refuse to copy from them?
7. How will the feature help a programmer think more clearly?

If those answers are weak, the feature is premature.
