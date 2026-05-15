# Formatting and Style: Deep Dive

> Status: source research for Nomi design.
> Purpose: Understand how programming languages handle formatting, style, and
> the shared visual culture that reduces cognitive load — and extract a
> formatter doctrine for Nomi grounded in what the ecosystem has proven works.

## 1. The Formatting Problem

Code is read far more than it is written. Every programmer knows this, yet
formatting was traditionally treated as personal preference — tabs vs spaces,
brace placement, line length. The result was predictable: style arguments in
code review, inconsistent codebases, and cognitive overhead every time you
switch files.

The formatter-as-tool movement changed this. Instead of negotiating style, a
team agrees on a formatter and lets it make the decisions. The key insight,
articulated most clearly by Rob Pike for `gofmt`, is that **the particular
style matters less than having ONE style.** Formatting is a coordination
problem, not an aesthetic problem.

This document surveys ten formatting systems across the language landscape,
extracts structural invariants, identifies genuine tradeoffs, and builds a
formatter doctrine for Nomi. The goal is not to copy any single system — it is
to understand the design space so Nomi's choices are deliberate, not accidental.

---

## 2. gofmt — The Canonical Formatter

### 2.1 Philosophy

gofmt is the most influential formatter in programming language history. It
shipped with Go 1.0 in 2012 and was not an optional tool — it was part of the
language distribution itself. The philosophy is captured in a single sentence
often attributed to Rob Pike: **"Gofmt's style is no one's favorite, but
gofmt is everyone's favorite."**

The "no configuration" stance is absolute. There is no `.gofmt` file. There
are no flags beyond `-w` (write in place) and `-s` (simplify). You cannot
configure gofmt to use 2-space indentation, to put braces on a new line, or to
use a different import ordering. The output is **the** canonical representation
of the Go program.

This was a deliberate sociological intervention. The Go team had watched C++
teams spend hours arguing about `.clang-format` settings, watched Python
projects fracture over PEP 8 interpretations, and decided that the only way to
end the style war was to make it impossible to fight.

### 2.2 How It Works

gofmt is not a pretty-printer in the traditional sense. It parses the source
into Go's AST (`go/parser`), then prints the AST using `go/printer` with a
fixed set of formatting rules. There is no intermediate "style model" — the
printer walks the AST and emits tokens directly with whitespace and
indentation determined by the tree structure.

The crucial property: `gofmt(gofmt(x)) == gofmt(x)`. The formatter is
idempotent. This is not trivial — many naive formatters oscillate on
repeated application.

### 2.3 Precise Formatting Rules

**Tabs vs spaces:** Go uses tabs for indentation, spaces for alignment. This
is enforced by gofmt. The argument: tabs let each developer set their own
display width without changing the file. A tab means "one level of
indentation"; its visual width is a viewer preference.

**Brace placement:** Opening brace on the same line as the statement being
opened, always. This is enforced by the lexer — Go's semicolon insertion
rules make the alternative a parse error. There is literally no valid Go
program where a brace opens a block on a new line.

```go
// This is the only valid Go:
func add(x, y int) int {
    return x + y
}

// This is a parse error:
func add(x, y int) int
{
    return x + y
}
```

**Import ordering:** gofmt groups imports into two blocks: standard library
first, then third-party, separated by a blank line, alphabetically within each
group:

```go
import (
    "fmt"
    "os"

    "github.com/user/pkg"
    "golang.org/x/tools"
)
```

**goimports** extends gofmt by adding and removing imports automatically. It
resolves the import path for any symbol used in the file and inserts the
correct `import` statement. This eliminates an entire class of manual work:
the programmer never writes import statements.

**Expression formatting:** gofmt uses a cost-based line-breaking algorithm.
The printer tries to fit expressions within a soft limit (roughly 80 columns)
and breaks lines at "best" points when expressions are too long. The algorithm
is not a simple greedy break; it considers multiple break points and chooses
the one that minimizes "ugliness" defined by the distance from the right
margin.

**Struct literals:**

```go
// Compact fits on one line:
p := Point{X: 10, Y: 20}

// Multi-field gets one per line:
config := Config{
    Host:    "localhost",
    Port:    8080,
    Timeout: 30 * time.Second,
}
```

### 2.4 What Worked Exceptionally Well

**Ending the style war.** Go codebases look the same regardless of who wrote
them. Reading a new Go project requires zero mental adaptation to a new style.

**Code review transformation.** Style comments in code review went from "put
a space before the brace" to actual design feedback. This is the single
largest quality-of-life improvement reported by Go teams.

**Tooling ecosystem.** Because every Go program has a canonical representation,
tools that operate on Go source can assume gofmt output. `gorename`, `guru`,
`gopls` — all assume gofmt-formatted input. This is a network effect: one
canonical form enables a richer tooling ecosystem.

**Refactoring diff quality.** When every file is canonical, a refactoring that
changes one thing changes exactly one line (modulo knock-on effects). Without
a canonical form, the same refactoring might trigger reflow that obscures the
actual change.

**The AST-to-string property.** gofmt's output is deterministically derived
from the AST. Two programs with the same AST produce identical output. This
means diff tools can compare ASTs instead of text, eliminating formatting
noise entirely from semantic diffs.

### 2.5 What Created Friction

**No configuration means no escape for genuine preferences.** Some developers
genuinely prefer 2-space indentation and find tabs uncomfortable. gofmt says:
you don't get a choice. The Go community considered this acceptable collateral
damage, but it is real friction.

**Line length is not configurable.** gofmt does not enforce a hard line length
limit. It tries to keep lines short but will produce long lines for deeply
nested expressions. Some teams add a `golangci-lint` rule for line length, but
this creates tension — the canonical formatter doesn't guarantee short lines.

**Generics formatting (Go 1.18).** When generics were added, gofmt needed new
rules for type parameters. The initial rules were imperfect — long type
parameter lists produced awkward formatting — and improved over several
releases. This highlights that the formatter must evolve with the language,
and the "no configuration" stance means the formatter maintainers must get the
formatting right for everyone.

**Generated code.** Some code generators produce output that doesn't pass
gofmt. The convention is to run `gofmt -w` on generated files, but this adds
a build step.

### 2.6 Key Structural Insight for Nomi

**Canonical representation is a superpower.** It enables tooling, improves
code review, eliminates bike-shedding, and makes refactoring diffs
semantically meaningful. The cost — no individual preference — is worth paying
because the social benefit (one style for all code) overwhelms individual
aesthetic preferences.

The second insight: **integrate the formatter into the language toolchain, not
as an afterthought.** gofmt shipped with Go 1.0. It was not added later. This
meant the Go community never developed competing styles — there was never a
"pre-gofmt" style to argue about.

---

## 3. Black (Python) — The Uncompromising Formatter

### 3.1 Philosophy

Black's tagline is "The Uncompromising Code Formatter." The philosophy is
similar to gofmt's — deterministic, opinionated, minimal configuration — but
Black operates in a very different ecosystem. Python had 25+ years of
formatting history before Black arrived in 2018. PEP 8 existed. Multiple
linters (flake8, pylint) enforced competing interpretations. Every project had
its own `.editorconfig`, its own line-length preference, its own quoting
convention.

Black's insight: **determinism beats configurability.** Given the same input,
Black always produces the same output. Period. There is no ambiguous
formatting — the algorithm makes a deterministic choice at every decision point.

Black allows exactly two configuration options: `--line-length` (default 88)
and `--target-version` (Python 3.x variants). That's it. No flag for
single-vs-double quotes. No flag for trailing commas. No flag for blank lines
between functions. Every other choice is made by the tool.

The 88-character line length is a studied choice. Research showed that 80
characters is a historical artifact (punch cards had 80 columns) and that 88
allows roughly 10% more content per line while still fitting comfortably in
side-by-side diffs on modern monitors. It's also visually memorable as a
power-of-two-ish number.

### 3.2 How It Works

Black parses Python source into a Concrete Syntax Tree (CST) using the
`lib2to3` parser (originally) and now its own parser. It then formats the CST
into a string using a cost-based line-breaking algorithm.

The algorithm:

1. **Parse** the source into a CST that preserves comments and whitespace.
2. **Normalize** the CST: convert single quotes to double quotes where
   possible, normalize numeric literals, remove redundant parentheses, add the
   "magic trailing comma" where appropriate.
3. **Format** the CST into lines using a greedy line-breaking algorithm:
   - Try to fit the expression on one line.
   - If it doesn't fit, break at the "best" point (lowest indentation,
     earliest in the expression) and recurse.
   - The algorithm is not globally optimal — it makes greedy local decisions
     — but the determinism guarantee means the result is consistent.

The key algorithmic choice: **Black never reflows previously broken lines.**
If a line is broken at a certain level, all subsequent levels are broken too.
This is what makes `Black(Black(x)) == Black(x)` — the first run decides the
break structure, and subsequent runs see the same structure.

### 3.3 Precise Formatting Rules

**Quoting:** Black prefers double quotes. If a string contains double quotes,
Black uses single quotes. This minimizes escaping:

```python
# Before:
x = 'hello world'
y = "it's a nice day"

# After:
x = "hello world"
y = "it's a nice day"  # double quotes, no escaping needed for apostrophe
```

**The Magic Trailing Comma:** This is Black's most controversial feature. A
trailing comma in a collection literal tells Black to "explode" the
collection — one element per line. Remove the trailing comma, and Black
collapses it back to a single line if it fits:

```python
# Without trailing comma — collapses if it fits:
result = [1, 2, 3, 4, 5]

# With trailing comma — always exploded:
result = [
    1,
    2,
    3,
    4,
    5,
]
```

The user controls the format by adding or removing the trailing comma. This is
a rare case where Black gives the user agency over formatting — through a
syntactic signal rather than a configuration option.

**Expression wrapping:** Black wraps long expressions at the highest possible
syntactic level:

```python
# Before:
result = some_function(arg1, arg2, arg3, arg4, arg5, arg6, arg7, arg8, arg9, arg10)

# After — wraps the whole call, not individual arguments:
result = some_function(
    arg1, arg2, arg3, arg4, arg5, arg6, arg7, arg8, arg9, arg10
)

# With a function call chain:
result = (
    df.groupby("column")
    .agg({"value": "sum"})
    .reset_index()
    .rename(columns={"value": "total"})
)
```

**Blank lines:** Black normalizes blank lines. Two blank lines before
top-level definitions, one blank line between methods. Extra blank lines are
removed. This is one of Black's most subtle but impactful normalizations.

**Whitespace inside brackets:** Black removes whitespace inside empty brackets
and normalizes to a single space inside non-empty ones:

```python
# Before:
x = [ 1, 2, 3 ]
y = [    ]

# After:
x = [1, 2, 3]
y = []
```

### 3.4 What Worked Exceptionally Well

**Cultural transformation.** Before Black, Python's formatting culture was
fragmented. PEP 8 gave guidance but not determinism. Black ended the
arguments. The Python community adopted Black faster than almost anyone
predicted — within 3 years, it was the default formatter for most major Python
projects (Django, pytest, SQLAlchemy, pandas).

**The trailing comma mechanism.** By giving the user one syntactic lever
(the trailing comma), Black avoids the need for a `# fmt: off` comment in
most cases. The user expresses intent through syntax the parser already
understands, not through a formatting-specific annotation.

**CI integration simplicity.** `black --check .` returns a non-zero exit code
if any file would be reformatted. This makes CI enforcement trivial: one
line in the CI config. Compare this to PEP 8 linters that required configuring
dozens of rules.

**Python versions.** Black's `--target-version` flag handles Python's
evolution gracefully. Older Python versions can't use the walrus operator
or f-strings in certain contexts; Black won't produce code that's invalid for
the target version. This is the rare case where formatter configuration is
truly necessary (syntax compatibility, not style preference).

### 3.5 What Created Friction

**88 characters vs 79.** PEP 8 recommends 79 characters. Black uses 88. This
created genuine conflict: some projects had PEP 8 strict linter rules that
flagged Black-formatted code. The resolution was usually to adopt Black and
drop the PEP 8 length rule, but the transition was painful for some teams.

**The string quoting normalization.** Black normalizes most strings to double
quotes. Projects that had consistently used single quotes for years suddenly
had every string change. This created massive initial diffs. Black's response:
run it once, accept the diff, move on.

**The "Black is not a linter" stance.** Black formats but does not lint. It
will leave `x = x + 1` alone even if `x += 1` would be better. This confused
some users who expected Black to be a complete style solution. The Python
ecosystem now standardizes on Black + isort + flake8/ruff as the "style
stack."

**Speed (historical).** Early Black was slow on large codebases. This was
mostly fixed by rewriting the parser and improving the algorithm, but the
initial experience left an impression.

### 3.6 Key Structural Insight for Nomi

**Determinism is the product, not the output.** Black's value is not that
the formatted code looks beautiful — it's that the formatted code is
predictable. Given the same input, you get the same output, every time,
on every machine, in every IDE. This is what eliminates style arguments:
not consensus, but certainty.

The trailing comma mechanism is a design pattern worth stealing: **give the
user one syntactic gesture that controls formatting behaviour, rather than
a configuration knob.** The gesture is visible in the code, version-controlled,
and reviewable — unlike a config file that lives elsewhere.

---

## 4. Rustfmt — The Integrated Formatter

### 4.1 Philosophy

Rustfmt is Rust's official formatter, distributed as part of the Rust
toolchain via `rustup`. It ships as a component (`rustfmt` or `cargo fmt`),
not a separate tool. The philosophy is integration: formatting is part of
the Rust development workflow, not an optional extra.

Rustfmt occupies a middle ground between gofmt's no-configuration absolutism
and clang-format's everything-configurable sprawl. It has configuration
options — about 30 — but they are explicitly marked as "unstable" or
"limited." The Rustfmt team's stated goal is to minimize the config surface
over time, converging toward a single canonical style.

### 4.2 How It Works

Rustfmt parses Rust source into the compiler's own AST (using `rustc`'s
parser, `syn`, or `rustc_parse`). It then walks the AST and produces
formatted output using a chain of "visitors" that handle different syntactic
constructs.

The formatting algorithm is structural, not cost-based. Instead of trying
multiple layouts and picking the lowest-cost one (like Black or Prettier),
Rustfmt uses rules: "match arms are formatted like this," "function parameters
are formatted like this." This makes the output predictable but can produce
suboptimal results for deeply nested or unusual constructs.

### 4.3 Handling Rust's Syntactic Complexity

Rust's syntax is substantially more complex than Go's or Python's. Rustfmt
must handle:

**Pattern matching:**

```rust
match value {
    // Single-arm, simple pattern — stays on one line:
    Some(x) if x > 0 => println!("positive"),

    // Multi-arm — each gets its own format:
    Some(x) => {
        let y = process(x);
        println!("{}", y)
    }
    None => return Err(Error::NotFound),
}
```

**Closures:** Rustfmt formats short closures on one line and long closures
as blocks:

```rust
// Short closure — inline:
let doubled: Vec<_> = nums.iter().map(|x| x * 2).collect();

// Long closure — block format:
let result: Vec<_> = nums
    .iter()
    .map(|x| {
        let y = expensive_computation(x);
        y.process()
    })
    .collect();
```

**Generics and where clauses:**

```rust
// Compact generics fit on one line:
fn foo<T: Display, U: Debug>(t: T, u: U) { ... }

// Complex bounds with where clause:
fn foo<T, U>(t: T, u: U) -> Result<(), Error>
where
    T: Display + Clone + Send + Sync + 'static,
    U: Debug + Default,
{ ... }
```

**Chained method calls:** Rustfmt uses a multi-line "builder" pattern:

```rust
let result = some_iterator
    .filter(|x| x.is_valid())
    .map(|x| x.transform())
    .collect::<Vec<_>>();
```

**Macros:** Rust's macro system is a formatting challenge. `macro_rules!`
definitions use their own mini-syntax. Rustfmt handles them with special
rules that preserve the internal structure:

```rust
macro_rules! my_macro {
    ($x:expr) => {
        println!("got: {}", $x)
    };
    ($x:expr, $y:expr) => {
        println!("got: {} and {}", $x, $y)
    };
}
```

### 4.4 Configuration Model

Rustfmt's configuration lives in `rustfmt.toml`. The most commonly used
options:

| Option | Values | Default |
|--------|--------|---------|
| `max_width` | integer | 100 |
| `tab_spaces` | integer | 4 |
| `hard_tabs` | bool | false |
| `edition` | "2015", "2018", "2021", "2024" | "2015" |
| `fn_single_line` | bool | false |
| `match_block_trailing_comma` | bool | false |
| `use_small_heuristics` | "Default", "Off", "Max" | "Default" |
| `imports_granularity` | "Preserve", "Crate", "Module", "Item", "One" | "Preserve" |
| `reorder_imports` | bool | true |
| `group_imports` | "Preserve", "StdExternalCrate" | "Preserve" |

The Rustfmt team explicitly marks most options as requiring nightly Rustfmt or
as "unstable." This is a deliberate strategy: offer configuration for
transitioning projects, but signal that the long-term destination is a single
style.

### 4.5 The `#[rustfmt::skip]` Escape Hatch

Rustfmt provides two escape hatches:

```rust
// Skip a single item:
#[rustfmt::skip]
fn this_function_has_manual_formatting() {
    // ... carefully formatted code ...
}

// Skip a block:
#[rustfmt::skip]
mod manually_formatted {
    // ... this entire module is skipped ...
}
```

The escape hatch is intentionally verbose. `#[rustfmt::skip]` is not a subtle
annotation — it's visible in code review and stands out in the source. This is
a deliberate design choice: the escape hatch should be uncomfortable enough
that programmers reach for it only when genuinely necessary.

### 4.6 `cargo fmt` Integration

`cargo fmt` formats the entire project. `cargo fmt --check` verifies
formatting in CI. `cargo fmt -- --check` passes flags to rustfmt directly.

The integration with Cargo means Rust developers never install rustfmt
separately. It comes with the toolchain via `rustup component add rustfmt`.
This is an underrated design decision: **the formatter is part of the
language, not part of the user's personal tool preferences.**

### 4.7 What Worked Exceptionally Well

**Integration with the compiler toolchain.** `rustup` installs rustfmt.
`cargo` runs it. New Rust developers format their code correctly from day one
without knowing rustfmt exists.

**Edition-aware formatting.** Rust editions (2015, 2018, 2021, 2024) can
change syntax. Rustfmt respects the edition and formats accordingly. This
handles language evolution gracefully.

**The deliberate push toward no-config.** By making configuration options
"unstable" and signaling that they may go away, Rustfmt creates a migration
path: projects can adopt Rustfmt with their preferred style, then gradually
converge on the default as options stabilize or are removed.

### 4.8 What Created Friction

**The 100-character default.** Rust's community is split between 80, 100, and
120 characters. Rustfmt's default of 100 is a compromise that satisfies no one.
Some projects change it; most don't bother and grumble about it.

**Structural algorithm limitations.** Rustfmt's rule-based approach sometimes
produces awkward formatting for unusual constructs. There's no cost function
to optimize globally — if the rule says "break here," it breaks there, even if
a human would make a different choice.

**Performance on large files.** Rustfmt parses and reformats the entire file.
On files with deeply nested macros or generated code, this can be slow.

**Interaction with `rust-analyzer`.** IDE formatting via `rust-analyzer` uses
Rustfmt under the hood, but the integration is imperfect — sometimes the IDE
shows different formatting than `cargo fmt` produces.

### 4.9 Key Structural Insight for Nomi

**Integrate the formatter into the language toolchain.** `cargo fmt` means
every Rust developer has the formatter. The formatter is not a third-party
tool you discover — it's part of the language experience. Nomi should ship a
formatter as part of `nomi`, not as a separate `nomi-fmt` tool.

The `#[rustfmt::skip]` escape hatch design — intentionally verbose, visible
in code review — is the right model. Escape hatches should exist but should
feel like a concession, not a feature.

---

## 5. Prettier — The Opinionated Web Formatter

### 5.1 Philosophy

Prettier calls itself "an opinionated code formatter." The philosophy is
articulated clearly in its documentation: "By far the biggest reason for
adopting Prettier is to stop all the on-going debates over styles." Prettier
drew explicit inspiration from gofmt and Black.

What makes Prettier distinctive is its **language-agnostic core.** Prettier
supports JavaScript, TypeScript, JSX, CSS, SCSS, Less, HTML, Vue, Angular,
GraphQL, Markdown, YAML, JSON, and more — all through a single tool. Each
language gets a plugin, but the core formatting algorithm is shared.

This multi-language scope means Prettier makes different tradeoffs than
single-language formatters. It must handle wildly different syntaxes with a
unified approach.

### 5.2 The Print Width Concept

Prettier's central formatting parameter is **print width** (default 80). The
algorithm fits as much content as possible on each line without exceeding
print width.

The key algorithmic property: **Prettier does not "reflow" lines that already
fit.** If content fits on one line, Prettier keeps it on one line. Only when
content exceeds print width does Prettier break and indent.

```javascript
// Fits on one line — stays compact:
const result = [1, 2, 3, 4, 5].map(x => x * 2).filter(x => x > 5);

// Exceeds 80 chars — broken at logical points:
const result = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
  .map(x => x * 2)
  .filter(x => x > 5)
  .reduce((acc, x) => acc + x, 0);
```

### 5.3 Handling Web Language Diversity

**JavaScript/TypeScript:**

```javascript
// Object literals — short stays inline:
const config = { host: "localhost", port: 8080 };

// Long — each property on its own line:
const config = {
  host: "localhost",
  port: 8080,
  timeout: 30000,
  retries: 3,
};

// Generics in TypeScript:
function identity<Type>(arg: Type): Type {
  return arg;
}

// Complex generic constraints:
function longest<
  Type extends { length: number; compare: (other: Type) => number },
>(a: Type, b: Type): Type {
  return a.compare(b) > 0 ? a : b;
}
```

**JSX:**

```jsx
// Simple JSX — inline:
<div className="greeting">Hello, {name}!</div>

// Complex JSX — multi-line with logical grouping:
<div className="container">
  <Header title={title} />
  <main>
    <p>Welcome to the application.</p>
    <Button onClick={handleClick} disabled={isLoading}>
      {isLoading ? "Loading..." : "Submit"}
    </Button>
  </main>
</div>
```

**Conditional expressions:** Prettier formats ternary expressions with a
characteristic indentation:

```javascript
// Simple ternary — inline:
const message = isLoggedIn ? "Welcome back!" : "Please sign in.";

// Nested ternary — Prettier's signature formatting:
const message = isLoggedIn
  ? user.hasSubscription
    ? "Welcome back, subscriber!"
    : "Welcome back! Upgrade for more features."
  : "Please sign in.";
```

This nested ternary format is controversial — some developers find it
readable, others find it an invitation to write nested ternaries that should
be `if` blocks.

### 5.4 The Wrapping Algorithm

Prettier's algorithm is a greedy line-breaker similar to Black's but with
some differences:

1. Try to print the entire document on one line.
2. If it exceeds print width, break at the highest-level "break parent."
3. Recurse into the broken parts.
4. The decision is greedy — Prettier does not backtrack.

Prettier uses a "document IR" (intermediate representation) between parsing
and printing. Parsers produce an AST; the printer converts the AST to a
document IR with explicit break opportunities; the layout engine chooses which
breaks to take.

### 5.5 Configuration

Prettier has more configuration than gofmt but far less than clang-format:

| Option | Values | Default |
|--------|--------|---------|
| `printWidth` | integer | 80 |
| `tabWidth` | integer | 2 |
| `useTabs` | bool | false |
| `semi` | bool | true |
| `singleQuote` | bool | false |
| `trailingComma` | "none", "es5", "all" | "all" |
| `bracketSpacing` | bool | true |
| `arrowParens` | "always", "avoid" | "always" |
| `endOfLine` | "lf", "crlf", "cr", "auto" | "lf" |

Prettier's position: these are the options that have genuine semantic or
ecosystem significance. `semi` matters because ASI (automatic semicolon
insertion) is a language feature. `singleQuote` matters because it affects
string escaping. `trailingComma` matters because ES5 compatibility. Every
option has a justification beyond "personal preference."

### 5.6 IDE Integration

Prettier's IDE integration is best-in-class. The VS Code extension formats
on save. The "format on save" experience means developers don't think about
formatting — they save the file and it's correctly formatted.

Prettier also offers a **pre-commit hook** (`lint-staged` + `prettier
--write`) and a **CI check** (`prettier --check`). The full integration
model: save (IDE) → commit (hook) → push (CI) — three layers of enforcement,
zero mental overhead.

### 5.7 What Worked Exceptionally Well

**Multi-language scope.** Web developers deal with JavaScript, CSS, HTML, JSON,
Markdown, and more — all in the same project. One formatter for all of them is
a massive simplification. No need to configure and maintain multiple formatting
tools.

**The "format on save" culture.** Prettier normalized the idea that formatting
happens automatically when you save a file. This is a different mental model
than running a formatter as a separate step.

**The escape hatch comment.** `// prettier-ignore` skips the next node.
`// prettier-ignore-start` / `// prettier-ignore-end` skips a block. The
comment syntax is intentionally different from normal comments to stand out.

### 5.8 What Created Friction

**The 80-character default in a 120-character web world.** Many web developers
found 80 characters too narrow. Prettier allows changing it, but the default
created initial resistance. The team held firm on 80 — changing the default
would have been a breaking change, and 80 was chosen deliberately as a
readability baseline.

**Semicolons.** Prettier adds semicolons by default. The JavaScript community
has a significant "no semicolons" faction. Prettier's `semi: false` option
addresses this, but it created early tension between the "opinionated" promise
and the configuration escape valve.

**The trailing comma configuration.** Prettier's `trailingComma` option has
gone through several iterations ("none" → "es5" → "all"). Each change
required projects to decide whether to adopt the new default. This is a case
where configuration options create ongoing maintenance burden.

**Markdown formatting.** Prettier formats Markdown, but Markdown has many
edge cases (code blocks inside lists, nested blockquotes) that interact badly
with automatic reformatting. Some projects disable Prettier for Markdown.

### 5.9 Key Structural Insight for Nomi

**The document IR is an architectural pattern worth understanding.** Separating
parsing (AST production) from formatting (document IR with break opportunities)
from layout (choosing breaks) creates clean interfaces. Each stage can evolve
independently. Nomi's formatter should consider this three-stage pipeline:
parse → document IR → layout.

The **multi-language architecture** is also instructive. If Nomi ever has
companion languages (build files, config languages, documentation formats),
Prettier's plugin model shows that a shared formatting engine can serve
multiple syntaxes with language-specific plugins.

---

## 6. Elm Format — Formatting as a Language Value

### 6.1 Philosophy

`elm-format` occupies a unique position in the formatter landscape. It is not
"the Elm formatter" — it is **the only way to format Elm code.** The Elm
community's stance is that there is exactly one correct way to format any
Elm program, and `elm-format` produces it.

This goes beyond gofmt's "this is the canonical representation." Elm's
position is "there is no other way." You cannot format Elm without
`elm-format`; you cannot configure `elm-format`; you cannot escape
`elm-format` (there is no `--skip` flag or annotation). Every Elm program
submitted to the package repository (elm-package) must pass `elm-format
--validate`.

This extreme position was possible because Elm is a small, young language with
a centralized package ecosystem. There was no pre-formatting legacy codebase
to accommodate. The community formed around the formatter from the beginning.

### 6.2 How It Works

`elm-format` parses Elm source into the compiler's own AST, then prints it
using a "pretty-printing" algorithm derived from Wadler's "A Prettier Printer"
(1998). The algorithm uses a layout algebra where each syntactic construct has
a preferred layout (horizontal if it fits, vertical if it doesn't) and a
"best" layout is chosen using a cost function.

The key property: `elm-format` is a **pure function** from AST to string.
Two programs with the same AST produce identical output.

### 6.3 Handling Elm's Syntax

**Pipeline formatting:** Elm's pipe operator (`|>`) is central to the
language's expression style. `elm-format` formats pipelines with a
characteristic rhythm:

```elm
-- Short pipeline — inline:
result = List.map (\x -> x * 2) (List.range 1 10)

-- Long pipeline — one operation per line:
result =
    List.range 1 10
        |> List.map (\x -> x * 2)
        |> List.filter (\x -> x > 10)
        |> List.sum
```

**Pattern matching with `case`:**

```elm
-- Simple case:
description result =
    case result of
        Ok value ->
            "Success: " ++ value

        Err error ->
            "Failure: " ++ error

-- Nested patterns:
process value =
    case value of
        Just (Ok x) ->
            x

        Just (Err _) ->
            default

        Nothing ->
            default
```

**Record types:**

```elm
-- Short record — inline:
type alias Point = { x : Float, y : Float }

-- Long record — one field per line:
type alias Config =
    { host : String
    , port : Int
    , timeout : Int
    , retries : Int
    }
```

Note the leading comma style for records. This is not a configuration option
— it is the only valid Elm formatting.

### 6.4 What Happens When a Community Agrees on One Formatter

Elm's formatting monoculture produced several observable effects:

**No style discussions ever.** Elm code review never includes formatting
feedback. Not "rarely" — never. Every Elm developer formats the same way.
The mental bandwidth that other languages spend on formatting is completely
freed for semantic review.

**Universal code appearance.** Every Elm codebase looks like every other
Elm codebase. Reading a new Elm library requires zero adaptation. The visual
grammar is constant across the entire ecosystem.

**Tooling simplicity.** Every Elm tool can assume `elm-format` output. IDE
plugins, documentation generators, and linters all consume `elm-format` output.

**The cost: lack of experimentation.** The Elm community cannot experiment
with alternative formatting styles. If `elm-format` makes a suboptimal choice
for a particular construct, there is no way for the community to demonstrate
a better approach. The formatter maintainers hold unilateral authority over
the visual appearance of all Elm code.

### 6.5 What Created Friction

**No escape hatch.** For generated code, DSLs embedded in Elm, or
pedagogical examples where formatting would obscure the teaching point,
`elm-format` cannot be disabled. This makes certain use cases genuinely
harder.

**Ecosystem lock-in.** Because `elm-format` is the only formatter, and the
package repository requires it, alternative formatting approaches cannot
gain traction. If `elm-format` makes a mistake, the ecosystem lives with it.

**Slow iteration.** `elm-format` development pace is tied to the Elm compiler
development pace, which is slow. Bugs in formatting persist for years.

### 6.6 Key Structural Insight for Nomi

Elm demonstrates the **end state** of the "no configuration" philosophy:
total uniformity. The benefits are real — zero formatting overhead, universal
code appearance, simplified tooling. The costs are also real — no escape
hatches, slow iteration, inability to experiment.

Nomi should aim for gofmt's position (canonical, not monopolistic) rather than
Elm's (monopolistic, enforced by the package registry). The formatter should be
the standard, but there should be an escape hatch, and the ecosystem should
not reject code that was formatted differently.

The **pipeline formatting** in Elm is particularly relevant for Nomi. Nomi's
`|>` operator needs clear, consistent formatting rules. Elm's approach — one
operation per line, indented by one level — is a strong candidate.

---

## 7. clang-format — The Configurable Formatter

### 7.1 Philosophy

clang-format is the anti-gofmt. Where gofmt says "no configuration,"
clang-format says "configure everything." A `.clang-format` file can have over
100 options controlling every aspect of C++ formatting.

This is not a design failure — it is a necessity. C++ codebases span 40 years
of formatting conventions. Google's C++ style, LLVM style, Chromium style,
WebKit style, Mozilla style, GNU style — all are different. clang-format
cannot enforce one style because the C++ ecosystem never agreed on one style.
The tool's job is to faithfully reproduce an existing style, not to impose a
new one.

### 7.2 Configuration Space

clang-format's configuration options cover:

**Indentation style:** `AccessModifierOffset`, `IndentCaseLabels`,
`IndentExternBlock`, `IndentGotoLabels`, `IndentPPDirectives`,
`IndentWidth`, `NamespaceIndentation`, `UseTab`

**Brace placement:** `BreakBeforeBraces` with values `Attach`, `Linux`,
`Mozilla`, `Stroustrup`, `Allman`, `Whitesmiths`, `GNU`, `WebKit`,
`Custom`

**Line breaking:** `AllowShortFunctionsOnASingleLine`,
`AllowShortIfStatementsOnASingleLine`, `AlwaysBreakAfterReturnType`,
`BreakBeforeBinaryOperators`, `BreakBeforeTernaryOperators`,
`ColumnLimit`

**Whitespace:** `SpaceAfterCStyleCast`, `SpaceBeforeAssignmentOperators`,
`SpaceBeforeParens`, `SpacesInAngles`, `SpacesInCStyleCastParentheses`

**Include ordering:** `IncludeBlocks`, `IncludeCategories`,
`SortIncludes`, `IncludeIsMainRegex`

**Alignment:** `AlignAfterOpenBracket`, `AlignConsecutiveAssignments`,
`AlignConsecutiveDeclarations`, `AlignOperands`

The full configuration file for a "generic" C++ project is typically 30-50
lines. Teams spend real time debating these values.

### 7.3 How It Works

clang-format uses a **penalty-based algorithm.** Each formatting decision
(where to break a line, how much to indent, etc.) is assigned a penalty.
The formatter searches for the layout that minimizes total penalty.

The penalty model creates flexibility at a cost. Adding a new rule means
defining its penalty and ensuring it doesn't interact badly with existing
penalties. The search space for optimal layout is large, so clang-format uses
heuristics and early termination rather than a true global optimization.

### 7.4 Predefined Styles

clang-format ships with predefined style bases: `LLVM`, `Google`,
`Chromium`, `Mozilla`, `WebKit`, `Microsoft`, `GNU`. A project can start
from one of these and override specific options:

```yaml
BasedOnStyle: Google
ColumnLimit: 100
IndentWidth: 4
AllowShortFunctionsOnASingleLine: None
```

This is a pragmatic compromise: most teams don't define every option from
scratch — they inherit a base style and tweak a few preferences.

### 7.5 What Worked Well

**Backward compatibility with existing codebases.** clang-format can be
configured to match an existing codebase's style, enabling gradual adoption
without a flag-day reformat. This is the killer feature for large, old
codebases.

**IDE integration.** clang-format is integrated into CLion, Visual Studio,
VS Code, Vim, and Emacs. The "format on save" experience works regardless
of the project's style configuration.

**The `// clang-format off` escape hatch.** A simple comment pair disables
formatting for a region. This is essential for C++ codebases that contain
macros, generated code, or formatting-sensitive constructs.

**Incremental adoption.** A project can add a `.clang-format` file without
reformatting the entire codebase. Individual files or directories can be
formatted gradually.

### 7.6 What Created Friction

**Configuration overhead.** Teams spend hours debating `.clang-format`
settings. This is the problem gofmt was designed to eliminate, and
clang-format recreates it for every team.

**Inconsistent formatting across the ecosystem.** Two C++ projects with
different `.clang-format` files look different. The cognitive cost of
switching between projects is real.

**The penalty-based algorithm can produce surprising results.** Because the
penalty model is complex and the search space is large, clang-format
occasionally produces formatting that no human would choose. When this
happens, the developer's options are: add `// clang-format off`, tweak the
config file, or accept the weird output.

**Poor handling of macros and templates.** C++ macros and deeply nested
templates are inherently hard to format. clang-format's structural approach
breaks down on macros (which are text-level, not AST-level) and produces
awkward formatting for complex templates.

**Version incompatibility.** clang-format versions can produce different
output for the same configuration. Teams must pin a clang-format version
or accept occasional formatting changes when upgrading.

### 7.7 When Is Configurability Worth It?

clang-format demonstrates that configurability is necessary when:

1. **The ecosystem has multiple entrenched styles.** You cannot impose one
   style on a 40-year-old ecosystem.
2. **The language has genuine dialect variation.** C++03 vs C++11 vs C++17 vs
   C++20 have different syntactic features that need different rules.
3. **The formatter is being adopted incrementally.** A flag-day reformat of a
   million-line codebase is not feasible.
4. **The language has constructs that resist algorithmic formatting.**
   Macros are the poster child — text-level constructs that don't parse as
   AST nodes.

Configurability is not worth it when:

1. **The language is new enough to establish a single convention.**
2. **The community is willing to accept a canonical style.**
3. **The formatter ships with the language from day one.**
4. **The language has no macro/preprocessor system.**

### 7.8 Key Structural Insight for Nomi

clang-format teaches us what happens when a formatter must serve an
ecosystem that never converged on a single style. The result is functional
but fragmented. Every team configures clang-format differently, so the
promise of "universal code appearance" is never realized.

For Nomi, the lesson is: **ship the formatter early.** Once the ecosystem
develops multiple formatting styles, imposing one is politically impossible.
The window for establishing a canonical style is open at language launch and
closes rapidly thereafter.

That said, clang-format's base style approach (inherit from a predefined style,
override a few options) is worth borrowing. Nomi could ship with a single
canonical style but offer a small number of "profile" options for teams with
strong specific preferences (e.g., tab width).

---

## 8. Ormolu / Fourmolu (Haskell) — Formatting Layout-Sensitive Languages

### 8.1 Philosophy

Ormolu is "a formatter for Haskell source code." Its philosophy is stated in
four principles:

1. **Idempotence.** Formatting already-formatted code doesn't change it.
2. **Syntax awareness.** Ormolu parses Haskell with GHC's own parser, not a
   regex or a separate grammar.
3. **No configuration.** Like gofmt, Ormolu takes no configuration.
4. **No escape hatches.** Ormolu does not respect `-- ORMOLU_DISABLE` by
   default (though a flag can be enabled).

Fourmolu is a fork of Ormolu that adds configuration options: indentation
width, comma style, import handling, record field alignment, and more. It was
created because some Haskell projects found Ormolu's no-configuration stance
too rigid.

### 8.2 The Layout Challenge

Haskell's layout rule is a significant challenge for formatters. In Haskell,
indentation determines block structure:

```haskell
-- The 'where' clause is part of the function because it's indented:
factorial n = go n 1
  where
    go 0 acc = acc
    go n acc = go (n - 1) (n * acc)

-- If 'where' were not indented, it would be a separate declaration:
factorial n = go n 1
where
    go 0 acc = acc
```

The formatter must understand layout semantics, not just emit aesthetically
pleasing output. Changing indentation can change program meaning.

Ormolu's approach: **parse with GHC, which resolves layout into explicit
block structure in the AST.** Then format from the AST, where indentation
is semantic, not syntactic. This means Ormolu can freely adjust indentation
without breaking program meaning because the meaning is already encoded in
the AST structure.

### 8.3 Formatting Rules

**Imports:**

```haskell
import Data.List (sort, group)
import qualified Data.Map as Map
import Data.Text (Text)
import Control.Monad (when, unless, forM_)
```

Ormolu sorts imports alphabetically by module name, but does not group them
(standard library vs third-party). Fourmolu adds import grouping.

**Data declarations:**

```haskell
-- Short — inline:
data Color = Red | Green | Blue

-- Long — one constructor per line:
data Expr
  = Lit Int
  | Add Expr Expr
  | Mul Expr Expr
  | IfThenElse Expr Expr Expr
```

**Function definitions:**

```haskell
-- Short function — one line:
add x y = x + y

-- Long function — signature on own line, body indented:
factorial :: Integer -> Integer
factorial n = go n 1
  where
    go 0 acc = acc
    go n acc = go (n - 1) (n * acc)
```

**Pattern matching:**

```haskell
-- Case expression:
describe result = case result of
  Just x -> "Got: " ++ show x
  Nothing -> "Nothing"
```

### 8.4 Ormolu vs Fourmolu: The Fork That Answers "How Much Config?"

Fourmolu exists because Ormolu's no-configuration stance was too rigid for
some Haskell projects. The fork adds:

- Indentation width (2, 4, etc.)
- Comma style (leading vs trailing)
- Import grouping (by package, by module)
- Record field alignment
- Single-constraint-pragma handling
- Various whitespace options

This fork illustrates a recurring pattern: **for every "no configuration"
formatter, there exists a project that genuinely needs one more option.**
The question is where to draw the line.

Ormolu's position: no configuration. The line is absolute. Fourmolu's
position: some configuration. The line is blurred. Neither is "wrong" —
they serve different segments of the Haskell ecosystem.

### 8.5 What Worked Well

**GHC parser integration.** Using the real Haskell parser means Ormolu never
misunderstands Haskell syntax. There are no edge cases where the formatter
thinks something is one construct but it's actually another.

**Handling of layout.** By resolving layout in the AST, Ormolu avoids the
fundamental tension other Haskell formatters face: "if I change the
indentation, does the meaning change?" The answer is always no because the
AST has explicit structure.

**Idempotence.** Ormolu was designed for idempotence from the start. The
GHC AST-to-AST roundtrip is carefully constructed so `ormolu (ormolu x)`
always equals `ormolu x`.

### 8.6 What Created Friction

**No configuration, again.** The same gofmt tension plays out in Haskell.
Some developers want different indentation widths or comma styles. Ormolu
says no. Fourmolu says yes. The ecosystem is split.

**GHC version coupling.** Ormolu is tightly coupled to a specific GHC version.
Upgrading GHC requires upgrading Ormolu, and Ormolu releases lag behind GHC
releases. This creates adoption friction.

**Performance.** Parsing with GHC is expensive. Ormolu is slower than
formatters that use their own parsers. On large Haskell codebases, this is
noticeable.

**No escape hatch.** Some Haskell codebases contain manually formatted
expressions that don't survive algorithmic formatting. Ormolu's response:
fix the code to be formattable. The community's response: use Fourmolu or
don't use a formatter.

### 8.7 Key Structural Insight for Nomi

Nomi is indentation-sensitive like Haskell. The Haskell formatter experience
offers a critical lesson: **parse with the real parser, resolve layout into
the AST, then format from the AST.** This is the only safe way to format an
indentation-sensitive language — the formatter must understand that changing
indentation could change meaning.

Ormolu/Fourmolu also demonstrates that **the "no configuration" line will
be challenged, and a fork may emerge.** The question is not whether to
offer configuration — it is whether the fork (with configuration) gains
more adoption than the original (without). If Nomi ships a no-configuration
formatter, some fraction of the community will want configuration. A
small, stable set of configuration options (like Rustfmt's) may be the
pragmatic middle ground.

---

## 9. dart format — The SDK-Integrated Formatter

### 9.1 Philosophy

`dart format` is the official Dart formatter, distributed as part of the
Dart SDK. Like `gofmt`, it is opinionated and has no configuration options.
Unlike gofmt, it was designed from the start to handle modern language
features and IDE integration.

Dart's philosophy is pragmatic: the formatter should produce "the
formatting that an experienced Dart developer would write by hand." It aims
for human-like output rather than mechanical consistency. This is a subtle
but important distinction from gofmt, which optimized for mechanical
consistency regardless of human aesthetics.

### 9.2 How It Works

`dart format` uses a sophisticated line-breaking algorithm based on the
"pretty-printing" literature. Key features:

**Indentation-based formatting.** Dart uses indentation for readability but
not for semantics (unlike Haskell). The formatter can freely adjust
indentation without changing program meaning.

**Multisplit solver.** The formatter finds optimal break points using a
**multisplit algorithm** that considers all possible combinations of break
points and chooses the one that minimizes a cost function. This is more
sophisticated than the greedy algorithms used by Black or Prettier — it
can find globally optimal layouts for complex expressions.

**Whitespace handling.** The formatter normalizes all whitespace: spaces,
blank lines, trailing whitespace. Two blank lines are replaced by one.
Blank lines before comments are preserved.

### 9.3 Handling Modern Dart Syntax

**Named parameters:**

```dart
// Short — inline:
void configure({String? host, int port = 8080}) { ... }

// Long — one per line:
void configure({
  String? host,
  int port = 8080,
  Duration timeout = const Duration(seconds: 30),
  bool enableLogging = false,
}) { ... }
```

**Cascade notation (a Dart distinctive):**

```dart
// Short cascade — inline:
querySelector('#button')..text = 'Click me'..onClick.listen(handleClick);

// Long cascade — one operation per line:
querySelector('#container')
  ..style.width = '100%'
  ..style.height = '200px'
  ..children.addAll([
    Header('Title'),
    Body(content),
    Footer(copyright),
  ]);
```

**Collection literals:**

```dart
// Short collection — inline:
final list = [1, 2, 3, 4, 5];
final map = {'a': 1, 'b': 2};

// Long collection — one element per line:
final list = [
  1,
  2,
  3,
  if (includeFour) 4,
  for (var i = 5; i < 10; i++) i,
];
```

**Patterns and records (Dart 3.0):**

```dart
// Pattern matching:
final result = switch (value) {
  0 => 'zero',
  1 => 'one',
  _ when value > 0 => 'positive',
  _ => 'negative',
};

// Record destructuring:
final (name, age, city) = ('Alice', 30, 'New York');

// Algebraic data types via sealed classes:
sealed class Result<T> {
  const factory Result.ok(T value) = Ok<T>;
  const factory Result.error(String message) = Error<T>;
}
```

### 9.4 IDE Integration

Dart's IDE story is distinct from other languages because the Dart SDK ships
the Dart Analysis Server, which provides formatting alongside diagnostics,
completions, and refactoring. The formatter is not a separate tool — it is
a service provided by the analysis server.

This means:
- Format-on-save in VS Code and IntelliJ uses the same formatter.
- The formatter is always version-locked to the SDK.
- No separate installation step.

### 9.5 What Worked Well

**Multisplit solver quality.** Dart's formatter produces higher-quality
output than most greedy formatters, especially for complex nested
expressions. The global optimization finds layouts that greedy algorithms
miss.

**Cascade formatting.** The cascade notation (`..`) is formatting-sensitive
— poorly formatted cascades are hard to read. Dart's formatter handles them
well, recognizing that cascades are a visual hierarchy.

**Collection-if and collection-for.** Dart's collection comprehension-like
syntax needs careful formatting. The formatter handles inline `if` and
`for` in collections gracefully.

**Version locking.** The formatter is versioned with the SDK, so there is
never a version mismatch. When you upgrade Dart, you get the formatter that
understands new syntax.

### 9.6 What Created Friction

**Blank line handling.** Dart's formatter aggressively removes blank lines.
Code that uses blank lines for logical grouping gets collapsed. Some
developers find this over-aggressive.

**The multisplit solver can be slow.** Finding globally optimal line breaks
is NP-hard in the worst case. The solver has heuristics for performance,
but on deeply nested expressions it can take noticeable time.

**No configuration means no escape from unpopular choices.** Some Dart
developers dislike the cascade indentation or the trailing comma behavior.
There is no recourse.

### 9.7 Key Structural Insight for Nomi

The multisplit solver is aspirational. A globally optimal line-breaking
algorithm produces better results than a greedy one, especially for
expressions where break choices interact (nested function calls, pipelines,
pattern matches). Nomi should aim for a cost-function-based approach that
considers break interactions, even if the search is not fully global.

Dart's cascades are analogous to Nomi's pipe operator and block calls.
The formatting challenge is the same: sequential operations that form a
visual hierarchy. Dart's solution — one operation per line, indented —
matches Elm's pipeline formatting and is likely right for Nomi.

---

## 10. zig fmt — Formatting in the Compiler

### 10.1 Philosophy

`zig fmt` is the Zig language formatter, built into the Zig compiler. It
follows the gofmt philosophy: no configuration, canonical output. `zig fmt
--check` exits with zero if the file is already formatted, non-zero if
changes are needed.

Zig's formatter philosophy is stated in three words: **"There is one way."**
There are no style guides for Zig. There is no discussion of formatting
conventions. There is `zig fmt` and that's it.

The formatter is implemented inside the Zig self-hosted compiler. This means
the compiler's parser, AST, and tokenizer are available to the formatter
without any duplication or compatibility issues.

### 10.2 Handling Zig's Unique Features

**Comptime:**

```zig
// Comptime expressions — formatted like normal expressions:
const value = comptime blk: {
    var x: i32 = 0;
    for (0..10) |i| {
        x += i * i;
    }
    break :blk x;
};
```

**Defer and errdefer:**

```zig
fn processFile(path: []const u8) !void {
    const file = try std.fs.cwd().openFile(path, .{});
    defer file.close();
    // ... read and process ...
}

fn processWithCleanup(path: []const u8) !void {
    const allocator = std.heap.page_allocator;
    const buffer = try allocator.alloc(u8, 1024);
    defer allocator.free(buffer);
    errdefer std.log.err("Processing failed, but buffer was freed", .{});
    // ... use buffer ...
}
```

Zig's formatter places `defer` and `errdefer` statements at the same
indentation level as surrounding code, immediately after the resource
acquisition they're paired with.

**Payload captures:**

```zig
// If with payload:
if (optional_value) |val| {
    std.debug.print("got: {}\n", .{val});
}

// For with index:
for (items, 0..) |item, index| {
    std.debug.print("{}: {}\n", .{index, item});
}
```

### 10.3 What Worked Well

**Compiler-integrated formatting.** The formatter is guaranteed to understand
the language exactly as the compiler does. There is no parser mismatch, no
version skew, no edge cases where the formatter misparses valid Zig.

**No separate tooling step.** Zig developers don't install a formatter.
They don't configure a formatter. They run `zig fmt` the same way they run
`zig build` — it's just part of the compiler.

**The "check" mode for CI.** `zig fmt --check` is a zero-configuration CI
step. Add one line to your CI config and formatting is enforced.

### 10.4 What Created Friction

**No formatting for comments or doc comments.** `zig fmt` formats code but
not comments. Doc comment formatting is left to the author.

**Evolving formatting rules.** As Zig's syntax evolves (async/await removal,
new `try` syntax, etc.), the formatter rules evolve too. Upgrading the
compiler can change the formatting of existing code. This is managed by
running `zig fmt` on the codebase after an upgrade.

**Limited IDE integration.** Zig's LSP integration is newer than the
language. `zig fmt` integration in editors is available but less mature than
Prettier's or Rustfmt's.

### 10.5 Key Structural Insight for Nomi

**Building the formatter into the compiler** eliminates the parser mismatch
problem entirely. The formatter and the compiler share the same parser, AST,
and token representation. This is only possible if the formatter is built
from day one alongside the compiler.

For Nomi, the current prototype uses a Python-based Lark parser. A production
formatter would share the production parser. In the prototype phase, the
formatter should at minimum use the same Lark grammar as the parser to
avoid divergence.

---

## 11. OCaml ocamlformat — Formatting a Language with History

### 11.1 Philosophy

ocamlformat is the official OCaml formatter, but it operates in a very
different context than most other formatters. OCaml is an ML-family language
with 30+ years of history. It has multiple entrenched formatting traditions:
Jane Street style, INRIA/camlp4 style, community convention style.
ocamlformat cannot impose one style — it must accommodate all of them.

ocamlformat's solution: **configuration profiles.** Instead of infinite
knobs, ocamlformat ships with named profiles that encode entire formatting
styles:

- `conventional`: modern community convention, readable and compact
- `janestreet`: Jane Street's house style (used in their massive OCaml
  codebase)
- `ocamlformat`: the tool's own preferred style
- `sparse`: more vertical whitespace for readability

A project picks a profile:

```
profile = janestreet
```

And optionally overrides specific options:

```
profile = janestreet
exp-grouping = parens
if-then-else = keyword-first
```

### 11.2 Handling OCaml's Syntax

**Type declarations:**

```ocaml
(* Short — inline *)
type color = Red | Green | Blue

(* Long variants — one per line *)
type expr =
  | Lit of int
  | Add of expr * expr
  | Mul of expr * expr
  | If of expr * expr * expr
```

**Function definitions:**

```ocaml
(* Short function — one line *)
let add x y = x + y

(* Long function — let-binding with type annotation *)
let factorial (n : int) : int =
  let rec go n acc =
    if n <= 1 then acc else go (n - 1) (n * acc)
  in
  go n 1
;;
```

**Module signatures:**

```ocaml
module type S = sig
  type t
  val empty : t
  val add : t -> int -> t
  val mem : t -> int -> bool
end
```

### 11.3 Configurable but Structured

ocamlformat's approach to configuration is more structured than
clang-format's. The profile system means most projects pick a profile and
never touch individual options. The options that can be overridden are
limited to genuinely meaningful formatting decisions (grouping style,
indentation width, comment placement), not micro-preferences.

This is a middle path: **offer meaningful choices through profiles, not
infinite micro-configuration.** The profile encodes a coherent style where
all options work together. Individual overrides are possible but
discouraged.

### 11.4 What Worked Well

**Profiles reduce configuration burden.** Instead of setting 20 options
individually, a project sets one profile. The profile author ensures
internal consistency.

**Jane Street adoption.** Jane Street, the largest OCaml user, adopted
ocamlformat and contributed the `janestreet` profile. This gave the
formatter credibility and a large real-world testbed.

**Incremental adoption in an old ecosystem.** OCaml codebases from 1998
can adopt ocamlformat without a flag-day reformat. The formatter can be
configured to match the existing style, then the project can migrate
gradually.

### 11.5 What Created Friction

**Profile complexity.** Each profile encodes 30-50 formatting decisions.
Understanding what a profile does requires reading documentation or
experimenting. The profile name is a black box.

**Legacy syntax compatibility.** OCaml has evolved syntax over 30 years.
Some codebases use syntax that ocamlformat handles poorly. The formatter
is limited by the parser — it cannot format code that doesn't parse as
valid OCaml.

**The `ocamlformat` profile changes over time.** The tool's own preferred
style evolves with releases. Projects using the `ocamlformat` profile get
formatting changes when they upgrade. This is the same version-skew problem
as clang-format.

### 11.6 Key Structural Insight for Nomi

The **profile concept** is the most interesting contribution. Profiles
encode coherent, named styles as a unit rather than as a collection of
independent knobs. A profile is a design decision — it says "this is how
the language looks" — rather than a configuration file that says "here are
my personal preferences."

For Nomi, profiles could be a future extension mechanism. Ship with one
canonical style (no configuration). If the community demands alternatives,
add named profiles that encode entire styles rather than individual options.
This keeps the configuration surface small and meaningful.

---

## 12. Cross-Language Synthesis

### 12.1 Structural Invariants

Across all ten systems, seven patterns appear consistently. These are not
taste — they are engineering invariants that any successful formatter must
satisfy.

**1. Idempotence.** `format(format(x)) == format(x)`. Every formatter that
succeeded made idempotence a first-class property. Formatters that didn't
(eventually) guarantee idempotence were abandoned or replaced. This is the
most fundamental invariant: formatting must be a stable fixed point.

**2. Syntax awareness.** The formatter must parse the language with a real
parser. Regex-based formatters (early JavaScript formatters, early Python
formatters) always fail on edge cases. Every successful modern formatter
uses the language's own parser or an equivalent.

**3. Determinism.** Given the same input, the formatter must produce the same
output. Every time. On every machine. This is what eliminates style
arguments — not that the formatting is beautiful, but that it is certain.

**4. Comment preservation.** Comments are not part of the AST in most
languages, but formatters must preserve them. Every successful formatter
invests significant effort in attaching comments to the correct AST nodes
and formatting them sensibly. Comment handling is the hardest part of
building a formatter.

**5. Toolchain integration.** The formatter must be one command away.
`gofmt`, `cargo fmt`, `zig fmt`, `dart format`, `black`, `prettier
--write` — all are a single command. If formatting requires configuration,
installation, or a complex invocation, adoption drops.

**6. CI enforcement.** The formatter must have a check-only mode that exits
non-zero when formatting is needed. `--check` is universal. Without it,
formatting is aspirational; with it, formatting is enforced.

**7. Version-stable output.** Formatting output should not change in
patch releases. This is harder than it sounds — the formatter's output
depends on the parser, and parser upgrades can change formatting. The
formatter and the compiler/parser must be version-locked or the formatter
must preserve backward compatibility.

### 12.2 Genuine Design Forks

These are the places where formatters made genuinely different tradeoffs, not
just different syntax-specific rules.

**1. Greedy vs global line-breaking.** Black and Prettier use greedy
algorithms (try to fit, break at first overflow, recurse). Dart uses a
multisplit solver (search for globally optimal breaks). Greedy is faster
and simpler; global produces better output. The difference matters for
deeply nested expressions.

**2. No config (gofmt) vs profiles (ocamlformat) vs full config
(clang-format).** This is the central tradeoff. No-config maximizes
ecosystem uniformity. Profiles offer meaningful choices without infinite
knobs. Full config is necessary for languages with entrenched style
diversity.

**3. Tabs (Go) vs spaces (Rust, Python, JS).** Go's tabs-for-indentation
is a principled choice: let each viewer set display width. Most other
languages use spaces. The tradeoff is viewer flexibility (tabs) vs visual
consistency (spaces). Note: no successful formatter uses tabs for alignment
— only for indentation.

**4. Structural rules (Rustfmt) vs cost functions (clang-format, Prettier).**
Rustfmt's rule-based approach ("match arms are formatted like this") is
predictable and fast but handles edge cases poorly. Cost-function approaches
("choose the layout with the lowest penalty") handle edge cases better but
can surprise users.

**5. Formatter as separate tool (Black, Prettier) vs compiler-integrated
(gofmt, zig fmt, dart format).** Shipping the formatter with the compiler
guarantees parser compatibility and zero installation friction. Shipping
as a separate tool allows independent evolution and multi-language support.

**6. Escape hatch design.** `# fmt: off/on` (Black), `// prettier-ignore`,
`#[rustfmt::skip]`, `// clang-format off/on`, or nothing at all (Elm,
Ormolu). The spectrum: no escape (max uniformity) → comment escape (common)
→ attribute escape (visible, intentional) → block escape (most permissive).

**7. Import ordering as formatting vs import management as a separate tool.**
gofmt orders imports; goimports adds/removes them. isort (Python) is
separate from Black. Rustfmt's `reorder_imports` is built in. The question:
is import management formatting (same tool) or a distinct concern (separate
tool)?

### 12.3 The Configuration Question

The configuration spectrum, from least to most:

```
No config   →  Minimal    →  Profiles    →  Full config
(gofmt)        (Prettier)    (ocamlformat)   (clang-format)
(Elm)          (Black)       (Rustfmt-ish)
(Zig)          (dart format)
(Ormolu)
```

**When is "no config" right?** When the language is young enough to establish
a single style, the community is willing to accept it, and the formatter
ships with the language from day one. This is Nomi's position.

**When is "profiles" right?** When the language has multiple legitimate
formatting traditions that cannot be reconciled. OCaml has Jane Street
style and community style; both are legitimate, and imposing one would
alienate half the ecosystem.

**When is "full config" right?** Almost never, but the exception is
ecosystems that predate formatters by decades. C++ had 30+ years of
formatting convention before clang-format. Imposing one style was not
politically possible.

**The anti-pattern: default-off configuration.** Some tools (early ESLint)
ship with all rules off and expect the user to configure everything. This
maximizes cognitive load and guarantees inconsistent styles across projects.
Every successful formatter ships with sensible defaults and minimizes what
can be changed.

### 12.4 Line Length and Wrapping

Line length is the most visible and most debated formatting parameter. The
survey reveals three approaches:

**Hard limit with soft enforcement (Black, Prettier).** The formatter aims
for a target line length but will exceed it when a construct genuinely
doesn't fit. String literals, long URLs, and deeply nested expressions can
exceed the limit. The formatter never breaks a line that fits within the
limit.

**Soft limit with best-effort (gofmt, Rustfmt).** The formatter tries to
keep lines short but does not guarantee it. Rustfmt's `max_width` and
gofmt's implicit limit are targets, not hard constraints.

**No limit (Elm, Zig).** The formatter optimizes for readability and lets
lines be as long as they need to be. Zig explicitly rejects line length
limits as a formatting concern.

**The practical truth:** the specific number (80, 88, 100, 120) matters far
less than having a number. Teams that agree on "88" spend zero time debating
line length. Teams that have no limit spend time debating whether specific
long lines are "too long."

**Wrapping strategy:** All successful formatters wrap at the highest possible
syntactic level, not at the word level. A function call with 10 arguments
wraps the entire argument list, not individual arguments:

```python
# Good — wraps at argument list level:
result = some_function(
    arg1, arg2, arg3, arg4, arg5, arg6, arg7, arg8, arg9, arg10
)

# Bad — wraps individual arguments (no formatter does this):
result = some_function(arg1, arg2, arg3, arg4, arg5, arg6,
    arg7, arg8, arg9, arg10)
```

### 12.5 Import/Use Ordering

Every formatter deals with imports. The conventions converge on:

1. **Group by source** (standard library, third-party, local).
2. **Sort alphabetically within each group.**
3. **Separate groups with blank lines.**
4. **Merge duplicate imports from the same module.**

```python
# Universal convention, with language-specific syntax:
# Group 1: standard library
import os
import sys

# Group 2: third-party
import numpy as np
import pandas as pd

# Group 3: local
from .utils import helper
```

gofmt, isort (Python), Rustfmt, and Prettier all converge on this pattern.
The variations are in specific syntax (Python's `from ... import`, Rust's
`use`, JavaScript's `import`) and in whether grouped imports are merged.

**Should the formatter also add/remove imports?** goimports (Go) does.
isort (Python) does, but is a separate tool from Black. Rustfmt reorders
but does not add/remove. The consensus is that import management (adding
unused imports, removing unused ones) is a separate concern from
formatting, but import ordering belongs in the formatter.

### 12.6 Diff Minimization

A formatter changes diffs. The effects:

**Positive: semantic diffs.** When formatting is canonical, a diff that
changes one semantic thing changes one line. Without canonical formatting,
the same semantic change might trigger reflow that touches many lines.

**Negative: formatting-only diffs.** When a formatter is first adopted or
upgraded, the initial diff is massive — every line changes. This breaks
`git blame` and makes code archaeology harder.

**Mitigation strategies:**

- **Flag-day reformat + `--ignore-rev`.** Format the entire codebase in one
  commit. Add the commit hash to `.git-blame-ignore-revs` so `git blame`
  skips it.
- **Gradual adoption.** Format only changed files (difficult to enforce).
- **Per-directory adoption.** Add `.formatter` files directory by directory.
- **Pre-commit hook.** Format only staged files, so the massive reformat
  happens incrementally as files are touched.

The flag-day + `--ignore-rev` approach is the most common successful
strategy. The initial diff is large, but it's a one-time cost and `git
blame` can see through it.

### 12.7 Integration Models

The formatter integration spectrum, from least to most integrated:

```
Manual CLI  →  Pre-commit hook  →  Format-on-save  →  CI check  →  Compiler-integrated
```

**Manual CLI:** Developer runs the formatter when they remember. Low
adherence.

**Pre-commit hook:** Formatting enforced at commit time. Better adherence,
but can be bypassed with `--no-verify`.

**Format-on-save:** IDE formats on every save. The gold standard for
developer experience — formatting happens without thinking.

**CI check:** Formatting enforced at push/PR time. Catches anything that
slipped past the pre-commit hook. High adherence.

**Compiler-integrated:** The formatter is part of the compiler chain.
`cargo fmt`, `zig fmt`, `dart format` — no separate tool.

The winning combination across the industry: **format-on-save in the IDE +
pre-commit hook + CI check.** Three layers of enforcement, zero layers of
cognitive overhead.

### 12.8 The "Escape Hatch" Problem

Every formatter needs an escape hatch. No formatter produces ideal output
for every construct. The question is how to design the escape hatch.

**The spectrum:**

1. **No escape hatch** (Elm, Ormolu by default). Maximum uniformity, but
   some code cannot be formatted.
2. **Comment-based escape** (Black: `# fmt: off/on`, Prettier:
   `// prettier-ignore`). Simple, visible, but easy to overuse.
3. **Attribute-based escape** (Rust: `#[rustfmt::skip]`). Verbose and
   intentional — harder to overuse accidentally.
4. **Per-file escape** (`.prettierignore`, `.fmtignore`). Exclude entire
   files from formatting.
5. **Configuration-based escape** (clang-format). Change the config to
   achieve the desired formatting.

**Design principles for escape hatches:**

- Make them visible in code review. `#[rustfmt::skip]` stands out.
- Make them intentional, not habitual. Long-form (multi-word) annotations
  are better than short ones.
- Make them local, not global. Skipping one statement is better than
  skipping the whole file.
- Ask: is this genuinely unformattable, or is the formatter's output
  acceptable even if not ideal?

### 12.9 Anti-Patterns

**1. Formatter as linter.** A formatter that also enforces semantic rules
creates confusion. Is it formatting or is it a style violation? Black
explicitly separates formatting from linting. The formatter changes
whitespace and trivial syntax; the linter catches semantic issues.

**2. Default-off configuration.** Requiring users to configure the
formatter before it produces useful output guarantees inconsistent
formatting and low adoption.

**3. Formatter that changes program semantics.** A formatter that
accidentally changes program meaning is worse than no formatter. Early
JavaScript formatters that broke ASI-dependent code are the canonical
example. The formatter must guarantee semantic preservation.

**4. Inconsistent versions across team members.** When different developers
have different formatter versions, formatting becomes non-deterministic at
the team level. The fix: version-lock the formatter (via the compiler
SDK or a lockfile).

**5. Formatting generated code.** Formatting auto-generated code
creates friction: the generator and the formatter fight. The convention
is to either: (a) generate pre-formatted code, (b) format generated code
after generation, or (c) exclude generated code from formatting.

**6. Changing formatting rules without a migration path.** When the
formatter changes its rules, every file in the codebase changes. Without
a flag-day reformat strategy, this creates an endless stream of
formatting-only diffs.

---

## 13. Nomi Adopt / Refuse / Adapt Table

Nomi's formatter doctrine, grounded in the survey above. Nomi aims for
readable syntax with Python-like indentation, pipe operators (`|>`),
pattern matching, block calls, and data declarations. The formatter
should be canonical (gofmt model), not configurable (clang-format model).

| # | Decision | Adopt / Refuse / Adapt | Rationale |
|---|----------|----------------------|-----------|
| 1 | **Tabs for indentation** | Adopt (gofmt) | Tabs mean "one indent level." Each viewer sets display width. Python-like indentation makes this especially important — tab width is a viewer preference that should not be embedded in the file. Use spaces for alignment within a line. |
| 2 | **Line length limit** | Adopt 100 characters | 80 is too narrow for modern code (pipeline expressions, pattern matches). 120 is too wide for side-by-side diffs. 100 is the consensus sweet spot (Rustfmt uses 100, many Python projects override Black's 88 to 100). |
| 3 | **One True Brace Style** | Adapt | Nomi uses indentation for blocks (Python-like), so brace placement is not a formatting concern. However, Nomi should enforce consistent colon/newline/indent for block-introducing constructs. No variation allowed. |
| 4 | **Import ordering** | Adopt (gofmt + isort model) | Three groups: standard library, third-party, local. Alphabetical within each. Blank line between groups. This is the universal convention. |
| 5 | **Import management** | Adapt to separate tool | Import ordering belongs in the formatter. Adding/removing imports is a separate concern (like goimports or isort). The formatter reorders; the import manager adds/removes. |
| 6 | **Expression wrapping** | Adopt (Black/Dart model) | Wrap at the highest syntactic level. Function arguments wrap the entire argument list, not individual arguments. Chain expressions wrap at the chain points. |
| 7 | **Pipeline formatting** | Adopt (Elm/Dart model) | Each `|>` operation on its own line, indented one level. This is the consensus across Elm, Dart, and the F# community. |
| 8 | **Pattern match formatting** | Adopt (Rust/Elm model) | Each match arm on its own line. Patterns and bodies aligned vertically. Guards (`when`/`if`) stay on the pattern line. Nested patterns increase indentation. |
| 9 | **Data declaration formatting** | Adapt from Rust/Haskell | One field per line for multi-field declarations. Single-field declarations can stay on one line. Derived clauses (`deriving`, `where` clauses) on separate lines. |
| 10 | **Block call formatting** | Adapt (Dart cascade model) | Block calls are analogous to Dart's cascades. Each statement in the block on its own line. The block is indented one level from the call. |
| 11 | **No configuration** | Adopt (gofmt) with one reserve | Nomi ships with one canonical style. No `.nomifmt` file. No config knobs. The reserve: if the community discovers a genuine need for a variant, add a named profile (ocamlformat model), not individual knobs. |
| 12 | **Ship with the language** | Adopt (gofmt, zig fmt) | The formatter ships with the Nomi toolchain. `nomi fmt` is available from day one. There is never a pre-formatter era of Nomi. |
| 13 | **`--check` mode for CI** | Adopt (universal) | `nomi fmt --check` exits non-zero if formatting is needed. Zero-config CI enforcement. |
| 14 | **Format-on-save IDE integration** | Adopt (Prettier model) | The Nomi LSP server provides formatting. Editors with the Nomi extension format on save by default. The user never runs the formatter manually during development. |
| 15 | **Flag-day reformat with `--ignore-rev`** | Adopt (industry best practice) | When the formatter rules change (language evolution), the upgrade path is: one commit that reformats everything, added to `.git-blame-ignore-revs`. |
| 16 | **Escape hatch: `# nomi: fmt: off` / `# nomi: fmt: on`** | Adapt (Black model) | Escape hatch comments for genuinely unformattable constructs. Intentionally verbose (three tokens) to discourage casual use. Visible in code review. |
| 17 | **Comment preservation and formatting** | Adopt (Black/Rustfmt model) | Comments are attached to the nearest AST node and formatted with it. Line comments stay line comments. Block comments are reflowed to fit line length. |
| 18 | **Blank line normalization** | Adopt (Black/Dart model) | Two blank lines before top-level declarations. One blank line between methods/declarations. Extra blank lines are collapsed. |
| 19 | **String quoting** | Adopt (Black model) | Prefer double quotes. Use single quotes when the string contains double quotes. This minimizes escaping. |
| 20 | **Trailing comma behavior** | Adapt (Black's "magic trailing comma") | A trailing comma in a collection, argument list, or parameter list signals "one element per line always." Without it, the formatter collapses to one line if it fits. This gives the user one syntactic formatting lever without configuration. |
| 21 | **AST-to-string determinism** | Adopt (gofmt, Black) | `format(format(x)) == format(x)`. The formatter produces a canonical string representation from the AST. Two programs with the same AST produce identical strings. |
| 22 | **Separate formatting from linting** | Adopt (Black model) | The formatter handles whitespace, line breaks, and trivial syntax. A separate linter handles semantic rules (unused variables, complexity thresholds, style conventions). Do not conflate them in one tool. |

---

## 14. Sources

- **gofmt:** "go fmt your code" — https://go.dev/blog/gofmt
- **gofmt internals:** `go/printer` package documentation — https://pkg.go.dev/go/printer
- **Black:** "The Uncompromising Code Formatter" — https://black.readthedocs.io/
- **Black's line-breaking algorithm:** https://black.readthedocs.io/en/stable/the_black_code_style.html
- **Rustfmt:** https://github.com/rust-lang/rustfmt
- **Rustfmt configuration:** https://rust-lang.github.io/rustfmt/
- **Prettier:** "Opinionated Code Formatter" — https://prettier.io/
- **Prettier's rationale:** https://prettier.io/docs/en/rationale.html
- **elm-format:** https://github.com/avh4/elm-format
- **Wadler's "A Prettier Printer":** Philip Wadler, 1998 — the theoretical foundation for most modern formatters
- **clang-format:** https://clang.llvm.org/docs/ClangFormat.html
- **clang-format style options:** https://clang.llvm.org/docs/ClangFormatStyleOptions.html
- **Ormolu:** "A formatter for Haskell source code" — https://github.com/tweag/ormolu
- **Fourmolu:** https://github.com/fourmolu/fourmolu
- **dart format:** https://dart.dev/tools/dart-format
- **Dart's multisplit solver:** Bob Nystrom, "Crafting Interpreters" — https://craftinginterpreters.com/
- **zig fmt:** https://ziglang.org/documentation/master/#zig-fmt
- **ocamlformat:** https://github.com/ocaml-ppx/ocamlformat
- **ocamlformat profiles:** https://ocaml.org/p/ocamlformat/latest/doc/Profiles.html
- **PEP 8 — Style Guide for Python Code:** https://peps.python.org/pep-0008/
- **"Gofmt's style is no one's favorite, but gofmt is everyone's favorite"** — attributed to Rob Pike, widely cited in Go community talks and blog posts
- **"Less is exponentially more"** — Rob Pike, 2012 — https://commandcenter.blogspot.com/2012/06/less-is-exponentially-more.html
- **"The Next 700 Programming Languages"** — Peter Landin, 1966 — semantic framing referenced in multiple formatter design discussions
- **"Crafting Interpreters"** — Bob Nystrom — detailed discussion of pretty-printing algorithms in the context of language implementation
