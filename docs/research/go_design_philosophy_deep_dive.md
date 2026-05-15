# Go Design Philosophy: Deep Dive

> Status: source research for Nomi design.
> Purpose: Understand Go's design trade-offs — simplicity as a feature,
> structural interfaces, error handling, concurrency — and extract lessons
> for Nomi's everyday programming posture.

## 1. The Simplicity Thesis

Go is the most prominent modern language to make simplicity its explicit,
non-negotiable design goal. Rob Pike's "Less is exponentially more" is not
a slogan — it is the lens through which every feature proposal is evaluated.
Go's designers had built C, Unix, Plan 9, and saw the complexity curve of
C++ and Java. Go was a deliberate reaction: a language for the kind of
programming that happens inside large teams over long timelines, where
readability and predictability beat expressiveness.

### What Go deliberately left out

The omissions are as informative as the inclusions:

- **No generics** (until 1.18, 12 years later). The team refused to add a
  feature until they had a design that felt simple enough. Even the 1.18
  design was controversial internally — Ian Lance Taylor spent years
  iterating proposals. The resulting generics are constrained: type
  parameters, type sets via interfaces, no template metaprogramming.

- **No exceptions.** `panic`/`recover` exist for unrecoverable errors, not
  for control flow. Error handling is explicit and value-based.

- **No inheritance.** Struct embedding provides composition, not subtyping.
  There is no `extends`, no virtual dispatch table, no protected members.

- **No operator overloading.** Go argues that `a + b` should always mean
  exactly one thing for the types you can see. Operator overloading hides
  computation — a `+` on two matrices might allocate or block.

- **No default/optional function arguments.** Every call site passes all
  arguments. This eliminates hidden behaviour when reading a call.

- **No ternary operator.** `x ? a : b` was rejected as "hard to read in
  nested form" — the same reasoning used by Go's designers to reject many
  other concise constructs.

- **No assertions.** `assert(x != nil)` was rejected because it can be
  compiled away in production, changing program behaviour between debug
  and release builds.

- **No function annotations / decorators.** Go prioritizes "one obvious way"
  and sees decorator stacking as implicit composition.

- **No macros or code generation in the language.** Go offers `go generate`
  as an external tool. Code generation is explicit, not invisible.

- **No pattern matching.** `switch` is a simpler construct; exhaustiveness
  is not enforced.

### The readability argument

Go's design documents repeat a core claim: **code is read far more than it
is written.** "Clever" code is explicitly bad code in Go culture. A Go
programmer who writes a dense three-line function that requires five
minutes of study has failed — the fix is a 15-line function that anyone
can understand in 30 seconds.

This is a genuine philosophical position, not a rationalization for missing
features. It means:

- Go will never add a feature that saves 3 lines of writing at the cost of
  30 seconds of reading.
- Go will prefer repetition over abstraction when the abstraction hides
  control flow.
- Go will accept verbosity in exchange for locality of understanding.

The `if err != nil` pattern is the most famous example: it is repetitive
and verbose, but every error path is visible at the call site without
tracing through exception unwinding, middleware, or implicit propagation.

### `gofmt` — one canonical format enforced by tooling

`gofmt` (and later `goimports`) is arguably Go's most successful design
decision. It eliminates entire categories of argument: tabs vs spaces,
brace placement, import ordering, spacing around operators. Every Go file
in the world looks the same.

This matters more than it first appears:

1. **Code review diffs are about semantics, not formatting.** No reviewer
   ever comments on style.
2. **Learning curve flattens.** New team members read Go code immediately.
3. **Refactoring tools work predictably.** `gorename`, `gopls`, and
   automated refactors don't fight formatting.
4. **Ecosystem coherence.** Open-source Go code from different authors reads
   as if it came from one project.

The lesson for Nomi is not that Nomi must look like Go — it's that **one
canonical format enforced by tooling is a force multiplier for readability
and toolability.** Nomi already has a pipeline with inspectable stages;
adding a canonical formatter at the surface level would give the same
benefit.

### Compare with: simplicity philosophies

| Language | Simplicity posture | Key difference from Go |
|----------|-------------------|----------------------|
| **Zig** | Explicit control, no hidden control flow, no hidden allocations, comptime over macros | Zig gives more low-level control; Go hides memory layout. Both reject hidden behaviour. |
| **Odin** | Explicit over implicit, C replacement with modern sensibilities, `context` for allocators/logging | Odin keeps more C-like flexibility (pointer arithmetic) while Go restricts it. Both value "obvious code." |
| **Python** | "One obvious way to do it" (PEP 20), readability counts | Python has more features (decorators, metaclasses, descriptors) but in practice the culture constrains them. Go bakes the constraint into the language. |
| **Rust** | More features but constrained by the borrow checker — you can't write unsafe patterns without `unsafe` | Rust adds features with strong guardrails; Go omits features. Different strategy, similar goal of preventing footguns. |
| **Swift** | Many features, progressive disclosure — novices see a simple language, experts unlock power | Swift's approach is "add everything, hide complexity through defaults." Go's approach is "don't add it at all." |

Go's simplicity thesis is at one end of a spectrum. Zig is nearby (explicit,
no hidden flow). Rust is in the middle (many features, strong guardrails).
Swift and C++ are at the other end (accumulate features, trust users to
pick subsets). Nomi should place itself deliberately on this spectrum
rather than drift. The convenience docs already argue for reducing surface
sugar to normal forms — that is a Go-aligned instinct.

---

## 2. Error Handling: `if err != nil`

### The design choice

Go's error handling was not an oversight. The team explicitly rejected
exceptions based on their experience with C++ and Java. Their reasoning:

1. **Exceptions create invisible control flow.** A function call might
   actually return three calls up the stack. You cannot see which by
   reading the call site.
2. **Exceptions encourage poor handling.** `catch (Exception e) { }` is
   the empty catch block that swallows errors. `throws Exception` on
   every method signature in Java is noise, not documentation.
3. **Exceptions couple error handling to the call stack.** This makes
   concurrent error handling awkward — which goroutine does the exception
   unwind through?

Instead, Go treats errors as ordinary values. Functions return `(result,
error)` tuples. The caller checks `if err != nil` at the call site.

### Error values over exceptions

```go
f, err := os.Open("config.json")
if err != nil {
    return fmt.Errorf("loading config: %w", err)
}
defer f.Close()
```

This is the canonical Go error pattern. `errors.Is(err, fs.ErrNotExist)`
checks for specific sentinel errors. `errors.As(err, &target)` extracts
typed errors from the chain. `%w` wraps errors while preserving the chain
for inspection.

Key properties of this model:

- **Errors are just values.** Any type implementing `Error() string` is an
  error. Error types can carry structured data.
- **Error wrapping is additive.** Each layer adds context. At the top, the
  error chain reads: `loading config: open config.json: permission denied`.
- **Sentinel errors are comparable.** `err == io.EOF` works because the
  error is a package-level variable.
- **No stack traces by default.** This is a trade-off. You don't pay for
  what you don't need, but debugging opaque errors requires adding context
  at every layer.

### The verbosity trade-off

The `if err != nil` pattern appears on roughly every third line in
system-level Go code. Critics call it boilerplate. Defenders call it
explicit, grep-able, and local.

The truth is in between:

- **What's gained:** Every error path is visible. You can read a function
  top to bottom and see exactly where errors are handled. There is no
  `except Exception: pass` lurking in a caller three frames up. Refactoring
  error handling is mechanical.
- **What's lost:** Signal-to-noise ratio drops. In a function that chains
  five operations, three lines might be actual logic and seven might be
  error checks. The happy path is obscured by the error paths.
- **The Go community's equilibrium:** Most Go programmers stop noticing
  after a few weeks. The pattern becomes background noise. Tooling (editor
  snippets, `errcheck` linter) reduces the typing cost.

### Nomi's position

Nomi already distinguishes three error categories (from
`docs/convenience/absence_and_result.md`):

1. **Absence** (`None`, `?.`, `??`) — "no value."
2. **Expected failure** (`Result`, `?`, `try`) — "operation failed."
3. **Unexpected error** (exceptions) — "something broke."

Go collapses absence and expected failure into one mechanism (`nil` error),
which is a meaningful design loss. A `nil` return from `map[key]` with a
`false` second return value is a completely different thing from an
`os.Open` failure, but Go represents both as multi-return with a check.

Nomi's `Result` + `?` can give the same explicit error paths as Go while
reducing the verbosity — `?` propagates errors visibly (like Rust `?` or
Zig `try`) without eight-line `if err != nil` blocks. The key is that `?`
is still visible in the source — it doesn't hide the error path, it
shortens its spelling.

**Lesson for Nomi:** Adopt Go's explicitness (errors are values, visible at
the call site). Reject Go's verbosity (every call needing a three-line
check). `Result` + `?` is the synthesis: the error path is one character,
not three lines, but it's still right there in the source.

### Error model comparison

| Language | Error mechanism | Propagation | Exhaustiveness | Structured errors |
|----------|----------------|-------------|----------------|-------------------|
| **Go** | Multi-return `(T, error)` | Manual `if err != nil` + `return` | Compiler checks unused values | `errors.Is/As`, sentinels, `%w` |
| **Zig** | Error union `!T` + error sets | `try` prefix operator | Error sets can be exhaustive | Error sets are named; `catch` captures |
| **Rust** | `Result<T,E>` enum | `?` operator | `must_use` on Result; exhaustive `match` | Enum variants carry data; `thiserror`/`anyhow` |
| **Swift** | `throws` + `Result<T,E>` | `try` / `try?` / `try!` | Checked at function boundary | `Result` enum with typed errors |
| **Gleam** | `Result(a, e)` type | `use` expression (no `?`) | Exhaustive `case` required | Algebraic `Ok`/`Error` |
| **Nomi** | `data Result[T,E]` (O/E) + exceptions | `?` (design phase) | `match` on Result enforces handling | `data` variants carry typed error info |

---

## 3. Interfaces: Structural Typing

### Implicit interface satisfaction

Go's most distinctive type-system feature: a type satisfies an interface
by implementing its methods. There is no `implements` keyword, no explicit
declaration, no `derive`. If it quacks like a duck, it is a duck:

```go
type Reader interface {
    Read(p []byte) (n int, err error)
}
```

Any type with a `Read([]byte) (int, error)` method satisfies `io.Reader`.
The type's author does not need to know `io.Reader` exists. This is
**structural typing** — the interface is defined by its shape, not by a
nominal declaration chain.

### The `io.Reader` ethos: one-method interfaces

Go's standard library is built on small interfaces. `io.Reader` is one
method. `io.Writer` is one method. `io.Closer` is one method. These compose
into `io.ReadWriter`, `io.ReadCloser`, `io.ReadWriteCloser` through
embedding:

```go
type ReadCloser interface {
    Reader
    Closer
}
```

This is Go's answer to the expression problem: define small contracts and
compose them. A function that needs to read takes `io.Reader` — it does not
care whether the source is a file, a network connection, an in-memory
buffer, or a decompressor. This is genuinely elegant and has shaped how
Go programmers design APIs.

### The nil interface gotcha

The most famous Go footgun: a nil concrete type inside a non-nil interface
is not equal to nil:

```go
var r io.Reader
var b *bytes.Buffer
r = b           // r is NOT nil, even though b is nil
r == nil        // false
```

An interface value is a pair: (type, value). `r` is `(*bytes.Buffer, nil)`,
which is not `(nil, nil)`. This bites every Go programmer at least once and
is a direct consequence of structural typing combined with nil pointers.

The migration from `interface{}` to `any` (Go 1.18) was a rename that
acknowledged this pain: the empty interface was always "any type," and the
keyword should say that. It does not fix the nil interface problem.

### Generics + interfaces: the compromise

Go 1.18 generics use interfaces as type constraints. A type parameter
`[T io.Reader]` constrains `T` to types satisfying `io.Reader`. This is
the "zero-cost" integration: generics reuse the existing interface concept
rather than introducing a separate constraint language.

The design is deliberately constrained:
- No variadic type parameters.
- No higher-kinded types.
- No specialization or template metaprogramming.
- Methods cannot take additional type parameters.

This is Go's simplicity thesis applied to generics: give 80% of the value
(typed collections, generic algorithms) for 20% of the complexity cost.

### Comparison: structural vs nominal typing

| Language | Typing | Satisfaction | Key property |
|----------|--------|-------------|--------------|
| **Go** | Structural | Implicit — method set matches the interface | Decouples interface definition from type definition |
| **Rust** | Nominal (traits) | Explicit `impl Trait for Type` | Coherence — one impl per type per trait in the defining crate |
| **Swift** | Nominal (protocols) | Explicit `class/struct: Protocol` in declaration or extension | Retroactive conformance via extensions |
| **Kotlin** | Nominal (interfaces) | Explicit `class Foo : Interface` | Declaration-site conformance; no retroactive |
| **TypeScript** | Structural | Implicit — shape matches type | Same as Go: decoupled, but no nil-interface gotcha (strict nulls) |
| **C++** | Nominal (concepts, C++20) | Explicit model, structural checking | Concepts check structural requirements but require explicit opt-in |
| **Python** | Duck typing (runtime) | No static check — `hasattr` + try | Most flexible, least safe. Protocols/mypy add optional structural checking. |

**Nomi's position:** Nomi is explicitly nominal with `data` and structural
at external boundaries (see `syntax_design_rules.md` axis table). This is
a deliberate hybrid — owned types are nominal (you said what it is),
external data is structural (it arrives with a shape, not a declaration).

Go's structural interfaces are elegant for small contracts but break down
for larger ones (the nil-interface problem, no exhaustiveness, accidental
satisfaction). Nomi's nominal core avoids these. But the `io.Reader`
lesson — one-method interfaces are powerful — maps naturally to Nomi's
block-call design, where a block-callable function is "anything that
accepts a block with the right signature."

---

## 4. Concurrency: Goroutines and Channels

### CSP model

Go's concurrency is built on Hoare's Communicating Sequential Processes:

> "Don't communicate by sharing memory; share memory by communicating."

Goroutines are lightweight user-space threads multiplexed onto OS threads.
Channels are typed conduits between goroutines. The `select` statement
multiplexes across multiple channel operations.

```go
go worker(ch)
ch <- item
result := <-ch
```

The runtime grows and shrinks the thread pool, manages the goroutine
scheduler, and handles blocking I/O under the hood. Starting a goroutine
costs a few KB of stack (growable). You can have 100,000 goroutines on a
laptop.

### What Go concurrency gets right

1. **The model is small.** Goroutines, channels, `select`, `sync` package.
   That's the core. Everything else (`errgroup`, worker pools, semaphores)
   is built on these primitives.
2. **CSP forces you to think about data ownership.** If you pass a value
   through a channel, the sender gives up ownership. If you share a pointer,
   you are explicitly choosing shared memory.
3. **`select` is a genuinely good primitive.** It handles timeouts,
   cancellation, and multiplexing in one construct. No custom event-loop
   or future-chaining needed.
4. **`errgroup` shows the library-first approach.** Rather than adding
   structured concurrency to the language, `golang.org/x/sync/errgroup`
   provides a small abstraction over `sync.WaitGroup` that propagates the
   first error. Library-first works when the core primitives are right.

### What Go concurrency gets wrong

1. **Channels are not the answer to everything.** The "share memory by
   communicating" slogan led early Go programmers to over-use channels.
   Many patterns are better expressed with mutexes and shared state. The
   community eventually reached equilibrium: use channels for
   communication between goroutines; use mutexes for shared state within
   a data structure.
2. **Goroutine leaks are easy.** A goroutine blocked on a channel send
   that nobody receives from will leak forever. There is no runtime
   detection of leaked goroutines (only the race detector helps).
3. **No structured concurrency.** There is no language-level guarantee
   that a spawned goroutine completes before its parent returns. `sync
   .WaitGroup` is manual. Nathaniel J. Smith's "Notes on structured
   concurrency" (the inspiration for Trio nurseries and Kotlin
   `coroutineScope`) argues that goto-like goroutine spawning is the
   concurrency equivalent of unstructured `goto` — powerful but
   uncomposable.
4. **Context propagation is viral.** `context.Context` passes cancellation,
   deadlines, and request-scoped values through every function. In
   practice, it becomes the first parameter of nearly every function in a
   server. This is explicit (good) but boilerplate-heavy (bad).
5. **Channel zero value.** A nil channel blocks forever in both send and
   receive. This is intentional (it makes `select` cases skippable) but
   is deeply unobvious to newcomers.

### Nomi's position

Nomi's concurrency story is intentionally deferred (see
`docs/convenience/concurrency.md`). The design direction is:

- **Block policies over function colors.** Go's model has no async/sync
  split — every function can spawn goroutines. This is the right call.
  Nomi avoids the function-color problem by using block policies for
  all control abstraction, including future concurrency.
- **Structured concurrency.** Go's unstructured `go` keyword is powerful
  but uncomposable. Nomi's `parallel:` block (future) should guarantee
  that all spawned work completes or is cancelled before the block exits.
- **Channels as library, not syntax.** Go's channels are built-in types
  with special syntax (`<-`, `chan`, `select`). Nomi can provide channels
  as a standard library type with block-policy-based operations rather
  than dedicated syntax.

### Concurrency model comparison

| Language | Model | Key abstraction | Structured? | Cancellation |
|----------|-------|----------------|-------------|-------------|
| **Go** | CSP | Goroutine + channel + `select` | No (manual WaitGroup) | `context.Context` |
| **Erlang/Elixir** | Actor model | Process + message passing | OTP supervisors | Process links + monitors |
| **Rust** | Async/await + tokio | Future + task + reactor | `JoinSet` / `FuturesUnordered` | `CancellationToken` / `drop` |
| **Kotlin** | Structured coroutines | `suspend` + `coroutineScope` | Yes (scope-bound) | `Job.cancel()` (cooperative) |
| **Swift** | Structured concurrency | `async` + task groups | Yes (task-tree) | `Task.cancel()` (cooperative) |
| **Java** | Virtual threads (Loom) | `Thread` (virtual) | No (like Go) | `Thread.interrupt()` |
| **Nomi** | Block policies (future) | Call + attached block + yield | Design target | Block policy scope exit |

---

## 5. Package Design

### One package per directory, one directory per package

Go's module system is built on a simple rule: a directory is a package.
All `.go` files in a directory share the same package declaration. The
package name is conventionally the directory's basename (with underscores
converted from dashes). This is so simple it's easy to miss how much
design weight it carries:

- **Finding code is trivial.** The import path maps directly to directory
  structure. `import "net/http"` means the `http` package inside the `net`
  directory. No alias files, no `__init__.py`, no `mod.rs`.
- **Packages are namespaces, not modules.** Within a package, all files
  share the same namespace. There is no `from X import Y` — everything
  defined in the package is visible to every file in the package.
- **Package boundaries are compilation boundaries.** Circular imports are
  caught by the compiler. This forces a directed acyclic graph of package
  dependencies, which in turn forces clean architecture. You literally
  cannot create a dependency cycle.

### Capitalization as visibility

Go uses capitalization for export control: `Name` is exported, `name` is
unexported. There is no `public`/`private`/`protected` keyword. The rule
is simple and universal, but has sharp edges:

- **Good:** It's always visible. You never wonder whether something is
  exported — it's right there in the identifier.
- **Bad:** It breaks with Unicode. Non-Latin scripts don't have case in
  Go's sense. Renaming for visibility changes the identifier itself,
  which can break serialization or external references.
- **Ugly:** It makes API design visible in naming. An exported field you
  later want to unexport requires renaming it (breaking consumers) or
  deprecating it (leaving clutter).

### No circular imports

This is a rule, not a guideline. The compiler enforces it. The result is
that Go package graphs are always DAGs. This forces developers to extract
shared types into a third package (often a `types` or `model` package)
when two packages need to reference each other's types. This is initially
annoying but pays off in maintainability — the dependency graph is always
explicit and comprehensible.

### `internal/` for private packages

Go 1.4 introduced the `internal` directory convention: packages under an
`internal/` directory can only be imported by code rooted at the parent of
`internal/`. This provides encapsulation within a module without needing
a separate repository. `net/http/internal` is importable only from within
`net/http` and its sub-packages.

### Standard library organization

Go's standard library is one of its strongest assets. The ethos: small,
focused packages that do one thing well. `net/http` is an HTTP server and
client. `encoding/json` is just JSON. `crypto/tls` is just TLS. Packages
are not organized by layer (model, controller, view) but by capability.

### Nomi's position

Nomi inherits Python's import system for interop but should learn from
Go's package design:

- **One package per directory** is simpler than Python's `__init__.py`
  package-as-directory-with-magic-file model.
- **No circular imports** should be a tooling-enforced rule, not just a
  convention.
- **Capitalization as visibility** is clever but not worth adopting. Nomi
  should use explicit `pub` or similar — the identifier should not change
  when you decide to export or hide it.
- **Small, capability-focused packages** are a good standard library
  philosophy regardless of language.

---

## 6. `defer`

### The design

`defer` schedules a function call to execute when the surrounding function
returns. Deferred calls execute in LIFO order — the last deferred call
runs first, like unwinding a stack.

```go
f, err := os.Open("config.json")
if err != nil {
    return err
}
defer f.Close()
// ... use f ...
```

The key design properties:

1. **Deferred at the acquisition point.** `defer f.Close()` sits right next
   to `os.Open`. You see the acquisition and the cleanup together. This is
   the defining ergonomic improvement over `try`/`finally`, where the
   cleanup block is physically separated from the acquisition.
2. **Arguments evaluated at defer point, execution at return.** `defer
   fmt.Println(i)` captures the value of `i` when `defer` is called, not
   when the function returns. If you want the final value, defer a closure
   that captures by reference.
3. **LIFO execution.** If you acquire A, then B, then C, cleanup runs C,
   B, A. This is naturally correct for nested resource acquisition.
4. **Interaction with named return values.** A deferred closure can
   modify named return values. This is used for error wrapping patterns.

### `defer` in loops

`defer` in a loop accumulates until the *function* returns, not the loop
iteration ends. This is a common pitfall:

```go
for _, file := range files {
    f, _ := os.Open(file)
    defer f.Close()  // ALL files close when the function returns — leak risk
}
```

The fix is an explicit closure or extracting the loop body into a function.
This makes `defer` unsuitable for loop-scoped cleanup — a notable gap.

### Cross-language `defer` comparison

| Language | Keyword | Argument eval | Error variant | Loop-scoped? | Scope |
|----------|---------|--------------|---------------|-------------|-------|
| **Go** | `defer` | At defer point | No (use named returns) | No (accumulates to function return) | Function |
| **Zig** | `defer` | At defer point | `errdefer` (only on error) | No (block-scoped with `{ }`) | Block |
| **Odin** | `defer` | At defer point | `defer if err != nil { }` pattern | Yes (deferred per iteration) | Scope |
| **Swift** | `defer` | At defer point | No | Yes (deferred at scope exit, including loops) | Scope |
| **Nomi** | Block cleanup policy | Policy-defined | Block policy (callee controls) | Depends on block policy | Block |

Go's `defer` is the reference implementation — the one every other
language's `defer` is measured against. Its core insight (put cleanup next
to acquisition) is universal. Its limitations (no loop-scope, no
error-only variant) have been addressed by Zig (`errdefer`) and Odin
(scope-level defer).

For Nomi, the lesson is: **cleanup should be visible at the acquisition
point.** Whether that's `defer`, a block policy, or a `using` block, the
principle remains. Nomi's block-call design is more general than `defer` —
a callee can define what "cleanup" means for its resource, and the block
policy handles both success-path and failure-path cleanup.

---

## 7. Zero Values and Initialization

### Every type has a zero value

Go guarantees that every variable declaration produces a usable value
without an explicit initializer. `var x int` is `0`. `var s string` is
`""` (not `nil`). `var p *int` is `nil`. There are no uninitialized
variables, no `undefined` like JavaScript, no indeterminate values like C.

The zero-value principle means you never wonder what a freshly-declared
variable contains. It means struct literals with omitted fields get their
zero values. It means `new(T)` and `var t T` produce identical results.

### Zero-value-usable types

Some Go types are designed to work with their zero value:

```go
var mu sync.Mutex   // Ready to use — no constructor needed
mu.Lock()
mu.Unlock()

var buf bytes.Buffer // Ready to use — no constructor needed
buf.WriteString("hello")

var wg sync.WaitGroup // Ready to use
wg.Add(1)
```

This is deliberate design: if a type needs a constructor to be usable, it
likely has unstated invariants that can be violated. Types that work with
their zero value make the happy path shorter.

### The `nil` problem

The zero value for pointers, slices, maps, channels, interfaces, and
functions is `nil`. The behaviour is inconsistent:

- A nil slice has `len 0`, can be appended to, and ranges over zero times.
  A nil `[]byte` is often indistinguishable from an empty `[]byte`.
- A nil map panics on write. `var m map[string]int; m["key"] = 1` panics.
  This is the most common nil-related panic in Go.
- A nil channel blocks forever in both send and receive. This is
  intentional and useful in `select`, but baffling to newcomers.
- A nil function panics on call. `var f func(); f()` panics.
- A nil interface is `(nil, nil)`, which is equal to `nil`. But an
  interface holding a nil concrete type is NOT nil — the classic gotcha.

### Nomi's position

Nomi should learn from Go's zero values but not replicate them:

**Adopt:** Types that work without a constructor. `sync.Mutex`-style
"zero value is useful" is a good API design principle for any language.

**Reject:** `nil` as a universal default. The nil-slice-works /
nil-map-panics inconsistency is confusing. Nomi's absence type (`None`)
should be explicit where absence is possible. The `Option` type enforces
handling rather than surprising with panics.

**Reject:** Zero values as meaningful state. `""` as the default string
is fine for display but dangerous as a sentinel — is this an empty name
or a missing name? Go conflates these. Nomi should keep absence (`None`)
separate from zero values (`""`, `0`, `[]`).

---

## 8. What Go Gets Right (and Nomi Should Adopt)

### `gofmt` — one canonical format

**Lesson:** A language should ship with a canonical formatter, and it
should be non-negotiable. Nomi's inspectable pipeline (raw tree to
transformed tree to surface AST to Python AST) is already a step toward
this — the pipeline is the single path from source to execution. Adding a
canonical surface formatter that outputs standardised Nomi text would
complete the story: one way to format, one pipeline to execute.

### Small interfaces — one-method contracts

**Lesson:** `io.Reader` is one method. The Reader/Writer/Closer composition
model is elegant and encourages focused abstractions. Nomi's block-call
design naturally mirrors this: a block-callable function is "a function
that accepts a block with signature X," which is the same structural
thinking as "a type that implements method X."

Nomi's `data` (nominal) and external boundaries (structural) hybrid is
already a more principled version of Go's all-structural approach. Keep
the small-contracts ethos, use nominal typing for owned types.

### Explicit error paths

**Lesson:** Errors should be visible at the call site. Go's `if err != nil`
is verbose but honest. Nomi's `Result` + `?` can achieve the same honesty
with less ceremony — `?` is one character that says "error may propagate
here" without dominating the source.

### `defer` for cleanup — visible at acquisition

**Lesson:** Cleanup should be declared right next to acquisition, not in a
separate `finally` block. LIFO execution is naturally correct for nested
resources. Nomi's block policies are a superset of `defer` — they handle
both success-path and failure-path cleanup, and the callee defines the
cleanup semantics.

### Package as directory — simple module structure

**Lesson:** One directory, one package, one namespace. The import path IS
the directory path. No `__init__.py` magic, no `mod.rs` routing. For
Nomi's future module system, this is the baseline simplicity to aim for.

### No circular imports

**Lesson:** Forcing a DAG dependency structure catches bad architecture
early. Python allows circular imports (and handles them with partial
module objects — a source of subtle bugs). Nomi should enforce acyclicity
at the tooling level.

---

## 9. What Go Gets Wrong (and Nomi Should Avoid)

### Zero values as meaningful state

**Problem:** `nil` slices work but `nil` maps panic. The zero value of
`int` is `0`, which is a perfectly valid integer — but is it a default
or a real value? Go conflates "not set" with "empty." Nomi should keep
absence (`None`) separate from zero values (`""`, `0`, `[]`). If a value
might be absent, the type should say so: `Option[T]`, not `T` with a
magic sentinel.

### No exhaustiveness checking

**Problem:** Go's `switch` without `default` compiles and runs fine. There
is no compiler check that you've handled all cases of an enum or all
variants of a sum type — because Go has neither enums nor sum types in the
ML/Haskell sense. `iota` is a convention, not a type-safe enumeration.

Nomi's `match` on `data` types should enforce exhaustiveness. This is one
of the core value propositions of algebraic data types and pattern matching
— the compiler tells you what you forgot.

### `if err != nil` verbosity

**Problem:** Explicit but repetitive. In functions that chain 5-10
fallible operations, error handling can be 60-70% of the lines. Nomi's
synthesis — `Result` + `?` — is the right upgrade: keep explicitness (the
`?` is visible in source), reduce ceremony (it's one character, not three
lines).

### No sum types

**Problem:** Go represents variants through either `interface{}` (losing
all type information) or multiple return values like `(T, bool)` (ad-hoc
and not composable). Nomi's `data` gives proper sum types with exhaustiveness
checking, pattern matching, and typed variant data.

### Capitalization as visibility

**Problem:** Changes to visibility require renaming the identifier. This
breaks consumers, serialization, and documentation links. It doesn't work
with non-Latin scripts. Explicit visibility modifiers (`pub`, `internal`,
`private`) are strictly better — they decouple the name from the access
policy.

### The nil interface problem

**Problem:** A typed nil pointer stored in a non-nil interface causes
runtime panics that the type system promised to prevent. This is a
structural-typing footgun that Nomi's nominal core avoids by design. If
Nomi adds structural typing for external data, it should do so with a
strict null-safety rule that prevents the typed-nil-in-untyped-interface
trap.

### Goroutine leaks and unstructured spawning

**Problem:** `go f()` is the concurrency equivalent of `goto` — powerful,
simple, and uncomposable. There is no guarantee that a spawned goroutine
will ever complete or be cleaned up. Nomi's future concurrency model should
be structured from the start, with block-scoped parallelism that guarantees
completion or cancellation.

---

## 10. Cross-Language Synthesis

### Go vs Zig vs Odin: three flavours of simplicity

Go, Zig, and Odin all position themselves as reactions against C++ and
Java complexity, but they react differently:

- **Go** wants to make reading code effortless for large teams. It removes
  features aggressively. It trusts the runtime (GC, scheduler). It prefers
  a small stdlib with "one way" for each task.
- **Zig** wants to make control explicit. It keeps pointers, manual memory,
  and compile-time execution. It trusts the programmer to want control, not
  protection. `try`, `errdefer`, and `comptime` are sharper tools than Go's
  equivalents.
- **Odin** wants to make game/systems programming pleasant without the C++
  complexity tax. It keeps more features than Go (operator overloading for
  math types, `using` for namespace injection, parametric polymorphism)
  but restricts them with a "don't abuse this" culture and a `context`
  system that makes allocators and loggers explicit.

For Nomi, the lesson is: **simplicity is not one thing.** Go's simplicity
is "fewer features." Zig's simplicity is "nothing hidden." Odin's
simplicity is "obvious code." Nomi can define its own: **every feature
reduces to a known normal form, and that reduction is inspectable by
tooling.** This is closer to Go's "one way" than Zig's "nothing hidden,"
but with a structural guarantee that Go lacks.

### The "one way" vs "multiple paradigms" tension

Go's "one way to do it" sits at one end of a spectrum. Python's "there
should be one — and preferably only one — obvious way to do it" (PEP 20)
is nearby. At the other end: C++ ("there are seven ways, and the style
guide picks the least dangerous"), Scala ("choose your paradigm"), and
Perl ("there's more than one way to do it" as a feature).

Nomi's position should be closer to Go than to Scala. The syntax design
rules already say that surface sugar must reduce to a normal form that
tooling can show. That's a "one way at the normal-form level, pleasant
surface variations" posture — stricter than Python, more flexible than Go.

### Structural vs nominal typing: where Go and Nomi agree and differ

Both Go and Nomi value decoupling: Go through structural interfaces, Nomi
through structural external boundaries. Both want the code that *uses* an
abstraction to define its shape, not the code that *provides* it. The
difference is scope:

- **Go:** All typing is structural. This is elegant for small interfaces
  but creates the nil-interface problem and accidental satisfaction.
- **Nomi:** Owned types are nominal; external boundaries are structural.
  This is more principled — you own what you declare, you describe what
  you receive.

### `defer` across five languages

The `defer` pattern appears in Go, Zig, Odin, Swift, and (potentially)
Nomi. The universal insight: **cleanup should be declared at the
acquisition point, not at a distant `finally` block.** LIFO execution
order is the natural unwinding order.

What varies:
- **Scope:** Go (function), Swift (current scope), Zig (block), Odin
  (scope). Nomi's block policies are the most flexible — the callee
  defines the cleanup scope.
- **Error sensitivity:** Go has no error-specific defer. Zig adds
  `errdefer` (run only on error). Odin patterns use `defer` with an
  explicit `if err != nil` check. Nomi's block policies handle both
  paths naturally through the block's result.
- **Argument evaluation:** All four languages evaluate arguments at the
  defer point, not at execution time. This is the correct choice — you
  want the value as it was when the cleanup was scheduled, not some
  mutated later state.

---

## 11. Summary: Go's Lessons for Nomi

### Adopt

| Go feature | Why | Nomi form |
|-----------|-----|-----------|
| `gofmt` | One canonical format eliminates style arguments and improves review | Canonical surface formatter + inspectable pipeline |
| Small interfaces | One-method contracts compose beautifully | Block-callable functions as small contracts |
| Errors as values | Explicit, grep-able, local reasoning | `Result` + `?` — explicit but concise |
| `defer` at acquisition | Cleanup visible next to allocation | Block policies with cleanup semantics |
| Package as directory | Simple, predictable, discoverable | One-package-per-directory module structure |
| No circular deps | Forces clean architecture DAG | Tooling-enforced acyclicity |
| Library-first concurrency | `errgroup` not language keyword | Block policies as the one control abstraction |

### Reject

| Go feature | Why | Nomi alternative |
|-----------|-----|-----------------|
| Zero values as sentinels | `nil` slice works, `nil` map panics — inconsistent | `Option` type separates absence from zero |
| No exhaustiveness | `switch` without `default` compiles fine | Exhaustive `match` on `data` types |
| `if err != nil` verbosity | Explicit but repetitive | `?` — visible propagation, one character |
| No sum types | `interface{}` or `(T, bool)` for variants | `data` with typed variant payloads |
| Capitalization as visibility | Breaks on rename, non-Latin, serialization | `pub` / explicit visibility modifiers |
| `nil` interface gotcha | Typed nil in untyped interface | Nominal core with strict null safety |
| Unstructured goroutines | `go` is concurrency `goto` | Structured block-scoped concurrency |

### Deliberately Ambiguous

| Go practice | The tension | Nomi's call |
|------------|-------------|-------------|
| "One way" vs expressiveness | Go is rigid; Python allows style variation | Normal-form reduction as the "one way," surface sugar for expressiveness |
| Stdlib scope | Go's stdlib is curated and small; Python's is "batteries included" | Prelude for core operations; library ecosystem for domain-specific |
| GC vs manual memory | Go uses GC; Rust/Zig don't | GC (Python-hosted) is correct for Nomi's target layer |
| `context.Context` propagation | Explicit but viral — every function gets it | Block policies make context implicit within a scoped call |
| Simplicity ceiling | Go resists features; languages that stop growing feel stagnant | Nomi should grow by *reducing* to existing normal forms, not by adding primitives |

Go is the most important reference point for Nomi's *posture* — not its
surface syntax or type system, but its discipline about what not to add
and its insistence that readability beats expressiveness. Nomi's design
should internalize Go's restraint while using its richer type system (`data`,
pattern matching, block policies) to fix Go's most painful omissions:
exhaustiveness, sum types, and structured error handling.
