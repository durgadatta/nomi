# From ADTs to Dependent Types

## Construction, Elimination, and Pattern Matching

This document is a **stand-alone conceptual note** on how sophisticated programming abstractions arise from a small set of core ideas. It connects algebraic data types, pattern matching, indexed types, guarded sums, and dependent types under a single lens: **construction and elimination**.

The goal is not formal completeness, but *conceptual continuity*: each abstraction layer should feel like a necessary refinement of the previous one, not a leap of faith.

---

## Guiding Principle

> **Types describe what must be provided. Values are witnesses that the description is satisfied.**

Everything below follows from this.

---

## Two Fundamental Notions

### Construction (Introduction)

**Construction** means:

> *Provide enough information (witness + payload) to satisfy a type.*

Examples:

* Pair `(a, b)` witnesses `A × B`
* `Left a` witnesses `A ∨ B`
* `Cons x xs` witnesses `Vec A (n+1)`

A constructor does not merely build data — it *asserts a fact*.

---

### Elimination (Use)

**Elimination** means:

> *Given a witness, extract or refine information guaranteed by the type.*

Examples:

* Using `(a,b)` to obtain `a` and `b`
* Case analysis on `Either`
* Pattern matching on vectors to learn their length

> **Pattern matching is the concrete syntax of elimination.**

To *use* a value is to eliminate its type.

---

## Curry–Howard in One Sentence

| Logic       | Programming  |
| ----------- | ------------ |
| Proposition | Type         |
| Proof       | Value        |
| Implication | Function     |
| Disjunction | Sum type     |
| Conjunction | Product type |

> **A proof is a value; to use a proof is to eliminate its type.**

---

## Ordinary Algebraic Data Types (ADTs)

### Products (AND)

```haskell
(a, b) :: (A, B)
```

* Construction: provide both `a` and `b`
* Elimination: pattern match `(a,b)`

Logical meaning: `A ∧ B`.

---

### Sums (OR)

```haskell
data Either A B = Left A | Right B
```

* Construction: choose a constructor + payload
* Elimination: handle **both cases**

Logical rule:

> **To use `A ∨ B`, you must handle both `A` and `B`.**

This is not a convention; it is the elimination rule for disjunction.

---

## Pattern Matching Is Not Syntax Sugar

Pattern matching:

* Reveals **which constructor was used**
* Refines what you can assume in each branch
* Implements logical **case analysis**

```haskell
f :: Either A B -> C
f (Left a)  = c_from_a a
f (Right b) = c_from_b b
```

Logical form:

```
(A → C) ∧ (B → C)
------------------
      A ∨ B → C
```

Pattern matching is *how proofs are used*.

---

## Indices: Making the Tag Explicit

### Indexed View of `Either`

Conceptually:

```
Either A B ≅ Σ b : Bool. Payload(b)
```

Where:

* `true  → Payload = A`
* `false → Payload = B`

Here:

* The **index** (`Bool`) is primary
* The constructor is a *witness that the index is satisfied*

Tags were indices all along.

---

## Indexed Types

### Example: Vectors

```idris
data Vec A : Nat -> Type where
  Nil  : Vec A 0
  Cons : A -> Vec A n -> Vec A (n+1)
```

* The index (`Nat`) restricts which constructors are possible
* Pattern matching refines the index

```idris
head : Vec A (S n) -> A
head (Cons x xs) = x
```

Impossible cases are **unrepresentable**: no value can be constructed whose type would require handling them.

---

## Guarded Sums

A **guarded sum** is an indexed sum where:

> The payload exists *only if* a predicate or index allows it.

---

### Degenerate Guard: `Either`

* Index = `Bool`
* Guard is trivial
* Constructor acts as a tag

This is the simplest guarded sum.

---

### Non-trivial Guard

```
Σ n : Nat. (n > 0) × Vec A n
```

* Payload exists only when the predicate holds
* Construction requires a proof
* Elimination refines the predicate

The guard is *semantic*, not merely structural.

---

## Dependent Pairs (Σ-types)

```
Σ x : A. P(x)
```

* Construction: `(x, proof_of_P(x))`
* Elimination: pattern match `(x,p)`

This generalizes:

* Records
* Guarded sums
* Existential types

---

## Dependent Functions (Π-types)

```
Π x : A. B(x)
```

* Generalizes functions `A -> B`
* Output type depends on input value

Logical meaning:

> For every `x`, if `x : A`, then `B(x)` holds.

Function application is **implication elimination**.

---

## Refinement Types

```
{x : Int | x > 0}
```

* Implicit Σ-type
* Proof is erased
* Same logical meaning as dependent pair

Refinement types trade explicitness for convenience.

---

## Pattern Matching as the Core Mechanism

Pattern matching:

* Eliminates values
* Refines indices
* Reveals witnesses
* Enforces guards

> **All explicit use of proofs in programming reduces to elimination, most commonly realized as pattern matching.**

---

## Conceptual Hierarchy

```
Ordinary ADTs
  ↓ (add indices)
Indexed Types / GADTs
  ↓ (add predicates)
Guarded Sums
  ↓ (generalize)
Σ-types (dependent pairs)
  ↓
Π-types (dependent functions)
```

Every step preserves the same ideas:

* Construction = provide witness + payload
* Elimination = refine using the witness

---

## Manifesto: Sophistication Without Obscurity

* Abstractions must grow by **refinement**, not replacement
* Every feature must admit clear construction and elimination rules
* Tags should become indices when they start carrying meaning
* Guards should be enforced by types, not conventions
* Pattern matching should be the primary eliminator

> **Sophistication is disciplined reuse under constraint.**

Dependent types are not a new idea — they are what remains when nothing unnecessary is left implicit.

---

## Bridging to Concrete Syntax

A language design guided by these ideas would:

* Treat constructors as *witness builders*, not just data creators
* Make indices explicit where they matter, implicit where they do not
* Use pattern matching as the *only* eliminator for structured data
* Allow gradual migration:

  * ADTs → GADTs → guarded sums → dependent pairs

### Example Design Moves

* Replace ad-hoc boolean flags with indexed constructors
* Replace partial functions with guarded input types
* Prefer elimination-by-pattern over runtime checks

The aim is not maximal expressiveness, but **semantic alignment**: the structure of programs should mirror the structure of their reasoning.

---

## Closing Perspective

> Sophistication is not the accumulation of features, but the disciplined reuse of a small number of ideas under increasing constraint.

Construction, elimination, and pattern matching are those ideas.
