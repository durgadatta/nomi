Nomi 
=====
**A Minimal, Systematic, and Intuitive Programming Language**  

Nomi is an experimental programming language built on the simplest foundation: **variables, function definitions, and function applications**. Inspired by functional programming and guided by cognitive principles, it emphasizes **clarity, coherence, and human-centered reasoning**.  

Instead of piling on features, Nomi builds a **unified core** where expressiveness emerges naturally. This minimalism encourages intuitive composition, aligning programming more closely with how humans think about processes and abstractions.  


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

Over the years, I have explored **Java, JavaScript, Scala, Julia, Lisp/Scheme, ALGOL, Haskell, PowerShell, Bash, Mathematica (Wolfram Language), R,  and APL**—each contributing insights into abstraction, notation, and usability.  

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

# Future Direction: Bridging Foundational Design with Cognitive Pragmatism

> *Dedicated to **Peter Landin**, a fiercely independent mind who revealed the prose within computation, and championed abstraction not as a barrier of symbols but as a bridge for human thought*

The project has reached an important inflection point. We now possess a functional, self-hosted Python interpreter—an extensible experimental substrate that already incorporates the emerging syntax and semantics of Nomi. While incremental improvements will continue, the primary work ahead is more foundational: constructing a principled, coherent design for the language itself.

This effort continues a long-standing intellectual pursuit: the search for a formal language of thought and computation. Its lineage runs from Leibniz’s *characteristica universalis*, through Boole’s algebra of logic, to Church’s Lambda Calculus. Yet the goal is not to produce a purely theoretical artifact. Instead, the ambition is synthetic: to unite the compositional clarity of foundational models (as seen in Lisp and the ALGOL family) with the cognitive usability and ergonomic simplicity that give Python its unique approachability.

The vision is a language that is both **industrial in capability** and **natural in expression**—one that prioritizes clear mental models and human comprehension over accidental complexity or sheer ecosystem mass. Realizing such a system demands a careful navigation of tradeoffs:

- avoiding over-mathematization that yields elegance without usability,
- avoiding abstraction that obscures rather than clarifies,
- avoiding ad-hoc growth that erodes conceptual unity.

The target is a system in which every construct composes cleanly, enabling a virtuous progression as espoused in famed SICP but with a cognitive touch:

**primitive → combination → abstraction → new primitive**

This cycle should scale to unbounded complexity without sacrificing conceptual transparency.

To reach this goal, I will engage deeply with the foundational literature of programming languages—drawing on the systematic rigor of the ALGOL tradition and the semantic frameworks pioneered by Landin, Strachey, Scott, and Hoare. In parallel, I will analyze the convergent lessons of modern language design: Scala’s multiparadigm synthesis, Rust’s ownership discipline, Julia’s performance-oriented multiple dispatch.

The challenge—and the opportunity—is to distill decades of theoretical insight and practical engineering into a single architecture: a language that is formally sound, semantically compositional, and a joy to think in.

## On Ambition and Attrition

Nomi is an experimental language shaped by curiosity, long-term thinking, and an awareness of uncertainty. History shows that many well-designed languages struggle to find adoption, not only because of technical limits, but because tooling, education, platforms, and community momentum matter just as much as ideas themselves. Nomi may grow slowly, change form, or even fade from view regardless of its internal merits. This is not a failure of intent but the normal pressure experienced by ambitious projects. If Nomi thrives, it will do so through shared effort; if it does not, its ideas can still travel forward through those who engage with it.

Evaluating a programming language is a long-term, challenging endeavor, shaped by debates between theory and practice, academia and industry. Every perspective contributes value, and progress emerges through independence, perseverance, and constant feedback. I do not aim to produce world-changing theorems; instead, I focus on concrete tools, real-world experience, and careful iteration—grounded on Python as a practical baseline. At the same time, curiosity and historical insight—nourished by fortunate exposure to world-class physicists and scientists, and a habit of questioning even my own limitations—guide refinements toward coherence and orthogonality. These tensions are not obstacles to be resolved; they are productive sources of motion, balancing immediate utility with long-term structural clarity.

For a deeper look at the intellectual lineage, design risks, and long-term context of Nomi, see [Positioning Within Ambition and Risk](documentation/positioning_ambition_risk.md)