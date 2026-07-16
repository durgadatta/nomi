# Nomi Documentation

> Status: canonical documentation entry point.
>
> Nomi keeps one target-language authority, one consolidated research set, and
> a separate implementation orientation. Current prototypes are evidence and
> migration vehicles; they do not define the future language.

## Start Here

For language design, read:

1. [Target Design](design/README.md)
2. [Syntax](design/syntax.md)
3. [Semantics](design/semantics.md)
4. [Industrial Model](design/industrial.md)
5. [Decision Ledger](design/decisions.md)
6. [Target Program](design/target.nomi)

For the evidence and unresolved forks behind those choices, read:

1. [Research Overview](research/README.md)
2. [Language Families](research/families.md)
3. [Design Convergences](research/convergences.md)
4. [Open Questions](research/open_questions.md)

For the current repository and runtime, read:

1. [Artifacts And Usage](orientation/artifacts_and_usage.md)
2. [Implementation Guideline](orientation/implementation_guideline.md)
3. [Exploratory Implementation Doctrine](orientation/exploratory_implementation_doctrine.md)

The [2026-07-16 Language Design Review](review/2026-07-16.md) records why the
old design corpus was consolidated and gives the concrete action sequence.

## Authority

When artifacts disagree, use this order:

```text
current user decision
-> docs/design target
-> docs/research evidence
-> docs/orientation current implementation map
-> executable prototypes and tests
-> Git history
```

Tests remain authoritative for what a supported implementation does today.
They are not a veto over a new target-language decision.

Target-only source belongs in `docs/design/target.nomi`. Files under `samples/`
are runnable product fixtures and must remain aligned with parser, runtime,
tests, generated web manifest, and browser execution.

## Documentation Types

| Location | Purpose | May decide target semantics? |
| --- | --- | --- |
| `docs/design/` | Canonical target language and industrial contracts | Yes |
| `docs/research/` | Consolidated evidence and bounded open questions | No; informs decisions |
| `docs/orientation/` | Current implementation, tooling, and collaboration | No |
| `docs/review/` | Dated judgments and evidence snapshots | No; decisions must be promoted |

New design notes should normally update an existing canonical file. Add a new
document only when it owns a durable information type that the current set
cannot hold cleanly.

## Design Change Workflow

1. Start with a failing or awkward program, not a borrowed feature.
2. Check [Open Questions](research/open_questions.md) and existing research
   convergence before doing new broad research.
3. Compare at least two Nomi surfaces and the explicit long form.
4. Specify semantics, formatting, diagnostics, effects, and interactions.
5. Update the [Target Program](design/target.nomi).
6. Record the decision or experiment in the [Decision Ledger](design/decisions.md).
7. Only then map the change onto parser, Surface/Core, runtimes, tests, and web.

## Implementation Orientation

- [AI Collaboration](orientation/ai_collaboration.md): repository doctrine for
  AI-assisted design, implementation, critique, and checkpoints.
- [Artifacts And Usage](orientation/artifacts_and_usage.md): current execution
  pipelines, runtime artifacts, samples, and validation commands.
- [Exploratory Implementation Doctrine](orientation/exploratory_implementation_doctrine.md):
  reversible implementation while semantics are still moving.
- [Implementation Guideline](orientation/implementation_guideline.md): current
  engineering posture and project history.
- [Performance Notes](orientation/performance_notes.md): parser/runtime
  performance experiments and measurements.
- [RAG MCP Context](orientation/rag_mcp.md): local code/document retrieval
  setup.
- [VS Code Extension](orientation/vscode_extension.md): local editor tooling.
- [WASM-JS Runtime Review](orientation/wasm_js_runtime_review.md): browser
  parser/runtime architecture evidence.

## Reviews

- [Language Design Review 2026-07-16](review/2026-07-16.md): syntax-first reset,
  research consolidation, target language, and ordered actions.

## Complete Markdown Inventory

This list is intentionally complete and is checked by tests.

### Design

- [Target Design](design/README.md)
- [Syntax](design/syntax.md)
- [Semantics](design/semantics.md)
- [Industrial Model](design/industrial.md)
- [Decision Ledger](design/decisions.md)

### Research

- [Research Overview](research/README.md)
- [Language Families](research/families.md)
- [Design Convergences](research/convergences.md)
- [Open Questions](research/open_questions.md)

### Orientation

- [AI Collaboration](orientation/ai_collaboration.md)
- [Artifacts And Usage](orientation/artifacts_and_usage.md)
- [Exploratory Implementation Doctrine](orientation/exploratory_implementation_doctrine.md)
- [Implementation Guideline](orientation/implementation_guideline.md)
- [Performance Notes](orientation/performance_notes.md)
- [RAG MCP Context](orientation/rag_mcp.md)
- [VS Code Extension](orientation/vscode_extension.md)
- [WASM-JS Runtime Review](orientation/wasm_js_runtime_review.md)

### Reviews

- [Language Design Review 2026-07-16](review/2026-07-16.md)
