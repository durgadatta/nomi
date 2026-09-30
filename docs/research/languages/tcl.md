# Tcl

> Status: comparative evidence; Nomi judgments are hypotheses.

## Observe

Tcl has a small command model with substitution performed before command
dispatch. Braces and quoting control substitution, making evaluation context
a central part of reading a program.
[Primary reference: Tcl language](https://www.tcl-lang.org/man/tcl8.6/TclCmd/Tcl.htm).

## Judge And Pay

**Adopt** the discipline of a small set of composable primitives. **Reject**
making strings and evaluation interchangeable in Nomi's default model.
Interpolation should create text, never execute it, and external command
arguments should be values rather than a freshly parsed program.

Tcl's extensible commands make embedded domain languages economical. Nomi's
closed core sacrifices some of that flexibility and will need explicit,
inspectable scoped tools if ordinary functions prove inadequate. A tiny grammar
is not by itself a tiny cognitive model: the reader must still know when data
becomes code.

## Test

Pass text containing command delimiters through interpolation, a configuration
decoder, and a process argv adapter. Require unchanged data and no evaluation.
For any future scoped DSL, demand an expansion artifact and source locations
before accepting it. See [metaprogramming](../features/metaprogramming.md) and
[tooling](../../design/targets/tooling.nomi).
