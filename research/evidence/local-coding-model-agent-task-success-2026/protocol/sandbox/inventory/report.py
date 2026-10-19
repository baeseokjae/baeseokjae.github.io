from .store import Store


def format_total(store):
    """Render the store total as a two-decimal string, e.g. 'total: 3.50'."""
    # Deliberately wrong in the frozen sandbox: the task is to fix this line.
    return "total: %d" % store.total()


def summarize(store, names):
    parts = ["%s=%s" % (name, store.get(name)) for name in names]
    return ", ".join(parts)
