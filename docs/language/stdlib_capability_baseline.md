# Standard Library Capability Baseline

> Status: active planning note for capability honesty in the standard library.
>
> Purpose: keep world-touching library functions explicit, testable, and
> explainable.

## Capability Baseline

| Capability | Stdlib examples | Test substitute | Event |
| --- | --- | --- | --- |
| `files` | `read_text`, `write_text`, `open` | fixture filesystem | `capability.files.*` |
| `network` | HTTP client | fake client/server | `capability.network.*` |
| `time` | `now`, timers, deadlines | fixed clock | `capability.time.*` |
| `random` | RNG, tokens, sampling | seeded RNG | `capability.random.*` |
| `process` | command values | fake runner | `capability.process.*` |
| `env` | env/config sources | explicit env map | `capability.env.*` |
| `secrets` | secret source/display | redacted fixture | `capability.secrets.*` |

## Rules

- Pure functions do not touch capabilities.
- World-touching functions require a capability value or block policy.
- Test fixtures can replace capabilities without changing program logic.
- Diagnostics and traces show what was touched and under what authority.
- Secret and PII values are redacted by default.

## Integration Comments

This baseline is intentionally practical. It borrows pressure from Roc
platforms, Unison abilities, and Effekt capabilities, but it does not require
ordinary users to understand effect typing.

