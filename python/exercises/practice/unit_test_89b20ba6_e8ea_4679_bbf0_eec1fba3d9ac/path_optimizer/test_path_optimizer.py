import unittest
from path_optimizer import find_optimal_path

class TestPathOptimizer(unittest.TestCase):
    def setUp(self):
        self.graph = {
            'A': {
                'coordinates': (37.7749, -122.4194),
                'traffic_density': 0.2,
                'edges': {
                    'B': {
                        'length': 5000,
                        'speed_limit': 50,
                        'toll_cost': 2,
                        'congestion_factors': [1.0] * 24
                    },
                    'C': {
                        'length': 3000,
                        'speed_limit': 30,
                        'toll_cost': 1,
                        'congestion_factors': [1.0] * 24
                    }
                }
            },
            'B': {
                'coordinates': (37.7833, -122.4167),
                'traffic_density': 0.5,
                'edges': {
                    'D': {
                        'length': 4000,
                        'speed_limit': 40,
                        'toll_cost': 3,
                        'congestion_factors': [1.0] * 24
                    }
                }
            },
            'C': {
                'coordinates': (37.7900, -122.4000),
                'traffic_density': 0.8,
                'edges': {
                    'D': {
                        'length': 2000,
                        'speed_limit': 60,
                        'toll_cost': 0,
                        'congestion_factors': [1.0] * 24
                    }
                }
            },
            'D': {
                'coordinates': (37.7967, -122.3933),
                'traffic_density': 0.1,
                'edges': {}
            }
        }

    def test_basic_path_finding(self):
        result = find_optimal_path(
            self.graph,
            'A',
            'D',
            departure_time=8,
            max_budget=5,
            earliest_arrival=0.1,
            latest_arrival=0.5,
            alpha=0.5
        )
        self.assertIsInstance(result, tuple)
        self.assertEqual(len(result), 4)
        path, travel_time, risk, toll = result
        self.assertIsInstance(path, list)
        self.assertGreater(len(path), 0)
        self.assertIsInstance(travel_time, float)
        self.assertIsInstance(risk, float)
        self.assertIsInstance(toll, int)

    def test_no_path_within_budget(self):
        result = find_optimal_path(
            self.graph,
            'A',
            'D',
            departure_time=8,
            max_budget=0,
            earliest_arrival=0.1,
            latest_arrival=0.5,
            alpha=0.5
        )
        self.assertEqual(result, ([], 0.0, 0.0, 0))

    def test_same_start_and_end(self):
        result = find_optimal_path(
            self.graph,
            'A',
            'A',
            departure_time=8,
            max_budget=5,
            earliest_arrival=0.1,
            latest_arrival=0.5,
            alpha=0.5
        )
        self.assertEqual(result, (['A'], 0.0, 0.2, 0))

    def test_time_constraints(self):
        result = find_optimal_path(
            self.graph,
            'A',
            'D',
            departure_time=8,
            max_budget=5,
            earliest_arrival=2.0,
            latest_arrival=3.0,
            alpha=0.5
        )
        self.assertEqual(result, ([], 0.0, 0.0, 0))

    def test_risk_aversion(self):
        low_risk_result = find_optimal_path(
            self.graph,
            'A',
            'D',
            departure_time=8,
            max_budget=5,
            earliest_arrival=0.1,
            latest_arrival=0.5,
            alpha=0.9
        )
        high_risk_result = find_optimal_path(
            self.graph,
            'A',
            'D',
            departure_time=8,
            max_budget=5,
            earliest_arrival=0.1,
            latest_arrival=0.5,
            alpha=0.1
        )
        self.assertNotEqual(low_risk_result[0], high_risk_result[0])

    def test_congestion_factors(self):
        modified_graph = self.graph.copy()
        modified_graph['A']['edges']['B']['congestion_factors'] = [5.0] * 24
        result = find_optimal_path(
            modified_graph,
            'A',
            'D',
            departure_time=8,
            max_budget=5,
            earliest_arrival=0.1,
            latest_arrival=0.5,
            alpha=0.5
        )
        self.assertEqual(result[0], ['A', 'C', 'D'])

if __name__ == '__main__':
    unittest.main()