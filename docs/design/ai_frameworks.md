# AI Frameworks And Differentiable Programs

> Status: designing domain contracts, 2026-10-10. No tensor type, automatic
> differentiation engine, training runtime or AI source syntax is admitted.
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
owns mathematical/empirical distinctions. This proposal owns AI-specific
contracts under the language-coherence packet; its
[research target](targets/research/scientific_model.nomi) and
[bridge](../review/2026-09-29-language-synthesis.md) retain admission status.

## Start From The Developer's Activity

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

These are ordinary library/artifact responsibilities, not new keywords or a
claim of a minimal universal IR. They compose the six candidate families
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
| AF0: authoring | Beginner linear regression, custom-operator author, failure-heavy stateful/distributed workflow | Explain axes/phase/premises, repair an invalid composition, compare drafts and checked exports; actual human trials |
| AF1: abstract programs | Closed operation signatures, named axes, scalar-profile labels, input-free metadata inference | Correct contraction; equal-size swapped axes; explicit broadcast; missing shape evidence; stale receipt |
| AF2: transformations | Versioned checked numeric subset or explicit operator values, JVP/VJP/batch source maps | Exact scalar oracle, pairing identity, numerical vectors in one established AD adapter; unsupported effect/custom-rule refusal |
| AF3: realizations | One bounded backend adapter, then a second under the same declared contract | Independent values/errors, precision policy, non-contiguous/empty shapes, measured completed device work |
| AF4: state and resume | Explicit model/optimizer/RNG/data transition and checkpoint basis | Weights-only resume refused, changed mode/schema, interrupted publication and repeated random choices |
| AF5: scale and serve | Sharding/collective and export profiles, pinned model/tokenizer/cache context | Uneven weighted mean, missing backward collective, unsupported export, tenant/cache mismatch and rank failure |
| AF6: learning evidence and agents | Selection-aware evaluation and capability-bound proposal/reconciliation | Held-out influence, unknown adaptation history, stale review, lost acknowledgement and untrusted retrieved instructions |

These gates refine ML1-ML6 and the existing function/numeric/effect questions;
they do not replace them with a second release backlog. No grammar change is
needed for the first comparison. Current CLI/web prototypes have no admitted
tensor, accelerator, autodiff or training contract. The scientific polynomial
probe is a bounded formal oracle, not a gradient engine. Existing generic object
composition does not infer tensor axes from nominal ports.

Prioritize AF1, then explicit-expression versus checked-function comparison and
AF2 with an established engine. Keep stateful/random/distributed challengers in
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
