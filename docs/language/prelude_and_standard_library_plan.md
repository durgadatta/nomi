# Prelude And Standard Library Plan

> Status: active standard-library planning note.
>
> Purpose: define the boring everyday library surface Nomi needs before
> additional syntax can be justified.

## Principle

Syntax should not compensate for a weak standard library. Before Nomi adds
more surface forms, ordinary tasks should be possible through clear values,
functions, results, and block policies.

## Python-Competitive Boring-Task Ladder

Python wins many users because ordinary work is immediately available. Nomi
must earn syntax ambitions by making boring tasks feel direct, checked, and
explainable.

The first prelude should support this ladder:

| Stage | User job | Required surface | Competitive bar |
| --- | --- | --- | --- |
| Text | clean, split, search, format, parse small strings | `text` helpers, one interpolation path, regex helper values | As approachable as Python strings, with safer typed sinks later. |
| Paths and files | read/write one file, list paths, check existence | `Path`, `read_text`, `write_text`, `list_dir` | No stringly path confusion in diagnostics. |
| Data files | JSON, TOML, CSV into owned data | codecs plus `Data.decode` | Better provenance and field errors than raw dict workflows. |
| CLI and env | parse args and environment into config | decoder into `data` | No ad hoc `sys.argv` and env-string validation scattered through code. |
| HTTP | fetch or post and handle expected failure | client value returning `Result` | Failure is data with status, body summary, redaction, and retry hooks. |
| Process | run commands safely | command values with preview/result | Safer than shell string interpolation. |
| Tests/examples | show behavior beside code | `check`, `examples:` | Examples should feed docs, tests, and explanations. |

This ladder is a design gate: if a proposed syntax feature does not help these
jobs, it should probably wait behind library work, diagnostics, or examples.

## Baseline Areas

| Area | First surface | Normal form |
| --- | --- | --- |
| Text | string functions, formatting, regex helpers | flow + pattern |
| Paths/files | `Path`, `file`, `read_text`, `write_text` | data boundary + capability |
| JSON/TOML/CSV | codecs plus `Data.decode` | data boundary |
| CLI args | argument decoder into `data` | data boundary |
| HTTP | client value returning `Result` | capability + result |
| Time | `Clock`, duration, instant | capability + value |
| Random | RNG value | capability |
| Process | command values | command + capability |
| Tables | rows, columns, verbs, plan values | flow |
| Tests/examples | `check`, `examples:` | explanation |
| Secrets | `Secret[T]`, redacted display | data boundary + explanation |

## Integration Comments

- Prefer library functions until syntax earns its place through repeated,
  readable examples.
- Every world-touching function declares a capability.
- Every boundary function returns `Result` or a decoded data value with
  diagnostics.
- Every display path honors redaction.

## First Packages To Design

```text
text
path
file
json
csv
toml
cli
http
time
process
table
test
```

The prelude should stay small. Rich domain libraries can grow outside the
prelude once package and capability policy exist.
