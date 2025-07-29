import unittest
from network_optimize import optimize_network_flow

class TestNetworkOptimize(unittest.TestCase):
    def setUp(self):
        # Basic test graph
        self.basic_graph = {
            "A": {"B": {"capacity": 10, "latency": 5}, "C": {"capacity": 15, "latency": 10}},
            "B": {"D": {"capacity": 20, "latency": 3}},
            "C": {"D": {"capacity": 8, "latency": 7}},
            "D": {}
        }
        
        self.basic_server_properties = {
            "A": {"load": 0, "max_load": 20, "content_availability": {"video1": False, "image2": True}},
            "B": {"load": 0, "max_load": 15, "content_availability": {"video1": True, "image2": False}},
            "C": {"load": 0, "max_load": 10, "content_availability": {"video1": True, "image2": True}},
            "D": {"load": 0, "max_load": 25, "content_availability": {"video1": True, "image2": True}}
        }

    def test_basic_routing(self):
        requests = [
            {"content_id": "video1", "source_location": "A", "destination_location": "D", "size": 5},
            {"content_id": "image2", "source_location": "B", "destination_location": "D", "size": 3}
        ]
        result = optimize_network_flow(self.basic_graph, requests, self.basic_server_properties)
        self.assertEqual(len(result), 2)  # Should return paths for both requests
        self.assertTrue(all(isinstance(path, list) for path in result))  # All paths should be lists

    def test_bandwidth_constraint(self):
        # Test when bandwidth is insufficient
        limited_graph = {
            "A": {"B": {"capacity": 2, "latency": 5}},
            "B": {"C": {"capacity": 2, "latency": 3}},
            "C": {}
        }
        limited_properties = {
            "A": {"load": 0, "max_load": 20, "content_availability": {"video1": True}},
            "B": {"load": 0, "max_load": 20, "content_availability": {"video1": True}},
            "C": {"load": 0, "max_load": 20, "content_availability": {"video1": True}}
        }
        requests = [
            {"content_id": "video1", "source_location": "A", "destination_location": "C", "size": 3}
        ]
        result = optimize_network_flow(limited_graph, requests, limited_properties)
        self.assertEqual(result, [[]])  # Should return empty path due to insufficient bandwidth

    def test_server_load_constraint(self):
        # Test when server load exceeds maximum
        heavy_load_properties = self.basic_server_properties.copy()
        heavy_load_properties["D"]["max_load"] = 2  # Set very low max load
        requests = [
            {"content_id": "video1", "source_location": "A", "destination_location": "D", "size": 5}
        ]
        result = optimize_network_flow(self.basic_graph, requests, heavy_load_properties)
        self.assertEqual(result, [[]])  # Should return empty path due to server load constraint

    def test_content_availability(self):
        # Test when content is not available
        requests = [
            {"content_id": "nonexistent_content", "source_location": "A", "destination_location": "D", "size": 1}
        ]
        result = optimize_network_flow(self.basic_graph, requests, self.basic_server_properties)
        self.assertEqual(result, [[]])  # Should return empty path due to content unavailability

    def test_disconnected_graph(self):
        # Test with disconnected graph
        disconnected_graph = {
            "A": {"B": {"capacity": 10, "latency": 5}},
            "C": {"D": {"capacity": 10, "latency": 5}},
            "B": {},
            "D": {}
        }
        requests = [
            {"content_id": "video1", "source_location": "A", "destination_location": "D", "size": 1}
        ]
        result = optimize_network_flow(disconnected_graph, requests, self.basic_server_properties)
        self.assertEqual(result, [[]])  # Should return empty path for disconnected nodes

    def test_multiple_valid_paths(self):
        # Test when multiple paths are possible
        requests = [
            {"content_id": "video1", "source_location": "A", "destination_location": "D", "size": 1}
        ]
        result = optimize_network_flow(self.basic_graph, requests, self.basic_server_properties)
        self.assertEqual(len(result), 1)
        self.assertTrue(len(result[0]) >= 2)  # Path should have at least source and destination

    def test_empty_requests(self):
        result = optimize_network_flow(self.basic_graph, [], self.basic_server_properties)
        self.assertEqual(result, [])  # Should return empty list for no requests

    def test_single_node_path(self):
        # Test when source and destination are the same
        requests = [
            {"content_id": "video1", "source_location": "D", "destination_location": "D", "size": 1}
        ]
        result = optimize_network_flow(self.basic_graph, requests, self.basic_server_properties)
        self.assertEqual(len(result), 1)
        self.assertEqual(len(result[0]), 1)  # Path should contain only one node

    def test_large_scale(self):
        # Generate a larger graph for performance testing
        large_graph = {}
        large_properties = {}
        for i in range(100):
            node = f"node{i}"
            large_graph[node] = {}
            large_properties[node] = {
                "load": 0,
                "max_load": 100,
                "content_availability": {"test_content": True}
            }
            if i > 0:
                large_graph[f"node{i-1}"][node] = {"capacity": 100, "latency": 1}

        large_requests = [
            {"content_id": "test_content", "source_location": "node0", 
             "destination_location": f"node{99}", "size": 1}
        ]
        
        result = optimize_network_flow(large_graph, large_requests, large_properties)
        self.assertEqual(len(result), 1)
        self.assertTrue(len(result[0]) > 0)

if __name__ == '__main__':
    unittest.main()