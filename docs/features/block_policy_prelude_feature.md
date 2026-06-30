# Block Policy Prelude Feature

> Status: active integration feature packet; design direction settled,
> implementation partial.
>
> Normal forms: block, binding, absence/result, capability, explanation.
>
> Canonical homes: this file owns the prelude-level block policy family and
> resource/capability diagnostic contract. Detailed block-call syntax remains
> in [Block Calls As Control Values](block_calls_feature.md), world authority
> remains in [State And Capability Model](state_and_capability_model.md), and
> cancellation/concurrency pressure remains in
> [Concurrency](../convenience/concurrency.md).

## One Sentence

Nomi block policies should make resource cleanup, retry, transaction, timeout,
trace, tests, and future concurrency feel like one ordinary call-plus-block
model.

```text
policy call -> attached caller block -> callee yield/resume
-> cleanup/cancel/commit/rollback -> semantic events
```

This packet exists because control-shaped work is where languages multiply
special cases:

- Python has `with`, decorators, callbacks, generators, fixtures, `async with`,
  and `contextlib`;
- Ruby has humane blocks but also receiver and DSL magic;
- Zig/Go/Swift/Odin have `defer`, with different scope behavior;
- Zig adds `errdefer` for rollback-on-failure;
- Gleam has `use` for callback-shaped control;
- BEAM systems have supervision, restart, and cancellation as first-class
  operational concerns;
- Rust/Kotlin/Java have structured resource and structured concurrency
  pressure;
- effect systems name world contact, but often cost too much for first-hour
  users.

Nomi should keep the humane control power while refusing keyword accumulation,
ambient capabilities, and second function colors.

## Design Position

The primitive is a block call:

```nomi
retry(3, on=NetworkError):
    send(request)

using(open(path)) -> file:
    text = file.read()

transaction(db) -> tx:
    tx.insert(user)
```

The callee owns the policy. The caller supplies local code. The callee invokes
the caller block through `yield`.

```nomi
func using(resource):
    acquired = resource.open()
    try:
        return yield acquired
    finally:
        acquired.close()
```

Every policy should answer the same questions:

| Question | Example |
| --- | --- |
| Who owns the policy? | `retry`, `using`, `transaction`, `trace`, `test` |
| When does the caller block run? | at each `yield` |
| What values cross the boundary? | yielded resources, attempts, fixtures, transaction handles |
| What happens on success? | return, commit, close, record pass |
| What happens on expected failure? | retry, rollback, return `Err`, record failure |
| What happens on unexpected error? | cleanup, re-raise or translate |
| What happens on cancellation? | cooperative cancel, cleanup, event |
| What world authority is granted? | file, network, clock, database, process |
| What does `explain` show? | enter, yield, resume, retry, cleanup, deny, cancel |

## Shared Model

### `BlockPolicy`

A block policy is an ordinary callable with attached caller-side code and
declared control behavior.

Minimum fields:

| Field | Meaning |
| --- | --- |
| `name` | `using`, `retry`, `timeout`, `transaction`, `trace`, `test`, `parallel` |
| `block_target` | binding target for yielded values, if any |
| `yield_contract` | zero, one, many, bidirectional, repeated |
| `result_contract` | callee return value, block result, `Result`, stream |
| `cleanup_contract` | always, success-only, error-only, cancellation, none |
| `failure_policy` | propagate, retry, suppress, translate, rollback, accumulate |
| `capabilities` | authority granted or requested by the policy |
| `events` | enter, yield, resume, retry, cleanup, commit, rollback, cancel, deny |
| `span` | source spans for call, block body, and callee yield |

The syntax can stay smooth because the model is explicit.

### `CapabilityGrant`

World contact is visible authority, not ambient global state.

Minimum fields:

| Field | Meaning |
| --- | --- |
| `family` | filesystem, network, time, random, process, environment, database, secrets |
| `scope` | lexical block or policy lifetime |
| `mode` | read, write, execute, connect, fixed, fake, secret |
| `source` | path, URL, command, env key, database handle, test fixture |
| `redaction` | what must not appear in events or diagnostics |
| `escape_policy` | whether the capability/resource may leave the block |

Capability grants should be values or block-policy effects. They should not be
invisible global permission.

### `PolicyEvent`

Block policies should emit semantic events compatible with
[Explanation And Trace Feature](explanation_trace_feature.md).

Required event actions:

| Action | Meaning |
| --- | --- |
| `entered` | policy call began |
| `yielded` | callee invoked caller block |
| `bound` | yielded values bound into block target |
| `resumed` | caller block returned to callee |
| `retried` | policy repeated block after expected failure |
| `committed` | transaction/test/resource policy succeeded |
| `rolled_back` | policy undid work after failure |
| `cleaned` | cleanup ran |
| `cancelled` | policy or child work was cancelled |
| `denied` | capability request was refused |
| `escaped` | resource/capability attempted to outlive scope |

## Prelude Policy Set

The first useful policy family:

| Policy | Purpose | Shape | Result |
| --- | --- | --- | --- |
| `using` | acquire/release resource | `using(open(path)) -> file:` | usually block result |
| `retry` | repeat on expected failure | `retry(3, on=NetworkError):` | successful block result or final failure |
| `timeout` | bound duration | `timeout(5s):` | block result or cancellation/failure |
| `transaction` | commit/rollback | `transaction(db) -> tx:` | block result after commit or rollback failure |
| `trace` | add diagnostic context | `trace("import users"):` | block result plus trace records |
| `test` | named check/fixture policy | `test("signup rejects young user"):` | test event/result |
| `world` | grant fake/real capabilities | `world(files=fixture(...), time=fixed(...)) -> w:` | block result under scoped authority |
| `on_error` | rollback-only cleanup | `on_error(cleanup):` | block result or cleanup-on-failure |
| `parallel` | future structured concurrency | `parallel:` | aggregated child results |

Not every policy needs syntax. They are functions that receive an attached
block.

## Syntax Variations And Decisions

### Canonical Block Policy

Canonical:

```nomi
retry(3, on=NetworkError):
    send(request)
```

Yielded value:

```nomi
using(open(path)) -> file:
    text = file.read()
```

Decision:

- Keep ordinary call spelling.
- Use indentation for the attached caller-side block.
- Use `-> binding_target` for yielded values.
- Route yielded values through the shared binding/pattern/constraint model.

### Python-Like `with`

Possible teaching alias:

```nomi
with open(path) -> file:
    text = file.read()
```

Decision:

- Do not make `with` the semantic primitive.
- If admitted, it should lower to `using(open(path)) -> file:`.
- Prefer policy-call spelling for retry, transaction, trace, test, and future
  concurrency so libraries stay first-class.

### Local `defer`

Scope cleanup:

```nomi
file = open(path)
defer file.close()
```

Decision:

- `defer` is useful for local always-run cleanup.
- `defer` should run when the current lexical scope exits, including block
  body exit.
- `errdefer` is not first-layer syntax; use an error-only policy such as
  `on_error`.

### Error-Only Cleanup

Library policy:

```nomi
on_error(delete(path)):
    write_file(path, content)
    verify_file(path)
```

Decision:

- Keep Zig-style rollback-on-failure as a library/policy first.
- Promote syntax only if ordinary code repeatedly proves it needs a shorter
  form.

### World/Capability Scope

Explicit capability block:

```nomi
world(files=fixture("people.csv"), time=fixed(now), network=false) -> w:
    result = import_people(w.files.path("people.csv"))
```

Decision:

- Use explicit capability values before any implicit effect context.
- Fake worlds and real worlds should share the same event vocabulary.
- Denied authority is a structured capability diagnostic.

### Structured Concurrency

Future policy:

```nomi
parallel:
    a = fetch(url_a)
    b = fetch(url_b)
```

Decision:

- No `async def`, no `await` as the Nomi design center.
- Concurrency should be a block policy over cancellation, cleanup, and result
  aggregation.
- Python `async` remains interop evidence, not the language normal form.

## Resource And Capability Diagnostics

Every resource/capability policy should report the same diagnostic vocabulary:

| Event | Required fields |
| --- | --- |
| enter | policy name, call span, capability request |
| grant | capability family, scope, mode, redaction |
| yield | callee span, yielded values, block target |
| bind fail | target, value, failed rule, no body entry |
| resume | block result or expected failure |
| retry | attempt, reason, remaining attempts |
| timeout/cancel | policy, elapsed time, cleanup status |
| cleanup | resource, cleanup action, success/failure |
| commit | transaction/test/policy result |
| rollback | cause, rollback action, success/failure |
| deny | requested authority, available authority, repair hint |
| escape | resource/capability, attempted destination, scope |

Example:

```text
retry(3): attempt 2 failed with NetworkError
  policy: retry
  block: send(request)
  action: retrying
  next: attempt 3 of 3
```

Example:

```text
capability denied: network
  policy: world(files=fixture(...), network=false)
  attempted: http.get("https://example.com")
  next: grant network=true or pass a fake HTTP client
```

## Result And Failure Semantics

Block policies should preserve the failure taxonomy:

| Failure kind | Policy behavior |
| --- | --- |
| Absence | pass through as ordinary value unless policy declares otherwise |
| Expected `Err` | retry/rollback/accumulate when policy says so |
| Unexpected exception | cleanup then re-raise or translate |
| Binding failure on yielded value | body does not run; policy receives diagnostic |
| Capability denial | structured diagnostic or `Err` depending on boundary |
| Cancellation | cooperative at yield/check points; cleanup always attempted |
| Cleanup failure | attached as suppressed/secondary diagnostic, not lost |

The callee owns whether a block `Err` becomes retry input, rollback cause,
test failure, or propagated result. The event trace should show that decision.

## Target Examples

### File Resource

```nomi
using(open(path)) -> file:
    text = file.read()
    parse(text)
```

Expected trace:

```text
entered using(open(path))
yielded file -> block target file
resumed with Parsed(...)
cleaned file.close()
```

### Retry

```nomi
result = retry(3, on=NetworkError):
    http.post(url, payload)
```

The block call returns the callee's result. `retry` may return the successful
block result or re-raise/return the final failure according to its contract.

### Transaction

```nomi
transaction(db) -> tx:
    user = tx.insert("users", payload)
    tx.insert("audit", {"user": user.id})
    user
```

Success commits. Failure rolls back. Explanation names both policy and caller
block frames.

### Trace

```nomi
trace("import people"):
    people =
        read_csv(path)
        |> select(Person.decode)
        |> collect_results
```

Trace blocks add context to events without changing semantics.

### Test World

```nomi
test("import uses fixed clock"):
    world(files=fixture("people.csv"), time=fixed("2026-06-30")) -> w:
        imported = import_people(w)
        expect(imported[0].created_at).equals("2026-06-30")
```

Tests become ordinary block policies over examples, capabilities, and
explanation events.

## Rejected Alternatives

| Alternative | Why not |
| --- | --- |
| Dedicated keyword per policy | Makes the language grow by keyword accumulation. |
| Python `with` as the only model | Too narrow for retry, test fixtures, tracing, transactions, and concurrency. |
| Ruby receiver magic | Hurts local reasoning and tool expansion. |
| Full continuations as user model | Too powerful and difficult to diagnose for ordinary control. |
| Ambient filesystem/network/time globals | Hard to test, replay, restrict, or explain. |
| Full algebraic effects first | Too theoretical before everyday scripts and diagnostics are strong. |
| `async`/`await` as Nomi syntax center | Creates function colors and ecosystem splits. |
| Resource ownership/lifetime syntax first | Pulls systems-language complexity into the daily layer. |
| String shell by default | Reintroduces injection and stringly command boundaries. |

## Implementation Slices

1. Keep `block_calls_feature.md` as the syntax contract for attached blocks and
   callee `yield`.
2. Define prelude policy docs for `using`, `retry`, `timeout`, `transaction`,
   `trace`, `test`, `world`, and `on_error`.
3. Add passive `BlockPolicy` metadata for policy name, yield contract, result
   contract, cleanup contract, failure policy, capabilities, and spans.
4. Route yielded values through the shared `BindingTarget` engine.
5. Emit block-policy events for enter, yield, bind, resume, retry, cleanup,
   commit, rollback, cancel, deny, and escape.
6. Add a host capability manifest for files, network, time, randomness,
   process, environment, database, and secrets.
7. Add diagnostics for capability denial and capability/resource escape.
8. Add `trace` rendering that shows both policy frame and caller block frame.
9. Add test-world fixtures for deterministic files, time, randomness, and
   network denial.
10. Treat structured concurrency as future policy work after cancellation and
    result aggregation are explicit.

## Test And Sample Gates

Before this packet is promoted beyond active design, the project should have:

- parser/lowering tests for block call and block target syntax;
- runtime tests that callee `yield` invokes caller block exactly when expected;
- binding tests that failed block parameters prevent body entry;
- policy fixtures for `using`, `retry`, `transaction`, `trace`, and `test`;
- event snapshots for enter/yield/resume/retry/cleanup/commit/rollback;
- denied-capability tests for files/network/time/process/environment;
- escaped-resource diagnostics for resources returned or stored beyond scope;
- cancellation target fixtures marked target-only until implemented;
- docs examples that distinguish `defer`, `using`, and `on_error`;
- capability matrix rows for block policy events and frontend explanation
  exposure.

## Promotion Rule

This packet becomes spec-ready only when at least `using`, `retry`,
`transaction`, and `trace` can produce shared block-policy events and explain
both the callee policy frame and the caller block frame. Until then, new policy
syntax should stay library-first or target-only.
