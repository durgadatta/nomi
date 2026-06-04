# Everyday Interface Languages: Deep Dive

> Status: source research for Nomi language-design pressure.
>
> Scope: comparative design note for computational surfaces that are often not
> treated as mainstream programming languages: Unix shell scripting,
> PowerShell, Excel formulas, Make, jq, CSS selectors, GraphQL, HTTP, and
> OpenAPI. This is not an active Nomi syntax spec. Fold stable decisions into
> `../convenience/`, `../features/`, or `../language/` after normal-form
> review.
>
> Purpose: extract what these everyday interface languages teach about process
> orchestration, grid calculation, resource-shaped APIs, selectors, pipelines,
> schemas, and inspectable boundaries.

## Why This Matters

Most language-design surveys over-weight general-purpose languages. But many
people meet computation first, or most often, through interfaces that do not
look like "programming languages" in the classic sense:

```text
shell command -> process and text stream
PowerShell pipeline -> object stream and command metadata
spreadsheet formula -> cell-local calculation over a visible grid
Make rule -> file target, prerequisites, recipe
jq filter -> JSON stream transformation
CSS selector -> structural pattern over a document tree
GraphQL query -> typed selection over a service graph
HTTP request -> method, resource, headers, representation
OpenAPI document -> machine-readable API boundary
```

These surfaces are not peripheral. They are proof that programming grows at
interfaces: files, processes, workbooks, URLs, tables, schemas, documents, and
services. Nomi should study them because Nomi's adoption path will likely be
ordinary automation, data transformation, notebooks, APIs, and small tools
before it is large application architecture.

The synthesis target is not:

```text
copy shell syntax
copy Excel formulas
copy REST route spelling
```

It is:

```text
source surface -> user need -> semantic difference -> Nomi normal form
```

## Source Scan

Primary and near-primary references used for this pass:

- GNU Bash Reference Manual, Shell Expansions:
  <https://www.gnu.org/s/bash/manual/html_node/Shell-Expansions.html>
- Bash Reference Manual, pipelines and shell behavior:
  <https://www.gnu.org/s/bash/manual/bash.html>
- Microsoft Learn, PowerShell pipelines:
  <https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_pipelines>
- Microsoft Support, Excel `LET`:
  <https://support.microsoft.com/en-us/office/let-function-34842dd8-b92b-4d3f-b325-b8b8f9908999>
- Microsoft Support, Excel `LAMBDA`:
  <https://support.microsoft.com/office/lambda-function-bd212d27-1cd1-4321-a34a-ccbf254b8b67>
- Microsoft Support, dynamic arrays and spilled arrays:
  <https://support.microsoft.com/en-us/office/dynamic-array-formulas-and-spilled-array-behavior-205c6b06-03ba-4151-89a1-87a7eb36e531>
- Microsoft Support, structured references in Excel tables:
  <https://support.microsoft.com/en-gb/office/using-structured-references-with-excel-tables-f5ed2452-2337-4f71-bed3-c8ae6d2b276e>
- GNU Make Manual:
  <https://www.gnu.org/software/make/manual/make.html>
- jq 1.8 Manual:
  <https://jqlang.org/manual/>
- W3C Selectors Level 4:
  <https://www.w3.org/TR/selectors-4/>
- GraphQL Specification, October 2021:
  <https://spec.graphql.org/October2021/>
- RFC 9110, HTTP Semantics:
  <https://httpwg.org/specs/rfc9110.html>
- OpenAPI Specification 3.1.1:
  <https://spec.openapis.org/oas/v3.1.1.html>

## Cross-Surface Thesis

Everyday interface languages converge on five design moves:

1. **They bind computation to a world surface.** The world surface may be a
   filesystem, process table, workbook grid, HTTP resource, document tree, JSON
   stream, or API schema.
2. **They privilege local readable actions.** A shell command, formula,
   selector, route, or query can usually be read without opening a full program.
3. **They hide an execution model until it breaks.** Word splitting, pipeline
   serialization, formula recalculation, cache semantics, dependency rebuilds,
   selector specificity, and API status codes are mostly implicit in ordinary
   use.
4. **They become powerful through composition.** Pipelines, chained filters,
   formulas over ranges, selectors plus combinators, GraphQL selection sets,
   and OpenAPI `$ref` all compose small pieces.
5. **They fail at boundaries.** Quoting, escaping, missing cells, dirty build
   targets, API version drift, nullability, status-code interpretation, and
   schema mismatch are the recurring pain points.

Nomi should extract the compositional wins while making boundary semantics
visible enough for `explain`, diagnostics, and future tooling.

## 1. Unix Shell Scripting

### User Need

The Unix shell is a language for immediate world contact:

- run programs;
- connect standard input and output;
- inspect and transform text;
- branch on process success;
- orchestrate files and directories;
- glue existing tools with little ceremony.

The key adoption lesson is latency. The user can type one command, see an
effect, then grow it into a script.

### What Works

Pipelines make transformation visible left-to-right:

```sh
cat access.log | grep 500 | sort | uniq -c
```

Exit status gives every command a small result protocol. Redirection makes
files, pipes, and terminal streams feel like one family. Shell variables,
command substitution, globbing, and here-documents make short automation
remarkably compact.

The deeper design insight is that the shell treats external programs as the
standard library. It succeeds because it is not self-contained.

### What Fails

Shell semantics become hazardous because too many things pass through strings:

- expansion order matters;
- unquoted values are split into words;
- filename expansion can reinterpret data as paths;
- whitespace and newlines carry accidental structure;
- exit status has only coarse success/failure information;
- pipelines can hide partial failure unless configured carefully;
- shell injection is easy when command construction is stringly.

The Bash expansion model is powerful but cognitively expensive: a written word
can pass through brace expansion, parameter expansion, command substitution,
word splitting, filename expansion, and quote removal before the command sees
arguments.

### Nomi Implication

Nomi should not copy shell's stringly default. It should adopt:

- value-first pipelines;
- explicit process values;
- typed argument vectors rather than shell-joined command strings;
- structured process results with `stdout`, `stderr`, `status`, `signal`,
  `duration`, and redaction metadata;
- an `explain` form that shows argv, environment deltas, working directory,
  redirections, and pipeline failure policy before execution when possible.

Nomi normal form:

```text
process call -> Command value + Argument values + Host capability
pipeline -> sequence of Process/Function stages with stream policy
shell text -> explicit string boundary, never the default command model
exit status -> Result[ProcessOutput, ProcessFailure]
```

## 2. PowerShell

### User Need

PowerShell answers a real weakness in Unix shell: administrators do not only
move lines of text; they move objects with properties. Its pipeline carries
structured .NET objects, while cmdlet naming and parameter metadata make
commands discoverable.

### What Works

The object pipeline lets a later stage access named properties rather than
parsing columns:

```powershell
Get-Process | Where-Object CPU -gt 100 | Sort-Object CPU
```

The verb-noun convention improves command discovery. Cmdlets expose parameters,
types, aliases, help text, and pipeline-binding behavior. This makes tooling
more reliable than ad hoc text filters.

### What Fails

PowerShell also shows the cost of object richness:

- object formatting and object values are separate, but users can confuse them;
- the pipeline has binding rules that are not always locally obvious;
- commands are verbose compared with Unix shell;
- crossing into native executables reintroduces string and quoting problems;
- runtime reflection makes many failures late.

### Nomi Implication

PowerShell points toward a Nomi process layer that is structured first and
text-compatible second. The useful abstraction is not "everything is an
object"; it is "pipeline stages declare what kind of value they accept and
emit."

Nomi normal form:

```text
pipeline stage -> accepts Value shape + emits Value shape
cmd metadata -> callable signature + examples + host capabilities
native process boundary -> explicit bytes/text/object adapter
```

Potential Nomi direction:

```nomi
ps("Get-Process")
| where .CPU > 100
| sort .CPU
```

This should remain a library/host capability until Nomi's own collection and
process result contracts are mature.

## 3. Excel Formulas And Workbooks

### User Need

Excel is a mass-market programming environment because it makes computation
visible, spatial, incremental, and immediately useful. A cell can contain a
literal, formula, error, formatted value, or reference into a larger grid. A
workbook is simultaneously program, data store, UI, report, and execution
environment.

### What Works

Excel's design strengths are often under-valued in PL discussions:

- cell-local formulas are easy to start;
- recalculation gives a live feedback loop;
- references expose dependencies in a concrete spatial model;
- dynamic arrays let a formula produce multiple neighboring values;
- structured table references replace fragile coordinates with names;
- `LET` gives formula-local names for readability and performance;
- `LAMBDA` lets users package formulas as workbook-native functions.

Excel is also a lesson in gradual reification. A beginner writes one formula.
Later they name intermediate values, use tables, spill arrays, and define
custom functions without leaving the workbook.

### What Fails

The same spatial model creates long-term fragility:

- formulas and data can be mixed invisibly;
- copy/paste changes references by default;
- errors are values but often lack domain-specific meaning;
- implicit type coercions can surprise users;
- hidden sheets, named ranges, and formatting can obscure logic;
- dependency graphs are present but not always inspected;
- collaborative changes can mutate both data and program at once.

### Nomi Implication

Nomi should learn from Excel's first-hour success without becoming a grid
language. The durable normal forms are:

```text
cell formula -> binding plus dependency edges
range -> collection/table value with shape
structured reference -> named projection over table shape
spill -> dynamic collection result with occupied-output check
LET -> local binding expression
LAMBDA -> named function value
recalculation -> dependency-driven evaluation profile
```

Nomi design pressure:

- notebooks and examples should show live dependency traces;
- table/range operations should explain shape and cardinality;
- errors should be values with provenance when they are expected domain
  failures;
- local names inside expressions should be ordinary bindings, not a separate
  formula-only system;
- generated examples should be inspectable as dependency graphs, not just
  printed output.

## 4. Make And Task Languages

### User Need

Make is a compact language for asking:

```text
Is this target up to date relative to its prerequisites?
If not, what recipe rebuilds it?
```

This is not ordinary control flow. It is dependency judgement over files.

### What Works

Make's lasting design contribution is the target/prerequisite/recipe shape:

```make
build/app: main.o util.o
	$(CC) -o $@ $^
```

The programmer declares artifacts and dependencies; the tool computes which
recipes need to run. Pattern rules and automatic variables reduce repetition.
This model still underlies modern build systems, task runners, and CI graphs.

### What Fails

Make mixes two languages: Make expansion and shell recipes. That split causes
quoting, escaping, variable timing, portability, and tab-sensitive syntax
problems. File timestamps are also an imperfect proxy for semantic freshness.

### Nomi Implication

Nomi should treat build/task automation as a declarative dependency graph, not
as ordinary scripts with a convention.

Nomi normal form:

```text
target -> named artifact or task
prerequisite -> dependency edge
recipe -> effectful block requiring host capabilities
freshness -> policy, not necessarily timestamp only
build run -> graph evaluation + event trace
```

This belongs first as a standard-library/task-runner design, not primary
language syntax.

## 5. jq And JSON Filter Languages

### User Need

jq is a command-line language for transforming JSON values and JSON streams.
Its core mental model is "a program is a filter": each filter receives input
and produces output, and filters compose through pipelines.

### What Works

jq succeeds because it brings structure to shell-like workflows:

- `.` is identity over JSON;
- `.field` and `.[]` are tiny selectors;
- `|` composes transformations;
- filters may emit multiple results;
- arrays and objects can be constructed from filtered values;
- streaming modes handle large JSON inputs.

It turns JSON exploration into a REPL-friendly activity.

### What Fails

jq also demonstrates risks:

- shell quoting collides with jq syntax;
- multi-result filters can surprise users expecting one value;
- missing fields, null, and absent paths require careful operators;
- dense filters can become write-only;
- command-line arguments need explicit typed injection.

### Nomi Implication

Nomi should treat structured data transformation as a first-class everyday
case. jq's lesson is not its punctuation; it is the clean identity/filter/pipe
model over values.

Nomi normal form:

```text
filter -> Function from Value to zero, one, or many Values
selector -> projection with absence policy
JSON boundary -> decode into Nomi Value with provenance
multi-result stream -> explicit collection/stream context
```

This connects directly to Nomi's table/flow vocabulary and absence/result
design.

## 6. CSS Selectors

### User Need

CSS selectors are a pattern language over document trees. They let users name
sets of elements by tag, class, id, attribute, relation, pseudo-class, and
structural position.

### What Works

Selectors are successful because they are declarative, compact, and reusable
across styling, querying, testing, scraping, and browser automation. A selector
is not a traversal algorithm; it is a match pattern over a tree.

Combinators expose relationships:

```css
main article > h2
button[disabled]
form:has(input:invalid)
```

The design lesson is that a selector can be a small readable predicate over a
known shape.

### What Fails

CSS selectors also show the cost of hidden environment:

- selector meaning depends on document language and tree construction;
- specificity creates non-local priority behavior;
- pseudo-classes may depend on dynamic state;
- invalid or unsupported selectors can fail differently across tools;
- selectors can be brittle when document structure changes.

### Nomi Implication

Nomi's pattern language should learn from selectors but keep specificity-like
priority out of ordinary data matching. Structural selection belongs as a
library-normal form over trees, records, JSON, XML/HTML, and UI documents.

Nomi normal form:

```text
selector -> Pattern + relation predicates over structured Value
match result -> collection of focused nodes plus path provenance
specificity/priority -> policy outside the core pattern
```

## 7. GraphQL

### User Need

GraphQL gives clients a typed query language for selecting exactly the shape of
data they need from a service graph. It shifts part of API interaction from
"which endpoint do I call?" to "which fields and nested fields do I select?"

### What Works

GraphQL's strongest design ideas are:

- a schema is part of the interface;
- selection sets mirror response shape;
- validation happens before execution;
- variables separate query text from values;
- introspection and descriptions support tools;
- fragments let repeated selection patterns be named.

The response shape being visually related to the request shape is a major
human-factors win.

### What Fails

GraphQL also brings tradeoffs:

- resolver performance can be non-obvious;
- authorization and field visibility are not solved by the query language
  alone;
- nullability is subtle and propagates through result shapes;
- caching is less uniform than resource-oriented HTTP caching;
- schema evolution requires governance and tooling discipline.

### Nomi Implication

GraphQL is evidence for shape-directed external data access. Nomi should not
embed GraphQL as a syntax model, but it should support typed boundaries where a
request shape and response shape are inspectably related.

Nomi normal form:

```text
schema -> boundary contract
selection set -> projection pattern over remote data shape
variables -> typed external inputs
response -> decoded Value + partial failure metadata
introspection -> tool-visible contract query
```

This belongs near data boundaries, API clients, and explainable external calls.

## 8. HTTP And Web API Design

### User Need

HTTP is a uniform interface for interacting with resources through methods,
headers, status codes, representations, and caches. Modern web API design also
adds resource naming conventions, authentication, pagination, rate limits,
idempotency keys, versioning, and machine-readable descriptions.

OpenAPI describes HTTP APIs so humans and tools can discover operations,
parameters, request bodies, responses, security schemes, examples, and schemas.

### What Works

HTTP's durable design strengths:

- resources are identified separately from method semantics;
- method properties such as safety and idempotency guide clients, caches, and
  retries;
- status codes give a shared result vocabulary;
- headers provide extensible metadata;
- representations decouple resource identity from payload format.

OpenAPI's durable design strengths:

- paths and operations make API surfaces inspectable;
- parameters and request bodies are explicit;
- response alternatives can be documented;
- schemas support validation and generated clients;
- examples and security requirements become part of the contract.

### What Fails

Web APIs fail where contracts are vague:

- endpoints drift from documentation;
- status codes are used inconsistently;
- errors are string blobs instead of typed results;
- pagination, filtering, and sorting conventions vary;
- retries can be unsafe without idempotency discipline;
- auth, secrets, and redaction are bolted on too late;
- versioning policy is often implicit.

### Nomi Implication

Nomi should make world-contact explicit. HTTP calls should not be ordinary
function calls with hidden effects; they should carry capability, timeout,
retry, idempotency, serialization, decoding, and redaction policy.

Nomi normal form:

```text
HTTP operation -> Method + Resource + Request contract + Response alternatives
OpenAPI document -> external boundary schema
API call -> effectful host operation returning Result[Decoded, ApiFailure]
status code -> result classifier, not the whole error model
secret/auth -> capability-marked value with redaction
```

Potential Nomi direction:

```nomi
client = Api.from_openapi("openapi.yaml")

user = client.users.get(id)
    |> decode User
    |> expect ok
```

The exact spelling is future work. The required design principle is clear:
API boundaries must be inspectable and capability-honest.

## Cross-Language Synthesis

### Invariants

Across these interface languages, the useful invariants are:

- **Shape before algorithm.** Selectors, GraphQL selection sets, OpenAPI
  schemas, Excel ranges, and Make prerequisites describe structure before
  procedural steps.
- **World boundary is part of meaning.** A command, cell reference, URL,
  selector, or target is meaningful because of the world it addresses.
- **Pipeline/composition is the dominant scaling move.** Shell, PowerShell,
  jq, formulas, and API clients all grow by chaining small transformations.
- **Metadata makes tools powerful.** PowerShell parameters, Excel dependency
  graphs, OpenAPI schemas, GraphQL introspection, Make dependency graphs, and
  CSS specificity all let tools reason beyond raw text.
- **Failure is plural.** Missing files, bad exit status, blocked spill ranges,
  absent JSON paths, selector mismatch, HTTP status codes, auth failure, schema
  validation, timeout, and partial GraphQL data are different failures.
- **Stringly boundaries are the recurring trap.** Shell quoting, SQL/JSON/API
  strings, command construction, path templates, and selector strings all hide
  structure from tools unless parsed and typed.

### Forks

These surfaces make several genuine design forks visible:

| Design fork | Shell-like answer | Structured answer | Nomi pressure |
| --- | --- | --- | --- |
| Pipeline payload | text/bytes | objects/values | Prefer values, provide explicit text adapters. |
| External calls | command strings | command/API objects | Model host effects as values plus capability. |
| Failure | exit code or error cell | typed result alternatives | Separate expected failure from crash/bug. |
| Selection | ad hoc text | structural pattern/query | Use patterns/projections with provenance. |
| Dependency | implicit order | graph | Make dependency graphs inspectable. |
| API contract | docs page | schema/spec | Decode against explicit boundary contracts. |
| User growth | one-liner | named reusable abstraction | Support gradual reification without model switch. |

### Anti-Patterns

Avoid importing these:

- shell-like implicit word splitting;
- string interpolation as the default command/API builder;
- hidden formula/program mixture with no dependency trace;
- specificity-style priority in ordinary pattern matching;
- API errors represented only as strings;
- status codes treated as complete result types;
- task/build freshness based only on unexamined timestamps;
- multi-result streams pretending to be single values;
- schema descriptions that are not validated against runtime behavior.

## Nomi Adopt / Refuse / Adapt

| Source idea | Decision | Nomi reason |
| --- | --- | --- |
| Value-first pipelines | Adopt | Fits Nomi flow and everyday transformation. |
| Unix process composition | Adapt | Useful, but needs typed argv and structured results. |
| Shell expansion stack | Refuse | Too implicit and stringly for local reasoning. |
| PowerShell object pipeline | Adapt | Strong metadata lesson; avoid .NET/object dominance. |
| Excel local formula feedback | Adopt | Great first-hour and notebook pressure. |
| Excel grid as whole language model | Refuse | Too spatial and mutation-prone for Nomi core. |
| Excel `LET`/`LAMBDA` progression | Adopt | Local binding and function reification match Nomi. |
| Make dependency graph | Adapt | Use for task/build library and explainable effects. |
| jq filter identity/pipe model | Adopt | Clean normal form for structured transforms. |
| CSS selector pattern compactness | Adapt | Useful over structured data; avoid hidden priority. |
| GraphQL selection mirrors response | Adopt | Excellent boundary/projection design lesson. |
| GraphQL resolver execution model | Refuse as core | Service-specific performance model belongs outside core. |
| HTTP uniform interface | Adapt | Model as host effect plus contracts and result taxonomy. |
| OpenAPI machine-readable boundary | Adopt | Supports generated clients, tests, diagnostics, explain. |

## Nomi Design Directions

### 1. World-Contact Values

Represent external contact as explicit values before execution:

```text
Command
ApiOperation
FileTarget
Selector
WorkbookRange
JsonFilter
```

These values should expose what they will touch, what capabilities they need,
what result shape they promise, and what failure alternatives are expected.

### 2. Boundary-First Standard Library

Several "language features" can start as libraries:

- `Process.run(...)`;
- `Api.from_openapi(...)`;
- `Json.decode(...)`;
- `Html.select(...)`;
- `Task.target(...)`;
- `Table.from_csv(...)`;
- notebook dependency inspection.

Promote syntax only after the normal forms prove common, teachable, and
inspectable.

### 3. Unified Pipeline Contracts

Pipelines need a shared contract across values, streams, processes, API calls,
and table transforms:

```text
stage accepts -> stage emits -> failure policy -> cardinality policy
```

This lets Nomi explain whether a pipeline is:

- one value to one value;
- one value to many values;
- stream to stream;
- process bytes to structured values;
- effectful API call to decoded value;
- table to table.

### 4. Shape And Provenance

Everyday interface languages repeatedly need paths:

```text
file path
cell address
JSON path
HTML node path
API route path
GraphQL field path
OpenAPI schema pointer
```

Nomi should preserve provenance for decoded and selected values. A diagnostic
should be able to say:

```text
value came from response.body.users[3].email
value failed User.email constraint
request was GET /users/{id}
schema source was openapi.yaml#/components/schemas/User
```

### 5. Failure Taxonomy For Interfaces

The research points to a minimum failure taxonomy:

```text
ParseFailure
DecodeFailure
ValidationFailure
ProcessFailure
HttpFailure
TimeoutFailure
AuthFailure
MissingPath
BlockedOutput
DependencyStale
CapabilityDenied
PartialResult
```

These should not all become core types immediately. But Nomi's result and
diagnostic design should leave room for this plurality.

## Suggested Follow-Up Docs

Stable ideas from this research should eventually be split into focused design
artifacts:

- `../features/process_and_command_boundary_feature.md`
- `../features/api_boundary_and_openapi_feature.md`
- `../features/selectors_and_structural_paths_feature.md`
- `../features/task_dependency_graph_feature.md`
- `../convenience/pipelines_and_streams.md`
- `../convenience/notebook_dependency_feedback.md`

## Bottom Line

The design lesson from these non-mainstream PL surfaces is that computation is
often most successful when it is attached to a concrete interface: a cell, a
file, a process, a document node, a JSON value, a target, a URL, or a schema.

Nomi should become good at those interface boundaries without inheriting their
accidental stringiness. The core direction is:

```text
explicit world boundary
  -> structured value
  -> readable transformation
  -> inspectable dependency/failure trace
  -> gradual reification into named functions, tasks, schemas, and examples
```

