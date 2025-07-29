import unittest
import av_routing

# Define two sample graphs for testing.
# Graph for route planning tests:
# Nodes: 0, 1, 2
# Edges: {0: [(1, 10), (2, 40)], 1: [(2, 20)]}
sample_graph_route = {
    0: [(1, 10), (2, 40)],
    1: [(2, 20)],
    2: []
}

# Graph for fleet rebalancing tests:
# Nodes: 0, 1, 2
# Edges: {0: [(1, 10), (2, 15)], 1: [(0, 10), (2, 5)], 2: [(0, 15), (1, 5)]}
sample_graph_fleet = {
    0: [(1, 10), (2, 15)],
    1: [(0, 10), (2, 5)],
    2: [(0, 15), (1, 5)]
}

# For testing, we assume that the av_routing module uses a global variable named "graph"
# to represent the road network, and that the functions plan_route and fleet_rebalance
# rely on this variable. We'll set it accordingly in our tests.

# We also need to control the congestion function.
# For most tests, we use a dummy congestion function that returns 1.
def constant_congestion(u, v, t):
    return 1

# A dynamic congestion function that returns different factors based on conditions.
def dynamic_congestion(u, v, t):
    # For edge (1, 2) if t >= 10, return congestion factor 2, otherwise 1.
    if u == 1 and v == 2 and t >= 10:
        return 2
    return 1

class TestPlanRoute(unittest.TestCase):
    def setUp(self):
        # Set the graph and congestion function to the constant ones.
        av_routing.graph = sample_graph_route
        av_routing.congestion = constant_congestion

    def test_basic_route(self):
        # With constant congestion, the travel time on edge (0->1) = 10 and (1->2) = 20.
        # So best route from 0 to 2 should be 0 -> 1 -> 2 with total time = 30.
        start = 0
        end = 2
        departure_time = 0
        horizon = 100
        expected_path = [0, 1, 2]
        expected_arrival = 30  # 0 + 10 + 20
        path, arrival_time = av_routing.plan_route(start, end, departure_time, horizon)
        self.assertEqual(path, expected_path)
        self.assertEqual(arrival_time, expected_arrival)

    def test_no_route(self):
        # Test a route where no path exists.
        # Request from 2 to 0 in the directed sample_graph_route.
        start = 2
        end = 0
        departure_time = 0
        horizon = 100
        path, arrival_time = av_routing.plan_route(start, end, departure_time, horizon)
        self.assertIsNone(path)
        self.assertIsNone(arrival_time)

    def test_dynamic_congestion(self):
        # Use dynamic congestion where the edge (1 -> 2) has congestion factor 2 if time>=10.
        av_routing.congestion = dynamic_congestion
        # For route planning from 0->2:
        # Two possible routes:
        # Route 0->1->2:
        #   Edge (0->1): base_time 10, congestion= constant 1 => 10.
        #   Arrival time at node 1 = 0 + 10 = 10.
        #   Edge (1->2): base_time 20, congestion now = 2 (since t==10) => 40.
        #   Total = 10 + 40 = 50.
        # Route 0->2 direct:
        #   base_time = 40, congestion=1 (always for that edge) => 40.
        # So expected best route is direct [0, 2].
        start = 0
        end = 2
        departure_time = 0
        horizon = 100
        expected_path = [0, 2]
        expected_arrival = 40
        path, arrival_time = av_routing.plan_route(start, end, departure_time, horizon)
        self.assertEqual(path, expected_path)
        self.assertEqual(arrival_time, expected_arrival)

class TestFleetRebalance(unittest.TestCase):
    def setUp(self):
        # Set the graph and congestion function to constant for fleet rebalancing tests.
        av_routing.graph = sample_graph_fleet
        av_routing.congestion = constant_congestion

    def test_basic_rebalance(self):
        # Two AVs with:
        # AV0: current location 0, desired destination originally 2.
        # AV1: current location 1, desired destination originally 0.
        # Possible assignments:
        # Option 1: No swap:
        #   cost from 0->2 = best is 0->1->2 = 10+5 = 15.
        #   cost from 1->0 = direct = 10.
        #   Total = 25.
        # Option 2: Swap:
        #   cost from 0->0 = 0 and cost from 1->2 = 5.
        #   Total = 5.
        # Optimal is swap.
        avs = [(0, 2), (1, 0)]
        expected_total = 5
        expected_assignment = {0: 1, 1: 0}  # mapping: AV index -> index of chosen destination from input list
        total_travel_time, assignment = av_routing.fleet_rebalance(avs)
        self.assertEqual(total_travel_time, expected_total)
        self.assertEqual(assignment, expected_assignment)

    def test_single_av(self):
        # Test fleet rebalancing with one AV.
        avs = [(0, 1)]
        # Shortest path from 0 to 1 in sample_graph_fleet is 10.
        expected_total = 10
        expected_assignment = {0: 0}  # Only one option.
        total_travel_time, assignment = av_routing.fleet_rebalance(avs)
        self.assertEqual(total_travel_time, expected_total)
        self.assertEqual(assignment, expected_assignment)

    def test_no_av(self):
        # Test fleet rebalancing with an empty list.
        avs = []
        expected_total = 0
        expected_assignment = {}
        total_travel_time, assignment = av_routing.fleet_rebalance(avs)
        self.assertEqual(total_travel_time, expected_total)
        self.assertEqual(assignment, expected_assignment)

if __name__ == '__main__':
    unittest.main()