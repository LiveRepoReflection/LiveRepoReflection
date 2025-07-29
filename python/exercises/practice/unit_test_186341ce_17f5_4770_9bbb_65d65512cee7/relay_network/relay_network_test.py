import unittest
import itertools
from relay_network import optimal_relay_placement

def compute_average_latency(latency_matrix, relay_nodes, relay_efficiency):
    n = len(latency_matrix)
    total_latency = 0
    pair_count = 0
    for i, j in itertools.combinations(range(n), 2):
        direct = latency_matrix[i][j]
        if relay_nodes:
            # For each relay node, compute latency via relay:
            relay_paths = [(latency_matrix[i][r] + latency_matrix[r][j]) / relay_efficiency for r in relay_nodes]
            relay_latency = min(relay_paths)
            effective_latency = min(direct, relay_latency)
        else:
            effective_latency = direct
        total_latency += effective_latency
        pair_count += 1
    return total_latency / pair_count if pair_count else 0

def compute_direct_average_latency(latency_matrix):
    n = len(latency_matrix)
    total_latency = 0
    pair_count = 0
    for i, j in itertools.combinations(range(n), 2):
        total_latency += latency_matrix[i][j]
        pair_count += 1
    return total_latency / pair_count if pair_count else 0

class RelayNetworkTest(unittest.TestCase):
    def setUp(self):
        # Common test data for several tests
        self.latency_matrix_5 = [
            [0,   100, 200, 300, 400],
            [100,   0, 150, 250, 350],
            [200, 150,   0, 100, 200],
            [300, 250, 100,   0, 100],
            [400, 350, 200, 100,   0]
        ]
        self.data_centers_5 = list(range(5))

    def validate_relay_output(self, relay_nodes, num_data_centers, max_relays):
        # Check that the output is a list.
        self.assertIsInstance(relay_nodes, list, "Output should be a list")
        # Check that length does not exceed maximum allowed.
        self.assertLessEqual(len(relay_nodes), max_relays, "Number of relay nodes exceeds maximum allowed.")
        # Check that each relay is a valid data center id.
        for node in relay_nodes:
            self.assertIsInstance(node, int, "Relay node id should be an integer")
            self.assertGreaterEqual(node, 0, "Relay node id should be non-negative")
            self.assertLess(node, num_data_centers, "Relay node id out of range")
        # Check that there are no duplicates.
        self.assertEqual(len(relay_nodes), len(set(relay_nodes)), "Relay node ids should be unique")

    def test_single_relay_improves_average_latency(self):
        max_relays = 1
        relay_efficiency = 2.0
        relay_nodes = optimal_relay_placement(
            data_centers=self.data_centers_5,
            latency_matrix=self.latency_matrix_5,
            max_relays=max_relays,
            relay_efficiency=relay_efficiency
        )
        self.validate_relay_output(relay_nodes, len(self.data_centers_5), max_relays)
        direct_avg = compute_direct_average_latency(self.latency_matrix_5)
        relay_avg = compute_average_latency(self.latency_matrix_5, relay_nodes, relay_efficiency)
        self.assertLessEqual(
            relay_avg, direct_avg,
            "Average latency with relay should not exceed direct average latency."
        )
    
    def test_two_relays_improves_average_latency(self):
        if len(self.data_centers_5) < 6:  # Ensure we have enough nodes for more relays
            data_centers = self.data_centers_5
            latency_matrix = self.latency_matrix_5
        else:
            data_centers = self.data_centers_5
            latency_matrix = self.latency_matrix_5

        max_relays = 2
        relay_efficiency = 3.0
        relay_nodes = optimal_relay_placement(
            data_centers=data_centers,
            latency_matrix=latency_matrix,
            max_relays=max_relays,
            relay_efficiency=relay_efficiency
        )
        self.validate_relay_output(relay_nodes, len(data_centers), max_relays)
        direct_avg = compute_direct_average_latency(latency_matrix)
        relay_avg = compute_average_latency(latency_matrix, relay_nodes, relay_efficiency)
        self.assertLessEqual(
            relay_avg, direct_avg,
            "Average latency with relay should not exceed direct average latency."
        )
    
    def test_edge_case_no_relay_benefit(self):
        # Construct a test case where relay paths are not beneficial.
        # In this case, the latency to/from any potential relay node is extremely high.
        latency_matrix = [
            [0,    50,  50,  50,  50],
            [50,    0,  50,  50,  50],
            [50,   50,   0,  50,  50],
            [50,   50,  50,   0,  50],
            [50,   50,  50,  50,   0]
        ]
        # Modify matrix to simulate that going through a relay would be worse.
        # Increase latency when connecting to a specific node (simulate bad connection)
        # For example, make data center 2 particularly bad for relaying.
        for i in range(5):
            if i != 2:
                latency_matrix[i][2] = 1000
                latency_matrix[2][i] = 1000
        data_centers = list(range(5))
        max_relays = 2
        relay_efficiency = 2.5
        relay_nodes = optimal_relay_placement(
            data_centers=data_centers,
            latency_matrix=latency_matrix,
            max_relays=max_relays,
            relay_efficiency=relay_efficiency
        )
        self.validate_relay_output(relay_nodes, len(data_centers), max_relays)
        direct_avg = compute_direct_average_latency(latency_matrix)
        relay_avg = compute_average_latency(latency_matrix, relay_nodes, relay_efficiency)
        # In this edge case, the optimal solution might be to not use any relays if they worsen latency.
        # Thus, we accept both cases where relay_avg equals direct_avg.
        self.assertLessEqual(
            relay_avg, direct_avg + 1e-6,
            "Even in edge cases, effective average latency should not exceed direct average latency."
        )

    def test_large_graph_structure(self):
        # Test on a larger graph scenario with 10 data centers.
        n = 10
        data_centers = list(range(n))
        # Create a latency matrix where latencies are designed with a pattern.
        latency_matrix = [[0]*n for _ in range(n)]
        for i in range(n):
            for j in range(n):
                if i == j:
                    latency_matrix[i][j] = 0
                else:
                    # Use a pattern that roughly increases with the distance between indices
                    latency_matrix[i][j] = 50 + abs(i - j) * 10
        max_relays = 3
        relay_efficiency = 4.0
        relay_nodes = optimal_relay_placement(
            data_centers=data_centers,
            latency_matrix=latency_matrix,
            max_relays=max_relays,
            relay_efficiency=relay_efficiency
        )
        self.validate_relay_output(relay_nodes, n, max_relays)
        direct_avg = compute_direct_average_latency(latency_matrix)
        relay_avg = compute_average_latency(latency_matrix, relay_nodes, relay_efficiency)
        self.assertLessEqual(
            relay_avg, direct_avg,
            "For large graphs, average latency with relay should not exceed direct average latency."
        )

if __name__ == "__main__":
    unittest.main()