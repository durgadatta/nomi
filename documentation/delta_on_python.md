# Function

## Defining a Function

Function **definition** and **application** are the most fundamental constructs of the language — most other features can be expressed in terms of these, either directly or conceptually.

In Python, there are two primary ways to define functions: using `def` and `lambda`.

### Renaming `def` to `func`

In Nomi, `def` has been renamed to **`func`** for greater semantic clarity.  
The word “define” (`def`) is too generic — it could mean defining **any** value (an integer, a class, etc.).  
While Python treats functions as *first-class values* (they can be passed around and returned), their definition syntax is syntactically coupled with a binding statement.

Thus, `func` is a more explicit and focused keyword for defining functions as values.

However, the **binding statement** and **block structure** of function definition are retained.  
In other words, no separate form like `my_func = func(...)` is introduced for named function declarations.  
The intention is to preserve Python’s familiar **declarative style**, while giving it clearer semantics through `func`.

For the most common use cases where functions are treated as *values* — especially for concise, inline, or higher-order uses — Nomi introduces a simplified **arrow-based function literal syntax** (described below).  
This serves the role of Python’s `lambda`, but with fewer arbitrary restrictions and clearer alignment with function theory.

Another key reason to retain the `func` block structure is to **respect the existing decorator model**.  
Decorators in Python operate at the level of *function definitions* rather than assignments.  
Splitting them into `name = func(...)` would complicate decorator semantics and break the familiar annotation flow:

```python
@decorator
func greet(name):
    print("Hello", name)
```

Therefore, Nomi enforces the *block-style* structure for nontrivial functions — those that require decorators, annotations, or multiple statements — while providing the arrow syntax for simple, expression-oriented functions.

### Rethinking `lambda`

The word *lambda* originates from **lambda calculus**, where Alonzo Church and Haskell Curry made foundational contributions.  
In that formalism, *all* functions are “lambdas” — that is, function values of type `λ`. In the same way that `3` is an `int`, every function is a `λ`.  

However, in Python, the name `lambda` has gradually acquired a narrower, informal association with “anonymous functions,” which is a misleading simplification of its theoretical roots.

That said, there are concrete syntactic and semantic differences between Python’s `def` and `lambda` beyond naming and anonymity.

### Differences in Python

* **Lambda:**
  * Parameters **cannot** be enclosed in parentheses.
  * Because of the above, **type hints** are not allowed (since `:` is already used for expression delimiting).
  * It can contain **only a single expression**, and **no explicit `return`** statement.
  * **Tuples** must be explicitly wrapped due to the “single expression” restriction.
    * For example, `return x, y` must be written as `=> (x, y)`, not `=> x, y` (the latter would evaluate `x` and then `y` separately).

Many of these restrictions stem from Python’s early **L1(1)** grammar (Left-to-right, leftmost derivation parsing with one-token lookahead).  
Python has since moved to **PEG parsing** (Parsing Expression Grammar), which removes many of those historical constraints.  
Guido van Rossum has written about this evolution [on Medium](https://medium.com/@gvanrossum_83706/peg-parsers-7ed72462f97c).

### Nomi’s Approach

In Nomi, the gap between named and literal functions is **further minimized**.  
Only the last two divergences (explicit `return` and multiple expressions) remain for simplicity and readability.

Nomi introduces a concise **arrow syntax** for function literals:

```python
(x, y) => x + y
(x:int) => x^2      # with type annotation
() => print("no-arg function")
(x, y) => (x^2, y^2)
```


# Binding

> Current design note: the active, implementation-oriented version of this idea
> now lives in
> [Binding Constraints Feature](design_review/binding_constraints_feature.md).

Binding is a fundamental concept as well. This is deeply connected to functions - function call is literally the evaluation of the function body with the arguments bound to the parameter on top of existing binding at the time of function definition (lexical closure -only this supported here for now) or the execution time (dynamic closure). It occurs in many contexts, most visibly in **assignment**, but also in:

* Function call arguments-to-parameter mapping  
* Iteration variables in `for` loops  
* `as` constructs in context managers (`with cm as var`)  
* Exception handling (`except Exception as e`)  
* Pattern matching  
* Packing/unpacking  
* Imports

Python currently supports **type annotations (hints)**, but they are **not enforced** by the interpreter. Some libraries, such as `dataclass` or `pydantic`, rely on them for runtime validation. *(Note: `pydantic` behavior may break under the changes proposed here.)*

---

## Binding Validation in Nomi

Nomi supports **enforced binding validation**. Each variable can optionally be annotated with:

* **Type/Class** (e.g., `int`)  
* **Predicate function** (e.g., `is_positive`)  
* **Expression** that can be interpreted as a predicate in the context of the variable (e.g., `a: a > 20 = 22`)

If any annotation fails its check, a **`TypeError`** is raised.

```python
is_pos = (a) => a > 0
a = 1
a:int = 1
a:int, is_positive, a > 20 = 19  # raises TypeError

b: b>20
b = 19 # fails

b:int = 10 # any new constraints the entire constraints
```

Note: When a variable is rebound with new annotations, **all previous annotations are reset**.

---

## Argument-to-Parameter Mapping

The same binding validation extends to **function calls**.  

To distinguish between multiple parameters and multiple constraints on a single parameter, **constraints must be wrapped in parentheses**:

```python
func f(a:int, b:(int, b > 20)):
    pass

f(x, y)  # Enforces corresponding constraints on each parameter
```

**Important notes:**

* Argument-to-parameter mapping is similar to multiple assignment (`a, b = x, y`) but not identical.  
  * Example: `x = 1, 2` is valid assignment, but for `func f(x)`, `f(1, 2)` is invalid.  
* Python’s rules for argument mapping (positional/keyword, defaults, varargs) carry over.  
* **Constraints are enforced after arguments are mapped to parameters**.

## TODO
* support other constraints such as `const`
  * `a:int, const = 4 `
* add the ability to make the function parameter bind dynamically when selectively request
  * something like -  `f(a:int,b:(int, dynamic), c, ...)`


There are other semantic aspect relevant to parameters but not in bare assignment such as pos-only, keyword-only, mandatory or optional etc; currently Python support them with special marker such as "/" or "*". Additional we may also have lexical(default) or dynamic etc. 


> Note: The harmonization between `def`/`lambda` discussed earlier could also apply here in between assignment and arg-param mapping, but this is more subtle and requires further exploration.


# Coroutine Blocks and Unified Control

Coroutines represent a powerful and deeply studied generalization of control flow — the ability to **pause and resume execution** at arbitrary points, rather than always running a function from start to finish.  
Python’s **generators** (`yield`) are one practical specialization of this idea, trading full generality for usability and clarity.

The exploration of **yield-to-block** structures aims to extend this idea beyond iteration — toward a unified, composable foundation for **control constructs**, including retries, context management, and structured concurrency.  
This bridges the gap between **statements and expressions**, **functions and blocks**, and even between **decorators and context managers**.

A concise illustration of how such a construct might work:

```python
func retry(max_times, exc=None):
    if exc is None:
        exc = Exception

    for i in range(max_times):
        try:
            yield  # Execute the block here
            print(f'successful after {i+1} attempts')
            return
        except exc as e:
            print(f'failed: attempt={i+1}, error: {e}')

    print(f'All {max_times} attempts failed!')


retry(3):
    1 / 0
```

Here, the block following retry(3): is implicitly passed to the function and executed at the yield point — allowing the retry logic to surround it seamlessly.
Such a mechanism generalizes Python’s existing context manager model while remaining minimal and explicit.
> *This concept builds on coroutine fundamentals and extends them toward systematic language design.*  
> *See the section on [Ruby-like Blocks](yield_to_block.md) for the historical background and rationale.*  
> *As discussed there, the above construct cannot be implemented naturally in current Python — as noted in this [Stack Overflow question](https://stackoverflow.com/questions/16919570/encapsulating-retries-into-with-block) — a limitation that appears to be intentional by design.*

Blocks can take parameters as well:
```python
func each(items):
    for item in items:
        yield item

# blocks that receives parameters
each([1,2,3]) -> item: # later with class handling, this would typically be [1,2,4].each() -> item: ...
    print(f'each {item}')
```
