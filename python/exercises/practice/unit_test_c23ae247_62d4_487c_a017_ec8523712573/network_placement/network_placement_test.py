import unittest
import math
import random
import time
from network_placement import optimize_network_placement

class TestNetworkPlacement(unittest.TestCase):
    def calculate_max_latency(self, nodes, gateways, assignments):
        """Calculate the maximum latency based on node assignments."""
        max_latency = 0
        for i, (x, y) in enumerate(nodes):
            gateway_idx = assignments[i]
            gx, gy = gateways[gateway_idx]
            distance = math.sqrt((x - gx) ** 2 + (y - gy) ** 2)
            max_latency = max(max_latency, distance)
        return max_latency

    def is_valid_solution(self, nodes, k, gateways, assignments):
        """Check if the solution is valid."""
        # Check if we have exactly k gateways
        self.assertEqual(len(gateways), k, "Number of gateways doesn't match k")
        
        # Check if all nodes are assigned to a valid gateway
        self.assertEqual(len(assignments), len(nodes), "Number of assignments doesn't match number of nodes")
        
        for assignment in assignments:
            self.assertTrue(0 <= assignment < k, f"Invalid gateway assignment: {assignment}")

        # Check if all gateway coordinates are within the valid range
        for gx, gy in gateways:
            self.assertTrue(0 <= gx <= 1000 and 0 <= gy <= 1000, 
                           f"Gateway coordinates out of range: ({gx}, {gy})")

    def test_simple_case(self):
        """Test with a simple case with an obvious solution."""
        nodes = [(0, 0), (0, 10), (10, 0), (10, 10)]
        k = 1
        
        gateways, assignments = optimize_network_placement(nodes, k)
        
        self.is_valid_solution(nodes, k, gateways, assignments)
        max_latency = self.calculate_max_latency(nodes, gateways, assignments)
        
        # Optimal solution should place the gateway at (5, 5)
        self.assertAlmostEqual(max_latency, 5*math.sqrt(2), delta=1e-6)

    def test_two_gateways(self):
        """Test with two distinct clusters of nodes."""
        nodes = [(0, 0), (1, 1), (2, 0), (100, 100), (101, 101), (102, 100)]
        k = 2
        
        gateways, assignments = optimize_network_placement(nodes, k)
        
        self.is_valid_solution(nodes, k, gateways, assignments)
        max_latency = self.calculate_max_latency(nodes, gateways, assignments)
        
        # Optimal solution should place gateways near (1, 0.5) and (101, 100.5)
        self.assertLessEqual(max_latency, 1.5)

    def test_single_node(self):
        """Test with a single node."""
        nodes = [(5, 5)]
        k = 1
        
        gateways, assignments = optimize_network_placement(nodes, k)
        
        self.is_valid_solution(nodes, k, gateways, assignments)
        max_latency = self.calculate_max_latency(nodes, gateways, assignments)
        
        # Optimal solution should place the gateway at the node
        self.assertAlmostEqual(max_latency, 0, delta=1e-6)

    def test_k_equals_n(self):
        """Test when k equals the number of nodes."""
        nodes = [(0, 0), (10, 10), (20, 20), (30, 30)]
        k = 4
        
        gateways, assignments = optimize_network_placement(nodes, k)
        
        self.is_valid_solution(nodes, k, gateways, assignments)
        max_latency = self.calculate_max_latency(nodes, gateways, assignments)
        
        # Optimal solution should place a gateway at each node
        self.assertAlmostEqual(max_latency, 0, delta=1e-6)

    def test_grid_pattern(self):
        """Test with nodes arranged in a grid pattern."""
        nodes = [(i*10, j*10) for i in range(3) for j in range(3)]
        k = 3
        
        gateways, assignments = optimize_network_placement(nodes, k)
        
        self.is_valid_solution(nodes, k, gateways, assignments)
        max_latency = self.calculate_max_latency(nodes, gateways, assignments)
        
        # Optimal solution should place gateways to minimize max distance
        self.assertLessEqual(max_latency, 10.0)

    def test_random_medium(self):
        """Test with a medium-sized random input."""
        random.seed(42)
        nodes = [(random.randint(0, 1000), random.randint(0, 1000)) for _ in range(50)]
        k = 5
        
        start_time = time.time()
        gateways, assignments = optimize_network_placement(nodes, k)
        end_time = time.time()
        
        self.is_valid_solution(nodes, k, gateways, assignments)
        self.assertLess(end_time - start_time, 10, "Solution took too long")

    def test_random_large(self):
        """Test with a large random input."""
        random.seed(42)
        nodes = [(random.randint(0, 1000), random.randint(0, 1000)) for _ in range(200)]
        k = 10
        
        start_time = time.time()
        gateways, assignments = optimize_network_placement(nodes, k)
        end_time = time.time()
        
        self.is_valid_solution(nodes, k, gateways, assignments)
        self.assertLess(end_time - start_time, 30, "Solution took too long")

    def test_performance_scaling(self):
        """Test how the solution scales with input size."""
        random.seed(42)
        
        sizes = [50, 100, 200]
        times = []
        
        for size in sizes:
            nodes = [(random.randint(0, 1000), random.randint(0, 1000)) for _ in range(size)]
            k = max(1, size // 20)
            
            start_time = time.time()
            gateways, assignments = optimize_network_placement(nodes, k)
            end_time = time.time()
            
            self.is_valid_solution(nodes, k, gateways, assignments)
            times.append(end_time - start_time)
        
        # Check that the algorithm scales reasonably
        if len(times) > 1 and times[0] > 0:
            # Check that the scaling is not much worse than quadratic
            ratio = times[-1] / times[0]
            size_ratio = (sizes[-1] / sizes[0]) ** 2  # Quadratic scaling
            self.assertLess(ratio, size_ratio * 2, 
                           f"Algorithm doesn't scale well: {times}, ratio: {ratio}, expected: {size_ratio}")

    def test_edge_case_all_same_point(self):
        """Test the edge case where all nodes are at the same point."""
        nodes = [(5, 5)] * 50
        k = 3
        
        gateways, assignments = optimize_network_placement(nodes, k)
        
        self.is_valid_solution(nodes, k, gateways, assignments)
        max_latency = self.calculate_max_latency(nodes, gateways, assignments)
        
        # Optimal solution should place at least one gateway at the shared point
        self.assertAlmostEqual(max_latency, 0, delta=1e-6)

    def test_edge_case_line(self):
        """Test the edge case where all nodes are on a straight line."""
        nodes = [(i, i) for i in range(10)]
        k = 2
        
        gateways, assignments = optimize_network_placement(nodes, k)
        
        self.is_valid_solution(nodes, k, gateways, assignments)
        max_latency = self.calculate_max_latency(nodes, gateways, assignments)
        
        # Optimal solution should place gateways at approximately (2.5, 2.5) and (7.5, 7.5)
        self.assertLessEqual(max_latency, 2.5 * math.sqrt(2) + 1e-6)

if __name__ == "__main__":
    unittest.main()