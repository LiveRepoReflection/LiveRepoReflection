import unittest
from dist_tx_coord.dist_tx_coord import coordinate_transaction

class TestDistributedTransactionCoordinator(unittest.TestCase):
    def setUp(self):
        # Helper functions for node behavior
        def can_commit_always(tid, ops):
            return True
            
        def can_commit_never(tid, ops):
            return False
            
        def can_commit_fail_node1(tid, ops):
            return ops[0][0] != 1  # Only node 1 fails
            
        # Node data tracking for verification
        self.node_data = {
            0: {},
            1: {},
            2: {}
        }
        
        def commit_func(tid, ops):
            for op in ops:
                node_id, op_type, key, value = op
                if op_type == "write":
                    self.node_data[node_id][key] = value
                    
        def rollback_func(tid, ops):
            pass  # For simplicity, we don't implement rollback tracking
            
        # Create test nodes
        self.nodes = [
            {
                "node_id": 0,
                "data": {},
                "can_commit": can_commit_always,
                "commit": commit_func,
                "rollback": rollback_func
            },
            {
                "node_id": 1,
                "data": {},
                "can_commit": can_commit_always,
                "commit": commit_func,
                "rollback": rollback_func
            },
            {
                "node_id": 2,
                "data": {},
                "can_commit": can_commit_always,
                "commit": commit_func,
                "rollback": rollback_func
            }
        ]
        
    def test_successful_transaction(self):
        transaction = {
            "transaction_id": 1,
            "operations": [
                (0, "write", "x", 10),
                (1, "write", "y", 20),
                (0, "read", "x", None)
            ],
            "expected_reads": {(0, "x"): 10}
        }
        
        result = coordinate_transaction(self.nodes, transaction)
        self.assertTrue(result)
        self.assertEqual(self.node_data[0]["x"], 10)
        self.assertEqual(self.node_data[1]["y"], 20)
        
    def test_failed_transaction_single_node(self):
        # Configure node 1 to always fail
        self.nodes[1]["can_commit"] = lambda tid, ops: False
        
        transaction = {
            "transaction_id": 2,
            "operations": [
                (0, "write", "x", 30),
                (1, "write", "y", 40),
                (2, "write", "z", 50)
            ],
            "expected_reads": {}
        }
        
        result = coordinate_transaction(self.nodes, transaction)
        self.assertFalse(result)
        self.assertEqual(self.node_data[0].get("x", None), None)
        self.assertEqual(self.node_data[1].get("y", None), None)
        self.assertEqual(self.node_data[2].get("z", None), None)
        
    def test_read_consistency(self):
        transaction = {
            "transaction_id": 3,
            "operations": [
                (0, "write", "a", 100),
                (0, "read", "a", None),
                (1, "write", "b", 200),
                (1, "read", "b", None)
            ],
            "expected_reads": {
                (0, "a"): 100,
                (1, "b"): 200
            }
        }
        
        result = coordinate_transaction(self.nodes, transaction)
        self.assertTrue(result)
        self.assertEqual(self.node_data[0]["a"], 100)
        self.assertEqual(self.node_data[1]["b"], 200)
        
    def test_partial_failure(self):
        # Configure node 1 to fail sometimes
        self.nodes[1]["can_commit"] = lambda tid, ops: tid % 2 == 0
        
        # This transaction should fail (odd tid)
        transaction1 = {
            "transaction_id": 5,
            "operations": [
                (0, "write", "c", 300),
                (1, "write", "d", 400)
            ],
            "expected_reads": {}
        }
        
        result1 = coordinate_transaction(self.nodes, transaction1)
        self.assertFalse(result1)
        
        # This transaction should succeed (even tid)
        transaction2 = {
            "transaction_id": 6,
            "operations": [
                (0, "write", "e", 500),
                (1, "write", "f", 600)
            ],
            "expected_reads": {}
        }
        
        result2 = coordinate_transaction(self.nodes, transaction2)
        self.assertTrue(result2)
        self.assertEqual(self.node_data[0]["e"], 500)
        self.assertEqual(self.node_data[1]["f"], 600)
        
    def test_empty_transaction(self):
        transaction = {
            "transaction_id": 7,
            "operations": [],
            "expected_reads": {}
        }
        
        result = coordinate_transaction(self.nodes, transaction)
        self.assertTrue(result)
        
    def test_read_verification_failure(self):
        transaction = {
            "transaction_id": 8,
            "operations": [
                (0, "write", "g", 700),
                (0, "read", "g", None)
            ],
            "expected_reads": {
                (0, "g"): 999  # Incorrect expected value
            }
        }
        
        with self.assertRaises(ValueError):
            coordinate_transaction(self.nodes, transaction)

if __name__ == '__main__':
    unittest.main()