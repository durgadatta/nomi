# GitHub Playground And Agentic Setup Review - 2026-09-29

> Status: dated review evidence and actionable plan.
>
> Scope: reconnect Nomi's current implementation, VS Code workflow, GitHub
> agent setup, and public browser playground. Durable language decisions still
> live under `docs/design/`; this review is about making the runnable,
> user-facing path trustworthy.

## Executive Summary

Nomi is in better shape than a cold restart usually suggests. The web runtime
checks pass, the WASM parser metadata is fresh, the browser playground is
documented as the default Rust/WASM plus JavaScript Core Runtime path, and the
agent infrastructure passes its own doctor check.

## Implementation Progress - 2026-09-29

The first implementation slice is now present locally. The baseline findings
below describe the state at review time; this table is the current handoff.

| Plan steps | Current state | User-facing evidence |
| --- | --- | --- |
| 1.1-1.5 | GitHub instructions and contribution templates added | Playground work is routed to shared skills and explicit checks. VS Code's actual instruction loading still needs an editor check. |
| 2.1-2.3 | `playground-ci.yml` added with independent Fast smoke, Web runtime, and Browser smoke jobs | PRs will exercise the public sample path after the workflow is pushed; no hosted CI run has been observed yet. |
| 4.1-4.3 | `scripts/check_web_browser.py` added | Chromium loads the real manifest/sample, runs `demo_terse.nomi`, checks exact output and visible pipeline metadata, then types and runs a scratch program producing `42`. |
| 4.5 | Browser dependency is an optional `web-test` extra; browser job is unconditional in PR CI | Local runtime checks remain quick. Future Pages deployment must depend on all three jobs. |
| 6.1-6.3 | Runtime check, browser smoke, launch, and agent-doctor tasks added | Contributors can exercise the GitHub user path from VS Code's task menu. |
| UI regression | Empty result placeholder now honors `hidden` | A successful run no longer shows "No result" above actual output; browser smoke checks this. |

Verification and constraints:

- A fresh Python 3.11 environment failed to import the interpreter at
  `ast.TypeAlias`. CI therefore uses Python 3.14 and Node.js 24; broad Python
  version support remains a separate task.
- Fresh local Python 3.14.0rc3 dependencies passed all 55 web/runtime contracts
  and 10 fast smoke checks. Local Node is 25.9.0; the hosted Linux/Python 3.14/
  Node 24 combination still needs its first Actions run.
- Chromium runs the real worker, Monaco, and CDN assets, with no runtime mocks.
  Browser evidence goes to ignored `reports/web-browser/` and the CI artifact
  `playground-browser`. The new visibility assertion reproduced the placeholder
  bug before its CSS fix.
- After the fix, the full Chromium smoke passed, and the output screenshot
  confirmed the empty placeholder was gone. Task JSON, workflow YAML, and
  browser-script lint checks passed. The agent doctor passed after rebuilding
  the ignored RAG index.
- No Pages deployment settings have changed. Caching and a README badge remain
  deferred until hosted checks are stable. Mobile layout coverage (4.4) and
  feature-level capability promotion (phase 5) remain open.

### Next Exact Slice

1. Review and push these changes, then observe all three `Playground CI` jobs
   on GitHub. Address any Linux/toolchain failures before changing Pages.
2. In repository settings, require Fast smoke, Web runtime, and Browser smoke
   for merges to `main`; a workflow file alone does not enforce branch rules.
3. Inspect the actual Pages publishing source and record its branch/environment
   in `docs/orientation/artifacts_and_usage.md`. The prior review only verified
   the public URL, not repository settings.
4. Prepare a minimal Pages artifact and verify it with this same browser script.
   It must retain the `/nomi/web/` relative-import layout, all fetched samples,
   and the worker/runtime/WASM dependencies.
5. Wire deployment to the same revision's successful checks, include the commit
   in release evidence, and rerun the smoke against the published `/nomi/web/`
   URL. Preserve the previous Pages source as the rollback route.

### Retrospective

Browser evidence found a visible defect that runtime contracts could not catch.
The durable improvement is the browser check shared by local tasks and CI.
The isolated installation also exposed an implicit Python version constraint;
the workflow now makes its tested version explicit. Language syntax, feature
metadata, and runtime semantics did not need to change for this slice.

## Review Baseline

The biggest gap is GitHub-facing operational glue:

- there was no `.github/` directory before this review;
- the live playground URL is reachable, but its published timestamp is older
  than the local validated tree;
- GitHub/VS Code agent instructions were not wired to the existing
  `AGENTS.md`, skills, VS Code extension tasks, or playground checks;
- pull requests had no template requiring playground, manifest, WASM, or
  sample impact to be stated;
- user-facing playground problems had no structured issue intake.

The near-term product goal should be:

```text
Any change to parser, runtime, samples, web UI, or VS Code support should make
it obvious whether a new user can still open the GitHub Pages playground and
run a Nomi sample.
```

## Evidence Collected

Reviewed local artifacts:

- `README.md`
- `docs/orientation/artifacts_and_usage.md`
- `docs/orientation/ai_collaboration.md`
- `docs/orientation/exploratory_implementation_doctrine.md`
- `docs/orientation/vscode_extension.md`
- `docs/orientation/wasm_js_runtime_review.md`
- `tools/vscode/nomi/README.md`
- `.agents/README.md`
- `.agents/skills/nomi-ai-native/SKILL.md`
- `.agents/skills/nomi-web/SKILL.md`
- `.agents/skills/nomi-language-design/SKILL.md`
- `.vscode/tasks.json`
- `scripts/check_web_runtime.py`

Checks run:

| Check | Result |
| --- | --- |
| `git status --short` | clean before edits |
| `python3 -m tools.syntax.inspect --stage capabilities` | produced capability table |
| `python3 -m tools.syntax.inspect --stage resolved-pipelines` | browser default is `rust-fast-ast-wasm -> js-core-runtime` |
| `python3 scripts/check_web_runtime.py` | pass: 55 browser/runtime contract tests passed, manifest and WASM fresh, agent doctor pass |
| `python3 .codex/scripts/agent_doctor.py` | pass |
| `curl -I https://durgadatta.github.io/nomi/web/` | HTTP 200 from GitHub Pages; `last-modified` was 2026-05-24 |

External documentation checked:

- GitHub repository instructions for Copilot in IDEs:
  <https://docs.github.com/en/copilot/how-tos/configure-custom-instructions-in-your-ide/add-repository-instructions-in-your-ide>
- GitHub support matrix for repository, path-specific, and agent instructions:
  <https://docs.github.com/en/copilot/reference/custom-instructions-support>
- VS Code custom instruction formats:
  <https://code.visualstudio.com/docs/agent-customization/custom-instructions>
- GitHub Pages custom workflow model:
  <https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages>

## What Is Already Done

### User-facing runnable surfaces

| Surface | Current state | User value |
| --- | --- | --- |
| GitHub Pages playground | Public URL exists and returns HTTP 200 | A newcomer can try Nomi without installing anything. |
| Browser runtime path | JS/WASM path is current default | Faster first-run path than the old Pyodide hot path. |
| Sample manifest | `web/manifest.json` and metadata are fresh | Playground samples track runnable repo files. |
| Runtime result UI | Output, bindings, diagnostics, and pipeline views exist | Users can see what happened and which pipeline ran. |
| Notebook cells | `# %%`, run-current, run-all, and session behavior documented | Playground can teach Nomi incrementally. |
| README entry point | README links the live playground near the top | The public path is discoverable. |

### Validation and contracts

| Surface | Current state | Why it matters |
| --- | --- | --- |
| `scripts/check_web_runtime.py` | Combines manifest freshness, WASM freshness, web contracts, and agent doctor | Good candidate for the main GitHub Actions gate. |
| WASM build metadata | `prototype/runtime/js/pkg/nomi_parser_build.json` records source hash and outputs | Prevents stale generated parser artifacts from silently shipping. |
| Manifest metadata | `web/manifest_metadata.json` records counts and digest | Lets CI detect sample/runtime drift. |
| Browser pipeline tests | `prototype/tests/contracts/test_wasm_js_pipeline_contract.py` wraps Node pipeline smoke | CI can catch browser execution drift through pytest. |
| Host capability contracts | Contract tests exist | Browser authority can stay explicit as features grow. |

### Agent and VS Code surfaces

| Surface | Current state | Why it matters |
| --- | --- | --- |
| `AGENTS.md` | Root project map loaded by agents | Shared working contract for Codex-style agents. |
| `.agents/skills/` | Domain skills exist for parser, runtime, web, tests, language design, and AI-native maintenance | Agents can route work by task type. |
| `.codex/hooks/` and `.claude/` shims | Doctor check passes | Agent setup is already validated locally. |
| `.vscode/tasks.json` | Extension setup/test/package tasks exist | VS Code users can run the extension workflow without memorizing commands. |
| VS Code extension | Syntax highlighting, snippets, run commands, symbols, hover, completions, and first-pass definition | Local editing has a credible starter tool. |

## Missing Or Weak

### 1. GitHub is not yet the operational center

There is now a `.github/` directory for agent instructions and templates, but
there is still no Actions workflow. That means the strongest local check,
`python3 scripts/check_web_runtime.py`, is not enforced on pull requests.

User-facing risk: a parser/runtime/sample change can pass local intent but ship
a broken public playground.

### 2. Pages freshness is invisible

The live URL returns HTTP 200, but the observed `last-modified` header was
2026-05-24 while this review is dated 2026-09-29. That may be fine if no public
deployment was intended, but today there is no visible release record tying the
current validated repo state to the deployed playground.

User-facing risk: README sends users to a playground that may lag behind the
current docs, samples, and runtime contracts.

### 3. The playground lacks a real browser smoke gate

The current checks cover manifest freshness, WASM freshness, Node pipeline
execution, and contracts. They do not actually load `web/index.html` in a
browser, click Run, and assert that a visible sample result appears.

User-facing risk: JavaScript modules can be valid and runtime contracts can
pass while CDN loading, Monaco layout, worker wiring, or DOM integration breaks
the public first minute.

### 4. VS Code and GitHub agent workflows were adjacent, not integrated

The VS Code extension has local tasks. The agent setup has Codex and Claude
contracts. GitHub Copilot in VS Code expects `.github/copilot-instructions.md`
and optional `.github/instructions/**/*.instructions.md`. Before this review,
those GitHub-native instruction files did not exist.

User-facing risk: agent work started from VS Code may skip the same playground
checks that protect the browser user path.

### 5. Product capability honesty is still manual

`tools.syntax.inspect --stage capabilities` says every implemented feature has
`web = no`. The browser nevertheless has a default JS/WASM runtime and samples
that run. This is partly honest because feature-level browser promotion is not
claimed, but it also means a user-facing playground readiness table does not
yet exist.

User-facing risk: contributors cannot quickly tell which syntax is expected to
work on GitHub Pages versus only in CLI/tests.

## Work Plan

### Phase 1: GitHub agent and contribution surfaces

**Goal:** make GitHub and VS Code agents start with the same user-facing
playground priorities as Codex/Claude.

| Step | Action | Files | Completion evidence |
| --- | --- | --- | --- |
| 1.1 | Add repository-wide Copilot instructions that route agents to `AGENTS.md`, `.agents/skills/`, and playground checks. | `.github/copilot-instructions.md` | Copilot references the file in VS Code; instructions stay under one page. |
| 1.2 | Add path-specific instructions for web/playground work. | `.github/instructions/web-playground.instructions.md` | Agents touching `web/**`, `prototype/runtime/js/**`, `samples/**`, or web scripts see the runtime checks. |
| 1.3 | Add path-specific instructions for VS Code extension work. | `.github/instructions/vscode-extension.instructions.md` | Agents touching `tools/vscode/nomi/**` see extension wrapper commands and web syntax-highlighting coupling. |
| 1.4 | Add PR template requiring playground impact, checks, and generated artifact status. | `.github/PULL_REQUEST_TEMPLATE.md` | Every PR asks whether users can still run a sample in the playground. |
| 1.5 | Add playground issue template. | `.github/ISSUE_TEMPLATE/playground.yml` | Users can report sample, browser, URL, diagnostics, and expected output. |

### Phase 2: CI gate for the runnable playground

**Goal:** every PR answers "can the GitHub playground still run Nomi?"

| Step | Action | Files | Completion evidence |
| --- | --- | --- | --- |
| 2.1 | Add a playground CI workflow that installs Python dev deps and runs `python3 scripts/check_web_runtime.py`. | `.github/workflows/playground-ci.yml` | PR checks fail on stale manifest, stale WASM metadata, runtime contract failure, or agent-doctor drift. |
| 2.2 | Add a separate fast smoke workflow or job for `pytest prototype/tests/smoke prototype/tests/contracts/test_web_no_pyodide_default_contract.py`. | `.github/workflows/playground-ci.yml` | Small failures show up quickly before the heavier web/runtime job completes. |
| 2.3 | Add Node setup explicitly because browser pipeline tests use `node`. | workflow | CI environment matches local contract tests rather than relying on runner defaults. |
| 2.4 | Cache pip and npm only after the workflow is green without cache. | workflow | Caching improves speed without hiding dependency/setup bugs. |
| 2.5 | Publish a README badge only after the workflow is stable for several runs. | `README.md` | Public status reflects a trustworthy gate, not aspirational automation. |

### Phase 3: Pages deployment visibility

**Goal:** make the live playground freshness inspectable before automating
production deploys.

| Step | Action | Files | Completion evidence |
| --- | --- | --- | --- |
| 3.1 | Decide whether GitHub Pages remains branch/root based or moves to GitHub Actions deployment. | docs + GitHub settings | Decision recorded with rollback path. |
| 3.2 | Add a lightweight deploy-status note that records expected public URL, source branch, and release check command. | `docs/orientation/artifacts_and_usage.md` or README | A maintainer can tell what should be live. |
| 3.3 | Add a Pages workflow only after CI gate is green. | `.github/workflows/pages.yml` | Deploy job depends on playground CI. |
| 3.4 | Include `web/`, `samples/`, `prototype/runtime/js/pkg/`, `.nojekyll`, and needed static runtime files in the Pages artifact. | workflow | Deployed artifact has everything the static playground imports. |
| 3.5 | After deployment, run `curl -I` and a browser smoke check against the public URL. | workflow or release checklist | Public URL freshness matches the deployed commit. |

### Phase 4: Real browser smoke tests

**Goal:** test the same thing a new user experiences.

| Step | Action | Files | Completion evidence |
| --- | --- | --- | --- |
| 4.1 | Add Playwright or an equivalent browser smoke harness for `web/index.html`. | `prototype/tests/e2e/` or `tools/web/` | Test loads local playground, waits for worker ready state, runs a tiny program, and sees output. |
| 4.2 | Cover the live sample path, not only scratch source. | test fixture | At least `samples/demo.nomi` or `samples/demo_terse.nomi` runs from the sample picker. |
| 4.3 | Assert pipeline metadata appears. | test fixture | Smoke catches regressions where code runs but the pipeline/result contract disappears. |
| 4.4 | Add a mobile-width screenshot/layout smoke only after functional browser smoke is stable. | test fixture | Prevents sidebar/editor/result overlap on the public page. |
| 4.5 | Make this test optional locally but required in Pages release workflow. | docs + workflow | Contributors have a fast path; release still checks the full user path. |

### Phase 5: Capability honesty for users

**Goal:** make runnable-vs-target status obvious inside docs and the
playground.

| Step | Action | Files | Completion evidence |
| --- | --- | --- | --- |
| 5.1 | Add a generated or inspected "playground supported today" table. | `docs/orientation/artifacts_and_usage.md`, maybe `web/` | Table is derived from metadata/checks, not hand-maintained prose. |
| 5.2 | Teach the playground to show a compact runtime profile label. | `web/app.js`, `web/index.html`, `web/style.css` | Users can see JS/WASM path and know this is current runnable behavior. |
| 5.3 | Add unsupported-feature diagnostics for known target-only syntax. | JS lowerer/worker diagnostics | Target-only examples fail with helpful messages instead of generic parser errors. |
| 5.4 | Keep target-only code out of `samples/` unless CLI and browser agree. | PR template + checks | Public sample list remains runnable. |
| 5.5 | Promote one small user-facing "first minute" sample as the release smoke fixture. | `samples/` + tests | The same snippet anchors README, playground, CI, and issue triage. |

### Phase 6: VS Code to playground loop

**Goal:** make local editor work feed the public playground with minimal drift.

| Step | Action | Files | Completion evidence |
| --- | --- | --- | --- |
| 6.1 | Add a VS Code task for `Nomi Web: Check Runtime`. | `.vscode/tasks.json` | VS Code users can run the same gate as CI. |
| 6.2 | Add a VS Code task for `Nomi Web: Launch Playground`. | `.vscode/tasks.json` | A contributor can open the local playground from command palette tasks. |
| 6.3 | Add a VS Code task for `Nomi Agent: Doctor`. | `.vscode/tasks.json` | Agent setup drift is visible in the same editor surface. |
| 6.4 | Keep TextMate and Monaco syntax updates paired. | `tools/vscode/nomi/syntaxes/nomi.tmLanguage.json`, `web/editor.js` | Path instructions point to the actual tokenizer; browser skill includes the new smoke gate. |
| 6.5 | Consider a problem matcher only after structured diagnostics stabilize. | `.vscode/tasks.json` | Compiler/runtime errors eventually surface natively in VS Code. |

## Recommended First Implementation Slice

Original sequence (see Implementation Progress above for completed work):

1. Commit the new `.github` instruction and template files plus this review.
2. Add `.vscode` tasks for `Nomi Web: Check Runtime`, `Nomi Web: Launch
   Playground`, and `Nomi Agent: Doctor`.
3. Add `.github/workflows/playground-ci.yml` running
   `python3 scripts/check_web_runtime.py`.
4. Add a local browser smoke test for the playground.
5. Only then decide whether Pages deploy should be automated from GitHub
   Actions.

This sequence improves the user-facing playground without prematurely turning
deployment into the next debugging surface.

## Acceptance Criteria

The GitHub playground loop is healthy when:

- `README.md` points to a live playground that reflects the latest intended
  public runtime state;
- every PR states playground impact and generated artifact status;
- CI runs the same web/runtime gate as local development;
- VS Code tasks expose the same checks as CI;
- agents working through Codex, Claude, Copilot, or VS Code start from the same
  repository contract;
- a browser smoke test proves that a real user can load GitHub Pages, choose a
  sample, run it, and see output;
- target-only language design remains clearly separated from runnable
  playground samples.
