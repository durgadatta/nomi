# TypeScript Type System: Deep Dive

> Status: source research for Nomi design.
> Purpose: Understand TypeScript's type system innovations — type narrowing,
> structural typing, union/intersection types, conditional types — and extract
> lessons for Nomi's constraint system, pattern matching, and data boundary
> design.

## 1. Type Narrowing / Flow Typing

Type narrowing is TypeScript's most distinctive contribution to practical type
systems. The type-checker traces control-flow paths and tightens a variable's
type as the code eliminates possibilities. This is not inference (guessing the
type once) but *refinement* (shrinking the type as the function body progresses).

### Control-flow-based narrowing

The checker re-evaluates types at each branch point. After a check, the
variable's type in that branch is the subset that satisfies the check:

- `typeof v === "string"` narrows `v` from `string | number` to `string` in the
  true branch and to `number` in the false branch.
- `v instanceof Date` narrows an object variable to the `Date` class.
- `"key" in obj` narrows a union of object types to those that contain the key.
- `v === null` / `v !== undefined` narrow by exact equality.
- Truthiness (`if (v)`) narrows away `null`, `undefined`, `0`, `""`, `false`,
  and `NaN` from the true branch.

The checker models this as a control-flow graph where each node carries a
refined type map for every in-scope variable. A branch that ends with `return`
or `throw` prunes the union for the code that follows — TypeScript knows
the function has already handled those cases.

### User-defined type guards

Programmers can teach the checker new narrowing rules:

```typescript
function isString(x: unknown): x is string {
    return typeof x === "string";
}
```

The `x is string` return type is a type predicate. After calling
`isString(v)`, the checker treats `v` as `string` in the true branch. The
companion `asserts x is Type` form narrows by throwing rather than returning
`false`, so the code after the call (with no branch) sees the narrowed type.

This is a deliberate escape from the closed-world assumption. The type system
cannot enumerate every user predicate, but it can *trust* them. The cost:
type predicates are unchecked assertions. If `isString` is wrong, the type
system lies.

### Discriminated unions

A discriminated union is a union of object types that each carry a literal
field — the discriminant — that the checker uses to route control flow:

```typescript
type Shape =
  | { kind: "circle"; radius: number }
  | { kind: "rect"; width: number; height: number };

function area(s: Shape): number {
    switch (s.kind) {
        case "circle": return Math.PI * s.radius ** 2;
        case "rect":   return s.width * s.height;
    }
}
```

Inside `case "circle"`, `s` is narrowed to the circle member. This is
exhaustiveness-checkable: if you omit a case, the return type no longer
unifies to `number` everywhere. Adding a `default: const _: never = s; return
_` branch forces the compiler to reject incomplete switches.

### Interaction with mutability

The narrowing story has a sharp edge around mutation. TypeScript narrows
`let` bindings freely because the checker can see every assignment in the
function body. It does not narrow properties of mutable objects or `const`
declared objects, because those could be mutated by a function call between
the check and the use:

```typescript
const obj: { x: string | null } = { x: "hello" };
if (obj.x !== null) {
    doSomething();  // could set obj.x = null
    console.log(obj.x.length);  // error: obj.x might be null
}
```

This is the soundness boundary. TypeScript chooses usefulness over soundness
in most places, but stops short of making the checker a false oracle for
concurrent mutation. The design philosophy: narrow when you can prove no
interleaving write, trust the developer otherwise.

### Cross-language comparison: type narrowing

| Language | Mechanism | Flow-sensitive? | User-definable? | Mutable-safe? |
|----------|-----------|-----------------|-----------------|---------------|
| TypeScript | Control-flow narrowing + type predicates | Yes | Yes (`x is T`) | Props of mutable objects: no |
| Kotlin | Smart casts (`is`, `!is`) | Yes | No (contracts are experimental) | Only for immutable locals (`val`) |
| Swift | `if let`, `guard let`, `switch` | Yes (pattern-bound) | No | Value types: yes; reference: guarded |
| Rust | `if let`, `match` with enum patterns | Yes | No (but `matches!` macro helps) | Ownership guarantees safety |
| Flow | Control-flow typing (same lineage) | Yes | Yes (`%checks`) | Similar to TypeScript |
| OCaml | Pattern matching on variants | Yes (match arm) | No | Immutable by default |
| Haskell | Pattern matching on constructors | Yes (case arm) | No | Immutable by default |

The lineage is interesting: TypeScript's flow typing descends from the Flow
type checker (Facebook, 2014), which itself drew on the occurrence typing of
Typed Racket. The key innovation TypeScript added was ergonomic type
predicates and broad adoption of discriminated unions as the everyday pattern.

### Nomi relevance

Nomi's pattern matching is the natural home for this capability. Rather than
teaching users separate `typeof`, `instanceof`, `in`, `=== null`, and custom
type guard syntax, Nomi can do all narrowing through a single `match` form
where each arm binds a refined pattern variable. The checker tracks which
arms eliminate which cases, and the `else`/fallthrough arm catches the
remainder. The `never`-style exhaustiveness guarantee (section 7) ensures
every case is handled.

The mutable-property tension is real for Nomi because Nomi allows rebinding.
If a name can be rebound between the check and the use, the narrow reading
is unsafe. The right rule: narrow the *pattern binding* in each arm, not the
original name. The pattern capture is immutable within its arm regardless of
what happens to the original binding.

---

## 2. Structural Typing

TypeScript matches types by shape, not by name. Two types are compatible if
they have the same required properties with compatible types — even if they
were defined independently and carry different names.

### Objects match by structure

```typescript
interface Point2D { x: number; y: number }
interface Vector2D { x: number; y: number }

const p: Point2D = { x: 1, y: 2 };
const v: Vector2D = p;  // OK: same shape
```

This is the opposite of nominal typing (Java, C#, Swift, Rust), where two
types with the same fields are distinct unless one explicitly extends or
implements the other. Structural typing makes TypeScript feel loose and
Python-like at the type level: if it walks like a duck, it is a duck.

### `interface` vs `type` — both structural

Despite syntactic differences (`interface` supports declaration merging;
`type` supports unions, intersections, and mapped types), both define
structural types. There is no nominal distinction between them. This
consistency is important: TypeScript never offers nominal semantics and never
pretends to.

### Excess property checking — the "freshness" exception

There is one deliberate violation of structural purity — excess property
checking on object literals:

```typescript
interface Point { x: number; y: number }
const p: Point = { x: 1, y: 2, z: 3 };  // error: 'z' does not exist in 'Point'

const obj = { x: 1, y: 2, z: 3 };
const p2: Point = obj;  // OK: obj is not "fresh"
```

A "fresh" object literal (one created at the point of assignment) is checked
for excess properties. A variable that happens to have extra fields is not.
This is a pragmatic compromise: it catches obvious typos in object literals
without breaking the structural compatibility that makes TypeScript useful
for working with JSON, API responses, and data transformations.

### Branded types — nominal simulation

When nominal guarantees are needed (e.g., distinguishing `UserId` from
`AccountId` even though both are strings), TypeScript uses branding:

```typescript
type UserId = string & { __brand: "UserId" };
type AccountId = string & { __brand: "AccountId" };

function makeUserId(id: string): UserId {
    return id as UserId;
}
```

The `__brand` property exists only at the type level (it is never a real
value), so there is no runtime cost. This is a workaround, not a language
feature. It works because `string & { __brand: "UserId" }` is structurally
distinct from `string & { __brand: "AccountId" }` — different brand values
mean different types.

### Cross-language comparison: structural typing

| Language | Default typing | Nominal escape | Override |
|----------|---------------|----------------|----------|
| TypeScript | Structural | Branded types (`& { __brand }`) | `as` cast |
| Go | Structural (interfaces) | None needed (interfaces are satisfied implicitly) | Type assertion |
| Python (mypy/pyright) | Nominal (classes) | Protocols (structural subtyping) | `typing.Protocol` |
| Scala 3 | Nominal (classes/traits) | Structural types (`{ def foo: Int }`) via reflection | Rarely used |
| OCaml | Nominal (variants, records) | Row polymorphism (objects, polymorphic variants) | `#field` syntax |
| Rust | Nominal (structs, enums, traits) | None (traits are nominal) | `unsafe` transmute |
| Swift | Nominal (structs, classes, enums, protocols) | None | `unsafeBitCast` |
| Kotlin | Nominal (classes, interfaces) | None | `as` cast |

Structural typing is rare among statically typed languages and common in
dynamically typed ones. TypeScript's genius was recognising that JavaScript
programmers already think structurally — objects are bags of properties — so
the type system should match that mental model rather than imposing nominal
discipline from outside.

### Nomi relevance

Nomi's data model is nominal by default: a `Point` and a `Vector` with the
same fields are different types, and a match on the type tag distinguishes
them. This is the right default for a language with runtime types.

But Nomi should support structural *patterns*: the ability to match "any
value with fields `x` and `y`" without naming the type. This gives the
TypeScript-like ergonomics for data transformation (process anything that
looks like a coordinate) without losing the nominal guarantees for API
boundaries and dispatch.

The branded-type pattern is a warning sign. When a language's users
repeatedly simulate a missing feature (nominal types) with a convention
(`__brand`), the language is rejecting a real need. Nomi should provide
nominal types directly so users do not invent branding conventions.

---

## 3. Union and Intersection Types

TypeScript's union and intersection types operate on sets of values — the
type system thinks in terms of "can this expression produce every value in
the declared type?"

### Union types (`A | B`)

A value of type `A | B` is either an `A` or a `B`. To use it, you must
narrow it (section 1). The union is untagged — there is no runtime
discriminant unless your types carry one. This is both the power (any ad-hoc
union works) and the danger (ad-hoc unions have no stable representation).

TypeScript uses unions for many things that other languages handle with
separate mechanisms:

| Concept | Other languages | TypeScript |
|---------|----------------|------------|
| Nullable types | `Option<T>` (Rust), `T?` (Kotlin/Swift) | `T | null` / `T | undefined` |
| Sum types | `enum` (Rust), `sealed class` (Kotlin) | Discriminated union |
| Error handling | `Result<T, E>` (Rust) | `T | Error` (informal) |
| Multiple return types | Overloading | `string | number` return |

The trade: one mechanism (union) replaces four, at the cost of making the
discriminant implicit rather than explicit.

### Intersection types (`A & B`)

A value of type `A & B` must satisfy both `A` and `B`. For object types, this
merges properties:

```typescript
type Named = { name: string };
type Aged = { age: number };
type Person = Named & Aged;  // { name: string; age: number }
```

For conflicting properties, the intersection resolves to `never` (for
primitives) or the more specific type (for objects). `string & number` is
`never` — no value is both a string and a number.

Intersections are useful for mixin patterns, extending types without
subclassing, and composing requirements at function boundaries. But they are
not a general-purpose type combinator: intersection distributes over object
types by merging properties, which is intuitive, but the behaviour for
functions (`((x: A) => void) & ((x: B) => void)`) is contravariant and
frequently surprises users.

### `never` — the bottom type

`never` is the type with no values. It appears in three roles:

1. **Exhaustiveness checking**: a `switch` default arm typed `never` proves
   all cases are handled.
2. **Function return type**: a function that always throws or never returns
   has return type `never`.
3. **Intersection conflict resolution**: `string & number` is `never`.

The `never`-as-exhaustiveness trick is a category-theoretic insight made
practical:

```typescript
function assertNever(x: never): never {
    throw new Error("Unexpected: " + x);
}
```

If the type system can prove the argument to `assertNever` is indeed
`never`, the switch is exhaustive. If a case is missing, the argument has a
concrete type and the call is a type error.

### `unknown` vs `any`

| Type | Safe? | Operations allowed | Use |
|------|-------|--------------------|-----|
| `unknown` | Yes | Nothing without narrowing | The safe top type; "I don't know what this is" |
| `any` | No | Anything — disables checking | Escape hatch; "trust me, don't check" |

`unknown` is the responsible top type: you cannot access properties, call
methods, or perform arithmetic on an `unknown` value without first narrowing
it. `any` is an opt-out from the type system: it is assignable to and from
everything. TypeScript added `unknown` in 3.0 (2018) precisely because `any`
was too permissive for the common case of "I don't know the type yet but I
promise to check before I use it."

### Cross-language comparison: union/intersection

| Language | Union mechanism | Intersection | Bottom type |
|----------|----------------|--------------|-------------|
| TypeScript | `A \| B` (untagged) | `A & B` (structural merge) | `never` |
| Kotlin | `sealed class` (nominal, tagged) | None | `Nothing` |
| Swift | `enum` with associated values (nominal, tagged) | Protocol composition (`A & B`) | `Never` |
| Rust | `enum` (nominal, tagged) | Trait bounds (`A + B`) | `!` (never type, unstable) |
| Scala 3 | `A \| B` (union types) + `enum` | `A & B` (intersection types) | `Nothing` |
| Haskell | `Either a b`, custom ADTs | N/A (no intersection types) | `Void` |
| OCaml | Polymorphic variants ``[`A \| `B]``, ADTs | Row polymorphism for objects | No bottom type |

TypeScript is unusual in having untagged unions as the *primary* mechanism.
Most languages use tagged/nominal unions (enums, ADTs, sealed classes) and
treat untagged unions as an advanced feature (Scala 3) or omit them entirely
(Rust, Swift, Kotlin, Haskell). The ergonomics favour TypeScript for ad-hoc
data transformation where creating a new enum for every intermediate union
would be ceremony-heavy. For API design and long-lived code, the nominal
approach gives better error messages and refactoring safety.

### Nomi relevance

Nomi should follow the ML-family consensus: discriminated (tagged) unions as
the primary union mechanism, not untagged unions. The discriminant makes
pattern matching straightforward, error messages precise, and refactoring
safe. Untagged unions (`A | B` as a type) are a sugar surface over tagged
unions with compiler-generated discriminants — useful for the "this function
returns a string or a number" case, but not the primary dispatch mechanism.

`never`-style exhaustiveness is a must-adopt. It is the category-theoretic
"bottom type" insight made usable: if the compiler can prove the remaining
case has type `never`, the match is exhaustive. Every Nomi `match` with a
type-annotated subject should benefit from this.

The `unknown` / `any` distinction translates directly into Nomi's constraint
model. `unknown` is the top of the constraint lattice — no constraint is
satisfied until the value is narrowed. `any` is the absence of constraints —
the opt-out. Nomi should provide both but name `any` in a way that signals
"you are leaving the checked world" (e.g., `unchecked`).

---

## 4. Conditional Types and Type-Level Programming

TypeScript's type system is Turing-complete, intentionally. The design
bet was that type-level computation, even at the cost of complexity, was
better than a simpler type system that programmers would work around with
casts and code generation.

### Conditional types

```typescript
type IsString<T> = T extends string ? true : false;
```

`T extends string ? X : Y` distributes over unions: if `T` is `string |
number`, the result is `IsString<string> | IsString<number>`, which is `true
| false`. Distribution is the key semantic property — it makes conditional
types useful for transforming union members individually rather than the
union as a whole.

### The `infer` keyword

`infer` captures a type variable from a structural pattern inside a
conditional type:

```typescript
type ReturnType<T> = T extends (...args: any[]) => infer R ? R : never;
type Flatten<T> = T extends Array<infer U> ? U : T;
```

This is type-level pattern matching. Instead of destructuring a value at
runtime, you destructure a type at compile time. The `infer` keyword creates
a type variable bound to whatever matched at that position.

### Mapped types

Mapped types iterate over the keys of a type and transform each property:

```typescript
type Readonly<T> = { readonly [K in keyof T]: T[K] };
type Partial<T> = { [K in keyof T]?: T[K] };
type Pick<T, K extends keyof T> = { [P in K]: T[P] };
```

This is type-level `map` over an object's properties. Combined with
conditional types, it enables precise type transforms:

```typescript
type Nullable<T> = { [K in keyof T]: T[K] | null };
type NonNullable<T> = { [K in keyof T]: NonNullable<T[K]> };
```

### Template literal types

TypeScript 4.1 (2020) introduced type-level string manipulation:

```typescript
type EventName<T extends string> = `on${Capitalize<T>}`;
// EventName<"click"> = "onClick"

type CSSValue = `${number}px` | `${number}em`;
// CSSValue matches "16px", "1.5em", etc.
```

Template literal types enable type-safe string DSLs: event names, CSS
values, routing paths, format strings. This is genuinely novel — no other
mainstream typed language has type-level string operations. The cost is
compile-time performance (large unions of template types expand
exponentially) and error messages that reference internal string type names.

### Recursive conditional types

TypeScript 4.1 also added support for recursion in conditional types
(previously forbidden beyond a shallow depth):

```typescript
type DeepReadonly<T> = {
    readonly [K in keyof T]: T[K] extends object
        ? DeepReadonly<T[K]>
        : T[K];
};
```

The compiler limits recursion depth to avoid infinite loops (default: 50),
but the capability is there. Combined with conditional types, mapped types,
and template literal types, the type system can express structural
transformations that previously required code generation.

### Cross-language comparison: type-level programming

| Language | Mechanism | Turing-complete? | String-level types? |
|----------|-----------|-------------------|---------------------|
| TypeScript | Conditional types + mapped types + template literal types | Yes | Yes (template literal types) |
| Haskell | Type families + type classes | Yes | No (type-level strings via `Symbol`) |
| Scala 3 | Match types + type-level tuples | Yes | No (type-level strings via literal singletons) |
| Rust | Const generics + trait bounds | No (deliberately) | No |
| OCaml | GADTs + module functors | Yes (module level) | No |
| Idris/Agda | Dependent types | Yes | Yes (strings are first-class types) |
| Zig | `comptime` (arbitrary code) | Yes (arbitrary code at compile time) | Yes (everything is comptime) |

The TypeScript approach is unusual: it builds type-level computation *on top
of* a structural type system, using set-theoretic operators (extends,
intersection, union) as its computation primitives. Haskell and Scala 3
separate type-level computation from term-level computation more cleanly.
Zig takes the opposite approach — eliminate the type/value distinction
entirely with `comptime`.

### Nomi relevance

TypeScript's type-level programming is impressive but it is a warning, not a
model. The Turing-complete type system is hard to debug (error messages
reference intermediate conditional types), has unpredictable compile-time
cost (template literal type expansion), and creates a second language
("mini-language" pattern from the integration critique) for type
computation.

Nomi should refuse this path. The language already has a computation model
(functions, pattern matching, binding). Adding a parallel type-level
computation model creates the two-languages problem: users must learn one
language for runtime and a different one for type/constraint transforms.

Instead, Nomi should make constraint/type transforms use the *same*
computation model as runtime code, evaluated either at constraint-check time
or via compile-time partial evaluation (in a future compiler). The Zig
approach — types are values, constraint transforms are just functions — is
conceptually cleaner. If a user wants `Readonly<T>`, they write a function
that transforms a constraint set, not a separate type-level language.

Template literal types are clever but too specialised for Nomi's first
layer. String-typed DSLs (event names, CSS values) are domain-specific
concerns that belong in libraries, not the core constraint system.

---

## 5. `as`, `satisfies`, `const` Modifiers

TypeScript provides several escape hatches and refinement operators that sit
between the type system and the programmer's intent.

### `as` — type assertion (unsafe cast)

`value as Type` tells the compiler to treat `value` as `Type` without
verification. It is an unchecked downcast:

```typescript
const el = document.getElementById("app") as HTMLDivElement;
```

If the element is not a `HTMLDivElement`, the type system lies and runtime
errors follow. TypeScript provides `as` because interop with untyped
JavaScript, DOM APIs, and JSON parsing requires it — not because it is a
good idea in general. The double-assertion `value as unknown as Type` is the
nuclear option: convert to the top type, then to any target type.

### `as const` — literal type widening prevention

TypeScript normally widens literal types: `"hello"` is inferred as `string`,
not as the literal type `"hello"`. `as const` suppresses this:

```typescript
const x = "hello";          // type: string
const y = "hello" as const; // type: "hello"
const obj = { x: 1, y: 2 } as const;  // type: { readonly x: 1; readonly y: 2 }
```

This is useful for discriminated unions, tuple types, and exhaustiveness
checking — anywhere you need the compiler to track exact literal values
rather than their widened types.

### `satisfies` — check type without widening

Added in TypeScript 4.9 (2022), `satisfies` verifies that a value matches a
type but preserves the narrower inferred type:

```typescript
const palette = {
    red: [255, 0, 0],
    green: "#00ff00",
    blue: [0, 0, 255],
} satisfies Record<string, string | number[]>;

// palette.green is inferred as string (the actual value type),
// not string | number[] (the constraint type)
palette.green.toUpperCase();  // OK: palette.green is string
```

Without `satisfies`, annotating `palette: Record<string, string | number[]>`
would widen `palette.green` to `string | number[]`, losing the knowledge
that it is a string. `satisfies` checks the constraint without losing
precision. This solves a real ergonomic problem: the conflict between "I
want the checker to validate this" and "I want the checker to remember
exactly what I wrote."

### `const` type parameters

TypeScript 5.0 (2023) added `const` type parameters:

```typescript
function identity<const T>(x: T): T { return x; }
const x = identity("hello");  // type: "hello", not string
```

This infers type arguments as if `as const` were applied. It is particularly
useful for generic functions that need to preserve literal types for their
callers.

### Cross-language comparison: casts and type modifiers

| Language | Upcast | Downcast (safe) | Downcast (unsafe) | Widening control |
|----------|--------|-----------------|-------------------|------------------|
| TypeScript | Implicit (structural) | Type guard narrowing | `as` | `as const`, `const T`, `satisfies` |
| Kotlin | Implicit | `as?` (returns null or cast) | `as` (throws on failure) | `const val` |
| Swift | Implicit (protocol) | `as?` (optional), `as!` (force) | `unsafeBitCast` | Literal type inference |
| Rust | `.into()`, `as` (numeric) | N/A (no downcast from traits) | `unsafe { transmute }` | Type annotation |
| Scala 3 | Implicit | `match` with pattern | `asInstanceOf` | Singleton type annotation |
| C# | Implicit, explicit cast syntax | `as` (returns null) | `(Type) expr` (throws) | N/A |

### Nomi relevance

`satisfies` is the most directly transferable idea. It solves a genuine
design tension: the user wants the compiler to check a constraint but does
not want the constraint to replace what the compiler knows about the actual
value. In Nomi terms: "check this constraint, but keep the concrete type."
This is a first-class operation, not an afterthought. Nomi should name it
something like `check` or `assert` (distinct from `match`, which
destructures rather than validates).

`as`-style unchecked casts should be refused. They are a JavaScript interop
necessity, not a language design feature. Nomi's runtime constraint model
means every cast can be checked. If the user wants to bypass checking, that
is a profiling/optimisation concern, not a type-system feature.

`as const` is an artefact of TypeScript's structural, inference-heavy type
system. In a nominal-first language where types are explicit, the widening
problem is less acute: the user writes the type, the compiler checks it. The
literal-vs-general distinction is a declaration-time choice, not an
inference-mode flag.

---

## 6. Declaration-Space vs Expression-Space

TypeScript inherits JavaScript's fundamental design: there is a type space
and a value space, and they are separate worlds that share syntax but not
semantics.

### Types are erased at runtime

TypeScript types do not exist at runtime. There is no `instanceof` check
against an interface, no reflection over a type alias, no dynamic
construction from a type. The compiler removes all type annotations and
emits plain JavaScript. This is TypeScript's "non-goal" #3 from the official
design goals: "Do not add runtime type information to the JavaScript output."

The consequence: type-level operations (`keyof`, conditional types, mapped
types) are compile-time only. You cannot write a function that takes a type
and returns a value, or that inspects a type at runtime to decide behaviour.

### `typeof` operator — two meanings

In value space, `typeof x` returns the JavaScript runtime string (`"string"`,
`"number"`, `"object"`, etc.). In type space, `typeof x` lifts the type of
the *value* `x` into a type:

```typescript
const config = { host: "localhost", port: 8080 };
type Config = typeof config;  // { host: string; port: number }
```

The same token does completely different things in the two spaces. This is a
common source of confusion for learners: "why does `typeof` sometimes return
a string and sometimes a type?"

### `keyof` operator

`keyof T` returns the union of property keys of `T` as a string literal
union type:

```typescript
type Keys = keyof { name: string; age: number };  // "name" | "age"
```

This is type-space only. There is no runtime `keyof` — you cannot iterate
over the keys of a type at runtime, only over the keys of a specific value.

### Value space vs type space: same syntax, different meanings

| Syntax | Value space | Type space |
|--------|-------------|------------|
| `typeof x` | `"string"`, `"number"`, etc. (runtime string) | The type of `x` (compile-time type) |
| `A & B` | Bitwise AND | Intersection type |
| `A | B` | Bitwise OR | Union type |
| `x is Type` | Never (only in return types) | Type predicate |
| `new T()` | Constructor call | Constructor type |
| `{ x: number }` | Object literal | Object type literal |

This dual meaning of syntax is TypeScript's most subtle design choice. It
feels natural to experienced users — types look like values because they
describe the shape of values — but it creates an invisible wall that
learners crash into repeatedly.

### Cross-language comparison: type/value separation

| Language | Types at runtime? | Separate type syntax? | Type ↔ value bridge |
|----------|--------------------|-----------------------|---------------------|
| TypeScript | No (erased) | Same syntax, different space | `typeof` (value → type) |
| Python (mypy/pyright) | Yes (types are objects) | Same syntax | `typing.get_type_hints()` at runtime |
| Zig | No (comptime is compile-time eval) | Types are just values at comptime | `@TypeOf`, `@typeInfo` (builtins) |
| Jai | Types are compile-time values | Types are just values | Arbitrary code at compile time |
| Julia | Yes (types are first-class values) | Same syntax | `typeof(x)`, dispatch on types |
| Rust | No (erased, except `dyn Trait`) | Separate syntax (traits vs structs) | `std::any::TypeId` (limited) |
| OCaml | Partially (modules exist at runtime) | Module types separate from values | First-class modules |

The deepest cut is between "types are erased" languages (TypeScript, Rust,
Haskell after compilation) and "types are values" languages (Python, Julia,
Zig, Jai). TypeScript inherits erasure from JavaScript's runtime model.
Nomi, running on Python's runtime, has types that exist — the question is
how to use them.

### Nomi relevance

Nomi should keep types/constraints as runtime entities. The language design
foundation says constraints are checked, not erased. This aligns with
Python's model (types are objects) and with Nomi's own design thesis
("explain what happened" requires runtime access to the constraint that
failed).

The `typeof` dual-meaning problem is a design smell. Nomi should avoid
syntax that means different things in different phases. If there is a
constraint-space operation (give me the constraint that describes this
value), it should have a distinct name or be accessed through an explicit
reflection mechanism rather than overloading a runtime operator.

The `keyof`-style type-level key enumeration is useful, but it should be a
reflection operation on a *constraint* (which exists at runtime), not a
compile-time-only type operator. Nomi's pattern matching on data fields
covers much of the use case without needing a separate `keyof` operator.

---

## 7. What TypeScript Deliberately Leaves Out

TypeScript's design goals explicitly exclude several features that other
typed languages treat as essential. Understanding these omissions clarifies
what TypeScript is — and what it is not.

### Nominal types

TypeScript has no `newtype` keyword, no nominal type alias, no way to say
"this `string` and that `string` are different types." The branded type
pattern (section 2) is a user-land convention. The design team has discussed
nominal types multiple times and consistently decided against them, arguing
that structural typing is the right match for JavaScript's dynamic object
model and that branding covers the few cases where nominal guarantees are
needed.

### Higher-kinded types (HKTs)

TypeScript cannot express `Functor<F>` or `Monad<M>` — type constructors
that abstract over other type constructors. This is a deliberate omission.
The design team considers HKT a power-to-confusion ratio problem: the
feature enables elegant library abstractions but the error messages,
inference complexity, and learning curve are high. The community has built
several HKT encodings using advanced conditional types, but none are
officially supported.

### Type classes / traits

TypeScript has no mechanism for "this type implements this interface because
these functions exist, even though nobody declared it." Interface
satisfaction is structural (the object has the properties) but there is no
decoupling of data definition from behaviour implementation. You cannot
write a `Comparable` trait and have `number` and `string` automatically
satisfy it through a separate `impl` block.

### Pattern matching

TypeScript has no dedicated pattern matching syntax. Discriminated union
narrowing via `switch` / `if` chains is the substitute. There is no `match`
keyword, no nested pattern destructuring, no guard clauses, and no
exhaustiveness guarantee beyond the `never` trick (section 3). The TC39
pattern matching proposal for JavaScript (which TypeScript would adopt) has
stalled at Stage 1.

### Exhaustiveness via `never`

The `never`-as-exhaustiveness pattern (section 3) is a user-discovered
technique, not a dedicated language feature. The compiler helps (narrowed
types in branches), but there is no `match` statement that the compiler
understands as "must handle all cases." This is a gap: exhaustiveness is the
right default for sum types, but TypeScript only achieves it through
discipline.

### Why these omissions make sense (for TypeScript)

TypeScript's design goal is "a typed superset of JavaScript." Every feature
must work within JavaScript's runtime semantics. Nominal types would require
runtime tags that JavaScript does not have. HKT would require type-level
lambda that JavaScript's type erasure cannot support. Pattern matching would
require new syntax that diverges from JavaScript's expression model.

The result is a type system that is *ingenious at checking JavaScript
patterns* but deliberately limited in the abstractions it can express. This
is TypeScript's coherence: it is not a new language with a type system; it
is a type system for an existing language, and the constraint is productive
rather than merely restrictive.

### Nomi relevance

These omissions are not flaws — they are the necessary consequence of
TypeScript's design goal (type-check JavaScript without changing its
runtime). Nomi has a different design goal (build a coherent language from
primitives up), so the calculus is different:

- **Nominal types**: Nomi should provide them. The language controls its own
  runtime and can tag values. Nominal types give refactoring safety, precise
  error messages, and the ability to distinguish semantically different
  things that have the same shape.
- **Higher-kinded types**: Defer to a later layer, if ever. The Nomi
  foundation explicitly defers advanced type-level proof and compiler-oriented
  cleverness. HKT is a power feature for library authors, not an everyday
  tool.
- **Type classes**: Interesting but not urgent. Nomi's constraint system can
  express "this value must satisfy these properties" through explicit
  constraints rather than implicit resolution. Explicit over implicit is the
  right default for a teachable language.
- **Pattern matching**: This is a first-class Nomi feature. It should cover
  discriminated unions, nested destructuring, guard clauses, and
  exhaustiveness — all the things TypeScript leaves to convention.
- **Exhaustiveness**: Nomi's `match` should guarantee exhaustiveness at the
  language level, not through a user-discovered `never` trick.

---

## Cross-Language Synthesis

### What's structurally the same

These features converge across languages even though the syntax and names
differ:

**Discriminated unions = Rust enums = Swift enums with associated values =
Kotlin sealed classes.** The core idea is identical across all four: a
finite set of named cases, each optionally carrying data, that can be
switched on with exhaustiveness checking. TypeScript encodes this pattern in
the type system without dedicated syntax; the other three make it a
first-class language construct. The semantic convergence is strong: tagged
sum types are the right answer to the question "how do I represent a value
that can be one of several distinct shapes?"

**Type narrowing by control flow = Kotlin smart casts = Swift `if let` /
`guard let` = Rust `if let` / `match`.** After a check, the compiler knows
more about the type. The mechanism differs (flow analysis, pattern binding,
or enum constructor matching) but the semantic effect is identical: a
variable has a broader type before the check and a narrower type inside the
branch.

**`keyof` / mapped types ≈ row polymorphism ≈ `derive` macros.** The
ability to iterate over the fields of a type and produce a transformed type
is a recurring need. TypeScript's `{ [K in keyof T]: ... }` is a built-in
type-level map. OCaml's row polymorphism gives structural object types with
`#field` access. Rust's `#[derive(...)]` macros do it at the syntax level
through code generation. Three different mechanisms for the same underlying
operation: "for each field, do something."

**`never` / `Nothing` / `!` / `Void` — the bottom type for exhaustiveness.**
The type with no values serves the same role everywhere: it proves a branch
is unreachable, and assigning the remaining case to it proves the match is
exhaustive. This is category theory (the initial object in the category of
types) made practical in compilers.

### What's genuinely different

**Structural vs nominal typing.** TypeScript matches types by shape; most
ML-family languages match by name. This is the single biggest philosophical
divide in type system design for everyday languages. Structural typing fits
data transformation and JSON-shaped programs. Nominal typing fits API design
and long-lived codebases. TypeScript chose structure because JavaScript is
structural. Rust chose nominal because refactoring safety matters more than
ad-hoc compatibility. Nomi should choose nominal with structural escape
hatches (matching by shape when explicitly requested).

**Erased vs retained types.** TypeScript types are gone at runtime. Python,
Julia, and Racket keep them alive. Erased types are simpler to implement and
faster at runtime. Retained types enable runtime reflection, dynamic
dispatch, and checked constraints. Nomi's core design commitment to
"constraints run at runtime" means it must retain types. The cost in
performance is acceptable for the target domain (scripts, data processing,
services) and can be recovered later through partial evaluation.

**Flow-sensitive vs declaration-sensitive narrowing.** TypeScript narrows
types through control flow analysis of the entire function body. Most typed
languages narrow only through pattern-matching bindings (Rust `if let`,
Haskell `case`). Flow sensitivity is more powerful but also more complex to
reason about, especially with mutation. Nomi should prefer
declaration-sensitive narrowing through pattern match bindings, with
flow-sensitive narrowing as a potential optimisation in a future compiler.

**Template literal types.** No other mainstream language has type-level
string manipulation. It is genuinely innovative, but it is also a
specialised feature whose use cases (type-safe event names, CSS values,
routing paths) are domain-specific. Nomi should defer this to libraries or a
later layer.

### Key tensions when synthesising

**Structural typing + pattern matching.** How do you match structurally
when you need nominal guarantees? If a `match` arm says `case { x, y }`,
does it match anything with `x` and `y` fields (structural) or only values
of a specific nominal type? The answer must be crisp: Nomi matches
nominally by default, structurally when the user opts in (e.g., with a
`pattern` or `shape` keyword). The TypeScript lesson is that structural
matching is useful for data transformation but dangerous for dispatch.

**Erased types + Nomi constraints.** Nomi wants runtime constraint checking.
TypeScript erases everything. The lesson is not that Nomi should erase its
constraints — it is that Nomi should design its constraint representation to
be cheap at runtime. A constraint that is structurally checkable (does this
value have an `x` field of type `number`?) can be compiled to a fast check.
A constraint that requires full type unification at runtime is expensive.
Design the constraint representation with this in mind.

**Type narrowing + mutation.** Flow typing breaks with mutation — if a value
can change between the check and the use, the narrow reading is unsound.
TypeScript handles this by not narrowing mutable object properties. Nomi's
rebinding model adds another dimension: a name can be rebound to a different
value. The safe design: narrow the *pattern binding* in each match arm, not
the original name. The pattern capture is immutable within its arm,
regardless of what happens to the original binding.

**`as` casts + safety.** TypeScript allows unsafe casts because JavaScript
interop demands it. Nomi is not interop-constrained in the same way. The
design should refuse unchecked casts in the core language. If a user wants
to bypass a constraint, they should do so explicitly (e.g., through an
`unchecked` block or a profiling mode), not through a silent `as` operator.

### What Nomi should adopt

1. **Discriminated unions as the primary union mechanism.** Untagged unions
   (`A | B`) are convenience sugar, not the core. The core is named cases
   with exhaustiveness checking.

2. **Type narrowing via pattern matching.** One form (`match`) covers
   `typeof`, `instanceof`, `in`, `===`, truthiness checks, and user-defined
   type guards. No separate narrowing syntax per check kind.

3. **`never`-style exhaustiveness.** The compiler proves every match is
   complete. The `never` type is the mechanism; the `match` keyword is the
   surface.

4. **`satisfies`-style constraint checking without widening.** "Check this
   constraint, but remember the exact type." A first-class operation named
   something like `check` or `assert` that validates without losing precision.

5. **`unknown` as the safe top type.** The type that says "I don't know what
   this is, and I promise to narrow before using it." The escape hatch
   (`any` equivalent) should exist but be named in a way that signals "you
   are leaving the checked world."

### What Nomi should refuse

1. **Structural typing as default.** The default is nominal. Structural
   matching is opt-in via explicit pattern syntax. This gives refactoring
   safety by default and structural convenience when needed.

2. **Type erasure.** Constraints are runtime entities. The language exists
   at runtime, and constraints are part of the language. The compiler may
   optimise away checks that are statically proven, but it never silently
   erases the constraint layer.

3. **`as`-style unsafe casts.** Constraints are checked, not bypassed. If
   the user needs an unchecked escape for optimisation, it is a profiling
   concern, not a type-system feature. The core language refuses silent
   downcasts.

4. **Type-level string manipulation.** Template literal types are a
   specialised feature for domain-specific DSLs. They do not belong in the
   first layer of a general-purpose language. Libraries can provide string
   validation; the compiler does not need to do string arithmetic at the
   type level.

5. **A separate type-level programming language.** Conditional types, mapped
   types, and `infer` together form a second computation model that users
   must learn. Nomi should keep one computation model (functions, pattern
   matching, binding) and apply it to constraint transforms the same way it
   applies it to value transforms. If the user wants to transform a
   constraint, they write a function — not a separate type-level expression.

---

## Comparison Tables

### Table 1: Feature Matrix

| Feature | TypeScript | Kotlin | Swift | Rust | Scala 3 | Haskell | OCaml |
|---------|-----------|--------|-------|------|---------|---------|-------|
| Structural typing | Default | No | No | No | Opt-in (structural types) | No (type classes) | Opt-in (row polymorphism) |
| Nominal typing | Via branding | Yes (classes) | Yes (structs/classes) | Yes (structs/enums) | Yes (classes/enums) | Yes (data/newtype) | Yes (variants/records) |
| Untagged unions | `A \| B` | No | No | No | `A \| B` (3.x) | No (use `Either`) | Polymorphic variants |
| Tagged/discriminated unions | Via discriminated union pattern | `sealed class` | `enum` with associated values | `enum` | `enum` | `data` / ADTs | Variants / GADTs |
| Type narrowing | Control-flow + type predicates | Smart casts | `if let` / `guard let` | `if let` / `match` | `match` | `case` | `match` |
| Exhaustiveness | Via `never` trick | `when` + sealed | `switch` | `match` | `match` | `case` | `match` |
| Conditional types | `T extends U ? X : Y` | No | No | No (const generics) | Match types (3.x) | Type families | GADTs |
| Mapped types | `{ [K in keyof T]: ... }` | No | No | `#[derive]` macros | No (scala-refined) | Generic programming | PPX derivers |
| Unsafe cast | `as` | `as` (throws) | `as!` (force) | `unsafe { transmute }` | `asInstanceOf` | `unsafeCoerce` | `Obj.magic` |
| Widening control | `as const`, `const T`, `satisfies` | N/A | Literal inference | Type annotation | Singleton types | N/A | N/A |
| Types at runtime | No (erased) | Partially (reflection) | Partially (Mirror) | No (erased) | Partially (reflection) | No (erased) | Partially |
| Bottom type | `never` | `Nothing` | `Never` | `!` (unstable) | `Nothing` | `Void` | No bottom type |
| Top type | `unknown` / `any` | `Any` | `Any` | N/A | `Any` | N/A | N/A |
| HKT | No | No | No | No (GATs partial) | Yes (kind projector) | Yes (core feature) | Yes (module functors) |
| Type classes / traits | No | No (interfaces) | Protocols | Traits | Given/using | Type classes | Module signatures |
| Pattern matching | Via `switch` only | `when` | `switch` | `match` | `match` | `case` | `match` |
| Template literal types | Yes | No | No | No | No | No | No |

### Table 2: Type Narrowing Mechanisms Across Languages

| Language | Mechanism | Trigger | Bind narrowed value? | Requires explicit check? |
|----------|-----------|---------|----------------------|--------------------------|
| TypeScript | Flow analysis | `typeof`, `===`, `in`, truthiness, type guards | No (original name narrows in scope) | Yes |
| TypeScript | Type predicates | Custom function returning `x is T` | No | Yes |
| Kotlin | Smart casts | `is` / `!is` check | No (original name casts in scope) | Yes |
| Swift | Optional binding | `if let x = opt` / `guard let x` | Yes (new name bound) | Yes |
| Swift | Type casting | `if let x = value as? Type` | Yes (new name bound) | Yes |
| Rust | `if let` | `if let Pattern = expr` | Yes (new names in pattern) | Yes |
| Rust | `match` | Arm pattern matches | Yes (pattern captures) | Yes |
| Scala 3 | `match` | Arm pattern matches type | Yes (pattern captures) | Yes |
| Haskell | `case` | Constructor pattern match | Yes (pattern captures) | Yes |
| OCaml | `match` | Constructor pattern match | Yes (pattern captures) | Yes |

**Pattern:** The ML family (Rust, Scala, Haskell, OCaml) binds narrowed values
through pattern captures — a new name is introduced for the narrowed value in
each branch. TypeScript and Kotlin narrow the *original name* in place, which
is more concise but breaks with mutation and alias analysis. Nomi should
follow the ML pattern: narrow through pattern bindings, not through in-place
narrowing of mutable variables.

### Table 3: Union Type Encoding Across Languages

| Language | Primary mechanism | Tagging | Exhaustiveness | Ad-hoc union? |
|----------|-------------------|---------|----------------|---------------|
| TypeScript | Discriminated union pattern (structural) | Literal field in type | `never` trick | Yes, `A \| B` directly |
| Kotlin | `sealed class` hierarchy | Class identity (nominal) | `when` over sealed | No |
| Swift | `enum` with associated values | Enum case (nominal) | `switch` | No |
| Rust | `enum` | Enum variant (nominal) | `match` | No, use `Either` crate |
| Scala 3 | `enum` + `A \| B` | Both: nominal (enum) and untagged (union) | `match` | Yes, `A \| B` |
| Haskell | ADT (`data`) | Constructor (nominal) | `case` | No, use `Either` |
| OCaml | Variants / polymorphic variants | Constructor / backtick tag | `match` | Yes, `` `A \| `B `` |
| Python | `Union[A, B]` (typing) | `isinstance` check at runtime | External tooling | Yes |

**Pattern:** Languages cluster into two groups. Nominal-first languages
(Kotlin, Swift, Rust, Haskell) use tagged unions with explicit discriminants
that the compiler can verify for exhaustiveness. Structural-friendly languages
(TypeScript, OCaml polymorphic variants, Scala 3) also support untagged
unions where the discriminant is implicit or absent. Nomi should be in the
first group (nominal-first, tagged) but provide syntactic sugar for the
second when appropriate.

---

## Source Notes

This analysis draws on:
- TypeScript handbook (type narrowing, discriminated unions, conditional
  types, mapped types, template literal types)
- TypeScript design goals and non-goals (documented since TS 1.0)
- Flow type checker (2014), Typed Racket (occurrence typing lineage)
- Kotlin language docs (smart casts, sealed classes)
- Swift language guide (enums, optional binding, type casting)
- Rust reference (enums, `match`, `if let`, never type)
- Scala 3 reference (union types, intersection types, match types, enums)
- Haskell 2010 language report and GHC extensions (type families, GADTs)
- OCaml manual (polymorphic variants, GADTs, row polymorphism)
- Nomi language foundation, specification, design dimensions, and integration
  critique (`docs/language/`, `docs/convenience/`)
