# Syntax Forms: Recognition Before Compression

> Status: syntax-first comparative study and experiments; no new Nomi syntax admitted.

Read beside the [syntax matrix](syntax_matrix.md),
[feature-row matrix](language_feature_matrix.md), and
[exact semantic transpose](feature_language_matrix.md). The matrix shows
languages; this view shows **competing forms of the same human act**. Its
foreign fragments use the primary references linked in each language row of
the syntax matrix. They are illustrative source, not executed translations.

The focused [data source forms](data_workflows/source_forms.md) extend this view
with R/dataframes, spreadsheet/M/DAX, scientific and unusual relational systems.
[Execution models](data_workflows/execution_models.md) compare workflow spellings;
the [notation atlas](notation_atlas.md) explores binders, sets, tensor indices and
domain/visual forms. These extensions do not alter the 45-language matrix scope.

Nomi judgments below follow [canonical syntax](../design/syntax.md) and
[the decision ledger](../design/decisions.md). Costs are design hypotheses,
not measured comprehension results. Syntax is more than punctuation: argument
position, omission, layout, scope, evaluation context and edit behavior all
change what a person must reconstruct.

## Form Families

Fragments with `...` omit bodies. A slash between code spans separates
alternatives; it is not a source operator. Foreign glyphs are intentional.

| Human act / Feature | Surface alternatives and examples | What the reader must recover | Nomi form and current judgment | Cost or discriminating test |
| --- | --- | --- | --- | --- |
| [Open a scope](features/binding.md) | Python `if p:` + indentation; Rust `if p { ... }`; Ruby `if p ... end`; Scheme `(if p a b)` | Scope end, statement/expression context, dangling branch | Indented suites; only final `:` opens a block | Compare nested edit/branch moves and a missing delimiter/indent diagnostic. |
| [Continue a line](../design/syntax.md#line-continuation) | Grouping parentheses; infix trailing operator; Bash backslash; Nomi next-line `.` / `\|>` | Does a newline end work or continue an expression? | Visible incomplete expression; no backslash; continuation creates no scope | Copy one stage and insert a comment; inspect formatter repair without changing meaning. |
| [Name a value](features/binding.md) | Python `x = 1`; Rust `let x = 1;`; C `int x = 1;`; Go `x := 1`; CUE `x: 1` | Declaration versus update versus constraint composition | `x = 1`; annotation `x: Int = 1` | Less binding ceremony, but deliberately incompatible with repeated Python assignment. |
| [Change state](features/binding.md) | Rust `let mut`; Kotlin `var`; Scheme `set!`; BQN `←` / `↩`; repeated `=` in Python | Which name can change, and where does history change? | `var n = 0`, then `set n = n + 1` | Two visible markers; compare alias/capture updates, not only an isolated counter. |
| [Assign inside an expression](features/binding.md) | C/BQN assignment expressions versus statement updates | Whether a value-producing expression also changes state | No assignment expression; use an explicit update statement | A named intermediate costs space but makes ordering reviewable. |
| [Define a function](features/functions.md) | Python `def`; Rust `fn`; Go `func`; Julia `f(x) = ...`; Elm `f x = ...` | Declaration versus call/equation, inferred versus public contract | One `func name(params) -> Type:` form; explicit `return` | Extra keyword/return; test scanning a file with definitions and calls together. |
| [Produce the function result](features/functions.md) | Ruby/Julia last expression; Rust tail expression; explicit `return` | Does a final expression return, get discarded, or run only for effects? | Explicit named-function return; lambda expression is its result | Longer tiny helpers; compare an inserted logging statement at the end. |
| [Call with arguments](features/functions.md) | `f(x, y)`; OCaml `f x y`; Scheme `(f x y)`; Wolfram `f[x, y]`; shell `f "$x"` | Argument boundaries, call grouping, value versus command words | `f(x, y)` only; positional before named | More delimiters; predictable nested calls and tooling spans. |
| [Name an argument](features/functions.md) | Nomi `limit=2`; Swift `limit: 2`; OCaml `~limit:2`; PowerShell `-Limit 2`; Julia keyword `;` | Argument label versus local parameter name, delimiter and defaults | `f(x, limit=2)`; names/defaults in abstract function values remain open | Compare callback adapters and reordered policy options, not typography alone. |
| [Anonymous expression](features/functions.md) | Python `lambda x:`; JS `x =>`; Rust `\|x\|`; MATLAB `@(x)`; Scheme `(lambda (x) ...)` | Inputs, arity, capture and result boundary | Always `(x) => expression`, including one input | Extra parentheses; never infer a parameter from `_`, `it`, `$0`, or a slot. |
| [Anonymous multi-step work](features/functions.md) | JS arrow block; Ruby `do` block; Swift trailing closure; Julia `do` call | Arity, return target, retention and invocation count | Name a `func`; statement lambda/block convenience not accepted | Nested builders become longer; whole builder program must justify another form. |
| [Partially apply/compose](features/functions.md) | Haskell `(+ 1)` / `f . g`; OCaml `f x`; Elixir capture `&(&1 + 1)` | Hidden parameter, currying and application order | `(x) => add(x, 1)`; ordinary compose library if needed | More names/calls; compare domain algebra before reopening global composition. |
| [Write a function type](../design/function_contracts.md#candidate-type-spellings) | C pointer declarator; TypeScript `(x: T) => U`; Haskell `T -> U` | Tuple input versus parameter pack, labels, effects, convention | `Fn[[A], B]` versus `func(A) -> B` versus domain protocol: **unaccepted candidates** | Check unary, binary, tuple, defaulted and async examples; punctuation cannot settle call compatibility. |
| [Model a product](features/types_data.md) | Java `record`; Rust `struct`; Kotlin `data class`; structural record literals | Nominal identity, mutability and generated projections | `data User:` + typed fields; `User(name="Ada")` | Named construction costs tokens; generated equality/codec/redaction needs its own contract. |
| [Model alternatives](features/types_data.md) | ML `A \| B of T`; Rust `enum`; Elm custom type; TS discriminated structural union | Closed cases versus open structural shapes or inheritance | Closed `data State:` cases; qualified `State.Running(...)` | Longer qualification; catches migrations only with real coverage checking. |
| [Choose a Boolean value](features/patterns.md) | `p ? a : b`; Python `a if p else b`; ML `if p then a else b`; Ruby `unless` | Condition position, truthiness and branch result | `if p then a else b`; suites use `if` / `else if` / `else` | One Boolean vocabulary; do not mistake surface familiarity for proved learnability. |
| [Choose by structure](features/patterns.md) | Python `case`; Rust `match ... =>`; ML `match ... with ... ->`; Erlang clauses | Capture, guard, exhaustiveness and execution hidden by extractors | `match`; expression arms `=>`, statement arms `:` | Two arm shapes encode value versus suite, not two choice mechanisms. |
| [Decompose a value](features/patterns.md) | JS/Rust destructuring; Dart patterns in declarations; Python starred remainder | Can binding fail? Does decomposition invoke host behavior? | Irrefutable binding only; refutable choice belongs in exhaustive match | More explicit matching; test a list head and a getter-backed host object. |
| [Ignore/remainder](features/patterns.md) | `_` wildcard/placeholder/type hole in different languages; Python `*tail`; JS `...rest` | Ignore value versus invent parameter versus absorb structure | `_` only pattern wildcard; `..tail` / `..rest` only pattern remainders | Refuse ambient meaning reuse even if the parser could distinguish contexts. |
| [Transform many values](features/collections.md) | Python comprehension; C# query; Haskell comprehension; method chain; explicit loop | Item scope, result order, strict/deferred work and callback control | Ordinary map/filter/fold calls; loops for statement/effectful work | Joins and rich builders may be wordier; compare plan calls before query grammar. |
| [Read a pipeline](features/collections.md) | Bash `\|`; PowerShell `\|`; F# `\|>`; method chains | Process/object stream, enumeration, laziness, or argument insertion? | `value \|> call(args)` inserts first argument only | Never imply concurrency, per-element calls, Result propagation or plan execution. |
| [Represent absence](features/failure.md) | Swift `T?`; Kotlin `?:`; JS null/undefined; ML `Maybe`/Option; SQL NULL | Absence versus invalidity; one or several null-like values | `Option[T]`, `none`, `?.`, `??` | More explicit types; keep `()` Unit distinct from absence. |
| [Propagate failure](features/failure.md) | Rust postfix `?`; Zig prefix `try`; Go error pairs; exception `throw` | Caller exit, error conversion, cleanup and ordinary/abnormal channel | Typed Option/Result `?`; explicit `.map_error((e) => Domain.Error(e))` | Boilerplate is visible; nested callback propagation must not jump to its caller. |
| [Validate a boundary](features/decoding.md) | Nickel `value \| Contract`; Pkl `Int(this >= 0)`; CUE `int & >=0`; TS assertion | Static claim, delayed contract, information merge or eager decode? | `age: Int where age >= 0`; explicit `User.decode(raw)` | Predicate is named, failure channels differ, arbitrary schema projection stays partial. |
| [Interpolate text](../design/syntax.md#literals) | Python `f"{x}"`; JS template `${x}`; Ruby `#{x}`; Swift `\(x)`; Tcl substitution | Text creation versus evaluation and escaping | `"{x}"`; raw `r"..."`; doubled braces escape | One interpolation family; test pasted braces and hostile external text. |
| [Own cleanup](features/resources.md) | Python `with`; Go `defer`; Zig `errdefer`; C++ RAII; Ruby block API | Lexical/function lifetime, invocation count, escape and release failure | Dedicated `with`; lexical unconditional `defer`; fallible run_scope API proposed | No universal policy block; source sugar waits on whole-completion typing. |
| [Suspend/start work](features/concurrency.md) | Rust suffix `.await`; JS/Swift prefix `await`; Go `go`; actor send; task constructors | Suspension versus start versus child lifetime | `async func`, `await`, `async with` group; cold calls | Short familiar syntax does not prove host cancellation or bounded queue memory. |
| [Describe requirements](features/effects.md) | Effectful function name convention; IO action type; runtime permission handles | Requirement declaration versus actual authority | Public `uses FileRead, Network`; host grants separately | Signature length pays for visible authority; do not encode every path in grammar. |
| [State numeric intent](features/numerics.md) | C/Java suffixes; Rust typed suffixes; MATLAB `.*`; Julia dotted broadcast; APL rank | Representation versus literal spelling; matrix versus elementwise work | Ordinary literals and domain library calls; defaults/array notation remain open | Shape/overflow/rounding laws must precede compact notation. |
| [Select a module](features/modules_tooling.md) | `import`; `use`; `require`; file include; Nix expression import | Binding versus textual inclusion versus evaluation/dependency resolution | Immutable imports; `pub` exposes declarations; manifests pin identity | No wildcard import; discovery must not execute module bodies. |
| [Extend notation](features/metaprogramming.md) | Racket macro; C preprocessor; Wolfram rewrite; HCL dynamic block | Binding hygiene, source provenance and authority | Ordinary values/calls first; scoped syntax deferred | Longer domains earn new notation only with expansion, formatting and diagnostics. |
| [Edit a computation through a view](interfaces/spreadsheets.md) | Excel formula bar, relative/absolute refs, named tables | Location versus identity, input versus derived value, stale result | Named source/model plus read-only projection first | Row sorting/copying must not silently redirect a reference or replay an effect. |
| [Invoke by gesture](interfaces/keyboard_commands.md) | Chord, palette, button, recorded key sequence | Context/focus, command identity, arguments and authority | Stable semantic command metadata outside source grammar | Test remapping/IME/focus collisions; raw keystroke replay is not semantic replay. |

## Punctuation Is Not A Universal Dictionary

| Token | Foreign recognition collisions | Nomi family | Counterexample to audit |
| --- | --- | --- | --- |
| `=` | Assignment, equation definition, named argument, configuration field | Create/default/name a value, never update an existing binding | A second `x = ...` must not quietly mutate. |
| `:` | Type separator, block opener, Nix lambda, shell punctuation | Type annotation or final suite opener, each context explicit | A continued declaration must not create an extra scope. |
| `->` | Lambda body, match arm, member access, function result | Function result type only | `(x) -> x + 1` is not a second lambda form. |
| `=>` | JS/C# lambda, ML/actor alternatives, a type-function arrow | Explicit inputs/pattern map to one expression | A statement arm uses `:`, not an invisible expression block. |
| `?` | Optional type, ternary, error propagation, attribute default/test | Option/Result propagation only | `T?` is not an alternate Nomi Option declaration. |
| `\|` | Shell/object pipe, union type, contract application, lambda bars | Pattern alternatives only | `A \| B` is not an admitted untagged type union. |
| `_` | Ignore, placeholder parameter, wildcard, inferred type, identifier convention | Pattern wildcard only; identifiers may still contain underscores | `map(xs, _ + 1)` is not a generated lambda. |
| `..` / `...` | Range, spread, rest, omitted grammar/body | `..` pattern remainder only | A documentation ellipsis must not be mistaken for runnable target syntax. |
| `{}` | Block, record, set, interpolation, namespace, implicit graph | Map literals/text interpolation, not a second suite or object grammar | Copying a foreign brace callback must not silently turn a value into code. |

## Beginner: Compare Whole Shapes

These original tiny examples expose one local transformation. They are not a
claim that all numeric/default/overflow semantics agree. Primary function
references are in [the matrix](syntax_matrix.md).

Python, explicit named form plus expression callback:

```python
def add_tax(amount, tax):
    return amount + tax

with_tax = lambda amount: add_tax(amount, 2)
print(with_tax(10))
```

OCaml, curried named form plus an explicit adapter:

```ocaml
let add_tax amount tax = amount + tax
let with_tax = fun amount -> add_tax amount 2
let result = with_tax 10
```

Rust, brace/tail-return form plus closure:

```rust
fn add_tax(amount: i32, tax: i32) -> i32 {
    amount + tax
}

fn main() {
    let with_tax = |amount| add_tax(amount, 2);
    println!("{}", with_tax(10));
}
```

Nomi, accepted surface shape; not currently runnable target conformance:

```nomi
func add_tax(amount: Int, tax: Int) -> Int:
    return amount + tax

with_tax = (amount) => add_tax(amount, 2)
print(with_tax(10))
```

**Reader task:** mark definition, inputs, call, result, capture, and output.
Then add a second statement and a shadowed local. Do not score characters
alone; record wrong return/capture/argument predictions. A result shown by a
playground must remain tied to that source revision.

## Production: Public Boundary At Real Widths

The following Nomi shape uses accepted syntax and **proposed** decoder/error
APIs. It returns typed expected errors; it is not an implemented service.

```nomi
pub func register(raw: Value) -> Result[User, AppError] uses Database:
    input = Signup.decode(raw)
        .map_error((errors) => AppError.Decode(errors))?
    user = User(name=input.name, email=input.email)
    return users.insert(user)
        .map_error((error) => AppError.Store(error))
```

Assume declared nominal AppError.Decode/Store payloads and matching proposed
codec/store signatures; the function does not manufacture these contracts.
This continuation style creates no scope. The reader can see raw input,
ownership conversion, error mapping, domain construction and database work.
The cost is repeated mapping and helper names.

For longer signatures, compare this 80-column-safe layout with a wider
rendering; both use the same source contract:

```nomi
pub func register(
    raw: Value,
    tenant: TenantId,
    policy: RegistrationPolicy,
) -> Result[User, AppError]
uses Database, Clock:
    ...
```

Here `...` is an omitted body for the layout study, not runnable code. Do not
invent an additional contract/decorator block solely to fit a line. Compare
call sites with policy names against positional Boolean arguments. Test a
formatter at 80/100 columns, hover over each callback and ask where `?` returns.
Formatter output has not been generated; these are paper candidates.

Function-value syntax remains a genuine unresolved fork. Compare the existing
[three callback type candidates](../design/function_contracts.md#candidate-type-spellings)
using unary, binary and one-tuple inputs, optional/named parameters, required
effects and latent task work. Their meaning must be specified before a preferred
spelling is admitted; this atlas does not choose one by appearance.

## Failure-Heavy: Invocation Count And Lifetime

First write the ordinary callback form from the
[resource proposal](../design/resource_lifetime.md), with its proposed library
contracts and unclosed region/type gates kept explicit:

```nomi
func read_body(reader: Reader) -> Result[Text, IoError] uses FileRead:
    return reader.read_all()

pub func read_text(path: Path) -> Result[Text, ScopeFailure[IoError]]
uses FileRead:
    return run_scope(files.reader_resource(path), read_body)
```

This is not an accepted fallible-`with` desugaring. Compare it with Python's
context-manager form, Ruby's file block, Go's function-scoped defer and C++
RAII **as different lifetime contracts**, not cosmetic equivalents. Nomi's
`with` is already reserved for exactly-once resource scope; it is not a
multi-invocation callback or a retry form.

```nomi
response = retry(() => http.get(url), attempts=3)?
```

The retry API is illustrative: an explicit zero-argument function makes repeated
invocation possible without hiding the inputs. It still needs authority/error
and async contracts. For each contender ask: who invokes, how often, who owns
the return, what happens on cancellation, can an error payload retain the
reader, and where is a failed release shown? No notation wins merely by hiding
those answers behind one block keyword.

## Bounded Next Comparisons

These route to existing questions, not a new independent backlog:

| Existing owner | Inputs to the syntax experiment | Required observable distinction | Removal criterion |
| --- | --- | --- | --- |
| [Constraint surface](open_questions.md#1-constraint-surface) | Field, cross-field rule, long predicate/note, invalid external field | Type/predicate/value/note spans plus declaration/input locations | Reject a shorter form if readers misidentify the checked value or failure channel. |
| [Callback contract](../design/function_contracts.md) | Unary, binary, tuple argument, defaults/labels, effectful callback, cold task | Call shape, return target, effects/captures and generic substitution | Reject typography that obscures arity or implies unsupported purity. |
| [Pattern ergonomics](open_questions.md#16-pattern-ergonomics-after-the-core-decision) | Exact map, remainder, qualified case, guarded case | Non-match versus guard rejection versus invariant failure | Keep explicit classifier if shorthand hides computation or coverage. |
| [Tables](open_questions.md#8-tables-and-query-plans) | Join, projection, window, missing match and duplicate row | Row scope plus inspectable plan, no construction-time effects | Reject scoped notation if it saves only characters over calls. |
| [Numeric model](open_questions.md#9-numeric-and-scientific-model) | Scalar, decimal, rank/frame mismatch, unit conversion | Representation/rounding/shape laws before spelling | Reject notation whose meaning depends on the host library. |
| [Representation fork](open_questions.md#17-computational-representations-and-change) | Grid sort, cell fill, stale source, invalid draft, keyboard edit | One authoritative computation and exact edit/dependency identity | Reject projection if comments, IDs, authority or current source are lost. |

No reader trial, formatter comparison, foreign execution or new syntax
admission occurred in this pass. Documentation/transpose checks establish
navigation and equivalence only. Preserve the current prototype and playground
while these examples remain research fixtures outside `samples/`.
