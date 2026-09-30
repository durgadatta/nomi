# Computation As A Cognitive Instrument

> Status: foundational research and Nomi hypotheses; no new syntax admitted.

Read this before the [interface threads](interfaces/README.md), then the
[interaction proposal](../design/interaction_model.md) and
[redesign agenda](../design/redesign_agenda.md). Sources were consulted on
2026-09-29/30. Historical interpretation, Nomi inference, and untested claims
are distinguished below. This is not a claim to exhaust either philosophy or HCI.

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

## A Cognitive Exercise, Before A Syntax Exercise

Work through each row using the invoice, a batch import, and a cancellation-heavy
job. Record the explicit Nomi long form, an alternative representation, the
fact gained, and the fact hidden. These are proposed exercises, not completed
user studies.

| Idea | Exercise | Consequence to investigate |
| --- | --- | --- |
| Identity versus location | Sort invoice rows without changing the selected item | Stable domain IDs; positions are view coordinates. |
| Meaning versus presentation | Rename a label without changing a binding | Symbol identity and lossless source matter more than rendered text. |
| Extension versus intention | Compare a list of results with a recipe for producing them | Distinct collection, stream, and plan types. |
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
