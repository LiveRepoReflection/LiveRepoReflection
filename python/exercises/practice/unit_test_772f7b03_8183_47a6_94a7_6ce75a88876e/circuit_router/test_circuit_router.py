import unittest
from circuit_router.circuit_router import find_paths

class TestCircuitRouter(unittest.TestCase):
    def test_small_grid_no_obstacles(self):
        grid_size = 5
        terminal_pairs = [((0, 0), (4, 4))]
        obstacles = set()
        wire_width = 1
        
        result = find_paths(grid_size, terminal_pairs, obstacles, wire_width)
        self.assertEqual(len(result), 1)
        self.assertTrue(len(result[0]) > 0)
        self.assertEqual(result[0][0], (0, 0))
        self.assertEqual(result[0][-1], (4, 4))

    def test_medium_grid_with_obstacles(self):
        grid_size = 10
        terminal_pairs = [((1, 1), (8, 8)), ((2, 2), (7, 7))]
        obstacles = {(4, 4), (5, 5), (6, 6)}
        wire_width = 1
        
        result = find_paths(grid_size, terminal_pairs, obstacles, wire_width)
        self.assertEqual(len(result), 2)
        for path in result:
            self.assertTrue(len(path) > 0)
            for point in path:
                self.assertNotIn(point, obstacles)

    def test_large_grid_multiple_pairs(self):
        grid_size = 20
        terminal_pairs = [
            ((0, 0), (19, 19)),
            ((5, 5), (15, 15)),
            ((10, 0), (10, 19))
        ]
        obstacles = {(i, i) for i in range(5, 15)}
        wire_width = 2
        
        result = find_paths(grid_size, terminal_pairs, obstacles, wire_width)
        self.assertEqual(len(result), 3)
        for i, path in enumerate(result):
            if not path:
                continue  # Some paths might be impossible
            self.assertEqual(path[0], terminal_pairs[i][0])
            self.assertEqual(path[-1], terminal_pairs[i][1])

    def test_impossible_path(self):
        grid_size = 5
        terminal_pairs = [((0, 0), (4, 4))]
        obstacles = {(1, 1), (2, 2), (3, 3)}
        wire_width = 2
        
        result = find_paths(grid_size, terminal_pairs, obstacles, wire_width)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], [])

    def test_wire_spacing_constraint(self):
        grid_size = 10
        terminal_pairs = [((1, 1), (8, 8)), ((2, 2), (7, 7))]
        obstacles = set()
        wire_width = 3
        
        result = find_paths(grid_size, terminal_pairs, obstacles, wire_width)
        self.assertEqual(len(result), 2)
        if len(result[0]) > 0 and len(result[1]) > 0:
            # Check that wires don't come within wire_width distance
            path1_set = set(result[0])
            path2_set = set(result[1])
            for p1 in path1_set:
                for dx in range(-wire_width//2 + 1, wire_width//2):
                    for dy in range(-wire_width//2 + 1, wire_width//2):
                        if (p1[0] + dx, p1[1] + dy) in path2_set:
                            self.fail("Wires violate spacing constraint")

    def test_grid_boundaries(self):
        grid_size = 5
        terminal_pairs = [((0, 0), (4, 4))]
        obstacles = set()
        wire_width = 2
        
        result = find_paths(grid_size, terminal_pairs, obstacles, wire_width)
        self.assertEqual(len(result), 1)
        for point in result[0]:
            self.assertTrue(0 <= point[0] < grid_size)
            self.assertTrue(0 <= point[1] < grid_size)

    def test_multiple_shortest_paths(self):
        grid_size = 3
        terminal_pairs = [((0, 0), (2, 2))]
        obstacles = set()
        wire_width = 1
        
        result = find_paths(grid_size, terminal_pairs, obstacles, wire_width)
        self.assertEqual(len(result), 1)
        # There are multiple valid shortest paths, just verify length
        self.assertEqual(len(result[0]), 5)  # Manhattan distance + 1

    def test_empty_input(self):
        grid_size = 10
        terminal_pairs = []
        obstacles = set()
        wire_width = 1
        
        result = find_paths(grid_size, terminal_pairs, obstacles, wire_width)
        self.assertEqual(len(result), 0)

if __name__ == '__main__':
    unittest.main()