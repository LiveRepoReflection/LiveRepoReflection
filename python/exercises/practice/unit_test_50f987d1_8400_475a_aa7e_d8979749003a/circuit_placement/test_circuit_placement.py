import unittest
from circuit_placement import circuit_placement

class TestCircuitPlacement(unittest.TestCase):
    def test_small_case(self):
        N = 4
        M = 3
        connections = [(0, 1, 10), (1, 2, 5), (2, 3, 2)]
        D = 5
        result = circuit_placement(N, M, connections, D)
        self.assertEqual(len(result), N)
        self._verify_distances(result, D)
        self._verify_connections(result, connections)

    def test_no_connections(self):
        N = 5
        M = 0
        connections = []
        D = 3
        result = circuit_placement(N, M, connections, D)
        self.assertEqual(len(result), N)
        self._verify_distances(result, D)

    def test_single_component(self):
        N = 1
        M = 0
        connections = []
        D = 1
        result = circuit_placement(N, M, connections, D)
        self.assertEqual(len(result), N)

    def test_fully_connected(self):
        N = 3
        M = 3
        connections = [(0, 1, 5), (1, 2, 5), (0, 2, 5)]
        D = 2
        result = circuit_placement(N, M, connections, D)
        self.assertEqual(len(result), N)
        self._verify_distances(result, D)
        self._verify_connections(result, connections)

    def test_large_distance_constraint(self):
        N = 3
        M = 2
        connections = [(0, 1, 1), (1, 2, 1)]
        D = 20
        result = circuit_placement(N, M, connections, D)
        self.assertEqual(len(result), N)
        self._verify_distances(result, D)

    def _verify_distances(self, placements, D):
        for i in range(len(placements)):
            for j in range(i+1, len(placements)):
                x1, y1 = placements[i]
                x2, y2 = placements[j]
                distance = ((x1 - x2)**2 + (y1 - y2)**2)**0.5
                self.assertGreaterEqual(distance, D, 
                    f"Components {i} and {j} are too close: {distance} < {D}")

    def _verify_connections(self, placements, connections):
        for c1, c2, _ in connections:
            x1, y1 = placements[c1]
            x2, y2 = placements[c2]
            self.assertNotEqual((x1, y1), (x2, y2),
                f"Connected components {c1} and {c2} are at same position")

if __name__ == '__main__':
    unittest.main()