# Concurrency & Async Convenience

## Async / Await

Cooperative concurrency with familiar sequential syntax.

**JavaScript / Python / C# / Rust**:

```javascript
async function fetchData(url) {
    const response = await fetch(url)
    return response.json()
}
```

```python
async def fetch_data(url):
    response = await fetch(url)
    return response.json()
```

```rust
async fn fetch_data(url: &str) -> Result<Data, Error> {
    let response = reqwest::get(url).await?;
    response.json().await
}
```

**Nomi** — Python's `async def` / `await` available.

---

## Structured Concurrency

Scoped coroutines that ensure cleanup and prevent leaks.

**Kotlin (coroutineScope) / Swift (task group)**:

```kotlin
suspend fun loadAll(): Pair<Data, Data> = coroutineScope {
    val a = async { fetchA() }
    val b = async { fetchB() }
    Pair(a.await(), b.await())
}   // scope waits for both; cancels on failure
```

```swift
func loadAll() async throws -> (Data, Data) {
    try await withThrowingTaskGroup(of: Data.self) { group in
        group.addTask { try await fetchA() }
        group.addTask { try await fetchB() }
        let results = try await group.reduce(into: []) { $0.append($1) }
        return (results[0], results[1])
    }
}
```

---

## Parallel Collections

Apply operations concurrently across collection elements.

**Kotlin**:

```kotlin
val results = list.parMap { heavyComputation(it) }
```

**Scala (.par) / Rust (rayon) / C# (PLINQ)**:

```scala
results = list.par.map(heavyComputation)
```

```rust
use rayon::prelude::*;
let results: Vec<_> = list.par_iter().map(|x| heavy(x)).collect();
```

**Nomi** — could build on `async` with `map_async` or `par_map`.

---

## Channels / Actors (CSP / Message Passing)

Communicating sequential processes — goroutines and channels.

**Go / Kotlin (channels) / Clojure (core.async)**:

```go
ch := make(chan int)
go func() { ch <- 42 }()
val := <-ch
```

```kotlin
val ch = Channel<Int>()
launch { ch.send(42) }
val value = ch.receive()
```

**Elixir (actors)**:

```elixir
send(pid, {:hello, "world"})
receive do
    {:hello, msg} -> IO.puts(msg)
end
```

---

## Reactive / Stream Processing

Observable sequences with declarative operations.

**RxJava / RxJS / Kotlin Flow / Swift Combine**:

```kotlin
flow {
    for (i in 1..3) {
        delay(100)
        emit(i)
    }
}.map { it * 2 }
 .filter { it > 3 }
 .collect { println(it) }
```

---

## Atomic / Lock-Free Operations

**Rust / Java / Kotlin**:

```rust
use std::sync::atomic::{AtomicI32, Ordering};
let counter = AtomicI32::new(0);
counter.fetch_add(1, Ordering::SeqCst);
```

---

## Implementation Priority

| Feature | Effort | Impact |
|---------|--------|--------|
| Async/await | **done** | — |
| Structured concurrency | medium | high |
| Parallel collections | medium | medium |
| Channels / actors | high | medium |
| Reactive streams | high | low |
| Atomics | **done** (Python) | — |
