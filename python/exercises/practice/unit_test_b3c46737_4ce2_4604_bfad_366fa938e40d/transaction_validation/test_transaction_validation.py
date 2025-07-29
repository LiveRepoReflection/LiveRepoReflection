import unittest
from transaction_validation.transaction_validation import can_commit_transaction

class TestTransactionValidation(unittest.TestCase):
    def test_single_service_ready(self):
        self.assertTrue(can_commit_transaction(1, [], ["READY"]))
    
    def test_single_service_aborted(self):
        self.assertFalse(can_commit_transaction(1, [], ["ABORTED"]))
    
    def test_linear_dependencies_all_ready(self):
        self.assertTrue(can_commit_transaction(
            3, [(0,1), (1,2)], ["READY", "READY", "READY"]))
    
    def test_linear_dependencies_with_abort(self):
        self.assertFalse(can_commit_transaction(
            3, [(0,1), (1,2)], ["READY", "ABORTED", "READY"]))
    
    def test_cycle_all_ready(self):
        self.assertTrue(can_commit_transaction(
            3, [(0,1), (1,2), (2,0)], ["READY", "READY", "READY"]))
    
    def test_cycle_with_abort(self):
        self.assertFalse(can_commit_transaction(
            3, [(0,1), (1,2), (2,0)], ["READY", "READY", "ABORTED"]))
    
    def test_disconnected_components(self):
        self.assertTrue(can_commit_transaction(
            4, [(0,1), (2,3)], ["READY", "READY", "READY", "READY"]))
    
    def test_disconnected_with_abort(self):
        self.assertFalse(can_commit_transaction(
            4, [(0,1), (2,3)], ["READY", "ABORTED", "READY", "READY"]))
    
    def test_complex_dependencies(self):
        self.assertFalse(can_commit_transaction(
            5, [(0,1), (1,2), (2,3), (3,4), (4,0)], ["READY", "READY", "ABORTED", "READY", "READY"]))
    
    def test_large_graph(self):
        n = 1000
        dependencies = [(i, i+1) for i in range(n-1)]
        initial_states = ["READY"] * n
        initial_states[-1] = "ABORTED"
        self.assertFalse(can_commit_transaction(n, dependencies, initial_states))

if __name__ == '__main__':
    unittest.main()