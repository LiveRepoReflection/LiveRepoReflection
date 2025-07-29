import unittest
from hypergraph_path import shortest_hypergraph_path

class TestHypergraphPath(unittest.TestCase):
    def test_simple_path(self):
        hypergraph = {
            "A": [{"A", "B"}, {"A", "C"}],
            "B": [{"A", "B"}, {"B", "D"}],
            "C": [{"A", "C"}],
            "D": [{"B", "D"}, {"D", "E"}],
            "E": [{"D", "E"}]
        }
        self.assertEqual(shortest_hypergraph_path(hypergraph, "A", "E"), 3)

    def test_disconnected_graph(self):
        hypergraph = {
            "A": [{"A", "B"}],
            "B": [{"A", "B"}],
            "C": [{"C", "D"}],
            "D": [{"C", "D"}]
        }
        self.assertEqual(shortest_hypergraph_path(hypergraph, "A", "D"), -1)

    def test_self_loop(self):
        hypergraph = {
            "A": [{"A"}, {"A", "B"}],
            "B": [{"A", "B"}, {"B"}]
        }
        self.assertEqual(shortest_hypergraph_path(hypergraph, "A", "B"), 1)

    def test_multiple_paths(self):
        hypergraph = {
            "A": [{"A", "B"}, {"A", "C"}],
            "B": [{"A", "B"}, {"B", "D"}],
            "C": [{"A", "C"}, {"C", "D"}],
            "D": [{"B", "D"}, {"C", "D"}]
        }
        self.assertEqual(shortest_hypergraph_path(hypergraph, "A", "D"), 2)

    def test_empty_hyperedge(self):
        hypergraph = {
            "A": [set(), {"A", "B"}],
            "B": [{"A", "B"}, set()],
            "C": [set()]
        }
        self.assertEqual(shortest_hypergraph_path(hypergraph, "A", "C"), -1)

    def test_large_hypergraph(self):
        hypergraph = {str(i): [set(str(i) for i in range(i, i+3))] for i in range(100)}
        hypergraph["0"].append({"0", "99"})
        hypergraph["99"].append({"0", "99"})
        self.assertEqual(shortest_hypergraph_path(hypergraph, "0", "99"), 1)

    def test_immediate_target(self):
        hypergraph = {
            "A": [{"A", "B"}],
            "B": [{"A", "B"}, {"B"}]
        }
        self.assertEqual(shortest_hypergraph_path(hypergraph, "B", "B"), 0)

    def test_complex_cycle(self):
        hypergraph = {
            "A": [{"A", "B"}, {"A", "C"}],
            "B": [{"A", "B"}, {"B", "C"}, {"B", "D"}],
            "C": [{"A", "C"}, {"B", "C"}, {"C", "D"}],
            "D": [{"B", "D"}, {"C", "D"}, {"D", "E"}],
            "E": [{"D", "E"}]
        }
        self.assertEqual(shortest_hypergraph_path(hypergraph, "A", "E"), 3)

if __name__ == '__main__':
    unittest.main()