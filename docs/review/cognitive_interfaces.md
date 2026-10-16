# Cognitive Interfaces Implementation Bridge

> Status: current implementation bridge; packet `designing`.
> Meaning belongs to the canonical design; evidence below names its limits.

Packet: `docs/research/interfaces/README.md`, `docs/design/interaction_model.md`, `docs/design/interaction_model_target.nomi`, `docs/review/cognitive_interfaces.md`.

## Current Evidence

The playground provides actual calculation/report repair, source editing,
inspection, run generations, stale-result controls, drafts, cancellation/reset,
recovery and desktop/mobile layouts. Finite interface/timing/revision probes and
prepared study stimuli expose counterexamples. These are distinct evidence
surfaces; no human comprehension or accessibility benefit is established by
passing automated browser checks.

The [natural-language dossier](../research/interfaces/natural_language.md) owns
role/reference/intent/localization stimuli and their prepared answer facts;
these are not executed NLP or participant outcomes.

## Open Gaps

Text, structured and mixed authoring remain competing models. Editable views,
typed partial work, complete provenance, owner-enforced publication and authentic
review scopes need integration. Human prediction, diagnosis, calibrated reliance,
repair and handoff require actual observations rather than self-review.

## Validation

Use the packet's commands in `config/design_passes.json` and its independent
fixtures. `python3 -m tools.design_passes check` validates routing and this record;
it does not execute the target. Browser support requires
`python3 scripts/check_web_runtime.py` and
`python3 scripts/check_web_browser.py --url https://durgadatta.github.io/nomi/web/`.
Record command outputs in ignored reports; do not accumulate dated test totals
or session narratives here. Research-model checks prove only their stated scope.

## Next Actions

1. Compare representations with identical calculation/report task facts.
2. Preserve distinct draft, checked, observed, stale and unknown outcomes.
3. Extend the existing HX/NL/scientific explanation cases with explicit context,
   competing support and interrupted handoff; retain independent answer facts.
4. Run a bounded keyboard/accessibility and comprehension trial before making
   usability claims or promoting a preferred authoring model.
