# Scientific Models As Instruments For Thinking

> Status: primary evidence and designing experiments, 2026-10-10. Mechanism
> synthesis under language-coherence, not a specification or human-study result.

The purpose is to connect domains through the activity of thinking.
Physics tests whether Nomi helps a person distinguish concepts, express a
model, derive a consequence, compare explanations and revise understanding.
Read [the design proposal](../design/scientific_discovery.md) for its five
candidate modeling contracts, and [cognitive foundations](cognition.md) for the
broader evidence. This note consolidates mechanisms rather than adding a
separate language review for every scientific package.

## Primary Mechanisms And Nomi Inferences

Sources were consulted on 2026-10-10. Stable mathematical distinctions are
separated from current API/version details. The Nomi consequences are proposed
design judgments; no cited system certifies Nomi semantics or usability.

| Primary evidence | Mechanism observed | Design consequence to investigate |
| --- | --- | --- |
| [Kirsh and Maglio, 1994](https://doi.org/10.1207/S15516709COG1804_1) | In Tetris, some external actions help reveal information rather than directly advance a plan | Inspection and rearrangement can be valuable actions without running a computation; task-specific evidence is still needed |
| [Victor's ladder of abstraction](https://worrydream.com/LadderOfAbstraction/) | Interactive movement between concrete trajectories and broader representations | Preserve a path from a summary/equation back to a particular case and its assumptions; a design demonstration is not a controlled usability result |
| [OpenMath overview](https://openmath.org/technical/), [content dictionaries](https://openmath.org/cd/) | Mathematical symbol meanings are qualified by dictionaries; application and binding objects are distinct | Symbol identity, binders and theory vocabularies need explicit contracts; importing a format does not establish semantic alignment |
| [ModelingToolkit initialization](https://docs.sciml.ai/ModelingToolkit/stable/tutorials/initialization/) | DAE initialization must satisfy algebraic constraints; transformations can change the solver state | Initial conditions and guesses remain distinct, and a structural transformation retains reconstruction maps and initialization obligations |
| [UFL form language](https://docs.fenicsproject.org/ufl/main/manual/form_language.html) | Variational forms retain function-space arguments, coefficients and interior/boundary/facet measures | A weak form is a typed mathematical object, not merely a callback returning a matrix; boundary terms and measures survive lowering |
| [PETSc time stepping](https://petsc.org/release/manual/ts/) | Time integration handles semi-discrete ODE/DAE forms; spatial discretization is already supplied | Continuum model, spatial discretization and time integration need different identities and error claims |
| [xTensor abstract indices](https://xact.es/Documentation/HTML/HTMLLinks/xTensorRefGuide.nb_3.html), [covariant derivatives](https://xact.es/Documentation/HTML/HTMLLinks/xTensorDoc.nb_39.html) | Abstract indices differ from components; a general connection need not be metric-compatible | Tensor variance, bundle and connection assumptions cannot be inferred from array shape or a derivative name |
| [SymPy quantum commutators](https://docs.sympy.org/latest/modules/physics/quantum/commutator.html) | Ordered operator products and unevaluated commutators have explicit algebraic rules | Scalar commutative normalization is a named profile, never a universal expression simplifier |
| [SciML algorithm interpretations](https://docs.sciml.ai/SciMLBase/stable/interfaces/Algorithms/) | Itô and Stratonovich interpretations differ; changing interpretation can require drift correction | Stochastic integral meaning belongs to the problem contract and transformations, not a hidden solver default |
| [PySINDy weak/integral examples](https://pysindy.readthedocs.io/en/latest/examples/12_weakform_SINDy_examples/example.html) | Weak formulations can avoid high-order differentiation of noisy observations; candidate libraries and prediction meanings matter | Candidate grammar, preprocessing, test functions and selection history remain part of a discovery result |
| [Structured versus decorated cospans](https://arxiv.org/abs/2101.09363) | Mathematical frameworks compose open systems through boundaries under stated hypotheses | Compare boundary-based model composition with directed function composition; do not impose category-theory notation on ordinary users |
| [FMI specification](https://fmi-standard.org/docs/main/) | Model Exchange, Co-Simulation and Scheduled Execution expose different interface contracts | An adapter declares what owns integration, events, state and scheduling; packaging compatibility does not prove mathematical equivalence |

The preceding proposal also retains the primary evidence for quantity kinds,
joint uncertainty, JVP/VJP differentiation, explicit assumptions and small
proof checkers. Those are linked at their detailed design consequences rather
than duplicated here.

## Genuine Forks

| Question | Credible choices | Discriminator and retained cost |
| --- | --- | --- |
| Mathematical identity | Stable named IDs with scoped binders; locally nameless/de Bruijn terms with a name projection | Same-spelled nested variables, capture avoidance, alpha-equivalence, readable diagnostics and repair across revisions |
| Space checking | Nominal quantity families plus explicit conversions; richer dimension/axis/frame constraints | Equal dimensions with different kinds, affine origin changes, unknown axes and incompatible coordinate frames; quantify annotation burden |
| Scientific artifact | Domain-owned mathematical model; generic object envelope with a domain validator | Cyclic constraints, binders, partial descriptions, adapters and independent replay; a nominal graph alone must reject no more than it knows |
| Algebraic transformations | Fixed terminating canonical fragment; bounded proof-producing rewrite search | Unsupported theory, cyclic rules, certificates, resource limits and changed premises; search success cannot establish checker completeness |
| Differential meaning | Symbolic/formal derivation; AD of a supported executable graph; sensitivity of an implicit/continuous solution | Nonsmooth branches, events, custom rules, different discretizations and complex conventions; these meanings stay distinguishable |
| Observation dependence | Named-source linear propagation; explicit joint probabilistic/interval models | Shared calibration, nonlinear transforms and absent covariance; no independence default and no interchangeable interval/posterior display |
| Primary representation | Text, structured mathematical workspace, or mixed editing | Creation, incomplete ideas, contradiction, baseline comparison, revision and handoff; count synchronizing/annotation/accessibility costs |
| Model composition | Directed typed outputs/inputs; open components joined by boundary relations | Circuit conservation, feedback, redundant equations and initialization; directed wiring cannot silently settle an acausal problem |

No fork is closed by this evidence pass. A bounded implementation can settle an
admitted fragment while leaving the broader representation choice open.

## Prepared Whole-Activity Comparisons

Each task has one supplied question, the same named objects in every candidate
view, a positive expectation and a failure case. These are prepared oracles,
not measured human outcomes or scientific software conformance.

| Task | Positive expectation | Counterexample or missing fact |
| --- | --- | --- |
| Explain a fading oscillation | Distinguish damping prediction from measurement-gain drift | Good fit to one candidate does not eliminate another explanation |
| Add damping to an ideal oscillator | Retain the new energy-dissipation claim and invalidate old conservation evidence | A source-only diff hides which scientific conclusion changed |
| Initialize a constrained pendulum | Check position and velocity constraints before integration | Correct position with incompatible velocity remains inconsistent |
| Derive a diffusion weak form | Preserve trial/test spaces, boundary terms and orientation | Dropping a nonzero boundary flux changes the problem |
| Change tensor coordinates | Apply a named transformation with its valid chart domain | Equal component-array sizes do not imply the same vector |
| Reorder quantum factors | Require an admitted commutation relation | Ordinary scalar sorting changes an operator product |
| Change stochastic solver interpretation | Transform the drift where the admitted conversion requires it | Switching only a method label changes the modeled process |
| Discover a law from noisy data | Retain candidate basis, data preprocessing and selection/evaluation history | In-sample fit plus dimensional consistency does not establish the law |
| Transfer a reasoning pattern to another domain | Reuse named baselines, premises, comparisons and revisions | An analogy cannot import a physics conservation law into an institution's policy |
| Hand off an unfinished investigation | Show the question, surviving evidence, contradictions and next discriminator | A polished explanation hides a missing observation or unproved premise |

For the constrained pendulum, the position constraint `q·q = l²` also yields
`q·v = 0` under the declared constant-length differentiable model. A supplied
initial position can satisfy the first while its velocity violates the second.
This algebraic example explains the prepared refusal; it is not a general DAE
index-reduction theorem.

## Quality And Admission

Keep a source-mechanism citation next to each extracted consequence. Preserve
formal, numerical, empirical and human-comprehension evidence separately.
An independent arithmetic checker can validate a stated formal identity; it
cannot check whether people understand the model, whether the model is
well-posed, or whether its premises describe nature.

The design owner orders SP0-SP5. The first exact formal experiment should expose
its assumptions and unsupported operations, not advertise a symbolic physics
engine. The [bounded probe](../design/scientific_discovery.md#try-a-formal-consequence-without-inputs)
now runs dimension/formal-polynomial witness checks with independently replayed
conditional/unknown outcomes and named claim explanations. This is evidence for
that fragment; general spaces/binders and actual human comparisons remain open.
Use reference/identity/revision helpers from the generic framework only
when their contracts match. Adapter round trips, mathematical semantic
alignment and actual human trials retain separate admission gates.

## Foundational Algebra Evidence

The user's minimal-algebra pivot challenges the existing six execution families,
rather than proposing six more language features. The
[redesign comparison](../design/reasoning_algebra.md) distinguishes a contextual
term foundation from supplied mathematical structures. Sources checked on
2026-10-10; the recommendations below are Nomi design inferences.

| Primary source | Mechanism | Consequence and limit |
| --- | --- | --- |
| [Blute, Cockett and Seely: differential categories](https://www.math.mcgill.ca/rags/difftl/difftl.abstract.html) | Differentiation is additional coherent structure on a categorical setting | Composable arrows alone do not derive differentiation. Compare explicit rule providers, not a universal `differentiate` compiler instruction. |
| [Cockett and Cruttwell: differential bundles and tangent categories](https://arxiv.org/abs/1606.08379) | Bundle and tangent constructions support structural differential geometry | Separate abstract spaces/bundles from coordinates. This evidence does not make a finite polynomial representation a manifold checker. |
| [Sussman and Wisdom: SICM, Lagrangian mechanics](https://tgvaughan.github.io/sicm/chapter001.html) | Executable descriptions compose paths, action and variations; symmetry supplies conservation in a stated variational setting | Use the whole derivation as a challenger. Retain admissible variations and theorem hypotheses; no `action` keyword or general conservation from any symmetry. |
| [SICM, Hamiltonian mechanics](https://tgvaughan.github.io/sicm/chapter003.html) | Quadratic Legendre construction explicitly solves for velocity using an invertible matrix | Check an inverse candidate before transporting descriptions. Singular or merely locally invertible fiber derivatives need a different contract. |
| [NIST DLMF, section 2.1](https://dlmf.nist.gov/2.1) | Order symbols, expansions and uniformity have defined regimes; differentiated asymptotics need extra conditions | Preserve exact remainder first, then attach qualified bound/order evidence. Truncation is not convergence or numerical error evidence. |

### A Smaller Core Is A Hypothesis, Not An Encoding Contest

Compare (a) execution families plus domain libraries, (b) lambda/variant
encoding, (c) bare objects/arrows and (d) contextual terms/composition/judgments.
Use the same ordinary report, two scoped maps, constrained variational model
and perturbation task. Count independent rules, annotation burden, hidden
premises, diagnostic repair steps and unsupported operations. Counting three
headings against six establishes no minimality result.

The closed [map experiment](../../tools/reasoning_algebra.py) establishes finite
formal identities without supplied inputs. Tangent lifting and substitution
operate on immutable scoped descriptions; exact realization is separate.
Fourteen [worked judgments](../../tools/reasoning_examples.py) exercise the
requested chains at bounded slices. Tests include independent exact arithmetic,
damping, singular inversion, stationary saddles and changed revisions.
Continuum variation, cotangent transport, asymptotic validity and independent
symbolic certificate replay remain unimplemented.

The next discriminator is R1/SP1: compare scoped-reference and locally nameless
binder artifacts on ordinary and scientific terms, including capture avoidance
and readable repair. R2/AF2 then uses an established symbolic/AD adapter and
independent checks; this is not a replacement general AD engine.
