import unittest
from distributed_bank import simulate_transactions

class DistributedBankTest(unittest.TestCase):
    def test_all_transactions_commit_no_failures(self):
        # Setup configuration without failure events
        num_nodes = 3
        initial_balances = {
            0: {"A": 100},
            1: {"B": 200},
            2: {"C": 300}
        }
        transactions = [
            {"from_account": "A", "to_account": "B", "amount": 50},
            {"from_account": "B", "to_account": "C", "amount": 100}
        ]
        node_distribution = {
            "A": 0,
            "B": 1,
            "C": 2
        }
        failure_events = []  # No failures
        
        # Execute the simulation
        success, final_state = simulate_transactions(num_nodes, transactions, node_distribution, initial_balances, failure_events)
        
        # Expected balances after transactions:
        # "A": 100 - 50 = 50 on node 0
        # "B": 200 + 50 - 100 = 150 on node 1
        # "C": 300 + 100 = 400 on node 2
        expected_state = {
            0: {"A": 50},
            1: {"B": 150},
            2: {"C": 400}
        }
        
        self.assertTrue(success)
        self.assertEqual(final_state, expected_state)

    def test_transaction_rollback_due_to_failure(self):
        # Setup configuration with a failure in one of the nodes
        num_nodes = 3
        initial_balances = {
            0: {"A": 100},
            1: {"B": 200},
            2: {"C": 300}
        }
        transactions = [
            {"from_account": "A", "to_account": "B", "amount": 50}
        ]
        node_distribution = {
            "A": 0,
            "B": 1,
            "C": 2
        }
        # Simulate a failure of node 1 during processing
        failure_events = [
            (1, "fail", 1)
        ]
        
        success, final_state = simulate_transactions(num_nodes, transactions, node_distribution, initial_balances, failure_events)
        
        # Since node 1 fails, the transaction should not commit (rolled back)
        # Final state should be identical to initial state
        self.assertFalse(success)
        self.assertEqual(final_state, initial_balances)
    
    def test_concurrent_transactions(self):
        # Setup configuration with multiple concurrent transactions
        num_nodes = 3
        initial_balances = {
            0: {"A": 100},
            1: {"B": 200, "D": 50},
            2: {"C": 300}
        }
        transactions = [
            {"from_account": "A", "to_account": "B", "amount": 50},
            {"from_account": "B", "to_account": "C", "amount": 100},
            {"from_account": "A", "to_account": "D", "amount": 30}
        ]
        node_distribution = {
            "A": 0,
            "B": 1,
            "C": 2,
            "D": 1
        }
        failure_events = []  # No failures
        
        success, final_state = simulate_transactions(num_nodes, transactions, node_distribution, initial_balances, failure_events)
        
        # Expected calculation:
        # Transaction 1: A -> B: A: 100 - 50 = 50, B: 200 + 50 = 250
        # Transaction 2: B -> C: B: 250 - 100 = 150, C: 300 + 100 = 400
        # Transaction 3: A -> D: A: 50 - 30 = 20, D: 50 + 30 = 80
        expected_state = {
            0: {"A": 20},
            1: {"B": 150, "D": 80},
            2: {"C": 400}
        }
        
        self.assertTrue(success)
        self.assertEqual(final_state, expected_state)

if __name__ == '__main__':
    unittest.main()