import unittest
from network_planner.network_planner import optimal_network_plan

class TestNetworkPlanner(unittest.TestCase):
    def test_small_network(self):
        N = 3
        M = 3
        links = [
            (0, 1, 10, 5),
            (0, 2, 15, 8),
            (1, 2, 20, 10)
        ]
        L = 15
        B = 30
        expected = [(0, 1, 10, 5), (0, 2, 15, 8)]
        result = optimal_network_plan(N, M, links, L, B)
        self.assertEqual(sorted(result), sorted(expected))

    def test_no_solution(self):
        N = 4
        M = 4
        links = [
            (0, 1, 100, 5),
            (1, 2, 100, 5),
            (2, 3, 100, 5),
            (0, 3, 1, 100)
        ]
        L = 10
        B = 200
        result = optimal_network_plan(N, M, links, L, B)
        self.assertEqual(result, [])

    def test_multiple_valid_solutions(self):
        N = 4
        M = 5
        links = [
            (0, 1, 10, 5),
            (0, 2, 15, 8),
            (1, 2, 12, 6),
            (1, 3, 8, 4),
            (2, 3, 10, 7)
        ]
        L = 20
        B = 40
        result = optimal_network_plan(N, M, links, L, B)
        self.assertTrue(len(result) >= 3)  # At least 3 links needed for connectivity
        self.assertTrue(sum(cost for _, _, cost, _ in result) <= B)

    def test_latency_constraint(self):
        N = 5
        M = 7
        links = [
            (0, 1, 5, 2),
            (0, 2, 8, 3),
            (1, 2, 6, 4),
            (1, 3, 10, 8),
            (2, 3, 7, 5),
            (2, 4, 12, 9),
            (3, 4, 9, 7)
        ]
        L = 15
        B = 40
        result = optimal_network_plan(N, M, links, L, B)
        self.assertTrue(self._verify_latency_constraint(N, result, L))

    def test_empty_input(self):
        N = 0
        M = 0
        links = []
        L = 0
        B = 0
        result = optimal_network_plan(N, M, links, L, B)
        self.assertEqual(result, [])

    def _verify_latency_constraint(self, N, network, max_latency):
        if not network:
            return False
            
        # Build adjacency list
        adj = {i: [] for i in range(N)}
        for u, v, _, lat in network:
            adj[u].append((v, lat))
            adj[v].append((u, lat))
            
        # Check all pairs shortest path
        for i in range(N):
            distances = {node: float('inf') for node in range(N)}
            distances[i] = 0
            visited = set()
            
            while len(visited) < N:
                current = min(
                    (node for node in range(N) if node not in visited),
                    key=lambda x: distances[x]
                )
                visited.add(current)
                
                for neighbor, lat in adj[current]:
                    if neighbor not in visited:
                        new_dist = distances[current] + lat
                        if new_dist < distances[neighbor]:
                            distances[neighbor] = new_dist
                            
            for j in range(N):
                if i != j and distances[j] > max_latency:
                    return False
        return True

if __name__ == '__main__':
    unittest.main()