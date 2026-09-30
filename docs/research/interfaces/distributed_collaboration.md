# Collaboration: Agreement Is Not Correctness

> Status: selected version-control and CRDT evidence; no distributed core proposal.

## Evidence And Pressure

Git revert records a new change reversing an earlier patch. Automerge's document
API preserves concurrent alternatives on conflicting property assignments and
exposes them through a conflicts API, even when ordinary reading selects one.
[Git revert](https://git-scm.com/docs/git-revert),
[Automerge conflicts](https://automerge.org/docs/reference/documents/conflicts/).

A synchronized document can converge while violating a program invariant. Two
edits that are individually reasonable can combine into an invalid public
signature or inconsistent units. Textual merge, structural merge, and semantic
compatibility are different claims.

## Nomi Normal Form And Placement

Keep collaboration in versioned document/change tooling. Track source revision,
binding identity, author/provenance, and semantic validation. A proposed rename
needs resolved references; a string replacement is not equivalent. Merged drafts
may exist before they are checked, but cannot inherit an old execution approval.

Inspect changes to public types, expected errors, effects, decode policy, and
capability requests before running. A semantic diff summarizes machine facts;
it does not prove behavior equivalent for arbitrary programs. CRDT convergence
is a possible editor transport, not the language's shared-memory semantics.

## Discriminating Experiment

Make concurrent edits to an invoice price and its units, then to a function body
and its declared effects. Compare textual diff with resolved contract diff.
Require explicit conflict/validation state and invalidate previews for an old
revision. The GitHub workflow benefit is reviewing what a program now means,
not merely seeing a clean merge or green formatting check.
