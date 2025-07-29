import unittest
from network_game import simulate_nash_equilibrium

class NetworkGameTest(unittest.TestCase):
    def valid_path(self, graph, path, start, end):
        current = start
        for eid in path:
            found = False
            if current in graph:
                for (nbr, edge_id) in graph[current]:
                    if edge_id == eid:
                        current = nbr
                        found = True
                        break
            if not found:
                return False
        return current == end

    def test_single_agent(self):
        # Trivial case with one edge.
        graph = {
            0: [(1, 10)],
            1: []
        }
        congestion_functions = {
            10: (1, 0)
        }
        start_nodes = [0]
        end_nodes = [1]

        result = simulate_nash_equilibrium(graph, congestion_functions, start_nodes, end_nodes)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], [10])
        self.assertTrue(self.valid_path(graph, result[0], start_nodes[0], end_nodes[0]))

    def test_multiple_agents(self):
        graph = {
            0: [(1, 0), (2, 1)],
            1: [(3, 2)],
            2: [(3, 3)],
            3: []
        }
        congestion_functions = {
            0: (1, 0),   # cost = 1*x + 0
            1: (2, 1),   # cost = 2*x + 1
            2: (1, 2),   # cost = 1*x + 2
            3: (3, 0)    # cost = 3*x + 0
        }
        start_nodes = [0, 0]
        end_nodes = [3, 3]

        result = simulate_nash_equilibrium(graph, congestion_functions, start_nodes, end_nodes)
        self.assertEqual(len(result), 2)
        for i in range(2):
            self.assertTrue(self.valid_path(graph, result[i], start_nodes[i], end_nodes[i]))
        # Check that each returned path is non-empty.
        for path in result:
            self.assertTrue(len(path) > 0)

    def test_tie_breaking(self):
        # Two parallel edges from 0 to 1 with identical cost functions.
        graph = {
            0: [(1, 5), (1, 3)],
            1: []
        }
        congestion_functions = {
            5: (1, 2),
            3: (1, 2)
        }
        start_nodes = [0]
        end_nodes = [1]

        result = simulate_nash_equilibrium(graph, congestion_functions, start_nodes, end_nodes)
        # Both edges yield the same cost. The tie-breaking rules favor fewer edges (both are one edge)
        # then lexicographical order, so edge 3 should be chosen over edge 5.
        self.assertEqual(result, [[3]])
        self.assertTrue(self.valid_path(graph, result[0], start_nodes[0], end_nodes[0]))

    def test_negative_cost(self):
        # Test with an edge that has a negative constant term.
        graph = {
            0: [(1, 0)],
            1: []
        }
        congestion_functions = {
            0: (1, -5)
        }
        start_nodes = [0]
        end_nodes = [1]

        result = simulate_nash_equilibrium(graph, congestion_functions, start_nodes, end_nodes)
        self.assertEqual(result, [[0]])
        self.assertTrue(self.valid_path(graph, result[0], start_nodes[0], end_nodes[0]))

    def test_convergence(self):
        # More complex graph intended to test convergence under multiple agents.
        graph = {
            0: [(1, 0), (2, 1)],
            1: [(3, 2), (4, 3)],
            2: [(4, 4)],
            3: [(5, 5)],
            4: [(5, 6)],
            5: []
        }
        congestion_functions = {
            0: (1, 1),
            1: (2, 0),
            2: (1, 2),
            3: (1, 1),
            4: (2, 1),
            5: (1, 0),
            6: (1, 2)
        }
        # Three agents with different start and end nodes.
        start_nodes = [0, 0, 1]
        end_nodes = [5, 5, 5]

        result = simulate_nash_equilibrium(graph, congestion_functions, start_nodes, end_nodes)
        self.assertEqual(len(result), 3)
        for i in range(3):
            self.assertTrue(self.valid_path(graph, result[i], start_nodes[i], end_nodes[i]))

if __name__ == '__main__':
    unittest.main()