---
name: nomi-reduce
description: Add a syntactic reduction to the Nomi language. Create a desugarer, register it, add interpreter override, write tests.
compatibility: deepseek
---

Before adding a reduction, check the `nomi-language-design` skill. Each
reduction should target a specific Nomi normal form and be grounded in the
cross-language research corpus (`docs/research/language_family_coverage_map.md`).

## Files you will touch
1. `prototype/parser/nomi/desugar/<name>.py` — new desugarer class
2. `prototype/parser/nomi/desugar/pipeline.py` — add to chain
3. `prototype/interpreter/reduced/interpreter.py` — add NotImplementedError override
4. `prototype/tests/unit/parser/desugar/test_<name>.py` — test the desugaring

After desugaring, verify Core IR roundtrip integrity:
```bash
NOMI_VERIFY_CORE=1 pytest prototype/tests/unit/parser/desugar/test_<name>.py
```
The `NOMI_VERIFY_CORE=1` gate catches forms that the reduced interpreter
would also reject, via the shared `verify_core(strict=True)` verifier.

For larger syntax reductions, also update the planned feature manifest or
`docs/language/syntax_substrate_todo_audit.md` with the feature owner, normal
form, status, pass metadata, diagnostics, and inspection expectations.

## Pattern

### Step 1: Create desugarer
```python
# prototype/parser/nomi/desugar/<name>.py
import ast
from .base import NomiDesugarer

class <Name>(NomiDesugarer):
    """docstring with before/after example and normal form"""
    removed_node_types = (...)
    def visit_<NodeType>(self, node):
        # Transform node to primitive AST
        return replacement_node  # or [stmt1, stmt2] for multi-node replacement
```

### Step 2: Register in pipeline
```python
# prototype/parser/nomi/desugar/pipeline.py
from .<name> import <Name>

def desugar_module(tree):
    ...
    tree = <Name>().visit(tree)
    ...
```

### Step 3: Override in reduced interpreter
```python
# prototype/interpreter/reduced/interpreter.py
def eval_<NodeType>(self, node, ...):
    raise NotImplementedError("<reason>")
```

### Step 4: Write tests
```python
# prototype/tests/unit/parser/desugar/test_<name>.py
from prototype.parser.nomi.desugar import desugar_module
from .conftest import find_node

class Test<Name>:
    def test_basic(self):
        tree = ast.parse("source code")
        tree = desugar_module(tree)
        assert find_node(tree, ast.<NodeType>) is None
```

## Verify
```bash
pytest prototype/tests/unit/parser/desugar/test_<name>.py
pytest prototype/tests/ -o "addopts="     # full suite, all interpreters
pytest --force-regen prototype/tests/regression/test_interpreter.py  # if output changed
```

## Rules
- Never change existing test files without asking
- Add new tests to `prototype/tests/unit/parser/desugar/`
- One reduction per commit
- Declare what node/form the pass removes and what normal form it produces.
- Prefer metadata beside the pass over undocumented ordering assumptions.
- Regenerate snapshots if interpreter output changes
