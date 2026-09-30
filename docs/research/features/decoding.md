# Decoding And Constraints

> Status: comparative evidence; strict boundary accepted, codec details proposed.

User pressure: reject malformed external input with all useful independent
paths before it becomes an owned value.

| Evidence | Mechanism | Nomi judgment |
| --- | --- | --- |
| [TypeScript](../languages/typescript.md) | Static narrowing | A static claim does not replace runtime validation. |
| [CUE](../languages/cue.md) | Constraint unification | Retain schema information, not general binding unification. |
| [Nickel](../languages/nickel.md) | Boundary contracts and blame | Explain expectation and offending value. |
| [Pkl](../languages/pkl.md) | Defaults/templates with constraints | Distinguish omission from invalid provided input. |
| [Dhall](../languages/dhall.md) | Total typed configuration | Runtime validation is not termination or authority safety. |

```nomi
raw = json.parse(text)?
input = BatchInput.decode(raw)?
```

Parsing establishes format; decoding establishes domain ownership. These
operations return different error types and need explicit mapping in an outer
Result. Value wrappers remain explicit in constructed boundary examples.
Defaults are not coercions. Closed decoding rejects unknown keys; explicit
version policy is needed for forward-compatible services.

The overall target uses JSON with integer ages, not CSV with an unspecified
text-to-Int conversion. A batch wrapper retains `$.customers[index].field`
paths and accumulates independent errors before any network request. Semantic
eligibility filtering happens later and is not malformed-input rejection.

**Experiment:** valid object, two independently invalid fields, and nested batch
with missing/extra keys. Add a normalization that can empty a value and require
validation after that transformation. Compare strict decoding with explicit
field adapters; never silently add coercion. Test schema export of arbitrary
predicates and report non-projectable portions.

**User-facing gate:** playground/editor diagnostics preserve exact input paths
and source ranges, with no partially constructed batch or hidden host request.
[Target](../../design/targets/boundaries.nomi).
