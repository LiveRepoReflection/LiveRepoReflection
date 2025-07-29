import unittest
from quantum_router import find_quantum_paths

class TestQuantumRouter(unittest.TestCase):
    def test_simple_2x2_grid(self):
        grid = [
            [1, 1, 1, 1],
            [1, 0, 0, 1],
            [1, 0, 0, 1],
            [1, 1, 1, 1]
        ]
        qubits = [(1, 1), (2, 2)]
        paths = find_quantum_paths(grid, qubits)
        
        self.assertIsNotNone(paths)
        self.assertTrue(self._verify_connectivity(paths, qubits))
        self.assertTrue(self._verify_no_obstacles(paths, grid))

    def test_impossible_connection(self):
        grid = [
            [1, 1, 1, 1, 1],
            [1, 0, 1, 0, 1],
            [1, 1, 1, 1, 1],
            [1, 0, 1, 0, 1],
            [1, 1, 1, 1, 1]
        ]
        qubits = [(1, 1), (3, 3)]
        paths = find_quantum_paths(grid, qubits)
        self.assertEqual(paths, [])

    def test_complex_routing(self):
        grid = [
            [1, 1, 1, 1, 1],
            [1, 0, 0, 0, 1],
            [1, 0, 1, 0, 1],
            [1, 0, 0, 0, 1],
            [1, 1, 1, 1, 1]
        ]
        qubits = [(1, 1), (1, 3), (3, 1), (3, 3)]
        paths = find_quantum_paths(grid, qubits)
        
        self.assertIsNotNone(paths)
        self.assertTrue(self._verify_connectivity(paths, qubits))
        self.assertTrue(self._verify_no_obstacles(paths, grid))
        self.assertTrue(self._verify_path_uniqueness(paths))

    def test_large_grid(self):
        # Create a 10x10 grid with some obstacles
        grid = [[0] * 10 for _ in range(10)]
        for i in range(10):
            grid[0][i] = grid[9][i] = grid[i][0] = grid[i][9] = 1
        grid[4][4] = grid[4][5] = grid[5][4] = grid[5][5] = 1
        
        qubits = [(1, 1), (1, 8), (8, 1), (8, 8)]
        paths = find_quantum_paths(grid, qubits)
        
        self.assertIsNotNone(paths)
        self.assertTrue(self._verify_connectivity(paths, qubits))
        self.assertTrue(self._verify_no_obstacles(paths, grid))

    def test_edge_cases(self):
        # Test with minimum possible valid grid
        grid = [
            [1, 1, 1],
            [1, 0, 1],
            [1, 1, 1]
        ]
        qubits = [(1, 1)]
        paths = find_quantum_paths(grid, qubits)
        self.assertEqual(paths, [])  # Single qubit, no paths needed

        # Test with no qubits
        grid = [[1, 1], [1, 1]]
        qubits = []
        paths = find_quantum_paths(grid, qubits)
        self.assertEqual(paths, [])

    def _verify_connectivity(self, paths, qubits):
        # Create an adjacency list from the paths
        adj_list = {qubit: set() for qubit in qubits}
        for path in paths:
            if len(path) >= 2:
                start, end = path[0], path[-1]
                adj_list[start].add(end)
                adj_list[end].add(start)

        # Use DFS to check if all qubits are connected
        visited = set()
        def dfs(node):
            visited.add(node)
            for neighbor in adj_list[node]:
                if neighbor not in visited:
                    dfs(neighbor)

        if qubits:
            dfs(qubits[0])
            return len(visited) == len(qubits)
        return True

    def _verify_no_obstacles(self, paths, grid):
        for path in paths:
            for row, col in path:
                if grid[row][col] == 1:
                    return False
        return True

    def _verify_path_uniqueness(self, paths):
        # Check that there's at most one path between any two qubits
        path_ends = set()
        for path in paths:
            if len(path) >= 2:
                ends = frozenset([path[0], path[-1]])
                if ends in path_ends:
                    return False
                path_ends.add(ends)
        return True

if __name__ == '__main__':
    unittest.main()