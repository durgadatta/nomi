# Table and Flow Systems: Deep Dive

> Status: source research for Nomi collection/table vocabulary design.
> Purpose: study how languages and systems handle structured collections --
> filtering, transforming, grouping, joining, and querying tabular data --
> and extract the structural invariants, genuine forks, and anti-patterns that
> should inform Nomi's shared vocabulary of `where select derive group join sort
> window fold`.
>
> Companion: `docs/features/structured_collections_query_language.md` for the
> Nomi design candidates that synthesise these findings.

## 1. SQL -- The Original Declarative Query Language

### 1.1 Core Design Philosophy

SQL's design thesis, dating from Codd's relational model (1970) through Chamberlin
and Boyce's SEQUEL (1974), is that users should declare **what they want**, not
**how to get it**. The relational algebra provides a small set of operations
(projection, selection, join, union, difference, Cartesian product) that are
provably complete for expressive relational queries. SQL layered a readable
English-like syntax over this algebra.

The radical bet was that users could write `SELECT name FROM employees WHERE
salary > 50000` without understanding B-tree indexes, hash joins, or the
physical layout of data on disk. The query optimizer would figure out the how.
This bet paid off so completely that 50 years later SQL remains the lingua
franca of data work, embedded in everything from SQLite on a phone to Snowflake
on a cluster.

### 1.2 What Worked Exceptionally Well

**The SELECT/FROM/WHERE triad.** This three-clause template -- pick columns,
name the source, state the row condition -- has been copied by every
declarative query system since. It is concise, readable, and maps cleanly to
the relational algebra operations of projection, Cartesian product (with
selection), and restriction.

```sql
-- English-like and still the most-read code on the planet
SELECT name, salary
FROM employees
WHERE department = 'Engineering'
  AND salary > 80000;
```

**Composability via subqueries and CTEs.** SQL allows a query to appear
anywhere a table name can appear, giving nested queries natural composition:

```sql
WITH high_earners AS (
    SELECT name, salary, department
    FROM employees
    WHERE salary > 80000
)
SELECT department, AVG(salary) as avg_salary
FROM high_earners
GROUP BY department
HAVING AVG(salary) > 100000;
```

The Common Table Expression (CTE, `WITH` clause) was a late addition to the
standard but fixed one of SQL's worst usability problems: deeply nested
subqueries that read inside-out. CTEs make the logical flow read top-to-bottom.

**GROUP BY and HAVING.** The split between `WHERE` (filter rows before
grouping) and `HAVING` (filter groups after aggregation) is semantically clean
once understood. It encodes a genuine phase distinction between row-level and
group-level predicates. Every system that handles aggregation needs this
distinction, even if it expresses it differently.

```sql
SELECT department, AVG(salary) as avg_sal
FROM employees
WHERE hire_date > '2020-01-01'   -- row filter, before grouping
GROUP BY department
HAVING AVG(salary) > 70000;      -- group filter, after aggregation
```

**Declarative optimization.** Because SQL describes the logical result rather
than the physical execution, the optimizer has enormous freedom: it can choose
index scans over table scans, reorder joins for selectivity, push predicates
down through subqueries, and select from dozens of join algorithms. This
separation of logical intent from physical execution is SQL's deepest
architectural insight and the reason it has survived every paradigm shift in
data systems.

**The schema as contract.** SQL's type system (tables have typed columns,
constraints like NOT NULL/UNIQUE/FOREIGN KEY) means that queries can be
validated against the schema before execution. This is a form of static
analysis that catches column-not-found, type-mismatch, and ambiguity errors at
query planning time rather than at runtime.

**UNION, INTERSECT, EXCEPT.** The set operations are simple, compose cleanly,
and handle schema alignment (columns by position or name). They are far less
prone to user error than equivalent operations in imperative code.

### 1.3 What Failed or Caused Persistent Friction

**Execution order vs lexical order.** This is the single most complained-about
design choice in SQL. The actual logical execution order is:

```
FROM → JOIN → WHERE → GROUP BY → HAVING → SELECT → ORDER BY → LIMIT
```

But the written order is:

```sql
SELECT ... FROM ... JOIN ... WHERE ... GROUP BY ... HAVING ... ORDER BY ... LIMIT
```

This mismatch causes real confusion. Beginners write `WHERE total > 100` after
`GROUP BY`, expecting `total` (an alias defined in `SELECT`) to be available to
`WHERE`. Experienced users know that `WHERE` runs before `SELECT`, so column
aliases are invisible there. The HAVING clause was added specifically because
`WHERE` cannot reference aggregate results -- but the name "HAVING" gives
newcomers zero hint about when to use it vs WHERE.

The root cause: Chamberlin and Boyce chose SELECT-first because it reads like
English ("find me these columns from this table where..."). They prioritized
natural-language readability over execution-order readability. Fifty years of
evidence suggests this was the wrong tradeoff. Every new query system (dplyr,
Polars, LINQ, Nushell, PRQL) puts the source first and the projection last.

**NULL semantics (three-valued logic).** SQL's `NULL` introduces a third truth
value: `NULL = NULL` is `NULL` (not true, not false), `NULL > 5` is `NULL`,
`NULL AND FALSE` is `FALSE` but `NULL AND TRUE` is `NULL`. This creates subtle
traps:

```sql
-- This returns no rows if any salary is NULL, because NULL NOT IN (...)
-- evaluates to NULL, not FALSE, and WHERE filters NULL the same as FALSE.
SELECT name FROM employees WHERE department NOT IN (
    SELECT department FROM active_departments
);
```

Aggregate functions silently skip NULLs (`AVG([1, NULL, 3])` = 2), but
`COUNT(*)` counts NULLs while `COUNT(column)` does not. Every SQL user
eventually learns these rules through painful debugging.

The deeper problem: SQL can't distinguish "I don't know this value" from "this
value does not apply" from "this value has not been entered yet." These are
three different semantics collapsed into one marker.

**The HAVING clause confusion.** `HAVING` is semantically `WHERE` after
aggregation. But the name tells you nothing about its function, and beginners
consistently try to use `WHERE` for group-level filtering. The duplicate syntax
for what is conceptually the same operation (filter rows) but at different
phases is purely an artifact of SQL's clause-order constraint -- `WHERE` must
lexically precede `GROUP BY`, so a second keyword was needed for
post-aggregation filtering. No modern system makes this mistake.

**Stringly-typed embedding.** SQL inside a host language (Python, Java, Go) is
almost always a string literal. This means no syntax highlighting for the SQL
within the string, no compile-time checking of column names, no type-checking
across the host-query boundary, and injection vulnerabilities requiring
parameterized-query discipline. ORMs and query builders paper over this but
introduce their own impedance mismatch:

```python
# The SQL is invisible to the Python type checker
query = "SELECT name FROM employees WHERE dept = ?"
cursor.execute(query, (dept,))

# ORM close the type gap but add learning curve and leaky abstractions
Employee.select().where(Employee.dept == dept)
```

**Window functions are powerful but alien.** SQL:2003 added window functions,
which compute over ordered partitions without collapsing rows. The syntax is
verbose and unlike anything else in SQL:

```sql
SELECT name, department, salary,
       RANK() OVER (PARTITION BY department ORDER BY salary DESC) as rank,
       AVG(salary) OVER (PARTITION BY department) as dept_avg
FROM employees;
```

The `OVER (PARTITION BY ... ORDER BY ...)` syntax is a mini-language that
doesn't compose with the rest of SQL. ROWS/RANGE frame specifications make it
even more opaque. Users who need windows regularly reach for a reference card.

**Stale REPL experience.** SQL editors run whole queries; there is no
interactive step-by-step pipeline inspection. Users typically build a query by
running it, seeing the output, editing, re-running. Compare this to dplyr or
Polars where you can add one verb at a time and inspect the intermediate
result: `data |> filter(x > 0) |> head()` then add `|> group_by(col) |> head()`
and so on.

### 1.4 The Key Structural Insight for Nomi

SQL demonstrates that **declarative collection operations can compose into
optimizable plans**. The separation of logical intent from physical execution is
the property worth preserving. But SQL also demonstrates that **clause order
should match execution order** -- write the source first, filter, then
aggregate, then project. And that **a single predicate syntax should work at
all phases** (row-level and group-level) without requiring a different keyword.

Nomi should adopt SQL's declarative intention but reverse its two worst
cognitive mistakes: put source first, and use the same predicate syntax at all
levels. The Nomi verb vocabulary (`where`, `group`, `summarize`, `select`) with
flow-order execution is the direct resolution of SQL's lesson.

Sources:
- Chamberlin, D. and Boyce, R. "SEQUEL: A Structured English Query Language" (1974). ACM SIGFIDET.
- Codd, E.F. "A Relational Model of Data for Large Shared Data Banks" (1970). CACM 13(6).
- Date, C.J. "SQL and Relational Theory" (2009). O'Reilly.
- [SQL logical processing order](https://learn.microsoft.com/en-us/sql/t-sql/queries/select-transact-sql?view=sql-server-ver16#logical-processing-order-of-the-select-statement)

---

## 2. LINQ (C#) -- Query Syntax Meets General-Purpose Language

### 2.1 Core Design Philosophy

LINQ (Language Integrated Query, 2007) was Erik Meijer and the C# team's
attempt to make querying a first-class language feature rather than a
string-embedded afterthought. The fundamental insight: **query syntax can lower
to method calls on a standard set of operators**. If you define `Where`,
`Select`, `GroupBy`, `Join`, `OrderBy` as methods (extension methods, in C#
terms) that follow a predictable signature pattern, then LINQ's query
expression syntax desugars into those method calls. Users get readable query
syntax, and library authors get a single API surface to implement.

This is the most important architectural lesson in the history of query
language integration: **query syntax is sugar over a method-call vocabulary**.
The same `IEnumerable<T>` operators work over in-memory collections (LINQ to
Objects), SQL databases (LINQ to SQL, Entity Framework), XML documents (LINQ
to XML), and any other data source by implementing `IQueryable<T>`.

### 2.2 What Worked Exceptionally Well

**Query expressions lowering to method calls.** This is LINQ's master insight:

```csharp
// Query expression syntax
var results = from e in employees
              where e.Salary > 80000
              orderby e.Name
              select e.Name;

// Desugars to identical method-call chain
var results = employees
    .Where(e => e.Salary > 80000)
    .OrderBy(e => e.Name)
    .Select(e => e.Name);
```

The two forms are semantically identical. The compiler translates the first
into the second. This means no duplication of implementation, no two-kinds-
of-function problem, no impedance mismatch between "query code" and "regular
code." It is sugar all the way down, and the desugaring is specified, stable,
and inspectable.

**Extension methods as the enabling mechanism.** C# extension methods let you
"add" methods to existing types without modifying them. `Where<T>` is defined
in `System.Linq.Enumerable` as an extension method on `IEnumerable<T>`. This
means the method-call chain reads left-to-right with dot notation:

```csharp
var results = employees
    .Where(e => e.Salary > 80000)
    .GroupBy(e => e.Department)
    .Select(g => new { Dept = g.Key, Avg = g.Average(e => e.Salary) });
```

Extension methods solved the "where do these operators live" problem cleanly:
they live in the standard library, imported with `using System.Linq;`, and any
type implementing `IEnumerable<T>` gets them automatically.

**`IQueryable<T>` and query provider composition.** `IQueryable<T>` extends
`IEnumerable<T>` with an expression-tree representation of the query. When you
call `.Where(e => e.Salary > 80000)` on an `IQueryable<Employee>`, the lambda
`e => e.Salary > 80000` is captured as an expression tree (an AST), not
compiled to a delegate. The query provider (e.g., Entity Framework's SQL Server
provider) can then translate that expression tree into SQL:

```csharp
IQueryable<Employee> dbEmployees = db.Employees;
var results = dbEmployees
    .Where(e => e.Salary > 80000)  // expression tree, not delegate
    .Select(e => e.Name);           // translates to SQL WHERE + SELECT
```

This is the critical architectural pattern: **the same surface syntax, one
implementation for in-memory objects (IEnumerable, eager delegates), and a
different implementation for remote data (IQueryable, expression trees
translated to backend-native queries).**

**Deferred execution.** LINQ queries over `IEnumerable<T>` and `IQueryable<T>`
are lazy: no work happens until you enumerate the result. This enables query
composition without intermediate materialization:

```csharp
var query = employees.Where(e => e.Salary > 80000);  // no work done
query = query.OrderBy(e => e.Name);                    // still no work
var result = query.ToList();                            // query executes now
```

This is the same lazy/eager boundary that Polars, Spark, and DuckDB make
explicit. LINQ makes it implicit but predictable: `ToList()`, `ToArray()`,
`First()`, and `Count()` are the materialization triggers.

**The `let` clause for intermediate bindings.** LINQ's `let` keyword
introduces a named intermediate value visible to subsequent clauses. This
solves the "I computed something and want to use it again" problem without
forcing subqueries:

```csharp
var results = from e in employees
              let tax = e.Salary * 0.3
              let net = e.Salary - tax
              where net > 50000
              select new { e.Name, net };
```

This lowers to `Select` with a transparent identifier (the compiler creates
an anonymous type holding both `e` and the derived values). It is syntactic
sugar, but it substantially improves readability for multi-step derivations.

### 2.3 What Failed or Caused Persistent Friction

**The two-syntax problem.** Despite the clean desugaring, the C# community
split between query-expression syntax and method-call (fluent) syntax.
Style guides disagree. Codebases mix both arbitrarily. The root cause: query
expressions don't support all operators (`Take`, `Skip`, `Distinct`, `Aggregate`
have no query-expression syntax), so users must drop to method calls for these,
creating hybrid code:

```csharp
var results = (from e in employees
               where e.Salary > 80000
               select e).Distinct().Take(10);
```

The parentheses around the query expression are a visual wart that signals
"the two syntaxes don't compose elegantly." The community largely settled on
method-call syntax as the default and query expressions for joins (where the
method-call equivalent is verbose with nested lambdas). But the cultural split
is permanent.

**Lambda verbosity in method syntax.** Method-call chains require explicit
lambda parameters:

```csharp
employees.Where(e => e.Salary > 80000)
         .Select(e => e.Name);
```

The `e => e.` prefix repeats on every clause. Compare to SQL (`WHERE salary
> 80000`) or dplyr (`filter(salary > 80000)`) where the column reference is
bare. C# has no "current row" implicit context, so the lambda parameter must be
named and referenced each time. The `_` discard (C# 7+) doesn't solve this
because you need the parameter to access properties.

**Expression-tree limitations.** Only a subset of C# expressions can be
translated to expression trees. `IQueryable` providers cannot handle `switch`
expressions, pattern matching, `try`/`catch`, or non-trivial control flow in
lambdas. The error messages when you exceed these limits are runtime errors from
the query provider, not compile-time diagnostics. This creates a "two dialects"
problem within LINQ itself: things that work in LINQ to Objects fail in LINQ
to SQL.

**Join syntax is complex for the common case.** LINQ's `join ... on ... equals
...` syntax is verbose and the `equals` keyword (required, not `==`) is
confusing:

```csharp
from e in employees
join d in departments on e.DeptId equals d.Id
select new { e.Name, d.DeptName };
```

The `equals` is not an operator but a contextual keyword that exists only
inside `join...on` clauses. It confused newcomers then and confuses them now.

**Error messages expose desugaring.** When a LINQ query fails, the error
message references the generated `SelectMany`/`GroupJoin`/transparent-
identifier code, not the user's query expression. This is the classic "leaky
sugar" problem: diagnostics reveal the internal rewriting rather than the
surface syntax the user wrote.

### 2.4 The Key Structural Insight for Nomi

The LINQ insight -- **query syntax lowers to method calls on a standard
vocabulary, and that vocabulary can be backed by different execution engines** --
is the most important architectural pattern for Nomi's collection/table design.
It means Nomi does not need to choose between method chains and query blocks.
Both can exist, both can lower to the same operators, and tooling can show the
lowering.

Concretely: Nomi's `|>` pipeline with named verbs (`where`, `select`, `group`,
`join`, etc.) is the method-call layer. A future `query:` block syntax would
lower to the same verbs. The verb vocabulary is the interface; pipeline and
query-block are two surface syntaxes over it.

The second-order insight: `IQueryable`'s expression-tree capture means the
same verb can be interpreted differently by different backends. Nomi should
ensure that collection verb arguments are structural enough to be captured
and re-targeted (like Polars expressions, not opaque Python lambdas).

Sources:
- Meijer, E. et al. "LINQ: Reconciling Objects, Relations, and XML in the .NET Framework" (2006). Microsoft.
- [LINQ query expression translation (C# spec)](https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/language-specification/expressions#12819-query-expressions)
- [IQueryable and expression trees](https://learn.microsoft.com/en-us/dotnet/csharp/advanced-topics/expression-trees/)

---

## 3. dplyr (R) -- The Tidyverse Grammar of Data Manipulation

### 3.1 Core Design Philosophy

Hadley Wickham's dplyr (2014) crystallized a key idea: **data manipulation is a
grammar**, and grammars are learnable when they have a small set of orthogonal
verbs, consistent argument order (data first), and a composition operator.
dplyr's thesis: every data transformation is one of five verbs -- `filter()`,
`select()`, `mutate()`, `arrange()`, `summarise()` -- composed with
`group_by()`.

The "data frame in, data frame out" principle means every verb takes a data
frame and returns a data frame. This enables chaining: the output of one verb
is the input to the next. No hidden state, no in-place mutation (by default),
no side effects. The verb names are English verbs, not acronyms or library-
specific jargon.

### 3.2 What Worked Exceptionally Well

**The five-verb core.** The one-thing-one-verb design is dplyr's killer
feature. Users learn five names and can express 80% of data tasks:

```r
library(dplyr)

starwars %>%
    filter(species == "Human", height > 170) %>%
    select(name, height, mass) %>%
    mutate(bmi = mass / ((height / 100)^2)) %>%
    arrange(desc(bmi))
```

Each verb does exactly one thing: `filter` keeps rows, `select` keeps columns,
`mutate` adds columns, `arrange` sorts rows, `summarise` collapses rows. The
argument order is always `data, ...` (data frame first).

**`group_by()` composes naturally.** `group_by()` doesn't change the data; it
adds grouping metadata. Subsequent verbs automatically respect the grouping:

```r
starwars %>%
    group_by(species) %>%
    summarise(
        count = n(),
        avg_height = mean(height, na.rm = TRUE),
        avg_mass = mean(mass, na.rm = TRUE)
    ) %>%
    filter(count > 1) %>%
    arrange(desc(count))
```

The user writes `summarise(avg_height = mean(height))` the same way whether
grouped or ungrouped. `group_by()` changes the context in which the verb runs,
not the verb's name or syntax. This is the group-as-context pattern that every
modern table system has adopted. Nomi should follow it directly.

**The pipe as composition glue.** The `%>%` (magrittr pipe, later `|>` base R
pipe) makes the data flow visible:

```r
# Without pipe: inside-out reading
arrange(
    filter(
        summarise(
            group_by(starwars, species),
            count = n()
        ),
        count > 1
    ),
    desc(count)
)

# With pipe: left-to-right, top-to-bottom reading
starwars %>%
    group_by(species) %>%
    summarise(count = n()) %>%
    filter(count > 1) %>%
    arrange(desc(count))
```

The pipe is not dplyr-specific; it is a general R composition operator. dplyr
adopted it, but it works with any R function that takes data as the first
argument. This generality is crucial: it means dplyr verbs compose with base R
functions, ggplot2, and user-defined functions without adapter code.

**The `across()` function for column-wise operations.** Modern dplyr uses
`across()` to apply operations to multiple columns:

```r
starwars %>%
    group_by(species) %>%
    summarise(across(c(height, mass), mean, na.rm = TRUE))
```

Before `across()`, dplyr had `_all`, `_at`, `_if` variants of each verb
(`summarise_all`, `summarise_at`, `summarise_if`). These scoped variants were
a maintainability disaster -- 7 verbs x 3 variants = 21 function signatures to
document, each with subtly different behaviour. `across()` replaced all of them
with a single function that works inside any verb. This is a meta-lesson: **one
general mechanism for column selection is better than N scoped verb variants**.

**`join()` with clear semantics.** dplyr's joins are explicit about the join
type in the function name:

```r
left_join(x, y, by = "id")      # keep all x rows
inner_join(x, y, by = "id")     # keep only matches
full_join(x, y, by = "id")      # keep all rows from both
anti_join(x, y, by = "id")      # keep x rows without matches
semi_join(x, y, by = "id")      # keep x rows with matches (but don't add y columns)
```

This is clearer than SQL's `LEFT JOIN`/`INNER JOIN`/`FULL OUTER JOIN` syntax
because the function name directly says what is kept. The `by =` argument uses
bare column names when the key names match, making the common case terse.

### 3.3 What Failed or Caused Persistent Friction

**Non-standard evaluation (NSE) and tidyeval.** dplyr's biggest design
tension: column names inside `filter()`, `mutate()`, etc. are bare names
(`species == "Human"`), not quoted strings or formula references. This is
"non-standard evaluation" -- R's ability to capture unevaluated expressions and
resolve them in a custom environment. It is magical when it works and baffling
when it fails.

```r
# This works: bare column names in interactive use
starwars %>% filter(species == "Human")

# This fails if you try to use a variable for the column name
col_name <- "species"
starwars %>% filter(col_name == "Human")  # WRONG: looks for literal column "col_name"

# This is the fix: embrace the variable with {{ }}
starwars %>% filter({{ col_name }} == "Human")
```

The fix (`{{ }}` embrace operator, `:=` walrus for naming with variables,
`.data[[var]]` for programmatic access) requires users to understand the
difference between quoted and unquoted expressions, environments, quosures,
and tidy evaluation. For package authors (writing functions that accept column
names as arguments), tidyeval is a significant barrier. The dplyr team has
invested heavily in documentation and error messages, but the fundamental
complexity remains: bare column names are convenient but break programmatic
use.

The lesson for Nomi: **bare column name resolution is powerful but must have
a clear escape hatch for programmatic column references**. A `.` or `it.`
prefix for column access (like Kotlin's `it`, or Polars' `pl.col("name")`) is
more verbose but eliminates the quoted/unquoted ambiguity.

**The `_all`/`_at`/`_if` → `across()` migration.** dplyr 1.0 deprecated 21
functions in favor of `across()`. The migration was worth it but the legacy
code remains in thousands of tutorials, blog posts, and production scripts.
This is the "convenience stack-collapse" pattern from Nomi's design lessons
doc: dplyr added convenience variants, they proliferated, and then a cleaner
unified mechanism replaced them -- but the old variants never fully disappear.

**Join key mismatch surprises.** When `by =` is omitted, dplyr guesses the
join keys by intersecting column names. This is convenient for interactive use
but dangerous in scripts: adding a column to either table silently changes the
join condition. The `by =` argument should arguably be required.

```r
# Danger: silent join on all common column names
left_join(orders, customers)
# Safer: explicit
left_join(orders, customers, by = "customer_id")
```

**Data frame vs tibble vs data.table.** The R ecosystem has three competing
data frame implementations (base `data.frame`, `tibble`, `data.table`) with
slightly different printing, subsetting, and performance behaviour. dplyr works
with all three but the print/slice/inspect experience differs subtly. This is
an ecosystem fragmentation cost, not dplyr's fault, but it affects the user
experience of every data pipeline.

### 3.4 The Key Structural Insight for Nomi

dplyr's core insight is that **a small verb vocabulary + a pipe operator +
data-frame-in/data-frame-out = a complete, learnable data manipulation
language**. The verbs are not syntax; they are ordinary functions that compose
through the pipe. This is the pattern Nomi should follow for its collection
verbs: `where`, `select`, `derive`, `group`, `summarize`, `join`, `sort`,
`window`, `fold` as library functions callable through `|>`.

The second insight: **grouping is a context, not a separate verb set**.
`group_by()` changes what subsequent verbs mean without requiring the user
to learn a different vocabulary. Nomi's `group` verb should work the same way:
after `group(.region)`, `summarize(total = sum(.amount))` automatically
aggregates per group.

The third insight (negative): **bare column names create a quoted/unquoted
ambiguity that scales poorly to programmatic use**. Nomi should use a visible
prefix (`.col` or `it.col`) for column references inside query expressions,
with auto-resolution as opt-in sugar (not the default).

Sources:
- Wickham, H. et al. "dplyr: A Grammar of Data Manipulation" (2014). R package.
- [dplyr documentation](https://dplyr.tidyverse.org/)
- [Tidy evaluation](https://rlang.r-lib.org/reference/topic-data-mask.html)
- [dplyr 1.0: across()](https://www.tidyverse.org/blog/2020/04/dplyr-1-0-0-colwise/)

---

## 4. Polars -- Modern High-Performance DataFrame Library

### 4.1 Core Design Philosophy

Polars (Ritchie Vink, 2020) is an Apache Arrow-native DataFrame library written
in Rust with Python, R, and Node.js bindings. Its core thesis: **expressions
are first-class, composable objects that describe columnar computations**.
Instead of passing opaque Python lambdas (as pandas does), users build Polars
expression trees with `pl.col()`, `.alias()`, `.cast()`, `.sum()`, etc. These
expressions are structural -- they can be inspected, optimized, and retargeted
to different execution modes (eager, lazy, streaming).

Polars is the closest existing system to what Nomi's collection/query layer
should be. Its expression model, lazy/eager split, `explain()` output, and
optimizer architecture are directly applicable to Nomi's design.

### 4.2 What Worked Exceptionally Well

**The expression system as structural computation.** Every operation in Polars
is or returns an expression. Expressions are composable: you build them from
smaller expressions, and the optimizer can inspect and rewrite them:

```python
import polars as pl

# Expressions as first-class values
is_high_salary = pl.col("salary") > 80000
net_pay = (pl.col("salary") - pl.col("tax")).alias("net")
upper_name = pl.col("name").str.to_uppercase()

# Compose them in a context
result = (
    employees
    .filter(is_high_salary)
    .select(upper_name, net_pay)
)
```

The critical property: `is_high_salary`, `net_pay`, and `upper_name` are
values you can store, pass around, compose, and reuse. They are not callbacks.
The Polars optimizer can push `is_high_salary` down to the scan operator,
eliminate unused columns from `net_pay`'s input, and fuse `str.to_uppercase()`
with other string operations.

This is fundamentally different from pandas, where `.apply(lambda row: ...)`
is an opaque Python function the optimizer cannot see inside. Polars'
expression model means the optimizer can reason about the entire query plan
as a tree of known operations.

**Lazy and eager modes with identical API.** Polars' `LazyFrame` has the same
methods as `DataFrame` (eager). The difference is **when computation happens**:

```python
# Eager: executes immediately
result = df.filter(pl.col("x") > 0).select("y")

# Lazy: builds a plan, nothing executes yet
plan = df.lazy().filter(pl.col("x") > 0).select("y")
result = plan.collect()  # query runs now

# The API is identical
```

This is the right design for Nomi: collection verbs should produce an
intermediate plan when piped over a lazy source, and execute immediately
when piped over an eager source. The user writes the same code either way.

**`explain()` for query plan inspection.** Polars can show the optimized
query plan as a string or graph:

```python
plan = (
    df.lazy()
    .filter(pl.col("status") == "paid")
    .group_by("customer_id")
    .agg(pl.col("amount").sum().alias("total"))
)
print(plan.explain())
```

Output (simplified):
```
AGGREGATE
  [total] BY [customer_id] FROM
    FILTER [(status == "paid")] FROM
      CSV SCAN data.csv
      PROJECT */6 COLUMNS
```

This is a first-class debugging tool. It answers "what will this query
actually do?" and "why is it slow?" without requiring the user to understand
the optimizer internals. The plan is readable, structural, and maps back to
the user's verbs. Nomi should provide the same: `explain pipeline` should
produce a stage-by-stage plan with schema at each stage.

**Streaming / out-of-core execution.** Polars can execute queries on data
larger than RAM by processing in batches:

```python
# Stream through the file; never materialize fully in memory
for batch in df.lazy().filter(...).select(...).collect(streaming=True):
    process(batch)
```

This is a natural consequence of the expression model: if the system knows
what operations will be applied (filter, select, aggregate), it can arrange
for them to run in a streaming pipeline without ever holding the full dataset
in memory. Nomi's collection verbs should be designed with this in mind:
verbs should be operations that can run over batches, not operations that
assume full materialization.

**Schema maintained across operations.** Every Polars expression knows its
output type. The schema is tracked through the query plan:

```python
plan = df.lazy().select(
    pl.col("salary").cast(pl.Float64).alias("float_salary")
)
print(plan.collect_schema())
# Schema: [('float_salary', Float64)]
```

If you try to `.sum()` a string column, Polars catches it at plan-building
time (before any data is processed). This is the kind of early error detection
that Nomi's constraints should enable: column types are part of the schema,
and verb operations validate against them before execution.

**`join()` with explicit key and cardinality awareness.** Polars joins are
clean:

```python
df.join(
    other,
    on="id",           # key column (same name in both)
    how="left"         # inner, left, outer, cross, semi, anti
)
```

The `validate` parameter checks cardinality assumptions:

```python
df.join(other, on="id", how="left", validate="1:1")   # expect one-to-one
df.join(other, on="id", how="left", validate="m:1")   # many-to-one
```

If the validation fails (e.g., you asked for 1:1 but the right table has
duplicate keys), Polars raises an error. This is a structural check, not a
runtime probabilistic test. Nomi's `join` should provide the same.

### 4.3 What Failed or Caused Persistent Friction

**`pl.col()` verbosity in long chains.** Every column reference requires
`pl.col("name")`:

```python
df.filter(
    pl.col("status") == "paid"
).group_by(
    pl.col("customer_id")
).agg(
    pl.col("amount").sum().alias("total"),
    pl.col("amount").mean().alias("avg"),
)
```

This is 16 characters of overhead (`pl.col("...")`) for every column
reference. Compare with dplyr `filter(status == "paid")` or SQL `WHERE status
= 'paid'`. Polars 1.0 added `col = pl.col` as an import convention
(`col("name")`), but this is a user convention, not a language feature.

The right Nomi design: inside query contexts (pipeline verbs taking table
operations, or a `query:` block), allow `.status` as shorthand and require
the full reference only when disambiguation is needed. Outside query contexts,
require explicit column reference.

**Expression API surface is large.** Polars' expression API covers hundreds
of methods across `pl.Expr.str`, `pl.Expr.dt`, `pl.Expr.list`, `pl.Expr.struct`,
`pl.Expr.arr`. At time of writing, `pl.Expr` has over 400 methods. This is
necessary for a production DataFrame library -- users need date parsing, string
extraction, JSON flattening -- but it means the "small vocabulary" ideal
doesn't scale to real-world data work. Nomi should accept this: the core verbs
are small, but column-level operations (string, datetime, math) will need a
rich standard library of expression functions.

**The DataFrame vs LazyFrame type distinction.** Users must remember to call
`.lazy()` to enter plan-building mode and `.collect()` to execute. Forgetting
`.lazy()` means you execute eagerly and lose optimization. Forgetting
`.collect()` means you have a `LazyFrame` when you expected a `DataFrame`.
Polars' error messages for this are good, but the type distinction is a
persistent papercut. Nomi should consider whether the lazy/eager distinction
needs to be explicit at all, or whether it can be inferred from context (e.g.,
destination is a `Table` value = collect; destination is a `Plan` = don't).

**Python/NumPy interop overhead.** Passing data between Polars and NumPy/pandas
involves converting via PyArrow, which has non-trivial overhead for small
datasets. This is an ecosystem problem, not a design problem, but it affects
the experience of using Polars inside a Python data pipeline. Nomi's native
collection types should avoid this by being the first-class representation from
day one.

### 4.4 The Key Structural Insight for Nomi

Polars' expression system is the blueprint for Nomi's collection verb
arguments. Nomi's `where(.status == "paid")` should capture the predicate
`.status == "paid"` as a structural expression, not as an opaque Python lambda.
This expression can then be:

1. Evaluated directly (eager mode, in-memory collection).
2. Included in a query plan (lazy mode, for optimization).
3. Translated to a backend-specific representation (SQL, Arrow compute).
4. Displayed in `explain()` output.

The principle: **verb arguments are structural expressions, not callbacks.**
This is what makes `explain()`, schema validation, backend retargeting, and
streaming execution possible.

The second insight: Polars' `explain()` is not a nice-to-have -- it is
essential infrastructure. Every table/collection system needs a way for users
to ask "what is this query going to do?" without running it. Nomi should build
`explain` into the collection verb system from the start, not bolt it on later.

Sources:
- [Polars expressions and contexts](https://docs.pola.rs/user-guide/concepts/expressions-and-contexts/)
- [Polars lazy API](https://docs.pola.rs/user-guide/concepts/lazy-api/)
- [Polars optimizer](https://docs.pola.rs/user-guide/lazy/optimizations/)
- Vink, R. "Polars: Lightning-fast DataFrame library" (2020).

---

## 5. DuckDB -- Embedded Analytical Database

### 5.1 Core Design Philosophy

DuckDB (Hannes Muhleisen and Mark Raasveldt, 2019) is an in-process OLAP
database. It compiles to a library that runs inside the host process (Python,
R, Node.js, Java, C++, Rust, etc.), reading and writing directly from host-
language data structures (Pandas DataFrames, Arrow tables, R data.frames)
without serialization or a client-server boundary.

The core insight: **for analytical workloads on local data, you do not need
a database server**. You need a query optimizer and execution engine that
works on in-memory or on-disk data in the same process. DuckDB's SQL
interface is fully standard, but its embedding model is what makes it
relevant to Nomi: it proves that query optimization belongs inside the
language runtime, not in a separate process.

### 5.2 What Worked Exceptionally Well

**In-process embedding with zero-copy interop.** DuckDB reads Pandas
DataFrames, Arrow tables, and R data.frames directly from memory without
copying:

```python
import duckdb
import pandas as pd

df = pd.read_csv("sales.csv")
# Query the Pandas DataFrame directly -- no import, no serialization
result = duckdb.sql("""
    SELECT region, SUM(amount) as total
    FROM df
    WHERE status = 'paid'
    GROUP BY region
    ORDER BY total DESC
""").df()
```

The `df` variable in SQL refers directly to the Python variable. There is
no `CREATE TABLE`, no `INSERT`, no ETL step. DuckDB reads the Arrow memory
layout directly, which is columnar (struct-of-arrays), matching its own
internal storage format.

This removes the most painful part of SQL-in-Python: the boundary crossing
between the host language's data and the SQL engine's data. DuckDB makes SQL
feel like a library call on host-language values.

**Friendly SQL extensions.** DuckDB adds ergonomic SQL features that address
real friction points:

```sql
-- GROUP BY ALL: group by all non-aggregated columns
SELECT region, product, SUM(amount) as total
FROM sales
GROUP BY ALL;

-- SELECT * EXCLUDE / REPLACE
SELECT * EXCLUDE (created_at, updated_at) FROM users;
SELECT * REPLACE (upper(name) AS name) FROM users;

-- Column expressions in WHERE (no subquery needed)
SELECT * FROM sales WHERE amount > AVG(amount);

-- Trailing commas (finally)
SELECT
    region,
    product,
    SUM(amount) as total,
FROM sales
GROUP BY ALL;

-- Direct file queries
SELECT * FROM 'sales.csv';
SELECT * FROM 'data/*.parquet';
```

Each of these fixes a specific SQL annoyance that has existed for decades.
`GROUP BY ALL` eliminates the tedious repetition of column names. `EXCLUDE`
solves the "I want almost all columns except these two" problem. Direct file
queries remove the `CREATE TABLE`/`COPY` ceremony for ad-hoc analysis.

The lesson: **even SQL -- the most established declarative query language --
benefits from ergonomic improvements that reduce ceremony**. Nomi can avoid
most of these problems from the start by designing its query syntax to be
ceremony-free.

**Vectorized execution engine.** DuckDB uses a vectorized execution model
(Morsel-driven parallelism): data flows through the query pipeline in
batches (vectors of ~2048 rows), and each operator processes a batch at a
time. This gives better cache locality than row-at-a-time processing (typical
OLTP databases) and lower overhead than full-column-at-a-time processing
(which requires materializing intermediate columns).

For Nomi, this validates the architectural direction: collection verbs should
be designed to work over batches, not individual elements or fully materialized
collections.

**Rich type system.** DuckDB supports nested types (STRUCT, LIST, MAP) as
first-class values:

```sql
SELECT
    user_id,
    orders[:2] as first_two_orders,  -- list slicing
    orders[1].amount as first_amount, -- struct field access
FROM users;
```

This means you do not need to flatten/join every time you work with nested
data. JSON and Parquet files with nested structure are queried naturally.
Nomi's type system should support the same: records, lists, and maps as
column types in tables, with direct access syntax.

**`EXPLAIN` and `EXPLAIN ANALYZE`.** DuckDB can show the query plan before
or after execution:

```sql
EXPLAIN SELECT region, SUM(amount) FROM sales GROUP BY region;
-- Shows the logical and physical plan, optimizer rewrites, cardinality estimates

EXPLAIN ANALYZE SELECT ...;
-- Shows the plan PLUS actual row counts and timings per operator
```

The `EXPLAIN ANALYZE` output shows where time is spent and whether the
optimizer's cardinality estimates were accurate. This is the gold standard
for query plan introspection. Nomi's `explain` should aspire to the same:
a stage-by-stage breakdown with schema at each step, optimizer rewrites
visible, and (after execution) actual row counts and timings.

### 5.3 What Failed or Caused Persistent Friction

**SQL as the only interface.** Despite DuckDB's excellent embedding, the
interface to the query engine is still SQL strings. This means:

```python
# Column names in strings -- no IDE completion, no refactoring
result = duckdb.sql("""
    SELECT rgn, SUM(amt) FROM df  -- typo: "rgn" not "region", caught at runtime
""")
```

There is a Python relational API (`duckdb.sql("FROM df").filter("amount > 0")`)
but it is less ergonomic than Polars' expression API and still relies on string-
typed column references. A relational algebra API is in development but not yet
the primary interface.

**Limited relational API.** DuckDB's Python relation API (`duckdb.from_df(df)`)
exists but has a smaller surface area than Polars or pandas. Users who want
expression-based composition typically reach for Polars and use DuckDB as the
execution engine (`polars.scan_parquet().collect(engine=duckdb_engine)`).

**The write-path ceremony.** Reading from host-language values is
zero-copy. Writing results back requires explicit conversion:

```python
result = duckdb.sql("SELECT * FROM df WHERE x > 0").df()     # to Pandas
result = duckdb.sql("SELECT * FROM df WHERE x > 0").arrow()  # to Arrow
result = duckdb.sql("SELECT * FROM df WHERE x > 0").pl()     # to Polars
```

The `.df()`, `.arrow()`, `.pl()` calls are a minor friction point but signal
a deeper issue: DuckDB doesn't know what "native" means in the host language
because each host language has different native types.

Nomi can avoid this entirely: if Nomi has a first-class `Table` type, DuckDB
(or a Nomi-native query engine) can return a `Table` directly, with zero
conversion.

### 5.4 The Key Structural Insight for Nomi

DuckDB proves that **an embedded query engine with zero-copy access to host-
language data structures is a compelling architecture**. Nomi should not
require a separate database process or wire protocol for query execution.
The query plan should execute on Nomi-native `Table` values, in-process,
with columnar memory layout.

The second insight: DuckDB's Friendly SQL features (`GROUP BY ALL`, `EXCLUDE`,
`REPLACE`, direct file queries, trailing commas) are not gimmicks -- they fix
real friction points that have persisted in SQL for decades. Nomi should
design its collection syntax to be friendly from the start: no mandatory
column repetition, easy column exclusion, zero-ceremony file reading.

The third insight: **`EXPLAIN` output should be readable, structural, and
include the optimizer's decisions**. DuckDB's `EXPLAIN` is the model for what
Nomi's `explain` should produce: a stage-by-stage tree that a data-literate
user (not a database internals expert) can understand.

Sources:
- Raasveldt, M. and Muhleisen, H. "DuckDB: an Embeddable Analytical Database" (2019). SIGMOD.
- [DuckDB Friendly SQL](https://duckdb.org/docs/stable/sql/dialect/friendly_sql)
- [DuckDB query execution](https://duckdb.org/docs/stable/internals/vector_execution)
- [DuckDB EXPLAIN](https://duckdb.org/docs/stable/guides/meta/explain)

---

## 6. Nushell -- Structured Shell Pipelines

### 6.1 Core Design Philosophy

Nushell (~2019) takes the Unix pipeline model (`stdout | stdin` text streams)
and replaces text with structured tables. Every command in Nushell outputs
structured data (a table with typed columns), and every subsequent command
in the pipeline receives that structured data. The filter/transform verbs --
`where`, `select`, `sort-by`, `group-by` -- work on rows and columns, not
on lines of text.

The key insight: **the shell pipeline is a natural query composition model**.
Users already think in pipes. If the data flowing through the pipe is typed
and structured rather than flat text, then `grep` becomes `where`, `awk
'{print $1, $2}'` becomes `select col1 col2`, `sort` becomes `sort-by col`.

### 6.2 What Worked Exceptionally Well

**Typed tables as universal interchange.** Every Nushell command that produces
output produces a table. Every command that consumes input expects a table
(or can iterate over a table's rows). This means commands compose without
the text-parsing glue that dominates traditional shell scripting:

```nu
# Nushell: structured, type-aware
> ls | where size > 1mb | sort-by modified | select name size
╭────┬───────────┬───────────╮
│  # │   name    │   size    │
├────┼───────────┼───────────┤
│  0 │ data.csv  │ 2.3 MB    │
│  1 │ log.txt   │ 5.1 MB    │
╰────┴───────────┴───────────╯

# Traditional shell: text parsing with awk/sed/perl
ls -l | awk '$5 > 1048576 { print $NF, $5 }' | sort -k2
```

The difference is not cosmetic. The second command breaks silently if a
filename contains a space. The first command works correctly with any
filename because the `name` column is a string value, not a whitespace-
delimited field.

**The verb vocabulary is small and consistent:**

| Nushell verb | What it does |
|-------------|-------------|
| `where` | Filter rows by predicate |
| `select` | Choose columns |
| `sort-by` | Order rows |
| `group-by` | Partition rows by key |
| `each` | Apply a closure to each row |
| `first`/`last`/`skip`/`take` | Limit/subset rows |
| `uniq`/`uniq-by` | Remove duplicates |
| `merge`/`append` | Combine tables |
| `rename` | Rename columns |
| `update`/`insert`/`upsert` | Modify/add column values |
| `pivot` | Long-to-wide reshape |
| `drop` | Remove columns |

These are learned in a day and usable forever. The names are ordinary English
words, not shell arcana. This is the same verb-minimalism that dplyr and Polars
demonstrate: 10-15 verbs cover 90% of data manipulation.

**The boundary between stringly-typed and structured data.** Nushell's
`from csv`, `from json`, `from xml`, `from yaml` commands are parsers that
convert external formats into structured tables. `to csv`, `to json`, etc.
convert tables back to external formats:

```nu
> open data.csv           # opens as structured table
| where amount > 100      # filter rows
| select name, amount     # choose columns
| sort-by amount          # order
| to json                 # serialize back
```

This is a clean boundary pattern: parse at the edge, work with structured
data in the middle, serialize at the other edge. Nomi should follow the
same pattern: `Data.decode` at the boundary, collection verbs in the middle,
serialization at the output boundary.

**Pipeline inspection at every step.** Nushell's `describe` command shows
the schema and type of the data passing through the pipeline:

```nu
> ls | describe
table<name: string, type: string, size: filesize, modified: date>
```

This is inline `explain` -- you can insert `describe` at any point in a
pipeline to see the current shape. Nomi's `explain` should support the same:
a stage-by-stage schema view that works on intermediate pipeline stages,
not just final results.

### 6.3 What Failed or Caused Persistent Friction

**Table vs list impedance.** Not all Nushell data is a table. Some commands
return lists (e.g., `each` applied to a list returns a list). Some commands
expect tables and fail on lists. The user must know which type each verb
expects and returns:

```nu
# This works: ls produces a table
> ls | where size > 1mb

# This doesn't: some commands produce lists
> [1 2 3] | where $it > 1   # works (list with where)
> [1 2 3] | select $it       # fails (select expects table columns)
```

This is the "two collection types" problem: lists and tables are different
data structures, and verbs vary in which they accept. Nomi should either
unify these (a list is a single-column table with no column name) or make
the distinction explicit and visible in the verb documentation and error
messages.

**Closure syntax is heavy for simple predicates.** Nushell uses `|variable|
expression` for closures:

```nu
> ls | where { |row| $row.size > 1mb }
> ls | where size > 1mb                 # shorthand (column reference)
```

The shorthand works for simple column comparisons but the closure syntax is
needed for anything non-trivial. The `{ |row| ... }` syntax is a small but
persistent readability tax compared to dplyr's bare column names or Polars'
`pl.col()`.

**Performance ceiling for large data.** Nushell is not a database; it
materializes tables at each pipeline step. A pipeline like `open huge.csv
| where ... | group-by ... | each { ... }` processes the entire dataset
in memory at each stage. There is no query optimizer, no predicate pushdown,
no lazy evaluation. For terabyte-scale data, this is a hard ceiling.

Nomi should not hit this ceiling because Nomi's collection verbs should
produce query plans (not materialized results) when the source is lazy.
The Nushell lesson is that pipeline syntax is excellent for composition but
needs an optimizer behind it for data of any scale.

### 6.4 The Key Structural Insight for Nomi

Nushell demonstrates that **the pipeline model is an excellent mental model
for data transformation**, and that **a small verb vocabulary on structured
tables replaces hundreds of lines of text-parsing shell scripts**. Users who
know Unix pipes already know Nushell's composition model; they only need to
learn the verb names.

For Nomi, this validates the pipeline + verb vocabulary approach. Nomi's
`data |> where(.x > 0) |> select(.name, .value) |> sort(.name)` is the same
pattern as Nushell's `data | where x > 0 | select name value | sort-by name`.
The difference: Nomi should have an optimizer and query plan behind it, so the
pipeline does not materialize after every step.

The second insight: **`describe`/`explain` inline in the pipeline is a
debugging superpower**. Nomi should let users insert `explain` at any point
in a pipeline to see the schema and plan at that point.

Sources:
- [Nushell documentation](https://www.nushell.sh/book/)
- [Nushell data model](https://www.nushell.sh/book/data_types.html)
- [Nushell pipelines](https://www.nushell.sh/book/pipelines.html)

---

## 7. pandas (Python) -- The Incumbent DataFrame Library

### 7.1 Core Design Philosophy

pandas (Wes McKinney, 2008) brought labeled, mixed-type, in-memory tabular
data to Python when the alternatives were NumPy structured arrays (no labels,
homogeneous types) and relational databases (heavy, external). Its design was
organic: it started as a collection of useful operations on labeled 2D data,
and it grew by accretion as users requested features. There was never a single
coherent "grammar of data" guiding its API.

This organic growth is both the reason for pandas' dominance (it had what
people needed, when they needed it) and its most persistent source of friction
(there are often 3-5 ways to do the same thing, and they interact unexpectedly).

### 7.2 What Worked Exceptionally Well

**Rich, comprehensive feature set.** For virtually any data manipulation task,
pandas has a function. Stack, unstack, pivot, melt, merge, join, concat, groupby,
resample, rolling, expanding, ewm, apply, transform, agg, pipe, query, eval --
all in one library. The sheer breadth means that once you learn pandas, you
rarely need to leave it for another library.

```python
# A typical pandas data pipeline
result = (df
    .query("status == 'paid'")
    .groupby("customer_id")
    .agg(total=("amount", "sum"), count=("amount", "count"))
    .query("total > 1000")
    .sort_values("total", ascending=False)
    .head(20)
)
```

**The `groupby()` split-apply-combine pattern.** `groupby()` is pandas' most
powerful abstraction. It splits the data into groups, applies a function to
each group, and combines the results:

```python
df.groupby("region")["amount"].agg(["sum", "mean", "std"])
df.groupby("region").apply(lambda g: g.nlargest(3, "amount"))
df.groupby("region").transform(lambda g: (g - g.mean()) / g.std())
```

The split-apply-combine mental model is intuitive and maps cleanly to the
relational algebra's grouping + aggregation. dplyr, Polars, and SQL all
implement the same pattern, though with different syntax.

**Method chaining via `.pipe()`.** pandas added `.pipe()` to support
chainable composition of custom operations:

```python
def add_bmi(df):
    return df.assign(bmi=df["mass"] / ((df["height"] / 100) ** 2))

result = (df
    .pipe(add_bmi)
    .query("bmi > 25")
)
```

`.pipe()` passes the DataFrame as the first argument, making custom functions
compose in the method chain. This is the same pattern as F#/Elixir `|>` and
R's `%>%`. The lesson: chainable composition is a user demand that will be
filled one way or another. If the language doesn't provide it natively, users
will emulate it.

**Rich plotting integration.** `.plot()`, `.hist()`, `.boxplot()` methods
on DataFrames make exploratory data analysis a one-liner. The tight coupling
between data manipulation (pandas) and visualization (matplotlib/seaborn) is
a key reason pandas dominates exploratory workflows.

### 7.3 What Failed or Caused Persistent Friction

**Too many ways to do the same thing.** This is the #1 complaint about pandas:

```python
# Access column: df["col"], df.col, df.loc[:, "col"], df.iloc[:, 0]
# Filter rows: df[df["col"] > 0], df.loc[df["col"] > 0], df.query("col > 0")
# Add column: df["new"] = ..., df.assign(new=...), df.insert(...), df.loc[:, "new"]
# Aggregation: df.groupby().agg(), df.groupby().aggregate(), df.groupby().apply()
```

Each method exists for a historical reason (e.g., `.loc` handles label-based
indexing that `.iloc` cannot, `.query()` supports expressions that `.loc`
doesn't). But the result for learners is paralysis: which one should I use?

This is the canonical "convenience stack-collapse" from Nomi's design lessons.
pandas has at least 5 orthographic variants per operation category, accumulated
over 15+ years. Nomi's response: **one way per verb, with a visible desugaring
so tooling can show that two spellings are the same**.

**Index confusion.** pandas' index is a row-labeling system that is distinct
from the data columns. Indexes can be single-level, multi-level, integer,
string, datetime. They have their own alignment semantics (arithmetic
operations align on index), and they interact with `groupby`, `merge`, `join`,
and `concat` in non-obvious ways:

```python
# Reset index to turn index into a regular column
df.reset_index()

# Set a column as the index
df.set_index("date")

# But now row selection differs:
df.loc["2020-01-01"]   # label-based, uses index
df.iloc[0]             # position-based, ignores index
```

The index is powerful for time-series alignment but creates a permanent
cognitive overhead: "is this column an index or a regular column?" In many
workflows, the index is `.reset_index(drop=True)`'d away immediately.

Nomi should avoid a separate index system. A table has columns; some columns
may be declared as keys (primary, foreign, or ordering). There is no separate
"index" dimension. Key metadata is visible and inspectable, not a hidden
alignment mechanism.

**Chained assignment ambiguity.** This is a long-standing pandas gotcha:

```python
# This MIGHT modify the original, or it might not. No way to know without
# understanding whether df.loc[df["x"] > 0] returns a view or a copy.
df.loc[df["x"] > 0]["y"] = 10   # SettingWithCopyWarning
```

The root cause is NumPy's view/copy semantics: sometimes a slice returns a
view (modifying it modifies the original), sometimes a copy (modifying it
does nothing). Pandas cannot know at index-time which will happen, so it
emits the `SettingWithCopyWarning`. This warning is universally despised -- it
appears in contexts where the user is doing nothing wrong, and it requires
deep understanding of pandas internals to suppress.

Nomi's response: **mutation should be explicit and visible**. `derive` adds
columns to a new table (no mutation). If mutation is desired, use an explicit
`mutate` or assignment syntax that the system can statically verify as safe.

**`inplace=True` proliferation.** Many pandas methods have an `inplace` flag:

```python
df.drop("col", axis=1, inplace=True)   # modifies df
df.drop("col", axis=1)                 # returns new DataFrame
```

This creates two code styles (mutating vs functional) that appear identical
except for a boolean flag. The ambiguity makes code review harder and leads to
bugs where `inplace=True` returns `None` (the method modifies in place and
returns nothing). The `inplace` parameter is being deprecated in pandas 3.0,
but existing code will carry it for years.

Nomi should not expose mutation flags on data-transformation verbs. By default,
verbs return new values. Mutation, if supported, should be a separate operation
with visible syntax.

**Performance surprises and the `.apply()` trap.** `.apply()` is the "do
anything" escape hatch, but it is orders of magnitude slower than vectorized
operations:

```python
# Fast: vectorized
df["z"] = df["x"] + df["y"]

# Slow: apply with Python function
df["z"] = df.apply(lambda row: row["x"] + row["y"], axis=1)
```

New pandas users consistently reach for `.apply()` because it looks like
`map()` or a `for` loop. The performance cliff is invisible until their
dataset grows. The fix (vectorized operations) requires thinking in columns,
not rows, which is a cognitive leap.

Nomi's structural expression model should make this cliff visible: column-
level expressions (like Polars) should be the primary API, with row-level
iteration as an explicit opt-in with a visible performance cost.

### 7.4 The Key Structural Insight for Nomi

pandas is the most important **negative** case study for Nomi. Its strengths
(breadth, community, integration) were achieved despite API flaws, not because
of coherent design. The specific lessons:

1. **No separate index.** Keys are columns with metadata.
2. **One way per verb.** No `.loc`/`.iloc`/`[]`/`.query()`/`.eval()`
   multiplicity.
3. **No `inplace=True`.** Verbs return new values. Mutation is explicit and
   separate.
4. **No view/copy ambiguity.** Immutable data structures or explicit copy
   operations.
5. **Structural expressions over opaque callbacks.** The `pl.col()` model, not
   the `.apply(lambda row: ...)` model.
6. **No `SettingWithCopyWarning`.** If the language needs to warn about
   ambiguous semantics, the semantics are wrong.
7. **Method chaining is user demand.** Provide `|>` as the canonical
   composition operator so users don't invent `.pipe()`.

Sources:
- McKinney, W. "pandas: a Foundational Python Library for Data Analysis and Statistics" (2011).
- [pandas documentation](https://pandas.pydata.org/docs/)
- [pandas API design principles](https://pandas.pydata.org/docs/development/design.html)
- [pandas SettingWithCopyWarning](https://pandas.pydata.org/docs/user_guide/indexing.html#returning-a-view-versus-a-copy)

---

## 8. K/Q -- Array Languages Applied to Tables

### 8.1 Core Design Philosophy

K and Q (Arthur Whitney, 1993/2003) are array languages where tables are
first-class data structures, not database entities. In K/Q, a table is a
dictionary of column vectors -- essentially a struct-of-arrays layout. The
language's array-oriented primitives (each, over, scan, where) apply to
tables naturally because a table IS an array (of arrays).

The design philosophy: **every operation that works on a list should work
on a table column, and every query is an expression in the language**.
There is no separate query language -- qSQL is just syntax sugar over
functional query expressions, which are ordinary q expressions producing
table values.

### 8.2 What Worked Exceptionally Well

**Tables as ordinary values.** In Q, a table literal is concise:

```q
orders: ([] id: 1 2 3; customer_id: `c1`c1`c2; status: `paid`open`paid; amount: 20 15 30)
```

This creates a table with named columns. The table is a value like any other.
You can pass it to a function, assign it to a variable, nest it inside another
table, or return it from a function. There is no impedance mismatch between
"query code" and "application code."

**qSQL as surface syntax.** Q provides SQL-like query syntax:

```q
select total: sum amount, count: count i by customer_id from orders where status = `paid
```

But this qSQL expression **is just syntactic sugar** for a functional form:

```q
?[orders; where (=; `status; `paid); (enlist `customer_id)!enlist `customer_id;
  (`total`count)!(sum; `amount), (count; `i)]
```

The functional form is an ordinary q expression. Any Q program can
construct this expression programmatically -- there is no string generation,
no injection risk, no "query builder" library. The language IS the query
builder.

This is an even deeper version of the LINQ insight. LINQ's query expressions
lower to method calls. Q's qSQL lowers to functional expressions. Both
demonstrate that **query syntax should be sugar over a value-level API**.

**Struct-of-arrays columnar layout.** Q tables store each column as its own
vector. Column operations (sum, average, filter, sort) are operations on
vectors, which are cache-efficient and SIMD-friendly. Row operations (accessing
all fields of a single row) are also fast because column vectors are aligned:
row N is at position N in every vector.

This columnar layout is the same architecture that Arrow, Polars, and DuckDB
use. K/Q got there first and proved that it works for "everything" -- not just
analytical queries but also transaction processing, streaming, and real-time
systems.

**Terse-but-composable operations.** Q can express complex transformations in
very little code:

```q
-- Sales ranking by department
select name, dept, amount, r: rank amount by dept from sales

-- Running total per customer
update running: sums amount by customer_id from orders

-- Pivot: count by status per customer
exec status!count i by customer_id from orders
```

Each of these is one expression. The combinators (`by`, `update`, `exec`,
`select`) compose without nesting. The terseness is not gratuitous -- it means
that a data transformation that would be a 20-line dplyr pipeline is a single
line of q, and therefore easier to compose, debug, and reason about.

**IPC and streaming built in.** Kdb+ (the database built on Q) supports
publish-subscribe, streaming queries, and in-memory + on-disk tables as
a unified abstraction. A query can join an in-memory table with an on-disk
table with a streaming feed -- the same `select` syntax covers all three.

### 8.3 What Failed or Caused Persistent Friction

**Extreme terseness reduces readability for non-experts.** Q's syntax is
information-dense to the point of being a barrier:

```q
?[t; ((=; `status; `paid); (>; `amount; 100)); 0b; `name`amount!`name`amount]
```

This is a functional query selecting `name` and `amount` where `status=paid`
and `amount>100`. An experienced q programmer reads this fluently. A
newcomer cannot guess what it does.

The lesson for Nomi: **terseness is a power tool, not a default**. Nomi's
collection verb names should be readable English words. The `_` hole shorthand
and pipeline `|>` provide conciseness without sacrificing readability. A dense
symbolic layer could be a future opt-in, never the only spelling.

**The interpreter is proprietary and expensive.** Kdb+ is a commercial product
with high licensing costs. This limited adoption outside finance. The language
design is excellent, but the distribution model prevented it from becoming the
"universal data language" it could have been.

**Small community, limited ecosystem.** Q has fewer than 50,000 developers
worldwide (most in finance). There are fewer open-source libraries, Stack
Overflow answers, and tutorials than for any other language with comparable
power. This is a distribution/ecosystem failure, not a language design failure,
but it means that Q's design insights are underappreciated.

**Error messages assume expertise.** Q's error messages are terse to match the
language. A type error in a complex `?[]` functional form can produce a cryptic
message that requires understanding of the functional query template. This is
the opposite of what Nomi's Explanation normal form requires: diagnostics
should use the user's vocabulary, not the implementation's.

### 8.4 The Key Structural Insight for Nomi

Q proves that **tables are ordinary language values, and query syntax should
lower to functional expressions**. This is the same insight as LINQ but arrived
at from the array-language direction rather than the object-oriented direction.
The convergence is striking.

The key structural takeaway for Nomi:

1. **Tables are values, not database artifacts.** A table literal, a query
   result, a file load, and an API response produce the same `Table` type.
2. **Columnar layout is the right default.** Struct-of-arrays, not array-of-
   structs.
3. **Query syntax lowers to functional form.** Nomi's `query:` blocks (future)
   should lower to the same verb-call chain that `|>` pipelines produce.
4. **Keys as metadata, not separate structures.** `keyed by customer_id` is
   table metadata. No separate index system.
5. **The language is the query builder.** Users should never generate Nomi
   syntax as strings. If they need to programmatically construct a query, they
   should use the same values and functions that the query syntax desugars into.

Sources:
- Whitney, A. "K" and "Q" programming languages. KX Systems.
- [Q for Mortals](https://code.kx.com/q4m3/)
- [qSQL queries](https://code.kx.com/q/basics/qsql/)
- [Functional qSQL](https://code.kx.com/q/basics/funsql/)

---

## 9. Cross-Language Synthesis

### 9.1 Structural Invariants -- Patterns Across All Successful Systems

After studying SQL, LINQ, dplyr, Polars, DuckDB, Nushell, pandas, and K/Q,
these patterns appear in every successful table/flow system:

**1. The verb vocabulary is 10-15 words, not 100.**
Every system has a small core: filter/where, select/project, derive/mutate,
aggregate/summarize, group, sort/order, join. The exact names differ but the
set of operations is stable across paradigms and decades. Systems that add
more verbs do so for specialized operations (reshape, window) that belong on
a separate shelf, not mixed into the core.

**2. Pipeline composition ("data in, data out") is universal.**
Whether the syntax is `|>` (Nomi, dplyr, Elixir), `.method()` chaining (LINQ,
Polars, pandas), SQL subqueries/CTEs, or `|` (Nushell), every successful
system provides a way to feed the output of one operation into the next as
input. The input type and output type are the same (table in, table out), so
operations compose arbitrarily.

**3. Grouping is a context, not a separate verb set.**
No successful system has separate verbs for grouped-vs-ungrouped operations.
`group_by()` changes what subsequent verbs mean without changing their names.
The user writes `summarize(avg = mean(amount))` whether or not `group_by()`
was called before. SQL's `GROUP BY` changes the scope of `SELECT` expressions.
dplyr's `group_by()` changes the behaviour of `summarise()`. Polars' `group_by()`
is followed by `.agg()`. The pattern is identical.

**4. The heavy lifting is in structural expressions, not opaque callbacks.**
SQL's expressions (`salary > 80000 AND department = 'Eng'`) are structural.
Polars' expressions (`pl.col("amount").sum().alias("total")`) are structural.
dplyr's tidy evaluation captures R expressions structurally. Even LINQ's
expression trees capture lambda structure for translation. No successful system
uses opaque host-language callbacks (`lambda row: ...`) as the primary query
mechanism -- pandas' `.apply()` is the cautionary tale.

**5. Lazy/eager is a source property, not a verb property.**
In Polars, a `DataFrame` is eager, a `LazyFrame` is lazy, but the verb API
(`.filter()`, `.select()`, `.group_by()`) is identical. In LINQ, `IEnumerable`
is eager (deferred execution but no optimization), `IQueryable` is lazy with
optimization, but the verb API is identical. The lesson: **laziness is a
property of the data source, not a different set of verbs**.

**6. Schema is tracked and inspectable.**
SQL's catalog, Polars' `collect_schema()`, DuckDB's `DESCRIBE`, dplyr's
`glimpse()` -- every system maintains a column-name + column-type schema and
lets users inspect it. Systems that lose the schema (pandas after certain
operations, base R) create bugs from silent type changes.

**7. Join key explicitness is a safety feature.**
Every system provides a way to specify join keys explicitly. Systems that
guess join keys (dplyr's auto-detect, pandas' index alignment) create subtle
bugs when the guess is wrong. The safe pattern: **explicit `on=` (or `by=`)
is the default; auto-detect is opt-in and warned about in diagnostics**.

### 9.2 Genuine Design Forks -- Where Systems Made Different Tradeoffs

**1. Row-level operations: bare column names vs explicit references.**

| Bare names (dplyr, SQL) | Explicit references (Polars, LINQ) |
|---|---|
| `filter(salary > 80000)` | `filter(pl.col("salary") > 80000)` |
| Magic when it works; confusing when it fails | Verbose but unambiguous; no magic |

This fork divides every system. dplyr's bare names are beloved by interactive
users but create the tidyeval complexity for package authors. Polars' explicit
`pl.col()` is more verbose but zero-magic. SQL's column names are bare within
the query but require string quoting at the language boundary.

**Nomi's fork position:** Use `.col` for column references (visible prefix,
unambiguous). Optionally allow bare names inside dedicated query blocks
(`query: where salary > 80000`), where the query context makes clear that
bare names resolve to columns. This is a deliberate fork toward explicitness
in pipeline context and convenience in query-block context. The lowering is
the same either way.

**2. Projection position: early (SQL-style) vs late (pipeline-style).**

| Early projection (SQL) | Late projection (dplyr, Polars, LINQ) |
|---|---|
| `SELECT name, salary FROM ... WHERE ...` | `... |> where(...) |> select(name, salary)` |
| Projection at the top; must read whole query to understand what columns exist | Projection at the end; columns available at each stage are visible from reading top-to-bottom |

SQL puts `SELECT` first (English reading order), but this means `WHERE` cannot
reference aliases from `SELECT`. Pipeline systems put `select` late (flow
order), which means every preceding verb can reference all upstream columns.
The flow order is strictly more composable. Even SQL CTEs (`WITH`) effectively
adopt flow order by letting users build up transformations step by step.

**Nomi's fork position:** Pipeline order (flow order). `where` before `select`.
`derive` before `summarize`. A `query:` block would follow the same order. This
is consistent with Nomi's explicit stance on flow ordering.

**3. Query language: standalone vs embedded vs integrated.**

| Standalone (SQL) | Embedded (DuckDB, LINQ to SQL) | Integrated (LINQ, Q) |
|---|---|---|
| Separate language with its own parser, types, optimizer | SQL strings in host language, optimized by embedded engine | Query syntax IS host-language syntax |

The "integrated" model (LINQ, Q) eliminates the impedance mismatch entirely
but requires the language to own the query semantics. The "embedded" model
(DuckDB) preserves SQL compatibility at the cost of string boundaries.

**Nomi's fork position:** Integrated. Nomi's collection verbs ARE Nomi syntax.
There is no second language. A `query:` block (future) is Nomi syntax with
different sugar; it lowers to the same Nomi verb calls.

**4. Mutable vs immutable data.**
pandas allows inplace mutation (`df.drop("col", inplace=True)`). dplyr,
Polars, and SQL return new tables. Q tables are mutable for performance in
financial contexts but the functional style is available.

**Nomi's fork position:** Immutable by default. Verbs return new values.
Explicit mutation, if added, is a separate operation.

**5. Index/key handling: implicit vs explicit vs absent.**

| Implicit index (pandas) | Explicit keys (Q) | No separate index (dplyr, Polars) |
|---|---|---|
| Row labels affect alignment, merging, grouping | Keyed tables: key columns are metadata, support lookup | Tables are sequences of rows; keys are just columns |

pandas' implicit index is widely considered its biggest design mistake. Q's
explicit keyed tables are powerful but niche. dplyr/Polars' "no separate index"
approach is the modern consensus.

**Nomi's fork position:** No separate index. Key metadata on columns
(`keyed by id`) for lookup, join, and uniqueness constraints. This is
Polars/Q territory, not pandas territory.

**6. Error model: runtime vs plan-construction time.**
SQL catches schema errors at query compilation (before execution). Polars
catches type errors at plan construction. dplyr catches column-not-found
at runtime (when the expression is evaluated). pandas catches almost
nothing until execution.

**Nomi's fork position:** Catch at plan construction time wherever structural
expressions allow. Schema validation, key existence, type compatibility,
and join cardinality should all be checkable before any data is processed.

**7. Terseness spectrum: APL/Q minimals vs SQL verbosity vs Python readability.**

| Ultra-terse (Q, K) | Moderate (dplyr, Polars) | Verbose (SQL, LINQ lambda syntax) |
|---|---|---|
| `select sum amount by customer_id from orders` | `orders \|> group_by(customer_id) \|> summarize(total=sum(amount))` | `SELECT customer_id, SUM(amount) FROM orders GROUP BY customer_id` |

**Nomi's fork position:** Moderate, leaning concise. `|>` enables compact
pipelines. `_` holes provide conciseness. But the verb names are full
English words, not glyphs or single letters. Terseness at the cost of
guessability is rejected.

### 9.3 The "Verb Vocabulary" Design

Every system converges on approximately these operations:

| Operation | SQL | LINQ | dplyr | Polars | Nushell | Q | Nomi (proposed) |
|---|---|---|---|---|---|---|---|
| Filter rows | `WHERE` | `Where` | `filter` | `filter` | `where` | `where` | `where` |
| Choose columns | `SELECT` | `Select` | `select` | `select` | `select` | `select` | `select` |
| Add columns | (in SELECT) | `Select` | `mutate` | `with_columns` | `update` | `update` | `derive` |
| Aggregate | `GROUP BY` + aggregates | `GroupBy` | `summarise` | `group_by().agg()` | `group-by` + `each` | `select ... by` | `group` + `summarize` |
| Sort | `ORDER BY` | `OrderBy` | `arrange` | `sort` | `sort-by` | `xasc`/`xdesc` | `sort` |
| Join | `JOIN` | `Join` | `*_join()` | `join` | `merge` | `lj`/`ij`/`uj` | `join` |
| Window | `OVER (...)` | (none built-in) | `window_order()` | `rolling()` | (limited) | `wj` | `window` |
| Fold/reduce | (aggregates) | `Aggregate` | `summarise(across())` | (aggregates) | `reduce` | `over` | `fold` |
| Limit | `LIMIT` / `TOP` | `Take` | `slice_head()` | `head()` / `limit()` | `first` / `last` | `#` | `take` |
| Distinct | `DISTINCT` | `Distinct` | `distinct` | `unique` | `uniq` | `distinct` | `distinct` |
| Reshape | `PIVOT` / `UNPIVOT` | (none) | `pivot_wider/longer` | `pivot` / `unpivot` | `pivot` | `xcol`/`xkey` | research-only |
| Inspect plan | `EXPLAIN` | (none) | (none) | `explain()` | `describe` | (none) | `explain` |

**Nomi's starting vocabulary should be:**

```
where      select      derive
group      summarize   join
sort       window      fold
take       distinct    explain
```

This is 11 verbs. They cover the core operations from every system studied.
`pivot`/`unpivot`/`melt`/`nest`/`unnest` are shape operations that belong
in a second shelf, not the core. `map` is a general-collection operation
(distinct from `derive` which is table-specific).

**The verb names were chosen for:**
- `where` over `filter`: matches SQL, Nushell; shorter; unambiguous in
  collection context (Nomi already uses `where` for table predicates, and
  `filter` is also available as a general-collection function).
- `select` over nothing else: used by SQL, LINQ, dplyr, Polars, Nushell, Q.
  This is the most universally agreed-upon verb name in data manipulation.
- `derive` over `mutate`: `mutate` implies mutation (which Nomi verbs do not
  do). `derive` says "compute a new column from existing ones." `with_columns`
  (Polars) is accurate but verbose.
- `group` + `summarize` (two verbs) over `group_by` (one verb) or `group_by()` +
  `.agg()` (method chaining): Two verbs keep the pipeline flat and make the
  group/aggregate phase boundary visible. `group` changes context; `summarize`
  applies in that context.
- `sort` over `order_by` or `arrange`: shorter, well-understood, matches
  Nomi's existing `sort` for collections.
- `join` over `merge`: matches SQL and Polars. `merge` is pandas-specific.
- `window` over `OVER(...)`: a verb, not a clause modifier. Windows should
  compose like other verbs.
- `fold` over `reduce` or `accumulate`: matches Nomi's existing `fold` in
  collection verbs. `reduce` is a special case of `fold` without an explicit
  initial accumulator.
- `take` over `limit` or `head`: works for both "take first N" and "take
  last N." `limit` is SQL-specific; `head`/`tail` are positional but not
  extensible to "take while" or "take from position."
- `explain` over nothing else: used by SQL, DuckDB, Polars; the universal
  word for "show me what this query will do."

### 9.4 Query Syntax vs Method Chain: The LINQ Lesson

The LINQ lesson is decisive for Nomi's design: **query syntax and method
chains can coexist if both lower to the same verb vocabulary**. There is no
need to choose one. The verb vocabulary is the interface; pipeline and query-
block are two surface syntaxes.

```
                    ┌──────────────────┐
                    │   Verb Vocabulary │  ← the interface (where, select,
                    │   (standard set)  │     derive, group, join, ...)
                    └────────┬─────────┘
                             │
              ┌──────────────┴──────────────┐
              │                             │
    ┌─────────┴─────────┐       ┌──────────┴──────────┐
    │ Pipeline Syntax   │       │ Query-Block Syntax  │  ← surface spellings
    │                   │       │                     │
    │ data              │       │ query data:         │
    │ |> where(...)     │       │   where ...         │
    │ |> group(...)     │  ==   │   group by ...      │  ← same plan produced
    │ |> summarize(...) │       │   summarize: ...    │
    └───────────────────┘       └─────────────────────┘
```

Nomi's implementation path:

1. **Phase 1 (current):** Implement the verb vocabulary as standard library
   functions callable through `|>`. This gives immediate pipeline composition.
   Users write `data |> where(.status == "paid") |> select(.name, .amount)`.

2. **Phase 2 (future):** When the verb vocabulary is stable, add `query:` block
   syntax as sugar that lowers to the same verb calls. The lowering is
   specified, stable, and inspectable through `explain` and tooling.

3. **Phase 3 (future-future):** Allow backends (in-memory interpreter,
   DuckDB-derived engine, remote SQL database) to implement the verb
   vocabulary. The user writes the same pipeline; the backend determines
   execution.

The phase ordering matters: **vocabulary first, syntax second, backends
third**. This prevents the "syntax is frozen before we understand the
semantics" trap and the "backend limits constrain the vocabulary" trap.

### 9.5 Lazy vs Eager Evaluation

The synthesis across all systems:

| System | Lazy trigger | Eager trigger | Plan inspection |
|---|---|---|---|
| SQL | Query is always a plan; execution is explicit (run) or implicit (fetch) | `SELECT ...` is a statement; some systems allow `EXPLAIN` | `EXPLAIN` |
| LINQ | `IEnumerable.Where()` returns iterator; `IQueryable.Where()` builds expression tree | `ToList()`, `ToArray()`, `First()`, `Count()`, `foreach` | No built-in (third-party) |
| dplyr | `filter()` on a `tbl_lazy` builds a query | `filter()` on a `data.frame/tibble` executes immediately; `collect()` triggers remote execution | `show_query()` |
| Polars | `df.lazy().filter(...)` builds `LazyFrame` | `df.filter(...)` on eager `DataFrame`; `.collect()` triggers lazy execution | `explain()` |
| DuckDB | (always a plan; SQL execution is lazy within the plan's lifetime) | (result materialization is the execution trigger) | `EXPLAIN` |
| Nushell | None (always eager) | Every pipeline step materializes | `describe` (schema only, not plan) |
| pandas | None (always eager) | Every method call executes immediately | None built-in |
| Q | `select ... from t` executes immediately | Kdb+ has deferred/lazy views but they are specialized | `parse` for functional form |

The consensus pattern: **laziness is a property of the data source**. If you
start from a lazy source (database connection, file path, `LazyFrame`), the
pipeline builds a plan and nothing executes until you request the result. If
you start from an eager source (in-memory DataFrame, list), each verb executes
immediately.

Nomi should follow this pattern exactly:

```nomi
# Eager: orders is an in-memory Table, each verb executes immediately
orders |> where(.status == "paid") |> select(.name, .amount)

# Lazy: orders is a lazy reference (file path, database query), builds a plan
orders_lazy |> where(.status == "paid") |> select(.name, .amount)
# ... nothing executed yet
result = collect(orders_lazy)  # now plan runs

# Inspect the plan before running
explain(orders_lazy)
```

The verb vocabulary is identical. `explain` works on lazy sources. `collect`
triggers execution. This is the Polars model, and it is the right one.

There is one important exception: **aggregation verbs on eager sources still
need to execute immediately** (they need the data to compute the result). This
is intuitive -- you can't `summarize` without seeing the data. But a `where`
or `select` on a lazy source should remain lazy. The distinction is: verbs
that reduce cardinality (summarize, count, fold without a lazy accumulator)
must execute; verbs that preserve structure (where, select, derive, sort,
window) can remain lazy.

### 9.6 The `explain` Function

Every system provides a way to inspect what a query will do. Nomi's `explain`
should learn from all of them:

**What `explain` should show:**

1. **Logical plan** -- the verb chain in execution order, with schema at each
   stage. This is what the user wrote, normalized.

2. **Optimized plan** -- what the optimizer changed. Predicate pushdown, column
   pruning, filter fusion, join reordering. Show what was moved or eliminated
   and why.

3. **Schema at each stage** -- column names, types, nullability. This lets users
   verify that `derive` produced the expected column type and that `summarize`
   didn't drop a column they needed.

4. **Backend information** -- which backend will execute this, what capabilities
   it has, and whether any stage cannot be executed by the chosen backend.

5. **After execution** -- actual row counts, time per stage, cardinality
   estimates vs actuals. (Like DuckDB's `EXPLAIN ANALYZE`.)

**Stages of `explain` output (example):**

```
Pipeline: 5 stages
Backend: in-memory (eager mode)

Stage 1: Scan orders
  Schema: id:Int, customer_id:Str, status:Str, amount:Dec, created_at:DateTime
  Source: local variable `orders`

Stage 2: where
  Predicate: .status == "paid"
  Schema: (unchanged — same 5 columns)
  Optimizer note: no index on `status`; full scan
  After execution: 1,247 rows matched (from 5,000 input)

Stage 3: group by .customer_id
  Key: customer_id:Str
  Schema: groups keyed by customer_id, each group has columns [id, status, amount, created_at]
  After execution: 342 groups

Stage 4: summarize
  Aggregates: total = sum(.amount):Dec, count = count():Int
  Schema: customer_id:Str, total:Dec, count:Int
  Optimizer note: sum/amount and count are separable; no repartitioning needed
  After execution: 342 rows

Stage 5: sort by total desc
  Order: total DESC
  Schema: (unchanged)
  After execution: sorted (342 rows)
```

This is an ambitious `explain` output, but it is what production data
systems need. Nomi should ship a basic version (stages + schema) in the
first collection-verb release and grow toward the full version.

**Anti-pattern to avoid:** `explain` that shows internal implementation
details (line numbers in the optimizer pass, internal variable names,
generated code that doesn't relate back to the user's verbs). The user
wrote verbs; `explain` should show verbs.

### 9.7 Column Name Scoping -- How Systems Handle Column References

The hardest design problem in collection/table systems is "what does this
name refer to?" These are the approaches:

**Approach A: Bare names resolve to columns (SQL, dplyr interactive, Nushell)**

```sql
WHERE salary > 80000   -- 'salary' is a column, no prefix needed
```

Pro: Readable. Con: Ambiguous when a variable in the enclosing scope has
the same name. dplyr's tidyeval complexity exists to resolve this ambiguity.

**Approach B: Explicit column references (Polars, LINQ lambdas)**

```python
filter(pl.col("salary") > 80000)    # explicit column reference
employees.Where(e => e.Salary > 80000)  # lambda parameter names the row
```

Pro: Unambiguous. Column names and variable names never collide. Con: Verbose
for simple queries. Every column reference requires a `pl.col()` wrapper.

**Approach C: Subject-dot notation (.col)**

```nomi
orders |> where(.amount > 100) |> select(.name, .total)
```

The `.` prefix means "this is a column of the current row." Unqualified
names refer to enclosing-scope variables. This is Kotlin's approach with
`it.` and Swift's with `$0.`.

Pro: Unambiguous; `.` is a visible column marker; scoping is lexical.
Con: Slightly more characters than bare names. Long chains of `.col.subcol`
can be visually noisy (but this is rare: column access is usually one level).

**Approach D: Context-dependent resolution (dplyr with tidyeval)**

```r
filter(data, salary > 80000)  # 'salary' could be a column OR a variable
```

Pro: Clean in interactive use. Con: The "could be either" ambiguity requires
complex resolution rules and creates the quoted/unquoted problem.

**Nomi's approach:** Hybrid, with explicit defaults.

1. **In pipeline context** (`data |> where(PREDICATE)`): Use subject-dot
   notation (`.col`). The `.` prefix is required. `where(.amount > 100)`
   is unambiguous: `.amount` is a column, `threshold` is a variable.

2. **In query-block context** (future, `query data:`): Allow bare column
   names by default. Inside a query block, the context is clear: you are
   operating on columns of the source table. Bare names resolve to columns
   first. Access enclosing-scope variables with `^name` or `outer.name`.

3. **Column sub-access:** `.col.subfield` for nested struct fields.
   `.col[index]` for list/map access. This mirrors Polars' `.str`, `.list`,
   `.struct` namespaces but as unified dot-access syntax.

4. **Programmatic column reference:** When the column name is stored in a
   variable, use `col(var_name)` function (like Polars' `pl.col(var)`).
   This escapes the `.col` literal syntax for computed column names.

This design gives: explicitness by default (pipeline), convenience when
appropriate (query block), and a programmatic escape hatch.

### 9.8 Anti-Patterns -- Table/Flow Mistakes That Consistently Hurt Usability

These are the systemic mistakes that appear across multiple systems:

**1. Execution order different from written order.**
SQL's `SELECT ... FROM ... WHERE ... GROUP BY ... HAVING ... ORDER BY` reads
in a different order than it executes. This has been the #1 usability complaint
for 50 years. Every system designed after SQL puts source first and projection
last.

**2. Too many ways to do the same thing.**
pandas' 5+ ways to access columns, filter rows, and aggregate. dplyr's
(at one point) 21 `_all`/`_at`/`_if` variants. The correct number is one
canonical spelling per operation, with a visible desugaring if convenience
spellings exist.

**3. Implicit index or row-label system.**
pandas' index is a separate axis from columns, with its own alignment
semantics. R's `rownames()` are metadata that affect subsetting. The lesson:
keys should be columns with metadata, not a separate dimension.

**4. Mutating operations indistinguishable from non-mutating.**
pandas' `inplace=True` flag. R's `:=` (data.table) vs `<-` (base). The
lesson: mutation should be a visibly different operation. Nomi treats verbs
as returning new values; mutation, if added, is explicit.

**5. Opaque callbacks as the primary query mechanism.**
pandas' `.apply(lambda row: ...)` is the worst-performing, least-optimizable,
hardest-to-explain path, yet it is often the first one users find. The
lesson: structural expressions should be the primary API. Callbacks are an
escape hatch, not a first resort.

**6. Stringly-typed query embedding.**
SQL strings in Python/Java/Go. No syntax highlighting, no compile-time
column-checking, injection risk. The lesson: the query API should be a
value-level interface in the language, not a string API.

**7. Schema loss through operations.**
pandas lets `groupby` return a `DataFrameGroupBy` object (not a DataFrame).
`melt`/`pivot` reshape but don't preserve type metadata. The lesson: schema
should be tracked through every operation. Every verb takes a `Table` and
returns a `Table` (or a `GroupedTable` that is a subtype of `Table`).

**8. The "default guess" that changes silently.**
dplyr's auto-detect join keys change when a column is added to either table.
Polars' `join(..., on=None)` raises an error rather than guessing. The lesson:
guesses that change silently are worse than requiring explicit specification.
Safety over convenience at the join boundary.

**9. Error messages in implementation vocabulary.**
LINQ error messages expose transparent identifiers and `SelectMany` calls.
Polars early errors referenced Rust internals. The lesson: error messages
must use the user's vocabulary (verb names, column names, schema) and provide
actionable suggestions.

**10. Two-phase semantics without visible phase boundaries.**
SQL's WHERE vs HAVING confuse because the phase distinction (row-level vs
group-level) is not visible in the keyword name. dplyr's `filter()` works
the same before and after `group_by()` -- the phase is determined by context.
The lesson: phase boundaries should be visible (e.g., `summarize` is always
group-level; `where` is always row-level; the `group` verb is the visible
phase transition).

---

## 10. Nomi Adopt / Refuse / Adapt Table

For each design pattern, a concrete recommendation mapped to Nomi's existing
verb vocabulary and design stance.

| # | Pattern | System(s) | Verdict | Nomi Recommendation |
|---|---|---|---|---|
| 1 | SELECT/FROM/WHERE as the fundamental clause triad | SQL | **Adapt** | Adopt the relational operations (project, filter, aggregate) but use flow order: source first, filter second, project last. Nomi: `data \|> where(...) \|> select(...)` |
| 2 | Query syntax lowers to method calls | LINQ | **Adopt** | This is the master architectural insight. Nomi's `query:` blocks (future) MUST lower to the same verb calls as `\|>` pipelines. Both produce an identical `QueryPlan`. |
| 3 | `IQueryable<T>` with expression-tree capture | LINQ | **Adapt** | Nomi verbs should take structural expressions (not opaque callbacks). The expression AST is the `IQueryable` equivalent: backends can translate it. |
| 4 | Extension methods as the operator delivery mechanism | LINQ | **Refuse** | Nomi operators are standard library functions callable through `\|>`. No extension-method mechanism needed. `\|>` is the universal composition operator. |
| 5 | The two-syntax split (query expressions vs method chains) | LINQ | **Adapt** | Accept that two surface spellings exist, but enforce that they lower to the same plan. Tooling must show the equivalence. One must be canonical (pipeline) and the other sugar (query block). |
| 6 | Bare column names in query context | dplyr, SQL | **Adapt** | Adopt bare names only inside dedicated query blocks (`query: where salary > 80000`). In pipeline context, require `.col` prefix. This prevents the tidyeval complexity. |
| 7 | `group_by()` as context, not separate verb set | dplyr, Polars, SQL | **Adopt** | Nomi's `group` verb adds grouping metadata. Subsequent verbs (`summarize`, `window`, `derive`) automatically respect the grouping. No separate grouped-verb vocabulary. |
| 8 | Pipe operator as composition glue | dplyr, Nushell | **Adopt** | Already adopted: Nomi's `\|>`. Works for collection verbs and general functions. |
| 9 | Non-standard evaluation / tidy eval | dplyr | **Refuse** | Bare column names must resolve unambiguously. No `{{ }}`, no quosures, no quoted/unquoted ambiguity. The `.col` / bare-name boundary is syntactic, not evaluative. |
| 10 | `across()` for column-wise operations | dplyr | **Adapt** | One general mechanism for "apply this to multiple columns" rather than per-verb scoped variants. Nomi: `select(cols("amount", "tax") \|> sum)` or similar. |
| 11 | Expressions as first-class composable values | Polars | **Adopt** | This is critical. Verb arguments are structural expressions that can be stored, composed, and retargeted. `where(.amount > 100)` captures an expression, not a callback. |
| 12 | Lazy/eager with identical API | Polars | **Adopt** | Lazy source → build plan. Eager source → execute immediately. Same verb API either way. `collect()` triggers lazy execution. |
| 13 | `explain()` for query plan visualization | Polars, DuckDB, SQL | **Adopt** | Ship `explain` from day one of the collection-verb system. Show stages, schema at each stage, optimizer rewrites, backend info. This is not optional infrastructure. |
| 14 | Streaming/out-of-core execution | Polars, DuckDB | **Adapt** | Design verbs to be batch-compatible from the start. `map`, `filter`, `derive` should work on batches. `sort` and `group` may require materialization but should degrade gracefully. |
| 15 | Schema maintained and validated across all operations | Polars, DuckDB | **Adopt** | Every verb preserves and augments the schema. Schema errors caught at plan-construction time. No silent column loss or type change. |
| 16 | In-process embedding with zero-copy host-language access | DuckDB | **Adopt** | Nomi's collection verbs operate on Nomi-native `Table` values in-process. No serialization boundary. No separate database process. Arrow-native memory layout. |
| 17 | Friendly SQL features (GROUP BY ALL, EXCLUDE, direct files) | DuckDB | **Adapt** | Nomi should be friendly by design: no column repetition ceremony, easy column exclusion, direct file reading as a verb. |
| 18 | EXPLAIN ANALYZE (actual rows/timing per stage) | DuckDB | **Adapt** | `explain` returns a plan. `explain` after execution (or `collect(plan, diagnose=True)`) adds actual row counts and timings. |
| 19 | Typed tables as universal interchange (shell pipelines) | Nushell | **Adopt** | Nomi tables are the universal interchange format for Nomi collection operations. Like Nushell, every verb takes a table and returns a table. |
| 20 | `describe` inline in the pipeline | Nushell | **Adapt** | Allow `explain` as an inline verb: `data \|> where(...) \|> explain \|> select(...)` shows the schema at that point without interrupting the pipeline. |
| 21 | No separate index | pandas (negative), Polars | **Adopt** | Keys as column metadata. No separate index axis. No index-alignment semantics. No `SettingWithCopyWarning`. |
| 22 | One way per verb | pandas (negative), dplyr | **Adopt** | One canonical verb per operation. No `.loc`/`.iloc`/`[]`/`.query()` multiplicity. If convenience aliases exist, they must desugar to the canonical verb. |
| 23 | No `inplace=True` / mutation flag | pandas (negative) | **Adopt** | Verbs return new values. Mutation is explicit and separate (assignment or `mutate` keyword). No boolean flag that changes semantics. |
| 24 | Tables are ordinary language values | Q, K | **Adopt** | Nomi `Table` is a first-class value. Table literals, query results, file loads, and API responses produce the same `Table` type. No database-vs-dataframe distinction. |
| 25 | Columnar (struct-of-arrays) memory layout | Q, Polars, DuckDB, Arrow | **Adopt** | Nomi tables use columnar layout (Arrow-native or similar). Row access is available but column operations are the fast path. |
| 26 | Query syntax that lowers to functional form | Q, LINQ | **Adopt** | Already adopted at the architectural level. The lowering is stable, specified, and inspectable. |
| 27 | Keys as table metadata, not separate structures | Q, Polars | **Adopt** | `keyed by customer_id` adds key metadata. Used for joins, uniqueness checking, and lookup. No separate key table/index. |
| 28 | Extreme terseness | Q, K, APL | **Refuse** (for now) | Readable English words for verbs. Terseness via `\|>` and `_` holes. A dense symbolic layer (research-only) could be a future opt-in for power users, never the default. |
| 29 | Deferred execution with materialization triggers | LINQ | **Adopt** | Lazy sources build plans; eager sources execute immediately. `collect()` is the explicit materialization trigger. Iteration over results also triggers execution. |
| 30 | The `let` clause for intermediate bindings | LINQ | **Adapt** | Nomi's `derive` covers the "compute a new column" case. For named intermediate values that aren't columns, `where:` clauses serve the same purpose. In query blocks, `let name = expr` could desugar to `derive name = expr`. |

---

## 11. Implementation Priorities for Nomi

Based on this analysis, the recommended implementation order:

### Phase 1: Core Verb Vocabulary (Library-First)
- `where`, `select`, `derive`, `sort`, `take`, `distinct`
- Operate on in-memory `Table` values (eager execution)
- Each verb is a standard library function callable through `|>`
- Structural expressions as verb arguments (not opaque callbacks)
- Schema tracked through all operations

### Phase 2: Grouping and Aggregation
- `group` (adds grouping metadata)
- `summarize` (aggregates within group context)
- `join` (inner, left, outer, semi, anti; explicit keys; cardinality validation)
- `fold` (explicit accumulator, works on grouped and ungrouped tables)

### Phase 3: Lazy Evaluation and explain()
- Lazy table source (file path, database reference)
- Identical verb API; lazy source builds plan instead of executing
- `collect()` to trigger execution
- `explain` to inspect plan (stages, schema, optimizer rewrites)

### Phase 4: Windows and Advanced Operations
- `window` (partition + order + frame + compute)
- Window functions (lag, lead, rank, row_number, rolling)
- `pivot`, `unpivot` (shape operations)

### Phase 5: Query Blocks and Backend Retargeting
- `query:` block syntax as sugar over verb calls
- Backend interface (in-memory, embedded engine, external database)
- `explain` with backend-specific optimizer output
- `explain` with post-execution row counts and timings

This ordering respects the design rule from Nomi's own docs: **vocabulary first,
syntax second, backends third**. Each phase adds capability without requiring
rewriting the previous phase.

---

## 12. Sources

### Primary Sources (Papers and Documentation)
- Chamberlin, D. and Boyce, R. "SEQUEL: A Structured English Query Language" (1974). ACM SIGFIDET.
- Codd, E.F. "A Relational Model of Data for Large Shared Data Banks" (1970). CACM 13(6).
- Meijer, E. et al. "LINQ: Reconciling Objects, Relations, and XML in the .NET Framework" (2006). Microsoft.
- Wickham, H. "dplyr: A Grammar of Data Manipulation" (2014). R package.
- Raasveldt, M. and Muhleisen, H. "DuckDB: an Embeddable Analytical Database" (2019). SIGMOD.
- McKinney, W. "pandas: a Foundational Python Library for Data Analysis and Statistics" (2011).
- Whitney, A. "K" and "Q" programming languages. KX Systems.
- Vink, R. "Polars: Lightning-fast DataFrame library" (2020).

### System Documentation
- [SQL logical processing order (Microsoft)](https://learn.microsoft.com/en-us/sql/t-sql/queries/select-transact-sql?view=sql-server-ver16#logical-processing-order-of-the-select-statement)
- [LINQ query expression translation (C# spec)](https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/language-specification/expressions#12819-query-expressions)
- [IQueryable and expression trees](https://learn.microsoft.com/en-us/dotnet/csharp/advanced-topics/expression-trees/)
- [dplyr documentation](https://dplyr.tidyverse.org/)
- [Tidy evaluation](https://rlang.r-lib.org/reference/topic-data-mask.html)
- [dplyr 1.0: across()](https://www.tidyverse.org/blog/2020/04/dplyr-1-0-0-colwise/)
- [Polars expressions and contexts](https://docs.pola.rs/user-guide/concepts/expressions-and-contexts/)
- [Polars lazy API](https://docs.pola.rs/user-guide/concepts/lazy-api/)
- [Polars optimizer](https://docs.pola.rs/user-guide/lazy/optimizations/)
- [DuckDB Friendly SQL](https://duckdb.org/docs/stable/sql/dialect/friendly_sql)
- [DuckDB query execution](https://duckdb.org/docs/stable/internals/vector_execution)
- [DuckDB EXPLAIN](https://duckdb.org/docs/stable/guides/meta/explain)
- [Nushell documentation](https://www.nushell.sh/book/)
- [Nushell data model](https://www.nushell.sh/book/data_types.html)
- [pandas documentation](https://pandas.pydata.org/docs/)
- [pandas API design principles](https://pandas.pydata.org/docs/development/design.html)
- [Q for Mortals](https://code.kx.com/q4m3/)
- [qSQL queries](https://code.kx.com/q/basics/qsql/)
- [Functional qSQL](https://code.kx.com/q/basics/funsql/)

### Nomi Project Documents (for grounding)
- `docs/features/structured_collections_query_language.md` -- Nomi query design candidates
- `docs/convenience/flow_and_collections.md` -- Nomi flow normal form
- `docs/convenience/design_lessons_and_integration.md` -- systemic patterns and integration rules
- `docs/language/language_design_dimensions.md` -- design-space framework
- `prototype/syntax/features.py` -- feature manifest registry
