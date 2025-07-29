import unittest
from route_optimization import optimize_route

class TestRouteOptimization(unittest.TestCase):
    def test_simple_graph(self):
        graph = {
            'depot': [('A', 10), ('B', 15)],
            'A': [('B', 5), ('C', 20), ('depot', 10)],
            'B': [('C', 10), ('depot', 15)],
            'C': [('depot', 5)]
        }
        start = 'depot'
        destinations = ['A', 'B', 'C']
        time_window = 60
        values = {'A': 50, 'B': 75, 'C': 25}
        
        result = optimize_route(graph, start, destinations, time_window, values)
        self.assertEqual(result, ['depot', 'A', 'B', 'C', 'depot'])

    def test_time_constraint(self):
        graph = {
            'depot': [('A', 10)],
            'A': [('B', 50), ('depot', 10)],
            'B': [('depot', 10)]
        }
        start = 'depot'
        destinations = ['A', 'B']
        time_window = 40
        values = {'A': 50, 'B': 100}
        
        result = optimize_route(graph, start, destinations, time_window, values)
        self.assertEqual(result, ['depot', 'A', 'depot'])

    def test_unreachable_destination(self):
        graph = {
            'depot': [('A', 10)],
            'A': [('depot', 10)],
            'B': [('depot', 10)]
        }
        start = 'depot'
        destinations = ['A', 'B']
        time_window = 100
        values = {'A': 50, 'B': 100}
        
        result = optimize_route(graph, start, destinations, time_window, values)
        self.assertEqual(result, [])

    def test_empty_destinations(self):
        graph = {
            'depot': [('A', 10)],
            'A': [('depot', 10)]
        }
        start = 'depot'
        destinations = []
        time_window = 100
        values = {}
        
        result = optimize_route(graph, start, destinations, time_window, values)
        self.assertEqual(result, ['depot'])

    def test_impossible_route(self):
        graph = {
            'depot': [('A', 100)],
            'A': [('depot', 100)]
        }
        start = 'depot'
        destinations = ['A']
        time_window = 50
        values = {'A': 1000}
        
        result = optimize_route(graph, start, destinations, time_window, values)
        self.assertEqual(result, [])

    def test_multiple_valid_routes(self):
        graph = {
            'depot': [('A', 5), ('B', 10)],
            'A': [('B', 5), ('depot', 5)],
            'B': [('A', 5), ('depot', 10)]
        }
        start = 'depot'
        destinations = ['A', 'B']
        time_window = 30
        values = {'A': 50, 'B': 75}
        
        result = optimize_route(graph, start, destinations, time_window, values)
        self.assertEqual(len(result), 4)  # Should visit both destinations and return
        self.assertEqual(result[0], 'depot')
        self.assertEqual(result[-1], 'depot')
        self.assertIn('A', result)
        self.assertIn('B', result)

if __name__ == '__main__':
    unittest.main()