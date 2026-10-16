# Pattern Matching Implementation Bridge

> Status: current implementation bridge; packet `implementing`.
> Meaning belongs to the canonical design; evidence below names its limits.

Packet: `docs/research/pattern_matching.md`, `docs/design/pattern_matching.md`, `docs/design/pattern_matching_target.nomi`, `docs/review/pattern_matching.md`.

## Current Evidence

Standalone Pattern Surface v1 is implemented through Lark and Rust producers,
a schema, shared literal decoding and parity fixtures. It is separate from the
default match parser/runtime. The accepted target remains exhaustive, inert and
transactional; the prototype's Python-shaped match forms are a migration surface.

## Open Gaps

Full target match containers, typed coverage/usefulness, fresh arm scopes and
backend-neutral lowering are unfinished. Successful prototype captures can occupy
the surrounding frame; Python-shaped guard/iteration behavior is not the target.
Literal/span integrity must be shared rather than independently reconstructed.

## Validation

Use the packet's commands in `config/design_passes.json` and its independent
fixtures. `python3 -m tools.design_passes check` validates routing and this record;
it does not execute the target. Browser support requires
`python3 scripts/check_web_runtime.py` and
`python3 scripts/check_web_browser.py --url https://durgadatta.github.io/nomi/web/`.
Record command outputs in ignored reports; do not accumulate dated test totals
or session narratives here. Research-model checks prove only their stated scope.

## Next Actions

1. Extract shared target vocabulary and scalar-literal contracts.
2. Replace fenced Pattern Surface decoding with the shared producer contract.
3. Add relational span/document validation, then typed match/coverage integration.
4. Promote runnable CLI/browser examples only after values, errors and capture
   transactionality conform on each declared path.
