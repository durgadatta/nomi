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
