import unittest
from network_connect import min_connections_needed

class NetworkConnectTest(unittest.TestCase):
    def test_already_strongly_connected(self):
        servers = ["A", "B", "C"]
        connections = [("A", "B"), ("B", "C"), ("C", "A")]
        self.assertEqual(min_connections_needed(servers, connections), 0)

    def test_already_strongly_connected_bidirectional(self):
        servers = ["A", "B", "C"]
        connections = [("A", "B"), ("B", "A"), ("B", "C"), ("C", "B"), ("A", "C"), ("C", "A")]
        self.assertEqual(min_connections_needed(servers, connections), 0)

    def test_single_server(self):
        servers = ["A"]
        connections = []
        self.assertEqual(min_connections_needed(servers, connections), 0)

    def test_single_server_with_self_loop(self):
        servers = ["A"]
        connections = [("A", "A")]
        self.assertEqual(min_connections_needed(servers, connections), 0)

    def test_empty_network(self):
        servers = []
        connections = []
        self.assertEqual(min_connections_needed(servers, connections), 0)

    def test_no_connections(self):
        servers = ["A", "B", "C"]
        connections = []
        self.assertEqual(min_connections_needed(servers, connections), 2)

    def test_linear_path_needs_one_connection(self):
        servers = ["A", "B", "C"]
        connections = [("A", "B"), ("B", "C")]
        self.assertEqual(min_connections_needed(servers, connections), 1)

    def test_basic_example_multiple_connections_needed(self):
        servers = ["A", "B", "C", "D"]
        connections = [("A", "B"), ("B", "C")]
        self.assertEqual(min_connections_needed(servers, connections), 2)
    
    def test_larger_example(self):
        servers = ["A", "B", "C", "D", "E"]
        connections = [("A", "B"), ("B", "C"), ("D", "E")]
        self.assertEqual(min_connections_needed(servers, connections), 2)
    
    def test_two_disconnected_components(self):
        servers = ["A", "B", "C", "D", "E", "F"]
        connections = [("A", "B"), ("B", "C"), ("C", "A"), ("D", "E"), ("E", "F"), ("F", "D")]
        self.assertEqual(min_connections_needed(servers, connections), 2)

    def test_three_disconnected_components(self):
        servers = ["A", "B", "C", "D", "E", "F", "G", "H"]
        connections = [
            ("A", "B"), ("B", "A"),
            ("C", "D"), ("D", "C"),
            ("E", "F"), ("F", "G"), ("G", "E"),
            ("H", "H")
        ]
        self.assertEqual(min_connections_needed(servers, connections), 4)

    def test_duplicate_connections(self):
        servers = ["A", "B", "C"]
        connections = [("A", "B"), ("A", "B"), ("B", "C")]
        self.assertEqual(min_connections_needed(servers, connections), 1)

    def test_self_loops_ignored(self):
        servers = ["A", "B", "C"]
        connections = [("A", "A"), ("A", "B"), ("B", "C"), ("C", "C")]
        self.assertEqual(min_connections_needed(servers, connections), 1)

    def test_invalid_server_in_connections(self):
        servers = ["A", "B", "C"]
        connections = [("A", "B"), ("B", "D")]
        with self.assertRaises(ValueError):
            min_connections_needed(servers, connections)

    def test_large_network(self):
        # Create a large network with 100 servers in a chain
        servers = [str(i) for i in range(100)]
        connections = [(str(i), str(i+1)) for i in range(99)]
        self.assertEqual(min_connections_needed(servers, connections), 1)
    
    def test_complex_network(self):
        servers = ["A", "B", "C", "D", "E", "F"]
        connections = [
            ("A", "B"), ("B", "C"), ("C", "D"), 
            ("D", "B"), ("E", "F"), ("F", "E")
        ]
        self.assertEqual(min_connections_needed(servers, connections), 2)
        
    def test_complex_network_with_cycles(self):
        servers = ["A", "B", "C", "D", "E", "F"]
        connections = [
            ("A", "B"), ("B", "C"), ("C", "A"),
            ("D", "E"), ("E", "F"), ("F", "D"),
            ("B", "D")
        ]
        self.assertEqual(min_connections_needed(servers, connections), 1)

if __name__ == "__main__":
    unittest.main()