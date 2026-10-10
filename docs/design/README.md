# Nomi Target Design

> Status: canonical target-language design.
>
> This directory defines the language Nomi is trying to become. It is not a
> description of the current Python, Rust/WASM, or JavaScript prototypes.
> Implementation artifacts are experiments against this target, never design
> authority.

## Reading Order

If you want to learn the runnable prototype, start with the
[user guide](../guide/README.md). For a plain-language explanation of the ideas
below and what is implemented, read
[Current Support And Growth](../guide/status.md). This reference owns the target
language; its examples are not all runnable yet.

For the broader purpose, competing directions and current gap, read the
[Computational Medium Vision](vision.md).

1. [Target Design](README.md) - product promise, principles, and language
   shape.
2. [Syntax](syntax.md) - the canonical source forms and notation budget.
3. [Semantics](semantics.md) - the behavior behind those forms.
4. [Pattern Matching](pattern_matching.md) - the first registered focused
   design pass and its complete pattern contract.
5. [Industrial Model](industrial.md) - packages, effects, concurrency,
   security, tooling, deployment, and conformance.
6. [Decision Ledger](decisions.md) - accepted, rejected, deferred, and open
   choices.
7. [Target Suite](targets/README.md) and [Overall Program](targets/overall.nomi) -
   category programs and one active whole-language pressure fixture.
8. [Pattern Target](pattern_matching_target.nomi) - focused pressure cases for
   pattern syntax, scope, coverage, and boundaries.
9. [Language Synthesis](synthesis.md) - critical cross-language evidence,
   interaction gaps, and ordered admission gates.
10. [Resource Completion Proposal](resource_lifetime.md) - designing packet,
    executed symbolic comparison, and remaining type/runtime admission gates.
11. [Interaction Proposal](interaction_model.md) and
    [Interaction Target](interaction_model_target.nomi) - cognitive/interface
    experiments; no new syntax admitted.
12. [Design-First Agenda](redesign_agenda.md) - unresolved whole-language
    dimensions and design closure before reversible implementation.
13. [Function Contracts](function_contracts.md) and
    [Callback Target](function_contracts_target.nomi) - designing pure/effectful
    callback comparison; generic/function-type notation remains open.
14. [Engine-Free Objects](object_framework.md) - designing domain-neutral
    descriptions, typed references, composition and explicit realization;
    implemented as a source-checkout research framework.
15. [Statistical Data Interface](statistical_data.md) - designing engine-free
    object contracts, named lazy plans, schema checking and bounded exact laws;
    a domain adapter over the shared direction; no data engine or source syntax admitted.

[The old target](target.nomi) remains a superseded predecessor, not an active
specification. Target programs illustrate accepted core syntax and explicitly
proposed library contracts; they are not runnable conformance claims.

Versioned frontend-neutral contracts live under [`schemas/`](schemas/). The
first is [Pattern Surface v1](schemas/pattern_surface.schema.json), a
target-only fragment artifact used for Lark/Rust conformance before target
`match` syntax becomes runnable.

The research behind these decisions is consolidated under
[Research](../research/README.md). The dated rationale and action sequence are
in the [2026-07-16 review](../review/2026-07-16.md). Registered focused passes
follow the [design-pass workflow](../orientation/design_pass_workflow.md).

## Product Promise

The broader goal is a [computational medium](vision.md): help people express,
explore, understand, revise and share ideas, then execute them with appropriate
assurance and control. The language, interaction environment and surrounding
practices must be designed together. Research can challenge the current shape;
the prototype and release milestones do not set the limits of that ambition.

Nomi is a general-purpose language for people who want Python's immediacy and
readability without making dynamic accidents, invisible boundaries, or weak
tooling the permanent cost of that friendliness.

It should be excellent for:

- scripts, CLIs, notebooks, and teaching;
- data ingestion, transformation, and validation;
- services, jobs, application logic, and automation;
- libraries that remain readable as teams and codebases grow;
- native, server, browser/Wasm, and embedded-host deployment where the runtime
  profile permits it.

The first minute remains as small as:

```nomi
name = "Ada"
print("Hello, {name}")
```

Growth should not force a second language:

```nomi
pub func register(raw: Value) -> Result[User, DecodeErrors] uses Database:
    input = Signup.decode(raw)?
    return users.insert(User.from(input))
```

The same code should remain legible to a beginner, a reviewer, a compiler, an
editor, and an automated agent.

## Design Thesis

Nomi optimizes for **local reasoning under growth**.

A reader should normally discover the important facts at the point where they
matter:

- a name says whether it is mutable;
- a public boundary states its types, failures, and effects;
- untrusted data visibly crosses a decoder;
- structural alternatives are visible in `match`;
- absence and expected failure do not masquerade as ordinary values;
- resource lifetime and suspension points are visible;
- generated code and implicit behavior remain inspectable.

Convenience is welcome when it removes ceremony without erasing one of those
facts. Brevity alone is not a design argument.

## Cognitive Model

Users should be able to organize the language around eight recurring acts:

| Act | Main surface | Question answered |
| --- | --- | --- |
| Name | bindings and scope | What does this value mean here? |
| Transform | functions, calls, pipeline | How does this value become another? |
| Model | `data`, collections, modules | What concepts exist in this program? |
| Choose | `if`, `match`, patterns | Which situation are we in? |
| Repeat | loops and collection operations | What happens for many values or over time? |
| Fail | `Option`, `Result`, panic | Is this missing, expected to fail, or broken? |
| Touch the world | effects, resources, tasks | What authority and time does this code use? |
| Understand | diagnostics, examples, traces | Why did this happen, and how can it change? |

These are teaching anchors, not a claim that the runtime needs exactly eight
node kinds or that all human activity fits eight acts. Compiler IR may be smaller
or larger. Discovery, creation, negotiation, delegation and collaboration also
shape the [whole-system vision](vision.md#broaden-the-unit-of-design); the
language acts are one orientation within it.

## Language Shape

### Friendly scripts, checked programs

Exploratory scripts and functions may omit annotations and run with defined
runtime checks. Static unknowns remain visible; they are not invented proofs.
Checked public APIs require complete inspectable contracts, which may be
inferred from the owning module or declared explicitly. An annotation policy
may require written signatures without changing the program's meaning.

Inference, declared promises, runtime checks and observed examples are distinct
evidence. Dynamic code does not need an `Any` annotation merely to begin;
crossing into a checked boundary requires supported evidence or an explicit
checked adapter. The [progressive assurance rules](semantics.md#progressive-assurance)
own this direction; general inference and package adapters remain design work.

This gives scripts a low floor and libraries a firm ceiling:

```nomi
answer = 40 + 2

pub func parse_port(text: Text) -> Result[Port, ParseError]:
    value = Int.parse(text)?
    return Port.decode(value)
```

### Immutable by default

`name = value` creates a lexical binding. Mutation is visible through `var`
and `set`. `data` values are immutable. Mutable state is local and explicit;
shared state requires a concurrency-safe abstraction.

### Nominal inside, structural at boundaries

Program-owned concepts use nominal `data`. External maps, JSON, rows, and host
values stay structural until an explicit decoder produces an owned value.
Constructors do not silently coerce external data.

### Three failure stories

- `Option[T]` means a value may be absent.
- `Result[T, E]` means an operation may fail in an expected, typed way.
- panic or an uncaught exception means an invariant or runtime has failed.

The three do not share fallback or propagation semantics accidentally.

### Effects are public facts

Pure code needs no marker. Checked public functions expose their resolved
effects, whether inferred or declared with `uses`. The compiler checks the
contract; the runtime supplies concrete capabilities. An unresolved call is
not evidence of purity, and an effect declaration does not grant authority.

### Concurrency is structured and explicit

`async func` and `await` mark asynchronous APIs and suspension points. Child
tasks live inside task groups and cannot silently outlive their owner.
Cancellation and multiple failures have defined semantics.

### One source language

Configuration, tests, schemas, queries, and build descriptions should use
ordinary Nomi values and functions wherever possible. A domain syntax must be
scoped, inspectable, and justified by a domain model that ordinary calls cannot
express clearly.

## Surface Layers

The current source-language organization uses four deliberate layers:

| Layer | Stability | Examples |
| --- | --- | --- |
| Core surface | Small and conservative | binding, `func`, call, `data`, `if`, `match`, loops, modules |
| Standard conveniences | Widely useful, mechanically reducible | `|>`, `?.`, `??`, postfix `?`, interpolation |
| Libraries and protocols | Evolvable without grammar changes | collections, decoding, files, HTTP, tables, testing |
| Scoped language tools | Explicitly entered and inspectable | symbolic expressions, query plans, staged code |

Moving a source feature inward needs evidence that the outer layer obscures or
cannot carry the selected model. This is a semantic-admission rule, not a
requirement that discovery start outside the core or prove a library failed
before comparing alternatives. The [vision](vision.md) can challenge the layer
organization itself; accepted source meaning changes through explicit decisions.

The [primitive composition hierarchy](primitive_composition.md) offers a
complementary view: six candidate semantic families, reusable combinations and
the laws that must survive reduction. It maps language, domain and interaction
constructs without choosing a new Core or accepting open mechanisms.

## Syntax Contract

Every accepted source form must satisfy all of these:

1. It has one ordinary long form.
2. Its punctuation carries one stable family of meanings.
3. It does not duplicate another common spelling for the same act.
4. Control transfer, failure, mutation, authority, and suspension stay visible.
5. Its formatter shape is defined before promotion.
6. Its diagnostic can name the user's construct and suggest a repair.
7. Its lowering can be inspected without exposing backend trivia.
8. Beginners can ignore it until a concrete task needs it.

This contract is why the target removes several attractive implemented forms.
Equation functions, placeholder lambdas, operator sections, local `where`
clauses, postfix conditionals, `unless`, multiple composition operators, and
universal yield-to-block control each save characters but create a parallel
way to read an already-covered idea.

## First Usable Language

The first product is **small scripts and trustworthy local data reports**.
A person should open the playground, change a calculation, validate imperfect
JSON, repair its errors, and reuse the same report function from the CLI.
That is the first release boundary; the broader general-purpose promise above
remains the destination. The [product synthesis](synthesis.md#first-product-contract)
owns selection and the [roadmap](../orientation/project_roadmap.md#delivery-order-and-dependencies)
owns delivery. Neither is a claim that target programs run today.

The selected release scope is:

- lexical bindings, visible local mutation, ordinary functions and calls;
- Int, Bool, Text, Unit, strict lists and the structural values needed for JSON;
- nominal immutable products/closed variants, constraints, `if`, `match`, loops;
- `Option`, `Result`, explicit error mapping and postfix propagation;
- strict decode/encode, original input paths and a small pure collection library;
- local module reuse with inspectable closed public contracts, inferred where
  supported and declared where needed;
- explicit host input/output, source-linked diagnostics, formatting and a
  small set of complete examples shared by the browser and CLI.

This scope still needs bounded scalar, codec, callable and host-run contracts
before implementation can claim conformance. It does not require a complete
generic inference system or every accepted convenience on day one. An omitted
feature is unsupported in the release profile, never silently given a different
meaning. Exploration remains available; stronger checking does not alter it.

Network clients, structured tasks, fallible language-managed resources, broad
package distribution, notebooks/LSP polish and additional numeric/domain APIs
follow after this release is useful. Existing working surfaces can remain as
clearly described prototype capabilities; they do not enlarge release promises.
Their focused fixtures continue to challenge extension boundaries.

The broader target also does not require:

- user-defined syntax or global macros;
- dependent types or theorem proving;
- implicit effects or hidden dependency injection;
- ownership/lifetime syntax;
- a built-in dataframe/query language;
- multiple dispatch, symbolic algebra, or array glyphs;
- distributed actors as a core primitive.

Those ideas remain possible only if the ordinary language proves a clean
extension boundary.

## Success Tests

For the first release, require the calculation, invalid-input repair and local
reuse journeys in [synthesis](synthesis.md#first-product-contract). The following
tests describe success as the language grows; they are not all prerequisites
for the first useful playground release.

The design succeeds when all of these are true:

- a newcomer produces a visible result in under a minute;
- a useful data-import program fits on one screen without magic;
- a public function reveals its input, output, expected failure, and effects;
- invalid external data reports every relevant path and repair in one pass;
- a reader never has to guess whether `_` means wildcard or hidden parameter;
- resource cleanup and task lifetime remain correct across every exit path;
- CLI, editor, notebook, browser, and native builds agree on semantics;
- a package build is reproducible from source, manifest, lockfile, and toolchain;
- advanced domains can grow without changing the meaning of ordinary code.
