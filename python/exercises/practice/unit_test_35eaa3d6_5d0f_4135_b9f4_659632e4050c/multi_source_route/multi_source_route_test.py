import unittest
from multi_source_route import find_optimal_routes


class MultiSourceRouteTest(unittest.TestCase):
    def test_basic_case(self):
        # A simple graph with 5 nodes (A, B, C, D, E)
        graph = {
            'A': {'C': 5, 'D': 8},
            'B': {'C': 6, 'E': 10},
            'C': {'D': 4, 'E': 7},
            'D': {},
            'E': {}
        }
        
        distribution_centers = {
            'A': {'vehicles': [{'capacity': 10, 'cost_per_distance': 1}, 
                             {'capacity': 10, 'cost_per_distance': 1}]},
            'B': {'vehicles': [{'capacity': 10, 'cost_per_distance': 1}]}
        }
        
        delivery_locations = {
            'C': {'demand': 5, 'time_window': (10, 15), 'waiting_cost': 0.5},
            'D': {'demand': 5, 'time_window': (12, 18), 'waiting_cost': 0.5},
            'E': {'demand': 3, 'time_window': (14, 16), 'waiting_cost': 0.5}
        }
        
        routes = find_optimal_routes(graph, distribution_centers, delivery_locations)
        
        # Check if we have routes for all vehicles
        self.assertEqual(len(routes), 3)
        
        # Check if all delivery locations are covered
        delivered_locations = set()
        for route in routes:
            delivered_locations.update(route['route'][1:])  # Exclude the starting point
        
        self.assertEqual(delivered_locations, {'C', 'D', 'E'})
        
        # Check if routes start from distribution centers
        for route in routes:
            self.assertIn(route['route'][0], distribution_centers.keys())
        
        # Check capacity constraints
        for route in routes:
            vehicle = route['vehicle']
            total_demand = sum(delivery_locations[loc]['demand'] for loc in route['route'][1:])
            self.assertLessEqual(total_demand, vehicle['capacity'])
        
        # Check time windows
        for route in routes:
            for i, loc in enumerate(route['route'][1:], 1):
                start_time = route['start_times'][i]
                time_window = delivery_locations[loc]['time_window']
                self.assertLessEqual(time_window[0], start_time)
                self.assertLessEqual(start_time, time_window[1])

    def test_no_feasible_solution(self):
        # Graph where some locations are unreachable
        graph = {
            'A': {'C': 5},
            'B': {'E': 10},
            'C': {},
            'D': {},
            'E': {}
        }
        
        distribution_centers = {
            'A': {'vehicles': [{'capacity': 10, 'cost_per_distance': 1}]},
            'B': {'vehicles': [{'capacity': 10, 'cost_per_distance': 1}]}
        }
        
        delivery_locations = {
            'C': {'demand': 5, 'time_window': (10, 15), 'waiting_cost': 0.5},
            'D': {'demand': 5, 'time_window': (12, 18), 'waiting_cost': 0.5},
            'E': {'demand': 3, 'time_window': (14, 16), 'waiting_cost': 0.5}
        }
        
        routes = find_optimal_routes(graph, distribution_centers, delivery_locations)
        
        # D should be unreachable
        all_delivered = set()
        for route in routes:
            all_delivered.update(route['route'][1:])
        
        self.assertNotIn('D', all_delivered)

    def test_capacity_constraints(self):
        graph = {
            'A': {'C': 5, 'D': 8, 'E': 10},
            'B': {},
            'C': {},
            'D': {},
            'E': {}
        }
        
        distribution_centers = {
            'A': {'vehicles': [{'capacity': 6, 'cost_per_distance': 1}]},
            'B': {'vehicles': []}
        }
        
        delivery_locations = {
            'C': {'demand': 5, 'time_window': (10, 15), 'waiting_cost': 0.5},
            'D': {'demand': 5, 'time_window': (12, 18), 'waiting_cost': 0.5},
            'E': {'demand': 3, 'time_window': (14, 16), 'waiting_cost': 0.5}
        }
        
        routes = find_optimal_routes(graph, distribution_centers, delivery_locations)
        
        # Check that capacity constraints are respected
        for route in routes:
            vehicle = route['vehicle']
            total_demand = sum(delivery_locations[loc]['demand'] for loc in route['route'][1:])
            self.assertLessEqual(total_demand, vehicle['capacity'])
        
        # Check that not all locations can be served due to capacity constraints
        all_delivered = set()
        for route in routes:
            all_delivered.update(route['route'][1:])
        
        self.assertLess(len(all_delivered), 3)

    def test_time_windows(self):
        graph = {
            'A': {'C': 5, 'D': 15, 'E': 20},
            'B': {},
            'C': {},
            'D': {},
            'E': {}
        }
        
        distribution_centers = {
            'A': {'vehicles': [{'capacity': 20, 'cost_per_distance': 1}]},
            'B': {'vehicles': []}
        }
        
        delivery_locations = {
            'C': {'demand': 5, 'time_window': (10, 15), 'waiting_cost': 0.5},
            'D': {'demand': 5, 'time_window': (12, 14), 'waiting_cost': 0.5},  # Tight time window
            'E': {'demand': 3, 'time_window': (14, 16), 'waiting_cost': 0.5}
        }
        
        routes = find_optimal_routes(graph, distribution_centers, delivery_locations)
        
        # Check time window compliance
        for route in routes:
            for i, loc in enumerate(route['route'][1:], 1):
                start_time = route['start_times'][i]
                time_window = delivery_locations[loc]['time_window']
                self.assertLessEqual(time_window[0], start_time)
                self.assertLessEqual(start_time, time_window[1])
        
        # Check if D is included (it has a tight time window and might be hard to reach)
        all_delivered = set()
        for route in routes:
            all_delivered.update(route['route'][1:])
        
        if 'D' in all_delivered:
            # If D is included, verify its time window is respected
            for route in routes:
                if 'D' in route['route']:
                    idx = route['route'].index('D')
                    start_time = route['start_times'][idx]
                    self.assertGreaterEqual(start_time, 12)
                    self.assertLessEqual(start_time, 14)

    def test_optimization_of_costs(self):
        graph = {
            'A': {'C': 5, 'D': 8},
            'B': {'C': 6, 'D': 10},
            'C': {},
            'D': {}
        }
        
        distribution_centers = {
            'A': {'vehicles': [{'capacity': 10, 'cost_per_distance': 1}]},
            'B': {'vehicles': [{'capacity': 10, 'cost_per_distance': 0.8}]}  # Lower cost per distance
        }
        
        delivery_locations = {
            'C': {'demand': 5, 'time_window': (10, 15), 'waiting_cost': 0.5},
            'D': {'demand': 5, 'time_window': (12, 18), 'waiting_cost': 0.5}
        }
        
        routes = find_optimal_routes(graph, distribution_centers, delivery_locations)
        
        # We expect the vehicle from B to be used because it has a lower cost per distance
        used_centers = {route['route'][0] for route in routes}
        self.assertIn('B', used_centers)
        
        # Calculate the total cost
        total_cost = 0
        for route in routes:
            total_cost += route['total_cost']
        
        # The optimal solution should use B's vehicle for at least one delivery
        # due to its lower cost per distance
        self.assertGreater(len([r for r in routes if r['route'][0] == 'B']), 0)

    def test_large_graph(self):
        # Create a larger graph to test scalability
        graph = {}
        for i in range(100):
            node = f'N{i}'
            graph[node] = {}
            for j in range(100):
                if i != j:
                    graph[node][f'N{j}'] = abs(i - j)  # Distance is the absolute difference
        
        distribution_centers = {
            'N0': {'vehicles': [{'capacity': 50, 'cost_per_distance': 1}]},
            'N49': {'vehicles': [{'capacity': 50, 'cost_per_distance': 1}]},
            'N99': {'vehicles': [{'capacity': 50, 'cost_per_distance': 1}]}
        }
        
        delivery_locations = {}
        for i in range(1, 20):
            if i % 2 == 0:  # Only use even-numbered nodes as delivery locations
                node = f'N{i}'
                delivery_locations[node] = {
                    'demand': i % 10 + 1,  # Demand between 1 and 10
                    'time_window': (10 + i, 20 + i),  # Different time windows
                    'waiting_cost': 0.5
                }
        
        routes = find_optimal_routes(graph, distribution_centers, delivery_locations)
        
        # Just check that we get a result without timeout
        self.assertIsNotNone(routes)
        
        # Check if all delivery locations are covered
        all_delivered = set()
        for route in routes:
            all_delivered.update(route['route'][1:])
        
        self.assertEqual(all_delivered, set(delivery_locations.keys()))

    def test_waiting_costs(self):
        graph = {
            'A': {'C': 5, 'D': 10},
            'B': {},
            'C': {'D': 4},
            'D': {}
        }
        
        distribution_centers = {
            'A': {'vehicles': [{'capacity': 10, 'cost_per_distance': 1}]},
            'B': {'vehicles': []}
        }
        
        delivery_locations = {
            'C': {'demand': 5, 'time_window': (10, 15), 'waiting_cost': 2.0},  # High waiting cost
            'D': {'demand': 5, 'time_window': (20, 25), 'waiting_cost': 0.1}   # Low waiting cost
        }
        
        routes = find_optimal_routes(graph, distribution_centers, delivery_locations)
        
        # If both C and D are in the same route, C should be visited first to minimize waiting costs
        for route in routes:
            if 'C' in route['route'] and 'D' in route['route']:
                c_index = route['route'].index('C')
                d_index = route['route'].index('D')
                self.assertLess(c_index, d_index)


if __name__ == '__main__':
    unittest.main()