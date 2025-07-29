import unittest
from shard_order import schedule_transactions

class TestShardOrder(unittest.TestCase):
    def check_order(self, transactions, N, result):
        # Create a map for quick lookup of transaction details by id.
        trans_map = {t["id"]: t for t in transactions}
        # For every shard from 0 to N-1, check the order.
        for shard in range(N):
            self.assertIn(shard, result, f"Shard {shard} missing in result")
            schedule = result[shard]
            # For each transaction in this shard's schedule,
            # ensure that all dependencies (which participate in this shard)
            # appear before the transaction.
            for i, tid in enumerate(schedule):
                self.assertIn(tid, trans_map, f"Unknown transaction id {tid} found in shard {shard}")
                deps = trans_map[tid]["dependencies"]
                for dep in deps:
                    if shard in trans_map[dep]["shards"]:
                        self.assertIn(dep, schedule, f"Dependency {dep} missing in shard {shard} for transaction {tid}")
                        self.assertLess(schedule.index(dep), i,
                                        f"In shard {shard}, dependency {dep} of transaction {tid} does not appear before it.")

    def test_empty_transactions(self):
        N = 3
        transactions = []
        result = schedule_transactions(transactions, N)
        expected = {i: [] for i in range(N)}
        self.assertEqual(result, expected)

    def test_single_transaction(self):
        N = 3
        transactions = [
            {"id": 1, "shards": [0, 2], "dependencies": []}
        ]
        result = schedule_transactions(transactions, N)
        expected = {0: [1], 1: [], 2: [1]}
        self.assertEqual(result, expected)

    def test_chain_dependencies(self):
        N = 3
        transactions = [
            {"id": 1, "shards": [0, 1], "dependencies": []},
            {"id": 2, "shards": [1, 2], "dependencies": [1]},
            {"id": 3, "shards": [0, 2], "dependencies": [2]}
        ]
        result = schedule_transactions(transactions, N)
        self.check_order(transactions, N, result)

    def test_independent_transactions(self):
        N = 4
        transactions = [
            {"id": 1, "shards": [0, 1], "dependencies": []},
            {"id": 2, "shards": [2, 3], "dependencies": []},
            {"id": 3, "shards": [0, 2], "dependencies": []},
            {"id": 4, "shards": [1, 3], "dependencies": []}
        ]
        result = schedule_transactions(transactions, N)
        self.check_order(transactions, N, result)
        # Verify that transactions appear only in their respective shards.
        for t in transactions:
            for shard in range(N):
                schedule = result[shard]
                if shard in t["shards"]:
                    self.assertIn(t["id"], schedule,
                                  f"Transaction {t['id']} should appear in shard {shard}")
                else:
                    self.assertNotIn(t["id"], schedule,
                                     f"Transaction {t['id']} should not appear in shard {shard}")

    def test_circular_dependency(self):
        N = 2
        transactions = [
            {"id": 1, "shards": [0, 1], "dependencies": [2]},
            {"id": 2, "shards": [0, 1], "dependencies": [1]}
        ]
        result = schedule_transactions(transactions, N)
        self.assertIsNone(result)

    def test_complex_dependencies(self):
        N = 4
        transactions = [
            {"id": 1, "shards": [0, 1], "dependencies": []},
            {"id": 2, "shards": [1, 2], "dependencies": [1]},
            {"id": 3, "shards": [2, 3], "dependencies": [1]},
            {"id": 4, "shards": [0, 3], "dependencies": [2, 3]},
            {"id": 5, "shards": [1, 2, 3], "dependencies": [2]},
            {"id": 6, "shards": [0], "dependencies": [4]},
            {"id": 7, "shards": [2], "dependencies": [5]}
        ]
        result = schedule_transactions(transactions, N)
        self.check_order(transactions, N, result)

if __name__ == '__main__':
    unittest.main()