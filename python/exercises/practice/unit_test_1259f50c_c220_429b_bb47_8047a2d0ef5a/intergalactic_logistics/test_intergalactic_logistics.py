import unittest
from intergalactic_logistics.intergalactic_logistics import max_resource_transport

class TestIntergalacticLogistics(unittest.TestCase):
    def test_simple_case(self):
        num_planets = 4
        wormholes = [(0, 1, 10), (1, 2, 5), (2, 3, 8)]
        source = 0
        destination = 3
        timeframe = 1
        self.assertEqual(max_resource_transport(num_planets, wormholes, source, destination, timeframe), 5)

    def test_multiple_paths(self):
        num_planets = 4
        wormholes = [(0, 1, 10), (0, 2, 5), (1, 3, 8), (2, 3, 4)]
        source = 0
        destination = 3
        timeframe = 1
        self.assertEqual(max_resource_transport(num_planets, wormholes, source, destination, timeframe), 12)

    def test_no_path(self):
        num_planets = 3
        wormholes = [(0, 1, 10), (1, 0, 5)]
        source = 0
        destination = 2
        timeframe = 1
        self.assertEqual(max_resource_transport(num_planets, wormholes, source, destination, timeframe), 0)

    def test_direct_connection(self):
        num_planets = 2
        wormholes = [(0, 1, 15)]
        source = 0
        destination = 1
        timeframe = 2
        self.assertEqual(max_resource_transport(num_planets, wormholes, source, destination, timeframe), 30)

    def test_multiple_wormholes_same_path(self):
        num_planets = 3
        wormholes = [(0, 1, 5), (0, 1, 10), (1, 2, 15)]
        source = 0
        destination = 2
        timeframe = 1
        self.assertEqual(max_resource_transport(num_planets, wormholes, source, destination, timeframe), 15)

    def test_large_timeframe(self):
        num_planets = 3
        wormholes = [(0, 1, 5), (1, 2, 3)]
        source = 0
        destination = 2
        timeframe = 100
        self.assertEqual(max_resource_transport(num_planets, wormholes, source, destination, timeframe), 300)

    def test_complex_network(self):
        num_planets = 6
        wormholes = [
            (0, 1, 16), (0, 2, 13),
            (1, 2, 10), (1, 3, 12),
            (2, 1, 4), (2, 4, 14),
            (3, 2, 9), (3, 5, 20),
            (4, 3, 7), (4, 5, 4)
        ]
        source = 0
        destination = 5
        timeframe = 1
        self.assertEqual(max_resource_transport(num_planets, wormholes, source, destination, timeframe), 23)

    def test_disconnected_graph(self):
        num_planets = 4
        wormholes = [(0, 1, 10), (2, 3, 5)]
        source = 0
        destination = 3
        timeframe = 1
        self.assertEqual(max_resource_transport(num_planets, wormholes, source, destination, timeframe), 0)

    def test_cyclic_graph(self):
        num_planets = 3
        wormholes = [(0, 1, 5), (1, 2, 3), (2, 0, 2)]
        source = 0
        destination = 2
        timeframe = 1
        self.assertEqual(max_resource_transport(num_planets, wormholes, source, destination, timeframe), 3)

    def test_max_capacity(self):
        num_planets = 2
        wormholes = [(0, 1, 1000)]
        source = 0
        destination = 1
        timeframe = 1000
        self.assertEqual(max_resource_transport(num_planets, wormholes, source, destination, timeframe), 1000000)

if __name__ == '__main__':
    unittest.main()