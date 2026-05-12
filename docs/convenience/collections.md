# Collections & Iteration Convenience

## Map, Filter, Reduce Chain

Method-chaining on collections is the dominant pattern in modern languages.

**Ruby / JavaScript / Kotlin / Scala / Rust**:

```ruby
[1,2,3].map { |x| x * 2 }
       .filter { |x| x > 3 }
       .reduce(0) { |a,b| a + b }
```

```javascript
[1,2,3].map(x => x * 2).filter(x => x > 3).reduce((a,b) => a + b, 0)
```

```kotlin
listOf(1,2,3).map { it * 2 }.filter { it > 3 }.reduce { a,b -> a + b }
```

```rust
vec![1,2,3].iter().map(|x| x * 2).filter(|x| *x > 3).sum()
```

**Nomi** — works via block calls + hole lambdas:

```nomi
result = [1,2,3].map(_ * 2).filter(_ > 3).reduce(_ + _, 0)
```

---

## Pipeline Operator

Threads a value through a sequence of transformations.  The value becomes
the first argument (Elixir/OCaml) or fills a placeholder (R).

**Elixir / F# / OCaml / Roc**:

```elixir
[1,2,3,4,5]
|> Enum.map(&(&1 * 2))
|> Enum.filter(&(&1 > 5))
|> Enum.sum()
```

```fsharp
[1..5]
|> List.map ((*) 2)
|> List.filter (fun x -> x > 5)
|> List.sum
```

**Nomi proposal**:

```nomi
[1,2,3,4,5]
|> map(_ * 2)
|> filter(_ > 5)
|> sum
```

Implementation: `x |> f` desugars to `f(x)`.  With placeholder: `x |> f(_, y)` → `f(x, y)`.

---

## Ranges

**Python / Ruby / Kotlin / Swift / Rust**:

```python
range(10)           # 0..9
range(1, 10, 2)     # 1,3,5,7,9
```

```kotlin
1..10               // inclusive
1 until 10          // exclusive
1..10 step 2        // with step
(10 downTo 1)       // descending
```

```swift
1...10              // inclusive
1..<10              // exclusive
stride(from: 1, to: 10, by: 2)
```

**Nomi proposal**:

```nomi
1..10               // desugars to range(1, 11)
1..<10              // desugars to range(1, 10)
1..10//2            // desugars to range(1, 10, 2)
```

---

## Spread / Splat

**JavaScript / Python / Ruby / Kotlin**:

```python
combined = [*a, *b]
merged = {**a, **b}
first, *rest = items
```

```kotlin
val combined = listOf(*a, *b)
val (first, second) = pair
```

**Nomi** — Python-style already supported: `*args`, `**kwargs`, `a, *rest = seq`.

For collection literals: `[*a, *b]`, `{**a, **b}` (desugar to `list`/`dict` constructors).

---

## Slices

**Python / Rust / Go / Kotlin**:

```python
items[1:5]       # index 1 to 4
items[:5]        # start to 4
items[1:]        # 1 to end
items[::-1]      # reverse
items[::2]       # every other
```

**Nomi** — slice syntax already parsed.

---

## Lazy Sequences

**Haskell / Kotlin (Sequence) / Rust (Iterator) / Python (generator)**:

```haskell
take 10 [1..]     -- infinite list
```

```kotlin
generateSequence(1) { it + 1 }.take(10).toList()
```

```python
(x for x in range(1000) if condition)  # generator expression
```

**Nomi** — generator expressions work via Python.  Future: lazy collection adapters.

---

## Set / Dict Comprehensions

**Python / Elixir / Haskell / Scala**:

```python
{x * 2 for x in range(5) if x % 2 == 0}
{k: v * 2 for k, v in d.items()}
```

**Nomi** — Python syntax supported.

---

## Implementation Priority

| Feature | Effort | Impact |
|---------|--------|--------|
| `|>` pipeline | low | high |
| `1..10` range syntax | low | high |
| Spread in literals `[*a, *b]` | low | medium |
| Slice sugar | already | — |
| Lazy sequences | medium | medium |
| Scalar broadcasting `.op` | medium | very high |
| R `%>%` pipe | already via `\|>` | — |
| R formula `~` | niche | — |

