import ast
from .signals import YieldException

class BindingMixin:
    # --- assign_target dispatch table -----------------------------------
    # Maps AST node type → method name.  Subclasses extend this dict to
    # register new assignment-target forms without touching the dispatch.
    _ASSIGN_TARGET_DISPATCH = {
        ast.Name: '_assign_name',
        ast.Attribute: '_assign_attr',
        ast.Subscript: '_assign_subscript',
        ast.Tuple: '_assign_sequence',
        ast.List: '_assign_sequence',
        ast.Starred: '_assign_starred',
    }

    # --- del_target dispatch table --------------------------------------
    _DEL_TARGET_DISPATCH = {
        ast.Name: '_del_name',
        ast.Attribute: '_del_attr',
        ast.Subscript: '_del_subscript',
    }

    def _iter_unpack_value(self, value, target):
        try:
            return iter(value)
        except TypeError as e:
            raise TypeError(f"Cannot unpack non-iterable {type(value).__name__} at line {self.get_lineno(target)}") from e

    def _starred_indices(self, elts, target):
        star_indices = [i for i, elt in enumerate(elts) if isinstance(elt, ast.Starred)]
        if len(star_indices) > 1:
            raise SyntaxError(f"multiple starred expressions in assignment at line {self.get_lineno(target)}")
        return star_indices

    def _assign_plain_sequence(self, elts, iterator, target):
        needed = len(elts)
        got = []
        try:
            for _ in range(needed):
                got.append(next(iterator))
        except StopIteration:
            raise ValueError(f"Not enough values to unpack (expected {needed}) at line {self.get_lineno(target)}")

        try:
            next(iterator)
            raise ValueError(f"Too many values to unpack (expected {needed}) at line {self.get_lineno(target)}")
        except StopIteration:
            pass

        for subtarget, subval in zip(elts, got):
            self.assign_target(subtarget, subval)

    def _assign_starred_sequence(self, elts, star_i, iterator, target):
        before = elts[:star_i]
        star = elts[star_i]
        after = elts[star_i + 1 :]

        before_vals = []
        try:
            for _ in before:
                before_vals.append(next(iterator))
        except StopIteration:
            min_needed = len(before) + len(after)
            raise ValueError(
                f"Not enough values to unpack (expected at least {min_needed}) at line {self.get_lineno(target)}"
            )

        rest = list(iterator)
        if len(rest) < len(after):
            min_needed = len(before) + len(after)
            raise ValueError(
                f"Not enough values to unpack (expected at least {min_needed}) at line {self.get_lineno(target)}"
            )

        if after:
            star_vals = rest[: len(rest) - len(after)]
            after_vals = rest[-len(after) :]
        else:
            star_vals = rest
            after_vals = []

        for subtarget, subval in zip(before, before_vals):
            self.assign_target(subtarget, subval)
        self.assign_target(star.value, list(star_vals))
        for subtarget, subval in zip(after, after_vals):
            self.assign_target(subtarget, subval)

    def _assign_sequence_target(self, target, value):
        elts = target.elts
        star_indices = self._starred_indices(elts, target)
        iterator = self._iter_unpack_value(value, target)

        if not star_indices:
            self._assign_plain_sequence(elts, iterator, target)
        else:
            self._assign_starred_sequence(elts, star_indices[0], iterator, target)

    def del_target(self, node: ast.expr) -> None:
        handler = self._DEL_TARGET_DISPATCH.get(type(node))
        if handler:
            return getattr(self, handler)(node)
        raise NotImplementedError(
            f"Delete target {node.__class__.__name__} not supported "
            f"at line {self.get_lineno(node)}"
        )

    def _del_name(self, node):
        self.current_env.delete(node.id)

    def _del_attr(self, node):
        try:
            delattr(self.eval(node.value), node.attr)
        except AttributeError as e:
            raise AttributeError(
                f"Cannot delete attribute '{node.attr}' "
                f"at line {self.get_lineno(node)}: {str(e)}"
            ) from e

    def _del_subscript(self, node):
        try:
            del self.eval(node.value)[self.eval(node.slice)]
        except (IndexError, KeyError) as e:
            raise IndexError(
                f"Subscript deletion error at line "
                f"{self.get_lineno(node)}: {str(e)}"
            ) from e

    def eval_Assign(self, node: ast.Assign, *, state=None, generator_state=None) -> None:
        """
        Evaluate assignment statements, supporting tuple/list unpacking and starred targets.
        """
        if state is None:
            # First time - try to evaluate the value
            try:
                value = self.eval(node.value, generator_state=generator_state)
            except YieldException as ye:
                generator_state.pause(node, 'awaiting_value')
                raise ye       
        elif state == "awaiting_value":
            value = generator_state.get_sent_value()
        else:
            value = self.eval(node.value)

        for target in node.targets:
            self.assign_target(target, value)

    def eval_AugAssign(self, node: ast.AugAssign) -> None:
        old_value = self.eval_target(node.target)
        op_value = self.eval(node.value)
        new_value = self.apply_operator(old_value, node.op, op_value, node)
        self.assign_target(node.target, new_value)

    def eval_AnnAssign(self, node: ast.AnnAssign) -> None:
        if node.value:
            value = self.eval(node.value)
            self.assign_target(node.target, value)

    def assign_target(self, target, value):
        """Recursive assignment helper. Supports: Name, Attribute, Subscript,
        Tuple/List unpacking (from any iterable), and Starred targets.
        New target types are registered via _ASSIGN_TARGET_DISPATCH."""
        handler = self._ASSIGN_TARGET_DISPATCH.get(type(target))
        if handler:
            return getattr(self, handler)(target, value)
        raise TypeError(
            f"Unsupported assignment target {target.__class__.__name__} "
            f"at line {self.get_lineno(target)}"
        )

    def _assign_name(self, target, value):
        self.current_env.set(target.id, value)

    def _assign_attr(self, target, value):
        obj = self.eval(target.value)
        setattr(obj, target.attr, value)

    def _assign_subscript(self, target, value):
        obj = self.eval(target.value)
        key = self.eval(target.slice)
        obj[key] = value

    def _assign_sequence(self, target, value):
        self._assign_sequence_target(target, value)

    def _assign_starred(self, target, value):
        self.assign_target(target.value, list(value))
