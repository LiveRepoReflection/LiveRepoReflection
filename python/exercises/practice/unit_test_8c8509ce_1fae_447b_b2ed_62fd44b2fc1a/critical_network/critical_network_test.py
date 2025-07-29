import unittest
from critical_network.critical_network import maximize_resilience

class CriticalNetworkTest(unittest.TestCase):
    def test_two_nodes_no_redundant(self):
        # Graph: 1 <-> 2, importance: [5, 10], k = 0
        # Failure outcomes:
        # - Remove 1: remaining {2} with sum = 10.
        # - Remove 2: remaining {1} with sum = 5.
        # Resilience = min(10, 5) = 5.
        n = 2
        k = 0
        importance = [5, 10]
        adj_list = [
            [2],  # Facility 1 connected to 2
            [1]   # Facility 2 connected to 1
        ]
        result = maximize_resilience(n, k, importance, adj_list)
        self.assertEqual(result, 5)

    def test_chain_three_no_redundant(self):
        # Graph: 1 - 2 - 3, importance: [5, 10, 20], k = 0
        # Failure outcomes:
        # - Remove 1: remaining {2, 3} connected with sum = 10 + 20 = 30.
        # - Remove 2: remaining split into {1} and {3}. Largest component = max(5, 20) = 20.
        # - Remove 3: remaining {1, 2} connected with sum = 5 + 10 = 15.
        # Resilience = min(30, 20, 15) = 15.
        n = 3
        k = 0
        importance = [5, 10, 20]
        adj_list = [
            [2],      # Facility 1 connected to 2
            [1, 3],   # Facility 2 connected to 1 and 3
            [2]       # Facility 3 connected to 2
        ]
        result = maximize_resilience(n, k, importance, adj_list)
        self.assertEqual(result, 15)

    def test_star_with_redundant(self):
        # Star graph: Facility 1 (center) connected to 2, 3, 4.
        # Importance: [100, 1, 1, 1], k = 1.
        # Without reinforcement, failure of center isolates leaves.
        # Reinforcement (e.g., adding a link between two leaves) can improve
        # connectivity when center fails.
        # Expected resilience computed for an optimal addition is 2.
        n = 4
        k = 1
        importance = [100, 1, 1, 1]
        adj_list = [
            [2, 3, 4],  # Facility 1 connected to all leaves
            [1],        # Facilities 2,3,4 connected only to center
            [1],
            [1]
        ]
        result = maximize_resilience(n, k, importance, adj_list)
        self.assertEqual(result, 2)

    def test_complete_graph(self):
        # Complete graph with n = 4, importance: [10, 20, 30, 40], k = 0.
        # For any failure, remaining graph is fully connected.
        # Failure outcomes:
        # - If facility 1 fails: sum = 20 + 30 + 40 = 90.
        # - If facility 2 fails: sum = 10 + 30 + 40 = 80.
        # - If facility 3 fails: sum = 10 + 20 + 40 = 70.
        # - If facility 4 fails: sum = 10 + 20 + 30 = 60.
        # Resilience = 60.
        n = 4
        k = 0
        importance = [10, 20, 30, 40]
        adj_list = [
            [2, 3, 4],
            [1, 3, 4],
            [1, 2, 4],
            [1, 2, 3]
        ]
        result = maximize_resilience(n, k, importance, adj_list)
        self.assertEqual(result, 60)

    def test_disconnected_components_with_redundant(self):
        # Graph has 2 disconnected components initially.
        # Component 1: Facilities 1 and 2 connected, importance: [10, 10].
        # Component 2: Facilities 3, 4, 5 as a chain, importance: [30, 5, 5].
        # k = 2 redundant links can be used to bridge the components.
        # An optimal strategy can connect the two components such that
        # for any single facility removal the largest connected component has sum = 30.
        n = 5
        k = 2
        importance = [10, 10, 30, 5, 5]
        adj_list = [
            [2],    # Facility 1 connected to 2
            [1],    # Facility 2 connected to 1
            [4],    # Facility 3 connected only to 4
            [3, 5], # Facility 4 connected to 3 and 5
            [4]     # Facility 5 connected to 4
        ]
        result = maximize_resilience(n, k, importance, adj_list)
        self.assertEqual(result, 30)

if __name__ == '__main__':
    unittest.main()