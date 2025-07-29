import unittest
from traffic_rebalance import optimal_traffic_rebalance

class TestOptimalTrafficRebalance(unittest.TestCase):

    def test_no_rerouting_single_edge(self):
        # Graph: one edge from 0 -> 1, capacity 10, flow 12 => congestion = (12-10)^2 = 4.
        graph = [(0, 1, 10, 12)]
        # One vehicle from 0 to 1.
        vehicle_routes = [(0, 1)]
        K = 0
        expected = 4
        result = optimal_traffic_rebalance(graph, vehicle_routes, K)
        self.assertEqual(result, expected)

    def test_rerouting_improves_congestion(self):
        # Graph with two paths from 0 to 2.
        # Edge details:
        # (0, 1): capacity=10, flow=12 -> congestion: (12-10)^2 = 4.
        # (1, 2): capacity=10, flow=12 -> congestion: 4.
        # (0, 2): capacity=10, flow=5 -> congestion: 0.
        # One vehicle originally routed from 0->1->2.
        graph = [
            (0, 1, 10, 12),
            (1, 2, 10, 12),
            (0, 2, 10, 5)
        ]
        vehicle_routes = [(0, 2)]
        # With no rerouting available, total congestion is 4 + 4 + 0 = 8.
        result_no_reroute = optimal_traffic_rebalance(graph, vehicle_routes, 0)
        self.assertEqual(result_no_reroute, 8)
        # With one reroute available, moving the vehicle to the alternate direct route:
        # New flows: (0,1): 11 -> congestion = 1; (1,2): 11 -> congestion = 1; (0,2): 6 -> congestion = 0.
        # Total congestion = 1 + 1 + 0 = 2.
        result_reroute = optimal_traffic_rebalance(graph, vehicle_routes, 1)
        self.assertEqual(result_reroute, 2)
        # If K > number of vehicles, result should remain optimal.
        result_extra = optimal_traffic_rebalance(graph, vehicle_routes, 5)
        self.assertEqual(result_extra, 2)

    def test_multiple_vehicles_rerouting(self):
        # Graph: four edges with two alternative routes from 0 to 3.
        # Congested route: (0,1): capacity=10, flow=15, (1,3): capacity=10, flow=15.
        # Alternative route: (0,2): capacity=10, flow=8, (2,3): capacity=10, flow=8.
        # Two vehicles initially assigned on the congested path.
        graph = [
            (0, 1, 10, 15),
            (1, 3, 10, 15),
            (0, 2, 10, 8),
            (2, 3, 10, 8)
        ]
        vehicle_routes = [(0, 3), (0, 3)]
        # With no rerouting:
        # Congestion on congested path: (15-10)^2 = 25 each for (0,1) and (1,3); alternative route remains 0.
        # Total congestion = 25 + 25 + 0 + 0 = 50.
        result_no_reroute = optimal_traffic_rebalance(graph, vehicle_routes, 0)
        self.assertEqual(result_no_reroute, 50)

        # With one vehicle rerouted:
        # One vehicle remains on congested path, one is rerouted.
        # For congested edges: new flows become 14 on each congested edge => congestion: (14-10)^2 = 16 each.
        # For alternative edges: new flows become 8+1=9 => congestion 0.
        # Total = 16 + 16 + 0 + 0 = 32.
        result_one_reroute = optimal_traffic_rebalance(graph, vehicle_routes, 1)
        self.assertEqual(result_one_reroute, 32)

        # With two vehicles rerouted:
        # Both vehicles rerouted: congested edges remain at original flows: 15-2=13 => congestion: (13-10)^2 = 9,
        # Alternative route edges: flow become 8+2=10 => congestion = 0.
        # Total = 9 + 9 + 0 + 0 = 18.
        result_two_reroute = optimal_traffic_rebalance(graph, vehicle_routes, 2)
        self.assertEqual(result_two_reroute, 18)

    def test_disconnected_graph_and_multiple_routes(self):
        # Graph: Two disconnected subgraphs.
        # Subgraph 1 (relevant): Nodes 0,1,2.
        #   Edges: (0, 1): capacity=5, flow=7   -> congestion: (7-5)^2 = 4.
        #           (1, 2): capacity=5, flow=7   -> congestion: 4.
        #           (0, 2): capacity=5, flow=3   -> congestion: 0.
        # One vehicle travels from 0 to 2.
        #
        # Subgraph 2 (irrelevant): Nodes 3,4.
        #   Edge: (3, 4): capacity=10, flow=8 -> congestion: 0.
        graph = [
            (0, 1, 5, 7),
            (1, 2, 5, 7),
            (0, 2, 5, 3),
            (3, 4, 10, 8)
        ]
        vehicle_routes = [(0, 2)]
        # With no rerouting:
        # Congestion in Subgraph1: 4 + 4 + 0 = 8,
        # Subgraph2: 0.
        expected_no_reroute = 8
        result = optimal_traffic_rebalance(graph, vehicle_routes, 0)
        self.assertEqual(result, expected_no_reroute)

        # With one reroute available:
        # Optimally, reroute the vehicle via the direct edge (0,2):
        # Updated flows: (0,1)=6 -> congestion=(6-5)^2 =1, (1,2)=6 -> congestion=1, (0,2)=4 -> congestion=0.
        # Total congestion = 1+1+0+0 = 2.
        expected_with_reroute = 2
        result_reroute = optimal_traffic_rebalance(graph, vehicle_routes, 1)
        self.assertEqual(result_reroute, expected_with_reroute)

    def test_no_possible_improvement(self):
        # Graph with all edges under capacity.
        graph = [
            (0, 1, 10, 7),
            (1, 2, 10, 7),
            (0, 2, 10, 5)
        ]
        vehicle_routes = [(0, 2)]
        # All edges are below or equal to capacity, so congestion is zero.
        for k in range(0, 5):
            self.assertEqual(optimal_traffic_rebalance(graph, vehicle_routes, k), 0)

if __name__ == '__main__':
    unittest.main()