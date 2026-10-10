# Nomi As A Computational Medium

> Status: guiding product vision; proposed directions and open architectural questions.
>
> This defines the ambition, not current support or newly accepted syntax.
> Release milestones are experiments toward it, not its boundaries.

## The Design Object

Nomi should help people turn ideas into understandable, usable computations,
and keep understanding and control as those computations change and grow.
Design the whole human-computer activity: the language, representations,
tools, examples, feedback, collaboration, execution and surrounding practices.
The programming language is a central part of that system.

A person might begin with a question, a table, a sketch, a demonstration, an
equation, an example, a conversation or a piece of code. They should be able to
make the important meaning explicit, inspect alternatives, revise the model,
decide what to trust and authorize what happens. They should also be able to
teach, share and maintain that work without recreating all its context.

The ambition is to synthesize useful mechanisms from programming-language
research and human activity wherever they occur. Mathematics, spreadsheets,
writing, design, games, music, scientific instruments, organizational work and
physical interaction are legitimate sources of pressure. The existing corpus
is a starting map. An unlisted discipline or an unfamiliar interaction is not
out of scope merely because it has no registered packet.

The [cognitive foundations](../research/cognition.md) explain why the environment
participates in reasoning. [Target Design](README.md) owns the current language
shape; the [interaction proposal](interaction_model.md) owns representation and
revision candidates. This page owns the broader purpose and questions that can
challenge both. It is not a second implementation queue.

## What “Best” Must Mean In Practice

Aim for a system that helps more people accomplish demanding work with less
avoidable confusion, error and maintenance burden. Evaluate that ambition
through actual tasks and competing designs. A larger feature inventory, a
shorter program or stronger formal machinery alone cannot establish it.

| Desired human outcome | What would count as evidence |
| --- | --- |
| Begin with an idea | A person can express an initial model without knowing the whole system or choosing all its abstractions first. |
| Understand what it means | They can predict relevant values, dependencies, assumptions, effects and failure cases; an attractive result alone is insufficient. |
| Explore and create | They can try alternatives, retain useful partial work and form abstractions from examples without accidentally acting on the world. |
| Correct a mistake | They can locate the actual cause, distinguish missing knowledge from invalid data, and make a repair whose consequences are visible. |
| Grow without losing the model | The same concepts survive reuse, stronger checking, larger data, concurrency, distribution and collaboration; necessary migrations are explainable. |
| Delegate while retaining agency | People can constrain a tool or agent, inspect its proposal, resolve ambiguity and determine what actually happened. |
| Work with others | A new contributor can recover decisions and assumptions; conflicts in meaning remain visible even when files merge. |
| Use it in real conditions | Relevant latency, memory, accessibility, privacy, deployment and failure-recovery behavior are measured on declared tasks and hosts. |

These objectives can conflict. A notation can make creation easier and review
harder; an abstraction can lower repetition and raise the learning threshold.
Record whose activity benefits, whose becomes harder and under which conditions.
Compare beginners, domain practitioners, experienced developers, reviewers and
maintainers rather than inventing one average programmer. Early observations
can expose problems; population-wide claims need evidence of their own.

## Broaden The Unit Of Design

### An evolving model, not only a finished program

Keep the route from an uncertain idea to a dependable artifact visible. A draft,
example, observation, assumption, checked contract and executed result represent
different kinds of knowledge. Their relationship should be navigable without
pretending that one proves all the others.

Consider a water-use plan. A unit type can prevent confusing liters and seconds;
a constraint can cap daily use; a test can check a schedule. None establishes
that a sensor is accurate or that the chosen policy serves the people affected.
The system should expose the model's assumptions and evidence boundaries and
let people revise them. This is a tooling/modeling hypothesis, not a proposal
to encode every social judgement in the type system.

Investigate artifacts that connect definitions, examples, data, explanations,
tests and change history. The appropriate ownership and storage may differ by
domain. Do not assume that putting everything in a source file, notebook or
universal graph solves that question.

### Several ways to express and inspect meaning

Text, tables, equations, diagrams, timelines, forms and dialogue can expose
different relationships. Study both authoring and inspection, including their
transitions: editing a row, seeing its formula, understanding a dependency,
extracting reusable logic and explaining a change to another person.

Text-primary with derived views is a reversible current candidate. Structured
authoring with source export remains a serious challenger. A domain may require
a mixed arrangement. None becomes the global answer merely because the current
parser or editor already exists. Compare identity, incomplete states, comments,
round trips, ambiguity, accessibility and collaborative change under each.

All supported channels need an explicit account of the meaning they produce
and the action they request. A proposed edit is not an execution grant. A change
to a model, a view layout, a program and external state are different operations.
Shared semantic commands are one candidate for connecting modalities; they may
need domain-specific families rather than one universal edit language.

### More than one computational way of thinking

Functions and explicit control flow remain important. Also investigate relations,
constraints, queries, transformations, state machines, reactive dependencies,
staged plans, simulations and stochastic models when a task calls for them.
Distinguish their laws and outcomes: a missing solution, an interrupted search,
an estimate and an observed event are not ordinary false values.

Synthesis should make these models compose intelligibly. It need not force them
through one evaluator or introduce syntax for each. Ordinary libraries, scoped
languages and new core mechanisms are competing placements. If a library-only
encoding repeatedly obscures the model, revisit the placement rather than
protecting a small core for its own sake. Any accepted change still needs
coherent semantics, diagnostics, tooling and independent examples.

### Creation includes unfinished work

Explore partial programs, provisional data and incomplete models as part of the
normal activity. Compare last-good snapshots, explicitly typed holes, isolated
partial evaluation and domain drafts. Recovery guesses must remain distinguishable
from intended meaning. A formal semantics for supported holes could change what
can run safely; a parser's guess does not provide that semantics.

Learning also needs room to make concrete things before naming general patterns.
Inspectable examples, reversible experiments and progressive assurance should
help a person acquire useful concepts. A restrictive editor that refuses every
intermediate state may be correct about completed programs and still fail at
supporting their creation.

### Collaboration and automation change the problem

Study handoff, negotiation, evolving requirements, multiple authors and long-lived
systems. Revision identity and type compatibility are necessary facts, but do not
explain why a decision was made or whether a combined change preserves intent.
Compare tools that retain assumptions, alternatives and reviewed consequences.

Treat AI, macros, synthesis and other automation as participants that can propose,
explain and carry out bounded work. Evaluate whether a person can detect wrong
advice, ask a useful question, revise the goal and stop or recover. Fluent output
and a high acceptance rate do not establish justified reliance. Separate model
inference, checked meaning, authority and observed external outcomes.

### Time, physical action and operating cost belong in the model

Interactive and physical systems expose deadlines, feedback, noisy observations,
resource ownership and actions that cannot be undone. A musical timeline, a
remote job and a device controller need different timing and failure contracts.
Record what can be replayed, what was only simulated and what already happened.
An undo of source cannot reverse an emitted sound, sent message or physical act.

Hardware, runtime and packaging choices should follow these pressures. Evaluate
responsiveness, throughput, precision, bounded work, data movement and retained
evidence alongside readability. “Fast” needs a workload and measurement; a
friendly abstraction should reveal relevant costs when the task depends on them.

## Synthesize Through Meaning And Boundaries

The useful connection between PL and HCI is a person working with a model whose
meaning, consequences and limits remain recoverable. Functions, types, algebraic
data, constraints, effects, resources, relations and incremental computation are
mechanisms to investigate for that purpose. They are not independent trophies.
The [generic-operation research](../research/generic_operations.md) shows how
small capabilities enable different compositions; the
[domain synthesis](../research/domain_composition.md) preserves their distinct laws.

Compare mechanisms at the boundaries where people otherwise reconstruct meaning:

| Boundary | Facts the composition must retain or explicitly change |
| --- | --- |
| Values and models | Units, identity, schema, uncertainty and omitted assumptions; equal displays need not denote equal concepts. |
| Computations | Evaluation/demand, order, cardinality, failure, time and cost; the same verb does not imply the same schedule or algebra. |
| Representations | What an edit changes, its coordinate/model basis, incomplete states and what cannot round trip. |
| Actions | Current authority, ownership, proposed versus committed state and observed external outcome. |
| Evidence | Which source, model, run or observation supports a claim, under which assumptions and coverage. |
| Growth | Which public meaning remains stable, which verification becomes invalid and which change requires migration. |

A shared envelope may help inspection without making every payload have the same
meaning. A richer type may expose a useful law while increasing entry cost.
A diagram may reveal structure while hiding action order. Evaluate these joins
in one whole activity; place each mechanism where it best supports that activity.
This is a synthesis method, not acceptance of a universal object, evaluator or IR.

## Pressure Programs That Can Change The Direction

Use the existing targets where they fit, but allow new programs to challenge the
map. These are exploration prompts, not APIs, release promises or additional gates.

| Whole activity | Cross-cutting pressure | A question that could overturn an assumption |
| --- | --- | --- |
| Calculate, repair and share an invoice | Tables, formulas, types, invalid drafts, reuse, review and export | Is source-first authoring still easiest after changing a computed value, sorting rows and handing the model to a colleague? |
| Build an explained scientific report | Data provenance, units, uncertainty, queries, plots, reproducibility and publication | Can a reader distinguish a measurement, assumption and derived conclusion without reconstructing the whole pipeline? |
| Create an interactive animation or musical piece | Concrete exploration, partial programs, temporal structure, latency and live feedback | Does explicit call-by-call code expose the useful structure, or does a temporal/domain representation deserve a different place? |
| Negotiate a shared allocation or schedule | Relations, constraints, conflicting preferences, multiple solutions and collaborative revision | Does a valid solution hide the policy choice, and can people explore alternatives without treating a solver as an oracle? |
| Delegate a multi-step workflow | Ambiguous goals, proposals, capability limits, external actions, interruption and unknown outcomes | Can a person recover the actual state and revise the plan after partial execution without trusting an agent's narrative? |
| Simulate, inspect and operate a feedback system | Units, observations, state, time, bounded control and physical effects | Which guarantees survive moving from simulation to the real host, and how does the interface show the remaining uncertainty? |

The [creative timing challenger](../research/interfaces/music_timing.md#creative-authoring-challenger--october-10)
develops one prompt into fixed beat/time facts and creation, ambiguous-goal,
unfinished-duration, stale-edit, handoff and playback questions. Its
[finite model experiment](../research/interfaces/music_timing.md#bounded-model-experiment)
executes selected schedule, draft and revision cases; authoring views and human
comparisons remain prepared. No Nomi implementation or device outcome is claimed.
The [explained-report challenger](../research/interfaces/structured_documents.md#explained-report-challenger)
separates measurement, missingness, calibration assumptions and derived summaries
under supplied facts. Together they test temporal creation and evidence-rich
interpretation beyond the existing runnable report.

A program is valuable here when it exposes a missing concept, a costly translation
between representations or a credible alternative. It does not need to fit an
old milestone before it can influence the design. Conversely, a compelling
demonstration does not make its mechanism suitable for every other program.

## Where Nomi Stands, 2026-10-10

Nomi is a research-rich language-design laboratory with runnable compatibility
prototypes. It has a broad selected evidence corpus, a substantial target and
useful local CLI/browser/notebook journeys. It has not yet demonstrated the
coherent computational medium described above.

| Area | Current evidence | Gap to this vision |
| --- | --- | --- |
| Language meaning | Written target contracts; bounded accepted pattern design; source analysis and several runtime paths | Much of the intended scalar/data/failure/call/module system cannot yet run together. Prototype parity is not target conformance. |
| Human reasoning | Cognitive/interaction research, prepared counterexamples and finite probes | No recorded human study establishes learning, comprehension, repair, handoff or accessibility benefits. |
| Representations and creation | Source editing, notebooks, output/diagnostic views, draft retention | Comparable authoring alternatives, typed partial work and transitions from concrete examples to reusable models remain unvalidated. |
| Evidence and explanation | Structured runtime diagnostics, capability/support records and checked subsets | No integrated user path connects intent, assumptions, source meaning, dependencies, observations and change consequences. |
| Composition and growth | A bounded JSON report and local calculations; finite timing/revision models; target/domain pressure programs | Checked local reuse and the broader domain/time/collaboration combinations are still design or experiment work. |
| Automation and agency | Agent/retrieval tooling; proposal, authority and reliance contracts | Development tooling does not demonstrate a user-facing delegation system or calibrated reliance. |
| Operation and distribution | Local tests, browser/kernel receipts and build/freshness checks | Clean supported-host installs, current public artifact, performance envelopes and long-lived recovery have incomplete evidence. |

Test counts describe exercised prototypes. Corpus size describes selected
coverage. Neither supplies a percentage of progress toward this vision. The
[delivery receipts](../orientation/project_roadmap.md#user-facing-readiness-audit)
preserve exact support; the [design agenda](redesign_agenda.md) preserves open
questions. This assessment does not promote any packet or claim a new trial.

## Close The Gap Without Closing Exploration

Run two connected loops. A discovery loop observes real activity, studies a
potentially useful idea, compares representations and prototypes unfamiliar
possibilities. A delivery loop chooses a promise, closes its contracts and makes
it usable through actual tools. Discovery can change that promise or replace a
mechanism; delivery supplies the real artifacts with which to test the ideas.

Open-ended observation, historical synthesis and speculative prototypes are
legitimate before a precise discriminator exists. Record their questions and
limits. Narrow experiments need explicit comparisons and outcomes; promotion
into the language needs stronger evidence than a research lead. Existing packets
are continuity tools, not a requirement that all discovery fit their old taxonomy.

The immediate opportunity is to develop a growing model through both loops:
make the intended calculation/report semantics and checked reuse real, while
comparing how people create, inspect, repair and share the same model. Keep the
semantic tasks equal when comparing representations, and label supplied facts
until actual analysis produces them. Do not postpone all human learning until
the compiler is complete or substitute a tabletop trial for implemented meaning.

In parallel, select a contrasting creative, collaborative or temporal activity
that may reveal what the small report misses. Its findings can revise the target,
research questions and schedule. The milestone structure must follow the design
that survives these comparisons; it cannot define the ambition in advance.

For each increment, retain the pressure, alternatives, mechanism, interaction
cost, independent expectations, observed outcome and next uncertainty. Say what
changed and what did not become established. A useful first release is an
instrument for this continuing synthesis, not the final definition of Nomi.

## What Can Stabilize In A Refinement Pass

Stabilize a scoped proposal by making its purpose, alternatives, meaning,
evidence and unresolved choices consistent. The
[hypothesis comparisons](redesign_agenda.md#comparison-and-falsification)
name ways the current candidates can fail. A stable description keeps a credible
fork open when evidence cannot decide it.

Different comparisons need different controls:

- **Models:** compare different rules and assumptions explicitly. Identical initial
  output does not make beat-anchored and time-anchored models equivalent.
- **Representations:** hold the selected model and semantic task facts constant;
  compare expression, prediction, repair, change and handoff costs.
- **Automation:** disclose the same available evidence; preserve ambiguity and
  measure detection/repair of wrong advice, not acceptance alone.
- **Execution profiles:** pin declared rules and capacities; compare values,
  events, failures and refusals on the supported overlap.

Review until the same question receives the same scoped answer through the vision,
target, research, guide and operational instructions; remaining choices have a
real next discriminator; and counterexamples no longer require an unrecorded
exception. Remove duplicate wording and machinery that add no distinct help.
Stop adding claims when the missing evidence requires execution or observations
that this pass has not produced. Record that frontier instead of declaring the
whole language stabilized or manufacturing a winner.
