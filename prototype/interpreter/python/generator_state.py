"""Public generator protocol for the hosted AST continuation adapter."""

from .continuation import Continuation, InjectedGeneratorExit


class CoroutineState:
    __slots__ = (
        "interpreter", "body", "env", "index", "return_value", "is_first_iteration",
        "paused_frames", "_processing_frame", "_pause_insertion_index", "_runner",
    )

    def __init__(self, interpreter, body, env):
        self.interpreter = interpreter
        self.body = body
        self.env = env
        self.index = 0
        self.return_value = None
        self.is_first_iteration = True
        # Retain these read-only-by-convention inspection fields for existing
        # clients. Continuation ownership no longer depends on a flattened queue.
        self.paused_frames = []
        self._processing_frame = None
        self._pause_insertion_index = 0
        self._runner = Continuation(interpreter, self).run()

    def __iter__(self):
        return self

    def __del__(self):
        # Host generator finalization must restore the source frame too.
        if hasattr(self, "_runner"):
            self.close()

    def __next__(self):
        return self.send(None)

    def _advance(self, operation, *args):
        with self.interpreter.this_env(self.env):
            try:
                value = operation(*args)
                self.is_first_iteration = False
                while True:
                    try:
                        self._handle_yield(value)
                    except Exception as error:
                        value = self._runner.throw(error)
                    else:
                        return value
            except StopIteration as stopped:
                self.return_value = stopped.value
                raise
            finally:
                if self._runner.gi_frame is None:
                    self.is_first_iteration = False

    def send(self, value):
        return self._advance(self._runner.send, value)

    def throw(self, exception, *args):
        if exception is GeneratorExit or isinstance(exception, GeneratorExit):
            error = exception(*args) if isinstance(exception, type) else exception
            if self.is_first_iteration or self._runner.gi_frame is None:
                return self._advance(self._runner.throw, error)
            return self._advance(self._runner.throw, InjectedGeneratorExit(error))
        return self._advance(self._runner.throw, exception, *args)

    def close(self):
        with self.interpreter.this_env(self.env):
            if self.is_first_iteration:
                self.is_first_iteration = False
                return self._runner.close()
            try:
                self._runner.throw(InjectedGeneratorExit(GeneratorExit()))
            except (GeneratorExit, InjectedGeneratorExit):
                return None
            except StopIteration as stopped:
                self.return_value = stopped.value
                return stopped.value
            raise RuntimeError("generator ignored GeneratorExit")

    def _handle_yield(self, value=None):
        """Nomi overrides this hook to run an attached block at a yield."""

    def get_lineno(self):
        if self.index < len(self.body):
            return getattr(self.body[self.index], "lineno", 1)
        return None
