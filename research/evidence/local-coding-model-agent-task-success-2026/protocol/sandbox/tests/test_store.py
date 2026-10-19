import unittest

from inventory import Store


class StoreTests(unittest.TestCase):
    def test_add_and_get(self):
        store = Store()
        store.add("bolt", 1.5)
        self.assertEqual(store.get("bolt"), 1.5)

    def test_negative_price_rejected(self):
        store = Store()
        with self.assertRaises(ValueError):
            store.add("broken", -1.0)

    def test_remove(self):
        store = Store()
        store.add("bolt", 1.5)
        self.assertEqual(store.remove("bolt"), 1.5)
        self.assertIsNone(store.get("bolt"))

    def test_total(self):
        store = Store()
        store.add("bolt", 1.5)
        store.add("nut", 2.0)
        self.assertEqual(store.total(), 3.5)


if __name__ == "__main__":
    unittest.main()
