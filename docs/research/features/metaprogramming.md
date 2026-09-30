# Metaprogramming

> Status: comparative evidence; scoped extensions deferred, ordinary calls first.

User pressure: express domain structure and remove real repetition without
losing meaning, source provenance, or control of authority.

| Evidence | Mechanism | Nomi judgment |
| --- | --- | --- |
| [Racket](../languages/racket.md) | Hygienic macros and expansion inspection | Preserve binding/source context; do not admit ambient syntax yet. |
| [Tcl](../languages/tcl.md) | Uniform commands and substitution | Keep ordinary text distinct from executable code. |
| [Wolfram](../languages/wolfram.md) | Symbolic transformation | Represent syntax explicitly instead of changing ordinary evaluation. |
| [SQL](../languages/sql.md), [C#](../languages/csharp.md) | Domain plans | Plan constructors before scoped query notation. |
| [APL](../languages/apl.md), [J](../languages/j.md), [Uiua](../languages/uiua.md) | Specialized composition | Consider scoped domain notation, not a second global core. |
| [HCL](../languages/hcl.md) | Host-defined description phases | Construction and execution must remain separate. |

The long form is an ordinary data structure plus functions operating on it.
For a query: source plan, filter expression value, projection, inspect, execute.
For symbolic math: explicit variable, constant, and operation nodes. There is
no accepted Nomi quotation/macro syntax to demonstrate here.

Generated codec or equality metadata should be an inspectable declared
projection; that does not require arbitrary user macros. Costs of deferral
include verbose builders and fewer abstraction opportunities. A scoped tool
can be justified only with hygiene, typed expansion, source maps, formatter,
sandbox budget, declared capabilities, and removal criteria.

**Experiment:** compare calls against a hypothetical scoped form for a beginner
filter, production join, and failure-heavy symbolic transform. Count recognition
rules, not just characters. Require identical plan/value semantics and exact
expanded error locations. Reject shorthand that merely duplicates core acts.

**User-facing gate:** playground inspection shows expansions and authority
before execution; unsupported notation never appears as a runnable sample.
[Tooling target](../../design/targets/tooling.nomi).
