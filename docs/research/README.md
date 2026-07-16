# Nomi Research

> Status: consolidated design evidence.
>
> This directory replaces the previous collection of overlapping surveys,
> deep dives, feature atlases, syntheses, and research plans. The source corpus
> remains recoverable in Git history at commit `08f2aad`; these documents retain
> the conclusions needed for current design work without preserving parallel
> authorities.

## Reading Order

1. [Language Families](families.md) - what major traditions contribute and
   what Nomi should not inherit.
2. [Design Convergences](convergences.md) - findings that recur across
   language, tooling, data, security, and pedagogy research.
3. [Open Questions](open_questions.md) - genuine forks that still require
   experiments rather than more broad surveys.

The decisions drawn from this evidence live in
[Target Design](../design/README.md), [Syntax](../design/syntax.md), and the
[Decision Ledger](../design/decisions.md). Research proposes; target design
decides.

## Corpus Covered

The consolidated corpus compared:

- Python, Ruby, JavaScript/TypeScript, Tcl, Bash, PowerShell, and other
  everyday interface languages;
- ALGOL, Lisp/Scheme/Racket, ML/OCaml/F#, Haskell, Elm, Roc, and Gleam;
- Rust, Go, Zig, Swift, Kotlin, Scala, C#, Java, Dart, C, and C++;
- Erlang, Elixir, actor systems, structured concurrency, and async runtimes;
- SQL, LINQ, dataframe systems, array languages, R, MATLAB, Julia, and
  Mathematica;
- Pydantic, serde, Elm decoders, zod, CUE, Nickel, Dhall, Pkl, Terraform/HCL,
  JSON Schema, and OpenAPI;
- package managers, standard libraries, formatters, language servers,
  notebooks, browser playgrounds, build systems, deployment systems, and Wasm;
- diagnostics, explanation, first-hour pedagogy, accessibility, AI-readable
  semantics, capabilities, secrets, supply-chain integrity, and governance.

This breadth is enough for the present design stage. New research should begin
with a failed target program or unresolved experiment, not another general
language tour.

## Method

The useful unit of comparison is not copied syntax. It is:

```text
user pressure
-> semantic mechanism
-> tradeoff
-> interaction with the whole language
-> Nomi decision or experiment
```

Each finding is classified as one of:

- **convergence** - many successful systems independently need the same
  semantic capability;
- **fork** - credible systems choose incompatible tradeoffs;
- **surface variation** - several spellings encode substantially the same
  mechanism;
- **anti-pattern** - a repeated failure mode with little compensating value;
- **Nomi hypothesis** - a choice that still needs direct evidence.

Research is strongest when it narrows the language. A list of attractive
features is not synthesis.

Registered focused passes may add one topic document when a cross-cutting
contract needs more evidence than the consolidated files can hold cleanly.
[Pattern Matching Research](pattern_matching.md) is the first such packet; it
links directly to canonical design, focused target source, and an implementation
bridge through the [design-pass workflow](../orientation/design_pass_workflow.md).

## Evidence Policy

The earlier corpus mixed primary documentation, comparative notes, design
essays, internal proposals, and implementation observations. These consolidated
documents preserve the level of confidence:

- Language behavior claims should ultimately be checked against official
  specifications or documentation.
- Ecosystem and pedagogy claims are tendencies, not natural laws.
- Nomi decisions are design judgments made from evidence, not facts proved by
  language popularity.
- Current implementation behavior never settles a language-design fork.

Representative primary references include the Python, Rust, Swift, Kotlin,
TypeScript, Go, Zig, Gleam, Elixir, OCaml, Racket, Julia, WebAssembly, and WIT
documentation; Pydantic, serde, zod, Elm JSON Decode, CUE, Dhall, Pkl, JSON
Schema, Terraform, Cargo, Go Modules, Nix, Deno, and Sigstore documentation;
and foundational work by Landin, Strachey, Hoare, Milner, Wadler, and related
language-design traditions.

The source URLs and longer bibliographies remain available in repository
history. Restore a deep dive only when a concrete open question needs its
detail; do not restore the old documentation topology.
