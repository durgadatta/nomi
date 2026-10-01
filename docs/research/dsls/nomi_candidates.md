# Nomi DSL Candidates And Discriminating Experiments

> Status: research synthesis and bounded experiments; no syntax/API admission.
>
> Completes the requested documentary research pass. Runtime integrations,
> reader studies and target-language experiments below remain unperformed.

## Research Judgment

Nomi should first test typed domain values, ordinary functions, explicit
decoders, separate parameters and inspectable plans. Parsed foreign DSLs are
useful when users already need that language. Scoped notation remains a
candidate only when ordinary APIs repeatedly fail a concrete readability task.
This is a research recommendation, not a decision-ledger amendment.

The main design opportunity is **making language boundaries explicit while
keeping common string work easy**. Do not turn `needs`, `uses` and `with` into
core workflow syntax merely because their domains use them. Nomi already has
a language meaning for `uses` in effect contracts; a GitHub adapter can own its
own field vocabulary without changing that meaning.

The target remains owned by [syntax](../../design/syntax.md),
[semantics](../../design/semantics.md),
[industrial contracts](../../design/industrial.md) and
[decisions](../../design/decisions.md). Research does not define a new frontend
extension point or a universal execution engine.

## Three Competing Approaches

| Candidate | Construction | Strength | Risk / removal criterion |
| --- | --- | --- | --- |
| A — Ordinary typed libraries | Data, nominal wrappers, functions, callbacks, encoders | Existing recognition path; visible APIs and effects | Remove any wrapper that conveys no enforced guarantee; measure verbosity on real nesting |
| B — Explicit parsed DSL values | Parse/check named foreign source; bind values separately | Native foreign notation and meaningful diagnostics | Remove if version/context/spans cannot be retained or execution sneaks into checking |
| C — Scoped notation lowering to A/B | A deliberately bounded source form with explicit semantic owner | Potentially clearer domain composition | Reject unless it outperforms A/B and has hygiene, formatting, recovery, types, effects and an inspectable reduction |

These can coexist by domain. A workflow graph naturally uses structured
objects; a regex naturally uses pattern source; a configuration file imported
from another system needs a lossless draft and a decoder. Coexistence is not
permission for arbitrary user-defined grammars.

Illustrative operation names, deliberately shown as pseudocode:

```text
source -> yaml.decode(profile, limits) -> Value -> Resource.decode(schema)
pattern_source -> regex.parse(dialect) -> ParsedPattern -> compile(flags)
operation_source -> graphql.check(schema) -> operation.bind(variables)
jobs -> workflow.check(interfaces) -> checked_plan -> runner.execute(grant)
```

None of these names is asserted to exist in the prototype. Each arrow needs
an error/result/source-map contract before becoming a target API.

## Candidate Laws

Use these as experiment oracles, with explicitly named supported domains:

1. **Preserve supplied data.** Encoding then decoding a supported value
   preserves its type and value. Literal text must not become a sibling field,
   expression operator, dependency or additional process argument.
2. **Separate program from parameters.** Changing a bound value leaves the
   parsed program structure unchanged except at designated value slots.
   Structural holes such as identifiers require their own checked operation.
3. **No implicit second evaluation.** Data is not interpreted again as source
   without an explicit domain operation and matching authority.
4. **Named checked guarantee.** Syntax acceptance, schema validation,
   reference resolution, policy checking and live admission are different facts.
5. **Explicit stage inputs.** An input cannot appear before its stage makes it
   available. A dependency's output is not a compile-time constant by default.
6. **Visible composition law.** Conflicts, order, list topology, priority,
   deletion, defaulting and unknown fields are not hidden by generic merge.
7. **Authority stays at the boundary.** Constructing an artifact does not
   authorize executing it; imports and host extensions are accounted for.
8. **Evidence survives reduction.** An error can identify the owning language,
   generated artifact and contributing source, with honest mapping precision.
9. **Sensitive evidence is controlled.** Explanation may show structure and
   safe placeholders without stringifying protected contributions.
10. **Portable means declared.** Edition, schema, dialect, flags, environment
    and dependency identity travel with a saved artifact or are explicitly
    rebound and checked when it is loaded.

These are desired candidate properties, not a proof of Nomi implementation.
The [host probes](experiments.md) demonstrate why some laws matter; they cannot
establish the laws over all domains or host implementations.

## Three Representative Programs

### Beginner: A Message In A Configuration File

Task: read a supplied service name, port and message; reject a non-integer port;
produce a configuration document and a human preview. Keep validation errors
at the input field, and preserve a literal multiline message.

Original input fixture:

```json
{
  "service": "welcome",
  "port": 8080,
  "message": "hello {guest}\nextra: true\n${LATER}"
}
```

Compare A: typed config plus whole-value encoder, B: parsed YAML plus checked
value substitution, C: proposed scoped construction. The oracle has exactly
three application fields; the message remains one Text value with unchanged
braces, dollar syntax and newlines. Changing port to `"8080"` must follow the
declared strict decode policy, not whichever host coercion is convenient.

Observe how a first-hour user distinguishes display interpolation from foreign
literal content. Format each candidate at 80 and 100 columns. Count places
where a reader must know an escape stage, not just total source characters.

### Ordinary Production: Build, Test And Deploy A Service

Task: construct a workflow graph and a versioned Kubernetes resource bundle.
Build and test produce separate outputs; deployment depends on both. One
step invokes a versioned reusable component with typed inputs. An application
config inside a ConfigMap remains a separately checked or explicitly opaque
language. Produce an explanation before any remote operation.

The research fixture's required graph is:

```text
build -> test
build + test -> deploy
deploy inputs: image digest, environment name, replica count
deployment output: observed resource status, not just encoded YAML
```

The exact GitHub dependency/output rules belong to its adapter. An independent
Nomi graph model need not inherit them. Compare direct typed handles, parsed
workflow references and scoped declarations on missing dependencies, duplicate
names, wrong input types, failed test, skipped build, cancellation and stale
schema identity.

Keep source-only validation separate from server admission and health
observation. A saved plan records component/schema identities and which facts
will be rebound at execution. Execution requires a driver and runtime authority;
the documentary experiment must not quietly run a deployment.

### Failure-Heavy: Generate Documents Containing Programs

Task: accept an untrusted title and generate a workflow/config/report bundle.
The title should travel as a value through YAML, process arguments, SQL and
HTML text; optional policy/pattern inputs should instead be explicitly parsed
as their named languages. Include missing inputs and malformed foreign source.

Corpus entries should include:

```text
plain\nextra: true
missing' OR 1=1 --
two words; $(do_not_execute) "quote"
${{ unresolved.name }}
{literal braces} and a closing-delimiter-like sequence
<img src=x onerror=example>
e + combining acute; an astral symbol; CRLF; NUL
undefined name; deep nesting; large expansion; missing dependency
```

These are data-only fixtures unless an explicit bounded parser is under test.
The shell-like entry must never be executed as a probe. HTML fixture output
must be inspected as data or by a controlled renderer, not pasted into an
unrestricted application. The oracle checks value preservation, rejection
stage, mapped diagnostics, limits, secret placeholders and absence of unintended
IO. Successful parsing alone is not the pass condition.

## Bounded Experiment Set

Each experiment must compare at least two candidates on the three programs
above, report formatted source/errors/explanation, and state its supported
domain. This is a research packet, not a second project-wide delivery queue.
Implementation work enters the [roadmap](../../orientation/project_roadmap.md)
and existing design passes after a discriminating result.

| ID / priority | Competing candidates | Cases and oracle | Reject / stop condition | Evidence now |
| --- | --- | --- | --- | --- |
| E1 / first | Existing raw/multiline forms versus a bounded delimiter refinement | Foreign quotes/braces/backslashes, tabs, CRLF, trailing breaks, terminator collisions; exact decoded Text | Need for repeated ad hoc escaping or unspecified formatter behavior; no new form without measured need | Target forms read; conformance experiment pending |
| E2 / first | Whole-value typed encoding versus text templates with explicit typed holes | Beginner fixture, newline/colon/list/Boolean values; decoded shape and type preserved | Any value can silently add structure; output only compared visually | YAML shape probe executed; target comparison pending |
| E3 / first | Separate parse/check/bind APIs versus one operation returning explicit evidence | Malformed source, unknown names, schema annotations, unavailable context | “Validated” hides which checks ran or triggers execution | Format-checker probe executed; Nomi API pending |
| E4 / next | Typed dependency handles versus named graph references | Direct/transitive outputs, cycles, duplicates, skipped/failed jobs, late inputs | Missing edges become empty strings; plan-time inputs silently rebound | Primary GitHub comparison only |
| E5 / next | Constraint combination versus ordered overlays/patches | Same scalar conflicts, keyed/atomic lists, deletion, defaults, unknown fields | One generic merge silently chooses a law; ownership disappears | Primary CUE/Nickel/Kubernetes comparison only |
| E6 / first | Segment provenance versus coarse outer span with explicit precision | Escapes, YAML folding, indentation removal, included files, repeated expansion | Invented exact columns or source secret exposure | Model proposed; mapping implementation pending |
| E7 / first | Bound arguments and domain literal constructors versus interpolated source | SQL values/identifiers, regex pattern/replacement, argv, URLs, GraphQL variables | Universal quoting or loss of parameter identity | SQLite, regex and POSIX lexical probes executed |
| E8 / next | Pure checked policy with supplied environment versus callback-only policy | Missing/undefined inputs, custom host function, denied file/network call | Restricted grammar presented as authority proof; undefined coerced silently | CEL/Rego/Starlark documentation only |
| E9 / first | Explicit Text/Bytes/index units versus inherited host semantics | Composed/decomposed text, emoji, invalid bytes, CRLF spans, case folding | Backend changes equality/indexing or replaces invalid bytes silently | Unicode unit probe executed; backend comparison pending |
| E10 / next | Input/output/fuel limits versus deadline-only evaluation | Deep nesting, aliases, huge pattern, expansion fanout, expensive total program | Unbounded memory or output despite timeout; undocumented truncation | No load/cost benchmark performed |
| E11 / later | Draft + recovered tree + last checked value versus validation on every edit | Half interpolation, unfinished quote, inner syntax error, rename and format | Editing discards source or executes stale checked meaning as fresh | Existing draft model reused; editor study pending |
| E12 / later | Domain-specific artifact contracts versus universal DSL AST | Regex/query/policy/workflow serialization across Python/JS/WASM | Universal representation obscures dialect/effects; cached environment mismatch | Architectural comparison only |

“First” means a small discriminating slice before syntax admission, not a
calendar promise. E1/E2/E3/E6/E7/E9 can initially be bounded source/value probes;
do not build a general engine to run them. E4/E5/E8 require a chosen adapter or
symbolic model with clearly limited claims. E10-E12 follow only if earlier
results leave a concrete problem.

## Evaluation Measures

Report all of the following; compactness alone is insufficient:

| Measure | Useful observation |
| --- | --- |
| Local reasoning | Can a reader identify the owning interpreter, stage and result type? |
| Beginner correctness | Can a reader preserve a literal message without learning several escaping rules? |
| Production scale | Dependency/interfaces/import changes remain reviewable across files |
| Failure location | Errors identify the actual field, inner source and contributing value |
| Explainability | Plan/parse/binding/effect evidence is inspectable before execution |
| Formatting/recovery | 80/100-column source and incomplete edits retain meaning |
| Isolation | Denied capabilities remain denied under host extension calls |
| Resource behavior | Defined limits, cancellation and cleanup; no silent output loss |
| Portability | Same declared semantics or explicit unsupported result on each backend |
| Reversibility | Library/artifact boundary survives changing parser or substrate |

Reader studies need recorded tasks and participants; none were performed here.
Benchmarks need input sizes, versions and distributions; no speed ranking is
inferred from documentation adjectives or a ten-case local probe.

## Route Results To Existing Owners

| Pressure | Existing authority / delivery owner | Promotion requirement |
| --- | --- | --- |
| Raw, multiline, display, Unicode and bytes | Syntax/scalar semantics; roadmap A03 | Close exact decoding/formatting rules and backend corpus |
| Templates/callbacks/typed holes | Function contracts; A08 and open questions 3/12 | Binder, function-value/effect contracts and whole-program evidence |
| Structural config and validation | Data/decoder semantics; A09/A12 | Strict decode, diagnostics and schema/version identity |
| Policy/import/execute authority | Industrial effects; A13/A30 | Static effect plus runtime host-grant contract |
| Workflow lifetime and late values | Completion/tasks/resources; A11/A14/A15 | State, cancellation, cleanup and output availability |
| Query/scoped row forms | Open question 8; DW1-DW3; A16 | Typed expression/row scope and inspectable plan |
| Syntax hygiene and foreign DSL admission | Open question 12; metaprogramming evidence | Library failure demonstrated; explicit grammar/format/recovery/phase owner |
| Generated source and projections | Open question 17; A19/A23 | Provenance/precision plus draft-versus-checked model |

Read [open questions](../open_questions.md),
[metaprogramming evidence](../features/metaprogramming.md) and
[DW1-DW8](../data_workflows/nomi_candidates.md) before promoting results.
The current research does not close those forks. Register a focused design
packet only when a coherent target contract and bridge are ready; do not create
a speculative packet for every surveyed product.

## Recommendation For The Next Implementation Slice

Choose E1/E2/E7/E9 as the first string-boundary packet: exact text forms,
whole-value encoding, explicit bound values and declared Unicode units. Add E6
source evidence at the same time, before generated artifacts become opaque.
E3 specifies what each checker guarantees. Together these reveal whether
ordinary libraries are sufficient and supply pressure for D1/D3 in the existing
design agenda.

The stop condition is a readable, correct ordinary-library solution on the
three programs. If that passes, no DSL syntax is needed for that domain.
If it fails, preserve the failure and compare B/C against the same oracles.
Do not accept a new string form, universal templating layer or grammar hook
simply because the survey found one elsewhere.
