import unittest
from network_path import optimal_route

class NetworkPathTest(unittest.TestCase):
    def test_simple_path(self):
        # Simple linear network: 0 -> 1 -> 2
        num_routers = 3
        edges = [
            (0, 1, 100),
            (1, 2, 200)
        ]
        source = 0
        destination = 2
        # One time window corresponding to unique_time 5
        time_windows = [(5, 6)]
        unique_times = [5]
        # For edge (0,1): congestion 0.0, for edge (1,2): congestion 0.5
        congestion_levels = [
            [0.0, 0.5]
        ]
        # Available capacities:
        # (0,1): 100 * (1 - 0.0) = 100 and (1,2): 200 * (1 - 0.5) = 100, so bottleneck = 100.
        expected = [100]
        result = optimal_route(num_routers, edges, source, destination, time_windows, congestion_levels, unique_times)
        self.assertEqual(result, expected)

    def test_diamond_network(self):
        # Diamond shaped network:
        # 0 -> 1 -> 3 and 0 -> 2 -> 3
        num_routers = 4
        edges = [
            (0, 1, 100),
            (0, 2, 50),
            (1, 3, 100),
            (2, 3, 200)
        ]
        source = 0
        destination = 3
        time_windows = [(5, 6)]
        unique_times = [5]
        # Congestion levels:
        # For edge (0,1): 0.1, (0,2): 0.0, (1,3): 0.4, (2,3): 0.2
        # Path 0->1->3: available: 100*0.9=90, 100*0.6=60, bottleneck=60.
        # Path 0->2->3: available: 50*1.0=50, 200*0.8=160, bottleneck=50.
        expected = [60]
        congestion_levels = [
            [0.1, 0.0, 0.4, 0.2]
        ]
        result = optimal_route(num_routers, edges, source, destination, time_windows, congestion_levels, unique_times)
        self.assertEqual(result, expected)

    def test_no_path_due_to_full_congestion(self):
        # Path exists structurally but one edge is fully congested.
        num_routers = 3
        edges = [
            (0, 1, 50),
            (1, 2, 50)
        ]
        source = 0
        destination = 2
        time_windows = [(5, 6)]
        unique_times = [5]
        # Set congestion to 1.0 (full congestion) for the first edge and 0 for the second.
        # Available capacity for (0,1): 50 * 0 = 0 so route is not viable.
        congestion_levels = [
            [1.0, 0.0]
        ]
        expected = [-1]
        result = optimal_route(num_routers, edges, source, destination, time_windows, congestion_levels, unique_times)
        self.assertEqual(result, expected)

    def test_multiple_time_windows(self):
        # Using a diamond network with multiple congestion snapshots.
        num_routers = 4
        edges = [
            (0, 1, 100),
            (0, 2, 50),
            (1, 3, 100),
            (2, 3, 200)
        ]
        source = 0
        destination = 3
        # Three time windows, each corresponding to a unique time.
        time_windows = [(5, 6), (10, 12), (15, 16)]
        unique_times = [5, 10, 15]
        congestion_levels = [
            # For time = 5:
            # (0,1):0.1, (0,2):0.0, (1,3):0.4, (2,3):0.2
            [0.1, 0.0, 0.4, 0.2],
            # For time = 10:
            # (0,1):0.0, (0,2):0.5, (1,3):0.0, (2,3):0.5
            [0.0, 0.5, 0.0, 0.5],
            # For time = 15:
            # (0,1):0.2, (0,2):0.2, (1,3):0.2, (2,3):0.2
            [0.2, 0.2, 0.2, 0.2]
        ]
        # Expected computation:
        # Time = 5:
        #   Path 0->1->3: 100*0.9 = 90, 100*0.6 = 60, bottleneck = 60.
        #   Path 0->2->3: 50*1.0 = 50, 200*0.8 = 160, bottleneck = 50.
        #   Best = 60.
        # Time = 10:
        #   Path 0->1->3: 100*1.0 = 100, 100*1.0 = 100, bottleneck = 100.
        #   Path 0->2->3: 50*0.5 = 25, 200*0.5 = 100, bottleneck = 25.
        #   Best = 100.
        # Time = 15:
        #   Path 0->1->3: 100*0.8 = 80, 100*0.8 = 80, bottleneck = 80.
        #   Path 0->2->3: 50*0.8 = 40, 200*0.8 = 160, bottleneck = 40.
        #   Best = 80.
        expected = [60, 100, 80]
        result = optimal_route(num_routers, edges, source, destination, time_windows, congestion_levels, unique_times)
        self.assertEqual(result, expected)

    def test_disconnected_network(self):
        # Test where the destination is not reachable in any way.
        num_routers = 4
        edges = [
            (0, 1, 100),
            (2, 3, 100)
        ]
        source = 0
        destination = 3
        time_windows = [(5, 6)]
        unique_times = [5]
        # There is no connection from source 0 to destination 3.
        congestion_levels = [
            [0.0, 0.0]
        ]
        expected = [-1]
        result = optimal_route(num_routers, edges, source, destination, time_windows, congestion_levels, unique_times)
        self.assertEqual(result, expected)

if __name__ == '__main__':
    unittest.main()