# R

> Status: comparative evidence; scope is the R language manual.

## Observe

R uses promise-based argument evaluation and supports vector recycling.
These mechanisms serve a statistical, vector-oriented environment, but differ
from simple eager scalar-call expectations.
[Primary reference: language definition](https://stat.ethz.ch/R-manual/R-devel/doc/manual/R-lang.html).

## Judge And Pay

**Adopt** numerical and tabular work as first-class user pressures. **Reject**
implicit recycling and delayed ordinary arguments as Nomi defaults. **Adapt**
vector operations to explicit shape-aware library calls with stated mismatch
behavior.

This costs terse exploratory formulas and domain-specific argument capture.
Nomi cannot replace those with a generic List API and declare data science
solved. Missing observations, units, table schemas, and plotting need explicit
library contracts; eager evaluation is only one part of the story.

## Test

Add length-three and length-two vectors, then compute a mean containing a
missing observation. Require explicit mismatch and missing-data policies,
not backend-dependent recycling or a silently discarded value. Compare the
verbose call form with an intentionally scoped statistical proposal only
after these laws exist. See [numerics](../features/numerics.md) and
[collections](../features/collections.md).
