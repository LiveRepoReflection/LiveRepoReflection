import unittest
from traffic_simulator import simulate_traffic_flow

class TrafficSimulatorTest(unittest.TestCase):
    def test_no_vehicles(self):
        graph = {
            1: [(2, 10, 5)],
            2: []
        }
        vehicles = []
        congestion_factor = 2.0
        T = 30
        avg_time = simulate_traffic_flow(graph, vehicles, congestion_factor, T)
        self.assertEqual(avg_time, 0)

    def test_single_vehicle_no_congestion(self):
        # A simple direct route with enough capacity so no congestion occurs.
        graph = {
            1: [(2, 10, 5)],
            2: [(3, 10, 10)],
            3: []
        }
        vehicles = [(1, 3, 0)]
        congestion_factor = 2.0
        T = 30
        # Expected travel time = 5 + 10 = 15
        avg_time = simulate_traffic_flow(graph, vehicles, congestion_factor, T)
        self.assertEqual(avg_time, 15)

    def test_single_vehicle_with_congestion(self):
        # Two vehicles on the same road segment with low capacity to force congestion.
        graph = {
            1: [(2, 1, 5)],  # capacity 1 so if two enter at same time, congestion occurs
            2: [(3, 10, 10)],
            3: []
        }
        vehicles = [(1, 3, 0), (1, 3, 0)]
        congestion_factor = 2.0
        T = 50
        # Both vehicles depart at time 0, road 1->2 has capacity 1 so congestion factor applies.
        # For both vehicles entering 1->2 at time 0, travel time becomes 5*2 = 10.
        # Then from 2->3, no congestion so travel time = 10.
        # Thus, each vehicle should take 10 + 10 = 20 if arrival times are within T.
        avg_time = simulate_traffic_flow(graph, vehicles, congestion_factor, T)
        self.assertEqual(avg_time, 20)

    def test_vehicle_timeout(self):
        # Test scenario with a vehicle that does not reach its destination within T.
        graph = {
            1: [(2, 10, 15)],
            2: [(3, 10, 20)],
            3: []
        }
        vehicles = [(1, 3, 0)]
        congestion_factor = 2.0
        # With no congestion, travel time should be 15 + 20 = 35, but we set T = 30 so timeout.
        T = 30
        avg_time = simulate_traffic_flow(graph, vehicles, congestion_factor, T)
        self.assertEqual(avg_time, 0)

    def test_multiple_routes(self):
        # Test a graph where vehicles can choose between a congested path and a faster alternative.
        graph = {
            1: [(2, 1, 5), (3, 10, 8)],
            2: [(4, 10, 10)],
            3: [(4, 10, 15)],
            4: []
        }
        # Two vehicles starting from 1 to 4.
        # If both take the 1->2->4 path, congestion may occur on 1->2.
        # The alternative path 1->3->4 is less congested.
        vehicles = [(1, 4, 0), (1, 4, 0)]
        congestion_factor = 2.0
        T = 50
        # Depending on simulation logic, vehicles could choose different paths. We only test that simulation returns
        # an average travel time > 0 and within a plausible range.
        avg_time = simulate_traffic_flow(graph, vehicles, congestion_factor, T)
        self.assertTrue(avg_time > 0)
        self.assertTrue(avg_time <= 50)

    def test_mixed_departure_times(self):
        # Test vehicles with staggered departure times to avoid or trigger congestion.
        graph = {
            1: [(2, 1, 5)],
            2: [(3, 1, 10)],
            3: []
        }
        # Three vehicles, the first two depart at same time causing congestion and the third departs later and avoids congestion.
        vehicles = [(1, 3, 0), (1, 3, 0), (1, 3, 10)]
        congestion_factor = 2.0
        T = 60
        # For the first two, 1->2 is congested so travel = 5*2 = 10, then 2->3 congested => 10*2=20; total = 30.
        # Third vehicle starts at time 10, may travel without congestion if previous vehicles clear.
        # Expected average time in range between 20 and 30.
        avg_time = simulate_traffic_flow(graph, vehicles, congestion_factor, T)
        self.assertTrue(20 <= avg_time <= 30)

if __name__ == '__main__':
    unittest.main()