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

Many of these restrictions stem from Python’s early **LR(1)** grammar (Left-to-right parsing with one-token lookahead).  
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


