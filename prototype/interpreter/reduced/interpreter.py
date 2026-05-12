"""
Reduced interpreter.

Inherits from NomiInterpreter. Each reduction commit removes one or more
``eval_*`` methods from this interpreter after the corresponding syntactic
form is desugared at parse time (see prototype/parser/nomi/desugar/).

Every removed method is replaced with an override that raises
NotImplementedError so that any AST form reaching this interpreter is
caught as an error rather than silently passing through to the parent.

The set of overridden methods is auto-derived from the desugar pipeline's
``removed_node_types`` metadata so the two stay in sync.
"""

import ast

from ..nomi.interpreter import Interpreter as NomiInterpreter
from ...parser.nomi.desugar.pipeline import get_removed_node_types


class Interpreter(NomiInterpreter):
    pass


# --- Auto-generated NotImplementedError overrides ---
# These match the removed_node_types declared by the desugar pipeline.

for _node_type in sorted(get_removed_node_types(), key=lambda t: t.__name__):
    _method_name = f'eval_{_node_type.__name__}'

    def _make_stub(node_type):
        """Closure factory so each override captures the right node type."""
        def _stub(self, node, *, state=None, generator_state=None):
            raise NotImplementedError(
                f"{node_type.__name__} should be desugared at parse time. "
                f"Check the desugar pipeline in prototype/parser/nomi/desugar/."
            )
        return _stub

    setattr(Interpreter, _method_name, _make_stub(_node_type))
