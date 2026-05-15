# Array Language Research (Deep Dive)

> Status: raw research notes; not an active syntax spec.
>
> Scope: documentation-only. This doc extends `../convenience/array_languages.md`
> with deeper exploration of rank polymorphism, function trains, Uiua's
> stack-oriented model, BQN combinators, K/Q table operations, and broadcasting
> semantics across languages.
>
> Consolidation note: surface-level adoptable patterns (adverbs, broadcasting,
> til, qSQL) are already in `../convenience/array_languages.md`. This doc adds
> semantic depth and analysis of what is genuinely useful vs too dense.

## 1. Rank Polymorphism

Rank polymorphism is the core semantic idea of APL-family languages. Every
function has an intrinsic rank -- the number of leading axes it normally
operates on. When applied to an array of higher rank, the function is
automatically mapped over the remaining axes.

### Natural Rank

In J, every verb has ranks. The rank conjunction `"` makes them visible:

```j
+ b. 0       NB. rank of + is 0 0 0 (operates on scalars)
,. b. 0      NB. rank of ,. is _ 1 _ (operates on items = last axis)
```

A verb with rank 0 operates on scalars. When given a matrix, it maps over
every scalar:

```j
1 + i. 3 3    NB. scalar + matrix → add 1 to every element
 1 2 3
 4 5 6
 7 8 9
```

### Leading Axis Agreement

When two arrays of different rank meet, the one with lower rank is extended by
replicating along leading axes until ranks match. This is **leading axis
agreement** (J) or **prefix agreement** (BQN):

```j
1 2 3 + i. 3 3    NB. vector + matrix
 1 3 5             NB. adds 1 to first row, 2 to second, 3 to third
 5 7 9
 9 11 13
```

```bqn
1‿2‿3 + 3‿3⥊↕9    # same: vector extends down rows
```

In BQN, the rule is: the leading axes of the lower-rank argument must be a
prefix of the higher-rank argument's shape. If shapes are `s` and `t` with
`∧´s ≡ ∧´t`, the result shape is `s⌈t`.

### Rank vs NumPy Broadcasting

The critical difference between APL and NumPy:

| Property | APL/J/BQN | NumPy |
| --- | --- | --- |
| Alignment | Leading axes | Trailing dimensions |
| Scalar extension | Implicit (rank 0 always maps) | 1-sized dims stretch |
| Example: `(3,) + (3,4)` | Error (3 != 3,4 prefix) | Valid (trailing 3 matches, leading 1 stretches) |
| Example: `(3,1) + (3,4)` | Error | Valid |
| Example: `(3,4,5) + (3,4)` | Error (3 != 3,4,5 prefix) | Error |
| Example: `(4,5) + (3,4,5)` | Valid (4,5 is prefix) | Error |

**NumPy** aligns trailing dimensions:
```python
a = np.ones((3, 1))   # shape (3, 1)
b = np.ones((3, 4))   # shape (3, 4)
a + b                  # → shape (3, 4); a's dim 1 stretches to 4
```

**APL** aligns leading dimensions:
```apl
(3 4⍴⍳12) + (4⍴1)     ⍝ vector of shape (4) is a prefix of (3,4) → valid
(3 4⍴⍳12) + (3⍴1)     ⍝ shape (3) is not a prefix of (3,4) → error
```

**Julia** makes it explicit:
```julia
a .+ b                 # explicit broadcast via dot
broadcast(+, a, b)     # programmatic form
```

The leading-axis approach makes more operations "just work" for data frames
(add a summary row to a table), while trailing-axis makes more operations
"just work" for linear algebra (matrix-vector product expectations).

### BQN's Rank Operator

BQN makes rank explicit with `⎉` (rank):

```bqn
a +⎉0 b     # map + over scalars (cells of rank 0)
a +⎉1 b     # map + over rows (cells of rank 1)
a +˝ b      # +˝ is +⎉¯1 (map over last axis, i.e., columns)
a +˘ b      # +˘ is +⎉∞ (map over all axes)
m ⌽⎉0‿1 v  # rotate cells with rank 0 of left, rank 1 of right
```

This gives precise control over which axes are mapped vs treated as units.

**Nomi note**: rank is powerful but complex to explain. Julia's explicit `.`
operator is a simpler model that handles the 90% case (broadcast everything
element-wise). Nomi could start with Julia-style explicit broadcasting and
reserve rank specification as a library/later feature for numeric users.

---

## 2. Function Trains (J and BQN)

Trains are the tacit/point-free programming mechanism in J and BQN. They allow
composing functions without naming arguments.

### 3-Trains (Forks)

A 3-train `(f g h)` applied monadically means `(f y) g (h y)`:

```j
avg =: +/ % #        NB. (+/) sum divided by (#) length
avg 1 2 3 4          NB. → 2.5
```

The evaluation rule: `(f g h) y` → `(f y) g (h y)`. The middle function `g` is
applied to the results of the outer functions `f` and `h`. When applied to `x`
and `y` (dyadic), it means `(x f y) g (x h y)`.

```bqn
Avg ← +´÷≠           # BQN: sum (+´) divided by length (≠)
Avg 1‿2‿3‿4          # → 2.5
```

BQN trains:
```bqn
(√+) 25              # 3-train: sqrt of plus? No...
# Actually: (F G H) x → (F x) G (H x)
# In BQN, monadic hook = 2-train, monadic fork = 3-train
```

### 2-Trains (Atop / Hook)

A 2-train `(g h)` has different meanings depending on arity:

**J**:
- Monadic hook: `(g h) y` → `y g (h y)` -- right result becomes right argument to g
- Dyadic hook: `x (g h) y` → `x g (h y)` -- right result only

```j
(* +) 3              NB. hook: 3 * (+ 3) = 3 * 3 = 9
(, #) 1 2 3          NB. hook: (1 2 3) , (# 1 2 3) = 1 2 3 3
```

**BQN**:
- 2-train `(g h)` → `g (h y)` -- simple composition (atop), no hook
- `⊸` (before) and `⟜` (after) cover hook use cases

### Evaluation Is Mechanical, Not Magic

Trains have precise, context-free evaluation rules. There is no type inference
or resolution -- it is purely syntactic:

```
Monadic 3-train:  (f g h) y  →  (f y) g (h y)
Monadic 2-train:  (g h) y    →  y g (h y)        -- J hook
Monadic 2-train:  (g h) y    →  g (h y)          -- BQN (atop)
Dyadic 3-train:   x (f g h) y → (x f y) g (x h y)
Dyadic 2-train:   x (g h) y   → x g (h y)        -- J
Dyadic 2-train:   x (g h) y   → g (x h y)        -- BQN
```

This mechanical quality is why trains compose: `(f g h) j k` is another fork
where the left tine is `f g h` (itself a fork).

**Nomi note**: trains require the reader to internalize three distinct
evaluation rules (monadic 2, monadic 3, dyadic 2, dyadic 3). For Nomi's design
goals, explicit `_` holes and `$1` positional parameters are clearer:

```nomi
avg = (+ / _) / (len _)       -- explicit holes, no train rules
```

This is point-free enough for short transforms without requiring the reader to
learn a separate sub-language of train evaluation.

---

## 3. Uiuia: Stack-Oriented Array Model

Uiuia is a relatively new language that combines APL-style array programming
with a concatenative/stack-based evaluation model. It uses Unicode glyphs and
runs on a stack machine.

### Core Model

Values sit on a stack, as in a concatenative language. But the values are
arrays (like APL), and every function is rank-polymorphic. The result is a
system where you combine APL's whole-array thinking with concatenative
composition:

```
# Stack: [1 2 3 4 5]
+1                  # add 1 to each element → [2 3 4 5 6]
×2                  # multiply each by 2 → [4 6 8 10 12]
⊃+                  # reduce with + → 40
```

### Key Design Decisions

1. **Stack-based, not flat-array**: programs are sequences of functions that
   transform the stack. Each function pops inputs and pushes outputs.

2. **Arrays are the only data**: no scalars, no records (initially). Everything
   is an array, and the stack holds arrays of any rank.

3. **Functions are arrays too**: a function can be an array of glyphs or a boxed
   representation. This enables meta-programming within the array model.

4. **Glyphs are functions**: each Unicode character is a primitive function.
   There are no keywords (like J but unlike BQN which also has keywords).

5. **Rank polymorphism is the default**: every primitive operates with natural
   rank. No explicit `.` operator needed (unlike Julia).

### Why This Combination Matters

The APL+stack combination solves a real APL problem: deeply nested
parentheses. In APL, complex expressions often require reading inside-out
due to right-to-left evaluation with no operator precedence:

```apl
(+/[1] (2×⍳3 4)) ⌈ 10    ⍝ read from innermost: reshape, double, sum, max
```

In Uiua, stack order gives left-to-right reading:
```
↯3_4⇡12 ×2 ⊃/+
```

This is genuinely more readable for pipeline-style data transforms.

**Nomi note**: Nomi's `|>` already solves the same reading-order problem through
a different mechanism (explicit threading rather than implicit stack). Uiua
shows that concatenative + array is a viable combination, and validates Nomi's
choice to pursue pipeline style rather than APL-style right-to-left expression.

---

## 4. BQN's Combinators

BQN provides a small set of combinators that replace most of J's hook/fork
machinery with explicit, composable operators:

### `○` (Over / After) -- Compose

```bqn
F○G x       # → F (G x)       -- monadic: F after G
x F○G y     # → (G x) F (G y) -- dyadic: preprocess both args with G
```

```bqn
=○≠ "abc" "def"    # compare after length → 1 (both length 3)
≠○≠ "ab" "cdef"    # lengths differ? after length of length? No:
# ≠○≠ means: (≠ left) ≠ (≠ right) → 2 ≠ 4 → 1
```

This is the BQN equivalent of "on" from Haskell: `compare `on` length`.

### `⊸` (Before) -- Preprocess Left

```bqn
F⊸G x       # → (F x) G x        -- apply F to x, use as left arg to G
x F⊸G y     # → (F x) G y        -- preprocess left arg only

# Example: filter by predicate
(3⊸<)¨ 1‿2‿3‿4‿5    # → ⟨0 0 0 1 1⟩  -- 3 < each element
(3⊸≤)⊸/ ↕10          # indices where ≥3: ⟨3 4 5 6 7 8 9⟩
```

### `⟜` (After) -- Preprocess Right

```bqn
F⟜G x       # → x F (G x)        -- apply G to x, use as right arg to F
x F⟜G y     # → x F (G y)        -- preprocess right arg only

-⟜1 5       # → 4                -- 5 - 1
5 -⟜1 10    # → 5 - 1 = 4       -- (dyadic: preprocess right)
5 -⟜1 10    # wait, dyadic: F⟜G means x F (G y), so 5 - (1 10)?
```

Actually, BQN's `⟜` monadic is `x F (G x)`; dyadic is `x F (G y)`. Common
patterns:

```bqn
5 -⟜1      # decrement: 5 - 1 = 4
3 ⊑⟜1      # pick index 1: ⟨a b c⟩ ⊑⟜1 → b (equivalent to 1⊑)
```

### `˜` (Self / Swap)

```bqn
F˜ x        # → x F x            -- monadic: duplicate
x F˜ y      # → y F x            -- dyadic: swap arguments

+˜ 5        # → 10               -- 5 + 5
-˜ 5 2      # → 2 - 5 = ¯3      -- swapped subtraction
```

### The Design Philosophy

BQN's combinators replace J's implicit hook/fork evaluation with explicit
operator application. Where J says "a sequence of three verbs is a fork --
just learn the rule," BQN says "use `⊸`, `⟜`, `○`, `˜` to say exactly how
arguments flow." This makes tacit code more explicit but preserves
composability: combinators compose with each other and with trains.

**Nomi note**: BQN's approach to combinators is the more transferable one.
Explicit argument routing (`⊸` = preprocess left, `⟜` = preprocess right)
is easier to learn and debug than implicit train evaluation rules. Nomi's `_`
holes and `$1`/`$2` positional parameters serve the same role -- they make
argument flow explicit rather than positional.

---

## 5. K/Q Table and Query Operations

K and Q treat tables as first-class language values. The query syntax is
not a separate language; it is the host language.

### K9/Shakti Table Model

Tables in K are flipped dictionaries (column-oriented):

```k
t: +`name`age`salary!(("alice";"bob";"carol");25 30 28;50000 60000 55000)
t                                   / a table
```

Key operations:

```k
select name, salary from t where age > 26
update salary: salary * 1.1 from t where age > 26
delete from t where age > 26

/ Aggregation with by:
select avg salary by age_group: age % 10 from t
```

### K9's Functional Query Forms

K9 also allows programmatic construction via parse trees:

```k
?[t; (age > 26); (name; salary); ()]        / select
![t; (age > 26); (salary; salary * 1.1)]     / update
```

These parse trees enable query composition: build queries from parts, combine
conditions, add columns programmatically. But they use positional encoding
that is hard to read unassisted.

### Q's Query Syntax

Q makes the K query surface more SQL-like:

```q
select name, salary from t where age > 26

select total: sum qty, avgPrice: avg price
by sym, date.month
from trades
where date within (2026.01.01; 2026.03.31)

update value: price * qty from trades where side = `buy
delete from trades where qty = 0
```

Q's `select` differs from SQL in important ways:
- Columns are in scope as names (no `t.name` needed when table is clear)
- `by` groups without requiring every column in `by` or an aggregate
- Nested queries compose naturally because the result is a table
- No `GROUP BY` requirement that all non-aggregated columns appear there

Q also has `exec` (return a list/atom, not a table) and `update` (mutate in
place -- Q is a vector language, so `update` copies columns efficiently).

### Fby (Filter-By) -- Correlated Subqueries

```q
select from trades where price > (avg; price) fby sym
-- keep trades where price > average price for that sym
```

`fby` avoids the need for explicit subqueries in common cases.

### Window Operations

```q
select price, mavg: 5 mavg price by sym from trades
-- 5-element moving average per symbol
```

### What Makes This Work

1. **Column-oriented storage**: tables are columns of vectors, not rows of
   dictionaries. Operations on columns are vectorized by default.

2. **Columns as implicit names**: within `select`/`update`/`delete`, column
   names resolve in the table scope. No `table["col"]` noise.

3. **Queries are expressions**: `select ... from t where ...` is an expression
   that produces a table. It composes with `|`, assignments, function calls.

4. **`by` is simple**: grouping is one keyword. No distinction between
   `GROUP BY` and window functions.

5. **Functional parse trees**: the underlying representation is a parse tree
   (list of lists) that can be built programmatically.

**Nomi note**: this is the strongest pattern for Nomi's Track 5 (structured
collections). The key transferable ideas:
- Table as a language value, not just a library object
- Column-name resolution in table scope (like R's data masking, but simpler)
- Query expressions as composable pipeline stages
- Functional representation for programmatic query building
- `by` as simple grouping without SQL's GROUP BY complexity

---

## 6. Broadcasting Semantics: Julia vs APL vs NumPy

This is worth its own section because the differences are subtle and have
large consequences for everyday use.

### Julia: Explicit `.` Dot Broadcasting

```julia
# Element-wise: always explicit via dot
a .+ b          # element-wise addition
sin.(x)         # apply sin to each element
f.(x, y)        # broadcast f over x and y

# Fused assignment
x .= y .+ z     # write broadcast result into x in-place

# Macro for whole expressions
@. x = y + z * w   # everything is broadcast
# equivalent to: x .= y .+ z .* w
```

Key properties:
- Opt-in: no implicit broadcasting. You see every broadcast point.
- Fuses: `a .+ b .* c` is one fused loop, not two.
- Dotted assignment `.=` writes in-place.
- The rule is simple: `.` before an operator or after a function name.

### APL: Implicit Rank-Driven Extension

```apl
1 + 2 3 4            ⍝ scalar + vector → element-wise (rank 0)
(3 2⍴⍳6) + (2⍴1)    ⍝ shape (3,2) + shape (2) → prefix match, adds 1 to each column
```

Key properties:
- Opt-out: broadcasting is the default. Every primitive has rank.
- The rules are determined by function rank and leading axis agreement.
- No explicit operator needed in common cases.
- Rank errors occur when shapes are not prefix-compatible.

### NumPy: Trailing-Dimension Broadcasting

```python
a = np.ones((3, 4, 5))
b = np.ones((4, 5))       # trailing dims match → valid
c = np.ones((3, 1, 5))    # dim 1 stretches to 4 → valid
d = np.ones((3, 4))       # trailing 4 != 5 → error
```

Key properties:
- Implicit: broadcasting happens automatically for compatible shapes.
- Trailing alignment: the natural fit for linear algebra expectations.
- 1-sized dimensions stretch to match.
- Predictable but can silently produce wrong results for misaligned data.

### Which Model Is Best?

| Model | Good for | Bad for |
| --- | --- | --- |
| Julia (explicit `.`) | Readability, safety, debugging | Brevity in math-heavy code |
| APL (implicit, rank) | Math notation fidelity, dense transforms | Learning curve, rank errors |
| NumPy (implicit, trailing) | Linear algebra, ML pipelines | Silent wrong results, confusing errors |

**Julia's model is the strongest transfer to a general-purpose language.**
Explicit marking of broadcast points makes the semantics visible. It gives
the user control over whether an operation is element-wise without needing to
understand rank theory.

Nomi should adopt Julia-style explicit broadcasting:
```nomi
a .+ b           # element-wise addition
f.(coll)         # map f over collection
```

This is simpler than APL's rank model and safer than NumPy's implicit
broadcasting. The dot is visually lightweight and already familiar from Julia.

---

## 7. What Is Genuinely Useful vs Too Dense

### Genuinely Useful for a General-Purpose Language

| Pattern | Source | Why useful |
| --- | --- | --- |
| Explicit broadcasting (`.op`) | Julia | Visible, safe, handles 90% of array use cases |
| `each` / `over` / `scan` as prominent primitives | APL/Q | Replaces most explicit loops |
| Range syntax (`1..10`) | All array languages | Universal need, syntactic convenience |
| Left-to-right pipeline (`\|>`) | Uiua, concatenative, Q | Readable data flow |
| Table as first-class value with column-name scoping | Q, K | Query composition without SQL |
| `by` for simple grouping | Q | Cleaner than SQL GROUP BY |
| Combinators for explicit argument routing | BQN | Clearer than implicit train rules |
| `where` as unified filter+find | Q | Natural language-like readability |

### Too Dense for Nomi's Design Goals

| Pattern | Source | Why too dense |
| --- | --- | --- |
| Implicit rank polymorphism | APL/J | Cognitive cost of rank errors; Julia's explicit `.` is clearer |
| 3-trains/forks (implicit evaluation) | J | Three distinct evaluation rules; `_` holes are clearer |
| 2-trains/hooks (implicit evaluation) | J | Magic argument insertion; explicit combinators preferred |
| Unicode glyphs as the primary syntax | APL, BQN, Uiua | Typing, tooling, and learning barrier; keywords are more accessible |
| Tacit programming as the default style | J | Code golf vs readability; point-free should be opt-in |
| Stack-based evaluation | Uiua, Forth | Mental stack tracking adds cognitive load; pipeline is clearer |
| Right-to-left evaluation | APL/J (no precedence) | Breaks reading expectations for non-APL programmers |
| Functional parse trees for queries | K9 | Positional encoding is unreadable; syntax forms are better |

### The Useful Middle Ground

The sweet spot for Nomi is:
- Pipeline (`|>`) for linear data flow (concatenative, Uiua)
- Explicit broadcasting (`.op`) for element-wise operations (Julia)
- Prominent adverbs (`map`, `fold`, `scan`) for data transforms (APL/Q)
- BQN-style explicit combinators for argument routing (`_`, `$1`, `$name`)
- Q-style column-name scoping for table operations (with clear boundaries)
- Words, not glyphs, for the primary syntax surface

---

## 8. Summary Design Table

| Idea | Where it lives | Nomi fit |
| --- | --- | --- |
| Rank polymorphism (leading axis) | J, BQN | Future layer; start with explicit `.op` |
| Rank polymorphism (trailing axis) | NumPy | Too implicit for safety |
| Explicit broadcasting | Julia | **Adopt**: `.op` and `f.(x)` |
| Function trains (3-train fork) | J, BQN | **Reject**: learn `_` holes instead |
| Function trains (2-train hook) | J | **Reject**: use explicit argument routing |
| BQN combinators (`○`, `⊸`, `⟜`, `˜`) | BQN | **Adapt**: explicit `_`/`$1`/`$name` routing |
| Stack+array model | Uiua | Pipeline `\|>` already provides this |
| Table as first-class value | K, Q | **Adopt**: Track 5 structured collections |
| Column-name scoping in queries | Q | **Adopt**: with clear lexical-scope discipline |
| `by` for grouping | Q | **Adopt**: simpler than SQL GROUP BY |
| Query parse trees | K9 | **Defer**: syntax forms first, programmatic composition later |
| `til` / range | APL / Q | **Adopted**: `1..10`, `1..<10` |
| Adverbs (`each`, `over`, `scan`) | All array languages | **Adopted**: `map`, `fold`, `scan` as prominent primitives |
