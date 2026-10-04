# AI And ML: Transformations, State And Evidence

> Status: selected primary research and Nomi candidates, not accepted tensor,
> differentiation, model, training, inference or agent APIs.
>
> Documentation checked 2026-10-04. Foreign snippets are illustrative and
> unexecuted; [local probes](composition_experiments.md) are original bounded
> models, not ML-engine conformance or empirical model-quality evidence.

[Dossier](README.md) · [Data/time](dependencies_and_time.md) ·
[Numerics](../features/numerics.md) · [Domain composition](../domain_composition.md)

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
