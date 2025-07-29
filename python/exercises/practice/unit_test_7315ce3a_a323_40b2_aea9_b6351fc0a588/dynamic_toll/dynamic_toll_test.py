import unittest
import math

# Import the function to test. Assume that the main optimization function is named optimize_tolls.
from dynamic_toll import optimize_tolls

def bpr_function_factory(capacity):
    # Returns a BPR congestion function with fixed capacity.
    return lambda volume: 1 + 0.15 * ((volume / capacity) ** 4)

class TestDynamicTollOptimization(unittest.TestCase):
    def test_single_edge_network(self):
        # Simple network with one edge and one OD pair.
        graph = {
            'nodes': ['A', 'B'],
            'edges': [
                {
                    'id': 'A_B',
                    'start': 'A',
                    'end': 'B',
                    'capacity': 100,
                    'free_flow_time': 10,
                    'congestion_func': bpr_function_factory(100)
                }
            ]
        }
        od_pairs = [
            {
                'origin': 'A',
                'destination': 'B',
                'demand': 50
            }
        ]
        T = 3
        max_toll = 10

        toll_matrix = optimize_tolls(graph, od_pairs, T, max_toll)
        
        # Check that toll_matrix is a list with T sublists.
        self.assertIsInstance(toll_matrix, list)
        self.assertEqual(len(toll_matrix), T)
        # Each sublist should have one toll corresponding to the one edge.
        for row in toll_matrix:
            self.assertIsInstance(row, list)
            self.assertEqual(len(row), len(graph['edges']))
            for toll in row:
                self.assertIsInstance(toll, int)
                self.assertGreaterEqual(toll, 0)
                self.assertLessEqual(toll, max_toll)
    
    def test_two_edge_parallel_network(self):
        # Network with two parallel edges between the same nodes.
        graph = {
            'nodes': ['A', 'B'],
            'edges': [
                {
                    'id': 'A_B_fast',
                    'start': 'A',
                    'end': 'B',
                    'capacity': 80,
                    'free_flow_time': 5,
                    'congestion_func': bpr_function_factory(80)
                },
                {
                    'id': 'A_B_slow',
                    'start': 'A',
                    'end': 'B',
                    'capacity': 150,
                    'free_flow_time': 8,
                    'congestion_func': bpr_function_factory(150)
                }
            ]
        }
        od_pairs = [
            {
                'origin': 'A',
                'destination': 'B',
                'demand': 100
            }
        ]
        T = 5
        max_toll = 15

        toll_matrix = optimize_tolls(graph, od_pairs, T, max_toll)

        # Verify dimensions
        self.assertIsInstance(toll_matrix, list)
        self.assertEqual(len(toll_matrix), T)
        for row in toll_matrix:
            self.assertIsInstance(row, list)
            self.assertEqual(len(row), len(graph['edges']))
            for toll in row:
                self.assertIsInstance(toll, int)
                self.assertGreaterEqual(toll, 0)
                self.assertLessEqual(toll, max_toll)
    
    def test_larger_network(self):
        # A larger network with 4 nodes and 5 edges.
        graph = {
            'nodes': ['A', 'B', 'C', 'D'],
            'edges': [
                {
                    'id': 'A_B',
                    'start': 'A',
                    'end': 'B',
                    'capacity': 120,
                    'free_flow_time': 7,
                    'congestion_func': bpr_function_factory(120)
                },
                {
                    'id': 'B_C',
                    'start': 'B',
                    'end': 'C',
                    'capacity': 90,
                    'free_flow_time': 6,
                    'congestion_func': bpr_function_factory(90)
                },
                {
                    'id': 'A_C',
                    'start': 'A',
                    'end': 'C',
                    'capacity': 100,
                    'free_flow_time': 10,
                    'congestion_func': bpr_function_factory(100)
                },
                {
                    'id': 'C_D',
                    'start': 'C',
                    'end': 'D',
                    'capacity': 110,
                    'free_flow_time': 8,
                    'congestion_func': bpr_function_factory(110)
                },
                {
                    'id': 'B_D',
                    'start': 'B',
                    'end': 'D',
                    'capacity': 130,
                    'free_flow_time': 9,
                    'congestion_func': bpr_function_factory(130)
                }
            ]
        }
        od_pairs = [
            {
                'origin': 'A',
                'destination': 'D',
                'demand': 150
            },
            {
                'origin': 'B',
                'destination': 'D',
                'demand': 80
            }
        ]
        T = 6
        max_toll = 20

        toll_matrix = optimize_tolls(graph, od_pairs, T, max_toll)

        # Check toll matrix dimensions and value properties
        self.assertIsInstance(toll_matrix, list)
        self.assertEqual(len(toll_matrix), T)
        for row in toll_matrix:
            self.assertIsInstance(row, list)
            self.assertEqual(len(row), len(graph['edges']))
            for toll in row:
                self.assertIsInstance(toll, int)
                self.assertGreaterEqual(toll, 0)
                self.assertLessEqual(toll, max_toll)

if __name__ == '__main__':
    unittest.main()