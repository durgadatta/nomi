# Absence & Result Handling

> Normal forms: Absence/result + Block.  Two distinct stories that do not
> collapse into each other: absence (`?.`, `??`, `Option`) handles "no
> value"; expected failure (`Result`, `try`, `?`) handles "operation
> failed"; exceptions handle "unexpected error."
>
> Companion: [design_lessons_and_integration.md §4.6](design_lessons_and_integration.md)
> for the integration critique and systemic lessons.

## 1. Absence Handling

### Optional Chaining `?.`

Short-circuits attribute, method, or subscript access when the receiver
is `None`. The receiver is evaluated once.

```nomi
name = user?.address?.city
first = items?.[0] ?? "missing"
value = config?.get("key")
```

Desugaring:
```
user?.address?.city
→ if user is None: None else user.address?.city
→ if user is None: None elif user.address is None: None else user.address.city
```

**Source reference:** JavaScript `?.`, Swift `?.`, Kotlin `?.`, C# `?.`, Ruby `&.`.
**Status:** implemented (attribute, method call, subscript).

### Null Coalescing `??`

Returns the right operand when the left is `None`.

```nomi
name = user.name ?? "anonymous"
```

Desugars to `user.name if user.name is not None else "anonymous"`.

**Source reference:** JavaScript `??`, Swift `??`, Kotlin `?:`, C# `??`.
**Status:** implemented.

### Option Type

Algebraic type for presence or absence. Safer than null because the
compiler or runtime enforces handling.

```nomi
data Option[T]:
    Some(value: T)
    None

name = find(42).unwrap_or("default")
upper = find(42).map(_.upper())
```

**Source reference:** Rust `Option<T>`, Swift `Optional<T>`, Scala `Option[T]`,
Haskell `Maybe`, OCaml `option`.
**Status:** design-needed (Track 4).

---

## 2. Expected Failure (Result)

### Result Type

Algebraic type for success or failure. Enables monadic error handling
without exceptions.

```nomi
data Result[T, E]:
    Ok(value: T)
    Err(error: E)
```

**Source reference:** Rust `Result<T,E>`, Swift `Result<T,E>`,
Kotlin `Result<T>`, Scala `Either[E,T]`.
**Status:** design-needed (Track 4).

### Try as Expression

Try-catch that produces a value, not just side-effects.

```nomi
safe = try:
    int("not a number")
except ValueError:
    0
```

Wraps in an IIFE so it can appear in expression position.

**Source reference:** Kotlin `try { } catch { }`, Scala `try { } catch { }`,
Rust `unwrap_or`.
**Status:** implemented.

### Error Propagation `?`

Unwrap a `Result` or propagate the error. Reduces boilerplate error-checking.

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

**Source reference:** Rust `?`, Swift `try`, Zig `try`.
**Status:** design-needed (requires `Result` type).

**Design note:** Deferred until `Result` is widely used. The risk: `?` for
Result next to `?.` for absence creates two visually similar operators with
different semantics. See [design_lessons_and_integration.md §4.6](design_lessons_and_integration.md).

---

## 3. Guard (Early Exit on Mismatch)

Unwrap a pattern or execute an early-exit body.

```nomi
guard Some(value) = optional:
    return

guard Ok(parsed) = parse(input):
    continue

func first(items):
    guard [head, *tail] = items:
        return "empty"
    return head
```

If the pattern matches, captures are bound and execution continues. If
it does not match, the guard body runs.

**Source reference:** Swift `guard let`, Rust `let ... else`.
**Status:** implemented (guard-let). The prototype does not yet verify
that the guard body actually exits — this will become a diagnostic once
control-flow analysis exists.

---

## 4. Defer (Cleanup on Scope Exit)

Schedule cleanup code regardless of how the scope exits.

```nomi
func process(path):
    file = open(path)
    defer file.close()
    # ... file used here; close runs on return or exception
```

LIFO execution of deferred calls.

**Source reference:** Go `defer`, Swift `defer`, Zig `defer`/`errdefer`.
For Zig's `errdefer` (defer only on error), see
[error_handling_defer_resource_cleanup_notes.md](../research/error_handling_defer_resource_cleanup_notes.md).

**Status:** implemented.

---

## 5. Implementation Status

| Feature | Status | Notes |
|---------|--------|-------|
| `?.` optional chain | implemented | attr, call, subscript |
| `??` null coalesce | implemented | |
| `try` as expression | implemented | IIFE wrapping |
| `guard` pattern | implemented | exit diagnostic future |
| `defer` | implemented | |
| `Option[T]` type | design-needed | Track 4 |
| `Result[T, E]` type | design-needed | Track 4 |
| `?` error propagation | design-needed | requires `Result` |
| Elvis `?? return/raise` | design-needed | would reduce to guard or `?` |

---

## 6. Research Sources

- [error_handling_defer_resource_cleanup_notes.md](../research/error_handling_defer_resource_cleanup_notes.md) — Zig, Hylo, Odin, Gleam, Roc
- [design_lessons_and_integration.md §4.6](design_lessons_and_integration.md) — integration critique
- [design_lessons_and_integration.md §7.6](design_lessons_and_integration.md) — three-distinct-stories systemic pattern
