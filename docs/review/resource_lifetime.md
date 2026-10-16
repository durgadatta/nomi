# Resource Lifetime Implementation Bridge

> Status: current implementation bridge; packet `designing`.
> Meaning belongs to the canonical design; evidence below names its limits.

Packet: `docs/research/resource_lifetime.md`, `docs/design/resource_lifetime.md`, `docs/design/resource_lifetime_target.nomi`, `docs/review/resource_lifetime.md`.

## Current Evidence

A deterministic resource-scope experiment compares completion carriers and
supplied-fact escape policies. Supported Python-hosted context/defer behavior
has actual compatibility tests. The target's exactly-once lexical release and
cause retention remain distinct from Python suppression and function-level
compatibility mechanisms. Typed completion with checked non-escape and runtime
revocation is a recommendation, not an accepted full resource runtime.

## Open Gaps

General callback/error/region metadata, heterogeneous cleanup causes, binding
failure after acquisition, in-flight use, release deadlines and actual async
cancellation/join schedules remain gates. An Err, diagnostic, closure or Task can
retain a handle; non-escape must cover the entire completion, not only Ok.

## Validation

Use the packet's commands in `config/design_passes.json` and its independent
fixtures. `python3 -m tools.design_passes check` validates routing and this record;
it does not execute the target. Browser support requires
`python3 scripts/check_web_runtime.py` and
`python3 scripts/check_web_browser.py --url https://durgadatta.github.io/nomi/web/`.
Record command outputs in ignored reports; do not accumulate dated test totals
or session narratives here. Research-model checks prove only their stated scope.

## Next Actions

1. Close resource/callback/error/region contracts with the function packet.
2. Compare phase-preserving heterogeneous adapters with compound resources.
3. Exercise enter/bind/body/release, multiple defers and controlled cancellation
   schedules with all causes retained and no use after revocation.
4. Admit one backend-neutral slice and differential CLI/browser fixtures before
   advertising general target resource support.
