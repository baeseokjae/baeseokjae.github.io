class Store:
    """A tiny in-memory price store used as a frozen agent-task sandbox."""

    def __init__(self):
        self._items = {}

    def add(self, name, price):
        if price < 0:
            raise ValueError("price must be non-negative")
        self._items[name] = price

    def get(self, name):
        return self._items.get(name)

    def remove(self, name):
        return self._items.pop(name, None)

    def total(self):
        return sum(self._items.values())
