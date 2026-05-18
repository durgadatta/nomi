# Overlooked Language Design Dimensions

> Status: source research note.
>
> Scope: follow-up research on design dimensions that sit around syntax and
> semantics: text identity, accessibility, compatibility, migration, and
> governance. This is not an active spec. Fold stable decisions into
> `docs/language/`, `docs/features/`, or `docs/convenience/`.

## Purpose

Nomi's research corpus covers syntax families, data boundaries, diagnostics,
formatting, packaging, deployment, security, AI-readable semantics, and
interactive explanation. The remaining blind spots are not more expression
forms. They are the surfaces that determine whether a language can survive
real use:

```text
source text identity
accessible tools
compatibility policy
migration tooling
governance process
```

These concerns should influence Nomi before 1.0. They become much more
expensive after code, packages, docs, and community expectations exist.

## Source Scan

This pass used primary sources where possible:

- Unicode Standard Annex #31, Identifier and Pattern Syntax:
  <https://unicode.org/reports/tr31/>
- Python PEP 387, Backwards Compatibility Policy:
  <https://peps.python.org/pep-0387/>
- Python PEP 1, PEP Purpose and Guidelines:
  <https://peps.python.org/pep-0001/>
- Rust Edition Guide and Cargo `fix`:
  <https://doc.rust-lang.org/edition-guide/>
  and <https://doc.rust-lang.org/cargo/commands/cargo-fix.html>
- W3C WAI Accessibility Standards Overview:
  <https://www.w3.org/WAI/standards-guidelines/>
- TC39 Process:
  <https://tc39.es/process-document/>
- Swift Evolution:
  <https://www.swift.org/swift-evolution/>
- Rust Governance:
  <https://www.rust-lang.org/governance/>

## 1. Source Text, Unicode, And Identifier Policy

### External Lessons

Unicode UAX #31 exists because parsers and lexers need a stable way to define
identifier and pattern syntax across Unicode versions. It defines identifier
classes, pattern syntax/whitespace classes, normalization considerations, and
conformance expectations. It also notes that programming languages combine
Unicode properties with language-specific additions or restrictions.

The most important lesson is that source text is not merely "UTF-8 plus
strings." A language needs an explicit policy for:

- which identifier characters are accepted;
- whether identifiers are normalized;
- how confusable and bidirectional text risks are diagnosed;
- whether the Unicode version is part of conformance;
- how string length, slicing, display width, and grapheme clusters are taught.

### Nomi Risk

Nomi currently says source files are Unicode/UTF-8, but does not yet define an
identifier profile, normalization policy, confusable-character diagnostics, or
display-width rules for tooling.

This can break:

- parser stability across Unicode versions;
- syntax highlighting and LSP tokenization;
- diagnostics that point at columns;
- beginners working in non-English contexts;
- security review of visually confusing names.

### Nomi Direction

Use a conservative Unicode profile:

- source files are UTF-8;
- identifiers follow a declared UAX #31-derived profile;
- ASCII identifiers remain the teaching style;
- tooling warns on mixed scripts, confusables, invisible format controls, and
  suspicious bidirectional text;
- string APIs distinguish bytes, code points, grapheme clusters, and display
  width.

This belongs in a focused source-text/lexical policy section of
`language_spec.md`, plus implementation TODOs for tokenizer diagnostics.

## 2. Accessibility Of Language Tools

### External Lessons

W3C WAI frames accessibility as an ecosystem: content, authoring tools, user
agents, ARIA semantics, evaluation reports, personalization, pronunciation, and
translation all matter. The relevant lesson for a programming language is not
"make the docs website accessible" only. It is that the whole authoring and
feedback loop needs accessibility semantics.

### Nomi Risk

Nomi emphasizes diagnostics, notebooks, web playgrounds, examples, and
explainable traces. Those surfaces can become inaccessible if they rely on:

- color-only distinctions;
- hover-only explanations;
- visual tree diagrams without text alternatives;
- non-linear notebook state that screen readers cannot summarize;
- diagnostics that are not machine-readable;
- examples that require mouse-oriented web UI.

### Nomi Direction

Treat accessibility as part of the explanation normal form:

- diagnostics and `explain` output must have structured text forms;
- web playground interactions need keyboard navigation and screen-reader
  labels;
- semantic event streams should be renderable as plain text, JSON, and UI;
- examples and traces should not depend on color alone;
- docs should preserve stable anchors and readable headings;
- pronunciation and localization should be considered for generated docs and
  teaching material.

This belongs partly in the explanation-event spec and partly in web/tooling
acceptance checks.

## 3. Compatibility, Editions, And Migration

### External Lessons

Python PEP 387 treats public syntax, behavior, APIs, argument/return shapes,
side effects, and raised exceptions as compatibility surfaces. Rust editions
show another pattern: keep old code compiling while allowing new source-level
rules, and use automated migration tooling such as `cargo fix --edition`.
Rust's own docs also warn that migration tools must be run across feature and
platform configurations to catch conditional code.

### Nomi Risk

Nomi currently has status labels and target fixtures, but not an explicit
compatibility contract. Without one, every syntax convenience risks becoming
permanent by accident.

Breaking surfaces include:

- grammar and parse trees;
- runtime behavior and exceptions;
- diagnostic/event schemas;
- sample outputs and regression snapshots;
- package/module paths;
- generated docs and examples;
- web/notebook behavior.

### Nomi Direction

Define a compatibility policy before public adoption:

- pre-1.0 syntax can change, but target-only syntax must never be presented as
  runnable stable behavior;
- after 1.0, public syntax, standard library APIs, diagnostic schemas, and
  package metadata need deprecation windows;
- editions should be considered before incompatible syntax changes;
- automated migration should be planned alongside any accepted syntax that may
  replace older spelling;
- feature profiles and capability matrices should record edition exposure.

This belongs in a compatibility/edition section of `language_spec.md` or a
focused language-process doc.

## 4. Governance And Proposal Process

### External Lessons

Python's PEP process distinguishes standards, informational, and process
documents, requires motivation, discussion links, ownership, and metadata.
TC39 uses staged proposals with progressively stronger requirements: problem
space, cross-cutting concerns, high-level API/syntax, spec text, tests, and
multiple implementations. Swift Evolution uses public discussion and tracks
accepted proposals as release goals. Rust's governance page highlights RFCs
and separate language/library/compiler/tools teams.

The pattern is consistent:

```text
language change -> owner -> motivation -> public discussion -> maturity stage
-> spec text -> implementation evidence -> release target
```

### Nomi Risk

Nomi is currently mostly solo/AI-assisted design. That is productive now, but
without a proposal process, future ideas can bypass the convergence loop and
reopen settled choices.

### Nomi Direction

Nomi should keep the current design proposal template but make it more
operational:

- every proposal has an owner, status, normal form, motivation, interaction
  map entry, target fixture, feature packet, and implementation gate;
- target-only examples are allowed but must be labeled;
- rejected alternatives are preserved;
- accepted proposals identify the release or experiment profile they target;
- later community review should happen in one canonical thread per proposal,
  not scattered across chats and docs.

This belongs in `design_proposal_template.md`, `spec_readiness_map.md`, and
the agent skills.

## 5. Localization And Internationalization

### External Lessons

Accessibility and Unicode sources both point at a wider issue: language tools
are read by humans in different scripts, locales, and assistive contexts.
Programming languages often postpone this until documentation and diagnostics
are already English-only and string APIs are already byte/code-unit biased.

### Nomi Risk

Nomi's diagnostics and examples aim to be unusually helpful. If they are
designed as English strings rather than structured messages with stable codes,
later localization will be difficult.

### Nomi Direction

Treat diagnostics as structured data:

- stable diagnostic code;
- message template;
- source spans;
- related spans;
- machine-readable values with redaction;
- remediation hint;
- optional localized rendering.

This aligns with the explanation-event model and should be included there from
the start, even if only English messages ship initially.

## 6. Documentation Versioning And Deprecation

The package-docs research already covers versioned documentation, but it should
be promoted more forcefully into the spec process. If Nomi uses examples,
feature packets, and target demos as design tools, users must be able to tell
which version of Nomi a page describes.

Nomi should require:

- every public docs page has a version/status marker;
- generated package docs are versioned;
- deprecated syntax includes replacement guidance and removal target;
- target-only docs are visibly separate from runnable samples;
- examples in docs carry capability metadata once the matrix exists.

## Consolidated Recommendations

| Overlooked dimension | Nomi action | Best home |
| --- | --- | --- |
| Unicode identifier policy | Define UAX #31-derived identifier profile, normalization, confusable/bidi warnings, and string-indexing model. | `language_spec.md` lexical section + tokenizer TODOs |
| Accessibility | Make diagnostics, explain views, playground, docs, and traces keyboard/screen-reader/plain-text friendly. | explanation-event feature + web checks |
| Compatibility and editions | Define public compatibility surfaces, deprecation windows, edition/migration policy, and automated fix expectations. | `language_spec.md` or process doc |
| Governance | Mature design proposal flow with owner, status, discussion, normal form, interaction map, spec text, and implementation gate. | `design_proposal_template.md`, `spec_readiness_map.md` |
| Localization | Use structured diagnostic/event records with stable codes and renderable messages. | explanation-event feature |
| Docs versioning | Version public docs and mark target-only examples visibly. | package docs plan + docs tooling |

## Nomi Normal-Form Mapping

These topics do not introduce new language primitives. They constrain existing
normal forms:

- source text and Unicode constrain **binding**, **pattern**, and **module**
  names;
- accessibility constrains **explanation** presentation;
- compatibility constrains all surface forms and migration;
- governance constrains proposal admission;
- localization constrains **diagnostic** and **trace** records;
- docs versioning constrains examples and package metadata.

## Next Exact Moves

1. Add a lexical/source-text policy section to `language_spec.md`.
2. Add compatibility/edition policy to `spec_readiness_map.md` or a focused
   process doc.
3. Add accessibility requirements to the explanation-event feature packet when
   it is created.
4. Update `design_proposal_template.md` with owner, status, discussion, target
   fixture, and migration fields.
5. Add tokenizer/source-span TODOs for Unicode identifier diagnostics once the
   parser profile work begins.
