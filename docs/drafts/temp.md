Nomi: A Language Specification
Version 0.2.0 — Core Language Design

Table of Contents
Philosophy

Design Principles

Syntax Overview

Lexical Structure

Values and Types

Bindings and Naming

Constraints

Functions

Data Types

Patterns and Matching

Blocks and Yield

Pipelines

Modules and Imports

Error Handling

Special Forms Reference

Complete Grammar

A Complete Example

1. Philosophy
A programming language is a medium for thought. Before it is a tool for instructing machines, it is a tool for thinking clearly about problems and communicating that thinking to others. The languages that endure succeed because they have a coherent center. They are about something.

Nomi makes this bet:

A language should be small in its core concepts and large in what you can express by composing them. Every feature should pull its weight across multiple contexts. The programmer should never have to learn a special sub-language for a common task.

This leads to a design discipline. We do not add features because another language has them or because they address a single use case elegantly. We add primitives that combine. The test of a feature is not "does this make X easier?" but "does this make X, Y, and Z easier in the same way?"

2. Design Principles
2.1 One Mechanism, Many Contexts
Every semantic mechanism in Nomi should work across all appropriate contexts. If we have a constraint system, it works in variable bindings, function parameters, data fields, pattern matching, and block parameters—identically. If we have a pattern language, it works in match, assignment, and block bindings—identically.

2.2 Explicit Over Implicit
Things that affect program behavior should be visible. There is no implicit type coercion in conditionals, no silent null propagation, no magic method resolution. When a value crosses a boundary, that crossing is explicit.

2.3 Explainable Always
Every error should be explainable in terms the programmer can act on. A constraint failure should say what constraint failed, what value was provided, and where the binding occurred. Diagnostics are not decoration; they are a first-class design concern.

2.4 Grow Gracefully
The language should work well for a 20-line script and for a 20,000-line application. The mechanisms that make a script clear (simple bindings, readable pipelines, straightforward error handling) should be the same mechanisms that scale to larger programs.

2.5 Reduce to the Core
Every "advanced" feature should be understandable as a combination of core primitives. Blocks are functions with attached closures. Pipelines are function application in a different order. Data types with members are ordinary functions with a calling convention.

3. Syntax Overview
Nomi's syntax draws primarily from Python's tradition of significant whitespace and readable keywords, with influences from ML-style data declarations, Ruby-style blocks, and Unix-style pipelines.

Key syntactic decisions:

Significant indentation for block structure (like Python, Haskell)

func for named function definitions

data for type definitions (from ML tradition)

match/case for pattern matching (from ML/Scala tradition)

|> for pipelines (from Elixir/OCaml tradition)

Colon-and-indent blocks for function bodies, conditionals, and loops

Arrow functions for expression-level lambdas: (x) => x + 1

4. Lexical Structure
4.1 Source Text
A Nomi source file is a sequence of Unicode characters encoded in UTF-8.

4.2 Lines and Indentation
Nomi uses significant indentation to delimit blocks. A block is introduced by a line ending in a colon. The block consists of the following lines indented more than the introducing line. The block ends when indentation returns to the level of the introducing line or less.

func greet(name: str) -> str: # colon introduces block
greeting = "Hello, " # indented: part of block
return greeting + name # indented: part of block

farewell = "Goodbye" # not indented: block ended

Within a block, all lines must use consistent indentation. The recommended indentation is 4 spaces. Tabs and spaces must not be mixed. Expressions within parentheses, brackets, or braces may span multiple lines without explicit continuation.

4.3 Comments
Line comments begin with # and extend to the end of the line. There are no block comments in the core language. Multi-line comments use repeated line comments.

This is a comment
x = 1 # so is this

Documentation comments are ordinary comments that immediately precede a declaration with no blank line between them.

4.4 Identifiers
Identifiers consist of a letter or underscore, followed by zero or more letters, digits, or underscores.

By convention:

snake_case for values, functions, modules, and fields

CamelCase for data types and variant constructors

_leading_underscore for private or internal names

_ alone as the wildcard pattern

4.5 Keywords
The following are reserved and may not be used as identifiers:

and as block break case const
continue data decode each elif else
examples export false for from func
global if import in is let
match module none not on or
quote raise return rewrite self then
true try use when while with
world yield

4.6 Operators
/ // % **
== != < > <= >=
= |> => -> | &
. , : ; @ _

4.7 Literals
Numeric literals:

42 # integer
3.14 # float
1.5e-3 # scientific notation
0xFF # hexadecimal
0o777 # octal
0b1010 # binary
1_000_000 # with separators

String literals:

"hello"
'hello'
"it's a string"
"multi\nline"
r"raw\string"
"""
multiline
string
"""

Boolean literals:

true
false

Absence literal:

none

5. Values and Types
5.1 Value Categories
Every expression evaluates to a value or raises an error.

Category	Description	Examples
Numbers	integers, floating-point	42, 3.14, 0xFF
Booleans	truth values	true, false
Absence	intentional nothing	none
Strings	Unicode text	"hello", 'world'
Tuples	fixed-length sequences	(1, 2, 3), ()
Lists	variable-length sequences	[1, 2, 3], []
Dictionaries	key-value mappings	{"a": 1, "b": 2}
Functions	callable values	(x) => x + 1
Data values	instances of data types	User(name="Ada")
5.2 Types
Every value has a type. A type is, operationally, a predicate: it answers the question "does this value belong to this category?" Type annotations are checked at runtime by default. Static checking is optional and additive.

Built-in types: int, float, str, bool, list, dict, tuple, func, type.

5.3 Truth
Conditions in if, while, and guard expressions require boolean values. There is no implicit truthiness. if items: is an error; write if len(items) > 0: or if items.is_empty():.

5.4 Equality
Equality (==) is structural for built-in types and for data types. Two values are equal if they represent the same information. Identity (is) tests whether two references point to the same object.

6. Bindings and Naming
6.1 Basic Binding
name = value

This binds name to value in the current scope. The name is available from this point to the end of the scope.

6.2 Annotated Binding
name: type = value
name: type, constraint = value
name: type, constraint else "message" = value

The annotation part (: followed by one or more constraints separated by commas) is checked at binding time. If any constraint fails, the binding is not created, and a BindingError is raised.

6.3 Binding Semantics
Evaluate the right side once

Tentatively bind left-side names to the value

Check constraints left to right in the tentative environment

If all pass, commit the binding

If any fail, raise BindingError with structured context

6.4 Rebinding
x = 1
x = 2 # rebinds x; old constraints still apply if present
x: str = "hi" # rebinds x with new constraint set

6.5 Constants
const pi = 3.14159
const max_users: int = 1000

Rebinding a const is an error.

6.6 Scope
Scopes are created by modules, functions, blocks, match cases, and comprehensions. Names are resolved lexically from innermost to outermost scope. Inner scopes may shadow outer bindings (with a warning).

7. Constraints
7.1 Constraint Forms
Constraints are executable predicates on values. They are used wherever binding occurs.

Type constraint
x: int

Predicate constraint
x >= 0

Combined
x: int, x >= 0, x < 150

With custom message
x: int, x >= 0 else "must not be negative"

Parameterized type
items: list[str]

Custom constraint function
email: str, contains(email, "@")

7.2 Where Constraints Work
Variable bindings: x: int = 5

Function parameters: func f(x: int, x >= 0): ...

Data fields: age: int, age >= 0

Pattern variables: case x: int, x > 0: ...

Block parameters: -> user: User, user.active: ...

7.3 Constraint Failure
A BindingError is raised with structured context:

BindingError: age failed constraint age >= 13
value: 12
constraint: age >= 13
binding: parameter age in signup(raw_age=12)
source: line 42, column 15

8. Functions
8.1 Named Functions
func name(params) -> ReturnType:
body

Example:

func add(x: int, y: int) -> int:
return x + y

func greet(name: str, greeting: str = "Hello") -> str:
return greeting + ", " + name + "!"

8.2 Parameters
Parameters are bindings and use the same constraint syntax:

func signup(
email: str, contains(email, "@"),
age: int, age >= 13,
plan: Plan = Plan.free
) -> User:
return User(email=email, age=age, plan=plan)

Required parameters have no default. Optional parameters specify a default after =. Defaults are evaluated at call time. Constraints are checked at each call.

8.3 Arrow Functions
(x) => x + 1
(x, y) => x + y
() => get_time()

Arrow functions are expressions, ideal for short transformations:

users.map((u) => u.name).sort()

8.4 Calling Functions
result = add(1, 2)
user = signup(email="a@b.com", age=25)

Arguments are evaluated left to right. Both positional and keyword arguments are supported. Keyword arguments must follow positional arguments.

8.5 Return Values
Functions return via return expr. If control reaches the end without a return, the function returns none.

8.6 Closures
Functions capture their lexical environment:

func make_adder(n: int) -> func:
return (x: int) => x + n

9. Data Types
9.1 Product Types (Records)
data Point:
x: float
y: float

data User:
name: str
email: str, contains(email, "@")
age: int, age >= 0
plan: Plan = Plan.free

This creates: a constructor, field accessors, structural equality, a string representation, and a pattern form for use in match. Fields are validated using the same constraint system used in bindings and function parameters.

9.2 Sum Types (Variants)
data Option[T]:
Some(value: T)
None

data Result[T, E]:
Ok(value: T)
Err(error: E)

data Shape:
Circle(radius: float)
Rectangle(width: float, height: float)
Point(x: float, y: float)

Sum types express alternatives. Each variant can carry different data.

9.3 Constructing Values
user = User(name="Ada", email="ada@example.com", age=36)
shape = Circle(radius=5.0)
result = Ok(user)

9.4 Decoding External Data
Domain types don't silently absorb external data. The boundary is explicit:

raw = json.parse(request.body)
user = User.decode(raw) # validates and constructs

decode checks that all required fields are present, rejects unknown fields, applies defaults, validates constraints, and returns the constructed value—or a DecodeError with field-level detail on what went wrong.

9.5 Member Functions
Functions closely related to a data type may be defined within it:

data User:
name: str
email: str

func display_name(self) -> str:
return self.name

user.display_name() is syntactic sugar for User.display_name(user). There is no inheritance or dynamic dispatch.

10. Patterns and Matching
10.1 Pattern Forms
Patterns describe the shape of a value and bind names to its parts.

_ # wildcard: matches anything, binds nothing
x # variable: matches anything, binds to x
x: int # typed variable: matches if x is int
x: int, x > 0 # constrained variable
42 # literal: matches exactly 42
(x, y) # tuple pattern: matches 2-tuple
[first, *rest] # list pattern: matches non-empty list
{"name": n} # dict pattern: matches dict with key "name"
Ok(value) # constructor pattern: matches Ok variant
Circle(radius=r) # constructor with field binding
Ok(x) | Err(x) # or-pattern: matches either variant

10.2 Match Expression
match value:
case pattern1:
body1
case pattern2 if guard:
body2
else:
default_body

Cases are tried in order. For each case, the pattern is tested. If it matches, variables are bound, constraints are checked, and the guard (if any) is evaluated. If all pass, the body runs. If not, the next case is tried.

match is an expression, so it produces a value:

description = match number:
case 0:
"zero"
case 1:
"one"
case n if n > 1:
"many"
else:
"unknown"

10.3 Destructuring Assignment
Patterns also work in assignment:

(x, y) = point
[first, *rest] = items
Ok(user) = result

11. Blocks and Yield
11.1 Block Syntax
A block is caller-side code attached to a function call:

callee(args) -> params:
body

Simple block with no parameters:

retry(3, on=NetworkError):
send(request)

With parameters:

using(open("file.txt")) -> file:
content = file.read()
process(content)

With typed, constrained parameters:

each(users) -> user: User, user.active:
send(user.email)

11.2 Writing Block-Accepting Functions
The callee uses yield to invoke the block:

func each(items: list):
for item in items:
yield item

func using(resource):
try:
yield resource
finally:
resource.close()

func retry(times: int, on: type = Exception):
for attempt in range(times):
try:
yield attempt
return
except on:
if attempt == times - 1:
raise

11.3 Block Semantics
A block expression desugars to an ordinary function call:

callee(a, b) -> p:
body

becomes:

callee(a, b, block=(p) => body)

The callee invokes the block by calling yield(value). The block's return value becomes the result of the yield expression in the callee.

12. Pipelines
12.1 Pipeline Syntax
Pipelines express sequential transformations:

result = data |> step1 |> step2 |> step3

This is equivalent to step3(step2(step1(data))).

12.2 Placeholder Syntax
The placeholder _ represents the value flowing through the pipeline:

names = users |> map(.name) |> where(.starts_with("A")) |> sort

12.3 Reduction Rules
x |> f -> f(x)
x |> f(a) -> f(x, a)
x |> f(a, _) -> f(a, x)

13. Modules and Imports
13.1 Module Structure
A Nomi file is a module:

module app.users

import app.database as db

data User:
name: str
email: str

export User, load, create

func load(id: int) -> User:
...

func create(data: CreateUser) -> User:
...

func _validate(email: str) -> bool:
... # private (starts with _)

13.2 Import Forms
import app.users # qualified: users.load(1)
import app.users as u # aliased: u.load(1)
from app.users import User, load # direct: User, load(1)

13.3 Exports
By default, names starting with _ are private. Everything else is public. An explicit export list overrides this.

14. Error Handling
14.1 Expected Failures
Model expected failures as data using Option or Result:

func find_user(id: int) -> Option[User]:
...

match find_user(42):
case Some(user):
print(user.name)
case None:
print("not found")

14.2 Unexpected Failures
Use exceptions for unexpected failures:

try:
user = load_user(id)
except NotFound as e:
log("not found: " + e.message)
except DatabaseError:
log("database error")
raise # re-raise
finally:
conn.close()

14.3 The Heuristic
If the caller can reasonably handle the failure → use a Result/Option type

If the failure indicates a bug or system problem → use exceptions

15. Special Forms Reference
These are Nomi's privileged syntactic forms. Everything else is either a library function or syntactic sugar that reduces to these forms.

Form	Purpose
name = value	Binding
name: constraint = value	Annotated binding
const name = value	Constant binding
func name(params) -> T: body	Named function
(params) => expr	Arrow function
return expr	Return from function
data Name: fields	Product type
data Name: Variant1 | Variant2	Sum type
match value: case pat: body	Pattern matching
if cond: body elif cond: body else: body	Conditional
for pat in expr: body	Iteration
while cond: body	Conditional loop
break / continue	Loop control
callee(args) -> pat: body	Block call
yield expr	Invoke block
expr |> expr	Pipeline
try: body except E as e: body finally: body	Exception handling
raise expr	Raise exception
import module / from module import names	Import
export names	Export
module name	Module declaration
16. Complete Grammar
program : (module_decl)? (declaration | statement)* EOF

module_decl : 'module' dotted_name

declaration : 'export' name (',' name)*
| 'data' name type_params? struct_body
| 'data' name type_params? '(' variant_list ')'
| 'func' name type_params? '(' params? ')' return_type? ':' block
| 'const' name ':' type_expr '=' expr

statement : binding
| expr
| 'if' expr ':' block ('elif' expr ':' block)* ('else' ':' block)?
| 'match' expr ':' match_cases
| 'for' pattern 'in' expr ':' block
| 'while' expr ':' block
| 'return' expr?
| 'raise' expr?
| 'break'
| 'continue'
| 'try' ':' block except_clause* ('else' ':' block)? ('finally' ':' block)?
| 'yield' expr

binding : pattern (':' annotations)? '=' expr

annotations : annotation (',' annotation)*
annotation : type_expr
| expr ('else' string)?

struct_body : '{' field* '}'
| ':' INDENT field* DEDENT

field : name ':' annotations ('=' expr)?
| 'func' name '(' 'self' params? ')' return_type? ':' block

variant_list : variant ('|' variant)*
variant : name type_params? ('(' fields? ')')?

params : param (',' param)*
param : name ':' annotations ('=' expr)?

return_type : '->' type_expr

type_expr : type_term ('|' type_term)*
type_term : name ('[' type_expr (',' type_expr)* ']')?

type_params : '[' name (',' name)* ']'

match_cases : case_clause+ else_clause?
case_clause : 'case' pattern ('if' expr)? ':' block
else_clause : 'else' ':' block

pattern : or_pattern
or_pattern : and_pattern ('|' and_pattern)*
and_pattern : primary_pattern
primary_pattern : literal
| '_'
| name (':' annotations)?
| '(' pattern (',' pattern)* ')'
| '[' pattern (',' pattern)* ']'
| '[' pattern ',' '' name ']'
| '{' key_pattern (',' key_pattern) '}'
| constructor_name '(' (key_pattern (',' key_pattern)*)? ')'

key_pattern : string ':' pattern
| name '=' pattern

block : ':' INDENT statement* DEDENT

expr : pipeline
pipeline : logical_or ('|>' logical_or)*
logical_or : logical_and ('or' logical_and)*
logical_and : not_expr ('and' not_expr)*
not_expr : 'not' not_expr | comparison
comparison : arith_expr (comp_op arith_expr)*
comp_op : '==' | '!=' | '<' | '>' | '<=' | '>=' | 'in' | 'is'
arith_expr : term (('+' | '-') term)*
term : factor (('' | '/' | '//' | '%') factor)
factor : ('+' | '-') factor | power
power : primary ('**' factor)*
primary : literal
| name
| '(' expr ')'
| primary '.' name
| primary '(' args? ')'
| primary '[' expr ']'
| primary ':' block_expr?
| arrow_func

args : arg (',' arg)*
arg : expr
| name '=' expr

arrow_func : '(' params? ')' '=>' expr
block_expr : '->' pattern ':' block

literal : INTEGER | FLOAT | STRING | 'true' | 'false' | 'none'
| '[' (expr (',' expr))? ']'
| '{' (key_value (',' key_value))? '}'
key_value : STRING ':' expr | name '=' expr

dotted_name : name ('.' name)*
constructor_name : UPPER_CASE name?
name : LOWER_CASE | UPPER_CASE

Operator Precedence
Precedence	Operators	Associativity
1 (lowest)	|>	left
2	or	left
3	and	left
4	not	right (prefix)
5	== != < > <= >= in is	none
6	+ -	left
7	* / // %	left
8	- (unary) + (unary)	right (prefix)
9	**	right
10	. () []	left
17. A Complete Example
module app.signup

import app.database as db
import app.email as email

---------- Domain types ----------
data Plan:
Free
Pro(max_users: int)
Enterprise(domains: list[str])

data SignupInput:
name: str, len(name) > 0 else "Name is required"
email_addr: str, contains(email_addr, "@") else "Invalid email"
age: int, age >= 13 else "Must be at least 13"
plan: Plan = Plan.Free

data SignupResult:
Created(user_id: str)
Duplicate(existing_id: str)
Invalid(reasons: list[str])

---------- Business logic ----------
func signup(input: SignupInput) -> SignupResult:

Check for duplicates
match db.find_user_by_email(input.email_addr):
case Some(existing):
return SignupResult.Duplicate(existing_id=existing.id)
case None:
pass

Create the user
user = db.create_user(
name=input.name,
email=input.email_addr,
age=input.age,
plan=input.plan
)

Send welcome email (best effort)
try:
using(email.connect()) -> conn:
conn.send_welcome(user.email, user.name)
except EmailError:
log("failed to send welcome email to " + user.email)

return SignupResult.Created(user_id=user.id)

---------- HTTP handler ----------
func handle_signup(request: HttpRequest) -> HttpResponse:
raw = request.json()

match SignupInput.decode(raw):
case Ok(input):
match signup(input):
case SignupResult.Created(id):
return HttpResponse(status=201, body={"id": id})
case SignupResult.Duplicate(id):
return HttpResponse(status=409, body={"error": "duplicate", "id": id})
case SignupResult.Invalid(reasons):
return HttpResponse(status=422, body={"errors": reasons})

case Err(error):
return HttpResponse(status=400, body={"error": error.message})

---------- Entry point ----------
func main():
server = HttpServer(handler=handle_signup, port=8080)
server.start()
print("Server running on port 8080")

if name == "main":
main()

End of Nomi Language Specification v0.2.0

