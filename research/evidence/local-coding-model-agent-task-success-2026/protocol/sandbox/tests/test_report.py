import unittest

from inventory import Store, format_total


class ReportTests(unittest.TestCase):
    def test_total_is_rendered_with_two_decimals(self):
        store = Store()
        store.add("bolt", 1.5)
        store.add("nut", 2.0)
        # Fails on the frozen sandbox: report.format_total renders '%d'.
        self.assertEqual(format_total(store), "total: 3.50")


if __name__ == "__main__":
    unittest.main()
