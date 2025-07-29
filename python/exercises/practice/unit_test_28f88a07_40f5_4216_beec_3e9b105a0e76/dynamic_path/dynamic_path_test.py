import unittest
from dynamic_path import lowest_latency_path, predictive_routing

def constant_congestion_prediction(edge, time):
    return 0.0

class TestDynamicPath(unittest.TestCase):
    def setUp(self):
        self.graph = {
            's': [('a', 1, 3), ('b', 2, 4)],
            'a': [('d', 1, 2)],
            'b': [('d', 3, 5)],
            'd': []
        }

    def test_lowest_latency_simple(self):
        # With no congestion, each edge cost equals its base_cost.
        # Two possible paths:
        #   s -> a -> d has cost 1 + 1 = 2
        #   s -> b -> d has cost 2 + 3 = 5
        # Therefore, the expected path is ['s', 'a', 'd'].
        start_time = 0
        end_time = 10
        path = lowest_latency_path(self.graph, 's', 'd', start_time, end_time)
        self.assertEqual(path, ['s', 'a', 'd'])

    def test_lowest_latency_no_path(self):
        # Test when destination is not reachable.
        graph_no_path = {
            's': [('a', 1, 2)],
            'a': [],
            'd': []
        }
        start_time = 0
        end_time = 10
        path = lowest_latency_path(graph_no_path, 's', 'd', start_time, end_time)
        self.assertEqual(path, [])

    def test_predictive_routing_simple(self):
        # Predictive routing with constant congestion returns the same behavior as lowest_latency.
        start_time = 0
        max_travel_time = 10
        path = predictive_routing(self.graph, 's', 'd', start_time, max_travel_time, constant_congestion_prediction)
        self.assertEqual(path, ['s', 'a', 'd'])

    def test_predictive_routing_time_constraint(self):
        # Modify graph to force a time constraint decision.
        # Graph:
        #   s -> a -> d: travel times 5 and 6 (total 11) exceed max_travel_time.
        #   s -> b -> d: travel times 2 and 3 (total 5) exactly fits the max_travel_time.
        graph_time = {
            's': [('a', 5, 7), ('b', 2, 4)],
            'a': [('d', 6, 8)],
            'b': [('d', 3, 5)],
            'd': []
        }
        start_time = 0
        max_travel_time = 5
        path = predictive_routing(graph_time, 's', 'd', start_time, max_travel_time, constant_congestion_prediction)
        self.assertEqual(path, ['s', 'b', 'd'])

    def test_predictive_routing_no_path(self):
        # Test a scenario where no available path can satisfy the maximum travel time constraint.
        graph_no_fit = {
            's': [('a', 4, 6)],
            'a': [('d', 4, 8)],
            'd': []
        }
        start_time = 0
        max_travel_time = 5  # Minimum required travel time is 4+4 = 8, which exceeds the limit.
        path = predictive_routing(graph_no_fit, 's', 'd', start_time, max_travel_time, constant_congestion_prediction)
        self.assertEqual(path, [])

if __name__ == '__main__':
    unittest.main()