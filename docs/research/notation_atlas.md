# Notation Beyond Programming

> Status: cross-disciplinary evidence and original design exercises; no new Nomi grammar.

Companion to [data/workflow research](data_workflows/README.md),
[cognitive foundations](cognition.md), and
[human-computer interfaces](interfaces/README.md). This is a deliberately broad
search for relationships humans learned to express economically, not a claim
that every notation should become executable or that the survey is exhaustive.
Original-survey primary references were consulted on 2026-09-30; later
continuations carry their own consultation dates and evidence limits. Foreign forms are
illustrative; no foreign-language execution, proof checking, chemical simulation,
clinical interpretation, or user trial was performed.

## The Cognitive Exercise

The [Leibniz/Boole/Dijkstra exercise](cognition.md) asks what a representation
lets us name, combine and reason about. A useful notation can make a relationship
into an object: membership, contraction, a bond, a dependency, a claim, a rhythm.
The omission is useful only when the reader can recover its governing context.

Proposed evaluation rule:

```text
gain = relationships made local + lawful transformations made visible
cost = context required + ambiguity + hidden phase/state + recovery difficulty
```

This is a qualitative review lens, not a measured cognitive formula. Before
copying a symbol, identify its binders, universe, coordinate system, algebra,
uncertainty and authority. Ask how someone types, reads aloud, searches, diffs,
formats, explains and repairs it without the visual display.

## Breadth Map

**Evidence** means a checked source is linked below. **Exercise** means an
original mathematical/design thought experiment, not an independently surveyed
domain standard. **Existing** routes to prior bounded repo research. Depth is
unequal on purpose: the following case studies own the strongest comparisons.

| Family / concrete form | Relationship compressed | Hidden context / failure | Possible Nomi home | Basis |
| --- | --- | --- | --- | --- |
| Sets: `x ∈ A`, `A ∩ B`, `A ⊆ B` | Membership, overlap, inclusion. | Universe, equality, finite versus predicate set. | Ordinary set APIs; optional mathematical projection. | Evidence: Lean below. |
| Venn/Euler-style regions | Boolean membership combinations / asserted containment. | Empty versus unshown region; not an area/count guarantee. | Read-only region inspector with textual membership table. | Evidence: Venn below; comparison is our exercise. |
| Set builder: `{x in U : P(x)}` | Bound variable and restricted domain. | Enumeration versus a predicate on an infinite domain. | Predicate value or bounded filtering, not ambiguous collection literal. | Evidence/exercise: Lean. |
| Quantifiers: `∀x`, `∃x` | Universal/existential scope. | Empty domain, termination, witness availability. | Named finite checks; scoped proof/constraint tool if justified. | Exercise. |
| Summation/product: `Σ_i`, `Π_i` | Binder, range and aggregation. | Order, empty case, overflow, numeric algebra. | Explicit fold/reduction contract. | Exercise. |
| Einstein indices: `C_ik = A_ij B_jk` | Shared axis contracts a dimension. | Free versus bound indices, output order, shape. | Named-axis API or fenced tensor notation. | Evidence: NumPy. |
| Matrix/block notation: `[[A,B],[C,D]]` | Spatial partition and shape. | Scalar versus block, row/column convention. | Shape-aware array API and matrix view. | Exercise. |
| Named-axis reshape: `b c h w -> b h w c` | Axis identity and permutation. | Factorization metadata; equal lengths aren't equal meaning. | Validated transformation value. | Evidence: einops/xarray. |
| Dimension/unit notation: `m/s²` | Quantity dimension and scale. | Affine units, calibration and uncertainty. | Quantity library; Unicode view not mandatory literals. | Evidence: UCUM. |
| Interval/tolerance: `[a,b]`, `x ± e` | Bounds/uncertainty. | Open endpoints, statistical versus guaranteed bound. | Separate Interval/Estimate models. | Exercise. |
| Derivative/integral: `d/dx`, `∫` | Rate/accumulation relative to a variable/domain. | Regularity, discretization, boundary conditions. | Scientific model objects; no promise that AD solves every derivative. | Exercise; scientific dossier. |
| Inference rule: premises over conclusion | Local derivation step. | Assumptions, side conditions, proof versus search. | Diagnostic/proof tree projection. | Exercise; MathML binding evidence. |
| Rewrite/equational law: `f(g(x)) = h(x)` | Substitution under a declared theory. | Effects, overflow, nontermination, observational equivalence. | Inspectable lawful optimizer rules. | Exercise. |
| Semiring/sum-product exercise | One composition pattern under several algebras. | Identity, associativity and representation limits. | Explicit algebra/policy value, never inferred rewrite permission. | Exercise; case 10. |
| Commutative diagram exercise | Two composition paths agree. | Diagram depicts an obligation, not an automatic proof. | Contract view with named equality evidence. | Exercise. |
| Bra-ket exercise: `⟨u,v⟩` | State/dual pairing. | Conjugation, basis, scalar domain and convention. | Typed linear-algebra API or scoped projection. | Exercise; no quantum-language survey claimed. |
| Probability/plate exercise | Repeated variables and conditional dependence. | Independence, observation status, conditioning and model assumptions. | Explicit probabilistic model with bounded inference adapter. | Exercise; not causal identification. |
| Type judgment: `Γ ⊢ e : T` | A result relative to assumptions. | Context Γ and derivation rules. | Type/effect diagnostic tree. | Exercise. |
| Free-body/engineering exercise | Forces and constraints on a chosen system. | Boundary, sign convention, omitted interactions. | Unit/frame-aware model projection. | Exercise; no engineering certification. |
| Knot/braid exercise | Crossing and composition modulo declared equivalence. | Projection versus topology and orientation. | Scoped model/rewrite laboratory, not core operators. | Exercise; no independent knot-tool survey. |
| Typographic/poetic structure exercise | Grouping, rhythm, quotation and juxtaposition. | Cultural interpretation; layout is not unique semantics. | Annotation/presentation tools with source preservation. | Exercise. |
| Grammar/automaton: productions and transitions | Allowed forms or state changes. | Recognition versus meaning; nondeterministic transitions. | Protocol/grammar tool, not overloaded `->`. | Existing state/protocol thread. |
| Datalog clauses | Closure of facts under relations. | Recursion/progress and relation universe. | Explicit relation model or scoped tool. | Evidence: Souffle in dossier. |
| Wiring diagrams: typed ports and junctions | Composition/shared variables. | Directed causality versus undirected constraints. | Typed model with several projections. | Evidence: AlgebraicJulia. |
| Petri-net/token exercise | Availability and consumption of resources. | Concurrency versus graphical order; firing policy. | Resource/protocol exploration. | Exercise; no independent Petri-net standard review here. |
| Temporal traces/windows | Order, event-time grouping and progress. | Processing time versus event time, late corrections. | Stream model; timeline projection. | Evidence: Beam in dossier. |
| Chemical formula: `H2O` | Element counts. | Isomers, charge, bonding and physical state omitted. | Composition model, not molecular identity. | Exercise. |
| Chemical graph: `CCO`, `C1CCCCC1` | Atoms, bonds, branches and ring closure. | Traversal-dependent encoding and stereochemical model. | Validated molecular graph importer/view. | Evidence: OpenSMILES. |
| Reaction: `2 H2 + O2 -> 2 H2O` | Stoichiometric transformation. | Not a rate law, spontaneous event or simulation. | Reaction model; conservation validator. | Exercise; SBGN model distinction. |
| Biological network glyphs | Entity/process/activity relations. | Different diagram languages mean different relations. | Model-tagged network projections. | Evidence: SBGN. |
| FASTA sequence/header | Biological sequence with an identifier. | Alphabet ambiguity, sequence identity versus metadata. | Versioned sequence model and decoder. | Evidence: NCBI. |
| HGVS reference-coordinate variants | Change relative to a named reference. | Reference version, sequence kind, predicted versus observed. | Typed reference-coordinate description. | Evidence: HGVS. |
| Phylogenetic tree exercise: `((A,B),C)` | Nested ancestry hypothesis. | Topology versus evolutionary time; inferred versus observed. | Tree model with explicitly named edge meaning. | Exercise; no Newick conformance claim. |
| Interlinear gloss | Word/morpheme alignment with annotations. | Annotation is analysis, not unmediated raw evidence. | Lossless aligned annotation view. | Evidence: Leipzig rules. |
| Dependency grammar | Word IDs and labeled head relations. | Token versus word; enhanced graph versus basic tree. | Source-aligned evidence model. | Evidence: UD CoNLL-U. |
| Anaphora: “it”, “that”, “the former” | Shared conversational referent. | Ambiguous scope, stale referent, missing authority. | Suggestions resolve to explicit source/model IDs. | Exercise; conversational thread. |
| Argument attack/support graph | Competing claims and dependencies. | Acceptability under a framework isn't truth. | Evidence/review tool, never automatic semantic approval. | Evidence: Dung. |
| Versioned legal document hierarchy | Parts, references and documentary identity. | Structural representation doesn't settle interpretation. | Stable IDs and provenance-aware document tooling. | Evidence: Akoma Ntoso. |
| Provenance graph | Entity/activity/agent derivation. | Lineage isn't correctness or permission. | Inspectable evidence protocol. | Evidence: W3C PROV. |
| Statistical data cube | Dimension/measure/attribute roles. | Observation context and units. | Explicit analysis context, not hidden ambient filters. | Evidence: W3C Data Cube. |
| Geographic coordinates/regions | Geometry in a reference system. | Longitude/latitude order, projection, dateline. | Frame-aware geometry types and map projection. | Evidence: GeoJSON. |
| Musical score | Pitch, rhythm, voices and performance markings. | Layout, symbolic duration and performed time differ. | Timed event model with score/text projections. | Evidence: MusicXML; existing music thread. |
| Keyboard chord/command | Action in a context. | Focus, mode, platform and conflict. | Semantic command IDs with accessible bindings. | Existing keyboard thread. |
| Ledger/balanced-entry exercise | Conservation of recorded amounts. | Balance doesn't establish truth of a transaction. | Domain invariant/check with evidence links. | Exercise. |
| Timeline/recipe/choreography exercise | Ordered coordinated actions. | Concurrency, optional steps, cancellation. | Workflow/protocol projections. | Exercise. |

This map stretches the search without pretending every family has a mature
Nomi proposals. Unreviewed candidates cannot justify core syntax admission.

## 1. Sets And Venn: Compression Of A Universe

Lean provides typed sets and membership/subset/union/intersection notation;
these sets need not be finite enumerated collections.
[Mathematics in Lean, sets and functions](https://leanprover-community.github.io/mathematics_in_lean/C04_Sets_and_Functions.html).
Venn's original paper studies diagrammatic representation of propositions and
reasoning, not the claim that a drawing is a universal programming language.
[Venn, 1880 primary paper](https://logic-teaching.github.io/pred/texts/Venn%201880%20-%20On%20the%20diagrammatic%20and%20mechanical%20representation%20of%20propositions%20and%20reasonings.pdf).

Original exercise: U={A,B,C,D}, eligible={A,B,C}, paid={A,C}.
Unpaid eligible = eligible minus paid = {B}; outside eligible = {D}.
The full Boolean region view has a lossless nonvisual equivalent:

| In eligible? | In paid? | Region in this U | What it does NOT establish |
| --- | --- | --- | --- |
| yes | yes | A, C | Correct payment amount or payment authenticity. |
| yes | no | B | Whether payment will arrive later. |
| no | yes | empty | Impossible in every future revision. |
| no | no | D | Membership in some unspecified larger universe. |

Venn-style Boolean regions distinguish all possible membership combinations;
a containment-only drawing may omit impossible combinations. Empty, unknown
and omitted must have different renderings. Circle area must not imply counts
unless the view declares a quantitative encoding. Complement without U is
underspecified; bag subtraction and list filtering are not set difference.

**Long form:** bind U, construct finite sets, call difference/intersection,
then inspect membership per entity. **Challenger:** mathematical view of the
same model. **Experiment:** add a paid entity outside U, duplicate input IDs,
then change U. Require explicit rejection or a declared expansion policy and
text-equivalent results. Do not turn ∩ into an overloaded list operator.

## 2. Einstein: A Binder Hiding In Repetition

Explicit NumPy `einsum("ij,jk->ik", a, b)` names contraction and output axes;
its integer-label API expresses the same structure without a string. Implicit
output order, repeated labels and broadcasting rules require care. NumPy's
general array notation is not identical to the covariant/contravariant discipline
of classical tensor calculus.
[NumPy einsum](https://numpy.org/doc/stable/reference/generated/numpy.einsum.html).

Original long form for matrix multiplication:

```text
for each i in rows(A), k in columns(B):
    C[i,k] = sum over j in contracted_domain of A[i,j] * B[j,k]
```

The notational invention is binding `j` through shared occurrence. A novice can
mistake it for an ordinary free variable. A robust model names input axes,
contracted axes and ordered output axes; equal dimension lengths alone don't
establish compatible meaning. Use the oracle A=[[1,2,3],[4,5,6]],
B=[[7,8],[9,10],[11,12]], C=[[58,64],[139,154]].

Candidate calls: `tensor.contract(a, b, spec)` with a validated description;
challenger: scoped Einstein view that expands to the same description. Keep
Nomi `->` for function result types outside that scope. Test mismatched lengths,
swapped axes, accidentally repeated labels, diagonal versus sum and explicit
output order. Show the failed binder/axis in diagnostics, not only “shape error”.

## 3. Axes, Units, Coordinates And Uncertainty Are Separate

einops expresses named-axis rearrangement and factorization;
xarray aligns/broadcasts by named dimensions and coordinates.
[einops tutorial](https://einops.rocks/1-einops-basics/),
[xarray computation](https://docs.xarray.dev/en/stable/user-guide/computation.html).
UCUM supplies machine-readable unit expressions, including cases beyond simple
multiplicative scaling. GeoJSON fixes a geographic reference and coordinate
order in its format.
[UCUM specification](https://ucum.org/ucum),
[GeoJSON RFC 7946](https://www.rfc-editor.org/rfc/rfc7946).

Original Nomi distinction:

```text
shape:     3 x 2
axis:      sample x coordinate
frame:     coordinate reference/version
unit:      meter
evidence:  measured / estimated / missing, with uncertainty model
```

No single shape annotation proves all five. A temperature reading's interval
and a statistical standard deviation aren't interchangeable. Celsius values
and temperature differences need distinct conversion reasoning. Geography can
make a mathematically plausible coordinate pair refer to the wrong place.

Candidate: ordinary quantity/axis/frame types, with scoped dense notation only
after explicit calls fail. Test equal-size but mismatched axes, affine conversion,
longitude/latitude swap, absent coordinate and unit-compatible but frame-invalid
addition. An optimizer cannot erase model/version metadata merely because the
underlying buffers have compatible shapes.

### Correlated Uncertainty: Shared Origin Is Part Of The Model

> Research-depth extension checked 2026-10-04; named subexperiment
> **DW4 / shared-uncertainty**, refining question 9 and the existing axis/unit
> exercise. No measurement type, covariance API or numerical engine is admitted.

The five-way distinction above already separates units, frames, axes and
uncertainty, and the [domain map](domain_composition.md#knowledge-is-not-one-tree-or-one-truth-value)
rejects a universal confidence number. The missing composition law concerns
**which uncertain inputs are shared**. Copying a measurement value or using it
twice does not create two independent measurements. Nor do different record IDs,
equal error bars, different instruments or a provenance edge alone establish
statistical independence.

Zero covariance likewise does not by itself establish independence. A
covariance basis can suffice for a selected affine variance law without being a
complete joint-distribution description for nonlinear transformations.

Selected primary evidence: **JCGM 100:2008**, section 5.2, requires correlated
inputs to enter combined uncertainty through their covariance. Shared calibration
or reference information can correlate otherwise distinct measurements.
[GUM primary text](https://www.iso.org/sites/JCGM/GUM/JCGM100/C045315e-html/C045315e_FILES/MAIN_C045315e/05_e.html).
**JCGM 102:2011**, sections 5.6/6.2, treats vector outputs, input/output covariance
and propagation through a measurement model; linearization and propagation of
joint distributions are distinct procedures. [Primary supplement](https://www.bipm.org/documents/20126/2071204/JCGM_102_2011_E.pdf).
These editions were checked on the date above. This is selected mechanism
evidence, not a metrology conformance audit or a claim that every uncertainty
model is Gaussian, linear or reducible to a covariance matrix.

Original exact affine oracle, with deliberately stated assumptions:

```text
X has estimate 10 and variance 1 under one supplied uncertainty model
reuse that same uncertain input: Y = X - X; estimate 0, variance 0
independent X1 and X2 each have estimate 10 and variance 1:
    Z = X1 - X2; estimate 0, variance 2
```

The variance difference follows algebraically from the supplied joint model;
it is not an executed measurement study. The zero case does not prove there is
no measurement error elsewhere, that two new readings cancel, or that floating
evaluation of arbitrary expressions has exact cancellation. In a second
original model, `Xi = true_value + shared_offset + noise_i`, the readings measure
one fixed scalar measurand. Assume a zero-mean finite-variance shared offset and
zero-mean finite-variance noise terms that are mutually independent, independent
of the offset, and all have the same fixed variance. For n readings,
`Var(mean(Xi)) = Var(shared_offset) + Var(noise_i)/n`. More readings reduce only
the independent-noise contribution under these assumptions; they do not remove
the shared-offset contribution. A naive per-value error bar can conceal this
distinction even when every unit and array shape matches.

**Competing candidate contracts**, library/domain-model first:

| Candidate | Visible composition | Cost / falsifier |
| --- | --- | --- |
| Explicit joint model plus covariance basis | State input identity, covariance assumptions and transformation basis together | A marginal standard deviation is promoted to a complete joint model; invalid matrix or unsupported nonlinear approximation goes unnoticed |
| Shared latent-source/sensitivity representation | Compose affine contributions by source identity; repeated references retain the same supplied source | Independently created values accidentally share an ID, or missing correlations are silently set to zero |
| Profiled joint-distribution propagation | Retain a named joint distribution and execute a bounded established numerical procedure | Sampling each marginal separately destroys dependencies or results claim exactness beyond the profile |
| Marginal-only observation | Display one estimate and its local uncertainty with an explicit composition limit | Unsupported arithmetic automatically assumes independence instead of returning a gap/error |

None implies an uncertainty wrapper around all Nomi numbers. Metadata belongs
to a measurement/evidence boundary that needs it. Identity is a modeling fact,
not a guess from object address, equal numeric payloads or a common instrument
label. A duplicate citation has a similar shared-origin pressure, but measurement
covariance does not automatically define independence of documentary testimony.
Keep those domain laws separate.

Candidate normal form, **protocol metalanguage**:

```text
bind measurand, units/frame and input/source basis
-> state joint uncertainty assumptions and unknown dependencies
-> describe a supported transformation without resampling copied inputs
-> check compatibility, covariance/distribution validity and method limits
-> propagate under a named exact/approximate profile
-> inspect output estimate, dependency basis, uncertainty and limitations
```

For a supplied affine covariance model the candidate reference equation is
`U_out = A U_in transpose(A)` with stated axis order and units. This finite
reference law does not license arbitrary automatic differentiation, nonlinear
linearization, asymptotic confidence claims or a general numerical optimizer.
The [AI/ML numeric-program boundary](data_workflows/ai_ml.md#differentiation-is-a-transformation-with-a-domain)
owns transformability; [adaptive evaluation](data_workflows/ai_ml.md#adaptive-evaluation-feedback-is-also-a-dependency)
owns a different kind of feedback dependence.

| Program / protocol | Observation and inspection | Failure-heavy discriminator |
| --- | --- | --- |
| Beginner: subtract a measurement from its explicit copy, then compare independent readings | Same central result, different supplied dependency/variance basis | Copying changes source identity or silently resamples an input |
| Production: combine calibrated readings into a derived quantity | Units/frame, shared calibration edition, covariance basis, method and unknown correlations remain visible | Averaging claims all uncertainty vanishes although the shared component remains |
| Failure-heavy: import incomplete covariance or nonlinear transformation | Distinguish unsupported method, invalid supplied covariance, unknown dependence and nonfinite arithmetic | Missing covariance becomes zero, an impossible covariance is accepted, or approximation is advertised as exact |

Inspection should expose a compact dependency view plus a textual equivalent,
including omitted sources and assumptions; it must not fetch calibration data
or authorize a device action merely by opening the view. Candidate diagnostics
include `joint dependence unspecified; independence not inferred` and
`transformation outside affine uncertainty profile`. Report a covariance basis
with named axes, not an unlabeled matrix that can be transposed accidentally.

**Falsifiers and stop/removal criteria:** compare alias versus independent
inputs, shared offset versus fresh noise, changed calibration edition, unknown
correlation, asymmetric/non-positive-semidefinite supplied covariance, swapped
axes, singular valid covariance, incompatible units and nonlinear/nonfinite
cases. Singularity alone is not a reason to reject the repeated-input model.
Reject automatic independent composition without evidence. Stop a stronger
claim when the joint model or method's domain is unknown; retain marginal
observations. Remove generic arithmetic sugar if it conceals resampling,
approximation or covariance/source identity from a reader.

**Unperformed:** neither oracle has been executed or captured; no established
uncertainty engine, covariance checker, device adapter, differential numeric
suite or reader study was run. DW4 and question 9 remain open. These cases add
research obligations, not new successful probes to the historical inventory.

## 4. Chemistry: Composition, Structure And Process

OpenSMILES distinguishes syntax from molecular-graph meaning and encodes bonds,
branches, ring links and stereochemical details. Traversal is an encoding choice;
text equality is not a complete molecular identity rule.
[OpenSMILES v1.0 primary specification](https://raw.githubusercontent.com/opensmiles/OpenSMILES/master/opensmiles.asciidoc).
SBGN explicitly has Process Description, Entity Relationship and Activity Flow
languages; one diagram type must not silently stand in for another.
[Systems Biology Graphical Notation](https://sbgn.github.io/).

Original exercise separates three models:

```text
H2O                      composition: element counts
CCO                      graph encoding: ethanol structure
2 H2 + O2 -> 2 H2O        stoichiometry: reactants/products and coefficients
```

The equation permits a conservation check, not a reaction-rate prediction or
proof the process occurs under actual conditions. Supply kinetics, compartments,
conditions and model assumptions separately before simulation. A bond diagram
has a richer alphabet than a generic directed task graph.

Candidate: immutable Composition/MolecularGraph/Reaction descriptions,
validated importers and multiple projections. A reaction arrow belongs inside
the domain representation, never a new meaning of Nomi `->`. Test an unmatched
ring label, wrong valence under a named model, atom imbalance, and a syntactically
valid graph whose simulation lacks conditions. The inspector must distinguish
parse validity, model validity and empirical adequacy.

## 5. Biology: Names Locate Evidence, Not Just Values

NCBI FASTA documents sequence identifiers, headers and nucleotide alphabet;
HGVS descriptions locate variation against a specified reference and sequence
kind, with conventions distinguishing prediction.
[NCBI FASTA format](https://www.ncbi.nlm.nih.gov/genbank/fastaformat/),
[HGVS basics, stable 21.1.4](https://hgvs-nomenclature.org/stable/background/basics/).

Original exercise: “position 42 changed” is incomplete without reference ID,
version, coordinate convention and sequence kind. Predicted and observed changes
must not share an unlabeled certainty state. A decoded variant description is
not an inferred phenotype or clinical judgment. Sequence equality doesn't imply
sample identity, provenance or reference equivalence.

Candidate `ReferenceVersion`, `SequenceCoordinate`, `VariantDescription` and
evidence records in a domain library. Test stale references, incompatible
coordinate types, ambiguity symbols and a predicted result imported as observed.
Transfer to general Nomi tooling: source spans and data paths also require
reference/revision identity, not just integers and strings.

## 6. Linguistics: Alignment And Analysis Layers

Leipzig glossing rules align annotated words/morphemes and explicitly distinguish
analytical glossing from the source material. CoNLL-U provides ordered fields
and IDs for words, basic head relations and enhanced dependencies; tokenization
and word identity are not always one-to-one.
[Leipzig Glossing Rules](https://www.eva.mpg.de/lingua/resources/glossing-rules.php),
[UD primary CoNLL-U definition](https://raw.githubusercontent.com/UniversalDependencies/docs/pages-source/format.md).

Original extraction: retain at least raw text, segmentation, IDs, annotations,
analysis version and alternatives. A formatter or AI explanation is an analysis
view, not permission to overwrite the source. Dependency syntax does not settle
semantic intention. Natural-language pronouns can improve conversation but must
resolve to explicit IDs before edits/effects are executed.

Candidate: lossless source-aligned annotations, competing analyses and stable
references across views. Test a multiword token, disputed segmentation, stale
annotation offsets and ambiguous “change that”. Ask for a concrete referent,
not an invisible guess. No proposal for an English-like global Nomi grammar.

## 7. Arguments, Proofs And Documentary Evidence

Dung models arguments and attack relationships to define acceptability under
specified semantics. That is not a general truth oracle.
[Dung, 1995 primary paper](https://cse-robotics.engr.tamu.edu/dshell/cs631/papers/dung95acceptability.pdf).
Akoma Ntoso represents structured legal documents and references;
PROV models entity/activity/agent provenance.
[Akoma Ntoso 1.0 vocabulary](https://docs.oasis-open.org/legaldocml/akn-core/v1.0/os/part1-vocabulary/akn-core-v1.0-os-part1-vocabulary.html),
[W3C PROV-DM](https://www.w3.org/TR/prov-dm/).

Original example: a proposal claims a transform is pure, a trace provides an
example, a counterexample shows file access, and a revised contract narrows the
claim. An argument graph can preserve this dispute. A proof tree would require
declared inference rules and checked premises. An execution trace demonstrates
one run, not universal correctness. A legislative structure supplies document
identity, not a language engine's authority to interpret law.

Candidate: `Claim`, `Evidence`, `Assumption`, `Counterexample`, `Status`,
versioned links and labeled support/attack relations in research tooling. Test
missing premises, cycles, conflicting accepted claims and superseded evidence.
Use it to improve design review, not automatically accept features by vote,
graph layout, citation count or AI confidence.

## 8. Wiring And Time: The Arrow Is Not The Meaning

AlgebraicJulia distinguishes directed-machine composition from undirected
resource-sharing diagrams. Shared ports can denote relational agreement rather
than a causal “run this then that”.
[Directed machines](https://blog.algebraicjulia.org/post/2021/01/machines/),
[Resource sharers](https://blog.algebraicjulia.org/post/2021/01/resource_sharers/).
MusicXML separates a structured score description from its visual/performance
interpretations; statistical data cubes name dimension, measure and attribute
roles.
[MusicXML 4.0](https://www.w3.org/2021/06/musicxml40/),
[W3C Data Cube](https://www.w3.org/TR/vocab-data-cube/).

Original exercise: the same line could mean function application, equality of
shared variables, dependency, causal influence, temporal precedence or an attack
on an argument. Generic node-and-edge storage is fine; generic unlabeled edge
semantics are not. Musical simultaneity, workflow concurrency and physical
coupling need different laws despite similar layouts.

Candidate: typed ports and labeled relation kinds, explicit clock/progress
models, text projections and declared feedback policy. Test a cycle as recursion,
an algebraic loop and a forbidden task dependency separately. A graph renderer
must not decide execution merely because a line points right.

## 9. Presentation Is Not Semantic Content

MathML distinguishes content-oriented representations from presentation markup.
It supplies useful binding/operator structure without proving every displayed
formula has one universal interpretation.
[MathML 3 content markup](https://www.w3.org/TR/MathML3/chapter4.html).

Nomi inference: preserve the model and source mapping independently of glyphs.
A Venn diagram, tensor indices, matrix grid or molecule rendering can be an
alternative view. Bidirectional editing is a harder contract: layout-only changes
should not alter semantics; semantic edits must validate against model revision;
ambiguous layouts cannot be silently lowered into code.

The [interaction proposal](../design/interaction_model.md) owns this fork.
Read-only views first remain a hypothesis, not evidence that editing is useless.
Keyboard and accessible text routes must identify the same entities and actions.
Unicode mathematical forms here are evidence, not a requirement to type special
characters into ordinary Nomi programs.

## 10. Algebra And Quantification: Reuse Laws, Not Just Shapes

Original exercise, not a reviewed GraphBLAS implementation: the matrix pattern
`C[i,k] = combine over j of extend(A[i,j], B[j,k])` can describe ordinary
sum/product, Boolean any/and reachability composition, or min/plus path costs.
The visible shape is similar; the identities, annihilators and laws are not.
Arithmetic on finite checked integers can overflow; floating-point sum does not
justify unrestricted reassociation. A law claimed of mathematical numbers isn't
automatically a law of their machine representation.

Likewise, `for all x in U: P(x)` and `there exists x in U: P(x)` compress repeated
reasoning but say nothing about how to enumerate an infinite U. On finite empty
U, the universal check is true and the existential check false. A found witness
is not an enumeration of all witnesses; failure to find one under a timeout
isn't a proof of nonexistence. A solver, a finite iterator and a proof checker
must return distinguishable kinds of evidence.

Candidate: explicitly named domain/algebra/policy values and separate
`check_all`, `find_witness`, `solve` and proof-artifact protocols where justified.
Don't make a user-supplied equality predicate a theorem, or let a solver mint a
runtime grant. Test an empty domain, a bounded search that returns Unknown,
overflow under reassociation, Boolean versus numeric composition and an invalid
rewrite proof. DW4 can exercise the finite tensor baseline; general solver/proof
notation remains a challenger, not a new implementation requirement.

The deeper ambition is compositional: a few explicit primitives can express
many domains once their laws and context are first-class. This is more useful
than adding a separate glyph for every operation, and more demanding than
claiming that every domain is “just functions” without naming its laws.

## Synthesis: Context Made Inspectable

Repeated transferable primitives are **binding, universe, relation, shape,
identity, conservation, phase, uncertainty and evidence**. Not every primitive
needs a core keyword. Ordinary immutable models can support domain notation and
visual explanations while keeping operations/effects explicit.

| Temptation | More coherent starting point | Evidence that could justify more |
| --- | --- | --- |
| Add ∩, Σ, tensor subscripts and reaction arrows globally. | Named ordinary APIs over explicit models. | Whole-program call baseline fails comprehension/error locality in a bounded domain. |
| Make every graph a workflow. | Model-tagged relations with distinct evaluation laws. | A declared sublanguage and conformance fixtures establish safe translation. |
| Make natural language executable by default. | Resolve suggestions to explicit edits/commands with IDs and grants. | Ambiguity/recovery and adversarial authorization trials pass. |
| Make diagrams the only source. | Lossless model plus text/visual projections. | Revision-safe editing, diffs, merge, accessibility and formatting contracts. |
| Present validity as truth. | Separate parsed, well-typed, model-valid, proved and empirically supported. | Named evidence/proof mechanisms justify a narrower claim. |

Exact next comparisons are [DW4/DW7 and companion experiments](data_workflows/nomi_candidates.md).
The [notation target](../design/targets/research/notation.nomi) is an unexecuted
ordinary-call baseline. No core syntax, interpreter behavior or playground
sample changed. Broader additions should expose a new failed program or a
genuine fork; a larger bibliography alone is not progress.
