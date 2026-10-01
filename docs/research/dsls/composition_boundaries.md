# Composing Orthogonal DSLs

> Status: original Nomi research fixtures and proposed contracts, 2026-10-01.
>
> The APIs and diagnostics below are hypotheses. No new syntax, domain engine,
> foreign adapter, or target-language guarantee is accepted here.

## Why Composition Is The Hard Test

The [atlas](domain_atlas.md) supplies breadth and the
[model comparison](orthogonal_models.md) supplies distinct semantic laws.
This chapter asks what happens when those laws meet inside one program.
All examples are original and explicitly bounded. External mechanisms remain
documentary evidence; the examples are not claims of an implemented Nomi API.

A proposed shared boundary protocol should retain:

```text
source/draft + dialect/version + environment identity
    -> parse evidence
    -> domain check evidence
    -> bound inputs + assumptions + authority request
    -> plan/model/projection
    -> execution/search/render observation
```

This is a vocabulary for inspection, not a universal linear pipeline. Some
owners combine stages; some models are never executed; imports may need
authority before checking; a reactive value may need a lifetime during binding;
a proof checker accepts a proof term rather than an execution plan. Each
adapter must state which stages it actually owns.

## Four Competing Integration Shapes

These refine the existing A/B/C [Nomi candidates](nomi_candidates.md), preserving
ordinary libraries as the initial choice.

| Shape | Useful when | What it retains | Stop condition |
| --- | --- | --- | --- |
| A / ordinary library values | Domain structure is readable as calls/records | Nominal domain types, ordinary host scope, explicit effects | Repeated source loss, unreadable whole programs or impossible domain refactoring |
| B / parsed foreign artifact | Native notation is important for users/interchange | Original foreign source, dialect, checked owner/environment | Cannot retain spans/versions or separates neither checking nor execution |
| C / bounded scoped notation | A and B fail a measured interaction requirement | A domain-owned grammar island with editing/formatting/reduction | Captures host names implicitly, mutates global grammar or reuses host control meaning |
| Adapter between domain artifacts | Two different laws must coexist | Typed conversion, lost-information report, target constraints | Pretends conversion is lossless or invents a shared evaluator |

A shared artifact envelope can carry provenance and diagnostic metadata while
its payload remains a domain-specific IR. A query, circuit, ontology and music
score do not need one interchangeable node algebra. This is a hypothesis to
test in E12/E22, not a prescribed implementation hierarchy.

## Twelve Boundary Pairs

For each pair, the safe composition below is a proposed explicit contract.
“Invalid inference” identifies a law to reject in a fixture, not a prohibition
on integrating those systems.

| Pair | Invalid inference | Proposed composition / discriminator |
| --- | --- | --- |
| Text template + structured configuration | Escaping a string validates the rendered resource | Preserve literal/value holes; encode whole values; decode/check resulting domain artifact (E2/E3) |
| Query + policy | Empty selection means denied or false | Preserve result cardinality; derive a named policy input; return determining evidence (E13/E19) |
| Ontology + schema | Not entailed means invalid, or shape-valid means logically complete | State entailment regime separately from validation graph and report (E19) |
| Constraint model + deployment | Feasible allocation is permission to deploy | Witness -> checked resource plan -> authority-bearing executor -> observation (E14/E16) |
| Proof/model checker + runtime | Formal success proves arbitrary deployed behavior | Retain assumptions, model mapping, bounds/axioms and implementation correspondence (E15) |
| Rewrite optimizer + numeric function | Algebraic equality permits float/effect reordering | Declare arithmetic/effect theory and side conditions before transformations (E20) |
| Reactive binding + resource scope | Construction ends when the initial value exists | Give subscriptions/update sources a lifetime, disposal and cancellation contract (E17) |
| Stream window + calendar | A day is always a fixed number of elapsed seconds | Convert through a named zone/calendar/time-domain policy (E18) |
| Signal/circuit + ordinary task | Host evaluation advances physical/logical time | Keep elaboration, simulation ticks and device execution separate (E17/E18) |
| Probability model + solver | A score is a draw; a best point is a posterior | Name score/sample/condition/infer/optimize and preserve method/evidence (E21) |
| Geometry + motion program | A valid shape/kinematic model is a valid movement | Check frame/unit/target constraints; simulate; execute only with device authority (E22) |
| Localized message + UI/document | All holes are text and translating a label changes a node ID | Preserve named argument schema, locale, branch/element identity and rendering context (E13/E22) |

## Fixture 1 — A Beginner's Schedule And Message

Pressure: show a localized reminder for a recurring local-time event. The
explicit long form should be intelligible without a grammar extension.

Research pseudocode; function names and artifact types are unimplemented:

```text
zone = zones.lookup("America/Toronto")
rule_source = text_source("FREQ=WEEKLY;BYDAY=MO", "reminder.rule")
rule = calendar.parse_recurrence(rule_source, CalendarDialect)
schedule = calendar.bind(rule, local_start, zone, AmbiguousTimePolicy)
message = messages.check(catalog_entry, locale, argument_schema)
occurrences = calendar.expand(schedule, bounded_interval)
label = messages.render(message, {"count": occurrences.count})
```

Assumptions to choose before a runnable experiment: the start is a local
date/time; the zone database and calendar dialect are pinned; the interval is
finite; the ambiguity policy is explicit. Parsing does not schedule a timer.

Failures: malformed recurrence; unknown zone; missing plural branch/argument;
unrepresentable local occurrence under the selected policy; expansion limit.
None should be silently converted to an empty label or an empty occurrence
list. Locale affects message selection and formatting, not occurrence identity.

Proposed diagnostic:

```text
calendar.bind: ambiguous local occurrence at reminder.start
source: local date/time argument, not reminder.rule
context: zone=America/Toronto; ambiguity policy was not supplied
help: select the occurrence policy before creating a checked schedule
```

Explanation projection: original rule, decoded literal, start/zone/version,
policy, bounded generated occurrences and message argument schema. Formatting
may alter outer indentation only when exact embedded source remains unchanged.
Discriminator: A versus B on readability, source ranges and locale changes;
do not consider C until those results expose a concrete failure.

## Fixture 2 — Allocate, Explain And Deploy

Pressure: place three jobs on two workers subject to capacity and policy,
then create resource descriptions. The solver is not the deployment owner.

Research pseudocode:

```text
inventory = decode_inventory(external_value, InventorySchema)
problem = allocation.describe(jobs, inventory, constraints, objective)
search = allocation.find(problem, SearchBudget)
witness = allocation.require_feasible(search)
decision = policy.decide(request, witness, checked_policy, policy_environment)
approved = policy.require_allowed(decision)
resources = deployment.describe(witness, approved, resource_schema)
plan = deployment.check(resources, cluster_snapshot, field_ownership)
observation = deployment.apply(plan, cluster_handle)
```

The function vocabulary deliberately separates domain stages. It does not
suggest that the assumed `require_*` functions are accepted APIs. A Nomi
implementation must decide which variants return Result and which evidence
the caller must inspect rather than hide behind propagation.

Failure-heavy cases:

- Search budget expires with an incumbent but without an optimality certificate.
- A feasible witness violates an independent authorization policy.
- Inventory changes after search and invalidates capacity assumptions.
- Schema checking succeeds but domain admission rejects a resource.
- Applying several resources succeeds partially before cancellation.
- A policy evaluation diagnostic occurs even when another rule allows access.

Proposed diagnostic:

```text
deployment.check: allocation assumption no longer holds
related: problem.worker["w2"].capacity; observed inventory revision
evidence: feasible witness under revision 12; current revision 13
help: rebuild the plan from a fresh inventory or explicitly reconcile the change
```

Inspector: solver problem/witness/bounds, determining policy rules, resource
source map, observed revision, field owner, requested effects and partial
completion record. Secrets remain redacted without discarding origin identity.
Discriminator: separate artifacts versus a convenient universal `run`; reject
the latter if it obscures any of these facts (E14/E16/E19).

## Fixture 3 — A Live Measurement And Signal Model

Pressure: ingest timestamped measurements, validate units, compute a windowed
estimate, and drive a simulated sampled signal. This combines four meanings of
“stream”: arrival sequence, event-time windows, reactive updates and samples.

Research pseudocode:

```text
measurements = data.decode_stream(input_handle, MeasurementSchema)
quantities = units.check_measurements(measurements, expected_dimension)
windows = events.window(quantities, EventClock, endpoints, late_policy)
estimate_updates = statistics.estimate(windows, inference_method, random_state)
signal_model = signals.describe(estimate_updates, sample_clock, hold_policy)
simulation = signals.simulate(signal_model, initial_state, finite_sample_count)
```

Independent choices: event timestamp versus arrival timestamp; window endpoints;
late-data update versus discard; deterministic exact estimate versus stochastic
approximation; conversion from an event update to a sampled signal; missing
sample/measurement policy; source/subscription lifetime. No shorthand may imply
these choices automatically.

Proposed diagnostic:

```text
signals.describe: event-time updates have no sample-clock conversion
related: windows.clock; signal_model.clock
help: supply a hold/resampling policy with declared missing-update behavior
```

Explanation: versioned input codec, quantity unit conversion, event/arrival
timestamps, watermark/trigger policy if supplied, estimate evidence, random
state identity, sample clock and conversion rule. Cancellation must dispose
the live input and update subscription according to the accepted resource owner.
Discriminator: nominal time/stream wrappers versus a scoped notation tool;
measure clarity and retained evidence before evaluating punctuation (E17/E18/E21).

## Fixture 4 — Strings Across Several Languages

Pressure: a localized narrative choice references a named asset whose bytes
match a pattern, then generates a query and a diagram of the resulting paths.
This is intentionally adversarial: the same `Text` representation carries many
different roles.

```text
user_text -> literal query parameter
asset_bytes -> byte-pattern matcher input
pattern_source -> named regex/byte-pattern parser
story_source -> narrative parser with branch identifiers
message_source -> locale-aware message parser with named arguments
path_results -> graph nodes/edges
node_display_text -> diagram label encoder
```

Original payloads: a quote/newline in display text; a brace in message source;
an asset name containing a slash; an emoji before an inner error; duplicate
path results; an empty collection; a story label identical to a host variable;
a regex literal that would be a quantifier if inserted as source.

Required evidence: role-tagged holes, byte/character offset units, missing versus
empty cardinality, branch/node identity separate from visible labels, explicit
dialect boundaries and source-backed diagnostic chains. Formatting or renaming
outer host source must not silently rewrite a foreign binder or asset key.

Proposed diagnostic:

```text
message.check: unknown argument "branch"
primary: catalog entry, decoded offset 27 (Unicode scalar units)
origin: embedded literal in story_ui.nomi
related: supplied argument schema contains "count" and "name"
```

A source map should distinguish exact correspondence, transformed text and
generated material with multiple origins. Assigning a fake precise original
span to generated syntax is worse evidence than naming the generating inputs.
E1/E2/E7/E9 cover exact source and mapping; E13/E22 add multiplicity and domain
identity. This fixture keeps strings central as coverage expands.

## Reduction, Formatting And Diagnostics

An inspection surface should show the relevant domain reduction without
pretending every reduction is a Python AST desugar operation:

| Domain | Inspectable artifact | Meaningful explanation |
| --- | --- | --- |
| Query | Bound plan and parameter map | Cardinality, dataset/schema, operation/source correspondence |
| Policy | Checked rules, request/environment | Determining rules, missing facts, evaluation diagnostics |
| Constraint | Variables/domains/constraints/objective | Witness, violated constraint, search status/bound |
| Proof/model | Proposition/model/assumptions | Goal/proof dependencies or counterexample trace/scope |
| Rewrite | Theory/rules/strategy/extraction | Applied side conditions and equality justification |
| Temporal | Clock/window/transition model | Enabling, late decision, tick/sample/event correspondence |
| Geometry/device | Scene/program/target bindings | Frame/unit changes and unsupported target capability |
| Text/media | Parsed message/document/score | Argument/mode/locale identity and rendered origin |

Proposed machine diagnostic fields extend the existing dossier's source-map
candidate: owner, phase, artifact/environment version, code, severity, source
range with offset unit, related origins, assumptions, evidence status, and
redacted context. Domain plugins may add typed details; host tools need a stable
common envelope. This does not prescribe one universal diagnostic payload.

Formatter rules to compare:

1. Outer formatting preserves the decoded foreign source or records a deliberate
   transformation with a mapping.
2. A foreign formatter is selected by explicit owner/dialect, not inferred from
   whichever strings look familiar.
3. Reformatting a draft is allowed to report uncertainty; it must not promote
   the draft to a checked artifact.
4. Renaming a host binder and renaming a foreign symbol are separate operations
   unless the checked binding map proves correspondence.

## Costs, Versioning And Portability

Different models have different ways to exhaust resources. The research
fixture suite should include recursion/grounding fanout, exponential search,
solver budget, state-space explosion, unbounded stream retention, excessive
pattern work, render expansion, imports, numerical nonconvergence and generated
device code size. A deadline is not a complete memory/output/authority policy.

Cache keys should be tested against source, domain/dialect version, checking
environment, imported data/schema, target capabilities and relevant method
configuration. Equal rendered text is not sufficient identity for all domains.
Stored artifacts require a declared recheck/migration rule before upgrade.

Cross-backend comparisons should transport domain values through a declared
contract and compare evidence, not merely final text. Python, JS, Rust/WASM and
future backends may expose different numeric ranges, text indices and host
capabilities; an adapter must report an unsupported boundary honestly.

## Admission And Rollback

Use E13-E22 in the existing [experiment table](nomi_candidates.md), alongside
E1-E12. These tests can first use finite models or pinned offline fixtures. A
foreign integration later adds its own pinned engine/version evidence; it
cannot inherit passing status from our local illustrative probes.

Before admitting a scoped language tool, require:

- A beginner, production and failure-heavy whole program exposing a measured
  failure in the ordinary library/parsed-artifact alternatives.
- A named semantic owner, dialect, phase, scope, result algebra and authority.
- Draft recovery, mapped diagnostics, formatting, rename and explanation behavior.
- Inspectable construction/reduction and conformance fixtures independent of
  the selected parser/solver/renderer substrate.
- An extraction/removal plan that preserves the domain library when notation
  is withdrawn; an implementation bridge routed to existing design owners.

Stop a candidate when it silently changes core token jobs, implicitly captures
names, conflates unknown with false, treats checked data as execution permission,
or makes errors less explainable. A syntax-only readability win does not outweigh
the loss of those facts. No formal DSL design packet or runtime implementation
is warranted by this expansion alone.
