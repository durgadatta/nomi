# State And Capability Model

> Status: active feature packet; design-needed with settled direction.
>
> Normal forms: block, data boundary, explanation.
>
> Scope: practical world authority, rebinding, mutation, resources, and block
> policies before any advanced effect typing.

## Everyday Pressure

Real programs touch files, networks, clocks, randomness, subprocesses,
environment variables, databases, caches, transactions, and secrets. Nomi
needs a visible authority story before it needs a type-theoretic effect system.

The first user model:

```text
world authority is a value or block policy, and world contact emits events
```

## User Syntax Sketch

```nomi
using file = open(path):
    text = file.read()

with world(files=true, network=false, time=fixed("2026-06-04")):
    result = import_people("people.csv")

transaction(db) -> tx:
    save_user(tx, user)
```

These are block policies, not one-off keywords. The callee grants or passes a
capability into the caller-side block, and the runtime can trace what happened.

## Capability Families

| Capability | Everyday use | First-layer policy |
| --- | --- | --- |
| Filesystem | read/write files, paths, directories | explicit file/path helpers |
| Network | HTTP, APIs, sockets | explicit client/session value |
| Time | clocks, timeouts, timestamps | injectable clock |
| Randomness | tokens, sampling, tests | injectable RNG |
| Process | subprocess argv, status, stdout/stderr | structured command value |
| Environment | env vars, config, secrets | explicit source with redaction |
| Database | transaction, connection, query plan | block-scoped transaction |

## Source Evidence

Roc platforms make I/O available through an application platform rather than a
global standard library. Nomi should not copy Roc's architecture wholesale, but
the design pressure is excellent: world access should be visible, scoped, and
replaceable for testing.

Unison abilities and Effekt effect handlers show a more advanced path:
effects can be named, required by functions, handled by context, and even
resumed. Nomi should keep those ideas as future-layer pressure while using
block policies and capability values for the first everyday language.

Effekt's capability/capture model is especially relevant for preventing
capabilities from escaping their valid scope. Nomi should eventually diagnose
stored or returned resources that outlive their policy block.

## Integration Comments

- Start with explicit capability values and block policies, not effect types.
- Let tests inject fake worlds:

  ```nomi
  with world(files=fixture("people.csv"), time=fixed(now)):
      check import_people("people.csv").count == 3
  ```

- Make command execution structured:

  ```nomi
  result = command("git", ["status", "--short"]).run()
  ```

  String shell mode should exist only as an explicitly unsafe helper.

- Transactions, retries, timeouts, and cleanup should share block-policy
  events: enter, yield, resume, retry, cancel, cleanup, commit, rollback.

## Rejected Alternatives

| Alternative | Why not first |
| --- | --- |
| Ambient globals for files/network/time | Hard to test, replay, or explain. |
| Full algebraic effects in first-hour Nomi | Too much theory before everyday scripts work. |
| Resource ownership syntax | Pulls systems-language complexity into the daily layer. |
| String shell by default | Reintroduces shell injection and stringly boundaries. |

## Implementation Slice

1. Define host capability manifest rows for files, network, time, randomness,
   process, environment, and database.
2. Add structured command values as library-first data.
3. Add block-policy event records for `using`, `transaction`, `retry`, and
   `timeout`.
4. Add test-world fixtures for deterministic time/files/randomness.
5. Add diagnostics for denied or escaped capabilities.

