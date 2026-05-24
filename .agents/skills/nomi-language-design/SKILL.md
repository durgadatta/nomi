---
name: nomi-language-design
description: Refine Nomi language design and syntax by researching other languages, grouping similar features, extracting user needs, reducing candidates to Nomi normal forms, and updating docs. Use for convenience-syntax research, philosophical design synthesis, feature admission decisions, and recommendations for how Nomi should combine ideas from other languages.
compatibility: codex, opencode, deepseek-tui, claude-code
---

# Nomi Language Design

Use this skill when the task is about Nomi's language direction, syntax
research, convenience features, design philosophy, or translating ideas from
other languages into a coherent Nomi surface.

Nomi is fast-evolving and exploratory. Treat existing docs, tests, parser
behavior, and prototype mechanics as design evidence, not immutable law. The
goal is to follow the idea and spirit of Nomi: small semantic primitives,
readable expression, explicit boundaries, inspectable reductions, and
reversible implementation. If the current repo snapshot conflicts with that
direction, name the drift and update the status/doc/skill instead of rigidly
aligning new work to stale artifacts.

For core/sugar/backend separation work, use
`docs/language/core_layer_separation_plan.md` as the operational layer map:
L0 runtime substrate, L1 implementation core IR, L2 semantic core, L3
canonical surface, L4 sugar reductions, L5 library conventions, L6 scoped
extensions, and L7 backend targets. The most important implementation rule is:
L4 sugar should reduce before eval; do not grant sugar permanent evaluator
semantics.

## Research Corpus (May 2026)

The project has a substantial cross-language research corpus — 23 deep-dive
files surveying 60+ languages and systems across 16 language families and 8
cross-cutting dimensions. Before doing new research, check whether the question
is already answered here.

**Navigation entry points:**

- `docs/research/language_family_coverage_map.md` — the index of indices. Use
  this FIRST when starting any research task. It contains: the coverage table
  (16 families with lessons, Nomi use, caveats), the deep dive index (23 files
  with line counts), and coverage priorities (what's done, what's next).
- `docs/research/cross_language_synthesis_master.md` — the capstone synthesis.
  8 universal convergences, 8 genuine design forks, 7 hidden incompatibilities,
  8 Nomi synthesis sections (one per normal form), 23-row Design Decision
  Record table, 5 structural risks, 7 open questions. Read this when making a
  cross-cutting design decision.
- `docs/research/research_notes_synthesis.md` — earlier synthesis with
  progressive-reification spine, major research pressures, design tensions, and
  the guardrail against rabbit holes.

**Deep dives by domain** (each ~800-2200 lines, comparative, with
Adopt/Refuse/Adapt tables):

| Domain | File | Systems surveyed |
|--------|------|------------------|
| Pattern matching | `pattern_matching_synthesis.md` | Rust, Swift, Kotlin, Scala 3, OCaml, Haskell, F#, Elixir, Gleam, Racket |
| Error/defer/resource | `error_handling_defer_resource_cleanup_notes.md` | Zig, Hylo, Odin, Gleam, Roc, Swift, Kotlin, Scala, Java, Python, C++, Haskell |
| Diagnostics | `diagnostics_and_explanations_comparative.md` | Rust, Elm, Racket, Swift, Scala 3, Clojure, Zig, TypeScript, Gleam, Python |
| Stdlib design | `standard_library_design_comparative.md` | Go, Rust, Python, Kotlin, Swift, Elixir, Zig, C#, Haskell, Racket |
| Type systems | `typescript_type_system_deep_dive.md` | TypeScript (narrowing, structural typing, conditional types, `satisfies`) |
| Go philosophy | `go_design_philosophy_deep_dive.md` | Go (simplicity, interfaces, goroutines, defer, zero values) |
| C#/Java/Dart | `csharp_java_dart_modern_features.md` | C#, Java, Dart (records, pattern matching, null safety, async) |
| BEAM platform | `beam_languages_erlang_elixir_gleam.md` | Erlang, Elixir, Gleam (OTP, supervisors, pipe, `use`) |
| Array languages | `array_languages_deep_dive.md` | APL, J, K, Q, BQN, Uiua (rank polymorphism, trains, combinators) |
| Concatenative | `concatenative_languages.md` | Forth, Factor, Joy, Kitten, Cat (stack effects, combinators) |
| Scientific | `scientific_languages_r_matlab_julia.md` | R, MATLAB, Julia (formulas, tidy eval, broadcasting) |
| Modern languages | `modern_language_feature_survey.md` | Mojo, Gleam, Roc, Hylo, Odin, Darklang, Verse, Koka, Unison |
| First-hour pedagogy | `first_hour_pedagogy_deep_dive.md` | Python, Go, Dart, Racket, Scratch, Logo, BASIC, Elm, Khan Academy, Swift Playgrounds |
| Packaging | `packaging_and_project_structure_deep_dive.md` | Python, Cargo, Go modules, Mix, npm, NuGet, Nix flakes, Maven |
| Data boundaries | `data_boundary_systems_deep_dive.md` | Pydantic, CUE, Nickel, Pkl, Dhall, Terraform, JSON Schema, TypeScript, serde, Elm decoders |
| Table/flow | `table_and_flow_systems_deep_dive.md` | SQL, LINQ, dplyr, Polars, DuckDB, Nushell, pandas, K/Q |
| Interactive | `interactive_explanation_deep_dive.md` | Jupyter, Pluto, Darklang, Smalltalk, Racket, Light Table, Observable, Swift Playgrounds, Bret Victor, Elm debugger |
| Formatting | `formatting_and_style_deep_dive.md` | gofmt, Black, Rustfmt, Prettier, elm-format, clang-format, Ormolu, dart format, zig fmt, ocamlformat |
| Package docs | `package_docs_and_examples_deep_dive.md` | Rustdoc, ExDoc, Julia, Sphinx, Scribble, Go, Javadoc, TypeDoc, Literate Programming, Diataxis |
| Deployment | `deployment_and_operations_deep_dive.md` | Go, Python, Node/Deno/Bun, Docker, Serverless, Rust, Java/JVM, Nix/NixOS, Wasm, Homebrew |
| Security | `security_and_trust_deep_dive.md` | Nix, capabilities, secrets, supply-chain, sandboxing, memory safety, IFC, crypto hygiene, auth, redaction |
| AI toolability | `ai_readable_semantics_deep_dive.md` | LSP, typed ASTs, Tree-sitter, semantic tokens, code actions, proof traces, design fixtures, notebooks, expansion display |

**How to use the research corpus:**

1. Start every research task by reading `language_family_coverage_map.md` to
   see if the topic is already covered and which deep dive covers it.
2. If a deep dive exists, read it before proposing new syntax. The
   Adopt/Refuse/Adapt tables already encode synthesis decisions.
3. If the topic is new, use the deep dive format: Status/Purpose, system
   surveys with philosophy/what-worked/what-failed/insight, cross-language
   synthesis (invariants, forks, anti-patterns), Nomi Adopt/Refuse/Adapt table.
4. After writing a new deep dive, update both index files:
   `language_family_coverage_map.md` (deep dive index + coverage priorities)
   and `research_notes_synthesis.md` (deep dive index section).
5. Stable Adopt decisions from deep dives should eventually migrate to
   `docs/convenience/` as design specs and to `docs/language/` as feature docs.
   Research files are source material, not active specification.

## Core Rule

Do not copy syntax because it is attractive elsewhere. Extract the durable user
need, compare close relatives, reduce the idea to a Nomi normal form, then
recommend one coherent spelling.

Also do not copy Nomi's current prototype shape merely because it exists. The
current implementation is a laboratory snapshot; the design target is the
coherent language it is helping reveal. Use current behavior to find
constraints, regressions, and examples, then decide whether it represents
active direction, bootstrap residue, or stale documentation.

```text
source language -> user need -> semantic difference -> Nomi normal form -> surface syntax
```

Never:

```text
source language -> copied syntax -> explanation after the fact
```

## Start Here

Read the smallest relevant set before changing docs or making recommendations.

**Foundation and direction:**
- `docs/language/language_foundation.md` — canonical design foundation.
- `docs/orientation/exploratory_implementation_doctrine.md` — implementation
  doctrine for keeping early language work flexible, declarative, and
  reversible.
- `docs/language/core_layer_separation_plan.md` — operational hierarchy for
  implementation core, semantic core, canonical surface, sugar, libraries,
  scoped extensions, eval separation, and backend targets.
- `docs/language/spec_readiness_map.md` — promotion workflow for turning
  research, convenience notes, feature docs, target fixtures, and
  implementation plans into spec-ready language sections.
- `docs/language/language_direction_and_gap_map.md` — adoption-oriented gaps
  and next design artifacts.
- `docs/language/docs_eagle_eye_review.md` — active distilled scan for hidden
  bridge gaps, obsolete/source-only lanes, and planning priorities.
- `docs/language/language_degrees_of_freedom.md` — strict core vs sugar,
  library-first, scoped extension, future layer, rejection framework.
- `docs/language/language_design_dimensions.md` — irreducible axes of
  variation and where languages converge.

**Specification and planning:**
- `docs/language/language_spec.md` — draft concrete language specification.
- `docs/language/forward_implementation_plan.md` — staged implementation plan
  with gates, caveats, risks, open questions.
- `docs/language/implementation_todos.md` — staged design and implementation
  tasks.
- `docs/language/target_program_fixtures.md` — aspirational everyday programs
  for testing design coherence.
- `docs/language/demo_target.nomi` — compact target-only script showing the
  desired future language across ordinary cases. It is not expected to parse
  today and must stay outside `samples/` until implemented and tested.
- `docs/language/target_language_tour.md` — aspirational Nomi program showing
  preferred syntax composing into one memorable whole.

**Convenience docs (normal-form design):**
- `docs/convenience/review_and_roadmap.md` — normal forms and feature status.
- `docs/convenience/design_lessons_and_integration.md` — design synthesis,
  systemic cruft patterns, feature interaction analysis.
- `docs/convenience/absence_and_result.md` — absence, result, error handling.
- `docs/convenience/flow_and_collections.md` — flow normal form.
- `docs/convenience/data_and_types.md` — data boundary, types, aliases.
- `docs/convenience/strings.md` — string pillar: interpolation, literals, typed
  wrappers, pattern matching on strings, Unicode, serialization, security.
- `docs/convenience/syntax_synthesis_matrix.md` — cross-language feature
  families and recommendations.
- Relevant focused docs under `docs/convenience/` (e.g., `patterns.md`,
  `functions.md`, `error_handling.md`, `null_handling.md`, `types.md`).

**Feature pillars:**
- `docs/features/binding_constraints_feature.md` — constrained binding.
- `docs/features/block_calls_feature.md` — yield-to-block and block-call design.
- `docs/features/structured_collections_query_language.md` — query/table verbs.

**Architecture and substrate:**
- `docs/language/adversarial_exploratory_implementation_critique.md` — hostile
  reading of how implementation convenience can prematurely freeze language
  design.
- `docs/language/core_layer_separation_plan.md` — read first when the task
  touches core-vs-sugar boundaries, eval dispatch, Core IR, reduced mode,
  feature layer metadata, or backend portability.
- `docs/language/architecture_refactoring_plan.md` — runtime API, pipeline,
  package, host, and frontend adapter refactoring.
- `docs/language/flexible_syntax_substrate_plan.md` — parser, grammar,
  lowering, and interpreter architecture.
- `docs/language/syntax_substrate_todo_audit.md` — central critique and TODO
  index for parser/grammar/lowering.

**Research corpus (use before doing new research):**
- `docs/research/language_family_coverage_map.md` — START HERE: index of all
  23 deep dives, coverage table, remaining gaps.
- `docs/research/cross_language_synthesis_master.md` — capstone synthesis:
  convergences, forks, incompatibilities, Nomi resolution per normal form.
- `docs/research/research_notes_synthesis.md` — earlier synthesis with
  progressive-reification spine and design tensions.
- Individual deep dives as listed in the Research Corpus section above.

For philosophical framing, use `docs/research/` as source material, then
reconcile claims back into the active docs listed above. The research corpus
is design evidence, not active specification.

## Nomi Normal Forms

Every accepted convenience should reduce to one or more of these:

- **Binding**: receive value, tentatively bind, check constraints, commit or diagnose.
- **Function**: parameters are bindings, body evaluates, result may be checked.
- **Pattern**: test structure, bind captures, check constraints, choose body.
- **Flow**: pass a value through calls, functions, collection transforms, or plans.
- **Block**: ordinary call plus attached caller-side code invoked by `yield`.
- **Absence/result**: distinguish missing value, expected failure, and unexpected error.
- **Data boundary**: external value explicitly decoded into owned data with diagnostics.
- **Explanation**: semantic events become traces, examples, diagnostics, or `explain` views.

Each normal form maps to a section in the capstone synthesis
(`cross_language_synthesis_master.md`) that reconciles cross-language research
into concrete Nomi design decisions.

Strings are a first-class cross-cutting pillar, not currently a ninth normal
form. String features should reduce to Data boundary, Pattern, Flow,
Absence/result, and Explanation unless a future capstone explicitly promotes
String to a new normal form.

If a candidate cannot reduce to this set, keep it research-only or propose the
smallest new primitive it would require.

## Core/Sugar Layer Workflow

Use this when the task mentions core, sugar, special forms, eval, backend
portability, Core IR, scoped extension, or Python independence.

1. Read `docs/language/core_layer_separation_plan.md` before proposing code.
2. Classify the feature or syntax:
   `L0 runtime substrate`, `L1 implementation core IR`, `L2 semantic core`,
   `L3 canonical surface`, `L4 sugar`, `L5 library convention`,
   `L6 scoped extension`, or `L7 backend`.
3. State the normal form and the reduction target. If it is L4 sugar, name the
   L2/L3 concept it expands to and avoid adding eval semantics.
4. If it is L2/L3 semantic core, plan both the user concept and the eventual
   L1 operations it lowers to.
5. If it is L6, require an explicit fence, inspectable expansion, and no
   meaning changes outside the scope.
6. If it is L7, require backend capability flags and avoid making backend
   limitations part of the language definition.
7. Update feature docs, `core_layer_separation_plan.md`, or
   `implementation_todos.md` when the classification changes.

## Research Workflow

1. **Check existing research first.** Read `language_family_coverage_map.md`
   to see if the topic is already covered. If a deep dive exists, read its
   Adopt/Refuse/Adapt table before proposing anything new.
2. Identify whether current repo artifacts reflect active direction,
   transitional implementation, or stale residue. Do not force the proposal to
   match stale state; record the drift and update the relevant status labels.
3. Identify the everyday programming pressure: readability, boundary safety,
   callback flattening, pattern choice, failure handling, data transformation,
   configuration, testing, explanation, or another concrete need.
4. Compare at least three nearby source-language forms (use the existing deep
   dives when they cover the languages — don't re-research from scratch).
5. Group almost-same features and name the nuance that actually matters.
6. Decide the Nomi normal form and whether the idea is:
   `implemented`, `prototype-ready`, `design-needed`, `library-first`,
   `research-only`, or `rejected-for-now`.
7. Recommend one Nomi path. Prefer library-first and docs-first when semantics,
   diagnostics, or interactions are not yet clear.
8. Update docs with a consolidation table, examples, status, and rationale.
9. If the research is genuinely new (not in the corpus), write a deep dive
   following the existing format, then update both index files.
10. For broad syntax/semantics planning, update
   `docs/language/syntax_substrate_todo_audit.md`,
   `docs/language/implementation_todos.md`, or
   `docs/language/forward_implementation_plan.md`.
11. Avoid implementation unless the user explicitly asks for it or the task is
    already scoped as implementation work.

## Spec-Editor Workflow

Use this when the user asks to consolidate docs, improve coherence, mark stale
material, or make the language easier to turn into a specification.

1. Read `language_foundation.md`, `language_spec.md`,
   `spec_readiness_map.md`, and `docs_eagle_eye_review.md` before editing.
2. Identify whether each touched doc is `active`, `source`, `historical`,
   `obsolete`, or `scratch`. Add or sharpen the status block when unclear.
3. Promote decisions, not essays. Move stable conclusions into the spec,
   feature docs, or convenience docs; leave research or draft files as
   evidence.
4. Keep the operational spec convergence loop explicit:
   research evidence -> interaction map -> focused feature packet -> target
   demo or fixture -> `language_spec.md` -> implementation slice -> runnable
   sample and tests.
5. For each promoted feature, require the feature packet from
   `spec_readiness_map.md`: everyday pressure, user syntax, normal form,
   reduction, diagnostics, interactions, rejected alternatives, implementation
   slice, current status.
6. Separate doc modes: tutorial, how-to, reference/spec, explanation,
   planning, source research. Do not let one page pretend to be all of them.
7. Make comments operational: name the next file to edit, the status to assign,
   the decision to preserve, the test/sample gate, or the reason to reject.
8. If the user asks for new research or "search", use current external sources
   and prefer official language references, specs, tours, or framework docs.
   Reconcile external lessons into Nomi normal forms instead of copying
   catalogues.
9. Update `docs/language/demo_target.nomi` when a global syntax decision
   changes the intended whole-language feel. Keep target-only syntax out of
   `samples/*.nomi` until parser, runtime, tests, and snapshots agree.
10. Update `docs/README.md`, `docs/convenience/README.md`, relevant feature
   docs, and this skill when the workflow itself changes.
11. Do not leave broken active links. If a doc is purged or demoted to drafts,
   update the active index or add an active distilled replacement.

## Iterative Convenience Refinement

Use this when the user asks for high-quality convenience syntax across
languages, especially functions, patterns, and collections.

Work in checkpointed passes:

1. **Checkpoint first.** If there is already finished work, commit it before
   starting a new research pass.
2. **Local consolidation pass.** Read `docs/convenience/README.md`,
   `functions.md`, `patterns.md`, `flow_and_collections.md`,
   `interaction_map.md`, `syntax_synthesis_matrix.md`, and
   `review_and_roadmap.md`. Tighten interactions, stale statuses, caveats, and
   next-pass notes.
3. **External research pass.** Search current official language references,
   standard library docs, or mature ecosystem docs for uncovered ideas. Prefer
   primary sources. Fold only durable user needs back into Nomi normal forms.
4. **Intersection pass.** For each candidate, decide whether it belongs to
   function, pattern, flow, block, result, data boundary, or explanation.
   Record caveats where the candidate crosses boundaries.
5. **Spec-shaping pass.** Convert accepted ideas into feature packets:
   everyday pressure, syntax, normal form, reduction, diagnostics,
   interactions, rejected alternatives, implementation slice, status.
6. **Target coherence pass.** If the decision affects more than one normal
   form, update `docs/convenience/interaction_map.md` and
   `docs/language/demo_target.nomi` before touching runnable samples.
7. **Commit after each pass.** Leave the repo in a coherent state with notes
   for the next exact pass.

For function/pattern/collection work, always check:

- Does piecewise function syntax remain just pattern dispatch?
- Does collection flow use ordinary function values or named verbs first?
- Does row/group syntax introduce new binding rules?
- Does a pattern candidate diagnose shape failure versus constraint failure?
- Does a pipeline candidate explain intermediate values and source paths?

## Coherence Checks

Before accepting a new surface form, ask:

- Does it reuse binding, function, pattern, flow, block, data boundary, or
  explanation semantics?
- Is it already analyzed in an existing deep dive? What does the
  Adopt/Refuse/Adapt table say?
- Does it duplicate an existing spelling with only a small aesthetic change?
- Can tooling show the desugared form?
- Can diagnostics speak in normal-form vocabulary rather than private sugar?
- Does it preserve Python parity where Nomi intentionally follows Python?
- Does it make common code clearer at the call site?
- Does it introduce another mini-language for validation, records, patterns,
  queries, callbacks, or testing?
- Can it be represented as a feature-owned manifest/profile instead of a
  scattered grammar, transformer, interpreter, and test patch?

Reject or defer features that add a second validation language, a second
placeholder family, a generic propagation operator for both absence and errors,
dense glyph notation as everyday syntax, global macros, or systems-language
ownership syntax in the first layer.

## Preferred Recommendations

These are grounded in the cross-language synthesis and deep dive corpus:

- Keep one binding/constraint story for assignments, parameters, fields,
  imports, block parameters, pattern captures, and decoder fields.
- Keep `data` for owned program values; use `Data.decode(...)`, patterns, and
  constraints for external structures.
- Keep pattern matching as the basis for `match`, if-let, guard-let, variants,
  mapping/list patterns, and destructuring.
- Keep `|>` as the main value-flow operator; use `_` when the piped value
  belongs somewhere other than the first argument.
- Keep composition separate from pipeline: pipeline applies a value now;
  composition builds a function for later.
- Keep one block-call story for resources, retry, transaction, fixtures,
  tracing, and future policy blocks.
- Treat `?.` and `??` as absence-only. Use `Result` plus `match` for expected
  failure before considering `?`.
- Start query/table/rank/shape work as named library functions and plan values
  before adding dense syntax.
- Treat examples, tests, traces, query plans, and decode errors as one
  explanation family.
- Keep one ordinary string interpolation mechanism (f-strings). Do not add `%`,
  `.format()`, `string.Template`, or heredocs. f-strings are the one way.
- Typed wrappers (`sql""`, `html""`, `re""`, `sh""`) are a design direction,
  not a parser task yet. They must produce distinct types, not `str`, and each
  target needs a context-specific safety contract.
- Paths are not strings. URLs are not strings. SQL queries are not strings.
  Each gets a distinct type with explicit `to_str()` conversion.
- Treat strings as a first-class pillar alongside functions and collections
  (see `docs/convenience/strings.md`).
- Config is a data-boundary problem (see `data_boundary_systems_deep_dive.md`),
  not a second data declaration language.
- Secrets and sensitive values should be redacted by default in diagnostics and
  `explain` output (see `security_and_trust_deep_dive.md`).
- Nomi should ship a canonical formatter from day one, no configuration (see
  `formatting_and_style_deep_dive.md`).
- Dependency resolution should use content-addressed integrity, domain-name
  import paths, and no code execution during fetch (see
  `packaging_and_project_structure_deep_dive.md` and
  `security_and_trust_deep_dive.md`).

## Documentation Style

When editing design docs:

- Distinguish implemented behavior, prototype-ready syntax, design-needed
  questions, library-first ideas, research-only notes, and rejected-for-now
  ideas.
- Prefer `active`, `source`, `historical`, `obsolete`, and `scratch` labels for
  document status. If a doc is obsolete, say exactly what replaced it.
- Prefer comparative tables for overlapping features.
- Prefer spec-shaped sections over essays: syntax, reduction, diagnostics,
  status, rejected alternatives, tests/samples, open questions.
- Include small Nomi examples only when they clarify the recommended normal
  form.
- Keep target-only examples in `target_program_fixtures.md` or
  `target_language_tour.md`; do not move them into runnable samples until
  parser, lowering, runtime, tests, and snapshots agree.
- Point to source-language docs or existing Nomi docs (especially the research
  deep dives) instead of duplicating large explanations.
- Update `docs/README.md`, `docs/convenience/README.md`, and both research
  index files when adding a new durable design document.

## Substrate Planning

When the user asks for major future syntax, semantics, or faster
experimentation:

- Treat `docs/language/flexible_syntax_substrate_plan.md` and
  `docs/language/syntax_substrate_todo_audit.md` as the bridge from language
  design to syntax implementation.
- Treat `docs/language/architecture_refactoring_plan.md` as the bridge from
  language design to runtime/tool/package architecture.
- Prefer plans that make features declarative: status, normal form, feature
  owner, grammar, surface/core node, lowering, diagnostics, tests, docs, and
  tool exposure.
- Preserve optionality. For broad proposals, state what current implementation
  substrate remains replaceable and what design choice the proposal could make
  harder later.
- Add or update inline `NOMI-SUBSTRATE-*` TODOs only at real architectural
  seams, and keep the central audit in sync.
- Keep target-only syntax out of runnable samples until parser/lowering/tests
  prove the intended status.

## Useful Source Families

When new research IS needed (not already in the corpus), consult these
families. Each now maps to the deep dive where it is comprehensively surveyed:

- **ML-family** (OCaml, F#, Haskell, Elm, Roc, ReScript) — see `pattern_matching_synthesis.md`, `error_handling_defer_resource_cleanup_notes.md`
- **Pattern/result family** (Rust, Swift, Gleam, Zig) — see `pattern_matching_synthesis.md`, `error_handling_defer_resource_cleanup_notes.md`
- **Block/callback family** (Ruby, Kotlin, Swift, Julia, Gleam, Python context managers) — see `beam_languages_erlang_elixir_gleam.md` (Gleam `use`), `csharp_java_dart_modern_features.md`
- **Flow/table family** (Elixir, F#, Clojure, Nushell, SQL, dplyr, Polars, LINQ) — see `table_and_flow_systems_deep_dive.md`
- **Boundary/config family** (CUE, Nickel, Pkl, Dhall, Nix, Terraform, JSON Schema, Pydantic) — see `data_boundary_systems_deep_dive.md`
- **Array/symbolic family** (APL, J, K, Q, BQN, Uiua, Julia, Mathematica) — see `array_languages_deep_dive.md`, `scientific_languages_r_matlab_julia.md`
- **Ownership/systems family** (Rust, Zig, Odin, Hylo, Mojo) — see `error_handling_defer_resource_cleanup_notes.md`, `go_design_philosophy_deep_dive.md`
- **Concatenative family** (Forth, Factor, Joy, Kitten, Cat) — see `concatenative_languages.md`
- **Scientific/notebook family** (MATLAB, R, Julia, Jupyter) — see `scientific_languages_r_matlab_julia.md`, `interactive_explanation_deep_dive.md`
- **Macro/research family** (Lisp, Scheme, Racket, Nim, Scala, Koka, Eff, Flix, Unison, Darklang) — see `modern_language_feature_survey.md`
- **Pedagogy/onboarding** — see `first_hour_pedagogy_deep_dive.md`
- **Tooling/IDE/AI collaboration** — see `ai_readable_semantics_deep_dive.md`, `diagnostics_and_explanations_comparative.md`
- **Packaging/deployment** — see `packaging_and_project_structure_deep_dive.md`, `deployment_and_operations_deep_dive.md`
- **Security/trust** — see `security_and_trust_deep_dive.md`
- **Documentation** — see `package_docs_and_examples_deep_dive.md`
- **Formatting/style** — see `formatting_and_style_deep_dive.md`
- **Stdlib design** — see `standard_library_design_comparative.md`

Before consulting any source family, read its corresponding deep dive first —
it already synthesizes 8-16 languages on that topic.

## Syntax Substrate Extension Path

When implementing new syntax in the prototype, follow the current extension
path (documented in `CLAUDE.md`):

1. **Grammar** — add a rule to the appropriate layer in
   `prototype/grammar/layers/`. Verify with `tools.syntax.inspect --stage raw-tree`.

2. **Lowering** — create a module in `prototype/parser/nomi/lowering/`
   with a mixin class. Mix it into `FunctionsMixin` in
   `prototype/parser/nomi/functions.py`.

3. **Desugar** (optional) — if the syntax needs an AST-level transform,
   create a pass in `prototype/parser/nomi/desugar/` and add an entry
   to `BUILTIN_FEATURES` in `prototype/syntax/features.py`.

4. **Surface node** (optional) — if Python AST cannot naturally represent
   the construct, define a `SurfaceNode` subclass in
   `prototype/syntax/surface.py` and emit it from the lowering step.
   The `lower_surface_to_python()` walker handles the lowering.

5. **Tests** — parser unit tests, functional tests, and regression
   snapshot regeneration.

Key substrate files:
- `prototype/syntax/features.py` — current feature manifest registry
- `prototype/syntax/surface.py` — surface node base + `lower_surface_to_python`
- `prototype/parser/nomi/lowering/` — per-feature Lark→AST lowering modules
- `prototype/parser/nomi/desugar/pipeline.py` — desugar pass chain (derived from features)
- `prototype/grammar/assemble.py` — grammar assembly (derived from features)
- `tools/syntax/inspect.py` — pipeline stage inspection CLI
