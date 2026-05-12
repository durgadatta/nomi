# Modules & Imports Convenience

## Import Aliases

Shorten or disambiguate imported names.

**Python / Kotlin / JavaScript**:

```python
import numpy as np
from collections import defaultdict as dd
```

```kotlin
import java.util.UUID as JavaUUID
```

```javascript
import { reallyLongFunctionName as fn } from './module'
```

**Nomi** — Python import syntax already supported.

---

## Re-Exports

Export something imported from another module.

**Rust / JavaScript / TypeScript**:

```rust
pub use self::inner::PublicType;
pub use crate::utils::helper;
```

```javascript
export { something } from './module'
export { default as MyClass } from './module'
```

---

## Wildcard / Star Imports

Import all public names from a module.

**Python / Rust / JavaScript**:

```python
from module import *
```

```rust
use crate::module::*;
```

**Nomi** — Python `from x import *` supported.

---

## Multi-Import / Grouped Import

Group related imports for readability.

**Go / Rust**:

```go
import (
    "fmt"
    "os"
    "strings"
)
```

```rust
use std::{
    collections::HashMap,
    fs::File,
    io::{self, Read},
};
```

---

## Qualified / Scoped Imports

Import a module without polluting the namespace.

**Python / OCaml / Haskell**:

```python
import os          # access via os.path.join()
import numpy as np
```

```haskell
import qualified Data.Map as Map   -- Map.lookup, Map.insert
```

---

## Conditional / Optional Imports

Import only if available.

**Python**:

```python
try:
    import orjson as json
except ImportError:
    import json
```

---

## Relative Imports

Import from sibling or parent packages.

**Python / JavaScript**:

```python
from . import sibling
from ..parent import something
```

**Nomi** — Python relative imports work.

---

## Implementation Priority

| Feature | Effort | Status |
|---------|--------|--------|
| Import aliases | already | done |
| Re-exports | medium | not started |
| Wildcard imports | already | done |
| Grouped imports | low | not started |
| Qualified imports | already | done |
| Relative imports | already | done |
