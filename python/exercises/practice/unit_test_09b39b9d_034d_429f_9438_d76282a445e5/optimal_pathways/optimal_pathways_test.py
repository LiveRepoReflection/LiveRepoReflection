import unittest
from optimal_pathways import find_k_shortest_paths


class OptimalPathwaysTest(unittest.TestCase):
    def test_basic_case(self):
        # Simple graph with one path
        n = 3
        edges = [(0, 1, 5), (1, 2, 5)]
        district_assignments = [0, 1, 2]
        risk_factors = [10, 20, 30]
        destination = 2
        k = 1
        max_risk = 100
        
        expected = [[0, 1, 2]]
        result = find_k_shortest_paths(n, len(edges), edges, district_assignments, risk_factors, destination, k, max_risk)
        self.assertEqual(result, expected)

    def test_multiple_paths(self):
        # Graph with multiple paths to destination
        n = 5
        edges = [
            (0, 1, 10), (0, 2, 5), 
            (1, 3, 1), (2, 3, 9), 
            (3, 4, 2)
        ]
        district_assignments = [0, 1, 2, 3, 4]
        risk_factors = [10, 20, 30, 15, 5]
        destination = 4
        k = 2
        max_risk = 100
        
        # Two possible paths: 0->1->3->4 (total time: 13) and 0->2->3->4 (total time: 16)
        expected = [[0, 1, 3, 4], [0, 2, 3, 4]]
        result = find_k_shortest_paths(n, len(edges), edges, district_assignments, risk_factors, destination, k, max_risk)
        self.assertEqual(result, expected)

    def test_risk_constraint(self):
        # Test where some paths exceed risk constraint
        n = 4
        edges = [(0, 1, 5), (0, 2, 4), (1, 3, 5), (2, 3, 6)]
        district_assignments = [0, 1, 2, 3]
        risk_factors = [10, 40, 20, 15]
        destination = 3
        k = 2
        max_risk = 45  # Path through district 1 exceeds this
        
        # Only path 0->2->3 is valid (total risk: 10 + 20 + 15 = 45)
        expected = [[0, 2, 3]]
        result = find_k_shortest_paths(n, len(edges), edges, district_assignments, risk_factors, destination, k, max_risk)
        self.assertEqual(result, expected)

    def test_no_valid_paths(self):
        # Test where no paths satisfy the risk constraint
        n = 3
        edges = [(0, 1, 5), (1, 2, 5)]
        district_assignments = [0, 1, 2]
        risk_factors = [30, 30, 30]
        destination = 2
        k = 1
        max_risk = 50  # Total risk would be 90
        
        expected = []
        result = find_k_shortest_paths(n, len(edges), edges, district_assignments, risk_factors, destination, k, max_risk)
        self.assertEqual(result, expected)

    def test_unreachable_destination(self):
        # Test with an unreachable destination
        n = 4
        edges = [(0, 1, 5), (1, 2, 5)]  # No path to node 3
        district_assignments = [0, 1, 2, 3]
        risk_factors = [10, 20, 30, 40]
        destination = 3
        k = 1
        max_risk = 100
        
        expected = []
        result = find_k_shortest_paths(n, len(edges), edges, district_assignments, risk_factors, destination, k, max_risk)
        self.assertEqual(result, expected)

    def test_same_start_and_destination(self):
        # Test when start and destination are the same
        n = 3
        edges = [(0, 1, 5), (1, 2, 5)]
        district_assignments = [0, 1, 2]
        risk_factors = [10, 20, 30]
        destination = 0
        k = 1
        max_risk = 100
        
        expected = [[0]]  # Just the start node itself
        result = find_k_shortest_paths(n, len(edges), edges, district_assignments, risk_factors, destination, k, max_risk)
        self.assertEqual(result, expected)

    def test_cycles_in_graph(self):
        # Test with cycles in the graph
        n = 4
        edges = [(0, 1, 5), (1, 2, 5), (2, 0, 5), (2, 3, 5)]
        district_assignments = [0, 1, 2, 3]
        risk_factors = [10, 20, 30, 40]
        destination = 3
        k = 3
        max_risk = 150
        
        # Paths: [0,1,2,3], potentially [0,1,2,0,1,2,3] etc.
        # We need the 3 shortest, not all possible paths with cycles
        result = find_k_shortest_paths(n, len(edges), edges, district_assignments, risk_factors, destination, k, max_risk)
        self.assertEqual(len(result), 1)  # Should only find the direct path
        self.assertEqual(result[0], [0, 1, 2, 3])

    def test_multiple_edges_between_nodes(self):
        # Test with multiple edges between the same nodes
        n = 3
        edges = [(0, 1, 5), (0, 1, 3), (1, 2, 5)]  # Two edges from 0 to 1
        district_assignments = [0, 1, 2]
        risk_factors = [10, 20, 30]
        destination = 2
        k = 2
        max_risk = 100
        
        # Should use the edge with weight 3 for the shortest path
        expected = [[0, 1, 2]]
        result = find_k_shortest_paths(n, len(edges), edges, district_assignments, risk_factors, destination, k, max_risk)
        self.assertEqual(result, expected)

    def test_larger_graph(self):
        # Test with a more complex graph
        n = 8
        edges = [
            (0, 1, 3), (0, 2, 5), (1, 3, 2), (1, 4, 6),
            (2, 5, 4), (3, 6, 1), (4, 6, 3), (5, 7, 5),
            (6, 7, 2)
        ]
        district_assignments = [0, 1, 2, 3, 1, 2, 3, 4]  # Some nodes share districts
        risk_factors = [10, 20, 15, 25, 30]
        destination = 7
        k = 3
        max_risk = 100
        
        # Calculate shortest paths and check expected properties
        result = find_k_shortest_paths(n, len(edges), edges, district_assignments, risk_factors, destination, k, max_risk)
        
        # Should return up to 3 paths
        self.assertLessEqual(len(result), 3)
        
        # All paths should start with 0 and end with 7
        for path in result:
            self.assertEqual(path[0], 0)
            self.assertEqual(path[-1], 7)
        
        # Check paths are ordered by travel time
        path_times = []
        for path in result:
            time = 0
            for i in range(len(path) - 1):
                for u, v, w in edges:
                    if u == path[i] and v == path[i + 1]:
                        time += w
                        break
            path_times.append(time)
        
        for i in range(len(path_times) - 1):
            self.assertLessEqual(path_times[i], path_times[i + 1])

    def test_exactly_k_paths(self):
        # Test where exactly k paths exist that satisfy constraints
        n = 5
        edges = [
            (0, 1, 3), (0, 2, 4), 
            (1, 3, 2), (2, 3, 1), 
            (3, 4, 2)
        ]
        district_assignments = [0, 1, 2, 3, 4]
        risk_factors = [10, 15, 20, 5, 10]
        destination = 4
        k = 2
        max_risk = 100
        
        # There are two paths: 0->1->3->4 and 0->2->3->4
        result = find_k_shortest_paths(n, len(edges), edges, district_assignments, risk_factors, destination, k, max_risk)
        self.assertEqual(len(result), 2)

    def test_disconnected_graph(self):
        # Test with a disconnected graph
        n = 7
        edges = [
            (0, 1, 5), (1, 2, 5),  # Connected component 1
            (3, 4, 5), (4, 5, 5), (5, 6, 5)  # Connected component 2
        ]
        district_assignments = [0, 1, 2, 3, 4, 5, 6]
        risk_factors = [10, 20, 30, 10, 20, 30, 40]
        destination = 6
        k = 1
        max_risk = 100
        
        # No path from 0 to 6
        expected = []
        result = find_k_shortest_paths(n, len(edges), edges, district_assignments, risk_factors, destination, k, max_risk)
        self.assertEqual(result, expected)

if __name__ == '__main__':
    unittest.main()