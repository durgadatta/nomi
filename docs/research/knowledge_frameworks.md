# General Knowledge Representation And Processing

> Status: research synthesis and bounded design handoff, consulted 2026-10-10/11.
>
> This is a broad, selective map beginning with Leibniz, not an exhaustive history
> or a claim that all knowledge has one formalization. The design owners are
> [the reasoning algebra](../design/reasoning_algebra.md) and
> [the interaction model](../design/interaction_model.md). No new syntax,
> ontology, general reasoner or proof adapter is implemented by this document.

## What We Are Trying To Unify

The useful ambition is a medium in which a person can name a question, describe
alternatives, expose assumptions, compose models, inspect consequences and revise
an explanation. Shared notation alone cannot supply shared meaning or a valid
inference procedure. A universal database, a universal calculus and a workspace
for several kinds of reasoning are different proposals.

For Nomi, the strongest candidate is **a small language for contextual descriptions
and composition, with explicit interpretations and inspectable judgments**.
Its extensibility comes from admitting structures, methods and checked bridges,
rather than introducing a keyword for every scientific theory. This extends the
existing candidate; it does not establish its minimality or completeness.

Read this document in three passes:

1. The historical map separates mechanisms and commitments worth borrowing.
2. The synthesis identifies the incompatibilities a coherent language must expose.
3. The handoff turns those findings into discriminating tasks within existing
   design passes. The unreviewed frontier remains a source-acquisition plan.

## Reading Depth And Historical Scope

The tables distinguish **T**: selected original text or primary translation;
**M**: selected official mechanism/specification; **A**: author or publisher
abstract only; and **I**: indexed original excerpt/catalog only. A selected reading
is not a cover-to-cover review or an executed implementation comparison. Dates
identify the work or pinned specification, not a page's recent crawl date.
Interpretations in the Nomi columns are our synthesis, not an author's proposal
for this language. No historical sequence below asserts direct influence unless
the primary source itself establishes it.

### Signs, Calculation, Inquiry And Augmentation

| Attempt and primary evidence | Depth and mechanism | What Nomi can borrow; what remains separate |
| --- | --- | --- |
| Leibniz, [letter to Gallois, 19 December 1678](https://www.leibniz-translations.com/gallois), and [symbols and the characteristic art](https://www.leibniz-translations.com/symbol) | I: indexed excerpts of Strickland's primary translations; the live pages exposed a script shell in this pass. Compositional signs were intended to aid discovery and judgment. | Recoverable composition is a design pressure. An ambition for universal calculation is not evidence that a universal ontology or decision procedure was achieved. |
| Leibniz, [*Meditations on Knowledge, Truth, and Ideas*, 1684](https://www.earlymoderntexts.com/assets/pdfs/leibniz1684.pdf) | T: Bennett's explicitly adapted, modernized text, with editorial interpolation; not a diplomatic translation. Symbolic compression and analysis of definitions are distinct. | A familiar name or nominal definition does not establish a possible object. Preserve definitions and obligations behind compact notation. |
| Boole, [*Laws of Thought*, 1854](https://www.gutenberg.org/files/15114/15114-pdf.pdf) | T: selected introductory/chapter material; algebraic relations, a universe of discourse, and a treatment of probability. | Make the universe and algebra explicit. This is not a modern empirical account of the whole human thinking mechanism. |
| Peirce, [*Deduction, Induction, and Hypothesis*, 1878](https://www.unav.es/gep/DeducInducHipotesis.html) | T: Spanish primary translation; different rearrangements of rule, case and result distinguish forms of inquiry. | A proposed explanation, a generalization from observations and a consequence of premises need different evidence contracts. Do not collapse them into “proved.” |
| Frege, [*Begriffsschrift*, 1879, translated preface](https://www.cs.cmu.edu/~iliano/courses/12S-CMU-80211/dl/Frege1879.pdf) | T: visually read translated preface, printed pages 5–6 and 8; Bauer-Mengelberg translation in van Heijenoort's edition. Discovery history differs from justification, and formal notation exposes hidden presuppositions. | Keep exploratory routes alongside checked derivations. A precise scientific notation can complement ordinary language without claiming to replace every human use of language. The calculus itself was not reviewed here. |
| Carnap, [*Testability and Meaning*, 1936](https://www.phil.cmu.edu/projects/carnap/editorial/latex_pdf/1936-10a.pdf) | T: selected original introduction and reducibility definitions; testing procedures, confirmation and meaning are differentiated. | Connect an empirical claim to possible testing conditions while distinguishing a test description from a successful observation. This does not admit a universal verification criterion or complete observational reduction. |
| Turing, [*On Computable Numbers*, 1936](https://www.cs.virginia.edu/~robins/Turing_Paper_1936.pdf) | T: selected original sections on computation and the decision problem. | A useful general reasoning environment need not decide every question. Search exhaustion, unsupported questions and refutation must remain distinguishable. |
| Shannon, [*A Mathematical Theory of Communication*, 1948](https://people.math.harvard.edu/~ctm/home/text/others/shannon/entropy/entropy.pdf) | T: introduction and selected formal setup; semantic questions are outside the communication problem studied. | Information quantity, compression and transmission are useful structures; none automatically measures truth, understanding or scientific importance. |
| Bush, [*As We May Think*, 1945](https://www.theatlantic.com/magazine/archive/1945/07/as-we-may-think/303881/) | T: selected original essay; the proposed memex supports associative trails through records. | Keep referable intermediate work and navigable trails. The essay is a proposal, not a measured usability result. |
| Engelbart, [*Augmenting Human Intellect*, 1962](https://www.dougengelbart.org/content/view/138/000/) | T: framework and selected scenarios; tools, language, methods and people form an interacting system. | Evaluate a whole investigation, including repair and explanation. Merely adding a visual editor does not establish cognitive benefit. |

The existing [cognitive foundations](cognition.md) retain the bounded readings
of Iverson, Dijkstra and later interaction work. Their contribution concerns how
people represent and act, not permission to equate psychological processes with
a compiler's formal calculus.

### Symbolic Knowledge, Defaults And Revision

| Attempt and primary evidence | Depth and mechanism | What Nomi can borrow; what remains separate |
| --- | --- | --- |
| McCarthy, [*Programs with Common Sense*, 1958/1959](https://www-formal.stanford.edu/jmc/mcc59.html) | A: author's account of the 1958 presentation and 1959 proceedings paper. Declarative advice is meant to participate in reasoning. | Statements and processing need not be the same object. A stored sentence requires an interpretation and inference policy. |
| Minsky, [*A Framework for Representing Knowledge*, 1974](https://dspace.mit.edu/entities/publication/0eca0164-cb5f-42de-8c86-43f54b23306d) | A, with [indexed original report text](https://courses.media.mit.edu/2004spring/mas966/Minsky%201974%20Framework%20for%20knowledge.pdf): frames organize stereotyped situations and expectations. | Structured expectations can aid modeling. Default expectations are revisable assumptions, not logical necessities. |
| Doyle, [*A Truth Maintenance System*, 1979](https://dspace.mit.edu/entities/publication/5377b306-4ecc-4687-b1f5-78cbb4a0543a) | A: original report abstract; records and maintains reasons for a program's beliefs. | Keep justifications and alternative support paths. Recording provenance alone does not implement belief maintenance. |
| Reiter, [*A Logic for Default Reasoning*, 1980](https://www.sciencedirect.com/science/article/pii/0004370280900144) | A: publisher abstract; a formal treatment of default reasoning. | A default rule needs a declared nonmonotonic semantics. Do not silently give a normal function call that behavior. |
| Brachman and Levesque, [*The Tractability of Subsumption in Frame-Based Description Languages*, 1984](https://cdn.aaai.org/AAAI/1984/AAAI84-036.pdf) | I: indexed original paper text, not a complete complexity review. | Expressivity and reasoning cost must be assessed together. “Knowledge graph” does not name a tractability guarantee. |
| Alchourrón, Gärdenfors and Makinson, [*On the Logic of Theory Change*, 1985](https://fitelson.org/piksi/piksi_22/agm.pdf) | T: selected definitions and postulates for expansion, contraction and revision of theories. | Revision is more than deleting a source row. Logical closure and choice of what to retain matter; a finite evidence ledger needs its own operational policy. |
| Lenat, Prakash and Shepherd, [*CYC*, 1985](https://ojs.aaai.org/aimagazine/index.php/aimagazine/article/view/510/0) | A: original article abstract; common-sense knowledge acquisition and brittleness motivate a large knowledge base. | Knowledge acquisition and maintenance are first-class costs. This reading does not establish that Cyc solved common sense or review its later context machinery. |
| McCarthy, [*Notes on Formalizing Context*](https://www-formal.stanford.edu/jmc/context3/context3.html), [lifting rules](https://www-formal.stanford.edu/jmc/context3/node4.html) | T: selected original context/lifting treatment. A proposition holds relative to a context; transfer requires rules. | Context is semantic, not just a folder label. A conclusion cannot inherit a different context's assumptions merely by import. |
| Sowa, [conceptual graphs](https://www.jfsowa.com/cg/index.htm) | T: author's selected overview and translation routes. Graph structure can have a logical interpretation. | A graph's edges need meanings and scope. Readability is an empirical question; the linked proposed standard is not treated here as proof of current ratification. |
| Davis, Shrobe and Szolovits, [*What Is a Knowledge Representation?*, 1993](https://groups.csail.mit.edu/medg/ftp/psz/k-rep.html) | T: original article, especially representation roles and combination. Representation concerns surrogates, commitments, reasoning, computation and human expression. | Combine theories of reasoning as well as callable mechanisms. A common object envelope alone cannot make incompatible methods coherent. |

### Logical Modularity And Mathematical Meaning

| Attempt and primary evidence | Depth and mechanism | What Nomi can borrow; what remains separate |
| --- | --- | --- |
| Goguen and Burstall, [institutions, 1990 report](https://publish.lfcs.inf.ed.ac.uk/reports/90/ECS-LFCS-90-106/) | T: [selected original definition and satisfaction condition](https://courses.grainger.illinois.edu/cs522/sp2016/InstitutionsAbstractModelTheory.pdf), alongside the report abstract; signatures, sentences, models and satisfaction under signature change. | An interpretation bridge has obligations, not just field renaming. Sentence translation and model reduction go in different directions. |
| Rabe and Kohlhase, [MMT](https://arxiv.org/abs/1105.0548) | A: authors' 2011 preprint abstract; foundation-independent modular representation with foundation-dependent checks. | Represent theories and their relationships without selecting one logic for all domains. Importable structure is not automatically a checked theorem. |
| Isabelle, [locales tutorial](https://isabelle.in.tum.de/doc/locales.pdf) | M: selected official tutorial; named contexts fix parameters and assumptions, interpretations discharge obligations. | Scoped assumptions and reusable consequences are a concrete candidate for R1/R2. Proof-system integration remains unperformed. |
| Lean, [logical connectives](https://lean-lang.org/doc/reference/latest/Basic-Propositions/Logical-Connectives/) | M: official reference; propositions and their proof terms differ from ordinary data products/sums. | A program Bool, a proposition and a proof are different contracts. Classical or constructive choices must not be smuggled into arbitrary data execution. |
| OpenMath, [2.0 standard, 2019 revision](https://openmath.org/standard/om20-2019-07-01/omstd20.html) | M: selected official object/content-dictionary/binding material. Symbols have qualified semantic dictionaries. | Preserve symbol identity, scope and declared meaning across interchange. Parsing a mathematical object does not prove a property of it. |
| Wolfram Language, [expressions](https://reference.wolfram.com/language/tutorial/Expressions.html) | M: official expression tutorial; a common structural representation supports symbolic work. | General structural manipulation is valuable. Domain equations, evaluation behavior and assumptions still require their own contracts. |
| Spivak, [functorial data migration](https://arxiv.org/abs/1009.1166) | A: author's abstract, 2010 submission/2013 revision; categorical schemas and data-migration constructions. | Schema maps can govern principled transfer. A mathematical construction does not automatically preserve every application's observation or meaning. |
| Modelica, [3.6 equations](https://specification.modelica.org/maint/3.6/equations.html) and [connections](https://specification.modelica.org/maint/3.6/connectors-and-connections.html) | M: selected pinned specification; equations describe relations, and connectors impose different potential/flow laws. | Relationships need not be a directed task graph. Model solvability and actual numerical realization are separate questions. |

Three further approaches sharpen the ontology/interchange distinction:

| Attempt and primary evidence | Depth and mechanism | What Nomi can borrow; what remains separate |
| --- | --- | --- |
| ISO, [Common Logic, 2018 edition](https://www.iso.org/standard/66249.html) | A: official abstract and scope, not the full standard. Declarative, model-theoretic information interchange is separated from proof rules and computational efficiency. | A shared logical interchange language need not prescribe the reasoning engine. Translation/checker behavior still needs an operational contract. |
| Borgo and Masolo, [foundational choices in DOLCE](https://www.loa.istc.cnr.it/old/Papers/IOShandDOLCEv16.pdf) | T: selected introduction and property/quality distinctions. Conceptual commitments distinguish instantiation from set membership and examine competing accounts of properties. | Ontological distinctions can guide domain libraries. Equal measured qualities do not imply object identity, and a class extension does not settle every meaning of a property. |
| BFO, [2020 artifact overview](https://bfo-ontology.github.io/bfo-2020.html) | M: official artifact/metadata overview, not a complete axiom review. Axioms are modularized and offered in multiple formalizations; a consistency-model artifact is supplied. | Formalization versions and translations should be referable. Publishing a consistency artifact is different from checking it, empirical validation or transferring every axiom to a weaker profile. |

A foundational ontology should therefore be an explicitly selected **theory
library**, rather than Nomi's universal superclass tree. Ontology classification,
set membership, nominal runtime typing and structural compatibility must have
named correspondence before one can substitute for another. For a concrete
counterexample, two specimens with equal reported lengths remain different
specimens; identical observed fields do not establish owner identity. A reusable
quality model can express that distinction without making all ordinary records
carry philosophical commitments.

The [scientific-model evidence](scientific_models.md) already owns
the selected mechanics, symbolic/AD, differential-form and solver comparisons.
This history adds a theory-translation lens; it does not restart those reviews.

### Shared Knowledge, Uncertainty And Learned Processing

| Attempt and primary evidence | Depth and mechanism | What Nomi can borrow; what remains separate |
| --- | --- | --- |
| W3C, [RDF 1.1 semantics](https://www.w3.org/TR/rdf11-mt/) | M: selected entailment and reification sections. A described statement is not thereby asserted. | Keep mention, assertion and inference distinct. An IRI or graph name is not a universal authority or identity decision. |
| W3C, [OWL 2 primer, second edition](https://www.w3.org/TR/owl2-primer/) | M: open-world reasoning and individual equality sections. Missing statements need not be false; different names need not denote different individuals. | Explicitly choose identity and completeness assumptions. Nominal Nomi owners and ontology individuals must not be equated by spelling. |
| W3C, [SHACL](https://www.w3.org/TR/shacl/) | M: selected graph-validation contract. | Validate a declared graph against declared shapes. Passing validation is not entailment of arbitrary facts or truth about the world. |
| W3C, [SKOS](https://www.w3.org/TR/skos-reference/) | M: selected concepts, labels and mapping properties. | Vocabulary alignment is useful without asserting entity identity. A concept match is not a license for unrestricted substitution. |
| W3C, [PROV-DM](https://www.w3.org/TR/prov-dm/) | M: selected entity/activity/agent and derivation model. | Preserve origin and derivation. Provenance does not itself establish authenticity, independence or correctness. |
| W3C, [RIF overview](https://www.w3.org/TR/rif-overview/) | M: overview of rule dialects, including logical and production-rule distinctions. | Rule interchange needs a dialect and execution/entailment contract. Serialized rules do not share a universal schedule. |
| W3C, [SPARQL 1.1 query](https://www.w3.org/TR/sparql11-query/) | M: selected dataset, negation and solution-sequence material. | Absence in one query dataset has a scoped meaning; result multiplicities matter. Query absence is not universal negation. |
| W3C, [OWL-Time](https://www.w3.org/TR/owl-time/) | M: selected instants, intervals and temporal reference systems. | Time qualifications belong in knowledge models. Equal-looking clock values need compatible reference systems. |
| Zadeh, [*Fuzzy Sets*, 1965](https://doi.org/10.1016/S0019-9958%2865%2990241-X) | A: indexed publisher abstract; classes with graded membership. The full text was not accessible in this pass. | Membership grades need their own semantics; do not reinterpret them as the probability that a crisp proposition is true. Later fuzzy/possibility systems remain unreviewed. |
| Jaynes, [*Probability Theory*, author draft](https://bayes.wustl.edu/etj/prob/book.pdf) | T: selected draft introduction and conditioning setup, not a review of the later published edition. | Plausibility depends on supplied information and assumptions. A probability is not a deductive certificate. |
| Pearl, [*Causal Inference in Statistics: An Overview*, 2009](https://ftp.cs.ucla.edu/pub/stat_ser/r350-reprint.pdf) | T: selected structural-model and intervention setup. | Observation and intervention ask different questions. A fitted predictive relation cannot silently become a causal mechanism. |
| ProbLog, [official introduction](https://dtai.cs.kuleuven.be/problog/) | M: official probabilistic-logic examples. | Logic and probability can compose within declared semantics. Probabilistic facts require dependence and query assumptions; they are not arbitrary confidence annotations. |
| Mikolov and colleagues, [word representations, 2013](https://arxiv.org/abs/1301.3781) | A: author abstract; continuous representations evaluated on language tasks. | Similarity can retrieve candidates. Proximity is not logical identity or an entailment rule. |
| Vaswani and colleagues, [Transformer, 2017](https://arxiv.org/abs/1706.03762) | A: author abstract; attention-based sequence architecture and reported translation evaluation. | Learned transformations are one processing method, not evidence that all reasoning is sequence prediction. |
| Lewis and colleagues, [RAG, 2020](https://arxiv.org/abs/2005.11401) | A: author abstract; parametric generation combined with retrieved material. | Retrieval supplies material for examination. A generated answer with a citation is not a proof, a verified observation or permission to act. |

## Synthesis: Six Distinctions The Language Must Preserve

### 1. A Representation Is A Commitment, Not The Represented World

An entity identifier, a type definition and a mathematical model answer different
questions. A model intentionally omits features. A type may classify allowed
program values without asserting that a real-world specimen exists. A measurement
links a process and instrument to an observation; it is not a transparent copy of
reality. A symbol's printed name cannot settle any of those distinctions.

Use ordinary typed descriptions with owned references, qualified definitions and
explicit interpretation. Keep mathematical inhabitance, runtime construction,
observation and identity reconciliation as separate judgments. Do not require
every ordinary record to carry an ontology.

### 2. Inference Policies Are Part Of The Question

Classical deduction, constructive proof, default reasoning, finite query negation,
probabilistic inference and causal inference cannot safely share an undeclared
meaning of “therefore.” Conflicting premises also require a policy: unrestricted
classical consequence and a contradiction-tolerant system behave differently.
The contradiction-tolerant alternatives are a frontier below, not reviewed proof
adapters or a newly accepted Nomi logic.

A reasoning profile should declare the relevant signature, admissible statements,
premises, identity/negation rules and checker contract. Profiles may differ in
their result types. A query result, a proof obligation and a posterior distribution
must not be squeezed into one global `Truth` or confidence enum. The existing
language's ordinary Booleans and control flow retain their own semantics.

### 3. Translation Needs A Preservation Claim

The institutions perspective gives a particularly useful test. For a signature
map `phi: A -> B`, its sentence translation goes forward while model reduction
goes backward. Under the required satisfaction law:

```text
B_model satisfies translate(phi, A_sentence)
    iff reduce(phi, B_model) satisfies A_sentence
```

This is a model of a checked relationship, not a law for every adapter. A schema
projection can lose facts. A coordinate map can have a local inverse but no global
inverse. An approximate solver can preserve a bound instead of exact equality.
An ontology alignment can preserve only specified queries. Declare whether a
bridge is an equivalence, a one-way sound translation, an approximation or an
unchecked correspondence, including its domain and obligations. Preservation
claims must name the particular judgments they cover.

This refines Nomi's checked composition: **composing functions is not automatically
composing their interpretations or transporting their evidence**.

### 4. Discovery And Justification Have Different Lifecycles

A person or learned model may propose a conjecture, retrieve an analogy or suggest
an experiment. A reasoner may derive a consequence. An instrument may produce an
observation. Keep each contribution's source and method without pretending one
generic evidence score orders them all.

Separate exploration branches from asserted premises. Retain reasons and revision
dependencies. If a premise is withdrawn, invalidate judgments that relied on it;
do not withdraw an independently justified conclusion merely because one support
path disappeared. Logical contraction, measurement correction and replacement of
a source file need different policies. Immutable history supports examination,
but does not choose the best current belief by itself.

### 5. A Description Does Not Select Its Engine

Reasoning plans and mathematical descriptions can be passive data. Realization
requires an explicit method and authority. A proof search, numerical solve, query,
simulation or laboratory action has its own costs, capabilities and result shape.
Even an engine-free workflow cannot generally certify its real-world conclusions
before observations exist. It can check structure, declared laws and conditional
consequences without supplying those observations.

Keep resource limits and partial results visible. A sound but incomplete method
can return no conclusion. A timeout is not falsity. A remote knowledge query is an
effect; opening an explanation of a captured answer should remain passive.

### 6. Human Understanding Is A Whole Activity

The user should be able to ask “why?”, “under which assumptions?”, “what changed?”
and “what would distinguish these alternatives?” before choosing a specialist
engine. Useful views include source, derivation, model comparison, units and
reference systems, dependency changes and unresolved obligations. These are
projections of qualified objects, not interchangeable pictures of a universal IR.

Human trials must include wrong assumptions, contradictory reports, incomplete
models and repair. Proof strength alone does not establish ease of understanding;
an attractive visualization alone does not establish semantic soundness.

## Interpolate From Nomi, Extrapolate Beyond It

The current [foundational audit](../design/reasoning_algebra.md) proposes contextual
terms, checked composition and explicit judgments. Its six scientific families
are candidate library structures. This research gives **context** more precise
dimensions without adding a seventh scientific primitive:

| Existing foundation | Refinement from this history | Composition it enables |
| --- | --- | --- |
| Contextual terms | Scope, qualified symbols, interpretation, premise set and theory revision remain distinguishable. | A reused model has stable references without inheriting unrelated assumptions. |
| Checked composition | Separate type/completion compatibility from preservation of selected semantic judgments. | An exact map, a model translation and a lossy projection can compose with visibly different guarantees. |
| Explicit judgments | Attach the question, profile, premises, method, artifact and revision dependencies. Keep profile-specific results. | Exact identity, empirical fit and a suggested explanation can be inspected together without becoming interchangeable claims. |
| Engine-free descriptions | Describe a question and possible methods before selecting an implementation. | Validate a proposed investigation's interfaces and obligations before spending compute or obtaining measurements. |
| Scoped execution | Preserve actual owners, effects, cleanup and completion. | A laboratory or remote retrieval action cannot be authorized by a theoretical context import. |
| Referable intermediates and views | Name theories, alternatives, premises, transformations, findings and unresolved steps. | A person can revisit an explanation and identify precisely which change invalidated it. |

The extrapolation is a **reasoning workspace** assembled from ordinary libraries:
theory descriptions, qualified statements, interpretation bridges, method plans,
evidence records and revision-aware views. It may combine deductive, numerical,
probabilistic and learned methods, but each method owns its contract. This is a
research direction, not a claim that those components exist today.

Avoid both extremes: a global ontology that every program must inhabit, and a
collection of unrelated engines whose answers happen to share a JSON envelope.
The coherence mechanism is explicit composition with declared correspondence and
preservation obligations. The ordinary program remains a program, with functions,
data, choices, effects and scopes; a modeling library adds obligations only when
the user chooses it.

## Whole-Activity Discriminators

### Scientific Explanation: Is A Fading Oscillation Dissipative?

Keep separate the ideal conservative oscillator, a damped model, the observation
process and a possible sensor drift. Exact conservation in the ideal description
is conditional on that model. A fitted fading amplitude does not by itself choose
between damping and instrumentation. Compare hypotheses, display required
assumptions and identify an experiment that could separate them. A learned
suggestion may propose the comparison; it cannot certify it.

The existing exact polynomial lab checks the ideal energy identity and a damped
counterexample without observations. It does not implement measurement models,
causal identification, a damping fit or experiment selection. Those distinctions
must survive any future unified interface.

### Ordinary Reporting: Does No Invoice Mean No Debt?

In a declared complete invoice snapshot, a scoped query can report no matching
invoice. In an incomplete imported knowledge base, the absence may leave the
question unresolved. Neither statement proves that no debt exists. A user should
see the dataset revision, completeness assumption and scope of the answer. This
is the ordinary-programming counterpart to scientific assumptions, not a physics
feature.

### Evidence Repair: Two Reports, One Withdrawn Source

Store both reports as reports before treating either as a premise. Display a
conflict without deriving arbitrary conclusions. A chosen deductive context may
require consistency checking; another method may tolerate a specified conflict.
Withdraw one report, retain the history, and recompute which conclusions still
have independent support. The governing method is explicit; there is no automatic
global overwrite of “truth.”

### Representation Change: From Exact Algebra To Simulation

The identity `(a + b) + c = a + (b + c)` in the rational polynomial profile is not
an unrestricted IEEE floating-point rewrite. Preserve the exact theorem in its
original profile; require a separate conversion and numerical error contract.
Likewise, exporting a nominal space as anonymous arrays loses identity unless a
bridge retains it. An adapter's ability to execute is not evidence of exact
semantic equivalence.

## Gaps And The Next Executable Work

This extends existing R0-R5 and interaction work, not a second implementation
roadmap. “Designed” below does not imply implemented support.

| Gap | Current evidence | Next discriminating artifact and owner |
| --- | --- | --- |
| General contextual binding and theory parameters | A separate pure-term lab now compares nominal and locally nameless binders with source spans and independent evaluation; Nomi/domain migration remains open. | **R1:** compare scoped references and locally nameless binders on the ordinary report and a parameterized map; test alpha-renaming, capture, stale references and source reconstruction. |
| Mention versus asserted premise | Research distinction; no general knowledge-statement lab. | Extend **R1** with a tiny finite premise ledger. Quoting/importing a statement must not assert it. Remove one of two supports and replay dependencies. Keep the policy explicit. |
| Interpretation and judgment profiles | One fixed exact rational-polynomial profile and separate domain labs. | **R2:** publish profile inputs/results and rule-provider obligations; reject an exact-to-float theorem transfer lacking a preservation contract. |
| Checked theory bridges | Exact map composition and supplied two-sided inverse checks only. | **R2:** replay a parameterized theory interpretation with an established symbolic/proof tool; include a deliberately invalid mapping and a one-way, non-equivalent mapping. Do not call arbitrary graph export a theory morphism. |
| Revision and alternative justification | Existing interaction probes model some stale-context boundaries; no general truth-maintenance implementation. | Extend **HX2/HX8** and R1 with independent support paths, conflicting reports and premise withdrawal. Match against a hand-written finite oracle. |
| Constraints, uncertainty and measurements | Selected scientific descriptions; no universal probability/causal/measurement layer. | **R3/R4:** preserve different types for constraints, empirical likelihood and approximation regimes. Reuse scientific owners and admit one boundary at a time. |
| Search and method selection | No general reasoner or proof-search planner. | In **R2**, use bounded methods with profile-specific incomplete/unsupported results. Assert that exhausting a budget never fabricates refutation. |
| Human explanation and discovery | Prepared interaction trials; no participant evidence for this redesign. | **SP0/R5:** compare explicit source with source plus assumption/derivation views on the four tasks above. Include correction, delayed recall and unfamiliar-domain transfer. |

An initial pilot should use finite propositional premises and explicit supplied
rules, not attempt general first-order theorem proving, ontology reconciliation or
belief revision optimization. Keep it under `tools/`, separate from the parser and
interpreter. Its removal gate is failure to improve scoped explanations or a
requirement for an ever-growing universal object. Implementation should follow
the binder comparison and independent oracle, not precede them.

## Corner Cases To Carry Into Those Artifacts

1. Same label, different owned object; different labels, possibly the same
   ontology individual. Neither resolution follows from spelling alone.
2. A quoted false statement is safe to describe; importing it does not assert it.
3. An existential consequence need not supply a named or constructible witness.
4. Missing rows, SQL null, an unknown proposition and an unsupported operation
   have different meanings and result contracts.
5. A shape-valid graph can have inadequate world coverage or inconsistent
   ontology commitments. Validation and entailment are different questions.
6. A default can be defeated by new information; a monotonic proof is still valid
   from its recorded premises even when those premises cease to be endorsed.
7. Removing one premise may leave a conclusion supported elsewhere. Revision
   must track support, not merely the first derivation encountered.
8. A classical proof from inconsistent premises is not acceptable world evidence.
   Consistency checks and conflict-tolerant methods are profile choices.
9. Local coordinate invertibility does not establish global theory equivalence.
10. Query bags, set membership, ontology identity and nominal owner identity must
    not share an undeclared equality operation.
11. Probability, fuzzy membership, similarity and instrument uncertainty are
    different quantities. The latter alternatives require additional research.
12. Two copies of the same originating report are not independent evidence.
13. An observation time, publication time and current query time can differ.
14. A numerical counterexample under another profile does not refute an exact
    theorem in its own profile; it may refute a proposed bridge.
15. A proof-search timeout cannot be displayed as “false.”
16. Proof-carrying input still needs a trusted checker and matching context;
    provenance alone supplies neither.
17. A theoretical assumption about permission cannot grant actual execution
    authority. Knowledge imports do not transfer capabilities.
18. A plausible analogy or retrieved citation remains a candidate until the
    relevant checking or observational process supports its claim.

## Unreviewed Frontier: Expand By Questions, Not By Names Alone

The map above is intentionally incomplete. These families are needed before
claiming a history of *all* general frameworks. The first-source tasks below are
not completed reviews, and no new design claim depends on them.

| Frontier | Source acquisition and question for a subsequent pass |
| --- | --- |
| Frege's calculus; Russell and Whitehead; Hilbert, Gödel, Tarski and Church | Beyond the translated Frege preface above, the [1879 original catalog/OCR listing](https://zenodo.org/records/6330677) was located but its full PDF was not read. Acquire the original formal sections and other texts, then compare binding, reference, model/metalanguage distinctions and precisely scoped expressivity/decision limits. |
| Carnap's construction program, Neurath and unity of science | The selected Carnap testing paper above does not review these programs. Read their original construction/unification proposals. Does coordination require a single reduction vocabulary, or can separately interpreted disciplines remain connected? |
| Otlet, Ranganathan and faceted classification | Acquire original documentation/classification works. Compare enumerative versus compositional indexing, provenance and historically contingent categories. |
| Grassmann, Bourbaki and Lawvere | Read primary structural constructions, including Lawvere's functorial-semantics thesis. Determine which algebraic universalities help a practical library and which demand burdensome prerequisites. |
| General systems, cybernetics and control | Acquire Bertalanffy and Wiener originals. Distinguish feedback, observability and model boundaries from universal ontological claims. Connect to dynamical/control owners. |
| GPS, Soar, ACT-R and scripts | Review original cognitive-architecture/problem-solving work. Separate an executable architecture, an empirical cognitive model and an interaction design hypothesis. |
| Formal concept analysis, lattices and classification | Obtain original FCA treatments. Compare extent/intent closure with probabilistic categorization, nominal types and ontology subsumption. |
| Fuzzy/possibility theories, evidence theory and contradiction-tolerant logics | Read beyond the Zadeh abstract above, then Dempster/Shafer, Belnap and argumentation originals. Compare actual update and consequence rules; do not package their numbers as generic confidence. |
| Algorithmic information, learning and discovery systems | Acquire Solomonoff/Kolmogorov sources and original DENDRAL, BACON, AM/EURISKO reports. Separate compression, induction, heuristic discovery and validated scientific explanation. |
| Active inquiry and automated scientific workflows | Review primary experiment-design and autonomous-laboratory systems. What supports intervention choice, stopping, safety and independent replication? |
| Formalized mathematics, ontologies and scientific model exchange | Beyond the selected Common Logic/DOLCE/BFO material above, read full axioms and mappings, SUMO/GFO/UFO, selected HoTT chapters, further proof-assistant kernels, OMDoc/MMT mechanisms, CellML units/imports and scientific exchange standards. Located catalogs/abstracts are not completed integrations. |
| Situated, embodied and culturally distinct knowledge practices | Select primary work and community-authored accounts; compare tacit/interactive know-how with formal statements. The selected Western computational lineage cannot stand for all human knowledge. |

The next research pass should choose a concrete failing task from this frontier,
record the original mechanism and its scope, and compare it against the current
candidate. It should revise the candidate when necessary, rather than force every
system into the same six scientific headings. The goal is a coherent language
that helps people discover and explain, not a catalog that grows without tests.
