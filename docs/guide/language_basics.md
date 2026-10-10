# Language Basics

> Status: introductory guide to a verified subset of the current prototype.

[User guide](README.md) / [Getting started](getting_started.md) / Language basics

Each example below is a complete program. Paste one at a time into a browser
scratch document, or save it as `example.nomi` and run:

```bash
nomi example.nomi --output program
```

The examples teach current prototype syntax. Read the
[support differences](status.md#prototype-and-target-differences) before
copying syntax from a target design document into a runnable program.

## Name Values

```nomi
name = "Ada"
quantity = 3
unit_cents = 1200
print("Hello, " + name)
print(quantity * unit_cents)
```

Output:

```text
Hello, Ada
3600
```

`=` gives a value a name. Quotes create text. `+` joins text here; `*` multiplies
numbers. `print` displays a value. A line starting with `#` is a comment.
Use integer cents for these examples rather than introducing decimal money rules.

Prototype compatibility also permits text repetition with an integer. Do not
read the invoice's wrong-input error as a complete checked numeric contract;
the [source checker](getting_started.md#check-a-program-without-running-it)
provides separate, limited type evidence.

The target will make ordinary names immutable and updates explicit. This guide
does not teach prototype rebinding as the future mutation contract.

## Define And Call A Function

```nomi
func subtotal(price, quantity):
    return price * quantity

print(subtotal(1200, 3))
print(subtotal(1200, 4))
```

Output:

```text
3600
4800
```

`func` introduces a named function. `price` and `quantity` are its parameters;
the call supplies their values in that order. The indented lines form its body.
`return` sends a result back to the caller. You can use that result in a larger
expression, as the invoice in Getting Started does.

Use consistent indentation; these examples use four spaces. A function
definition does not run its body until the function is called.

## Choose With A Condition

```nomi
age = 20
if age >= 18:
    print("eligible")
else:
    print("below minimum age")
```

Output:

```text
eligible
```

`>=` compares values. `if` chooses a branch using the condition; `else` supplies
the alternative. Change the age to `12` to take the other branch. `==` compares
for equality; it is different from naming a value with `=`.

## Work With A List

```nomi
amounts = [900, 360]
print(amounts[0])
print(len(amounts))
for amount in amounts:
    print(amount)
```

Output:

```text
900
2
900
360
```

Square brackets create a list. `amounts[0]` reads its first element: indexing
starts at zero. `len` gives its length. `for` runs the indented body for each
element in order. Reading an index outside the list fails; it does not supply
an absent value automatically.

## Group Named Fields

```nomi
customer = {"name": "Ada", "age": 20}
print(customer["name"])
print(customer["age"])
```

Output:

```text
Ada
20
```

This map associates keys with values. A key such as `"name"` is text; bracket
lookup retrieves its associated value. A missing key fails. This simple map is
not a validated customer type: use the report example to see an explicit
validation boundary. The planned `data` system will give owned concepts their
own identity and checked fields.

## Select And Transform A Collection

```nomi
func eligible(age):
    return age >= 18

func next_year(age):
    return age + 1

ages = [20, 12, 30]
adults = list(filter(eligible, ages))
future_ages = list(map(next_year, adults))
print(adults)
print(future_ages)
```

Output:

```text
[20, 30]
[21, 31]
```

`filter` keeps elements whose function returns true. `map` applies a function
to each element. The function passed to another operation is often called a
**callback**. Current `map` and `filter` take the callback first; `list(...)`
materializes their results so the Python and browser examples agree.
The [target collection convention](status.md#prototype-and-target-differences)
is different, so this ordering is labeled as prototype behavior.

## Accumulate A Total And Its History

```nomi
func add(total, amount):
    return total + amount

amounts = [900, 360]
print(fold(amounts, 0, add))
print(scan(amounts, 0, add))
print(fold([], 0, add))
```

Output:

```text
1260
[0, 900, 1260]
0
```

`fold` starts with a seed (`0` here) and combines it with each element in order.
The result becomes the next call's first argument. `scan` keeps the seed and
each intermediate result. An empty fold returns its seed. These are ordinary
library calls; they do not imply streaming, parallelism, or a database query.

## Convert Text Explicitly

```nomi
text = " 3 "
quantity = int(text.strip())
print(quantity + 1)
```

Output:

```text
4
```

`strip()` removes surrounding whitespace; `int(...)` converts numeric text.
Text such as `"three"` cannot be converted this way and produces an error.
This is an exploratory conversion, not a decoder that collects every input
error. For that workflow, continue with the
[JSON report](getting_started.md#validate-a-json-report).

## If You Know Python

Many expressions and indented control-flow forms feel familiar. Nomi uses
`func` for the functions taught here, and its collection/runtime APIs have their
own supported subset. Existing Python compatibility does not mean arbitrary
Python modules or methods work in the browser. The target is also changing
binding, data, failure, and effect contracts deliberately.

Use the [example catalog](examples.md) to continue with complete programs,
or [tools and troubleshooting](tools.md) to work with your own files.
