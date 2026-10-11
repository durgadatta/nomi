# AI, Learning And Knowledge: Conceptual Foundations

> Status: selected primary research and Nomi candidates, not accepted tensor,
> differentiation, model, training, inference or agent APIs.
>
> Documentation checked 2026-10-04. Foreign snippets are illustrative and
> unexecuted; [local probes](composition_experiments.md) are original bounded
> models, not ML-engine conformance or empirical model-quality evidence.

[Dossier](README.md) · [Data/time](dependencies_and_time.md) ·
[Numerics](../features/numerics.md) · [Domain composition](../domain_composition.md)

The [AI framework proposal](../../design/ai_frameworks.md) owns integration with
engine-free objects and thinking support. Its framework-author extension was checked 2026-10-10. The conceptual
continuation below was consulted 2026-10-11; earlier sections retain their dates.

## Intelligence As A Language Pressure — October 11

The user's continuation changes the question from “can Nomi host an ML
framework?” to **“can the same language represent, improve and act on models
without an additional conceptual language?”** Numerical operators are one
realization. The intellectual work includes creating hypotheses, explaining
observations, imagining alternatives, discovering reusable structure, choosing
questions and revising beliefs. The [design owner](../../design/ai_frameworks.md#intelligence-belongs-in-the-shared-foundation)
turns this evidence into a coherent candidate, not a collection of new keywords.

### Primary Evidence And Actual Reading Depth

**T** means selected original sections; **M** selected official mechanism
contracts; **A** an author abstract. None means entire-paper reproduction or
empirical validation. All rows were consulted on October 11. Publication years
come from the works, not a search engine's crawl date. The Church paper is from
2008 despite its 2024 proceedings reissue. GenJAX is a related implementation,
not evidence that every interface below exists unchanged in the 2018 Gen report.

| Primary work / depth | Mechanism worth retaining | Nomi inference and discriminator |
| --- | --- | --- |
| [Church, Goodman et al., 2008](https://ai.cs.washington.edu/www/media/papers/church_GooManRoyBonTenUAI2008.pdf), **T**, stochastic memoization/query sections | Generative programs compose; stochastic memoization changes the modeled joint dependence, not merely runtime cost | Model description, random choice and conditioning need different contracts. Sharing a latent draw and drawing twice must not become equivalent through caching. |
| [Gen report, Cusumano-Towner et al., 2018](https://dspace.mit.edu/entities/publication/6538d5bf-2254-4c05-aaae-c687926cf2f6), **A**; [GenJAX core](https://genjax.gen.dev/library/core.html), **M**, generative function/trace/target interfaces | Models, addressed choices, targets and inference operations have distinct roles; edit proposals have additional validity requirements | Separate the object being inferred from the method and its execution trace. Address edits must preserve observation meaning or name discarded evidence. |
| [Lake, Salakhutdinov and Tenenbaum, 2015](https://cbmm-new.mit.edu/publications/human-level-concept-learning-through-probabilistic-program-induction), **A** | Concepts represented as explanatory programs, demonstrated for handwritten characters | Learn structural descriptions as well as numeric parameters. A narrow character result does not establish universal one-shot learning. |
| [Lake et al., 2017](https://gershmanlab.com/pubs/Lake17.pdf), **T**, original introduction | Model building, compositionality, causality and learning to learn challenge recognition-only accounts | Compare reusable mechanisms and transfer, not only a score on another sample from the same distribution. These are research hypotheses, not settled laws of cognition. |
| [DreamCoder, Ellis et al., PLDI 2021](https://www.neurosymbolic.org/papers/EllisWNSMHCST21.pdf), **T**, sections 2–3 | Typed program search, abstraction/library learning and learned search guidance are coupled but distinct; finite beams approximate inference | Proposed abstractions need hygiene, explicit assumptions and checked refactoring. A learned search priority or finite beam is not completeness or a new semantic rule. |
| [Causal representation learning, Schölkopf et al., 2021](https://arxiv.org/pdf/2102.11107), **T**, introduction and modeling levels | Observed dependence, changed mechanisms and discovery of causal variables are different tasks | A generative model is not automatically an identifiable causal model. Compare observationally indistinguishable candidates under intervention. |
| [Relational inductive biases, Battaglia et al., 2018](https://arxiv.org/abs/1806.01261), **A** | Structured entities/relations and shared computation encourage combinatorial generalization | Retain typed relationships and invariance assumptions independently of a graph layout. A neural graph is not a proof of equivariance or causal structure. |
| [DreamerV3, Hafner et al., 2023](https://arxiv.org/abs/2301.04104), **A**, original preprint | Learned environment models support imagined trajectories for behavior improvement | Distinguish simulated outcomes, actual observations, policy and objective. No benchmark result is reproduced or treated as general intelligence evidence. |
| [Soar architecture manual](https://soar.eecs.umich.edu/soar_manual/02_TheSoarArchitecture/), **M**, support/impasse/chunking | Subproblem results carry support; chunking generalizes resolved reasoning into reusable productions | Keep support and learned generalization distinct. Missing negative premises can overgeneralize a learned rule; a cached conclusion must not erase its context. |
| [CoALA, Sumers et al., 2023/24](https://arxiv.org/html/2309.02427v3), **T**, section 4 | Working, episodic, semantic and procedural memory; internal and external actions in a decision cycle | These become context, traces, descriptions and reusable procedures with different read/write rules. Generated text does not acquire truth or live authority by entering memory. |
| [DeepProbLog, Manhaeve et al., 2018](https://arxiv.org/abs/1805.10872), **A** | Learned neural predicates integrate with probabilistic logic | A learned score and a supplied logical relation must retain their distinct semantics; duplicate proof paths must not silently double probability mass. |
| [Friston, 2010](https://www.fil.ion.ucl.ac.uk/~karl/NRN.pdf), **T**, introduction/Box 1 | A proposed variational account connects perception, learning and action through explicit model/objective assumptions | Compare unified objectives as supplied structures. Do not make a disputed brain theory or one free-energy objective mandatory language semantics. |
| [Ouyang et al., 2022](https://arxiv.org/abs/2203.02155), **A** | Demonstrations, rankings and optimization encode a selected feedback process | Preference evidence needs its population, elicitation and objective. A preferred answer is not thereby a theorem, calibrated probability or universal human intent. |
| [Hinton and McClelland, 1987](https://proceedings.neurips.cc/paper_files/paper/1987/hash/afacc5db3e0e85b446e6c7727cd7dca5-Abstract.html), **A** | Learned internal representations evaluated through reconstruction | Encoders/decoders and learned spaces need a declared comparison criterion. Low reconstruction loss alone does not establish identifiable meaning. |

These sources differ in aims and commitments. A language should support their
mechanisms and comparisons without declaring one of them the true account of
intelligence. The historical [knowledge synthesis](../knowledge_frameworks.md)
remains the owner for logic, truth maintenance, ontologies, probability and
retrieval. Its Leibniz-to-modern route now connects to this model-building route.

### Distill The Recurring Mechanisms

A useful common vocabulary is **description, context, transformation and
qualified assessment**, with revision/action retaining ordinary state/effect
laws. It describes the following activities without requiring one universal
model class:

| Activity | Composition pressure | Fact that stays explicit |
| --- | --- | --- |
| Predict or imagine | A state/world description and a transition or generative law | Support, observation map, latent sharing and realization profile |
| Infer or explain | A query over alternatives constrained/reweighted by evidence | Hypothesis space, prior/constraints, likelihood and method coverage |
| Learn | A context-qualified transition over parameters, structure or reusable procedures | Objective, examples, selected search space and learning history |
| Abstract or analogize | Discover a reusable scoped term or an interpretation between structures | Preserved laws versus observed similarity; lost distinctions |
| Plan | Compose possible transitions and compare their consequences under an objective | Horizon, risk, cost, feasibility and actual action authority |
| Explore or ask | Compare prospective evidence for a chosen intellectual or practical objective | Information gain differs from decision value and novelty differs from learning progress |
| Remember | Retain descriptions, episodes, support and executable procedures | Retention/retrieval selection, access policy and revision basis |
| Reconsider | Change premises/model/objective and replay relevant consequences | Alternative support, non-invertible updates and stale evidence |
| Think about thinking | Compare reasoning methods under cost/coverage constraints | A budgeted proposal can remain incomplete; no guaranteed best universal reasoner |
| Communicate or teach | Relate an expression to another person's context and interpretation | Ambiguity, perspective and grounding; agreement is not automatic truth |

These are **derived activities**, not ten proposed opcodes. A probability
measure adds laws to a space; a hypothesis is a candidate description; a policy
is a proposed decision procedure. A neural network can provide any suitable
approximate map or proposal. Its implementation need not define those concepts.

Three unifications are tempting but wrong without further obligations:

1. “Inference is inversion.” A deterministic bijection, relational preimage,
   Bayesian conditional and causal counterfactual have different existence,
   uniqueness and support assumptions.
2. “Learning is just optimization.” Search, structure induction, memory revision
   and parameter fitting can use optimization; the objective and eligible
   updates still define what is learned. Stationarity need not mean a useful
   solution, and a predictive fit need not identify a causal mechanism.
3. “Everything is a weighted graph.” Boolean relation, probability measure,
   logical support and preference weights have different combination laws.
   A graph may store all four without making them interchangeable.

### Corner Cases That Challenge The Foundation

- An observation has zero modeled probability: keep “impossible under this
  model” rather than inventing a posterior or claiming the world is impossible.
- A model predicts observations but leaves two hypotheses indistinguishable:
  retain non-identifiability; a search result cannot manufacture uniqueness.
- A copied report and a fresh observation use different dependence models.
  Neither report IDs nor common provenance alone determine independence.
- Conditioning on an action is not replacing its causal mechanism. A
  counterfactual also needs a declared coupling to the same past world.
- A deterministic transformation merges two alternatives: sum finite mass,
  expose lost distinctions and refuse an inverse-equivalence claim.
- A shared latent parameter and per-call fresh randomness are different joint
  models. Ordinary memoization/rematerialization rules must not erase this.
- A learned abstraction matches examples but changes behavior elsewhere:
  label empirical fit separately from a checked semantics-preserving rewrite.
- A perfect measurement is irrelevant to the selected decision. Query novelty,
  entropy reduction, practical loss and cost need different objectives.
- A policy stops at its horizon; the environment has not necessarily terminated.
  A simulated successful action has not necessarily happened.
- A reward, surrogate loss or preference record changes: earlier “best” answers
  retain their old objective, not authority over the revised question.
- A posterior is numerically exact under a misspecified model. Mathematical
  exactness does not establish calibration, robustness or empirical adequacy.
- A method or retriever changes which alternatives were examined: carry search
  and selection history rather than imply that discarded alternatives were
  refuted or missing documents were false.
- Learning modifies a procedure with effects: preserve capture/lifetime/grant
  contracts; a learned executable artifact is not its own admission authority.
- Memory compaction or model unlearning removes storage but not necessarily
  influence. Existing learned-removal and adaptive-evaluation owners still apply.

### Broader Frontier: Acquisition, Not Claimed Coverage

| Area still to deepen | Primary entry point / current depth | Discriminating question |
| --- | --- | --- |
| Sequential decisions and partial observability | [Sutton/Barto 2018 complete draft](https://www.incompleteideas.net/book/bookdraft2018mar21.pdf), indexed original; full text unavailable in this pass | Can a belief state, recurrent policy and terminal/truncated outcome share ordinary context/completion rules? |
| Cognitive timing and activation | [ACT-R reference manual](https://act-r.psy.cmu.edu/actr7.x/reference-manual.pdf), indexed, not section-reviewed | How do latency and retrieval selection affect a compositional explanation without becoming truth values? |
| Predictive/energy-based world models | [LeCun 2022 position paper](https://openreview.net/pdf?id=BZ5a1r-kVsf), indexed, not section-reviewed | When can latent compatibility energies replace normalized likelihoods, and what question remains answerable? |
| Intrinsic motivation | [Schmidhuber creativity chapter](https://people.idsia.ch/~juergen/creativitybook.pdf), author abstract/index | Can learning progress be distinguished from unpredictable noise and from practical decision value? |
| Meta-learning and adaptive optimization | [Chen et al. 2017](https://proceedings.mlr.press/v70/chen17e.html), author abstract | Which learned method contracts survive a new task distribution or a longer horizon? |
| Continual learning | [Schwarz et al. 2018](https://proceedings.mlr.press/v80/schwarz18a/schwarz18a.pdf), indexed | Can new model revisions preserve prior task coverage without claiming semantic equivalence or guaranteed non-forgetting? |
| Multi-agent/game/epistemic models | Extend the knowledge synthesis's modal/game frontier; no new primary review here | Who knows which premise, what is publicly communicated, and which equilibrium/existence claim is actually checked? |
| Information/compression and universal induction | Extend existing Shannon/MDL/program-induction routes; no universal induction theorem reviewed here | Which encoding, prior, computability and approximation choices determine the claimed compression or generalization? |
| Embodied/developmental/social learning | Extend cognitive and interaction owners; selected model-building evidence only | Which meanings arise from intervention or teaching rather than passive examples? |
| Robust/set-valued uncertainty and formal learning bounds | Extend numerics/causal/evaluation owners; no bound implementation | When is a set of admissible answers more honest than a normalized probability? |

### Executed Finite Conceptual Slice

`python3 -m tools.finite_inquiry` now composes exact finite measures and kernels,
conditions a captured joint world on declared events, compares decision losses
and values a prospective measurement. Eleven focused checks include identity,
associativity, duplicate/correlated report handling, withdrawal, zero mass,
stale revisions and exhaustive contingent-policy comparison. A separate replay
uses unnormalized joint losses, avoiding the producer's conditional calculation.

This is an engine-free proof of composition at a finite slice, not a general
AI framework, empirical discovery result or accepted Nomi API. It adds no
random sampling, causal model, optimizer, matrix backend or external action.
The common source/reference/structure integration is the next AF1/R2 gate.

## Three Programs To Keep The Survey Honest

1. A beginner fits a scaler on training rows and predicts on held-out rows.
2. A production model uses a pinned feature snapshot, parameter/checkpoint
   artifact, explicit randomness and backend profile; it exports and serves
   through a schema-checked adapter.
3. A failure-heavy research assistant retrieves versioned documents, proposes
   a change, waits for review, and may encounter a lost tool acknowledgement.

The first needs a friendly API. The second needs reproducibility and resource
contracts. The third needs provenance, budgets, authority and uncertain-outcome
handling. They should compose through ordinary Nomi concepts, but they are not
the same kind of graph or statistical claim.

## Mechanism Survey

Depth is selected-mechanism review, not certification of an entire framework.
Edition-sensitive claims use pinned sources where the rolling route redirects.

| Primary system | Mechanism to extract | Nomi fork / hidden cost |
| --- | --- | --- |
| [scikit-learn pitfalls](https://scikit-learn.org/stable/common_pitfalls.html) | Fit/transform/predict and train-only preprocessing; pipelines in validation | Distinct specification/learned artifact versus one mutable estimator; a pipeline alone cannot fix wrong split design |
| [PyTorch 2.14 autograd](https://docs.pytorch.org/docs/2.14/notes/autograd.html) | Runtime graph of differentiable operations, recreated by execution | Dynamic trace versus staged program; saved tensors, mutation and derivative conventions need contracts |
| [JAX transformations](https://docs.jax.dev/en/latest/automatic-differentiation.html) and [sharp bits](https://docs.jax.dev/en/latest/notebooks/Common_Gotchas_in_JAX.html) | Transform functions for differentiation/vectorization/compilation | Transformation domain versus arbitrary pure Nomi callback; purity is necessary but not enough for supported primitives |
| [TensorFlow `tf.function`](https://www.tensorflow.org/guide/function) | Trace Python into graph execution, with specialization/retracing | Source execution at trace time versus repeated graph execution; ordinary side effects cannot silently change phase |
| [Keras 3 layers](https://keras.io/api/layers/base_layer/) | Recursively composed computation plus trainable/non-trainable state and dtype policy | Structure/state/initialization/mode separation; a callable can build or update state |
| [Flax NNX 0.12.4 graph](https://flax.readthedocs.io/en/v0.12.4/api_reference/flax.nnx/graph.html) | Split graph definition and state; merge back into a module graph | Explicit state-bearing versus functional interface; do not mix Linen/NNX contracts |
| [Optax transformations](https://optax.readthedocs.io/en/latest/api/optimizers.html) | Optimizer initialization, state and update transformations | Parameter identity, optimizer state, step count and update application are independent |
| [JAX typed RNG keys](https://docs.jax.dev/en/latest/jep/9263-typed-keys.html) | Typed random keys with generator identity | Explicit streams/subkeys versus ambient RNG; branch topology and key reuse remain semantic choices |
| [Hugging Face datasets](https://huggingface.co/docs/datasets/en/about_mapstyle_vs_iterable) | Map-style versus iterable datasets and distinct loading/access behavior | Snapshot/indexed collection versus consumable stream; ordering/shuffle/state/cancellation policies |
| [TFX guide](https://www.tensorflow.org/tfx/guide) | Validation, transform, training, evaluation and serving components | Data/schema/model artifacts versus orchestration; evaluation does not grant deployment authority |
| [MLflow registry](https://mlflow.org/docs/latest/ml/model-registry/) | Model versions, lineage and mutable aliases | Human alias versus resolved version/digest; registry provenance is not a proof of fitness |
| [ONNX concepts](https://onnx.ai/onnx/intro/concepts.html) | Graph interchange, typed values, control-flow subgraphs and per-domain opsets | Export compatibility versus semantic equivalence or portability of arbitrary code |
| [StableHLO specification](https://openxla.org/stablehlo/spec) | Defined tensor/control-flow operation semantics | A numeric domain IR versus Nomi's entire Core; unsupported operations/profiles must reject honestly |
| [Pyro 1.9.1 historical introduction](https://pyro.ai/examples/intro_part_i.html) and [inference](https://pyro.ai/examples/intro_part_ii.html) | Named random variables, observation and inference | Distribution/model versus sample versus posterior approximation; tutorials are now marked deprecated |
| [Gymnasium environment](https://gymnasium.farama.org/api/env/) | Step/reset, observations/actions/rewards, terminated versus truncated | Environment transition versus prediction; stopping at a budget is not reaching a terminal state |
| [LangGraph checkpointers](https://docs.langchain.com/oss/python/langgraph/checkpointers) and [functional API](https://docs.langchain.com/oss/python/langgraph/functional-api) | Persisted thread state, task-result restoration and resume | Checkpoint/state store versus exactly-once external tool action; model outputs need recording |
| [vLLM 0.20.1 prefix cache](https://docs.vllm.ai/en/v0.20.1/design/prefix_caching/) | Reuse KV prefix computation with explicit cache context/salt | Prefix work versus final answer; tenant isolation, eviction and model/tokenizer context |
| [PyTorch reproducibility](https://docs.pytorch.org/docs/2.14/notes/randomness.html) | Control some nondeterminism within a pinned platform/profile | Same seed versus bitwise cross-device/release equivalence; reduction and kernel policy matter |

This spans classical supervised learning, differentiable programming, model
state, optimization, data ingestion, production artifacts, interchange,
probabilistic inference, reinforcement learning and generative-agent execution.
Distributed collectives, privacy accounting, causal inference, multimodal
alignment and specialized hardware still need their own concrete admission
programs; they are not silently covered by mentioning a framework.

## Four Different Things Called A Model

The [generic-operation hierarchy](../generic_operations.md) puts differentiate,
vectorize, trace and compile beside map/fold/cache rather than treating them as
universal Function methods. Shape, supported primitives, state/randomness,
staging and host profiles remain this domain's contracts; a pure callback alone
does not establish transformation eligibility.

| Artifact | Owns | Does not establish |
| --- | --- | --- |
| Model specification | Architecture/algorithm, hyperparameters, input/output contract | Learned parameters or predictive validity |
| Learned artifact | Parameters and other inference state, training evidence, feature contract | Ability to resume training exactly |
| Training checkpoint | Parameters, optimizer/scheduler state, RNG/data-position/state and step basis under a profile | Cross-hardware deterministic resume, or retained input access |
| Evaluation record | Dataset/split identity, metric definition, uncertainty and observed results | Truth, fairness, causality, safety or authorization to deploy |

Keras and Flax expose state as well as computation; Optax has its own optimizer
state. **Nomi inference:** make state crossing visible even when implementation
uses mutable accelerator buffers internally. Ordinary immutable `data` need
not copy every buffer on every step: ownership/aliasing and controlled mutation
must be defined at the adapter boundary, not inferred from wrapper immutability.
[Keras](https://keras.io/api/layers/base_layer/),
[Flax](https://flax.readthedocs.io/en/v0.12.4/api_reference/flax.nnx/graph.html),
[Optax](https://optax.readthedocs.io/en/latest/api/optimizers.html).

Persisting weights alone must not be named an exact training-resume operation.
Nor should deserializing a checkpoint load arbitrary executable objects or mint
GPU/network authority. Codec/profile compatibility, integrity, trust and current
permissions are separate checks.

## Differentiation Is A Transformation With A Domain

Candidate metalanguage, not accepted Nomi generic/function-type syntax:

```text
NumericProgram[InputShape, OutputShape, ScalarPolicy]
  = checked numeric operations + explicit binders/state + source mapping
differentiate(program, with_respect_to, derivative_policy)
  = Result[DerivativeProgram, UnsupportedOrInvalid]
compile(program, backend_profile)
  = Result[ExecutableArtifact, CompileError]
execute(artifact, arguments, device_grant, limits)
  = Result[CompletedNumericResult, ExecutionError]
```

JAX transforms functions under its supported/pure operation model. PyTorch
constructs an autograd graph from the operations actually executed. TensorFlow
tracing separates Python execution from later graph execution. None is evidence
that arbitrary Nomi closures can be translated or differentiated.
[JAX](https://docs.jax.dev/en/latest/notebooks/Common_Gotchas_in_JAX.html),
[PyTorch](https://docs.pytorch.org/docs/2.14/notes/autograd.html),
[TensorFlow](https://www.tensorflow.org/guide/function).

Candidate contracts before admitting `grad` as a standard operation:

- Specify which inputs are differentiable and what happens to integers,
  discrete choices, missing values and effects.
- Keep forward-mode JVP, reverse-mode VJP and scalar-loss gradient distinct;
  a scalar gradient is not every possible Jacobian interface.
- State derivative conventions at nondifferentiable points, stopped gradients
  and custom derivative rules. A returned number is not a proof of smoothness.
- Preserve primal/derivative source locations and shape/unit meaning; gradients
  depend on the quantity and coordinate basis differentiated against.
- Separate tracing, checking, compiling and invoking. Report specialization
  conditions; shape/control-flow changes may require a new checked artifact.
- Bound saved intermediates and rematerialization; replaying a region must not
  repeat host effects or alter random choices unless its explicit contract says so.
- Define higher-order transformation composition and rejection. `grad`, batch
  mapping and compilation cannot be reordered merely because syntax nests well.

No global quotation of lambdas, ambient tensor evaluator, or hidden meaning of
`|>` is proposed. First compare explicit operator values and one checked
function subset; use a scoped numeric tool only when the long form fails real
programs. The [function-contract packet](../../design/function_contracts.md)
owns callbacks/effects/captures; numeric laws remain open in D3/question 9.

## Shape, Dtype, Units And Placement Are Independent

An array has several potentially relevant contracts:

```text
element scalar policy
+ rank/shape and named-axis identity
+ units/coordinate frame and missing/mask policy
+ layout/strides/aliasing and sparse/ragged representation
+ device/memory space and sharding
+ numerical/reduction/error policy
```

An axis called `time` can denote observations, tokens or simulation steps.
Equal extents do not make axes interchangeable. Broadcast should be an explicit
law rather than a silent repair of unrelated dimensions. A tensor buffer is not
a typed table schema, and a mask is not a universal `Option` encoding.

StableHLO is evidence that a numerical operation language can have specified
semantics. ONNX is evidence for interchange under operation-set domains and
versions, including control flow. **Inference:** retain domain IRs behind
checked adapters rather than pretend Nomi Core must directly be ONNX or HLO.
Translation requires a capability/operation matrix, diagnostics for rejected
features, and differential value/error/precision fixtures.
[StableHLO](https://openxla.org/stablehlo/spec),
[ONNX](https://onnx.ai/onnx/intro/concepts.html).

Device placement and host transfer can consume time, memory and authority.
Asynchronous dispatch completion is not necessarily completed device work.
These are Nomi candidate obligations, not measured performance facts. Browser
profiles must explicitly reject unsupported devices/operators, not silently
perform host-rounded arithmetic under the same portability claim.

## Data Splits Connect ML To Temporal Data

scikit-learn explicitly warns against fitting preprocessing on test data and
recommends splitting first. Its pipelines help apply fit/transform correctly
inside validation. They cannot infer whether patient/entity groups, temporal
boundaries or future features were selected appropriately.
[Primary pitfalls](https://scikit-learn.org/stable/common_pitfalls.html).

Candidate lifecycle:

```nomi
# Fictional APIs; no implicit fit or ordinary-call quotation.
split = learning.temporal_split(feature_snapshot, cutoff=cutoff)?
scaler = learning.fit_scaler(split.training)?
train = learning.transform(scaler, split.training)?
test = learning.transform(scaler, split.held_out)?
fitted = learning.fit(model_spec, train, seed=seed, profile=profile)?
evaluation = learning.evaluate(fitted, test, metric=metric)?
```

The local arithmetic counterexample is intentionally small: training values
`[1,3]` have mean 2; including held-out value 100 produces mean `104/3`.
Changing the held-out value must not change a fitted training-only mean.
This is a leakage discriminator, not an estimator implementation or evidence
of model accuracy.

Point-in-time features additionally need both **business/event time** and
**availability/system time**. A measurement valid yesterday but recorded
tomorrow is unavailable to yesterday's prediction. Corrected hindsight and
reproducing an original decision are different queries; the data chapter's
bitemporal basis supplies that distinction. Bind label horizon, feature schema,
entity/split IDs and preprocessing artifact to training/evaluation evidence.
No metadata proves the chosen experimental design is scientifically sound.

### Adaptive Evaluation: Feedback Is Also A Dependency

> Research-depth extension checked 2026-10-04; named subexperiment
> **ML1 / adaptive-holdout**, refining DW5 and questions 8/9/17. No evaluation
> API, statistical guarantee or mandatory experiment policy is admitted.

Training-only preprocessing, entity/time splits and feature availability above
prevent important leakage paths. They do not describe a developer choosing
features, prompts, thresholds, metrics or stopping time **after seeing evaluation
feedback**. The evaluator's dataset can be absent from the training function's
read set while influencing the delivered model through human or agent decisions.
This is a research gap in the evaluation record's meaning, not evidence that
the existing fit/transform distinction is wrong.

Selected primary evidence has three scopes. Cawley and Talbot (**2010**) analyze
overfitting a model-selection criterion and subsequent evaluation bias.
[Primary paper](https://jmlr.org/papers/v11/cawley10a.html).
Dwork et al. (**2015**, arXiv v2) study adaptive holdout reuse and propose
procedures with statistical guarantees under their stated assumptions; reuse
is not universally forbidden or safe. [Primary paper](https://arxiv.org/abs/1506.02629v2).
The scikit-learn **1.9.1** nested-CV example separates inner parameter selection
from outer evaluation. It demonstrates a selected procedure, not immunity to
repeatedly redesigning that procedure using its outer scores.
[Official example](https://scikit-learn.org/1.9/auto_examples/model_selection/plot_nested_cross_validation_iris.html).
These sources were checked on the date above; no foreign example was executed.

Original finite counterexample: holdout labels are four binary values. Prepare
all sixteen possible prediction vectors without reading those labels, score
each, and publish only the best score. One vector matches perfectly for **every**
possible holdout. No fit call read the holdout, yet selecting the winner did.
For fresh independent fair binary labels, that selected fixed prediction rule
still has expected accuracy one half. This constructed probability model is not
a measured result, a claim about real datasets or a useful learning algorithm.

The counterexample separates selection from prediction. Additional edges to
include are changing the reported metric after results arrive, reporting only
successful seeds, reading a public benchmark leaderboard, using test errors to
rewrite an LLM prompt, and repeatedly checking a conventional fixed-sample claim
until a desired result appears. A sequential/adaptive procedure may be valid
under its own stopping/selection assumptions; the objection is presenting it
as an independent fixed procedure without those assumptions.

**Competing candidate contracts**, ordinary library evidence values first:

| Candidate | Visible claim | Cost / rejecting observation |
| --- | --- | --- |
| Explicit selection set plus independent final evaluation | Selection feedback and final assessment have separate declared purposes/bases | Final feedback influences another candidate while its record still says independent assessment |
| Complete bounded search/selection procedure evaluated externally | Evaluation concerns a procedure, including its search, rather than just the selected parameter vector | Search changes using outer feedback without changing the procedure/evidence basis |
| Profiled adaptive evaluation procedure | Named algorithm, assumptions, feedback interface, stopping rule and scope support a specific statistical claim | Plain score caching, query counts or a history log are presented as that algorithm or its guarantee |
| Exploratory observation only | Preserve scores and incomplete selection history without asserting confirmatory validity | A useful exploratory record is mislabeled invalid merely because it does not support a stronger claim |

An evaluation dataset is not necessarily a linear consumable resource. Reading
it twice does not destroy its values; it changes which independence/selection
claims are justified. A policy may restrict feedback exposure, but inspection
must explain the evidence obligation instead of pretending `evaluate` inherently
uses up data. Missing human/agent decision history is **unknown exposure**, not
proof no adaptation happened. A digest of code cannot record an unobserved
conversation or certify an analyst's independence.

Candidate normal form, **protocol metalanguage**, not proposed exports:

```text
state evaluation purpose, population, selection and stopping assumptions
-> bind dataset/split and candidate-or-search-procedure identity
-> record permitted feedback exposures and resulting decisions where observed
-> freeze the declared subject before independent assessment, or select an
   explicitly justified adaptive procedure
-> retain all relevant outcomes and history coverage under privacy policy
-> publish observation plus the narrower claim actually supported
```

| Program / protocol | Observation and inspection | Failure-heavy discriminator |
| --- | --- | --- |
| Beginner: select on validation, then assess a fixed candidate | Show distinct dataset purposes and which score selected the model | User tunes again after final score; the next claim must account for that feedback |
| Production: evaluate a complete search/preprocessing procedure | Pin search, metric bundle, split/entity/time rules and observed feedback history; keep outer outcomes separate | Selected seeds/folds disappear, or repeated outer comparisons are labeled one untouched assessment |
| Failure-heavy: agent edits prompts after benchmark feedback | Bind prompt/candidate revisions, feedback receipts and known exposure scope | Resume hides earlier feedback or presents an incomplete log as proof of independence |

Candidate diagnostics distinguish `score observed for selection` from
`independent assessment not established: feedback history is incomplete`.
Views should identify metric direction, population and procedure scope; a green
score does not certify generalization, fairness, causality or deployment fitness.
These records compose with [shared-origin uncertainty](../notation_atlas.md#correlated-uncertainty-shared-origin-is-part-of-the-model)
and [learned-state erasure](#data-erasure-and-learned-influence-are-different-operations);
do not retain personal labels or prompts merely to make a provenance graph full.

**Falsifiers and stop/removal criteria:** compare the sixteen-vector winner
with an independently chosen fixed vector; expose the same score through CLI,
dashboard and agent; change selection/metric/stopping rules after feedback;
omit prior exposures; and replay an evaluation record against another candidate.
Reject a universal `validated=true` wrapper if it cannot name the assessed
subject and claim. Prefer exploratory records when independent/adaptive claims
cannot be supported; do not automatically prohibit legitimate reuse. Stop
before stronger guarantees without a domain-qualified experimental procedure.

**Unperformed:** the finite model has not been captured or executed here. No
estimator, nested-CV/adaptive evaluator, exposure enforcement, statistical proof
audit or human repair study has been performed. ML1/DW5 remain open.

## Randomness, Checkpoints And Reproducibility

JAX's typed keys distinguish generator implementations, and its explicit-key
model makes random state visible. PyTorch's documented reproducibility limits
include release/platform differences and CPU/GPU behavior despite identical
seeds. A Nomi `Seed` should therefore not be a universal reproducibility token.
[JAX key proposal](https://docs.jax.dev/en/latest/jep/9263-typed-keys.html),
[PyTorch limits](https://docs.pytorch.org/docs/2.14/notes/randomness.html).

Separate claims:

| Claim | Minimum evidence to ask for |
| --- | --- |
| Repeatable input selection | Snapshot/split/ordering and data-loader position |
| Repeatable random choices | Algorithm/key derivation/stream ownership and recorded state |
| Repeatable numerical result in one profile | Code/operators, dtype/reduction/kernel/device versions and declared nondeterminism |
| Equivalent result across profiles | Independent tolerance/exactness contract and executed differential vectors |
| Scientifically replicable conclusion | Experimental assumptions, population, metric/uncertainty and independent study |

For distributed or dynamically scheduled work, derive random-stream identity
from stable logical work identity under a specified scheme if that is the
chosen policy; worker arrival order should not silently choose samples.
Reusing a key deliberately versus accidentally must be visible. A key digest
does not establish statistical independence, privacy or cryptographic security.

Gradient checkpoint/rematerialization is a memory/recompute strategy, training
checkpoint is persisted state, and agent checkpoint is recorded execution state.
Calling all three time travel would conceal the relevant guarantees.

### Data Erasure And Learned Influence Are Different Operations

> Research-depth extension checked 2026-10-04; named subexperiment
> **ML4 / learned-removal**, also refining ML5, DT3/DT4 and DW5. This is not a
> privacy-law interpretation, generic unlearning API or claim of certified erasure.

The [data/time failure cases](dependencies_and_time.md#failure-cases-that-must-shape-the-design)
already distinguish retained history from current read permission, and
[messaging ME24](messaging_and_events.md#edge-cases-and-falsifiers) includes
payload copies, snapshots and projections. Privacy accounting remains explicitly
outside this survey's selected mechanisms. The additional composition question
is narrower: what happens to **learned artifacts and training descendants** when
an input contribution is withdrawn? Deleting a source record, revoking access,
invalidating an artifact, retiring serving endpoints and removing learned
influence are different operations with different evidence.

Selected primary evidence: Guo et al. (**2020**) define certified removal relative
to a specified training procedure and develop a mechanism for linear classifiers;
that does not certify arbitrary model updates. [Primary paper](https://proceedings.mlr.press/v119/guo20c.html).
Bourtoule et al. (**2021**, arXiv v3 from 2020) propose SISA training to limit the
training scope affected by removal and reduce retraining work. This is evidence
that removal cost can shape training architecture, not a universal inverse of
`fit`. [Primary paper](https://arxiv.org/abs/1912.03817v3).
Both were checked on the date above; no removal method or benchmark was executed.

Original deterministic arithmetic oracle:

```text
training contributions: a=0, b=100; exact fitted mean=50
delete stored contribution b, keep existing learned artifact: prediction=50
retrain the same exact mean procedure on retained a: prediction=0
```

This oracle is about a declared training procedure, not whether a model knows
a concept or whether a particular legal duty is satisfied. An exact sum/count
update can match recomputation for this bounded mean model if its contribution
basis, arithmetic and empty-result contract are preserved. It is not a removal
law for arbitrary optimizer steps. For stochastic training, identical weights,
matching output distribution under a stated definition, approximate distance
to retraining and observed task-score change are distinct possible claims.

**Candidate operation boundaries**, none admitted:

| Operation | Evidence it could own | Does not establish |
| --- | --- | --- |
| Revoke access / retire artifact | Current read/serve policy and endpoint outcome | Existing copies or learned influence disappeared |
| Delete owned stored records | Defined storage scope, descendants searched and deletion/expiry outcome | An imported copy, inaccessible backup or model state is covered automatically |
| Invalidate descendants | Known lineage basis, affected artifact IDs and permitted future use | Lineage is complete or an invalidated artifact was physically removed |
| Rebuild under retained basis | New artifact, retained contributions, training edition/profile and outcome | Bitwise equality across profiles or elimination of all ability to infer a fact |
| Supported removal update | Selected algorithm, reference procedure, assumptions and exact/approximate/certified claim | A low forgetting-task score is a general removal certificate |

A removal request needs a declared unit: record ID, subject, feature contribution,
client update or another domain-owned selection. Duplicated records and retained
correlated examples expose why removing one contribution does not imply the
model can no longer predict the same information. Do not silently reinterpret
"delete record b" as "erase every similar concept". Repeated requests need
stable identity and idempotent bookkeeping; an unknown prior outcome is not a
reason to subtract the contribution again.

Competing initial contracts are: **invalidate/retire and rebuild**, which avoids
claiming unsupported updates but may lose availability; **support only named
removal-capable training profiles**, which can give narrower guarantees with
architecture/state costs; or **record a domain-approved approximate update**,
which must expose its weaker comparison and residual uncertainty. A serving
policy may forbid the old artifact before a replacement is ready. Policy
selection and legal adequacy remain outside a generic language library.

The initial Nomi owner is an ordinary learning/storage library with profiled
adapters. It reuses owned artifact values, explicit Result outcomes, effects,
resource/task lifetimes and current capabilities; no global `erase` keyword or
universal value-history mechanism is proposed. D1-D3 remain prerequisites for
typed state, callbacks, retained regions and numeric comparison contracts.

Candidate normal form, **protocol metalanguage**:

```text
resolve authorized request and contribution selection under an explicit basis
-> enumerate known source/artifact/checkpoint/cache/export descendants and gaps
-> apply the declared access/retention/serving policy
-> select rebuild or a supported removal procedure with its reference claim
-> record new artifact, outcome, residual/unavailable scope and review basis
-> publish/retire through current authority; reconcile uncertain outcomes
```

Lineage can guide that work without proving it found every copy. An old training
checkpoint can reintroduce a removed contribution on resume; an export, distilled
model, fitted preprocessing artifact or inference cache may have another owner.
Erasure evidence itself must not retain the sensitive content it purports to
remove. A redacted contribution reference can be useful, but its identity,
retention and disclosure policy still need an owner.

| Program / protocol | Required observations | Adversarial edge |
| --- | --- | --- |
| Beginner: remove one exact-mean contribution and refit | Old artifact differs from retained-source recomputation; empty retained input has typed absence/error | Deleting the row is reported as updating the prediction |
| Production: withdraw a contribution across a declared artifact lineage | Contribution/basis identity, selected claim, known descendants, unavailable copies and replacement/retirement outcome | A stale checkpoint resumes, or a serving alias still resolves to the old artifact |
| Failure-heavy: partial deletion with lost replacement acknowledgment | Separate revoked use, unavailable evidence, incomplete deletion and unknown publication | Retry subtracts twice, success hides an external export, or replay restores an old grant |

Inspection should say `source removed; artifact still derived from prior basis`
or `removal comparison unavailable: reference training inputs expired`, not one
Boolean `forgotten`. Keep numerical/evaluation observations separate from the
removal claim; [adaptive evaluation](#adaptive-evaluation-feedback-is-also-a-dependency)
also applies when a removal method is chosen using the reported score.

**Falsifiers and stop/removal criteria:** test duplicate and repeated requests,
empty retained data, stale preprocessing/checkpoints, incomplete lineage,
changed training profile, retained equivalent examples, inaccessible exports
and unknown retirement/publication outcomes. Reject generic `unfit` or universal
inverse-update abstractions without a named reference law. Stop a certificate
claim when assumptions, scope, verifier or reference comparison are unavailable;
report the narrower observed action rather than fabricate proof. Remove a common
wrapper if it collapses access control, storage erasure and learned-state change.

**Unperformed:** no probe capture, training/removal engine, lineage-completeness
checker, privacy accounting, certificate verifier, serving adapter or physical
deletion test has been run. The arithmetic oracle is designed evidence only;
this extension neither closes ML4/ML5 nor expands their implementation status.

## Generative AI Is An Effectful Evidence Producer

MLflow aliases are mutable references to model versions. LangGraph distinguishes
thread checkpoints from cross-thread stores; its functional API documents
restoring task results during resume. vLLM's versioned prefix-cache design
includes request salt/context in reuse. These are useful mechanisms, but none
makes a model answer trustworthy or a tool action authorized.
[MLflow](https://mlflow.org/docs/latest/ml/model-registry/),
[LangGraph persistence](https://docs.langchain.com/oss/python/langgraph/persistence),
[functional replay](https://docs.langchain.com/oss/python/langgraph/functional-api),
[vLLM cache](https://docs.vllm.ai/en/v0.20.1/design/prefix_caching/).

Candidate inference request identity includes resolved model/adapter version,
tokenizer, prompt/template/messages, decoding policy, retrieved evidence versions
and relevant runtime profile. This is a context inventory, not a recipe that
guarantees identical answers from an unpinned remote provider. Record observed
responses when replay needs them. A prefix-cache hit does not imply a complete
answer cache, cross-tenant permission or deterministic decoding.

The assistant program needs `Request -> Observation -> Proposal -> Checked
Action`, not natural-language source that automatically executes. Retrieval
results and generated text are untrusted data; tool schemas constrain shape but
not purpose, truth or authority. Model/tool budgets, cancellation, moderation,
review scope, privacy and unknown remote outcomes remain explicit. Looping
agents need a state-transition/progress owner, not forced acyclicity.

## Other Learning Modes Must Keep Their Own Laws

Pyro's historical tutorial separates stochastic models, observations and
inference machinery. An approximate posterior sample is neither a certain fact
nor a deterministic value justified by a schema. Gymnasium separates MDP
termination from external truncation because learning algorithms interpret
them differently.
[Pyro model/inference](https://pyro.ai/examples/intro_part_ii.html),
[Gymnasium step](https://gymnasium.farama.org/api/env/).

**Nomi inference:** distributions, samples, inference diagnostics, optimization
objectives and environment transitions can be nominal domain values under the
same Result/effect/resource framework. They do not all reduce semantically to
`predict(Text) -> Text`, a confidence Float, or one Boolean success flag.

## Candidate Primitives And Experiments

| Candidate | Initial layer / core pressure | Adversarial discriminator |
| --- | --- | --- |
| Numeric expression plus transformation contract | Library/scoped numeric tool; D1 callbacks and D3 scalar laws | Unsupported operation/effect, wrong differentiation variable, nondifferentiable point |
| Tensor shape/axis/dtype/unit contract | Library/protocol, not a global glyph language | Equal-size swapped axes, implicit broadcast, unsupported browser precision |
| ModelSpec / LearnedArtifact / TrainingState | Nominal library values and explicit update | Weights-only resume, stale preprocessing, changed schema, train/eval mode |
| Random stream/key policy | Explicit library value/capability | Reordered work, reused key, backend/version mismatch |
| Dataset/split/feature basis | Data/history contracts composed with learning | Held-out influence, group leak, future-arriving valid fact |
| Evaluation record | Evidence envelope with domain-owned payload | Empty/biased evaluation, metric direction, wrong population, uncertainty omitted |
| Model/serving request artifact | Codec/profile/resource adapters | Mutable alias, untrusted checkpoint, data movement failure, stale tokenizer |
| Agent transition/proposal | Workflow and interaction contracts, fresh authority | Resume repeats send, malicious retrieved instruction, reviewed payload changed |

| ID | Deliverable | Stop or promotion gate |
| --- | --- | --- |
| ML1 | Type the train-only preprocessing long form and held-out counterexample, including temporal availability | Stop if schema/split/evidence identity is unbound; no automatic fit |
| ML2 | Compare explicit numeric expression values with a checked function subset for differentiation | Three programs and unsupported-effect/shape diagnostics; no claim pure implies translatable |
| ML3 | Independent scalar/shape/gradient golden vectors through one established AD engine adapter | Record exact/tolerance/profile rules; custom AD engine is not the first implementation |
| ML4 | Fake checkpoint/restore model: parameters plus optimizer/RNG/data position versus weights only | Explicitly distinguish inference restore and training resume; no bitwise guarantee without execution |
| ML5 | Version-pinned serving and retrieval/agent proposal with lost acknowledgement and tenant cache context | No replayed permission/tool action; exact review/current grant checked independently |
| ML6 | Small export/import comparison against pinned ONNX or StableHLO profile | Unsupported operations reject; source maps and differential errors/values before a runnable sample |

DW5 remains the original lifecycle question. These extensions narrow it and
questions 4/7/8/9/12/15/17 rather than select a framework or admit syntax.
The immediate dependency is D1-D3 closure, not adding training keywords.

## Framework Authors: Rules, Transformations And Implementations

Framework authors add operators, abstract evaluators, transformations, backends,
state carriers or export adapters. A forward API alone does not establish
gradient, batching, tracing, aliasing or distributed behavior. The following
are selected mechanisms, not executed foreign examples or complete audits.

| Primary source, checked 2026-10-10 | Mechanism / scope | Nomi inference and fork |
| --- | --- | --- |
| [PyTorch custom operators](https://docs.pytorch.org/tutorials/advanced/python_custom_ops.html) | Schema/aliasing, metadata-only fake kernels and separate autograd/batching registrations; registration checks differ from numerical/gradient checks | Semantic entry plus optional capabilities versus a backend callback implicitly defining everything |
| [JAX custom derivative JEP](https://docs.jax.dev/en/latest/jep/2026-custom-derivatives.html) | Historical custom-transform/batching conflict and a design preserving custom derivative calls; serialized re-transformation is outside that proposal's scope | Preserve rule identity rather than inline away an intended derivative; no portable arbitrary-callback claim |
| [JAX extension API](https://docs.jax.dev/en/latest/jax.extend.html) | Internal extension machinery explicitly lacks cross-release compatibility guarantees | Pin adapters/toolchains instead of making framework internals Nomi's permanent boundary |
| [JAX symbolic shapes](https://docs.jax.dev/en/latest/export/shape_poly.html) | Export dimension variables with limited constraint reasoning | Proof/unknown/runtime obligation versus compatibility guessed from a sampled shape |
| [PyTorch export](https://docs.pytorch.org/docs/stable/export.html) | Capture with dynamic shape specifications and constraint checks | Checked source subset with specialization evidence versus expression constructors |
| [JAX AD and sharding](https://docs.jax.dev/en/latest/301/sharding-ad.html) | Cotangent placement relates to primal placement; pending sums retain required backward meaning | Track replicated, sharded and unreduced values; a communication-free primal may require backward communication |
| [PyTorch DDP design](https://docs.pytorch.org/docs/2.14/notes/ddp.html) | Gradient synchronization through buckets/hooks with coordinated collective order | Participant/order contract beyond map or task groups; weighted objective remains separate |
| [PyTorch AMP examples](https://docs.pytorch.org/docs/2.14/notes/amp_examples.html) | Autocast, scaling, accumulation, unscaling and optimizer steps | Explicit arithmetic/transition policies versus a dtype label claiming a complete training contract |
| [DLPack Python specification](https://dmlc.github.io/dlpack/latest/python_spec.html) | Tensor sharing, lifetime responsibility and stream coordination | Zero-copy adapters need alias/lifetime/completion contracts; immutable descriptions are not immutable storage |
| [Triton matrix multiplication](https://triton-lang.org/main/getting-started/tutorials/03-matrix-multiplication.html) | Blocked kernels with masks and accumulation choices | Kernel tool behind host/layout/numerical profiles; its demonstrations are not Nomi benchmarks |
| [ONNX IR](https://onnx.ai/onnx/repo-docs/IR.html) | Versioned operator-set dependencies; serialized graph distinct from internal representation | Export/receiving support remain explicit; serialization does not establish execution equivalence |

### Discriminators Before A General Tensor Runtime

1. **Axis identity:** contract `batch × features` with `features × outputs`.
   Replace the weight's contracting axis with equal-size `tokens`. Extents
   alone cannot detect the intended error. Nominal axes cost explicit conversion.
2. **Abstract versus concrete rule:** declare one output shape and implement
   another. Metadata checking and kernel evidence must remain separate; repeating
   a declaration does not validate it. Test empty/non-contiguous/aliasing cases.
3. **Derivative versus transpose:** use `f(w,x,b)=w*x+b` for an exact derivative
   oracle and separately check JVP/VJP pairing. A mutually consistent but wrong
   linear map and transpose can pass pairing.
4. **Batch coupling:** independent per-example losses differ from a
   batch-normalized/coupled objective. Retain axes, state/mode and objective;
   transformations do not commute by notation alone.
5. **Uneven reduction:** shard values `[0]` and `[10,10,10]`. Mean of shard
   means is 5; global mean is `15/2`. Weighting and placement need an objective
   contract, not just a collective name.
6. **Stateful replay:** repeat a region with dropout/model state and interrupted
   checkpoint publication. Rematerialization, retry and resume have distinct laws
   for randomness, progress and visible state.
7. **Profile migration:** change an operation, tokenizer, derivative, precision
   or layout while retaining an architecture label. Reject stale claims; preserve
   narrower artifacts still useful for inspection.

These are prepared comparisons, not executed ML-engine or participant trials.
The mean arithmetic is a finite counterexample, not a distributed experiment.
Framework usability needs separate authoring/repair/handoff trials.

### One Integration Path

Prefer semantic spaces, checked programs, transformation rules, explicit state
transitions, qualified realization and scoped evidence over unrelated keywords.
A shared envelope supplies identity/revision/navigation; domain rules supply
meaning. Authors should inspect missing capabilities before implementation.
Library users can defer those details until a composition or portability fails.

The [shape probe](../../../tools/ai_probe.py) executes the first axis discriminator
on a named linear-loss description without arrays, weights or an AI engine.
It provides immutable snapshots, dependency explanations and optional **declared**
backend coverage. Distinct equal-size axes and implicit broadcast refuse; every
intermediate is checked. This is not tensor arithmetic, AD, abstract evaluation
of arbitrary source or independent replay.

AF0-AF6 in the [design owner](../../design/ai_frameworks.md#integration-and-gap-analysis)
refine ML1-ML6. Next compare expressions with a checked numeric function subset,
then use one established engine for independent scalar/shape/gradient vectors.
The scientific polynomial probe is one exact oracle, not justification for
replacing ML3 with a custom general AD engine.
