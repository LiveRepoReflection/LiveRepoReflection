import unittest
from network_control import simulate_network_control

class NetworkControlTest(unittest.TestCase):
    def test_direct_edge_no_congestion_then_congestion(self):
        # Graph with a single direct edge from 0 to 1.
        # Edge capacity = 10.
        # T = 0.7, so congestion occurs if sending_rate / 10 > 0.7, i.e., when sending_rate > 7.
        # A = 2, B = 0.5, R_min = 0.5, R_max = 10, time_steps = 5.
        # Simulation:
        # Step 1: R = 1; 1/10=0.1 -> no congestion, update R = min(1+2,10)=3.
        # Step 2: R = 3; 3/10=0.3 -> no congestion, update R = 3+2=5.
        # Step 3: R = 5; 5/10=0.5 -> no congestion, update R = 5+2=7.
        # Step 4: R = 7; 7/10=0.7, not strictly greater than T, update R = 7+2=9.
        # Step 5: R = 9; 9/10=0.9 -> congestion, update R = max(0.5, 9*0.5)=4.5.
        # The output list should be the sending rates at the start of each time step.
        n = 2
        m = 1
        edges = [(0, 1, 10)]
        T = 0.7
        A = 2
        B = 0.5
        R_min = 0.5
        R_max = 10
        time_steps = 5
        expected = [1.000000, 3.000000, 5.000000, 7.000000, 9.000000]
        result = simulate_network_control(n, m, edges, T, A, B, R_min, R_max, time_steps)
        self.assertEqual(result, expected)

    def test_disconnected_graph_increases_rate(self):
        # Graph where destination (node 2) is disconnected from source (node 0)
        # Only one edge (0,1,5) is provided.
        # Maximum flow is 0 so no edge gets any flow, hence no congestion.
        # T = 0.7, A = 1, B = 0.5, R_min = 0.5, R_max = 10, time_steps = 3.
        # Rate increases additively each step.
        n = 3
        m = 1
        edges = [(0, 1, 5)]
        T = 0.7
        A = 1
        B = 0.5
        R_min = 0.5
        R_max = 10
        time_steps = 3
        # Simulation:
        # Step 1: R = 1; no flow available => no congestion; update: 1+1 = 2.
        # Step 2: R = 2; update: 2+1 = 3.
        # Step 3: R = 3; update would be 4 but simulation ends.
        expected = [1.000000, 2.000000, 3.000000]
        result = simulate_network_control(n, m, edges, T, A, B, R_min, R_max, time_steps)
        self.assertEqual(result, expected)

    def test_single_path_multiple_hops(self):
        # Graph with a single path from source to destination through intermediate nodes.
        # n = 4; edges: 0->1, 1->2, 2->3, each with capacity = 7.
        # T = 0.8, A = 1, B = 0.5, R_min = 1, R_max = 10, time_steps = 4.
        # For a single path, utilization = sending_rate / 7.
        # Simulation:
        # Step 1: R = 1; 1/7 ~ 0.142857 < 0.8, update R = 1+1 = 2.
        # Step 2: R = 2; 2/7 ~ 0.285714 < 0.8, update R = 2+1 = 3.
        # Step 3: R = 3; 3/7 ~ 0.428571 < 0.8, update R = 3+1 = 4.
        # Step 4: R = 4; 4/7 ~ 0.571429 < 0.8, update would be 5 but simulation stops.
        expected = [1.000000, 2.000000, 3.000000, 4.000000]
        n = 4
        m = 3
        edges = [(0, 1, 7), (1, 2, 7), (2, 3, 7)]
        T = 0.8
        A = 1
        B = 0.5
        R_min = 1
        R_max = 10
        time_steps = 4
        result = simulate_network_control(n, m, edges, T, A, B, R_min, R_max, time_steps)
        self.assertEqual(result, expected)

    def test_rate_limits_and_congestion(self):
        # Graph with a single direct edge from source to destination.
        # Check that R_max is not exceeded and R_min is respected on multiplicative decrease.
        # n = 2; edge: (0,1,20), T = 0.5, A = 5, B = 0.2, R_min = 1, R_max = 15, time_steps = 4.
        # Simulation:
        # Step 1: R = 1; utilization = 1/20 = 0.05 (<0.5), update: min(1+5,15)=6.
        # Step 2: R = 6; utilization = 6/20 = 0.3 (<0.5), update: 6+5=11.
        # Step 3: R = 11; utilization = 11/20 = 0.55 (>0.5), congestion so update: max(1, 11*0.2)=2.2.
        # Step 4: R = 2.2; utilization = 2.2/20 = 0.11 (<0.5), update: 2.2+5=7.2 (capped by R_max if needed, here 7.2 < 15).
        expected = [1.000000, 6.000000, 11.000000, 2.200000]
        n = 2
        m = 1
        edges = [(0, 1, 20)]
        T = 0.5
        A = 5
        B = 0.2
        R_min = 1
        R_max = 15
        time_steps = 4
        result = simulate_network_control(n, m, edges, T, A, B, R_min, R_max, time_steps)
        self.assertEqual(result, expected)

if __name__ == '__main__':
    unittest.main()