# Block Calls As Control Values

> Status: focused feature design.
>
> This is the first focused follow-up to the cognition-first language direction.
> It studies one syntax/idea deeply: caller-side blocks attached to calls, and
> how they reduce to a small core without becoming a pile of copied Ruby,
> Python, Kotlin, or Scheme syntax.

First-principles position:

```text
Transform -> Sequence In Time -> Touch The World -> Explain
```

Block calls exist because some transformations are time-shaped policies:
acquire, yield, retry, cancel, clean up, authorize, and explain.

## One Sentence

A Nomi block call is an ordinary call with caller-side code attached; the callee
may invoke that code explicitly with `yield`.

```python
retry(3, on=NetworkError):
    send(request)

transaction(db) -> tx:
    tx.insert(user)
```

## Why This Idea Belongs

Many everyday programming patterns are control policies:

- acquire and release a resource,
- retry an operation,
- add a timeout,
- run a transaction,
- collect logs and traces,
- run a test with fixtures,
- schedule parallel work,
- temporarily grant a capability,
- validate setup before a body runs,
- clean up after success, failure, or cancellation.

Python has several partial answers: `with`, decorators, callbacks, generators,
context managers, `async with`, fixtures, and higher-order functions. Ruby has a
clearer general idea: a method can receive a caller-side block and `yield` to
it. Kotlin has trailing lambdas. Scheme has functions and continuations. ALGOL
has block structure.

Nomi should translate those ideas into one coherent construct:

> A block is control-shaped code supplied by the caller to a callee-owned policy.

## Core Form

Zero-yield-value block:

```python
retry(3):
    send_request()
```

Yielded-value block:

```python
using(open(path)) -> file:
    data = file.read()
```

Multiple yielded values:

```python
pairs(headers) -> key, value:
    print(key, value)
```

Constrained block parameter:

```python
each(users) -> user:User:
    send(user.email)
```

Pattern block parameter:

```python
events(stream) -> {"type": "click", "target": target}:
    record_click(target)
```

The block parameter syntax after `->` is a binding target. That is the key
coherence decision: block parameters should not invent a new parameter system.
They reuse the binding/pattern/constraint story.

## Callee Form

The callee uses `yield` to invoke the attached block:

```python
func retry(times, on=Exception):
    for attempt in range(times):
        try:
            yield
            return
        except on:
            if attempt == times - 1:
                raise
```

Yielding values:

```python
func each(items):
    for item in items:
        yield item
```

Bidirectional yield is allowed as the coroutine layer matures:

```python
func ask(prompt):
    answer = yield prompt
    return normalize(answer)
```

The first operational subset may support only simple `yield` and `yield value`,
but the design target is a resumable call point where the block can return a
value to the callee.

## Reduction To Small Core

Surface:

```python
transaction(db) -> tx:
    tx.insert(user)
```

Conceptual reduction:

```text
block_value =
    Block(
        caller_env=current lexical environment,
        binding_target=tx,
        body=[tx.insert(user)],
    )

transaction(db, __block__=block_value)
```

Inside the callee:

```python
yield value
```

reduces to:

```text
invoke __block__ with yielded value
bind yielded value to the block binding target
execute block body in caller lexical environment
return block result to the callee
```

This keeps the small core:

```text
value
binding
function
call
block
yield
pattern
constraint
effect
diagnostic
```

No new control keyword is needed for `retry`, `transaction`, `using`, `timeout`,
or `trace`. They are functions that own policy and invoke a caller-supplied
block.

## Variations Considered

### Variation 1: Python `with` Only

```python
with transaction(db) as tx:
    tx.insert(user)
```

Strengths:

- familiar to Python programmers,
- clear resource acquisition/release shape,
- easy to explain for simple setup/cleanup.

Weaknesses:

- specialized around enter/exit,
- awkward for retry because the body must run multiple times,
- awkward for yielded streams of values,
- separate from decorators, fixtures, and higher-order control,
- does not naturally generalize to bidirectional coroutine communication.

Nomi decision:

`with` can remain as a compatibility or library surface, but it should reduce to
block calls or block policies. It should not be the only control abstraction.

### Variation 2: Higher-Order Functions With Arrow Lambdas

```python
retry(3, () => send_request())

using(open(path), (file) =>:
    data = file.read()
)
```

Strengths:

- small theoretical core,
- familiar in functional languages,
- easy to pass around as values.

Weaknesses:

- visually noisy for multiline control,
- creates a function scope when the programmer often wants caller-local code,
- makes policy look like data plumbing instead of control structure,
- poor fit with Python-like indentation.

Nomi decision:

Function values remain important, but block calls should exist for
control-shaped code. A block is not merely a prettier lambda; it has caller-side
execution and control-flow semantics.

### Variation 3: Ruby `do ... end`

```ruby
retry(3) do
  send_request()
end
```

Strengths:

- proven ergonomic model,
- method-owned control is natural,
- block parameters are clear in Ruby.

Weaknesses:

- `do/end` conflicts with Nomi's Python-readable indentation direction,
- Ruby's implicit receiver conventions are too magical for Nomi,
- Ruby has several block spellings and subtle precedence issues.

Nomi decision:

Borrow the semantic idea, not the surface. Nomi uses indentation:

```python
retry(3):
    send_request()
```

### Variation 4: Kotlin Trailing Lambda

```kotlin
retry(3) {
    sendRequest()
}
```

Strengths:

- clean for single trailing blocks,
- strong fit with builder APIs and scoped receivers.

Weaknesses:

- braces are less consistent with Nomi's Python-like block structure,
- implicit receivers can obscure which object owns a name,
- multiple lambdas and receiver lambdas add mental overhead.

Nomi decision:

Borrow trailing behavior, reject brace syntax and implicit receiver defaults.
If receiver-like scopes are added later, they must be explicit and inspectable.

### Variation 5: Full Continuations

Scheme-style continuations could express almost every control pattern.

Strengths:

- extremely general,
- theoretically elegant,
- captures nonlocal control and advanced flow.

Weaknesses:

- too hard for ordinary local reasoning,
- diagnostics become difficult,
- too powerful as the default explanation for everyday control.

Nomi decision:

Keep resumable `yield` as the practical control primitive. Full continuation
power may exist internally or in advanced scoped features, but it should not be
the ordinary user-facing model.

### Variation 6: Dedicated Keywords For Each Policy

```python
retry 3:
    ...

timeout 5s:
    ...

transaction db:
    ...
```

Strengths:

- highly readable for a few built-in policies,
- easy to optimize or special-case.

Weaknesses:

- grows the language by keyword accumulation,
- makes libraries second-class,
- violates the goal of reducing many patterns to a small core.

Nomi decision:

Policy names should usually be functions. Syntax should make the block
attachment smooth, not create a keyword for each policy.

## Chosen Direction

Use this syntax:

```python
call(args):
    block_body

call(args) -> binding_target:
    block_body
```

with this meaning:

- `call(args)` is evaluated as an ordinary call,
- the indented body is packaged as a caller-side block,
- the optional `-> binding_target` describes how yielded values bind into the
  block body,
- `yield` inside the callee invokes the block,
- block invocation uses the same binding, pattern, and constraint rules as the
  rest of the language,
- the block executes in the caller's lexical context, under well-defined
  rebinding rules.

## Scope And Binding

The hardest design choice is whether the block runs in a new function-like
scope or in the caller's scope.

Chosen direction:

> A block executes in the caller's lexical environment, but yielded values are
> introduced through an explicit binding target.

Example:

```python
total = 0

each(items) -> item:int:
    total += item
```

`total` is the caller's binding. `item` is the block parameter binding for each
yield.

Open design details:

- Does assigning a new name inside a block create a binding visible after the
  block?
- Should there be a `scope:` or `let:` wrapper for block-local names?
- How do `global` and `nonlocal` interact with block execution?
- Can a block return early from the enclosing function, or only from the block?

Default position:

- existing caller bindings may be read and rebound,
- yielded parameters are scoped to the block invocation,
- new names should be local to the block unless explicitly exported,
- nonlocal control such as `return`, `break`, and `continue` needs a separate
  rule per enclosing construct.

This should be specified carefully before blocks become too powerful.

## Result Semantics

There are three possible meanings for a block call's result.

Option A: result is always the callee return value.

```python
result = retry(3):
    send()
```

Option B: result is the last block expression.

```python
value = using(resource) -> r:
    r.read()
```

Option C: result is whatever the callee returns, and the callee may choose to
use the block result.

```python
func using(resource):
    acquired = acquire(resource)
    try:
        return yield acquired
    finally:
        release(acquired)
```

Chosen direction:

Option C. The block call expression returns the callee's return value. If the
callee wants the block's value, it receives it as the result of `yield` and can
return it.

This keeps control ownership with the callee and makes `yield` the explicit
boundary.

## Error And Cancellation Semantics

Block calls must define failure clearly:

- if the block body raises, the exception resumes at the callee's `yield`,
- the callee may catch, retry, translate, or re-raise it,
- `finally` in the callee must run when the block exits by success, failure, or
  cancellation,
- diagnostics should show both the callee policy frame and caller block frame.

Example:

```python
func retry(times, on=Exception):
    for attempt in range(times):
        try:
            return yield
        except on as error:
            if attempt == times - 1:
                raise
```

The exception belongs to the block body, but policy belongs to `retry`.

## Coherence With Other Features

### Binding And Constraints

Block parameters are binding targets:

```python
each(users) -> user:(User, user.active):
    send(user.email)
```

The yielded value is tentatively bound, constraints are checked, and the block
body runs only after successful binding.

### Patterns And Data

Blocks can receive structured values:

```python
events(stream) -> Click(target):
    record(target)
```

This should reuse match/destructuring patterns.

### Pipelines

Block policies can appear inside expression flow when the return value is clear:

```python
result =
    fetch(url)
    |> retrying(3, _)
    |> parse_json
```

But normal block calls are better for control policies with multi-line bodies.

### Effects And Capabilities

Capabilities are naturally scoped by block calls:

```python
with world(fs, network) -> w:
    data = w.network.get(url)
    w.fs.write(path, data)
```

Whether the spelling is `with world(...)` or `world(...):`, the semantic model
should be a block policy that grants capabilities for the body.

### Examples And Tests

Tests and examples are block policies:

```python
test "signup rejects young user":
    expect(signup({"age": 12})).is Err
```

This may later be syntax sugar for a block call:

```python
test("signup rejects young user"):
    expect(signup({"age": 12})).is Err
```

### Symbolic Code

Blocks are runtime control, not symbolic transformation. Symbolic blocks need an
explicit boundary:

```python
rule = quote:
    x + 0 -> x
```

This prevents block syntax from becoming a hidden macro system.

## Diagnostics

A block-aware diagnostic should answer:

- which call owned the control policy?
- where did the callee yield?
- what values were yielded?
- how were yielded values bound?
- did a block parameter constraint fail?
- did the block raise?
- did the callee retry, suppress, translate, or re-raise?

Example diagnostic shape:

```text
BlockError: yielded value failed block parameter constraint
  policy: each(users)
  yield: item at each.nomi:3
  block parameter: user:User
  value: {"name": "Ada"}
  note: expected User
```

This is part of the feature, not optional tooling.

## Syntax Admission Rule

The block-call syntax is admitted because it:

- reduces many control policies to call plus block plus yield,
- preserves Python-readable indentation,
- borrows Ruby's best control abstraction without copying Ruby's receiver magic,
- generalizes Python `with` without being limited to enter/exit,
- composes with constrained binding and patterns,
- creates a natural home for effects, tests, transactions, tracing, and cleanup,
- has an inspectable desugaring.

## Implementation Todo Slice

- Parse `call(args): suite` as a block call.
- Parse `call(args) -> binding_target: suite`.
- Represent attached blocks explicitly rather than as an ad hoc keyword long
  term.
- Route yielded values through the shared binding engine.
- Define block lexical scope and rebinding rules.
- Support `yield` returning the block body's result.
- Propagate block exceptions back through the yielding callee.
- Add diagnostics for yield location, block binding, and policy frames.
- Add examples for `retry`, `using`, `transaction`, `each`, `test`, and
  `world`.

## Open Questions

- Should `with resource -> r:` be canonical syntax, or should all policy blocks
  use ordinary call form?
- Should block bodies have final-expression return by default?
- Should new names inside a block escape to the surrounding scope?
- Should `return` inside a block return from the block, the callee, or the
  enclosing caller function?
- How should async block policies compose with normal block policies?
- Can block values be named and passed explicitly, or should that be a separate
  later feature?

These questions should be answered by preserving one block story, not by adding
special cases for each policy.
