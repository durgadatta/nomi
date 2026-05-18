# Target Language Tour

> Status: aspirational design artifact.
>
> Scope: documentation-only. This file is not an implementation promise and is
> not expected to parse today. It is a north-star program for judging whether
> Nomi's future syntax is globally consistent, semantically meaningful,
> pleasant to read, and easy to remember.

## Purpose

This tour is the larger companion to
[Target Program Fixtures](target_program_fixtures.md). The fixtures keep design
pressure grounded in ordinary tasks. This file asks a harder question:

```text
If Nomi eventually becomes the language it wants to be,
what should one rich, coherent program feel like?
```

The program below deliberately ignores current implementation complexity. It
does not ignore semantic physics. Every special-looking form should still
reduce to one of Nomi's normal forms:

- binding;
- function;
- pattern;
- flow;
- caller-side block;
- absence/result;
- data boundary;
- explanation.

For a smaller script-shaped target that is easier to compare against the
future operational spec, see [Target Demo Script](demo_target.nomi). The demo
uses the same design choices as this tour, but keeps to ordinary language
cases: config, data boundaries, functions, flow, result handling, block
policies, request decoding, and explanation.

The goal is not to stack syntax from many languages. The goal is to synthesize
the useful pressures behind Python, ML-family languages, Rust/Swift/Gleam,
Ruby/Kotlin/Julia blocks, SQL/dataframe flow, CUE/Pkl/Pydantic boundaries,
notebooks, and symbolic systems into one teachable surface.

## Reading Guide

Read this as if it were a single future `civic_intake.nomi` file with generous
comments. The domain is intentionally boring: import community-service intake
requests, validate them, deduplicate them, save them, serve a tiny HTTP API,
and explain what happened.

Boring is useful. A language that cannot make this kind of program excellent is
not ready for broader ambition.

```nomi
module examples.civic_intake

export main, import_requests, app

from nomi.cli import command, arg, flag
from nomi.collections import chunks, last, sum
from nomi.config import config, cli_args, toml
from nomi.concurrent import task_group
from nomi.csv import read_csv
from nomi.db import Database, TransientDatabaseError
from nomi.http import HttpApp, Request, Response, http, json, bad_request, not_found
from nomi.io import Path, Secret, open
from nomi.option import Optional, some, none
from nomi.time import Instant, Duration, now
from nomi.result import Result, Ok, Err, collect_results
from nomi.system import Env, World
from nomi.table import Table, table, where, select, derive, group, sort
from nomi.text import contains, matches, slug, trim
from nomi.uuid import uuid


# ---------------------------------------------------------------------------
# Configuration is ordinary data with constraints.
# External sources cross through decode so provenance and diagnostics survive.
# ---------------------------------------------------------------------------

data AppConfig:
    host:str = "127.0.0.1"
    port:int, port > 0, port < 65536 = 8080
    database_url:Secret[str]
    import_batch_size:int, import_batch_size > 0 = 500
    default_sla:Duration = 2 hr

    examples:
        {database_url: "postgres://local"} =>
            AppConfig(database_url=Secret("postgres://local"))


func load_config(argv:list[str], env:Env) -> Result[AppConfig, Error]:
    config_source =
        config.defaults
        |> config.merge(toml("nomi.toml"), optional=true)
        |> config.merge(env, prefix="NOMI_")
        |> config.merge(cli_args(argv))

    decoded = AppConfig.decode(config_source)
    return decoded.map_error(error -> error.redact_secrets())


# ---------------------------------------------------------------------------
# Domain values are owned program data.
# Field syntax is binding syntax: receive a value, check constraints, commit.
# ---------------------------------------------------------------------------

data Email:
    value:str, contains(value, "@") else "Email must contain @"

    examples:
        " A@EXAMPLE.COM " => Email("a@example.com")

    func decode(raw:any) -> Result[Email, Error]:
        match str.decode(raw):
            case Ok(text):
                return Ok(Email(normalize_email(text)))
            case Err(error):
                return Err(error)


data Phone:
    value:str, matches(value, r"^\+?[0-9 .()-]{7,}$") else "Invalid phone"


data Contact:
    case ByEmail(email:Email)
    case ByPhone(phone:Phone)
    case Missing


data Region:
    code:str, matches(code, r"^[a-z][a-z0-9-]*$")
    name:str, len(name) > 0


data RequestId:
    value:str, matches(value, r"^req_[a-z0-9_]+$")


data Assignee:
    display_name:str, len(trim(display_name)) > 0


data IntakeRequest:
    id:RequestId
    name:str, len(trim(name)) > 0 else "Name is required"
    contact:Contact
    region:Region
    topic:str, len(trim(topic)) > 0 else "Topic is required"
    details:str = ""
    submitted_at:Instant
    sla:Duration
    tags:list[str] = []
    assignee:Optional[Assignee] = none

    # Derived fields are ordinary functions. They are not hidden object magic.
    func key(self) -> str:
        return slug("{self.region.code}-{self.name}-{self.topic}")


data ImportReport:
    source:Path
    received:int, received >= 0
    accepted:int, accepted >= 0
    rejected:int, rejected >= 0
    duplicates:int, duplicates >= 0
    saved:int, saved >= 0


data PublicIntakeRequest:
    id:RequestId
    name:str
    contact:str
    region:str
    topic:str
    due_at:Instant
    assignee:str


data ReferenceData:
    regions:list[Region]
    topics:list[str]
    refreshed_at:Instant


# ---------------------------------------------------------------------------
# Small functions should feel familiar before they feel clever.
# Examples double as documentation, tests, and future explanation anchors.
# ---------------------------------------------------------------------------

func normalize_email(email:str) -> str:
    examples:
        " A@B.COM " => "a@b.com"
        "x@y.com" => "x@y.com"

    return email.strip().lower()


func parse_contact(raw:any) -> Result[Contact, Error]:
    match raw:
        case none:
            return Ok(Contact.Missing)

    text = str.decode(raw).map(trim)

    match text:
        case Ok(""):
            return Ok(Contact.Missing)
        case Ok(value) if contains(value, "@"):
            return Email.decode(value).map(Contact.ByEmail)
        case Ok(value) if matches(value, r"^\+?[0-9 .()-]{7,}$"):
            return Phone.decode(value).map(Contact.ByPhone)
        case Ok(value):
            return Err(Error("Expected email or phone", value=value))
        case Err(error):
            return Err(error)


func public_contact(contact:Contact) -> str:
    match contact:
        case Contact.ByEmail(Email(value)):
            user, domain = value.split_once("@")
            return "{user.take(2)}...@{domain}"
        case Contact.ByPhone(Phone(value)):
            return value.take_last(4).pad_start(len(value), "*")
        case Contact.Missing:
            return "none"


func display_assignee(request:IntakeRequest) -> str:
    # Optional fields may use absence operators, but not error propagation.
    return request.assignee?.display_name ?? "Unassigned"


func public_view(request:IntakeRequest) -> PublicIntakeRequest:
    return PublicIntakeRequest(
        id=request.id,
        name=request.name,
        contact=public_contact(request.contact),
        region=request.region.name,
        topic=request.topic,
        due_at=request.submitted_at + request.sla,
        assignee=display_assignee(request),
    )


# ---------------------------------------------------------------------------
# Boundary rows are decoded into owned domain values.
# This keeps CSV quirks out of the rest of the program.
# ---------------------------------------------------------------------------

data IntakeRow:
    name:str
    contact:any = none
    region_code:str
    region_name:str
    topic:str
    details:str = ""
    submitted_at:Instant
    tags:list[str] = []


func row_to_request(row:IntakeRow, default_sla:Duration) -> Result[IntakeRequest, Error]:
    contact = parse_contact(row.contact)

    match contact:
        case Ok(contact_value):
            region = Region(code=slug(row.region_code), name=row.region_name)
            id = RequestId("req_{slug(row.region_code)}_{slug(row.name)}_{slug(row.topic)}")

            return Ok(IntakeRequest(
                id=id,
                name=row.name,
                contact=contact_value,
                region=region,
                topic=row.topic,
                details=row.details,
                submitted_at=row.submitted_at,
                sla=default_sla,
                tags=row.tags,
            ))

        case Err(error):
            return Err(error.at(field="contact"))


# ---------------------------------------------------------------------------
# Flow is ordinary value movement.
# Pipeline applies a value now. Underscore marks the current value in tiny
# local functions. Larger logic gets a named function.
# ---------------------------------------------------------------------------

func load_requests(path:Path, default_sla:Duration) -> Result[list[IntakeRequest], Error]:
    rows =
        read_csv(path, provenance=true)
        |> select(row -> IntakeRow.decode(row).at(row.source_path))
        |> collect_results(policy="all_errors")

    match rows:
        case Ok(decoded_rows):
            return decoded_rows
                |> select(row -> row_to_request(row, default_sla))
                |> collect_results(policy="all_errors")

        case Err(error):
            return Err(error)


func dedupe_requests(requests:list[IntakeRequest]) -> list[IntakeRequest]:
    return requests
        |> group(by=_.key())
        |> select(group -> group.items |> sort(by=_.submitted_at) |> last)
        |> sort(by=_.submitted_at)


func summarize_requests(requests:list[IntakeRequest]) -> Table:
    return requests
        |> table
        |> derive(
            due_at = _.submitted_at + _.sla,
            contact_kind = match _.contact:
                case Contact.ByEmail(_): "email"
                case Contact.ByPhone(_): "phone"
                case Contact.Missing: "missing",
        )
        |> group(by=_.region.code)
        |> derive(
            count = count(),
            missing_contact = count_where(_.contact_kind == "missing"),
            soonest_due = min(_.due_at),
        )
        |> sort(by=_.soonest_due)


# ---------------------------------------------------------------------------
# Structured concurrency is also a block policy.
# The callee owns cancellation, joining, and failure aggregation semantics.
# ---------------------------------------------------------------------------

func refresh_reference_data(world:World) -> Result[ReferenceData, Error]:
    result =
        task_group(cancel_on_error=true) -> tasks:
            regions = tasks.spawn:
                world.http.get_json("/reference/regions")
                    .and_then(list[Region].decode)

            topics = tasks.spawn:
                world.http.get_json("/reference/topics")
                    .and_then(list[str].decode)

            match collect_results([regions.await, topics.await]):
                case Ok([regions, topics]):
                    Ok(ReferenceData(
                        regions=regions,
                        topics=topics,
                        refreshed_at=now(),
                    ))

                case Err(error):
                    Err(explain(error))

    return result


# ---------------------------------------------------------------------------
# Blocks are caller-side code attached to ordinary calls.
# Resource, retry, transaction, trace, and concurrency policies reuse one idea.
# ---------------------------------------------------------------------------

func import_requests(db:Database, source:Path, config:AppConfig) -> Result[ImportReport, Error]:
    return trace "import requests from {source}":
        loaded =
            using(open(source)) -> file:
                load_requests(file.path, config.default_sla)

        match loaded:
            case Err(error):
                Err(explain(error))

            case Ok(requests):
                unique = dedupe_requests(requests)
                summary = summarize_requests(unique)

                explain(summary)

                saved =
                    transaction(db) -> tx:
                        saved_count =
                            retry(times=3, on=TransientDatabaseError):
                                unique
                                |> chunks(config.import_batch_size)
                                |> select(batch -> tx.requests.upsert_many(batch))
                                |> sum

                        tx.imports.record(source=source, saved=saved_count, at=now())
                        saved_count

                Ok(ImportReport(
                    source=source,
                    received=len(requests),
                    accepted=len(unique),
                    rejected=0,
                    duplicates=len(requests) - len(unique),
                    saved=saved,
                ))


# ---------------------------------------------------------------------------
# Absence and expected failure are separate.
# ?. and ?? are absence-only. Result is used for expected failure.
# ---------------------------------------------------------------------------

func find_request(db:Database, id:RequestId) -> Result[IntakeRequest, Error]:
    maybe_row = db.requests.find(id)

    match maybe_row:
        case some(row):
            return IntakeRequest.decode(row)
        case none:
            return Err(NotFound("No request with id {id.value}"))


# ---------------------------------------------------------------------------
# HTTP is a boundary. Requests decode; responses encode.
# Routes are library values plus block callbacks, not a separate language.
# ---------------------------------------------------------------------------

data CreateRequest:
    name:str, len(trim(name)) > 0
    contact:any = none
    region:Region
    topic:str, len(trim(topic)) > 0
    details:str = ""


func app(db:Database, config:AppConfig) -> HttpApp:
    return http.app:

        GET "/health" -> request:
            return json({ok: true, at: now()})

        GET "/requests/{id}" -> request:
            id = RequestId.decode(request.path.id)

            match id:
                case Err(error):
                    return bad_request(explain(error))

                case Ok(request_id):
                    match find_request(db, request_id):
                        case Ok(item):
                            return json(public_view(item))
                        case Err(NotFound(message)):
                            return not_found({error: message})
                        case Err(error):
                            return Response.internal_error(explain(error))

        POST "/requests" -> request:
            input = CreateRequest.decode(request.json)

            match input:
                case Err(error):
                    return bad_request(explain(error))

                case Ok(form):
                    contact = parse_contact(form.contact)

                    match contact:
                        case Err(error):
                            return bad_request(explain(error))

                        case Ok(contact_value):
                            item = IntakeRequest(
                                id=RequestId("req_manual_{uuid()}"),
                                name=form.name,
                                contact=contact_value,
                                region=form.region,
                                topic=form.topic,
                                details=form.details,
                                submitted_at=now(),
                                sla=config.default_sla,
                            )

                            transaction(db) -> tx:
                                tx.requests.insert(item)

                            return json(public_view(item), status=201)


# ---------------------------------------------------------------------------
# CLI composition should remain boring.
# Command declarations are data plus functions, not parser magic.
# ---------------------------------------------------------------------------

main = command "civic-intake":
    arg source:Path, exists(source)
    flag explain_only:bool = false

    run argv, world:
        config = load_config(argv, world.env)

        match config:
            case Err(error):
                world.stderr.write(explain(error))
                return 2

            case Ok(config):
                db = Database.connect(config.database_url)

                if explain_only:
                    requests = load_requests(source, config.default_sla)
                    show(explain(requests).with_sources().redact_secrets())
                    return 0

                match import_requests(db, source, config):
                    case Ok(report):
                        world.stdout.write(report)
                        return 0
                    case Err(error):
                        world.stderr.write(explain(error))
                        return 1


# ---------------------------------------------------------------------------
# Tests and examples are one explanation family.
# They use normal bindings, calls, patterns, and checks.
# ---------------------------------------------------------------------------

test "normalizes email":
    check normalize_email(" A@B.COM ") == "a@b.com"


test "parses contact variants":
    check parse_contact("a@b.com") == Ok(Contact.ByEmail(Email("a@b.com")))
    check parse_contact("+1 555 0100") is Ok(Contact.ByPhone(_))
    check parse_contact("") == Ok(Contact.Missing)


test "dedupe keeps latest request for the same person topic and region":
    first = IntakeRequest(
        id=RequestId("req_north_ada_housing"),
        name="Ada",
        contact=Contact.Missing,
        region=Region(code="north", name="North"),
        topic="Housing",
        submitted_at=Instant("2026-05-01T09:00:00Z"),
        sla=2 hr,
    )

    later = first with:
        id = RequestId("req_north_ada_housing_later")
        details = "Updated phone number"
        submitted_at = Instant("2026-05-01T10:00:00Z")

    check dedupe_requests([first, later]) == [later]


# ---------------------------------------------------------------------------
# Future layer: scoped notation and symbolic structure are fenced.
# Ordinary code above does not need to understand this section.
# ---------------------------------------------------------------------------

use units:
    average_review_time = 18 min
    daily_capacity = 6 hr / average_review_time

    check daily_capacity >= 20


scoring_rule = quote:
    urgent(topic, details) + waiting_time(submitted_at)

simple_scoring_rule =
    rewrite scoring_rule with:
        urgent("Housing", _) -> 10
        urgent("Food", _) -> 8
        urgent(_, details) if contains(details, "today") -> 7
        urgent(_, _) -> 1

explain(simple_scoring_rule)
```

## Research Crosswalk

The tour is intentionally conservative about surface forms while borrowing
strongly from many language traditions.

| Source pressure | What Nomi keeps | Where the tour shows it |
| --- | --- | --- |
| Python | Familiar functions, modules, imports, indentation, ordinary scripts | `func`, `module`, CLI `main`, explicit `return` |
| ML family, Rust, Swift, Gleam | Variants, pattern choice, expected failure as values | `data Contact`, `match`, `Result`, `Ok`, `Err` |
| Ruby, Kotlin, Julia, Nim, Gleam | Callback-heavy APIs become readable blocks | `using`, `transaction`, `retry`, `task_group`, `http.app` |
| SQL, dplyr, Polars, Nushell | Whole-data transforms read left to right | `|>`, `table`, `derive`, `group`, `sort` |
| CUE, Nickel, Pkl, Dhall, Pydantic | External data keeps provenance and field diagnostics | `AppConfig.decode`, `IntakeRow.decode`, `.at(row.source_path)` |
| Darklang, notebooks, doc tests | Execution should be inspectable and teachable | `examples:`, `test`, `trace`, `explain(...).with_sources()` |
| Array and symbolic languages | Advanced notation is powerful but fenced | `use units:`, `quote:`, `rewrite` |

This crosswalk should stay aligned with
[Syntax Synthesis Matrix](../convenience/syntax_synthesis_matrix.md) and
[Expanded Language Research](../convenience/expanded_language_research.md).
If those research docs accept or reject a surface form, this tour should show
the consequence in one coherent program.

## What This Demonstrates

| Area | Surface in the tour | Normal form underneath | Adoption reason |
| --- | --- | --- | --- |
| Modules | `module`, `export`, `from ... import ...` | Namespaces and explicit public bindings | Medium programs need obvious structure. |
| Data | `data AppConfig`, `data IntakeRequest` | Field bindings plus construction | Domain models should be readable and checked. |
| Constraints | `port:int, port > 0` | Binding check with diagnostics | Validation should live where values enter. |
| Boundaries | `AppConfig.decode`, `IntakeRow.decode` | External data to owned data | CSV, JSON, env, CLI, and HTTP need provenance. |
| Variants | `case ByEmail`, `case Missing` | Data alternatives plus pattern choice | Expected alternatives should be explicit. |
| Failure | `Result`, `Ok`, `Err`, `match` | Expected failure as data | Public failures should be handled locally. |
| Absence | `?.`, `??`, `some`, `none` | Missing value only | Avoid mixing absence with error propagation. |
| Flow | `|>`, `select`, `group`, `derive` | Value through calls/functions/plans | Data work should read top to bottom. |
| Blocks | `using`, `transaction`, `retry`, `task_group`, `trace` | Call with attached caller code | Policy should be composable and explainable. |
| Resources | `using(open(...)) -> file:` | Block policy with cleanup | IO should be ordinary but safe. |
| Tests | `examples:`, `test`, `check` | Executable examples and assertions | Documentation and verification should reinforce each other. |
| Explanation | `explain(error)`, `explain(summary).with_sources()` | Semantic trace/report view | Errors and plans must teach the program. |
| Scoped notation | `use units:` | Local extension with expansion | Domain notation should not infect ordinary code. |
| Symbolic work | `quote:`, `rewrite` | Code/data boundary and explicit rules | Advanced power needs visible fences. |

## Consistency Rules Captured By The Tour

The tour should be treated as a taste contract until a later design document
replaces it.

- One field language: data fields, parameters, CLI args, route captures, and
  block parameters all use binding plus constraints.
- One boundary story: external data is decoded into owned values with
  provenance, defaults, and diagnostics.
- One expected-failure story: use `Result` and `match` before adding any
  propagation sugar.
- One absence story: use `some`/`none`, `?.`, and `??` only for missing values.
- One flow story: pipeline applies a value now; composition, if later admitted,
  builds functions for later.
- One block story: resource, retry, transaction, trace, command, route, test,
  task group, and future concurrency policies are all calls with attached
  caller code.
- One explanation story: examples, tests, decode errors, traces, query plans,
  and symbolic rewrites are all inspectable semantic events.
- One advanced-power story: notation and code-as-data require explicit fences
  such as `use units:` and `quote:`.

## Deliberate Omissions

The tour avoids several tempting forms even though other languages use them
well.

| Omitted form | Why it is omitted here |
| --- | --- |
| Global macros | They would make ordinary files dialect-dependent before the core is stable. |
| A peer `shape` declaration | External structure is handled by `decode`, patterns, and constraints for now. |
| Broad `?` propagation | It risks merging absence, expected failure, and early return too soon. |
| Multiple placeholder families | `_` is enough for tiny local functions; larger transforms get names. |
| Dense query syntax | Table verbs and plan values should prove themselves before SQL-like syntax enters. |
| Dense array glyphs | Rank and shape ideas remain valuable, but not as the first everyday surface. |
| Unfenced effect handlers | Structured block policies should mature before algebraic effects enter user code. |
| Ambient effects | IO, time, randomness, network, and database authority should stay visible through values or policies. |

## Open Design Questions

This file is a target, not a settled spec. The following decisions still need
focused design:

- Should variant syntax be part of `data`, or should Nomi use a separate
  `variant` keyword?
- Should `decode` return `Result` everywhere, or should some boundary forms
  diagnose directly in command/test contexts?
- How much table vocabulary belongs in the standard library before any query
  syntax is considered?
- What exact provenance object should `read_csv(..., provenance=true)` attach
  to each row, and how should `explain(...).with_sources()` display it?
- Should `command` and `http.app` blocks be library conventions, special
  forms, or library conventions with formatter support?
- What should `task_group` return when multiple child tasks fail, and how does
  cancellation appear in traces?
- What is the precise scoping model for `examples:`, nested functions, and
  methods declared inside `data`?
- Should `with:` updates be core data-copy syntax, library sugar, or deferred?
- What minimal capability model makes `world`, databases, time, network, and
  randomness explainable without burdening first-hour users?
- How should `quote:` preserve source spans, names, and typed bindings across
  rewrites?

## How To Use This File

Use this tour when evaluating proposals:

1. Insert the proposed syntax into the program.
2. Ask whether the program becomes clearer after a week away.
3. Expand the proposed syntax to normal forms.
4. Check whether diagnostics can explain the expansion in user terms.
5. Remove any feature that only makes one line clever while making the whole
   file harder to remember.

If a future syntax cannot live gracefully in this file, it probably does not
belong in the everyday language layer yet.
