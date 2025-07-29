import unittest
from data_aggregator import DataAggregator

class TestDataAggregator(unittest.TestCase):
    def setUp(self):
        # Sample tree structure for testing
        self.tree = {
            'root': {
                'children': ['node1', 'node2'],
                'data': []
            },
            'node1': {
                'children': ['leaf1', 'leaf2'],
                'data': []
            },
            'node2': {
                'children': ['leaf3'],
                'data': []
            },
            'leaf1': {
                'children': [],
                'data': [1.0, 2.0, 3.0]
            },
            'leaf2': {
                'children': [],
                'data': [4.0, 5.0, 6.0]
            },
            'leaf3': {
                'children': [],
                'data': [7.0, 8.0, 9.0]
            }
        }
        self.aggregator = DataAggregator(self.tree)

    def test_basic_queries(self):
        # Test basic aggregation queries
        self.assertEqual(self.aggregator.query('leaf1', 'min'), 1.0)
        self.assertEqual(self.aggregator.query('leaf1', 'max'), 3.0)
        self.assertEqual(self.aggregator.query('leaf1', 'sum'), 6.0)
        self.assertEqual(self.aggregator.query('leaf1', 'average'), 2.0)

    def test_intermediate_node_queries(self):
        # Test queries on intermediate nodes
        self.assertEqual(self.aggregator.query('node1', 'min'), 1.0)
        self.assertEqual(self.aggregator.query('node1', 'max'), 6.0)
        self.assertEqual(self.aggregator.query('node1', 'sum'), 21.0)
        self.assertEqual(self.aggregator.query('node1', 'average'), 3.5)

    def test_root_queries(self):
        # Test queries on root node
        self.assertEqual(self.aggregator.query('root', 'min'), 1.0)
        self.assertEqual(self.aggregator.query('root', 'max'), 9.0)
        self.assertEqual(self.aggregator.query('root', 'sum'), 45.0)
        self.assertEqual(self.aggregator.query('root', 'average'), 5.0)

    def test_empty_node(self):
        # Test queries on empty nodes
        empty_tree = {
            'empty': {
                'children': [],
                'data': []
            }
        }
        aggregator = DataAggregator(empty_tree)
        with self.assertRaises(ValueError):
            aggregator.query('empty', 'min')

    def test_invalid_node(self):
        # Test queries on non-existent nodes
        with self.assertRaises(KeyError):
            self.aggregator.query('nonexistent', 'min')

    def test_invalid_statistic(self):
        # Test queries with invalid statistics
        with self.assertRaises(ValueError):
            self.aggregator.query('root', 'invalid_stat')

    def test_large_tree(self):
        # Test with a larger tree
        large_tree = {'root': {'children': [], 'data': []}}
        for i in range(1000):
            node_id = f'node_{i}'
            large_tree[node_id] = {
                'children': [],
                'data': [float(i)] * 100
            }
            large_tree['root']['children'].append(node_id)

        aggregator = DataAggregator(large_tree)
        self.assertEqual(aggregator.query('root', 'min'), 0.0)
        self.assertEqual(aggregator.query('root', 'max'), 999.0)

    def test_floating_point_precision(self):
        # Test floating point precision handling
        precision_tree = {
            'root': {
                'children': ['leaf1', 'leaf2'],
                'data': []
            },
            'leaf1': {
                'children': [],
                'data': [0.1, 0.2, 0.3]
            },
            'leaf2': {
                'children': [],
                'data': [0.4, 0.5, 0.6]
            }
        }
        aggregator = DataAggregator(precision_tree)
        self.assertAlmostEqual(aggregator.query('root', 'sum'), 2.1)
        self.assertAlmostEqual(aggregator.query('root', 'average'), 0.35)

    def test_data_updates(self):
        # Test handling of data updates
        self.tree['leaf1']['data'].append(10.0)
        self.assertEqual(self.aggregator.query('leaf1', 'max'), 10.0)
        self.assertEqual(self.aggregator.query('root', 'max'), 10.0)

if __name__ == '__main__':
    unittest.main()