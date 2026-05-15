# Data Boundary Systems: Comprehensive Deep Dive

> Status: active research.  Source material for Nomi's data-boundary normal form.
> Companion: [../convenience/data_and_types.md](../convenience/data_and_types.md)
> for the Nomi-side vocabulary; [design_lessons_and_integration.md §4.7](../convenience/design_lessons_and_integration.md)
> for the integration decisions; [language_design_dimensions.md §4.6](../language/language_design_dimensions.md)
> for the boundary-crossing convergence analysis.

## Purpose

Every non-trivial program has a boundary. On one side: external data — JSON from
an API, bytes from a config file, user input from a form, environment variables
from a shell, rows from a database. On the other side: internal program state —
typed structs, validated invariants, trusted values that functions reason about.

Crossing that boundary is where most production bugs live. Incorrect types.
Missing fields. Values that satisfy the wire format but violate business rules.
Constraints that exist in documentation but not in code. Config languages that
duplicate the host language's type system at lower fidelity.

This document surveys ten systems that tackle the data boundary problem from
genuinely different angles. It asks: what worked, what failed, and what does
each system reveal about the structural invariants every data-boundary system
must respect?

Nomi's starting position: **config is a data-boundary problem, not a second data
declaration language.** Constraints, `data` declarations, and `Data.decode(...)`
should handle external data boundaries without introducing a parallel type system
or a separate schema language. This research deepens that decision with
comparative evidence.

---

## 1. Pydantic (Python)

### Core philosophy

Pydantic builds a runtime validation layer on top of Python's type annotation
syntax. A `BaseModel` subclass uses Python type hints as a schema language:
fields declare their types, and Pydantic validates incoming data against those
declarations at construction time. The core insight: **type annotations are
already a schema language — make them executable.**

```python
from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime

class User(BaseModel):
    name: str
    email: str
    age: int = Field(ge=0, le=150)
    joined: datetime
    tags: list[str] = []

    @field_validator("email")
    @classmethod
    def email_must_contain_at(cls, v: str) -> str:
        if "@" not in v:
            raise ValueError("invalid email")
        return v.lower()

# The boundary crossing: external dict → validated model
raw = {"name": "Ada", "email": "Ada@Example.com", "age": 30, "joined": "2024-01-01T00:00:00"}
user = User(**raw)  # Validates eagerly at construction
# user.email == "ada@example.com"  (validator ran)

# Serialization: model → dict / JSON
user.model_dump()              # {"name": "Ada", "email": "ada@example.com", ...}
user.model_dump_json()         # JSON string

# Deserialization: JSON string → model
user2 = User.model_validate_json('{"name":"Bob","email":"bob@test.com","age":25,"joined":"2024-06-01T00:00:00"}')
```

### What worked exceptionally well

1. **Zero-syntax-gap between schema and code.** The schema IS the Python class.
   No separate `.json` schema file, no code generation step, no impedance
   mismatch. When you change the `User` class, the validation changes with it.
   This eliminates the schema-drift problem that plagues JSON Schema and
   protobuf workflows.

2. **Composable validators.** `field_validator`, `model_validator` (v2),
   `BeforeValidator`, `AfterValidator`, `WrapValidator` — the validator
   composition model is rich without requiring a new expression language.
   Validators are ordinary Python functions.

3. **The ecosystem effect.** Because Pydantic models are ordinary Python
   classes, the entire Python ecosystem of type checkers (mypy, pyright),
   IDE autocompletion, and documentation generators (sphinx) works on
   Pydantic models automatically. This is the key advantage of type-first
   data boundary systems: the data boundary vocabulary is the language's
   own vocabulary.

4. **Strict vs. lax modes.** Pydantic v2 introduced a nuanced coercion model.
   `str` fields can accept `int` and convert (lax mode) or reject (`strict`
   mode). This acknowledges that data boundaries are rarely pure: sometimes
   you want "yes, `"42"` should become `42`" and sometimes you want "no,
   this is wrong." Making the boundary policy explicit per-field is the
   right granularity.

### What failed or caused persistent friction

1. **Validation happens at construction, not at the call site.** The
   canonical Pydantic pattern (`User(**raw)`) puts validation inside the
   constructor. But the constructor is called from application code, not
   from the boundary. This means validation can happen deep in a call
   stack, far from where the data entered the system. The boundary
   crossing is not visually distinct from ordinary object construction.

2. **Performance ceiling.** Runtime Python validation of every field on
   every construction is inherently slow. Pydantic v2 rewrote the core
   in Rust (pydantic-core) to address this, but the approach of
   "validate everything at runtime" has a ceiling that compile-time
   approaches (Rust serde, TypeScript) do not.

3. **The `Optional` / `| None` saga.** Python's type annotation churn
   (`Optional[X]` vs `X | None`, `List[X]` vs `list[X]`) means Pydantic
   documentation, tutorials, and codebases use multiple styles. Pydantic
   supports all of them, but the fragmentation is visible to users.

4. **JSON Schema export is lossy.** Pydantic can export a JSON Schema from
   a model, but custom validators (Python functions) do not survive the
   export. The generated schema is a subset of the actual validation.
   This is the fundamental tension: the richer your validation, the less
   portable your schema.

### Key structural insight for Nomi

**The schema should be the program type, not a separate artifact.** Pydantic
proves that when the validation vocabulary is the host language's type
vocabulary, the ecosystem advantages (tooling, type checkers, IDE support) are
massive. Nomi's `data` declarations should carry constraints as first-class
values — not as a separate JSON Schema-like mini-language — so that the same
constraint vocabulary works for internal bindings (`name: positive_int`) and
external decoding (`Data.decode(raw, User.decoder)`).

The second insight: **coercion policy must be per-field and visible.** Pydantic's
lax/strict model acknowledges that data boundaries are heterogeneous. A field
that comes from a config file might accept string-to-int coercion; a field that
comes from a database should not. Nomi's `Data.decode` should accept a policy
parameter that controls coercion at the field level.

---

## 2. CUE

### Core philosophy

CUE (Configure, Unify, Execute) is a language built around a single operation:
**unification.** Types are values, values are types, and the language's job is
to find the most specific value that satisfies all constraints. There is no
distinction between "this is a schema" and "this is an instance" — both are CUE
values, and the CUE runtime unifies them.

```cue
// Schema: what a valid user looks like
#User: {
    name:   string
    email:  =~"^[^@]+@[^@]+$"
    age:    >=0 & <=150
    tags:   [...string]
    joined: string
    // Default value — applied when concrete value is missing
    role:   "member" | *"viewer"
}

// Instance: a concrete user
ada: #User & {
    name:   "Ada"
    email:  "ada@example.com"
    age:    30
    joined: "2024-01-01T00:00:00"
}

// CUE unifies schema + instance. If ada.email were missing,
// CUE would report: "ada.email: incomplete value string"
// If ada.age were 200, CUE would report: "ada.age: conflicting values
// >=0 & <=150 and 200"
```

### What "types are values" means

In most languages, `int` is a type-level construct and `42` is a value-level
construct — they live in different phases (compile time vs runtime). In CUE,
`int` IS a value. It is the set of all integers. `string` is the set of all
strings. `>=0` is the set of numbers greater than or equal to zero. `"hello"`
is the most specific set — the singleton containing only `"hello"`.

Unification (`&`) computes the intersection: `int & >=0 & <=100` = the set of
integers 0..100. This means constraints compose by set intersection without
the user needing to think about "ordering" or "which validator runs first."

Concrete example of the power: a value expression like `>=0 & <=100` is
simultaneously a type ("some number in this range"), a constraint ("this
field must be in this range"), and a partial concrete value (when unified
with more specific data, it constrains the result).

### What worked exceptionally well

1. **Constraints compose without ordering.** Because unification is
   commutative (`A & B = B & A`), there is no "did this validator run
   before that one?" problem. All constraints are simultaneously active.
   This is a fundamental improvement over sequential validator chains
   where ordering can hide bugs.

2. **Defaults via disjunction with preference.** `"member" | *"viewer"`
   means "this field is either `"member"` or `"viewer"`, and if nothing
   chooses, default to `"viewer"`". The `*` marker indicates the preferred
   (default) branch of a disjunction. This is the cleanest default-value
   mechanism in any configuration system: defaults are not a separate
   "if missing then X" rule but a structural property of the value lattice.

3. **Schema is data, data is schema.** A concrete value (like a production
   config) IS a valid schema for validation purposes. You can use last
   week's config as a schema to validate this week's config — any field
   that changed will be flagged. This collapses the schema-definition and
   golden-file-testing workflows into one operation.

4. **Packages and imports are deterministic.** CUE's module system is
   content-addressable and hermetic. `import "example.com/schema:user"`
   resolves to a specific version. This means schemas have reproducible
   validation semantics — unlike JSON Schema where `$ref` resolution is
   implementation-dependent.

### What failed or caused persistent friction

1. **The learning cliff.** "Types are values, values are types, unification
   computes the meet" — this is beautiful if you already understand lattice
   theory, and baffling if you don't. CUE's power comes from a mathematical
   foundation that most programmers do not have. The language trades
   learnability for expressiveness.

2. **No computation in the language.** CUE is not Turing-complete and
   deliberately lacks general-purpose computation. You cannot write a
   function that transforms data in CUE. This means CUE is purely a
   validation/configuration language — you still need a separate language
   (Go, Python, etc.) to do anything with the validated data. This is a
   deliberate design choice but creates a two-language workflow.

3. **Error messages can be opaque.** When unification fails, CUE reports
   "conflicting values" with the two terms that could not be unified. But
   in deeply nested structures with transitive imports, the conflict may
   appear far from its source. Understanding WHY two values conflict often
   requires tracing the unification graph manually.

4. **Limited adoption.** CUE remains niche. The learning curve, the lack of
   computation, and the two-language workflow have limited its growth.
   Jsonnet (which is less ambitious but more approachable) has wider
   adoption in the Kubernetes ecosystem.

### Key structural insight for Nomi

**Constraint composition must be order-independent.** The single most
important structural insight from CUE: when a field has constraint A and
constraint B, the result should not depend on whether A was checked before
B. Nomi's constraint vocabulary should be commutative: binding `name:(>0 & <100)
= value` should be equivalent to checking both range constraints simultaneously.

The secondary insight: **defaults belong in the value, not in a separate
mechanism.** Nomi's `data` declarations should support "zero value" defaults
that are part of the type definition, not a separate `.with_defaults()` method
or config-file-level default map.

The caution: **CUE is too powerful for the first Nomi layer.** Unification as
a general constraint-solving mechanism brings a constraint-solver runtime.
Nomi should start with explicit decoding (data-from-schema) and treat
schema-from-data (unification direction) as a future tool, not a language
feature.

---

## 3. Nickel

### Core philosophy

Nickel is a configuration language designed around **contracts** — runtime
assertions that attach to values and check properties at the boundary between
modules. Nickel's contract system is gradual: you can start with untyped
configuration and progressively add contracts as you discover the invariants
that matter.

```nickel
# A contract that checks a value at the boundary
let User = {
  name | String,
  email | String,
  age | Num,
} in

# A contract is the schema
let ValidUser = contract {
  name | String,
  age | Num,
  email
    | String
    | doc "Must be a valid email address",
} in

# Apply the contract to a value
let user = { name = "Ada", email = "ada@example.com", age = 30 } | ValidUser in

# Merging: two records combined, with contracts enforced
let defaults = { role = "viewer", active = true } in
let overrides = { name = "Ada", role = "admin" } in
let merged = defaults & overrides  # & is merge, with override semantics
# merged.role == "admin" (overrides wins)
# merged.active == true (from defaults)
```

### How Nickel's contracts differ from CUE's unification

| Aspect | CUE unification | Nickel contracts |
|--------|----------------|------------------|
| Order dependence | Commutative (`A & B = B & A`) | Contracts checked at annotation site |
| Partial values | Values can be incomplete | Records are complete at each step |
| Merge semantics | Set intersection (meet) | Recursive override (last-wins for scalars) |
| Defaults | Disjunction preference (`*`) | Merge ordering |
| Computational model | Constraint solving | Eager evaluation with contract checks |
| Gradual typing | Not gradual (all values typed) | Gradual (add contracts progressively) |

The fundamental difference: CUE asks "what is the most specific value that
satisfies all constraints?" Nickel asks "what is the result of merging these
values, and does it satisfy the contracts I've declared?" CUE is
constraint-first; Nickel is merge-first with assertion checking.

### What worked exceptionally well

1. **Gradual typing is the right posture for configuration.** You can write
   `let port = 8080` with no contract, then later add `let port | Port =
   8080` when you realize ports need validation. The annotation site is
   where the contract lives — not at the type definition, not at the call
   site, but at the binding. This is the same posture Nomi takes with
   `name:constraint = value`.

2. **Merge is the central operation.** In configuration, you are almost
   always combining sources: defaults + environment + user overrides +
   computed values. Nickel's `&` operator makes this the primary mental
   model. The override semantics (scalars: last wins; records: recursive
   merge; lists: append) handle the common cases without ceremony.

3. **Contracts are user-definable.** A Nickel contract is just a function
   from a value to a value (or an error). This means contracts compose
   like functions. Unlike JSON Schema where adding a custom validator
   requires an extension mechanism, Nickel contracts are ordinary code.

4. **Metavalues — documentation and metadata on fields.** Nickel supports
   `| doc "..."` and `| default = ...` annotations that travel with the
   contract. These are not comments — they are structured metadata that
   tooling can consume. Nomi's `examples:` and `check:` blocks serve a
   similar role for binding and explanation.

### What failed or caused persistent friction

1. **Merge semantics have edge cases.** Nickel's merge is not commutative:
   `A & B` can differ from `B & A` when both define the same scalar field.
   The "last wins" rule is intuitive for simple cases but produces
   surprising results in deeply nested merges with contracts on
   intermediate nodes.

2. **Contract checking is positional, not global.** A contract is checked
   at the point where it is applied (the `|` operator). If a downstream
   module uses a value in a way that violates a contract declared upstream,
   the error is reported at the upstream annotation site — which may be
   confusing. CUE's approach (unification is global) avoids this but at
   the cost of requiring a solver.

3. **Performance of deep contract checking.** Recursive contracts on large
   records with nested structures can be slow. Nickel addresses this with
   lazy contract checking (check only when a field is accessed), but lazy
   checking means errors surface far from the boundary crossing — the
   opposite of what you want in a data boundary system.

4. **Small ecosystem.** Nickel is a research project with production
   aspirations. The ecosystem of reusable contracts, tooling, and
   integrations is small compared to JSON Schema or Pydantic.

### Key structural insight for Nomi

**The `name:constraint = value` pattern is the right annotation site.**
Nickel's `let x | Contract = value` and Nomi's `name:constraint = value`
converge on the same design: the binding is where the constraint lives.
This is correct because the binding is where external data becomes internal
state. The constraint is part of the boundary crossing, not a property of
the type (CUE) or a separate schema document (JSON Schema).

The secondary insight: **merge must have policy.** Nickel's merge is
"scalars last-wins, records recursive, lists append." Real-world
configuration needs different merge policies for different fields: some
should override, some should concatenate, some should reject duplicates.
Nomi's merge vocabulary should support named merge policies rather than
a single universal merge rule.

---

## 4. Pkl (Apple)

### Core philosophy

Pkl (Pickle, pronounced "pickle") is a configuration-as-code language from
Apple. Its central idea: configuration files should be programmable enough
to eliminate repetition, but not so programmable that they become
unpredictable. Pkl has classes, methods, expressions, conditionals, and
loops — but it is evaluated to produce static configuration output (JSON,
YAML, XML, PropertyList, etc.), not to run as a service.

```pkl
// Define a configuration template
class Application {
  name: String
  port: UInt16(this > 1024)
  host: String = "localhost"
  debug: Boolean = false

  // Computed property
  url: String = "http://\(host):\(port)"
}

// Amend: extend a template with overrides
amends "package://example.com/BaseConfig@1.0"

// Use it
myapp = new Application {
  name = "my-service"
  port = 8080
  // host and debug defaulted
}

// Output as JSON
// pkl eval -f json config.pkl
```

### The template/amends model

Pkl's `amends` keyword is the most original design element. It means "this
file extends and overrides a base template, and must produce valid output
of the base template's type." An `amends` file is type-checked against the
template it amends, so missing required fields or type mismatches are caught
before runtime.

This is different from both CUE (unification of partial values) and Nickel
(merge with contracts). In Pkl, the template IS the schema, and `amends`
creates an instance that must conform. The direction is schema-to-data,
not data-to-schema.

```pkl
// base.pkl
class Service {
  name: String
  port: UInt16
  replicas: UInt(default = 1)
}

// production.pkl — amends the template
amends "base.pkl"

name = "api"
port = 443
replicas = 3  // overrides default
// If port were missing, evaluation fails: "required property 'port' is missing"
```

### What worked exceptionally well

1. **Type-safe configuration with code reuse.** Pkl is the only system in
   this survey that combines a full type system (classes, inheritance,
   generics, type aliases) with configuration output. You can write
   `class Database { host: String; port: UInt16 }` and use it to generate
   JSON, YAML, and environment variables from the same template. This is
   the "one source of truth for configuration shape" that infrastructure
   teams dream about.

2. **Amends creates a provable conformance chain.** Because `amends`
   requires the base template's type, the relationship between a
   production config and its template is statically verifiable. You
   cannot accidentally drift from the template. This is stronger than
   JSON Schema's `$ref` (which can break silently) and stronger than
   Pydantic's model inheritance (which is Python-side only).

3. **The evaluator is deterministic and sandboxed.** No file system access.
   No network access (beyond `import`). No side effects. The same input
   always produces the same output. This is the "not Turing-complete"
   property that Dhall also provides but Pkl delivers with a more
   familiar syntax (curly braces, dots, equals).

4. **Multi-format output without multi-format input.** Write one `.pkl`
   file, output JSON, YAML, XML, or Java properties. The output format is
   a rendering concern, not a schema concern. This means the config file
   is canonical; the output is derived. Schema drift between formats
   cannot happen because there is only one schema (the `.pkl` file).

### What failed or caused persistent friction

1. **Template versioning is still a human problem.** `amends
   "package://example.com/BaseConfig@1.0"` pins to a version. But
   migrating from `@1.0` to `@2.0` requires updating every file that
   amends the template. Pkl provides tooling but cannot automate the
   "this field was renamed, this field was removed" semantic migration.

2. **The language is larger than it looks.** Pkl has classes, methods,
   type aliases, generics, modules, amends, imports, globs, string
   interpolation, conditionals, and loops. It is a full language — just
   not Turing-complete. The learning curve for configuration authors
   (who may not be programmers) is steeper than YAML or JSON with a
   schema.

3. **Closed ecosystem (Apple).** Pkl was open-sourced in 2024 but is
   primarily developed and used at Apple. The community of reusable
   templates, tooling integrations (IDE support beyond IntelliJ), and
   third-party libraries is nascent.

4. **The "configuration as code" boundary question.** Pkl lets you write
   `if (env == "production") port = 443 else port = 3000`. This is
   powerful, but it also means the configuration file contains logic
   that previously lived in deployment scripts. Where does the config
   end and the program begin? Pkl does not answer this — it provides
   a substrate and leaves the boundary to the user.

### Key structural insight for Nomi

**The template/amends conformance chain is the right pattern for layered
configuration.** When a production config amends a template, the type
checker verifies conformance. This is a stronger guarantee than any
runtime-only validation system can provide. Nomi's `Data.decode` should
support a "decode against" pattern: `Data.decode(raw, against=BaseConfig.decoder)`
where the decoder verifies that the raw data conforms to the base type
AND that overrides do not introduce invalid fields.

The caution: **Pkl is a separate language for configuration.** This is
exactly what Nomi's "config is a data-boundary problem" position argues
against. Pkl's value for Nomi is in its structural ideas (template/amends
conformance, deterministic evaluation, multi-format output), not in its
existence as a standalone config language.

---

## 5. Dhall

### Core philosophy

Dhall is a programmable configuration language that is **deliberately not
Turing-complete.** Every Dhall program is guaranteed to terminate. Every
Dhall expression has a normal form. You cannot write an infinite loop in
Dhall.

This is not a performance decision. It is a trust decision. When you
evaluate a Dhall configuration, you know it will produce a result without
side effects, without consuming unbounded resources, and without leaking
information. You can evaluate untrusted Dhall from a third party safely.

```dhall
-- A type for user configuration
let User : Type = { name : Text, age : Natural, email : Text }

-- A function that produces a validated user
let makeUser =
      \(name : Text) ->
      \(age : Natural) ->
      \(email : Text) ->
      -- The type annotation is the validation
        { name = name, age = age, email = email } : User

-- Use it
let ada = makeUser "Ada" 30 "ada@example.com"

-- Normal form: the fully-evaluated, type-checked value
-- { name = "Ada", age = 30, email = "ada@example.com" }

-- Import: resolve a remote Dhall expression with integrity check
let schema = https://example.com/schemas/user.dhall
  sha256:d3b07384d113edec49eaa6238ad5ff00
in schema.User
```

### What not being Turing-complete means in practice

Dhall forbids general recursion. You cannot write:

```dhall
let factorial = \(n : Natural) -> if Natural/isZero n then 1 else n * factorial (Natural/subtract 1 n)
-- ERROR: factorial is not defined in its own body
```

You CAN use `Natural/fold` for bounded iteration (like iterating over a list
of known length), but not for unbounded loops. The termination guarantee is
structural: every recursive construct in Dhall has a decreasing argument that
must eventually reach a base case.

This is the same guarantee as the simply-typed lambda calculus (no Y
combinator) plus built-in folds over finite structures.

### The import system and integrity checking

Dhall's import system is the most sophisticated in any configuration language:

1. **Content-addressed integrity.** `sha256:...` freezes an import to a
   specific version. If the upstream content changes, the hash check fails
   and evaluation stops. This prevents supply-chain attacks on configuration.

2. **Semantic integrity.** `? interpreted as` for importing values with
   specified types. The imported expression must have the declared type,
   checked at import time.

3. **Environment variable imports.** `env:HOME` imports the value of the
   `HOME` environment variable as a Dhall `Text`. This makes Dhall
   configurations aware of their deployment environment without making
   the environment variables part of the Dhall source.

4. **Caching with revalidation.** Imports are cached locally. The cache
   can be refreshed with a freshness period. This balances reproducibility
   (pinned hashes) with auto-updating (loose imports).

### What worked exceptionally well

1. **Safety as a language property, not a sandbox.** Because Dhall is not
   Turing-complete, the safety guarantee is mathematical, not
   implementation-dependent. You don't need to trust the sandbox
   implementation — the language itself cannot express infinite loops or
   side effects. This is fundamentally stronger than running an untrusted
   Python script in a container.

2. **The import system solves the real configuration problem.** Most
   configuration in large systems is not written from scratch — it
   references shared schemas, base configs, and organization-wide
   defaults. Dhall's import system (with integrity hashes) makes this
   safe and reproducible. You can import a schema from a URL, freeze it
   with a hash, and never worry about upstream changes breaking your
   config.

3. **Normalization as a debugging tool.** Because every Dhall expression
   normalizes, you can ask "what is the fully-evaluated JSON equivalent
   of this configuration?" at any point. There is no hidden state, no
   unexpanded macro, no unresolved import. The normal form IS the truth.

4. **Language bindings produce language-native values.** Dhall-to-JSON,
   Dhall-to-YAML, Dhall-to-Python, Dhall-to-Rust — because the normal
   form is a pure data value, binding to any host language is
   straightforward. The Dhall program evaluates to a value, and the host
   language deserializes that value.

### What failed or caused persistent friction

1. **No general computation is genuinely limiting.** You cannot write a
   `map` function that transforms a list of users into a list of names
   unless you use the built-in list operations. This is intentional, but
   it means Dhall cannot replace a general-purpose language for
   configuration that requires computation (e.g., "read all files in
   this directory, parse them, merge the results").

2. **The type system is verbose.** Dhall's syntax for type annotations on
   every lambda parameter, every `let` binding, and every record field
   makes even moderately complex configurations visually dense. The verbosity
   argument that Go makes about code applies doubly to configuration:
   **configuration is read far more than it is written**, and verbosity
   hurts readability.

3. **JSON-like output is the ceiling.** Dhall evaluates to a normal form
   that is essentially a JSON-like value (records, lists, text, numbers,
   booleans, null). This is fine for static configuration but cannot
   express functions, lazy values, or computed properties that survive
   into the output. If your target system needs "a function that computes
   the port based on the instance index," Dhall cannot express that in
   the output.

4. **Adoption ceiling.** Dhall is used in some Haskell and Nix-adjacent
   communities but has not crossed into mainstream use. The combination
   of a niche syntax (Haskell-like), a non-standard evaluation model,
   and limited computation has kept it from replacing YAML/JSON for most
   teams.

### Key structural insight for Nomi

**Not-Turing-complete is the right property for configuration that is
shared, imported, or executed on CI.** Nomi's first layer does not need
to be non-Turing-complete (it is a general-purpose language), but Nomi's
*data boundary vocabulary* should be evaluable without full language
execution. This means: a `data` declaration with constraints and defaults
should be resolvable to a normal form by a tool that understands `data`,
constraints, and merge — without needing to execute arbitrary Nomi code.

The integrity-checking insight: **Data.decode should support content
addressing.** If Nomi's `import` system supports a hash-pinning mechanism
(like `import "schema.nomi" sha256:...`), then data boundary schemas can
be shared across teams without supply-chain risk.

---

## 6. Terraform / HCL (HashiCorp Configuration Language)

### Core philosophy

HCL is a configuration language designed for machine-writable, human-readable
infrastructure configuration. Its core insight: **configuration files have
two audiences — humans (who author, review, and debug them) and machines
(who parse, validate, and execute them) — and optimization for one audience
should not cripple the other.**

```hcl
# HCL: Terraform configuration
variable "environment" {
  type        = string
  description = "Deployment environment"
  default     = "staging"

  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Environment must be dev, staging, or prod."
  }
}

resource "aws_instance" "web" {
  ami           = "ami-0c55b159cbfafe1f0"
  instance_type = var.environment == "prod" ? "t3.large" : "t3.micro"

  tags = {
    Name        = "web-${var.environment}"
    Environment = var.environment
  }
}

output "instance_ip" {
  value       = aws_instance.web.public_ip
  description = "The public IP of the web instance"
}
```

### How HCL balances readability with machine-processability

HCL's design makes three deliberate tradeoffs:

1. **Block structure, not expression-everything.** HCL uses blocks
   (`resource "aws_instance" "web" { ... }`) rather than nested
   function calls. A block visually groups related settings; a
   function call would obscure them. But blocks are also parseable
   into a clean AST — the `type label name { body }` pattern is
   unambiguous to both humans and machines.

2. **String interpolation is template-style, not concatenation.**
   `"web-${var.environment}"` reads like a sentence. The `${}` marker
   makes interpolation visually distinct from literal text. This is
   superior to both YAML's implicit string handling and JSON's lack
   of interpolation.

3. **Variables are declared, not inferred.** `variable "x" { type = ... }`
   forces explicit declaration of inputs. This is the opposite of Python's
   "everything in scope is accessible." HCL's approach means you can look
   at a module's variable block and see exactly what it needs — a property
   called "input discoverability" that is critical for shared configuration.

### Lessons from Terraform's state management for data boundaries

Terraform's state file is a data-boundary system hiding in plain sight. It
stores the mapping between configuration resources and real-world
infrastructure. Key lessons:

1. **State is a cache, not a source of truth.** Terraform can always
   reconstruct state from the real world (by calling cloud APIs). The
   state file is an optimization, not the authority. This principle
   generalizes: any boundary cache (compiled schemas, validated configs,
   serialized models) must be reconstructible from the canonical source.

2. **Drift detection.** `terraform plan` detects when real-world state
   has diverged from the configuration. This is the data-boundary principle
   in infrastructure clothing: the boundary between configuration (intent)
   and reality (state) must be continuously verifiable. For Nomi: a
   `Data.verify` operation that checks whether an already-decoded value
   still satisfies its constraints as schemas evolve.

3. **State locking.** Only one process can modify state at a time. This
   is a data-boundary problem: when multiple writers can cross the boundary,
   you need isolation. Nomi's data boundary should be pure (no side effects),
   but applications built on Nomi that maintain boundary caches need this.

4. **Resource lifecycle.** `create`, `update`, `delete`, `replace` — the
   lifecycle of a boundary-crossing value mirrors Terraform's resource
   lifecycle. A value is decoded (create), re-validated (update), or
   discarded (delete). The lifecycle should be explicit, not implicit.

### What worked exceptionally well

1. **Input → plan → apply is the canonical three-phase boundary crossing.**
   Input (define what you want) → plan (show what will happen) → apply
   (execute). Terraform made this three-phase model ubiquitous. For data
   boundaries: decode (define the expected shape) → validate (show what
   validates and what fails) → construct (produce internal values).

2. **Module ecosystem with version constraints.** The Terraform Registry
   hosts thousands of reusable modules, each with version constraints.
   `source = "terraform-aws-modules/vpc/aws"` plus `version = "~> 5.0"`
   is the pattern for schema reuse. This is what Pydantic, CUE, and Nickel
   all lack: a shared registry of reusable schemas with versioning.

3. **Validation blocks are explicit and separate from type constraints.**
   `validation { condition = ...; error_message = "..." }` is a better
   pattern than Pydantic's `@field_validator` decorator because the
   validation intent is explicit in the configuration, not hidden in
   Python function bodies. The error message is part of the validation
   definition, not a separate concern.

### What failed or caused persistent friction

1. **HCL is its own language with its own semantics.** Terraform's `for`
   expressions, `for_each` meta-arguments, `dynamic` blocks, and `count`
   are not standard programming-language constructs. They are HCL-specific
   idioms that must be learned separately. This is the second-mini-language
   trap: HCL started as a simple configuration language and grew its own
   computation model.

2. **State file corruption.** Terraform's state file is a JSON blob that
   can become corrupted, desynchronized, or too large to manage. The
   absence of a schema for the state file itself (it is a free-form JSON
   blob per provider) means state corruption is a runtime problem, not a
   type problem.

3. **Module versioning is a coordination problem.** When module A requires
   provider version `>= 4.0` and module B requires `>= 5.0`, resolution
   can fail in ways that are hard to debug. This is the same problem as
   Python dependency resolution, CUE module resolution, and Nix channel
   conflicts — schema versioning is a social problem that tooling can
   help but cannot solve.

### Key structural insight for Nomi

**The three-phase boundary crossing is a design pattern, not just a
Terraform thing.** Nomi's `Data.decode(source, Decoder)` should return
not a value but a result that carries intermediate state:

```
decode_result = Data.decode(raw, User.decoder)
# decode_result.valid   — bool
# decode_result.value   — Optional[User]
# decode_result.errors  — list of validation errors
# decode_result.warnings — list of coercion/conversion notes
```

This lets the caller inspect what WILL happen before committing to the
decoded value. The three phases: (1) parse the raw source, (2) validate
against constraints, (3) construct the internal value. Errors accumulated
in phase 2 should be inspectable before phase 3.

The caution: **HCL's evolution into a second mini-language is a warning.**
Configuration languages that add loops, conditionals, and functions
eventually become general-purpose. Nomi should keep its data boundary
vocabulary declarative (constraints, defaults, merge policies) and leave
computation to the host language.

---

## 7. JSON Schema

### Core philosophy

JSON Schema is the maximally declarative approach: the schema is a JSON
document that describes what a valid JSON document looks like. No code
executes during validation. The validator is an interpreter that walks the
schema and the instance in parallel, checking constraints.

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://example.com/user.schema.json",
  "title": "User",
  "type": "object",
  "properties": {
    "name": { "type": "string", "minLength": 1 },
    "email": { "type": "string", "format": "email" },
    "age": { "type": "integer", "minimum": 0, "maximum": 150 },
    "tags": {
      "type": "array",
      "items": { "type": "string" },
      "uniqueItems": true
    },
    "role": { "enum": ["admin", "viewer", "editor"] }
  },
  "required": ["name", "email", "age"],
  "additionalProperties": false
}
```

### How JSON Schema handles composition

JSON Schema's composition keywords are the most interesting part of its
design:

1. **`allOf`** — the instance must validate against ALL of the subschemas.
   This is schema intersection. Used for mixin-style composition: `{"allOf":
   [{"$ref": "address.json"}, {"properties": {"type": {"const": "home"}}}]}`.

2. **`anyOf`** — the instance must validate against AT LEAST ONE subschema.
   This is schema union. Used for variant types: a field that can be a
   string OR a number.

3. **`oneOf`** — the instance must validate against EXACTLY ONE subschema.
   This is exclusive choice. Used for discriminated unions: a response
   that is either a Success OR an Error, not both.

4. **`not`** — the instance must NOT validate against the subschema. Schema
   negation. Rarely used because it creates confusing error messages.

These compose arbitrarily: `{"allOf": [A, {"anyOf": [B, C]}], "not": D}`.
But the composition is structural, not computational — the validator
checks each subschema independently and combines results.

### Lessons from JSON Schema's evolution for Nomi's data vocabulary

1. **Draft proliferation hurts.** JSON Schema has had 10+ drafts (draft-04
   through 2020-12). Each draft changes keyword behavior. Validators
   implement different drafts with different levels of support. Schema
   authors tag their schemas with `$schema` to declare which draft they
   use. This is the same versioning problem as Python 2/3, but worse
   because it is per-schema rather than per-program.

2. **`additionalProperties: false` is the most important keyword nobody
   uses.** By default, JSON Schema allows arbitrary extra properties on
   objects. This means a typo in a property name passes validation silently.
   The `additionalProperties: false` keyword closes the object, but it
   must be set explicitly on every object schema. Most schemas omit it.
   The lesson: **closed-by-default is safer than open-by-default for
   data boundaries.** Nomi's `data` declarations should be closed
   (no extra fields allowed) unless explicitly opened.

3. **Format is a graveyard of good intentions.** `"format": "email"`,
   `"format": "uri"`, `"format": "date-time"` — these are optional
   validations that many validators implement inconsistently. Some
   validators check format by default; some require a flag. Some
   formats (like `"hostname"`) have RFC definitions that don't match
   real-world usage. The lesson: **timeless validation rules (type,
   range, required) should be built-in; culture-dependent rules
   (format, regex) should be library functions.**

4. **`$ref` is a distributed system with all the hard problems.**
   JSON Schema's `$ref` resolves to a URI, which can be local (within
   the same document), file-relative (same file system), or remote
   (HTTP URL). Each resolver handles these differently. Caching,
   circular references, and versioning are all underspecified. The
   lesson: **references across schema boundaries must have explicit
   resolution semantics with integrity guarantees** (Dhall's hash-pinned
   imports are the right model).

### What worked exceptionally well

1. **Language-independent by design.** A JSON Schema can be used by a
   Python validator, a JavaScript validator, a Java validator, and a
   Rust validator — all from the same schema file. This is genuinely
   valuable in polyglot architectures and is something no type-first
   approach (Pydantic, serde) can provide.

2. **Composition keywords are the right primitive set.** `allOf`, `anyOf`,
   `oneOf`, `not` — with just these four, you can express any boolean
   combination of schemas. The primitives are mathematically well-founded
   (they form a boolean algebra over the set of valid JSON values).

3. **Annotations travel with the data.** `"title"`, `"description"`,
   `"examples"`, `"default"`, `"deprecated"`, `"readOnly"`,
   `"writeOnly"` — these are not validation keywords. They are metadata
   that survives validation. Tooling (form generators, documentation
   generators, API explorers) consumes them. Nomi should have a separate
   concern for metadata on data declarations: constraint metadata
   (checked by the runtime) vs documentation metadata (consumed by
   tooling).

### What failed or caused persistent friction

1. **The schema is not the program.** JSON Schema defines the shape of
   data but not the behavior. You still need a second language to DO
   something with validated data. This is the core frustration of
   schema-first approaches: they double the number of artifacts without
   doubling the expressiveness.

2. **No way to express dependent constraints.** "If `type` is `"email"`,
   then `address` must match an email regex. If `type` is `"postal"`,
   then `address` must have a `zip` field." JSON Schema's `if`/`then`/`else`
   keywords (added in draft-07) can express this, but the syntax is
   verbose and few validators support it well. The lesson: **constraint
   logic that depends on other field values must be expressible within
   the constraint vocabulary.** Nomi should not need a separate "business
   rules" layer.

3. **Error output is an afterthought.** The JSON Schema specification
   does not mandate an error format. Each validator produces different
   error structures. Some aggregate all errors; some stop at the first.
   Some include the schema path; some the instance path. Lesson: **the
   error format is part of the data boundary contract.** Nomi's
   `Data.decode` should return a structured error type, not ad-hoc
   messages.

---

## 8. TypeScript: Type Narrowing at Boundaries

### Core philosophy

TypeScript's approach to data boundaries is fundamentally different from
every other system in this survey. TypeScript does not validate data at
runtime. It uses static type checking to ensure that the program treats
external data with appropriate caution. The pattern: `unknown` at the
boundary, narrowed to a known type through runtime checks.

```typescript
// Data enters the system as `unknown`
const raw: unknown = JSON.parse(apiResponse);

// Type guard: narrow from unknown → User
function isUser(value: unknown): value is User {
  return (
    typeof value === "object" &&
    value !== null &&
    "name" in value &&
    "email" in value &&
    typeof (value as any).name === "string" &&
    typeof (value as any).email === "string"
  );
}

if (isUser(raw)) {
  // TypeScript knows raw is User here
  console.log(raw.name.toUpperCase());
}

// With zod: schema library that bridges runtime and type level
import { z } from "zod";

const UserSchema = z.object({
  name: z.string().min(1),
  email: z.string().email(),
  age: z.number().int().min(0).max(150),
});

type User = z.infer<typeof UserSchema>;  // Extract the TypeScript type

// Parse at the boundary
const user = UserSchema.parse(JSON.parse(apiResponse));
// user is typed as { name: string; email: string; age: number }
```

### The `unknown → validated type` pattern

The `unknown` type is the key. It means "this value could be anything; you
must check it before you can use it for anything specific." TypeScript
enforces this at compile time: you cannot access `.name` on an `unknown`
value. You must first narrow it through a type guard, an assertion, or a
validation library.

This is the "parse, don't validate" pattern (Alexis King, 2019): the
validation step should PRODUCE a typed value, not just return a boolean.
`zod`'s `.parse()` returns a value of the inferred type; `.safeParse()`
returns a discriminated union (`{ success: true; data: T } | { success:
false; error: ZodError }`).

### How zod / yup / io-ts work with TypeScript's type system

| Library | Approach | Type extraction | Runtime cost |
|---------|----------|----------------|-------------|
| **zod** | Schema builder → runtime validation + static type | `z.infer<typeof schema>` | Validation runs at call site |
| **yup** | Similar to zod, older, less TS integration | `InferType<typeof schema>` | Validation runs at call site |
| **io-ts** | Codec-based (encoder + decoder), functional | `t.TypeOf<typeof codec>` | Validation runs at call site |
| **typebox** | JSON Schema generation + static type from schema | `Static<typeof schema>` | Compile-time type + runtime JSON Schema |

All four share the same architecture: (1) define a schema as a value, (2)
use TypeScript's type inference to extract the static type from the schema
value, (3) at the boundary, call `.parse()` or `.decode()` to get a typed
value or an error. The schema IS the source of truth for both runtime
validation and the static type — there is no duplication.

### What worked exceptionally well

1. **The type system enforces boundary checking.** If a function takes
   `User`, you cannot pass `unknown` to it. The type checker forces
   you to validate at the boundary. This is the compile-time equivalent
   of "your API surface should accept validated types, not raw data."
   The compiler is your boundary enforcer.

2. **`z.infer` eliminates the type/schema duality.** The schema definition
   IS the type definition. There is no separate `.d.ts` file, no code
   generation, no schema synchronization problem. When you add a field
   to the schema, the TypeScript type updates automatically. This is the
   same advantage as Pydantic but with compile-time enforcement.

3. **Discriminated unions for error handling.** `zod`'s `.safeParse()`
   returns `{ success: true; data: T } | { success: false; error: ZodError }`.
   TypeScript narrows this union based on `if (result.success)`. The
   happy path and error path are both typed — you cannot forget to
   handle the error case.

4. **Zod errors are structured and traversable.** `ZodError` contains a
   tree of issues, each with a path, a code, and a message. This is the
   error format that JSON Schema should have mandated. Tooling can
   render it as a tree, filter by severity, or localize messages.

### What failed or caused persistent friction

1. **No validation means no validation.** TypeScript's compile-time
   enforcement evaporates at runtime. `JSON.parse()` returns `any` by
   default, and TypeScript will let you treat it as any type without
   complaint. The compiler does not enforce the `unknown → validated`
   pattern — it is a convention that teams must adopt. `strict: true`
   and lint rules help, but the language does not require boundary
   checking.

2. **Schema libraries are all runtime overhead.** Every `.parse()` call
   executes validation logic at runtime. In hot paths (processing many
   API responses), this adds measurable overhead. Rust's serde and
   Haskell's aeson avoid this by generating optimized deserialization
   code at compile time.

3. **The type/schema gap still exists at the edges.** `z.enum(["admin",
   "viewer"])` produces `z.ZodEnum<["admin", "viewer"]>`. The inferred
   type is `"admin" | "viewer"`. But if you need to use this type in
   another schema, you need to extract it: `type Role = z.infer<typeof
   RoleSchema>`. This is ergonomic but still a two-step process
   (schema → type) rather than a single declaration.

4. **io-ts vs zod vs yup fragmentation.** The TypeScript ecosystem has
   not converged on a single validation library. zod is the current
   leader, but yup and io-ts have significant usage. Each has different
   APIs and different levels of TypeScript integration. This is the
   standard-library split problem in miniature.

### Key structural insight for Nomi

**The `unknown → validated type` pattern is the canonical boundary
crossing.** Nomi's `Data.decode(raw, Decoder)` should return a Result type,
not a value-or-exception. The caller should be forced (by type or by
convention) to handle both the success and failure cases.

The TypeScript/zod convergence also validates Nomi's "no separate schema
language" position. The schema IS the type definition. Type extraction
(`z.infer`) proves that you can have one source of truth that produces
both compile-time types (for program correctness) and runtime validation
(for data safety) without duplication.

---

## 9. Rust serde

### Core philosophy

Serde (SERialization/DEserialization) is the Rust ecosystem's answer to
data boundaries. Its core insight: **the serialize/deserialize operation is
a trait implementation, not a separate schema language.** Any Rust type can
implement `Serialize` and `Deserialize`, and serde provides a `#[derive]`
macro that generates the implementation from the struct definition.

```rust
use serde::{Deserialize, Serialize};

#[derive(Debug, Serialize, Deserialize)]
struct User {
    name: String,
    email: String,
    age: u8,
    #[serde(default)]                    // field is optional with default
    role: String,                        // default: String::default() = ""
    #[serde(default = "default_tags")]   // custom default function
    tags: Vec<String>,
    #[serde(rename = "joinedAt")]        // JSON field name differs from Rust field
    joined_at: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    notes: Option<String>,               // not serialized if None
}

fn default_tags() -> Vec<String> {
    vec!["new".to_string()]
}

// Boundary crossing: JSON string → Rust struct
let json = r#"{"name":"Ada","email":"ada@example.com","age":30,"joinedAt":"2024-01-01"}"#;
let user: User = serde_json::from_str(json).unwrap();
// user.tags == vec!["new"]  (default applied)
```

### How serde separates the data format from the Rust type

Serde's architecture has three layers:

1. **Data model** — serde defines a minimal data model that all formats
   map to: primitives (bool, i8..i64, u8..u64, f32, f64, char, string,
   byte array), sequences, maps, options, and structs/enums. This is the
   "serde data model" — not JSON, not TOML, not YAML, but a common
   abstraction over all of them.

2. **Format implementations** — each format (JSON, YAML, TOML, MessagePack,
   Bincode, etc.) maps its wire representation to the serde data model.
   A format crate implements `Serializer` and `Deserializer` traits
   that know how to produce/consume the serde data model.

3. **Type implementations** — each Rust type implements `Serialize` and
   `Deserialize` traits that map the type to/from the serde data model.
   The `#[derive]` macro generates this mapping from the struct definition.

This three-layer architecture means:
- Adding a new format (e.g., `serde_bson`) does not require any change
  to the type definitions.
- Adding a new type does not require changes to the format implementations.
- The data model is the stable interface between them.

### The `Deserialize` trait and `#[derive(Deserialize)]`

```rust
// The trait that makes deserialization work
pub trait Deserialize<'de>: Sized {
    fn deserialize<D>(deserializer: D) -> Result<Self, D::Error>
    where
        D: Deserializer<'de>;
}

// What #[derive(Deserialize)] generates (conceptually):
impl<'de> Deserialize<'de> for User {
    fn deserialize<D>(deserializer: D) -> Result<Self, D::Error>
    where
        D: Deserializer<'de>,
    {
        // Generated visitor that knows the field names, types, and defaults
        // Compile-time guarantees: missing required field → error
        //                          wrong type → error
        //                          extra field → error (by default)
    }
}
```

The generated code is zero-cost in the Rust sense: it is monomorphized at
compile time, inlined, and optimized like hand-written code. No reflection,
no runtime type inspection, no schema interpretation overhead.

### What worked exceptionally well

1. **Zero-cost abstraction.** The `#[derive]` macro generates specialized
   deserialization code at compile time. There is no runtime schema
   interpretation overhead. This is fundamentally impossible in Python
   (Pydantic), TypeScript (zod), and most other languages — it requires
   compile-time code generation with monomorphization.

2. **Format independence.** Because serde separates the data model from
   the format, the same struct can be deserialized from JSON, YAML, TOML,
   Bincode, etc. without any change to the struct definition. This is the
   cleanest separation in any data-boundary system surveyed here.

3. **Attribute-based customization is local and visible.** `#[serde(rename
   = "...")]`, `#[serde(default)]`, `#[serde(deny_unknown_fields)]` —
   these attributes live on the field they affect. They are not in a
   separate configuration file, not in a schema document, not in a
   runtime validator function. The boundary behavior is visible in the
   type definition.

4. **Compile-time field verification.** If you add a field to a struct and
   forget to update the JSON, the compiler does not catch it — but serde
   will catch it at runtime (unknown field → error, if `deny_unknown_fields`
   is set). More importantly, if you remove a field from the struct and
   the JSON still has it, `deny_unknown_fields` catches the mismatch.
   This is the "schema drift" problem solved without a separate schema.

### What failed or caused persistent friction

1. **The derive macro is opaque to new users.** `#[derive(Serialize,
   Deserialize)]` looks like magic. When it fails (e.g., "the trait
   bound `T: Deserialize` is not satisfied"), the error message names
   generated code the user has never seen. Debugging serde derive
   failures requires understanding what the macro generates.

2. **Custom deserialization is verbose.** If you need custom logic
   (e.g., "parse this field as either a string or a number"), you
   must implement `Deserialize` manually or use `serde(deserialize_with
   = "...")` pointing at a custom function. The manual implementation
   requires implementing a `Visitor` trait with methods for each serde
   data model type — this is the cost of the format independence.

3. **Untagged enums have performance and correctness issues.**
   `#[serde(untagged)]` on enums tells serde to try each variant in
   order until one succeeds. This is slow (O(n) variants), produces
   confusing errors (the first variant's error is reported, not the
   intended one), and has ambiguous cases. The lesson: **discriminated
   union deserialization needs a tag field; untagged deserialization
   is fragile.**

4. **The data model is a leaky abstraction.** The serde data model
   distinguishes between "struct" (named fields) and "tuple" (positional
   fields) and "map" (key-value pairs). Some formats (JSON) don't
   distinguish structs from maps at the wire level. This means the same
   JSON `{"a":1}` can be a struct with field `a` or a map with key `"a"`,
   and serde's behavior depends on the target type, not on the data.

### Key structural insight for Nomi

**The three-layer architecture is the right decomposition.**
Data model (intermediate representation) + format implementations
(wire → data model) + type implementations (data model → language type)
is the cleanest separation of concerns for data boundaries. Nomi should
aim for this: `Data.decode` takes a source and a format, produces a
data model representation, then decodes that into a Nomi `data` type.

The attribute pattern is transferable: **constraint modifiers should live
on the field they constrain.** `data User { name: str, @rename("joinedAt")
joined: str }` — the boundary metadata is visible in the type definition,
not hidden in a separate schema file or runtime configuration.

---

## 10. Elm JSON Decoders

### Core philosophy

Elm's approach to data boundaries is the most principled in this survey.
An Elm `Decoder a` is NOT a parser for JSON strings. It is a typed decoder
for JSON *values* (the output of `Json.Decode.decodeString`). The JSON
parser converts a string into a `Json.Value`. The decoder converts a
`Json.Value` into a typed Elm value. These are separate concerns with
separate types.

```elm
import Json.Decode exposing (Decoder, string, int, field, map4, at, list, oneOf)

type alias User =
    { name : String
    , email : String
    , age : Int
    , tags : List String
    }

userDecoder : Decoder User
userDecoder =
    map4 User
        (field "name" string)
        (field "email" string)
        (field "age" int)
        (field "tags" (list string))

-- Boundary crossing: JSON string → Result
decodeUser : String -> Result String User
decodeUser raw =
    case Json.Decode.decodeString userDecoder raw of
        Ok user ->
            -- user: User (type-safe Elm value)
            Ok user

        Err error ->
            -- error: Json.Decode.Error (structured error with path)
            Err (Json.Decode.errorToString error)
```

### How Elm decoders compose

Decoders are first-class values of type `Decoder a`. They compose through
a small set of primitives:

1. **`map : (a -> b) -> Decoder a -> Decoder b`** — transform a decoded
   value. The Elm equivalent of `serde(deserialize_with = "...")` but
   with the full Elm type system behind it.

2. **`andThen : (a -> Decoder b) -> Decoder a -> Decoder b`** — decode
   something, then use the result to choose the next decoder. This is
   the monadic bind for decoders. Enables dependent decoding: "if
   `type` field is `"email"`, decode `address` as an email; if `"postal"`,
   decode `address` as a postal address."

3. **`oneOf : List (Decoder a) -> Decoder a`** — try each decoder in order
   until one succeeds. This is the equivalent of serde's `untagged` enums
   or JSON Schema's `anyOf`, but with Elm's guarantee that all possibilities
   are handled.

4. **`field : String -> Decoder a -> Decoder a`** — decode a named field.
   Fields compose: `field "user" (field "address" string)` decodes
   `{"user": {"address": "..."}}`.

5. **`at : List String -> Decoder a -> Decoder a`** — decode a nested path.
   `at ["user", "address", "city"] string` avoids nested `field` calls.

### Why Decoder is separate from the JSON parser

This is the design decision that distinguishes Elm from every other system
in this survey. The JSON parser (`Json.Decode.decodeString : Decoder a ->
String -> Result Error a`) produces a `Json.Value` internally but does not
expose it. The Decoder operates on the parsed JSON value, not on the raw
string.

The separation means:

1. **The JSON parser's job is narrow and complete:** turn a string into a
   JSON value or fail with a parse error. This is a solved problem with a
   deterministic answer.

2. **The Decoder's job is also narrow and complete:** turn a JSON value
   into a typed Elm value or fail with a structured decode error. This is
   the application-specific logic that varies by type.

3. **Decoders can be tested independently of JSON parsing.** You can
   construct a `Json.Value` in Elm and test that `userDecoder` produces
   the expected result. No JSON strings needed.

4. **Decoders carry precise error information.** An Elm decode error
   includes the path (e.g., `.users[3].address.city`) and what went wrong
   at that path. This is because the Decoder tracks context as it walks
   the JSON value.

### What worked exceptionally well

1. **Decoders as values is the right abstraction level.** A `Decoder User`
   is a value you can pass to functions, store in data structures, compose
   with `map`/`andThen`/`oneOf`, and test in isolation. This is strictly
   more powerful than any schema-as-configuration approach because
   decoders are first-class.

2. **Separating parsing from decoding eliminates a class of errors.**
   When parsing fails, the error is always "invalid JSON at position X."
   When decoding fails, the error is always "expected Y at path Z but
   got W." These are different diagnostic categories that should never
   be conflated.

3. **Custom decoders are first-class, not escape hatches.** In Elm, a
   custom decoder is just a function that returns a `Decoder a`. There
   is no distinction between "built-in" and "custom" — the `Decoder`
   type is open. Compare with JSON Schema (custom formats are outside
   the spec) or Pydantic (custom validators are decorators on a
   separate class).

4. **Type safety through the entire pipeline.** Because Elm has no
   `null`, no `undefined`, and exhaustive pattern matching, a decoded
   value is guaranteed to have the declared type. There is no `is None`
   check after decoding, no "did I forget to handle the null case?" The
   type system guarantees it.

### What failed or caused persistent friction

1. **Decoders are verbose for simple types.** Writing `map4 User (field
   "name" string) (field "email" string) (field "age" int) (field "tags"
   (list string))` for a four-field record is boilerplate that no other
   system in this survey requires. Pydantic and serde do this with zero
   code. Elm's position is that the explicitness is worth it (you can
   see exactly what the decoder does), but the verbosity cost is real.

2. **Code generation is the community workaround.** Because hand-writing
   decoders is tedious, the Elm community built tools (`elm-json-decode-pipeline`,
   `json-schema-to-elm`) that generate decoders from type definitions or
   JSON Schema. The fact that codegen exists signals that the verbosity
   is a real problem, and the community solution introduces the same
   schema-drift risk that Elm's design tries to avoid.

3. **No reflection means no automatic derivation.** Elm cannot implement
   `#[derive(Deserialize)]` because there is no runtime type information.
   Every decoder must be handwritten or generated. This is a fundamental
   constraint of Elm's design (no typeclasses, no reflection) and the price
   of the other guarantees Elm provides.

4. **The `oneOf` / untagged union problem.** Like serde's `untagged`,
   Elm's `oneOf` tries decoders in order and reports the first that
   succeeds. Ambiguous cases (two decoders that could both match) are
   silently handled by ordering, which is fragile.

### Key structural insight for Nomi

**Separate parsing from decoding.** This is the single most important
structural insight from Elm. The JSON parser should produce a `Value`
or a parse error. The Decoder should consume a `Value` and produce a
typed value or a structured decode error. These are two distinct phases
with distinct error types. Nomi's `Data.decode(source, Decoder)` should
internally compose a parser and a decoder, but expose the distinction
in error types and in the API (you should be able to decode a `Value`
that was parsed elsewhere).

**Decoders as values with `map`/`andThen`/`oneOf`.** Elm proves that a
small set of combinators (`map`, `andThen`, `oneOf`, `field`, `at`) is
sufficient to express any data boundary pattern. Nomi's `Decoder` type
should support the same combinators, expressed as Nomi functions, not as
a separate mini-language.

---

## Cross-Language Synthesis

### Structural Invariants

These patterns appear across ALL successful data boundary systems. A system
that violates one of these invariants reliably causes friction.

**1. The schema lives with the type, not in a separate artifact.**
Pydantic (schema IS the Python class), serde (derive macro on the struct),
zod (schema IS the TypeScript value). The counter-example is JSON Schema
(schema in a separate JSON file) and OpenAPI (schema in a YAML file that
the host language cannot type-check). Every successful system collapses
the schema/type distinction. Every system that maintains it accumulates
drift.

**2. Error information is structured, path-addressed, and accumulable.**
Zod's `ZodError` with path trees, Elm's path-addressed decode errors,
Pydantic's `ValidationError` with locators. The counter-example is
JSON Schema (no standard error format). Every successful system treats
error representation as a first-class design concern. The error must
say WHAT failed, WHERE in the data structure, and WHY (the constraint
that was violated).

**3. The boundary crossing is a typed operation with a known result type.**
`Data.decode(...)` returns `Result[User, DecodeError]`, not `User | None`,
not a raw dict with a hope and a prayer. Elm's `Result Error a`, Rust's
`Result<T, E>`, zod's `.safeParse()` discriminated union. Every successful
system makes the possibility of failure visible in the return type.

**4. Coercion policy is explicit per-field, not implicit per-format.**
Pydantic's strict/lax modes, serde's `#[serde(deserialize_with)]`, Nickel's
per-field contracts. The counter-example is JavaScript's implicit type
coercion that made `"5" + 3 = "53"`. Every successful system lets the
user specify "this field coerces strings to ints" vs "this field rejects
non-int values" at the field level.

**5. Custom validation is first-class, not an escape hatch.**
Zod's `.refine()`, Pydantic's `@field_validator`, Elm's custom decoder
functions, Nickel's user-defined contracts. Every successful system
allows the user to add validation logic that is checked at the same point
and with the same error reporting as built-in validation. The counter-
example is JSON Schema (custom formats are implementation-defined).

**6. The decode pipeline composes.**
Elm's `field("a", field("b", string))`, zod's `.shape({ a: z.object({ b:
z.string() }) })`, serde's nested struct deserialization. Every successful
system supports nested decoding where inner decoders compose into outer
decoders without the user managing the nesting manually.

**7. Explicitness beats implicitness at the boundary.**
The `unknown` type in TypeScript, `deny_unknown_fields` in serde, closed
`data` in Nomi. Every successful system makes the boundary crossing
VISIBLE in code (you can see where data enters the system) and AUDITABLE
(you can see what the boundary policy is).

### Genuine Design Forks

These are places where systems made genuinely different, irreconcilable
choices. Nomi must choose one path; it cannot have both.

**1. Parse-time vs runtime validation.**
Rust serde (parse-time, through generated code) vs Pydantic (runtime,
through validator functions). The tradeoff: parse-time is faster and
catches errors earlier, but it cannot express validation rules that
depend on runtime state (e.g., "this port must be available on this
machine"). Nomi's position: runtime-first because the first layer
targets Python-hosted execution with flexible validation.

**2. Closed-by-default vs open-by-default.**
Elm (closed — decoder defines exactly which fields exist), JSON Schema
(open — `additionalProperties` is true by default), serde (closed for
known fields, ignores unknown by default, `deny_unknown_fields` opt-in).
Nomi's position: `data` declarations should be closed-by-default. Extra
fields at the boundary should be an error unless explicitly allowed.

**3. Schema-first vs type-first.**
JSON Schema (schema defines the shape, types are separate) vs Pydantic
(type defines the shape, schema is implicit). Nomi's position: type-first.
The `data` declaration is the canonical shape definition. Schema export
is a tooling concern, not a language feature.

**4. Error aggregation vs fail-fast.**
Zod (returns all errors), Pydantic v2 (returns all errors by default),
Elm (fails on first error). The tradeoff: aggregation gives the user a
complete picture; fail-fast gives faster feedback with simpler
implementation. Nomi's position: aggregate errors by default, with an
option for fail-fast. The decode result should carry ALL validation
failures.

**5. Unification (constraint solving) vs validation (constraint checking).**
CUE (unification — find the most specific value that satisfies all
constraints) vs Nickel (validation — check that a concrete value
satisfies declared contracts). Nomi's position: validation. Start with
explicit decoding (data-from-schema). Unification is powerful but
brings a solver runtime that is not appropriate for the first layer.

**6. Imports with integrity vs imports by name.**
Dhall (import with hash pinning) vs JSON Schema `$ref` (import by URI,
no integrity guarantee). Nomi's position: support hash-pinned imports
for shared schemas. The `import` system should distinguish between
"import this local file" (no hash needed) and "import this remote
resource" (hash required or strongly recommended).

**7. General-purpose vs configuration-only.**
Pkl (general-purpose language that evaluates to configuration), Dhall
(not Turing-complete, purely for configuration), Pydantic (library
in a general-purpose language). Nomi's position: data boundary is a
feature of a general-purpose language, not a justification for a
second language. Configuration, validation, and type definitions use
the same syntax and the same constraint vocabulary.

### The Decode Pipeline Design Space

Every data boundary system implements some version of this pipeline:

```
Raw bytes → Parsed Value → Validated/Decoded Value → Internal Type
              (format)         (constraints)            (usage)
```

Systems differ in where they draw the boundaries between stages and
what the stages are called:

| System | Parse stage | Decode/Validate stage | Output type |
|--------|------------|----------------------|-------------|
| Pydantic | `model_validate_json` (internal) | `@field_validator` + type coercions | `BaseModel` subclass |
| CUE | Not applicable (CUE is the format) | Unification with schema | CUE value (concrete) |
| Nickel | Not applicable (Nickel is the format) | Contract checking at `\|` | Nickel value |
| Pkl | Pkl parser | Type checking + amends resolution | Pkl value → rendered format |
| Dhall | Dhall parser | Type checking + normalization | Dhall normal form → rendered format |
| Terraform/HCL | HCL parser | Variable validation + resource type checking | Terraform plan |
| JSON Schema | JSON parser (separate) | Schema validation | JSON value (untyped) |
| TypeScript/zod | `JSON.parse` (separate) | `.parse()` or `.safeParse()` | TypeScript type |
| Rust serde | Format parser (serde_json) | `Deserialize` implementation | Rust type |
| Elm | `Json.Decode.decodeString` | `Decoder a` | Elm type |

The key design choice is: **are the parse and decode stages separable?**
Elm says yes (and proves it with the `Decoder` type). Pydantic says
no (and bundles them in `model_validate_json`). Nomi should follow Elm:
`Data.decode` should accept either a raw string (bundled parse+decode)
or a pre-parsed `Value` (decode only). The `Value` type should be the
intermediate representation that decouples format parsing from type
decoding.

### Merge and Override Semantics

Every configuration system needs to combine values from multiple sources.
The systems in this survey offer different merge semantics:

| System | Merge operation | Scalar conflict | Record conflict | List conflict |
|--------|----------------|-----------------|-----------------|---------------|
| CUE | `&` (unification) | Must be equal (meet) | Recursive unification | Recursive unification |
| Nickel | `&` (merge) | Last wins | Recursive merge | Append |
| Pkl | `amends` | Override (instance wins) | Override | Not directly mergeable |
| Dhall | `//` (override) | Right wins | Right wins | Override |
| Terraform | `merge()` function | Last wins | Deep merge | Override |
| JSON Schema | `allOf` (intersection) | Must satisfy all | Recursive intersection | Must satisfy all |
| Pydantic | Not built-in | N/A | N/A | N/A |

The irreducible tension: **merge semantics are domain-specific, not
universal.** A "merge" of two port numbers should arguably reject
duplicates. A "merge" of two lists of allowed origins should arguably
concatenate. A "merge" of two database connection strings should
arguably let the more specific override the more general.

Nomi's lesson: **provide merge as a configurable operation, not a single
built-in operator.** `Data.merge(a, b, policy)` where `policy` specifies
per-field or per-type merge rules. The default policy should be
conservative (reject on conflict) with explicit overrides for common
patterns (scalar-override, list-concat, record-recursive).

### Error Accumulation vs Fail-Fast

| System | Default behavior | Configurable? |
|--------|-----------------|---------------|
| Pydantic v2 | Accumulate all errors | No (always accumulates) |
| Zod | Accumulate all errors | No (always accumulates) |
| JSON Schema (ajv) | Accumulate all errors | `allErrors: true/false` |
| Elm | Fail at first error | No (always fail-fast) |
| Rust serde | Fail at first error | No (monadic bind fails fast) |
| CUE | Accumulate all conflicts | No (always accumulates all) |

The tradeoff is real:

- **Accumulation** gives the user a complete picture in one pass. For
  large configuration files, this is essential — fixing one error at
  a time across 100 fields is unacceptable.

- **Fail-fast** gives simpler implementation and faster feedback. For
  interactive use (IDE validation as-you-type), fail-fast feels more
  responsive.

Nomi should default to accumulation: `Data.decode` returns ALL validation
errors. The `Data.decode_strict` variant (or a parameter on `Data.decode`)
can provide fail-fast behavior for interactive/tooling use cases.

A structural note: systems that use monadic composition (Elm's `andThen`,
Rust's `?`) naturally fail fast because monadic bind short-circuits on
error. Systems that use applicative composition can accumulate errors
because they check all fields independently. Nomi's decoder combinators
should support both: `Decoder.and_then` (monadic, fail-fast) and
`Decoder.map2` (applicative, accumulates).

### Provenance and Source Tracking

When a value is the result of merging multiple sources, knowing WHERE
each field came from is critical for debugging and auditing.

| System | Provenance support |
|--------|-------------------|
| CUE | Not built-in; each value has a single origin path |
| Nickel | Merge metadata includes source file and location |
| Dhall | Import chain is recorded; `dhall resolve` shows resolved imports |
| Terraform | State file records resource origin (module, provider) |
| Pydantic | Not supported; validated values lose source information |
| JSON Schema | Not supported; validation is stateless |

Provenance matters in three scenarios:
1. **Debugging:** "Why is this field `null`?" → trace back to the source
   that set it.
2. **Auditing:** "Who changed this value?" → compare provenance across
   versions.
3. **Policy enforcement:** "This field can only be set by the production
   config, not by user overrides." → provenance-based merge policy.

Nomi's position: **provenance should be optional metadata, not a required
part of every value.** `Data.decode(source, Decoder)` should optionally
attach source information to decoded fields. The `explain` system should
be able to show provenance when available:

```
explain user.role
# user.role = "admin"
#   source: config/production.nomi:42 (overrides base.nomi:15)
#   constraint: must be one of ["admin", "viewer", "editor"]
#   constraint: satisfied
```

### The "Config Language" Question

When does a data boundary system become its own language, and how does
Nomi avoid that?

A system becomes its own language when it acquires:
1. **Control flow** — conditionals, loops, pattern matching that differ
   from the host language.
2. **Type system** — a separate type vocabulary that does not map to the
   host language's types.
3. **Computation model** — a different evaluation strategy (lazy vs eager,
   constraint-solving vs sequential).
4. **Import/module system** — a separate dependency resolution mechanism.

Pkl and Dhall are their own languages (they have all four). Nickel has
2-3 (control flow, type system). CUE has 3 (type system, computation
model, import system). Pydantic has 0 — it is a library in Python that
uses Python's control flow, type system, computation model, and import
system. TypeScript/zod has 0 — same reason.

Nomi's position: **zero of four.** The data boundary vocabulary uses:
- Nomi's control flow (`match`, `if`, `for`) for conditional validation
- Nomi's type system (`data`, `str`, `int`, `Result`) for schema types
- Nomi's computation model (eager, sequential) for validation logic
- Nomi's import system (`import`) for schema sharing

The moment someone proposes adding `if/else` syntax to a data boundary
definition, or a `let` binding that doesn't work like Nomi's `let`, or
a separate import path for schema files — that is the second-mini-language
trap. The correct response is: "reduce it to an existing Nomi normal form."

### Anti-Patterns

These data boundary mistakes consistently hurt ecosystems. Nomi should
avoid all of them.

**1. The Separate Schema File.**
JSON Schema, XSD, proto files, OpenAPI specs — a schema in a separate
file that the host language cannot type-check. Invariably, the schema
and the code diverge. Fields are added to the schema but not the code,
or vice versa. The fix is always the same (code generation, drift
detection, CI checks), and it's always a patch over the fundamental
flaw: two sources of truth for the same thing.

**2. Validation That Returns Boolean.**
`isValid(data)` returns `true` or `false`. The caller knows validation
failed but not WHY. The data is not narrowed to a validated type. The
caller must re-validate later because the compiler doesn't know the
data was checked. This is the anti-pattern that Elm's `Decoder a`,
zod's `.safeParse()`, and serde's `Result<T, E>` all fix: validation
should PRODUCE a typed value, not return a boolean.

**3. Default Values That Hide Missing Data.**
`port: int = 8080` — was the port explicitly set to 8080, or was it
missing and defaulted? The distinction matters for auditing and
troubleshooting. JSON Schema's `"default"` keyword is annotation-only
(does not apply the default during validation — that's a separate
concern). Pydantic defaults are applied silently. The fix: default
application should be traceable. Nomi should record whether a field
value came from the source data or from a default.

**4. Open-By-Default Records.**
JSON Schema's `additionalProperties: true` by default means typos pass
validation. Serde's default (ignore unknown fields) means renamed fields
are silently dropped. The fix is `deny_unknown_fields` or
`additionalProperties: false`, but both are opt-in. The safe default
is closed: reject unknown fields unless explicitly allowed.

**5. Format-Specific Validation Logic.**
"Validate email if the source is JSON, but not if it's YAML" — format-
specific validation creates behavior that depends on the transport, not
the data. Serde avoids this by validating at the Deserialize trait level
(format-independent). Pydantic avoids this by validating at the model
level (format-independent). Nomi should validate at the `data` level,
not at the format level.

**6. Coercion Without Signal.**
JavaScript's `==`, Python 2's `"5" == 5`, YAML's `1.0` interpreted as a
float — coercion that changes a value's type without warning. The fix
is explicit coercion policy. Pydantic v2 says: `str` field accepts `int`
and coerces (lax by default), but with `strict=True` it rejects. The
coercion MUST be opt-in and visible.

**7. Error Messages That Leak Implementation Detail.**
"AttributeError: 'NoneType' object has no attribute 'name'" — this is a
null-pointer error, not a validation error. The user needs "field 'name'
is required but was missing." Every successful system translates
implementation-level failures into domain-level error messages. Nomi's
explanation normal form should ensure that data boundary errors speak
in constraint vocabulary, not in implementation vocabulary.

**8. The Partial Validation Trap.**
"Validated at construction, but field values can be mutated afterward"
— Python dataclasses (without `frozen=True`), JavaScript objects after
zod validation. The type system says "this is a User" but the value can
become invalid through mutation. Rust avoids this with ownership
(mutation is controlled). Elm avoids this with immutability. Nomi's
position: `data` values should be immutable by default. Mutation at
the field level should be opt-in with a visible marker.

**9. No Schema Version Negotiation.**
API changes from v1 to v2. The schema changes. Old clients break. This
is a universal problem, but most data-boundary systems leave versioning
to the application layer. The few that address it (Dhall's hash-pinned
imports, Pkl's `amends "package@2.0"`) provide version pinning but not
version negotiation. Nomi should support versioned schemas
(`import schema as UserV2 from "schemas.nomi"`) and provide migration
tooling for schema evolution.

**10. Validation as a Separate Step From Construction.**
```python
user = User()          # constructed, unvalidated
user.name = "Ada"      # field set, unvalidated
user.validate()        # validate as a separate step
```
Between construction and `validate()`, the object is in an invalid state.
Pydantic avoids this by validating at construction. Elm's `Decoder` avoids
this by making construction impossible without validation. Nomi should
follow: a `data` value is valid at construction or the construction
fails. There is no "constructed but unvalidated" state.

---

## Nomi Adopt / Refuse / Adapt Table

| # | Idea | Source | Nomi Action | How it maps to Nomi's vocabulary |
|---|------|--------|-------------|----------------------------------|
| 1 | Schema IS the type definition (no separate schema language) | Pydantic, zod | **Adopt** | `data` declarations serve as both the program type and the decode schema. `Data.decode(raw, User.decoder)` uses the `data` definition as its sole schema source. |
| 2 | Structured errors with paths and constraint names | Elm, zod | **Adopt** | `DecodeError` carries a path (`["user", "address", "city"]`), the constraint that failed (`required`, `type_mismatch`, `out_of_range`), and the value that failed. The `explain` system consumes these. |
| 3 | Three-layer architecture: format → data model → type | serde | **Adopt** | `Data.decode(source, Decoder)` internally: (1) format parser produces `Value`, (2) `Decoder` maps `Value` → `data` type. Separate `Data.parse(source, Format)` for parse-only. |
| 4 | `Result` return type from decode | Elm, Rust, zod | **Adopt** | `Data.decode(...)` returns `Result[User, DecodeError]`. Caller handles error explicitly. No exceptions for expected decode failures. |
| 5 | Closed-by-default `data` declarations | Elm, serde `deny_unknown_fields` | **Adopt** | `data User { name: str; email: str }` rejects unknown fields. Openness is opt-in: `data User { name: str; @extra_fields_ok ... }` with an explicit marker. |
| 6 | Per-field coercion policy | Pydantic strict/lax | **Adopt** | `data User { @strict age: int; @lax port: int }` — `@strict` rejects coercion; `@lax` accepts string-to-int conversion. Default is `@strict` (no silent coercion). |
| 7 | Decoders as first-class composable values | Elm | **Adopt** | `Decoder` is a Nomi type. Combinators: `Decoder.field`, `Decoder.at`, `Decoder.map`, `Decoder.and_then`, `Decoder.one_of`. All are ordinary Nomi functions. |
| 8 | Merge with explicit per-field policy | Nickel, Terraform | **Adapt** | `Data.merge(a, b, merge_policy)` with named policies (`override`, `concat`, `reject_on_conflict`). Adapt Nickel's merge by making the policy explicit per-call rather than universal. |
| 9 | Constraint composition is order-independent | CUE | **Adapt** | Nomi's constraint vocabulary should be commutative (`name:(>0 & <100) = value`). Adapt CUE's unification to runtime constraint checking — no solver, but the constraints compose regardless of order. |
| 10 | Not-Turing-complete for shared/imported configuration | Dhall | **Adapt** | Nomi itself is Turing-complete. But `data` declarations should be evaluable without arbitrary code execution — adapt Dhall's termination guarantee to Nomi's `data` layer by restricting `data` body expressions to pure constraint expressions. |
| 11 | Import with content-addressed integrity | Dhall | **Adopt** | `import "schema.nomi" sha256:...` for shared schemas. The hash is optional for local files, required for remote imports. |
| 12 | Default values are part of the `data` declaration | Pkl, CUE, serde | **Adopt** | `data User { name: str; @default("viewer") role: str }`. Defaults are visible in the data definition. Default application is traced for provenance. |
| 13 | Template/amends conformance chain | Pkl | **Adapt** | `Data.decode(raw, against=BaseConfig.decoder)` where `against` verifies that the decoded value conforms to a base type AND does not introduce undeclared overrides. Adapt Pkl's `amends` to Nomi's `against` parameter. |
| 14 | Three-phase boundary: parse → validate → construct | Terraform plan/apply | **Adapt** | `Data.decode(raw, Decoder)` returns an intermediate `DecodePlan` that carries validation results before construction. The caller inspects the plan before committing. Adapt Terraform's plan/apply to Nomi's validate/construct separation. |
| 15 | Provenance tracking as optional metadata | Nickel, Dhall | **Adapt** | `Data.decode(raw, Decoder, source="config/prod.nomi")` attaches source info to decoded fields. Provenance is queryable via `explain`. Adapt Nickel's merge metadata to Nomi's `explain` normal form. |
| 16 | Separate parsing from decoding | Elm | **Adopt** | `Data.parse(raw, Format.json)` → `Result[Value, ParseError]`. `Data.decode_value(value, Decoder)` → `Result[T, DecodeError]`. `Data.decode` composes both. |
| 17 | Accumulate errors by default, fail-fast as option | Zod, Pydantic | **Adopt** | `Data.decode(...)` returns ALL validation errors. `Data.decode_strict(...)` (or a `fail_fast` parameter) stops at the first error. |
| 18 | Validation produces a proof-carrying value (parse, don't validate) | TypeScript/zod, Elm | **Adopt** | `Data.decode` returns a value of the decoded type, not a boolean + an untyped value. The return type `Result[User, DecodeError]` encodes "the value is valid" in the type. |
| 19 | No separate mini-language for data boundary expressions | Pydantic, zod | **Adopt** | Constraints, validators, and boundary logic use Nomi expressions (functions, pattern matching, pipeline). No embedded DSL with its own parser. |
| 20 | Unification-based constraint solving | CUE | **Refuse** (for now) | CUE's unification is powerful but brings a constraint-solver runtime. For the first layer, Nomi uses explicit decoding (data-from-schema). Unification is deferred to a future tool/layer. |
| 21 | Schema export to portable formats (JSON Schema, OpenAPI) | Pydantic, Pkl | **Adapt** | `data` declarations can export to JSON Schema for interop. But the export is a tooling concern (`nomi schema export`), not a language feature. Adapt Pydantic's `model_json_schema()` to Nomi's CLI tooling. |
| 22 | Code generation from schema | Pkl, OpenAPI | **Refuse** | Nomi is the language. There is no second language to generate code for. Schema ↔ type is bidirectional because they are the same thing. Reject codegen as a data boundary pattern — it is a symptom of the separate-schema anti-pattern. |
| 23 | Lazy contract checking (check on field access, not at decode time) | Nickel | **Refuse** | Lazy checking means errors surface far from the boundary crossing — the opposite of what data boundaries need. Nomi validates eagerly at decode time. Deferred validation is a separate concern (assertions in function bodies). |
| 24 | `allOf` / `anyOf` / `oneOf` / `not` as primitive schema combinators | JSON Schema | **Adapt** | Adapt JSON Schema's composition keywords to Nomi's constraint vocabulary: `name:(A & B)` for intersection, `name:(A | B)` for union. `not` is not needed (express with negated constraints). The key adaptation: these combine Nomi constraints, not schema documents. |

---

## Sources

### Primary sources (language documentation and specifications)

- Pydantic v2 documentation: https://docs.pydantic.dev/latest/
- CUE language specification: https://cuelang.org/docs/references/spec/
- Nickel user manual: https://nickel-lang.org/user-manual/
- Pkl language reference: https://pkl-lang.org/main/current/language-reference/
- Dhall language specification: https://github.com/dhall-lang/dhall-lang/blob/master/standard/README.md
- Terraform HCL syntax: https://developer.hashicorp.com/terraform/language/syntax/configuration
- JSON Schema specification (2020-12): https://json-schema.org/draft/2020-12/json-schema-core.html
- TypeScript handbook — narrowing: https://www.typescriptlang.org/docs/handbook/2/narrowing.html
- zod documentation: https://zod.dev/
- Rust serde documentation: https://serde.rs/
- Elm JSON Decode documentation: https://package.elm-lang.org/packages/elm/json/latest/Json-Decode

### Key design essays and papers

- Alexis King, "Parse, Don't Validate" (2019): https://lexi-lambda.github.io/blog/2019/11/05/parse-don-t-validate/
- Marcel van Lohuizen, "The Logic of CUE" (2019): https://cuelang.org/docs/concepts/logic/
- Gabriel Gonzalez, "Dhall: A Non-Repudiable Configuration Language" (2018)
- Phil Wadler, "The Expression Problem" (1998) — for the open/closed type tension that underlies schema extensibility
- Peter Landin, "The Next 700 Programming Languages" (1966) — for the convergence thesis that underlies "don't build a second mini-language"

### Nomi internal references

- [../convenience/data_and_types.md](../convenience/data_and_types.md) — Nomi's data boundary vocabulary
- [../convenience/design_lessons_and_integration.md §4.7](../convenience/design_lessons_and_integration.md) — integration decisions for data boundary normal form
- [../convenience/design_lessons_and_integration.md §1.1](../convenience/design_lessons_and_integration.md) — the second-mini-language systemic pattern
- [../language/language_design_dimensions.md §4.6](../language/language_design_dimensions.md) — boundary crossing as Explain + Choose
- [../language/language_foundation.md](../language/language_foundation.md) — canonical design foundation, scope constraints for first layer
- [../convenience/absence_and_result.md](../convenience/absence_and_result.md) — `Result[T, E]` for expected failure (the return type of `Data.decode`)
