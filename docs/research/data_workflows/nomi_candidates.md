# Nomi Synthesis And Experiments

> Status: candidate design and live bounded experiment order; no accepted new syntax.

[Dossier](README.md) · [Source evidence](source_forms.md) ·
[Execution evidence](execution_models.md) · [Notation](../notation_atlas.md)

## The Synthesis

The aim is a language where **relationships are cheap to name and expensive to
misinterpret**. Existing syntax supplies names, immutable data, explicit
functions, patterns, Result, effects and resource scopes. Richer models should
initially be values/APIs whose inspection exposes their different laws.

| Pressure | Existing long form | Candidate extraction | Layer / unresolved gate |
| --- | --- | --- | --- |
| Set membership and overlap | Explicit equality checks and Boolean branches. | Finite-set operations; Venn region view over a named universe. | Library/view; equality, enumeration and universe contract. |
| Table transformation | Eager `map`, `filter`, `fold` on decoded rows. | Schema-bound expression values, explicit `TablePlan`, `explain`, `collect`. | Library first; generic/schema/operator and backend-law gates. |
| Dense array calculation | Explicit loops, reduction and index selection. | Named axes; explicit contraction description; validated scoped tensor tool only if needed. | Library versus scoped tool; shape, units, numeric/error laws. |
| Scientific learning | Individually call preprocessing/training/prediction. | ModelSpec versus FittedModel with partition evidence. | Library; learned-state, reproducibility and resource contracts. |
| Scheduled output | Manually inspect inputs, run tasks, store result/history. | Typed ports, explicit partition, attempt record and publication protocol. | Library/tool; persistence, cache and uncertain-effect state. |
| Biological/chemical structure | Lists of atoms/edges or reference-coordinate records. | Validated domain models plus textual and graphical projections. | Domain library/scoped importer; reference/model version and error paths. |
| Explanation/argument | Prose reasons and manually linked evidence. | Typed claim/evidence/attack graph; rendered inference view. | Tool; acceptability is not truth, proof status must remain explicit. |

These are original proposals inferred from the evidence, not features accepted
by borrowing another system's prestige. The four-layer admission discipline
in [the design skill](../../../.agents/skills/nomi-language-design/SKILL.md)
still applies. A view is a projection, not a fifth core syntax layer.

## Concrete Surface Fork: Eager Callback Or Expression Data

```nomi
# Accepted target forms; proposed standard-library contracts.
amounts = rows |> map((row) => row.quantity * row.unit_price_minor)
total = amounts |> fold(0, (sum, amount) => sum + amount)

# Candidate library form, NOT accepted exports or a grammar extension.
quantity = columns.int(schema, "quantity")?
price = columns.int(schema, "unit_price_minor")?
amount = expressions.multiply(quantity, price)?
plan = tables.with_column(source, "amount", amount)?
description = tables.explain(plan)
```

The first executes ordinary callbacks. The second constructs validated data;
it has no implicit lambda quotation. The alternative is a scoped query language
with dedicated row bindings. Don't claim the library baseline wins until joins,
windows, schemas and failure-heavy examples have been compared.

Reject global `where` reuse, `_` hole arguments, or a second meaning of `|>`.
If a future scoped tool uses foreign punctuation, it must own its parser,
edition, binder rules, diagnostics, formatter and expansion mapping. A string
passed to an ordinary call is easy to add but not automatically a good editor
interface; diagnostics must map offsets back to the source literal.

## Structured Data Comparison Showcase

> Candidate application retained from the earlier brief, integrated 2026-10-16.
> This extends DW1-DW3; no comparison tool or new connector is implemented here.

The brief proposes a practical regression/reconciliation tool: compare source A
and source B, explain common and one-sided records, and drill down to changed
fields. It is a useful pressure program for ordinary data, callbacks, constraints,
failure and reporting. It does not replace the first calculation/JSON-report
release or select a dataframe/query language.

Retain the broader application scope in layers:

| Layer | Candidate capabilities | Contract needed before implementation |
| --- | --- | --- |
| Sources | CSV, Excel, Parquet and later connectors | Explicit format/schema conversion, original row/cell provenance, resource and host capability requirements. |
| Alignment | Configured primary/composite keys, column mapping, intersection, A minus B, B minus A | State whether membership compares keys, full rows, sets or bags; duplicate and missing-key policies cannot be guessed. |
| Comparable values | Per-column transforms, projected values, custom equality, date/day-aware comparison | Preserve raw and normalized values; declare units, time zone/calendar, missingness and equality laws. Approximate equality must not silently become a hash/set identity. |
| Workflow | Preprocessing/postprocessing hooks and versioned configurations/results | Callback order/effects, failure policy, source snapshots, policy identity and invalidation; postprocessing cannot silently change the comparison basis. |
| Review and output | Summary, row/column drilldown, machine report and polished email-style rendering | Explain each difference back to inputs and policy; encoding, rendering, saving and actual message delivery are separate operations. |

**First bounded fixture (prepared, not executed):** compare two already-decoded
in-memory lists under a declared unique Text `id` policy and exact Int `amount`:

```text
A = [("a", 100), ("b", 200), ("d", 400)]
B = [("a", 100), ("b", 250), ("c", 300)]
shared keys       = ["a", "b"]
unchanged keys    = ["a"]
changed fields   = [("b", "amount", 200, 250)]
A-only keys      = ["d"]
B-only keys      = ["c"]
```

This prepared policy orders shared/A-only results by A and B-only results by B.
Reverse an input and require only the corresponding order to change. A duplicate
`"b"` or missing key must produce a path-addressed policy failure before any
successful comparison report; do not overwrite or multiply rows. A whole-row set
comparison would put the two `"b"` rows in different one-sided sets, so it must
be a separately selected policy rather than an alternate label for key alignment.

Add independent cases for mapped columns, explicit normalization, missing cells
versus absent rows, and instants that cross a local calendar-day boundary. Keep
the original values and selected time-zone basis available for explanation.
Compare eager ordinary functions with the existing schema-bound expression/plan
candidate under the same policies. Inspect values, errors, invocation traces and
source paths; do not add connectors, UI or notation to answer a policy question.

After that comparison, choose one connector and verify its independent conversion
fixtures on an actual host before adding another format. Rich drilldown,
configuration versioning and rendering remain later application pressures. A
rendered email summary does not send mail. Existing
[function contracts](../../design/function_contracts.md),
[table question](../open_questions.md#8-tables-and-query-plans), and
[delivery roadmap](../../orientation/project_roadmap.md) own admission and priority.

## Comparison As A Policy-Qualified Judgment

> Interpolation and extrapolation, 2026-10-16. Prepared research expectations,
> not a result schema, implemented comparison API or new equality law.

The [canonical synthesis](../../design/synthesis.md#extend-the-earlier-brief-while-preserving-the-core)
connects this application to shared binding, carrier and evidence responsibilities.
Keep four questions explicit: which rows align; which raw fields differ; whether
those differences satisfy a selected policy; and whether all requested work
completed. A single `equal` Bool would conceal useful distinctions.

For the preceding A/B fixture, compare exact assessment with a declared absolute
amount tolerance of 50. The unchanged row remains `a`, and `b` still has the raw
change `200 -> 250`. Exact assessment rejects that change; the tolerance policy
accepts it. The one-sided `d` and `c` remain one-sided under both assessments.
An overall acceptance verdict additionally needs an explicit one-sided-row
policy; tolerance alone cannot supply it. No tolerant assessment changes Int
equality or silently drops the original difference.

The [target-only ordinary function](../../design/targets/research/data_collections.nomi)
supplies a concrete long form for pairwise amount acceptance. It requires no
new pattern, implicit subject, operator or callback convention. Its prepared
oracle also exposes `0 ~ 40` and `40 ~ 80` but not `0 ~ 80` at tolerance 50.
Here `~` is explanatory notation only. Do not use this predicate as a hash-key
equivalence or build grouping by chaining accepted pairs without a separate
clustering/order policy.

| Activity or change | Required observation | Existing owner |
| --- | --- | --- |
| Compare valid snapshots under exact policy | Raw changes and one-sided rows match the literal oracle; no effects needed after inputs are owned | DW1-DW3, ordinary data/functions |
| Reassess under tolerance 50, then 49 | Raw `b` difference persists; its acceptance changes from true to false; source rows stay untouched | Generic callbacks and explicit policy/revision basis |
| Change B's `b` amount from 250 to 251 | The old tolerance-50 assessment cannot be reused; recomputation rejects the difference | DT dependencies, identity and invalidation |
| Introduce a duplicate `b` key | Alignment fails with both original paths; no successful or partially trusted comparison | Decode versus application-policy failure |
| Inspect, render, then deny save | Inspection needs no file/network grant; rendering does not send; denied save leaves the owned comparison available | Effects/capabilities and host outcome handling |
| Compare a stream prefix | Report observed coverage and unfinished state. Under declared positional alignment, a concrete mismatch can refute equality early; agreement needs both ends before a complete equality claim | Stream demand and resource/task completion |
| Receive a proposed projection from an AI tool | Preserve proposal origin, policy/context and independent test/check results; applying it creates a new assessment basis | Existing AI proposal, evidence and authority owners |

The bounded experiment should compare explicit eager calls with inert expression
data using these same expectations. Observe invocation count/order, values,
failure channels, raw paths and policy identity. A pure callback label alone
does not license reordering or fusion when failure/termination can differ.
Define diagnostic and view specimens that distinguish malformed input, duplicate
keys, an ordinary unaccepted difference, incomplete work and refused export.

The longer-term candidates are portable descriptions, exact incremental reuse,
prefix-qualified streaming observations and proposed policies. They remain
separate forks with the falsifiers in the synthesis. None requires a universal
comparison protocol, contextual expression syntax, symbolic unification inside
`match`, or an extra semantic Core node. No new comparison experiment has run
in this design continuation.

## Proposed Contracts Before Implementations

The following is **metalanguage**, not accepted Nomi type or effect syntax:

```text
TableExpr[Schema, Output, Cardinality, NullPolicy]
  = validated operator data bound to a schema identity, never a live reader
TablePlan[Schema]
  = immutable source description + typed operations + policy + source mapping
collect(plan, grant, limits)
  = Result[OwnedTable, ExecuteError]; no hidden reuse of prior permission
FittedModel
  = learned state + feature schema + training/split/environment evidence
WorkflowSpec
  = typed port/dependency description + operation versions + policy
AttemptRecord
  = partition + input snapshots + attempt identity + observed outcomes
PublicationState
  = Pending | Confirmed | Rejected | Uncertain
```

Unclosed gates: generic/protocol spelling, pure/effectful callback contracts,
typed schema reflection, higher-order region retention, latent task effects,
serialization and backend determinism. These examples must not be cited as
proof that Nomi already has any of those contracts.

## Bounded Experiments

This is the live local order; the [redesign agenda](../../design/redesign_agenda.md)
owns project-wide precedence. Existing open questions 2/3/4/7/8/9/12/17 own the
underlying forks. No separate implementation backlog is created here.

| ID / priority | Fork and exact deliverable | Adversarial oracle | Accept / stop gate | User-facing result |
| --- | --- | --- | --- | --- |
| DW1 / first | Write typed contracts for eager callbacks, schema-bound expressions and collect in metalanguage; compare two candidate public signatures. | A callback reads a file; expression references the wrong schema; plan retains a reader. | Reject illegal translation/retention before execution; name each open generic/effect gate. No engine work yet. | Hover/inspection can distinguish calculation, description and execution. |
| DW2 | Implement an isolated Python reference model of the reconciliation, comparing eager rows and expression data; no parser change. | README's 2100/1300 oracle; duplicate payment A; unknown amount; changed row order. | Equal values/errors under declared null/key/order rules; immutable plan construction; explain without I/O. Stop if contracts still undefined. | A result can explain an unmatched order without silently inflating money. |
| DW3 | Write the same joins, window and grouped projection using calls versus a fenced scoped-query sketch; supply formatter/diagnostic specimens. | Name collision `quantity`; missing column; scalar/group/window shape mismatch. | Two-reader scope/cardinality/error-location trial plus accessibility transcript; no choice based only on character count. | A beginner can identify where every column comes from. |
| DW4 | Compare loops, named-axis operations and explicit contractions for a 2x3 times 3x2 matrix. | Expected `[[58,64],[139,154]]`; swapped axis identity; mismatched contraction size; unknown unit. | Exact integer oracle and source-local shape errors; numeric reassociation policy explicit; readable text alternative to glyphs. | Tensor view reveals contracted and surviving axes. |
| DW5 | Model train/fit/predict lifecycle with an explicit temporal split and fitted scaler. | Held-out outlier must not change training statistics; incompatible schema rejected. | State transitions inspectable; no hidden refit; no unsupported reproducibility promise. | Model report distinguishes specification from learned artifact. |
| DW6 | Build a fake-runner state model for daily publication, not a real service integration. | Crash after send/before acknowledgment; changed input; revoked grant; late correction. | Distinguish Uncertain from failure; partition/attempt/idempotency keys visible; no implicit replay of external effect. | Backfill preview states what will rerun and what needs reconciliation. |
| DW7 | Compare finite-set calls and a Venn projection with a named universe, plus typed chemical/reference models. | Complement without universe; nonmatching reference versions; invalid ring link or unbalanced stoichiometry. | No false proof, clinical inference or automatic simulation; lossless textual model and error paths. | Diagrams make relationships visible while limitations remain inspectable. |
| DW8 / last | Only for a settled slice: independent value/error fixtures, formatter and source mapping, CLI/browser implementation plan. | Native/browser mismatch, stale source revision, denied authority, resource escape. | Existing tests/supported playground samples remain green; new sample only after conformance, not from aspirational files. | A small honest playground experience, not a menu of unsupported syntax. |

No DW experiment has run in this documentation pass. Numbers are specifications
of future reference checks, not claimed measurements or comprehension results.
If two forms are semantically identical and neither wins comprehension/error
locality, stop at ordinary calls and delete the proposed shorthand.

The [October data/time extension](dependencies_and_time.md) adds DT1-DT5;
[AI/ML](ai_ml.md) adds ML1-ML6; and [cross-domain composition](../domain_composition.md)
adds DC1-DC6. They refine these existing forks rather than mark DW1-DW8 complete.
[Local models](composition_experiments.md) execute selected counterexamples,
not Nomi contracts or foreign-framework integration. The canonical synthesis
continues to own admission order.

## Diagnostics, Formatting And Views

Example terminal diagnostic (candidate):

```text
E-TABLE-KEY: payment key A occurs twice
  input payments[1].order_id and payments[4].order_id
  anti_join policy requires unique payment keys
  no plan executed; choose a domain reconciliation policy before collecting
```

Machine fields: stable code, source spans, input paths, schema identity,
policy identity, phase, related locations, revision and suggestion applicability.
Human views should show named steps, schema/cardinality/null badges, logical and
physical plans, source mappings, run identity and stale/denied states. Keyboard
commands operate on semantic IDs, not pixel coordinates; text and screen-reader
views must expose equivalent relationships. These are acceptance criteria, not
instructions to put tutorial text into the runtime UI.

Formatter baseline: ordinary calls, explicit lambda inputs, multiline named
arguments for large policies, no hidden input aliases. A view edit becomes a
validated patch against a source/model revision. Invalid intermediate drafts
stay drafts; no automatic collect/fit/run occurs on focus or visualization.

## Interactions And Rejected Shortcuts

| Neighbor | Required interaction | Reject |
| --- | --- | --- |
| Binding / data | Immutable descriptions; explicit entity/snapshot/schema identity. | Column names silently captured from an unrelated lexical variable. |
| Result / absence | Decode/plan/execute errors separate; missing cell represented under a policy. | NaN, empty text, None and execution failure treated as one value. |
| Effects / authority | Description construction separate from permission and execution. | Cached permission or trace-time side effects used as a runtime guarantee. |
| Resource / async | No handle escaping via closure/plan/trace/Err; lexical tasks stay lexical. | Durable workflow hidden behind ordinary cold `Task`. |
| Numeric laws | Overflow, float ordering, units and reduction policy inspectable. | Optimizer assumes all addition is associative. |
| Modules / tooling | Versioned scoped languages and engine profiles; source-local diagnostics. | Global punctuation extension or macro quoting by convenience. |
| Provenance | Observation identifies revision/run; uncertainty explicit. | A pretty graph presented as proof of correctness. |

The target [category fixtures](../../design/targets/research/README.md) show the
call-based baseline. Their `lab.*` contracts are proposals and can be removed
without changing the current grammar, browser assets, runtime registry or
packaging. This preserves the research project's optionality.
