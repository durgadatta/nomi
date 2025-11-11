Nomi 
=====
**A Minimal, Systematic, and Intuitive Programming Language**  

Nomi is an experimental programming language built on the simplest foundation: **variables, function definitions, and function applications**. Inspired by functional programming and guided by cognitive principles, it emphasizes **clarity, coherence, and human-centered reasoning**.  

Instead of piling on features, Nomi builds a **unified core** where expressiveness emerges naturally. This minimalism encourages intuitive composition, aligning programming more closely with how humans think about processes and abstractions.  

---

# Vision  

Programming today is fragmented—split across domains like **frontend, backend, data science, AI, systems, embedded devices, and cloud computing, deployment, testing, infrastructure, configuration** etc. Each introduces its own languages, libraries, and mental models. The result is a patchwork that forces developers to constantly switch paradigms.  

Most mainstream languages double down on **implementation details**—memory management, optimization tricks, platform quirks—while progress in **abstraction, readability, and usability** stagnates. Over time, technical debt and backward compatibility slow down innovation.  

**Nomi takes a different path.**  
- Built on a **minimal, coherent core** rooted in **Lambda Calculus**, it favors **expression and composition over machinery and quirks**.  
- Adaptations, domain-specific features, and libraries can **layer naturally**, without breaking the underlying model.  
- Its design keeps the **language small but its reach large**, enabling use across domains without fragmentation.  

Performance is not the immediate goal. **Readability, composability, and human-centered expression come first.** Efficiency will emerge through simple, systematic decisions.  

---

# Principles  

- **Minimal Core** → only variables, functions, and applications.  
- **Systematic Extensions** → everything else is layered consistently.  
- **Human-Centered** → aligns with natural reasoning, not machine quirks.  
- **Domain-Agnostic** → one core, many applications, without paradigm shifts.  
- **Simplicity First** → clarity before cleverness; efficiency through design.  

---

# Context  

My journey began with **C**, which revealed the power of low-level control but also its cognitive burden. **Python** opened my eyes to readability and expressiveness. **Tcl** shifted my perspective to **language as a craft**, not just a tool.  

Over the years, I have explored **Java, JavaScript, Scala, Julia, Lisp/Scheme, Haskell, PowerShell, Bash, Mathematica (Wolfram Language), R,  and APL**—each contributing insights into abstraction, notation, and usability.  

In 2015, I published an early [blog post](https://dindefi.wordpress.com/2015/09/08/programming-languages-pl/) (now dormant), capturing fragments of this vision. Since then, these fragments have matured into a more systematic thought process.  

**Nomi is the culmination of a decade of exploration—minimal at its base, expansive in its reach.**  


# Current Status Preview

## Functions, Binding, and Unified Control in Nomi

Nomi refines Python’s **function**, **binding**, and **control flow** foundations into a more **systematic, expression-oriented model**.

### Functions

`def` becomes **`func`** for semantic clarity, while an **arrow syntax** offers concise, expression-level functions:

```python
@decorator
func greet(name):
    print("Hello", name)
```

```python
(x, y) => x + y
(x:int) => x^2
() => print("no args")
```

### Binding and Validation

All bindings — assignments, parameters, loops, etc. — can carry **type and predicate constraints** that are validated automatically:

```python
is_pos = (a) => a > 0
a:int, is_pos, a > 20 = 19  # Raises TypeError
```

```python
func f(a:int, b:(int, b > 20)): pass
f(1, 30)   # OK
f(1, 10)   # Fails
```

### Generator Blocks and Unified Control

Python’s **generators** are a specialized form of **coroutines** — resumable functions built around `yield`.  
Nomi **generalizes generators**, extending their applicability beyond iteration to any block-structured control pattern.  
This leads to the **yield-to-block** construct, which allows code blocks to be passed and executed at controlled suspension points:

```python
func retry(max_times):
    for i in range(max_times):
        try:
            yield
            print(f"success on attempt {i+1}")
            return
        except Exception:
            print(f"failed attempt {i+1}")
```

```python
retry(3):
    1 / 0
```

This bridges **statements and expressions**, **functions and blocks**, and even **decorators and context managers** — realizing the latent generality of Python’s `yield` mechanism.

> See more details on [Delta on Python](documentation/delta_on_python.md) for detailed rationale and examples.

