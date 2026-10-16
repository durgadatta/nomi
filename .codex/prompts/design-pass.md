# Design Pass

Use when researching, deciding, or implementing one bounded Nomi language
feature.

Prompt:

```text
Check `config/design_passes.json` before creating notes. If this topic is
registered, run `python3 -m tools.design_passes show <id>` and read its research,
canonical design, focused target, and bridge. If it is new and deserves a
durable focused packet, follow `docs/orientation/design_pass_workflow.md`.

Work in this order:
1. name the user pressure and current pass status;
2. reconcile primary research with the canonical design spine;
3. update the focused target and broad target where the decision has pressure;
4. audit parser, Surface/Core, runtimes, diagnostics, editor, tests, and web;
5. update validation and exact next actions in the registry;
6. refresh the bridge's current evidence, gaps, validation and next actions in
   place; put any necessary project chronology only in HISTORY.md;
7. run `python3 -m tools.design_passes check` and the registered validations.

Do not create a parallel synthesis document, treat a backend as specification,
or promote target-only code into `samples/` before supported execution surfaces
agree.
```
