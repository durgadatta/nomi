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
