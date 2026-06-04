# Project Improvement Review 2026-06-03

> Status: source evidence from the 2026-06-03 improvement scan.
>
> Scope: dated full-repo critical review. Durable actions from this scan have
> been consolidated into
> [`implementation_todos.md`](../language/implementation_todos.md#current-consolidated-priority-2026-06-03)
> and [`implementation_codebase_audit.md`](../language/implementation_codebase_audit.md#consolidation-refresh-2026-06-03).
> Keep this file as evidence, not as a second backlog.

## Scan Evidence

Commands run during this pass:

```bash
rg --files -g '!*__pycache__*' -g '!*.pyc' -g '!node_modules' -g '!dist' -g '!build'
python3 -m tools.rag_mcp.cli search "implementation evolvability capability matrix AI collaboration feature metadata"
python3 .codex/scripts/agent_doctor.py
python3 -m tools.syntax.inspect --stage capabilities
python3 -m tools.syntax.inspect --stage parser-frontends
python3 -m tools.syntax.inspect --stage eval-backends
python3 -m tools.syntax.inspect --stage resolved-pipelines
python3 scripts/check_web_runtime.py
pytest -q
```

Observed validation state:

| Check | Result | Note |
| --- | --- | --- |
| Full pytest | pass | `1198 passed, 76 skipped, 10 warnings` |
| Web/runtime check | pass | Manifest fresh, WASM parser fresh, 55 browser/runtime contract tests passed |
| Agent doctor | pass | RAG index rebuilt after the docs edit; `.nomi/rag_index.json` is derived and ignored |
| Docs lifecycle | pass | Every `docs/**/*.md` has a near-top `> Status:` block |
| Git tracking hygiene | mostly good | Reports, caches, local state, and Codex runtime logs are ignored/untracked |

## Consolidated Findings

| Finding | Durable home |
| --- | --- |
| The project is healthy: full pytest, web/runtime checks, docs lifecycle, and agent infrastructure all passed. | This evidence note. |
| Capability honesty is the next highest-leverage fix; many user-facing axes are still derived/defaulted. | `implementation_todos.md`, Track 0A. |
| Source-to-meaning has two live roads: Python/session default and browser Rust/WASM -> JS Core Runtime. | `implementation_codebase_audit.md`, browser/runtime parity items. |
| Surface/Core authority is still aspirational where `DataDecl`, `MatchExpr`, `PipeExpr`, and `BindingTarget` lower through Python AST paths. | `implementation_codebase_audit.md`, Surface/Core findings. |
| Diagnostics and explanation are the product gap; every feature still reports `explain: no`. | `implementation_todos.md`, runtime/result contract items. |
| The docs are strong but heavy; future scans should fold actions into existing backlogs instead of becoming permanent planning spines. | `docs/README.md`, `implementation_todos.md`. |

## AI-Slop And Workspace Hygiene

This scan did not find severe tracked AI-slop. The remaining issues are
ordinary but worth cleaning before the next wave of agent work.

| Signal | Evidence | Severity | Action |
| --- | --- | --- | --- |
| Unanchored TODOs | `Dockerfile:1`, `scripts/run_nomi_docker.py:5`, `prototype/tests/data/sample_sources/interpreter/blocks.nomi:51` | low | Convert to `NOMI-*` anchors or remove if stale. |
| Stale RAG index | Warning appeared during scan, then cleared after `python3 -m tools.rag_mcp.cli build` | resolved | Rebuild after large docs/code edits when `agent_doctor.py` warns. |
| Local cache clutter | Many `__pycache__`, `.pytest_cache`, `.codex/*.sqlite`, logs, and reports exist locally | low | No tracked risk; optional cleanup before handoff screenshots or packaging. |
| Capability defaults | Most feature exposure is inferred, not declared | medium | Promote explicit axes before feature promotion. |
| Runtime placeholders | `prototype/runtime/diagnostics.py` and semantic events are placeholder-shaped | medium | Wire one real event family before adding more diagnostics prose. |
| Docker/setup TODO wording | Dockerfile and macOS setup TODO are informal and misspelled | low | Tighten or anchor during setup/tooling pass. |

## Review Bottom Line

Nomi's main risk is no longer "AI wrote careless code." The current risk is
more subtle: enough good infrastructure now exists that derived tables,
partial Core IR, browser success, and polished docs can sound more authoritative
than they are. The next pass should make the existing truth surfaces stricter,
not add another layer of vision.
