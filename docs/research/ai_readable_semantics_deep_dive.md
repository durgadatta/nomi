# AI-Readable Semantics: How Languages Expose Meaning to Machines

> Status: cross-language comparative research; active synthesis for Nomi design.
>
> Purpose: Study how programming languages make their semantics machine-readable
> for AI tools — LSP servers, analyzers, refactoring engines, AI code assistants
> — and what infrastructure makes a language "AI-friendly" from day one. Extract
> concrete design decisions for Nomi's tooling architecture.

## 1. LSP (Language Server Protocol)

### Core Design Insight for AI Readability

LSP's structural insight is simple and profound: **language intelligence is a
function of the source text, not the editor.** By defining a JSON-RPC protocol
between an editor and a language server, LSP decouples the analysis engine from
every display surface. The editor knows nothing about the language beyond what
file extension maps to which server. The server knows nothing about the editor
beyond what position the cursor is at.

This decoupling is the single most important architectural decision in modern
language tooling. Before LSP, every editor implemented its own C++ parser, its
own Java indexer, its own Python analyzer. The result was N x M integration
effort: N editors times M languages, each pair a bespoke integration. After LSP,
the complexity collapses to M: one server per language, consumed by every
editor. The economics flipped from quadratic to linear.

### Protocol Capabilities: What LSP Makes Machine-Readable

LSP defines a set of **capabilities** that a server can advertise and an editor
can consume. Each capability is a contract: the editor sends a request with a
document URI and a cursor position, the server returns a structured response.

**Diagnostics (`textDocument/publishDiagnostics`):** The server pushes
diagnostics (errors, warnings, hints) when a document changes. The diagnostic
carries a range, a severity level, a message string, and an optional error code.
This is the most fundamental LSP capability — it makes the compiler's error
output available in-editor without the programmer invoking a build step. For AI
tools, diagnostics are the primary signal of "the code is wrong and here is why."

**Completion (`textDocument/completion`):** The server returns a list of
completion items given a cursor position. Each item carries a label, a kind
(function, variable, class, keyword, snippet), optional documentation, and an
optional text edit. The important design choice is that LSP completion is
**position-aware, not token-prefix matching.** The server receives the full
document and cursor position, so it can use type context, scope analysis, and
import resolution to rank suggestions. This is what separates LSP completion
from grep-based completion.

**Hover (`textDocument/hover`):** The server returns formatted documentation for
the symbol at a position. Typically shows type, docstring, and signature. For AI
tools, hover information is a fast path to "what is this thing and what does it
expect?"

**Go-to-Definition (`textDocument/definition`):** The server resolves a symbol
reference to its definition location. This requires full name resolution and
import tracking. The server returns a list of `Location` objects (URI + range).
For AI tools, go-to-definition is the primary mechanism for "follow the chain of
meaning" — understanding what a symbol actually refers to.

**References (`textDocument/references`):** The inverse of go-to-def: find all
uses of a symbol. Requires a cross-file index. Returns a list of `Location`
objects. For AI refactoring, this is essential: "find every call site so I can
change the signature."

**Rename (`textDocument/rename`):** Prepare a rename (validate it is possible)
and execute it (return a `WorkspaceEdit` with all required text changes). This
requires the server to understand alias analysis — distinguishing shadowed
bindings from genuinely distinct symbols.

**Code Actions (`textDocument/codeAction`):** Given a diagnostic, the server
returns a list of `CodeAction` objects, each containing a title, a kind
(quickfix, refactor, source), and an optional `WorkspaceEdit`. This is the
bridge from "your code has a problem" to "here is how to fix it." For AI agents,
code actions are the closest LSP gets to "do the fix."

**Semantic Tokens (`textDocument/semanticTokens/full`):** The server returns
token-level classification of source text: variable, parameter, type, function,
keyword, operator, etc. Each token carries a type index and zero or more
modifier flags (declaration, readonly, static, async). The editor uses these for
syntax highlighting that goes beyond regex-based TextMate grammars.

**Signature Help (`textDocument/signatureHelp`):** When the cursor is inside a
function call, the server returns the active parameter index and the function's
signature. For AI tools, this is a lightweight type-at-point query.

### What Makes a Good LSP Implementation

The difference between a minimal LSP and a good one is not feature count. It is:

1. **Incrementality.** A good LSP server does not re-parse the entire project on
   every keystroke. It caches parsed files, maintains a dependency graph,
   invalidates only what changed, and recomputes only what depends on the
   change. rust-analyzer's "salsa" incremental computation framework is the gold
   standard: every analysis result is a memoized function of a `(file, change)`
   pair, and the framework recomputes the minimal set of affected results.

2. **Error tolerance.** The server must produce useful results even when the
   code has syntax errors. If completion stops working because there is an
   unmatched brace on line 40, the server is useless during editing. Tree-sitter
   is the standard solution (see section 3), but hand-written error-recovery in
   the parser also works (TypeScript's parser does this well).

3. **Cross-file awareness.** Completion that only sees the current file is
   barely better than grep. A good server indexes the project: imports,
   exports, type definitions, trait implementations. rust-analyzer builds a
   crate-level index; TypeScript's tsserver builds a project-level type graph.

4. **Low latency.** LSP is an interactive protocol. Completion results must
   arrive in under 100ms or the editor feels sluggish. rust-analyzer achieves
   this by computing completion candidates incrementally as the user types and
   cancelling stale requests when new input arrives.

5. **Semantic depth, not string matching.** Completion that suggests `x` because
   it starts with `x` is trivial. Completion that suggests `x` because it is the
   only variable of type `Config` in scope is what matters. This requires the
   server to have a type checker, not just a parser.

### Protocol Limitations

**Workspace symbol search is underspecified.** `workspace/symbol` lets the user
search for a symbol by name, but the protocol leaves ranking entirely to the
server. TypeScript's "open symbol" is fast and accurate; many other LSP
implementations return an unsorted list of everything matching the substring.

**Cross-file analysis is optional.** LSP does not require a server to maintain a
project-level index. A server that only parses the open file is LSP-compliant
but nearly useless for real work. The protocol does not standardize how projects
are defined (tsconfig.json, Cargo.toml, package.json), so editor integration
often requires editor-specific glue to discover the project root.

**No standard query language.** LSP provides fixed request types (hover,
definition, references) but no general query interface. If an AI tool wants to
ask "show me all places where a value of type `Result<T, E>` is constructed,"
there is no standard LSP request for that. The tool must either use
`workspace/symbol` with heuristics or implement its own query over the server's
index.

**Refactoring is limited to rename.** LSP's built-in refactoring is
`textDocument/rename` only. Everything else (extract function, inline variable,
change signature) requires `textDocument/codeAction` with custom action kinds,
which every server implements differently.

### Key Structural Insight for Nomi

Nomi should build an LSP server that exposes **the pipeline**, not just the
final result. When a programmer hovers on a piece of Nomi syntax, the hover card
should optionally show which lowering rule produced the underlying Python AST —
not just the type. The `textDocument/codeAction` response should include an
action "show desugaring" that jumps to the pipeline stage representation for the
current selection.

The LSP server should be a first-class artifact in the Nomi toolchain, not an
afterthought. It should share the parser, type checker, and constraint solver
with the compiler — there should be one analysis engine, consumed by both the
compiler and the LSP server, with the LSP server exposing that engine's results
over JSON-RPC.

---

## 2. Typed ASTs and Source Maps

### Core Design Insight for AI Readability

A parse tree answers "what does this text look like?" A typed AST answers "what
does this text mean?" The distance between those two answers is the entire
compiler middle-end. For AI tools, the parse tree is insufficient — knowing that
`x` is an `Identifier` node tells you nothing about what `x` evaluates to. The
typed AST is the minimum viable representation for any tool that needs to reason
about program behavior.

### TypeScript's `ts.TypeChecker` as a Queryable Type Database

TypeScript's architecture is the clearest example of a typed AST designed for
tool consumption. The `ts.TypeChecker` API is not a compiler internal that
happens to be public — it is the primary interface through which every
TypeScript tool (tsserver, ESLint, Prettier, language service plugins) interacts
with the type system.

The key design decisions:

- **Every `ts.Node` has a `ts.Type` queryable through `typeChecker.getTypeAtLocation(node)`.**
  The type checker maintains a mapping from syntax node to inferred type. Tools
  do not walk type structures; they query types by AST node.

- **The type checker models structural types, not just declared types.**
  `{name: string, age: number}` is a real type in the checker, not sugar for
  `object`. This means tools can ask "does this expression have a `name`
  property?" and get an answer without reasoning about nominal type hierarchies.

- **The symbol table is separate from the AST.**
  `ts.Symbol` objects represent declarations (variables, functions, classes,
  modules). The AST is the syntax tree; the symbol table is the semantic
  meaning. `typeChecker.getSymbolAtLocation(node)` bridges syntax to semantics.

- **The language service is the public API.**
  `ts.LanguageService` wraps the type checker with LSP-style queries:
  `getCompletionsAtPosition`, `getQuickInfoAtPosition`, `getDefinitionAtPosition`.
  TypeScript's tsserver is essentially a JSON-RPC wrapper over
  `ts.LanguageService`.

For AI tools, the TypeScript model is ideal: query the type of any expression,
the symbol of any identifier, the signature of any call. Every question an AI
agent might ask about a piece of code has a one-function answer.

### Rust's HIR/MIR and rust-analyzer's Approach

Rust's compiler has a multi-layer IR stack: AST (raw parse) → HIR (high-level
IR, desugared but still type-aware) → THIR (typed HIR) → MIR (mid-level IR,
control-flow graph) → LLVM IR.

rust-analyzer does not use the Rust compiler's IR. It builds its own simplified
representation: a **syntax tree** (lossless CST via rowan, not a lossy AST), a
**name resolution** layer (imports resolved, paths expanded), and a **type
inference** layer based on chalk (a recursive solver implementing Rust's trait
system). The key architectural difference from TypeScript is that rust-analyzer
is **lazy and incremental**: it only computes the information that is needed for
the current query, and it caches everything via the salsa framework.

The important lesson for Nomi: **the analysis engine for tooling does not need
to be the same as the analysis engine for compilation.** They need to agree on
semantics, but they can have different architectures optimized for different
access patterns. The compiler needs throughput; the tooling server needs
latency. rust-analyzer can answer "what is the type of this expression?" in
milliseconds because it only computes types for the requested expression and its
dependencies, not for the entire crate.

### Source Maps for Debugging and Analysis

Source maps solve a deceptively simple problem: "this bytecode position
corresponds to which source position?" The problem is deceptively simple because
in any multi-stage compiler, source locations must be propagated through every
transformation. If a desugar pass replaces `for x in y: body` with a while-loop,
the generated while-loop nodes must carry the source span of the original `for`
expression. Otherwise, a runtime error inside the loop body will point to
generated code that the user never wrote.

JavaScript source maps (the V3 spec) are the de facto standard. They map
positions in generated JavaScript to positions in original source (TypeScript,
CoffeeScript, minified JS, etc.). The format is a JSON file with a base64 VLQ
encoding of a mapping table. The design insight is that source maps are **a
separate artifact from the generated code**, not embedded in it. This means
source maps are optional — production code omits them; development code includes
them.

For Nomi, the multi-stage pipeline (grammar → surface AST → Python AST →
desugared AST → interpreter) creates a source map problem: an error at the
interpreter level needs to reference the original Nomi source span, not the
lowered Python AST position. The solution is span propagation: every
transformation must copy or compose source spans from its inputs to its outputs.
Nomi's `SourceSpan` (in `prototype/syntax/surface.py`) already captures
`file, line, col, end_line, end_col` and is attached to `SurfaceNode` instances
via the `@captures_span` decorator. This infrastructure must be extended so
every desugar pass propagates spans through its generated AST.

### What Typed ASTs Enable That Parse Trees Cannot

| Operation | Parse Tree | Typed AST |
|-----------|-----------|-----------|
| Rename variable | Guess via text matching | Know exactly via binding resolution |
| Find all callers of `f()` | Find all `f(` text | Find all calls with same definition |
| Extract function | Guess what is used | Know free variables, return type |
| Inline variable | Must parse both sites | Know the variable is single-assignment |
| Change parameter order | Must find all call sites manually | Enumerate all call sites, show diff |
| Add optional parameter | Cannot check for breakage | Show every call site with argument count |
| Auto-import | Cannot know what to import | Knows exports, types, re-exports |

The pattern: **precise refactoring requires semantic information that the parse
tree does not contain.** The parse tree tells you where tokens are; the typed
AST tells you what tokens mean. Any tool that does not have access to the typed
AST is limited to text-level operations that can be incorrect (renaming a local
variable `x` should not rename a struct field also named `x` in the same file).

### Key Structural Insight for Nomi

Nomi's Python AST substrate is both a convenience and a limitation. The
convenience: Nomi gets Python's AST tooling for free (ast.dump, ast.unparse,
ast.NodeVisitor). The limitation: Python's AST has no type information, no
binding resolution, no import tracking beyond raw imports. A Nomi LSP server
built purely on Python AST cannot answer "what type is this expression?" without
adding a type-checking layer on top.

Nomi should define a **semantic model** that sits above the Python AST: a typed
AST or a semantic index that maps AST nodes to types, bindings to definitions,
and call sites to callees. This model does not need to be as sophisticated as
TypeScript's type checker initially, but its existence from day one prevents the
"parse-tree-only" tooling trap.

---

## 3. Tree-sitter

### Core Design Insight for AI Readability

Tree-sitter solved a problem that parser combinator libraries and hand-written
recursive descent parsers systematically failed at: **produce a useful parse tree
even when the input is malformed.** This is not a bonus feature. It is the
defining requirement for editor tooling.

A parser that fails on the first syntax error produces no tree, which means the
editor gets no syntax highlighting, no folding, no symbol outline, and no
selection expansion. During editing, code is routinely malformed — the user is
typing, brackets are unbalanced, a newline is missing, a keyword is incomplete.
If the parser gives up, the editor gives up.

Tree-sitter's solution is an **incremental GLR parser with automatic error
recovery.** When the user edits a character, Tree-sitter re-parses only the
affected region, reuses the unchanged parts of the parse tree, and inserts error
nodes for syntax that does not match any rule. The error nodes are explicit in
the tree: `(ERROR (identifier) (identifier))` means "two identifiers were found
where a statement was expected." The editor can then highlight the error nodes
differently (usually with no highlighting, falling through to the base text
color).

### Error Recovery in Incremental Parsing

Tree-sitter's error recovery strategy is simple and effective:

1. **Insert error nodes.** When the parser cannot match any production at a
   position, it creates an `ERROR` node, skips one token, and tries again. This
   means every token ends up in the tree — nothing is dropped.

2. **Prefer structural nodes.** When parsing a block, Tree-sitter prefers to
   parse as many statements as possible, even if some are erroneous. A block
   with three statements where the second has a syntax error produces:
   `(block (stmt) (ERROR) (stmt))` — preserving the surrounding structure.

3. **Incremental re-parsing.** On edit, Tree-sitter walks the existing tree to
   find the changed range, creates a new tree for that range, and splices it
   into the existing tree. The unchanged subtrees are reused by pointer
   identity. This is what makes Tree-sitter fast enough to run on every
   keystroke — it does O(log n) work, not O(n).

### How Tree-sitter Grammars Differ from Parser Combinator Grammars

Tree-sitter grammars are **concrete syntax tree (CST) grammars**, not abstract
syntax tree (AST) grammars. Every token, every keyword, every punctuation
character must appear in the grammar and produces a node in the tree. A Lark
grammar might skip commas and semicolons; a Tree-sitter grammar must include
them as named or anonymous nodes.

This has a profound implication for AI readability: **Tree-sitter trees are
lossless.** You can reconstruct the exact source text from the tree (modulo
whitespace in some implementations). This means the tree can be used for
formatting, refactoring, and code generation without losing trivia (comments,
whitespace, semicolons).

The tradeoff: CST grammars are more verbose and harder to maintain than AST
grammars. They must handle every token placement, every optional delimiter,
every alternate syntax. But this verbosity is the cost of robustness — a CST
grammar that handles every input is more valuable for tooling than an AST
grammar that rejects malformed input.

### What Tree-sitter Tells Us About Designing Syntax for Toolability

Tree-sitter's success (Neovim, Helix, Zed, Emacs, GitHub, VS Code integration)
reveals several design constraints on syntax:

1. **Avoid significant whitespace that varies by context.** Python's indentation
   is notoriously hard to parse in isolation — an `if` block's indentation
   structure depends on the preceding statement. Tree-sitter's Python grammar
   uses external (hand-written) scanner code for indentation, which works but is
   significantly more complex than the grammar for brace-delimited languages.

2. **Prefer delimited blocks over indentation-based blocks.** Brace-delimited
   blocks (`{}`) are trivial to parse incrementally. Indentation-based blocks
   (`: + indent`) require the parser to track column positions across lines,
   which complicates incremental re-parsing.

3. **Keywords should be unambiguous.** If a keyword can also be an identifier
   (like `async` in Python before 3.5), the grammar must handle both contexts.
   Tree-sitter's word-token optimization makes this fast, but the grammar
   complexity remains.

4. **Expression syntax should be composable without ambiguity.** Operators with
   changing precedence (like `!!` for non-null assertion in TypeScript, which
   has different precedence than `!` negation) create grammar conflicts that
   require parser hacks.

5. **Each syntactic construct should produce a unique, predictable node type.**
   If two constructs produce the same node type (e.g., function declarations
   vs. arrow functions both producing `(function ...)` in Tree-sitter), tools
   must inspect deeper tree structure to distinguish them. Distinct syntax
   should produce distinct tree nodes.

### Key Structural Insight for Nomi

Nomi should ship a Tree-sitter grammar as part of its core language definition,
not as an optional community contribution. The Tree-sitter grammar and the Lark
parser grammar should agree on the language's syntax, but they serve different
roles: the Lark grammar is the canonical specification used by the compiler; the
Tree-sitter grammar is the robust, error-tolerant parser used by editors. Nomi's
design should avoid syntax features that are hard to express in Tree-sitter
(complex indentation rules, context-dependent tokenization).

Nomi's existing Lark grammar (in `prototype/grammar/layers/`) is already
factored into layers. A parallel Tree-sitter grammar could mirror this layering
with a `grammar.js` that composes scanner functions and rule definitions
corresponding to the same layers. The key is maintaining semantic equivalence:
the Tree-sitter tree and the Lark tree should agree on the shape of valid
syntax, even though Tree-sitter includes error nodes that Lark does not.

---

## 4. Semantic Tokens and Syntax Coloring

### Core Design Insight for AI Readability

Semantic tokens are the simplest LSP capability with the highest cognitive
impact. The idea: instead of regex-based syntax highlighting (which only
distinguishes keywords, strings, comments, and numbers), the compiler
classifies every token with its semantic role. A variable is colored
differently from a parameter; a mutable binding is colored differently from an
immutable one; a type is colored differently from a value.

The effect is not cosmetic. Semantic coloring reduces the time to visually
parse code by making structure instantly apparent. A function parameter and a
local variable may both be identifiers as far as TextMate is concerned, but to
the programmer they are different categories with different rules. Semantic
tokens make that categorization visible.

### LSP Semantic Tokens vs TextMate Grammars

TextMate grammars (the traditional approach, used by VS Code's built-in
highlighting) operate on **regular expressions over source text.** They match
patterns like `\b(function|const|let|var)\b` and assign scopes like
`keyword.control`. They have no understanding of scope, binding, or type.

LSP semantic tokens operate on **compiler output over the parse tree.** The
server classifies each token by its position in the AST:

- Is it a declaration or a reference?
- Is it a variable, parameter, type, function, or method?
- Is it mutable, readonly, static, or async?
- Is it a builtin, a global, or an import?

The server returns a compact integer encoding of the token types and modifiers,
and the editor maps those integers to colors and font styles via theme rules
(`editor.semanticTokenColorCustomizations`).

The two systems are composable: TextMate provides the baseline (keywords are
bold, strings are green, comments are gray), and semantic tokens override or
augment specific tokens (parameters are italic, mutable variables have an
underline, types are teal).

### What Information Semantic Coloring Should Convey

The best semantic token implementations (rust-analyzer, TypeScript, Haskell LSP)
converge on a shared palette of distinctions:

**Category (token type):**
- `variable` — a value binding
- `parameter` — a function parameter
- `type` — a type name (class, struct, enum, interface)
- `function` — a function or method name
- `keyword` — a language keyword (already handled by TextMate)
- `operator` — an operator token
- `string`, `number`, `comment` — literals (already handled by TextMate)

**Modifiers (flags that modify the base type):**
- `declaration` — this is where the name is defined
- `readonly` — this binding is immutable
- `mutable` — this binding can be reassigned
- `static` — this is a static method or property
- `abstract` — this is an abstract method
- `deprecated` — this identifier is deprecated
- `async` — this function is async
- `generic` — this is a type parameter (e.g., `T` in `List<T>`)
- `builtin` — this is a built-in (e.g., `int`, `str` in Python)
- `unresolved` — this reference could not be resolved (distinct coloring for
  errors)

The convergence on this palette is not accidental. These distinctions correspond
to **semantic categories that programmers already think about** when reading
code. The coloring makes those categories visible at a glance, reducing the
working memory required to track which names are what.

### How Semantic Coloring Reduces Cognitive Load

A function signature like this in a typical monochrome editor:

```
def process(config, items, callback):
    for item in items:
        result = callback(config, item)
        if result is not None:
            yield result
```

With semantic tokens:

- `config` (parameter) appears in one color — you know it comes from outside
- `items` (parameter) appears in the same color
- `callback` (parameter, callable) appears with the callable modifier
- `item` (local variable) appears in a different color — you know it's scoped
- `result` (local variable) appears in the same local color
- `yield` (keyword) appears in keyword color

The visual distinction between parameters and locals alone saves the reader from
having to trace scopes mentally. The distinction between callable and non-callable
names prevents the common error of trying to call a non-function.

### Examples from Production LSPs

**rust-analyzer:** The most comprehensive semantic token implementation.
Distinguishes: `variable`, `parameter`, `type`, `function`, `method`, `macro`,
`lifetime`, `namespace`, `enumMember`, `property`. Modifiers: `mutable`,
`unsafe`, `static`, `async`, `consuming`, `callable`. A `&mut self` parameter
carries both `parameter` and `mutable`, coloring it distinctively.

**TypeScript:** Distinguishes `variable`, `parameter`, `type`, `function`,
`method`, `class`, `interface`, `enum`, `enumMember`, `property`, `typeParameter`.
Integrates with VS Code's TextMate fallback so that unresolved references
(wrongly spelled imports, shadowed names) get a distinct error color.

**Haskell LSP (haskell-language-server):** Distinguishes `type`, `typeVariable`,
`module`, `function`. Modifiers: `dataConstructor`, `typeClass`, `imported`.
Type constructors (`Just`, `Left`) are colored differently from type classes
(`Eq`, `Show`), which are colored differently from type variables (`a`, `b`).
This is critical for reading Haskell, where the same identifier can be a type
constructor in one context and a value constructor in another.

### Key Structural Insight for Nomi

Nomi's semantic token design should reflect Nomi's own semantic categories:
constrained bindings, block-call parameters, lowering-generated names. A
Nomi-specific semantic token palette might include:

| Token Type | Nomi Meaning |
|-----------|-------------|
| `variable` | A let-binding or val-binding |
| `parameter` | A function parameter |
| `constrainedParameter` | A parameter with a constraint (`x: Int`) |
| `type` | A type name |
| `function` | A function name |
| `blockParam` | A block-call parameter (`\|y\|` in `f(x) do \|y\|: ... end`) |
| `surfaceKeyword` | A Nomi-only keyword (`where`, `match`, `defer`) |
| `loweredName` | A name generated by the lowering step (e.g., `_nomi_where_body`) |

The `loweredName` category is Nomi-specific: it makes visible what the pipeline
generated, helping the programmer distinguish "what I wrote" from "what the
compiler introduced." This is especially valuable when debugging desugar
transformations.

---

## 5. Code Action and Refactoring Infrastructure

### Core Design Insight for AI Readability

The "diagnostic → code action" pipeline is the highest-value interface between a
compiler and a programmer. A diagnostic says what is wrong; a code action says
how to fix it. The structural requirement is that each diagnostic must carry
enough information for a fix to be **mechanically derivable**, not just
human-interpretable. If the diagnostic is "unused variable `x`" and the fix is
"remove the variable declaration," the diagnostic must carry the range of the
declaration, the range of all references (to confirm they are all dead), and a
flag indicating whether the declaration has side effects.

### Rust's `rustfix` for Applying Compiler Suggestions

`rustc --fix` applies machine-applicable suggestions from compiler diagnostics
directly to the source code. The pipeline is:

```
rustc → diagnostics with MachineApplicable suggestions → rustfix → edited source files
```

Each suggestion carries a `Suggestion` struct: a message, a list of
source replacements (span + replacement text), and an applicability level:

- `MachineApplicable` — the suggestion is always correct; apply it automatically
- `MaybeIncorrect` — the suggestion is usually correct; review before applying
- `HasPlaceholders` — the suggestion contains `...` for the programmer to fill in
- `Unspecified` — the suggestion is just text; do not apply automatically

The `MachineApplicable` level is the key innovation. It encodes the compiler's
**confidence** in the suggestion, turning "the compiler suggests" into "the
compiler certifies." A `MachineApplicable` suggestion for adding a missing `;`
is applied without review; a `MaybeIncorrect` suggestion for changing a type
annotation requires confirmation.

For AI agents, applicability levels are essential metadata. An AI tool that
blindly applies all compiler suggestions will eventually break code. An AI tool
that filters by `MachineApplicable` and reviews `MaybeIncorrect` can fix
mechanical issues (missing imports, missing semicolons, unused variables) with
high confidence.

### TypeScript's Quick Fixes

TypeScript's `ts.LanguageService.getCodeFixesAtPosition` returns an array of
`CodeFixAction` objects, each with a description and a list of `FileTextChanges`.
The quick fix system is integrated into the type checker: when the type checker
detects an error, it records the error code and enough context to derive fix
candidates.

Examples of TypeScript quick fixes:
- `Cannot find name 'foo'. Did you mean 'Foo'?` → rename to `Foo` or create declaration
- `Property 'bar' does not exist on type 'T'` → declare property on type or
  change access to known property
- `Type 'string' is not assignable to type 'number'` → add type assertion or
  `parseInt()` call
- `Unused variable 'x'` → prefix with `_` or remove declaration
- `Import declaration conflicts with local declaration` → rename import

The pattern: TypeScript's quick fixes are **derived from the type checker's
internal state**, not from pattern matching on error message strings. The type
checker knows which type was expected and which was found, which names are
similar (edit distance), and which imports are available. The fix generation
code queries this state and produces concrete edits.

### The "Diagnostic → Code Action" Pipeline Architecture

The pipeline should be:

```
Compiler pass → DiagnosticCollector.emits(Diagnostic {
    code: "E001",
    message: "...",
    spans: [...],
    context: {  // machine-readable additional data
        expected_type: "Int",
        actual_type: "String",
        similar_names: ["foo", "Foo"],
        available_imports: ["foo from bar.baz"],
    }
}) → CodeActionProvider.provides(Diagnostic) → [CodeAction {
    title: "Rename to 'Foo'",
    edit: WorkspaceEdit { changes: {uri: [TextEdit {range, newText: "Foo"}]} },
    isPreferred: true,
}]
```

The critical design decision is what `context` contains. For most diagnostics,
the context should include:
- The expected and actual types (for type mismatch diagnostics)
- The names of similar symbols (for "name not found" diagnostics)
- The available imports (for auto-import)
- The constraint that failed (for constraint violation diagnostics)
- The source spans of related locations (for multi-span diagnostics)

This context is what enables code actions to be **generated, not hand-written
for every diagnostic.** A general "replace with similar name" code action works
for any name-resolution diagnostic because the context always includes
`similar_names`. A general "add import" code action works for any unresolved
name because the context always includes `available_imports`.

### How Should Refactoring Operations Be Specified?

Refactoring operations (extract function, inline variable, change signature,
convert to arrow function) are more complex than quick fixes. They require:

1. **Preconditions:** Is the refactoring valid at this location? Can you extract
   this expression into a function without changing semantics?
2. **Input from the user:** What should the new function be named? Which
   parameters should it take?
3. **A source transformation:** What edits produce the refactored code?

The LSP protocol handles this with `textDocument/codeAction` (the server returns
available refactorings at a location) and `workspace/executeCommand` (the server
executes a named refactoring with arguments). But the specification of the
refactoring itself — the transformation rules — are server-internal. There is no
standard refactoring engine.

TypeScript's refactoring API is the most structured:
```typescript
const edits = ts.LanguageService.getEditsForRefactor(
    fileName, startPosition, endPosition,
    'Extract function', // refactor name
    'function',         // action name
    { name: 'newFunction' } // user-provided arguments
);
```

For Nomi, refactorings should be specified as **AST transformations with
precondition checks.** Each refactoring is a function `(AST, Range) → Option<AST>`
that checks preconditions and produces the transformed tree. The transformation
can be tested independently of the LSP server by asserting that `apply_refactor(code, range)` produces expected output.

### Key Structural Insight for Nomi

Nomi's diagnostic infrastructure should include a `context` field that carries
structured data for fix generation from the start. Every diagnostic emitted by
the parser, the constraint checker, or the interpreter should carry the
information needed to generate code actions — not just the information needed to
display an error message.

The `textDocument/codeAction` handler should be generic: it reads the
diagnostic's `context`, applies a set of fix-generating rules to that context,
and returns code actions. New diagnostics should not require new code action
handler code; they should work automatically because the context carries the
right data.

---

## 6. Proof Traces and Explanation

### Core Design Insight for AI Readability

When a compiler rejects a program, it has **reasons** — a chain of inference
steps that led to the conclusion "this is wrong." Most compilers discard those
reasons and only report the conclusion. The "show your work" principle says:
expose the inference chain as structured output that both humans and tools can
inspect.

For AI tools, this is transformative. An AI agent that sees "type mismatch:
expected Int, got String" must guess why the String appeared. An AI agent that
sees the full inference chain — "String came from `user.name` at line 42, which
has type String because `User.name` is declared as String at line 15, which is
accessed because `getUser()` returns User" — can reason about which link in the
chain to fix.

### Rust's `--explain` for Error Codes

Rust's `rustc --explain E0382` prints a full page explanation of the "use of
moved value" error, including example code that produces the error and example
fixes. The explanation is a Markdown document checked into the compiler source,
keyed by error code. This means:

- Explanations are versioned with the compiler
- Explanations can include code snippets that are actually tested
- The same explanation is available via `--explain`, the Rust Reference, and
  rust-analyzer's hover cards
- Error codes are stable identifiers that survive across compiler versions

For AI tools, error codes are a fast path to semantic understanding. An AI agent
that sees `E0382` can look up the explanation and understand the *concept*
(ownership and moves) behind the error, not just the *message*.

### Haskell's Typed Holes and GHC's Evidence Output

GHC's typed holes are the most direct implementation of "the compiler tells you
what it knows." When the programmer writes `_` in an expression, GHC reports:

```
Found hole: _ :: Int -> Bool
Relevant bindings include:
  isEven :: Int -> Bool
  isPositive :: Int -> Bool
Valid hole fits include:
  isEven :: Int -> Bool
  isPositive :: Int -> Bool
  (not .) isEven :: Int -> Bool
```

The key mechanism: GHC **solves for the type of the hole** within the
surrounding type context, then searches the environment for bindings with
compatible types, then generates **valid hole fits** — expressions that could
replace the hole. This is type-directed program synthesis at the granularity of
a single expression.

For AI tools, typed holes are a structured query mechanism. An AI agent can ask
"what can go here?" by inserting a hole, invoking the type checker, and reading
the valid hole fits. This is a two-way interaction between the AI and the
compiler that requires no natural language — it is entirely type-driven.

GHC's evidence output (`-fdefer-type-errors`) takes this further: type errors
become runtime warnings that carry the full type mismatch information to the
point of execution. This means the error trace includes both the compile-time
type context and the runtime call stack.

### Coq/Lean Proof Terms as Inspectable Artifacts

In proof assistants, the proof term IS the explanation. When Coq or Lean accepts
a proof, it produces a lambda term whose type is the theorem being proved. This
term can be:

- **Printed** as a concrete expression (often very large, but fully explicit)
- **Simplified** to show the computational content
- **Checked** independently by a small kernel type checker
- **Extracted** to executable code in OCaml, Haskell, or Scheme

The critical property is that the proof term is **self-contained verification.**
You don't need to trust the proof assistant's tactics — you can check the proof
term with a small, independently auditable kernel. This is the strongest form
of "show your work": the reasoning artifact is itself a computable object that
can be verified by a different program.

For programming languages, the analogous concept is **lowering traces.** If a
compiler transforms source through intermediate representations, it should be
able to produce a trace of each transformation step, with the source spans that
justify each step. This trace is a "proof" that the transformation is correct —
or at least an inspectable artifact that a tool can use to explain to a
programmer what the compiler did.

### How Should a Language Expose Its Type Inference and Constraint Solving?

The key design decision is **output format.** The choices are:

1. **Natural language prose** (Elm's approach): "I think you meant..."
   Human-readable but not machine-queryable.

2. **Structured trace** (Scala 3's `-explain`): The reasoning is presented as
   structured sections (which implicits were tried, why each failed). More
   queryable than prose but still text-oriented.

3. **Data structure / JSON** (Clojure's `explain-data`): The explanation is a
   Clojure map that can be rendered as text or consumed programmatically.
   Machine-queryable; every field is typed.

4. **Inspectable proof term** (Coq/Lean): The explanation is a formal object
   that can be checked independently. Maximum rigor; high implementation cost.

For a practical language like Nomi, option 3 (structured data with JSON
representation) is the right target. The explanation should be a typed data
structure that carries:
- The inference rule applied at each step
- The source spans of the premises
- The constraint that was solved or that failed
- The substitution that was applied
- The remaining unsolved constraints

This structure can be rendered as human-readable prose, as JSON for tool
consumption, or as an interactive tree for a notebook or IDE.

### Key Structural Insight for Nomi

Nomi's design philosophy — "every layer should remain peelable, inspectable, and
reducible to a smaller core" — is already aligned with the "show your work"
principle. The `python3 -m tools.syntax.inspect` CLI already exposes pipeline
stages. Nomi should extend this to produce a **pipeline trace** for each
expression: what grammar rule produced the parse, what lowering rule produced
the surface AST, what desugar pass transformed it, and what interpreter rule
evaluates it.

The pipeline trace should be a first-class artifact: a structured representation
of "how did the compiler/language arrive at this result for this expression."
For a type error, the trace shows the constraint that failed and the inference
steps that led to it. For a runtime error, the trace shows the surface syntax
that was lowered to the expression that raised the error.

---

## 7. Design Fixtures and Test Infrastructure

### Core Design Insight for AI Readability

A language project's test infrastructure is the **ground truth for tooling
behavior.** Every diagnostic format, every code action output, every
completion ranking — these are not purely implementation concerns. They are
semantic contracts that should be tested with the same rigor as the language's
evaluation semantics. For AI agents contributing to a language project, the
test infrastructure is the primary specification of what correct tooling
behavior looks like.

### Rust's rust-analyzer Test Infrastructure

rust-analyzer's test infrastructure is the most sophisticated in the language
tooling space. The key patterns:

**1. Fixture-based tests with inline annotations.**
```rust
fn foo() {
    let x = 1;
    x; // $0
} // $0 is the cursor position
```
The `$0` annotation marks the cursor position for completion, hover, or
go-to-definition tests. The test framework extracts the annotation, runs the
corresponding LSP request, and asserts the output.

**2. Expectation-based tests.**
```rust
fn foo() {
    let x: i32 = 1;
    x; // ^ i32
}
```
The `^ i32` annotation declares what the hover type should be. The test
framework compares the server's actual hover output against the
annotation.

**3. Snapshot testing for diagnostics.**
The test framework captures all diagnostics for a fixture file and saves them
as a `.snap` file. When diagnostics change, the test fails and the developer
reviews the diff, then updates the snapshot if the change is expected:
```
cargo test -- --update-snapshots
```

**4. Move-check annotations for code actions.**
```rust
fn foo() {
    let x = 1;
    x + 1; // $0
}
// After apply 'remove unused x':
fn foo() {
    1 + 1;
}
```
The test framework applies the code action at `$0` and asserts the resulting
source matches the expected output.

### TypeScript's Baselines

TypeScript's test infrastructure uses **baseline files** — `.baseline` or
`.types` files that capture the expected output of the type checker for a given
input. A test like:
```typescript
// @module: commonjs
// @target: ES2015
// @strict: true

const x: string = 42; // Error
```
produces a baseline:
```
tests/cases/compiler/example.ts(4,7): error TS2322: Type 'number' is not assignable to type 'string'.
```

The baseline is version-controlled. When the type checker changes, the baseline
diffs show exactly what changed. This is the same snapshot testing pattern as
rust-analyzer, applied at the compiler level.

TypeScript also has **fourslash tests** — a DSL for specifying sequences of LSP
interactions:
```typescript
// @filename: a.ts
//// export const x = 1;

// @filename: b.ts
//// import { x[|/*completion*/|] } from "./a";
////
//// verify.completions({ exact: ["x"] });
```
The `[|/*completion*/|]` annotation marks the position, and the `verify`
directive asserts the expected LSP response.

### The Snapshot Testing Pattern for Diagnostics and Code Actions

The snapshot testing pattern is ubiquitous because it solves a specific problem:
**tooling output is high-dimensional and hard to assert manually.** A diagnostic
includes a message, a range, a severity, optional related information, optional
code actions. Writing an assertion for each field is tedious and fragile.
Snapshot testing captures the complete output and lets the developer review the
diff on change.

The pattern:
```
Input file → Tool → Output → Compare to stored snapshot → Pass/Fail
                                               ↓
                                         Review diff → Update snapshot
```

For Nomi, snapshot testing should cover:
- **Parser output:** For a given `.nomi` source, does the raw tree, surface AST,
  and Python AST match expected snapshots?
- **Diagnostic output:** For a given `.nomi` source with intentional errors,
  does the diagnostic collector produce the expected error messages and code
  actions?
- **Lowering trace:** For a given `.nomi` source, does the pipeline trace
  show the expected transformation steps?

Nomi already has regression snapshots at `prototype/tests/regression/` which
test interpreter output. These should be extended to cover pipeline stages and
diagnostics.

### How to Structure Tooling Tests for AI Agents

AI agents contributing to a language project need the test infrastructure to be
**self-documenting and discoverable.** Recommendations:

1. **Fixture files should be minimal and focused.** Each fixture should test one
   diagnostic or one code action. The file name should describe the feature
   being tested (`unused_variable_after_desugar.nomi`).

2. **Annotations should be consistent and documented.** Use a small, documented
   set of annotation markers (`$0` for cursor, `// error` for expected
   diagnostic, `// ^ type` for expected type hover). Document them in the test
   README or in the fixture directory.

3. **Snapshot diffs should be human-readable.** When a snapshot changes, the
   diff should clearly show what changed and why. Avoid snapshots that are
   machine-only (e.g., binary blobs).

4. **The test harness should be runnable with a single command.** `pytest
   prototype/tests/tooling/` should run all tooling tests and report results.

5. **Golden tests for diagnostics should be separate from behavior tests.**
   A test that says "this program should produce this exact error message" is a
   golden test; a test that says "this program should produce an error on line
   5" is a behavior test. Golden tests are more brittle and should be siloed.

### Key Structural Insight for Nomi

Nomi's test infrastructure should adopt the fixture + annotation pattern for
tooling tests from the start. Define a test DSL that lets developers write:

```
// $0 marks the cursor for completion/hover tests
// --- error E001 --- marks an expected diagnostic with code
//         ^-- this span
// --- code-action "rename to _x" --- marks the expected code action result
// --- trace --- marks the beginning of an expected pipeline trace
```

These annotations should be recognized by the test harness, which extracts them,
runs the relevant tooling operation, and asserts the output. The harness should
produce snapshot files for full-structure assertions and annotation-based
assertions for specific, stable properties.

---

## 8. Notebook-Based AI Collaboration

### Core Design Insight for AI Readability

Jupyter's nbformat — a JSON document with cells containing source, outputs, and
metadata — is de facto **the most AI-consumed structured code format in the
world.** AI tools (Copilot, Codex, Claude, Gemini) read and generate notebook
cells as part of their standard input/output pipeline. Understanding how AI
tools interact with notebooks is essential for designing a language whose source
format is AI-friendly.

### Jupyter's nbformat as a Machine-Readable Code Format

A `.ipynb` file is a JSON document with this structure:

```json
{
  "cells": [
    {
      "cell_type": "code",
      "source": ["x = 1\n", "y = x + 2\n"],
      "outputs": [{"output_type": "execute_result", "data": {"text/plain": "3"}}],
      "execution_count": 1,
      "metadata": {"collapsed": false}
    }
  ],
  "metadata": {
    "kernelspec": {"name": "python3", "display_name": "Python 3"},
    "language_info": {"name": "python", "version": "3.11.0"}
  },
  "nbformat": 4,
  "nbformat_minor": 5
}
```

The key structural properties:
- **Cells are explicit boundaries.** Each cell is a discrete unit of code or
  documentation. AI tools can reason about cells individually.
- **Outputs are attached to their source.** The `outputs` array captures what
  happened when the cell ran — errors, printed text, displayed images.
- **Execution order is recorded.** `execution_count` numbers the cells in the
  order they were run, even if the notebook was executed out of order.
- **Metadata is extensible.** `kernelspec`, `language_info`, and arbitrary
  additional metadata provide machine-readable context about the execution
  environment.

For AI tools, nbformat has two critical properties: (1) it is **pure JSON** —
no custom parser needed; (2) it preserves the **human's structure** — cells,
their order, and their interleaving with prose are all explicit.

### How AI Tools Read and Generate Notebook Cells

**Copilot/Copilot Chat:** Can read the entire notebook as context and suggest
code for individual cells. The notebook structure gives Copilot more context
than a single file — it sees the imports, the data loading, the transformations,
and the visualizations, and can suggest code that fits within that narrative.

**Claude/Claude Code:** Can read `.ipynb` files via the NotebookRead tool,
seeing cells with their outputs inline. Can edit notebooks via NotebookEdit
(replace, insert, delete cells). The agent sees the notebook as a structured
document — it can append new cells, modify existing ones, and re-execute.

**Codex/OpenCode:** Can read and write notebooks as part of workspace tooling.
The notebook is a file like any other, but the agent understands the cell
structure and can reason about execution state (what variables are defined,
which cells depend on which).

The common pattern: AI tools treat notebooks as **semantic documents** rather
than **files containing code.** The difference is that a semantic document has
explicit sectioning (cells), interleaved explanation (markdown cells), and
execution history (outputs). An AI agent can read the markdown cell "Now we
clean the data" and understand the intent of the following code cell, then
suggest modifications that preserve that intent.

### "AI Writes a File" vs "AI Operates on a Semantic Document"

When an AI writes a `.py` file, it produces a linear stream of text. The model
must simulate the execution order — what is defined before what is used — but
the file itself does not encode execution order.

When an AI operates on a `.ipynb` notebook, the cells provide an explicit
execution narrative. The AI can see:
- Which cells have been executed (by `execution_count`)
- What variables were defined at each point (by examining outputs)
- Where errors occurred (by examining error outputs)
- What the human's intent was (by reading markdown cells)

This changes the AI's task from "write correct code" to "extend an existing
computational narrative." The AI can edit a single cell and leave the rest of
the notebook intact, or append new cells that build on previous ones.

### How Should a Language Make Its Source Format AI-Friendly?

The notebook experience suggests design principles for any language's source
format:

1. **Structured sections are better than monolithic files.** A language that
   supports named sections, markup comments, or literate programming constructs
   gives AI tools more structure to reason about.

2. **Explicit dependencies are better than implicit ones.** If a module's
   imports clearly declare what it depends on, an AI tool can reason about the
   module's context without reading the entire project.

3. **Machine-readable metadata is essential.** The nbformat's `kernelspec` and
   `language_info` tell AI tools what language and runtime to expect. A source
   file that declares `// @nomi-language-mode: reduced` gives the AI tool
   information about how to interpret the code.

4. **Output attachment is valuable.** If a language's tooling can attach
   execution output to source (like a notebook cell's outputs), AI tools can
   see what happened when the code ran, not just what the code says.

### Key Structural Insight for Nomi

Nomi already has a Jupyter kernel (`tools/jupyter/nomi_kernel.py`) that
supports execution, completion, and `%ast` for AST inspection. The kernel
should be extended to support **cell-level error tracebacks with pipeline
information.** When a cell errors, the error output should optionally include
the surface AST, the lowering step, and the desugared form — not just the
Python traceback.

Nomi should also consider a **Nomi Notebook Format (`.nomi.nb`)** that embeds
pipeline stage information as cell metadata. When a notebook cell is executed,
the kernel records in the cell's metadata:
- The pipeline stages that were traversed
- The surface AST before lowering
- The Python AST after desugaring
- Any constraints that were checked

This makes the notebook self-documenting for AI tools: an AI agent reading a
`.nomi.nb` file can see not just the source and output, but the intermediate
representations that the compiler produced.

---

## 9. Structured Expansion and Lowering Displays

### Core Design Insight for AI Readability

The difference between "the compiler accepted my code" and "I understand what
the compiler did" is the difference between a black box and a glass box.
Languages that expose their lowering steps as inspectable output make the
compiler's reasoning transparent. For AI tools, this transparency is essential:
an AI agent that sees only the final result of compilation cannot debug why a
particular lowering produced unexpected behavior.

### Debug Representations of Desugared Code

Rust's `-Zunpretty=hir` flag prints the HIR (high-level IR) representation of
a crate. This is not just a debug dump — it is a readable, formatted tree that
shows how the compiler desugared the source:

```rust
// Source
for x in iter {
    println!("{}", x);
}

// HIR (simplified)
match IntoIterator::into_iter(iter) {
    mut iter => loop {
        match Iterator::next(&mut iter) {
            Some(x) => { println!("{}", x); }
            None => break,
        }
    }
}
```

The HIR output shows:
- The `for` loop desugared into a `match` + `loop` + `match Some/None`
- The `IntoIterator` trait resolution
- The `mut` binding for the iterator

Haskell's `-ddump-simpl` is even more powerful, showing the Core representation
after all desugaring and optimization:

```haskell
-- Source
map f xs = [f x | x <- xs]

-- Core
map f xs = build (\c n -> foldr (\x b -> c (f x) b) n xs)
```

The Core output reveals that list comprehensions are desugared through
`build`/`foldr` fusion — a non-obvious optimization that can explain
performance behavior.

For AI tools, the desugared output is a **ground truth** for understanding the
language's semantics. If an AI agent needs to know what `for x in iter` means,
it can look at the HIR output rather than reading the Rust reference or
guessing from behavior. The desugared representation is an **executable
specification** of what the syntax means.

### How Elm's Compiler Explains Type Inference

Elm's compiler error messages include type information that walks through the
inference:

```
The 1st argument to `List.map` is not what I expect:

3| List.map "hello" [1, 2, 3]
   ^^^^^^^^^
This `"hello"` value is a:

    String

But `List.map` needs the 1st argument to be:

    a -> b
```

The compiler shows both the actual type (`String`) and the expected type
(`a -> b`) with the type variable names from the function's signature. This is
a **contextualized type display** — it shows the function's declared type
signature alongside the concrete type of the argument, making it clear why they
do not match.

### The Nomi Pipeline as an Inspectable Multi-Stage System

Nomi's pipeline:

```
Source → raw Lark tree → layer-transformed tree → surface AST (mixed)
      → Python AST (pure) → desugared Python AST → interpreter eval
```

The `python3 -m tools.syntax.inspect` CLI already exposes each stage:

```
$ python3 -m tools.syntax.inspect example.nomi --stage raw-tree
# Shows the raw Lark parse tree

$ python3 -m tools.syntax.inspect example.nomi --stage surface-ast
# Shows surface AST with Nomi-specific nodes

$ python3 -m tools.syntax.inspect example.nomi --stage python-ast
# Shows final desugared Python AST
```

For AI readability, this pipeline is already well-designed. The extensions that
would make it AI-tool-consumable:

1. **JSON output mode.** The `inspect` CLI should support `--format json` to
   produce machine-parseable output at each stage. An AI tool can query
   "what is the raw parse tree for line 10?" and get structured JSON.

2. **Stage-by-stage diff.** The CLI should support `--diff` to show what each
   transformation changed from the previous stage. This is essential for
   understanding lowering: the programmer writes Nomi syntax; the diff shows
   what Python AST the lowering produced.

3. **Span tracking across stages.** Each transformation should emit the mapping
   from output spans back to input spans. When the programmer inspects the
   Python AST for a Nomi expression, the returned data should include
   `sourceSpan: { file: "example.nomi", line: 5, col: 10 }`.

4. **Explain mode.** `python3 -m tools.syntax.inspect example.nomi --explain E001`
   should explain a diagnostic code with the relevant pipeline stages,
   showing the source, the lowering, and the constraint that failed.

### How Should a Multi-Stage Pipeline Expose Each Stage for Inspection?

The design requirement is that every stage is **independently queryable.** An AI
tool should be able to ask:

1. "What is the parse tree for this source region?" → returns the raw tree,
   layer-transformed tree, or both.

2. "What surface nodes were produced by lowering this source region?" → returns
   the surface AST nodes with their source spans.

3. "What Python AST was produced by desugaring this surface node?" → returns the
   Python AST with the mapping back to the surface node.

4. "What transformed Python AST was produced by a specific desugar pass?" →
   returns the AST before and after the pass, with the diff.

5. "What interpreter rule will evaluate this expression?" → returns the relevant
   `eval_*` method name and its interpreter mode (python/nomi/reduced).

Each query should be answerable at a specific source location, and the result
should include the full chain of transformations that produced it.

### Key Structural Insight for Nomi

Nomi's inspectability infrastructure (the `inspect` CLI) should evolve into a
**pipeline query API** — a set of functions that answer specific questions about
pipeline stages at specific source locations. This API should be callable from:

- The CLI (`python3 -m tools.syntax.inspect`)
- The LSP server (as custom LSP extensions or `workspace/executeCommand`)
- The notebook kernel (as `%pipeline` magics)
- Python test fixtures (as assertion helpers)

The API should return structured data (JSON or Python objects), not just
formatted text, so that both humans and machines can consume it.

---

## 10. Gradual Typing and Type Annotations as Machine-Readable Contracts

### Core Design Insight for AI Readability

Type annotations are the single most information-dense form of documentation
that an AI tool can consume. A function signature `def process(items: List[User], config: Config) -> Report` tells an AI tool more than three paragraphs of
docstring. The type annotation is **structured, checkable, and precise** — three
properties that natural language documentation cannot guarantee.

### Python's Type Stub (.pyi) Files

Python's `.pyi` stub files separate type information from implementation. A
stub file contains only function signatures, class declarations, and variable
type annotations — no implementations. The type checker reads the stub, the
interpreter reads the implementation.

```python
# process.pyi
from typing import List, Optional
from models import User, Config, Report

def process(items: List[User], config: Config) -> Report: ...
def find_user(name: str) -> Optional[User]: ...
```

For AI tools, `.pyi` files are an **index into the library's type space.** An AI
agent that needs to know what `process` returns can read the stub without
reading the implementation. This is the same separation of interface and
implementation that programmers use, but automated: the AI tool queries the
interface and then decides whether it needs to read the implementation.

The limitation: Python stubs are not guaranteed to match the implementation.
mypy and pyright check for consistency, but a stale stub is a lying stub. The
type annotation is a claim, not a proof.

### TypeScript's Declaration Files (.d.ts)

TypeScript's `.d.ts` files serve the same role as Python's `.pyi` files but with
stronger guarantees. A `.d.ts` file can be:
- **Auto-generated** by `tsc --declaration` from `.ts` source
- **Hand-written** for JavaScript libraries that have no TypeScript source
- **Published** via DefinitelyTyped (`@types/*`) for community-maintained types

The key architectural difference from Python: TypeScript's declaration files are
**the public API of a package.** The `tsconfig.json` `declaration: true` setting
ensures that the `.d.ts` is regenerated on every build. This makes stale stubs
a build error, not a maintenance hazard.

For AI tools, `.d.ts` files are the primary mechanism for understanding library
APIs. An AI agent that encounters `import { useState } from "react"` can read
`react/index.d.ts` to discover:
- `useState` has type `<S>(initialState: S | (() => S)) => [S, Dispatch<SetStateAction<S>>]`
- The return type is a tuple of `[value, setter]`
- `Dispatch` and `SetStateAction` are generic utility types

This type information is sufficient for the AI to generate correct usage without
reading React's source code or documentation.

### How Do Type Annotations Help AI Tools Understand Intent?

Type annotations serve three distinct functions for AI tools:

1. **Constraint on code generation.** When an AI generates code, the type
   annotation constrains the search space. If the function returns
   `Optional[User]`, the AI will not generate code that assumes a non-null
   result without a null check.

2. **Signal of programmer intent.** `def get_name() -> Optional[str]` signals
   that the result may be missing. `def get_name() -> str` signals that the
   programmer believes the name is always available. An AI tool can use this
   signal to understand the programmer's mental model — not just the code's
   behavior.

3. **Enables refactoring.** "Change the return type of `get_name` from `str` to
   `Optional[str]`" is a refactoring that the AI can execute mechanically:
   find all call sites, insert null checks where needed, propagate the
   Optional through the call chain. This is only possible because the type
   annotation makes the change's impact computable.

The difference between "this function takes a dict" and "this function takes
`{name: str, age: int}`" is the difference between a tool that can only
suggest valid key names and a tool that can suggest valid values for each key.
Structural type annotations (TypeScript's object types, Python's TypedDict)
carry more information per character than any other form of code documentation.

### How Should AI Tools Query and Use Type Information?

The ideal type query interface for AI tools:

```python
# Hypothetical API
type_checker.get_type_at_location(file, line, col)
# → TypeInfo { type: "List[User]", span: ..., definition: ..., generics: [...] }

type_checker.get_signature_at_location(file, line, col)
# → Signature { params: [...], return_type: ..., generics: [...] }

type_checker.get_fields_of_type("User")
# → [Field("name", "str"), Field("age", "int"), Field("email", "Optional[str]")]

type_checker.get_implementors_of("Protocol")
# → ["User", "Admin", "Guest"]

type_checker.get_callers_of("process")
# → [(file, line, col, arg_types), ...]
```

This is essentially what TypeScript's `ts.LanguageService` provides and what
rust-analyzer's salsa queries provide. The key property is that the AI tool
does not need to walk the AST looking for types — it asks the type database
directly.

### Key Structural Insight for Nomi

Nomi should define a **type annotation syntax** that is part of the language
from day one, not an optional tool. Even if the initial implementation only
checks annotations at runtime (like Python's `@typechecked` decorators), having
the syntax means:
- AI tools have a structured format for understanding function contracts
- The annotation syntax is stable and can be targeted by tooling
- Gradual typing can be added incrementally without changing syntax

Nomi's binding constraint syntax (`name: constraint = value`) already integrates
type annotations into the binding form. This is a better foundation than
Python's `name: type = value` because `constraint` generalizes to non-type
constraints (range checks, field presence, etc.). An AI tool reading Nomi source
sees `x: Int = 42` and understands both the type and the value, in the same
syntactic position.

Nomi should also generate **declaration files** (`.nomi.d` or similar) that
capture the public API of a module in a form that AI tools can consume without
executing the code. These declaration files are the Nomi equivalent of
TypeScript's `.d.ts` — structured, checkable, and publishable.

---

## 11. Cross-Language Synthesis

### Structural Invariants: Patterns That Appear Across ALL Successful AI/Tooling-Friendly Languages

**Invariant 1: Source spans survive the entire pipeline.**
Every language with good tooling preserves source location information from the
parser through every intermediate representation to the final diagnostic output.
Rust's HIR, MIR, and LLVM IR all carry source spans. TypeScript's AST nodes all
carry `pos` and `end`. Haskell's GHC Core includes `SrcSpan` annotations. When
spans are dropped, downstream diagnostics degrade to "somewhere in this
function."

**Invariant 2: The compiler's internal analysis is exposed through a stable,
query-oriented API.**
TypeScript's `ts.LanguageService`, Rust's rust-analyzer salsa queries, Clojure's
`explain-data` — all provide a way for tools to ask specific questions and get
structured answers. The API is not "here is the compiler's internal state, good
luck" — it is "ask this specific question, get this specific answer."

**Invariant 3: Diagnostics are structured data, not strings.**
Every language with good diagnostics (Rust, Swift, TypeScript) emits
diagnostics as typed structures with fields for severity, code, message, spans,
and suggestions. The human-readable text is a rendering of the structure, not
the structure itself. This enables multiple renderers (terminal, IDE, JSON) from
a single diagnostic format.

**Invariant 4: Error codes are stable identifiers.**
Rust's `E0382`, Scala 3's `E007`, TypeScript's `TS2322` — every language that
takes tooling seriously assigns stable error codes. Error codes enable:
- Machine-lookup of explanations (`rustc --explain E0382`)
- Tool configuration (`#[allow(E0382)]`, `@ts-ignore TS2322`)
- Regression testing (the same error always has the same code)
- Documentation cross-referencing

**Invariant 5: The analysis engine is incremental.**
rust-analyzer's salsa, TypeScript's per-file invalidation, Tree-sitter's
incremental parsing — every performant language tool uses incremental
computation. Re-parsing the entire project on every keystroke is not viable.
Incrementality is an architectural constraint, not an optimization.

**Invariant 6: Syntax is regular enough for error-tolerant parsing.**
Languages with good tooling have syntax that supports error recovery. This does
not mean LL(1) grammar — Rust's macro-heavy syntax is far from LL(1). But the
syntax has enough delimiters and keywords that a parser can find statement
boundaries even when the interior of a statement is malformed.

**Invariant 7: The analysis engine and the compiler share the same semantic
model.**
rust-analyzer does not use `rustc` internally, but it implements the same type
system and trait resolution. TypeScript's tsserver is the same type checker that
`tsc` uses. When the tooling engine disagrees with the compiler on what a
program means, the tooling is incorrect. There must be **one definition of the
language's semantics** that both the compiler and tooling implement.

### Genuine Design Forks: Where Languages Made Genuinely Different Tradeoffs About Toolability

**Fork 1: Compiler-reuse vs independent analysis engine.**
- **Reuse:** TypeScript (tsc IS tsserver), Python (Pyright is an independent
  tool), Clojure (spec is a library).
- **Independent:** rust-analyzer (does not use rustc), Haskell (ghcide/HLS are
  separate from GHC).

The tradeoff: reusing the compiler guarantees semantic consistency but couples
the tool to the compiler's architecture (batch compilation, not interactive
querying). An independent engine can be optimized for latency and incrementality
but risks semantic divergence.

**Fork 2: CST-preserving vs AST-only tree representation.**
- **CST-preserving:** Tree-sitter (lossless, every token preserved), Swift
  libsyntax (lossless syntax tree for the parser, separate AST for the compiler).
- **AST-only:** Python's `ast` module, Go's `go/ast`, Rust's `syn` (lossy, discards
  comments and formatting).

CST preservation enables lossless round-tripping (parse → modify → print without
losing formatting). AST-only is simpler but cannot be used for formatting tools
or precise refactorings that preserve user formatting choices.

**Fork 3: Batch vs incremental analysis.**
- **Batch:** GHC (compiles the entire module at once, -fdefer-type-errors is an
  afterthought for IDE use).
- **Incremental:** rust-analyzer (every analysis is a lazy, memoized query),
  TypeScript (per-file invalidation with project-level caching).

Batch analysis is simpler to implement and reason about. Incremental analysis is
required for IDE responsiveness but adds significant architectural complexity.

**Fork 4: Prose-first vs data-first diagnostics.**
- **Prose-first:** Elm (diagnostics read like a teacher explaining an error),
  early Python (human-written error messages).
- **Data-first:** Rust (diagnostics are Diagnostic structs), Clojure
  (explain-data returns a data structure).

Prose-first diagnostics are more accessible to beginners. Data-first diagnostics
are consumable by tools, testable, and localizable. Rust's approach (prose
embedded in a structured diagnostic) is the best hybrid.

**Fork 5: Type-in-compiler vs type-in-external-tool.**
- **Type-in-compiler:** TypeScript, Rust, Elm, Haskell — the type checker is
  part of the standard toolchain.
- **Type-in-external-tool:** Python (mypy/Pyright are separate), Ruby (Sorbet is
  separate), JavaScript (TypeScript is a separate compiler).

When types are in the compiler, every tool gets type information for free. When
types are in an external tool, the ecosystem fragments: some tools see types,
some do not. AI tools in the Python ecosystem must work with and without type
information, significantly increasing complexity.

**Fork 6: IDE-first vs compiler-first diagnostic format.**
- **IDE-first:** Swift (diagnostics carry FixIts consumable by Xcode), Dart
  (diagnostics designed for Dart Analysis Server).
- **Compiler-first:** GHC (diagnostics designed for terminal output, IDE
  adaptation is secondary), GCC.

IDE-first diagnostics carry structured fix suggestions and work with the editor
protocol natively. Compiler-first diagnostics are portable but require the IDE
to parse terminal output.

**Fork 7: Open-world vs closed-world analysis.**
- **Open-world:** TypeScript (any JavaScript file is valid TypeScript, `.d.ts`
  files can add types to any library), Python (type stubs can be added
  independently of the library).
- **Closed-world:** Rust (the compiler sees the entire crate graph), Elm (the
  compiler sees the entire project).

Open-world analysis enables gradual adoption and ecosystem participation but
makes completeness guarantees impossible — the analyzer can never know all
possible callers. Closed-world analysis enables stronger guarantees but requires
the entire project to be in the language from the start.

### The "AI-First Language Design" Question

**Should a language be designed differently knowing AI agents will write, read,
and refactor it?**

The answer from the evidence surveyed: **yes, but not in the ways most people
assume.** The "AI-first" changes are not about making syntax easier for LLMs to
generate (LLMs can generate any syntax). They are about making the language's
semantics machine-readable so that AI tools can reason about correctness, not
just generate plausible text.

The concrete AI-first design principles:

1. **Every construct should have a deterministic, inspectable lowering.**
   Sugar that desugars in multiple context-dependent ways is hard for AI tools
   to reason about. An AI agent should be able to query "what does this syntax
   mean?" and get a single, stable answer.

2. **Type information should be available without execution.**
   An AI agent should be able to determine the type of any expression by
   querying the analysis engine, without running the program. This means the
   language needs a static type system or a type inference mechanism.

3. **Error messages should include machine-readable fix suggestions.**
   "Expected Int, got String" is human-readable. A fix suggestion with the
   range and replacement text is machine-applicable. An AI agent can apply the
   fix and re-check, creating a tight feedback loop.

4. **The pipeline should be queryable at arbitrary granularity.**
   An AI agent should be able to ask "show me the desugared form of expression E
   on line 42" and get just that expression's lowering, not the entire file's.

5. **Changes should be previewable before application.**
   This is a property of the tooling, not the language directly, but the
   language's AST design affects it. If the AST is lossless (preserves
   formatting), then a refactoring preview can show exactly what changes, with
   no unrelated reformatting.

Counter-principles (things that do NOT matter for AI-first design):
- Terseness vs verbosity: LLMs handle both equally.
- Natural-language-like syntax: LLMs do not benefit from English-like syntax.
- Dynamic features for flexibility: LLMs benefit from static guarantees that
  enable checking.

### AST Design for Toolability

What makes an AST easy for tools to work with? The properties that matter,
ranked:

1. **Source spans on every node.** Without spans, tools cannot map between the
   AST and the source text. Spans should be a required field, not optional.

2. **Lossless round-tripping.** If you parse source, modify the tree, and print
   it, the output should differ from the input only where you made changes.
   Comments, whitespace, and formatting should survive untouched. This requires
   a CST, not an AST, or an AST that preserves trivia as node attachments.

3. **Stable node types.** Adding a new language feature should not renumber the
   enum of AST node types. Tools that match on node type need stable
   identifiers. Use string-based node types (like Tree-sitter) or explicitly
   stable enum values.

4. **Explicit rather than implicit structure.** Every syntactic construct should
   produce a unique, predictable tree shape. Two constructs that look similar
   should not produce identical trees.

5. **Immutable or copy-on-write.** Tools that modify ASTs benefit from
   structural sharing. If changing one node requires deep-copying the entire
   tree, refactoring tools become slow and complex (Python's `ast` module has
   this problem; Roslyn's `SyntaxNode` with `With*` methods does not).

6. **Visitor pattern with context.** Walking an AST should pass context
   (ancestor nodes, scope stack) to the visitor. Python's `ast.NodeVisitor`
   passes only the current node; tools must maintain their own context stack.

### Diagnostics as Machine-Readable Output

The minimum viable machine-readable diagnostic format:

```json
{
  "diagnostics": [
    {
      "code": "E001",
      "severity": "error",
      "message": "type mismatch: expected Int, got String",
      "spans": [
        {"file": "main.nomi", "start": {"line": 5, "col": 10}, "end": {"line": 5, "col": 14}, "label": "this expression"},
        {"file": "main.nomi", "start": {"line": 2, "col": 5}, "end": {"line": 2, "col": 8}, "label": "declared here as String"}
      ],
      "because": [
        {"message": "`user.name` has type String", "span": {"file": "types.nomi", "line": 15, "col": 3, "end_line": 15, "end_col": 7}}
      ],
      "suggestions": [
        {"title": "convert to Int", "edit": {"range": "...", "newText": "int(user.name)"}},
        {"title": "change expected type to String", "edit": {"range": "...", "newText": "String"}}
      ],
      "pipeline_stage": "constraint-checking"
    }
  ]
}
```

The `because` field enables error chaining. The `suggestions` field enables code
actions. The `pipeline_stage` field tells tools where in the pipeline the error
was detected (parse, lower, desugar, type-check, runtime).

### The Expansion/Explain Pipeline

How should a compiler expose its reasoning as inspectable output? The
architecture should be:

```
Source → Stage 1 (parse) → Trace 1
       → Stage 2 (lower) → Trace 2
       → Stage 3 (desugar) → Trace 3
       → Stage 4 (type-check) → Trace 4
       → Stage 5 (evaluate) → Trace 5
```

Each trace records what the stage did to the source: what nodes were created,
what transformations were applied, what constraints were checked. The traces are
linked: Trace 3 references the nodes in Trace 2 that it transformed.

The `--explain <code>` command queries this trace database for all entries
related to a specific diagnostic code, and renders them in reading order. The
`--trace <expression>` command shows the full pipeline trace for a specific
source expression.

### IDE Integration Architecture

The architectural choices for IDE integration:

1. **Compiler as LSP server.** The compiler binary also speaks LSP. Examples:
   `gopls`, `dart analyze`, `pylsp` (wrapping existing tools). Simplicity: one
   binary, one semantic model. Cost: the compiler must be designed for
   interactive use.

2. **Dedicated LSP server wrapping compiler queries.** A separate process that
   calls the compiler for analysis and translates results to LSP. Examples:
   `rust-analyzer` (does not use rustc for analysis), `Pyright` (separate from
   the Python interpreter). Flexibility: the LSP server can cache and optimize
   independently. Cost: semantic divergence risk.

3. **Library-level LSP.** The language's standard library includes an LSP
   server. Example: TypeScript's `tsserver` is `ts.LanguageService` plus a
   JSON-RPC wrapper. Modularity: any tool can embed the language service.
   Cost: requires the language runtime on the developer's machine.

4. **Hybrid.** The compiler produces structured output consumed by a thin LSP
   server. Example: Nomi could compile to a `.nomi-semantic` file (similar to
   TypeScript's `.d.ts`) that the LSP server reads and indexes. The LSP server
   does not need to run the compiler; it needs to read the compiler's output.

For Nomi, option 4 is the most practical near-term path. The Nomi compiler
produces a semantic index file (a JSON artifact containing types, bindings,
constraints, and source spans). The LSP server reads the index, watches files
for changes, re-runs the compiler on changed files, and updates the index.
This decouples the LSP server's latency requirements from the compiler's
throughput requirements.

### Anti-Patterns: Tooling Mistakes That Consistently Hurt Ecosystems

1. **Stringly-typed diagnostics.** Storing diagnostic messages as raw strings
   with no structure. Prevents tools from querying, filtering, or categorizing
   diagnostics. Prevents localizing error messages. Prevents code actions from
   being mechanically derived.

2. **Sporadic span preservation.** Preserving source spans "when convenient"
   rather than requiring every AST node to carry one. Results in diagnostics
   that sometimes point to the exact expression and sometimes point to "line 42
   somewhere."

3. **No error codes.** "Error on line 5" with no stable identifier. Prevents
   documentation, tool suppression, and regression testing. Error codes are
   cheap to add and expensive to retrofit.

4. **Compiler and IDE using different parsers.** Python's tokenizer and
   Tree-sitter's Python grammar are different; they occasionally disagree on
   edge cases. The result is syntax highlighting that shows one thing and the
   compiler that accepts/rejects another.

5. **Batch-only compilation with no incremental mode.** GHC's batch model means
   IDE tooling must either accept multi-second latency or build a parallel
   incremental analysis engine (which is what GHCide/HLS did, at enormous
   engineering cost).

6. **No standard project model.** How does the tooling find all the files in a
   project? Python has `sys.path`, `pyproject.toml`, `setup.py`, `requirements.txt`,
   and a dozen conventions. TypeScript has `tsconfig.json`. Rust has
   `Cargo.toml`. The project model is the root of all cross-file analysis; a
   language that does not define one forces every tool to invent its own.

7. **Comments and trivia as second-class citizens.** Most AST formats drop
   comments. This means any tool that modifies and re-prints source destroys
   comments. Over time, programmers learn not to trust any automatic code
   modification tool, because it nukes the documentation.

8. **Diagnostic output that cannot be silenced.** If every type error is a
   blocking compilation failure with no suppress mechanism, AI agents cannot
   iterate: they must fix every error before seeing any subsequent errors.

---

## 12. Nomi Adopt/Refuse/Adapt Table

| # | Design Decision | Action | Rationale |
|---|----------------|--------|-----------|
| 1 | **LSP server architecture** | Adopt Rust/TypeScript model: one language service, consumed by both compiler and LSP server. LSP server is a thin JSON-RPC wrapper over the semantic model. | Prevents semantic divergence between compiler and IDE. TypeScript proves this works at scale. |
| 2 | **Tree-sitter grammar** | Adopt as a first-class language artifact. Ship alongside the Lark grammar. Maintain semantic equivalence. | Tree-sitter is table stakes for modern editor integration (Neovim, Helix, Zed, VS Code). A language without a Tree-sitter grammar is invisible to half the editor ecosystem. |
| 3 | **Lossless CST vs lossy AST** | Adapt: use a lossy Python AST for compilation (current approach) but preserve trivia (comments, whitespace) in the surface AST and propagate spans through all stages. When producing API output for tools, include the surface AST span alongside the Python AST span. | Full CST preservation (like Swift libsyntax or Roslyn) is a major engineering investment. Span propagation through the pipeline gives 80% of the benefit at 20% of the cost. |
| 4 | **Diagnostic format** | Adopt structured diagnostics: `{code, severity, message, spans, because, suggestions, pipeline_stage}`. All pipeline stages emit into a `DiagnosticCollector`. Never emit a raw string. | The Rust/Swift model. Diagnostics as data enables JSON output, code actions, testing, and tool consumption. Nomi's existing design philosophy ("every layer inspectable") requires this. |
| 5 | **Error codes** | Adopt stable error codes from day one. Namespace by pipeline stage: `P` for parse, `L` for lowering, `D` for desugar, `T` for type/constraint check, `R` for runtime. | Error codes are cheap to allocate and expensive to retrofit. Rust (`E0382`), Scala 3 (`E007`), TypeScript (`TS2322`) all use them. |
| 6 | **Machine-applicable fix suggestions** | Adopt the Swift FixIt model: each suggestion includes a source edit (range + replacement text) and an applicability level (MachineApplicable, MaybeIncorrect, Unspecified). | AI agents need confidence levels for suggestions. MachineApplicable fixes can be applied blindly; MaybeIncorrect require review. |
| 7 | **Source maps across pipeline stages** | Adopt explicit span propagation: every desugar pass must produce a span mapping from output AST nodes back to input AST nodes. The `inspect` CLI should show the span chain for any output node. | Nomi's `SourceSpan` and `@captures_span` already exist. Extend this to all desugar passes. Without span propagation, multi-stage diagnostics degrade to "somewhere in the file." |
| 8 | **Expansion display (desugar trace)** | Adopt as a first-class inspection mode. `python3 -m tools.syntax.inspect --stage trace` shows each transformation step with before/after diffs. The notebook kernel's `%trace` command shows the pipeline trace for a cell. | Nomi's design philosophy demands this. The `inspect` CLI already exists; adding `--stage trace` and `--diff` extends it to full pipeline transparency. |
| 9 | **Semantic token design** | Adapt: add Nomi-specific token types (`constrainedParameter`, `blockParam`, `surfaceKeyword`, `loweredName`) alongside standard LSP token types. | Standard LSP token types (variable, parameter, type, function) cover 80% of needs. Nomi-specific types make the remaining 20% (constraints, blocks, lowered names) visually distinct. |
| 10 | **Pipeline query API** | Adopt a query-oriented API: `get_parse_tree(file, range)`, `get_surface_ast(file, range)`, `get_python_ast(file, range)`, `get_pipeline_trace(file, range)`, `get_diagnostics(file)`. Each returns structured JSON. | The API enables both the LSP server and the CLI to use the same query logic. AI tools can ask precise questions about specific source regions. |
| 11 | **Design fixture conventions** | Adopt rust-analyzer-style fixture tests with inline annotations (`$0` for cursor, `// error` for expected diagnostics, `// ^ type` for expected hover, `// --- code-action ---` for expected fixes). | Fixture-based tests are self-documenting and AI-readable. An AI agent can read a fixture and understand what the tooling should produce, without reading test harness code. |
| 12 | **Snapshot testing for diagnostics** | Adopt snapshot testing for full diagnostic output, with `--update-snapshots` flag. Separate golden tests (exact message match) from behavior tests (error on expected line). | Nomi already has interpreter regression snapshots. Extend the pattern to diagnostics and code actions. |
| 13 | **Notebook metadata for pipeline stages** | Adopt: the notebook kernel records pipeline stage information in cell metadata after execution (`pipeline_stages`, `surface_ast`, `python_ast`). The `%ast` magic shows the desugared AST; add `%trace` for the full pipeline. | Makes notebook cells self-documenting for AI tools. An AI agent reading a `.nomi.nb` can see not just source and output but the compiler's intermediate representations. |
| 14 | **Type annotation syntax** | Adopt from the start. Nomi's `name: constraint = value` already supports type annotations as a subset of constraints. | Having the syntax means AI tools have structured contracts from day one. Runtime-checked type annotations are a valid starting point; static checking can be added incrementally. |
| 15 | **Declaration files** | Adapt: generate `.nomi.d` files (machine-readable module APIs) as a compilation artifact, but make them optional. The LSP server should work with or without them. | TypeScript's `.d.ts` files prove the value of declaration files for tooling, but they require a stable ABI commitment. Nomi can start with optional declaration generation. |
| 16 | **IDE integration architecture** | Adapt: compiler produces semantic index files (`.nomi-semantic` JSON containing types, bindings, constraints, source spans). A thin LSP server reads these indexes, watches for changes, and re-runs the compiler on changed files. | Decouples LSP server latency from compiler throughput. The LSP server does not need to run the compiler; it reads the compiler's structured output. This is the most practical path for a prototype-stage language. |
| 17 | **Incremental computation** | Adopt for the LSP server. The compiler can be batch-oriented initially, but the LSP server must be incremental: cache analysis results per file, invalidate on change, and recompute only what depends on the changed file. | rust-analyzer's salsa framework is the gold standard, but even simple per-file caching with dependency tracking is a 10x improvement over re-analyzing the project on every keystroke. |
| 18 | **Error suppression mechanism** | Adopt `#nomi:ignore(E001)` or similar suppression syntax so AI agents can suppress known errors while iterating. | Without suppression, every error blocks further analysis. TypeScript's `@ts-ignore` and Rust's `#[allow(...)]` prove the pattern. |
| 19 | **Lossless AST for refactoring** | Refuse (for now): do not build a full lossless CST. Preserve trivia (comments) in span metadata and ensure desugar passes propagate spans. | Full lossless CST (Roslyn, Swift libsyntax) is a major engineering investment. Span propagation + comment preservation gives sufficient precision for initial tooling without the CST complexity. |
| 20 | **Proof-term emission** | Refuse (for now): do not emit full proof terms like Coq/Lean. Instead, emit structured pipeline traces that serve the same explanatory role without the formal verification guarantee. | Full proof terms require a formalized type theory and kernel checker. Pipeline traces provide the "show your work" benefit without the formal verification engineering cost. |

---

## Sources

- [Language Server Protocol Specification](https://microsoft.github.io/language-server-protocol/specifications/lsp/3.17/specification/)
- [LSP Semantic Tokens](https://microsoft.github.io/language-server-protocol/specifications/lsp/3.17/specification/#textDocument_semanticTokens)
- [Rust Compiler Development Guide — Diagnostics](https://rustc-dev-guide.rust-lang.org/diagnostics.html)
- [rust-analyzer Architecture](https://github.com/rust-lang/rust-analyzer/blob/master/docs/dev/architecture.md)
- [salsa: Incremental Computation Framework](https://salsa-rs.github.io/salsa/)
- [Tree-sitter Documentation](https://tree-sitter.github.io/tree-sitter/)
- [Tree-sitter Parsing Algorithm](https://tree-sitter.github.io/tree-sitter/using-parsers)
- [TypeScript Compiler API — TypeChecker](https://github.com/microsoft/TypeScript/wiki/Using-the-Compiler-API)
- [TypeScript Language Service](https://github.com/microsoft/TypeScript/wiki/Using-the-Language-Service-API)
- [Rust Error Code Index](https://doc.rust-lang.org/error_codes/error-index.html)
- [Swift Compiler — DiagnosticEngine](https://github.com/apple/swift/blob/main/docs/Diagnostics.md)
- [GHC Typed Holes](https://downloads.haskell.org/ghc/latest/docs/users_guide/exts/typed_holes.html)
- [GHC Debugging Flags](https://downloads.haskell.org/ghc/latest/docs/users_guide/debugging.html)
- [Jupyter nbformat Specification](https://nbformat.readthedocs.io/en/latest/format_description.html)
- [Clojure spec Guide — Explain](https://clojure.org/guides/spec)
- [Scala 3 Error Messages and -explain](https://docs.scala-lang.org/scala3/reference/changed-features/type-inference.html)
- [Python 3.11 Improved Error Messages](https://docs.python.org/3/whatsnew/3.11.html#whatsnew311-pep657)
- [Source Map V3 Specification](https://sourcemaps.info/spec.html)
- [Roslyn Syntax Tree API](https://docs.microsoft.com/en-us/dotnet/csharp/roslyn-sdk/work-with-syntax)
- [Elm Compiler Error Messages](https://elm-lang.org/news/compiler-errors-for-humans)
- [Zig Error Return Traces](https://ziglang.org/documentation/master/#Error-Return-Traces)
