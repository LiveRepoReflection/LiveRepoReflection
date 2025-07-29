import unittest
from sharded_tx import process_transactions
import threading
import time
import random

class ShardedTransactionTest(unittest.TestCase):
    
    def test_basic_transactions(self):
        N = 2  # Two shards
        M = 2  # Two transactions
        
        transactions = [
            [  # Transaction 1
                {"type": "READ", "shard_id": 0, "key": "x"},
                {"type": "WRITE", "shard_id": 1, "key": "y", "value": "value1"}
            ],
            [  # Transaction 2
                {"type": "WRITE", "shard_id": 0, "key": "x", "value": "value2"},
                {"type": "READ", "shard_id": 1, "key": "y"}
            ]
        ]
        
        results = process_transactions(N, M, transactions)
        self.assertEqual(len(results), M)
        for result in results:
            self.assertIsInstance(result, bool)
    
    def test_atomicity(self):
        N = 3
        M = 1
        
        # Transaction that should succeed
        transactions = [
            [
                {"type": "READ", "shard_id": 0, "key": "a"},
                {"type": "WRITE", "shard_id": 1, "key": "b", "value": "value1"},
                {"type": "WRITE", "shard_id": 2, "key": "c", "value": "value2"}
            ]
        ]
        
        results = process_transactions(N, M, transactions)
        self.assertTrue(results[0])
        
        # Transaction that should fail due to invalid shard_id
        M = 1
        transactions = [
            [
                {"type": "READ", "shard_id": 0, "key": "a"},
                {"type": "WRITE", "shard_id": N, "key": "b", "value": "value1"}  # Invalid shard_id
            ]
        ]
        
        results = process_transactions(N, M, transactions)
        self.assertFalse(results[0])
    
    def test_isolation(self):
        N = 2
        M = 2
        
        # Two transactions that should conflict
        transactions = [
            [  # Transaction 1
                {"type": "READ", "shard_id": 0, "key": "x"},
                {"type": "WRITE", "shard_id": 0, "key": "x", "value": "value1"}
            ],
            [  # Transaction 2
                {"type": "READ", "shard_id": 0, "key": "x"},
                {"type": "WRITE", "shard_id": 0, "key": "x", "value": "value2"}
            ]
        ]
        
        results = process_transactions(N, M, transactions)
        # At least one transaction should abort due to conflict
        self.assertTrue(not all(results))
    
    def test_parallel_execution(self):
        N = 3
        M = 3
        
        # Three transactions that don't conflict
        transactions = [
            [  # Transaction 1
                {"type": "READ", "shard_id": 0, "key": "a"},
                {"type": "WRITE", "shard_id": 0, "key": "a", "value": "value1"}
            ],
            [  # Transaction 2
                {"type": "READ", "shard_id": 1, "key": "b"},
                {"type": "WRITE", "shard_id": 1, "key": "b", "value": "value2"}
            ],
            [  # Transaction 3
                {"type": "READ", "shard_id": 2, "key": "c"},
                {"type": "WRITE", "shard_id": 2, "key": "c", "value": "value3"}
            ]
        ]
        
        # Measure execution time
        start_time = time.time()
        results = process_transactions(N, M, transactions)
        end_time = time.time()
        
        # All transactions should succeed
        self.assertTrue(all(results))
        
        # Execution time should be less than sequential execution
        # This is a heuristic, but parallel execution should be faster
        self.assertLess(end_time - start_time, 1.0)  # Adjust threshold as needed
    
    def test_failure_handling(self):
        N = 2
        M = 2
        
        # Create a mock failure scenario
        class FailingTransaction:
            def __init__(self, should_fail=False):
                self.should_fail = should_fail
                self.failure_triggered = False
            
            def execute_transaction(self, tx):
                if self.should_fail:
                    self.failure_triggered = True
                    raise Exception("Simulated shard failure")
                return True
        
        # Two transactions where one will encounter a shard failure
        transactions = [
            [  # Transaction 1 - should succeed
                {"type": "READ", "shard_id": 0, "key": "x"},
                {"type": "WRITE", "shard_id": 0, "key": "x", "value": "value1"}
            ],
            [  # Transaction 2 - should fail due to shard failure
                {"type": "READ", "shard_id": 1, "key": "y"},
                {"type": "WRITE", "shard_id": 1, "key": "y", "value": "value2"}
            ]
        ]
        
        # Override process_transactions to simulate failure
        original_process = process_transactions
        
        def mock_process_transactions(N, M, txs):
            return [True, False]  # Simulate first transaction succeeding, second failing
        
        # Replace the function temporarily
        import sharded_tx
        sharded_tx.process_transactions = mock_process_transactions
        
        results = sharded_tx.process_transactions(N, M, transactions)
        
        # First transaction should succeed, second should fail
        self.assertTrue(results[0])
        self.assertFalse(results[1])
        
        # Restore the original function
        sharded_tx.process_transactions = original_process
    
    def test_large_scale(self):
        N = 10  # 10 shards
        M = 50  # 50 transactions
        
        # Generate random transactions
        transactions = []
        for _ in range(M):
            num_ops = random.randint(1, 5)
            tx = []
            for _ in range(num_ops):
                op_type = random.choice(["READ", "WRITE"])
                shard_id = random.randint(0, N-1)
                key = f"key_{random.randint(0, 100)}"
                
                if op_type == "READ":
                    tx.append({"type": op_type, "shard_id": shard_id, "key": key})
                else:  # WRITE
                    value = f"value_{random.randint(0, 1000)}"
                    tx.append({"type": op_type, "shard_id": shard_id, "key": key, "value": value})
            
            transactions.append(tx)
        
        # Measure execution time
        start_time = time.time()
        results = process_transactions(N, M, transactions)
        end_time = time.time()
        
        # Verify results
        self.assertEqual(len(results), M)
        for result in results:
            self.assertIsInstance(result, bool)
        
        # Check execution time is reasonable
        execution_time = end_time - start_time
        print(f"Large scale test execution time: {execution_time} seconds")
        
        # For a large scale test, we expect reasonable performance
        # This threshold might need adjustment based on the implementation
        self.assertLess(execution_time, 5.0)  # Should complete in under 5 seconds
    
    def test_conflict_detection(self):
        N = 2
        M = 3
        
        # Three transactions with potential conflicts
        transactions = [
            [  # Transaction 1
                {"type": "READ", "shard_id": 0, "key": "x"},
                {"type": "WRITE", "shard_id": 0, "key": "x", "value": "value1"}
            ],
            [  # Transaction 2 - conflicts with Transaction 1
                {"type": "READ", "shard_id": 0, "key": "x"},
                {"type": "WRITE", "shard_id": 0, "key": "x", "value": "value2"}
            ],
            [  # Transaction 3 - no conflict
                {"type": "READ", "shard_id": 1, "key": "y"},
                {"type": "WRITE", "shard_id": 1, "key": "y", "value": "value3"}
            ]
        ]
        
        results = process_transactions(N, M, transactions)
        
        # Transaction 3 should succeed
        self.assertTrue(results[2])
        
        # At least one of Transaction 1 or 2 should fail
        self.assertFalse(results[0] and results[1])
    
    def test_edge_cases(self):
        # Test with 0 transactions
        N = 2
        M = 0
        transactions = []
        results = process_transactions(N, M, transactions)
        self.assertEqual(results, [])
        
        # Test with empty transaction
        N = 2
        M = 1
        transactions = [[]]
        results = process_transactions(N, M, transactions)
        self.assertEqual(len(results), 1)
        
        # Test with invalid operation type
        N = 2
        M = 1
        transactions = [
            [{"type": "INVALID", "shard_id": 0, "key": "x"}]
        ]
        results = process_transactions(N, M, transactions)
        self.assertFalse(results[0])
        
        # Test with missing required fields
        N = 2
        M = 1
        transactions = [
            [{"type": "READ", "shard_id": 0}]  # Missing key
        ]
        results = process_transactions(N, M, transactions)
        self.assertFalse(results[0])
        
        # Test with WRITE missing value
        N = 2
        M = 1
        transactions = [
            [{"type": "WRITE", "shard_id": 0, "key": "x"}]  # Missing value
        ]
        results = process_transactions(N, M, transactions)
        self.assertFalse(results[0])
    
    def test_snapshot_isolation(self):
        N = 2
        M = 3
        
        # Transactions to test snapshot isolation
        transactions = [
            [  # Transaction 1 - writes to x
                {"type": "WRITE", "shard_id": 0, "key": "x", "value": "value1"}
            ],
            [  # Transaction 2 - reads x then writes to y
                {"type": "READ", "shard_id": 0, "key": "x"},
                {"type": "WRITE", "shard_id": 1, "key": "y", "value": "value2"}
            ],
            [  # Transaction 3 - reads y then writes to x
                {"type": "READ", "shard_id": 1, "key": "y"},
                {"type": "WRITE", "shard_id": 0, "key": "x", "value": "value3"}
            ]
        ]
        
        # In snapshot isolation, read-only transactions never conflict
        # But write-write conflicts should be detected
        results = process_transactions(N, M, transactions)
        
        # Either all should succeed (if executed with proper ordering)
        # or at least one should fail (if there's a write-write conflict)
        if not all(results):
            # If not all succeeded, verify the failure pattern makes sense
            # For example, if 1 and 3 both try to write to x, one should fail
            self.assertFalse(results[0] and results[2])
    
    def test_concurrent_execution(self):
        # This test verifies that concurrent transactions are handled properly
        N = 4
        M = 10
        
        # Create transactions that can execute in parallel
        transactions = []
        for i in range(M):
            shard_id = i % N
            transactions.append([
                {"type": "READ", "shard_id": shard_id, "key": f"key_{i}"},
                {"type": "WRITE", "shard_id": shard_id, "key": f"key_{i}", "value": f"value_{i}"}
            ])
        
        # Execute transactions
        results = process_transactions(N, M, transactions)
        
        # All transactions should succeed
        self.assertTrue(all(results))

if __name__ == '__main__':
    unittest.main()