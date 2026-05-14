---
name: nomi-language-design
description: Refine Nomi language design and syntax by researching other languages, grouping similar features, extracting user needs, reducing candidates to Nomi normal forms, and updating docs without accumulating incoherent syntax. Use for convenience-syntax research, philosophical design synthesis, feature admission decisions, and recommendations for how Nomi should combine ideas from other languages.
compatibility: codex, opencode, deepseek-tui, claude-code
---

# Nomi Language Design

Use this skill when the task is about Nomi's language direction, syntax
research, convenience features, design philosophy, or translating ideas from
other languages into a coherent Nomi surface.

This file is intentionally plain Markdown with YAML frontmatter so Codex,
OpenCode, deepseek-tui, Claude Code, or another agent can all read the same
instructions. If a tool has a skill loader, load this skill. If not, read this
file directly before working.

## Core Rule

Do not copy syntax because it is attractive elsewhere. Extract the durable user
need, compare close relatives, reduce the idea to a Nomi normal form, then
recommend one coherent spelling.

```text
source language -> user need -> semantic difference -> Nomi normal form -> surface syntax
```

Never:

```text
source language -> copied syntax -> explanation after the fact
```

## Start Here

Read the smallest relevant set before changing docs or making recommendations:

- `docs/language/language_foundation.md` — canonical design foundation.
- `docs/language/language_direction_and_gap_map.md` — adoption-oriented gaps,
  caveats, and next design artifacts.
- `docs/language/language_degrees_of_freedom.md` — strict core vs sugar,
  library-first, scoped extension, future layer, and rejection framework.
- `docs/language/target_program_fixtures.md` — aspirational everyday programs
  for testing design coherence before implementation.
- `docs/language/design_proposal_template.md` — proposal structure for moving
  research ideas toward accepted Nomi decisions.
- `docs/language/language_spec.md` — draft concrete language specification.
- `docs/convenience/review_and_roadmap.md` — normal forms and feature status labels.
- `docs/convenience/syntax_synthesis_matrix.md` — cross-language feature families and recommendations.
- `docs/convenience/expanded_language_research.md` — newer language and PL research synthesis.
- Relevant focused docs under `docs/convenience/`, such as `functions.md`,
  `collections.md`, `patterns.md`, `error_handling.md`, `null_handling.md`,
  `types.md`, `scope_context.md`, `array_languages.md`, or `others.md`.
- Relevant feature pillars under `docs/features/`, especially
  `binding_constraints_feature.md`, `block_calls_feature.md`, and
  `structured_collections_query_language.md`.

For philosophical framing, use `docs/research/` and `docs/notes/` as source
material, then reconcile claims back into the active docs above.

For broad language-family coverage, check
`docs/research/language_family_coverage_map.md` before adding a new source
tradition or claiming a gap is already covered.

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

If a candidate cannot reduce to this set, keep it research-only or propose the
smallest new primitive it would require.

## Research Workflow

1. Identify the everyday programming pressure: readability, boundary safety,
   callback flattening, pattern choice, failure handling, data transformation,
   configuration, testing, explanation, or another concrete need.
2. Compare at least three nearby source-language forms when possible.
3. Group almost-same features and name the nuance that actually matters.
4. Decide the Nomi normal form and whether the idea is:
   `implemented`, `prototype-ready`, `design-needed`, `library-first`,
   `research-only`, or `rejected-for-now`.
5. Recommend one Nomi path. Prefer library-first and docs-first when semantics,
   diagnostics, or interactions are not yet clear.
6. Update docs with a consolidation table, examples, status, and rationale.
7. Avoid implementation unless the user explicitly asks for it or the task is
   already scoped as implementation work.

## Coherence Checks

Before accepting a new surface form, ask:

- Does it reuse binding, function, pattern, flow, block, data boundary, or
  explanation semantics?
- Does it duplicate an existing spelling with only a small aesthetic change?
- Can tooling show the desugared form?
- Can diagnostics speak in normal-form vocabulary rather than private sugar?
- Does it preserve Python parity where Nomi intentionally follows Python?
- Does it make common code clearer at the call site?
- Does it introduce another mini-language for validation, records, patterns,
  queries, callbacks, or testing?

Reject or defer features that add a second validation language, a second
placeholder family, a generic propagation operator for both absence and errors,
dense glyph notation as everyday syntax, global macros, or systems-language
ownership syntax in the first layer.

## Preferred Recommendations

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

## Documentation Style

When editing design docs:

- Distinguish implemented behavior, prototype-ready syntax, design-needed
  questions, library-first ideas, research-only notes, and rejected-for-now
  ideas.
- Prefer comparative tables for overlapping features.
- Include small Nomi examples only when they clarify the recommended normal
  form.
- Point to source-language docs or existing Nomi docs instead of duplicating
  large explanations.
- Update `docs/README.md` or `docs/convenience/README.md` when adding a new
  durable design document.

## Useful Source Families

- ML-family: OCaml, F#, Haskell, Elm, Roc, ReScript.
- Pattern/result family: Rust, Swift, Gleam, Zig, Crystal, Verse.
- Block/callback family: Ruby, Kotlin, Swift, Julia, Nim, Python context managers.
- Flow/table family: Elixir, F#, Clojure threading macros, Nushell, SQL, dplyr,
  pandas, Polars, LINQ.
- Boundary/config family: CUE, Nickel, Pkl, Dhall, Nix, Terraform/HCL,
  JSON Schema, Pydantic.
- Array/symbolic family: APL, J, K, Q, BQN, Uiua, Julia, Mathematica.
- Macro/research family: Lisp, Scheme, Racket, Nim, Scala, Koka, Eff, Flix,
  Unison.

Use web research when the user asks for more coverage, recent language details,
official docs, or precise citations.
