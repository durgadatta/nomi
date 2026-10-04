# Text As A Computational Interface

> Status: comparative research, candidate vocabulary and bounded implementation
> handoff; no Nomi API, syntax, codec, template engine or shell integration is
> accepted by this chapter.
>
> Primary specifications and maintainer documentation checked 2026-10-03;
> representation/encoding references rechecked 2026-10-04.
> Local observations are limited to the explicitly named
> [probe capture](probe_results.json).

## Thesis And Boundary

Programming languages are usually authored as text, but their useful interface
is not "strings everywhere." Text scales because it is inspectable, copyable,
searchable, streamable, diffable, versionable, scriptable and recoverable with
minimal tooling. Structure and meaning scale because parsers, types, schemas,
names, source maps and execution boundaries prevent every piece of text from
being interpreted in every possible way.

The central design pressure is therefore:

```text
easy text at the human boundary
-> explicit representation and interpretation stages
-> owned values and checked structure
-> explicit authority before effects
-> text again only through a named display or encoding contract
```

This chapter deepens [strings and embedding](strings_and_embedding.md). That
chapter owns literal forms, contextual construction and embedded languages.
This chapter owns operation vocabulary, text-producing and text-consuming API
names, human/tool interfaces, and the contracts hidden by apparently simple
string transformations. The canonical target remains
[syntax](../../design/syntax.md), [semantics](../../design/semantics.md) and
[industrial contracts](../../design/industrial.md).

## One Representation, Many Roles

The same sequence of Unicode scalar values can be all of the following:

| Role | Consumer | Relevant identity | Dangerous collapse |
| --- | --- | --- | --- |
| Human prose | Person, screen reader, translator | Message, locale and presentation context | Treating prose as a stable machine protocol |
| Source code | Lexer/parser/editor/compiler | Edition, exact source and source spans | Treating displayed order as lexical order |
| Display form | UI, log or diagnostic renderer | Audience, locale, redaction and width | Treating a lossy display as a codec |
| Serialized value | Decoder for a named format | Media type, format edition and schema | Treating valid syntax as owned application data |
| Template source | Template engine | Trusted source, environment and output context | Re-evaluating supplied values as templates |
| Foreign program | Shell, query, regex, policy or build engine | Dialect, phase, bindings and authority | Calling a quoted fragment safe for every position |
| Protocol field | HTTP, line protocol or environment file parser | Framing, encoding and size limits | Losing record boundaries or delimiter collisions |
| Identifier/reference | Resolver and symbol table | Normalization policy, scope and nominal owner | Comparing only rendered glyphs |
| Opaque payload | Future or unavailable consumer | Exact preservation and declared owner | Normalizing or interpreting without permission |

`Text` can represent each role in memory. It does not establish any of their
contracts. A Nomi API should preserve role in the operation name, nominal type,
module, result, or attached evidence rather than require readers to infer it
from a bare `Text -> Text` signature.

## Text Is A Stack, Not A Scalar Detail

At least these layers can matter independently:

```text
bytes
-> character encoding
-> Unicode scalar sequence
-> normalization policy
-> grapheme/word/line segmentation
-> lexical tokens and trivia
-> recovered or complete syntax
-> resolved/checked meaning
-> formatted or rendered artifact
-> transport framing
-> destination interpretation
```

Unicode normalization gives named equivalence transformations; text
segmentation defines default grapheme, word and sentence boundaries. Neither
turns byte offsets, scalar offsets, UTF-16 code units and user-perceived
characters into the same unit.
[Unicode normalization](https://www.unicode.org/reports/tr15/) and
[text segmentation](https://www.unicode.org/reports/tr29/).

HTTP makes the outer contract equally visible: `Content-Type` describes the
media type and intended processing, while `Content-Encoding` is another ordered
layer. Identical bytes under different media metadata need not have identical
meaning. Content sniffing can reach the wrong processing model.
[HTTP representation metadata](https://www.rfc-editor.org/rfc/rfc9110.html#section-8.1).

**Inference:** Nomi's core `Text` value can stay small, but boundaries need
separate encoding, format, dialect, schema, locale, framing and provenance
arguments where those facts affect meaning. A universal rich string object
would make ordinary text expensive and still fail to own domain semantics.

## Producer And Consumer Names Are Semantic Promises

Names are not merely style. They tell a caller whether the result is for a
person or a machine, whether information can be lost, whether failure is
expected, whether IO occurs, and which consumer may interpret the result.

### Candidate Operation Vocabulary

These are proposed meanings to test, not accepted Nomi exports.

| Name | Direction | Promise | Must not imply |
| --- | --- | --- | --- |
| `display` | Value -> Text | Human-facing representation under an audience/locale/redaction policy | Stable syntax, losslessness or parseability |
| `inspect` | Value/evidence -> inspectable document | Developer-facing structure with depth/size/redaction limits | Stable wire format or complete secret-bearing state |
| `format` | Value + format policy -> Text/document | Layout or conventional representation, possibly locale-sensitive | An inverse parser or semantic preservation after rounding |
| `render` | Template/document/model + context -> artifact | Evaluate presentation structure under a named output context | Generic escaping, source trust or execution authority |
| `encode` | Owned value -> Text/Bytes | Format-defined representation, edition and failure policy | Human readability or canonical bytes |
| `decode` | Text/Bytes -> Result[value, diagnostics] | Validate a representation into owned data under a profile | Merely splitting tokens or accepting unknown fields silently |
| `serialize` | Value/graph -> transport or storage representation | Preserve the documented data model and identity policy | Text output, stable ordering or executable reconstruction |
| `deserialize` | Representation -> Result[value, diagnostics] | Inverse over the supported serialized domain | Trust, authorization or live-resource restoration |
| `parse` | Source -> syntax/value + diagnostics | Apply a named grammar while retaining source evidence | Type/schema validity, name resolution or permission to run |
| `check` | Parsed/value + environment -> checked artifact | Establish exactly enumerated static/schema/policy facts | Live admission, freshness or successful execution |
| `bind` | Checked structure + typed inputs -> bound artifact | Preserve program/value separation and binding identity | Text substitution or raw syntax insertion |
| `quote` | Value/fragment -> one literal/token for dialect/context | Prevent the value from changing that one syntactic role | A whole command/query/document being safe |
| `escape` | Text -> Text for one output context | Encode characters significant in the named context | Validation, sanitization or safety in a nested context |
| `normalize` | Value -> equivalent value under named relation | Apply one documented equivalence or presentation rule | A universal semantic normal form |
| `canonicalize` | Value -> unique representation under a named specification | Stable comparison/hash input for the admitted domain | Preservation of authored spelling or Unicode normalization |
| `read_text` | Path/reader + encoding -> Result[Text, IO/decode error] | Perform IO and decode bytes explicitly | Pure parsing or platform-independent newline identity |
| `write_text` | Path/writer + Text + encoding -> Result | Encode and perform IO with replacement/atomicity policy | Serialization, durable commit or publication |
| `load` | Store/reader -> Result[artifact] | Read persisted state using a named storage contract | Text-only operation or trust in stored contents |
| `save` | Artifact -> store/writer result | Persist using explicit replacement/durability behavior | Export to another system or remote publication |
| `import` | External representation/system -> owned artifact | Cross a system boundary with provenance and compatibility rules | Simple parsing or semantic identity with the source system |
| `export` | Owned artifact -> external representation/system | Produce a declared interchange artifact or external state | Human display or automatic publication |
| `convert` | Representation A -> representation B | A deliberately broad, documented conversion with loss policy | Generic meaning preservation for arbitrary Text |
| `split` / `join` | Text <-> sequence | Structural operation under an exact separator/boundary rule | Record decoding, shell parsing or line-ending preservation |

Three naming laws follow:

1. Name the **semantic destination**, not only the return type. `to_text` is
   insufficient when display, JSON, shell source and an HTML attribute differ.
2. Pair a broad verb with a qualified module or object. `json.encode`,
   `utf8.decode` and `html.escape_text` reveal more than global `encode` or
   `escape` functions.
3. Put expected failure and loss in the signature or policy. A name cannot make
   replacement decoding, locale dependence, rounding or unknown-field dropping
   harmless.

### Python: Compact Names, Several Conventions

Python demonstrates both the value and the ambiguity of established naming:

| Python surface | Contract exposed | Research lesson |
| --- | --- | --- |
| `str(x)` / `__str__` | Informal, printable representation | User-facing text is not required to be source or invertible |
| `repr(x)` / `__repr__` | Information-rich developer representation | Inspectability deserves a separate channel |
| `format(x, spec)` / `__format__` | Representation controlled by a format specification | Formatting policy belongs to the operation, not the value identity |
| `bytes.decode(...)` | Bytes -> `str` under encoding/error policy | The receiver makes direction memorable, but `decode` still needs policy |
| `str.encode(...)` | `str` -> bytes under an encoding/error policy | Encoding is a representation boundary, not generic serialization |
| `json.dump` / `json.load` | Value <-> text stream | Missing `s` means stream/file-like destination or source |
| `json.dumps` / `json.loads` | Value <-> string | The historical suffix is concise but not self-explanatory outside Python |
| `Path.read_text` / `write_text` | IO plus character coding | The name exposes text rather than bytes and keeps IO visible |
| `shlex.split` / `join` | POSIX-like lexical words <-> shell-escaped string | A named dialect is essential; it is not process execution |
| `re.escape` | Literalize regex pattern metacharacters | Even one domain has separate pattern and replacement contexts |

Python explicitly distinguishes `__str__`, `__repr__` and `__format__`.
Its JSON encoder always emits `str`, not bytes, and repeated `dump` calls do
not create a framed stream. `pathlib` separates pure path manipulation from
concrete IO.
[Python data model](https://docs.python.org/3/reference/datamodel.html#object.__repr__),
[JSON encoder/decoder](https://docs.python.org/3/library/json.html), and
[pathlib](https://docs.python.org/3/library/pathlib.html).

The local probe observes three representations from one Python object and a
lossy decimal format that does not round-trip. This does not recommend Python's
dunder protocol for Nomi; it demonstrates why one implicit `to_string` hook
cannot honestly serve diagnostics, UI, persistence and source construction.

### Cross-Language Naming Evidence

| Ecosystem | Producing names | Consuming names | Important distinction |
| --- | --- | --- | --- |
| Rust | `Display`, `Debug`, `ToString`, `format!`, serde `Serialize` | `FromStr`, `parse`, serde `Deserialize` | `Display` may be lossy and not parseable; `Debug` is programmer-facing and unstable |
| Go | `Stringer`, `Formatter`, `TextMarshaler`, `AppendText` | `Scanner`, `TextUnmarshaler` | Destination families (`Print`, `Sprint`, `Fprint`, `Append`) are encoded in names; marshal/unmarshal are paired |
| ECMAScript | `String`, `toString`, template literals/tags, `JSON.stringify`, `TextEncoder.encode` | `JSON.parse`, `TextDecoder.decode` | Generic conversion, structured codec, byte codec and literal-segment construction are different mechanisms |
| Swift | `CustomStringConvertible`, `CustomDebugStringConvertible` | `LosslessStringConvertible.init?` | Lossless conversion is a stronger, separately named protocol from description |
| Java | `toString`, `Formatter`, locale `Format.format` | `Format.parseObject`, type-specific `parse` | `toString` is human-readable and explicitly not stable; locale formats have parsing context |
| .NET | `ToString`, `TryFormat`, `ISpanFormattable` | `Parse`, `TryParse`, `IParsable` | `Try` communicates ordinary failure; culture/style providers change accepted text |
| Elixir | `String.Chars.to_string` | Domain parsers and decoders | Interpolation uses the display-like protocol; `Inspect` is a distinct algebra document and can hide private fields |
| PowerShell | `Format-*`, `Out-*`, `Export-*`, `ConvertTo-*` | `Import-*`, `ConvertFrom-*`, `Read-*` | Verb families distinguish layout, environment output, persistence and representation conversion |

Rust's documentation is unusually explicit: `Display` is user-facing and may
omit precision or state; `FromStr` need not accept it unless the type documents
that round-trip. `Debug` output is programmer-facing and not stable.
[Rust `Display`](https://doc.rust-lang.org/std/fmt/trait.Display.html),
[`FromStr`](https://doc.rust-lang.org/std/str/trait.FromStr.html), and
[`Debug`](https://doc.rust-lang.org/std/fmt/trait.Debug.html).

Go's encoding interfaces come in producer/consumer pairs, require textual
marshaling to produce UTF-8, and state a round-trip obligation from
`MarshalText` to `UnmarshalText`. The documentation warns that adding these
methods can be a breaking wire-format change because encoders discover them.
Go's `fmt` names output destination independently from formatting behavior.
[Go encoding interfaces](https://pkg.go.dev/encoding) and
[`fmt`](https://pkg.go.dev/fmt).

ECMAScript's `JSON.stringify` is a structured-data conversion with specified
omission, replacement and failure behavior; it is not the same operation as
generic `ToString`. Tagged templates expose cooked/raw literal segments and
substitution values to a tag instead of first flattening them into one string.
`TextEncoder`/`TextDecoder` separately cross the byte boundary.
[ECMAScript JSON](https://tc39.es/ecma262/multipage/structured-data.html#sec-json-object),
[template literals](https://tc39.es/ecma262/multipage/ecmascript-language-expressions.html#sec-template-literals),
and [Encoding API](https://encoding.spec.whatwg.org/#api).

Swift makes losslessness a protocol stronger than ordinary textual description.
Java's base `toString` is concise human information and is not stable across
time or runs. .NET's `Parse` throws while `TryParse` reports ordinary rejection,
and culture/style providers affect the recognized language. Elixir separates
interpolation's `String.Chars` from structured, redaction-aware `Inspect`.
[Swift lossless strings](https://developer.apple.com/documentation/swift/losslessstringconvertible),
[Java `Object.toString`](https://docs.oracle.com/en/java/javase/20/docs/api/java.base/java/lang/Object.html#toString%28%29),
[.NET numeric parsing](https://learn.microsoft.com/dotnet/standard/base-types/parsing-numeric),
[Elixir `String.Chars`](https://hexdocs.pm/elixir/String.Chars.html), and
[`Inspect`](https://hexdocs.pm/elixir/Inspect.html).

**Inference:** no ecosystem vocabulary can be copied wholesale. Nomi should
borrow the distinctions: user display versus developer inspection, lossless
codec versus presentation, expected rejection versus exceptional failure,
destination versus layout, and ordinary value conversion versus persistence.

## PowerShell's Controlled Vocabulary

PowerShell formally uses `Verb-Noun` command names. The verb names the general
action, the singular noun names the resource, and parameters refine the action.
The official vocabulary does **not** define parallel adverb or adjective slots;
qualifiers normally live in the noun, parameter names, switches and values.
That correction matters because the useful mechanism is controlled semantic
verbs and discoverable resource nouns, not an English grammar embedded into
every command name.
[Approved verbs](https://learn.microsoft.com/powershell/scripting/developer/cmdlet/approved-verbs-for-windows-powershell-commands)
and [cmdlet naming](https://learn.microsoft.com/powershell/scripting/developer/cmdlet/strongly-encouraged-development-guidelines).

Text-related groups carry strong distinctions:

| Verb | PowerShell meaning | Nomi pressure |
| --- | --- | --- |
| `Format` | Arrange objects in a specified form or layout | Do not treat formatting objects as data serialization |
| `Out` | Send data out of the PowerShell environment | Destination/effect is distinct from representation |
| `ConvertTo` | Convert varied inputs to the noun's primary representation | Direction and target are discoverable |
| `ConvertFrom` | Convert the noun's primary representation to supported outputs | Direction and source are discoverable |
| `Export` | Encapsulate input into persistent storage or interchange format | Persistence/export is stronger than string conversion |
| `Import` | Create usable resources from storage or interchange | Provenance and external contract enter the system |
| `Get` | Retrieve a resource | Retrieval should not be confused with parsing supplied text |
| `Read` | Acquire information from a source | IO/source behavior should stay visible |
| `Write` | Add information to a target | Output effects should not hide behind display conversion |
| `Test` | Verify a condition or resource | A Boolean test is weaker than diagnostics-rich decoding |
| `Select` | Choose from a resource | Projection is not formatting or serialization |
| `Join` / `Split` | Combine or separate resources | Boundary rules must be named for text records |

PowerShell's object pipeline is an additional warning: formatting should occur
near the final human destination. Early formatting discards structured
properties that later pipeline stages could have consumed: `Format-Table`
emits formatting objects, so `Export-Csv` exports their formatting properties
rather than the original records.
[PowerShell export warning](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.utility/export-csv).
The broader lesson
is independent of PowerShell syntax: keep owned values structured through
composition and choose the textual audience at the edge.

Nomi should not impose one approved-verb registry on every library. Domain
language matters, synonyms sometimes carry real distinctions, and verb-noun
names can become cumbersome for ordinary methods. A smaller lintable glossary
for cross-cutting boundary verbs is a credible tool experiment.

## Configuration And Build Files Are Layered Programs

YAML, JSON or line-oriented syntax is often only the first parser. The
application assigns meaning to keys, chooses expression sites, schedules work,
invokes another interpreter and decides whether text is data or source.

| Surface | Text/structure stages | Design evidence |
| --- | --- | --- |
| Ansible | YAML -> Ansible data/tag provenance -> Jinja expression/template -> module/action -> remote boundary | Current Ansible renders trusted template source on the control node; returned values do not automatically become template source |
| GitHub Actions | YAML -> workflow schema -> `${{ }}` expression contexts -> runner interpolation -> chosen shell -> workflow-command/environment-file protocol | Context availability depends on phase; untrusted context text can later reach executable scripts |
| Kubernetes | YAML reader -> JSON-compatible API object -> versioned schema/field validation -> admission -> controller reconciliation | Manifest syntax is not API validity, admission, successful reconciliation or observed health |
| Helm | Go template + Helm functions -> YAML text -> Kubernetes object decoding/admission | `quote`, `toYaml` and `tpl` have different authority; rendering creates another program for another consumer |
| Terraform/HCL | HCL structure/expressions/templates -> provider values -> remote API | `jsonencode`/`yamlencode` construct whole values more reliably than hand-written template punctuation |
| Ninja | Ninja lexer/variable expansion -> rule command string -> platform command runner/shell | Variables usually expand once; rule variables expand at use; `$` is Ninja's escape and command interpretation is later |
| GNU Make | Make parse/expansion -> selected recipe expansion -> configured shell -> process | `$` and `$$` belong to different interpreters; recipe expansion occurs only for selected targets |
| Dockerfile | Dockerfile parser -> instruction-specific parsing -> exec-array or shell form -> process | A JSON-looking exec form and shell form have different argument and expansion semantics |

Ansible 2.19's documented trust-model inversion is especially useful evidence:
only strings from trusted sources are eligible to be templates, while values
may be referenced by those templates. Losing provenance now removes templating
ability instead of granting evaluation. Its removal of an implicit second
literal-evaluation pass also shows that "helpful" string-to-value recovery can
create confusion and security exposure.
[Ansible templating](https://docs.ansible.com/projects/ansible/latest/playbook_guide/playbooks_templating.html)
and [2.19 changes](https://docs.ansible.com/projects/ansible/latest/porting_guides/porting_guide_12.html).

GitHub distinguishes literal strings from expressions and warns that some
contexts contain attacker-controlled values. Its environment-file multiline
protocol warns that a delimiter occurring alone in arbitrary content is unsafe
and recommends a file for arbitrary values.
[GitHub expressions](https://docs.github.com/actions/reference/workflows-and-actions/expressions),
[contexts](https://docs.github.com/actions/concepts/workflows-and-actions/contexts),
and [workflow commands](https://docs.github.com/actions/reference/workflows-and-actions/workflow-commands).

Kubernetes manifests are commonly YAML, but API requests carry serialized
objects whose `apiVersion`, `kind`, metadata and spec have versioned meaning.
Server-side field validation can ignore, warn about or reject unknown and
duplicate fields; even strict schema acceptance is not controller success.
[Kubernetes objects](https://kubernetes.io/docs/concepts/overview/working-with-objects/)
and [API field validation](https://kubernetes.io/docs/reference/using-api/api-concepts/#field-validation).

Ninja deliberately presents itself as a low-level build system whose files are
often generated by a meta-build system. Its small language still has scoped and
phase-sensitive expansion. GNU Make adds another `$` owner when recipes enter a
shell. Terraform explicitly recommends generating JSON/YAML from a whole value
with `jsonencode`/`yamlencode` instead of manually maintaining delimiters.
[Ninja manual](https://ninja-build.org/manual.html),
[GNU Make recipe expansion](https://www.gnu.org/software/make/manual/html_node/Variables-in-Recipes.html),
and [Terraform templates](https://developer.hashicorp.com/terraform/language/functions/templatefile#generating-json-or-yaml-from-a-template).

### Stage Ledger For Generated Text

Before accepting a text-producing API or configuration adapter, record:

| Field | Question |
| --- | --- |
| Producer | Which function/template/person emitted this segment? |
| Representation | Bytes, Text, tokens, tree, value, document or plan? |
| Interpreter | Which exact grammar/schema/engine reads it next? |
| Stage | Parse, template, bind, check, plan, execute or display? |
| Holes | Are insertions values, identifiers, literal fragments or raw source? |
| Trust | Is the source trusted to define computation? Are inserted values only data? |
| Context | HTML text, YAML scalar, shell word, regex pattern, SQL value, etc.? |
| Failure | Which owner reports malformed, unknown, stale, denied or over-budget input? |
| Evidence | Can a diagnostic map generated ranges back to every contributor? |
| Authority | What explicit operation and grant can cause effects? |

A value that cannot answer these questions should remain opaque text. It must
not be promoted to "safe," "validated" or "executable" by a generic wrapper.

## Templating Is Not One Operation

At least four distinct facilities are often called templating:

1. **Message formatting:** human prose plus typed named arguments, plural and
   selection rules, locale and translation context.
2. **Presentation rendering:** a trusted document template produces HTML, text
   or another view with output-context-aware escaping.
3. **Structured value generation:** typed values become JSON/YAML/configuration
   through a format encoder.
4. **Program generation:** source text for a shell, query, policy, workflow or
   programming language is constructed for later interpretation.

Jinja's autoescape is an environment/evaluation-context policy, often selected
by template name. Marking a value safe is fragile across operations that do not
preserve that marker; a text template is not automatically safe for HTML,
JavaScript, CSS, URLs and attributes at once.
[Jinja API](https://jinja.palletsprojects.com/en/stable/api/#autoescaping) and
[template escaping](https://jinja.palletsprojects.com/en/stable/templates/#html-escaping).

ICU message formatting keeps a translatable message as a unit so translators
can reorder arguments and choose plural/select branches. Concatenating localized
fragments loses grammatical context. A Nomi display string, localized message,
HTML template and machine codec therefore should not share one universal
interpolation contract.
[ICU messages](https://unicode-org.github.io/icu/userguide/format_parse/messages/).

**Candidate rule:** ordinary Nomi interpolation remains convenient display
construction. Domain encoders receive values; message renderers receive a
message identity, locale and named arguments; source builders receive parsed
fragments or role-checked holes. None silently feeds its output to another
evaluator.

## Exactness, Round Trips And Canonicalization

"Round-trip" can name several different laws:

```text
decode(encode(value)) == value
parse(format(tree)) is semantically equivalent to tree
format(parse(source)) is canonical source
lossless_format(parse(source)) preserves source and trivia
display(parse(display(value))) approximately recovers a value
```

Only the first is a normal codec law, and even it needs a supported value
domain. Terraform documents that JSON cannot represent all Terraform types, so
`jsondecode(jsonencode(value))` may change type information. Rust documents that
`Display` need not round-trip through `FromStr`. Java's locale `Format` notes
cases where adjacent formatted values cannot be parsed unambiguously.

Canonicalization is not pretty-printing and not Unicode normalization. JSON
Canonicalization Scheme constrains data, primitive serialization and property
ordering for repeatable hashing; it explicitly preserves Unicode string data
without applying Unicode normalization. Generic `canonicalize(text)` would
erase which equivalence relation and consumer justified the transformation.
[JCS](https://www.rfc-editor.org/rfc/rfc8785.html).

## Lines, Records, Streams And Files

"Text file" does not settle the record contract. POSIX text files constrain
lines, NUL and maximum line length for utilities; arbitrary files may contain
mixed CRLF/LF/CR, a final unterminated line, NUL, huge lines or partial code
units. Python's `splitlines()` deliberately recognizes several boundaries and,
without `keepends`, cannot reproduce them.
[POSIX text file definition](https://pubs.opengroup.org/onlinepubs/9799919799/basedefs/V1_chap03.html#tag_03_387).

Text transports need explicit answers for:

- encoding and invalid-sequence policy;
- newline recognition, preservation and canonical output;
- record delimiter and collision/framing policy;
- maximum record, nesting and total sizes;
- partial final records and retry/resume identity;
- backpressure, cancellation and flush behavior;
- atomic replacement, durability and concurrent readers;
- whether comments, ordering, duplicate keys and spelling survive;
- media type, edition, schema and content-coding metadata.

Newline-delimited formats are pleasant while values cannot contain raw newlines
or have a real escaping/framing rule. Sentinel-delimited multiline protocols
must prove that the sentinel cannot collide, generate a checked unique delimiter,
or carry the arbitrary payload out of band. The local delimiter probe is an
original finite model; it is not GitHub runner conformance.

## Human Editing And Tooling

Text remains Nomi's recommended first primary representation because it offers
a universal fallback. That recommendation creates obligations beyond parsing
complete files:

- retain invalid and incomplete draft text while exposing recovered structure;
- distinguish authored source, formatted source and generated artifacts;
- preserve comments/trivia under a separately stated lossless contract;
- attach diagnostics to exact or honestly coarse spans after interpolation,
  decoding, normalization and generated expansion;
- identify offset units at every API boundary;
- keep selection and cursor motion grapheme-aware while compiler spans remain
  stable in a specified source coordinate system;
- show tabs, line endings, trailing space, control characters and invalid bytes
  on demand without silently rewriting them;
- support bidirectional text according to lexical structure, not only plain-text
  display order;
- diagnose relevant confusable identifiers early without prohibiting legitimate
  multilingual prose and names;
- preserve a plain-text fallback for screen readers, terminals, patches and
  environments without a rich projection;
- make large/generated/minified text inspectable with bounded previews and an
  exact artifact download rather than truncating without evidence.

Unicode Source Code Handling recommends lexically aware bidirectional display
and early diagnostics for confusable identifiers. It also observes that diffs,
terminals and email patches may only render plain text.
[Unicode source handling](https://www.unicode.org/reports/tr55/) and
[security mechanisms](https://www.unicode.org/reports/tr39/).

The Language Server Protocol negotiates position encoding because UTF-8,
UTF-16 and UTF-32 offsets are not interchangeable. Nomi's parser, diagnostics,
Monaco bridge and source maps need one internal coordinate contract plus
explicit adapters; relying on Python indices in one backend and JavaScript
indices in another will eventually misplace diagnostics.
[LSP 3.17](https://microsoft.github.io/language-server-protocol/specifications/lsp/3.17/specification/#positionEncodingKind).

## Security And Authority

Text's universality makes it an unusually effective authority-smuggling medium.
The following hazards are different and need different controls:

| Hazard | Boundary failure | Needed response |
| --- | --- | --- |
| Injection | A value becomes grammar in SQL, shell, HTML, regex or a template | Typed parameters or destination/role-specific construction |
| Template injection | Untrusted data becomes trusted template source | Source trust provenance; no implicit second evaluation |
| Control-sequence injection | Logs/terminals interpret escape sequences | Bounded escaped inspection; safe terminal writer policy |
| Log forging | Newlines/control fields create apparent records | Structured events and explicit text rendering/framing |
| Secret exposure | Display/debug/source maps stringify protected values | Redaction before rendering, with retained sensitivity provenance |
| Unicode spoofing | Displayed tokens differ from lexical order or resemble other names | Lexical display, control visibility and scoped confusable diagnostics |
| Resource exhaustion | Small source expands, backtracks, nests or emits huge output | Separate input, depth, work, time and output budgets |
| Canonicalization mismatch | Signer and verifier compare different representations | One pinned canonicalization contract and exact preimage evidence |
| Stale interpretation | Same Text is checked under changed schema/environment | Artifact identity includes edition, schema and environment |
| Capability laundering | Saved/rendered text is later executed with ambient authority | Execution accepts explicit grants, never authority from serialization |

Escaping is neither validation nor authorization. "Sanitize" is too vague for a
public primitive unless it names a policy and result domain. A safe HTML text
node is not safe inside a JavaScript string; a shell-quoted word is not a safe
shell program; a SQL value parameter cannot stand for a table name.

## Text And Conversational/Generated Systems

Generated text is a proposal or artifact, not evidence of intent or authority.
For agent and model interfaces:

- keep instructions, supplied data, retrieved evidence and generated proposals
  as separately attributed contributions;
- use typed tool schemas for action parameters rather than parsing persuasive
  prose back into commands;
- preserve exact source and model/tool/version identity for generated patches;
- require ordinary parser/type/schema/effect checks after generation;
- bind human review to the exact candidate and material inputs;
- never treat a fenced code block, JSON-looking paragraph or confident wording
  as a capability grant;
- report truncation and omitted context before presenting an explanation as
  complete.

Text remains valuable here precisely because a person can inspect and revise it.
That benefit disappears when hidden parsing or ambient execution turns prose
directly into effects.

## Candidate Nomi API Shape

The following is explanatory notation. Module names, protocols, generics and
error variants are not accepted:

```text
display.text(value, audience, locale, redaction) -> Text
inspect.document(value, limits, redaction) -> Inspection

utf8.encode(text) -> Bytes
utf8.decode(bytes, errors=Strict) -> Result[Text, DecodeError]

json.encode(value, profile) -> Result[Text, EncodeError]
json.decode(source, profile, limits) -> Result[Decoded[Value], DocumentErrors]
resource.decode(document, schema) -> Result[Resource, FieldErrors]

regex.parse(source, dialect) -> Result[ParsedPattern, PatternErrors]
regex.literal(text, dialect) -> Pattern

template.parse(trusted_source, language) -> Result[Template, TemplateErrors]
template.render(template, bindings, output_context, limits) -> Result[Rendered, RenderErrors]

process.prepare(program, argv, environment, directory) -> ProcessInvocation
process.run(invocation, grant) -> Result[ProcessReport, ProcessError] uses Process
```

Properties to falsify:

1. Display/inspect output is never accepted implicitly by a decoder.
2. Strict decode never inserts replacement characters; repairing decode returns
   repair evidence and cannot masquerade as exact source.
3. Encoding then decoding preserves every admitted value or reports the
   documented representational loss before encoding.
4. Parser/checker artifacts retain exact source, edition, owner and diagnostics.
5. Bound values cannot introduce structure outside their declared hole role.
6. Rendering never upgrades an untrusted value into template source.
7. Source construction, checking and previewing require no execution grant.
8. Redaction survives formatting, interpolation, diagnostics and source mapping.
9. Text offsets name their coordinate system and remain correct across backends.
10. No saved text or serialized plan contains ambient or replayable authority.

The [target-only pressure program](../../design/targets/research/text_boundaries.nomi)
puts these distinctions into ordinary source-shaped examples without claiming
that the imports exist or the file typechecks.

## Implementation Destinations

This research should become small contracts in existing owners rather than a
new universal text subsystem:

| Pressure | Existing extraction point | First reversible step |
| --- | --- | --- |
| Literal/interpolation contract | `prototype/grammar/`, parser frontends and canonical syntax | Golden vectors for braces, raw/multiline text, CRLF and invalid forms across frontends |
| Text/Bytes conversion | runtime scalar/codec design and Python/JS bridges | Backend-neutral UTF-8 strict-decode vectors with explicit failure offsets |
| Display versus inspection | diagnostics, CLI and browser value rendering | Two internal rendering intents plus mandatory secret redaction tests |
| Document encoding | decoding/design packet and adapter libraries | JSON value encoder/strict decoder spike; no generic serialization protocol yet |
| Source positions | parser payloads, diagnostics, Monaco worker and LSP-facing tooling | Inventory current offset units, then add astral/combining/CRLF parity fixtures |
| Process arguments | process/effect boundary, not string interpolation | Inspectable argv invocation value; no shell execution in the browser |
| Templates/messages | library experiment | Compare ICU-style named messages, trusted templates and structured encoders on one fixture |
| Naming discipline | docs/lint/tool metadata | Experimental boundary-verb glossary warning, never a compiler naming restriction |
| Generated provenance | Surface/source map and interaction evidence | Segment record for literal/value/generated contributions with coarse-span fallback |
| Security controls | diagnostics and host capabilities | Invisible-control/confusable diagnostics plus terminal/log safe rendering fixtures |

No parser or runtime implementation should begin with a generic `SafeText`,
`ValidatedText`, `Stringable`, template evaluator or user-extensible grammar.
Those names would combine guarantees that the evidence keeps separate.

## Bounded Experiments T1-T10

| ID | Comparison | Oracle | Stop / reject condition |
| --- | --- | --- | --- |
| T1 | `display`, `inspect`, format policy and codec on the same values | Audience, stability, redaction and round-trip claims remain distinct | One implicit hook feeds logs, UI and persistence |
| T2 | Strict UTF-8 decode versus repair with evidence | Invalid byte offset and original bytes remain recoverable | Silent replacement under an exact API |
| T3 | Scalar, UTF-8, UTF-16 and grapheme coordinates | CLI/browser diagnostics select the same visible source | Backend-dependent columns or split grapheme cursor edits |
| T4 | Typed JSON/YAML encoding versus text templates | Values preserve type/shape and cannot add sibling fields | Manual quoting wins only by ignoring adversarial inputs |
| T5 | Trusted template plus values versus second-pass templating | Supplied text remains data at every later stage | Any ordinary value becomes executable template source |
| T6 | Argv invocation versus POSIX and Windows shell source | Exact arguments and preview survive spaces, newlines, leading dashes and wildcards | A universal quote function is required |
| T7 | Fixed sentinel, generated sentinel and length-prefixed framing | Arbitrary payload round-trips or collision is rejected before output | Collision can truncate/reinterpret a record |
| T8 | Source-preserving parse/format versus semantic canonical format | Comments/trivia and semantic equality are reported separately | Formatter claims a lossless round-trip it cannot provide |
| T9 | Localized message object versus fragment interpolation | Translators can reorder named typed arguments and plural branches | English word order is embedded in application concatenation |
| T10 | Text-primary source plus projection versus structured primary document | Invalid drafts, diffs, accessibility, identity and inverse edits are measured | Either candidate is declared universal without user/tool evidence |

T1-T3 and T7 now have small host/model observations in
[executed probes](experiments.md). They do not establish Nomi behavior. T4-T10
remain candidate comparisons even where neighboring documentary evidence is
strong.

## Research Judgment

The [generic-operation hierarchy](../generic_operations.md) carries
display/inspection/encoding and equality/hash context into reusable value
protocols. A broadly available method remains conditional on its law/profile;
serialization is not automatically a property of every object or callable.

Retain text as Nomi's primary authored and fallback interface. Make simple prose
and interpolation pleasant. At boundaries, prefer owned values, explicit
decoders, contextual encoders, typed arguments, preserved source and separate
execution. Add rich text/domain types only when they enforce a guarantee that a
module plus `Text` cannot expose clearly.

The next design decision is not new string punctuation. It is a small scalar and
rendering contract that says:

- what `Text` contains and how it relates to Bytes;
- which indexing/offset units public APIs expose;
- what ordinary interpolation calls for supplied values;
- how display, inspection and encoding differ;
- how invalid decoding, normalization and line endings are represented;
- how secrets and generated-source contributions survive rendering.

Close that contract with T1-T3 before admitting a general codec, template or
embedded-language facility.
