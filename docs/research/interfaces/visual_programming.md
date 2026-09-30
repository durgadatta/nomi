# Visual Programs: An Edge Needs A Meaning

> Status: selected visual-interface evidence; not a graph-language proposal.

## Evidence And Pressure

Node-RED documents message objects traveling through nodes. Blockly's generator
contract distinguishes value and statement blocks and emits code with precedence
handling. These are different mechanisms, not one generic visual semantics.
[Node-RED messages](https://nodered.org/docs/user-guide/messages),
[Blockly generators](https://developers.google.com/blockly/guides/create-custom-blocks/code-generation/block-code).

A graph can make dependencies visible; it can also obscure ordering, shared
state, loops, and graph expansion. A connected port does not establish type
correctness or safe resource lifetime. Scratch and LabVIEW remain neighboring
interfaces to test, not independently reviewed implementations in this pass.

## Nomi Normal Form And Placement

A diagram of `map(lines, line_total)` should identify the collection, function,
and resulting value. A sequential pipeline and a dependency DAG are not
interchangeable: edge kinds must say data dependency, event delivery, control
order, or resource ownership. The source's eager left-to-right evaluation is
not replaced by a node scheduler because a view was opened.

Use a typed, source-mapped view before an editable block frontend. An eventual
frontend must produce the same versioned Surface artifacts and diagnostics,
including unsupported constructs, comments, and hygienic generated names.
Do not assume string generation provides that contract.

## Discriminating Experiment

Render a pure invoice pipeline and an effectful import side by side with source.
Ask reviewers to predict evaluation order, reused inputs, and failure exits.
Introduce one fan-out and one cycle. Require edge meaning and an explicit cycle
diagnostic; reject the graph if reviewers infer accidental parallelism. The
playground's existing Pipeline inspection is a route for this work, not evidence
that a live visual programming editor exists.
