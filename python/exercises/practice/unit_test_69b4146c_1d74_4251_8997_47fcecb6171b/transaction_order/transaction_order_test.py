import unittest

from transaction_order import order_transactions

class TransactionOrderTest(unittest.TestCase):
    def validate_order(self, dependencies, order):
        """
        Helper function to validate that the transaction order satisfies
        each dependency: for each (A, B) in dependencies, transaction B must
        come before transaction A.
        """
        position = {tid: i for i, tid in enumerate(order)}
        for a, b in dependencies:
            if a in position and b in position and position[b] >= position[a]:
                return False
        return True

    def test_simple_dependency(self):
        N = 3
        transactions = [
            (1, {0, 1}, ["read A", "write B"]),
            (2, {1, 2}, ["read B", "write C"]),
            (3, {0, 2}, ["read C", "write A"])
        ]
        dependencies = [(2, 1), (3, 2)]
        result = order_transactions(N, transactions, dependencies)
        self.assertTrue(result, "Expected a valid order for non-cyclic dependencies")
        self.assertEqual(len(result), len(transactions),
                         "The order should include all transactions")
        self.assertTrue(self.validate_order(dependencies, result),
                        "The returned order does not satisfy the dependencies")

    def test_cycle_detection(self):
        N = 2
        transactions = [
            (1, {0}, ["read X", "write Y"]),
            (2, {0}, ["read Y", "write Z"])
        ]
        dependencies = [(1, 2), (2, 1)]
        result = order_transactions(N, transactions, dependencies)
        self.assertEqual(result, [],
                         "Expected an empty order due to cyclic dependency")

    def test_conflict_resolution(self):
        N = 3
        transactions = [
            (1, {0, 1}, ["read A", "write B"]),
            (2, {1, 2}, ["read A", "write B"]),  # Conflicts with transaction 1 due to shared node and same operations
            (3, {0, 2}, ["read C", "write D"])
        ]
        dependencies = []
        result = order_transactions(N, transactions, dependencies)
        # The order must include every transaction id
        self.assertEqual(set(result), {1, 2, 3},
                         "The order must include all transactions")
        # Check for consistency: repeated ordering on the same input should yield the same result,
        # ensuring a consistent tie-breaking mechanism.
        result2 = order_transactions(N, transactions, dependencies)
        self.assertEqual(result, result2,
                         "The ordering should be consistent across multiple runs for the same input")

    def test_complex_dependencies(self):
        N = 4
        transactions = [
            (1, {0, 1}, ["read A", "write B"]),
            (2, {1, 2}, ["read B", "write C"]),
            (3, {2, 3}, ["read C", "write D"]),
            (4, {0, 3}, ["read D", "write A"]),
            (5, {1, 3}, ["read A", "write E"])
        ]
        dependencies = [(2, 1), (3, 2), (4, 3), (5, 1), (5, 4)]
        result = order_transactions(N, transactions, dependencies)
        self.assertTrue(result, "Expected a valid order for complex dependencies")
        self.assertEqual(set(result), {1, 2, 3, 4, 5},
                         "The order must include all transactions")
        self.assertTrue(self.validate_order(dependencies, result),
                        "The returned order does not satisfy the given dependency constraints")

    def test_no_dependencies(self):
        N = 2
        transactions = [
            (1, {0}, ["read X"]),
            (2, {1}, ["write Y"]),
            (3, {0, 1}, ["read Z", "write W"])
        ]
        dependencies = []
        result = order_transactions(N, transactions, dependencies)
        self.assertEqual(set(result), {1, 2, 3},
                         "The order must include all transactions when there are no dependencies")
        self.assertEqual(len(result), 3,
                         "The order length must be equal to the number of transactions")

if __name__ == '__main__':
    unittest.main()