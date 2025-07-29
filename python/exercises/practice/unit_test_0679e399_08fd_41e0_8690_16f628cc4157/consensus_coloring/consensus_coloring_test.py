import unittest
import time
from consensus_coloring import ConsensusColoring

class TestConsensusColoring(unittest.TestCase):
    def setUp(self):
        # Initialize the consensus coloring system.
        self.cc = ConsensusColoring()

    def wait_for_convergence(self):
        # Helper function to simulate waiting for the system to converge.
        # If the implementation provides an explicit converge method, call it.
        if hasattr(self.cc, "converge"):
            self.cc.converge()
        else:
            time.sleep(0.1)

    def test_single_edge_coloring(self):
        # Test that two connected nodes get different colors.
        self.cc.add_node(1)
        self.cc.add_node(2)
        self.cc.add_edge(1, 2)
        self.wait_for_convergence()
        color1 = self.cc.get_color(1)
        color2 = self.cc.get_color(2)
        self.assertIsNotNone(color1)
        self.assertIsNotNone(color2)
        self.assertNotEqual(color1, color2)

    def test_triangle_coloring(self):
        # Create a triangle graph and test that all adjacent nodes have different colors.
        for node in [1, 2, 3]:
            self.cc.add_node(node)
        self.cc.add_edge(1, 2)
        self.cc.add_edge(2, 3)
        self.cc.add_edge(1, 3)
        self.wait_for_convergence()
        c1 = self.cc.get_color(1)
        c2 = self.cc.get_color(2)
        c3 = self.cc.get_color(3)
        self.assertIsNotNone(c1)
        self.assertIsNotNone(c2)
        self.assertIsNotNone(c3)
        self.assertNotEqual(c1, c2)
        self.assertNotEqual(c2, c3)
        self.assertNotEqual(c1, c3)

    def test_dynamic_edge_addition_removal(self):
        # Create nodes and edges, then remove an edge and test coloring stability.
        for node in [1, 2, 3]:
            self.cc.add_node(node)
        self.cc.add_edge(1, 2)
        self.cc.add_edge(2, 3)
        self.cc.add_edge(1, 3)
        self.wait_for_convergence()
        # Check initial coloring on the triangle.
        self.assertNotEqual(self.cc.get_color(1), self.cc.get_color(2))
        self.assertNotEqual(self.cc.get_color(2), self.cc.get_color(3))
        self.assertNotEqual(self.cc.get_color(1), self.cc.get_color(3))
        # Remove one edge and ensure adjacent nodes (still connected) remain with different colors.
        self.cc.remove_edge(1, 3)
        self.wait_for_convergence()
        self.assertNotEqual(self.cc.get_color(1), self.cc.get_color(2))
        self.assertNotEqual(self.cc.get_color(2), self.cc.get_color(3))
        # Since node 1 and node 3 are no longer directly connected, equality is now acceptable.

    def test_node_removal(self):
        # Test that removing a node updates the system correctly.
        for node in [1, 2, 3, 4]:
            self.cc.add_node(node)
        self.cc.add_edge(1, 2)
        self.cc.add_edge(2, 3)
        self.cc.add_edge(3, 4)
        self.wait_for_convergence()
        self.cc.remove_node(2)
        self.wait_for_convergence()
        # Attempting to get color for a removed node should raise an exception.
        with self.assertRaises(Exception):
            self.cc.get_color(2)
        # Check that adjacent relationships outside the removed node maintain valid coloring.
        color1 = self.cc.get_color(1)
        color3 = self.cc.get_color(3)
        self.assertIsNotNone(color1)
        self.assertIsNotNone(color3)
        # If there was an edge between node 1 and node 3 (added in the convergence to repair inconsistencies),
        # they must have different colors.
        neighbors_of_1 = self.cc.get_neighbors(1) if hasattr(self.cc, "get_neighbors") else []
        if 3 in neighbors_of_1:
            self.assertNotEqual(color1, color3)

    def test_large_scale_simulation(self):
        # Simulate a larger graph scenario with a chain structure and additional random edges.
        num_nodes = 100
        for node in range(1, num_nodes + 1):
            self.cc.add_node(node)
        # Create a chain graph.
        for node in range(1, num_nodes):
            self.cc.add_edge(node, node + 1)
        # Add extra edges to create additional constraints.
        extra_edges = [(1, 50), (20, 70), (33, 66), (10, 90)]
        for u, v in extra_edges:
            self.cc.add_edge(u, v)
        self.wait_for_convergence()
        # Verify that all connected nodes have different colors.
        for node in range(1, num_nodes + 1):
            if hasattr(self.cc, "get_neighbors"):
                for neighbor in self.cc.get_neighbors(node):
                    self.assertNotEqual(self.cc.get_color(node), self.cc.get_color(neighbor))

if __name__ == "__main__":
    unittest.main()