import unittest
from intercity_network import max_cities_visited

class TestIntercityNetwork(unittest.TestCase):
    def test_simple_network(self):
        cities = {1, 2, 3}
        transport = [(1, 2, 10, 5), (2, 3, 15, 8)]
        origin = 1
        budget = 30
        time_limit = 15
        self.assertEqual(max_cities_visited(cities, transport, origin, budget, time_limit), 3)

    def test_no_possible_paths(self):
        cities = {1, 2, 3}
        transport = [(1, 2, 10, 5)]
        origin = 3
        budget = 50
        time_limit = 20
        self.assertEqual(max_cities_visited(cities, transport, origin, budget, time_limit), 1)

    def test_multiple_path_options(self):
        cities = {1, 2, 3, 4}
        transport = [(1, 2, 10, 5), (1, 3, 15, 8), (2, 4, 20, 12), (3, 4, 5, 3)]
        origin = 1
        budget = 40
        time_limit = 20
        self.assertEqual(max_cities_visited(cities, transport, origin, budget, time_limit), 3)

    def test_zero_budget(self):
        cities = {1, 2}
        transport = [(1, 2, 10, 5)]
        origin = 1
        budget = 0
        time_limit = 5
        self.assertEqual(max_cities_visited(cities, transport, origin, budget, time_limit), 1)

    def test_zero_time(self):
        cities = {1, 2}
        transport = [(1, 2, 10, 5)]
        origin = 1
        budget = 10
        time_limit = 0
        self.assertEqual(max_cities_visited(cities, transport, origin, budget, time_limit), 1)

    def test_cyclic_graph(self):
        cities = {1, 2, 3}
        transport = [(1, 2, 10, 5), (2, 3, 15, 8), (3, 1, 5, 3)]
        origin = 1
        budget = 50
        time_limit = 30
        self.assertEqual(max_cities_visited(cities, transport, origin, budget, time_limit), 3)

    def test_disconnected_graph(self):
        cities = {1, 2, 3, 4}
        transport = [(1, 2, 10, 5), (3, 4, 15, 8)]
        origin = 1
        budget = 50
        time_limit = 20
        self.assertEqual(max_cities_visited(cities, transport, origin, budget, time_limit), 2)

    def test_multiple_transport_options(self):
        cities = {1, 2, 3}
        transport = [(1, 2, 10, 5), (1, 2, 15, 3), (2, 3, 20, 10), (2, 3, 10, 15)]
        origin = 1
        budget = 30
        time_limit = 20
        self.assertEqual(max_cities_visited(cities, transport, origin, budget, time_limit), 3)

    def test_large_network(self):
        cities = {1, 2, 3, 4, 5, 6, 7, 8}
        transport = [
            (1, 2, 5, 3), (1, 3, 10, 5), (2, 4, 8, 4), 
            (3, 4, 12, 6), (4, 5, 6, 2), (5, 6, 7, 3),
            (5, 7, 15, 8), (6, 8, 9, 4), (7, 8, 5, 2)
        ]
        origin = 1
        budget = 50
        time_limit = 30
        self.assertEqual(max_cities_visited(cities, transport, origin, budget, time_limit), 6)

if __name__ == '__main__':
    unittest.main()