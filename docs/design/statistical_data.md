# Statistical Data Interface

> Status: designing proposal, 2026-10-10. A bounded engine-free research model
> implements schema checking and two closed laws. This is not an accepted Nomi
> package, language syntax, dataframe executor, or general theorem prover.

The interface should let someone describe a complete analysis before supplying
observations: name its inputs, select and transform variables, specify the
quantity being estimated, inspect every intermediate, check compatible
composition, and justify selected rewrites. Execution is a later, explicit
binding to an implementation that accepts the same contracts.

The selected direction is **immutable statistical objects with typed ports,
named dependencies, and versioned domain laws**. A table is one important
object, alongside distributions, estimators, models, uncertainty and proofs.
The [research comparison](../research/data_workflows/statistical_objects.md)
explains what Polars, pandas, R, dplyr, Ibis and Substrait contribute. The
[maintainer guide](../research/synthesis_guide.md) remains the research entrypoint.

## Try The Interface Without Data

From the repository root, with Python only:

```bash
python3 -m tools.statistical_interface check docs/research/data_workflows/statistical_plan.json
python3 -m tools.statistical_interface inspect docs/research/data_workflows/statistical_plan.json difference
python3 -m tools.statistical_interface prove docs/research/data_workflows/statistical_plan.json average decomposed
python3 -m tools.statistical_interface catalog
```

The [example](../research/data_workflows/statistical_plan.json) declares three
fields, filters on a non-null Boolean eligibility column, subtracts two nullable
measurements, and names the sum, valid count, row count, mean, expanded mean and
published alias. There are **no rows, dataset locations, engine objects or
callbacks**. Every node remains inspectable, including intermediates that are
not outputs. The interface does not import Polars, pandas, R or a database.

The third command returns `equivalent`. Replacing `decomposed` with
`wrong_denominator` returns `unknown`: counting all selected rows does not
establish the denominator needed for nullable differences. Exit codes are
0 for checked/equivalent, 1 for unknown equality, and 2 for an invalid contract.
Unknown is an honest limit of the rules, not a proof of inequality.

The Python entrypoint is `Plan.from_document(document)` in the
[research implementation](../../tools/statistical_interface/model.py).
`check()`, `inspect(node_id)`, `prove(left_id, right_id)` and
`verify(certificate)` are passive operations. Documents and inspection results
are detached snapshots. Build a new plan for each revision.

## Separate Five Questions

| Question | Evidence | What it cannot establish |
| --- | --- | --- |
| Is this a well-formed description? | Closed operation ports, unique references, acyclic dependencies and bounded artifact validation | Actual observations exist or satisfy the schema |
| Do the objects compose? | Types, observation domains, nullability, units and explicit policies | A filter leaves rows, a model is identified, or a procedure is scientifically appropriate |
| Are these descriptions equivalent? | Named theory, side conditions and replayable derivation | Every engine computes the same bits or every arbitrary program is decidable |
| Can this implementation execute it? | Pinned adapter capability receipt and accepted numeric/physical contract | Data satisfies population assumptions or results generalize |
| What happened in this execution? | Validated bindings, snapshots, engine receipt, diagnostics and result provenance | Statistical assumptions become true merely because execution succeeded |

The current model implements the first question, a small fragment of the
second, and bounded definitional checking for the third. It deliberately has
no execution path. Full unit checking, relational cardinality reasoning,
inference, fitted models and execution receipts are still proposed.

## Object Identity And Passive Inspection

Every object has a graph-local identity, a kind, contract, dependencies and
operation revision. The full design additionally needs source locations,
descriptive labels and a semantic revision. A label can change without changing
identity. Equal schemas and equal display names do not identify the same input.
Object references do not imply data has been materialized or retained.

The model uses bounded node IDs rather than source-language binding syntax.
Input IDs identify independent abstract sources. Relation aliases preserve an
observation domain; filtering creates a new domain. A column belongs to that
domain. Two equally long columns from different domains cannot be combined
positionally without an explicit alignment operation. An aggregate is a scalar
expression with provenance, not a one-row column implicitly broadcast anywhere.

Plan inspection must show the original named graph and a law-qualified
normalized projection. Optimization may share computation, but it must retain
a mapping from each requested reference to the implementing operation and
diagnostic origin. The same reference may acquire several physical realizations
for different adapters. A reference is not a storage address or engine handle.

Checking has no scan, schema discovery, sampling, display callback, automatic
collection or arbitrary user function execution. Data-dependent schemas, such
as an open-ended pivot, need a declared finite output vocabulary or remain
unresolved. Inspecting a fitted model description cannot fit it. Inspecting a
plot specification cannot fetch its data or execute a formatter.

## The Statistical Object Families

The [declarative catalog](../../config/data_interface.json) records 25 extensible
families and their proposed contract fields. This is an organizing vocabulary,
not an assertion that all statistical practice is exhaustively enumerated or
implemented. A family can have many specialized objects and revisioned methods.

| Layer | Objects | Required distinction |
| --- | --- | --- |
| Observations | Input port, schema, relation, column, scalar expression, selection | Declared schema versus resolved input; variable versus realized values; domain versus row count |
| Relational context | Partition, window | Group grain, missing keys, empty groups, order, frame and tie policy |
| Summaries | Aggregate state, weight | Update/merge/finalize; frequency, analytic, probability and survey weights are different contracts |
| Statistical intent | Estimand, estimator, parameter | Population target versus procedure; constrained parameter space versus fitted value |
| Probability | Distribution, random variable | Density/mass/CDF/sampling; marginal distributions versus a joint dependence model |
| Learning | Model specification, fitted artifact, prediction | Symbolic model versus learned state; training snapshot versus prediction input |
| Inference | Resampling plan, hypothesis test, uncertainty | Sampling unit, reference law, selection history, coverage/credibility and joint origin |
| Evaluation and presentation | Score, visualization | Loss and evaluation population versus rendering and interaction |
| Evidence | Proof artifact, execution receipt | Derivation about descriptions versus observations about a run |

A `ModelSpec` can depend on distributions and formulas without a dataset. A
`FitPlan` can depend on a model and an input port without being a fitted
artifact. A future `FittedArtifact` requires learned state and a training
receipt. A `Prediction` describes which kind of prediction is requested; a
point estimate, predictive distribution and confidence interval are not
interchangeable. These names illustrate objects, not accepted Nomi classes.

The catalog marks the current graph families `fragment` and the remaining
families `catalog-only`. Its fields describe the intended full contracts;
`fragment_support` names what is actually checked. A catalog-only distribution
is not silently accepted by the checker. New methods must declare ports,
type rules, policy parameters, laws, counterexamples and adapter obligations.

## A Small Set Of Domain Primitives

General-language Value/Bind/Apply/Choose/Perform/Scope families provide the
language substrate. Statistical composition needs additional domain contracts:

| Primitive family | Composition | Non-erasable obligation |
| --- | --- | --- |
| Declare and reference | Introduce an input, schema, variable or parameter; refer to a node | Identity, contract revision and observation domain |
| Transform | Project, compute, select, align, join | Null propagation, keys, multiplicity, broadcast and domain preservation |
| Partition and order | Group, sort, window | Output grain, absent groups, ties, frames and time basis |
| Accumulate and finalize | Initialize state, update, merge, finish | Identity, merge laws, missingness, numerical accuracy and empty result |
| Specify a measure or objective | Distribution, loss, likelihood, estimand | Support, normalization, units, dependence and assumptions |
| Plan an algorithm | Fit, optimize, sample, resample, predict | State ownership, stopping, randomness, leakage and diagnostics |
| Justify and bind | Compare descriptions; request an adapter execution | Theory/side conditions versus capabilities, physical representation and actual input validation |

This is a library architecture hypothesis, not seven new source keywords.
It must be challenged by awkward statistical objects, not made universal by
flattening their obligations into an opaque `apply` node.

### What Can Compose From Counts And Sums?

Let the selected valid observation domain be `D`. In exact arithmetic:

```text
N = count(D)
S = sum(x over D)
Q = sum(x*x over D)
mean = Missing if N=0 else S/N
variance(ddof) = Missing if N<=ddof else (Q - S*S/N)/(N-ddof)
covariance(ddof) = (sum(x*y) - sum(x)*sum(y)/N)/(N-ddof)
```

The variance formula additionally needs `N>0`, a declared `ddof`, and a chosen
empty-result contract. Covariance must use **one paired-valid domain** for all
four reductions. Independently dropping missing values in each variable breaks
that formula. These variance/covariance forms are proposed exact definitions;
the executable model does not yet admit their laws or operators.

Weighted mean can use `(sum(w*x), sum(w))` only after specifying the weight kind,
shared pair mask, allowed weights and zero-total behavior. Weighted variance
has no single denominator valid for every kind of weight. A distributed mean
can merge `(S,N)` by addition and finalize once; averaging partition means
without counts changes the result. Floating state needs its own accuracy and
merge-order contract rather than borrowing the exact law.

Quantiles need an order statistic and a defined interpolation method. An exact
arbitrary quantile is not generally reducible to a fixed number of counts and
ordinary moment sums. A bounded sketch is a different object with an error
contract. Likelihood and CDF are distinct operations; a density at a point is
not a probability of that exact continuous value. A bootstrap also requires a
sampling unit and dependence policy, not merely a repeated `map`.

## The First Implemented Law

The closed `mean-valid-exact-v1` rule is:

```text
mean(x) = safe_divide(sum(x), count_valid(x))
```

Its context is explicit:

- `x` is the **same column expression in the same observation domain**.
- Its values are exact integers/rationals, in `exact-rational-v1`.
- Aggregations skip declared nulls; the denominator counts precisely those
  non-null values. NaN is not an alternative spelling of null.
- Sum over no valid values is exact zero. The mean and `safe_divide` both return
  Missing for zero denominator. Ordinary division with an error on zero is a
  different operation.
- The current fragment is dimensionless, finite and unordered. No independent
  sampling, distributional or nonempty-population assumption is needed.

The law therefore covers empty and all-null inputs without acquiring any rows.
This establishes a **definitional identity in the chosen theory**. It does not
prove a backend's `avg` implementation conforms, invent a universal definition
of every library's mean, or infer a scientific population mean from a sample.
An unguarded `sum(x)/count_valid(x)` would require a proved positive valid count
or a compatible zero-denominator contract. A user's assertion is not that proof.

The checker normalizes aliases and expands only the exact mean rule. It does
not reorder sums, distribute products, solve predicates, infer positive
cardinality, or execute callbacks. The opaque Float64 profile can be checked
structurally but receives no exact mean expansion. Even exact-valued fields
under an unspecified numeric profile do not authorize the rule.

Proof receipts record the plan/catalog/checker context, profile, original
references, applied rules and normalized term fingerprints. `verify` recomputes
the derivation and requires an exact receipt match. Schema, profile or catalog
changes invalidate a receipt. The closed checker and its rule definitions are
the trusted base; replay by the same checker is not independent formal
verification. SHA-256 fingerprints assume collision resistance. A future proof
format should expose an independently replayable normalized DAG and separate
semantic identity from incidental manifest order and output selection.

## Interface Versus Implementation

The future adapter boundary has four explicit stages:

| Stage | Request | Required receipt or refusal |
| --- | --- | --- |
| Capability negotiation | Checked graph, operation revisions, numeric profile and requested outputs | Supported operations/policies/types; unsupported combinations, conversion costs and accuracy changes |
| Binding | Input IDs to authorized source/snapshot handles | Schema validation, concrete revisions, null/representation rules and authority; no unchecked URI embedded in a proof graph |
| Compilation | Accepted graph and bindings | Physical plan, output-reference mapping, law-qualified rewrites, pushdown and materialization choices |
| Execution | Explicit approved run with resource and cancellation policy | Results plus engine/version/input/profile receipt, partial outcomes, diagnostics and cleanup completion |

These stages are interface proposals; **no adapter is implemented**. Interface
separation does not guarantee every engine supports every object. An adapter
must refuse an exact-rational contract if it only has fixed-width or floating
arithmetic, rather than silently casting. An eager pandas implementation can
execute a lazy description at the boundary without turning the interface eager.
An R adapter must resolve method dispatch, recycling and missingness explicitly.
A Polars adapter must resolve context and expression support explicitly.

Physical row layout, Arrow buffers, vectorization, SQL pushdown, distributed
partitions, GPU lowering and object storage stay behind that boundary. Typed
normalization and physical optimization remain separate: a mathematical rewrite
can increase intermediate size or numerical error on a different profile.
An execution receipt records what the adapter actually accepted, not just what
the interface requested.

## Current Gaps And Selected Data-Only Path

| Order | Concrete next closure | Acceptance evidence |
| --- | --- | --- |
| 1 — implemented fragment | Named schema-only graph, inert inspection and bounded mean identity | Focused tests, invalid/cyclic/foreign-object refusal, unknown count/Float64 laws, revision/tamper refusal |
| 2 — next | Independently replayable expression/theory artifacts; exact variance/covariance and explicit units | External replay of the derivation; paired-mask, ddof, zero-count and dimensional counterexamples; no backend required |
| 3 | Group, window, alignment and join contracts | Duplicate keys, nullable keys, absent versus empty groups, tie policies and cardinality changes; no implicit index alignment |
| 4 | Distribution/estimand/estimator and model-description interfaces | Support and normalization obligations, joint dependence, sample-design/weight distinctions, named pre-fit intermediates |
| 5 | One pinned adapter for a deliberately small accepted fragment | Bind-time validation, conversion refusal, independent arithmetic oracles, operation support matrix, output provenance and cancellation receipts |
| 6 | Fit/predict/resampling/inference objects | Training/evaluation separation, stochastic stream identity, learned-state provenance, convergence and assumption diagnostics |
| 7 | User interaction and Nomi admission | One full analysis readable before data exists; independently checked plan and engine explanation; diagnostic/source/formatter/runtime contracts before any syntax admission |

The artifact boundary currently permits at most 512 nodes, dependency/nesting
depth 64, 128 fields per input and 1 MB of JSON. IDs are bounded. Unknown
attributes, operations, types, duplicate keys/IDs/fields, dangling references,
cycles, mixed exact/float column arithmetic and nullable filter masks are
refused. These are laboratory limits, not language limits. JSON is a portable
experiment encoding, not the desired user-facing statistical notation.

The existing [DW1-DW8](../research/data_workflows/nomi_candidates.md), numeric
question 9 and [ML1-ML6](../research/data_workflows/ai_ml.md) retain their ownership.
This path supplies concrete interface evidence to them. Complete Nomi generic
and effect checking is needed for eventual package admission, but not for
continuing this isolated experiment. Removal criteria: replace this model when
a checked domain library and independent proof consumer cover its fragment;
keep its counterexamples and provenance obligations as conformance evidence.
