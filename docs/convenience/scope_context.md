# Scope & Context Convenience

## Where Clause (Local Bindings)

Define bindings local to an expression.  Already implemented in Nomi.

**Haskell**:

```haskell
area = pi * r * r
  where
    pi = 3.14159
    r = 5

roots a b c = ( (-b + d) / (2*a), (-b - d) / (2*a) )
  where d = sqrt (b*b - 4*a*c)
```

**Nomi** (implemented — block + inline forms):

```nomi
area = pi * r * r where:
    pi = 3.14159
    r = 5

result = x * 2 where x = 5        # inline
ss(x,y) = s(x)+s(y) where s(n)=n*n  # inline on equation
```

---

## Scope Functions (let / apply / also / run / with)

Execute a block with a value as context, returning a result.  Kotlin's
standard library defines five variants differing in receiver binding and
return value.

**Kotlin**:

```kotlin
// let:  value as argument, return block result
val len = "hello".let { it.length }

// run:  value as receiver, return block result
val len = "hello".run { length }

// apply: value as receiver, return value itself
val person = Person().apply {
    name = "Alice"
    age = 30
}

// also: value as argument, return value itself
val list = mutableListOf<Int>().also { it.add(42) }

// with: value as receiver (not extension), return block result
val s = with(person) { "$name is $age" }
```

**Swift** (similar patterns):

```swift
let label = UILabel().apply {
    $0.text = "Hello"
    $0.textColor = .red
}
```

**Nomi** — `where` clause covers the basic use case.  For receiver-style
(`apply`/`run`), could extend `where` or use block calls:

```nomi
person = Person() where:
    name = "Alice"
    age = 30

result = person where:
    name + " is " + str(age)
```

---

## Implicit / Context Parameters

Values automatically passed through the call chain without explicit
argument threading at every call site.

**Scala (given/using)**:

```scala
def sort[T](list: List[T])(using ord: Ordering[T]): List[T] = ...

given Ordering[Int] = Ordering.Int
sort(List(3, 1, 2))  // ord passed implicitly

// context function
def render(using ctx: Context): String = ...
```

**Kotlin (context receivers — experimental)**:

```kotlin
context(Logger)
fun process() {
    info("processing...")   // Logger method available
}
```

**Haskell (type classes)**:

```haskell
sort :: Ord a => [a] -> [a]
sort = ...   -- Ord dictionary passed implicitly
```

**Nomi** (Track 7 — capability scopes, `world` values, `using` blocks):

```nomi
func sort[T](list: list[T]) using Ordering[T] -> list[T]:
    ...

using ordering = int_ordering:
    sorted = sort([3, 1, 2])
```

---

## Builder DSL via Trailing Lambda

Domain-specific syntax using trailing block parameters.

**Kotlin**:

```kotlin
html {
    head { title("Page") }
    body {
        h1 { +"Welcome" }
        p { +"Content here" }
    }
}
```

**Groovy / Ruby (blocks)**:

```groovy
def xml = new MarkupBuilder()
xml.records {
    car(name: 'HSV', make: 'Holden', year: 2006)
}
```

**Nomi** — `block_call_stmt` enables this pattern.  DSL builders can be
written as library functions that yield values to blocks:

```nomi
html:
    head:
        title("Page")
    body:
        h1: "Welcome"
        p: "Content"
```

---

## Implementation Priority

| Feature | Effort | Impact |
|---------|--------|--------|
| Where clause | **done** | — |
| Scope functions (let/apply) | low | medium |
| Builder DSL | **done** (block_call_stmt) | — |
| Implicit parameters | high | high |
