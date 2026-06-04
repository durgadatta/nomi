# Orthogonal Language Feature Coverage

> Status: source research note.
>
> Scope: documentation-only. This note maps language features that cut across
> Nomi's normal forms rather than belonging to one syntax family. It is not a
> spec. Fold stable decisions into `../language/language_spec.md`,
> `../language/language_direction_and_gap_map.md`, focused feature docs, or
> tooling checks.

## Purpose

Most Nomi research asks how features reduce to normal forms such as binding,
function, pattern, flow, block, data boundary, absence/result, and explanation.
That is necessary but not sufficient. Real languages also live or die on
orthogonal surfaces:

```text
source text
formatting
diagnostics
tooling
packages
security
observability
interop
migration
governance
```

These do not usually deserve new core primitives. They constrain how every
normal form is exposed, taught, stabilized, and trusted.

The design test is:

```text
Does this dimension make existing normal forms clearer, safer, easier to
migrate, or easier to explain?
```

If yes, it belongs in Nomi's design pressure. If it only adds another surface
without improving the normal forms, keep it out of the first everyday layer.

## Orthogonal Coverage Matrix

| Dimension | Source traditions | User pressure | Nomi design consequence | Normal forms touched |
| --- | --- | --- | --- | --- |
| Source text and Unicode | Unicode UAX #31, Python, Swift, Rust, JavaScript | Names, strings, columns, diagnostics, non-English code, security review | Define UTF-8, identifier profile, normalization, confusable/bidi warnings, grapheme/display-width APIs. | binding, pattern, module, explanation |
| Formatting and style | gofmt, Black, Rustfmt, Prettier, elm-format, dart format | Code should look familiar after time away. | Ship one formatter style; syntax proposals must be format-stable before promotion. | all surface forms |
| Diagnostic/event schema | Rust, Elm, Gleam, TypeScript, LSP, notebooks | Users need actionable failures, not exception strings. | Use structured diagnostics with code, phase, span, rule, value summary, redaction, and next step. | explanation, binding, decode, pattern, block |
| Accessibility | W3C WAI, screen readers, keyboard-first tools | Explain output must work beyond color/hover/visual diagrams. | Every diagnostic, trace, playground control, and notebook cell needs plain-text and machine-readable rendering. | explanation, tooling |
| Localization | Unicode, message catalogs, compiler diagnostics | Helpful errors should not be hardwired to English prose. | Separate diagnostic code/data from rendered messages; keep examples translatable where possible. | explanation, docs |
| Examples as checks | Rustdoc, ExDoc, doctest, Julia docs, Racket Scribble | Docs should not drift from behavior. | Examples need capability metadata, fixture policy, and a path into tests. | example, explanation, package docs |
| Observability and tracing | Elm debugger, Darklang traces, OpenTelemetry, debuggers, query plans | Users need to understand behavior across stages and hosts. | Treat `trace`, `explain`, pipeline plans, decode paths, and block events as one event stream. | explanation, flow, block, data boundary |
| Profiling and performance feedback | Python profilers, Julia `@time`, browser devtools, database explain plans | Slow code should be inspectable without changing semantics. | Profiling should be a tooling/policy layer over events, not magic syntax in the first language. | explanation, flow, block |
| Package and module identity | Cargo, Go modules, npm, Mix, Python packaging, Maven | Code must scale beyond one file. | Module names, exports, package manifests, examples, versions, and capabilities should be explicit data. | module, binding, package docs |
| Dependency trust and supply chain | Cargo audit, npm, Nix, Sigstore, package signing | Packages are authority boundaries. | Package metadata should eventually declare permissions, provenance, lockfiles, checksums, and review status. | module, capability, explanation |
| Host capabilities | Object capabilities, WASI, browser permissions, OS handles, Pony, Nix | Files, network, time, randomness, and secrets need visible authority. | Start practical: capability values and block policies before effect-system notation. | block, data boundary, explanation |
| Secrets and redaction | Pydantic SecretStr, cloud secret managers, security logging | Diagnostics must help without leaking credentials or PII. | Redaction metadata belongs on data fields and event values; display and explain obey it by default. | data boundary, explanation |
| Serialization and wire formats | JSON Schema, serde, protobuf, OpenAPI, Elm decoders | Programs cross process/API/file boundaries. | Decode external shape into owned `data`; emit field-path diagnostics; keep wire compatibility separate from constructors. | data boundary, result, explanation |
| State and mutation | Python rebinding, Rust ownership, Clojure atoms, databases, transactions | Everyday programs mutate caches, files, rows, and objects. | Distinguish rebinding, mutable containers, external state, and transactional policies before adding clever update syntax. | binding, block, capability |
| Concurrency and cancellation | Go, BEAM, Kotlin structured concurrency, Swift tasks, Trio | Async work needs cancellation, cleanup, and failure grouping. | Keep first core synchronous; add structured concurrency through block policies and capability-aware tasks. | block, result, explanation |
| Interop and FFI | Python C API, JS/Wasm, Rust FFI, JVM/CLR interop | Nomi's first ecosystem advantage is calling existing libraries. | Foreign calls are boundaries with capability, type/shape, error, and diagnostic adapters. | call, data boundary, result, capability |
| Compatibility and editions | Python PEP 387, Rust editions, TC39 stages | Syntax and libraries need migration paths. | Define public compatibility surfaces, target-only separation, deprecations, editions, and automated fix expectations. | all surface forms |
| Governance and proposal flow | PEPs, Rust RFCs, TC39, Swift Evolution | Future ideas need a path that preserves coherence. | Proposals need owner, status, normal form, interaction map entry, target fixture, diagnostics, and rejected alternatives. | docs/process |
| Testing and conformance | Python test suite, Rust compiletest, Test262, language specs | Users need to know what counts as the language. | Feature packets need parse, lower, runtime, diagnostic, frontend, docs, and conformance checks. | explanation, spec, tooling |
| Error recovery and editor UX | Tree-sitter, LSP, IDE parsers, TypeScript server | Incomplete code must still be useful in tools. | Parser profiles should support partial syntax, structured recovery, semantic tokens, and expansion hints. | source, tooling, explanation |
| Incremental and reactive execution | Jupyter, Pluto, Observable, spreadsheets, build systems | Notebooks and playgrounds need stale/dependency awareness. | Cell execution is tooling; dependency/staleness events should be structured, not a second language. | explanation, module, flow |
| Build/deploy/runtime profile | Go, Docker, Nix, Wasm/WASI, serverless, Homebrew | Useful languages have a path from script to shipped artifact. | Runtime profiles and host capabilities should be visible before deployment syntax or package promises harden. | module, capability, package |

## Orthogonal Features Worth Naming Early

These are not first-layer syntax features, but they should influence feature
packets now.

### 1. Redaction As Data Metadata

Secrets, tokens, PII, and private fields are common in ordinary scripts and API
code. Redaction should not be an afterthought in logging or display.

Design note:

```nomi
data AppConfig:
    database_url:Secret[str]
```

The key decision is that `Secret[T]` or field metadata affects display,
diagnostics, traces, examples, and serialization. It should not change ordinary
binding or data construction semantics.

### 2. Examples With Capability Policy

Examples should become checks, but examples sometimes touch files, clocks,
network, randomness, packages, or secrets.

Design note:

```nomi
examples:
    using fixture("people.csv"):
        load_people("people.csv") => Ok([...])
```

The example system needs a policy model before it becomes normative. This is a
block/explanation issue, not a separate testing language.

### 3. Query Plans As Explainable Values

Data work often needs lazy plans and backend lowering. The danger is a second
SQL-like language inside Nomi.

Design note:

```nomi
plan =
    rows
    |> where(_.active)
    |> group(by=_.region)
    |> derive(count = count())

explain(plan)
```

Plans should be values with explainable stages. Syntax should wait until row
and group binding are explicit.

### 4. Capability Values Before Effect Syntax

Files, network, clocks, subprocesses, and randomness are ordinary needs. Nomi
should make authority visible without requiring effect-system theory in the
first hour.

Design note:

```nomi
using(world.files.open(path)) -> file:
    text = file.read()
```

The first layer can use ordinary values and block policies. Algebraic effects,
typed capabilities, or handlers remain future layers.

### 5. Migration Metadata Beside Features

Because Nomi is exploratory, feature status must not silently become permanent.
Each spec-ready feature should carry:

- current status;
- experiment or edition profile;
- replacement guidance if superseded;
- target fixtures;
- compatibility risk;
- formatter and diagnostic expectations.

This is not user syntax, but it is part of language design discipline.

## Orthogonal Admission Rules

Use these rules before adding or promoting an orthogonal feature:

1. Does it constrain an existing normal form rather than invent a new one?
2. Does it improve first-hour learning, trustworthy boundaries, explainable
   failures, package growth, or migration?
3. Can it be represented as metadata, a capability, a library value, a block
   policy, or a tooling view before syntax?
4. Does it have a plain-text and structured representation?
5. Does it preserve source spans, stable names, and redaction?
6. Does it have a versioning or compatibility story?
7. Does it avoid making one host, editor, package manager, or backend the
   hidden language definition?

If not, keep it research-only.

## Research Coverage Gaps To Fill Later

The current corpus is broad, but these areas still deserve deeper dives if
they become design blockers:

| Gap | Why it may matter | Trigger for deeper research |
| --- | --- | --- |
| Observability standards | `trace`/`explain` could benefit from established event models. | Before defining the explanation event schema. |
| Accessibility of coding tools | Nomi's web/notebook/diagnostic surfaces need concrete acceptance rules. | Before treating the playground or notebook as teaching defaults. |
| FFI and host interop | Python interop is a central adoption path. | Before promising stable foreign library calls. |
| Serialization compatibility | `data.decode` and API boundaries need wire-version rules. | Before writing a decode boundary feature spec. |
| Conformance and editions | Public syntax needs compatibility policy. | Before any non-experimental release profile. |
| Reactive/incremental notebooks | Cells, stale state, and dependency graphs shape user trust. | Before adding richer notebook semantics. |
| Supply-chain trust | Package use is an authority boundary. | Before a package manager or remote dependency story. |
| Build artifact profiles | Web, CLI, notebook, server, and Wasm hosts differ. | Before deployment docs become user-facing promises. |

## Nomi Synthesis

Orthogonal features should make Nomi more coherent, not larger. The desired
shape is:

```text
normal forms define meaning
orthogonal features preserve trust, accessibility, migration, and tooling
feature packets connect both
```

The next design packets should therefore include an "orthogonal impact" row:

```text
source text:
formatter:
diagnostics/events:
accessibility:
security/redaction:
compatibility/migration:
tooling/frontend:
package/docs:
```

Most rows can say "none" for small features. The point is to catch hidden
global costs before attractive local syntax hardens.
