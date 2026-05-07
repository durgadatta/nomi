# Cross-Language Feature Synthesis Examples

> Status: comparative design study.
>
> This document compares similar but not identical language features across
> several well-loved languages, then proposes a Nomi synthesis for each family.
> The emphasis is surface usability plus reduction to a small core.

## Reading Guide

Each section follows the same pattern:

- the recurring programming need,
- representative syntax from existing languages,
- what each language gets right,
- what creates friction,
- proposed Nomi syntax,
- reduction to Nomi primitives.

The recurring primitives are:

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

## 1. Naming Functions

### Recurring Need

Define reusable behavior and bind it to a name.

### Existing Forms

Python:

```python
def add(x, y):
    return x + y
```

Ruby:

```ruby
def add(x, y)
  x + y
end
```

Scala:

```scala
def add(x: Int, y: Int): Int =
  x + y
```

Kotlin:

```kotlin
fun add(x: Int, y: Int): Int {
    return x + y
}
```

Scheme:

```scheme
(define (add x y)
  (+ x y))
```

Mathematica:

```wolfram
add[x_, y_] := x + y
```

### Observations

Python and Ruby are readable but `def` is generic. Kotlin's `fun` is explicit
but informal. Scala separates expression-bodied and block-bodied definitions.
Scheme is semantically regular but visually foreign to Python readers.
Mathematica's pattern-based definition is powerful, but `_` patterns in the
definition head are not beginner-friendly.

### Nomi Synthesis

```python
func add(x:int, y:int) -> int:
    x + y
```

or, when an explicit return is clearer:

```python
func add(x:int, y:int) -> int:
    return x + y
```

Expression form:

```python
add = (x:int, y:int) => x + y
```

### Reduction

```python
func add(x:int, y:int) -> int:
    x + y
```

reduces to:

```text
bind name `add`
to function value with parameters x, y
validate x:int and y:int when called
evaluate body
validate return:int if return constraint is present
```

## 2. Anonymous Functions And Function Literals

### Existing Forms

Python:

```python
lambda x: x + 1
```

JavaScript:

```javascript
x => x + 1
(x, y) => x + y
```

Scala:

```scala
(x: Int) => x + 1
```

Kotlin:

```kotlin
{ x: Int -> x + 1 }
```

Ruby:

```ruby
->(x) { x + 1 }
```

Haskell:

```haskell
\x -> x + 1
```

APL:

```apl
{right + 1}
```

### Observations

JavaScript and Scala arrows are readable and familiar. Kotlin/Ruby blocks are
good in call positions, but less uniform with named functions. Python's
`lambda` is constrained and visually unlike `def`. Haskell and APL are compact
but not aligned with Nomi's readability goal.

### Nomi Synthesis

```python
(x) => x + 1
(x:int) => x + 1
(x:int, y:int) => x + y
```

Multi-line:

```python
(user) =>:
    base = user.score
    bonus = user.reviews * 2
    base + bonus
```

### Reduction

Arrow functions create ordinary function values. Multi-line arrows are sugar for
anonymous `func` values whose final expression is returned.

## 3. Binding, Declaration, And Mutation

### Existing Forms

Python:

```python
x = 1
x: int = 1
```

JavaScript:

```javascript
let x = 1
const y = 2
```

Kotlin:

```kotlin
var x = 1
val y = 2
```

Rust:

```rust
let x = 1;
let mut y = 2;
```

Scala:

```scala
var x = 1
val y = 2
```

Mathematica:

```wolfram
x = 1
x := RandomInteger[]
```

### Observations

Python is light but does not distinguish constant intent. Kotlin/Scala/Rust make
mutability explicit but add declaration ceremony. Mathematica distinguishes
immediate and delayed binding, an important symbolic/programming distinction.

### Nomi Synthesis

Default simple binding:

```python
x = 1
```

Constrained binding:

```python
x:int = 1
x:int, x > 0 = 1
```

Constant binding:

```python
const max_retries:int = 3
```

Delayed binding candidate:

```python
now := clock.time()
```

Possible meaning: `now` evaluates its right side each time it is used. This is
Mathematica-inspired and should remain candidate syntax because delayed
evaluation can harm local reasoning.

### Reduction

```python
const x:int = 1
```

reduces to:

```text
bind x to 1
validate int
mark binding as non-rebindable
```

```python
now := clock.time()
```

reduces to:

```text
bind now to a zero-argument delayed expression/function
evaluate on access
```

## 4. Type Hints, Contracts, And Guards

### Existing Forms

Python:

```python
def f(x: int) -> int:
    return x + 1
```

TypeScript:

```typescript
function f(x: number): number {
  return x + 1
}
```

Kotlin:

```kotlin
fun f(x: Int): Int = x + 1
```

Eiffel-style contract idea:

```text
require x > 0
ensure result > x
```

Rust:

```rust
fn f(x: i32) -> i32 { x + 1 }
```

Racket contracts:

```scheme
(-> integer? integer?)
```

### Observations

Type annotations are widely understood. Contracts are semantically valuable but
often syntactically heavy or external to the function signature.

### Nomi Synthesis

```python
func sqrt(x:(float, x >= 0)) -> float:
    ...
```

Named constraints:

```python
positive = (x) => x > 0

func charge(amount:(Money, positive)):
    ...
```

Postcondition candidate:

```python
func inc(x:int) -> result:(int, result > x):
    x + 1
```

Block contract candidate:

```python
func transfer(from, to, amount:(Money, amount > 0)):
    require from.balance >= amount
    ...
    ensure from.balance == old(from.balance) - amount
```

### Reduction

Constraints reduce to predicates checked at binding boundaries. Return
constraints are binding constraints on the implicit `result` binding.

## 5. Blocks, Closures, And Trailing Lambdas

### Existing Forms

Ruby:

```ruby
3.times do |i|
  puts i
end
```

Kotlin:

```kotlin
users.forEach { user ->
    println(user.name)
}
```

Scala:

```scala
users.foreach { user =>
  println(user.name)
}
```

JavaScript:

```javascript
users.forEach(user => {
  console.log(user.name)
})
```

Python:

```python
for user in users:
    print(user.name)
```

### Observations

Ruby/Kotlin/Scala are excellent at passing behavior into library calls. Python
is excellent at making loops visually explicit. Nomi should combine these:
library-defined control with Python-like indentation.

### Nomi Synthesis

```python
users.each() -> user:
    print(user.name)
```

```python
retry(3):
    send_request()
```

```python
transaction(db):
    create_user()
    send_email()
```

### Reduction

All reduce to calls with attached caller-side blocks. The block is invoked by
`yield` in the callee.

## 6. Context Managers, Resource Scope, And Cleanup

### Existing Forms

Python:

```python
with open(path) as f:
    data = f.read()
```

Ruby:

```ruby
File.open(path) do |f|
  data = f.read
end
```

C#:

```csharp
using var f = File.Open(path);
```

Go:

```go
defer file.Close()
```

Swift:

```swift
defer { cleanup() }
```

### Observations

Python's `with` is very readable but specialized. Ruby's block style generalizes
better. Go/Swift `defer` is useful inside functions, but can hide cleanup order.

### Nomi Synthesis

General block:

```python
using(open(path)) -> f:
    data = f.read()
```

Domain-specific helper:

```python
file(path) -> f:
    data = f.read()
```

Cleanup candidate:

```python
func write(path, text):
    f = open(path, "w")
    defer f.close()
    f.write(text)
```

### Reduction

`using(resource) -> x:` is a block call that yields the acquired value and
performs cleanup after the block returns or raises.

## 7. Pattern Matching And Destructuring

### Existing Forms

Python:

```python
match value:
    case {"name": name}:
        print(name)
```

Scala:

```scala
value match {
  case Some(x) => x
  case None => 0
}
```

Rust:

```rust
match result {
    Ok(value) => value,
    Err(error) => return Err(error),
}
```

Elixir:

```elixir
{:ok, value} = result
```

Haskell:

```haskell
case result of
  Just x -> x
  Nothing -> 0
```

Mathematica:

```wolfram
expr /. f[x_] -> x
```

### Observations

Pattern matching is one of the strongest cross-language ideas. The friction is
surface syntax: Python is readable but statement-oriented; Scala/Rust/Haskell
are powerful but visually less Python-like; Mathematica is extremely powerful
for symbolic expressions.

### Nomi Synthesis

Statement:

```python
match result:
    case Ok(value):
        use(value)
    case Err(error):
        report(error)
```

Expression:

```python
value = match result:
    case Ok(value):
        value
    case Err(error):
        default
```

Binding:

```python
Ok(value) = result
```

Constrained:

```python
case User(age:(int, age >= 18)):
    allow()
```

### Reduction

Patterns are shape tests plus binding. Match is ordered pattern testing with
optional guards.

## 8. Null, Option, Maybe, And Result

### Existing Forms

Python:

```python
if user is not None:
    city = user.address.city
```

Kotlin:

```kotlin
val city = user?.address?.city ?: "unknown"
```

Swift:

```swift
let city = user?.address?.city ?? "unknown"
```

Rust:

```rust
let city = user.and_then(|u| u.address).map(|a| a.city);
```

Haskell:

```haskell
case maybeUser of
  Just user -> ...
  Nothing -> ...
```

Scala:

```scala
user.map(_.address).map(_.city).getOrElse("unknown")
```

### Observations

Kotlin/Swift are best for everyday ergonomics. Rust/Haskell/Scala model absence
more explicitly. Python is readable but verbose and error-prone for nested
access.

### Nomi Synthesis

Everyday:

```python
city = user?.address?.city ?: "unknown"
```

Explicit:

```python
match user:
    case Some(user):
        user.address.city
    case None:
        "unknown"
```

Result:

```python
config = read_config(path)?
```

### Reduction

Safe access desugars to conditional match over empty/non-empty values. `?`
result propagation desugars to `match Ok/Err`.

## 9. Pipelines, Method Chains, And Postfix Application

### Existing Forms

Unix shell:

```sh
cat file | grep error | sort
```

F#:

```fsharp
text |> parse |> normalize |> summarize
```

Elixir:

```elixir
text |> parse() |> normalize() |> summarize()
```

Mathematica:

```wolfram
text // parse // normalize // summarize
```

Kotlin:

```kotlin
text.parse().normalize().summarize()
```

Python:

```python
summarize(normalize(parse(text)))
```

### Observations

Pipelines are best when the dataflow matters more than nesting. Method chains
are readable when operations naturally belong to the receiver. Python nested
calls become hard to scan.

### Nomi Synthesis

```python
summary = text |> parse |> normalize |> summarize
```

With placeholders:

```python
summary = text |> parse(mode="loose", _) |> summarize(style="short", _)
```

With collection operations:

```python
names = users |> filter(_, active) |> map(_, name) |> sort
```

### Reduction

`x |> f` becomes `f(x)`. `x |> f(_, y)` becomes `f(x, y)`.

## 10. Comprehensions, Maps, Queries, And Array Thinking

### Existing Forms

Python:

```python
[x * 2 for x in xs if x > 0]
```

Haskell:

```haskell
[x * 2 | x <- xs, x > 0]
```

Scala:

```scala
for x <- xs if x > 0 yield x * 2
```

LINQ:

```csharp
from x in xs
where x > 0
select x * 2
```

APL:

```apl
2 * xs
```

Mathematica:

```wolfram
Select[xs, # > 0 &] * 2
```

### Observations

Python comprehensions are compact and readable for simple cases. LINQ/query
syntax is excellent for tabular domains. APL is extremely concise for arrays but
not self-explanatory to broad audiences.

### Nomi Synthesis

Comprehension:

```python
doubles = [x * 2 for x in xs if x > 0]
```

Pipeline:

```python
doubles = xs |> filter(_, (x) => x > 0) |> map(_, (x) => x * 2)
```

Query candidate:

```python
query users -> u:
    where u.active
    select u.name
    order by u.name
```

Array shorthand candidate:

```python
ys = xs.*2
```

### Reduction

All reduce to iteration, binding, predicate calls, and result construction.

## 11. Data Modeling

### Existing Forms

Python dataclass:

```python
@dataclass
class User:
    id: int
    name: str
```

Kotlin:

```kotlin
data class User(val id: Int, val name: String)
```

Scala:

```scala
case class User(id: Int, name: String)
```

Rust:

```rust
struct User {
    id: i32,
    name: String,
}
```

Haskell:

```haskell
data User = User { id :: Int, name :: String }
```

### Observations

Kotlin/Scala are strongest for concise value data. Python dataclasses are useful
but decorator-plus-class is a workaround. Rust/Haskell are explicit but heavier
for everyday scripting.

### Nomi Synthesis

```python
data User(id:int, name:str, active:bool = True)
```

Pattern:

```python
case User(id, name, active=True):
    ...
```

Copy/update candidate:

```python
new_user = user with {active = False}
```

### Reduction

Data declarations bind a constructor, field accessors, equality, representation,
and pattern shape.

## 12. Traits, Protocols, Typeclasses, And Interfaces

### Existing Forms

Java/Kotlin:

```kotlin
interface Drawable {
    fun draw(canvas: Canvas)
}
```

Rust:

```rust
trait Drawable {
    fn draw(&self, canvas: Canvas);
}
```

Haskell:

```haskell
class Drawable a where
  draw :: a -> Canvas -> Canvas
```

Python:

```python
class Drawable(Protocol):
    def draw(self, canvas): ...
```

Scala:

```scala
trait Drawable {
  def draw(canvas: Canvas): Unit
}
```

### Observations

These features all express named behavioral expectations. The main difference is
nominal versus structural matching and whether implementation is attached to the
type or discovered externally.

### Nomi Synthesis

Nominal-ish:

```python
trait Drawable:
    func draw(self, canvas)

impl Drawable for Circle:
    func draw(self, canvas):
        canvas.circle(self.center, self.radius)
```

Structural:

```python
protocol Drawable:
    func draw(self, canvas)
```

### Reduction

Traits/protocols are named sets of function constraints. `impl` binds functions
into a dispatch table or capability scope.

## 13. Extension Methods And Open Functions

### Existing Forms

Kotlin:

```kotlin
fun String.words(): List<String> = split(" ")
```

Scala:

```scala
extension (s: String)
  def words = s.split(" ")
```

C#:

```csharp
public static Words(this string s) { ... }
```

Ruby:

```ruby
class String
  def words
    split(" ")
  end
end
```

### Observations

Extension methods improve fluent APIs. Ruby's monkey patching is powerful but
globally risky. Kotlin/Scala keep extensions more scoped.

### Nomi Synthesis

```python
func String.words(self):
    self.split(" ")
```

Use:

```python
"a b c".words()
```

Scoped import:

```python
use text.extensions.words
```

### Reduction

Method syntax reduces to a function call with receiver as first argument, using
module-visible extension lookup.

## 14. Macros, Templates, And Code Generation

### Existing Forms

Lisp:

```scheme
(define-syntax unless
  ...)
```

Rust:

```rust
println!("x = {}", x);
```

Template Haskell:

```haskell
$(deriveJSON ''User)
```

Scala:

```scala
inline def ...
```

Mathematica:

```wolfram
Hold[expr]
```

### Observations

Macros are useful when the language can represent code as data. They are also
one of the easiest ways to destroy local readability.

### Nomi Synthesis

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

### Reduction

Macros are functions from quoted expression values to quoted expression values,
expanded in explicit macro scope.

## 15. Symbolic Rewrite And Rule-Based Programming

### Existing Forms

Mathematica:

```wolfram
expr /. x_ + 0 -> x
expr //. rules
```

Prolog:

```prolog
ancestor(X, Y) :- parent(X, Z), ancestor(Z, Y).
```

Stratego/rewrite systems:

```text
Plus(x, Zero) -> x
```

Lisp:

```scheme
(match expr
  [`(+ ,x 0) x])
```

### Observations

Rewrite systems are excellent for symbolic domains, compilers, optimizers, and
mathematics. They should operate over explicit expression data, not ordinary
runtime code invisibly.

### Nomi Synthesis

```python
expr = quote:
    (x + 0) * 1

normal = expr //. [
    x + 0 -> x,
    x * 1 -> x,
]
```

### Reduction

Rules are pattern functions over expression values. `/.` applies once; `//.`
applies until stable.

## 16. Error Handling

### Existing Forms

Python:

```python
try:
    work()
except Error as e:
    recover(e)
```

Go:

```go
value, err := work()
if err != nil { return err }
```

Rust:

```rust
let value = work()?;
```

Swift:

```swift
let value = try work()
```

Haskell:

```haskell
Either Error Value
```

### Observations

Exceptions are readable for exceptional control. Result values are better when
failure is part of the ordinary API contract. Go is explicit but repetitive.
Rust is concise because the `?` operator has a clear `Result` model.

### Nomi Synthesis

Exceptions:

```python
try:
    work()
except Error as e:
    recover(e)
```

Result:

```python
value = work()?
```

Pattern:

```python
match work():
    case Ok(value):
        use(value)
    case Err(error):
        recover(error)
```

### Reduction

`?` is syntax over `match Ok/Err` and early return from the current function.

## 17. Modules, Imports, And Capability Scope

### Existing Forms

Python:

```python
from math import sqrt
```

Rust:

```rust
use std::collections::HashMap;
```

Haskell:

```haskell
import qualified Data.Map as Map
```

JavaScript:

```javascript
import { sqrt } from "math"
```

### Observations

Imports do more than bring names into scope. They may also bring extension
methods, traits, macros, and rewrite rules. Nomi should make such capabilities
visible.

### Nomi Synthesis

```python
import math
from math import sqrt
use text.extensions.words
use symbolic.algebra.rules as algebra
```

### Reduction

`import` binds names. `use` brings scoped capabilities into the current module:
extensions, traits, macros, or rules.

## 18. Summary Matrix

| Need | Python | Ruby | Scala/Kotlin | Lisp/Mathematica/APL | Proposed Nomi |
| --- | --- | --- | --- | --- | --- |
| Function | `def` | `def` | `def` / `fun` | `define`, `f[x_] :=` | `func` |
| Function value | `lambda` | `-> {}` | `=>`, `{ -> }` | `lambda`, pure funcs | `(x) => expr` |
| Block control | `with`, loops | `do/end` blocks | trailing lambdas | higher-order funcs | `call(args): block` |
| Binding constraints | hints only | dynamic | types | predicates/patterns | `x:int, pred = v` |
| Pattern matching | `match` | limited | strong | symbolic patterns | `match`, pattern binding |
| Pipeline | nested calls | method chains | chains | `//`, array flow | `value |> f` |
| Data values | dataclass | Struct | data/case class | records/expressions | `data User(...)` |
| Null safety | manual | nil chaining | `?.`, `?:` | Maybe-like | `?.`, `?:`, match |
| Symbolic rewrite | AST libs | metaprogramming | macros/libs | native rules | `quote`, `/.`, `//.` |

The synthesis is intentionally conservative at the core and ambitious at the
surface. Each proposed surface form should remain peelable back to primitives.
