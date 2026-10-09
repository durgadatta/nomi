"""Bounded continuation adapter for the hosted compatibility interpreter.

Host generator frames retain child values and deliver child failures to their
waiting AST parents. Source is never compiled or executed by the host. Ordinary
subtrees still use the existing interpreter; only paths to a yield use this
adapter. This is a backend mechanism, not Nomi's target completion contract.
"""

import ast
import sys
from contextlib import ExitStack

from .context_managers import context_methods
from .signals import BreakException, ContinueException, ControlException, ReturnException


class SourceException(BaseException):
    """Transport an actual source error through private host generator frames."""

    def __init__(self, error):
        self.error = error

    def restore_context(self, context=None):
        restore_source_context(self.error, self.__context__ if context is None else context)
        return self.error


class ProtocolFailure:
    """Expose a delegation lookup failure without resuming the source yield."""

    def __init__(self, error):
        self.error = error


class ProtocolWarning:
    """Report an ignored delegation close lookup failure in the public adapter."""

    def __init__(self, error, iterator):
        self.error = error
        self.iterator = iterator


def restore_source_context(error, context):
    while isinstance(context, (SourceException, ControlException)):
        context = context.error if isinstance(context, SourceException) else context.__context__
    if context is not None and context is not error:
        error.__context__ = context


def source_operation(operation, /, *args, **kwargs):
    """Keep host generator protocol exceptions from escaping a source operation."""
    try:
        return operation(*args, **kwargs)
    except (StopIteration, GeneratorExit) as error:
        raise SourceException(error) from None


def enclosing_scope_children(node):
    """Visit definition-time expressions without visiting nested function bodies."""
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda)):
        return iter([
            *getattr(node, "decorator_list", []), *node.args.defaults,
            *(item for item in node.args.kw_defaults if item is not None),
        ])
    if isinstance(node, ast.ClassDef):
        return iter([*node.decorator_list, *node.bases, *node.keywords, *node.body])
    return ast.iter_child_nodes(node)


def contains_scope_yield(node):
    if isinstance(node, (ast.Yield, ast.YieldFrom)):
        return True
    return any(contains_scope_yield(child) for child in enclosing_scope_children(node))


class Continuation:
    # Admit suspended paths explicitly. Other shapes are rejected before any
    # generator-body effect, rather than replayed or partially evaluated.
    _HANDLERS = {
        ast.Yield: "_yield", ast.YieldFrom: "_yield_from",
        ast.Expr: "_expr", ast.Assign: "_assign", ast.Return: "_return",
        ast.BinOp: "_binary", ast.Call: "_call",
        ast.If: "_if", ast.For: "_for", ast.While: "_while",
        ast.Try: "_try", ast.With: "_with",
    }
    _CONTAINERS = (ast.keyword, ast.Starred, ast.ExceptHandler, ast.withitem)

    def __init__(self, interpreter, owner):
        self.interpreter = interpreter
        self.owner = owner
        self.active = set()

    def run(self):
        for statement in self.owner.body:
            self._validate(statement)
        source_error = None
        try:
            for index, statement in enumerate(self.owner.body):
                self.owner.index = index
                yield from self.evaluate(statement)
        except ReturnException as transfer:
            return transfer.value
        except SourceException as transfer:
            source_error = transfer.restore_context()
        finally:
            self.owner.index = len(self.owner.body)
        if source_error is not None:
            # Only this public generator boundary applies host StopIteration rules.
            raise source_error

    def _validate(self, node):
        if not isinstance(node, ast.AST):
            return False
        children = [self._validate(child) for child in enclosing_scope_children(node)]
        active = isinstance(node, (ast.Yield, ast.YieldFrom)) or any(children)
        if not active:
            return False
        if type(node) not in self._HANDLERS and not isinstance(node, self._CONTAINERS):
            self._unsupported(node)
        if isinstance(node, ast.Assign) and any(target in self.active for target in node.targets):
            self._unsupported(node, "suspending assignment target")
        if isinstance(node, ast.For) and node.target in self.active:
            self._unsupported(node, "suspending loop target")
        if isinstance(node, ast.With) and any(item.optional_vars in self.active for item in node.items):
            self._unsupported(node, "suspending context target")
        handler = getattr(self.interpreter, f"eval_{type(node).__name__}", None)
        if getattr(handler, "_nomi_requires_desugaring", False):
            handler(node)
        self.active.add(node)
        return True

    def _unsupported(self, node, detail=None):
        raise NotImplementedError(
            f"Hosted generator suspension through {detail or type(node).__name__} "
            f"is not supported at line {self.interpreter.get_lineno(node)}"
        )

    def evaluate(self, node):
        if node not in self.active:
            return source_operation(self.interpreter.eval, node)
        try:
            return (yield from getattr(self, self._HANDLERS[type(node)])(node))
        except self.interpreter.pass_through_exceptions:
            raise
        except Exception as error:
            raise RuntimeError(
                f"Error evaluating {type(node).__name__} at line "
                f"{self.interpreter.get_lineno(node)}: {error}"
            ) from error

    def block(self, statements):
        for statement in statements:
            yield from self.evaluate(statement)

    def _yield(self, node):
        value = yield from self.evaluate(node.value)
        active_error = sys.exception()
        try:
            return (yield value)
        except SourceException as transfer:
            transfer.restore_context(active_error)
            raise
        except BaseException as error:
            if not isinstance(error, ControlException):
                restore_source_context(error, active_error)
            raise

    def _receive(self, value):
        try:
            return (yield value), None
        except SourceException as transfer:
            return None, transfer.restore_context()
        except BaseException as error:
            return None, error

    def _yield_from(self, node):
        iterator = source_operation(iter, (yield from self.evaluate(node.value)))
        try:
            value = next(iterator)
        except StopIteration as stopped:
            return stopped.value
        while True:
            sent, injected = yield from self._receive(value)
            while True:
                if injected is not None:
                    if isinstance(injected, GeneratorExit):
                        lookup_error = None
                        try:
                            close = getattr(iterator, "close", None)
                        except BaseException as error:
                            lookup_error = error
                        if lookup_error is not None:
                            yield ProtocolWarning(lookup_error, iterator)
                            close = None
                        if close is not None:
                            source_operation(close)
                        raise SourceException(injected) from None
                    lookup_error = None
                    try:
                        throw = getattr(iterator, "throw", None)
                    except BaseException as error:
                        lookup_error = error
                    if lookup_error is not None:
                        sent, injected = yield from self._receive(ProtocolFailure(lookup_error))
                        continue
                    if throw is None:
                        if isinstance(injected, StopIteration):
                            raise SourceException(injected) from None
                        raise injected
                    try:
                        value = throw(injected)
                    except StopIteration as stopped:
                        return stopped.value
                    except GeneratorExit as error:
                        raise SourceException(error) from None
                else:
                    try:
                        value = next(iterator) if sent is None else iterator.send(sent)
                    except StopIteration as stopped:
                        return stopped.value
                    except GeneratorExit as error:
                        raise SourceException(error) from None
                break

    def _expr(self, node):
        return (yield from self.evaluate(node.value))

    def _assign(self, node):
        value = yield from self.evaluate(node.value)
        for target in node.targets:
            source_operation(self.interpreter.assign_target, target, value)

    def _return(self, node):
        value = yield from self.evaluate(node.value)
        raise ReturnException(value)

    def _binary(self, node):
        left = yield from self.evaluate(node.left)
        right = yield from self.evaluate(node.right)
        return source_operation(self.interpreter.apply_operator, left, node.op, right, node)

    def _call(self, node):
        interpreter = self.interpreter
        function = yield from self.evaluate(node.func)
        arguments, keywords = [], {}
        for argument in node.args:
            value_node = argument.value if isinstance(argument, ast.Starred) else argument
            value = yield from self.evaluate(value_node)
            source_operation(interpreter._append_positional_value, arguments, argument, value)
        for keyword in node.keywords:
            if keyword.value in self.active:
                value = yield from self.evaluate(keyword.value)
            else:
                value = source_operation(interpreter._keyword_value, keyword)
            source_operation(interpreter._merge_keyword_value, keywords, keyword, value,
                             call_node=node)
        return source_operation(function, *arguments, **keywords)

    def _if(self, node):
        condition = yield from self.evaluate(node.test)
        yield from self.block(node.body if source_operation(bool, condition) else node.orelse)

    def _for(self, node):
        iterable = yield from self.evaluate(node.iter)
        for value in source_operation(iter, iterable):
            source_operation(self.interpreter.assign_target, node.target, value)
            try:
                yield from self.block(node.body)
            except ContinueException:
                continue
            except BreakException:
                break
        else:
            yield from self.block(node.orelse)

    def _while(self, node):
        while source_operation(bool, (yield from self.evaluate(node.test))):
            try:
                yield from self.block(node.body)
            except ContinueException:
                continue
            except BreakException:
                break
        else:
            yield from self.block(node.orelse)

    def _transfer_block(self, statements):
        try:
            yield from self.block(statements)
        except ControlException as transfer:
            return transfer

    def _try(self, node):
        pending_transfer = None
        body_error = None
        completion_error = None
        try:
            try:
                pending_transfer = yield from self._transfer_block(node.body)
            except BaseException as transfer:
                body_error = transfer.restore_context() if isinstance(transfer, SourceException) else transfer
            if body_error is not None:
                try:
                    raise body_error
                except BaseException as error:
                    for handler in node.handlers:
                        kind = yield from self.evaluate(handler.type)
                        if handler.type is None or self.interpreter._matches_exception(error, kind):
                            if handler.name:
                                source_operation(self.interpreter.current_env.set,
                                                 handler.name, error)
                            pending_transfer = yield from self._transfer_block(handler.body)
                            break
                    else:
                        raise
            elif pending_transfer is None:
                pending_transfer = yield from self._transfer_block(node.orelse)
        except BaseException as transfer:
            completion_error = transfer.restore_context() if isinstance(transfer, SourceException) else transfer
        try:
            try:
                if completion_error is not None:
                    raise completion_error
            finally:
                yield from self.block(node.finalbody)
        except (StopIteration, GeneratorExit) as error:
            raise SourceException(error) from None
        if pending_transfer is not None:
            raise pending_transfer

    def _with(self, node):
        yield from self._with_scope(node.items, node.body)

    def _with_scope(self, items, body):
        if not items:
            yield from self.block(body)
            return
        state = {"stack": ExitStack(), "suppressed_cleanup": False}
        pending_transfer = None
        completion_error = None
        try:
            item = items[0]
            context = yield from self.evaluate(item.context_expr)
            enter, exit_method = source_operation(context_methods, context)
            value = source_operation(enter)

            def release(*info):
                result = exit_method(*info)
                if info[1] is None:
                    return False
                suppressed = bool(result)
                if suppressed:
                    state["suppressed_cleanup"] = True
                return suppressed

            state["stack"].push(release)
            if item.optional_vars:
                source_operation(self.interpreter.assign_target, item.optional_vars, value)
            yield from self._with_scope(items[1:], body)
        except ControlException as transfer:
            pending_transfer = transfer
        except BaseException as transfer:
            completion_error = transfer.restore_context() if isinstance(transfer, SourceException) else transfer
        if completion_error is not None:
            # Restore the actual active source error for host context protocols.
            try:
                raise completion_error
            except BaseException as error:
                if not source_operation(state["stack"].__exit__,
                                        type(error), error, error.__traceback__):
                    if isinstance(error, (StopIteration, GeneratorExit)):
                        raise SourceException(error) from None
                    raise
            return
        suppressed = source_operation(self.interpreter._close_without_error, state)
        if not suppressed and pending_transfer is not None:
            raise pending_transfer
