# Data Source Forms

> Status: primary-source comparison and original Nomi hypotheses; not a specification.

[Dossier](README.md) · [Execution](execution_models.md) ·
[Synthesis](nomi_candidates.md) · [Notation](../notation_atlas.md)

## Literal Syntax And Its Cognitive Contract

These are representative fragments, not standalone tested programs. Definitions
of `df`, schemas, imports, packages, and storage are intentionally omitted.
The important comparison is **what the reader must know to interpret the form**.

| System / primary evidence | Representative form | Relationship compressed | Critical cost; possible Nomi lesson |
| --- | --- | --- | --- |
| [R formula](https://search.r-project.org/R/refmans/stats/html/formula.html) | `y ~ x * z` | Response, terms, interaction. | `*` is not numeric multiplication here; formula carries an environment. Prefer an explicit model value with a visible binding context. |
| [dplyr](https://dplyr.tidyverse.org/articles/programming.html) | `summarise(df, total = sum(.data$amount))` | Column names evaluated in a data mask. | Data and lexical names can collide; forwarding uses another notation (`{{ x }}`). Keep row/schema scope inspectable. |
| [data.table](https://rdatatable.gitlab.io/data.table/articles/datatable-reference-semantics.html) | `DT[quantity > 0, .(total = sum(amount)), by = customer]` | Rows, projection, grouping in three slots. | Dense positional roles; `:=` updates by reference. Distinguish operation from ownership and mutation. |
| [pandas indexing](https://pandas.pydata.org/pandas-docs/stable/user_guide/indexing.html) | `df.loc[df["quantity"] > 0, "amount"]` | A labeled-axis selection and mask. | Label alignment differs from position; don't let a list-looking value conceal a key join. |
| [pandas CoW](https://pandas.pydata.org/docs/user_guide/copy_on_write.html) | `df.loc[mask, "amount"] = values` | Explicit selected update. | pandas 3.0 CoW changes old view/copy assumptions; chained assignment is not a route to updating the original. Critique current semantics, not historical folklore. |
| [Polars contexts](https://docs.pola.rs/user-guide/concepts/expressions-and-contexts/) | `lf.group_by("customer").agg(pl.col("amount").sum())` | An expression interpreted in a grouped context. | Context affects cardinality; `Expr` is not an arbitrary row callback. Favor expression values before quoting callbacks. |
| [Excel LET](https://support.microsoft.com/en-us/excel/functions/let-function) | `=LET(q,2,p,400,q*p)` | Local names inside a cell formula. | Cell placement is separate from variable scope; make intermediate names useful outside a debugger. |
| [Excel LAMBDA](https://support.microsoft.com/en-us/excel/functions/lambda-function) | `=LAMBDA(q,p,q*p)(2,400)` | Parameterized reusable calculation. | Workbook naming/inspection differ from lexical modules. Local functions and navigation should share one contract. |
| [Excel FILTER](https://support.microsoft.com/en-us/excel/functions/filter-function) | `=FILTER(Sales,Sales[Qty]>0,"")` | A dynamic spilled array selected by a Boolean array. | Empty-string fallback is not a typed empty table; spill location is a spatial constraint. Separate result from its view. |
| [VBA Formula2](https://learn.microsoft.com/en-us/office/vba/api/excel.range.formula2) | `Worksheets("Report").Range("A1").Formula2 = "=SUM(B2:B9)"` | A program installs another language in a spatial host. | Two parsers and ambient workbook state; qualify handles and expose generated-source locations. |
| [Power Query M](https://learn.microsoft.com/en-us/powerquery-m/evaluation-model) | `let kept = Table.SelectRows(src, each [Qty] > 0) in kept` | Named transformation steps and record context. | Lists/records/tables/let have lazy evaluation; not every expression does. Named steps are valuable without copying `each` as implicit input. |
| [DAX context](https://support.microsoft.com/en-us/excel/context-in-dax-formulas) | `CALCULATE(SUM(Sales[Amount]), Sales[Region] = "north")` | A measure evaluated under modified filter context. | A measure is not a scalar independent of context; expose context as an argument or inspectable model. |
| [scikit-learn](https://scikit-learn.org/stable/modules/compose.html) | `Pipeline([("scale", StandardScaler()), ("fit", Ridge())])` | Stateful fit/transform stages with named parameters. | Construction, training, inference are distinct; `scale__with_mean` is a second name-routing convention. |
| [Dask graphs](https://docs.dask.org/en/stable/graphs.html) | `delayed(score)(delayed(load)(path)).compute()` | Deferred dependencies followed by execution. | A normal-looking call builds a graph; input identity and side-effect assumptions remain user obligations. |
| [xarray](https://docs.xarray.dev/en/stable/user-guide/computation.html) | `a + b` with named dimensions/coordinates | Alignment and broadcasting by axis identity. | Default arithmetic aligns shared coordinates by intersection; names alone don't establish units or complete coverage. |
| [JAX tracing](https://docs.jax.dev/en/latest/jit-compilation.html) | `jax.jit(f)(x)` | Staging numeric operations for an execution backend. | Python effects during tracing aren't replayed as mathematical operations. Explicit staging matters more than concise decorator syntax. |
| [Ibis](https://ibis-project.org/tutorials/basics) | `t.filter(t.quantity > 0).execute()` | Deferred relational expressions with backend execution. | Backend equivalence, errors, and preview execution need a declared policy; method chains don't guarantee purity. |
| [q](https://code.kx.com/q4m3/9_Queries_q-sql/) | `select total:sum amount by customer from sales where quantity>0` | Relational work over column-oriented ordered tables. | Familiar SQL appearance can hide different ordering rules; retain the physical/logical distinction. |
| [jq 1.8](https://jqlang.org/manual/) | `.[] \| select(.quantity > 0) \| .amount` | Zero/many-result filters composed over JSON. | This pipe is not first-argument insertion and not single-value composition. Decode external JSON before trusting it. |
| [Nushell](https://www.nushell.sh/book/pipelines.html) | `open sales.csv \| where quantity > 0 \| get amount` | Structured values flowing through commands. | External processes still cross byte/text boundaries; types and process authority must remain visible. |
| [Futhark](https://futhark.readthedocs.io/en/stable/language-reference.html) | `map (\x -> x * x) xs` | Regular parallel-array transformation. | Shape and consumption restrictions buy optimization; don't silently apply their restrictions to arbitrary Nomi callbacks. |
| [Souffle](https://souffle-lang.github.io/tutorial) | `reach(x,z) :- reach(x,y), edge(y,z).` | Relations closed under inference. | A fixed point, not a list traversal or ordered task sequence. Relation scope deserves its own model. |

Arrow intentionally has no syntax row: its [columnar format](https://arrow.apache.org/docs/format/Columnar.html)
defines a physical representation/interchange boundary, not row-name resolution,
query laws, or scheduling. Nomi may adapt engines using it without making it the
meaning of `Table` or promising universal zero-copy transfer.

## A. Names Are Part Of The Data Model

Compare three original reductions of the same arithmetic:

```python
# pandas: Series carry index labels as well as values.
report = df.assign(amount=df["quantity"] * df["unit_price_minor"])
report = report.loc[report["quantity"] > 0]
totals = report.groupby("customer", dropna=False)["amount"].sum()

# Polars: column expression objects, not Python row closures.
plan = (
    pl.scan_csv("sales.csv")
    .filter(pl.col("quantity") > 0)
    .with_columns((pl.col("quantity") * pl.col("unit_price_minor")).alias("amount"))
    .group_by("customer").agg(pl.col("amount").sum())
)
```

```r
# dplyr: .data makes the origin of names explicit.
totals <- sales |>
  dplyr::mutate(amount = .data$quantity * .data$unit_price_minor) |>
  dplyr::group_by(.data$customer) |>
  dplyr::summarise(total = sum(.data$amount), .groups = "drop")
```

These do not establish equivalence: missing values, overflow, key treatment,
sorting and source decoding still need policies. pandas label alignment can
reorder an assigned Series; that must not be described as ordinary positional
array assignment. R masking is useful interactive compression but makes a
function's free names harder to inspect. Polars exposes expression construction
well, but a projected scalar and grouped expression don't have identical shape.
Sources: [pandas indexing](https://pandas.pydata.org/pandas-docs/stable/user_guide/indexing.html),
[dplyr programming](https://dplyr.tidyverse.org/articles/programming.html),
[Polars contexts](https://docs.pola.rs/user-guide/concepts/expressions-and-contexts/).

**Nomi hypothesis:** start with immutable decoded rows and explicit `(row) =>`
callbacks for eager lists. For an optimizable plan, use schema-bound expression
data. Never assume translating an arbitrary pure closure is possible: purity
doesn't imply membership in a backend's expression language.

## B. A Join Is A Claim About Identity And Multiplicity

For the reconciliation story, a left join and an anti-join answer different
questions. SQL bags, finite sets, indexed Series and ordered tables are not
interchangeable just because they display rows. The proposed Nomi contract must
declare:

- What identifies an order and a payment? Is a missing key allowed?
- Are repeated keys invalid, intentional many-to-many matches, or reduced first?
- Does unmatched mean no entity, unknown evidence, or a delayed event?
- Does output preserve input order, sort by key, or make no ordering promise?
- Which policies belong to the domain decoder and which to a query operation?

Candidate explicit API: `anti_join(orders, payments, order_key, payment_key,
policy)` followed by a named grouping operation. Reject an implementation that
silently multiplies amounts on duplicate payment keys. A query view should show
the estimated cardinality and the declared key rule, not only connecting lines.
These are Nomi design requirements, not claims that every surveyed engine
performs those checks automatically.

## C. Spreadsheet Forms Teach Spatial Reasoning

Excel's LET/LAMBDA make formulas nameable and reusable; FILTER makes the result
occupy a dynamic region. A VBA routine can write Formula2 into a qualified
range, adding a host-language boundary. `Worksheet.Change` does not represent
formula recalculation and may receive several cells, so it cannot be treated as
a universal reactive dependency signal. Sources:
[LET](https://support.microsoft.com/en-us/excel/functions/let-function),
[LAMBDA](https://support.microsoft.com/en-us/excel/functions/lambda-function),
[FILTER](https://support.microsoft.com/en-us/excel/functions/filter-function),
[Formula2](https://learn.microsoft.com/en-us/office/vba/api/excel.range.formula2),
[Change](https://learn.microsoft.com/en-us/office/vba/api/excel.worksheet.change).

**Critique:** locality is excellent for inspection but fragile when screen
coordinates are mistaken for domain identity. Macros also mix editing authority
with computation and can leave event suppression enabled on failure.
**Nomi extraction:** a table projection with stable entity IDs, explicit derived
columns, invalid draft cells, revision-aware patches and ordinary named
functions. Opening a view must not grant file-write authority or rerun a model.

Power Query adds named transformation history; [folding](https://learn.microsoft.com/en-us/power-query/power-query-folding)
may be full, partial or absent depending on connector/operations. Its
[plan view](https://learn.microsoft.com/en-us/power-query/query-plan) and
[folding indicators](https://learn.microsoft.com/en-us/power-query/step-folding-indicators)
are documented for Power Query Online, not every host.
**Extraction:** source steps and optimized steps should both remain inspectable;
an optimizer's reordered plan must retain diagnostic source attribution.
DAX's context-sensitive measures motivate an explicit observation context,
not another overloaded meaning for Nomi's lexical scope.

## D. Scientific Notation Must Expose Learned State

SciPy supplies numerical algorithms across subpackages, not a single branded
workflow `Pipeline`: [SciPy tutorial](https://docs.scipy.org/doc/scipy/tutorial/index.html).
scikit-learn's pipeline separates fitting and inference, requires intermediate
transformers, and names nested parameters. Putting preprocessing inside each
cross-validation fit helps avoid learning preprocessing statistics from test
data; it does not repair a wrongly chosen temporal split. Its optional cache
clones/caches fitted transformers, not the final estimator.
[Pipeline documentation](https://scikit-learn.org/stable/modules/compose.html).

**Nomi hypothesis:** separate `ModelSpec`, `FittedModel` and `PredictionBatch`.
Fit requires a training partition; inference cannot quietly refit a scaler.
Carry split, seed, environment and feature-schema fingerprints in the inspection
record. Do not call learned parameters immutable evidence of external truth.
Missingness and units deserve types/policies, not implicit NaN coercion.

Named xarray dimensions, Futhark size constraints and JAX staging illustrate
three different solutions: axis identity, shape restrictions, and traced
execution. None should become a universal meaning of an ordinary Nomi call.
Use [the notation atlas](../notation_atlas.md) for contraction and axis forms.

## E. Esoteric Does Not Mean Unprincipled

The useful edge is a **different compositional law**, not unfamiliar glyphs:
jq composes multi-result filters; q combines terse vector/relational operations;
Souffle repeatedly derives facts; Futhark restricts array computations to make
execution tractable. Existing [APL](../languages/apl.md),
[J](../languages/j.md), [BQN](../languages/bqn.md) and
[Uiua](../languages/uiua.md) reviews cover rank, tacit forms and stack models.
Their lesson is to show the rank/axis/stack effect, not to reintroduce rejected
operator sections or hole lambdas into Nomi.

Bounded challenger: compare `group_sum(plan, key, amount)` to a validated
domain expression view. Do not compare only typing speed; require the reader to
identify scope, output shape and failure location after an adversarial change.
