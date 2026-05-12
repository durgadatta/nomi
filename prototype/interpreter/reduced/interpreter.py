"""
Reduced interpreter.

Inherits from NomiInterpreter. Each reduction commit removes one or more
``eval_*`` methods from this interpreter after the corresponding syntactic
form is desugared at parse time (see prototypical/parser/nomi/desugar/).

Every removed method is replaced with an override that raises
NotImplementedError so that any AST form reaching this interpreter is
caught as an error rather than silently passing through to the parent.
"""

from ..nomi.interpreter import Interpreter as NomiInterpreter


class Interpreter(NomiInterpreter):

    # --- augassign -------------------------------------------------------
    # Desugarer: prototype/parser/nomi/desugar/augassign.py
    def eval_AugAssign(self, node):
        raise NotImplementedError(
            "Augmented assignment should be desugared at parse time. "
            "Desugarer transforms x+=y into x=x+y."
        )

    # --- assert ----------------------------------------------------------
    # Desugarer: prototype/parser/nomi/desugar/assert_.py
    def eval_Assert(self, node):
        raise NotImplementedError(
            "Assert should be desugared at parse time. "
            "Desugarer transforms assert into if/raise."
        )

    # --- pass ------------------------------------------------------------
    # Desugarer: prototype/parser/nomi/desugar/pass_.py
    def eval_Pass(self, node):
        raise NotImplementedError(
            "Pass should be desugared at parse time. "
            "Desugarer replaces pass with a constant expression."
        )

    # --- with ------------------------------------------------------------
    # Desugarer: prototype/parser/nomi/desugar/with_.py
    def eval_With(self, node, *, state=None, generator_state=None):
        raise NotImplementedError(
            "With should be desugared at parse time. "
            "Desugarer expands with into enter/assign/try/except/else."
        )

    # --- f-strings -------------------------------------------------------
    # Desugarer: prototype/parser/nomi/desugar/fstring.py
    def eval_JoinedStr(self, node):
        raise NotImplementedError(
            "F-strings should be desugared at parse time. "
            "Desugarer expands f-strings into concatenation and format calls."
        )

    def eval_FormattedValue(self, node):
        raise NotImplementedError(
            "F-strings should be desugared at parse time. "
            "Desugarer expands f-strings into concatenation and format calls."
        )
