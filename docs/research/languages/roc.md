# Roc

> Status: comparative evidence; Roc is evolving; scope is platform boundaries.

## Observe

Roc separates application code from a platform that supplies the connection to
the outside world. The platform contract is an architectural boundary, not
merely a naming convention for utility functions.
[Primary reference: platforms](https://www.roc-lang.org/docs/main/langref/platforms/).

## Judge And Pay

**Adopt** making host interaction a first-class boundary. **Adapt** this to
Nomi's declared effects and concrete capability grants across CLI and browser
profiles. **Defer** copying Roc syntax or an entire app/platform packaging model
while Nomi's host ABI remains exploratory.

Nomi loses the simplicity of one centrally constrained application architecture
by targeting scripts, notebooks, services, and embedded hosts. Its effect
vocabulary alone will not repair that complexity. Each host profile must state
which capabilities exist, how they are granted, and how unavailable authority
is diagnosed before execution.

## Test

Use [effects](../../design/targets/effects.nomi) with a CLI grant restricted to
one input path and a browser profile with no filesystem grant. Require the
same source contract and distinct, structured denial outcomes. See
[effects](../features/effects.md) and [modules/tooling](../features/modules_tooling.md).
