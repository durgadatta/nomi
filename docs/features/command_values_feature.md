# Command Values Feature

> Status: active feature packet; design-needed, library-first.
>
> Normal forms: data boundary, call, state/capability, explanation.
>
> Canonical homes: this file owns command values; [state_and_capability_model.md](state_and_capability_model.md)
> owns authority; [explanation_trace_feature.md](explanation_trace_feature.md)
> owns command events.

## Purpose

Nomi should treat commands as structured values, not shell strings. This
supports CLI tools, task automation, agent preview/replay, notebooks, and
safe subprocess use without importing shell injection as a default behavior.

## User Syntax Sketch

```nomi
status = command("git", ["status", "--short"]).run()

backup =
    command("tar", ["-czf", output, input])
    |> require_capability(process=true, files=[input, output])

preview(backup)
result = backup.run()
```

String shell mode is explicit:

```nomi
unsafe_shell("git status --short").run()
```

## Command Record

| Field | Meaning |
| --- | --- |
| `name` | stable command name for UI/agent display |
| `argv` | structured argument list |
| `cwd` | working directory |
| `env` | explicit environment additions |
| `stdin` | none, text, bytes, or file |
| `capabilities` | files/process/network/env requirements |
| `preview` | safe human-readable summary |
| `result` | status, stdout, stderr, duration, events |

## Integration Comments

- Commands are values first and syntax later, if ever.
- CLI entrypoints should decode arguments into data before constructing
  command values.
- Agents and UI projections should preview the command value and required
  capabilities before running it.
- Command execution emits `capability` and `command` events.

## Rejected Alternatives

| Alternative | Why not first |
| --- | --- |
| Shell strings by default | Unsafe, unstructured, hard to preview. |
| One-off task DSL | Becomes a build system before commands are data. |
| Hidden ambient env/cwd | Breaks replay and explanation. |

