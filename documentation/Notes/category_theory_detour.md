## A brief detour: category theory

It has been about a month since the last visible update. The short explanation is straightforward: I returned to category theory after many years and ended up spending far longer there than expected.

This text is not a tutorial, nor a declaration of direction. It is a *linking note*: an attempt to explain why this detour belongs alongside the rest of the project, and why the time spent here felt like alignment rather than delay.

### Lineage, not novelty

My understanding of programming languages has always been shaped by a particular lineage: ALGOL 60, Dijkstra, Hoare, structured programming, and the influence of relational and predicate calculus.

That tradition treats programming as a discipline of reasoning. The emphasis is on structure, invariants, and clarity—not on accumulating techniques or tools. Category theory enters here not as a fashionable import, but as a continuation of the same impulse: to improve the language we use to talk about computation.

### What category theory actually changed

Category theory emerged in the 1940s (Eilenberg–Mac Lane) with a quiet shift in emphasis. Instead of organizing mathematics around elements and constructions, it organized it around relationships and composition.

Its long-term contribution was not primarily new results, but unification. Ideas that appeared different on the surface were shown to share the same shape. Once named, those shapes could be reused.

This mirrors the role logic played in programming. Logic did not merely add proofs; it gave programmers working vocabulary: predicate, variable, scope, binding, substitution, evaluation order, type, judgment. Those terms did not stay theoretical—they became practical tools for writing, discussing, and reasoning about programs.

Category theory offers vocabulary at a different level, but with a similar effect: object, morphism, composition, product, coproduct, universal property, adjunction. These words point to patterns programmers already encounter, but often only handle implicitly.

### From abstraction to practice

Seen from the ground, category theory is not about importing exotic mathematics into a language. It is about making familiar ideas precise enough to rely on.

* **Composition** captures the common intuition behind function chaining, pipelines, middleware stacks, dataflow graphs, and build systems—and insists that this glue behave predictably.
* **Products and coproducts** give a clear account of tuples versus sum types, records versus variants, and the symmetry between “and” and “or”.
* **Universal properties** provide a way to define interfaces by the problem they solve uniquely, rather than by enumerating methods and corner cases.
* **Functors** clarify what it means to transform data while preserving structure—something programmers do constantly when mapping over collections, streams, futures, or syntax trees.
* **Equational reasoning** formalizes the expectation that refactoring should preserve meaning, and that equivalent constructions should be interchangeable.

None of this requires categorical syntax to appear in the language. What it requires is design discipline: small cores, lawful composition, and abstractions that behave uniformly rather than surprisingly.

### On restraint and distillation

It is easy to impose category theory—just as it is easy to impose any powerful mathematical idea—superficially. One can graft terminology and abstractions onto a system and claim rigor without gaining clarity.

The harder task is distillation: absorbing the ideas deeply enough that they vanish into a clean, minimal interface.

This problem is familiar in systems work. Large organizations routinely accumulate layers of SaaS products, cloud services, and frameworks, exposing their combined complexity to users. The harder achievement is to absorb that complexity and present a coherent surface, as platforms like Athena or Aladdin attempt to do.

Category theory presents the same challenge. Its value lies not in visible machinery, but in the constraints it imposes on design—on what must exist, what can be derived, and what should be excluded.

### On the pause

Returning to this material has been slow and often disorienting. Intuitions fail; progress is uneven. But the clarity gained here feels qualitatively different from ad hoc progress.

The expectation is that this grounding will make it easier to project rough ideas into cleaner structures, interpolate between partial designs, and extrapolate without losing coherence.

The recent silence, then, has not been inactivity but consolidation. This detour is less a diversion than a reinforcement of foundations, very much in the spirit of the traditions that motivated this project in the first place.


# Temporary Conclusion on the Category Theory Detour

I have now spent hundreds of hours exploring category theory in the context of thinking about Nomi. Over this period, I have learned a substantial amount of terminology and become familiar with many central concepts — adjunctions, limits and colimits, functors, natural transformations, universal properties, and the categorical view of logic. My coverage has expanded significantly. I now recognize recurring structural patterns across different areas, and the internal consistency of my understanding has improved. Ideas that once felt opaque now feel interconnected; I can often see why definitions are shaped the way they are, even if I cannot yet fully command them.

At the same time, much of this knowledge remains partially digested. Some of it is still half-formed: I know the vocabulary, I can trace the formal shapes, but I do not yet grasp the ideas with enough depth and precision to responsibly embed them into the core design of Nomi. I cannot extract from category theory a foundation that feels both technically solid and conceptually earned.

Throughout this detour, I have learned from a range of voices — the structural clarity of Eugenia Cheng, the logical discipline of Peter Smith, the programmer’s perspective of Bartosz Milewski, the applied and conceptual framing of David Spivak, the type-theoretic and foundational insights of Robert Harper and the logical depth of Robert Goldblatt, along with the expository precision of Tom Leinster, the structural and conceptual sensibility of Harold Simmons, and the computational and philosophical bridges built by Noson Yanofsky. Each contributed a different lens, and together they expanded my conceptual landscape.

I remain vaguely but strongly convinced that category theory — particularly in its deep entanglement with logic — can help streamline and clarify many of the foundational ideas behind Nomi. It feels like the right altitude of abstraction. But at this stage, my understanding is not yet mature enough to integrate it in a principled way.

So this path pauses here.

I expect to return to it later, likely with sharper questions and more concrete pressures emerging from the language design itself. For now, category theory remains a background structure: suggestive, powerful, and unfinished in my hands.

This is not an ending, only a suspension. 