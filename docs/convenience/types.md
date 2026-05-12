# Type System Convenience

## Type Aliases

Short names for complex types.

**Kotlin / Swift / Rust / TypeScript**:

```kotlin
typealias UserId = String
typealias Callback = (Int, String) -> Boolean
typealias UserMap = Map<UserId, User>
```

```rust
type UserId = String;
type Callback = fn(i32, &str) -> bool;
type UserMap = HashMap<UserId, User>;
```

**Nomi proposal**:

```nomi
type UserId = str
type Callback = (int, str) -> bool
```

---

## Data / Value Classes

Classes that auto-generate constructors, field access, equality, display,
copy, and destructuring.

**Kotlin**:

```kotlin
data class Point(val x: Int, val y: Int)
val p = Point(1, 2)
val (x, y) = p              // destructuring
println(p)                   // Point(x=1, y=2)
p.copy(y = 3)               // Point(x=1, y=3)
p == Point(1, 2)            // true
```

**Scala (case class)**:

```scala
case class Point(x: Int, y: Int)
val p = Point(1, 2)
p.copy(y = 3)
```

**Rust (derive)**:

```rust
#[derive(Debug, Clone, PartialEq)]
struct Point { x: i32, y: i32 }
```

**Nomi** (Track 4):

```nomi
data Point(x: int, y: int)
p = Point(1, 2)
x, y = p    # destructuring
```

---

## Extension Functions / Methods

Add methods to existing types without modifying their source.

**Kotlin / Swift / C# / Rust (impl)**:

```kotlin
fun String.isPalindrome(): Boolean = this == this.reversed()
"racecar".isPalindrome()  // true

fun Int.squared(): Int = this * this
5.squared()               // 25
```

```swift
extension String {
    var isPalindrome: Bool { self == String(self.reversed()) }
}
```

```rust
impl StringExt for str {
    fn is_palindrome(&self) -> bool { ... }
}
```

**Nomi proposal**:

```nomi
func str.is_palindrome() -> bool:
    return this == this.reversed()

func int.squared() -> int:
    return this * this
```

The `this` keyword refers to the receiver.  Desugars to a regular function
that takes the receiver as the first argument, but callable with `.` syntax.

---

## Operator Overloading

Define `+`, `-`, `*`, `[]`, `()` etc. for user types.

**Kotlin / Rust / Swift / C++ / Haskell**:

```kotlin
data class Vector(val x: Int, val y: Int) {
    operator fun plus(other: Vector) = Vector(x + other.x, y + other.y)
    operator fun get(index: Int) = if (index == 0) x else y
}
val v3 = v1 + v2
val x = v3[0]
```

```haskell
instance Num Vector where
    Vector x1 y1 + Vector x2 y2 = Vector (x1 + x2) (y1 + y2)
```

**Nomi** — Python `__add__`, `__getitem__` work.  Declaration in Nomi syntax
not yet designed.

---

## Named / Default Struct Fields

**Rust / Swift / Kotlin**:

```rust
struct Config {
    host: String,
    port: u16,
}
let config = Config { host: "localhost".into(), port: 8080 };
let config = Config { port: 8080, ..Default::default() };
```

**Nomi** — Python dataclasses via `@dataclass`.  Nomi-native `data` will
support named and positional construction.

---

## Sealed / Enum Classes (Sum Types)

Closed set of variants, enabling exhaustive pattern matching.

**Kotlin / Rust / Swift / Scala**:

```kotlin
sealed class Result<out T, out E> {
    data class Ok<T>(val value: T) : Result<T, Nothing>()
    data class Err<E>(val error: E) : Result<Nothing, E>()
}
```

```rust
enum Result<T, E> { Ok(T), Err(E) }
```

**Nomi** (Track 4 — `data` with sum variants):

```nomi
data Result[T, E]:
    Ok(value: T)
    Err(error: E)
```

---

## Implementation Priority

| Feature | Effort | Impact |
|---------|--------|--------|
| Type aliases | low | high |
| Data classes | high | very high |
| Sealed/enum (sum types) | high | very high |
| Extension functions | medium | high |
| Operator overloading (declarative) | high | medium |
