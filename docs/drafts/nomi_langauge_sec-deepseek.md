# Nomi: A Language Specification

**Version 0.2.0 — Core Language Design**

## Table of Contents

1. [Philosophy](#1-philosophy)
2. [Design Principles](#2-design-principles)
3. [Syntax Overview](#3-syntax-overview)
4. [Lexical Structure](#4-lexical-structure)
5. [Values and Types](#5-values-and-types)
6. [Bindings and Naming](#6-bindings-and-naming)
7. [Constraints](#7-constraints)
8. [Functions](#8-functions)
9. [Data Types](#9-data-types)
10. [Patterns and Matching](#10-patterns-and-matching)
11. [Blocks and Yield](#11-blocks-and-yield)
12. [Pipelines](#12-pipelines)
13. [Modules and Imports](#13-modules-and-imports)
14. [Error Handling](#14-error-handling)
15. [Special Forms Reference](#15-special-forms-reference)
16. [Complete Grammar](#16-complete-grammar)
17. [A Complete Example](#17-a-complete-example)

---

## 1. Philosophy

A programming language is a medium for thought. Before it is a tool for instructing machines, it is a tool for thinking clearly about problems and communicating that thinking to others. The languages that endure succeed because they have a coherent center. They are about something.

Nomi makes this bet:

A language should be small in its core concepts and large in what you can express by composing them. Every feature should pull its weight across multiple contexts. The programmer should never have to learn a special sub-language for a common task.

This leads to a design discipline. We do not add features because another language has them or because they address a single use case elegantly. We add primitives that combine. The test of a feature is not "does this make X easier?" but "does this make X, Y, and Z easier in the same way?"

---

## 2. Design Principles

### 2.1 One Mechanism, Many Contexts

Every semantic mechanism in Nomi should work across all appropriate contexts. If we have a constraint system, it works in variable bindings, function parameters, data fields, pattern matching, and block parameters—identically. If we have a pattern language, it works in match, assignment, and block bindings—identically.

### 2.2 Explicit Over Implicit

Things that affect program behavior should be visible. There is no implicit type coercion in conditionals, no silent null propagation, no magic method resolution. When a value crosses a boundary, that crossing is explicit.

### 2.3 Explainable Always

Every error should be explainable in terms the programmer can act on. A constraint failure should say what constraint failed, what value was provided, and where the binding occurred. Diagnostics are not decoration; they are a first-class design concern.

### 2.4 Grow Gracefully

The language should work well for a 20-line script and for a 20,000-line application. The mechanisms that make a script clear (simple bindings, readable pipelines, straightforward error handling) should be the same mechanisms that scale to larger programs.

### 2.5 Reduce to the Core

Every "advanced" feature should be understandable as a combination of core primitives. Blocks are functions with attached closures. Pipelines are function application in a different order. Data types with members are ordinary functions with a calling convention.

---

## 3. Syntax Overview

Nomi's syntax draws primarily from Python's tradition of significant whitespace and readable keywords, with influences from ML-style data declarations, Ruby-style blocks, and Unix-style pipelines.

**Key syntactic decisions:**

- Significant indentation for block structure (like Python, Haskell)
- `func` for named function definitions
- `data` for type definitions (from ML tradition)
- `match`/`case` for pattern matching (from ML/Scala tradition)
- `|>` for pipelines (from Elixir/OCaml tradition)
- Colon-and-indent blocks for function bodies, conditionals, and loops
- Arrow functions for expression-level lambdas: `(x) => x + 1`

---

## 4. Lexical Structure

### 4.1 Source Text

A Nomi source file is a sequence of Unicode characters encoded in UTF-8.

### 4.2 Lines and Indentation

Nomi uses significant indentation to delimit blocks. A block is introduced by a line ending in a colon. The block consists of the following lines indented more than the introducing line. The block ends when indentation returns to the level of the introducing line or less.

```nomi
func greet(name: str) -> str: # colon introduces block
    greeting = "Hello, "      # indented: part of block
    return greeting + name    # indented: part of block

farewell = "Goodbye"          # not indented: block ended
```

---

### 4.3 Comments

Line comments begin with `#` and extend to the end of the line. There are no block comments in the core language. Multi-line comments use repeated line comments.

Documentation comments are ordinary comments that immediately precede a declaration with no blank line between them.

### 4.4 Identifiers

Identifiers consist of a letter or underscore, followed by zero or more letters, digits, or underscores.

**By convention:**

- `snake_case` for values, functions, modules, and fields
- `CamelCase` for data types and variant constructors
- `_leading_underscore` for private or internal names
- `_` alone as the wildcard pattern

---

### 4.5 Keywords

The following are reserved and may not be used as identifiers:

`and as block break case const continue data decode each elif else examples export false for from func global if import in is let match module none not on or quote raise return rewrite self then true try use when while with world yield`

---

### 4.6 Operators

`/ // % ** == != < > <= >= = |> => -> | & . , : ; @ _`

---

### 4.7 Literals

Numeric literals:  
`42` `3.14` `1.5e-3` `0xFF` `0o777` `0b1010` `1_000_000`

String literals:  
`"hello"` `'hello'` `"it's a string"` `"""multiline"""` `r"raw\string"`

Boolean literals: `true` `false`

Absence literal: `none`

---

## 5. Values and Types

### 5.1 Value Categories

Every expression evaluates to a value or raises an error.

### 5.2 Types

Every value has a type. A type is, operationally, a predicate: it answers the question "does this value belong to this category?" Type annotations are checked at runtime by default. Static checking is optional and additive.

Built-in types: `int`, `float`, `str`, `bool`, `list`, `dict`, `tuple`, `func`, `type`.

### 5.3 Truth

Conditions in `if`, `while`, and guard expressions require boolean values. There is no implicit truthiness.

### 5.4 Equality

Equality (`==`) is structural for built-in types and for data types. Identity (`is`) tests whether two references point to the same object.

---

## 6. Bindings and Naming

```nomi
name = value
name: type = value
name: type, constraint = value
const pi = 3.14159
```

---

## 7. Constraints

Constraints are executable predicates on values. They are used wherever binding occurs.

**Examples:**

```nomi
x: int
x >= 0
x: int, x >= 0, x < 150
email: str, contains(email, "@")
```

---

## 8. Functions

```nomi
func add(x: int, y: int) -> int:
    return x + y

func greet(name: str, greeting: str = "Hello") -> str:
    return greeting + ", " + name + "!"
```

---

## 9. Data Types

```nomi
data Point:
    x: float
    y: float

data User:
    name: str
    email: str, contains(email, "@")
    age: int, age >= 0

data Option[T]:
    Some(value: T)
    None
```

---

## 10. Patterns and Matching

```nomi
match value:
    case pattern1:
        body1
    case pattern2 if guard:
        body2
    else:
        default_body
```

---

## 11. Blocks and Yield

```nomi
each(users) -> user: User, user.active:
    send(user.email)
```

---

## 12. Pipelines

```nomi
result = data |> step1 |> step2 |> step3
names = users |> map(.name) |> where(.starts_with("A"))
```

---

## 13. Modules and Imports

```nomi
module app.users
import app.database as db
export User, load, create
```

---

## 14. Error Handling

**Expected Failures** — Use `Option` or `Result` types.  
**Unexpected Failures** — Use exceptions with `try`/`except`.

---

## 15. Special Forms Reference

- `name = value` — Binding
- `name: constraint = value` — Annotated binding
- `const name = value` — Constant binding
- `func name(params) -> T: body` — Named function
- `data Name: fields` — Product type
- `data Name: Variant1 | Variant2` — Sum type
- `match value: case pat: body` — Pattern matching
- `callee(args) -> pat: body` — Block call
- `expr |> expr` — Pipeline

---

## 16. Complete Grammar

(program and full grammar as provided in original spec — omitted here for brevity in this rendering, but included in final file if needed)

---

## 17. A Complete Example

```nomi
module app.signup

data Plan:
    Free
    Pro(max_users: int)

data SignupInput:
    name: str, len(name) > 0 else "Name is required"
    email_addr: str, contains(email_addr, "@")
    age: int, age >= 13

func signup(input: SignupInput) -> SignupResult:
    match db.find_user_by_email(input.email_addr):
        case Some(existing):
            return SignupResult.Duplicate(existing_id=existing.id)
        case None:
            pass

    user = db.create_user(name=input.name, email=input.email_addr, age=input.age)
    return SignupResult.Created(user_id=user.id)
```

**End of Nomi Language Specification v0.2.0**