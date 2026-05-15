# BEAM Languages: Erlang, Elixir, Gleam

> Status: source research for Nomi design.
> Purpose: Understand the BEAM ecosystem's innovations — actors, supervision,
> let-it-crash, pattern matching, OTP — and extract lessons for Nomi's
> block/yield model, concurrency posture, and error handling design.

## 1. The BEAM Platform

The BEAM is the virtual machine at the heart of Erlang, Elixir, and Gleam.
It was designed at Ericsson in the 1980s for telecom switches that could not
go down — ever. That origin story shapes every design decision in the VM.

### Lightweight Preemptive Processes

BEAM processes are not OS threads. They are VM-level green threads with a few
KB of initial memory each. A single BEAM node comfortably runs hundreds of
thousands of them. The VM preempts processes at function-call boundaries using
a reduction counter — each function call costs one or more reductions, and
after consuming its budget the process yields to the scheduler. This is
preemptive, not cooperative: a tight infinite loop without function calls will
eventually be preempted by the reduction-count mechanism.

This contrasts sharply with:

- **Go goroutines**: preempted at function calls too, but goroutines share
  memory freely and communicate via channels as a convention, not a rule.
- **Rust async**: purely cooperative — a task that never awaits never yields.
  Rust async is essentially compile-time state machines.
- **JVM virtual threads**: OS-thread-backed carriers that unmount on blocking.
  Preemptive in practice, but heavyweight compared to BEAM processes.
- **Swift actors**: cooperative concurrency with `await` points, closer to
  Rust async than to BEAM processes.

### Message Passing as the Only IPC

BEAM processes share nothing. The only way to communicate is `send(pid, msg)`.
Messages are copied into the receiver's mailbox — there is no shared-memory
hole. This is the Actor Model as originally described by Carl Hewitt, fully
realized.

The mailbox is ordered per-sender but interleaved across senders. Selective
receive lets a process scan its mailbox and defer messages it is not ready to
handle — a unique BEAM capability with no counterpart in Go channels or Rust
mpsc.

### Process Isolation

A crashed process does not corrupt its neighbours. The VM tears down the
process, runs any linked monitors or `EXIT` signals, and leaves the rest of
the system running. This property enables the let-it-crash philosophy: write
the happy path, crash on unexpected states, and let a supervisor restart
cleanly.

### Hot Code Reloading

The BEAM supports swapping module code while the system runs. Two versions of
a module coexist; new calls use the new version, and running processes complete
with the old version. This was essential for telecom (five-nines uptime) but
is less relevant to Nomi's current scope.

### The "Let It Crash" Philosophy

This is the BEAM's defining idea, and the one most worth studying for Nomi.
The principle: defensive code to handle *expected* errors. For *unexpected*
errors, do not clutter the happy path with guards — let the process crash and
let a supervisor decide what to do. A supervisor might restart the process,
restart related processes, give up after N attempts, or escalate.

The insight is organizational, not technical: error recovery is a separate
concern from business logic. Mixing them produces code where 70% of lines are
error paths and the actual logic is buried.

**Nomi note**: This separation of concerns is exactly what Nomi's block/yield
model can express at the block level. A block with a `retry(3)` policy, a
`timeout(5s)` policy, or a `transaction` policy is a miniature supervisor.
The BEAM proves that separating execution from recovery scales from single
processes to entire systems.

---

## 2. Erlang: The Origin

Erlang is a strict, dynamically-typed functional language. Its syntax is
Prolog-inspired (the first Erlang was implemented in Prolog), which makes it
look alien to developers raised on C-family syntax but internally consistent.

### Functional Core

```erlang
% Function with multiple clauses
factorial(0) -> 1;
factorial(N) when N > 0 -> N * factorial(N - 1).

% Anonymous function (fun)
Double = fun(X) -> X * 2 end.
lists:map(Double, [1, 2, 3]).  % → [2, 4, 6]
```

Evaluation is strict (eager). Variables are immutable — once bound, they
cannot be rebound. "Assignment" `X = 5` is actually pattern matching: `X` is
unbound, so it matches and binds to 5. `X = 6` after that is a match error
because 5 does not match 6.

### Pattern Matching Everywhere

Pattern matching is not a feature — it is the fundamental operation of the
language. Every `=` is a match. Function clause selection is pattern matching.
`case` is pattern matching. `receive` is pattern matching on mailbox contents.

```erlang
% Destructuring in function heads
area({square, Side}) -> Side * Side;
area({rectangle, W, H}) -> W * H;
area({circle, R}) -> math:pi() * R * R.

% Case expression
describe(N) ->
    case N of
        0 -> zero;
        1 -> one;
        _ -> many
    end.
```

### Receive and Selective Receive

```erlang
loop(State) ->
    receive
        {increment, N} ->
            loop(State + N);
        {get, From} ->
            From ! {result, State},
            loop(State);
        stop ->
            ok
    after 5000 ->
        io:format("timeout, stopping~n"),
        ok
    end.
```

`receive` scans the mailbox from oldest to newest. If the first message does
not match any clause, it is set aside and the next is tried. A message that
never matches stays in the mailbox forever (mailbox leak). `after` provides a
timeout fallback. This is powerful for protocol implementation but too
low-level for general application code.

### Links and Monitors

- **Links** are bidirectional: when a linked process dies, the other receives
  an `EXIT` signal. If it is not trapping exits, it dies too. Links are the
  backbone of supervision.
- **Monitors** are unidirectional: a monitoring process receives a `DOWN`
  message when the monitored process dies, but is not killed itself.

### Exception Model

```erlang
try
    dangerous_operation()
catch
    error:Reason -> handle_error(Reason);
    throw:Value  -> handle_throw(Value);
    exit:Reason  -> handle_exit(Reason)
after
    cleanup()
end.
```

Three exception classes: `error` (runtime errors), `throw` (non-local return),
`exit` (process termination). The `after` clause runs unconditionally, like
Python's `finally`.

### Bit Syntax

Erlang's bit syntax is unmatched among general-purpose languages. It lets you
pattern-match on binary data at the bit level:

```erlang
<<Version:4, Type:4, Length:16, Payload:Length/binary>> = Packet.
```

This made Erlang the natural choice for network protocol implementation and
remains a unique capability that no other mainstream language provides.

### Comparison: Erlang vs Elixir vs Gleam

| Aspect | Erlang | Elixir | Gleam |
|--------|--------|--------|-------|
| Syntax family | Prolog | Ruby-like | ML/Elm-like |
| Typing | Dynamic | Dynamic | Static (Hindley-Milner) |
| Pipe operator | No (arg-last convention) | `\|>` | `\|>` and `\|>` |
| String type | List of integers | UTF-8 binary | UTF-8 String (wrapper) |
| Module system | `-module`/`-export` | `defmodule`/`def` | `pub fn` |
| Metaprogramming | Preprocessor + parse transforms | Macros (`quote`/`unquote`) | None (by design) |
| Pattern matching | Everywhere | Everywhere + `^` pin | Exhaustive `case` |

---

## 3. Elixir: Modern Ergonomics

Elixir keeps the BEAM semantics — same process model, same VM, same OTP — but
wraps them in a modern, approachable syntax and adds powerful abstractions.

### Control Flow

```elixir
# case with guards
case temperature do
  t when t < 0    -> :freezing
  t when t < 100  -> :liquid
  _               -> :gas
end

# cond — multi-condition without a subject
cond do
  is_nil(x)  -> :empty
  x < 0      -> :negative
  true       -> :positive
end

# with — chaining fallible operations
with {:ok, user} <- fetch_user(id),
     {:ok, posts} <- fetch_posts(user),
     {:ok, _} <- update_last_seen(user) do
  {:ok, posts}
else
  {:error, :not_found} -> {:error, "User not found"}
  {:error, reason} -> {:error, reason}
end
```

The `with` expression is one of Elixir's best ideas. It chains operations
that return `{:ok, value}` / `{:error, reason}` and short-circuits on the
first error. The `else` block lets you normalize different error shapes before
returning. This is the tagged-tuple equivalent of Haskell's do-notation for
Maybe/Either, but more explicit about error shapes.

**Nomi note**: `with` is the closest existing construct to Nomi's block
composition with error propagation. Nomi's `try` expression generalizes this
by making the Result shape part of the value, not a tuple convention.

### Pipe Operator

```elixir
# Without pipe
result = Enum.sum(Enum.filter(Enum.map(input, &(&1 * 2)), &(&1 > 10)))

# With pipe — reads left-to-right, data first
result =
  input
  |> Enum.map(&(&1 * 2))
  |> Enum.filter(&(&1 > 10))
  |> Enum.sum()
```

The pipe operator is Elixir's primary composition mechanism. It threads the
result of each expression as the first argument to the next. This works
because Elixir's standard library follows an "input as first argument"
convention (like Clojure's `->`, not `->>`).

The pipe's real power is not just readability — it is that it encourages
designing functions as small, composable transformations. A pipeline of 10
small functions is clearer than one large function with 10 intermediate
variables.

**Nomi note**: Nomi already has `|>`. The lesson from Elixir is to design the
standard library around it: make the "main" argument consistently the first or
last parameter, and make functions small enough that a pipeline feels natural
rather than forced.

### Protocols

```elixir
defprotocol Size do
  def size(data)
end

defimpl Size, for: List do
  def size(list), do: length(list)
end

defimpl Size, for: Map do
  def size(map), do: map_size(map)
end

defimpl Size, for: BitString do
  def size(str), do: byte_size(str)
end
```

Protocols provide polymorphism without inheritance. Any type can implement any
protocol, even types defined in other libraries. This is structurally similar
to Clojure protocols, Rust traits (but without the type parameter), and Go
interfaces (but explicit rather than structural).

### `use` Macro for DSL Construction

```elixir
defmodule MyServer do
  use GenServer

  def handle_call(:get_state, _from, state) do
    {:reply, state, state}
  end
end
```

`use` injects code at compile time — typically setting up module attributes,
importing functions, and defining default callbacks. Combined with Elixir's
macro system, this enables clean DSLs. But it comes at a cost: `use` obscures
what code is actually running, and macro-heavy Elixir projects can be hard to
debug.

**Nomi note**: Gleam deliberately excluded macros. Nomi should tread carefully:
DSL construction via block calls and surface syntax lowering is more
transparent than compile-time code injection.

### GenServer, Task, Agent Abstractions

- **Task**: fire-and-forget or awaitable async work. Wraps `spawn` behind a
  simple API.
- **Agent**: simple state holder. GenServer with only `get`/`update`.
- **GenServer**: the universal server. Handles synchronous calls, asynchronous
  casts, and direct messages.

These abstractions show the layered design of OTP: give users a simple
interface for simple cases, and let them drop down to GenServer when they
need more control.

### Supervisor Strategies

```elixir
Supervisor.start_link(children,
  strategy: :one_for_one   # restart only the crashed child
  # :one_for_all           # restart ALL children if any crash
  # :rest_for_one          # restart crashed child + children after it
)
```

The three strategies encode different dependency assumptions:

- `one_for_one`: children are independent. A crash in one does not affect
  others.
- `one_for_all`: children are tightly coupled. All must be restarted together
  to reach a consistent state.
- `rest_for_one`: children form a pipeline. If an earlier stage crashes, later
  stages must restart too.

**Nomi note**: These strategies map directly onto block composition patterns.
`one_for_one` is parallel blocks with independent recovery. `one_for_all` is a
transactional block. `rest_for_one` is a sequential pipeline where failure
propagates forward.

---

## 4. Gleam: Types on the BEAM

Gleam is a statically-typed language compiling to both BEAM and JavaScript.
It keeps Erlang's interop and OTP compatibility while adding an ML-style type
system with full type inference.

### ML-Style Static Typing

```gleam
pub type Temperature {
  Celsius(Int)
  Fahrenheit(Int)
}

pub fn to_celsius(temp: Temperature) -> Int {
  case temp {
    Celsius(n) -> n
    Fahrenheit(n) -> (n - 32) * 5 / 9
  }
}
```

The type system is Hindley-Milner (like OCaml, Haskell, Elm). Types are
inferred everywhere — you rarely write type annotations except on exported
functions. The compiler catches exhaustiveness errors, type mismatches, and
unused variables at compile time.

### Case with Exhaustiveness Checking

```gleam
case result {
  Ok(value) -> process(value)
  Error(reason) -> log_error(reason)
}
// Compiler ERROR if you forget the Error branch
```

Gleam's `case` is exhaustive. The compiler knows all constructors of a type
and requires every branch to be handled. This eliminates a whole class of
runtime errors — the "I forgot to handle this case" bug that plagues dynamic
language code.

### `use` Expression (Monadic Sugar)

Gleam's `use` is different from Elixir's — it is sugared callback passing:

```gleam
// Without use — explicit callback
result.map(fn(db) {
  db.insert(user)
  db.insert(profile)
})

// With use — flattened
use db <- result.map
db.insert(user)
db.insert(profile)
```

The `use` expression takes the rest of the block as a callback and passes it
to the right-hand function. This is general sugar — it works with `result.map`,
`result.try`, `bool.guard`, and any function that takes a callback. It is
Gleam's answer to Haskell's `do` notation, but simpler and not tied to monads.

**Nomi note**: Gleam's `use` is structurally identical to Nomi's block calls.
Both are syntactic sugar for "take this block, turn it into a callback, and
pass it to a function." The key insight is that you only need ONE such
mechanism — you do not need separate `async/await`, `for/yield`, and
`with/do` syntax. One good block-passing sugar covers all of them.

### Try Expression

```gleam
try
  user = fetch_user(id)
  posts = fetch_posts(user)
  update_last_seen(user)
  Ok(posts)
catch
  NotFound -> Error("Not found")
end
```

Gleam's `try` is a dedicated Result-chaining expression. It is more
specialized than `use` but provides a very clean syntax for the common case
of chaining fallible operations. The compiler enforces that both the happy
path and the catch path produce the same outer type (`Result(a, e)` typically).

### No `nil` — `Result` and `Option`

Gleam has no null/nil. Functions that can fail return `Result(value, error)`.
Optional values use `Option(value)` with `Some(x)` and `None`. This is the
standard ML approach and eliminates null-pointer exceptions entirely.

Compare with:

- **Elixir**: uses `nil` conventionally. `{:ok, val}` / `{:error, reason}`
  is a convention, not a type.
- **Erlang**: also convention-based. `undefined` is the sentinel.
- **Rust**: same approach as Gleam — `Option<T>` and `Result<T, E>` are proper
  sum types.

**Nomi note**: Nomi's `Result[T, E]` follows Gleam's path. The lesson is that
making error/absence part of the type system, not a convention, eliminates an
entire category of bugs that plague Erlang and Elixir codebases.

---

## 5. OTP Design Patterns

OTP (Open Telecom Platform) is the real secret weapon of the BEAM. It is a set
of libraries, design principles, and battle-tested patterns that turn raw
processes into reliable systems.

### GenServer — The Universal Server

```elixir
defmodule Counter do
  use GenServer

  # Client API (runs in caller's process)
  def increment(pid, n), do: GenServer.call(pid, {:increment, n})
  def get(pid), do: GenServer.call(pid, :get)

  # Server callbacks (run in server process)
  @impl true
  def handle_call({:increment, n}, _from, state), do: {:reply, :ok, state + n}
  def handle_call(:get, _from, state), do: {:reply, state, state}
end
```

The GenServer separates client API from server logic. The client functions
run in the caller's process — they send messages and wait. The callbacks run
in the server's process — they process messages sequentially.

Three callback types:

- `handle_call`: synchronous request-response. Caller blocks until reply.
- `handle_cast`: asynchronous fire-and-forget. No reply.
- `handle_info`: handles direct messages that were not sent via `call`/`cast`

The return tuple from callbacks encodes both the reply and the next state.
This is functional programming applied to stateful servers: each callback
is a pure function from `(message, current_state)` to `(reply, next_state)`.

### Supervision Trees

```
                  +-----------+
                  | Supervisor|
                  | (one_for_ |
                  |   one)    |
                  +-----+-----+
                        |
          +-------------+-------------+
          |             |             |
    +-----v-----+ +----v------+ +----v------+
    | Worker A  | | Supervisor| | Worker C  |
    |           | | (rest_for | |           |
    +-----------+ |   _one)   | +-----------+
                  +-----+-----+
                        |
              +---------+---------+
              |                   |
        +-----v-----+      +-----v-----+
        | Worker B1 |      | Worker B2 |
        |           |      |           |
        +-----------+      +-----------+
```

A supervision tree is a hierarchy of processes where parents monitor and
restart children. The tree shape encodes the dependency structure:

- **Workers**: leaf processes that do the actual work. When a worker crashes,
  its supervisor decides what to restart.
- **Supervisors**: interior nodes that only supervise. Supervisors should be
  simple enough that they never crash — if a supervisor crashes, its parent
  handles it.

The tree is not just an architectural diagram — it is the runtime structure.
Every process is linked to its parent, so a crash signal propagates up the
tree until a supervisor can handle it.

### DynamicSupervisor

For processes that need to be started at runtime (user sessions, connections,
dynamic workers), `DynamicSupervisor` lets you start and stop children without
declaring them at boot time. The supervisor still tracks and restarts them.

### Registry for Process Discovery

```elixir
{:ok, _} = Registry.start_link(keys: :unique, name: MyRegistry)
Registry.register(MyRegistry, "user:42", %{pid: self()})
[{pid, value}] = Registry.lookup(MyRegistry, "user:42")
```

The Registry maps names to PIDs without a single bottleneck process. Each
partition of the registry runs independently, enabling parallel lookups.

### ETS / DETS

- **ETS**: in-memory key-value store, shared between processes, with
  per-table concurrency. Think Redis but in-process.
- **DETS**: disk-based version of ETS. Survives restarts.

ETS tables can be `set`, `ordered_set`, `bag`, or `duplicate_bag`. They
support pattern-matching queries using match specifications — essentially
a mini query language expressed as Erlang terms.

### Applications and Releases

An OTP application is a component with a lifecycle: `start/2` and `stop/1`
callbacks. Applications declare dependencies on other applications. A release
bundles the BEAM VM, all needed applications, and configuration into a single
deployable artifact.

### Comparison: OTP vs Other Concurrency Frameworks

| Aspect | OTP | Akka (JVM) | Orleans (C#) | Swift Actors |
|--------|-----|------------|--------------|--------------|
| Process model | VM green threads | JVM threads | Virtual actors | Cooperative |
| Isolation | Full memory isolation | Object isolation | Object isolation | Actor isolation |
| Supervision | Built-in, hierarchical | Built-in, hierarchical | Via placement | Manual |
| Message passing | Copy, selective receive | ActorRef tell/ask | Async methods | `await` calls |
| State management | Functional callbacks | Mutable, become() | Mutable fields | Mutable, isolated |
| Hot reload | Yes | No | Via partitioning | No |

---

## 6. Pattern Matching in the BEAM Family

Pattern matching is the central control-flow mechanism across all three BEAM
languages. Understanding its evolution from Erlang through Gleam reveals what
is essential and what is historical.

### Multi-Clause Functions

```erlang
% Erlang: each clause is a separate match attempt
eval({add, A, B}) -> eval(A) + eval(B);
eval({mul, A, B}) -> eval(A) * eval(B);
eval({const, N}) when is_number(N) -> N;
eval(_) -> error(bad_expr).
```

```elixir
# Elixir: guard clauses with `when`
def eval({:add, a, b}), do: eval(a) + eval(b)
def eval({:mul, a, b}), do: eval(a) * eval(b)
def eval({:const, n}) when is_number(n), do: n
def eval(_), do: raise "bad expression"
```

```gleam
// Gleam: single function, case inside
pub fn eval(expr: Expr) -> Int {
  case expr {
    Add(a, b) -> eval(a) + eval(b)
    Mul(a, b) -> eval(a) * eval(b)
    Const(n) -> n
  }
}
```

Gleam does not have multi-clause functions by design. Instead, it uses
`case` inside a single function body. This is a deliberate simplification:
multi-clause functions interact confusingly with default arguments, and a
single `case` body is easier to reason about.

### Pin Operator (Elixir)

```elixir
x = 1
{x, ^x} = {2, 1}  # OK: x is rebound to 2, ^x means "match existing x" (1)
{x, ^x} = {2, 2}  # MatchError: ^x expects 1 but got 2
```

The pin `^` forces a match against the existing binding rather than rebinding.
This is Elixir's solution to a problem Erlang avoids by making all variables
single-assignment. Since Elixir allows rebinding, the pin is needed to
disambiguate "match existing value" from "bind new value."

Erlang does not need pin because variables cannot be rebound at all — `X = 1`
then `X = 2` is a match error in Erlang.

### Guard Clauses

Guards are a restricted set of expressions that can run in pattern-matching
contexts. The restriction exists because guards must be side-effect-free and
must not fail — they run during pattern matching, not after.

Erlang/Elixir allow only: comparisons, boolean operations, arithmetic, type
checks (`is_number`, `is_list`), and a few built-in functions (`abs`, `length`,
`map_size`, etc.). Custom functions are NOT allowed in guards.

Haskell does not restrict guards: any pure expression can appear. This is
possible because Haskell's type system guarantees purity at the type level.
BEAM languages cannot make that guarantee.

Gleam avoids guards entirely — use `if` or nested `case` inside branches
instead. This is cleaner but more verbose for arithmetic conditions.

### Comparison: Pattern Matching Across Languages

| Feature | Erlang | Elixir | Gleam | Haskell | Rust | Scala |
|---------|--------|--------|-------|---------|------|-------|
| Multi-clause functions | Yes | Yes | No | Yes | No | No |
| Pin operator | N/A (single-assign) | `^` | N/A (single-assign) | N/A | `ref` | Backticks |
| Guard clauses | Yes (restricted) | Yes (restricted) | No | Yes (unrestricted) | `if` guards | Yes (unrestricted) |
| Exhaustiveness check | Warn (dialyzer) | Warn (dialyzer) | Compile error | Compile warn | Compile error | Compile warn |
| Nested patterns | Yes | Yes | Yes | Yes | Limited | Yes |
| As-patterns | No | `=` in patterns | Yes (`as`) | Yes (`@`) | Yes (`@`) | Yes (`@`) |
| Or-patterns | `;` in clauses | Partial (v1.12+) | Yes (`\|`) | No | Yes (`\|`) | Yes (`\|`) |

**Nomi note**: The key design choice is whether to have multi-clause functions
or single-body-with-case. Gleam chose single-body for simplicity. Nomi should
follow Gleam here: one function body, `case`/`match` for branching. Multi-clause
functions interact poorly with default arguments, keyword arguments, and
documentation tooling.

---

## 7. Error Handling Across the BEAM

Error handling is where the three BEAM languages diverge most sharply. Erlang
has a dual model (exceptions + return values). Elixir adds `with` and `rescue`.
Gleam eliminates exceptions entirely for application code. Each approach
reveals something about the trade-off between explicitness and ergonomics.

### Let It Crash (Philosophy, Not Just a Catchphrase)

The core principle: do not write defensive code for unrecoverable errors.
If a file should exist but does not, crash. The supervisor restarts. If a
network connection drops, crash. The supervisor restarts. The corollary:
only handle errors you can meaningfully recover from.

This is NOT "ignore errors." It is "separate error recovery from business
logic." Error recovery lives in supervisors. Business logic lives in workers.
The worker's job is to do the work or crash cleanly.

### Erlang: Error Returns vs Exceptions

Erlang codebases often mix two styles:

```erlang
% Style 1: Tagged return values (convention)
open_file(Name) ->
    case file:open(Name, [read]) of
        {ok, Fd} -> {ok, Fd};
        {error, Reason} -> {error, {open_failed, Name, Reason}}
    end.

% Style 2: Let it crash (supervisor handles it)
open_file!(Name) ->
    {ok, Fd} = file:open(Name, [read]),  % crashes on error
    Fd.
```

The `!` suffix convention marks functions that crash on error rather than
returning a tagged tuple. This is similar to the Rust `unwrap()` convention
but at the naming level rather than the type level.

### Elixir: `with`, `try`, `rescue`

```elixir
# with for chaining tagged tuples
with {:ok, user} <- fetch_user(id),
     {:ok, _} <- validate(user),
     {:ok, result} <- process(user) do
  {:ok, result}
else
  {:error, :not_found} -> {:error, "missing"}
end

# try/rescue for exceptions
try do
  dangerous()
rescue
  RuntimeError -> handle()
  e in ArgumentError -> handle_arg(e)
after
  cleanup()
end
```

The split between `with` (for `{:ok, :error}` tuples) and `try`/`rescue`
(for exceptions) reflects a tension in Elixir's design: the language has
both convention-based error handling and exception handling, and choosing
between them is ad-hoc.

### Gleam: `Result` Type and `try`

```gleam
pub fn open_config(path: String) -> Result(Config, ConfigError) {
  try
    contents = file.read(path)
    parsed = parse_config(contents)
    validate_config(parsed)
  catch
    FileError(e) -> Error(ConfigError(e))
    ParseError(e) -> Error(ConfigError(e))
  end
}
```

Gleam eliminates exceptions for application code. Functions return
`Result(t, e)` or `Option(t)`. The `try` expression chains these.
There is no `throw`, no `raise`, no `catch Exception` hierarchy.
The type system ensures you handle both success and error paths.

This is the cleanest error model on the BEAM and aligns with modern
consensus (Rust, Swift, Kotlin all moving toward typed errors).

### Comparison: Error Handling Models

| Language | Primary mechanism | Error type | Unwrap/Crash | Convention or type? |
|----------|------------------|------------|--------------|---------------------|
| Erlang | Tagged tuples + exceptions | Dynamic | Pattern match crash | Convention |
| Elixir | `with` + `try`/`rescue` | Dynamic | `!` functions | Convention + syntax |
| Gleam | `Result` + `try` | Static (sum type) | `let assert Ok(x) =` | Type system |
| Rust | `Result` + `?` | Static (enum) | `unwrap()` | Type system |
| Go | Multiple return `(val, err)` | Dynamic (error interface) | `panic` | Convention |
| Zig | Error unions `!T` + `try` | Static (error set) | `catch unreachable` | Type system |
| Swift | `throws` + `do`/`catch` | Static (error protocol) | `try!` | Type system |

**Nomi note**: Gleam and Rust converge on the same answer: typed errors via sum
types, with syntactic sugar for propagation (`try` in Gleam, `?` in Rust).
Nomi should follow this path. The `let it crash` philosophy can coexist: a
process (or block) can choose to crash on errors it cannot handle, while
still using typed `Result` for errors it propagates upward.

---

## 8. What Nomi Should Learn from the BEAM

### Adopt

**Pipe operator philosophy.** Elixir proved that `|>` is not just syntactic
sugar — it is a design principle. When the standard library is designed
around the pipe, code becomes easier to write, read, and refactor. Nomi
already has `|>`. The lesson is to design the library ecosystem around it.

**Pattern matching as the primary branching mechanism.** Across all three
BEAM languages, pattern matching is the first tool for control flow, not a
niche feature. `if`/`else` chains are a distant second choice. This aligns
with Nomi's design direction: matching against shapes (types, structures,
results) is more readable and more maintainable than cascading conditionals.

**`with`-style chaining for fallible operations.** Elixir's `with` expression
captures a universal pattern: chain N operations, stop at the first error,
normalize different error shapes. Nomi's `try` expression generalizes this
by making the Result type explicit rather than relying on tuple convention.

**Gleam's `use` expression as block-call precedent.** Gleam's `use` is proof
that a single mechanism — callback-passing sugar — can cover many use cases
that other languages need separate syntax for. Nomi's block calls are the same
idea. The Gleam community's positive reception validates the approach.

**Erlang's bit syntax as a future data boundary.** Structural matching on
binary data is a genuine superpower. Nomi should not copy the syntax, but the
concept of bit-level structural matching is worth keeping as a future
extension point in Nomi's data boundary design.

**Supervision as block policy.** OTP supervisors and Nomi's block policies
(`retry`, `timeout`, `transaction`) solve the same problem: separate execution
logic from recovery logic. The BEAM's 30-year track record with supervision
trees validates this separation of concerns.

### Refuse/Defer

**Full actor model for Nomi's first language.** Actors are powerful but
require rethinking the entire runtime. Every value crossing a process boundary
must be copied (or, in some implementations, the VM must guarantee immutability
at the memory level). This is too large a commitment for Nomi v1.

**Hot code reloading.** This is an operational concern, not a language concern.
It requires VM support, module versioning, and careful state migration. Nomi
should focus on language-level features first.

**`receive` with selective message matching.** Too low-level for application
code. Even in Elixir, `receive` is rarely used directly — `GenServer` and
`Task` wrap it. Nomi should provide higher-level concurrency abstractions.

**Erlang's `;` `.` `,` syntax distinctions.** Sentences end with `.`, clauses
end with `;`, sub-expressions end with `,`. This is the single biggest source
of syntax errors for newcomers to Erlang. Nomi should avoid terminator
distinctions that encode structural meaning.

**Elixir's macro-heavy DSL construction.** Macros are powerful but create
"spooky action at a distance" — code that does not mean what it looks like it
means. Gleam's rejection of macros was a deliberate choice for predictability.
Nomi should prefer surface syntax lowering (transparent, inspectable) over
macro-based DSLs.

### Adapt

**OTP supervision trees -> Nomi block policies.** OTP supervision encodes
recovery strategies in the runtime structure. Nomi's block policies encode
recovery strategies in the syntactic structure. Both separate "what to do"
from "what to do when it fails":

| OTP Concept | Nomi Equivalent |
|-------------|-----------------|
| `one_for_one` supervision | Parallel blocks with independent retry |
| `one_for_all` supervision | Transactional block (all-or-nothing) |
| `rest_for_one` supervision | Sequential pipeline with propagation |
| `max_restarts` / `max_seconds` | `retry(n, within: t)` |
| `DynamicSupervisor` | Blocks spawned at runtime with policies |
| `Supervisor.start_child` | `spawn` block with inherited policy |

**`{:ok, value}` / `{:error, reason}` -> Nomi's `Result[T, E]`.** The tagged
tuple convention works but is a convention, not a guarantee. Gleam and Rust
show that making Result a proper type eliminates entire categories of bugs.

**Elixir protocols -> Nomi's extension methods.** Protocols enable polymorphism
without inheritance. Nomi's extension methods (design-needed) should support
the same pattern: define an interface, implement it for any type, dispatch
based on the type of the first argument.

**Gleam's `use` -> Nomi's block calls.** Both are sugar for callback passing.
The design principle: provide ONE general mechanism rather than separate
`async/await`, `for/yield`, `with`/`do`, and `transaction {}` syntax. Let
libraries define the semantics; let the language provide the sugar.

---

## 9. Cross-Language Synthesis

### Concurrency Model Comparison

| Platform | Model | Scheduling | Memory model | Error propagation | Key abstraction |
|----------|-------|------------|--------------|-------------------|-----------------|
| BEAM | Actors, no shared memory | Preemptive (reduction counts) | Process isolation, copy | Links, monitors, supervisors | OTP GenServer |
| Go | Goroutines + channels | Preemptive (function preemption) | Shared memory | Error returns, `recover` | `go` + channels |
| Rust | Async tasks | Cooperative (poll-based) | Ownership + borrowing | `Result`, `panic` | `Future` trait |
| Swift | Actors + async/await | Cooperative | Actor isolation | `throws`, `try` | `actor` keyword |
| Kotlin | Coroutines | Cooperative (suspend) | Shared memory | `Result`, `runCatching` | `suspend` functions |
| Java (21+) | Virtual threads | Preemptive (unmount on block) | Shared memory | Exceptions, `Future` | `Thread.startVirtual` |

The BEAM's process isolation is the strongest guarantee: a process crash
physically cannot corrupt another process's memory. Go's goroutines share
memory freely — the `go` race detector is a best-effort tool, not a guarantee.
Rust's type system prevents data races but not deadlocks or logic errors.

**Nomi note**: Nomi's initial concurrency posture should be conservative. The
BEAM teaches that strong isolation (no shared memory) simplifies error
recovery, but it also requires a VM built for it. Nomi should start with a
simpler model (e.g., async blocks) and leave actor-model semantics as a
future language layer.

### Let-It-Crash vs Defensive Programming

The let-it-crash philosophy stands in opposition to Rust's "handle every error
at the point of occurrence" and Go's "if err != nil" dogma:

| Approach | Philosophy | Error location | Recovery location |
|----------|------------|----------------|-------------------|
| BEAM (let it crash) | Happy path only | Crash point (process dies) | Supervisor (up the tree) |
| Rust | Handle or propagate | `?` operator | Caller (up the stack) |
| Go | Handle explicitly | `if err != nil` | Same function or caller |
| Java/Python | Catch or declare | `try`/`catch` | Caller or logging |
| Erlang/Elixir (with) | Chain and short-circuit | `with` expression | Single error handler |

The BEAM approach works because of process isolation. A crashed process
releases all resources, and the supervisor starts a fresh one. Without
process isolation, let-it-crash is dangerous — a crash might leave shared
state inconsistent.

**Nomi note**: Nomi can adopt the let-it-crash philosophy at the block level
without requiring full process isolation. A block with a `transaction`
policy that rolls back on failure gives you the same guarantee: the block body
only needs to handle the happy path, and the policy handles recovery.

### Erlang/Elixir Pattern Matching vs ML-Family Pattern Matching

BEAM pattern matching developed independently from ML-family matching but
converged on similar capabilities:

| Aspect | BEAM (Erlang/Elixir) | ML (OCaml/Haskell/F#) |
|--------|---------------------|----------------------|
| Origin | Prolog unification | Algebraic data types |
| Arity | Fixed (no currying) | Curried by default |
| Guards | Restricted functions | Unrestricted (Haskell) or `when` (OCaml, limited) |
| Exhaustiveness | Optional (dialyzer) | Compiler checked |
| Nested patterns | Yes | Yes |
| Or-patterns | Partial | Yes (Haskell no, OCaml yes) |
| View patterns | No | Yes (Haskell, F#) |

The convergence is interesting: two communities, starting from different
foundations (unification vs ADTs), arrived at very similar pattern-matching
facilities. This suggests pattern matching is a "local maximum" in language
design — a stable, well-understood feature that every language should include.

### The BEAM as a Platform vs Language-Level Features

A key lesson from the BEAM ecosystem: many features that feel like "language"
features are actually VM features:

| Feature | VM-dependent? | Could be syntax sugar? |
|---------|---------------|------------------------|
| Process spawning | Yes (scheduler, isolation) | No |
| Message passing | Yes (mailbox, copy semantics) | Partially (async/await is sugar) |
| Selective receive | Yes (mailbox scan) | No |
| Pattern matching | No (purely syntactic) | Yes |
| Pipe operator | No (function call sugar) | Yes |
| `with` expression | No (control flow sugar) | Yes |
| `use` expression | No (callback sugar) | Yes |
| Hot code reload | Yes (code server, versioning) | No |
| Supervision trees | No (design pattern) | Yes (can be library) |
| Bit syntax | Partially (binary VM type) | Partially |

**Nomi note**: Nomi should be opinionated about what belongs in the language
vs what belongs in libraries. Pattern matching, pipes, block calls, and `try`
are language features because they shape how every program is written.
Supervision, registry, ETS are library/pattern concerns that can be built on
top. Hot code reload is an operational feature that is not relevant to Nomi's
design layer.

---

## 10. Comparison Tables

### Table 1: BEAM Languages Comparison

| Dimension | Erlang | Elixir | Gleam |
|-----------|--------|--------|-------|
| **First appeared** | 1986 | 2011 | 2019 |
| **Paradigm** | Functional, dynamic | Functional, dynamic, macro | Functional, static |
| **Type system** | Dynamic, optional (dialyzer) | Dynamic, optional (dialyzer) | Static, Hindley-Milner inference |
| **Syntax heritage** | Prolog | Ruby | Elm/OCaml |
| **Pipe operator** | No (convention) | `\|>` | `\|>` |
| **Pattern matching** | Multi-clause, guards | Multi-clause, guards, `^` pin | `case` exhaustive |
| **Error model** | Tagged tuples + exceptions | Tagged tuples + exceptions | `Result` type + `try` |
| **Null/nil** | `undefined` atom | `nil` atom | No null (`Option`) |
| **Metaprogramming** | Parse transforms | Macros (`quote`/`unquote`) | None (deliberate) |
| **String type** | List of integers | UTF-8 binary | UTF-8 String |
| **Records/Structs** | Records (compile-time) | Structs (map-based) | Custom types |
| **Module system** | Flat, `-module`/`-export` | Nested `defmodule`/`def` | Flat, `pub fn` |
| **Tooling** | rebar3, erlang.mk | Mix, Hex | Gleam build tool |

### Table 2: Concurrency Model Comparison

| Dimension | BEAM | Go | Rust (tokio) | Swift | Kotlin | Java (Loom) |
|-----------|------|----|--------------|-------|--------|-------------|
| **Unit** | Process (green) | Goroutine | Task | Task | Coroutine | Virtual thread |
| **Scheduling** | Preemptive (reduction) | Preemptive (preemption) | Cooperative (poll) | Cooperative (await) | Cooperative (suspend) | Preemptive (unmount) |
| **Memory model** | Copy, isolated | Shared memory | Ownership, no races | Actor isolation | Shared memory | Shared memory |
| **IPC** | Message passing | Channels (convention) | Channels | Actor methods | Channels | Shared state |
| **Error isolation** | Full (crash = process death) | Partial (panic in goroutine) | Partial (panic = abort) | Partial (task cancel) | Partial (exception in coroutine) | Partial (exception in thread) |
| **Supervision** | Built-in (OTP) | None (library) | None (library) | None (manual) | None (manual) | None (manual) |
| **Built-in timeouts** | `receive ... after` | `context.WithTimeout` | `tokio::time::timeout` | `Task.sleep` + cancel | `withTimeout` | `Future.get(timeout)` |
| **Typical scale** | 100K–1M processes | 10K–100K goroutines | 1K–10K tasks | 1K–10K tasks | 1K–10K coroutines | 10K–100K threads |

### Table 3: Pattern Matching Features Across BEAM Languages

| Feature | Erlang | Elixir | Gleam |
|---------|--------|--------|-------|
| Multi-clause functions | Yes (`;` separated) | Yes (`do`/`end` each) | No (single body + `case`) |
| Guard clauses | Yes (`when ...`) | Yes (`when ...`) | No (use `if` in branch) |
| Pin operator | N/A (single assignment) | `^var` | N/A (single assignment) |
| List destructuring | `[H\|T]` | `[h\|t]` | `[head, ..tail]` |
| Tuple destructuring | `{A, B, C}` | `{a, b, c}` | `#(a, b, c)` |
| Map/Record destructuring | `#{key := V}` | `%{key: v}` | Record field access |
| Binary matching | `<<A:8, B:16>>` | `<<a::8, b::16>>` | No (use library) |
| Exhaustiveness check | Optional (dialyzer) | Optional (dialyzer) | Required (compile error) |
| Or-patterns | `;` in case clauses | Partial (v1.12+) | Yes (`\|` in branches) |
| As-patterns | No | `=` in patterns | `variable as pattern` |
| Wildcard | `_` | `_` | `_` |
| String matching | List pattern on codepoints | Binary matching `<<s::utf8>>` | No |

---

## Synthesis: The BEAM's Architecture Lesson for Nomi

The BEAM ecosystem achieves something rare: three languages (one dynamic with
Prolog syntax, one dynamic with Ruby syntax, one static with ML syntax) sharing
one VM and one set of runtime guarantees. The grammar changes; the error model
evolves; the type system varies. But the architectural spine — isolated
processes, message passing, supervision — stays constant.

This separation of concerns is the deepest lesson for Nomi. The BEAM
demonstrates that:

1. **Syntax is a skin.** Erlang, Elixir, and Gleam look completely different
   but share the same runtime guarantees. Nomi should be similarly comfortable
   with multiple surface syntaxes (`.nomi` files, block syntax, notebook cells)
   that compile to the same core.

2. **Error recovery is a separate axis.** Let-it-crash is not a syntax feature
   or a type system feature — it is an architectural commitment. Nomi's block
   policies (`retry`, `timeout`, `transaction`) can provide the same separation
   without requiring a full actor model.

3. **One good sugar mechanism beats many special ones.** Gleam's `use` covers
   what other languages need `async`, `await`, `for`, `yield`, `do`, and `with`
   for. Nomi's block calls follow the same principle. The BEAM ecosystem
   validates that "one general mechanism, many library uses" is a sustainable
   design.

4. **Convention-based error handling degrades at scale.** Erlang's tagged
   tuples and Elixir's `{:ok, :error}` work for small codebases but fail to
   scale without type enforcement. Gleam's `Result` type is the correct answer
   for a modern language. Nomi's `Result[T, E]` should follow Gleam's lead.

5. **Pattern matching is a solved problem.** Three different syntaxes, three
   different type system stances — all converge on pattern matching as the
   primary branching mechanism. Nomi should treat pattern matching on
   types/structures/results as the default, with `if`/`else` as the fallback
   for simple boolean conditions.

6. **The pipe is a cultural force.** Elixir's `|>` reshaped not just code
   style but library design. Functions were redesigned to be pipe-friendly.
   Nomi adopting `|>` is the first step; the second step is designing the
   standard library so that every function composes cleanly in a pipeline.

The BEAM's 35-year arc — from Ericsson's telecom switches to Gleam's
type-safe web servers — shows that a well-designed runtime platform
outlasts syntax trends. Nomi's challenge is to find its own version of this:
a small, coherent core that supports multiple surface languages and scales
from scripts to systems.
