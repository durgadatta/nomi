# Ruby-like Blocks in Python: Historical Context and Design Rationale

> Current design note: block parameters should eventually reuse the same binding
> engine as assignment and function parameters. See
> [Binding Constraints Feature](design_review/binding_constraints_feature.md).

The idea of generalizing Python’s context managers to support **Ruby-style implicit block yielding** has appeared repeatedly throughout Python’s design history. These constructs offer elegant generalization and can subsume many specialized control-flow patterns. However, the Python community has traditionally been cautious: such features risk obscuring intent when used in place of explicit **control-flow constructs like loops or exception handlers**.

 > block will be almost like an anonymous function that is passed to generator (to be executed at the yield point) with a notable difference: this block is executed within's the caller environment, not a new function environment.
## Limitations of Current Context Managers

As noted in this [Stack Overflow discussion](https://stackoverflow.com/questions/16919570/encapsulating-retries-into-with-block), patterns such as a `retry` context manager are difficult to express naturally in Python. This difficulty is not accidental—it reflects a deliberate design philosophy that prioritizes **explicit control flow** over implicit abstractions.

The standard library’s [`contextlib`](https://docs.python.org/3/library/contextlib.html) provides narrowly scoped tools to handle specific cases. This indicates a conscious decision: **complex control constructs should evolve through libraries, not the language core**.

## Historical Proposals and Their Outcomes

**Accepted Proposal**
- [PEP 343 – The “with” Statement](https://peps.python.org/pep-0343/): Introduced the modern context manager protocol.

**Rejected or Subsumed Proposals**
- [PEP 310 – Reliable Acquisition/Release Pairs](https://peps.python.org/pep-0310/)
- [PEP 340 – Anonymous Block Statements](https://peps.python.org/pep-0340/)

**Contemporary Discussions and Unresolved Challenges**  
The desire for block scoping hasn't disappeared. A recent [discussion](https://discuss.python.org/t/simplistic-block-scope-a-syntactic-sugar/82952/7) on the Python Discourse forum from 2024 focuses around a "simplistic block scope" as syntactic sugar.  
These proposals explored more general block semantics but were ultimately narrowed in scope to favor explicit, predictable behavior.

---

## Rationale for Revisiting Generalized Blocks

Despite past reservations, this exploration proceeds for several strategic reasons.

### 1. Systematic Design

The language aspires to an **expression-oriented model** that blurs, where appropriate, the line between statements and expressions.  
Where these must coexist, integration should be **natural, minimal, and composable**.

By doing so, we can gradually evolve constructs that **bridge the gap between decorators and context managers**—and more broadly, between **function invocation and block execution**—to achieve a unified control abstraction framework.

Coroutines are deep and powerful constructs with a long history of research.  
The *yield-to-block* mechanism, or Python’s generator model, represents a **specialized trade-off**—favoring practical usability over full generality.  
A highly recommended starting point for understanding coroutine design philosophy is [Simon Tatham’s write-up](https://www.chiark.greenend.org.uk/~sgtatham/quasiblog/coroutines-philosophy/).

The primary motivation for proceeding with a *yield-to-block* structure, despite known reservations in the Python community (many of which are well-founded), is to **lay the groundwork for a more general coroutine infrastructure**—from which more powerful and elegant control constructs could eventually emerge.

At the very least, a coroutine introduces a new primitive:  
the ability to **pause execution at any point and resume later**—a fundamental shift from the traditional stateless “start-to-finish” function model.  
This concept also forms a **bridge between statements and expressions**, opening paths to new compositional abstractions.

Coroutines have already proven useful as the foundation for **lazy iterators**, **context managers** (e.g., `contextlib.contextmanager`), and **test frameworks** like `pytest`.  
Much remains to be explored in how such mechanisms can unify control-flow design more systematically.

### 2. Minimalist Primitives

Functions inherently encapsulate **execution blocks**, **parameterization**, and **scoping**.  
By introducing intermediate abstractions that capture only some of these features, we can:

- Avoid unnecessary function definitions used solely to localize scope or control nesting  
- Reduce boilerplate from defining and immediately invoking small helper functions  
- Preserve a small, orthogonal set of core primitives with broad compositional power

### 3. Composition Over Restriction

Generalized block-yielding constructs promote **composition over specialization**.  
Rather than introducing bespoke syntax for every control-flow need, they provide flexible primitives that can be composed into richer abstractions when necessary.

---

This implementation is exploratory.  
The goal is to test whether the **expressiveness–explicitness balance** can be improved without compromising clarity—acknowledging that future refinement may still be required.


## Current Limitations

* Full expression level yield is not currently supported. For instance, `v=(yield 2) + (yield 3)` does not work - this will not generate [1,2]. This is due to the usage of ast-walking with adhoc pause-resume interpreter. This technical limitation well be eventually be overcome so that yield can occur anywhere in the expression; review the [python doc](https://docs.python.org/3/reference/expressions.html#yieldexpr) carefully. This may require significant re-write of interpreter to by either fully continuation-passing-style or a fully linearized interpreter, i.e. a bytecode interpreter like the CPython's VM.
    * Towards supporting expression-level yield at any place, specific form of `lhs = yield x` is now supported. This enables most of the general functionalities of bi-directional co-routine communication (though the complex expression has to be manually reduced into this form)
    * similar approach will be taken to make function-call resumable
    * later, all expressions will be reduced to call

* General parameter/arguments mapping as in function is not how block receive the yielded values (now 1:1 mapping is done with almost like parallel assignment,  without support for default values, constraints etc.). While we may still keep some restriction like in Python's def vs lambda (can't take type annotation), the gap will be minimized.


* In Python, `finally` in `try` is triggered when the generator is garbage-collected as well. Nomi's evolution has not yet reached that fine level of scrutiny; this will be addressed when low-level meta-implementation details are considered.
    * As reference on this [SO question](https://stackoverflow.com/questions/56062909/try-finally-in-python-3-generator), due to the above, we get different behavior on using `next(gen())` vs `x=gen(); next(x)` in this block.

        ```python
        def gen():
            try:
                while True:
                    yield 1
            finally:
                print("stop")

        next(gen()) # prints stop; GC happens immediately after the call
        # vs x = gen(); next(g) # prints stop after the last stmt (after GC)
        print("after generator") # to easily see the GC point
        ```
