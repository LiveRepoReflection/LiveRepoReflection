import unittest
from interdimensional_cable import minimum_transmission_cost


class InterdimensionalCableTest(unittest.TestCase):
    def test_basic_example(self):
        realities = ["A", "B", "C", "D"]
        cables = [("A", "B", 1), ("B", "C", 2), ("A", "C", 5), ("C", "D", 1), ("A", "D", 10)]
        start = "A"
        end = "D"
        k = 2
        self.assertEqual(minimum_transmission_cost(realities, cables, start, end, k), 6)

    def test_no_path_within_k_hops(self):
        realities = ["A", "B", "C"]
        cables = [("A", "B", 1), ("B", "C", 2)]
        start = "A"
        end = "C"
        k = 1
        self.assertEqual(minimum_transmission_cost(realities, cables, start, end, k), -1)

    def test_direct_path_exists(self):
        realities = ["A", "B", "C", "D"]
        cables = [("A", "B", 10), ("A", "C", 15), ("A", "D", 20)]
        start = "A"
        end = "D"
        k = 1
        self.assertEqual(minimum_transmission_cost(realities, cables, start, end, k), 20)

    def test_multiple_paths_exist(self):
        realities = ["A", "B", "C", "D", "E"]
        cables = [
            ("A", "B", 1), ("B", "D", 1), 
            ("A", "C", 2), ("C", "D", 2),
            ("A", "E", 10), ("E", "D", 1)
        ]
        start = "A"
        end = "D"
        k = 2
        self.assertEqual(minimum_transmission_cost(realities, cables, start, end, k), 2)

    def test_cycle_in_graph(self):
        realities = ["A", "B", "C", "D"]
        cables = [
            ("A", "B", 1), ("B", "C", 2), 
            ("C", "A", 3), ("C", "D", 4)
        ]
        start = "A"
        end = "D"
        k = 3
        self.assertEqual(minimum_transmission_cost(realities, cables, start, end, k), 7)

    def test_zero_hops_same_node(self):
        realities = ["A", "B", "C"]
        cables = [("A", "B", 1), ("B", "C", 2)]
        start = "A"
        end = "A"
        k = 0
        self.assertEqual(minimum_transmission_cost(realities, cables, start, end, k), 0)

    def test_zero_hops_different_node(self):
        realities = ["A", "B", "C"]
        cables = [("A", "B", 1), ("B", "C", 2)]
        start = "A"
        end = "B"
        k = 0
        self.assertEqual(minimum_transmission_cost(realities, cables, start, end, k), -1)

    def test_parallel_edges(self):
        realities = ["A", "B", "C"]
        cables = [
            ("A", "B", 5), ("A", "B", 3), 
            ("B", "C", 2), ("B", "C", 1)
        ]
        start = "A"
        end = "C"
        k = 2
        self.assertEqual(minimum_transmission_cost(realities, cables, start, end, k), 4)

    def test_large_graph(self):
        # Create a more complex test case with multiple paths
        realities = [f"R{i}" for i in range(10)]
        cables = []
        
        # Connect each node to several others with different weights
        for i in range(9):
            cables.append((f"R{i}", f"R{i+1}", i+1))
            
        # Add some shortcuts
        cables.append(("R0", "R5", 10))
        cables.append(("R5", "R9", 10))
        cables.append(("R0", "R9", 25))
        
        start = "R0"
        end = "R9"
        
        # With K=1, only direct path is available
        self.assertEqual(minimum_transmission_cost(realities, cables, start, end, k=1), 25)
        
        # With K=2, path R0->R5->R9 is better
        self.assertEqual(minimum_transmission_cost(realities, cables, start, end, k=2), 20)
        
        # With K=9, the full path R0->R1->...->R9 is possible but not optimal
        self.assertEqual(minimum_transmission_cost(realities, cables, start, end, k=9), 20)

    def test_disconnected_graph(self):
        realities = ["A", "B", "C", "D", "E"]
        cables = [("A", "B", 1), ("D", "E", 2)]
        start = "A"
        end = "E"
        k = 5
        self.assertEqual(minimum_transmission_cost(realities, cables, start, end, k), -1)

    def test_negative_edge_case(self):
        realities = []
        cables = []
        with self.assertRaises(ValueError):
            minimum_transmission_cost(realities, cables, "", "", 0)
            
    def test_unreachable_destination(self):
        realities = ["A", "B", "C", "D"]
        cables = [("A", "B", 1), ("B", "C", 2), ("C", "B", 3)]
        start = "A"
        end = "D"
        k = 10
        self.assertEqual(minimum_transmission_cost(realities, cables, start, end, k), -1)

    def test_large_k_value(self):
        realities = ["A", "B", "C", "D"]
        cables = [("A", "B", 1), ("B", "C", 2), ("C", "D", 3)]
        start = "A"
        end = "D"
        k = 100
        self.assertEqual(minimum_transmission_cost(realities, cables, start, end, k), 6)


if __name__ == "__main__":
    unittest.main()