# Strings, Embedded Languages And Boundary Preservation

> Status: string-focused DSL research and competing semantic contracts.
>
> External evidence checked 2026-10-01. Proposed type/API names below are
> explanatory notation, not implemented Nomi exports or admitted syntax.

## Why Strings Are Central

Text serves many different roles: prose, identifiers, paths, serialized values,
patterns, templates, queries, policies and executable source. The same runtime
representation does not give them the same contract. A string may be a final
value for one consumer and a program for the next.

An important inference is that Nomi needs to preserve **what is literal, what
is a supplied value, and which interpreter owns the next step**. Raw literals
solve host escape processing. Contextual construction solves a different
problem. A parsed or checked DSL object solves another. None automatically
implies permission to execute it.

## The Current Target And The Remaining String Questions

[Target syntax](../../design/syntax.md) already accepts ordinary double-quoted
brace interpolation, doubled literal braces, raw text that disables both
escaping and interpolation, bytes, and triple-quoted multiline text. The
[ledger](../../design/decisions.md) rejects a parallel ordinary/f-string split.
These are accepted target choices; a DSL survey cannot quietly reopen them.

The following contracts still need explicit closure or conformance evidence:

| Topic | Required decision / evidence |
| --- | --- |
| Raw delimiter collision | How to represent embedded closing quotes and terminators without a new unbounded family |
| Multiline indentation | Exact leading/trailing newline, indentation, tab and CRLF behavior |
| Interpolation grammar | Expression boundaries, nested strings/braces, evaluation order, recovery |
| Display conversion | Accepted types, user-defined display, locale, failure and effect behavior |
| Formatting | Numeric precision, dates, width and alignment without changing scalar meaning |
| Text indexing | Bytes, code units, scalar values and graphemes must be distinguished |
| Equality and normalization | Exact comparison versus explicit normalization/collation |
| Invalid encoding | Text decode failure versus a preserved Bytes value |
| Embedded diagnostics | Source identity and mapped ranges after transforms |
| Tool support | Partial literal completion, formatting, syntax highlighting and rename |
| Secret-bearing text | Whether interpolation, debug and diagnostic rendering can expose protected data |
| Backend parity | Python/JS/WASM cannot inherit contradictory host string behavior |

These are string-contract pressures for roadmap A03/A12/A19, not twelve new
syntax features. The default experiment should strengthen existing primitives.

## Literal Preservation Is A Distinct Capability

Several languages reduce escape burden in different ways:

| Mechanism | Preserves what? | What it does not establish |
| --- | --- | --- |
| Nomi raw text target | Host escapes and interpolation are disabled | Validity or safety of another language |
| YAML literal block | Most authored line structure after block decoding | Exact source bytes, final newline or inner grammar |
| Pkl custom delimiters | Ordinary quotes/backslashes with a chosen delimiter/escape prefix | A blanket ban on interpolation; it remains available with the matching prefix |
| Nix indented strings | Convenient multiline layout and a different escaping convention | Interpolation-free shell/configuration content |
| JS tagged templates | Literal segments, raw/cooked forms and substitution values | An automatically safe tag implementation |
| Racket syntax objects | Structure plus lexical/source information | A reason to treat unstructured text as hygienic syntax |

[Pkl literals](https://pkl-lang.org/main/latest/language-reference/index.html),
[Nix literals](https://nix.dev/manual/nix/2.34/language/string-literals.html),
[ECMAScript template semantics](https://tc39.es/ecma262/multipage/ecmascript-language-expressions.html#sec-template-literals),
[Racket syntax objects](https://docs.racket-lang.org/guide/stx-obj.html).
YAML's specific transformations are demonstrated in the
[executed probes](experiments.md).

The practical fixture is foreign source containing every Nomi metacharacter:
braces, quotes, backslashes, dollars, newlines, indentation and a delimiter-like
sequence. Test authored source -> decoded Text -> encoded foreign document ->
foreign decoder. A rendered screenshot or successful host parse is not enough.

## Interpolation Can Mean Three Different Operations

**Display interpolation:** stringify a value into prose. The output is Text.
This needs a display/formatting contract, including errors and redaction.

**Value substitution:** insert a typed value into a structured position. A
Boolean remains Boolean, a list remains a list, and a string remains one
string. GitLab inputs distinguish whole-value substitution from interpolation
inside a larger string.
[GitLab inputs](https://docs.gitlab.com/ci/inputs/).

**Syntax construction:** build a query, expression or document with separate
literal structure and typed holes. ECMAScript tagged-template evaluation passes
the literal array and expression values separately, which a library may use to
construct a non-string object.
[Tagged-template evaluation](https://tc39.es/ecma262/multipage/ecmascript-language-expressions.html#sec-template-literals).

Our inference is that combining these under a universal `interpolate` API
would make the result's meaning hard to inspect. Nomi can first test ordinary
functions receiving a structure and values; convenience notation must retain
the same inspectable semantic object.

### An Original Multi-Stage String

Imagine generating a GitHub workflow whose script writes a Kubernetes
ConfigMap containing an application template:

```text
Nomi source literal
-> Nomi Text / structured workflow
-> workflow YAML
-> GitHub expression evaluation
-> shell script
-> generated resource YAML
-> ConfigMap Text
-> application template evaluation
-> HTML rendering
```

The characters `${{...}}`, `$x`, `{visitor}`, quotes and newlines belong to
different interpreters. A backslash that escapes one parser may be preserved,
removed or given another meaning by the next. The experiment should remove
unnecessary text stages by using structured encoding and separate value
channels, then explicitly name the remaining source interpretation stages.

This is an original stress scenario. The products' documented stages are
covered in [layered configuration](layered_configuration.md); the combined
scenario was not deployed or executed.

## There Is No Context-Free Escape Function

The following table records domain obligations. Recommended Nomi types and
constructors remain hypotheses.

| Destination | Keep as a value when possible | If source must be generated | Critical distinction |
| --- | --- | --- | --- |
| JSON/YAML scalar | Encode the complete value | Use the format encoder | Value encoding versus handwritten quoting |
| SQL data value | Bound parameter | Driver-defined literal handling only where necessary | A data parameter cannot stand for SQL grammar |
| SQL identifier | Validated/structured identifier API | Dialect-specific identifier quoting | Identifier versus string literal |
| GraphQL argument | Variables object | Checked operation builder | Variable type and schema identity |
| Process argument | Argument vector | Platform/shell-specific construction | An argument versus a script or option |
| Shell script | Script source plus separate environment/arguments | Explicit shell dialect and quoting rules | Parser stage and expansion stage |
| HTML text/attribute | Renderer with a known context | Context-specific encoding | Text, attribute, URL, JS and CSS contexts differ |
| URL | Construct components | Percent-encode the specific component | Path segment, query value and whole URI differ |
| Regex | Literal-pattern constructor or compiled pattern | Dialect-specific pattern quoting | Pattern syntax versus replacement syntax |
| Glob/path selector | Structured segments where possible | Named dialect and platform | Wildcards versus literal filesystem names |
| JSONPath/XPath | Parsed selector plus context | Correctly quoted name selector | Property key versus query program |
| Template | Parsed template plus supplied bindings | Trusted template source with named rendering context | Value binding versus second-pass template evaluation |
| Policy expression | Parsed/checked expression plus bindings | Explicit source and environment contract | Decision value versus arbitrary executable source |
| Grammar/code | Syntax tree with source/binding information | Parser/formatter with ownership rules | Syntax node, identifier and literal splice differ |

PostgreSQL's parameter APIs separate values from command text and provide
different handling for identifiers. GraphQL likewise supplies variables
separately from an operation's source.
[PostgreSQL commands](https://www.postgresql.org/docs/17/libpq-exec.html),
[GraphQL variables](https://graphql.org/learn/queries/).

Dockerfile exec form parses a JSON argument array without automatically
invoking a shell; shell form invokes a shell. Explicitly choosing `sh -c`
crosses back into script interpretation even inside exec form.
[Dockerfile forms](https://docs.docker.com/reference/dockerfile/).
GNU Make recipe variables are expanded by Make, with `$$` used to pass a
dollar onward to the shell.
[Make recipe expansion](https://www.gnu.org/software/make/manual/html_node/Variables-in-Recipes.html).

HTML prevention guidance distinguishes text, attribute, URL, JavaScript and CSS
contexts; escaping an unsafe structural position is insufficient. URI reserved
characters have roles that depend on the component.
[OWASP output contexts](https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html),
[RFC 3986](https://www.rfc-editor.org/rfc/rfc3986.html).

Python's `re.escape` handles pattern metacharacters and is explicitly unsuitable
for replacement-string escaping. RE2 excludes constructs such as backreferences
and lookaround supported by some other engines.
[Python regex](https://docs.python.org/3.14/library/re.html),
[RE2 dialect](https://github.com/google/re2/blob/main/doc/syntax.txt).
**Inference:** a saved regex must carry its dialect and flags; a portable
pattern type cannot promise all host engines' syntax or complexity behavior.

The local probes demonstrate structured YAML encoding, bound SQL values,
literal regex construction and POSIX lexical argument round-tripping. They do
not prove Windows quoting, real shell execution or general injection immunity.

## Parse, Check, Render And Execute Are Different Promises

An explanatory state model:

```text
Draft source
  -> Parsed[D, Edition]
  -> Checked[D, Edition, Environment]
  -> Bound / planned artifact
  -> Authorized execution
  -> Result plus events
```

These labels need not become five public generic types. They describe
guarantees that must not collapse accidentally. A parser may recover an
incomplete tree, a checker may reject unknown names, and execution can still
fail because of IO or remote state.

CEL explicitly separates parse, check and evaluate and requires evaluation
bindings to match the compiled environment.
[CEL processing](https://cel.dev/overview/cel-overview).
JSON Schema 2020-12 distinguishes `format` annotation from assertion behavior;
a schema-looking field alone does not guarantee semantic validation.
[Validation vocabularies](https://json-schema.org/draft/2020-12/json-schema-validation).
This is demonstrated by the installed jsonschema library with and without its
format checker.

Nomi candidates should specify whether checked means syntax-only, schema-valid,
names-resolved, policy-typed, resource-budgeted or executable in a given host.
Do not use a universal `ValidatedText` label that invites callers to infer
guarantees no checker established.

## Unicode And Bytes Need Their Own Contract

Unicode normalization and text segmentation are different operations. Canonical
equivalence can relate different scalar sequences; extended grapheme clusters
describe user-perceived character boundaries and require defined segmentation
rules. Neither byte count nor UTF-16 code-unit count is interchangeable with
grapheme count.
[Normalization](https://unicode.org/reports/tr15/),
[Segmentation](https://www.unicode.org/reports/tr29/).

Our probe observes `é` as one scalar versus `e` plus combining acute as two;
the strings compare unequal before NFC. An emoji occupies one scalar, four
UTF-8 bytes and two UTF-16 code units in the tested host operations. It does
not test grapheme segmentation.

Nomi should test the following independently:

- Text validity and explicit Bytes decoding errors; no silent replacement in a
  supposedly exact artifact.
- Exact equality versus opt-in normalization, search and locale-aware collation.
- Scalar iteration versus grapheme UI movement versus byte IO offsets.
- Formatter/source-map offsets across astral symbols, combining marks and CRLF.
- Identifier policy, case folding and visually confusable names.
- Regex classes, character boundaries and dialect-specific Unicode versions.
- Hashing, canonical serialization and signatures: normalize only if the named
  contract requires it, and retain authored source separately.

Starlark deliberately leaves string element width implementation-dependent
(8 or 16 bits). That is evidence of a real portability fork, not a suitable
default for Nomi's multiple backends.
[Starlark strings](https://github.com/bazelbuild/starlark/blob/master/spec.md).

## Source Maps Must Survive Nontrivial Transformations

A generated artifact needs more than one starting line number. Consider
multiline indentation removal, YAML folding, escape decoding, inserted values,
included files and one source definition emitted into many resources.

An experimental source-map record should retain:

| Field | Purpose |
| --- | --- |
| Original source ID and revision | Do not blame an edited document using stale offsets |
| Stage and transform ID | Identify the decoder/expander that changed coordinates |
| Generated artifact range | Locate the failing consumer input |
| Original contributing ranges | Support many-to-one and one-to-many mapping |
| Contribution kind | Literal, substituted value, included source, generated delimiter |
| DSL/schema/environment identity | Explain which checker owns the error |
| Sensitive contribution marker | Render a safe placeholder rather than source secrets |
| Mapping precision | Exact range, enclosing span or unavailable mapping |

This is a proposed experiment record, not a repository-wide schema change.
If exact inversion is impossible after folding, diagnostics should say so and
show a trustworthy enclosing source span plus the generated context. A guessed
column is worse evidence than an explicitly coarse span.

At least three diagnostic locations may matter: the inner DSL error, the outer
field carrying it, and the input or definition that contributed the text.
Keep the error's semantic owner and all useful causes. An outer YAML syntax
error and a rejected CEL identifier should not have the same generic message.

Racket's syntax-object model supplies a concrete precedent for retaining
binding/location information alongside structure.
[Syntax metadata](https://docs.racket-lang.org/guide/stx-obj.html).
Nomi's existing structured-document research supplies the draft/committed-value
distinction; reuse it rather than inventing a separate editor model.
[Preserve the draft](../interfaces/structured_documents.md).

## Effects, Imports, Cost And Secrets

These are Nomi hypotheses to test, not proven properties of DSLs:

- Parsing a file already requires a file-read boundary; parsing supplied Text
  need not. Remote imports are separately authorized inputs.
- Pure construction must not implicitly deploy, query a database, spawn a
  process or access a secret through a host helper.
- Snapshot environment inputs used to build a reproducible plan. A later run
  should show which inputs are fresh rather than silently rebinding everything.
- Fuel, input size, nesting, expansion, output count and time limits are distinct.
  A terminating configuration can still be too expensive.
- Cache identity must include semantics/version/environment and relevant
  authority; text-only caching can reuse the wrong checked artifact.
- Keep secret provenance through encoding and interpolation. Prevent ordinary
  display/debug/source-map rendering from exposing sensitive contributions.
- Authorization should narrow runtime handles without pretending an effect
  name alone confines every host implementation.
- Cancellation and resource release belong to execution, including policy or
  query adapters that call external services.

Dhall's guarantees explicitly distinguish totality from practical evaluation
duration, and its import integrity checks refer to normalized meaning rather
than cosmetic source identity.
[Safety](https://docs.dhall-lang.org/discussions/Safety-guarantees.html),
[Integrity](https://docs.dhall-lang.org/tutorials/Language-Tour.html).
That motivates separate source, semantic and dependency identities, with no
claim that Nomi currently implements them.

## Strings Across Orthogonal Domains

The [expanded atlas](domain_atlas.md) keeps strings central while extending
beyond configuration. The same host Text type may carry these different roles;
the table names proposed boundary distinctions, not accepted Nomi types.

| Role | Example pressure | Evidence/operation to preserve |
| --- | --- | --- |
| Literal/display text | Diagram label, narration, user message | Exact text versus contextual rendering and escaping |
| Domain source | Policy, recurrence, pattern, query, music mini-notation | Dialect, original source, parse/check phase and mapped diagnostics |
| Foreign binder | Logic variable, proof binder, rewrite variable | Owning scope and capture/hygiene rules |
| Schema/field reference | Protocol field, query column, message argument | Schema/environment identity and rename correspondence |
| Entity/resource reference | User ID, workflow job, scene asset, robot joint | Nominal identity distinct from display spelling |
| Namespace/reference coordinate | IRI, genomic reference, spatial frame | Versioned context rather than a globally meaningful bare name |
| Pattern over bytes | Hex signature or binary layout condition | Bytes/bit offsets distinct from Unicode text indices |
| Molecular/shape description | Molecular graph versus substructure query | Parsed value and pattern are different domains |
| Unit expression | Quantity unit or special scale | Parse/normalize/convert under a named algebra; preserve display choice |
| Localized message | Plural/select branches with named arguments | Argument schema, locale and translated source as one artifact |
| Calendar/clock expression | Recurrence, event window, rhythm/cycle pattern | Time domain, endpoints, zone/version and conversion policy |
| Device command | Packet rule, shader entry, modal machine program | Target capability, retained state and explicit execution authority |
| Human evidence anchor | Legal provision, test scenario, model assumption | Source identity and relation to executable/formal interpretation |
| Opaque external payload | Unknown future vocabulary or stored source | Preserve without evaluation; expose unknown owner/version honestly |

**Inference:** validating one string role should not promote it to another.
A checked identifier is not checked program source. A parsed graph is not a
compiled pattern. Normalized units do not authorize motion. A translated label
does not rename a foreign binder. Distinct wrapper values and explicit adapters
are credible ordinary-library candidates before new source notation.

### Three Equalities And Several Normalizations

Compare separately:

1. Exact source equality: bytes/text and line-ending/encoding contract.
2. Parsed representation equality: the owner chooses whether spelling,
   comments, order and alternative forms matter.
3. Domain equivalence: a named theory/context establishes equivalent meaning.

Unicode normalization, whitespace formatting, query equivalence, unit
conversion, graph isomorphism and semantic hashing are different operations.
No generic `normalize(Text)` should claim all of them. Keep the original source
alongside any normalized semantic artifact and report the evidence/precision
of the correspondence.

### Construction Holes Need A Role Schema

For a bounded embedding candidate, name each hole as value, literal text,
identifier/reference, pattern, checked domain fragment or raw source. Define
its cardinality, phase, allowed type, scope and diagnostic origin. Raw source
insertion should be an explicit separately reviewed capability; it must not
be a fallback when a typed value fails to encode.

Message arguments and query parameters supply simple initial experiments.
Logic/proof binders, coordinate references and device targets require stronger
domain-specific checks. The library should report an unsupported hole role
instead of inventing universal quoting. This extends E2/E7 with E13/E22 and
the fourth [composition fixture](composition_boundaries.md#fixture-4--strings-across-several-languages).

## String APIs To Compare Before Adding Syntax

Compare ordinary functions and explicit value types for:

1. **Exact text:** known encoding/newline behavior and explicit display format.
2. **Structured encoding:** whole-value JSON/YAML serialization with limits.
3. **Domain literals:** literal regex, URL components, path segments and SQL
   identifiers, each with its own rejection policy.
4. **Parsed domain programs:** regex/query/policy/template source carrying
   dialect, spans and diagnostics.
5. **Bound construction:** structured SQL/GraphQL/workflow/config values with
   separate arguments, references and contexts.
6. **Explicit execution:** authority-bearing driver/runner calls returning
   typed results, cancellation and events.

Only then compare convenience notation that lowers to those same objects.
Reject a proposal if it merely saves punctuation while discarding values,
source maps, dialect identity or effect visibility. The bounded evaluation
plan is in [Nomi candidates](nomi_candidates.md).
