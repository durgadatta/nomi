# Adversarial Exploratory Implementation Critique

> Status: active critique.
>
> Scope: how the implementation can accidentally stop serving language design.
> This critique assumes Nomi is early, exploratory, and intentionally flexible.

## Thesis

The most dangerous failure mode is not a slow parser or a missing backend. The
danger is that implementation convenience quietly decides the language before
the language design is ready.

The project should optimize for reversible semantics, inspectable reductions,
and metadata-driven extension. A feature that works by accident across five
hardcoded files is worse than a feature that is slower but clearly declared,
inspectable, and easy to remove.

## Hostile Reading

Nomi currently has several impressive but competing substrate paths:

- Lark grammar plus postlexer;
- Python AST lowering;
- desugar passes;
- Nomi/Python/reduced interpreters;
- Core IR;
- Python direct runtime;
- JavaScript Core Runtime;
- Rust/WASM parser plus JS lowering;
- legacy Pyodide bridge;
- web/notebook/CLI adapters.

Each path is locally reasonable. Together, they can turn exploratory language
work into a coordination maze.

If the project is not careful, the next six months could produce this shape:

```text
feature semantics live in:
  a grammar rule,
  a postlexer exception,
  a Rust payload string,
  a JS regex lowerer,
  a Python AST adapter,
  a desugar pass,
  an eval_* method,
  a doc paragraph,
  and a sample snapshot.
```

That would make Nomi less like a new language design and more like a pile of
prototype compatibility obligations.

## Highest-Risk Inversions

### 1. Code Becomes The Spec

If the real answer to "what does this feature mean?" is "read the lowering
code," Nomi has lost the thread.

Required response:

- features must have spec-shaped metadata;
- inspection must show reductions;
- tests must compare artifacts, not just successful stdout.

### 2. Fast Browser Path Becomes A Shadow Language

The Rust/WASM plus JS path is valuable because it removes Pyodide from the hot
path. It is also dangerous because it can parse/lower differently from the
Lark/Python path while producing plausible output.

Required response:

- create source-to-Core parity tests;
- version the Rust AST JSON schema;
- demote `Expr::Raw(String)` to an explicit unsupported/fallback mechanism;
- keep browser-default claims separate from language-default claims.

### 3. Python AST Remains The Semantic Center

Python AST is still useful as a bootstrap backend, but it is a poor long-term
semantic substrate for Nomi. It hides Nomi-specific surface concepts, source
spans, constraints, block policies, and diagnostic provenance.

Required response:

- migrate awkward syntax into Surface IR;
- lower Surface IR to Core IR before Python AST where possible;
- keep Python AST as one backend artifact.

### 4. Declarative Registries Become Decorative

Feature registries and backend specs are only useful if they drive behavior.
If agents still add manual imports, manual lists, separate docs, and separate
tests, the registry becomes theater.

Required response:

- require every new feature to declare its owner, layer, status, normal form,
  implementation modules, diagnostics, and test expectations;
- derive grammar/lowering/desugar/runtime inspection from the registry;
- fail tests when docs and registry capability claims diverge.

### 5. AI Agents Accelerate The Wrong Thing

AI tools are good at filling in repetitive implementation gaps. In an
exploratory language project, that is a double-edged gift: an agent can quickly
make a premature design look real.

Required response:

- agent skills must prefer critique, metadata, and reversible slices before
  implementation;
- broad changes should include an "optionality preserved/lost" note;
- hardcoded wiring should be called out explicitly in final summaries.

## Spec-Driven Architecture Pressure

Nomi should move toward a small set of authoritative declarations:

| Declaration | What it should drive |
| --- | --- |
| `SyntaxFeature` | grammar layers, lowering mixins, desugar passes, status, docs, tests |
| parser frontend spec | accepted source, payload schema, spans, host support, promotion gates |
| eval backend spec | Core IR support, host capability needs, diagnostics, promotion gates |
| host capability manifest | builtins, browser/server availability, side effects, errors |
| result/diagnostic schema | CLI/web/notebook display, tests, traces, agent inspection |
| generated artifact metadata | manifest freshness, WASM package freshness, deployment trust |

The goal is not a grand plugin framework. The goal is fewer hidden agreements.

## Design Review Questions

For any proposed implementation, ask adversarially:

1. If we reject this feature next week, what files must be unwound?
2. Is the feature declared in data, or only implied by code?
3. Can two parser frontends discover the same meaning without copying logic?
4. Can a backend reject unsupported behavior with a structured diagnostic?
5. Can docs, tests, and inspection derive status from one source?
6. Does this preserve the normal-form model or add a private mini-language?
7. Would an AI agent know where to add the next related feature?
8. Does this make the implementation easier or harder to change?

## Near-Term Groundwork

1. Extend `SyntaxFeature` until it can be the real declaration point for
   implemented syntax.
2. Define a versioned Rust AST JSON schema and a parity harness against the
   Python source-to-Core path.
3. Add a host capability manifest before adding more direct-runtime builtins.
4. Add a shared `ExecutionResult`/diagnostic JSON contract for browser and
   notebook adapters.
5. Add generated artifact freshness metadata for WASM outputs.
6. Add an agent review template based on the exploratory doctrine.
7. Make docs that describe implementation status cite registry/capability
   tables or tests rather than hand-maintained prose.

## Acceptance Standard

A feature is prototype-acceptable when:

- it is declared;
- it is inspectable;
- it has a parity oracle or a named divergence;
- it can be disabled or removed locally;
- it has focused tests;
- it does not make Python AST, JS regex lowering, or one backend's limitation
  the definition of Nomi.

