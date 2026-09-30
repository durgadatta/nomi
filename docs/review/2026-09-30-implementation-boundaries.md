# Implementation Boundary Review

> Status: dated discovery/fix checkpoint, preserving current supported behavior.
>
> Research checkpoint `fc54379` completed the semantic transpose and concrete
> syntax atlas before this implementation diversion. Target syntax is unchanged.
>
> Scope expanded to the whole project after the user clarified that editor
> work is only one slice. Discovery, fixes, and verification were interspersed;
> each independent task was committed separately.

## Discovery And Fixes

| Discovery | Change | Evidence gate |
| --- | --- | --- |
| Wheel declarations omitted runtime data and a minimum Python version. | Declare Python 3.12+, package grammar/host/JS/WASM/demo data, exclude test/dependency/build package trees. | Build a clean-copy wheel and run public Python and optional JS runtime plus default CLI from outside checkout. |
| CLI depended directly on the parser default and relative demo path. | Runtime owns the default; CLI passes only explicit overrides. Use package-relative demo and a script-local import path for source execution. | Existing CLI tests plus isolated dependency-free `--help` and installed-demo checks. |
| Node backend combined semantics with process/JSON mechanics. | Extract reusable one-shot `json_process.py`; leave Core verification, serialization, result mapping, and capabilities in the adapter. | Existing JS parity/session tests plus new malformed-response, launch failure, timeout, and argv checks. |
| Editor composed POSIX shell text and ignored failed/cancelled saves. | Plain-data runner plan plus VS Code `ProcessExecution` task; trust, opened-folder, and saved-file gates. | Eleven unit checks and five real-host checks, including file names with spaces/quotes and selection cleanup. |
| Selection temp names could collide, leaked files, and used temp-file workspace lookup. | Unique temp directories, original-document scoped settings/cwd, cleanup at task completion or failed launch. | Concurrent selections, outside-root cwd, and launch-failure scenarios. Empty-workspace rejection was discovered by real-host checks and fixed explicitly. |
| Notebook introspection coupled to parser/interpreter internals; silent requests leaked streams/command output. | Public session creation/inspection/bindings; suppress output while preserving silent cell state. | New tests failed first; 15 notebook checks and actual kernel output `7`/`30` passed after the fix. |
| Playground launcher opened the browser before starting the server, did not reap interrupted children, and allowed invalid/overflow ports. | Bounded listener readiness, finally-based shutdown/wait/kill, port range guard, localhost URL for wildcard binding. | New lifecycle checks failed first; 11 checks passed, including a real HTTP/interrupt scenario. |
| Inspection CLI copied Core/backend orchestration and manually scanned arguments. | Delegate 16 supported views to runtime inspection; preserve full-pass output and fenced parser debug views; argparse validates inputs; source invocation avoids stdlib `inspect` shadowing. | Nineteen new checks plus existing target/profile checks: 49 passed; direct source Core verification passed. |
| RAG resources bypassed configured selection, index discovery followed escaping/excluded symlinks, and subfolder-source URIs could not round-trip. | Shared discovery rules check resolved boundaries; source-relative resource URIs; listing/reads recheck selection. | New tests reproduced five failures; 15 resource/retrieval checks passed after the fix. |
| Invalid MCP stdio frames crashed the server, and notifications could receive replies. | Parse/envelope errors are framed responses; valid later requests continue; no notification replies. | Seven new tests failed first; combined RAG suite passed 22 checks. |
| GitHub workflow ran only selected smoke/browser contracts, not the project gold-standard suite. | Separate full Python 3.14 suite and Python 3.12 installed-wheel/CLI jobs; existing playground gates retained. | Workflow YAML parsed; five jobs verified. Existing action `v7` tags checked against official GitHub refs. Hosted runs remain pending. |
| Extension source link pointed at a placeholder repository. | Repository URL now matches `git remote origin`; publisher/license choices remain open. | Parsed metadata check; local VSIX packaging succeeds without publishing. |

This pass adds boundaries around existing operations, not an alternative
semantics layer. No grammar/interpreter rules, backend defaults, supported
samples, browser JS/WASM engine outputs, existing tests, or snapshots changed.
The web manifest is regenerated for the added Python runtime module.

## Separate Commits

| Commit | Logical task |
| --- | --- |
| `55f8bcc` | Package runtime assets and decouple CLI defaults. |
| `f44bf0a` | Runtime JSON process transport. |
| `0a461aa` | Editor runner/task lifecycle. |
| `d9997e9` | Notebook facade and silent requests. |
| `6f8b9e0` | Playground launcher lifecycle. |
| `e20c21a` | Inspection CLI deduplication. |
| `5ac9889` | RAG resource selection/URI boundaries. |
| `156f1a8` | MCP stdio framing recovery. |
| `93944cf` | Full-suite/minimum-Python CI gates. |
| `9e73fbd` | Repository metadata alignment. |

General layer/documentation/test-review reconciliation is a separate docs
checkpoint after these implementations, not bundled into an engine rewrite.

## Final Global Scan

| Area | Evidence inspected/executed | Result |
| --- | --- | --- |
| Packaging/CLI | Package discovery/data, script imports/defaults, clean-copy wheel tests outside checkout. | Fixed and verified on local Python 3.14; minimum-version CI declared but not run here. |
| Runtime/parser/Core | Registries, session/API policy, process adapters, inspection duplication, native/parser parity in the full suite. | Defaults/artifacts preserved; facade duplication removed. Further native extraction needs source-map/session contracts and measurements. |
| Browser/playground | Worker/lowerer/runtime ownership, manifests/WASM metadata, launcher, 55 contracts, Chromium UI. | Sample/Pipeline/scratch and freshness passed. Regex/raw-expression bridge remains a declared migration risk. |
| Notebook | Session ownership, completion/AST/output, kernelspec/launcher, notebook contracts and real kernel. | Direct introspection coupling and silent output fixed; visible execution retained. |
| Editor | Runner settings/lifecycle, task/trust API, real host, VSIX contents/metadata. | Process execution verified on macOS; default latest-host harness remains a separately noted test-tool issue. |
| RAG/agent tooling | Source discovery/resource policy, stdio errors, hooks/config/packet doctor. | Read/framing defects fixed; ignored retrieval index refreshed. No agent instruction proliferation. |
| CI/release | Workflow jobs/action refs, toolchain, artifacts, license/publisher/origin. | Full/minimum-version gates added; source link corrected. Hosted CI and owner-approved licensing/publisher remain pending. |
| Docker/deployment | Dockerfile (Python 3.12), host/container launcher and notebook entrypoint read; static deployment workflow reviewed. | No container build, daemon startup, hosted deployment, package publication, or remote push performed. Do not mistake static review for end-to-end validation. |
| Docs/tests | Canonical inventory/authority, runtime maps, warnings/skips, test selectors and coverage. | Runtime docs reconciled; suspected test defects reserved for the requested separate pass. |

The repeated scan produced additional notebook, launcher, inspection, RAG,
CI, and release-link fixes after the initial boundary changes. Remaining items
below require a semantic/resource/release contract or the separate test pass;
they were not hidden by promoting unsupported capabilities or relaxing tests.

## Issues Still Open

- The browser `Expr::Raw`/regex lowering bridge and duplicated scanning are
  already documented in [Artifacts And Usage](../orientation/artifacts_and_usage.md).
  They need structured payload/parity work, not an untested parser rewrite.
- Parser frontend registration remains a large module with initialization
  coupling. Extraction should follow a measured change pressure and the
  existing registry, not create a competing backend list.
- JSON transport has no persistent-session, output-size, memory, sandbox,
  or process-tree termination contract. A timeout parameter alone does not
  establish safe execution of arbitrary untrusted code.
- Extension cleanup occurs while its host is alive. Reload/crash cleanup,
  multi-root real-host scenarios, and Windows/Linux execution remain future
  work; macOS file/selection execution was verified in this pass.
- Package entry points for repository-oriented development tools still require
  their checkout/configuration; installed language execution is the profile
  verified here. Packaging every repository workflow needs a separate scope.
- No root license file exists, while the extension metadata declares MIT and
  carries an unconfirmed publisher. Repository metadata now matches origin.
  Licensing/publication require an
  owner decision; no license was invented or package published.
- Python 3.12 is the AST-imposed minimum; the local validation environment is
  Python 3.14. The new clean minimum-version CI job still needs a hosted run.
- RAG source rechecks currently enumerate selected files. Measure large book
  collections before adding a cache; cached permission decisions must not
  outlive configuration changes. Old search snippets require index rebuilding.

The [layer map](../orientation/implementation_layers.md) owns the ordered next
steps and admission gate for native/optimized engines. The
[test review](2026-09-30-test-issues.md) separately records suspected test defects
and gaps for the requested later pass.

## Validation Record

- Full local suite: **1427 passed, 76 intentional mode/frontend skips, three
  existing pytest deprecation warnings** on Python 3.14.0rc3.
- Web/runtime: **55 passed**; manifest has 121 runtime files and nine samples;
  eight WASM outputs are fresh. Agent doctor passes after ignored RAG refresh.
- Chromium: actual `demo_terse.nomi` output, Pipeline view, and scratch `42`
  passed. Screenshots/trace/logs remain ignored under `reports/web-browser/`.
- Notebook: actual installed kernel smoke printed `7` and `30`.
- Editor: eleven unit checks, five real-host checks on macOS VS Code 1.139.1
  with the actual `Code` executable and an opened workspace. Existing three
  navigation tests also passed in cached 1.119.0. The default latest launcher
  `ENOENT` is recorded separately, not counted as a successful wrapper run.
- VSIX: packaged locally, runtime modules included, tests/dependencies excluded;
  missing-license warning remains. Nothing published.
- Five design packets remain coherent; no target syntax was changed.

Local latest-host reproduction uses the ignored
`tools/vscode/nomi/.vscode-test/latest-check.cjs`, which sets explicit test files,
an opened repo workspace, and `useInstallation.fromPath` to the downloaded
macOS `Code` executable. From the extension directory:

```bash
NOMI_TEST_PYTHON=/absolute/path/to/project/python npm test -- --config .vscode-test/latest-check.cjs
```

That machine-local helper is validation evidence, not a committed repair of
the test launcher. The durable repair belongs to the separate test pass.

## Session Close Checkpoint

After research commit `d897cca`, the user requested one final bounded
implementation pass and session wind-up. This inspected the existing transport,
Docker/notebook launchers, public caller imports, and verification scripts.
It did not reopen the language design or start a native-engine extraction.

| Discovery | Fix / commit | User-facing consequence |
| --- | --- | --- |
| Process text decoding depended on locale; arbitrary stderr could mask success/failure; unencodable requests spawned before encoding failed. | `057d1f5`: binary pipes, explicit UTF-8 request/stdout, diagnostic-only replacement decoding, pre-launch encoding rejection. | Non-ASCII data crosses the engine boundary predictably; corrupt output names the backend instead of leaking a codec exception. |
| Python JSON parsing accepted non-JSON NaN/Infinity tokens from a backend. | `057d1f5`: reject those tokens recursively during JSON parsing; schema ownership stays in the adapter. | A malformed engine response cannot silently enter the runtime as a valid JSON object. |
| Invalid ports/wait/resources reached Docker setup; token punctuation split the URL query/fragment. | `d3e00f5`: validate numeric options before setup and use structured query encoding. | Invalid commands fail before host setup; user-supplied tokens remain one authentication value. |

New tests reproduced **19 failures and four passes** before the fixes;
the focused transport/Node/launcher set then passed all **46 tests**.
Only two new test files were added. No existing tests, snapshots, samples,
interpreter rules, backend defaults, extension code or WASM outputs changed.
Web generation produced no tracked artifact changes.

Final validation on local Python 3.14.0rc3:

- Full suite: **1454 passed, 76 skipped, 12 existing warnings** with four workers.
- Web/runtime: **55 passed**; manifest and all eight WASM outputs fresh.
- Fresh Chromium: real sample output, Pipeline metadata and scratch `42` passed;
  ignored screenshots/logs/trace were regenerated. Its temporary server exited.
- Five registered design packets coherent; new tests and transport lint passed.

No Docker daemon/setup/build, new extension-host run, hosted CI, minimum-Python
run, publication or remote push was performed. Docker tests isolate option/URL
logic; they are not container integration evidence. The helper still has no
output/memory/process-tree limit. Numeric representation limits, duplicate keys
and adapter result schemas remain separate contracts. Docker launch logs still
print tokens; URL encoding is not redaction or a new credential-security claim.
The existing deferred-test findings remain in
[the separate review](2026-09-30-test-issues.md), not silently fixed here.

### Exact Resume Point

Design-first continuation: read [function contracts](../design/function_contracts.md)
and execute **DW1** in [the data/notation synthesis](../research/data_workflows/nomi_candidates.md):
write and compare callback, schema-bound expression and collect contracts under
effect/retention failures. Do not begin a query engine before those contracts close.
Implementation continuation, when requested, uses
[the existing layer plan](../orientation/implementation_layers.md); test-harness
repairs use the separate test pass. This checkpoint records completed evidence,
not another live backlog.
