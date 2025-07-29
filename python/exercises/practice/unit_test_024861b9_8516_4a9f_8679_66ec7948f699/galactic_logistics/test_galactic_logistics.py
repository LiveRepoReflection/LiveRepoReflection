import unittest
from galactic_logistics import optimize_logistics

class TestGalacticLogistics(unittest.TestCase):
    def test_basic_two_planets(self):
        N = 2  # number of planets
        M = 1  # number of goods
        wormholes = [(1, 2, 10, 50), (2, 1, 15, 75)]
        planet_data = [
            {
                "production": [(1, 100)],
                "demand": [(1, 20)]
            },
            {
                "production": [(1, 30)],
                "demand": [(1, 110)]
            }
        ]
        T_max = 1000
        self.assertEqual(optimize_logistics(N, M, wormholes, planet_data, T_max), 4000)

    def test_impossible_delivery(self):
        N = 2
        M = 1
        wormholes = [(1, 2, 10, 50)]  # Only one-way wormhole
        planet_data = [
            {
                "production": [(1, 0)],  # No production
                "demand": [(1, 20)]
            },
            {
                "production": [(1, 30)],
                "demand": [(1, 10)]
            }
        ]
        T_max = 1000
        self.assertEqual(optimize_logistics(N, M, wormholes, planet_data, T_max), -1)

    def test_time_constraint_violation(self):
        N = 2
        M = 1
        wormholes = [(1, 2, 2000, 50)]  # Time exceeds T_max
        planet_data = [
            {
                "production": [(1, 100)],
                "demand": [(1, 0)]
            },
            {
                "production": [(1, 0)],
                "demand": [(1, 50)]
            }
        ]
        T_max = 1000
        self.assertEqual(optimize_logistics(N, M, wormholes, planet_data, T_max), -1)

    def test_complex_network(self):
        N = 4
        M = 2
        wormholes = [
            (1, 2, 10, 50),
            (2, 3, 15, 60),
            (3, 4, 20, 70),
            (1, 4, 50, 40),
            (2, 4, 30, 55),
            (3, 1, 25, 65)
        ]
        planet_data = [
            {
                "production": [(1, 200), (2, 150)],
                "demand": [(1, 50), (2, 50)]
            },
            {
                "production": [(1, 100), (2, 100)],
                "demand": [(1, 100), (2, 100)]
            },
            {
                "production": [(1, 150), (2, 50)],
                "demand": [(1, 150), (2, 100)]
            },
            {
                "production": [(1, 50), (2, 200)],
                "demand": [(1, 200), (2, 150)]
            }
        ]
        T_max = 1000
        result = optimize_logistics(N, M, wormholes, planet_data, T_max)
        self.assertGreater(result, 0)  # Should find a valid solution

    def test_multiple_goods_same_planet(self):
        N = 2
        M = 2
        wormholes = [(1, 2, 10, 50), (2, 1, 10, 50)]
        planet_data = [
            {
                "production": [(1, 100), (2, 100)],
                "demand": [(1, 100), (2, 0)]
            },
            {
                "production": [(1, 0), (2, 0)],
                "demand": [(1, 0), (2, 100)]
            }
        ]
        T_max = 100
        self.assertEqual(optimize_logistics(N, M, wormholes, planet_data, T_max), 5000)

    def test_edge_cases(self):
        # Test minimum possible values
        N = 1
        M = 1
        wormholes = []
        planet_data = [
            {
                "production": [(1, 10)],
                "demand": [(1, 10)]
            }
        ]
        T_max = 1
        self.assertEqual(optimize_logistics(N, M, wormholes, planet_data, T_max), 0)

        # Test maximum constraints
        N = 50
        M = 20
        wormholes = [(1, 2, 100, 1000)]
        planet_data = [{"production": [], "demand": []} for _ in range(N)]
        T_max = 100000
        self.assertEqual(optimize_logistics(N, M, wormholes, planet_data, T_max), 0)

    def test_disconnected_graph(self):
        N = 3
        M = 1
        wormholes = [(1, 2, 10, 50)]  # Planet 3 is disconnected
        planet_data = [
            {
                "production": [(1, 100)],
                "demand": [(1, 0)]
            },
            {
                "production": [(1, 0)],
                "demand": [(1, 50)]
            },
            {
                "production": [(1, 0)],
                "demand": [(1, 10)]
            }
        ]
        T_max = 1000
        self.assertEqual(optimize_logistics(N, M, wormholes, planet_data, T_max), -1)

if __name__ == '__main__':
    unittest.main()