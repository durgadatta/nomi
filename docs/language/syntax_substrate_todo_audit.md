# Syntax Substrate TODO Audit

> Status: active critique and TODO index.
>
> Scope: parser, grammar, lowering, desugaring, interpreter boundaries,
> diagnostics, and syntax experimentation. This document collects the concrete
> changes that would make Nomi easier to evolve toward the target language
> tour.

## Purpose

Nomi's design ambition now reaches beyond small syntax conveniences. The
language wants data boundaries, constraints, result handling, table flow,
block policies, tests, explanation, scoped notation, and symbolic structure to
feel like one language. That requires a substrate where new syntax can be
added, inspected, revised, and removed without a tense cross-repo hunt.

This audit is deliberately critical. It is not saying the current prototype is
bad; it is naming where the prototype still makes language growth harder than
it needs to be.

Use this document together with:

- [Flexible Syntax Substrate Plan](flexible_syntax_substrate_plan.md)
- [Forward Implementation Plan](forward_implementation_plan.md)
- [Target Language Tour](target_language_tour.md)
- [Syntax Synthesis Matrix](../convenience/syntax_synthesis_matrix.md)

Inline code comments use stable IDs such as `NOMI-SUBSTRATE-001`. Keep those
IDs in sync with the table below.

## Summary Critique

The current pipeline is powerful enough to keep experimenting:

```text
Lark grammar layers
-> parse-tree transforms
-> NomiToPythonAST
-> Python AST desugars
-> layered interpreters
```

The main risk is not grammar expressiveness. The main risk is **diffusion of
responsibility**. A feature does not yet have one home. Adding syntax can
scatter into:

- `.lark` fragments;
- parse-tree transforms;
- transformer mixins;
- custom Python AST metadata;
- desugar passes;
- interpreter methods;
- reduced-interpreter guards;
- tests and snapshots;
- docs and target fixtures.

That scatter is survivable for isolated conveniences. It becomes dangerous for
the target language, where many features need to compose.

The desired shift:

```text
from "find every place this syntax must be wired"
to   "open one feature package and follow its declared lowering path"
```

## Central TODO Index

| ID | Theme | Status | Current pain | Desired change | Suggested first patch |
| --- | --- | --- | --- | --- | --- |
| NOMI-SUBSTRATE-001 | Feature manifest registry | ✅ done | ~~Core layers and transforms are hardcoded in `assemble.py`.~~ | Each syntax feature declares grammar, transforms, lowering, docs, tests, and status. | `SyntaxFeature` dataclass in `prototype/syntax/features.py`; `BUILTIN_FEATURES` drives layer order, transforms, lowering mixins, and desugar passes. |
| NOMI-SUBSTRATE-002 | Feature-set parser API | 🔵 deferred | `extra_layers` is useful but stringly and grammar-only. | `get_parser(features=[...])` should select feature manifests, not just raw layer files. | Keep current `extra_layers` cache key, then add `features` as a named higher-level API. |
| NOMI-SUBSTRATE-003 | Parse/lowering inspection | ✅ done | ~~Grammar changes lack a standard visible artifact.~~ | A CLI prints raw tree, transformed tree, surface AST, core AST, and Python AST. | `python3 -m tools.syntax.inspect --stage <stage> FILE` exists. |
| NOMI-SUBSTRATE-004 | Source spans | 🟡 partial | Tokens know positions, but lowered nodes usually forget them. | Every surface/core node carries `SourceSpan`; Python AST backend keeps a side table if needed. | `captures_span` decorator + `visit_wrapper` wired for `BlockCall`; enable parser positions with `NOMI_PARSER_SPANS=1` or `preserve_positions=True`. Apply to remaining surface-node-producing methods. |
| NOMI-SUBSTRATE-005 | Surface AST | 🟡 partial | Nomi syntax lowers directly into Python AST or custom attributes. | Add Nomi-owned surface nodes for syntax that Python AST cannot represent naturally. | `BlockCall` done with `lower_surface_to_python`; `PipeExpr`, `MatchExpr`, `BindingTarget`, `DataDecl` pending. |
| NOMI-SUBSTRATE-006 | Core AST | 🔵 deferred | "Normal form" exists mostly in docs. | Add a small core AST matching binding, function, pattern, flow, block, result, boundary, explanation. | Deferred until surface nodes settle. |
| NOMI-SUBSTRATE-007 | Python AST backend boundary | 🔵 deferred | Python AST is both IR and backend. | Keep Python AST as one backend while building a direct Nomi core interpreter over time. | Deferred until core AST exists. |
| NOMI-SUBSTRATE-008 | Declarative lowering passes | ✅ done | ~~`DESUGAR_PASSES` is ordered manually.~~ | Passes declare name, dependencies, input nodes, removed nodes, produced nodes, and normal forms. | `Phase`, `depends_on`, `input_node_types`, `removed_node_types`, `produced_node_types`, and `normal_forms` live on `BaseDesugarer`; pipeline is manifest-derived, phase-ordered, validated, and inspectable with `--stage passes` / `--stage expansions`. |
| NOMI-SUBSTRATE-009 | Lowering invariant checks | ✅ done | ~~Reduced interpreter guards only Python AST node types removed by desugars.~~ | Check that no forbidden surface/core nodes survive each lowering phase. | `_check_pass_invariants` in `pipeline.py` validates after each pass that `removed_node_types` nodes are absent; unit-tested. |
| NOMI-SUBSTRATE-010 | Block call representation | 🟡 partial | ~~Block bodies live inside `ast.keyword.value` as custom `Block` objects.~~ | Give block calls a Nomi-owned node, then lower to Python-compatible encoding. | `BlockCall` surface node exists with `lower()`; remaining: defer lowering until after desugar. |
| NOMI-SUBSTRATE-011 | Binding target model | ⬜ pending | Assignment, parameters, patterns, fields, and block params do not yet share one node model. | Create one `BindingTarget` and `Constraint` representation reused across all name-introduction sites. | Prototype for annotated assignment first, then parameters and patterns. |
| NOMI-SUBSTRATE-012 | Soft keyword policy | ⬜ pending | Soft keyword behavior exists in places, but the policy is not encoded. | Feature manifests declare soft keywords and ambiguity tests. | Add tests that future keywords still parse as names outside feature positions. |
| NOMI-SUBSTRATE-013 | Syntax islands | ⬜ pending | Future fenced notation must either fail parse or be implemented early. | Parse `quote:`, `use units:`, and future DSL regions as island nodes with raw text and spans. | Add one disabled/experimental island feature that parses but cannot run. |
| NOMI-SUBSTRATE-014 | Grammar conflict review | ⬜ pending | Lark can accept grammar growth that later becomes hard to reason about. | Feature tests include ambiguity/conflict fixtures and parse snapshots. | Add a `prototype/tests/unit/parser/snapshots/` harness for selected source snippets. |
| NOMI-SUBSTRATE-015 | Diagnostics contract | ⬜ pending | Parse/lowering errors often fall through as generic Python/Lark errors. | Each feature declares common mistakes and Nomi-worded diagnostic messages. | Start with pipeline stage errors, block-call body errors, and placeholder-scope errors. |
| NOMI-SUBSTRATE-016 | Target tour parsing mode | ⬜ pending | Aspirational examples cannot be partially parsed or inspected yet. | Syntax labs can parse target-tour subsets in explicit experimental modes. | Add `nomi --features data,block,trace --parse-only target.nomi`. |
| NOMI-SUBSTRATE-017 | Feature lifecycle statuses | ✅ done | ~~Docs have statuses, code does not.~~ | Code-level feature manifests use `implemented`, `prototype-ready`, `design-needed`, `research-only`, `rejected-for-now`. | `SyntaxFeature.status` with documented lifecycle states; used in `BUILTIN_FEATURES`. |
| NOMI-SUBSTRATE-018 | Grammar reference regeneration | ⬜ pending | `nomi.ref.lark` is documented as generated but lacks a first-class command. | One command regenerates/checks the reference grammar. | Add `python3 -m tools.syntax.grammar_ref --check`. |
| NOMI-SUBSTRATE-019 | Normal-form expansion view | 🟡 partial | ~~Users and agents cannot ask "what did this syntax become?"~~ | Tooling shows feature-by-feature expansion from surface to core. | `--stage expansions` shows pass-by-pass Python AST rewrites and normal forms; remaining: surface/core expansion with source provenance. |
| NOMI-SUBSTRATE-020 | Test template for syntax features | ⬜ pending | New syntax tests are easy to place inconsistently. | A feature template names parse, lower, diagnostic, runtime, docs, and fixture tests. | Add `prototype/syntax/features/_template/README.md`. |
| NOMI-SUBSTRATE-021 | Capability/spec matrix | 🟡 partial | ~~Feature state is scattered across docs, parser support, interpreter modes, tests, samples, and web/notebook surfaces.~~ | A single machine-readable matrix tells whether a feature is target-only, parse-only, lowerable, runnable, explainable, documented, and exposed in tools. | `FeatureCapabilityAxes`, `render_feature_capability_table()`, and `inspect(stage="capabilities")` expose a derived matrix. Remaining: explicit reduced-mode, samples, web, notebook, and spec-status axes. |
| NOMI-SUBSTRATE-022 | Experiment profiles | ⬜ pending | `extra_layers` can load grammar fragments, but there is no named profile such as default, lab, target-tour, or docs-only. | Syntax experiments run under explicit profiles without mutating the default parser. | Add profile names over feature sets after `features=[...]` exists. |
| NOMI-SUBSTRATE-023 | Declarative node and lowering schemas | ⬜ pending | Lowering logic is mostly handwritten transformer methods that directly emit Python AST. | Surface/core nodes and lowering passes declare their inputs, outputs, normal form, diagnostics, and examples. | Introduce schemas as metadata beside existing code before generating any behavior. |
| NOMI-SUBSTRATE-024 | Interpreter semantic registry | ⬜ pending | Runtime behavior is discovered from `eval_*` method names, which is convenient but does not expose feature ownership or trace events. | Interpreter handlers declare the semantic operation they implement, feature owner, accepted node kinds, resumable policy, and trace hooks. | Wrap the existing dispatch table with metadata while preserving method-name dispatch. |
| NOMI-SUBSTRATE-025 | Semantic event protocol | ⬜ pending | Diagnostics and future `explain` views need consistent events for binding, call, block, match, decode, pipeline, and rewrite. | Runtime and lowering can emit structured events independent of presentation. | Define event names and fields in docs first; implement as no-op hooks before feature-specific events. |
| NOMI-SUBSTRATE-026 | Feature-driven test matrix | ⬜ pending | Current tests cover interpreters well, but syntax-feature coverage is not declared in one place. | Feature manifests list parse, lower, diagnostic, runtime, regression, web, notebook, and docs checks. | Add pytest options later; first document the matrix and add TODOs at test collection seams. |
| NOMI-SUBSTRATE-027 | Playground feature toggles | ⬜ pending | The web playground runs the current default language, but future syntax labs need visible opt-in and lowering inspection. | Browser users can select a feature profile and inspect expansion without changing default semantics. | Reuse feature profiles once the parser API and inspection CLI exist. |
| NOMI-SUBSTRATE-028 | Agent workflow contract | ⬜ pending | Skills know current file paths but not the desired manifest/spec-driven workflow. | Agent skills require normal-form, status, docs, tests, and inspection decisions before implementation. | Update `.agents/skills/nomi-*` to treat feature manifests and substrate TODOs as the default path. |
| NOMI-SUBSTRATE-029 | Parser/cache identity | 🟡 partial | ~~Parser and raw-tree caches are not keyed by feature profile, grammar version, source path, or source version.~~ | Cache keys represent profile, feature set, grammar assembly, source identity, and position mode. | `ParserCacheKey` and `RawTreeCacheKey` now cover grammar layers, grammar version, feature profile placeholder, source identity, and position mode. Remaining: real feature-profile/source-version inputs for docs-only and target-tour parsing. |
| NOMI-SUBSTRATE-030 | Data declaration surface node | ⬜ pending | `data` lowers directly to `ClassDef` and ad hoc `TypeError` checks. | `DataDecl` is a Nomi-owned surface/core node that reuses binding targets, constraints, decode, diagnostics, and redaction. | Emit a passive `DataDecl` surface node for inspection before changing runtime behavior. |
| NOMI-SUBSTRATE-031 | Match expression surface node | ⬜ pending | Match expressions lower to IIFE-style Python AST, hiding return/scope/failure semantics. | `MatchExpr` records subject, cases, guards, pattern failures, and expression value semantics before backend lowering. | Emit `MatchExpr` as a surface node and keep existing IIFE lowering as the backend path. |
| NOMI-SUBSTRATE-032 | Postlexer contract and snapshots | 🟡 partial | ~~LALR disambiguation relies on Python postlexer scans and virtual tokens that are not declared as feature-owned artifacts.~~ | Every virtual token rewrite has fixture snapshots, owner metadata, and performance notes. | Token-stream contract tests now cover arrow params, sections, match case colons, guard `if`, block colons, postfix guards, and implicit multiplication. Remaining: owner metadata and performance budget coverage. |
| NOMI-SUBSTRATE-033 | Desugar pass profiles | 🟡 partial | ~~Default Nomi mode selects desugar passes by class-name allowlist.~~ | Feature manifests declare which passes run in default, reduced, lab, and docs-only profiles. | Done for default/reduced: `SyntaxFeature.desugar_profiles` derives `NOMI_INTERPRETER_DESUGAR_PASSES`, and runtime pass inspection shows the selected mode's pass set. Remaining: lab/docs-only profile integration. |
| NOMI-SUBSTRATE-034 | Core IR text/debug format | 🟡 partial | ~~Future Core IR is named in docs but has no inspectable artifact contract.~~ | Core IR has a stable textual/debug dump and verifier output before native backends exist. | `prototype/syntax/core.py`, `dump_core`, `verify_core`, and `inspect(stage="core")` exist for a tiny subset. Remaining: make Surface -> Core lowering authoritative instead of projecting backward from Python AST. |
| NOMI-SUBSTRATE-035 | Capability status axes | 🟡 partial | ~~`SyntaxFeature.status` is one coarse lifecycle label.~~ | Feature support is visible across parse, lower, run, reduce, explain, docs/spec, samples, web, and notebook axes. | Initial derived axes live in `FeatureCapabilityAxes`; remaining work is making non-derived axes explicit per feature. |

## Inline TODO Locations

Current inline comments have been placed at these high-leverage seams:

| ID | File | Why this location matters |
| --- | --- | --- |
| NOMI-SUBSTRATE-001 | `prototype/syntax/features.py` | ✅ Done — `BUILTIN_FEATURES` drives layers, transforms, mixins, desugar passes. |
| NOMI-SUBSTRATE-002 | `prototype/parser/nomi/usage.py` | Parser API still uses `extra_layers` stringly; feature-set API deferred. |
| NOMI-SUBSTRATE-003 | `tools/syntax/inspect.py` | ✅ Done — CLI with `--stage` for raw-tree, transformed-tree, surface-ast, python-ast. |
| NOMI-SUBSTRATE-004 | `prototype/syntax/surface.py`, `prototype/parser/nomi/lowering/block_call.py` | `captures_span` decorator + `visit_wrapper` wired for BlockCall; parser positions are opt-in with `NOMI_PARSER_SPANS=1` / `preserve_positions=True`. |
| NOMI-SUBSTRATE-005 | `prototype/parser/nomi/ast_.py`, `prototype/syntax/surface.py` | `BlockCall` + `lower_surface_to_python` done; PipeExpr, MatchExpr, BindingTarget, DataDecl pending. |
| NOMI-SUBSTRATE-008 | `prototype/parser/nomi/desugar/base.py`, `pipeline.py` | ✅ Done — `Phase`, dependencies, input/removed/produced node types, and normal forms on `BaseDesugarer`; pipeline auto-derived, phase-ordered, validated, and inspectable. |
| NOMI-SUBSTRATE-010 | `prototype/parser/nomi/desugar/base.py`, `prototype/parser/nomi/lowering/block_call.py` | `BlockCall` surface node exists; remaining: defer lowering until after desugar. |
| NOMI-SUBSTRATE-011 | `prototype/interpreter/nomi/binding.py` | Constraint handling is centered on `AnnAssign`; needs shared `BindingTarget` for parameters, fields, captures, imports, and block params. |
| NOMI-SUBSTRATE-012 | `prototype/grammar/layers/statements.lark` | New keywords should remain soft until proven otherwise. |
| NOMI-SUBSTRATE-013 | `prototype/grammar/layers/expressions.lark` | Future fenced expressions need a safe parser holding zone. |
| NOMI-SUBSTRATE-019 | `prototype/interpreter/reduced/interpreter.py` | Reduced interpreter guardrails should evolve into full normal-form checks. |
| NOMI-SUBSTRATE-023 | `prototype/parser/nomi/functions.py` | Transformer methods should gradually become feature-owned lowering declarations instead of direct Python AST factories. |
| NOMI-SUBSTRATE-024 | `prototype/interpreter/python/interpreter.py` | `eval_*` dispatch should grow semantic metadata without losing its simple method dispatch. |
| NOMI-SUBSTRATE-026 | `prototype/tests/conftest.py` | Interpreter-mode parametrization should eventually compose with feature-profile parametrization. |
| NOMI-SUBSTRATE-029 | `prototype/parser/nomi/usage.py` | Parser/raw-tree caches must grow full profile/source/grammar identity before docs-only or target-tour parsing. |
| NOMI-SUBSTRATE-030 | `prototype/parser/nomi/lowering/data_decl.py` | Data declarations need a surface node and shared binding/diagnostic/decode semantics. |
| NOMI-SUBSTRATE-031 | `prototype/parser/nomi/lowering/match_expr.py` | Match expressions need surface/core representation before richer diagnostics and control semantics. |
| NOMI-SUBSTRATE-032 | `prototype/parser/nomi/postlexer.py` | Postlexer rewrites need fixture snapshots, feature ownership, and performance budget coverage. |
| NOMI-SUBSTRATE-033 | `prototype/parser/nomi/desugar/pipeline.py`, `prototype/syntax/features.py`, `prototype/runtime/api.py` | Default/reduced pass selection and inspection are manifest metadata; lab/docs-only profile integration remains. |
| NOMI-SUBSTRATE-034 | `prototype/syntax/surface.py`, `prototype/syntax/core.py` | Surface nodes need an authoritative Core IR destination before MLIR, LLVM, or Wasm backends become meaningful. |
| NOMI-SUBSTRATE-035 | `prototype/syntax/features.py` | A single lifecycle status should not overstate parse/lower/run/reduce/explain/docs/tooling coverage. |

Add new inline TODOs only when they point to a real architectural seam. Avoid
sprinkling IDs everywhere.

## Detailed Critique

### 1. Grammar Layers Are Useful But Not Yet Feature-Owned

The layer files are a good start because they group terminals, expressions,
statements, patterns, bindings, and calls. But source-language features do not
map perfectly to those layers. For example, `data` will need statement grammar,
field binding grammar, constraints, decode behavior, diagnostics, samples, and
docs. Splitting that across current layers is fine internally, but the feature
needs one owner.

Caveat: do not overbuild a plugin system. Start with static manifests for
built-in features. Dynamic loading can wait.

### 2. Python AST Is A Great Bootstrap And A Poor Long-Term Center

Python AST gives Nomi quick parity and a working interpreter path. But syntax
like block policies, match expressions, constrained binding, data fields, and
trace/explain do not naturally fit Python AST. The current workaround pattern
is either IIFEs or metadata/custom objects attached to Python nodes.

That is acceptable during bootstrap, but it is a warning sign. Nomi should not
ask every future feature to pretend it is Python syntax before it can be
reasoned about.

Caveat: do not rip Python AST out wholesale. Create Nomi surface/core nodes for
new or awkward features first, then keep lowering to Python AST as a backend.

### 3. Diagnostics Need Source Spans Before They Need Fancy Formatting

The target language depends on excellent diagnostics. That does not begin with
beautiful error messages; it begins with source spans surviving every parse and
lowering step.

The first win is modest:

```text
node.span -> file, start line/column, end line/column
```

Even if only a few node types get spans at first, it changes the architecture
from "diagnostics someday" to "diagnostics have a place to attach."

Caveat: Python AST has `lineno`/`col_offset`, but those are not enough for
multi-token Nomi constructs such as block calls, where clauses, and future
fenced syntax.

### 4. Desugar Passes Should Become Contracts

The current `DESUGAR_PASSES` list is readable, but it does not state why the
order is correct, which nodes each pass expects, or which normal forms it
produces. As features grow, pass ordering becomes hidden language semantics.

The pass manager should eventually be able to answer:

```text
What nodes can enter this pass?
What nodes can leave it?
Which normal form does it produce?
Which later passes depend on it?
What should never reach runtime?
```

Caveat: do this by wrapping existing passes in metadata first. Do not rewrite
all desugars at the same time.

### 5. Syntax Experiments Need Parse-Only Lifecycles

The target language tour intentionally contains future forms. The project
needs a way to parse and inspect these without pretending runtime support
exists. Feature lifecycle should be explicit:

```text
research-only: docs and maybe syntax island
design-needed: parse-only experiment, no runtime
prototype-ready: parse + lower + diagnostics, maybe partial runtime
implemented: default parser and tests
```

Caveat: parse-only syntax can be dangerous if users mistake it for supported
behavior. Keep it behind explicit feature flags and clear diagnostics.

### 6. Normal Forms Should Become Executable

The docs say every convenience should reduce to binding, function, pattern,
flow, block, absence/result, data boundary, or explanation. That is the right
doctrine. The implementation should make it concrete.

Eventually, adding syntax should require declaring:

```text
normal_forms = ["flow", "function"]
```

and supplying a lowering that proves it.

Caveat: the normal-form set may evolve. Feature manifests should allow a
feature to propose a new primitive, but make that rare and review-heavy.

## Suggested Work Packages

### Package 1: Inspection And Snapshots

Goal: make parser changes visible.

Tasks:

- Add `tools.syntax.inspect`.
- Print raw Lark tree and transformed Lark tree.
- Print current Python AST.
- Add one snapshot fixture for pipeline, match, where, block call, and
  underscore lambda.
- Add `--check` mode later.

Risks:

- Snapshots can become noisy. Keep them small and representative.

### Package 2: Feature Manifest Skeleton

Goal: give syntax features one home before moving behavior.

Tasks:

- Add `prototype/syntax/feature.py`.
- Define feature status enum.
- Define grammar fragment, transforms, lower passes, docs, and test pointers.
- Register current core grammar as one built-in feature group.
- Keep existing layer files where they are until migration is useful.

Risks:

- Too much abstraction too early. Keep the manifest passive at first.

### Package 3: Source Span Prototype

Goal: prove diagnostics can point to Nomi source.

Tasks:

- Add `SourceSpan`.
- Preserve spans for function definitions, assignments, calls, match cases,
  and block calls.
- Add tests for span shape, not exact formatting.
- Show spans in inspection CLI.

Risks:

- Lark tree/token span handling may be uneven around indentation and synthetic
  nodes. Accept partial coverage first.

### Package 4: BlockCall Surface Node

Goal: stop making the most Nomi-specific control form hide inside Python AST
keywords.

Tasks:

- Add `BlockCall` surface node.
- Change block-call lowering to produce `BlockCall`.
- Add a backend lowering pass from `BlockCall` to today's `Block` keyword
  representation.
- Keep interpreter behavior unchanged.
- Add snapshot tests for the surface node and backend lowering.

Risks:

- Resumable control is delicate. Do not change runtime semantics in the first
  patch.

### Package 5: Declarative Desugar Metadata

Goal: make pass ordering and guarantees explicit.

Tasks:

- [x] Add pass metadata on `BaseDesugarer`.
- [x] Wrap existing `DESUGAR_PASSES`.
- [x] Print pass list from inspection CLI.
- [x] Check `removed_node_types` after passes.
- [x] Add dependencies and phase ordering.
- [x] Add produced-node and normal-form metadata.
- [x] Add expected-input metadata.
- [x] Add before/after expansion snapshots.

Risks:

- Topological sorting is unnecessary at first. Manual order plus metadata is
  enough for the first iteration.

### Package 6: Syntax Labs

Goal: safely parse future ideas.

Tasks:

- Add feature-set parser API.
- Add `--features` to CLI parse/inspect commands.
- Add parse-only diagnostics for unsupported features.
- Parse one future feature as a syntax island.

Risks:

- Feature flags can fragment expectations. Keep labs out of default examples.

## Caveats

- A flexible substrate is not a license to add incoherent syntax. It makes
  coherence easier to test.
- The grammar should remain readable. Feature manifests should organize it,
  not hide it behind generated complexity.
- The target is not "plugins everywhere." The target is local ownership,
  inspectable lowering, and reversible experiments.
- Python parity still matters. A Nomi-owned AST should preserve Python-like
  behavior where Nomi intentionally follows Python.
- Some syntax work should remain docs-only until diagnostics and normal-form
  reductions are clear.

## Maintenance Rules

- When adding an inline `NOMI-SUBSTRATE-*` comment, add or update its row here.
- When completing a TODO, keep the row but mark it as done in a short note
  until a later cleanup pass removes or archives it.
- When a new syntax feature is proposed, list which TODOs it depends on.
- When target-tour syntax changes, ask whether the substrate needs a new TODO.
- When implementation diverges from this audit, update the audit rather than
  letting it become stale.
