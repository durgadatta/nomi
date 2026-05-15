# Concatenative Language Research

> Status: raw research notes; not an active syntax spec.
>
> Scope: documentation-only. This doc surveys concatenative and stack-based
> languages (Forth, Factor, Joy, Kitten, Cat) for patterns worth understanding
> in Nomi's design.
>
> Consolidation note: stable observations should fold into
> `../convenience/functions.md`, `../convenience/collections.md`, or
> `../language/language_foundation.md`.

## 1. The Core Model: Concatenation Is Composition

In a concatenative language, juxtaposition means function composition. The
program `f g h` means "apply f, then g, then h." There is no function
application syntax because data flows implicitly on a stack.

Applicative languages separate composition from application:
```haskell
h(g(f(x)))      -- applicative: nested application
h . g . f        -- applicative: explicit composition
x |> f |> g |> h -- applicative: pipeline spelling
```

Concatenative languages make composition the default:
```factor
f g h            -- data flows left to right through the stack
```

The implicit data path eliminates parameter names entirely, making it the
purest form of point-free programming.

**Nomi note**: pipeline (`|>`) already gives a concatenative feel. The key
difference is that `|>` threads one value, while concatenative code threads a
stack of values. The composition operators (`>>`, `<<`) close the gap further.

## 2. Stack Effect Declarations

Factor's stack effect notation is the type signature of a concatenative world.
It declares what a word consumes and produces:

```factor
: square   ( x -- y ) dup * ;
: add      ( a b -- sum ) + ;
: map-over ( seq quot -- seq' ) map ;
: bi-combine ( x p q -- p(x) q(x) ) [ keep ] dip call ;
```

The declaration `( a b -- c d )` means "consumes a and b, produces c and d."
This is the concatenative equivalent of a type signature, but focused on
stack shape rather than value type. Kitten and Cat extend this to typed stack
effects:

```kitten
define square (Int32 -> Int32):
  dup (*)

define apply_both (a (a -> b) (a -> c) -> b c):
  -> {f} {g};
  {g} dip apply   // apply g, keeping result; then apply f
```

Stack effects make data flow visible without naming intermediate values
or declaring formal parameters.

**Semantic idea**: the stack effect is a contract. It documents the
transformation independently of the implementation. This is the same idea as a
type signature or a contract, specialized to stack-shaped data flow.

## 3. Core Stack Combinators

Combinators are the universal vocabulary of stack manipulation. They are small,
named operations that rearrange the stack without naming values:

| Combinator | Stack effect | Meaning |
| --- | --- | --- |
| `dup` | `( x -- x x )` | Duplicate top |
| `drop` | `( x -- )` | Discard top |
| `swap` | `( x y -- y x )` | Exchange top two |
| `over` | `( x y -- x y x )` | Copy second item to top |
| `rot` | `( x y z -- y z x )` | Rotate third to top |
| `nip` | `( x y -- y )` | Drop second item |
| `tuck` | `( x y -- y x y )` | Copy top under second |
| `2dup` | `( x y -- x y x y )` | Duplicate top pair |
| `-rot` | `( x y z -- z x y )` | Reverse rotate |

All concatenative languages share this vocabulary. It is the assembly language
of data routing, widely criticized for obscuring intent, but also the source of
concatenative conciseness.

**Nomi note**: these are too low-level to surface directly. The lesson is not
"add `swap` to Nomi." The lesson is that naming data flow paths explicitly
(such as with pipeline, `_` holes, and `where:` bindings) replaces a whole
class of mechanical shuffling with readable structure.

## 4. Quotations

A quotation is deferred code -- an anonymous block that sits on the stack
until a combinator executes it. It is the concatenative lambda:

```factor
[ 2 * ]          -- push a quotation that doubles
[ 1 + ]          -- push a quotation that increments
                 -- stack: quotation1 quotation2
```

```factor
4 [ 2 * ] call   -- stack: 8
```

Quotations satisfy "code is data" without macros: any word can receive a
quotation and decide when, whether, and how many times to call it.

Key quotation combinators:

```factor
[ 2 * ] call      -- execute quotation
[ 2 * ] curry     -- partially apply: ( x -- [ 2 * ] )
[ + ] 2curry      -- ( x y -- [ x + y ] )
[ f ] [ g ] compose -- ( -- [ f g ] ) ; new quotation = f then g
```

Joy makes quotations central: there are no named functions, only quoted
programs and combinators that execute them.

## 5. Higher-Order Combinators

Factor's combinator family generalizes function application patterns:

```factor
-- bi: apply two quotations to one value, produce two results
5 [ 2 * ] [ 3 + ] bi         -- stack: 10 8

-- tri: apply three quotations to one value
5 [ 2 * ] [ 3 + ] [ 6 - ] tri  -- stack: 10 8 -1

-- bi@: apply one quotation to two values
2 3 [ 1 + ] bi@              -- stack: 3 4

-- bi*: apply two quotations to two values (one each)
2 3 [ 1 + ] [ 10 * ] bi*     -- stack: 3 30

-- 2bi: apply two quotations to two values (both get both)
2 3 [ + ] [ * ] 2bi          -- stack: 5 6

-- keep: apply quotation, keep original below result
5 [ 2 * ] keep               -- stack: 5 10

-- dip: save top value, apply quotation to rest, restore
x y z [ f ] dip              -- x y z  ->  x f(y) z
                             -- "dip under" = save and restore
```

The `dip` combinator is particularly important. It temporarily removes a value
from the stack, applies a quotation to everything below, then puts the saved
value back. This is the concatenative way to say "operate on a substructure
while preserving context."

Joy generalizes further with recursion combinators:

```joy
-- Linear recursion (base case, recursive case)
[null] [1 +] [pred] linrec   -- if null, 1+; else pred then recurse

-- Binary recursion (divide-and-conquer)
[small] [solve] [split] [combine] binrec

-- General recursion with condition
[base?] [base-act] [rec-act] [genrec] genrec
```

These show a deep concatenative idea: recursion patterns are first-class
combinators, not language keywords.

## 6. Factor's `call(` Syntax and Locals

Factor is opinionated: stack shuffling is preferred, but locals exist when
shuffling becomes unreadable. `call(` introduces named locals with stack-effect
discipline:

```factor
:: discriminant ( a b c -- D )
    b sq 4 a c * * - ;

-- With locals via call(:
: quadratic-roots ( a b c -- r1 r2 )
    [let | a b c |
        b sq 4 a c * * - :> D
        b neg D sqrt + 2 a * /
        b neg D sqrt - 2 a * /
    ] ;
```

The `[let ... :> ...]` form binds stack values to local names. `call(` is
syntactic sugar that desugars to stack operations:

```factor
-- call( syntax:
[| a b | a b + b a - ] call( x y -- sum diff )

-- Desugars to:
x y [ dup >r >r + r> r> - ] call
-- (using retain stack to preserve values)
```

Factor thus preserves the stack-effect contract even with locals: the
declaration `call( x y -- sum diff )` still documents what the block consumes
and produces.

**Semantic idea**: locals are not a separate paradigm. They are a readability
layer that desugars to stack shuffling. This is the same pattern Nomi uses for
`_` holes, `$1` positional parameters, and `where:` bindings -- surface syntax
that reduces to core binding+call.

## 7. How Concatenative Code Composes vs Applicative Code

Consider summing the squares of even numbers:

**Applicative (Python)**:
```python
sum(x * x for x in numbers if x % 2 == 0)
```

**Applicative pipeline (Nomi/Elixir)**:
```nomi
numbers |> where(_ % 2 == 0) |> map(_ * _) |> sum
```

**Concatenative (Factor)**:
```factor
[ even? ] filter [ sq ] map sum
```

The concatenative version is shorter because: (1) no parameter name for the
collection, (2) no `|>` or `.` threading operator, (3) the data is always
implicitly "the next thing." But it is also harder to read for someone who
does not track the stack mentally.

The difference in composition models:

| Question | Applicative | Concatenative |
| --- | --- | --- |
| What is `f g`? | Apply f to g (application) | Do f, then g (composition) |
| How is data named? | Explicit parameters | Implicit on stack |
| How are functions composed? | `f . g` or `f >> g` | `f g` (juxtaposition) |
| Where does the data go? | Explicit argument position | Top of stack (convention) |
| How are multiple values returned? | Tuples, destructuring | Multiple values on stack |
| How do you read a program? | Inside-out or left-to-right | Left-to-right |

**Nomi note**: Nomi's pipeline `|>` gives the left-to-right readability of
concatenative code with the explicit data threading of applicative code. The
remaining gap is multi-value threading. A concatenative program naturally
passes multiple values through the stack; `|>` only passes one. Nomi might
consider whether destructuring at pipeline boundaries addresses this:

```nomi
(x, y) = compute() |> transform  -- single value
```

This is weaker than the stack model but clearer. It may be the right tradeoff.

## 8. What Patterns Transfer To An Applicative Language

| Concatenative pattern | Transferable? | Nomi surface |
| --- | --- | --- |
| Left-to-right composition | Yes | `|>` pipeline, `>>` composition |
| Stack effect declarations | Partial | Binding constraints on parameters; `func name(x: int, y: int) -> (sum, diff)` |
| `dup` (reuse a value) | Partial | `_` hole reuse, `where:` bindings |
| `dip` (operate on substructure) | Yes | `with` scope, context managers, `apply` |
| `bi` / `tri` (apply multiple functions to one value) | Yes | `apply(f, g)` or tuple output |
| `keep` (transform, preserve original) | Yes | `also` scope (Kotlin-like), debug trace |
| `curry` (partial application) | Yes | `_` holes, `partial` |
| `compose` (build pipelines as values) | Yes | `>>` and `<<` operators |
| `call(` (locals desugared to shuffling) | Transfer the pattern, not syntax | `_` holes, `$1` parameters, `where:` desugar to core binding |
| Quotations as first-class deferred code | Yes | Block values (already in Nomi) |
| Recursion combinators (`linrec`, `binrec`) | Library | `fold`, `scan`, recursion schemes as library functions |
| `if` as a function (not keyword) | No | Keep `if` as syntax; the cost of making control flow stack-based is too high |

### The Most Valuable Transfer: `dip` and the "temporarily remove" pattern

The `dip` combinator is the most underappreciated idea. It says: "save this
value aside, do work on everything else, then restore it." In applicative
code, this corresponds to:

```python
# "dip under": transform a substructure while preserving the outer shape
record = {**original, "nested": transform(original["nested"])}
```

Nomi's `with` or scope-function pattern could express this directly:
```nomi
data.with(.field = transform(it))  -- update one field, keep the rest
```

This is narrower than general `dip` but captures the same intuition: operate
on a part while the whole is preserved.

### The Non-Transfer: Stack Shuffling As A Daily Programming Model

Concatenative languages require the programmer to mentally track the stack
depth and order. This is a real cognitive cost. The combinators `swap`, `rot`,
`-rot`, `nip`, `tuck`, `over`, `2dup`, `2swap`, `pick`, `roll`, etc. form a
whole vocabulary for rearranging data that has no equivalent in applicative
code -- because applicative code names the data instead.

The lesson for Nomi: **naming is not boilerplate, it is cognitive support.**
Concatenative code eliminates names for conciseness, but pays for it with
mental stack tracking. Nomi should preserve names as the default and offer
point-free style (`_`, `$1`, `>>`, `|>`) as an opt-in for when names really
are noise.

## 9. Source-Language Quick Reference

### Forth
```forth
: square   dup * ;               \ define word: duplicate, multiply
: fact     dup 1 > if dup 1- recurse * then ;
3 square .                        \ prints 9
```

### Factor
```factor
USE: math.functions
: distance ( x y -- d ) [ sq ] bi@ + sqrt ;
3 4 distance .                   ! prints 5.0

: discriminant ( a b c -- D ) [ sq ] [ 4 * * ] [ ] tri* - ;

[ 1 2 3 4 5 ] [ even? ] filter   ! → { 2 4 }
[ 1 2 3 ] [ 10 * ] map           ! → { 10 20 30 }
```

### Joy
```joy
-- Definition without named parameters
DEFINE square == dup * .
DEFINE average == [+] 2cleave / .

-- Recursion combinator: factorial
[null] [succ] [dup pred] [*] linrec

-- Programs are quotations
[1 2 3] [dup *] map   -- → [1 4 9]
```

### Cat
```
define square { dup * }
define compose { [apply] dip apply }
-- Stack effect types inferred
```

### Kitten
```
define square (Int32 -> Int32):
  dup (*)

define twice<A> ((A -> A) A -> A):
  -> {f} x;
  x f f
```

## 10. Design Pressure For Nomi

Concatenative languages offer three durable ideas for an applicative language:

1. **Left-to-right reading order as the default.** Nomi's `|>` already does
   this. Function composition `>>` extends it to function building.

2. **Data-flow documentation that is independent of implementation.** Factor's
   stack effects are an extreme version of "what goes in, what comes out."
   Nomi's parameter constraints and result annotations serve the same role, but
   Factor's discipline of writing the contract first is worth emulating in
   teaching materials.

3. **Combinators as a shared vocabulary of data routing.** `dip`, `keep`, `bi`,
   `bi@`, and `compose` are not just Factor quirks. They represent universal
   patterns of how data flows through transformations. When a Nomi user writes
   `|> where(_ > 0) |> map(_ * 2)`, they are composing transformations in a
   way that directly parallels concatenative style, but with explicit data
   flow.

The line Nomi should not cross is making stack manipulation the default mental
model. Stack-based programming rewards experts but punishes readers. The right
balance is: pipeline for linear data flow, named bindings for non-linear flow,
and point-free holes for the short paths where names are truly overhead.
