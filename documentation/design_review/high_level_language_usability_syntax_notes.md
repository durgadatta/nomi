# High-Level Language Usability Syntax Notes

> Status: speculative source note for Nomi design review.
>
> Purpose: study syntax and ideas from high-level and very-high-level
> languages that optimize for users, cognition, declarative expression,
> specification, and readable intent.
>
> Companion notes:
>
> - [Python Language Changes Deferred By Complexity](python_changes_deferred_by_complexity.md)
> - [Python Syntax Stretch Feature Atlas](python_syntax_stretch_feature_atlas.md)

## Design Question

Nomi is Python-adjacent today, but the deeper goal is not "Python with more
features." The goal is a language that keeps Python's ordinary readability
while learning from languages and systems that care about:

- human-centered APIs;
- declarative data transformation;
- spec-like program structure;
- helpful diagnostics;
- executable examples;
- built-in domain meaning;
- local reasoning over cleverness.

The central question is:

```text
What syntax makes a program easier to think with, not merely shorter to type?
```

## Reference Traditions

### Python: Readability, Explicitness, And One Obvious Path

Python's design folklore, summarized in PEP 20, values readability,
explicitness, simplicity over complication, and explainable implementation.
These are not just style preferences. They are cognitive constraints: readers
should not need to simulate too much hidden machinery to understand ordinary
code.

Nomi lesson:

- Keep familiar indentation and direct control flow.
- Make implicit behavior visible when it matters.
- Prefer features whose implementation story can be explained to users.
- Do not let clever syntax defeat local reasoning.

Reference:

- [PEP 20 - The Zen of Python](https://peps.python.org/pep-0020/)

### R And The Tidyverse: A Grammar For Human Data Work

Base R and the tidyverse are valuable because they are built around analysts'
workflows. The tidyverse design principles emphasize human-centered,
consistent, composable, and inclusive APIs. Tidy evaluation lets users write
data variables directly in data contexts:

```r
starwars |>
  filter(species == "Human", homeworld == "Naboo")
```

instead of repeatedly writing the dataframe name.

This is a usability win because it matches the analyst's attention: "filter
these rows by these columns." But it also creates cognitive cost when writing
functions, because users must learn the difference between data variables and
environment variables.

Nomi lesson:

- Declarative syntax can reduce noise when the current subject is obvious.
- Subject-specific name lookup is powerful but must be marked and explainable.
- A grammar of verbs is easier to learn when names, argument order, and return
  shapes are consistent.
- Data work benefits from pipelines, column-aware transforms, and diagnostics
  that show intermediate tables.

References:

- [Tidy design principles](https://design.tidyverse.org/unifying.html)
- [Programming with dplyr](https://dplyr.tidyverse.org/articles/programming.html)
- [rlang overview](https://rlang.r-lib.org/index.html)

### Ruby: Natural Blocks And Programmer Happiness

Ruby is useful to study because it optimizes for a language that feels natural
to the programmer. Ruby's official introduction frames the language as a
careful balance of influences from Perl, Smalltalk, Eiffel, Ada, and Lisp, with
a syntax that is simple in appearance but complex inside.

Ruby's most important syntax lesson for Nomi is not any single keyword. It is
the block tradition:

```ruby
items.each do |item|
  puts item
end
```

The block is a caller-side chunk of behavior passed into a method. This gives
Ruby a fluent way to express iteration, resource handling, callbacks, and
mini-DSLs.

Nomi lesson:

- Caller-side blocks are cognitively important because they preserve direct
  code shape while allowing library-defined policy.
- A block should feel natural, but the control transfer must be inspectable.
- Natural syntax can be worth internal complexity only if diagnostics expose
  what is happening.

References:

- [About Ruby](https://www.ruby-lang.org/en/about/)
- [Official Ruby FAQ](https://www.ruby-lang.org/en/documentation/faq/1/)

### Kotlin: Pragmatic Safety With Familiar Syntax

Kotlin is an instructive "make Java nicer without abandoning the ecosystem"
language. Its official specification describes pragmatism as a main design
idea: features and tools should help users get work done. Kotlin also shows how
to make safety feel ergonomic, especially through nullability in the type
system:

```kotlin
val name: String = "Ada"
val nickname: String? = null
val display = nickname ?: name
```

The syntax is not just shorter than Java. It moves important states into the
surface language: nullable vs non-null, expression-valued `if`, safe calls,
data classes, sealed classes, and smart casts.

Nomi lesson:

- Safety features work best when they fit normal expression flow.
- Nullability and missingness should be visible in binding and type stories.
- Pragmatic evolution matters: a language can be principled without being
  frozen.
- User feedback and migration comfort are design constraints.

References:

- [Kotlin language specification introduction](https://kotlinlang.org/spec/introduction.html)
- [Kotlin null safety](https://kotlinlang.org/docs/null-safety.html)
- [Kotlin evolution principles](https://kotlinlang.org/docs/kotlin-evolution-principles.html)
- [Kotlin API guideline: simplicity](https://kotlinlang.org/docs/api-guidelines-simplicity.html)

### Julia: High-Level Mathematical Expression With Multiple Dispatch

Julia is valuable because it refuses the usual split between high-level
interactive programming and performance-oriented implementation. It keeps a
dynamic, expressive feel while making multiple dispatch central:

```julia
area(shape::Circle) = pi * shape.radius^2
area(shape::Rectangle) = shape.width * shape.height
```

Julia also exposes code as manipulable structure through metaprogramming, while
warning that metaprogramming adds complexity.

Nomi lesson:

- High-level syntax can still have a precise dispatch and type story.
- Generic functions can be more natural than receiver-owned methods for some
  domains.
- Mathematical and data workflows benefit from notation that respects the
  domain.
- Metaprogramming should be treated as power with cognitive cost, not as a
  first solution.

References:

- [Julia methods and multiple dispatch](https://docs.julialang.org/en/v1/manual/methods/)
- [Julia metaprogramming](https://docs.julialang.org/en/v1/manual/metaprogramming/)
- [Julia noteworthy differences from other languages](https://docs.julialang.org/en/v1/manual/noteworthy-differences/)

### Swift: Clarity At The Point Of Use

Swift's API guidelines are one of the clearest articulations of use-site
design. The core rule is that declarations are written once but calls are read
many times, so the call site must be clear.

```swift
employees.remove(at: index)
```

The `at` label is not decoration. It prevents confusion between "remove the
element at this position" and "remove this value."

Nomi lesson:

- Syntax design should be evaluated at the use site.
- Brevity is not the same as clarity.
- Argument labels and names can carry semantic load.
- Documentation pressure is a design tool: if the feature cannot be described
  simply, the feature may be wrong.

Reference:

- [Swift API Design Guidelines](https://www.swift.org/documentation/api-design-guidelines/)

### Elm: Friendly Compile-Time Help

Elm is worth studying for its focus on user-facing compiler messages and the
promise of avoiding many runtime errors in practice through type inference.
Elm's guide emphasizes that the compiler can quickly analyze how values flow
through a program and report invalid use with friendly errors.

Nomi lesson:

- Diagnostics are part of language design, not tooling polish after the fact.
- A type or constraint system should help users repair code, not merely reject
  it.
- Friendly errors make stronger semantics feel less hostile.

Reference:

- [Elm guide: types](https://guide.elm-lang.org/types/)

### Wolfram Language: Knowledge-Based Symbolic Programming

Wolfram Language is very high-level in a different direction: it builds a large
amount of algorithmic and world knowledge into the language. It also treats
data, formulas, code, graphics, documents, and interfaces as symbolic
expressions.

Nomi should not copy that scale, but the design pressure is useful: users often
want to express domain ideas directly rather than assemble low-level machinery.

Nomi lesson:

- Very high-level languages can reduce cognitive load by making domain objects
  first-class.
- A unified representation can make programs more inspectable.
- Built-in knowledge is powerful, but it risks bloat unless scoped carefully.
- Nomi might prefer "domain-aware libraries with strong display and diagnostic
  protocols" over a huge built-in knowledge base.

References:

- [Wolfram Language overview](https://www.wolfram.com/language/)
- [Wolfram Language principles and concepts](https://www.wolfram.com/language/principles/)

### Dhall: Programmable Configuration With Total Evaluation

Dhall is useful because it targets a very specific high-level need:
maintainable configuration. It describes itself as JSON plus functions, types,
and imports, while forbidding arbitrary side effects.

This is spec-driven language design: configuration should be programmable
enough to remove repetition, but constrained enough to remain safe and
normalizable.

Nomi lesson:

- Configuration and schemas should not require a separate weak language.
- Total, side-effect-free sublanguages can be valuable for specs,
  configuration, examples, and constraints.
- Semantic normalization and semantic diffing are powerful design tools.

References:

- [Dhall language](https://dhall-lang.org/)
- [Dhall programmable configuration discussion](https://docs.dhall-lang.org/discussions/Programmable-configuration-files.html)

### TLA+: Design Before Code

TLA+ is not a general programming language; it is a high-level specification
language for modeling programs and systems, especially concurrent and
distributed ones. Its design pressure is different from Python, Ruby, or R:
write a precise model of behavior first, then check whether all possible
behaviors satisfy the required properties.

Nomi should not try to become TLA+. But it should borrow the idea that some
parts of a program are better written as claims about behavior than as
instructions.

Nomi lesson:

- Some syntax should describe what must be true, not what steps to run.
- Lightweight invariants, examples, and pre/post conditions can bring
  specification closer to everyday code.
- Exhaustive checking may be too heavy for the first language, but checkable
  examples and constraints are a practical bridge.
- Spec-like syntax should make design assumptions visible before implementation
  details bury them.

Reference:

- [The TLA+ Home Page](https://lamport.org/tla/tla.html)

## Syntax Ideas For Nomi

### 1. Subject-Oriented Blocks

Inspired by R pipelines, Ruby blocks, Kotlin scope functions, and SQL clauses.

Problem:

Many high-level tasks have a current subject: a table, a value, a request, a
configuration, a drawing, a document, or a test case.

Possible Nomi shape:

```python
with user:
    name = .name.trim()
    email = .email.lower()
```

```python
users:
    where .active
    sort .last_login desc
    select .name, .email
```

Why this helps:

- It removes repeated subject names.
- It keeps attention on the domain object.
- It can make declarative transformations read top-down.

Risk:

- Dot shorthand must not obscure where names come from.
- Subject scope needs clear boundaries.

Reduction target:

```text
evaluate subject once -> bind implicit subject -> resolve dotted forms against it
```

### 2. Verb Grammars For Common Domains

Inspired by tidyverse, SQL, dplyr, ggplot2, LINQ, APL, and shell pipelines.

Problem:

General-purpose calls are flexible, but domain work often has a small grammar:
filter, group, summarize, join, select, reshape, plot.

Possible Nomi shape:

```python
orders
    |> where(.status == "paid")
    |> group_by(.customer_id)
    |> summarize(total=sum(.amount), count=count())
```

or:

```python
table orders:
    where status == "paid"
    group by customer_id
    summarize total = sum(amount), count = count()
```

Why this helps:

- Users learn a stable grammar, not many unrelated APIs.
- The output of each step can be inspected.
- The language can produce better diagnostics: missing column, wrong type,
  grouping mismatch, aggregation error.

Risk:

- A domain grammar can become a mini-language.
- It must still reduce to calls, bindings, and constraints.

Reduction target:

```text
collection -> transform step -> transform step -> checked result
```

### 3. Declarative Data And Schema Blocks

Inspired by dataclasses, Kotlin data classes, Swift structs, ML/Rust variants,
JSON Schema, Pydantic, Dhall, and SQL DDL.

Problem:

Many programs spend energy converting messy external data into trusted internal
data.

Possible Nomi shape:

```python
data User:
    name:(str, len(name) > 0)
    email:(str, contains("@"))
    age:(int, age >= 0)
```

```python
schema SignupRequest:
    email: str, contains("@")
    age: int, age >= 13
    referrer?: str
```

Why this helps:

- It unifies documentation, validation, construction, and diagnostics.
- It keeps data shape close to constraints.
- It can generate examples and boundary checks.

Risk:

- `data` and `schema` should not become two unrelated validation languages.
- Optionality, missingness, defaults, and conversion need one story.

Reduction target:

```text
field binding -> constraint checks -> data value or diagnostic
```

### 4. Spec Blocks Next To Code

Inspired by contracts, doctest, property tests, examples, Alloy/TLA-style
specification, and literate programming.

Problem:

The intended behavior of a function often lives in comments, tests, docs, and
issue threads rather than near the function.

Possible Nomi shape:

```python
func clamp(x:int, low:int, high:int) -> int:
    ...

spec clamp:
    requires low <= high
    ensures result >= low
    ensures result <= high

example:
    clamp(12, 0, 10) == 10
    clamp(-1, 0, 10) == 0
```

Why this helps:

- Behavior is readable before implementation details.
- Examples and contracts become executable design material.
- Diagnostics can distinguish precondition failure, implementation bug, and
  test failure.

Risk:

- Full formal methods are too heavy for the first everyday language.
- Specs must be optional and useful even when partial.

Reduction target:

```text
function -> examples and constraints -> checkable claims -> diagnostics
```

### 5. Friendly Failure Syntax

Inspired by Elm diagnostics, rlang structured errors, Rust compiler messages,
and Python tracebacks.

Problem:

Errors often tell the machine-level failure but not the user's violated
intention.

Possible Nomi shape:

```python
age:int, age >= 13 = raw_age
```

Diagnostic:

```text
BindingError: age failed constraint age >= 13
  value: 10
  expected: int and age >= 13
  source: signup.nomi:4
```

Why this helps:

- Language features feel safer when failures explain the rule.
- Users can repair code from the message.
- Constraints, patterns, calls, and data construction share one diagnostic
  format.

Risk:

- Diagnostics require source spans, retained expressions, and value summaries.
- Poor diagnostics make ambitious syntax feel magical.

Reduction target:

```text
semantic event -> retained source expression -> structured diagnostic
```

### 6. Missingness As A First-Class Design Topic

Inspired by Kotlin null safety, Swift optionals, R `NA`, SQL `NULL`, Haskell
`Maybe`, Rust `Option`, and Python `None`.

Problem:

High-level languages constantly represent missing, invalid, unknown, empty, and
failed values. These are not the same.

Possible Nomi shape:

```python
name:str? = user.nickname
display = name else user.name
```

or:

```python
match parse_int(raw):
    case Some(n):
        ...
    case None:
        ...
```

Why this helps:

- It avoids conflating `None`, empty string, empty list, invalid parse, and
  missing field.
- It lets diagnostics say which absence occurred.
- It supports safe data ingestion.

Risk:

- Too many absence types can overwhelm beginners.
- Python interop will always expose ordinary `None`.

Reduction target:

```text
value present/missing/result -> explicit branch or default -> diagnostic if
used unsafely
```

### 7. Literate And Notebook-Friendly Cells

Inspired by Jupyter, R Markdown, Mathematica/Wolfram notebooks, Observable,
doctest, and literate programming.

Problem:

For exploration, teaching, and analysis, code is often read with results,
notes, plots, and examples.

Possible Nomi shape:

```python
note:
    "Load source rows and normalize email addresses."

rows = read_csv(path)
clean = normalize(rows)

show clean |> sample(5)
```

Why this helps:

- It treats explanation as part of the program artifact.
- It supports AI collaboration and human review.
- It can keep examples and traces close to code.

Risk:

- Notebook state can become hidden global state.
- The language should distinguish source semantics from presentation.

Reduction target:

```text
source cells -> ordered evaluation -> visible artifacts -> reproducible trace
```

### 8. Progressive Disclosure Of Power

Inspired by Python, Kotlin, Swift, Elm, Ruby, and tidyverse ergonomics.

Problem:

Very-high-level languages can become intimidating when advanced features are
visible too early.

Possible Nomi shape:

```python
name = "Ada"
greet(name)
```

then:

```python
name:(str, len(name) > 0) = input_name
```

then:

```python
data User:
    name:(str, len(name) > 0)
```

then:

```python
example:
    User(name="Ada").name == "Ada"
```

Why this helps:

- A beginner can start with values and calls.
- The same concepts recur as constraints, data, examples, and diagnostics.
- The language grows by reinforcing concepts rather than adding unrelated
  subsystems.

Risk:

- If advanced syntax does not reduce to the same primitives, the ladder breaks.

Reduction target:

```text
same primitive, richer surface
```

## Candidate Syntax Families

### Human Data Work

Good candidates:

- pipelines;
- subject-dot shorthand inside explicit subject blocks;
- table transforms with stable verbs;
- column-aware diagnostics;
- examples that show before/after rows.

Avoid early:

- full SQL clone;
- implicit global data masking everywhere;
- backend-specific query magic.

### Domain Modeling

Good candidates:

- `data` declarations;
- optional and defaulted fields;
- constrained fields;
- closed variants;
- exhaustive match diagnostics.

Avoid early:

- inheritance-heavy modeling;
- ad hoc schema syntax separate from `data`;
- too many record literal shorthands before the data story stabilizes.

### Specification And Validation

Good candidates:

- `example` blocks;
- lightweight `requires` and `ensures`;
- boundary validation;
- structured diagnostics;
- traceable constraint failures.

Avoid early:

- full proof systems;
- dependent types as everyday syntax;
- specs that cannot run or explain failures.

### User-Defined Control

Good candidates:

- block calls;
- retry/transaction/using/test patterns;
- explicit `yield` points;
- diagnostics for block invocation.

Avoid early:

- invisible coroutine effects;
- arbitrary control macros;
- concurrency before ordinary block control is stable.

### Very-High-Level Knowledge

Good candidates:

- domain-aware libraries with rich values;
- units as constrained values;
- safe templates for SQL, HTML, paths, and shell;
- inspectable symbolic forms for diagnostics.

Avoid early:

- massive built-in knowledge base;
- symbolic rewrite as a default execution model;
- notation that only experts can read.

## Nomi Design Principles From These Traditions

1. Optimize for the reader at the use site.
2. Let common workflows have a grammar, but keep that grammar reducible.
3. Make the current subject explicit when using subject-oriented lookup.
4. Treat diagnostics as part of the feature.
5. Put constraints where names are introduced.
6. Distinguish missing, invalid, empty, and failed.
7. Keep examples executable and near the behavior they explain.
8. Prefer progressive disclosure over feature walls.
9. Borrow operations, not surface fashion.
10. Keep the first language ordinary enough to remember after time away.

## Most Promising Next Design Threads

These are the threads most aligned with the current Nomi foundation:

- a table/data transformation grammar that reduces to pipelines and calls;
- a `data`/`schema` story that reuses constrained binding;
- subject-oriented blocks with visible scope;
- executable `example` blocks and lightweight specs;
- friendly structured diagnostics for binding, pattern, and call failures;
- a clear missingness model before adding safe-navigation sugar.

Each should be evaluated through the same path:

```text
syntax -> reduction -> diagnostic -> tests -> documentation
```

If that path is hard to write down, the idea is still source material rather
than language design.

## Source Links

- Python: [PEP 20 - The Zen of Python](https://peps.python.org/pep-0020/)
- R/tidyverse: [Tidy design principles](https://design.tidyverse.org/unifying.html)
- R/tidyverse: [Programming with dplyr](https://dplyr.tidyverse.org/articles/programming.html)
- R/tidyverse: [rlang overview](https://rlang.r-lib.org/index.html)
- Ruby: [About Ruby](https://www.ruby-lang.org/en/about/)
- Ruby: [Official Ruby FAQ](https://www.ruby-lang.org/en/documentation/faq/1/)
- Kotlin: [Language specification introduction](https://kotlinlang.org/spec/introduction.html)
- Kotlin: [Null safety](https://kotlinlang.org/docs/null-safety.html)
- Kotlin: [Evolution principles](https://kotlinlang.org/docs/kotlin-evolution-principles.html)
- Kotlin: [API guideline: simplicity](https://kotlinlang.org/docs/api-guidelines-simplicity.html)
- Julia: [Methods and multiple dispatch](https://docs.julialang.org/en/v1/manual/methods/)
- Julia: [Metaprogramming](https://docs.julialang.org/en/v1/manual/metaprogramming/)
- Swift: [API Design Guidelines](https://www.swift.org/documentation/api-design-guidelines/)
- Elm: [Guide: types](https://guide.elm-lang.org/types/)
- Wolfram: [Language overview](https://www.wolfram.com/language/)
- Wolfram: [Principles and concepts](https://www.wolfram.com/language/principles/)
- Dhall: [Language overview](https://dhall-lang.org/)
- Dhall: [Programmable configuration files](https://docs.dhall-lang.org/discussions/Programmable-configuration-files.html)
- TLA+: [The TLA+ Home Page](https://lamport.org/tla/tla.html)
