import unittest
from dynamic_router import dynamic_router

class TestDynamicRouter(unittest.TestCase):
    def test_example(self):
        # Test based on the provided example with dynamic updates.
        N = 4
        initial_links = [
            (0, 1, 5),
            (0, 2, 10),
            (1, 3, 2),
            (2, 3, 7)
        ]
        operations = [
            ({0, 1}, 3),   # Query: from sources {0,1} to destination 3.
                           # Expected shortest latency:
                           #   From node 0: path 0->1->3 = 5 + 2 = 7.
                           #   From node 1: direct path 1->3 = 2.
                           # Minimum latency = 2.
            (1, 3, 1),    # Update: Change latency on link (1, 3) to 1.
            ({0}, 3),     # Query: from source {0} to destination 3.
                           # Expected path: 0->1->3 = 5 + 1 = 6.
            (0, 2, 12),   # Update: Change latency on link (0, 2) to 12.
            ({2, 3}, 1)   # Query: from sources {2, 3} to destination 1.
                           # Expected:
                           #   For node 2: possible paths: 2->0->1 = 12 + 5 = 17; 2->3->1 = 7 + 1 = 8.
                           #   For node 3: direct path 3->1 = 1.
                           # Minimum latency = 1.
        ]
        expected = [2, 6, 1]
        result = dynamic_router(N, initial_links, operations)
        self.assertEqual(result, expected)

    def test_disconnected(self):
        # Test when some nodes are disconnected.
        N = 3
        initial_links = [
            (0, 1, 4)
        ]
        operations = [
            ({0, 2}, 1),  # Query: from sources {0,2} to destination 1.
                           # Node 0 connects to 1 with latency 4.
                           # Node 2 is disconnected.
                           # Expected latency = 4.
            ({1}, 2)      # Query: from source {1} to destination 2.
                           # There is no path from node 1 to node 2.
                           # Expected latency = -1.
        ]
        expected = [4, -1]
        result = dynamic_router(N, initial_links, operations)
        self.assertEqual(result, expected)

    def test_multiple_updates(self):
        # Test with multiple updates in a larger network.
        N = 5
        initial_links = [
            (0, 1, 10),
            (1, 2, 10),
            (2, 3, 10),
            (3, 4, 10)
        ]
        operations = [
            ({0, 4}, 3),   # Query: from sources {0,4} to destination 3.
                            # From node 0: 0->1->2->3 = 10+10+10 = 30.
                            # From node 4: direct link 4->3 = 10.
                            # Expected latency = 10.
            (0, 4, 1),     # Update: Change/add link (0,4) to latency 1.
                            # Being undirected, link (4,0) is also updated.
            ({0}, 3),      # Query: from source {0} to destination 3.
                            # New potential path: 0->4->3 = 1+10 = 11.
                            # Other path: 0->1->2->3 = 10+10+10 = 30.
                            # Expected latency = 11.
            (1, 2, 1),     # Update: Change latency on link (1,2) to 1.
            ({0}, 3),      # Query: from source {0} to destination 3.
                            # Now: 0->1->2->3 = 10+1+10 = 21; 0->4->3 remains 11.
                            # Expected latency = 11.
            (0, 1, 1),     # Update: Change latency on link (0,1) to 1.
            ({0}, 3)       # Query: from source {0} to destination 3.
                            # Now: 0->1->2->3 = 1+1+10 = 12; 0->4->3 = 1+10 = 11.
                            # Expected latency remains 11.
        ]
        expected = [10, 11, 11, 11]
        result = dynamic_router(N, initial_links, operations)
        self.assertEqual(result, expected)

    def test_no_queries(self):
        # Test scenario where operations include only update operations.
        N = 4
        initial_links = [
            (0, 1, 3),
            (1, 2, 4),
            (2, 3, 5)
        ]
        operations = [
            (0, 1, 2),
            (1, 2, 2),
            (2, 3, 2)
        ]
        # Since there are no query operations, the expected result is an empty list.
        expected = []
        result = dynamic_router(N, initial_links, operations)
        self.assertEqual(result, expected)

if __name__ == '__main__':
    unittest.main()