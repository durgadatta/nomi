# C#, Java, and Dart: Modern Feature Deep Dive

> Status: source research for Nomi design.
> Purpose: Survey modern language features in C#, Java, and Dart that are
> relevant to Nomi's design — especially pattern matching, records/data,
> null safety, and async models.

---

## C#

C# has undergone one of the most aggressive modernization trajectories of any
mainstream language. Starting from a Java-like OO baseline in the early 2000s,
it has absorbed functional patterns, declarative data modeling, and
expression-oriented syntax across versions 7 through 12. Three threads matter
most for Nomi: pattern matching (how to inspect and destructure variants),
records (how to model data with minimal ceremony), and null safety (how to
retrofit safety onto a nullable-by-default type system).

### 1. Pattern Matching (C# 7-12)

C# pattern matching did not land all at once. It accreted across six language
versions, each adding one or two pattern forms. This incremental rollout is
itself a design lesson: pattern matching can be adopted gradually without
breaking existing code, and each new pattern form unlocks new expressiveness
without requiring a rewrite of the old.

**Type patterns (C# 7).** The simplest form. `if (x is int i)` tests whether
`x` is an `int` and, if so, binds it to a new variable `i` in the enclosing
scope. This is the declaration pattern — a type test plus a binding in one
syntactic position. It eliminates the cast-after-check antipattern that
dominated C# for a decade.

```
if (x is int i)        → declaration pattern
if (x is string s)     → declaration pattern
```

**Property patterns (C# 8).** Patterns can now reach into object fields and
properties. `if (x is { Name: "Ada", Age: > 30 })` matches when `x.Name` equals
`"Ada"` and `x.Age` exceeds 30. Property patterns are recursive — nested
objects can be matched in a single pattern expression. This makes them
essentially structural: you describe the shape you want, not how to navigate
to it.

```
if (person is { Address: { City: "London" } })   → nested property pattern
if (user is { IsActive: true, Role: "admin" })   → multiple properties
```

**Switch expressions (C# 8).** The `switch` statement became a `switch`
expression — it produces a value and can appear anywhere an expression is
expected. The syntax uses `=>` arms (like a lambda) and `_` for the discard
/default case. This is the expression-oriented conditional that Nomi should aim
for: every branch produces a value, and exhaustiveness is checked by the
compiler.

```
var label = x switch {
    1 => "one",
    2 => "two",
    _ => "many"
};
```

**Tuple and positional patterns (C# 8-9).** Tuples can be destructured
directly in patterns. `if (point is (0, 0))` matches when both components are
zero. Combined with deconstruction (a `Deconstruct` method), this works on
user-defined types as well.

```
if (point is (0, 0))              → tuple pattern
if (point is (var x, > 0))        → positional with binding and relational
```

**List patterns (C# 11).** Lists and arrays can be matched with slice
patterns. `list is [1, .. var rest, 5]` matches when the first element is 1,
the last is 5, and everything in between is bound to `rest`. The `..` slice
pattern can appear at most once per list pattern. This is comparable to
Haskell/OCaml list patterns (`x :: xs`) but more verbose.

```
if (list is [1, 2, 3])              → exact list pattern
if (list is [1, .. var middle, 5])  → slice pattern
if (list is [])                      → empty list pattern
```

**Relational patterns and combinators (C# 9+).** Patterns can express
comparisons (`>`, `<`, `>=`, `<=`) and can be combined with `and`, `or`, and
`not`. This means a single `is` expression can replace a chain of `if`
conditions.

```
if (x is > 0 and < 10)              → range check as pattern
if (x is not null)                   → null check as pattern
if (x is int or long)                → type union as pattern
```

**Exhaustiveness.** C# enforces exhaustiveness on switch expressions when the
matched type is an enum or when `[ExhaustiveMatch]` is used (analyzer-driven,
not built-in). The real guarantee comes with sealed hierarchies — if you match
on a sealed type and cover all permitted subtypes, the compiler knows the match
is exhaustive. This is the pattern that Java and Dart later adopted more
explicitly.

**Nomi relevance.** C# shows that pattern matching can be added to a
statement-oriented language without breaking backward compatibility. The key
design decision is making the switch/match an expression with mandatory
exhaustiveness, not an optional statement. Nomi should adopt expression-switch
from day one, not retrofit it.

**Compare with:** Rust `match` (the gold standard — always exhaustive, always
an expression, no fallthrough), Swift `switch` (exhaustive on enums, `let`
binding), Kotlin `when` (no fallthrough, expression form, smart casts), F#
`match` (ML-style, exhaustive, expression, active patterns).

### 2. Records (C# 9-10)

Records are C#'s answer to "how do I model data without ceremony?" They
represent a significant departure from C#'s class-default-mutable heritage.

**Value semantics.** Two record instances are equal if all their fields are
equal — structural equality, not reference equality. `Equals`, `GetHashCode`,
and `ToString` are generated by the compiler. A `record` also generates a
`Deconstruct` method, so records can be destructured in patterns and variable
declarations.

**`record class` vs `record struct` (C# 10).** C# distinguishes between
reference-type records (`record class`, heap-allocated, nullable) and
value-type records (`record struct`, stack-allocated, not nullable). This split
is unique among mainstream languages — most pick one memory model for their data
types. The distinction matters for performance (avoiding heap allocations) and
for semantics (reference-type records can be null, value-type ones cannot).

```
record class Person(string Name, int Age);      // reference type, nullable
record struct Point(int X, int Y);              // value type, non-nullable
```

**Primary constructors.** The parameter list after the record name is a primary
constructor. The compiler generates public `init`-only properties for each
parameter. This is syntactically identical to Kotlin data classes and Scala
case classes — the convergence is striking.

**`with` expression.** Non-destructive mutation: `user with { Name = "New" }`
creates a copy of `user` where `Name` is changed and all other fields are
preserved. This is the same operation as Kotlin `copy()`, Scala `copy()`, and
Dart `copyWith`. C# embeds it as language syntax rather than a generated method,
which means it works uniformly on all records and anonymous types.

```
var updated = user with { Name = "Ada" };       // copy, change Name
var moved = point with { X = point.X + 10 };    // copy, change X
```

**`required` and `init`.** The `required` keyword on a property means it must
be set during construction. The `init` accessor means a property can be set
during object initialization but is read-only afterward. Together they create
immutable-by-default objects without forcing a constructor for every
combination:

```
class Config {
    public required string Host { get; init; }
    public required int Port { get; init; }
}
var c = new Config { Host = "localhost", Port = 5432 };
```

**Nomi relevance.** The `with` expression is the cleanest "copy with
modification" syntax across all languages surveyed. Nomi's `data` construct
should adopt it. The `record struct` vs `record class` distinction may be
premature for Nomi's first layer — most languages get by with one data model.

**Compare with:** Kotlin `data class` (similar, `copy()` method, `componentN()`
for destructuring), Swift `struct` (value type by default, no `with` but
`var`/`let` distinction on properties), Scala `case class` (similar, companion
object with `apply`/`unapply`, `copy()` method), Java `record` (simpler, no
`with`, no inheritance, canonical constructor is the only constructor).

### 3. LINQ and Expression-Driven Design

LINQ (Language Integrated Query, C# 3.0) is two things at once: a fluent API
for collection transformation, and a mechanism for capturing code as data
(expression trees). The second part is what makes it unusual — not just
syntactic sugar, but a metaprogramming system.

**Query syntax vs method syntax.** LINQ has two surface forms that compile to
the same thing:

```
// Query syntax (SQL-like):
var results = from u in users
              where u.IsActive
              orderby u.Name
              select u.Name;

// Method syntax (fluent/lambda):
var results = users.Where(u => u.IsActive)
                   .OrderBy(u => u.Name)
                   .Select(u => u.Name);
```

The query syntax is desugared into the method syntax by the compiler. This is a
classic desugaring pattern — the surface language is semantically identical to
the method-call form. Nomi could adopt a similar approach: design a readable
surface syntax that desugars to block/yield method chains.

**Expression trees.** When a lambda is assigned to `Expression<Func<T, R>>`
instead of `Func<T, R>>`, the compiler emits an AST representation of the
lambda body instead of IL. This AST can be inspected at runtime, translated to
SQL (Entity Framework), or compiled to a different target. This is a
compile-time metaprogramming mechanism that does not require macros or code
generation:

```
Expression<Func<User, bool>> filter = u => u.Age > 18;
// filter is now a tree: GreaterThan(MemberAccess("Age"), Constant(18))
```

**`IQueryable<T>`.** The separation of `IEnumerable<T>` (in-memory, eager tree)
from `IQueryable<T>` (query provider, lazy translation) means the same LINQ
methods work on in-memory collections and remote databases. The query provider
receives the expression tree and translates it to the target language (SQL,
OData, etc.).

**Deferred execution.** LINQ queries do not execute until the result is
enumerated. This is lazy evaluation: `users.Where(...).Select(...)` builds a
pipeline description. Iteration (or `.ToList()`) triggers execution. This is
the same model as Rust iterators, Kotlin sequences, and Java streams.

**Extension methods.** LINQ works because C# allows adding methods to existing
types via `static class` with `this` on the first parameter:

```
public static class StringExtensions {
    public static bool IsPalindrome(this string s) => s == new string(s.Reverse().ToArray());
}
```

This is a pragmatic alternative to monkey-patching or wrapper types. Extension
methods are resolved at compile time, statically dispatched, and scoped by
namespace imports. They enable the "fluent interface" style that LINQ depends
on.

**Nomi relevance.** Extension methods are feature Nomi needs. They let the
standard library grow without touching core types. Expression trees (code as
data) are too advanced for Nomi's first layer but represent a design direction
worth keeping open. Deferred execution / lazy pipelines align with Nomi's
block/yield model — blocks can produce sequences lazily.

**Compare with:** Kotlin sequences (`asSequence().map{}.filter{}`, same lazy
pipeline model), Rust iterators (zero-cost, lazy, `map`/`filter`/`collect`),
Swift trailing closures (similar fluent style but closures, not expression
trees), Elixir `Enum` (eager but `Stream` for lazy).

### 4. Null Safety and Nullable Reference Types (C# 8+)

C# took the unique approach of making null safety **opt-in per file** via
`#nullable enable`. This is fundamentally different from Kotlin (always on) and
Dart (sound, migration-based). The opt-in model was chosen because C# had 15+
years of nullable-by-default code that could not be broken.

**Nullable reference types.** With nullability enabled, `string` means
"non-null" and `string?` means "maybe null." The compiler performs flow
analysis to track null state across branches:

```
string? maybe = GetName();
if (maybe != null) {
    Console.WriteLine(maybe.Length);  // safe — maybe is known non-null here
}
```

**Null-forgiving operator.** `x!` suppresses the null warning. It says "I know
this looks nullable but trust me, it isn't." It is dangerous — a runtime
`NullReferenceException` if wrong — but necessary for interop with
non-annotated code. Every language with null safety has this operator (Kotlin
`!!`, Dart `!`, TypeScript `!`).

**Null-coalescing assignment.** `x ??= "default"` assigns `"default"` to `x`
only if `x` is null. Combined with `??` (coalesce) and `?.` (safe navigation),
C# has the full set of null-safety operators.

**Nomi relevance.** The opt-in model is a cautionary tale. Kotlin and Dart show
that sound, always-on null safety is better if you can do it from the start.
Nomi should have null safety baked in, not retrofitted. The `!` operator is
dangerous in every language — Nomi should require explicit handling (match,
unwrap, or default) rather than a bang operator.

**Compare with:** Kotlin `?`/`!!` (always on, platform types for Java interop),
Swift optionals (`?`/`!`, `if let`, `guard let`, `??`), Dart NNBD (sound,
migration-based, `?`/`!`/`??`/`?.`), TypeScript strict null checks (opt-in,
`?`/`!`/`??`/`?.`), Rust `Option<T>` (no null at all, `None` is a variant).

### 5. Async/Await and Tasks

C#'s async model (C# 5, 2012) was the blueprint that JavaScript, Python, Swift,
Rust, and Dart later followed. It is a cooperative, task-based model built on
top of a thread pool.

**`Task<T>` / `ValueTask<T>`.** These are the async work representations. A
`Task<T>` is a future/promise that will eventually produce a `T`. `ValueTask<T>`
is a stack-allocated alternative for cases where the result is often synchronous
(avoids heap allocation). The split between `Task` and `ValueTask` is an
optimization — most languages use a single Future/Promise type.

**`async`/`await`.** Methods marked `async` can use `await` to suspend until a
task completes. The compiler rewrites the method into a state machine.
`ConfigureAwait(false)` avoids capturing the synchronization context, which
prevents deadlocks in library code — a C#-specific wart that other languages
mostly avoided.

**`IAsyncEnumerable<T>` and `await foreach` (C# 8).** Async iteration: produce
a stream of values over time, consuming them with `await foreach`. This is the
async analog of `IEnumerable<T>`:

```
await foreach (var item in GetItemsAsync()) {
    Process(item);
}
```

**Structured concurrency (partial).** `Task.WhenAll` waits for all tasks to
complete. `Task.WhenAny` waits for the first. These are primitives for
structured concurrency but they are library methods, not language constructs.
C# does not enforce structured concurrency the way Swift and Kotlin do — you can
fire-and-forget a task, and orphaned work is a known problem.

**Nomi relevance.** C# shows both the power and the cost of `async`/`await`:
the function coloring problem (async functions can only be called from async
functions), the state machine overhead, and the accident of fire-and-forget.
Nomi's block/yield model is a different approach to the same problem — blocks
can suspend and resume without coloring. The `ValueTask`/`Task` split shows
that async work representation matters for performance; Nomi should think
carefully about what its equivalent is.

**Compare with:** Kotlin coroutines (suspend functions, structured concurrency
via `coroutineScope`, no function coloring within suspend context), Swift
async/await (actor-based, structured concurrency with `TaskGroup`, `async let`),
Rust async (zero-cost, no runtime, `Future` trait, executor pluggable), Go
goroutines (preemptive-ish, channels for communication, no await keyword).

---

## Java

Java's modernization has been slower and more deliberate than C#'s, but the
trajectory is similar. Records, sealed classes, pattern matching, and virtual
threads form a coherent vision: make data and control flow explicit, and make
concurrency cheap.

### 1. Records (Java 14-16)

Java records are the most minimal of all the "data class" implementations.
Where Kotlin, Scala, and C# add features (copy methods, destructuring,
companion objects), Java strips back to the absolute minimum: a record is a
transparent, shallowly-immutable data carrier.

```
record Point(int x, int y) {}
```

This generates: a canonical constructor, accessor methods (`x()`, `y()`),
`equals`, `hashCode`, and `toString`. That is the complete feature set. No
`copy` method, no `with` expression, no destructuring in variable declarations
(though record patterns in `switch` cover destructuring in case labels).

**Compact constructor.** The only customization point: you can write a
constructor that omits the parameter list and the field assignments. The
compiler appends the field assignments after your code:

```
record PositivePoint(int x, int y) {
    PositivePoint {                      // compact constructor — no parameter list
        if (x < 0 || y < 0) throw new IllegalArgumentException("must be positive");
    }
}
```

**Restrictions.** Records are implicitly `final` (cannot be extended). They
cannot extend other classes (they implicitly extend `java.lang.Record`). They
can implement interfaces. Fields are always `private final`. These restrictions
are intentional — a record is a pure data aggregate, not a general-purpose
class.

**Nomi relevance.** Java's minimalism is instructive. Not every data feature
needs to be in the language — you can add `copy`/`with` later as a library or a
subsequent language version. The compact constructor pattern (validate, then let
the compiler do the assignments) is cleaner than writing a full constructor by
hand. Nomi's `data` construct should support validation at construction time.

**Compare with:** C# `record` (more feature-rich: `with`, primary constructors
on non-records, `record struct`), Kotlin `data class` (`copy()`, `componentN()`,
can be mutable via `var`), Scala `case class` (most feature-rich: `copy()`,
`apply`/`unapply`, pattern matching, serializable), Dart records (anonymous,
structural, not nominal).

### 2. Sealed Classes and Pattern Matching (Java 17-21)

Java's pattern matching story is built on sealed class hierarchies.
Exhaustiveness is the goal — the compiler must verify that a `switch` covers
every possible subtype — and sealed classes are the mechanism.

**Sealed classes (Java 17).** A sealed class or interface explicitly lists the
types that may extend it:

```
sealed interface Shape permits Circle, Rectangle, Triangle {}
record Circle(double radius) implements Shape {}
record Rectangle(double width, double height) implements Shape {}
record Triangle(double base, double height) implements Shape {}
```

The compiler now knows that any `Shape` must be one of `Circle`, `Rectangle`, or
`Triangle`. This is the exhaustiveness foundation.

**Switch pattern matching (Java 17 preview, 21 final).** With sealed types,
`switch` can match on the concrete type and destructure in one step:

```
double area(Shape s) {
    return switch (s) {
        case Circle(var r) -> Math.PI * r * r;
        case Rectangle(var w, var h) -> w * h;
        case Triangle(var b, var h) -> 0.5 * b * h;
        // no default needed — sealed hierarchy makes this exhaustive
    };
}
```

This is essentially ML-style algebraic data types built from OO primitives. The
`sealed interface` is the sum type; the `record` implementations are the product
types; `switch` is the case analysis. The compiler guarantees no case is missed.

**Guards (`when` clause).** Java uses `when` for guards (identical to C#'s
`when`, different from Kotlin's `if` and Scala's `if`):

```
case User(var name) when name.length() > 0 -> "named user: " + name;
case User(var name) -> "empty name";  // fallthrough for empty names
```

Guards make patterns precise without requiring nested conditionals. When a guard
fails, matching falls through to the next case (same behavior as all languages
with guards).

**Record patterns (Java 19).** Records can be destructured in case labels:

```
case Pair(Pair(var a, var b), var c) -> a + b + c;
```

This is nested destructuring — the same as Rust `match`, Swift `switch`, and C#
positional patterns.

**Switch expressions (Java 14).** Java's `switch` gained an expression form
with arrow syntax: `case 1 -> "one"`. The expression form requires
exhaustiveness (all values covered or a `default`). No fallthrough in arrow
form — this eliminates a major source of bugs from C/Java's traditional
fallthrough `switch`.

**Nomi relevance.** Java's path shows how sealed + pattern matching can be
adopted incrementally. Sealed classes came first (Java 17), then record patterns
(Java 19), then full switch pattern matching (Java 21). Each step is useful on
its own. Nomi should design for this trajectory — sealed type hierarchies for
exhaustiveness, then pattern matching as the natural way to inspect them.
Expression-switch with mandatory exhaustiveness should be Nomi's primary
conditional for variant types.

**Compare with:** Kotlin `sealed class`/`sealed interface` + `when` (smart
casts, expression form, exhaustiveness), Rust `enum` + `match` (always
exhaustive, always expression), Swift `enum` with associated values + `switch`
(exhaustive, `let` binding), Scala `sealed` + `match` (exhaustiveness
warnings, extractors via `unapply`).

### 3. Virtual Threads (Java 21 — Project Loom)

Virtual threads are Java's answer to the "million concurrent tasks" problem.
They are lightweight, user-mode threads managed by the JVM, not the OS.

**Lightweight concurrency.** A virtual thread consumes ~200-300 bytes when
blocked (vs ~2MB for a platform thread's stack). This means you can have
millions of virtual threads on a single JVM. When a virtual thread blocks on
I/O, the JVM unmounts it from the carrier thread and mounts another virtual
thread — the OS thread is never idle waiting for I/O.

```
Thread.startVirtualThread(() -> {
    // runs in a virtual thread
});
```

**Programming model unchanged.** Code written for platform threads works
unchanged on virtual threads. `synchronized`, `wait`, `notify`, `ThreadLocal` —
all the old APIs work. This is the key design choice: virtual threads do not
require a new programming model (unlike callbacks, futures, or coroutines).
They make the thread-per-request model scalable without changing how you write
the request handler.

**Structured concurrency (preview).** `StructuredTaskScope` enforces that
subtasks complete within their parent scope. If the scope exits, all subtasks
are cancelled. This prevents orphaned work — the same goal as Kotlin's
`coroutineScope` and Swift's `TaskGroup`:

```
try (var scope = new StructuredTaskScope.ShutdownOnFailure()) {
    Future<String> user = scope.fork(() -> fetchUser());
    Future<Order> order = scope.fork(() -> fetchOrder());
    scope.join();
    scope.throwIfFailed();
    return new Response(user.resultNow(), order.resultNow());
}
// both subtasks are guaranteed done (or cancelled) here
```

**`ScopedValue` (preview).** A replacement for `ThreadLocal` that is immutable,
scoped, and inheritable by child threads. It avoids the memory-leak and
composability problems of `ThreadLocal`:

```
ScopedValue.where(USER, currentUser).run(() -> {
    var user = ScopedValue.get(USER);  // available in this scope and children
});
```

**Nomi relevance.** Virtual threads demonstrate that lightweight concurrency
does not require `async`/`await` — a runtime can make blocking cheap instead of
making blocking forbidden. Nomi's block/yield model sits somewhere between
virtual threads (blocking is fine) and coroutines (suspension is explicit).
`StructuredTaskScope` is the model for structured concurrency that Nomi should
study — tasks have a parent scope, and leaving the scope means all children are
done.

**Compare with:** Go goroutines (M:N scheduling, channels, `select`, `defer`),
Erlang processes (actor model, message passing, supervision trees, preemptive),
Kotlin coroutines (suspension points, structured concurrency via
`coroutineScope`), Swift structured concurrency (`TaskGroup`, `async let`,
actor-based isolation).

### 4. Other Modern Features

**Text blocks (Java 15).** Multi-line string literals using triple quotes.
Incidental whitespace is stripped based on the closing delimiter's indentation.
Interpolation is not built-in (unlike C# `$"..."`, Kotlin `"$x"`, Dart
`"$x"`). This is a surprisingly conservative choice — Java treats strings as
pure data and leaves formatting to `String.formatted()`.

```
String json = """
    {
        "name": "Ada",
        "age": 30
    }
    """;
```

**`var` (Java 10).** Local variable type inference. Limited to local variables
with initializers — cannot be used for fields, parameters, or return types. This
is conservative compared to C# `var`, Kotlin `val`/`var`, and Scala `val`/`var`.
The restriction to locals keeps type inference tractable and error messages
clear.

**`Optional<T>` (Java 8).** A container that may or may not hold a value.
Limited compared to `Option` in Rust/Scala/Swift — no pattern matching on it,
no `map`/`flatMap`/`filter` as instance methods until later versions. Java
discourages using `Optional` for fields or parameters; it is primarily a return
type. This is a half-measure compared to true null safety.

**`Stream<T>` (Java 8).** Lazy collection pipeline: `filter`, `map`,
`flatMap`, `collect`. Similar to C# LINQ (method syntax) and Kotlin sequences.
No expression tree equivalent — streams are always in-memory or backed by a
custom `Spliterator`. The `collect` terminal operation with `Collectors` is
powerful but verbose.

**Nomi relevance.** Text blocks are table stakes — every modern language needs
multi-line strings with clean indentation handling. `var`/type inference is a
usability feature that Nomi should consider carefully: inference reduces
ceremony but too much inference hurts readability. `Optional` as a half-measure
is a warning — if Nomi wants null safety, it should be sound and pervasive, not
a library type.

**Compare with:** C# LINQ (method syntax identical, query syntax extra,
expression trees for translation), Kotlin sequences (same lazy model, more
concise due to `it` and trailing lambda syntax), Rust iterators (zero-cost
abstraction, `iter()`/`into_iter()`, `collect()` is type-inferred).

---

## Dart

Dart is the newest of the three and the only one that designed null safety into
the type system from a point of full migration. Its pattern matching (3.0) and
records (3.0) are the most recently shipped of any language surveyed here,
making Dart a useful "what did the latest iteration learn?" data point.

### 1. Null Safety (NNBD — Dart 2.12+)

Dart's null safety is **sound** — the type system guarantees that a non-nullable
variable is never null at runtime. This is stronger than TypeScript (which is
unsound by design) and C# (which is flow-analysis-based with escape hatches).
Only Kotlin and Swift match Dart's level of soundness.

**Nullable and non-nullable types.** `String` means "this is always a string."
`String?` means "this might be null." The compiler enforces the distinction.
This is the same surface syntax as Kotlin, Swift, and TypeScript — the `?`
postfix for nullability has become the universal convention.

```
String name = "Ada";        // non-nullable — can never be null
String? maybe = null;       // nullable — must be checked before use
```

**Type promotion.** Dart's flow analysis narrows types after null checks.
After `if (maybe != null)`, the variable is promoted to non-nullable `String`
within the then-branch. This works across `if`, `assert`, and early returns:

```
if (maybe == null) return;
print(maybe.length);  // maybe is promoted to String here
```

**Null safety operators.** `?.` (safe navigation), `??` (if-null coalesce),
`??=` (if-null assignment), `!` (null assertion — throws if null). The `!`
operator is the same dangerous escape hatch found in every language. Dart also
has `?..` (null-aware cascade) and `?[]` (null-aware index).

**`late` variables.** A `late` variable is non-nullable but initialized after
declaration. The compiler trusts the programmer — accessing a `late` variable
before initialization throws at runtime. This is a pragmatic compromise: not all
initialization fits into a constructor, and `late` avoids forcing the variable
to be nullable.

```
late String name;           // will be initialized before use
name = "Ada";               // initialization
print(name.length);         // safe — name is non-nullable
```

**Migration story.** Dart's null safety was rolled out via a migration tool
(`dart migrate`) that analyzed code, added `?` annotations, and suggested where
`!` assertions were needed. Packages declared null safety opt-in, and the
ecosystem migrated over ~2 years. This is the cleanest null-safety migration in
the industry — cleaner than TypeScript (still unsound), C# (still opt-in), or
Kotlin (Java interop is perennially unsafe).

**Nomi relevance.** Dart proves that sound null safety can be added to an
existing language with an existing ecosystem, and that the result is worth the
migration pain. Nomi should bake null safety in from the start — there is no
excuse for a new language in 2024+ to be null-unsafe. The `late` pattern is
useful — Nomi should consider a way to declare "initialized later but
non-nullable" without forcing Option wrapping.

**Compare with:** Kotlin null safety (always on, sound within Kotlin, platform
types for Java interop, `?`/`!!`/`?.`/`?:`), Swift optionals (`?`/`!`, `if
let`, `guard let`, `??`, optional chaining), TypeScript strict null checks
(opt-in, unsound at module boundaries, `?`/`!`/`??`/`?.`), Rust `Option<T>`
(no null in the language, `None` is a variant, `unwrap()` is the assertion).

### 2. Pattern Matching (Dart 3.0+)

Dart 3.0 (May 2023) shipped pattern matching as a unified feature across
`switch`, variable declarations, and destructuring assignments. Dart's approach
is notable for making patterns a first-class concept that appears in multiple
syntactic positions, not just `switch`.

**Switch expression with exhaustiveness.** Like Java 21 and C# 8, Dart's
`switch` can be an expression that produces a value. The compiler checks
exhaustiveness on sealed types:

```
String describe(Shape s) => switch (s) {
    Circle(:var radius) => 'Circle with radius $radius',
    Rectangle(:var width, :var height) => 'Rectangle ${width}x$height',
  };
```

No `default` needed when the sealed hierarchy is fully covered. The `:var name`
syntax for named-field destructuring is a Dart innovation — it reads as "the
field named `radius`, bound to variable `radius`."

**Destructuring in variable declarations.** Patterns work in `var` and `final`
declarations, not just `switch`:

```
var (a, b) = pair;                  // destructure a record
var (:name, :age) = person;         // destructure named fields
var [first, ...rest] = list;        // destructure a list
```

This means patterns are a general-purpose binding mechanism, not just a match
construct. It is the same unification seen in Rust (`let (x, y) = pair`) and
Swift (`let (x, y) = pair`).

**Record types as patterns.** Dart records `(int, String)` are both types and
patterns — constructing them and destructuring them use the same syntax. This is
elegant: the language does not need separate "record literal" and "record
pattern" syntax.

```
(int, String) pair = (1, "hello");      // construction
var (num, text) = pair;                 // destructuring — num=1, text="hello"
```

**`sealed` classes for exhaustiveness.** Like Java, Dart uses `sealed` on
classes to restrict the subtype hierarchy. The compiler enforces that all
subtypes are in the same library. Combined with `switch` expressions, this
gives exhaustiveness checking without requiring a separate enum/sum-type
construct:

```
sealed class Result {}
class Success extends Result { final dynamic value; ... }
class Failure extends Result { final String error; ... }
```

**Nomi relevance.** Dart's unification of patterns across `switch`, `var`, and
assignment is the right model. Patterns should not be a special syntax confined
to `match` — they should be the language's general mechanism for binding and
destructuring. The Dart `:var name` syntax for named fields is worth comparing
with JavaScript's `{ name }` and Rust's `Struct { name }` syntax when designing
Nomi's pattern syntax.

**Compare with:** Swift patterns (in `switch`, `if case`, `for case`, `let`
bindings, `case let` syntax), Kotlin `when` (destructuring in `when` via
`componentN()`, not general patterns), Rust `match` + `if let` + `let`
destructuring (unified across all three positions, `ref`/`ref mut` for binding
mode).

### 3. Records and Data (Dart 3.0+)

Dart has two distinct "data" constructs: record types (anonymous, structural)
and classes with `sealed`/`final` modifiers (nominal, with behavior). This
two-tier approach is unique among the surveyed languages.

**Record types.** Anonymous, structurally-typed tuples with optional named
fields:

```
(int, String) pair = (1, "hello");              // positional record
({int x, int y}) point = (x: 10, y: 20);       // named record
(int, {String name}) hybrid = (1, name: "Ada"); // mixed positional and named
```

Records have structural equality — two records are equal if they have the same
shape and all fields are equal. They are ideal for ad-hoc data: return multiple
values from a function, pass a pair of values, represent a point without
defining a class. They are essentially "tuples with field names."

**Classes with modifiers.** Dart classes can be `sealed` (subtypes restricted to
the same library), `final` (no subclassing at all), `base` (subclassing allowed
but implementation outside the library prohibited), or `interface` (only
interface implementation, no extension). These modifiers give library authors
control over the subtype hierarchy.

**No `copy`/`with` on records.** Dart records do not have a built-in copy
mechanism, unlike C# (`with`) or Kotlin/Scala (`copy()`). For classes, Dart
developers write `copyWith` methods by hand. This is a gap — the language has
the pattern matching to destructure records but no concise syntax for
"take this record and change one field."

**`sealed` for exhaustiveness.** The `sealed` modifier on classes is the bridge
between OO inheritance and functional exhaustiveness. It transforms a class
hierarchy into a closed set of cases that the compiler can check. This is the
same pattern as Java 17's `sealed` and Kotlin's `sealed class`.

**Nomi relevance.** Dart's split between anonymous records and nominal classes
is an interesting design choice. For Nomi, a unified `data` construct that
covers both cases (named data with optional behavior) is likely better than
forcing a choice between "throwaway tuple" and "full class." Dart's lack of a
`with` expression on records is a noticeable ergonomic gap — Nomi should design
`with` from the start.

**Compare with:** Java records (nominal only, no anonymous records/tuples, no
`with`/`copy`), C# records (nominal, `with` expression, positional construction
via primary constructor), Kotlin data classes (nominal, `copy()` method,
`componentN()` for destructuring).

### 4. Extension Types / Extension Methods

Dart has a two-tier extension system: extension methods (Dart 2.7, lightweight
syntax sugar) and extension types (Dart 3, zero-cost wrappers with stronger
encapsulation).

**Extension methods (Dart 2.7).** Add methods to existing types without
modifying the type or creating a subclass:

```
extension StringX on String {
  bool get isPalindrome => this == split('').reversed.join('');
}
// usage: "racecar".isPalindrome → true
```

Extension methods are resolved statically — there is no dynamic dispatch on the
extension receiver. This avoids the complexity of monkey-patching (Ruby) or
protocol extensions with retroactive conformance conflicts (Swift).

**Extension types (Dart 3).** A zero-cost wrapper type that allows adding an
interface to an existing type without heap allocation. The wrapper is erased at
compile time — it exists only in the static type system, not at runtime:

```
extension type UserId(int id) {
  bool get isValid => id > 0;
}
// UserId and int are the same value at runtime, but the type system
// prevents accidentally passing an int where a UserId is expected.
```

This is similar to Haskell's `newtype` and Rust's newtype pattern — compile-time
type safety with zero runtime cost.

**Nomi relevance.** Extension methods are essential for Nomi's design. They
allow the standard library to grow without modifying core types, and they enable
fluent-style method chaining on built-in types. Extension types (zero-cost
wrappers) are a more advanced feature that Nomi could defer but should keep in
mind as a mechanism for type-safe newtypes.

**Compare with:** Kotlin extensions (extension functions and properties, static
dispatch, scoped by import), C# extension methods (`static class` + `this`
parameter, static dispatch), Swift extensions (add methods, computed
properties, protocol conformances — more powerful due to protocol retroactive
conformance).

### 5. Async Model

Dart's async model is the same `Future`/`async`/`await` pattern as JavaScript
and C#, but with one important architectural difference: isolates for
parallelism.

**`Future<T>` + `async`/`await`.** Single-threaded event loop (like
JavaScript). `Future<T>` is a promise-like value that completes asynchronously.
`async` functions return `Future<T>`. `await` suspends until the future
completes:

```
Future<String> fetchName() async {
  var response = await http.get(url);
  return response.body;
}
```

**`Stream<T>` and `await for`.** Async iterables. A `Stream<T>` produces a
sequence of values over time. `await for` consumes them in order:

```
await for (var event in eventStream) {
  print('Received: $event');
}
```

This is the same model as C#'s `IAsyncEnumerable<T>` + `await foreach`.

**Isolates.** Dart's answer to parallelism. An isolate is a separate heap with
its own event loop. Isolates communicate via message passing (ports). No shared
memory — this eliminates data races by construction. Spawning an isolate is
similar to Web Workers in JavaScript or `multiprocessing` in Python:

```
var isolate = await Isolate.spawn(workerFunction, message);
```

**Nomi relevance.** Dart's event-loop model is simpler than C#'s thread-pool
model but limits parallelism to isolates. Nomi's block/yield approach should
study isolates as a model for parallel, non-shared-memory computation. The
`Stream` + `await for` pattern is analogous to Nomi's block yielding — a block
can produce a stream of values, and the caller can iterate with a yield/receive
model.

**Compare with:** JavaScript `Promise`/`async`/`await` (single-thread event
loop, Web Workers for parallelism, same model as Dart), C# `Task<T>`/`async`
/`await` (thread-pool-based, `IAsyncEnumerable<T>` for streams), Kotlin
coroutines (suspend functions, `Flow<T>` for streams, structured concurrency).

---

## Cross-Language Synthesis

### Records/Data Classes — The Convergence

Every major language has converged on some form of "named field bag with value
semantics." The convergence is striking because the languages started from
different paradigms (OO, functional, multi-paradigm) and arrived at similar
solutions within a few years of each other.

**What is structurally the same across all languages:**

| Feature | C# | Java | Kotlin | Scala | Dart | Swift | Rust |
|---------|----|----|------|--------|-------|-------|------|
| Named fields | Yes | Yes | Yes | Yes | Named records yes | Yes | Yes |
| Value equality | Yes | Yes | Yes | Yes | Yes (records) | Yes | Opt-in derive |
| Copy-with-modify | `with` expr | No | `copy()` | `copy()` | No (manual) | `var` mutation | Struct update syntax |
| Immutable by default | Init-only | Yes | val/var choice | val/var choice | Fields mutable | let/var choice | let/var choice |
| Destructuring | Deconstruct | Record patterns | componentN() | unapply | Pattern match | Pattern match | Pattern match |
| Validation at construction | Init/set | Compact ctor | init block | require | Assert in body | init / guard | No built-in |
| Anonymous/structural option | Anonymous types | No | No | Tuples | Records (anon) | Tuples | Tuples |

**What is different:**

1. **Reference vs value type.** C# is the only language that splits records
   into `record class` (reference type, heap) and `record struct` (value type,
   stack). Every other language picks one memory model for data.

2. **Mutability defaults.** Java records are always immutable. Kotlin and Scala
   let you choose `val` vs `var` per field. Dart records are always immutable
   (positional fields), but class fields are mutable by default. C# records are
   immutable by convention (`init`-only) but support `set`.

3. **Nominal vs structural.** Java, C#, Kotlin, and Scala records are nominal —
   two records with the same fields but different names are different types.
   Dart records are structural — `(int, String)` is a type, and any two such
   records are the same type. This is the biggest philosophical split in the
   data-class design space.

4. **Validation during construction.** Java has the compact constructor — the
   cleanest validation story. C# has `init` with validation in the accessor
   body. Kotlin and Scala use `init` blocks. Dart has no built-in validation
   for records.

### Pattern Matching — The Convergence

Pattern matching features are converging across languages. The same feature set
appears in C#, Java, Dart, Kotlin, Swift, and Rust, though the syntax and the
completeness guarantees vary.

| Feature | C# | Java 21 | Dart 3 | Kotlin | Swift | Rust |
|---------|----|----|------|--------|-------|------|
| Type test + bind | `x is int i` | `case int i` | `case int i` | `is Int` + smart cast | `case let i as Int` | `i32` in match |
| Property/field patterns | `{Name: "A"}` | Record deconstruct | `:var name` | Destructure in when | Enum assoc values | Struct destructure |
| Guards | `when` | `when` | `when` | `if` | `where` | `if` |
| Exhaustiveness | Analyzer | Compiler (sealed) | Compiler (sealed) | Compiler (sealed) | Compiler (enum) | Compiler (always) |
| Expression form | switch expr | switch expr | switch expr | when expr | N/A (statement) | match expr |
| List/array patterns | `[1, .. var r]` | No | `[first, ...rest]` | No | No | `[first, ..]` on slices |
| OR patterns | `and`/`or` | No | `\|` | `,` (comma) | `,` (comma) | `\|` |
| Variable binding in patterns | `var x` | `var x` | `var x` | Destructure only | `let x` | `x` (implicit) |

**Key observations:**

- **Exhaustiveness is the killer feature.** Every language now ties pattern
  matching to sealed/closed type hierarchies to get compiler-verified
  exhaustiveness. This single feature eliminates an entire class of bugs
  (forgotten cases) and enables safe refactoring (add a variant, the compiler
  finds all incomplete matches).

- **Everyone converged on `when` for guards.** C#, Java, and Dart all use
  `when`. Kotlin uses `if`, Swift uses `where`, Rust uses `if`. The keyword
  varies but the semantics are identical: an additional boolean condition that
  must be true for the case to match.

- **Expression form is universal.** Every language now has `switch`/`match` as
  a value-producing expression. This is a dramatic shift from the C tradition of
  `switch` as a jump table. The reason is clear: when you match on variants,
  you almost always want to produce a value.

- **Destructuring is moving out of `switch` and into variable declarations.**
  Dart, Rust, and Swift all support patterns in `let`/`var` declarations. C#
  supports deconstruction via `Deconstruct`. Java is the holdout — destructuring
  is confined to `case` labels. The direction is clear: patterns should be the
  language's general binding mechanism, not just a match feature.

### Null Safety — The Convergence

Kotlin, Swift, Dart, TypeScript, and C# 8+ have all converged on the same
surface syntax for null safety. The differences are in soundness guarantees
and opt-in vs opt-out.

| Feature | Kotlin | Swift | Dart | TypeScript | C# 8+ |
|---------|--------|-------|------|------------|-------|
| Nullable syntax | `T?` | `T?` | `T?` | `T \| null` | `T?` |
| Safe navigation | `?.` | `?.` (optional chaining) | `?.` | `?.` | `?.` |
| Coalesce | `?:` | `??` | `??` | `??` | `??` |
| Assert non-null | `!!` | `!` (force unwrap) | `!` | `!` | `!` |
| Soundness | Yes | Yes | Yes | No | Partial |
| Opt-in or always on | Always on (except Java interop) | Always on | Migration-based, now always on | Opt-in (`strictNullChecks`) | Opt-in per file |
| Late init | `lateinit` | `!` IUO | `late` | `!` (definite assignment assertion) | Null-forgiving |
| Map/flatMap on nullable | Extension functions | `map`/`flatMap` | `map` on `?` | No | Via LINQ |
| `if let` / flow narrowing | Smart cast | `if let` / `guard let` | Type promotion | Type guard narrowing | Flow analysis |

**Key observations:**

- **`T?` is the universal syntax.** Every language uses the postfix `?` to
  denote nullable types. This is one of the strongest convergences in
  programming language design of the last decade.

- **Sound vs unsound is the real dividing line.** TypeScript's null safety is
  unsound by design (for interop with JavaScript). C#'s is partially sound
  (flow-analysis-based, escape hatches). Kotlin, Swift, and Dart are sound
  (the compiler guarantees no null dereference in safe code). Soundness is
  expensive (requires a migration, breaks interop) but pays off in reliability.

- **The `!` operator is dangerous everywhere.** Every language has a
  "trust me, it's not null" operator. Every language documents it as dangerous.
  Every language has bugs caused by misuse. Nomi should consider whether to
  include this operator at all or require explicit handling (match, unwrap with
  default, propagate).

- **Flow analysis / narrowing is the ergonomic key.** The difference between
  tolerable null safety and frustrating null safety is whether the compiler
  understands control flow. After `if (x != null)`, the variable should be
  non-nullable inside the branch. Kotlin's smart casts, Swift's optional
  binding, Dart's type promotion, and C#'s flow analysis all achieve this.
  Without flow narrowing, null safety requires a cascade of `!!` assertions.

---

## What Nomi Should Learn

### Adopt

**Sealed/closed type hierarchies for exhaustiveness.** All three languages
(C#, Java, Dart) have converged on this pattern. A `data` type hierarchy that is
explicitly closed lets the compiler check that every case is handled. Nomi
should design `data` as a closed hierarchy from the start, not as open classes
with a sealed modifier added later.

**Expression-switch/match as the primary conditional for variants.** Nomi
should make `match` an expression (produces a value) with mandatory
exhaustiveness on sealed types. This is the single highest-leverage design
decision in the pattern matching space. Every language that added it later had
to work around the legacy of statement-switch.

**Records with value semantics.** Nomi's `data` construct (already in the
design) should provide structural equality, destructuring, and `with`-style copy
from day one. The convergence is clear: every major language has this feature,
and the ergonomics of `with` (copy with modification) are too important to defer
to a library method.

**Extension methods.** C#, Kotlin, Swift, and Dart all have extension methods.
They enable fluent APIs, reduce the need for utility classes, and let the
standard library grow without modifying core types. Nomi should design for
extension methods early — the syntax details can be deferred, but the semantic
model (static dispatch, scoped by import) should be committed.

**`with` expression for data copy.** C#'s `with` expression is the cleanest
"copy with modification" syntax across all languages. It reads as a declarative
specification of what changed, not a procedural sequence of field assignments.
Nomi should adopt this syntax for all `data` types.

### Refuse/Defer

**`async`/`await` as language keywords.** Nomi's block/yield model is a
different approach to asynchronous control flow. Adding `async`/`await` would
create two competing concurrency models. The block protocol (suspend, resume,
yield values) is more general — it subsumes async iteration and generators
without function coloring.

**`!` / `!!` null assertions.** The null assertion operator is the single most
dangerous feature in every language that has it. Nomi should require explicit
null handling: match on `Some`/`None`, provide a default (`??`), or propagate
(`?` in a chain). A bang operator that says "trust me, crash if I'm wrong" is
not consistent with Nomi's design values of local reasoning and inspectable
reduction.

**LINQ-style expression trees.** Expression trees (capturing lambda bodies as
AST at compile time) are extremely powerful but introduce metaprogramming
complexity that is inappropriate for Nomi's first layer. The pipeline pattern
(`data | filter | map | collect`) can be achieved with regular functions and
blocks. Expression trees can be considered later as an optimization or a
compile-time feature.

**Virtual threads / lightweight processes.** Java's virtual threads and Go's
goroutines are solutions to the C10k problem. Nomi's block policy model
(controlled suspension, structured concurrency) should handle this at the
language level. Deferring to the runtime for lightweight concurrency is
reasonable, but it should not be a core language feature on day one.

### Adapt

**C# positioned records as "data with value semantics."** This exactly matches
Nomi's `data` construct concept. The C# design shows that records work well when
they are: (1) value-equal by default, (2) immutable by convention, (3) have
a concise construction syntax, and (4) support `with`-style non-destructive
mutation.

**Java's incremental path: sealed first, then pattern matching, then
exhaustiveness.** Nomi does not need to ship the full pattern matching suite on
day one. A sealed `data` hierarchy with destructuring in `match` is enough for
the first release. Recording patterns (destructuring in variable declarations),
nested patterns, and OR patterns can follow. The key is to design the syntax so
that these extensions are additive, not breaking.

**Dart's sound null safety migration shows it can be done.** Dart proved that
an existing language with millions of lines of code can migrate to sound null
safety. Nomi, as a new language, has no excuse — null safety should be baked
into the type system from commit zero. The `late` pattern (non-nullable but
initialized after declaration) is worth adopting.

**C# `with` expression is the cleanest copy-with-modify syntax.** Every
language has a copy mechanism: Kotlin `copy()`, Scala `copy()`, Dart manual
`copyWith`. C# is the only one that made it a language expression rather than a
generated method. The expression form (`user with { Name = "New" }`) is more
readable, more declarative, and works uniformly on all data types without
requiring code generation for each type.

---

## Comparison Tables

### 1. Records/Data Classes Across Languages

| Feature | C# record | Java record | Kotlin data class | Scala case class | Dart record | Swift struct | Rust struct | Nomi (target) |
|---------|-----------|-------------|-------------------|------------------|-------------|-------------|-------------|--------------|
| Structural equality | Yes (generated) | Yes (generated) | Yes (generated) | Yes (generated) | Yes (records) | No (by default) | Opt-in (derive) | Yes |
| `with`/copy | `with { }` expr | No | `copy()` method | `copy()` method | Manual | Mutate via `var` | Struct update syntax | `with { }` expr |
| Immutable by default | Init-only (convention) | Yes | Choice (val/var) | Choice (val/var) | Yes (records) | Choice (let/var) | Choice (let/mut) | Yes |
| Primary constructor | Yes | Yes | Yes | Yes | N/A (anonymous) | Implicit memberwise init | No (convention) | Yes |
| Destructuring | Deconstruct method | Record patterns | componentN() | unapply / patterns | Pattern matching | Pattern matching | Pattern matching | Pattern matching |
| Nominal vs structural | Nominal | Nominal | Nominal | Nominal | Structural | Nominal | Nominal | Nominal |
| Validation at construction | Init/set body | Compact constructor | init block | require / assert | None | init / guard | Convention (new) | Compact validation |
| Reference or value type | Both (record class/struct) | Reference | Reference | Reference | N/A | Value | Value (default) | TBD |
| Can extend other types | Yes (classes) | No (implicitly final) | Yes (open by default) | Yes (open by default) | N/A (anonymous) | No (protocols only) | No (traits only) | TBD |

### 2. Pattern Matching Feature Matrix (C# / Java / Dart)

| Feature | C# | Java 21 | Dart 3.0 |
|---------|----|----|------|
| Type test + binding | `x is int i` | `case int i ->` | `case int i =>` |
| Property/field patterns | `{ Name: "A", Age: > 30 }` | Record deconstruct only | `:var name` in switch |
| Nested patterns | Yes (recursive) | Yes (record patterns) | Yes (recursive) |
| Guards | `when` clause | `when` clause | `when` clause |
| OR patterns | `or` combinator | No | `\|` combinator |
| AND patterns | `and` combinator | No | No |
| NOT patterns | `not` combinator | No | No |
| Relational patterns | `> 0 and < 10` | No (use guard) | `<`, `>`, `<=`, `>=` |
| List/slice patterns | `[1, .. var r, 5]` | No | `[first, ...rest]` |
| Exhaustiveness | Analyzer-driven | Compiler (sealed) | Compiler (sealed) |
| Switch as expression | Yes (`=>`) | Yes (`->`) | Yes (`=>`) |
| Patterns in var decls | Deconstruct only | No | Yes (`var (a, b) =`) |
| Var binding syntax | `var x` in pattern | `var x` in record pattern | `var x` or `:var x` |
| Discard/wildcard | `_` | `_` in record patterns | `_` (wildcard) |

### 3. Null Safety Comparison

| Feature | Kotlin | Swift | Dart | TypeScript | C# 8+ |
|---------|--------|-------|------|------------|-------|
| Nullable syntax | `T?` | `T?` (Optional) | `T?` | `T \| null` / `T?` | `T?` |
| Non-null syntax | `T` | `T` | `T` | `T` | `T` |
| Safe navigation | `?.` | `?.` | `?.` | `?.` | `?.` |
| Coalesce | `?:` | `??` | `??` | `??` | `??` |
| Coalescing assignment | No | No | `??=` | `??=` | `??=` |
| Assert non-null | `!!` | `!` | `!` | `!` | `!` |
| Flow narrowing | Smart casts | `if let` / `guard let` | Type promotion | Type guards | Flow analysis |
| Map on optional | Extension fns | `map` / `flatMap` | Extension methods | No | Extension methods |
| Soundness | Yes (except Java interop) | Yes | Yes | No (by design) | Partial |
| Always-on vs opt-in | Always on | Always on | Always on (post-migration) | Opt-in (`strictNullChecks`) | Opt-in per file (`#nullable enable`) |
| Late initialization | `lateinit var` | Implicitly unwrapped optional (`!`) | `late` keyword | `!` (definite assignment) | Null-forgiving operator (no late init) |
| Non-null assertion semantics | Throws NPE immediately | Runtime trap / UB | Throws TypeError | Compiles to `undefined` access | Throws NRE |

---

## Summary of Cross-Cutting Themes

**1. The data-class convergence is one of the strongest in language design.**
Every major language now has a way to say "here is a named collection of fields,
compare them by value, let me copy with modifications." The syntax varies but
the semantics are identical. Nomi should not innovate here — adopt the
consensus and move on.

**2. Pattern matching is eating the conditional.**
The trajectory is clear: type tests, destructuring, and exhaustiveness checking
are replacing `if`-`else` chains and `instanceof`-`cast` pairs. The
expression-switch with exhaustiveness is the terminal form. Nomi should build
around this as the primary conditional for structured data.

**3. Null safety is a solved problem — if you start with it.**
The languages that baked null safety in from the start (Kotlin, Swift) or
migrated to sound null safety (Dart) have a much better story than the
languages that tried to retrofit it (C#, TypeScript). Nomi is a new language —
there is no legacy code to protect. Sound null safety from day one is not
negotiable.

**4. The async model is not settled.**
While `async`/`await` is the dominant surface syntax, the underlying models
diverge significantly (thread pools, event loops, coroutines, virtual threads,
structured concurrency). Nomi's block/yield approach is a legitimate alternative
that does not have to follow the `async`/`await` consensus — the design space
for concurrency is still open.

**5. Incremental adoption works.**
Java's path (sealed classes, then pattern matching, then exhaustiveness) and
C#'s path (type patterns, then property patterns, then list patterns, then
relational patterns) show that language features can be shipped incrementally
without locking the design. Nomi should ship a minimal but complete feature set
first (sealed data + expression-match + with-expression) and add pattern forms
as they prove necessary.
