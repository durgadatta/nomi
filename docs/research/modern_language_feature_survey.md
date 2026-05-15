# Modern Language Feature Survey

> Status: raw research notes.
>
> Purpose: survey novel syntax and semantics from modern languages that are
> not yet deeply covered in the existing research corpus. For each language,
> extract the key ideas, show concrete syntax, and evaluate transferability
> to Nomi's design space (everyday medium-level programming with normal forms).
>
> Companion: [Language Family Coverage Map](language_family_coverage_map.md)
> already covers some of these at the family level; this document deepens
> the individual-language detail.

---

## Mojo (Modular)

### var vs let distinction

**Key idea:** `let` declares an immutable binding (Rust-style "immutable by
default"), while `var` declares a mutable binding. This is the opposite of
Python's default (everything is mutable). The compiler uses this to decide
whether to copy or transfer ownership.

**Concrete syntax:**
```mojo
let x: Int = 42       # immutable binding, may be stored in register
var y: Int = 42       # mutable binding, must have a memory location
y += 1                # ok
# x += 1              # compile error: x is immutable

fn example():
    let a = 10        # type inferred, immutable
    var b = a         # b is a copy
    b = 20            # ok, b is mutable, a unchanged
```

**Semantics:** The distinction is not just about reassignment. `let` values
can participate in ownership transfers differently. The compiler can optimize
`let` bindings more aggressively because their identity does not matter.

**Nomi transfer evaluation:**

Already aligned. Nomi's binding story treats all bindings as a single
operation (`receive value, optionally check, bind in scope`). Adding
`var`/`let` as two binding modes would be a second binding story and
violates the coherence contract:

> "Names are introduced through binding. Assignment, function parameters,
> block parameters, loop variables, pattern captures, imports, and exception
> aliases should all be understandable as: receive a value -> optionally
> check it -> bind it in a scope."

Nomi can signal mutability through constraints rather than binding keywords:
`name = value` (readable) versus `name:var = value` (explicitly mutable).
This keeps one binding story with optional mutability annotation.

**Verdict:** Do not split binding into two keywords. Consider a constraint
like `@mutable` or `mut` as an annotation on the binding target, not a
separate keyword.

### Ownership: borrowed, inout, owned

**Key idea:** Mojo's ownership model provides Rust-like safety without Rust's
borrow-checker complexity. Three conventions govern how arguments are passed:

- `borrowed` (default): callee can read but not mutate; caller retains
  ownership.
- `inout`: callee can mutate; caller retains ownership; changes are visible
  at the call site.
- `owned`: ownership transfers to the callee; caller cannot use the value
  after the call.

**Concrete syntax:**
```mojo
fn read_data(data: borrowed Data):        # default, explicit spelling optional
    print(data.field)

fn modify_data(data: inout Data):
    data.field = new_value

fn consume_data(data: owned Data):
    # data is destroyed when this function returns
    let internal = data.field
    # caller's reference is dead
```

**Semantics:** The compiler enforces these at compile time. `owned` enables
move semantics and eliminates copies for large values. `inout` replaces C++
reference parameters with explicit syntax.

**Nomi transfer evaluation:**

Ownership is explicitly postponed in Nomi's first-language scope:

> "The first usable Nomi should deliberately postpone: manual memory
> management."

However, the `inout` pattern is interesting for Nomi's block/yield story.
When `yield` sends a value to a block, there is an implicit ownership
question: does the yielded value belong to the callee or the block?

Mojo's `inout` maps to Nomi's yield semantics: the callee yields control, the
block may inspect or transform the value, and control returns. This is
already the model in Nomi's block design.

**Verdict:** Ownership syntax stays postponed. The yield/block story already
encodes a form of temporary reference that `inout` formalizes.

### @value decorator and value semantics

**Key idea:** `@value` generates a struct with value semantics: the identity
of a value type is its contents, not its location. Two `@value` structs are
equal if their fields are equal. Copying is deep.

**Concrete syntax:**
```mojo
@value
struct Point:
    var x: Float64
    var y: Float64

let p1 = Point(1.0, 2.0)
let p2 = Point(1.0, 2.0)
assert p1 == p2           # structural equality, generated automatically
```

**Semantics:** The `@value` decorator is a compile-time transformation that
generates `__eq__`, `__hash__`, `__copy__`, and move constructors. It is
similar to Python's `@dataclass` but with stronger guarantees about identity.

**Nomi transfer evaluation:**

Nomi's `data` declarations already encode value semantics. A `data` type has
structural equality, field access, display, and pattern forms. Mojo's
`@value` confirms that value semantics are a necessary default for
program-owned data, which aligns with Nomi's `data` design.

```nomi
# Nomi equivalent
data Point(x:Float, y:Float)
```

No transfer needed -- Nomi already has this.

**Verdict:** Already covered by `data`. No transfer needed.

### SIMD vectorization

**Key idea:** Mojo exposes SIMD as a first-class type in the standard
library. `SIMD[DType, size]` is a hardware vector register. Operations on
SIMD values map directly to hardware instructions.

**Concrete syntax:**
```mojo
from sys.intrinsics import SIMD

let a = SIMD[DType.int32, 4](1, 2, 3, 4)
let b = SIMD[DType.int32, 4](5, 6, 7, 8)
let c = a + b              # single instruction: [6, 8, 10, 12]
let d = a * b              # single instruction: [5, 12, 21, 32]
```

**Semantics:** SIMD values are not general collections. They are
fixed-width, hardware-aligned vectors with element-wise arithmetic.

**Nomi transfer evaluation:**

Nomi's first language is medium-level programming (scripts, data, CLIs,
services), not numerical or systems programming. SIMD belongs in the
postponed category. When Nomi later adds collection-level optimization,
"listable calls" that lower to SIMD could be an implementation strategy, but
users should not write SIMD types directly.

**Verdict:** Postpone. SIMD is an implementation detail for collection
lowering, not user-facing syntax.

### How it extends Python syntax

**Key idea:** Mojo is a superset of Python syntax with additions: `fn` (stricter
functions) vs `def` (classic Python functions), `struct` (value types) vs
`class` (reference types), ownership annotations, and compile-time
metaprogramming.

The `fn` declaration enforces:
- Arguments are immutable by default.
- Return type is required.
- Local variables must be declared.
- No implicit exceptions from called functions.

**Concrete syntax:**
```mojo
# Python-compatible
def legacy_style(a, b):
    return a + b

# Mojo-strict
fn modern_style(a: Int, b: Int) -> Int:
    let result = a + b
    return result
```

**Nomi transfer evaluation:**

Nomi is deliberately Python-adjacent for adoption, not a Python superset.
The `fn` vs `def` distinction would duplicate Nomi's function story. Nomi
has one function spelling (`func`) with optional constraints on parameters
and return values. The strictness is opt-in per parameter:

```nomi
func add(x:int, y:int) -> int:
    return x + y

# Looser version: no constraints
func add(x, y):
    return x + y
```

**Verdict:** No transfer. Nomi offers gradual constraint addition on one
function form rather than two function keywords.

---

## Jai (Jonathan Blow)

### Compile-time execution model

**Key idea:** Any Jai function can be marked to run at compile time. The
compiler executes it, and its result becomes a compile-time constant. There
is no separate macro language or template DSL. You write ordinary Jai code.

**Concrete syntax:**
```jai
# Compile-time function
compute_table :: () -> [] int {
    result: [100] int;
    for i: 0..99 {
        result[i] = i * i;
    }
    return result;
}

# Evaluated at compile time; the array is baked into the binary
squares := compute_table();
```

The `::` operator marks a compile-time binding or function. The compiler
runs the function during compilation. The result is a constant in the final
binary.

A program can also inspect types and generate code at compile time:

```jai
# Compile-time reflection: iterate over struct members
print_struct_fields :: (T: type) {
    for field: T.members {
        print("%: %\n", field.name, field.type);
    }
}
```

**Semantics:** The compiler includes a full Jai interpreter. Compile-time
code has access to the same standard library as runtime code. This means
serialization, code generation, and data transformation are regular Jai
programs.

**Nomi transfer evaluation:**

This is one of the strongest transfer candidates. Nomi's block/example/trace
story already points toward "examples as executable tests." Jai's
compile-time execution extends that idea: what if data initialization,
validation suites, and test fixtures are programs that run before the main
program?

Nomi's design already contains `examples` as executable anchors:

```nomi
func slugify(title:str) -> str:
    examples:
        " Hello World " => "hello-world"
    return title.strip().lower().replace(" ", "-")
```

The Jai lesson is: *don't build a separate compile-time language*. Make the
same language work in both phases. Nomi could extend its example/check system
so that `check` blocks run at program verification time using the same
interpreter.

Jai's compile-time reflection (iterating struct members) is more speculative
for Nomi. It requires exposing the type/field graph as inspectable values.
This aligns with Nomi's "explanation" story but is later-layer work.

**Verdict:** Strong transfer. The pattern "ordinary code that runs at an
earlier phase" maps to Nomi's examples, checks, and future verification
layer. Do not invent a separate macro/preprocessor/query language to do what
ordinary Nomi can do.

### using for context

**Key idea:** Jai's `using` brings a struct's fields into the current scope
without qualification. It is a controlled form of namespace flattening,
similar to Pascal's `with` but more explicit.

**Concrete syntax:**
```jai
Vector3 :: struct {
    x, y, z: float;
}

move_entity :: (pos: Vector3, delta: Vector3) {
    using pos;
    pos = Vector3.{ x + delta.x, y + delta.y, z + delta.z };
    # 'x' refers to pos.x without qualifying
}
```

Multiple `using` declarations create ambiguity resolution rules. The
innermost `using` wins.

**Semantics:** This is syntactic rather than semantic. It flattens namespace
access without changing scoping rules. The intent is to reduce repetition
when a single struct is the "current subject."

**Nomi transfer evaluation:**

Nomi's block parameters already provide a form of contextual access:

```nomi
using(open(path)) -> file:
    text = file.read()
# 'file' is scoped to the block
```

But `using` in Jai's sense (flattening a struct's fields into scope) is
different. It's related to Nomi's collection transformation story, where
placeholders like `_` refer to the current element:

```nomi
users |> where(_.active) |> select(_.name)
```

The `_` placeholder is a controlled form of "the current subject" without
flattening all fields. This is safer than `using` because it does not
create ambiguous field references.

**Verdict:** Partial transfer. The `_` placeholder already serves the
"current subject" role without the ambiguity risk of full field flattening.
Jai's `using` is a cautionary reference: flattening fields into scope is
convenient but creates resolution puzzles.

### SOA/AOS data layout directives

**Key idea:** Jai lets the programmer switch between Array-of-Structs (AOS)
and Struct-of-Arrays (SOA) layout without changing the logical code. A
compiler directive controls memory layout, and access syntax stays the same.

**Concrete syntax:**
```jai
Entity :: struct {
    position: Vector3;
    velocity: Vector3;
    health: float;
}

# AOS layout (default): Entity[N]
# stored as [pos,vel,hp], [pos,vel,hp], [pos,vel,hp] ...

# SOA directive:
Entity :: struct SOA {
    position: Vector3;
    velocity: Vector3;
    health: float;
}
# stored as [pos,pos,pos...], [vel,vel,vel...], [hp,hp,hp...]

# Access syntax is identical:
entities: [1000] Entity;
entities[5].health = 0.5;   # compiler emits correct offset for layout
```

**Semantics:** The programmer writes `entities[i].field`. The compiler
chooses the memory access pattern based on the layout directive. This
separates logical structure from memory representation.

**Nomi transfer evaluation:**

This is firmly in Nomi's postponed category (systems programming, memory
layout). Nomi's collection story is about transformation verbs (`where`,
`select`, `map`), not memory layout directives.

For Nomi's future collection layer, the relevant lesson is: *preserve the
same access syntax for different storage backends*. If Nomi later supports
columnar data through backends like Polars or DuckDB, the syntax should be:

```nomi
# Same access syntax regardless of backend
people |> where(_.age >= 18) |> select(_.name)
```

Whether `people` is an in-memory list or a lazy Arrow table is an
implementation detail.

**Verdict:** No syntax transfer. The abstraction principle (same access
syntax, different storage) is a useful reminder for collection backends.

### #run for compile-time code

**Key idea:** `#run` executes arbitrary Jai code at compile time and
splices the result into the program text. It is more general than
compile-time functions because the code runs as a side-effecting script.

**Concrete syntax:**
```jai
#run {
    // This runs during compilation
    file_contents := read_file("config.json");
    print("Config loaded: % bytes\n", file_contents.count);
}

// #run can generate declarations:
#run string_table("data/strings.txt");

// The string_table function (defined elsewhere) reads a file
// and emits array declarations into the program at this point.
```

**Semantics:** The `#run` block is a mini-program that executes during
compilation. It can read files, compute values, and emit code. This is
how Jai avoids external build scripts and code generators.

**Nomi transfer evaluation:**

Jai's `#run` solves a real problem: build-time code generation without a
separate build system. Nomi can learn from the need without adopting the
syntax. The Nomi translation is:

- Module initialization that runs once at load time (similar to Python
  module-level code).
- Design-fixture generation for tests.
- Compile-time constant tables computed by ordinary functions.

Nomi's constraint: "Do not make ordinary code implicitly symbolic." A
`#run`-style feature must be explicitly marked so readers know when code
runs at a different phase.

**Verdict:** Later-layer transfer. Module initialization already covers some
of this. For metaprogramming, Nomi's `quote`/rewrite boundary (planned for
layer L11) is the right vehicle. Jai's lesson is: *make compile-time code
look like ordinary code*, don't invent a second language.

---

## Darklang

### Trace-driven development

**Key idea:** Darklang records live HTTP traces through your program. Instead
of writing tests manually, you send a real request and Darklang captures the
input, every intermediate value, and the output. You can then replay the
trace, inspect any intermediate value, and refactor against captured
behavior.

**Concrete workflow:**
```text
1. Deploy handler (one click)
2. Send a request from the UI or curl
3. Darklang captures: request -> handler -> intermediate values -> response
4. Click any intermediate value to see its contents at that point in time
5. Edit the handler code; Darklang replays the trace against the new code
6. See where the new code diverges from the captured trace
```

**Semantics:** Traces are first-class development artifacts, not log lines.
The editor shows you data flowing through your code. This flips the
debugging model: you don't set breakpoints and guess; you click values that
were actually computed.

**Nomi transfer evaluation:**

This is one of the highest-impact transfers for Nomi. Nomi's design already
commits to "every semantic event should be able to explain itself" and
"diagnostics are not later decoration." Darklang shows what happens when
this is taken seriously at the tooling level.

Nomi's traceable events already include: bind, judge, call, match, yield,
effect, rewrite, example-check. Darklang adds: *capture traces from live
execution and replay them during development*.

The transfer is not syntax. It is a design commitment: Nomi's trace records
should be structured enough to support replay. When a user edits a function
with `examples`, the interpreter should be able to re-run the examples
against the new code. When a user debugs a pipeline, the intermediate values
should be inspectable.

**Verdict:** Strong transfer. Nomi's trace layer (L10) should be designed
with replay in mind. The syntax transfer is not needed; the semantic
transfer (structured traces, replayable examples, intermediate-value
inspection) is essential.

### Deployless architecture

**Key idea:** In Darklang, there is no deployment step. You edit code in the
editor, and it is live. There are no build servers, no CI/CD pipelines, no
Docker images, no Kubernetes configs. The entire infrastructure layer is
invisible.

**Concrete semantics:**
```text
- No `git push` + CI + deploy pipeline
- Edit code, it's live immediately
- Database migrations are handled by the platform
- Secrets are managed by the platform
- Scaling is handled by the platform
```

**Nomi transfer evaluation:**

Nomi is not a cloud platform and should not become one. The deployless ideal
is a platform property, not a language property. However, the *spirit* of
deployless matters for Nomi: reduce the gap between "I wrote code" and "I
can see what it does."

Nomi can approximate this through:
- A fast REPL/interactive mode.
- The notebook kernel showing results immediately.
- Examples that run as you type (live-checking, like a linter on save).
- The web playground with instant feedback.

**Verdict:** Indirect transfer. Nomi should invest in fast feedback cycles
(REPL, notebook, playground) but not pretend infrastructure does not exist.
The design principle is: *minimize the distance between edit and feedback*.

### How traces inform type inference

**Key idea:** Darklang infers types from live traces. If your handler always
receives `{"name": "Alice", "age": 30}`, Darklang infers the input type as
`{name: String, age: Int}`. If a trace arrives with `{"name": "Bob", "age":
"forty-two"}`, Darklang detects the mismatch and flags it.

**Concrete semantics:**
```text
Request 1: {"name": "Alice", "age": 30}      -> inferred: {name: Str, age: Int}
Request 2: {"name": "Bob", "age": "unknown"} -> type error flagged in editor
```

The type system is not declared. It is discovered from observed data. The
editor shows inferred types as hints, and mismatches appear as diagnostics.

**Nomi transfer evaluation:**

This is the opposite of Nomi's explicit boundary philosophy. Nomi wants
users to declare what they expect:

```nomi
data User(name:str, age:int)
user = User.decode(raw)
```

Darklang's trace-inference is appealing for rapid prototyping, but it
creates a fragile dependency on observed data. A trace might not cover all
cases. Nomi's explicit constraints (`age:int, age >= 0`) say what must be
true, not what has been observed.

However, trace-informed *diagnostics* are valuable. If Nomi records traces of
actual values flowing through a `decode` boundary, it could warn: "You
declared `age:int` but 12% of observed values are floats that truncate."

**Verdict:** Partial transfer. Keep explicit constraints as the source of
truth. Use traces to enrich diagnostics and catch mismatches between declared
expectations and observed reality. Do not infer types from traces.

---

## Unison

### Content-addressed code

**Key idea:** Unison identifies every definition by a hash of its content
(its abstract syntax tree). Names are purely local aliases. The same
definition has the same hash regardless of what it's called or where it
lives.

**Concrete syntax:**
```unison
-- This definition has a hash, e.g. #abc123def
square x = x * x

-- These names all refer to the same definition
sq = square
quadrat = square
alCuadrado = square

-- Renaming is free: just change the name binding
> names square
  square : Nat -> Nat
  sq : Nat -> Nat
  quadrat : Nat -> Nat
```

Updating a function creates a new hash. Old callers can still reference the
old hash. There is no "dependency hell" because the hash uniquely identifies
the exact code.

**Semantics:** The codebase is a content-addressed store. "Updating a
dependency" means changing which hash a name points to. There is no
version-range constraint solver. Two versions of a library can coexist
because they have different hashes.

**Nomi transfer evaluation:**

This is a radical departure from file-based source management and is not
compatible with Nomi's first-language scope. Nomi is Python-adjacent; users
expect files, directories, and packages.

However, the *idea* of content-addressing is useful at a lower layer:
- Snapshot tests could be keyed by the hash of the code that produced them.
- Trace records could reference the specific version of a function that
  produced them.
- Design fixtures could pin expected output to the exact code version.

**Verdict:** No syntax transfer. The content-addressing idea can inform test
and trace infrastructure. Use hashes as stable identifiers for artifacts,
not as the primary code organization model.

### Abilities / algebraic effects

**Key idea:** Unison's ability system tracks which side effects a function
requires. An ability is like a type-level annotation for effects: `{IO}` for
I/O, `{Exception}` for exceptions, `{Store v}` for mutable state. Abilities
compose in function signatures.

**Concrete syntax:**
```unison
-- A function requiring IO
greet : Text -> {IO} Text
greet name =
    printLine ("Hello, " ++ name)
    name

-- A pure function (no abilities required)
add : Nat -> Nat -> Nat
add x y = x + y

-- A function requiring both IO and Exception
riskyRead : Text -> {IO, Exception} Text
riskyRead path =
    contents = readFile path
    if contents == "" then raise (Generic "empty file")
    else contents

-- Ability polymorphism: requires whatever abilities `f` requires
map : (a -> {e} b) -> [a] -> {e} [b]
```

The `{e}` syntax means "this function requires whatever abilities the
argument function `f` requires." Ability handlers provide the implementation
for an ability:

```unison
-- A handler for the Stream ability
Stream.toList : '{Stream a} r -> ([a], r)
```

**Semantics:** Abilities are type-tracked, not runtime-tracked. The compiler
ensures that a function only uses abilities it declares. Handlers provide
ability implementations and can be swapped (e.g., a test handler for I/O).

**Nomi transfer evaluation:**

Nomi explicitly postpones implicit effect tracking:

> "The first usable Nomi should deliberately postpone: implicit effect
> tracking."

Unison's abilities confirm that algebraic effects are a clean model for
tracking side effects. But Nomi's first language should not require users to
annotate `{IO}`, `{Exception}`, etc. on every function.

The transfer to Nomi is at the design level, not the syntax level. Nomi's
block system already provides a form of effect handling:

```nomi
retry(3, on=NetworkError):
    send(request)
```

The `retry` block is an effect handler for `NetworkError`. The block wraps a
body and provides policy for a specific effect. This is a more restricted but
more readable form of algebraic effects.

**Verdict:** Structural transfer, no syntax transfer. Nomi's block calls
already encode the handler/effect relationship. When Nomi adds effects (layer
L9), Unison's ability polymorphism is a good model for "this function
requires the abilities that `f` requires." Keep effects opt-in and
explicitly handled, never globally ambient.

### unique types for safe mutation

**Key idea:** Unison's `unique` type provides safe in-place mutation in a
pure language. A `unique` value is guaranteed to have exactly one reference
to it. When there's only one reference, mutating in place is observationally
equivalent to creating a new copy.

**Concrete syntax:**
```unison
-- A mutable buffer with unique reference
unique type MutableBuf a = MutableBuf (Array a)

-- Use it within a scope: create, mutate, extract value
modifyBuf : MutableBuf Nat -> Nat -> MutableBuf Nat
modifyBuf buf n =
    -- buf is unique, can be mutated in place
    MutableBuf.modify (at 0) (v -> v + n) buf
    buf
```

**Semantics:** The uniqueness guarantee is enforced by the type system. If a
value is `unique`, it cannot be aliased. The compiler can then emit in-place
mutation because no other reference can observe the change.

**Nomi transfer evaluation:**

This is systems-level optimization, firmly postponed. Nomi's first language
does not need to reason about aliasing for performance.

However, the *pattern* of unique references maps to Nomi's future capability
layer. When Nomi adds mutable state (layer L9), "unique reference" is a
useful capability model: a function that holds the unique capability to a
resource can mutate it safely.

**Verdict:** No syntax transfer. The uniqueness pattern may inform
capability design in the later effects/worlds layer.

### How refactoring works with hashed definitions

**Key idea:** In Unison, renaming a function does not change its hash.
Changing a function's body creates a new hash. The old hash still exists.
"Refactoring" means creating new hashes and optionally deprecating old ones.

**Concrete workflow:**
```text
1. Edit `square x = x * x` to `square x = x ** 2`
2. Unison computes new hash #def456gh
3. Old hash #abc123 still exists; existing callers still work
4. Run `upgrade` to find callers and suggest updating to new hash
5. Review each caller; accept or defer the upgrade
```

There is no flag day where all code must work with the new version. Old and
new can coexist. Upgrades are incremental.

**Nomi transfer evaluation:**

Nomi is file-based and will use conventional module/package versioning. The
hash-based upgrade model is a property of content-addressed code and does not
transfer to a file-based language.

However, the *incremental upgrade* pattern is valuable: Nomi's design
fixtures and regression tests should make it easy to run old examples against
new code and see where behavior changes.

**Verdict:** No direct transfer. The incremental upgrade UX is a reminder
that examples/traces should make behavior changes visible across versions.

---

## Configuration Languages (CUE, Nickel, Pkl, Dhall)

### CUE: unification / constraints as types

**Key idea:** CUE unifies types and values into one lattice. `string` is the
set of all strings. `"hello"` is a string. `"hello"` is-a `string`. CUE's
unification operator `&` combines constraints: `A & B` is the most specific
value that satisfies both.

**Concrete syntax:**
```cue
// Types are values at the top of the lattice
name: string         // name is some string
port: int & >=1024   // port is an int AND >= 1024
mode: "read" | "write" | "exec"

// Concrete values unify with types
spec: {
    name: "web-server"    // this IS-A string
    port: 8080            // this IS-A int AND >=1024
}

// Unification merges constraints from multiple sources
#Def: {
    name: string
    port: int & >=1024
}
spec: #Def & {
    port: 8080  // unifies: 8080 satisfies int & >=1024
}
```

**Semantics:** CUE has no separate "type language" and "value language."
Everything is a value in a constraint lattice. Unification means "find the
most specific value that satisfies all constraints." This is different from
both type checking (which validates) and JSON Schema (which describes).

**Nomi transfer evaluation:**

CUE's unification is the deepest semantic idea of any configuration language.
It treats "what must be true" and "what is true" as inhabiting the same
space. This aligns powerfully with Nomi's constraint story:

```nomi
age:int, age >= 13 else "Must be at least 13" = raw_age
```

Nomi already has `&`-like semantics in its constraint model: a binding can
carry multiple constraints, and they must all be satisfied. The
`value:Type, predicate` syntax is effectively unification: the value must be
both a `Type` AND satisfy the predicate.

The transfer is not syntax (Nomi already has its constraint syntax). It is
the design insight: *constraints are values in the same lattice as data*.
This means Nomi's constraint system should be able to:
- Compose constraints (a value must satisfy all of them).
- Report which constraint(s) failed.
- Allow constraints on constraint expressions.

CUE's `|` (disjunction) is also relevant: `mode: "read" | "write" | "exec"`
is a form of enumeration constraint that Nomi could adopt as a pattern form
or variant constraint.

**Verdict:** Strong semantic transfer. Nomi's constraint model already
mirrors CUE's unification in spirit. The `&` composition of constraints and
`|` enumeration of alternatives are patterns Nomi should support in its
constraint engine.

### Nickel: contracts

**Key idea:** Nickel separates contracts from types. A contract is a runtime
check that can be applied to any value. Contracts are first-class: they can
be passed as arguments, composed, and applied dynamically.

**Concrete syntax:**
```nickel
let NonZero = fun label value =>
    if value == 0 then
        std.contract.blame_with_message "value must be non-zero" label
    else
        value
in

let divide : Number -> Number -> Number = fun x y =>
    x / (y | NonZero)
in
divide 10 0  // => contract error: value must be non-zero
```

**Semantics:** The `|` operator applies a contract to a value. Contracts are
functions that take a label (for error reporting) and a value, and either
return the value or blame the label. Nickel uses contracts for data
validation at module boundaries.

**Nomi transfer evaluation:**

Nickel's contracts are close to Nomi's constraints but with a key difference:
contracts are applied *at use sites* (`y | NonZero`), while Nomi constraints
are applied *at binding sites* (`age:int, age >= 13 = raw_age`).

Nomi's model is cleaner for everyday code because the constraint lives with
the declaration, not scattered at every use. But Nickel's contract model is
useful for library boundaries where the constraint author is different from
the value producer.

The transfer insight: Nomi's `Constraint` values should be first-class. A
user should be able to:

```nomi
constraint NonNegative = (x:int, x >= 0)
# Reusable constraint, applied at binding sites
```

This is already implied by Nomi's operational core: `Constraint` is a core
type. The survey confirms it should be a user-visible type, not just an
internal mechanism.

**Verdict:** Partial transfer. First-class named constraints (`constraint`
keyword or `Constraint` type) would let users compose and reuse constraints
without duplicating predicate expressions. Nickel confirms that contracts as
values are useful at boundaries.

### Pkl: schema-as-values

**Key idea:** Pkl configurations are programs that evaluate to values.
Schemas are not external JSON Schema documents; they are functions that
produce values. You can write loops, conditionals, and transformations in
your configuration, not just static data.

**Concrete syntax:**
```pkl
// Schema definition (a template that produces configuration)
module MyApp

host: String
port: UInt16 = 8080

// Configuration that instantiates the schema
amends "MyApp.pkl"

host = "myapp.example.com"
port = 3000
```

```pkl
// Type-safe, with full programming features
class Server(host: String, port: Int) {
    url = "https://\(host):\(port)"
}

// Programmatic configuration
hidden (env: String) -> Server = new {
    when (env) {
        "prod" -> Server { host = "prod.example.com"; port = 443 }
        else -> Server { host = "dev.example.com"; port = 8080 }
    }
}

servers = List("staging", "prod").map(env -> new Server {
    host = "\(env).example.com"
    port = 443
})
```

**Semantics:** Configuration is a program that evaluates to a typed value.
Pkl blends schema definitions with value computation. `amends` means
"validate against this schema." Loops, functions, and conditionals are
available in configuration files.

**Nomi transfer evaluation:**

Pkl confirms Nomi's design decision that data boundaries are about programs
producing checked values:

> "config is a data-boundary problem, not a second data declaration language"

Pkl shows that a single language can handle both schema definition and value
production. Nomi's `data` + `decode` already follows this pattern:

```nomi
data Config(host:str, port:int, port >= 1024)
config = Config.decode(raw)
```

The transfer insight: Nomi should ensure that configuration files can use the
full language (functions, conditionals, loops) when producing data values.
The `decode` boundary is enough to ensure that what comes out is valid.

**Verdict:** Already aligned. Pkl confirms the approach. The one gap is
configuration *merging* (Pkl's `amends` supports overriding defaults
hierarchically). Nomi should consider a merge/override policy for data
values: when you `decode` a file that references another file, how do fields
combine?

### Dhall: pure configuration and imports

**Key idea:** Dhall is a total (non-Turing-complete) configuration language.
It can fetch config from URLs, enforce structural correctness, and guarantee
termination. It is explicitly not a general-purpose language.

**Concrete syntax:**
```dhall
-- Import from URL (with content-addressing for integrity)
let Server = https://example.com/schemas/Server.dhall

in  Server::{
    , host = "myapp.example.com"
    , port = 8080
}
```

```dhall
-- Type-safe configuration with functions (but no recursion)
let ports = [8080, 8081, 8082]

let server = \(host : Text) -> \(port : Natural) ->
    { host = host, port = port }

in  map Natural Text ports
```

**Semantics:** Dhall guarantees termination by banning recursion. It
guarantees reproducibility by content-addressing imports (the URL can include
a hash). It is designed to be a safe configuration language that can be
embedded in any host language.

**Nomi transfer evaluation:**

Dhall's non-Turing-completeness is a feature for configuration (you can't
write infinite loops in your Kubernetes config). Nomi is general-purpose, so
this constraint does not apply.

Dhall's import model (URL + content hash) is interesting for Nomi's future
module system. If Nomi supports fetching code or data from external sources,
a content-hash pinning mechanism ensures reproducibility.

Dhall's functional purity means configurations have no side effects. Nomi
does not enforce this for code, but configuration data should be produced by
pure computation (no file writes, no network calls during config evaluation).

**Verdict:** Partial transfer. Content-addressed imports and pure
configuration evaluation are useful design constraints for Nomi's module
system. The non-Turing-completeness is not needed for Nomi's general-purpose
scope.

### What each does that the others don't

| Feature | CUE | Nickel | Pkl | Dhall |
|---------|-----|--------|-----|-------|
| Unification / lattice semantics | Yes | No | No | No |
| First-class contracts | No | Yes | No | No |
| Turing-complete config | No | Yes | Yes | No |
| Remote imports with hashing | Limited | No | Yes (via amends) | Yes |
| Schema-as-program | Yes | Yes | Yes | Limited |
| Value-level constraints as types | Yes | No | No | No |
| Gradual typing | Yes | Yes | Yes | Yes |

### Patterns transferable to general-purpose data boundaries

1. **Unification for constraints**: CUE's `&` as constraint composition.
   Nomi already has this in its multi-constraint binding. Make it explicit
   and composable.

2. **Contracts as values**: Nickel's first-class contracts. Nomi should let
   users name and reuse constraint expressions.

3. **Configuration is code**: Pkl's schema-as-program. Nomi's `data` + `decode`
   already treats configuration as an instance of data production. Keep the
   full language available when producing configuration values.

4. **Content-addressed imports**: Dhall's import integrity. When Nomi adds a
   module/package system, consider content hashes for reproducibility.

5. **Merge/disjunction**: CUE's `|` for alternatives and Pkl's `amends` for
   overriding. Nomi should define a clear merge policy for data values: how do
   defaults, overrides, and disjunctions compose?

---

## Wren

### Fiber-based concurrency model

**Key idea:** Wren uses lightweight fibers for concurrency. Fibers are
cooperative: they yield control voluntarily. Unlike OS threads, fibers are
cheap (you can have thousands). Unlike async/await, there is no function
color -- any function can yield.

**Concrete syntax:**
```wren
// Create a fiber
var fiber = Fiber.new {
    System.print("Fiber started")
    Fiber.yield()          // voluntarily yield control
    System.print("Fiber resumed")
}

fiber.call()    // prints "Fiber started", returns at yield
fiber.call()    // prints "Fiber resumed", fiber completes
```

```wren
// Fiber with value passing
var fiber = Fiber.new {
    var value = Fiber.yield("hello")  // yield sends "hello", returns "world"
    System.print(value)               // prints "world"
}

fiber.call()          // returns "hello"
fiber.call("world")   // passes "world" back, fiber completes
```

**Semantics:** Only one fiber runs at a time. `Fiber.yield()` suspends the
current fiber and returns control to the caller. `fiber.call()` resumes the
fiber. Values pass in both directions at the yield/call boundary.

**Nomi transfer evaluation:**

This is almost identical to Nomi's block/yield model:

```nomi
coroutine_style_block:
    # do work
    yield(value)   # suspend, send value to caller
    # caller returns control with new value
```

```nomi
# The caller side: invoke the block, get values back
using(fiber_block) -> val:
    process(val)
    # implicit: control returns to fiber
```

Wren's fiber model confirms that `yield` with bidirectional value passing is
a sufficient primitive for cooperative concurrency. Nomi's block story
already captures this. The transfer insight is that fibers and blocks are the
same abstraction seen from different angles: a block is caller-side code
controlled by a callee; a fiber is callee-side code controlled by a caller.
They are inverses.

**Verdict:** Already aligned. Wren confirms that cooperative fibers and
Nomi's block/yield are the same pattern. No new syntax needed.

### Small embeddable OO design

**Key idea:** Wren is designed to be embedded in a C host application. It has
a small, regular object model: everything is an object, classes are objects,
and inheritance is single and simple. The entire language fits in a small,
embeddable VM.

**Concrete syntax:**
```wren
class Rectangle {
    construct new(width, height) {
        _width = width
        _height = height
    }

    area { _width * _height }   // getter (no parentheses)
    width=(value) { _width = value }  // setter
}

var rect = Rectangle.new(3, 4)
System.print(rect.area)  // 12
rect.width = 5           // calls setter
```

**Semantics:** Wren's OO is intentionally small. No metaclasses, no
method_missing, no mixins. The design tradeoff is: expressive enough for game
scripting, simple enough for the VM to be tiny.

**Nomi transfer evaluation:**

Nomi is not an embeddable scripting language and does not need Wren's
minimalism constraints. Nomi's data declarations already provide constructor
functions, field access, and pattern forms without a class keyword:

```nomi
data Rectangle(width:Num, height:Num)

func area(rect:Rectangle) -> Num:
    return rect.width * rect.height
```

Nomi's approach is to separate data (what it is) from functions (what you do
with it) rather than bundling them into classes. This is a deliberate design
choice that aligns with Nomi's coherence contract: one data story, one
function story.

Wren's getter/setter syntax (`area { ... }` / `width=(value) { ... }`) is
syntactic sugar for property access. Nomi could consider property-style
access (implicit getter/setter calls that look like field access) as a later
convenience, but it should reduce to ordinary function calls.

**Verdict:** No syntax transfer. Nomi's data/function separation is
deliberate. Property access (sugar for getter/setter calls) could be a
later convenience layer if it reduces cleanly to functions.

---

## Janet

### PEGs (parsing expression grammars) as first-class syntax

**Key idea:** Janet includes PEG as a first-class language construct. You
define a grammar inline using the `peg/compile` function, and Janet uses it
to parse text. PEGs are an alternative to regex that handle nested structures
and are more readable for complex patterns.

**Concrete syntax:**
```janet
(def grammar
  (peg/compile
    ~{:s (any (+ :w :d))
      :w (range "az" "AZ")
      :d (range "09")
      :main (* :s -1)}))

(peg/match grammar "hello42")   # => @["hello42"]
(peg/match grammar "hello!")    # => nil (no match)
```

PEG patterns can be composed and reused:
```janet
(def identifier
  (peg/compile
    ~{:start (* (range "az" "AZ" "_") (any (+ (range "az" "AZ" "09") "_")))
      :main (* :start -1)}))

(def assignment
  (peg/compile
    ~{:main (* (cmt :identifier '=) :value (cmt (+ (range "09") "."))
               -1)}))
```

The `~` prefix creates a "peg literal" -- syntax that looks like a regex
pattern but is a PEG grammar. `*` means sequence, `+` means one or more,
`any` means zero or more, `range` is character class, `-1` means end of
input.

**Semantics:** PEGs are recognition-based, not backtracking (unlike regex).
`/` is ordered choice: try first, if it fails try second. This avoids
exponential backtracking and makes PEGs deterministic. The grammar is a
first-class value you can compose, inspect, and pass around.

**Nomi transfer evaluation:**

This is a significant transfer candidate. Nomi needs a parsing/decoding story
for external data. Janet's PEG integration shows that parsing can be part of
the language rather than a separate tool.

For Nomi, the transfer is not PEG syntax directly. It is the principle:
*structural pattern matching for text is the same abstraction as structural
pattern matching for data*. Nomi's pattern system should be able to match
both structured values and text sequences:

```nomi
# Structured data pattern (already in Nomi's design)
match raw:
    case {"email": email:str, "age": age:int}:
        ...

# Text parsing pattern (hypothetical future)
parse csv_line:
    case [name:word, "," age:int, "," email:word]:
        ...
```

Nomi's pattern engine (structural test + tentative bindings + constraints)
could be the foundation for a text-parsing layer. Janet's PEGs show that
inline grammar definition works well as part of the language rather than an
external DSL.

**Verdict:** Architectural transfer. Nomi's pattern system should be
designed with future text/sequence matching in mind. Janet shows that PEG
literals as first-class values are more composable than regex strings.

### Fibers and resume

**Key idea:** Janet has first-class fibers similar to Wren's. `fiber/new`
creates a fiber from a function, `resume` runs or continues it, and `yield`
suspends it.

**Concrete syntax:**
```janet
(def f (fiber/new (fn []
    (print "step 1")
    (yield 1)
    (print "step 2")
    (yield 2)
    (print "done")
    3)))

(resume f)   # prints "step 1", returns 1
(resume f)   # prints "step 2", returns 2
(resume f)   # prints "done", returns 3
```

```janet
# Error handling across fibers
(def f (fiber/new (fn [] (error "boom"))))
(def result (resume f))
(when (= (fiber/status f) :error)
  (print "fiber errored: " (fiber/last-value f)))
```

**Semantics:** Janet's fibers are the same model as Wren's: cooperative
multitasking with value passing. The `fiber/status` introspection
(`:pending`, `:alive`, `:dead`, `:error`) is notable: fibers have observable
state that can be queried without resuming.

**Nomi transfer evaluation:**

Same as Wren: the fiber model is already Nomi's block/yield model. Janet adds
one transferable idea: observable fiber/block state. Nomi blocks should be
introspectable:

```nomi
block = retry(3, on=NetworkError):
    send(request)

# Query block: has it been invoked? completed? errored?
block.status     # => :pending | :running | :done | :failed
block.trace      # => list of yield/resume/error events
```

This aligns with Nomi's trace/explanation story (layer L10).

**Verdict:** Already aligned for fibers. Janet's block status introspection
is a useful addition to Nomi's trace model.

### Tables and prototypes

**Key idea:** Janet's primary data structure is the table (mutable mapping)
with prototype-based inheritance. A table can have a prototype table;
property lookup falls through to the prototype.

**Concrete syntax:**
```janet
(def animal @{:species "unknown" :sound "..."})

(def dog (table/setproto @{:sound "woof"} animal))

(get dog :species)   # => "unknown" (inherited from animal)
(get dog :sound)     # => "woof"     (own property)
```

Janet also supports abstract data types with prototypes:

```janet
(def Dog
  @{:type :Dog
    :bark (fn [self] (string "woof, I'm " (self :name)))})

(def fido (table/setproto @{:name "Fido"} Dog))
(fido :bark)   # => "woof, I'm Fido"
```

**Semantics:** This is prototype-based OO (like JavaScript, Lua) rather than
class-based. Methods are ordinary functions stored in tables. Inheritance is
delegation.

**Nomi transfer evaluation:**

Nomi explicitly avoids prototype-based dispatch in favor of data + function
separation. Prototype inheritance creates implicit lookup chains that
conflict with Nomi's "explicit boundaries" rule.

However, Janet's table model is useful as a reminder that not all data needs
class-based organization. Nomi's mapping patterns and structural pattern
matching already handle prototype-like "recognize by structure, not nominal
type":

```nomi
match value:
    case {"sound": s:str, "name": n:str}:
        # Matches any mapping with these fields, regardless of prototype
```

**Verdict:** No transfer. Nomi deliberately chooses data + function
separation over prototype-based dispatch.

---

## Lobster

### Memory management (ownership without annotations)

**Key idea:** Lobster achieves memory safety and deterministic cleanup
without ownership annotations. The compiler infers ownership from the
program's data flow. The programmer never writes `borrow`, `owned`, or
lifetime annotations.

**Concrete semantics:**
```lobster
// Lobster infers that `v` is owned by this scope
// and frees it at the end. No manual annotation.

fn make_vector(x:float, y:float, z:float): new_vector3 =
    return [ x, y, z ]      // allocated, returned to caller

fn use_vector():
    let v = make_vector(1, 2, 3)
    print(v.x)
    // v is freed here (end of scope), no GC, no annotation

// Shared references use reference counting (inferred):
fn share_vector(v):
    let copy = v             // refcount incremented
    print(copy.x)
    // copy's refcount decremented here
```

The key insight: in most programs, ownership is obvious from the data flow.
The compiler tracks whether each value has a single owner (unique, freed at
end of scope) or is shared (reference counted). The programmer doesn't write
annotations because the compiler can see when a value escapes its scope, when
it's aliased, and when it's dead.

**Nomi transfer evaluation:**

This is strong evidence for Nomi's position to postpone ownership syntax.
Lobster demonstrates that ownership can be inferred by the compiler without
user-visible annotations. Nomi's first language does not need `borrowed`,
`inout`, `owned` keywords because the runtime or compiler can infer resource
cleanup.

The transfer is not Lobster's implementation (which requires sophisticated
flow analysis). It's the design principle: *ownership is an implementation
concern, not a required user-facing syntax*. Users care about "when is my
file closed?" and "when is my memory freed?" but do not need to annotate
every reference.

Nomi's block system already handles the common case:

```nomi
using(open(path)) -> file:
    text = file.read()
# file is closed here; the `using` block encodes the ownership policy
```

The `using` block is a visible boundary for resource ownership. Lobster shows
that even this could be inferred, but Nomi keeps it explicit for readability.

**Verdict:** Indirect transfer. Lobster validates Nomi's decision to
postpone ownership annotations. The compiler can infer more than we might
assume. Nomi's `using` blocks already handle deterministic cleanup at visible
boundaries.

### Type system approach

**Key idea:** Lobster has a gradual type system. Types are optional. When you
declare them, the compiler checks them. When you don't, the runtime handles
it. The type checker uses flow-sensitive typing and structural subtyping.

**Concrete syntax:**
```lobster
// Untyped
def add(a, b):
    return a + b

// Typed: structural matching, not nominal
def add(a::number, b::number)::number:
    return a + b

// Type inference from context
let v: vector3 = [ x, y, z ]   // type is inferred
let list = [1, 2, 3]           // type inferred as [int]
```

**Semantics:** Types describe structure, not names. `{x:float, y:float}` is
the type for any value with those fields, regardless of whether it was
declared as `Point` or `Position`. This is structural typing.

**Nomi transfer evaluation:**

Nomi's type story is still being designed. Lobster's structural typing is
compatible with Nomi's pattern philosophy ("patterns test structure and bind
names"). If Nomi adds a type annotation system, structural types are a better
fit than nominal types because they align with the pattern engine:

```nomi
# Structural: any value with x:float and y:float works here
func distance(p:{x:float, y:float}) -> float:
    return sqrt(p.x ** 2 + p.y ** 2)
```

However, Nomi's `data` declarations create nominal distinctions:

```nomi
data Point(x:float, y:float)
data Vector(x:float, y:float)
# Point and Vector have the same structure but different meanings
```

The resolution is to allow both: structural types for "I need something with
these fields" and nominal types for "I need this specific domain type." The
binding constraint `:Type` can accept either.

**Verdict:** Partial transfer. Lobster's gradual, structural typing is a
good model for Nomi. Keep types optional, structural by default, with nominal
types available through `data` declarations.

---

## D (language)

### static if and compile-time reflection

**Key idea:** D's `static if` evaluates a condition at compile time and
includes or excludes code based on the result. Combined with `__traits`, it
enables compile-time introspection of types, functions, and modules.

**Concrete syntax:**
```d
// Compile-time conditional
static if (is(T == int)) {
    int fast_add(T a, T b) { return a + b; }
} else {
    T generic_add(T a, T b) { return a + b; }
}

// Compile-time reflection: iterate over struct fields
struct Person {
    string name;
    int age;
    double height;
}

string toJSON(Person p) {
    string result = "{";
    // foreach over struct members at compile time
    static foreach (member; __traits(allMembers, Person)) {
        result ~= `"` ~ member ~ `": ` ~ to!string(__traits(getMember, p, member)) ~ ",";
    }
    result ~= "}";
    return result;
}

// Type introspection
static if (__traits(compiles, a + b)) {
    // This code only included if a + b compiles
}
```

**Semantics:** The `static if` branch is resolved during compilation. The
excluded branch is not type-checked. This enables type-generic code without
templates or generics (though D has those too). `__traits` provides
compile-time reflection: list struct members, check if an expression
compiles, get parameter names, etc.

**Nomi transfer evaluation:**

D's `static if` is a dual-phase construct: some code runs at compile time,
some at runtime. This is the same insight as Jai's `#run` but with different
syntax.

For Nomi, the transfer is at the design level:
- Nomi's examples already run at check/verification time.
- Nomi's future `quote`/rewrite layer could inspect and generate code at
  compile time.
- `static foreach` (iterate over struct members at compile time) is useful for
  deriving serialization, display, and comparison automatically.

Nomi could generate `data` boilerplate (encode/decode, display, equality)
using compile-time reflection over data fields:

```nomi
# Hypothetical: derived display for a data type
# The compiler already knows the fields; it generates display automatically
data Person(name:str, age:int)
# Person("Ada", 30) -> displays as: Person(name="Ada", age=30)
```

**Verdict:** Later-layer transfer (L11 quote/rewrite). Compile-time
reflection over data fields is the most immediate use case for generated
derivations.

### Contract programming (in, out, invariant)

**Key idea:** D supports Design by Contract natively. `in` contracts check
preconditions before a function body. `out` contracts check postconditions
after the body. `invariant` contracts check class invariants at method
boundaries.

**Concrete syntax:**
```d
int sqrt(int x)
in {
    assert(x >= 0, "Cannot compute sqrt of negative number");
}
out (result) {
    assert(result >= 0, "sqrt must be non-negative");
    assert(result * result <= x, "sqrt squared must not exceed input");
}
do {
    // function body
    return cast(int) std.math.sqrt(cast(real) x);
}

// Class invariant
class BankAccount {
    double balance;
    invariant {
        assert(balance >= 0, "Balance must never be negative");
    }
}
```

`in` contracts can read the function arguments. `out (result)` contracts
can read both the arguments and the return value.

**Semantics:** Contracts are runtime checks, not compile-time proofs. They
can be enabled/disabled per build (debug vs. release). Failed contracts throw
assertion errors with the contract text.

**Nomi transfer evaluation:**

This is one of the closest matches to Nomi's constraint model. D's `in`
contract is Nomi's parameter constraint. D's `out` contract is Nomi's return
constraint. D's `invariant` is a per-data-type constraint that applies to all
field modifications.

```nomi
# Nomi equivalent of D contract
func sqrt(x:(int, x >= 0 else "Cannot compute sqrt of negative number")) -> (int, result >= 0):
    return int(sqrt(x))

# D's invariant: data-level constraint
data BankAccount(balance:float, balance >= 0 else "Balance must never be negative")
```

Nomi's approach is more integrated: constraints are part of the binding
system, not a separate contract layer. D's contracts are tied to the function
declaration but are conceptually separate. Nomi unifies constraints with
binding.

D's `out (result)` syntax is notable because it names the return value for
constraint checking. Nomi should support this:

```nomi
func sqrt(x:int) -> result:(int, result >= 0):
    return int(sqrt(x))
```

The transfer: Nomi should allow naming the return value so that return
constraints can reference it.

**Verdict:** Strong transfer. Nomi's constraints are a tighter integration of
D's contracts. Add named result bindings for return constraints. D's
invariant pattern is already covered by data field constraints.

### scope for ownership

**Key idea:** D's `scope` attribute prevents a reference from escaping its
scope. A `scope` parameter or local variable cannot be stored in a global,
returned, or assigned to a longer-lived reference.

**Concrete syntax:**
```d
void process(scope int* ptr) {
    *ptr = 42;
    // ptr cannot escape this function; the compiler enforces this
    // global_ptr = ptr;  // compile error: scope variable escapes
}

scope int* get_ref() {
    int local = 10;
    // return &local;  // compile error: scope return from stack variable
}
```

**Semantics:** `scope` is a lightweight ownership annotation for memory
safety. It is simpler than Rust's borrow checker because it has a single
rule: "don't escape." The compiler checks this locally without whole-program
analysis.

**Nomi transfer evaluation:**

This is systems-level ownership control, explicitly postponed in Nomi's first
language. However, the *local* nature of `scope` (one rule, locally
checkable) is interesting. When Nomi adds ownership annotations, a
single-rule system ("this reference must stay in this scope") is simpler to
use and explain than Rust's full borrow system.

Nomi's `using` block already provides scope-bounded resource ownership:

```nomi
using(open(path)) -> file:
    # file is scoped to this block; it cannot escape
    text = file.read()
# file is closed here
```

**Verdict:** Postpone. The `using` block already covers scope-bounded
resource ownership for Nomi's everyday layer.

### @safe, @trusted, @system attributes

**Key idea:** D partitions functions into safety levels:
- `@safe`: compiler guarantees memory safety (no pointer arithmetic, no
  unchecked casts).
- `@trusted`: manually verified to be safe; can call `@system` code but
  presents a safe interface.
- `@system`: no safety guarantees; full access to low-level operations.

**Concrete syntax:**
```d
@safe int add(int a, int b) {
    return a + b;
    // int* p = &a + 1;  // compile error: pointer arithmetic not @safe
}

@trusted int fast_copy(void* dst, void* src, size_t n) {
    // Calls @system memcpy; trusts that it's safe
    import core.stdc.string : memcpy;
    memcpy(dst, src, n);
    return 0;
}

@system int raw_access(int* ptr) {
    *(ptr + 1000) = 42;  // allowed, but unsafe
    return 0;
}
```

**Semantics:** Safety is transitive: a `@safe` function can only call
`@safe` or `@trusted` functions, not `@system` functions directly. `@trusted`
is the escape hatch: a human vouches for the safety of a function that uses
unsafe internals.

**Nomi transfer evaluation:**

This is the most transferable idea from D. Nomi needs a way to designate
"safety zones" in code. The triplet `@safe` / `@trusted` / `@system` is
directly applicable to Nomi's constraint and trust model:

- `@safe` code: constraints are checked, data boundaries are enforced, no
  raw/untrusted access.
- `@trusted` code: the boundary where external libraries or raw data enter;
  the programmer asserts that the conversion is correct.
- `@system` code: no guarantees; used for low-level interop.

In Nomi terms:

```nomi
# @safe: constraints checked, data boundaries enforced (default Nomi)
func get_user_age(user:User) -> int:
    return user.age

# @trusted: programmer asserts safety of external interaction
@trusted
func decode_raw_csv(path:str) -> list[dict]:
    # This function calls external CSV parser
    # Output is checked by the caller's decode boundary
    return raw_csv_parse(path)

# @system: no constraint guarantees
@system
func raw_memory_operation(ptr:Ptr):
    ptr.write(42)
```

The transfer is not the exact syntax. It's the security posture: make the
safe path the default, require explicit annotation for untrusted code, and
provide a `@trusted` bridge for the boundary between them.

**Verdict:** Strong transfer. Nomi's constraint and data-boundary system
should be the `@safe` default. External interop and raw operations should be
explicitly annotated. This aligns with Nomi's existing commitment to
explicit boundaries.

---

## Cross-Cutting Themes

### Theme 1: Compile-Time Execution Is The Missing Metaprogramming Layer

Jai's `#run`, D's `static if`/`static foreach`, and Unison's content-hashing
all point to the same need: programs that inspect and generate programs.
Nomi's examples, traces, and future quote/rewrite layer should absorb this
without creating a second macro language.

### Theme 2: Constraints Are The Universal Boundary

CUE's unification, D's contracts, Nickel's first-class contracts, and Mojo's
value types all converge on constraints as the universal boundary primitive.
Nomi has already committed to this. The survey confirms it is the right bet.

### Theme 3: Fibers == Blocks == Cooperative Control

Wren's fibers, Janet's fibers, and Mojo's ownership model all describe the
same primitive: suspend, pass values, resume. Nomi's block/yield system
already captures this. The survey confirms the abstraction is powerful enough
to avoid adding both fibers and async/await and block parameters as separate
constructs.

### Theme 4: Data Boundaries Need Merge/Override Policies

CUE's unification, Pkl's `amends`, and Dhall's imports all handle the problem
of composing partial data definitions. Nomi's `decode` handles conversion but
not composition of multiple partial data sources. A merge/override/fallback
policy for data values is a gap.

### Theme 5: Safety Levels Should Be Named, Not Assumed

D's `@safe`/`@trusted`/`@system` triplet and Mojo's `fn` vs `def` both
create named safety levels. Nomi should define safety levels for code
(constrained/checked vs. trusted-interop vs. raw) and make them part of the
language's diagnostic vocabulary.

---

## Transfer Priority Summary

| Priority | Idea | Source | Nomi layer |
|----------|------|--------|------------|
| Immediate | Constraints as first-class values | Nickel, CUE, D | L3 constraints |
| Immediate | Named return bindings for constraints | D contracts | L4 functions |
| Immediate | Block/fiber state introspection | Janet, Wren | L8 blocks |
| Near-term | Trace-driven development | Darklang | L10 traces |
| Near-term | Safety level annotations | D (@safe/@trusted) | Data boundaries |
| Near-term | Constraint composition (unification model) | CUE | L3 constraints |
| Later | Compile-time reflection over data fields | Jai, D | L11 quote/rewrite |
| Later | Structural typing with nominal data | Lobster, D | Type system |
| Later | Data merge/override policies | Pkl, CUE | Configuration |
| Postpone | Ownership annotations (borrowed/inout/owned) | Mojo, D, Rust | Systems layer |
| Postpone | SOA/AOS layout directives | Jai | Systems layer |
| Postpone | Content-addressed code (hash-based identity) | Unison, Dhall | Module system |
| Postpone | SIMD vector types | Mojo | Implementation |
| Postpone | unique types for mutation | Unison | Systems layer |
| Postpone | Prototype-based dispatch | Janet | Rejected |
| Postpone | var vs let separate binding keywords | Mojo | Rejected |
| Rejected | Deployless platform (not language concern) | Darklang | N/A |
| Rejected | Non-Turing-complete config | Dhall | N/A |

---
