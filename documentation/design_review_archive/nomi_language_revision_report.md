# Nomi Language Revision Report

> Status: provisional design report.
>
> This document is modeled in spirit after language reports such as the Haskell
> Report, Scheme reports, and the ALGOL 68 report. It is not yet a formal
> specification. It records a coherent proposed revision of Nomi's surface
> language and semantic core so later implementation work has a stable target.

## 0. Scope

This report describes Nomi as a small-core, Python-readable language with a rich
surface syntax. The design emphasizes:

- semantic reducibility,
- local readability,
- explicit binding,
- block-structured control,
- expression orientation where readable,
- symbolic/code-shaped data as an explicit advanced facility.

The report does not define a parser, bytecode format, object layout, package
manager, optimizer, standard library, or foreign function interface.

## 1. Design Thesis

Nomi is organized around a small set of semantic primitives:

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
rewrite
```

Every surface feature admitted into the language should reduce to these
primitives.

The design follows this rule:

> Surface richness is acceptable only when the desugaring path remains obvious.

This lets Nomi borrow ideas from many languages without becoming a patchwork of
unrelated features.

## 2. Notational Conventions

Examples use proposed Nomi syntax. Some syntax is established in the current
prototype, while other syntax is proposed.

Status labels:

- **Core**: intended to be part of the central language.
- **Candidate**: promising, but needs more design pressure.
- **Library-first**: should be expressible through core features before becoming
  syntax.
- **Advanced**: powerful but should remain explicit and scoped.

## 3. Lexical And Layout Structure

### 3.1 Indentation

Nomi uses indentation for block structure.

```python
if ready:
    run()
else:
    wait()
```

Indentation is semantic. This follows Python and the broader off-side rule
tradition.

### 3.2 Comments

Line comments use `#`.

```python
# Load and normalize records.
records = load(path)
```

Block comments are not required in the core. Documentation strings and
editor-supported region comments are preferred.

### 3.3 Identifiers

Identifiers are plain names:

```python
user
total_count
normalize_space
```

The core style favors lowercase names for values/functions and capitalized names
for data constructors/types, but that is a convention rather than a semantic
requirement.

### 3.4 Keywords

Core proposed keywords:

```text
func
if
else
for
in
while
break
continue
return
yield
try
except
finally
raise
match
case
class
import
from
as
const
data
trait
protocol
impl
quote
macro
```

Not all keywords should necessarily enter the first implementation. `data`,
`trait`, `protocol`, `impl`, `quote`, and `macro` may be staged.

## 4. Values

A value is any runtime entity that can be bound to a name, passed to a function,
returned, stored in a structure, or matched by a pattern.

Examples:

```python
1
3.14
"hello"
True
None
[1, 2, 3]
{"name": "Ada"}
Point(2, 3)
(x) => x + 1
```

Functions are values. Data constructors produce values. Quoted expressions
produce expression values.

## 5. Bindings

### 5.1 Simple Binding

```python
x = 1
name = "Ada"
```

Meaning:

```text
evaluate right-hand side
bind resulting value to left-hand name or pattern
```

### 5.2 Constrained Binding

```python
x:int = 1
x:int, x > 0 = 1
```

Meaning:

```text
evaluate right-hand side
tentatively bind value
evaluate constraints in binding context
commit binding if all constraints pass
raise TypeError or BindingError otherwise
```

### 5.3 Constant Binding

```python
const max_retries:int = 3
```

Meaning:

```text
bind max_retries once
reject later rebinding in the same scope
```

Status: candidate core.

### 5.4 Pattern Binding

```python
(x, y) = point
[first, *rest] = items
{"id": id, "name": name} = user
```

Meaning:

```text
match the right-hand value against the left-hand pattern
bind names introduced by the pattern
fail atomically if the pattern does not match
```

## 6. Constraints

Constraints are predicates attached to bindings.

```python
age:(int, age >= 0) = 34
```

A constraint may be:

- a type/class-like value,
- a predicate function,
- an expression evaluated in the binding context.

Examples:

```python
age:int = 34
amount:positive = 10
score: score >= 0 = 5
```

All binding positions may support constraints:

```python
func f(x:(int, x > 0)): ...
for user:User in users: ...
each(users) -> user:User: ...
case User(age:(int, age >= 18)): ...
```

## 7. Functions

### 7.1 Function Definition

```python
func add(x:int, y:int) -> int:
    x + y
```

Meaning:

```text
create function value
bind it to add
on call, bind arguments to parameters
validate parameter constraints
execute body
validate return constraint if present
return result
```

### 7.2 Explicit Return

```python
func add(x, y):
    return x + y
```

`return` exits the current function and supplies a result value.

### 7.3 Final Expression Return

Candidate:

```python
func add(x, y):
    x + y
```

In expression-oriented function bodies, the final expression may be the result.
This should be admitted only if it does not make action-heavy functions
ambiguous.

### 7.4 Arrow Functions

```python
(x) => x + 1
(x:int, y:int) => x + y
```

Arrow functions create function values. They do not introduce a name unless
bound.

```python
inc = (x:int) => x + 1
```

### 7.5 Multi-Line Arrow Functions

Candidate:

```python
score = (user) =>:
    base = user.score
    bonus = user.rank * 10
    base + bonus
```

This desugars to an anonymous block-bodied function.

## 8. Calls

### 8.1 Positional And Keyword Calls

```python
move(point, dx=1, dy=2)
```

Calls map arguments to parameters, then perform parameter binding.

### 8.2 Spread

```python
f(*args, **kwargs)
```

Spread expands values into positional and keyword arguments.

### 8.3 Pipeline Application

Candidate:

```python
result = text |> parse |> normalize |> summarize
```

Desugaring:

```python
summarize(normalize(parse(text)))
```

Placeholder:

```python
result = text |> parse(mode="loose", _)
```

Desugaring:

```python
parse(mode="loose", text)
```

## 9. Blocks

### 9.1 Ordinary Statement Blocks

```python
if ready:
    run()
```

Blocks group statements under a control construct.

### 9.2 Caller-Side Blocks

```python
retry(3):
    send_request()
```

Meaning:

```text
call retry(3) with an attached caller-side block
the callee may invoke the block with yield
```

### 9.3 Block Parameters

```python
each(users) -> user:
    print(user.name)
```

Meaning:

```text
callee yields values
block boundary binds yielded values to user
body executes in caller scope with that binding
```

### 9.4 Constrained Block Parameters

Candidate syntax:

```python
each(users) -> user:User:
    print(user.name)
```

Alternative:

```python
each(users) -> user(User):
    print(user.name)
```

The report records the semantic requirement but does not choose the final
surface form.

### 9.5 Yield To Block

Inside a block-control function:

```python
func each(items):
    for item in items:
        yield item
```

`yield item` invokes the attached block with `item`. Exceptions raised by the
block are visible around the `yield` expression.

## 10. Control

### 10.1 Conditional Statement

```python
if condition:
    consequent()
else:
    alternative()
```

### 10.2 Conditional Expression Block

Candidate:

```python
label = if score >= 90:
    "excellent"
else:
    "ok"
```

The selected branch's final expression becomes the conditional value.

### 10.3 Loops

```python
for item in items:
    print(item)

while ready:
    step()
```

Loop variables are bindings and may be constrained:

```python
for user:User in users:
    print(user.name)
```

### 10.4 Library-Defined Control

Block calls make control abstraction library-definable:

```python
timeout(5):
    fetch(url)

transaction(db):
    save(record)

test "record saves":
    assert save(record).ok
```

These forms reduce to calls with attached blocks.

## 11. Pattern Matching

### 11.1 Match Statement

```python
match value:
    case Point(x, y):
        print(x, y)
    case _:
        print("unknown")
```

### 11.2 Match Expression

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

### 11.3 Guards

```python
match user:
    case User(age) if age >= 18:
        allow()
    case _:
        deny()
```

### 11.4 Constraint Patterns

```python
match user:
    case User(age:(int, age >= 18)):
        allow()
```

Patterns are binding forms with shape checks.

## 12. Data Declarations

Candidate core:

```python
data Point(x:int, y:int)
```

Meaning:

```text
bind constructor Point
define fields x and y
define pattern Point(x, y)
define equality and representation unless overridden
```

Defaults:

```python
data User(id:int, name:str, active:bool = True)
```

Copy/update candidate:

```python
inactive = user with {active = False}
```

## 13. Classes And Objects

Class syntax may remain Python-like:

```python
class Account:
    func deposit(self, amount:(int, amount > 0)):
        self.balance += amount
```

Classes are for identity, mutation, inheritance, or behavior-rich entities.
`data` is preferred for plain structured values.

Extension-style functions are candidate syntax:

```python
func String.words(self):
    self.split()
```

Use:

```python
"hello world".words()
```

Desugaring:

```python
String.words("hello world")
```

under scoped extension lookup.

## 14. Traits And Protocols

Candidate:

```python
trait Drawable:
    func draw(self, canvas)
```

Implementation:

```python
impl Drawable for Circle:
    func draw(self, canvas):
        canvas.circle(self.center, self.radius)
```

Structural protocol:

```python
protocol Reader:
    func read(self, n:int) -> bytes
```

Traits and protocols are named constraint sets over available functions.

## 15. Absence And Failure

### 15.1 None

Nomi may retain Python's `None` as the empty value.

### 15.2 Optional Marker

Candidate:

```python
email:str?
```

Meaning: `email` may be a `str` or empty.

### 15.3 Safe Access

Candidate:

```python
city = user?.address?.city
name = user.name ?: "guest"
```

Desugaring:

```text
if receiver is empty, return empty
otherwise perform access
```

### 15.4 Result Values

Candidate:

```python
config = read_config(path)?
```

Desugaring:

```python
match read_config(path):
    case Ok(value):
        config = value
    case Err(error):
        return Err(error)
```

The `?` operator requires a coherent `Result` model.

## 16. Exceptions

Nomi retains Python-like exceptions:

```python
try:
    work()
except NetworkError as error:
    retry_later(error)
finally:
    cleanup()
```

Expression `try` is candidate syntax:

```python
config = try:
    load_config()
except FileNotFoundError:
    default_config()
```

## 17. Symbolic Expressions

### 17.1 Quote

Advanced:

```python
expr = quote:
    x + 0
```

Meaning: capture syntax as an expression value rather than evaluating it.

Short quote candidate:

```python
expr = '(x + 0)
```

### 17.2 Evaluation

```python
value = eval(expr, env={"x": 3})
```

Evaluation is explicit.

## 18. Rewrite Rules

Advanced:

```python
simplified = expr /. x + 0 -> x
```

Multiple:

```python
simplified = expr /. [
    x + 0 -> x,
    x * 1 -> x,
]
```

Repeated:

```python
normal = expr //. [
    x + 0 -> x,
    x * 1 -> x,
]
```

Meaning:

```text
match expression value against pattern
construct replacement expression
return transformed expression value
```

No unquoted runtime code is rewritten.

## 19. Macros

Advanced and explicit:

```python
macro assert_equal(left, right):
    quote:
        if {left} != {right}:
            raise AssertionError(f"{left} != {right}")
```

Macros are functions from expression values to expression values. Macro use must
be scoped and visible through imports or `use`.

## 20. Modules And Imports

### 20.1 Imports

```python
import math
from pathlib import Path
```

Imports bind names.

### 20.2 Use

Candidate:

```python
use text.extensions.words
use symbolic.algebra.rules as algebra
```

`use` brings capabilities into scope:

- extension functions,
- traits,
- protocols,
- macros,
- rewrite rules.

The purpose is to avoid hidden global mutation.

## 21. Standard Surface Libraries

The language should prefer library-defined block abstractions before adding
keywords.

Examples:

```python
retry(3): ...
timeout(5): ...
transaction(db): ...
test "name": ...
cases(data) -> row: ...
scope() -> task: ...
```

These all reduce to calls and blocks.

## 22. Desugaring Summary

| Surface form | Desugars to |
| --- | --- |
| `func f(x): body` | bind `f` to function value |
| `(x) => expr` | function value returning `expr` |
| `x:T = v` | bind then validate `T` |
| `(x, y) = v` | pattern match then bind |
| `call(args): block` | call with attached caller block |
| `yield v` | invoke attached block with `v` |
| `each(xs) -> x: block` | block call plus yielded-value binding |
| `value |> f` | `f(value)` |
| `f >> g` | `(x) => g(f(x))` |
| `data Point(x, y)` | constructor, fields, pattern shape |
| `user?.name` | guarded access over empty/non-empty value |
| `expr /. rule` | rewrite quoted expression value |
| `quote: body` | expression value, not evaluated code |

## 23. Revision Staging

### Revision 0: Current Prototype Direction

- `func`
- arrow functions
- constrained binding
- constrained parameters
- block calls
- `yield` to block

### Revision 1: Coherent Usability Layer

- pattern binding everywhere
- expression `if` and `match`
- data declarations
- pipelines
- extension functions
- optional/null-safe syntax after absence semantics are settled

### Revision 2: Symbolic And Meta Layer

- `quote`
- rewrite rules
- scoped macros
- tagged syntax blocks
- rule libraries

### Revision 3: Capability And Effect Layer

- traits/protocols
- result propagation
- structured concurrency blocks
- effect constraints if justified by real examples

## 24. Design Risks

### 24.1 Syntax Accumulation

Nomi must avoid collecting syntax because it is attractive in other languages.
Each form needs a clear primitive reduction.

### 24.2 Hidden Control

Block calls and macros can obscure control flow. Nomi should keep block
boundaries visually explicit and macro capabilities import-scoped.

### 24.3 Symbolic Density

APL and Mathematica show the value and danger of dense notation. Nomi should
support symbolic and array-heavy domains while keeping ordinary code readable.

### 24.4 Fragmented Error Semantics

Exceptions, `None`, optional values, and `Result` can conflict. The language
needs a coherent story before adding `?`, `?.`, `?:`, and `str?` together.

## 25. Conformance For Future Implementations

A future implementation conforming to this report should:

1. Preserve the small-core reductions.
2. Provide deterministic binding and constraint behavior.
3. Make block invocation and exception flow around `yield` explicit.
4. Keep symbolic rewriting limited to explicit expression values.
5. Avoid global hidden changes from imports, extensions, macros, or rules.

This conformance definition is intentionally semantic rather than mechanical.

## 26. Concluding Position

Nomi should be rich enough to express modern programming patterns directly, but
small enough that each pattern can be explained by reduction.

The core should remain compact:

```text
values, bindings, constraints, functions, calls, blocks, yield, patterns, quote
```

The surface may grow:

```text
data, traits, protocols, pipelines, rewrite rules, macros, optional syntax,
structured concurrency
```

but every addition must preserve the ability to peel code back to primitives.
That is the central discipline of this revision.
