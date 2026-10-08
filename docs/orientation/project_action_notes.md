# Project Action Notes

> Status: proposed, notes-only action detail; not implementation, semantic
> acceptance, release approval or a second priority registry.
>
> Planning baseline: `3184ef3`; drafted 2026-10-05, reviewed 2026-10-08.
> All checkboxes describe
> future work, not actions executed or results obtained by this notes pass.

## Navigation

| Area | Detail |
| --- | --- |
| Planning method | [Task definition](#task-definition-rules), [all scales](#actions-at-every-scale), [dependency gates](#shared-dependency-and-promotion-rules) |
| A01-A10 | [Product, language, source, types, calls, data and patterns](#a01-product-scope-and-milestones) |
| A11-A20 | [Completion, resources, authority, tasks, libraries, sessions and diagnostics](#a11-failure-control-transfer-and-resumable-completion) |
| A21-A23 | [Playground, Jupyter and editor experience](#a21-playground-documents-and-interaction) |
| A24-A32 | [Verification, performance, packages, release, security and maintenance](#a24-tests-oracles-differential-evidence-and-fuzzing) |
| A33 | [Text interfaces and DSL boundaries](#a33-text-interfaces-strings-and-scoped-dsls) |
| Domain growth | [Conditional extension recipes](#domain-extension-recipes) |
| Research execution | [Eleven gap units](#eleven-research-units-to-turn-into-evidence) |
| Larger changes | [Rewrite triggers](#bounded-redesign-and-rewrite-triggers) |
| Closure | [Evidence tiers](#completion-evidence-to-prepare), [handoff](#handoff-and-task-closure) |

## Ownership And Use

These notes expand the existing [A01-A33 work map](project_roadmap.md#whole-project-work-map)
into local tasks and cross-system completion criteria. The roadmap still owns
priorities, delivery order and milestone receipts; the
[redesign agenda](../design/redesign_agenda.md#ordered-design-closure) owns D0-D7.
Do not schedule a second independent queue from this document. Move a selected
task's exact contract and evidence into its existing semantic/engineering owner,
then link its completion from the roadmap rather than check off a whole subsystem.

Read the [latest runtime receipt](project_roadmap.md#scoped-runtime-continuation-receipt)
before treating an older audit finding as pending. Hosted call/default binding,
synchronous scope cleanup, child-frame ordering, native displayed values,
historical binding-name maps, scalar range fences and workbench recovery have
bounded repairs already. Their remaining target contracts and unsupported
compositions are different work. The
[research gap expansion](../research/README.md#research-gap-continuation) documents
unperformed comparisons; documentation completeness is not implementation.

Task basis labels:

| Label | Meaning | Required next evidence |
| --- | --- | --- |
| Gap | A current limitation is recorded in a maintained receipt/fixture | Reproduce at the selected revision and surface before repair |
| Target | Canonical target direction exists but the supported prototype is narrower/different | Accepted/rejected fixtures and an explicit migration profile |
| Fork | Two or more credible contracts remain; no implementation choice is accepted here | A bounded comparison with a falsifier and a recorded decision |
| Investigate | A risk or missing evidence needs inspection; not a demonstrated defect | Confirm, narrow or dismiss with a minimal observation |
| Extend | Optional usefulness after dependencies close | A representative program that existing calls/tooling cannot serve adequately |
| Host Gate | Local evidence cannot settle a remote, platform or human-context claim | Actual declared-host/revision/participant evidence with scope and consent |

## Task Definition Rules

- [ ] For every selected task, name one user pressure, semantic owner, current
  profile, affected artifact and smallest reviewable output.
- [ ] Record prerequisites as A/D/packet links, not a vague requirement to finish
  the entire language. Distinguish paper/model work from executable promotion.
- [ ] Write positive, negative and unsupported cases before an implementation
  decision. Include beginner, ordinary production and failure-heavy programs.
- [ ] State what must remain unchanged: effects, order, call count, cleanup,
  source identity, retained causes, authority and supported samples as applicable.
- [ ] Require a local diagnostic/inspection result as well as successful stdout.
  A refusal or honest unknown may be the correct outcome.
- [ ] Give every experimental abstraction a fallback, removal criterion and
  named extraction point. Do not create universal metadata machinery for one case.
- [ ] Separate bug repair, target acceptance, test organization, snapshot changes,
  generated assets and backend replacement into independently reviewable work.
- [ ] Preserve existing tests and case identities; seek the required approval
  before editing existing tests. New focused tests must not relax an oracle to
  match a convenient implementation.
- [ ] Mark completion with an exact revision, commands, host/profile, observed
  outcomes, skipped coverage and remaining boundary. An unchecked task is not
  automatically a release blocker; the roadmap determines that scope.

## Actions At Every Scale

| Scale | To do | Completion test |
| --- | --- | --- |
| Product | Choose one bounded first-audience promise and explicit exclusions | A newcomer can run, understand and repair the promised workflow without fictional APIs |
| Language | Close a small interacting semantic slice, not isolated spellings | Binding/call/type/failure/effect/lifetime meanings agree in one program |
| Architecture | Make source, typed artifacts, execution and host policy separately owned | One engine can be exchanged without commands acquiring hidden semantic rules |
| Package | Define public interface, nominal ownership, build inputs and evolution | Downstream checking does not execute imports or inspect private implementation to guess contracts |
| Module | Reduce mutable shared state and make boundaries inspectable | Imports, state, callbacks and diagnostics have one discoverable owner |
| Function | Specify call mapping, defaults, retained captures, outcomes and effects | Both successful and conflicting uses have local explanations |
| Operation | Preserve once-only evaluation, atomic binding and completion | A failed step cannot publish a partial binding or repeat a prior effect |
| Domain | Reuse foundations while retaining domain-specific laws and evidence | One adapter cannot silently reinterpret another model's edges, identity or guarantee |
| Human workflow | Separate intent, explanation, review, authority and execution | A stale, ambiguous, denied or incomplete action has a safe repair/refusal path |
| Delivery | Tie claims to artifacts and actual supported environments | The installed CLI and hosted browser identify the checked revision and profile |
| Maintenance | Keep tasks, evidence, decision routes and retrieval current | A new contributor can find the next exact step without rediscovering old repairs |

## Shared Dependency And Promotion Rules

- [ ] Use D1/A08 to close calls, generics, protocols and callback effects before
  claiming rich data/resource/ML APIs are typeable.
- [ ] Use D2/A11/A14/A15 to close completion, all-cause cleanup, escape, task
  ownership and cancellation before promoting resource-heavy programs.
- [ ] Use D3/A03/A12/A26 to close scalar, Text/Bytes, codec and contextual identity
  laws before stable interchange or cross-host claims.
- [ ] Reconcile these contracts in D4's composed import/report/job program; list
  every unresolved library contract explicitly rather than hide it behind a name.
- [ ] Use D5 to compare representations and human repair separately from formal
  validity. Do not let an attractive view select an unsettled execution model.
- [ ] Use D6 for the smallest capability-gated frontend/artifact/runtime migration,
  then D7 for one supported CLI/browser sample. Research targets stay outside
  `samples/` until their declared support is independently demonstrated.
- [ ] Allow independent maintenance, source-map, harness and hypothesis work
  where its own prerequisites are ready; D1-D7 are not a blanket ban on useful
  local work or a reason to promise the whole corpus in the next release.
- [ ] Interpret dependencies as named contract slices, not completion of entire
  A items. Shared inputs may be co-designed: atomic binding precedes data
  construction; the threat model precedes grant/transport enforcement; their
  later composition evidence does not block initial analysis in a cycle.

## Global And Local Work

The sections below retain existing A IDs. Their checklists are decomposition
notes, not new work IDs, assigned dates or automatic implementation approval.

### A01 Product Scope And Milestones

**Basis:** Target / Fork. **Depends on:** D4 and the selected A02 profile.
**Owners:** target README, synthesis, target suite and roadmap milestone table.

- [ ] Define the smallest useful preview promise for scripts, data boundaries
  and failure-heavy jobs; name audiences and excluded capabilities explicitly.
- [ ] Annotate one beginner invoice, one import/report and one cleanup/cancellation
  job with every real API, unresolved contract and intended host profile.
- [ ] Decide what belongs in an experimental preview versus a target-language
  demonstration; do not turn research breadth into a release feature list.
- [ ] Specify first-use, prediction and repair outcomes: obtain a result, locate
  the relevant source, understand failure/authority and make a safe next change.
- [ ] Prepare a milestone claim sheet tying each promise to fixtures, examples,
  actual hosts and a known-limit statement; keep public claims narrower than code.

**Done:** a milestone can be demonstrated and explained end to end with no
unresolved API presented as supported. **Stop:** shrink the promise when its
language or host prerequisites remain unsettled; do not rewrite the whole project
to meet an invented date.

### A02 Feature And Profile Honesty

**Basis:** Target / Investigate. **Depends on:** existing registry/evidence owners.
**Local surface:** `prototype/syntax/features.py`, frontend/backend specs,
`prototype/runtime/pipeline.py`, runtime inspection and UI capability consumers.

- [ ] Refresh the current target-disposition census; resolve each still-unreviewed
  entry at its canonical owner without assuming an old count is current.
- [ ] Distinguish syntax acceptance, typed meaning, lowering, execution, diagnostics,
  browser/notebook exposure and verified evidence in existing metadata.
- [ ] Audit parser/backend/profile combinations for pre-effect rejection; a
  frontend accepting a form must not make an unsupported evaluator look capable.
- [ ] Attach actual fixture/revision references to evidence claims, preserving
  supported-but-unverified, deliberately unsupported and retired states.
- [ ] Sketch one bounded target profile with migration diagnostics for prototype
  truthiness, rebinding and retired conveniences; leave current defaults honest.
- [ ] Make CLI inspection, playground selection and contributor docs derive the
  same support interpretation rather than maintain a second feature inventory.

**Done:** every advertised combination has an explicit contract and evidence
state; unsupported work cannot execute effects. **Stop:** no profile promotion
from metadata edits alone and no universal registry rewrite without demonstrated
duplicated ownership.

### A03 Scalars, Text, Bytes And Portable Values

**Basis:** Fork / Target. **Depends on:** D3; callback rendering also needs A08.
**Owners:** syntax/semantics, scalar descriptors, Core JSON and Python/JS adapters;
research routes T1-T10 and open question 9.

- [ ] Write one expression/pattern/decoder/interchange golden-vector set: integer
  limits, checked narrowing, division/remainder, Decimal context, rounding,
  NaN/infinity, negative zero, equality and map-key eligibility.
- [ ] Compare the existing JS exact-range fence with a tagged exact-integer
  representation as separate profile choices; preserve Python's supported wider
  range until a target migration is explicitly chosen.
- [ ] Specify Text/Bytes constructors, strict decode failures, replacement policy,
  BOM handling, surrogate/non-scalar boundaries and encoding profiles.
- [ ] Define code-point indexing separately from grapheme selection and display
  width; map UTF-8 source offsets, Python positions and Monaco UTF-16 coordinates.
- [ ] Close interpolation order, once-only calls, literal braces, raw/multiline
  semantics and display/inspect/render/encode distinctions with side-effect cases.
- [ ] Add proposed limits for literal size, numeric digits and serialization
  depth; report rejection before uncontrolled allocation where feasible.
- [ ] Challenge normalization/confusables, bidirectional controls, embedded NUL,
  locale sorting and escaping without changing semantic identity implicitly.

**Done:** vectors agree or explicitly reject on each declared profile, and text
never acquires execution authority from a consumer's second interpretation.
**Stop:** no universal Unicode index unit, wire codec or numeric algebra inferred
from whichever host happened to run the example.

### A04 Grammar, Source Preservation And Parser Frontends

**Basis:** Target / Investigate. **Depends on:** A02/A03 and the pattern packet.
**Local surface:** grammar, `prototype/parser/nomi/frontend.py`, Rust/WASM payloads,
Python/JS adapters, source-span and parse-acceptance fixtures.

- [ ] Produce target-positive/negative parse facts independent of current grammar;
  keep prototype acceptance and target admission in separate fixture lanes.
- [ ] Specify versioned lossless tokens/CST, comments/trivia and source identity
  for one family; retain original source when a lossless parser is not available.
- [ ] Compare incomplete-edit recovery with hard execution rejection; mark every
  recovery node non-executable rather than evaluate a guessed repair.
- [ ] Replace one Raw family with structured fields, starting from a concrete
  call/argument/slice pressure, with unknown-version and malformed-payload cases.
- [ ] Check continuation indentation, CRLF, nested delimiters, interpolation,
  Unicode positions and off-by-one boundaries in both source adapters.
- [ ] Keep Rust/Tree-sitter/other candidates opt-in until parse shape, payload,
  diagnostics, lowering and useful-host evidence agree for the named profile.

**Done:** the selected family has structured parity and exact declared mapping;
no adapter depends on formatter text as an API. **Stop:** retain an explicit
fallback/rejection when replacing Raw loses information or duplicates policy.

### A05 Resolution, Types And Typed Surface

**Basis:** Target / Fork. **Depends on:** A03/A08 and versioned artifact boundaries.
**Owners:** canonical semantics, Surface/schema definitions and module interfaces.

- [ ] Specify stable lexical symbols, scope/visibility, shadowing, module constants
  and cross-edit identity independently of host dictionary lookup.
- [ ] Define one typed slice for literals, bindings, functions, calls, Bool choice
  and failures before designing a whole-language checker architecture.
- [ ] Compare local inference/public annotations using recursive, ambiguous and
  separately compiled examples; reject implicit Any as an inference repair.
- [ ] Separate type, effect, constraint, region and exhaustiveness judgments, each
  with an origin and an explicit inferred/supplied/assumed status.
- [ ] Include polymorphic shared storage, an outer-slot wrapper, fresh factories,
  opaque variance and imported protocol ownership in D1/D3 judgments.
- [ ] Sketch passive interface artifacts that can be checked and cached without
  executing imports; specify invalidation and unknown schema/edition handling.
- [ ] Plan source-local diagnostics showing the conflicting use and its binding,
  capture or declaration origin rather than a backend-internal type dump.

**Done:** independent positive/negative facts validate resolved typed artifacts
for one slice. **Stop:** do not add compiler stages whose required facts exist
only as manually invented metadata or require whole-program private inspection.

### A06 Core, Lowering And Inspectable Reduction

**Basis:** Gap / Target. **Depends on:** A04/A05, the selected completion contract.
**Local surface:** `prototype/syntax/core.py`, `core_json.py`, verification,
Surface/Python/JS lowering and `prototype/parser/nomi/desugar/`.

- [ ] Design a versioned source-map/span carrier for serialized Core, including
  source revision, generated origins, related locations and malformed maps.
- [ ] Specify structural artifact comparisons alongside stdout: control target,
  evaluation order, function/default boundaries, constraints and failure channels.
- [ ] Lower one target-owned Surface operation directly while retaining Python
  AST as an adapter, not an implicit source specification.
- [ ] Validate unknown versions, illegal node placements, missing fields, cycles,
  nonfinite scalar transport and excessive depth at the artifact boundary.
- [ ] Review reductions for fresh-name hygiene, once-only evaluation, nearest
  lexical return and cleanup; retire reduced evaluator hooks only when the
  corresponding normal form is independently verified.
- [ ] Distinguish checked Core operations from host compatibility intrinsics;
  an unsupported profile must reject an intrinsic before external effects.

**Done:** two frontend paths produce equivalent verified artifacts and diagnostics
for the slice. **Stop:** avoid a whole-IR replacement until one closed contract
shows why its current representation cannot preserve the required behavior.

### A07 Binding, Mutation And Constraints

**Basis:** Target / Investigate. **Depends on:** A05's selected binding/type slice
and accepted binding law. **Co-design inputs:** A09 construction, A19 diagnostics.
**Local surface:** environment/binding layers, constraint descriptors and checking.

- [ ] Model immutable names, explicit mutable cells, fresh lexical scopes and
  captured-cell ownership without silently breaking prototype reassignment.
- [ ] Share the evaluate/tentatively-bind/check/commit protocol across declarations,
  parameters, destructuring and data construction; test failure at each phase.
- [ ] Specify `set` as a checked transition preserving declared constraints; a
  rejected update must not partially overwrite a cell or related fields.
- [ ] Challenge sibling field references, declaration-wide constraints, aliasing,
  closures, pattern arms and default evaluation with source-linked diagnostics.
- [ ] Separate internal contract violations from external accumulated decode
  errors, and determine when a constraint can be statically discharged.
- [ ] Specify deterministic/effect-free predicate requirements and honest handling
  of opaque host callbacks; a Boolean-looking function is not a purity proof.

**Done:** atomic publication and failure traces agree across selected profiles;
the migration makes create-versus-change visible. **Stop:** no quiet target
change justified only by Python parity or a convenient host assignment operation.

### A08 Calls, Generics, Protocols And Functional Abstractions

**Basis:** Fork / Target. **Depends on:** D1, with D2/D3 for retained/portable values.
**Owners:** [function packet](../design/function_contracts.md), callback target,
functions/effects evidence and GA1-GA8.

- [ ] Encode and verify accepted left-to-right once-only argument evaluation and
  declaration-order call-time defaults. Close remaining call-shape, label,
  function-type, generic spelling and inference choices while retaining explicit
  public generic contracts.
- [ ] Type map/fold, derived decode and resource/task callbacks together under
  pure-only and effect-polymorphic challengers; make latent/retained effects visible.
- [ ] Define protocol owner, receiver/implementation identity, conformance,
  extension ambiguity and separate-checking metadata before convenient dispatch.
- [ ] Compare conservative, relaxed and effect/region-aware generalization using
  delayed identity and shared outer storage; exclude variables fixed by the
  monomorphic environment under every candidate.
- [ ] Specify invocation count, order, demand, failure prefix and closure lifetime
  for strict map/filter, seeded scan, fallible tap and whole-value pipe.
- [ ] Keep Eq/Hash/codec capability conditional; compare context-bound cache and
  wrapper order without creating universal Object/Function methods.
- [ ] Distinguish repeat, bounded iteration and fixed-point convergence; require
  named laws/profiles before associativity, fusion or parallel reduce rewrites.
- [ ] Prepare 80/100-column signatures, hover output and conflicting-callback
  diagnostics; count recognition and repair costs, not accepted snippet count.

**Done:** D1's three programs have coherent inferred/declared contracts and
independent negative judgments. **Stop:** no functional-paradigm mandate,
automatic currying, purity from naming or source notation selected by popularity.

### A09 Nominal Data And Generated Behavior

**Basis:** Target / Fork. **Depends on:** A05/A07/A08 and A12 for boundaries.
**Owners:** data semantics, type/field descriptors and generated protocol metadata.

- [ ] Specify nominal declaration identity, field order/defaults, variant tags,
  immutable construction and atomic declaration-constraint checking.
- [ ] Derive equality, conditional hashing, redaction-aware display, patterns and
  codecs as inspectable protocol behavior rather than hidden host reflection.
- [ ] Distinguish language hash law, process hash and persistent content identity;
  mutable or identity-sensitive values need explicit eligibility boundaries.
- [ ] Challenge recursive/cyclic host inputs, nested sensitive values, absent
  versus null fields and constructors that receive unchecked structural objects.
- [ ] Expose the generated long form and allow explicit owned overrides only
  under a resolved protocol contract; retain source/field provenance.
- [ ] Review package-version crossings and branded/runtime owner checks without
  assuming equal fields or labels unify nominal declarations.

**Done:** construction/derived behavior has independently checked laws and no
partial owned value escapes failure. **Stop:** generated metadata alone does not
prove immutability, codec round trips or compatibility across package versions.

### A10 Patterns, Choice And Exhaustiveness

**Basis:** Target; registered packet is implementing, not fully validated.
**Depends on:** A03/A04 for fragment work; A05/A09 for typed coverage.
**Owners:** [pattern contract](../design/pattern_matching.md), Pattern Surface v1,
Lark/Rust frontends and matching fixtures.

- [ ] Strengthen shared vocabulary/scalar/span invariants in the existing fragment
  boundary before promoting full match execution.
- [ ] Define lossless statement/expression match containers, arm scope and source
  maps; accepted direct-arm syntax must not drift into retired host spellings.
- [ ] Preserve structural test, tentative capture, optional pure Bool guard and
  all-or-none arm commit with left-biased alternatives and one subject evaluation.
- [ ] Implement typed closed-variant exhaustiveness and redundancy/missing witnesses
  separately from guards and open structural data; reject unsupported proof claims.
- [ ] Cover exact maps, explicit rest, absent versus present none, nested data,
  overlapping alternatives, incompatible captures and invalid constraints.
- [ ] Plan local diagnostics and formatter output, then gate CLI/browser/sample
  promotion on artifact and behavior parity, not parse acceptance alone.

**Done:** the admitted slice has transactional captures, correct coverage
judgments and equivalent host behavior. **Stop:** do not reopen rejected choice
aliases/user extractors or claim complete matching from the fragment schema.

### A11 Failure, Control Transfer And Resumable Completion

**Basis:** Gap / Fork / Target. **Depends on:** A05/A06/A08 and D2.
**Local surface:** Python generator/expression/call/exception/context-manager
layers, portable value/control records and the runtime continuation plan.

- [ ] First isolate an effectful compound-expression operand and a paused child
  failing under nested `try`/`with`; retain operand, phase, active child and pending
  completion facts before choosing a coherent engine or explicit rejection.
- [ ] Inventory yield-capable node states and child-to-parent completion delivery;
  cover resumed None, nested re-yield, exhaustion and the waiting ancestor scope.
- [ ] Specify supported send/throw/close semantics, including cleanup when a
  generator closes while suspended; do not treat a close placeholder as success.
- [ ] Keep hosted exception/suppression/context-chain compatibility separate from
  target Option/Result/Unit, panic, cancellation and typed all-cause completion.
- [ ] Define completion destination and cause order through calls, propagation,
  loops, resource scopes and task groups; preserve nearest-function return.
- [ ] Challenge failed operands before a callee, short-circuit operations, failed
  finalizers and multiple cleanup causes using independent traces, not only output.
- [ ] Decide observable structured outcomes and source locations for unsupported
  suspension, host abort and incomplete cleanup without collapsing them into Err.

**Done:** supported compatibility traces preserve once-only operands and cleanup;
the separately admitted target slice preserves all completion categories/causes.
**Stop:** stop operator-specific patches when phase state is duplicated; unsupported
shapes need a pre-effect fence, not an apparent successful partial execution.

### A12 Decode, Encode, Schemas And Boundary Evolution

**Basis:** Target / Fork. **Depends on:** A03/A08/A09/A11 and D3.
**Local surface:** `prototype/runtime/decode.py`, data descriptors, codec protocols,
schema/export targets and boundary diagnostics.

- [ ] Specify strict structural-to-owned decode, closed fields, aliases, defaults,
  versions and opt-in adapters; constructors must not become implicit parsers.
- [ ] Accumulate independent indexed errors while withholding declaration predicates
  whose required fields did not decode; publish no partial owned object.
- [ ] Define variant wire tags, missing versus null, duplicate map keys, unknown
  fields, malformed UTF-8, nonfinite numbers and bounded input/depth policy.
- [ ] Expose representable, approximated and omitted constraints in schema exports;
  a successful projection must not imply it expresses arbitrary predicates.
- [ ] Compare source/structural/wire compatibility and explicit migration with
  provenance; include rolling clients, event replay and expired schema editions.
- [ ] Define redaction and round-trip claims for supported codecs; serialization
  must not reconstruct native pointers, live leases or execution authority.
- [ ] Investigate delayed/function/stream validation only when a real boundary
  needs it; eager decode must not claim to validate future invocations/values.

**Done:** a malformed batch reports independent paths and performs no downstream
publication, while supported round trips name their exact profile. **Stop:** no
universal serializer, silent coercion or generic schema-completeness claim.

### A13 Effects, Grants And Host Providers

**Basis:** Target / Fork. **Depends on:** A08's callback contract and A30's initial
threat model, not completed security enforcement. **Co-design inputs:** A30 grant
and disclosure policy.
**Owners:** industrial effects contract, host descriptors, provider interfaces,
runtime profiles and typed effect/region evidence.

- [ ] Settle the initial effect taxonomy and transitive callback effects; show
  declaration, available category and current concrete grant as different facts.
- [ ] Sketch unforgeable provider/handle authority, narrowing, task delegation,
  revocation and cold-task authorization timing before new effectful adapters.
- [ ] Verify host descriptors by version, arity, callback behavior, result/error
  conversion and actual denied-operation tests; metadata alone is not enforcement.
- [ ] Provide injectable deterministic clock/random/file/network substitutes
  through providers rather than patch process globals in replay tests.
- [ ] Define preflight and use-time checks for browser/restricted profiles, while
  acknowledging races and unknown external outcomes at the owning boundary.
- [ ] Keep foreign-thread callbacks from inheriting ambient task-local grants;
  attach/bridge them under an explicit callback authority policy.

**Done:** a `uses` declaration never grants authority, denied work has a defined
effect boundary and inspection names the exact granted operation. **Stop:** no
sandbox or purity claim from a builtin allowlist, signature or permission label.

### A14 Resources, Defer, Regions And Foreign Callbacks

**Basis:** Fork / Target; hosted synchronous repairs are not the target contract.
**Depends on:** A08/A11/A13 and the resource-lifetime packet.

- [ ] Type Reader/resource callbacks, heterogeneous nested errors and whole-
  completion escape through success, Err, causes, closures, tasks and diagnostics.
- [ ] Complete the target trace matrix for enter failure, binding failure after
  enter, body failure, return/break/continue and simultaneous release failure.
- [ ] Specify lexical defer registration and capture timing, LIFO order, exactly-
  once release and the observation point after required cleanup.
- [ ] Compare static non-escape plus revocation with runtime-only closed-handle
  enforcement, retaining copied data as distinct from aliased resource state.
- [ ] Use event-controlled enter/body/exit cancellation, in-flight operations,
  repeated requests, cleanup deadlines and join; timeout may mean incomplete.
- [ ] Compare restricted immediate callbacks, owned-event bridging and explicit
  re-entry; distinguish admission closure, deregistration and final quiescence.
- [ ] Pin one safe foreign adapter/ABI before probing callbacks during registration,
  self-close, foreign threads, borrowed buffers or supported abnormal containment.

**Done:** the accepted slice preserves every required cause, releases exactly
once and proves/observes the declared non-escape/quiescence boundary. **Stop:** no
native undefined-behavior experiment, implicit panic-to-Err conversion or portable
unwind guarantee inferred from a single host; no target cleanup claim from worker kill.

### A15 Tasks, Scheduling, Memory Publication And Backpressure

**Basis:** Fork / Target. **Depends on:** A11/A13/A14 and D2.
**Owners:** concurrency/task contracts, scheduler fixtures and memory research.

- [ ] Specify cold construction, start/await authority, retained captures and
  scoped task handles; no task should silently survive its admitted owner.
- [ ] Compare cancel-siblings and collect-all abnormal policy separately from
  ordinary returned Err; define observation/cause order independently of timestamps.
- [ ] Test parent/child cancellation, deadlines, simultaneous failures and cleanup
  joining with explicit controlled events rather than sleep-based assertions.
- [ ] Bound active work, queued items, queued bytes and evidence independently;
  choose demand/backpressure/drop policy before an unbounded stream adapter.
- [ ] State admissible sharing, ownership transfer, immutable publication, lock/
  channel/join happens-before edges and a race policy for declared host profiles.
- [ ] Separate visibility from atomic compound invariants and task lifetime;
  a sequential scheduler model is not weak-memory evidence.
- [ ] Model shutdown and restart without reporting a cancellation request, empty
  queue or dead worker as proof that all external work/resources completed.

**Done:** bounded tasks have explicit lifetime, order and publication guarantees,
with supported host evidence and honest incomplete outcomes. **Stop:** no implicit
detached task, fairness guarantee or portable atomic memory law from host timing.

### A16 Collections, Streams, Tables And Numeric Plans

**Basis:** Extend / Fork. **Depends on:** A03/A08/A12/A15; DW/DT/ML owners.
**Local surface:** collection library, plan/domain values, callbacks and adapters.

- [ ] Close strict traversal order, call count, failure prefix, seeded histories,
  single-pass demand, replayability and iterator/resource cleanup.
- [ ] Distinguish map of Result values, fail-fast traversal and accumulated errors;
  keep tap/observer effects and aliasing visible instead of treating them as identity.
- [ ] Test cache contexts, mutation, receiver state, authority and wrapper order;
  encoded equality and hash values are not automatically safe memoization keys.
- [ ] Compare eager rows, schema-bound expression data and scoped query notation
  using DW1-DW3: duplicate keys, missing values, joins, windows and cardinality.
- [ ] Keep schema, snapshot, partition, ordering and temporal basis distinct;
  predicate consistency and lawful incrementality need their own owners/profiles.
- [ ] Compare named axes/units/frames and explicit contractions under DW4/DW5;
  pure callbacks are not automatically translatable numeric/query programs.
- [ ] Use established engines behind a declared adapter only after its bounded
  laws, errors, source maps, budget and host data movement are specified.

**Done:** one useful library/plan slice has independent value, order, error and
resource oracles. **Stop:** no table/array/workflow keyword, universal graph algebra
or parallel reduction without a demonstrated ordinary-call deficiency and laws.

### A17 Prelude And Standard Library

**Basis:** Target / Extend. **Depends on:** A08/A09/A11/A12/A13.
**Owners:** industrial stdlib target and explicit library/API contracts.

- [ ] Inventory host conveniences used by runnable samples and classify each as
  prelude, explicit module, profile adapter or temporary compatibility escape.
- [ ] Specify a small typed text/bytes/collection/console/JSON foundation with
  consistent names, data-first transforms and named policy arguments.
- [ ] Give partial operations Option/Result and visible limits/effects; clarify
  display, inspection, parsing, encoding, formatting and execution verbs.
- [ ] Prepare files/HTTP/process/database protocols with deadlines, ownership,
  failure conversion, output limits and declared publication guarantees.
- [ ] Review Eq/Hash/display/codec capabilities and generic operation laws by
  carrier, not a universal object hierarchy or one programming-paradigm doctrine.
- [ ] Incubate domain libraries with versioned examples and removal criteria
  before committing them to the permanent prelude or global grammar.

**Done:** a selected useful program needs no untyped host escape, and every
public call has checked input/result/failure/effect meaning. **Stop:** remove
unused convenience APIs that create a second recognition path without real leverage.

### A18 Sessions, Caches, Transport And Process Lifecycle

**Basis:** Gap / Investigate / Fork. **Depends on:** A02 profile evidence, A19's
selected result envelope and A30's initial transport threat model.
**Co-design inputs:** A30 enforcement/retention checks, not all security work.
**Local surface:** `prototype/runtime/api.py`, `session.py`, `pipeline.py`, backend
adapters, `backends/json_process.py` and worker request envelopes.

- [ ] Specify failed-cell state, reset/close, backend switching and definition
  ownership; test which earlier effects/bindings survive a later failure.
- [ ] Retain once-only displayed values and historical names from the existing
  repair; decide explicitly which result values are references versus owned data.
- [ ] Define cache keys from source, grammar/options, artifact/schema, profile,
  interface and relevant context; test eviction, AST mutation and stale provenance.
- [ ] Define request/response schema, duplicate-key policy, byte/depth/output/event
  limits, timeout and process-tree termination before more subprocess integrations.
- [ ] Compare buffering and bounded streaming only for a measured need; label
  transport failures separately from program errors and genuine empty output.
- [ ] Extract shared transport below parser/backend registration if import cycles
  justify it; keep native parse error and runtime result categories distinct.
- [ ] Admit persistent workers only with explicit startup/handshake/reset/cancel/
  close contracts, retained-value eligibility and demonstrable startup benefit.

**Done:** session/transport failure is structured, bounded and recoverable, and
caches cannot cross incompatible contexts. **Stop:** no deep-copying live handles,
serialization of authority or sandbox claim from process separation/timeout alone.

### A19 Results, Diagnostics, Events And Explanation

**Basis:** Target / Extend. **Depends on:** A03/A04/A06, D2 for composed causes.
**Local surface:** runtime result/diagnostic/collector owners, worker envelopes
and CLI/kernel/editor/browser renderers.

- [ ] Map current producer/consumer fields into one versioned result envelope:
  status, payload eligibility, stdout, diagnostics, causes, source revision,
  offset units, captured/unavailable bindings and measured/unavailable timings.
- [ ] Carry related spans, constraints, call/dispatch origins and repair proposals
  without guessing line one or applying an old span to a new source revision.
- [ ] Add one real semantic producer at a time for matching, propagation, denied
  capability, cleanup or tasks; passive fields are not observed event coverage.
- [ ] Bound event count/payload/depth and preserve total/shown/omitted facts;
  implement sensitive-value policy at each sink instead of stripping labels later.
- [ ] Compare raw trace with question-bound why/why-not diagnosis, false premises
  and multiple blockers under C09/HX2/HX8; repair needs separate sufficiency,
  domain-acceptability and current-authority evidence.
- [ ] Make terminal, JSON, notebook, browser and editor render the same semantic
  facts while allowing presentation differences and honest redacted unknowns.

**Done:** one end-to-end failure is locally explainable across declared consumers
without invented facts, rerunning effects or dropped causes. **Stop:** no universal
causal engine, automatic safe repair or trace-completeness claim from fluent prose.

### A20 CLI, REPL, Check And Formatter

**Basis:** Target / Extend. **Depends on:** A04/A05/A18/A19.
**Local surface:** `scripts/cli.py`, public runtime/session API and distribution.

- [ ] Specify exit/status codes, program stdout, diagnostic stderr, JSON output
  and compatibility before adding command variants; retain current output modes.
- [ ] Cover unreadable/non-UTF-8 paths, spaces, invalid profiles, partial failure,
  SIGINT, closed pipes and failed value rendering from an installed artifact.
- [ ] Define REPL incomplete-input, persistent state, failed definitions, history,
  reset and interrupt semantics using the session owner rather than a second engine.
- [ ] Define parse/check/type/effect capabilities separately; a syntax-only command
  must not claim to check types, lifetimes or authority.
- [ ] Specify discovery and invocation of target `example` declarations for one
  admitted slice, with module/session isolation, grants/effects, cleanup and
  structured `check` failures; do not advertise a test/doc command before support.
- [ ] Specify a formatter's admitted source subset, trivia retention, canonical
  widths, idempotence and semantic preservation; do not format guessed recovery.
- [ ] Connect inspection, explanation and machine-applicable repairs to versioned
  artifacts, retaining the original source when unsupported formatting is requested.

**Done:** installed outside-checkout transcripts separate output, tooling and
failure; checking/formatting state their real scope. **Stop:** no blanket CLI
redesign, implicit failed-state repair or compatibility promise from a debug transcript.

### A21 Playground, Documents And Interaction

**Basis:** Investigate / Extend / Host Gate. **Depends on:** A02/A03/A18/A19.
**Local surface:** `web/app.js`, `documents.js`, `demos.js`, `cells.js`, `editor.js`,
`runtime.js`, worker adapters, `index.html`, `style.css` and browser scenarios.

- [ ] Specify state transitions among shipped sample, restored draft, imported
  file and scratch document; include changed shipped identity and storage editions.
- [ ] Challenge duplicate tabs, draft ID collisions, failed save, unload during
  import, mixed line endings and late completions after replacing a document.
- [ ] Retain source-preserving import/export and stale-result labels; no load,
  sample navigation or view inspection may implicitly execute source.
- [ ] Derive profile/backend/unsupported evidence from existing runtime records;
  keep result, source, model, worker and generation identities aligned.
- [ ] Inventory every fetched editor/icon/runtime asset and choose online-only
  versus packaged/offline behavior with a truthful recovery/fallback policy.
- [ ] Compare loading, partial-ready, failed, retrying, running, stopping and reset
  states, including delayed responses from an abandoned bootstrap attempt.
- [ ] Prepare manual keyboard/screen-reader/IME/zoom/reduced-motion Run/Stop/repair
  tasks; disabled actions need accessible reasons and focus must survive failures.
- [ ] Incubate read-only table/dependency/type/effect views before editable inverse
  projections; pair every view with equivalent textual facts and source context.

**Done:** selected actual browser workflows preserve source/identity, recover
without duplicate ownership and expose honest outcomes on declared viewports.
**Stop:** no accessibility/comprehension certification from screenshots/DOM checks,
no inferred inverse edits or CDN upgrades hidden inside a visual polish task.

### A22 Jupyter And Notebook Delivery

**Basis:** Investigate / Host Gate / Extend. **Depends on:** A18/A19; D2 for cleanup.
**Local surface:** `tools/jupyter/nomi_kernel.py`, installation/check/launch tools,
notebook sources and kernel messaging.

- [ ] Specify failed-cell state, user expressions, display/stream/error ownership,
  silent requests, `%run` file identity, reset and interrupt in one kernel contract.
- [ ] Compare real protocol transcripts with helper-only tests, preserving the
  current persistent definitions and single-expression display behavior.
- [ ] Validate kernelspec interpreter/path resolution outside the checkout,
  moved installations, optional dependencies and executable version mismatch.
- [ ] Preserve source/diagnostic identity for `%run` and notebook cells; show stale
  results after edits without pretending historical bindings are frozen values.
- [ ] Test startup, execution, error repair, long-cell interruption and shutdown
  under the declared environments, distinguishing acknowledgment from cleanup.
- [ ] Define portable notebook source/export metadata and privacy expectations;
  generated notebooks must not silently become a second sample authority.

**Done:** actual kernel conversations cover persistence, silence, failure and
reset for the supported artifact. **Stop:** no claim that a unit helper verifies
kernelspec startup or that host interruption implements target cancellation.

### A23 VS Code, Resolution And Language-Server Growth

**Basis:** Investigate / Target / Host Gate. **Depends on:** A04/A05/A19/A28.
**Local surface:** `tools/vscode/nomi/`, runner/task/extension code, syntax/snippets,
test launcher, package metadata and shared parser/resolution artifacts.

- [ ] Reproduce the documented editor-host executable-name mismatch through the
  tracked launcher, then compare a bounded launcher repair with a pinned host.
- [ ] Add real-host file/selection lifecycle scenarios for multi-root settings,
  paths with spaces, failed save, cancellation, reload and temporary-file cleanup.
- [ ] Keep workspace trust, no-workspace refusal, argv/cwd resolution and installed
  CLI execution explicit; skipped GUI dependencies are not test passes.
- [ ] Label current regex navigation scope and compare one symbol family against
  shared source/resolution artifacts before choosing a complete LSP architecture.
- [ ] Challenge shadowed names, strings/comments resembling declarations, unsaved
  incomplete code, import aliases and stale rename/source revisions.
- [ ] Align Monaco/TextMate/snippet vocabulary with declared profiles; separate
  highlighting from semantic resolution and machine-applicable refactoring.
- [ ] Verify declared OS/editor combinations before cross-platform claims; record
  actual host version, workspace setup and process/task teardown evidence.

**Done:** one symbol/runner slice has correct identity and real-host lifecycle
evidence. **Stop:** no shell-string execution, text-equality rename, automatic
editor installation or full-LSP claim from parser-backed navigation alone.

### A24 Tests, Oracles, Differential Evidence And Fuzzing

**Basis:** Investigate / Target. **Depends on:** semantic owners and A02 evidence.
**Owners:** test layout/skills, [deferred test review](../review/2026-09-30-test-issues.md),
fixture ladders, parser/artifact/runtime/browser and installed-distribution checks.

- [ ] Audit case collection and selector behavior under declared pytest versions;
  invalid/empty mode selections must not silently count as useful coverage.
- [ ] Reconcile skips by feature/profile/backend/host, keeping deliberate exclusions
  and the suspended-child known gap distinct from missing dependencies.
- [ ] Create behavioral coverage per admitted Core/Surface operation, beyond
  textual handler-presence checks or aggregate pass counts.
- [ ] Use independent expected values, structures, call traces and cause order;
  do not let two adapters sharing the same bug serve as each other's sole oracle.
- [ ] Add bounded property/metamorphic/fuzz cases for literals, spans, bindings,
  codec paths, malformed artifacts and completion; minimize failures to fixtures.
- [ ] Control random seeds, event schedules, locale, encodings and environment;
  compare declared order/laws rather than nondeterministic wall-clock timing.
- [ ] Separate research-capture integrity from runtime conformance and supplied
  study answers from observed comprehension; preserve explicit execution flags.
- [ ] Prepare independent example/check fixtures for the A20 runner: discovery,
  order, isolated state, failed checks with source/compared values, denied effects
  and cleanup. Keep this language contract separate from pytest organization.
- [ ] Plan reviewed test-maintenance changes independently of runtime fixes,
  preserving collected identities, snapshots, assertions and intentional skips.

**Done:** the selected feature's positive/negative/unsupported paths have independent
oracles on required surfaces; failures are reproducible and attributable.
**Stop:** no skip removal, snapshot regeneration or weakened assertions simply
to improve a green count; coverage inventory is not a proof of all semantics.

### A25 Performance, Allocation And Resource Budgets

**Basis:** Investigate / Extend. **Depends on:** A24 and declared semantic profiles.
**Local surface:** `tools/perf/`, [performance owner](performance_notes.md), parser/
session/worker/transport pipelines and inspection overhead.

- [ ] Refresh measurements instead of repeating historical parser speedups as
  current whole-product performance; record toolchain, source, hardware and options.
- [ ] Separate cold startup, parser construction, parse, transform, lowering,
  verification, evaluation, cache hit, serialization and rendering.
- [ ] Compare spans off/on, tracing off/on and cold/warm CLI/browser/optional-host
  behavior using distributions and memory, not only a single median demo.
- [ ] Propose loose opt-in budgets for input depth/bytes, output/events, queue
  memory, worker startup and long-lived sessions; identify the enforcing owner.
- [ ] Measure allocation/retention under cache churn, editor/model disposal,
  streaming demand and repeated failure/reset, using non-sensitive fixtures.
- [ ] Consider Rust/native/caching/fusion/persistent workers only after the
  measured bottleneck and semantic/source/authority obligations are named.

**Done:** one proposed optimization demonstrates a reproducible useful benefit
without losing supported observations. **Stop:** keep noisy budgets out of the
default suite initially; do not trade diagnostics, ownership or exact values for
unqualified speed or rebuild an engine because of a historical microbenchmark.

### A26 Modules, Nominal Ownership And Reproducible Builds

**Basis:** Target / Fork. **Depends on:** A05/A08/A13; D3 identity and D4 composition.
**Owners:** industrial module/package contracts, module targets, interfaces,
questions 13/14 and nominal-identity research.

- [ ] Start with locked local multi-module analysis and passive public interfaces
  before federation, remote publication or a package-manager rewrite.
- [ ] Specify resolution, visibility, explicit imports/re-exports, initialization
  order and cycle policy; interface discovery must not execute module bodies.
- [ ] Compare revision-qualified declarations with stable public identity and
  checked compatibility; runtime instance owners/fresh brands remain separate.
- [ ] Challenge duplicate-version diamonds, identical artifacts via mirrors,
  wrappers versus re-exports, altered public predicates and same-number store IDs.
- [ ] Preserve the canonical private-implementation/interface identity rule while
  recording dependencies that actually determine public contract meaning.
- [ ] Define source/manifest/lock/toolchain/profile/build-input identity, offline
  reuse, pure fetch, cache validation and explicit edition migration.
- [ ] Separate source, behavior and wire compatibility; later signature/key/log/
  registry-transfer work requires its own threat and recovery profiles.

**Done:** selected libraries analyze without execution, resolve owners correctly
and reproduce artifacts from declared inputs. **Stop:** no proof of arbitrary
helper equivalence, identity from labels, silent lock upgrade or invented mirror type.

### A27 FFI, Specialized Profiles And Future Engines

**Basis:** Extend / Fork. **Depends on:** A03/A06/A13/A24; A14 for retained callbacks.
**Owners:** industrial FFI/profile contracts and
[engine admission](implementation_layers.md#admitting-an-optimized-engine).

- [ ] Choose one needed typed boundary with explicit value conversion, allocation,
  ownership, threading, blocking, effects and ordinary/abnormal error mapping.
- [ ] Specify callback return/retention, executor attachment, lifetime and supported
  unwind containment independently of the host language's default behavior.
- [ ] Keep foreign buffers/device memory transfer and profiling observable; a
  compatible array shape does not settle aliasing or memory publication.
- [ ] Require versioned input/output artifacts, independent fixture parity,
  installed packaging and actual host diagnostics before candidate promotion.
- [ ] Keep bytecode/native/GPU/restricted evaluator proposals opt-in until a
  measured pressure justifies one bounded engine or profile experiment.
- [ ] State fallback/rejection and removal gates for unsupported host combinations;
  specialized profiles must not silently reinterpret ordinary source meaning.

**Done:** one adapter/engine implements its declared boundary with useful measured
evidence and no hidden command policy. **Stop:** no general backend rewrite,
portable unwind, zero-copy or sandbox claim from an unsafe host escape.

### A28 Distribution, CI, Hosted Preview And Release

**Basis:** Host Gate / Investigate. **Depends on:** A01/A02/A21/A24/A30.
**Local surface:** `pyproject.toml`, changelog/README, distribution fixtures,
`.github/workflows/playground-ci.yml`, manifest/build metadata and Pages layout.

- [ ] Define experimental-preview claims by host: installed CLI, default browser,
  optional Pyodide, notebook and editor; do not conflate these support promises.
- [ ] Resolve root license, third-party notices, publisher identity and release
  ownership before publication; extension metadata is not a root license choice.
- [ ] Build and inspect the intended artifact from a clean source tree; verify
  grammars, runtime data, JS/WASM assets and demo outside editable installation.
- [ ] Observe same-revision CI jobs on their declared Python/Node/OS environments;
  a configured workflow and local release candidate are different evidence.
- [ ] Inspect authorized Pages source/settings and deploy only with approval;
  record exact revision/artifact identity, subpath imports and cache strategy.
- [ ] Run published-URL default/optional-host checks for the selected artifact;
  HTTP 200 or a timestamp cannot prove matched HTML/worker/parser/sample versions.
- [ ] Prepare rollback to a complete matching prior artifact, release notes,
  known gaps, checksums/provenance and a sanitized reproduction/support route.
- [ ] Distinguish freshness checking from regeneration; explain every generated
  manifest/WASM diff by changed inputs and retain successful `--check` evidence.

**Done:** owner-approved release claims match actual installed/hosted revision
evidence and a usable rollback. **Stop:** no push/deploy/publish, stable label,
compatibility promise or license selection from these planning notes.

### A29 Containers And Portable Notebook Integration

**Basis:** Host Gate / Investigate. **Depends on:** A22/A28/A30.
**Local surface:** Dockerfile/build context, `scripts/run_nomi_docker.py`,
`tools/docker/` and notebook/service readiness.

- [ ] Use an already available daemon to build/run the selected artifact; record
  an unavailable daemon rather than install or reconfigure a container runtime.
- [ ] Verify kernel startup, readiness, interruption, shutdown, restart and
  notebook discovery against real process/container state.
- [ ] Compare image-tag reuse with digest/build-input identity; pin the selected
  policy before treating a mutable tag as attested content.
- [ ] Retain generated credentials/loopback guards and test synthetic-secret
  sinks in launcher, server-owned logs, readiness and timeout failures.
- [ ] Review mounts, network, user, filesystem, resource limits and context
  exclusions under a declared notebook profile; do not advertise isolation by name.
- [ ] Challenge incompatible existing container, changed token/port/image,
  readiness impostor, missing notebook and partial startup/teardown.

**Done:** real clean-build/reuse/lifecycle evidence matches the declared local
profile. **Stop:** no public development-service exposure, daemon installation
or hardened-container claim without explicit approval and tested policy.

### A30 Security, Privacy, Redaction And Execution Isolation

**Basis:** Investigate / Target. **Initial analysis:** no prerequisite to finish
A09/A13/A18/A19. **Enforcement depends on:** each selected value, grant, transport
or result contract; those owners consume the initial threat model first.
**Owners:** industrial security, host/process/storage boundaries and sink policy.

- [ ] Define the preview threat model: trusted local code, untrusted data, imported
  packages, browser storage, subprocesses, agent proposals and remote effects.
- [ ] Inventory stdout, binding display, CLI JSON, kernel repr, diagnostics,
  causes, traces, exports, caches, clipboard, local drafts and retrieval as sinks.
- [ ] Specify sensitivity/retention/disclosure policy at each sink with synthetic
  values; masked visible text must not leave raw exports or cached evidence unnoticed.
- [ ] Inspect hostile display/host repr, nested keys/paths/errors, timing/length
  disclosure and redaction failures without using real credentials or user secrets.
- [ ] Separate effect declarations, grants, allowlists, resource limits, process
  isolation and sandbox guarantees; test only the chosen profile's actual controls.
- [ ] Define trust for external manifests/artifacts and dependency bootstrap;
  validation, hashing and authentication are different guarantees.
- [ ] Plan incident/revocation/cache-expiry and supported reporting procedures
  with owner approval; do not invent legal adequacy or public-response commitments.

**Done:** selected threats have explicit enforcement and negative evidence,
with honest unsupported/retention gaps. **Stop:** no vulnerability assertion
without reproduction, noninterference claim from masking or unsafe native probe.

### A31 Documentation, Learning, Research And Community

**Basis:** Investigate / Extend. **Depends on:** A01/A02 and semantic owners.
**Local surface:** README, docs index, runnable samples, target/research routes,
changelog, issue/PR instructions and contribution guidance.

- [ ] Walk beginner, contributor and bug-reporter routes through the supported
  preview; record missing information and repair friction instead of adding
  competing tutorial authorities.
- [ ] Keep runnable, accepted target, open proposal, supplied model and observed
  experiment statuses visible; hypothetical `lab.*` APIs are not installation steps.
- [ ] Update examples from real support/outputs and failure transcripts, including
  malformed input, stale state, denied authority and cleanup limits.
- [ ] Connect one executable documentation page to the A20/A24 example/check
  slice; distinguish extractable supported examples from aspirational targets,
  and record actual doc-runner results rather than treat fenced prose as a test.
- [ ] Link historical evidence to latest completion receipts, archive or consolidate
  stale scheduling lists and ensure each live question has one owning location.
- [ ] Turn research into bounded comparisons, independent oracles and decisions,
  not another catalog; preserve contrary results and inaccessible-source limits.
- [ ] Prepare sanitized issue reproduction, contributor setup, architecture routes,
  sample expectations and owner-approved release/community policies.
- [ ] Define human evaluation with task-specific expertise, accessibility context,
  equal semantic facts, assistance/consent and realistic limits on generalization.

**Done:** a new person can obtain a result, understand a limit and report/repair a
failure using current owners. **Stop:** no research-count completion percentage,
universal usability claim or public community commitment from documentation volume.

### A32 Agents, Retrieval And Repeatable Maintenance

**Basis:** Investigate / Extend. **Depends on:** A02/A31 and retrieval trust policy.
**Owners:** [AI collaboration](ai_collaboration.md), repo-local skills, prompts,
hooks/doctor, design registry and `tools/rag_mcp/`.

- [ ] Prepare task evals for current-source discovery, target/prototype conflict,
  unsupported profile selection, focused verification and clean resumption.
- [ ] Verify actual clients consume the intended skill/shim/hook routes; parsed
  configuration and doctor success do not prove useful agent behavior.
- [ ] Check retrieval coverage for source, Nomi, Rust, JS, schemas and documentation;
  dated reviews and cached snippets must not outrank current canonical owners.
- [ ] Recheck excluded/symlink/out-of-root sources and sensitive retained snippets
  at query/resource time; index presence alone is not current privacy enforcement.
- [ ] Keep checkpoints concise: goal, modified paths, exact next action, tests,
  dependencies and uncertainty; use file ownership to prevent overlapping edits.
- [ ] Promote repeated reasoning to skills and deterministic invariants to checks
  only after recurring friction is observed; remove superseded guidance.
- [ ] Use bounded context and source citations to evaluate result quality, not raw
  prompt size, number of subagents or a new retrieval database by default.

**Done:** representative real-client tasks cite direct current sources, choose
honest profiles and recover safely from stale context. **Stop:** no instruction
growth, permission caching or new tool integration without demonstrated need.

### A33 Text Interfaces, Strings And Scoped DSLs

**Basis:** Fork / Extend. Catalog expansion is documented; candidate execution
remains open. **Depends on:** A03/A08/A12/A13 and T/E experiment owners.
**Owners:** [text interface](../research/dsls/text_as_interface.md), strings/embedding,
layered configuration, DSL experiments and the cognitive packet.

- [ ] Start T1-T3 with representation intent, strict Text/Bytes decode and offset
  units; compare producing/consuming names under actual contracts, not naming lore.
- [ ] For one boundary, test structured whole-value encoders, template trust,
  argv construction, stream framing and consumer-specific escape rules (T4-T7).
- [ ] Preserve authored text and segment provenance through escapes, folding,
  included files and repeated expansion; source maps may be bounded/lossy explicitly.
- [ ] Compare lossless versus semantic formatting and localized message roles;
  T8-T10 need actual editing/discovery pressure, not another generic string API.
- [ ] Use E1/E2/E3/E6/E7/E9 first for delimiter collision, structured construction,
  named parse/check/bind guarantees, bound parameters and coordinate identity.
- [ ] Extend layered config only with concrete merge/overlay/list-deletion,
  environment/absence/dependency and bounded-evaluation cases (E4/E5/E8/E10).
- [ ] Keep E11-E22 solver/proof/temporal/device/documentary models conditional;
  their success and evidence semantics are not interchangeable DSL engine results.

**Done:** one composed interpretation boundary preserves meaning, provenance,
limits and current authority without evaluating user values again. **Stop:** no
universal SafeText/ValidatedText type, implicit prose execution, global grammar
extension or formatter-string interchange to avoid a structured contract.

## Domain Extension Recipes

These are conditional A16/A17/A27/A31/A33 tasks, not additional core features or
requirements for the next preview. The
[domain composition owner](../research/domain_composition.md) and its DC1-DC6
comparisons retain their payload/layer decisions. Reuse names, values, types,
relations, failure, effects, resources and tasks before proposing new primitives.
Begin each domain with inert descriptions and ordinary calls; execution follows
only after the relevant D1-D3 contracts and adapter profile are settled.

### Data, Databases, DAGs And Time

- [ ] Type a schema/snapshot/partition/asset reference and a two-input inert plan;
  distinguish scheduling, lineage, dataflow, control and provenance edge roles.
- [ ] Compare checked DAG ownership with a general typed relation; include cycles,
  diamonds, missing inputs, multiple valid topological orders and bounded feedback.
- [ ] Pin valid/system/event/processing time and retained historical availability;
  deleted backing content must not silently fall back to latest data.
- [ ] Compare aggregate revision guards, precise predicate validation and a named
  store isolation profile using write skew, absent rows and bypass writers.
- [ ] State incremental insertion/deletion laws per operation, cache read sets,
  backfill identity and publication authority; DAG readiness proves none of these.
- [ ] Gate one query/workflow adapter on independent duplicate/null/cardinality,
  order/error/source-map and uncertain-commit fixtures. Defer notation until DW3
  shows an ordinary-call failure; route to DW1-DW3 and DT1-DT5.

### AI, ML, Numerical Transformation And Agents

- [ ] Type a model specification separately from fitted state, preprocessing,
  optimizer/RNG/data position, inference artifact and training resume checkpoint.
- [ ] Bind split/entity/time/feature availability and adaptive feedback exposure;
  include model/prompt/metric/seed selection and unknown prior evaluation history.
- [ ] Specify supported numeric transformations, axes/units, staged binders,
  derivative domain and exact/tolerance/profile vectors before an AD adapter.
- [ ] Compare artifact invalidation/retraining with a method-qualified removal
  profile; cover stale checkpoints, exports, inference caches and retained copies.
- [ ] Freeze serving/request identity, retrieval sources, decoding context and
  tenant/current authority; an agent answer remains evidence input, not a tool grant.
- [ ] Gate one pinned engine or serving slice with independent shape/gradient,
  leakage, checkpoint, lost-ack and denied-tool fixtures. Model quality, privacy,
  generalization and unlearning claims require separate qualified evidence;
  route to DW4/DW5 and ML1-ML6.

### Messaging, Queues, Pub/Sub And Durable Workflows

- [ ] Define envelope/entity/event/delivery/attempt identity separately; distinguish
  queue receipt, subscription delivery and partition position/frontier.
- [ ] Model ownership, demand, settlement, redelivery and retained dedup horizon;
  include poison events, conflicting same-ID payloads, offset holes and rebalance.
- [ ] Specify exact atomic participants for inbox/outbox and external publication;
  crash after effect/before ack needs reconciliation, not an exactly-once slogan.
- [ ] Separate replaying pure projections from effectful workflow replay, handler
  edition, current authority and saga compensation; feedback need not be a DAG.
- [ ] Bound queued bytes, active handlers and shutdown join; a confirmed local
  stop must not conceal unknown remote delivery or incomplete settlement.
- [ ] Choose one MSG carrier/adapter under MSG1-MSG6 after typed contracts; leave
  other brokers as counterexamples, not a required implementation portfolio.

### Web, Services, CLI And Automation

- [ ] Derive typed request/response/command values, media/schema/version, explicit
  path/argument roles and transport-specific error/stream completion.
- [ ] Compare conditional update, idempotency/reconciliation and authorization
  freshness using lost response, stale precondition and repeated invocation.
- [ ] Keep argv construction separate from shell source; cover spaces, newlines,
  leading dash, framing delimiters, stdout data and stderr diagnostics.
- [ ] Define deadline/cancellation/body/stream ownership through files, HTTP and
  subprocesses; slow consumers and closed pipes need bounded cleanup evidence.
- [ ] Add one practical library example only after supported ordinary calls,
  providers and codecs agree; reject hidden global environment reads or implicit
  retry of non-replay-safe work. Route to A12/A13/A17/A20 and T4-T7/DC5.

### DevOps, Cloud, Configuration And Deployment

- [ ] Represent desired state, observed revision, inert plan and apply receipt
  separately; checking a plan must not execute provisioners or authorize apply.
- [ ] Bind layered config origins, overlay/list-delete policy, dependency basis,
  secret references and environment/profile identity before interpolating text.
- [ ] Test changed context after review, partial apply, denied/revoked grants,
  drift and uncertain outcome; recorded intent is not a completed deployment.
- [ ] Specify reconciliation/retry/rollback-versus-compensation and resource
  lease limits at the real provider, not only a local plan object.
- [ ] Admit one profiled adapter with reviewed preview/apply/observe boundaries;
  postpone general cloud orchestration and global infrastructure syntax. Route
  to A13/A17/A27/A30, E4/E5/E8 and DC5/DC6.

### Visual Tools, Design Systems And Collaboration

- [ ] Define model/view/selection identity, coordinate frame, token/reference
  edition and semantic command independently of mouse/keyboard gestures.
- [ ] Begin with a read-only projection that exposes the same facts as text;
  sorting/filtering or changing a coordinate frame must not retarget an action.
- [ ] Keep draft validity, checked model, inverse-edit domain, comments and source
  provenance explicit; unsupported inverse edits should refuse rather than guess.
- [ ] Compare current-authority/review/base freshness at the actual commit owner,
  then review convergence, constraint validity and human shared understanding separately.
- [ ] Add keyboard/IME/screen-reader/zoom and split-information handoff tasks;
  an authentic acknowledgment is not a completed check or a mental-state proof.
- [ ] Gate editable views or new notation only on HX/DC discriminator outcomes,
  with textual repair fallback; route to HX1-HX4/HX6/HX8 and NL2/NL4.

### Support, Telemetry, Diagnosis And Runbooks

- [ ] Model observations, hypotheses, explanation questions, bounded diagnostic
  steps and proposed actions as different values with named evidence coverage.
- [ ] Preserve run/snapshot/epoch identity and total/shown/omitted/redacted facts;
  missing telemetry is not proof that an event never occurred.
- [ ] Compare why/why-not, false-premise and multiple-blocker diagnosis before
  suggesting repair; changing the first false condition may be insufficient.
- [ ] Make a runbook step declare inputs, authority, effects, limits and expected
  observations; inspection must not run it or repeat an uncertain remote effect.
- [ ] Pilot one supplied-fact repair/handoff task before integrating real remote
  operations; useful uncertainty/refusal is a valid outcome. Route to A19/A30,
  C09/C12/HX2/HX5/HX8 and DC5.

### Mathematics And Scientific Research

- [ ] Type expressions, binders, assumptions, units, axes, frames and method
  profiles; numeric equality, symbolic equivalence and proof are distinct claims.
- [ ] Compare shared-origin affine uncertainty, explicit covariance and qualified
  joint propagation using X-X, shared calibration and missing/nonlinear inputs.
- [ ] Preserve protocol/population/data/software/randomness/evaluation identities;
  a complete manifest is not independent replication or scientific validity.
- [ ] State exact arithmetic/reassociation/approximation and solver budget/result
  policies; timeout, unsupported and no solution must remain distinct.
- [ ] Use an established procedure behind a scoped adapter for one pressure case;
  do not build a universal math, proof or simulation evaluator first. Route to
  A03/A16/A27, DW4/DW5, ML2/ML3 and scoped E experiments.

### Documents, Legal Structure, Naming And Catalogs

- [ ] Preserve source/edition/reference, term/concept/entity/label and context
  before interpreting imported prose, scientific names or catalog records.
- [ ] Separate style lint, controlled parsing, domain checking, human interpretation
  and authorized action; structural validity is not truth, assent or legal authority.
- [ ] Model precise/directional/approximate/disputed mappings, aliases and missing
  evidence rather than merge concepts by title, spelling or translation label.
- [ ] Compare lexical/grammatical/domain argument roles, quantifier scope, modality,
  changed referents and audience/locale under ordinary-call challengers.
- [ ] Let contradictions and ambiguity remain inspectable; an institutional
  review/decision protocol owns interpretation, not a universal Bool replacement.
- [ ] Pilot one versioned resolver or documentary import/report at DC3/DC4/DC5,
  retaining provenance/redaction and explicit human review; defer universal
  ontology, English compiler grammar and unsupported expert-domain execution.

### Spatial, Musical, Physical And Other Future Domains

- [ ] Use explicit frame/clock/unit/event/signal identity, timing and model edition
  in an inert geometry/score/device description before actual actuation.
- [ ] Compare checked description, simulation evidence and real observed outcome;
  a drawing or bounded simulation must not certify physical feasibility/safety.
- [ ] State delay, sampling, control authority, emergency/stop behavior and
  hardware/host limits; independent real-time and safety evidence is a new gate.
- [ ] Reuse chemistry/biology/finance/reference notation as domain-owned values
  where useful, preserving its specialized identity, uncertainty and interpretation.
- [ ] Admit one new domain via DC6 only if its ordinary composition works without
  global evaluator changes; defer real device/clinical/financial/legal authority
  claims to their qualified owners and required evidence.

## Eleven Research Units To Turn Into Evidence

This is execution preparation for the existing
[gap owners](../research/README.md#research-gap-continuation), not another question
series. Start with supplied judgments/independent oracles, then a removable
model/adapter or human comparison as appropriate. Their detailed sources and
method limitations remain with the research owner.

| Unit / route | Next bounded task | Discriminator and completion evidence |
| --- | --- | --- |
| Polymorphic sharing; A05/A08, D1/D3 | Compare allocation/type judgments under conservative, relaxed and effect/region-aware rules | One delayed slot and an outer-slot wrapper reject incompatible uses; fresh factories/stateless cases explain acceptance or benign rejection without changing allocation |
| Memory publication; A13/A15/A27, question 15 | Write owned-message/guarded-sharing litmus outcomes and admitted synchronization edges | Payload/readiness and reused buffers do not gain visibility from timing; later model/host evidence covers the declared memory profile |
| Predicate consistency; A16, DT4 | Prepare two-owner write-skew and absent-row schedules for aggregate, predicate and store-profile candidates | The real commit boundary preserves the invariant or returns conflict; stale snapshots and per-row freshness alone cannot pass as proof |
| Foreign callbacks; A14/A27, question 5 | Compare safe admission/re-entry/deregistration histories before one pinned adapter | Immediate-result needs, live gate lifetime and in-flight drain remain distinct; unsupported thread/unwind behavior is refused |
| Nominal identity; A05/A26, questions 13/14 | Compare passive interface records across a dependency diamond, re-export and independent stores | Declaration identity, public contract dependency and runtime owner facts explain crossings without import execution or arbitrary private-source identity changes |
| Adaptive evaluation; A16, ML1 | Prepare fixed-versus-selected prediction and feedback-exposure records | Selection/optional stopping and unknown history qualify the claim; a later procedure-specific evaluator establishes only its named assumptions |
| Correlated uncertainty; A03/A16, DW4 | Define joint/latent-source affine oracles and unsupported nonlinear/missing-dependence cases | Same-origin cancellation differs from independent inputs; shared-offset averaging states its measurand and independence/variance assumptions |
| Learned removal; A16/A30, ML4 | Compare invalidation/retraining with one supported removal reference procedure | Old mean/model, stale checkpoints/copies and repeated requests expose storage deletion versus influence; reference scope/assumptions are explicit |
| Calibrated reliance; A21/A31, C12/HX8 | Independently review a matched repeated-advice stimulus sequence before a pilot | Omission/commission opportunities, correctness, independent checking and confidence are scored separately; no longitudinal/population claim from a pilot |
| Team understanding; A21/A31, C12/HX8 | Prepare split-information dyad handoff and missing-check oracles | Assigned/acknowledged/completed/unknown facts remain distinct; pair-level dependencies and prompting confounds are retained |
| Contrastive diagnosis; A19/A31, C09/HX2/HX8 | Compare equal supplied facts as raw trace versus why/why-not view | False premise, wrong run and multiple blockers remain visible; explanation support, repair sufficiency and permission are scored separately |

## Bounded Redesign And Rewrite Triggers

Larger changes are legitimate when a required contract cannot be represented
honestly. These notes identify conditions for proposing them, not permission
to rewrite now. Start with the failed program and preserve a rollback/unsupported
boundary; do not use file size, research breadth or aesthetic preference alone.

| Pressure / owner | Small first move | Larger proposal justified when | Evidence and replacement limit |
| --- | --- | --- | --- |
| Continuation state; A08/A11/A18 | Record operand/phase/child/pending completion for two minimal failures | Isolated handlers cannot preserve once-only work and ancestor cleanup without duplicated state | One versioned frame/completion design, independent traces, explicit unsupported shapes; no simultaneous task/IR rewrite |
| Raw reparsing; A04/A06 | Structure one family behind a versioned adapter | Raw text loses source, argument/binder identity or profile rejection that the admitted family requires | Dual producer/consumer fixtures and retained fallback; do not replace every frontend at once |
| Typed artifacts; A05/A08/A26 | Define and check one closed typed interface/slice | Host AST/dictionaries cannot retain required symbol/type/effect/region owners | Separate supplied/inferred facts and downstream consumers; do not build a universal checker prematurely |
| Completion/cleanup carriers; A11/A14/A15 | Compare one accepted slice with hosted compatibility | Distinct completion channels cannot compose causes, transfer targets and joins under current representation | Negative escape/cancel/cleanup fixtures and capability-gated migration; no blanket suppression change |
| Registry/import ownership; A02/A18/A32 | Inventory one concrete cycle or duplicated policy | Parser/runtime/transport initialization forces policy duplication or prevents safe replacement | Passive descriptors and bounded lower owner; no wrapper framework around every module |
| Process transport; A18/A27/A30 | Bound/version one request-response envelope | Whole buffering or one-shot process state cannot meet a measured needed budget/lifecycle | Streaming or persistent candidate with reset/cancel/close/error fixtures; timeout never advertised as isolation |
| Diagnostics/source mapping; A04/A06/A19 | Add a validated versioned span carrier for one path | Incompatible host locations/envelopes lose originating source or causes repeatedly | Shared semantic record with small adapters; do not require all proposed event producers at once |
| Playground document state; A18/A21 | Specify current document/run/draft/model transitions | Independent mutable UI flags cannot maintain identity, freshness and recovery under tested workflows | One owned state protocol with preservation/disposal cases; no cosmetic redesign as a substitute |
| Backend performance; A25/A27 | Measure a stable corpus and one bottleneck | A chosen engine cannot meet the justified budget while preserving the closed contract | Opt-in engine, parity, host/installed evidence and measured benefit; retain readable orchestration |
| Documentation sprawl; A31 | Resolve one duplicate owner/stale route | Live priorities or guarantees are genuinely contradicted across active docs | Consolidate authority and retain dated evidence in history/reviews; no deletion of unresolved obligations |

- [ ] For each proposed rewrite, state old/new artifact boundaries, unchanged user
  observables, migration profile, fallback, proof/test oracle and removal trigger.
- [ ] Compare a narrow repair, a bounded extraction and a replacement using the
  same pressure cases; explain which future design choices each preserves.
- [ ] Migrate one vertical category/consumer at a time and review generated assets,
  installed distributions and actual host behavior only where affected.
- [ ] Keep target acceptance and prototype-mechanism replacement separate; a
  successful compatibility rewrite need not accept its substrate's semantics.

## Completion Evidence To Prepare

The following are future evidence requirements, not checks run for these notes.
Select the appropriate tier for a task; do not rerun unrelated expensive suites
as a substitute for an independent local oracle.

| Deliverable | Minimum evidence to prepare | What must remain unclaimed |
| --- | --- | --- |
| Documentation/action notes | Lifecycle/inventory/links, authority and owner review, whitespace | Execution of the proposed tasks |
| Design choice | Two credible contracts where unsettled, three program levels, formatting/diagnostics, falsifier and ledger decision | Runtime/compiler/human validation from paper examples |
| Typed artifact | Independent inferred/supplied positive/negative facts, schema/version/resolution and downstream checking | A whole-language checker from one slice |
| Runtime repair | Minimal reproduction, independent value/effect/cause/order oracle, neighboring modes and relevant broader suite | Unsupported generators, tasks or target completion from hosted parity |
| Parser/lowering | Acceptance/rejection, structured payload/spans, corruption cases and effect-order parity | Full execution from parse acceptance or equivalent stdout |
| Domain adapter | Pinned profile, independent semantic/error/authority/source-map vectors, unsupported/uncertain outcomes | Another engine/domain's laws or universal reliability |
| Playground change | Actual worker/Monaco/runtime workflow, recovery/stale/reset/draft cases, desktop/mobile evidence | Assistive-technology or human comprehension from screenshots |
| Notebook/editor | Real supported host messaging/task lifecycle and declared platform/version | GUI/client execution from helper or mocked tests |
| Artifact/distribution | Clean installed artifact, generated freshness, assets/digests and outside-checkout execution | Remote CI/publication from local packaging |
| Remote release | Owner approval, exact deployed revision, hosted checks and rollback evidence | Identity from HTTP status alone or stable compatibility from a preview |
| Security boundary | Declared threats/sinks, synthetic-secret negatives, enforcement and retention scope | General sandbox/noninterference/legal adequacy from redaction |
| Human study | Reviewed supplied facts, consent/setup, matched conditions, expertise/confounds and uncertainty | Universal/population/longitudinal benefit from a small pilot |
| Performance | Corpus/toolchain/hardware/options, cold/warm distributions and memory/overhead | Whole-product speed from one cached arithmetic example |

## Handoff And Task Closure

- [ ] Choose the next task through the roadmap's existing dependencies, informed
  by current receipts and one failed user/program pressure; do not execute this
  document as a giant unchecked installation or feature list.
- [ ] Start each task with the canonical owner and applicable repo-local skill;
  retrieval supplies candidate paths, not authority or permission.
- [ ] Record the selected hypothesis/contract, exact first reproduction/judgment,
  expected artifacts and test/host evidence before edits or expensive experiments.
- [ ] Leave changed paths, actual checks, unresolved risks and the next exact step
  in the owner/receipt when a pass ends; do not report the whole A item complete
  because one bounded patch or corpus expansion finished.
- [ ] Revisit/remove notes after their owner settles the question or their pressure
  disappears; replace stale task prose with a link to evidence, not a second live
  copy of semantic decisions or implementation status.
- [ ] Preserve the ability to stop, refuse, defer or reject a candidate. Coherent
  extensibility is successful when new domains fit explicit boundaries, not when
  every idea becomes permanent syntax or immediate release scope.
