# Dhall

> Status: comparative evidence; scope is safety and import integrity.

## Observe

Dhall deliberately restricts recursion to obtain total evaluation for typed
expressions; termination is not a practical time bound. Its imports also have
security policies and optional semantic integrity hashes.
[Primary references: safety guarantees](https://docs.dhall-lang.org/discussions/Safety-guarantees.html),
[language tour](https://docs.dhall-lang.org/tutorials/Language-Tour.html).

## Judge And Pay

**Adopt** separating deterministic evaluation from import authority and resource
limits. **Adapt** integrity to Nomi's manifests and lockfiles. **Reject** claiming
a general-purpose Nomi program is safe configuration simply because it uses
typed immutable values.

Nomi loses Dhall's totality guarantee. A pure recursive computation can still
diverge or consume excessive memory. A configuration profile therefore needs
explicit budgets and grants; the `uses` set alone does not make it safe.
Semantic hashing also requires much more than a source-file checksum.

## Test

Evaluate a pure divergent configuration, an oversized value, and a denied
remote import. Require three distinct diagnostics and no accidental network
grant. Test a stale lock entry independently of a type error. See
[effects](../features/effects.md), [modules/tooling](../features/modules_tooling.md),
and [modules.nomi](../../design/targets/modules.nomi).
