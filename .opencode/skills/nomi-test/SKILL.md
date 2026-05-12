---
name: nomi-test
description: Write tests for the Nomi language — unit, functional, regression, e2e. Multi-interpreter test patterns.
compatibility: deepseek
---

## Test directories
- `prototype/tests/unit/` — Single module/class tests
- `prototype/tests/functional/` — Multi-module integration
- `prototype/tests/regression/` — Snapshot-based with file_regression fixture
- `prototype/tests/e2e/` — Full pipeline, CLI, scenarios
- `prototype/tests/unit/parser/desugar/` — Desugar pass tests (shared conftest.py)

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
```

## Rules
- Never modify existing test files without asking
- Add new tests for new functionality
- One test class per desugar pass
- `conftest.py` has shared helpers: `find_node`, `is_store`, `is_load`
