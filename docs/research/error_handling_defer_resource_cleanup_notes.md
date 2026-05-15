# Error Handling, Defer, and Resource Cleanup: Research Notes

> Status: source research notes for Nomi design.
>
> Covers: Zig, Hylo (Val), Odin, Gleam, and Roc.
>
> Focus: error handling, deferred execution, resource cleanup, and
> ownership/resource semantics. Each section gives concrete syntax
> and a short explanation of the semantic model.

## Zig

### `try` and `!` Error Union Operator

```zig
// !T means "T or an error"
fn openConfig(path: []const u8) !Config {
    // try propagates error upward: if openFile returns an error,
    // openConfig returns that error immediately
    const file = try std.fs.cwd().openFile(path, .{});
    defer file.close();
    const contents = try file.readToEndAlloc(allocator, 1024);
    return parseConfig(contents);
}

// Error union type explicitly names possible errors
fn fallibleOp() error{OutOfMemory}!void {
    const data = try allocator.alloc(u8, 1024);
    // ...
}
```

Semantics: The `!` operator in a return type declares that the function returns
either a value of the base type or an error from a possibly-inferred error set.
The `try` keyword is a prefix operator that unwraps the value or propagates the
error up the call stack -- it is equivalent to `expr catch |err| return err`.
There are no hidden exceptions; every error path is visible in the source.

### `errdefer`

```zig
fn processFile(path: []const u8) !void {
    var file = try std.fs.cwd().createFile(path, .{});
    // This runs ONLY on error, not on normal return
    errdefer std.fs.cwd().deleteFile(path) catch {};

    try file.writeAll("header\n");
    // If writeAll fails above, deleteFile runs.
    // If we reach here without error, deleteFile does NOT run.
    try file.writeAll("body\n");
    // Success: file stays on disk.
}
```

Semantics: `errdefer` is `defer` conditioned on the return status. The deferred
block runs only if the enclosing scope exits via an error return. This enables
"undo on failure" patterns -- allocate a resource, and if anything goes wrong
before you commit, the resource is automatically cleaned up. On success, the
deferred cleanup is skipped because the resource is meant to persist.

### Error Sets and `catch`

```zig
// Explicit error set
const FileError = error{
    NotFound,
    PermissionDenied,
    Unexpected,
};

fn readStuff(path: []const u8) FileError![]u8 {
    // catch with error capture
    const file = std.fs.cwd().openFile(path, .{}) catch |err| {
        if (err == error.NotFound) return &[_]u8{};
        return err; // re-propagate other errors
    };
    // catch with default value
    const name = std.process.getEnvVarOwned(allocator, "USER")
        catch "unknown";
    // ...
}
```

Semantics: Error sets are explicit enumerated types whose values are errors, not
integers. Every fallible function has a statically-known error set (or inferred
one). The `catch` operator provides two forms: `expr catch default_value` and
`expr catch |err| { handler }`. There are no null exceptions, no catch-all
blocks without explicit error captures, and no silent error swallowing.

### How Errors Compose

```zig
// Inferred error set: the compiler infers the union of all errors
// returned from this function body
fn composedOp() !void {
    // Each of these could return different errors;
    // the inferred set becomes error{ReadError, ParseError, WriteError}
    const data = try readInput();       // error{ReadError}![]u8
    const parsed = try parse(data);     // error{ParseError}!Parsed
    try writeOutput(parsed);            // error{WriteError}!void
}

// Explicit composition via ||
fn needsTwo() (error{A} || error{B})!void {
    try opA(); // error{A}!void
    try opB(); // error{B}!void
}
```

Semantics: Zig's compiler infers error sets from all `try` and `return err`
sites, so a function's error surface is always visible without manual
annotation. The `||` operator merges named error sets. This means error
composition happens at compile time -- the caller of `composedOp` knows every
possible failure mode without reading the body. Error sets form a structural
type: two error sets are compatible if one is a subset of the other. The
dual-return convention (return `value, error`) is avoided entirely; the `!`
union is the single error-handling mechanism.

---

## Hylo (Val)

### `inout` Parameters and the Ownership Model

```hylo
// sink: the parameter takes ownership of the value
fun consume(x: sink String) {
    // x is owned here; when this scope exits, x is deinitialized
    print(x)
}

// inout: mutable borrow; caller sees mutations
fun increment(x: inout Int) {
    x += 1  // mutation is visible at the call site
}

// set: initialization of uninitialized memory
fun init(x: set Int) {
    x = 42  // x was uninitialized; we set it
}

// yield: the function yields a value (used with closures)
fun yielding_example() yield Int {
    // yield gives a value back to the caller *without* destroying
    // the function's local state
    yield 1
    yield 2
}

// let (default): immutable borrow; parameter is read-only
fun inspect(x: let String) {
    print(x)  // read only
}
```

Semantics: Hylo's ownership model is based on parameter conventions, not
lifetime annotations or reference kinds at the type level. A parameter
convention (`let`, `inout`, `sink`, `set`, `yield`) tells the compiler how the
callee uses the argument, and the compiler enforces safe usage at the call
site -- preventing use-after-move, double-consume, and mutation of borrowed
state. The model is "move by default" with explicit borrowing, the inverse of
Rust's "borrow by default with explicit moves."

### Subscripts with Projections

```hylo
type Matrix {
    var rows: Int
    var cols: Int
    var storage: Array[Float64]

    // subscript that returns a projection (inout) --
    // allows in-place mutation of the element
    subscript (self: let Matrix, r: Int, c: Int): inout Float64 {
        // A projection evaluates to a reference into self,
        // not an independent value. The compiler tracks that
        // self is borrowed so long as the projection lives.
        yield &self.storage[r * self.cols + c]
    }
}

// Usage: in-place mutation through the subscript
var m = Matrix(rows: 3, cols: 3, storage: ...)
m[1, 2] = 5.0  // writes through the projection
```

Semantics: Subscripts in Hylo are not limited to returning values; they can
return projections -- references into the subscripted value. A projection binds
the subscript result to the lifetime of the subscripted object, so the compiler
can enforce that `m` is not consumed or mutably borrowed elsewhere while the
projection is live. This makes subscripts as powerful as direct field access
while being defined by user code.

---

## Odin

### `defer` Statement

```odin
read_file :: proc(path: string) -> ([]byte, bool) {
    handle, ok := os.open(path)
    if !ok do return nil, false
    defer os.close(handle)

    // Multiple defers stack in LIFO order
    defer fmt.println("done reading")

    data, ok2 := os.read_entire_file_from_handle(handle)
    return data, ok2
    // os.close runs first, then fmt.println
}
```

Semantics: `defer` schedules a statement to run when the current scope exits,
regardless of how it exits (return, end of scope, or branch). Multiple defers in
the same scope execute in reverse declaration order (LIFO). This is the same
model as Go's defer, but Odin's is statement-scoped rather than
function-scoped, giving finer control over when cleanup fires -- a defer inside
a loop body runs at the end of each iteration, not at function exit.

### `using` for Context

```odin
Context :: struct {
    allocator: Allocator,
    temp_allocator: Allocator,
    logger: Logger,
}

// using brings struct fields into scope as local names
do_work :: proc(ctx: using Context) {
    // ctx.allocator is accessible as just "allocator"
    data := make([]byte, 1024, allocator)
    // ctx.logger accessible as "logger"
    logger.info("working", data)
}

// using on a struct field for composition
Entity :: struct {
    position: Vector3,
    using health: Health,
    // health.current, health.max -> Entity.current, Entity.max
}
```

Semantics: `using` is an explicit scope-import mechanism. On a procedure
parameter, it makes struct fields available as direct names inside the body --
effectively a Pascal `with` that is always explicit and lexically scoped.
On a struct field, `using` flattens the nested struct's fields into the
parent struct's field namespace, enabling delegation and composition without
boilerplate forwarding methods.

### Error Handling with `or_return`

```odin
// Multiple return values convention: (value, ok) or (value, error)
open_config :: proc(path: string) -> (Config, Error) {
    // or_return: on failure (ok == false or err != nil),
    // return the zero values and the error immediately
    file := os.open(path) or_return
    defer os.close(file)

    data := os.read_entire_file(file) or_return
    config := parse_json(data) or_return
    return config, nil
}

// or_return propagates the last return value as the error
write_result :: proc(data: []byte) -> Error {
    os.write_file("out.txt", data) or_return
    return nil
}
```

Semantics: `or_return` is syntactic sugar over Odin's multi-return convention.
Since Odin uses `(value, ok)` or `(value, error)` returns rather than sum types,
`or_return` checks the status value and, if it indicates failure, returns the
error from the current procedure. It only works in procedures that return a
status as the last parameter (a compiler-checked convention). This gives Zig's
`try`-like conciseness without abandoning the multi-return model.

### Explicit Allocators and `context`

```odin
// context is a thread-local implicit variable of type runtime.Context
make_stuff :: proc() -> []Thing {
    // Uses context.allocator implicitly
    return make([]Thing, 128)
}

make_stuff_with :: proc(allocator: Allocator) -> []Thing {
    // Explicit allocator as parameter
    return make([]Thing, 128, allocator)
}

// context contains: allocator, temp_allocator, logger,
//                   random_generator, user_data, etc.

// Set a custom allocator for the scope
{
    context.allocator = tracking_allocator()
    defer report_leaks(context.allocator)

    // All allocations in this scope use the tracking allocator
    data := make_stuff()
}
```

Semantics: Odin's `context` is an implicit thread-local variable that carries
runtime services (allocators, logger, random source). Libraries accept
`context` implicitly; callers set it explicitly. There is no global allocator
hiding in the runtime. The temp allocator pattern (arena that resets at scope
exit) is a first-class convention: `defer free_all(context.temp_allocator)`.
This makes allocation strategy visible at the use site without threading it
through every function signature individually.

---

## Gleam

### `use` Expressions (Replacing Callbacks)

```gleam
// Without use: explicit callback nesting
pub fn main() {
  database.connect()
  |> fn(db) {
    database.query(db, "SELECT * FROM users")
    |> fn(rows) {
      process(rows)
    }
  }
}

// With use: the callback becomes sequential-looking code
pub fn main() {
  use db <- database.connect()
  use rows <- database.query(db, "SELECT * FROM users")
  process(rows)
}

// use with result for early-return error handling
pub fn load_config(path: String) -> Result(Config, Error) {
  use contents <- file.read(path)    // returns Error if file.read fails
  use config <- json.decode(contents) // returns Error if decode fails
  Ok(config)
}

// Desugaring rule: use x <- expr
// becomes: expr(fn(x) { rest_of_scope })
// The rest of scope (everything after the use line) becomes the callback body.
```

Semantics: `use` is a syntactic abstraction over the callback-passing pattern.
It takes the expression on the right (which must be a function call that accepts
a callback as its last argument) and the rest of the current scope becomes the
callback body. This is not a special control-flow operator -- it desugars purely
at the syntax level into ordinary higher-order function calls. The technique is
general: it works for iteration, result handling, resource scoping, and any
callback-based API. Unlike `async/await`, it does not introduce function
coloring or require runtime support.

### `try` and `let assert`

```gleam
// try: pattern-matches on Ok/Error, propagates errors
fn parse_and_validate(input: String) -> Result(Validated, Error) {
  use parsed <- try(json.decode(input, decoder))  // try + use together
  use validated <- try(validate(parsed))
  Ok(validated)
}

// let assert: crashes on pattern mismatch (for invariants)
fn must_have_name(user: User) -> String {
  let assert Ok(name) = get_name(user)
  name
}

// try without use: for simpler cases
fn demo() -> Result(Int, Error) {
  let value = try(some_fallible_operation())
  Ok(value + 1)
}
```

Semantics: `try` in Gleam is not a keyword of the runtime; it is syntactic
shorthand for pattern matching on `Result(a, e)` where the `Error` branch
immediately returns the error from the enclosing function. Combined with `use`,
it creates a concise early-return-on-error style. `let assert` is the
"dangerous" sibling: it asserts a pattern must match and crashes with a helpful
message if it does not, used for programmer-verified invariants rather than
recoverable errors.

### Pipe Operator Semantics

```gleam
// Pipe passes the LHS as the first argument to the RHS function
pub fn demo() -> List(String) {
  users
  |> list.filter(fn(u) { u.age >= 18 })
  |> list.map(fn(u) { u.name })
  |> list.sort(by: string.compare)
}

// Equivalent to:
list.sort(
  list.map(
    list.filter(users, fn(u) { u.age >= 18 }),
    fn(u) { u.name },
  ),
  by: string.compare,
)

// Pipe with anonymous function captures
pub fn process() {
  data
  |> fn(d) { clean(d) }
  |> fn(d) { validate(d) }
  |> fn(d) { save(d) }
}
```

Semantics: The pipe `|>` is a simple left-to-right application operator: `x |>
f(a, b)` desugars to `f(x, a, b)`. It works with any function, including
anonymous ones created inline with `fn`. Pipes enable reading transformations in
the order they happen rather than inside-out. Unlike F# or Elm pipes (which are
operator overloading), Gleam's pipe is part of the language grammar and the
compiler resolves the function at compile time.

---

## Roc

### Tag Unions

```roc
# Tag union: a closed set of named variants, each with optional payload
Response :
    [ Loading
    , Loaded (List User)
    , Error LoadError
    ]

# Usage with pattern matching
displayResponse : Response -> Str
displayResponse = \response ->
    when response is
        Loading -> "Loading..."
        Loaded users -> "Found \((List.len users)) users"
        Error LoadError -> "Failed to load"

# Tag unions for error handling
parseMessage : Str -> [Ok Msg, Err ParseErr]
```

Semantics: Tag unions in Roc are closed discriminated unions -- every possible
variant is listed at the type declaration, and pattern matching must be
exhaustive. Tags are not constructors of an algebraic data type in the ML
sense; they are opaque markers that are unique per declaration. Unlike
TypeScript's string-based discriminated unions, Roc tags carry no runtime string
overhead and are checked for exhaustiveness at compile time.

### `!` Error Handling Operator

```roc
# Task that can fail with a specific error type
decodeAndValidate : Str -> Task (List User) DecodeErr !

# The ! means: this function is fallible; errors propagate implicitly
decodeAndValidate = \raw ->
    # ? operator (or Task.await with !) unwraps success or short-circuits
    decoded <- decodeUsers raw |> Task.onErr \err -> Task.fail err
    validated <- validateAll decoded |> Task.onErr \err -> Task.fail err
    Task.ok validated

# Error propagation with backpassing
loadUsers : Str -> Task (List User) [LoadFailed DecodeErr NetworkErr] !
```

Semantics: Roc uses two distinct mechanisms together. The `Task` type
represents I/O and fallible operations (not a general monad). The `!` suffix on
a function type marks it as fallible and enables error propagation via `?` (or
equivalently, `<-` combined with `!`). The `!` is part of the type, not a
separate exception mechanism -- errors must be handled before a value can be
used in pure code. Error types compose via anonymous tag unions like
`[LoadFailed DecodeErr NetworkErr]`.

### Functional Purity Approach

```roc
# Pure functions: no ! marker, guaranteed no I/O
# They can only return values based on their inputs
add : Int, Int -> Int
add = \x, y -> x + y

# The compiler tracks purity through the type system:
# - Pure functions cannot call Task functions
# - Task functions can call pure functions
# - There is no `unsafePerformIO` or escape hatch

# Effects are explicit in the function signature
processFile : Path -> Task Str FileErr !
```

Semantics: Roc enforces a strict pure/effect boundary at the type level. A
function that touches I/O must return a `Task` and have `!` in its signature.
Pure functions cannot call effectful ones, period. This is not an effect system
with user-defined effects or handlers -- it is a single, hard boundary between
computation and interaction, enforced by the compiler rather than convention.
The approach is reminiscent of Elm's `Cmd` but with finer-grained error typing.

### Backend-Passing Style

```roc
# A Roc application receives a platform (backend) as input
app : Platform -> Task {} [ServerErr]
app = \platform ->
    # All I/O goes through the platform record
    request <- platform.server.receive
    response = handleRequest request
    platform.server.send response
    app platform  # recursive loop for long-running servers

# CLI backend
main : Task {} CliErr !
main = cliApp cliPlatform

# The same logic, different platform
webMain : Task {} ServerErr !
webMain = \req -> app { server: req }
```

Semantics: Roc programs are pure functions that receive a platform record
providing all effectful capabilities. This is backend-passing style: the
platform is passed through program layers explicitly rather than imported as
ambient authority. The top-level `main` binds to a specific platform; everything
below it is parameterized over a platform interface. This separates "what the
program computes" from "how I/O happens" without needing monad transformers or
effect stacks. Testing is straightforward: pass a mock platform record and
everything below `main` runs identically.

---

## Quick-Reference Summary Table

| Language | Error propagation | Deferred cleanup | Resource model | Unique contribution |
| --- | --- | --- | --- | --- |
| Zig | `try` + error union `!` + explicit error sets | `defer` / `errdefer` | Manual, backed by `defer` | `errdefer` -- deferred only on error |
| Hylo | -- (ownership prevents errors; Rust-like `?` planned) | Destructors via ownership conventions | `sink/inout/let/set/yield` parameter conventions | Ownership as parameter convention, not lifetime annotation |
| Odin | multi-return + `or_return` | `defer` (scope-scoped) | Explicit allocators via `context` | `or_return` sugar over status-return convention |
| Gleam | `try` + `Ok/Error` Result type | `use` with resource types | Immutable; resources through `use` callbacks | `use` -- callback-to-sequential desugaring |
| Roc | `!` fallibility marker + `?` propagation | Platform cleanup + `Task` lifecycle | Purity boundary; platform-passing | Backend-passing style + compile-time pure/effect split |

---

## Swift

### `throws` / `try` / `try?` / `try!` — Typed Throws

```swift
// A function that can throw — the error type is part of the signature
enum ConfigError: Error {
    case missingFile(String)
    case parseError(String)
}

func loadConfig(path: String) throws -> Config {
    let data = try String(contentsOfFile: path) // try: must be in a throws context
    guard let parsed = parse(data) else {
        throw ConfigError.parseError("invalid format")
    }
    return parsed
}

// Calling: do-catch with pattern matching on error types
do {
    let config = try loadConfig(path: "config.json")
    print(config)
} catch ConfigError.missingFile(let name) {
    print("Missing: \(name)")
} catch { // catch-all
    print("Unknown error: \(error)")
}

// try? converts a throw into an Optional — failure becomes nil
let maybeConfig = try? loadConfig(path: "config.json") // Optional<Config>

// try! asserts no error will be thrown — crashes if it is
let mustExist = try! loadConfig(path: "known-good.json") // Config (non-optional)
```

Semantics: Swift separates throwable functions from non-throwable ones at the type
level — a function marked `throws` cannot be called without `try`, `try?`, or
`try!`. Swift 6 adds typed throws: `throws(MyError)` to constrain the error type
statically. The `Error` protocol is the base for all throwable types; enums
conforming to `Error` are the idiomatic pattern. `do { try ... } catch { ... }`
supports pattern matching on error cases, including `where` clauses for
conditional matching. `rethrows` marks higher-order functions that only throw if
a passed-in closure throws, preserving type information through generics.

### `Result<T, E>` in the Standard Library

```swift
func fetch(url: URL) -> Result<Data, NetworkError> {
    // Result is a first-class value, not a throw
    return .success(data)
}

// Functional transformation on Result
fetch(url: someURL)
    .map { data in parse(data) }        // transforms success
    .mapError { error in ... }          // transforms error
    .flatMap { parsed in validate(parsed) } // success->new Result

// Switching on Result
switch fetch(url: url) {
case .success(let data): process(data)
case .failure(let error): handle(error)
}

// Bridging to throws
let data = try fetch(url: url).get() // get() throws on failure
```

Semantics: `Result<T, E>` is the "expected failure as value" alternative to
`throws`. It is composable with `map`/`flatMap`/`mapError`, can be stored in
properties, passed between threads, and batched. The `get()` method bridges back
to the `throws` world. Swift offers both `throws` (propagation upward) and
`Result` (value-passing), allowing the programmer to choose the mechanism that
fits the use case.

### `defer` and `guard`

```swift
func processFile(path: String) throws -> Data {
    let handle = try FileHandle(forReadingFrom: URL(fileURLWithPath: path))
    defer {
        try? handle.close() // runs on scope exit, regardless of error
    }

    // Multiple defers: LIFO order
    defer { print("done processing") }

    // guard for early exit with required condition
    guard let header = try handle.read(upToCount: 4) else {
        throw FileError.unexpectedEOF
    }
    guard header == magicBytes else {
        throw FileError.invalidFormat
    }

    return try handle.readToEnd() ?? Data()
    // defer fires in reverse order: "done processing", then handle.close()
}
```

Semantics: `defer` runs the deferred block when the enclosing scope exits, even
if the exit is via a thrown error. Multiple defers execute in LIFO order. `guard`
is a structured early-exit pattern: `guard let` / `guard condition else { ... }`
requires the else block to exit the current scope (via `return`, `throw`,
`break`, `continue`, or `fatalError`). The bound value is available for the rest
of the scope. This is the idiomatic Swift style for "unwrap or bail."

### `async throws` for Structured Concurrency

```swift
func loadAndProcess(_ urls: [URL]) async throws -> [Processed] {
    try await withThrowingTaskGroup(of: (Data, URL).self) { group in
        for url in urls {
            group.addTask { try await (fetch(url: url), url) }
        }
        var results: [Processed] = []
        for try await (data, url) in group {
            results.append(try await process(data, url))
        }
        return results
    }
}
```

Semantics: `async throws` combines structured concurrency with error propagation.
`withThrowingTaskGroup` scopes concurrent child tasks; if any child throws, the
group cancels remaining tasks and propagates the error. Errors from concurrent
tasks are not lost — the group collects them. Swift's structured concurrency model
means cancellation is cooperative and error propagation is explicit.

---

## Kotlin

### `Result<T>` and `runCatching`

```kotlin
// runCatching wraps a block that may throw, returning Result<T>
val result = runCatching {
    readFile("config.json")
}

// Result transformation chain
val config = runCatching { loadConfig(path) }
    .map { config -> config.withOverrides(envOverrides) }  // on success
    .mapCatching { config -> validateConfig(config) }      // can throw, becomes Err
    .recover { error -> defaultConfig }                    // on failure, provide fallback
    .getOrThrow()                                          // unwrap or re-throw

// getOrNull / getOrElse / getOrDefault
val data = result.getOrNull()         // null on failure
val data = result.getOrElse { byteArrayOf() } // default on failure
val data = result.getOrDefault(defaultConfig)
```

Semantics: `Result<T>` is Kotlin's standard wrapper for a computation that may
fail. `runCatching` is the entry point — it catches `Throwable` and wraps it.
`map` transforms success, `mapCatching` transforms success but can itself throw
(becoming `Result.failure`), `recover` handles the error case, and `getOrNull`
drops error information for optional semantics. Unlike Rust, `Result` is not
the primary error mechanism — Kotlin also has unchecked exceptions. The `?`
operator chain (`?.`, `?:`) is for null safety only, not error handling.

### `require` / `check` / `assert` — Preconditions

```kotlin
fun process(name: String, count: Int) {
    require(name.isNotBlank()) { "name must not be blank" }
    // require throws IllegalArgumentException if false

    check(count > 0) { "count must be positive" }
    // check throws IllegalStateException if false

    assert(count % 2 == 0) // only enabled with -ea JVM flag
}
```

Semantics: Three tiers of precondition checking, graded by severity. `require`
validates arguments (IllegalArgumentException), `check` validates state
(IllegalStateException), `assert` is for programmer-verified invariants and is
disabled at runtime unless assertions are enabled. This distinguishes "caller got
it wrong" from "internal state is wrong" from "debug-only invariant."

### `Nothing` Type and `use` for AutoCloseable

```kotlin
// Nothing: the type of expressions that never return
fun fail(message: String): Nothing {
    throw IllegalStateException(message)
}

// This compiles because Nothing is a subtype of every type
val x: String = fail("unreachable")

// use: like Python 'with' or C# 'using' — guarantees close()
fun readFirstLine(path: String): String {
    return FileReader(path).use { reader ->
        BufferedReader(reader).use { br ->
            br.readLine() ?: ""
        }
    }
}

// use calls close() on scope exit (even on exception)
// Multiple use blocks nest; innermost closes first
```

Semantics: `Nothing` is the bottom type — functions that never return (infinite
loops, always-throw) have `Nothing` as their return type, and `Nothing` is a
subtype of every type. This enables type-safe throw expressions and exhaustiveness
checking. `use` is an extension function on `AutoCloseable` that ensures
`.close()` runs when the lambda exits, including on exception — the functional
equivalent of Java's try-with-resources.

### `@Throws` for Java Interop

```kotlin
@Throws(IOException::class)
fun readConfig(path: String): String {
    // Java callers will see 'throws IOException' in the method signature
    return File(path).readText()
}
```

Semantics: Kotlin does not have checked exceptions — all exceptions are
unchecked. The `@Throws` annotation exists solely for Java interop; it makes
Kotlin-compiled methods declare their throws in the bytecode so Java callers
are forced to handle them. This is a deliberate design choice: checked exceptions
were found to cause excessive wrapping and swallowing in real-world Java
codebases.

---

## Scala

### `Try[T]` — Success/Failure Monad

```scala
import scala.util.{Try, Success, Failure}

// Try wraps a computation result — no throws needed at call site
val result: Try[Config] = Try(loadConfig("config.json"))

// Composing with map/flatMap/recover (Try is a monad)
val validated: Try[Config] = result
  .map(config => config.withDefaults)
  .flatMap(config => Try(validate(config)))  // flatMap for fallible transform
  .recover { case e: FileNotFoundException => defaultConfig }
  .recoverWith { case e: ParseException => Try(loadFallback()) }

// Pattern matching
result match {
  case Success(config) => println(s"OK: $config")
  case Failure(e: FileNotFoundException) => println("Missing file")
  case Failure(e) => println(s"Failed: ${e.getMessage}")
}

// Converting to Option / Either
result.toOption   // Some(config) or None
result.toEither   // Right(config) or Left(Throwable)
```

Semantics: `Try[T]` is the idiomatic Scala way to wrap exceptions. It is
`Success[T]` or `Failure[Throwable]` and forms a monad — it supports
`map`/`flatMap`/`filter` and works in for-comprehensions. Unlike checked
exceptions, `Try` is a value — it can be stored, passed, and composed without
special syntax. The `Try {}` constructor catches non-fatal exceptions
automatically. For-comprehensions with `Try` give sequential-looking code with
automatic short-circuit on failure.

### `Either[L, R]` and `Option[T]`

```scala
// Either for typed error values (more specific than Try)
def parse(input: String): Either[ParseError, Ast] = {
  if (valid) Right(ast)
  else Left(ParseError("unexpected token"))
}

// Chaining with Either
val result: Either[AppError, Output] = for {
  config <- loadConfig(path)      // short-circuits on Left
  parsed <- parseConfig(config)   // type-safe error propagation
  output <- process(parsed)
} yield output

// Option[T] — Some/None for absence
def findUser(id: UserId): Option[User] = users.get(id)
val name: String = findUser(id).map(_.name).getOrElse("unknown")
```

Semantics: `Either[L, R]` is the general-purpose "this or that" type; by
convention, `Left` is the error case and `Right` is the success case. It forms a
monad (biased on `Right`) since Scala 2.12, enabling for-comprehension syntax.
`Option[T]` is `Some[T]` | `None` for optional values. The three types form a
hierarchy of specificity: `Option` (present/absent) < `Try` (value/exception) <
`Either` (typed success/typed failure). Scala 3 extends this with the `boundary`/`break` mechanism and `Either`-based error handling via the `CanEqual` trait.

### `Using` Trait (Scala 3) — Scoped Resources

```scala
import scala.util.Using

// Using manages a resource through its lifecycle
val content: Try[String] = Using(Source.fromFile("config.json")) { source =>
  source.mkString
}
// Source is automatically closed

// Multiple resources
val result = Using(Source.fromFile("a.txt")) { a =>
  Using(Source.fromFile("b.txt")) { b =>
    a.mkString + b.mkString
  }.get
}

// Using.Manager for multiple resources (flat nesting)
val result2 = Using.Manager { use =>
  val a = use(Source.fromFile("a.txt"))
  val b = use(Source.fromFile("b.txt"))
  a.mkString + b.mkString
}
// Both a and b are closed; order is reverse-acquisition (LIFO)
```

Semantics: `Using` is Scala's version of try-with-resources. It takes a
resource (anything with `.close()`) and a function that uses it; the resource
is always closed after the function completes, even on exception. `Using.Manager`
allows multiple resources to be allocated in the same scope — all are closed in
LIFO order when the block exits. Resources that fail to close do not mask the
primary exception; those secondary failures are added as suppressed exceptions.

### `scala.util.control.Exception` — Catching as Values

```scala
import scala.util.control.Exception._

// Catch specific exceptions as Option
val asOption: Option[Config] = catching(classOf[FileNotFoundException])
  .opt(loadConfig(path))

// Catch as Try
val asTry: Try[Config] = catching(classOf[ParseException])
  .try(loadConfig(path))

// Catch with handler
val handled = handling(classOf[IOException]) by { e: IOException =>
  defaultConfig
} apply loadConfig(path)
```

Semantics: The `Exception` object provides combinator-style exception handling:
pick which exceptions to catch, specify whether the result is `Option` or `Try`,
and apply the guarded expression. This is a bridge between Java-style exception
throwing and Scala's functional error types — the exception is caught at the
boundary and converted to a value, preventing it from propagating further.

---

## Java

### Checked Exceptions — The Original "Explicit Error Handling"

```java
// Checked exception: calling code MUST handle or declare
public Config loadConfig(String path) throws IOException, ParseException {
    // IOException is checked — the compiler enforces handling
    try (FileReader reader = new FileReader(path)) {
        return parseConfig(reader);
    }
    // If parseConfig throws ParseException (also checked),
    // it propagates to the caller.
}

// The caller must either catch or declare:
public void init() {
    try {
        Config c = loadConfig("config.json");
    } catch (IOException e) {
        throw new UncheckedIOException("Failed to load", e);
    } catch (ParseException e) {
        throw new RuntimeException("Bad config", e);
    }
}
```

Semantics: Checked exceptions are Java's original innovation — the compiler
verifies that every checked exception is either caught or declared in the
method's `throws` clause. This forces error handling into the type system,
making the error surface visible at API boundaries. In practice, checked
exceptions are widely criticized for boilerplate (wrapping, swallowing,
re-throwing) and for interacting poorly with lambdas and streams. Unchecked
exceptions (`RuntimeException` and subclasses) are the pragmatic escape hatch.

### Try-with-Resources

```java
// Automatic resource cleanup via AutoCloseable
public List<String> readLines(String path) throws IOException {
    // Resources declared in try() are AutoCloseable; close() called
    // in reverse declaration order, even on exception.
    try (
        FileReader fr = new FileReader(path);
        BufferedReader br = new BufferedReader(fr)
    ) {
        return br.lines().collect(Collectors.toList());
    }
    // br.close() runs first, then fr.close()
    // If both the body and close() throw, the body exception is primary
    // and close() exceptions are added as suppressed.
}

// try-with-resources with catch and finally
try (var conn = DriverManager.getConnection(url)) {
    // use conn
} catch (SQLException e) {
    // handle DB errors
} finally {
    // runs after close()
}
```

Semantics: Introduced in Java 7, try-with-resources guarantees that any resource
implementing `AutoCloseable` is closed when the block exits. Resources are closed
in reverse declaration order. If the body and a `close()` both throw, the body
exception is primary and the close exception is added as suppressed. This is
Java's most-used resource cleanup pattern, replacing the older try-finally
manual-close idiom.

### `Optional<T>` — Limited but Ubiquitous

```java
// Optional for absence — no pattern matching, but chaining methods
Optional<User> maybeUser = userRepo.findById(id);

// map / flatMap / filter / or / orElse / orElseGet / orElseThrow
String name = maybeUser
    .map(User::name)
    .filter(n -> !n.isBlank())
    .orElse("unknown");

// No pattern matching on Optional — must unwrap to check
if (maybeUser.isPresent()) { ... }

// Java 9+ additions: ifPresentOrElse, or, stream
maybeUser.ifPresentOrElse(
    user -> process(user),
    () -> log("not found")
);
```

Semantics: `Optional<T>` is Java's container for values that may be absent. It
is intentionally limited — it does not implement `Iterable`, cannot be used in
enhanced for-loops, and there is no pattern matching on its state. The design
philosophy is that `Optional` is for return types only, not for fields or method
parameters. Java 21+ sealed types with pattern matching are a more general
alternative for modeling `Result`-like types.

### Sealed Types + Pattern Matching (Java 21) — Enabling Result-like Modeling

```java
// Sealed hierarchy enables exhaustive pattern matching
public sealed interface Result<T, E> {
    record Success<T, E>(T value) implements Result<T, E> {}
    record Failure<T, E>(E error) implements Result<T, E> {}
}

// Pattern matching with switch — compiler checks exhaustiveness
String describe(Result<Config, AppError> result) {
    return switch (result) {
        case Result.Success(var config) -> "OK: " + config;
        case Result.Failure(var error) -> "Error: " + error.message();
    };
    // No default needed — sealed means compiler knows all cases
}

// Guarded patterns
String handle(Result<Config, AppError> result) {
    return switch (result) {
        case Result.Success(Config c) when c.isExpired() -> "Expired";
        case Result.Success(Config c) -> "Valid";
        case Result.Failure(NetworkError e) -> "Network down";
        case Result.Failure(AppError e) -> "App error";
    };
}
```

Semantics: Java 21 sealed types + record patterns + switch expressions give Java
the building blocks for typed error handling. A sealed interface guarantees
exhaustiveness — the compiler knows all possible subtypes, so switch expressions
on sealed types need no `default`. Combined with record deconstruction in
patterns, this enables Rust-like `Result` modeling natively in Java without
libraries.

### Virtual Threads + Structured Concurrency (Java 21)

```java
// StructuredTaskScope: all child tasks complete or are cancelled together
try (var scope = new StructuredTaskScope.ShutdownOnFailure()) {
    Future<User> user = scope.fork(() -> fetchUser(id));
    Future<Order> order = scope.fork(() -> fetchOrder(id));

    scope.join();           // wait for all tasks
    scope.throwIfFailed();  // propagate any failure

    return new Report(user.resultNow(), order.resultNow());
}
// scope is AutoCloseable — guarantees cleanup
```

Semantics: Structured concurrency (`StructuredTaskScope`) ties child task
lifetimes to a parent scope. If any child fails, the scope shuts down and
cancels remaining children. The scope is itself `AutoCloseable`, so cleanup
is deterministic. Virtual threads make blocking cheap, so structured concurrency
patterns that would be too expensive with platform threads become practical.

---

## Python

### `try`/`except`/`else`/`finally` — The Full Exception Model

```python
# Full try-except-else-finally chain
def load_config(path: str) -> Config:
    f = None
    try:
        f = open(path)
        data = f.read()
    except FileNotFoundError:
        raise ConfigError(f"Missing config: {path}")
    except PermissionError:
        raise ConfigError(f"Cannot read config: {path}")
    except OSError as e:
        raise ConfigError(f"I/O error: {e}") from e  # exception chaining
    else:
        # else: runs only if no exception in try block
        return parse_config(data)
    finally:
        # finally: ALWAYS runs — cleanup, logging, etc.
        if f:
            f.close()

# Multiple exception types in one clause
try:
    risky_operation()
except (ValueError, TypeError):
    handle_bad_input()

# Exception chaining: from / from None
try:
    parse(input)
except ParseError as e:
    raise AppError("Failed") from e  # preserves cause chain
    # raise AppError("Failed") from None  # suppresses cause chain
```

Semantics: Python's exception model is the most mature of any dynamic language.
The `try`/`except`/`else`/`finally` chain provides four distinct phases: try the
operation, handle specific exceptions, run code only on success (else), and run
cleanup unconditionally (finally). Exception chaining via `raise ... from` creates
a cause chain (accessed via `__cause__`), distinguishing "this failed because
that failed" from "we caught that and raised this instead." `raise ... from None`
suppresses the chain for deliberate context switches.

### `ExceptionGroup` / `except*` (Python 3.11) — Multiple Simultaneous Exceptions

```python
# ExceptionGroup: multiple exceptions raised at once
def process_all(tasks: list[Task]) -> None:
    errors = []
    for task in tasks:
        try:
            task.run()
        except Exception as e:
            errors.append(e)
    if errors:
        raise ExceptionGroup("task failures", errors)

# except* catches exceptions from a group individually
try:
    process_all(tasks)
except* OSError as eg:
    # eg.exceptions contains all OSError instances
    for e in eg.exceptions:
        log(f"I/O error: {e}")
except* ValueError as eg:
    # all ValueError instances
    for e in eg.exceptions:
        log(f"Bad value: {e}")
# Remaining unhandled exceptions re-form a group and propagate
```

Semantics: Introduced in PEP 654 (Python 3.11), `ExceptionGroup` allows multiple
exceptions to be raised simultaneously — critical for concurrent code where
several tasks fail independently. `except*` splits an exception group by type,
handling all instances of each type. This solves the "one of N errors is
arbitrarily chosen and the others are lost" problem that plagued `asyncio.gather`
and concurrent.futures. Nested exception groups form trees, with each `except*`
peeling off one layer.

### `contextlib` — Context Managers, ExitStack, and Friends

```python
from contextlib import contextmanager, ExitStack, closing, suppress, redirect_stderr

# @contextmanager: generator-based context manager
@contextmanager
def managed_resource(path: str):
    resource = acquire(path)
    try:
        yield resource  # body runs here
    finally:
        resource.release()  # always runs, even on exception

with managed_resource("data.db") as r:
    r.query("...")

# ExitStack: dynamic collection of context managers
def process_files(paths: list[str]):
    with ExitStack() as stack:
        files = [stack.enter_context(open(p)) for p in paths]
        # ALL files are closed on exit, in reverse order
        process(files)

# suppress: catch and discard specific exceptions
from contextlib import suppress
with suppress(FileNotFoundError):
    os.remove("temp.txt")  # no error if file doesn't exist

# closing: make any .close()-able object a context manager
from contextlib import closing
with closing(urllib.urlopen("http://example.com")) as page:
    page.read()
```

Semantics: Python's context manager protocol (`__enter__`/`__exit__`) is the
standard resource management pattern. `contextlib` provides a rich toolkit:
`@contextmanager` turns generators into context managers (with try/finally for
cleanup), `ExitStack` allows dynamic, runtime-determined sets of managed
resources, `suppress` explicitly discards specific exceptions, and `closing`
adapts legacy close()-based APIs into context managers. The `__exit__` method
receives the exception triple (type, value, traceback) and can suppress the
exception by returning `True`.

### `traceback` Module — Structured Access to Tracebacks

```python
import traceback

try:
    risky()
except Exception:
    # traceback object is a structured value, not just a string
    tb = sys.exc_info()[2]

    # Format as string
    print("".join(traceback.format_tb(tb)))

    # Walk the stack programmatically
    for frame_summary in traceback.extract_tb(tb):
        print(frame_summary.filename, frame_summary.lineno, frame_summary.name)

    # TracebackException: high-level representation with chaining support
    tbe = traceback.TracebackException.from_exception(e)
    print("".join(tbe.format()))  # includes __cause__ and __context__ chains
```

Semantics: Python's `traceback` module provides structured, programmatic access
to traceback information — not just string formatting. `traceback.extract_tb`
returns `FrameSummary` named tuples with filename, line number, function name,
and source line. `TracebackException` handles chaining: it walks the
`__cause__` and `__context__` chains to produce a complete multi-exception
traceback (critical now that ExceptionGroups produce nested chains).

### `match` Statement (3.10+) — Pattern Matching on Exceptions

```python
def handle_error(e: Exception) -> str:
    match e:
        case FileNotFoundError(path=str(p)) if p.endswith(".json"):
            return f"JSON config missing: {p}"
        case FileNotFoundError():
            return "File not found"
        case PermissionError() if os.geteuid() == 0:
            return "Running as root but permission denied"
        case OSError(errno=err):
            return f"OS error {err}"
        case ConfigError(cause=ParseError(line=line)):
            return f"Parse failed at line {line}"
        case _:
            return f"Unknown: {e}"
```

Semantics: Python 3.10's `match` statement supports structural pattern matching
on exception objects — destructuring attributes, matching nested exceptions, and
applying guards (`if` clauses). This is more expressive than `except` type
dispatch, especially for errors with structured payloads. The combination of
match + ExceptionGroup + `except*` gives Python a layered error handling system
that spans from "simple try/except" to "pattern-matched multi-error dispatch."

---

## C++ (Modern)

### RAII — The Original Resource-Cleanup Pattern

```cpp
// RAII: resource acquisition IS initialization
// The destructor runs deterministically when the object goes out of scope.
class FileHandle {
    int fd;
public:
    FileHandle(const std::string& path) : fd(::open(path.c_str(), O_RDONLY)) {
        if (fd == -1) throw std::runtime_error("Cannot open file");
    }
    ~FileHandle() {
        if (fd != -1) ::close(fd);  // deterministic cleanup
    }
    // Move-only or copyable? Moves transfer ownership.
    FileHandle(FileHandle&& other) noexcept : fd(other.fd) {
        other.fd = -1;  // leave source in valid empty state
    }
    FileHandle& operator=(FileHandle&& other) noexcept {
        if (this != &other) {
            if (fd != -1) ::close(fd);
            fd = other.fd;
            other.fd = -1;
        }
        return *this;
    }
};

void process_file(const std::string& path) {
    FileHandle f(path);   // acquired here
    // ... use f ...
    // f.~FileHandle() runs here — always, even if exception thrown
}
```

Semantics: RAII (Resource Acquisition Is Initialization) is C++'s fundamental
resource management idiom. An object owns a resource; the destructor releases it.
The destructor runs deterministically when the object goes out of scope — return,
end of block, or stack unwinding from an exception. This is more robust than
`defer` because it cannot be forgotten (the compiler inserts it) and composes
automatically (member destructors run in reverse declaration order). Modern C++
discourages raw `new`/`delete` in favor of `std::unique_ptr`, `std::shared_ptr`,
and containers that apply RAII to memory as well.

### `noexcept` — Function-Level Exception Specification

```cpp
// noexcept: this function does not throw
int add(int a, int b) noexcept { return a + b; }

// noexcept with condition
template<typename T>
void swap(T& a, T& b) noexcept(noexcept(T(std::declval<T&&>()))) {
    T tmp = std::move(a); a = std::move(b); b = std::move(tmp);
}

// noexcept is part of the type system (since C++17)
void (*fp)() noexcept = &safe_func;  // ok
// void (*fp2)() noexcept = &throwing_func; // error

// Moving noexcept objects lets containers optimize
// (e.g., std::vector growth uses moves instead of copies if noexcept)
```

Semantics: `noexcept` is a compile-time guarantee that a function does not throw.
If a `noexcept` function throws, `std::terminate` is called. The specifier is
part of the function type since C++17 and enables container optimizations —
`std::vector` growth will move elements (O(1)) instead of copying them (O(n))
if the move constructor is noexcept. The `noexcept` operator checks an
expression at compile time: `noexcept(f(args))` is true if `f(args)` is
declared `noexcept`. This is a simpler, more performant alternative to Java-style
checked exceptions — guarantee no-throw instead of enumerating what may throw.

### `std::expected<T, E>` (C++23) — Value-or-Error Union Type

```cpp
#include <expected>

// expected<T, E>: either a value T or an error E
std::expected<Config, AppError> load_config(const std::string& path) {
    auto file = open_file(path);
    if (!file) return std::unexpected(file.error());  // propagate error

    auto data = file->read_all();
    if (!data) return std::unexpected(ConfigError::IOMalformed);

    return parse(data.value());  // return value
}

// Using expected:
auto config = load_config("config.json");
if (config) {
    process(*config);           // dereference to get value
} else {
    log(config.error());        // .error() to get the error
}

// Monadic operations (also C++23)
auto result = load_config(path)
    .and_then([](auto c) { return validate(c); })  // flatMap on success
    .transform([](auto c) { return c.withDefaults(); })  // map on success
    .or_else([](auto e) { return load_default(); })  // handle error
    .transform_error([](auto e) { return to_user_error(e); });  // map error

// value_or: extract with fallback
Config c = load_config(path).value_or(Config::default());
```

Semantics: `std::expected<T, E>` (C++23) is the standard value-or-error type. It
is a discriminated union that contains either a `T` or an `E`. The monadic
operations (`and_then`, `transform`, `or_else`, `transform_error`) enable
functional-style chaining without exceptions. Unlike `std::optional<T>`,
`expected` carries error information. Unlike exceptions, `expected` is a
value — it can be stored, moved across threads, and composed without stack
unwinding. Error handling with `expected` is explicit at every call site.

### `std::optional<T>` (C++17)

```cpp
// optional: a value that may be absent
std::optional<User> find_user(const std::string& name) {
    if (auto it = users.find(name); it != users.end()) {
        return *it;
    }
    return std::nullopt;  // explicit "no value"
}

// Using optional:
auto user = find_user("alice");
std::string name = user.value_or("unknown");     // with fallback
if (user.has_value()) { process(*user); }

// value() throws std::bad_optional_access if empty
// and_then / transform / or_else available in C++23
```

Semantics: `std::optional<T>` models "value or nothing." Its interface is
simpler than `expected` — there is no error payload, only presence or absence.
Before C++23, it lacked monadic operations; with C++23, it has `and_then`,
`transform`, and `or_else`, bringing it in line with `expected` for the
value-only use case.

### RAII vs `defer` — Deterministic Destructors vs Explicit Defer Statements

```cpp
// RAII: cleanup is attached to TYPES, not to SCOPES
struct ScopedTransaction {
    Database& db;
    bool committed = false;

    ~ScopedTransaction() {
        if (!committed) db.rollback();  // auto-rollback on scope exit
    }

    void commit() { committed = true; db.commit(); }
};

void transfer(Database& db, Account from, Account to, Money amt) {
    ScopedTransaction tx(db);
    db.debit(from, amt);
    db.credit(to, amt);
    tx.commit();  // success: destructor skips rollback
}
// If anything throws, tx.~ScopedTransaction() calls rollback()
```

Semantics: RAII and `defer` solve the same problem (deterministic cleanup) in
different ways. RAII attaches cleanup to types — the destructor defines what
"cleanup" means, and every instance of the type gets it automatically. `defer`
attaches cleanup to scopes — a statement schedules cleanup at the point of
acquisition. RAII is more automatic (no per-use-site code) but requires
wrapper types. `defer` is more local (cleanup visible at acquisition point)
but requires explicit statements. The two approaches can achieve identical
correctness; the trade-off is between type-system machinery (RAII) and
explicit code at each use (defer).

---

## Haskell

### `Maybe a` — The Canonical Optional Type

```haskell
-- Maybe a = Nothing | Just a
findUser :: UserId -> Map UserId User -> Maybe User
findUser uid = Map.lookup uid

-- Pattern matching
case findUser uid users of
    Just user -> process user
    Nothing   -> putStrLn "User not found"

-- Combinators: maybe, fromMaybe, mapMaybe
name = maybe "unknown" userName (findUser uid users)
name = fromMaybe "unknown" $ findUser uid users

-- Do-notation with Maybe
getDisplayName :: UserId -> Map UserId User -> Maybe String
getDisplayName uid users = do
    user <- Map.lookup uid users           -- short-circuits on Nothing
    profile <- userProfile user            -- Nothing propagates
    guard (not $ profileHidden profile)    -- guard: Nothing if False
    return (profileDisplayName profile)

-- isJust, isNothing, catMaybes, mapMaybe
activeNames = mapMaybe (\u -> if userActive u then Just (userName u) else Nothing) allUsers
```

Semantics: `Maybe a` is the algebraic data type for optionality — `Just a` or
`Nothing`. In do-notation, `<-` on a `Maybe` short-circuits on `Nothing`: the
entire `do` block becomes `Nothing` if any step yields `Nothing`. The `guard`
function from `Control.Monad` uses `Alternative` to turn a boolean condition
into `Nothing` (failure) or `Just ()` (continue). This makes `Maybe` compose
like an effect system — sequential operations that may fail at any step become a
single `Maybe`-valued expression.

### `Either e a` — The Canonical Result Type

```haskell
-- Either e a = Left e | Right a
parseConfig :: String -> Either ParseError Config
parseConfig input =
    case runParser configParser input of
        Left err -> Left (ParseError err)
        Right cfg -> Right cfg

-- Do-notation with Either (right-biased)
processConfig :: FilePath -> Either AppError Config
processConfig path = do
    contents <- readFileEither path       -- Returns Either AppError String
    config <- parseConfig contents        -- Left short-circuits
    validated <- validateConfig config    -- error propagation is linear
    return validated

-- fromRight, fromLeft, isRight, isLeft, partitionEithers
results = map tryLoad paths
(good, bad) = partitionEithers results  -- ([Config], [AppError])
```

Semantics: `Either e a` is the generic two-case type; by convention (and since
base 4.10 / GHC 8.2), `Left` is error and `Right` is success, biased for
do-notation. In a `do` block, `<-` on `Left err` causes the entire block to
become `Left err` — linear error propagation without manual checks at each step.
Unlike Rust's `Result`, Haskell's `Either` has no `?` operator — do-notation
serves the same purpose. The `ExceptT` monad transformer lifts `Either`-style
error handling into any monad stack.

### `ExceptT e m a` — Monad Transformer for Exceptions

```haskell
-- ExceptT layers Either-style error handling on top of any monad
import Control.Monad.Except

type App = ExceptT AppError IO

-- throwError: signal failure
loadConfig :: FilePath -> App Config
loadConfig path = do
    exists <- liftIO $ doesFileExist path
    unless exists $ throwError (ConfigNotFound path)
    contents <- liftIO $ readFile path
    case parse config contents of
        Left err -> throwError (ParseError err)
        Right cfg -> return cfg

-- catchError: handle errors within the monad
robustLoad :: FilePath -> App Config
robustLoad path = loadConfig path `catchError` \case
    ConfigNotFound _ -> return defaultConfig
    ParseError msg   -> throwError (AppError ("Parse: " ++ msg))

-- runExceptT unwraps the IO (Either AppError Config)
main :: IO ()
main = do
    result <- runExceptT (robustLoad "config.json")
    case result of
        Left err -> putStrLn ("Failed: " ++ show err)
        Right cfg -> putStrLn ("Loaded: " ++ show cfg)
```

Semantics: `ExceptT e m a` is a monad transformer that adds `Either e`-style
error handling to any underlying monad `m`. `throwError` signals an error (like
`Left`), and `catchError` catches it (like `catch`). Since `ExceptT` is a
transformer, it composes with other transformers (ReaderT, StateT) in a monad
stack. This is the "exceptions as monadic effects" pattern — errors propagate
through the monad automatically while the caller can catch and handle them at
any level.

### `MonadThrow` / `MonadCatch` / `MonadMask` — Exception Handling in Monadic Code

```haskell
import Control.Monad.Catch (MonadThrow, MonadCatch, MonadMask, bracket, catch, throwM)

-- MonadThrow: monads that can throw exceptions
-- IO is the canonical instance; ExceptT e m is NOT (it uses Left instead)
throwM :: MonadThrow m => SomeException -> m a

-- catch: like try/catch for monadic code
safeOp :: (MonadCatch m) => m a -> (SomeException -> m a) -> m a
safeOp op handler = op `catch` handler

-- MonadMask: for bracket operations (resource scoping)
-- bracket ensures cleanup even on exceptions
withFile :: FilePath -> IOMode -> (Handle -> IO r) -> IO r
withFile path mode = bracket (openFile path mode) hClose

-- bracket: acquire, use, release
bracket :: MonadMask m => m a -> (a -> m b) -> (a -> m c) -> m c
bracket acquire release use = ...
-- release ALWAYS runs, even if 'use' throws
-- If both throw, the use-exception is primary, release-exception is secondary

-- bracket uses finalizers registered with the runtime exception handler
-- on exception, the RTS unwinds and runs finalizers before propagating
```

Semantics: The `exceptions` package (re-exported by `unliftio`) provides a
typeclass hierarchy for exception handling that works across monad stacks.
`MonadThrow` is for monads that can throw exceptions (mainly `IO`).
`MonadCatch` adds `catch` and `try`. `MonadMask` enables `bracket` — the
functional equivalent of `try`/`finally` or RAII. `bracket acquire release use`
guarantees that `release` runs after `use`, even if `use` throws. The key
insight is that `bracket` doesn't depend on destructors or deferred statements;
it is a higher-order function that encodes the acquire-use-release pattern as a
first-class combinator.

### Pure vs Impure Error Handling — Exceptions Are in `IO`

```haskell
-- Pure: use Maybe, Either, or a custom ADT — no exceptions
-- The type tells you exactly what can fail
safeDivide :: Double -> Double -> Maybe Double
safeDivide _ 0 = Nothing
safeDivide x y = Just (x / y)

-- Impure: IO exception handling
-- Exceptions can only be caught in IO (or a stack ending in IO)
riskyIO :: IO ()
riskyIO = do
    result <- try (readFile "data.txt") :: IO (Either IOException String)
    case result of
        Left e  -> putStrLn ("IO failed: " ++ show e)
        Right s -> putStrLn ("Read: " ++ s)

-- Pure code cannot throw or catch exceptions — this is enforced by the type system
-- There is no unsafePerformIO escape hatch for exceptions
```

Semantics: In Haskell, exception throwing and catching are confined to `IO`.
Pure functions return `Maybe`, `Either`, or custom sum types to model failure —
the types are visible in the function signature, and there is no hidden exception
path. This is a stronger guarantee than Rust's `panic!` (which can happen
anywhere) or Zig's `@panic`. `try` lifts an `IO` action that may throw into an
`IO (Either SomeException a)` — converting impure exception handling into a pure
value after the fact. The `MonadUnliftIO` pattern ensures resource cleanup in
exception-heavy code without `MonadBaseControl`'s unsafety.

---

## Cross-Language Synthesis

### The Three Error Stories (Every Language Tells)

Every language converges on three distinct error stories:

1. **Absence** (this value may not exist)
   - Swift: `nil` + `if let`/`guard let`/`??`
   - Rust: `Option<T>` + `?` + `unwrap_or`
   - Kotlin: `?` + `?.` + `?:` + `!!`
   - Python: `None` + `is None` + `or` (no safe navigation until walrus)
   - Haskell: `Maybe a` + do-notation + `maybe`
   - Java: `Optional<T>` + `orElse`/`map` (no pattern matching)
   - C++: `std::optional<T>` + `value_or`
   - Zig: `?T` (optional type, distinct from error union `!T`)
   - Gleam: `Option(value)` / `Error(e)` — unifies absence and error into `Result`

2. **Expected Failure** (this operation can fail, and that's normal)
   - Swift: `throws` + `try`/`do-catch` + `Result<T, E>`
   - Rust: `Result<T, E>` + `?`
   - Zig: `!T` error union + `try`
   - Gleam: `Result(value, error)` + `try`
   - Scala: `Try[T]` + `Either[L, R]`
   - Go: `(value, error)` return pattern
   - Kotlin: `Result<T>` + `runCatching`
   - Haskell: `Either e a` + do-notation + `ExceptT`
   - C++: `std::expected<T, E>`
   - Python: `try`/`except` (though same mechanism as unexpected errors)

3. **Unexpected Failure** (this is a bug or unrecoverable condition)
   - Rust: `panic!` / `unwrap` / `expect`
   - Zig: `@panic` / `unreachable`
   - Swift: `fatalError` / `preconditionFailure` / `try!`
   - Erlang/Elixir: let it crash + supervisor restart
   - Python: `raise` / uncaught exceptions
   - Go: `panic` (rare, discouraged)
   - Kotlin: `throw` / `error()` (unchecked exceptions)
   - C++: uncaught exceptions → `std::terminate`
   - Haskell: `error` / `undefined` (pure code panics) + imprecise exceptions in IO

### What's Structurally Identical (Just Syntax Sugar)

- `a?.b` in Swift/Kotlin/C#/JavaScript is semantically identical — short-circuit on null
- `defer` in Go/Zig/Odin/Swift is semantically identical — LIFO cleanup at scope exit
- `try` + `catch` in Java/Python/C#/Swift is structurally identical — exception matching
- `Result.map` / `Result.andThen` in Rust/Kotlin/Scala/Haskell — functor/monad on Result
- RAII in C++ = `defer` in Zig = `Drop` in Rust = `finally` in Python = `defer` in Go — deterministic cleanup
- `bracket` in Haskell = `try-with-resources` in Java = `with` in Python = `Using` in Scala = `defer` in Zig — acquire-use-release pattern
- `optional.and_then` in Rust = `optional.flatMap` in Scala = `bind` on Maybe in Haskell = do-notation `<-` on Maybe — monadic chaining on optional values

### What's Genuinely Different (Real Design Choices)

1. **Error propagation direction:**
   - Upward (exceptions): Java, Python, Swift, C++ — errors bubble up automatically
   - Inline (return values): Go, Rust, Zig, Gleam — errors are explicit at call site
   - Two-tier (both available): Swift (`throws` + `Result`), Kotlin (exceptions + `Result`), Scala (exceptions + `Try`/`Either`)
   - Collapse (let it crash): Erlang/Elixir — errors are expected in production
   - Functional (monadic): Haskell (Either, ExceptT) — error is an effect in the type

2. **Error type richness:**
   - Typed: Java checked exceptions, Swift typed throws, Zig error sets, Rust enums, Gleam custom types
   - Untyped: Python, Go (error is an interface value), Erlang (anything can be thrown)
   - Discriminated: Rust enums, Scala sealed traits, Gleam custom types, Java 21 sealed types, Haskell ADTs
   - Neither: C (error codes are ints)

3. **Resource cleanup:**
   - Scoped (RAII/destructor): C++, Rust (Drop), Swift (classes with deinit)
   - Block-based (context manager): Python (`with`), Java (`try-with-resources`), Kotlin (`use`), Scala (`Using`)
   - Defer-statement: Zig (`defer`), Go (`defer`), Odin (`defer`), Swift (`defer`)
   - Functional (bracket): Haskell (`bracket`, `withFile`)
   - Manual: C (`goto cleanup`)

4. **Propagation operator (`?` and friends):**
   - Rust: `?` returns `Err` from current function (needs `From` conversion)
   - Swift: `try?` returns `nil`, `try!` panics on throw
   - Zig: `try` returns error union from current function
   - Gleam: `try` extracts `Ok` value or returns `Error` early
   - Kotlin: `?:` is null-coalesce, NOT error propagation
   - C++: `std::expected` uses `.and_then()` / `.or_else()` — no syntax-level `?` operator

5. **Checked vs unchecked exceptions:**
   - Checked (compiler-enforced): Java (checked exceptions)
   - Unchecked (runtime only): Python, Kotlin, C#, Ruby, JavaScript
   - No exceptions at all: Rust, Zig, Gleam (use `Result`/error union values)
   - Optional checked: Swift (typed throws in Swift 6); Scala (you choose Try vs throw)

6. **Error context / chaining:**
   - Built-in cause chain: Java (`initCause`), Python (`raise ... from`), C++ (`std::nested_exception`)
   - Manual wrapping: Go (`fmt.Errorf("...: %w", err)`), Rust (`anyhow::Context` trait)
   - Stack traces: Python (always), Java (always), Go (manual via `%w`), Rust (`anyhow` optional)
   - Multiple simultaneous errors: Python (`ExceptionGroup` / `except*`)

### Key Tensions When Synthesizing

1. **One `?` operator, many semantics:**
   Rust's `?` (early return on Err) vs Swift's `try?` (nil on throw) vs Zig's
   `try` (early return on error) vs Kotlin's `?:` (null fallback). Different
   semantics share similar syntax. Nomi must pick ONE semantic for `?` and
   document it clearly, OR provide a distinct operator for each of the three
   error stories. The risk of overloaded `?` is confusion between "this value
   might be None" and "this operation might fail."

2. **Defer + Error Recovery:**
   Zig's `errdefer` only runs on error path. Go's `defer` always runs. Odin
   distinguishes `defer` from `defer_err`. This raises a design question: should
   cleanup code know WHY it's being called? Zig's answer is yes (rollback on
   failure, keep resource on success). Go and Swift's answer is no (cleanup
   should be unconditional, because the cleanup code shouldn't have to reason
   about the success/failure state of the scope). Nomi's current `defer` follows
   Go/Swift: always run, regardless of exit reason.

3. **Try Expression vs Statement:**
   Some languages make try an expression (Rust `?`, Gleam `try`, Scala
   for-comprehension, Haskell do-notation). Some make it a statement (Python
   `try:`, Swift `do {} catch {}`). Expression-oriented try is more composable —
   you can assign the result or pass it to a function — but requires a value
   for both success and failure paths. Statement-oriented try is easier for
   side-effecting error recovery (logging, retrying, re-raising). The Rust `?`
   operator is the most minimal expression-oriented form: a single character
   that returns the error or unwraps the value.

4. **Null Coalesce + Error Coalesce:**
   Swift uses `??` for nil only. Zig uses `??` for error unwrapping with a
   default (equivalent to `catch default`). Different semantics, same syntax.
   Nomi uses `??` for null only, following the absence normal form — errors
   are a separate concern and should not share syntax with absence.

5. **The Collapse Problem:**
   When absence, expected failure, and unexpected error all use the same
   mechanism (e.g., Python — everything is an exception), the programmer can't
   distinguish "this is normal" from "this is a bug." Python's `StopIteration`
   is the canonical example: an expected control-flow signal used the same
   mechanism as a genuine error, causing confusion and subtle bugs (fixed in
   PEP 479 by making it a `RuntimeError`). Nomi's three distinct stories
   (absence via `?.`/`??`, Result via `Result[T, E]`, and raise via a raise
   mechanism) prevent this collapse by giving each concern its own type-level
   representation and its own syntax.

6. **The Wrapping Problem:**
   When each layer adds its own error type (Java: `IOException` →
   `ConfigException` → `AppException`), the error chain grows with the call
   stack. Solutions: Rust's `From` trait (automatic conversion via `?`),
   Go's `%w` (error wrapping with `errors.Is`/`As`), Python's `raise ... from`
   (cause chain), Java's `initCause`. The design tension: wrapping preserves
   context but creates type explosion; not wrapping loses context but keeps
   types simple.

7. **Error Handling in Concurrent Code:**
   Concurrent error handling is under-solved across languages. Python 3.11's
   `ExceptionGroup`/`except*` is the most sophisticated approach — multiple
   errors can be raised and caught simultaneously. Go's `errgroup` collects
   the first error and cancels the rest. Rust's `join_all` on futures returns
   all results but doesn't natively group errors. Swift's task groups collect
   errors from child tasks. Any language with concurrency needs a story for
   "N things can fail at once, and I need all N errors, not just the first."

### What Nomi Should Learn

| Lesson | Source | Nomi Application |
|--------|--------|-----------------|
| Three distinct error stories | Systemic pattern across all languages | Presence/Result/Error already distinct in Nomi; reinforce this separation |
| Defer must run regardless of error path | Go, Python finally, C++ RAII, Swift | Nomi's defer always runs; `_nomi_defer` attribute stripped at desugar time |
| Error propagation must be explicit but brief | Rust `?`, Gleam `try`, Zig `try` | Nomi's `?` (when designed) should reduce to a Result match, not an exception |
| Cleanup must be visible at acquisition point | Zig, Go, Swift defer philosophy | Nomi's defer is immediate, not buried in object protocol |
| Expected failure is not an exception | Rust, Gleam, Zig philosophy | Nomi's `Result[T, E]` is the expected-failure type, distinct from raise |
| Don't collapse absence into error | Swift, Kotlin lesson | Nomi's `?.` and `??` are ONLY about None, never about errors |
| Typed errors are better than bare strings | Rust enums, Zig error sets, Gleam custom types, Scala sealed traits | Nomi's Result carries typed errors; error types should be plain nominal types |
| Monadic composition on Result is ergonomic | Rust, Kotlin, Scala, Haskell | Nomi should consider `and_then` / `map` / `or_else` style combinators on Result |
| Exhaustiveness checking prevents silent error paths | Rust, Java 21 sealed, Scala sealed, Gleam custom types | Nomi's Result match should be checked for exhaustiveness at some level |
| Resource scope should nest naturally | Python ExitStack, Scala Using.Manager, Java try-with-resources | Nomi's defer already supports nesting; LIFO order matches all other languages |
| Exception chaining preserves debugging context | Python `raise from`, Java `initCause`, Go `%w` | Nomi should preserve error cause chains when converting between error representations |
| Concurrent errors need group semantics | Python ExceptionGroup, Swift task groups | Nomi's concurrency model (when built) needs multi-error collection |

---

## Comprehensive Language Comparison Table

| Language | Absence Type | Error Type | Propagation | Cleanup | Panic/Unrecoverable | Distinctive Feature | Transferable to Nomi? |
|----------|-------------|------------|-------------|---------|---------------------|---------------------|----------------------|
| **Swift** | `nil` + `Optional<T>` + `if let`/`guard let`/`??` | `Error` protocol + `throws` + typed throws (Swift 6) | `try`/`try?`/`try!` + `do-catch` with pattern matching | `defer` (LIFO, unconditional) | `fatalError` / `preconditionFailure` / `try!` | Typed throws + optional try in same language; `guard` for early-exit-with-binding | `guard`-style binding pattern; separate nil-coalesce from error-coalesce |
| **Kotlin** | `?` nullable types + `?.`/`?:`/`!!`/`let` | `Result<T>` + unchecked exceptions | `runCatching` + `.map()`/`.recover()`/`.getOrNull()` | `use` for AutoCloseable (like `with`) | `throw` / `error()` (unchecked) | `Nothing` bottom type for compile-time exhaustiveness; null-safety baked into type system | `Nothing`-style bottom type for `fail()`; `?.`/`?:` for nil only |
| **Scala** | `Option[T]` (`Some`/`None`) + pattern matching | `Try[T]` (Success/Failure) + `Either[L, R]` | for-comprehension on Try/Either; `.map()`/`.flatMap()`/`.recover()` | `Using` trait + `Using.Manager` (like ExitStack) | `throw` + no checked exceptions | Try as a monad — for-comprehension with automatic short-circuit; `Using.Manager` for multi-resource scoping | Monadic Try/Either with for-comprehension syntax; `Using.Manager`-style multi-resource blocks |
| **Java** | `Optional<T>` (limited: no pattern matching) | Checked exceptions + `throws` | `try`/`catch`/`finally`; compiler-enforced handling | `try-with-resources` (AutoCloseable) | Unchecked `RuntimeException` | Checked exceptions as original explicit-error-type system; sealed types + pattern matching (21) enable Result-like modeling | Sealed-type Result with exhaustive switch; try-with-resources semantics (suppressed exceptions) |
| **Python** | `None` + `is None` + `or` (no safe navigation) | Exception hierarchy + `try`/`except`/`else`/`finally` | `raise` upward propagation; `raise ... from` for chaining | `with` statement + `contextlib` (ExitStack, suppress, closing) | `raise` (all exceptions are unchecked) | `ExceptionGroup`/`except*` for multiple simultaneous exceptions; `match` statement for pattern matching on exception types; `contextlib` toolkit | ExceptionGroup for concurrent errors; match-based exception dispatch; ExitStack for dynamic resource management |
| **C++** | `std::optional<T>` (C++17) + `value_or` | Exceptions + `std::expected<T, E>` (C++23) | `try`/`catch`/`throw`; `expected.and_then()` | RAII (deterministic destructors) + `noexcept` guarantees | Uncaught exception → `std::terminate` | RAII as deterministic cleanup attached to types; `std::expected` monadic operations; `noexcept` part of type system | RAII-style cleanup via Drop trait; `expected.and_then()`/`.or_else()` combinators |
| **Haskell** | `Maybe a` (`Just`/`Nothing`) + do-notation | `Either e a` + `ExceptT e m a` + `MonadThrow`/`MonadCatch`/`MonadMask` | do-notation `<-` on Either/Maybe; `throwError`/`catchError` | `bracket` (acquire-use-release functional combinator) | `error` / `undefined` (pure); imprecise exceptions in IO | Pure/impure split: exceptions only in IO; `bracket` as functional RAII; `ExceptT` monad transformer for exception-in-any-monad | `bracket` as first-class combinator; pure/impure separation of error handling; do-notation for Result sequencing |
| **Zig** | `?T` (optional type, distinct from error union) | `!T` error union + explicit error sets | `try` (propagates error); `catch` (handle or default) | `defer` (always) + `errdefer` (only on error) | `@panic` / `unreachable` | `errdefer` — deferred cleanup only on error path; error sets as compile-time-inferred structural types | `errdefer` for rollback-on-failure patterns; error set inference at compile time |
| **Rust** | `Option<T>` + `?` operator + `unwrap_or` | `Result<T, E>` + `?` operator + `From` trait | `?` (early return on Err with From conversion) | `Drop` trait (RAII) + ownership/borrowing | `panic!` / `unwrap` / `expect` | Three-tier error story (Option/Result/panic); `?` operator with automatic `From` conversion; exhaustive match on enums | Three-tier error separation; `?` operator design; exhaustive match enforcement |
| **Go** | `nil` + multi-return `(value, ok)` | `(value, error)` multi-return pattern | `if err != nil { return err }` (manual) | `defer` (function-scoped, LIFO) | `panic` (rare, discouraged) | `defer` at function scope; explicit if-err-return convention over special syntax | Unconditional defer; explicit error handling at call site |
| **Gleam** | Unifies absence + error in `Result(a, e)` | `Result(value, error)` + custom types | `try` (pattern-match on Result, short-circuit on Error) | `use` expression (callback desugaring) | `let assert` (crash on pattern mismatch) | `use` — sequential-looking code from callback-passing via pure syntax desugaring; no exceptions at all | `use` expression for callback-to-sequential; `try` as syntactic shorthand for Result match |
| **Erlang/Elixir** | `nil` + pattern matching | `{:ok, value}` / `{:error, reason}` tuples | `with` (Elixir — chained pattern matching with else) | Process termination + supervisors (let it crash) | Crash is the recovery mechanism; supervisors restart | Let-it-crash philosophy + supervisor trees — errors in production are normal, not exceptional | Supervisor-style error recovery for concurrent actors; `with` for chained ok/error matching |
| **Odin** | `nil` + multi-return `(value, ok)` | `(value, error)` multi-return + `or_return` | `or_return` (sugar for if-err-return) | `defer` (scope-scoped, LIFO) | `panic` | `using` for struct-field scope import; `or_return` over multi-return convention; `context` for implicit services | `or_return` syntactic sugar; scope-scoped defer (finer than Go) |
| **Roc** | Tag union `[Ok a, Err e]` | `!` fallibility marker + `Task` type | `?` operator + `<-` in Task pipelines | `Task` lifecycle + platform cleanup | Tag match crash if unhandled | Backend-passing style — all I/O through a platform record; pure/effect split at the type level | Platform-passing for I/O isolation; `!` fallibility marker as part of function type |
