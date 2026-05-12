# String Convenience

## String Interpolation

Embed expressions directly in string literals.

**JavaScript / Kotlin / Ruby / Swift / Scala**:

```javascript
`Hello ${name}, you are ${age} years old`
```

```kotlin
"Hello $name, you are ${age} years old"
```

```ruby
"Hello #{name}, you are #{age} years old"
```

**Nomi** — f-string syntax (when parser supports it; currently blocked):

```nomi
f"Hello {name}, you are {age} years old"
```

---

## Multi-Line Strings / Heredocs

Strings spanning multiple lines without escape hell.

**Kotlin / Rust / Ruby / JavaScript**:

```kotlin
val sql = """
    SELECT * FROM users
    WHERE age > ${minAge}
    ORDER BY name
""".trimIndent()   // strips common leading whitespace
```

```rust
let sql = r#"
    SELECT * FROM users
    WHERE age > {minAge}
    ORDER BY name
"#;
```

```ruby
sql = <<~SQL
    SELECT * FROM users
    WHERE age > #{min_age}
    ORDER BY name
SQL
```

**Nomi proposal** — triple-quoted strings (already in Python, add to Nomi parser):

```nomi
sql = \"\"\"
    SELECT * FROM users
    WHERE age > {min_age}
    ORDER BY name
\"\"\"
```

---

## Raw Strings

Strings where backslashes are literal, not escape characters.  Essential
for regex patterns and Windows paths.

**Python / Rust / C#**:

```python
r"C:\Users\name"           # raw string
re.match(r"\d+", text)     # regex
```

```rust
r"C:\Users\name"
r#"raw string with "quotes" inside"#
```

**Nomi** — Python's `r"..."` available.

---

## String Methods as Infix / Operators

**Python (in operator)**:

```python
"sub" in "string"         # True
```

**Kotlin (operator overloading)**:

```kotlin
"hello" * 3               // "hellohellohello"
```

---

## Regex Literals

First-class regex syntax without string escaping.

**JavaScript / Ruby / Perl**:

```javascript
/pattern/flags.test(str)
str.match(/pattern/g)
```

```ruby
str =~ /pattern/
str.match?(/pattern/)
```

**Nomi** — use `re` module.  Regex literals not planned (keep as library).

---

## String Builder / Interpolation Builder

Efficient string construction with a builder pattern.

**Kotlin**:

```kotlin
val text = buildString {
    append("Hello, ")
    append(name)
    append("!")
}
```

**Nomi** — `"".join(...)` works; `StringIO` for streaming.

---

## Implementation Priority

| Feature | Effort | Impact |
|---------|--------|--------|
| Triple-quoted strings in Nomi parser | low | high |
| f-string support in Nomi parser | medium | high |
| `.trimIndent()` equivalent | low | medium |
| Regex literals | N/A | keep as library |
