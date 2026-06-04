# Adversarial Language Design Enhancement Notes 2026-06-04

> Status: active critique and enhancement queue.
>
> Scope: documentation-only. This is a hostile senior-language-designer review
> after the June 2026 research expansion into everyday interfaces,
> representation boundaries, remaining feature gaps, and human-computer
> interface languages.
>
> Purpose: convert the broadened design ambition into sharper gates. This file
> is not another vision document. It names where Nomi's current synthesis can
> still fail and what enhancement notes should be absorbed into feature packets,
> specs, tests, and implementation metadata.
>
> Implementation path:
> [Adversarial Enhancement Implementation Plan 2026-06-04](adversarial_enhancement_implementation_plan_2026_06_04.md).

## Position

Nomi has done enough research. More source traditions will not save the design
if the project cannot now say "no" with precision.

The dangerous new temptation is this:

```text
Everything humans use to interact with computers is relevant to Nomi,
therefore Nomi should design for everything.
```

That conclusion is wrong. The right conclusion is narrower and harder:

```text
Everything humans use to interact with computers may reveal a user need.
Only needs that reduce to Nomi's normal forms should affect the language.
Everything else belongs in tools, libraries, frontends, or research.
```

If Nomi absorbs UI, agents, config, shells, spreadsheets, APIs, query systems,
templates, notebooks, visual tools, and accessibility as peer language
features, it will become incoherent. If it treats them as projections over
bindings, commands, data boundaries, capabilities, flow, block policies, and
explanation events, it can become unusually strong.

## Executive Verdict

The design direction is promising but overextended. The current docs prove that
Nomi can synthesize many traditions; they do not yet prove that the language
can survive its own ambition.

The next enhancement phase should be brutal:

1. Stop adding broad research unless a concrete feature packet is blocked.
2. Promote one command/event/explanation spine that UI, agents, CLI, notebooks,
   and diagnostics all share.
3. Harden data-boundary and failure-taxonomy packets before more surface
   syntax.
4. Turn "UI is projection" into metadata and tests, not prose.
5. Refuse any feature that cannot show its long form, diagnostics, source
   spans, capability needs, and accessibility rendering.

The highest-value work is not another syntax form. It is making the existing
normal-form doctrine executable.

## Top Failure Modes

| Risk | Severity | Hostile reading | Enhancement required |
| --- | --- | --- | --- |
| Research becomes permission to accumulate | High | The corpus now covers almost every attractive source of ideas, so any feature can find a precedent. | Require proposals to name rejected precedents, not only inspirations. |
| UI-as-language becomes UI-only semantics | High | Direct manipulation, notebooks, and agent panes could gain behavior that text, tests, and `explain` cannot represent. | Add a command/event registry before richer UI features. |
| Normal forms become slogans | High | Binding, flow, block, data boundary, and explanation are named everywhere but not yet enforced as one artifact path. | Each feature packet must include a reduction table and an inspection command. |
| Explanation remains too late | High | Diagnostics now have a first binding producer, but most features still lack event producers. | Define the explanation-event packet before query, decode, UI controls, or agent actions expand. |
| Data boundary is overloaded | High | Decode, config, schemas, forms, API responses, environment, CLI args, and UI controls all want the same layer. | Write one data-boundary feature packet with provenance, merge, redaction, and accumulated errors. |
| Command model is missing | High | Menus, command palettes, CLI commands, agent tool calls, notebooks, and UI actions all imply commands, but Nomi has no command artifact. | Add a command/value design packet before treating UI affordances as product promises. |
| Agent interface becomes magical | Medium | Natural language prompts could be mistaken for language syntax or trusted plans. | Require preview, typed commands, capability checks, diffs, and replay for agent surfaces. |
| Accessibility remains moral prose | Medium | The docs say accessible renderings matter, but features do not yet have accessibility acceptance rows. | Add accessibility rendering to feature packet templates and docs lifecycle tests. |
| First-hour path is crowded | Medium | `func`, arrows, equations, holes, sections, where, match, constraints, data, blocks, flow, and decode are too much for first contact. | Freeze first-hour Nomi to values, names, calls, `func`, simple arrows, constraints, and diagnostics. |
| Tooling claims outrun semantics | Medium | Web, notebook, Rust/WASM, JS runtime, Core IR, and agent support can look complete while supporting different subsets. | Keep capability matrices feature-owned and frontend-specific. |

## Enhancement Notes By Design Area

### 1. Command Values Are The Missing Bridge

Nomi now says UI affordances, command palettes, shortcuts, agent actions, CLI
tasks, and notebook buttons should reduce to commands. That is correct. It is
also under-specified.

Enhancement note:

```text
Command:
  name
  intent
  inputs
  normal_form
  required_capabilities
  preview
  execute
  undo_or_recover
  event_schema
  accessibility_summary
```

Hard requirement: shortcuts, menu items, command-palette entries, agent tool
calls, and UI buttons must be aliases or renderings of a `Command` value, not
separate handlers.

Do not add Nomi UI controls beyond toy demos until this packet exists.

### 2. Explanation Must Become The Product Spine

`explain` cannot be a late command. It must be the common substrate for:

- diagnostics;
- failed constraints;
- decode paths;
- query plans;
- block policy traces;
- UI progress;
- notebook stale state;
- accessibility summaries;
- agent action logs;
- undo/replay.

Enhancement note:

```text
Event:
  id
  parent_id
  phase
  feature
  operation
  source_span
  value_summary
  capability
  failure_kind
  redaction
  next_step
```

Binding constraints now emit the first real event family. Good. The next event
families should be decode, block policy, pipeline, and command execution. Do
not spend effort on prettier diagnostics before the event schema stabilizes.

### 3. Data Boundary Must Absorb Forms, Config, APIs, And UI Controls

Forms and UI controls are not a separate design domain. They are data-boundary
inputs with better affordances.

Enhancement note:

```text
external representation/control
  -> raw value with source path
  -> decode
  -> constraints/defaults/redaction
  -> owned data
  -> event stream
```

The data-boundary packet must cover:

- JSON/CSV/YAML/TOML;
- CLI args and environment;
- OpenAPI/GraphQL/schema import;
- forms and notebook widgets;
- config layering;
- defaults and provenance;
- unknown fields;
- accumulated errors;
- redaction;
- partial success policy.

If each of these becomes its own feature, Nomi will recreate the schema DSL
problem it is trying to avoid.

### 4. UI Is A Projection, But Projection Needs Tests

The phrase "UI is projection" is strong but currently unenforced.

Enhancement note:

Each UI-facing feature must have at least two renderings:

```text
canonical event/data form
human rendering
```

For important features, require four:

```text
CLI text
JSON/event
web/notebook rendering
accessibility/plain-text rendering
```

If a feature only works through a visual graph, gesture, hover, color, or chat
summary, it is not language-ready.

### 5. Agent Interaction Must Be Treated As Unsafe UI

Agents are not magic collaborators in the language semantics. They are
high-variance UI surfaces that can propose commands.

Enhancement note:

```text
prompt -> plan -> command values -> preview/diff -> capability confirmation
       -> execution -> events -> summary
```

An agent should never be the only representation of a change. If a plan cannot
be replayed from commands and diffs, it is not trustworthy.

This matters for Nomi because AI toolability is already central to the repo.
Without a command/event model, agent integrations will grow private behaviors.

### 6. First-Hour Nomi Must Be Smaller

The design currently has too many good ideas for a first-hour experience.
That is not a compliment.

Enhancement note:

First-hour Nomi should teach only:

- values;
- names;
- calls;
- `func`;
- simple arrow functions only when needed for callbacks;
- binding constraints;
- `print`;
- one diagnostic/explain example.

Delay:

- holes;
- `$name`;
- operator sections;
- composition;
- piecewise equations;
- `where:`;
- match expressions;
- block calls;
- data declarations;
- decode;
- result taxonomy;
- UI controls;
- agents.

If the language is good, it will survive a small first hour.

### 7. Feature Packets Need A HCI Row

Every user-facing feature packet should include a "human interface impact"
section:

```text
Text form:
Command-palette name:
CLI rendering:
Notebook/web rendering:
Accessibility rendering:
Agent preview:
Undo/replay:
Capability:
Failure kind:
Long form:
```

This is the practical consequence of considering all human-computer
interfaces. It is not a license to add UI syntax.

### 8. Refuse Premature Visual Programming

Visual programming will be tempting because Nomi has flow plans, explanation,
notebooks, data boundaries, and human-interface research. Resist it.

Enhancement note:

Adopt:

- visual dependency graphs;
- pipeline explain views;
- notebook widgets over bound values;
- command palettes;
- direct manipulation over parameters as a frontend projection.

Refuse:

- visual graph as canonical source;
- gestures with no textual command equivalent;
- agent plans that cannot produce durable artifacts;
- canvas-only diagnostics;
- hidden generated code that cannot be inspected.

### 9. Standard Library Shape Is Now A Language Design Issue

Once Nomi admits shells, APIs, config, UI, notebooks, and agents as evidence,
the standard library becomes central. Syntax alone cannot deliver daily
usefulness.

Enhancement note:

The prelude/stdlib plan should prioritize:

- paths/files;
- text;
- JSON/CSV/TOML/YAML;
- CLI args/env;
- HTTP;
- time;
- subprocess;
- config;
- secrets;
- tables;
- tests;
- command registry;
- diagnostics/explain rendering.

Without boring libraries, Nomi will overcompensate with syntax.

### 10. Capability Honesty Must Include Human Surfaces

The capability matrix already separates parse/lower/run/reduce/explain/docs/
tests/samples/web/notebook. After the HCI pass, the next honest axes are:

- command exposed;
- accessibility rendering;
- agent-previewable;
- undo/replay story;
- capability-declared;
- event-producing.

Do not add all of these as code fields immediately. But feature packets should
start answering them now.

## Hard "No" List

These are ideas Nomi should refuse unless a later feature packet overturns the
decision with tests and reductions:

1. A visual graph as the canonical program representation.
2. Natural-language prompts as executable Nomi source.
3. A forms DSL separate from `data`/`decode`/constraints.
4. A config language that does not reduce to data boundaries.
5. Query syntax before row/group/laziness/explain scopes are specified.
6. UI controls that mutate invisible global state.
7. Gesture-only operations.
8. Agent actions without preview and durable diff/result.
9. Feature-specific failure vocabularies.
10. Examples that require web/notebook UI to understand the core semantics.

## Enhancement Queue

This is the recommended order.

### Packet 1: Explanation Event Schema

Owner: language/runtime/tooling.

Deliverables:

- event record shape;
- redaction model;
- source-span/value-summary fields;
- CLI text rendering;
- JSON rendering;
- accessibility rendering notes;
- binding-constraint event migration note.

Why first: every other surface needs this.

### Packet 2: Data Boundary And Decode

Owner: language/data.

Deliverables:

- `decode` semantics;
- form/control input mapping;
- config merge policy;
- unknown-field policy;
- defaults/provenance;
- accumulated errors;
- redaction;
- examples for JSON, env, CLI, and forms.

Why second: external data is the main everyday boundary.

### Packet 3: Command Values And UI Projection

Owner: tooling/runtime/language.

Deliverables:

- command metadata shape;
- command palette mapping;
- shortcut alias rule;
- agent preview/replay contract;
- undo/recover field;
- capability declaration;
- event output.

Why third: it prevents UI and agent surfaces from becoming private languages.

### Packet 4: Failure Taxonomy

Owner: language/runtime.

Deliverables:

- absence vs pattern failure vs constraint failure vs decode failure vs
  expected `Result` failure vs unexpected exception;
- user-facing names;
- event fields;
- propagation rules;
- examples.

Why fourth: failure vocabulary must be stable before convenience operators
expand.

### Packet 5: First-Hour Nomi

Owner: docs/language/product.

Deliverables:

- tiny tutorial;
- runnable sample;
- diagnostic example;
- exclusion list;
- path to second-hour conveniences.

Why fifth: it keeps ambition honest.

## Acceptance Gates For New Features

No new user-facing feature should be promoted unless it can answer:

1. What normal form owns it?
2. What is the long form?
3. What event does it emit?
4. What failure kind can occur?
5. What capability does it need?
6. How does it render in CLI text?
7. How does it render in JSON/events?
8. How does it render accessibly?
9. How would a command palette expose it?
10. How would an agent preview it?
11. Is it undoable/replayable?
12. What syntax or UI tradition was deliberately refused?

If the feature cannot answer these in one page, it is not ready.

## Final Adversarial Advice

Nomi should stop proving that it has read widely. It has.

Now it must prove taste:

```text
fewer primitives
stricter packets
visible capabilities
one command model
one event model
one data-boundary model
boring first-hour path
```

The best version of Nomi is not the language that includes UI, agents, shells,
spreadsheets, APIs, config, notebooks, and typed data. It is the language that
can look at all of those surfaces and say:

```text
That is a binding.
That is a command.
That is a data boundary.
That is a capability.
That is a flow.
That is a block policy.
That is an explanation event.
That does not belong in the language.
```
