# Strings

> Pillar, not a new normal form. Strings are the most universal interface
> between programs and humans, but this document does not expand Nomi's
> current eight-normal-form spine. String features reduce to existing owners:
> Data boundary (typed wrappers, serialization, safe construction), Pattern
> (literal and regex matching), Flow (transformation pipelines and collection
> verbs), Absence/result (parsing and search failure), and Explanation
> (display, diagnostics, redaction, source spans).
>
> This doc elevates strings from a subsection of data-and-types to a
> first-class design pillar alongside functions, collections, patterns, and
> data boundaries. A future capstone pass may decide that String deserves
> promotion to a ninth normal form, but that would be a language-design event,
> not a convenience-doc edit.
>
> Deep research: this doc is the first synthesis. A dedicated string-systems
> deep dive is a coverage priority. For now the cross-language survey draws from:
> Python (f-strings, str API, textwrap), JavaScript (template literals, tagged
> templates), Kotlin (string templates, trimMargin), Swift (extended delimiters,
> grapheme clusters, custom interpolation), Scala (custom interpolators, triple
> quotes), Rust (format!, String vs &str, UTF-8), C# (interpolation, verbatim,
> raw literals), Java (text blocks), Ruby (heredocs, %q, symbols), Elixir
> (sigils, IO data), Go (strings package, no interpolation), Haskell (Text vs
> String, OverloadedStrings).
>
> Interaction map: [interaction_map.md](interaction_map.md) connects strings to
> data boundary (typed strings), patterns (regex capture, string deconstruction),
> flow (pipeline over string transforms), and explanation (diagnostic display,
> error messages).

## Design Pressure

Strings are the most common data type after numbers. Every program constructs,
slices, searches, formats, and displays strings. Yet most languages treat
string handling as an afterthought — a grab-bag of methods on a type, a
formatting mini-language that doesn't compose, and no help for the
most dangerous operation: embedding strings in other languages (SQL, HTML,
shell).

The design pressures are:

1. **Safe construction.** Every string built from user data that crosses into
   SQL, HTML, shell, or another language boundary is an injection risk. The
   language should make safe construction the default path.

2. **Readable interpolation.** Users read interpolated strings more than they
   write them. The syntax must make expressions visible without drowning in
   delimiters.

3. **Clear representation.** Users should not need to think about internal
   encoding (UTF-8 vs UTF-16 vs grapheme clusters) for everyday operations.
   But they should be able to when it matters.

4. **Composable transformation.** String operations (split, join, filter,
   map over lines, trim, indent, wrap) should compose through the same
   pipeline/collection flow as everything else.

5. **One obvious ordinary string path.** Python's journey from `%` →
   `.format()` → f-strings is a cautionary tale. Nomi should have one
   `str`-producing interpolation syntax that is good enough to prevent
   alternatives from emerging.

6. **Typed wrappers beat stringly-typed code.** A Path is not a string. A
   URL is not a string. A regex pattern is not a string. These should be
   distinct types that accept strings at the boundary but don't decay back.

---

## 0. Normal-Form Ownership

String design crosses several normal forms. The coherence rule is that each
string feature must name its owner before it moves from research to spec:

| String feature | Normal-form owner | Reduction target |
|----------------|-------------------|------------------|
| Literal text and interpolation | Data boundary + Explanation | construct text; preserve expression spans for diagnostics |
| Typed string wrappers (`Path`, `Url`, `Sql`, `Html`, `Regex`) | Data boundary | decode or construct a trusted value from untrusted text |
| Regex capture and string destructuring | Pattern | test text, bind captures, preserve match failure vs constraint failure |
| Split/map/filter/join/lines/wrap | Flow | transform text through ordinary calls and collection verbs |
| Search, parse, decode, encode | Absence/result | return `none` or `Result`, not sentinel values or hidden exceptions |
| Display, debug, logging, redaction | Explanation | render structured values without losing secrecy or source context |

The important consequence: **string syntax does not get its own evaluator
semantics.** Literal sugar, typed interpolation, and regex capture must lower
to ordinary calls, pattern attempts, typed wrappers, and explanation events.

---

## 1. String Interpolation

### 1.1 Canonical Form: Extended f-strings

Nomi inherits Python's f-string syntax as the single ordinary `str`-producing
interpolation mechanism:

```nomi
name = "Nomi"
greeting = f"Hello, {name}!"

# Expressions work — the same expression syntax as everywhere else
f"{user.name} is {user.age} years old"

# Multi-line interpolation
f"""
Dear {recipient.title} {recipient.last_name},

Your order #{order.id} has shipped.
"""
```

**Design decision: f-string syntax is the one ordinary string interpolation
way.** Nomi rejects the Python fragmentation where `%`, `.format()`, `f""`,
and `string.Template` all coexist. f-strings won because the expression is
visible at the call site. The `f` prefix is learnable and searchable. Typed
interpolators such as `sql""` are not alternative ways to build `str`; they are
typed boundary constructors.

**Source reference:** Python f-strings, JavaScript `${expr}`, Kotlin
`$name ${expr}`, Swift `\(expr)`, Ruby `#{expr}`, C# `$"{expr}"`,
Scala `s"$name ${expr}"`, Dart `$name ${expr}`.

### 1.2 Expression Power

Python restricts f-string expressions (no backslashes, no comments
inside `{}`). Nomi should relax these where they don't harm readability:

```nomi
# Multi-line expressions in interpolation (Swift-like)
f"Total: {
    items
    |> select(_.price)
    |> sum
}"

# Nested f-strings should work (debugging use case)
f"Result: {f"inner value = {x}"}"

# Format specs (Python-compatible)
f"{value:.2f}"
f"{name:>20}"
```

**Status:** implemented (Python-compatible f-strings). Extended expression
power is design-settled for f-string expressions matching Nomi's expression
grammar.

### 1.3 Typed Interpolators (Design Direction)

Scala's custom string interpolators (`s"", f"", raw""`) and JavaScript's
tagged templates show a pattern worth adopting: let the prefix select a
processing mode. Nomi extends this to typed strings:

```nomi
# Candidate built-in prefixes for safe construction
sql"SELECT * FROM users WHERE id = {user_id}"     # → Sql literal, not str
html"<div class={cls}>{content}</div>"             # → Html literal, not str
re"\d{3}-\d{2}-\d{4}"                             # → Regex pattern, compiled
sh"tar -czf {archive} {path}"                     # → command value, not str

# Each prefix returns a distinct type — not a string
query: Sql = sql"SELECT ..."
template: Html = html"<p>{body}</p>"
```

Each custom prefix:
- Produces a distinct type (not `str`)
- Applies target-specific safe construction
- Is rejected at compile time if the prefix isn't imported/available
- Composes with the `Data.decode()` boundary

Target-specific means different things in different domains. SQL interpolation
should produce a query plus bound parameters, not escaped SQL text. HTML
interpolation must distinguish text nodes, attributes, URLs, and raw fragments.
Shell interpolation should prefer structured argument vectors or capability
scopes over shell-language strings. URL interpolation must encode path segments
and query parameters differently. The prefix dispatch mechanism can be shared,
but the safety contract is per target.

**Source reference:** Scala custom interpolators, JavaScript tagged
templates, Elixir sigils.

**Status:** design-needed as syntax and dispatch. The goal of distinct typed
wrappers is design-settled; the exact prefix grammar, lookup rules,
compile-time execution policy, and per-target safety contracts need a feature
packet before implementation.

### 1.3.1 The Desugaring Model

The key design insight from Scala and Elixir: **interpolation desugars into
a function call.** A prefix is not a language keyword — it is a function name:

```text
sql"SELECT * WHERE id = {id}"
→ StringContext("SELECT * WHERE id = ", "").sql(id)
```

In Scala, `s""`, `f""`, and `raw""` are built-in. Any library can define an
implicit class extending `StringContext` with a method `json(...)` returning
`Json`. The compile-time expansion means the method can return any type and
the compiler enforces it. No second mini-language for format specs.

Elixir's sigil model is even more general. `~r/pattern/iflags` desugars to
`sigil_r("pattern", ["i"])`. Lowercase = interpolation enabled; uppercase
(`~R`) = raw (no interpolation). Users define custom sigils as functions
`sigil_X/2`. Eight delimiter options let the user choose what doesn't
collide with content. Sigils run at compile time — `~r` compiles the regex
once. The mechanism is one two-argument function call. Nothing more.

Nomi should adapt both, but the final spelling is not settled:
- Prefix-triggered interpolation desugars to a function call (Scala model)
- Raw/interpolated mode is explicit; uppercase-as-raw is a candidate, not a
  commitment
- User-definable processors require an importable name and an inspectable
  expansion
- Compile-time execution is allowed only for known-safe processors with a
  sandboxed or declarative contract

```nomi
# Candidate custom processor:
# user defines string_processor json(parts, values, flags) -> Json
config = json"{\"key\": {value}}"              # → Json, not str
```

Open dispatch questions:
- Is the prefix resolved like an imported function, a method on `StringContext`,
  or a registered compile-time capability?
- Which processors may run at compile time, and how are side effects forbidden?
- How does `explain` display the expansion and the original source spans?
- How are raw mode, flags, and extended delimiters combined without creating a
  second mini-language?

### 1.4 Debug / Development Interpolation

Rust's `dbg!()` and Python's `f"{x=}"` (3.8+) make debugging convenient:

```nomi
# Expression-print form: prints "name = 'Nomi'" etc.
f"{name=}"       # → "name='Nomi'"
f"{x + y=}"      # → "x + y=42"

# Multi-value debug dump
debug"(x, y, z)"  # → "x=1, y=2, z=3"  (design-needed)
```

**Status:** `f"{expr=}"` is design-settled. `debug""` is design-needed.

---

## 2. String Literal Forms

### 2.1 Multi-Line Strings

```nomi
# Current prototype: Python-compatible triple-quoted string
doc = """
    line one
    line two
    """

# Future design target: indentation follows the closing delimiter
```

Kotlin's `trimMargin()` and Java's `String.stripIndent()` converge on the
same behavior: the common leading whitespace is removed. Java 13+ text
blocks take this further: the compiler determines the minimum indentation
across non-blank lines, strips it automatically, and the horizontal position
of the closing `"""` defines the margin. Content to the right of the closing
delimiter is "essential" indentation. C# 11 uses the same algorithm.

**Design direction: adopt the Java/C# closing-delimiter algorithm.** When
the closing `"""` is at indent N, strip N spaces from every non-blank line.
This eliminates the need for post-hoc `.dedent()` calls and makes multi-line
strings "just work" in indented code.

**Status:** implemented only as Python-compatible triple-quoted strings.
The auto-indent algorithm is design-needed until exact whitespace rules,
diagnostics, and compatibility with current Python behavior are specified.

### 2.2 Raw Strings

```nomi
# No escape processing
path = r"C:\Users\name\docs"
pattern = r"\d+\.\d+"

# Combined with multiline
regex = r"""
    \d{3}   # area code
    -
    \d{3}   # exchange
    -
    \d{4}   # subscriber
    """
```

**Status:** implemented (Python-compatible `r""`). Extended delimiters
(Rust model) are design-needed as a future enhancement.

### 2.3 Extended / Custom Delimiters (Design Direction)

Python's `r""` has a well-known edge case: `r"\"` is a syntax error because
a raw string can't end with a backslash. Every Python developer hits this.

Rust's delimiter escalation (`r###"..."###`) eliminates ALL edge cases:
the string starts with `r`, then N `#` characters, then `"`, then content,
then `"`, then N `#` characters. To embed `"#` in content, add one more `#`
to the delimiter. There is no content that cannot be embedded — you can
always escalate. Swift's extended delimiters (`#"..."#`) work identically.

```nomi
# Rust-style delimiter escalation
json = r#"{"name": "Nomi", "version": "0.1"}"#

# More # characters let the content contain "# without escaping
text = r##"This contains "# inside the text"##

# For strings containing "# — add more # delimiters (always works)
text = r###"This contains "# and "## delimiters"###

# The general rule: r#...# always works. No edge cases. No backslash standing
# before closing quote. No "" doubling. Just add more #.
```

**Source reference:** Rust `r#"..."#` (zero edge cases), Swift `#"..."#`
(extended delimiters with `\#(expr)` for interpolation), C# 11 raw string
literals (quote-count escalation).

**Status:** design-needed. Python's `r""` covers many cases already;
Rust-style delimiter escalation is a later priority but is the correct
long-term candidate because it eliminates the `r"\"` edge case permanently.
Interpolation inside extended delimiters remains an open spelling question
(Swift uses explicit escaped interpolation; Rust raw strings do not
interpolate).

### 2.4 Heredocs (Rejected)

Ruby, PHP, and shell heredocs solve multi-line with embedded quotes, but
they break indentation and have complex delimiter rules. Triple-quoted
strings with extended delimiters cover the same use case more cleanly.

**Status:** rejected-for-now. Triple-quoted strings + extended delimiters
cover heredoc use cases without a second multi-line mechanism.

---

## 3. String API

### 3.1 Methods on `str`

Nomi inherits Python's rich string method vocabulary. The principle:
common operations are methods on `str`; rare operations are library
functions.

```nomi
# Everyday operations — methods
name.strip()
name.lower()
name.startswith("Dr.")
name.replace("_", " ")
", ".join(items)
text.split("\n")
text.splitlines()

# Search
text.contains("needle")     # → bool
text.index_of("needle")     # → int? (None if not found)
```

**Design fork: methods vs free functions.** Python and Ruby use methods
on the string object. Go uses package-level functions (`strings.Split`).
Rust uses methods on `str` that return iterators (`split()`, `lines()`,
`chars()`) — avoiding eager allocation. Nomi keeps methods for
discoverability (IDE autocomplete) but uses iterator returns for operations
that produce multiple values, letting the user collect into the desired type:

```nomi
# Iterator returns — no eager allocation
for word in text.split():
    ...

# Collect when you need a concrete collection
words = text.split() |> collect(list)
unique_words = text.split() |> collect(set)
```

```nomi
# Pipeline over strings — free functions compose
cleaned = text
    |> strip
    |> replace(_, "  ", " ")
    |> splitlines
    |> select(where(_, not _.is_empty))
```

### 3.2 Collection Verbs on Strings

Strings are text values with multiple useful views: bytes, code points,
grapheme clusters, lines, words, and display cells. Collection verbs should
work through an explicit view so the iteration unit is visible:

```nomi
# Map over code points / one-code-point strings
"hello".code_points() |> select(chr(_).upper()) |> collect(into: str)

# Filter through a character-like view
"a1b2c3".chars() |> where(_.is_digit()) |> collect(into: str)

# Fold/reduce
"hello".code_points() |> fold(0, (acc, cp) -> acc + cp)

# Lines as a lazy sequence
text.lines() |> where(_.starts_with("ERROR"))
```

**Status:** basic collection iteration is implemented (Python string
iteration). Collection verb vocabulary for strings is design-settled, but
the default string view for `|> where` / `|> select` is design-needed.

### 3.3 String Builder (Library-First)

For performance-sensitive string construction (loops, large concatenation):

```nomi
# Builder pattern — mutable, efficient
result = build_string():
    .append("Header\n")
    .append_line(f"Item {i}")  # adds \n
    .extend(lines)

# Or: collect into string
result = items |> select(_.name) |> collect(into: str, sep: ", ")
```

**Source reference:** Kotlin `buildString {}`, Java `StringBuilder`,
Rust `String::with_capacity`, Go `strings.Builder`.

**Status:** library-first. The core language provides immutable `str`;
`build_string` is a library concern.

### 3.4 String Formatting / Padding / Alignment

```nomi
# Format specs on f-string expressions
f"{name:>20}"          # right-align in 20
f"{name:<20}"          # left-align
f"{name:^20}"          # center
f"{price:.2f}"         # two decimal places
f"{ratio:.1%}"         # percentage

# Programmatic padding (library)
"hello".pad_left(10)     # "     hello"
"hello".pad_right(10)    # "hello     "
"hello".center(10)       # "  hello   "
```

**Status:** f-string format specs are implemented (Python-compatible).
Programmatic padding is prototype-ready.

---

## 4. Typed Strings

### 4.1 The Problem

"Stringly-typed" code uses `str` for things that are not strings:
file paths, URLs, SQL queries, HTML fragments, regex patterns, shell
commands, email addresses, phone numbers. This causes:

- **Injection**: `f"SELECT * FROM users WHERE name = '{name}'"` — every
  language with string interpolation has this bug.
- **Confusion**: `open(path)` vs `open(url)` — both take strings, one
  hits the filesystem, the other the network.
- **Accidental coupling**: `path + "/" + filename` breaks on Windows.
  `url + "/" + endpoint` breaks when the base URL has a path.

### 4.2 Distinct Types

Nomi's design should provide distinct types for common string-like values:

```nomi
# Path — not a string
config_path: Path = Path("./config.toml")
config_path / "subdir" / "file.txt"     # / operator joins
config_path.extension()                  # "toml"
config_path.parent()                     # Path("./")

# URL — not a string
api: Url = Url("https://api.example.com/v1")
api / "users" / user_id                  # / joins path segments
api.with_query("page", "2")             # query params, properly encoded

# SQL — not a string
query: Sql = sql"SELECT * FROM users WHERE id = {user_id}"
# user_id is bound as a parameter; query is a Sql value, not str

# HTML — not a string
page: Html = html"<div class={cls}>{content}</div>"
# content is escaped according to HTML context; page is an Html value, not str

# Regex — not a string
pattern: Regex = re"\d{3}-\d{2}-\d{4}"
# Future target: compiled once and captures produce typed match objects
```

### 4.3 Conversion Protocol

Typed strings have explicit conversion to/from `str`:

```nomi
# str → Typed: explicit boundary crossing
path = Path("./data")         # from str
url = Url("https://...")      # from str

# Typed → str: explicit extraction
path_str = path.to_str()      # Path → str (platform-native)
url_str = url.to_str()        # URL → str (encoded)

# Implicit coercion into str-accepting APIs is rejected
open(path)                   # fine: open expects Path
write_text(path.to_str())    # explicit extraction when a raw str is required

# Display is not coercion
f"The path is {path}"         # uses Path.Display
path_str = path.to_str()      # explicit platform-native string extraction
```

This builds on Nomi's Data Boundary normal form: typed wrappers are the
boundary between untyped string data and typed string values.

**Source reference:** Python `pathlib.Path`, Rust `Path`/`PathBuf`/`Url`,
Java `java.nio.Path`, Scala `os.Path`, Go `net/url.URL`.

**Status:** `Path` is design-settled as a standard-library value. `Url`,
`Sql`, `Html`, `Regex`, and command values are design-needed as a family:
the wrapper principle is settled, but each type needs construction,
conversion, display, redaction, and sink contracts before implementation.

---

## 5. Pattern Matching on Strings

### 5.1 Destructuring

String destructuring through pattern matching:

```nomi
# Match on literal strings
match status:
    case "ok": handle_ok()
    case "error": handle_error()

# Match with regex captures (design-needed)
match text:
    case re"(\d{3})-(\d{2})-(\d{4})" as area, exchange, subscriber:
        format_ssn(area, exchange, subscriber)
    case re"(\w+)@(\w+\.\w+)" as user, domain:
        validate_email(user, domain)

# Match with guards on strings
match command:
    case cmd if cmd.starts_with("GET "): handle_get(cmd)
    case cmd if cmd.starts_with("POST "): handle_post(cmd)
```

### 5.2 Regex Integration

Regex remains library-first (not a second pattern language in the
grammar), but gets first-class integration through typed wrappers and
pattern capture:

```nomi
# Compiled regex — explicit, named, composes
ssn_pattern = re.compile(r"(\d{3})-(\d{2})-(\d{4})")

# Match as expression
match_result = ssn_pattern.match(text)
if match_result:
    area, exchange, subscriber = match_result.groups()

# Find all with named groups
for match in ssn_pattern.find_all(document):
    print(match["area"], match["exchange"], match["subscriber"])

# Replace with function
result = ssn_pattern.replace(text, (m) -> f"***-**-{m[3]}")
```

**Source reference:** Python `re` module, Rust `regex` crate, Elixir
`~r/` sigil, JavaScript regex literals, Scala `.r` method.

**Status:** Python-compatible `re` module is implemented. A `Regex` typed
wrapper and regex capture in `match` are design-needed until the engine policy,
capture binding form, named-group behavior, failed-match diagnostics, and
catastrophic-backtracking stance are specified. Regex as a language literal
(like JS `/re/`) is rejected; typed string construction is the preferred path.

### 5.3 String Slicing and Indexing

```nomi
# Python-compatible slicing
text[0]        # first character (string of length 1)
text[0:5]      # first 5 characters
text[-1]       # last character
text[::2]      # every other character

# Grapheme-cluster-aware indexing (design-needed)
text.graphemes()[0]    # first user-perceived character (Swift model)
```

**Design fork:** Swift exposes `String` as grapheme clusters, which makes
integer indexing intentionally unavailable and many index operations O(n).
Python exposes code-point indexing with an implementation-dependent storage
layout. Nomi keeps Python-compatible indexing for now and adds grapheme-cluster
access as explicit opt-in.

**Status:** Python-compatible slicing is implemented. Grapheme-cluster
access is design-needed as a library view, including Unicode-version policy
and indexing complexity guarantees.

---

## 6. String Representation

### 6.1 Internal Encoding

Nomi's `str` is immutable and stores valid Unicode. The internal encoding
(UTF-8, UTF-16, or hybrid) is an implementation detail, not part of the
language definition. The Python prototype uses Python's flexible string
representation (ASCII-compact, UCS-1, UCS-2, UCS-4 depending on content).

**Design fork:** Rust and Go mandate UTF-8 at the language level. Swift
uses UTF-8 internally but exposes grapheme clusters. Java and C# use
UTF-16 with surrogates. Python 3 uses a flexible representation.

Nomi's position: the language spec says "valid Unicode, immutable."
The internal encoding is the runtime's choice. The prelude provides:
- `str.to_utf8() -> bytes`
- `str.from_utf8(bytes) -> Result[str, DecodeError]`
- `str.code_points() -> Iterator[int]`
- `str.graphemes() -> Iterator[str]`

### 6.2 String vs Bytes

```nomi
# str is Unicode text
text: str = "hello"

# bytes is raw octets
data: bytes = b"hello"

# Explicit conversion at boundaries
text = str.from_utf8(data)    # Result[str, DecodeError]
data = text.to_utf8()         # bytes
```

### 6.3 Interning and Performance

String interning is a runtime optimization, not a language feature.
Nomi's runtime MAY intern string literals and short-lived temporaries,
but the language semantics don't depend on identity comparison for
strings (`==` is value equality, always).

**Source reference:** Python's automatic interning of identifiers, Java's
`String.intern()`, Rust's `&str` vs `String`, Ruby's frozen strings.

---

## 7. Serialization and Display

### 7.1 Display vs Debug

Rust's `Display`/`Debug` distinction is worth adopting:

```nomi
# Display — human-readable, no quotes, no type wrapper
print(f"Hello, {name}")       # Hello, Nomi

# Debug — developer-readable, with quotes and type info
print(f"{name:?}")            # "Nomi" (str)
print(f"{path:?}")            # Path("./config.toml")
print(f"{secret:?}")          # Secret("***")  (redacted)
```

Every type implements `Display` (human) and `Debug` (developer). The
`:?` format spec switches to Debug.

**Status:** design-settled.

### 7.2 The Format Protocol

Nomi extends Python's `__format__` protocol so custom types control how
they appear in f-strings:

```nomi
# Python-compatible: type defines __format__
data Point:
    x: float
    y: float

    func __format__(self, spec: str) -> str:
        match spec:
            case "": return f"({self.x}, {self.y})"
            case "p": return f"({self.x:.1f}, {self.y:.1f})"
            case _: return f"Point({self.x}, {self.y})"

p = Point(3.5, 7.2)
f"{p}"       # "(3.5, 7.2)"
f"{p:p}"     # "(3.5, 7.2)"
```

---

## 8. Unicode Handling

### 8.1 Design Position

Unicode is the one true character set. Nomi source files are UTF-8.
The `str` type stores Unicode text. There is no `unicode` vs `str`
distinction (Python 2's most painful migration). There is no "default
encoding" that varies by platform.

Nomi should name the text unit being used instead of pretending there is one
universal "character":

| Unit | Meaning | Typical use |
|------|---------|-------------|
| byte | raw octet | files, network, hashing, binary protocols |
| code point | Unicode scalar value; Python-compatible indexing exposes this as a one-code-point string today | parsing, simple transforms, compatibility |
| grapheme cluster | user-perceived character | cursor movement, emoji-safe slicing, UI text |
| display cell | terminal/editor column width | alignment, tables, diagnostics |

The default prototype behavior is Python-compatible. The design target is a
small set of explicit views (`bytes`, `code_points`, `graphemes`,
`display_cells`) so correctness-sensitive code can say what it means.

```nomi
# Normalization — four Unicode normalization forms (library)
"café".normalize("NFC")    # → composed (canonical)
"café".normalize("NFD")    # → decomposed (canonical)
"ｶﾌｪ".normalize("NFKC")   # → compatibility composed
"ｶﾌｪ".normalize("NFKD")   # → compatibility decomposed

# Case folding (locale-aware opt-in)
"STRASSE".lower()             # "strasse" (Unicode default)
"STRASSE".lower(locale="tr")  # "strasse" (Turkish İ → i, not I)

# Explicit canonical equivalence check (no auto-normalization)
"café".nfc_eq("café")   # True (compare in NFC)
```

**Design fork: auto-normalization for equality.** Swift normalizes strings
before comparison: `"é" == "e\u{301}"` is true because Swift applies
canonical equivalence. Every other language treats these as different
strings. Nomi follows the majority: `==` compares code-point-by-code-point.
Canonical equivalence is explicit via `str.nfc_eq(other)`.

The reason: normalization changes representation, compatibility
normalization can be lossy, locale-sensitive comparisons are culturally
variable, and automatic normalization adds runtime cost. Making it explicit
keeps string comparison predictable and fast, while still making the correct
comparison easy to reach.

**The Turkish-i problem.** Uppercase `I` in Turkish is `İ` (dotted) and
lowercase `ı` (dotless). `"FILE".lower(locale="tr")` produces `"fıle"` —
not `"file"`. This is the canonical example of why locale-sensitive string
operations must be opt-in. Unicode-default case operations use the Common
locale; locale-specific operations require an explicit locale parameter.

### 8.2 Grapheme Cluster Awareness

Swift's model is the gold standard: `String` is a collection of
`Character` values, where each `Character` is an extended grapheme
cluster — one or more Unicode scalars forming a single user-perceived
character. `"👨‍👩‍👧‍👦".count == 1` in Swift (it's one family emoji,
visually one character) but 7 Unicode scalars.

Swift also canonicalizes string equality: `"é"` (U+00E9 precomposed)
equals `"e\u{301}"` (e + combining acute). This is correct but depends
on ICU for grapheme breaking, adds binary size, and changes behavior
across Unicode versions.

Nomi adopts grapheme-cluster awareness as opt-in, not default:

```nomi
# Default: code-point indexing (O(1), predictable, Python-compatible)
text[0]               # first code point

# Opt-in: grapheme-cluster view (correct for user-facing operations)
text.graphemes()[0]   # first user-visible character
text.grapheme_count() # number of user-visible characters

# Emoji-safe substring
"👨‍👩‍👧‍👦".grapheme_count()  # 1
```

The Swift maintainers' principle guides the design: "degenerate cases
can be weird in service of making realistic/important usage better." But
the cost — no O(1) indexing ever — is too high for a language that
prioritizes predictability. Make the 99% case easy (grapheme counting,
emoji-safe substrings) without breaking the 1% case (O(1) code-point
access for systems programming).

**Status:** Python-compatible indexing is implemented. Grapheme-cluster views,
display-cell width, locale-aware case operations, collation, and Unicode
version pinning are library-first design work.

---

## 9. Security

### 9.1 Injection Prevention

The primary injection vector in every language is string concatenation into a
structured context (SQL, HTML, shell, XML, JSON, CSS, URLs). Nomi's defense is
not "escape everything"; it is **make the target context explicit and typed**:

1. **Typed wrappers** (`Sql`, `Html`, command values) that are NOT subtypes of
   `str`.
2. **Custom interpolators** (`sql""`, `html""`) that produce typed wrappers
   via the prefix-dispatch mechanism (see §1.3.1).
3. **No implicit coercion** — `Sql` doesn't decay to `str`; you must call
   `.to_str()` explicitly.
4. **Parameterized or context-aware by default** — `sql"..."` binds values as
   parameters, `html"..."` escapes according to HTML context, URL builders
   encode path and query segments differently, and command APIs prefer argv
   values over shell-language strings.

```nomi
# Safe: user_id is parameterized, not string-concatenated
query = sql"SELECT * FROM users WHERE id = {user_id}"

# Type error: can't use Sql where raw str is expected
execute(query)  # execute() takes Sql, not str

# Wrong but explicit: raw string construction
# (requires .raw() to opt out — visible in code review)
dangerous = Sql.raw(f"SELECT * FROM users WHERE id = '{user_id}'")
```

### 9.2 The Taint-Tracking Lesson

Perl's `-T` taint mode (1989) was the most comprehensive language-level
injection defense: external data is marked tainted, derived data inherits
taint, tainted data can't touch dangerous operations (`eval`, `system`,
`exec`, file open) without explicit untainting via regex capture validation.
Ruby had `$SAFE` levels with `taint`/`untaint` methods.

Both failed. Ruby removed `taint`/`untaint` in 2.7-3.0 because the
ecosystem (Rails, Rack) never integrated with it. The lesson: **language-level
taint tracking only works if the entire ecosystem participates.** A new
language cannot mandate this from day one.

Nomi's approach: **make safe sinks typed.** `execute()` takes `Sql`, not
`str`; `render()` takes `Html`, not a raw template string; `run()` takes a
command value or argv list, not a shell snippet by default. This is cheaper
than full taint tracking and more reliable than framework conventions, while
still allowing explicit escape hatches such as `Sql.raw(...)` for migration and
low-level interop.

**Source reference:** Perl taint mode (comprehensive, ecosystem-ignored),
Ruby `$SAFE`/`taint`/`untaint` (removed in 2.7-3.0), Rust newtype wrappers
for safe strings, Haskell `newtype`, Scala opaque types.

### 9.3 Secrets in Strings

`@secret` fields (from `data_and_types.md`) apply to string values:

```nomi
data Credentials:
    @secret password: str

creds = Credentials(password="hunter2")
f"Password: {creds.password}"   # "Password: Secret("***")"
f"Password: {creds.password:?}" # "Password: Secret("***")"
```

### 9.4 Log Sanitization

Logs and diagnostics should redact `@secret` fields by default. The
`explain --unsafe` flag shows raw values for debugging:

```nomi
explain(creds)           # shows redacted
explain --unsafe(creds)  # shows raw values
```

---

## 10. Library-First Decisions

Features that belong in libraries, not the language:

| Feature | Reason |
|---------|--------|
| Regex literals (`/pat/`) | `re""` typed string covers this; JS-style literals add escape problems |
| Heredocs (`<<EOF`) | Triple-quoted strings + extended delimiters are sufficient |
| String templates (like `string.Template`) | f-strings are the one mechanism |
| `%` formatting, `.format()` | Rejected; f-strings are the one way |
| `char` type | `str` of length 1 covers it; a separate `char` type adds conversion pain |
| `symbol` type (Ruby-style) | Interned strings are a runtime optimization, not a language type |
| `byte` string literal variants beyond `b""` | `bytes` covers raw octets |

---

## 11. Spec Packet Needed

Before typed interpolation or Unicode-aware string views move into the
implementation queue, they need a feature packet with these decisions:

| Area | Required decision |
|------|-------------------|
| Prefix grammar | Which prefixes are legal, how raw/interpolated mode composes with `r""`, `f""`, triple quotes, and extended delimiters |
| Name lookup | Whether `sql""` resolves as an imported function, a registered processor, a method on a context object, or a standard-prelude form |
| Lowering | Exact desugaring into parts, values, flags, source spans, and target type |
| Compile-time execution | Which processors may run at compile time; sandbox, purity, caching, and error reporting rules |
| Safety contracts | SQL parameterization, HTML context escaping, URL path/query encoding, command argv construction, regex compilation policy |
| Regex engine | Backtracking vs linear-time engine, flags, Unicode classes, named captures, replacement semantics |
| Unicode views | Default iteration unit, grapheme library dependency, Unicode version pinning, display-width policy |
| Conversion | `to_str()`, `Display`, `Debug`, redaction, logging, and serialization contracts for each typed wrapper |
| Diagnostics | How syntax errors, unsafe raw construction, failed regex compilation, and context-mismatched interpolation are explained |
| Explainability | Machine-readable expansion events connecting source literal parts to constructed typed values |

This is the bridge from ambitious design to implementation-quality work. Until
the packet exists, typed string wrappers remain a direction, not a parser task.

---

## 12. Implementation Status

| Feature | Status |
|---------|--------|
| f-string interpolation | implemented |
| f-string `{expr=}` debug form | design-settled |
| Multi-line triple-quoted strings | implemented |
| Raw strings (`r""`) | implemented |
| Python-compatible string methods | implemented |
| Iterator-returning methods (`split()`, `lines()`) | design-needed |
| Extended delimiters (`r##"..."##`) | design-needed |
| Auto-indent stripping (Java/C# closing-delimiter model) | design-needed |
| `sql""` / `html""` / `re""` / `sh""` typed strings | design-needed |
| Custom prefix/interpolator dispatch (sigil model) | design-needed |
| `Path` type (not str) with `/` operator | design-settled |
| `Url` type (not str) | design-needed |
| Regex capture in `match` patterns (Scala extractor model) | design-needed |
| Display vs Debug format (`:?`) | design-settled |
| `__format__` protocol | implemented (Python) |
| Collection verbs over strings (pipeline-compatible) | design-needed for default string view |
| `build_string` / `StringBuilder` | library-first |
| Grapheme-cluster access | library-first, design-needed |
| Unicode normalization / case folding | library-first |
| Locale-aware case operations | library-first |
| Canonical equivalence (`nfc_eq`) | library-first |
| `@secret` field redaction in display | design-settled |
| `explain --unsafe` | design-settled |
| Opaque safe string types (injection prevention at type level) | design direction; needs per-sink contracts |
| Language-level taint tracking | rejected |
| Heredocs (`<<EOF`) | rejected-for-now |
| Regex literals (`/pat/`) as grammar-level syntax | rejected |
| `symbol` type (interned-string type) | rejected |

---

## 13. Design Context

This doc establishes the **String pillar** as a first-class design concern
alongside functions, collections, patterns, and data boundaries. It is not
currently a ninth normal form; it is a cross-cutting pillar whose features must
reduce to existing normal forms before they become syntax.
For the broader picture:

- [Language Foundation §Primitive Cognitive Acts](../language/language_foundation.md) —
  strings cross-cut Distinguish, Transform, Choose, and Touch the World.
- [Data Boundary](data_and_types.md) — `Data.decode()` protocol, `@secret`
  fields, typed wrappers that make strings safe at boundaries.
- [Patterns](patterns.md) — regex capture in `match`, string deconstruction,
  guard patterns on string values.
- [Flow & Collections](flow_and_collections.md) — pipeline over string
  transforms, collection verb vocabulary applied to strings.
- [Absence & Result](absence_and_result.md) — `str.index_of()` returns
  `int?` not `-1`; parse failures return `Result` not throw.
- [Design Lessons & Integration](design_lessons_and_integration.md) —
  Python's string formatting fragmentation, SQL injection as the most
  famous second-language problem, Swift's grapheme-cluster surprise.
- [Syntax Design Rules](syntax_design_rules.md) — regex literals as
  library-first; typed strings through prefix dispatch rather than
  language syntax.
- [Language Spec §Strings](../language/language_spec.md) — core string
  type, interpolation, literals, conversion.
- **Coverage priority:** A dedicated `string_systems_deep_dive.md` is
  needed in `docs/research/` covering the full spectrum: interpolation
  design space, typed strings, regex integration, Unicode policies,
  display-width/collation/localization, shell and SQL safety, and format
  protocols across 12+ languages.
