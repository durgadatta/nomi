# Cross-Language Feature Comparisons

> Status: comparative evidence and experiment routes, not target specification.

Packet: `docs/design/synthesis.md`, `docs/design/targets/overall.nomi`,
`docs/review/2026-09-29-language-synthesis.md`.

Start with the [maintainer synthesis guide](../synthesis_guide.md) to research
and integrate mechanisms. Its eight expanded language comparisons feed these
existing semantic owners; the guide is a working route, not another specification.

Read across a feature row or down a language column in the
[single synthesis matrix](../language_feature_matrix.md), then follow a feature
page below or an individual language in [the language index](../languages/README.md).
The [transpose](../feature_language_matrix.md) preserves every summary;
the [syntax matrix](../syntax_matrix.md) and [form study](../syntax_forms.md)
add source fragments, competing spellings and whole-program recognition tasks.
Linked language pages contain primary citations and version limits.
Matrices are selective comparisons of
relevant mechanisms, not claims that omitted languages lack a capability.
The Nomi recommendations are judgments; no usability or runtime benchmark was
performed in this pass.

| Feature | Target pressure |
| --- | --- |
| [Bindings and state](binding.md) | Name a fact, then visibly change state. |
| [Functions and calls](functions.md) | Transform values without hidden argument/control rules; [generic operations](../generic_operations.md) develop the property hierarchy. |
| [Types and owned data](types_data.md) | Model concepts while keeping local inference. |
| [Patterns and choice](patterns.md) | Handle every structural alternative. |
| [Failure and absence](failure.md) | Distinguish missing, rejected, and broken. |
| [Effects and authority](effects.md) | Explain what can touch the world. |
| [Resource lifetime](resources.md) | Release on every exit without losing causes. |
| [Concurrency](concurrency.md) | Own tasks, bound work, and observe failures. |
| [Collections and plans](collections.md) | Know when and how transformation executes. |
| [Decoding and constraints](decoding.md) | Convert external structure into valid owned data. |
| [Numerics and shape](numerics.md) | Make representation, rounding, and dimensions deliberate. |
| [Modules and tooling](modules_tooling.md) | Grow into packages without losing inspectability. |
| [Metaprogramming](metaprogramming.md) | Add domain power without expanding ambient core syntax. |

Each page connects observation, Nomi long form, interactions, and a bounded
test. The [synthesis](../../design/synthesis.md) orders cross-feature work;
[open questions](../open_questions.md) retain the active experiment agenda.
Accepted forms remain in [syntax](../../design/syntax.md),
[semantics](../../design/semantics.md), and [decisions](../../design/decisions.md).

The [domain composition continuation](../domain_composition.md) tests whether
these foundations can support data/time, AI/ML and documentary/human domains
coherently. The same [registered synthesis](../../design/synthesis.md#domain-layer-proposal)
owns the proposal; [local experiments](../data_workflows/composition_experiments.md)
are bounded models, not a new specification or runtime capability inventory.

## Research Gap Continuation

The October 4 research-only audit deepens four existing owners rather than
adding feature rows: [polymorphic sharing](functions.md#polymorphic-sharing-and-generalization),
[memory visibility](concurrency.md#memory-visibility-and-publication),
[foreign callback lifetime and re-entry](resources.md#foreign-callbacks-and-re-entry),
and [package-qualified nominal identity](modules_tooling.md#nominal-identity-across-package-instances).
Each distinguishes existing coverage from the sharper unresolved contract,
compares alternatives, and supplies beginner/production/failure-heavy inputs.
These are unperformed discriminators, not accepted generic notation, a memory
model, an FFI ABI or a package/type identity scheme. The
[research overview](../README.md#research-gap-continuation) routes the related
data, numeric and human-interaction obligations without changing the matrix.
