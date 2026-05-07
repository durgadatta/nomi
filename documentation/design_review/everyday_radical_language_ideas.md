# Everyday Radical Language Ideas

> Status: design notebook for widely useful features.
>
> This document is about radical ideas for ordinary programming. The target is
> not niche symbolic systems, expert concurrency, theorem proving, or exotic
> memory models. The target is the kind of feature that could become as normal as
> Python decorators, context managers, comprehensions, varargs, keyword
> arguments, `map`/`filter`, or pattern matching.

## Aim

The best radical feature is one that stops feeling radical after a week.

It should help with daily code:

- naming values,
- transforming collections,
- validating inputs,
- handling missing values,
- opening and closing resources,
- logging and debugging,
- retrying operations,
- shaping data,
- writing tests,
- composing small functions,
- explaining errors,
- avoiding boilerplate.

The bar is high: a feature should be simple at first contact, useful in small
scripts, and still meaningful in large systems.

## Design Filter

Every idea here should pass these tests.

### It Helps Tiny Code

The feature should improve a 20-line script, not only a 200k-line service.

### It Reads Locally

A reader should not need global compiler knowledge to understand the surface
meaning.

### It Desugars

The feature should reduce to ordinary primitives:

```text
binding
function
call
block
pattern
constraint
collection
context
```

### It Is Common Enough

The feature should plausibly appear in everyday code as often as decorators,
comprehensions, `with`, `try`, or keyword arguments.

## Everyday Concern Matrix

| Daily concern | Proposed syntax family | Reduces to |
| --- | --- | --- |
| Validate external input | constrained binding, form binding | binding + predicates |
| Explain validation failure | `else "message"` on constraints | structured errors |
| Avoid temporary variables leaking | `do:` expression blocks, `let` in pipelines | local block + final value |
| Cleanup resources | `using`, `cleanup`, `temporarily` | `try/finally` block |
| Apply cross-cutting behavior | function `with` policies | decorators/wrappers |
| Handle missing values | `?.`, `?:`, `??`, `?=` | optional match + fallback |
| Transform collections | transform blocks, comprehensions with `let` | loops + yield/build |
| Unpack structured data | pattern binding with `else` | match + binding |
| Propagate ordinary failures | `?`, `recover` | `Result` match or try/except |
| Retry or time-limit work | `retry`, `timeout`, `rate`, `cancel_after` | block policies |
| Log and trace | `log`, `trace` | structured event emission |
| Explain decisions | `explain`, `explainable` | expression trace tree |
| Write examples/tests | `examples`, `cases` | data + generated tests |
| Patch nested data | `with:` patch blocks | copy/update |
| Scope mutation | `mut` blocks | explicit receiver mutation |
| Inject dependencies | `needs`, `using services` | explicit environment parameters |
| Run independent work | `parallel`, `race`, `background` | task creation + join/handle |
| Save memory | `stream`, `keep last`, `temp` | representation/lifetime policy |
| Shape JSON/tables | `shape`, `table`, `config` | structural constraints |
| Handle time | duration literals, schedules | unit values + block policies |
| Protect secrets | `secret`, `reveal` | redacted value wrapper |
| Debug state changes | `snapshot`, `watch`, `tracked` | snapshots + diff |
| Encode project defaults | `convention` | scoped syntax/policy defaults |

The important point is that these are not special domains. They are the daily
texture of practical programming.

## Syntax Taste

The proposed forms should feel like small extensions of familiar Python:

```python
using file = open(path):
    text = file.read()

user = fetch_user(id)? else "missing user"

names = users.map -> user:
    user.name

parallel:
    user = fetch_user(id)
    orders = fetch_orders(id)
```

The syntax can be radical underneath, but the first read should be ordinary.

## 1. Binding With Built-In Validation

Python made assignment pleasant. Nomi can make validated assignment pleasant.

### Sample

```python
age:int, age >= 0 = form.age
email:str, contains(email, "@") = form.email
```

In function parameters:

```python
func signup(email:(str, contains(email, "@")), age:(int, age >= 13)):
    ...
```

In loop variables:

```python
for user:User in users:
    send(user.email)
```

### Why Everyday

Most programs validate incoming values. Today this is scattered across
frameworks, assertions, type hints, validators, dataclasses, schemas, and tests.
One binding model would make validation ordinary.

### Desugaring

```python
age:int, age >= 0 = form.age
```

means:

```python
tmp = form.age
if not isinstance(tmp, int): raise TypeError
age = tmp
if not age >= 0: raise TypeError
```

## 2. Human Error Messages On Constraints

Validation should explain itself.

### Sample

```python
age:int, age >= 18 else "Must be 18 or older" = form.age
```

Function parameter:

```python
func buy(amount:(Money, amount > 0 else "Amount must be positive")):
    ...
```

Structured error:

```python
email:str, contains(email, "@") else {
    field: "email",
    message: "Email must contain @",
} = form.email
```

### Why Everyday

Every web app, CLI, API, and data pipeline needs errors that humans can act on.
Current code repeats validation and message wiring everywhere.

### Desugaring

A constraint failure raises a structured validation error carrying the given
message or object.

## 3. Named Intermediate Values In Expressions

People often want expression flow without hiding intermediate names.

### Sample

```python
price = (
    base = item.price
    tax = base * tax_rate
    base + tax
)
```

Pipeline-local bindings:

```python
result = text
    |> parse
    |> let tokens = _
    |> normalize(tokens)
    |> summarize
```

Block expression:

```python
total = do:
    subtotal = items.sum((i) => i.price)
    tax = subtotal * rate
    subtotal + tax
```

### Why Everyday

This avoids the false choice between one large expression and several outer
scope temporary variables.

### Desugaring

`do:` creates a small expression block. The final expression becomes the value.

## 4. One-Line Scoped Cleanup

Context managers are everyday because cleanup is everyday.

### Sample

```python
file = open(path) cleanup file.close()
data = file.read()
```

Block form:

```python
using file = open(path):
    data = file.read()
```

Multiple resources:

```python
using db = connect(), lock = mutex.acquire():
    update(db)
```

### Why Everyday

People open files, acquire locks, create temp dirs, patch environments, and
start spans constantly. `with` is good; Nomi can generalize it while keeping it
plain.

### Desugaring

```python
using file = open(path):
    data = file.read()
```

means:

```python
file = open(path)
try:
    data = file.read()
finally:
    file.close()
```

for resources with a cleanup protocol.

## 5. Decorators With Parameters That Read Like Policy

Python decorators are widely useful, but stacked decorators can become visually
indirect.

### Sample

```python
func fetch_user(id)
with cache(ttl=60), retry(3), timeout(2):
    api.get_user(id)
```

Equivalent decorator-like form:

```python
@cache(ttl=60)
@retry(3)
@timeout(2)
func fetch_user(id):
    api.get_user(id)
```

### Why Everyday

Caching, retrying, timing, auth checks, validation, tracing, and logging are not
advanced. They are daily work.

### Desugaring

The `with policy` form wraps the function value with policy functions, just like
decorators, but keeps the policy close to the body.

## 6. Default-On Missing Values

Missing values are everyday. Handling them should be lightweight.

### Sample

```python
name = user.name ?: "guest"
city = user?.address?.city ?: "unknown"
```

Binding with default:

```python
email = form.email ?? fail("email required")
```

Default object:

```python
settings.theme ?= "light"
```

Meaning: assign default only if missing.

### Why Everyday

APIs, forms, JSON, configs, and optional fields produce missing values
constantly.

### Desugaring

```python
city = user?.address?.city ?: "unknown"
```

means guarded access plus fallback.

## 7. Collection Transform Blocks

Comprehensions are loved because they make collection transformation local.
Nomi can generalize without losing readability.

### Sample

```python
names = collect users -> user:
    if user.active:
        yield user.name
```

Map:

```python
names = users.map -> user:
    user.name
```

Filter:

```python
active = users.keep -> user:
    user.active
```

Group:

```python
by_team = users.group -> user:
    user.team
```

### Why Everyday

Most programs transform collections. `map/filter/reduce` are powerful but can
be noisy with lambdas. Comprehensions are compact but become awkward for
multi-step transformation.

### Desugaring

These are block calls where the collection operation controls iteration and the
caller supplies the body.

## 8. Multi-Step Comprehensions

Python comprehensions are excellent until the body needs names.

### Sample

```python
result = [
    final
    for user in users
    let email = user.email?.lower()
    let final = normalize(email)
    if final is not None
]
```

Dictionary:

```python
by_slug = {
    slug: user
    for user in users
    let slug = slugify(user.name)
    if slug not in blocked
}
```

### Why Everyday

Intermediate names make data transformations readable without forcing a loop.

### Desugaring

Comprehension `let` binds per iteration before later filters or result
expressions.

## 9. Everyday Pattern Binding

Pattern matching should not be only a `match` feature.

### Sample

```python
Point(x, y) = point
Ok(value) = result else return result
{"id": id, "name": name} = payload
```

Optional pattern:

```python
User(email=Some(email)) = user else:
    return "missing email"
```

### Why Everyday

People constantly unpack structured data. Pattern binding makes shape checks and
name extraction one operation.

### Desugaring

Pattern binding is match plus assignment, with atomic failure.

## 10. Result Handling Without Ceremony

Exceptions and result values are both useful. Everyday code needs simple
propagation.

### Sample

```python
config = read_config(path)?
db = connect(config.db)?
run(db)
```

With recovery:

```python
config = read_config(path) recover error:
    default_config()
```

With message:

```python
user = fetch_user(id)? else "Could not load user"
```

### Why Everyday

File IO, APIs, parsing, config, and database operations fail constantly. Boilerplate
error plumbing obscures the normal path.

### Desugaring

`?` matches `Ok/Err` or success/failure values and returns early on failure.
`recover` is expression-level `try/except` or `Result` recovery.

## 11. Inline Retry And Timeout Blocks

Retry and timeout are everyday, not advanced.

### Sample

```python
user = retry(3):
    fetch_user(id)
```

Timeout:

```python
response = timeout(2 seconds):
    http.get(url)
```

Fallback:

```python
avatar = timeout(500 ms) else default_avatar:
    fetch_avatar(user)
```

### Why Everyday

Network calls, file systems, subprocesses, locks, and services fail or hang.
Every app eventually reimplements this.

### Desugaring

These are block calls that run the block under policy and return the block's
result.

## 12. Logging Without String Soup

Logging should be common, structured, and low-friction.

### Sample

```python
log user_created(user.id, user.email)
```

Structured:

```python
log "payment failed":
    user_id = user.id
    reason = error.reason
    retryable = error.retryable
```

Around a block:

```python
trace "load dashboard":
    user = fetch_user(id)
    orders = fetch_orders(id)
```

### Why Everyday

Developers log constantly. String logs lose structure and are hard to query.

### Desugaring

`log` emits a structured event value. `trace` is a block call that records start,
end, duration, errors, and nested logs.

## 13. Automatic Local Explanation

Explain small decisions without requiring a proof system.

### Sample

```python
if explain can_refund(order) -> reason:
    refund(order)
else:
    show(reason)
```

Function:

```python
explainable func can_refund(order):
    order.age_days <= 30
    and order.status != "final_sale"
```

### Why Everyday

Users ask why forms are rejected, why access is denied, why a workflow is
blocked. Developers currently hand-write explanation paths separately from logic.

### Desugaring

An explainable Boolean expression returns `{value, reason}` rather than only
`bool`.

## 14. Test Cases As First-Class Data

Testing should be lighter than framework ceremony.

### Sample

```python
examples slugify:
    "Hello World" => "hello-world"
    " A+B " => "a-b"
```

Attached to function:

```python
func slugify(text):
examples:
    "Hello World" => "hello-world"
    " A+B " => "a-b"
:
    text.lower().strip().replace(non_word+, "-")
```

Table cases:

```python
cases:
    a  b  expected
    1  2  3
    2  3  5
run -> row:
    assert add(row.a, row.b) == row.expected
```

### Why Everyday

Examples are how programmers communicate behavior. They should be executable by
default.

### Desugaring

Examples are data plus generated tests.

## 15. Patch Blocks For Object Updates

Updating nested data is common and verbose.

### Sample

```python
updated = user with:
    name = "Ada"
    settings.theme = "dark"
    settings.notifications.email = True
```

Conditional patch:

```python
updated = user with:
    if form.name:
        name = form.name
    if form.theme:
        settings.theme = form.theme
```

### Why Everyday

APIs, forms, config, immutable data, and UI state all need structured updates.

### Desugaring

Patch blocks copy a value and apply field updates, producing a new value unless
the receiver is explicitly mutable.

## 16. Safe Mutation Blocks

Mutation is useful but should be visually scoped.

### Sample

```python
mut user:
    name = form.name
    email = form.email
```

Nested:

```python
mut cart:
    items.append(item)
    total = items.sum((i) => i.price)
```

### Why Everyday

Mutation is common. A visible mutation block makes side effects easier to review
without requiring a pure functional style.

### Desugaring

Inside `mut user`, bare field assignments target `user`. The block is syntax for
explicit receiver mutation.

## 17. Function Policies For Common Concerns

Make everyday wrappers first-class.

### Sample

```python
func get_user(id)
policy:
    cache ttl=60
    retry 3 on NetworkError
    timeout 2 seconds
    log slow if duration > 500 ms
:
    api.get_user(id)
```

Small form:

```python
func get_user(id) with cache(ttl=60), retry(3):
    api.get_user(id)
```

### Why Everyday

Caching, retries, timing, rate limits, auth, tracing, and validation are normal
application concerns.

### Desugaring

Policies are function decorators/wrappers with structured configuration.

## 18. Local Dependency Injection Without Frameworks

Passing dependencies should be easy but explicit.

### Sample

```python
func send_welcome(user) needs mail, templates:
    body = templates.render("welcome", user)
    mail.send(user.email, body)
```

Call with environment:

```python
send_welcome(user) using app_services
```

Test:

```python
send_welcome(user) using fake_services:
    mail = Mailbox.capture()
    templates = TestTemplates()
```

### Why Everyday

Dependency injection frameworks are common because the need is common. The
language can make the pattern smaller.

### Desugaring

`needs` adds explicit parameters resolved from a supplied environment object.

## 19. Tiny Concurrent Everyday Blocks

Concurrency should appear as "do these independent things together", not as a
framework.

### Sample

```python
parallel:
    user = fetch_user(id)
    orders = fetch_orders(id)
    recommendations = fetch_recommendations(id)

render(user, orders, recommendations)
```

With limits:

```python
parallel limit=5:
    for url in urls:
        pages[url] = fetch(url)
```

Race:

```python
winner = race:
    cache.get(key)
    db.get(key)
```

### Why Everyday

Fetching several independent values is common in web apps, CLIs, data scripts,
and UI code.

### Desugaring

`parallel` creates tasks for independent statements and joins at the end of the
block. Names assigned inside become available after successful join.

## 20. Lazy By Need

Laziness should be opt-in and local.

### Sample

```python
lazy report = build_large_report()
```

Use:

```python
if user.downloads:
    send(report)
```

Memoized:

```python
once expensive = compute()
```

### Why Everyday

People often want "do not compute this unless needed" or "compute this once."
Today this requires ad hoc closures, properties, caches, or decorators.

### Desugaring

`lazy` binds a suspended computation. `once` binds a memoized suspended
computation.

## 21. Everyday Memory Hints Without Ownership Ceremony

Memory optimization can be common if expressed as intent rather than mechanics.

### Sample

```python
stream lines = file.lines()
```

Meaning: do not load all lines into memory.

Bounded collection:

```python
recent = keep last 100 events
```

Borrow-like read block:

```python
read image.pixels -> pixels:
    histogram = pixels.histogram()
```

Temporary arena:

```python
temp:
    buffer = allocate(size)
    process(buffer)
```

### Why Everyday

Developers constantly choose between lists, iterators, caches, streaming, and
temporary buffers. The language can expose common intent without Rust-level
ownership complexity.

### Desugaring

These forms choose library-backed representations and lifetimes:

- `stream` means iterator/lazy sequence,
- `keep last n` means bounded queue,
- `read` means non-mutating access scope,
- `temp` means values released after block.

## 22. Built-In Shape For Data Tables

Tabular data is everyday now.

### Sample

```python
table users:
    id:int
    name:str
    email:str?
```

Use:

```python
active = users.where((u) => u.active)
names = users.select(name)
```

Inline:

```python
rows = table:
    name   age
    "Ada"  36
    "Alan" 41
```

### Why Everyday

CSV, JSON arrays, database rows, dataframes, and UI grids are everywhere.

### Desugaring

A table is a collection of records with column constraints and query helpers.

## 23. Better Defaults For Function Arguments

Varargs and keyword args were radical once. Nomi can smooth common cases.

### Sample

```python
func connect(
    host = "localhost",
    port:int = 5432,
    timeout = 2 seconds,
    **options,
):
    ...
```

Require keyword:

```python
func send(to, *, subject, body):
    ...
```

Forward unknown options:

```python
func wrapper(*args, **opts):
    target(*args, **opts)
```

Named shorthand:

```python
send(:to, :subject, body)
```

### Why Everyday

APIs evolve. Good argument syntax keeps calls readable and wrappers simple.

### Desugaring

Mostly Python-compatible argument binding plus optional shorthand expansion.

## 24. Everyday Format And Parse Pairs

Formatting and parsing should be paired when possible.

### Sample

```python
format iso_date(date):
    "{date.year}-{date.month:02}-{date.day:02}"
```

Use:

```python
text = iso_date(Date(2026, 5, 7))
date = iso_date.parse("2026-05-07")
```

Form binding:

```python
Date(year, month, day) = iso_date.parse(text)
```

### Why Everyday

Dates, IDs, slugs, paths, URLs, and messages are constantly formatted and
parsed. Defining both together reduces drift.

### Desugaring

A format definition is a function plus a generated or declared parser relation.

## 25. Small Queries Over Ordinary Collections

SQL-like ideas are useful outside databases.

### Sample

```python
result = from users -> u:
    where u.active
    group by u.team
    select {
        team: key,
        count: count(u),
    }
```

Smaller:

```python
active_names = users
    |> where(_, (u) => u.active)
    |> select(_, (u) => u.name)
```

### Why Everyday

Most programs query collections. A small query form can make common data work
clearer than nested loops.

### Desugaring

Queries are collection transformations: filter, group, map, sort, aggregate.

## 26. Local Undo Blocks

Make reversible local changes easy.

### Sample

```python
temporarily settings:
    theme = "dark"
    debug = True
:
    render_preview()
```

Environment:

```python
temporarily env:
    PATH = test_path
:
    run_tool()
```

### Why Everyday

Tests, previews, config overrides, environment changes, and mocks need temporary
state constantly.

### Desugaring

Save old values, apply changes, run block, restore in `finally`.

## 27. Built-In Snapshots For Debugging

Debugging daily code often means asking "what changed?"

### Sample

```python
before = snapshot cart
apply_coupon(cart, code)
diff before cart
```

Block:

```python
watch cart:
    apply_coupon(cart, code)
```

Possible output:

```text
cart.total: 100 -> 80
cart.discounts: [] -> [Coupon("SAVE20")]
```

### Why Everyday

State changes cause bugs. Snapshot/diff should not require custom tooling.

### Desugaring

Snapshots are structured copies or persistent-version handles. Diffs compare
values by fields.

## 28. Safe Indexing And Bounds Defaults

Index errors are common and often avoidable.

### Sample

```python
first = users[0] ?: guest_user
name = users[0]?.name ?: "guest"
```

Checked slice:

```python
page = users[page_start..<page_end] clamp
```

Meaning: clamp the requested range to available bounds instead of failing.

Named access:

```python
header = rows.first else fail("empty file")
last = rows.last ?: default_row
```

### Why Everyday

Empty lists and out-of-range indexes are routine. The code should show whether
failure, fallback, or clamping is intended.

### Desugaring

Safe indexing returns an optional/missing value. `clamp` rewrites the range
against the collection length before indexing.

## 29. String Cleanup Pipelines

String normalization is everywhere.

### Sample

```python
slug = text
    |> trim
    |> lower
    |> replace(non_word+, "-")
    |> strip("-")
```

Common cleanup profile:

```python
name = form.name clean:
    trim
    collapse_space
    title_case
```

Validation plus cleanup:

```python
email:str = form.email clean:
    trim
    lower
check:
    contains(email, "@") else "Invalid email"
```

### Why Everyday

Data from humans and APIs is messy. Cleanup code is usually repetitive and
split across helpers.

### Desugaring

`clean:` is a pipeline block applied to the value. `check:` is a constraint
block over the cleaned binding.

## 30. Form And JSON Binding

Parsing request bodies, JSON, CLI args, and forms should feel like binding, not
framework ceremony.

### Sample

```python
bind form Signup:
    email:str, contains(email, "@")
    age:int, age >= 13
    name:str clean trim
```

Use:

```python
signup = Signup.from(request.form)?
```

Inline:

```python
{
    "email": email:(str, contains(email, "@")),
    "age": age:(int, age >= 13),
} = request.json
else error ->:
    return bad_request(error)
```

### Why Everyday

Most applications bind external data into internal names. Today this requires
schemas, validators, serializers, DTOs, or manual parsing.

### Desugaring

`bind form` declares a data shape plus converters and constraints. Inline
binding is pattern binding plus validation.

## 31. CLI Arguments As Function Calls

CLIs should be ordinary functions with argument binding.

### Sample

```python
command resize(
    input:Path,
    output:Path,
    width:int = 800,
    height:int = 600,
    keep_aspect:bool = True,
):
    image = load(input)
    save(image.resize(width, height, keep_aspect), output)
```

Generated usage:

```text
resize input output --width 800 --height 600 --keep-aspect
```

Subcommands:

```python
command users:
    command create(email:str, admin:bool=False):
        ...

    command delete(id:int, force:bool=False):
        ...
```

### Why Everyday

Every project grows scripts. Argument parsing is useful but boilerplate-heavy.

### Desugaring

`command` is a function plus generated parser, help text, type conversion, and
validation from the function signature.

## 32. Configuration As Typed Data With Layers

Configuration is daily code, but current practice is scattered across env vars,
YAML, JSON, flags, secrets, and defaults.

### Sample

```python
config AppConfig:
    host:str = "localhost"
    port:int = 8000
    debug:bool = False
    database_url:str from env "DATABASE_URL"
```

Layering:

```python
settings = AppConfig load:
    defaults
    file "app.toml"
    env
    cli_args
```

Use:

```python
server.start(settings.host, settings.port)
```

### Why Everyday

Almost every application has config. The language can make precedence and
validation explicit.

### Desugaring

`config` is a data declaration plus loaders, defaulting, converters, and
constraint checks.

## 33. Small Batching Syntax

Batching is common in APIs, databases, logging, and UI updates.

### Sample

```python
batch size=100:
    for user in users:
        send_email(user)
```

Collect then flush:

```python
batch emails every 100 or 5 seconds:
    emails.add(message)
flush -> chunk:
    mail.send_bulk(chunk)
```

### Why Everyday

Developers often need "do this in chunks" but write loops and counters by hand.

### Desugaring

`batch` is a block-control helper that buffers values and yields chunks to a
flush block.

## 34. Rate Limit Blocks

Rate limiting should be as ordinary as retry.

### Sample

```python
rate 10 per second:
    for url in urls:
        fetch(url)
```

Per key:

```python
rate 100 per minute by user.id:
    send_notification(user)
```

### Why Everyday

APIs, email, notifications, jobs, and scraping all need rate control.

### Desugaring

`rate` is a block-control policy that schedules block execution according to a
token bucket or similar limiter.

## 35. Cancellation As A Block Policy

Everyday async code needs cancellation that is visible and scoped.

### Sample

```python
cancel_after 5 seconds:
    render_report()
```

Cancel when another block completes:

```python
cancel_rest when first_done:
    fast = fetch(cache)
    slow = fetch(database)
```

Manual scope:

```python
cancel_scope -> cancel:
    button.on_click(cancel)
    upload(file)
```

### Why Everyday

Users close pages, requests timeout, jobs are superseded. Cancellation should
not require expert async architecture.

### Desugaring

Cancellation blocks pass a cancellation token through a scoped context and
ensure cleanup when cancellation fires.

## 36. Background Work That Returns A Handle

Starting background work should be simple, but not invisible.

### Sample

```python
task = background:
    generate_report()

notify_when task.done:
    send(task.result)
```

Fire-and-track:

```python
background named "sync contacts":
    sync_contacts()
```

### Why Everyday

Apps often start work that outlives the current screen/request/script. The
language should make the handle explicit so errors are not lost.

### Desugaring

`background` creates a task value with result, error, cancellation, and status.

## 37. Progress As A Language-Level Convention

Long-running tasks should expose progress without custom callback plumbing.

### Sample

```python
progress "import users" -> step:
    for row in csv.rows():
        import_user(row)
        step()
```

Known total:

```python
progress total=len(files) -> step:
    for file in files:
        process(file)
        step(label=file.name)
```

Consumer:

```python
for update in task.progress:
    print(update.percent, update.label)
```

### Why Everyday

Imports, exports, uploads, batch jobs, reports, and migrations need progress.

### Desugaring

`progress` creates a structured progress reporter and passes it into a block.

## 38. Built-In Memo And Cache Bindings

Caching is often just binding with a retention policy.

### Sample

```python
memo user = fetch_user(id)
```

Keyed:

```python
memo fetch_user(id) ttl=60:
    api.get_user(id)
```

Invalidate:

```python
invalidate fetch_user(id)
```

### Why Everyday

Caching is not rare. Developers constantly memoize expensive calls, API
responses, file reads, and computed properties.

### Desugaring

`memo` is a binding/function wrapper backed by a cache keyed by arguments or
declared key expressions.

## 39. Dirty Tracking For Ordinary Values

Apps often need to know what changed.

### Sample

```python
tracked user = edit_user(original)

if user.changed:
    save(user.changes)
```

Field check:

```python
if user.email.changed:
    send_confirmation(user.email)
```

### Why Everyday

Forms, settings, editors, ORM objects, and UI state all need change tracking.

### Desugaring

`tracked` wraps a value with original/current snapshots and field-level diff.

## 40. Built-In Undo For User-Facing State

Undo is common but hard.

### Sample

```python
undoable document:
    title = "New title"
    body.replace(selection, text)
```

Use:

```python
document.undo()
document.redo()
```

Named action:

```python
undoable "format paragraph" on document:
    paragraph.style = "quote"
```

### Why Everyday

Editors, dashboards, admin tools, forms, and design tools need undo. The pattern
is not niche.

### Desugaring

`undoable` records inverse patches or before/after snapshots for a scoped
mutation block.

## 41. Declarative Loading States

UI and service code constantly handles loading/error/empty/success states.

### Sample

```python
load users = fetch_users()

view users:
    loading:
        spinner()
    error e:
        error_box(e)
    empty:
        empty_state("No users")
    ready users:
        user_table(users)
```

Non-UI:

```python
when users:
    ready value:
        process(value)
    error e:
        retry_later(e)
```

### Why Everyday

This pattern appears in web apps, CLIs, services, and data loading.

### Desugaring

`load` creates a state value: `Loading | Error(e) | Empty | Ready(value)`.
`view/when` is pattern matching over that state.

## 42. Shape-Aware Dictionaries

Dictionaries are everyday, but key mistakes are common.

### Sample

```python
shape UserPayload:
    id:int
    name:str
    email:str?

payload:UserPayload = request.json
```

Access:

```python
payload.name
payload["name"]
```

Partial:

```python
patch:partial UserPayload = request.json
```

### Why Everyday

JSON-like dictionaries dominate modern programming. Shape constraints should be
lightweight.

### Desugaring

Shapes are structural constraints over mapping values plus optional field access
sugar.

## 43. Everyday Data Migration Blocks

Changing data shape is common.

### Sample

```python
migrate UserPayload v1 -> v2:
    full_name = name
    email = email ?: None
    drop name
```

Use:

```python
payload = UserPayload.v2.from(raw)
```

### Why Everyday

APIs, configs, saved files, caches, and database records evolve.

### Desugaring

Migration blocks are named transformation functions between shaped data
versions.

## 44. Small Time Syntax For Durations And Schedules

Time is everyday but libraries make it verbose.

### Sample

```python
timeout(2 seconds):
    fetch(url)

retry every 500 ms up_to 5 seconds:
    connect()
```

Schedule:

```python
every 1 hour:
    sync()
```

Business time:

```python
due = today + 3 business_days
```

### Why Everyday

Timeouts, retries, schedules, cache TTLs, and due dates appear everywhere.

### Desugaring

Duration literals are unit-tagged values. Schedule forms are block-control
helpers over clocks.

## 45. Permission Checks As Ordinary Guards

Authorization is daily code and should not be scattered.

### Sample

```python
allow user can "delete" document:
    document.owner == user or user.admin
```

Use:

```python
require user can "delete" document:
    delete(document)
else reason:
    forbidden(reason)
```

### Why Everyday

Most apps check permissions. Policies should be readable, testable, and
explainable.

### Desugaring

Permission declarations are named predicates returning structured allow/deny
results.

## 46. Localized Data Redaction

Redacting sensitive values is ordinary in logs, errors, and UI.

### Sample

```python
secret password = form.password
token:secret str = request.headers["Authorization"]
```

Logging:

```python
log login_failed(user.email, password)
```

Output:

```text
login_failed email="a@b.com" password="[secret]"
```

Explicit reveal:

```python
reveal password in secure_world:
    verify(password)
```

### Why Everyday

Secrets leak through logs and errors. Redaction should be a value property, not
an afterthought.

### Desugaring

`secret` wraps a value with display/logging constraints and explicit reveal
requirements.

## 47. Built-In Sampling For Expensive Work

Instrumentation and validation often need sampling.

### Sample

```python
sample 1 percent:
    validate_full_payload(payload)
```

Log sampling:

```python
log slow_query(query) sample 10 percent
```

### Why Everyday

Production checks, logs, metrics, and traces often cannot run for every event.

### Desugaring

`sample` is a probabilistic guard around a block or event emission.

## 48. Assertions That Can Become Runtime Policies

Assertions are useful in development but often disappear in production.

### Sample

```python
assert user.email is not None
    else "User must have email before invite"
```

Policy:

```python
assert mode production:
    log and continue
mode test:
    raise
```

### Why Everyday

Teams want different assertion behavior in tests, staging, and production.

### Desugaring

Assertions emit structured failures handled by an assertion policy.

## 49. Importable Local Conventions

Projects develop conventions. Make them explicit and scoped.

### Sample

```python
convention web_app:
    default timeout = 2 seconds
    default retry = 2 on NetworkError
    log structured
    secret fields = ["password", "token"]
```

Use:

```python
use convention web_app
```

### Why Everyday

Projects have repeated defaults. Today these become framework magic or copied
boilerplate.

### Desugaring

Conventions are scoped defaults for policies, logging, validation, and
capabilities. Expansions must be inspectable.

## 50. Everyday Feature Priority

The most promising daily radical features are:

- validated binding with human messages,
- missing-value fallback and safe access,
- expression blocks with local names,
- generalized cleanup blocks,
- collection transform blocks and multi-step comprehensions,
- pattern binding with `else`,
- retry/timeout/rate/cancel blocks,
- structured log/trace,
- function policies,
- local dependency injection,
- tiny `parallel`, `race`, and `background`,
- stream/bounded/temp memory hints,
- config/CLI/form binding,
- patch/mutation/undo blocks,
- shape-aware dictionaries,
- durations and schedules,
- secrets/redaction,
- project conventions.

These are not niche. They are the texture of ordinary programs.

## 51. A Daily Nomi Example

This is the target flavor: radical only because many daily concerns become
first-class and small.

```python
data User(id:int, name:str, email:str?)

func load_dashboard(user_id:int)
with cache(ttl=30), timeout(2 seconds), retry(2):
    parallel:
        user = fetch_user(user_id)?
        orders = fetch_orders(user_id)?
        recommendations = fetch_recommendations(user_id) recover:
            []

    email = user.email ?: "missing"

    trace "dashboard loaded":
        log user_loaded(user.id, email)
        log order_count(len(orders))

    {
        user: user,
        orders: orders,
        recommendations: recommendations,
    }
```

None of this should feel advanced:

- policies wrap a function,
- parallel fetches independent values,
- `?` handles ordinary failures,
- `recover` supplies fallback,
- `?:` handles missing values,
- `trace` and `log` produce structured observability,
- final dictionary is the result.

## 52. Expanded Daily Example: CLI Script

```python
command import_users(
    file:Path,
    dry_run:bool = False,
    batch_size:int = 100,
):
    config AppConfig:
        database_url:str from env "DATABASE_URL"

    settings = AppConfig load env

    using db = connect(settings.database_url):
        stream rows = csv(file).rows()

        progress total=rows.count? -> step:
            batch size=batch_size:
                for row in rows:
                    user = User.from(row)? else error:
                        log invalid_user(row, error) sample 10 percent
                        continue

                    if dry_run:
                        log would_import(user.email)
                    else:
                        db.users.upsert(user)

                    step()
```

This is everyday code:

- CLI args,
- env config,
- scoped database cleanup,
- streaming file reads,
- progress,
- batching,
- validation,
- structured logs,
- dry-run behavior.

## 53. Expanded Daily Example: Web Handler

```python
shape SignupPayload:
    email:str
    age:int
    name:str?

func signup(request)
with timeout(2 seconds), trace("signup"):
    payload:SignupPayload = request.json
    else error:
        return bad_request(error)

    email:str, contains(email, "@") else "Invalid email" = payload.email clean:
        trim
        lower

    age:int, age >= 13 else "Must be at least 13" = payload.age
    name = payload.name ?: "friend"

    require not users.exists(email=email):
        user = User(email=email, age=age, name=name)
        users.insert(user)?
        send_welcome(user) background
        return created(user)
    else:
        return conflict("Email already registered")
```

The feature mix is routine:

- JSON shape,
- cleaning,
- validation messages,
- missing defaults,
- requirement guard,
- result propagation,
- background side task,
- tracing.

## 54. Expanded Daily Example: UI State Update

```python
data Settings(theme:str, email_alerts:bool, timezone:str?)

tracked settings = load_settings(user)

view settings:
    loading:
        spinner()
    error e:
        error_box(e)
    ready settings:
        form settings -> draft:
            field theme choices ["light", "dark", "system"]
            field email_alerts toggle
            field timezone optional

            preview = settings with:
                theme = draft.theme
                email_alerts = draft.email_alerts
                timezone = draft.timezone

            temporarily app.settings = preview:
                render_preview()

            if draft.changed:
                save(preview)?
```

This combines:

- load-state matching,
- forms,
- patch blocks,
- temporary overrides,
- tracked changes,
- result handling.

## 55. The Real Radical Move

The radical move is not adding exotic features. It is noticing that daily code
already contains hidden patterns:

- validate this,
- default that,
- clean this up,
- retry this,
- run these together,
- log this structurally,
- explain this decision,
- transform this collection,
- patch this object,
- temporarily override this state,
- do this only if needed.

Nomi should make those patterns ordinary syntax, while keeping each one
desugarable into simple primitives.

That is how a radical feature becomes commonplace.
