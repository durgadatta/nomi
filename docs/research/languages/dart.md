# Dart

> Status: comparative evidence; scope is patterns.

## Observe

Dart patterns cover matching and destructuring, including object patterns that
access getters. This allows patterns to span more than inert structural data.
[Primary reference: patterns](https://dart.dev/language/patterns).

## Judge And Pay

**Adopt** concise structural decomposition. **Adapt** it to Nomi's explicitly
bounded pattern grammar and transactional captures. **Reject** getter-driven
or arbitrary user behavior during structural matching in the accepted target.
Boundary decoding must happen before matching owned values.

Nomi loses some useful destructuring of host objects. It also limits pattern
binding outside match rather than proliferating shorthand statements. The cost
is longer code for certain object integrations, so adapters need readable
ordinary accessors and explicit classification rather than magic patterns.

## Test

Create a host object whose getter increments a counter. Convert it explicitly
at the host boundary; then require repeated Nomi matching not to call the
getter again. Exercise failed arms to ensure captures never leak. See
[patterns](../features/patterns.md), [decoding](../features/decoding.md), and
[patterns.nomi](../../design/targets/patterns.nomi).
