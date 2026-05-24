# Exploratory Implementation Doctrine

> Status: active agent and implementation doctrine.
>
> Purpose: keep Nomi easy to reshape while it is still an early language-design
> initiative, not a stabilized implementation project.

## Core Position

Nomi is not merely a codebase trying to accumulate working features. It is a
language-design laboratory. The implementation exists to make design pressure
concrete, inspectable, testable, and reversible.

That changes the engineering default:

```text
stable product implementation:
  choose a path -> harden it -> optimize it -> document it

Nomi exploratory implementation:
  declare intent -> encode metadata/spec -> generate or select paths ->
  inspect artifacts -> test behavior -> keep the choice reversible
```

The prototype may be fast and useful, but its architecture should not make
current mechanics feel inevitable. Python AST, Lark, Rust/WASM, JavaScript,
Core IR, and Pyodide are substrates. Nomi's normal forms, feature metadata,
diagnostics, examples, and reductions are the language design.

## Doctrine

### 1. Specifications Before Clever Code

Every nontrivial feature should have a spec-shaped declaration before or beside
implementation:

- feature owner;
- status and promotion gate;
- normal form;
- layer classification;
- grammar or syntax entry;
- surface node or payload contract;
- reduction/core target;
- runtime/backend capability;
- diagnostics and examples;
- tests and inspection stages.

If a change cannot say these things, keep it as a spike or local experiment.

### 2. Metadata Should Drive Pipelines

Prefer registries, manifests, capability tables, schemas, and profile specs
over hand-edited wiring.

Good default:

```text
feature metadata -> parser/lowering/desugar/runtime/test selection
```

Suspicious default:

```text
add import here, add class there, append to list there, remember a doc table
```

Manual wiring is acceptable for a spike only when the next extraction point is
named.

### 3. Experiments Need Fences

Fast paths and exploratory backends are welcome, but they must not silently
become the language definition.

Each experiment should declare:

- what it proves;
- what it does not prove;
- which oracle it compares against;
- which capability flags remain false;
- how users and agents can inspect the divergence.

### 4. Source-To-Meaning Must Stay Inspectable

Every user-facing syntax should eventually show this chain:

```text
source -> CST/tree -> Surface IR -> Core IR/reduction -> runtime events
```

For today's prototype, Python AST may sit in the chain, but it should not be
the only explanation of meaning.

### 5. Data Beats Control Flow For Language Definition

Use data/config/schema when the project is declaring what exists:

- syntax features;
- parser frontends;
- eval backends;
- host capabilities;
- desugar passes;
- runtime profiles;
- diagnostics;
- fixture coverage;
- generated artifacts.

Use imperative code for execution after the declarative shape is clear.

### 6. Reversibility Is A First-Class Quality

Because Nomi is early, a good implementation is one that can be changed without
archaeology. Favor:

- small registries over global side effects;
- adapters over direct cross-subsystem imports;
- versioned payloads over informal JSON;
- generated tables over duplicated docs;
- feature flags/profiles over hidden defaults;
- tests that compare artifacts, not only final stdout.

### 7. AI Tools Must Preserve Design Optionality

AI agents should not rush from "possible" to "implemented." Their job is to
make uncertainty explicit and shrink the next safe step.

Before changing parser/interpreter/runtime behavior, an agent should ask:

- What normal form owns this?
- What metadata or manifest should drive it?
- What artifact should be inspectable?
- What is the smallest reversible implementation?
- What tests prove parity or intentional divergence?
- What future design choice would this make harder?

## Declarative Groundwork Targets

Near-term work should prefer these foundations:

1. A feature manifest that can drive grammar, lowering, desugar, docs,
   inspection, capability tables, and tests.
2. A parser frontend contract with versioned payload/schema metadata.
3. A source-to-Core parity harness for Lark/Python and Rust/WASM/JS paths.
4. Host capability manifests shared across Python, Node, browser, and future
   Wasm/WASI hosts.
5. A browser/Python `ExecutionResult` JSON shape with structured diagnostics.
6. Generated artifact metadata for `web/manifest.json` and WASM parser output.
7. Agent-facing checklists that reject hardcoded feature wiring unless it is an
   explicitly fenced spike.

## Anti-Patterns

These are the habits most likely to trap Nomi in accidental complexity:

- adding syntax by patching parser, lowerer, runtime, docs, and tests
  independently with no feature-owned declaration;
- treating Python AST parity as language semantics;
- accepting a Rust/WASM or JS path because it is fast without source-to-Core
  parity;
- letting `Expr::Raw(String)` or regex lowering become the normal extension
  mechanism;
- documenting capabilities manually while code uses separate hidden flags;
- adding AI instructions that are longer than the invariant they protect;
- committing generated artifacts without a freshness check or explanation;
- letting examples migrate into runnable samples before status, tests, and
  snapshots agree.

## Agent Review Gate

For substantial changes, every AI tool should be able to report:

```text
Feature/status:
Normal form:
Declarative owner:
Generated/derived wiring:
Manual wiring still present:
Inspection artifact:
Parity oracle:
Tests/checks:
Reversibility risk:
```

If this report is mostly blank, the work is not ready to harden.

