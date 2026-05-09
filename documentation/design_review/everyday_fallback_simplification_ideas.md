# Everyday Fallback Simplification Ideas

> Status: practical source note for Nomi design review.
>
> Purpose: collect useful language ideas that are not extensively covered in
> the focused design notes, but that simplify the most typical programming use
> cases. These are deliberately not advanced or fancy topics. They are the
> everyday friction points that make small programs either pleasant or tedious.
>
> Related notes:
>
> - [Nomi Language Foundation](language_foundation.md)
> - [Structured Collections And Query Language](structured_collections_query_language.md)
> - [Symbolic And Structural Computation](symbolic_structural_computation.md)
> - [Block Calls As Control Values](block_calls_feature.md)

## Why This Document Exists

The larger design notes focus on functions, bindings, constraints, blocks,
collections, symbolic computation, and high-level syntax. Those are important,
but many programmers judge a language by ordinary tasks:

```text
read a file
parse JSON
validate config
write a CLI
format text
handle dates
retry a request
log what happened
show a useful error
write a small test
ship a script
```

This note is a fallback shelf for practical ideas. Each idea should simplify
common programming without adding a new subsystem. The standard should be:

```text
Does this make a normal small program clearer?
Can it reuse binding, data, constraints, blocks, examples, traces, or modules?
Would a user remember it after a month away?
```

## Admission Rule

An everyday feature belongs here if it:

- removes repeated boilerplate from common scripts or services;
- improves boundary safety for files, config, CLI args, JSON, HTTP, or env;
- makes failures easier to diagnose;
- composes with the core rather than creating a special mini-language;
- can be implemented in a small slice before becoming syntax.

An idea does not belong here if it mainly serves:

- advanced type theory;
- compiler optimization;
- distributed systems;
- expert notation;
- macro systems;
- broad concurrency models;
- symbolic rewrite as a default execution mode.

## 1. Boundary Data As A First-Class Workflow

Most everyday bugs happen at boundaries:

```text
CLI args
environment variables
config files
JSON payloads
CSV rows
HTTP requests
database rows
forms
```

Nomi should make boundary conversion one repeated story:

```text
external value -> decode -> bind fields -> check constraints -> produce data
or diagnostic
```

Possible shape:

```python
data Config:
    input_path:Path, exists(input_path)
    output_path:Path
    min_age:int, min_age >= 0 = 13

config = Config.decode(file("config.toml"))
```

For JSON:

```python
data SignupRequest:
    email:str, contains(email, "@")
    age:int, age >= 13

request = SignupRequest.decode(http.body.json)
```

Design target:

- one `decode` protocol for dicts, JSON, config, rows, and CLI args;
- missing/extra field policy is explicit;
- diagnostics mention the field path and failed rule;
- generated examples can show accepted and rejected input.

## 2. Config Layering

Config often comes from several places:

```text
defaults < config file < environment < CLI args
```

Today this is usually custom glue code. Nomi could make the layering pattern
visible and checked.

Possible shape:

```python
config = Config.load:
    defaults:
        min_age = 13
    file "app.toml"
    env prefix "NOMI_"
    args cli_args
```

Reduction:

```text
load sources in order -> merge by field -> decode Config -> diagnostics
```

Good diagnostics:

```text
ConfigError: invalid field min_age
  source: environment NOMI_MIN_AGE
  value: "-2"
  failed: min_age >= 0
```

This is not a special config language. It is structured data decoding plus
source provenance.

## 3. CLI Commands From Data And Functions

Small programs often need a CLI. The language can make this a direct mapping
from function parameters and data constraints.

Possible shape:

```python
data ImportOptions:
    input:Path, exists(input)
    output:Path
    dry_run:bool = false

command import(options:ImportOptions):
    rows = read_csv(options.input)
    ...
```

or:

```python
command import(input:(Path, exists(input)), output:Path, dry_run:bool=false):
    ...
```

Expected generated behavior:

```text
--input PATH
--output PATH
--dry-run
--help
```

Reduction:

```text
argv -> structured decode -> parameter binding -> function call
```

Diagnostics should use CLI language:

```text
ArgumentError: --input path does not exist
  value: "people.csv"
```

## 4. Path And File Values

Paths are not just strings. Filesystem programming becomes clearer when paths,
files, directories, extensions, and existence checks are first-class ordinary
values.

Possible shape:

```python
input:Path, exists(input), extension(input) == ".csv" = args.input
output:Path = args.output
```

Common operations:

```python
path.parent
path.name
path.stem
path.ext
path / "child.txt"
path.exists()
path.is_file()
path.is_dir()
```

Safe file patterns:

```python
using read_text(input) -> text:
    ...

write_json(output, report, atomic=true)
```

Design target:

- `Path` is a value with display and diagnostics;
- file operations return clear errors with path and operation;
- common operations do not require string splitting;
- atomic writes and temporary paths are library-level defaults.

## 5. Text Processing That Stays Readable

Typical scripts do a lot of text cleanup. Nomi should make the common path
pleasant without requiring regex for everything.

Possible shape:

```python
name =
    raw_name
    |> strip
    |> collapse_spaces
    |> title_case
```

Common text verbs:

```text
strip
trim_prefix
trim_suffix
split
split_lines
join
replace
contains
starts_with
ends_with
collapse_spaces
lower
upper
title_case
parse_int
parse_float
```

Regex should remain available but not dominate:

```python
email:str, matches(email, email_pattern) = raw_email
```

Design target:

- plain text transforms are composable pipeline functions;
- parse functions return `Result` or produce diagnostic-rich decode failures;
- regex captures can bind named fields through patterns later.

## 6. Structured Templates

String interpolation is useful, but everyday code also needs safe templates for
HTML, SQL, shell commands, paths, logs, and messages.

Possible shape:

```python
message = text"Imported {count} rows from {path}"
```

Later, typed templates:

```python
html"<a href={url}>{label}</a>"
sql"select * from users where id = {user_id}"
```

Near-term target:

- keep ordinary text templates simple;
- make diagnostic messages easy to construct;
- postpone domain-specific escaping until typed template values exist.

## 7. Dates, Times, Durations, And Time Zones

Dates and times are everyday and famously error-prone. Nomi should provide
plain concepts early.

Possible shape:

```python
deadline:Date = Date.parse("2026-05-09")
timeout:Duration = 5 seconds
started:Instant = now()
```

Common concepts:

```text
Date          calendar date
Time          clock time without date
DateTime      date + time, maybe local
Instant       absolute moment
Duration      elapsed time
TimeZone      named zone
```

Design target:

- distinguish calendar dates from instants;
- make durations readable;
- require explicit time zone conversion at boundaries;
- diagnostics should explain parse failures and ambiguous local times.

This should stay practical. Do not build temporal logic into the language.

## 8. Expected Failure Versus Bug

Everyday programming needs a simple distinction:

```text
expected failure: invalid input, missing file, parse failed, HTTP 404
bug/unexpected failure: invariant broken, impossible state, programmer error
```

Possible shape:

```python
match parse_int(raw):
    case Ok(n):
        n
    case Err(error):
        explain(error)
```

Convenience for boundary decode:

```python
age:int = parse_int(raw_age) else "age must be an integer"
```

Design target:

- use `Result` or diagnostic values at boundaries;
- keep exceptions for unexpected failures;
- provide a small amount of ergonomic sugar, but do not hide exits.

## 9. Structured Logging As Data

Logging should not be string formatting only. Logs are event values.

Possible shape:

```python
log "import.started", path=input
log "import.finished", rows=len(rows), accepted=len(accepted)
```

or:

```python
trace "import people":
    rows = read_csv(input)
    accepted = rows |> where(valid_person)
```

Design target:

- logs are structured records with names and fields;
- trace blocks can attach timing and nested events;
- diagnostics and examples can reuse trace records;
- logging should not require a global mutable logger in small programs.

## 10. Display, Inspect, And Diff

A language for humans needs good ways to see values.

Common needs:

```text
print a user-facing message
inspect a value for debugging
pretty-print a table
show a diff between expected and actual
render a diagnostic
```

Possible shape:

```python
show report
inspect config
diff expected, actual
```

Design target:

- `show` is for user-facing display;
- `inspect` is for developer-facing structure;
- `diff` understands strings, lists, records, tables, and diagnostics;
- examples use `diff` in failure output.

## 11. Examples, Checks, And Tiny Tests

Testing should be approachable before a project needs a full test framework.

Possible shape:

```python
func normalize_email(email:str) -> str:
    examples:
        " A@B.COM " => "a@b.com"
    return email.strip().lower()
```

Ad hoc checks:

```python
check normalize_email(" A@B.COM ") == "a@b.com"
```

Test blocks:

```python
test "config rejects negative age":
    Config.decode({"min_age": -1}) raises ConfigError
```

Design target:

- examples double as docs and tests;
- failure output shows evaluated values and diffs;
- fixtures can be block policies later;
- tests use normal language features, not a separate assertion mini-language.

## 12. Common Resource Policies

Block calls already cover this design area, but the everyday list deserves to
be explicit.

Common policies:

```text
using       acquire/release resource
retry       retry expected transient failure
timeout     limit duration
temporary   create and clean up temp file/dir
transaction commit/rollback
trace       record nested events
test        run isolated example
```

Possible shape:

```python
using open(path) -> file:
    text = file.read()
```

```python
retry(3, on=NetworkError):
    fetch(url)
```

Reduction:

```text
policy call receives block -> policy invokes block -> trace explains result
```

Design target:

- standard library policies use the same block mechanism;
- failures show both policy frame and user block frame;
- no special syntax per policy.

## 13. Small Task Automation

Developers constantly write task scripts:

```text
format
test
build
clean
serve
release
generate
```

Nomi could make project tasks ordinary functions with metadata.

Possible shape:

```python
task test:
    run "pytest"

task report depends test:
    run "python3 scripts/test_report.py --no-open"
```

Near-term alternative:

```python
func task_test():
    sh("pytest")
```

Design target:

- task definitions are discoverable;
- dependencies are explicit;
- shell commands are structured enough for diagnostics;
- avoid becoming a full build system in the first language.

## 14. Shell And Process Boundaries

Shelling out is common but dangerous. Nomi should make the safe path easier
than string concatenation.

Possible shape:

```python
result = run ["git", "status", "--short"]
```

or:

```python
run command:
    "git"
    "status"
    "--short"
```

Design target:

- command arguments are lists, not one interpolated string by default;
- result includes stdout, stderr, status, and duration;
- failure diagnostics show the command and exit code;
- shell string mode is explicit when needed.

## 15. HTTP And API Boundaries

HTTP is common enough to deserve a clean pattern, but not enough to dominate
the core language.

Possible shape:

```python
response = http.get(url, timeout=5 seconds)

match response:
    case Ok(resp) if resp.status == 200:
        data = User.decode(resp.json)
    case Ok(resp):
        explain resp.status
    case Err(error):
        explain error
```

Design target:

- request and response are data values;
- JSON decode uses the same boundary workflow;
- retry and timeout are block policies or arguments;
- diagnostics include URL, status, method, and decode path.

## 16. Names, Imports, And Small Modules

Typical projects need simple module boundaries. The first story should be
boring and predictable.

Possible shape:

```python
import data.csv
from app.config import Config
```

Design target:

- imports bind module values or names through normal binding;
- relative imports are explicit;
- module-level side effects are discouraged but not hidden;
- diagnostics explain import path resolution;
- small scripts can grow into modules without reorganizing everything.

## 17. Defaults And Options

Typical functions often have default behavior with a few options.

Problem:

Too many boolean flags make calls hard to read:

```python
write_json(path, data, true, false, true)
```

Better:

```python
write_json(path, data, pretty=true, atomic=true)
```

For repeated option sets:

```python
data WriteOptions:
    pretty:bool = false
    atomic:bool = true
    overwrite:bool = false

write_json(path, data, options=WriteOptions(pretty=true))
```

Design target:

- prefer named arguments for options;
- use data values when options become a family;
- diagnostics mention option names;
- avoid enum/stringly options where a small data type is clearer.

## 18. Caching And Memoization For Ordinary Work

Caching is common in scripts and notebooks:

```text
download once
parse once
expensive calculation once
cache file result
```

Possible shape:

```python
cached "users", ttl=1 hour:
    fetch_users()
```

or:

```python
users = cache("users", ttl=1 hour, compute=() => fetch_users())
```

Design target:

- cache keys are visible;
- invalidation policy is explicit;
- cached values carry provenance;
- cache failures are diagnostics, not mysterious stale state.

This should stay a library/block policy first.

## 19. Randomness And Reproducibility

Randomness is ordinary in tests, data sampling, simulations, and demos.

Possible shape:

```python
rng = Random(seed=42)
sample = rows |> sample(10, rng=rng)
```

Design target:

- random sources are values;
- examples and tests can pin seeds;
- diagnostics can report seed and sampling operation;
- avoid hidden global randomness in reproducible paths.

## 20. User Prompts And Interactive Scripts

Many small tools ask users questions.

Possible shape:

```python
name = prompt("Name")
overwrite = confirm("Overwrite output?", default=false)
choice = choose("Format", ["json", "csv", "html"])
```

Design target:

- prompts return typed values or diagnostics;
- defaults and validation are visible;
- non-interactive mode fails clearly instead of hanging;
- CLI flags can bypass prompts.

## 21. Small State Machines

Typical applications often have a few states:

```text
draft -> submitted -> approved -> archived
```

This can be handled by data variants and match, not a heavy state-machine
framework.

Possible shape:

```python
data InvoiceState:
    Draft
    Submitted(at:DateTime)
    Paid(at:DateTime)
    Cancelled(reason:str)

func can_edit(state:InvoiceState) -> bool:
    match state:
        case Draft:
            true
        case Submitted(_):
            false
        case Paid(_):
            false
        case Cancelled(_):
            false
```

Design target:

- variants cover most state modeling;
- examples show allowed transitions;
- later, transition helpers can be library functions.

## 22. Project And Environment Introspection

Everyday scripts ask:

```text
where am I running?
what project root?
what config file?
what environment?
what version?
```

Possible shape:

```python
root = project.root()
mode = env("APP_ENV", default="dev")
version = project.version()
```

Design target:

- environment access is explicit;
- missing env vars produce helpful errors;
- project root detection is inspectable;
- secrets are displayed redacted by default.

## 23. Redaction And Secret Values

Typical programs handle tokens, passwords, and API keys. The first safety win
is display behavior.

Possible shape:

```python
api_key:Secret[str] = env("API_KEY")
```

Display:

```text
Secret("***")
```

Design target:

- secrets do not print raw values by default;
- logs and diagnostics redact them;
- explicit unwrap is possible at boundaries;
- this can be a library type first.

## 24. "Happy Path Plus Boundary" Program Shape

Nomi should make this ordinary shape easy:

```python
data Config:
    input:Path, exists(input)
    output:Path
    min_age:int, min_age >= 0 = 13

data Person:
    name:str
    email:str, contains(email, "@")
    age:int, age >= 0

command run(config:Config):
    trace "load people":
        people = read_csv(config.input) |> map(Person.decode)

    accepted =
        people
        |> where(_.age >= config.min_age)

    report = {
        "accepted": len(accepted),
        "rejected": len(people) - len(accepted),
    }

    write_json(config.output, report, atomic=true)
```

The important part is not this exact syntax. It is that common work composes:

```text
CLI/config decode
file IO
structured rows
constraints
collection transform
trace
safe output
```

## Candidate Standard Library Families

These should exist before or alongside new syntax:

```text
path        Path, file operations, temp paths
text        string transforms and parsers
json        encode/decode with diagnostics
csv         row decoding and schema checks
config      layered config loading
cli         command/argument decoding
time        Date, Time, Instant, Duration, TimeZone
result      Ok, Err, expected failure helpers
log         structured events
test        examples, checks, diffs
http        request/response values
process     safe command execution
cache       visible cache policies
secret      redacted values
display     show, inspect, diff
```

## Reduction To Core

These everyday ideas should reduce to the same Nomi core:

```text
Path/config/CLI/JSON decode -> Data + Binding + Constraint + Diagnostic
File/resource handling      -> Block + Function + Trace
Text transforms             -> Function + Pipeline
Dates/durations             -> Value + Data + Constraint
Expected failure            -> Data variants + Match + Diagnostic
Logging/tracing             -> Trace + Data
Examples/checks             -> Example + Call + Diagnostic
Tasks/processes             -> Function + Module + Result
Secrets                     -> Data + Display policy
```

No feature should require a separate mental model when a core primitive can
explain it.

## Good First Slice

A small implementation path:

```text
Path value and simple file helpers
Result values
data decode diagnostics for dict/JSON
Config loading from dict/file/env in a library
simple command wrapper from a function
show/inspect/diff helpers
check/example execution
structured log events
```

First sample:

```python
data Config:
    input:Path, exists(input)
    output:Path

command main(config:Config):
    rows = read_csv(config.input)
    write_json(config.output, {"rows": len(rows)}, atomic=true)
```

Expected diagnostic:

```text
ArgumentError: --input failed exists(input)
  value: "missing.csv"
  command: main
  parameter: config.input
```

## Design Principles

1. Prefer practical library features before syntax.
2. Make boundary conversion one story everywhere.
3. Keep path, time, result, config, and secret values explicit.
4. Use constraints for validation, not ad hoc checks.
5. Use block policies for resource and retry patterns.
6. Use examples and checks for small tests.
7. Make diagnostics name the user's concept: path, argument, config field,
   JSON field, command, or file operation.
8. Avoid hidden global state for config, logging, randomness, and environment.
9. Make the safe path shorter than the unsafe path.
10. Keep the language ordinary enough that small scripts stay small.
