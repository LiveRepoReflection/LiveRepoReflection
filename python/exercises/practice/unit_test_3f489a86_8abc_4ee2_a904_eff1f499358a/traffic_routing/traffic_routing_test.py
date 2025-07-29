import unittest
from traffic_routing import optimal_traffic_flow

class TrafficRoutingTest(unittest.TestCase):
    def test_single_vehicle_simple_path(self):
        graph = {
            0: {1: {'time': 5, 'capacity': 10}},
            1: {2: {'time': 5, 'capacity': 10}},
            2: {}
        }
        requests = [(0, 2, 0)]
        simulation_duration = 20
        
        def get_capacity(graph, u, v, time):
            return 0  # Always empty roads
        
        avg_time = optimal_traffic_flow(graph, requests, simulation_duration, get_capacity)
        self.assertEqual(avg_time, 10.0)
    
    def test_single_vehicle_no_path(self):
        graph = {
            0: {1: {'time': 5, 'capacity': 10}},
            1: {},
            2: {}
        }
        requests = [(0, 2, 0)]
        simulation_duration = 20
        
        def get_capacity(graph, u, v, time):
            return 0  # Always empty roads
        
        avg_time = optimal_traffic_flow(graph, requests, simulation_duration, get_capacity)
        self.assertEqual(avg_time, 20.0)  # Penalized with simulation duration
    
    def test_single_vehicle_blocked_path(self):
        graph = {
            0: {1: {'time': 5, 'capacity': 1}},
            1: {2: {'time': 5, 'capacity': 1}},
            2: {}
        }
        requests = [(0, 2, 0)]
        simulation_duration = 20
        
        def get_capacity(graph, u, v, time):
            # Road is at capacity
            return graph[u][v]['capacity']
        
        avg_time = optimal_traffic_flow(graph, requests, simulation_duration, get_capacity)
        self.assertEqual(avg_time, 20.0)  # Penalized with simulation duration
    
    def test_multiple_vehicles_simple_paths(self):
        graph = {
            0: {1: {'time': 5, 'capacity': 10}, 2: {'time': 12, 'capacity': 10}},
            1: {3: {'time': 8, 'capacity': 10}},
            2: {3: {'time': 4, 'capacity': 10}},
            3: {}
        }
        requests = [(0, 3, 0), (0, 3, 1)]
        simulation_duration = 30
        
        def get_capacity(graph, u, v, time):
            return 0  # Always empty roads
        
        avg_time = optimal_traffic_flow(graph, requests, simulation_duration, get_capacity)
        # First vehicle should take path 0->1->3 with time 13
        # Second vehicle should take path 0->1->3 with time 13
        # Average: (13 + 13) / 2 = 13.0
        self.assertEqual(avg_time, 13.0)
    
    def test_multiple_vehicles_with_capacity_constraints(self):
        graph = {
            0: {1: {'time': 5, 'capacity': 1}, 2: {'time': 12, 'capacity': 10}},
            1: {3: {'time': 8, 'capacity': 10}},
            2: {3: {'time': 4, 'capacity': 10}},
            3: {}
        }
        requests = [(0, 3, 0), (0, 3, 1)]
        simulation_duration = 30
        
        # First route uses 0->1, second needs alternative
        vehicle_positions = {}
        
        def get_capacity(graph, u, v, time):
            # Update based on the simulation time
            count = 0
            for pos in vehicle_positions.values():
                if time in pos and pos[time] == (u, v):
                    count += 1
            return count
        
        # Track first vehicle on 0->1 at time 0, and 1->3 at time 5
        vehicle_positions[0] = {0: (0, 1), 5: (1, 3)}
        
        avg_time = optimal_traffic_flow(graph, requests, simulation_duration, get_capacity)
        # First vehicle should take path 0->1->3 with time 13
        # Second vehicle should take path 0->2->3 with time 16 (since 0->1 is at capacity)
        # Average: (13 + 16) / 2 = 14.5
        self.assertEqual(avg_time, 14.5)
    
    def test_dynamic_traffic_updates(self):
        graph = {
            0: {1: {'time': 5, 'capacity': 10}, 2: {'time': 12, 'capacity': 10}},
            1: {3: {'time': 8, 'capacity': 10}},
            2: {3: {'time': 4, 'capacity': 10}},
            3: {}
        }
        requests = [(0, 3, 0), (0, 3, 5)]
        simulation_duration = 30
        
        # Traffic conditions change during simulation
        dynamic_times = {
            5: {0: {1: {'time': 15, 'capacity': 10}}}  # At time 5, road 0->1 becomes congested
        }
        
        def get_capacity(graph, u, v, time):
            # Update the graph with dynamic traffic conditions
            if time in dynamic_times:
                for node in dynamic_times[time]:
                    for neighbor, data in dynamic_times[time][node].items():
                        if neighbor in graph[node]:
                            graph[node][neighbor] = data
            return 0  # No capacity issues
        
        avg_time = optimal_traffic_flow(graph, requests, simulation_duration, get_capacity)
        # First vehicle starts at time 0, takes path 0->1->3 with time 13
        # Second vehicle starts at time 5, by which time 0->1 has time 15
        # Second vehicle should take path 0->2->3 with time 16
        # Average: (13 + 16) / 2 = 14.5
        self.assertAlmostEqual(avg_time, 14.5, delta=0.1)
    
    def test_lost_vehicles(self):
        graph = {
            0: {1: {'time': 5, 'capacity': 10}},
            1: {2: {'time': 5, 'capacity': 10}},
            2: {}
        }
        # Vehicle starts too late to reach destination within simulation
        requests = [(0, 2, 15)]
        simulation_duration = 20
        
        def get_capacity(graph, u, v, time):
            return 0  # Always empty roads
        
        avg_time = optimal_traffic_flow(graph, requests, simulation_duration, get_capacity)
        # Vehicle needs 10 time units but only has 5 left, so it's lost
        self.assertEqual(avg_time, 20.0)  # Penalized with simulation duration
    
    def test_complex_scenario(self):
        graph = {
            0: {1: {'time': 10, 'capacity': 50}, 2: {'time': 15, 'capacity': 30}},
            1: {3: {'time': 20, 'capacity': 40}},
            2: {3: {'time': 12, 'capacity': 20}, 4: {'time': 8, 'capacity': 60}},
            3: {4: {'time': 5, 'capacity': 25}},
            4: {}
        }
        requests = [(0, 4, 0), (1, 4, 5), (2, 3, 10)]
        simulation_duration = 60
        
        dynamic_traffic = {
            # At t=20, road 2->4 gets congested
            20: {2: {4: {'time': 20, 'capacity': 60}}},
            # At t=30, road 0->1 gets congested
            30: {0: {1: {'time': 25, 'capacity': 50}}}
        }
        
        vehicle_positions = {}
        
        def get_capacity(graph, u, v, time):
            # Update the graph with dynamic traffic conditions
            if time in dynamic_traffic:
                for node in dynamic_traffic[time]:
                    for neighbor, data in dynamic_traffic[time][node].items():
                        if neighbor in graph[node]:
                            graph[node][neighbor] = data
            
            # Calculate current load
            count = 0
            for pos in vehicle_positions.values():
                if time in pos and pos[time] == (u, v):
                    count += 1
            return count
        
        # Track some vehicle positions to simulate traffic
        vehicle_positions[0] = {5: (0, 2), 20: (2, 4)}
        vehicle_positions[1] = {10: (1, 3), 30: (3, 4)}
        
        avg_time = optimal_traffic_flow(graph, requests, simulation_duration, get_capacity)
        # A reasonable estimate for this complex scenario (may vary with implementation)
        self.assertGreater(avg_time, 0.0)
        self.assertLess(avg_time, 60.0)  # Should be less than simulation duration

if __name__ == '__main__':
    unittest.main()