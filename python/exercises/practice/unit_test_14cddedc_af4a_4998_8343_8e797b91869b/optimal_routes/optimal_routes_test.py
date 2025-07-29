import unittest
from optimal_routes import find_optimal_routes


class TestOptimalRoutes(unittest.TestCase):
    
    def test_simple_route(self):
        # Simple graph with time-independent travel times
        graph = {
            0: {1: lambda t: 10},  # Depot to Pickup: 10 seconds
            1: {2: lambda t: 15},  # Pickup to Delivery: 15 seconds
            2: {0: lambda t: 12}   # Delivery to Depot: 12 seconds
        }
        
        def time_dependent_travel_times(graph, start_node, end_node, departure_time):
            return graph[start_node][end_node](departure_time)
        
        delivery_tasks = [(1, 2, 0, 100)]  # Pickup at 1, deliver at 2, between time 0 and 100
        depot_location = 0
        max_flight_time = 50  # More than enough for the route
        
        routes = find_optimal_routes(graph, delivery_tasks, depot_location, max_flight_time, time_dependent_travel_times)
        
        self.assertEqual(len(routes), 1)
        self.assertEqual(routes[0][0], 0)  # Start at depot
        self.assertEqual(routes[0][1], 1)  # Go to pickup location
        self.assertEqual(routes[0][2], 2)  # Go to delivery location
        self.assertEqual(routes[0][3], 0)  # Return to depot
    
    def test_time_dependent_route(self):
        # Graph with time-dependent travel times
        graph = {
            0: {1: lambda t: 10 + (t % 60) // 10},  # Travel time increases slightly every 10 seconds
            1: {2: lambda t: 15 + (t % 60) // 5},
            2: {0: lambda t: 12 + (t % 60) // 15}
        }
        
        def time_dependent_travel_times(graph, start_node, end_node, departure_time):
            return graph[start_node][end_node](departure_time)
        
        delivery_tasks = [(1, 2, 10, 60)]  # Pickup at 1, deliver at 2, between time 10 and 60
        depot_location = 0
        max_flight_time = 60
        
        routes = find_optimal_routes(graph, delivery_tasks, depot_location, max_flight_time, time_dependent_travel_times)
        
        self.assertEqual(len(routes), 1)
        self.assertEqual(routes[0][0], 0)  # Start at depot
        # We don't strictly check the middle parts of the route as the optimal path
        # may vary based on the implementation
        self.assertEqual(routes[0][-1], 0)  # End at depot
    
    def test_multiple_delivery_tasks(self):
        # Graph with multiple possible routes
        graph = {
            0: {1: lambda t: 10, 3: lambda t: 15},
            1: {2: lambda t: 15, 4: lambda t: 20},
            2: {0: lambda t: 12, 5: lambda t: 18},
            3: {4: lambda t: 8, 0: lambda t: 15},
            4: {5: lambda t: 10, 0: lambda t: 20},
            5: {0: lambda t: 18, 3: lambda t: 12}
        }
        
        def time_dependent_travel_times(graph, start_node, end_node, departure_time):
            return graph[start_node][end_node](departure_time)
        
        delivery_tasks = [
            (1, 2, 0, 100),  # Pickup at 1, deliver at 2, between time 0 and 100
            (3, 4, 0, 100),  # Pickup at 3, deliver at 4, between time 0 and 100
            (4, 5, 0, 100)   # Pickup at 4, deliver at 5, between time 0 and 100
        ]
        depot_location = 0
        max_flight_time = 60
        
        routes = find_optimal_routes(graph, delivery_tasks, depot_location, max_flight_time, time_dependent_travel_times)
        
        self.assertEqual(len(routes), 3)
        for route in routes:
            self.assertEqual(route[0], 0)  # Start at depot
            self.assertEqual(route[-1], 0)  # End at depot
    
    def test_infeasible_route_due_to_time_window(self):
        # Graph where the time window constraints make the delivery infeasible
        graph = {
            0: {1: lambda t: 50},  # Depot to Pickup: 50 seconds
            1: {2: lambda t: 30},  # Pickup to Delivery: 30 seconds
            2: {0: lambda t: 40}   # Delivery to Depot: 40 seconds
        }
        
        def time_dependent_travel_times(graph, start_node, end_node, departure_time):
            return graph[start_node][end_node](departure_time)
        
        # The pickup location can be reached at t=50, delivery at t=80, but the window is [0, 60]
        delivery_tasks = [(1, 2, 0, 60)]
        depot_location = 0
        max_flight_time = 200
        
        routes = find_optimal_routes(graph, delivery_tasks, depot_location, max_flight_time, time_dependent_travel_times)
        
        self.assertEqual(routes, [])  # Expect empty list for infeasible routes
    
    def test_infeasible_route_due_to_flight_time(self):
        # Graph where the max flight time constraint makes the delivery infeasible
        graph = {
            0: {1: lambda t: 20},
            1: {2: lambda t: 20},
            2: {0: lambda t: 20}
        }
        
        def time_dependent_travel_times(graph, start_node, end_node, departure_time):
            return graph[start_node][end_node](departure_time)
        
        delivery_tasks = [(1, 2, 0, 100)]
        depot_location = 0
        max_flight_time = 50  # Total route requires 60 seconds
        
        routes = find_optimal_routes(graph, delivery_tasks, depot_location, max_flight_time, time_dependent_travel_times)
        
        self.assertEqual(routes, [])  # Expect empty list for infeasible routes
    
    def test_complex_time_dependent_graph(self):
        # A more complex graph with highly variable time-dependent travel times
        def rush_hour_traffic(t):
            # Simulate traffic: worse during rush hours (7-9 AM, 4-6 PM)
            morning_rush = 25200 <= t < 32400  # 7-9 AM
            evening_rush = 57600 <= t < 64800  # 4-6 PM
            
            if morning_rush or evening_rush:
                return 2.0  # Double travel time during rush hours
            return 1.0
        
        graph = {
            0: {1: lambda t: 15 * rush_hour_traffic(t), 2: lambda t: 25 * rush_hour_traffic(t)},
            1: {0: lambda t: 15 * rush_hour_traffic(t), 3: lambda t: 20 * rush_hour_traffic(t)},
            2: {0: lambda t: 25 * rush_hour_traffic(t), 3: lambda t: 30 * rush_hour_traffic(t)},
            3: {1: lambda t: 20 * rush_hour_traffic(t), 2: lambda t: 30 * rush_hour_traffic(t)}
        }
        
        def time_dependent_travel_times(graph, start_node, end_node, departure_time):
            return graph[start_node][end_node](departure_time)
        
        # Delivery during non-rush hour
        delivery_tasks = [(1, 3, 36000, 50000)]  # Around 10 AM to 2 PM
        depot_location = 0
        max_flight_time = 100
        
        routes = find_optimal_routes(graph, delivery_tasks, depot_location, max_flight_time, time_dependent_travel_times)
        
        self.assertEqual(len(routes), 1)
        
        # Delivery during rush hour
        delivery_tasks = [(1, 3, 28800, 32400)]  # 8-9 AM (rush hour)
        
        routes = find_optimal_routes(graph, delivery_tasks, depot_location, max_flight_time, time_dependent_travel_times)
        
        # This might be feasible or not depending on the exact implementation
        # so we don't assert specific results here
    
    def test_intermediate_stops(self):
        # Graph where the optimal route requires intermediate stops
        graph = {
            0: {1: lambda t: 30, 2: lambda t: 10},
            1: {3: lambda t: 20, 0: lambda t: 30},
            2: {1: lambda t: 10, 0: lambda t: 10},
            3: {0: lambda t: 40, 2: lambda t: 10}
        }
        
        def time_dependent_travel_times(graph, start_node, end_node, departure_time):
            return graph[start_node][end_node](departure_time)
        
        delivery_tasks = [(1, 3, 0, 100)]  # Direct path: 0->1->3->0 = 90
        # Optimal path might be 0->2->1->3->0 = 50
        depot_location = 0
        max_flight_time = 100
        
        routes = find_optimal_routes(graph, delivery_tasks, depot_location, max_flight_time, time_dependent_travel_times)
        
        self.assertEqual(len(routes), 1)
        # The actual path depends on the implementation, but it should be valid
        for i in range(len(routes[0]) - 1):
            self.assertIn(routes[0][i+1], graph[routes[0][i]])
    
    def test_large_scale_scenario(self):
        # Create a larger graph to test scalability
        import random
        random.seed(42)  # For reproducibility
        
        num_nodes = 50
        graph = {i: {} for i in range(num_nodes)}
        
        # Connect nodes with random travel times
        for i in range(num_nodes):
            for j in range(num_nodes):
                if i != j and random.random() < 0.2:  # 20% chance of connection
                    base_time = random.randint(10, 50)
                    graph[i][j] = lambda t, base=base_time: base + (t % 3600) // 600
        
        def time_dependent_travel_times(graph, start_node, end_node, departure_time):
            if end_node in graph[start_node]:
                return graph[start_node][end_node](departure_time)
            return float('inf')  # No direct connection
        
        # Generate a few random delivery tasks
        delivery_tasks = []
        for _ in range(5):
            pickup = random.randint(1, num_nodes - 1)
            delivery = random.randint(1, num_nodes - 1)
            while delivery == pickup:
                delivery = random.randint(1, num_nodes - 1)
            
            start_time = random.randint(0, 36000)
            end_time = start_time + random.randint(3600, 7200)
            
            delivery_tasks.append((pickup, delivery, start_time, end_time))
        
        depot_location = 0
        max_flight_time = 500
        
        # This test just checks that the function doesn't crash with a larger input
        # and returns a result in a reasonable time
        try:
            routes = find_optimal_routes(graph, delivery_tasks, depot_location, max_flight_time, time_dependent_travel_times)
            # We don't assert anything specific about the routes
        except Exception as e:
            self.fail(f"find_optimal_routes raised an exception: {e}")


if __name__ == '__main__':
    unittest.main()