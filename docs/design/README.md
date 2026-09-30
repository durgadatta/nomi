# Nomi Target Design

> Status: canonical target-language design.
>
> This directory defines the language Nomi is trying to become. It is not a
> description of the current Python, Rust/WASM, or JavaScript prototypes.
> Implementation artifacts are experiments against this target, never design
> authority.

## Reading Order

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
node kinds. Compiler IR may be smaller or larger.

## Language Shape

### Friendly scripts, checked programs

Types are inferred in local code. Public package APIs require annotations.
There is no implicit `Any`: code that intentionally leaves the checked world
uses `Any` explicitly.

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

Pure code needs no marker. Public functions that touch files, clocks, random
sources, processes, databases, or networks declare a `uses` set. The compiler
checks that effects are available; the runtime supplies concrete capabilities.

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

Nomi has four deliberate layers:

| Layer | Stability | Examples |
| --- | --- | --- |
| Core surface | Small and conservative | binding, `func`, call, `data`, `if`, `match`, loops, modules |
| Standard conveniences | Widely useful, mechanically reducible | `|>`, `?.`, `??`, postfix `?`, interpolation |
| Libraries and protocols | Evolvable without grammar changes | collections, decoding, files, HTTP, tables, testing |
| Scoped language tools | Explicitly entered and inspectable | symbolic expressions, query plans, staged code |

A feature moves inward only after real programs show that the outer layer is
insufficient.

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

The first serious target includes:

- literals, bindings, functions, calls, modules, and a small prelude;
- local type inference and explicit public signatures;
- immutable product and variant data;
- exhaustive patterns and `match`;
- lists, maps, loops, and one pipeline vocabulary;
- `Option`, `Result`, postfix propagation, and deterministic cleanup;
- explicit decode/encode boundaries with accumulated errors;
- console, files, JSON, text, time, process, and HTTP through
  capability-checked APIs;
- examples, structured diagnostics, formatting, REPL, package tooling, and LSP;
- structured asynchronous tasks.

The first target does not require:

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
