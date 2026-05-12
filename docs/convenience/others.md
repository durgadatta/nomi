# Miscellaneous & Niche Conveniences

Smaller features and cross-language oddities that don't yet warrant a
full doc.  Grouped by language or theme.  May be promoted later.

---

## Go — Simplicity Through Constraint

### Short Variable Declaration `:=`

```go
x := 42                    // declare + infer type
name := "hello"
items := []int{1, 2, 3}
```

Saves `var x int = 42`.  In a Python-like language this is less useful
(type inference already exists), but the walrus operator `:=` for
expression-assignment (Python 3.8) is related.

### Multiple Return Values

```go
func divmod(a, b int) (int, int) { return a / b, a % b }
q, r := divmod(10, 3)     // q=3, r=1
```

**Nomi** — implicit tuple returns already work.

### Defer

```go
defer file.Close()         // runs when enclosing function returns
defer mu.Unlock()
```

LIFO execution of deferred calls on scope exit.  Cleaner than `try/finally`.

### Blank Identifier `_`

```go
for _, v := range items { ... }
val, _ := returnsTwo()
```

**Nomi** — `_` is a regular identifier already used for holes + wildcards.

---

## Rust — Safety Through Ownership (Not Sugars)

Rust's conveniences are mostly type-system and ownership features, not
syntax sugar.  A few are portable:

### `if let` / `while let`

```rust
if let Some(value) = optional {
    println!("{value}");
}
while let Some(item) = iter.next() {
    process(item);
}
```

**Nomi** — covered in [patterns.md](patterns.md).

### Match Ergonomics

```rust
match &optional {
    Some(v) => ...     // auto-deref
    None => ...
}
```

### Range Syntax `..`, `..=`

```rust
0..10       // exclusive: 0,1,...,9
1..=10      // inclusive: 1,2,...,10
(0..10).step_by(2)
```

### `?` Error Propagation

```rust
let val = fallible()?;   // unwrap Ok, or return Err
```

**Nomi** — covered in [error_handling.md](error_handling.md).

### Closures `|x| x + 1`

```rust
let add_one = |x| x + 1;
let sum = |a, b| a + b;
```

`||` syntax is unusual.  Nomi uses `=>`.

---

## Ruby — Everything Is an Expression

### Blocks with `do..end` and `{ }`

```ruby
[1,2,3].map { |x| x * 2 }
[1,2,3].each do |x|
    puts x
end
```

### `unless` / `until` (Inverted Conditionals)

```ruby
puts "cold" unless temp > 20
sleep until ready?
```

**Nomi proposal** — syntactic sugar:

```nomi
print("ok") unless error
```

### `%w`, `%i`, `%q` (Percent Literals)

```ruby
%w[alice bob carol]       // → ["alice", "bob", "carol"]
%i[alice bob]              // → [:alice, :bob]  (symbols)
%q(no "escaping" needed)   // → 'no "escaping" needed'
```

Not portable to a Python-like language.

### Safe Navigation `&.`

```ruby
user&.address&.city        // nil-safe chaining
obj&.method
```

**Nomi** — covered in [null_handling.md](null_handling.md), as `?.`.

### Postfix `if`/`unless` as Expression Modifier

```ruby
return unless user
x = compute if flag
```

Single-line conditional for early return / guard.

---

## TypeScript / JavaScript — Modern Web Sugar

### Optional Chaining `?.`

```typescript
const city = user?.address?.city
const first = arr?.[0]
const result = obj?.method?.()
```

**Nomi** — covered in [null_handling.md](null_handling.md).

### Nullish Coalescing `??`

```typescript
const name = input ?? "default"
```

### Destructuring with Defaults and Renames

```typescript
const { name: userName = "anon", age } = obj
const [first, , third = 0] = arr
```

### Spread / Rest

```typescript
const combined = [...a, ...b]
const { a, ...rest } = obj
function f(x, ...rest) { }
```

### Template Literals

```typescript
`Hello ${name}, you are ${age + 1} next year`
```

Tagged templates for DSLs:
```typescript
sql`SELECT * FROM users WHERE id = ${id}`
```

### Arrow Functions

```typescript
const add = (a, b) => a + b
const square = x => x * x     // parens optional for single param
```

**Nomi** — `(x) => x * x` already supported.  Single-param `x => x * x`
(no parens) could be added.

---

## Swift — Safety + Readability

### Argument Labels

```swift
func move(from start: Point, to end: Point) { ... }
move(from: a, to: b)
```

External label vs internal name.  Adds clarity at call site.

### Trailing Closure Syntax

```swift
list.map { $0 * 2 }
list.filter { $0 > 5 }
```

No parens needed when the last argument is a closure.

### `$0`, `$1` Positional Parameters

```swift
list.map { $0 * 2 }
list.reduce(0) { $0 + $1 }
list.sorted { $0.age < $1.age }
```

**Nomi** — `_` holes cover this.  `$1` for second parameter could be added.

### `guard let` (Early Exit)

```swift
guard let value = optional else { return }
// value is bound here
```

**Nomi** — covered in [patterns.md](patterns.md).

### `defer`

```swift
defer { file.close() }
```

### `@discardableResult`, `@frozen`, `@inlinable`

**Nomi** — decorators already work.  Attribute semantics differ.

---

## Elixir — Functional + Macro + Pipe

### Pipeline `|>`

```elixir
[1,2,3,4,5]
|> Enum.map(&(&1 * 2))
|> Enum.filter(&(&1 > 5))
|> Enum.sum()
```

**Nomi** — covered in [collections.md](collections.md).

### Capture Operator `&`

```elixir
&(&1 + 1)          // → fn x -> x + 1 end
&String.upcase/1   // → &String.upcase(&1)
&(&1 + &2)         // → fn x, y -> x + y end
```

**Nomi** — `_ + 1`, `_ + _` (implemented).

### Pattern Matching Everywhere

```elixir
{:ok, result} = operation()     // crashes if not :ok tuple
[head | tail] = list
%{name: n} = person
```

Pattern matching in assignment is a powerful Elixir idiom.

### `with` for Chained Operations

```elixir
with {:ok, a} <- step1(),
     {:ok, b} <- step2(a),
     {:ok, c} <- step3(b) do
  {:ok, c}
else
  {:error, reason} -> {:error, reason}
end
```

Chain of fallible operations — short-circuits on first error.
Similar to Rust's `?` or Haskell's `do` notation.

### Guard Clauses on Functions

```elixir
def sign(n) when n > 0, do: 1
def sign(n) when n < 0, do: -1
def sign(0), do: 0
```

**Nomi** — piecewise functions already do this.  Guards (`when n > 0`)
not yet supported.

---

## Scala — Type-Level Sugar

### Implicit Parameters / Given

```scala
def sort[T](list: List[T])(using ord: Ordering[T]): List[T] = ...
given Ordering[Int] = Ordering.Int
sort(List(3, 1, 2))
```

**Nomi** — Track 7.

### `for` Comprehensions (Monadic)

```scala
for {
    x <- option1
    y <- option2(x)
} yield x + y
```

Desugars to `flatMap`/`map`.

### Extension Methods

```scala
extension (s: String)
    def isPalindrome: Boolean = s == s.reverse
```

**Nomi** — see [types.md](types.md).

### Infix Types

```scala
type \/[A, B] = Either[A, B]
val x: String \/ Int = Right(42)
```

### `@main` Annotation

```scala
@main def hello(name: String) = println(s"Hello $name")
```

---

## Haskell — Purity + Type Classes

### List Comprehensions

```haskell
[x * 2 | x <- [0..9], even x]
```

### Sections `(+2)`, `(2*)`, `(+)`

**Nomi** — implemented.

### `where` and `let..in`

**Nomi** — `where` implemented.  `let..in` = same, before expression.

### Guards

```haskell
sign n | n > 0     = 1
       | n < 0     = -1
       | otherwise = 0
```

### `$` (Low-Precedence Application)

```haskell
print $ sum $ map (*2) [1..10]
-- same as: print (sum (map (*2) [1..10]))
```

Avoids parentheses in deeply nested application.

### `.` (Function Composition)

```haskell
process = sort . filter (>0) . map (*2)
```

**Nomi** — `<<` / `>>` planned.

---

## Pascal / Delphi — Classic Sugar

### `with` Statement (Record Field Shorthand)

```pascal
with person do begin
    Name := 'Alice';
    Age := 30;
end;
```

Brings record fields into scope.  Controversial (field ambiguity).

### Sets and `in`

```pascal
if ch in ['A'..'Z', 'a'..'z'] then ...
```

### `:=` Assignment, `=` Comparison

```pascal
x := 42;
if x = 42 then ...
```

Visual distinction between mutation and equality.

---

## SQL — Declarative Data

### `SELECT ... WHERE ... GROUP BY`

The original declarative data language.  Q's array-SQL, LINQ, and
dataframe APIs all derive from it.

### `WITH` (CTE — Common Table Expressions)

```sql
WITH active_users AS (
    SELECT * FROM users WHERE active = 1
)
SELECT * FROM active_users WHERE age > 18
```

Named subqueries for readability — essentially local bindings.

---

## PowerShell — Object Pipeline

### Pipeline with `|`

```powershell
Get-ChildItem | Where-Object { $_.Length -gt 1MB } | Sort-Object Length
```

Objects, not text, flow through the pipeline.  `$_` is the current item
(like Scala's `_`).

### `$_` and `$PSItem` (Current Pipeline Object)

```powershell
1..10 | ForEach-Object { $_ * 2 }
```

### `%` and `?` as Aliases

```powershell
dir | % { $_.Name }           // ForEach-Object
dir | ? { $_.Length -gt 0 }   // Where-Object
```

### Range `1..10`

```powershell
1..10 | % { $_ * $_ }
```

---

## .NET / C# — LINQ and More

### LINQ Query Syntax

```csharp
var result = from u in users
             where u.Age > 18
             orderby u.Name
             select u.Name;
```

Language-level SQL-like queries.  Desugars to method calls.

### `??` and `??=`

```csharp
var name = input ?? "default";
list ??= new List<int>();
```

### `?.` and `?[]` Null-Conditional

```csharp
var city = user?.Address?.City;
var first = arr?[0];
```

### Expression-Bodied Members

```csharp
int Double(int x) => x * 2;
string Name => $"{First} {Last}";
```

### `nameof()`

```csharp
string name = nameof(user.Age);   // "Age"  (compile-time)
```

---

## R — Statistical Computing

### `%>%` Pipe

```r
data %>%
    filter(age > 18) %>%
    select(name, age) %>%
    arrange(age)
```

### `~` Formula

```r
lm(y ~ x1 + x2, data = df)       // y modeled by x1 + x2
y ~ .                              // all predictors
```

### `%in%`

```r
x %in% c("a", "b", "c")           // membership test
```

### `1:10` and `seq()`

```r
1:10                              // 1 2 3 4 5 6 7 8 9 10
seq(1, 10, by = 2)               // 1 3 5 7 9
```

### Non-Standard Evaluation (Tidyverse)

```r
filter(df, age > 18)   // age resolved in df scope, no df$age needed
```

Columns treated as variables in the data context.

---

## Academic / Research Languages

### Agda / Idris — Dependent Types + Interactive Editing

```idris
data Vect : Nat -> Type -> Type where
    Nil  : Vect 0 a
    (::) : a -> Vect n a -> Vect (S n) a

append : Vect n a -> Vect m a -> Vect (n + m) a
```

Types depend on values.  Interactive "holes" for incremental development.

### Unison — Content-Addressed Code

```unison
unique type Token = Open | Close
```

Code identified by hash, not name.  No builds — code is immutable.

### Darklang — Deployless / Trace-Driven Development

No infrastructure.  Code == deployment.  Every execution traces values.

### Koka / Eff — Algebraic Effects

```koka
effect ask {
    fun ask() : string
}

fun greet() : ask () {
    println("Hello, " ++ ask())
}
```

Effects tracked in types.  No monad transformers needed.

### Flix — Datalog Constraints

```flix
def reachable(g: List[(Int, Int)], src: Int, dst: Int): Bool =
    let edges = inject g;
    Path(x, y) :- edges(x, y).
    Path(x, z) :- Path(x, y), edges(y, z).
    Path(src, dst) |> check
```

Datalog-style rules embedded in a functional language.

### Verse (Epic Games) — Spatial/Temporal Logic

```verse
MovePlayer(Agent) :=
    race:
        UpdatePosition(Agent)
        CheckCollision(Agent)
```

Built-in temporal reasoning for game logic.

### Intentional Programming / Projectional Editing

Not a language, but a paradigm: edit the AST directly, not text.
Syntax is a rendering, not the source of truth.  Enables multiple
notations for the same code.

### ColorForth / Piet — Visual / Non-Textual

Esoteric, but the idea that notation can be non-textual has
implications for tooling (structural editors, visual programming).

### Pony — Reference Capabilities

```pony
actor Main
    new create(env: Env) =>
        env.out.print("Hello, world!")
```

Six reference capabilities (`iso`, `val`, `ref`, `box`, `trn`, `tag`).
No data races.  No deadlocks.

### Whiley — Verifying Compiler

```whiley
function sum(int[] xs) -> (int r)
ensures r >= 0:
    ...
```

Pre/post conditions verified at compile time.

---
