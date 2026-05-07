# Streamlined Programmer Experience Design

> Status: synthesis proposal.
>
> This document reviews and condenses the current Nomi design notes into a
> user-facing language direction. It is not an implementation plan. The priority
> is the experience of the programmer: common tasks should become smaller,
> clearer, and more coherent, even when the implementation is difficult.

## 1. Purpose

Nomi should not be "Python plus more features." It should be a coherent
language that keeps Python's local readability while making the recurring
patterns of real programming feel first-class:

- validate incoming values,
- bind and reshape data,
- pass behavior into control patterns,
- clean up resources,
- transform collections and tables,
- handle missing values and ordinary failures,
- compose small functions,
- query structured data,
- attach policies such as retry, timeout, cache, trace, and permissions,
- explain what happened when something fails.

The design goal is:

> Make the common hidden patterns of programming visible, small, and reusable,
> without forcing the programmer to feel the machinery underneath.

Python already did this successfully with decorators, context managers, keyword
arguments, varargs, comprehensions, destructuring, `map`, `filter`, `reduce`,
generators, and pattern matching. Nomi should continue that direction, but with
a more unified semantic spine.

In an AI-assisted programming world, this matters even more. AI can generate
many possible programs quickly; a language should provide the durable,
inspectable structure where those programs can be understood, constrained,
edited, tested, and trusted.

## 2. Design Thesis

Nomi should have a small set of concepts that explain a large set of surface
features:

```text
value
binding
constraint
function
call
block
yield
pattern
collection
table
policy
quote
rewrite
```

The programmer should mostly experience these as ordinary code:

```python
user:User = request.json

retry(3, on=NetworkError):
    send_welcome(user)

names = users |> filter(_, active) |> map(_, name) |> sort
```

The language designer should be able to peel them back:

- `user:User = request.json` is binding plus validation.
- `retry(...):` is a call with an attached caller-side block.
- `|>` is ordinary function application written left-to-right.

The core discipline is:

> Surface richness is acceptable only when the desugaring remains explainable.

## 3. Programmer Promise

Nomi should make these promises to a working programmer.

1. Simple code should read like direct Python-like prose.
2. Repeated ceremony should become syntax only when the pattern is common.
3. The same idea should mean the same thing in every position.
4. Advanced features should have explicit boundaries.
5. Failure should be reported in the language of the feature that failed.
6. Powerful features should be scoped by imports or `use`, not hidden globally.
7. The language should be explainable by desugaring, tracing, or inspection.

This is more important than implementation simplicity. A feature may require a
hard parser, a custom interpreter, bytecode, continuations, symbolic data, or
query planning. That is acceptable if the programmer-facing model is simple and
the feature has a plausible semantic account.

## 4. Cross-Language Synthesis

Nomi should borrow ideas, not surface clutter.

| Source | What to keep | What to avoid |
| --- | --- | --- |
| Python | indentation, local readability, ordinary calls, keyword args, exceptions, comprehensions | fragmented special cases and non-enforced annotations |
| ALGOL | block structure, lexical scope, structured control | ceremony that separates specification from daily coding |
| Scheme/Lisp | regular core, functions as values, code as data | making everyday code visually alien |
| Mathematica | symbolic expressions, rewrite rules, delayed/evaluation control | implicit rewriting of normal runtime code |
| APL | whole-collection thinking, rank/shape awareness | dense symbolic notation as the default style |
| KDB/q | table-first and vector-first data work, temporal/data analytics fluency | terse glyph-heavy expert syntax |
| SQL | declarative filtering, projection, grouping, joining, aggregation | a separate string language with weak composition |
| Scala | expression orientation, pattern matching, compositional APIs | too many equivalent spellings |
| Kotlin | null-safety, data classes, extension functions, trailing lambdas | modifier and annotation buildup |
| Groovy | closures, builders, named-argument DSLs, configuration ergonomics | hidden dynamic magic and ambiguous receiver scope |
| Ruby | caller-side blocks as humane control abstraction | overly implicit receivers and control surprises |
| Rust | explicit recoverable failure with `Result` and `?` | making everyday code feel ownership-heavy |

If "Schema" means Scheme, the Lisp/Scheme line applies. If it means data schema,
the `shape`, `data`, `table`, and constraint sections below are the relevant
synthesis.

## 5. The Main Streamlining Move

The documents already point to a strong unification:

> Binding is the core operation for names. Blocks are the core operation for
> actions.

Many features become simpler when viewed through those two ideas.

Binding explains:

- assignment,
- function parameters,
- keyword and vararg mapping,
- destructuring,
- loop variables,
- match-case names,
- imports,
- exception aliases,
- table row/column projection,
- JSON/form/config/CLI binding.

Blocks explain:

- context managers,
- retry/timeout/rate-limit scopes,
- transactions,
- tests,
- cleanup,
- logging and tracing,
- small concurrency scopes,
- custom iteration,
- local policy application.

Nomi should make both uniform.

## 6. Feature Family 1: Binding With Constraints

Validated binding should be as natural as assignment.

```python
age:int, age >= 0 = payload.age
email:str, contains(email, "@") = payload.email
```

With human-facing failure messages:

```python
age:int, age >= 13 else "Must be at least 13" = payload.age
email:str, contains(email, "@") else "Invalid email" = payload.email
```

The same model applies to parameters:

```python
func charge(account:Account, amount:(Money, amount > 0)):
    account.debit(amount)
```

and block parameters:

```python
each(users) -> user:User:
    send(user.email)
```

and patterns:

```python
match payload:
    case {"age": age:(int, age >= 13), "email": email:str}:
        signup(age, email)
```

Desugaring:

```text
evaluate value
tentatively bind name or pattern
check all constraints in the binding context
commit if all pass
raise structured BindingError if any fail
```

This turns many ad hoc validation libraries into one language habit.

## 7. Feature Family 2: Data, Shape, And Pattern Binding

Nomi needs two related but distinct user-facing forms.

`data` is for values the program owns:

```python
data User(id:int, name:str, email:str?, active:bool = True)
```

`shape` is for external or structural data the program receives:

```python
shape SignupPayload:
    email:str
    age:int, age >= 13 else "Must be at least 13"
    name:str?
```

Usage:

```python
payload:SignupPayload = request.json
else error:
    return bad_request(error)

user = User(
    id=new_id(),
    name=payload.name ?: "friend",
    email=payload.email,
)
```

Pattern binding should be ordinary:

```python
{"email": email, "age": age} = request.json
Point(x, y) = point
[first, *rest] = items
```

Desugaring:

- `data` creates constructors, fields, equality, representation, and pattern
  shape.
- `shape` creates a structural validator and binder.
- pattern binding is atomic shape checking plus name binding.

This synthesizes Python dataclasses, Kotlin data classes, Scala case classes,
SQL schemas, JSON schema, and ML-style destructuring.

## 8. Feature Family 3: Functions, Calls, And Arguments

Named functions should be explicit:

```python
func normalize(text:str) -> str:
    text.strip().lower()
```

Function values should be light:

```python
normalize = (text:str) => text.strip().lower()
```

The gap between named and anonymous functions should stay small. Parameters are
bindings, return values may be constrained, and arrow functions are ordinary
function values.

Calls should keep Python's strengths:

```python
send(to=email, subject=subject, body=body)
send(*args, **options)
```

Named argument shorthand can be considered only if it stays obvious:

```python
send(:email, :subject, body)
```

Possible desugaring:

```python
send(email=email, subject=subject, body=body)
```

The principle is that call mapping, parameter binding, defaults, varargs, and
constraints should be one coherent operation.

## 9. Feature Family 4: Blocks As User-Defined Control

The most important control feature is the caller-side block:

```python
retry(3, on=NetworkError):
    send_request()
```

The callee owns the control pattern:

```python
func retry(times:int, on=Exception):
    for attempt in 1..times:
        try:
            yield attempt
            return
        except on as error:
            if attempt == times:
                raise error
```

The caller can receive yielded values:

```python
retry(3, on=NetworkError) -> attempt:
    log attempt_started(attempt)
    send_request()
```

This one form should cover many daily abstractions:

```python
using file = open(path):
    text = file.read()

transaction(db):
    save(user)
    send_welcome(user)

timeout(2 seconds):
    fetch(url)

test "withdraw reduces balance":
    account.withdraw(30)
    assert account.balance == 70
```

Desugaring:

```text
call function with attached caller-side block
callee invokes the block with yield
yielded values bind to block parameters
exceptions from the block are visible around yield
```

This synthesizes Ruby blocks, Groovy closures, Kotlin trailing lambdas, Python
context managers, decorators, generators, and coroutine ideas.

## 10. Feature Family 5: Policies On Functions And Blocks

Decorators are powerful because they make cross-cutting behavior small. Nomi
should generalize the idea into readable policy syntax.

```python
func load_dashboard(user_id:int)
with cache(ttl=30), timeout(2 seconds), retry(2), trace("dashboard"):
    user = fetch_user(user_id)?
    orders = fetch_orders(user_id)?
    {user: user, orders: orders}
```

Equivalent idea:

```python
@cache(ttl=30)
@timeout(2 seconds)
@retry(2)
@trace("dashboard")
func load_dashboard(user_id:int):
    ...
```

Policy syntax should not be a separate feature family. It should reduce to
function wrapping and/or block control:

```text
create function value
wrap it with cache
wrap it with timeout
wrap it with retry
wrap it with trace
bind the final function
```

This keeps decorators, context managers, dependency injection, tracing, retry,
permissions, rate limits, and transactions conceptually close.

## 11. Feature Family 6: Pipelines And Composition

Nested calls hide the flow:

```python
result = summarize(normalize(parse(text)))
```

Pipelines expose it:

```python
result = text |> parse |> normalize |> summarize
```

Placeholders support non-leading arguments:

```python
result = text |> parse(mode="loose", _) |> summarize(style="short", _)
```

Composition builds a function:

```python
clean = strip >> lower >> normalize_space
name = raw_name |> clean
```

Desugaring:

```text
x |> f          == f(x)
x |> f(_, y)    == f(x, y)
f >> g          == (x) => g(f(x))
```

This borrows from F#, Elixir, Mathematica postfix flow, Unix pipes, APL
composition, and method chaining, while keeping Python-like reading order.

## 12. Feature Family 7: Collections, Arrays, Tables, And Queries

Nomi should treat collections and tables as ordinary values with strong
transformation support.

For lists and streams:

```python
names = (
    users
    |> filter(_, (u) => u.active)
    |> map(_, (u) => u.name)
    |> sort
)
```

Block form for readability:

```python
names = users.map -> user:
    user.name
```

For tables, prefer composable operations first:

```python
summary = (
    orders
    |> where(_, (o) => o.status == "paid")
    |> derive(_, total = price * quantity)
    |> group(_, by=customer_id)
    |> summarize(_, revenue = sum(total), count = count())
    |> order(_, by=revenue, desc=True)
)
```

Inside table transformations, the final design may allow column names to bind
from the table shape, KDB/APL/SQL-style. When that would be ambiguous, an
explicit row alias or lambda should be required.

SQL-like query blocks may be admitted when the table use case proves common:

```python
summary = query orders -> o:
    where o.status == "paid"
    derive total = o.price * o.quantity
    group by o.customer_id
    select {
        customer_id: o.customer_id,
        revenue: sum(total),
        count: count(),
    }
    order by revenue desc
```

The table model should learn from SQL, KDB/q, APL, LINQ, Pandas, and relational
algebra:

- columns can behave like vectors,
- row binding should be readable,
- filtering/projection/grouping/joining should compose,
- queries should be inspectable,
- operations should be values, not stringly-typed fragments.

Desugaring:

```text
query/table forms reduce to relational operations:
where, select/project, derive, group, aggregate, join, order
```

This gives Nomi a path toward data fluency without embedding raw SQL strings as
the main abstraction.

## 13. Feature Family 8: Missing Values And Ordinary Failure

Nomi needs one coherent story for absence and failure.

Everyday missing values:

```python
city = user?.address?.city ?: "unknown"
```

Explicit match:

```python
city = match user:
    case Some(user):
        user.address.city
    case None:
        "unknown"
```

Ordinary recoverable failure:

```python
config = read_config(path)?
```

Fallback:

```python
recommendations = fetch_recommendations(user)? recover:
    []
```

Desugaring:

```text
safe access checks empty/non-empty before field access
fallback selects the right side when the left side is empty
? matches Ok/Err and returns Err from the current function
recover handles Err or selected exceptions with a local block
```

Exceptions should remain for exceptional control. `Result`-style values should
be used when failure is part of the normal API contract.

## 14. Feature Family 9: Local Configuration, CLI, Forms, And External Data

Many everyday programs begin by mapping outside data into internal shape.

CLI:

```python
command import_users(
    file:Path,
    dry_run:bool = False,
    batch_size:int = 100,
):
    ...
```

Config:

```python
config AppConfig:
    database_url:str from env "DATABASE_URL"
    batch_size:int = 100
```

Forms and JSON:

```python
payload:SignupPayload = request.json
else error:
    return bad_request(error)
```

This family should be built from binding, constraints, defaults, and structured
errors. It should feel like one habit whether the source is CLI args,
environment variables, JSON, forms, config files, or database rows.

## 15. Feature Family 10: Scoped Extensions And Capabilities

Extension-style functions are useful:

```python
func String.words(self):
    self.split()
```

Use:

```python
use text.extensions.words

"hello world".words()
```

The important rule is scope:

```text
import brings names
use brings capabilities
```

Capabilities may include:

- extension functions,
- traits/protocols,
- rewrite rules,
- macros,
- query dialects,
- domain policies.

This borrows from Kotlin/Scala extensions, Rust `use`, Haskell imports, Groovy
DSL ergonomics, and Mathematica rule libraries while avoiding global monkey
patching.

## 16. Feature Family 11: Explicit Symbolic Power

Nomi should support symbolic and meta-level programming, but only with visible
boundaries.

```python
expr = quote:
    (x + 0) * 1

normal = expr //. [
    x + 0 -> x,
    x * 1 -> x,
]
```

Macros are advanced functions over quoted code:

```python
macro assert_equal(left, right):
    quote:
        if {left} != {right}:
            raise AssertionError(f"{left} != {right}")
```

Rules:

- ordinary runtime code is not rewritten invisibly,
- quote/eval boundaries are explicit,
- macro and rule imports are scoped,
- the expanded form should be inspectable.

This captures the useful parts of Lisp and Mathematica without making normal
programs unpredictable.

## 17. Feature Family 12: Explanation, Trace, And Inspectability

If Nomi adds high-level features, it should also make them explainable.

```python
trace "signup":
    payload:SignupPayload = request.json
    user = create_user(payload)?
    send_welcome(user)
```

Constraint failures should say which binding failed:

```text
BindingError: age failed constraint age >= 13
value: 11
message: Must be at least 13
```

Pipelines and queries should be inspectable:

```python
explain summary
```

Possible output:

```text
orders
| where status == "paid"
| derive total = price * quantity
| group by customer_id
| summarize revenue = sum(total), count = count()
| order by revenue desc
```

This is especially important for SQL/KDB/APL/Mathematica-inspired power:
high-level transformation should come with high-level explanation.

## 18. Preferred Staging

### Stage 1: Everyday Coherence

Admit the features that reduce daily boilerplate most clearly:

- `func` and arrow functions,
- constrained binding with messages,
- constrained parameters and block parameters,
- pattern binding and `match`,
- caller-side block calls and `yield`,
- `data` and `shape`,
- safe access and fallback,
- pipelines,
- block-based cleanup/retry/timeout/test.

### Stage 2: Data Fluency

Add the surface needed for table-heavy and collection-heavy work:

- table values,
- `where`, `select`, `derive`, `group`, `join`, `summarize`, `order`,
- query blocks if pipeline syntax is not enough,
- column/vector operations,
- streaming and batching blocks.

### Stage 3: Scoped Power

Add advanced features with strict boundaries:

- scoped extension functions,
- traits/protocols,
- `use` capabilities,
- `quote`,
- rewrite rules,
- macros,
- explainable transformations.

### Stage 4: Radical But Inspectable

Explore only after the daily core is stable:

- calculational blocks,
- relations and bidirectional functions,
- live/timeline values,
- counterfactual execution,
- proof-carrying functions,
- explicit worlds/effects.

These may define Nomi's long-term identity, but they should not destabilize the
daily language.

## 19. Admission Test For Any New Feature

A proposed feature should answer yes to these questions:

1. Does it make a common task simpler at first read?
2. Does it reuse binding, function, call, block, pattern, table, policy, quote,
   or rewrite?
3. Can a programmer inspect the desugaring or explanation?
4. Is its scope visible?
5. Does failure produce a local, useful error?
6. Would a Python programmer recognize the rough intent?
7. Does it avoid becoming a second hidden language?

If not, keep it library-first.

## 20. A Target Daily Example

```python
data User(id:int, name:str, email:str?, active:bool = True)

shape SignupPayload:
    email:str, contains(email, "@") else "Invalid email"
    age:int, age >= 13 else "Must be at least 13"
    name:str?

func signup(request)
with timeout(2 seconds), trace("signup"), rate(limit=100/minute):
    payload:SignupPayload = request.json
    else error:
        return bad_request(error)

    email = payload.email |> strip |> lower
    name = payload.name ?: "friend"

    require not users.exists(email=email):
        user = User(id=new_id(), name=name, email=email)

        transaction(db):
            users.insert(user)?
            send_welcome(user) background

        return created(user)
    else:
        return conflict("Email already registered")
```

The programmer sees ordinary work:

- bind external JSON to a shape,
- validate with useful messages,
- clean and default values,
- require a condition,
- run a transaction,
- propagate ordinary failures,
- start background work,
- return a response.

The designer sees the small core:

- binding,
- constraints,
- functions,
- calls,
- blocks,
- policies,
- pattern/failure flow.

## 21. A Target Data Example

```python
summary = query orders -> o:
    where o.status == "paid"
    derive total = o.price * o.quantity
    group by o.customer_id
    select {
        customer_id: o.customer_id,
        revenue: sum(total),
        first_order: min(o.created_at),
        last_order: max(o.created_at),
    }
    order by revenue desc
```

This should feel like SQL when SQL is the right mental model, like KDB/APL when
columnar/vector operations matter, and like Python when embedded in ordinary
application code.

Desugaring is relational:

```text
orders
| filter status == paid
| derive total
| group customer_id
| aggregate revenue, first_order, last_order
| order
```

No string query language is required for the common case.

## 22. Closing Position

Nomi's opportunity is not to add every elegant idea from Mathematica, Scala,
Kotlin, Groovy, APL, ALGOL, Scheme, KDB, SQL, Ruby, Rust, and Python.

The opportunity is to compress their best lessons into a small number of habits:

- bind values with meaning,
- shape data at the boundary,
- pass blocks into control,
- compose transformations left-to-right,
- treat collections and tables as first-class,
- handle absence and failure deliberately,
- scope powerful extensions,
- expose symbolic power explicitly,
- explain high-level behavior when asked.

If those habits become ordinary, Nomi can drastically reduce the complexity of
typical programming tasks without making the programmer feel the complexity that
the language implementation absorbs.

## Appendix: Source Documents Reviewed

- [ai-codex_project_overview_vision.md](ai-codex_project_overview_vision.md)
- [artifacts_and_usage.md](artifacts_and_usage.md)
- [cross_language_feature_synthesis.md](cross_language_feature_synthesis.md)
- [delta_on_python.md](delta_on_python.md)
- [everyday_radical_language_ideas.md](everyday_radical_language_ideas.md)
- [Implementation_guideline.md](Implementation_guideline.md)
- [language_syntax_synthesis.md](language_syntax_synthesis.md)
- [nomi_language_revision_report.md](nomi_language_revision_report.md)
- [positioning_ambition_risk.md](positioning_ambition_risk.md)
- [proposed_language_feature_design_plan.md](proposed_language_feature_design_plan.md)
- [proposed_syntax_samples.md](proposed_syntax_samples.md)
- [radical_language_feature_ideas.md](radical_language_feature_ideas.md)
- [yield_to_block.md](yield_to_block.md)
- [Notes/category_theory_detour.md](Notes/category_theory_detour.md)
- [Notes/meta.md](Notes/meta.md)
- [Notes/tractable_sophistication.md](Notes/tractable_sophistication.md)
