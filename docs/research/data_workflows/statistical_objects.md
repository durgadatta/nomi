# Statistical Objects Before Observations

> Status: research evidence and synthesis, checked 2026-10-10. Foreign-system
> claims below come from primary documentation; those systems were not executed
> in this pass. The separate Nomi research checker has executed local tests.

The selected question is now specifically data/statistics: can we describe an
analysis, inspect every intermediate and check selected identities before
supplying observations, while leaving storage and execution replaceable?
The [design proposal](../../design/statistical_data.md) owns the candidate
interface, current law, limitations and actionable path. This document owns the
comparison, scientific pressures and counterexamples.

## Existing Systems Supply Different Pieces

| Primary reference | Mechanism to retain | Boundary to strengthen in Nomi |
| --- | --- | --- |
| [Polars lazy API](https://docs.pola.rs/user-guide/concepts/lazy-api/) | A plan can be constructed lazily, inspected with `explain`, and built from a declared schema | Passive checking must remain separate from source discovery and collection |
| [Polars schema resolution](https://docs.pola.rs/api/python/stable/reference/lazyframe/api/polars.LazyFrame.collect_schema.html) | `collect_schema` resolves a lazy plan's schema; documentation warns it can read storage metadata or contact a network | Laziness alone is insufficient for input-free checking; unknown schemas remain unknown unless an explicitly authorized resolver runs |
| [pandas Series mean](https://pandas.pydata.org/docs/reference/api/pandas.Series.mean.html) | The mean has explicit axis, missing-value and numeric-column options | Make the selected observation domain, missing policy and scalar versus column shape part of the object contract |
| [R mean](https://stat.ethz.ch/R-manual/R-devel/library/base/html/mean.html) | A generic mean admits methods, trimming and a missing-value policy | A method name is not one universally portable algebraic law; operator identity includes definition and policy |
| [R weighted mean](https://stat.ethz.ch/R-manual/R-devel/library/stats/html/weighted.mean.html) | Missing weights, zero weights and normalization have distinct documented behavior | Weight support and pair masks need contracts; substituting arbitrary `sum(w*x)/sum(w)` is unsafe without them |
| [dplyr summaries](https://dplyr.tidyverse.org/reference/summarise.html) | Summary output grain and grouping retention are explicit concerns; reuse/overwrite of summary variables differs by backend | Name every intermediate with immutable identity and resolve grain before physical lowering |
| [Ibis unbound expressions](https://ibis-project.org/how-to/extending/unbound_expression) | Schema-bearing tables can be described without a data connection and later executed by supported backends | Engine separation already has a strong precedent; the proposed additional work is law-qualified equivalence, statistical intent and inspectable evidence |
| [Substrait aggregation](https://substrait.io/expressions/aggregate_functions/) | Aggregate interfaces distinguish ordering, decomposability, intermediate state and execution phase | Keep semantic laws separate from serialized operator names; state shape, update/merge/finalize and numeric contracts must agree |

Version fences: the retrieved pandas page identifies 3.0.6; dplyr identifies
1.2.1. R references are **R-devel** (the weighted-mean page reports stats 4.6.0),
not a claim about the user's released R installation. Polars, Ibis and Substrait
are rolling documentation consulted on the date above. These are source
observations, not cross-engine conformance or performance measurements.

The proposal is therefore not that existing systems lack lazy tables or engine
abstraction. It combines those precedents with a stricter no-input checking
boundary, named statistical intent, and small, auditable semantic theories.

## Three Kinds Of Abstraction Must Stay Distinct

**Computational descriptions** specify schema, expressions, relational context,
algorithms and dependency graphs. They can often be checked without data.
**Statistical specifications** additionally state population, estimand, sample
design, dependence, distributional assumptions and interpretation. Many of these
are obligations rather than mechanically established facts. **Realized objects**
contain observations, learned state or execution results and need explicit
bindings, authority and provenance.

A named `NormalDistribution(mu, sigma)` description can be checked for a valid
parameter space if positivity is established. It does not prove the observed
data are normal. A regression specification can expose formula terms and a
prediction contract without fitting. Declared column types do not establish
full rank, no confounding, independence or causal identification. A valid
confidence-interval procedure does not turn an arbitrary adaptive sample into
a valid experiment.

The complete family vocabulary is in the
[catalog](../../../config/data_interface.json); the design groups it by layer.
Expansion should occur through typed specialized objects, not a claim that one
generic `StatisticalObject` makes every operation meaningful on every instance.

## Composition Obligations For Statistical Families

| Family | Useful composition | Required policy or counterexample |
| --- | --- | --- |
| Observation domain | Source → select → aligned variables → summary | Filtering can erase every row; equal lengths do not imply paired observations |
| Aggregate state | Initialize → update → merge → finalize | Partition means require counts; empty state and finalization can have different types |
| Weight | Pair domain → weighted products/sums → finalize | Frequency counts, precision weights, sampling probabilities and survey design are not interchangeable |
| Moment | Count, first moment, cross-product, second moment | Pairwise missingness, ddof, finite-sample denominator and physical units |
| Order statistic | Domain → ordering contract → quantile | Ties, interpolation, rank definition, approximation bounds and merge behavior |
| Distribution | Support + parameters + base measure → density/mass/CDF | Density is not probability at a continuous point; mixed discrete/continuous support needs an explicit measure |
| Joint random variables | Marginals + dependence → transformation | Equal means/variances do not prove independence; shared origins must remain referenceable |
| Estimand/estimator | Population target + design + algorithm | A perfectly computed sample statistic can estimate the wrong target |
| Model and prediction | Terms + likelihood/link → fit plan → learned artifact → predict | New levels, missing predictors, training-only transformations and prediction kind |
| Optimization | Objective + constraints + initialization + algorithm | Convergence, identifiability, local optima and boundary solutions are diagnostics, not type facts |
| Resampling | Sampling unit + dependence + random stream → replicates | Row bootstrap breaks clustered/time dependence; retries must not silently change the stochastic experiment |
| Test and uncertainty | Null/alternative + statistic + reference law → result | Multiplicity, selection history, conditioning and nominal versus achieved coverage |
| Evaluation | Prediction + target + loss + held-out domain | Leakage includes adaptive use of evaluation feedback, not just direct training access |
| Presentation | Named result → encodings/scales → view | Aggregation, omitted categories, uncertainty transformation and display-triggered execution |

These are original design discriminators, not claims that the checker currently
proves them. Detailed train/evaluation and uncertainty pressures remain in
[AI/ML](ai_ml.md), [correlated uncertainty](../notation_atlas.md#correlated-uncertainty-shared-origin-is-part-of-the-model)
and [dependencies/time](dependencies_and_time.md).

## Corner Cases For The Mean Request

The requested equality becomes checkable only after defining the operator:

| Case | Counterexample or obligation | Required checker response |
| --- | --- | --- |
| Nullable observations | `[2, null]`: valid count 1, row count 2 | Refuse an unconditional rewrite using row count |
| All missing or empty | Both have valid count zero | Match Missing/NaN/error behavior explicitly; the selected exact theory chooses Missing |
| Filtered or grouped input | A nonempty source can produce an empty selected domain or group | Source cardinality is not a valid-count proof |
| Different masks | Sum over eligible values divided by count over all values | Preserve the same expression/domain in numerator and denominator |
| Floating accumulation | `[10^16, 1, -10^16]`: left-fold sum and compensated sum can differ | Exact rewrite is unavailable for an unspecified float implementation |
| Bounded integer arithmetic | A partial sum can overflow even when a final mean fits | Exact integers, checked overflow and wrapping arithmetic are separate profiles |
| Weights | Value and weight validity masks differ; total weight can be zero | State weight kind, shared pair policy and zero-total behavior |
| Partitioning | Partition A `[0]`, partition B `[10,10,10]`: mean of partition means 5, pooled mean 7.5 | Merge sums/counts, not unweighted means |
| Units | Mean of temperatures and ratio of two measured quantities | Count is dimensionless; addition needs compatible units; affine units require a separate contract |
| Evidence revisions | Same display graph after a schema, numeric or theory change | Invalidate the prior receipt |

The model establishes the symbolic exact mean identity on the schema-only
example. Its tests also check negative denominators/domains/profiles, inertness,
aliases and forged receipts. Finite exact-arithmetic and floating countermodels
exercise the rule's trusted definition; they are not the justification for
equality on arbitrary unseen inputs. That justification is the declared
definition and closed derivation. There is no empirical distributional proof.

## Trade-Offs To Resolve Through The Data Path

**Explicit schema versus discovery.** Declared schemas permit passive checking
and reproducible tooling. Actual binding must validate them, and an honest
checker sometimes reports unresolved shape. Running a scan to fill a gap
changes the activity and authority boundary.

**Stable references versus optimizer freedom.** Keeping every intermediate
addressable supports explanation, diagnostics and reuse. It should not force
every intermediate to be stored. The adapter needs a mapping from logical
references to physical computations, including computations fused away.

**Small trusted theory versus expressiveness.** Closed laws make receipts
auditable. Arbitrary callbacks or claimed algebraic properties cannot be used as
proofs. Extension requires a versioned theory and a checked rule/derivation, or
an explicitly assumed proposition that remains visible as conditional evidence.

**Portability versus capability.** A backend-neutral interface should reveal
unsupported operations, conversion, accuracy and cost. A lowest-common-
denominator interface would discard useful capabilities; pretending engines
agree would conceal different answers. A richer object can have partial adapter
support without changing its meaning.

**Exact laws versus practical numerics.** Counts and rational sums have clean
merge laws. Real analyses need stable floats, decimals, complex numbers,
intervals, automatic differentiation and approximate algorithms. Those require
separate theories and error contracts, not expansion of the exact proof scope
by changing a dtype spelling.

**Scientific intent versus mechanical checking.** Typeable estimators and model
plans should expose assumptions and diagnostics. Assumptions about sampling,
identification or model adequacy need evidence from study design and observations;
they cannot be certified by a DAG constructor.

**One coherent language versus a second evaluation language.** The future Nomi
library should construct ordinary immutable descriptions and inspect them through
ordinary references. R formulas and dataframe expression contexts provide useful
forms to compare, but no implicit ambient column namespace or universal staged
evaluator is admitted. JSON is just the current engine-free laboratory boundary.

Continue only through the ordered closures in the
[design proposal](../../design/statistical_data.md#current-gaps-and-selected-data-only-path).
The next experiment remains data-specific: expose independently replayable
expression artifacts and extend exact paired moments with units, before a
physical adapter or broad source syntax.
