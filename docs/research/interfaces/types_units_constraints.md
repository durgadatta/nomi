# Units And Constraints: Meaning Is More Than A Number

> Status: quantity evidence and proposed constraint/solver separation.

## Evidence And Pressure

The SI Brochure distinguishes quantities, numerical values, and units. This
is a primary metrological reference, not a specification of a programming
language's numeric representation.
[BIPM brochure](https://www.bipm.org/documents/d/guest/si-brochure-9-pdf).

Two numerically equal values can describe different quantities. A time point
is not a duration; an affine temperature scale is not handled by multiplying
all values; a currency amount also needs currency and rounding policy. These
are modelling obligations, not reasons to invent a suffix for every unit.

## Nomi Normal Form And Placement

Use nominal values and ordinary explicit conversions. Keep the existing
`where` predicate a pure validity check. It neither changes units nor finds
values that satisfy a relation. Decoding user-entered quantities should report
type, unit, range, and cross-field errors as expected accumulated failures;
direct invalid construction remains a contract violation.

Dimensional analysis, interval uncertainty, symbolic constraints, and exact
decimal policy need distinct library/type contracts. A general solver takes
a model and a budget, not an executable `where` predicate presumed invertible.
Unit inference may help users only if diagnostics explain the actual mismatch.

**Adapt:** explicit quantity identity and locally inspectable constraints.
**Defer:** implicit conversions and unit syntax. **Reject:** adding/subtracting
values because their host representations are both floating-point numbers.

## Discriminating Experiment

Compare nominal constructors with a quantity-library proposal on distance/time,
absolute temperature/difference, and two currencies. Include overflow, rounding,
unknown units, and impossible intervals. Inspect a generated input form and
schema: omitted dimensional/cross-field rules must be reported, not advertised
as enforced. The user payoff is an error naming the mistaken concept rather
than a generic failed multiplication.
