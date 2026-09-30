# MATLAB

> Status: comparative evidence; scope is compatible array sizes.

## Observe

MATLAB specifies compatibility rules for array operations, including expansion
of singleton dimensions. Shape agreement is therefore part of the operation,
not incidental container bookkeeping.
[Primary reference: compatible array sizes](https://www.mathworks.com/help/matlab/matlab_prog/compatible-array-sizes-for-basic-operations.html).

## Judge And Pay

**Adopt** documented shape algebra. **Adapt** broadcasting to named Nomi array
operations before assigning it default scalar punctuation. **Reject** letting
an implementation choose shape behavior from its host numerical library.

Named operations cost familiar compact notation and may frustrate numerical
users. That tradeoff should be measured on actual matrix code rather than
decided through a dislike of symbols. Any later operator surface must preserve
the distinction between matrix operations, elementwise operations, and scalar
arithmetic.

## Test

Write a shape table for scalar, vector, row, column, empty dimension, and
incompatible matrix inputs. Require precise expected shapes or errors and
matching CLI/browser results. The current
[numeric fixture](../../design/targets/numerics.nomi) only pressures decimal
rounding; it is not array conformance. See [numerics](../features/numerics.md).
