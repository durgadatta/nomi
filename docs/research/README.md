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
3. [Language-Feature Matrix](language_feature_matrix.md),
   [Language Reviews](languages/README.md), and [Feature Comparisons](features/README.md) -
   one feature-by-language synthesis table and its detailed reviews, with primary
   sources, bounded scope, Nomi costs, and concrete experiments.
4. [Open Questions](open_questions.md) - genuine forks that still require
   experiments rather than more broad surveys.
5. [Resource Experiment](resource_lifetime.md) - executed symbolic comparison
   of cleanup carriers and supplied-fact escape policies; not runtime conformance.
6. [Cognitive Foundations](cognition.md) and
   [Human-Computer Languages](interfaces/README.md) - the requested expansion
   beyond conventional languages, with 18 bounded interface threads.
7. [Redesign Frontiers](design_frontiers.md) - primary evidence for eight further
   design pressures, from typed incomplete programs to qualified guarantees.

The [language synthesis](../design/synthesis.md) links that evidence to category
targets, the revised overall program, and user-facing playground gates. The
44 language reviews and 13 feature pages are deliberately indexed evidence,
not independent specifications or 44 new implementation backlogs.

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

The interface expansion adds questions about representation, change, evidence,
and time; it does not turn every interface into a new syntax proposal. Further
research should begin with a failed target program or unresolved experiment,
using the [design-first agenda](../design/redesign_agenda.md) for coverage gaps.

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

The old source URLs and longer bibliographies remain available in repository
history. The September review adds freshly checked primary references under
the requested language/feature indexes; it does not restore old competing
atlases or syntheses. Extend these pages only for a concrete target deficiency.
