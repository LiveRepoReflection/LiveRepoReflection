import unittest
from network_qos_routing import find_minimum_cost

class TestNetworkQosRouting(unittest.TestCase):
    def test_single_valid_path(self):
        # Simple case with a direct edge and enough capacity
        nodes = [(100, 5), (100, 10)]
        edges = [(0, 1, 50, 0.05)]
        source = 0
        destination = 1
        demand = 50
        max_latency = 100
        max_packet_loss_rate = 0.1
        # Cost: 50*5 + 50*10 = 250 + 500 = 750
        self.assertEqual(find_minimum_cost(nodes, edges, source, destination, demand, max_latency, max_packet_loss_rate), 750)

    def test_multiple_paths_choose_minimum_cost(self):
        # Two paths: choose the one with minimum cost, both paths satisfy constraints.
        nodes = [(50, 1), (60, 2), (40, 3), (70, 1)]
        edges = [
            (0, 1, 10, 0.05),
            (0, 2, 15, 0.1),
            (1, 3, 20, 0.02),
            (2, 3, 25, 0.08)
        ]
        source = 0
        destination = 3
        demand = 30
        max_latency = 60
        max_packet_loss_rate = 0.2
        # Expected to choose path 0->1->3 with cost: 30*1 + 30*2 + 30*1 = 30+60+30 = 120.
        self.assertEqual(find_minimum_cost(nodes, edges, source, destination, demand, max_latency, max_packet_loss_rate), 120)

    def test_over_capacity_node(self):
        # The middle node does not have enough cpu capacity for the given demand.
        nodes = [(100, 1), (20, 5), (100, 1)]
        edges = [
            (0, 1, 10, 0.01),
            (1, 2, 10, 0.01)
        ]
        source = 0
        destination = 2
        demand = 50   # Node 1 capacity is 20, so path is invalid.
        max_latency = 50
        max_packet_loss_rate = 0.1
        self.assertEqual(find_minimum_cost(nodes, edges, source, destination, demand, max_latency, max_packet_loss_rate), -1)

    def test_latency_violation(self):
        # The only valid path exceeds the maximum allowed latency.
        nodes = [(100, 1), (100, 2), (100, 3)]
        edges = [
            (0, 1, 100, 0.01),
            (1, 2, 150, 0.01)
        ]
        source = 0
        destination = 2
        demand = 30
        max_latency = 200  # Total latency would be 250, so violation.
        max_packet_loss_rate = 0.1
        self.assertEqual(find_minimum_cost(nodes, edges, source, destination, demand, max_latency, max_packet_loss_rate), -1)

    def test_packet_loss_violation(self):
        # The only valid path exceeds the packet loss rate constraint.
        nodes = [(100, 2), (100, 3), (100, 4)]
        edges = [
            (0, 1, 20, 0.3),   # high loss rate
            (1, 2, 20, 0.3)
        ]
        source = 0
        destination = 2
        demand = 40
        max_latency = 100
        # Overall loss rate = 1 - (0.7 * 0.7) = 0.51, which is above the allowed value
        max_packet_loss_rate = 0.5
        self.assertEqual(find_minimum_cost(nodes, edges, source, destination, demand, max_latency, max_packet_loss_rate), -1)

    def test_non_connected_graph(self):
        # Graph with no valid path from source to destination
        nodes = [(100, 1), (100, 2), (100, 3)]
        edges = [
            (0, 1, 10, 0.01)
            # No edge from node 1 to node 2, so destination unreachable.
        ]
        source = 0
        destination = 2
        demand = 10
        max_latency = 50
        max_packet_loss_rate = 0.05
        self.assertEqual(find_minimum_cost(nodes, edges, source, destination, demand, max_latency, max_packet_loss_rate), -1)

    def test_zero_demand(self):
        # When demand is zero, the cost should be zero regardless of node costs.
        nodes = [(10, 100), (20, 200)]
        edges = [(0, 1, 5, 0.05)]
        source = 0
        destination = 1
        demand = 0
        max_latency = 10
        max_packet_loss_rate = 0.1
        self.assertEqual(find_minimum_cost(nodes, edges, source, destination, demand, max_latency, max_packet_loss_rate), 0)

    def test_complex_case_multiple_options(self):
        # More complex graph with several possible paths.
        nodes = [
            (100, 1),   # 0
            (80, 3),    # 1
            (70, 2),    # 2
            (90, 4),    # 3
            (100, 1)    # 4
        ]
        edges = [
            (0, 1, 10, 0.05),
            (1, 4, 40, 0.02),
            (0, 2, 20, 0.1),
            (2, 3, 15, 0.03),
            (3, 4, 10, 0.02),
            (1, 2, 5, 0.05),
            (2, 4, 30, 0.04)
        ]
        source = 0
        destination = 4
        demand = 60
        max_latency = 70
        # Evaluate different potential paths and their costs:
        #  Path 0->1->4: Cost = 60*1 + 60*3 + 60*1 = 60 + 180 + 60 = 300, latency = 10+40=50, loss = 1 - (0.95*0.98) = 0.069
        #  Path 0->2->3->4: Cost = 60*1 + 60*2 + 60*4 + 60*1 = 60 + 120 + 240 + 60 = 480, latency = 20+15+10=45, loss = 1 - (0.9*0.97*0.98) ~ 0.143
        #  Path 0->2->4: Cost = 60*1 + 60*2 + 60*1 = 60+120+60 = 240, latency = 20+30=50, loss = 1 - (0.9*0.96)= 0.136
        # Both paths satisfy constraints; the minimum cost is 240.
        self.assertEqual(find_minimum_cost(nodes, edges, source, destination, demand, max_latency, 0.15), 240)

if __name__ == '__main__':
    unittest.main()