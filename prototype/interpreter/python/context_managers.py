import ast
import sys
from copy import copy
from contextlib import ExitStack

from .signals import ControlException, YieldException, YieldFromException


def context_methods(context_obj):
    """Resolve the legacy protocol on the type, binding its descriptors once."""
    cls = type(context_obj)

    def resolve(name):
        for base in type.__getattribute__(cls, "__mro__"):
            namespace = type.__getattribute__(base, "__dict__")
            if name in namespace:
                descriptor = namespace[name]
                try:
                    getter = type.__getattribute__(type(descriptor), "__get__")
                except AttributeError:
                    getter = None
                return getter(descriptor, context_obj, cls) if getter else descriptor
        raise TypeError(f"'{cls.__name__}' object does not support the context manager protocol")

    # Capture exit before enter; successful acquisition immediately registers it.
    exit_method = resolve("__exit__")
    return resolve("__enter__"), exit_method


class ContextManagerMixin:
    def eval_With(self, node: ast.With, *, state=None, generator_state=None) -> None:
        if state is None:
            items, body = node.items, node.body
            if len(items) > 1:
                nested = copy(node)
                nested.items = items[1:]
                items, body = items[:1], [nested]
            stack = ExitStack()
            state = {'stack': stack, 'body_index': 0, 'node': node,
                     'body': body, 'suppressed_cleanup': False}
            pending_transfer = None
            try:
                for item in items:
                    enter, exit_method = context_methods(self.eval(item.context_expr))
                    value = enter()

                    def release(*info, method=exit_method):
                        result = method(*info)
                        if info[1] is None:
                            return False
                        suppressed = bool(result)
                        if suppressed:
                            state['suppressed_cleanup'] = True
                        return suppressed

                    stack.push(release)
                    if item.optional_vars:
                        self.assign_target(item.optional_vars, value)
            except ControlException:
                pending_transfer = sys.exception()
            except BaseException as error:
                if not stack.__exit__(type(error), error, error.__traceback__):
                    raise
                return

            if pending_transfer is not None:
                if not self._close_without_error(state):
                    raise pending_transfer
                return

        self._execute_with_body(state.get('body', node.body), state=state, generator_state=generator_state)

    def _execute_with_body(self, body, *, state, generator_state=None):
        stack = state['stack']
        pending_transfer = None
        try:
            if generator_state is not None:
                generator_state.raise_injected_exception()
            index = state['body_index']
            while index < len(body):
                try:
                    self.eval(body[index], generator_state=generator_state)
                    index += 1
                except (YieldException, YieldFromException):
                    state['body_index'] = index + 1
                    if generator_state is not None:
                        generator_state.pause(state['node'], state)
                    raise
        except (YieldException, YieldFromException):
            # Suspension retains the acquired scopes; it is not a completion.
            raise
        except ControlException:
            pending_transfer = sys.exception()
        except BaseException as error:
            if not stack.__exit__(type(error), error, error.__traceback__):
                raise
        else:
            self._close_without_error(state)

        if pending_transfer is not None:
            if not self._close_without_error(state):
                raise pending_transfer

    def _close_without_error(self, state):
        context = sys.exception()
        while isinstance(context, ControlException):
            context = context.__context__
        try:
            state['stack'].close()
        except BaseException as error:
            # ExitStack clears ambient context on no-error close. Restore real
            # context without exposing pending private control signals.
            tail = error
            seen = {id(tail)}
            while tail.__context__ is not None and id(tail.__context__) not in seen:
                tail = tail.__context__
                seen.add(id(tail))
            if tail.__context__ is None and context is not None and id(context) not in seen:
                tail.__context__ = context
            raise
        return state['suppressed_cleanup']
