# Data & Types

> Normal form: Data boundary.  Covers type aliases, data declarations,
> strings, and extension methods.  For binding constraints specifically,
> see [../features/binding_constraints_feature.md](../features/binding_constraints_feature.md).

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

Nominal types with named fields, constraints, and auto-generated
constructors.

```nomi
data User:
    name: str
    age: int

data Result[T, E]:
    Ok(value: T)
    Err(error: E)
```

**Source reference:** Kotlin `data class`, Swift `struct`, Rust `struct` +
`enum`, Scala `case class`, Haskell `data`.
**Status:** design-needed for data classes; sum types depend on the
pattern normal form for exhaustiveness checking.

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

### Interpolation

Embed expressions in string literals.

```nomi
f"Hello {name}, you are {age} years old"
```

**Source reference:** Python f-strings, JavaScript template literals,
Kotlin `"$name ${age}"`, Ruby `"#{name}"`, Swift `"\\(name)"`.
**Status:** implemented (f-string syntax desugars at parse time).

### Multi-Line Strings

Triple-quoted strings with indentation handling.

```nomi
doc = """
    line one
    line two
    """
```

**Status:** implemented.

### Raw Strings

No escape processing.

```nomi
path = r"C:\Users\name\docs"
```

**Status:** implemented (Python-compatible).

### Regex Literals

**Status:** library-first. Keep regex as a library concern, not
language syntax. Every language with regex literals (JavaScript, Ruby,
Perl) has had to add escape-related special cases.

---

## 4. Implementation Status

| Feature | Status |
|---------|--------|
| Type aliases (`type X = Y`) | implemented |
| f-string interpolation | implemented |
| Triple-quoted strings | implemented |
| Raw strings (`r"..."`) | implemented |
| Data class declarations | design-needed |
| Sum types (sealed/enum) | design-needed |
| Extension methods | design-needed |
| Declarative operator overloading | design-needed |
| Regex literals | library-first |
