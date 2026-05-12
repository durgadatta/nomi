# Error Handling Convenience

## Try / Catch as Expression

Try-catch that produces a value, not just side-effects.

**Kotlin / Rust / Scala**:

```kotlin
val result = try { risky() } catch (e: Exception) { fallback }
```

```scala
val result = try { risky() } catch { case e: Exception => fallback }
```

**Nomi proposal**:

```nomi
result = try:
    risky()
except Exception as e:
    fallback
```

---

## Error Propagation Operator (`?` / `!`)

Unwrap a Result/Option or propagate the error.  Eliminates
boilerplate error-checking.

**Rust**:

```rust
fn process() -> Result<i32, Error> {
    let a = step1()?;
    let b = step2(a)?;
    Ok(a + b)
}

fn get_name(id: i32) -> Option<String> {
    let user = find_user(id)?;
    Some(user.name)
}
```

**Swift**:

```swift
func process() throws -> Int {
    let a = try step1()
    let b = try step2(a)
    return a + b
}
```

**Kotlin (Result)**:

```kotlin
fun process(): Result<Int, Error> {
    val a = step1().getOrElse { return it }
    val b = step2(a).getOrElse { return it }
    Ok(a + b)
}
```

**Nomi proposal** (requires Result type from Track 4):

```nomi
func process() -> Result[Int, Error]:
    a = step1()?
    b = step2(a)?
    return a + b
```

`expr?` desugars to:
```
match expr:
    case Ok(v): v
    case Err(e): return Err(e)
```

---

## Guard / Let-Else

Early-exit pattern: unwrap or return/break/continue.

**Swift**:

```swift
guard let value = optional else { return }
// value is bound and non-nil here
```

**Rust**:

```rust
let Some(value) = optional else { return };
let Ok(parsed) = parse(input) else { continue };
```

**Nomi proposal**:

```nomi
guard Some(value) = optional:
    return

guard Ok(parsed) = parse(input):
    continue
```

---

## Defer / Finally as Expression

Execute cleanup code regardless of how a scope exits.

**Go / Swift / Zig**:

```go
defer file.close()
```

```swift
defer { file.close() }
```

**Nomi** — `finally` in try blocks, `with` for context managers.

---

## Implementation Priority

| Feature | Effort | Impact |
|---------|--------|--------|
| `?` propagate | low (with Result) | very high |
| try as expression | medium | high |
| guard / let-else | medium | high |
| defer | low | medium |
