# Syntax Feature Test Template

Use this checklist when a feature grows beyond a one-line parser or runtime
fix. Keep unused rows as `N/A` with a reason; do not create placeholder test
files.

## Feature Entry

- `prototype/syntax/features.py`: `SyntaxFeature` entry with `name`, `layer`,
  `semantic_forms`, `reduces_to`, `docs`, `tests`, and `coverage`.
- `docs/language/syntax_substrate_todo_audit.md`: TODO row updated if the
  feature opens or closes an architectural seam.

## Expected Coverage

| Surface | Path |
| --- | --- |
| Parse shape | `prototype/tests/unit/parser/test_<feature>.py` or `prototype/tests/features/<feature>/test_<feature>_parse.py` |
| Lowering or normal form | `prototype/tests/unit/parser/desugar/test_<feature>.py` or `prototype/tests/features/<feature>/test_<feature>_lowering.py` |
| Diagnostics | `prototype/tests/features/<feature>/test_<feature>_diagnostics.py` |
| Runtime behavior | `prototype/tests/features/<feature>/test_<feature>_runtime.py` |
| Reduced invariants | `prototype/tests/unit/interpreter/test_reduced_contract.py` or a feature-local reduced test |
| Regression sample | `prototype/tests/data/sample_sources/interpreter/<feature>.nomi` or `samples/<feature>.nomi` |
| Web playground | `prototype/tests/contracts/` or `prototype/tests/e2e/` when browser-visible |
| Notebook | `prototype/tests/contracts/test_notebook_kernel_contract.py` or `prototype/tests/e2e/` when notebook-visible |
| Docs/spec | `docs/features/`, `docs/language/`, or `docs/convenience/` |

## Validation

Run the smallest relevant slice first:

```bash
pytest prototype/tests/features/<feature>
pytest prototype/tests/unit/parser/test_<feature>.py
pytest --interpreter-modes reduced prototype/tests/features/<feature>
```

Broaden only when the feature touches shared parser, runtime, web, or sample
behavior.
