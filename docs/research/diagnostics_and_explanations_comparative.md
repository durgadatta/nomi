# Diagnostics, Error Messages, and Explanation Design

> Status: cross-language comparative research; active synthesis for Nomi design.
>
> Purpose: Compare how languages design diagnostic messages, error reporting,
> and program explanation — then extract durable lessons for Nomi's explanation
> normal form.

## Why This Matters for Nomi

Every language that takes diagnostics seriously made an architectural decision
*before* the first error message was written: where does explanation live, what
information does the pipeline preserve, and who produces the text? Nomi is
building its explanation normal form now, so we can learn from languages that
got this right (and wrong) without inheriting their constraints.

This document is not a catalogue of error message quality. It is a comparison
of **diagnostic architectures** — the structural decisions that determine
whether a language can explain itself well, and whether that explanation
composes across layers, libraries, and tools.

---

## 1. Language Deep-Dives (Architectural Focus)

### 1.1 Rust — The Structured Diagnostic Architecture

Rust's diagnostic system is not "good error messages bolted onto the compiler."
It is an **internal diagnostic framework** that every compiler pass emits into,
and that framework enforces structural consistency across all error kinds.

**The architecture layer cake:**

```
Compiler pass → DiagnosticBuilder<'a> → Diagnostic { level, code, messages, spans, children }
             → Emitter (JSON / human-readable / IDE) → output
```

Every compiler error goes through `DiagnosticBuilder`. A pass never prints a
string directly. It constructs a typed structure: a primary span (where the
error is), optional secondary spans (related locations), labels on each span,
a `help:` block with concrete suggestions, and a `note:` block with contextual
information.

**Span strategy:** Multi-span with labeled sub-spans. Rust's borrow-checker
diagnostics routinely use 3-4 spans: "borrow occurs here," "move occurs here,"
"value borrowed here after move." Each span carries its own label string, and
the renderer places them in reading order.

**Error codes as stable identifiers:** `E0382` (use of moved value), `E0502`
(cannot borrow as mutable because also borrowed as immutable). These are:
- Machine-lookup: `rustc --explain E0382` prints a full explanation page
- Stable across compiler versions (error codes are part of the stability guarantee)
- Indexed in the Rust Reference
- Usable as `#[allow(E0382)]` for lint-level control

**The "compiler as teacher" philosophy:** Rust's diagnostics don't just say
what's wrong — they teach the concept. A borrow error doesn't just say "move
after borrow." It explains ownership, shows the conflicting regions, and often
suggests a structural fix (add a block scope, clone the value, use a reference).

**`rust-analyzer` and LSP integration:** The same diagnostic structure that
`rustc` emits as text is emitted as LSP `Diagnostic` objects by
`rust-analyzer`, with `relatedInformation` carrying the multi-span links. This
means editor squiggles, hover cards, and `rustc` output share the same
underlying diagnostic model.

**Library participation — `anyhow` and `thiserror`:** The structured approach
extends into libraries:
- `thiserror` derives `std::error::Error` with `#[error("...")]` format strings
- `anyhow` provides context chaining: `anyhow::Context::context("while reading config")`
- Library errors carry `source()` chains for causal tracing
- The `#[source]` attribute preserves the error chain for diagnostics

Rust's key architectural insight: **diagnostics are structured data first,
rendered text second.** The text is a view over the structure, not the structure
itself.

---

### 1.2 Elm — The Beginner-First Diagnostic System

Elm's diagnostics are famous not because they are architecturally general (they
are not) but because they are **optimized for a specific audience** — learners
who do not know the language yet. Every design decision flows from "the person
reading this error may have never seen a type before."

**Distinctive elements:**

*Suggestion-first formatting.* An Elm type mismatch doesn't just show the types.
It re-reads the user's code, compares it to known patterns, and says "I think
you meant..." with a concrete replacement. This is a **heuristic suggestion
engine** built into the type checker, not a generic formatting layer.

*Prose error style.* Elm errors read like a teacher explaining a mistake, not
like a compiler dump. The message uses complete sentences, avoids jargon unless
defined, and often includes the *reasoning* behind the suggestion.

*No runtime exceptions (almost).* Because Elm's type system eliminates null,
undefined, and unhandled cases, there are almost no runtime errors in user code.
This means the entire diagnostic budget is spent on compile-time: type errors,
syntax suggestions, and pattern exhaustiveness checks.

*Architecture limitation.* Elm's diagnostics are deeply coupled to the type
checker's constraint solver. The "I think you meant" suggestions work because
the solver explores nearby solutions and reports the closest match. This is
powerful but **non-portable** — a dynamic language cannot replicate it without
a type inference engine.

**Key lesson:** Elm proves that diagnostic quality is not just about message
text. It's about what information the compiler *has available* when it produces
the message. Elm's solver knows multiple near-miss types — the diagnostic
rendering just surfaces that information. The **architecture** (constraint
solving → near-miss search → suggestion) produces the quality; the message text
is the last mile.

---

### 1.3 Gleam — The Friendly Compiler with Specific Suggestions

Gleam sits between Rust and Elm philosophically. Its compiler emits structured
diagnostics with specific "Did you mean?" suggestions, but unlike Elm, it does
not attempt full heuristic exploration. Gleam's suggestions are **deterministic**
— based on edit distance of names, known imports, and pattern exhaustiveness
analysis.

**Architecture:** Gleam's compiler is written in Rust and uses a
`Diagnostic`-like internal structure. Diagnostics carry a location, a message,
optional labels, and optional "hints" (suggestions). The compiler renderer
produces terminal-colored output with carets and highlights.

**Pattern-match exhaustiveness** is a signature diagnostic. When a pattern is
non-exhaustive, Gleam shows the uncovered patterns with actual constructor
names, not just "patterns not covered." The diagnostic says "You forgot these
cases: `Ok(value)`, `Error(reason)`" — using the user's own type definitions.

**What Gleam adds to the synthesis:** Gleam shows that a compiler for a
smaller, simpler language can still produce excellent diagnostics *if the
diagnostic infrastructure is built in from the start.* Gleam's compiler is
younger than Rust's but its diagnostics are already competitive because the
authors treated diagnostics as a first-class compiler output, not an
afterthought.

---

### 1.4 Racket — Contracts, Blame, and Gradual Explanation

Racket's diagnostic story is fundamentally different from the ML-family
languages above because Racket is **gradually typed** and **dynamically
checked.** The diagnostic architecture lives in the runtime, not (only) the
compiler.

**Contract violation diagnostics:** When a function contract is violated, Racket
produces a blame assignment:
```
> (string-length 42)
string-length: contract violation
  expected: string?
  given: 42
  in: the 1st argument of
      (-> string? exact-nonnegative-integer?)
  contract from: <collects>/racket/private/string.rkt
  blaming: top-level
   (assuming the contract is correct)
```

The key architectural concepts:

*Positive vs. negative blame.* If a function's *body* violates the contract,
that's positive blame — the function promised something and didn't deliver. If
the *caller* passes a bad argument, that's negative blame — the caller broke
the function's precondition. Racket's contract system distinguishes these and
reports them differently.

*Blame tracking across module boundaries.* Contracts are attached at module
boundaries (via `provide/contract`), and the blame message names the specific
module that is responsible. This creates a **distributed accountability**
model: library code and client code each have clear responsibilities.

*Gradual typing bridge.* Typed Racket's type errors are reported with the same
blame model. If typed code calls untyped code, the contract system inserts
runtime checks at the boundary, and violations blame the untyped module.

**What Racket contributes:** The insight that explanation is not just about the
*current line of code* — it's about **who is responsible for the mistake.**
Blame assignment turns a type error from "something doesn't match" into "you
passed wrong data" or "the function you called is broken." This is a
**relational diagnostic model** rather than a declarative one.

---

### 1.5 Swift — Fix-Its and IDE-First Diagnostics

Swift's diagnostic architecture is designed for **IDE integration**, not for
terminal output. The diagnostic engine produces `Diagnostic` objects with
attached `FixIt` objects — structured, machine-applicable corrections.

**Fix-Its as first-class diagnostics:**
```swift
let x = 5
x += 1  // error: 'let' constant cannot be mutated
        // fix-it: change 'let' to 'var'
```

The FixIt is not just a string suggestion — it is a **source edit** (start
position, end position, replacement text) that the IDE can apply with one
click. Xcode's "Fix" button executes the FixIt directly. This is the
strongest form of machine-applicable suggestion in any language surveyed.

**Diagnostic architecture in the compiler:**
- `DiagnosticEngine` collects diagnostics from all compiler passes
- Each diagnostic has a `DiagnosticKind` (error, warning, note, remark)
- Diagnostics carry source ranges, not just points
- `DiagnosticConsumer` is a protocol — text output and Xcode output are
  separate consumers of the same diagnostic structure
- Result builder diagnostics (`ViewBuilder`, `SceneBuilder`) are emitted by the
  type checker when it detects structural issues in DSL code

**What Swift contributes:** The insight that diagnostics should be **consumable
by tools, not just by humans.** A FixIt is a structured operation (replace
range X with text Y), and that structure survives from the compiler through the
LSP to the IDE. Nomi should consider whether its explanation normal form should
include machine-applicable suggestions, not just human-readable text.

---

### 1.6 Scala 3 — The `-explain` Architecture

Scala 3's diagnostic system is built around a **separation of detection and
explanation.** The compiler detects errors and assigns them error codes; the
`-explain` flag enables detailed, prose explanations that are stored separately
from the detection logic.

**Error message format without `-explain`:**
```
-- [E007] Type Mismatch Error: src/main.scala:5:10
5 |  val x: Int = "hello"
  |           ^^^^^^^^^^^
  |           Found: ("hello": String)
  |           Required: Int
```

**With `-explain`:**
```
-- [E007] Type Mismatch Error: src/main.scala:5:10
...
Explanation:
  The assigned value does not match the declared type.
  ...
```

**The `-explain` infrastructure:**
- Error messages are defined in a central `messages` file with error IDs
- Each error ID has a short template (for the inline message) and optionally
  a long explanation (for `-explain`)
- Explanations live in the compiler source, not in external docs
- The same error IDs are used across compiler phases (typer, implicit search,
  pattern matching)

**Implicit resolution diagnostics** are Scala 3's most distinctive feature.
When implicit search fails, `-explain` walks the programmer through *why* each
candidate was rejected:
```
-- [E172] Implicit not found Error: ...
Implicit not found for type Encoder[User]
  The following implicits were tried:
    - encoderDerived: failed because no instance of Mirror.Of[User]
    - encoderJson: failed because User is not a subtype of Json
```

**What Scala 3 contributes:** The **expand-on-demand** model. The compact
message is what you see inline; the detailed explanation is what you get when
you ask for more. This avoids overwhelming beginners with detail while giving
experts deep context when needed. It also separates the *detection* code from
the *explanation* prose, making both easier to maintain.

---

### 1.7 Python — Rapidly Improving with Structural Constraints

Python 3.11+ represents a dramatic improvement in diagnostic quality, achieved
within the constraints of a runtime-centric language with no type checker in
the interpreter itself.

**3.11 SyntaxError improvements:**
```
>>> x = {"a": 1, "b": 2, "a": 3}
  File "<stdin>", line 1
    x = {"a": 1, "b": 2, "a": 3}
          ^^^^^^^^^^^^^^^^^^^^
SyntaxError: duplicate key 'a' in dictionary
```
The caret range now spans the entire duplicate entry, not just one character.
The interpreter is able to do this because parsing preserves full source
positions.

**"Did you mean?" for NameError:**
```
>>> import mattplotlib
ModuleNotFoundError: No module named 'mattplotlib'. Did you mean: 'matplotlib'?
```
This is powered by `difflib.get_close_matches` in the standard library —
a general-purpose suggestion mechanism that works for any name lookup failure.

**mypy/Pyright diagnostic style:** External type checkers produce their own
diagnostic format. Pyright uses a JSON diagnostic output for IDE integration,
and its error messages include type information that the runtime interpreter
lacks:
```
error: Argument of type "str" cannot be assigned to parameter "x" of type "int"
  "str" is incompatible with "int" (reportArgumentType)
```

**What Python contributes:** The lesson that diagnostics can improve
**incrementally** even in an existing language, without rebuilding the
interpreter architecture. Python 3.11 didn't add a diagnostic framework — it
improved span recording and added a suggestion heuristic. But the limitation is
clear: without a unified diagnostic architecture, each improvement is a
one-off, and external tools (mypy, Pyright) duplicate the work of producing
good diagnostics with no shared infrastructure.

---

### 1.8 Clojure — Spec Explain and Runtime Data Explanation

Clojure's `clojure.spec` is a runtime specification and explanation system that
is **completely decoupled from the compiler.** It represents a fundamentally
different architectural choice: explanation as a library, not as a language
feature.

**`clojure.spec/explain`:**
```clojure
(s/def ::name string?)
(s/def ::age pos-int?)
(s/def ::person (s/keys :req [::name ::age]))

(s/explain ::person {:name "Alice"})
;; In: [:age] val: nil fails spec: :user/age
;;   at: [:age] predicate: pos-int?
;;   :user/person fails spec: :user/person
;;     at: [:name] predicate: string?
```

The key architectural features:

*Path-based navigation.* `:In [:age]` tells you where in the data structure
the failure occurred. This composes: nested map failures produce nested paths.

*Predicate reporting.* The explain output names the failing predicate
(`pos-int?`), giving the programmer a concrete function to inspect.

*Machine-readable explain-data.* `clojure.spec/explain-data` returns a Clojure
data structure instead of a string. This enables programmatic consumption,
test frameworks to report spec failures, and tooling to render explanations
differently.

*Generative testing with shrunk examples.* `clojure.spec/test` generates random
data, finds counterexamples, and **shrinks** them to minimal failing cases.
The shrunk example is the explanation: "here is the simplest input that breaks
your specification."

**What Clojure contributes:** The insight that explanation can be a
**language-level library** rather than a compiler feature. If your language can
represent data well, your explanation system can be data structures that are
rendered for humans but consumable by programs. This is the most lightweight
architectural approach — but it requires the language to have good data
literals and a culture of library-driven design.

---

### 1.9 Haskell — GHC's Diagnostic Depth

GHC's diagnostics are **comprehensive but uneven** — capable of extraordinary
detail for type errors and hopelessly opaque for certain error kinds. The
architecture is worth studying because it reveals what happens when diagnostic
infrastructure is built around a deeply sophisticated compiler IR.

**Type error formatting:** GHC 9.2+ improved type error formatting
significantly. Mismatched types are shown with the expected and actual types
aligned, and GHC sometimes offers suggestions (e.g., "add a type annotation"
or "try enabling FlexibleContexts").

**`-fdefer-type-errors`:** Type errors become runtime warnings, and the program
runs until the erroneous code is reached. The runtime error message then
includes the full source location and the type error text. This is a unique
"defer and run" strategy that no other statically typed language offers.

**`-ddump-simpl` and intermediate representations:** GHC can dump its Core
(desugared Haskell), STG (spineless tagless G-machine), and Cmm (C--) IRs.
These are not "diagnostics" in the user-facing sense, but they are **program
explanation** in the deep sense: the compiler can show the programmer exactly
how the program was transformed. This is a debug-level explanation facility
built into the compiler architecture.

**GHCi `:info` and `:type`:** Interactive explanation is a distinct diagnostic
mode. `:info` shows a value's type, class instances, and fixity. `:type`
shows the inferred type of an expression without evaluating it. These are
**incremental explanation tools** that the programmer uses during development,
not when an error occurs.

**Liquid Haskell error traces:** Liquid Haskell (a refinement type system on
top of GHC) produces error traces that show the constraint solving path —
which refinement was violated, which subtyping constraint failed, and which
path condition led to the violation. This multi-step reasoning trace is a
model for how Nomi's constraint system might explain itself.

**What Haskell contributes:** The diagnostic tool is also a **program
explanation tool.** `:info`, `:type`, and `-ddump-simpl` are not error messages
— they are ways the compiler explains the *program* to the programmer, not just
the *error.*

---

### 1.10 Zig — Compile-Time Error Traces

Zig's diagnostic architecture is unique because it collapses compile-time and
runtime: `comptime` code can produce errors, and those errors carry source
locations from the compile-time execution trace.

**`@compileError`:** When a compile-time check fails, `@compileError` emits an
error that is not a runtime panic — it is a **compile-time error** emitted by
compile-time code execution. The error message carries the source location of
the `@compileError` call.

**Error return traces:**
```
error: FileNotFound
  src/main.zig:10:25: 0x1000 in openConfig (main)
        const file = try std.fs.cwd().openFile(path, .{});
                        ^
  src/main.zig:5:30: 0x1001 in main (main)
        const config = try openConfig("config.txt");
                             ^
```
Each `try` that propagates the error records the return address. When the error
is finally caught, the trace shows every propagation point. This is like a
stack trace, but **only for error propagation points,** not for every function
call.

**"note:" chains:** Zig's compiler errors can emit `@compileError` with
context:
```
error: unable to evaluate constant expression
  note: called from here
  note: called from here
```
The "note:" chain walks backward through the comptime call stack.

**What Zig contributes:** Error traces that show the **propagation path,** not
just the origination point. A `FileNotFound` at the bottom of a call chain is
unhelpful without knowing which high-level operation tried to open the file.
Zig's error return traces solve this by recording the `try` chain.

---

## 2. Cross-Language Synthesis: What's Structurally the Same

Despite wildly different architectures, every effective diagnostic system
shares these invariants:

### Invariant 1: Source Location

Every system reports *where* the error is. The minimum is `file:line:col`.
Better systems include a span (range). The best include multiple spans with
labeled relationships.

| Language | Minimum location | Span support | Multi-span |
|----------|-----------------|--------------|------------|
| Rust     | file:line:col   | Yes (range)  | Yes (labeled sub-spans) |
| Elm      | line:col        | Yes (range)  | Rarely needed |
| Gleam    | file:line:col   | Yes (range)  | Yes |
| Racket   | module:line:col | Context only | Via contract boundary |
| Swift    | file:line:col   | Yes (SourceRange) | Via FixIt attachments |
| Scala 3  | file:line:col   | Yes (caret line) | No |
| Python   | file:line       | Yes (3.11+) | No |
| Clojure  | Variable         | Data path | Via spec paths |
| Haskell  | module:line:col | Yes | Via type error spans |
| Zig      | file:line:col   | Yes | Via note: chains |

**Lesson for Nomi:** Source spans must be preserved through every pipeline
stage — parsing, lowering, desugaring, interpretation. A desugar pass that
drops source location destroys downstream diagnostic quality. The span is the
**universal key** that all diagnostics join on.

### Invariant 2: Error Categorization

Every system classifies errors: syntax error vs type error vs runtime error vs
warning. The categories differ, but the *act of categorizing* is universal.
Categorization enables:
- Filtering (show me only type errors)
- Prioritization (syntax errors block type checking)
- Tooling (LSP diagnostic severity levels)
- User expectation ("this is a warning, I can ignore it for now")

### Invariant 3: Contextual Code Display

Showing the offending line of code is not universal (Clojure's spec explain
shows data, not code) but it is overwhelmingly common. The best systems show:
- The line of code with the error
- A visual indicator (caret, underline, highlight) pointing to the error
- Surrounding lines for context

### Invariant 4: Some Form of Causality

Every diagnostic explains *why* something is wrong, not just *what* is wrong.
The minimum is "expected X, got Y." Better systems chain causality: "X is
required here because Y was inferred at Z." The best systems attribute
responsibility: "your code broke the contract" vs "the library's code broke the
contract."

### Invariant 5: Some Form of Remediation

Every system that is considered "good" at diagnostics provides a path to fix
the error. This ranges from:
- Minimal: "expected Int, got String" (the fix is implicit: change the value)
- Helpful: "consider adding a type annotation"
- Specific: "did you mean `matplotlib`?"
- Machine-applicable: Swift's FixIt, `rustc --fix`, ESLint `--fix`

**The pattern:** the more specific the remediation, the more structural
information the diagnostic system needs. Remediation quality is bounded by the
**structural information the diagnostic pipeline preserves.**

---

## 3. Cross-Language Synthesis: What's Genuinely Different

These are real design choices, not implementation details:

### Choice 1: Span Granularity — Point vs Range vs Multi-Span

**Single point** (line:col): Python before 3.11, most older compilers.
Advantage: simple. Cost: can only point to one character, ambiguous in complex
expressions.

**Range** (start:end): Rust, Swift, Scala 3. Advantage: shows the whole
expression, not just one character. Cost: requires every AST node to carry a
range during compilation.

**Multi-span** (primary + secondary spans): Rust's borrow checker. Advantage:
shows relationships between code locations. Cost: requires the diagnostic pass
to identify and label related locations.

**Data path** (key → nested key): Clojure spec. Advantage: explains failures
in terms the programmer thinks about (data structure navigation). Cost: only
useful for data validation, not for syntax or type errors.

### Choice 2: Message Composition — Single Message vs Chained "Because"

**Single message:** "Type mismatch: expected Int, got String." The entire
explanation is in one text block.

**Chained "because":** "Expected Int, got String. The String came from
`user.name` which has type String. `user.name` is used here because `getName`
returns `User`. `getName` is called at line 42." Each link explains *how* the
error information propagated to the error site.

**Design question for Nomi:** Should Nomi's explanation normal form be a
**tree** (error → immediate cause → upstream cause → root cause) or a **flat
message** with optional notes?

### Choice 3: Fix Suggestions — Human-Readable vs Machine-Applicable

**Human-readable only:** "Did you mean `matplotlib`?" The programmer reads it
and makes the change.

**Machine-applicable:** Swift's FixIt, `rustc --fix`, ESLint `--fix`. The
suggestion carries a source edit (range + replacement text).

**Hybrid:** Rust's `rustc --explain` is human-readable but machine-addressable
(via the error code).

### Choice 4: Library Participation — Can Library Code Produce Structured Diagnostics?

**No library participation:** Elm, Gleam. The compiler produces all diagnostics.

**Error trait / interface:** Rust (`std::error::Error`), Python (exception
hierarchy). Libraries define error types that carry structured information.

**Library diagnostics framework:** Racket's contracts. Library code declares
contracts, and the runtime produces contract violation diagnostics automatically.

**Runtime explanation library:** Clojure's spec. Libraries define specs, and
the `clojure.spec/explain` function produces diagnostics.

**Design question for Nomi:** Nomi's explanation normal form should enable
library code to participate. A library should be able to say "here is a
constraint, and here is what to say when it fails."

### Choice 5: Error Codes — Machine-Lookup vs Human-Memorizable vs None

**Stable, machine-lookup error codes:** Rust (`E0382`), Scala 3 (`E007`).

**Human-memorizable categories:** Python (`TypeError`, `NameError`).

**No error codes:** Elm, Gleam (mostly).

---

## 4. Key Tensions When Synthesizing

### Tension 1: Compiler as Teacher vs Compiler as Tool

**Teacher philosophy** (Elm, Rust): The compiler should explain the *language
concept* behind the error. A borrow error is an opportunity to teach ownership.

**Tool philosophy** (Zig, Clojure): The compiler should state the *fact* of the
error and let the programmer investigate.

**The tension:** Teacher-mode diagnostics are verbose and can feel patronizing
to experts. Tool-mode diagnostics are terse and can be inscrutable to beginners.
Rust's `--explain` is a compromise (terse inline, verbose on demand).

### Tension 2: Structured vs Narrative Diagnostics

**Structured** (Rust, Swift LSP): The diagnostic is a data structure with typed
fields. The human-readable text is one rendering.

**Narrative** (Elm, early Python): The diagnostic is prose. It reads like a
human wrote it. The structure is implicit in the text formatting.

**Can you have both?** Rust comes closest: the structured `Diagnostic` has a
`message` field that is prose, but the spans, labels, and suggestions are
structured. The prose is embedded in the structure, not the other way around.

### Tension 3: Compiler-Centric vs Runtime-Centric Explanation

**Compiler-centric** (Rust, Elm, Gleam, Zig, Haskell): Diagnostics are produced
at compile time. Full type information, full source spans, full control.

**Runtime-centric** (Clojure, Racket, Python): Diagnostics are produced at
runtime. Can include actual runtime values in error messages.

**The synthesis challenge:** Nomi should bridge both. Compile-time constraints
should produce diagnostics at parse/analysis time. Runtime constraints should
produce diagnostics with the actual failing value. The explanation normal form
must work for both phases.

### Tension 4: Explanation Depth — Surface vs Deep Causality

**Surface:** "Type mismatch: expected Int, got String."

**Deep:** "Type mismatch: expected Int, got String. The String came from field
`name` of type `User`, which was returned by `getUser()` called at line 15..."

**The tension:** Deep diagnostics require the system to *record* the causal
chain. Each recording mechanism is a separate infrastructure investment.

---

## 5. What Breaks When Combining Approaches

### Failure Mode 1: Elm's Suggestions Without Elm's Solver

Elm's "I think you meant..." suggestions depend on the constraint solver
exploring near-miss types. Without a constraint-based type inference engine,
Nomi cannot produce this style of suggestion.

**Mitigation:** Nomi can do simpler suggestion heuristics (edit distance on
names, known imports, similar function signatures) that don't require a full
solver. Python 3.11 demonstrates this — `difflib`-based "did you mean?" works
without a type checker.

### Failure Mode 2: Rust's Multi-Span Diagnostics Without Rust's Compiler IR

Rust's multi-span borrow errors depend on MIR (mid-level IR) that tracks the
lifetime of every value. A language without this IR cannot identify and label
related source locations for borrow-like errors.

**Mitigation:** Nomi doesn't need to replicate Rust's borrow checker. But if
Nomi adds constraints that span multiple source locations, it needs a mechanism
to track constraint origins across pipeline stages.

### Failure Mode 3: Racket's Blame Without Contract Boundaries

Racket's blame assignment works because contracts are explicitly declared at
module boundaries (via `provide/contract`). If Nomi's constraints are implicit
or inferred, there is no boundary to blame.

**Mitigation:** Nomi's binding constraints are declared inline
(`name: constraint = value`). The declaration point IS the boundary. Blame
assignment can work at the granularity of individual constraint declarations.

### Failure Mode 4: Clojure's Spec Explain Without Runtime Data Literals

`clojure.spec/explain` returns a Clojure data structure. This works because
Clojure has first-class data literals and a culture of treating data as the
universal interface.

**Mitigation:** Nomi's explanation normal form should be a typed data
structure with a JSON representation, not just a string. This preserves the
"explanation as data" property without requiring the entire language to be
data-literal-oriented.

### Failure Mode 5: Zig's Error Return Traces Without Explicit Error Propagation

Zig's error return traces work because every error propagation point is visible
(`try` keyword) and the compiler can instrument each one. In a language with
implicit exception propagation, the propagation path is not visible in source.

**Mitigation:** Nomi has not yet chosen between explicit error propagation
(Rust/Zig-style) and implicit (Python exception-style). The choice affects
diagnostic architecture: explicit propagation enables return traces; implicit
propagation requires different tracing infrastructure.

---

## 6. Synthesis for Nomi

### 6.1 What Infrastructure Must Exist Before Diagnostics Can Be Good

The cross-language analysis reveals a **minimum viable diagnostic
infrastructure** that must exist before message text matters:

1. **Source spans that survive the pipeline.** Every node in the AST, surface
   AST, and lowered Python AST must carry its original source span. Desugar
   passes must propagate or compose spans.

2. **A diagnostic collector, not printf.** Compiler passes, type checkers, and
   runtime checks should emit into a `DiagnosticCollector` that assembles
   structured diagnostics. No pass should print directly to stderr.

3. **Error categorization (at minimum level/code).** Every diagnostic must have
   a level (error, warning, note, help) and ideally a stable code.

4. **A constraint recording mechanism.** When a constraint is checked (at
   compile time or runtime), the system must record: what constraint, what
   value, what location, what binding.

5. **Multiple rendering modes.** The diagnostic structure must be renderable as
   terminal text, LSP JSON, and human-readable prose. The structure is the
   source of truth; the renderings are views.

### 6.2 Diagnostic Vocabulary Nomi Should Use Consistently

Based on the languages surveyed, a consistent vocabulary helps users parse
diagnostics quickly:

| Token | Meaning | Used by |
|-------|---------|---------|
| `error:` | The primary problem | All languages |
| `warning:` | Something suspicious but not blocking | All languages |
| `note:` | Additional context, not the error itself | Rust, Zig, Haskell |
| `help:` | A concrete suggestion for fixing | Rust |
| `because:` | Causal chain link | Nomi convention |
| `in:` | Location context | Racket, Scala 3 |
| `from:` | Origin of a value/type | Racket, Rust |
| `expected:` | What should have been | Most languages |
| `found:` / `got:` | What was actually there | Most languages |
| `hint:` | Non-actionable suggestion | Gleam |

**Nomi's vocabulary:** Nomi should adopt `error:` / `warning:` / `note:` /
`help:` from Rust's taxonomy, and add `because:` for causal chaining. The
`because:` tag is Nomi-specific — it signals that the following text explains
*why* the error occurred, not just *what* the error is.

### 6.3 How Nomi's Diagnostics Should Compose

The composition model is the hardest design problem. Nomi's diagnostics will
come from multiple sources: the parser, the type checker, the constraint
system, the runtime, and (eventually) libraries.

**The composition chain should be:**

```
Binding error → constraint failure → field path → source span
```

Example: a type mismatch in a nested record field accessed through a function
return:

```
error: type mismatch for `user.profile.name`
  expected: String
  found: Int
  because: `get_user()` at line 30 returns `User`, whose `profile` field
           contains `name: Int` at definition line 12
  because: constraint `@has_field(profile.name, String)` was checked at line 30
  help: ensure `User.name` is defined as `String`, or convert the Int to String
        before use
```

### 6.4 Compiler-as-Teacher vs Runtime-Explanation Traditions

Nomi should learn from both traditions:

**From the compiler-as-teacher tradition** (Elm, Rust, Scala 3):
- Diagnostics should explain the *language concept* behind the error
- The `--explain` flag pattern: terse inline, verbose on demand
- Error codes as stable references for documentation and tooling

**From the runtime-explanation tradition** (Clojure, Racket, Python):
- Diagnostics should include *actual values* from the runtime
- The explanation should navigate the *data structure* that failed
- Machine-readable explanation data enables testing and tooling

**Where Nomi should go further:**
- Diagnostic composition across pipeline stages: a parse error in a lowered
  construct should reference the original syntax, the lowering rule, and the
  intermediate representation
- Constraint explanation as a first-class mode
- Tools should be able to *query* the explanation system interactively

### 6.5 The Explanation Normal Form (Draft)

Based on the cross-language analysis, Nomi's explanation normal form should
have these fields:

| Field | Type | Purpose | Source of inspiration |
|-------|------|---------|----------------------|
| `level` | enum(error, warning, note, help) | Severity | Rust, Swift |
| `code` | string (optional) | Stable identifier | Rust, Scala 3 |
| `message` | string | Primary explanation text | All |
| `spans` | list of {location, label} | Where in source | Rust |
| `because` | list of Explanation | Causal chain | Nomi convention |
| `suggestion` | optional {text, edit?} | Remediation | Swift, Rust |
| `data_path` | optional list of keys | Where in data structure | Clojure spec |
| `value` | optional any | The actual runtime value | Clojure, Racket |

This is a **typed data structure** (not a string) that can be rendered as
terminal text, LSP JSON, or interactive notebook output. The `because` field
is the key Nomi addition — it enables composing explanations from multiple
sources into a single causal narrative.

---

## 7. Cross-Language Comparison Table

| Language | Diagnostic Architecture | Span Strategy | Suggestion Style | Library Participation | Distinctive Strength | Transferable to Nomi? |
|----------|------------------------|---------------|------------------|----------------------|---------------------|----------------------|
| **Rust** | Structured DiagnosticBuilder, all passes emit into framework | Multi-span with labeled sub-spans | Machine-applicable via `--fix`, human via `--explain` | `std::error::Error` trait, `anyhow` context chaining | Error codes as stable identifiers; multi-span borrow diagnostics | DiagnosticBuilder pattern, error codes, `--explain` flag |
| **Elm** | Constraint solver produces near-miss suggestions | Single range | Prose "I think you meant..." heuristic | None — all diagnostics are compiler-internal | Beginner-first pedagogy; suggestions based on solver exploration | Suggestion heuristics (adapted for Nomi's constraint system) |
| **Gleam** | Compiler-internal Diagnostic struct with hints | Single range with caret | Deterministic "Did you mean?" via edit distance | None — early stage | Friendly without full solver; exhaustiveness checking | Deterministic suggestion generation |
| **Racket** | Contract system at module boundaries, runtime blame | Module:line:col + contract boundary | Implicit — the contract IS the suggestion | Contracts declared via `provide/contract` | Blame assignment (positive/negative); distributed accountability | Blame model for constraint violations |
| **Swift** | DiagnosticEngine + FixIt objects; IDE-first | SourceRange | Machine-applicable FixIt (source edit) | Error protocol + `#error`/`#warning` directives | FixIt as structured source edit consumable by IDE | FixIt pattern for Nomi's VS Code extension |
| **Scala 3** | Central error messages file, `-explain` flag | Caret line | Detailed prose on demand via `-explain` | None systematic | Expand-on-demand; implicit search failure walkthrough | `--explain` pattern; separation of detection and explanation |
| **Python** | Improved interpreter internals (3.11+), external type checkers | Caret range (3.11+) | "Did you mean?" via `difflib` for NameError | Exception hierarchy, `__cause__` chaining | Incremental improvement without architecture rewrite | `difflib`-style suggestion for names |
| **Clojure** | `clojure.spec` — explanation as library, not compiler | Data path (navigates structure) | Generative testing with shrunk counterexamples | Specs are library code; `explain-data` is machine-readable | Explanation as data structure; generative testing integration | "Explanation as data" principle |
| **Haskell** | GHC diagnostic rendering, defer-to-runtime option, dump flags | Range | Occasional prose suggestions | None systematic beyond `error`/`undefined` | `-fdefer-type-errors`; GHCi `:info`/`:type` as interactive explanation | Interactive explanation mode; deferred checking |
| **Zig** | Compile-time error traces via `comptime`; error return traces | Point + note: chain | `note:` chains walk the call stack | `@compileError` in library code | Error return traces (propagation path, not just origin) | Error return traces; `note:` chain composition |

---

## 8. Concrete Recommendations for Nomi

1. **Build the diagnostic collector first.** Before writing a single error
   message, create a `DiagnosticCollector` that every pipeline stage emits
   into. This is Rust's model and it pays off immediately.

2. **Preserve source spans through every transformation.** Desugar passes
   must propagate source spans. If a lowered construct replaces `a?.b` with
   an `if`-`else` tree, the `if` node should carry the span of the original
   `a?.b`.

3. **Use `--explain` from day one.** Separate detection from explanation.
   The inline message is what the compiler knows for certain; the `--explain`
   message is the pedagogical context. This is Scala 3's model.

4. **Adopt the `because:` chain for composability.** When a constraint fails
   because a binding failed because a function returned a bad value, the
   explanation should compose those causes.

5. **Design for structured data, render for humans.** The explanation normal
   form is a typed structure with JSON representation. Never store explanation
   as a string internally.

6. **Enable library participation with explain decorators.** Libraries should
   be able to attach explanation metadata to their functions and types.

7. **Start with deterministic suggestions, grow into heuristic ones.** Gleam's
   edit-distance-based "Did you mean?" is simple and effective. Start there.

8. **Reserve error codes even if they are not stable yet.** The code namespace
   is cheap to allocate and expensive to retrofit.

---

## 9. References

- Rust Compiler Development Guide, "Diagnostics" chapter
- Elm Compiler source, `Error` module (particularly type-diff and suggestion generation)
- Gleam Compiler, `diagnostics` module
- Racket Guide, "Contracts" chapter; "Typed Racket Guide"
- Swift Compiler, `include/swift/AST/DiagnosticEngine.h`
- Scala 3 Compiler, `compiler/src/dotty/tools/dotc/reporting/messages.scala`
- Python 3.11 release notes, "Improved Error Messages" section
- `clojure.spec` Guide, "Explain" section
- GHC User Guide, "Debugging the Compiler" chapter
- Zig Language Reference, "Errors" and "Compile Variables" sections
