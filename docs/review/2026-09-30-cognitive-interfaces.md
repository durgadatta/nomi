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

### Evidence That Changed The Design

Spreadsheet reference changes, keyboard command contexts, draft form validity,
solver enumeration, and causal ordering expose different kinds of hidden state.
They motivate a shared identity/change/epoch model, not a larger grammar.
Leibniz/Boole/Dijkstra provide questions about representation, laws, and reasoning;
they are not authorities endorsing specific Nomi choices.

### Workflow Friction

The historical target remains linked from some entrypoints, and current feature
coverage is easier to inspect than its accepted/rejected target direction.
Broad research also risks becoming another catalog without a discriminating
program. Using the same invoice across representations keeps the comparison
concrete while the overall import continues to expose industrial gaps.

### Durable Improvement

Correct active target routing, add one registered cognitive-interface packet,
and give the design-first agenda ownership of cross-cutting closure gates.
Use the existing feature registry for the bounded disposition migration rather
than introduce another parallel list of language features.

### Next Pass

D0 inspection metadata is implemented without changing prototype execution.
Continue D1 using the [function packet](../design/function_contracts.md) and
its three type-spelling candidates; resolve callback/generic/effect contracts
using the specified functions;
only after that promote a settled semantic slice toward CLI/browser conformance.
