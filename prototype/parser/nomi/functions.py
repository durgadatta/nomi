"""Nomi-specific AST-lowering mixin.

Composed dynamically from the syntax feature registry
(prototype/syntax/features.py).  Each lowering module lives under
``prototype/parser/nomi/lowering/`` and declares its mixin in the
feature manifest.

To add a new lowering: create the module, then add one entry to
BUILTIN_FEATURES in prototype/syntax/features.py.  No need to edit
this file.
"""

from prototype.syntax.features import get_lowering_mixins

# Build the mixin from all lowering features in the registry.
# Mixins are ordered left-to-right, matching their declaration order
# in BUILTIN_FEATURES.  Later mixins can override methods from earlier ones.
_lowering_bases = tuple(get_lowering_mixins())

# Build FunctionsMixin dynamically so the class attribute name is
# meaningful for debugging and documentation.
FunctionsMixin = type("FunctionsMixin", _lowering_bases, {})
