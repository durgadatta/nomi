"""Defer statement: ``defer file.close()`` — sets ``_nomi_defer`` on the stmt."""


class DeferMixin:
    def defer_stmt(self, items):
        stmt = items[0]
        stmt._nomi_defer = True
        return stmt
