# Scientific Language Research: MATLAB, R, Julia

> Status: raw research notes; not an active syntax spec.
>
> Scope: documentation-only. This doc surveys patterns from MATLAB, R, and Julia
> with emphasis on broadcasting, formula interfaces, non-standard evaluation,
> whole-array philosophy, and what transfers to a general-purpose language.

## 1. Julia: Broadcasting With `.`

Julia's dot-broadcasting is the cleanest broadcasting model across
scientific languages. It is opt-in, visually lightweight, and composes.

### The Dot Operator

Any function or operator prefixed/postfixed with `.` broadcasts element-wise:

```julia
# Unary operators and functions
sin.(x)                # sin applied to each element
sqrt.(A)               # sqrt of each element in matrix A
lowercase.(names)      # works on any collection

# Binary operators
a .+ b                 # element-wise addition
A .* B                 # element-wise multiplication (not matrix multiply)
x .^ 2                 # square each element

# Fused: a .+ b .* c is one loop, not two
result = a .+ b .* c  # single allocation, fused broadcast

# In-place (mutates existing array)
x .= y .+ z            # write result into x without allocating
x .+= 1                # increment each element in-place
```

### The `@.` Macro

Broadcast an entire expression:

```julia
@. x = 3 * y + z^2     # everything broadcasts
# equivalent to: x .= 3 .* y .+ z .^ 2
```

This is powerful for mathematical code where every operation in a formula
should be element-wise. The `@.` macro makes the choice of broadcasting
visible without cluttering the expression with dots.

### Broadcasting Non-Scalar Collections

```julia
f.(xs, ys)             # f applied element-wise to each pair
map(f, xs, ys)         # equivalent
f.(xs, ys')            # broadcast with transposed ys → matrix result
```

### Why This Model Excels

1. **Opt-in**: broadcasting is always visible (`.`) or explicitly wrapped (`@.`)
2. **Fused**: `a .+ b .* c` is one fused loop -- no intermediate arrays
3. **In-place**: `.=` avoids allocation for large arrays
4. **Uniform**: works on any function, not just built-in operators
5. **Non-numeric**: `.` works on strings, custom types, any iterable

**Nomi note**: Julia's `.` model is the recommended starting point for Nomi
broadcasting. It is explicit, safe, and handles the 90% use case. APL-style
implicit rank and NumPy-style implicit trailing alignment both trade safety
for brevity in ways that conflict with Nomi's readability-first design.

```nomi
# Proposed Nomi surface:
result = a .+ b          # element-wise addition
sin.(angles)             # broadcast function over collection
names |> map(lowercase)  # pipeline spelling of same
```

---

## 2. R's Formula Interface

R's formula interface is a mini-language for specifying statistical models.
It is one of the most successful examples of a domain-specific notation
embedded in a general-purpose language.

### Basic Formula Syntax

```r
# y ~ x            : y modelled by x
# y ~ x1 + x2      : additive effects of x1 and x2
# y ~ x1 * x2      : main effects + interaction (expands to x1 + x2 + x1:x2)
# y ~ x1:x2        : interaction only
# y ~ x1 - 1       : remove intercept
# y ~ .             : all variables in data except y
# y ~ . - z         : all except y and z
# y ~ poly(x, 3)   : polynomial terms up to degree 3
# y ~ I(x1 + x2)   : escape: compute x1+x2 as a predictor (not "add x2 to model")
# y ~ log(x)        : log transform of x
# y ~ (1 | group)   : random intercept by group (mixed models)
# y ~ (1 + x | g)   : random slope and intercept by g
```

The key is that `+`, `*`, `:`, `|`, `-` have **different meanings inside**
a formula context than in normal R expressions. `+` means "add a predictor,"
not arithmetic addition. `*` means "expand to main effects plus interaction."

### What A Formula Carries

A formula is not just a string. It is a structured object with:

```r
f <- y ~ x1 + x2 * x3

# Components:
terms(f)              # the expanded term structure
attr(terms(f), "factors")   # matrix of term appearances
attr(terms(f), "term.labels") # c("x1", "x2", "x3", "x2:x3")
model.frame(f, data)  # build the actual design matrix from data
model.matrix(f, data) # numeric matrix ready for computation
```

The formula carries:
- The symbolic expression (the formula itself)
- The expanded structure (what each `*` means)
- The environment where variables should be looked up
- The ability to build a model matrix from a data frame

### The `I()` Escape Hatch

`I()` means "interpret as identity" -- it returns to normal R evaluation
within a formula:

```r
y ~ x + I(x^2)        # quadratic: x plus x-squared
y ~ x1 + I(x1 + x2)   # single predictor = sum of x1 and x2
```

This is analogous to unquote in macro systems. It distinguishes "I want a
polynomial term" from "the formula operator `+`."

### Design Insight: The Formula Is A Syntax Value

R formulas are an early example of the pattern Nomi wants for `quote:`: a
program fragment that is captured as data, carries its environment, and can
be inspected, transformed, and evaluated in a controlled context.

The formula `y ~ x1 + x2` is:
1. A quoted expression (the syntax is preserved as data)
2. With a specific interpretation (model specification, not arithmetic)
3. That carries metadata (term structure, environment)
4. That can be programmatically manipulated (`update(f, . ~ . + z)`)
5. And evaluates in a data context (columns resolved in the data frame)

**Nomi note**: this is the core pattern for Nomi's `quote:` boundary. A
quoted expression should be a syntax value that carries its environment
and has a documented interpretation. The formula interface shows that a
small domain-specific notation can be extremely productive when its
boundaries are clear.

---

## 3. R's Tidy Evaluation (Non-Standard Evaluation)

Tidy evaluation (Tidy Eval) is R's systematic approach to non-standard
evaluation -- the ability to refer to data-frame columns as if they were
ordinary variables.

### Data Masking

The core idea: column names in a data frame become accessible as if they
were variables in the current scope:

```r
# "species" and "homeworld" are columns in starwars, not global variables
starwars |>
  filter(species == "Human", homeworld == "Tatooine") |>
  select(name, height, mass)
```

This works because `filter()` and `select()` create a **data mask**: column
names are resolved before environment variables. The programmer writes
column names directly, not `df$species`.

### The Two Kinds of Variables

Tidy eval distinguishes:

| Kind | Example | Resolved in |
| --- | --- | --- |
| Data variables | `species`, `height` in `filter(species == "Human")` | Data mask (the data frame) |
| Env variables | `threshold <- 100; filter(x > threshold)` | User environment |

The ambiguity is both the power and the cost. In interactive use, data
variables "just work." In function writing, you must learn the difference.

### Embracing `{{ }}` For Programming

When writing functions that use tidy eval, `{{ }}` passes a column name
through:

```r
# Function that lets caller name columns naturally
summarize_by <- function(df, group_col, value_col) {
  df |>
    group_by({{ group_col }}) |>
    summarize(mean = mean({{ value_col }}, na.rm = TRUE))
}

# Caller writes column names, not strings:
summarize_by(starwars, species, height)
```

`{{ }}` captures both the expression *and* its environment, then passes
it into the data mask context.

### Quosures: Quoted Expressions With Environments

A **quosure** is a quoted expression that carries its evaluation environment.
This is the primitive that `{{ }}` builds on:

```r
library(rlang)

quo <- enquo(species)     # capture species + its environment
quo                       # <quosure> expr: ^species, env: 0x7f...

eval_tidy(quo, data = starwars)  # evaluate quo in data context
```

### The `:=` Walrus For Dynamic Names

`=` is for literal names; `:=` is for names stored in variables:

```r
col_name <- "height"

# This doesn't work: starwars |> mutate(col_name = height / 100)
# It would create a column literally named "col_name"

# This works:
starwars |> mutate(!!col_name := height / 100)
# or:
starwars |> mutate("{col_name}" := height / 100)
```

### The Tidy Eval Challenge

Tidy evaluation is genuinely powerful but creates a sharp distinction
between interactive use and function writing:

```r
# Interactive: easy
starwars |> filter(height > 200)

# Function writing: must learn new concepts
tall_characters <- function(data, col, threshold) {
  data |> filter({{ col }} > threshold)
}
```

This is a real usability problem: the same syntax means different things
depending on context, and the programmer must understand the implementation
(quosures, data masks, embracing) to write correct functions.

**Nomi note**: the lesson is not "adopt tidy eval as-is." The lesson is:

1. **Subject-oriented name resolution is powerful** -- being able to say
   `where(salary > 100k)` inside a table scope eliminates repetitive
   `table["salary"]` noise.

2. **The boundary must be explicit** -- Nomi should mark when column-name
   scoping is active, so the reader never confuses column variables with
   environment variables.

3. **Quosures are the right primitive** -- a quoted expression plus its
   environment is a clean building block. R's implementation via `enquo()`
   and `eval_tidy()` is messy because it was retrofitted; a language
   designed from scratch can make this clean.

Proposed Nomi design: column scoping is only active within an explicit
table-scope boundary, such as a `select`/`where` block or a `with_table`
form:

```nomi
trades
|> where(salary > threshold)    -- "salary" from table, "threshold" from env
|> select(name, salary)
```

The key rule: within a table-verb argument expression, unqualified names
resolve in table-then-environment order. The scope boundary is the verb
itself (`where`, `select`, `derive`, `group_by`), not a separate syntactic
form.

---

## 4. MATLAB: Everything Is An Array

MATLAB's design center is that every value is an array. There is no scalar
type -- a scalar is a 1x1 array. This uniformity simplifies the type system
at the cost of conflating distinct concepts.

### The Array-First Philosophy

```matlab
x = 42;                % x is a 1x1 array
size(x)                % → [1 1]
x(1)                   % → 42 (valid: index into a scalar)
x(1,1)                 % → 42 (same)

v = [1 2 3];           % row vector: 1x3 array
size(v)                 % → [1 3]
```

Everything is an array, so array operations are the default:

```matlab
A * B                  % matrix multiplication (not element-wise)
A .* B                 % element-wise: explicit dot required
A / B                  % matrix right-division (A * inv(B))
A ./ B                 % element-wise division
A ^ 3                  % matrix power (A * A * A)
A .^ 3                 % element-wise power
```

### The Colon Operator

The colon `:` is deeply integrated and multi-purpose:

```matlab
1:10                   % → [1 2 3 4 5 6 7 8 9 10]
1:2:10                 % → [1 3 5 7 9]  (start:step:end)
A(:, 3)                % → all rows, column 3 (the entire slice)
A(2, :)                % → row 2, all columns
A(:)                   % → all elements as a column vector (linearize)
```

The colon as "all in this dimension" is particularly elegant --
`A(:, j)` is "column j, all rows" and reads naturally.

### Linear Indexing

Any N-dimensional array can be indexed linearly:

```matlab
A = [1 2 3; 4 5 6];   % 2x3 matrix
A(4)                    % → 5 (column-major: goes down first column)
A(:)                    % → [1; 4; 2; 5; 3; 6] (linearized)
```

### Array Expansion (Implicit Broadcasting Since R2016b)

Modern MATLAB has implicit broadcasting for compatible shapes:

```matlab
A = [1 2; 3 4];
B = [10 20];
A + B                  % B expands to [10 20; 10 20], then added
```

This is trailing-dimension broadcasting (NumPy-style).

### What Transfers

| Pattern | Useful? | Notes |
| --- | --- | --- |
| Everything-is-array | No | Conflates scalar and collection; type richness matters for general-purpose code |
| Matrix ops as default | No | Most general-purpose code is element-wise, not linear-algebraic |
| `.` for element-wise | Yes | Useful pattern, but Julia's consistent `.` is better designed |
| Colon `:` for slices | Yes | Universal pattern: `a[1..5]`, `a[:, 2]` |
| Linear indexing | Partial | Convenient but hides shape; explicit reshape is clearer |
| Implicit broadcasting | No | Julia's explicit `.` is safer |
| Semicolon `;` for row separation | Maybe | `[1, 2; 3, 4]` reads better than nested lists for matrix literals |

**Nomi note**: the colon operator for "all in this dimension" is worth
studying. Nomi's slices already handle `a[1:5]` and `a[::2]`. The `:` for
"all" could be `a[:, 2]` (all rows, column 2), which is natural syntax.

---

## 5. MATLAB's Function Handle And Anonymous Functions

```matlab
f = @(x) x.^2 + 1;     % anonymous function (lambda)
f([1 2 3])             % → [2 5 10]

g = @sin;               % function handle to built-in
feval(g, pi/2)          % → 1

% Array of function handles
funcs = {@sin, @cos, @tan};
funcs{1}(0)            % → 0
```

MATLAB's `@` syntax is relevant to Nomi only as a cautionary example:
distinguishing "function handle" from "function call" with a separate
syntax creates mental friction. Nomi's `(x) => expr` for lambdas and
direct name references for function values is cleaner.

---

## 6. Julia: Multiple Dispatch

Multiple dispatch is Julia's core abstraction. Functions are generic;
methods are specialized on argument types. This is not just a feature of
the type system -- it is the central organizing principle of the language.

### Dispatch By Argument Types

```julia
f(x::Int)    = "integer $x"
f(x::Float64) = "float $x"
f(x::String) = "string $x"

f(1)          # → "integer 1"
f(1.0)        # → "float 1.0"
f("hi")       # → "string hi"
```

Multiple dispatch is on *all* arguments, not just the first:

```julia
collide(a::Asteroid, b::Asteroid) = "crater"
collide(a::Spaceship, b::Asteroid) = "destroyed!"
collide(a::Asteroid, b::Spaceship) = "destroyed!"
collide(a::Spaceship, b::Spaceship) = "deflected"
```

### Generic Functions

Every function is generic from birth:

```julia
+(x::MyType, y::MyType) = MyType(x.val + y.val)
```

You can add methods to any function, including built-in operators.
This is how Julia libraries extend `+`, `*`, `show`, `convert`, etc.
for their types.

### Parametric Types

```julia
struct Point{T}
    x::T
    y::T
end

function distance(p::Point{T}) where T <: Number
    sqrt(p.x^2 + p.y^2)
end
```

### Design Pressure

Multiple dispatch is elegant for mathematical code where operations
naturally specialize on combinations of types (number * matrix,
rational * integer, etc.). It is less obviously beneficial for
general business logic where type-based dispatch on multiple arguments
is rare.

**Nomi note**: Nomi's first dispatch model should be single-dispatch
(method calls on a receiver) or explicit pattern matching over arguments.
Multiple dispatch is powerful but adds complexity that most general-purpose
programs do not need. It should remain a future-layer research item, not a
first language feature.

---

## 7. Julia: Macros And Metaprogramming

Julia macros operate on syntax at parse time:

```julia
macro sayhello(name)
    return :( println("Hello, ", $name) )
end

@sayhello "world"    # → prints: Hello, world

@time expensive_fn() # built-in: time the expression
@. x = y + z         # built-in: broadcast everything
```

Key properties:
- Macros receive the expression's AST (type `Expr`)
- `$` splices values into generated expressions
- `@` prefix distinguishes macro calls from function calls
- Macro expansion happens at parse time, before compilation

Julia's macro system is cleaner than Lisp's because `@` marks macro
calls visibly, but it shares the power/risk tradeoff: macros can
rewrite arbitrary code, which can produce incomprehensible errors.

**Nomi note**: Nomi's `quote:` boundary should also enable a future
macro-like expansion layer, but with stricter guardrails:
- Expansion must be inspectable (`expand` shows the result)
- Source spans must be preserved through expansion
- Macros operate on syntax values, not raw ASTs
- The `@` sigil or equivalent makes macro calls visually distinct

---

## 8. R: Conditions, Restarts, And Signal System

R has a condition system that is more flexible than Python's exceptions
and more structured than Lisp's condition system. It separates:

- **Signaling** a condition (something happened)
- **Handling** a condition (what to do about it)
- **Restarting** (how to continue after handling)

### Conditions

```r
# Signal a condition
warn("temperature too high")
stop("cannot divide by zero")
message("computation complete")

# Custom conditions
abort <- function(msg, class = "my_error") {
  cnd <- structure(list(message = msg), class = c(class, "condition"))
  stop(cnd)
}
```

### Handlers

```r
# Handle via tryCatch
tryCatch(
  risky_operation(),
  error = function(e) { message("Caught: ", e$message); NA },
  warning = function(w) { message("Warning: ", w$message) }
)

# Handle via withCallingHandlers (doesn't abort execution)
withCallingHandlers(
  risky_operation(),
  warning = function(w) { message("Noted: ", w$message); invokeRestart("muffleWarning") }
)
```

### Restarts

The key innovation: a handler can invoke a **restart** -- a named recovery
point established by the code that signaled the condition. This allows the
handler to say "retry," "use a default value," or "skip this item" without
unwinding the stack:

```r
# Establish restarts around risky code
withRestarts(
  {
    if (fail) invokeRestart("use_default", 0)
    result
  },
  use_default = function(val) val
)
```

This is more structured than Python's exception model (where the choice is
binary: catch or propagate) and less formal than algebraic effects. It
provides a practical middle ground for recoverable conditions.

### On-Exit

```r
result <- tryCatch({
  file <- open("data.csv")
  on.exit(close(file))
  process(file)
})
# file is closed regardless of success/failure
```

**Nomi note**: R's condition/restart model is a strong candidate for Nomi's
future effects/capabilities layer. The key insight is separating:
1. What went wrong (the condition object)
2. What to do (the handler)
3. How to continue (the restart)

Nomi's block calls and `yield` already provide a substrate for this. A
future `signal`/`handle`/`restart` layer could build on it:

```nomi
with restarts:
    use_default = (val) => val
    retry = () => do_work()
do:
    risky_operation()
handle:
    error(e) if e.recoverable:
        restart(use_default, 0)
```

---

## 9. R: Vector Semantics And Recycling

### Everything Is A Vector

There are no scalars in R. The number `5` is a vector of length 1:

```r
x <- 5
length(x)           # → 1
is.vector(x)        # → TRUE
```

### Recycling Rule

When two vectors of different lengths meet in an operation, the shorter is
recycled (repeated to match the longer):

```r
c(1, 2, 3) + c(10, 20)        # → 11 22 13  (warning if not exact multiple)
c(1, 2, 3) + c(10, 20, 30)    # → 11 22 33  (lengths match)
c(1, 2, 3, 4) + c(10, 20)     # → 11 22 13 24  (exact recycling, no warning)
```

Recycling is convenient for interactive work but a common source of bugs
in production code. Modern R warns when lengths are not multiples.

### Attributes

Every R object can have arbitrary named attributes:

```r
x <- 1:10
attr(x, "units") <- "meters"
names(x) <- letters[1:10]
# x is now a named vector with a unit attribute
```

This flexibility enables the class system (S3 dispatch is based on the
`class` attribute) but also means any code can silently attach metadata
to any value.

**Nomi note**: recycling and implicit vector extension are convenient but
unsafe patterns. Julia's explicit `.` broadcasting is a better model.
Attributes as general metadata are powerful but should be structured
(explicit annotations on values, not arbitrary key-value dicts).

---

## 10. MATLAB/R/Julia: The Notebook Culture

All three languages have a strong notebook culture that directly shapes
how their syntax is used:

### MATLAB Live Editor

MATLAB's live scripts intermix code, output, equations, and narrative.
The tight integration means MATLAB code often uses intermediate variables
that double as documentation in the notebook.

### R Markdown / Quarto

R's notebook culture is built on R Markdown and Quarto. Code chunks
interleave with prose, and the output (tables, plots, models) renders
inline. This encourages a workflow where code is organized for narrative
clarity:

````r
```{r}
#| label: clean-data
#| message: false

data |>
  filter(!is.na(value)) |>
  mutate(date = ymd(date_string))
```
````

### Julia Pluto

Pluto notebooks are reactive: changing a cell recomputes all dependent
cells. This creates a different programming experience where the
notebook becomes a living document with guaranteed consistency.

### Design Pressure

Notebook culture rewards:
- **Pipeline style**: `data |> filter |> mutate |> plot` reads as a narrative
- **Intermediate naming**: `cleaned <- ...` doubles as documentation
- **Visible inspection**: intermediate values are displayed automatically
- **Incremental building**: code grows organically from exploration

**Nomi note**: Nomi's pipeline and binding syntax should be designed with
notebook/REPL workflows in mind. Pipeline breaks (`|>` at line boundaries)
should feel natural. Expression results should be inspectable. Bindings
should support the "name intermediate steps for clarity" pattern.

---

## 11. What Transfers: Summary Table

### From Julia

| Idea | Transfer | Nomi surface |
| --- | --- | --- |
| Explicit `.` broadcasting | **Adopt** | `a .+ b`, `f.(coll)` |
| Multiple dispatch | **Defer** | Future layer; start with single dispatch + `data` patterns |
| `@.` macro for broadcast-everything | **Defer** | Needs `quote:` + macro layer first |
| Parametric types | **Adapt** | `data` with type parameters when type layer matures |
| Struct/immutable defaults | Already in | `data` declarations |
| Macros via `@` | **Defer** | Needs `quote:` boundary first |

### From R

| Idea | Transfer | Nomi surface |
| --- | --- | --- |
| Formula interface (`y ~ x1 + x2`) | **Adapt** | `quote:` captures formula-like syntax values for modeling/query DSLs |
| Data masking (column names in scope) | **Adopt** | Table verbs (`where`, `select`) with column-name resolution |
| Tidy eval `{{ }}` embracing | **Adapt** | Explicit `quote:`/`unquote:` boundaries, not implicit NSE |
| Quosures (quoted expr + env) | **Adopt** | `quote:` produces syntax values carrying their environment |
| Conditions, handlers, restarts | **Study** | Future signal/effect layer |
| Pipeline `|>` | **Adopted** | Already in Nomi |
| `on.exit` cleanup | **Adopt** | `defer` (already implemented) |
| Recycling rule | **Reject** | Unsafe implicit behavior; Julia's explicit `.` is better |
| Everything-is-vector | **Reject** | Conflates scalar and collection |

### From MATLAB

| Idea | Transfer | Nomi surface |
| --- | --- | --- |
| Colon `:` for all/slices | **Adapt** | `a[:, 2]`, `a[1..5]` |
| `.` for element-wise ops | Already covered | Julia's `.` model supersedes MATLAB's |
| Everything-is-array | **Reject** | Inappropriate for general-purpose code |
| Matrix ops as default | **Reject** | General-purpose code is mostly element-wise |
| `;` for explicit output suppression | **Defer** | Notebook/REPL concern |
| Live scripts / notebook integration | **Adapt** | Notebook tooling (already in progress) |

---

## 12. Design Pressure For Nomi

The scientific languages converge on several design pressures that apply to
general-purpose data work (not just math):

1. **Broadcasting should be visible but not noisy.** Julia's `.` is the
   gold standard: one character that says "element-wise," consistent
   across all functions and operators.

2. **Table/data-frame operations need a scoped-name model.** R's data
   masking and Q's column-name scoping both solve the same problem:
   reduce `df["col"]` noise in data transforms. Nomi's table verbs
   should adopt this with explicit scope boundaries.

3. **Formula-like syntax values are a reusable pattern.** R's formula
   interface shows that a small embedded notation (`y ~ x1 + x2`) can
   be enormously productive when it carries structure and evaluates
   in a controlled context. Nomi's `quote:` should support this.

4. **Pipeline style matches notebook/exploratory workflows.** All three
   languages have embraced pipeline-style data transforms. Nomi's `|>`
   is the right choice; it should remain the primary data-flow operator.

5. **Conditions and restarts are a better model than exceptions alone.**
   R's condition system separates signaling from handling from recovery.
   For a language that values explanation and inspectability, this
   model is more transparent than "throw/catch" binary choice.

6. **Not everything should be an array.** MATLAB and R conflate scalars
   with collections. Julia shows that keeping them separate (but with
   explicit broadcasting to bridge) produces safer, clearer code.
