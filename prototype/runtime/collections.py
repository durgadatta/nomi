"""Bounded ordinary-call collection experiments; no static callback guarantees."""


def fold(items, seed, combine):
    """Ordered left reduction with an explicit seed and fail-fast callbacks."""
    if not callable(combine):
        raise TypeError("fold combine must be callable")
    state = seed
    for item in items:
        state = combine(state, item)
    return state


def scan(items, seed, combine):
    """Seeded left history. Mutable states are retained by reference, not copied."""
    if not callable(combine):
        raise TypeError("scan combine must be callable")
    states = [seed]
    state = seed
    for item in items:
        state = combine(state, item)
        states.append(state)
    return states
