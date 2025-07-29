import unittest
from node_allocator import allocate_nodes

class NodeAllocatorTest(unittest.TestCase):
    def test_empty_request(self):
        # When job_request is all zeros, no nodes should be required.
        N = 3
        M = 2
        node_resources = [
            [5, 3],
            [2, 4],
            [3, 1]
        ]
        job_request = [0, 0]
        self.assertEqual(allocate_nodes(node_resources, job_request), 0)

    def test_single_node_sufficient(self):
        # One node exactly satisfies the request.
        node_resources = [
            [7, 5],
            [2, 4],
            [3, 1]
        ]
        job_request = [7, 5]
        self.assertEqual(allocate_nodes(node_resources, job_request), 1)

    def test_multiple_nodes_required(self):
        # Multiple nodes required to satisfy the job_request.
        # For instance, combining two nodes to meet both resource requirements.
        node_resources = [
            [5, 3],
            [2, 4],
            [3, 1]
        ]
        # 5+2 >= 7 and 3+4 >= 7, so minimum required nodes are 2.
        job_request = [7, 7]
        self.assertEqual(allocate_nodes(node_resources, job_request), 2)

    def test_insufficient_resources(self):
        # The overall available resources are insufficient.
        node_resources = [
            [5, 3],
            [2, 4],
            [3, 1]
        ]
        job_request = [11, 5]  # Total of first type is 10 which is less than 11.
        self.assertEqual(allocate_nodes(node_resources, job_request), -1)

    def test_multiple_valid_combinations(self):
        # More than one combination might satisfy job_request.
        # The algorithm must find the combination with minimum nodes.
        node_resources = [
            [4, 2],
            [3, 3],
            [2, 2],
            [5, 1]
        ]
        # Possibility: nodes 0 and 1 together provide [7, 5], nodes 3 and 2 potentially provide [7, 3] which is not enough.
        # The minimal pair is nodes [0,1] or any valid combination that sums to at least [7,5].
        job_request = [7, 5]
        self.assertEqual(allocate_nodes(node_resources, job_request), 2)

    def test_large_input_complexity(self):
        # Test with a larger number of nodes and resource types.
        # This is a performance and correctness test.
        N = 50
        M = 3
        # Create 50 nodes; each node has increasing resources.
        node_resources = [[i % 10 + 1, (i*2) % 10 + 1, (i*3) % 10 + 1] for i in range(1, N+1)]
        # Set a job_request that can only be satisfied by at least 5 nodes in some combination.
        job_request = [30, 30, 30]
        result = allocate_nodes(node_resources, job_request)
        # The expected minimal count is not immediately trivial,
        # We check that the result is not -1 and is between 1 and N.
        self.assertTrue(1 <= result <= N)
        # Additionally, recalc the total provided by all nodes to ensure feasibility.
        total_resources = [sum(node[i] for node in node_resources) for i in range(M)]
        for req, tot in zip(job_request, total_resources):
            self.assertTrue(tot >= req, "Overall resources should be sufficient")
    
if __name__ == "__main__":
    unittest.main()