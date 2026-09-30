# Design Pass Workflow

> Status: canonical AI-assisted language-design workflow.
>
> This process connects research, target decisions, pressure fixtures,
> implementation reality, and agent learning without making any one prototype
> the language specification.

## Purpose

Nomi changes quickly, and a design conversation can otherwise disappear into
chat history or leave four partially overlapping documents behind. A registered
design pass turns one bounded language question into a durable packet:

```text
research evidence
-> canonical design
-> focused target program
-> current-to-target bridge
-> validation and retrospective
```

The registry at `config/design_passes.json` is an index and routing surface. It
does not decide semantics. Target authority remains under `docs/design/`.

## Packet Contract

Every registered pass owns exactly these artifacts:

| Artifact | Location | Responsibility |
| --- | --- | --- |
| Research | `docs/research/<topic>.md` | Primary evidence, real uses, genuine forks, and rejected mechanisms |
| Design | `docs/design/<topic>.md` | Accepted target syntax, semantics, diagnostics, and boundaries |
| Target | `docs/design/<topic>_target.nomi` | Coherent positive examples plus clearly commented rejection cases |
| Bridge | `docs/review/<date>-<topic>.md` | Current implementation audit, ordered migration, risks, and retrospective |

The four artifacts link one another by repository-relative path. Broad target
files such as `syntax.md`, `semantics.md`, `decisions.md`, and the active
`targets/overall.nomi` / category suite
still receive the durable cross-language changes; a focused design file may
own detail that would make those spine documents unreadable.

## Lifecycle

Pass status is one of:

| Status | Meaning |
| --- | --- |
| `researching` | Evidence is being gathered around a bounded question. |
| `designing` | Credible candidates are being pressure-tested. |
| `design-accepted` | The target is coherent; implementation work remains. |
| `implementing` | Parser, IR, runtime, tooling, and fixtures are converging. |
| `validated` | Target behavior agrees across the declared conformance surfaces. |
| `paused` | Work is intentionally deferred with a named reason and next trigger. |
| `rejected` | The proposal failed its admission test; rationale remains discoverable. |

Status describes the whole packet, not whether one backend happens to parse a
spelling. Update `last_reviewed`, checks, and next actions whenever status moves.

## Pass Loop

1. **Discover.** Check the registry before creating notes. Resume an existing
   packet when its keywords and user pressure match.
2. **Research.** Start from a real program and use official specifications,
   primary papers, and current Nomi evidence. Record forks, not language tours.
3. **Decide.** Update canonical target docs and the decision ledger. State what
   is rejected as carefully as what is accepted.
4. **Pressure-test.** Put the choice in a focused target file and the broad
   whole-language target. Include formatting and diagnostic expectations.
5. **Bridge.** Audit every current frontend, IR, runtime, editor, test, and web
   surface that disagrees. Order migration by semantic dependency.
6. **Validate.** Run the commands registered with the pass. Target-only files
   stay outside `samples/` until all supported execution surfaces agree.
7. **Reflect.** Record what evidence changed the design, what slowed the pass,
   the smallest durable workflow improvement, and the exact next pass.

Run the deterministic surface with:

```bash
python3 -m tools.design_passes list
python3 -m tools.design_passes show pattern-matching
python3 -m tools.design_passes check
```

## Self-Improvement Rule

Each bridge note ends with a `Pass Retrospective` containing four headings:

- `Evidence That Changed The Design`
- `Workflow Friction`
- `Durable Improvement`
- `Next Pass`

The durable improvement must be a concrete edit to a check, skill, prompt,
registry field, fixture, or canonical document, or an explicit statement that
no process change was justified. This is evidence-driven self-improvement, not
automatic growth of instructions after every task.

Recurring friction should move inward:

```text
one-off observation -> bridge note
repeated reasoning need -> skill or prompt
deterministic invariant -> validator, hook, or test
source-discovery need -> RAG/MCP
target semantic decision -> docs/design
```

Delete or consolidate obsolete guidance when promoting a better workflow. The
system improves when agents need less rediscovery, not when context files only
become longer.

## Agent Routing

Session hooks show a bounded list of open passes. Prompt hooks match registry
keywords and inject the four relevant packet paths without that startup cap.
Agents still read the files before editing; injected paths are navigation, not
preloaded truth.

The `nomi-language-design` skill owns packet reasoning. The `nomi-ai-native`
skill owns the workflow machinery. Parser, interpreter, test, Rust/Wasm, and
web skills consume the bridge and conformance expectations when implementation
begins.

## Completion Gate

A pass is `validated` only when:

- canonical design and focused examples agree;
- accepted and rejected source fixtures exist;
- parse, typed Surface/Core, runtime result, diagnostic, and tooling contracts
  are explicit;
- supported CLI and browser paths agree or honestly reject the feature;
- registered validation commands pass;
- the bridge has no unnamed blocker and its retrospective is complete;
- remaining work is a new bounded pass rather than an unclosed part of this one.
