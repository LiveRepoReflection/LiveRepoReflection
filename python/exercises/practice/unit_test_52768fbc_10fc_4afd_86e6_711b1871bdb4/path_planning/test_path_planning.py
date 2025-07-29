import unittest
from path_planning import find_optimal_path

class TestPathPlanning(unittest.TestCase):
    def setUp(self):
        # Mock edge cost and capacity functions for testing
        def mock_edge_cost(u, v, t):
            if (u, v) == (0, 1):
                return 2 if t < 5 else 5
            if (u, v) == (1, 2):
                return 3
            return 1

        def mock_edge_capacity(u, v, t):
            if (u, v) == (0, 1) and t >= 5:
                return 0
            return 1

        self.get_edge_cost = mock_edge_cost
        self.get_edge_capacity = mock_edge_capacity

    def test_basic_path(self):
        graph = [(0, 1, 2), (1, 2, 3)]
        result = find_optimal_path(
            N=3,
            M=2,
            graph=graph,
            S=0,
            D=2,
            T_start=0,
            T_end=10,
            L=5,
            get_edge_cost=self.get_edge_cost,
            get_edge_capacity=self.get_edge_capacity
        )
        self.assertEqual(result, [0, 1, 2])

    def test_no_path_exists(self):
        graph = [(0, 1, 2)]
        result = find_optimal_path(
            N=3,
            M=1,
            graph=graph,
            S=0,
            D=2,
            T_start=0,
            T_end=10,
            L=5,
            get_edge_cost=self.get_edge_cost,
            get_edge_capacity=self.get_edge_capacity
        )
        self.assertEqual(result, [])

    def test_capacity_constraint(self):
        graph = [(0, 1, 2), (1, 2, 3)]
        result = find_optimal_path(
            N=3,
            M=2,
            graph=graph,
            S=0,
            D=2,
            T_start=6,
            T_end=10,
            L=5,
            get_edge_cost=self.get_edge_cost,
            get_edge_capacity=self.get_edge_capacity
        )
        self.assertEqual(result, [])

    def test_time_window_constraint(self):
        graph = [(0, 1, 2), (1, 2, 3)]
        result = find_optimal_path(
            N=3,
            M=2,
            graph=graph,
            S=0,
            D=2,
            T_start=11,
            T_end=15,
            L=5,
            get_edge_cost=self.get_edge_cost,
            get_edge_capacity=self.get_edge_capacity
        )
        self.assertEqual(result, [])

    def test_large_graph(self):
        # Create a large graph
        graph = []
        for i in range(999):
            graph.append((i, i+1, 1))
        
        result = find_optimal_path(
            N=1000,
            M=999,
            graph=graph,
            S=0,
            D=999,
            T_start=0,
            T_end=1000,
            L=100,
            get_edge_cost=self.get_edge_cost,
            get_edge_capacity=self.get_edge_capacity
        )
        self.assertGreater(len(result), 0)

    def test_invalid_input(self):
        with self.assertRaises(ValueError):
            find_optimal_path(
                N=0,  # Invalid N
                M=2,
                graph=[(0, 1, 2), (1, 2, 3)],
                S=0,
                D=2,
                T_start=0,
                T_end=10,
                L=5,
                get_edge_cost=self.get_edge_cost,
                get_edge_capacity=self.get_edge_capacity
            )

    def test_multiple_paths(self):
        graph = [
            (0, 1, 2), (1, 3, 2),
            (0, 2, 2), (2, 3, 2)
        ]
        result = find_optimal_path(
            N=4,
            M=4,
            graph=graph,
            S=0,
            D=3,
            T_start=0,
            T_end=10,
            L=5,
            get_edge_cost=self.get_edge_cost,
            get_edge_capacity=self.get_edge_capacity
        )
        self.assertTrue(result in [[0, 1, 3], [0, 2, 3]])

    def test_lookahead_optimization(self):
        graph = [(0, 1, 2), (1, 2, 3)]
        result = find_optimal_path(
            N=3,
            M=2,
            graph=graph,
            S=0,
            D=2,
            T_start=0,
            T_end=10,
            L=1,  # Small lookahead
            get_edge_cost=self.get_edge_cost,
            get_edge_capacity=self.get_edge_capacity
        )
        # Should find path before cost increases
        self.assertEqual(result, [0, 1, 2])

if __name__ == '__main__':
    unittest.main()