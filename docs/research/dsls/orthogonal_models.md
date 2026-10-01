# Orthogonal DSL Models

> Status: comparative research and proposed boundary laws, checked 2026-10-01.
>
> These are analytical models, not accepted Nomi semantics. Foreign systems
> were researched through primary sources; none was executed for this chapter.

## What Orthogonal Means Here

Orthogonal means that a family introduces a meaning which another family does
not supply merely by changing its notation. This is a research classification,
not a mathematical assertion that all axes are independent. A constraint model
can contain a temporal model; a circuit can implement a stream processor; a
probabilistic model can be compiled to a differentiable computation.

The important test is what a user may infer from a successfully constructed
artifact. A parsed formula is not a satisfying assignment. A satisfying
assignment is not an optimal solution. A model without a discovered
counterexample is not an unqualified proof about a deployed system. A probability
density is not a sample. A generated machine program is not permission to move
a machine. Those distinctions need explicit adapters even when every surface
looks like an expression returning a value.

Read this alongside the [family atlas](domain_atlas.md), the
[composition cases](composition_boundaries.md), and the
[coverage catalog](coverage.json). The atlas groups user domains; this chapter
groups semantic pressures. Neither classification should become Nomi's IR.

## Independent Questions

Extend the dossier's original nine axes with these questions:

| Dimension | Alternatives which need separate contracts |
| --- | --- |
| Denotation | Value, set/bag/sequence, relation, distribution, behavior set, circuit, geometry, document, obligation |
| Success evidence | Parsed tree, checked environment, validated instance, witness, counterexample, proof term, execution observation |
| Unknowns | Absent value, unbound logic variable, decision variable, symbolic parameter, future event, missing knowledge |
| Multiplicity | Exactly one, optional, finite many, unbounded stream, multiple models, many equivalent representations |
| Order | Source order, priority order, unordered conjunction, partial dependency order, physical time |
| Time | None, logical tick, sample index, event time, processing time, wall-clock recurrence, continuous time |
| State | Immutable artifact, mutable store, feedback register, tokens, external desired/observed state, durable history |
| Search | None, backtracking, fixed point, grounding + solving, optimization, bounded exploration, heuristic inference |
| Algebra | Sets/bags, Boolean/lattice operations, exact arithmetic, floating point, unit algebra, geometric composition |
| Identity | Lexical binder, database/schema identifier, entity identity, node identity, resource identity, coordinate frame |
| Execution owner | Host evaluator, database, solver, controller, renderer, simulator, device, proof kernel |
| Explanation | Value trace, rule provenance, unsatisfiable core, witness, counterexample trace, blame, rendered/source correspondence |

**Inference:** a useful artifact contract is multidimensional. Labels such as
“declarative,” “safe,” “typed,” or “pure” leave most of this table unanswered.

## Twenty-Four Semantic Models

The IDs below are research tags shared by the catalog. They are neither a
feature list nor mutually exclusive buckets. The examples are representative
roles; details and primary links appear in the atlas and existing chapters.

| ID / model | Construction denotes | Distinguishing pressure | Representative roles |
| --- | --- | --- | --- |
| M01 Structural description | Data graph or schema-governed instance | Representation validity versus application meaning | YAML, Protobuf, CDDL, URDF |
| M02 Staged configuration | Value or plan after evaluation/expansion | Inputs and authority change between phases | Dhall, Jsonnet, HCL, Helm |
| M03 Contextual text construction | Structured text with substitutions | Literal, value, identifier and source holes differ | Jinja, tagged templates, Fluent |
| M04 Relational selection | Set/bag of bindings or ordered result | Multiplicity, null/empty and context | SQL, SPARQL, XPath, FHIRPath |
| M05 Recognition/transduction | Pattern match, parse or output stream | Acceptance, recovery and application interpretation differ | RE2, PEG, Kaitai, jq |
| M06 Monotone deduction | Closure of facts under rules | Fixed point; adding facts preserves conclusions within the fragment | Positive finite Datalog |
| M07 Search and alternative models | Answers or candidate interpretations | Branching, negation and enumeration policy | Prolog, answer-set programming |
| M08 Constraint/optimization | Feasible region plus optional objective | Checking, finding and proving optimality differ | SMT-LIB, MiniZinc, CVX |
| M09 Knowledge entailment | Consequences under stated assumptions | Missing knowledge is not automatically false | OWL |
| M10 Decision/authorization | Decision plus evidence or obligations | Defaults, conflicts, precedence and enforcement owner | Cedar, Rego, DMN, ODRL |
| M11 Proof construction | Term proving a formal proposition | Search procedure distinct from trusted checking | Lean tactics |
| M12 Behavioral specification | Allowed traces/states and properties | Safety, liveness, fairness and exploration bounds | TLA+, Alloy, UPPAAL |
| M13 Rewrite/equivalence | Directed transformation or equivalence classes | Strategy, termination and extraction cost | Stratego, Maude, egg |
| M14 Dependency planning | DAG or graph of artifacts/actions | Ready does not imply authorized or conflict-free | Bazel, Make, CI workflows |
| M15 Token/event control | State transitions, tokens, event reactions | Enabling, consumption, priority and macrosteps | Petri nets, SCXML, BPMN |
| M16 Reactive/incremental computation | Live dependency relation | Recompute lifetime, glitches, feedback and updates | QML, spreadsheets, Vega |
| M17 Stream/time-series computation | Windowed or continuous observations | Event time, lateness, trigger and retention | Beam, PromQL, LogQL |
| M18 Synchronous signal/circuit | Clocked or sampled computation | Simultaneity, delay and causality | Chisel, Lustre, Faust |
| M19 Physical/equation simulation | Equations over physical variables | Numerical method, units, initialization and tolerance | Modelica, SPICE, SBML |
| M20 Probability/inference | Distribution, density or weighted model | Score, sample, condition and infer differ | Stan, PRISM |
| M21 Differentiable/staged computation | Transformable numeric computation | Derivative rules, shape, precision and tracing | JAX, symbolic differentiation |
| M22 Spatial/visual composition | Geometry, scene or layout | Frames, identity, layering and rendered evidence | OpenSCAD, USD, CSS, DOT |
| M23 Timed/narrative/document composition | Score, message, document or branching story | Locale, layout, rhythm and interaction history | LilyPond, Tidal, Typst, ink |
| M24 Device/data-plane execution | Program interpreted by specialized hardware | Target capabilities, synchronization and irreversible effects | WGSL, OpenQASM, P4, G-code |

## Deduction, Search, Knowledge And Decisions

### Rules Do Not All Mean The Same Thing

Soufflé supports Datalog-style recursive relations, but its extensions include
arithmetic functors that can produce nontermination. Therefore the useful law
“finite positive rules over a finite domain reach a least fixed point” belongs
to a deliberately bounded fragment, not every program bearing the Datalog
label. [Soufflé tutorial](https://souffle-lang.github.io/tutorial).

Prolog's constraint facilities distinguish posting constraints from enumerating
solutions with labeling. Clingo explicitly separates grounding from answer-set
solving. A host adapter must preserve these phases and alternative answers;
an arbitrary first solution cannot silently become the meaning of a model.
[SWI-Prolog CLP(FD)](https://www.swi-prolog.org/pldoc/man?section=clpfd),
[clingo](https://potassco.org/clingo/).

OWL's open-world reasoning treats missing information differently from a
closed-world database. SHACL validates a data graph against shapes. A
conclusion entailed by an ontology and an instance satisfying a shape answer
different questions. Translating either to a generic predicate can erase the
knowledge assumption or validation scope.
[OWL 2 primer](https://www.w3.org/TR/owl2-primer/),
[SHACL recommendation](https://www.w3.org/TR/shacl/).

Original counterexample: facts contain `employee(Ada)` but no clearance fact.
Under one closed-world lookup, `has_clearance(Ada)` is false. Under an
open-world interpretation, both a model with clearance and a model without
clearance remain possible. A denial decision requires a separate policy. The
[finite probe](experiments.md#orthogonal-model-probes) records this distinction
without implementing an ontology reasoner.

### Conflict Is A Domain Law

Cedar defaults to deny, lets a satisfied forbid override satisfied permits,
and returns determining policies and evaluation diagnostics. It also uses
skip-on-error: a policy evaluation error does not become an overriding forbid.
Consequently “errors always deny” is not an adequate description of its
combination law. [Cedar authorization](https://docs.cedarpolicy.com/auth/authorization.html).

DMN decision tables have declared hit policies. Camunda documents single-hit
policies such as Unique and First and multiple-hit policies such as Collect.
The same matching rows can therefore mean a violation, a prioritized result or
many results. ODRL additionally represents duties; describing a duty does not
itself perform its action.
[Camunda hit policies](https://docs.camunda.io/docs/components/modeler/dmn/decision-table-hit-policy/),
[ODRL 2.2 duties](https://www.w3.org/TR/odrl-model/#duty).

**Nomi fork:** an ordinary function can return a rich domain decision; a
domain artifact can retain rule provenance. Neither requires a core rule
keyword. Test decision variants, explanation and enforcement separation before
considering notation.

## Validation, Solving, Optimization And Proof

MiniZinc distinguishes parameters from decision variables and supports solve
items for satisfaction or optimization. CVX admits a disciplined composition
ruleset that is sufficient, not necessary, for convexity. Rejection by that
checker does not establish that a mathematical expression is nonconvex.
[MiniZinc modeling](https://docs.minizinc.dev/en/stable/modelling.html),
[CVX DCP rules](https://cvxr.com/cvx/doc/dcp.html).

Alloy analysis uses scopes to bound exploration. A successful bounded search
must retain its scope; it is not an unbounded theorem. Lean's tactic language
constructs proof terms which the kernel checks. A tactic search failing to
find a proof is distinct from a counterexample, and a checked proof concerns
the formal statement and assumptions actually supplied.
[Alloy language reference](https://alloytools.org/download/alloy-language-reference.pdf),
[Lean tactics](https://lean-lang.org/doc/reference/latest/Tactic-Proofs/).

Original example: assign two jobs to two slots, requiring different slots.
There are two feasible assignments. Checking one supplied assignment gives a
Boolean; finding assignments gives a collection; minimizing a cost selects an
optimum; a search stopped before inspecting all assignments gives incomplete
evidence. These cannot share an undocumented `solve -> Bool` API.

Proposed result distinctions, expressed here as descriptive alternatives rather
than accepted type declarations:

| Operation | Evidence it may return | Failure/incompleteness which must remain visible |
| --- | --- | --- |
| Parse | Source-backed tree | Syntax diagnostics, incomplete draft |
| Check | Artifact tied to environment/assumptions | Unsupported construct, type/shape/dialect errors |
| Validate | Instance report | Violation, missing prerequisite, validator limitation |
| Find | Witness or bounded answer collection | Unsatisfiable under stated assumptions; budget exhausted |
| Optimize | Feasible incumbent, bound and optimality status | Infeasible, unbounded, unknown, approximate or interrupted |
| Explore | Counterexample or bounded coverage evidence | State/time bound, unsupported model, aborted exploration |
| Prove | Checked proof term plus theorem/assumptions | Search failure, checker rejection, axiom dependency |
| Execute | Observation and completion record | Domain failure, host failure, cancellation, partial effects |

**Inference:** Nomi's Result and Option remain useful building blocks, but do
not select the domain-specific evidence variants. `None`, false, unsatisfiable,
unknown and denied should not collapse into one propagation convention.

## Rewriting Is Not Evaluation Order

Stratego separates transformation rules from traversal strategies; indiscriminate
normalization can fail to terminate or choose an unwanted result. Maude's
rewriting-logic model can describe state changes, rather than only expression
simplification. Equality saturation with egg keeps equivalent expressions in
an e-graph and separates exploration from extraction of a chosen expression.
[Strategic rewriting](https://spoofax.dev/background/stratego/strategic-rewriting/strategic-rewriting/),
[Maude foundational manual](https://maude.cs.illinois.edu/maude1/manual/maude-manual-html/maude-manual_61.html),
[egg primary paper](https://arxiv.org/abs/2004.03082).

The Maude citation is historical foundational evidence, not verification of
the latest implementation. These three mechanisms should not be summarized as
an ordered list of Nomi desugar passes. They have different semantic purposes.

Original counterexample: reassociation is valid over exact integer addition,
but `(1e16 + -1e16) + 1` and `1e16 + (-1e16 + 1)` differ in the local float
probe. Rewrite admission needs a named arithmetic theory, rounding policy,
side conditions and effect policy. “Pure” alone does not establish equality.

**Nomi fork:** retain inspectable reductions for supported source conveniences;
use a separate library artifact for speculative equivalence search. Do not give
a domain optimizer permission to reorder general host evaluation.

## Many Kinds Of Time And Concurrency

### Behavior Sets, Events And Tokens

TLA+ describes behaviors and temporal properties; PlusCal translates algorithms
to TLA+. UPPAAL's timed semantics has delay and action transitions over clock
valuations and location invariants. SCXML processes follow-up microsteps before
the next external event, but a macrostep need not terminate. Thus even
“run to completion” needs the particular completion boundary.
[TLA+ book](https://lamport.azurewebsites.net/tla/book-02-02-27.pdf),
[PlusCal translation](https://lamport.azurewebsites.net/tla/tutorial/session11-1.html),
[UPPAAL semantics](https://docs.uppaal.org/language-reference/system-description/semantics/),
[SCXML execution semantics](https://www.w3.org/TR/scxml/#AlgorithmforSCXMLInterpretation).

A Petri-net token can model consumable availability, while a DAG edge models a
dependency. PNML supplies interchange for Petri-net models, not a general
production workflow executor. In our finite one-token probe, two individually
enabled transitions compete for the same token; executing one disables the
other. Two ready DAG jobs do not encode that exclusion without an additional
resource law. [PNML project](https://www.pnml.org/).

### Recompute, Windows, Clocks And Samples

QML bindings update properties when dependencies change; an imperative
assignment can replace a binding. That is a distinct operation from updating
an input while preserving the live relation.
[QML binding lifecycle](https://doc.qt.io/qt-6/qtqml-syntax-propertybinding.html).

Beam separates event-time windows, processing-time behavior, watermarks and
triggers. A watermark concerns estimated completeness, not proof that no late
event can occur. PromQL distinguishes instant vectors and range vectors, and
its range selector uses a left-open, right-closed interval. Importing a generic
`window` operation without endpoint and lateness policies loses meaning.
[Beam programming guide](https://beam.apache.org/documentation/programming-guide/),
[PromQL basics](https://prometheus.io/docs/prometheus/latest/querying/basics/).

Chisel's `RegNext` delays a signal by one cycle; host evaluation elaborates
hardware instead of advancing the circuit's clock. Faust's recursive
composition routes feedback through an implicit one-sample delay. Logical
ticks, sample indices and seconds are not interchangeable merely because all
can be represented by integers.
[Chisel sequential circuits](https://www.chisel-lang.org/docs/explanations/sequential-circuits),
[Faust recursive composition](https://faustdoc.grame.fr/manual/syntax/).

iCalendar distinguishes floating local time, UTC time and local time with a
time-zone reference. A recurrence in a local calendar has a different contract
from repeatedly adding a fixed number of seconds. An adapter must retain the
calendar/time-zone context rather than parsing every time-like string as a
timestamp. [RFC 5545 date-time](https://www.rfc-editor.org/rfc/rfc5545.html#section-3.3.5).

**Nomi fork:** ordinary nominal time/frame/signal values versus a scoped
temporal tool. First test whether explicit library composition keeps clocks,
lifetime, cancellation and feedback intelligible. Do not repurpose `async` or
`|>` to stand for all these relationships.

## Probability, Derivatives And Physical Models

Stan distribution statements contribute to a joint density; its manual now
discourages the historical name “sampling statements.” Writing a model and
running an inference algorithm are distinct activities. PRISM instead uses
probabilistic system models and model checking. A posterior inference result
and a reachability probability answer different questions.
[Stan statements](https://mc-stan.org/docs/reference-manual/statements.html),
[PRISM language](https://www.prismmodelchecker.org/manual/ThePRISMLanguage/Introduction).

JAX's `grad` transforms a scalar-output function into a gradient function.
This is an embedded domain operation within a general-purpose host, not a new
external syntax. Modelica equations state relationships among variables rather
than ordinary assignment order. Numerical simulation also needs initialization,
solver and tolerance contracts; a schema-valid model alone does not establish
a reliable trajectory.
[JAX differentiation](https://docs.jax.dev/en/latest/automatic-differentiation.html),
[Modelica 3.6 equations](https://specification.modelica.org/maint/3.6/equations.html).

UCUM distinguishes equality of units from commensurability and treats special
non-ratio scales separately from ordinary unit multiplication. A numeric domain
must therefore specify whether a value is a point on a scale, a difference,
a quantity, a probability or a dimensionless number.
[UCUM semantics](https://ucum.org/ucum).

**Inference:** common Nomi support should preserve numeric representation,
shape, units, random-state ownership, reproducibility metadata and failure
evidence. It should not supply one generic `model.run()` meaning for all of them.

## Space, Rendering, Language And Devices

USD composes and overrides scene assets in a scenegraph; DOT describes graphs
for layout. A picture of a dependency does not grant the picture execution
semantics. Typst switches among markup, math and code modes. Fluent selects
message variants using values and locale plural categories, so localized text
is not reducible to ordinary positional interpolation.
[USD introduction](https://openusd.org/release/intro.html),
[DOT language](https://graphviz.org/doc/info/lang.html),
[Typst syntax](https://typst.app/docs/reference/syntax/),
[Fluent selectors](https://projectfluent.org/fluent/guide/selectors.html).

WGSL requires `workgroupBarrier` calls in uniform control flow. OpenQASM gate
definitions describe unitary operations with restrictions different from
ordinary host functions. LinuxCNC documents modal G-code commands whose meaning
depends on retained controller modes. These are target-owned semantics; a
well-typed host callback or well-formed text does not satisfy them automatically.
[WGSL uniformity](https://www.w3.org/TR/WGSL/#uniformity-analysis),
[OpenQASM gates](https://openqasm.com/language/gates.html),
[LinuxCNC G-code](https://linuxcnc.org/docs/stable/html/gcode/overview.html).

**Nomi fork:** separate checked artifact types and adapters for domain owners.
Host effects, device capabilities and simulator evidence must remain visible
at execution boundaries. A shared editing/source-map protocol may be useful;
a shared evaluator which invents the meaning of every model is not justified.

## Consequences For The Existing Design

| Nomi owner | Pressure added by this expansion | Concrete next discriminator |
| --- | --- | --- |
| Strings/data boundaries | Text can encode binders, byte patterns, molecules, units, messages and commands | E13/E22: preserve exact source and return distinct checked values |
| Function contracts | A callback may build a domain expression, not execute at every runtime event | E17/E21: state invocation/staging/effect contract |
| Failure/completion | Unknown, infeasible, denied, no match and partial observation differ | E14/E19: domain result algebra and explanation |
| Effects/resources | Checking/importing/executing can have separate authority and lifetimes | E16/E17/E22: cancellation, caches and handles |
| Queries/data workflows | Sets, bags, sequences, event windows and streams differ | E13/E18: multiplicity and temporal witnesses |
| Numerical design | Rewrite laws, units, inference and derivatives depend on representation | E20/E21: exact/float/unit/gradient boundaries |
| Cognitive interfaces/tooling | Draft recovery, proof goals, plans and rendered projections need different explanation | E15/E22: source-backed diagnostics and inspectable artifacts |

The new discriminators are in the existing [candidate experiment table](nomi_candidates.md).
They extend E1-E12; they do not create another live project backlog. Their
priority remains after the initial string-boundary packet unless a target
program demonstrates an immediate gap.
