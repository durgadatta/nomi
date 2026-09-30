# Deferred Test Review

> Status: dated test-maintenance evidence for a separate pass.
>
> No existing test files were modified during the implementation-boundary pass.
> New boundary tests add coverage; they do not settle the issues below.

## Observations

| Issue | Evidence/owner | Why it matters | Separate-pass action |
| --- | --- | --- | --- |
| Pytest 10 collection compatibility | `prototype/tests/regression/test_python_ast_parity.py`, `test_python_interpreter_parity.py`, `test_python_to_ast_regression.py`: full run emits three `PytestRemovedIn10Warning` messages for non-Collection parameter iterables (`map` in the warning). Files pass `Path.glob()` iterables to parametrization. | A currently green suite may stop collecting under a future pytest release. | Reproduce under the chosen pytest versions; materialize deterministic collections without changing case identities or snapshots, then compare collected cases before/after. |
| Intentional skip policy needs a coverage audit | The final serial `-rs` run reports 26 Nomi-source/Python-mode skips, 30 Python-source/Nomi-frontend skips, and 10 Python-source skips for each Nomi-family interpreter: 76 total. | These are supported matrix exclusions, not observed dependency failures. Cross-product duplication can still conceal untested supported paths. | Audit fixture/backend coverage while keeping intentional skips. Do not remove skips merely to improve a count. |
| Fixture environment overrides can yield empty selections | `_resolve_modes` and `_resolve_parser_frontends` in `prototype/tests/conftest.py` filter environment values against available names without raising on unknown names. | A typo can produce empty parametrization instead of the intended coverage. This is code-review evidence, not a reproduced failing run. | Test invalid and partially valid env values, decide fail-fast vs explicit warning, and preserve documented valid overrides. |
| Editor execution coverage remains platform-bounded | Existing `extension.test.js` covers activation, symbols, and definitions. New `runner_process.test.js` runs real file/selection tasks in an opened workspace; new unit coverage covers lifecycle/trust/settings. | The five host tests passed locally on macOS, but do not prove Windows/Linux, actual multi-root settings, cancellation, or reload cleanup. | Add the remaining real-host scenarios. The new process suite intentionally skips when no workspace is opened; distinguish that dependency from a pass. |
| Latest macOS host launcher has an executable-name mismatch | `@vscode/test-electron` resolves `Contents/MacOS/Electron`; downloaded VS Code 1.139.1 contains `Contents/MacOS/Code`. The default wrapper failed with `ENOENT` before tests ran. | A harness failure blocks the normal verification command even when extension activation and execution work. | Repair/version the test launcher in the separate pass. Existing test config/dependency lock were left unchanged. Local latest-host verification used an ignored config with `useInstallation.fromPath` and explicit files/workspace. |
| JS dispatch completeness check is partly textual | `prototype/tests/unit/runtime/test_js_core_runtime_backend.py` includes registered-node handler checks; the file also has actual parity/session scenarios. | A handler name in source is not proof of correct behavior for every registered Core node. | Inventory behavioral fixture coverage per Core node; add missing success/failure/control-flow cases without replacing useful existing parity tests. |

## Reproduction

```bash
python3 -m pytest -q -n 0 -rs
python3 -m pytest -q -n 0 prototype/tests/regression/test_python_ast_parity.py
python3 tools/vscode/nomi/scripts/nomi-vscode.py test
```

Use the same configured environment as the implementation checks. Dependency
or GUI/network setup failures are not automatically language/test defects.

The first broad scan reported one documentation inventory failure because the
new transposed research document had not yet been indexed while the scan was
running. That was an unfinished documentation change, not a test bug; indexing
was corrected in research commit `fc54379`. No snapshots were regenerated and
no assertions were relaxed.

Release confidence also needs minimum-version Python and multi-platform
editor runs. The current local Python environment is 3.14; declaring 3.12 as
the minimum is not evidence that this session tested every supported version.
The new CI minimum-version job covers wheel/CLI behavior, not the entire AST
snapshot corpus. Those hosted jobs have not been executed in this session.

Final local result: **1427 passed, 76 skipped, three deprecation warnings**.
No existing tests or regression snapshots changed. New tests intentionally
failed first for notebook output/boundaries, launcher lifecycle, inspection
arguments, and RAG resource/framing failures before their implementation fixes.
