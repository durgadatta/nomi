# Python Syntax Stretch Feature Atlas

> Status: speculative source note for Nomi design review.
>
> Purpose: list features that could, in principle, stretch Python-like syntax
> further while borrowing loved ideas from nearby and distant languages.
>
> Companion note:
> [Python Language Changes Deferred By Complexity](python_changes_deferred_by_complexity.md)
> focuses on ideas with concrete Python proposal history. This note is broader:
> it treats Python as a familiar surface to stretch, not as the final target.

## Reading This Note

Python is loved because ordinary code looks like executable prose:

```python
for item in items:
    if valid(item):
        save(item)
```

The best stretch features should preserve that quality. They should make common
program shapes clearer without turning Nomi into a museum of borrowed syntax.

The test for each idea is:

```text
Does this make intent more local, visible, and composable?
Can it reduce to Nomi's core concepts?
Can diagnostics explain it when it fails?
```

The sections below are not an implementation plan. They are a design atlas:
directions worth studying, grouped by the kind of pressure they place on a
Python-like language.

## 1. Expression-Oriented Control

Source traditions: ML, Rust, Kotlin, Scala, Ruby, Lisp, Julia.

Python separates statements and expressions strongly. This keeps syntax simple,
but it creates friction when a programmer wants to name the result of a branch,
match, loop, or protected operation.

Possible stretch:

```python
status =
    if score >= 90:
        "excellent"
    elif score >= 70:
        "solid"
    else:
        "needs_review"
```

```python
result =
    try:
        parse(raw)
    except ParseError as error:
        recover(error)
```

Why people like it:

- It reduces temporary variables and mutation.
- It makes "this control flow computes a value" explicit.
- It aligns with functional and expression-oriented languages.

Risk:

- Python's indentation blocks were designed as statements, not expression
  subtrees.
- `return`, `break`, `continue`, `yield`, and exceptions become harder to
  reason about inside value-producing blocks.

Nomi angle:

Expression-oriented control is attractive if it reduces to `Block` and `Value`
without creating two meanings for the same syntax. The first safe version might
be expression-valued `if` and `match`, while loop-valued and try-valued forms
remain later research.

## 2. Pipeline And Threading Operators

Source traditions: Unix pipes, Elixir, F#, Clojure, R/tidyverse, Julia
packages, shell languages.

Python call nesting can hide the data path:

```python
result = summarize(clean(load(path)))
```

Possible stretch:

```python
result = path |> load |> clean |> summarize
```

With arguments:

```python
users
    |> filter(active)
    |> sort_by(_.last_login)
    |> take(20)
```

Why people like it:

- The main value flows left to right.
- Each transformation is visible as a step.
- It works especially well in data cleanup, notebooks, CLIs, and text
  processing.

Risk:

- Placeholder rules can get complicated.
- Python already has method chaining, comprehensions, generator expressions,
  and assignment expressions; a pipeline must earn its place.
- Debugging intermediate values needs first-class trace support.

Nomi angle:

Pipelines fit Nomi if they reduce to ordinary calls and can produce traceable
intermediate diagnostics:

```text
x |> f(a) |> g
=> g(f(x, a))
```

or:

```text
x |> f(_, a) |> g
=> g(f(x, a))
```

## 3. Placeholder And Partial Application Syntax

Source traditions: Scala, Kotlin, Haskell sections, Clojure threading,
Mathematica slots, Julia's partial-application idioms.

Python often needs small lambdas:

```python
sorted(users, key=lambda user: user.profile.name.lower())
```

Possible stretch:

```python
sorted(users, key=_.profile.name.lower())
```

```python
add_tax = _ * 1.08
is_adult = _.age >= 18
```

Why people like it:

- It makes common callback shapes compact.
- It removes repeated throwaway names.
- It pairs well with pipelines and collection transforms.

Risk:

- `_` already has meanings: throwaway binding, REPL last result, gettext alias.
- Implicit function creation can hide arity and scope.
- Multiple placeholders need clear ordering rules.

Nomi angle:

This can be useful, but only if placeholder expressions are visibly function
values. Nomi may prefer explicit arrow syntax for first-pass clarity:

```python
user => user.profile.name.lower()
```

Then consider `_` only for very common one-argument transforms.

## 4. Generalized Block Calls

Source traditions: Ruby blocks, Kotlin trailing lambdas, Smalltalk message
blocks, Lisp higher-order control, Python context managers.

Python has `with`, decorators, callbacks, generators, and context managers.
They solve related control-shaping problems through separate mechanisms.

Possible stretch:

```python
retry(3):
    fetch(url)
```

```python
transaction(db) -> tx:
    tx.insert(order)
    tx.insert(audit_entry)
```

```python
users.each() -> user:
    send_email(user)
```

Why people like it:

- It lets libraries define readable control forms.
- It turns callback-heavy APIs into direct code.
- It unifies retries, transactions, iteration, tests, tracing, and resources.

Risk:

- Hidden execution order can surprise readers.
- Resuming a caller block more than once is powerful but delicate.
- Cleanup, exceptions, return, cancellation, and nested blocks need exact
  semantics.

Nomi angle:

This is one of the strongest candidates for Nomi because it can reduce to the
existing core:

```text
call receives block -> callee invokes block with yield -> diagnostics explain
```

The feature should stay small before it becomes a general effect system.

## 5. Data Declarations And Closed Variants

Source traditions: ML algebraic data types, Rust enums, Swift enums, Kotlin
sealed classes, Scala case classes, Haskell data declarations.

Python has classes, dataclasses, named tuples, enums, and pattern matching, but
no single simple construct for "these are the variants of this domain value."

Possible stretch:

```python
data Payment:
    Card(number:str, expiry:str)
    Cash(amount:Money)
    Credit(account_id:str)
```

```python
match payment:
    case Card(number, expiry):
        ...
    case Cash(amount):
        ...
    case Credit(account_id):
        ...
```

Why people like it:

- It makes domain shapes explicit.
- Exhaustive matching becomes possible.
- Constructors, display, equality, destructuring, and validation can be
  generated coherently.

Risk:

- Python classes are open and dynamic; closed variants are a different model.
- Interop with normal objects must be clear.
- Generated behavior can become magical if not inspectable.

Nomi angle:

Nomi already wants a `data` story. This is a high-value direction because it
supports the "one data story" and "one pattern story" from the foundation.

## 6. Rich Patterns Beyond Python Match

Source traditions: ML, Haskell, Rust, Erlang, Elixir, Scala, Prolog, Racket.

Python pattern matching is useful, but conservative. A stretched pattern system
could cover more binding and validation cases.

Possible stretch:

```python
match response:
    case {"ok": True, "user": User(name:(str, len(name) > 0))}:
        ...
```

```python
case [first, *middle, last] if first <= last:
    ...
```

```python
case Point(x, y) where x*x + y*y < 100:
    ...
```

Why people like it:

- It makes data shape and constraints visible together.
- It reduces manual `isinstance`, key-checking, and unpacking code.
- It can power destructuring assignment, loop filters, function parameters,
  and block parameters.

Risk:

- Patterns can become a second language inside the language.
- Capture names, constants, predicates, and guards are easy to confuse.
- Partial binding on failed matches needs precise semantics.

Nomi angle:

Patterns should reuse binding constraints. Avoid separate mini-syntax for
validation. A pattern match should be explainable as:

```text
test shape -> bind tentative names -> check constraints -> commit or fail
```

## 7. First-Class Constraints And Refinement-Like Types

Source traditions: Eiffel contracts, Racket contracts, Liquid Haskell, F*,
Pydantic, JSON Schema, TypeScript narrowing, Rust type states.

Python annotations describe types for tools, but runtime value rules usually
live in separate code.

Possible stretch:

```python
age:int, age >= 0 = raw_age
```

```python
func signup(email:(str, contains("@")), age:(int, age >= 13)):
    ...
```

```python
data User:
    name:(str, len(name) > 0)
    age:(int, age >= 0)
```

Why people like it:

- It places the rule where the name is introduced.
- It improves API boundaries.
- It makes validation, documentation, examples, and diagnostics share one
  source of truth.

Risk:

- Runtime checks have cost.
- Predicate evaluation can have side effects unless constrained.
- Static and runtime meanings may diverge.
- Error messages need to identify both the value and the failed rule.

Nomi angle:

This is central. Nomi should treat constraints as a semantic primitive rather
than as annotation metadata.

## 8. Effect And Capability Markers

Source traditions: Koka, Eff, OCaml effects, Haskell monads, Rust ownership and
borrowing, Pony capabilities, object-capability systems.

Python functions can read files, mutate globals, perform network calls, await,
raise, log, and spawn work without the signature saying much about those
effects.

Possible stretch:

```python
func load_user(id:UserId) -> User uses db, io:
    ...
```

```python
func render(user:User) -> Html pure:
    ...
```

Why people like it:

- It makes important behavior visible at boundaries.
- It helps testing, sandboxing, concurrency, and security.
- It supports local reasoning about what a function is allowed to do.

Risk:

- Full effect systems are difficult to teach.
- Python libraries are dynamic and often effectful by convention.
- Over-precise effect tracking can make everyday code feel bureaucratic.

Nomi angle:

Postpone full effects. Start with lightweight capability-oriented checks for
high-value boundaries, such as file, network, environment, database, and
subprocess access. Keep the everyday language friendly.

## 9. Result-Oriented Error Handling

Source traditions: Rust `Result`, Haskell `Either`, Swift `try?`, Go explicit
errors, Zig error unions, Railway-oriented programming.

Python exceptions are powerful but nonlocal. Some workflows benefit from errors
as values.

Possible stretch:

```python
user = parse_user(raw)?
profile = fetch_profile(user.id)?
return render(profile)
```

or:

```python
match parse_user(raw):
    case Ok(user):
        ...
    case Err(error):
        diagnose(error)
```

Why people like it:

- Expected failures become visible in types and control flow.
- It composes well in parsers, validation, CLI tools, and API boundaries.
- It can produce better diagnostics than generic exceptions.

Risk:

- Python already has exceptions; adding a parallel model can split style.
- `?`-style propagation is terse but can hide exits.
- Mixing exceptions and result values requires conventions.

Nomi angle:

Nomi may benefit from `Result` for validation and parsing while keeping
exceptions for unexpected failures. The diagnostic story should decide this,
not syntax fashion.

## 10. Multiple Dispatch And Open Generic Functions

Source traditions: Julia, CLOS, Dylan, R S3/S4, multimethod libraries.

Python methods dispatch primarily on the receiver. `functools.singledispatch`
adds one-argument generic functions, but multi-argument dispatch is not a core
language idea.

Possible stretch:

```python
func collide(a:Circle, b:Rectangle):
    ...

func collide(a:Rectangle, b:Circle):
    ...
```

Why people like it:

- It models operations where no single object should "own" the method.
- It is excellent for numeric towers, geometry, symbolic systems, and data
  transformations.
- It keeps behavior extensible across independent types.

Risk:

- Dispatch order and ambiguity rules can get complicated.
- Runtime performance and caching matter.
- It interacts heavily with modules, imports, inheritance, and static analysis.

Nomi angle:

Multiple dispatch is attractive but should probably wait until single-dispatch
functions, data, constraints, and modules are stable. It belongs near advanced
generic programming, not the first everyday core.

## 11. Units, Dimensions, And Domain Quantities

Source traditions: F#, Ada, Frink, Mathematica, scientific Python libraries,
type-level units in several languages.

Python numeric code often loses domain meaning:

```python
distance = 10
time = 2
speed = distance / time
```

Possible stretch:

```python
distance = 10 meters
duration = 2 seconds
speed = distance / duration
```

or:

```python
distance: Quantity["length"] = 10.m
```

Why people like it:

- It catches unit mistakes early.
- It makes scientific and engineering code readable.
- It preserves meaning through arithmetic.

Risk:

- Syntax can conflict with attribute access, calls, and multiplication.
- Unit systems need conversions, dimensions, display rules, and performance.
- It may be too domain-specific for the first language core.

Nomi angle:

This is a good example of a feature that might belong in a library if Nomi has
strong constraints, operator definitions, and display protocols. Built-in
syntax should wait.

## 12. Query And Collection Comprehension Syntax

Source traditions: SQL, LINQ, list comprehensions, Haskell, R/tidyverse,
Pandas, APL, jq.

Python comprehensions are beloved, but complex data queries often become nested
loops, chained method calls, or library-specific strings.

Possible stretch:

```python
active_names =
    from user in users
    where user.active
    order by user.last_login desc
    select user.name
```

or pipeline-shaped:

```python
users
    |> where(_.active)
    |> order_by(_.last_login, desc=True)
    |> select(_.name)
```

Why people like it:

- It gives data transformations a readable shape.
- It can target in-memory collections, SQL, dataframe engines, or streams.
- It makes filtering, grouping, joining, and projection explicit.

Risk:

- Query syntax easily becomes a second language.
- Backend translation can hide runtime behavior.
- Python already has comprehensions; the new form must justify itself.

Nomi angle:

Prefer a small collection-transform core plus traceable pipelines before a full
query language. Add SQL-like syntax only if ordinary transformations cannot
stay readable.

## 13. Array And Table-Oriented Operators

Source traditions: APL, J, K, R, MATLAB, NumPy, Julia, Mathematica.

Python reaches for libraries for vectorization. That works well, but the syntax
often exposes library compromises.

Possible stretch:

```python
normalized = (values - mean(values)) / std(values)
```

with first-class elementwise semantics, broadcasting, and shape diagnostics.

Why people like it:

- It makes numerical and tabular code concise.
- Shape-aware errors can be much better than generic runtime failures.
- It supports AI, statistics, image processing, and scientific workflows.

Risk:

- Elementwise vs scalar operations must be clear.
- Broadcasting rules are powerful but nontrivial.
- APL-like notation can become expert-only quickly.

Nomi angle:

Keep the first language ordinary. Later, Nomi could support shape constraints
and array protocols without making APL notation part of the base syntax.

## 14. Hygienic Macros And Syntax Extensions

Source traditions: Lisp, Scheme/Racket, Rust macros, Scala metaprogramming,
Elixir macros, Template Haskell.

Python has decorators, metaclasses, import hooks, AST transforms, and code
generation, but not a mainstream hygienic macro system.

Possible stretch:

```python
macro unless(condition):
    expand to:
        if not condition:
            yield
```

Why people like it:

- It lets libraries create new abstractions without waiting for language
  changes.
- It can remove boilerplate cleanly.
- It is powerful for DSLs, testing, data declarations, and embedded languages.

Risk:

- Macro systems can fragment a language.
- Tooling, formatting, debugging, and error messages become harder.
- Hygiene, phase separation, and expansion order are deep topics.

Nomi angle:

Do not put general macros in the first language. Nomi's design goal is a small,
rememberable core. Macro-like power may eventually belong behind a disciplined
plugin or compile-time API.

## 15. Keyword Shorthand And Record Literals

Source traditions: JavaScript object shorthand, Ruby keyword arguments, Swift
member shorthand, Kotlin named parameters, Elm records.

Python keyword arguments are readable but repetitive:

```python
User(name=name, email=email, active=active)
```

Possible stretch:

```python
User(name, email, active)
```

when fields are known, or:

```python
{name, email, active}
```

meaning:

```python
{"name": name, "email": email, "active": active}
```

Why people like it:

- It reduces boilerplate in data construction.
- It makes mapping from local names to fields direct.
- It supports common API and JSON-shaped code.

Risk:

- It can hide whether a position, field name, or local variable is being used.
- Python already uses `{name}` for sets, not mappings.
- Shorthand is pleasant until names diverge.

Nomi angle:

Useful, but only after `data` and mapping literals are settled. Field punning
should be optional sugar over explicit binding.

## 16. String Templates With Structure

Source traditions: JavaScript template literals, Ruby interpolation, Swift
string interpolation, SQL parameterization, shell heredocs.

Python f-strings are loved, but they produce strings directly. Many contexts
need structured interpolation: SQL, shell commands, HTML, regexes, paths, and
diagnostics.

Possible stretch:

```python
sql"select * from users where id = {user_id}"
html"<a href={url}>{label}</a>"
path"/Users/{name}/Downloads"
```

Why people like it:

- It keeps the readability of interpolation while preserving structure.
- It can make injection-safe APIs the default.
- It lets domain-specific validators inspect the template before execution.

Risk:

- Prefixes can proliferate.
- Each template domain needs escaping and validation rules.
- Runtime and compile-time behavior must be clear.

Nomi angle:

This is promising for diagnostics and safe boundaries. Treat templates as
typed values, not just prettier strings.

## 17. Traits, Protocols, And Extension Methods

Source traditions: Rust traits, Swift protocols and extensions, Haskell type
classes, Go interfaces, Kotlin extension functions, Scala implicits.

Python has duck typing, ABCs, protocols for type checkers, and monkey patching,
but no single clean story for extending behavior onto existing types.

Possible stretch:

```python
trait JsonEncode[T]:
    func to_json(value:T) -> Json

impl JsonEncode[User]:
    func to_json(user):
        ...
```

or extension style:

```python
extend str:
    func slug():
        ...
```

Why people like it:

- It separates data ownership from behavior extension.
- It helps avoid inheritance abuse.
- It can make generic algorithms clearer.

Risk:

- Method lookup can become less local.
- Conflicting implementations need rules.
- Import order and module visibility matter.

Nomi angle:

Protocols are likely useful before full traits. Extension methods are tempting,
but they should not make it hard to answer "where did this method come from?"

## 18. Structured Concurrency

Source traditions: Trio, Kotlin coroutines, Swift structured concurrency,
Erlang supervision trees, Go contexts, async/await ecosystems.

Python has `async`/`await`, tasks, event loops, and libraries, but structured
concurrency is mostly library-level.

Possible stretch:

```python
concurrent:
    user = fetch_user(id)
    orders = fetch_orders(id)
return render(user, orders)
```

```python
supervise:
    run worker_a()
    run worker_b()
```

Why people like it:

- Child work has a visible lifetime.
- Cancellation and failure can be scoped.
- It avoids orphaned tasks and unclear ownership.

Risk:

- Async semantics are already a major teaching cost.
- Scheduling, cancellation, resource cleanup, and exception aggregation are
  difficult to specify.
- It may pull the first language too far toward systems concerns.

Nomi angle:

Postpone. The block-call model may eventually support structured concurrency,
but Nomi should first prove ordinary block control with retries, transactions,
and tracing.

## 19. Examples As Executable Language Objects

Source traditions: doctest, literate programming, R notebooks, Rust doc tests,
property-based testing, example-based specifications.

Python has doctest and testing frameworks, but examples are not core language
objects.

Possible stretch:

```python
func slug(text:str) -> str:
    ...

example:
    slug("Hello, World!") == "hello-world"
```

```python
example user signup:
    signup("a@example.com", age=20)
    raises signup("a@example.com", age=10)
```

Why people like it:

- Examples live next to the code they explain.
- They support teaching, testing, diagnostics, and AI-assisted exploration.
- They give a language a built-in way to show intent.

Risk:

- Test execution, isolation, fixtures, and nondeterminism need rules.
- Examples can rot if treated as comments rather than checked artifacts.
- Tooling must present failures clearly.

Nomi angle:

This aligns strongly with the foundation's `Example`, `Trace`, and
`Diagnostic` concepts. It is not merely testing syntax; it is part of how code
explains itself.

## 20. Traceable Evaluation And Explainable Reduction

Source traditions: debuggers, notebooks, spreadsheets, Mathematica evaluation,
term rewriting systems, teaching languages, proof assistants.

Python executes directly but does not expose a first-class reduction trace for
ordinary code.

Possible stretch:

```python
trace:
    total = invoice.items |> map(_.price) |> sum
```

Diagnostic output could show each pipeline step, binding check, pattern match,
and block invocation.

Why people like it:

- It helps learning and debugging.
- It makes transformations inspectable.
- It pairs naturally with constraints and examples.

Risk:

- Tracing everything can be expensive and noisy.
- Privacy and security matter when traces contain real data.
- Optimizations can obscure source-level steps.

Nomi angle:

This is a major differentiator. Nomi should design features so they can explain
their reduction locally. Traceability can be the glue between ambitious syntax
and human trust.

## Feature Admission Categories

High alignment with Nomi's current foundation:

- generalized block calls;
- constrained binding and contracts;
- data declarations with closed variants;
- richer patterns sharing binding constraints;
- executable examples;
- traceable pipelines and evaluation.

Promising but should wait for stronger core semantics:

- expression-valued `try` and loops;
- placeholder partial application;
- result-oriented propagation syntax;
- structured string templates;
- protocols and traits;
- query syntax.

Research-heavy or likely later-stage:

- full effect systems;
- multiple dispatch;
- units and dimensions as syntax;
- array/table operators;
- hygienic macros;
- structured concurrency.

## Design Warnings

1. Do not copy a syntax because it is loved elsewhere; identify the operation
   people love.
2. Do not add a second mini-language when binding, constraints, calls, blocks,
   or patterns can explain the feature.
3. Do not make clever one-line syntax that becomes hard to diagnose.
4. Do not let advanced notation distort the first everyday language.
5. Do not assume Python's limits are accidental; many are load-bearing
   simplicity choices.
6. Do notice when Python's limits come from historical constraints that Nomi
   does not share.

## Core Question For Each Candidate

For every feature above, ask:

```text
What is the smallest Nomi primitive this reduces to?
What does the programmer see when it succeeds?
What does the programmer see when it fails?
Can it be taught as part of the same story as binding, function, call, data,
pattern, block, example, trace, and diagnostic?
```

If the answer is clear, the feature is a candidate. If not, it remains source
material.
