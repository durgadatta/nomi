# Cognitive Integration Boundary Plan

> Status: active consolidation plan.
>
> Scope: documentation-only. This file consolidates language research into
> Nomi integration boundaries, syntax variants, tradeoffs, and example shapes.
> It is not a language specification and does not promote syntax by itself.

## Purpose

Nomi should become a serious, cognitive programming language: readable in the
small, composable in the middle, powerful at the edges, and inspectable when
something fails. The risk is not lack of inspiration. The risk is letting good
ideas from Python, Julia, Ruby, Mathematica, Scheme/Racket, Clojure, Scala,
F#, Nim, R, SQL, APL, and shell become unrelated local features.

This plan keeps the integration rule explicit:

```text
source-language lesson
-> user pressure
-> Nomi normal form
-> integration boundary
-> syntax candidates
-> tradeoff
-> feature packet or refusal
```

Every serious language has escape hatches: macros, metaprogramming, implicit
contexts, DSLs, query planners, type providers, runtime reflection, dynamic
dispatch, notebooks, shells, packages, and foreign calls. Nomi should have
power, but the power must cross visible boundaries.

## Cognitive Ladder

The everyday language should climb without forcing users to switch mental
models:

```text
value
-> name
-> call
-> function
-> checked binding
-> owned data
-> pattern choice
-> readable flow
-> expected failure
-> block policy
-> world capability
-> trace/explain
-> structural/symbolic layer
```

Each rung should be teachable as a local cognitive act:

| Rung | Cognitive act | Normal-form owner |
| --- | --- | --- |
| value | distinguish a thing | binding + data boundary |
| name | make it locally available | binding |
| call | ask behavior to happen | function |
| function | reuse transformation | function |
| checked binding | judge a value at a boundary | binding + explanation |
| owned data | give shape and invariants | data boundary + binding |
| pattern choice | choose by structure | pattern |
| readable flow | transform left-to-right | flow |
| expected failure | keep non-success visible | absence/result |
| block policy | attach caller-side code to a call | block |
| world capability | touch files/network/time/processes visibly | block + explanation |
| trace/explain | inspect what happened | explanation |
| structural layer | talk about code/dataflow as values | explanation + pattern + flow |

## Integration Boundaries

These are the boundaries that prevent Nomi from becoming a feature buffet.

| Boundary | What crosses it | Examples | Required explanation |
| --- | --- | --- | --- |
| Data boundary | external values become owned values | JSON, CSV, env, CLI, HTTP, config | source path, raw value, target field, rule, redaction |
| Failure boundary | non-success becomes typed and inspectable | `none`, `Result`, exception, pattern non-match, constraint failure | failure kind, value, rule, next action |
| Control boundary | caller-side code becomes part of a call | `using`, `retry`, `transaction`, `trace`, `test` | enter, yield, resume, cleanup, cancellation |
| Context boundary | names resolve through an explicit context | row scopes, config scopes, extension imports, capabilities | context owner, lookup path, shadowing rule |
| Structural boundary | code/computation becomes a value | `quote:`, `describe`, query plans, rewrite rules | expansion, source spans, unsupported behavior |
| Host boundary | code touches the outside world | file, network, process, time, random, secrets | capability, authority, effect summary, redaction |
| Backend boundary | a plan runs somewhere else | SQL engine, dataframe engine, JS runtime, Wasm, native backend | capability table, unsupported nodes, result contract |

Default rule:

```text
ordinary code stays direct
powerful context is explicit
every boundary emits inspectable evidence
```

## Additional Source-Language Lessons

The existing research corpus already covers many families. This pass adds a
few sharpened integration lessons from official references and mature language
surfaces:

| Source | Useful lesson | Nomi integration boundary |
| --- | --- | --- |
| F# computation expressions | A single builder protocol can make async, sequence, option/result, and query-like workflows look direct while preserving `Bind`, `Return`, `Using`, and other operations. | Block/result/flow policies should have explicit builders or policy values before syntax expands. |
| F# type providers | External schemas can become typed surfaces, but the boundary to external data must stay visible. | Decode/data-boundary tools may generate helpers, but provenance and failure remain explicit. |
| Clojure transducers | Transformation can be decoupled from concrete collection type and evaluation context. | Collection verbs should be ordinary composable transformations before table syntax hardens. |
| Clojure spec | Validation can also conform, explain, generate examples, and instrument functions. | Constraints should feed diagnostics, examples, and future generation; not just throw errors. |
| Scala 3 extension methods | Method-like surface can translate to ordinary functions with an explicit receiver. | Extension syntax, if admitted, should reduce to function calls and remain import/scoped. |
| Scala 3 context parameters/functions | Context can be passed implicitly but remains a typed language concept. | Nomi should start with explicit context/capability values; scoped implicit context is a later layer. |
| Nim macros/templates | Compile-time syntax transformation is powerful because AST nodes are explicit. | Macro-like power belongs behind `quote:`/syntax values plus expansion traces, not global ambient rewrite. |
| Ruby blocks | Library-authored control feels humane when block shape is ordinary and local. | Block calls are a core Nomi differentiator, but policy events must be inspectable. |
| Mathematica rules | Rewriting is powerful when expressions are uniform and rules are first-class. | Rewrite only over quoted/described values, with explicit strategy and trace. |

Source anchors:

- F# computation expressions:
  <https://learn.microsoft.com/en-us/dotnet/fsharp/language-reference/computation-expressions>
- F# type providers:
  <https://learn.microsoft.com/en-us/dotnet/fsharp/tutorials/type-providers/>
- Clojure transducers:
  <https://clojure.org/reference/transducers>
- Clojure spec:
  <https://clojure.org/guides/spec>
- Scala 3 extension methods:
  <https://docs.scala-lang.org/scala3/reference/contextual/extension-methods.html>
- Scala 3 context parameters:
  <https://docs.scala-lang.org/scala3/reference/contextual/context-parameters.html>
- Nim macros:
  <https://nim-lang.org/docs/manual.html#macros>

## Syntax Variation Packets

These packets are target design material. They show possible forms, tradeoffs,
and integration boundaries. They are not implementation instructions.

### 1. Checked Binding And Data Decode

User pressure:

```text
Make assumptions executable at the place where values enter the program.
```

Variants:

```nomi
# A. Current Nomi direction: compact checked binding
age:int, age >= 13 else "Must be at least 13" = raw_age

# B. Verbose where-clause binding
age:int where age >= 13 else "Must be at least 13" = raw_age

# C. Cast-like form
age = raw_age as int where age >= 13

# D. Decode boundary
payload = Signup.decode(request.json)
```

Tradeoff:

| Variant | Fit | Cost |
| --- | --- | --- |
| A | Reuses assignment and parameter constraint shape; terse enough for daily use. | Dense if many constraints accumulate. |
| B | Reads more like English; easier for first-hour docs. | Adds another local grammar shape unless it reduces to A. |
| C | Familiar from casting languages. | Makes checking look like conversion and hides binding as the owner. |
| D | Best for external data. | Requires `data`/decode feature maturity before first-hour use. |

Recommendation:

- Keep A as the canonical checked-binding direction.
- Allow B only if it is pure sugar over the same binding packet.
- Refuse C as the primary story; conversion is not the same as binding.
- Use D for external input, not ordinary local values.

Integration boundary:

```text
raw value -> binding target -> constraints -> commit or diagnostic event
```

### 2. Patterns, Guards, And Constraint Failure

User pressure:

```text
Choose behavior by shape without leaking partial bindings or hiding failed
checks.
```

Variants:

```nomi
# A. Match with constrained capture
match value:
    case User(name, age:int, age >= 13):
        allow(name)

# B. Guard separates shape from judgement
match value:
    case User(name, age) if age >= 13:
        allow(name)

# C. If-let / guard-let convenience
if User(name, age:int, age >= 13) = value:
    allow(name)
```

Tradeoff:

| Variant | Fit | Cost |
| --- | --- | --- |
| A | One pattern/binding story; captures and constraints compose. | Must explain whether constraint failure is non-match or diagnostic. |
| B | Keeps shape and predicate visually distinct. | Can drift into ad hoc boolean guards with weaker diagnostics. |
| C | Excellent for small optional/pattern checks. | Needs careful binding rollback and value contract. |

Recommendation:

- Treat pattern capture as tentative binding.
- Constraint failure inside match should be case non-match with trace evidence,
  unless the feature packet declares diagnostic-failure mode.
- Add if-let/guard-let only after match semantics are stable.

Integration boundary:

```text
subject -> pattern test -> tentative captures -> guard/constraint
-> case choice + trace
```

### 3. Flow, Tables, And Query Syntax

User pressure:

```text
Make transformations read left-to-right from lists to tables to plans.
```

Variants:

```nomi
# A. Pipeline over ordinary verbs
active =
    users
    |> where(_.active)
    |> select(_.email)
    |> sort

# B. Row-scope shorthand for table values
active =
    users
    |> where(.active)
    |> select(.email)

# C. Query block as sugar
active = query users:
    where .active
    select .email
    sort .email

# D. SQL string
active = sql"select email from users where active"
```

Tradeoff:

| Variant | Fit | Cost |
| --- | --- | --- |
| A | Best first surface; ordinary functions and pipeline explain everything. | Repeated lambdas can become noisy for table work. |
| B | Strong table ergonomics; exposes row context. | Needs explicit context boundary and ambiguity diagnostics. |
| C | Familiar to SQL/data users; can optimize as plan. | Risks becoming a second language unless it lowers to A/B. |
| D | Great interop with SQL engines. | String boundary, injection risk, weak source spans unless typed sink is mature. |

Recommendation:

- A is canonical first.
- B is design-needed for table values with an explicit row context.
- C is future L4 sugar only after verb vocabulary and plan values stabilize.
- D belongs as a typed `Sql` value with parameterization, not the Nomi core.

Integration boundary:

```text
value pipeline -> table context -> logical plan -> backend capability
-> collect/explain
```

### 4. Block Policies And Humane Control

User pressure:

```text
Let libraries express resource, retry, transaction, trace, fixture, and test
patterns without one keyword per policy.
```

Variants:

```nomi
# A. Current block-call direction
using(file(path)):
    text = yield
    print(text)

# B. Python-like with
with file(path) as f:
    print(f.read())

# C. Ruby-style policy block
file(path).using:
    print(read())

# D. Named policy call
retry(times=3):
    fetch(url)
```

Tradeoff:

| Variant | Fit | Cost |
| --- | --- | --- |
| A | One call-plus-block model; library-authored control stays explicit. | Requires users to learn `yield` as the policy/body handshake. |
| B | Familiar to Python users. | Narrower than retry/transaction/trace unless generalized. |
| C | Humane and DSL-like. | Implicit receivers and ambient method lookup hurt local reasoning. |
| D | Very readable for common policies. | Could become many special-looking APIs unless all are block calls. |

Recommendation:

- Keep A as the semantic model.
- Allow D as ordinary block-call library style.
- Treat B as a compatibility teaching analogy, not the core.
- Refuse C unless receiver/context rules become explicit and inspectable.

Integration boundary:

```text
policy call -> caller block -> yield/resume -> cleanup/cancel events
```

### 5. Absence, Result, And Propagation

User pressure:

```text
Keep "not present", "expected failure", and "unexpected failure" distinct.
```

Variants:

```nomi
# A. Explicit match
match User.decode(raw):
    case Ok(user):
        save(user)
    case Err(error):
        explain(error)

# B. Guard-style early return
user = User.decode(raw)?
save(user)

# C. Absence-only defaults
email = user.profile?.email ?? "unknown"

# D. Try expression
user = try User.decode(raw)
```

Tradeoff:

| Variant | Fit | Cost |
| --- | --- | --- |
| A | Most explicit; teaches failure taxonomy and diagnostics. | Verbose for linear happy-path code. |
| B | Excellent after Result semantics are settled. | Easy to overuse before users know what propagates. |
| C | Good for absence only. | Dangerous if generalized to errors. |
| D | Familiar from exception languages. | Can blur expected failure and exception again. |

Recommendation:

- Teach A first.
- Keep C absence-only.
- Defer B until `Result` and decode examples show repeated boilerplate.
- Do not use D as a generic failure surface.

Integration boundary:

```text
absence -> optional access/default
expected failure -> Result + match/possible propagation
unexpected failure -> exception/error diagnostic
```

### 6. Contexts, Extensions, And Scoped Notation

User pressure:

```text
Let a local domain offer fluent names without changing the whole language.
```

Variants:

```nomi
# A. Explicit context value
format_report(report, context=TableContext(locale="en_CA"))

# B. Scoped use
use table(rows):
    rows |> where(.active) |> select(.email)

# C. Extension import
use table.verbs
rows.where(_.active).select(_.email)

# D. Ambient implicit context
rows |> where(.active)
```

Tradeoff:

| Variant | Fit | Cost |
| --- | --- | --- |
| A | Most explicit; easiest to debug. | Verbose in repeated local domains. |
| B | Good scoped boundary; context is visible. | Needs expansion/lookup display. |
| C | Familiar method fluency. | Method lookup can obscure ordinary functions. |
| D | Pleasant but too magical as a first layer. | Hidden context and diagnostics become hard. |

Recommendation:

- Start with A.
- Add B only with inspectable expansion and source spans.
- Allow C only as sugar over imported functions if feature ownership is clear.
- Refuse D in the ordinary layer.

Integration boundary:

```text
lexical scope -> explicit context scope -> name lookup trace
```

### 7. Quote, Rewrite, And Symbolic Power

User pressure:

```text
Talk about code, formulas, plans, and transformations as values.
```

Variants:

```nomi
# A. Syntax quote
expr = quote:
    x + 0

# B. Rewrite rule
simplified = rewrite expr:
    case a + 0 -> a

# C. Mathematica-like replacement
simplified = expr /. (a + 0 -> a)

# D. Macro-like scoped notation
use algebra:
    simplify(x + 0)
```

Tradeoff:

| Variant | Fit | Cost |
| --- | --- | --- |
| A | Clear boundary, source spans, teachable. | Requires later APIs for useful manipulation. |
| B | Good Nomi shape: pattern plus transformation plus trace. | Needs syntax-value and rewrite strategy model. |
| C | Familiar to Mathematica users. | Dense, glyphy, and less first-hour readable. |
| D | Pleasant for domains after boundaries exist. | Dangerous without expansion display and scoped authority. |

Recommendation:

- A first.
- B after pattern and syntax values are stable.
- C research-only unless a symbolic layer earns a compact operator.
- D future L6 scoped extension.

Integration boundary:

```text
source -> SyntaxValue -> pattern/rewrite strategy -> expansion trace
```

### 8. Examples, Checks, And Explain

User pressure:

```text
Make behavior, docs, tests, and diagnostics one family.
```

Variants:

```nomi
# A. Examples inside function
func normalize_email(email:str) -> str:
    examples:
        " A@B.COM " => "a@b.com"
    return email.strip().lower()

# B. Standalone check
check normalize_email(" A@B.COM ") == "a@b.com"

# C. Trace block
trace "import users":
    users = load_users(path)

# D. Explain view
explain(User.decode(raw))
```

Tradeoff:

| Variant | Fit | Cost |
| --- | --- | --- |
| A | Great for docs and behavior near definition. | Needs policy for expensive or world-touching examples. |
| B | Simple test/check surface. | Can drift away from docs if not linked. |
| C | Useful for workflows and pipelines. | Trace volume and redaction need policy. |
| D | One view over events. | Requires producers before it becomes useful. |

Recommendation:

- Treat all four as views over semantic events.
- Add examples and checks before fancy proof syntax.
- Redaction and capability policy are part of the feature, not logging
  decoration.

Integration boundary:

```text
semantic event -> trace record -> diagnostic / example / test / explain view
```

## Whole-Language Example Set

These target-only examples show how the integration boundaries should compose.
They belong in docs and fixtures until implementation and snapshots agree.

### First-Hour Script

```nomi
name = "Ada"
print("Hello, {name}")

func greet(name:str) -> str:
    return "Hello, {name}"

age:int, age >= 13 else "Must be at least 13" = 42
print(greet(name))
```

Boundary focus: binding + function + diagnostic.

### External Data Boundary

```nomi
data Signup:
    email:str, contains(email, "@")
    age:int, age >= 13

match Signup.decode(request.json):
    case Ok(signup):
        save(signup)
    case Err(error):
        explain(error)
```

Boundary focus: data boundary + result + explanation.

### Data Flow And Table Plan

```nomi
plan =
    read_csv(path)
    |> where(.age >= 13)
    |> derive(domain = email_domain(.email))
    |> group_by(.domain)
    |> summarize(count = count())

plan.explain()
people = plan.collect()
```

Boundary focus: flow + table context + plan + backend.

### Block Policy

```nomi
transaction(db):
    user = Signup.decode(request.json)?
    insert_user(user)
```

Boundary focus: block + result + capability + cleanup.

### Symbolic Rewrite

```nomi
expr = quote:
    x + 0

simplified = rewrite expr:
    case a + 0 -> a

explain(simplified)
```

Boundary focus: quote + pattern + rewrite + trace.

## Consolidation Decisions

| Decision | Status | Why |
| --- | --- | --- |
| Checked binding remains the first local judgement surface. | active direction | It unifies assignment, parameters, fields, captures, and decode slots. |
| Pipeline remains the first flow syntax. | active direction | It explains collection and table work through ordinary calls. |
| Query syntax is future sugar over verbs and plan values. | design-needed | Avoids a second language before table context and explain are mature. |
| Block calls are the policy primitive. | active direction | They unify resource, retry, transaction, trace, fixture, and future concurrency. |
| `?.`/`??` stay absence-only. | active direction | Prevents absence and expected failure from collapsing. |
| Result propagation is deferred. | prototype-ready later | `match` should teach failure taxonomy first. |
| Extension/context syntax is scoped or explicit. | design-needed | Hidden context is powerful but cognitively expensive. |
| Symbolic power crosses `quote:`/`describe` boundaries. | active direction | Preserves Mathematica/Racket power without ambient magic. |
| Examples, checks, traces, and explain share semantic events. | active direction | Makes docs, tests, diagnostics, notebooks, and agents one product surface. |

## Next Consolidation Work

1. Turn the binding/data/pattern packet into a single focused feature
   refinement: binding target, tentative capture, constraint failure, decode
   diagnostics, and examples.
2. Turn flow/table/rank into a concrete collection/table vocabulary packet
   with target examples and refusal rules.
3. Turn block policy into a prelude packet: `using`, `retry`, `transaction`,
   `trace`, `test`, cancellation, cleanup, and capability denial.
4. Turn quote/rewrite into a future-layer packet with source spans, expansion
   display, rewrite strategies, and redaction.
5. Update `target_program_fixtures.md` and `demo_target.nomi` only after these
   packets agree on spelling and layer status.
