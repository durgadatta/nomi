# Design Proposal Template

> Status: active process template.
>
> Scope: documentation-only. Use this template when turning a research idea,
> source-language feature, or user pain point into a Nomi design proposal.

## Purpose

Nomi needs a repeatable way to refine language ideas without drifting into
feature collection. A proposal should make the human need, language precedents,
normal-form reduction, diagnostics, and rejection criteria visible before any
implementation work begins.

Use this template for:

- new syntax;
- changes to existing syntax;
- standard-library concepts that may become syntax later;
- data-boundary, failure, block, query, symbolic, or effect designs;
- design disputes where several source languages suggest different answers.

## Proposal Header

```text
Title:
Status: sketch | research | design-needed | library-first | prototype-ready | rejected-for-now | accepted
Author:
Date:
Related docs:
Related issues/commits:
```

Status meanings should match
[Convenience Review And Roadmap](../convenience/review_and_roadmap.md).

## 1. Everyday Need

Describe the ordinary programming pressure in one paragraph.

Good prompts:

- What real task is awkward today?
- Who feels the pain: beginner, scripter, data user, app developer, library
  author, domain expert, AI assistant?
- What does this make easier to read, write, debug, or explain?
- Is this first-hour, everyday, library-author, or future-layer pressure?

Avoid starting with a source-language spelling.

## 2. Example Before Design

Show the code a user wants to write.

```nomi
# desired shape
```

Then show the explicit long form it should reduce to.

```nomi
# normal-form expansion
```

If the long form is unclear, the proposal is not ready for syntax.

## 3. Source-Language References

Compare at least three nearby precedents when possible.

| Source | Feature | What to learn | What not to copy |
| --- | --- | --- | --- |
| Language A |  |  |  |
| Language B |  |  |  |
| Language C |  |  |  |

Use [Language Family Coverage Map](../research/language_family_coverage_map.md)
to avoid missing an obvious tradition.

If the proposal revives an idea from `docs/archive/`, `docs/drafts/`, or a
large research note, answer this archive-promotion checklist:

- What is the durable need after removing the old document's local rhetoric?
- Which active normal form absorbs it?
- Which active doc already covers part of it?
- What is the smallest new decision or example worth promoting?
- What source examples are kept?
- What source examples are rejected?
- What target fixture or tour snippet changes?

## 4. Nomi Normal Form

Mark every normal form involved:

- [ ] Binding
- [ ] Function
- [ ] Pattern
- [ ] Flow
- [ ] Block
- [ ] Absence/result
- [ ] Data boundary
- [ ] Explanation
- [ ] New primitive required

If "new primitive required" is checked, explain why existing normal forms do
not suffice.

## 5. Degree Of Freedom

Classify the proposal using
[Language Degrees Of Freedom](language_degrees_of_freedom.md):

- [ ] Fixed core
- [ ] Surface sugar
- [ ] Library convention
- [ ] Scoped extension
- [ ] Advanced layer
- [ ] Rejected freedom

Explain why this degree is appropriate. Prefer library convention when the
semantics, names, or diagnostics are not yet settled.

## 6. Semantics

Specify the behavior in boring terms:

- evaluation order;
- scope and binding rules;
- success and failure cases;
- interaction with constraints;
- interaction with `none`, `Result`, and exceptions;
- interaction with blocks, returns, loops, and cleanup;
- eager/lazy or plan/value behavior;
- what happens at module boundaries.

Do not rely on "like language X" as semantics.

## 7. Diagnostics And Explanation

For every failure mode, specify:

| Failure | Diagnostic should show | Explanation hook |
| --- | --- | --- |
|  | source span, value, normal form, user message |  |

Ask:

- Can `explain(...)` show the desugared form or trace?
- Does the diagnostic use Nomi vocabulary?
- Can tooling point from expansion back to source?
- What would an AI assistant need to explain this correctly?

## 8. Teaching Story

Write the one-sentence rule a user should remember.

```text
Use ___ when ___.
```

Then write the warning:

```text
Do not use ___ for ___.
```

If this requires many caveats, the proposal may be too broad.

## 9. Alternatives Considered

List rejected designs.

| Alternative | Why it is tempting | Why not |
| --- | --- | --- |
|  |  |  |

Include at least:

- no new syntax;
- library-first version;
- source-language spelling;
- more explicit long form.

## 10. Coherence Checks

- [ ] Reuses an existing normal form.
- [ ] Does not create a second validation, pattern, query, block, or failure
      language.
- [ ] Has one canonical teaching spelling.
- [ ] Keeps advanced behavior fenced if it is not first-layer.
- [ ] Can be explained to a beginner or safely ignored by a beginner.
- [ ] Can be shown by tooling as normal-form expansion.
- [ ] Preserves the decisions in
      [Language Direction And Gap Map](language_direction_and_gap_map.md).
- [ ] Fits at least one fixture in
      [Target Program Fixtures](target_program_fixtures.md).
- [ ] Does not make the larger
      [Target Language Tour](target_language_tour.md) less coherent.

## 11. Documentation Changes

List docs that would need updates:

- `docs/language/language_spec.md`
- `docs/language/language_foundation.md`
- relevant `docs/features/...`
- relevant `docs/convenience/...`
- `docs/language/target_program_fixtures.md`
- `docs/language/target_language_tour.md`
- examples or samples, only after implementation

## 12. Acceptance Bar

Choose one:

- **research-only**: useful source material, no current language target.
- **library-first**: start with functions/data/block policies and examples.
- **design-needed**: promising but semantics or diagnostics are not settled.
- **prototype-ready**: syntax, reduction, diagnostics, and tests are clear.
- **accepted**: update canonical docs and later implement.
- **rejected-for-now**: document why it should not enter the first everyday
  language.

State the next concrete doc action.

## Minimal Proposal Skeleton

For quick notes, use this shorter form:

```markdown
# Proposal: ...

Status:

## Need

## Desired Nomi

## Normal Form

## Source-Language References

## Degree Of Freedom

## Diagnostics

## Alternatives

## Decision
```

The full template should be used before a design becomes canonical.
