# Executed Interaction Boundary Probes

> Status: reproducible original research models and host observations, captured
> 2026-10-02; no Nomi, browser, foreign service, or device conformance claimed.

The [edge atlas](edge_cases.md) is the coverage map; the
[composition cases](composition_cases.md) own HX1-HX8 candidate comparisons.
These observations motivate those comparisons without executing their proposed
APIs. They extend the method used by the [DSL probes](../dsls/experiments.md)
within the same [cognitive-interface packet](README.md).

## Reproduce

From the repository root:

```bash
python3 docs/research/interfaces/probe_interactions.py
```

The [script](probe_interactions.py) uses only the Python standard library and
executes 23 independent probes. Assertions check the stated counterexamples
and candidate rules; run without Python's `-O` option. It performs no network,
process, browser, Nomi, device, or foreign solver execution. Optional `--output`
writes a generated research capture; otherwise JSON goes to stdout.

Verify the checked-in capture without rewriting it:

```bash
python3 docs/research/interfaces/probe_interactions.py \
    --check docs/research/interfaces/probe_results.json
pytest -n 0 prototype/tests/unit/tools/test_interaction_research.py \
    prototype/tests/unit/tools/test_interaction_study_research.py \
    prototype/tests/unit/tools/test_interaction_capture_boundary.py
```

The checker reuses the capture's date for comparison and compares every field
except the reported Python and Unicode versions. Those historical versions are
preserved and displayed beside the current host versions. The probe outcomes,
bounds, inputs, IDs, and execution flags must still agree, including their JSON
types. A changed outcome fails the check; review the evidence before updating
the capture. Running with `-O` is rejected rather than silently skipping asserts.
The tests also check case/probe/composition references, local links and anchors,
and table structure. These are research-integrity checks, not usability tests.

The checker rejects repeated object fields at every nesting level before
comparison. Otherwise contradictory execution flags or outcomes could disappear
under a parser's last-field policy. RFC 8259 recommends unique object names and
documents divergent duplicate handling; strict rejection here is a local
research-capture policy, not an accepted Nomi decoder contract.
[JSON object interoperability, section 4](https://www.rfc-editor.org/rfc/rfc8259#section-4).
The capture also explicitly records `human_execution: false`. Tests cover
malformed input, boolean-versus-number drift, non-writing verification, and
object reordering; they establish no general security or interoperability proof.

```bash
python3 docs/research/interfaces/probe_interactions.py \
    --observed-on 2026-10-02 \
    --output docs/research/interfaces/probe_results.json
ruff check docs/research/interfaces/probe_interactions.py \
    prototype/tests/unit/tools/test_interaction_research.py \
    prototype/tests/unit/tools/test_interaction_study_research.py \
    prototype/tests/unit/tools/test_interaction_capture_boundary.py
```

The date defaults to the local current date. Later captures should use their
actual date and preserve reported versions. The checked-in
[capture](probe_results.json) records Python 3.14.0rc3 and Unicode database
16.0.0. A Unicode standard's current version and this host database version
are different evidence facts. Report schema is local to this research artifact,
not a public Nomi protocol or accepted runtime schema.

## Results And Limits

| Probe | Counterexample or observed distinction | Candidate implication | Bound or exclusion |
| --- | --- | --- | --- |
| P01: identity | Sorted position selects cup while stored ID still selects tea | H01/C01: target by domain identity | Two unique rows; no real grid or source refactor |
| P02: incarnation | Revision 1 matches numerically across two different session incarnations | H70/C02: revision needs object/history context | Two explicit contexts; no production identity service |
| P03: draft commit | Blank/minus/malformed/negative drafts retain quantity 2 at revision 7; valid 3 commits revision 8 | H41/C03: store draft separately from checked value | Imposed ASCII unsigned-integer codec; no Nomi decoder, form, locale or IME |
| P04: inverse | Over 16 pairs, total 0 has seven inverses, total 3 has two, total 7 has none | H15/C04: alternatives or read-only projection | Finite integer domain only; no general inversion/solver |
| P05: value/effects | Both conjunction orders return false; one calls the counted predicate and one skips it | H66/C06: preserve observation/evaluation laws | Host short circuit and in-memory counter; no external action |
| P06: domain/evidence | Complement changes with the universe; collapsing four support/refutation records to one bit loses distinctions | H25/C06: explicit domain and evidence kind | Original records; no many-valued core logic or reasoner |
| P07: all paths | Some branch is safe in all five initial states; every branch is safe in only four | C06: existence of a good outcome differs from all-path precondition | Two terminating transitions; not arbitrary program verification |
| P08: progress | Decreasing and stutter traces both maintain nonnegative state; only one completes within the supplied budget | H29/C05/C06: invariant and completion evidence differ | Two four-state traces; no unbounded termination/fairness proof |
| P09: epochs | In both arrival permutations, run-aware selection keeps current; arrival-only selection can show old | H33/C08: archive old evidence without retargeting current result | Two supplied replies; no worker or scheduler integration |
| P10: authority | Cached allowed is true while current grant set denies the same artifact | H90/C02: recheck current execution authority | Set-membership toy policy; no revocation-race/handle implementation |
| P11: uncertain action | Lost acknowledgment follows one modeled action; same key/payload reconciles; changed payload conflicts | H69/H72/C05: unknown is not no-action, and retry identity has a payload contract | Fake provider ledger; no external exactly-once or rollback guarantee |
| P12: merge | Two valid range edits combine into invalid [8, 5] | H45/C07: merged drafts require actual domain validation | Property-wise toy merge, not Git/Automerge/CRDT execution |
| P13: projection loss | Distinct exact values render as 1.00; projected ranges omit their cross-field rule | H16/H40/C04: display/schema does not provide a complete inverse or validator | Two Decimals and declared rule sets; no exporter or codec conformance |
| P14: passive evidence | Naive getter touches the counter; four snapshot views do not; budget shows three of five events and export omits one supplied secret key | H36/H89/C09: captured, bounded, explicitly partial evidence | Imposed toy redaction; no information-flow or real renderer guarantee |
| P15: text coordinates | Same prefix occupies eight UTF-8 bytes, five UTF-16 units, four scalars; NFC relates two unequal sequences | H77/C10: source revision and offset unit travel together | Host encodings/normalization; no grapheme segmentation, bidi algorithm, or parser |
| P16: adapters | Supplied adapters carry the same command; composition Enter and pointer cancel dispatch none | H09/H76/C03: modality requests an explicit semantic command | Imposed finite policy; no actual adapter, IME, accessibility or focus test |
| P17: frame reset | Old local x=2 becomes world x=12 under the changed offset; explicit reprojection restores world x=2 | H81/C11: frame epoch belongs to the proposal | Known 1-D translation only; no XR tracking or calibration error |
| P18: control context | Range-only accepts all four sample/mode pairs; freshness/mode rule accepts one | H85/H86/C11: value validity does not establish current intervention context | Imposed same-clock policy; no physical safety or sensor/device test |
| P19: publication race | Four of six prepare/publish orders accept two edits against one base under unconditional publication; the guarded step accepts one in all six | H14/H30/H45/C07: candidate validity needs an owner-enforced publication boundary | Two commands and an imposed indivisible compare-and-publish step; no real concurrency, crash, ABA, or linearizability proof |
| P20: review scope | Grant-only admits five of six actions; review-only admits two; both checks admit only the original reviewed action | H47/H62/H72/H90/C02/C07: current authority and required review scope are separate facts | Supplied exact-match policy; no real approval, person, authentication, one-shot use, or revocation-race enforcement |
| P21: reused history | Incarnation/counter accepts a rewound history, a copied fork, and an unchanged model; supplied commit identity distinguishes the first two | H14/H46/H70/H71/C02/C07: restoring values is not restoring publication context | Three explicit comparisons; supplied tokens, no identity service or blanket ban on pure-result reuse |
| P22: clock provenance | Numeric age marks three of five samples fresh; clock-aware rules mark only one fresh, two incomparable, one stale, one invalid future | H53/H55/H85/C11: subtract only comparable timestamp values | Imposed same-clock rule with no clock mapping/skew; no real synchronization, sensor trust, or safety |
| P23: indistinguishable outcomes | Two supplied worlds expose identical unknown/Stop-requested observations but have zero versus one hidden action | H62/H64/H69/H87/C05/C12: grade inference from visible evidence, not secret truth | Two supplied worlds only; no actual transport, reconciliation, pending/duplicate events, or human study |

The counterexamples are evidence against specific overbroad claims, not proof
that the candidate is the only workable design. For example, P02 rejects
number-only freshness but does not choose hashes over counters plus incarnation.
P12 does not prove domain-aware merging is preferable to retaining an invalid
draft. P16 demonstrates an imposed command policy, not correctness of the
browser's existing keyboard handler. Local models cannot establish what a human
understands; C12 still needs a study.

P19 tests one possible strict-freshness publication rule, not a mandate to use
compare-and-swap in every library. A serialized owner is another candidate.
P20 assumes this application requires exact action review: other applications
can explicitly authorize a bounded class of automatic actions. It tests neither
the person's understanding nor whether a review record is authentic. A pure
model function, a current grant, and a genuine human endorsement are not the
same guarantee.

P21 sharpens P02/P19's assumptions: incarnation/counter suffices only within
an owner-enforced non-reused history. Undo can restore values under a new commit;
forks need distinct history context. Pure-result reuse can still be valid after
explicit repreparation. P22 sharpens P18's same-clock limit: an incomparable
observation is not known stale. A declared cross-clock mapping with uncertainty
is another candidate, not an implicit subtraction of unrelated ticks.

P23 adds a counterfactual control to P11's lost-acknowledgment case. Unknown
does not mean no action, but it also does not mean certain completed action.
The [study fixtures](study_cases.json) separate participant-visible facts from
hidden facilitator controls and answer keys. Their integrity tests cannot
establish that a real renderer keeps those facts separate or that people
interpret them correctly; HX8 still needs an actual trial.

## Philosophy Connected To A Check

Leibniz's concern with discoverable relations becomes the question of whether a
projection preserves domain and exposes a hidden assumption (P04/P13).
Boole's interpretation/domain pressure motivates universe/evidence distinctions
(P05/P06). Dijkstra's precondition/progress pressure motivates all-path and
completion distinctions (P07/P08). Peirce motivates observing the difference
between candidate rules; Hoare motivates unchanged state on rejection.
The gap review adds a publication-history question (P19) and an endorsement
scope question (P20); neither is settled by a sequential postcondition or an
"allowed" bit. These are original engineering translations, explained and sourced in
[cognition](../cognition.md), not reconstructions of those authors' formal systems.

No philosophical authority can turn the pass count into proof of intent,
usability, safety, or general semantics. The capture's explicit evidence-kind
and execution flags prevent a local model result from being mistaken for a
Nomi, browser, solver, or device integration result.

## Implementation Promotion

1. Select one HX experiment from [the composition packet](composition_cases.md).
2. Specify producer/consumer facts, invalid/stale/unsupported diagnostics,
   ownership, source/epoch identity, authority, and removal gate.
3. Resolve its callback, scalar/codec, resource/task dependencies in D1-D3.
4. Replace supplied facts with real frontend/backend/command adapters for one
   supported slice. Preserve negative fixtures and explicit observation scope.
5. Run CLI/browser conformance and relevant manual input/accessibility tasks
   before promoting a runnable sample.

The research remains `designing`. Probes now supply deterministic motivating
evidence; HX1-HX8 and the human study are still unperformed Nomi candidate
comparisons. Generated web assets, runtime capability tables, grammar, and
supported samples do not change because of this capture.

## Creative Timing Model

The [creative challenger](music_timing.md#creative-authoring-challenger--october-10)
has a separate, executed finite model comparison. Its
[24 literal cases](timing_cases.json) are not additional P-series probes, a
replacement for the historical capture, or an HX authoring/human trial. The
[model profile and commands](music_timing.md#bounded-model-experiment) state the
supplied rational-time, serialized-change and delivery policies. The driver
reports current host identity and explicit execution exclusions.

| Cases | Observed distinction | Limit |
| --- | --- | --- |
| Beat/absolute baselines and tempo changes | Equal initial schedules diverge after the same tempo metadata change | Two explicit models; no inferred intent or automatic conversion |
| Fractional time | The supplied 180 beats/minute case retains exact thirds of milliseconds | Host rational arithmetic; not Nomi scalar or audio-clock conformance |
| Onset/duration changes and replay | Named, basis-matched, current-base edits change the model; replay/stale/wrong-basis/unknown-note edits do not | Serialized owner; no shared-state atomicity, selective revalidation or graph merge |
| Unfinished, negative and zero-duration drafts; boolean tempo | Invalid input preserves the checked model and records note-field drafts | Imposed domain and pair format; not a source parser, locale codec or typed partial-program system |
| Ambiguous request | The supplied ambiguous label leaves the model unchanged | No natural-language interpretation or human intent evidence |
| Reset, incarnation reuse and retained draft | A reused revision counter does not validate the old proposal; a retained draft keeps its original base; restoring a used incarnation is refused | Case-local supplied identities, not global history/identity enforcement or automatic draft migration |
| Passive inspection and old run | Inspecting does not deliver events; a retained old run delivers its old schedule after a current-model change | Pure computation and local records; no frontend or asynchronous worker |
| Local Stop, clock replay and equal-time order | Stop leaves an unmatched note-on; the cursor avoids redelivery; ties follow the declared rule | No release acknowledgment, scheduler timing or device standard |

The literal expectation paths test named observations, not every possible output
or every model state. A pass establishes consistency with this finite profile.
The independently authored oracle cannot establish that the profile is desirable.
All planned local events delivered is distinct from external success, just as
refusing further local delivery is distinct from acknowledged cleanup.

Next compare strict refusal with explicitly revalidated coordinate edits and
choose matched model rules before constructing authoring alternatives. A human
comparison must withhold reviewer answers until initial predictions and preserve
the distinction between selected-model understanding and representation benefit.
The cognitive packet remains `designing`; no target or runnable sample is promoted.
