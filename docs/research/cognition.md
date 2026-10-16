# Computation As A Cognitive Instrument

> Status: foundational research and Nomi hypotheses; no new syntax admitted.

Read this before the [interface threads](interfaces/README.md), then the
[interaction proposal](../design/interaction_model.md) and
[redesign agenda](../design/redesign_agenda.md). Sources were consulted on
2026-09-29/30 and extended with selected primary readings on 2026-10-02 and
2026-10-10.
Historical interpretation, Nomi inference, and untested claims
are distinguished below. This is not a claim to exhaust either philosophy or HCI.

Easier thinking is the shared purpose across domains. The [scientific-model synthesis](scientific_models.md)
adds primary mechanisms for referable models, premises, evidence and alternative
representations; [SP0](../design/scientific_discovery.md#design-from-thinking-activities)
prepares prediction, diagnosis, revision and handoff tasks. These are design
inferences and unperformed human comparisons, not a theory that formal semantics
captures all cognition or a claim that Nomi already improves it.

The [natural-language continuation](interfaces/natural_language.md) supplies
selected linguistic, pragmatic and code-comprehension evidence for naming,
roles, scope, dialogue repair and multilingual access. It translates these into
NL1-NL6 under the existing interaction packet; prepared stimuli are not human
results or a claim that fluent prose makes a computation correct.

The [general knowledge-framework synthesis](knowledge_frameworks.md) continues
this history from Leibniz into logic, defaults and revision, modular theories,
knowledge exchange, uncertainty and learned methods. It separates representation,
inference, realization and human augmentation, with source-depth labels and a
bounded handoff to the existing foundation and interaction owners.

## Start Before Programming Languages

The design object is a person making an idea sufficiently precise to inspect,
communicate, test, revise, and sometimes execute. Source code is one powerful
representation of that activity, not its entire definition.

Begin with a mundane problem: calculate an invoice. Before choosing keywords,
identify quantities, identities, dependencies, alternatives, acceptable states,
changes, authority, and evidence. A handwritten table, spreadsheet, equation,
function, and dialogue can all express parts of this problem. Each makes some
relationships apparent and leaves others implicit.

The question is not which interface is universally best. It is which facts a
representation lets this person reason about without reconstructing hidden
machinery. A notation that calculates correctly can still invite incorrect
interpretation. A beautiful diagram can be ambiguous about execution order.

## Primary Foundations And Their Limits

### Leibniz: Representation For Discovery And Judgement

In his 19 December 1678 letter to Gallois, Leibniz describes a characteristic
whose signs support discovering and judging relationships, not just recording
them. The reference is Lloyd Strickland's translation of that specific letter,
not an assertion that a universal calculus was achieved.
[Primary translated letter](https://www.leibniz-translations.com/gallois).

**Nomi inference:** a language should help find a missing case, expose a
dependency, and compare alternatives, not merely encode an already finished
algorithm. Candidate tooling: examples beside definitions, missing-pattern
witnesses, semantic diffs, and inspectable normal forms. **Limit:** naming a
concept does not settle its meaning; disagreement about models survives formal
notation. Do not market the compiler as an oracle of intent or truth.

His 1684 *Meditations on Knowledge, Truth and Ideas* distinguishes recognition
from an articulated analysis, discusses symbolic thinking, and cautions that
apparently understood definitions can conceal contradiction. The linked
Jonathan Bennett version modernizes and interpolates the text; it is not a
diplomatic translation and is used for bounded interpretation, not quotation.
[Adapted primary text](https://www.earlymoderntexts.com/assets/pdfs/leibniz1684.pdf).

**Actionable distinction:** familiarity with the name `Invoice` is not evidence
that its constraints are satisfiable or that it represents the intended invoice.
A type/decoder explanation should expose domain, construction rules, and omitted
assumptions. A contradiction witness and a missing external observation require
different repairs. A nominal declaration can name an impossible concept; parsing
it does not establish a valid inhabitant.

**Candidate experiment:** compare a label-only hover with a bounded contract
view on empty invoices, conflicting ranges, and duplicate identities. Ask people
to predict valid construction, not merely recall a name. A useful abstraction
lets them defer internal details and retrieve those details when an edge arises;
requiring every expansion at all times would defeat symbolic compression.

### Boole: Operations With Laws, Not Decorative Symbols

Boole's 1854 *Laws of Thought*, especially chapters II-VI, develops symbolic
operations and their interpretation in logical reasoning. The book also treats
probability; it should not be reduced to a slogan that all thought is binary.
[Primary book](https://www.gutenberg.org/files/15114/15114-pdf.pdf).

**Nomi inference:** give an operation a domain, meaning, and laws before giving
it punctuation. Commutativity of pure conjunction is not permission to reorder
effectful short-circuit evaluation. Unknown evidence, absence, failed decoding,
and false are different states. Exhaustiveness is a statement about a declared
closed domain, not about every event the real world can produce.

Chapter III makes the universe of discourse part of interpretation; chapters
V-VI distinguish formal manipulation from interpretation. Boole's historical
calculus is not simply today's programming Bool/operators, and his empirical
claims about mind are not adopted as a modern cognitive theory.

**Actionable distinction:** set complement needs a universe. "Not in the query
result" can mean excluded, not indexed, inaccessible, or not yet observed. An
operation should carry its actual domain and evidence status; absence must not
silently become false. The idempotence of class selection does not make a
duplicate-bearing list, effectful predicate, or remote action idempotent.

**Candidate experiment:** compare the same predicate on two declared universes,
then reorder predicates that produce an external observation. Check both result
and invocation trace. Keep core `Bool` ordinary; explicit uncertainty and
conflicting evidence can be library data with domain-specific combination rules.
Nothing here proposes a universal many-valued core logic.

### Dijkstra: Structure That Supports Reasoning

EWD249 connects useful program structure with enumeration, induction, and
abstraction as aids to understanding. The text is *Notes on Structured
Programming*, with a 1970 second-edition transcription of the 1969 work.
[Primary notes](https://www.cs.utexas.edu/~EWD/transcriptions/EWD02xx/EWD249/EWD249.html).

**Nomi inference:** make a loop's invariant and progress argument discussable;
make a scope's exits enumerable; let a function contract hide implementation
without hiding authority or failure. Tests are evidence for examples, not a
universal proof. Fewer lines do not necessarily mean fewer facts to remember.
**Limit:** this does not demand a proof assistant for a greeting script.

EWD418 adds predicate transformers and guarded alternatives. Its `wp(S, R)`
includes proper termination; arbitrary eligible guarded branches must all meet
the required postcondition. Its alternatives are unordered, unlike Nomi's
accepted first-success, source-ordered `match`.
[Guarded commands and derivation](https://www.cs.utexas.edu/~EWD/transcriptions/EWD04xx/EWD418.html).

**Actionable distinction:** an invariant says what remains true; a progress
argument says why an activity finishes. A cancel request does not prove that
children joined or cleanup completed. One successful interleaving does not
establish correctness for every admissible event order. Record the allowed
orders, transition preconditions, and completion obligation before making the
toolbar say "Stopped".

**Candidate experiment:** enumerate a small transition model, retaining a
counterexample for each unsafe order. Compare "some path reaches the result"
with "all admitted paths preserve the requirement." Treat fairness as a
separate scheduler assumption: nondeterministic choice alone promises no fair
selection. A bounded model result must state its bound and excluded host events.
Do not import guarded-command punctuation or reorder ordinary match arms.

### Iverson: Notation That Reveals Relationships

Iverson's 1980 Turing lecture evaluates notation as a tool of thought, including
its support for expression, suggestion, and proof.
[Primary lecture](https://www.jsoftware.com/papers/tot1.htm).

**Nomi inference:** compare map/fold and shape-aware array operations with loops
on the same problem. Keep axes, dimensions, identities, and empty cases visible.
**Limit:** compact glyphs may transfer effort from typing to recognition; a
domain expert's fluency is not a beginner's starting point. Dense notation
remains a scoped candidate, not an ordinary-module requirement.

### Engelbart And Sutherland: The Environment Participates

Engelbart's 1962 report considers human capability together with tools,
language, and methods. Sutherland's Sketchpad thesis demonstrates interactive
graphical construction rather than only textual instruction.
[Engelbart report](https://dougengelbart.org/content/view/138/000/),
[Sketchpad thesis](https://www.cl.cam.ac.uk/techreports/UCAM-CL-TR-574.html).

**Nomi inference:** editor feedback, projection, revision, and inspection can be
part of the language experience without becoming grammar. A drag should become
an explicit candidate change, not an invisible second semantics. **Limit:** an
interactive demonstration is not evidence that visual representation scales
better, is accessible, or yields correct programs in every domain.

### Abstraction, Cognitive Tradeoffs, And Causality

SICP provides a primary treatment of procedural/data abstraction and constructing
languages. Green and Blackwell's 1998 tutorial gives a vocabulary for tradeoffs
such as hidden dependencies, viscosity, and premature commitment. Lamport's
1978 paper distinguishes causal event order from simply reading wall-clock
timestamps.
[SICP](https://web.mit.edu/6.001/6.037/sicp.pdf),
[Cognitive Dimensions](https://www.cl.cam.ac.uk/~afb21/CognitiveDimensions/CDtutorial.pdf),
[Time, Clocks, And Ordering](https://lamport.azurewebsites.net/pubs/time-clocks.pdf).

**Nomi inference:** abstraction needs inspection and a tolerable entry cost;
editing needs room for incomplete ideas; task explanations need causal links,
not an apparently authoritative total order. These references motivate questions,
not one combined theory that proves Nomi's proposed design.

## Creation And Understanding

The [guiding vision](../design/vision.md) brings these foundations into the
whole-system design. The added construction and understanding evidence below
also challenges an implementation-only notion of progress.

### Resnick And Silverman: Creation Has Many Starting Points

Their 2005 paper reflects on construction kits that support designing meaningful
artifacts. It distinguishes ease of starting from diversity of possible projects
and describes different paths through making. Its examples and principles arise
from work with children; they do not establish which Nomi representation works
for professional teams.
[Primary paper](https://dam-prod.media.mit.edu/x/files/papers/IDC-2005.pdf).

**Nomi inference:** supplied examples should be starting material for independent
creation. Compare whether people can change the model, make an artifact of their
own and recognize a reusable idea. An invoice-only progression cannot test the
range of creative activity. A contrasting animation, music or simulation task
can expose missing temporal, representational or learning concepts. Keep the
scope and comparison explicit; diversity of artifacts alone does not establish
correctness or sustained learning.

### Victor: Explain The Computation In Its Working Context

Victor's 2012 design essay proposes environments that expose vocabulary, flow
and state and let learners develop programs through feedback and abstraction.
Its illustrated designs supply mechanisms and critique, not a controlled study
that demonstrates a universally superior programming system.
[Author's essay](https://worrydream.com/LearnableProgramming/).

**Nomi inference:** a final value beside source may leave a person reconstructing
the relevant computation. Compare explanations connected to actual inputs,
dependencies and meaningful time intervals. Use an initially correct program,
a wrong expectation, an incomplete model and a changed requirement. Measure
prediction and repair separately from visual appeal. Recorded execution can
support inspection; scrubbing a trace must not replay effects. The computational
model may itself need revision if an interface merely exposes its confusion.

## Further Philosophical Lenses

These authors do not form one school, and their disagreements should remain
visible. Computation, logic, human activity, and communication answer different
questions. The design consequences below are original Nomi proposals, not
historical endorsements or evidence of cognitive effectiveness.

### Peirce: A Difference Must Make A Difference In Practice

Peirce's 1878 *How to Make Our Ideas Clear* connects conceptual clarification
with conceivable practical effects, rather than familiarity with a word alone.
[Primary essay](https://www.peirce.org/writings/p119.html).

**Nomi inference:** make two semantic candidates distinguishable through a
program or interaction. "Safe Stop" is not a useful label until a trace shows
whether it requests cancellation, waits for cleanup, or reports uncertainty.
"Same program" needs an equivalence criterion: value, failure, effects, timing,
and provenance may differ despite identical output text.

**Implementation action:** a fixture should name input/context, allowed events,
observable outcome, and a counterexample to a competing rule. A property can be
tested under fake capabilities without sending real requests. **Limit:** finite
observations are not a universal equivalence proof; deciding that two meanings
are indistinguishable requires stating which observations were admitted.

### Hoare: State Assumptions And The Claim They Support

Hoare's 1969 paper presents axioms and inference rules for reasoning about
program properties. Its abstract was checked through the publisher-linked
record; the full historical proof was not independently reconstructed here.
[Primary paper](https://dl.acm.org/doi/10.1145/363235.363259).
The partial/total correctness distinction here uses Dijkstra's explicit
comparison in EWD418, not an attribution of termination to every Hoare triple.

**Nomi inference:** a command can have a precondition, postcondition, and allowed
failure without making users learn theorem-prover notation. Applying an edit
requires the same model incarnation/revision and a valid target; success creates
one new valid model. Rejection must leave the committed model untouched.

**Implementation action:** stage candidate data, check against current state,
then publish atomically; record the precondition that failed. Test deliberately
invalid and stale requests and verify no partial change. **Limit:** validating
today's input does not prove the business model is right, and checking a function
result does not prove it terminates or is free of external effects.

**Concurrency gap:** this sequential obligation needs an explicit operation
boundary when state is shared. Herlihy and Wing's 1990 treatment of concurrent
histories makes that distinction precise; it is a separate primary source,
not a property attributed to Hoare's abstract.
[Primary concurrent-object paper](https://www.cs.cmu.edu/~wing/publications/HerlihyWing90.pdf).
P19 compares six prepare/publish orders under supplied rules. A valid immutable
candidate can race with another candidate; an owner must enforce freshness at
publication. The model proves no real implementation linearizable and promises
no remote atomicity or fairness.

### Turing: Mechanical Procedures Have A Boundary

Turing's 1936 work defines a machine model and establishes limits on general
mechanical decision procedures. This reading concerns its computability and
decision-problem argument; it does not claim that the paper states every modern
formulation of the halting problem verbatim.
[Primary paper](https://theory.stanford.edu/~trevisan/cs172-07/turing36.pdf).

**Nomi inference:** unrestricted programs cannot inherit a blanket promise of
termination, intent inference, complete inversion, or semantic equivalence
checking. A useful checker narrows a fragment and names its assumptions. A
budgeted tool must distinguish complete rejection from unfinished analysis.

**Implementation action:** artifact/evidence records carry analysis scope and
completion status. Unknown or unsupported is a useful honest result, with a
witness or partial trace where available. **Limit:** undecidability is not a
reason to abandon static checks; finite/decidable fragments and explicit
contracts can still offer strong guarantees.

### Shannon: Transport Fidelity Is Not Semantic Fidelity

Shannon's 1948 paper separates the engineering problem of selecting/transmitting
messages from their semantic interpretation.
[Primary paper, introduction](https://home.csulb.edu/~cwallis/382/readings/482/shannon.mathematical.theory.communication.1948.pdf).

**Nomi inference:** a byte-perfect transfer, valid JSON payload, or converged
document can faithfully transmit the wrong model. Entropy or character count is
not a measure of human understanding. A compact representation may require more
reconstruction, and a lossless codec may preserve ambiguous intent perfectly.

**Implementation action:** separate transport/encoding checks, source/identity
checks, type/decode checks, and domain acceptance. Retain provenance across each
boundary. **Limit:** source compression and communication statistics do not
select a language notation or establish usability.

### Simon: Reasoning Has An Attention Budget

Simon's 1955 model replaces an ideal of globally informed calculation with
simplified choice procedures, satisfactory alternatives, and changing aspiration
levels. This is a model of rational choice, not a ready-made editor experiment.
[Primary paper](https://cooperative-individualism.org/simon-herbert_a-behavioral-model-of-rational-choice-1955-feb.pdf),
[author archive record](https://digitalcollections.library.cmu.edu/node/48694).

**Nomi inference:** expose the next decision a person actually needs to make.
One undifferentiated wall of types, effects, traces, and solver facts can reduce
practical control even if every item is accurate. Progressive disclosure must
preserve access to assumptions and critical failures, not hide them to appear
simple. A feasible answer should not be advertised as optimal.

**Implementation action:** compare bounded summaries plus retrievable detail
with a full dump on creation, review, interruption, and repair tasks. Measure
wrong conclusions and recovery cost, not only task speed. **Limit:** no fixed
"human capacity" constant or universal novice/expert threshold is inferred.

### Suchman: Plans Participate In Work; They Do Not Exhaust It

Suchman's situated-action account treats plans as resources within ongoing
practical activity, rather than complete prescriptions for every contingency.
The consulted source is the author's chapter summary in the second edition;
the 1985 Xerox report could not be fetched and is not counted as checked evidence.
[Author chapter](https://www.cambridge.org/core/books/abs/humanmachine-reconfigurations/situated-actions/F4AA82303887FF0875BD656977661875).

**Nomi inference:** a workflow or agent proposal needs revision and repair when
the situation changes. Preserve completed work, uncertain outcomes, changed
assumptions, and the remaining proposal. Do not infer human intent solely from
button presses or claim a plan's validity proves its continued appropriateness.

**Implementation action:** run an interrupted invoice/import task, change a
requirement midway, and ask the user to reconcile it. Provide explicit command
targets and a reviewable change, with contextual explanation. **Limit:** this
does not reject plans, typed APIs, or useful automation; it challenges the claim
that their formal completeness also captures the person's practical situation.

## Philosophy To Observable Obligations

The philosophical gap includes ontology (what counts as an object), epistemology
(what is known and how), logic (which inferences are justified), action (what
can be changed), and values (whose purposes count). The following tensions are
design work, not a universal philosophy of computation.

Intension means a defining description or rule here; extension means the
members/results it determines. Human intention is the purpose for choosing
that description. A query plan, its rows, and the reason someone asked the
query are three different objects of discussion.

| Tension | Concrete question | Candidate implementation obligation | Counterpressure |
| --- | --- | --- | --- |
| Identity versus appearance | Is this the same line after sort, rename, or reset? | Domain/binding/incarnation identity separate from labels and offsets | Too many identifiers can become another hidden system to debug. |
| Definition versus inhabitance | Does a declared concept admit any valid value? | Expose constraints and contradiction/witness evidence within a declared fragment | General satisfiability is not promised. |
| Truth versus evidence | Does no result mean false, unknown, denied, or incomplete? | Preserve typed evidence status and searched domain | A universal evidence lattice would impose inappropriate domain laws. |
| Law versus execution | Does a rewrite preserve calls, failure, and numeric behavior? | Name purity, order, numeric, and termination side conditions | Refusing every rewrite would sacrifice useful optimization. |
| Intension versus extension | Is this a recipe, all its results, or one observation? | Distinct plan/collection/stream/result epochs | Users still need a coherent vocabulary across those values. |
| Prediction versus intervention | Does opening an explanation change the world? | Passive captured evidence and explicit effectful inspection adapters | Capture and retention themselves have cost and privacy implications. |
| Possibility versus authority | Can a valid plan actually run here now? | Profile eligibility plus current concrete capability enforcement | Detailed grants must remain understandable. |
| Reversal versus responsibility | Which consequences remain after undo or Stop? | Local reversal, compensation, and uncertain outcomes remain distinct | Recovery can require domain judgment no tool can settle. |
| Formal correctness versus purpose | Who chose the domain, objective, exclusions, and acceptable errors? | Preserve assumptions/provenance and let users revise the model | Metadata does not resolve moral or organizational disagreement. |

The normative Nomi recommendation is to preserve a person's ability to inspect,
contest, and revise a model. It is our design judgment, not a theorem derived
from Leibniz or a requirement to ask permission for every reversible edit.
In a multi-person tool, authorship, review, and execution authority can belong
to different people; command records should not erase that difference.

Review, comprehension, and authority are also distinct. If an application
requires exact action review, broad `publish` permission cannot silently reuse
endorsement after changing recipient, payload, or relevant model context.
P20 tests a supplied exact-match rule; it cannot establish the review's
authenticity or whether a person understood it. Explicit bounded automation is
a competing policy, not an exception requiring a new language keyword. The
[HX8 protocol](interfaces/composition_cases.md#hx8-minimal-study-protocol)
makes agency and repair observable study questions rather than inferred virtues.

## Actionable Translation Map

The [edge atlas](interfaces/edge_cases.md) and
[composition cases](interfaces/composition_cases.md) supply the pressures below.
The [experiment report](interfaces/experiments.md) distinguishes executed local
models from future Nomi integrations and human studies.

| Lens | Nomi artifact or behavior to investigate | Smallest falsifying case | Implementation destination |
| --- | --- | --- | --- |
| Leibniz | Inspectable definition, domain, normal form, and assumptions | H40/H52: schema omits a rule or proof uses changed assumptions | Typed Surface/decoder projection and tooling metadata, not new grammar |
| Boole | Domain-qualified laws and explicit evidence states | H25/H66: absent evidence or reordered effectful predicate | Library evidence values; optimizer side conditions; existing Bool contract |
| Dijkstra | Atomic transition, all exit paths, invariant plus progress | H29/H87: Stop requested but completion obligation unmet | Runtime/task events and command-state transition model |
| Hoare | Preconditions/postconditions and unchanged state on rejection | H14/H45/H70: stale, invalid, or different incarnation | Checked candidate-change transaction adapter |
| Peirce | Competing semantics with observable differences | C02/C05: same displayed output, different authority/outcome | Backend-neutral result/event fixtures |
| Turing | Qualified unknown/unsupported/bounded analysis | H24/H49/H94: budget, search, recovered source | Tool analysis and solver result records |
| Iverson | Notation that reveals dependency/shape without false laws | H67/H68: empty shape and Float reassociation | Collection/array contracts and inspectable lowering |
| Shannon | Separate transport, semantics, and intended model | H08/H44/H77: display codec or offset-unit confusion | Versioned serialization/source-map adapters |
| Engelbart | Tools, language, methods, and learning evaluated together | H93/H96: fast creation but poor review/repair | Shared command/inspection surfaces and task studies |
| Sutherland | Spatial relations with explicit constraints and inverse limits | H15/H81: ambiguous edit or changed frame | Read-only projection before bounded spatial edit adapter |
| Simon | Attention-aware summary without loss of critical facts | H74/H96: notification flood or hidden uncertainty | Bounded diagnostics/trace views and interrupted-task study |
| Suchman | Repair and renegotiation as situation changes | H62/H88: revised intent after partial execution | Proposal/history model with actual outcomes |
| Green/Blackwell | Cost of change, hidden dependencies, premature commitment | H22/H46: rename/delete repair requires unrelated edits | Resolved refactoring and competing representation study |
| Lamport | Causal relationships separate from arrival/wall-clock order | H33/H55: old result or simultaneous events | Epoch/event identity and declared ordering policy |

These are extraction points, not 14 modules to implement. The
[implementation map](interfaces/composition_cases.md#implementation-handoff)
names actual current files and missing contracts. None of these readings admits
a universal calculus, proof assistant, solver, or natural-language evaluator.

## A Cognitive Exercise, Before A Syntax Exercise

Work through each row using the invoice, a batch import, and a cancellation-heavy
job. Record the explicit Nomi long form, an alternative representation, the
fact gained, and the fact hidden. These are proposed exercises, not completed
user studies.

| Idea | Exercise | Consequence to investigate |
| --- | --- | --- |
| Identity versus location | Sort invoice rows without changing the selected item | Stable domain IDs; positions are view coordinates. |
| Meaning versus presentation | Rename a label without changing a binding | Symbol identity and lossless source matter more than rendered text. |
| Extension versus intension | Compare a list of results with a recipe for producing them | Distinct collection, stream, and plan types. |
| Truth versus evidence | Express unavailable, invalid, uncertain, and false inputs | Variant values, provenance, and explicit uncertainty; no truthiness. |
| Law versus evaluation | Swap two operands that read a clock | Algebraic rewrite requires purity and numeric side conditions. |
| Relation versus direction | Given quantity and total, solve for price | Inverting a function is not ordinary evaluation; specify solution space. |
| Invariant versus construction | Check valid dates, then find a feasible schedule | Predicate checking and bounded solver search are different APIs. |
| Time versus order | Replay two independently arriving responses | Epoch and causality metadata; reject stale commits. |
| Action versus observation | Reopen a result view after sending a request | Inspection must not repeat external effects. |
| Reversal versus compensation | Undo a text edit after a payment was sent | Source history cannot undo the world. |
| Abstraction versus concealment | Use a codec, then inspect its omitted constraints | Generated projections report what they cannot represent. |
| Possibility versus authority | Describe a process spawn in a browser | A plan expresses intent; a capability authorizes execution. |

## Candidate Laws For Nomi Tools

These are design obligations to test, not universal algebra or accepted APIs:

- **Observation:** rendering a completed value does not execute the program again.
- **Projection:** exporting and re-importing a supported view preserves resolved
  meaning; unsupported constructs remain readable and are not silently erased.
- **Identity:** rearranging a view does not retarget a command to another entity.
- **Atomic change:** validation either commits the entire proposed change or none.
- **Freshness:** a preview for revision A cannot silently authorize revision B.
- **Provenance:** an explanation can distinguish source, supplied input, inferred
  contract, host observation, and a suggestion from a person or agent.
- **Authority:** a transformation of source or data cannot manufacture permission.
- **Bounded explanation:** inspection has cost, retention, and redaction policies.

Round-trip equality should concern resolved meaning, not necessarily identical
whitespace. Comments and source layout need a separate lossless preservation
contract. Not every diagram has an inverse textual edit, and not every valid
program has a useful diagram. A read-only view is an honest outcome.

## Critical Counterpressure

A universal representation can become an abstraction tax. More metadata can
improve inspection while making compilation, privacy, and interoperability
harder. Static guarantees may exclude exploratory drafts; live feedback may
encourage unsafe reruns. A tiny core may merely relocate complexity into
unlearnable libraries. A powerful type system may explain less if diagnostics
expose inference machinery instead of the user's concept.

Therefore evaluate **concepts a person must track**, not keyword count alone.
Test novice creation, expert revision, teammate review, fault diagnosis, and
keyboard/screen-reader use separately. Do not average away a critical failure
because one interaction became faster.

## What This Changes Now

The design agenda should own representation, change, evidence, time, and
authority alongside values and functions. It should not invent a universal
symbol set or put natural language, spreadsheet coordinates, or gesture state
inside the base grammar. Start with one small shared computation and competing
views; permit that experiment to falsify the current text-first hypothesis.
