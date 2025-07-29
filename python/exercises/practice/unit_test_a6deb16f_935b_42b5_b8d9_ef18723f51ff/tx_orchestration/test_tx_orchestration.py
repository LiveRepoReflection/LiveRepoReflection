import unittest
from tx_orchestration import orchestrate_transaction

class TestTransactionOrchestration(unittest.TestCase):
    def test_simple_success(self):
        graph = {"A": [], "B": ["A"]}
        operations = {"A": lambda: True, "B": lambda: True}
        compensations = {"A": lambda: None, "B": lambda: None}
        self.assertTrue(orchestrate_transaction(graph, operations, compensations))

    def test_simple_failure(self):
        graph = {"A": [], "B": ["A"]}
        operations = {"A": lambda: True, "B": lambda: False}
        compensations = {"A": lambda: None, "B": lambda: None}
        self.assertFalse(orchestrate_transaction(graph, operations, compensations))

    def test_complex_dag_success(self):
        graph = {"A": [], "B": ["A"], "C": ["A"], "D": ["B", "C"]}
        operations = {"A": lambda: True, "B": lambda: True, "C": lambda: True, "D": lambda: True}
        compensations = {"A": lambda: None, "B": lambda: None, "C": lambda: None, "D": lambda: None}
        self.assertTrue(orchestrate_transaction(graph, operations, compensations))

    def test_complex_dag_failure(self):
        graph = {"A": [], "B": ["A"], "C": ["A"], "D": ["B", "C"]}
        operations = {"A": lambda: True, "B": lambda: True, "C": lambda: False, "D": lambda: True}
        compensations = {"A": lambda: None, "B": lambda: None, "C": lambda: None, "D": lambda: None}
        self.assertFalse(orchestrate_transaction(graph, operations, compensations))

    def test_empty_graph(self):
        graph = {}
        operations = {}
        compensations = {}
        self.assertTrue(orchestrate_transaction(graph, operations, compensations))

    def test_single_node_success(self):
        graph = {"A": []}
        operations = {"A": lambda: True}
        compensations = {"A": lambda: None}
        self.assertTrue(orchestrate_transaction(graph, operations, compensations))

    def test_single_node_failure(self):
        graph = {"A": []}
        operations = {"A": lambda: False}
        compensations = {"A": lambda: None}
        self.assertFalse(orchestrate_transaction(graph, operations, compensations))

    def test_diamond_dag_success(self):
        graph = {"A": [], "B": ["A"], "C": ["A"], "D": ["B", "C"]}
        operations = {"A": lambda: True, "B": lambda: True, "C": lambda: True, "D": lambda: True}
        compensations = {"A": lambda: None, "B": lambda: None, "C": lambda: None, "D": lambda: None}
        self.assertTrue(orchestrate_transaction(graph, operations, compensations))

    def test_diamond_dag_failure(self):
        graph = {"A": [], "B": ["A"], "C": ["A"], "D": ["B", "C"]}
        operations = {"A": lambda: True, "B": lambda: True, "C": lambda: True, "D": lambda: False}
        compensations = {"A": lambda: None, "B": lambda: None, "C": lambda: None, "D": lambda: None}
        self.assertFalse(orchestrate_transaction(graph, operations, compensations))

    def test_parallel_branches_success(self):
        graph = {"A": [], "B": [], "C": ["A", "B"]}
        operations = {"A": lambda: True, "B": lambda: True, "C": lambda: True}
        compensations = {"A": lambda: None, "B": lambda: None, "C": lambda: None}
        self.assertTrue(orchestrate_transaction(graph, operations, compensations))

    def test_parallel_branches_failure(self):
        graph = {"A": [], "B": [], "C": ["A", "B"]}
        operations = {"A": lambda: True, "B": lambda: False, "C": lambda: True}
        compensations = {"A": lambda: None, "B": lambda: None, "C": lambda: None}
        self.assertFalse(orchestrate_transaction(graph, operations, compensations))

if __name__ == '__main__':
    unittest.main()