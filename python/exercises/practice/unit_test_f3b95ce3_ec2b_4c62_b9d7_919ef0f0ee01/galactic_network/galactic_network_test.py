import unittest
import math
from galactic_network import compute_network_cost

class TestGalacticNetwork(unittest.TestCase):
    def test_single_planet(self):
        # Only one planet: No links needed, cost should be 0.0
        N = 1
        planet_coordinates = [(0, 0, 0)]
        tech_matrix = [[0]]
        critical_planets = []
        K = 0
        result = compute_network_cost(N, planet_coordinates, tech_matrix, critical_planets, K)
        self.assertAlmostEqual(result, 0.0, places=6)

    def test_two_planets(self):
        # Two planets: one link between them
        N = 2
        planet_coordinates = [(0, 0, 0), (3, 4, 0)]  # distance = 5
        tech_matrix = [
            [0, 2],
            [2, 0]
        ]
        critical_planets = []
        K = 0
        # Only one edge: cost = 5*2 = 10
        expected = 10.0
        result = compute_network_cost(N, planet_coordinates, tech_matrix, critical_planets, K)
        self.assertAlmostEqual(result, expected, places=6)

    def test_three_planets_no_additional(self):
        # Three planets in a triangle
        N = 3
        planet_coordinates = [(0, 0, 0), (3, 0, 0), (0, 4, 0)]
        # All tech multipliers are 1
        tech_matrix = [
            [0, 1, 1],
            [1, 0, 1],
            [1, 1, 0]
        ]
        critical_planets = [0]
        K = 2
        # MST: edges (0-1)=3 and (0-2)=4, cost = 7.0.
        # Planet 0 has degree 2, so no additional link needed.
        expected = 7.0
        result = compute_network_cost(N, planet_coordinates, tech_matrix, critical_planets, K)
        self.assertAlmostEqual(result, expected, places=6)

    def test_four_planets_with_additional(self):
        # Four planets in a rectangle
        N = 4
        planet_coordinates = [(0, 0, 0), (3, 0, 0), (0, 4, 0), (3, 4, 0)]
        tech_matrix = [
            [0, 1, 1, 1],
            [1, 0, 1, 1],
            [1, 1, 0, 1],
            [1, 1, 1, 0]
        ]
        # MST (minimum spanning tree) could be:
        # edge 0-1: cost 3
        # edge 0-2: cost 4
        # edge 2-3: cost 3  --> Total MST cost = 10.
        # If we set critical_planets = [1] and require K = 2, then planet 1 initially connects only to 0 (degree 1).
        # Additional cheapest link for planet 1: either 1-3: distance = 4 or 1-2: distance = 5.
        # Best additional link is 1-3 with cost 4.
        N_expected = 10.0 + 4.0  # Total = 14.0
        critical_planets = [1]
        K = 2
        result = compute_network_cost(N, planet_coordinates, tech_matrix, critical_planets, K)
        self.assertAlmostEqual(result, N_expected, places=6)

    def test_five_planets_varied(self):
        # Five planets with varied multipliers
        N = 5
        planet_coordinates = [
            (0.0, 0.0, 0.0),   # Planet 0
            (1.0, 0.0, 0.0),   # Planet 1
            (0.0, 1.0, 0.0),   # Planet 2
            (1.0, 1.0, 0.0),   # Planet 3
            (0.5, 0.5, 1.0)    # Planet 4
        ]
        # Construct a symmetric tech_matrix with custom multipliers
        tech_matrix = [
            [0,    1,   1.5, 1,   0.5],
            [1,    0,   1,   1.2, 1],
            [1.5,  1,   0,   1,   0.8],
            [1,    1.2, 1,   0,   1],
            [0.5,  1,   0.8, 1,   0]
        ]
        # Based on manual computation:
        # Distances:
        # 0-1: 1      => cost = 1*1 = 1.0
        # 0-2: 1      => cost = 1*1.5 = 1.5
        # 0-3: sqrt2  => cost = 1.41421356 *1 = 1.41421356
        # 0-4: sqrt(0.5^2+0.5^2+1^2)=sqrt(1.5)=1.22474487 => cost = 1.22474487*0.5 = 0.61237244
        # 1-2: sqrt2  => cost = 1.41421356*1 = 1.41421356
        # 1-3: 1      => cost = 1*1.2 = 1.2
        # 1-4: 1.22474487 => cost = 1.22474487*1 = 1.22474487
        # 2-3: 1      => cost = 1*1 = 1.0
        # 2-4: 1.22474487 => cost = 1.22474487*0.8 = 0.97979590
        # 3-4: 1.22474487 => cost = 1.22474487*1 = 1.22474487
        # An optimal MST can be selected as:
        # Edge 0-4: 0.61237244
        # Edge 2-4: 0.97979590
        # Edge 0-1: 1.0
        # Edge 2-3: 1.0
        # Total MST cost ~ 3.59216834
        # Now, let critical_planets = [1, 4] with K = 2.
        # Check degrees in MST:
        #   Planet 1: currently connected only via edge 0-1 (degree 1) -> needs one extra edge.
        # For planet 1, additional options:
        #   1-3: cost = 1.2
        #   1-2: cost = 1.41421356, and 1-4 is already in MST (or considered connected via 0-4 and 0-1).
        # Additional edge chosen: 1-3 with cost 1.2.
        #   Planet 4: already degree 2 (connected to 0 and 2) -> no extra needed.
        # Total expected cost ~ 3.59216834 + 1.2 = 4.79216834
        expected = 3.59216834 + 1.2
        critical_planets = [1, 4]
        K = 2
        result = compute_network_cost(N, planet_coordinates, tech_matrix, critical_planets, K)
        self.assertAlmostEqual(result, expected, places=6)

if __name__ == '__main__':
    unittest.main()