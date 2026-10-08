# Nomi Frontier Handoff

> Status: temporary, user-requested handoff for the next GPT 6 Astra pass.
> Prepared 2026-10-08 from `8b82d8a` and its linked delivery receipts.
> This document selects investigations; it is not language authority, a new
> backlog, target acceptance, implementation evidence or release permission.

## Mission

Push Nomi toward a coherent language and useful product, not a larger collection
of features. Find the smallest semantic mechanisms that support readable scripts,
checked libraries, data work, effects, failure, resources and rich tools together.
Challenge the current design seriously: rejecting a recommendation, deleting an
abstraction or replacing a bounded mechanism can be the most valuable outcome.

The completed preparation pass was documentation-only. The next user-authorized
design/implementation pass should produce decisions and executable evidence,
not repeat the global bibliography or implement every unchecked note. The user's
choice of Astra does not change repository permissions or configure any model.

Preserve local reasoning under growth. Python AST, Lark, Rust/WASM, JavaScript,
Pyodide and Core IR are replaceable laboratory substrates, not language laws.
Use [the exploratory doctrine](docs/orientation/exploratory_implementation_doctrine.md)
to keep experiments inspectable and reversible. Larger rewrites are legitimate
when a failed required program demonstrates their need; compare them against a
narrow repair and bounded extraction on the same independent oracles.

Quick route: [baseline](#baseline-and-evidence), [first session](#first-session),
[semantic frontier](#lane-one-close-a-semantic-frontier),
[continuation engineering](#lane-two-continuation-engineering),
[domain extension](#extend-without-flattening-domains),
[verification](#verification-and-product-gates),
[next-pass request](#suggested-next-pass-request).

## Start Here

Read this route, then only the packet and code required for the chosen slice:

1. [AGENTS.md](AGENTS.md), [README](README.md), [docs authority](docs/README.md)
   and `opencode.json`; inspect the worktree before editing.
2. [Target design](docs/design/README.md), [syntax](docs/design/syntax.md),
   [semantics](docs/design/semantics.md), [industrial contracts](docs/design/industrial.md)
   and [decision ledger](docs/design/decisions.md).
3. [Synthesis](docs/design/synthesis.md), [D0-D7 agenda](docs/design/redesign_agenda.md),
   [active target suite](docs/design/targets/README.md) and
   [overall program](docs/design/targets/overall.nomi). `docs/design/target.nomi`
   is superseded, even where older entrypoints still mention it.
4. [Latest runtime receipt](docs/orientation/project_roadmap.md#scoped-runtime-continuation-receipt),
   [roadmap queue](docs/orientation/project_roadmap.md#first-reviewable-work-queue)
   and [detailed A01-A33 notes](docs/orientation/project_action_notes.md).
5. [Registered packets](config/design_passes.json),
   [packet workflow](docs/orientation/design_pass_workflow.md),
   [convergences](docs/research/convergences.md) and
   [bounded open questions](docs/research/open_questions.md).

Use [.agents/skills/nomi-language-design](.agents/skills/nomi-language-design/SKILL.md)
for semantic work and [nomi-ai-native](.agents/skills/nomi-ai-native/SKILL.md)
for handoff/process changes. Before implementation, read the applicable
`nomi-interp`, `nomi-parse`, `nomi-rust-parser`, `nomi-reduce`, `nomi-test` or
`nomi-web` skill rather than infer the local workflow. Local RAG is source
discovery, not authority; reconcile every useful hit with the active owner.

Do not restore the old corpus at `08f2aad` as parallel authority. Retrieve a
historical detail only when a selected open question needs it.

## Baseline And Evidence

| Checkpoint | What it establishes | What it does not establish |
| --- | --- | --- |
| `8b82d8a` | Comprehensive notes, A01-A33 decomposition, domain recipes, eleven research units, rewrite/evidence gates; repaired Q02-Q04 queue entries distinguished from residuals | Execution of proposed tasks or acceptance of any new contract |
| `3184ef3` | Detailed research-gap and bounded experiment contracts | Execution of new comparisons, foreign adapters or human studies |
| `f8209ea` | Once-only native displayed values and historical binding-name maps | Deep-owned snapshots of mutable values/handles; Pyodide displayed-value support |
| `e949551` / receipt `000ad54` | Hosted hook binding, synchronous scope/try cleanup and child-before-parent normal resumption | General operand/phase continuations, failed-child unwind, close/throw, async cleanup or D2 conformance |

The last runtime receipt reports **2,931 passed / 81 skipped**, **1,177 web/runtime
passed / 1 skipped**, actual default/Pyodide Chromium workflows and native-hosted
completion comparisons. These are historical October 4 local observations, not
checks run for this handoff or proof against a future revision. Local tools were
Python 3.14.0rc3, Node 25.9.0 and Cargo 1.95.0; refresh actual versions.

The notes preparation reran 127 documentation/packet/target-fixture checks,
validated all five packet structures and checked 253 local links/anchors.
Documentation checks do not parse/typecheck the whole target. The four affected
design packets remain `designing`; pattern matching remains `implementing`.

Current behavior to retain or label explicitly:

- The default browser is Rust/WASM parsing, structured JS lowering and the JS
  Core runtime. Legacy Pyodide is a separate bootstrap/execution path.
- Hosted ordinary calls/defaults and synchronous context hooks have bounded
  repairs. Portable lowering refuses named/unpacked calls and hosted scope
  intrinsics before effects; richer hosted support is not portable support.
- JS rejects integers outside +/-9007199254740991; Python admits wider integers.
  This repair is not the final scalar/wire contract.
- Browser text length, iteration, indexing and slicing use code points, not
  graphemes. Browser slices work; Python-AST-to-Core slice lowering remains fenced.
- Native session results retain values and historical names without rerunning
  effects; contained mutable values/handles remain references. Pyodide is output-only.
- Worker termination is a host stop, not proof of language cancellation or cleanup.
- Root licensing, actual minimum-version/hosted CI, exact Pages revision,
  container/digest evidence and human accessibility studies remain distinct gates.

## First Session

1. Record `git status --short`, `git log -8 --oneline`, actual tool versions and
   any user changes. Never revert unrelated work. Refresh the baseline if HEAD
   moved after this handoff.
2. Validate packet structure and generated freshness using the startup commands
   below. Check capabilities/dispositions; refresh D0's census rather than assume
   its historical count of three unreviewed directions still holds.
3. Select **one primary semantic question** through D1/the roadmap and **one
   bounded engineering discriminator** if useful. Start from failed pressure,
   not a list of interesting mechanisms. State deliverables and stop gates.
4. Delegate independent review/oracle preparation on disjoint files. Give each
   reviewer its exact contract, evidence limits and no-edit boundary as needed.
   A second implementation sharing assumptions is not an independent oracle.
5. Write candidate judgments/traces before choosing or repairing a producer.
   Implement only after identifying the accepted contract or compatibility lane.
   Leave the existing owner with the exact next step if evidence is insufficient.

```bash
python3 -m tools.design_passes list
python3 -m tools.design_passes show function-contracts
python3 -m tools.design_passes check
python3 scripts/make_web.py --check
scripts/build_wasm.sh --check
python3 .codex/scripts/agent_doctor.py
```

Freshness failure is a finding to explain, not permission to regenerate files
indiscriminately. The two lanes below can proceed independently. Accepted
pattern-fragment migration, source mapping and harness maintenance may also
advance where their own prerequisites are ready; D1-D7 do not freeze all work.

## Lane One: Close A Semantic Frontier

### D1: Callable Contracts

Use the [function packet](docs/design/function_contracts.md),
[callback target](docs/design/function_contracts_target.nomi) and
[current-to-target bridge](docs/review/2026-09-30-function-contracts.md).
The agenda makes D1 the next gate; synthesis starts its admission route with
cleanup. Resolve callback/resource metadata together in paper derivations, then
carry unclosed region/completion obligations into D2. Do not create a circular
requirement to implement every resource/task facility before comparing callbacks.

Type ordered map/fold, derived decode and `run_scope` together under:

- Pure-only strict callbacks versus effect-polymorphic strict callbacks. The
  pure-only recommendation is not accepted or a functional-paradigm mandate.
- Explicit parameter-list type constructor versus function-type literal;
  genuine domain protocols are a challenger, not one protocol per arity.
- Exact positional callback shape versus compatible defaulted/labelled shape.
  Two parameters differ from one tuple parameter; defaults obey accepted call-time
  laws, not whichever host representation is easiest.

Prepare positive/negative judgments for Clock/Random, captured mutation, empty
input, ordinary Err elements, abnormal callback failure, cold tasks and borrowed
handles inside results, causes, diagnostics and returned closures. Purity is not
an empty `uses` set; a cold task can retain effects/authority/regions. A
`retained=false` comment is not a proof of non-escape.

Challenge conservative, relaxed and effect/region-aware generalization with
delayed identity, a captured shared outer slot and independent fresh factories.
Every candidate excludes variables fixed by the surrounding monomorphic
environment. Reject inconsistent sharing without changing allocation to make
the judgment convenient.

Include two equally applicable imported protocol extensions as a required
negative judgment. The diagnostic must identify both declaration/package owners
and an explicit disambiguation route; convenience dispatch must not select by
import order or privately inspect an implementation.

**Output:** coherent call/type/effect/region/interface facts for three program
levels; 80/100-column signatures; hover and conflicting-call/capture diagnostics;
an explicit choice, rejection or sharply bounded unresolved obligation. Encode
accepted once-only evaluation/default laws instead of reopening them implicitly.
If an actual type-inference slice is feasible, compare inferred output against
independently supplied judgments. A supplied-fact validator is not a typechecker.

### Follow-On Frontiers

Select the next row only when its required contracts are sufficiently closed.
Do not build all of them in a single pass.

| Frontier / owner | Exact comparison | Independent discriminator | Completion / refusal gate |
| --- | --- | --- | --- |
| D2 completion/resources/tasks; A11/A14/A15 | Typed recoverable scope failure plus distinct abnormal completion; static non-escape plus revocation versus runtime-only checks; cancel-siblings versus collect-all abnormal task failure | Body/release Err, panic and cancellation; binding failure after enter; LIFO release/join; ordinary returned Err distinct from abnormal failure; independent active/queue/evidence bounds | One slice retains causes, transfer targets and declared observation order, not timestamp order; deadlines/worker termination are not completed cleanup |
| D3 portable values; A03/A12 | Display/inspection/encoding; strict UTF-8 decode versus evidenced repair; scalar/UTF-8/UTF-16/grapheme coordinates; exact numeric transport | Fixed bytes, values, paths, spans and sensitive-value negatives prepared independently of adapters | One versioned golden contract on declared hosts; reject host-default coercion, replacement or display-as-wire semantics |
| Interface/nominal ownership; A05/A26 | Passive separately checked interfaces across diamonds/re-exports/stores | Declaration/package identity, public dependency and runtime owner/brand facts | Import execution/private-source coincidence cannot create type identity; instance ownership need not make every declaration generative |
| D4 whole-program coherence; A01/A17 | Beginner invoice, boundary-heavy import/report and failure-heavy resource job | Explain every call, expected error, authority, suspension and cleanup; list proposed APIs explicitly | One vertical contract fits locally without fictional support; revise a decision when composition fails |
| D5 representations; A21/A31 | Text plus read-only projection versus structured-document primary | Same supplied facts; invalid drafts, stale revisions, denied grants, changed referents and missing checks | Preserve identity/comments/fallback/accessibility; actual human observations remain separate from fixture answers and screenshots |
| D6/D7 migration; A04/A06/A20/A28 | One admitted source/artifact/runtime/diagnostic family through two frontend paths | Independent accepted/rejected/corrupt artifacts, spans, values and order | Gated profile, rollback and an honest runnable sample; no whole-target conformance from parsing or stdout alone |

Task bounds must separately name active work, queued item count/bytes and retained
result/evidence storage. A running-task limit alone does not bound memory.

Prototype a checked typed interface when host AST/dictionaries cannot retain
required symbol/type/effect/region ownership. Start with one producer and one
downstream consumer, not a universal checker or whole IR replacement. Keep
supplied, inferred and observed facts distinguishable in inspection output.

## Lane Two: Continuation Engineering

Start with [the exact runtime next step](docs/orientation/project_roadmap.md#iterative-runtime-continuation-plan).
Relevant owners are `prototype/interpreter/python/generator_state.py`,
`expressions.py`, `function_call.py`, `control.py`, `exceptions.py`,
`context_managers.py` and their Nomi/reduced overrides. Read current code before
selecting the owner; these are starting locations, not a prescribed architecture.

Prepare two minimal native/hosted reproductions:

1. An effectful completed left operand plus a yielding right operand in a compound
   expression. Preserve the left value, exactly one left effect, the sent value
   including `None`, the resume phase and final result.
2. A failing paused child under nested `try`/`with`. Deliver failure to the waiting
   ancestor so handlers and every required exit observe the right error/completion;
   no ancestor disappears merely because a child resumed first.

Use declared native Python values, event order, active error/context facts and
cleanup traces as compatibility oracles across `python`, `nomi` and `reduced`.
Record operand, phase, child and pending completion together. Compare a narrow
repair, bounded continuation extraction and explicit pre-effect unsupported-shape
fence. Choose one coherent boundary rather than repeated operator-specific patches.

The existing focused anchors are
[generator frame boundaries](prototype/tests/unit/interpreter/python/test_generator_frame_boundaries.py),
[context boundaries](prototype/tests/unit/interpreter/python/test_context_scope_boundaries.py)
and [exception completion](prototype/tests/unit/interpreter/python/test_exception_completion_boundaries.py).
The reduced failed-child skip is intentional evidence, not permission to remove
it or weaken assertions. Add new reproductions; obtain required approval before
editing existing tests. Close/throw, async cleanup and target generator admission
remain separately gated unless the selected contract and actual fixtures cover them.

**Output:** explicit supported/unsupported shapes, one bounded mechanism or fence,
once-only/cause/order fixtures, relevant neighboring/full tests and an updated
receipt. Hosted Python suppression/context parity must not silently become Nomi's
typed all-cause completion contract. Keep target design and compatibility repair
in separately reviewable commits.

## Extend Without Flattening Domains

Use [A33](docs/orientation/project_action_notes.md#a33-text-interfaces-strings-and-scoped-dsls),
[domain recipes](docs/orientation/project_action_notes.md#domain-extension-recipes)
and their research owners, not another new domain catalog. Choose one inert
description before an executor. Ordinary calls/protocols come first; new global
grammar is not justified merely by repeated composition failure. Scoped notation
needs demonstrated ordinary-call pressure plus hygiene, budgets, source maps,
formatting and removal gates. A further core primitive additionally needs a
missing semantic contract and an independent conformance slice.

| Pressure | Small reusable foundation | Domain law that must remain owned |
| --- | --- | --- |
| Data/DAG/time/database | Typed identity, dependency/plan, snapshot basis, revision and commit boundary | Scheduling order, cyclic/fixed-point rules, predicate consistency, history and crash durability are not one graph law |
| AI/ML/science | Shape/unit/clock, numeric profile, randomness, evidence/provenance, budget | Differentiability, convergence, adaptive evaluation, correlation and learned removal require separate assumptions/oracles |
| Queues/pub-sub/events | Message identity, position, owned delivery/settlement, bounded demand | Partition order, lease, replay, local atomicity and broker durability are profile-specific; no universal exactly-once promise |
| Text/config/web/CLI | Text/Bytes, versioned decode/encode, source maps, contextual escaping and command plan | Display, inspection, serialization, shell arguments and template stages differ; quoting at one stage does not secure all sinks |
| Visual/support/documentary domains | Referent/revision, reviewable change, explanation/evidence, explicit executor authority | Approval covers the exact proposed action under current authority, not truth, repair safety, a changed revision or new executor capabilities |

For generic operations use [GA1-GA8](docs/research/generic_operations.md#bounded-experiments)
to expose order, demand, retention, cache context, failure prefix and algebraic
side conditions. Do not create universal Object/Function methods or assume hash,
encoding, serialization, parallel reduce and fixed-point convergence are total.

For natural language use [its research owner](docs/research/interfaces/natural_language.md)
for naming/semantic roles, quantifier scope, audience, localization and changed
referents. Compare discoverable aliases/labels without giving prose execution
authority. An English-friendly surface must not impose English-only identifiers
or hide binding/scope behind grammatical intuition.

Translate [philosophical inspiration](docs/research/cognition.md) into falsifiable
obligations: Leibniz-style
composable representation suggests explicit identities, operators and interpreters,
not a universal knowledge engine; Boole-style calculation suggests named logical
laws without confusing unknown, contradiction, failure and False; Dijkstra-style
reasoning suggests local invariants and inspectable reductions that still account
for effects, cleanup and concurrency. Judge these proposed translations by actual
programs, not by claims about what historical thinkers would endorse.

The [eleven research units](docs/orientation/project_action_notes.md#eleven-research-units-to-turn-into-evidence)
have prepared discriminators. Existing countermodels can falsify naive policies;
they do not prove adapters, weak-memory behavior, numeric convergence, durable
recovery or human comprehension. Execute a selected comparison or eliminate a
candidate instead of merely expanding its prose.

## Verification And Product Gates

Scale checks to the changed contract. Do not use large green counts as a
substitute for independent outcomes, or claim a listed command was executed.

| Changed surface | Required evidence |
| --- | --- |
| Design/docs | Selected packet validations, target positives/negatives, local links/anchors and authority review; no runtime claim from doc checks |
| Parser/Surface/Core | Two declared frontend paths, acceptance/rejection, corrupt/versioned artifacts and span/order parity; `prototype/syntax/core_json.py` currently needs a versioned span-carrier decision |
| Hosted runtime | New failing reproductions, three hosted modes, independent value/effect/cause order, neighboring suites then relevant broader suite |
| Browser/runtime assets | Manifest generation when inputs change, `--check`, WASM rebuild only for its changed inputs, actual default and affected Pyodide workflows with desktop/mobile screenshots |
| User-facing sample | Supported profile, normal regressions, intentional snapshot policy, fresh artifacts and actual CLI/browser execution; target-only source stays outside `samples/` |
| Distribution/editor/notebook | Installed outside-checkout artifact or actual declared editor/kernel/container host; mocked/helper tests are not client/host evidence |
| Human claims | Reviewed stimulus facts, consent/accessibility/expertise/confounds and observed task results; no population or longitudinal benefit from a pilot |

Useful focused and promotion commands, conditional on the work selected:

```bash
python3 -m pytest -q -n 4 prototype/tests/unit/tools/test_docs_lifecycle.py prototype/tests/unit/tools/test_design_passes.py prototype/tests/unit/tools/test_design_packet_boundaries.py prototype/tests/unit/tools/test_target_fixture_coherence.py --tb=short
python3 -m pytest -q -n 0 prototype/tests/unit/interpreter/python/test_generator_frame_boundaries.py prototype/tests/unit/interpreter/python/test_context_scope_boundaries.py prototype/tests/unit/interpreter/python/test_exception_completion_boundaries.py
python3 scripts/check_web_runtime.py
python3 scripts/check_web_browser.py --legacy-pyodide
python3 -m pytest -q -n 4 --tb=short
git diff --check
```

Preserve existing tests unless the user explicitly requests or approves the
specific edit, as required by [nomi-test's rules](.agents/skills/nomi-test/SKILL.md#rules).
Reuse recorded authorization for the same scoped work; do not request it again
or generalize it to unrelated edits. Independent evidence must justify changes;
follow `nomi-test` for new test placement and snapshot policy. Keep generated
caches/reports/browser captures out of commits.
Stop servers/processes used for verification; retain a requested usable dev
server with its URL when the future task changes the web experience.

Public release still needs owner decisions on root license, support versions,
artifact identity and authentication/deployment policy, plus actual hosted
evidence and rollback. No push, publication, deployment, license selection,
credentials, privileged services or unsafe native/device probes are authorized
by this handoff. Ask for the specific missing approval rather than broaden claims.

## Completion And Continuity

Commit logical slices: comparison/decision, bounded implementation, then verified
integration/receipt as warranted. Do not manufacture checkpoints or mix target
acceptance, test reorganization, snapshots and backend replacement together.
Update existing packet owners, registry next actions, bridge retrospective and
roadmap receipt; do not make this temporary file permanent parallel authority.

A successful frontier pass leaves fewer unexplained contracts, one or more
credible alternatives eliminated by evidence, and a demonstrably more useful or
more honest supported path. An explicit rejection or narrowed unsupported fence
counts; a bibliography-only expansion or broad rewrite without a pressure oracle
does not. Domain breadth remains optional, not the next release obligation.

At each checkpoint record:

```text
Baseline and changed paths:
Selected pressure / A-D-packet owner:
Candidates, hypothesis and independent oracle:
Decision or remaining exact obligation:
Implemented / accepted / speculative boundaries:
Actual commands, host/profile, results and skips:
Preserved behavior, migration/fallback and removal trigger:
Unresolved approval/security/human/host gates:
Next exact task and first fixture/command:
```

When this handoff is consumed, move durable conclusions into their existing
owners and remove or mark this file consumed with the final checkpoint. Do not
leave both its baseline and a newer receipt competing as live instructions.
Update its links in the docs index, roadmap and action notes if retiring the file.

## Suggested Next-Pass Request

> Read `ASTRA_HANDOFF.md` and the named owners. Begin a bounded local design and
> implementation frontier pass: challenge D1 on the three representative programs,
> and reproduce the two remaining continuation failures before selecting a repair,
> extraction or pre-effect fence. Iterate through independent review, verification
> and coherent commits. Preserve runnable CLI/browser surfaces and distinguish
> accepted target, supported prototype and unperformed evidence. Respect approval
> boundaries for existing tests and external operations. End with decisions,
> actual results, remaining risks and the exact next step, not another broad plan.
