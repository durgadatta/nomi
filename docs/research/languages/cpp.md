# C++

> Status: comparative evidence; scope is the Core Guidelines' RAII advice.

## Observe

The C++ Core Guidelines recommend tying resources to objects whose destruction
releases them. This separates resource management from scattered manual
release calls; it is guidance, not a complete account of the C++ standard.
[Primary reference: RAII](https://isocpp.github.io/CppCoreGuidelines/CppCoreGuidelines#Rr-raii).

## Judge And Pay

**Adopt** lifetime-bound deterministic release. **Adapt** it to explicit Nomi
`with`/`defer`, independent of GC reclamation. **Reject** finalizers as the
normal resource correctness mechanism and reject assuming exactly-once close
also prevents use-after-close.

Explicit scopes lose some of RAII's compositional object ownership. A Nomi
data object containing a file handle raises an unresolved question: may that
handle escape, and who owns its close? A library-only promise cannot settle
every alias if the language allows unchecked escape.

## Test

Return a reader, capture it in a callback, and send it to a child task from
inside `with`. Specify rejection or a checked ownership transfer for each.
Also combine a body error and release error without discarding either cause.
See [resources](../features/resources.md) and
[resources.nomi](../../design/targets/resources.nomi).
