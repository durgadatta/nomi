# Prelude And Standard Library Plan

> Status: active standard-library planning note.
>
> Purpose: define the boring everyday library surface Nomi needs before
> additional syntax can be justified.

## Principle

Syntax should not compensate for a weak standard library. Before Nomi adds
more surface forms, ordinary tasks should be possible through clear values,
functions, results, and block policies.

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

