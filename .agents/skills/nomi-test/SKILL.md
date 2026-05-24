---
name: nomi-test
description: Write tests for the Nomi language — unit, functional, regression, e2e. Multi-interpreter test patterns.
compatibility: deepseek
---

For the semantic rationale behind tested behavior, see the
`nomi-language-design` skill and the research corpus.

## Test directories
- `prototype/tests/unit/` — Single module/class tests
- `prototype/tests/functional/` — Retired compatibility bucket; do not add new tests here
- `prototype/tests/regression/` — Snapshot-based with file_regression fixture
- `prototype/tests/e2e/` — Full pipeline, CLI, scenarios
- `prototype/tests/unit/parser/desugar/` — Desugar pass tests (shared conftest.py)

Before reorganizing existing tests, read
`docs/language/test_suite_restructure_plan.md`. That plan is the current
planning-only target for feature packets, contract tests, smoke tests,
regression snapshots, and e2e tiers.

## Feature coverage direction
Future syntax work should be feature-driven rather than only file-driven. For
each non-trivial feature, plan coverage for:

- parse snapshots;
- lowering/normal-form snapshots;
- diagnostics for common mistakes;
- runtime behavior in `nomi` and `reduced` modes;
- reduced-interpreter invariants;
- sample regression coverage when the syntax becomes user-facing;
- web playground and notebook checks when the feature is exposed there;
- docs/spec references.

## Test data
- `prototype/tests/data/sample_sources/interpreter/` — .py and .nomi source files
- `prototype/tests/regression/test_interpreter/` — Snapshot .txt files

## Multi-interpreter tests
Tests with `interpreter_mode` parameter are auto-parametrized across python/nomi/reduced.

```python
from prototype.interpreter.helpers import get_run_eval_loop

def test_something(interpreter_mode):
    if interpreter_mode == 'python':
        pytest.skip('Nomi-specific syntax not supported by Python parser')
    run_eval_loop = get_run_eval_loop(interpreter_mode)
    bindings = run_eval_loop(code='func f(): return 1\nx = f()\n')
    assert bindings['x'] == 1
```

## Desugar tests
```python
# prototype/tests/unit/parser/desugar/test_<name>.py
from prototype.parser.nomi.desugar import desugar_module
from .conftest import find_node

class Test<Name>:
    def test_basic(self):
        tree = ast.parse("form to desugar")
        tree = desugar_module(tree)
        assert find_node(tree, ast.<NodeType>) is None
```

## Running tests
```bash
pytest                                                    # full suite, all interpreters
pytest --interpreter-modes reduced                        # only reduced
pytest prototype/tests/path/to/test_file.py               # focused
pytest --force-regen prototype/tests/regression/test_interpreter.py  # regen snapshots
pytest prototype/tests/ -o "addopts="                     # serial (override -n auto)
NOMI_VERIFY_CORE=1 pytest                                 # with Core IR verification gate
NOMI_USE_CORE_IR=1 pytest                                # route eval through Core IR + backend
pytest prototype/tests/unit/runtime/test_backend_fixture_ladder.py  # python/core/js backend parity
```

## Rules
- Never modify existing test files unless the user explicitly asks for a test
  refactor/restructure or approves the edit
- Add new tests for new functionality
- One test class per desugar pass
- `conftest.py` has shared helpers: `find_node`, `is_store`, `is_load`
- When adding a feature-profile or manifest test path, update
  `docs/language/syntax_substrate_todo_audit.md` so the matrix stays visible.
- During test-suite restructure work, move one semantic cluster per commit and
  preserve behavior separately from semantic changes.
