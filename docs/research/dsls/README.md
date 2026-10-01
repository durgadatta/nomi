# DSLs And Strings: Research Dossier

> Status: dedicated research evidence and bounded Nomi hypotheses.
>
> Primary documentation checked on 2026-10-01. This dossier does not accept
> language syntax, promise a DSL engine, or establish host conformance.

## Purpose And Reading Order

The user requested a separate, deep DSL investigation after the
[global project scan](../../orientation/project_roadmap.md), with particular
attention to strings, Kubernetes configuration, GitHub Actions, and systems
that add application interpretation to YAML. This dossier owns those boundaries.
The existing [data/workflow research](../data_workflows/README.md) continues to
own tables, numerical notation, and DW1-DW8; this is not a replacement survey.

1. This taxonomy: what counts as a DSL and which mechanisms must be compared.
2. [Layered configuration](layered_configuration.md): Kubernetes, GitHub
   Actions, Helm, Kustomize, Compose, GitLab, Azure, Ansible and Argo.
3. [Strings and embedding](strings_and_embedding.md): literal preservation,
   interpolation, contextual construction, Unicode, source maps and authority.
4. [Nomi candidates](nomi_candidates.md): competing library and notation
   approaches, semantic laws, representative programs and experiment gates.
5. [Executed probes](experiments.md): ten local observations with reproducible
   [code](probe_boundaries.py) and [captured results](probe_results.json).

The central research inference is that **a DSL boundary is a contract between
representations, semantic owners and execution phases**. Borrowing a keyword
or a delimiter does not supply that contract. The strongest near-term Nomi
pressure is typed construction, explicit validation and inspectable evaluation;
general grammar extensibility has not earned admission.

## Method And Confidence

Each comparison asks: who writes this language, what structure is produced,
who supplies names, when values exist, what can fail, what effects are possible,
and where an error is reported? Examples here are original research fixtures,
not copied application templates or production deployment instructions.

Evidence levels:

| Level | Meaning | Evidence here |
| --- | --- | --- |
| Documented | A primary specification or maintainer document states behavior | Linked beside each external claim |
| Observed | A named implementation produced a captured result | Python/PyYAML/jsonschema/SQLite probes only |
| Inferred | A cross-system design conclusion | Explicitly called inference or Nomi hypothesis |
| Proposed | A competing contract awaiting an experiment | Candidates and E1-E12 below; no accepted API |

Live documentation can change. YAML 1.2.2, JSON Schema 2020-12, XPath 3.1,
CWL 1.2 and Modelica 3.6 references identify editions; unversioned application
documentation describes the material inspected on the check date. A later
integration must pin parser, runner, controller, schema and extension versions.
Reading documentation is not evidence that the associated service was run.

## What Counts As A DSL

An external DSL has its own source/parser; an internal DSL uses a host API.
A structured document can still carry a domain language when fields define
operations, dependencies or policy. Fowler's distinction is useful for these
forms, but it does not determine their safety or expressiveness.
[Internal and external DSLs](https://www.martinfowler.com/books/dsl.html).

Use independent axes rather than one continuum from simple to powerful:

| Axis | Alternatives | Question for Nomi |
| --- | --- | --- |
| Representation | Text, host calls, data objects, visual projections | Can source and semantic structure both be inspected? |
| Semantic model | Values, constraints, queries, plans, rules, transitions | What result does construction actually promise? |
| Evaluation | Eager, lazy, reactive, solver-driven, reconciled | When do errors and effects occur? |
| Staging | Load, expand, check, plan, execute, observe | Which inputs are available at each stage? |
| Authority | Pure, supplied functions, IO handles, external runner | Who grants filesystem, process or network access? |
| Binding | Lexical names, schema fields, row names, node references | Which scope owns an identifier? |
| Extensibility | Functions, schemas, vocabulary, macros, grammar | Can one extension change unrelated source meaning? |
| Portability | Standard, dialect, provider, plugin, host-defined | What identity must travel with an artifact? |
| Persistence | Ephemeral evaluation, saved plan, durable workflow | Can a version upgrade change stored behavior? |

A reusable library can be domain-oriented without requiring a new language.
Conversely, a few YAML keys can define a distributed program whose behavior is
far more complex than its short surface suggests.

## Representative Coverage Map

This is broad family coverage, not a claim to enumerate every DSL. The last
column is a Nomi research question, not a feature recommendation. Detailed
configuration facts belong to the linked configuration chapter, avoiding
parallel per-product essays.

| Family / representative | Semantic object | Main boundary pressure | Primary reference |
| --- | --- | --- | --- |
| Serialization: YAML | Tagged graph / application value | Edition, duplicate keys, scalar decoding, alias policy | [YAML 1.2.2](https://yaml.org/spec/1.2.2/) |
| Structural schema: JSON Schema | Assertions and annotations over instances | Dialect, vocabulary, exact validation guarantee | [2020-12 validation](https://json-schema.org/draft/2020-12/json-schema-validation) |
| API resources: Kubernetes | Versioned desired-state objects | Schema, admission, field ownership, reconciliation | [Controllers](https://kubernetes.io/docs/concepts/architecture/controller/) |
| CI/workflows: GitHub Actions | Jobs, invocation contracts, runtime steps | Dependency edges, context availability, shell source | [Workflow syntax](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax) |
| Template deployment: Helm | Generated resource text | Text stages and template reevaluation | [Chart tips](https://helm.sh/docs/howto/charts_tips_and_tricks/) |
| Structured overlays: Kustomize | Transformed resources | Patch kind, target identity, ordered composition | [Kustomize](https://kubernetes.io/docs/tasks/manage-kubernetes-objects/kustomization/) |
| Local service assembly: Compose | Service model | Interpolation versus container environment | [Interpolation](https://docs.docker.com/reference/compose-file/interpolation/) |
| Pipeline inputs: GitLab CI | Expanded pipeline configuration | Whole-value type preservation | [Inputs](https://docs.gitlab.com/ci/inputs/) |
| Staged pipelines: Azure | Expanded plan and runtime tasks | Compile-time, runtime and macro phases | [Expressions](https://learn.microsoft.com/en-us/azure/devops/pipelines/process/expressions?view=azure-devops) |
| Automation: Ansible | Host-oriented tasks | Conditions versus template expressions | [Conditionals](https://docs.ansible.com/ansible/latest/playbook_guide/playbooks_conditionals.html) |
| Cluster workflows: Argo | Templates, DAGs and steps | Multiple embedded expression dialects | [Variables](https://argo-workflows.readthedocs.io/en/latest/variables/) |
| Constraint configuration: CUE | Unified values and constraints | Conflict evidence rather than silent override | [Unification](https://cuelang.org/docs/tour/basics/unification/) |
| Total typed configuration: Dhall | Normalized typed value | Import authority and practical resource limits | [Safety guarantees](https://docs.dhall-lang.org/discussions/Safety-guarantees.html) |
| Programmable configuration: Jsonnet | Lazy value later manifested | Validation timing and representation costs | [Language reference](https://jsonnet.org/ref/language.html) |
| Amended configuration: Pkl | Modules/objects rendered as data | String indentation and custom delimiters | [Language reference](https://pkl-lang.org/main/latest/language-reference/index.html) |
| Contract configuration: Nickel | Merged values with contracts | Priority, conflict and blame location | [Merging](https://nickel-lang.org/user-manual/merging/), [contracts](https://nickel-lang.org/user-manual/contracts/) |
| Host schema plus expressions: HCL | Bodies, expressions and templates | Parser grammar versus host interpretation | [HCL syntax](https://github.com/hashicorp/hcl/blob/main/hclsyntax/spec.md) |
| Infrastructure templates: Terraform | Configuration-derived output | Encoding structured output rather than stitching text | [templatefile](https://developer.hashicorp.com/terraform/language/functions/templatefile) |
| Package/build configuration: Nix | Expressions and generated text | Interpolation inside shell/configuration strings | [String literals](https://nix.dev/manual/nix/2.34/language/string-literals.html) |
| Embedded configuration language: Starlark | Host-defined configuration values | Core restrictions versus host capabilities | [Specification](https://github.com/bazelbuild/starlark/blob/master/spec.md) |
| Build extensions: Bazel | Target graph then action graph | Analysis distinct from executing commands | [Extension phases](https://bazel.build/extending/concepts) |
| Build recipes: Make | Dependencies and shell recipes | Make expansion versus shell expansion | [Recipe variables](https://www.gnu.org/software/make/manual/html_node/Variables-in-Recipes.html) |
| Image construction: Dockerfile | Image-build instructions | JSON exec form versus shell source | [Reference](https://docs.docker.com/reference/dockerfile/) |
| Relational queries: SQL | Database query with bound values | Value parameters versus identifiers and syntax | [libpq commands](https://www.postgresql.org/docs/17/libpq-exec.html) |
| API queries: GraphQL | Schema-checked operations | Query source versus separately supplied variables | [Queries](https://graphql.org/learn/queries/) |
| Document transforms: jq | Filters producing output streams | Zero, one or many outputs; explicit collection | [Tutorial](https://jqlang.org/tutorial/) |
| Document selection: JSONPath | Nodelist with locations | Missing versus empty result, dialect portability | [RFC 9535](https://www.rfc-editor.org/rfc/rfc9535.html) |
| XML queries: XPath | Typed sequences and context-dependent expressions | Namespace and context ownership | [XPath 3.1](https://www.w3.org/TR/xpath-31/) |
| Embedded policy: CEL | Checked expression evaluated against bindings | Environment identity and repeated evaluation | [CEL overview](https://cel.dev/overview/cel-overview) |
| Policy rules: Rego | Decisions derived from structured data | Undefined versus false and default policy | [Policy language](https://www.openpolicyagent.org/docs/policy-language) |
| Text matching: regular expressions | Compiled pattern and captures | Dialect, literal quoting and match budget | [RE2 syntax](https://github.com/google/re2/blob/main/doc/syntax.txt) |
| Text templates: Jinja | Rendered document | Undefined inputs, escaping and output context | [Template documentation](https://jinja.palletsprojects.com/en/stable/templates/) |
| Embedded construction: JS tagged templates | Literal segments plus argument values | Preserve structure before stringification | [ECMAScript template semantics](https://tc39.es/ecma262/multipage/ecmascript-language-expressions.html#sec-template-literals) |
| Style languages: CSS | Parsed rules interpreted by a renderer | Error recovery does not equal accepted declaration semantics | [CSS Syntax 3](https://www.w3.org/TR/css-syntax-3/) |
| Visual/dataflow specification: Vega | Reactive visualization with expressions | Supplied datum/signal scopes and interaction | [Expression language](https://vega.github.io/vega/docs/expressions/) |
| Scientific workflows: CWL | Typed tool invocation and workflow description | Argument construction and explicit expression requirements | [CommandLineTool 1.2](https://www.commonwl.org/v1.2/CommandLineTool.html) |
| Computational pipelines: Nextflow | Processes and workflow composition | Host-like syntax and separately interpreted scripts | [Scripts](https://docs.seqera.io/nextflow/script) |
| Temporal behavior: statecharts | States, transitions and events | Lifecycle, hierarchy and cancellation | [Statecharts](https://stately.ai/docs/state-machines-and-statecharts) |
| Constraint solving: SMT-LIB | Formula, theory and solver interaction | Model/unknown/error distinct from application execution | [Standard](https://smt-lib.org/language.shtml) |
| Physical modeling: Modelica | Equations and model composition | Equation semantics distinct from assignment | [Equations 3.6](https://specification.modelica.org/maint/3.6/equations.html) |
| Protocol schemas: Protobuf | Message contract and generated bindings | Schema evolution and source/runtime identity | [proto3 guide](https://protobuf.dev/programming-guides/proto3/) |
| Grammar notation: ABNF | Language productions | Recognition without application meaning | [RFC 5234](https://www.rfc-editor.org/info/rfc5234/) |
| Parser generator API: Tree-sitter | Grammar and parser tables | Precedence, conflicts and recoverable source trees | [Grammar DSL](https://tree-sitter.github.io/tree-sitter/creating-parsers/2-the-grammar-dsl.html) |
| Language construction: Racket | Reader and expander layers | Hygiene, lexical scope and source provenance | [Creating languages](https://docs.racket-lang.org/guide/languages.html) |

## Mechanisms Worth Comparing In Depth

HCL explicitly separates structural, expression and template sublanguages;
the embedding application supplies interpretation and evaluation context.
This is a useful model for describing YAML applications without pretending
their keys are part of YAML itself.
[HCL specification](https://github.com/hashicorp/hcl/blob/main/spec.md),
[syntax specification](https://github.com/hashicorp/hcl/blob/main/hclsyntax/spec.md).

CUE's unification combines constraints rather than imposing an arbitrary
last-writer rule. Nickel gives merge priorities explicit meaning and retains
contract blame information. These are different candidates, not two spellings
of a generic deep merge.
[CUE](https://cuelang.org/docs/tour/basics/unification/),
[Nickel merge](https://nickel-lang.org/user-manual/merging/),
[Nickel blame](https://nickel-lang.org/user-manual/contracts/).

Dhall separates total normalization from input resolution; termination does
not imply a useful latency bound. Jsonnet's lazy arrays and objects defer work,
while its strings are strict. A Nomi validated configuration value therefore
needs a stated validation/materialization stage, even if construction is pure.
[Dhall safety](https://docs.dhall-lang.org/discussions/Safety-guarantees.html),
[Jsonnet evaluation](https://jsonnet.org/ref/language.html).

Starlark's core is restricted, but its host supplies additional functions and
values. Bazel distinguishes loading, analysis and execution. **Inference:**
restricted syntax alone does not establish restricted deployment authority;
the allowed host bindings and execution stage need separate contracts.
[Starlark](https://github.com/bazelbuild/starlark/blob/master/spec.md),
[Bazel phases](https://bazel.build/extending/concepts).

CEL compiles/checks against a supplied environment, then evaluates with matching
bindings. Rego has undefined results that are not ordinary false values.
**Inference:** Nomi should expose policy result and environment contracts rather
than treating all policies as arbitrary `Text -> Bool` functions.
[CEL](https://cel.dev/overview/cel-overview),
[Rego](https://www.openpolicyagent.org/docs/policy-language).

Racket syntax objects retain lexical-binding and source-location information.
That makes hygienic transformation a substantially stronger facility than
concatenating strings. The lesson for Nomi is evidence retention; it is not a
recommendation to admit unrestricted macros now.
[Syntax objects](https://docs.racket-lang.org/guide/stx-obj.html).

## Cross-Family Conclusions And Limits

The following are research inferences to test:

- Model configuration, a checked policy, a query plan and an execution result
  as different values. Their failure and authority contracts differ.
- Preserve literal segments and substitution values before rendering. A plain
  string erases boundaries that a domain checker may need.
- Prefer host-independent semantic objects with domain-specific adapters.
  One universal AST or evaluator would force incompatible models together.
- Make dialect/schema/version/context part of an artifact's identity. Equal
  source text does not guarantee equal meaning under different owners.
- Make merge laws explicit. Order-independent constraints, ordered overlays,
  list replacement and field ownership cannot share an unnamed merge operation.
- Keep incomplete source editable while preventing an incomplete draft from
  becoming a checked or executed artifact.
- Evaluate affordances for completion, refactoring, formatting, explanation,
  source maps and redaction alongside syntax—not after admitting it.

Specialized hardware HDLs, music/game DSLs, legal/financial rule systems,
spreadsheet engines, robotics languages and every vendor workflow dialect were
not individually validated. Their main representation/time/solver pressures are
covered by representative families above and the existing
[notation atlas](../notation_atlas.md). A concrete Nomi target deficiency should
trigger a focused extension, not another unbounded catalog.
