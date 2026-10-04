# Numerics And Shape

> Status: comparative evidence; numeric defaults remain open, APIs illustrative.

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

Do not infer a default Int width, wrapping overflow, Decimal context, Float
determinism, or array broadcast from this spelling. Decimal must not secretly
mean scaled binary Float. Currency text is not proof of unit safety.

**Experiment:** candidate A arbitrary-precision default Int versus candidate B
checked fixed-width default Int; separately specify explicit fixed-width host
conversions. Produce golden vectors for values beyond 2**53, overflow, NaN,
negative zero, non-finite JSON, decimal division/rounding, and shape mismatch.
Run identical vectors on CLI and JS/Wasm and report representation/performance
costs without making a speed claim beforehand.

Then compare named array calls with one scoped notation on beginner scalar,
production finance, and failure-heavy image-kernel programs. Do not add notation
until representation and laws are settled.

**User-facing gate:** the playground cannot display host-rounded values as
portable Nomi results. [Target](../../design/targets/numerics.nomi).
