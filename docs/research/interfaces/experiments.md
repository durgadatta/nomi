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
executes 18 independent probes. Assertions check the stated counterexamples
and candidate rules; run without Python's `-O` option. It performs no network,
process, browser, Nomi, device, or foreign solver execution. Optional `--output`
writes a generated research capture; otherwise JSON goes to stdout.

```bash
python3 docs/research/interfaces/probe_interactions.py \
    --observed-on 2026-10-02 \
    --output docs/research/interfaces/probe_results.json
ruff check docs/research/interfaces/probe_interactions.py
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

The counterexamples are evidence against specific overbroad claims, not proof
that the candidate is the only workable design. For example, P02 rejects
number-only freshness but does not choose hashes over counters plus incarnation.
P12 does not prove domain-aware merging is preferable to retaining an invalid
draft. P16 demonstrates an imposed command policy, not correctness of the
browser's existing keyboard handler. Local models cannot establish what a human
understands; C12 still needs a study.

## Philosophy Connected To A Check

Leibniz's concern with discoverable relations becomes the question of whether a
projection preserves domain and exposes a hidden assumption (P04/P13).
Boole's interpretation/domain pressure motivates universe/evidence distinctions
(P05/P06). Dijkstra's precondition/progress pressure motivates all-path and
completion distinctions (P07/P08). Peirce motivates observing the difference
between candidate rules; Hoare motivates unchanged state on rejection.
These are original engineering translations, explained and sourced in
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
