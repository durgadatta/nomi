# Nomi Research

> Status: consolidated design evidence.
>
> This directory replaces the previous collection of overlapping surveys,
> deep dives, feature atlases, syntheses, and research plans. The source corpus
> remains recoverable in Git history at commit `08f2aad`; these documents retain
> the conclusions needed for current design work without preserving parallel
> authorities.

## Reading Order

The [guiding vision](../design/vision.md) defines the broader human-computer
ambition. This corpus is a selected evidence map, not a boundary around valid
research. New observations, disciplines and competing models can change its
taxonomy and the target. Discovery and feature admission have different gates.

1. [Language Families](families.md) - what major traditions contribute and
   what Nomi should not inherit.
2. [Design Convergences](convergences.md) - findings that recur across
   language, tooling, data, security, and pedagogy research.
3. [Language-Feature Matrix](language_feature_matrix.md),
   [Transpose](feature_language_matrix.md), [Syntax Matrix](syntax_matrix.md),
   and [Syntax Forms](syntax_forms.md) alongside
   [Language Reviews](languages/README.md), and [Feature Comparisons](features/README.md) -
   equivalent semantic views, literal source forms and alternative spellings,
   with primary sources, bounded scope, Nomi costs, and concrete experiments.
4. [Open Questions](open_questions.md) - genuine forks that still require
   experiments rather than more broad surveys.
5. [Resource Experiment](resource_lifetime.md) - executed symbolic comparison
   of cleanup carriers and supplied-fact escape policies; not runtime conformance.
6. [Cognitive Foundations](cognition.md) and
   [Human-Computer Languages](interfaces/README.md) - the requested expansion
   beyond conventional languages, with 18 bounded interface threads. The linked
   [edge atlas](interfaces/edge_cases.md) extends coverage to 96 cases across
   24 families; [composition experiments](interfaces/composition_cases.md)
   connect philosophical questions to actionable contracts and current files.
   [executed probes](interfaces/experiments.md) are original local models,
   not Nomi/browser conformance or user studies.
   [Natural-language structure](interfaces/natural_language.md) adds roles,
   naming, segmentation, scope, reference, modality, repair and NL1-NL6 with
   prepared study facts, not a natural-language execution mode.
7. [Redesign Frontiers](design_frontiers.md) - primary evidence for eight further
   design pressures, from typed incomplete programs to qualified guarantees.
8. [Data And Workflow Languages](data_workflows/README.md) and
   [Notation Beyond Programming](notation_atlas.md) - deeper literal forms and
   execution layers, plus mathematical, scientific and humanistic representations.
   Their synthesis owns DW1-DW8; no new core syntax is admitted.
   [Dependencies and time](data_workflows/dependencies_and_time.md) and
   [AI/ML](data_workflows/ai_ml.md) deepen that work with DT1-DT5 and ML1-ML6.
   [Domain composition](domain_composition.md) maps selected families into the
   existing layers and DC1-DC6; [local composition probes](data_workflows/composition_experiments.md)
   distinguish executed counterexamples from unperformed integrations.
   [Messaging and event architectures](data_workflows/messaging_and_events.md)
   add queue/pub-sub/log, actor, outbox/inbox, projection, saga and workflow
   compositions with MSG1-MSG6, 24 edges and ten finite countermodels.
9. [DSLs And Strings](dsls/README.md) - dedicated deep research on layered
   configuration, strings and orthogonal models: 122 representatives across
   50 families, 24 semantic models, twelve composition pairs and four extended
   fixtures. [Text as an interface](dsls/text_as_interface.md) adds naming,
   rendering, codecs, localization, tooling and T1-T10; eighteen boundary
   observations plus eight finite-model probes sharpen E1-E22. Depth and
   unperformed integrations are explicit; grammar extensions remain unaccepted.

The [language synthesis](../design/synthesis.md) links that evidence to category
targets, the revised overall program, and user-facing playground gates. The
44 language reviews and 13 matrix feature categories are deliberately indexed
evidence, not independent specifications or 44 new implementation backlogs.
The [generic-operation continuation](generic_operations.md) deepens
the function category with a property hierarchy, GA1-GA8 and bounded local
counterexamples rather than adding another matrix axis or paradigm requirement.

The decisions drawn from this evidence live in
[Target Design](../design/README.md), [Syntax](../design/syntax.md), and the
[Decision Ledger](../design/decisions.md). Research proposes; target design
decides.

## Research Gap Continuation

The research-only audit on 2026-10-04 identified sharper contracts inside
already covered topics, not eleven wholly missing fields. The ten reported
findings split into eleven units because concurrency includes both memory
visibility and database predicate consistency. Their detailed evidence stays
with these existing owners:

| Research unit | Counterexample or distinction | Detailed owner |
| --- | --- | --- |
| Polymorphic sharing | A delayed identity closure retains the previous argument; generalization must account for shared state. | [Functions](features/functions.md#polymorphic-sharing-and-generalization) |
| Memory publication | Owning a task or yielding execution does not establish visibility of its shared writes. | [Concurrency](features/concurrency.md#memory-visibility-and-publication) |
| Predicate consistency | Disjoint guarded row updates can both succeed while violating a cross-row invariant. | [Dependencies and time](data_workflows/dependencies_and_time.md#predicate-consistency-beyond-snapshots-and-row-guards) |
| Foreign callbacks | Re-entry, foreign threads, unwinding and in-flight deregistration need distinct contracts. | [Resources](features/resources.md#foreign-callbacks-and-re-entry) |
| Nominal identity | Equal names and fields across package versions need not denote the same owned type. | [Modules and tooling](features/modules_tooling.md#nominal-identity-across-package-instances) |
| Adaptive evaluation | Held-out feedback can influence selection even when training never reads the held-out rows. | [AI/ML](data_workflows/ai_ml.md#adaptive-evaluation-feedback-is-also-a-dependency) |
| Correlated uncertainty | Reusing one uncertain origin differs from using independent values with equal summaries. | [Notation](notation_atlas.md#correlated-uncertainty-shared-origin-is-part-of-the-model) |
| Learned influence removal | Deleting a source row is not the same operation as invalidating or removing its learned influence. | [AI/ML](data_workflows/ai_ml.md#data-erasure-and-learned-influence-are-different-operations) |
| Calibrated reliance | Repeated correct advice can conceal a rare misleading suggestion or omitted warning. | [C12/HX8](interfaces/composition_cases.md#c12-advisory-reliability-and-calibrated-reliance) |
| Team understanding | Authentic approvals can coexist with an unchecked obligation each reviewer assumes another owns. | [C12/HX8](interfaces/composition_cases.md#c12-team-handoff-and-distributed-understanding) |
| Contrastive diagnosis | A trace, an answer to why-not, and an authorized repair establish different facts. | [Query and search](interfaces/query_search.md#contrastive-explanation-and-diagnosis) |

Each substantive unit records bounded primary evidence, original counterexamples,
competing contracts, layer/normal-form/inspection implications, representative
programs and falsifying experiments. Existing questions, DT/ML/DW and C/HX owners
remain the routing system; this table is navigation, not another priority list.
No new experiment was executed, participant recruited, target rule accepted,
ABI guaranteed or runtime behavior changed. Existing local probe captures and
prepared study inventories retain their earlier scope.

## For Readers Learning Nomi

Research is supporting evidence, not a prerequisite for trying the language.
Start with the [user guide](../guide/README.md) for runnable programs and
[Current Support And Growth](../guide/status.md) for the distinction between
implemented behavior, target contracts, and open experiments. Use the indexes
here when a specific design question or domain interests you.

## Corpus Covered

The consolidated corpus compared:

- Python, Ruby, JavaScript/TypeScript, Tcl, Bash, PowerShell, and other
  everyday interface languages;
- ALGOL, Lisp/Scheme/Racket, ML/OCaml/F#, Haskell, Elm, Roc, and Gleam;
- Rust, Go, Zig, Swift, Kotlin, Scala, C#, Java, Dart, C, and C++;
- Erlang, Elixir, actor systems, structured concurrency, and async runtimes;
- SQL, LINQ, dataframe systems, array languages, R, MATLAB, Julia, and
  Mathematica;
- Pydantic, serde, Elm decoders, zod, CUE, Nickel, Dhall, Pkl, Terraform/HCL,
  JSON Schema, and OpenAPI;
- layered YAML systems including Kubernetes, GitHub Actions, Helm, Kustomize,
  Compose, GitLab CI, Azure Pipelines, Ansible and Argo; embedded query, policy,
  pattern, template, build, grammar and modeling DSLs;
- orthogonal rule/search/knowledge/proof systems, optimization, temporal/state/
  token/stream/signal models, probability/differentiation/physical models,
  hardware/quantum/network/device roles, spatial/robotics, localized messages,
  documents/music/narrative and scientific/legal/accounting notation;
- package managers, standard libraries, formatters, language servers,
  notebooks, browser playgrounds, build systems, deployment systems, and Wasm;
- diagnostics, explanation, first-hour pedagogy, accessibility, AI-readable
  semantics, capabilities, secrets, supply-chain integrity, and governance.

The interface expansion adds questions about representation, change, evidence,
and time. Its edge extension includes accessibility/attention, multilingual and
multimodal input, tangible/spatial models, physical supervision, privacy/evidence,
and learning/repair, with unresearched domains explicitly named. It does not turn
every interface into a new syntax proposal. Further research may begin with an
observed activity, an unexplained difficulty, a primary mechanism or a speculative
alternative, as well as a failed target program. Use the
[design-first agenda](../design/redesign_agenda.md) for known questions; extend
it when the discovery exposes a gap in the map itself.

## Method

The useful unit of comparison is not copied syntax. It is:

```text
user pressure
-> semantic mechanism
-> tradeoff
-> interaction with the whole language
-> Nomi decision or experiment
```

Each finding is classified as one of:

- **convergence** - many successful systems independently need the same
  semantic capability;
- **fork** - credible systems choose incompatible tradeoffs;
- **surface variation** - several spellings encode substantially the same
  mechanism;
- **anti-pattern** - a repeated failure mode with little compensating value;
- **Nomi hypothesis** - a choice that still needs direct evidence.

Research is strongest when it explains which mechanism helps which activity,
what it costs and which alternatives remain. It may broaden the design object,
replace a model or simplify the language. A list of attractive features is not
synthesis.

Registered focused passes may add one topic document when a cross-cutting
contract needs more evidence than the consolidated files can hold cleanly.
[Pattern Matching Research](pattern_matching.md) is the first such packet; it
links directly to canonical design, focused target source, and an implementation
bridge through the [design-pass workflow](../orientation/design_pass_workflow.md).

## Evidence Policy

The earlier corpus mixed primary documentation, comparative notes, design
essays, internal proposals, and implementation observations. These consolidated
documents preserve the level of confidence:

- Language behavior claims should ultimately be checked against official
  specifications or documentation.
- Ecosystem and pedagogy claims are tendencies, not natural laws.
- Nomi decisions are design judgments made from evidence, not facts proved by
  language popularity.
- Current implementation behavior never settles a language-design fork.

Representative primary references include the Python, Rust, Swift, Kotlin,
TypeScript, Go, Zig, Gleam, Elixir, OCaml, Racket, Julia, WebAssembly, and WIT
documentation; Pydantic, serde, zod, Elm JSON Decode, CUE, Dhall, Pkl, JSON
Schema, Terraform, Cargo, Go Modules, Nix, Deno, and Sigstore documentation;
and foundational work by Landin, Strachey, Hoare, Milner, Wadler, and related
language-design traditions.

The old source URLs and longer bibliographies remain available in repository
history. The September review adds freshly checked primary references under
the requested language/feature indexes; it does not restore old competing
atlases or syntheses. Extend these pages with the question, evidence boundary and
design consequence of a useful discovery. An implementation or syntax proposal
must additionally develop concrete programs, contracts and discriminators.
