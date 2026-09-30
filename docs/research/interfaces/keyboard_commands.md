# Keyboard Commands: Meaning Before Gesture

> Status: interface evidence and proposed command contract; no shortcut defaults.

## Evidence And Pressure

VS Code associates commands with contextual keybindings and chords. Emacs
keyboard macros record input sequences. W3C guidance distinguishes focus from
selection and calls for control over character-key shortcuts.
[VS Code bindings](https://code.visualstudio.com/docs/configure/keybindings),
[Emacs macros](https://www.gnu.org/s/emacs/manual/html_node/emacs/Keyboard-Macros.html),
[Keyboard interaction](https://www.w3.org/WAI/ARIA/apg/practices/keyboard-interface/),
[Character shortcuts](https://www.w3.org/WAI/WCAG22/Understanding/character-key-shortcuts.html).

A key chord is a tiny invocation language. Modal operator/motion composition
is a useful further experiment, not a license to copy Vim's entire state model.
Raw key replay may depend on layout, selection, focus, timing, or an IME.
Efficiency for an experienced typist does not establish discoverability.

## Proposed Normal Form

Represent a command by stable ID, typed arguments, target/revision, precondition,
required authority, and completion. A menu, palette, button, keybinding, or
agent can request the same operation. Gesture configuration is adapter metadata,
not grammar. Record semantic commands for replay only when context is explicit;
never serialize capability handles into a macro.

**Adapt:** composable command identity and contextual discoverability.
**Reject:** source-language keywords for editor commands, unremappable global
single-character shortcuts, or macros that silently reacquire authority.
Disabled commands should explain the missing precondition. Focus and selected
domain objects must remain separate concepts.

## Discriminating Experiment

On the GitHub playground compare Run, Stop, Inspect, and Apply Edit through
palette and keyboard paths. Test editor focus, result focus, text selection,
composition input, remapping, and a stopped worker. Every path must reach the
same operation with no duplicate execution. Choose defaults only after checking
Monaco/browser/OS collisions and assistive-technology workflows. The current
`Shift+Enter` cell behavior remains prototype behavior, not a new design decision.
