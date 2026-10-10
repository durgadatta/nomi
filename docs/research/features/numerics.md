# Numerics And Shape

> Status: comparative evidence; exact default Int accepted 2026-10-09;
> richer scalar/array contracts remain open and APIs are illustrative.

User pressure: obtain deliberate, portable numerical results, not accidental
host behavior.

The [notation atlas](../notation_atlas.md) deepens bound indices, axes,
units/frames and algebra laws. [Scientific source forms](../data_workflows/source_forms.md)
add fit/transform and tracing boundaries; DW4/DW5 own the corresponding experiments.
The [AI/ML continuation](../data_workflows/ai_ml.md) deepens supported numeric
transformations, dtype/axis/placement, explicit state/randomness and ML1-ML6.
Its local arithmetic/metadata models do not execute an AD engine or close the
portable numeric contract.

| Evidence | Mechanism | Nomi consequence |
| --- | --- | --- |
| [C](../languages/c.md) | Representation and invalid arithmetic | Specify overflow and checked host narrowing. |
| [R](../languages/r.md) | Vector recycling and missing observations | Explicit shape and missing-data policy. |
| [MATLAB](../languages/matlab.md) | Singleton-dimension expansion | A complete shape agreement table. |
| [Julia](../languages/julia.md) | Explicit broadcast/fusion | Library contracts before optimization or notation. |
| [APL](../languages/apl.md), [J](../languages/j.md), [BQN](../languages/bqn.md), [Uiua](../languages/uiua.md) | Rank-oriented composition | Borrow algebra, not an ambient glyph vocabulary. |
| [Wolfram](../languages/wolfram.md) | Symbolic evaluation | Explicit expression values or a scoped tool. |

Proposed ordinary call, not an accepted stdlib signature:

```nomi
share = decimal.divide(amount, 3, scale=2, rounding=Rounding.HalfEven)?
```

The accepted default Int is mathematical and exact; fixed width is an explicit
representation/host-boundary choice. See the
[scalar contract](../../design/semantics.md#first-product-scalar-contract).
This illustrative Decimal call does not settle Decimal context, Float
determinism, or array broadcasting. Decimal must not secretly mean scaled
binary Float. Currency text is not proof of unit safety.

**Next experiment:** preserve the accepted exact Int law while comparing
representation strategies, checked fixed-width host conversions, and measured
capacity. The former default-width fork is closed; reopening it requires a named
new conflict and ledger revision. Separately prepare the open Float/Decimal/array
golden vectors: values beyond 2**53, explicit narrowing overflow, NaN, negative
zero, non-finite JSON, decimal division/rounding, and shape mismatch. Run supported
vectors on CLI and JS/Wasm; distinguish exact comparison, tolerance, and
profile-specific results. Report representation/performance costs without
making a speed claim beforehand.

Then compare named array calls with one scoped notation on beginner scalar,
production finance, and failure-heavy image-kernel programs. Do not add notation
until representation and laws are settled.

**User-facing gate:** the playground cannot display host-rounded values as
portable Nomi results. [Target](../../design/targets/numerics.nomi).

## Transformations Need A Stated Theory

> Research continuation 2026-10-10: question 9, linked to question 12 for
> symbolic/staged descriptions. No additional numeric theory or array API selected.

The expanded [Wolfram](../languages/wolfram.md), [Haskell](../languages/haskell.md),
[Julia](../languages/julia.md), and [Mojo](../languages/mojo.md) reviews distinguish
rewrite assumptions, interface laws, execution plans, and static parameters.
Their composition is a Nomi research question. A well-typed transformation is
not automatically meaning-preserving under every admitted scalar representation.

| Proposed transformation | Fact that must be established | Negative case |
| --- | --- | --- |
| Cancel `x/x` | Defined division and nonzero x in the stated theory | x is zero or carries unsupported exceptional values |
| Reassociate additions | Admitted associativity under the representation/profile | Finite-precision rounding changes the result |
| Fuse two traversals | Callback order/count/failure laws permit the change | Callback records events or fails at an intermediate step |
| Specialize by dtype/shape | Representation and shape metadata are available at that stage | Shape only arrives from runtime external input |
| Increase a precision label | A representation operation, without invented input accuracy | Already-rounded input cannot recover discarded information |
| Replace an expression by a normal form | Strategy terminates within its declared theory/budget | Rules cycle or different strategies reach different forms |

**Prepared comparison:** exact rational-expression data, finite-precision scalar
execution, and effectful array callbacks receive the same apparent algebraic
identity. Require each candidate to state where the identity is valid, conditional,
or refused. Do not compare all three using an oracle derived from host Float.
Keep declared symbolic assumptions separate from measured observations and
uncertainty models. A cancellation of one uncertain source with itself is a
provenance question as well as arithmetic; the
[shared-origin comparison](../notation_atlas.md#correlated-uncertainty-shared-origin-is-part-of-the-model)
owns that extension.

For an accepted optimization, preserve values, admitted exceptional values,
invocation/failure traces, shape, and boundary conversions under its declared
profile. Include diagnostic and plan inspection costs. These unexecuted cases
complement the existing AI/ML and notation work rather than selecting a universal
numeric engine. Use the [maintainer guide](../synthesis_guide.md) for the joint
staging/dispatch/resource comparison.
