import unittest
import uuid
import json
from datetime import datetime, timedelta
from tx_aggregator import aggregate_transactions

class TestTransactionAggregator(unittest.TestCase):
    def setUp(self):
        # Generate test data
        self.worker_ids = ["worker1", "worker2", "worker3"]
        self.now = int(datetime.now().timestamp() * 1000)
        self.hour_ago = self.now - 3600000
        self.day_ago = self.now - 86400000
        
        # Create sample transactions
        self.common_tx_id = str(uuid.uuid4())
        self.tx1 = {
            "transaction_id": self.common_tx_id,
            "timestamp": self.hour_ago + 1000,
            "payload": {"amount": 100}
        }
        self.tx2 = {
            "transaction_id": str(uuid.uuid4()),
            "timestamp": self.hour_ago + 2000,
            "payload": {"amount": 200}
        }
        self.tx3 = {
            "transaction_id": self.common_tx_id,
            "timestamp": self.hour_ago + 500,  # Earlier duplicate
            "payload": {"amount": 50}
        }
        self.old_tx = {
            "transaction_id": str(uuid.uuid4()),
            "timestamp": self.day_ago,
            "payload": {"amount": 300}
        }

        # Mock worker logs
        self.worker_logs = {
            "worker1": [self.tx1, self.tx2],
            "worker2": [self.tx3, self.old_tx],
            "worker3": [self.tx1]  # Another duplicate
        }

    def mock_fetch_log(self, worker_id):
        return self.worker_logs.get(worker_id, [])

    def test_basic_aggregation(self):
        result = aggregate_transactions(
            self.worker_ids,
            self.hour_ago,
            self.now,
            self.mock_fetch_log
        )
        
        # Should contain 2 unique transactions within time window
        self.assertEqual(len(result), 2)
        
        # Earliest version of duplicate should be kept
        self.assertEqual(result[0]["transaction_id"], self.common_tx_id)
        self.assertEqual(result[0]["timestamp"], self.hour_ago + 500)
        
        # Order should be by timestamp
        self.assertLess(result[0]["timestamp"], result[1]["timestamp"])

    def test_time_window_filtering(self):
        result = aggregate_transactions(
            self.worker_ids,
            self.hour_ago,
            self.hour_ago + 1500,
            self.mock_fetch_log
        )
        
        # Should only include tx3 (earlier version of common_tx)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["transaction_id"], self.common_tx_id)

    def test_empty_time_window(self):
        result = aggregate_transactions(
            self.worker_ids,
            self.now + 1000,
            self.now + 2000,
            self.mock_fetch_log
        )
        self.assertEqual(len(result), 0)

    def test_all_workers_empty(self):
        result = aggregate_transactions(
            ["worker4", "worker5"],  # non-existent workers
            self.hour_ago,
            self.now,
            self.mock_fetch_log
        )
        self.assertEqual(len(result), 0)

    def test_large_number_of_workers(self):
        # Test with 1000 workers (each with empty logs)
        many_workers = [f"worker_{i}" for i in range(1000)]
        result = aggregate_transactions(
            many_workers,
            self.hour_ago,
            self.now,
            lambda _: []  # all empty logs
        )
        self.assertEqual(len(result), 0)

    def test_duplicates_across_many_workers(self):
        # Create scenario with same transaction reported by many workers
        tx_id = str(uuid.uuid4())
        base_time = self.hour_ago
        worker_ids = [f"dup_worker_{i}" for i in range(100)]
        
        # Each worker reports the same transaction with slightly different timestamps
        def mock_fetch(worker_id):
            worker_num = int(worker_id.split("_")[-1])
            return [{
                "transaction_id": tx_id,
                "timestamp": base_time + worker_num,
                "payload": {"worker": worker_num}
            }]
        
        result = aggregate_transactions(
            worker_ids,
            base_time,
            base_time + 1000,
            mock_fetch
        )
        
        # Should only keep the earliest version (worker_0)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["timestamp"], base_time)

if __name__ == '__main__':
    unittest.main()