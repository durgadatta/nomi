"""Public generator protocol for the hosted AST continuation adapter."""

import sys
import traceback
from types import SimpleNamespace, TracebackType

from .continuation import Continuation, ProtocolFailure, ProtocolWarning, SourceException


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
                    value = self._drive_protocol(value)
                    if isinstance(value, ProtocolFailure):
                        raise value.error
                    try:
                        self._handle_yield(value)
                    except Exception as error:
                        value = self._throw_into_runner(error)
                    else:
                        return value
            except StopIteration as stopped:
                if self._runner.gi_frame is None:
                    self.return_value = stopped.value
                raise
            finally:
                if self._runner.gi_frame is None:
                    self.is_first_iteration = False

    def _drive_protocol(self, value):
        while isinstance(value, ProtocolWarning):
            self._report_unraisable(value)
            value = self._runner.send(None)
        return value

    @staticmethod
    def _report_unraisable(warning):
        try:
            label = repr(warning.iterator)
        except BaseException:
            label = f"<{type(warning.iterator).__name__}>"
        record = SimpleNamespace(
            exc_type=type(warning.error), exc_value=warning.error,
            exc_traceback=warning.error.__traceback__,
            err_msg=f"Exception ignored while closing generator {label}", object=None,
        )
        try:
            if sys.unraisablehook is sys.__unraisablehook__:
                # CPython's native hook-argument constructor is private.
                print(record.err_msg + ":", file=sys.stderr)
                traceback.print_exception(warning.error, file=sys.stderr)
            else:
                sys.unraisablehook(record)
        except BaseException as error:
            try:
                print("Exception ignored in sys.unraisablehook:", file=sys.stderr)
                traceback.print_exception(error, file=sys.stderr)
            except BaseException:
                pass

    def send(self, value):
        return self._advance(self._runner.send, value)

    def throw(self, exception, *args):
        return self._advance(self._throw_into_runner, exception, *args)

    def _throw_into_runner(self, exception, *args):
        if (isinstance(exception, (StopIteration, GeneratorExit))
                or isinstance(exception, type) and issubclass(exception, (StopIteration, GeneratorExit))):
            if len(args) > 2:
                raise TypeError("throw expected at most 3 arguments")
            if len(args) > 1 and args[1] is not None and not isinstance(args[1], TracebackType):
                raise TypeError("throw() third argument must be a traceback object")
            value = args[0] if args else None
            if isinstance(exception, type):
                if isinstance(value, exception):
                    error = value
                elif value is None:
                    error = exception()
                elif isinstance(value, tuple):
                    error = exception(*value)
                else:
                    error = exception(value)
            else:
                if value is not None:
                    raise TypeError("instance exception may not have a separate value")
                error = exception
            if len(args) > 1 and args[1] is not None:
                error = BaseException.with_traceback(error, args[1])
            if self.is_first_iteration or self._runner.gi_frame is None:
                return self._runner.throw(error)
            return self._runner.throw(SourceException(error))
        return self._runner.throw(exception, *args)

    def close(self):
        with self.interpreter.this_env(self.env):
            if self._runner.gi_frame is None:
                return None
            if self.is_first_iteration:
                self.is_first_iteration = False
                return self._runner.close()
            try:
                self._drive_protocol(self._runner.throw(SourceException(GeneratorExit())))
            except GeneratorExit:
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
