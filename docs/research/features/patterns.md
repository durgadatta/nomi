# Patterns And Choice

> Status: comparative evidence; registered pattern contract remains authoritative.

User pressure: handle every state and inspect structure without leaking
tentative bindings or executing surprising behavior.

| Evidence | Mechanism | Nomi judgment |
| --- | --- | --- |
| [Elm](../languages/elm.md), [OCaml](../languages/ocaml.md) | Closed alternatives | Exhaustive structural match. |
| [F#](../languages/fsharp.md), [Scala](../languages/scala.md) | Active patterns/extractors | Visible classifier call first; no user extractors in core. |
| [Dart](../languages/dart.md) | Object patterns can access getters | Match inert owned structure, not arbitrary host access. |
| [Python](../languages/python.md) | Suite-based structural choice | Keep readable indentation, strengthen coverage contract. |

```nomi
label = match state:
    State.Queued => "waiting"
    State.Assigned(owner) => owner
```

Accepted Nomi distinctions: Bool `if` versus structural `match`; expression
`=>` arms versus statement `:` arms; exact lists/maps unless remainder is
explicit; transactional arm-local captures; pure guards that do not establish
coverage. `_` is only a wildcard. Matching cannot consume streams.

Costs include explicit intermediates for domain views and longer handling of
host objects. A catch-all can hide migration pressure; a compiler should explain
unreachable arms and missing alternatives rather than merely accept broad `_`.

**Experiment:** reuse the existing [registered pattern research](../pattern_matching.md)
and [canonical contract](../../design/pattern_matching.md). Add pressure cases
for failed capture, guarded arms, unknown external tags, and getter adapters.
Do not create a competing coverage algorithm in this survey.

**User-facing gate:** promote only the registered accepted syntax/Surface
contract with source-stable diagnostics and CLI/browser agreement.
[Short target](../../design/targets/patterns.nomi);
[full target](../../design/pattern_matching_target.nomi).
