# Cognitive And Interface Design Review

> Status: dated research/design checkpoint; not a second live implementation backlog.

Packet: `docs/research/interfaces/README.md`,
`docs/design/interaction_model.md`,
`docs/design/interaction_model_target.nomi`.

## Scope And Findings

The user requested design before implementation, extending programming-language
research to any human interface with computation, grounded in Leibniz, Boole,
and Dijkstra rather than current syntax fashions. This pass adds foundational
cognitive exercises, 18 interface threads, an interaction proposal, three
invoice pressure programs, and a broader design-first agenda.

1. Representation is a design dimension missing from a purely syntax-led review.
   A table, diagram, or command should reveal relationships, not create hidden
   execution semantics. Text-primary versus structured-document primary remains
   a credible fork, not a closed debate.
2. Change and time need explicit identities: source revision, model revision,
   domain identity, run identity, and observation epoch cannot be substituted.
3. Checking a predicate, solving a relation, querying a snapshot, and searching
   incomplete evidence are different acts. One pipeline glyph cannot settle them.
4. Historical ideas motivate inspectability and laws, but do not prove usability.
   No user trial, target typechecking, accessibility certification, or interface
   implementation was performed by this research pass.
5. Generic/callback/effect contracts still block claims that the overall target
   is a complete design. Implementation should advance only a settled slice.

## Evidence Quality

Primary translated historical texts, primary papers, standards, and official
tool documentation support selected mechanisms. Each thread separates these
from original Nomi hypotheses. Neighboring interfaces in the coverage map were
not all independently reviewed; detailed MIDI, robotics, Petri-net/BPMN, and
general proof-assistant contracts remain beyond this pass. Failed manual fetches
were not used as evidence; the music thread uses Puckette's primary text instead.

Historical readings are deliberately bounded: Leibniz's Gallois letter, selected
Boole chapters, EWD249, Iverson's lecture, Engelbart's report, and Sketchpad.
This does not reconstruct a unified historical philosophy or assert an exhaustive
survey. Source editions/dialects matter, especially archived Observable docs.

## Documentation Audit

| Finding | Severity/scope | Resolution or live owner |
| --- | --- | --- |
| Root README still routes target design to the superseded fixture | Misleading first entry point | Route to target suite/overall. |
| Workflow names legacy target as the broad update destination | Agent routing drift | Name the active suite and preserve historical file only as predecessor. |
| Research overview says breadth is enough without acknowledging this requested expansion | Scope ambiguity | Link cognition/interfaces and retain bounded admission rules. |
| Research, dated review, registry and synthesis repeat next steps | Duplication risk | Agenda/synthesis own live order; registry routes; dated review records evidence. |
| Prototype feature lifecycle says implemented without target disposition | Conflates today's coverage with language acceptance | D0 checkpoint adds independent direction metadata; never disables runtime from it. |
| Generic/protocol/callback and scalar/codec contracts remain incomplete | High design risk | D1/D3 in live agenda; no UI/sample promotion yet. |
| Bidirectional view/source, draft recovery, run epochs and command identity underspecified | New industrial contract gaps | Interaction proposal and its ordered experiments. |
| No evidence from accessibility or comprehension trials | Product-design risk | D5 includes manual trials; automated browser tests are not sufficient. |

This is a targeted authority/dependency audit, not a claim to have eliminated
every duplicate paragraph or reviewed every implementation line. Repetition of
a contract summary across target/example/review is useful; competing definitions
and live backlogs are not. Do not delete the 44 requested language critiques or
13 feature comparisons merely because they discuss the same mechanisms from
different directions.

## Validation And Continuation

Live gates, deliverables and user outcomes are owned by
[the redesign agenda](../design/redesign_agenda.md),
[interaction experiments](../design/interaction_model.md), and
[existing synthesis](../design/synthesis.md). Packet status stays `designing`.

Validation: 63 focused resource/docs/packet tests passed; four registered packets
passed coherence checks; local links across 130 Markdown/target files resolved;
agent-doctor checks passed and the ignored local RAG index was rebuilt (1268
chunks). `git diff --check` passed. These checks do not validate the invoice
source or proposed laws.
Target sources remain outside `samples/`; no web manifest update is justified.
The next semantic design pass types map/fold, a derived decoder, and a resource
callback with their error/effect/region metadata before another syntax proposal.

## D0 Migration Checkpoint

The existing `SyntaxFeature` registry now carries an optional immutable
`TargetDirection` with direction, canonical contract, normal form and reason.
Across 32 prototype entries: 18 retire, seven rework, two retain, two open, and
three unreviewed. These count implementation contributions, not 32 independent
language features. Expression precedence, assert reduction and pass reduction
remain unreviewed; no missing metadata is interpreted as target acceptance.

`python3 -m tools.syntax.inspect --stage target-alignment` and the shared
`inspect(stage="target_alignment")` facade expose the same record-derived table.
No pipeline selector, capability axis, grammar, runtime semantics, or sample
changed. Tests compare all current grammar/lowering/desugar selections before
and after changing directions, including retired forms that still execute.
The migration is removable by deleting the optional field/inspection stage;
it introduces no new wire schema, engine, or language keyword.

Final broader validation: 484 targeted tests (including 28 new direction tests)
and 55 web/runtime contract tests passed; manifest and WASM freshness passed.
Five registered packets remained coherent and the ignored RAG index was rebuilt
with 1299 chunks. New test-file lint passed. Full-file
lint still reports the same 12 pre-existing diagnostics verified against HEAD
in features.py, runtime/api.py and tools/syntax/inspect.py; unrelated exception,
annotation and import cleanup is intentionally outside this change.
The full Python suite and a fresh Playwright browser run were not performed.

## Pass Retrospective

### Data And Cross-Disciplinary Extension

The requested continuation adds the linked
[data/workflow dossier](../research/data_workflows/README.md) and
[notation atlas](../research/notation_atlas.md), with six independent
[research pressure programs](../design/targets/research/README.md).
This remains the same cognitive-interface packet, not another target authority.

The new evidence changes the questions, not accepted syntax:

- Similar function-call shapes can construct an Airflow graph, run a Prefect
  task, build a dataframe expression, or train an estimator. Phase must be part
  of the public contract, not inferred from a chain or arrow.
- Set/Venn views need a universe; tensor notation binds indices; coordinate
  descriptions need a reference/version. These expose context that a short
  string or pretty graph can conceal.
- Graphs in chemistry, argumentation, directed dataflow and undirected relations
  have incompatible edge meanings. A shared renderer isn't a shared evaluator.
- Workflow partition, materialization and attempt identity differ. Cached work
  cannot cache authorization; an external-effect acknowledgment can be uncertain.
- Scientific preprocessing has learned state. Fit/transform/predict and training
  evidence deserve distinct models even when each uses ordinary call syntax.

The atlas maps 45 families with ten deeper cases. It explicitly marks mathematical
thought exercises and prior-thread references separately from checked evidence.
Primary papers support selected mechanisms, not replicated performance claims
or complete proof reviews. A failed GraphBLAS PDF fetch was not used; the
semiring discussion is an original finite-mathematics exercise. No Newick,
Petri-net, quantum-language or engineering-standard conformance was researched.

Syntax pressure programs use fictional lab APIs and remain unparsed/untyped.
No interpreter, grammar, sample, generated asset, extension or package behavior
changed. DW1-DW8 in [the synthesis](../research/data_workflows/nomi_candidates.md)
own local experiment order; D1 function contracts still precede an engine.

Follow-up validation: 17 focused documentation/matrix/packet checks passed;
full suite 1431 passed, 76 skipped; 55 web/runtime checks and manifest/WASM
freshness passed. The 12 broad-run warnings are the same three parametrization
deprecations repeated across four workers, recorded in the separate test review.
Five registered packets and agent configuration checks passed. No fresh browser
GUI run, foreign-system execution, accessibility trial or target conformance is
claimed. These results establish preserved supported surfaces, not research
correctness or usability.

### Human Computation Edge Extension, 2026-10-02

The requested continuation follows the latest DSL boundary/model research,
extending the existing packet rather than registering another authority. It
adds [96 edge cases in 24 families](../research/interfaces/edge_cases.md),
[twelve composition cases and HX1-HX8 comparisons](../research/interfaces/composition_cases.md),
and [18 executed local probes](../research/interfaces/experiments.md) with a
checked-in capture. The six additional families cover accessibility/attention,
multilingual/multimodal input, embodied/spatial models, physical supervision,
privacy/evidence, and learning/repair. All cases are original pressures and
explicitly bounded, not claimed bugs or exhaustive human coverage.

[Cognition](../research/cognition.md) now connects selected readings of Leibniz,
Boole, Dijkstra, Peirce, Hoare, Turing, Shannon, Simon, Suchman, and earlier
interface foundations to concrete artifact/command/library obligations. It
separates historical claims, original inference, normative design judgment,
and experiment. Leibniz's 1684 text is an adapted translation; Hoare's abstract
and Dijkstra's comparison support a limited reading, not a reconstructed proof.
Suchman's available author chapter summary was used; the 1985 report fetch
failed. No universal philosophy of computation or usability claim follows.

Observed counterexamples: numerical revisions can recur across model histories;
valid concurrent edits can yield an invalid merged range; equal displayed
values can conceal exact differences; value laws can change effect traces;
an invariant can hold without completion; and a lost acknowledgment can follow
a completed modeled action. Actual source/backend behavior is not inferred from
those supplied finite models.

The interaction proposal now exposes incarnation/context and incomplete-evidence
pressure. Its target-only invoice fixture carries an incarnation and rejects an
edit from another history even when revision numbers match; a second example
keeps the same line ID after row reordering. These remain unparsed/untyped target
examples. No supported interpreter, grammar, web asset, notebook, extension, or
sample changes. The real-file handoff identifies existing structures and missing
contracts, including the gap between worker termination and structured cleanup.

HX1-HX8 own this extension's candidate details under the existing interaction
experiment order and D0-D7 gates. No new core semantics or production public API
is accepted. Local captures test proposed small-model rules; human studies,
actual IME/accessibility trials, capability enforcement and remote/device
integration remain unperformed.

Validation for the October extension: 58 registered focused syntax/docs/matrix
tests passed; all five design packets were coherent; probe-script lint and
`git diff --check` passed. All 18 probes reproduced the captured JSON inputs,
results, limits, and host metadata. An additional audit checked 24 interface/
cognition/proposal documents, 134 local links and heading anchors, table widths,
96 unique ordered case IDs, 24 family sections, twelve composition IDs, eight
HX experiment IDs, and all probe-to-atlas references. The documentation inventory
tests include the three new Markdown files. The ignored local RAG index was
rebuilt. These checks do not typecheck the target, validate all external URLs,
or establish human comprehension. The full suite, web/browser conformance and
manual trials were not rerun for this research-only extension.

### Follow-Up Gap Review, 2026-10-02

After the expansion checkpoint, the requested review found three concrete
preparation gaps: one-off audits did not protect captures over time; immutable
snapshot validation did not specify shared-state publication; and review could
be mistaken for current execution authority. The extension now has
[maintained integrity tests](../../prototype/tests/unit/tools/test_interaction_research.py),
non-writing capture verification, and two more bounded models, P19/P20.

P19 enumerates six two-command prepare/publish orders. Four accept both
same-base candidates under unconditional publication; an imposed atomic guard
accepts exactly one in all six. P20 separately checks an imposed exact-review
scope and a current grant across six supplied records. Neither proves real
publication, authentic approval, comprehension, crash recovery, or revocation
timing. Herlihy/Wing and MITRE supply the operation-history/race distinction;
W3C evaluation guidance bounds accessibility study claims. Sources and limits
are linked from the research, not promoted as accepted language policy.

The target-only invoice now demonstrates two valid immutable successor
candidates from one snapshot, explicitly without publishing either. HX1 owns
the serialized-owner/guarded-publication choice and review-scope dependency.
The [HX8 protocol](../research/interfaces/composition_cases.md#hx8-minimal-study-protocol)
adds U01-U07 supplied answer facts, prediction/repair scoring, counterbalanced
conditions, fictional data, incident records, and reporting of blocked input
paths. It remains unperformed and cannot be scored as empirical validation.

The registered check now compares every capture field except historical host
version strings, displays original and current versions, and rejects changed
outcomes, execution flags, or use of Python `-O`. It never rewrites a capture.
The tests preserve ordered IDs, references, local links/anchors, and table shape.
No current runtime, parser, supported sample, or UI behavior changes.

Validation: 68 focused syntax/docs/research tests passed, including ten new
checks; all 20 probes verified against the capture; packet, target-direction,
lint, and whitespace checks passed. Real browser/human trials remain unperformed.

### Iterative Review Cycle, 2026-10-02

#### Pass 1: Semantic Counterexamples

The wider semantic scan reconciled history/clock pressure with binding, data,
task, and capability target contracts. P02/P19 assume a non-reused committed
history; P18 assumes comparable clocks. P21 now supplies undo/copy-fork cases
that defeat incarnation/counter equality while retaining an unchanged positive
control. P22 supplies five timestamp contexts: fresh, old, unrelated clock,
previous boot, and invalid future. Incomparable is not known stale.

Both are original finite models with explicit limits. The candidates are
new committed context or distinct branch identity, and same-clock freshness or
declared mapping with uncertainty. History identity generation, pure-result
repreparation, clock synchronization, and physical safety remain open; no new
runtime policy is accepted. HX1/HX7 retain ownership rather than adding a queue.

Validation: all 22 probe captures and 68 focused tests passed, along with
packet, lint, and whitespace checks. Integration and human evidence are not
inferred from the added model comparisons.

#### Pass 2: Evidence And Study Method

The method scan found a missing negative control: P11's modeled lost
acknowledgment demonstrated action despite unknown outcome, but could teach
that every unknown outcome implies action. P23 now supplies indistinguishable
visible records for lost delivery versus lost acknowledgment, with zero/one
hidden actions. Neither definite non-action nor definite completion follows.

The [U01-U07 fixture set](../research/interfaces/study_cases.json) gives exact
supplied prompts, inputs and answer facts, with facilitator-only worlds kept
outside participant-visible records. Partial/complete trace controls distinguish
execution completion from complete evidence. Eight new integrity tests check
arithmetic, identity, drafts, history, uncertainty, traces, transfer and routing.
They are not a renderer, human grader, usability result or conformance claim.

The protocol now records rubric disagreements, answer-key exposure, assigned
and attempted denominators, blocked-task causes, and assistance. W3C's method
guidance distinguishes accessibility investigation from unassisted timing;
those observations must not be pooled into a speed claim. Historical readings
remain qualified and normative design inferences remain explicitly ours.

Validation: 76 focused tests and all 23 captured probes passed; packet,
lint and whitespace checks passed. Actual participants, UI/assistive adapters,
authentic approval, transport and physical measurements remain unperformed.

#### Pass 3: Repository And Capture Integration

The integration scan ran the full suite and existing web/runtime checks, then
challenged the capture boundary. A focused failing test demonstrated that root
and nested duplicate JSON fields could be silently reduced to their last value,
even with a contradictory execution flag. The local checker now rejects all
repeated object fields through the structured parser's object-pairs hook.
RFC 8259 section 4 supplies interoperability context; this strict policy applies
to research evidence, not the unaccepted Nomi decoder design.

Thirteen new boundary/inventory checks cover duplicate fields, malformed
captures, exact boolean types, separate check/write modes, object reordering,
study-fixture uniqueness, explicit `human_execution: false`, and the primary
index's actual probe inventory. Current counts remain with the probe report and
interface index; secondary routes no longer copy a changing number. Historical
validation counts above remain dated evidence rather than current inventories.

Final validation: `pytest -n 4` passed 1,485 tests with 76 skipped and four
dependency deprecation warnings from Jupyter's path migration. The existing
`check_web_runtime.py` passed 55 contracts and manifest/WASM freshness checks;
the agent doctor passed. All 23 captures reproduced; packet, target-direction,
lint, link/anchor/table/reference and whitespace checks passed. RAG was rebuilt
after the edits. No supported runtime, grammar, UI or generated web asset changed.
Actual browser interaction, IME/assistive trials, human studies, authenticated
review, physical clocks/devices and real remote recovery remain unperformed.

### Text Interface Extension, 2026-10-03

The requested text-focused continuation extends the existing DSL/string dossier
and cognitive-interface packet rather than creating another authority. It adds
[a focused chapter](../research/dsls/text_as_interface.md), a
[target-only pressure program](../design/targets/research/text_boundaries.nomi),
and eight additional local host/model observations. The chapter compares text
producer/consumer names across Python, Rust, Go, ECMAScript, Swift, Java, .NET,
Elixir and PowerShell; layered interpretation in Ansible, GitHub Actions,
Kubernetes,
Helm, Terraform, Ninja and Make; and Unicode, localization, framing, security,
source maps, human editing and generated-text authority.

The PowerShell finding is narrower than an English grammar for commands: the
documented convention is an approved action verb plus a singular resource noun,
with parameters providing refinements. The transferable mechanism is a
discoverable semantic vocabulary. It does not justify a compiler restriction
on Nomi function names.

The local capture now has eighteen DSL/text boundary observations. New cases
distinguish Python display/debug/format channels, strict/repairing byte decode,
line-ending preservation, lossy numeric presentation, visible Unicode scalar
structure, an invisible bidirectional control, destination-specific encoders
and delimiter collision. No shell, terminal, template engine, cloud service or
Nomi runtime was executed. T1-T10 remain candidate comparisons, and no public
API or new string syntax is accepted.

Completion audit, 2026-10-04: corrected the pressure fixture's raw template
literal so Nomi interpolation cannot consume template bindings prematurely;
the supplied GitHub-like braces are escaped at the Nomi source boundary.
Capture checks compare outcomes while preserving historical host versions as
provenance. The discovery catalog keeps its original checked date: this focused
extension does not claim to refresh all 122 systems.

Validation before the completion audit: 153 tools tests and 95 focused
syntax/research checks passed, as did all five design packets, the interaction
capture, target-direction inspection, lint, local links and whitespace. RAG was
rebuilt and the agent doctor passed. These checks validate research integrity,
not execution/typechecking of fictional APIs or foreign-system conformance.

The 2026-10-04 [domain continuation](2026-09-29-language-synthesis.md#domain-composition-continuation-2026-10-04)
is owned by the registered language-coherence synthesis. Data/time, AI/ML and
documentary payloads share this packet's context/evidence/projection boundaries
without selecting a universal graph, ontology or editable IR. Its bridge owns
the new local capture and validation; this bridge does not duplicate that inventory.

### Evidence That Changed The Design

Spreadsheet reference changes, keyboard command contexts, draft form validity,
solver enumeration, and causal ordering expose different kinds of hidden state.
They motivate a shared identity/change/epoch model, not a larger grammar.
Leibniz/Boole/Dijkstra provide questions about representation, laws, and reasoning;
they are not authorities endorsing specific Nomi choices.

The October counterexamples add context beyond a counter: model incarnation,
authority state, observation epoch, source coordinate unit, and reference frame.
They also require evidence to distinguish an unchanged valid model from an
invalid draft, a stopped local task from an unknown remote action, and a bounded
explanation from a complete trace. The recommendation stays library/tool-first.

The follow-up makes publication history and review scope observable in P19/P20;
they cannot be inferred from a valid candidate or broad capability category.

### Workflow Friction

The historical target remains linked from some entrypoints, and current feature
coverage is easier to inspect than its accepted/rejected target direction.
Broad research also risks becoming another catalog without a discriminating
program. Using the same invoice across representations keeps the comparison
concrete while the overall import continues to expose industrial gaps.

This extension also exposed a recurring risk of treating every numbered case as
an implemented test. The atlas owns coverage, composition cases own discriminators,
and the capture owns only its stated finite observations. Source fetch failures
and abstract-only readings are retained as evidence limits rather than filled
with an unsupported historical synthesis.

One-off integrity checks also lacked a durable replay path. The new capture
checker retains historical versions while comparing outcomes; a differing host
version alone is not falsely reported as differing semantics.

### Durable Improvement

Correct active target routing, add one registered cognitive-interface packet,
and give the design-first agenda ownership of cross-cutting closure gates.
Use the existing feature registry for the bounded disposition migration rather
than introduce another parallel list of language features.

The October improvement is a reproducible local probe/capture with stable case
IDs, explicit execution flags, and one real-file handoff. Registry/index routes
point to it from the existing packet. This adds no new agent instructions,
universal metadata framework, or runtime registry; removal is confined to the
research extension and its target-only examples.

The follow-up adds ten maintained research-integrity tests and a non-writing
`--check` mode to the existing script, plus a concrete unperformed HX8 protocol.

The three additional review/fix passes bring the maintained research checks to
31, add paired study stimuli and publication/history/clock/evidence controls,
and remove duplicated live inventory counts from secondary navigation. These
are scoped data, checks, and clearer obligations rather than a universal engine.

### Next Pass

D0 inspection metadata is implemented without changing prototype execution.
Continue D1 using the [function packet](../design/function_contracts.md) and
its three type-spelling candidates; resolve callback/generic/effect contracts
using the specified functions;
only after that promote a settled semantic slice toward CLI/browser conformance.

For this extension, prepare HX1's proposal context/read-set contract or HX2's
bounded evidence envelope using the existing result/event structures. Resolve
the relevant D1-D3 obligations before production promotion, then replace one
probe's supplied facts with real adapters and retain its stale/invalid/denied
negative fixtures. C12 and HX3/HX8 need manual human/input trials; the local probe
count does not close them.

Carry P19's publication boundary and P20's review scope into HX1; use the
prepared U01-U07 protocol only after the compared views expose the same facts.

### Natural Language Continuation, 2026-10-04

**Evidence That Changed The Design:** the [linguistic dossier](../research/interfaces/natural_language.md)
separates lexical form/sense, grammatical role, domain role, resolved binding and
audience label. UD/WALS/FrameNet make English-only mappings unsafe assumptions;
Pane's study exposes several uses of Boolean words; grounding research motivates
repair rather than inferred intent. The code-comprehension study is a counterweight
to the premise that English-looking syntax automatically recruits sentence
comprehension or eases programming. None of these sources chooses Nomi syntax.

**Workflow Friction:** original vocabulary-paper and Grice PDF fetches failed;
the narrower vocabulary mechanism uses a primary Dumais interview, without
claiming unavailable quantitative results. Some pages returned author-hosted
paper copies or rolling references; dates, editions, populations and inference
limits remain explicit. A fluent stimulus can also conceal missing facts, so
meaning-preserving, ambiguity-control and discovery trials are separated.

**Durable Improvement:** NL1-NL6, twenty adversarial distinctions, three ordinary-call
target pressures and ten prepared study cases route through the same cognitive
packet. Maintained checks preserve supplied/hidden facts, Bool fixture oracles,
identity/localization boundaries and navigation. No NLP model, grammar, naming
linter, runtime API, new playground sample or existing test was changed.

The coherence review also removed Python-style `case` markers from the recent
messaging challenger and the new linguistic target. Both now follow the
accepted pattern contract's direct arms; a narrow maintained guard prevents
that drafting drift without modifying the parser or older research targets.

**Next Pass:** close D1-D3 for one actual command, then pilot NL2's equal-typed
role swap and NL4's changed referent under HX8. Ask for prediction, missing facts,
effects and repair; treat clarification as success. Run locale/assistive-input
trials on the same command identity separately from English phrase preference.
Do not grade comprehension using schema checks or hidden outcomes, and do not
promote controlled prose until its ordinary-call challenger genuinely fails.

**Verification:** 27 new linguistic/target checks passed; 75 combined
cognitive/docs/packet checks passed before the two final match-arm guards were
added, and all 64 linguistic/messaging checks then passed. The final full suite
passed 1,994 tests with 80 existing skips and ten worker-repeated Jupyter path
deprecation warnings. All five packets, target-direction inspection, the existing
23-probe interaction capture, Ruff and whitespace checks passed. Web manifest
freshness (123 runtime files, 11 samples) and WASM freshness (eight outputs)
passed without regeneration because no runtime module or runnable sample changed.
These checks do not typecheck the research targets, validate the example
translations or establish comprehension, accessibility or NLP performance.

## Research Gap Continuation, 2026-10-04

The user requested detailed documentation of the research audit's remaining
edges, without implementation. Existing C12/HX8 now owns
[repeated-advice reliance](../research/interfaces/composition_cases.md#c12-advisory-reliability-and-calibrated-reliance)
and [team handoff](../research/interfaces/composition_cases.md#c12-team-handoff-and-distributed-understanding).
[Contrastive diagnosis](../research/interfaces/query_search.md#contrastive-explanation-and-diagnosis)
extends C09/HX2/HX8; the
[linguistic dossier](../research/interfaces/natural_language.md#grounding-reliance-and-shared-understanding)
links those distinctions rather than duplicate their protocols. This adds no
new numbered thread, study fixture, participant, result or target rule.

**Evidence That Changed The Design:** selected primary automation research
distinguishes missed cues from following erroneous advice. Whyline supplies a
question-bound alternative to undirected traces, including false premises.
Distributed cognition supplies a framework-level lead for split knowledge, not
a verified handoff benefit. The added Nomi counterexamples separate task
correctness from justified reliance, authentic approval from completed checking,
and accurate branch evidence from sufficient repair. All remain hypotheses.

**Workflow Friction:** a full distributed-cognition PDF fetch failed; the limited
abstract/introduction extraction is explicitly retained. Historical simulation
and small debugging-study populations cannot settle contemporary programming
usability. New hypothetical sequence and dyad tasks also need reviewed answer
oracles; existing prepared fixtures are not silently claimed to cover them.

**Durable Improvement:** detailed alternatives, normal forms, inspection facts,
beginner/production/failure-heavy pressures, confounds and falsifiers now live
in the existing packet. The registry and question 17 route to them without
inventing new global experiment IDs, a universal understanding bit, a causal
engine or an automatic repair API. Existing probe captures and U01-U07/N01-N10
remain unchanged; no new test or runtime behavior is introduced.

**Next Pass:** select and pilot one matched comparison, with independently
reviewed supplied facts and explicit disclosure scope. Record initial prediction,
missing facts and repair separately from confidence/time. Treat dyads as linked
observations and prompting as an intervention. A tabletop study of supplied
facts and a later actual adapter/capture trial answer different questions;
neither can justify population-wide or longitudinal claims without its own design.

## Frontier Planning Continuation, 2026-10-09

### Evidence That Changed The Design

A representation comparison needs equal semantic inputs and equally demanding
failure tasks. A structured candidate cannot postpone source export/merge, and
a text candidate cannot silently replace unsupported source. Old closures across
notebook reruns expose a separate binding/session question that a checking policy
cannot decide.

### Workflow Friction

The implementation-led frontier plan risked postponing human/domain comparison
until every compiler gate closed. Conversely, supplied-fact demonstrations could
be mistaken for typed product evidence if their origin was not explicit.

### Durable Improvement

The [paired trial](../design/interaction_model.md#paired-representation-and-revision-trial)
reuses HX8 with fixed invoice stimuli, underdetermined/stale/unsupported/late-run
cases, keyboard/IME requirements and text-versus-structured costs. It includes
binding/re-execution alternatives and a table/document challenger without adding
another study inventory, renderer or source notation.

### Next Pass

Prepare comparable views under the existing HX8 protocol; supplied-fact trials
can precede source typing if labeled, while production promotion needs actual
contracts. Continue text-primary read-only as the reversible baseline and retain
the structured challenger. No study, accessibility verification, independent
review or measured representation winner was produced by this planning pass.
