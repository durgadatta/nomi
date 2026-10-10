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

## Phases, Binding, And Rewrite Laws

> Research continuation 2026-10-10: question 12, with numeric theory owned by
> question 9. No quotation, macro, or compile-time parameter syntax is admitted.

[Wolfram](../languages/wolfram.md), [Scala](../languages/scala.md),
[Rust](../languages/rust.md), and [Mojo](../languages/mojo.md) deepen different
parts of this question. Symbolic expression transformation, typed staged code,
constant evaluation, and static type/value parameters are separate mechanisms.
Their primary references and version scopes live in those reviews.

For Nomi, compare these explicit contracts before notation:

| Candidate | Input and output | Admission obligation |
| --- | --- | --- |
| Expression library | Inert domain expression to inert expression/result | Binding identity, declared theory/strategy, assumptions, budget |
| Schema-derived projection | Declared checked metadata to codec/equality implementation | Deterministic derivation, inspectable output, exact provenance |
| Restricted static parameters | Declared type/value facts to specialized implementation | Stage availability, bounded instantiation, fallback/rejection |
| Typed staged transformation | Typed source representation to generated typed source | Hygiene, phase consistency, source maps, authority, termination budget |

Writing an expression value does not run it. Simplifying a symbolic expression
does not establish a universally valid equation. Generating a function does not
invoke that function. Evaluating a build-time constant does not authorize a build
to read a runtime secret. Preserve these distinctions in inspection and errors.

A reusable binding model should compare lexical identities against text names.
When replacing a free variable beneath a binder, either preserve the intended
identity with capture avoidance or reject an unsupported transformation. Do not
reparse display text to reconstruct binding. Distinguish substitution into an
inert expression from injection of a runtime value into generated source.

**Prepared negative cases:** substitute a free `y` beneath a binder also named
`y`; move generated code referencing a local outside that local's stage/scope;
attempt build-time filesystem or host access; specialize on a shape known only
at runtime; introduce a cyclic rewrite; change a generator dependency without
invalidating its output. Require a phase/source-located diagnostic or declared
bounded refusal. A budget-limited result must not be labelled proven normal form.

**Whole-program cost:** compare an ordinary codec builder, a declared derivation,
and a general macro in the same malformed-input report. Include compile time,
code size, debugging steps, formatter output, and the source origin of errors.
Prefer the smallest candidate that answers the actual pressure. Keep research
models removable and avoid making a universal AST the owner of every domain.
The [maintainer guide](../synthesis_guide.md) supplies the shared review worksheet.
