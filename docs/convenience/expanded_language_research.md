# Language Research Index

> Status: cross-reference index.  The detailed language surveys originally
> in this file now live in dedicated research notes under `docs/research/`.
> This file is a finding aid — start here, then go to the deep dives.

## Research Files by Topic

| Topic | File | Covers |
|-------|------|--------|
| Error handling & cleanup | [error_handling_defer_resource_cleanup_notes.md](../research/error_handling_defer_resource_cleanup_notes.md) | Zig, Hylo, Odin, Gleam, Roc |
| Modern language features | [modern_language_feature_survey.md](../research/modern_language_feature_survey.md) | Mojo, Jai, Darklang, Unison, CUE/Nickel/Pkl/Dhall, Wren, Janet, Lobster, D |
| Deep type-system features | [deep_language_feature_survey.md](../research/deep_language_feature_survey.md) | Haskell, OCaml, Agda/Idris, Swift, Kotlin, Scala 3, F# |
| Concatenative languages | [concatenative_languages.md](../research/concatenative_languages.md) | Forth, Factor, Joy, Kitten, Cat |
| Array languages (deep) | [array_languages_deep_dive.md](../research/array_languages_deep_dive.md) | APL, J, K, BQN, Uiua |
| Scientific languages | [scientific_languages_r_matlab_julia.md](../research/scientific_languages_r_matlab_julia.md) | MATLAB, R, Julia |
| Python deferred changes | [python_changes_deferred_by_complexity.md](../research/python_changes_deferred_by_complexity.md) | Python PEPs rejected for complexity |
| Python syntax atlas | [python_syntax_stretch_feature_atlas.md](../research/python_syntax_stretch_feature_atlas.md) | Python syntax extension directions |
| Usability & syntax | [high_level_language_usability_syntax_notes.md](../research/high_level_language_usability_syntax_notes.md) | Human-centric design across languages |
| Everyday fallback ideas | [everyday_fallback_simplification_ideas.md](../research/everyday_fallback_simplification_ideas.md) | Practical simplification candidates |
| Language family coverage | [language_family_coverage_map.md](../research/language_family_coverage_map.md) | Which families are covered, which are gaps |
| Research synthesis | [research_notes_synthesis.md](../research/research_notes_synthesis.md) | Cross-cutting theses from all research |
| Cognitive vision | [cognitive_language_vision.md](../research/cognitive_language_vision.md) | Long-term cognitive design principles |

## Design Synthesis

For the critical integration layer (how features compose, conflict, and
what other languages learned), see:

- [design_lessons_and_integration.md](design_lessons_and_integration.md) — systemic cruft patterns, feature interaction analysis, community praise/regret, designer quotes, integration rules
- [syntax_synthesis_matrix.md](syntax_synthesis_matrix.md) — cross-language feature families with nuanced differences and Nomi recommendations
- [review_and_roadmap.md](review_and_roadmap.md) — normal-form status spine and implementation roadmap

## How to Use This

1. Identify the user need (error handling? data boundaries? flow?).
2. Find the relevant research file above.
3. Cross-reference with the design synthesis documents for integration critique.
4. Make recommendations using the normal-form reduction workflow in the
   [nomi-language-design skill](../../.agents/skills/nomi-language-design/SKILL.md).
