# Function Contracts Implementation Bridge

> Status: current implementation bridge; packet `designing`.
> Meaning belongs to the canonical design; evidence below names its limits.

Packet: `docs/research/features/functions.md`, `docs/design/function_contracts.md`, `docs/design/function_contracts_target.nomi`, `docs/review/function_contracts.md`.

## Current Evidence

Ordinary calls, defaults, callback execution and bounded scalar/direct-call
source analysis run in the prototype. The target requires inspectable call shape,
result, effects, captures and completion facts. Pure-only versus effect-polymorphic
collections, generalization and function-type notation remain designing.
Closed source capture in the reasoning lab is a different, restricted producer.

## Open Gaps

Observed call-site types do not establish a generic public contract. Named and
defaulted call compatibility, stateful polymorphic sharing, capture regions,
latent task effects, protocol coherence and complete exported evidence need a
shared checked model. Manual paper derivations do not supply a typechecker.

## Validation

Use the packet's commands in `config/design_passes.json` and its independent
fixtures. `python3 -m tools.design_passes check` validates routing and this record;
it does not execute the target. Browser support requires
`python3 scripts/check_web_runtime.py` and
`python3 scripts/check_web_browser.py --url https://durgadatta.github.io/nomi/web/`.
Record command outputs in ignored reports; do not accumulate dated test totals
or session narratives here. Research-model checks prove only their stated scope.

## Next Actions

1. Establish the closed scalar/report callback contracts needed for local reuse.
2. Compare exact positional shape with explicit default/label adapters and check
   shared-storage counterexamples before generalizing functions.
3. Specify whole-completion region export jointly with resource lifetime.
4. Produce frontend-neutral positive/negative facts and independent consumers
   before admitting general function-type syntax or checked module interfaces.
