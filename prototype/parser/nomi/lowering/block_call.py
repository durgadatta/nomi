"""Block-call lowering: ``f(x) do: ... end`` → ``BlockCall`` surface node.

The ``BlockCall`` surface node preserves the call structure in a Nomi-owned
node before ``lower_surface_to_python`` converts it to Python AST encoding.
"""

from prototype.syntax.surface import BlockCall, captures_span


class BlockCallMixin:
    @captures_span
    def block_call_stmt(self, items):
        call, params, block = items
        return BlockCall(
            func=call.func,
            args=call.args,
            keywords=list(call.keywords),
            block_params=params,
            block_body=block,
        )
