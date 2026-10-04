# Pattern Matching

> Status: canonical focused design for target Nomi. It refines the pattern
> sections of `syntax.md` and `semantics.md`; current prototypes do not yet
> conform.

## Pass Packet

- Research: `docs/research/pattern_matching.md`
- Canonical design: `docs/design/pattern_matching.md`
- Focused target: `docs/design/pattern_matching_target.nomi`
- Implementation bridge: `docs/review/2026-07-16-pattern-matching.md`

## Design Goal

Pattern matching answers one question:

```text
Which declared structural situation is this value in, and what immutable
parts does that situation expose?
```

It is not an alternate function-call syntax, parser framework, validation
language, iteration protocol, or general Boolean conditional. `if` chooses on
`Bool`; `match` chooses on structure.

## One Match Form

Value-producing arms map a pattern to one expression:

```nomi
label = match state:
    JobState.Queued => "queued"
    JobState.Running(started_at) => "running since {started_at}"
    JobState.Failed(error) => "failed: {error.summary}"
    JobState.Finished(_) => "finished"
```

Statement arms open blocks:

```nomi
match event:
    Event.Created(item):
        index.add(item)
        audit.record(event)
    Event.Deleted(id):
        index.remove(id)
    Event.Stopped:
        shutdown()
```

One `match` cannot mix `=>` and `:` arms. `=>` always maps to exactly one
expression. A colon arm is statement-only; Nomi does not infer a block's final
value.

There is no `case` keyword. Indentation after `match subject:` already creates
an unambiguous pattern-arm context. There is no inline semicolon form.

## Pattern Grammar

This sketch fixes recognition and precedence; the lossless grammar may use
more nodes for comments and trivia.

```text
match-expression  := "match" expression ":" expression-arm+
match-statement   := "match" expression ":" statement-arm+
expression-arm    := pattern ["when" expression] "=>" expression
statement-arm     := pattern ["when" expression] ":" suite

pattern           := or-pattern ["as" capture]
or-pattern        := primary-pattern ("|" primary-pattern)*
primary-pattern   := wildcard | capture | literal | nominal-pattern
                   | tuple-pattern | list-pattern | map-pattern
                   | "(" pattern ")"
```

The formatter parenthesizes an `as` pattern containing alternatives:

```nomi
(Command.Read(path) | Command.Write(path)) as request
```

## Initial Pattern Set

| Form | Meaning |
| --- | --- |
| `_` | match any value and bind nothing |
| `name` | match any value and bind immutable `name` |
| `none`, `true`, `false`, integer, text, bytes | match a primitive literal using language-defined value equality |
| `Type.Case` | match a zero-payload nominal variant |
| `Type.Case(p1, p2)` | match a nominal variant and its declared payload order |
| `Product(p1, p2)` | match nominal product fields in declared order |
| `(p1, p2)` | match an exact tuple shape |
| `[p1, p2]` | match an exact strict-list shape |
| `[head, ..tail]` | match a strict list and bind one list remainder |
| `{key: pattern}` | match an exact map with literal keys |
| `{key: pattern, ..}` | require listed entries and ignore additional entries |
| `{key: pattern, ..rest}` | require listed entries and capture additional entries |
| `p1 | p2` | match alternatives from left to right |
| `pattern as whole` | also bind the complete matched value |

Float literal patterns are excluded initially because NaN and backend numeric
representations make equality less obvious. Use a pure `when` comparison when
classification by a floating value is genuinely required.

Lowercase unqualified non-keyword identifiers are always captures. Reserved
vocabulary is never a capture. User-defined variants are qualified, so a
reader never has to ask whether `ready` loads a constant or creates a name.
Prelude `Some`, `Ok`, and `Err` may remain unqualified when type inference
makes them unambiguous; `none` is the no-payload `Option` case.

Primitive literal patterns use the same spelling, escape decoding, and value
normalization as expression literals. Text containing interpolation is an
expression and therefore not a literal pattern. Pattern context adds no
single-quoted or backend-native literal dialect. Frontends must share this
codec; matching their lexemes while disagreeing on decoded values is a
conformance failure.

Duplicate captures in one pattern are errors. Nomi does not give repeated names
an implicit equality meaning:

```nomi
# Error: `item` is captured twice.
# Pair(item, item) => item

Pair(left, right) when left == right => left
```

## Collection Shape

Tuple and list patterns are exact unless a list contains one `..` remainder.
`..rest` may appear between a fixed prefix and suffix and captures a strict
list. A bare `..` ignores the remainder. Neither form consumes a `Stream` or
invokes an iteration protocol.

Map patterns are exact unless they contain one `..` or `..rest`. Keys are
compile-time primitive literals, duplicates are errors, and matching never
invokes user equality or lookup code. `..rest` receives a map containing only
unmatched entries.

```nomi
match payload:
    {"kind": "health"} => HealthCheck       # exactly one entry
    {"kind": "user", "id": id, ..} => UserRoute(id)
    {"kind": "batch", ..rest} => BatchRoute(rest)
    _ => UnknownRoute
```

Structural collection patterns apply only to the corresponding strict Nomi
value. A list pattern does not match text, bytes, tuples, arbitrary iterables,
or host objects. A map pattern does not duck-type an object. External objects
first become the closed `Value` representation or cross an explicit interop
adapter.

## Nominal Shape

The initial nominal pattern form is compiler-generated from `data`; it cannot
be replaced by user code. Product and variant fields use declaration order in
patterns, even though multi-field construction uses named arguments. This
keeps patterns compact and makes a declaration-order change a checked source
change.

User-defined extractors, class tests, method-based deconstruction, view
patterns, regex patterns, and match macros are not part of the initial core.
Visible calls can normalize or parse a value before it is matched.

## Attempt And Commit

The subject expression is evaluated exactly once. Each arm follows this
transaction:

```text
structurally test against the already-evaluated subject
-> accumulate tentative immutable captures
-> if structure fails, discard all captures and try the next arm
-> evaluate one optional guard in an arm-local tentative scope
-> if guard is false, discard all captures and try the next arm
-> commit captures to the selected arm scope
-> evaluate that arm only
```

No capture from a failed nested pattern, failed alternative, or rejected guard
is observable. Successful captures do not outlive the selected arm. Match
arms do not fall through.

Structural matching is pure, total, and non-consuming. A malformed runtime
value or broken nominal invariant is a runtime integrity failure, not a
non-match that silently selects another arm.

## Alternatives

Every alternative must bind the same names with compatible types. Alternatives
are structurally attempted left to right. After the first structural success,
the arm guard runs once. Guard rejection proceeds to the next arm; it does not
backtrack into another alternative in the same arm.

This gives effects no foothold in alternative selection and makes evaluation
count fixed. When overlapping alternatives could bind materially different
values, use separate arms to make the policy visible.

## Guards

`when` refines arm applicability after structural matching:

```nomi
match command:
    Command.Run(name) when name != "" => start(name)
    Command.Run(_) => InvalidCommand.EmptyName
    Command.Stop => stop()
```

A guard:

- must have type `Bool`;
- may read pattern captures and immutable outer bindings;
- must be deterministic and have an empty effect set;
- is evaluated exactly once;
- propagates panic rather than treating it as rejection;
- never contributes proof of exhaustiveness.

`when` is not `where`. A guard answers whether an otherwise valid arm applies.
A `where` constraint defines validity for a binding or `data` value. External
validity belongs in `decode`, where independent errors can accumulate.

## Exhaustiveness And Usefulness

Every `match` is exhaustive, including statement-position matches. Nomi never
silently performs no statement because no arm matched.

The checker uses typed pattern-matrix usefulness analysis:

- closed `data`, `Option`, `Result`, `Bool`, tuples, and finite nested
  combinations can be closed by constructors;
- lists and maps can be closed by a complete structural partition or a
  catch-all;
- `Unknown`, explicit `Any`, open host values, and spaces the checker cannot
  prove finite require `_` or a capture arm;
- a guarded arm contributes no coverage; a later unguarded arm must cover its
  structural space;
- or-patterns are expanded for coverage in source order;
- a wholly useless arm is a compile-time error;
- partial overlap is legal because first-match order is explicit policy.

A defensive runtime `NonExhaustiveMatch` diagnostic exists for corrupted IR,
unchecked foreign code, or a compiler defect. It is never normal control flow.

Value arms must produce one compatible result type. A terminating expression
such as `panic(...)` inhabits the required result position without inventing a
value.

## Binding Versus Matching

Bindings may destructure only when the pattern is statically irrefutable for
the source type:

```nomi
(x, y) = point.as_tuple()       # RHS type is exactly (Int, Int)
UserId(raw) = known_user_id     # single-case product data
```

A list head, one variant of a multi-variant type, a literal, or an uncertain
map shape is refutable and therefore illegal on the left of `=`. Use exhaustive
`match` instead. Parameters and `for` targets follow the same irrefutability
rule.

This keeps ordinary binding free of hidden pattern failure. Nomi has no
`if let`, `while let`, `guard let`, `let assert`, pattern-dispatched function
clauses, or refutable parameter shorthand.

## External Values And Decode

Pattern matching may inspect a `Value` to route by shape:

```nomi
match value:
    Value.Map({"version": Value.Number(2), ..}) => Version2.decode(value)
    Value.Map({"version": Value.Number(1), ..}) => Version1.decode(value)
    _ => Err(DecodeErrors.expected("versioned map", value))
```

The pattern does not establish that all fields are valid, apply defaults,
coerce representations, or accumulate field errors. A decoder owns those jobs.
Ordinary non-match is branch selection; decode failure is structured expected
failure with paths and repair information.

## Formatting

The formatter:

- indents every arm one level under `match`;
- aligns neither arrows nor colons with padding spaces;
- keeps a short pattern, guard, and expression on one line;
- wraps a long guarded pattern inside parentheses and keeps `when` with the
  closing pattern line when it fits;
- indents a wrapped arm expression one continuation level after `=>`;
- formats nested collection patterns with ordinary collection rules;
- parenthesizes alternative patterns before `as`;
- never inserts `case` or semicolons.

```nomi
result = match event:
    Event.Message(
        Message.Metadata(source, received_at),
        payload,
    ) when accepts(source, received_at) => handle(payload)
    _ => ignored
```

## Diagnostics

Pattern diagnostics are structured records shared by CLI, editor, notebook,
and browser. At minimum they include source spans, subject type, pattern path,
capture names/types, and a repair.

Required diagnostics include:

- `NonExhaustiveMatch` with witness patterns and insertion location;
- `UselessMatchArm` naming the earlier covering arm;
- `MixedMatchArmKinds` for `=>` and `:` in one match;
- `DuplicatePatternCapture`;
- `AlternativeBindingMismatch` with per-alternative names and types;
- `RefutableBindingPattern` suggesting exhaustive `match`;
- `GuardNotBool` and `EffectfulMatchGuard`;
- `UnsupportedPatternSubject` for stream/host duck matching;
- `UnexpectedMapEntries` in optional match explanation traces, not as an
  ordinary error for an unselected arm.

Pattern attempts are normally quiet. An opt-in explanation trace may distinguish
constructor mismatch, literal mismatch, missing/extra entry, length mismatch,
and guard rejection without turning expected branch selection into errors.

## Surface And Core Contract

Patterns are a dedicated syntax category, not expression nodes reused by
convention. The implementation target has lossless Surface nodes for:

```text
WildcardPattern
CapturePattern
LiteralPattern
NominalPattern
TuplePattern
ListPattern(prefix, rest, suffix)
MapPattern(entries, openness, rest)
OrPattern
AsPattern
```

The experimental Pattern Surface v1 shape is pinned by
[`schemas/pattern_surface.schema.json`](schemas/pattern_surface.schema.json).
Its envelope carries the exact source, one structural root or structured
diagnostics, and half-open UTF-8 byte spans. Exact source owns whitespace,
comments, quoting, and grouping punctuation; grouping widens the enclosed
node's span instead of introducing a semantic pattern kind. Literal lexemes,
nominal payload punctuation, list prefix/rest/suffix shape, and exact/open map
shape remain explicit in the tree.

The v1 producer profile parses one target pattern fragment independently of
the runnable grammar. Lark and Rust must emit the same payload for the shared
positive and negative fixtures in
`prototype/tests/data/pattern_surface/v1.json`. This profile does not admit
target `match` arms or make target pattern syntax executable.

Fixture parity is a lower bound, not proof that every accepted source spelling
is equivalent. Before the schema is promoted, conformance must enumerate the
complete accepted scalar-literal and identifier grammar, validate every
payload against the JSON Schema, and check relational invariants such as child
span containment that JSON Schema cannot express directly.

`Match` records statement/value mode, one evaluated subject, ordered arms,
typed result or `Unit`, source spans, and coverage evidence. Each arm records a
pattern, optional typed pure guard, body, capture frame, and usefulness result.

Core lowering may compile the pattern matrix to tests and projections, but it
must preserve atomic captures, arm scope, first-match order, single guard
evaluation, and source-linked diagnostics. No backend's native match construct
is semantic authority.

## Admission Boundary

New pattern forms must show all of:

1. a recurring program that is materially worse with a visible function call
   and existing patterns;
2. pure, deterministic, non-consuming structural behavior;
3. a decidable or explicitly conservative coverage rule;
4. fixed capture scope and alternative-binding semantics;
5. formatter and structured diagnostic shapes;
6. parity across native, browser, notebook, and editor surfaces;
7. no new alias for refutable choice.

Until then, normalization functions plus closed patterns are the extension
mechanism.
