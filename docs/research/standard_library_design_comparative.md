# Standard Library Design: Cross-Language Comparison

> Status: cross-language comparative research; active synthesis for Nomi design.
> Purpose: Understand how languages decide what belongs in the standard library,
> how it's organized, and what lessons apply to Nomi's prelude and stdlib design.

---

## Go

**What's included:** `fmt`, `io`, `net/http`, `encoding/json`, `encoding/csv`,
`database/sql`, `sync`, `context`, `testing`, `os`, `crypto`, `math`, `time`,
`strings`, `regexp`, `sort`, `errors`, `log`. About 150 packages. The signature
property of Go's stdlib is what it deliberately excludes: no GUI, no ML, no
async/await runtime (goroutines handle that at the language level), no ORM, no
HTML templating engine in stdlib (it has `html/template` but it's deliberately
simple).

**Organization:** Flat package namespace with domain-grouped prefixes:
`encoding/*` for serialization, `crypto/*` for cryptographic algorithms, `net/*`
for networking. Each package is small and focused. The `syscall` package is
deliberately sealed off from most users; platform abstraction lives in `os`.

**Prelude/auto-import:** There is no prelude. Everything is explicitly imported.
Even `fmt.Println` requires `import "fmt"`. This is a deliberate philosophical
choice: "every import documents a dependency."

**Inclusion criteria:** The Go compatibility promise (Go 1, 2012) froze the
language spec and stdlib API surface almost entirely. New stdlib additions go
through the proposal process on the Go issue tracker. The bar is high: the
feature must be broadly useful, impossible to implement outside stdlib, and
well-understood enough that the API will survive the compatibility freeze.
`golang.org/x/` serves as an incubation space where packages mature before
potential stdlib promotion.

**Stdlib growth:** Very slow by design. `context` was added in Go 1.7 (2016)
after years of discussion. `embed` was added in Go 1.16 (2021). `slices` and
`maps` generic packages arrived in Go 1.21 (2023). Deprecation is
documentation-only; the compatibility promise means nothing is ever removed.

**Key regrets:** The Go team has expressed regret about a few stdlib APIs:
`time.Parse` uses a reference time format string that is hard to remember
(`Mon Jan 2 15:04:05 MST 2006`); `database/sql` could have been designed
differently with generics in mind; `os.IsExist` and friends have confusing
semantics around wrapped errors. The `golang.org/x/` incubation model worked
well for `context` and `oauth2` but some x/ packages have languished for years
without promotion or deprecation.

**Nomi-relevant lesson:** Go's "explicit import" philosophy is the strongest
vote against a broad auto-imported prelude. The `golang.org/x/` incubation
model is a good pattern for Nomi's pre-stdlib feature incubation. Go's
compatibility promise is the extreme end of the stability spectrum — Nomi
should decide early where it sits on that spectrum.

---

## Rust

**What's included:** Rust splits into three tiers: `core` (no allocation, usable
in embedded/no_std), `alloc` (heap types like `Vec`, `String`, `Box`), and
`std` (full standard library: `std::io`, `std::net`, `std::sync`, `std::time`,
`std::fs`, `std::collections`, `std::thread`). `std` re-exports everything from
`core` and `alloc`. Notable inclusions: `std::sync::mpsc` channels, `Arc`, `Rc`,
`Mutex`, `RwLock`. Notable exclusions: HTTP client/server, JSON, CSV, random
number generation, regex — all live in crates.io.

**Organization:** Hierarchical module tree rooted at `std::`. `std::collections`
contains `HashMap`, `BTreeMap`, `HashSet`, `VecDeque`, `LinkedList`.
`std::sync` has concurrency primitives. `std::io` has `Read`, `Write`, `Seek`
traits and `BufReader`, `BufWriter`. The module tree is shallow: typically
`std::domain::specific`.

**Prelude/auto-import:** Rust has `std::prelude` — auto-imported in every
module. The 2021 edition prelude includes: `Clone`, `Copy`, `Drop`, `Eq`,
`PartialEq`, `Ord`, `PartialOrd`, `From`, `Into`, `AsRef`, `AsMut`, `TryInto`,
`TryFrom`, `Default`, `Iterator`, `Extend`, `ToString`, `FromStr`, `Box`,
`Option`, `Result`, `String`, `Vec`, `ToOwned`, `IntoIterator`, `FromIterator`.
The prelude is deliberately restricted to traits and fundamental types, NOT
functions or modules. Users can still need `use std::io::prelude::*` for I/O
traits. The prelude changes across editions, but additions are conservative.

**Inclusion criteria:** RFC process (https://github.com/rust-lang/rfcs) with
libs team review. The bar: "should this be in std, or should it be a crate?"
The default answer for new features is "crate first, std maybe later."
Stabilization requires real-world usage data from the crate ecosystem. The
`libc` crate and `rand` crate are canonical examples of things that are NOT in
std but are effectively part of the language's ecosystem.

**Stdlib growth:** Slow but deliberate. `std::time::Instant` was stabilized
after long debate. `HashMap` has gone through multiple internal rewrites (from
Robin Hood hashing to HashBrown SwissTable). Small additions happen in minor
releases. Deprecations are marked with `#[deprecated]` attributes and can
trigger warnings; actual removal only happens across edition boundaries.

**Key regrets:** `std::sync::mpsc` channels have known performance limitations
(they were chosen for simplicity over crossbeam-style MPMC). `std::io::Error`
predates good error handling patterns and is awkward to work with. Some feel
`HashMap` should have been a crate from the start to allow faster iteration.
The `libc` crate's quasi-std status creates confusion about what's actually
in the standard library.

**Nomi-relevant lesson:** The three-tier split (`core`/`alloc`/`std`) is a
pattern worth studying for Nomi's degrees-of-freedom ladder. The prelude
design — only traits and fundamental types, never functions — is a clean
boundary. The "crate first, std maybe later" policy is the right default for
any new language that has a package ecosystem.

---

## Python

**What's included:** One of the largest stdlibs in existence: `os`, `sys`, `io`,
`json`, `csv`, `sqlite3`, `http.server`, `urllib`, `socket`, `email`, `xml`,
`html.parser`, `threading`, `asyncio`, `multiprocessing`, `logging`,
`unittest`, `doctest`, `pathlib`, `typing`, `dataclasses`, `enum`, `functools`,
`itertools`, `collections`, `math`, `statistics`, `random`, `re`, `tkinter`,
`turtle`, `wave`, `zipfile`, `tarfile`, `subprocess`, `argparse`. The list
goes on. Python's philosophy is "batteries included" — you can build a web
server, parse XML, send email, and draw turtle graphics without a single
`pip install`.

**Organization:** Flat namespace with some domain groupings: `os.*`, `http.*`,
`html.*`, `xml.*`, `email.*`, `urllib.*`, `logging.*`, `unittest.*`,
`collections.*`. The top-level namespace is crowded. Module names follow
snake_case. Some of the groupings feel arbitrary (`urllib` is one package,
`http` is another, they should arguably be related).

**Prelude/auto-import:** Builtins — about 80 functions and types available
without import: `print`, `len`, `range`, `int`, `str`, `list`, `dict`, `set`,
`tuple`, `open`, `input`, `zip`, `map`, `filter`, `sorted`, `enumerate`,
`isinstance`, `type`, `Exception`, `True`, `False`, `None`. Python's builtins
are a mix of fundamental types, common operations, and debugging aids. The
builtin namespace is global and immutable — you can shadow names but you can't
remove them.

**Inclusion criteria:** Historically, a PEP and BDFL approval. The bar was:
"would a typical Python programmer need this?" In practice, this led to
inclusion of many packages (like `turtle`) that now feel like historical
artifacts. The modern bar is higher: new stdlib additions must justify why
PyPI is insufficient. Recent additions like `secrets` (PEP 506) and
`dataclasses` (PEP 557) cleared this bar by providing functionality that is
broadly useful and benefits from stdlib-level stability.

**Stdlib growth:** Heavy growth through Python 2.x and early 3.x. Slowed
significantly in Python 3.6+. Some modules are now "frozen" — they receive
bug fixes but no features (`audioop`, `crypt`, `imghdr`, `nntplib`,
`sndhdr`). PEP 594 (2020) scheduled 19 modules for removal in Python 3.13,
including `aifc`, `cgi`, `cgitb`, `chunk`, `msilib`, `pipes`, `smtpd`,
`sunau`, `uu`, `xdrlib`. These were deprecated because they're either
unmaintained, superseded, or tied to legacy protocols.

**Key regrets:** "Batteries included" led to a stdlib that is too large to
maintain well. Modules like `urllib` have confusing multi-file structures.
`http.server` is in the stdlib but explicitly not production-ready, creating a
confusing signal. The `re` module could be simpler (Go's `regexp` is a better
API). `subprocess` has too many ways to do the same thing. The `typing` module
initially underestimated how much type-system machinery would need to live in
the stdlib. The lesson: a large stdlib is a maintenance liability that
compounds over decades.

**Nomi-relevant lesson:** This is the cautionary tale. Nomi should explicitly
NOT be "batteries included" in the Python sense. A lean stdlib with a clear
remit is sustainable; a maximal stdlib becomes a museum of frozen code. The
"frozen module" concept is worth adopting — explicitly signal which modules
are in maintenance mode.

---

## Kotlin

**What's included:** Kotlin extends the Java standard library with:
`kotlin.collections` (extension functions on Java collections like `map`,
`filter`, `fold`, `groupBy`), `kotlin.sequences` (lazy evaluation),
`kotlin.text` (string manipulation), `kotlin.io` (file I/O helpers),
`kotlin.ranges`, `kotlin.coroutines` (core coroutine primitives). The Kotlin
stdlib is deliberately small because it depends on Java's much larger stdlib.
`kotlinx.coroutines` is separate from `kotlin.coroutines` — the former is the
full async framework, the latter is just the language-level primitives.

**Organization:** `kotlin.*` packages mirror the Java domains they extend.
`kotlin.collections` has extension functions on `List`, `Set`, `Map`.
`kotlin.io` has `use` (try-with-resources), `forEachLine`, `readText`.
`kotlin.let`, `.apply`, `.run`, `.also`, `.with` — the five scope functions —
are extension functions on `Any`. The `kotlinx.*` namespace is for non-stdlib
Kotlin-maintained libraries that ship separately.

**Prelude/auto-import:** Kotlin auto-imports the entire `kotlin.*` package
(about 50 top-level functions and extension functions): `println`, `listOf`,
`mutableListOf`, `mapOf`, `setOf`, `arrayOf`, `require`, `check`, `assert`,
`TODO`, `run`, `with`, `lazy`, `sequenceOf`, `emptyList`, etc. This is one of
the most aggressive auto-import strategies among modern languages. The
rationale: Kotlin's extension functions on Java types would be too verbose
without auto-import.

**Inclusion criteria:** JetBrains controls the Kotlin stdlib directly. New
stdlib additions go through the KEEP (Kotlin Evolution and Enhancement
Process). The bar: does this need to be in `kotlin.*` (auto-imported,
guaranteed stable) or can it live in `kotlinx.*` (opt-in, may evolve)? The
`kotlinx` namespace is the incubation zone, analogous to Go's `golang.org/x/`.

**Stdlib growth:** Measured growth with each Kotlin version. The stdlib grows
primarily through new extension functions on existing types. `kotlinx.*`
libraries (serialization, coroutines, datetime) grow faster and sometimes
graduate to tighter stdlib coupling without moving into `kotlin.*` proper.
Binary compatibility is a key constraint because Kotlin/JVM shares the JVM
ecosystem.

**Key regrets:** The scope functions (`let`, `apply`, `run`, `also`, `with`)
are powerful but confusing to newcomers — five functions with subtly different
receiver semantics is a learnability tax. The distinction between `kotlin.*`
and `kotlinx.*` is not always clear to users. Some extension functions in the
stdlib (`kotlin.io.readText`) have edge cases that surprise users (character
encoding defaults, large file behavior). The tight coupling to Java's stdlib
means Kotlin inherits Java's stdlib design decisions whether it wants to or not.

**Nomi-relevant lesson:** Extension functions on existing types — Kotlin's
signature move — create a tension with auto-import. When extension functions
are auto-imported, they become invisible dependencies that change the apparent
API of types the user didn't know were extended. Nomi should prefer explicit
imports for extension methods. The `kotlinx` incubation namespace is a good
pattern: clearly signal what's stable vs. evolving.

---

## Swift

**What's included:** The Swift Standard Library (`Swift` module) is small and
focused: `Array`, `Dictionary`, `Set`, `String`, `Int`, `Double`, `Bool`,
`Optional`, `Result`, `Range`, `Sequence`, `Collection`, `IteratorProtocol`,
`Codable`, `Encodable`, `Decodable`, `Error`, `Hashable`, `Equatable`,
`Comparable`. Foundation (a separate framework inherited from Objective-C)
provides `Data`, `Date`, `URL`, `FileManager`, `JSONEncoder`, `JSONDecoder`,
`Bundle`, `NotificationCenter`, `UserDefaults`, `RunLoop`. The split is
historical: the Swift stdlib is the pure-Swift layer; Foundation is the
Objective-C bridge. This split is actively being dissolved (swift-foundation
rewrites Foundation in Swift).

**Organization:** The Swift stdlib uses protocol-oriented design: `Sequence`
with associated type `Element`, `Collection` extends `Sequence`,
`MutableCollection` extends `Collection`, `RangeReplaceableCollection` extends
`MutableCollection`. Algorithms are protocol extensions — `map`, `filter`,
`reduce` are on `Sequence`, not on `Array`. Foundation uses a more traditional
class hierarchy but is moving toward protocol-based design too.

**Prelude/auto-import:** Swift auto-imports only the `Swift` module — types,
protocols, and free functions like `print`, `min`, `max`, `abs`, `zip`. No
Foundation types are auto-imported. This is a small, principled prelude: the
language's own types and operations. Everything else (including `Date`,
`JSONDecoder`, `FileManager`) requires `import Foundation`.

**Inclusion criteria:** Swift Evolution process — proposals via
forums.swift.org, reviewed by the Swift core team. The bar: must be something
that cannot be reasonably implemented in a package, must be broadly useful
across Swift's supported platforms (Apple, Linux, Windows), and must align
with Swift's API design guidelines. The swift-foundation project represents an
attempt to disentangle what should be cross-platform stdlib from what is
Apple-platform-specific.

**Stdlib growth:** Steady but conservative. New Collection algorithms (`isSorted`,
`endOfPrefix`) are added via the Swift Algorithms package first. New types
like `Result` were added after long community discussion. Deprecation uses
`@available(swift, deprecated)` and removal can happen across major Swift
versions (Swift 3 to 4 removed several older APIs).

**Key regrets:** The Foundation/Stdlib split is confusing — it is not obvious
to newcomers why `String` is in the stdlib but `Data` is in Foundation. The
Codable system is elegant but its error messages are notoriously unhelpful.
`String.Index` is not an `Int`, which is principled (Unicode correctness) but
frustrating for simple tasks. The `Result` type arrived late (Swift 5) after
years of everyone reinventing it; the language should have shipped it sooner.

**Nomi-relevant lesson:** Protocol-oriented stdlib design — algorithms on
protocols, not concrete types — is an excellent fit for Nomi's normal-forms
approach. The small, principled prelude (just the language's own types and
operations) is the right size. The stdlib/framework split is a warning: it
created two tiers of "standard" that confused users for years.

---

## Elixir

**What's included:** Elixir stdlib plus Erlang OTP gives a uniquely deep
runtime: `Enum` (eager collection operations), `Stream` (lazy/composable),
`Task` (lightweight async), `GenServer` (actor abstraction), `Supervisor`
(fault tolerance trees), `Agent` (simple state), `Registry` (name lookup),
`Application` (lifecycle), `Logger`, `File`, `Path`, `String`, `List`,
`Map`, `Keyword`, `IO`, `Inspect`, `Kernel` (language primitives), `Process`,
`Node`, `Module`, `Code`. This is arguably the deepest stdlib in any language
when you include OTP — you get a battle-tested actor system, distributed
computing, and fault tolerance primitives out of the box.

**Organization:** `Elixir.*` modules form the language layer:
`Elixir.Enum`, `Elixir.String`, `Elixir.Kernel` (the macro-defined language
primitives). `Erlang.*` modules form the VM layer: `:erlang`, `:ets`,
`:gen_server`, `:supervisor`, `:gen_tcp`. Elixir modules follow PascalCase;
Erlang modules are atoms with lowercase names. The convention is
protocol-defined operations: `Enumerable` protocol has `reduce/3`; `Enum`
module works on any `Enumerable`; `Inspect` protocol has `inspect/2`; `String`
module works on any `String.Chars`.

**Prelude/auto-import:** `Kernel` module is auto-imported — it contains
`+/2`, `-/2`, `=/2`, `==/2`, `is_atom/1`, `is_list/1`, `def/2`,
`defmodule/2`, `if/2`, `case/2`, `cond/1`, `raise/1`, `inspect/2`,
`IO.inspect/2`, `require/1`, `import/1`, `alias/1`. The auto-import is
substantial because Elixir's AST is macro-heavy and almost everything is a
function call under the hood. However, `Enum`, `String`, `Task` etc. are NOT
auto-imported — only the language-defining macros and guard-friendly predicates.

**Inclusion criteria:** José Valim and the Elixir core team manage the stdlib.
Additions go through the Elixir mailing list discussion and core team review.
The bar: must be a fundamental protocol, a broadly-applicable data operation,
or a core runtime service. Erlang OTP modules are maintained by the Erlang
team and Elixir inherits them automatically.

**Stdlib growth:** Elixir's stdlib grows slowly. `Enum` and `Stream` get new
functions in most minor releases. `Kernel` additions are rare and carefully
considered. The `D` (data validation) and `Nx` (numerical computing) packages
are deliberately kept outside stdlib. Deprecation uses `@deprecated` module
attributes with clear migration paths, and deprecation warnings are enabled
by default.

**Key regrets:** `Enum` and `Stream` have slightly different function sets
(`Enum` has `sort`, `Stream` doesn't) because not every operation makes sense
in both modes, but the asymmetry confuses users. The `Access` behavior
(`data[key]`) is inconsistently implemented across types. `Kernel` could
simplify by removing infrequently-used macros. The `String` module has some
functions that should arguably be in `Enum` (or vice versa).

**Nomi-relevant lesson:** Elixir's protocols (`Enumerable`, `Inspect`,
`Collectable`) are a model for how Nomi's normal forms can anchor stdlib
design: each normal form defines a protocol, and the stdlib provides both the
protocol and concrete implementations for built-in types. The `Kernel` + opt-in
module split is a good prelude boundary: auto-import only what the language
itself needs, require explicit import for everything else.

---

## Zig

**What's included:** A minimal, explicit stdlib: `std.ArrayList`,
`std.AutoHashMap`, `std.StringHashMap`, `std.fmt` (formatting), `std.io`,
`std.fs` (filesystem), `std.mem` (memory operations), `std.os` (OS
abstractions), `std.net`, `std.Thread`, `std.time`, `std.rand`, `std.testing`,
`std.json`, `std.zig` (language reflection). Everything in Zig's stdlib is
available in source form; the compiler compiles what's used.

**Organization:** Flat namespace under `std`. `std.mem` contains memory
operations: `copy`, `set`, `zeroes`, `eql`, `indexOf`, `startsWith`. `std.fmt`
contains formatting. `std.fs` contains filesystem operations. The structure is
pragmatic rather than hierarchical. Each module is a single `.zig` file.

**Prelude/auto-import:** `@import("std")` is required — nothing is
auto-imported. Zig has no prelude. Even `std.debug.print` requires explicit
import of `std`. This is the most extreme explicit-import stance among
modern languages.

**Inclusion criteria:** The stdlib is maintained alongside the compiler in the
same repository. Andrew Kelley and core contributors review additions. The
bar: "does this need allocator-passing and compile-time guarantees that
third-party libraries can't provide?" Zig's stdlib is explicitly incomplete
by design — things like HTTP clients, advanced data structures, and GUI
bindings are expected to live in the package ecosystem.

**Stdlib growth:** Steady but intentionally limited. The stdlib is versioned
with the compiler; breaking changes to the stdlib are acceptable before 1.0
(Zig is pre-1.0 as of 2024). After 1.0, the stdlib will stabilize. Zig's
design philosophy explicitly rejects stdlib maximalism: "If it can be a
third-party library, it should be."

**Key regrets:** The stdlib has accumulated some duplication (multiple hash
map implementations: `AutoHashMap`, `StringHashMap`, `AutoHashMapUnmanaged`,
`StringHashMapUnmanaged`) that could be unified with comptime. `std.fmt` has
some confusing default behaviors. `std.os` exposes platform-specific details
that leak through the abstraction. The decision to tie stdlib versioning to
compiler versioning means you can't upgrade the stdlib without upgrading the
compiler, which creates friction for library authors.

**Nomi-relevant lesson:** Zig's explicit allocator passing is a design
principle that Nomi should study for its memory model story. The "nothing
auto-imported" stance is the cleanest possible prelude design. The stdlib
being compiled from source alongside user code is a pattern that Nomi could
adopt for its own stdlib — no compiled artifact to link against, just the
source that gets compiled into the final binary. The UEFI/embedded/wasm tier
of Zig's stdlib is a lesson in portability: platform-specific parts are
behind comptime switches.

---

## C# / .NET BCL

**What's included:** The .NET Base Class Library is enormous and deeply
layered: `System.Linq` (functional collection operations), `System.Collections.Generic`
(`List<T>`, `Dictionary<K,V>`, `HashSet<T>`, `Queue<T>`, `Stack<T>`),
`System.Threading.Tasks` (`Task<T>`, async/await infrastructure),
`System.IO`, `System.Net.Http`, `System.Text.Json`, `System.Text.RegularExpressions`,
`System.Xml`, `System.Data`, `System.Diagnostics`, `System.Security.Cryptography`,
`System.Reflection`, `System.Globalization`, `System.Numerics`. The BCL is
managed by the .NET Foundation and ships as part of the .NET runtime.

**Organization:** Deep namespace hierarchy: `System.*` is the root,
`System.Collections.*` branches into generic, concurrent, specialized.
`System.Threading.*` branches into `Tasks`, `Channels`, `Timers`.
`System.IO.*` branches into `Pipes`, `Compression`, `MemoryMappedFiles`.
The naming convention is PascalCase with dots. The hierarchy is logical
but deep — finding the right namespace can require IDE assistance.

**Prelude/auto-import:** C# has implicit `using` directives (called "global
usings" in modern C#): `System`, `System.Collections.Generic`, `System.IO`,
`System.Linq`, `System.Net.Http`, `System.Threading`, `System.Threading.Tasks`.
This is substantial but configurable — projects can customize global usings
in their `.csproj` file. The `System` namespace provides `Console`,
`Math`, `GC`, `DateTime`, `String`, `Int32`, etc.

**Inclusion criteria:** .NET Foundation design reviews and community
proposals via the dotnet/runtime repository. The bar is high: the feature
must serve a broad .NET developer need, align with .NET design guidelines,
and be maintainable indefinitely. The `Microsoft.Extensions.*` namespace
serves as a semi-stdlib incubation zone (dependency injection, logging,
configuration, hosting).

**Stdlib growth:** Steady growth with each .NET release. .NET Core (now .NET 8+)
retained most of the .NET Framework BCL but deprecated legacy technologies
(`System.Web`, `System.Runtime.Remoting`, `System.EnterpriseServices`).
`System.Text.Json` was added as a modern alternative to `Newtonsoft.Json`.
`Span<T>` and `Memory<T>` were added to `System` for zero-allocation
slicing. The `Microsoft.Extensions.*` packages are versioned separately from
the runtime, allowing faster iteration.

**Key regrets:** The .NET Framework BCL accumulated too many overlapping APIs
over 20+ years (`ArrayList` vs `List<T>`, `Hashtable` vs `Dictionary<K,V>`,
`WebClient` vs `HttpClient`). The `System.Xml` namespace is a museum of XML
APIs that no one should use anymore but can't be removed. `DateTime` predates
`DateTimeOffset` and has implicit timezone behavior that creates bugs. LINQ's
deferred execution surprises newcomers. The `Microsoft.Extensions.*` ecosystem
is powerful but discouragingly large for newcomers to navigate.

**Nomi-relevant lesson:** Namespace hierarchy depth is a real usability tax —
C# needs deep nesting because the BCL is huge, but the result is hard to
navigate without IDE tooling. The LINQ pattern — extension methods on
`IEnumerable<T>` — is a powerful way to add operations without changing
the type. The `Microsoft.Extensions.*` separately-versioned incubation model
is a good alternative to Go's `golang.org/x/` for packages that need
independent versioning.

---

## Haskell

**What's included:** `base` package contains the core: `Prelude` (auto-imported
functions and types), `Data.List`, `Data.Maybe`, `Data.Either`, `Control.Monad`,
`Control.Applicative`, `Text.Printf`, `System.IO`, `Debug.Trace`, `Foreign.*`,
`GHC.*`. The Haskell Report specifies a minimal stdlib; GHC `base` is much
larger. Separate "blessed" packages provide essential functionality not in
`base`: `text` (efficient Unicode strings), `bytestring` (binary data),
`vector` (efficient arrays), `containers` (Map, Set, Seq, IntMap),
`unordered-containers` (HashMap, HashSet), `mtl` (monad transformer library),
`aeson` (JSON), `http-client`, `async`, `stm` (software transactional memory).

**Organization:** `base` uses a deep module hierarchy: `Data.*` for data
structures and operations, `Control.*` for control flow and monads,
`System.*` for OS interactions, `Foreign.*` for FFI, `GHC.*` for compiler
internals. The naming convention is `Data.Structure.Operation` or
`Control.Monad.Specific`. Package names on Hackage follow a flat namespace.

**Prelude/auto-import:** `Prelude` is auto-imported in every Haskell module.
It exports about 140 functions and types: basic types (`Bool`, `Int`,
`Integer`, `Char`, `String`, `Maybe`, `Either`, `IO`, `[]`), class-based
operations (`Eq`, `Ord`, `Show`, `Read`, `Enum`, `Num`, `Fractional`,
`Floating`, `Monad`, `Functor`, `Applicative`, `Foldable`, `Traversable`),
and functions (`map`, `filter`, `foldr`, `foldl`, `head`, `tail`, `init`,
`last`, `reverse`, `take`, `drop`, `++`, `!!`, `elem`, `lookup`, `maybe`,
`either`, `fst`, `snd`, `id`, `const`, `flip`, `(.)`, `($)`, `curry`,
`uncurry`, `error`, `undefined`, `seq`, and many more).

**Inclusion criteria:** The Haskell Report defines the language standard;
GHC's `base` is managed by the GHC team. Changes to `base` go through the
GHC proposals process. The bar for `base` inclusion is: fundamental to
Haskell programming, requires compiler support, or is so universal that
a separate package would be unnecessary indirection. The strong preference
in the Haskell community is to keep things in Hackage packages rather than
in `base`. Many prominent community members argue `base` should shrink, not grow.

**Stdlib growth:** Very slow. GHC `base` changes are conservative and often gated
by the Haskell Prime process (which moves even slower than GHC). Most innovation
happens in Hackage packages. `Data.Semigroup` was in `base` for years before
it was properly integrated. `MonadFail` was a multi-year migration. The
`Foldable`/`Traversable` move to `Prelude` (GHC 7.10) was controversial.

**Key regrets:** This section is long because Haskell's stdlib has the most
articulated regrets in language design. `Prelude` includes partial functions
(`head`, `tail`, `init`, `last`, `!!`, `read`) that crash on empty inputs
instead of returning `Maybe`. `String = [Char]` is a linked list of characters
— elegant but catastrophically inefficient for real string processing; this
single decision created the need for `text` and `bytestring` as separate
packages that now fragment the ecosystem. `Num` is a problematic typeclass
(it bundles `+`, `-`, `*`, `abs`, `signum`, `fromInteger` into one typeclass
even though many types need only some of these). `fail` was in `Monad` for
decades before being extracted. `Prelude` exports `map` but not the more
general `fmap` (though this is partially resolved by `fmap` being in
`Functor`). `Data.List` has 100+ functions — many are rarely used and create
a discoverability problem. The `text`/`bytestring`/`String` split means
beginners must immediately understand three incompatible string types before
they can write a useful program.

**Nomi-relevant lesson:** This is the canonical "prelude problem" case study.
The regrets are so well-documented that they form a checklist for Nomi:
(1) No partial functions in the prelude — use `Result`/`Option` return types
for operations that can fail. (2) The base string type must be efficient; don't
define it as a list of characters. (3) Typeclass/trait hierarchies should be
composable, not monolithic — small, single-purpose traits. (4) The prelude
should be minimal and curated; broad auto-import creates a legacy burden that
is politically impossible to undo. (5) Any type or function auto-imported
into every module will be used by decades of code — get it right the first time.

---

## Racket

**What's included:** Racket ships as a full language ecosystem: `racket/base`
(minimal: basic definitions, data structures, I/O), `racket` (the full
language: pattern matching, classes, units, contracts, futures, places,
delimited continuations, custodians), `racket/gui` (cross-platform GUI
toolkit), `racket/draw`, `racket/web-server` (production web server),
`racket/raco` (package management), `racket/contract` (design by contract),
`racket/stream`, `racket/set`, `racket/dict`, `racket/sequence`,
`racket/syntax` (macro infrastructure), `racket/match` (pattern matching),
`racket/struct`. Plus "teachpacks" for education: `htdp/bsl` (Beginning
Student Language) through `htdp/isl` (Intermediate Student Language).

**Organization:** Collections are organized by `collection/name`:
`racket/*` for the core, `net/*` for networking, `db/*` for databases,
`web-server/*` for web, `plot/*` for plotting, `pict/*` for pictures,
`slideshow/*` for presentations. Each collection provides multiple modules.
The `#lang` system means every file declares which language it uses
( `#lang racket` vs `#lang racket/base` vs `#lang scribble/base`). This
is a uniquely Racket approach: the "stdlib" depends on which language
you're writing in.

**Prelude/auto-import:** Racket's prelude depends on the `#lang`. `#lang racket`
auto-imports the full language, which is substantial. `#lang racket/base`
auto-imports a much smaller set. The design intentionally supports this
gradation — you opt into more language features by choosing a richer `#lang`.
Teachpacks further restrict what's available, creating a clean learning
progression.

**Inclusion criteria:** The Racket core team manages the core distribution.
Additions to `racket/*` require justification that they serve a broad need
and are coherent with the language's design. The package ecosystem
(`pkgs.racket-lang.org`) is the default venue for new libraries. Racket's
distribution ships many packages bundled, but they are managed through the
`raco` package manager, so they're technically separate from the core.

**Stdlib growth:** Racket releases include new packages in the distribution
and occasionally new core modules. The language levels system means most
"stdlib" growth happens through packages, not core. The `racket/base` vs
`racket` distinction has been stable for many releases.

**Key regrets:** The `racket` vs `racket/base` split is under-documented —
new users often don't know which to choose and default to the larger
`racket`, importing far more than they need. Some core modules have confusing
naming ( `racket/function` for function composition, `racket/list` for list
operations — why are these separate?). The language-level system is
powerful but creates a discoverability problem: "which module do I need?"
requires experience.

**Nomi-relevant lesson:** The `#lang`-based language levels are a unique
approach to the prelude problem: instead of a single auto-import set for
the entire language, let the programmer choose their level of abstraction.
Nomi could consider something similar: a hierarchical prelude where
different target environments (embedded, application, scripting) get
different auto-import sets. The teachpack model is also valuable —
providing restricted subsets for learning and for constrained environments.

---

## Cross-Language Synthesis

### What's structurally the same across good stdlibs

Virtually every language's stdlib provides these domains:

1. **Collections**: `List`, `Map`/`Dict`/`HashMap`, `Set`, with map/filter/reduce
   operations. The operations outlive the data structures — `Enum` in Elixir,
   `Iterator` in Rust, `IEnumerable` in C# are the real stdlib APIs.

2. **I/O primitives**: files, stdin/stdout/stderr, buffered reading/writing,
   path manipulation. Every language abstracts Unix/Windows differences
   differently, but the primitives are universal.

3. **String manipulation**: splitting, joining, trimming, searching,
   formatting. Unicode handling varies wildly (Rust and Swift do it right;
   Haskell famously does not).

4. **Error/Result types**: `Result` (Rust, Swift), `Either` (Haskell),
   `Result`/`Error` (Swift). Every modern language has a tagged union for
   success/failure. Go is the notable exception (multiple return + `error`
   interface).

5. **Basic math**: arithmetic, trigonometry, number parsing, random numbers
   (though random is often excluded from the minimal core).

6. **Testing**: `testing` (Go, Zig), `#[test]` attribute (Rust),
   `unittest`/`pytest` (Python). Testing support in stdlib is almost universal.

7. **Concurrency primitives**: threads, channels, mutexes, atomics.
   Async/await infrastructure is split between stdlib and ecosystem.

### What's genuinely different (real design choices)

#### Size: Go's minimalism vs Python's "batteries included"

Go believes in a small stdlib that covers essentials and lets the community
build everything else. Python believes in a stdlib so comprehensive that you
rarely need external packages. Go's approach scales better for maintenance
and compiler evolution; Python's approach was better for adoption in an era
before package managers were universal. Today, with mature package ecosystems,
the Go model is clearly superior for language maintainers.

The right question is not "how big should the stdlib be?" but "what
justifies inclusion?" Rust's answer: if it can be a crate, it should be.
Go's answer: if it's universally needed and benefits from the compatibility
promise, it should be in stdlib. Python's answer (historically): if it's useful.

#### Prelude: auto-import philosophy

| Approach | Languages | Trade-off |
|----------|-----------|-----------|
| No prelude (import everything) | Go, Zig | Maximum clarity, maximum boilerplate |
| Minimal prelude (traits + fundamental types only) | Rust, Swift | Clean boundary, some boilerplate |
| Language kernel (primitives + macros) | Elixir | Good for AST-heavy languages |
| Broad prelude (common ops, functions) | Kotlin, Haskell | Low boilerplate, high namespace pollution |
| Configurable prelude | C# (global usings), Racket (#lang) | Flexible but complex |

The trend across newer languages (Rust, Swift, Zig) is toward minimal
preludes with explicit imports for everything else. The lesson from
Haskell's Prelude regrets is that broad auto-import creates obligations
you can never fully discharge.

#### Allocation model

| Model | Languages | How it shapes the stdlib |
|-------|-----------|--------------------------|
| GC, hidden allocation | Go, Python, Kotlin, Elixir, C#, Haskell, Racket | Stdlib allocates freely; APIs are simple |
| Ownership + borrowing | Rust | Stdlib APIs expose ownership semantics (`&self` vs `self`); some types need explicit `Rc`/`Arc` |
| Explicit allocator passing | Zig | Every stdlib function that allocates takes an `Allocator` parameter; the stdlib has `Unmanaged` variants that don't allocate |

This is the deepest structural difference. Zig's explicit allocator pattern
means the stdlib API surface is larger (managed + unmanaged variants for
every allocator-using type), but the control it gives the programmer is
commensurate. Nomi's allocation story will fundamentally shape its stdlib
API design.

#### Extension mechanism

| Pattern | Languages | How it works |
|---------|-----------|--------------|
| Extension functions on existing types | Kotlin | `fun String.isPalindrome(): Boolean` adds methods to `String` |
| Extension methods (LINQ) | C# | `static class Enumerable { static IEnumerable<T> Where(...) this IEnumerable<T> ... }` |
| Trait implementation on foreign types | Rust | `impl MyTrait for ForeignType { ... }` |
| Protocol conformance in extensions | Swift | `extension ForeignType: MyProtocol { ... }` |
| No extension, just free functions | Go, Zig | Functions take the type as first argument |

Extension mechanisms interact with the prelude problem: if extension
functions are auto-imported, users see methods they didn't know existed on
types they didn't know were extended. Kotlin embraces this; Rust rejects it
(trait methods are only visible when the trait is in scope). Nomi should
prefer the Rust approach: extensions are explicit, not invisible.

#### Core vs contrib split

| Language | Core stdlib | Incubation/contrib | Promotion path |
|----------|-------------|-------------------|----------------|
| Go | stdlib | golang.org/x/ | Proposal + review |
| Rust | std | crates.io (rand, regex, etc.) | RFC + stabilization |
| Python | stdlib | PyPI | PEP + BDFL/delegate |
| Kotlin | kotlin.* | kotlinx.* | KEEP + team review |
| Swift | Swift + Foundation | swift-package-manager ecosystem | Swift Evolution |
| .NET | System.* | Microsoft.Extensions.* | Design review |
| Elixir | Elixir + OTP | Hex packages | Core team review |
| Haskell | base + Prelude | Hackage | GHC proposals |

The incubation pattern is universal: have a lower-stakes place where APIs
can evolve before being frozen into the stdlib. Go's `golang.org/x/`,
Kotlin's `kotlinx.*`, Rust's "crate first" policy, and .NET's
`Microsoft.Extensions.*` all serve this function.

#### Deprecation policy

| Strategy | Languages | How it works |
|----------|-----------|--------------|
| Never remove | Go | Compatibility promise; deprecated items stay forever |
| Edition-based removal | Rust | Breaking changes only across edition boundaries (every 3 years) |
| Major version removal | Python, Swift, Elixir | Deprecated → warning → removed in next major version |
| Pre-1.0 instability | Zig | Breaking changes acceptable before 1.0 |
| Runtime versioning | .NET | BCL tied to runtime version; `Microsoft.Extensions.*` versioned independently |

### Key tensions when designing a stdlib

1. **Batteries included vs lean core.** The more you include, the more you
   maintain, the slower you can change, and the higher the bar for new
   additions. Python's experience is the cautionary tale; Go's is the
   success story (with the caveat that Go made this choice when package
   managers were mature).

2. **Stable vs evolving.** Once an API is in the stdlib, you're stuck with it.
   Go's `time.Parse` reference format, Rust's `mpsc` channels, Haskell's
   partial `head` function — all are immortal once included. This creates
   enormous pressure to "get the API right" before inclusion, which in
   turn slows down stdlib growth. The incubation zone pattern partially
   resolves this but creates its own confusion (what's stable vs what's not?).

3. **Naming and discoverability.** How do users find the right module? Go's
   godoc, Rust's rustdoc, and Elixir's hexdocs are excellent; Python's
   stdlib documentation is sprawling; Haskell's Hackage discoverability is
   poor without external guides. The stdlib's organizational structure IS
   its discoverability — good naming conventions matter enormously.

4. **The prelude problem.** The prelude shapes every user's mental model.
   Haskell's prelude teaches `String = [Char]` as normal. Rust's prelude
   teaches trait-based generics as normal. Every item in the prelude is a
   pedagogical commitment: "this is how you write programs in this language."

5. **Platform abstraction.** How much does the stdlib paper over OS
   differences? Go's `os` package is excellent at this. Zig exposes
   platform details but makes them compile-time. Python's `os` gives
   you a portable API but also an escape hatch to `os.name` and
   platform-specific modules. Rust's `std::fs` is cross-platform but
   exposes `std::os::unix` and `std::os::windows` for platform specifics.

### What breaks when combining approaches

- **Extension functions (Kotlin) + broad prelude (Haskell).** Auto-imported
  extension functions create invisible methods on types. Combined, you get
  name conflicts from methods you didn't know existed, on types you didn't
  know were extended. Resolution: Rust's explicit trait imports.

- **Explicit allocation (Zig) + GC (Go).** These are fundamentally
  incompatible allocation models. Nomi must choose one story or provide a
  clean bridging mechanism. The degrees-of-freedom ladder might accommodate
  both as different "freedom levels," but the transition must be explicit.

- **Protocol-based dispatch (Swift) + duck typing (Python).** The former
  resolves methods at compile time through protocol conformance; the latter
  resolves at runtime through `__getattr__`. Cross-language stdlib design
  can't easily combine these.

- **Lazy sequences (Elixir Stream, C# IEnumerable) + strict collections.**
  This works when clearly separated (Elixir's `Enum` vs `Stream`) but
  fails when implicit (Haskell's lazy-by-default lists). The lesson: make
  evaluation strategy explicit in the API.

### What Nomi should adopt

1. **Lean prelude shaped by normal forms.** The eight normal forms determine
   what must be in the prelude: binding, function, pattern, flow, block,
   data boundary, absence/result, explanation. Each normal form gets its
   core type(s) and a minimal set of operations. Nothing else is auto-imported.
   This gives the prelude a principled boundary: "if it's a normal form
   operation, it's in the prelude."

2. **Explicit imports by default.** Follow Rust, Go, and Zig: no broad
   auto-import. Exception: the normal-form types and their core operations
   (similar to Rust's prelude of traits and fundamental types). Extension
   methods require explicit import to be in scope.

3. **Stdlib as library conventions first.** The stdlib should demonstrate
   the conventions that Nomi libraries are expected to follow: allocator
   passing (if that's the model), error handling, naming, documentation.
   The stdlib is the exemplar, not the exhaust.

4. **Organization by normal form / domain.** Modules are named for what they
   do, not how they're implemented. A module for flow operations, a module
   for pattern operations, a module for I/O, a module for networking. The
   cross-language evidence strongly supports domain-based naming over
   implementation-based naming.

5. **Incubation zone.** A `nomi.x` namespace (or similar) where packages
   can mature before potential stdlib promotion. Clear documentation about
   the stability status of each package. The incubation zone is versioned
   independently from the stdlib core.

6. **Compatibility promise once in stdlib.** Once an API enters the stdlib,
   it is stable. Breaking changes require an edition/version boundary.
   Deprecation is available but removal is only across major versions.

7. **Protocol-oriented core.** Like Swift and Elixir, define protocols
   (traits) for the fundamental operations: `Iterable`, `Showable`,
   `Equatable`, `Comparable`, `Hashable`, `Encodable`, `Decodable`.
   Stdlib operations are defined on protocols, not concrete types.

### What Nomi should avoid

1. **Python's "everything in stdlib" approach.** Maintenance burden compounds
   over decades. Modules that seemed essential in 2005 (like `turtle` or
   `imghdr`) become maintenance anchors in 2025. The stdlib should be the
   essential foundation, not a museum.

2. **Haskell's controversial Prelude.** Partial functions (`head`, `tail`),
   inefficient default string type (`String = [Char]`), monolithic
   typeclasses (`Num`), and a bloated export list that can never be
   meaningfully reduced because of backward compatibility.

3. **Implicit imports that make code hard to trace.** Extension functions
   that appear from nowhere. Type conversions that happen silently.
   Auto-imported operators that shadow user-defined ones.

4. **Org-chart-driven module structure.** Python's `urllib` (five files,
   confusing structure) and .NET's deep namespace hierarchies are symptoms
   of letting implementation history dictate module organization. Domain
   concepts should drive module organization.

5. **Stdlib as the only way to do something.** If the stdlib provides a
   `Result` type, third-party code should be able to define their own
   result types that work with the same protocols. The stdlib should
   define protocols, not monopolize implementations.

6. **Premature optimization of the stdlib for performance.** Get the
   API right first; optimize later. Many stdlib regrets (Haskell's
   `String`, Rust's `mpsc`) come from optimizing for a performance
   characteristic that turned out to be the wrong one.

---

## Comparison Tables

### Stdlib Scope Matrix

| Domain | Go | Rust | Python | Kotlin | Swift | Elixir | Zig | C# | Haskell | Racket |
|--------|-----|------|--------|--------|-------|--------|-----|-----|---------|--------|
| Collections | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes |
| I/O | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes |
| Networking | Yes | Yes | Yes | Yes | - | Yes | Yes | Yes | - | Yes |
| HTTP client | Yes | - | Yes | - | - | - | - | Yes | - (pkg) | Yes |
| HTTP server | Yes | - | Yes | - | - | - | - | Yes | - (pkg) | Yes |
| JSON | Yes | - | Yes | - | Yes | Yes | Yes | Yes | - (pkg) | Yes |
| CSV | Yes | - | Yes | - | - | - | - | - | - (pkg) | - |
| SQL/database | Yes | - | Yes | - | - | - | - | Yes | - (pkg) | Yes |
| Testing | Yes | Yes | Yes | - (JUnit) | Yes | Yes | Yes | Yes | - (pkg) | Yes |
| Async/concurrency | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes | - (pkg) | Yes |
| CLI/argparse | Yes | - | Yes | - | - | Yes | Yes | Yes | - (pkg) | Yes |
| OS abstraction | Yes | Yes | Yes | Yes | - | Yes | Yes | Yes | Yes | Yes |
| Cryptography | Yes | - | Yes | - | - | Yes | - | Yes | - (pkg) | Yes |
| Math | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes |
| String ops | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes |
| Time/date | Yes | Yes | Yes | Yes | - | Yes | Yes | Yes | Yes | - (pkg) |
| Regex | Yes | - | Yes | - | - | Yes | - | Yes | - (pkg) | Yes |
| GUI | - | - | Yes (tk) | - | - | - | - | - | - | Yes |
| Web server | Yes | - | Yes | - | - | - | - | Yes | - | Yes |

Notes: `-` = not in stdlib (available as external package). `- (pkg)` = explicitly a
separate package in the language's ecosystem. Empty `-` = not emphasized by the language.
"Swift" entries marked `-` for networking/HTTP/OS reflect the Swift stdlib proper;
Foundation adds some of these but is a separate framework.

### Prelude Design

| Language | Auto-imported | Approx count | Can prelude change? | Notable inclusions | Notable exclusions |
|----------|---------------|-------------|---------------------|--------------------|--------------------|
| Go | Nothing | 0 | N/A | N/A | Everything requires import |
| Rust | Traits + fundamental types | ~25 traits + types | Across editions | Clone, Copy, Iterator, From, Into, Option, Result, Vec, String | All functions, all modules, all macros (except `vec!`) |
| Python | Builtins | ~80 | Very rarely, through PEP | print, len, range, int, str, list, dict | Collections, math, json, datetime |
| Kotlin | kotlin.* | ~50 functions | Rarely, through KEEP | let, apply, run, listOf, mapOf, println, require | kotlinx.*, kotlin.collections extension functions |
| Swift | Swift module | ~50 types + functions | Swift Evolution | Array, String, Optional, print, Result, Codable | Foundation types (Date, URL, JSONDecoder) |
| Elixir | Kernel macros + guards | ~120 | Core team review | +, =, def, if, case, is_list, raise, inspect | Enum, String, Task, GenServer |
| Zig | Nothing | 0 | N/A | N/A | std.debug.print requires `const std = @import("std")` |
| C# | Global usings (configurable) | ~10 namespaces | Configurable per project | System, System.Linq, System.Threading.Tasks | System.Text.Json (must be imported) |
| Haskell | Prelude | ~140 | Very rarely (GHC proposals) | Bool, Int, Maybe, Either, IO, map, filter, head, tail, fst, snd, (+), (-), ($) | Data.Map, Data.Set, Text, ByteString |
| Racket | Depends on #lang | Varies | Via language level choice | #lang racket imports ~hundreds; #lang racket/base imports ~scores | Packages must be explicitly required |

### Organization Philosophy

| Language | Naming convention | Directory/module structure | Core vs contrib split | Extension mechanism |
|----------|-------------------|---------------------------|----------------------|---------------------|
| Go | lowercase, flat prefix | domain-prefixed (`encoding/json`) | stdlib vs golang.org/x/ | Free functions, interfaces |
| Rust | snake_case, hierarchical | `std::domain::specific` | std vs crates.io | Traits (foreign impl allowed) |
| Python | snake_case, flat-ish | `domain.subdomain` | stdlib vs PyPI | Duck typing, magic methods |
| Kotlin | camelCase, flat | `kotlin.domain` | kotlin.* vs kotlinx.* | Extension functions |
| Swift | PascalCase types, camelCase methods | Module-based (Swift, Foundation) | Stdlib vs Foundation vs SPM | Protocol extensions |
| Elixir | PascalCase modules, snake_case fns | `Elixir.Module` | Elixir/OTP vs Hex | Protocols |
| Zig | camelCase, flat | `std.module` | std vs package manager | Free functions, comptime |
| C# | PascalCase, deep hierarchy | `System.Domain.Subdomain` | System.* vs Microsoft.Extensions.* | Extension methods (LINQ) |
| Haskell | PascalCase modules, camelCase fns | `Data.Structure` or `Control.Category` | base vs Hackage | Typeclasses |
| Racket | Collection-based | `collection/name` | `#lang racket/base` vs `#lang racket` vs packages | Macros, language levels |

---

## Design Principles for Nomi's Prelude and Stdlib

Based on the cross-language analysis, the following principles emerge:

1. **The prelude should be defined by the normal forms**, not by committee
   negotiation. If a type or operation is required to express one of the
   eight normal forms, it belongs in the prelude. If not, it requires
   explicit import. This gives a principled, defensible boundary.

2. **Explicit over implicit.** Every import documents a dependency. Extension
   functions are only visible when the providing module is in scope. No
   silent type conversions, no invisible imports, no magic names.

3. **Stdlib as exemplar, not exhaust.** The stdlib demonstrates how Nomi
   libraries should be written: naming conventions, error handling patterns,
   documentation style, memory model (if allocator passing is the model).
   It does not attempt to cover every domain.

4. **Protocols for operations, modules for implementations.** Like Swift's
   protocol-oriented design and Elixir's protocol system, define protocols
   for the fundamental operations and let the stdlib provide implementations
   for built-in types. Third-party types conform to the same protocols.

5. **Incubation zone with clear stability signals.** A `nomi.x` or similar
   namespace where packages mature. Each package signals its stability tier:
   experimental, stabilizing, stable, deprecated. Stable packages are
   candidates for stdlib promotion if they serve a universal need.

6. **Compatibility promise with edition escape hatches.** Once in stdlib,
   APIs are stable. Breaking changes require an edition boundary (Rust model)
   or major version increment. Deprecation is available but removal is
   constrained and well-signaled.

7. **Domain-organized, not implementation-organized.** Module names reflect
   what the user wants to accomplish, not how the code is structured
   internally. `collections`, `io`, `net`, `text`, `time`, `math` — the
   cross-language consensus is compelling and Nomi should follow it.

8. **Testability is a stdlib requirement.** Like Go and Zig, testing support
   should be in the stdlib. A language that requires external dependencies
   to run tests has failed at being a complete programming tool.

---

*Cross-language sources: Go standard library documentation and Go blog posts on
compatibility promise; Rust std documentation and RFC process; Python PEP
documentation (PEP 594, PEP 506, PEP 557); Kotlin documentation and KEEP
proposals; Swift Evolution proposals and stdlib documentation; Elixir
documentation and Erlang OTP design principles; Zig stdlib documentation and
Andrew Kelley's design talks; .NET BCL documentation and design guidelines;
Haskell Report, GHC documentation, and community discussions on Prelude design;
Racket Guide and language levels documentation.*
