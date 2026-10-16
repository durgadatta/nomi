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

## Matching, Unification And Equivalence Exploration

> Current symbolic research leads; no new symbolic engine,
> extractor, rewrite syntax or inference rule is accepted.

Keep these symbolic questions distinct rather than treating them as
a progression that ordinary `match` must implement:

| Lead | Question to investigate | Prepared discriminator |
| --- | --- | --- |
| Terms, ground terms, patterns and substitutions | Which variables are bindable, and who owns their identity? | Distinct scoped variables with the same display name must not merge. |
| One-sided matching versus syntactic unification | Is only a pattern variable instantiated, or may both terms contain unknowns? | Compare matching `f(x)` against ground `f(1)` with solving `f(x) = f(g(y))`; require explicit cyclic-term/occurs-check policy for `x = f(x)`. |
| Equational unification | Which declared theory permits alternative substitutions? | A commutative operation may admit swapped operands; an ordinary ordered constructor must not inherit that law. |
| Anti-unification | Can a common template expose reusable structure without asserting equality? | Generalize two different expressions while retaining their distinct substitutions; a template is not a proof that the inputs agree. |
| Directed rewriting and normal forms | Which strategy, side conditions and termination evidence justify a result? | Competing rules and a cycle distinguish chosen output, incomplete search and established normal form. |
| E-graphs and extraction | How are justified equivalences retained and one representative selected? | Separate equality evidence, saturation budget and extraction cost; reaching a limit cannot claim complete equivalence exploration. |

The next useful comparison is explicit inert term data plus ordinary library
operations against a scoped symbolic tool. Fix binding identities, assumptions,
rules, strategy, limits and source provenance first. Compare results and
refusals under an exact theory and a numerical profile; no rule may silently
duplicate an effectful computation. Existing
[DSL rewrite comparisons](../dsls/orthogonal_models.md),
[numeric laws](numerics.md#transformations-need-a-stated-theory), and the
[reasoning algebra](../../design/reasoning_algebra.md) already own adjacent
work. Their finite probes do not establish general unification or saturation.

Further reading leads include *Term Rewriting and All That*, Dershowitz's work,
automated reasoning and modern e-graph literature.
Those are acquisition leads, not verified citations or claims of completed
source review. Select a primary source and bounded case
before extending the evidence. Ordinary Nomi patterns remain inert, closed
structural tests; Scala-style extractors and view patterns remain outside the
initial core.
