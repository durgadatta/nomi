# Human-Computer Interface Languages Deep Dive

> Status: source research for Nomi human-computer interface design.
>
> Scope: comparative evidence, not active specification. This file treats
> human-facing computer interfaces as languages: GUIs, forms, menus, command
> palettes, direct manipulation, notebooks, visual tools, accessibility APIs,
> chat/agent surfaces, gestures, and workflow UIs.
>
> Purpose: widen Nomi's design evidence beyond programming languages and
> machine-facing interface languages. Anything a human uses to tell a computer
> what they want is design evidence for Nomi's surface, diagnostics, tooling,
> and explanation model.

## Thesis

Programming language design is a subset of human-computer interaction design.
Text syntax is only one interface for intention. Users also program computers
through:

- forms and validation messages;
- buttons, menus, tabs, palettes, shortcuts, and command bars;
- drag-and-drop, resize handles, direct manipulation, and gestures;
- spreadsheets, notebooks, timelines, node graphs, design canvases, and CAD
  editors;
- dashboards, filters, saved views, query builders, and workflow automations;
- shells, launchers, search boxes, chat prompts, and agent task panes;
- accessibility trees, keyboard focus order, screen-reader announcements, and
  voice control.

These are not all "programming languages" in the academic sense. They are
interaction languages. They have vocabulary, grammar, feedback, state,
permissions, errors, undo, composition, discoverability, and social norms. Nomi
should learn from them without becoming a visual programming system.

The design goal:

```text
human intention
  -> visible affordance or text form
  -> structured command/value/event
  -> validation and capability boundary
  -> reversible action or durable program
  -> explanation trace
```

Nomi should treat every UI surface as a possible projection of the same
semantic core, not as a separate mode with private behavior.

## Source Scan

Primary and near-primary sources used for this pass:

- W3C WCAG overview:
  <https://www.w3.org/WAI/standards-guidelines/wcag/>
- W3C WCAG 2.2 recommendation:
  <https://www.w3.org/TR/WCAG22/>
- W3C WAI-ARIA:
  <https://www.w3.org/TR/wai-aria-1.2/>
- HTML Living Standard, forms:
  <https://html.spec.whatwg.org/multipage/forms.html>
- W3C Pointer Events:
  <https://www.w3.org/TR/pointerevents/>
- Apple Human Interface Guidelines:
  <https://developer.apple.com/design/human-interface-guidelines/>
- Material Design interaction and components:
  <https://m2.material.io/design/interaction/gestures.html>
  and <https://developer.android.com/design/ui/mobile/guides/components/material-overview>
- Microsoft Fluent Design:
  <https://fluent2.microsoft.design/>
- Nielsen Norman Group usability heuristics:
  <https://www.nngroup.com/articles/ten-usability-heuristics/>

Adjacent Nomi sources already covering parts of this space:

- [interactive_explanation_deep_dive.md](interactive_explanation_deep_dive.md)
  for notebooks, live editors, dependency graphs, and explanation views.
- [overlooked_language_design_dimensions.md](overlooked_language_design_dimensions.md)
  for accessibility, source text, localization, migration, and governance.
- [orthogonal_language_feature_coverage.md](orthogonal_language_feature_coverage.md)
  for accessibility, editor UX, diagnostics, observability, and tooling.
- [ai_readable_semantics_deep_dive.md](ai_readable_semantics_deep_dive.md)
  for machine-readable semantics, LSP, semantic tokens, code actions, and
  structured traces.
- [everyday_interface_languages_deep_dive.md](everyday_interface_languages_deep_dive.md)
  for shells, spreadsheets, selectors, APIs, and workflow systems.

## 1. UI As Language

### 1.1 Vocabulary

Every interface names actions and objects:

- `Save`, `Open`, `Run`, `Preview`, `Undo`, `Filter`, `Sort`;
- fields such as `Email`, `Date`, `Output path`, `API key`;
- states such as selected, disabled, pending, dirty, stale, failed, synced;
- roles such as button, textbox, menu item, tab, dialog, alert, slider;
- gestures such as tap, press, drag, pinch, scrub, hover, focus, type.

In Nomi terms, this is **binding + command + capability metadata**. A UI label
is a surface name for a semantic operation. If the operation cannot be named in
the event model, it is not explainable.

Nomi design consequence:

```text
UI action label -> command value -> capability check -> semantic event
```

### 1.2 Grammar

Interfaces define legal sequences:

- a form field is filled before submit;
- a menu opens before an item is chosen;
- drag starts, moves, then drops or cancels;
- a wizard advances step by step;
- a command palette filters commands, then executes one;
- a notebook cell edits, runs, becomes stale, reruns, exports;
- an agent task asks, confirms, executes, reports, and can be interrupted.

These are not just UI details. They are control-flow policies. Nomi should see
them as **block policies and state transitions**, not as ad hoc frontend code.

Nomi design consequence:

```text
interaction sequence -> block policy -> events -> undo/replay/explain
```

### 1.3 Feedback

Good interfaces continuously answer:

- What is possible?
- What happened?
- What is happening now?
- What failed?
- What can I do next?
- What will be affected if I continue?

This maps directly onto Nomi's explanation normal form. A diagnostic is a UI
event. A progress indicator is a UI event. A stale notebook cell is a UI event.
A disabled button is a UI event plus a reason.

Nomi design consequence:

```text
semantic event -> text diagnostic | UI state | accessibility announcement
```

## 2. Interface Families

### 2.1 Forms And Validation

HTML forms, app forms, settings panels, API consoles, checkout flows, and admin
dashboards are declarative binding systems:

- field name;
- expected type;
- allowed values;
- default;
- required/optional status;
- validation;
- error message;
- privacy and redaction policy;
- submit action;
- disabled/loading/success/failure state.

What works:

- constraints near the field;
- immediate but non-hostile feedback;
- preserving user input after failure;
- clear required/optional states;
- autocomplete and defaults where provenance is visible;
- summary errors plus per-field errors;
- keyboard and screen-reader operability.

What fails:

- validation only after submit;
- generic "invalid input" messages;
- hidden normalization;
- formatting requirements not shown until failure;
- disabled controls without a reason;
- silently dropping partial user input;
- visual-only error indication.

Nomi normal form:

```text
field -> binding target -> decode/constraint -> diagnostic + provenance
```

Nomi should treat forms as an external-data boundary. A form submit is a
`decode` operation with source paths and user-facing blame.

### 2.2 Menus, Command Palettes, And Shortcuts

Menus and palettes are discoverable command languages. They expose a vocabulary
without requiring the user to remember exact syntax.

What works:

- commands have stable names;
- commands are searchable;
- disabled commands expose why they are unavailable;
- shortcuts are accelerators, not the only path;
- commands can be previewed, undone, and repeated;
- command history is visible.

What fails:

- hidden command modes;
- same shortcut meaning different things by subtle focus context;
- destructive actions without review;
- command names that describe implementation rather than user intention;
- macros recorded as opaque UI events that cannot be inspected.

Nomi normal form:

```text
command palette item -> named function/block policy -> explainable event
shortcut -> alias for command, not separate semantics
```

Nomi should eventually let tooling expose language operations through command
palettes, but the command must reduce to a normal Nomi action.

### 2.3 Direct Manipulation

Direct manipulation interfaces let users act on visible objects: drag a file,
resize a shape, scrub a number, reorder a list, connect nodes, draw a selection
box, pan a canvas.

What works:

- visible object, visible affordance, immediate feedback;
- reversible operations;
- snapping and constraints that can be inspected;
- handles expose degrees of freedom;
- operations can be represented as commands after the gesture.

What fails:

- gestures with no textual equivalent;
- precision hidden behind pointer skill;
- state changes that cannot be reviewed, diffed, or scripted;
- no keyboard alternative;
- undo stacks that collapse many semantic actions into one vague step.

Nomi normal form:

```text
gesture -> command value -> constraint/policy -> event stream -> undo record
```

Nomi should not copy gestures into syntax. It should make traces rich enough
that frontends can offer gestures over values, flows, and parameters.

### 2.4 Notebooks, Cells, And Live Views

Nomi already studies Jupyter, Pluto, Observable, Light Table, Swift
Playgrounds, and Bret Victor-style live programming. The broader UI lesson is
that a notebook is not just "code plus prose." It is an interaction language
with cells, dependency order, stale state, rich outputs, controls, export, and
sharing.

What works:

- cell as named transformation;
- visible dependencies;
- stale output markers;
- inline values and rich media;
- widgets as bound values;
- export to a reproducible artifact.

What fails:

- hidden execution order;
- outputs that lie about current state;
- UI controls that mutate global state invisibly;
- irreproducible notebooks tied to proprietary hosted state.

Nomi normal form:

```text
cell/input widget -> binding/flow node -> dependency graph -> explanation
```

Nomi should make notebook cells and widgets views over bindings and flows, not
a second execution language.

### 2.5 Visual Programming And Node Graphs

Scratch, LabVIEW, Unreal Blueprints, Blender geometry nodes, dataflow tools,
workflow builders, Zapier-like automations, and design tools show that visual
programming is powerful when the domain is spatial, sequential, or dataflow
oriented.

What works:

- concrete domain objects are visible;
- connections show dependency;
- nodes can expose typed ports;
- non-programmers can assemble workflows;
- visual layout carries domain meaning.

What fails:

- large graphs become harder to scan than text;
- copy/paste, diff, review, merge, and abstraction are weaker;
- visual geometry becomes accidental semantics;
- hidden generated code cannot be trusted;
- accessibility and keyboard navigation are often poor.

Nomi normal form:

```text
node graph -> flow plan/module graph -> textual normal form + visual view
```

Nomi should refuse visual programming as the primary language, but adopt visual
views over flow plans, dependency graphs, traces, and data pipelines.

### 2.6 Design Canvases, CAD, Timelines, And Media Tools

Figma, Sketch, Illustrator, CAD systems, DAWs, video editors, animation
timelines, and game editors are high-bandwidth languages for spatial and
temporal intent.

What works:

- layers, groups, constraints, guides, snapping, keyframes, and timelines;
- inspectors expose selected-object properties;
- operations are reversible and previewable;
- object identity persists across edits;
- constraints can be manipulated visually.

What fails:

- plugin/script models diverge from manual editing semantics;
- generated assets become hard to diff;
- hidden layout constraints surprise users;
- history is linear while the artifact is structured.

Nomi normal form:

```text
artifact object -> data value
inspector edit -> constrained binding update
timeline/keyframe -> ordered event/value series
```

The lesson for Nomi is not "be a design tool." The lesson is that data,
constraints, and time-shaped events need inspectable identities.

### 2.7 Search, Launchers, And Query Boxes

Search boxes and launchers are forgiving text languages. Users type partial
intent, not exact syntax. Examples include Spotlight, browser address bars,
IDE symbol search, command palettes, database filters, and app-wide search.

What works:

- partial matching;
- ranking with visible categories;
- correction and disambiguation;
- preview before action;
- history and saved searches;
- plain-text fallback.

What fails:

- ranking that changes without explanation;
- executing destructive actions from ambiguous text;
- no way to inspect the parsed query;
- search syntax that differs across every product surface.

Nomi normal form:

```text
loose query -> parsed intent candidates -> preview -> explicit command
```

Nomi tooling should support fuzzy discovery, but program semantics should not
depend on fuzzy parsing.

### 2.8 Chat, Prompts, And Agent Interfaces

Chat interfaces are becoming a general computer-use surface. They combine
natural language, commands, file context, tool calls, confirmations, and
execution traces.

What works:

- low barrier to expressing intent;
- conversational clarification;
- generated plans and diffs;
- tool-call summaries;
- interrupt/resume;
- ability to explain why an action was taken.

What fails:

- ungrounded confidence;
- hidden context selection;
- tool actions without preview;
- state changes not captured as durable artifacts;
- natural language treated as a reliable program;
- inability to replay, diff, or audit.

Nomi normal form:

```text
prompt -> proposed plan -> typed command values -> capability confirmation
       -> execution events -> durable diff/result
```

Nomi should make agent interaction a first-class tooling surface, not a source
language. A prompt can propose code, commands, or plans, but the committed
artifact must be inspectable Nomi, structured data, or explicit host action.

### 2.9 Accessibility Interfaces

Accessibility is not an afterthought UI layer. Screen readers, keyboard focus,
ARIA roles, captions, text alternatives, switch control, voice control, high
contrast, reduced motion, and semantic landmarks are parallel interfaces to
the same computation.

What works:

- semantic roles and names;
- focus order matching task order;
- keyboard alternatives;
- text alternatives for visual output;
- error messages tied to fields;
- live regions and status announcements;
- no information conveyed only by color, hover, or spatial position.

What fails:

- visual-only diagrams;
- unlabelled controls;
- canvas UIs without semantic mirrors;
- focus traps;
- hover-only help;
- gesture-only operations;
- generated explanations that cannot be read linearly.

Nomi normal form:

```text
semantic event/value -> accessible text/tree representation
```

Every Nomi explanation surface should have a plain-text and structured form.
If a visual trace cannot be rendered as text/JSON, it is not the canonical
trace.

### 2.10 Games, Simulations, And Interactive Worlds

Games and simulations teach feedback, onboarding, discoverability, and state.
They are full of interaction languages: movement, inventory, menus, maps,
quests, tutorials, physics constraints, save/load, and replay.

What works:

- tutorial through doing;
- immediate feedback;
- safe failure and retry;
- clear state transitions;
- progressive disclosure;
- replay and ghost views.

What fails:

- hidden rules;
- irreversible early mistakes;
- unclear affordances;
- state that cannot be inspected;
- tutorial text disconnected from action.

Nomi normal form:

```text
interaction loop -> state transition -> event log -> replay/explain
```

The lesson is that Nomi's teaching surface should be interactive and
recoverable, not just a static syntax tour.

## 3. Cross-Interface Invariants

Across human-facing interfaces, the same invariants keep appearing.

### 3.1 Affordance

Users need to see what actions exist. In code, syntax and names are
affordances. In tooling, command palettes, completion, examples, and inline
diagnostics are affordances.

Nomi rule:

```text
No important operation should exist only as folklore.
```

### 3.2 Feedback

Every action should produce a visible, structured result: value, effect,
diagnostic, progress, cancellation, or no-op reason.

Nomi rule:

```text
Every semantic step can emit an event.
```

### 3.3 Reversibility

Undo is the UI form of local reasoning. If a change cannot be undone or
replayed, users need stronger preview and confirmation.

Nomi rule:

```text
World-changing operations need capability, preview, event, and recovery story.
```

### 3.4 Discoverability And Progressive Disclosure

Good interfaces let beginners start without hiding the path to expert use.

Nomi rule:

```text
Long form first, short form second, command palette/examples always.
```

### 3.5 State Visibility

Invisible state is the root of many UI and language failures: stale notebook
cells, hidden global variables, mutable UI selections, current working
directory, active database connection, selected object, clipboard, focus.

Nomi rule:

```text
Ambient state must either be explicit context or explainable capability state.
```

### 3.6 Accessibility And Alternate Renderings

An interface is not complete if it works only through one sensory or motor
channel.

Nomi rule:

```text
Canonical semantics are text/JSON/event data; visuals are projections.
```

### 3.7 Inspection Before Automation

Users trust automation when they can inspect the intended action before it
runs and inspect the result after it runs.

Nomi rule:

```text
Agent/tool automation produces plans, diffs, events, and durable artifacts.
```

## 4. Anti-Patterns

### 4.1 UI-Only Semantics

If the UI can do something that cannot be represented in code, data, or events,
the UI has become a hidden language.

Refuse:

```text
manual operation -> invisible special case
```

Adapt:

```text
manual operation -> command value -> event -> optional generated Nomi
```

### 4.2 Text-Only Elitism

If the language ignores visual, interactive, and accessible representations, it
will make simple exploration unnecessarily hard.

Refuse:

```text
source text is the only legitimate interface
```

Adapt:

```text
source text is canonical; UI views are faithful projections
```

### 4.3 Mode Confusion

Modes are dangerous when users cannot see which grammar is active: insert vs
normal mode, selection mode, command mode, edit mode, notebook hidden state,
agent planning vs executing.

Nomi should make modes explicit in diagnostics, prompt/tool UI, notebooks, and
feature profiles.

### 4.4 Confirmation Fatigue

Not every action needs a modal confirmation. What matters is risk:

- reversible local edit: no confirmation;
- destructive world action: preview and confirm;
- expensive action: estimate and cancel;
- sensitive action: capability and redaction;
- ambiguous action: clarify first.

This maps to block policies and host capabilities.

### 4.5 Private Failure Vocabulary

Forms say "invalid." APIs say "400." Shells say exit 2. Widgets turn red.
Agents say "I had trouble." These should not be separate failure languages.

Nomi should use one failure taxonomy and render it differently for each UI.

## 5. Adopt / Refuse / Adapt

| Source idea | Nomi decision | Rationale |
| --- | --- | --- |
| Forms as field constraints | Adopt | They map directly to binding targets, decode, provenance, and diagnostics. |
| UI controls as mutable globals | Refuse | Controls should bind values or commands through visible state. |
| Command palettes | Adopt | They expose the operation vocabulary without adding syntax. |
| Shortcuts as separate semantics | Refuse | Shortcuts are aliases for commands, not their own language. |
| Direct manipulation | Adapt | Use gestures as frontend projections that emit command values/events. |
| Visual programming as primary language | Refuse | Text remains canonical for diff, review, abstraction, accessibility, and tooling. |
| Visual flow/dependency views | Adopt | Flow plans, notebooks, and traces benefit from graphical projections. |
| Notebook widgets | Adapt | Widgets are bound values with dependency edges, not hidden side effects. |
| Accessibility tree | Adopt | Explanation events need accessible text/structured renderings. |
| Natural-language prompts as code | Refuse | Prompts may propose plans, but committed artifacts must be explicit. |
| Agent task panes | Adapt | Agents produce inspectable plans, diffs, capability requests, and events. |
| Undo/redo doctrine | Adopt | Reversibility is a semantic design pressure, not just editor polish. |
| Fuzzy search | Adapt | Use for discovery; never make program meaning depend on fuzzy parsing. |
| Gesture-only actions | Refuse | Every gesture needs keyboard/text/command equivalent. |
| Live preview | Adopt | Preview is an explanation view over values, effects, and traces. |

## 6. Nomi Design Consequences

### 6.1 UI Is A Projection Layer

Nomi should define source text, notebooks, playground controls, diagrams, REPLs,
command palettes, and agent panes as projections over the same semantic data:

```text
Surface/Core/value/event/capability -> renderer
```

Renderers can be textual, visual, accessible, notebook, web, CLI, or agentic.
They must not introduce private semantics.

### 6.2 Controls Bind Values

Sliders, checkboxes, dropdowns, date pickers, file pickers, color pickers, and
text fields should be modeled as bindings with constraints and provenance:

```nomi
threshold: float, 0 <= threshold <= 1 = ui.slider(0.5)
```

This is a design direction, not a syntax commitment. The important normal form
is:

```text
control -> binding -> constraint -> event -> recompute dependents
```

### 6.3 Commands Are Values

UI commands, CLI commands, command-palette entries, and agent tool calls should
share one inspectable shape:

```text
Command:
  name
  inputs
  capabilities
  preview
  run
  undo/recover
  event schema
```

This supports undo, permissions, explanation, keyboard shortcuts, menus, and
agent plans without separate code paths.

### 6.4 Explanation Has Multiple Renderings

The same explanation event stream should render as:

- CLI text;
- JSON;
- notebook cell annotations;
- web playground panels;
- screen-reader-friendly summaries;
- visual graphs;
- agent progress summaries.

The event stream is canonical. The UI is a view.

### 6.5 UI State Is Capability/Context State

Current file, selected project, active cell, focused value, active profile,
environment, secrets, network access, and working directory should be visible
context, not invisible global state.

```text
active UI context -> explicit capability/context record -> explain
```

### 6.6 Agent Interfaces Need Preview And Replay

An agent interaction is safe when it can be decomposed into:

```text
request -> plan -> proposed commands -> diffs/previews -> capability checks
        -> execution -> event log -> summary
```

Nomi should not treat chat as a magical source language. It is a high-level
proposal surface over explicit artifacts.

## 7. Normal Form Mapping

| UI pressure | Nomi normal form | Design consequence |
| --- | --- | --- |
| Field input | Binding + Data boundary | Forms decode into owned values with field paths. |
| Submit | Call + Capability | Actions name required world authority. |
| Menu command | Function/Block | Command palette entries invoke named operations. |
| Shortcut | Surface alias | Shortcut has no private semantics. |
| Dialog/wizard | Block policy | Multi-step interaction is structured control flow. |
| Drag/drop | Command event | Gesture emits command value and undo record. |
| Slider/scrub | Binding + Flow | Control rebinds a value and recomputes dependents. |
| Notebook cell | Binding + Flow + Explanation | Cell is a named transformation with dependency events. |
| Node graph | Flow plan | Visual graph projects flow values and modules. |
| Accessibility tree | Explanation | Semantic events have alternate renderings. |
| Chat prompt | Tooling/Command proposal | Natural language proposes explicit artifacts. |
| Undo/replay | Explanation + Block | Action events support reversal or reconstruction. |

## 8. Feature Packet Pressure

Human-computer interface research does not immediately add syntax. It changes
the quality bar for future feature packets.

Each user-facing feature packet should answer:

1. What is the textual form?
2. What is the command-palette name?
3. What is the form/control equivalent, if any?
4. What event is emitted?
5. How is failure rendered in CLI, notebook, web, and accessibility output?
6. What state does it read or write?
7. Is it undoable, replayable, or world-changing?
8. What capability does it require?
9. How would an agent preview and execute it?
10. What is the long form a user can inspect?

If a feature cannot answer these, keep it in research or library form.

## 9. Immediate Nomi Directions

### 9.1 Explain As The Universal UI Backend

`explain` should not be only a text command. It should be the backend for:

- diagnostics;
- notebook stale-state markers;
- visual dependency graphs;
- CLI progress output;
- accessibility announcements;
- agent summaries;
- debugger timelines;
- command previews.

### 9.2 UI Controls As Bound Values

When Nomi grows notebook/web controls, they should begin as bound values with
constraints, not as ad hoc callbacks.

### 9.3 Command Registry Before More UI

Before building many UI affordances, Nomi needs a command registry or equivalent
metadata surface where operations declare:

- name;
- inputs;
- feature owner;
- capability;
- status;
- event output;
- docs/tests.

This is similar to feature manifests but user-facing.

### 9.4 Accessibility Acceptance Rules

Every explanation, diagnostic, playground control, and notebook output should
have:

- plain-text rendering;
- structured JSON/event rendering;
- keyboard path;
- no color-only meaning;
- source/value references that do not depend on visual layout alone.

### 9.5 Agent-Readable And Human-Readable Are The Same Direction

Machine-readable semantics help agents, but they also help humans:

- source spans support hover and screen-reader references;
- typed events support diagnostics and progress panels;
- capability metadata supports security prompts;
- command values support undo, review, and automation;
- examples support teaching and code actions.

The goal is not to optimize for agents over people. The goal is to make the
language's meaning explicit enough that many interfaces can render it honestly.

## 10. Core Decision

Nomi should consider every human-computer interface as design evidence, but it
should not absorb every interface as syntax.

The durable rule:

```text
If humans use it to tell the computer what to do,
study it.

If it can be reduced to binding, function, pattern, flow, block,
data boundary, absence/result, or explanation,
consider it.

If it requires private UI-only semantics,
refuse it or keep it as a frontend projection.
```

