# Researching And Integrating One Coherent Language

> Status: maintainer/designer research guide, prepared 2026-10-10. Comparative
> evidence and proposed experiments; no new target semantics accepted here.

This is the working entry point for Nomi's developer, maintainer, and language
designer. Use it to turn an interesting mechanism into an informed language
choice. The objective is one language whose parts support the same way of
reasoning as work grows from exploration into shared programs. A collection of
individually attractive features does not establish that coherence.

The broader [vision](../design/vision.md) guides discovery. Current accepted
meaning lives in [syntax](../design/syntax.md), [semantics](../design/semantics.md),
and [industrial contracts](../design/industrial.md). Research can challenge those
choices explicitly. The Python and browser prototypes are replaceable evidence
surfaces; their present capabilities do not bound the language we can investigate.

## Find Your Question

The current selected continuation focuses solely on data/statistics. Start with
the [Statistical Data Interface](../design/statistical_data.md), then its
[primary-system comparison](data_workflows/statistical_objects.md). The
engine-free model checks a named lazy workflow and exact mean decomposition
without observations. Broader statistical families are interface contracts;
distribution/model execution and arbitrary algebraic proof remain open.

| You want to… | Read next | Produce |
| --- | --- | --- |
| Understand the present language hypothesis | [Synthesis](../design/synthesis.md), [decision ledger](../design/decisions.md), [overall program](../design/targets/overall.nomi) | A named pressure or conflict with an existing law |
| Discover mechanisms | [Language reviews](languages/README.md), [families](families.md), [convergences](convergences.md) | A sourced semantic observation with version scope |
| Compare one area | [Feature owners](features/README.md), [semantic matrix](language_feature_matrix.md), [syntax forms](syntax_forms.md) | Alternatives, interaction costs, and a counterexample |
| Resume an unresolved choice | [Open questions](open_questions.md), [registered passes](../orientation/design_pass_workflow.md) | One bounded discriminator under the existing owner |
| Test composition beyond ordinary source | [Interfaces](interfaces/README.md), [domain composition](domain_composition.md), [DSL models](dsls/orthogonal_models.md) | A whole activity, preserving domain-specific meaning |
| Move a settled result into the language | [Admission workflow](#integrate-a-settled-result) | Canonical laws, independent fixtures, and a reversible bridge |

For this pass, start with the eight expanded reviews below. Follow the linked
feature owners for synthesis; they consolidate shared questions rather than
requiring a reader to reconcile eight independent proposals.

## What The Named Languages Contribute

These are selected mechanisms and tensions, not rankings or full language
inventories. The individual reviews carry primary sources, costs, scope, and
prepared cases. “Candidate” means a research alternative, not an accepted API.

| Review | Study in depth | Coherence question for Nomi |
| --- | --- | --- |
| [Mathematica / Wolfram](languages/wolfram.md) | Expression evaluation, held forms, rule strategy, assumptions, binding identity, precision | Can a symbolic domain remain explicit without changing ordinary eager calls? |
| [Haskell](languages/haskell.md) | Demand, currying, classes, inference, IO, roles, linear arrows | Which abstractions survive an eager language, and what laws do their types actually establish? |
| [Scala](languages/scala.md) | Contextual arguments, opaque types, extractors, typed staging, experimental captures | Can supplied behavior and captured authority remain locally discoverable? |
| [Kotlin](languages/kotlin.md) | Sealed states, smart casts, extensions, inline control, invocation contracts, coroutines/Flow | Can friendly APIs preserve stable refinement, return targets, and lifecycle ownership? |
| [Rust](languages/rust.md) | Borrowing, drop limits, coherence, Result, pinning, const evaluation | Which guarantees need a checker, and which need separate operational contracts? |
| [Mojo](languages/mojo.md) | Access conventions, origins, traits, static parameters, typed raising, Python boundaries | Can efficient specialization coexist with a simple ordinary profile and portable meaning? |
| [Julia](languages/julia.md) | Multiple dispatch, specialization, broadcast plans, world age | Can numerical extensibility and interactive change preserve inspectable selection and execution? |
| [TypeScript](languages/typescript.md) | Structural compatibility, refinement, erased assertions, type projections, read-only views | How can tooling convenience coexist with owned-data validation and deliberate public contracts? |

The categories matter. Julia is a numerical/general-purpose alternative;
TypeScript is a typed JavaScript ecosystem language. Neither is simply a newer
Python implementation. Mojo changes native access/staging contracts while
providing Python interoperability. Comparing them solely by syntax familiarity
or a headline benchmark would obscure the actual language choices.

### The Python-Adjacent Comparison Needs Several Axes

Python annotations are not enforced by its runtime. Cython's pure mode adds
static information and compiler-specific functionality to Python-compatible
source, with limits on what that mode can express. Codon's overview names
compatibility differences arising from static compilation, including fixed-width
integer behavior. PyPy's documentation explains how its GC strategy changes
observable finalization timing relative to CPython.
[Primary references: Python typing](https://docs.python.org/3.14/library/typing.html),
[Cython pure mode](https://docs.cython.org/en/latest/src/tutorial/pure.html),
[Codon differences](https://docs.exaloop.io/language/overview/),
[PyPy differences](https://doc.pypy.org/cpython_differences.html).

Use these as adjacent comparators, not additional full reviews in this pass.
Study source compatibility, semantic compatibility, execution profile, foreign
object sharing, installation, and library reach separately. For Nomi, an exact
Int operation, a shared Python object, and a borrowed native buffer need explicit
contracts even if all three appear inside familiar indentation. Measure native
computation and boundary transfer independently. Never promote vendor performance
figures into Nomi evidence without a pinned reproducible experiment.

## The Working Semantic Spine

The current target organizes ordinary computation around values, explicit calls,
owned concepts, structural choice, typed expected failure, and visible world
interaction. That is a working synthesis with accepted laws and unresolved
contracts; it is not a claim that the full target is executable.

| Current intended law or distinction | What a new candidate must account for |
| --- | --- |
| Ordinary call arguments evaluate eagerly, left to right, once | Holding, laziness, retry, macros, and fusion must name their distinct phase/carrier |
| Immutable binding; visible `var`/`set` state changes | Read-only access does not prove deep immutability or absence of aliases |
| Nominal owned data; structural received values; explicit decoding | Type assertions, representation equality, and foreign annotations cannot bypass validation |
| Inert transactional patterns; ordinary classifier calls | Computation hidden in patterns needs a complete challenger contract |
| Option, Result, panic, and cancellation remain distinct | Error convenience must preserve channel, cause, and cleanup ownership |
| Effects describe potential behavior; handles grant authority | Inference, contextual search, and captures cannot manufacture permission |
| List, Stream, and TablePlan have distinct execution meaning | Reuse of a verb must not hide when callbacks run or how many times |
| Default mathematical Int is exact; wider numeric rules remain open | Backend storage and capacity must not silently change arithmetic meaning |
| Exploration can retain unknown facts; checked exports need evidence | Unknown is neither implicit Any nor a proof supplied by a client |

Some laws may be revised by new evidence. Name the affected decision, show the
whole-program consequence, and update its canonical owner. A domain-specific
model can also remain outside the ordinary evaluator: symbolic expressions,
query plans, differentiable descriptions, and documents need not share a
universal executable IR.

### Combinations To Investigate

The named languages need not contribute indivisible packages. Compare coherent
combinations whose boundaries remain explicit:

| Combination hypothesis | What it preserves | What still needs evidence |
| --- | --- | --- |
| Eager ordinary functions plus explicit demand-bearing carriers | Local call timing with deferred streams/plans | Failure, repeat-consumption, retention and capability lifetime |
| Nominal owned data plus structural foreign values | Internal concepts and ecosystem reach | Decoding, alias isolation, versioned adapters and representation cost |
| Ordinary functions plus supplied operation values | Alternate behavior without hidden source-level dispatch | Generic contracts, capture facts, ergonomics and coherent defaults |
| GC ordinary values plus scoped native/resource handles | Simple common values with deliberate external validity | Escape checking, suspension, foreign callbacks and release outcomes |
| Exact scalar meaning plus explicit representations/specialization | Portable meaning with optional optimized execution | Capacity, compilation, conversion and accepted transformation laws |
| Explicit expression/plan data plus inspectable staged tools | Symbolic/domain abstraction without ambient second evaluation | Binding, theory, stage inputs, source provenance and build authority |

These are research hypotheses shaped by the current target, not a selected final
language architecture. A credible broader challenger may revise them. Evaluate
the combination in one activity and explain the smallest extra law it introduces.

## Research One Mechanism Through A Repeatable Loop

1. **Start with an activity.** Describe what a person is creating, understanding,
   repairing, or sharing. Discovery may begin with an unfamiliar mechanism;
   develop the concrete pressure before asking to admit it.
2. **Check the existing owner.** Search the corpus and decision ledger. Reuse an
   open question or registered packet when it fits. Registration organizes mature
   questions; it need not precede discovery.
3. **Record primary evidence.** Identify specification/manual/paper, version or
   retrieval date, actual mechanism, limitations, and what you have not executed.
   Separate language rules, libraries, tooling behavior, and implementation facts.
4. **Write the explicit form.** Express the operation with values and calls or a
   small model first. Name binding identity, evaluation, dispatch, type evidence,
   failure, authority, resources, and stage. Do not start by copying punctuation.
5. **Compare genuine alternatives.** Include the current model and a credible
   challenger, rather than a deliberately inconvenient strawman. Measure what
   each gains and what it gives up.
6. **Challenge interactions.** Use the matrix below and one whole program.
   Count implicit laws a reader must know, not just tokens saved.
7. **Prepare an independent oracle.** Fix inputs and expected values, events,
   diagnostics, cleanup, and revision identity before implementing either model.
   A shared helper in both models can conceal the very mistake being compared.
8. **Execute a bounded comparison when ready.** Distinguish host demonstrations,
   foreign-language executions, Nomi conformance, and human observations. Each
   supplies different evidence. Preserve negative and refusal cases.
9. **Record disposition.** Keep open, adopt the idea, adapt its placement, defer,
   or reject it for the stated audience. Explain the loss and what evidence would
   change the judgment. A well-supported result may need no new syntax.
10. **Integrate or stop.** Update existing evidence and the next exact action.
    Promote only the settled obligations through the canonical workflow below.

### Copyable Candidate Worksheet

Place this in the existing feature owner or matching packet while the question
is active. It is a compact review aid, not a new registry or mandatory document.

Evidence labels describe independent surfaces rather than a single confidence
score. A foreign compiler accepting one example does not establish a language
law across versions; a local model does not establish a Nomi checker; a reader
study does not prove semantic soundness. Record the assumptions and scope of any
formal argument separately, including whether it covers partiality, effects,
aliases, and foreign code.

```text
Activity and deficiency:
Primary mechanism, source, version/date:
Evidence surfaces and limits: documentation / model / foreign run / Nomi checks / formal argument / human observation
Current Nomi law and any explicit conflict:
Explicit long form; proposed convenience if needed:
Candidates and semantic owner/placement:
Binding, evaluation, dispatch, type/phase facts:
Failure, authority, resource, cancellation facts:
Package/revision identity and cross-backend obligations:
Independent inputs and expected observable results:
Costs, diagnostics, formatter, inspection, removal criterion:
Disposition; next discriminator; canonical files affected if accepted:
```

## Where The Features Must Compose

| Interaction | Pressure from the reviews | Discriminator and existing owner |
| --- | --- | --- |
| Evaluation × carrier × failure | Haskell demand; Wolfram held forms; Julia fusion; Kotlin Flow | Count callback events before partial consumption, failure, and repeated consumption; [collections](features/collections.md), questions 7/8 |
| Generics × mutable sharing | Haskell inference; contextual operation values; captured callbacks | Delayed identity retains state across incompatible instantiations; [functions](features/functions.md#polymorphic-sharing-and-generalization), questions 2/3 |
| Dispatch × package identity | Haskell instances; Scala givens; Rust coherence; Julia methods; Mojo traits | Independently authored adapters overlap without a unique winner; [functions](features/functions.md#dispatch-coherence-and-operation-values), questions 3/10/13 |
| Nominality × conversion × aliases | Scala opaque representation; TypeScript structure/readonly; Mojo foreign objects | Equal layout must not bypass decoding or keep hidden mutable aliases; [types/data](features/types_data.md), questions 2/11/13 |
| Effects × capture × scope | Scala capture tracking; Rust borrowing; Mojo origins; Kotlin jobs | Reader escapes through closure, error, container, or task; [resources](features/resources.md), questions 4/5 |
| Staging × binding × authority | Wolfram rules; Scala quotes; Rust const; Mojo parameters | Generated reference escapes scope or build attempts world access; [metaprogramming](features/metaprogramming.md#phases-binding-and-rewrite-laws), question 12 |
| Algebra × representation × optimization | Wolfram assumptions; Haskell laws; Julia fusion; static numeric specialization | Rewrite is invalid for zero, finite-precision values, or effectful callbacks; [numerics](features/numerics.md#transformations-need-a-stated-theory), question 9 |
| Interactive change × existing computation | Julia world age; lexical captures; notebook revisions | Old task and new call identify the definition and context they use; [modules/tooling](features/modules_tooling.md#definition-visibility-during-interactive-change), questions 14/17 |

The table exposes research dependencies. It does not prescribe doing eight new
implementations in parallel. Choose one failed discriminator, close the smallest
contract needed to answer it, and rerun its whole-program case.

## Prepared Whole-Program Comparison

Use one scientific report that imports received observations, validates owned
records, computes a numerical result, explains a symbolic transformation, and
exports a result through a resource scope. Keep its package consumer and an
interactive revision of the calculation in the same study. This is a research
scenario; it does not expand the accepted first-product report contract.

Compare a baseline of explicit values/calls/dictionaries with one challenger at
a time. Do not combine a new dispatch model, numeric theory, lifetime checker,
and macro system and attribute any result to only one of them.

| Fixed case | Required observation before choosing candidates |
| --- | --- |
| Received record has wrong numeric type and unknown tag | Decode paths remain stable; no partially validated owned value is published |
| Values include integer `9007199254740993` | Exact input survives supported transport; a float approximation is named separately |
| Two adapters offer comparison/codec behavior for the same concept | Chosen implementation has an origin, or ambiguity is diagnosed deterministically |
| Two pure array passes become one plan; then callback records visits | Pure result agreement and complete effect/failure traces are separate oracles |
| Symbolic `x/x` is simplified with `x=0` still possible | Transformation refuses, preserves a condition, or states a restricted theory |
| A precision label is increased after binary approximation | No claim that original exact input or measurement accuracy was recovered |
| A reader is captured by a delayed calculation and its body fails | Scope validity, cause preservation, and cleanup attempts remain explicit |
| Function changes after a task starts | Old and new observations identify definition/input revisions; stale evidence is visible |

Add a beginner reading task, a production package task, and a failure-heavy
repair task to the same candidates. The existing [overall target](../design/targets/overall.nomi)
and [growth journeys](../design/synthesis.md#growth-journeys-and-boundary-evidence)
provide baseline pressures. This prepared program is not a benchmark or evidence
of usability; its inputs and traces must be materialized before execution.

### Two Small Pilots With Literal Expectations

These pilots make the first comparison executable without building the entire
scientific report. They are paper oracles prepared here, not executed results.
Put any later model/probe beside its existing feature owner and preserve the
literal records independently of the implementation.

**Evaluation pilot:** input `[1, 2, 3]`; operation A records `A(x)` and produces
`x + 10`; operation B records `B(y)`, fails with a named error at `y = 12`, and
otherwise produces `2*y`. Events are append-only observations, so the callbacks
are deliberately effectful. The candidate contracts, not foreign language
defaults, define the following traversals:

| Declared candidate | Literal expected events | Outcome |
| --- | --- | --- |
| Materialize all A results, then traverse B left to right | `A(1), A(2), A(3), B(11), B(12)` | Named error; no completed result list |
| Traverse each item through A then B, stopping on first failure | `A(1), B(11), A(2), B(12)` | Same named error; different effect trace |
| Demand one item from an explicit fresh stream | `A(1), B(11)` | One consumed value `22`; remaining producer has a declared owner |

The first two agree on the error but are observably different. Fusion cannot be
called semantics-preserving for this contract solely because successful pure
numbers agree. Compare a separate pure/total callback version and preserve its
values before studying optimization cost. Reconsuming the stream additionally
requires a restart/replay/single-use rule; do not infer it from the verb `map`.
Owner: [collections](features/collections.md) and [numeric laws](features/numerics.md).

**Behavior-selection pilot:** two validated identifiers have displayed names
`item2` and `item10`, with integer suffixes 2 and 10. Lexical ordering produces
`[item10, item2]`; suffix ordering produces `[item2, item10]`. Both are intentional.
Explicit operation values must make both selections possible and visible. A
globally coherent single default must explain the alternate path and its cost;
scoped/contextual selection must explain ambiguity and origin. Add an unrelated
adapter import and require the deliberately selected behavior to stay stable.
Independently overlapping two-argument methods need their separate ambiguity
case; neither order here resolves that conflict. Owner:
[dispatch comparison](features/functions.md#dispatch-coherence-and-operation-values).

## Depth Gaps Worth Researching Next

The corpus already covers many of these domains. The gap is often an interaction,
a checked counterexample, or implementation evidence, rather than a missing
language name. These routes extend existing questions instead of creating a
second backlog.

| Underexplored depth | Small next comparison | Owner |
| --- | --- | --- |
| Higher-kinded operations and law evidence | Explicit dictionary for traversal/merge versus a constructor-polymorphic interface; test identity, composition, partiality, and effect order | Questions 2/3; [generic operations](generic_operations.md), [Haskell](languages/haskell.md) |
| Control effects and continuation ownership | Direct callback/Result versus one-shot handled suspension; abandon or resume twice while holding a resource | Questions 4/5/7; [effects](features/effects.md#control-effects-and-continuation-ownership), [resources](features/resources.md) |
| Totality and stronger contracts | Ordinary constrained function versus a proof/termination-backed library contract; preserve a usable partial computation path | Questions 1/2/9/12; [constraints](features/decoding.md), [symbolic/proof models](dsls/orthogonal_models.md) |
| Gradual assurance at a foreign mutable boundary | Checked adapter versus explicit dynamic handle; mutate through a second alias after validation | Questions 2/11/15; [TypeScript](languages/typescript.md), [decoding](features/decoding.md) |
| Borrowing without universal ownership syntax | Immutable copied value versus region-scoped buffer versus borrowed profile; resize, suspend, and transfer views | Question 5; [resource comparison](resource_lifetime.md), [Rust](languages/rust.md), [Mojo](languages/mojo.md) |
| Separate compilation for staged generic code | Declared static inputs versus runtime specialization; change generator/dependency and inspect invalidation | Questions 2/12/13/15; [metaprogramming](features/metaprogramming.md), [modules/tooling](features/modules_tooling.md) |
| Representation choice and cost predictability | Exact scalars plus explicit fixed-width adapters; boxed versus specialized arrays under identical observable laws | Questions 9/15; [numerics](features/numerics.md), [Julia](languages/julia.md), [Mojo](languages/mojo.md) |
| Evolution of running programs | Frozen revision versus explicit refresh versus live lookup; old closure, task, cached result, and migrated data | Questions 11/14/17; [modules/tooling](features/modules_tooling.md), [interaction proposal](../design/interaction_model.md) |

Two primary leads deepen the adjacent frontier. OCaml 5.3 documents effect
handlers with one-shot continuations: repeated resumption is checked dynamically,
while ensuring eventual resumption/discontinuation remains the programmer's
responsibility. Lean distinguishes recursive definitions supported by termination
reasoning from `partial` definitions that remain opaque to its logic. These are
useful challenges to claims that a type/effect annotation alone establishes
cleanup or totality.
[Primary references: OCaml handlers](https://ocaml.org/manual/5.3/effects.html),
[Lean recursion](https://lean-lang.org/doc/reference/latest/Definitions/Recursive-Definitions/).

These are discovery leads, not full new language dossiers or selected Nomi
mechanisms. Also retain the broader human-activity question: can a person predict,
inspect, repair, and share the composed behavior? A proof system, fast compiler,
or clever notation can improve one dimension while making the activity harder.
Use the existing [cognitive](cognition.md) and [interaction](interfaces/composition_cases.md)
protocols where that is the actual unresolved question.

## Composition Corner Cases And Research Quality

The [candidate six-family synthesis](../design/synthesis.md#candidate-primitive-synthesis-and-integration-path)
provides one integration path. Value, Bind, Apply, Choose, Perform, and Scope are
semantic families, not accepted opcodes or a universal domain model. Most
conveniences combine them; lifetime, scheduling, type soundness, numerical laws,
and domain-specific meaning remain obligations. The canonical proposal owns the
composition map, gap receipts, and ordered steps.

The following cases sharpen coverage beyond isolated feature reviews. Existing
owners retain the detailed experiments; these expectations are prepared, not
executed language comparisons.

| Corner case | Required distinction or negative oracle | Owner |
| --- | --- | --- |
| `map` callback returns Err on the second of three inputs | Ordinary map retains three Result elements; fail-fast traversal is a separate contract | Functions, questions 3/6/7 |
| Option of Result versus Result of Option | Missing record, failed lookup and missing payload remain separately matchable | Failure, question 6 |
| Empty input with an effectful callback | Zero runtime calls do not establish static purity | Functions/effects, questions 2/4 |
| Read-only covariant view retains a mutable producer alias | Type-safe reading is not immutability, freshness or permission to write | Types/data, question 2 |
| Protocol includes generic methods or a Self-dependent result | Erased runtime dispatch needs its own supported signature; ordinary conformance does not establish it | Functions, questions 3/10 |
| A key changes equality/hash behavior after insertion | Equality/hash coherence and lifetime stability are separate from interface shape | Generic operations, question 3 |
| Floating NaN or approximate equality used in a set/merge | Domain equality, tolerance and hash policy cannot be interchanged | Numerics, question 9 |
| Default callback allocates a shared cell | Adapter/inlining cannot silently change allocation frequency or capture identity | Binding/functions, questions 1/2 |
| Resource is retained by an error cause or diagnostic closure | Whole-completion non-escape includes failure/inspection carriers | Resources, question 5 |
| Child catches cancellation and keeps running | Stop request is not observed quiescence; scope must join or report its limit | Concurrency, questions 5/7 |
| Retry follows a lost response after remote publication | Unknown outcome differs from failure; another call may duplicate an effect | Messaging, questions 6/15 |
| Rewrite crosses a failing/effectful callback | Same successful values are insufficient when counts, order or partial effects change | Numerics/metaprogramming, questions 9/12 |
| Source snapshot is unchanged but numeric theory or schema changes | Cached proof/result depends on its theory/profile, not only text | Modules/tooling, questions 13/14 |
| Generated field/default depends on runtime context | Declared derivation cannot manufacture an earlier-stage value or authority | Metaprogramming, question 12 |
| An editor renames a display label but binding identity is unchanged | A source edit, domain change and projection edit have different owners | Interaction, question 17 |
| Statistical mean uses count of all rows while sum skips null | The two reductions observe different domains; no unconditional identity | Data/statistics, questions 8/9 |
| Filter leaves an empty group despite nonempty source | Source cardinality does not prove valid denominator for a group | Data/statistics, questions 8/9 |
| Quantile/variance/weighted mean uses implicit policy | Definition, interpolation, ddof, weights and missingness are explicit parameters | Data/statistics, question 9 |

### New Primary Mechanisms To Challenge The Model

Kotlin's variance/projection documentation distinguishes safe producer/consumer
substitution from immutability. Rust's dyn-compatibility requirements show that
not every trait interface supports an erased runtime object. Python's data model
requires equal hashable objects to share a hash and explains why changing a key's
hash breaks hashed-container placement. Asyncio documents cooperative cancellation
and the risk of swallowing it inside structured work.
[Primary references: Kotlin generics](https://kotlinlang.org/docs/generics.html),
[Rust traits](https://doc.rust-lang.org/reference/items/traits.html),
[Python data model](https://docs.python.org/3/reference/datamodel.html),
[asyncio tasks](https://docs.python.org/3/library/asyncio-task.html).

These living references were consulted on 2026-10-10; the unversioned Python
pages then served 3.15 documentation. They are selected mechanisms, not tested
cross-version guarantees. The Nomi consequences in the case table are proposed
oracles. Keep type safety, representation erasure, lawfulness, lifecycle progress,
and empirical validity separate when integrating them.

### Quality Gate For Every New Finding

Record a positive case and a false-success case that the proposed abstraction
might mistakenly accept. Name its inputs, assumptions, expected observation,
and semantic owner. Check whether a type, static fact, law, runtime guard, or
actual observation establishes the required claim. Preserve unknown/conditional
results when that evidence is unavailable. Compare repair and explanation costs
alongside implementation cost; a small encoding with opaque errors can lose to
a richer domain interface.

Continue through the ordered path in the synthesis, using one data workflow as
the next composition pressure. Existing packets keep their status and source
semantics until evidence justifies explicit promotion.

## Integrate A Settled Result

Research placement begins with an ordinary library or protocol where practical;
compare mechanically reducible convenience, scoped tools, and core changes as
needed. These are working placement choices, not a barrier to discovering a
better model. A proposal that changes the division must pay for the new laws.

For admission, specify source and meaning, invocation/control rules, typing and
constraints, effect/authority rules, cleanup/cancellation, package identity,
diagnostics, formatting, inspectable lowering, independent conformance fixtures,
and removal criteria. Update the accepted [syntax](../design/syntax.md),
[semantics](../design/semantics.md), [industrial contracts](../design/industrial.md),
[ledger](../design/decisions.md), and affected [targets](../design/targets/README.md)
together. Reconcile the whole [synthesis](../design/synthesis.md). Link evidence
from the existing feature owner and close only the question actually answered.

Then create the smallest reversible implementation bridge. Keep target-only
source out of runnable samples until frontend, runtime, diagnostics, and backend
contracts agree. Do not make a new parser spelling stand in for a semantic checker.
A library-shaped mechanism can still require substantial type/resource evidence.

Use the existing `language-coherence` packet for this guide. More focused
function, resource, pattern, or interaction choices retain their own registered
owners. Inspect the packet and validate documentation before checkpointing:

```bash
python3 -m tools.design_passes show language-coherence
python3 -m tools.design_passes check
pytest -n 0 prototype/tests/unit/tools/test_research_matrices.py prototype/tests/unit/tools/test_docs_lifecycle.py prototype/tests/unit/tools/test_design_passes.py prototype/tests/unit/tools/test_target_fixture_coherence.py prototype/tests/unit/tools/test_design_packet_boundaries.py
git diff --check
```

Those checks verify routing and document/fixture coherence. They do not execute
foreign languages, prove target semantics, or measure human understanding.
Record performed evidence and the next exact discriminator in the
[existing bridge](../review/2026-09-29-language-synthesis.md), then return here to
choose the next question. This pass prepares the deeper synthesis decision; it
does not preselect its outcome.
