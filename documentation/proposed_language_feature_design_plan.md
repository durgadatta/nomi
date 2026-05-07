# Proposed Language Feature Design Plan

> Status: design proposal, not implementation guidance.
>
> This document captures proposed Nomi language features at the level of user-facing
> semantics. The goal is to make sample code fragments meaningful and implementable
> later, while keeping the design centered on usability and Python-like readability.
>
> Companion documents:
>
> - [Proposed Syntax Samples](proposed_syntax_samples.md) is the sample-heavy
>   syntax catalog.
> - [Language Syntax Synthesis](language_syntax_synthesis.md) explains the
>   small-core philosophy and cross-language reductions behind the catalog.
> - [Cross-Language Feature Synthesis Examples](cross_language_feature_synthesis.md)
>   compares similar features across several languages before proposing Nomi
>   forms.
> - [Nomi Language Revision Report](nomi_language_revision_report.md) records a
>   report-style proposed language revision.
> - [Radical Language Feature Ideas](radical_language_feature_ideas.md) collects
>   more speculative ideas such as calculational blocks, relations, proof-carrying
>   code, live values, worlds, semantic holes, and counterfactual execution.

## Purpose

Nomi should feel close enough to Python that a Python programmer can read small
programs immediately, but the meaning of the core constructs should be cleaner,
more uniform, and less accidental.

The design priority is not ease of implementation. It is the shape of the
language as experienced by the programmer:

- Can the code be read locally?
- Does syntax say what kind of thing is being introduced?
- Do constraints and blocks mean the same thing across contexts?
- Can a simple fragment be explained without referring to parser internals?
- Does a feature reduce mental overhead compared with ordinary Python?

Implementation can come later. This plan defines the semantic target.

## Cross-Language Syntax Synthesis

This section lists coherent proposed syntax families for Nomi. The intent is not
to copy any one language, but to synthesize useful ideas from Python,
Mathematica, ALGOL, APL, Lisp, Ruby, Scala, Kotlin, and related language
families into a small Python-readable surface.

The proposed direction:

- Python supplies indentation, plain reading order, ordinary calls, and everyday
  approachability.
- ALGOL supplies block structure, lexical scope, and procedural clarity.
- Lisp supplies the idea that code has a regular underlying structure and that
  programs can manipulate program-shaped values.
- Mathematica supplies symbolic transformation, rules, and expression rewriting.
- APL supplies concise array-oriented thinking and whole-collection operations.
- Ruby supplies caller-side blocks as ergonomic control abstractions.
- Scala supplies expression orientation, pattern matching, and typed functional
  composition.
- Kotlin supplies null-safety, trailing functional arguments, extension-style
  usability, and lightweight data modeling.

Nomi should borrow the ideas, not the visual noise. The syntax should remain
readable as ordinary text.

### Syntax Tiers

Not every idea should enter the core language at the same level.

**Core syntax** should be small and stable:

- `func` definitions,
- arrow functions,
- binding constraints,
- pattern binding,
- block calls,
- `yield` to attached blocks,
- expression-oriented conditionals and matching.

**Candidate syntax** should be designed but held until examples justify it:

- pipe and composition operators,
- symbolic rewrite rules,
- array rank/map shorthand,
- null-safe access,
- extension declarations,
- lightweight data/type declarations.

**Library-led syntax** should start as ordinary functions and blocks before it
becomes language syntax:

- concurrency scopes,
- transactions,
- resources,
- tests,
- parsers,
- symbolic algebra,
- dataframes and tensor operations.

### Coherent Proposed Syntax List

| Idea | Proposed syntax | Main influence | Meaning |
| --- | --- | --- | --- |
| Named function | `func f(x): ...` | Python, ALGOL | Bind `f` to a function with block body. |
| Function value | `(x) => x + 1` | Scala, Kotlin | Create an expression-level function value. |
| Constrained binding | `x:int, x > 0 = 3` | Python hints, contracts | Bind only if all constraints pass. |
| Pattern binding | `(x, y) = point` | Python, ML, Scala | Destructure a value into names. |
| Block call | `retry(3): ...` | Ruby, Python blocks | Pass caller-side code into callee-owned control. |
| Yield to block | `yield value` | Python generators, Ruby | Invoke the attached block with a value. |
| Block parameter | `each(xs) -> x: ...` | Ruby, Kotlin | Name values yielded by the callee. |
| Match expression | `match value: case ...` | Python, Scala, ML | Choose by structural pattern. |
| Pipe forward | `value |> f(_)` | F#, Elixir, Mathematica | Pass a value through a readable transformation chain. |
| Composition | `f >> g` | APL, functional languages | Build a function that applies `f`, then `g`. |
| Rewrite rule | `expr /. pattern -> replacement` | Mathematica | Transform expression-shaped data by rule. |
| Quoted form | `quote: ...` or `'expr` | Lisp, Mathematica | Treat code-shaped syntax as data. |
| Null-safe access | `user?.name` | Kotlin | Access only if the receiver is not empty/null. |
| Defaulting | `name ?: "guest"` | Kotlin | Use fallback when left side is empty/null. |
| Range | `1..10` | Kotlin, Ruby | Inclusive range value. |
| Half-open range | `1..<10` | Kotlin, Swift | Range excluding the end. |
| Spread | `f(*xs, **opts)` | Python | Expand sequence or mapping into arguments. |
| Data declaration | `data Point(x:int, y:int)` | Kotlin, Scala | Declare a lightweight structured value. |
| Extension function | `func String.words(self): ...` | Kotlin, Scala | Add callable behavior to an existing type's interface. |
| Resource block | `using resource: ...` | Python, C#, Ruby blocks | Scoped setup and cleanup, possibly library-defined. |

This table is a proposal map, not a final grammar.

### Function And Call Syntax

Nomi should keep ordinary Python-style calls:

```python
total = add(2, 3)
```

Named functions use `func`:

```python
func add(x:int, y:int):
    return x + y
```

Function values use arrows:

```python
add = (x:int, y:int) => x + y
```

These two forms should have the same function semantics. The distinction is
surface usability:

- `func` is for named, block-shaped definitions.
- `=>` is for expression-shaped function values.

### Pipeline Syntax

Python reads well for nested calls until transformations become too deeply
nested:

```python
result = summarize(normalize(parse(text)))
```

A pipeline form can expose left-to-right data flow:

```python
result = text |> parse(_) |> normalize(_) |> summarize(_)
```

Meaning:

- start with `text`,
- substitute it into `_` in the next stage,
- pass each stage result forward.

For single-argument calls, a shorthand may be allowed:

```python
result = text |> parse |> normalize |> summarize
```

This borrows from functional pipeline languages and Mathematica's postfix style,
but keeps a Python-like reading order. The placeholder `_` should mean "the
value flowing through this pipeline position" only in syntactic contexts that
make that meaning obvious.

### Function Composition

Composition creates a function instead of immediately applying values:

```python
clean = strip >> lower >> normalize_space
```

Meaning:

```python
clean(x) == normalize_space(lower(strip(x)))
```

This is APL-like and functional, but expressed with ASCII operators. It should be
used for reusable transformation functions, not for ordinary imperative steps.

Pipeline applies now. Composition builds a later callable.

```python
value |> clean      # apply now
clean = f >> g      # define composed function
```

### Pattern Binding And Matching

Binding should support patterns consistently:

```python
(x, y) = point
{"name": name, "age": age} = user
```

The same pattern idea should appear in `match`:

```python
match response:
    case {"status": 200, "body": body}:
        body
    case {"status": code} if code >= 400:
        raise RequestError(code)
```

Meaning:

- patterns bind names,
- guards refine cases,
- failed patterns do not partially bind names,
- successful patterns expose their bindings in the case body.

This synthesis draws from Python pattern matching, ML/Scala destructuring, and
Lisp's long tradition of structural code/data manipulation.

### Symbolic Rewrite Rules

Mathematica's strongest idea for Nomi is not its bracket syntax, but its rule
semantics: transform expression-shaped values by matching patterns.

Candidate syntax:

```python
simplified = expr /. x + 0 -> x
```

Meaning:

- treat `expr` as a structured expression value,
- find subexpressions matching `x + 0`,
- replace them with `x`,
- produce the transformed expression.

Multiple rules:

```python
simplified = expr /. [
    x + 0 -> x,
    x * 1 -> x,
    x * 0 -> 0,
]
```

Rules should operate on explicit expression values, not secretly rewrite normal
runtime code. This preserves local reasoning.

Open syntax question: `->` is also useful for block yielded values. If both
forms remain, context must make them visually unambiguous:

```python
each(xs) -> x:          # block value binding
expr /. pattern -> out  # rewrite rule
```

### Quoted Expressions

To support symbolic rewriting and code-shaped data, Nomi may need a quote form.
Lisp uses quote; Mathematica treats expressions uniformly.

Candidate forms:

```python
expr = quote:
    x + 0
```

or:

```python
expr = '(x + 0)
```

Meaning:

- do not evaluate `x + 0` as normal code,
- capture its structured expression form as data.

The block form is more readable for large expressions:

```python
rule_input = quote:
    if amount > 0:
        account.balance -= amount
```

This should remain an advanced feature. It is powerful, but it can easily harm
ordinary readability if used casually.

### Array And Collection Orientation

APL's lesson is that whole-array thinking can remove incidental loops. Nomi
should make collection operations readable before making them cryptic.

Candidate forms:

```python
xs.map((x) => x * 2)
xs.filter((x) => x > 0)
xs.reduce(0, (a, x) => a + x)
```

Possible pipeline form:

```python
result = (
    xs
    |> map(_, (x) => x * 2)
    |> filter(_, (x) => x > 0)
    |> sum
)
```

Possible array-lift shorthand:

```python
ys = xs.*2
zs = xs.+ys
```

Meaning:

- apply the scalar operation elementwise.

This shorthand is intentionally risky. It is compact, but Nomi should not become
APL-like in visual density by default. The safer baseline is named collection
operations plus pipelines.

### Ranges And Slices

Ranges are common enough to deserve clear syntax:

```python
1..10      # inclusive range
1..<10     # half-open range
```

Use cases:

```python
for i in 1..<10:
    print(i)

xs[1..<4]
```

The half-open range should be favored for indexing because it matches Python's
slice convention. Inclusive ranges are useful for human-facing domains.

### Null And Optional Values

Nomi should avoid making absence handling verbose in application code.

Candidate syntax:

```python
city = user?.address?.city
name = user.name ?: "guest"
```

Meaning:

- `?.` stops access when the receiver is empty/null and returns the empty/null
  value.
- `?:` provides a fallback when the left side is empty/null.

This comes from Kotlin and related languages. The design question is whether
Nomi should have a distinguished `None`-like value only, or a richer optional
value model.

### Data Declarations

For simple structured values, a Kotlin/Scala-like data declaration may be more
usable than a full class:

```python
data Point(x:int, y:int)
```

Meaning:

- declare a structured value type,
- create fields `x` and `y`,
- generate ordinary construction, equality, and readable representation.

Example:

```python
p = Point(2, 3)
print(p.x)
```

This should be a convenience for value-shaped data, not a replacement for a
full object system.

### Extension-Style Functions

Kotlin and Scala show that method-like usability can be separated from actual
class ownership.

Candidate syntax:

```python
func String.words(self):
    return self.split()
```

Use:

```python
"hello world".words()
```

Meaning:

- define a function whose first receiver is a `String`,
- allow method-call syntax as a convenience,
- do not mutate the original `String` type globally unless the module/import
  system makes that extension visible.

This is mainly a usability feature. It lets library authors create fluent APIs
without forcing all behavior into classes.

### Block-Based Resource And Policy Syntax

Ruby's blocks and Python's `with` suggest a broader Nomi direction:

```python
transaction(db):
    create_user()
    send_welcome()
```

```python
timeout(5):
    fetch(url)
```

```python
parallel():
    fetch_user()
    fetch_orders()
```

These should all be explainable as block calls. The syntax should not require a
new language keyword for every policy. The language supplies the block mechanism;
libraries supply the control patterns.

### Expression-Oriented Statements

Scala and Kotlin make many constructs expressions. Nomi should move in that
direction selectively.

Candidate:

```python
label = if score >= 90:
    "excellent"
else:
    "ok"
```

Candidate:

```python
kind = match value:
    case int:
        "number"
    case str:
        "text"
    case _:
        "other"
```

Meaning:

- the construct produces a value,
- the chosen branch's final expression is the value,
- statement-style layout is preserved for readability.

This avoids the common split where small expressions are composable but larger
control structures are trapped as statements.

### Keywords To Prefer

Nomi should prefer plain, semantic keywords:

| Concept | Candidate keyword |
| --- | --- |
| Function definition | `func` |
| Lightweight data value | `data` |
| Interface/protocol | `trait` or `protocol` |
| Explicit constant binding | `const` |
| Mutable cell or variable marker | possibly none by default |
| Symbolic quote | `quote` |
| Pattern matching | `match`, `case` |
| Local import/use | `use` or Python-compatible `import` |

Keyword growth should be conservative. A library-defined block call is often
better than a new keyword.

### Syntax To Avoid Or Treat Carefully

Some powerful ideas from the inspiration languages should be handled carefully:

- Avoid pervasive punctuation like APL unless confined to array libraries.
- Avoid Lisp-like parenthesis-first syntax at the surface, even if the internal
  representation is regular.
- Avoid Mathematica-style capitalized builtins and bracket-heavy calls.
- Avoid Ruby's highly implicit receiver conventions where they harm local
  clarity.
- Avoid Scala's tendency toward many equivalent spellings for the same idea.
- Avoid Kotlin-style annotation and modifier buildup unless it remains readable.

The synthesis should preserve a Python-like "one obvious reading" even when the
semantic model is more systematic than Python's.

## Guiding Usability Principles

### Stay Python-Readable

Nomi should preserve Python's strongest usability property: code is scanned as
plain procedural text. Indentation, familiar operators, ordinary function calls,
and statement sequencing remain central.

Nomi should avoid symbolic density unless the symbol has a clear, recurring
meaning. A feature should earn its syntax by making common code easier to read,
not merely shorter.

### Make Core Concepts Explicit

Python's `def` keyword says that something is being defined, but not what kind
of thing. Nomi uses `func` because the construct introduces a function.

This principle applies broadly:

- Function definition introduces callable behavior.
- Binding attaches a value to a name.
- Annotation constrains a binding.
- A block call passes caller-side code to a callable control abstraction.
- `yield` inside such an abstraction marks where the caller's block runs.

The same concept should keep the same meaning wherever it appears.

### Prefer One Mental Model Per Concept

Nomi should minimize avoidable splits such as:

- named function versus anonymous function,
- assignment annotation versus parameter annotation,
- context manager versus block control helper,
- loop body versus callback body.

The surface syntax can still differ when readability demands it, but the
underlying explanation should stay unified.

## Feature 1: `func` Definitions

### Surface Form

```python
func greet(name):
    print("Hello", name)
```

### Meaning

This binds the name `greet` to a function value. When called, the function maps
arguments to parameters, creates a local execution environment, runs its body,
and returns either an explicit `return` value or the default empty value.

The key semantic point is that `func` introduces a function, not a generic
definition. The binding of the name is still visible and Python-like, but the
keyword now matches the kind of value being created.

### Decorators

```python
@logged
func greet(name):
    print("Hello", name)
```

Decorators apply to the function value produced by the function definition and
then bind the decorated result to the function name. This preserves Python's
readable decorator flow.

Conceptually:

```python
greet = logged(func_value)
```

The block form remains preferred for named, decorated, annotated, or multi-step
functions.

## Feature 2: Arrow Function Literals

### Surface Form

```python
(x, y) => x + y
(x:int) => x * x
() => print("ready")
```

### Meaning

An arrow expression creates a function value directly. It is the expression-level
form of function creation.

```python
square = (x:int) => x * x
```

This means:

- create a function that accepts one parameter `x`,
- constrain `x` to `int`,
- evaluate `x * x` when called,
- return that expression result.

Arrow functions are not "lesser functions." They are ordinary function values
with concise syntax for expression-oriented cases.

### Usability Rule

Use `func` when the function has a name, decorators, several statements, or a
body that benefits from vertical structure.

Use `=>` when the function is best read inline as a value.

```python
numbers.map((x) => x * 2)
```

The readability goal is similar to Python's `lambda`, but without treating
inline functions as a special, restricted sub-language.

## Feature 3: Binding Constraints

### Surface Form

```python
age:int = 34
score: score >= 0 = 10
amount:int, amount > 0 = 25
```

### Meaning

A binding associates a name with a value. A constrained binding additionally
checks that the value satisfies the listed constraints.

```python
age:int = 34
```

This means:

- bind `34` to `age`,
- check that the value is an instance of `int`,
- allow the binding only if the check passes.

```python
score: score >= 0 = 10
```

This means:

- tentatively bind `10` to `score`,
- evaluate `score >= 0` in the binding context,
- keep the binding if the expression is true,
- otherwise raise `TypeError`.

### Multiple Constraints

```python
amount:int, amount > 0 = 25
```

This means that all constraints must pass. The binding is valid only if `amount`
is an `int` and is greater than zero.

Constraints are programmer-facing validation, not optional documentation.

### Rebinding

```python
amount:int = 25
amount = 30
amount:str = "paid"
```

Proposed semantics:

- A constrained binding records constraints on that name.
- A later plain rebinding must satisfy the active constraints.
- A later annotated rebinding replaces the old constraint set with the new one.

This gives constraints a stable meaning while still allowing the programmer to
change the intended domain explicitly.

## Feature 4: Parameter Constraints

### Surface Form

```python
func withdraw(account, amount:(int, amount > 0)):
    account.balance -= amount
```

### Meaning

Parameter binding is binding. When a function is called, arguments are first
mapped to parameters using normal Python-like call rules. After that mapping,
each parameter's constraints are checked.

```python
withdraw(my_account, 10)
```

This means:

- map `my_account` to `account`,
- map `10` to `amount`,
- check that `amount` is an `int`,
- check that `amount > 0`,
- run the function body if all checks pass.

The parentheses around `(int, amount > 0)` distinguish multiple constraints on
one parameter from multiple parameters.

### Usability Goal

The same annotation idea should work in assignment and function parameters.
Users should not have to learn a separate validation model for function calls.

## Feature 5: Block Calls

### Surface Form

```python
retry(3):
    send_request()
```

### Meaning

This calls `retry(3)` with an attached caller-side block. The block is not
ordinary function syntax and should not be mentally treated as a callback.

The block:

- is written in the caller's indentation flow,
- runs where the callee yields to it,
- sees the caller's surrounding names,
- is controlled by the callee's block-yield behavior.

The most useful mental model is:

> The callee owns the control pattern. The caller supplies the work to be placed
> inside that pattern.

### Defining a Block-Control Function

```python
func retry(max_times):
    for attempt in range(max_times):
        try:
            yield
            return
        except Exception:
            pass
```

Here, `yield` means "run the attached caller block here."

When used as:

```python
retry(3):
    send_request()
```

the `send_request()` block may be attempted up to three times, depending on the
control logic inside `retry`.

### Why This Is Not Just `with`

Python's `with` handles enter/exit resource patterns well. Nomi block calls are
intended to express broader control patterns:

- retry,
- timing,
- setup/cleanup,
- temporary policy changes,
- structured iteration,
- scoped error handling,
- eventually, concurrency or scheduling patterns.

The usability goal is to avoid forcing every control abstraction into the shape
of a context manager, callback, decorator, or loop.

## Feature 6: Yielding Values Into Blocks

### Surface Form

```python
each([1, 2, 3]) -> item:
    print(item)
```

### Meaning

The callee may yield values to the attached block. The caller names those yielded
values after `->`.

```python
func each(items):
    for item in items:
        yield item
```

Used as:

```python
each([1, 2, 3]) -> item:
    print(item)
```

This means:

- call `each` with the list,
- each time `each` yields a value, bind it to `item`,
- run the caller block with that binding,
- resume `each` after the block completes.

The user-facing behavior is close to a `for` loop, but the iteration policy is
owned by `each`.

### Multiple Yielded Values

```python
pairs(data) -> key, value:
    print(key, value)
```

This should behave like destructuring assignment at the block boundary. If the
yielded value cannot be bound to the declared names, the block call fails with a
clear binding error.

## Feature 7: Block Parameters With Constraints

### Surface Form

```python
each(users) -> user: User:
    print(user.name)
```

Alternative candidate:

```python
each(users) -> user(User):
    print(user.name)
```

### Proposed Meaning

The yielded value is bound to the block parameter and validated using the same
constraint model as assignment and function parameters.

The exact syntax needs further design. The semantic goal is clear:

- block parameters are bindings,
- bindings may have constraints,
- invalid yielded values fail at the boundary where they are received.

### Design Concern

The syntax must remain easy to scan. Block calls already use `:` for the block
body, so adding parameter constraints must not create a dense or confusing line.

This is a usability-first open question.

## Feature 8: Caller-Scope Blocks

### Sample

```python
message = "start"

once:
    message = "done"

print(message)
```

If `once` is a block-control abstraction that yields exactly once, the final
print should show:

```python
done
```

### Meaning

The attached block executes in the caller's environment, not in a fresh function
environment. This is the major semantic difference between a Nomi block and an
ordinary function callback.

This makes block calls feel like structured control flow rather than nested
function definitions.

### Usability Benefit

The programmer can write:

```python
transaction(db):
    user = create_user()
    send_welcome(user)
```

without wrapping the body in a separate function solely to pass it around.

The body reads as normal sequential code, while the callee supplies the control
frame around it.

## Feature 9: Expression-Oriented Growth

Nomi should gradually make more constructs expression-friendly, but not at the
cost of readability.

Candidate direction:

```python
result = retry(3):
    compute()
```

Possible meaning:

- the block call as a whole produces the value returned by the block-control
  function,
- yielded block results can be captured and transformed by the callee,
- failure behavior remains explicit through exceptions or declared alternatives.

This is intentionally left less settled than basic block statements. The
statement form should be designed first because it is easier to read and closer
to Python's current mental model.

## Feature 10: Unified Meaning of Sample Fragments

### Fragment A

```python
is_pos = (x) => x > 0
count:int, is_pos = 3
```

Meaning:

- `is_pos` is a function value.
- `count` is bound to `3`.
- `3` must be an `int`.
- `is_pos(3)` must be true.

### Fragment B

```python
func repeat(n:int, body):
    for i in range(n):
        yield i
```

Meaning:

- `repeat` is a block-control function when used with an attached block.
- `n` must be an `int`.
- every `yield i` invokes the caller block with `i`.

The explicit `body` parameter may not be needed in final syntax. It is included
here only to expose the concept that a block is supplied by the caller.

### Fragment C

```python
repeat(3) -> i:
    print(i)
```

Meaning:

- call `repeat(3)`,
- bind each yielded value to `i`,
- run the indented block once per yielded value.

### Fragment D

```python
func protect(lock):
    lock.acquire()
    try:
        yield
    finally:
        lock.release()

protect(my_lock):
    update_shared_state()
```

Meaning:

- the callee handles resource policy,
- the caller writes the protected work inline,
- cleanup is guaranteed by the control abstraction.

This reads like a context manager but is explained through the same block-yield
mechanism as retry and iteration.

## Open Design Questions

### Block Argument Syntax

Current candidate:

```python
each(items) -> item:
    ...
```

Questions:

- Should `->` always mean values flow from callee to block?
- Should zero-argument blocks omit `->` entirely?
- Should constrained block parameters reuse function parameter syntax exactly?

### Return Values From Blocks

If the caller block computes a value:

```python
measure:
    expensive_call()
```

Questions:

- Does the block implicitly return its last expression?
- Does the callee receive that value as the result of `yield`?
- Should statement blocks and expression blocks be separate forms?

### Exception Boundaries

When the caller block raises an exception, the callee should be able to catch it
around `yield`.

```python
func retry(n):
    for i in range(n):
        try:
            yield
            return
        except NetworkError:
            continue
```

This behavior is essential for retry-like control abstractions. The final design
must make exception ownership understandable from the code's visual structure.

### Name Binding in Blocks

Caller-scope execution is usable, but it raises questions:

- Does assignment inside a block always affect the caller scope?
- Are block parameters local to the block body?
- How do `nonlocal` and `global` interact with block calls?

The usability target is that block bodies behave like ordinary in-place code
unless a binding is explicitly introduced by the block boundary.

## Proposed Design Milestones

### Milestone 1: Stabilize Core Reading

Define the informal semantics of:

- `func`,
- arrow functions,
- constrained assignment,
- constrained parameters.

Success criterion: a Python user can read small Nomi snippets and correctly
explain name binding, validation, and function calls.

### Milestone 2: Stabilize Block Statement Semantics

Define:

- `call(...): block`,
- `call(...) -> names: block`,
- caller-scope execution,
- `yield` to attached block,
- exception flow around `yield`.

Success criterion: retry, resource protection, and simple iteration examples
all share one explanation.

### Milestone 3: Decide Constraint Syntax for Block Parameters

Pick the most readable form for constrained block inputs.

Success criterion: block parameter constraints are readable beside the block
colon and clearly reuse the normal binding model.

### Milestone 4: Explore Expression-Level Block Calls

Only after statement blocks feel stable, explore block calls that produce values
directly inside expressions.

Success criterion: expression block calls improve clarity in real examples and
do not make ordinary control flow harder to scan.

## Non-Goals For This Document

This document does not specify:

- parser grammar,
- AST representation,
- bytecode or interpreter strategy,
- performance model,
- full type system,
- complete exception lifecycle,
- module/package semantics.

Those belong in implementation and specification documents after the user-facing
semantics settle.

## Working Thesis

Nomi's proposed feature set should make Python-like code more semantically
regular without making it feel foreign.

The language should let programmers write ordinary-looking code whose deeper
meaning is cleaner:

- functions are functions,
- bindings may validate,
- parameters are bindings,
- blocks are caller-side code placed into callee-owned control patterns,
- `yield` is the bridge between the two.

If these meanings remain stable, later implementation work can proceed against a
clear semantic target rather than a collection of isolated syntax experiments.
