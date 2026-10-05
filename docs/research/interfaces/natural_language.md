# Natural Language As A Design Resource

> Status: selected linguistic/HCI evidence and Nomi design hypotheses, checked
> 2026-10-04. No natural-language evaluator, new grammar, NLP model, naming lint
> or human study is implemented by this pass.

Packet: [interface research](README.md), [interaction proposal](../../design/interaction_model.md),
[target challenger](../../design/targets/research/natural_language.nomi),
[current-to-target bridge](../../review/2026-09-30-cognitive-interfaces.md).
Neighbors: [text boundaries](../dsls/text_as_interface.md),
[PowerShell](../languages/powershell.md), [cognition](../cognition.md),
[domain composition](../domain_composition.md).

## Begin With Meaning, Not English-Looking Syntax

A person asks: "Send the revised report to everyone who has not approved it."
Which report revision? Who is everyone? Does "it" refer to the report or a
previous request? Is missing approval a known negative or absent evidence?
Does "send" request an effect, describe an intended plan, or ask whether sending
is possible? A fluent paraphrase can leave every consequential question open.

Natural language offers much more than convenient words for functions. It
packages relations, distinguishes roles, composes meanings, organizes discourse,
uses context, negotiates intention and repairs misunderstandings. A programming
language can borrow those affordances without inheriting implicit authority,
unbounded context or unrestricted ambiguity. Conversely, ordinary language can
remain valuable for discovery, explanation and drafts without becoming source
semantics. Neither "all code should read like English" nor "human language has
nothing to teach formal systems" follows from the evidence.

This chapter treats *division* as segmentation and conceptual organization:
words/phrases/clauses, lexical roles, topic/focus, local discourse and domain
vocabularies. These are research lenses, not a universal biological hierarchy,
mandatory compiler phases or an assertion that a module is literally a paragraph.

## Selected Evidence And Limits

Historical paper dates describe their studies, not a refreshed population.
Universal Dependencies references are **UD v2**; WALS chapter 81 is a selected
typology reference, not a frequency census of current speakers. Swift and
PowerShell guidelines are rolling documentation. WCAG is **2.2**; UAX #31 is
rolling Unicode guidance, not Nomi's accepted identifier profile.

| Primary source | Mechanism or observation | Bounded design use |
| --- | --- | --- |
| [UD syntax](https://universaldependencies.org/u/overview/syntax.html) and [morphology](https://universaldependencies.org/u/overview/morphology.html) | Distinguishes word forms, lemmas, grammatical features and typed dependencies; language-specific realizations differ | Separate token spelling, grammatical role and resolved program identity; an annotation scheme is not the language's semantics |
| [Dryer, WALS chapter 81](https://wals.info/chapter/81) | Describes several dominant argument/verb orders and languages without one dominant order under its definitions | English subject-verb-object order is not a universal usability requirement |
| [Baker, Fillmore and Lowe, FrameNet (1998)](https://aclanthology.org/C98-1013.pdf) | Semantic participants are named within frames, not only by grammatical subject/object | Domain-specific argument roles, not a universal agent/patient object model |
| [Pane, Ratanamahatana and Myers (2001)](https://john.pane.net/pdf/PaneRatanamahatanaMyers2001.pdf) | Non-programmers' problem descriptions include set/event organization, underspecification and differing uses of Boolean words; `and` can express sequencing | Test predictions and missing facts rather than copy prose directly into grammar |
| [Clark and Brennan (1991)](https://web.stanford.edu/~clark/1990s/Clark%2C%20H.H.%20_%20Brennan%2C%20S.E.%20_Grounding%20in%20communication_%201991.pdf) | Communication develops common ground through presentation, acceptance and repair; purpose and medium affect costs | Clarification and revision-bound readback are interaction protocols, not proof of understanding or capability grants |
| [Dumais, primary interview (2019)](https://www.microsoft.com/en-us/research/podcast/hci-ir-and-the-search-for-better-search-with-dr-susan-dumais/) | Discusses synonymy and a shared word having different senses as retrieval problems | Multiple discovery terms can route to one checked command without multiplying executable spellings |
| [Blackwell (1996)](https://www.cl.cam.ac.uk/~afb21/publications/PPIG96.html) | Separates interface metaphor from problem-solving analogy in visual programming analysis | State the mapping and where it fails; familiarity alone is not a semantic law |
| [Ivanova et al. (2020), author-hosted paper](https://web.mit.edu/evlab/assets/papers/Ivanova_et_al_2020_eLife.pdf) | In the reported Python/ScratchJr comprehension tasks, multiple-demand regions responded strongly; language-selective regions weakly or not at all | Code comprehension is not simply sentence comprehension; this native-English, proficient sample does not decide naming, pedagogy or all populations |
| [Kuhn, controlled natural languages (2014)](https://aclanthology.org/J14-1005.pdf) | Compares precision, expressiveness, naturalness and simplicity; human communication, translation and formal representation are different aims | A controlled document language needs an explicit grammar/interpretation contract, not a universal English execution mode |
| [Swift API guidelines](https://www.swift.org/documentation/api-design-guidelines/) and [PowerShell verbs](https://learn.microsoft.com/en-us/powershell/scripting/developer/cmdlet/approved-verbs-for-windows-powershell-commands) | Swift considers use-site phrases, argument labels and effects; PowerShell uses an approved verb/resource vocabulary | Compare grammatical cues with semantic roles; guidelines from one ecosystem are not Nomi compiler restrictions |
| [WCAG 2.2](https://www.w3.org/TR/WCAG22/#label-in-name) and [Unicode identifiers](https://www.unicode.org/reports/tr31/) | Accessible names relate to visible labels; identifier/normalization profiles require explicit choices | Localized presentation must preserve command identity; script and identifier policy need independent security/portability work |

Scope limits: ACM/CACM fetches for Furnas et al.'s 1987 vocabulary paper failed;
its quantitative results are **not** claimed here. Dumais's interview supports
the narrower retrieval mechanism. The Grice PDF fetch also failed; this pass
does not derive a diagnostic specification from unreviewed conversational maxims.
No NLP corpus, treebank, translation engine or foreign language runtime was run.
Studies and guidelines generate hypotheses, not evidence that Nomi is easier.

## A Compositional Hierarchy

```text
authored sounds/text/signs and segmentation
  -> lexical units, names, senses and grammatical features
  -> phrases, roles and explicit relations
  -> clauses, scope, alternatives and temporal/modal distinctions
  -> discourse, reference, context and revision
  -> dialogue, clarification, review and negotiated action
  -> domain vocabularies, institutions and knowledge practices
```

This is a design-learning route, not a claim that language is one tree or that
every culture realizes these levels identically. Syntax trees, discourse graphs,
domain dependencies and authorization relations have different owners. A frame
can guide a function's roles without turning its names into a theorem checker.

### Linguistic Pressure On Programming Components

The following transfers are **Nomi hypotheses**, not deductions from a
part-of-speech tag or experimentally proven recommendations:

| Linguistic distinction | Nomi component to challenge | Cost or boundary |
| --- | --- | --- |
| Form, lemma and sense | Identifier, resolved binding, glossary entry | A stemmer or translated word must not merge bindings |
| Nominal reference | Data/type/module names | A noun does not mean mutable object or OOP ownership |
| Predicate/valency | Function and parameter contract | Arity, role, effects and errors need types, not English transitivity |
| Frame participants | Named call arguments | `source`, `destination`, `amount` differ even with equal host types |
| Modification | Field, predicate, policy value or refined type | `safe`, `fast`, `latest`, `valid` need a named basis, not marketing adjectives |
| Adverbial manner | Explicit algorithm/profile/budget | `quickly` has no bound until a latency/resource contract is specified |
| Number/collectivity | Single item, collection, stream, table plan | A plural name cannot authorize automatic enumeration or flattening |
| Case/preposition | Role labels and contextual references | Role clarity matters more than literal English `to`/`from`; reserved words still apply |
| Tense/aspect | Description, cold task, running action, completed observation | `sent` cannot mean merely requested; grammatical tense is not a clock or commit receipt |
| Modality | Ability, policy permission, obligation, prediction | `can_send` must say which question it answers; none creates a runtime grant |
| Negation/quantification | Bool predicates and explicit collection operations | `not every` differs from `every not`; empty domain and unknown evidence must be stated |
| Coordination | Data grouping, Boolean expression, sequence or parallel tasks | Prose `and` cannot choose between these execution meanings |
| Anaphora/deixis | Binding reference, selection target, source/model context | `it`, `this`, `there`, `now` need a pinned referent/basis when committed |
| Topic/focus | Receiver, pipeline input, local name and diagnostic emphasis | A pipeline still inserts the first argument; it does not infer discourse roles |
| Ellipsis/default | Omitted argument and inferred type | Omission must have one visible contract; ambient conversational context is not a default |
| Register/domain terminology | Package glossary and import qualification | Domain-specific senses must not be flattened into one approved vocabulary |
| Quotation/mention | Text literal, authored source, command/data boundary | Mentioning an instruction is not requesting or authorizing it |
| Repair | Draft, diagnostic, clarification and checked edit | Suggestions preserve original input and cannot silently execute |

## Naming As A Small Semantic Interface

A proposed naming contract has separate dimensions:

```text
resolved identity and public compatibility
domain concept and role
operation/representation boundary
units, cardinality and time/basis where needed
failure, effects and completion in the signature
display label, search aliases and audience documentation
```

The compiler resolves declarations, not inferred dictionary senses. A library
may use domain verbs such as `settle`, `differentiate` or `reconcile` that a
general glossary does not replace. At a call site, modules can supply context:
`json.decode` and `text.decode_utf8` need not expand into sentence-length names.
Short local names are appropriate when their roles remain locally recoverable.

Concrete contrasts to study:

| Tempting name | Question hidden | Candidate explicit form |
| --- | --- | --- |
| `process(data)` | Parse, validate, transform or execute? | `orders.decode(raw)` followed by `orders.prepare(input)` |
| `get_report()` | Build, read retained result or query live state? | `reports.read_snapshot(ref)` versus `reports.collect(plan)` |
| `send(report, users, true)` | Which role and what does the Boolean change? | `publisher.prepare(report, recipients=ids, policy=DeliveryPolicy.RequireReceipt)` |
| `is_valid(value)` | Valid for which schema, edition and purpose? | `invoice.decode(raw)` or a narrowly typed predicate |
| `can_publish(plan)` | Supported, allowed, reviewed or likely to work? | Separate profile check, current grant and scoped review |
| `latest()` | Latest by ingestion, event time, revision or observation? | `history.at_revision(ref)` with explicit unavailable history |
| `save()` | Draft persisted, synchronized, committed or replicated? | Completion variants named by the storage owner |

Do not mechanically require every function to be a verb, every Bool to start
with `is_`, or every collection to have English plural morphology. In particular,
Swift's side-effect naming convention is an ecosystem mechanism, not a universal
truth that a noun phrase is pure or an imperative phrase effectful. PowerShell
documents verb/resource naming, not mandatory adverb/adjective name slots.
Nomi already uses `uses`, Result, explicit mutation and suspension for facts
that word endings cannot establish. A future lint must be opt-in, glossary-aware
and removable if it mostly judges vocabulary rather than finding contradictions.

## Division, Scope And Comprehension

**Lexical relations:** a vocabulary can group related senses and show broader/
narrower concepts without making them runtime synonyms or subtype relations.
`publish`, `export` and `save` may overlap in everyday discourse while denoting
different effects here. Conversely, two teams may use different words for one
checked operation. Discovery can retain both histories; source resolution must
still choose one imported declaration. Domain glossaries should include examples,
counterexamples and "not the same as" entries, not only dictionary definitions.

**Categories:** familiar concepts can have borderline cases; an executable
predicate needs a declared boundary or an explicit unresolved result. A diagram
label such as "customer" does not decide eligibility, legal status, account role
or organizational responsibility. Nominal types can record a chosen domain
contract without pretending to settle every ordinary-language category. A
hypernym in a glossary is not automatic class inheritance, variance or coercion.

**Segmentation:** underscores, whitespace, indentation and punctuation can
expose units, but a word boundary is not necessarily a concept boundary.
`read_only_snapshot` is a compound concept; splitting it into independent
dictionary meanings loses its contract. Do not use syllable/word counts as a
universal readability score. Compare compound interpretation in the task's
domain and record unfamiliar terms separately from syntax errors.

**Roles before word order:** the receiver in an OOP call, first argument in a
pipeline and grammatical subject are not necessarily the acting authority.
Compare `transfer(500, a, b)` with named source/destination/amount roles using
the same contract. Two account values can be swapped without a type error if
their role distinction is not represented. Labels help only if they name the
right roles; nominal source/recipient wrappers are another candidate with cost.

**Scope:** `not all(items, approved)` is not `all(items, not_approved)`.
For total Bool predicates over an empty list, universal quantification holds
and existential quantification does not. An application may separately require
a nonempty population. These are logical/model facts, not a claim about what
people spontaneously mean by "everyone." Missing evidence requires a separate
domain interpretation; it is not automatically false. Changing normal Bool
semantics to emulate prose would hide rather than resolve that distinction.

**Discourse:** a useful local binding can establish a topic that subsequent
operations reuse. A module groups a domain vocabulary, and a public signature
states what a caller must know without reading an entire narrative. These are
design analogies, not permission for implicit pronouns or conversational state
in name resolution. Editor selection and source binding are different referents.

**Attachment and scope cues:** "approved reviewers of this report" can leave
open whether people are approved for a role or have approved the document.
An explicit selection names the relation, its subject/object and report basis.
Likewise an existential check does not mean "some but not all": over two
approved people, both `any(approval_values)` and `all(approval_values)` hold.
A possible prose inference must not silently strengthen the declared predicate. Add population
and relation examples to documentation, not new English operator aliases.

**Voice and repair:** spoken punctuation, pauses, emphasis, homophones and
recognition alternatives are additional input pressures, not source authority.
An adapter can preserve alternative transcripts and read back resolved roles
through accessible text before a consequential action. Do not use prosody or
the word "just" to infer permission, suppress a precondition or skip review.
"Fix it again" also presupposes a referent, prior action and fault; those facts
need evidence rather than an accommodating invented history. These are proposed
adversarial trials, not measurements of a speech-recognition system.

**Psychology:** vocabulary familiarity, relation recognition, memory for roles,
prediction of control flow, confidence calibration and repair are separate
outcomes. They can trade off: a fluent metaphor may encourage a wrong prediction,
and a longer label may clarify a role while slowing scanning. The neural study
above cannot prescribe a syntax; this pass makes no deterministic linguistic
relativity claim, fixed working-memory quota or universal learning-style claim.

## Pragmatics: Dialogue Without Ambient Execution

Candidate normal form:

```text
authored request retained as draft
-> proposed interpretation with missing/ambiguous/unsupported facts
-> clarify roles, scope, references and consequences
-> checked typed candidate plus bounded read-only explanation
-> scoped review if required + current execution authority
-> explicit commit at the actual owner boundary
-> observed completion, rejection or unresolved outcome
```

"Can you publish this?" can ask a question or request action. A conversational
adapter must not resolve that distinction solely by politeness or confidence.
The proposed interpretation remains untrusted; decode/check it through the
same command contract as a form or palette. Clarification must not disclose
private candidate targets merely to resolve a phrase. A conversational readback
is neither authenticated review nor proof of understanding.

The [target](../../design/targets/research/natural_language.nomi) supplies a
beginner role-preserving request value, production handling of a **supplied**
interpretation, and failure-heavy reviewed submission. It implements no parser
for prose. A ready interpretation still needs semantic checks, freshness,
domain identity and current authority; canceled work can leave remote outcome
unknown. The [messaging dossier](../data_workflows/messaging_and_events.md)
owns the corresponding delivery/reconciliation contracts.

A future controlled-language tool belongs to an explicitly selected domain
package. It needs grammar/edition, typed roles, quantifier scope, normalization,
source provenance, diagnostics, formatter/round trips and a removal path.
Free prose, controlled prose and checked Nomi source remain different artifacts.
An LLM may propose a draft, but generated fluency never upgrades its evidence.

### Grounding, Reliance And Shared Understanding

The proposed dialogue protocol needs two further distinctions. First, fluent
or cautious wording is not calibrated reliability. A person can report high
confidence while relying on an unsupported suggestion, or reject useful advice
because every answer sounds uncertain. Repeated correct advice may change what
they check on a later task; the absence of a warning can be misread as a completed
negative check. These are research questions about reliance and task history,
not deductions from grammatical modality or an instruction to make every answer
less confident. Tool scores need a named measurement population and evaluation
basis before they are presented as probabilities.

Second, common ground in a conversation is not a globally shared knowledge bit.
In a team, one person may know the currency assumption, another the recipient,
and a successor only the final source/result. Receipt of a summary, assigned
checking, observed completed checking, understanding, endorsement and authority
are different claims. Two genuine approvals can coexist with each reviewer
assuming the other checked a fact. A revision-bound handoff must not present
pending work as completed or require disclosure of a private fact merely to
resolve a reference. Source/protocol records can expose the gap; they cannot
certify a person's mental state or settle institutional responsibility.

The substantive counterexamples, primary-source limits, alternatives and
unperformed methods live in
[C12's advisory-reliability protocol](composition_cases.md#c12-advisory-reliability-and-calibrated-reliance)
and [team-handoff protocol](composition_cases.md#c12-team-handoff-and-distributed-understanding).
They refine HX8, not NL1-NL6 or the prepared N01-N10/U01-U07 inventory. The
existing individual prediction/repair trial cannot by itself establish safe
long-term reliance or team knowledge transfer.

Explanations also need a question and contrast. "Why did this happen?", "Why
didn't the expected action happen?" and "What change would make it happen?"
need different evidence. The premise may be false, and a truthful trace can
identify one blocker without justifying a unique or safe repair. The
[contrastive-explanation research](query_search.md#contrastive-explanation-and-diagnosis)
owns that distinction under C09/HX2/HX8. Asking for missing facts is still
success; a confident paraphrase is not a causal argument or an execution grant.

## Localization, Access And Terminology

Separate stable machine command identity from localized visible/accessibility
labels and search terms. Discovery may recognize "ship", "send" and a translated
phrase while displaying the resolved command and its target before activation.
Do not emit executable identifier synonyms just to match every query. Alias
collisions can return multiple choices rather than silently pick a command.
Locale changes cannot change stored bindings, amounts, units, grants or targets.

N09's English/French labels are illustrative supplied presentation data, not
professionally validated translations. Its meaning-preserving comparison
concerns declared command identity/target, not verified linguistic equivalence
or a fluency test comparing languages. Translator review and users' language
context must be recorded before any actual wording comparison.

WCAG's visible-label/accessibility-name relationship supports a concrete
cross-modal check; it does not prove an entire command UI accessible. Test voice,
screen-reader, keyboard, IME and text fallback paths against the same command
identity. Translate whole messages with named typed fields rather than assemble
English fragments, as in [text-interface T9](../dsls/text_as_interface.md).
Publish terminology context so translators can distinguish a queue from a log,
permission from possibility, and unknown completion from known rejection.

Unicode identifiers require an explicit repertoire, normalization, collision,
confusable/bidirectional and cross-host policy. Do not add ad hoc stemming,
case-folding or translation to binding resolution in the name of naturalness.
This pass does not choose ASCII-only or multilingual identifiers; D3 and the
existing text-boundary work remain prerequisites for that decision.

## Edge Cases To Reject A Candidate

| Case | Trigger | Required distinction / falsifier |
| --- | --- | --- |
| LN01 | Two equal-typed account arguments are swapped | Role error remains visible; grammatical fluency is not enough |
| LN02 | `not every` becomes `every not` | Quantifier scope changes the selected set |
| LN03 | "All are approved" over no rows | Explicit empty-domain policy; no implied nonempty fact |
| LN04 | `and` is taken as sequence/parallel/conjunction | One source contract, explicit task scheduling |
| LN05 | "Can I send?" is executed | Query/request/permission remain separate |
| LN06 | "it/this" after selection or revision changes | Clarify/pin the referent; reject stale reviewed targets |
| LN07 | "latest/yesterday" spans clocks or time zones | Name the temporal basis; no silent local-time reinterpretation |
| LN08 | Missing evidence becomes known non-approval | Domain evidence state is not default Bool false |
| LN09 | A compound is stemmed into another symbol | Identifier identity is not dictionary normalization |
| LN10 | Two translations/search aliases collide | Discovery disambiguation; no automatic source rewrite |
| LN11 | `safe`, `clean`, `valid` hides purpose/profile | A declared check basis and residual uncertainty |
| LN12 | Singular/plural implies eager enumeration | Carrier types and invocation count, not inflection |
| LN13 | Pipeline or method receiver is assumed actor | Explicit semantic roles and authority owner |
| LN14 | A quoted command is executed | Mention, draft and invocation are different |
| LN15 | A fluent explanation invents a cause or source span | Only supported facts; omitted/unknown evidence visible |
| LN16 | Indirect wording hides a destructive effect | Consequences and execution boundary visible before commitment |
| LN17 | Approval word is remembered after grant revocation | Review scope and current authority separately enforced |
| LN18 | UI labels imply remote cancellation or universal undo | Observed outcome and effect-specific reconciliation |
| LN19 | A translated label diverges from accessible name | Same named command discoverable across modalities |
| LN20 | Familiar syntax is measured only on experts in English | Record population, prior vocabulary and language context; no universal conclusion |

## Bounded Forks And Study Preparation

NL1-NL6 refine T1/T9/T10 and HX3/HX8 under existing questions 4/5/7/11/15/17.
They are not six new implementation projects or a second design authority.

| Experiment | Credible alternatives | Discriminator / owner |
| --- | --- | --- |
| NL1 | Ecosystem-wide verb rules versus opt-in domain glossary/role guidance | Predict effects/errors on three real call sites; false positives and terminology loss; D1/T1 |
| NL2 | Positional phrases versus named roles versus role-specific nominal wrappers | Source/destination swaps, Boolean policy and nested calls; prediction/repair cost; D1 |
| NL3 | Boolean long forms versus checked selection/projection views | Scope, empty population and unknown approval controls; semantics unchanged; HX3/D3 |
| NL4 | Automatic context resolution versus explicit clarification/context pinning | Changed referent, late response, changed review and unknown effect; HX1/HX3/D2 |
| NL5 | One canonical executable vocabulary versus localized discovery aliases | Alias collisions, visible/accessibility name agreement, exact command identity; T9/HX8 |
| NL6 | Free prose proposals versus a scoped controlled-language tool | Unsupported construction, ambiguity, round-trip/source provenance and no implicit grant; T10/D4/D7 |

[Prepared cases N01-N10](language_cases.json) are original stimuli and supplied
facts, **not observed responses**, a benchmark, NLP acceptance vectors or a
grader. [Integrity tests](../../../prototype/tests/unit/tools/test_natural_language_research.py)
guard IDs, facts, navigation and boundaries. Python evaluations of small Boolean
oracles establish only those fixture facts, not Nomi execution or comprehension.

Study protocol, extending the [existing HX8 preparation](composition_cases.md#hx8-minimal-study-protocol):

1. Pre-register one fork and task outcome; recruit beginners and experienced
   readers with recorded domain/programming experience and language context.
   Participation is voluntary; do not diagnose people from task errors.
2. For meaning-preserving comparisons, expose the same types, facts, effects and
   policy in both conditions. Counterbalance order and use disjoint matched
   instances to avoid training on an answer; record training/support separately.
3. Ambiguity controls deliberately omit a fact in both presentations. Asking for
   it is success, not slowness or a wrong answer. Vocabulary-discovery cases are
   not equivalent-program comparisons; analyze them separately.
4. Ask for predicted result/target, evidence needed, effect boundary and a repair
   before allowing execution. Record confidence, clarification, wrong-target,
   wrong-scope, false-certainty and unintended-action incidents.
5. Assess prediction, learning transfer, delayed recall and repair independently
   of token count/speed/preference. Measure unsupported tasks and accessibility
   blockers; assisted and unassisted trials are not interchangeable.
6. Use independent reviewers and retain rationale for semantic judgments;
   automated schema/DOM checks cannot grade understanding. Report qualitative
   mechanisms and uncertainty; determine sample size for the chosen question,
   not a universal fixed number proving a notation easy.

## Admission, Handoff And Stop

Next: select NL2's same-type role swap and NL4's changed referent for an HX8
pilot, after D1-D3 give the actual command one typed contract. Do not wait for
every linguistic topic to close. Begin with documentation/inspection over the
existing [invoice](../../design/interaction_model_target.nomi), not a new NLP
engine or conversational execution grammar.

Current extraction points are resolved binding/source facts, public signatures,
the structured diagnostic records and shared semantic command adapter proposed
by the interaction packet. Naming lint is optional tooling, command labels are
projections, codecs/controlled vocabularies are libraries, and a controlled
language is a scoped tool only if ordinary calls demonstrably fail. This pass
adds no runtime exports or playground samples.

Retain a proposal only when it improves correct prediction or repair without
hiding identity, invocation count, scope, failure, authority or suspension.
Remove a synonym layer that multiplies source recognition paths, a linter that
enforces English tastes, or a paraphraser that invents facts. Natural language
should make computation more intelligible and discussable, not less accountable.
