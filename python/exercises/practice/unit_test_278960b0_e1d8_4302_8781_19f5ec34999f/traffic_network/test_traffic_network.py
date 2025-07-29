import unittest
from traffic_network import optimize_traffic

class TestTrafficNetwork(unittest.TestCase):
    def test_basic_path(self):
        network = {
            1: [(2, 1000, 10)],  # intersection 1 connects to 2, length 1000m, capacity 10 vehicles/s
            2: [(3, 1000, 10)],
            3: []
        }
        result = optimize_traffic(
            network=network,
            source=1,
            destination=3,
            total_flow=5,
            default_speed_limit=20,
            penalty_exponent=2,
            max_penalty=1.0
        )
        self.assertIsInstance(result, dict)
        self.assertEqual(len(result), 2)  # Should contain two segments
        for (start, end), speed in result.items():
            self.assertTrue(0.5 <= speed <= 1.5)  # Speed limits within constraints

    def test_no_path_exists(self):
        network = {
            1: [(2, 1000, 10)],
            2: [],
            3: []  # No path to 3
        }
        result = optimize_traffic(
            network=network,
            source=1,
            destination=3,
            total_flow=5,
            default_speed_limit=20,
            penalty_exponent=2,
            max_penalty=1.0
        )
        self.assertEqual(result, {})

    def test_capacity_constraint(self):
        network = {
            1: [(2, 1000, 5)],  # capacity too low for total_flow
            2: [(3, 1000, 5)],
            3: []
        }
        result = optimize_traffic(
            network=network,
            source=1,
            destination=3,
            total_flow=10,  # Exceeds capacity
            default_speed_limit=20,
            penalty_exponent=2,
            max_penalty=1.0
        )
        self.assertEqual(result, {})

    def test_multiple_paths(self):
        network = {
            1: [(2, 1000, 10), (4, 2000, 20)],
            2: [(3, 1000, 10)],
            3: [],
            4: [(3, 1000, 20)]
        }
        result = optimize_traffic(
            network=network,
            source=1,
            destination=3,
            total_flow=8,
            default_speed_limit=20,
            penalty_exponent=2,
            max_penalty=2.0
        )
        self.assertIsInstance(result, dict)
        self.assertGreater(len(result), 0)

    def test_large_network(self):
        # Create a large network with 100 nodes in a chain
        network = {i: [(i+1, 1000, 20)] for i in range(1, 100)}
        network[100] = []
        
        result = optimize_traffic(
            network=network,
            source=1,
            destination=100,
            total_flow=5,
            default_speed_limit=20,
            penalty_exponent=2,
            max_penalty=50.0
        )
        self.assertIsInstance(result, dict)
        self.assertEqual(len(result), 99)  # Should have 99 segments

    def test_speed_limit_bounds(self):
        network = {
            1: [(2, 1000, 10)],
            2: [(3, 1000, 10)],
            3: []
        }
        result = optimize_traffic(
            network=network,
            source=1,
            destination=3,
            total_flow=5,
            default_speed_limit=20,
            penalty_exponent=2,
            max_penalty=1.0
        )
        for speed in result.values():
            self.assertGreaterEqual(speed, 0.5)
            self.assertLessEqual(speed, 1.5)

    def test_congestion_penalty_limit(self):
        network = {
            1: [(2, 1000, 10)],
            2: [(3, 1000, 10)],
            3: []
        }
        result = optimize_traffic(
            network=network,
            source=1,
            destination=3,
            total_flow=9,  # High flow causing high congestion
            default_speed_limit=20,
            penalty_exponent=2,
            max_penalty=0.1  # Very low penalty threshold
        )
        self.assertEqual(result, {})  # Should be impossible to satisfy

    def test_invalid_inputs(self):
        with self.assertRaises((ValueError, TypeError)):
            optimize_traffic(
                network={},  # Empty network
                source=1,
                destination=3,
                total_flow=-5,  # Invalid negative flow
                default_speed_limit=20,
                penalty_exponent=2,
                max_penalty=1.0
            )

    def test_complex_network_with_cycles(self):
        network = {
            1: [(2, 1000, 10), (4, 1500, 15)],
            2: [(3, 1000, 10), (4, 800, 12)],
            3: [(5, 1000, 10)],
            4: [(3, 1000, 10), (5, 2000, 20)],
            5: []
        }
        result = optimize_traffic(
            network=network,
            source=1,
            destination=5,
            total_flow=7,
            default_speed_limit=20,
            penalty_exponent=2,
            max_penalty=3.0
        )
        self.assertIsInstance(result, dict)
        self.assertGreater(len(result), 0)

if __name__ == '__main__':
    unittest.main()