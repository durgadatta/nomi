# Nomi Test Suite

> Status: migration guide.
>
> The current layout is being reorganized toward the phased plan in
> `docs/language/test_suite_restructure_plan.md`. During migration, prefer the
> target meaning of each bucket even when old files still live in their
> original path.

## Current Buckets

| Path | Meaning |
| --- | --- |
| `unit/` | Tests for one module, class, parser pass, interpreter layer, runtime helper, or tool helper. |
| `functional/` | Compatibility bucket for multi-module language behavior that has not yet moved into a feature packet. |
| `features/` | Target home for feature-owned language tests. Add this path only with real tests, not placeholders. |
| `contracts/` | Target home for stable public API and adapter contracts that do not need full e2e surfaces. |
| `regression/` | Snapshot and broad-output drift checks. These are review gates, not the main edit loop. |
| `e2e/` | CLI, web, notebook, report, and scenario tests that exercise user-facing surfaces end to end. |
| `smoke/` | Tiny checkout-alive checks collected by default and selectable with `pytest -m smoke`. |

## Interpreter Fixtures

Use `nomi_mode` for new Nomi-only syntax. It runs against `nomi` and
`reduced`.

Use `interpreter_mode` only when a behavior should hold for Python parity as
well as Nomi-family interpreters.

```python
from prototype.interpreter.helpers import get_run_eval_loop


def test_nomi_feature(nomi_mode):
    run = get_run_eval_loop(nomi_mode)
    bindings = run(code="double(x) = x * 2\nresult = double(5)\n")
    assert bindings["result"] == 10
```

## Run Tiers

```bash
# Unit or desugar edit loop
pytest prototype/tests/unit
pytest prototype/tests/unit/parser/desugar

# Existing feature behavior during migration
pytest prototype/tests/functional --interpreter-modes reduced

# Target feature packet shape, once a packet exists
pytest prototype/tests/features/<feature>

# Public runtime/tool contracts, once promoted
pytest prototype/tests/contracts prototype/tests/unit/runtime

# Snapshot and broad output gates
pytest prototype/tests/regression

# User-facing tooling gates
pytest prototype/tests/e2e

# Full local suite
pytest
```

`pytest -m smoke` is the tiny confidence command. Smoke tests should stay
assertion-based, avoid snapshots, and avoid writing local inspection artifacts.

## Migration Rules

- Move one semantic cluster per commit.
- Preserve behavior while moving tests; semantic changes get their own patch.
- Keep low-level implementation-shape checks in `unit/`.
- Put language behavior under `features/<feature>/` when the feature has enough
  surface area to need parse, lowering, diagnostics, runtime, or reduced
  coverage.
- Keep snapshot regeneration separate from pure organization work.
