# Language Degrees Of Freedom

> Status: active design framework.
>
> Scope: documentation-only. This document classifies where Nomi should be
> strict, flexible, library-led, or explicitly fenced. It helps avoid treating
> every design question as a binary choice between "syntax" and "no syntax."

## Purpose

A pleasant language needs controlled freedom. Too little freedom makes ordinary
programming feel cramped. Too much freedom makes every file its own dialect.

Nomi should therefore design along multiple degrees of freedom:

```text
surface freedom
semantic freedom
library freedom
tooling freedom
domain freedom
runtime freedom
```

The goal is not maximal choice. The goal is the right freedom at the right
layer, with enough regularity that code remains readable after time away.

## The Ladder

Use this ladder when deciding how much freedom a feature should have.

| Level | Meaning | Good for | Risk |
| --- | --- | --- | --- |
| Fixed core | One canonical operation with one meaning. | Binding, calls, pattern success/failure, data construction. | Too rigid if it blocks common work. |
| Surface sugar | One pleasant spelling that expands to the core. | Pipelines, holes, if-let, guard-let, equations. | Memory burden if many aliases exist. |
| Library convention | Ordinary functions, values, and block policies. | Query verbs, config merge, result helpers, trace policies. | Conventions may fragment without standard names. |
| Scoped extension | Extra notation or power visible in a local scope. | Units, symbolic math, domain templates, query DSLs. | Can become a private dialect if expansion is not inspectable. |
| Advanced layer | Compatible feature family not needed for the first language. | Effects, macros, dense array notation, regions, proof-like types. | Can distort the everyday language if introduced too early. |
| Rejected freedom | A choice that creates incoherence. | Global syntax mutation, second validation language, broad implicit conversions. | Tempting because it may solve one local problem elegantly. |

This ladder complements the
[Syntax Synthesis Matrix](../convenience/syntax_synthesis_matrix.md) admission
ladder. The synthesis matrix asks whether a feature enters. This document asks
how freely it may vary once admitted.

## Dimension Map

| Dimension | Nomi should be strict about | Nomi should allow freedom in |
| --- | --- | --- |
| Binding | How names enter scope and how constraints fail. | Which predicates, types, and messages a binding uses. |
| Function calls | Argument mapping, defaults, return behavior, diagnostics. | Function values, higher-order use, composition, library APIs. |
| Patterns | Structural test, tentative binding, constraint distinction. | Pattern forms admitted over time: lists, maps, variants, regex captures. |
| Data | `data` as owned values; fields reuse binding. | Display policy, derived helpers, library codecs. |
| External boundaries | Decode is explicit; provenance is retained. | Source kinds: JSON, CSV, env, CLI, HTTP, config, database rows. |
| Failure | Absence, expected failure, exception, and constraint failure stay distinct. | Helper combinators, result pipelines, domain error types. |
| Flow | Pipeline applies values; composition builds functions. | Verb vocabulary, eager/lazy plan choice, backend lowering. |
| Blocks | Caller-side block attached to a call; callee invokes with `yield`. | Policies such as retry, using, trace, transaction, fixture, timeout. |
| Mutation | Rebinding and mutation must be visible enough to reason about. | Library data structures, transaction policies, future lenses/projections. |
| Effects | Authority boundaries should be explainable. | Capability models can begin as conventions before type-level tracking. |
| Syntax | Shared style, few placeholders, visible advanced boundaries. | Local style within normal forms; future scoped notation. |
| Tooling | Expansion and diagnostics must be inspectable. | Editors, notebooks, reports, and AI tools can present different views. |

## Strict Core

The following should have very low freedom. They are memory anchors:

- A binding receives a value, checks constraints, and commits or diagnoses.
- A function call maps arguments to parameter bindings.
- A pattern either fits or does not; captures are tentative until success.
- A data declaration creates owned program values.
- External values cross explicit decode or pattern boundaries.
- A pipeline is value flow now; composition is function construction for later.
- A block is caller-side code attached to a call.
- Diagnostics speak in language concepts rather than interpreter internals.

If any of these become ambiguous, the rest of the language loses its footing.

## Flexible Surface

Surface sugar is welcome when it is visibly one of the strict core operations:

```nomi
active_names =
    users
    |> where(_.active)
    |> select(_.name)
    |> sort
```

The syntax may be flexible in layout and composition, but the expansion should
be boring:

```text
sort(select(where(users, _ => _.active), _ => _.name))
```

The exact expansion above is illustrative, not canonical; the important point
is that tooling can show ordinary calls and function values underneath.

## Library-First Freedom

Many good ideas should start as libraries because libraries can explore names,
data models, and ergonomics without freezing syntax.

Prefer library-first for:

- collection/table verbs;
- config merge policies;
- result combinators;
- trace/report formats;
- typed templates;
- rank/shape operations;
- task/process helpers;
- file/network/world capabilities.

A library pattern deserves syntax only after:

1. several examples use it repeatedly;
2. the reduction to normal forms is obvious;
3. diagnostics are better with syntax than with functions;
4. it does not create a second mini-language.

## Scoped Extension Freedom

Some domains genuinely need notation: units, math, regular expressions,
queries, templates, symbolic rewrites, or proof-like checks. Nomi should allow
this only with explicit fences:

```nomi
use units:
    distance = 12 m
    time = 3 s

quote:
    x + 0
```

Rules for scoped extension:

- The scope must be visible in source.
- Tooling must show the expanded form.
- The extension must not change meanings outside its scope.
- Diagnostics must point through the expansion to the user's source.
- Ordinary Nomi must remain readable without knowing the extension.

## Degrees By Audience

Different users need different freedom.

| Audience | Preferred freedom | Guardrail |
| --- | --- | --- |
| Beginner | Fixed core plus a few surface conveniences. | Do not require advanced theory to read examples. |
| Scripter | Library freedom for files, data, CLI, HTTP, process. | Keep boundary checks and errors visible. |
| Data user | Flow verbs, table plans, notebook explanation. | Do not hide execution timing or backend limits. |
| Library author | Block policies and standard conventions. | Policies must explain yield, retry, cleanup, and cancellation. |
| Domain expert | Scoped extension and templates. | Fenced notation with expansion and diagnostics. |
| Researcher | Advanced layers. | Must not leak into the first everyday surface. |
| AI assistant | Inspectable expansion and explicit status labels. | No private syntax with unexplainable semantics. |

## Design Questions

When reviewing a proposal, ask:

1. What degree of freedom does this feature require?
2. Can it begin as a library convention?
3. If it needs syntax, what normal form does it expand to?
4. If it needs domain notation, what fence contains it?
5. What does a beginner need to know to ignore it safely?
6. What does tooling show when explaining it?
7. What existing freedom does it duplicate?
8. What user mistake becomes easier if this freedom is allowed?

## Worked Example: Applying The Ladder

A concrete decision record showing the ladder applied to features that landed
at different levels.

### Example 1: Pipeline `|>` — classified as Surface Sugar

**Proposal:** `value |> f` passes `value` into `f`.

**Ladder analysis:**

| Level | Question | Answer |
|---|---|---|
| Fixed core | Is `|>` a new execution model? | No. `a \|> f` = `f(a)`. It's ordinary call, ordinary evaluation. |
| Surface sugar | Does it have one canonical expansion? | Yes. `a \|> f(b)` = `f(a, b)`. Tooling can show the call underneath. |
| Library convention | Could a function do this? | `pipe(a, f)` works but is unreadable nested. Sugar wins because it's used on nearly every line. |
| Scoped extension | Does it need a fence? | No — it doesn't change meanings outside itself. |
| Advanced layer | Does it require advanced knowledge? | No — beginners can read `\|>` as "then" without understanding desugaring. |
| Rejected freedom | Would rejection fragment the language? | No, but it would force ugly nesting or temporary variables for simple left-to-right chains. |

**Decision:** Surface sugar. The expansion is boring and inspectable. The syntax
is lightweight because it's used constantly.

### Example 2: Collection Verbs (where, select, map, fold) — classified as Library Convention

**Proposal:** `users |> where(_.active) |> select(_.name)`

**Ladder analysis:**

| Level | Question | Answer |
|---|---|---|
| Fixed core | Are these new semantics? | No. Each verb is a function that takes a collection and a predicate/transform. |
| Surface sugar | Should they have dedicated syntax? | Not yet. They compose with `\|>` already. Dedicated syntax would add keywords without new semantics. |
| Library convention | Can they start as functions? | Yes. A standard prelude module provides them. Users import what they need. |
| Scoped extension | — | Not needed. |
| Advanced layer | — | Not needed. |
| Rejected freedom | — | Not relevant; function vocab is the right freedom level. |

**Decision:** Library convention. If several programs use the same ten verbs
repeatedly, and diagnostics are clearly better with syntax, revisit. Until then,
library functions are the right vehicle.

### Example 3: Symbolic Rewrite / `quote` — classified as Scoped Extension

**Proposal:** `quote: x + 0` rewrites to `x` (symbolic algebra).

**Ladder analysis:**

| Level | Question | Answer |
|---|---|---|
| Fixed core | Is symbolic rewrite part of the everyday computational model? | No. Ordinary programs don't need term rewriting. |
| Surface sugar | Can it desugar to ordinary Nomi? | No — the semantics are genuinely different (manipulating unevaluated terms). |
| Library convention | Can a library do this without syntax? | Partially. A library can provide rewrite functions, but readable term notation needs a fence. |
| Scoped extension | Does it need a visible fence? | Yes. `quote:` or `use symbolic:` keeps the notation contained. Outside the fence, ordinary Nomi. |
| Advanced layer | Should it wait? | Yes. Not needed for the first everyday language. |
| Rejected freedom | Would global term rewriting be rejected? | Yes — ambient rewriting would break local reasoning. |

**Decision:** Scoped extension, deferred to advanced layer. The fence (`quote:`
or `use`) is required, and the feature is not part of the first language users
learn.

### What The Examples Show

- The ladder catches feature creep before it becomes syntax. "Collection verbs
  are useful" does not automatically mean "they need keywords."
- The ladder distinguishes *new semantics* (needs scoped extension or advanced
  layer) from *new sugar* (surface, if the expansion is boring).
- A feature can move up the ladder later: if collection verbs prove themselves in
  libraries, they can graduate to sugar. Moving *down* is harder — once syntax
  exists, removing it breaks programs.
- The hardest call is between library convention and surface sugar. The tiebreaker
  is: would the library spelling make common code worse to read? For `|>`, yes
  (nested calls are unreadable). For collection verbs, not yet (pipeline + function
  names are clear enough).

## Current Recommendations

- Keep binding, data, pattern, flow, block, and explanation as strict memory
  anchors.
- Keep convenience syntax small and canonical: `|>`, `_`, `$1`, `where`,
  if-let/guard-let, equation forms.
- Keep query, config, result, trace, and rank/shape experiments library-first
  until examples prove syntax improves them.
- Fence symbolic rewrite, scoped notation, effects, and advanced array
  notation.
- Reject global macros, user-defined precedence in ordinary modules, broad
  implicit conversions, and multiple equivalent validation systems.

Nomi should feel generous in what users can express, but conservative in how
many concepts they must remember.
