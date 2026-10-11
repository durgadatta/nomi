# Learning, Inference And Intelligent Programs

> Status: shared-foundation redesign candidate, 2026-10-11. No general model,
> inference, tensor, training or AI source syntax is admitted.
> The bounded source-checkout shape experiment below is separately identified.

Nomi should help people **develop AI frameworks as well as use them**. A person
should be able to describe a model, understand why it is composable, inspect a
transformation, implement an operator or backend, and compare an experiment
without losing the original question. This extends the shared
[thinking goal](vision.md#the-design-object), not a promise that all intelligence
reduces to a tensor graph. Statistical learning, probabilistic models, symbolic
reasoning, simulation, search and effectful agents retain their own laws.

The [primary research](../research/data_workflows/ai_ml.md) owns evidence and
forks. The [engine-free framework](object_framework.md) owns shared description,
reference and realization boundaries. [Scientific discovery](scientific_discovery.md)
owns mathematical/empirical distinctions. This proposal owns the shared foundation's intelligence pressures and AI implementation
contracts under the language-coherence packet; its
[research target](targets/research/scientific_model.nomi) and
[bridge](../review/2026-09-29-language-synthesis.md) retain admission status.

## Intelligence Belongs In The Shared Foundation

The goal is **one language for building and improving explanations and behavior**.
Nomi should express learned, symbolic, probabilistic and ordinary computational
models through the same naming, binding, composition, inspection and revision
rules. A person should not have to move into a separate framework's conceptual
language to ask what follows from a model, how evidence changes it, which
abstraction can be reused, or which experiment is worth doing.

This is a proposed foundational responsibility, broader than accelerator
execution or a standard AI package. It challenges the current split between
ordinary source functions and the several laboratory description formats.
[Primary AI evidence](../research/data_workflows/ai_ml.md#intelligence-as-a-language-pressure--october-11)
adds generative programming, program/library induction, causal representation,
relational learning, cognitive memory and world-model planning to the
[historical knowledge synthesis](../research/knowledge_frameworks.md). These
are competing research approaches, not one settled theory of intelligence.

The strongest current candidate remains the reasoning algebra's three
responsibilities: **contextual descriptions, lawful composition/transformation,
and qualified questions/judgments**. Updating or acting on an answer uses
ordinary state, failure, scope and effect semantics. The third responsibility
must now cover epistemic *and* practical questions without equating their
answers. Whether this remains the smallest coherent organization is open.

### What The Language Must Guarantee

| Shared semantic responsibility | Why ordinary programming and intelligence both need it | What is supplied above the foundation |
| --- | --- | --- |
| Resolved identity, types and scoped dependencies | A captured variable, hypothesis, latent choice or scientific parameter must retain its owner through substitution and reuse | Domain spaces, variable roles, model vocabulary and learned feature names |
| First-class inspectable descriptions with explicit interpretation | A description can be composed or transformed without running arbitrary host code; source and artifact revisions remain related | Numeric, logical, stochastic, causal and other structure providers with declared domains |
| Lawful composition and hygienic transformation | Reusable functions, models, explanations and learned abstractions must preserve the facts they claim to preserve | Differentiation, inference, simplification, abstraction and planning methods, each with obligations |
| Context-qualified queries and evidence | An exact identity, posterior, feasible plan and model evaluation are useful answers with different meanings | Consequence relations, priors/likelihoods, objectives, approximation rules and evaluation designs |
| Explicit revision, publication and action | Updating a belief, changing code and performing an external action have distinct observable consequences | Learning policies, retention/retrieval, checkpointing, experiment execution and human collaboration |

These are candidate **language guarantees**, not a universal `Model` superclass,
five mandatory annotations or five new keywords. Ordinary inferred code remains
ordinary. Algorithms and domain structures should be expressible as Nomi values
and procedures under those guarantees; engines implement a selected contract.
Replacing an engine must not replace the question's meaning. A source function
still needs an admitted reification domain before it can become a transformable
description; arbitrary closures are not automatically serializable or analyzable.

The implementation comparison should extract shared machinery from the labs
rather than standardize each lab's current schema. Do not select Python AST,
a tensor graph, a theorem prover or a weighted relation as the definition of
all Nomi meaning. Keep Nomi source as one producer and library constructors as
another, both targeting the same selected scoped contracts where they agree.

### Models, Relations And Measures

A deterministic map assigns an output to an input. A relation can admit several
outputs or none. A probability kernel assigns a measure on possible outputs
for an input, under explicit normalization/measurability/support conditions.
An unnormalized potential or a set of admissible distributions supplies
something different. These can use shared typed descriptions and composition
interfaces while keeping their own laws.

For finite kernels, composition sums over an intermediate space:
`(K ; L)(x,z) = sum_y K(x,y) * L(y,z)`.
An ordinary deterministic map embeds as point mass. Mapping a measure forward
sums mass over alternatives merged by the map. This composition must preserve
normalization; it does not establish an inverse, causal mechanism or empirical
validity. Continuous composition needs additional measure/integration contracts,
not an unrestricted substitution of a finite `sum` with numeric quadrature.

Do not identify stochastic choice with an ordinary Bool branch, a sample with a
distribution, or uncertainty with failure. Unobserved latent sharing belongs to
the model; random streams and sampled traces belong to a realization. Named
choice sites require scoped identity and a trace contract. A shared latent draw
versus fresh draws changes meaning, even when both implementations return the
same marginal distribution for a single call.

Boolean relations, signed logical support, probability measures and preference
weights cannot share unspecified addition/multiplication. Each supplies a law
profile. A storage graph may represent them all; that does not give it one
consequence relation. Constraint sets and intervals remain useful alternatives
when a calibrated probability is unavailable.

### Derive Intelligent Activities Through Composition

The notation here is explanatory metalanguage, not admitted Nomi exports.
Each row must ultimately have a readable ordinary long form and source mapping.

| Derived activity | Composition from shared descriptions and laws | Result that must remain qualified |
| --- | --- | --- |
| Prediction and imagination | State/model + transition/generative law + observation map | Distribution or simulated outcome under that model and realization |
| Deduction | Premises + supplied consequence rules + checked derivation | Supported/conditional conclusion with retained assumptions and coverage |
| Abduction | Hypothesis descriptions + explanation criterion + bounded search | Candidate explanations; uniqueness/completeness are separate claims |
| Bayesian inference | Prior/joint model + evidence/query + conditioning/marginalization | Conditional measure under the model, or zero-support/unsupported/incomplete result |
| Parameter learning | Model family + examples/objective + permitted state update | Revised parameter artifact and training/evaluation basis |
| Structure or concept learning | Typed term/relationship search + examples/priors + proposed abstraction | New description/library revision with empirical or checked preservation evidence |
| Analogy and transfer | Explicit interpretation between structures + preserved judgments | Which conclusions/operations survive and which distinctions are lost |
| Planning and control | Possible transitions + objective/constraints + selection over policies | A proposed contingent policy under horizon/risk/cost assumptions |
| Active inquiry | Prospective observation/intervention + possible updates + selected value criterion | Expected benefit and cost of asking/acting; no observation has happened yet |
| Memory and reconsideration | Retained descriptions/traces/support + selected retrieval + revision/replay | Selected context and remaining support, never all-world knowledge |
| Meta-learning and metareasoning | Methods described as values + task/history + objective/budget + checked replacement | Learned method and its measured domain; no universal optimal reasoner |

A gradient is one variation operator useful for some learning updates. Search,
constraint propagation, exact enumeration, learned recognition and human
correction are other methods. A neural component can propose a program, approximate
an inference map or supply a perception model without defining what a proof,
objective or observation means. “No separate framework” means these activities
compose through shared language semantics; it does not mean all algorithms
become compiler instructions or all evidence has one type.

### Causal Thinking Requires More Than Conditioning

A causal description retains mechanisms, exogenous uncertainty and a declared
family of interventions. An intervention changes a mechanism while retaining
those declared as unaffected. A counterfactual additionally couples the changed
model to the same past world under explicit assumptions. Observation, model
revision, hypothetical intervention and actually operating an instrument are
four different activities.

A small discriminator: let `U` be a fair bit and observe `X=Y=U`. One model uses
`X=U; Y=X`; another uses `Y=U; X=Y`. Both produce exactly the same observational
distribution. Under `do(X=0)`, the first has `P(Y=1)=0`, the second `P(Y=1)=1/2`.
A correlation model cannot choose between them without additional assumptions
or evidence. Neither a valid probability calculation nor a checked theory
bridge can silently supply causal identification.

For scientific discovery, connect this to existing observation/realization and
inverse-model owners. A learned causal variable needs a role/interpretation and
an intervention contract; a latent feature name alone supplies neither. Units,
conservation, symmetries and invariance across environments can constrain model
search without proving that the unique physical mechanism has been found.

### Learn Abstractions Without Changing Meaning Silently

Learning a parameter changes a selected model instance. Learning an abstraction
can change the vocabulary used to describe many models. The latter is a
first-class design pressure on binding and revision, not an optimizer feature.
A proposed reusable function should have scoped parameters, declared captures,
source correspondence and a preservation claim with its own basis.

Compare three outcomes:

- A beta-equivalent extraction in the admitted pure-term domain can earn a
  checked refactoring claim, after hygienic substitution and type checking.
- A hypothesis matching finite examples earns coverage of those examples.
  It does not thereby become a universal replacement for the old program.
- A learned approximation can replace an expensive map under a declared error
  and use regime. Its empirical loss does not automatically establish the bound.

Library growth, type/feature discovery and learned search guidance can reinforce
one another, but remain separately versioned. A changed hypothesis vocabulary
may require a checked interpretation to compare old and new belief states.
Compression scores depend on the coding/prior/objective; they do not settle
human readability or scientific truth. Effectful learned procedures additionally
retain ordinary effect, capture, resource and completion obligations.

### Memory, Goals And The Thinking Loop

The shared objects support a deliberate loop:

```text
question + current context
  -> propose alternatives / retrieve selected descriptions
  -> derive or infer consequences under a named method
  -> compare under an explicit intellectual or practical objective
  -> propose a question, model revision or action
  -> check and publish the revision / authorize and perform the action
  -> capture the actual observation or outcome, then reconsider
```

Working memory is the selected active context. Episodes are qualified traces
and observations; semantic memory stores descriptions and their evidence;
procedural memory stores reusable transformations/policies. These are roles
with different retention and read/write rules, not four global stores built
into the compiler. Retrieval quality and freshness are different from evidence
strength. A model-generated explanation can propose premises or procedures;
publication and execution remain separate checks.

A goal can select information gain, predictive accuracy, explanation simplicity,
practical loss, resource cost or a combination with declared constraints.
Those objectives can disagree. Perfect information about an irrelevant variable
has no decision value; unpredictable noise can be novel without teaching a
useful model. Choosing a query is not being compelled to perform it. Preserve
ties, infeasible/no-supported answers and the option to stop. Human correction,
teaching, ambiguity resolution and perspective changes belong in this loop.

### Executed Finite Inquiry, Not A Matrix Framework

The [finite inquiry lab](../../tools/finite_inquiry.py) is an original bounded
composition, runnable with `python3 -m tools.finite_inquiry`. Immutable spaces,
measures, kernels, observations and loss descriptions contain no callbacks,
RNG, solver or live authority. The exact adapter checks finite normalization,
composes kernels, conditions a shared joint world, compares decisions and
computes one-step decision value for a prospective observation. All inputs are
qualified descriptions; no sensor, optimizer or accelerator is invoked.

In its oscillator example, two model hypotheses have equal prior mass. A
prospective measurement has declared reliability `3/4`; the supplied mismatch
loss is one. Baseline expected loss is `1/2`, expected loss after observing is
`1/4`, and cost is `1/8`. Net expected decision value is `1/8`. This answers a
conditional model question, not whether the instrument or hypotheses are right.

Eleven focused checks include kernel laws, exact path enumeration, event
idempotence, withdrawal, zero-support evidence, irrelevant information,
zero-mass outcomes, tied decisions and stale revisions. An independent consumer
replays inquiry through unnormalized joint losses. Exhaustive contingent-policy
tests compare all choices after every possible outcome. Repeated report events
are intersected, not multiplied as independent likelihoods; repeated independent
measurements must be explicitly represented in the joint model.

The profile permits at most eight members per finite space, sixteen observation
constraints and bounded nonnegative exact rational inputs. These are lab caps,
not language limits. Zero-support conditioning returns no invented posterior.
Withdrawal recomputes from the original model and remaining evidence, since a
conditioning update need not be invertible. Assessment fingerprints bind model,
experiment and objective content/revision/cost; changed context refuses replay.
An assessment proposes no external action and grants no authority.

General probabilistic source programs, continuous inference, stochastic traces,
general causal interventions, unrestricted structure learning and empirical
model adequacy remain unimplemented. The artifacts test the conceptual foundation rather than
claiming a general intelligence engine. Bounded source/function/kernel integration now runs; broader typed source and
structure/evidence contracts remain necessary before language admission.

The inquiry artifact now also retains each prospective outcome as a named,
immutable branch: its modeled mass, conditional hypothesis measure and tied
best decisions. A zero-mass branch is still referable but has no invented
posterior or decision. `describe` exposes detached JSON without executing or
validating anything; `verify_inquiry` independently checks those intermediates
as well as the aggregate loss. Four additional checks reject forged branches
with correct aggregates and confirm passive inspection/immutability. These
hypothetical branches are not reports that an observation occurred.

The [explicit Nomi producer](../../tools/nomi_terms.py) also captures bounded
pure scientific/ordinary functions through the actual frontend into the same
scoped-term contract. This closes the Python-only authoring comparison for that
profile; general source admission, evidence transport and richer structure providers
remain separate obligations.

### Executed Bounded Program Induction

Run `python3 -m tools.program_search` to construct pure rational functions from
a captured typed grammar and teaching examples. The
[producer](../../tools/program_search.py) enumerates bodies by node count and
explicit grammar order, checks example outputs, and retains bounded proposals
using the shared transformation provider. No callback, learned truth or execution
authority is embedded in a proposal. Separate
[tuple enumeration and arithmetic replay](../../tools/program_search_replay.py)
checks counts, ranked proposals, retention and complete/incomplete coverage.

The demonstration learns both `x` and `x*x` from `(0,0)` and `(1,1)`; an actual
example `(2,4)` removes the line. Another test induces `-2*position - velocity`
from supplied force examples. These are original finite comparisons, not
reproductions of DreamCoder or a neural learner. A match establishes only the
supplied examples. Exhaustiveness is bounded by the declared grammar and node
limit; it does not establish that the actual mechanism is in that grammar.

Descriptions retain example/grammar identities and exact contents, ordering,
search budget and proposal limit. There are one to three scalar parameters,
up to four constants/operations, seven body nodes, sixteen examples and five
thousand examined candidates. Constants and example rationals have a declared
16-bit capacity. Retention truncation is distinct from incomplete search. Multiple
spellings of the same function remain distinct proposals; their prior coding and
semantic deduplication require explicit policies. No learned approximation or
universal refactoring claim is inferred from example fit.

### Source-Linked Hypotheses And Two Deeper Discriminators

`python3 -m tools.intelligence_examples` connects actual Nomi scoped-function capture to
finite inquiry. The two oscillator mechanisms are source-derived pure rational
functions with the same checked callable contract. Their finite alternative
identities bind the full source/type/origin inspection fingerprints. Changing
formula content invalidates the inquiry basis even if a producer reuses the old
source revision label. The measurement likelihood and mismatch loss remain
explicit assumptions; the mechanism text does not establish those numbers.

The command also runs the causal discriminator above. Independent tests execute
its binary structural assignments separately from the kernel adapter. Both
observational distributions agree, while the intervened `Y=1` probabilities are
zero and one-half. This is a supplied finite mechanism comparison, not learned
causal identification or a general intervention engine.

For abstraction learning, `x*x` and `x` agree at supplied examples zero and one
but disagree at two. Finite fit therefore fails a universal replacement claim.
Separately, hygienic beta extraction of `offset=5` yields an alpha-equivalent
`x+5` term in the admitted pure-term lab. Five cross-lab checks pass. These are
executable conceptual counterexamples, not empirical discovery benchmarks.

The comparison CLI now uses the bounded Nomi producer; the Python-expression
adapter remains available explicitly. Both capture inert checked terms. Closed
rational functions and finite kernels share a provider boundary, while source
reconstruction, general law/evidence transport, richer types and runtime
integration remain open. Do not treat this bridge as a universal model hierarchy.

### Executed Adaptive Observation And Revision

The [adaptive inquiry journal](../../tools/adaptive_inquiry.py) now captures
original priors, trial occurrences, reports and explicit endorsement. Each report
binds the full captured trial law. Copies about the same trial count once;
conflicting outcomes about that occurrence are `conflicting-reports`, distinct
from `impossible-under-model`. Withdrawal recomputes from the original prior.
The admitted profile explicitly declares conditional independence of **distinct
trials given the modeled state**. This is a supplied modeling assumption; source
names or report multiplicity cannot establish it. Correlated trials need a joint
state/likelihood description, not silent multiplication.

A one-step plan recomputes model-relative information value for each captured
question and objective. It retains best-query ties and zero-value stop ties;
negative-value queries do not compel action. No supported posterior requests
model/evidence repair. Changed priors, trial laws, endorsements, query costs or
objectives invalidate earlier assessments. Independent likelihood-product replay
and the existing unnormalized joint-loss checker verify estimates and plans.

Run `python3 -m tools.intelligence_loop` for an inspectable composition of
induction, prediction, inquiry and revision. `--observe 4 --at 2` explicitly
supplies a teaching observation, rechecks examples and stops; `--observe 3`
retains unexpected output through an explicit zero-likelihood outside-support
bucket and requests repair. `--json` exposes every named intermediate. A source
or learned description neither samples a sensor nor authorizes world action.
The original observed scalar is retained in a content-addressed input record.
No posterior is silently transported into a revised hypothesis vocabulary.

The journal bounds trials/reports/questions at 16/32/8 and reuses finite exact
model capacities. Its conditional-independence law and one-step objective are
not universal cognitive primitives. A bounded contingent lookahead now follows this one-step comparison. General
stateful planning, latent-dependent observations, causal discovery, vocabulary
transport and human
interaction remain subsequent discriminators. See the
[runnable guide](../guide/reasoning_lab.md) for authoring and correction.

### Checked Hypothesis Restriction

The [support-restriction bridge](../../tools/model_refinement.py) now compares
an original program family with an explicitly selected subset or permutation.
Only exact artifact identities and callable contracts are preserved. A new
vocabulary, equal sample outputs or changed grammar does not establish transport.
An independent retained-set/mass replay verifies the assessment.

Removing positive probability returns `positive-mass-loss` with no transported
measure; it does not silently renormalize. Removing only zero-mass alternatives
can produce a support-preserving measure. Explicit adapters restrict prediction
rows and objective state columns while preserving the original outcome/decision
spaces. Six checks include stale contexts, permutation, positive-mass refusal,
preserved predictive distributions/decisions and end-to-end refinement proposals.

The discovery loop exposes a checked restriction proposal after a supported
observation. It keeps the original journal/prior active, rather than publishing
a conditioned prior that would destroy withdrawal semantics. Repair after zero
support proposes no empty/fabricated model. Broader vocabulary interpretation,
semantic deduplication, missing/truncated hypotheses and evidence publication
remain open; the bridge's guarantee is relative to the captured finite family.

### Stronger Evidence For A Learned Description

[Scoped polynomial interpretation](../../tools/scoped_polynomials.py) now lets
source, constructor and induced pure functions enter the existing formal map
algebra. Independent pinned SymPy replay checks their exact meaning and tangent
vectors from qualified-owner terms. A force proposal learned from examples can
therefore earn a separate formal identity to an explicit force description.
Neither judgment establishes that the force describes an actual system.

Alpha equality, exact polynomial equality and example fit remain different
contracts. Equivalent spellings could later be grouped under a declared coding
and prior policy, but no vocabulary collapse or probability change is automatic.
Formal symbolic differentiation supplies an established algebra oracle; it is
not a general numeric/accelerator AD adapter or a theory of learning.

### Compose Contingent Inquiry Beyond One Step

The [contingent policy comparison](../../tools/inquiry_policy.py) now composes
the same journal estimates, kernels, losses and prospective branches through a
bounded horizon. Each option's cost is its query cost plus outcome-weighted
continuation loss/cost. Stopping is always available. Complete search retains
all best first-query/stop ties; partial search exposes feasible incumbents and
conservative lower/upper cost bounds, not an optimality claim.

The discriminator asks for two-bit parity. Each bit alone has no decision value,
so one-step inquiry stops. A two-step policy sees that their combination resolves
parity. With cost `1/16` per query, expected loss plus costs is `1/8`, below the
stop loss `1/2`. An independent enumeration of all two-step contingent strategies
checks that optimum. Separate policy replay validates every query through the
existing joint-loss checker and independently recomputes continuation bounds,
coverage, stopping decisions and budget use. Zero-mass branches have no children;
unsupported evidence supplies no policy.

Run `python3 -m tools.inquiry_policy --horizon 1`, then `--horizon 2`.
`--budget 1` retains incomplete bounds; `--json` exposes named policy branches.
The profile admits up to three query methods, horizon three and 256 internal
expansions, following the journal's explicit conditional-independence assumption.
It models inquiry about a fixed hidden state, not general world transitions,
causal action, correlated unmodeled draws or an unbounded agent planner.

## Start From The Developer's Activity

The [minimal reasoning algebra](reasoning_algebra.md) now challenges the common
foundation with contextual terms, composition and judgments. Its formal tangent
map experiment is a finite exact rule comparison, not general AD or a tensor
engine. R1/R2 align scoped descriptions and tangent/cotangent obligations with
AF1/AF2; an established AD adapter remains the next general derivative oracle.

| Activity | What the environment should explain | A discriminating failure |
| --- | --- | --- |
| Express a hypothesis | Architecture, objective, assumptions, trainable choices and alternatives | A better benchmark score is presented as a general explanation |
| Compose a model | Named intermediates, axes, scalar policy, state and mode | Equal-size token and feature axes silently align |
| Transform a program | Primal, tangent/cotangent, batching, staging and source mapping | A custom operator supports a forward kernel but has no valid VJP |
| Build a framework primitive | One operator contract with independently admitted rules/adapters | A backend callback becomes its own shape or derivative oracle |
| Train and resume | Old/new state, data position, randomness, accumulation and publication | Weights-only loading is called exact training resume |
| Diagnose an experiment | Missing premises, nonfinite values, numerical error and selection history | A shape check or derivative test is called model-quality evidence |
| Scale or serve | Placement, collectives, cache context, completion and resource ownership | Local gradients are mistaken for the global weighted objective |
| Delegate research | Proposed changes, retrieved sources, evaluation basis and actual authority | Model output or retrieved text is treated as an executable instruction |

Keep drafts useful: an unresolved architecture, shape or custom derivative may
be inspected and revised. A checked export must expose or discharge its missing
contracts. Unknown support is neither implicit success nor proof the idea is
invalid. A human should see the missing fact and its owner before implementation
details. Text, mathematical and graph views should refer to the same identities;
changing a view must propose a checked revision, not mutate a running model.

## A Few Reusable Contracts

These domain contracts build on the shared semantic responsibilities above.
They are not new keywords or a claim of a minimal universal IR. They compose the six candidate families
[Value, Bind, Apply, Choose, Perform and Scope](primitive_composition.md).

| Contract | Composition | Domain facts that cannot be erased |
| --- | --- | --- |
| Semantic space | Value + identity + validation | Scalar policy, named axes, shape constraints, units/basis and tangent/cotangent meaning |
| Numeric program | Bind + typed operation application + explicit choice/scope | Operation versions, captured constants/state, phase, supported control flow and source map |
| Transformation | Program values + checked context + domain rules | JVP/VJP, batch, specialization and rematerialization domains; rejected combinations |
| State transition | Owned state + Apply + explicit update/publication | Parameter sharing, optimizer/model state, RNG, data progress, mode, cancellation and commit basis |
| Realization | Description + capability matrix + Perform + Scope | Numerical method, device/layout/sharding, buffer lifetime, communication and completed work |
| Evidence | Context-qualified claim/observation + revision | Formal rule checks, numerical comparisons, empirical evaluation and human comprehension have different coverage |

Training is a composition of these contracts: a checked loss program,
transformation, explicit state transition, qualified realization and recorded
experiment. A transformer layer is a library composition of projection,
contraction, masking, normalization and related operators. An optimizer is a
state transition with its own state and numerical rules. A conversational agent
is an effectful workflow with model observations, not a differentiable tensor
operator by default.

## Separate Description, Check, Transform, Compile And Run

Proposed protocol metalanguage; names and type notation are not accepted exports:

```text
draft program + unresolved obligations
  -> domain check -> checked NumericProgram under a named profile
  -> transform(program, rule set, selected inputs) -> transformed program
  -> plan(program, implementation profile) -> unresolved or admitted plan
  -> compile(plan, toolchain) -> compiled artifact + specialization contract
  -> execute(artifact, bindings, actual grants, limits) -> completed run evidence
```

Each arrow can refuse or leave an explicitly narrower unknown. Ordinary eager
calls still evaluate arguments once; constructing a program is an ordinary
call that returns inert data. Neither purity nor a callable type proves that an
arbitrary closure can be traced, translated, differentiated or serialized.
Compare explicit expression constructors with a checked source-function subset
before admitting quotation or a scoped numeric tool. A trace-time host print,
file read or parameter initialization cannot silently become a once-per-batch
operation. Specialization records capture values, shape constraints and mode.

A mathematical model may contain cyclic equations; an execution graph needs
explicit loop/control-flow structure. An autograd tape records an execution and
saved intermediates; it is not automatically the original program or a portable
model. Domain IRs such as ONNX/StableHLO belong behind typed adapters, not as
definitions of the entire Nomi language.

## Tensor Meaning Is More Than An Extent List

Specify independent dimensions of a tensor contract:

- element/scalar policy, accumulation precision, conversions and nonfinite rules;
- ordered axis identities and extents, including symbolic constraints;
- quantity kind, unit, coordinate basis and tangent/cotangent space when relevant;
- missing/mask semantics, dense/sparse/ragged representation;
- layout, strides, ownership, views and writable aliasing;
- device/memory space, mesh placement and pending reduction state.

Equal extents do not imply interchangeable axes. A token mask, absent observation
and numerical NaN are different meanings. Broadcasting, reshaping, flattening,
axis renaming and coordinate conversion need explicit laws and source mappings.
An extent variable is not an axis identity; two axes can share one extent
without being semantically equal. Shape constraints may be unresolved: do not
invent a symbolic arithmetic solver or silently use a sample input as proof.

Rank/shape checking does not prove useful values, finite arithmetic, correct
masking, nonempty reductions or correct units. A mean over a possibly empty
domain needs a defined empty policy; masked means need a selected denominator.
Attention requires separate query/key/value axes and causal/padding rules.
Sparse duplicate indices and ragged segment boundaries also need domain laws.

### Tangents And Cotangents

For a differentiable program `f: X -> Y`, a JVP maps a primal point and tangent
in `T(X)` to a primal result and tangent in `T(Y)`. A VJP maps a primal point and
cotangent in `T*(Y)` to a cotangent in `T*(X)`. Identifying these spaces with
ordinary arrays requires a declared coordinate/pairing convention. Scientific
units and sharding obligations do not disappear because shapes match.

Use the pairing identity `pair(Jv, u) = pair(v, J* u)` as one independent
discriminator for a linearization/transposition pair. It does not prove that
`J` is the derivative of `f`; compare primal derivatives separately. Finite
differences have step-size/rounding limitations and cannot settle every
nondifferentiable or ill-conditioned case. Exact polynomial cases provide a
small independent oracle; an established engine adapter should precede building
a general custom AD engine.

Keep scalar-loss gradient, JVP, VJP, Hessian-vector product and per-example
gradient distinct. `stop_gradient`, custom rules, subgradient conventions,
complex differentiation and implicit differentiation need named policies.
Batching and differentiation commute only under their admitted contracts;
batch-coupled statistics invalidate an assumption of independent examples.

## Developing An Operator Or A Backend

A declarative operator entry should own stable identity/version, semantic
signature, abstract inference, definedness, alias/effect behavior and source
diagnostics. Its other capabilities are **separate optional registrations**:

| Registration | Establishes | Cannot establish alone |
| --- | --- | --- |
| Abstract rule | Metadata result and obligations without tensor data | Forward numerical correctness |
| Reference semantics | A bounded independent value/error oracle | Fast kernel correctness on every host |
| Decomposition | Equivalent composition under stated scalar/domain laws | Floating-point equality after arbitrary reassociation |
| JVP / transpose / VJP | Named derivative behavior and residual requirements | Higher-order AD or batching support automatically |
| Batch rule | Axis mapping under a specific batching contract | Data-parallel sharding or collective behavior |
| Backend lowering | Implementation under dtype/layout/device/operation profile | Source equivalence merely because compilation succeeded |
| Codec / export rule | Versioned transport and resolved operation dependencies | Support on every receiving engine |

A new operation may have useful abstract meaning before a kernel exists. A
framework author must be able to supply a kernel without replacing the abstract
checker. An adapter cannot change an operation's semantics under the same
identity. Registration declarations require independent evidence; self-reported
support is not conformance. Keep unsupported capability combinations visible.

Example diagnostic, proposed rather than an implemented general diagnostic:

```text
AI_AXIS_MISMATCH at prediction
Contracting input axis features[32] with weight axis tokens[32].
Equal extents do not establish that these axes have the same meaning.
Related: input.features; weights.tokens
Repair: supply feature-indexed weights, or a separately checked axis conversion.
```

Do not suggest an automatic rename or transpose as a verified repair. A
framework-specific renderer can expose device details after the semantic cause.

## State, Randomness And Training Are Visible

Separate ModelSpec, parameter state, non-trainable inference/training state,
optimizer/scheduler state, RNG state, data progress and evaluation record.
Parameter identity supports intentional tying; equal-shaped parameters are not
the same parameter. A read-only wrapper does not prove a foreign buffer cannot
be mutated through another alias. Resource adapters own borrowing and donation.

Proposed training-step long form:

```text
validate old state + batch basis + explicit random choices
-> evaluate primal loss, next model state and saved derivative residuals
-> compute selected gradients under a derivative profile
-> apply gradient aggregation, scaling/clipping and optimizer policy
-> propose next parameters, optimizer/RNG/data state and step result
-> publish one coherent checkpoint/progress basis through an explicit owner
```

Physical buffer reuse may implement immutable logical states, provided aliases,
failure and visibility preserve the contract. Do not promise atomic publication
across arbitrary devices and filesystems. Cancellation before publication,
partial device failure and uncertain external save outcomes need explicit
reconciliation. Retrying a step must state whether it reuses or changes its
random choices and data. Microbatch accumulation, loss scaling, overflow-skip
and schedule advancement must specify which transitions happen.

Random generator identity, key splitting/reuse, stream position and algorithm
are explicit. A seed is insufficient for cross-host bitwise equivalence. A
training checkpoint needs optimizer/scheduler, model/RNG/data progress and its
execution basis; weights alone support a narrower inference restore. A train
mode flag cannot hide initialization, state mutation or dropout randomness.
Rematerialization must preserve random choices and avoid duplicated host effects.

## Distributed And Hardware Work Retain Their Laws

Device work has logical submission and physical completion; result observation
and timing need a declared synchronization basis. Allocation, transfer,
compilation, collectives and release have owners and failure channels. A
capability name in an artifact grants none of that authority.

Sharding is not just batch mapping. Distinguish global semantic axes, mesh axes,
local slices, replication and unreduced partial values. A VJP may require
communication even when its primal operation does not. Specify membership,
collective order, weighted aggregation, uneven batches, rank failure and
recovery. A mean of shard means generally differs from a global mean when
shard sizes differ. Cancellation cannot let one participant skip a collective
while peers wait without a group failure policy.

Kernel-development tools need explicit layouts, memory spaces, synchronization
and resource models behind checked adapters. Quantization/calibration, mixed
precision, sparsity, routing and fused attention are profiled implementations
with independent error/gradient/performance checks. Reassociation and fusion
must not silently claim exact equivalence for floating-point programs. Benchmark
compilation, transfer and synchronized execution separately; vendor results
are not Nomi measurements.

## Experiments, Foundation Models And Agents

Keep specification, learned state, run, training checkpoint, evaluation,
deployment and request identities separate. Evaluation binds a dataset/split,
population, metric, selection procedure and uncertainty. Train-only preparation
does not by itself account for adaptive feedback, entity/time leakage or
contamination. The existing [adaptive evaluation and erasure research](../research/data_workflows/ai_ml.md)
retains those obligations. No evidence digest certifies unobserved independence.

Foundation-model descriptions additionally bind tokenizer, prompt/template,
input modalities, adapter weights, generation policy and model version. KV-cache
reuse depends on the actual computational and tenant context; a cache hit does
not validate an answer. Multimodal alignment and temporal meaning need explicit
contracts. Serving separates compiled/loaded artifacts, batching, capacity,
request cancellation, token streaming and completed output.

RAG retrieves evidence with source/revision/coverage; ranking is not truth.
Retrieved instructions are content, and structured model output still crosses
a decoder. An agent produces proposals and observations with budgets and actual
tool grants. Restoring conversation state or replaying a model answer does not
restore permission or establish exactly-once external action. Lost tool
acknowledgement requires reconciliation. Prompt/tool/model changes invalidate
the relevant evidence, even if displayed text looks similar.

Probabilistic programming, causal inference and reinforcement learning remain
distinct extensions: joint distributions/conditioning and approximate inference;
intervention/identifiability assumptions; environment state/actions/rewards and
termination versus truncation. Neural embeddings do not erase those semantics.

## Integration And Gap Analysis

The existing six-family hierarchy remains unchanged. These domain combinations
use its description, validation, transformation, learned-state, evidence,
resource and deployment ingredients; they do not establish new accepted Core
instructions or complete tensor laws.

| Gate | Deliverable | Independent positive and negative discriminator |
| --- | --- | --- |
| AF0: authoring | An ordinary report, scientific hypothesis/inquiry, beginner regression, custom operator and failure-heavy agent | Explain assumptions/phase/premises, compare drafts, correct a model and hand off its question; actual human trials |
| AF1: abstract programs | One scoped source/constructor contract across ordinary maps, logical hypotheses, finite kernels and numeric programs | Hygiene, same-label/different-owner, named axes, latent sharing, changed vocabulary and stale context |
| AF2: transformations | Explicit structure providers for deduction, finite inference, abstraction/refactoring and numeric variation | Independent support/models, zero-support inference, invalid bridge, non-equivalent learned extraction, established AD vectors; bounded incomplete results |
| AF3: realizations | One bounded backend adapter, then a second under the same declared contract | Independent values/errors, precision policy, non-contiguous/empty shapes, measured completed device work |
| AF4: state and resume | Explicit model/optimizer/RNG/data transition and checkpoint basis | Weights-only resume refused, changed mode/schema, interrupted publication and repeated random choices |
| AF5: scale and serve | Sharding/collective and export profiles, pinned model/tokenizer/cache context | Uneven weighted mean, missing backward collective, unsupported export, tenant/cache mismatch and rank failure |
| AF6: learning evidence and agents | Model/objective revision, adaptive inquiry, structure learning and capability-bound proposals | Non-identifiability, observational versus intervention answers, irrelevant information, held-out influence, stale review and lost acknowledgement |

These gates refine ML1-ML6 and the existing function/numeric/effect questions;
they do not replace them with a second release backlog. No grammar change is
needed for the first comparison. Current CLI/web prototypes have no admitted
tensor, accelerator, autodiff or training contract. The scientific polynomial
probe is a bounded formal oracle, not a gradient engine. Existing generic object
composition does not infer tensor axes from nominal ports.

Extend the bounded AF1 Nomi-source/constructor and R2 function/kernel provider
comparison to logical and numeric challengers. Program induction now supplies
example-qualified proposals. Next connect actual observations to adaptive inquiry,
then follow with AF2 established symbolic/AD checks and causal/abstraction-learning
comparisons; do not let matrix execution dictate the
foundation. Keep stateful/random/distributed challengers in
the pressure set from the start so a convenient pure example does not determine
all later semantics. Compare development tasks and handoff, not only numerical
outputs. Extract shared machinery where context/reference meanings agree;
retain domain-specific validation, evidence and operational profiles.

## Try A Tensor Contract Without Inputs

The bounded [shape probe](../../tools/ai_probe.py) checks a closed pure metadata
profile, `named-tensor-shapes-v1`. The
[linear regression description](../research/data_workflows/ai_linear_program.json)
names feature, weight, target, prediction, residual and loss objects. It stores
no arrays, learned weights, callbacks or device handles.

```bash
python3 -m tools.ai_probe docs/research/data_workflows/ai_linear_program.json
python3 -m tools.ai_probe docs/research/data_workflows/ai_linear_program.json --object prediction
```

The profile admits input/parameter, rank-two contraction, equal-signature
add/subtract, square, explicit broadcast and mean over all axes. Scalars have
empty axis lists. Up to eight globally named axes have fixed positive extents
or separately named positive extent variables. Shape compatibility uses axis
identity, not just extent equality; expressions do not solve relationships
between different extent variables. This candidate chooses nonempty axes, not
the language's eventual empty-tensor policy. Float32/Float64 are **metadata
labels only**; no scalar arithmetic or numerical conformance is established.

Every named intermediate, including disconnected ones, is checked. Reports
retain inferred signatures, leaf dependencies and full-context identity.
`--object` explains a selected intermediate. Immutable snapshots and detached
reports keep inspection from changing the description. The bound is 128 objects,
rank four, depth 64 and a 1 MB artifact. The tool refuses host values, unsupported
operations, cycles, implicit broadcasting and malformed dimensions/dtypes.

An optional backend descriptor lists operation names and scalar labels. It
produces `declared-coverage` or `unsupported` for the chosen program, not a
compiled executable or verified kernel. Without one, backend support is
`unknown`. All reports retain `derivatives: not-produced`, `execution: not-run`
and `numerical-correctness: not-established`. The checker neither imports an AI
framework nor allocates tensors. Removal/extraction point: replace its closed
operator table/profile with an admitted domain artifact, preserving independent
axis counterexamples, source identity and honest capability outcomes.

The shared [transformation boundary](../../tools/reasoning_structures.py) now
provides closed callable families and explicit finite prediction kernels. Pure
Nomi source, constructor terms and finite inquiry compose without callbacks or
execution authority stored in descriptions. Carrier-specific equality, law
checks, general typed sources and evidence transport remain separate gates.
