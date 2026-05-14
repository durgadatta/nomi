"""Where-clause lowering: attach body as ``_nomi_where_body`` on the stmt.

The actual rewriting is done by the ``WhereClause`` desugar pass.
"""


class WhereClauseMixin:
    def assign_where(self, items):
        stmt, where_body = items
        if hasattr(stmt, '_nomi_where_body'):
            stmt._nomi_where_body.extend(where_body)
        else:
            stmt._nomi_where_body = where_body
        return stmt

    def assign_where_inline(self, items):
        stmt, where_stmt = items
        stmt._nomi_where_body = [where_stmt]
        return stmt
