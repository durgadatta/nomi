# Nomi Industrial Model

> Status: canonical target for language-scale engineering.
>
> Industrial scale here means that programs can be understood, built, tested,
> secured, deployed, observed, and evolved predictably. It does not mean that
> every domain belongs in the core language.

## The Industrial Bar

Nomi is not industrial because it can parse ambitious syntax. It becomes
industrial when these are contracts:

```text
source identity
typed interfaces
failure and effect boundaries
deterministic builds
package integrity
runtime isolation
concurrency lifetime
tooling protocol
backend conformance
release and migration policy
```

Each contract should be testable without trusting one implementation.

## Language Artifacts

The toolchain should expose stable, versioned artifacts:

| Artifact | Purpose |
| --- | --- |
| Tokens and lossless CST | formatting, refactoring, comments, syntax recovery |
| Surface AST | source constructs with spans and names |
| Typed surface | resolved bindings, types, constraints, effects, exhaustiveness |
| Core IR | small backend-independent executable semantics |
| Module interface | public types, functions, effects, docs, protocol conformance |
| Diagnostic/event records | frontend-independent explanation |
| Package/build graph | reproducible dependency and target resolution |

No parser frontend, host AST, bytecode, VM object, or JavaScript payload is the
language definition. Frontends conform by producing valid Surface artifacts;
backends conform by executing Core semantics.

Every artifact has a schema version and an upgrade policy. Tools reject unknown
major versions rather than guessing.

## Compiler And Runtime Profiles

One language may support several profiles without changing source meaning:

- interpreter/REPL for immediate feedback;
- browser/Wasm for playgrounds and embedded clients;
- portable bytecode for fast startup and managed deployment;
- native ahead-of-time builds for services and CLIs;
- restricted deterministic evaluator for package metadata and tooling.

Profiles publish capability tables. Unsupported features fail before execution
with a precise explanation; they do not degrade silently.

Memory is garbage-collected in the general profile. Specialized runtimes may
use regions, reference counting, escape analysis, or compact tracing collectors
behind the same semantics. Manual lifetime syntax is not imposed on ordinary
programs.

## Projects And Packages

`nomi.toml` declares:

- package identity and version;
- language edition and minimum toolchain;
- source roots and exported modules;
- direct dependencies;
- build targets and entry points;
- requested runtime capabilities;
- test, benchmark, and example targets;
- foreign interfaces and generated artifact policies.

`nomi.lock` pins the exact content hash of every transitive dependency and the
resolver version. Dependency fetch is pure: it downloads, verifies, and caches
content without executing package code.

Package names are domain- or organization-scoped rather than a single global
bare-name namespace. Publication is immutable. Registries use signatures and
an append-only transparency log. Version selection never upgrades a locked
dependency implicitly.

Builds are sandboxed and deterministic by default. Source, manifest, lockfile,
toolchain, target, and declared build inputs determine the artifact. Network,
environment, clock, and undeclared filesystem reads are unavailable during a
normal build.

## Modules And API Evolution

Modules are private by default. Public APIs require explicit types, expected
failure, effects, documentation, and stability metadata in their checked
interface artifact. These contracts may be inferred locally or declared in
source; written annotations are a selectable policy, not the only way to
produce a checked interface. Dynamic exploratory modules retain unknowns and
need supported adapters or stronger evidence to cross a checked boundary.
Interface artifacts allow incremental builds and downstream analysis without
running module code. Their identity includes the resolved public contract;
inference changes that contract visibly in API diffs.

Before a stable release, Nomi may break source freely. After a stable release:

- semantic compatibility is promised within an edition;
- new editions may change grammar or defaults with automated migration;
- packages declare their edition independently;
- old and new editions may coexist in one dependency graph through normalized
  Core contracts;
- deprecation diagnostics include a machine-applicable rewrite when possible;
- wire and stored-data compatibility remain application contracts, not an
  accidental consequence of source compatibility.

No compatibility policy should freeze a bad design before the first complete
language is proven. The current repository has no backward-compatibility
obligation.

## Standard Library

The prelude is intentionally small:

- scalar and collection types;
- `Option`, `Result`, and core protocols;
- basic comparison, iteration, formatting, and diagnostics;
- `print`, `check`, and a few universally understood operations.

Prelude membership does not hide authority: `print` still contributes the
`ConsoleWrite` effect, inferred or declared and exposed in checked public APIs.

Everything else is explicitly imported. The standard library is organized by
domain, not implementation history:

```text
text, bytes, collections, math, time, console
path, files, process, environment
json, csv, url, http
task, sync, testing, logging, trace
crypto, secret, encoding, ffi
```

Strict and lazy APIs have visibly different types. Partial operations return
`Option` or `Result`; no ubiquitous `head()`-style panic traps. Extension
methods and protocol implementations are visible only when their module is in
scope.

Experimental APIs mature in versioned packages before standard-library
promotion. Inclusion means accepting a long compatibility obligation, so the
stdlib is an exemplar rather than an encyclopedia.

## Effects, Authority, And Sandboxing

Effect declarations aid review and static checking. Runtime capabilities grant
authority. Both layers matter:

- command-line and deployment policy grants human-readable permissions;
- the runtime turns grants into unforgeable handles;
- modules and tasks receive only the capabilities they need;
- child processes start with a reduced, explicit set;
- browsers and embedded hosts can virtualize or deny unsupported effects;
- test runners replace clock, random, network, filesystem, and process
  capabilities without monkey-patching globals.

Authority is monotonic inside a sandbox: code may delegate or drop a capability
but cannot recreate one from a path or string.

## Security And Trust

Security defaults are language and ecosystem design:

- remote artifacts are content-addressed and signed;
- package fetch runs no scripts;
- builds use no ambient network or secrets;
- `Secret[T]` and sensitive-field metadata redact display, diagnostics, logs,
  traces, examples, and crash reports by default;
- revealing a secret is explicit, auditable, and capability-checked;
- cryptography APIs expose safe constructions rather than algorithm/mode
  combinations;
- decoded external values are strict and closed by default;
- unsafe foreign objects remain inside `UnsafeHost` boundaries;
- dependency, capability, and artifact graphs are inspectable.

Full information-flow types are deferred. Practical redaction, provenance,
least authority, and explicit boundaries deliver more benefit with less
annotation burden.

## Concurrency And Operations

The runtime provides structured tasks, cancellation, deadlines, task-local
capabilities, bounded channels, synchronization primitives, and error groups.
Libraries may build actors, supervisors, event loops, and data-parallel
executors without changing ordinary function semantics.

Operational hooks are structured and bounded:

- logs and traces use typed fields, source context, and redaction;
- metrics have declared names, units, and cardinality policy;
- task and resource events share trace identifiers;
- panic reports preserve causes and async ancestry;
- replayable capabilities support deterministic incident reproduction;
- runtime inspection cannot expose secrets merely because debug mode is on.

Backpressure and cancellation are part of stream/network contracts, not hidden
framework behavior.

## Data And Service Boundaries

The same `data` declarations drive constructors, decoders, encoders, schema
export, API documentation, and pattern exhaustiveness. There is still one
source of truth; generated JSON Schema, OpenAPI, database mappings, or host
types are projections.

Boundary contracts include:

- strict/explicit coercion policy;
- field and cross-field constraints;
- accumulated path-addressed errors;
- defaults with provenance;
- unknown-field policy;
- version and migration hooks;
- sensitive-field handling;
- resource and size limits to resist malicious inputs.

Schema generation never implies that all Nomi constraints are portable.
Tooling reports which rules were represented, approximated, or omitted.

## Foreign Interfaces

The portable ABI is based on an interface-description layer compatible with
Wasm components and native bindings. FFI generation is typed and reviewable;
it does not infer semantics from arbitrary host reflection.

Foreign calls declare ownership, allocation, thread affinity, blocking,
effects, errors, and panic behavior. Adapters copy or borrow only according to
the interface contract. Host exceptions and sentinel values do not leak into
ordinary Nomi code.

Python, JavaScript, Rust, C, JVM, and database interop are important adoption
paths, but none defines Nomi's object, exception, iteration, numeric, or async
semantics.

## Tooling As Product

The minimum supported toolchain is one coherent command:

```text
nomi run
nomi repl
nomi check
nomi fmt
nomi test
nomi doc
nomi explain
nomi build
nomi add/update/audit
nomi migrate
```

The formatter is canonical and edition-aware. The language server uses the
same typed surface and diagnostic engine as the compiler. REPL, notebook,
browser, CLI, and editor render the same result records.

Documentation examples are executable. Search links types, functions,
protocols, effects, examples, and source. Error codes resolve to short,
versioned explanations rather than unstable prose searches.

## Testing And Conformance

Language conformance is a data-driven suite containing:

- accepted and rejected source fixtures;
- typed Surface and Core snapshots;
- result, output, diagnostic, effect, and event expectations;
- resource/cancellation/multi-error scenarios;
- package resolution and reproducible-build fixtures;
- cross-backend differential tests;
- formatter idempotence and parser round trips;
- fuzzing for parsers, decoders, and FFI boundaries.

Each backend publishes the profile and conformance version it passes. Frontend
features do not claim support merely because they parse; parse, type, lower,
run, diagnose, format, and tool support are separate evidence axes.

Web playground samples are conformance programs, not hand-maintained copies.
Generated manifests and Wasm artifacts have freshness checks.

## Performance Model

Performance should be predictable before it is maximal. Nomi specifies:

- complexity expectations for core collections;
- integer overflow and floating-point modes;
- allocation and copy visibility in profiling tools;
- streaming versus materialization boundaries;
- blocking versus async operations;
- task and resource limits;
- deterministic benchmark harnesses.

Optimization uses typed Core IR, specialization, escape analysis, inlining,
vectorization, and backend-specific lowering. Dense scientific or array syntax
is not a prerequisite for fast array kernels; libraries and compiler protocols
can carry shape/rank information explicitly first.

## Deployment

Build outputs are immutable, content-addressed artifacts. Supported targets
should include native CLIs/services and Wasm components. Cross-compilation,
debug symbol separation, SBOM generation, signatures, provenance attestations,
and minimal runtime packaging are normal build outputs.

Production never resolves dependencies or compiles source. CI builds once,
tests the exact artifact, and promotes that artifact by digest. Runtime startup,
memory, and cold-start goals are profile-specific and continuously measured.

## Governance

Language changes use concise decision records containing:

- user pressure and representative programs;
- syntax and semantic alternatives;
- interaction with every nearby construct;
- diagnostics, formatting, tooling, and migration;
- implementation-independent conformance cases;
- explicit rejection and rollback criteria.

Research proposes; target design decides; implementations experiment;
conformance validates. A polished prototype does not bypass that order.
