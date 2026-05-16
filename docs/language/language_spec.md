# Nomi Language Specification

> Status: draft language specification.
>
> This document specifies the intended Nomi language, not the current
> implementation. It is concrete enough to guide syntax examples, parser work,
> diagnostics, documentation, and teaching material. When this document
> conflicts with older design notes, this document wins unless the user or a
> later accepted spec explicitly overrides it.
>
> This document is also a coherence filter. Nomi should not accumulate
> unrelated conveniences from other languages. New syntax is admitted only when
> it reduces to a small normal form that users can recognize elsewhere in the
> language.

## 1. Design Target

Nomi is a general-purpose language for everyday programs that should remain
clear as they grow:

- scripts and automation;
- command-line tools;
- notebooks and exploratory work;
- data cleanup and transformation;
- API and configuration boundaries;
- small services and application logic;
- teaching examples;
- glue code that should still be readable six months later.

Nomi is not designed first around manual memory, advanced concurrency,
metaprogramming, proof systems, or compiler-oriented cleverness. Those may
become later layers, but the base language must be teachable, memorable, and
useful without them.

The design rule is:

```text
few remembered operations, many composable uses
```

The user should recognize the same ideas everywhere:

```text
value
binding
constraint
function
call
data
pattern
match
collection
block
module
example
diagnostic
```

### 1.1 Relation To The Prototype

The Python-hosted prototype is a laboratory for this specification. Some
features below are implemented, some are partially implemented, and some are
forward-looking. The spec should name the intended semantics without pretending
that all of them already exist.

For implementation details — grammar interactions, AST quirks, desugar pass
invariants, source-span wiring, and features that failed or were deferred — see
[Implementation Learnings](../convenience/implementation_learnings.md).

For the extension path (how to add new syntax in the current prototype), see
the [CLAUDE.md](../../CLAUDE.md) section "Adding new syntax" and the
[Feature Manifest Registry](../../prototype/syntax/features.py)
(`BUILTIN_FEATURES`).

Feature status terms:

- **core**: part of the intended first complete language.
- **surface**: convenience syntax that must reduce to core semantics.
- **library-first**: should begin as functions, data values, or block policies.
- **design-needed**: promising, but a key semantic or diagnostic rule is still
  unsettled.
- **future layer**: compatible with the core, but not part of the first
  language users need to learn.
- **research-only**: source material until a normal form and diagnostics are
  clear.

Every implementation commit that accepts new user-facing syntax should update
the runnable teaching examples after tests pass:

```text
samples/demo.nomi
samples/demo_terse.nomi
```

Focused examples may live in additional `samples/*.nomi` files, and web or
notebook tooling may load them from the same sample directory.

### 1.2 Coherence Contracts

Nomi's surface grows by reduction, not collection. The same normal forms should
explain most language features:

| Normal form | Used for | Core reduction |
| --- | --- | --- |
| Binding | assignments, parameters, block parameters, data fields, imports, exception aliases, pattern captures | receive value, tentatively bind, check constraints, commit or diagnose |
| Function | named functions, arrows, equations, implicit holes, operator sections, composition | map parameter bindings to a body and result |
| Pattern | `match`, destructuring, if-let, guard-let, variant cases, structural recognition | test shape, bind captures, check constraints, choose or fail |
| Flow | pipelines, collection transforms, query plans, method chains | value passed through ordinary calls or function values |
| Block | `using`, `retry`, `transaction`, `trace`, fixtures, future capabilities | ordinary call plus attached caller-side code invoked by `yield` |
| Data boundary | constructors, `Data.decode`, config, CLI, JSON, table rows | field bindings plus constraint diagnostics |
| Absence/result | `none`, `?.`, `??`, `Result`, expected failure | absence value or data variant plus pattern matching |
| Explanation | examples, traces, diagnostics, `explain` | source-spanned events with structured context |

If two candidate features reduce to the same row, the spec should prefer one
canonical spelling or document one as an obvious special case of the other.
If a candidate cannot reduce to any row, it remains future or research material.

### 1.3 Surface Convenience Rule

Surface features are welcome when they make common code easier to read and
remember. They must satisfy all of the following:

- They desugar to a named normal form.
- The desugared form can be shown by tooling.
- Diagnostics use the normal-form vocabulary, not the sugar's private terms.
- Similar features share syntax or are explicitly presented as special cases.
- They do not change the meaning of existing core programs.

For example, `if-let`, destructuring assignment, and a constrained match capture
are all pattern/binding forms. They should not have three unrelated failure
models.

## 2. Specification Style

This specification uses normative words:

- **must**: required language behavior;
- **must not**: forbidden language behavior;
- **should**: expected behavior with room for later refinement;
- **may**: allowed behavior.

Code examples in this document are Nomi unless marked otherwise.

Grammar snippets are descriptive rather than a complete parser grammar. A later
grammar document may refine details, but it must preserve the semantics here.

## 3. Program Structure

A Nomi program is a sequence of top-level declarations and executable
statements.

```python
import csv

data Person:
    name:str
    email:str, contains(email, "@")

func load(path:str) -> list[Person]:
    rows = csv.read(path)
    return rows |> map(Person.decode)

people = load("people.csv")
print(len(people))
```

A file is a module. Top-level statements execute in module order when the file
is run as a program. Top-level declarations bind names in the module scope.

The module name is derived from its path unless an optional declaration appears
at the top:

```python
module app.signup
```

## 4. Lexical Structure

### 4.1 Source Text

Source files are Unicode text. UTF-8 is the required interchange encoding.

Newlines separate logical lines except inside open parentheses, brackets, or
braces.

### 4.2 Comments

Line comments begin with `#` and continue to the end of the line.

```python
# normalize before validation
email = raw.email.strip().lower()
```

Documentation comments are ordinary comments immediately preceding a
declaration. Tooling may attach them to the following declaration.

```python
# Return a lowercase, trimmed email address.
func normalize_email(email:str) -> str:
    return email.strip().lower()
```

Cell markers for notebooks and playgrounds are comments, not language syntax:

```python
# %% Load data
rows = read_csv(path)

# %% Transform
clean = rows |> where(_.valid)
```

Tools may use `# %%` to split an editor buffer into cells. A conforming
compiler or interpreter must treat those lines as comments. Running cells in a
persistent session is a tooling behavior, not a different module semantics.

### 4.3 Layout

Indentation is significant. A line ending in `:` begins an indented block.

```python
if age >= 18:
    label = "adult"
else:
    label = "minor"
```

Tabs are not part of the reference style. Conforming tools should reject mixed
tabs and spaces in indentation.

A line may continue after `=`, `return`, `=>`, `|>`, a binary operator, or an
open delimiter. The continued expression must be indented relative to the line
that introduced it.

### 4.4 Identifiers

Identifiers name bindings, functions, modules, data constructors, fields, and
type parameters.

Reference style:

```text
lower_snake_case      value, function, module, field
UpperCamelCase       data type, variant constructor, type parameter
_leading_underscore  private or intentionally local convention
_                   wildcard pattern or placeholder
```

The style is not merely aesthetic. In patterns, bare lowercase identifiers bind
new names, while uppercase identifiers are resolved as constructors or named
constants.

### 4.5 Keywords

Reserved keywords:

```text
and as break by case const continue data elif else examples except false finally
for from func guard if import in is match module none not or raise return true
try unless when while yield export
```

Future-reserved keywords:

```text
capability computation effect extend impl interface protocol quote shape trait
use world
```

Future-reserved words are not active syntax in the everyday language.

## 5. Values

Every expression evaluates to a value or raises an error.

Core value categories:

- numbers;
- booleans;
- strings;
- absence;
- tuples;
- lists;
- dictionaries;
- functions;
- data values;
- modules;
- errors.

### 5.1 Literals

```python
42
3.14
true
false
none
"hello"
'hello'
[1, 2, 3]
(1, 2)
{"name": "Ada", "age": 36}
```

`true`, `false`, and `none` are the canonical literals. Compatibility layers
may accept `True`, `False`, and `None`, but this specification uses lowercase.

### 5.2 Equality And Identity

`==` compares values for semantic equality.

`is` compares identity. It should be used only when identity matters.

Data values compare by constructor and field values unless a later spec
declares a different equality policy.

### 5.3 Truth

Conditions require a boolean value.

Nomi must not use Python-style broad truthiness for ordinary conditions in the
core language. If a program wants to test emptiness, it should say so:

```python
if len(items) > 0:
    ...
```

This avoids accidental branching on numbers, strings, lists, or `none`.

## 6. Bindings And Scope

A binding connects a value to a name or pattern target in a scope.

```python
name = "Ada"
age:int = raw_age
email:str, contains(email, "@") = raw_email
```

Scopes:

- module scope;
- function scope;
- block scope;
- match-case scope;
- comprehension or collection-transform scope.

Names are resolved lexically. Inner scopes may shadow outer bindings.

### 6.1 Rebinding

Bindings may be rebound in the same mutable local scope:

```python
count:int, count >= 0 = 0
count = count + 1
```

Rebinding without a new annotation keeps the active constraints for that
binding. Rebinding with a new annotation replaces that binding's constraint set
in the current scope.

```python
value:int = 1
value = 2       # checked as int
value:str = "2" # new local constraint set
```

### 6.2 Constants

`const` introduces a binding that may not be rebound in the same scope.

```python
const pi:float = 3.14159
```

Attempting to rebind a constant raises `BindingError`.

### 6.3 Assignment Targets

Assignment targets may be:

- a name;
- a tuple or list pattern;
- a data pattern;
- a mapping pattern;
- a field target when the receiver is explicitly mutable.

The everyday language does not include mutable data fields. Field assignment is
reserved for explicit mutable library types and must not be confused with
ordinary data values.

### 6.4 Declarations Without Values

A binding may declare constraints before a value is assigned:

```python
port:int, port > 0, port < 65536
port = config.port
```

This is a binding contract in the current scope. Later assignment to `port`
must satisfy the active constraints. A declaration without a value does not
create a usable runtime value; reading it before assignment raises
`BindingError` or `NameError` with a diagnostic that points to the declaration.

Declaration-before-assignment is useful for module boundaries, mutually
referenced setup, and teaching constraints. It should not become a second type
system: it is still the same binding normal form.

## 7. Constraints

A constraint is an executable judgement over a tentative binding.

```python
age:int, age >= 13 else "Must be at least 13" = raw_age
```

Binding proceeds as:

```text
evaluate right side once
tentatively bind target names
check constraints in the tentative environment
commit bindings if all checks pass
raise BindingError if any check fails
```

### 7.1 Constraint Forms

Type or class constraint:

```python
age:int = value
```

Predicate constraint:

```python
email:str, contains(email, "@") = value
```

Expression constraint:

```python
amount:int, amount > 0 = value
```

Message constraint:

```python
age:int, age >= 13 else "Must be at least 13" = value
```

Multiple constraints are evaluated from left to right.

### 7.2 Constraint Names

Built-in constraint names:

```text
Any bool int float str list dict tuple function data module error
```

Parameterized constraints:

```python
list[int]
dict[str, int]
Result[User, SignupError]
```

The language treats type annotations as constraints first. Static tooling may
use them for analysis, but runtime semantics must not depend on a full static
type checker.

### 7.3 Constraint Composition

Constraint lists are conjunctions evaluated left to right:

```python
age:int, age >= 13, age < 130 = raw_age
```

The first failing constraint determines the primary diagnostic. Tooling may
show later constraints as unevaluated. A constraint may refer to names already
in scope and to tentative names introduced by the current binding target.

Equivalent validation surfaces should normalize to the same representation:

```python
data User:
    email:str, contains(email, "@")

func signup(email:(str, contains(email, "@"))):
    ...

match raw:
    case {"email": email:(str, contains(email, "@"))}:
        ...
```

All three examples express "bind `email`, then check the same constraints".
They differ in where the value arrives, not in the validation model.

### 7.4 Constraint Failure

Constraint failure raises `BindingError`.

Minimum diagnostic fields:

```text
name
value
constraint
message
source_span
binding_kind
```

Example:

```text
BindingError: age failed constraint age >= 13
  value: 12
  binding: parameter age in signup(...)
  note: Must be at least 13
```

## 8. Expressions

Expressions produce values.

Expression categories:

- literals;
- names;
- calls;
- field access;
- indexing;
- operators;
- `if` expressions;
- `match` expressions;
- collection literals;
- arrow functions;
- parenthesized expressions;
- pipelines.

Expression-oriented syntax should still leave evaluation order inspectable.
When a convenience expression is accepted, it must say whether it is eager,
lazy, short-circuiting, value-producing, or control-producing.

### 8.1 Operators

Core operators:

```text
or
and
not
== != < <= > >=
is
in
|>
+ -
* / // %
**
.
[]
()
```

`and` and `or` short-circuit and require boolean operands.

The pipeline operator `|>` passes the value on its left into the call or
function expression on its right:

```python
clean =
    raw
    |> strip
    |> lower
    |> normalize_space
```

Reduction:

```text
raw |> f      == f(raw)
raw |> f(a)   == f(raw, a)
```

If the right side contains `_`, the piped value replaces `_`:

```python
numbers |> map(_ * 2)
```

Pipeline is immediate application. Function composition is a different surface:
it builds a function value for later use.

```python
normalize = strip >> lower >> normalize_space
clean = raw |> normalize
```

The reference composition operator is `>>` for left-to-right composition.
Compatibility layers may accept prototype spellings such as `>>>` or `<<<`,
but teaching material should converge on one ordinary direction:

```text
f >> g  ==  (x) => g(f(x))
```

Do not introduce a separate method-chain or query-chain execution model.
Method calls, pipelines, collection verbs, and query plans must all reduce to
ordinary call or flow normal forms.

### 8.2 Field Access And Indexing

```python
user.email
items[0]
mapping["key"]
```

Field access on data values reads a declared field. Missing fields raise
`FieldError`.

Indexing behavior is defined by the receiver's type.

### 8.3 Conditional Expressions

`if` may be used as a statement or as a value-producing expression.

```python
label =
    if age >= 18:
        "adult"
    else:
        "minor"
```

All branches of a value-producing `if` must produce a value. Conditions must be
boolean.

### 8.4 Block Values

Some blocks are value-producing: `if` expressions, `match` expressions, and
caller-side blocks invoked by `yield`.

The value of a value-producing block is the value of its last expression.
Assignments, declarations, and loop statements produce `none`. A block used in
a value position must end with an expression or an explicit `return` from the
enclosing function.

### 8.5 Absence-Aware Expressions

Absence-aware access is sugar for checking `none` before continuing.

```python
name = user?.profile?.name ?? "anonymous"
```

Semantics:

```text
receiver?.field     returns none if receiver is none, otherwise receiver.field
receiver?.[index]   returns none if receiver is none, otherwise receiver[index]
receiver?.call(...) returns none if receiver is none, otherwise receiver.call(...)
left ?? fallback    returns left unless left is none, otherwise fallback
```

These operators are only about absence. They must not catch exceptions, consume
`Err` values, or hide failed constraints. Expected failure belongs to `Result`
and pattern matching; unexpected failure belongs to errors.

### 8.6 Try Expressions And Propagation

`try` may be used as a statement and may later be admitted as a value-producing
expression:

```python
safe_age = try int(raw_age) except: 0
```

The normal form is an expression boundary with explicit recovery. A future
result-propagation operator such as `?` is allowed only if it desugars to
`Result` matching plus an explicit return or block-policy rule:

```python
age = parse_int(raw_age)?
```

Potential reduction:

```text
match parse_int(raw_age):
    case Ok(value): value
    case Err(error): return Err(error)
```

The exact propagation target must be specified before this becomes core syntax.
It is **design-needed**, not first-layer core.

## 9. Functions And Calls

### 9.1 Function Declarations

```python
func name(parameter_list) -> return_constraint:
    body
```

Example:

```python
func add(x:int, y:int) -> int:
    return x + y
```

`return` exits the current function. A function with no explicit return returns
`none`.

### 9.2 Parameters

Parameters are bindings.

```python
func signup(
    email:(str, contains(email, "@")),
    age:(int, age >= 13),
    plan:Plan = Plan.Free,
) -> SignupInput:
    return SignupInput(email=email, age=age, plan=plan)
```

Parameter kinds:

- positional or keyword;
- keyword-only after `*`;
- variadic positional `*items`;
- variadic keyword `**options`;
- defaulted parameters.

After arguments are mapped to parameters, each parameter binding is validated.

### 9.3 Arrow Functions

Arrow functions are expression-level function values.

```python
double = (x:int) => x * 2
is_adult = (age:(int, age >= 18)) => true
```

Arrow functions contain one expression. Use `func` for named or block-bodied
functions.

### 9.4 Implicit Functions And Holes

Small transformations may use hole syntax as surface sugar for arrow
functions:

```python
double = _ * 2
add = $1 + $2
field = $.name
```

Reduction:

```text
_ * 2      == (value) => value * 2
$1 + $2    == (a, b) => a + b
$.name     == (value) => value.name
```

Use holes only when the generated parameters are obvious from the expression.
If constraints, names, defaults, or more than a tiny expression would improve
readability, use `=>` or `func`.

Operator sections are the same feature family:

```python
increment = (+ 1)
less_than_ten = (< 10)
```

They reduce to ordinary functions. They are surface convenience, not a separate
operator model.

### 9.5 Equation And Piecewise Function Surface

Equation-style definitions may be accepted as a compact function surface:

```python
fact(0) = 1
fact(n:int, n > 0) = n * fact(n - 1)
```

This reduces to a function with pattern and constraint dispatch over
parameters. Cases are tried in order, and failed parameter constraints skip the
case before the body runs.

Guarded equations are the same idea:

```python
sign(n) when n > 0 = 1
sign(n) when n < 0 = -1
sign(n) = 0
```

The canonical long form remains `func` plus `match` or `if`. Equation syntax is
surface-level and should be taught after functions and patterns, not before
them.

### 9.6 Calls

```python
add(1, 2)
send(email=user.email)
```

Calls evaluate the callee, evaluate arguments left to right, map arguments to
parameters, validate parameter constraints, execute the body, and return the
result.

Unknown arguments, duplicate arguments, missing required arguments, and wrong
arity raise `CallError`.

## 10. Data Declarations

`data` defines program-owned values.

### 10.1 Product Data

Single-line form:

```python
data User(id:UserId, email:Email, plan:Plan)
```

Block form:

```python
data User:
    id:UserId
    email:Email
    plan:Plan = Plan.Free
```

Constructor:

```python
user = User(id=id, email=email)
```

Data fields are read-only in the everyday language.

### 10.2 Field Constraints

Fields are bindings checked by the constructor.

```python
data Person:
    name:str
    email:str, contains(email, "@") else "Invalid email"
    age:int, age >= 0
```

Construction fails with `BindingError` or `ConstructionError` containing the
field path.

### 10.3 Sum Data

```python
data Result[T, E]:
    Ok(value:T)
    Err(error:E)
```

`Ok` and `Err` are constructors and patterns.

```python
result = Ok(user)

match result:
    case Ok(user):
        user.name
    case Err(error):
        explain(error)
```

### 10.4 Data Conversion From External Values

Raw external structure does not silently become domain data.

`DataName.decode(value)` is the standard explicit decoder for data declarations.

```python
signup_input = SignupInput.decode(raw)
```

Default decoder policy:

- mapping keys correspond to field names;
- missing required fields fail;
- unknown fields fail;
- defaults are applied after required fields are checked;
- field constraints are checked exactly as constructor constraints;
- errors include the field path.

Lenient decoding is a library concern and must be explicit.

Decode is the normal form for JSON, forms, environment variables, CLI args,
CSV rows, TOML/YAML files, and table rows. These inputs may have different
source formats, but they should share one boundary story:

```python
data SignupInput:
    email:str, contains(email, "@")
    age:int, age >= 13 else "Must be at least 13"
    plan:Plan = Plan.Free

input = SignupInput.decode(request.json)
```

Configuration layering should begin as library or block-policy code that
produces a mapping for `decode`, not as a parallel schema language:

```python
config = AppConfig.decode:
    defaults {"port": 8080}
    file "app.toml"
    env prefix="APP_"
    args cli_args
```

This block-style decode surface is future syntax. Its required reduction is:
collect source values with provenance, merge by an explicit policy, then run
ordinary field binding and constraints.

A future `shape` feature may be admitted only as a named structural
pattern/constraint for values the program does not own. It must not duplicate
`data` constructors, field rules, or decode diagnostics.

### 10.5 Display

Data values display as constructor calls:

```text
User(id=42, email="a@b.com", plan=Free)
```

Display should be stable enough for diagnostics and examples, but it is not a
serialization format.

## 11. Patterns And Match

Patterns test structure and bind names.

### 11.1 Pattern Forms

Wildcard:

```python
_
```

Literal:

```python
42
"ok"
true
none
```

Capture:

```python
name
name:int
name:(int, name >= 0)
```

Tuple or list:

```python
(x, y)
[first, *rest]
```

Mapping:

```python
{"email": email:str, "age": age:(int, age >= 13)}
```

Data constructor:

```python
User(id=id, email=email)
Ok(value)
Err(error)
```

Alternative:

```python
Ok(value) | Err(value)
```

All alternatives in one alternative pattern must bind the same names with
compatible constraints.

Guard:

```python
case User(age=age) if age >= 18:
    ...
```

### 11.2 Match

```python
match value:
    case pattern:
        body
    case pattern if guard:
        body
    else:
        body
```

Cases are tried in order. The first case whose pattern and guard succeed is
selected.

If no case matches and no `else` exists, `MatchError` is raised.

`match` may produce a value:

```python
message =
    match result:
        case Ok(user):
            "hello " + user.name
        case Err(error):
            explain(error)
```

All selected value-producing case bodies must produce a value.

### 11.3 Pattern Failure Versus Constraint Failure

In `match`, pattern failure means the case is skipped.

Constraint failure during tentative case binding also skips the case before the
body starts.

In direct destructuring assignment, failure raises `PatternError` or
`BindingError`.

### 11.4 Pattern Conveniences

Pattern conveniences are special cases of `match` plus binding.

If-let:

```python
if Ok(user) = fetch_user(id):
    send(user.email)
else:
    log("missing user")
```

Reduction:

```python
match fetch_user(id):
    case Ok(user):
        send(user.email)
    else:
        log("missing user")
```

Guard-let:

```python
guard Ok(user) = fetch_user(id):
    return Err("missing user")
```

The guard body runs on pattern failure and normally exits the current function,
block, or policy. It is a convenience for early boundary checks, not a new
kind of exception.

While-let:

```python
while [head, *tail] = items:
    process(head)
    items = tail
```

The pattern is re-evaluated before each loop iteration. Captures are scoped to
the loop body.

These surfaces are useful because they make everyday checks short. They remain
coherent only if their diagnostics mention the same pattern and binding events
that a `match` would have produced.

## 12. Collections And Repetition

### 12.1 Loops

```python
for item in items:
    print(item)
```

```python
while remaining > 0:
    remaining = remaining - 1
```

`break` exits the nearest loop. `continue` begins the next iteration.

Loop variables are bindings in the loop body scope.

### 12.2 Collection Transforms

The standard transform vocabulary:

```text
map
where
select
derive
fold
scan
group
summarize
join
sort
take
drop
count
any
all
window
reshape
```

Examples:

```python
names =
    users
    |> where(_.active)
    |> select(_.name)
    |> sort
```

```python
total =
    orders
    |> select(_.amount)
    |> fold(0, (sum, amount) => sum + amount)
```

Collection operations are library functions with ordinary call semantics. The
pipeline is syntax for readable value flow, not a separate query language.

### 12.3 Comprehensions

List comprehensions are permitted as sugar over transforms:

```python
names = [user.name for user in users if user.active]
```

They reduce to `where` plus `select`.

### 12.4 Tables, Queries, And Plans

Tables, rows, columns, groups, windows, and query plans are future core-adjacent
values. They should reuse the same transform vocabulary rather than embedding
SQL strings or copying a dataframe method catalog.

Candidate surface:

```python
active =
    users
    |> where(_.active)
    |> select({"name": _.name, "email": _.email})
    |> sort(_.name)
```

Grouped candidate:

```python
revenue =
    orders
    |> group(_.customer_id)
    |> summarize({
        total: sum(_.amount),
        count: count(),
    })
```

The required normal form is an inspectable flow of transforms. A collection may
execute eagerly, lazily, or through a backend, but the user-facing semantics are
the same:

```text
input collection -> transform value or query plan -> result collection
```

Backends may expose `explain(plan)` to show schema, logical plan, optimization,
and execution diagnostics. Backend-specific acceleration must not change
binding, pattern, or constraint semantics.

### 12.5 Arrays And Shape

Array-language ideas such as rank, axis, shape, reduce, scan, key/group, and
whole-array mapping are valuable future pressure. Nomi should admit them with
readable names first:

```python
matrix |> shape
matrix |> map_axis(0, sum)
values |> scan(0, (total, value) => total + value)
```

Dense symbolic notation is research-only until the readable vocabulary proves
itself and can be shown as a normal-form reduction.

## 13. Blocks And Yield

A block is caller-side code attached to a call.

```python
retry(3, on=NetworkError):
    send(request)
```

Block with yielded value:

```python
using(open(path)) -> file:
    text = file.read()
```

Block parameters are binding targets:

```python
each(users) -> user:User:
    send(user.email)
```

The function name owns the policy. `retry`, `using`, `transaction`, `timeout`,
`test`, and `trace` are ordinary functions or prelude policies that receive a
block; they are not separate control keywords in the core.

### 13.1 Callee Semantics

A function invokes its attached block with `yield`.

```python
func each(items):
    for item in items:
        yield item
```

`yield value` invokes the attached block, binds yielded values to the block
parameter target, executes the block body in the caller lexical environment,
and returns the block result to the callee.

Calling `yield` when no block is attached raises `BlockError`.

### 13.2 Block Result

The value of a block body is the value of its last expression, or `none` if it
does not produce a value.

```python
func twice():
    a = yield
    b = yield
    return [a, b]

values = twice():
    now()
```

### 13.3 Control Boundaries

`return` inside a block returns from the nearest lexically enclosing `func`, not
from the callee that yielded to the block.

Nonlocal block returns may be restricted by a later spec if they make
diagnostics unclear. Implementations must report them explicitly if supported.

### 13.4 Policy Blocks

Policy blocks are the intended home for many conveniences that other languages
spell as keywords, decorators, context managers, fixtures, callbacks, or
effect handlers.

Examples:

```python
using(open(path)) -> file:
    text = file.read()

retry(3, on=NetworkError):
    fetch(url)

transaction(db) -> tx:
    tx.insert(user)

trace("import users"):
    users = read_users(path)
```

Each example is an ordinary call with an attached block. The callee decides
when to enter, repeat, cancel, or clean up the block. The caller writes the
body in the surrounding lexical context.

Future capability or effect systems should start here:

```python
with_capability(fs.read("config")):
    config = AppConfig.decode(read_text("config/app.toml"))
```

That surface is a **future layer**. The core requirement is that a policy can
explain which block it invoked, with what yielded values, under what authority,
and why it retried, failed, or cleaned up.

## 14. Errors

Expected alternatives should usually be modeled with data:

```python
data Result[T, E]:
    Ok(value:T)
    Err(error:E)
```

Unexpected or exceptional failures use errors.

Expected failure and unexpected failure must stay distinct:

| Situation | Preferred model |
| --- | --- |
| missing optional value | `none` or `Option[T]` |
| parse/decode can fail as part of normal flow | `Result[T, E]` |
| input violates a declared boundary | `BindingError` or `DecodeError` |
| program cannot continue normally | `raise Error(...)` |

This distinction keeps `?.`, `??`, `Result`, `try`, `raise`, and future `?`
propagation from collapsing into one confusing mechanism.

### 14.1 Raising

```python
raise Error("missing file")
```

### 14.2 Handling

```python
try:
    user = load_user(id)
except NotFound as error:
    return Err(error)
finally:
    cleanup()
```

`except` clauses are tried in order. The exception alias is a binding.

### 14.3 Result Values

`Result[T, E]` is the standard expected-failure data shape:

```python
data Result[T, E]:
    Ok(value:T)
    Err(error:E)
```

Use `match` for explicit handling:

```python
match parse_int(raw):
    case Ok(age):
        signup(age)
    case Err(error):
        explain(error)
```

APIs should prefer `Result` when failure is routine and recoverable. They
should raise errors when failure is exceptional, unrecoverable at the call
site, or caused by a broken language boundary.

### 14.4 Standard Error Categories

```text
Error
BindingError
BlockError
CallError
ConstructionError
DecodeError
FieldError
IndexError
MatchError
ModuleError
NameError
PatternError
PipelineError
```

All errors should carry message, source span when available, and structured
context.

## 15. Examples

`examples:` attaches executable examples to a declaration.

```python
func normalize_email(email:str) -> str:
    examples:
        " A@B.COM " => "a@b.com"
    return email.strip().lower()
```

An example has input expression on the left and expected output expression on
the right.

For multi-argument functions:

```python
func add(x:int, y:int) -> int:
    examples:
        (2, 3) => 5
    return x + y
```

Examples are:

- documentation;
- runnable tests;
- diagnostic anchors;
- optional runtime metadata.

Example failure must report the example span, evaluated input, expected output,
and actual output.

## 16. Modules And Imports

### 16.1 Module Declarations

```python
module app.signup
```

The declaration, if present, must be first except for comments.

### 16.2 Imports

```python
import csv
import app.users as users
from app.email import normalize_email, Email
```

Imports bind module values or exported names in the current module scope.

### 16.3 Exports

Top-level names are exported unless they begin with `_`.

Explicit export lists may restrict exports:

```python
export User, signup
```

If an `export` declaration appears, only listed names are exported.

## 17. Methods And Member Calls

The everyday core does not include classes or inheritance.

Data plus functions is the primary modeling style:

```python
data User:
    name:str
    email:Email

func display_name(user:User) -> str:
    return user.name
```

Member calls are permitted only when a function is explicitly exported as a
member by the data declaration or standard library.

```python
data User:
    name:str
    email:Email

    func display_name(self) -> str:
        return self.name

user.display_name()
```

This is sugar for a function whose first parameter is `self`. There is no
implicit inheritance, monkey patching, hidden receiver scope, or global method
mutation in the core language.

## 18. Standard Prelude

The standard prelude is automatically available.

Required names:

```text
true false none
Any bool int float str list dict tuple function
print len range
contains
map where select derive fold scan group summarize join sort take drop count any all
window reshape
using retry timeout transaction test trace
Result Ok Err Option Some NoneValue
Error BindingError CallError ConstructionError DecodeError FieldError
IndexError MatchError ModuleError NameError PatternError BlockError
PipelineError
explain
```

`none` is the absence value. `NoneValue` is the optional-data variant used when
the program wants absence as explicit data rather than an ambient value.

```python
data Option[T]:
    Some(value:T)
    NoneValue()
```

## 19. Diagnostics, Trace, And Explain

Diagnostics are part of the language contract. They are how the small normal
forms stay visible after syntax grows.

Every diagnostic should include, when available:

```text
source span
normal form involved
surface syntax involved
value or structure being processed
binding target, pattern, call, block, or transform name
failed constraint or selected case
suggested next action when clear
```

Examples:

```text
BindingError: age failed constraint age >= 13
  at signup.nomi:12:17
  binding: parameter age in signup(...)
  value: 12
  note: Must be at least 13
```

```text
PipelineError: stage 3 failed in users |> where(...) |> select(...)
  stage: select(_.email)
  input: User(name="Ada", email=none)
  cause: FieldError: email is none
```

`explain(value_or_event)` is the user-facing entry point for structured
explanation. Implementations may start with formatted text, but the target is a
structured explanation value that tools can render.

Traceable events:

- binding and constraint checks;
- function argument mapping;
- data construction and decode;
- pattern attempts and selected cases;
- pipeline and collection transform stages;
- block entry, yield, resume, retry, cleanup, and cancellation;
- example execution;
- future query plans, symbolic rewrites, and capability use.

## 20. Grammar Summary

This grammar is a guide for the concrete surface.

```text
program       ::= module_decl? statement*
module_decl   ::= "module" module_name newline

statement     ::= declaration
                | assignment
                | binding_decl
                | const_decl
                | equation_decl
                | if_stmt
                | match_stmt
                | for_stmt
                | while_stmt
                | try_stmt
                | return_stmt
                | raise_stmt
                | break_stmt
                | continue_stmt
                | block_call
                | expr_stmt

declaration   ::= import_decl | export_decl | data_decl | func_decl

assignment    ::= target constraint_list? "=" expression
binding_decl  ::= target constraint_list
const_decl    ::= "const" identifier constraint_list? "=" expression
target        ::= identifier | pattern

constraint_list ::= ":" constraint ("," constraint)*
constraint    ::= type_expr | expression ("else" string)?

func_decl     ::= "func" identifier "(" params? ")" return_decl? ":" block
equation_decl ::= identifier "(" patterns? ")" guard? "=" expression
return_decl   ::= "->" constraint
params        ::= param ("," param)* ","?
param         ::= identifier constraint_list? default?
default       ::= "=" expression

data_decl     ::= "data" identifier type_params? data_body
data_body     ::= "(" fields? ")" | ":" indented_data_members
data_member   ::= field | variant | func_decl
field         ::= identifier constraint_list? default?
variant       ::= identifier "(" fields? ")"

expression    ::= literal
                | identifier
                | call
                | field_access
                | index
                | operator_expr
                | if_expr
                | match_expr
                | arrow_func
                | hole_expr
                | collection_literal
                | pipeline_expr
                | composition_expr
                | try_expr

pattern       ::= "_"
                | literal
                | capture_pattern
                | tuple_pattern
                | list_pattern
                | mapping_pattern
                | constructor_pattern
                | pattern "|" pattern

block_call    ::= call block_params? ":" block
block_params  ::= "->" target
```

## 21. Out Of Scope For The Core Spec

The following are intentionally excluded from the first core:

- class inheritance;
- mutable data fields by default;
- implicit conversions;
- global monkey patching;
- operator overloading by user code;
- macro systems;
- custom syntax extensions;
- async/await;
- threads and multiprocessing;
- manual memory management;
- dependent types;
- full type inference requirements.

Later specs may add some of these as layers. They must not change the meaning
of existing core programs.

Future-layer candidates that are intentionally compatible with the core:

- symbolic quotation and rewrite via explicit `quote:` boundaries;
- inspectable computation descriptions and backend lowering;
- table/query plans beyond ordinary collection transforms;
- capability and effect typing;
- structured concurrency through block policies;
- scoped notation with `use`, where tooling can show desugaring;
- named structural `shape` contracts, if they remain a data-boundary form.

Rejected for the first core:

- implicit conversions at binding boundaries;
- schema/config languages separate from `data` and `decode`;
- one keyword per control policy;
- global syntax mutation;
- user-defined operator precedence in ordinary modules;
- broad truthiness for conditions.

## 22. Design Reference Documents

### Internal design docs (Nomi's own design spine)

These are the active documents that feed this spec. When this spec is silent on
a design question, these are where the rationale lives:

- [Language Foundation](language_foundation.md) — canonical design entry point, coherence contracts, milestones
- [Spec Readiness Map](spec_readiness_map.md) — promotion map from research and feature docs into spec-ready sections
- [Language Design Dimensions](language_design_dimensions.md) — irreducible axes of variation, convergence points
- [Language Degrees Of Freedom](language_degrees_of_freedom.md) — core/sugar/library/scoped/rejected ladder
- [Design Lessons and Integration](../convenience/design_lessons_and_integration.md) — systemic cruft patterns, feature interactions, designer quotes, synthesis methodology
- [Syntax Design Rules](../convenience/syntax_design_rules.md) — concrete syntax-design rules with nuance and conflict resolution
- [Syntax Synthesis Matrix](../convenience/syntax_synthesis_matrix.md) — cross-language feature families and Nomi recommendations
- [Implementation Learnings](../convenience/implementation_learnings.md) — grammar interactions, AST bugs, deferred features
- [Language Direction And Gap Map](language_direction_and_gap_map.md) — adoption-facing gaps and docs consolidation policy
- [Docs Eagle Eye Review](docs_eagle_eye_review.md) — active bridge-gap review for future spec quality

### External language references

This spec learned document shape and design pressure from these references. They
are not Nomi's authority; they are comparison points.

- Scheme R7RS: https://r7rs.org/
- Haskell 2010 Language Report: https://www.haskell.org/onlinereport/haskell2010/
- ALGOL 60 Revised Report: https://archive.computerhistory.org/resources/text/algol/algol_bulletin/EX/RR60/INDEX.HTM
- Python Language Reference: https://docs.python.org/3/reference/
- Kotlin Language Specification: https://kotlinlang.org/spec/kotlin-spec.html
- Ruby Syntax Reference: https://docs.ruby-lang.org/en/master/syntax_rdoc.html
- Scala 3 Reference: https://docs.scala-lang.org/scala3/reference/
- Racket contracts and blame: https://docs.racket-lang.org/guide/contracts.html
- Gleam language tour: https://tour.gleam.run/
- Roc language examples: https://www.roc-lang.org/examples
- Zig language reference: https://ziglang.org/documentation/master/
- CUE language reference: https://cuelang.org/docs/reference/spec/
- Polars lazy API concepts: https://docs.pola.rs/user-guide/concepts/lazy-api/
- DuckDB friendly SQL: https://duckdb.org/docs/stable/sql/dialect/friendly_sql
- JAX jaxpr and tracing: https://docs.jax.dev/en/latest/jaxpr.html

## 23. Conformance

A conforming Nomi implementation must:

- parse the lexical structure and block layout described here;
- implement the core values and literals;
- implement lexical binding and scope;
- validate constraints at binding boundaries;
- implement functions, calls, and arrow functions;
- implement product and sum `data`;
- implement explicit data decoding through `DataName.decode`;
- implement patterns and `match`;
- implement loops and collection transform calls;
- implement block calls and `yield`;
- implement structured errors;
- attach examples to declarations and provide a way to run them;
- provide the standard prelude;
- produce diagnostics with source spans where source is available.

An implementation may omit future-reserved features. It must not accept syntax
whose meaning conflicts with this specification.
