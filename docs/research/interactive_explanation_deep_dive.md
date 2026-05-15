# Interactive Explanation Deep Dive

## Status

Active comparative research. This document grounds Nomi's interactive
workflow design (REPL, notebook, trace, explanation) in evidence from
ten real systems. It is a decision-support document, not a specification.
The Adopt/Refuse/Adapt table in §12 is the primary output for
implementation planning. Companion documents:
`diagnostics_and_explanations_comparative.md` (diagnostic architecture),
`cross_language_synthesis_master.md` §5 (explanation normal form),
`language_design_dimensions.md` (design space axes).

## Purpose

Nomi's product promise includes "explain what happened" as a core
operation alongside "name a value," "transform values with functions,"
and "check what must be true." This document studies how real
programming environments have delivered on the promise of interactive
explanation — REPLs, notebooks, traces, live feedback, visual
programming — and extracts the structural lessons that should shape
Nomi's interactive workflow.

This is not a catalogue of features. It is a comparison of interactive
architectures: the structural decisions that determine whether an
environment makes program behavior inspectable, reproducible, and
teachable. The question is not "should Nomi have a notebook?" but
"what interactive primitives make explanation a first-class experience,
and how do those primitives compose with Nomi's existing normal forms?"

The document covers ten systems, then synthesizes the patterns, forks,
and tradeoffs. It ends with a concrete Adopt/Refuse/Adapt table for
Nomi.

---

## 1. Jupyter — The Accidental Standard

### The Core Interactive Insight

Jupyter's genius was recognizing that interactive computing is
fundamentally a **conversation between a human and a running process.**
The cell is not a file. It is a unit of interaction: write some code,
execute it, see output, write more. This matches how scientists and
exploratory programmers actually work — they don't write programs
top-to-bottom; they probe, inspect, adjust, and accumulate.

The IPython kernel (2001, Fernando Perez) preceded the notebook
interface by a decade. The kernel protocol is the invisible
architectural achievement: a JSON-based message bus connecting a
frontend (notebook, console, IDE) to a long-running language process.
The protocol defines `execute_request`, `execute_result`,
`display_data`, `error`, `stream`, and `input_request` — a complete
language for interactive computation that is completely independent of
both the user interface and the language runtime.

### What Worked Exceptionally Well

**The kernel protocol as a general interactive substrate.** The
separation of frontend from kernel means Jupyter supports 100+
languages through the same interface. The protocol is the product.
Every language that implements a Jupyter kernel (Python, Julia, R,
Scala, Haskell, Scheme, Prolog, Bash) gets the same notebook
experience. This is the opposite of building a custom IDE per language.
It is a recognition that interactive computing is a general need with
a small set of protocol operations.

**Rich output as a first-class concept.** Jupyter's `display_data`
message carries MIME-typed output: `text/plain`, `text/html`,
`image/png`, `application/vnd.plotly.v1+json`. A cell's output is not a
string; it is a bundle of representations. This means a single library
(matplotlib, plotly, pandas) can render itself as a table, a chart, an
interactive widget, or raw text depending on the frontend. The
separation of "what was computed" from "how it is displayed" is the
right abstraction.

**The cell as a unit of incremental construction.** The cell models
the way people actually explore data: load data in cell 1, clean it in
cell 2, visualize in cell 3, notice a problem, go back to cell 2,
change the cleaning, re-execute, update the plot. This loop is
fundamentally different from edit-save-compile-run. The notebook
collapses the cycle to edit-shift-enter-see.

**Magic commands.** IPython's `%` and `%%` magics recognize that some
operations are not Python expressions but meta-operations on the
interactive session: `%timeit`, `%debug`, `%run`, `%%bash`. They are
not part of the language grammar but part of the interactive protocol.
This separation is correct: interactive affordances should not compete
for syntax space with language constructs.

### What Failed or Caused Persistent Friction

**Mutable hidden state.** Jupyter does not track which cells were
executed or in what order. The kernel maintains a single mutable
namespace. Execute cell 2, then cell 5, then cell 2 again, and the
state is whatever it is. There is no guarantee that executing cells
top-to-bottom produces the same state as the current kernel state. This
is the "hidden state problem" — the notebook file is not a truthful
representation of the program that produced the outputs visible on
screen. A notebook opened by a colleague produces different results
than the colleague saw, because the notebook records code but not the
execution order.

**Non-linear execution as a footgun.** The freedom to execute cells in
any order is powerful during exploration but catastrophic for
reproducibility. A notebook that works perfectly for its author may
fail entirely when executed linearly because cell 5 assumed cell 3 ran
first but cell 3 wasn't in the linear path. This creates "works on my
machine" at the cell level.

**The notebook file format as a version control disaster.** The
`.ipynb` format is JSON with embedded base64-encoded output blobs and
execution counts. Diffing notebooks is painful. Merging them is nearly
impossible. The format conflates source code, output, and metadata in a
single file, making it hostile to every version control operation
programmers rely on.

**No test story.** A notebook cannot be imported as a module, cannot
be parametrized over inputs, and cannot be run in CI without fragile
tooling (`nbconvert`, `papermill`, `nbval`). The cell is a unit of
interaction but not a unit of testing or composition. This creates a
wall between "exploratory code" (notebook) and "production code"
(modules), forcing a rewrite when exploration graduates to deployment.

**Kernel death without recovery.** The kernel process can die
(oOM, segfault, infinite loop). When it does, all state is lost. There
is no checkpointing, no replay, no incremental recovery. The user
starts over.

### Key Structural Insight for Nomi

Jupyter got the **protocol separation** right and the **state model**
wrong. The interactive surface (cells, output, display) should be
separated from the execution backend (kernel, language runtime) through
a well-defined protocol — Jupyter's kernel protocol is the model to
beat. But the execution model must track dependency order, not rely on
the user to maintain it mentally. A notebook should know which cells
are stale relative to their dependencies. The file format should
separate source from output so version control works.

---

## 2. Pluto (Julia) — Reactive Notebooks With Deterministic Execution

### The Core Interactive Insight

Pluto's thesis: a notebook cell is not an imperative command to the
kernel. It is a **reactive function of its dependencies.** When you
define `x = 3` in cell A and `y = x + 1` in cell B, Pluto understands
that B depends on A. If you change A, B recomputes automatically. The
execution order is not the order cells appear on screen — it is the
topological order of the dependency graph.

This inverts Jupyter's model. In Jupyter, you manage execution order
manually and the notebook silently drifts from its own source. In
Pluto, the notebook IS the dependency graph, and execution order is
derived from it deterministically.

### What Worked Exceptionally Well

**Dependency analysis through syntax.** Pluto parses each cell and
extracts variable references. If cell B references `x`, and `x` is
defined in cell A, Pluto records the edge A -> B. This is done without
executing the cell. The dependency graph is a static property of the
code text, computed at parse time. This means Pluto can tell you "this
cell references variables that don't exist" before you run anything.

**Automatic reactivity.** When a cell changes, every downstream cell
recomputes. But Pluto is smart about it: if the value of `x` doesn't
actually change (the expression `3` is replaced with `1 + 2`), Pluto
does not recompute downstream cells because their inputs haven't
changed. This is value-aware reactivity, not naive dirty-flag
propagation.

**Hidden state made visible.** Pluto shows which cells are computing,
which are stale, which have errors. There is no hidden kernel state
because the state IS the set of cell return values, and every cell's
state is visible as its output. If a cell references a variable that
changed, it recomputes. If it references a variable that was deleted,
it shows an error. The notebook cannot lie about how it was executed
because there is exactly one valid execution order for any given
notebook state.

**Package management as part of the notebook.** Pluto cells can
contain `using` statements, and Pluto's package manager automatically
installs missing packages and records them in the notebook's
`Project.toml`-equivalent manifest. A Pluto notebook carries its own
environment. Opening a notebook on a different machine reproduces the
exact package versions. This solves the "works on my machine" problem
at the package level, not just the code level.

**Export as static HTML.** Pluto notebooks can render to a standalone
HTML file with all outputs embedded and all code visible. The
interactive reactivity is lost, but the artifact is a truthful
snapshot.

### What Failed or Caused Persistent Friction

**The single-definition constraint.** Pluto enforces that each
variable is defined in exactly one cell. You cannot redefine `x` in
cell A and then redefine `x` in cell D. This is necessary for
dependency analysis (which `x` does cell B depend on?), but it
conflicts with the natural exploratory workflow where you try different
values of `x` and see what happens. Pluto's workaround is `@bind` for
interactive widgets, but the tension between "one definition" and
"exploratory iteration" is real.

**The "everything recomputes" problem.** If you change a cell near the
top of a long notebook, everything below it recomputes. For
data-science workflows where loading and cleaning data takes minutes,
this is painful. Pluto has caching (`PlutoRunner.@use_cache`) but it
is opt-in and fragile. The reactivity model assumes cells are cheap
to recompute, which is true for pure functions but false for I/O-bound
data loading.

**No notebook-as-module.** Like Jupyter, Pluto notebooks are not
importable as Julia modules. You cannot `include("analysis.jl")` as a
library. The notebook is an artifact, not a composable unit.

**The notebook file is still a custom format.** Pluto uses `.jl` files
with cell markers in comments rather than JSON, which is a vast
improvement for version control. But the cell-marking convention
(`# ╔═╡ ...` UUIDs) is still a proprietary layer over plain code.

### Key Structural Insight for Nomi

Pluto proves that **dependency-aware execution is feasible and
desirable** for interactive computing. The key architectural move is
treating the notebook not as a list of commands but as a set of
definitions with a derived partial order. Nomi should adopt this
principle: every interactive unit (cell, block, pipeline stage) should
declare what it reads and what it produces, so the system can derive
execution order and staleness automatically. But Nomi should also
solve the exploratory-redefinition problem that Pluto punts on — by
allowing variable shadowing in interactive scope while tracking which
downstream cells depend on which definition.

---

## 3. Darklang — Traces as a First-Class Language Concept

### The Core Interactive Insight

Darklang's central thesis: **every execution should produce a
trace, and the trace should be the primary artifact of
development.** In Darklang, every HTTP request to your application is
automatically recorded. The trace contains every input, every function
call, every intermediate value, every database query, every external
API call, and every output. You don't add logging statements. You don't
configure a debugger. The trace exists because the runtime was built
to produce it.

This changes the edit-debug cycle fundamentally. In a traditional
language, you see a bug, you hypothesize, you add `print` statements or
attach a debugger, you reproduce the bug, you inspect state. In
Darklang, you click on the failing request in the trace list and you
see exactly what happened — every value at every step. The trace IS
the debugger. There is no separate "debug mode."

### What Worked Exceptionally Well

**Trace-driven development as a workflow.** The "replay" button on a
trace re-executes the handler with the exact same inputs. You can edit
your code, hit replay, and see whether the new code produces the right
output for that specific request. This is test-driven development
without writing tests — the production traces ARE your test cases. You
build up a library of traces representing real user behavior, and you
validate every code change against that library.

**Live values in the editor.** The Darklang editor does not just show
code. It shows the values that code produced on the most recent
execution. Each expression is annotated with its runtime value. This
collapses the separation between "writing code" and "seeing what it
does" into a single view. You don't run the program to see output; the
output is always visible as an annotation on the code that produced it.

**The "404s as traces" insight.** In most web frameworks, a 404 error
produces a minimal log line. In Darklang, a 404 produces a full trace
showing the entire routing decision process — which routes were
checked, which patterns matched, which didn't. This turns opaque "why
didn't my route match?" debugging into an inspectable decision tree.

**Feature flags as trace dimensions.** Darklang's feature flag system
is integrated with traces. Every trace records which feature flags were
active. You can filter traces by flag combination. This makes feature
flag testing deterministic: toggle a flag, replay traces, verify
behavior.

**Type checking across execution boundaries.** Because Darklang
controls the entire stack (language, editor, runtime, infrastructure),
it can type-check not just internal code but the boundaries between
your code and external services. If your handler expects a JSON field
`user_id` as an integer but the incoming request sends a string, the
trace shows the type mismatch at the boundary.

### What Failed or Caused Persistent Friction

**The walled-garden problem.** Darklang is not a language you can run
locally. It is a cloud platform. Your code, your traces, your data —
all live in Darklang's infrastructure. This is architecturally elegant
(they can instrument everything) but practically limiting (you can't
use it for anything that needs local execution, offline work, or
self-hosted infrastructure). The full-stack integration that makes
traces powerful also makes the system a monoculture.

**Limited language scope.** Darklang was designed for HTTP services.
Its abstractions (handlers, datastores, workers) map cleanly to
web-backend patterns but poorly to other domains: data analysis,
scripting, CLI tools, embedded systems, game logic. The trace model
works beautifully within the domain but doesn't generalize.

**Trace volume without filtering.** Every request produces a trace.
For high-traffic services, the trace volume is enormous. Darklang
provides filtering and sampling, but the fundamental tension remains:
more traces = more debugging power = more storage cost. The "keep
everything" model doesn't scale to all workloads.

**The node-and-edge editor.** Darklang's visual editor is a
node-and-edge graph of function calls, not a text editor. While this
makes data flow visible, it makes common text-editing operations
(copy-paste, find-replace, refactoring) significantly harder. The
visual representation is information-dense but low-bandwidth for input.

### Key Structural Insight for Nomi

The trace-as-first-class-citizen model is the right ambition. Every
Nomi execution should produce a trace record, and that record should
carry source spans from parse time so the trace can be rendered back
onto the source code. The key design constraint: traces should be a
**property of the runtime, not of a special debug mode.** The user
shouldn't have to "enable tracing" — tracing should be always-on for
interactive sessions, with configurable retention for production. Nomi
should learn from Darklang's scope limitation: the trace model should
be general (any computation produces a trace) not domain-specific
(only HTTP handlers produce traces). The `explain` operation in Nomi's
product promise maps directly to "render this trace as an inspectable
structure."

---

## 4. Smalltalk — The Original Live Programming Environment

### The Core Interactive Insight

Smalltalk invented live programming in the 1970s and remains, in
significant ways, unsurpassed. The core insight: **the program is not
a text file you edit and then run. The program is a running world of
objects, and the programming environment is a set of tools for
inspecting and modifying that world while it runs.**

Smalltalk's "image" is a snapshot of the entire running system —
every object, every class, every method, every stack frame, every
window. You don't start Smalltalk by loading source files. You resume
an image. The image IS the program. Source code is a serialization
format for methods, not the ground truth. The ground truth is the live
object graph.

### What Worked Exceptionally Well

**The object inspector.** In Smalltalk, you can inspect any object at
any time. The inspector shows you the object's class, its instance
variables (with their values, which are themselves inspectable), and
its methods. Clicking on an instance variable opens a new inspector on
that object. This creates an ad-hoc object graph browser that follows
the actual runtime relationships between objects, not the static type
hierarchy. Debugging becomes "follow the references until you find the
wrong value."

**The class browser.** Smalltalk's browser is not a file explorer. It
is a live query tool over the class hierarchy. The four-pane browser
(categories, classes, protocols, methods) shows you every class in the
system, every method on every class, and lets you edit any method
immediately. There is no "open file" step because there are no files.
The browser IS the codebase, and it is always in sync with the running
system because the codebase IS the running system.

**The edit-continue debugger.** When a Smalltalk program hits an error
or a breakpoint, the debugger opens showing the full stack. You can
inspect any variable in any stack frame, evaluate expressions in the
context of that frame, edit the method that caused the error, and
**continue execution from where it stopped.** The edit is applied to
the running system immediately. The program resumes with the fixed
code. This collapses the edit-compile-debug cycle into a single
continuous flow: error -> inspect -> fix -> continue.

**`doesNotUnderstand:` as a universal extension point.** When you send
a message to an object that doesn't have a corresponding method, the
runtime sends `doesNotUnderstand:` instead. You can override this
method to create proxies, mock objects, remote object references, or
lazy-loading stubs. This single hook enables an enormous range of
meta-object protocols without special language features.

**`become:` for in-place object replacement.** Smalltalk's `become:`
message swaps the identity of two objects. Every reference to object A
now points to object B, and vice versa. This is used for live system
upgrades: create the new version of a class, migrate instances, then
`become:` the new class into the old class's identity. No restart
required. The running system has been transformed.

### What Failed or Caused Persistent Friction

**The image as a single point of failure.** The image is powerful but
fragile. Corrupt the image and you lose everything — all code, all
objects, all state. There is no "source of truth" outside the image.
Modern Smalltalks have source files (`.st`), but they are derived from
the image, not the other way around. This makes version control,
collaboration, and CI fundamentally awkward.

**The image as a deployment artifact.** Shipping a Smalltalk
application means shipping an image. The image contains the entire
development environment (browser, debugger, compiler) alongside the
application code. Stripping the image is possible but labor-intensive.
This blur between development and deployment is philosophically elegant
but operationally problematic.

**Collaboration friction.** Two programmers cannot easily work on the
same image simultaneously. Smalltalk's answer was "put the image on a
server" (GemStone) or "merge changesets," but neither approach matched
the simplicity of git branches and text files. The image model is
fantastic for solo exploration but hostile to distributed version
control.

**Learning curve of the environment.** Smalltalk's environment is
completely alien to programmers trained on files, editors, and command
lines. The browser, inspector, and debugger are not "tools you open
when needed" — they ARE the programming environment. There is no
"just edit a file" fallback. This all-in commitment creates a high
activation barrier.

**Performance transparency.** When every method lookup is a message
send and every message send can be intercepted via
`doesNotUnderstand:`, performance characteristics become opaque. A
seemingly simple operation might trigger a chain of meta-object
protocol interactions. The live environment's power obscures its cost.

### Key Structural Insight for Nomi

Smalltalk's inspector-browser-debugger triad is the gold standard for
interactive object inspection. The key lesson: **the programming
environment should be a set of live views over the running program, not
a set of static tools applied to source files.** Nomi should provide
inspectable runtime state — every binding, every pipeline stage,
every block invocation should be inspectable in the way Smalltalk
objects are inspectable. The `explain` operation should open an
inspector on the relevant trace record, not just print text.

Smalltalk's image model is probably wrong for Nomi (it creates the
single-point-of-failure problem), but the edit-continue workflow is
right. Nomi should support interactive error recovery: when a pipeline
stage fails, let the user inspect the value that failed, edit the
stage, and re-execute without restarting the entire computation.

---

## 5. Racket — The REPL as a Design Surface

### The Core Interactive Insight

Racket's REPL is not a toy. It is a **programming environment
architectural layer** that supports module contexts, contract
monitoring, and language-level extensibility. In Python, the REPL is
"evaluate expressions in a global namespace." In Racket, the REPL is
"interact with a running program at a specific module boundary, with
full contract enforcement and macro expansion."

### What Worked Exceptionally Well

**The `,enter` command for module context.** Racket's REPL allows you
to "enter" a module: `,enter "my-module.rkt"`. After entering, the
REPL evaluates expressions in the lexical context of that module.
Private bindings are accessible. Macros defined in the module are
available. This means the REPL is not a separate execution context from
your program — it is a window INTO your program's namespace. This is
fundamentally different from Python's `import` at the REPL, which
creates a separate module object you access through the global
namespace.

**Contract monitoring at the REPL boundary.** Racket's contract system
attaches runtime checks to module boundaries. When you call a function
at the REPL, contracts on that function's arguments and return value
are enforced. If you pass a value that violates the contract, you get a
blame message that identifies the violating party and the contract
location. This means the interactive boundary is CHECKED, not
unchecked. The REPL is not a backdoor that bypasses type safety or
contracts.

**Scribble for literate programming.** Racket's Scribble system embeds
executable code in documentation. The documentation is a program that
produces rendered output. Code examples in docs are not copy-pasted
illustrations — they are actual Racket expressions that are evaluated
at documentation-build time. If the example produces a different value
than the docs claim, the build fails. This is "documentation as
continuous integration."

**DrRacket's interactive annotations.** DrRacket, the Racket IDE,
shows macro expansion inline: click on a macro use and see the expanded
code. It shows contract violations with arrows pointing from the
offending value to the contract that was violated. It shows test
coverage as colored overlays on source code. These are not separate
tools — they are annotations on the primary artifact (the code text).

**Language-oriented programming at the REPL.** Racket's `#lang`
mechanism means the REPL itself can run in different language modes.
`#lang racket` gives you the standard Racket REPL. `#lang datalog`
gives you a Datalog REPL. `#lang scribble` gives you a documentation
REPL. The REPL inherits the language's semantics, not just its syntax.
This means Racket is not one language with a REPL — it is a REPL
platform for building languages.

### What Failed or Caused Persistent Friction

**The REPL's invisibility to non-Racket programmers.** Racket's REPL
capabilities (`namespace-variable-binding`,
`namespace-undefine-variable!`, `current-namespace`) are powerful but
poorly communicated. Most programmers experience the Racket REPL as
"like Python's but with more parentheses" because the architectural
distinctions aren't visible at the surface.

**Contract monitoring overhead.** Contracts are checked at runtime, and
complex contracts (especially higher-order contracts on functions that
take functions and return functions) can impose significant overhead.
The contract system's power at the REPL boundary comes with a
performance cost that can surprise users.

**DrRacket's complexity.** DrRacket provides a rich set of interactive
tools, but discovering them requires learning the IDE. The "check
syntax" button, the macro stepper, the contract profiler — these are
powerful but not self-revealing.

**The language tower's cognitive load.** The `#lang` mechanism is
brilliant but creates a meta-problem: which language am I currently
using? What bindings are available? What semantics apply? The power is
real, but the user's mental model must track an additional dimension
(current language) on top of the usual dimensions (current module,
current namespace).

### Key Structural Insight for Nomi

Racket's `,enter` command is the right model for Nomi's REPL: the REPL
should be a window into a specific execution context, not a separate
global namespace. When the user is working in a Nomi notebook or
source file and opens a REPL, the REPL should share the bindings,
contracts, and pipeline state of that context. The REPL is not an
alternative to the program — it is an interactive view of the
program.

Contract monitoring at the interactive boundary is also critical for
Nomi. If Nomi has binding constraints (`x: int > 0`), those constraints
should be enforced when the user interactively rebinds `x` at the REPL,
not silently bypassed. The interactive boundary should be the most
checked boundary, not the least.

---

## 6. Light Table — The Ambitious Experiment

### The Core Interactive Insight

Light Table (Chris Granger, 2012) attempted a radical vision: **the
editor itself should be a live programming environment where every
expression shows its value, every function shows its outputs, and
code is not a document but a live, inspectable computation.** The
Kickstarter video showed a ClojureScript program where each line
displayed its evaluation result inline, values propagated through the
code as you typed, and documentation appeared on demand.

The core architecture: Light Table connected to a language runtime
(initially ClojureScript via the browser's JavaScript engine) through
a WebSocket-based "client" protocol. Each editor pane was a live view
over an evaluation context. Typing an expression triggered evaluation
and displayed the result in the editor gutter.

### What Worked Exceptionally Well

**Inline evaluation as the default.** Light Table showed values next to
every expression, not in a separate output pane. The value of `(+ 1 2)`
appeared to the right of `(+ 1 2)`. This collapsed the distance between
"the code" and "what the code does" to literally zero pixels. You read
the code and its result simultaneously.

**Watchers and live data flow.** Light Table's "watches" let you select
an expression and see its value update as you edited other parts of the
program. A watch on the output variable would change in real time as
you edited the function that produces it. This made data flow visible
without explicit debugging.

**The insta-REPL.** Every editor pane was a REPL. There was no
distinction between "editing a file" and "interacting with a REPL."
You typed code, saw results. You evaluated a region, saw results. The
REPL was not a tool you opened — it was the default mode of the
editor.

**Documentation as a live view.** Light Table could show documentation
for any function on demand, and the documentation included live
examples you could edit and re-evaluate inline. This made documentation
exploratory rather than static.

**Plugin architecture as a lesson.** Light Table's behavior was
defined by plugins written in ClojureScript. You could inspect and
modify the editor's behavior from within the editor itself. This was
Smalltalk's "the environment is written in the language" philosophy
applied to a modern editor.

### Why It Did Not Achieve Mainstream Adoption

**The browser-as-runtime constraint.** Light Table was built on
Electron (then called Atom Shell). The language runtimes it connected
to ran inside the browser's JavaScript engine. This worked for
ClojureScript and JavaScript but made connecting to other languages
(native Python, C++, Java) impractical. The live-evaluation
architecture assumed a single-threaded, browser-hosted runtime, which
doesn't match how most production languages work.

**Performance of pervasive evaluation.** Evaluating every expression
on every keystroke is expensive. Light Table's ClojureScript compiler
was fast enough for many expressions but not for all. Large files or
expensive computations caused visible lag. The "evaluate everything
always" model doesn't scale without smart caching and incremental
re-evaluation — which Light Table didn't have time to build.

**The plugin trap.** "Everything is a plugin" means the core experience
depends on the quality of community plugins. When the community is
small, the plugin ecosystem is sparse. When the plugin ecosystem is
sparse, the editor feels bare. This is a chicken-and-egg problem that
bedeviled Light Table.

**Competing with established editors.** Light Table asked programmers
to switch editors. This is one of the hardest asks in software.
Programmers have years of muscle memory, custom configurations, and
workflows built around their current editor. A live-evaluation feature,
no matter how good, is rarely enough to justify switching.

**The project's scope versus maintainer capacity.** Light Table was
ambitious: a new editor, a new plugin system, a new evaluation
protocol, new language integrations, new UI paradigms. The team was
small. The burn rate of maintaining all these pieces simultaneously was
unsustainable. Chris Granger eventually moved on to Eve, another
ambitious project, and Light Table entered maintenance mode.

**The ideas arrived before the ecosystem was ready.** WebAssembly didn't
exist. Language server protocol didn't exist. Jupyter's kernel protocol
was in its infancy. The infrastructure for connecting editors to
language runtimes was embryonic. Light Table had to build everything
from scratch. Today, many of Light Table's ideas are being
re-implemented on more mature infrastructure (VS Code's notebook API,
Jupyter's real-time collaboration, Observable's reactive evaluation).

### Key Structural Insight for Nomi

Light Table proved that **inline value display is compelling** — seeing
values next to the code that produced them changes how programmers
think about their programs. Nomi should support this as a view mode:
the pipeline `data |> where(_.active) |> select(_.name)` should be
displayable with intermediate values annotated at each stage.

Light Table also proved that **"evaluate everything on every keystroke"
doesn't scale.** Nomi should support explicit evaluation triggers
(shift-enter, like Jupyter) as the primary interaction model, with
optional auto-evaluation for pure, cheap computations. The system
should know which expressions are expensive (I/O, large data) and
avoid auto-evaluating them.

The deeper lesson: **infrastructure before experience.** Light Table
tried to build the experience before the infrastructure existed. Nomi
should build on existing protocols (Jupyter kernel protocol, LSP)
rather than inventing new ones, and layer its interactive experience on
top of mature infrastructure.

---

## 7. Observable — Reactive JavaScript Notebooks

### The Core Interactive Insight

Observable's model: **a cell is a function of its dependencies, and
execution order is the topological order of the dependency graph.**
This sounds like Pluto, and the lineage is direct (both descend from
the same reactive-programming lineage), but Observable applies it to
JavaScript with a distinctive syntax and execution model.

The key difference from Jupyter: Observable cells do not execute in
document order. They execute in dependency order. If cell C depends on
cell A and cell B, C runs after both A and B complete, regardless of
where C appears in the document. This means the document is a
declaration of relationships, not a sequence of commands.

### What Worked Exceptionally Well

**Topological execution as the only mode.** Observable does not offer a
"run cells in order" mode. The dependency graph IS the execution order.
This eliminates the hidden-state problem entirely. You cannot execute
cells in the wrong order because the system doesn't let you specify an
order. You specify dependencies, and the system derives the order. This
is a hard constraint that eliminates an entire class of notebook bugs.

**The cell-as-function model.** An Observable cell is literally a
function: `viewof x = { ... }` defines a cell whose value is computed
by a function. The function's arguments are the cell's dependencies,
inferred from the function body. This is a clean model: cells are
functions, dependencies are parameters, execution is function
evaluation. No hidden global state.

**Named cells create a namespace.** Every cell has a name. Cells
reference each other by name. There is no "the global variable `x`" —
there is "the cell named `x`." The cell namespace is flat, visible,
and complete. You can see every name in the document at a glance.

**Views and mutable state are separated.** A "view" cell (`viewof x =
...`) creates an interactive widget whose value can change. Other cells
depend on the value of `x`, not on the widget state. When the user
interacts with the widget, the value changes, and dependent cells
recompute. The mutable state (widget interaction) is represented as a
stream of immutable values. This is functional reactive programming
made concrete and visible.

**Generators for animation.** Observable cells can be generator
functions that `yield` values over time. A cell that `yield`s produces
a stream of values, and downstream cells recompute on each new value.
This makes time-varying computation (animations, simulations, live data
feeds) as natural as static computation.

**Fork-and-remix as the collaboration model.** Observable notebooks
are hosted, and any notebook can be forked with one click. The fork
preserves the full history and attribution. This is GitHub's fork
model applied to notebooks, and it works for the same reasons:
discoverability, attribution, and low-friction experimentation.

### What Failed or Caused Persistent Friction

**JavaScript-only.** Observable is tied to JavaScript. The dependency
analysis works by parsing JavaScript and extracting variable
references. This is elegant for JavaScript but doesn't generalize to
other languages. The reactive runtime is a JavaScript library, not a
language-agnostic protocol.

**The hosted-only model.** Observable notebooks run on Observable's
servers. There is an open-source version (Observable Framework) but
the primary experience is cloud-hosted. This creates the same
walled-garden concerns as Darklang, though less severely since
JavaScript can run anywhere.

**The flat namespace constraint.** Every cell name must be unique
within a notebook. This is correct for dependency analysis but
conflicts with the natural desire to reuse names in different sections
("let me define `data` here, and then define `data` again after
filtering"). Observable's answer is to use different names
(`rawData`, `cleanedData`), which is explicit but verbose.

**The "everything recomputes" problem on load.** When you open an
Observable notebook, every cell runs. For notebooks that load large
datasets or perform expensive computations, this means a long wait
before you can interact. Observable has caching (`await` cells that
resolve to the same value are not recomputed), but the cold-start
experience is slow.

**Limited offline support.** Observable notebooks require a network
connection for initial load (though they can work offline once loaded).
This makes them unsuitable for fieldwork, air-gapped environments, or
unreliable connectivity.

### Key Structural Insight for Nomi

Observable proves that **topological execution with named cells is a
viable and superior alternative to sequential execution.** Nomi should
adopt this model: every interactive unit produces a named value, every
reference to a name creates a dependency edge, and execution order is
the topological order of the dependency graph. The document is a set of
definitions, not a script.

Observable's cell-as-function model is the right abstraction:
`cell = f(dep1, dep2, ...)`. Nomi should make this explicit: a
pipeline stage is a function from input values to an output value, and
the runtime tracks which stages depend on which values.

The "views" concept — mutable interaction points that produce
immutable value streams — is also critical for Nomi. Interactive
widgets (sliders, selectors, inputs) should be first-class cells whose
value changes feed the dependency graph, not imperative callbacks that
mutate hidden state.

---

## 8. Swift Playgrounds / Xcode Playgrounds

### The Core Interactive Insight

Swift Playgrounds (originally introduced by Apple in 2014 as Xcode
Playgrounds, then evolved into the iPad-native Swift Playgrounds app)
bridges the gap between "learning to code" and "exploring code
interactively." The core insight: **code execution should produce
visible, inspectable intermediate results inline, and the user should
be able to see the timeline of values a variable took over time.**

### What Worked Exceptionally Well

**Inline result display.** Swift Playgrounds show the value of each
line in the right margin, color-coded by type: blue for strings, purple
for numbers, green for booleans. You don't need `print()` statements to
see what your code does. The values are just there, visible as you read
the code. This is the same insight as Light Table's inline evaluation,
implemented with Apple's production-quality engineering.

**"Run to this line" interaction.** You can click on a line number to
execute the playground up to that line and pause. This is more
fine-grained than a breakpoint: it's "show me the state of the world
at this exact point." Combined with the inline values, this makes
debugging visual rather than textual. You see your program's state at
a glance, not by typing commands in a debugger console.

**The results sidebar as a value history.** The right sidebar doesn't
just show the current value of each expression. It can show the history
of values across multiple executions. For a loop that runs 100 times,
you see not just the final value but how the value changed over time —
a miniature time series embedded in the editor.

**The timeline for graphical output.** Graphical output (images,
charts, views) appears in a timeline panel below the code. You can
scrub through the timeline to see how the output evolved. This is
particularly powerful for animations and UI development: you see the
visual output changing as the code executes, not just the final frame.

**Live view debugging.** Swift Playgrounds support a "live view" that
updates in real time as you edit code. Change a color constant and the
view updates immediately. Add a UI element and it appears in the live
view. This tightens the feedback loop for UI development to
sub-second, matching the experience of CSS hot-reload in web
development.

**The educational framing.** Swift Playgrounds were designed
explicitly for learning. The "Learn to Code" lessons use a
game-like structure: solve puzzles by writing code, with immediate
visual feedback on whether your solution works. The inline values, the
timeline, the live view — all serve the pedagogical goal of making
computation visible and concrete.

### What Failed or Caused Persistent Friction

**Performance ceilings.** Complex playgrounds with large data
processing or many iterations become slow. The inline evaluation overhead
(computing and rendering values on every line) adds up. Apple added
manual execution control ("run manually" vs "run automatically") to
mitigate this, but the tension between "show everything" and "go fast"
remains.

**The macOS/iPad split.** Xcode Playgrounds (macOS) and Swift
Playgrounds (iPad) are different products with different capabilities.
Xcode Playgrounds support richer debugging, but Swift Playgrounds have
the better learning experience. The feature set is fragmented across
platforms.

**Limited scope.** Playgrounds work well for algorithms, UI
prototyping, and learning. They don't work for apps that require
multiple files, complex build systems, networking, or persistent
state. The playground is an island, not a development environment.

**The resources folder as a hidden dependency.** Playgrounds can access
a "Resources" folder for data files, but this folder is hidden in the
UI. Adding data requires Finder operations outside the playground. This
breaks the self-contained-experience promise.

**No standard sharing format.** A playground is a bundle (a directory
masquerading as a file). Sharing playgrounds means sharing the bundle.
There is no plain-text representation, no version-control-friendly
format, no equivalent of Observable's fork-and-remix.

### Key Structural Insight for Nomi

The **inline value display with color-coded types** is a concrete UX
pattern Nomi should implement: pipeline stages show their output values
in the margin, colored by the type of the value (number, string,
collection, table). The **value history as a timeline** is also
critical: a variable that changes over multiple iterations should show
its history, not just its final value. This is especially important for
Nomi's data-transformation workflows, where "how did the data change at
each pipeline stage?" is the natural question.

The "Run to this line" interaction maps directly to Nomi's pipeline:
you should be able to inspect the data at any pipeline stage boundary,
seeing exactly what value passed from one stage to the next. This is
the `explain` operation applied to a pipeline: "show me what the data
looked like after the `where` stage and before the `select` stage."

---

## 9. Bret Victor's Demos — The Conceptual Foundation

### The Core Interactive Insight

Bret Victor's 2012 talk "Inventing on Principle" and his demos (Learnable
Programming, Drawing Dynamic Visualizations, Stop Drawing Dead Fish)
articulated a principle that underlies much of the work above: **the
creator must have an immediate connection with what they are creating.**
For programmers, this means the code editor should show what the code
DOES, not just what the code SAYS.

His demos were not products. They were provocations. But they named a
set of design principles that have influenced every interactive
programming project since.

### What Worked Exceptionally Well (In the Demos)

**Scrubbing values.** In Victor's JavaScript demo, you can click on a
numeric literal (like `30` in `circle(30)`) and drag left or right to
change the value, with the canvas updating in real time. This means
parameter exploration is a direct manipulation gesture, not an
edit-recompile cycle. You feel the relationship between the number and
the output.

**Seeing state over time.** Victor's Mario-like platformer demo shows
not just the current frame but a ghost trail of previous positions. His
circuit simulator shows voltage at every node simultaneously. His
algorithm animator shows the data structure at every step of the sort.
The insight: **time should be a spatial dimension you can see, not a
dimension you must replay mentally.**

**The "why" interaction.** In Victor's "Learnable Programming" essay,
he proposes that clicking on a variable should show you where it was
defined, where it was modified, and what values it took — all
visually, inline, without leaving the code. This is the "explain"
operation Nomi has adopted as a product promise, and Victor
articulated it a decade before it appeared in programming language
design documents.

**Spatial layout of execution.** Victor's demos often arrange outputs
spatially to reveal structure: a function's outputs for different
inputs are shown side by side; a loop's iterations are shown in a
grid; an algorithm's steps are shown as a flipbook. The visual layout
conveys information that a single "final output" view cannot.

**The "context" principle.** Code should be editable in the context of
its output. You should see what `circle(50)` draws AS you type `50`,
not after you finish the file and run it. This is the principle Light
Table tried to implement and Swift Playgrounds partially achieved.

### What Failed (In the Sense of Not Being Implemented)

**None of these demos became products.** Victor's work was explicitly
research and provocation, not product development. But the fact that
15 years later, no mainstream programming environment implements all of
these ideas is itself a data point. Why?

**The gap between demo and generality.** Victor's demos work for the
specific programs they demonstrate. Generalizing the "scrub a numeric
literal" feature to any numeric literal in any program requires the
editor to understand the semantics of every expression — which values
are numbers, which numbers are safe to change, how changing this
number affects program flow. This is not a UI problem; it is a language
semantics problem.

**The integration cost.** Victor's demos assume the editor has deep
knowledge of the language runtime — the canvas drawing API, the game
loop, the data structure internals. Building this integration for a
general-purpose language is a massive engineering effort. Each language
feature needs a visual counterpart. Most language designers don't
design the visual experience alongside the language semantics.

**The "what about everything else" problem.** Scrubbing numbers and
seeing canvas output works for creative coding. But what about database
queries? What about network requests? What about concurrent processes?
The demos focus on domains with clear visual outputs, but most
programming involves invisible abstractions (data flowing through
services, state machines transitioning, data structures being indexed).
Making these visible is harder than making a circle's radius visible.

**The tooling monoculture lock-in.** Victor's vision requires an
integrated editor-runtime-visualizer that is tightly coupled to the
language. This is the Smalltalk model, and it suffers from Smalltalk's
problem: you can't use your preferred editor, your preferred version
control, your preferred build system. The all-in-one environment is
powerful but isolating.

### Key Structural Insight for Nomi

Victor's demos articulate the destination. The path is: **make the
runtime produce structured trace data, then build views over that data
that answer specific questions.** The "scrub a number" interaction is a
view over the parameter space of a function. The "see state over time"
interaction is a view over the execution history of a variable. The
"why" interaction is a view over the dependency graph of a value.

Nomi should build the trace infrastructure FIRST (every execution
produces inspectable trace records) and the visual interactions SECOND
(views over trace records that answer user questions). The mistake is
building the visual interaction without the trace infrastructure —
that is what makes the demos hard to generalize. The trace
infrastructure makes the interactions general because every view is a
query over a standard trace format.

---

## 10. Elm's Debugger — Time-Travel Debugging

### The Core Interactive Insight

Elm's debugger (2016, Evan Czaplicki) introduced time-travel debugging
to web development: **every state transition in an Elm application is
recorded, and the debugger allows you to step backward and forward
through the entire application history.** You can pause, rewind, replay,
and inspect any state the application was ever in.

The architectural insight: time-travel debugging is possible because
Elm enforces a strict model-update-view architecture. State changes
flow through a single `update` function: `(state, action) -> state`.
Every action is a value, and every state is a value. The debugger
records the stream of actions and the stream of states, and replaying
history is just re-applying the `update` function to the recorded
actions.

### What Worked Exceptionally Well

**The import/export of debug histories.** You can export the debug
history as a file, send it to a colleague, and they can replay your
exact user session. This is a superpower for bug reproduction. Instead
of "I clicked the button and something weird happened — can you
reproduce it?", you send the debug history and your colleague sees
exactly what you saw.

**The message-as-value design.** Because Elm actions are plain values
(`Increment`, `Decrement`, `SetName "Alice"`), they serialize and
deserialize trivially. The debugger doesn't need to instrument opaque
function calls or capture mutable state — it just records the message
stream. The same property that makes Elm's architecture testable makes
it debuggable.

**The slider for time.** The debugger's primary UI is a slider that
moves through application history. Drag left to go back in time, drag
right to go forward. This makes time a tangible dimension you can
explore. The slider shows thumbnails of the application state at each
point, so you can visually scan for the moment things went wrong.

**The explicit "debug mode" flag.** Elm's debugger is compiled into
the application with `elm make --debug`. In production builds
(`--optimize`), the debugger is stripped out entirely. This is the
right separation: the trace infrastructure exists at development time,
and the overhead is removed at production time. No production
performance penalty for trace support.

### What Failed or Caused Persistent Friction

**The scope limitation to Elm's architecture.** Time-travel debugging
works because every state change goes through one function. If your
application has side-effecting code outside the `update` function
(direct DOM manipulation, `setTimeout`, WebSocket handlers that bypass
the message loop), the debugger can't see it. The debugger assumes a
discipline that not all Elm code follows, and that no JavaScript or
TypeScript code follows.

**Ports are opaque to the debugger.** Elm's `port` system (for
interacting with JavaScript) is a black box to the debugger. Data
flowing in through ports is recorded as a raw value with no provenance.
Data flowing out through ports disappears from the trace. This is
correct (the debugger can't instrument JavaScript), but it creates a
blind spot at exactly the boundary where many bugs occur.

**The debugger's performance ceiling.** Recording every state for a
long-running application with frequent updates consumes memory. The
debugger has a configurable history length, but the default is
surprisingly small. Long debugging sessions require management of the
trace buffer.

**The debugger is tied to the browser.** Elm compiles to JavaScript,
and the debugger runs in the browser as part of the Elm runtime's
development mode. There is no command-line debugger, no CI integration,
no headless replay. The debugger is a browser artifact.

**The "what changed?" question is only partially answered.** The
debugger shows you that state changed from `{count: 3}` to `{count:
4}`, and it shows you that the message was `Increment`. But it doesn't
explain WHY `Increment` was sent — which view element was clicked,
which timer fired, which subscription produced the message. The
provenance chain stops at the message.

### Key Structural Insight for Nomi

Elm proves that **time-travel debugging requires architectural
constraints on how state changes.** Nomi should adopt the same
principle: state transitions that flow through identifiable boundaries
(pipeline stages, block invocations, constraint checks) can be traced.
State transitions that happen opaquely (direct mutation of shared state,
untracked side effects) cannot.

The import/export of debug histories is a capability Nomi should
support from day one. A Nomi trace should be a serializable value that
can be saved, shared, and replayed. The `explain` operation on a
binding should show the history of values that binding took, not just
the current value.

The explicit opt-in to tracing (`--debug` vs `--optimize`) is the right
model. Nomi should support trace collection in development/interactive
mode with near-zero overhead for production compilation. The
"always-on tracing" of Darklang is aspirational but carries a
performance cost that not all contexts can bear.

---

## 11. Cross-Language Synthesis

### 11.1 Structural Invariants — Patterns Across All Successful Interactive Systems

Seven patterns appear in every successful interactive programming
system studied here. These are not opinions — they are constraints
that any interactive system must satisfy to work.

**1. The separation of interactive protocol from language runtime.**
Jupyter's kernel protocol, Racket's REPL server, LSP — every
successful system separates the interactive surface from the execution
backend. The protocol defines what can be asked (execute, inspect,
complete) and what can be returned (result, error, display). The
language runtime implements the protocol. This separation allows
frontends to evolve independently of language versions.

**2. Names as the unit of dependency.** Every cell in Pluto, every cell
in Observable, every module binding in Racket — the dependency
tracking that enables smart re-execution works by tracking NAMES. "Cell
B depends on variable `x` which is defined in cell A." This requires
that the system can statically extract variable references without
executing the cell. The granularity of the name (whole variable?
field path? element?) determines the granularity of the dependency
graph.

**3. Execution order derived from the dependency graph, not from
document order.** Pluto and Observable both derive execution order from
the dependency graph. Jupyter derives it from the user's manual
actions. The Jupyter model creates hidden state; the Pluto/Observable
model eliminates it. The derived-order model requires the dependency
graph to be computable statically, before execution.

**4. Values displayed in context, not in a separate output pane.** Light
Table's inline values, Swift Playgrounds' margin annotations, Darklang's
live values in the editor, Smalltalk's inspector — the value is shown
next to the code that produced it. This collapses the distance between
"the program" and "the output" to zero. The unit of display is the
expression, not the file or the cell.

**5. History as a first-class dimension.** Elm's time-travel debugger,
Swift Playgrounds' value history, Darklang's request traces — these
all recognize that the current value is not enough. The user needs to
see how the value CHANGED over time. History is not a log file — it
is an interactive timeline.

**6. The ability to inspect inside values.** Smalltalk's
inspector, Jupyter's rich display, Racket's structure inspector — all
allow the user to open a value and see its internal structure. A
collection shows its elements. An object shows its fields. A function
shows its definition. This is the "drill down" interaction that turns
a value from an opaque token into an explorable structure.

**7. Error context preserved across the interactive boundary.** Rust's
diagnostic spans, Racket's contract blame, Darklang's trace-on-404 —
these all ensure that when something fails, the error report carries
enough context (source location, call chain, input values) for the
user to understand WHY it failed. The interactive boundary should
amplify diagnostic information, not suppress it.

### 11.2 Genuine Design Forks — Where Systems Made Irreconcilable Choices

Seven forks where systems chose different paths, and both paths have
merit.

**1. Sequential vs. topological execution.**
Jupyter executes cells in the order the user runs them. Observable
executes cells in topological order of the dependency graph. The
Jupyter model gives the user more control (execute cell 5 before cell
2 if you want). The Observable model gives the user more correctness
(no hidden state). Neither is universally better. The fork depends on
whether the user's mental model is "I am building a computation step
by step" (Jupyter) or "I am declaring relationships that the system
should maintain" (Observable).

**2. File-based vs. image-based source of truth.**
Smalltalk stores the program as a live image. Every other system stores
the program as text files. The image model allows edit-continue, live
inspection of everything, and no disconnect between code and runtime.
The file model allows version control, collaboration, and deterministic
builds. The image model lost the industry, but it lost for operational
reasons (version control, CI/CD) not because the interactive experience
was inferior. The interactive experience of image-based development
remains superior.

**3. Always-on tracing vs. opt-in tracing.**
Darklang traces every execution automatically. Elm traces only in debug
mode. The always-on model makes every execution inspectable but
imposes a permanent overhead. The opt-in model has no overhead in
production but requires the user to anticipate which executions they
want to trace. The fork is about the cost/coverage tradeoff.

**4. Language-integrated vs. protocol-separated interactivity.**
Smalltalk and Darklang integrate the interactive experience into the
language runtime. Jupyter and LSP separate the interactive protocol
from the language. The integrated model allows deeper interactivity
(the runtime knows what a "cell" is). The separated model allows
cross-language tooling (one editor, many languages). The fork is about
depth vs. breadth.

**5. Named cells vs. positional cells.**
Observable and Pluto require every cell to have a name. Jupyter allows
anonymous cells. Named cells create a namespace for dependency tracking.
Positional cells are simpler (type code, run it). The fork is about
whether the overhead of naming is worth the benefit of dependency
tracking.

**6. Single-definition vs. redefinition allowed.**
Pluto enforces that each variable name is defined in exactly one cell.
Jupyter and Observable allow redefining a variable in a later cell.
Single-definition enables deterministic dependency resolution.
Redefinition enables exploratory iteration. The fork is about whether
the system privileges correctness or exploration.

**7. Visual editor vs. text editor.**
Darklang uses a node-and-edge visual editor. Smalltalk's browser is a
list-of-methods editor, not a text file editor. Every other system
uses text files. Visual editors make structure visible and
discoverable. Text editors make editing fast and support standard
tooling (git, grep, diff). The fork is about the editor modality vs.
the tool ecosystem.

### 11.3 The "Notebook vs. REPL vs. Live Editor" Design Space

These three modes are not competing alternatives. They answer
different questions in the interactive workflow, and they compose.

| Mode | Core question | Best for | Weakness |
|------|---------------|----------|----------|
| **REPL** | "What does this expression evaluate to?" | Quick exploration, library discovery, one-shot computation | No persistence, no narrative, no data context |
| **Notebook** | "What is the story of this analysis?" | Data exploration, teaching, reproducible research | Hidden state (Jupyter), recomputation cost (Pluto), flat namespace (Observable) |
| **Live editor** | "What does my program look like as I build it?" | Creative coding, UI development, algorithm visualization | Requires deep language integration, doesn't scale to large programs |

**When each mode shines:**

- **REPL shines** when the user has a specific question ("what does
  `str.split` return?") and needs an immediate answer. The REPL is
  a query tool, not a composition tool.

- **Notebooks shine** when the user is building a narrative around
  data — loading, cleaning, transforming, visualizing, interpreting.
  The notebook preserves the exploration path so it can be shared,
  reproduced, and extended.

- **Live editors shine** when the user is building something visual or
  interactive — a UI, a game, a visualization — and needs to see the
  output evolve as the code changes. The live editor collapses the
  code-output loop to zero.

**How they compose:**

The ideal Nomi interactive experience should blend all three:
- A **live editor** view for pipeline construction, showing
  intermediate values at each stage
- A **REPL** view for quick one-off queries within a notebook context,
  sharing the notebook's namespace (like Racket's `,enter`)
- A **notebook** view for narrative structure, with named cells that
  form a dependency graph

The composition insight: these are VIEWS over the same underlying
execution state, not separate tools. The user should move fluidly
between them.

### 11.4 Reactive Execution Models Compared

| Model | System | Execution trigger | Dependency tracking | Staleness detection |
|-------|--------|-------------------|---------------------|---------------------|
| **Manual sequential** | Jupyter | User runs each cell | None (user's responsibility) | None |
| **Static topological** | Pluto, Observable | Automatic on edit | Static name analysis | Yes (downstream recompute) |
| **Value-aware topological** | Pluto | Automatic on edit | Static name analysis + value comparison | Only if value changed |
| **Live keystroke** | Light Table | Every keystroke | Expression tree analysis | Re-eval on any change |
| **Explicit snapshot** | Swift Playgrounds | User clicks "run to line" | Manual breakpoint | Manual |
| **Message-stream** | Elm Debugger | On each message | Architecture-enforced | Replay on demand |

**Nomi's target:** A hybrid of static topological + value-aware
optimization. Each interactive unit (cell, pipeline stage) declares its
inputs and outputs by name. The dependency graph is computed
statically. On edit, downstream units are marked stale. But if
re-evaluation produces the same value, further downstream units are NOT
recomputed (value-aware optimization). The user can also opt for
manual execution (like Jupyter) as an escape hatch for expensive
computations.

### 11.5 State Visibility — How Much Program State Should Be Visible?

The systems studied fall on a spectrum:

```
All state invisible <---> All state visible
  (traditional          (Smalltalk
   compiler)             inspector)
```

| Point on spectrum | System | What's visible | The cost |
|-------------------|--------|----------------|----------|
| Nothing visible | Traditional compiler | Only what you `print()` | No overhead, no help |
| Final result visible | Standard REPL | The last expression's value | No history, no intermediates |
| Named values visible | Pluto | The value of each named cell | Overhead of tracking per-cell |
| All expression values | Light Table | Every expression's value | Significant eval overhead |
| All object state | Smalltalk | Every field of every object | Image size, performance |
| All execution history | Elm Debugger, Darklang | Every state at every step | Memory, performance |

**Nomi's position:** Between "named values visible" and "all expression
values." Pipeline stages should default to showing their output value.
Bindings should show their current value. Blocks should show what they
produced on last execution. Full trace history should be available on
demand (the `explain` operation) but not shown by default. The user
should be able to toggle between "show me the current state" (summary
view) and "show me everything that happened" (trace view).

The design principle: **show the state that answers the user's current
question, and make the rest one click away.** Don't show everything by
default (information overload). Don't hide everything by default (no
help). Show the current value at each named boundary, and provide
`explain` for the full trace.

### 11.6 Time-Travel and Traces — Recording Execution for Inspection

Every system studied that supports time-travel debugging imposes a
structural constraint on the program:

| System | Structural constraint | Enables |
|--------|----------------------|---------|
| Elm | `(state, msg) -> state` pure update function | Record stream of msgs, replay by re-applying |
| Darklang | HTTP handlers with traced I/O calls | Record inputs + call tree, replay by re-executing |
| Redux DevTools | `(state, action) -> state` reducer | Same as Elm |
| Smalltalk | Image snapshot + change log | Restore image, replay changes |

The invariant: **time-travel requires that state transitions are
values that can be recorded and replayed.** You cannot time-travel
through code that mutates opaque state or calls impure functions with
no record of their side effects.

For Nomi, this means:
- Pipeline stages should record their input and output values
- Block invocations should record their entry state and exit state
- Constraint checks should record the value checked and the result (pass/fail)
- Bindings should record their value history

Each of these is a trace event. A trace is a sequence of trace events.
`explain` renders a trace as an inspectable structure.

### 11.7 The "Explain" Button — What Should Happen When the User Asks "Why?"

This is the core question for Nomi's interactive design. The systems
studied provide different answers:

| System | "Explain" means | Output |
|--------|----------------|--------|
| Rust (`rustc --explain`) | "Explain this error code" | Prose explanation with examples |
| Smalltalk (inspector) | "Show me this object's internals" | Inspector window on the object |
| Pluto (stale cells) | "Why did this cell recompute?" | Highlight changed dependencies |
| Elm Debugger | "How did we get to this state?" | Message list with state diffs |
| Darklang (trace) | "What happened during this request?" | Full trace with all values |
| Observable | "What does this cell depend on?" | Dependency graph highlighting |
| Python (`%debug`) | "Drop into post-mortem debugger" | Stack trace with local variables |

For Nomi, `explain` should be a **context-sensitive operation that
renders the trace record most relevant to the user's current
selection.** If the user selects a binding, `explain` shows the value
history. If the user selects a pipeline stage, `explain` shows the
input, output, and any constraint violations. If the user selects an
error, `explain` shows the trace up to the error with blame
assignment. If the user selects a value, `explain` opens an inspector
on that value.

The output of `explain` is not a string. It is a structured trace view
that the frontend renders — text, table, graph, or interactive
widget depending on the value type and the user's question.

### 11.8 Anti-Patterns — Interactive Design Mistakes That Consistently Hurt Usability

1. **The silent state drift.** Jupyter's core flaw: the notebook shows
   code and output, but the kernel state may not match either. Always
   show whether the displayed output matches the current kernel state.
   Stale outputs should be visually marked.

2. **The output-as-text assumption.** REPLs that only display strings
   throw away structure. Values should carry their representations
   (text, table, image, interactive) and the frontend should choose the
   best representation for the medium.

3. **The "run everything" hammer.** Systems that recompute everything
   on every change (Light Table, Observable on cold load) waste
   computation and user patience. Smart invalidation (only recompute
   what changed and what depends on it) is not optional.

4. **The walled garden.** Darklang and Observable host code on their
   servers. This enables deep integration but prevents local
   development, offline work, and self-hosted deployment. Interactive
   features must work with local execution.

5. **The second syntax trap.** IPython magics (`%timeit`), Observable's
   cell syntax (`viewof`, `mutable`), Pluto's `@bind` — each system
   invents a meta-syntax for interactive operations that exists outside
   the language grammar. These meta-syntaxes grow features, accrete
   syntax, and become a second language. Interactive operations should
   be library functions or protocol messages, not magic syntax.

6. **The binary format trap.** `.ipynb` JSON with base64 outputs,
   Smalltalk image files, Swift playground bundles — binary or
   semi-binary formats are hostile to version control, diffing, and
   code review. The source representation should be plain text. Outputs
   and traces should be separate files or computed on load.

7. **The trace-everything cliff.** Always-on tracing (Darklang) works
   until it doesn't — at scale, managing trace volume becomes the
   primary engineering challenge. Tracing should be configurable: what
   to trace, how much to retain, when to discard.

8. **The discoverability cliff.** DrRacket, Smalltalk, and Light Table
   all pack enormous power into their environments, but discovering
   that power requires learning the environment. Interactive features
   should be visibly discoverable — command palette entries, hover
   tooltips, contextual menus — not hidden behind memorized keybindings
   and menu hierarchies.

---

## 12. Nomi Adopt / Refuse / Adapt

| # | Concept | Source | Verdict | Nomi Application |
|---|---------|--------|---------|------------------|
| 1 | **Kernel protocol separation** | Jupyter | **Adopt** | Separate the interactive protocol (execute, inspect, complete, explain) from the language runtime. Build on the Jupyter kernel protocol rather than inventing a new one. Nomi kernels implement the protocol; frontends (VS Code, web, CLI) consume it. |
| 2 | **Dependency-graph execution** | Pluto, Observable | **Adopt** | Every interactive unit (cell, pipeline stage, block) declares its named inputs and outputs. The runtime derives execution order from the dependency graph. Stale outputs are visually marked. |
| 3 | **Value-aware recomputation** | Pluto | **Adopt** | When a cell's inputs haven't meaningfully changed (same value, not just same source text), skip recomputation of downstream cells. Use structural equality for value comparison. |
| 4 | **Rich MIME-typed output** | Jupyter | **Adopt** | Every value carries display representations (text, table, chart, interactive widget). The frontend renders the best representation for the medium. `explain` renders structured views, not text strings. |
| 5 | **Trace records as runtime output** | Darklang | **Adopt** | Every execution produces a trace: a sequence of events with source spans, input values, output values, and timing. Trace is a standard data structure, not a debug-mode special case. Trace collection is configurable (always-on for interactive, opt-in for production). |
| 6 | **`explain` as context-sensitive trace view** | Rust, Smalltalk, Victor | **Adopt** | `explain` on a binding shows value history. On a pipeline stage shows input/output/constraints. On an error shows the causal trace with blame assignment. On a value opens an inspector. The output is structured data the frontend renders. |
| 7 | **REPL as context window** | Racket (`,enter`) | **Adopt** | The REPL is not a separate global namespace. It is a window into a specific execution context (notebook, module, pipeline). All bindings, contracts, and constraints of that context are active in the REPL. |
| 8 | **Inline value display** | Light Table, Swift Playgrounds | **Adopt** | Pipeline stage outputs and binding values are shown inline in the margin, color-coded by type. This is a view mode, not the only mode — toggleable for users who prefer a separate output pane. |
| 9 | **Cell-as-function model** | Observable | **Adapt** | Adopt the "cell is a function of named inputs" model, but adapt to allow cell-local redefinition for exploration. A cell can shadow a name from an earlier cell; the dependency graph tracks which downstream cells depend on which definition. Shadowed definitions are visually marked. |
| 10 | **Image-based state persistence** | Smalltalk | **Refuse** | The image model (entire running system as a snapshot) creates version-control and collaboration problems that outweigh its interactive benefits. Nomi should use plain-text source with separate trace/state files. |
| 11 | **Visual editor replacing text editor** | Darklang, Smalltalk | **Refuse** | Visual programming editors (node-and-edge graphs, class hierarchy browsers as the primary interface) limit editing bandwidth and break standard tooling. Nomi should use text as the primary editing surface, with visual annotations (values, traces, dependency edges) as overlays on the text. |
| 12 | **Hand-managed execution order** | Jupyter | **Refuse** | Users should not be responsible for tracking which cells need re-execution. The system should derive execution order from the dependency graph. Manual execution ("run this cell now") is a fallback for expensive computations, not the default mode. |
| 13 | **Package management embedded in notebook** | Pluto | **Adapt** | Adopt the principle (notebook carries its own environment declaration) but adapt the mechanism. Nomi notebooks declare dependencies in a standard manifest format (like `pyproject.toml`). The runtime validates the environment on notebook open. |
| 14 | **Time-travel debugger** | Elm | **Adapt** | Adopt the structured-state-change model (state transitions as traceable values) but adapt to Nomi's broader semantics. Not just message-passing architectures — any value flowing through a pipeline or block boundary is a traceable state transition. |
| 15 | **Value scrubbing / direct manipulation** | Bret Victor | **Adapt** | Adopt the concept (direct manipulation of values as parameter exploration) but implement as a frontend view over the trace infrastructure, not as a deep language integration. The "scrub a number" interaction is a query: "what does this function output for nearby inputs?" |
| 16 | **Smart invalidation, not "run everything"** | Light Table (failure) | **Adopt** | Only recompute cells whose dependencies changed. Mark stale cells visually. Allow the user to explicitly trigger recomputation. Never silently recompute expensive cells (I/O, large data loads). |
| 17 | **Fork-and-remix collaboration** | Observable | **Adapt** | Adopt the principle (notebooks are forkable, preserving provenance and attribution) but adapt to work with standard git, not a proprietary platform. A notebook is a git repository with a standard structure. |
| 18 | **Contract/constraint enforcement at interactive boundary** | Racket | **Adopt** | Nomi binding constraints (`x: int > 0`) are enforced when the user interactively rebinds `x` at the REPL or in a notebook cell. The interactive boundary is the MOST checked boundary. Constraint violations produce blame assignments with source spans. |
| 19 | **Export to static, reproducible artifact** | Pluto, Observable | **Adopt** | Every notebook can export to a standalone, runnable artifact (a Nomi script that produces the same outputs in the same order). The export is deterministic and verifiable. |
| 20 | **Meta-syntax for interactive operations** | IPython magics, Observable | **Refuse** | Nomi should not invent a second mini-language for interactive operations. `explain`, `inspect`, `trace` are library functions that operate on trace records, not special syntax. The interactive protocol carries operations as structured messages, not magic strings. |

---

## Sources

- [Jupyter Kernel Protocol](https://jupyter-client.readthedocs.io/en/stable/messaging.html) — The JSON message specification for Jupyter kernels.
- [IPython: A System for Interactive Scientific Computing](https://ipython.org/) — Fernando Perez, 2001-present.
- [Pluto.jl: Reactive Notebooks for Julia](https://github.com/fonsp/Pluto.jl) — Fons van der Plas et al., 2019-present.
- [Pluto: Interactivity and Reactivity](https://plutojl.org/) — Pluto documentation on dependency analysis and reactivity.
- [Darklang: Trace-Driven Development](https://darklang.com/) — Paul Biggar et al., 2017-present.
- [Darklang: The Design of Trace-Driven Development](https://blog.darklang.com/) — Darklang blog, trace architecture posts.
- [Smalltalk-80: The Language and Its Implementation](https://dl.acm.org/doi/book/10.5555/273) — Adele Goldberg and David Robson, 1983.
- [Design Principles Behind Smalltalk](https://www.cs.virginia.edu/~evans/cs655/readings/smalltalk.html) — Dan Ingalls, 1981.
- [The Racket Guide: Interactive Development](https://docs.racket-lang.org/guide/interactive.html) — Racket documentation on the REPL and `,enter`.
- [Scribble: The Racket Documentation Tool](https://docs.racket-lang.org/scribble/) — Matthew Flatt et al.
- [Light Table](https://github.com/LightTable/LightTable) — Chris Granger et al., 2012-2016.
- [Light Table: An IDE for an Interactive Programming Experience](https://www.chris-granger.com/2012/04/12/light-table---a-new-ide-concept/) — Chris Granger, 2012.
- [Eve: Programming Designed for Humans](https://www.chris-granger.com/2014/10/01/beyond-light-table/) — Chris Granger on the transition from Light Table to Eve.
- [Observable: Reactive JavaScript Notebooks](https://observablehq.com/) — Mike Bostock, Jeremy Ashkenas et al., 2017-present.
- [Observable's Not JavaScript](https://observablehq.com/@observablehq/observables-not-javascript) — Observable documentation on the reactive execution model.
- [Swift Playgrounds](https://www.apple.com/swift/playgrounds/) — Apple, 2014-present.
- [Xcode Playgrounds Documentation](https://developer.apple.com/documentation/swift-playgrounds) — Apple.
- [Inventing on Principle](https://www.youtube.com/watch?v=PUv66718DII) — Bret Victor, 2012 (talk).
- [Learnable Programming](http://worrydream.com/LearnableProgramming/) — Bret Victor, 2012.
- [Drawing Dynamic Visualizations](http://worrydream.com/DrawingDynamicVisualizationsTalkAddendum/) — Bret Victor, 2013.
- [Elm Debugger: Time-Travel Debugging](https://elm-lang.org/news/time-travel-made-easy) — Evan Czaplicki, 2016.
- [The Elm Architecture](https://guide.elm-lang.org/architecture/) — Elm documentation.
- [The Next 700 Programming Languages](https://www.cs.cmu.edu/~crary/819-f09/Landin66.pdf) — Peter Landin, 1966.
- [Jupyter Notebooks: The Good, the Bad, and the Ugly](https://www.youtube.com/watch?v=7jiPeIFXb6U) — Joel Grus, 2018 (talk on Jupyter's reproducibility problems).
- [Rust Compiler Error Index](https://doc.rust-lang.org/error_codes/error-index.html) — Rust documentation on structured error codes.
- [Nomi Cross-Language Synthesis](cross_language_synthesis_master.md) — Nomi's existing synthesis document, §5 on explanation normal form.
- [Nomi Diagnostics and Explanations](diagnostics_and_explanations_comparative.md) — Nomi's diagnostic architecture comparison.
- [Nomi Language Foundation](../language/language_foundation.md) — "explain what happened" in the product promise.
