# Absence & Result Handling

> Normal forms: Absence/result + Block.
>
> Three distinct stories that do not collapse into each other:
> - **Absence** (`none`, `?.`, `??`, `Option[T]`) — "no value"
> - **Expected failure** (`Result[T, E]`, `match`, `try`-as-expression) — "operation failed"
> - **Unexpected error** (exceptions) — "unexpected, unrecoverable at this call site"
>
> Deep research: [error_handling_defer_resource_cleanup_notes.md](../research/error_handling_defer_resource_cleanup_notes.md)
> (16-language error/defer/resource survey),
> [cross_language_synthesis_master.md §4.7](../research/cross_language_synthesis_master.md)
> (capstone absence/result synthesis),
> [security_and_trust_deep_dive.md](../research/security_and_trust_deep_dive.md)
> (secret redaction in diagnostics).
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

`Option[T]` is the absence-bearing type. It is structural (not nominal):
`Some(42)` matches the `Option` pattern regardless of origin. This lets
Nomi code use `Option` without mandatory imports and allows Python `None`
to interoperate naturally.

```nomi
data Option[T]:
    Some(value: T)
    None

# `none` is the canonical spelling (Python None interop)
name = find(42).unwrap_or("default")
upper = find(42).map(_.upper())
```

The spelling `none` (not `None`, `nil`, `null`) is the canonical absence
value. Python `None` is accepted at the boundary but `none` is the
preferred Nomi spelling.

**Source reference:** Rust `Option<T>`, Swift `Optional<T>`, Scala `Option[T]`,
Haskell `Maybe`, OCaml `option`.
**Status:** design-settled (implementation deferred to Track 4).

---

## 2. Expected Failure (Result)

### Result Type

`Result[T, E]` is the expected-failure type. It is nominal (`data`),
not structural — `Ok(42)` from different modules are the same `Result`
type, but `Result` is not confused with other two-variant data types.

```nomi
data Result[T, E]:
    Ok(value: T)
    Err(error: E)
```

The primary consumption story is `match`:

```nomi
match parse(input):
    case Ok(value): process(value)
    case Err(error): log(error); recover
```

Result is distinct from `Option`. `?.` and `??` operate on `Option`
(absence) only — they do NOT short-circuit on `Err`. This prevents the
Python mistake of silently mixing `None` with error states.

**Source reference:** Rust `Result<T,E>`, Swift `Result<T,E>`,
Kotlin `Result<T>`, Scala `Either[E,T]`.
**Status:** design-settled (implementation deferred to Track 4).

### Try as Expression

Try-catch that produces a value, not just side-effects.

```nomi
safe = try:
    int("not a number")
except ValueError:
    0
```

Current prototype lowering may use an IIFE so it can appear in expression
position. That is a backend bridge, not the source-level model; see
[expression_statement_orientation.md](expression_statement_orientation.md) for
the value-producing block and control-transfer doctrine.

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
**Status:** deferred. `match` is the primary `Result` consumption story.
`?` will be considered only after `Result` is widely used and return-type
rules are explicit.

**Deferral rationale:** `?` for Result next to `?.` for absence are visually
similar operators with different semantics: `?.` short-circuits on `none`;
`?` propagates `Err`. Early Nomi code will use explicit `match` for Result
handling. If this proves verbose in the same way Go's `if err != nil` does,
`?` can be added as a surface sugar — it lower to the same `match` form
users already write. See [design_lessons_and_integration.md §4.6](design_lessons_and_integration.md)
for the full analysis.

### Error Conversion

When `?` or other propagation operators are added, they will need explicit
error conversion rules:

```nomi
# Sketch: error conversion trait
trait IntoError[E]:
    func into_error(self) -> E
```

This is Rust's `From`/`Into` pattern for error types. The design is deferred
with `?` — the conversion story should be settled before propagation syntax.

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
| `try` as expression | implemented | IIFE backend bridge; source semantics need value-block doctrine |
| `guard` pattern | implemented | exit diagnostic future |
| `defer` | implemented | |
| `Option[T]` type | design-settled | structural; `none`/`Some`; implementation deferred to Track 4 |
| `Result[T, E]` type | design-settled | nominal data type; `Ok`/`Err`; implementation deferred to Track 4 |
| `?` error propagation | deferred | `match` primary; reconsider after Result usage data |
| Elvis `?? return/raise` | rejected-for-now | would reduce to guard or `?`; adds no new semantic capability |
| `Secret[T]` / `PII[T]` in error messages | design-settled | auto-redact in diagnostics; see [data_and_types.md](data_and_types.md) |

---

## 6. Research Sources

- [error_handling_defer_resource_cleanup_notes.md](../research/error_handling_defer_resource_cleanup_notes.md) — 16-language survey: Zig, Hylo, Odin, Gleam, Roc, Swift, Kotlin, Scala, Java, Python, C++, Haskell
- [cross_language_synthesis_master.md §4.7](../research/cross_language_synthesis_master.md) — capstone absence/result synthesis with Nomi Adopt/Refuse decisions
- [design_lessons_and_integration.md §4.6](design_lessons_and_integration.md) — integration critique
- [design_lessons_and_integration.md §7.6](design_lessons_and_integration.md) — three-distinct-stories systemic pattern
- [security_and_trust_deep_dive.md](../research/security_and_trust_deep_dive.md) — `Secret[T]` redaction in diagnostics and error messages

## 7. Design Context

This doc covers Nomi's **Absence/result** and **Block** normal forms.
For the broader picture:

- [Language Foundation §Coherence Contract](../language/language_foundation.md) —
  the One Explanation Story (diagnostics from semantic events) and the One Block
  Story (caller-side code attached to a call).
- [Language Specification §8.5-8.6, §13-14](../language/language_spec.md) —
  absence-aware expressions, try expressions, blocks and yield, errors and
  Result values.
- [Design Lessons and Integration §4.6](design_lessons_and_integration.md) —
  integration critique of absence/result/error handling.
- [Implementation Learnings](../convenience/implementation_learnings.md) —
  `_nomi_defer` attribute stripping before re-evaluation, `"try"` in
  expression position, `match_case` guard handling.
- [Block Calls Feature](../features/block_calls_feature.md) — detailed block
  design, yield semantics, control boundaries, and policy blocks.
