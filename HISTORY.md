# Nomi Project History

> Status: condensed project evolution. Current behavior, decisions and priorities
> belong to the live guides, design contracts and roadmap.

This is the single narrative history of the project. Detailed old reviews,
handoffs, measurements and session logs remain available through Git history;
they are not parallel specifications or task queues. Publication dates and host
versions in research evidence are retained because they delimit that evidence.

## Prototype Foundation

Nomi began as a Python-hosted language experiment with Lark, Python AST and
layered interpreters. It explored reductions, constraints, patterns, callbacks
and resumable block control. Parser work established LALR parsing, explicit
postlexing, caches, source-position profiles and interchangeable frontend
experiments. Python compatibility was a laboratory tool rather than the final
language definition.

## Language And Documentation Consolidation

The target converged on explicit functions, immutable nominal data, transactional
binding and structural choice, typed expected failure, visible mutation,
effects/capabilities and structured lifetime. Several runnable shorthands were
rejected from the target. Comparative language research was consolidated into
shared feature owners, with focused design packets joining evidence, contracts,
pressure programs and implementation gaps.

## Portable Runtime And Usable Tools

A Rust/WASM parser and JavaScript runtime made the browser independent of
Pyodide by default. Runtime inspection, sessions, diagnostics and capability
registries became shared boundaries. Packaging, CLI, Jupyter, editor execution,
Unicode/text handling, call/default binding, cleanup, collection ordering and
browser recovery gained focused checks. Static assets and samples acquired
freshness checks. Host compatibility repairs did not imply target conformance.

## First Product And Reasoning Experiments

The first product scope became calculation, JSON report/repair/export and
checked local reuse. A bounded report library with two manual schemas runs
before the complete target nominal-data/Result system is ready. Research also
expanded into engine-free descriptions, statistical plans, exact scientific
maps, scoped binders, premise support, theory interpretation, typed program
proposals and finite adaptive inquiry with independent replay.

## Current-State Consolidation

Earlier notes about binding, composition, rewriting, category theory and a
structured-data comparison tool were reconciled with accepted contracts.
Further portable, incremental, streaming and learned-policy candidates remain
explicitly unaccepted. DIGEST.md supplies the repository story. Active documents
now describe present meaning, support, gaps and next actions; chronological
receipts and AI-session narration are no longer appended to them.

The playground is published at https://durgadatta.github.io/nomi/web/ from the
main branch. Browser verification, rather than an older audit or commit name,
establishes what the public site currently serves.

## Recovering Detailed Evidence

Use `git log --follow -- PATH` and `git show REVISION:PATH` when an old artifact
is actually needed. Removed handoff and dated-review files remain recoverable
that way. For present work start with [DIGEST.md](DIGEST.md), the
[implementation map](docs/orientation/artifacts_and_usage.md), the
[roadmap](docs/orientation/project_roadmap.md) and the registered current bridges.
Do not restore old essays as competing live authority.
