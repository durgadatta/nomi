# Data Decode Boundary Feature

> Status: active feature packet; design-settled direction, implementation
> pending.
>
> Normal forms: data boundary, binding, explanation.
>
> Canonical homes: this file owns decode/config/provenance behavior;
> [binding_constraints_feature.md](binding_constraints_feature.md) owns
> binding constraint semantics; [explanation_trace_feature.md](explanation_trace_feature.md)
> owns the shared event shape.

## Everyday Pressure

Most useful scripts touch external data: JSON, CSV, CLI arguments, environment
variables, form fields, HTTP bodies, config files, database rows, and notebook
cells. Nomi should not let those values silently become trusted domain values.

The core rule:

```text
external representation -> parse/codec -> external value -> decode -> owned data
```

`data` constructs owned program values. `decode` crosses a boundary from messy
world values into owned meaning.

## User Syntax

```nomi
data Config:
    host:str = "localhost"
    port:int, port > 0 = 8080
    @secret token:str

result = Config.decode(file("config.toml"))

match result:
    case Ok(config):
        run(config)
    case Err(errors):
        explain(errors)
```

Nested and collection decoders are values:

```nomi
users = Data.decode(raw_json, list[User])
row = User.decode(csv_row, source="people.csv:42")
```

## Semantics

Decode performs:

1. Parse or accept an external value from a representation.
2. Map fields by name or declared decoder.
3. Apply defaults and optional-field policy.
4. Reuse binding constraints for each decoded field.
5. Return `Ok(value)` or `Err(DecodeErrorList)`.

Decode should accumulate all field errors by default. A strict/fail-fast helper
can exist as a library mode, but the first user-facing model should help users
fix a whole input file in one pass.

## Policies

| Case | Default | Override direction |
| --- | --- | --- |
| Missing required field | error | none |
| Missing field with default | fill default | none |
| Optional field | `none` | explicit optional type |
| Extra field | error | `extra=ignore` or `extra=pass_through` |
| Nested decode failure | collect path | none |
| Secret/PII field | redact in diagnostics | explicit unsafe explain |

## Diagnostics

Every decode error should carry:

- source identity: file, URL, request, env, CLI, row, or cell;
- field path: for example `users[2].age`;
- raw value when safe to show;
- expected type or constraint;
- failed rule/message;
- redaction policy;
- related source span when available.

Example:

```text
config.toml:12:7: Config.port failed constraint port > 0
  value: -1
  field: port
  next: choose a positive integer or remove the field to use default 8080
```

## Source Evidence

Pkl shows the need for a configuration language with templating, validation,
tooling, embeddings, and code generation. Nomi should adopt the user need, not
a separate config language: config crosses through `decode` into ordinary
`data`.

Roc keeps I/O outside the standard library and gives applications a platform
that supplies world primitives. Nomi should use that pressure to keep decode
sources explicit: file/env/network data came from a capability, not from an
ambient global.

CUE, Nickel, Dhall, Terraform, JSON Schema, Pydantic, serde, Elm decoders, and
Pkl all confirm the same lesson: boundary data wants defaults, constraints,
merge, provenance, redaction, and precise paths.

## Integration Comments

- Decode errors are expected failures: return `Result[T, DecodeErrorList]`.
- Decode field checks reuse binding constraints; no second validation
  language.
- Config layering is library-first over decode sources:

  ```nomi
  raw =
      Config.sources(defaults, file("app.toml"), env(), cli_args())
      |> merge(policy="last-wins-with-trace")

  config = Config.decode(raw)
  ```

- Query/table ingestion should decode rows into owned data before domain
  logic:

  ```nomi
  people =
      read_csv(path)
      |> select(Person.decode)
      |> collect_results
  ```

## Rejected Alternatives

| Alternative | Why not first |
| --- | --- |
| `shape` as peer to `data` | Splits owned data from validation before one data story is stable. |
| Config-only syntax | Creates a second field language for defaults and constraints. |
| Boolean validation | Loses paths, source spans, raw values, and repair guidance. |
| Silent extra fields | Hides spelling mistakes and stale config. |

## Implementation Slice

1. Add `DecodeError` and `DecodeErrorList` value shapes.
2. Add field-path and source-provenance data structures.
3. Route decoded fields through the shared binding constraint engine.
4. Return structured `Result` from decode helpers.
5. Emit explanation events for field success/failure.
6. Add fixtures for JSON, CSV, env, CLI, and TOML-like mappings.

