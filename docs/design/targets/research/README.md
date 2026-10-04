# Research Pressure Programs

> Status: target-only research candidates; proposed lab APIs, not accepted library contracts.

These independent modules put the requested broad research into source form.
They belong to the existing [target suite](../README.md), but do not replace its
overall target or admit new syntax. [Data synthesis](../../../research/data_workflows/nomi_candidates.md)
and [notation research](../../../research/notation_atlas.md) own their questions.

| Category | Source | What a human should see | Unclosed gate |
| --- | --- | --- | --- |
| Eager collection baseline | [data_collections.nomi](data_collections.nomi) | Real callbacks and predictable evaluation, versus table planning. | Numeric/collection callback contracts. |
| Table description | [table_plan.nomi](table_plan.nomi) | Schema-bound expressions; explain doesn't collect. | Generic/schema/null/cardinality and engine laws. |
| Scientific learned state | [scientific_model.nomi](scientific_model.nomi) | Fit sees training data; prediction doesn't refit. | Split/schema/learned-state and reproducibility contracts. |
| Workflow publication | [workflow.nomi](workflow.nomi) | Partition/attempt/idempotency identities; uncertain external outcome. | Persistence, runtime grants and retry/reconciliation contracts. |
| Set/tensor/chemistry | [notation.nomi](notation.nomi) | Named universe, contracted axes and conservation model. | Equality, shape/unit and domain-validator contracts. |
| Overall reconciliation | [overall.nomi](overall.nomi) | Decode, validate keys, calculate, preview, separately publish. | Higher-order effect/generic and domain-error contracts. |
| Text boundaries | [text_boundaries.nomi](text_boundaries.nomi) | Display, strict decode, structured encoding, trusted rendering and argv preparation stay distinct. | Scalar/index, rendering, codec, provenance and process contracts. |
| Domain composition | [domain_layers.nomi](domain_layers.nomi) | Pinned report inputs, train-only descriptions, inert independent workflow steps and reviewed publication compose without changing call semantics. | Typed ports/descriptions, temporal basis, learned state, facade error conversion and real review/authority/publication protocols. |
| Generic operations | [generic_operations.nomi](generic_operations.nomi) | Strict transforms and seeded history, an explicit context-bound cache/codec, observable passthrough failure and bounded integer iteration. | Callback/generic/protocol/effect/region, cache policy, numeric and iteration outcome contracts. |
| Messaging architecture | [messaging.nomi](messaging.nomi) | Pure reconstruction, one-delivery atomic local intent and uncertain relay/reconciliation remain distinct. | Identity/codec, ownership/fencing, settlement/progress, local transaction, effects and pinned adapter crash/recovery contracts. |

Every `lab.*` module is **fictional proposed API**. These files have not been
parsed, typechecked or executed. Imports summarize the required boundary; they
are not stub implementations or exports available in the CLI/browser. Error
unification in the lab facades is deliberate and still needs a public contract.
Finite small-integer oracles do not establish general overflow behavior.

Examples use accepted target source shapes and ordinary calls. No global set
glyph, row quotation, tensor binder, reaction arrow or workflow keyword is added.
The callback/effect/region contract in [function design](../../function_contracts.md)
must close before claiming the API is typeable. Inspectable plan/view values
must not retain a live reader, task, credential or grant.

Only a settled category may later be promoted to `samples/` after independent
CLI/browser conformance. Documentation tests only guard research navigation and
the boundary between aspirational and runnable files.
