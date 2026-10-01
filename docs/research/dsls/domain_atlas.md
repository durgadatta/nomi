# DSL Domain Atlas

> Status: broad primary-source research with explicit depth limits, 2026-10-01.
>
> Domain coverage is evidence for Nomi experiments, not syntax admission or
> a claim of compatibility with the named systems.

## Scope And How To Use The Atlas

This expansion treats configuration as one part of a much larger space. The
[machine-readable catalog](coverage.json) records representatives, family IDs,
semantic-model tags, primary references, coverage depth and local evidence.
The family partition below is for navigation: systems can cross families, and
general-purpose languages appear only for their relevant embedded DSL role.
JAX, Racket and Lean are not classified wholesale as narrow domain languages.

Each row pairs a user pressure with a distinction that an integration must
preserve. The counterexamples are original research fixtures. External
semantics are supported by the linked primary references; implications for
Nomi are research inferences. Existing chapters retain the deeper Kubernetes,
GitHub Actions, string and configuration comparisons.

Coverage labels in the catalog:

- `mechanism-reviewed`: a specific documented mechanism is compared in this
  dossier; this is not a complete product/language review.
- `indexed`: an official source establishes the representative's role, but
  detailed semantics, versions and integrations remain untested here.

The first dossier's ten host probes and the new eight finite-model probes are
separate evidence. No catalog entry means that its foreign runtime passed a
conformance test. A family count measures breadth, never design quality.

## A. Description, Configuration And Operations

| Family | User pressure / representatives | Distinction to preserve | String or source boundary |
| --- | --- | --- | --- |
| F01 Serialization | Exchange values: YAML | Tagged graph and scalar policy precede domain interpretation | Duplicate/alias/source evidence can disappear during decoding |
| F02 Schema and wire contracts | Validate/evolve messages: JSON Schema, Protobuf, CDDL | Shape, vocabulary and wire compatibility are different guarantees | A field spelling or schema reference is not an arbitrary Text value |
| F03 Constraint/programmed configuration | Construct environment-specific values: CUE, Dhall, Jsonnet, Pkl, Nickel, HCL | Unification, priorities, laziness and totality have different laws | Imports and template expressions have their own stages and scopes |
| F04 Desired-state infrastructure | Declare external resources: Kubernetes, Terraform | Desired state, plan, admission and observed state differ | Provider/resource identities require versions and authority |
| F05 Templates and overlays | Reuse deployment descriptions: Helm, Kustomize | Rendered text versus structured patch; merge order and field identity | Source generation cannot be treated as scalar substitution |
| F06 CI orchestration | Assemble jobs: GitHub Actions, GitLab, Azure, Argo | Edges, invocation interfaces and context availability differ | `needs`, `uses`, `with` belong to the workflow owner; script text has another owner |
| F07 Service/host automation | Operate services: Compose, Ansible, systemd | Load/expand/condition/launch/reconcile are separate operations | Command fields do not all use a shell grammar |
| F08 Build/package/image descriptions | Produce artifacts: Bazel, Starlark, Nix, Make, Dockerfile | Loading/analysis/execution and action identity affect caching | Host expressions, recipe expansion and command arguments need separate spans |

Detailed evidence is in [layered configuration](layered_configuration.md) and
the original [coverage map](README.md#representative-coverage-map).
CDDL describes CBOR/JSON data structures; it is not itself a runtime validator
or an API implementation. [RFC 8610](https://www.rfc-editor.org/rfc/rfc8610.html).
systemd's command-line rules explicitly differ from ordinary shell syntax;
an adapter must not infer pipelines or shell redirection from an `ExecStart`
field. The inspected maintainer source also has explicit shell-invocation
prefixes; these need version-aware handling rather than inference from a
shell-looking argument. The public manual was access-blocked, so the source
was used. [systemd service command documentation](https://raw.githubusercontent.com/systemd/systemd/main/man/systemd.service.xml).

Original counterexample: a key named `uses` in a YAML document is ordinary
mapping data until a domain owner supplies meaning. A Nomi decoder should not
reserve it globally because GitHub Actions interprets it specially.

**Nomi fork and experiment:** typed resource builders plus codecs versus
explicitly parsed foreign configuration. E2-E8 already compare these choices.
Keep input schemas, expansion contexts, imports and execution handles visible;
do not add one core “configuration block” that invents a common evaluation law.

## B. Selection, Recognition And Language Construction

| Family | User pressure / representatives | Distinction to preserve | String or source boundary |
| --- | --- | --- | --- |
| F09 Relational/graph querying | Ask questions of stored relations: SQL, SPARQL | Bags versus sets; binding compatibility; ordering and entailment regimes | Values, identifiers, query syntax and dataset identities differ |
| F10 Document/API querying | Navigate structured values: GraphQL, jq, JSONPath, XPath, FHIRPath | A stream, nodelist, sequence, operation and collection are different results | Root/current node, namespace and schema own names |
| F13 Recognition and detection | Find text/byte/packet structures: RE2, YARA, Wireshark filters | Match versus extraction; byte versus character; any/all repeated fields | Pattern source and literal data have separate contracts |
| F15 Grammar/parser construction | Describe accepted source: ABNF, PEG, ANTLR, Tree-sitter, Kaitai | Recognition, generated parser, recovery and binary layout differ | Grammar literals are not application values; offsets may be bytes |
| F16 Language construction | Build a reader/expander: Racket | Reader, lexical hygiene, expansion and execution differ | Syntax objects retain binder/source identity beyond plain text |
| F48 Commands/text processing | Invoke or transform: POSIX shell, awk | Argument vectors, shell programs and pattern/action streams differ | Words undergo owner-specific expansion; matching text may generate output |

SPARQL's solutions use multiset semantics. FHIRPath maps missing underlying
elements to empty collections, and its singleton operations have explicit
cardinality rules. Neither should inherit Nomi Option semantics implicitly.
[SPARQL 1.1 algebra](https://www.w3.org/TR/sparql11-query/#sparqlAlgebra),
[FHIRPath STU3 collections](https://hl7.org/fhirpath/STU3/en/index.html).

Ford's PEG formalism uses prioritized choice. Reordering alternatives can
change the recognized language, unlike an unordered mathematical union of
alternatives. Kaitai describes binary layouts, including byte/bit order and
alignment; a YAML carrier does not make those semantics YAML semantics.
[PEG primary paper](https://bford.info/pub/lang/peg.pdf),
[Kaitai guide](https://doc.kaitai.io/user_guide.html).

YARA distinguishes hexadecimal, text and regex strings. Wireshark display
filters operate on typed protocol fields; these are not capture-filter syntax.
We index ANTLR as a parser-generator role rather than claiming parity with
Tree-sitter recovery or PEG recognition.
[YARA rules](https://yara.readthedocs.io/en/stable/writingrules.html),
[Wireshark display filters](https://www.wireshark.org/docs/man-pages/wireshark-filter.html),
[ANTLR project](https://www.antlr.org/).

Original counterexamples: two duplicate matching rows survive a bag query but
collapse in a set; an empty selection is not a parse failure; a grammar that
recognizes an integer does not decide whether the integer names a user, a
length or a duration. E13/E22 test these boundaries.

**Nomi fork:** ordinary combinators with explicit result cardinality versus a
foreign query/pattern artifact. Require named root/schema/dialect environments
and contextual quoting. Defer general reader/grammar extensibility until a
library failure and an editing/formatting contract are demonstrated.

## C. Logic, Knowledge, Policy And Law

| Family | User pressure / representatives | Distinction to preserve | String or source boundary |
| --- | --- | --- | --- |
| F11 Authorization/policy | Decide access from data: CEL, Rego, Cedar, SpiceDB | Evaluation context, undefined, default, conflict and relation traversal | Entity IDs and checked field names are not executable expression holes |
| F12 Decision/rights/legal rules | Explain decisions and duties: DMN, FEEL, ODRL, Catala | Hit policy, exception precedence, obligation and executable rule interpretation | Human source/provision IDs need retained provenance |
| F17 Logic programming | Derive or search answers: Soufflé, Prolog CLP(FD), clingo | Closure, procedural search and alternative stable models differ | Logic variables are domain binders; external names require mappings |
| F18 Knowledge/shape systems | Represent and inspect knowledge: OWL, SHACL | Open-world entailment versus graph validation | IRIs, datatypes, namespaces and imported vocabularies have identities |
| F19 Constraint/optimization | Find feasible/best values: SMT-LIB, MiniZinc, CVX | Assignment check, satisfiability, feasibility, objective and certification differ | Variable labels are symbolic references, not host variable capture |
| F20 Proof/tactics | Construct checkable evidence: Lean tactic language | A tactic program constructs a proof; kernel acceptance is a separate guarantee | Binder hygiene and theorem/axiom identity must survive serialization |

SpiceDB schemas describe relations and permissions over relationship data.
Its intersection arrow requires permission through all linked subjects,
whereas ordinary arrows have a different traversal condition. A generic
“graph path” interpretation would lose the authorization law.
[SpiceDB schema](https://authzed.com/docs/spicedb/concepts/schema).

Catala encodes definitions and explicit exceptions, including exceptions of
exceptions. It also supports literate legal source. We study the mechanism of
source-backed rule interpretation; executable output does not by itself
certify legal correctness or choose an applicable jurisdiction.
[Catala exceptions](https://book.catala-lang.org/en/5-4-definitions-exceptions.html),
[literate programming](https://book.catala-lang.org/en/5-1-literate-programming.html).

The [orthogonal-model chapter](orthogonal_models.md#deduction-search-knowledge-and-decisions)
compares rule, world-assumption, conflict and evidence laws in depth.

Original counterexamples: an unbound variable is not missing data; no answer
found within a budget is not proof of no answer; lack of a permission fact is
not the same reasoning operation as an explicit forbid. A decision table with
two matching rows needs its hit policy before either row can be selected.

**Nomi fork:** return domain evidence from ordinary libraries, with a separately
checked rule/model artifact where needed. E14/E15/E19 discriminate whether the
existing failure and inspection interfaces preserve uncertainty, alternatives,
assumptions, determining rules and witnesses.

## D. Formal Behavior, Rewriting And Planning

| Family | User pressure / representatives | Distinction to preserve | String or source boundary |
| --- | --- | --- | --- |
| F21 Behavioral/formal models | Describe allowed behaviors: TLA+, PlusCal, Alloy, UPPAAL, PRISM | Temporal property, bounded relation search, timed automata and probabilistic reachability differ | State/property labels must map to model assumptions and trace spans |
| F22 Rewrite/equivalence systems | Transform or explore alternatives: Maude, Stratego, egg | State rewrite, traversal strategy and equality saturation differ | Rewrite binders and side conditions require a named theory |
| F23 Scientific workflows | Execute reproducible tools: CWL, Nextflow | Dataflow model, process scripts and executor/cache contracts | Paths, argv and scripts require distinct quoting/effect boundaries |
| F24 Token/business workflows | Describe process progress: Petri nets/PNML, BPMN | Token enabling, gateways, durable history and compensation differ | A diagram or interchange file is not a runner guarantee |
| F25 State/behavior control | Respond to events: statecharts, SCXML, BehaviorTree.CPP | Event macrosteps versus recurring ticks and running/success/failure | State/node references and external action names need explicit ownership |
| F26 Planning | Find actions achieving goals: PDDL | Domain model, initial facts, goals, plan search and plan execution differ | Object/action names and requirements belong to the planning domain |

PRISM documents multiple probabilistic model types; UPPAAL defines timed
transitions. PDDL's 1998 committee manual separates domains/problems and action
descriptions. We cite that edition for the foundational split, not later
durative/numeric extensions. BehaviorTree.CPP 3.8 documents different restart
behavior among its sequence variants when children return Running or Failure.
[PRISM](https://www.prismmodelchecker.org/manual/ThePRISMLanguage/Introduction),
[UPPAAL](https://docs.uppaal.org/language-reference/system-description/semantics/),
[PDDL 1998](https://www.cs.cmu.edu/~mmv/planning/readings/98aips-PDDL.pdf),
[sequence variants, version 3.8](https://www.behaviortree.dev/docs/3.8/nodes-library/SequenceNode/).

BPMN 2.0.2 and PNML are indexed as modeling/interchange standards. This survey
does not verify vendor persistence, transaction, compensation or deployment
semantics. Such guarantees must be tested against the chosen engine.
[BPMN 2.0.2](https://www.omg.org/spec/BPMN/2.0.2/About-BPMN),
[PNML](https://www.pnml.org/).

Original counterexamples: a dependency cycle may be an error in a build graph,
a valid feedback path in a signal model, or a transition loop in a state
machine. “Cycle detected” is not a universally correct diagnostic. A computed
plan may become invalid after the physical world changes.

**Nomi fork:** domain-typed graphs and traces versus a universal graph executor.
E16/E17 preserve token/resource laws and lifecycle; E15/E20 preserve formal
assumptions and rewrite theories. Keep `with` and task completion tied to their
accepted resource semantics rather than borrowing process-engine vocabulary.

## E. Reactive, Streaming, Signal And Numeric Models

| Family | User pressure / representatives | Distinction to preserve | String or source boundary |
| --- | --- | --- | --- |
| F27 Reactive UI/table/visualization | Keep views updated: QML, Excel formulas, Vega | Live binding, recomputation, spill and input mutation differ | Field/cell references have scopes, identities and rename behavior |
| F28 Stream processing | Process events over time: Beam | Event-time membership versus arrival, triggers and late data | Timestamp/time-domain labels cannot be erased into integers |
| F29 Observability queries | Inspect telemetry: PromQL, LogQL | Time-series types and log/filter/metric stages differ | Labels, regexes, range durations and query strings are typed sublanguages |
| F30 Synchronous/signal languages | Compose timed signals: Lustre, Faust, SuperCollider patterns | Logical tick, sample feedback and event generation differ | Signal/node/clock names need retained execution-domain identity |
| F31 Hardware elaboration | Build circuits: Chisel | Host elaboration versus simultaneous clocked hardware | Register/wire names are hardware references, not host state mutation |
| F32 Physical/biological simulation | State equations/reactions: Modelica, SPICE/ngspice, SBML | Mathematical model, numerical solver and observation differ | Units, component/model IDs and initial conditions need schema/context |
| F33 Probability/inference | Define uncertain models: Stan | Density evaluation, conditioning, simulation and posterior inference differ | Parameter/data/model names have different stages |
| F34 Symbolic/differentiable computation | Transform numeric functions: JAX, SymPy | Symbolic solution, derivative transform and numerical evaluation differ | Symbol names and host capture are different binding mechanisms |
| F45 Units/measurement notation | Exchange quantities: UCUM | Dimensions, magnitudes and special scales differ | Unit strings are parsed expressions; display labels are not unit identity |

The [model comparison](orthogonal_models.md#probability-derivatives-and-physical-models)
owns the deeper numerical distinctions. SBML is indexed as a systems-biology
model format with versioned specifications; ngspice as a circuit simulator with
netlist/control languages. Schema validity does not establish physiological or
physical truth. [SBML specifications](https://sbml.org/documents/specifications/),
[ngspice documentation](https://ngspice.sourceforge.io/docs.html).

Lustre's project describes the synchronous approach and associated verification
tools. SuperCollider's Pattern abstraction produces streams of values/events.
They are indexed as distinct temporal roles rather than asserted to share
Faust's sample-by-sample feedback semantics.
[Lustre tool documentation](https://www-verimag.imag.fr/DIST-TOOLS/SYNCHRONE/lustre-v6/),
[SuperCollider Pattern](https://docs.supercollider.online/Classes/Pattern.html).

Excel's relative/absolute/structured references and spill boundaries remain
owned by the existing [spreadsheet thread](../interfaces/spreadsheets.md).
LogQL has log and metric query roles; it should not be coerced into PromQL
merely because some syntax is familiar.
[LogQL](https://grafana.com/docs/loki/latest/query/).

Original counterexamples: a late event has an old event timestamp but a new
arrival timestamp; a float rewrite can change a result; one density statement
need not draw a random number; a quantity point and a temperature difference
cannot have the same unrestricted arithmetic merely because both use degrees.

**Nomi fork:** library types and transformations that retain domains versus
scoped mathematical notation. E18/E20/E21 test temporal endpoints, arithmetic
theories, probabilistic evidence and callback staging. Existing DW experiments
continue to own the broader scientific/data workflow program.

## F. Devices, Networks, Space And Motion

| Family | User pressure / representatives | Distinction to preserve | String or source boundary |
| --- | --- | --- | --- |
| F35 GPU/shader execution | Compute/render on parallel devices: WGSL | Invocation/address spaces, uniformity and synchronization | Entry points and resource bindings belong to a target module |
| F36 Quantum programs | Compose quantum/classical operations: OpenQASM | Gate construction, measurement, control and target execution differ | Qubit identifiers cannot become ordinary copied data |
| F37 Packet/data-plane policy | Describe packet handling: P4, nftables | Parser, match/action, stateful chain and control-plane updates differ | Header/field/table identities and ordering have owner-specific meaning |
| F38 Geometry/scene composition | Construct shapes/assets: OpenSCAD, OpenUSD | Geometry operation versus layered scene identity and override | Paths/assets/frames are structured references, not display text |
| F39 Robotics/manufacturing | Describe bodies or machine operations: URDF, G-code | Kinematic description versus modal action/execution | Joints, coordinate frames, units, modes and target capabilities differ |
| F40 Diagram/graph layout | Communicate structures: DOT, Mermaid | Graph syntax, layout and rendering differ from represented execution | Labels/HTML-like labels and node IDs need different escaping |
| F49 Stylesheet rules | Describe presentation: CSS | Cascade/context/application behavior follows parsing | Selector/property/URL text has distinct grammar and context |

P4 specifies packet-processing programs and distinguishes program structure
from control-plane table contents. We use its versioned 1.1.0 specification
for this distinction, without asserting current target support. nftables
describes rules/chains/sets for packet filtering; importing its rule text should
not authorize changing the host ruleset.
[P4-16 1.1.0](https://p4lang.github.io/p4-spec/docs/P4-16-v1.1.0-spec.html),
[nftables manual](https://www.netfilter.org/projects/nftables/manpage.html).

OpenSCAD's project documentation indexes geometric primitives, transformations
and Boolean operations. URDF's maintainer repository documents version-dependent
robot-description parsing. Mermaid and DOT are indexed for visual notation;
neither a rendered arrow nor a graph label establishes an application contract.
[OpenSCAD documentation](https://openscad.org/documentation.html),
[urdfdom](https://github.com/ros/urdfdom),
[Mermaid flowcharts](https://mermaid.js.org/syntax/flowchart.html).

Original counterexample: `X10` in a modal machine program depends on established
modes and coordinates; a numeric literal in an immutable robot description
does not command motion. Equal source text interpreted for two controllers can
have different capability/support outcomes.

**Nomi fork:** checked target-specific artifacts with explicit simulator/device
adapters. E17/E22 demand target identity, capability checks, validation-only
authority and mapped diagnostics. Physical execution is outside these probes.

## G. Documents, Messages, Media And Narrative

| Family | User pressure / representatives | Distinction to preserve | String or source boundary |
| --- | --- | --- | --- |
| F14 Templates/localized messages | Render context-dependent text: Jinja, JS tagged templates, Fluent, ICU MessageFormat | Substitution, escaping, selection and locale grammar differ | Named typed holes; translator-controlled whole messages; locale identity |
| F41 Structured documents | Compose readable publications: Typst, CommonMark | Markup/math/code modes versus document parsing/rendering | Delimiters, code islands, references and rendered/source correspondence |
| F42 Music/timed media | Compose scores/patterns: Tidal, LilyPond, MusicXML | Engraving, symbolic score, cycle pattern and playback differ | Notes/sample names, rational durations and text strings have distinct roles |
| F43 Interactive narrative | Write branching stories: ink | Choice display, emitted narrative and persistent story state differ | Text may contain control syntax; localization must preserve branch identity |
| F47 Calendar/recurrence | Schedule civil-time occurrences: iCalendar | Local calendar rule versus instant/duration and scheduler policy | Zone IDs, dates and recurrence expressions need typed parsing |
| F50 Executable examples | Describe behavior for tests: Gherkin | Human-readable step text versus executable step definitions | Matching a sentence does not constrain the authority of its implementation |

Fluent permits numeric exact matches and locale plural categories. ICU documents
plural/select arguments and recommends whole-message branches for translators.
Localized message ASTs should preserve named arguments and selection rather
than merely concatenate a prefix, number and suffix.
[Fluent selectors](https://projectfluent.org/fluent/guide/selectors.html),
[ICU messages](https://unicode-org.github.io/icu/userguide/format_parse/messages/).

Tidal's mini-notation parses strings into cyclic patterns, including subdivision,
rests and speed changes. LilyPond combines sequential and simultaneous music
expressions. MusicXML 4.0 is a score-interchange format, not a specified audio
engine. Similar-looking brackets do not establish a common duration algebra.
[Tidal mini-notation](https://tidalcycles.org/docs/reference/mini_notation/),
[LilyPond 2.24 expressions](https://lilypond.org/doc/v2.24/Documentation/learning/music-expressions-explained),
[MusicXML 4.0](https://www.w3.org/2021/06/musicxml40/).

ink distinguishes displayed choice text from text emitted after the choice.
Gherkin connects scenario steps to implementation definitions. We index these
for semantic/human-source correspondence, without treating natural-language
surface as a guarantee of arbitrary machine understanding.
[ink tutorial](https://www.inklestudios.com/ink/web-tutorial/),
[Gherkin reference](https://cucumber.io/docs/gherkin/reference/),
[CommonMark 0.31.2](https://spec.commonmark.org/0.31.2/).

Original counterexamples: English singular/plural cannot define another locale's
selection law; a cycle index is not seconds; translation of a choice label
must not accidentally rename its target; a rendered document can be valid even
when a referenced external asset is unavailable to the execution environment.

**Nomi fork:** ordinary typed document/message/score values versus bounded
scoped text notation. E1/E2/E9 remain central; E13/E18/E22 add argument schemas,
clock identities, source modes, rendering explanations and translation edits.

## H. Scientific Notation, Clinical Queries And Accounting

| Family | User pressure / representatives | Distinction to preserve | String or source boundary |
| --- | --- | --- | --- |
| F44 Molecular/clinical nomenclature | Exchange domain structures: SMILES, SMARTS, HGVS, CQL; FHIRPath cross-link | Molecular graph, substructure pattern, reference-dependent variant and clinical expression differ | Atom/variant/reference names and model/terminology versions are semantic inputs |
| F46 Accounting ledger | Record balanced transactions: Beancount | Posting weights, inventories, assertions and narration differ | Account/commodity IDs are structured names; narration remains text |

Daylight describes SMILES as molecular graphs with optional stereochemical
information and multiple valid source representations; SMARTS is a query
notation for molecular patterns. Do not use raw string equality as molecular
identity, or treat a molecule and a substructure query as the same value.
[SMILES](https://www.daylight.com/dayhtml/doc/theory/theory.smiles.html),
[SMARTS](https://www.daylight.com/dayhtml/doc/theory/theory.smarts.html).

HGVS and CQL are indexed for reference/context-sensitive scientific notation,
not evaluated as medical guidance. Their versions and reference/model inputs
must be pinned for any later adapter.
[HGVS nomenclature](https://hgvs-nomenclature.org/stable/),
[HL7 CQL](https://cql.hl7.org/).

Beancount documents balancing through the weight of postings rather than a
naive sum of unqualified numbers; costs and prices affect that calculation.
This is mechanism evidence from its historical syntax guide, not a claim about
every current plugin or report engine.
[Beancount syntax](https://beancount.github.io/docs/beancount_language_syntax/).

Original counterexamples: the same variant coordinate against two reference
sequences need not identify the same change; equal numeric amounts in distinct
commodities cannot be added without a conversion/valuation rule; a description
of a molecule does not establish a measured physical property.

**Nomi fork:** validated nominal references/quantities and domain codecs before
symbolic notation. E13/E19/E21/E22 test model identity, evidence, unit/reference
checking and exact string preservation. The existing
[notation atlas](../notation_atlas.md) remains the owner of broader thought
experiments in chemistry, genetics, linguistic notation and evidence.

## Breadth Limits And Deliberate Gaps

This is coverage of distinct pressures, not an inventory of every DSL ever
published. Additional vendor dialects rarely justify new core syntax, but can
introduce consequential semantics. Candidate follow-ups are indexed here as
gaps rather than presented as researched facts:

| Remaining cluster | What a later targeted investigation must establish |
| --- | --- |
| PLC/industrial control, safety-critical avionics | Scan cycles, real-time assumptions, certified tool boundaries and device IO |
| GIS/geospatial and maps | Coordinate reference systems, geodesic operations, topology and precision |
| Accessibility/layout constraint systems | Constraint priorities, focus/interaction state and semantic rendered structure |
| Process calculi/session/choreography languages | Communication duality, projection and distributed progress assumptions |
| Financial contracts/trading/actuarial languages | Time, valuation, obligations, rounding and external data authority |
| Epidemiological/agent-based/ecological models | Stochastic updates, scheduler assumptions and empirical calibration |
| Security protocol and cryptographic proof tools | Adversary model, symbolic/computational assumptions and proof scope |
| Educational/turtle/block/robot languages | Projection consistency, beginner errors and physical/simulated distinction |
| More build/workflow/config variants | Host vocabulary, merge/expansion rules, plugins and stored-version migration |
| Natural language and agent tool specifications | Ambiguity, tool authority, evidence, reproducibility and review boundaries |

These gaps do not block the initial string work. Extend a family only when a
target program exposes a missing law. For a future addition, record its
pressure, semantic model, genuine competing Nomi choices, original failure
fixture, diagnostic and stopping criterion in the same dossier.
