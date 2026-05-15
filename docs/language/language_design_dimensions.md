# Language Design Dimensions

> Status: active design framework.  This document analyses the irreducible
> dimensions along which programming languages systematically vary — not at
> the syntax level, but at the semantic and cognitive level.
>
> Companion: [language_degrees_of_freedom.md](language_degrees_of_freedom.md)
> for Nomi's policy on each dimension.  This document analyses the
> dimensions themselves.

## Purpose

Programming languages look very different at the surface.  `for` loops,
`match` expressions, `|>` pipelines, `do` notation, `async`/`await`,
`defer`, `?.` — the lexical variety is enormous.

But one level up from syntax, the concepts they encode vary much less.
Two levels up, they converge almost completely.  At some level of
abstraction, every language feature reduces to one of a small set of
irreducible primitives.

This document:

1. Names the **axes** along which languages systematically vary.
2. Shows **convergence points** where different syntax encodes the same
   semantic operation.
3. Maps the **hierarchy** from surface syntax down to universal
   computation primitives.
4. Places Nomi in this design space.

The goal is not a taxonomy for its own sake.  The goal is to make
Nomi's design decisions *visible as choices in a known space*, so that
each decision can be evaluated against the alternatives rather than
made in isolation.

## 1. The Convergence Thesis

```
Surface syntax   →  infinite variation (every language is different)
Idioms/patterns  →  families of related forms (ML-family, C-family, Lisp-family)
Semantic models  →  ~15-20 distinct mechanisms (pattern matching, type classes, etc.)
Core primitives  →  ~6-8 irreducible operations
Computation      →  1 (λ-calculus, Turing machine, SKI — all equivalent)
```

Peter Landin's 1966 paper "The Next 700 Programming Languages" made this
argument: most languages are surface variations over a lambda-calculus core
with some "syntactic sugar" for common patterns.  The corollary for language
design: **don't add a new primitive when a known primitive already covers
the semantics, expressed through different sugar.**

The designer's job is to identify the right level to work at.  Too close to
syntax and you build a feature collage.  Too close to computation and you
build an unadorned lambda calculus that nobody wants to use.  The sweet spot
is designing at the **core primitives** level with deliberate, inspectable
surface sugar.

## 2. The Hierarchical View

### Level 5 — Computation Itself (Universal)

All languages converge here.  The λ-calculus, Turing machines, partial
recursive functions, register machines, cellular automata, and the SKI
combinator calculus are all computationally equivalent.  This is the
Church-Turing thesis: anything computable by one model is computable by
all.

For language design, this level is too low to be useful.  Nobody wants
to write programs directly in the λ-calculus.  But it is the guarantee
that any feature can be *expressed* — the question is only how clearly.

### Level 4 — Core Primitives (~6-8 operations)

These are the irreducible semantic operations from which all language
features are built.  They appear in every language, though sometimes
implicitly or in restricted form.

| Primitive | What it does | Appears as |
|-----------|-------------|------------|
| **Bind** | Associate a name with a value in a scope | `let`, `const`, `var`, `=`, `:=`, `def`, `val`, parameters, pattern captures, imports |
| **Abstract** | Parameterise code over values or types | `fn`, `λ`, `func`, `def`, `proc`, `sub`, generics, templates, functors |
| **Apply** | Use an abstraction with concrete arguments | function call `f(x)`, method dispatch `obj.m()`, type application `Vec<Int>` |
| **Choose** | Select a computation path based on a condition | `if`/`else`, `match`/`case`, `switch`, `cond`, `? :` , pattern matching |
| **Compose** | Combine smaller things into larger things | sequencing `;`, piping `|>`, composition `.`/`>>>`, concatenation `++` |
| **Contain** | Delimit a region with its own names and rules | blocks `{ }`, indented suites, `let..in`, `where`, modules, closures, objects |
| **Signal** | Communicate information outside normal return | exceptions, `Result`, `Option`, `?`, effects, callbacks, `yield`, continuations |
| **Explain** | Make program behaviour inspectable | types, assertions, contracts, traces, examples, debuggers, error messages |

A language may omit one of these (e.g., a pure functional language omits
exceptions from Signal), but it cannot omit all forms of it (pure
languages use `Result` / `Option` instead).  A language may combine
primitives (objects are Contain + Bind + Apply).  A language may provide
multiple forms of the same primitive (exceptions AND `Result`).

The design rule: **every language feature should be analysable as a
combination of these primitives**.  If a feature requires a genuinely
new primitive, that is a significant language-design event.

These eight primitives are the foundation for Nomi's eight normal forms (see
[convenience README](../convenience/README.md)). Each normal form is a Nomi-specific
packaging of one or two primitives into a user-visible pattern:

| Primitive | Nomi normal form | How Nomi packages it |
|-----------|-----------------|---------------------|
| Bind | Binding | names + constraints + commit or diagnose |
| Abstract + Apply | Function | parameters as bindings, body evaluates, result may be checked |
| Choose + Contain + Bind | Pattern | structural test + captures + constraints + body selection |
| Compose + Apply | Flow | value through calls, pipelines, collection transforms |
| Contain + Signal | Block | call + attached caller-side code invoked by `yield` |
| Bind + Contain | Data boundary | explicit decode, field bindings, owned program values |
| Signal (value-encoded) | Absence/result | `none`, `?.`, `??`, `Result[T, E]` with pattern matching |
| Explain | Explanation | source-spanned events, traces, diagnostics, `explain` |

This mapping is the coherence check: every Nomi normal form should be traceable
to one or two core primitives. A normal form that requires three or more
primitives is probably two normal forms in a trench coat.

### Level 3 — Semantic Mechanisms (~15-20)

These are the concrete mechanisms that languages build from the core
primitives.  This is where languages start to look different from each
other, but the variation is systematic and analysable.

| Mechanism | Built from | Languages |
|-----------|-----------|-----------|
| Pattern matching | Choose + Contain + Bind | ML, Rust, Swift, Haskell, Scala |
| Type classes / traits | Abstract + Apply (at type level) | Haskell, Rust, Scala 3, Swift |
| Exception handling | Signal (non-local) | Python, Java, Ruby, C++ |
| Result/Either monad | Signal (value-encoded) + Choose | Rust, Haskell, OCaml, Swift |
| Generators / coroutines | Signal (suspendable) + Apply | Python, JavaScript, Lua, Kotlin |
| Actors / processes | Contain + Signal (message) | Erlang, Elixir, Akka, Go (goroutines) |
| Lazy evaluation | Abstract (thunk) + Apply (force) | Haskell, Scala `lazy val`, R `promise` |
| Ownership / borrowing | Contain (lifetime) + Abstract (region) | Rust, Hylo, Vale, Mojo |
| Algebraic effects | Signal (user-defined) + Contain (handler) | Koka, Eff, OCaml 5, Unison |
| Macros | Apply (compile-time) + Abstract (syntax) | Lisp, Racket, Rust, Scala 3, Julia |
| Module systems | Contain + Bind + Abstract (module-level) | ML, Rust, JavaScript, Go, Haskell |
| Reactive / dataflow | Compose (stream) + Signal (change) | Elm, Rx, Svelte, Excel, LabVIEW |
| Unification / constraints | Apply (bidirectional) + Signal (failure) | Prolog, CUE, Nickel, type inference |
| Gradual typing | Contain (typed boundary) + Explain | TypeScript, Python (mypy), Typed Racket, Ruby (RBS) |
| Dependent types | Abstract (value → type) + Apply (type-level) | Idris, Agda, Coq, Lean, F* |

Each mechanism is a *composition* of core primitives with specific
constraints.  For example: pattern matching = Choose (select case) +
Contain (each case body is a scope) + Bind (captures are bound in that
scope).  A guard adds another Choose inside the pattern.

### Level 2 — Idioms and Families

Languages cluster into families that share common mechanisms:

| Family | Signature mechanisms | Languages |
|--------|---------------------|-----------|
| ML-family | Algebraic types, pattern matching, type inference, parametric polymorphism | SML, OCaml, Haskell, F#, Elm, Roc, Scala, Rust, Swift |
| C-family | Statement/expression split, braces, mutable variables, manual memory or GC | C, C++, Java, C#, JavaScript, Go, D |
| Lisp-family | S-expressions, macros, code-as-data, dynamic typing or gradual typing | Lisp, Scheme, Racket, Clojure, Common Lisp |
| Array-family | Implicit rank, broadcasting, whole-array operations, tacit composition | APL, J, K, Q, BQN, Uiua, MATLAB, Julia |
| Logic-family | Unification, backtracking, relations as primitives | Prolog, Datalog, Mercury, miniKanren, Flix |
| Actor-family | Isolated processes, message passing, supervisor trees | Erlang, Elixir, Akka, Pony |
| Concatenative-family | Stack-based composition, postfix, combinators | Forth, Factor, Joy, Kitten, Cat, PostScript |
| Spreadsheet-family | Reactive cells, spatial addressing, declarative constraints | Excel, Google Sheets, Airtable |
| Configuration-family | Constraints, unification, layering, hermetic evaluation | CUE, Nickel, Pkl, Dhall, Nix, Terraform |

Families share not just syntax but **cognitive models**: how a programmer
thinks about solving a problem.  An ML-family programmer thinks "what are
my types and how do I transform them?"  An array-family programmer thinks
"what operations apply to the whole structure at once?"  A logic-family
programmer thinks "what relations must hold?"

### Level 1 — Surface Syntax

This is what varies most and matters least for semantics.  `fn` vs `func`
vs `def` vs `fun` vs `λ` — all Abstract.  `|>` vs `.` vs `->>` vs `>>`
vs threading macros — all Compose.  `match` vs `case` vs `switch` vs
`cond` — all Choose.  A language that copies another language's keywords
without understanding its semantic mechanisms is a language that will
accumulate incoherent features.

The design rule from the convergence thesis: **choose syntax for
consistency at Level 2 (idiom family) and semantics at Level 3 (semantic
mechanisms), not for superficial similarity at Level 1.**

## 3. The Axes of Systematic Variation

These are the dimensions where languages make *different but equally valid*
choices.  Each axis is a spectrum, not a binary.

### 3.1 Evaluation Axis

**When and how expressions are reduced to values.**

```
Eager (strict) ←——————————————————————→ Lazy (non-strict)
    │                                           │
    │  Python, Java, C, Rust, Go, OCaml         Haskell, R (promises)
    │  Julia, Swift, C#, JavaScript             Miranda, Clean
    │
    └── Call-by-value (evaluate argument before call)
    └── Call-by-reference (Fortran, C++ refs)
    └── Call-by-name (Algol 60, Haskell with ~)
    └── Call-by-need (Haskell, R — evaluate once, memoise)
```

**What varies:** When side effects happen, termination behaviour, space
usage predictability.

**Where it converges:** Call-by-need with no side effects = call-by-name.
Call-by-name with sharing = call-by-need.  Under purity, evaluation order
doesn't matter (Church-Rosser).  The difference only matters with effects.

**Nomi's position:** Eager, following Python.  Laziness should be opt-in
with a visible marker (future `lazy` keyword or `~` prefix), not the
default.  See [design_lessons_and_integration.md §1.4](../convenience/design_lessons_and_integration.md).

### 3.2 Type Discipline Axis

**When and how types are checked.**

```
Dynamic ←——————————————————————————————→ Static
   │                                           │
   │  Python, Ruby, JavaScript, Clojure         Haskell, Rust, OCaml, Scala
   │  Erlang, Elixir, Racket                    Swift, Kotlin, TypeScript
   │
   └── Gradual typing (TypeScript, Python/mypy, Typed Racket)
   └── Optional typing (Dart, Groovy)
   └── Soft typing (Scheme, early Racket research)
```

Sub-axes within static typing:

```
Nominal ←——————————————————————————————→ Structural
   │                                           │
   │  "named the same type"                    "has the same shape"
   │  Java, Rust, Haskell, Swift               TypeScript, Go interfaces, OCaml objects
   │  Kotlin, Scala nominal paths              C++ templates (effective structural)

Manifest ←——————————————————————————————→ Inferred
   │                                           │
   │  "write the types"                        "types are deduced"
   │  Java, C# (traditional)                   Haskell, OCaml, Rust (mostly inferred)
   │  C, C++ (partially)                       Scala, Swift (local inference)
```

**Where it converges:** Under the Curry-Howard correspondence, types ARE
propositions and programs ARE proofs.  A dynamic language is one that
checks the proof at runtime rather than compile time.  A gradually-typed
language checks part of the proof at compile time and part at runtime.

**Nomi's position:** Runtime-checked constraints for the first layer.
`name:Type, predicate = value` — the constraint is checked at binding
time.  Static checking is a future upgrade path that should not change
runtime semantics.

### 3.3 Memory/Ownership Axis

**Who is responsible for deallocating memory, and when.**

```
Manual ←———— GC ————→ Ownership/Borrowing ————→ Reference Counting
  │        │              │                          │
  │  C     Java, Go    Rust, Hylo              Swift (ARC), Python
  │  C++   Haskell     Vale, Mojo              Objective-C
  │  Zig   OCaml       Cyclone                 C++ shared_ptr
  │        Elixir
  │        JavaScript
```

Sub-axes:

```
Shared mutable ←————————————————————→ Immutable
   │                                         │
   │  Java, Python, Go, C++                  Haskell, Clojure, Erlang
   │  JavaScript, Ruby                       Elm, PureScript
   │
   └── Uniqueness (Rust: one mutable reference OR many immutable)
   └── Linear types (Rust, Linear Haskell: exactly one use)
   └── Affine types (Rust: at most one use)
   └── Relevant types (at least one use)
```

**Where it converges:** A garbage collector is an ownership system where
the runtime tracks all references.  The borrow checker is an ownership
system where the compiler tracks all references.  Reference counting is
an ownership system where values track their own references.  All three
prevent use-after-free; they differ in when the check happens and who
pays the cost.

**Nomi's position:** Python-hosted for the prototype, so GC semantics.
The permanent runtime should avoid the GIL constraint — see
[design_lessons_and_integration.md §7.7](../convenience/design_lessons_and_integration.md).

### 3.4 Effect Axis

**How side effects are represented and controlled.**

```
Implicit ←——————————————————————————————→ Explicit
   │                                           │
   │  Exceptions (Python, Java)                Result type (Rust, Haskell)
   │  Global state (C, Python)                 IO monad (Haskell)
   │  Ambient authority (most languages)       Algebraic effects (Koka, Eff, OCaml 5)
   │                                           Capabilities (Unison, Austral)
   │                                           Platform-passing (Roc)
```

Sub-axes:

```
Unchecked ←——————————————————————————————→ Checked
   │                                           │
   │  "any function can do I/O"                "the type tells you if there are effects"
   │  Python, JavaScript, Go, Ruby             Haskell (IO), Rust (traits), Roc (!)

Monadic ←——————————————————————————————→ Direct-style
   │                                           │
   │  Haskell do-notation, Scala for           Koka, Eff, OCaml 5 (effect handlers)
   │  F# computation expressions               Unison abilities
   │                                           Roc (platform passing)
```

**Where it converges:** A monad is an effect handler where the handler is
built into the language as `>>=` (bind).  An algebraic effect is a monad
where the handler is user-definable.  Platform-passing (Roc) is an effect
system where effects are records passed as explicit arguments.

**Nomi's position:** Block calls as the single effect primitive.  A
callee uses `yield` to invoke caller-side code.  This encodes resource
management (`using`), retry, transaction, tracing, and future effects
without a second function color.

### 3.5 Dispatch Axis

**How a function call resolves to a specific implementation.**

```
Single dispatch ←————————————————————→ Multiple dispatch
   │                                           │
   │  obj.method() — dispatch on obj           f(x, y) — dispatch on all args
   │  Python, Java, Ruby, C++, C#              Julia, Common Lisp (CLOS)
   │  Kotlin, Swift, JavaScript                Dylan, R (S4)
   │
   └── Pattern matching as dispatch:
   │    match value: case Pat1: ... case Pat2: ...
   │    Rust, Haskell, OCaml, Scala, Swift
   │
   └── Predicate dispatch:
   │    dispatch based on arbitrary runtime predicates
   │    Clojure multimethods, Haskell MultiParamTypeClasses + OverlappingInstances
   │
   └── Static dispatch (monomorphisation):
   │    compile to separate code per concrete type
   │    Rust generics, C++ templates, Zig comptime
   │
   └── Dynamic dispatch (vtable):
   │    resolve at runtime through a table of function pointers
   │    Java interfaces, Go interfaces, Haskell type classes (dictionary passing)
```

**Where it converges:** All dispatch is "given a set of possible
implementations, pick one based on some criteria."  Single dispatch:
pick based on the first argument's runtime type.  Multiple dispatch:
pick based on all arguments' runtime types.  Pattern matching: pick
based on the shape of one value.  Predicate dispatch: pick based on
arbitrary conditions.  Static dispatch: pick at compile time.  The
differences are in *what information* is used for the choice and *when*
the choice is made.

**Nomi's position:** Pattern matching as the primary dispatch mechanism
(`match`, if-let, guard-let, piecewise equations).  Single dispatch
through method calls for Python compatibility.  Multiple dispatch
deferred (library-first or future layer).

### 3.6 Binding and Mutability Axis

**How names are associated with values, and whether those associations
can change or be used multiple times.**

```
Immutable-by-default ←——————————————→ Mutable-by-default
   │                                           │
   │  Rust, Haskell, OCaml, Clojure            Python, Java, C, Go
   │  Scala (val/var), Kotlin (val/var)        JavaScript (let vs const added later)
   │  Swift (let/var), Elm                      Ruby
```

Substructural axis (how many times a value can be used):

```
Linear (exactly once) → Affine (at most once) → Relevant (at least once) → Unrestricted
        │                       │                       │
        │  Linear Haskell       Rust, Hylo              (no mainstream language
        │  Clean                                         enforces relevance only)
```

**Where it converges:** Immutable-by-default is unrestricted + compiler
enforcement (or cultural norm) against mutation.  Linear types restrict
to exactly one use — useful for manual memory management without GC.
Affine types (Rust) are linear types that allow dropping.

**Nomi's position:** One binding story.  `name = value` is the common
case.  `name:constraint = value` adds constraints.  Immutability is not
enforced at the binding keyword level but through constraints
(`name:(const)` could mean "do not rebind").  See
[design_lessons_and_integration.md §4.1](../convenience/design_lessons_and_integration.md).

### 3.7 Modularity Axis

**How code is grouped, encapsulated, and composed.**

```
Files-as-modules ←————————————→ First-class modules ——————→ Packages/crates
      │                                  │                        │
      │  Go, Python, JavaScript          OCaml, Racket            Rust, Haskell
      │  "one file = one module"         "modules are values"     "modules are versioned"
      │
      └── Internal (ML functors): parameterise module by module
      └── External (type classes): parameterise by named interface
      └── Mixin (Scala, Ruby): compose traits/modules into classes
```

**Where it converges:** A module is Contain + Bind at module level.  A
functor is Abstract + Apply at module level (function from module to
module).  A type class is Abstract + Apply where the module is implicitly
selected.  A package is a module with versioning.  All are ways to answer
"where does this name come from and who can see it?"

**Nomi's position:** Python-compatible imports for the first layer.  A
simple `module` keyword for namespacing.  No functors, no module types,
no first-class modules initially.  Keep module syntax stable from 1.0.

### 3.8 Concurrency Axis

**How multiple computations execute simultaneously.**

```
Shared memory ←——————————————————————————————→ Message passing
      │                                                │
      │  Java threads, C++ threads, Python GIL          Erlang actors, Go goroutines+channels
      │  Rust threads (safe via ownership)              Elixir processes, Akka
      │
      └── STM (Software Transactional Memory):
      │    Clojure refs, Haskell STM
      │
      └── Data parallelism:
      │    APL, Julia, NumPy — same operation on many elements
      │    Rust rayon, Haskell Accelerate
      │
      └── Structured concurrency:
           Kotlin coroutines, Swift async/await, Python Trio, Java Project Loom
```

**Where it converges:** A thread is an independent execution context.
A goroutine/process/actor is a lightweight thread with communication
discipline.  A transaction is "do all of these or none of these."
Concurrency primitives differ in: (1) granularity of isolation, (2)
mechanism of communication, (3) cost of spawning, (4) who handles
scheduling.

**Nomi's position:** Block calls as the concurrency primitive.  Future
concurrency models (structured concurrency, data parallelism) should
reduce to block policies, not new keywords.  Avoid function coloring.

### 3.9 Data Model Axis

**How compound data is constructed and accessed.**

```
Objects ←———— ADTs ————→ Prototypes ——————→ Relations
   │          │             │                   │
   │  Java    Haskell    JavaScript         Prolog, SQL
   │  Python  Rust       Lua, Self          Datalog
   │  Ruby    OCaml      Io                 CUE (constraint-based)
   │  C++     Scala
   │  C#      F#
   │
   └── Row types / extensible records:
   │    OCaml objects, PureScript rows, Elm records
   │    "a record with at least these fields"
   │
   └── Columnar / array-of-structs vs struct-of-arrays:
        APL, J, K, Julia, Polars, Arrow
```

Sub-axes:

```
Open ←——————————————————————————————————→ Closed
   │                                           │
   │  "more variants can be added later"       "all variants are known here"
   │  OCaml polymorphic variants               Haskell ADTs, Rust enums
   │  TypeScript union types                   Scala 3 enums

Extensible ←————————————————————————————→ Fixed
   │                                           │
   │  "more fields can be added"               "these are all the fields"
   │  PureScript rows, Elm records             Haskell records, Java classes
```

**Where it converges:** An object is a record of named values with
attached behaviour (methods).  An algebraic data type is a tagged union
of records.  A prototype is a record that delegates to another record.
A relation is a set of records with constraints.  All are Contain + Bind
with different rules for openness and extensibility.

**Nomi's position:** Nominal `data` for owned types, structural matching
for external values.  Keep nominal and structural distinct.  Mapping
patterns for record-like access over both.

## 4. Convergence Points

These are the places where seemingly different language features reduce
to the same underlying semantic operation.  Understanding these
convergences prevents adding redundant primitives.

### 4.1 The Elimination Form

`match`, `case`, `switch`, `cond`, `if`/`else`, `?.`, `??`, function
clauses, visitor pattern — all are **Choose** primitives.  They select
one of several continuations based on inspecting a value.

```
match value:              if condition:            value?.field
    case A: handlerA          thenBranch           // if value is None: None
    case B: handlerB      else: elseBranch         // else: value.field
    case _: default
```

All three are elimination forms.  The differences: `match` inspects
structure; `if` inspects a boolean; `?.` inspects for None.  Adding a
new keyword for each "kind of choice" duplicates the Choose primitive.

**Nomi's rule:** `match` for structural choice, `if` for boolean choice,
`?.` for absence short-circuit.  No additional choice syntax.

### 4.2 The Context Thread

Monads, effect handlers, implicit parameters, context receivers,
capabilities, dependency injection — all are ways to **thread implicit
context through computation.**

```
// Monadic: bind threads the context
do { x <- step1; step2 x }

// Effect handler: handle threads the context
try { step1(); step2() } with { effect op -> handler }

// Implicit parameter: compiler threads the context
def process()(using ctx: Context) = { step1(ctx); step2(ctx) }

// Block call: caller provides code; callee controls when it runs
retry(3): { send_request() }
```

All encode "there is context that the callee needs but shouldn't have to
explicitly thread through every intermediate function."  The differences:
where the context is declared (definition site vs call site), whether it
can be intercepted (effects can, implicit params cannot), and whether it
changes the function's type (monads do, block calls do not).

**Nomi's rule:** Block calls (`f(x) -> p: body`) are the context-threading
primitive.  They keep the caller's lexical scope, make the policy visible
at the call site, and avoid function coloring.

### 4.3 The Named Collection

Records, structs, objects, modules, dictionaries, namespaces, classes,
type classes, traits — all are **Contain + Bind**.  They group named
things together.

```
// Struct: names + types + layout
struct User { name: String, age: i32 }

// Object: names + behaviour + encapsulation
class User { constructor(name) { this.name = name } greet() { ... } }

// Module: names + visibility
module User { export func greet() { ... } }

// Dictionary: names + dynamic access
user = {"name": "Ada", "age": 30}
```

All are named collections.  The differences: static vs dynamic field
access, open vs closed field sets, value-level vs type-level grouping,
whether behaviour (methods) travels with the data.

**Nomi's rule:** `data` for nominal owned collections.  Dicts/maps for
dynamic collections.  Modules for code organisation.  Do not confuse
these — each has a distinct normal form.

### 4.4 The On-Demand Sequence

Generators, iterators, lazy lists, streams, coroutines, channels,
async sequences — all are **Signal (suspendable) + Compose (sequential)**.

```
// Python generator
def gen(): yield 1; yield 2; yield 3

// Haskell lazy list
[1..]  // infinite, computed on demand

// JavaScript async iterator
async function* gen() { yield 1; yield await fetch(); }

// Go channel
ch := make(chan int); go func() { ch <- 1; ch <- 2 }()
```

All produce a sequence of values where each value is produced on demand
rather than all at once.  The differences: whether production is
synchronous or asynchronous, whether the producer or consumer drives
iteration, whether the sequence can be infinite.

**Nomi's rule:** Generators via `yield` in functions.  Lazy sequences as
library values.  Block calls for consumer-driven iteration patterns
(`each(data) -> item: body`).

### 4.5 The State + Behaviour Bundle

Closures, objects, actors, processes, services — all bundle state with
behaviour and control access to the state.

```
// Closure: state captured from enclosing scope
func make_counter():
    count = 0
    return func(): count += 1; return count

// Object: state + methods
class Counter:
    count = 0
    func increment(): self.count += 1; return self.count

// Actor: state + message handler
actor Counter:
    count = 0
    receive increment: count += 1; reply count
```

All three provide "private state with a public interface."  The
differences: closures use lexical scope for privacy, objects use
explicit encapsulation, actors add asynchronous message passing.

**Nomi's rule:** Closures for simple state capture.  Data values for
structured state.  Block policies for resource state (open/close,
acquire/release).

### 4.6 The Boundary Crossing

Type annotations, contracts, assertions, schema validation, decode,
`instanceof`, `isinstance`, pattern guards — all are **Explain +
Choose**.  They check that a value meets some specification before
allowing it to proceed.

```
// Type annotation: compiler checks
fn process(x: i32) -> String { ... }

// Contract: runtime checks at module boundary
(provide (contract-out [process (-> i32? string?)]))

// Decode: explicit boundary check
let user = Data.decode(json, User.decoder)

// Guard: runtime pattern + predicate
case n if n > 0 => "positive"
```

All are "prove this property about this value."  The differences: compile
time vs runtime, static types vs dynamic predicates, automatic inference
vs explicit annotation, the vocabulary for expressing the property.

**Nomi's rule:** Constraints at binding boundaries for runtime checks.
`Data.decode` for external boundaries.  Pattern guards for structural
conditions.  Static checking as a future upgrade over the same constraint
vocabulary.

### 4.7 The (Co)Recursive Decomposition

Recursion, iteration, fold, map, for-comprehension, while loops,
fixed-point combinators — all are ways to **apply a computation
repeatedly until a condition is met.**

```
// Recursion
func factorial(n): if n <= 1: 1 else: n * factorial(n - 1)

// Iteration
for item in items: process(item)

// Fold
items.fold(initial, fn(acc, item): combine(acc, item))

// Fixed-point
fix(λf. λn. if n <= 1 then 1 else n * f(n-1))
```

All encode "do this until we're done."  The differences: structural
recursion (guaranteed to terminate) vs general recursion, eager vs
lazy accumulation, fold direction (left vs right).

**Nomi's rule:** `for` for iteration, recursion for structural
decomposition, library fold/map/filter for collection pipelines.
No special syntax for fixed points.

## 5. The Expression Problem — A Cardinal Dimension

The Expression Problem (Wadler, 1998) is not just a type-system puzzle.
It reveals a fundamental tradeoff that every language must navigate:
**data extensibility vs. operation extensibility.**

### The Problem

Given a set of data variants and a set of operations over them, you want
to add BOTH without modifying existing code and while preserving static
safety.  No language solves this perfectly — every language privileges
one dimension over the other.

### The Solution Space

| Approach | Add operations | Add variants | Static exhaustiveness | Languages |
|----------|---------------|-------------|----------------------|-----------|
| OOP classes | Hard (visitor pattern) | Easy (subclass) | No | Java, C#, Python |
| ADTs + pattern matching | Easy (new function) | Hard (modify all matches) | Yes | ML, Haskell, Rust |
| Multimethods | Easy | Easy | No | Clojure, CLOS |
| Type classes | Easy (new instance) | Easy (new data + instance) | No (open) | Haskell, Rust traits |
| Extension + given | Easy (extension) | Easy (new case + given) | No | Scala 3 |
| Polymorphic variants | Easy | Easy | No (open) | OCaml |
| Multiple dispatch | Easy | Easy | No | Julia |
| Protocols + extensions | Easy | Easy (conformance) | No | Swift |

### What This Reveals

The Expression Problem exposes a **cardinal dimension** of language
design: the tradeoff between **closed-world exhaustiveness** (ML
ADTs) and **open-world extensibility** (OOP classes, type classes,
polymorphic variants).

- If you close the set of variants, you get exhaustiveness checking
  but lose the ability to add variants without modifying the type.
- If you open the set of variants, you gain extensibility but lose
  the compiler's ability to say "you forgot a case."

This is not an implementation oversight.  It is a consequence of the
Curry-Howard correspondence: types are propositions, pattern matching
is proof by cases.  An open set of cases cannot have a completeness
proof.

**Nomi's position:** Nominal `data` for closed owned types (exhaustiveness
possible).  Structural matching for open external values (extensibility).
Keep these two distinct rather than trying to unify them into one
mechanism.  See [language_foundation.md §Data](language_foundation.md).

## 6. Single-Primitive Languages

Languages that commit to ONE primitive and build everything on it reveal
what is truly necessary vs what is convenient notation.

| Language | One primitive | Everything else is... |
|----------|--------------|----------------------|
| **Lisp** | S-expression + λ | Macros build control structures, objects (CLOS), pattern matching |
| **Smalltalk** | Object + message | `ifTrue:` is a message to a Boolean; `whileTrue:` is a block-valued message |
| **Haskell** | Pure function | I/O is a value (IO type); state is threaded (State monad); exceptions are values |
| **Forth** | Stack word | Variables are stack positions; control flow is compile-time stack manipulation |
| **APL** | Array operator | Scalars are 0-rank arrays; control flow is array selection |
| **Prolog** | Horn clause | Numbers are terms; I/O is side-effect predicates |
| **Tcl** | String | Lists are space-separated strings; code is a string passed to `eval` |
| **Erlang** | Process | State is a recursive process; I/O is process communication |
| **Lua** | Table | Objects are tables; modules are tables; arrays are tables with integer keys |
| **Excel** | Cell (reactive reference) | Computation is a dependency graph; control flow is IF() function |
| **λ-calculus** | λ + application | Numbers are Church numerals; booleans are Church booleans; recursion is the Y combinator |

**What this reveals:**

1. **Turing-completeness requires very little.**  The λ-calculus with
   application alone is enough.  Everything else is for human factors:
   readability, performance, error detection, tooling.

2. **The "everything is X" commitment is both a strength and a ceiling.**
   Lisp's "everything is a list" makes macros natural but makes static
   types hard.  Haskell's "everything is pure" eliminates a class of bugs
   but requires monads for I/O.  Lua's "everything is a table" is
   elegant but makes performance predictable only with JIT.

3. **Languages that add primitives over time hit less design friction**
   than languages that commit to one primitive and must encode
   everything in it.  The "one primitive" languages have a beautiful
   uniformity in the small but struggle when the encoded concepts
   interact in complex ways.

4. **The right number of primitives is not 1 and not 20.**  Nomi's 8
   normal forms (binding, function, pattern, flow, block, data boundary,
   absence/result, explanation) are deliberately more than 1 but far
   fewer than the number of keywords in a typical language.

## 6. Positioning Nomi in the Design Space

For each axis, Nomi's position and the rationale:

| Axis | Nomi's position | Rationale |
|------|----------------|-----------|
| **Evaluation** | Eager (Python-compatible) | Laziness opt-in with visible marker |
| **Type discipline** | Runtime constraints first | Static checking as future upgrade |
| **Memory** | GC (Python-hosted) | Permanent runtime TBD; avoid GIL constraint |
| **Effects** | Explicit block policies | One primitive for resources, retry, trace, future effects |
| **Dispatch** | Pattern matching primary | Single dispatch for Python compat; multiple dispatch deferred |
| **Binding** | One binding story | No `let`/`var`/`const` distinction; optional constraints |
| **Modularity** | Files-as-modules initially | Simple import/export; no functors |
| **Concurrency** | Block policies as primitive | Avoid function coloring; structured concurrency as library |
| **Data** | Nominal `data` + structural matching | Closed for owned types, open for external recognition |
| **Metaprogramming** | Deferred to future layer | Scoped notation (`quote:`, `use units:`) for domain DSLs |

Nomi's design thesis, restated in terms of this framework:

> Nomi is an eager, nominally-typed, pattern-matching language with
> runtime constraints, explicit block-policy effects, and one binding
> story.  It deliberately keeps its core-primitive count low and its
> axis positions conservative, preferring library-first exploration
> and future compile-time upgrades over early commitment to advanced
> semantic mechanisms.

This thesis translates into concrete design rules and a synthesis process.
For the rules (primitive budget, axis coherence, elimination form, etc.), see
[Syntax Design Rules](../convenience/syntax_design_rules.md). For the process
(stance → loop → worked examples → traps), see
[Design Lessons and Integration §9](../convenience/design_lessons_and_integration.md).
For how strictly each design area is controlled, see
[Language Degrees Of Freedom](language_degrees_of_freedom.md).

## 8. The Cognitive Dimension

Languages differ not just in what computations they enable, but in what
**cognitive operations** they make easy.  This is a higher-level axis
than evaluation strategy or type discipline — it is about how the
programmer thinks.

### Local Reasoning

"Can I understand this function by reading only this function?"

| Helps local reasoning | Hurts local reasoning |
|-----------------------|----------------------|
| Immutability (Haskell, Clojure) | Mutable shared state (Python, Java) |
| Borrow checker (Rust) — prevents aliasing bugs | Exceptions (Python, Java) — non-local control flow |
| Pure functions (Haskell, Elm) — no hidden effects | Global variables — invisible coupling |
| Named constraints (Nomi) — what must be true is visible | Monkey-patching (Ruby) — any import can change any class |

### Temporal Reasoning

"Can I understand what happens when?"

| Helps | Hurts |
|-------|-------|
| Eager evaluation (most languages) — execution order follows source | Lazy evaluation (Haskell) — demand-driven order, space leaks |
| Explicit suspension points (Nomi `yield`) | Hidden non-local control (exceptions, async callbacks) |
| Structured concurrency (Kotlin, Swift) — scoped lifetimes | Unstructured threads + shared memory |

### Spatial Reasoning

"Can I understand where data lives?"

| Helps | Hurts |
|-------|-------|
| Value semantics (Rust, Swift, C++) — no aliasing surprises | Reference semantics (Python, Java) — multiple names, same object |
| Ownership tracking (Rust) — exactly one owner | Manual memory (C, Zig) — must track lifetimes |
| Explicit data boundaries (Nomi `Data.decode`) | Implicit serialization (Ruby `Marshal`, Python `pickle`) |

### Whole-Program Reasoning

"Do I need to know the entire codebase?"

| Helps | Hurts |
|-------|-------|
| Explicit imports — dependencies are visible | Type class instances — any module can add one |
| Nominal types — behaviour is bounded by the type definition | Monkey-patching — behaviour depends on what's loaded |
| Sealed data variants — exhaustiveness checking | Open classes — anything can be extended anywhere |

### The Extent/Intent Convergence

All cognitive properties converge on a single tension between:

- **Extent** (what IS): the state of the program.  Immutability, value
  semantics, ownership, and explicit data boundaries all address extent —
  they tell you what exists and what it refers to.
- **Intent** (what HAPPENS): the behaviour of the program.  Pure functions,
  structured concurrency, explicit suspension, and trace records all
  address intent — they tell you what the program does and in what order.

A language cannot optimise both simultaneously without compromise.
Haskell maximises extent reasoning (pure, immutable) at the cost of
intent reasoning (laziness makes execution order opaque).  Python
maximises intent reasoning (eager, sequential) at the cost of extent
reasoning (shared mutable state, no ownership tracking).

**Nomi's cognitive strategy:**
1. Constraints tell you what must be true about a value (extent, local).
2. Blocks make control policies explicit at the call site (intent, local).
3. Eager evaluation means execution follows source order (intent, temporal).
4. Trace records are first-class — ask "what happened?" (intent, whole-program).
5. Explicit imports, nominal data, no monkey-patching (extent, whole-program).

### The "No Free Variable" Test

A useful litmus test for cognitive load: can a newcomer understand one
function by reading that function alone?

- In a pure functional language: yes (no side effects, no mutation).
- In Python with exceptions: almost (need to know what exceptions callees throw).
- In Ruby with monkey-patching: no (any `require` could have changed any class).
- In Rust with ownership: yes (the type tells you about borrowing, aliasing).

Nomi's target: **a newcomer should be able to understand one function by
reading that function, its imports, and the `data` declarations it
references — nothing else.** This means: no monkey-patching, no open
classes, no implicit conversions, no global mutable state in the prelude.

## 9. Falsifiability — Testing Nomi's Primitive Set

A design-space framework is useful only if it can be falsified.  Here
are concrete tests for whether Nomi's set of primitives is the right
size:

### The "Can I Express This?" Test

If a common programming need **cannot** be expressed through Nomi's core
primitives without introducing a genuinely new irreducible concept, the
core is too small.

Candidates to test:
- **SIMD / vector computation** — can it reduce to collection verbs?
- **Probabilistic programming** — can it reduce to generators + constraints?
- **Bidirectional transformations (lenses)** — can they reduce to functions + data?
- **Reactive UI updates** — can they reduce to block policies + traces?

### The "Is This Actually Different?" Test

If a proposed feature introduces a new mechanism that is semantically
identical to an existing mechanism with different syntax, the core is
already the right size — the proposal is surface sugar.

Candidates to test:
- `unless` (inverted `if`) — same as `if not`
- `until` (inverted `while`) — same as `while not`
- `unless ... else` — same as `if ... else` with branches swapped
- `do...while` — same as `while True: ...; if not cond: break`

### The "Second Mini-Language" Test

If a proposed feature requires a new vocabulary of operators,
precedence rules, and scoping that does not compose with the existing
core, it is a second mini-language — reject.

Candidates to reject or fence:
- Embedded SQL with `SELECT ... FROM ... WHERE` as Nomi syntax
- Regex literals with their own escape rules
- Format strings with a new expression sub-language

### The "First-Hour" Test

Can a newcomer write a useful program after one hour with the language?
This constrains how many primitives the surface exposes.

If the first-hour program requires explaining monads, ownership, effect
handlers, or type-level computation, the primitives are not layered
correctly.  Each primitive should be usable without understanding all
the others.

## 10. References

### Primary Sources

- Landin, P. "The Next 700 Programming Languages" (1966).  CACM 9(3).
- Reynolds, J. "Definitional Interpreters for Higher-Order Programming Languages" (1972).
- Felleisen, M. et al. "A Programmer's Reduction Semantics for classes and mixins" (multiple papers).
- Krishnamurthi, S. "Programming Languages: Application and Interpretation" (2003, 2023).
- Cook, W. "On Understanding Data Abstraction, Revisited" (2009).  OOPSLA.
- Van Roy, P. "Programming Paradigms for Dummies: What Every Programmer Should Know" (2009).
- Wadler, P. "The Expression Problem" (1998).  Discussion on Java Generics mailing list.

### Nomi's Own Design Framework

- [language_degrees_of_freedom.md](language_degrees_of_freedom.md) — Core/sugar/library/scoped/rejected framework
- [language_foundation.md](language_foundation.md) — Canonical design foundation
- [language_spec.md](language_spec.md) — Draft language specification
- [../convenience/design_lessons_and_integration.md](../convenience/design_lessons_and_integration.md) — Systemic patterns, feature interactions, designer quotes
- [../convenience/syntax_synthesis_matrix.md](../convenience/syntax_synthesis_matrix.md) — Cross-language feature families

### Language-Specific Research

- [../research/deep_language_feature_survey.md](../research/deep_language_feature_survey.md)
- [../research/modern_language_feature_survey.md](../research/modern_language_feature_survey.md)
- [../research/error_handling_defer_resource_cleanup_notes.md](../research/error_handling_defer_resource_cleanup_notes.md)
- [../research/concatenative_languages.md](../research/concatenative_languages.md)
- [../research/array_languages_deep_dive.md](../research/array_languages_deep_dive.md)
