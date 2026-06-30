# Competitive Language Research Plan 2026-06-30

> Status: active research plan; source material for future language, feature,
> convenience, and implementation docs.
>
> Scope: documentation-only. This file plans the next intense research and
> consolidation phase for making Nomi a serious high-level programming
> language competitor. It is not a language specification and does not promote
> syntax by itself.

## Purpose

Nomi should be judged against serious languages and systems, not against a toy
prototype. The ambition is to become a credible everyday high-level language
for people who might otherwise reach for Python, Julia, Ruby, Mathematica,
Scheme/Racket, R, JavaScript/TypeScript, or domain tools such as SQL, shell,
notebooks, and configuration languages.

The goal is not to imitate those systems. The goal is to understand why people
choose them, where they fail, and which durable needs Nomi can satisfy through
its own normal forms:

```text
binding -> function -> pattern -> flow -> block -> absence/result
-> data boundary -> explanation
```

This research phase should produce sharper design gates, not a larger
catalogue. Every finding should eventually answer:

```text
What user job is at stake?
Which competing system handles it well?
What does that system make hard?
Which Nomi normal form owns the need?
What should Nomi adopt, adapt, refuse, or defer?
What feature packet, target fixture, sample, test, or implementation slice
would prove it?
```

For the current consolidation of integration boundaries, syntax variants,
tradeoffs, and target examples, see
[`cognitive_integration_boundary_plan.md`](../language/cognitive_integration_boundary_plan.md).
The first focused integration artifact from that plan is
[`binding_data_pattern_integration_feature.md`](../features/binding_data_pattern_integration_feature.md).

## Competitive Thesis

Nomi's plausible competitive position is:

```text
Python's approachability and ecosystem bridge
+ Julia's mathematical and scientific fluency
+ Ruby's humane blocks and library-authored control
+ Mathematica's symbolic and whole-expression power
+ Scheme/Racket's small-core discipline and language-building clarity
+ SQL/R/APL's whole-data transformation instincts
+ Rust/Gleam-style failure clarity
+ CUE/Pydantic-style boundary confidence
+ Racket/Darklang/Elm-style explanation pressure
= one coherent everyday language with inspectable reductions
```

That formula is intentionally demanding. Nomi should not become a feature
buffet. A feature is competitive only if it improves the small-script to
checked-data to readable-transformation to explainable-result path without
forcing a second mental model.

## Competitor Benchmark Matrix

Use this matrix to organize the next research passes. Each row should turn into
one focused pass with examples, refusal rules, and Nomi design consequences.

| Competitor surface | What users choose it for | Nomi must learn | Nomi must refuse |
| --- | --- | --- | --- |
| Python | Readability, batteries, notebooks, scripting, interop, ecosystem reach | First-hour success, boring stdlib, Python migration bridge, clear dynamic ergonomics | Ambient dynamic failure, vague data boundaries, stringly config, slow hidden paths as semantics |
| Julia | Scientific computing, multiple dispatch, broadcasting, composable math, notebooks | Whole-array thinking, mathematical syntax discipline, generic functions as design pressure | Performance-first complexity in the daily layer, dispatch as hidden control, too many local spellings |
| Ruby | Blocks, humane DSLs, expressive libraries, readable internal APIs | Block policies, caller-side code attached to calls, library-authored control with good taste | Global monkeypatching, implicit receivers, magical DSLs that tools cannot expand |
| Mathematica | Symbolic expressions, rewrite rules, notebooks, pattern-driven transformation | Explicit quote/rewrite layer, whole-expression manipulation, explainable transformation traces | Implicit symbolic evaluation in ordinary code, dense special cases, hidden evaluation order |
| Scheme/Racket | Small core, macros, teaching languages, contracts, language-oriented programming | Minimal semantic core, explicit expansion, contracts as explanation, language-building discipline | Unfenced macros, syntax that ordinary users cannot locally reason about |
| R | Data frames, formulas, vectorization, notebooks, statistics workflows | Data masks as scoped contexts, table verbs, formula-like boundary surfaces, rich display | Non-standard evaluation without inspectable context, partial recycling, silent missingness |
| SQL/LINQ/Polars | Query plans, grouping, joins, backend execution, explain plans | Collection/table vocabulary, plan values, backend capability honesty | A second query language disconnected from ordinary flow and binding |
| Shell/PowerShell/Nushell | Process orchestration, pipelines, files, commands, structured output | Command values, previews, subprocess results, capability boundaries | Raw string streams as the language core, unsafe shell interpolation |
| TypeScript/Kotlin/Swift/C# | Mainstream safety, null handling, records, pattern growth, async ecosystems | Gradual safety lessons, absence clarity, records/data ergonomics, editor expectations | Feature-menu accumulation and duplicated local conveniences |
| Rust/Gleam/Zig/Go | Failure discipline, resource cleanup, simple deployment, explicitness | Result values, block cleanup policies, capability honesty, deployment seriousness | Systems-language ownership syntax in first-hour Nomi |

## Research Streams

### Stream 1: Everyday Python-Competitive Core

Question:

```text
What makes a Python programmer try Nomi for a real script in one sitting?
```

Read first:

- `docs/research/first_hour_pedagogy_deep_dive.md`
- `docs/research/standard_library_design_comparative.md`
- `docs/research/package_docs_and_examples_deep_dive.md`
- `docs/language/first_hour_nomi.md`
- `docs/language/prelude_and_standard_library_plan.md`
- `docs/language/delta_on_python.md`

Outputs:

- A first-hour rewrite pass for `first_hour_nomi.md`.
- A Python migration and interop note that distinguishes preserved Python
  shape from deliberate Nomi departures.
- A boring-task fixture set: files, paths, JSON, CSV, CLI args, env vars,
  HTTP, subprocesses, time, tests.

Admission gate:

- The first-hour path must be runnable or clearly marked target-only.
- Each improvement must reduce to binding, function, flow, data boundary,
  result, or explanation.

### Stream 2: Scientific, Array, Table, And Notebook Power

Question:

```text
How can Nomi compete with Julia, R, MATLAB, Mathematica, SQL, and Polars
without becoming dense or domain-fragmented?
```

Read first:

- `docs/research/scientific_languages_r_matlab_julia.md`
- `docs/research/array_languages_deep_dive.md`
- `docs/research/table_and_flow_systems_deep_dive.md`
- `docs/research/interactive_explanation_deep_dive.md`
- `docs/features/structured_collections_query_language.md`
- `docs/convenience/flow_and_collections.md`

Outputs:

- A collection/table vocabulary packet for `where`, `select`, `derive`,
  `group`, `join`, `sort`, `window`, `fold`, `collect`, and plan values.
- A notebook/data fixture ladder that starts with lists and records before
  tables, lazy plans, broadcasting, or rank.
- A refusal table for dense array glyphs, implicit vector recycling, and
  hidden dataframe scoping.

Admission gate:

- Query and table work must reduce to ordinary flow, binding, pattern, and
  explanation events.
- Whole-array and symbolic ideas stay library-first or future-layer until
  diagnostics can show shape, rank, plan, and source paths.

### Stream 3: Blocks, Policies, Resources, And Humane Control

Question:

```text
Can Nomi get Ruby-level block expressiveness with Python-level readability and
Rust/Zig-level cleanup honesty?
```

Read first:

- `docs/features/block_calls_feature.md`
- `docs/research/error_handling_defer_resource_cleanup_notes.md`
- `docs/research/beam_languages_erlang_elixir_gleam.md`
- `docs/features/state_and_capability_model.md`
- `docs/convenience/concurrency.md`

Outputs:

- A block policy prelude packet: `using`, `retry`, `transaction`, `trace`,
  `test`, and later structured concurrency.
- A resource/capability diagnostic table: enter, yield, resume, cleanup,
  cancel, escape, deny.
- A design decision on which cleanup forms are syntax, block policies, or
  library functions.

Admission gate:

- Blocks remain caller-side code attached to calls.
- Cleanup, retry, cancellation, and capability denial must produce semantic
  events before broad syntax promotion.

### Stream 4: Symbolic, Reflective, And Language-Building Power

Question:

```text
How can Nomi learn from Mathematica, Lisp, Scheme, Racket, Julia macros, R
formulas, and e-graphs while keeping ordinary code locally readable?
```

Read first:

- `docs/research/research_notes_synthesis.md`
- `docs/features/symbolic_structural_computation.md`
- `docs/research/array_languages_deep_dive.md`
- `docs/research/ai_readable_semantics_deep_dive.md`
- `docs/convenience/meta_testing.md`
- `docs/language/language_degrees_of_freedom.md`

Outputs:

- A quote/syntax-values feature packet.
- A rewrite/unification strategy note that separates pattern matching,
  unification, rewriting, normalization, and explanation.
- A scoped-notation refusal/admission guide.

Admission gate:

- Ordinary code must not become implicitly symbolic.
- Expansion, rewrite, and notation must be fenced, source-spanned, and
  inspectable.

### Stream 5: Explanation, Diagnostics, And AI-Readable Semantics

Question:

```text
Can Nomi make explainability a language feature rather than an IDE afterthought?
```

Read first:

- `docs/features/explanation_trace_feature.md`
- `docs/research/diagnostics_and_explanations_comparative.md`
- `docs/research/interactive_explanation_deep_dive.md`
- `docs/research/ai_readable_semantics_deep_dive.md`
- `docs/research/human_computer_interface_languages_deep_dive.md`
- `docs/language/current_capability_matrix.md`

Outputs:

- A semantic event producer map for binding, decode, match, pipeline, block,
  query, examples, capability, and rewrite.
- An explain output shape for terminal, notebook, web, docs, tests, and agents.
- Accessibility and localization notes for diagnostics.

Admission gate:

- Every major feature packet must answer: what happened, where, what value,
  what rule, what next step, and what is redacted.

### Stream 6: Adoption Infrastructure As Language Design

Question:

```text
What boring infrastructure must exist before Nomi can credibly compete with
Python, Julia, Ruby, and Racket?
```

Read first:

- `docs/research/formatting_and_style_deep_dive.md`
- `docs/research/packaging_and_project_structure_deep_dive.md`
- `docs/research/deployment_and_operations_deep_dive.md`
- `docs/research/security_and_trust_deep_dive.md`
- `docs/language/stdlib_capability_baseline.md`
- `docs/language/modern_language_implementation_artifacts.md`

Outputs:

- A style/formatter doctrine with no-config canonical formatting.
- A package/project manifest note with integrity, examples, docs, tests,
  capability declarations, and Python interop boundaries.
- A deployment and trust checklist for local scripts, notebooks, web,
  packages, and future Wasm/WASI targets.

Admission gate:

- Tooling claims must be backed by generated artifacts, checks, or explicit
  target-only labels.

## Consolidation Method

Each stream should run in four passes:

1. **Evidence pass:** read existing deep dives and note only durable lessons,
   not catalog entries.
2. **Normal-form pass:** map each lesson to binding, function, pattern, flow,
   block, absence/result, data boundary, or explanation.
3. **Competitive gate pass:** compare Nomi against the target competitor for
   the user job. Record what Nomi must beat, match, or explicitly refuse.
4. **Artifact pass:** update exactly one of: feature packet, convenience doc,
   language spec section, target fixture, implementation todo, or sample/test
   gate.

Do not leave conclusions only in this research plan. This file is the campaign
map. Durable decisions belong in active language, feature, convenience, or
implementation docs.

## Initial Consolidation Notes

These are the immediate design notes this plan should preserve:

| Pressure | Consolidated note | Likely home |
| --- | --- | --- |
| Python competitiveness | Nomi needs boring-task confidence before exotic syntax. | `first_hour_nomi.md`, `prelude_and_standard_library_plan.md`, `delta_on_python.md` |
| CUE/Pydantic/Elm decoder competitiveness | External data should become owned program values through one binding, constraint, decode, and explanation story. | `binding_data_pattern_integration_feature.md`, `data_decode_boundary_feature.md`, `binding_constraints_feature.md` |
| Julia/R/Mathematica competitiveness | Whole-data and symbolic power must be designed as flow, plan, rank/shape, quote, rewrite, and explanation, not patched onto scalar Python. | `structured_collections_query_language.md`, `symbolic_structural_computation.md` |
| Ruby competitiveness | Block calls are a major differentiator, but only if policies are inspectable and not magical DSLs. | `block_calls_feature.md`, `state_and_capability_model.md` |
| Scheme/Racket competitiveness | Small-core clarity matters more than macro power. Expansion must be visible and fenced. | `language_foundation.md`, future quote/syntax packet |
| SQL/Polars competitiveness | Query syntax should wait for stable verbs and plan values. | collection/table vocabulary packet |
| AI-era competitiveness | Source-to-meaning and semantic events are product features. | `explanation_trace_feature.md`, `current_capability_matrix.md` |

## Near-Term Commit Sequence

1. Commit this research plan and index updates.
2. Write a competitive first-hour/Python-bridge pass.
3. Write the binding/data/pattern integration packet.
   (Done:
   [`binding_data_pattern_integration_feature.md`](../features/binding_data_pattern_integration_feature.md).)
4. Write the collection/table vocabulary packet.
5. Write the block policy prelude packet.
6. Write the quote/syntax-values and rewrite boundary plan.
7. Write the semantic event producer map.
8. Refresh target fixtures and `demo_target.nomi` only after the design
   surfaces above agree.

## Stop Rules

- Stop adding research when a stream repeats existing deep-dive conclusions
  without producing a new decision, fixture, or feature packet.
- Stop adding syntax when a library function, data value, block policy, or
  scoped extension would prove the user need first.
- Stop comparing Nomi to a competitor when the comparison becomes brand
  admiration instead of user-job analysis.
- Stop before implementation when the feature owner, normal form, diagnostics,
  capability axes, and test/sample gate are not visible.
