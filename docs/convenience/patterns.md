# Pattern Matching Convenience

## Match Statement

**Rust / Swift / Kotlin (when) / Elixir**:

```rust
match value {
    1 => "one",
    2 | 3 => "two or three",
    n if n > 10 => "big",
    _ => "other",
}
```

```kotlin
when (value) {
    1 -> "one"
    2, 3 -> "two or three"
    in 10..100 -> "big"
    else -> "other"
}
```

**Nomi** (supported):

```nomi
match value:
    case 1: return "one"
    case 2 | 3: return "two or three"
    case n if n > 10: return "big"
    case _: return "other"
```

---

## Destructuring in Match

**Rust / Elixir / OCaml / Haskell**:

```rust
match opt {
    Some(x) if x > 0 => process(x),
    Some(_) => fallback(),
    None => default(),
}

match point {
    (0, y) => println!("on y axis at {y}"),
    (x, 0) => println!("on x axis at {x}"),
    (x, y) => println!("at ({x}, {y})"),
}
```

```elixir
case list do
    [head | tail] -> process(head, tail)
    [] -> {:empty}
end
```

**Nomi** (partially supported):

```nomi
match list:
    case [head, *tail]: process(head, tail)
    case []: return "empty"
```

---

## Match as Expression

Using match to produce a value, not just execute statements.

**Rust / Scala / Kotlin (when-as-expression) / F#**:

```rust
let label = match n {
    1 => "one",
    _ => "many",
};

let result = match optional {
    Some(v) => v * 2,
    None => 0,
};
```

**Scala**:

```scala
val label = n match {
    case 1 => "one"
    case _ => "many"
}
```

**Nomi proposal**:

```nomi
label = match n:
    case 1: "one"
    case _: "many"

result = match optional:
    case Some(v): v * 2
    case None: 0
```

Each case body is an expression (last value returned).

---

## If-Let / While-Let

Conditional destructuring as a control-flow shortcut.

**Rust / Swift**:

```rust
if let Some(value) = optional {
    println!("got {value}");
}

while let Some(item) = iter.next() {
    process(item);
}
```

**Swift**:

```swift
if let value = optional {
    print(value)
}

guard let value = optional else { return }
```

**Nomi**:

```nomi
if Some(value) = optional:
    print(value)
```

`if-let` is implemented and supports an `else` branch:

```nomi
if [head, *tail] = items:
    print(head)
else:
    print("empty")
```

`while-let` is also implemented.  The expression is re-evaluated each
iteration; the loop exits when the pattern no longer matches:

```nomi
items = [1, 2, 3]
total = 0

while [head, *tail] = items:
    total += head
    items = tail
```

`guard-let` is implemented.  On match, captures are bound and execution
continues.  On non-match, the guard body runs:

```nomi
func first(items):
    guard [head, *tail] = items:
        return "empty"
    return head
```

The current prototype does not yet enforce that the guard body exits.  That
diagnostic is future work.

---

## Or Patterns

Matching multiple alternatives in one case.

**Rust / OCaml / Haskell**:

```rust
match x {
    1 | 2 | 3 => "small",
    4..=10 => "medium",
    _ => "large",
}
```

**Nomi** (supported): `case 1 | 2 | 3:` works via or_pattern in grammar.

---

## Guards (Conditional Patterns)

Extra boolean conditions on pattern matches.

**Rust / Haskell / Elixir (when)**:

```rust
match pair {
    (x, y) if x == y => "equal",
    (x, y) if x > y => "descending",
    _ => "ascending",
}
```

**Nomi** (supported): `case n if n > 10:` — guards already parse.

---

## Exhaustiveness Checking

Compile-time verification that all cases are covered.

**Rust / Swift / Kotlin (sealed class)**:

```rust
match value {  // error: non-exhaustive patterns
    Some(x) => ...,
    // None not covered
}
```

**Nomi** — runtime-only for now; compile-time requires type info (Track 4).

---

## Implementation Priority

| Feature | Effort | Impact |
|---------|--------|--------|
| Match as expression | done for expression-valued cases | high |
| If-let / while-let | done | high |
| Guard-let | implemented; exit diagnostics future | high |
| Exhaustiveness | high | medium |
| Destructuring all forms | partial | done |
