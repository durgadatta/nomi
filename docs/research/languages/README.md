# Critical Language Reviews

> Status: comparative evidence, reviewed 2026-09-29; not Nomi specification.

These 44 reviews answer a bounded question: which mechanisms help Nomi keep
local reasoning as a script becomes a package? This is a deliberately selected
comparison set, not a ranking or a complete catalogue of languages. Each page
separates sourced observations from Nomi design judgments and supplies a
concrete falsification exercise. No comparative usability study was run.

Primary documentation was consulted for the cited mechanisms on 2026-09-29.
Version scope matters: Haskell means the 2010 report, C means the C11 committee
draft, Java's cited records changes are a historical specification draft,
Scala means Scala 3, APL means Dyalog, SQL means PostgreSQL, HCL means
Terraform's expression dialect, and Zig's cited master manual is moving.
Uiua's cited release article is historical, not a current feature inventory.
Other unversioned manuals are living references, not pinned conformance data.
Examples in the linked Nomi suite are proposals, not executed comparisons.

| Family | Individual reviews |
| --- | --- |
| Everyday interfaces | [Python](python.md), [Ruby](ruby.md), [JavaScript](javascript.md), [TypeScript](typescript.md), [Bash](bash.md), [PowerShell](powershell.md), [Tcl](tcl.md) |
| Functional composition | [Scheme](scheme.md), [Racket](racket.md), [Clojure](clojure.md), [OCaml](ocaml.md), [F#](fsharp.md), [Haskell](haskell.md), [Elm](elm.md), [Gleam](gleam.md), [Roc](roc.md) |
| Systems and application contracts | [Rust](rust.md), [Go](go.md), [Zig](zig.md), [Swift](swift.md), [Kotlin](kotlin.md), [Scala](scala.md), [Java](java.md), [C#](csharp.md), [Dart](dart.md), [C](c.md), [C++](cpp.md) |
| Concurrent services | [Erlang](erlang.md), [Elixir](elixir.md) |
| Relational and numerical work | [SQL](sql.md), [R](r.md), [MATLAB](matlab.md), [Julia](julia.md), [APL](apl.md), [J](j.md), [BQN](bqn.md), [Uiua](uiua.md), [Wolfram Language](wolfram.md) |
| Configuration and policy | [CUE](cue.md), [Nickel](nickel.md), [Dhall](dhall.md), [Pkl](pkl.md), [Nix](nix.md), [HCL](hcl.md) |

Read the [single feature-by-language matrix](../language_feature_matrix.md)
or its [language-row transpose](../feature_language_matrix.md) for compact
mechanisms and Nomi implications. The [syntax matrix](../syntax_matrix.md)
and [form study](../syntax_forms.md) compare the actual source users read/write;
their separately cited syntax evidence extends these bounded mechanism reviews.
Read [feature comparisons](../features/README.md)
for detailed comparisons along one axis, then [the synthesis](../../design/synthesis.md)
to see how they fit together. [Human-computer languages](../interfaces/README.md)
adds the separate interface dimension, including Excel, keyboard commands,
forms, and diagrams.
The older [families](../families.md) and
[convergences](../convergences.md) remain the compact evidence spine. These
pages deepen that spine at the user's request; they do not revive the old
corpus or introduce another language authority. Decisions still belong in
[the ledger](../../design/decisions.md).

## Review Contract

- **Observe:** state the actual mechanism, not a caricature of the language.
- **Judge:** adopt its semantic idea, adapt its surface, defer it, or reject it
  for Nomi's audience. Rejection is not a verdict on its original audience.
- **Pay:** identify what Nomi loses by making that choice.
- **Test:** name input, observable result, and an experiment that could change
  the judgment. Implementation and usability evidence are still pending.

Work from the [open experiments](../open_questions.md), not from a desire to
copy every interesting feature. Source links support observations; subsequent
recommendations are explicitly Nomi hypotheses.
