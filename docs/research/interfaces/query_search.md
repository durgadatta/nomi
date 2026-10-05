# Query And Search: Evidence Has A Domain

> Status: Nomi hypotheses grounded in relational evidence already reviewed.

## Evidence And Pressure

The [SQL review](../languages/sql.md) and
[collection comparison](../features/collections.md) own checked relational
mechanisms. Facets, pivot views, and ranked retrieval are additional interface
probes: each helps a person ask a question without spelling an execution loop.
They should not be treated as identical implementations of selection.

## Cognitive Distinctions

An exact query over a closed snapshot can return an empty set. A search system
may instead have incomplete coverage, a threshold, or uncertain ranking. "No
result" is not universally evidence that no matching object exists. Grouping,
ordering, duplicates, absence, and pagination also change what a displayed
table means. Nomi needs types and explanations for these distinctions before
a pleasant query notation can be judged coherent.

## Nomi Normal Form And Placement

Start with ordinary `filter`, `map`, and explicit aggregation on owned data.
A table-plan library may build a typed expression value, explain its schema
and execution strategy, then execute with a supplied capability. A retrieval
library should return coverage/provenance and ranking information appropriate
to its contract. Never make generic `|>` imply remote query execution.

**Adapt:** inspecting schema and intermediate relations, reusable named queries.
**Defer:** SQL-like scoped syntax pending joins, windows, and nullable boundary
cases. **Reject:** hidden network activity when inspecting a plan or treating
ranked model output as checked truth.

## Discriminating Experiment

Compare explicit calls and a plan builder for invoice grouping, missing-price
rows, duplicate IDs, and a remotely paginated dataset. Explain whether the
display is complete and when computation occurs. A playground table view should
display row count and snapshot identity; correctness precedes query brevity.

## Contrastive Explanation And Diagnosis

Status: selected primary research and original Nomi pressure cases, checked
2026-10-04. No explanation engine, causal-inference library, repair API,
additional prepared study fixtures or new syntax is admitted here. This
extends [C09/HX2's evidence boundary](composition_cases.md#c09-explain-without-repeating-or-leaking)
and [C12/HX8's interpretation study](composition_cases.md#hx8-minimal-study-protocol).
It complements [natural-language dialogue](natural_language.md#grounding-reliance-and-shared-understanding),
not a second account of program semantics.

A query selects evidence, but a useful explanation must also identify the
question. "What happened?", "Why this rather than that?", "Why didn't the
expected event happen?", and "Which change would repair it?" are different
requests. A complete observed trace can answer the first without establishing
a unique cause, a sufficient hypothetical change, or permission to perform it.
An incomplete trace may not even establish whether the expected event occurred.
Explanatory usefulness and evidential support must be assessed separately.

### Primary Evidence And Limits

Ko and Myers' 2004 Whyline paper presents interrogative debugging in Alice.
It distinguishes why/why-not questions and answers based on false premises,
invariants, or data/control flow. Its methods describe four participants without
the tool and five with an iteratively modified tool, recruited from an HCI
Masters program. The paper also discusses limits involving complex expressions,
selected execution instances and complete-history recording.
[Primary paper, question taxonomy, methods and limitations](https://www.cs.cmu.edu/~NatProg/papers/Ko2004Whyline.pdf).
This supplies a concrete design alternative and cautions about generalization;
it does not establish Nomi usability, a universal speed advantage, or the safety
of generated repairs. We do not reproduce its performance numbers as a product
claim. Its program data/control dependencies are not a general causal theory
of external business outcomes or statistical observations.

### Distinctions To Preserve

| Question or evidence | What it can establish under its stated model | What does not follow |
| --- | --- | --- |
| Observed event/value | This event was captured, or this value belonged to the named run | That every relevant event was captured or the person intended it. |
| Program dependency/slice | Recorded inputs or branches contributed under the supplied execution model | A dependency is the unique root cause or changing it alone suffices. |
| Why-not question | A named expected event was prevented, impossible, unobserved, or based on a false premise | One absent visible effect proves the underlying action did not occur. |
| Hypothetical change | A declared model predicts an outcome under named allowed changes and fixed assumptions | The real host will behave identically, or the change is authorized. |
| Minimal diagnosis/repair | Minimal according to an explicit candidate set, cost and ordering | Universally smallest, safest or preferred by the person. |
| Redacted/bounded explanation | The disclosed evidence supports a qualified claim | Hidden evidence is irrelevant or may be exposed to complete the answer. |

Necessity and sufficiency depend on the contrast and admitted interventions.
"Changing this input was sufficient in this deterministic pure model" is a
narrower claim than "this input caused the production incident." A successful
program rerun after several edits does not isolate which edit mattered. Multiple
independently sufficient blockers, interacting conditions and unsupported host
behavior need explicit alternatives or an honest unknown result. Do not impose
one universal causal algebra on program traces, statistical data and human
organizational outcomes.

### Pressure Scenarios And Counterexamples

**Beginner:** an invoice discount is guarded by a minimum quantity and active
membership. Quantity is two, so short-circuit evaluation never consults the
membership condition. Highlighting the first false predicate explains the
recorded branch. It does not prove that changing quantity to ten enables the
discount: membership may be false, unavailable, or from another observation
epoch. If retained input evidence also establishes inactive membership, there
are two blockers; the first evaluated one is not a unique sufficient repair.
Compare a plain trace, a question-bound explanation, and a list of qualified
hypothetical changes without executing them.

**Production:** ask why a filtered reconciliation omitted an order rather than
why a particular predicate evaluated false. Duplicate keys, missing-price decode
failure, policy exclusion and incomplete retrieval have different owners. A
dataflow diagram can show all contributing stages while concealing which
contrast the reviewer meant. Pin the order, population/snapshot, expected
membership and rule revision. If a proposed repair changes accepted domain
policy, it is a new reviewed model, not an automatic diagnostic correction.
The [data/workflow dossier](../data_workflows/README.md) owns join, cardinality
and execution laws; this section owns how the question scopes their explanation.

**Failure-heavy:** a publication button apparently has no effect. The action
could have run without changing the displayed value, run remotely with a lost
acknowledgment, been rejected locally, or never been invoked. Ask whether the
question's premise is supported before inventing a blocker. Local Stop and a
shortened trace do not settle the remote outcome. An explanation must not send
another publication just to gather evidence; explicit reconciliation uses the
owning provider's contract and current authority.

Additional falsifying cases:

- A completed event is rendered out of view. "Why didn't it run?" has a false
  premise; changing a predicate to force another run can duplicate an effect.
- Two conditions independently prevent the result. The first false condition
  is an accurate trace fact but an insufficient single-field repair.
- A debugger selects the latest execution, while the person refers to an older
  failed run. The same source span does not identify the same question instance.
- A predicate reads a clock or remote state. A counterfactual rerun changes that
  observation as well as the proposed input; it is not a controlled comparison.
- One "minimal" repair changes price; another changes quantity. Their equal
  edit counts do not settle domain cost, permitted fields or the person's goal.
- Revealing the exact blocker discloses a protected condition. "Cannot explain
  within this disclosure scope" is different from "no blocker exists."
- A correct but very long dependency dump prevents the reader locating the
  relevant contrast. Truthful completeness is not automatically useful diagnosis.

### Candidate Normal Form And Layer

```text
retained question + named observed/expected outcome and run/model basis
  -> verify premise and identify available evidence/coverage
  -> explain within an explicit model and disclose alternatives/unknowns
  -> optional hypothetical change under stated permitted inputs/assumptions
  -> ordinary checked candidate change, review and current authority
  -> explicit owner commit and separately observed outcome
```

This is a tool/library protocol over source, ordinary nominal values and existing
evidence records. It is not new Core syntax, implicit program inversion or a
universal explanation record required on every function. Domain owners define
the meaningful outcome, intervention set and guarantee. Static analysis may
reject an unsupported hypothesis; captured evidence may support only a historical
claim. Creating an explanation grants no resource, query or execution authority.

Illustrative diagnostic facts are `EXPLANATION_PREMISE_CONTRADICTED`,
`EXPLANATION_EVIDENCE_INCOMPLETE`, and `REPAIR_NOT_SHOWN_SUFFICIENT`; these are
not accepted stable codes. A diagnostic should name the person's question,
relevant source/input paths, exact run/snapshot, stated contrast and remaining
unknown rather than simply print the backend's slice. Inspection preserves
redaction and C09's total/shown/omitted distinction. A formatter still renders
ordinary source; explanation prose cannot silently become a source rewrite.

### Bounded Research Comparison And Stop Rules

Extend one HX8 task with matched supplied-fact failures. Compare A, the raw
source/result and bounded trace, with B, the same facts organized around an
explicit why/why-not question. A hypothetical-repair view is a separate later
condition, not extra evidence given only to B. Include a single known blocker,
multiple blockers, a false premise, a mismatched run and indistinguishable
unknown-outcome worlds. These are proposed stimuli, not additions to U01-U07
or N01-N10 and not observed participant answers. Independently review their
oracles and disclosure scopes before use.

Ask for the question's premise, supported explanation, additional evidence
needed and a prediction under one named permitted change. Appropriate refusal
or uncertainty is success when the evidence cannot discriminate the supplied
worlds. Record explanation accuracy separately from repair sufficiency, domain
acceptability, confidence and time. Use matched disjoint instances, counterbalance
order, record prior domain/debugging experience and assistance, and preserve
initial misconceptions before repair. A tabletop mockup can study interpretation
of supplied facts without a Nomi explanation engine. An executable comparison
must later verify actual evidence capture and command behavior; these are
different claims. Small formative trials do not establish universal diagnosis
quality or population effect sizes.

Reject or remove a candidate that implies unique causation from one dependency,
answers for the wrong run, turns absent evidence into a definite failure,
advertises an unverified edit as a sufficient repair, leaks protected conditions,
or repeats an external action during inspection. Prefer the plain evidence view
when question machinery adds confusion or excessive search cost. A useful
alternative may preserve uncertainty rather than produce an answer; the burden
is improved prediction/repair without stronger unsupported claims, not fluent
prose or a shorter trace.
