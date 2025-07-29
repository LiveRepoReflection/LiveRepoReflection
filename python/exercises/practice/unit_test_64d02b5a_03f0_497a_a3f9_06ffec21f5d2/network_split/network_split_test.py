import unittest
from network_split import split_network

def compute_density(subnet, edges):
    # Calculate the number of edges that exist within the subnet
    edge_count = 0
    for u, v in edges:
        if u in subnet and v in subnet:
            edge_count += 1
    n = len(subnet)
    if n <= 1:
        # For 0 or 1 node, define density as 1.0 (maximally dense by definition)
        return 1.0
    max_edges = n * (n - 1) / 2
    return edge_count / max_edges

def validate_partition(partitions, N, edges, D, M):
    # Check that every router appears exactly once in exactly one partition
    all_nodes = set()
    for subnet in partitions:
        all_nodes.update(subnet)
    if all_nodes != set(range(N)):
        return False, "Some routers are missing or duplicated in the partitions."
    
    # Check each sub-network's constraints
    for subnet in partitions:
        if len(subnet) > M:
            return False, f"Sub-network {subnet} exceeds maximum allowed size {M}."
        density = compute_density(subnet, edges)
        if density < D:
            return False, f"Sub-network {subnet} has density {density} which is below the threshold {D}."
    return True, ""

class TestNetworkSplit(unittest.TestCase):

    def test_single_router(self):
        # Minimal case: one router, no edges, no critical routers.
        N = 1
        edges = []
        C = set()
        D = 0
        M = 1
        partitions = split_network(N, edges, C, D, M)
        valid, msg = validate_partition(partitions, N, edges, D, M)
        self.assertTrue(valid, msg)

    def test_triangle_network(self):
        # Three routers fully connected forming a triangle.
        N = 3
        edges = [(0, 1), (1, 2), (0, 2)]
        C = {0}  # One critical router; should not affect partitioning drastically.
        D = 0.5
        M = 3
        partitions = split_network(N, edges, C, D, M)
        valid, msg = validate_partition(partitions, N, edges, D, M)
        self.assertTrue(valid, msg)

    def test_provided_example(self):
        # Provided example input from the problem description.
        N = 6
        edges = [(0, 1), (0, 2), (1, 2), (3, 4), (4, 5)]
        C = {0, 3, 5}
        D = 0.4
        M = 4
        partitions = split_network(N, edges, C, D, M)
        valid, msg = validate_partition(partitions, N, edges, D, M)
        self.assertTrue(valid, msg)
    
    def test_linear_chain(self):
        # A linear chain of routers: 0-1-2-3-4 with critical routers at both ends.
        N = 5
        edges = [(0, 1), (1, 2), (2, 3), (3, 4)]
        C = {0, 4}
        D = 0.3
        M = 3
        partitions = split_network(N, edges, C, D, M)
        valid, msg = validate_partition(partitions, N, edges, D, M)
        self.assertTrue(valid, msg)

    def test_dense_cluster(self):
        # Fully connected 4-node clique. With high density requirement, it should remain intact if allowed.
        N = 4
        edges = [(0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3)]
        C = {1, 2}
        D = 0.9
        M = 4
        partitions = split_network(N, edges, C, D, M)
        valid, msg = validate_partition(partitions, N, edges, D, M)
        self.assertTrue(valid, msg)
    
    def test_mandatory_split_due_to_size(self):
        # A graph that forces the algorithm to split because M (max size) constraint is tight.
        N = 7
        edges = [(0, 1), (0, 2), (1, 2), (2, 3), (3, 4), (4, 5), (4, 6), (5, 6)]
        C = {2, 4}
        D = 0.3
        M = 3
        partitions = split_network(N, edges, C, D, M)
        valid, msg = validate_partition(partitions, N, edges, D, M)
        self.assertTrue(valid, msg)
    
    def test_multiple_critical_nodes(self):
        # A more intricate graph to test distribution of critical routers.
        N = 8
        edges = [(0, 1), (1, 2), (2, 3), (3, 0), 
                 (4, 5), (5, 6), (6, 7), (7, 4),
                 (2, 5)]
        C = {0, 2, 4, 6}
        D = 0.5
        M = 4
        partitions = split_network(N, edges, C, D, M)
        valid, msg = validate_partition(partitions, N, edges, D, M)
        self.assertTrue(valid, msg)

if __name__ == '__main__':
    unittest.main()