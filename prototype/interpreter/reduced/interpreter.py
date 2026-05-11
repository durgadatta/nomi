from ..nomi.interpreter import Interpreter as NomiInterpreter


class Interpreter(NomiInterpreter):

    def eval_AugAssign(self, node):
        raise NotImplementedError(
            "Augmented assignment should be desugared at parse time. "
            "Desugarer transforms x+=y into x=x+y."
        )

    def eval_Assert(self, node):
        raise NotImplementedError(
            "Assert should be desugared at parse time. "
            "Desugarer transforms assert into if/raise."
        )

    def eval_Pass(self, node):
        raise NotImplementedError(
            "Pass should be desugared at parse time. "
            "Desugarer replaces pass with a constant expression."
        )

    def eval_With(self, node, *, state=None, generator_state=None):
        raise NotImplementedError(
            "With should be desugared at parse time. "
            "Desugarer expands with into enter/assign/try/except/else."
        )
