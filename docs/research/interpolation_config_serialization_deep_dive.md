# Interpolation, Config, And Serialization Languages: Deep Dive

> Status: source research for Nomi representation-boundary design.
>
> Scope: documentation-only synthesis of interpolation/template languages,
> configuration formats, schema languages, and serialization formats. This is
> not an active syntax spec. Fold stable decisions into `../convenience/`,
> `../features/`, or `../language/` after normal-form review.
>
> Purpose: treat interpolation, config, and serialization as one family of
> representation-boundary systems: places where values become text/bytes, text
> or bytes become values, or a document describes how such conversion should
> happen.

## Why This Matters

Nomi's recent research notes covered interface languages and remaining advanced
feature gaps. Interpolation, config, and serialization sit between them:

```text
interpolation -> values become text for a sink
template -> values become a structured text document
config -> text/data declares desired settings
schema -> document describes valid external shape
serialization -> owned values become wire/storage bytes
deserialization -> wire/storage bytes become owned values
```

These are not minor library topics. They are where many production bugs and
security vulnerabilities appear:

- SQL/HTML/shell injection through interpolation;
- YAML/TOML/JSON config ambiguity;
- schema drift between OpenAPI/JSON Schema/protobuf and application code;
- lossy serialization of dates, decimals, enums, bytes, and missing values;
- template languages that grow loops, conditionals, filters, includes, and
  imports until they become a second programming language.

The synthesis target is:

```text
representation boundary -> typed sink/source -> policy -> provenance -> explain
```

## Source Scan

Primary and near-primary references used for this pass:

- Python lexical analysis, formatted string literals:
  <https://docs.python.org/3/reference/lexical_analysis.html>
- ECMAScript template literals, via MDN/spec links:
  <https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Template_literals>
- Jinja template designer documentation:
  <https://jinja.palletsprojects.com/en/2.10.x/templates/>
- Terraform expressions, strings, and templates:
  <https://developer.hashicorp.com/terraform/language/expressions>
- HCL repository and language model:
  <https://github.com/hashicorp/hcl>
- JSON RFC 8259:
  <https://datatracker.ietf.org/doc/rfc8259/>
- YAML 1.2.2 specification:
  <https://yaml.org/spec/1.2.2/>
- TOML v1.0.0:
  <https://toml.io/en/v1.0.0>
- JSON Schema 2020-12:
  <https://json-schema.org/specification>
- Protocol Buffers proto3 language guide:
  <https://protobuf.dev/programming-guides/proto3/>
- Apache Avro documentation:
  <https://avro.apache.org/docs/>

## 1. Interpolation And Template Languages

### User Need

Users need to produce text:

```text
log message
CLI output
file path
URL
SQL query
HTML
JSON document
shell command
email
configuration snippet
generated source code
```

Python f-strings, JavaScript template literals, Terraform templates, Jinja,
Mustache, ERB, JSX, and many logging/format strings all answer this need.

### What Works

Plain interpolation is humane:

```python
f"Hello {name}"
```

It gives users one obvious way to combine literal text and values. JavaScript
tagged templates show another useful idea: the interpolator can be a function
that receives literal segments and values separately, allowing sink-specific
escaping or typed output.

Template engines such as Jinja succeed because they are convenient at document
scale: loops, conditionals, filters, includes, inheritance, and autoescaping
let a mostly-static document contain dynamic parts.

### What Fails

Interpolation becomes dangerous when the target sink is not plain text:

- SQL requires parameterization, not string concatenation;
- HTML requires escaping plus context awareness;
- shell commands require argv construction, not joined strings;
- URLs require component-aware encoding;
- JSON/YAML/TOML should usually be produced by serializers, not hand templates;
- generated code requires syntax-aware construction and source maps.

Template engines fail by becoming second languages. Once a template has
variables, loops, conditionals, filters, imports, includes, inheritance,
macros, whitespace control, and autoescaping policy, users must learn a
separate execution model with its own scoping and error behavior.

### Nomi Implication

Nomi should separate plain string interpolation from typed templates.

Nomi normal form:

```text
plain interpolation -> String construction
typed interpolation -> Template[Sink] value + escaping/encoding policy
SQL construction -> query value with parameters
HTML construction -> HTML value with context-aware escaping
shell construction -> Command value with argv, never joined command text
URL construction -> URL value with component encoding
generated code -> SyntaxValue or source artifact with spans
```

Admission posture:

- plain interpolation belongs in the everyday language;
- sink-specific templates are library-first typed values;
- SQL/HTML/shell templates must not return raw strings by default;
- template engines with control flow should be block policies or future scoped
  extensions, not a hidden sub-language inside strings.

## 2. Configuration Languages

### User Need

Config needs to express:

```text
defaults
environment-specific overrides
CLI/env/file layering
documentation
constraints
references
merge behavior
secrets/redaction
provenance
machine generation
human editing
```

TOML chooses obvious key/value configuration. YAML chooses flexible
human-authored nested data. HCL gives applications a structured config model
with attributes, blocks, expressions, and a JSON variant. CUE, Nickel, Pkl,
Dhall, Nix, Terraform, and JSON Schema add constraints, merging, defaults,
imports, and reproducibility.

### What Works

TOML's strength is bounded ambition: obvious key/value pairs, arrays, tables,
and typed scalars. HCL's strength is making blocks and attributes part of an
information model rather than treating config as arbitrary maps. CUE/Nickel/Pkl
show that config often needs validation, defaults, merge, and documentation.

The recurring successful pattern is:

```text
source document + source path + merge policy + validation -> trusted config
```

### What Fails

Config fails when it becomes a weak programming language:

- YAML has many scalar and string forms, so human readability can hide parser
  surprises;
- HCL/Terraform expressions can become dynamic enough to obscure intent;
- Nix/Dhall/CUE-style power can be excellent but may make config feel like
  programming;
- layered config often loses provenance;
- secrets are frequently treated as ordinary strings;
- defaults and omission/null semantics differ across formats.

### Nomi Implication

Nomi's existing direction is right: config is a data-boundary problem, not a
peer language.

Nomi normal form:

```text
config source -> parsed external Value + SourcePath
merge -> ordered flow with conflict policy
decode -> owned Data value with constraints/defaults
secret -> capability-marked/redacted value
explain -> source, path, merge origin, default, failed rule
```

Potential shape:

```nomi
config =
    Config.defaults
    |> config.merge(toml("app.toml"), optional: true)
    |> config.merge(env(prefix: "APP_"))
    |> config.merge(cli_args(argv))
    |> decode AppConfig
```

The important point is that TOML/YAML/JSON/HCL remain source formats. They do
not define Nomi's data model.

## 3. Serialization And Wire Formats

### User Need

Serialization needs to answer:

```text
how values become bytes/text
how bytes/text become values
what schema governs the boundary
how versions evolve
how unknown fields are handled
how missing/default fields behave
how numbers, decimals, dates, bytes, enums, and nulls round-trip
what is human-readable vs compact/fast
```

JSON, YAML, TOML, XML, CSV, Protocol Buffers, Avro, MessagePack, CBOR, Parquet,
and Arrow are different points in this space.

### What Works

JSON works because it is small, text-based, language-independent, and easy to
inspect. Protocol Buffers work because a `.proto` schema can generate code and
define a compact binary wire format. Avro's notable design pressure is schema
being part of data exchange and schema evolution rather than only codegen.

The durable lesson is that serialization is a boundary contract, not just a
string/bytes operation.

### What Fails

Serialization fails at semantic edges:

- JSON has no native date, decimal, bytes, or comments;
- YAML is flexible enough that loaders and versions matter;
- TOML is good for config but not a general wire protocol;
- protobuf is efficient but requires a schema/codegen culture;
- schema evolution rules are easy to violate;
- generated code can drift from runtime behavior;
- lossless round-tripping is often assumed but not guaranteed.

### Nomi Implication

Nomi should define serialization through codecs:

```text
Codec[Source, Target]
Encoder[T]
Decoder[T]
SchemaExport[T]
```

Nomi normal form:

```text
serialize value -> encoded representation + codec metadata
deserialize bytes/text -> Result[Value, DecodeFailure]
schema import/export -> tool artifact, not peer language authority
version migration -> explicit transform with provenance
unknown field -> policy: reject / preserve / ignore / warn
```

`data` should own the local program shape. Serialization formats should be
adapters with explicit policies.

## 4. Schema Languages

### User Need

Schemas need to describe values before or outside the program:

```text
valid JSON document
API request/response
wire message
database table
config file
event stream
generated client/server contract
```

JSON Schema, OpenAPI, Protocol Buffers, Avro schemas, XML Schema, GraphQL SDL,
and database schemas all solve pieces of this.

### What Works

Schemas improve tooling:

- generated docs;
- generated clients;
- validation before execution;
- editor completions;
- compatibility checks;
- examples and tests.

### What Fails

Schema systems drift when there are too many authorities:

```text
source code says one thing
schema says another
docs say another
runtime validators say another
tests assume another
```

JSON Schema is expressive but itself a language. Protocol Buffers are clear but
can make the `.proto` file the real source of truth. OpenAPI is useful but
often lags actual service behavior.

### Nomi Implication

Nomi needs explicit authority rules:

```text
owned program data -> `data`
external boundary contract -> imported schema/codec
runtime trust crossing -> decode
tooling artifact -> schema export/import with hash/version
```

Schema import is useful; schema authority should be visible.

Nomi normal form:

```text
schema -> boundary contract
data -> owned local shape
decode -> reconcile external contract with owned shape
explain -> show schema path, data field, failed rule, source span
```

## Cross-Language Synthesis

### Invariants

- **Representation is not meaning.** JSON, YAML, TOML, protobuf bytes, and
  templates are representations of values, not the values themselves.
- **The sink/source matters.** A string safe for logs may be unsafe for SQL,
  shell, HTML, URLs, or JSON.
- **Schema authority must be explicit.** Generated code, runtime validation,
  and external schema files cannot all silently claim to be source of truth.
- **Config needs provenance.** Defaults, file values, environment variables,
  CLI args, and secrets need source paths and merge history.
- **Serialization needs evolution policy.** Unknown fields, missing fields,
  default values, enum changes, and numeric precision are semantic decisions.
- **Templates grow into languages.** Control flow inside templates must be
  fenced, inspectable, and formatter-aware.

### Anti-Patterns

Avoid importing these:

- raw string interpolation into SQL, shell, HTML, URLs, or code;
- template engines as an untyped second language inside strings;
- config values with no provenance or merge explanation;
- schema export that drops custom constraints without warning;
- separate `schema`/`config` declarations that duplicate `data`;
- treating JSON/YAML/TOML as owned data instead of external representation;
- code generation that hides source spans and generated names;
- default/null/omitted field behavior that differs silently by format.

## Nomi Adopt / Refuse / Adapt

| Source idea | Decision | Nomi reason |
| --- | --- | --- |
| Plain interpolation | Adopt | Everyday string construction is universal. |
| Tagged/typed templates | Adapt | Useful as typed sink values with escaping policy. |
| Raw SQL/HTML/shell string templates | Refuse | Unsafe; use query/HTML/Command values. |
| Jinja-style document templates | Library-first | Useful, but must remain fenced and typed by sink. |
| TOML-style obvious config | Adapt | Good source format; decode into owned `data`. |
| YAML flexibility | Adapt cautiously | Accept as external data only with strict decode policy. |
| HCL blocks/attributes | Adapt | Good information model; avoid dynamic config as core syntax. |
| CUE/Nickel/Pkl constraints | Adapt | Provenance/default/merge lessons; do not make peer config language. |
| JSON as universal interchange | Adopt as codec | Small useful representation; not Nomi's data model. |
| JSON Schema/OpenAPI | Adapt | Boundary contracts and tooling artifacts. |
| Protocol Buffers/Avro | Adapt | Schema evolution and compact codecs; keep codegen/tooling separate. |
| Schema export from `data` | Adopt as tooling | Useful docs/client generation; warn on lossy constraints. |

## Nomi Design Directions

### 1. Typed Sinks

Interpolation should know what it is building:

```text
String
SQLQuery
HTML
URL
Command
JSONText
SyntaxValue
```

Each sink has its own escaping, validation, redaction, and explanation policy.

### 2. Codec Registry

Serialization should be driven by registered codecs:

```text
json
yaml(strict)
toml
csv
protobuf(schema)
avro(schema)
```

Every codec should state:

- accepted source type;
- output representation;
- unknown-field policy;
- missing/default policy;
- number/date/bytes policy;
- provenance support;
- lossy/lossless claim.

### 3. Config As Flow

Layered config is flow over sources:

```text
defaults |> file |> env |> cli |> decode
```

The merge operation should preserve source provenance and conflict diagnostics.

### 4. Schema As Boundary Artifact

Schema import/export is tooling, not language authority by default. A package
may declare that an external schema is authoritative, but that declaration must
be visible in the module/package metadata and in `explain`.

## Bottom Line

Interpolation, config, and serialization are one design family: representation
boundaries. Nomi should handle them with the same discipline as process/API
boundaries:

```text
typed source/sink
  -> explicit codec or template policy
  -> owned `data` value or typed output value
  -> provenance and redaction
  -> explainable failure
```

This lets Nomi stay friendly for ordinary strings and config while refusing the
old trap: "just build the important thing as a string."

