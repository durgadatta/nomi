# Proposed Syntax Samples

> Status: exploratory syntax catalog.
>
> This document is intentionally sample-heavy. It sketches what Nomi code could
> look like if it synthesized well-loved syntax ideas from Python, Ruby,
> Mathematica, Lisp, ALGOL, APL, Scala, Kotlin, ML, Haskell, Rust, Swift, and
> related languages while remaining reducible to a small semantic core.

## Small Core Assumption

Every surface form in this document should reduce to a small set of primitives:

- values,
- names and bindings,
- constraints on bindings,
- functions,
- function calls,
- caller-side blocks,
- `yield` to blocks,
- patterns,
- explicit expression values for symbolic/code-shaped data.

If a syntax form cannot be explained through these ideas, it should stay out of
the language until its primitive meaning is clearer.

## 1. Binding

Basic binding should remain Python-readable.

```python
name = "Nomi"
count = 3
enabled = True
```

Constrained binding validates at the point of binding.

```python
age:int = 34
age:int, age >= 0 = 34
email:str, contains(email, "@") = "a@b.com"
```

Predicate functions are ordinary constraints.

```python
is_pos = (x) => x > 0
amount:int, is_pos = 25
```

Constant binding can be explicit if Nomi later distinguishes rebinding policy.

```python
const pi = 3.14159
const app_name:str = "Nomi"
```

Destructuring is binding through a pattern.

```python
(x, y) = point
[first, *rest] = items
{"id": id, "name": name} = user
```

Constrained destructuring should reuse the same binding idea.

```python
(x:int, y:int) = point
{"age": age:(int, age >= 0)} = user
```

Reduction:

```python
(x, y) = point
```

means:

```python
tmp = point
x = tmp[0]
y = tmp[1]
```

plus shape checks.

## 2. Functions

Named functions use `func`.

```python
func add(x, y):
    return x + y
```

Parameters are bindings, so constraints work there too.

```python
func withdraw(account, amount:(int, amount > 0)):
    account.balance -= amount
```

Expression functions use arrows.

```python
square = (x:int) => x * x
add = (x, y) => x + y
```

Multi-line expression functions can use a block when readability needs it.

```python
score_user = (user) =>:
    base = user.reputation
    bonus = user.completed_tasks * 2
    base + bonus
```

Reduction:

```python
score_user = (user) =>:
    base = user.reputation
    bonus = user.completed_tasks * 2
    base + bonus
```

means:

```python
func score_user(user):
    base = user.reputation
    bonus = user.completed_tasks * 2
    return base + bonus
```

Decorators remain Python-like.

```python
@logged
@timed
func fetch_user(id:int):
    return api.get_user(id)
```

Inline anonymous block parameters can use the same arrow syntax.

```python
users.map((u) => u.name)
users.filter((u) => u.active)
```

## 3. Calls

Ordinary calls remain ordinary.

```python
send(email, subject, body)
```

Keyword arguments stay readable.

```python
send(to=email, subject="Welcome", body=body)
```

Spread is Python-compatible.

```python
send(*args, **options)
```

Named argument shorthand can be considered for common object construction and
calls where the variable name matches the parameter name.

```python
send(:email, :subject, body)
```

Possible reduction:

```python
send(email=email, subject=subject, body=body)
```

This is useful but optional. It should be admitted only if it stays visually
clear.

## 4. Blocks

Ruby's strongest contribution is caller-side blocks. Nomi should make that idea
Python-readable.

```python
retry(3):
    send_request()
```

Zero-argument block call:

```python
transaction(db):
    create_user()
    send_welcome_email()
```

Yielded value block call:

```python
each(users) -> user:
    print(user.name)
```

Multiple yielded values:

```python
pairs(headers) -> key, value:
    print(key, value)
```

Constrained yielded values:

```python
each(users) -> user:User:
    print(user.name)
```

Alternative if the double colon reads poorly:

```python
each(users) -> user(User):
    print(user.name)
```

The block runs in caller scope.

```python
status = "pending"

once():
    status = "done"

print(status)  # "done"
```

Reduction:

```python
retry(3):
    send_request()
```

means:

```python
retry(3, block=<caller block containing send_request()>)
```

and inside `retry`, `yield` invokes that block.

## 5. Control As Library-Defined Blocks

The language should not need a new keyword for every control pattern.

```python
timeout(5):
    fetch(url)
```

```python
lock(my_lock):
    update_shared_state()
```

```python
measure("load users") -> elapsed:
    users = load_users()
```

```python
with_env(DEBUG=True):
    run_tests()
```

```python
capture_logs() -> logs:
    service.run()
print(logs)
```

Possible library-defined concurrency:

```python
parallel():
    fetch_user()
    fetch_orders()
    fetch_recommendations()
```

Possible structured tasks:

```python
scope() -> task:
    user = task.spawn(() => fetch_user())
    orders = task.spawn(() => fetch_orders())
    combine(user.await(), orders.await())
```

Reduction: all are calls with attached blocks. The callee decides when and how
often to `yield`.

## 6. Conditionals As Expressions

Statement style remains valid.

```python
if score >= 90:
    label = "excellent"
else:
    label = "ok"
```

Expression-oriented form:

```python
label = if score >= 90:
    "excellent"
else:
    "ok"
```

Guard-like early exit, inspired by Swift/Kotlin/Rust ergonomics:

```python
guard user is not None:
    return "missing user"

send_welcome(user)
```

Possible reduction:

```python
if not (user is not None):
    return "missing user"
send_welcome(user)
```

`unless` is Ruby-readable but should be used sparingly.

```python
return unless ready
```

Possible reduction:

```python
if not ready:
    return
```

This is concise, but it may hurt Python-like clarity. Candidate only.

## 7. Pattern Matching

Use Python's readable `match`, but allow expression orientation.

```python
match event:
    case {"type": "click", "x": x, "y": y}:
        handle_click(x, y)
    case {"type": "key", "key": key}:
        handle_key(key)
    case _:
        ignore(event)
```

As an expression:

```python
kind = match value:
    case int:
        "number"
    case str:
        "text"
    case [first, *rest]:
        "sequence"
    case _:
        "unknown"
```

Match with constraints:

```python
match user:
    case {"age": age:(int, age >= 18)}:
        allow()
    case _:
        deny()
```

Algebraic-data-like pattern:

```python
match result:
    case Ok(value):
        value
    case Err(error):
        raise error
```

Reduction: `match` is repeated pattern binding plus guards.

## 8. Data Values

Lightweight structured values:

```python
data Point(x:int, y:int)
data User(id:int, name:str, email:str?)
```

Construction:

```python
p = Point(2, 3)
u = User(id=1, name="Ada", email=None)
```

Pattern use:

```python
match p:
    case Point(x, y):
        x + y
```

Default values:

```python
data User(
    id:int,
    name:str,
    active:bool = True,
)
```

Derived fields could be library-level, not core syntax.

```python
data Invoice(items):
    total = items.sum((item) => item.price)
```

Reduction: `data` declares a constructor, named fields, equality, and pattern
shape. It is sugar over ordinary values plus bindings.

## 9. Traits, Protocols, And Interfaces

Scala/Rust/Kotlin suggest named behavioral contracts, but Nomi should keep them
plain.

```python
trait Drawable:
    func draw(self, canvas)
```

```python
trait Sized:
    func len(self) -> int
```

Implementation candidate:

```python
impl Drawable for Circle:
    func draw(self, canvas):
        canvas.circle(self.center, self.radius)
```

Duck-typed protocol candidate:

```python
protocol Reader:
    func read(self, n:int) -> bytes
```

Reduction: a trait/protocol is a named set of function constraints. It should
not require a heavy class hierarchy.

## 10. Extension-Style Functions

Kotlin/Scala-style extension functions improve method usability without forcing
ownership into classes.

```python
func String.words(self):
    return self.split()
```

Use:

```python
"hello world".words()
```

Pipeline-friendly:

```python
text |> String.words
```

Generic extension:

```python
func List[T].second(self) -> T:
    return self[1]
```

Reduction:

```python
"hello".words()
```

means:

```python
String.words("hello")
```

under module-visible extension lookup.

## 11. Pipelines

Nested calls:

```python
result = summarize(normalize(parse(text)))
```

Pipeline:

```python
result = text |> parse |> normalize |> summarize
```

Placeholder form:

```python
result = text |> parse(mode="loose", _) |> normalize(_) |> summarize(_)
```

Multi-line pipeline:

```python
result = (
    text
    |> parse
    |> normalize
    |> summarize
)
```

Pipelines with lambdas:

```python
names = users |> map(_, (u) => u.name) |> sort
```

Pipelines with blocks:

```python
report = users |> group_by(_, (u) => u.team) |> render:
    title = "Users by team"
```

The last example is speculative. The simple rule should be: `|>` rewrites into
a call where the left value is inserted into the next stage.

## 12. Function Composition

Composition builds a function.

```python
clean = strip >> lower >> normalize_space
```

Use:

```python
clean("  HELLO  ")
```

Backward composition may be allowed but is lower priority.

```python
clean = normalize_space << lower << strip
```

Reduction:

```python
(f >> g)(x) == g(f(x))
```

Composition should be for function values, while pipelines are for values now.

## 13. Collection And Array Operations

Readable whole-collection operations:

```python
xs.map((x) => x * 2)
xs.filter((x) => x > 0)
xs.sum()
```

Pipeline style:

```python
total = (
    xs
    |> filter(_, (x) => x > 0)
    |> map(_, (x) => x * 2)
    |> sum
)
```

Comprehension remains Python-like:

```python
doubles = [x * 2 for x in xs if x > 0]
```

Dictionary comprehension:

```python
by_id = {user.id: user for user in users}
```

APL-inspired elementwise shorthand is candidate-only.

```python
ys = xs.*2
zs = xs.+ys
mask = xs.>0
```

Reduction:

```python
xs.*2 == xs.map((x) => x * 2)
xs.+ys == zip(xs, ys).map((x, y) => x + y)
```

Rank-like operation may be library-first:

```python
matrix.each_row() -> row:
    print(row.sum())
```

Instead of dense symbolic rank operators, prefer named operations first.

## 14. Ranges, Slices, And Indexing

Human inclusive range:

```python
1..10
```

Index-friendly half-open range:

```python
0..<n
```

Slicing:

```python
xs[1..<4]
xs[..3]
xs[3..]
xs[..]
```

Step:

```python
xs[0..<10 by 2]
```

Reduction: ranges are values. Slices are indexing calls with range values.

```python
xs[1..<4] == xs.get(range(1, 4, end="open"))
```

## 15. Null, Option, And Result

Kotlin-style safe access:

```python
city = user?.address?.city
```

Fallback:

```python
name = user.name ?: "guest"
```

Required value:

```python
name = user.name!
```

`!` is risky. It should mean "fail here if empty" and should be visually
obvious in code review.

Option-style pattern:

```python
match user.email:
    case Some(email):
        send(email)
    case None:
        skip()
```

Result-style error handling:

```python
result = read_config(path)

match result:
    case Ok(config):
        start(config)
    case Err(error):
        report(error)
```

Try-like propagation candidate:

```python
config = read_config(path)?
start(config)
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

This is inspired by Rust. It should only exist if Nomi has a clear `Result`
model.

## 16. Errors And Recovery

Python-like exceptions remain familiar.

```python
try:
    load()
except FileNotFoundError as e:
    recover(e)
finally:
    cleanup()
```

Block-based recovery:

```python
retry(3, on=NetworkError):
    fetch(url)
```

Expression recovery:

```python
config = try:
    load_config()
except FileNotFoundError:
    default_config()
```

Reduction: expression `try` is statement `try` whose selected branch produces a
value.

## 17. Loops And Iteration

Keep Python loops.

```python
for user in users:
    print(user.name)
```

Ranges:

```python
for i in 0..<10:
    print(i)
```

Block-defined iteration:

```python
users.each() -> user:
    print(user.name)
```

Loop with destructuring:

```python
for key, value in pairs:
    print(key, value)
```

Loop with constraints:

```python
for user:User in users:
    print(user.name)
```

Reduction: loop variable binding is binding with optional constraints.

## 18. Modules And Use

Python-compatible imports should remain.

```python
import math
from pathlib import Path
```

Candidate `use` for bringing extension functions, traits, or rule sets into
scope:

```python
use text.words
use math.vector.*
```

Reduction: `use` is controlled import plus scope-visible capabilities.

Local alias:

```python
import numpy as np
use dataframe as df
```

The design should avoid hidden global mutation.

## 19. Symbolic Expressions

Quote expression-shaped code:

```python
expr = quote:
    x + 0
```

Short quote for small expressions:

```python
expr = '(x + 0)
```

Inspect:

```python
expr.head
expr.args
```

Evaluate explicitly:

```python
value = eval(expr, env={"x": 3})
```

Reduction: quoted syntax produces an explicit expression value. It does not run
as ordinary code until passed to an evaluator.

## 20. Rewrite Rules

Mathematica-style transformation:

```python
simplified = expr /. x + 0 -> x
```

Multiple rules:

```python
simplified = expr /. [
    x + 0 -> x,
    0 + x -> x,
    x * 1 -> x,
    1 * x -> x,
]
```

Repeated rewrite:

```python
normal = expr //. [
    x + 0 -> x,
    x * 1 -> x,
]
```

Conditional rule:

```python
expr /. n -> n * 2 if n:int
```

Function-backed rule:

```python
expr /. Call(name, args) -> lower_call(name, args)
```

Reduction: rewriting is pattern matching over explicit expression values plus
construction of replacement expression values.

## 21. Macros And Compile-Time Transformation

Lisp teaches that macros are powerful because code can be represented as data.
Nomi should be cautious here.

Candidate:

```python
macro assert_equal(left, right):
    quote:
        if {left} != {right}:
            raise AssertionError(f"{left} != {right}")
```

Use:

```python
assert_equal(user.name, "Ada")
```

Reduction: a macro is a function from quoted syntax to quoted syntax, expanded
before normal evaluation.

Restriction: macros should be explicit imports and should not silently change
the meaning of ordinary local syntax.

## 22. String And Template Syntax

Keep Python-like f-strings.

```python
message = f"Hello {user.name}"
```

Multi-line:

```python
sql = f"""
select *
from users
where team = {team_id}
"""
```

Safe template block candidate:

```python
query = sql():
    select *
    from users
    where team = {team_id}
```

Reduction: tagged blocks are function/block calls over raw text or quoted
syntax.

```python
sql:
    select * from users
```

means:

```python
sql(block_text)
```

or:

```python
sql(block_expression)
```

depending on the tag.

## 23. Object And Method Syntax

Class syntax can remain Python-like.

```python
class Account:
    func deposit(self, amount:(int, amount > 0)):
        self.balance += amount
```

Data values should cover many class use cases:

```python
data Account(id:int, balance:int)
```

Property-like computed members:

```python
class Circle:
    func area(self):
        return pi * self.radius * self.radius
```

Candidate property sugar:

```python
class Circle:
    prop area:
        pi * self.radius * self.radius
```

Reduction:

```python
prop area: expr
```

means a zero-argument method exposed as field-like access.

## 24. Query And Dataflow Syntax

LINQ/SQL-like readability is useful, but should probably be library-led.

Pipeline query:

```python
active_names = (
    users
    |> filter(_, (u) => u.active)
    |> map(_, (u) => u.name)
    |> sort
)
```

Query block candidate:

```python
query users -> u:
    where u.active
    select u.name
    order by u.name
```

Reduction: query blocks are quoted or block-structured calls to a query builder.

The pipeline form should be preferred until query syntax proves its value.

## 25. Tests And Assertions

Tests are good examples for block syntax.

```python
test "withdraw reduces balance":
    account = Account(balance=100)
    account.withdraw(30)
    assert account.balance == 70
```

Parameterized:

```python
cases([(1, 2, 3), (2, 3, 5)]) -> a, b, expected:
    test f"{a} + {b}":
        assert add(a, b) == expected
```

Reduction: `test` can be a block call that registers and runs a caller-side
block. It does not need to be a primitive keyword at first.

## 26. Effects And Actions

Nomi should distinguish value-shaped code from action-shaped code through usage,
not heavy ceremony.

Value:

```python
total = items.sum((x) => x.price)
```

Action:

```python
for item in items:
    save(item)
```

Action block:

```python
transaction(db):
    for item in items:
        save(item)
```

Possible effect annotation:

```python
func save_user(user) !io:
    db.save(user)
```

This is speculative. If effects enter the language, they should be constraints
on functions/actions, not a separate programming model.

## 27. Async And Concurrency

Python's `async` is familiar, but structured concurrency may be more usable.

```python
async func fetch_user(id):
    return await http.get(f"/users/{id}")
```

Block scope:

```python
async_scope() -> task:
    user = task.spawn(() => fetch_user(id))
    orders = task.spawn(() => fetch_orders(id))
    render(await user, await orders)
```

Candidate lighter syntax:

```python
async:
    user = spawn fetch_user(id)
    orders = spawn fetch_orders(id)
    render(await user, await orders)
```

The block-call version is more consistent with the small core. Dedicated syntax
should wait until the pattern is stable.

## 28. Defer And Cleanup

Go/Swift-style `defer` is useful but reducible to block cleanup.

```python
func write_file(path, text):
    f = open(path, "w")
    defer f.close()
    f.write(text)
```

Reduction:

```python
with open(path, "w") as f:
    f.write(text)
```

or a block-control cleanup stack. Candidate only, because block calls may cover
most cleanup use cases.

## 29. Named Blocks And Local Structure

ALGOL-like block structure can improve local organization.

```python
block:
    temp = compute()
    result = normalize(temp)
```

Scoped block candidate:

```python
scope:
    temp = compute()
    result = normalize(temp)
print(temp)  # error if scope is isolated
```

Nomi's default block calls use caller scope. Isolated scopes should be explicit.

```python
isolated:
    temp = compute()
```

Reduction: a scoped block is a function/block call with an explicit environment
policy.

## 30. Style Summary

Preferred Nomi syntax should look like this:

```python
data User(id:int, name:str, email:str?)

func active_email(user:User) -> str?:
    if user.active:
        user.email
    else:
        None

emails = (
    users
    |> filter(_, (u) => u.active)
    |> map(_, active_email)
    |> filter(_, (email) => email is not None)
)

retry(3, on=NetworkError):
    send_batch(emails)
```

The code is Python-readable, but it has:

- constrained bindings,
- expression-oriented functions,
- data declarations,
- pipeline flow,
- block-based retry control.

All of it reduces to the small core: values, bindings, functions, calls,
patterns, constraints, blocks, and explicit control around `yield`.
