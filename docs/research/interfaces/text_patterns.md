# Patterns And Selectors: Describe A Set

> Status: interface comparison; existing Nomi structural patterns remain authoritative.

## Evidence And Pressure

CSS Selectors specifies selection over document structure. RE2 publishes an
explicitly bounded syntax repertoire rather than supporting every regex form.
[Selectors](https://www.w3.org/TR/selectors-4/),
[RE2 syntax](https://github.com/google/re2/wiki/Syntax).

Regex, globs, tree paths, and structural patterns all help describe subsets,
but differ in subject, capture, anchoring, traversal, and failure. A path can
name one item, select many, or describe a location that does not exist. Those
are not interchangeable outcomes.

## Nomi Normal Form And Placement

Keep core `match` structural, pure, and exhaustive. A text-search library can
compile a pattern to `Result[CompiledPattern, PatternError]`, then search under
declared input/result budgets. A document-selector library returns explicit
matches and stable paths. Neither should turn a core pattern attempt into an
arbitrary user computation or hide expensive iteration inside an extractor.

An editor selector can be a proposed typed path over known Surface node kinds.
It should distinguish a missing target from an empty match set and an invalid
query. Replacing all matches requires a separate candidate-change transaction.
**Defer:** scoped notation until explicit builder calls fail representative
queries. **Reject:** a universal punctuation syntax that blurs string, tree,
nominal-data, and stream matching.

## Discriminating Experiment

Select missing-field diagnostics, select calls to an effectful API, and replace
one binding across shadowed scopes. Compare explicit predicates with a scoped
selector builder. Include nested inputs and malformed patterns. Require bounded
cost and no replacement by textual name alone. The user-facing payoff is a
reliable search/refactor workflow, not more forms of `match`.
