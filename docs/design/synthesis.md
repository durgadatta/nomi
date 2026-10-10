# Nomi Language Synthesis

> Status: active whole-language design synthesis; open contracts are not accepted.

Packet: `docs/research/features/README.md`,
`docs/design/targets/overall.nomi`,
`docs/review/2026-09-29-language-synthesis.md`.

## Read The Language

For the broader design purpose, start with the [computational-medium vision](vision.md).
It can challenge this synthesis's models, representations and priorities.
The selected product below is a delivery experiment, not a research boundary.

Start with the [first-product contract](#first-product-contract) and
[local report program](targets/overall.nomi), then consult the relevant
[category fixture](targets/README.md). The
[language reviews](../research/languages/README.md) and
[feature comparisons](../research/features/README.md) supply evidence when a
concrete fork needs it. Reading or implementing the entire research inventory
is not a release prerequisite. No usability study or comparative benchmark was
conducted by this synthesis.

This synthesis connects those views. Accepted source and behavior still belong
to [syntax](syntax.md), [semantics](semantics.md), [industrial contracts](industrial.md),
and [the decision ledger](decisions.md). Proposed library signatures in target
comments are hypotheses, not exports. The current playground runs a different,
supported prototype surface. Do not advertise these fixtures as executable.

The [cognitive/interface expansion](interaction_model.md) adds 18 non-standard
interface threads and a second coherence fixture without admitting grammar.
Use the [design-first agenda](redesign_agenda.md) for cross-cutting gaps and
closure order; the sequence below continues to own import-workflow admission.

## First Product Contract

October 9 synthesis selects **small scripts and trustworthy local data reports**
as the first useful product. The primary user is a person who can read simple
code and wants a calculation or a small data transformation to work, explain
mistakes, and become reusable. Local library authors are the next user, reached
through the same journey. Services, research computing, notebooks and larger
automation remain destinations, not simultaneous launch requirements.

The product promise is: **start with a short script; turn imperfect input into
an understandable result; reuse that logic without changing its meaning**.
This is a scope decision and a contract to validate, not evidence of adoption
or a claim that the prototype already supplies it.

| Journey | Concrete result | Evidence required before release |
| --- | --- | --- |
| Calculate | Change invoice quantity from 3 to 4; result changes from 3850 to 5050 integer cents | Correct calculation, visible source/result revision, useful wrong-argument error, no annotation ceremony to begin. |
| Validate and report | Paste two customer rows; obtain received=2, eligible=1, skipped_ineligible=1; inspect Ada's normalized row | Decode precedes filtering; malformed name and age produce both original input paths; no success report on error. |
| Reuse | Import the calculation/report function in a second local module and run the same inputs in the CLI and browser | Same values/errors and checked boundary, no private-body access by consumers, unknown dependencies remain visible. |

The report is local and pure: Text and options enter, a typed Result leaves.
The host explicitly supplies input and saves an encoded output on request.
Inspecting a report, encoding it and successfully saving it are three distinct
outcomes. No public network service, secret, task scheduler or language resource
scope is needed to explain this first complete workflow.

### Selected Core And Library Boundary

This selects an initial supported profile from the target. It neither invents
a second language nor reverses accepted semantics for omitted features. Each
row must have source, diagnostics, formatting and portable behavior before
being advertised. The existing prototype may support additional experimental
forms while the release profile remains explicit.

| Include for the first product | Coherent rule | Boundary on the commitment |
| --- | --- | --- |
| Names and local state | Lexical binding; immutable by default; mutation uses `var`/`set` | No separate reactive assignment, automatic dependency tracking or hidden shared state. |
| Values | Exact Int, distinct Bool, exact Unicode Text, Unit; strict List; structural `Value` at external boundaries | The bounded scalar meaning is accepted; portable execution, codecs and measured capacity still need closure. Float/Decimal/Bytes/time APIs are later scope. |
| Calls | One `func` form, ordinary calls, explicit expression lambdas, accepted argument/default laws | No currying, holes, overload resolution or user generic/protocol declaration syntax required for release. |
| Owned concepts | Nominal immutable products and closed variants with explicit constraints | A small declared shape is enough; no universal object hierarchy or arbitrary schema generator. |
| Choice and repetition | Bool `if`, exhaustive `match`, ordinary loops | Ship the needed accepted pattern subset honestly; advanced pattern optimization is not a gate. |
| Expected outcomes | Option and Result as closed alternatives; explicit mapping and `?` | Panic remains separate; no implicit Err filtering, exception-to-Result conversion or changed evaluation order. |
| Data boundary | Strict JSON parse/decode, accumulated independent errors, explicit encode | JSON only initially; CSV conversion, rolling schemas and arbitrary host objects need separate adapters. |
| Collection library | Ordered eager map/filter/fold; synchronous, non-retaining pure callbacks for the selected checked path | Closed type instances still require real contracts and effect checking; user polymorphism is not inferred from examples. |
| Reuse | Local modules, private/public boundary, inferred-or-declared closed public contracts | No registry, solver, remote package install or general public inference algorithm needed first. |
| Touching the world | Explicit console and host input/save adapters with ordinary operation failures | Host-owned transport does not silently introduce source-level File/Network authority or pretend to settle fallible `with`. |
| Understanding | Format, run, inspect a value, follow an error to source/input, inspect a public signature | Explain actual facts; advanced graphs, editable projections and agent-suggested changes are later experiments. |

The notation budget stays the one in [syntax](syntax.md). Accepted conveniences
such as interpolation, `?` and `|>` can share their existing normal forms; they
do not justify extra spellings. The first report uses named intermediate values
and ordinary collection calls so its stages remain easy to inspect. Remove a
convenience from the initial profile if it adds disproportionate implementation
work without improving these journeys; retain its target disposition explicitly.

### What Waits And What Keeps It Possible

| Later capability | Why it waits | Re-entry pressure and preserved boundary |
| --- | --- | --- |
| HTTP, services and concurrent jobs | They add authority, timing, cancellation and remote outcome to an otherwise local task | A second real workflow needs remote work; resource/task packets own grants, bounds and completion. |
| Fallible scoped resources and regions | Host adapters can own the first bounded read/save operations | User code must manage a live handle; preserve explicit owned-value versus scoped-handle distinction. |
| Public generics, protocols and effect polymorphism | Closed exports and checked library instances cover the selected examples | Repeated local libraries cannot express a useful contract; use the existing callback/shared-storage witnesses. |
| Rich numeric, table, array, ML and document APIs | Domain laws and performance costs differ | Add ordinary packages with explicit codecs and effects; only consider scoped notation after calls fail a real program. |
| Editable tables/graphs, notebook semantics and collaboration | Source plus read-only results can complete the first task | Measured creation/repair trouble triggers the paired representation trial; source/revision identity remains available. |
| Package registry, native optimizing engine and multiple polished IDEs | Distribution breadth is not needed to test a small reusable program | Local module identity, portable conformance and versioned producer/consumer contracts leave room for these later. |

Existing research is a reserve of alternatives. Reuse it when a selected
program exposes a missing contract; do not turn every mechanism surveyed into
a required subsystem. No generic plugin framework or universal IR is needed
merely to keep extension possible.

### Bounded Closure Before Coding The Target Slice

October 9 accepts the bounded Int/Bool/Text meaning in
[semantics](semantics.md#first-product-scalar-contract), with
[independent vectors](semantics.md#independent-scalar-vectors) and a decision in
[the ledger](decisions.md#first-product-scalars-october-9-acceptance). Exact Int
avoids both browser rounding and an arbitrary fixed-width overflow law. Bool
is distinct; Text has explicit code-point units and scalar-value ordering.
This does not establish portable implementation or accept every scalar API.

The first report's [bounded boundary rules](semantics.md#first-report-boundary-contract)
now select strict shapes, lexical Int decoding, finite ASCII trim, error order
and explicit encoding. The library bridge below is a proposed experiment, not
implemented target support. Remaining callable/run choices need independent
evidence; broader D1-D3 questions stay open outside this profile.

| Owner / decision | Target disposition | Discriminator and required result |
| --- | --- | --- |
| D3 / scalar and text contract | Accepted: exact Int, Bool distinction, bounded operations, scalar Text/code-point units/order; finite ASCII trim for the report. Pending: portable wire and measured limits | Execute canonical scalar vectors plus retained U+0085/U+FEFF and original numeric-token tests; record capacity refusal separately from wrong values. |
| D3 / data and codecs | Selected closed report shapes, duplicate decoded-key refusal, lexical Int fields, original ordered paths and explicit report wire. Derived target codecs remain unimplemented | Missing/extra/wrong fields, two simultaneous errors, empty/128/129 rows, repeated IDs and limit/limit-plus-one cases through independent parser/decoder producers. A lab success does not admit general schemas or target data. |
| D1 / callable and module boundary | Closed monomorphic public exports; checked pure synchronous library callbacks; local module identity | The invoice and report must resolve every call, default, capture and imported effect. Two passive consumers agree; unknown/private/changed-dependency cases cannot manufacture proof. Explicit adapters are preferable to unexplained inference. |
| D4/D5 / run and host contract | One selected source entry, explicit input/options, a Result inspector, user-requested encode/save; text remains authoritative | Pin entry binding and errors, data limits, source/input/run revisions, stop/restart and host failure behavior. A stale run cannot replace a new result; save failure cannot be shown as completed publication. |

If a candidate fails, simplify the program or library contract first. Any new
language law still needs its canonical syntax/semantics/decision update. A
handwritten demo result, a supplied type record or a passing link checker cannot
close these gates. No new general survey is needed before making the comparisons.

The calculation migration begins with reproduced JS host coercion, while
preserving separately supported prototype operations. It then closes exact Int
transport and execution, Bool boundaries, canonical scalar source spelling and
coordinate conversion before claiming target conformance. The current Python
runner still uses `True`/`False` and does not establish target `true`/`false` or
`none`; the current scalar analyzer can certify host truth testing and comparisons
whose successful values disagree across hosts. Checking policy cannot repair
these differences by changing source meaning. Report implementation now follows
the selected finite trim and external shape below. Internal tagged decimal
transport is distinct from the proposed structural JSON Value experiment;
no budget measurements or implemented transport version follow from this plan.

### Report Library Experiment

This bounded plan is selected before report code. Its normal form is ordinary library
calls: parse, decode, source-defined report transformation, inspect, then encode.
No native `build_report` may hide filtering, normalization or counting. The
[semantic owner](semantics.md#first-report-boundary-contract) holds the rules;
this section owns the proposed bridge and target promotion obligations.

| Selected lab compatibility call | Closed outcome / scope |
| --- | --- |
| `parse_json(text)` | `{ok: true, value: tree}` or `{ok: false, kind: "input-format", errors: [...], complete: Bool}`; exact tokens, duplicate paths and strict scalar Text. |
| `decode_data(tree, schema_name)` | `{ok: true, value: record, defaults_applied: [...]}` or `{ok: false, kind: "decode", errors: [...], complete: Bool}`; only `report-batch` and `report-options` descriptors produce fresh detached structural records. |
| `encode_json(value)` | `{ok: true, text: Text}` or `{ok: false, kind: "encode", errors: [...], complete: Bool}`; only the bounded structural output family in semantics. |
| `trim_text(text)` | Text trimmed by the selected six ASCII scalars, with no normalization; wrong call types refuse. |

Parse success has exactly `ok` and `value`; encode success has `ok` and `text`.
Decode success has exactly `ok`, `value`, `defaults_applied`, recording applied
default paths (empty for batch, `[["minimum_age"]]` for omitted options age).
Failure records have exactly `ok`, `kind`, `errors`, `complete`. Each error has exactly
`code`, `path`, `path_text`, `expected`, `message`; no raw input/value echo or
fabricated source span. These records are compatibility outcomes, not target `Result` or evidence of
nominal immutable `data`. Decoding does not trim the returned fields; the Nomi
function applies `trim_text`, eligibility and report counts after success.
Its selected compatibility form is `build_report(text, options_text="{}")`:
parse/decode the separately supplied options JSON through `report-options`,
whose only field is non-negative Int `minimum_age` with declared default `13`.
Record actual default application; invalid options remain separate from row
errors and defaults never fill missing batch/row fields.
Unknown schema names refuse without executing arbitrary predicates. Manual
schema metadata is a fenced extraction point for admitted `DataDecl`
descriptors, not a user schema DSL or an alternate language specification.

The selected lab tree is `{schema: "nomi.json-value", version: 1, root: node}`.
All node records have exactly the listed fields:

| `kind` | Other fields |
| --- | --- |
| `null` | None. |
| `bool` | `value: Bool`. |
| `text` | `value: Text`. |
| `number` | `token: Text`, validated against JSON number grammar without conversion. |
| `list` | `items: List[node]`. |
| `map` | `entries: List[[Text, node]]`, preserving input key order. |

The decoder validates schema/version, exact record fields, every scalar/tag,
number token, duplicate key, cycle and structural limit before applying the
batch descriptor. Supplied trees are untrusted structured data: matching a
tag cannot certify source checking or host identity. Ordinary untagged input
maps cannot impersonate Number through JSON content; they parse as `map` nodes.
Unknown versions/kinds and malformed records refuse, with no guessed defaults.
The tree contains numeric spelling evidence; it is not a runtime numeric tower
or the target's nominal `Value` implementation.

Prepare literal independent expected vectors for the two-row report, both
malformed field paths, below-threshold malformed rows, duplicate IDs versus
duplicate/escape-equivalent keys, missing/extra fields, Bool/Text/`1.0`/`1e0`
age, empty/128/129 rows, supplementary and invalid Text, and exact-or-refused
wide Int. Pin error ordering and nested CustomerId encoding. The five limits
in semantics, plus the shared accounting below, remain provisional; measure boundaries and retained error/output
behavior before a supported-capacity claim.

Use `prototype/runtime/decode.py` for error records and existing provider
metadata for the ordinary calls. Add small replaceable Python/JS library
owners and a two-descriptor closed schema registry; do not add report branches to Core eval.
Source remains responsible for the report. A compatibility sample may use
current dictionaries, explicit returns and callback-first APIs, with an honest
profile label and real CLI/browser evidence. Keep `overall.nomi` target-only.

Target promotion still needs `pub`/checked local modules, named checked data
construction/defaults/constraints, nominal variants and Option/Result,
`map_error`/`?`, data-first checked library instances, canonical Bool source,
immutable binding rules, source explanations and formatting. Current probes
refuse these forms or lack their runtime/library owners. The scalar analyzer's
unknown library call is not purity proof. Remove manual schema/outcome adapters
only when declaration-derived target contracts and independent consumers replace
them. Neither a useful compatibility report nor passing library tests completes
the first-product target or general D1/D3 contracts.

### Report Admission Gaps

October 9 synthesis closure: the eight planning gaps now have selected bounded
answers below. This completes the implementation brief, not the implementation
or the whole designing packet. The interfaces are selected for the lab; target
nominal data, Result, checked libraries and modules retain their own admission
gates. Scheduling stays in the
[roadmap](../orientation/project_roadmap.md#report-and-target-delivery-gates).

October 10 execution receipt: the bounded compatibility library/source and
default-browser repair/export slice now runs against independent records.
See the [implementation receipt](../orientation/frontier_checkpoint_2026-10-08.md#report-compatibility-completion-receipt-2026-10-10)
for routes, limits, measurements and remaining gaps. The table below retains
the admission obligations: structural outcomes and two manual descriptors are
still a bridge, while source-derived trust, nominal target contracts, separate
input/options host controls and supported production capacity remain open.

| Gap / existing owner | Selected plan and reason | Evidence still required |
| --- | --- | --- |
| Failure classification and completeness; A11/A12/A19 | Keep operation `kind` plus stable rule codes. This identifies the failed stage without duplicating a second category field that could disagree. `complete` describes completed validation at that stage, as defined below. | Literal records for each code, first-error parse, full decode, truncation and capacity refusal; no host crash translated into an input error. |
| Two input boundaries; A12/A18/A19 | Options-first fail-fast, then batch parse/decode; accumulate independent errors within the admitted batch. Invalid policy is repaired before inspecting rows. The outer record names the failed boundary. Defer simultaneous two-input aggregation, which adds partial-stage states without changing the report. | Both inputs malformed; repaired options expose the row failures next. Source/input/options revisions cannot be interchanged. |
| Budgets across stages; A12/A25 | Local byte/depth/node limits plus one run-owned boundary-work and encoded-output allowance. Repeated library calls share it; independent resettable calls cannot establish a bounded run. Count shared children by occurrence, reject cycles and define supplied-tree byte cost below. | Boundary and repeated-call probes, conversion capacity and pinned time/memory measurements. This ledger does not bound source loops or replace worker Stop. |
| Error and path protocol; A19/A30 | Preserve exact segment paths; use one escaped display grammar, static messages and bounded diagnostic serialization. Oversized diagnostic evidence produces an explicit limit refusal, never a silently shortened machine path. Run identity belongs to the host envelope. | Empty/dotted/control/supplementary keys, diagnostic overflow, input revision changes and redaction at nonlocal logging sinks. |
| Structural adapter safety; A03/A09/A12 | Whitelist the existing tagged scalar/list/map families and validate every tree record. Materialize plain data; reject foreign/callable/nominal objects until an explicit projection is supplied. Decode returns fresh records. | Adapter tests independently of library tests, including Bool/Int, null/absent, aliasing, cycles and forged tags. This is an owned structural boundary, not a sandbox for arbitrary native proxies or getters. |
| JSON parser and encoder selection; A12/A17 | Use a bounded token-preserving scanner and deterministic structural writer. Host JSON defaults lose token/duplicate evidence; a hook-based Python adapter would still need early-limit scanning and a separate JS strategy. Keep the scanner behind ordinary calls so it can be replaced. | The exact lexical/escape vectors below on both implementations; no runtime parsing or measured scanner claim follows from this selection. |
| Provider/checker trust; A05/A08/A13/A17 | Declare arity, boxing, failure, purity and capacity as trusted library metadata in the existing inventory. Keep source-inferred facts separately labeled. Unknown or changed providers cannot certify checked exports. | Non-executing check, wrong call types, provider contract invalidation and public diagnostics. Metadata-only registration cannot promote source purity. |
| Replacement and target conformance; A04-A10/A26 | Extract the same two descriptors from admitted DataDecl metadata, then replace outcome maps with nominal Result and migrate consumers. A third manual schema, executable predicate language or ad hoc import mechanism triggers target work first. | The same independent report cases before/after extraction, target source/format/diagnostic agreement and two passive reuse consumers. Compatibility success never closes this gate. |

#### Selected Lab Failure And Entry Records

The four ordinary-call records above are retained. `kind` is the operation:
`input-format`, `decode` or `encode`. The stable codes are:

| Rule code | Meaning |
| --- | --- |
| `NOMI-JSON-SYNTAX` | Invalid JSON token, escape, separator or trailing content. |
| `NOMI-JSON-DUPLICATE-KEY` | A second decoded occurrence of a map key. |
| `NOMI-TEXT-INVALID` | A lone surrogate or other invalid scalar Text boundary. |
| `NOMI-VALUE-TREE` | Malformed tree schema/version/record/tag or cyclic supplied tree. |
| `NOMI-DECODE-TYPE` | Wrong structural field type or non-integer-form Number for Int. |
| `NOMI-DECODE-MISSING` / `NOMI-DECODE-EXTRA` | Absent required field / unexpected field. |
| `NOMI-DECODE-CONSTRAINT` | A validly typed field or container fails its declared predicate. |
| `NOMI-NUMERIC-CAPACITY` | The selected backend cannot materialize an exact Int. |
| `NOMI-BOUNDARY-LIMIT` | Byte, depth, node, boundary-work, diagnostic or encoded-output allowance exhausted. |
| `NOMI-ENCODE-TYPE` / `NOMI-ENCODE-CYCLE` | Unsupported output value / cyclic output graph. |

Parse and encode fail at the first detected violation with `complete=false`;
they do not promise all-error recovery. Supplied-tree validation likewise stops
on its first invalid record. Schema decode returns `complete=true` only after
all independent applicable checks finish; a shape/cardinality failure suppresses
dependent child checks and can still be complete. Numeric capacity and resource
refusals stop validation immediately with `complete=false` and only that refusal;
they do not promise the preceding partial field-error list. The 65th independent
schema error instead returns the first
64 with `complete=false`. Cancellation and unexpected host bugs remain runner
outcomes, not fabricated library failures. Wrong call types, arity and unknown
schema names are caller contract errors before library processing, not bad JSON.

The compatibility `build_report(text, options_text="{}")` performs these stages:
parse options, decode options, parse batch, decode batch, transform. The first
failed stage returns exactly `{ok: false, boundary: "options" | "customers",
failure: library_failure}`. Success returns exactly `{ok: true, report: record,
defaults_applied: paths}`. Default paths refer only to options; the report wire
does not include them. `report_json(report)` separately returns the encode
outcome. An invalid options JSON call is a compatibility entry failure, not a
new variant of target `ImportError`: the target accepts typed `ReportOptions`.

Authoritative path segments remain unchanged. Display is `$` at root, `[n]` for
non-negative indexes, `.key` only for ASCII `[A-Za-z_][A-Za-z0-9_]*`, and
`["escaped key"]` otherwise, using the selected JSON string writer. For example,
`["a.b", 0, ""]` renders `$["a.b"][0][""]`. Expectations and repair messages
are static rule text, at most 256 scalar characters each; raw values, key text
and parser excerpts never enter them. Exact keys remain in local path records.
The host attaches source/input/options/run identity outside the library record,
marks stale results, and excludes input paths from telemetry by default.

#### Selected Lexical And Capacity Rules

JSON whitespace is only U+0009, U+000A, U+000D and U+0020. Reject an initial BOM,
comments, trailing commas, trailing non-whitespace and non-finite numbers.
Number tokens match `-?(0|[1-9][0-9]*)(\.[0-9]+)?([eE][+-]?[0-9]+)?` exactly;
the original token survives parsing. `-0` decodes to Int zero and encodes as `0`.
The parser accepts the ordinary JSON escapes and four-hex-digit Unicode
escapes, combines a high/low surrogate pair, and rejects lone surrogates and
unescaped control characters. Duplicate keys fail upon reading the second
decoded key, before its value; the diagnostic uses that key's structural path.

The writer emits `\b`, `\t`, `\n`, `\f`, `\r` for those five control characters;
other U+0000..U+001F use lowercase `\u00xx`. Quote and backslash are escaped;
slash, supplementary scalars, U+2028 and U+2029 remain literal UTF-8. No BOM,
terminal newline, pretty-print spacing or optional escaping is emitted. Maps
use scalar-value key order; number output is canonical decimal Int.

Each parse call admits at most 256 KiB of scalar-valid UTF-8 input. A supplied
Value tree's byte cost is its equivalent minimal JSON text, using original
Number tokens, map entry order and the selected string escaping; transport
schema/tag overhead is excluded. No serialization need be allocated to measure
that cost. Tree validation and encoding enforce 32 container depth and 8,192
value occurrences independently; keys count toward bytes/work, not value nodes.
Every shared acyclic occurrence incurs its full cost and is independently
decoded; a reference on the active ancestor path is a cycle.

The run host owns one shared boundary allowance, initialized once and passed
through provider adapters: 256 KiB aggregate parse/supplied-tree admission,
1,000,000 boundary-work units and 64 KiB aggregate encoded output. Options count
toward the same input allowance, including the default `{}`. Every call charges
again; decode of an untrusted supplied tree also charges its byte cost even if
it came from a prior parse. There is no trusted-tree bypass based on a tag.
Standalone library tests create an explicit fresh allowance for each case.

A work unit is charged before each scalar consumed by scanning, each record,
field or value occurrence visited, each scalar inspected by validation or a
key comparison, and each output byte emitted. Reinspection charges again.
Before native numeric conversion, enforce the backend's declared decimal-digit
capacity; native conversion failure cannot leak as a schema constraint error.
These accounting rules bound the library work measured by the adapter; they are
not an execution-time guarantee. Receipts identify implementation/profile and
observed charges, because different algorithms may exhaust capacity differently
while still agreeing on successful values.

Each failure envelope also has a 16 KiB UTF-8 serialization ceiling under the
selected writer. If lossless paths/errors exceed it, return a single
`NOMI-BOUNDARY-LIMIT` at root, expected `bounded diagnostic output`, message
`Validation stopped at the diagnostic budget.`, and `complete=false`. Earlier
oversized evidence is discarded explicitly; no partial machine path or omitted
total is invented. Checking this ceiling uses a separate bounded writer and
does not consume the report-export allowance; the fixed fallback always fits.
The 64-error cap continues to apply when diagnostic bytes fit.

All numeric limits are provisional lab settings, not supported-capacity
claims. Local measurements are recorded in the implementation receipt;
representative host validation remains an execution gate, not an undecided accounting
rule: test below/at/above each limit, repeated calls, escaped expansion, shared
graphs and huge tokens on pinned Python/Node/browser hosts; record peak memory,
elapsed time, refusal stage and preserved output. Source/evaluation work,
stdout retention and Stop/restart remain separate runner admission gates.

### Independent Report Oracles To Materialize

These expectations come from the selected report laws and target program, not
captured output. They are prepared fixtures; none has been executed as a report
in this planning pass. The error codes and outer outcome now follow the selected
lab contract above; the checked-in
[literal cases](../../prototype/tests/data/report_boundary/v1.json) materialize
the first handoff vectors. They are expected evidence for future implementations,
not generated snapshots or proof of conformance.

| Input / action | Expected value or refusal |
| --- | --- |
| The target's Ada/Bo input; omitted options age | `received=2`, `eligible=1`, `skipped_ineligible=1`; one customer with ID `c-1`, name `Ada`, age `20`; record options default path `["minimum_age"]`. |
| Same input, explicit minimum age `0` | Both rows in original order; counts `2/2/0`; no applied default. |
| Empty batch, valid options | Counts `0/0/0` and an empty customer list; no special empty-result failure. |
| One row with ID `c-1`, blank name and age `-1` | Name path then age path; no report, even though age is ineligible. Repair both fields and rerun without reusing the old failure. |
| Same valid ID on two eligible rows | Two customers, original order and independent normalized names; no merge or uniqueness failure. |
| Options `{}` versus `{"minimum_age":13}` | Same eligibility, distinct default provenance. Missing `age` in a row still fails. |
| Age token `true`, `"20"`, `20.0` or `2e1` | Int-field refusal. None becomes Int `20`; each independently valid neighboring field still receives its checks. |
| Duplicate `name`/`\u006eame` in one object | Format failure at the decoded `name` path before schema decode; repeated IDs remain permitted. |
| An eligible age token `9007199254740993` | Exact value where supported; explicit numeric-capacity refusal otherwise. Cross-host equality of rounded output is never a pass. |
| 128 valid rows versus 129 | First is admitted if resource budgets also allow it; second reports cardinality at `["customers"]` without row decode. |
| 64 versus 65 independent validation errors, within byte/work allowances | Exactly 64 retained; `complete=true` only when validation finishes without omission. On observing error 65 return the first 64 and `complete=false`, with no invented total. A diagnostic-byte refusal follows its separate incomplete rule. |
| Successful report, failed encode or host save | The report remains inspectable. Encode/save failure cannot become a successful export or rerun the computation implicitly. |

For the first row, the selected deterministic encoder's exact UTF-8 text is:

```json
{"customers":[{"age":20,"id":{"value":"c-1"},"name":"Ada"}],"eligible":1,"received":2,"skipped_ineligible":1}
```

Add vectors for every admission decision as it closes, including limit-minus-one,
limit and limit-plus-one for the chosen accounting units. Compare four routes:
standalone boundary functions, public Python execution, Python-produced Core/JS,
and committed-WASM-produced Core/browser. Two consumers of the same lowering are
not independent parser evidence. A refused unsupported route is recorded as
refused, not skipped silently or counted as conformance.

## One Coherent Model

### October 9 Planning Synthesis

The first product now has one causal path: explicit Text/options enter a strict
boundary, valid rows become a report through ordinary source functions, and the
user inspects that result before explicitly encoding or saving it. Decoding,
eligibility, normalization, encoding and host publication have different owners
and observable failure stages. Error paths retain the original input; source
checking and runtime capability do not silently change this meaning.

This path needs a small number of composable language mechanisms: scalar laws,
lexical names, checked calls, immutable nominal data, constraints, closed failure
values and structural choice. JSON, trim and eager collection operations belong
to libraries. No new grammar, universal schema/evaluator, generalized query
system or framework is needed to implement the bounded report experiment.
The compatibility bridge is deliberately temporary: declaration-derived data
replaces manual schema metadata, Result replaces outcome maps, and public module
evidence replaces trusted local wiring as those target mechanisms become ready.

The planning result is complete at that boundary: product selection, precise lab
rules, independent expected records, implementation owners, dependency order,
replacement triggers and completion evidence are explicit. The immediate next
action is executable library comparison. A missing measured capacity or an
unperformed browser/user trial is an execution obligation, not an invitation to
invent another semantic choice or repeat the research survey.

The larger language remains open in bounded ways. D1 still owns public inference,
callback/generic/effect and module identity comparisons; D2 owns resources,
cancellation and task completion; the cognitive packet owns observed benefits of
alternative representations. Domain and engine expansion follow the existing
frontier ledger. None is implicitly accepted by this report, and none must be
solved merely to run its closed library experiment. Reopen this synthesis only
when a concrete program or independent vector contradicts a selected law, the
two-descriptor bridge needs a third schema, or a target extraction cannot preserve
the established observations. Record that counterexample in the existing owner.

Nomi should borrow semantic mechanisms, not accumulate familiar spellings.

| User act | Evidence synthesis | Nomi shape | Cost paid |
| --- | --- | --- | --- |
| Name | Python's immediacy plus lexical/immutable reasoning | Inferred immutable binding; `var`/`set` for change | Breaks Python assignment habits. |
| Transform | First-class functions without multiple call/control rules | `func`, explicit expression lambda, ordinary calls | More helpers and explicit partial application. |
| Model | ML-style alternatives plus nominal package identity | Immutable product/closed variant `data` | Adapters and breaking variant evolution. |
| Choose | Exhaustive structural choice without hidden extractors | Bool `if`, bounded transactional `match` | Explicit classifiers and host adapters. |
| Repeat | Familiar verbs with domain-specific execution laws | Eager List; explicit Stream/TablePlan/Array APIs | Multiple typed domain contracts, not one magical pipeline. |
| Fail | Typed expected outcomes distinct from absence and bugs | Option, Result, `?`, separate panic/cancellation | Explicit context mapping and outcome composition. |
| Touch the world | Resource and task ownership plus host boundaries | Lexical cleanup, `uses`, grants, cold tasks/groups | Signatures and lifecycle policies require care. |
| Understand | Live inspection, source provenance, package contracts | Shared diagnostic/artifact model, examples/checks | Tooling must be designed with semantics, not appended later. |

These choices largely reaffirm the accepted target. This pass does **not** add
keywords, extractors, implicit conversions, generic declaration syntax, macro
quotation, or a second query language. A beautiful short example is not enough
to admit any of them.

## Candidate Primitive Synthesis And Integration Path

> Designing hypothesis, 2026-10-10. These six semantic families organize a
> comparison; they are not accepted opcodes, syntax, or a universal domain IR.

The research can converge on a small common substrate while keeping domain laws
explicit. Compare this model against both a smaller lambda/variant kernel and
richer domain-specific primitives. A smaller encoding wins only when its behavior,
checking, debugging, and user activity remain understandable. The eight teaching
acts remain useful; the families below concern semantic obligations instead.

| Family | Minimal responsibility | Law that cannot disappear in an encoding |
| --- | --- | --- |
| Value | Construct/project atoms, products, variants, and explicit opaque handles | Runtime type/nominal identity and invariant-preserving owned construction; received structure is separate |
| Bind | Associate resolved identities with values or explicit cells; capture lexical relationships | Value/cell capture, fresh allocation, shadowing and package declaration identity survive rewriting |
| Apply | Invoke a callable with a declared shape and completion contract | Eager once-only ordered inputs/defaults, exact return target, effects/captures and expected failure |
| Choose | Select a branch by Bool or inert structural elimination | Only selected work runs; tentative pattern bindings commit atomically; guards do not become arbitrary extractors |
| Perform | Request a named local-state, host, or scheduler operation through its owner | Validation before state publication; world authority, representation and suspension are explicit and distinct |
| Scope | Bound the lifetime of resources, work, and control completion | Enter/body/release phases, all causes, child joins and escape rules remain observable |

Perform does not introduce a new global effect taxonomy: local cell mutation and
world access retain their existing distinct contracts. Scope is a family of
specified policies, not a universal user-defined block handler. A resource scope,
function return boundary, and task group cannot share an unspecified completion
rule. Observed traces, revisions, types, and contracts accompany these operations;
they are evidence dimensions, not a seventh universal runtime object.

### Compose Richer Features

The formulas below are semantic metalanguage, not Nomi source or proof that the
present runtimes implement the reduction. Each names a remaining obligation.

| Feature | Composition | Remaining obligation |
| --- | --- | --- |
| Option / Result | Value variants + Choose + Apply | Absence, expected failure, panic and cancellation stay separate |
| `?` / `??` / `?.` | Choose the relevant variant + return/apply the selected continuation | Preserve short circuit and nearest-function propagation; no hidden error conversion |
| Constraints and decoders | Apply checks to tentative typed fields + Value construction + owner-controlled publication | Accumulate independent external errors; internal invariant violations retain their own channel |
| Immutable update / `set` | Bind an immutable replacement or Perform a validated cell update | Atomicity is scoped to the actual owner; no implied distributed transaction |
| Methods and protocols | Value of supplied operations + Bind identity + Apply | Selection, coherence, variance, effects and capture facts must be checked |
| List map / filter / fold | Apply + Choose + explicit ordered traversal/state | Strict versus demand-bearing carriers; Result elements do not auto-propagate |
| Retry | Apply a fresh attempt under an explicit policy + Choose completion | Partial effects, idempotency and cancellation; replay is not rollback |
| Resources | Perform acquire + Scope body/release + Choose typed completion | Non-escape through successes, errors, closures, tasks and diagnostics |
| Async / streams | Value description + Perform start/poll/suspend + Scope ownership | Backpressure, single/repeated consumption, child failure and release policy |
| Tables / statistical plans | Value of typed domain nodes + Apply checked composition + explicit execution operations | Grain, null, shape, ordering, numeric theory and adapter conformance |
| Symbolic rewriting / derivation | Value expression/schema + Apply a declared transformation + Bind preserved identities | Theory, stage, hygiene, source provenance, budget and unknown proof status |
| Semantic commands / views | Value candidate/projection + Apply validation + Perform owner commit | Revision freshness, review scope, authority, unsupported content and domain-specific inverse laws |
| Modules / checked reuse | Bind declaration identity + Value complete interface + Apply imported callable | Separate checking, verification dependencies and compatibility evidence |

Iteration/suspension and runtime memory machinery still need operational rules.
Encoding them as recursive functions or library protocols does not establish
bounded stack space, progress, scheduling fairness, or cleanup. Numeric operations
and native handles also retain profile-specific primitive implementations. The
model reduces repeated semantic concepts; it does not claim every mechanism is
free or that every domain has the same algebra.

### Gap Analysis With Concrete Closure Receipts

| Gap now | Required receipt | Dependency and tradeoff |
| --- | --- | --- |
| No complete common callable evidence for the broad target | Closed positive/negative call contracts, then general capture/effect/region fixtures | Start monomorphic; general inference increases reuse and checker complexity |
| Nominal/structural boundary not fully source-derived | Typed construction/decoder derivation and independent malformed-input paths | More adapters buy invariants; copying versus foreign sharing stays explicit |
| Operation selection and variance remain open | Two intentional behaviors, colliding packages, mutable-container substitution, erased-callable limits | Explicit operation values cost plumbing; ambient resolution costs local reasoning |
| Resource/task guarantees rely on supplied facts/models | Escape rejection plus deterministic enter/body/release/cancel traces and owned children | GC simplicity does not establish external validity; stronger restrictions reduce escapes |
| Domain optimization laws are not mechanically checked | Typed inert plan, declared theory, side conditions and independently checked rewrite steps | Restrict the first theory; broader rewrite power raises proof and diagnostic cost |
| Interactive evidence can outlive its basis | Revision/dependency-bound inspection and owner-enforced stale publication refusal | Frozen runs retain predictability; live adoption costs reproducibility and memory |
| Statistical abstractions lack a common checked interface | Input-free schema/plan checking, named intermediates, exact mean decomposition, explicit unresolved assumptions | Abstract ports enable replaceable engines; schema checks cannot certify actual data or inference validity |

### One Ordered Path

Use the existing D0-D7 owners; these increments are a dependency path through them,
not another release schedule. Discovery can continue while an implementation
increment is open. Close only the promises of the selected slice.

| Step | Work and accountable owner | Exit evidence | If it fails |
| --- | --- | --- | --- |
| 1 | Derive the existing report through Value/Bind/Apply/Choose; language-coherence with function contracts | Every call, type, default, failure and callback has a named contract; unresolved facts remain visible | Narrow the checked subset or improve the contract; never insert Any |
| 2 | Extract a replaceable typed-plan interface for the selected data/statistical workflow; data owner under language-coherence | Declared input ports suffice for structural checking; every intermediate can be referenced; no scan/UDF/collect during checking | Separate data-dependent schema discovery or opaque callbacks into explicit unsupported/runtime obligations |
| 3 | Establish one bounded equational theory, beginning with exact mean and defined empty/missing policy | Proof records name rewrite definitions, source/grain/mask/profile, and every required assumption | Return conditional/unknown; preserve original plan and prohibit an unjustified optimization |
| 4 | Compare adapters behind that interface, starting with one pinned execution profile | Engines either preserve the interface's values/absence/errors/order or refuse; logical plan identity stays independent | Name a backend-specific profile or conversion cost; do not change interface laws silently |
| 5 | Add one scoped execution case only when needed; resource/function owners | Complete cause/escape/cancellation traces and owned work; inspection remains passive | Retain explicit synchronous execution; keep the richer lifetime candidate open |
| 6 | Reuse and inspect the same checked workflow from two consumers; cognitive packet owns representation comparison | Independent consumer checking, revision invalidation, named intermediates and repair/handoff observations | Improve interfaces/diagnostics before adding another syntax |
| 7 | Admit a proven useful convenience or generalization | Long form, formatter, lowering, diagnostics, independent conformance and removal criteria agree | Keep the ordinary composition; a failed shorthand does not reject the domain need |

The immediate next action is step 2's inert statistical/data interface and step
3's bounded mean law, following the user's requested data-platform direction.
This is an isolated design experiment; it does not declare the broad target
implemented or make all prior language topics prerequisites for investigating it.
The [maintainer guide](../research/synthesis_guide.md) owns the research worksheet
and interaction counterexamples. The [agenda](redesign_agenda.md) keeps D0-D7;
the [roadmap](../orientation/project_roadmap.md) still owns distribution scheduling.

## Where The Previous Program Broke Down

The [legacy target](target.nomi) exposed useful ambitions but hid interactions:

1. CSV rows were decoded into Int and Instant fields without an explicit text
   conversion policy. Strict decoding cannot imply those conversions.
2. Mapping a per-row decoder and collecting Results did not specify preservation
   of original row paths or accumulation behavior.
3. "Rejected" counted age-ineligible valid rows, while malformed data aborted
   the workflow. That is misleading report terminology.
4. Normalization entered constrained constructors without a stated preservation
   argument. A transforming boundary needs validation if predicates can change.
5. TaskGroup had a running limit but no named abnormal-failure policy, queued
   memory bound, or public composed-outcome contract.
6. Config acquisition, retry, and generated codec APIs were underspecified;
   Clock and other inferred effects could disappear from an attractive signature.
7. Constructor values and callback generics/effects were assumed by examples
   before their declaration and dispatch rules were settled.

The earlier combined fixture improved those boundaries, but still made a useful
local report depend on network, task, resource and publication design. The
October 9 product synthesis removes that dependency from the active
[overall fixture](targets/overall.nomi). It now validates a maximum-128-row
batch, preserves original error paths, filters valid rows, normalizes names,
and returns an owned report. Repeated IDs are retained in source order because
rows are observations, not updates to an identity registry.

The pure function does not publish files. An explicit encoder and host save
operation follow inspection. Proposed codecs and callback contracts remain
labeled; byte/depth/work limits are not implied by a row count. The richer
network/resource program remains in Git at `915aea1`; category and focused
resource/concurrency fixtures retain its extension pressure.

## Interactions To Resolve First

Use the four [bounded closure decisions](#bounded-closure-before-coding-the-target-slice)
for this product. General cleanup outcomes, handle escape, task failure policy,
queue bounds, effect polymorphism and schema evolution remain owned by their
existing packets. They become release blockers only when a selected workflow
requires those guarantees. The executed resource comparison is useful symbolic
evidence for later expansion, not a prerequisite for a pure local report.

## Action Sequence

| Order | Reviewable deliverable | Visible outcome and admission |
| --- | --- | --- |
| 1 | Agree the three first-product journeys, source fixture and explicit exclusions | A person can explain the promised product before reading compiler plans. |
| 2 | Close the selected scalar, codec, closed-call/module and host-run contracts | Every operation in the local report has an owner, independent expected behavior and a useful failure. |
| 3 | Implement the smallest complete calculation path, then report decode/repair | Source, checking, lowering, formatting and diagnostics agree on the supported subset; no disconnected subsystem counts as a finished product slice. |
| 4 | Add reusable local boundaries to those same programs | Two consumers can use checked public evidence; unknown dependencies remain honest. |
| 5 | Promote supported examples and complete the browser/CLI journey | Actual user-path checks, matching values/errors, fresh assets and installed/browser evidence. |
| 6 | Validate distribution, then select the next real workflow | Traceable artifact and rollback; only measured pressure admits later resource, task or domain work. |

The [project roadmap](../orientation/project_roadmap.md#delivery-order-and-dependencies)
owns M0-M5 scheduling. The pattern pass continues within the accepted subset;
a whole-pattern rewrite, every callback mechanism and a new interface framework
are not prerequisites. The dated bridge records why this order changed.

## Prototype Evidence And Next Admission

### October 8: exploration and selected assurance

The latest direction reopens mandatory public annotations. Canonical
[semantics](semantics.md#progressive-assurance) now accepts dynamic exploration
with honest unknowns and checked interfaces whose complete contracts may be
inferred locally or declared. Source semantics, selected checking restrictions,
runtime authority and engine choice remain independent. The whole-program
fixture includes an inferable public batch limit and a negative unknown-call
boundary; neither supplies a general inference algorithm.

The conservative scalar/direct-call module experiment is now preserved at
6aec9f3: an unannotated invoice, output that defeats purity, and an unknown
dependency that defeats closed evidence. Its type and purity requirements are
independent. The [checkpoint](../orientation/frontier_checkpoint_2026-10-08.md)
distinguishes passing analysis/integration checks from unresolved hosted
continuation failures. Call-context facts must not be generalized into public
proofs; uncalled function effects must not become module effects. This bounded
experiment leaves D1/D2 and dynamic package adapters open. Research
still routes through [the feature packet](../research/features/README.md) and
[the bridge](../review/2026-09-29-language-synthesis.md).

The October 4 delivery pass converts selected research into bounded runnable
experiments and interaction repairs. It deliberately does not turn all research
categories into language primitives. These observations constrain future design
but do not settle its open contracts:

| Research pressure | Runnable evidence | Still unresolved |
| --- | --- | --- |
| Text as a composable interface | `samples/text_pipeline.nomi.nb`: explicit whitespace trimming, delimiter split, conversion, ordered state and bounded windows; code-point access fixtures in both JS parser routes | Exact scalar-sequence meaning and code-point units are accepted; validity, portable ordering, offsets, explicit trim/normalization, localization and safe rendering still need implementation evidence |
| Pragmatic generic operations | Ordinary `fold(items, seed, combine)` and seeded `scan`; empty, order, callback-failure and reference-history tests | Typed generic callbacks, effect checking, immutable history, parallel merge laws and conditional object protocols |
| Data dependencies and time | `samples/data_pipeline.nomi`: visible filter/map/fold stages and integer cents | Typed dependency descriptions, snapshot/time axes, incremental execution and durable provenance |
| Cognitive repair and observation | Source-linked known errors, per-execution output, document/run generations and stale-result labels; inspection distinguishes missing evidence from known empty/zero records | Full source maps, semantic commands, task unwinding, usability/accessibility study and durable revision identity |
| Portable values and boundaries | JavaScript exact-integer range rejection; shallow tagged slices; special text keys preserved without inherited host fields | Exact first-product Int is accepted; tagged transport, measured capacity, Text/Bytes validity, equality/hash/map identity, scalar codecs and cross-host conformance remain unfinished |
| Eager failure and callable boundaries | Portable errors stop later eager work; partial Core call shapes reject unsupported names/parameter kinds before effects | Versioned named/default/callback binding, typed expected outcomes and composed abnormal completion |

The next target delivery step is the bounded first-product closure above. Broader
discovery proceeds alongside it under the vision and can revise that direction.
Use runnable collection traces as behavioral evidence, not as proof of typed callbacks.
Co-design general callbacks and resources when the later resource workflow is
selected; do not make their full D1/D2 resolution a prerequisite for this report.

AI/ML, web, scientific and documentary domains retain their distinct library/
plan owners in the proposal below. A browser worker being terminated is not a
language-level cancellation/cleanup implementation; a sequence of source edits
is not data time travel. Those distinctions keep a cohesive language possible
without claiming that small prototype experiments implement entire domains.

## Growth Journeys And Boundary Evidence

October 9 planning continuation. These are conditional design comparisons and
prepared expectations, not executed target programs or additional accepted
syntax. They connect the existing fixtures to the first reusable product slice.
The [frontier plan](../../FRONTIER_PLAN.md) owns execution order; this section
owns the whole-program questions. Do not replace the wider invoice/import/job
journeys with the scalar prototype simply because it is runnable.

### Invoice: Explore, Extract, Then Share

Start with the runnable `scripts/check_invoice.nomi`: `subtotal(1200, 3) + 250`
prints `3850`. Change quantity to 4 in a new source revision: the expected result
is `5050`. No floating-point money, currency conversion or rounding claim is
needed. The richer [invoice fixture](interaction_model_target.nomi) separately
uses Tea/Cup rows and totals `1500`; keep the same inputs within each paired
representation comparison.

The important transition is extracting a reusable function. The unannotated
`price * quantity` body does not by itself select Int multiplication from every
possible protocol. One observed Int call cannot select a universal public type.
Compare an inferred contract where the owner has sufficient evidence with an
explicitly directed boundary:

```nomi
pub func subtotal(price: Int, quantity: Int) -> Int:
    return price * quantity
```

This uses accepted target syntax but is not a claim the scalar checker can
verify annotations or export modules. Scalar operations still need an owned
numeric profile. The body and meaning stay the same; the public promise is now
checkable independently of clients. Negative-price validation would be a new
domain requirement, not something a stricter type policy may silently invent.

| Step | Prepared observation | Failure and repair |
| --- | --- | --- |
| Create and inspect | Calculation facts are distinct from the ConsoleWrite action | Unknown arithmetic dispatch stays an obligation, not a guessed Int. |
| Revise | New source gives 5050; old result keeps its source revision | A late 3850 result stays historical and cannot overwrite the new run. |
| Restrict | Type and purity checks examine the same source facts | `print` blocks whole-script purity; inspect/extract the pure calculation, or retain the effectful script policy. |
| Reuse | A checked consumer reads the exported contract without executing or inspecting private module code | Ambiguous public parameters require direction; do not specialize the library from its first client. |
| Repair | Explain the call site, public promise and missing evidence together | Fix a mismatched argument or establish the owner contract; an annotation alone cannot certify an unknown host call. |

Prepared policy matrix for the existing module-execution experiment:

| Source | Preview | known-types | pure | both |
| --- | --- | --- | --- | --- |
| Scalar calculation only | Facts available | Satisfied | Satisfied | Satisfied |
| Same calculation plus scalar print | Facts plus ConsoleWrite | Satisfied | Unfulfilled | Unfulfilled |
| Used unknown external call | Unknowns visible | Unfulfilled | Unfulfilled | Unfulfilled |
| Unknown call only in an uncalled plain function, with no defaults/annotations | Latent obligation visible | Module obligations can be satisfied | Module obligations can be satisfied | Module obligations can be satisfied |

The last row would **not** satisfy a complete exported-function policy for that
body. Every verdict names its scope. A malformed policy is a request error;
unknown or contradicted evidence cannot satisfy an obligation. Preview success
means a report was produced, not that the program is proved safe. Policy order
must not affect facts, obligations or admission; there is no `pure wins` rule.
Profiles may name sets of restrictions only if their expansion and prerequisites
are inspectable. Package syntax and a general prerequisite solver remain open.

Proposed terminal explanation for the reusable unannotated multiply:

```text
Cannot establish a checked public contract for subtotal.
The multiplication does not determine price and quantity's parameter types.
Declare the intended parameter types, or keep this definition exploratory.
The observed call subtotal(1200, 3) is evidence for that call only.
```

The editor relates the public declaration and multiplication; the machine record
needs an exported-function scope, unresolved parameter/protocol obligations,
evidence origin and those source relations. Code names/schema are not assigned
by this example. If the producer lacks real spans, show the function/source
revision without inventing a location. Adding Int declarations directs checking;
the body must still be verified against that contract.

### Import And Report: Keep The Boundary While Growing The Program

Use `build_report` and `report_json` from
[the overall fixture](targets/overall.nomi). Inspect a Result on in-memory Text,
repair the input, then reuse the same function through an explicit host adapter.
Relaxed static checking never bypasses decoding.

| Prepared input/event | Expected observation | Repair or owner |
| --- | --- | --- |
| Empty name and age -1 | Both indexed paths, no successful report | Fix both fields; filtering may not hide malformed rows. |
| Valid age 12 with minimum 13 | received=1, eligible=0, skipped_ineligible=1 | Change the eligibility policy explicitly if intended. |
| Duplicate customer IDs | Preserve both rows in original order | This is a report over observations, not an update registry. |
| 128 rows with an enormous Text | Row count is insufficient to admit the input | Host/codec byte, depth, work and diagnostic budgets apply. |
| Unknown field, duplicate JSON key or rounded host number | Refusal under the selected strict codec contract | Never silently coerce, drop information or fabricate exactness. |
| New source/input while an old run finishes | Old result remains historical | Run identity prevents replacement of the current result. |
| Encode succeeds but host save fails | Report remains inspectable; save is failed or explicitly uncertain | Repair the host destination; do not rerun pure computation unnecessarily or claim publication. |

The pure `maximum_batch_size()` remains the first small public-inference
discriminator. Private comments may preserve its contract while invalidating
source verification; result/effect changes may break compatibility. Consumer
observations and backend switches cannot repair an incomplete public contract.

Network grants, response identity, lost remote acknowledgment and task cleanup
remain important later pressure in the resource/concurrency fixtures. They do
not belong to the first report's error type or release dependency chain.

### Resource Job: Reuse The Operation Without Exporting Its Lease

Use `read_text`, `copy_text` and `receive` from
[the resource fixture](resource_lifetime_target.nomi). The library long form
already separates resource description, enter, body and release. Exploration
can omit static facts but cannot omit promised runtime revocation or cleanup.
Checked reuse must carry callback effects, the fresh region and whole-completion
non-escape; it may return owned Text or Bytes, never a hidden retained reader.

Creation-to-repair story: read owned text; inspect the enter/body/release trace;
extract the operation into a reusable function; select a lifetime obligation;
reject an escaping callback; repair by returning an owned value while the
resource is live. That repair changes when work happens and must be explained,
not applied as an allegedly equivalent rewrite. Body error plus release error
retains both causes. Cancellation is observed only after required join/cleanup,
or as explicitly incomplete when the host cannot finish. The
[resource discrimination table](resource_lifetime.md#remaining-completion-experiments)
owns exact expectations and remaining choices.

### Evidence That Must Survive All Three Journeys

Proposed artifact distinction, refining the accepted assurance direction:

| Record | Identity and validity basis | Consumer obligation |
| --- | --- | --- |
| Source evidence | Exact source revision, edition, producer/rule version, dependency basis and numeric/host assumptions actually used | Refuse unsupported or stale evidence; never promote supplied examples into inferred facts. |
| Public contract | Module/declaration identity, exported types/effects/call shape and supported contract version | Check compatibility without private client code; a same-named type from another package is not automatically identical. |
| Verification record | Contract plus the implementation/dependencies it was checked against | A private edit may preserve the contract while requiring a new verification record. |
| Build/run selection | Exact executable content, profile and input snapshot | Recheck current authority at effect boundaries; static evidence is not a transferable grant. |
| Explanation/view | Source or value epoch, completeness and redaction | Keep unavailable spans and omitted facts explicit; formatting a new revision cannot reuse old offsets blindly. |

At the local-reuse milestone, the contract experiment should use a locally
produced, closed monomorphic scalar contract. Unknown dependencies prevent checked export. An explicit dynamic
adapter remains a challenger for later work: runtime shape checks alone cannot
certify purity, non-escape or termination of arbitrary foreign code. Do not
design a universal adapter before stating which of those guarantees it enforces.

## Domain Layer Proposal

Status: designing hypothesis; no new syntax, core IR or public APIs accepted.
The [data/time research](../research/data_workflows/dependencies_and_time.md),
[AI/ML survey](../research/data_workflows/ai_ml.md) and
[cross-domain synthesis](../research/domain_composition.md) extend the existing
four-layer model. They test a language that can host rich domains coherently,
without assigning a new meaning to ordinary calls or pipelines.

The [messaging and event architecture continuation](../research/data_workflows/messaging_and_events.md)
adds durable communication pressure to this same proposal. Actors/channels stay
library-first; no broker syntax or universal reliable-delivery primitive is
accepted. Transport evidence does not establish business completion.

Existing typed values, immutable data, explicit functions, Result, constraints,
effects, lifetimes, tasks and modules are the common foundations. Candidate
shared contracts are contextual references, typed descriptions/relations,
domain-owned transitions, interpretation/execution boundaries, evidence and
revision-bound projections/commands. They initially belong to libraries,
protocols and tooling; metadata is attached only where the artifact needs it.
Do not add a universal object/graph wrapper to every value.

| Pressure | Proposed semantic owner | Boundary that must survive composition |
| --- | --- | --- |
| Dependencies | Typed relation library; checked DAG specialization | Prerequisite, lineage, attribution, numeric dependence and feedback differ |
| History | Storage/temporal library | Version, valid time, system/availability time, replay and compensation differ |
| Learning | Numeric/learning library; scoped numeric tool if earned | Specification, learned artifact, training checkpoint and evaluation differ |
| Messaging | Channel/transport/storage libraries and verified adapter profiles | Event versus attempt identity, ownership, settlement versus progress, atomic scope and replay versus authorized effects differ |
| Knowledge/documents | Reference/edition/interpretation library | Labels, entities, evidence, formal rules and human interpretation differ |
| Shared inspection | Tooling envelope, domain-owned payload and source maps | Captured evidence versus current observations; preview never executes |
| Execution adapters | Domain/profile owner, effects/resources/tasks | Checked description versus current grants, completion and uncertain outcome |

Recommendation: one source language with ordinary domain packages and explicit
scoped tools, not global web/data/ML modes. Domain IRs remain distinct and can
lower through versioned checked adapters. One diagnostic/evidence envelope
does not imply one algebra, optimizer, identity or truth system.

The [composition target](targets/research/domain_layers.nomi) supplies report,
train-only description and failure-heavy reviewed-publication long forms using
fictional facades. It has not been parsed/typechecked/executed. The
[local probes](../research/data_workflows/composition_experiments.md) execute
selected finite discriminators, not these APIs or foreign engines. No DAG,
time-travel, tensor, learning or natural-language keywords are admitted.

The [messaging target](targets/research/messaging.nomi) challenges ordinary calls
with a pure reconstruction, one-delivery local inbox/state/outbox transaction,
and failure-heavy relay/reconciliation. It is also fictional and untyped.
Candidate envelope, endpoint, delivery, position, transition and budget contracts
compose into queues, subscriptions, logs, projections, sagas and durable
workflows; they are not six new core types imposed on every object. Keep a
guarantee's participants, ordering scope, retention horizon and failure model
visible. Unknown remote outcome is not ordinary rejection; local cancellation
is not remote rollback; an old grant is not replay authority. Library receipts
must not interchange queue settlement and partition checkpoint semantics.

MSG1-MSG6 remain subgates of D1-D3 and DC1/DC5/DC6. The ten captured finite
countermodels falsify selected naive policies only. Admission still requires
typing the three programs and independent crash/recovery vectors for one pinned
adapter; no broker, durable storage, async scheduler or authenticated authority
was exercised by those models.

Admission order remains D1-D3 then D4: resolve generic/schema/callback/effect/
region and scalar/codec/identity contracts; type the composed program; compare
one data, one numeric and one documentary adapter under DC1/DC5. These studies
extend existing questions 4/7/8/9/11/12/15/17, not a second implementation backlog.
Only evidence that ordinary calls fail three representative programs can justify
scoped notation. A further core primitive needs a concrete missing semantic
contract, an independent conformance slice and an explicit removal criterion.

## Admission And Stop Rules

A target category becomes a supported sample only when it has one meaning
across source, typing, effects, lowering, runtime, diagnostics, and formatter.
Passing doc tests proves links/status/packet consistency, not target parsing or
execution. Keep these sources outside `samples/` until that gate is met.

Library-first is not ambition reduction: tables, arrays, actors, build plans,
and symbolic work remain important. It is a way to discover durable laws before
fixing notation. Admit a scoped surface only if explicit calls genuinely fail
a domain program and the alternative has hygiene, budgets, source maps,
inspection, and a removal path. Stop research when an experiment distinguishes
the candidates, and promote the result into the canonical contract.
