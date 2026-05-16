# Convenience Features

Per-feature syntax docs for Nomi convenience forms, backed by comparative
research.  This folder consolidates more than it expands — prefer enhancing
an existing doc over adding a new one.

Start with [design_lessons_and_integration.md](design_lessons_and_integration.md)
for the critical synthesis.  Then use the per-feature docs below.

## Normal Forms

Every accepted convenience reduces to one of eight normal forms:

- **Binding** — receive value, tentatively bind, check constraints, commit or diagnose
- **Function** — parameters are bindings, body evaluates, result may be checked
- **Pattern** — test structure, bind captures, check constraints, choose body
- **Flow** — pass a value through calls, functions, collection transforms, or plans
- **Block** — ordinary call plus attached caller-side code invoked by `yield`
- **Absence/result** — distinguish missing value, expected failure, and unexpected error
- **Data boundary** — external value explicitly decoded into owned data with diagnostics
- **Explanation** — semantic events become traces, examples, diagnostics, or `explain` views

## Documents

### Synthesis & Planning

| Doc | Purpose |
|-----|---------|
| [design_lessons_and_integration.md](design_lessons_and_integration.md) | Systemic cruft patterns, feature interactions, community praise/regret, designer quotes, integration rules |
| [syntax_design_rules.md](syntax_design_rules.md) | Concrete syntax-design rules derived from the dimensions analysis (primitive budget, axis coherence, elimination form, etc.) |
| [review_and_roadmap.md](review_and_roadmap.md) | Normal-form status spine, cross-doc critique, implementation roadmap |
| [syntax_synthesis_matrix.md](syntax_synthesis_matrix.md) | Cross-language feature families with nuanced differences and Nomi recommendations |
| [expanded_language_research.md](expanded_language_research.md) | Index to detailed research notes in `docs/research/` |

### Per-Feature Docs

| Doc | Normal form | Status |
|-----|-------------|--------|
| [functions.md](functions.md) | Function | implemented (func, `=>`, equations, holes, sections, compose, where); implicit scoping appendix |
| [patterns.md](patterns.md) | Pattern | implemented (match, if-let, while-let, guard-let); if-let detail + match-expr challenges appendices |
| [flow_and_collections.md](flow_and_collections.md) | Flow | implemented (pipeline, ranges, range-step, spread) |
| [absence_and_result.md](absence_and_result.md) | Absence/result + Block | implemented (`?.`, `??`, try-expr, guard-let, defer); Result/Option design-settled |
| [data_and_types.md](data_and_types.md) | Data boundary | type aliases + strings implemented; data classes + decode + @secret/@pii design-settled |
| [scope_context.md](scope_context.md) | Binding + Block | where + block-call DSL implemented; implicit params research-only |
| [concurrency.md](concurrency.md) | Block + Flow | Python async interop available; structured concurrency design-settled |
| [meta_testing.md](meta_testing.md) | Explanation + Block | decorators implemented; examples + checks design-settled |
| [modules_imports.md](modules_imports.md) | Binding | Python-compatible imports implemented; visibility + re-exports design-settled |

### Feature Readiness Summary

| Status | Count | Features |
|--------|-------|----------|
| **implemented** | 10+ | `func`, `=>`, equations, piecewise, holes, sections, compose, `where`, `\|>`, ranges, spread, `unless`, if-let, while-let, guard-let, match, or-patterns, `?.`, `??`, try-expr, `defer`, decorators, f-strings, type aliases, imports (Python-compatible) |
| **design-settled** | 15 | `Result[T,E]`, `Option[T]`, `Data.decode()`, `@secret`/`@pii`, `pub` visibility, re-exports, content-addressed imports, `examples:` blocks, `check:` statements, structured concurrency (block policies), collection verb vocabulary (12 verbs), query plans, `nomi fmt`, Tree-sitter + LSP, domain-name import paths |
| **prototype-ready** | 3 | binding error diagnostics, `BindingTarget`, constrained captures |
| **design-needed** | 5 | cancellation semantics, concurrency diagnostics, extension methods, operator overloading, regex capture patterns |
| **library-first** | 5+ | command functions, config layering, path values, safe commands, parallel collections |
| **research-only** | 3+ | macros, channels/actors, pure/read-only blocks |

### Reference

| Doc | Purpose |
|-----|---------|
| [implementation_learnings.md](implementation_learnings.md) | Grammar interactions, AST bugs, deferred features — living reference |

## Research Sources

The cross-language research corpus lives in `../research/` — 23 deep-dive files
surveying 60+ languages/systems across 16 language families and 8 cross-cutting
dimensions. Each deep dive includes a cross-language synthesis and a Nomi
Adopt/Refuse/Adapt table.

Start with the index: [../research/language_family_coverage_map.md](../research/language_family_coverage_map.md)

Capstone synthesis: [../research/cross_language_synthesis_master.md](../research/cross_language_synthesis_master.md)
(8 universal convergences, 8 design forks, 7 hidden incompatibilities, Nomi
resolution per normal form)

For the full deep dive index with line counts and coverage, see the
[Deep Dive Index](../research/language_family_coverage_map.md#deep-dive-index).

## Navigation by Intent

Start here based on what you're trying to do:

| Intent | Start with |
|--------|-----------|
| **Evaluate a new syntax proposal** | [syntax_design_rules.md](syntax_design_rules.md) → [design_lessons_and_integration.md §9](design_lessons_and_integration.md) (synthesis methodology) |
| **Understand why a design decision was made** | [design_lessons_and_integration.md](design_lessons_and_integration.md) (cruft patterns, designer regrets, integration rules) → [cross_language_synthesis_master.md](../research/cross_language_synthesis_master.md) (capstone) |
| **See what's implemented vs. planned** | [review_and_roadmap.md](review_and_roadmap.md) (status spine) |
| **Promote a design into the spec** | [../language/spec_readiness_map.md](../language/spec_readiness_map.md) (feature packet + spec conversion matrix) |
| **Compare Nomi's approach to other languages** | [syntax_synthesis_matrix.md](syntax_synthesis_matrix.md) (cross-language families) |
| **Implement a feature** | `docs/features/binding_constraints_feature.md`, `block_calls_feature.md` → `prototype/` code |
| **Add new syntax** | [design_lessons_and_integration.md §9](design_lessons_and_integration.md) (synthesis loop) → `CLAUDE.md` (extension path) |
| **Understand a specific normal form** | Per-feature docs below (functions, patterns, flow, absence, data, scope, concurrency, testing, modules) |
| **Find cross-language research on a topic** | [../research/language_family_coverage_map.md](../research/language_family_coverage_map.md) → deep dive for that domain |

### The Synthesis Docs (read in order)

1. [syntax_design_rules.md](syntax_design_rules.md) — concrete rules for designing surface syntax, derived from the dimensions analysis.  Includes nuance (when rules bend, how conflicts resolve).
2. [design_lessons_and_integration.md](design_lessons_and_integration.md) — systemic cruft patterns, feature interactions, community praise/regret, designer quotes, integration rules, and the synthesis methodology (§9).
3. [syntax_synthesis_matrix.md](syntax_synthesis_matrix.md) — cross-language feature families, semantic differences, and Nomi recommendations.
4. [review_and_roadmap.md](review_and_roadmap.md) — normal-form status spine and implementation phases.

These four docs form the synthesis stack: rules → lessons → comparisons → roadmap.

## Consolidation Rules

- Do not add a new doc when an existing doc can absorb the idea.
- Keep companion notes as appendices in the parent doc once stable.
- Source-language catalogues belong in `docs/research/`, not here.
- Implemented features should have runnable examples in `samples/demo.nomi`
  and `samples/demo_terse.nomi` after tests pass.
- When adding a synthesis insight, check whether it fits in the rules, lessons,
  matrix, or roadmap before creating a new doc.
