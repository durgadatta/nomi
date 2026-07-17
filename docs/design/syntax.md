# Nomi Syntax

> Status: canonical target syntax.
>
> This is a syntax contract for the aspirational language. Examples are not a
> promise that the current prototype parses or runs them.

## Visual Character

Nomi uses UTF-8 source, indentation-delimited blocks, four-space canonical
indentation, and newline-oriented statements. The formatter owns whitespace;
semantic meaning never depends on alignment beyond block indentation.

Names use `snake_case`. Types and data variants use `UpperCamelCase`.
Comments begin with `#`. Public declarations begin with `pub`.

```nomi
pub data User:
    id: UserId
    display_name: Text

pub func greet(user: User) -> Text:
    return "Hello, {user.display_name}"
```

The visual target is familiar without being Python-compatible by obligation.

## Line Continuation

A newline ends a statement unless the expression or declaration is visibly
incomplete. Continuation is allowed:

- inside `()`, `[]`, or `{}`;
- after `=`, `=>`, a comma, or an infix operator;
- on a more-indented line beginning with `.` or `|>`;
- before a declaration's final `uses` clause and `:`.

```nomi
result = source
    |> filter((item) => item.ready)
    |> map((item) => item.value)

resource = files.open(path, mode="read")
    .map_error(AppError.Input)?
```

Only a final `:` opens a block. Continuation indentation never creates a
scope, and Nomi has no backslash continuation. The formatter chooses the
canonical breaks and indents continuation lines one level beyond their owner.

## Literals

```nomi
42
3.14
true
false
none
()
"ordinary text"
"Hello, {user.name}"
r"raw text: {not_interpolated}"
b"bytes"
"""multiline text"""
[1, 2, 3]
{"name": "Ada", "active": true}
(10, 20)
```

Double-quoted text interpolates braces. `{{` and `}}` produce literal braces.
Raw text disables escapes and interpolation. There is no parallel `f"..."`
family.

Decimal digit separators use one `_` between digits; they may not lead,
trail, or repeat. Ignoring an optional sign, a decimal integer is `0` or starts
with `1` through `9`, so padded leading zeros are not accepted. Literal
decoding is one language-owned contract shared by expressions, patterns,
schemas, and every parser frontend.

The core scalar type names are `Bool`, `Int`, `Float`, `Decimal`, `Text`,
`Bytes`, and `Unit`. `()` is the sole `Unit` value; it means successful
completion without a payload. It is distinct from `none`, which means absence
inside `Option`. Collection types are `List[T]`, `Map[K, V]`, `Set[T]`, and
tuples such as `(Int, Text)`.

## Bindings And Mutation

An ordinary assignment creates a new immutable lexical binding:

```nomi
name = "Ada"
port: Int = 8080
```

Mutation requires both a mutable declaration and a visible update:

```nomi
var attempts = 0
set attempts = attempts + 1
```

Reusing `=` for rebinding is an error. This keeps a reader from having to
search the scope to learn whether a line creates meaning or changes history.

Destructuring uses the same binding rule:

```nomi
(first, second) = point.as_tuple()
UserId(raw) = known_user_id
```

A destructuring binding must be statically irrefutable for the source type.
Tuple and single-case product decomposition qualify; a list head, literal, or
one case of a multi-variant type does not. Refutable structural choice uses an
exhaustive `match`, so ordinary binding never hides a pattern-failure path.

## Constraints

`where` has one source-language role: attach an executable constraint to a
binding. The bound name is available in its own constraint.

```nomi
age: Int where age >= 0 = raw_age
port: Int where 1 <= port and port <= 65535 = raw_port
```

A short human note may follow the predicate:

```nomi
age: Int where age >= 13 note "account holders must be at least 13" = raw_age
```

The same shape appears on parameters and fields:

```nomi
func reserve(count: Int where count > 0) -> Reservation:
    return Reservation(count=count)

data Range:
    lower: Int
    upper: Int where upper >= lower
```

Declaration-level constraints can refer to several fields:

```nomi
data Window:
    starts_at: Instant
    ends_at: Instant
    where ends_at > starts_at note "a window must end after it starts"
```

Constraints are not boolean-returning validators. They are retained semantic
records with source spans, names, values, and optional notes.

## Functions And Calls

There is one named function form:

```nomi
func normalize_email(email: Text) -> Text:
    cleaned = email.trim()
    return cleaned.lower()
```

Published functions require complete parameter and result types. A private
function may omit an annotation only when its signature is inferable from its
body and direct lexical uses; recursive or ambiguous functions must annotate.
Tooling always displays the resolved signature.

There is one anonymous expression function form. Parentheses are always
present, including for one parameter:

```nomi
is_adult = (person) => person.age >= 18
add = (left, right) => left + right
missing = () => none
```

Calls use positional arguments followed by named arguments. Public APIs should
prefer named arguments for booleans and policy choices.

```nomi
send(message, retry=true, timeout=5.seconds)
```

Defaults are declared in parameter bindings:

```nomi
func connect(host: Text, port: Int = 443, secure: Bool = true) -> Connection:
    ...
```

There are no equation definitions, no whitespace calls, no placeholder
lambdas, no operator sections, and no function-composition operator. Ordinary
functions and a library `compose` cover those meanings without multiplying
the grammar.

`->` appears only in function signatures. `=>` maps an explicit input or
pattern to one expression.

## Data

Product data declares immutable owned values:

```nomi
data User:
    id: UserId
    name: Text where name.trim() != ""
    tags: List[Text] = []
```

Construction uses named fields:

```nomi
user = User(id=id, name="Ada")
```

Variant data declares a closed set of qualified cases:

```nomi
data JobState:
    Queued
    Running(started_at: Instant)
    Failed(error: JobError)
    Finished(result: Report)
```

Construction and matching qualify user-defined variants:

```nomi
state = JobState.Running(started_at=clock.now())
```

Product construction requires named fields. Variant payloads may use their
declared order when there is one field; variants with several fields use named
arguments in construction. Patterns remain positional because their field
order is declared by the variant.

`Result.Ok`, `Result.Err`, `Option.Some`, and `none` are prelude forms and may
be written as `Ok`, `Err`, `Some`, and `none` when unambiguous.

Type aliases use `type` and do not create a runtime wrapper:

```nomi
type Headers = Map[Text, Text]
```

Use single-field `data` when nominal identity or constraints matter.
The initial language has no untagged union type; durable alternatives use
variant `data`, while uncertain external values use `Unknown` or `Value`.

## Conditionals

Boolean conditions require `Bool`; collections, numbers, text, `Option`, and
`Result` do not have implicit truthiness.

```nomi
if user.active:
    notify(user)
else if user.pending:
    queue_reminder(user)
else:
    archive(user)
```

Local value choice uses an inline expression:

```nomi
label = if user.active then "active" else "inactive"
```

There is no `unless`, postfix conditional, ternary punctuation, or implicit
optional test. These all ask the same boolean question and use `if`.

## Patterns And Match

`match` is the only multi-way structural choice form:

```nomi
message = match outcome:
    Ok(user) => "Welcome, {user.name}"
    Err(error) => "Could not register: {error.summary}"
```

Statement branches use blocks:

```nomi
match event:
    Event.Created(item):
        index.add(item)
        audit.record(event)
    Event.Deleted(id):
        index.remove(id)
    _:
        log.debug("ignored event")
```

Every `match` is exhaustive, including statement-position matches. A value
match also requires every reachable arm to produce a compatible value. Closed
variants are covered by their declared cases; open or unknown spaces require a
structural partition the checker can prove or an explicit catch-all. `_` is
only a pattern wildcard; it never generates a function parameter.

Patterns include literals, captures, wildcards, variants, tuples, lists,
mappings, alternatives, and whole-value `as` bindings. An arm may add a
`when` guard after its complete pattern:

```nomi
match value:
    0 => "zero"
    1 | 2 => "small"
    [head, ..tail] => "head={head}, rest={tail.length}"
    {"kind": "user", "id": id, ..} => "user:{id}"
    count when count > 100 => "large"
    _ => "other"
```

Captures are tentative, immutable, and scoped to the selected arm. Structural
failure or a false guard discards all of them. `when` requires a pure `Bool`
and runs once after structural success. Alternative patterns bind the same
names and compatible types. A capture uses an ordinary non-keyword identifier;
reserved vocabulary never changes meaning merely because it appears inside a
pattern.

Literal patterns reuse the canonical scalar spelling and decoder. Text
interpolation is an expression, so interpolated text is not a literal pattern;
normalize first or use a pure `when` guard. Pattern context does not introduce
single-quoted strings or any other context-specific literal dialect.

Lists and maps are exact unless one pattern-only remainder marker is present.
`..` accepts unmentioned elements or entries; `..rest` captures them. Matching
operates on strict language values and never consumes an iterator or calls a
user extractor.

The complete pattern set, precedence, coverage rules, formatting, and
diagnostics are specified in [Pattern Matching](pattern_matching.md), with
pressure examples in [the focused target](pattern_matching_target.nomi).

There is no separate `if let`, `guard let`, `while let`, or piecewise function
syntax. A one-case structural decision remains a small `match`; repeated
structural consumption uses a loop plus `match` or an iterator API.

## Loops And Collections

Loops are statement-oriented:

```nomi
for item in items:
    process(item)

while queue.has_items():
    process(queue.take())
```

`break` and `continue` target the nearest lexical loop. Value-producing
collection work uses one familiar verb family:

```nomi
names =
    users
    |> filter((user) => user.active)
    |> map((user) => user.name)
    |> sort()
```

Pipeline insertion is fixed:

```text
value |> f              means f(value)
value |> f(a, b)        means f(value, a, b)
```

The right-hand call is a pipeline stage, so `filter(predicate)` need not be a
valid partial call by itself. APIs intended for pipelines put their data
argument first.

Canonical verbs are `map`, `filter`, `flat_map`, `fold`, `group_by`,
`sort_by`, `take`, and `collect`. There are no parallel `select`/`where` names.
Strict collections and lazy `Stream` values are distinct. Table libraries may
implement the same verbs and preserve plans, but query syntax is not core.

## Absence And Expected Failure

`Option[T]` represents absence. Safe navigation and fallback apply only to
`Option`:

```nomi
city = user.address?.city ?? "unknown"
```

`Result[T, E]` represents expected failure. Postfix `?` extracts `Ok` or
returns `Err` from the nearest function:

```nomi
func load_user(raw: Value) -> Result[User, DecodeErrors]:
    input = UserInput.decode(raw)?
    return Ok(User.from(input))
```

The enclosing function must return a compatible `Result` (or `Option` when
propagating an `Option`). Error conversion is explicit before propagation:

```nomi
text = files.read(path).map_error(AppError.ReadFailed)?
```

`?` never catches panics, exceptions, cancellation, or arbitrary effects.
`??` never handles `Err`.

Unexpected invariant failures use `panic`. Host exceptions are translated at
interop boundaries; routine Nomi APIs return typed `Result` values.

`panic` is a terminating expression and requires a diagnostic message:

```nomi
panic("queue length became negative")
```

## Resources And Cleanup

`with` owns one acquire/use/release scope. The body executes exactly once and
cleanup runs on normal exit, `return`, `break`, propagated failure, panic, and
cancellation.

```nomi
func read_text(path: Path) -> Result[Text, IoError] uses FileRead:
    resource = files.open(path, mode="read")?
    with resource as file:
        return file.read_all()
```

`defer` registers unconditional LIFO cleanup at lexical scope exit:

```nomi
socket = network.connect(address)?
defer socket.close()
```

`with` is not a universal callback or retry notation. Policies that may invoke
code zero or multiple times receive an explicit function value:

```nomi
response = retry(() => http.get(url), attempts=3)?
```

This keeps execution multiplicity visible.

## Async And Structured Tasks

Asynchronous APIs and suspension points are explicit:

```nomi
async func fetch_user(id: UserId) -> Result[User, HttpError] uses Network:
    response = await http.get("/users/{id}")?
    return User.decode(response.json)
```

Concurrent child work lives in an asynchronous task group:

```nomi
async with TaskGroup() as tasks:
    left = tasks.start(fetch_user(left_id))
    right = tasks.start(fetch_user(right_id))
    users = await tasks.all([left, right])?
```

Tasks cannot escape the group unless explicitly detached through a separately
audited runtime API. `await` is the only ordinary suspension marker. Iteration,
resource scope, generators, and retries do not pretend to be concurrency.

## Effects And Capabilities

Public functions declare the world capabilities they use:

```nomi
pub func write_report(path: Path, report: Report) -> Result[Unit, IoError]
uses Clock, FileWrite:
    generated_at = clock.now()
    return files.write_json(path, report.with_time(generated_at))
```

The `uses` clause is part of the function contract. It is not an argument list
and does not hide expected failures. Private functions may infer effects, but
tooling always displays the resolved set. Tests and hosts supply capability
implementations explicitly.

Direct script statements also infer a module effect set; `nomi check` and the
host display that set before execution. Published library modules cannot hide
effectful initialization. Prelude `print` requires `ConsoleWrite`, even when a
small script leaves that effect inferred.

## Modules

Files are modules. A module declaration is unnecessary when the path already
determines identity.

```nomi
import std.json
import app.models as models
from std.collections import map, filter, collect
```

Imports are immutable bindings. Wildcard imports are not allowed. Declarations
are private unless marked `pub`:

```nomi
pub data User:
    ...

pub func find_user(id: UserId) -> Result[User, StoreError] uses Database:
    ...
```

Dependency versions and hashes belong in `nomi.toml` and `nomi.lock`, not in
ordinary source imports.

## Examples And Checks

Executable examples are ordinary top-level declarations:

```nomi
example "normalizes an email":
    check normalize_email(" ADA@EXAMPLE.COM ") == "ada@example.com"
```

`check` records its source expression and compared values, producing a
structured diagnostic on failure. Examples can live next to code or in test
modules; they do not create a private function-body language.

## Reserved Vocabulary

Core keywords:

```text
and as async await break check continue data defer else example false for
from func if import in match none not note or panic pub return set then true
type uses var when where while with
```

Reserved for likely future use, but not accepted syntax:

```text
actor catch class effect extend generator interface macro protocol raise
trait yield
```

Reservation prevents accidental identifier churn; it does not promise a
feature.

## Operator Budget

| Operator | Meaning family |
| --- | --- |
| `=` | create binding, parameter default, named argument, field construction |
| `==`, `!=`, `<`, `<=`, `>`, `>=` | comparison |
| `+`, `-`, `*`, `/`, `//`, `%`, `**` | arithmetic through protocols |
| `->` | function result type only |
| `=>` | explicit input/pattern maps to one expression |
| `|>` | pass a value to a call stage |
| `|` | alternatives in patterns |
| `..` | remaining list elements or map entries in patterns only |
| `?` | propagate `Option` or `Result` only |
| `?.`, `??` | navigate or default `Option` only |

No accepted operator changes evaluation mode invisibly, performs assignment as
an expression, composes functions, starts concurrency, or grants authority.
