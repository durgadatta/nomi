# Deep Language Feature Survey

> Status: raw research notes. Not an active language spec.
>
> Scope: documentation-only. This document surveys deeper features in Haskell,
> OCaml, Agda/Idris, Swift, Kotlin, Scala 3, and F# that are not yet covered in
> Nomi's existing convenience research. For each feature, it names the problem
> solved, gives concrete syntax, describes the semantic model, and assesses
> whether the idea can be expressed in Nomi's normal forms (binding, function,
> pattern, flow, block, data boundary, absence/result, explanation).
>
> Consolidation: if a feature idea is promoted, fold it into a focused feature
> spec or the convenience roadmap. Keep this file as source material.

---

## 1. Haskell (deeper features beyond Nomi's existing coverage)

### 1.1 GADTs (Generalized Algebraic Data Types)

**Problem solved**: Ordinary ADTs use the same return type for every
constructor. GADTs let each constructor refine the type parameters differently,
so the type checker can learn new facts from pattern matching. This eliminates
impossible-states bugs and replaces runtime checks with compile-time
invalidation.

**Core syntax**:

```haskell
-- Ordinary ADT: all constructors return Expr a for the same a
data Expr a where
    Lit    :: a -> Expr a
    Add    :: Expr Int -> Expr Int -> Expr Int
    Eq     :: Expr Int -> Expr Int -> Expr Bool
    IfThen :: Expr Bool -> Expr a -> Expr a -> Expr a

-- Evaluation: the type index a guides what each case returns
eval :: Expr a -> a
eval (Lit x)      = x
eval (Add a b)    = eval a + eval b      -- a ~ Int here
eval (Eq a b)     = eval a == eval b     -- a ~ Bool here
eval (IfThen c t f) = if eval c then eval t else eval f
```

Notice: `Add` forces the type parameter to `Int`; `Eq` forces it to `Bool`;
`IfThen` accepts any `a`. Pattern matching on a constructor refines the type
index, so `eval (Add a b)` knows the return type is `Int` without casts.

Real-world use of GADTs for type-safe ASTs:

```haskell
data Term a where
    TInt  :: Int -> Term Int
    TBool :: Bool -> Term Bool
    TAdd  :: Term Int -> Term Int -> Term Int
    TAnd  :: Term Bool -> Term Bool -> Term Bool
    TEq   :: (Eq a, Show a) => Term a -> Term a -> Term Bool

-- No catch-all needed; each constructor constrains a
eval :: Term a -> a
eval (TInt n)    = n
eval (TBool b)   = b
eval (TAdd a b)  = eval a + eval b
eval (TAnd a b)  = eval a && eval b
eval (TEq a b)   = eval a == eval b
```

**Semantic model**: GADTs are an indexed family of types. Each constructor
carries a type equality constraint that the compiler records and uses during
pattern matching. The elimination rule for GADTs is "learn an equality
constraint, then proceed with the refined context."

**Nomi normal-form assessment**:

- **Data boundary**: A GADT is a `data` declaration where each variant carries
  an implicit type equality that refines the type parameters. Nomi's `data`
  today names variants but does not support per-variant refinement of type
  parameters.
- **Pattern**: Pattern matching on a GADT refines the type parameters in each
  case. This is pattern plus a type-level judgement that eliminates impossible
  cases. Nomi's pattern normal form already refines runtime values; GADTs show
  how to extend this to the type level.
- **Explanation**: GADT exhaustiveness and impossibility diagnostics are a
  natural extension of match diagnostics: "case Add is impossible in this
  branch because the type index is Bool, not Int."

Transferability: medium-low for Nomi's first everyday layer. GADTs require a
type checker with equality constraints. They could become a future-layer
extension of `data` with indexed type parameters. The diagnostic value is
high: "this case cannot occur" is more helpful than a runtime match failure.

---

### 1.2 Pattern Synonyms

**Problem solved**: Complex or deeply nested patterns become repetitive.
Pattern synonyms give a name to a pattern shape, used identically in
construction and matching contexts. They hide representation details without
needing a full abstraction barrier.

**Core syntax**:

```haskell
-- Unidirectional pattern synonym (pattern match only)
pattern Head x <- (x : _)

-- Explicitly bidirectional (construction and matching)
pattern Point2 x y = (x, y)

-- Bidirectional with different construct/match shapes
pattern IsZero :: Int -> Bool
pattern IsZero n <- (n == 0)
  where
    IsZero n = (n == 0)  -- explicit constructor side

-- Complex example: hide internal representation
data Tree a = Leaf a | Branch (Tree a) (Tree a)

pattern Empty :: Tree a
pattern Empty = Branch Empty Empty

pattern Singleton x = Branch (Leaf x) (Leaf x)
```

Usage:

```haskell
heading :: [a] -> Maybe a
heading (Head x : _) = Just x
heading _             = Nothing

-- Construction side
origin = Point2 0 0
-- Pattern matching side
case origin of
    Point2 x y -> x + y
```

**Semantic model**: A pattern synonym is a named pattern bundled with an
optional constructor. Unidirectionally, it's an alias for matching. Bidirectionally,
it's a pair of (pattern, expression) that are inverses. The compiler checks
bidirectionality when the synonym is defined.

**Nomi normal-form assessment**:

- **Pattern**: This is a direct extension of the pattern normal form. A pattern
  synonym introduces a named, reusable pattern that can appear anywhere a
  pattern is expected.
- **Function**: The constructor side of a bidirectional synonym is a function
  from bound names to an expression. This reduces to a function call.
- **Explanation**: Synonyms preserve diagnostic clarity by expanding to the
  underlying pattern in error messages, while showing the user's chosen name.

Transferability: high for Nomi. Nomi already has a pattern normal form. A
pattern synonym is a named pattern binding. The surface could be:

```nomi
pattern Point2D(x, y) = (x, y)  # named pattern
point = Point2D(3, 4)           # construction
match point:
    case Point2D(px, py):
        px + py
```

This is a data-boundary-adjacent pattern feature. It does not require GADTs or
dependent types.

---

### 1.3 View Patterns

**Problem solved**: Abstract types expose their structure through functions,
not directly. You cannot pattern-match on values you cannot see. View patterns
let you apply a function during matching and pattern-match on its result.

**Core syntax**:

```haskell
-- size returns an Int, but we pattern-match by range
size :: Seq a -> Int

describe :: Seq a -> String
describe (size -> 0) = "empty"
describe (size -> 1) = "singleton"
describe (size -> n) | n > 10 = "large"
describe _           = "small"

-- Complex example: matching on a Set's head/tail via views
data Set a = ... -- abstract

view :: Set a -> Maybe (a, Set a)

case mySet of
    (view -> Just (x, rest)) -> x : toList rest
    _                         -> []
```

**Semantic model**: A view pattern `(f -> pat)` evaluates `f value`, then
matches the result against `pat`. If the original value does not match any
case's view pattern, fall through to the next case. The view function runs
each time it's tried.

**Nomi normal-form assessment**:

- **Pattern**: The view is syntactic sugar that extends pattern matching to
  abstract types. It reduces to: evaluate `f(the_value)`, then match the
  result. This is pattern matching with a pre-transformation step.
- **Explanation**: Diagnostics must show both: "view function `size` returned
  5, which didn't match pattern `0`." The user doesn't see the internal
  structure, so the explanation must bridge the view layer.

Transferability: medium. Nomi's guard mechanism (`case pat if guard:`) already
covers the most common use: matching a derived property. View patterns add
convenience for the case where the derived property itself has structure to
match. Nomi could express this as a guard-let inside a match case:

```nomi
match value:
    case _ if let n = size(value) and n == 0:
        "empty"
    case _ if let n = size(value) and n == 1:
        "singleton"
```

The view-pattern surface is a pattern-level convenience, not a new semantic
model. Low priority for the first everyday layer.

---

### 1.4 Type Families and Associated Types

**Problem solved**: Type classes give overloading (same name, different
implementations by type), but sometimes the output type of an overloaded
function should depend on the input type. Ordinary type classes can't express
"given a container type, return its element type." Type families encode
type-level functions.

**Core syntax**:

```haskell
-- Open type family: can add instances anywhere
type family Element c
type instance Element [a]  = a
type instance Element Text  = Char
type instance Element (Map k v) = v

-- Associated type family: tied to a class
class Collection c where
    type Elem c
    empty   :: c
    insert  :: Elem c -> c -> c
    member  :: Elem c -> c -> Bool

instance Collection [a] where
    type Elem [a] = a
    empty   = []
    insert  = (:)
    member  = elem

instance Collection (Map k v) where
    type Elem (Map k v) = v
    empty   = Map.empty
    insert v m = ...

-- Closed type family: all cases in one place, tried in order
type family IfThenElse (cond :: Bool) (t :: *) (f :: *) where
    IfThenElse True  t f = t
    IfThenElse False t f = f
```

**Semantic model**: A type family is a function at the type level. Open
families allow new instances anywhere (like type classes). Closed families are
like pattern matching on types at definition time. Associated types are type
families defined inside a class, so each instance declares both the methods
and the type mapping. The compiler reduces type-family applications during
type checking.

**Nomi normal-form assessment**:

- **Function**: Type families are functions at the type level. Conceptually
  they reduce to "apply a compile-time function to type arguments to produce a
  type." Nomi does not have type-level computation in the first everyday
  layer.
- **Data boundary**: Associated types can express container structure (what
  an element type is). This is related to Nomi's type constraints like
  `list[int]` where `int` is the element type parameter.
- **Explanation**: Diagnostics here need to show "type family X applied to Y
  reduced to Z" -- similar to function-call tracing, but at compile time.

Transferability: low for the first everyday layer. Nomi intentionally
postpones full type inference and type-level computation. The practical need
(expressing element types of collections) is served by parameterized
constraints like `list[int]`. If Nomi later adds a static type discipline,
associated types become relevant as a way to express structural relationships
between types.

---

### 1.5 DerivingVia / DerivingStrategies

**Problem solved**: Many type classes have boilerplate implementations.
DerivingVia lets you reuse an existing instance for a newtype by routing
through an isomorphic type. DerivingStrategies disambiguates which deriving
mechanism (stock, anyclass, newtype, via) is being used.

**Core syntax**:

```haskell
-- Newtype with a type-level tag but the same runtime representation
newtype Age = Age Int
    deriving Show via Int
    -- "Show Age by converting to/from Int"
    -- equivalent to: instance Show Age where show (Age n) = show n

-- With DerivingStrategies, disambiguate:
newtype UserId = UserId UUID
    deriving stock    (Eq, Ord)      -- derived structurally
    deriving newtype  Show            -- use the wrapped type's instance
    deriving anyclass (ToJSON, FromJSON)  -- generic/anyclass derivation

-- DerivingVia for custom numeric-like semantics
newtype Total = Total Int
    deriving (Semigroup, Monoid) via Sum Int
    -- Total { getTotal = 5 } <> Total { getTotal = 3 } = Total { getTotal = 8 }
```

**Semantic model**: DerivingVia is type-level delegation. "Implement these
methods for NewType by converting the NewType to WrappedType, using
WrappedType's instance, and converting back." This is a compile-time
transformation that generates the boilerplate. It is entirely a type-level
and metaprogramming concern.

**Nomi normal-form assessment**:

- **Function**: Conceptually reduces to "generate a set of function
  implementations by composition with conversion functions." This is
  macro/synthesis territory.
- **Explanation**: The important diagnostic is: "method `show` on `Age`
  delegates to `show` on `Int` via `Age -> Int` conversion." This is
  traceable derivation.
- **Data boundary**: The routing-through-isomorphic-type idea is related to
  Nomi's explicit decode boundary. A type like `UserId` wrapping `int` could
  declare "delegate string representation to int." But this is a static
  type/metaprogramming concern.

Transferability: very low for the first Nomi layer. This is compiler-level
boilerplate generation. Nomi could achieve a similar goal with explicit
delegation at the binding level:

```nomi
data UserId(value: int)
UserAge(value: int, value >= 0)

# Reuse display from underlying type (hypothetical)
func display(id: UserId) -> str:
    return display(id.value)
```

The runtime equivalent is simple; the compile-time code generation aspect is
explicitly future-layer in Nomi.

---

## 2. OCaml (deeper features)

### 2.1 Polymorphic Variants (backtick syntax)

**Problem solved**: Ordinary variants are nominal -- `type color = Red | Blue`
requires advance declaration. Sometimes you want structural variants that
don't need a declaration: a function that accepts `[\`Red | \`Blue]` and a
function that accepts `[\`Red | \`Blue | \`Green]` should be composable
without a shared type declaration. Polymorphic variants solve ad hoc variant
composition.

**Core syntax**:

```ocaml
-- Polymorphic variants use backtick syntax
let color_to_code = function
  | `Red   -> "#FF0000"
  | `Blue  -> "#0000FF"
  | `Green -> "#00FF00"

-- The inferred type is a row-polymorphic variant:
-- color_to_code : [< `Red | `Blue | `Green ] -> string
-- "<" means "accepts these or fewer tags"

-- A function that accepts additional tags
let extended = function
  | `Red  -> "#FF0000"
  | `Blue -> "#0000FF"
  | `Rgb (r, g, b) -> Printf.sprintf "#%02X%02X%02X" r g b
-- [< `Red | `Blue | `Rgb of int * int * int ] -> string

-- Adding a tag to an existing set: row extension
let with_alpha color = function
  | `Alpha a -> (color, a)
  | _        -> (color, 1.0)
-- The type expresses: "input has `Alpha and possibly more;
-- return the original color type preserved"
-- with_alpha : [> `Alpha of float ] as 'a -> ('a * float)

-- Closed variants (exact set, no more, no less)
let is_primary = function
  | `Red | `Blue | `Green -> true
  | _ -> false
-- [> `Red | `Blue | `Green ] -> bool
-- ">" means "accepts these or more tags"
```

Key type annotations:
- `[< A | B]` -- upper bound: at most these tags (function can handle them)
- `[> A | B]` -- lower bound: at least these tags (caller must provide them)
- `[= A | B]` -- exact set: exactly these tags (closed variant)

**Semantic model**: Polymorphic variants are structural types based on row
polymorphism. A variant value `\`Red` has type `[> \`Red]` ("at least Red").
When you match on it, the match constrains the type to `[< \`Red | ...]`
("at most these cases"). The type checker infers the intersection of upper and
lower bounds, possibly leaving the row open with a row variable.

The backtick syntax is the constructor; there is no `type ... =` declaration.
Values with the same tag from different modules are the same type.

**Nomi normal-form assessment**:

- **Data boundary**: This is a data declaration without a declaration -- the
  tags are self-describing tokens. In CUE/Nickel terms, this is structural
  typing for variants. Nomi's `data` is nominal (you declare `Result[T,E]`
  with `Ok(value)` and `Err(error)`). Polymorphic variants are the structural
  alternative.
- **Pattern**: Pattern matching on polymorphic variants is identical to
  matching on nominal variants. The row-polymorphism aspect is a static type
  concern.
- **Explanation**: The principal diagnostic need is: "your match covers
  `Red | Blue` but the input might also be `Green`, which has no case."

Transferability: medium as a design concept, low as a syntax copy. Nomi's
first everyday layer prefers nominal data declarations. However, the
*structural variant* idea is useful for one-off pattern recognition where
declaring a full `data` type is overkill.

Nomi could grow a structural-variant surface:

```nomi
# Hypothetical: structural sum patterns
match color:
    case #Red:   "#FF0000"
    case #Blue:  "#0000FF"
    case #Green: "#00FF00"
```

This would extend the pattern normal form to include structural tags. The
`#` or backtick marker would distinguish structural from nominal constructors
(uppercase convention currently marks nominal constructors).

For everyday Nomi, the right initial posture is: use nominal `data` for owned
variants; use structural mapping patterns (`{"tag": "red", ...}`) for ad hoc
external structure. Polymorphic variants are most useful when a static type
system with row inference exists, which Nomi intentionally postpones.

---

### 2.2 First-Class Modules

**Problem solved**: OCaml modules are a powerful structuring mechanism, but
normally they're a separate language layer -- you can't pass a module to a
function or store it in a data structure. First-class modules let you pack a
module into a value, pass it around, and unpack it later with a structural
check.

**Core syntax**:

```ocaml
-- Define a module type
module type SHOW = sig
    type t
    val show : t -> string
end

-- Regular module implementing the type
module IntShow : SHOW = struct
    type t = int
    let show = string_of_int
end

-- Pack a module into a first-class value
let int_show : (module SHOW with type t = int) =
    (module IntShow)

-- Unpack it
let show_value (type a) (module S : SHOW with type t = a) (x : a) =
    S.show x

-- Or unpack inline:
let () =
    let module S = (val int_show : SHOW with type t = int) in
    print_endline (S.show 42)

-- Heterogeneous list of first-class modules
let printers : (module SHOW with type t = _) list = [
    (module IntShow);
    (module StringShow : SHOW with type t = string);
]
```

**Semantic model**: `(module M : S)` packs module `M` into a first-class
value of type `(module S)`. `(val e : S)` unpacks a first-class module value
back into a module, enabling module-level operations on a runtime value. The
packed module is existential: the concrete type `t` is hidden. To use it, you
unpack with a type annotation that reveals `t`. This is the module-form of
the expression problem and dependency injection.

**Nomi normal-form assessment**:

- **Module**: Nomi modules today are file-level namespaces. First-class
  modules turn modules into values that can be passed as function arguments.
  This is related to Nomi's import/binding form: `import app.users as users`
  binds a module value.
- **Data boundary**: Packing a module is constructing a module-as-value;
  unpacking is structural recognition plus binding. The boundary story is
  the same as "decode this value as conforming to this shape."
- **Function**: Once packed, a module can be passed to functions. This is
  ordinary call semantics -- the callee receives a module value.

Transferability: low for the first everyday layer. Nomi modules are
intentionally simple (import/export, no functors, no module types). First-class
modules in OCaml solve a problem that Nomi doesn't have yet: how to abstract
over whole implementations at runtime. If Nomi later grows module types and
signatures, first-class modules become a way to pass implementations as
arguments. The core enabling concept is not syntax but the idea that a module
can be reified as a value -- this shares DNA with Nomi's ambition to make
everything reducible to value, binding, function, call.

---

### 2.3 PPX Extension Points

**Problem solved**: OCaml syntax is fixed. But sometimes you need syntactic
extensions: deriving JSON serializers, generating lenses, inserting logging,
adding pre/post conditions, or building EDSLs. PPX (Pre-Processor eXtensions)
are a metaprogramming system that transforms the OCaml AST before compilation.
Extension points are location markers in source code where PPX rewriters
operate.

**Core syntax**:

```ocaml
-- Extension point syntax: [%extension_name payload]
let%lwt result = Lwt_unix.sleep 1.0 in   -- Lwt monadic syntax
  Lwt.return (result + 1)

-- Deriving-like PPX
type person = {
    name  : string;
    age   : int;
    email : string option;
} [@@deriving yojson, show, eq]
-- generates: person_of_yojson, person_to_yojson, show_person, equal_person

-- Inline expression extension
let config = [%yaml_file "./config.yaml"]
-- Reads a YAML file at compile time and inlines the parsed value

-- Attribute-style extension (decorator-like)
let[@trace "user_lookup"] find_user id =
    ...

-- Pattern extension
match value with
| [%re "([a-z]+)@([a-z]+)"] realm -> ...
```

**Semantic model**: Extension points are AST nodes with a payload string or
AST payload. PPX rewriters are functions `Parsetree -> Parsetree` that
register for specific extension point names. The compiler runs all matching
rewriters in order. The extension point syntax uses `%` for expressions,
`%%` for structure items, `@@` for attributes on declarations.

This is the OCaml answer to macros, decorators, code generation, and embedded
DSLs. Unlike Lisp macros, PPX rewriters operate on a fixed AST and are not
part of the core language semantics.

**Nomi normal-form assessment**:

- **Pattern, flow, block**: PPX extensions can generate any of these. The
  extension point is a hook, not a normal form itself.
- **Explanation**: The critical need is desugaring visibility: "this
  `[@@deriving show]` expanded to functions `show, show_list` at lines
  X-Y." Nomi's L11 (quote/rewrite/notation) is the right home.
- **Data boundary**: `[%yaml_file "..."]` is a compile-time data boundary,
  pulling external structure in before the program runs.

Transferability: explicitly future-layer per Nomi's design. Nomi postpones
global macro systems until source spans, desugaring explanations, and normal
forms are mature. PPX is reference pressure for what a macro system should
feel like: named extensions with clear points of invocation and inspectable
expansion. Nomi's planned `use` scopes and `quote:` boundaries are the
corresponding future features.

---

### 2.4 Labeled and Optional Arguments

**Problem solved**: OCaml (unlike most ML-family languages) supports named
arguments with labels. This improves readability at the call site and makes
argument order optional for labeled parameters. Optional arguments provide
defaulted parameters where the caller can omit them.

**Core syntax**:

```ocaml
-- Labeled argument with ~
let send_email ~from ~to_ ~subject ~body =
    Printf.sprintf "From: %s\nTo: %s\nSubject: %s\n\n%s"
      from to_ subject body

-- Call site: labels are mandatory when defined
let msg = send_email ~from:"a@b.com" ~to_:"c@d.com"
                     ~subject:"Hello" ~body:"..."

-- Labeled arguments can be supplied in any order
let msg = send_email ~to_:"c@d.com" ~subject:"Hi" ~body:"." ~from:"a@b.com"

-- Optional argument with ?
let concat ?(sep = " ") x y = x ^ sep ^ y
-- Usage:
let a = concat "hello" "world"        -- "hello world"
let b = concat ~sep:"," "a" "b"       -- "a,b"

-- Optional argument without default (becomes 'a option in callee)
let wrap ?prefix x =
    match prefix with
    | Some p -> p ^ x ^ p
    | None   -> x
-- Usage: wrap "hello"  or  wrap ~prefix:"**" "hello"
```

**Semantic model**: `~name` marks a labeled parameter. At the call site,
`~name:value` provides the argument, and order is irrelevant among labeled
arguments (but positional arguments must come after optional ones). `~?name`
or `?(name = default)` marks an optional parameter. Inside the function,
un-supplied optional parameters are `None`; supplied ones are `Some value`.

This is not sugar over records. The runtime erases labels; they are a
compile-time argument-mapping mechanism with first-class status in the type
system.

**Nomi normal-form assessment**:

- **Binding**: Named/keyword arguments are already part of Nomi's call
  normal form: `send(email=user.email)`. The OCaml approach adds the
  constraint that labeled arguments must be supplied with labels (no
  positional fallback unless explicitly positional).
- **Function**: Optional arguments with defaults are currently expressed as
  defaulted parameters in Nomi: `func send(from:str, to:str, subject:str="")`.
  OCaml's `?prefix` with automatic `option` wrapping is a different approach
  from explicit `= default` syntax.
- **Data boundary**: Labeled arguments are a call-site readability concern,
  not a data declaration concern.

Transferability: already partially present. Nomi's keyword arguments
(`send(email=user.email)`) are the Python-compatible base. The tension is
whether Nomi should require labels at call sites when parameters are declared
with labels (OCaml style) or allow positional fallback (Python style). Nomi's
current approach (Python-compatible) is reasonable for the first everyday
layer. A later "require labels" annotation on parameters could add the OCaml
style:

```nomi
# Hypothetical: label-required parameters
func send(~from:str, ~to:str, ~subject:str):
    ...
# Call site must use labels
send(from="a@b.com", to="c@d.com", subject="Hi")
```

---

## 3. Agda / Idris (dependent types)

### 3.1 Dependent Pattern Matching

**Problem solved**: Ordinary pattern matching is structural: you match on
constructors. Dependent pattern matching also refines the type indices as you
match, learning facts that eliminate impossible cases and constrain values in
each branch. This replaces runtime "impossible" errors with compile-time
invalidation.

**Core syntax** (Idris):

```idris
-- Vect: a list whose type knows its length
data Vect : Nat -> Type -> Type where
    Nil  : Vect 0 a
    (::) : a -> Vect n a -> Vect (S n) a

-- head: only for non-empty vectors -- the type guarantees safety
head : Vect (S n) a -> a
head (x :: xs) = x
-- No Nil case needed: the type index S n makes Nil impossible

-- Dependent pair (Sigma type)
data IsJust : Maybe a -> Type where
    ItIsJust : (x : a) -> IsJust (Just x)

-- Append: the output length is the sum of input lengths
append : Vect n a -> Vect m a -> Vect (n + m) a
append Nil       ys = ys
append (x :: xs) ys = x :: append xs ys
-- The type checker learns: in Nil branch, n ~ 0, so n + m ~ m
-- In Cons branch, n ~ S k, so n + m ~ S (k + m)
```

Dependent elimination on booleans (Idris):

```idris
-- A type that is parameterized by a boolean
data IsTrue : Bool -> Type where
    Yes : IsTrue True

-- Function that requires a proof the value is > 0
safeDiv : (n : Int) -> (d : Int) -> {auto prf : IsTrue (d > 0)} -> Int
safeDiv n d = n `div` d

-- Call with automatic proof search
result = safeDiv 10 5  -- compiles, d > 0 is true
```

**Semantic model**: Dependent pattern matching is Martin-Lof's elimination
rule for inductive families. When you match a constructor, the type checker
unifies the constructor's index with the scrutinee's index. This unification
substitutes into the context, learning new equalities. If a constructor's
indices can never unify with the scrutinee's indices, that case is omitted
entirely (it's impossible). This is a judgmental equality reasoning step at
each case.

**Nomi normal-form assessment**:

- **Pattern**: This is the pattern normal form extended with type-level
  learning. The runtime behavior (structural matching) is identical. The
  difference is that the type checker eliminates impossible cases statically.
- **Data boundary**: The `data` declaration carries indexed type parameters
  (`Vect n a`). Each variant refines the index. This is the approach sketched
  in Nomi's `docs/drafts/type_theory_design_guide.md` as "indexed types."
- **Explanation**: Diagnostics are richer: "the case `Nil` is impossible
  because the index `n` must be `S _` here" rather than "match error at
  runtime."

Transferability: explicitly research-only for the first Nomi layer per
`language_spec.md` section 21 ("dependent types -- excluded from first core").
The value is in understanding the elimination rule: pattern matching at the
runtime level is structurally identical for ordinary ADTs and GADTs/dependent
types. What changes is what the type checker learns. Nomi's runtime pattern
matching can be designed so that a future static checker can layer type-level
learning on top without changing the elimination semantics.

---

### 3.2 `with` Abstraction (Agda)

**Problem solved**: When you pattern match on an expression that appears
multiple times in the goal type, the connection between occurrences is lost.
The `with` construct lets you abstract over an expression, generalizing all
its occurrences in the context and goal, then pattern match on the abstracted
version.

**Core syntax** (Agda):

```agda
-- Without 'with': pattern match on n directly
filter : {A : Set} -> (A -> Bool) -> List A -> List A
filter p []       = []
filter p (x :: xs) with p x
... | true  = x :: filter p xs
... | false = filter p xs

-- 'with' on an intermediate computation
-- The goal type can depend on the with-expression
merge : List Nat -> List Nat -> List Nat
merge []       ys       = ys
merge xs       []       = xs
merge (x :: xs) (y :: ys) with compare x y
... | less    = x :: merge xs (y :: ys)
... | greater = y :: merge (x :: xs) ys
... | equal   = x :: y :: merge xs ys

-- Complex 'with': abstracting multiple expressions
verify : (n m : Nat) -> n + m == m + n
verify n m with n + m | m + n
... | s | t = {! proof of s == t !}
```

**Semantic model**: `with e` replaces all occurrences of `e` in the goal type
and context with a fresh variable `w`, then pattern matches on `w`. This is
the elimination of the expression into its possible shapes, carrying the
equality `w == e` into each branch. It generalizes the "case on intermediate
result" pattern while keeping the type information precise.

**Nomi normal-form assessment**:

- **Pattern**: This is pattern matching on an intermediate expression, with
  the key insight that the match must "remember" the connection between the
  scrutinee and the original expression. Nomi's `match` already supports
  expressions: `match p(x)`, so the surface is similar.
- **Function**: `with` in Agda is primarily a type-level tool. At runtime, it
  is just pattern matching on a value.
- **Flow**: The "compute then match" shape is a flow-and-pattern combination.

Transferability: low for the first layer. The surface convenience (match on
intermediate value) exists in Nomi via `match expression:`. The semantic heavy
lifting in Agda (rewriting the goal type) is dependent-types-specific. The
design lesson for Nomi is: when a pattern match needs to "remember" the
relationship between the original expression and the matched value, the match
system should carry that link. This is future diagnostic and trace work.

---

### 3.3 Views and Covering (Agda)

**Problem solved**: Data types have a canonical representation (their
constructors), but sometimes the natural patterns for a problem don't match
the representation. The view idiom defines an alternative set of "constructors"
for pattern matching. Covering ensures that the view is bijective (every value
maps to exactly one view constructor).

**Core syntax** (Idris/Agda):

```idris
-- Natural numbers viewed as either zero or one more than some n
data Parity : Nat -> Type where
    Even : Parity (n + n)
    Odd  : Parity (S (n + n))

-- View function: classify any Nat into Parity
parity : (n : Nat) -> Parity n
parity Z         = Even {n = Z}
parity (S Z)     = Odd  {n = Z}
parity (S (S k)) with parity k
    | Even {n} = Even {n = S n}
    | Odd  {n} = Odd  {n = S n}

-- Use the view to write a function by natural patterns
half : Nat -> Nat
half n with parity n
    | Even {n = m} = m
    | Odd  {n = m} = m
```

**Semantic model**: A view is a dependent type family `View : T -> Type` plus
a covering function `view : (x : T) -> View x`. When you match `x` against
the view constructors, the type checker learns that `view x` has a particular
shape, which constrains `x` itself. Covering means every `x : T` can be
expressed by exactly one view constructor -- the view is a re-presentation of
the data.

**Nomi normal-form assessment**:

- **Pattern**: Views are a superset of Haskell's view patterns but tied into
  the dependent pattern matching system. They provide alternate pattern
  surfaces for data.
- **Data boundary**: A view is a semantic interface over a concrete
  representation -- a data access pattern that does not expose internals.
  This shares spirit with Nomi's explicit decode/structural pattern boundary.
- **Explanation**: View diagnostics trace from the concrete constructor to the
  view constructor, showing both levels.

Transferability: medium as a concept. The view/covering pattern is a
disciplined form of "match on the abstract shape, not the implementation."
Nomi can achieve this through pattern synonyms (section 1.2), which are the
surface-level version of views. Dependent views require a type-level function
from values to view types, which is beyond Nomi's first layer.

---

### 3.4 What is Transferable to Non-Dependent Languages

The transferable insights from dependent pattern matching for Nomi:

1. **Elimination rule discipline**: Pattern matching is not syntax sugar -- it
   is the elimination rule for sum types. Nomi should treat pattern matching
   as a semantic primitive, not just convenient branching.

2. **Impossible case detection**: Even without a dependent type checker, Nomi
   can detect impossible cases at runtime and report them differently from
   ordinary non-matches. "This `Nil` case can never be reached when matching
   a non-empty list" is a different diagnostic from "no case matched."

3. **Exhaustiveness as a diagnostic, not a type error**: Nomi's first layer
   can run exhaustiveness checks at runtime with helpful messages ("these
   constructors are not handled: Ok, Err") without requiring compile-time
   enforcement. The same analysis can be used for documentation and tooling.

4. **Constructor as witness**: The idea that a constructor carries information
   (not just a tag) maps to Nomi's constrained constructors: `Ok(value:T)`
   carries the type information and the payload. Treat constructors as
   semantic witnesses, not just data wrappers.

5. **Indexed data as a natural extension path**: Nomi's `data` with type
   parameters (`data Result[T, E]: ...`) is already lightly indexed. The path
   to richer indexing (length-indexed vectors, type-state machines) is a
   natural extension of the same `data` form, should Nomi ever grow a static
   type checker.

6. **`with` as "match on abstracted expression"**: The surface idea is useful
   in non-dependent settings: evaluate an expression, then case-split on it
   with the context "remembering" what the expression was.

---

## 4. Swift (deeper features)

### 4.1 Result Builders (formerly Function Builders)

**Problem solved**: SwiftUI and similar DSLs need to build structured values
from imperative-looking sequential code. A result builder transforms a
sequence of statements (with `if`, `for`, etc.) into a single aggregated value
by calling builder methods at each step. This replaces deeply nested
constructor calls with readable linear syntax.

**Core syntax**:

```swift
// Result builder definition
@resultBuilder
struct ViewBuilder {
    // Required: build a single expression into the result type
    static func buildExpression(_ expression: some View) -> some View {
        expression
    }

    // Required: combine children into a block
    static func buildBlock(_ components: (some View)...) -> some View {
        // return a tuple or composite view
    }

    // Optional: handle if/else
    static func buildEither(first: some View) -> some View { ... }
    static func buildEither(second: some View) -> some View { ... }

    // Optional: handle for loops
    static func buildArray(_ components: [some View]) -> some View { ... }

    // Optional: handle availability checks
    static func buildLimitedAvailability(_ component: some View) -> some View { ... }

    // Optional: handle optional binding (if let)
    static func buildOptional(_ component: (some View)?) -> some View? { ... }
}

// Usage: the @ViewBuilder attribute enables builder syntax
@ViewBuilder func greeting(user: User?) -> some View {
    Text("Hello")
    if let user = user {
        Text(user.name)
    } else {
        Text("Guest")
    }
    // This body becomes calls to buildExpression, buildBlock, buildOptional, etc.
}
```

**Semantic model**: The Swift compiler transforms the function body into a
series of builder-method calls. Each statement becomes `buildExpression(...)`.
`if`/`else` becomes `buildEither(first:)` / `buildEither(second:)`. `for`
becomes `buildArray(...)`. The entire block is wrapped in `buildBlock(...)`.
The builder struct is a normal Swift type with static methods; the special
sauce is the compiler's transformation of control flow into builder calls.

This is a domain-specific metaprogramming feature: declarative UI,
attributed strings, regex builders, and HTML builders all use this mechanism.

**Nomi normal-form assessment**:

- **Block**: This is a block-policy pattern. A result builder is a callee that
  transforms a block (with control flow) into a structured value. The
  transformation is compile-time but the shape is identical to Nomi's block
  calls: attach caller-side code, let the callee build a result from it.
- **Function**: The builder methods (`buildBlock`, `buildEither`) are ordinary
  functions. The compiler generates calls to them.
- **Explanation**: The key diagnostic is showing the desugared form: "your
  `@ViewBuilder` body expanded to: `buildBlock(Text("Hello"), buildOptional(...))`".

Transferability: high as a concept, but as a compile-time metaprogramming
feature it's future-layer. Nomi's block calls are the runtime analogue:

```nomi
# Hypothetical: Nomi builder pattern using block calls
html_page = div(class="container"):
    h1:
        "Welcome"
    if user:
        p:
            "Hello, " + user.name

# Where `div`, `h1`, `p` are block-call functions that build HTML nodes,
# and `if` inside the block is ordinary control flow executed at call time.
```

The difference: Swift's result builders transform control flow at compile time
into a single structured value. Nomi's block calls could achieve similar
ergonomics at runtime if the callee's `yield` policy invokes the block in a
builder context. This is a natural extension of the block normal form.

---

### 4.2 Property Wrappers

**Problem solved**: Repeated property patterns (lazy initialization, UserDefaults
storage, thread-safe access, value clamping, logging) involve boilerplate
getter/setter logic. Property wrappers extract the access pattern into a
reusable type that can be attached to any property.

**Core syntax**:

```swift
// Define a property wrapper
@propertyWrapper
struct Clamped<Value: Comparable> {
    private var value: Value
    let range: ClosedRange<Value>

    var wrappedValue: Value {
        get { value }
        set { value = min(max(newValue, range.lowerBound), range.upperBound) }
    }

    init(wrappedValue: Value, _ range: ClosedRange<Value>) {
        self.range = range
        self.value = min(max(wrappedValue, range.lowerBound), range.upperBound)
    }
}

// Usage: apply the wrapper to properties
struct Player {
    @Clamped(wrappedValue: 100, 0...100) var health: Int
    @Clamped(wrappedValue: 0, 0...100)   var mana: Int
}

var p = Player()
p.health = 150  // stored as 100
p.mana   = -10  // stored as 0

// Built-in wrappers
@State var count = 0           // SwiftUI reactive state
@Binding var isPresented: Bool // two-way binding to parent
@Published var name = ""       // Combine publisher
@Environment(\.colorScheme) var colorScheme  // dependency injection
@UserDefault("username") var username = ""
```

**Semantic model**: `@Wrapper(args) var name: Type = initial` desugars to a
private stored property `_name: Wrapper` plus a computed property `name` that
routes through `_name.wrappedValue`. The compiler injects `_name` at
initialization and translates property accesses. Additional projected values
(`$name`) expose the wrapper itself for binding or observation.

This is the metaprogramming answer to Python's `@property` descriptor pattern
and Kotlin's delegated properties, unified into a single type-level concept.

**Nomi normal-form assessment**:

- **Binding**: The core operation is: "bind `name`, but route reads and writes
  through a wrapper that checks/transforms values." This is structurally
  identical to Nomi's constrained binding (`age:int, age >= 0 = value`), where
  the constraint runs at each rebinding. A property wrapper is a reusable
  constraint bundle with both read and write paths.
- **Data boundary**: Wrappers create a boundary between the stored
  representation and the access surface. This is the data-boundary normal
  form applied to individual fields.
- **Explanation**: The diagnostic story is: "property `health` rejected value
  150 because wrapper `Clamped(0...100)` clamped it to 100." This is the same
  shape as a constraint diagnostic.

Transferability: medium-high as a concept. Nomi's constraint system is
write-time only (checked at binding). Property wrappers add read-time
transformation (wrap the value before returning). Nomi could express this as
a field-level policy:

```nomi
# Hypothetical: Nomi field wrapper
data Player:
    health: int, clamp(0, 100) = 100
    mana: int, clamp(0, 100) = 0

# Where `clamp(min, max)` is a reusable constraint-plus-postprocessing policy
```

The binding normal form already covers the write-time check. The concept of
"each field access goes through a wrapper" is a data-level policy that Nomi
could add as a field annotation without introducing a parallel metaprogramming
layer.

---

### 4.3 Macros (Swift 5.9+)

**Problem solved**: Boilerplate generation in Swift (Codable conformance,
equatable conformance, case detection on enums) previously required manual
implementation or Sourcery (a third-party code generator). Swift Macros are
compiler-integrated code generation that runs at compile time, with full
access to the AST, producing validated source code.

**Core syntax**:

```swift
-- Freestanding macro (expression or declaration)
let url = #URL("https://example.com")  // validates URL at compile time
#warning("This code needs review")      // compile-time diagnostic

// Attached macro (on a declaration)
@AddAsync
func fetchUser(id: String) -> User {
    // macro generates: func fetchUserAsync(id: String) async -> User
    return database.lookup(id)
}

// Case detection macro
@CaseDetection
enum Path {
    case home
    case profile(User)
    case settings(Settings)
}
// generates: var isHome: Bool, var isProfile: Bool, etc.

// Observable macro (SwiftUI)
@Observable
class ViewModel {
    var count = 0
    var name = ""
}
// generates: observation tracking infrastructure

// Macro definition (uses SwiftSyntax for AST manipulation)
public struct URLMacro: ExpressionMacro {
    public static func expansion(
        of node: some FreestandingMacroExpansionSyntax,
        in context: some MacroExpansionContext
    ) throws -> ExprSyntax {
        // Extract the URL string from the macro argument
        // Validate it at compile time
        // Produce the URL initializer expression
    }
}
```

**Semantic model**: A macro is a Swift function that takes AST nodes and
returns AST nodes. It runs in a sandboxed process during compilation. The
compiler validates that the output is syntactically correct and does not
capture arbitrary information. Macros are explicitly opted in (no ambient
rewriting) and the expansion can be inspected by the developer.

The key design constraints:
- Macros only see the AST they're attached to (no global namespace access)
- Expansion is deterministic and inspectable
- Errors from macros are compiler diagnostics with source locations
- Macros are distributed as Swift packages

**Nomi normal-form assessment**:

- **Explanation**: The desugaring-inspection requirement aligns with Nomi's
  principle that every surface form must be expandable to a normal form.
- **Block**: A macro is a compile-time block policy that transforms code.
  Nomi's L11 (quote/rewrite/notation) is the corresponding layer.

Transferability: future-layer per Nomi's design. The Swift macro design is
exemplary reference for how to add metaprogramming without destroying local
reasoning: sandboxed, inspectable, explicit opt-in, deterministic. Nomi's
future `quote:` and `use` scopes should learn from this. The `#macro(args)`
syntax is a good convention for making macro invocation visibly distinct from
ordinary function calls.

---

### 4.4 `some` and `any` Keyword Distinction

**Problem solved**: Swift protocols can be used as existential types
(`any View`) or as opaque result types (`some View`). Confusing them leads to
boxing overhead, loss of type identity, and confusing compiler errors.
Explicit `some` and `any` disambiguate.

**Core syntax**:

```swift
// `some`: opaque type -- the concrete type is known but hidden
func makeView() -> some View {
    return Text("Hello")  // compiler knows it's Text, but hides it
}
// The caller knows only: "this returns a View"
// but the compiler knows the concrete type for optimization and identity checks

// `any`: existential -- a box holding any type conforming to View
func makeAnyView(condition: Bool) -> any View {
    if condition {
        return Text("Hello")  // boxed
    } else {
        return Image("icon")  // boxed
    }
}
// The caller gets a box; operations on it go through the protocol witness table

var items: [any View] = [Text("A"), Image("B")]
var specific: some View = Text("C")  // some View is concrete, known at compile time

// `some` in parameter position (Swift 6+)
func render(_ view: some View) { ... }
// Compiler knows the concrete type, can optimize/inline
// Different from `any View` which erases type information
```

**Semantic model**:

| | `some P` | `any P` |
| --- | --- | --- |
| Concrete type | Known at compile time (opaque) | Erased (existential) |
| Storage | Inline, stack-allocated | Boxed, heap-allocated |
| Identity | Preserved | Lost (two `any P` with same type are different boxes) |
| Heterogeneous | No (all returns same concrete type) | Yes (different types in one variable) |
| Protocol witness | Static dispatch possible | Dynamic dispatch via witness table |
| Same-type constraint | `x: some P == y: some P` means `x` and `y` have the same type | Not expressible |

**Nomi normal-form assessment**:

- **Data boundary**: The `some`/`any` distinction is about type erasure: when
  does crossing a boundary erase or preserve concrete type information?
  Nomi's explicit decode boundary (`DataName.decode(raw)`) asks a similar
  question: does the decoded value retain its source identity?
- **Binding**: `some P` vs `any P` are different binding strategies for
  constrained values. Nomi's current constraint system binds concrete values
  and checks type constraints; there is no "erase type behind a protocol"
  concept because there are no protocols/type classes.
- **Explanation**: Diagnostics distinguish "you can't return two different
  concrete types behind `some P`" from "you can return any type behind `any P`
  but lose type identity."

Transferability: low for the first everyday layer. This is a static-type-level
feature. Nomi does not have protocols or type erasure semantics. The design
lesson is the clarity of the keyword choice: using distinct words for distinct
semantics (opaque vs. existential). If Nomi later grows a protocol/trait
layer, the `some`/`any` distinction should be adopted.

---

## 5. Kotlin (deeper features)

### 5.1 Context Receivers

**Problem solved**: Extension functions let you add methods to a single
receiver type. Context receivers let you add methods that have access to
multiple implicit receivers (dependency contexts) without passing them
explicitly. This solves the "many dependencies, but I don't want to thread
them through every function" problem with lexical discipline.

**Core syntax**:

```kotlin
// Define a context (can be any type)
interface LoggerContext {
    fun log(msg: String)
}

interface DatabaseContext {
    fun query(sql: String): List<Map<String, Any>>
}

// Context receiver: the function requires both contexts to be in scope
context(LoggerContext, DatabaseContext)
fun createUser(name: String, email: String) {
    log("Creating user $name")
    query("INSERT INTO users VALUES ('$name', '$email')")
    log("User created")
}

// Usage: providing the contexts
class App : LoggerContext by ConsoleLogger, DatabaseContext by PostgresDB {
    fun run() {
        // Both contexts are in scope, so createUser is callable
        createUser("Ada", "ada@example.com")
    }
}

// Alternative: explicit scope
with(ConsoleLogger) {
    with(PostgresDB) {
        createUser("Ada", "ada@example.com")
    }
}
```

**Semantic model**: `context(A, B) fun f()` means: to call `f`, the caller
must be inside a lexical scope where `A` and `B` are available as implicit
receivers. Inside `f`, members of `A` and `B` are accessible without
qualification (as if `A.this` and `B.this` were in scope). This is lexical
multi-receiver dispatch: the receivers are determined at the call site by the
current scope, not by the function definition.

Unlike Scala's `given`/`using` (which resolves instances globally), context
receivers are lexically scoped. They must be in scope at the call site via
extension receiver, dispatch receiver, or explicit `with`.

**Nomi normal-form assessment**:

- **Block**: Context receivers are a block-policy pattern: "inside this scope,
  these capabilities/contexts are available, and any function that needs them
  can use them." The `with` block is the explicit surface for this.
- **Module**: The idea of "this function needs access to Logger and Database"
  is dependency declaration. Nomi imports are module-level; context receivers
  are finer-grained (expression/block level).
- **Explanation**: Diagnostics should show: "`createUser` requires `LoggerContext`
  and `DatabaseContext`. Currently in scope: `LoggerContext` only. Missing:
  `DatabaseContext`."

Transferability: medium as a design concept. Nomi's block normal form and
future capability layer (L9) are the natural home. The core idea is
"declared dependencies satisfied by the lexical scope" rather than passed
as explicit arguments. This could be prototyped in Nomi as:

```nomi
# Hypothetical: capability-scoped block
with(logger, database):
    create_user(name, email)

# Where `create_user` declares it needs those contexts
func create_user(name:str, email:str) requires (logger:Logger, db:Database):
    logger.log("Creating user " + name)
    db.query("INSERT ...")
```

The explicit `requires` declaration and the lexical `with` block are
consistent with Nomi's principle of visible boundaries for implicit magic.

---

### 5.2 Inline Functions with `reified`

**Problem solved**: Kotlin generics are erased at runtime (JVM compatibility).
Usually you cannot access type parameters at runtime: `if (value is T)` does
not compile. `reified` type parameters, available only in `inline` functions,
are not erased -- the compiler inserts the actual type at each call site,
enabling type checks and reflection on generic parameters.

**Core syntax**:

```kotlin
// Without reified: cannot check T at runtime
fun <T> filterByType(items: List<Any>): List<T> {
    return items.filter { it is T }  // ERROR: Cannot check for instance of erased type T
}

// With reified: T is available at runtime
inline fun <reified T> filterByType(items: List<Any>): List<T> {
    return items.filterIsInstance<T>()  // Works: T is known at call site
}

// Usage: the compiler inlines the call and substitutes the actual type
val numbers = filterByType<Int>(listOf(1, "two", 3, "four"))
// Becomes (inlined): listOf(1, "two", 3, "four").filterIsInstance<Int>()

// Practical use: type-safe deserialization
inline fun <reified T : Any> String.fromJson(): T =
    jacksonObjectMapper().readValue(this, T::class.java)

val user = """{"name":"Ada"}""".fromJson<User>()

// Another use: enum value iteration
inline fun <reified T : Enum<T>> enumValues(): Array<T> =
    enumValues<T>()
```

**Semantic model**: `inline` copies the function body to the call site.
`reified` makes the type parameter available as a runtime value (`T::class`).
The combination means: the function body, with the concrete type substituted,
is inserted at the call site. No boxing, no type erasure. The cost is binary
size (code duplication) and the restriction that `reified` can only be used
on `inline` functions.

**Nomi normal-form assessment**:

- **Function**: The core is "this function's behavior depends on a type, but
  I want the type to be a runtime value." This is a compile-time
  specialization concept. Nomi does not have generic type erasure (it runs
  on Python), so the need is different.
- **Explanation**: The diagnostic for misuse is: "`reified` type parameter
  `T` used in a non-inline context -- add `inline` or remove `reified`."

Transferability: low. This solves a JVM-specific problem (type erasure). In
Python-hosted Nomi, type information is available at runtime naturally. If
Nomi is ever compiled to a target with erased generics, `reified`-style
specialization becomes relevant. The design lesson is the explicit marker:
using `reified` signals "this type parameter will survive to runtime and costs
inline expansion."

---

### 5.3 Contracts / `callsInPlace`

**Problem solved**: The Kotlin compiler performs smart casts (automatic type
narrowing after a null/type check) and definite-initialization analysis. But
these analyses don't cross function boundaries. Contracts let library authors
tell the compiler what effect a function has on its arguments or control flow,
enabling smart casts and initialization analysis to work through calls.

**Core syntax**:

```kotlin
// Without contract: the compiler doesn't know check() ensures non-null
fun check(condition: Boolean) {
    if (!condition) throw IllegalStateException()
}

val name: String? = "Ada"
check(name != null)
println(name.length)  // ERROR: name might be null (compiler doesn't know check() semantics)

// With contract: tell the compiler what check() implies
@OptIn(ExperimentalContracts::class)
fun check(condition: Boolean) {
    contract {
        returns() implies (condition)
    }
    if (!condition) throw IllegalStateException()
}

val name: String? = "Ada"
check(name != null)
println(name.length)  // OK: compiler now knows name != null

// callsInPlace: tell the compiler that a lambda is invoked exactly once
inline fun <T> runOnce(block: () -> T): T {
    contract {
        callsInPlace(block, InvocationKind.EXACTLY_ONCE)
    }
    return block()
}

fun example() {
    val x: Int
    runOnce {
        x = 42  // OK: compiler knows block runs exactly once, so x is initialized
    }
    println(x)  // OK
}

// Multiple effects
inline fun <R> myRun(block: () -> R): R {
    contract {
        callsInPlace(block, InvocationKind.EXACTLY_ONCE)
    }
    return block()
}
```

**Semantic model**: A contract is a logical assertion about the function's
effect on the program state. `returns() implies (condition)` means "if this
function returns normally, the condition is true." `callsInPlace(block,
EXACTLY_ONCE)` means "the block parameter is invoked exactly once during this
call." The compiler uses these facts in its flow analysis.

This is not runtime behavior; it's a compile-time proof system embedded in the
type checker. The contracts are trusted (the compiler does not verify them;
the author asserts them).

**Nomi normal-form assessment**:

- **Explanation**: Contracts are explanation mechanisms: "this function
  guarantees X when it returns." Nomi's constraint and diagnostic normal forms
  are the runtime analogue: `BindingError` explains why a value wasn't
  accepted. Contracts extend this to compile-time.
- **Function**: The contract is attached to a function declaration as
  additional semantic information. This is similar to Nomi's `examples:`
  blocks that attach behavior to declarations.
- **Block**: `callsInPlace` is a promise about how a block parameter is used.
  Nomi's block call semantics could include explicit invocation-mode metadata.

Transferability: low for the first layer but relevant for diagnostics.
Nomi's constraint and example systems are runtime-first. Contracts represent
the compile-time version. If Nomi ever adds a static checker, the contract
concept (declaring effects on analysis state) is exactly what would connect
library code to type-checker reasoning. The Nomi spin: contracts should be
expressed in Nomi's own constraint language, not a separate mini-logic.

---

### 5.4 Type-Safe Builders (deep dive)

**Problem solved**: Building deeply nested structures (HTML, UI layouts, SQL,
configuration) with ordinary constructor calls leads to parenthesized,
hard-to-read code. Kotlin's type-safe builders combine extension functions,
lambdas with receivers, and `@DslMarker` to create readable, type-checked
hierarchical construction with scope control.

**Core syntax**:

```kotlin
// HTML DSL via type-safe builders
html {
    head {
        title("Kotlin HTML DSL")
    }
    body {
        h1("Welcome")
        p {
            +"This is a "
            a(href = "https://kotlinlang.org") { +"link" }
            +"."
        }
        // Implicit receiver prevents accessing outer scope elements
        // html {  // Would be a compile error with @DslMarker
        //     ...
        // }
    }
}

// The enabling features:
@DslMarker
annotation class HtmlTagMarker

@HtmlTagMarker
abstract class Tag(val name: String) {
    val children = mutableListOf<Tag>()

    operator fun String.unaryPlus() {
        children.add(TextElement(this))
    }
}

class HTML : Tag("html") {
    fun head(init: Head.() -> Unit): Head {
        val head = Head()
        head.init()         // lambda with Head as receiver
        children.add(head)
        return head
    }
    fun body(init: Body.() -> Unit): Body { ... }
}

// @DslMarker: prevents accessing implicit receivers from outer builder scopes
// Without it, you could accidentally call body() inside head()
```

**Semantic model**: The builder pattern rests on three Kotlin features working
together:

1. **Lambda with receiver**: `init: Head.() -> Unit` means `init` is a
   lambda where `this` is implicitly a `Head`. Inside the lambda, `title()`
   resolves on `Head`.

2. **Extension functions**: The builder methods (`head`, `body`, `title`) are
   extension functions on their parent type, so they're only available in the
   right scope. You can't call `h1()` outside a `body` block.

3. **`@DslMarker`**: An annotation that prevents implicit receiver
   resolution from crossing nested builder scopes. Without it, `h1()` in a
   nested `div { }` inside `body { }` could accidentally be called on the
   enclosing `body`. `@DslMarker` enforces "only the innermost receiver."

**Nomi normal-form assessment**:

- **Block**: This is a block-call pattern par excellence. Each builder method
  (`head { ... }`, `body { ... }`) is a function that receives a block. The
  nesting is natural block nesting. Nomi's block calls (`using(...):`,
  `retry(...):`) are the same shape.
- **Function**: Lambda-with-receiver is a special form of function call where
  the receiver is implicit. Nomi does not have implicit receivers per its
  design rule against hidden `this`.
- **Data boundary**: The builder constructs a data value. The nesting
  structure maps directly to a tree of data constructors. Nomi's `data`
  declarations and constructor calls achieve the same end, but without the
  implicit-receiver ergonomics.

Transferability: high as a pattern, medium as syntax. The core insight is that
block call nesting naturally models hierarchical construction. Nomi could
achieve similar readability with explicit parameters instead of implicit
receivers:

```nomi
# Hypothetical: explicit-receiver builder style
html:
    head:
        title("Kotlin HTML DSL")
    body:
        h1("Welcome")
        p:
            text("This is a ")
            a(href="https://kotlinlang.org"):
                text("link")

# Where html, head, body, h1, p, a are functions that take blocks
```

The difference: Kotlin's implicit receiver `this` makes the DSL methods appear
as bare identifiers. Nomi would require explicit reference or named block
parameters. The `@DslMarker` scope-control concept is directly applicable to
Nomi's block scoping: preventing block code from accidentally reaching into an
outer block's context.

---

## 6. Scala 3 (deeper features)

### 6.1 `given`/`using` for Implicit Parameters

**Problem solved**: Scala 2's `implicit` was overloaded (implicit parameters,
implicit conversions, implicit classes, implicit evidence). Scala 3
disambiguates: `given` defines a canonical instance, `using` declares that a
function parameter should be resolved from available givens. This is
type-directed dependency injection at the language level.

**Core syntax**:

```scala
// Define a canonical instance
given IntOrdering: Ordering[Int] with
    def compare(x: Int, y: Int): Int = x - y

// Or with an anonymous given
given Ordering[String] = Ordering.String  // use the existing default

// Declare that a function uses a given
def sort[A](list: List[A])(using ord: Ordering[A]): List[A] = ...

// Call: the `using` parameter is resolved from givens in scope
val sorted = sort(List(3, 1, 2))  // resolves given IntOrdering automatically

// Explicitly passing a using parameter
val custom = sort(List(3, 1, 2))(using myCustomOrdering)

// Given with context bounds (shorthand)
def sort[A: Ordering](list: List[A]): List[A]
// Equivalent to: def sort[A](list: List[A])(using Ordering[A])

// Multiple using parameters
def sendEmail(to: String, subject: String, body: String)(using
    smtp: SmtpConfig,
    logger: Logger
): Unit = ...

// Importing givens
import Config.given SmtpConfig  // import only the given SmtpConfig
```

**Semantic model**: `given` values are resolved by type at the call site.
Resolution searches: current scope, imports, companion objects of the type
and the given's type. Resolution is at compile time and deterministic. A
compile error occurs if no `given` is found or if multiple match (ambiguous).

This separates concerns: `using` declares dependency, `given` provides
fulfillment. The caller doesn't thread dependencies through call chains.

**Nomi normal-form assessment**:

- **Module**: `given`/`using` is a module-level and call-level dependency
  injection mechanism. Nomi's imports are module-level namespace operations.
  Givens are type-directed imports: "import a value by its type, not its
  name."
- **Binding**: `using` parameters are bindings, identical to explicit
  parameters except they're resolved from context. Nomi's binding normal form
  already supports defaulted parameters; `using` is a richer default where
  the default comes from the type's canonical instance.
- **Explanation**: The diagnostic "no given instance of `Ordering[User]` found"
  is a compile-time version of Nomi's `BindingError` -- a constraint
  satisfaction failure.

Transferability: medium as a design concept, low as a direct copy. Nomi's
design rules forbid implicit receivers and hidden conversion. `given`/`using`
is explicit about what is being resolved (the type is visible in the
signature), unlike Scala 2's implicit which could do hidden conversions. The
explicit `using` keyword marks the resolution boundary.

Nomi could use a similar pattern for capability resolution (L9):

```nomi
# Hypothetical: using-like dependency resolution
func send_email(to:str, subject:str, body:str) using (smtp:SmtpConfig, logger:Logger):
    ...

# At the call site, using parameters are resolved from the current scope
with_capability(my_smtp, my_logger):
    send_email(to="a@b.com", subject="Hi", body="...")
```

The `using` keyword serves as a visible marker: "this parameter comes from
context, not from the caller's explicit arguments." This is consistent with
Nomi's principle of visible boundaries.

---

### 6.2 Extension Methods

**Problem solved**: Add methods to existing types without modifying their
source and without wrapper types. Like Kotlin's extension functions and C#'s
extension methods, but integrated with Scala's type-class and given system.

**Core syntax**:

```scala
// Extension method on a closed type
extension (s: String)
    def isPalindrome: Boolean = s == s.reverse
    def countChar(c: Char): Int = s.count(_ == c)

// Usage
"racecar".isPalindrome           // true
"hello".countChar('l')           // 2

// Extension with type parameters
extension [T](list: List[T])
    def second: Option[T] = list match
        case _ :: x :: _ => Some(x)
        case _ => None

// Collective extensions (multiple methods sharing the same receiver)
extension (n: Int)
    def isEven: Boolean = n % 2 == 0
    def isOdd: Boolean  = n % 2 != 0
    def squared: Int    = n * n

// Generic extension with using clause
extension [T](list: List[T])(using ord: Ordering[T])
    def maxOption: Option[T] = list.reduceOption(ord.max)
```

**Semantic model**: `extension (s: String) def foo = ...` desugars to a
regular method with the receiver as the first parameter. At the call site,
`"hello".foo` desugars to `foo("hello")`. The extension is resolved by the
receiver's static type. Extensions are non-virtual (no dynamic dispatch based
on runtime type). They can be imported and scoped.

**Nomi normal-form assessment**:

- **Function**: Extension methods are a call-site sugar for ordinary functions
  where the first argument moves before the dot. Nomi's `func str.is_palindrome()`
  proposal in `others.md` is exactly this.
- **Binding**: The receiver is bound to `this` (or a named receiver) inside
  the extension body. This is a binding normal form.
- **Explanation**: Diagnostics should show: "extension method `isPalindrome`
  defined on `String` at my_utils.nomi:12" -- explicit about where the method
  comes from.

Transferability: already planned in Nomi (`convenience/types.md`). The Scala
3 form with `extension` as a declaration block is cleaner than defining each
method separately. Nomi's proposed surface (`func str.is_palindrome()`) is
essentially the same.

---

### 6.3 `inline` and Macro System

**Problem solved**: Scala 3 macros are safer and simpler than Scala 2 macros.
`inline` specializes code at compile time, eliminating abstraction overhead
for small functions. Macros are `inline def` with quoted expressions (`'{...}`)
that can analyze and synthesize code at compile time.

**Core syntax**:

```scala
// Inline: compile-time specialization (no runtime overhead)
inline def assert(condition: Boolean, message: => String): Unit =
    if !condition then throw AssertionError(message)

// Inline conditional: constant folding at compile time
inline def debugLog(inline msg: String): Unit =
    inline if debugEnabled then println(msg)

// Inline match: exhaustiveness checked at compile time
inline def describe(x: Any): String = inline x match
    case n: Int    => s"Integer: $n"
    case s: String => s"String: $s"
    case _         => "unknown"

// Macro: code generation with Quotes API
import scala.quoted.*

inline def inspect(inline x: Any): String = ${ inspectCode('x) }

def inspectCode(x: Expr[Any])(using Quotes): Expr[String] =
    val source = x.show  // get the source code of the expression
    val value  = x.value.getOrElse("not a compile-time value")
    '{ s"expression `${${Expr(source)}}` evaluates to `${${Expr(value)}}`" }

// Usage
val result = inspect(2 + 3)  // "expression `2 + 3` evaluates to `5`"

// Inline with summoning givens at compile time
inline def summonAll[T <: Tuple]: List[Any] =
    inline erasedValue[T] match
        case _: EmptyTuple => Nil
        case _: (head *: tail) => summonInline[head] :: summonAll[tail]
```

**Semantic model**: `inline` does controlled copy-paste at the call site.
`inline if` eliminates dead branches at compile time based on constant
conditions. `inline match` reduces the match at compile time. Macros use `'{
... }` to quote expressions and `${ ... }` to splice. The macro system runs
in a separate compilation phase with access to the typed AST.

The security model: macros are declared with `inline`, operate on quoted
expressions (not arbitrary strings), and the output is type-checked. There is
no "arbitrary code execution at compile time with full system access" -- the
Quotes API mediates what macros can inspect.

**Nomi normal-form assessment**:

- **Function**: `inline` is compile-time specialization of function calls.
  Nomi's pipeline lowering is a runtime analogue: desugar surface forms to
  call sequences.
- **Explanation**: The desugaring must be visible: "this `inline` call was
  expanded to: ..." This matches Nomi's explanation normal form.
- **Block**: `inline match` is a compile-time version of `match` where cases
  are eliminated based on known types.

Transferability: future-layer per Nomi's design. The Scala 3 macro system is
a good model for a future Nomi macro/rewrite layer: explicit quoting
boundary, type-safe code generation, inspectable expansion. Nomi's planned
`quote:` syntax and explicit `use` scopes align with this approach.

---

### 6.4 Match Types

**Problem solved**: Type-level functions that compute the result type of an
operation based on input types. "If I have an `Either[A, B]`, mapping over
it with `A => C` should give `Either[C, B]`." Match types express this
dependency at the type level with familiar pattern-matching syntax.

**Core syntax**:

```scala
// Match type: a function from types to types using pattern matching
type Elem[X] = X match
    case String      => Char
    case Array[t]    => t
    case Iterable[t] => t

// Usage in type signatures
def first(x: Iterable[t]): Elem[Iterable[t]] = x.head

// Complex example: map over Either
type EitherMap[T] = T match
    case Left[a, b]  => Left[a, b]
    case Right[a, b] => Right[a, b]

// Dependent match type: compute return type from value-level input
type ComputeType(x: Boolean) = x match
    case true  => Int
    case false => String

// Recursive match types (type-level recursion)
type Concat[X <: Tuple, Y <: Tuple] <: Tuple = X match
    case EmptyTuple    => Y
    case head *: tail  => head *: Concat[tail, Y]
```

**Semantic model**: Match types are type-level pattern matching. At type
checking time, the compiler reduces `Elem[String]` by matching `String`
against the cases, finding `case String => Char`, and substituting `Char`.
This is evaluated lazily (only when needed) and must be provably terminating.
The compiler checks exhaustiveness similar to value-level match.

**Nomi normal-form assessment**:

- **Pattern**: Match types use pattern-matching syntax familiar from value
  level. The reduction is the same as value-level match: try cases in order,
  pick the first match, substitute. This is the pattern normal form lifted to
  the type level.
- **Explanation**: Reduction traces show: "`Elem[String]` matched case
  `String => Char`, reduced to `Char`."

Transferability: research-only for Nomi's first layer. Nomi intentionally
postpones type-level computation. The design lesson is the syntactic
consistency: match types use `match`/`case` syntax, creating a visual
parallel with value-level pattern matching. If Nomi ever grows type-level
features, using the same syntax for type-level and value-level matching
reduces the cognitive load.

---

### 6.5 Union and Intersection Types

**Problem solved**: Many APIs need to express "this parameter can be an A or
a B" (union) or "this parameter must be both A and B" (intersection). Without
language support, users create ad hoc sum types or complex trait hierarchies.
Union and intersection types make these constraints first-class.

**Core syntax**:

```scala
// Union type: A or B
type StringOrInt = String | Int

def process(value: String | Int): String = value match
    case s: String => s.toUpperCase
    case n: Int    => n.toString

// Variables can hold union types
var x: String | Int = "hello"
x = 42  // OK
x = true  // Compile error: Boolean is not String | Int

// Intersection type: A and B
trait Resettable:
    def reset(): Unit

trait Loggable:
    def log(msg: String): Unit

def useComplex(obj: Resettable & Loggable): Unit =
    obj.log("starting")
    obj.reset()
    obj.log("done")

// Usage: type must satisfy both traits
class MyService extends Resettable, Loggable:
    def reset() = ...
    def log(msg: String) = ...

useComplex(MyService())  // OK
```

**Semantic model**:
- `A | B`: the value must be of type A or type B. The type checker tracks
  which alternative is possible at each point. Pattern matching narrows the
  type.
- `A & B`: the value must satisfy both A and B. You can call members from
  either. The compiler checks that the concrete type actually implements both.

Union types are the dual of intersection types. They are most useful for:
- Ad hoc result types: `String | Error`
- Nullable types: `String | Null` (used instead of `Option[String]` in some
  patterns)
- Heterogeneous collections: `List[String | Int]`

**Nomi normal-form assessment**:

- **Data boundary**: Union types are a lightweight alternative to nominal sum
  types. Nomi's `data Result[T, E]` with `Ok(value)` and `Err(error)` is the
  nominal approach. Union types are structural: `String | Error` without
  wrapping in constructors. This is related to OCaml's polymorphic variants.
- **Pattern**: Pattern matching on union types uses type-test patterns
  (`case s: String`). This is pattern matching extended with type narrowing.
- **Explanation**: "Expected `Resettable & Loggable`, but `MyService` does
  not implement `Loggable`" -- structured like a constraint diagnostic.

Transferability: low for the first layer. Nomi prefers nominal `data`
declarations over structural unions. The `String | Error` union style loses
the semantic distinction between "the value is a string" and "the value is an
error." Nomi's `Result[T, E]` with explicit `Ok`/`Err` constructors makes the
success/failure distinction visible. However, union types are useful for
expressing simple "one of these" relationships without ceremony. This tension
(structural vs. nominal) is the same as OCaml's polymorphic variants vs.
regular variants.

---

### 6.6 Opaque Type Aliases

**Problem solved**: A type alias (`type UserId = String`) is transparent: the
compiler treats `UserId` and `String` as identical. You lose the semantic
distinction and can accidentally pass a raw string where a `UserId` is
expected. Opaque types create a compile-time abstraction boundary where the
underlying type is known to the defining scope but hidden from consumers.

**Core syntax**:

```scala
// Declare an opaque type in a scope
object User:
    opaque type UserId = String

    // Companion methods: the only place that knows UserId is String
    def parse(s: String): Option[UserId] =
        if s.matches("[a-zA-Z0-9]+") then Some(s) else None

    def value(id: UserId): String = id

// Outside the defining scope, UserId and String are distinct
import User.*

val id: UserId = User.parse("abc123").get
val s: String = User.value(id)  // OK: explicit conversion

// val s: String = id  // Compile error: UserId is not String
// val bad: UserId = "raw-string"  // Compile error: String is not UserId
```

**Semantic model**: An opaque type is like a newtype (Haskell) or a branded
type (TypeScript). Inside the defining scope, `UserId = String`. Outside,
they're unrelated -- you must use the API's constructors and accessors. At
runtime, the representation is identical (no boxing, no wrapper object). At
compile time, the type barrier prevents misuse.

This is a zero-cost abstraction: you pay nothing at runtime for the type
safety.

**Nomi normal-form assessment**:

- **Data boundary**: Opaque types are a data boundary. A value crosses from
  "raw string" to "validated UserId" through an explicit conversion
  (`parse`). This is structurally identical to Nomi's `DataName.decode(raw)`
  boundary.
- **Binding**: The constrained binding `user_id: UserId = parse(raw)` applies
  the boundary check. The opaque type guarantees that `user_id` can't be
  accidentally reused as a plain string.
- **Explanation**: "Expected `UserId`, got `String`. Use `User.parse(s)` to
  convert." The diagnostic mirrors Nomi's decode boundary messages.

Transferability: high as a concept, already partially present. Nomi's `data`
with a single field is the current way to achieve this:

```nomi
data UserId(value: str)  # nominal wrapper, explicit construction
```

The difference: Scala's opaque type has zero runtime overhead (no allocation
for the wrapper). Nomi's Python-hosted `data UserId(value: str)` does create a
wrapper object. If Nomi is ever compiled, opaque/nominal types that erase at
runtime but check at compile time are the optimal path. For the first everyday
layer, the `data` wrapper approach is sufficient and provides better
diagnostics (field access, display, pattern matching).

---

## 7. F# (deeper features)

### 7.1 Computation Expressions

**Problem solved**: Monadic and applicative code (async, optional chaining,
sequence generation, logging) becomes deeply nested without syntactic support.
Computation expressions provide a general syntax for sequencing operations
within a computational context (monad, applicative, or custom builder). They
are F#'s answer to Haskell's `do` notation, generalized.

**Core syntax**:

```fsharp
// Async computation expression
let fetchUserAsync (id: string) = async {
    let! user = db.QueryAsync("SELECT * FROM users WHERE id = @id", id)
    let! orders = db.QueryAsync("SELECT * FROM orders WHERE user_id = @uid", user.Id)
    return (user, orders)
}

// Optional computation expression (maybe monad)
let divideAll (numbers: float list) = maybe {
    let! x = numbers |> List.tryHead
    let! y = numbers |> List.tryItem 1
    let! result = if y = 0.0 then None else Some (x / y)
    return result
}

// Sequence computation expression
let squares = seq {
    for i in 1..10 do
        yield i * i
}

// Query computation expression
let activeUsers = query {
    for user in db.Users do
    where (user.Active)
    select (user.Name, user.Email)
}

// Custom computation expression builder
type LoggingBuilder() =
    member _.Bind(x, f) =
        printfn $"Value: {x}"
        f x
    member _.Return(x) = x

let log = LoggingBuilder()

let result = log {
    let! a = 5
    let! b = 10
    return a + b
}
// Prints: Value: 5
// Prints: Value: 10
// Returns: 15
```

**Semantic model**: `builder { ... }` is syntax that desugars to calls on the
builder object. `let! x = e` becomes `builder.Bind(e, fun x -> ...)`.
`return x` becomes `builder.Return(x)`. `yield x` becomes
`builder.Yield(x)`. The builder is an ordinary F# type with specific method
signatures.

The builder methods and their desugaring:
| CE syntax | Builder method | Meaning |
| --- | --- | --- |
| `let! x = e in body` | `Bind(e, fun x -> body)` | Sequence in monad |
| `let! x = e` (no body) | `BindReturn(e, fun x -> ...)` | Bind + Return combined |
| `return x` | `Return(x)` | Lift value into context |
| `yield x` | `Yield(x)` | Produce element in sequence |
| `return! e` | `ReturnFrom(e)` | Flatten/join |
| `if cond then body` | `Zero()` + `Combine(...)` | Conditional |
| `for x in xs do body` | `For(xs, fun x -> body)` | Iteration |

**Nomi normal-form assessment**:

- **Block**: Computation expressions are a block-policy pattern. The builder
  controls how the block's statements are sequenced. `async { ... }` is
  structurally identical to Nomi's block calls: attach a block to a policy
  function.
- **Flow**: `let!` is a flow operator that sequences operations in a context.
  Nomi's pipeline operator `|>` is flow over values; computation expressions
  are flow over contextual operations.
- **Function**: The builder methods (`Bind`, `Return`, `For`) are ordinary
  functions. The CE syntax is sugar that reduces to call sequences.

Transferability: medium-high as a design pattern. Computation expressions are
a generalization of Nomi's block policy concept. The key insight: the same
block syntax (`{ ... }`) can mean "run sequentially in this context," where
the context is determined by the builder.

Nomi could express this via block calls with different contexts:

```nomi
# Hypothetical: Nomi computation-expression equivalent using block calls
user_data = async:
    user = await db.query("SELECT * FROM users WHERE id = ?", id)
    orders = await db.query("SELECT * FROM orders WHERE user_id = ?", user.id)
    (user, orders)

# Where `async` is a block-policy function that understands `await`
# and the block body is desugared to Bind/Return calls on the async builder
```

The general lesson: instead of adding `async/await` as keywords, make async a
block-policy library that uses the block normal form. The builder protocol
(Bind, Return, etc.) becomes the standard protocol for contextual sequencing.
This is directly aligned with Nomi's "one block story" coherence contract.

---

### 7.2 Active Patterns

**Problem solved**: Ordinary pattern matching tests structure against
constructors. Active patterns let you define custom "virtual constructors"
that can decompose values in domain-specific ways. This is pattern matching
extended with user-defined decomposition.

**Core syntax**:

```fsharp
// Complete active pattern: partitions all values into cases
let (|Positive|Negative|Zero|) (n: int) =
    if n > 0 then Positive
    elif n < 0 then Negative
    else Zero

// Usage: pattern match with active patterns
let describe n =
    match n with
    | Positive -> "positive"
    | Negative -> "negative"
    | Zero     -> "zero"

// Partial active pattern: only matches some values (returns option)
let (|Integer|_|) (s: string) =
    match System.Int32.TryParse(s) with
    | (true, n) -> Some n
    | _ -> None

let parse s =
    match s with
    | Integer n -> $"Got an integer: {n}"
    | _         -> $"Not an integer"

// Parameterized active pattern
let (|DivisibleBy|_|) (divisor: int) (n: int) =
    if n % divisor = 0 then Some DivisibleBy else None

let fizzbuzz n =
    match n with
    | DivisibleBy 3 & DivisibleBy 5 -> "FizzBuzz"
    | DivisibleBy 3 -> "Fizz"
    | DivisibleBy 5 -> "Buzz"
    | _ -> string n

// Active pattern that decomposes into multiple values
let (|RegexMatch|_|) (pattern: string) (input: string) =
    let m = System.Text.RegularExpressions.Regex.Match(input, pattern)
    if m.Success then
        Some (List.tail [ for g in m.Groups -> g.Value ])
    else None

let extractEmail s =
    match s with
    | RegexMatch @"([^@]+)@(.+)" [ name; domain ] ->
        $"Name: {name}, Domain: {domain}"
    | _ -> "No email found"
```

**Semantic model**: Active patterns are functions that participate in pattern
matching. A complete active pattern `(|A|B|C|)` is a function `T -> Choice<A,
B, C>` where each case is a branch. A partial active pattern `(|P|_|)` is a
function `T -> Option<U>`. The compiler converts `match x with | A -> ...`
into `match (|A|B|C|) x with ...`.

Active patterns bridge the gap between abstract data types and pattern
matching: you can pattern-match on the abstract view without exposing the
concrete representation.

**Nomi normal-form assessment**:

- **Pattern**: This is the pattern normal form extended with user-defined
  decomposition. The active pattern is a function from value to "shape
  judgment" that the match system uses. This is the same relationship as
  Scala's `unapply` extractors.
- **Data boundary**: Active patterns are a boundary between concrete
  representation and pattern-visible abstraction. This is the pattern-side
  counterpart of Nomi's `Data.decode(raw)` (which is the construction-side
  boundary).
- **Explanation**: When an active pattern fails, the diagnostic should show
  the active pattern name and optionally why it failed. "Pattern `Integer` did
  not match `\"hello\"` because `Int32.TryParse` returned `false`."

Transferability: high. Active patterns are a direct extension of Nomi's
pattern normal form. They complement pattern synonyms (Haskell section 1.2):
- Pattern synonyms: name a concrete pattern shape.
- Active patterns: define a new pattern shape over abstract values.

Nomi could express active patterns as pattern-producing functions:

```nomi
# Hypothetical: active pattern in Nomi
pattern Integer(s:str) -> int?:
    return int.parse(s)  # returns Result or Option

match value:
    case Integer(n):
        "got an integer: " + str(n)
    case _:
        "not an integer"
```

The key design question: should active patterns return `Option`/`Result`
(partial match) or raise on failure? Nomi's pattern normal form has two
failure modes: case-skip (in `match`) and error (in destructuring
assignment). Active patterns should respect this distinction: return `none`
to skip the case, raise an error for unexpected failures.

---

### 7.3 Units of Measure

**Problem solved**: Numeric quantities in scientific and engineering code have
units (meters, seconds, kilograms, etc.). Adding two lengths is fine; adding
a length and a time is a mistake. Units of measure let the type checker
validate dimensional consistency at compile time with zero runtime overhead.

**Core syntax**:

```fsharp
// Define units
[<Measure>] type m       // meters
[<Measure>] type s       // seconds
[<Measure>] type kg      // kilograms

// Annotate numeric values with units
let distance: float<m> = 100.0<m>
let time: float<s> = 9.8<s>
let mass: float<kg> = 70.0<kg>

// Derive compound units
let speed: float<m/s> = distance / time    // 100.0 / 9.8 = 10.2 m/s
let acceleration: float<m/s^2> = speed / time

// Type checker catches unit errors
let wrong = distance + time   // COMPILE ERROR: type mismatch
//            ^^^^^^^^^ m     ^^^^^^^^^ s
// Cannot add meters to seconds

// Unit conversions with functions
let metersPerSecondToMph (v: float<m/s>) =
    v * 2.23694<mph/(m/s)>  // conversion factor has unit
// Result type: float<mph>

// Generic functions over units
let sqr (x: float<'u>) : float<'u^2> = x * x
// Works for any unit

// Dimensionless quantities
let dimensionless: float = 42.0  // no unit annotation
let ratio = distance / (2.0<m>)  // float (m/m cancels out)

// Real-world: physics simulation
[<Measure>] type N = kg m / s^2  // Newton = kg * m / s^2

let force (mass: float<kg>) (accel: float<m/s^2>) : float<N> =
    mass * accel
```

**Semantic model**: Units of measure are a compile-time-only type annotation
on floating-point (and integral) values. The type checker tracks unit
arithmetic: `m / s = m*s^-1`, `m * m = m^2`. Units are erased at runtime; the
runtime representation is identical to a plain float. The type checker
validates dimensional consistency but does not track unit values (i.e., it
can't distinguish Celsius from Fahrenheit -- only compound units).

**Nomi normal-form assessment**:

- **Constraint**: Units are constraints on numeric values. `speed: float<m/s>`
  constrains `speed` to have dimensions of meters per second. This is the
  binding constraint normal form applied to a dimensional annotation.
- **Data boundary**: Unit-annotated values cross a boundary when converting
  between units (e.g., meters to feet). The boundary function carries the
  conversion factor and changes the type-level unit.
- **Explanation**: "Cannot add `float<m>` and `float<s>`: units are
  incompatible." This is a constraint diagnostic, identical in shape to Nomi's
  `BindingError`.

Transferability: medium as a concept, low for implementation without a static
type checker. Nomi's runtime constraint system can check dimensional
consistency at the value level:

```nomi
# Hypothetical: runtime unit constraints using binding
speed: float, unit("m/s") = distance / time
force: float, unit("kg*m/s^2") = mass * acceleration

# Where `unit(...)` is a constraint that records the dimensional annotation
# and checks it against the computed dimensional expression
```

The runtime-only approach can't check unit consistency of expressions without
computing their dimensional formula at runtime. A compile-time approach (like
F#) is zero-cost and catches errors before execution. For Nomi's first
everyday layer, units could be expressed as data that carries metadata:

```nomi
data Quantity(value: float, unit: str)

func add(a: Quantity, b: Quantity) -> Quantity:
    assert a.unit == b.unit else "Cannot add " + a.unit + " to " + b.unit
    return Quantity(a.value + b.value, a.unit)
```

This is library-first: units are data plus constraints, not fundamental
language syntax. The F# model shows the ideal: zero overhead, full dimensional
analysis at compile time. Nomi's runtime model is the practical first step.

---

### 7.4 Type Providers

**Problem solved**: External data sources (databases, CSV files, JSON APIs,
web services) have schemas that the programmer knows but can't express in
static types without manual mapping. Type providers connect to a data source
at compile time, read its schema, and generate types that are available for
IntelliSense, type checking, and completion -- without manual code generation.

**Core syntax**:

```fsharp
// SQL type provider: reads the database schema at compile time
type Db = SqlDataConnection<"Server=.;Database=MyApp;Integrated Security=SSPI">

let users = Db.GetDataContext().Users
// users has type Table<UserRow> where UserRow is generated from the DB schema
// users.Name, users.Email, users.Age are all typed and IntelliSense-complete

let adults = query {
    for user in users do
    where (user.Age >= 18)
    select (user.Name, user.Email)
}
// Compile error if you type user.Agee (misspelled column)

// JSON type provider: reads a sample JSON and infers the schema
type Config = JsonProvider<"""
    { "host": "localhost", "port": 8080, "useSsl": true }
""">

let config = Config.Load("config.json")
let host: string = config.Host   // typed access
let port: int = config.Port

// CSV type provider
type SalesData = CsvProvider<"sales_sample.csv">

let rows = SalesData.Load("sales_2024.csv")
for row in rows do
    printfn $"Product: {row.Product}, Quantity: {row.Quantity}"

// WorldBank type provider (live API)
type WorldBank = WorldBankDataProvider<Asynchronous=true>
let data = WorldBank.GetDataContext()
let uk = data.Countries.``United Kingdom``
let gdp = uk.Indicators.``GDP (current US$)``
```

**Semantic model**: A type provider is a compile-time component that connects
to an external data source, reads its schema, and emits types into the
compilation. The types are erased (or hosted) at runtime -- they're primarily
a development experience and static safety feature. The data source is
accessed only at compile time (for schema) and optionally at runtime (for
data).

Key properties:
- Schema is read at compile time (or design time in IDE)
- Generated types are available for IntelliSense, refactoring, type checking
- The provider can be parameterized (connection string, sample data, file path)
- Types can be erased (no runtime cost) or generative (actual .NET types)
- Errors ("column not found") become compile errors, not runtime exceptions

**Nomi normal-form assessment**:

- **Data boundary**: Type providers are a data boundary taken to the extreme:
  the external schema becomes part of the program's type structure at design
  time. Nomi's `DataName.decode(raw)` is the runtime counterpart: external
  data crosses a boundary and is validated. Type providers move the boundary
  check to compile time.
- **Explanation**: The diagnostic "column `agee` not found in table `Users`.
  Available columns: `Name`, `Email`, `Age`" is identical in shape regardless
  of whether the check happens at compile time or runtime. Nomi's decode
  diagnostics provide the same information.
- **Module**: A type provider generates module-level type declarations. This
  is compile-time code generation tied to external schema.

Transferability: low as a direct feature (requires compile-time schema access
and code generation), but high as a design inspiration. Nomi's approach
achieves similar safety at runtime through explicit decode boundaries:

```nomi
data UserRow(name: str, email: str, age: int)

func load_users(db_path: str) -> list[UserRow]:
    rows = sql_query(db_path, "SELECT name, email, age FROM users")
    return rows |> map(UserRow.decode)
```

The type provider idea could manifest in Nomi as a tooling feature: "load
schema from database at edit time, show available columns, validate column
references before execution." This is tooling (like LSP completions) rather
than language syntax.

---

## Feature-by-Feature Transferability Summary

| Feature | Language | Nomi normal forms involved | First-layer suitability | Recommendation |
| --- | --- | --- | --- | --- |
| GADTs | Haskell | Data, Pattern | No (needs static type checker with equality constraints) | Future layer: index refinement on `data` |
| Pattern synonyms | Haskell | Pattern, Function | Yes | Add as named pattern binding in Tier 1 surface sugar |
| View patterns | Haskell | Pattern, Function | Conditional | Low priority; guards cover the most common use |
| Type families | Haskell | Function (type level) | No | Future static typing layer |
| DerivingVia | Haskell | Function (code gen) | No | Future macro/rewrite layer |
| Polymorphic variants | OCaml | Data, Pattern | No (needs row polymorphism) | Let nominal `data` mature first; revisit as structural variant option |
| First-class modules | OCaml | Module, Function, Data boundary | No | Future module-type layer |
| PPX extensions | OCaml | Pattern, Flow, Block | No | Future `use`/`quote` layer (L11) |
| Labeled arguments | OCaml | Binding, Function | Partially present | Nomi already has keyword args; consider label-required modifier |
| Dependent pattern matching | Agda/Idris | Pattern, Data | No (needs dependent type checker) | Research inspiration for exhaustiveness diagnostics |
| `with` abstraction | Agda | Pattern, Flow | No at type level | Useful surface for "match on intermediate expression" |
| Views and covering | Agda | Pattern, Data boundary | Conceptually | Pattern synonyms + active patterns are the surface version |
| Result builders | Swift | Block, Function | Conceptually | Block call extension: callee transforms control flow into structured value |
| Property wrappers | Swift | Binding, Constraint | Conceptually | Constraint bundles with read/write paths; extension of binding normal form |
| Macros (Swift 5.9+) | Swift | Explanation, Function | No | Future `quote`/`use` layer; exemplary sandboxed design |
| `some`/`any` | Swift | Data boundary (static) | No (needs protocols) | Design lesson: distinct keywords for distinct semantics |
| Context receivers | Kotlin | Block, Module | Conceptually | Future capability layer: `with(capability):` blocks |
| `reified` / inline | Kotlin | Function (compile-time) | No (JVM-specific) | Not applicable to Python-hosted Nomi |
| Contracts / `callsInPlace` | Kotlin | Explanation, Function | No (needs static analyzer) | Design inspiration for attaching logical assertions to functions |
| Type-safe builders | Kotlin | Block, Function, Data boundary | Partially | Block call nesting; avoid implicit receiver |
| `given`/`using` | Scala 3 | Module, Binding | Conceptually | Future capability resolution: type-directed dependency injection |
| Extension methods | Scala 3 | Function | Already planned | `func str.method()` surface already in design |
| `inline` and macros | Scala 3 | Function, Explanation | No | Future `quote`/`use` layer (L11) |
| Match types | Scala 3 | Pattern (type level) | No (research) | Type-level pattern matching; keep as research reference |
| Union/intersection types | Scala 3 | Data boundary | No | Prefer nominal `data`; revisit if structural needs emerge |
| Opaque type aliases | Scala 3 | Data boundary, Binding | Partially | `data` with single field already achieves this at runtime |
| Computation expressions | F# | Block, Flow, Function | Conceptually | Block policy with contextual sequencing protocol |
| Active patterns | F# | Pattern, Function, Data boundary | Yes | Extension of pattern normal form with user-defined decomposition |
| Units of measure | F# | Constraint, Data boundary | Library-first | Runtime unit constraints; compile-time checking is future work |
| Type providers | F# | Data boundary, Module | Tooling-level | Idea for design-time schema integration; not language syntax |

---

## Key Design Insights for Nomi

### 1. Pattern is under-rated as a normal form

Active patterns (F#), pattern synonyms (Haskell), view patterns (Haskell),
and dependent views (Agda) all point to the same need: user-defined pattern
surfaces over abstract data. Nomi's pattern normal form should support naming
patterns (synonyms) and defining decomposition functions (active patterns) as
first-order extensions.

### 2. Block policies absorb many seemingly disparate features

Computation expressions (F#), result builders (Swift), type-safe builders
(Kotlin), context receivers (Kotlin) all reduce to: "a callee controls how
caller-side code is executed, and the block body is in the caller's lexical
scope." Nomi's block normal form is the right foundation for all of these.

### 3. The compile-time vs. runtime boundary is a spectrum

Many features (GADTs, dependent pattern matching, contracts, opaque types,
units of measure) are *more valuable* at compile time (zero overhead, earlier
error detection) but *still useful* at runtime (better diagnostics). Nomi's
runtime-first approach with structured diagnostics is a valid starting point;
each feature can be upgraded to compile-time later without changing its
semantic shape.

### 4. Nominal vs. structural is a recurring tension

Polymorphic variants (OCaml), union types (Scala), and structural patterns
are structural. Nomi's `data` declarations, opaque types, and nominal
constructors are nominal. The right design: nominal for owned data, structural
for pattern recognition over external values. Keep this distinction explicit.

### 5. Visible boundaries are the unifying insight

Every feature surveyed that works well (Swift macros, Kotlin context
receivers, Scala `given`/`using`, F# active patterns) has an explicit boundary
that says "something special happens here." Nomi's design rule ("explicit
boundary words for risky power") is validated across all seven languages.

### 6. The type-theory ladder from the survey

The research validates the progression sketched in `type_theory_design_guide.md`:

```
ordinary ADT patterns
  -> pattern synonyms (name a pattern)
  -> active patterns (compute a pattern from a value)
  -> view patterns (apply function, then pattern-match)
  -> GADTs (type-indexed constructors, learn from matching)
  -> dependent views (covering function + type-level learning)
```

Each step preserves the elimination rule (pattern matching) while adding a new
capability, exactly matching Nomi's principle of "sophistication through
refinement, not replacement."
