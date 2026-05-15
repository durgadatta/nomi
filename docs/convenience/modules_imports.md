# Modules & Imports Convenience

> Normal form: Binding. Imports are name bindings; modules are containers of
> bindings. Python-compatible import syntax is implemented.
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

## 2. Re-Exports

Export a name imported from another module. Enables module facade patterns and
controlled public surfaces.

**Source reference:** Rust `pub use`, JavaScript `export { x } from './mod'`.

**Status:** design-needed. Depends on module visibility and export policy being
stable.

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
| Re-exports | design-needed | Wait for module visibility and export policy. |
| Grouped imports | library-first | Python multi-line imports are sufficient. |
| Conditional / optional imports | library-first | Use `try/except ImportError`; no syntax needed. |
| Module-level visibility (`pub`) | design-needed | Part of broader module semantics design. |

## 7. Architecture Rule

Do not add many import spellings before module semantics and export policy are
stable. The current Python-compatible surface is adequate. The next increment
should be diagnostics and explicit re-export policy, not more syntax.

## 8. Research Sources

- [design_lessons_and_integration.md §7.8](design_lessons_and_integration.md) — package management as part of language design
