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
