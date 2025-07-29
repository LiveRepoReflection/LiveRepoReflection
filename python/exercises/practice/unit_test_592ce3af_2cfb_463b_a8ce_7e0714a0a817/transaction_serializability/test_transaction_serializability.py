import unittest
from transaction_serializability import can_serialize_transactions

class TestTransactionSerializability(unittest.TestCase):
    def test_simple_chain(self):
        num_nodes = 2
        transactions = [
            (0, ["A"], ["B"]),
            (1, ["B"], ["C"]),
            (0, ["C"], ["D"])
        ]
        self.assertTrue(can_serialize_transactions(num_nodes, transactions))

    def test_circular_dependency(self):
        num_nodes = 2
        transactions = [
            (0, ["A"], ["B"]),
            (1, ["B"], ["A"])
        ]
        self.assertFalse(can_serialize_transactions(num_nodes, transactions))

    def test_independent_transactions(self):
        num_nodes = 2
        transactions = [
            (0, ["A"], ["B"]),
            (1, ["C"], ["D"]),
            (0, ["E"], ["F"])
        ]
        self.assertTrue(can_serialize_transactions(num_nodes, transactions))

    def test_complex_dependency(self):
        num_nodes = 3
        transactions = [
            (0, ["A", "B"], ["C"]),
            (1, ["C"], ["D", "E"]),
            (2, ["D"], ["B"])
        ]
        self.assertFalse(can_serialize_transactions(num_nodes, transactions))

    def test_empty_transactions(self):
        num_nodes = 1
        transactions = []
        self.assertTrue(can_serialize_transactions(num_nodes, transactions))

    def test_single_transaction(self):
        num_nodes = 1
        transactions = [(0, ["A"], ["B"])]
        self.assertTrue(can_serialize_transactions(num_nodes, transactions))

    def test_same_read_write(self):
        num_nodes = 2
        transactions = [
            (0, ["A"], ["A"]),
            (1, ["A"], ["B"])
        ]
        self.assertFalse(can_serialize_transactions(num_nodes, transactions))

    def test_large_transaction_set(self):
        num_nodes = 5
        transactions = [
            (0, ["A"], ["B"]),
            (1, ["B"], ["C"]),
            (2, ["C"], ["D"]),
            (3, ["D"], ["E"]),
            (4, ["E"], ["F"]),
            (0, ["F"], ["G"]),
            (1, ["G"], ["H"]),
            (2, ["H"], ["I"]),
            (3, ["I"], ["J"]),
            (4, ["J"], ["K"])
        ]
        self.assertTrue(can_serialize_transactions(num_nodes, transactions))

    def test_complex_cycle(self):
        num_nodes = 4
        transactions = [
            (0, ["A"], ["B"]),
            (1, ["B"], ["C"]),
            (2, ["C"], ["D"]),
            (3, ["D"], ["E"]),
            (0, ["E"], ["A"])
        ]
        self.assertFalse(can_serialize_transactions(num_nodes, transactions))

    def test_multiple_reads(self):
        num_nodes = 3
        transactions = [
            (0, ["A", "B", "C"], ["D"]),
            (1, ["D"], ["E"]),
            (2, ["E"], ["F"])
        ]
        self.assertTrue(can_serialize_transactions(num_nodes, transactions))

    def test_multiple_writes(self):
        num_nodes = 2
        transactions = [
            (0, ["A"], ["B", "C", "D"]),
            (1, ["B", "C"], ["E"])
        ]
        self.assertTrue(can_serialize_transactions(num_nodes, transactions))

    def test_boundary_cases(self):
        num_nodes = 1
        transactions = [(0, [], ["A"])]
        self.assertTrue(can_serialize_transactions(num_nodes, transactions))
        
        transactions = [(0, ["A"], [])]
        self.assertTrue(can_serialize_transactions(num_nodes, transactions))

    def test_max_constraints(self):
        # Test with maximum constraints
        num_nodes = 100
        transactions = [(i % 100, [f"R{i}"], [f"W{i}"]) for i in range(500)]
        self.assertTrue(can_serialize_transactions(num_nodes, transactions))

if __name__ == '__main__':
    unittest.main()