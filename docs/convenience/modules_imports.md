# Modules & Imports Convenience

> Normal form: Binding. Imports are name bindings; modules are containers of
> bindings. Python-compatible import syntax is implemented; module visibility
> and re-exports are design-settled.
>
> Deep research: [packaging_and_project_structure_deep_dive.md](../research/packaging_and_project_structure_deep_dive.md)
> (8-ecosystem survey: Python, Cargo, Go modules, Mix, npm, NuGet, Nix flakes, Maven),
> [security_and_trust_deep_dive.md](../research/security_and_trust_deep_dive.md)
> (content-addressed imports, supply-chain integrity).
>
> Companion: [design_lessons_and_integration.md §7.8](design_lessons_and_integration.md)
> for the package-management systemic pattern.

## Normal Form

Module and import features reduce to the binding normal form:

```text
import → bind an external module or name into the current scope
re-export → bind a name to the module's public surface
```

Imports are bindings. They should reuse binding semantics (name introduction,
shadowing rules, diagnostics) rather than defining a parallel name system.

## 1. Import Syntax (Python-Compatible)

Python import syntax is the current surface. It covers the common cases.

```nomi
import os
import numpy as np
from collections import defaultdict
from . import sibling
from ..parent import something
```

**Status:** implemented (Python-compatible).

## 2. Module Visibility and Re-Exports

### Module Visibility (`pub`)

By default, module-level names are private to the module. The `pub` keyword
makes a name visible to importing modules:

```nomi
# Private (default)
func helper(): ...

# Public
pub func api_function(): ...

pub data Config:
    host: str
    port: int
```

This follows Rust's `pub` / Go's exported-name convention (capitalized = public
in Go; `pub` keyword in Nomi). The `pub` keyword is explicit rather than
convention-based because it makes visibility visible at the definition site.

### Re-Exports

A module can re-export a name imported from another module, enabling facade
patterns and controlled public surfaces:

```nomi
# Re-export for public API surface
pub import some_internal_module.some_function
```

Or, with explicit naming:

```nomi
from .internal.impl import process
pub use process  # re-export
```

This is Rust's `pub use` model: re-exports are explicit, visible at the module
surface, and participate in documentation generation.

**Design principles (from cross-language synthesis):**

- **Files are modules.** Each `.nomi` file is one module. The file path IS the
  module path (Python/Go model, not Rust's `mod` declaration model).
- **No separate package manifest is required for simple modules.** A directory
  with `.nomi` files is a package. A `package.nomi` file can add metadata
  (edition, version, dependencies) but is optional for single-file packages.
- **No code execution during import.** Fetching a dependency is download +
  hash verification only (Nix model). Import resolution and compilation
  happen before any user code runs.
- **Domain-name import paths** for external dependencies:
  `import "example.com/user/pkg"` (Go/Deno model). No bare-name global
  namespace.

**Source reference:** Rust `pub use`, JavaScript `export { x } from './mod'`,
Go modules, Deno URL imports, Nix fixed-output derivations.
**Status:** design-settled; implementation requires packaging infrastructure.

## 3. Wildcard / Star Imports

Import all public names from a module.

```nomi
from module import *
```

**Status:** implemented (Python-compatible). Use sparingly — explicit imports
improve local reasoning.

## 4. Grouped / Multi-Import

Group related imports for readability.

**Source reference:** Go `import ( ... )`, Rust `use { ... }`.

**Status:** library-first. Python multi-line imports cover the readability
need; grouped syntax adds a new form for marginal gain.

## 5. Qualified / Scoped Imports

Import a module without polluting the namespace.

```nomi
import os           # access via os.path.join()
```

**Status:** implemented (Python-compatible). Python's `import module` already
provides qualified access.

## 6. Synthesis Decisions

| Candidate | Status | Decision |
|-----------|--------|----------|
| Import aliases (`import x as y`) | implemented | Python-compatible. |
| Relative imports (`from . import x`) | implemented | Python-compatible. |
| Wildcard imports (`from x import *`) | implemented | Python-compatible; discourage as style. |
| Re-exports (`pub import` / `pub use`) | design-settled | Rust `pub use` model; explicit re-exports at module surface. |
| Module visibility (`pub`) | design-settled | `pub` keyword at definition site; private by default. |
| Grouped imports | library-first | Python multi-line imports are sufficient. |
| Conditional / optional imports | library-first | Use `try/except ImportError`; no syntax needed. |
| Domain-name import paths | design-settled | `import "example.com/user/pkg"` for external deps. |
| No code execution during import | design-settled | Nix model: download + hash verify only. |
| Content-addressed imports | design-settled | `import ".../pkg.nomi" sha256:abc...` for integrity. |
| Files as modules | design-settled | One `.nomi` file = one module; path = module path. |

## 7. Architecture Rule

Do not add many import spellings before module semantics and export policy are
stable. The current Python-compatible surface is adequate. The next increment
should be diagnostics and explicit re-export policy, not more syntax.

## 8. Research Sources

- [design_lessons_and_integration.md §7.8](design_lessons_and_integration.md) — package management as part of language design
