import unittest
import math
from time_route import optimal_route

def example_travel_time_function(time):
    hour = (time // 60) % 24
    if 7 <= hour < 9 or 17 <= hour < 19:
        return 10
    else:
        return 5

class TimeRouteTest(unittest.TestCase):

    def test_example_route(self):
        graph = {
            1: {2: example_travel_time_function, 3: example_travel_time_function},
            2: {4: example_travel_time_function},
            3: {4: example_travel_time_function},
            4: {}
        }
        start_intersection = 1
        destination_intersection = 4
        start_time = 480  # 8:00 AM
        travel_time, route = optimal_route(graph, start_intersection, destination_intersection, start_time)
        self.assertEqual(travel_time, 20)
        self.assertEqual(route[0], 1)
        self.assertEqual(route[-1], 4)
        self.assertEqual(len(route), 3)

    def test_no_route(self):
        graph = {
            1: {2: example_travel_time_function},
            2: {},
            3: {4: example_travel_time_function},
            4: {}
        }
        start_intersection = 1
        destination_intersection = 4
        start_time = 300
        travel_time, route = optimal_route(graph, start_intersection, destination_intersection, start_time)
        self.assertEqual(travel_time, float('inf'))
        self.assertEqual(route, [])

    def test_trivial_same_node(self):
        graph = {
            1: {}
        }
        start_intersection = 1
        destination_intersection = 1
        start_time = 600
        travel_time, route = optimal_route(graph, start_intersection, destination_intersection, start_time)
        self.assertEqual(travel_time, 0)
        self.assertEqual(route, [1])

    def test_complex_graph(self):
        def fast_function(time):
            return 3

        def slow_function(time):
            return 7

        graph = {
            1: {2: fast_function, 3: slow_function},
            2: {4: fast_function, 5: slow_function},
            3: {5: fast_function},
            4: {6: fast_function},
            5: {6: slow_function, 4: fast_function},
            6: {}
        }
        start_intersection = 1
        destination_intersection = 6
        start_time = 100

        travel_time, route = optimal_route(graph, start_intersection, destination_intersection, start_time)
        self.assertEqual(travel_time, 9)
        self.assertEqual(route[0], 1)
        self.assertEqual(route[-1], 6)

    def test_time_calculation(self):
        def variable_time_function(time):
            if time % 100 < 50:
                return 2
            else:
                return 12

        graph = {
            1: {2: variable_time_function},
            2: {3: variable_time_function},
            3: {}
        }
        start_intersection = 1
        destination_intersection = 3
        
        start_time = 20
        travel_time, route = optimal_route(graph, start_intersection, destination_intersection, start_time)
        self.assertEqual(travel_time, 4)
        self.assertEqual(route, [1, 2, 3])
        
        start_time = 60
        travel_time, route = optimal_route(graph, start_intersection, destination_intersection, start_time)
        self.assertEqual(travel_time, 24)
        self.assertEqual(route, [1, 2, 3])

if __name__ == '__main__':
    unittest.main()