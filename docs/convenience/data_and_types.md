# Data & Types

> Normal form: Data boundary.  Covers type aliases, data declarations,
> strings, extension methods, and the data-boundary decode protocol.
> For binding constraints specifically, see
> [../features/binding_constraints_feature.md](../features/binding_constraints_feature.md).
>
> Deep research: [data_boundary_systems_deep_dive.md](../research/data_boundary_systems_deep_dive.md)
> (10-system survey: Pydantic, CUE, Nickel, Pkl, Dhall, Terraform, JSON Schema,
> TypeScript, serde, Elm decoders),
> [security_and_trust_deep_dive.md](../research/security_and_trust_deep_dive.md)
> (10-dimension survey: Nix, capabilities, secrets, supply-chain, sandboxing,
> crypto hygiene, auth, redaction).

## 1. Type Aliases

Short names for complex types.

```nomi
type UserId = str
type Callback = (int, str) -> bool
```

**Source reference:** Kotlin `typealias`, Swift `typealias`, Rust `type`,
TypeScript `type`.
**Status:** implemented.

---

## 2. Data Declarations

`data` is the single keyword for owned product and sum types. It generates
constructors, field accessors, equality, display, and pattern forms. There is
no separate `struct`/`enum`/`class`/`record` keyword family.

### Product Types

```nomi
data User:
    name: str
    age: int where _ >= 0
```

Fields reuse the binding normal form: same constraint syntax, same diagnostics,
same lifecycle (evaluate → tentatively bind → check constraints → commit or
`BindingError`).

### Sum Types

```nomi
data Result[T, E]:
    Ok(value: T)
    Err(error: E)

data Option[T]:
    Some(value: T)
    None
```

Sum types enable exhaustiveness checking in `match` expressions. The pattern
normal form (§3 of [patterns.md](patterns.md)) handles deconstruction.

### Exhaustiveness

Exhaustiveness is checked for closed `data` variants (nominal types). Structural
matching against external values (mapping patterns, destructuring) is not
exhaustiveness-checked since the set of possible shapes is open.

**Source reference:** Kotlin `data class`, Swift `struct`, Rust `struct` +
`enum`, Scala `case class`, Haskell `data`.
**Status:** design-settled for the `data` keyword and its semantics;
implementation deferred.

### Data Boundary: `Data.decode()`

External data crosses into Nomi through an explicit decode boundary. The
principle (from cross-language synthesis across Pydantic, CUE, Elm, Rust
serde, and TypeScript/zod) is:

> Parse, don't validate. `Data.decode()` returns `Result[T, DecodeErrorList]`,
> not a boolean plus untyped value.

```nomi
data User:
    name: str
    age: int where _ >= 0

# Explicit boundary crossing — result is Result[User, DecodeErrorList]
user_result = Data.decode(json_bytes, User)
match user_result:
    case Ok(user): ...
    case Err(errors): ...
```

### Decoders as Composable Values

Decoders are first-class, composable values (Elm model):

```nomi
# A decoder is a value of type Decoder[T]
user_decoder: Decoder[User] = Data.decoder(User)

# Decoders compose
list_decoder = Data.list_of(user_decoder)
nested_decoder = Data.field("users", Data.list_of(user_decoder))
```

### Error Accumulation

`Data.decode()` accumulates ALL validation errors by default (Zod/Pydantic
model). `Data.decode_strict()` stops at the first error. Each error carries:
- Field path (e.g., `["users", 2, "age"]`)
- Expected type or constraint
- Actual value (with redaction for `@secret` fields)
- Source span when available

### Missing/Extra Field Policy

By default: extra fields are rejected (closed-by-default). Missing fields
with defaults are filled; missing fields without defaults are errors.
Opt-in policies via annotations:

```nomi
data Config:
    @extra_fields(ignore)  # or: reject, pass_through
    host: str
    port: int = 8080
```

### Field Provenance

Decoded values carry optional source-span metadata for diagnostics. When
`Data.decode` fails, error messages can point to the exact location in the
source document (JSON line/column, CSV row, etc.).

**Source reference:** Elm `Json.Decode`, Rust `serde::Deserialize`, Python
Pydantic, TypeScript zod, Dhall imports.
**Status:** prototype-ready for the decode protocol; field provenance
prototype-ready after decode.

### `@secret` and `@pii` Field Annotations

Sensitive fields are marked at the data declaration:

```nomi
data Credentials:
    username: str
    @secret password: str
    @pii email: str
```

Effects:
- Display shows `Credentials(username="alice", password=Secret("***"), email=PII("***"))`
- Diagnostics and error messages redact annotated fields automatically
- `explain` respects annotations; `explain --unsafe` shows raw values
- Equality comparison for `@secret` fields uses constant-time comparison
- `@pii` fields carry a provenance tag for GDPR/data-privacy audit

The `Secret[T]` and `PII[T]` wrapper types are part of the standard prelude.
See [security_and_trust_deep_dive.md](../research/security_and_trust_deep_dive.md) for
the full security dimension synthesis.

**Status:** design-settled.

### Import with Content-Addressed Integrity

External data schemas and modules can be imported with hash verification
(Dhall/Nix/Go sum database model):

```nomi
import "example.com/user/schema.nomi" sha256:abc123...
```

- No code execution during dependency fetch (Nix fetch-vs-build separation)
- Domain-name import paths (no bare-name global namespace — Go/Deno model)
- Unused imports are a compile error (Go model)
- Lockfile records transitive hashes as a Merkle tree

**Status:** design-settled; implementation requires packaging infrastructure.

### Extension Methods

Add methods to existing types without inheritance.

```nomi
func str.is_palindrome() -> bool:
    return self == self.reversed()
```

**Source reference:** Kotlin extension functions, Swift extensions,
Rust `impl Trait for Type`, C# extension methods.
**Status:** design-needed.

### Operator Overloading

User-defined behaviour for built-in operators.

```nomi
# Declarative: name the protocol, not the dunder method
func Vector.add(other: Vector) -> Vector:
    return Vector(self.x + other.x, self.y + other.y)
```

**Source reference:** Python `__add__`/`__getitem__`, Kotlin `operator`,
Swift operator declarations, Haskell type classes.
**Status:** design-needed.

---

## 3. Strings

> Moved to [strings.md](strings.md) — elevated to a first-class pillar
> alongside functions, collections, and patterns. Covers interpolation,
> literal forms, string API, typed wrappers, pattern matching, Unicode,
> serialization, and security.

---

## 4. Implementation Status

| Feature | Status |
|---------|--------|
| Type aliases (`type X = Y`) | implemented |
| Data class declarations (`data`) | design-settled |
| Sum types (variants) | design-settled |
| `Data.decode()` protocol | prototype-ready |
| Decoders as composable values | design-settled |
| Error accumulation (all errors) | design-settled |
| Missing/extra field policies | design-settled |
| Field provenance / source spans | prototype-ready |
| `@secret` / `@pii` field annotations | design-settled |
| Content-addressed imports | design-settled |
| Extension methods | design-needed |
| Declarative operator overloading | design-needed |
| Strings (interpolation, literals, typed wrappers) | see [strings.md](strings.md) |

## 5. Design Context

This doc covers Nomi's **Data boundary** normal form. For the broader picture:

- [Language Foundation §Coherence Contract](../language/language_foundation.md) —
  the One Data Story (external values explicitly decoded into owned data with
  diagnostics).
- [Language Specification §9-10](../language/language_spec.md) — data
  declarations, type aliases, and the decode protocol.
- [Language Degrees Of Freedom §Scoped Extension Freedom](../language/language_degrees_of_freedom.md) —
  why data boundaries use explicit `Data.decode()` rather than implicit coercion.
- [Absence and Result](absence_and_result.md) — `Result[T, E]` as the return
  type of `Data.decode()`; error accumulation vs fail-fast.
- [Security and Trust Deep Dive](../research/security_and_trust_deep_dive.md) —
  `Secret[T]`, `PII[T]`, content-addressed imports, crypto hygiene.
- [Data Boundary Systems Deep Dive](../research/data_boundary_systems_deep_dive.md) —
  full 10-system synthesis (Pydantic, CUE, Nickel, Pkl, Dhall, Terraform,
  JSON Schema, TypeScript, serde, Elm decoders).
- [Strings](strings.md) — string pillar: interpolation, literals, typed
  wrappers, pattern matching on strings, Unicode, serialization, security.
- [Implementation Learnings](../convenience/implementation_learnings.md) —
  grammar and AST interactions for type annotations.
