import unittest
from k_hop_network import find_k_hop_neighborhood

class MockGraphAPI:
    def __init__(self, graph_data):
        self.graph_data = graph_data
        self.call_count = 0
        
    def get_neighbors(self, user_id):
        self.call_count += 1
        return self.graph_data.get(user_id, [])

class KHopNetworkTest(unittest.TestCase):
    def setUp(self):
        # Reset for each test
        self.MAX_API_CALLS = 100
        
    def test_simple_graph(self):
        graph = {
            1: [2, 3],
            2: [1, 4, 5],
            3: [1, 6],
            4: [2],
            5: [2],
            6: [3]
        }
        api = MockGraphAPI(graph)
        result = find_k_hop_neighborhood(1, 2, api.get_neighbors, self.MAX_API_CALLS)
        self.assertEqual(result, [2, 3, 4, 5, 6])
        self.assertLessEqual(api.call_count, self.MAX_API_CALLS)

    def test_empty_graph(self):
        api = MockGraphAPI({})
        result = find_k_hop_neighborhood(1, 2, api.get_neighbors, self.MAX_API_CALLS)
        self.assertEqual(result, [])
        self.assertLessEqual(api.call_count, self.MAX_API_CALLS)

    def test_single_node(self):
        graph = {1: []}
        api = MockGraphAPI(graph)
        result = find_k_hop_neighborhood(1, 1, api.get_neighbors, self.MAX_API_CALLS)
        self.assertEqual(result, [])
        self.assertLessEqual(api.call_count, self.MAX_API_CALLS)

    def test_linear_graph(self):
        graph = {
            1: [2],
            2: [1, 3],
            3: [2, 4],
            4: [3, 5],
            5: [4]
        }
        api = MockGraphAPI(graph)
        result = find_k_hop_neighborhood(1, 3, api.get_neighbors, self.MAX_API_CALLS)
        self.assertEqual(result, [2, 3, 4])
        self.assertLessEqual(api.call_count, self.MAX_API_CALLS)

    def test_cyclic_graph(self):
        graph = {
            1: [2, 5],
            2: [1, 3],
            3: [2, 4],
            4: [3, 5],
            5: [1, 4]
        }
        api = MockGraphAPI(graph)
        result = find_k_hop_neighborhood(1, 2, api.get_neighbors, self.MAX_API_CALLS)
        self.assertEqual(result, [2, 3, 4, 5])
        self.assertLessEqual(api.call_count, self.MAX_API_CALLS)

    def test_disconnected_components(self):
        graph = {
            1: [2, 3],
            2: [1],
            3: [1],
            4: [5],
            5: [4]
        }
        api = MockGraphAPI(graph)
        result = find_k_hop_neighborhood(1, 5, api.get_neighbors, self.MAX_API_CALLS)
        self.assertEqual(result, [2, 3])
        self.assertLessEqual(api.call_count, self.MAX_API_CALLS)

    def test_large_k(self):
        graph = {
            1: [2],
            2: [1, 3],
            3: [2]
        }
        api = MockGraphAPI(graph)
        result = find_k_hop_neighborhood(1, 10, api.get_neighbors, self.MAX_API_CALLS)
        self.assertEqual(result, [2, 3])
        self.assertLessEqual(api.call_count, self.MAX_API_CALLS)

    def test_dense_graph(self):
        # Create a complete graph with 10 nodes
        graph = {i: [j for j in range(1, 11) if j != i] for i in range(1, 11)}
        api = MockGraphAPI(graph)
        result = find_k_hop_neighborhood(1, 1, api.get_neighbors, self.MAX_API_CALLS)
        expected = list(range(2, 11))
        self.assertEqual(result, expected)
        self.assertLessEqual(api.call_count, self.MAX_API_CALLS)

    def test_exceeds_max_api_calls(self):
        # Create a graph that would require many API calls
        graph = {i: [i+1] for i in range(1, 1001)}
        api = MockGraphAPI(graph)
        with self.assertRaises(Exception):
            find_k_hop_neighborhood(1, 999, api.get_neighbors, 10)

    def test_duplicate_paths(self):
        graph = {
            1: [2, 3],
            2: [1, 3, 4],
            3: [1, 2, 4],
            4: [2, 3]
        }
        api = MockGraphAPI(graph)
        result = find_k_hop_neighborhood(1, 2, api.get_neighbors, self.MAX_API_CALLS)
        self.assertEqual(result, [2, 3, 4])
        self.assertLessEqual(api.call_count, self.MAX_API_CALLS)

if __name__ == '__main__':
    unittest.main()