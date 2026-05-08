# Radical Language Feature Ideas

> Status: wild design notebook.
>
> This document is intentionally more speculative than the other Nomi design
> documents. It explores language features that may be difficult, unfamiliar, or
> socially risky, but are at least theoretically implementable. The criterion is
> not contemporary implementation ease. The criterion is whether a feature could
> make programming radically easier to use while still having a possible semantic
> account.

## Spirit

This document takes inspiration from:

- Leibniz: a calculus of thought, symbolic notation that helps humans reason.
- Boole: algebraic manipulation of logic.
- Dijkstra: calculational program derivation, weakest preconditions, guarded
  commands, structured reasoning.
- Iverson/APL: notation as a tool of thought.
- Lisp: programs as manipulable symbolic objects.
- Mathematica: rules, symbolic forms, transformation, and evaluation control.
- Prolog: relations, search, and unification.
- Haskell/ML: algebraic structure, equations, types, and purity as leverage.
- Smalltalk/Ruby: message passing and blocks as humane control.
- Spreadsheets: live dependency graphs and approachable reactive computation.

The attitude:

> A program should be not only instructions for a machine, but a manipulable
> object of reasoning for a human.

## Radical Design Permission

The rest of Nomi should remain Python-readable and reducible to a small core.
This document permits more aggressive ideas, provided they can still be given a
semantics in terms of:

```text
value
binding
constraint
function
call
block
yield
pattern
quote
rewrite
relation
proof
time
world
```

The last four are new speculative primitives:

- `relation`: a predicate-like definition that can be queried in multiple
  directions.
- `proof`: a checkable justification object.
- `time`: versioned or evolving values.
- `world`: an explicit boundary for external effects.

## 1. Calculational Blocks

Dijkstra-style programming treats programs as things one can derive and
transform, not merely write.

### Sample

```python
calc:
    sum([1, 2, 3, 4])
== 1 + 2 + 3 + 4
== 3 + 3 + 4
== 6 + 4
== 10
```

Meaning: each step must be justified by equality, a known rewrite rule, or an
explicit named reason.

With reasons:

```python
calc:
    sum(xs + ys)
== sum(xs) + sum(ys)       by sum_concat
== total_x + total_y       where total_x = sum(xs), total_y = sum(ys)
```

### Function Derivation

```python
derive func triangle(n:int, n >= 0) -> int:
    goal:
        result == sum(1..n)

    calc:
        sum(1..n)
    == n * (n + 1) / 2     by arithmetic_series

    return n * (n + 1) / 2
```

### Reduction

A `calc` block is quoted expression syntax plus rewrite/proof checking. It can
be ignored at runtime after verification, or retained as metadata.

## 2. Guarded Commands

Dijkstra's guarded command language made nondeterminism and preconditions
explicit.

### Sample

```python
choose:
    when x >= y:
        max = x
    when y >= x:
        max = y
```

If multiple guards are true, any branch may be selected unless determinism is
requested.

Deterministic form:

```python
choose one:
    when status == 200:
        handle_ok()
    when status >= 400:
        handle_error()
    otherwise:
        handle_unknown()
```

Parallel guarded assignment:

```python
do:
    when x > 0:
        x -= 1
    when y > 0:
        y -= 1
until x == 0 and y == 0
```

### Why It Is Interesting

This gives algorithms a direct notation for "any enabled step is valid." It is
closer to specifications, distributed algorithms, and search problems than
ordinary sequential `if`.

### Reduction

Guarded commands reduce to a set of predicate/block pairs plus a scheduler
policy:

```text
evaluate guards
select enabled branch according to policy
run selected branch
```

## 3. Boolean Algebra As Code

Boole's insight: logic can be calculated.

### Sample

```python
logic:
    allowed = admin or (owner and not suspended)

minimize allowed:
    admin or owner and not suspended
```

Truth-table generation:

```python
truth allowed(admin, owner, suspended):
    admin or (owner and not suspended)
```

Possible output value:

```python
[
    {admin=False, owner=False, suspended=False, allowed=False},
    {admin=False, owner=True,  suspended=False, allowed=True},
    ...
]
```

Boolean proof:

```python
prove:
    not (a and b) == (not a) or (not b)
by boolean_algebra
```

### Use In Real Code

```python
policy can_delete(user, document):
    user.admin or (
        document.owner == user
        and not document.locked
        and not user.suspended
    )

explain can_delete(alice, report)
```

Possible explanation:

```text
can_delete = true because:
  document.owner == user
  document.locked == false
  user.suspended == false
```

### Reduction

Boolean policy syntax reduces to ordinary expressions plus quoted expression
trees that can be simplified, evaluated, and explained.

## 4. Relations Instead Of One-Way Functions

Functions compute in one direction. Relations describe constraints that may be
queried in multiple directions.

### Sample

```python
rel parent(parent, child)
rel ancestor(a, b):
    parent(a, b)
or:
    parent(a, x)
    ancestor(x, b)
```

Query:

```python
find x where ancestor("Ada", x)
```

Reverse query:

```python
find x where ancestor(x, "Grace")
```

### Arithmetic Relations

```python
rel add(x, y, z):
    x + y == z

find y where add(2, y, 10)   # y = 8
find x, y where add(x, y, 10), x > 0, y > 0
```

### User-Friendly Constraint Solving

```python
solve:
    monthly_payment * months == principal + interest
    principal == 10000
    months == 24
    interest == 1200
for monthly_payment
```

### Reduction

Relations reduce to predicates over values plus a search/unification engine.
This is not easy, but it is theoretically clean.

## 5. Bidirectional Functions

Some transformations are naturally reversible. Make that explicit.

### Sample

```python
bidir celsius_fahrenheit:
    f = c * 9 / 5 + 32
```

Use forward:

```python
fahrenheit = celsius_fahrenheit(c=100).f
```

Use backward:

```python
celsius = celsius_fahrenheit(f=212).c
```

### Structured Parser/Printer

```python
bidir iso_date:
    text = f"{year}-{month:02}-{day:02}"
```

```python
iso_date(year=2026, month=5, day=7).text
iso_date(text="2026-05-07").year
```

### Reduction

A bidirectional function is a relation with preferred projections and possibly
declared invertibility constraints.

## 6. Live Values And Time Travel

Spreadsheets are popular because values update when dependencies change.
Languages should be able to express this deliberately.

### Sample

```python
live subtotal = items.sum((item) => item.price)
live tax = subtotal * tax_rate
live total = subtotal + tax
```

When `items` changes, `subtotal`, `tax`, and `total` update.

### Timeline Values

```python
timeline balance:
    starts 0
    deposit(amount) => balance + amount
    withdraw(amount) if balance >= amount => balance - amount
```

Query:

```python
balance.at("2026-05-07")
balance.history()
balance.explain_change(at=event_id)
```

### Time Travel Debugging

```python
debug timeline:
    run program
    watch user.balance
    rewind to before failed_payment
```

### Reduction

`live` bindings form a dependency graph. `timeline` values are event-sourced
state with versioned bindings.

## 7. World-Passing Effects

Effects can be made explicit without making user code unbearable.

### Sample

```python
func save_user(user) using world:
    world.db.users.insert(user)
    world.log.info(f"saved {user.id}")
```

Call:

```python
save_user(user) in production_world
```

Test:

```python
test "save user":
    fake = world.memory()
    save_user(user) in fake
    assert fake.db.users.contains(user)
```

### Capability Slices

```python
func send_email(email) using world.mail, world.log:
    world.mail.send(email)
    world.log.info("sent")
```

### Reduction

Effects are explicit parameters. `world` is a structured value containing
capabilities. The syntax is sugar over dependency injection, but much more
pleasant.

## 8. Explainable Execution

Programs should be able to explain their own decisions.

### Sample

```python
explainable func approve(application):
    application.score >= 700
    and application.income > application.debt * 3
    and not application.flagged
```

Use:

```python
decision = approve(app)
print(decision.value)
print(decision.why)
```

Possible output:

```text
approved because:
  score >= 700                 true, 742 >= 700
  income > debt * 3            true, 9000 > 2000 * 3
  not flagged                  true
```

### Debuggable Branches

```python
if explain user.can_delete(document):
    delete(document)
else -> reason:
    show(reason)
```

### Reduction

An explainable function evaluates an expression while retaining a proof tree or
trace tree for predicates and branches.

## 9. Proof-Carrying Programs

Let programs carry small checkable proofs about their behavior.

### Sample

```python
func abs(x:int) -> result:(int, result >= 0):
    if x >= 0:
        x
    else:
        -x
proof:
    case x >= 0:
        result == x
        x >= 0
    case x < 0:
        result == -x
        -x > 0
```

### Loop Invariant

```python
func sum_to(n:int, n >= 0) -> int:
    total = 0
    i = 0

    while i <= n
    invariant total == sum(0..<i):
        total += i
        i += 1

    total
```

### Reduction

Proof blocks are quoted logical assertions checked by a verifier, theorem
prover, SMT solver, or runtime assertion system.

## 10. Intent Blocks

Sometimes the user knows the desired property better than the algorithm.

### Sample

```python
intent sort_users(users):
    produce result
    where:
        result.permutation_of(users)
        result.every_adjacent((a, b) => a.name <= b.name)
    prefer:
        stable
        O(n log n)
```

The implementation may be synthesized, selected from a library, or checked
against the intent.

Manual implementation with intent:

```python
func sort_users(users)
ensures:
    result.permutation_of(users)
    result.every_adjacent((a, b) => a.name <= b.name)
:
    merge_sort(users, by=(u) => u.name)
```

### Reduction

Intent blocks are constraints over input/output behavior. They can be checked,
used for synthesis, or used as executable tests.

## 11. Holes And Typed Questions

Let unfinished code be first-class.

### Sample

```python
func invoice_total(invoice):
    subtotal = invoice.items.sum((item) => item.price)
    tax = ?
    subtotal + tax
```

The environment can report:

```text
hole tax:
  expected: Money
  available:
    subtotal: Money
    invoice.tax_rate: Rate
  possible:
    subtotal * invoice.tax_rate
```

Named holes:

```python
tax = ?tax
```

Constraint hole:

```python
discount = ? where 0 <= discount <= subtotal
```

### Reduction

A hole is an explicit placeholder value with required constraints and available
context. It is not runtime `None`; it is an incomplete program marker.

## 12. Semantic Search In The Language

Search for code by what it does, not by its name.

### Sample

```python
use function where:
    input: list[int]
    output: int
    ensures result == input.max()
as max_int
```

Ask the environment:

```python
find function:
    takes User
    returns str
    mentions email
```

### Reduction

Semantic search queries metadata, types/constraints, tests, examples, and proof
objects. This is a language-integrated tooling feature, not magic execution.

## 13. Examples As Semantics

Examples can be more than tests; they can define intended behavior.

### Sample

```python
func slugify(text):
examples:
    "Hello World" => "hello-world"
    " Nomi  Lang " => "nomi-lang"
    "A+B" => "a-b"
:
    text.lower().strip().replace(non_word+, "-")
```

Example-driven hole:

```python
func slugify(text):
examples:
    "Hello World" => "hello-world"
    "A+B" => "a-b"
:
    ?
```

### Reduction

Examples are input/output constraints. They can run as tests, guide synthesis,
or document behavior.

## 14. Units And Dimensions As Bindings

Leibniz wanted notation to prevent error. Units are a practical case.

### Sample

```python
distance = 10 meter
time = 2 second
speed = distance / time
```

The language knows:

```python
speed : meter / second
```

Invalid:

```python
distance + time  # DimensionError
```

Conversions:

```python
height = 6 foot
height in meter
```

### Domain Units

```python
unit USD
unit EUR

price = 10 USD
tax = 2 USD
total = price + tax
```

### Reduction

Units are constraints attached to numeric values, with algebra over dimensions.

## 15. Algebraic Effects As Friendly Blocks

Effect systems are usually hard to use. Blocks can make them humane.

### Sample

```python
effect Ask[T]:
    ask(prompt:str) -> T

func signup():
    name = ask("name?")
    email = ask("email?")
    User(name, email)
```

Handle:

```python
handle Ask with form_answers:
    user = signup()
```

Test:

```python
handle Ask with ["Ada", "ada@example.com"]:
    assert signup().name == "Ada"
```

### Reduction

Effects are resumable operations. Handlers are block-control functions that
decide how to resume.

## 16. Conversations As Programs

Many programs are interaction protocols. Make the protocol explicit.

### Sample

```python
dialog checkout:
    ask shipping_address -> address
    ask payment_method -> payment
    confirm order(address, payment) -> ok
    when ok:
        submit_order()
    otherwise:
        cancel()
```

Type of protocol:

```python
checkout : Dialog[OrderResult]
```

Testing:

```python
simulate checkout:
    shipping_address <- fake_address
    payment_method <- fake_card
    confirm <- True
expect:
    OrderSubmitted
```

### Reduction

A dialog is a state machine plus effect handlers for user input.

## 17. State Machines As Values

### Sample

```python
machine Door:
    state Open
    state Closed
    state Locked

    Closed --open--> Open
    Open --close--> Closed
    Closed --lock--> Locked
    Locked --unlock--> Closed
```

Use:

```python
door = Door.Closed
door = door.open()
door = door.close().lock()
```

Invalid transition:

```python
Door.Open.lock()  # TransitionError
```

### With Actions

```python
machine Order:
    state Draft
    state Paid
    state Shipped

    Draft --pay(payment)--> Paid:
        charge(payment)

    Paid --ship(label)--> Shipped:
        carrier.send(label)
```

### Reduction

A machine is a data type plus constrained transition functions.

## 18. Dataflow Equations

Let some programs be equations, not sequences.

### Sample

```python
flow invoice:
    subtotal = sum(items.price)
    tax = subtotal * tax_rate
    total = subtotal + tax
```

Order does not matter:

```python
flow physics:
    velocity = distance / time
    distance = velocity * time
```

Query:

```python
solve physics where distance=100, time=5 for velocity
solve physics where velocity=20, time=5 for distance
```

### Reduction

Dataflow equations are relations plus dependency solving.

## 19. Multiple Worlds: Simulation And Reality

Programs often need to run against real, test, simulated, or hypothetical
worlds.

### Sample

```python
world production:
    db = Postgres(url)
    mail = Sendgrid(key)
    clock = SystemClock()

world simulation:
    db = MemoryDb()
    mail = Mailbox.capture()
    clock = FakeClock("2026-05-07")
```

Run:

```python
signup(user) in production
signup(user) in simulation
```

Compare:

```python
compare:
    signup(user) in production_shadow
    signup(user) in new_pipeline
expect same:
    db.users
    emitted_events
```

### Reduction

A world is an explicit value containing capabilities, state, clocks, and effect
handlers.

## 20. Typed Logs And Audit Trails

Logs should be queryable semantic events, not strings.

### Sample

```python
event UserCreated(user_id:int, email:str)
event PaymentFailed(user_id:int, reason:str)

emit UserCreated(user.id, user.email)
```

Query:

```python
audit:
    find PaymentFailed(user_id, reason)
    where reason == "card_declined"
```

Explain:

```python
why user.status == "suspended":
    trace events for user.id
```

### Reduction

Events are data values appended to an event stream. Audit queries are relations
over event histories.

## 21. Program Slices As First-Class Objects

Let users name and transform parts of programs.

### Sample

```python
slice payment_flow:
    from checkout()
    through charge_card()
    until receipt_sent()
```

Use:

```python
profile payment_flow
prove payment_flow does_not_log(CardNumber)
rewrite payment_flow with async_io_rules
```

### Reduction

A slice is a quoted graph of definitions, calls, and effects. Tools can analyze
or transform it.

## 22. Counterfactual Execution

Ask what would have happened.

### Sample

```python
actual = run order_pipeline(order)

counterfactual:
    assume order.shipping = "express"
    rerun from price_quote
compare:
    actual.total
    counterfactual.total
```

In business logic:

```python
what_if:
    user.plan = "enterprise"
then:
    quote(user)
```

### Reduction

Counterfactual execution is time-travel plus world snapshots plus changed
bindings.

## 23. Negotiated Types

Instead of a type being only a declaration, let the compiler/runtime negotiate
the most useful representation under constraints.

### Sample

```python
choose representation Matrix:
    operations:
        multiply
        transpose
        row_slice
    constraints:
        rows > 1_000_000
        sparsity > 0.95
    prefer:
        memory < 1GB
        fast multiply
```

Use:

```python
A:Matrix = load_matrix(path)
B = A.transpose().multiply(A)
```

### Reduction

Representation choice is a compile/runtime strategy selection constrained by
declared operations and costs. The program semantics remain value-level.

## 24. Ambiguous Notation With Required Resolution

Sometimes human intent is ambiguous. Let code admit ambiguity temporarily but
force resolution before execution.

### Sample

```python
rate = "5%"
amount = 100 USD
fee = amount * rate
```

The system reports:

```text
Ambiguous:
  "5%" may mean Percent(5) or Probability(0.05)
Resolve with:
  rate = 5 percent
```

Explicit ambiguity:

```python
rate = ambiguous:
    5 percent
    Probability(0.05)
```

### Reduction

Ambiguous values are sets of possible values with constraints. Execution
requires the set to collapse to one value.

## 25. Notation Definitions

Let libraries define small, scoped notation, but require desugaring.

### Sample

```python
notation finance:
    "{amount} USD" => Money(amount, "USD")
    "{a} percent" => Percent(a)
```

Use:

```python
use notation finance

price = 10 USD
tax_rate = 8 percent
```

### Guardrails

Every notation must expose its expansion:

```python
expand price = 10 USD
# price = Money(10, "USD")
```

### Reduction

Notation is scoped parsing sugar into ordinary expressions. It is macro-like,
but constrained to declared patterns.

## 26. Human-Centered Error Messages As Syntax

Let code specify what failure should mean to a user.

### Sample

```python
age:int, age >= 18
else message:
    "You must be at least 18 to create an account."
= form.age
```

Function:

```python
func signup(age:(int, age >= 18 else "Must be 18+")):
    ...
```

### Reduction

Constraint failures carry structured explanation values.

## 27. Programs As Legal/Policy Text

Policies are executable logic plus explanation.

### Sample

```python
policy refund_allowed(order):
    allow when:
        order.days_since_purchase <= 30
        and order.status != "final_sale"

    deny when:
        order.item.category == "perishable"
        because "Perishable goods are not refundable."

    otherwise review
```

Use:

```python
decision = refund_allowed(order)
match decision:
    case Allow:
        refund(order)
    case Deny(reason):
        show(reason)
    case Review:
        escalate(order)
```

### Reduction

Policy is ordered guarded commands returning structured decision values and
explanations.

## 28. Literate Execution

Documentation and execution should be able to live together without notebooks.

### Sample

```python
doc "Compute monthly payment":
    We use the standard amortization formula.

    Given:
        principal = 10000 USD
        annual_rate = 6 percent
        months = 24

    calc:
        monthly_rate = annual_rate / 12
        payment = amortize(principal, monthly_rate, months)

    expect:
        payment.round(2) == 443.21 USD
```

### Reduction

`doc` blocks contain markdown-like text plus executable code, examples, and
assertions as structured values.

## 29. Whole-System Contracts

Let a system declare global laws.

### Sample

```python
law money_conserved:
    for every transfer in ledger:
        transfer.from.balance_before - transfer.amount == transfer.from.balance_after
        transfer.to.balance_before + transfer.amount == transfer.to.balance_after
```

Runtime checking:

```python
check law money_conserved during:
    run_settlement()
```

Static/query checking:

```python
prove law money_conserved for payment_pipeline
```

### Reduction

Laws are quantified constraints over values, events, timelines, or program
slices.

## 30. A Radical Nomi Sample

This is intentionally dense, but every piece has a possible semantic story.

```python
use notation finance
use symbolic.boolean

data User(id:int, email:str?, score:int)
data Order(id:int, user:User, total:Money, status:str)

event OrderApproved(order_id:int, reason:Proof)
event OrderRejected(order_id:int, reason:Proof)

policy approve(order):
    allow when:
        order.user.score >= 700
        and order.total <= 5000 USD
        and order.user.email is not None
    deny when:
        order.user.email is None
        because "email required"
    otherwise review

world simulation:
    db = MemoryDb()
    mail = Mailbox.capture()
    clock = FakeClock("2026-05-07")

func process(order:Order) using world:
    decision = explain approve(order)

    choose one:
        when decision is Allow:
            world.db.orders.save(order with {status = "approved"})
            emit OrderApproved(order.id, decision.why)
        when decision is Deny(reason):
            world.db.orders.save(order with {status = "rejected"})
            emit OrderRejected(order.id, reason)
        otherwise:
            world.db.reviews.enqueue(order)

test "approval is explainable":
    order = Order(1, User(7, "ada@example.com", 742), 1200 USD, "new")
    process(order) in simulation

    audit:
        find OrderApproved(order_id, reason)
        where order_id == 1

    prove:
        reason implies order.user.score >= 700
```

What is radical here:

- money notation is scoped syntax,
- policy is executable guarded logic,
- approval produces proof/explanation,
- effects run through an explicit world,
- events are typed,
- audit is relational,
- tests can assert over proof objects.

All of it is theoretically reducible to values, bindings, constraints,
functions, blocks, relations, proof objects, and world-passing effects.

## 31. Admission Rules For Wild Features

Even radical features should pass these tests.

### Human Value

Does the syntax make a hard thing easy for a human?

### Semantic Account

Can the feature be explained without saying "the compiler just knows"?

### Inspectability

Can the system show the desugaring, proof, trace, or explanation?

### Scope Control

Can the feature be imported, enabled, disabled, or localized?

### Failure Clarity

When the feature fails, can it say why in domain language?

## 32. Features That Would Make Designers Pause

The strongest radical candidates are:

- calculational `calc` blocks,
- executable Boolean/policy algebra with explanations,
- relations and bidirectional functions,
- live/timeline values,
- explicit `world` effects,
- proof-carrying functions,
- holes as typed questions,
- semantic search inside the language,
- examples as semantic constraints,
- notation definitions with required expansion,
- typed audit events,
- counterfactual execution,
- whole-system laws.

These ideas are dangerous if mixed casually into the everyday language. They are
also the ideas most likely to make Nomi feel like more than a Python variant.

## 33. Closing Note

A radical language should not merely let programmers write shorter code. It
should let them ask better questions:

```python
why did this happen?
what would happen if this changed?
what laws does this system preserve?
what code satisfies these examples?
what proof explains this decision?
what relation connects these values?
what world did this action affect?
```

If Nomi can make even a few of these questions ordinary, it will have earned its
own identity.
