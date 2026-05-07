# Language Syntax Synthesis

> Status: design note.
>
> This document explains the ideas behind the proposed syntax catalog in
> [Proposed Syntax Samples](proposed_syntax_samples.md). It is concerned with
> usability, semantic coherence, and reducibility to a small core, not immediate
> implementation.

## Aim

Nomi should synthesize well-loved language ideas without becoming a museum of
syntax. The goal is not to combine Python, Lisp, Ruby, Mathematica, APL, Scala,
Kotlin, Rust, Swift, and ML mechanically. The goal is to identify the durable
ideas behind their syntax and express those ideas in a Python-readable form.

The result should feel like:

- Python in local readability,
- ALGOL in block structure,
- Lisp in regularity and code-as-data potential,
- Mathematica in symbolic transformation,
- APL in whole-collection thinking,
- Ruby in block ergonomics,
- Scala/ML in pattern and expression orientation,
- Kotlin/Swift in practical null-safety and lightweight modeling,
- Rust in explicit recoverable error flow where useful.

But Nomi should not inherit every surface habit from those languages.

## The Small Core

The proposed syntax should reduce to the following core.

### Values

Values are the things programs compute with:

```python
3
"hello"
[1, 2, 3]
Point(2, 3)
```

Most language features should either create values, transform values, or control
when value-producing code runs.

### Bindings

A binding gives a name to a value.

```python
x = 3
```

Binding is the common semantic operation behind:

- assignment,
- function parameters,
- loop variables,
- block parameters,
- pattern destructuring,
- imports,
- exception names,
- match-case names.

Unifying these reduces the number of rules a programmer has to remember.

### Constraints

Constraints refine bindings.

```python
x:int, x > 0 = 3
```

The same idea should apply in every binding position:

```python
func f(x:(int, x > 0)): ...

for x:int in xs:
    ...

each(xs) -> x:int:
    ...

case {"age": age:(int, age >= 0)}:
    ...
```

Reduction: bind first in a temporary context, validate, then commit or fail.

### Functions

Functions abstract value-producing or action-producing behavior.

```python
func add(x, y):
    return x + y
```

Arrow functions are the expression form of the same idea:

```python
(x, y) => x + y
```

Reduction: both create function values. `func` additionally binds a name and
supports block layout.

### Calls

Function application stays ordinary.

```python
f(x, y)
```

Most advanced syntax should reduce to calls:

```python
xs.map((x) => x * 2)
text |> normalize
transaction(db): ...
```

### Blocks

Blocks represent caller-side code supplied to a callee.

```python
retry(3):
    send_request()
```

The callee invokes the attached block with `yield`.

```python
func retry(n):
    for i in range(n):
        try:
            yield
            return
        except Exception:
            pass
```

This is the primitive that lets library-defined control structures exist without
adding a new keyword for each one.

### Patterns

Patterns describe the shape a value must have and the names to bind.

```python
(x, y) = point

match response:
    case {"status": 200, "body": body}:
        body
```

Pattern matching reduces to conditional shape tests plus binding.

### Explicit Expression Values

For symbolic programming and macro-like facilities, code-shaped syntax must be
captured explicitly.

```python
expr = quote:
    x + 0
```

Rewrite rules operate on these expression values.

```python
expr /. x + 0 -> x
```

This preserves normal local reasoning: ordinary code runs; quoted code is data.

## Design Rule: Syntax Must Desugar

A proposed syntax form should answer three questions:

1. What primitive does it reduce to?
2. What common human pattern does it make easier to express?
3. What ambiguity or hidden control does it introduce?

If the answers are weak, the syntax should remain a library pattern or be
dropped.

## Synthesis By Language Family

### Python: Readable Local Code

Python's central gift is ordinary readability:

```python
for user in users:
    if user.active:
        send(user.email)
```

Nomi should keep:

- indentation,
- plain names,
- ordinary calls,
- keyword arguments,
- exceptions,
- comprehensions where they remain readable,
- familiar data literals.

Nomi should refine Python where the semantics are uneven:

- `def` becomes `func`,
- type hints become runtime binding constraints where requested,
- `lambda` becomes ordinary arrow functions,
- context managers generalize into block calls,
- statement-only constructs can become expression-producing when readable.

### ALGOL: Blocks And Scope

ALGOL's durable idea is structured blocks. Nomi should treat block shape as a
semantic tool, not just formatting.

```python
if ready:
    run()

transaction(db):
    update()

scope:
    temp = compute()
```

Block syntax should communicate where control and names live. Caller-side blocks
should be explicit, and isolated scopes should be explicit too.

### Lisp: Regular Structure And Code As Data

Lisp shows that programs become more powerful when code has a regular structure.
Nomi should borrow this at the semantic layer without adopting Lisp's surface
parentheses.

```python
expr = quote:
    x + 0
```

Possible macro-like forms should be functions from expression values to
expression values:

```python
macro unless(cond, body):
    quote:
        if not {cond}:
            {body}
```

But macros should be rare, explicit, and import-scoped. Nomi should not allow
uncontrolled syntax mutation to undermine readability.

### Mathematica: Rules And Symbolic Transformation

Mathematica's key insight is expression transformation:

```python
simplified = expr /. [
    x + 0 -> x,
    x * 1 -> x,
]
```

In Nomi, this should reduce to:

- quoted expression values,
- pattern matching,
- replacement construction,
- repeated application when requested.

This can support symbolic algebra, AST transformations, query planners, and
domain-specific rewrites without making everyday code magical.

### APL: Whole-Collection Thinking

APL demonstrates how much incidental looping disappears when operations apply
to whole collections.

Nomi should prefer readable forms first:

```python
xs.map((x) => x * 2)
xs.filter((x) => x > 0)
```

and pipeline forms:

```python
result = xs |> filter(_, is_pos) |> map(_, square) |> sum
```

Elementwise symbolic shorthand is possible:

```python
ys = xs.*2
zs = xs.+ys
```

but this should remain candidate syntax. APL's power is real, but its visual
density is not aligned with Nomi's Python-readable goal.

### Ruby: Blocks As Control Abstractions

Ruby's block ergonomics are a major design source:

```python
each(users) -> user:
    print(user.name)

retry(3):
    send_request()
```

The crucial idea is not just callback syntax. It is that the caller writes code
in place while the callee owns the control pattern.

Reduction:

```python
callee(args):
    body
```

means:

```python
callee(args, block=<caller-scope body>)
```

and the callee invokes the block with `yield`.

### Scala, ML, And Haskell: Expressions, Patterns, And Composition

These languages show the value of expression orientation:

```python
kind = match value:
    case int:
        "number"
    case str:
        "text"
```

and compositional functions:

```python
clean = strip >> lower >> normalize_space
```

They also show the importance of pattern matching as a general way to process
structured values:

```python
match result:
    case Ok(value):
        value
    case Err(error):
        recover(error)
```

Nomi should borrow these ideas, but keep syntax less abstract than Scala and
less symbolic than Haskell.

### Kotlin And Swift: Practical Modeling And Null Safety

Modern application code benefits from lightweight value models:

```python
data User(id:int, name:str, email:str?)
```

and safe access:

```python
email = user?.profile?.email ?: "missing"
```

These forms reduce common boilerplate. The design risk is that `None`, optional
types, nullable types, and result types can become fragmented. Nomi needs one
coherent absence/error story before this syntax becomes final.

### Rust: Recoverable Errors And Explicit Propagation

Rust's `Result` flow is attractive because it makes recoverable errors explicit.

Candidate:

```python
config = read_config(path)?
```

Reduction:

```python
tmp = read_config(path)
match tmp:
    case Ok(value):
        config = value
    case Err(error):
        return Err(error)
```

This should not replace exceptions casually. It is useful when a function's
normal contract includes failure as a value.

## Coherent Surface Families

### Family 1: Definition Forms

```python
func f(x): ...
data Point(x:int, y:int)
trait Drawable: ...
protocol Reader: ...
```

All define named program concepts. Each should reduce to bindings and
constraints:

- `func` binds a function value,
- `data` binds a constructor and pattern shape,
- `trait` binds a behavioral constraint set,
- `protocol` binds a structural constraint set.

### Family 2: Expression Functions And Composition

```python
(x) => x + 1
f >> g
value |> f
```

Reduction:

- arrows create function values,
- composition creates function values,
- pipelines call functions with flowing values.

### Family 3: Binding And Pattern Forms

```python
x:int = 3
(x, y) = point
case Point(x, y):
for user:User in users:
each(users) -> user:User:
```

Reduction: each is binding plus optional validation.

### Family 4: Block Control Forms

```python
retry(3): ...
transaction(db): ...
timeout(5): ...
test "name": ...
```

Reduction: each is a call with an attached caller-side block. Some may become
keywords later, but they should begin as library-defined block calls.

### Family 5: Symbolic Forms

```python
quote: ...
expr /. pattern -> replacement
macro name(...): ...
```

Reduction: explicit expression values plus functions over those values.

## Sample Program: Data Processing

```python
data User(id:int, name:str, age:(int, age >= 0), email:str?)

func adult(user:User) -> bool:
    user.age >= 18

func normalized_email(user:User) -> str?:
    user.email?.lower()

emails = (
    users
    |> filter(_, adult)
    |> map(_, normalized_email)
    |> filter(_, (email) => email is not None)
    |> sort
)
```

Reduction:

- `data` creates a structured value constructor and pattern.
- `func` binds functions.
- `str?` is a constraint or optional type marker.
- `|>` rewrites nested calls left-to-right.
- `?.` rewrites guarded access.

## Sample Program: Control Abstraction

```python
func retry(times:int, on=Exception):
    for attempt in 1..times:
        try:
            yield attempt
            return
        except on as error:
            if attempt == times:
                raise error

retry(3, on=NetworkError) -> attempt:
    print(f"attempt {attempt}")
    send_request()
```

Reduction:

- the block call passes caller-side code to `retry`,
- `yield attempt` invokes the block with `attempt`,
- `attempt` is bound at the block boundary,
- exceptions from the block are visible around `yield`.

## Sample Program: Symbolic Rules

```python
expr = quote:
    (x + 0) * 1

simplified = expr //. [
    x + 0 -> x,
    0 + x -> x,
    x * 1 -> x,
    1 * x -> x,
]
```

Reduction:

- `quote` creates expression data,
- rules are pattern/replacement pairs,
- `//.` repeats rewrite until stable,
- no ordinary runtime code is rewritten implicitly.

## Sample Program: Testing

```python
test "withdraw reduces balance":
    account = Account(balance=100)
    account.withdraw(30)
    assert account.balance == 70

cases([(100, 30, 70), (50, 10, 40)]) -> start, amount, expected:
    test f"withdraw {amount} from {start}":
        account = Account(balance=start)
        account.withdraw(amount)
        assert account.balance == expected
```

Reduction:

- `test` is a block call registering a named block,
- `cases` yields values into a caller block,
- block parameters are bindings.

## Syntax Admission Criteria

A syntax proposal should be admitted only if it passes these tests.

### Readability

Can a Python programmer guess the basic meaning from the sample?

Good:

```python
retry(3):
    send_request()
```

Risky:

```python
send_request repeat_symbol 3
```

The second stands in for dense symbolic repetition. It may be elegant in an APL
context, but it does not fit Nomi's surface.

### Reducibility

Can the form be explained in terms of primitives?

Good:

```python
value |> f
```

reduces to:

```python
f(value)
```

Risky: syntax that requires a new invisible runtime model.

### Orthogonality

Does the form reuse existing concepts?

Good:

```python
each(users) -> user:User:
    ...
```

because block parameters are bindings, and bindings can have constraints.

Risky: a special validation system only for block parameters.

### Local Reasoning

Can the reader see where control flows and where names are bound?

Block calls should make control abstraction visible:

```python
transaction(db):
    update()
```

Symbolic rewriting should be explicit:

```python
expr /. rule
```

### Frequency

Does the feature serve common code?

High-frequency:

- constrained binding,
- data values,
- pattern matching,
- block calls,
- pipelines,
- null-safe access.

Lower-frequency:

- macros,
- repeated rewrite rules,
- array-rank shorthand,
- custom query syntax.

Lower-frequency features can still exist, but they should be library-led or
advanced.

## Features To Keep Library-First

Some ideas are attractive but should begin as libraries using the small core.

### Query Syntax

Prefer:

```python
users |> filter(_, active) |> map(_, name)
```

before:

```python
query users -> u:
    where u.active
    select u.name
```

### Concurrency Syntax

Prefer:

```python
scope() -> task:
    user = task.spawn(() => fetch_user())
```

before:

```python
async:
    user = spawn fetch_user()
```

### Macros

Prefer explicit `quote` and rewrite functions before open-ended macro syntax.

### Array Shorthand

Prefer named whole-collection operations before symbolic elementwise operators.

## Risks

### Too Many Spellings

Scala demonstrates the cost of too many equivalent forms. Nomi should avoid
adding syntax if an existing form is already clear.

### Too Much Implicitness

Ruby demonstrates the elegance and risk of implicit receivers and flexible
blocks. Nomi should keep caller-side blocks visible and avoid hidden receivers
except for controlled extension methods.

### Too Much Symbolism

APL and Mathematica demonstrate how notation can become a powerful private
language. Nomi should support symbolic domains without making ordinary programs
look symbolic by default.

### Too Much Magic

Lisp macros and Mathematica rewriting can change code meaning deeply. Nomi
should require explicit quote/rewrite/macro boundaries.

## Working Design Position

Nomi should be a small-core language with a rich but disciplined surface.

The core is:

```text
value
binding
constraint
function
call
block
yield
pattern
quote
```

The surface can then support:

```text
data values
pipelines
composition
pattern matching
block control
symbolic rewrites
null-safe access
extension functions
structured tests
structured concurrency
```

Each surface form should be explainable by peeling it back to the core. If that
peeling process is natural, the syntax is a candidate. If it feels like a
separate language hidden inside Nomi, it should remain outside the core.

The long-term design goal is not minimal syntax. It is tractable
sophistication: a language where advanced forms exist, but every advanced form
has a clear path back to simple primitives.
