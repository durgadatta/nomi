# Syntax And Special Forms Quality Review

> Status: active design review.
>
> Scope: documentation-only audit of Nomi's syntax, special forms, convenience
> surfaces, user experience, research coverage, and promotion quality. This file
> does not propose new syntax by itself; it decides what must be true before
> syntax becomes part of the language.
>
> Read with: [syntax_design_rules.md](syntax_design_rules.md),
> [expression_statement_orientation.md](expression_statement_orientation.md),
> [review_and_roadmap.md](review_and_roadmap.md),
> [vertical_pillars.md](vertical_pillars.md), and
> [language_spec.md](../language/language_spec.md).

## Executive Judgment

Nomi's design spine is strong: normal forms, expression/statement doctrine,
surface pillars, and cross-language research now give the project enough
structure to say "no" intelligently. The main risk is not lack of ideas. The
main risk is **promotion without packet quality**: syntax becoming implemented,
documented, or taught before its diagnostics, reduction, status, and user path
are equally clear.

The language should therefore harden around this stance:

```text
few semantic anchors
concrete daily-use surfaces
library-first exploration
inspectable reductions
diagnostics before syntax promotion
```

Nomi should not try to be an encyclopedia of language conveniences. It should
feel generous because the few accepted conveniences compose well.

## Coverage Assessment

| Area | Coverage quality | Current strength | Main gap |
|------|------------------|------------------|----------|
| Strings/text | strong | String pillar ties interpolation, literals, typed sinks, patterns, Unicode, serialization, and security. | Spec packets for typed strings, regex capture, Unicode views. |
| Functions/calls | strong | Universal surface and secondary gates are now explicit. | Final composition spelling, diagnostics for generated parameters, extension-function story. |
| Collections/flow | improved, still volatile | Primary ordinary-collection layer is separated from table/query secondary layer. | Canonical verb naming and materialization rules. |
| Data values | important but underdeveloped | Data/type docs and vertical pillars name `data` as the upgrade path from maps. | Focused data-values-and-variants packet. |
| Patterns/selectors | good but status-sensitive | Pattern family is broad and coherent. | Full value-producing match suites, exhaustiveness, mapping patterns, selector scope. |
| Absence/result/failure | good direction, incomplete taxonomy | Distinction between absence, Result, exceptions, pattern non-match, and constraint failure is mostly clear. | One failure taxonomy and propagation target rules. |
| Blocks/policies | conceptually strong | Block-call model unifies resource, retry, fixture, trace, future concurrency. | Everyday policy packet plus source/Core representation for block values. |
| Resources/world | high-impact, thin spec | Vertical pillar identifies paths, URLs, commands, secrets, capabilities. | Concrete resource/world feature packet and prelude surface. |
| Modules/packages | useful but not syntax-reviewed enough | Module visibility, re-exports, content-addressed imports are named. | Growth path from script to package, migration and capability identity. |
| Explanation/diagnostics | central but still scattered | Examples/checks/traces/explain are recognized as a normal form. | Shared event schema and feature diagnostics contract. |
| Measures/time/shape | important, future-leaning | Correctness surface identified. | Keep units/time/shape library-first until everyday examples justify syntax. |

## Special Form Inventory

Special forms are constructs whose behavior cannot be understood as ordinary
function calls without knowing reduction or control rules. They deserve a
stricter bar than ordinary library functions.

| Surface | Current role | Layer | Quality judgment |
|---------|--------------|-------|------------------|
| assignment/binding constraints | core naming and judgement | strict core | Keep. Everything else should reuse this binding story. |
| `func` | named block-bodied behavior | strict core/canonical surface | Keep as calm long form. |
| equation definitions | compact named expression behavior | surface sugar | Keep; style-limit no-parens forms. |
| `=>` arrows | anonymous expression functions | surface sugar | Keep; use `func` for statement bodies. |
| `_`, `$1`, `$name`, sections | tiny function generation | surface sugar | Keep style-limited; no extra placeholder aliases. |
| `where` | local support bindings | surface sugar over Binding | Keep; ensure scope and diagnostics are clear. |
| `if` / `unless` | boolean choice | core plus sugar | `if` core; `unless` sugar only, not a design centerpiece. |
| `match` | canonical structural choice | core Pattern surface | Keep; expression form gated by value-block doctrine. |
| if-let / while-let / guard-let | pattern short forms | surface sugar | Keep as strict subsets of `match` + Binding. |
| `?.` / `??` | absence short forms | surface sugar | Keep absence-only; do not merge with Result. |
| `try` expression | recovery boundary | partial/design-sensitive | Keep narrow; clarify value-block and propagation semantics. |
| `defer` | cleanup action | Block/exit policy | Keep implemented behavior; align with block policy and Result story. |
| `|>` pipeline | value flow | surface sugar | Keep as first-class flow surface. |
| `>>>` / `<<<` composition | function construction | surface sugar | Keep concept; settle teaching spelling. |
| ranges/slices/spread/comprehensions | collection construction and flow | surface/library | Keep Python-compatible surface; diagnostics and status should stay honest. |
| block calls `call(...) -> x:` | scoped policy | core Block surface | Keep as the one control-policy abstraction. |
| `examples:` / `check:` | explanation/test surface | design-settled | Keep direction; needs event schema before hard spec. |
| `data` | owned data values | core Data surface | High priority; needs focused packet. |
| `import` / `pub` / re-export | module binding | core/surface | Keep, but avoid package-system overclaim. |
| typed string prefixes | boundary values | design-needed | Good direction; require sink-specific diagnostics. |
| query blocks | scoped flow notation | future/secondary | Do not promote before verbs, row scope, materialization, and explain are settled. |
| macros/quote/scoped rewrites | code-as-data | future/fenced | Keep out of everyday syntax until expansion and diagnostics are first-class. |

## Syntax Quality Gates

No new syntax or special form should be promoted unless it passes all gates.

| Gate | Required answer |
|------|-----------------|
| Everyday pressure | What common program becomes clearer for a broad audience? |
| Surface specificity | Is this syntax for a concrete thing users write/read, not an abstract virtue? |
| Normal-form reduction | Which existing normal form owns it? |
| Library-first attempt | Why are ordinary functions, data values, or block policies insufficient? |
| Status honesty | Is it implemented, partial, prototype-ready, design-needed, library-first, future, research-only, or rejected? |
| Diagnostics | What does failure say, with source span, value, rule, and next action? |
| Explanation | What does `explain` show after desugaring or execution? |
| Interaction | How does it compose with binding, patterns, blocks, results, modules, and examples? |
| Expression/statement rule | If it can appear in expression position, what is the value contract and control-transfer behavior? |
| Formatter rule | How should it look after `nomi fmt`? |
| First-hour effect | Can beginners ignore it safely until they need it? |
| Migration posture | If the syntax changes later, can tooling explain or migrate it? |

The highest-risk promotions are the ones that pass "looks nice" but fail
diagnostics, interaction, or status honesty.

## User-Experience Bar

Nomi's syntax should be pleasing in the way a good tool is pleasing: the next
step feels obvious, and the advanced form does not shame the simple form.

Use this user path as the UX benchmark:

```text
print a value
bind a name
write a function
transform a collection
shape data
choose by pattern
handle absence/failure
touch a file or URL
wrap a policy block
split into modules
explain what happened
```

For every new convenience, ask where it belongs in that path. If it belongs
nowhere, it is probably niche or too early.

### Pleasing Syntax Traits

- **One obvious long form.** There is always a calm, explicit spelling.
- **Short forms are strict subsets.** Sugar never has more semantic power than
  the long form it abbreviates.
- **Local consequence is visible.** A reader can tell whether a line binds,
  branches, propagates, yields, retries, defers, decodes, or explains.
- **Advanced power is fenced.** Query, symbolic, rank, template, effect, and
  macro-like features do not leak into ordinary files.
- **Diagnostics teach the model.** Error messages name normal forms:
  binding, pattern, block, result, decode path, flow stage, or example.
- **The formatter is part of the design.** Syntax is not accepted until its
  formatted shape looks ordinary.

### Unpleasant Syntax Smells

- a keyword that exists only to make one library API shorter;
- two short forms for the same cognitive act;
- syntax whose failure vocabulary is private to that feature;
- expression forms that rely on hidden function wrappers for user-visible
  control behavior;
- mini-languages inside strings without typed output and escaping policy;
- table/query features that make ordinary collections feel second-class;
- "advanced" notation that users must learn before they can read basic code.

## Current Gap Closures

This review closes or sharpens these gaps:

1. **Special-form inventory.** The project now has one place that lists the
   surface forms and their quality status.
2. **Promotion gates.** Feature packets and syntax proposals now have a UX and
   diagnostics checklist beyond normal-form reduction.
3. **Status humility.** Collection/query, expression-block, and explanation
   surfaces should remain design-needed or secondary when their user contract is
   not fully specified.
4. **First-hour pressure.** Syntax should be judged against the path from
   tiny scripts to maintainable tools, not only cross-language attractiveness.

## Remaining Review Findings

### 1. Status Claims Are Still Too Coarse

The docs use `design-settled` for some areas where the approach is settled but
the full feature packet is not. Examples:

- collection/query plans: direction is clear, but row scope, materialization,
  ordinary-collection naming, and explain output remain design-needed;
- structured concurrency: block-policy approach is settled, but cancellation,
  supervision diagnostics, and Result interaction are not;
- examples/checks: direction is strong, but the shared event schema is missing;
- data/decode: direction is strong, but constructor/display/equality,
  field-level defaults, provenance, and accumulated errors need one packet.

Use `design-settled approach` only when the model is accepted but the complete
feature packet is not ready for normative spec text.

### 2. The Spec Needs Capability Marking

`language_spec.md` is intentionally aspirational in places. That is fine, but
future readers need visible status per section:

```text
implemented / partial / target-only / design-needed / library-first
```

Without that, a polished paragraph can look more implemented than it is.

### 3. Explanation Is The Weakest Load-Bearing Normal Form

Nomi's promise depends on inspectable reduction and humane diagnostics. Yet
explanation is still more principle than packet. Before adding more syntax,
create a shared event vocabulary for:

- binding failure;
- pattern non-match and guard failure;
- decode field/path failure;
- result propagation or recovery;
- pipeline stage values;
- block enter/yield/resume/cleanup;
- example/check failures;
- redaction and unsafe reveal.

### 4. Data And Failure Need Focused Packets

The next syntax-quality work should not be a new surface feature. It should be:

1. `data` values and variants as the upgrade from maps/tuples;
2. failure taxonomy across `none`, `Result`, exceptions, pattern non-match,
   constraint failure, decode diagnostics, and block policy failure.

Those packets will make many current syntax decisions less speculative.

### 5. The Keyword Budget Needs A Ledger

Nomi already has enough keywords to feel like a real language. Every new
keyword must justify:

- why a function or block policy is not enough;
- whether it is a first-hour concept;
- how it interacts with `match`, `data`, `func`, `yield`, `return`, and `import`;
- whether it has a future migration path.

Do not add keywords for table verbs, effect handlers, scope helpers, task
definitions, macros, or domain templates before library/scoped-extension forms
prove themselves.

## Recommended Next Passes

1. **Capability/status matrix.** Add a matrix across parse, lower, run, tests,
   samples, docs, web, and notebook exposure for every visible syntax family.
2. **Data values and variants packet.** Move `data` from broad direction to a
   spec-ready feature packet.
3. **Failure taxonomy packet.** Unify absence/result/exceptions/pattern
   failure/constraint failure/decode failure/block failure.
4. **Explanation event schema.** Define the shared event vocabulary before more
   feature-specific diagnostics are implemented.
5. **First-hour language path.** Create a tiny runnable teaching path that
   shows the core without advanced surfaces.
6. **Keyword and special-form ledger.** Track accepted, future-reserved,
   rejected, and library-first keywords/special forms with rationale.

## Review Checklist

Use this checklist for future design reviews:

- Does the feature improve strings, functions, collections, data, patterns,
  failure, resources, blocks, modules, explanation, or measures?
- Is it primary, secondary, library-first, scoped, future, or rejected?
- Does it reduce to a normal form users already know?
- Is the long form obvious?
- Is the short form a strict subset?
- Are branch/value/control-transfer rules explicit?
- Are diagnostics and `explain` part of the proposal?
- Does formatter output look ordinary?
- Is there a first-hour story and an expert escape hatch?
- What syntax did we deliberately refuse?

If a proposal cannot answer these quickly, it is not ready for implementation.
