# Current Capability Matrix

> Status: active capability index; generated truth lives in
> `tools.syntax.inspect`.
>
> Purpose: give users and agents one stable place to find what syntax works
> today without freezing a hand-copied table into stale documentation.

## Live Command

Use the inspection command as the current source of truth:

```bash
python3 -m tools.syntax.inspect --stage capabilities
```

The table currently reports these axes:

```text
feature
target-only
parse
lower
run
reduce
explain
docs
tests
samples
web
notebook
```

## Current Read

The important signal is conservative capability honesty:

- many existing features parse, lower, run, and reduce;
- docs/tests/samples coverage is explicit for many promoted surface forms;
- explanation, web exposure, and notebook exposure are mostly still `no`;
- target-only syntax should stay out of runnable samples until the matrix and
  regression tests agree.

Do not read a `yes` in parse/lower/run as proof that a feature is spec-ready.
Spec readiness also requires diagnostics, examples, rejected alternatives,
frontend exposure decisions, and a reversible implementation story.

## Generated Read: 2026-06-30

The current generated table gives a useful, deliberately conservative picture:

- every listed feature is currently `target-only: no`;
- every listed feature currently reports `parse`, `lower`, `run`, and
  `reduce` as `yes`;
- `docs`, `tests`, and `samples` vary by feature and are now useful review
  signals;
- `explain`, `web`, and `notebook` currently report `no` across the generated
  feature rows.

That last line is the most important product gap. It does not mean the web
playground or notebook cannot execute Nomi code. It means feature-level
explanation and frontend exposure have not yet been declared as capability
facts in the syntax feature metadata.

The next matrix improvement is not a hand-copied static table. The next
improvement is to make the missing axes feature-owned:

| Axis | Current read | Needed next fact |
| --- | --- | --- |
| `explain` | uniformly `no` | Which features emit semantic events and can render explain output? |
| `web` | uniformly `no` | Which features are exposed through the current browser-default Rust/WASM -> JS path? |
| `notebook` | uniformly `no` | Which features have notebook display/error/result semantics covered? |
| diagnostics | partially implicit | Which feature owns each diagnostic/event producer? |
| reduced mode | mostly derived | Which features are proven by reduced-mode invariants? |
| docs/spec status | partially explicit | Which features are normative, partial, target-only, or design-needed? |

## Promotion Rule

Before moving a feature from design or target fixture into runnable examples,
check:

1. The feature has a canonical owner doc or feature packet.
2. The capability table does not overstate parser/lowering/runtime support.
3. Tests or samples prove the intended current behavior.
4. Missing axes are explicit, especially explain/web/notebook.

## When To Split Further

Keep the generated table as the truth source. Add a separate static matrix only
if the generated output grows too large for ordinary review and the static
matrix is produced mechanically from feature metadata.
