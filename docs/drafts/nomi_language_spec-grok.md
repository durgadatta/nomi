# Nomi Language Specification

**Version 0.1 (Baseline Draft)**  
**Date**: May 2026  
**Status**: Coherent synthesis from Python, Ruby, Haskell, Scala, Kotlin, TypeScript + original Nomi vision – ready for iteration

**Nomi** is a modern general-purpose programming language that feels delightful for scripts and scales naturally to robust applications and libraries.

## Core Philosophy

- Readable like Python
- Expressive and joyful like Ruby
- Compositional and safe like Haskell
- Pragmatic and ergonomic like Kotlin/Scala
- Great developer experience like TypeScript
- Strong focus on inspectable execution, rich diagnostics, and explicit boundaries (Nomi spirit)

**One-line vision**: Beautifully readable code that naturally evolves from script to large system without changing dialect.

**Key Principles**:
- Immutability by default, explicit mutability
- Blocks as a core primitive for control flow and resource management
- Pipelines for readable data flow
- Gradual typing + runtime constraints
- Excellent errors are a language feature, not an afterthought
- Last-expression semantics
- Few special forms, many composable uses

---

## 1. Lexical Structure

- **Encoding**: UTF-8
- **Indentation**: Significant (prefer 4 spaces). Mixed tabs/spaces rejected.
- **Line structure**: Newlines end statements. `:` opens an indented block.
- **Comments**: 
  - `#` — line comment
  - `##` — documentation comment (attached to next declaration)
- **Identifiers**:
  - `snake_case` for values, functions, modules, fields
  - `UpperCamelCase` for data types and variants
  - `_leading_underscore` for private
  - `_` as wildcard
- **Keywords**: `func`, `data`, `match`, `case`, `do`, `import`, `from`, `as`, `module`, `export`, `where`, `else`, `try`, `except`, `finally`, etc.

### Literals

```nomi
42          # Int
3.14        # Float
true false  # Bool
none        # None
"hello" 'world'
[1, 2, 3]                       # List
(1, 2, 3)                       # Tuple
{name: "Ada", age: 36}          # Dict / record literal
```

---

## 2. Bindings and Variables

```nomi
name = value                    # immutable, type inferred
count: Int = 42                 # explicit type
mutable_count := 0              # mutable (explicit, use sparingly)

# With runtime + static constraints
age: Int where age >= 0 and age <= 150 = raw_age

email: String where email.contains("@") else "Invalid email format" = input

# Named reusable predicate
predicate Adult(age: Int) = age >= 18
```

Rebinding only allowed for mutable variables (`:=`).

---

## 3. Functions

```nomi
func greet(name: String) -> String:
    ## Greets a person
    return "Hello, {name}!"

# Arrow function (expression)
greet = (name: String) => "Hello, {name}!"

# With constraints
func signup(
    email: String where email.contains("@"),
    age: Int where Adult(age)
) -> Result[User, Error]:
    ...
```

**Pipeline operator** (core syntax for flow):

```nomi
processed = raw_users
    |> filter(_.active)
    |> map(_.name)
    |> sort()
    |> take(10)
```

**Extension functions**:

```nomi
func String.upper_first() -> String:
    return self[0].upper() + self[1:]
```

---

## 4. Data Types

```nomi
data User:
    id: UserId
    name: String
    email: Email
    active: Bool = true

    func display_name(self) -> String:
        return self.name
```

**Sum types / Variants**:

```nomi
data Result[T, E]:
    Ok(value: T)
    Err(error: E)
```

Features:
- Immutable by default
- Automatic constructor, equality, string representation
- Pattern matching support
- Explicit decoding: `User.decode(raw_data)`

---

## 5. Pattern Matching

```nomi
match fetch_result:
    case Ok(user):
        process_user(user)
    case Err(e) if e.code == 404:
        handle_not_found()
    case Err(e):
        log(e)
    else:
        raise UnexpectedError()
```

Destructuring:

```nomi
{ name, email } = user_dict
[first, *rest] = items
Ok(user) = get_user(id)   # raises PatternError on mismatch
```

---

## 6. Blocks (Ruby-inspired core feature)

```nomi
# Resource handling
content = open("data.txt") do |file|
    file.read()
end

# Policy / control
result = retry(times: 3, on: [NetworkError, Timeout]) do
    api.post(payload)
end

# Iteration
process_all(users) do |user|
    send_notification(user)
end
```

**Semantics**:
- Block is attached to the preceding call.
- Passed as a callable to the function.
- Callee invokes via `yield value`.
- Lexical scoping (closes over caller environment).
- Exceptions propagate through `yield`.

This one feature unifies `with`, callbacks, generators, domain policies, etc.

---

## 7. Control Flow

```nomi
if condition:
    ...
elif other:
    ...
else:
    ...

for item in collection:
    ...

while condition:
    ...

# Expression form
grade = if score >= 90: "A" elif score >= 80: "B" else: "C"

# Last expression is return value
func max(a: Int, b: Int):
    if a > b: a else: b
```

---

## 8. Modules and Imports

```nomi
module app.signup

import std.io
import std.collections as coll
import app.core.{User, Result, Ok, Err}
from app.email import normalize_email, validate_email

export User, signup   # optional; defaults to non-underscore names
```

---

## 9. Error Handling

**Preferred**: `Result[T, E]` for expected errors.

**Exceptions** for unexpected cases:

```nomi
try:
    data = load_critical_file()
except FileNotFound as e:
    log(e)
finally:
    cleanup()
```

All errors include rich context: source location, values, constraints, stack.

---

## 10. Executable Examples

```nomi
func normalize_email(email: String) -> String:
    examples:
        "  Ada@EXAMPLE.COM " => "ada@example.com"
        "invalid" => raise ValueError("bad email")

    return email.strip().lower()
```

---

## 11. Concurrency (v1)

```nomi
async func fetch_all(users: List[UserId]) -> List[User]:
    ...
```

Structured concurrency via blocks planned for future versions.

---

## 12. Full Example

```nomi
module app.main

data SignupInput:
    email: String where email.contains("@")
    age: Int where age >= 13

func signup(input: SignupInput) -> Result[User, SignupError]:
    user = User.create(input.email, input.age)
    return Ok(user)

# Main flow
result = read_stdin_json()
    |> SignupInput.decode()
    |> flat_map(signup)
    |> map(user => welcome_email(user))
```

---

## Appendix: Core Special Forms (Kernel)

1. Binding (`=`, `:=`, `: Type where ...`)
2. Function definition (`func` and `=>`)
3. Data definition (`data`)
4. Pattern matching (`match` / `case`)
5. Block attachment (`do ... end` or indented block)
6. Pipeline (`|>`)
7. Module / Import system

Everything else is built on top of these.

---

This specification provides a clean, coherent baseline that blends the best qualities of the referenced languages while maintaining a small, understandable core.

Copy this content into a file named `nomi-spec.md` for editing and iteration.
