"""Scoped frame model for portable Core Runtime backends."""

from __future__ import annotations

from dataclasses import dataclass, field

from prototype.runtime.backends.values import Value, unbox_value


@dataclass(slots=True)
class Frame:
    """One lexical scope frame with an optional parent frame."""

    parent: Frame | None = None
    bindings: dict[str, Value] = field(default_factory=dict)
    captures: set[str] = field(default_factory=set)

    def lookup(self, name: str) -> Value | None:
        if name in self.bindings:
            return self.bindings[name]
        if self.parent is not None:
            return self.parent.lookup(name)
        return None

    def bind(self, name: str, value: Value) -> None:
        self.bindings[name] = value

    def assign(self, name: str, value: Value) -> None:
        frame = self._nearest_frame_with(name)
        if frame is None:
            self.bindings[name] = value
        else:
            frame.bindings[name] = value

    def extend(
        self,
        params: tuple[str, ...] = (),
        args: tuple[Value, ...] = (),
        *,
        captures: set[str] | None = None,
    ) -> Frame:
        if len(args) != len(params):
            raise TypeError(
                f"Expected {len(params)} arguments, received {len(args)}"
            )
        child = Frame(parent=self, captures=set(captures or ()))
        for param, arg in zip(params, args):
            child.bind(param, arg)
        return child

    def export_bindings(self) -> dict[str, object]:
        return {
            name: unbox_value(value)
            for name, value in self.bindings.items()
        }

    def _nearest_frame_with(self, name: str) -> Frame | None:
        if name in self.bindings:
            return self
        if self.parent is not None:
            return self.parent._nearest_frame_with(name)
        return None
