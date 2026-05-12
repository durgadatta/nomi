# Array-Language Conveniences (APL / J / K / Q)

Patterns from APL-family languages that produce extreme conciseness.
These are the "three adverbs" model, SQL-like queries, and implicit
broadcasting — each can inspire simple features in a general-purpose
language.

---

## 1. Implicit Broadcasting (Scalar × Array)

In APL/J/K/Q, scalar operations automatically extend to arrays.

```q
1 + 10 20 30          / → 11 21 31
3 * 1 2 3             / → 3 6 9
```

```python
# Python needs explicit:
[1 + x for x in [10, 20, 30]]
list(map(lambda x: 3 * x, [1, 2, 3]))
```

**Nomi proposal** — implicit broadcasting for arithmetic:

```nomi
nums + 1        # same as [x + 1 for x in nums]
2 * nums        # same as [2 * x for x in nums]
nums1 + nums2   # element-wise, not concatenation
```

Requires distinguishing scalar ops from array ops. Julia uses `.` for this:
```julia
nums .+ 1       # explicit broadcast
nums1 .+ nums2  # explicit
```

Nomi could adopt the dot `.op` convention (less implicit, more explicit).

**Impact: very high** — eliminates most comprehension boilerplate for data transforms.

---

## 2. Three Universal Adverbs (each / over / scan)

The core idea: treat `each`, `over` (reduce), and `scan` (cumulative) as
**first-class language features**, not niche library calls.

**Q**:

```q
count each ("abc"; "de"; "f")      / → 3 2 1       (map)
(+) over 1 2 3 4                    / → 10          (reduce)
(+) scan 1 2 3 4                    / → 1 3 6 10    (cumulative)
```

**K**:

```k
+': 1 2 3 4         / each-prior: 1 3 5 7  (1, 1+2, 2+3, 3+4)
```

**J (tacit / point-free)**:

```j
avg =: +/ % #        / fork: sum divided by count — no variable names!
avg 1 2 3 4          / → 2.5
```

**Nomi — three adverbs as language primitives**:

```nomi
map(f, coll)          # → [f(x) for x in coll]
fold(+, 0, coll)      # → reduce
scan(+, coll)         # → [a, a+b, a+b+c, ...]

# Or as methods:
coll.map(f)           # each
coll.fold(+, 0)       # over
coll.scan(+)          # scan
```

`fold` and `scan` are already in the standard library. Making them
prominent, discoverable, and with clean syntax is the key.

**Impact: high** — replaces most explicit loops for data transforms.

---

## 3. Iota / Range Generation

The verb for "give me the first N integers."

| Language | Expression | Result |
|----------|-----------|--------|
| APL | `ι 10` | `1 2 3 4 5 6 7 8 9 10` |
| J | `i. 10` | `0 1 2 3 4 5 6 7 8 9` |
| K | `!10` | `0 1 2 3 4 5 6 7 8 9` |
| Q | `til 10` | `0 1 2 3 4 5 6 7 8 9` |
| Python | `range(10)` | `range(0, 10)` |

The beauty is that `til` / `ι` composes directly with other adverbs:
```q
1 + til 10           / → 1 2 3 4 5 6 7 8 9 10
sum til 100          / → 4950
```

**Nomi** — `range(10)` already works. A `1..10` range syntax (from `collections.md`)
would provide the composability: `1..10 | map(_ * 2) | sum`.

---

## 4. Where as Filter

In Q, `where` is both a filter and an index-finder.

```q
nums: 10 5 8 12 3
where nums > 7          / → 0 2 3        (indices where true)
nums where nums > 7     / → 10 8 12      (filter by boolean mask)
```

The same keyword serves two related purposes based on context:
- `where condition` → find indices
- `values where condition` → filter values

**Nomi** — `filter` and `find_index` are already separate. The name `where`
is taken by the where-clause for local bindings.

---

## 5. Q SQL: Select / Update / By / Where

Language-level query expressions on tabular/structured data (not a
separate query language).

```q
select total: sum qty, avgPrice: avg price
by sym
from trades
where date = 2026.01.01
```

```q
update value: price * qty from trades
```

```q
delete from trades where qty = 0
```

**Key properties:**
- Columns are implicit names in scope — no `row["sym"]`
- `by` groups for aggregation
- `select` creates a new table
- `update` modifies columns in-place
- All in the host language, composable with other functions

**Nomi** (Track 5 — structured collections and query language):

```nomi
trades
| select(sum(qty) as total, avg(price) as avg_price by sym)
| where(date == today)
```

---

## 6. Each-Left / Each-Right (Pairwise Broadcast)

```q
1 2 3 +\: 10 20       / each-left: add 1,2,3 to each of 10,20
1 2 3 +/: 10 20       / each-right: add 10,20 to each of 1,2,3
```

Creates a Cartesian product of operations without nested loops.

**Nomi** — `cross_map(f, A, B)` or `A.cross(B, f)`. Not an operator worth
baking into syntax — a library function suffices.

---

## 7. Forks and Hooks (Tacit / Point-Free)

J's implicit argument plumbing eliminates variable names entirely.

```j
avg =: +/ % #          / fork: sum(V) divided by length(V)
avg 1 2 3 4             / → 2.5
```

A **fork** `(f g h)` applied to `y` means `g(f(y), h(y))`.
A **hook** `(g h)` applied to `y` means `y g (h y)`.

**Nomi** — point-free style is partially supported via `_` holes
(`_ + _`), `_` in pipelines, and composition `<<` / `>>` (planned).
Full tacit programming (forks/hooks) requires a paradigm shift — not
worth the complexity for a general-purpose language.

---

## Summary of Adoptable Patterns

| Pattern | Source | Nomi Status | Impact |
|---------|--------|-------------|--------|
| Scalar broadcasting `.op` | Julia, APL | Not planned | Very high |
| `each` / `over` / `scan` as primitives | APL/Q | `map`/`reduce` exist | High |
| `til` / `1..10` range syntax | APL/Q | `range()` exists, `1..10` planned | High |
| Where as filter | Q | `filter()` exists | Medium |
| Q SQL: `select/by/where` | Q | Track 5 | High |
| Each-left / each-right | Q | Library | Low |
| Forks / hooks (tacit) | J | `_` holes partial | Low |
