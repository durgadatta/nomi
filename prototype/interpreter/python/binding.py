import ast

class BindingMixin:
    def del_target(self, node: ast.expr) -> None:
        if isinstance(node, ast.Name):
            self.current_env.delete(node.id)
        elif isinstance(node, ast.Attribute):
            try:
                delattr(self.eval(node.value), node.attr)
            except AttributeError as e:
                raise AttributeError(f"Cannot delete attribute '{node.attr}' at line {self.get_lineno(node)}: {str(e)}") from e
        elif isinstance(node, ast.Subscript):
            try:
                del self.eval(node.value)[self.eval(node.slice)]
            except (IndexError, KeyError) as e:
                raise IndexError(f"Subscript deletion error at line {self.get_lineno(node)}: {str(e)}") from e
        else:
            raise NotImplementedError(f"Delete target {node.__class__.__name__} not supported at line {self.get_lineno(node)}")

    def eval_Assign(self, node: ast.Assign) -> None:
        """
        Evaluate assignment statements, supporting tuple/list unpacking and starred targets.
        """
        value = self.eval(node.value)

        for target in node.targets:
            self._assign_target(target, value)


    def assign_target(self, target, value):
        """Helper: recursively assign value to target."""
        if isinstance(target, ast.Name):
            # Simple variable assignment
            self.current_env.set(target.id, value)

        elif isinstance(target, ast.Attribute):
            # Object attribute: obj.attr = value
            obj = self.eval(target.value)
            setattr(obj, target.attr, value)

        elif isinstance(target, ast.Subscript):
            # Subscript assignment: obj[key] = value
            obj = self.eval(target.value)
            key = self.eval(target.slice)
            obj[key] = value

        elif isinstance(target, (ast.Tuple, ast.List)):
            # Sequence unpacking assignment
            if not isinstance(value, (list, tuple)):
                raise TypeError(
                    f"Cannot unpack non-iterable {type(value).__name__} "
                    f"object at line {self.get_lineno(target)}"
                )

            elts = target.elts
            has_star = any(isinstance(e, ast.Starred) for e in elts)

            if not has_star:
                if len(value) != len(elts):
                    raise ValueError(
                        f"Unpack mismatch: expected {len(elts)} values, got {len(value)}"
                    )
                for subtarget, subval in zip(elts, value):
                    self._assign_target(subtarget, subval)
            else:
                # Handle one starred target (Python allows only one)
                star_index = next(i for i, e in enumerate(elts) if isinstance(e, ast.Starred))
                before = elts[:star_index]
                starred = elts[star_index]
                after = elts[star_index + 1 :]

                if len(value) < len(before) + len(after):
                    raise ValueError(
                        f"Unpack mismatch: not enough values to unpack "
                        f"(expected at least {len(before) + len(after)}, got {len(value)})"
                    )

                # Split the sequence according to star position
                before_vals = value[: len(before)]
                star_vals = value[len(before) : len(value) - len(after)]
                after_vals = value[-len(after) :] if after else []

                # Assign parts
                for subtarget, subval in zip(before, before_vals):
                    self._assign_target(subtarget, subval)
                self._assign_target(starred.value, list(star_vals))
                for subtarget, subval in zip(after, after_vals):
                    self._assign_target(subtarget, subval)

        elif isinstance(target, ast.Starred):
            # Starred on LHS (only occurs within tuple/list)
            self._assign_target(target.value, list(value))

        else:
            raise TypeError(
                f"Unsupported assignment target {target.__class__.__name__} "
                f"at line {self.get_lineno(target)}"
            )

    def eval_AugAssign(self, node: ast.AugAssign) -> None:
        old_value = self.eval_target(node.target)
        op_value = self.eval(node.value)
        new_value = self.apply_operator(old_value, node.op, op_value)
        self.assign_target(node.target, new_value)

    def eval_AnnAssign(self, node: ast.AnnAssign) -> None:
        if node.value:
            value = self.eval(node.value)
            self.assign_target(node.target, value)

    def _assign_target(self, target, value):
        """Recursive assignment helper. Supports: Name, Attribute, Subscript,
        Tuple/List unpacking (from any iterable), and Starred targets."""
        # Simple name
        if isinstance(target, ast.Name):
            self.current_env.set(target.id, value)
            return

        # Attribute: obj.attr = value
        if isinstance(target, ast.Attribute):
            obj = self.eval(target.value)
            setattr(obj, target.attr, value)
            return

        # Subscript: obj[key] = value
        if isinstance(target, ast.Subscript):
            obj = self.eval(target.value)
            # target.slice may be an ast.Index or node depending on Python version;
            # reuse your existing eval logic for slice nodes
            key = self.eval(target.slice)
            obj[key] = value
            return

        # Tuple/List unpacking (accept any iterable, including generators)
        if isinstance(target, (ast.Tuple, ast.List)):
            elts = target.elts
            # validate single starred target rule
            star_indices = [i for i, e in enumerate(elts) if isinstance(e, ast.Starred)]
            if len(star_indices) > 1:
                raise SyntaxError(f"multiple starred expressions in assignment at line {self.get_lineno(target)}")

            try:
                iterator = iter(value)
            except TypeError as e:
                raise TypeError(f"Cannot unpack non-iterable {type(value).__name__} at line {self.get_lineno(target)}") from e

            if not star_indices:
                # Non-starred: must get exactly len(elts) items
                needed = len(elts)
                got = []
                try:
                    for _ in range(needed):
                        got.append(next(iterator))
                except StopIteration:
                    raise ValueError(f"Not enough values to unpack (expected {needed}) at line {self.get_lineno(target)}")

                # Ensure there are no trailing items
                try:
                    next(iterator)
                    raise ValueError(f"Too many values to unpack (expected {needed}) at line {self.get_lineno(target)}")
                except StopIteration:
                    pass

                for subtarget, subval in zip(elts, got):
                    self._assign_target(subtarget, subval)

            else:
                # Starred present (Python allows exactly one)
                star_i = star_indices[0]
                before = elts[:star_i]
                star = elts[star_i]            # ast.Starred
                after = elts[star_i + 1 :]

                # Collect 'before' items
                before_vals = []
                try:
                    for _ in before:
                        before_vals.append(next(iterator))
                except StopIteration:
                    min_needed = len(before) + len(after)
                    raise ValueError(
                        f"Not enough values to unpack (expected at least {min_needed}) at line {self.get_lineno(target)}"
                    )

                # Collect the remainder to slice off 'after' from the tail
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

                # Assign
                for subtarget, subval in zip(before, before_vals):
                    self._assign_target(subtarget, subval)
                # starred target gets a list of remaining values
                self._assign_target(star.value, list(star_vals))
                for subtarget, subval in zip(after, after_vals):
                    self._assign_target(subtarget, subval)
            return

        # Starred alone (should only appear inside Tuple/List target)
        if isinstance(target, ast.Starred):
            # Treat like assigning the whole iterable as list
            self._assign_target(target.value, list(value))
            return

        # Unsupported target
        raise TypeError(f"Unsupported assignment target {target.__class__.__name__} at line {self.get_lineno(target)}")   