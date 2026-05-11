from ..nomi.interpreter import Interpreter as NomiInterpreter


class Interpreter(NomiInterpreter):

    def eval_AugAssign(self, node):
        raise NotImplementedError(
            "Augmented assignment should be desugared at parse time. "
            "Desugarer transforms x+=y into x=x+y."
        )
