# Language Redesign Frontiers

> Status: primary-source research and proposed experiments; no target extensions accepted.

Consulted 2026-09-30. This deepens the [design-first agenda](../design/redesign_agenda.md)
after [cognitive foundations](cognition.md) and [interface threads](interfaces/README.md).
The selected references expose design forks; they are not a complete inventory
of modern language research. Historical mechanisms are deliberately included
where they challenge a contemporary default.

## 1. Incomplete Programs Have A Semantics Question

Hazel models missing/erroneous parts with typed holes and supports defined
partial results in its language/editor model. The project and its 2023 paper
on live pattern matching are primary evidence, not a transferable guarantee
for recovered Nomi syntax.
[Project](https://hazel.org/),
[Pattern paper](https://hazel.org/papers/peanut-oopsla2023.pdf).

**Fork:** non-executable drafts with a last checked snapshot versus formally
typed partial computations that can run supported portions. The second can
reveal useful feedback but needs stuck/unknown results, effect isolation, and
coverage reasoning about future fillings. Nomi must not execute a parser's
guessed recovery node as if it were intended source.

**Experiment:** remove an invoice function body, introduce a branch type error,
and leave a network target incomplete. Compare last-good inspection with a
typed-hole tool spike. Require unknown/stuck provenance and no unauthorized
effect. Do not reuse `_`: the existing wildcard contract remains intact.

## 2. Higher-Order Effects Need A Real Type Model

Leijen's updated 2013 Koka report and the living Koka guide describe function
effect types and polymorphic effects; map is a concrete example of a callback
determining an operation's effects. Koka's broader effect/control model is not
identical to Nomi's capability requirements or abnormal completion channels.
[Report](https://www.microsoft.com/en-us/research/publication/koka-programming-with-row-polymorphic-effect-types/),
[Guide](https://koka-lang.github.io/koka/doc/kokaspec.html).

**Fork:** pure-only collection callbacks versus effect-polymorphic callbacks.
The latter saves loops but requires effect variables, substitutions, closure
capture rules, and useful mismatch diagnostics. No `uses` declaration grants
authority; no empty world-effect row proves termination or absence of panic.

**Experiment:** type map/fold, map_error, and run_scope under both policies.
Include a mutable capture, a clock read, a cold task, and an escaping borrowed
handle. [The function proposal](../design/function_contracts.md) owns the
contract analysis; notation remains unaccepted.

## 3. Editable Projections Need Update Laws

Foster, Greenwald, Moore, Pierce, and Schmitt's POPL 2005 paper constructs
bidirectional tree transformations with explicitly related get/putback
behavior. This is the checked conference version, not the later journal date.
It acknowledges domain-specific limits, including difficult relational updates.
[Primary paper](https://www.cis.upenn.edu/~bcpierce/papers/newlenses-popl.pdf).

**Fork:** read-only views with explicit commands versus bidirectional editing
over a supported subset. For a candidate Nomi projection, test that putting
back an unchanged view preserves the source, and viewing an admissible committed
update yields the requested view. These are proposed obligations within a
declared domain, not guarantees for every diagram or arbitrary function.

**Experiment:** quantity literal edits, row reordering, filtered-out rows,
comments, computed totals, and ambiguous inverse edits. A total can correspond
to many input combinations; ask rather than silently solve or rewrite one.

## 4. Incrementality Is An Artifact Contract

Rust's compiler development guide describes dependency queries and red-green
validation for cached results. This is compiler incrementality, not authorization
to rerun user effects whenever inputs change.
[Primary guide](https://rustc-dev-guide.rust-lang.org/queries/incremental-compilation.html).

**Fork:** coarse whole-source caches versus dependency-aware typed artifacts.
Nomi needs identities, dependencies, profile/edition/schema versions, and
invalidations before optimizing. Source offsets are insufficient identifiers
after edits; a source hash alone may omit relevant host/compiler inputs.

**Experiment:** change a comment, private body, public effect set, decoder policy,
and host profile separately. Compare cache reuse with fresh analysis and demand
identical resolved contracts and diagnostics. Trace the reason for invalidation;
do not store secrets merely to improve reproducibility.

## 5. Convergence And Coordination Are Different

The 2011 Bloom/CALM paper relates logical monotonicity to coordination requirements
for distributed consistency in its model. It is not a theorem that every
monotone-looking Nomi callback can execute without coordination.
[Primary paper](https://www.cidrdb.org/cidr2011/Papers/CIDR11_Paper35.pdf).

**Fork:** centralized checked transitions versus explicit distributed plans
with consistency/coordination contracts. Learning more facts is different from
making a final decision based on a currently absent fact. A merge can converge
while breaking an invariant; a last-writer display is not a proof of agreement
on application meaning.

**Experiment:** collect job completions versus declare all jobs completed; merge
independent invoice rows versus maintain a capacity limit. Annotate what needs
a closed epoch, coordinator, or explicit consistency policy. Keep this in
library plans and tool explanations before considering actor/distribution syntax.

## 6. Examples Constrain Intent; They Do Not Determine It

Microsoft PROSE synthesizes ranked programs consistent with examples within a
specified DSL. Gulwani's primary account discusses ambiguity and clarification
as part of programming by examples.
[Framework](https://www.microsoft.com/en-us/research/project/prose-framework/),
[Primary account](https://www.microsoft.com/en-us/research/wp-content/uploads/2016/12/pbe16.pdf).

**Fork:** examples only as tests versus examples also as bounded synthesis
input. A generated candidate remains a proposal with a domain, assumptions,
alternatives, and provenance. Example consistency is not correctness on unseen
input; ranking is not evidence of the user's intended rule.

**Experiment:** infer name extraction from two examples deliberately consistent
with two rules. Require a distinguishing question/input before committing a
candidate. Export explicit Nomi source or a scoped model and run independent
tests. Do not embed model guesses into overload resolution or static semantics.

## 7. Unicode Is Part Of Reasoning And Security

UAX31 defines identifier profiles; UTS39 supplies security mechanisms including
confusable detection; UTS55 treats source-code presentation. These living
references require a pinned version/profile before Nomi conformance claims.
[Identifiers](https://unicode.org/reports/tr31/),
[Security](https://www.unicode.org/reports/tr39/),
[Source handling](https://www.unicode.org/reports/tr55/).

**Fork:** narrower source identifiers versus broad Unicode with explicit
normalization/security/presentation policy. UTF-8 alone decides none of these.
Identifier equality, string equality, grapheme navigation, sorting, and visual
similarity are separate contracts. International users pay the cost of an
ASCII-only policy; all users pay the cost of ambiguous display.

**Experiment:** precomposed/decomposed names, mixed-script lookalikes, bidi controls,
combining marks, and IME composition. Use code-point descriptions in fixtures
when display is ambiguous. Test source diagnostics and rename, not just parsing.

## 8. Purity Does Not Bound Resource Consumption

Wasmtime documents configurable fuel and epoch interruption. They are distinct
runtime mechanisms and do not define a universal Nomi instruction-cost model.
[Primary API](https://docs.wasmtime.dev/api/wasmtime/struct.Config.html).

**Fork:** cooperative host deadlines alone versus semantic/profile resource
budgets with interruption support. Pure code can diverge, allocate indefinitely,
or create an enormous explanation. Host calls and cleanup may have different
interruptibility; a budget failure must not pretend release completed.

**Experiment:** pure nontermination, large integer growth, bounded trace overflow,
slow host calls, and cancellation during cleanup. Compare CLI/browser outcomes
under a locked profile. Keep timeout, deterministic step-budget exhaustion,
memory limit, and incomplete cleanup distinct in diagnostics.

## Synthesis And Priority

The strongest crosscutting requirement is **inspectable qualified guarantees**.
Every "checked", "pure", "replayable", "merged", "approved", or "solved"
label needs a scope and limits. This joins the historical cognitive exercise
to modern tooling without making one fashionable mechanism the new core.

Next close function-value/callback metadata, then use it for resource/task and
projection experiments. Typed holes, lenses, synthesis, and distributed models
remain challenger designs. No engine integration, benchmark, solver execution,
or usability experiment was performed for this page.
