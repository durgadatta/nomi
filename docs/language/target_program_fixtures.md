# Target Program Fixtures

> Status: active design fixture.
>
> Scope: documentation-only. These examples are aspirational target programs,
> not a claim about current parser or runtime support. They are meant to keep
> language design grounded in ordinary tasks.

## Purpose

Nomi should be judged against programs people actually write:

- small scripts;
- CLI tools;
- JSON/CSV/config cleanup;
- notebook transformations;
- HTTP/API boundaries;
- tests and examples;
- resource and transaction policies;
- package/module organization;
- eventually symbolic and domain-specific work.

These fixtures are not demos. Demos show what works today. Fixtures show what
the language should make coherent tomorrow.

For a larger single-file north-star program, read
[Target Language Tour](target_language_tour.md). This fixture file stays short
and task-focused; the tour shows how the same decisions compose across a
larger program.

For a medium-sized script-shaped target, read
[Target Demo Script](demo_target.nomi). It is intentionally not in `samples/`
because it uses aspirational syntax. Move pieces into runnable samples only
after the implementation and regression snapshots support them.

Each fixture should answer:

```text
What enters the program?
What is checked?
What is transformed?
What can fail?
What does the runtime explain?
```

## Fixture Discipline

Use these rules when editing fixtures:

- Prefer boring real tasks over feature showcases.
- Keep examples short enough to read in one sitting.
- Use syntax already recommended by `language_foundation.md`,
  `language_direction_and_gap_map.md`, and `syntax_synthesis_matrix.md`.
- If syntax is speculative, keep it visibly reducible to binding, function,
  pattern, flow, block, data boundary, or explanation.
- Do not add another spelling just to make one fixture shorter.
- When implementation catches up, move runnable versions into `samples/` and
  tests, but keep this file as the design target.

## Fixture 1: First-Hour Script

Goal: a Python user should understand this without theory.

```nomi
name = "Ada"
age:int, age >= 0 = 36

func greet(name:str) -> str:
    return "Hello, {name}"

message = greet(name)
print(message)
```

Design pressure:

- bindings are ordinary;
- constraints are readable;
- functions look familiar;
- diagnostics should explain failed constraints in plain language.

Open questions:

- Should string interpolation use Python-style `f"..."`, Nomi default
  interpolation, or both with one teaching style?
- What is the smallest error message that teaches constraints?

## Fixture 2: CLI Data Cleanup

Goal: convert messy command-line input and a CSV file into checked domain data.

```nomi
data ImportArgs:
    input:Path, exists(input)
    output:Path
    min_age:int, min_age >= 0 = 13

data Person:
    name:str, len(name) > 0 else "Name is required"
    email:str, contains(email, "@") else "Email must contain @"
    age:int, age >= 0

func main(raw_args:list[str]) -> Result[None, Error]:
    args = ImportArgs.decode(cli_args(raw_args))

    people =
        read_csv(args.input)
        |> select(Person.decode)
        |> collect_results

    match people:
        case Ok(rows):
            write_json(args.output, rows)
            return Ok(none)
        case Err(error):
            return Err(explain(error))
```

Design pressure:

- CLI args are an external boundary;
- CSV rows are external boundaries;
- `Person.decode` should preserve row and column provenance;
- `collect_results` should keep enough context to explain all or first errors.

Open questions:

- Should decode collect all row errors by default or fail fast?
- How should redaction work for secrets in CLI/env/config?

## Fixture 3: Config Layering

Goal: combine defaults, config file, environment, and CLI args without a
separate configuration language.

```nomi
data AppConfig:
    host:str = "127.0.0.1"
    port:int, port > 0, port < 65536 = 8080
    database_url:Secret[str]
    cache_ttl:Duration = 5 min

config =
    AppConfig.decode:
        merge defaults
        merge toml("app.toml")
        merge env(prefix="APP_")
        merge cli_args(argv)

explain(config)
```

Design pressure:

- config is a data-boundary problem;
- field provenance matters;
- secrets need redacted display;
- duration literals need diagnostics around units and time ambiguity.

Open questions:

- Is block-style `decode:` syntax worth it, or should merge remain a library
  call such as `AppConfig.decode(merge(...))`?
- What merge conflicts should diagnose versus override?

## Fixture 4: Notebook Transformation

Goal: make exploratory data work readable and inspectable.

```nomi
# %% Load
rows = read_csv("people.csv")

# %% Clean
clean =
    rows
    |> where(_.email != none)
    |> derive(
        email = _.email.strip().lower(),
        adult = _.age >= 18,
    )
    |> where(_.adult)

# %% Explain
explain(clean)
show(clean |> count)
```

Design pressure:

- notebook cells remain comments/tooling, not core language syntax;
- transforms should be explainable stage by stage;
- `derive` needs a clear binding scope for row fields;
- lazy/eager behavior should be visible.

Open questions:

- Should table rows use `_`, named row bindings, or both?
- What does `explain` show for an eager list versus a lazy query plan?

## Fixture 5: HTTP Boundary

Goal: show how Nomi handles request validation, expected failure, and response
construction.

```nomi
data SignupRequest:
    email:str, contains(email, "@")
    age:int, age >= 13 else "Must be at least 13"

data SignupResponse:
    id:UserId
    email:str

func signup_handler(request:Request) -> Response:
    match SignupRequest.decode(request.json):
        case Ok(input):
            user = create_user(input)
            return json(SignupResponse(id=user.id, email=user.email))
        case Err(error):
            return bad_request(explain(error))
```

Design pressure:

- request JSON is external;
- decode errors should become user-facing diagnostics safely;
- `Result` should be natural before any propagation sugar;
- response data should be owned and displayable.

Open questions:

- Should `decode` return `Result` by default or raise a `BindingError` at some
  boundaries?
- What information is safe to return in public API errors?

## Fixture 6: Resource Policy

Goal: resource management should be one block-call story.

```nomi
func copy_file(input:Path, output:Path) -> Result[None, Error]:
    using(open(input)) -> source:
        using(open(output, mode="write")) -> target:
            target.write(source.read())
            return Ok(none)
```

Design pressure:

- `using` is a block policy, not a special context-manager language;
- yielded resources bind through normal block parameters;
- cleanup should be traceable;
- failures during cleanup need a diagnostic policy.

Open questions:

- Should `using` be a standard library function, a keyword-like policy, or both
  with one canonical teaching style?
- How should cleanup errors combine with body errors?

## Fixture 7: Retry And Transaction

Goal: retries and transactions should share block-policy vocabulary.

```nomi
func save_people(db:Database, people:list[Person]) -> Result[int, Error]:
    transaction(db) -> tx:
        retry(3, on=NetworkError):
            for person in people:
                tx.people.insert(person)

        return Ok(len(people))
```

Design pressure:

- transaction and retry are policies over blocks;
- nested policies should explain entry, yield, retry, commit, rollback;
- cancellation and partial success need named semantics.

Open questions:

- Does `return` inside a policy block return from the function or the block?
- How does `retry` interact with non-idempotent actions?

## Fixture 8: Examples As Tests And Docs

Goal: examples should document behavior, test it, and anchor explanations.

```nomi
func normalize_email(email:str) -> str:
    examples:
        " A@B.COM " => "a@b.com"
        "x@y.com" => "x@y.com"

    return email.strip().lower()

check normalize_email(" A@B.COM ") == "a@b.com"
```

Design pressure:

- examples are not a separate test language;
- examples attach to functions/data and can run as tests;
- failures should explain expected, actual, source, and related constraints.

Open questions:

- Should examples allow setup blocks?
- How are examples exposed in generated docs and notebooks?

## Fixture 9: Module And Package Shape

Goal: medium programs need ordinary structure before advanced abstraction.

```nomi
module people.importer

export ImportArgs, Person, load_people

from nomi.csv import read_csv
from nomi.json import write_json

data Person:
    name:str
    email:str, contains(email, "@")

func load_people(path:Path) -> Result[list[Person], Error]:
    return read_csv(path) |> select(Person.decode) |> collect_results
```

Design pressure:

- module declaration should be optional but clear;
- exports should be explicit for package APIs;
- standard library names should be boring and predictable;
- Python interop should not obscure Nomi boundaries.

Open questions:

- Should `export` be required for public package APIs?
- How should `.py` and `.nomi` modules import each other during bootstrap?

## Fixture 10: Future Symbolic Layer

Goal: advanced power exists, but ordinary code stays ordinary.

```nomi
expr = quote:
    x + 0

rule = quote:
    a + 0 -> a

simplified = rewrite(expr, rule)
explain(simplified)
```

Design pressure:

- code becomes data only at `quote:`;
- rewrite is explicit and explainable;
- rules are values, not ambient magic;
- source spans survive through transformation.

Open questions:

- Is rewrite syntax `expr /. pattern -> replacement` worth admitting later?
- What minimum expression model is needed independent of Python AST?

## Fixture 11: Future Scoped Notation

Goal: domain notation is local, inspectable, and optional.

```nomi
use units:
    distance = 120 km
    time = 2 hr
    speed = distance / time

explain(speed)
```

Design pressure:

- notation is scoped;
- expanded form must be inspectable;
- units are data/constraints, not parser magic everywhere.

Open questions:

- What is the smallest scoped notation mechanism that does not become macros?
- How should formatter/tooling display expanded notation?

## Fixture Review Checklist

For each fixture, keep asking:

- Can a Python programmer understand the ordinary shape?
- Does every special surface reduce to a known normal form?
- Does the example solve a recognizable task?
- Does it show where external data enters?
- Does it distinguish absence, expected failure, exception, and constraint
  failure?
- Does it make diagnostics and explanation visible?
- Does it avoid advanced notation unless the fixture is explicitly future-layer?

## Next Fixture Gaps

Add future fixtures for:

- filesystem tree transforms;
- subprocess/process-result handling;
- secrets and redacted logs;
- time zones and schedules;
- package publishing;
- test fixtures and temporary resources;
- streaming data;
- small web service routing;
- dataframe joins and grouped windows;
- AI-assisted code explanation.
