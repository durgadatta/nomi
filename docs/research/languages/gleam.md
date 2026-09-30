# Gleam

> Status: comparative evidence; scope is the official language tour.

## Observe

Gleam models domain alternatives with custom types and examines alternatives
with case expressions. The official tour presents these as everyday tools,
not advanced metaprogramming.
[Primary references: custom types](https://tour.gleam.run/data-types/custom-types/),
[case expressions](https://tour.gleam.run/flow-control/case-expressions/).

## Judge And Pay

**Adopt** an approachable typed core. **Adapt** its explicit data-and-choice
story to indentation, `data`, and `match`. **Reject** assuming approachability
requires dynamic fallback or multiple callable forms.

Nomi's constraints, effects, decoders, and resources make a larger cognitive
contract than the two mechanisms examined here. The fact that each feature is
defensible individually does not mean their combination is teachable. Gleam
is a useful restraint: a first-hour Nomi lesson should not require the entire
industrial model before a user can model and transform one value.

## Test

Teach the [data](../../design/targets/data.nomi) and
[failure](../../design/targets/failure.nomi) fixtures without generics or task
groups. Record whether beginners can add a variant and handle a rejected
parse. Delay more syntax if the basic recognition paths remain unclear.
See [types/data](../features/types_data.md) and [failure](../features/failure.md).
