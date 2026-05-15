# Concurrency & Async Convenience

> Normal forms: Block + Flow. The block/yield model is the one control
> abstraction — async, iteration, resource management, and structured
> concurrency are all block policies, not separate function colors.
>
> Deep research: [cross_language_synthesis_master.md §4.5](../research/cross_language_synthesis_master.md)
> (capstone block normal form),
> [beam_languages_erlang_elixir_gleam.md](../research/beam_languages_erlang_elixir_gleam.md)
> (OTP, supervision trees, let-it-crash, Gleam `use`).
>
> Companion: [design_lessons_and_integration.md §7.1](design_lessons_and_integration.md)
> for the function-color systemic pattern and why Nomi avoids it.

## Design Pressure

Every language that added a second function color (async/sync) later regretted
the ecosystem split: Python `async def`, JavaScript `async`, Rust `async fn`,
Kotlin `suspend`. They all created executor/library fragmentation, "what color
is my function" as permanent cognitive overhead, and bridging code at every
color boundary.

Nomi's position: the block/yield model is the one control abstraction. If
concurrency is added, it must be via block policies, not `async def`.

## Normal Form

Concurrency features reduce to the block and flow normal forms:

```text
block policy → callee controls scheduling, cancellation, and cleanup
flow → parallel operations over collections
```

The callee uses `yield` — a single, general mechanism — whether the caller is
retrying, tracing, iterating, or running concurrently.

## 1. Async/Await (Python-Compatible)

Python's `async def` / `await` is available for interop but is not the Nomi
concurrency design target. It exists because Nomi runs on Python and must
interoperate with Python's async ecosystem.

**Status:** available for Python interop only. Not the long-term concurrency
model.

## 2. Structured Concurrency (Future)

Scoped coroutines that ensure cleanup and prevent leaks. Grow from block
calls, cancellation, result values, and capability boundaries.

```nomi
# Future direction — not implemented:
parallel:
    a = fetch(url_a)
    b = fetch(url_b)
result = (a, b)
```

### Design (from cross-language synthesis)

The block-policy approach means the concurrency scope is an ordinary call with
an attached block. Cancellation, timeout, and cleanup are policies the callee
applies, not keywords in the language. This design follows from the capstone
synthesis ([cross_language_synthesis_master.md §4.5](../research/cross_language_synthesis_master.md))
and BEAM platform analysis ([beam_languages_erlang_elixir_gleam.md](../research/beam_languages_erlang_elixir_gleam.md)).

**Core principles (design-settled):**

- **No function coloring.** `yield` is the single control-transfer mechanism.
  Concurrency is not a separate function family — it's a block policy.
- **Supervision as block policy.** The callee manages child task lifecycle,
  restart, and cleanup (Erlang/OTP supervision tree model, adapted to block
  calls).
- **Cancellation is a block concern.** Cancelling a block cancels all child
  blocks it spawned. The cancellation propagates through the yield mechanism.
- **Error handling in concurrent contexts uses `Result` + `match`.** When a
  child task fails, the parent receives `Err(...)` via the block mechanism.
  Exceptions are for unexpected errors only.
- **`defer` runs on block exit**, including cancellation exit — cleanup is
  guaranteed regardless of how the block terminates.

**Prerequisites (must be settled first):**
- Block-call semantics (implemented — see [block_calls_feature.md](../features/block_calls_feature.md))
- `Result[T, E]` type (design-settled — see [absence_and_result.md](absence_and_result.md))
- Cancellation semantics (design-needed — sketched below)
- Diagnostics for concurrent failures (design-needed)

### Cancellation Semantics (Sketch)

Cancellation is cooperative (not preemptive). A block polls for cancellation
at yield points:

```nomi
# The callee checks for cancellation; the block yields control
func fetch_with_timeout(url, timeout):
    timer = start_timer(timeout)
    defer timer.cancel()
    yield  # check for cancellation
    result = http.get(url)
    yield  # check again
    return result
```

The key invariant: cancellation only happens at `yield` points, so all cleanup
(`defer` blocks) runs deterministically.

**Status:** design-settled for the approach (block policies, no function
coloring, supervision). Implementation waits for block calls, cancellation,
and `Result` to be settled.

### Channels / Actors

Deferred to library/advanced layer. The block-call model can express
message-passing patterns (Go goroutines/channels, Elixir actors), but the
design space is large. The first everyday language does not need these.

**Status:** research-only.

## 3. Parallel Collections (Future)

Apply operations concurrently across collection elements. Reduces to flow
normal form with a concurrency policy.

```nomi
# Future direction — library-first:
results = users |> par_map(_.compute_score)
```

**Source reference:** Kotlin `.parMap`, Scala `.par`, Rust rayon, C# PLINQ.

**Status:** library-first. Build on structured concurrency primitives when
they exist.

## 4. Channels / Actors (Research)

Communicating sequential processes — goroutines and channels; actor mailboxes.

**Source reference:** Go goroutines/channels, Kotlin channels, Clojure
core.async, Elixir/Erlang actors.

**Status:** research-only. The block-call model can express message-passing
patterns, but the design space is large and should not constrain the first
everyday language.

## 5. Synthesis Decisions

| Candidate | Status | Decision |
|-----------|--------|----------|
| Python async/await | available (interop) | Use for Python ecosystem compatibility; not the Nomi design target. |
| Structured concurrency | design-settled (approach) | Block policies, no function coloring, supervision model. Implementation waits for prerequisites. |
| Parallel collections | library-first | Build on structured concurrency; `par_map` as a block policy. |
| Channels / actors | research-only | Block-call patterns can express this; defer to future layer. |
| Reactive streams | research-only | Pipeline over async sequences; library-first if needed. |
| Atomics / lock-free | available (Python) | Python interop only. |

## 6. Architecture Rule

Do not add `async`, `await`, `suspend`, or any second function color as Nomi
syntax. The block/yield model is the one control abstraction. All concurrency
patterns — parallelism, structured concurrency, actors, streams — must reduce
to block policies or flow verbs, not to separate function colors.

## 7. Research Sources

- [design_lessons_and_integration.md §7.1](design_lessons_and_integration.md) — function-color systemic pattern
- [design_lessons_and_integration.md §7.7](design_lessons_and_integration.md) — concurrency primitives as initial design
- [../features/block_calls_feature.md](../features/block_calls_feature.md) — block-call design
