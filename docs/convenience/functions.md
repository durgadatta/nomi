# Function Convenience Across Languages

Research notes on syntactic shortcuts for defining functions — what
exists, what Nomi has, and what could be added long-term.  Each section
describes the mechanism, shows examples in the source language, and
maps to a possible Nomi form.

---

## 1. Lightweight Equations

**Haskell**: `f a b = expr` (no `=`, just whitespace parameters)

```haskell
add a b = a + b
const x _ = x
```

**Nomi** (implemented): `f(a, b) = expr`

```nomi
add(a, b) = a + b
pi() = 3.14
```

**Future**: allow single-argument equations without parens: `double x = x * 2`

---

## 2. Pattern-Matching / Piecewise Definitions

**Haskell**: multiple equations with patterns, tried top-to-bottom

```haskell
fact 0 = 1
fact n = n * fact (n - 1)

fib 0 = 0
fib 1 = 1
fib n = fib (n - 1) + fib (n - 2)

-- multi-arg
and True  True  = True
and _     _     = False

-- guards
sign n | n > 0     = 1
       | n < 0     = -1
       | otherwise = 0
```

**Elixir**: multiple clauses with pattern matching

```elixir
def fact(0), do: 1
def fact(n), do: n * fact(n - 1)
```

**Nomi** (implemented): contiguous equations merged into match dispatch

```nomi
fact(1) = 1
fact(n) = fact(n - 1) * n
```

**Future**: guard clauses (`|` syntax), multi-arg patterns, wildcards in patterns

---

## 3. Lambda / Anonymous Function Shortcuts

### 3a. Arrow Functions

**JavaScript / TypeScript / Kotlin**:

```javascript
const add = (a, b) => a + b
```

**Nomi** (implemented):

```nomi
add = (a, b) => a + b
```

### 3b. Underscore / Hole-Filling

**Scala**: `_` as placeholder, scope extends to smallest enclosing expression

```scala
list.map(_.name)           // (x) => x.name
list.filter(_.age > 18)    // (x) => x.age > 18
list.reduce(_ + _)         // (x, y) => x + y
"hello".map(_.toUpper)     // (x) => x.toUpper
```

**Kotlin**: `it` as implicit single-parameter name

```kotlin
list.map { it.name }
list.filter { it.age > 18 }
list.reduce { acc, it -> acc + it }
```

**Swift**: `$0`, `$1`, ... as positional shorthand

```swift
list.map { $0.name }
list.reduce(0) { $0 + $1 }
list.sorted { $0.age < $1.age }
```

**Nomi** (implemented): `_` as hole

```nomi
_.upper()           // (x) => x.upper()
_ + 1               // (x) => x + 1
_ + _               // (x, y) => x + y
list.map(_.name)    // list.map((x) => x.name)
```

**Future**: Swift-style positional `$1`, Kotlin-style `it` as alternative

### 3c. Operator Sections (Partial Application)

**Haskell**: binary operator with one operand missing

```haskell
(+2)        -- \x -> x + 2
(2*)        -- \x -> 2 * x
(/)         -- \x y -> x / y  (operator as function)
map (*2) [1,2,3]  -- [2,4,6]
filter (>5) [1..10]  -- [6,7,8,9,10]
```

**Scala**: same via underscore holes

```scala
_ + 2          // (x) => x + 2
2 * _          // (x) => 2 * x
```

**F#**: same

```fsharp
(+) 2 3       // 5
List.map ((*) 2) [1;2;3]  // [2;4;6]
```

**Nomi** (not yet implemented):

Proposed syntax:
```nomi
(+2)        // (x) => x + 2
(2*)        // (x) => 2 * x
(+)         // (x, y) => x + y  (operator as value)
```

---

## 4. Where Clauses (Local Bindings)

**Haskell**: `where` introduces local bindings after an expression

```haskell
area = pi * r * r
  where
    pi = 3.14159
    r = 5

roots a b c = ( (-b + sqrt disc) / (2*a),
               (-b - sqrt disc) / (2*a) )
  where
    disc = b*b - 4*a*c
```

**Elixir / F#**: `let ... in` (before, not after)

```fsharp
let pi = 3.14159
let r = 5
area = pi * r * r
```

**Nomi** (implemented):

```nomi
area = pi * r * r where:
    pi = 3.14159
    r = 5

# mixed with other forms
scaled = double(x) + 1 where:
    double = _ * 2
    x = 5
```

**Future**: multi-line where for compound statements, `where` on any expression

---

## 5. Function Composition

**Haskell**: `.` operator for composition

```haskell
process = sort . filter (>0) . map (*2)
-- process xs = sort (filter (>0) (map (*2) xs))
```

**F#**: `>>` and `<<` operators

```fsharp
let process = (List.map ((*) 2)) >> (List.filter (fun x -> x > 0)) >> List.sort
```

**Elm / Roc**: `>>` and `<<`

```elm
process = List.sort << List.filter (\x -> x > 0) << List.map ((*) 2)
```

**Nomi** (not yet implemented):

Proposed syntax:
```nomi
process = sort << filter(_ > 0) << map(_ * 2)
# or
process = data |> map(_ * 2) |> filter(_ > 0) |> sort
```

---

## 6. Method / Extension Function Syntax

**Kotlin**: extension functions and receiver lambdas

```kotlin
fun String.greet() = "Hello, $this"

// receiver lambda
html {
    head { title("Page") }
    body { p("content") }
}
```

**Swift**: same

```swift
extension String {
    func greet() -> String { "Hello, \(self)" }
}
```

**Nomi** (not yet implemented):

Proposed syntax using `_` hole + method chain:
```nomi
greet = "Hello, " + _  // already works

// extension-style (future)
func String.greet():
    return "Hello, " + this
```

---

## 7. Named / Labeled Arguments

**Swift / Kotlin / C#**: labeled parameters at call site

```swift
func move(from start: Point, to end: Point) { ... }
move(from: a, to: b)
```

**OCaml**: labeled arguments

```ocaml
let move ~from ~to = ...
move ~from:a ~to:b
```

**Nomi** (partially supported): named arguments at call site

```nomi
func move(from, to):
    ...
move(from=a, to=b)  # works via keyword arguments
```

---

## 8. Default / Optional Parameters

**Most languages**: `=` to provide default

```python
def greet(name="world"):
    return f"Hello, {name}"
```

**Kotlin**: same, with named-arg calls

```kotlin
fun greet(name: String = "world") = "Hello, $name"
greet(name = "alice")
```

**Nomi** (partially supported): `func` supports defaults; `f(a, b)=expr` does not yet

```nomi
func greet(name="world"):
    return "Hello, " + name
```

---

## 9. Variadic Functions

**Python**: `*args` and `**kwargs`

```python
def sum_all(*args):
    return sum(args)
```

**Nomi** (supported): same via `*args`

```nomi
func sum_all(*args):
    return sum(args)
```

---

## 10. Currying / Partial Application

**Haskell**: automatic currying (every function is curried)

```haskell
add :: Int -> Int -> Int
add x y = x + y
add3 = add 3   -- Int -> Int
add3 5         -- 8
```

**F#**: same

```fsharp
let add x y = x + y
let add3 = add 3
add3 5  // 8
```

**Nomi** (not yet implemented):

Proposed:
```nomi
add = (x, y) => x + y
add3 = add(3, _)    // partial application
add3(5)             // 8
```

---

## 11. Block / Trailing Lambda Syntax

**Ruby**: block attached to method calls

```ruby
[1,2,3].map { |x| x * 2 }
[1,2,3].each { |x| puts x }

# with do..end
file.open do |f|
    f.write("hello")
end
```

**Kotlin**: trailing lambda convention

```kotlin
list.map { it * 2 }
list.filter { it > 0 }
```

**Nomi** (implemented): `block_call_stmt` for yield-to-block

```nomi
times(3) -> counter:
    print(f"Count: {counter}")

each(items) -> item:
    print(f"Item: {item}")
```

---

## 12. Point-Free / Tacit Programming

**Haskell**: point-free style omits parameters entirely

```haskell
sum = foldr (+) 0          -- no explicit parameter
length = foldr (\_ n -> n + 1) 0
compose = (.)

-- combinators
apply f x = f x
flip f x y = f y x
```

**J / APL**: extreme point-free (tacit) via forks and hooks

```j
mean =: +/ % #              NB. sum divided by count
```

**Nomi** (not yet implemented):

Point-free can be approximated with `_` holes:
```nomi
sum = foldr(_ + _, 0)
```

But true point-free would require richer combinators.

---

## 13. Match / Case as Function Body

**Haskell / Rust / OCaml**: `function` keyword for immediate pattern match

```haskell
-- Haskell
describe = \case
    0 -> "zero"
    1 -> "one"
    n -> "many"
```

```rust
// Rust
let describe = |n| match n {
    0 => "zero",
    1 => "one",
    _ => "many",
};
```

**Nomi** (not yet implemented):

Proposed:
```nomi
describe = match:
    case 0: return "zero"
    case 1: return "one"
    case n: return "many"
```

---

## 14. Do-Notation / Comprehension Sugar

**Haskell**: `do` notation for monadic chains

```haskell
result = do
    x <- action1
    y <- action2 x
    return (x + y)
```

**Scala**: `for` comprehensions

```scala
for {
    x <- action1
    y <- action2(x)
} yield x + y
```

**Nomi** (not yet implemented):

Could desugar to yield-to-block or flatMap chains.

---

## 15. Implicit / Context Parameters

**Scala**: `given` / `using` for implicit context

```scala
def sort[T](list: List[T])(using ord: Ordering[T]) = ...

given Ordering[Int] = Ordering.Int
sort(List(3, 1, 2))  // ord passed implicitly
```

**Kotlin**: context receivers

**Nomi** (Track 7): capability scopes, `world` values

---

## 16. Other Languages — Function Shortcuts Survey

A research catalogue of how different language traditions create functions
concisely.  Source material for future convenience features.

### Implicit Parameters

| Language | Form | Mechanism |
|----------|------|-----------|
| Scala | `_.name`, `_ + _` | Underscore holes (Nomi adopted) |
| Swift | `$0`, `$1`, ... | Positional dollar holes (Nomi adopted) |
| Kotlin | `it` | Implicit single-param name in trailing lambda |
| Elixir | `&(&1 + &2)` | `&` capture operator, `&1`, `&2` positional |
| F# | `fun x y -> x + y` | Lightweight lambda keyword |

### Explicit Lambdas

| Language | Form | Expression body? |
|----------|------|------------------|
| Nomi | `x => expr`, `(x,y) => expr` | Yes |
| JS/TS | `(x, y) => expr` | Yes |
| Rust | `\|x\| x + 1`, `\|x, y\| { ... }` | Single-expression or block |
| Ruby | `{ \|x\| x + 1 }`, `-> (x) { x + 1 }` | Block or stabby lambda |
| C++ | `[](int x) { return x + 1; }` | Block only |
| Java | `(x) -> x + 1`, `String::length` | Expression or method ref |
| Python | `lambda x: x + 1` | Expression only |

### Operator / Expression Shorthands

| Language | Form | What it does |
|----------|------|-------------|
| Haskell | `(+2)`, `(2*)`, `(+)` | Operator sections (Nomi adopted) |
| Haskell | `f . g` | Function composition |
| F# / Elm / Roc | `f >> g`, `f << g` | Forward/backward composition |
| Java | `String::length` | Method reference → function |
| Swift | `\Type.method` | Key-path as function reference |
| Python | `functools.partial(f, x)` | Partial application |
| J / APL | `+/ % #` | Point-free (tacit) via forks & hooks |

### Blocks as Functions

| Language | Form | Yield points |
|----------|------|-------------|
| Ruby | `method { \|x\| x + 1 }` | Block attached to call |
| Kotlin | `method { it + 1 }` | Trailing lambda convention |
| Nomi | `method() -> x: body` | Explicit yield-to-block (implemented) |
| Groovy | `method { x -> x + 1 }` | Closure blocks |

### Tacit / Point-Free

| Language | Form | Mechanism |
|----------|------|-----------|
| J / APL | `mean =: +/ % #` | Forks (pair) and hooks |
| Haskell | `sum = foldr (+) 0` | Currying + sections |
| Joy / Factor | `[dup *]` | Concatenative (stack-based) |

### Candidates for Future Nomi

| Idea | Source | Viability |
|------|--------|-----------|
| `it` as implicit lambda param (top-level) | Kotlin | Simple, conflicts with var name |
| `&` capture operator | Elixir | High effort, overlaps with `$N` |
| `String::length` method refs | Java/Swift | Medium, needs type info |
| `>>` / `<<` composition | F#/Elm | Conflicts with bit-shift operators |
| `.` composition | Haskell | High effort syntax change |
| `partial(f, x)` built-in | Python | Simple, library-level |

---

## Priority Order for Nomi

What to add next, roughly in order of impact:

| # | Feature | Effort | Impact | Status |
|---|---------|--------|--------|--------|
| 1 | Operator sections `(+2)`, `(2*)`, `(+)` | low | high | **done** |
| 2 | `$1`, `$2` positional hole (Swift-style) | low | medium | **done** |
| 3 | `$name` named hole | low | medium | **done** |
| 4 | Guards in piecewise `when n > 0` | medium | high | **done** |
| 5 | Function composition `>>>`, `<<<` | low | high | **done** |
| 6 | Single-arg equation without parens `double x = x*2` | low | medium | **done** |
| 7 | `match` as expression (return value) | medium | high | not started |
| 8 | Defaults in equation args `f(a, b=2) = a+b` | medium | medium | **done** |
| 9 | Currying / partial application `f(_, b)` | medium | medium | not started |
| 10 | Multi-line `where` for compound stmts | medium | medium | not started |
| 11 | `function` / `\case` keyword | low | medium | not started |
| 12 | Point-free combinators | high | low | not started |
| 13 | Do-notation / monad sugar | high | low | not started |
| 14 | Implicit parameters | high | low | not started |
