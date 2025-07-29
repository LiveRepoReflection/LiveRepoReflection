import unittest
from optimal_placement import allocate_files

def manhattan_distance(p1, p2):
    return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])

class TestOptimalPlacement(unittest.TestCase):
    def verify_constraints(self, allocation, node_capacities, node_locations, file_sizes, replication_factor):
        N = len(node_capacities)
        M = len(file_sizes)
        
        # Check that allocation is a list of length M
        self.assertEqual(len(allocation), M, "Allocation must have an entry for each file.")
        
        # Initialize storage usage per node
        storage_usage = [0] * N

        for i, nodes in enumerate(allocation):
            # Check that each file is allocated to replication_factor nodes
            self.assertEqual(len(nodes), replication_factor,
                             f"File {i} must be allocated to {replication_factor} nodes.")
            # Check that each node index is valid and update storage usage.
            seen_nodes = set()
            for node in nodes:
                self.assertIsInstance(node, int, "Node indices must be integers.")
                self.assertGreaterEqual(node, 0, "Node index must be non-negative.")
                self.assertLess(node, N, "Node index out of valid range.")
                # Ensure a file is not replicated twice on the same node.
                self.assertNotIn(node, seen_nodes,
                                 f"File {i} has duplicate replica on node {node}.")
                seen_nodes.add(node)
                storage_usage[node] += file_sizes[i]

        # Check that node capacities are not exceeded.
        for node, usage in enumerate(storage_usage):
            self.assertLessEqual(usage, node_capacities[node],
                f"Node {node} exceeds its capacity: used {usage}, capacity {node_capacities[node]}.")

    def test_small_scenario(self):
        # Define a small scenario with 3 nodes and 2 files.
        N = 3
        M = 2
        replication_factor = 1
        node_capacities = [10, 10, 10]
        node_locations = [(0, 0), (2, 2), (5, 5)]
        file_sizes = [5, 5]
        file_popularities = [100, 50]
        client_location = (0, 0)
        
        allocation = allocate_files(
            N, M, replication_factor,
            node_capacities, node_locations,
            file_sizes, file_popularities,
            client_location
        )
        
        # Verify allocation meets capacity and replication constraints.
        self.verify_constraints(allocation, node_capacities, node_locations, file_sizes, replication_factor)

        # For verification of latency, compute the weighted average distance.
        total_weighted_latency = 0
        for i, nodes in enumerate(allocation):
            distances = [manhattan_distance(client_location, node_locations[node]) for node in nodes]
            avg_distance = sum(distances) / len(distances)
            total_weighted_latency += file_popularities[i] * avg_distance
        
        # In this simple test, we ensure non-negative total weighted latency.
        self.assertGreaterEqual(total_weighted_latency, 0)

    def test_complex_scenario(self):
        # Define a more complex scenario with 5 nodes and 4 files.
        N = 5
        M = 4
        replication_factor = 2
        node_capacities = [15, 10, 20, 10, 15]
        node_locations = [(0, 0), (1, 3), (4, 4), (7, 1), (3, 5)]
        file_sizes = [5, 7, 4, 6]
        file_popularities = [80, 120, 60, 90]
        client_location = (2, 2)
        
        allocation = allocate_files(
            N, M, replication_factor,
            node_capacities, node_locations,
            file_sizes, file_popularities,
            client_location
        )
        
        self.verify_constraints(allocation, node_capacities, node_locations, file_sizes, replication_factor)
        
        # Verify that for each file, the average distance to the client is calculated and is non-negative.
        for i, nodes in enumerate(allocation):
            distances = [manhattan_distance(client_location, node_locations[node]) for node in nodes]
            avg_distance = sum(distances) / len(distances)
            self.assertGreaterEqual(avg_distance, 0)

    def test_edge_case_no_capacity(self):
        # Test where one of the nodes has zero capacity.
        N = 3
        M = 2
        replication_factor = 1
        node_capacities = [0, 10, 10]
        node_locations = [(0, 0), (2, 2), (4, 4)]
        file_sizes = [5, 5]
        file_popularities = [100, 50]
        client_location = (0, 0)
        
        allocation = allocate_files(
            N, M, replication_factor,
            node_capacities, node_locations,
            file_sizes, file_popularities,
            client_location
        )
        
        self.verify_constraints(allocation, node_capacities, node_locations, file_sizes, replication_factor)
        
    def test_high_replication(self):
        # Test scenario where replication factor is greater than 1 and nearly all nodes are used.
        N = 4
        M = 3
        replication_factor = 3
        node_capacities = [10, 10, 10, 10]
        node_locations = [(0, 0), (1, 1), (2, 2), (3, 3)]
        file_sizes = [3, 3, 3]
        file_popularities = [50, 70, 30]
        client_location = (0, 0)
        
        allocation = allocate_files(
            N, M, replication_factor,
            node_capacities, node_locations,
            file_sizes, file_popularities,
            client_location
        )
        
        self.verify_constraints(allocation, node_capacities, node_locations, file_sizes, replication_factor)

if __name__ == '__main__':
    unittest.main()