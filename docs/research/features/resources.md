# Resource Lifetime

> Status: comparative evidence; lexical release accepted, escape/envelope open.

User pressure: close a resource on every exit without losing the original cause.

| Evidence | Mechanism | Nomi consequence |
| --- | --- | --- |
| [Python](../languages/python.md) | Explicit resource protocol | Dedicated exactly-once scope. |
| [C++](../languages/cpp.md) | RAII | Release lifetime is separate from GC memory reclamation. |
| [Go](../languages/go.md) | Function-scoped defer | Nomi deliberately chooses lexical scope. |
| [Zig](../languages/zig.md) | Error-only cleanup | Rollback is a distinct use case, not admitted syntax yet. |

Conceptual long form: acquire; run body; record its outcome; release exactly
once; compose outcomes without discarding causes. This is a semantic expansion,
not a Nomi `try` form. The accepted surface is:

```nomi
resource = files.open_reader(path)?
with resource as reader:
    return reader.read_all()
```

The fixture assumes infallible release for this narrow reader. General release
may fail or suspend and requires a composed outcome contract. `defer` is
unconditional, LIFO, and lexical; registration/capture timing must be specified.

Two unresolved choices are static non-escape enforcement versus runtime
closed-handle checks, and domain-visible cleanup Results versus a distinct
abnormal envelope. Exactly-once release alone prevents neither alias escape
nor loss of a cleanup error. GC does not choose between these options.

**Experiment:** three programs: early read return, staged acquisition rollback,
and async cancellation while release fails. Also return/capture/send the handle
outside scope. Produce event traces, composed causes, diagnostic locations, and
an explicit rule for each escape. Reject designs that allow double close or
silent use-after-close.

**User-facing gate:** explain output must show enter/body/exit and all causes;
playground promotion waits on the narrow supported contract.
[Target](../../design/targets/resources.nomi).
