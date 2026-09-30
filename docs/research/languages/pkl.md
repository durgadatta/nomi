# Pkl

> Status: comparative evidence; scope is templating and constraint diagnostics.

## Observe

Pkl combines configuration templates, type annotations, and constraints.
Its introduction demonstrates diagnostics that show both a constraint and the
value supplied by an amending module.
[Primary reference: introducing Pkl](https://pkl-lang.org/blog/introducing-pkl.html).

## Judge And Pay

**Adopt** reporting where an expectation originates and where it was violated.
**Adapt** reusable configuration to Nomi data and ordinary functions. **Defer**
amendment/inheritance notation rather than introduce a second object model.

Nomi may require more explicit construction for large configuration families.
It must compensate with readable defaults and useful errors, while keeping
missing fields distinct from malformed provided fields. Defaults cannot become
a hidden coercion policy or mask an unknown key.

## Test

Decode an omitted defaulted field, an explicitly invalid value, and an unknown
field. Require different outcomes and both declaration/input locations where
available. Compare a configuration builder with a template without admitting
new syntax yet. See [decoding](../features/decoding.md),
[modules/tooling](../features/modules_tooling.md), and
[boundaries.nomi](../../design/targets/boundaries.nomi).
