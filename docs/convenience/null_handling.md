# Null / Optional Convenience

## Optional Chaining

Short-circuit property access, method call, or subscript when the receiver
is null/none.

**JavaScript / Swift / Kotlin / C# / Ruby**:

```javascript
const name = user?.address?.city
const first = list?.[0]
const result = obj?.method?.()
```

```kotlin
val name = user?.address?.city
val first = list?.getOrNull(0)
val result = obj?.method()
```

```swift
let name = user?.address?.city
```

**Nomi proposal**:

```nomi
name = user?.address?.city
first = list?.[0]
result = obj?.method()
```

AST desugaring:
```
user?.address?.city
→ if user is None: None else user.address?.city
→ if user is None: None elif user.address is None: None else user.address.city
```

---

## Null Coalescing

Provide a default value when the left operand is null/none.

**JavaScript / Swift / Kotlin / C#**:

```javascript
const name = user.name ?? "anonymous"
```

```kotlin
val name = user.name ?: "anonymous"
```

```swift
let name = user.name ?? "anonymous"
```

**Nomi proposal**:

```nomi
name = user.name ?? "anonymous"
```

Desugars to: `user.name if user.name is not None else "anonymous"`.

---

## Elvis Operator (Return/Throw on Null)

Short-circuit with non-value action when null.

**Kotlin**:

```kotlin
val name = user.name ?: return          // early return
val data = cache[key] ?: throw NotFound()
val config = load() ?: defaultConfig   // fallback
```

**Swift (guard)**:

```swift
guard let name = user.name else { return }
```

**Nomi proposal**:

```nomi
name = user.name ?? return
data = cache[key] ?? raise NotFound()
```

---

## Option / Maybe Type

Algebraic type representing presence or absence of a value.  Safer than
null because the compiler forces handling.

**Rust / Swift / Scala / Haskell / OCaml**:

```rust
enum Option<T> { Some(T), None }

fn find(x: i32) -> Option<String> { ... }

match find(42) {
    Some(name) => println!("found {name}"),
    None => println!("not found"),
}

let name = find(42).unwrap_or("default".into());
let upper = find(42).map(|s| s.to_uppercase());
```

**Scala**:

```scala
val name = find(42).getOrElse("default")
val upper = find(42).map(_.toUpperCase)
```

**Nomi** (Track 4):

```nomi
data Option[T]:
    Some(value: T)
    None

name = find(42).unwrap_or("default")
upper = find(42).map(_.upper())
```

---

## Result Type (Error as Value)

Algebraic type for success or failure.  Enables `?` operator and monadic
error handling.

**Rust / Swift / Kotlin (Result) / Scala (Either)**:

```rust
enum Result<T, E> { Ok(T), Err(E) }

fn parse(s: &str) -> Result<i32, ParseError> { ... }

let num = parse("10")?;         // propagate error
let num = parse("10").unwrap(); // panic on error
```

**Nomi** (Track 4):

```nomi
data Result[T, E]:
    Ok(value: T)
    Err(error: E)
```

---

## Implementation Priority

| Feature | Effort | Impact |
|---------|--------|--------|
| `??` null coalesce | low | high |
| `?.` optional chain | medium | high |
| Option type | high | high |
| Result type | high | high |
| Elvis `?? return` | medium | medium |
