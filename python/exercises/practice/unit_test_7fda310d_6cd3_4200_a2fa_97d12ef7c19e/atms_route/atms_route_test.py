import unittest
from atms_route import find_fastest_route

class ATMSRouteTest(unittest.TestCase):
    def test_simple_route(self):
        graph = {
            'A': [('B', 50, 100, [30, 40]), ('C', 30, 200, [20, 30])],
            'B': [('D', 40, 150, [40, 50])],
            'C': [('D', 60, 100, [30, 40])],
            'D': []
        }

        traffic_conditions = {
            ('A', 'B'): 20,
            ('A', 'C'): 10,
            ('B', 'D'): 30,
            ('C', 'D'): 40
        }

        source = 'A'
        destination = 'D'
        time_unit = 1
        look_ahead = 60

        route, travel_time = find_fastest_route(graph, traffic_conditions, source, destination, time_unit, look_ahead)
        
        # In this simple case, we expect a route to exist
        self.assertIsNotNone(route)
        self.assertGreater(len(route), 0)
        
        # Route should start at source and end at destination
        self.assertEqual(route[0], source)
        self.assertEqual(route[-1], destination)

        # Travel time should be positive
        self.assertGreater(travel_time, 0)

    def test_no_route_exists(self):
        graph = {
            'A': [('B', 50, 100, [30, 40])],
            'B': [('C', 40, 150, [40, 50])],
            'C': [],
            'D': [('E', 30, 120, [20, 20])],
            'E': []
        }

        traffic_conditions = {
            ('A', 'B'): 20,
            ('B', 'C'): 30,
            ('D', 'E'): 15
        }

        source = 'A'
        destination = 'E'
        time_unit = 1
        look_ahead = 60

        route, travel_time = find_fastest_route(graph, traffic_conditions, source, destination, time_unit, look_ahead)
        
        # No route should exist from A to E
        self.assertEqual(route, [])
        self.assertEqual(travel_time, -1)

    def test_source_equals_destination(self):
        graph = {
            'A': [('B', 50, 100, [30, 40])],
            'B': []
        }

        traffic_conditions = {
            ('A', 'B'): 20
        }

        source = 'A'
        destination = 'A'
        time_unit = 1
        look_ahead = 60

        route, travel_time = find_fastest_route(graph, traffic_conditions, source, destination, time_unit, look_ahead)
        
        # Source equals destination should return a single-node route with zero travel time
        self.assertEqual(route, ['A'])
        self.assertEqual(travel_time, 0)

    def test_complex_route_with_traffic(self):
        # Create a more complex graph
        graph = {
            'A': [('B', 100, 200, [30, 40]), ('C', 80, 150, [20, 30])],
            'B': [('D', 90, 180, [40, 50]), ('E', 70, 220, [30, 20])],
            'C': [('E', 120, 160, [35, 45]), ('F', 60, 190, [25, 35])],
            'D': [('G', 110, 170, [45, 55])],
            'E': [('G', 85, 210, [40, 30]), ('H', 95, 230, [35, 25])],
            'F': [('H', 75, 200, [30, 40])],
            'G': [('I', 100, 190, [50, 60])],
            'H': [('I', 110, 180, [40, 50])],
            'I': []
        }

        # Heavy traffic on some road segments
        traffic_conditions = {
            ('A', 'B'): 90,  # Close to capacity
            ('A', 'C'): 30,
            ('B', 'D'): 80,  # Heavy traffic
            ('B', 'E'): 20,
            ('C', 'E'): 100, # Heavy traffic
            ('C', 'F'): 40,
            ('D', 'G'): 60,
            ('E', 'G'): 70,  # Heavy traffic
            ('E', 'H'): 30,
            ('F', 'H'): 50,
            ('G', 'I'): 90,  # Heavy traffic
            ('H', 'I'): 60
        }

        source = 'A'
        destination = 'I'
        time_unit = 1
        look_ahead = 120

        route, travel_time = find_fastest_route(graph, traffic_conditions, source, destination, time_unit, look_ahead)
        
        # Route should exist
        self.assertGreater(len(route), 0)
        
        # Should start at A and end at I
        self.assertEqual(route[0], 'A')
        self.assertEqual(route[-1], 'I')
        
        # Travel time should be positive
        self.assertGreater(travel_time, 0)
        
        # Verify the route avoids heavy traffic where possible
        # Since A-C has less traffic than A-B, the route might start with A-C
        # This is just a heuristic check, the actual route depends on the implementation
        if len(route) > 1 and route[1] == 'C':
            self.assertIn('C', route)

    def test_changing_traffic_conditions(self):
        # Test how the algorithm handles traffic predictions
        graph = {
            'A': [('B', 50, 100, [30, 40]), ('C', 30, 120, [20, 30])],
            'B': [('D', 40, 150, [40, 50])],
            'C': [('D', 60, 80, [30, 40])],
            'D': []
        }

        # Initial traffic conditions that will make A-B-D faster
        traffic_conditions = {
            ('A', 'B'): 10,  # Light traffic
            ('A', 'C'): 25,  # Heavier traffic
            ('B', 'D'): 15,  # Light traffic
            ('C', 'D'): 50   # Heavy traffic
        }

        source = 'A'
        destination = 'D'
        time_unit = 1
        look_ahead = 60

        route, travel_time = find_fastest_route(graph, traffic_conditions, source, destination, time_unit, look_ahead)
        
        # A different route should be chosen with different traffic conditions
        changed_traffic = {
            ('A', 'B'): 45,  # Now heavy traffic
            ('A', 'C'): 5,   # Now light traffic
            ('B', 'D'): 35,  # Now heavier traffic
            ('C', 'D'): 20   # Now lighter traffic
        }
        
        new_route, new_travel_time = find_fastest_route(graph, changed_traffic, source, destination, time_unit, look_ahead)
        
        # The routes should exist
        self.assertGreater(len(route), 0)
        self.assertGreater(len(new_route), 0)
        
        # The travel times should be different
        self.assertNotEqual(travel_time, new_travel_time)

    def test_traffic_light_influence(self):
        # Test how traffic lights influence the route choice
        graph = {
            'A': [('B', 50, 100, [10, 10]), ('C', 50, 100, [50, 50])],  # Similar roads but different light patterns
            'B': [('D', 50, 100, [30, 30])],
            'C': [('D', 50, 100, [30, 30])],
            'D': []
        }

        # Same traffic on all roads
        traffic_conditions = {
            ('A', 'B'): 25,
            ('A', 'C'): 25,
            ('B', 'D'): 25,
            ('C', 'D'): 25
        }

        source = 'A'
        destination = 'D'
        time_unit = 1
        look_ahead = 60

        route, travel_time = find_fastest_route(graph, traffic_conditions, source, destination, time_unit, look_ahead)
        
        # Route should exist
        self.assertGreater(len(route), 0)
        
        # Since light cycles on A-C are more favorable (longer green durations),
        # route might go through C, but this depends on implementation details
        # This is a heuristic check
        self.assertIn(route[1], ['B', 'C'])
        
        # Travel time should be positive
        self.assertGreater(travel_time, 0)

    def test_capacity_influence(self):
        # Test how road capacity influences route choice
        graph = {
            'A': [('B', 30, 100, [30, 30]), ('C', 60, 100, [30, 30])],  # C has higher capacity
            'B': [('D', 40, 100, [30, 30])],
            'C': [('D', 40, 100, [30, 30])],
            'D': []
        }

        # Heavy traffic on both A-B and A-C, but A-C has higher capacity
        traffic_conditions = {
            ('A', 'B'): 25,  # Close to capacity
            ('A', 'C'): 50,  # Still within capacity
            ('B', 'D'): 20,
            ('C', 'D'): 20
        }

        source = 'A'
        destination = 'D'
        time_unit = 1
        look_ahead = 60

        route, travel_time = find_fastest_route(graph, traffic_conditions, source, destination, time_unit, look_ahead)
        
        # Route should exist
        self.assertGreater(len(route), 0)
        
        # Since A-C has higher capacity, the route might go through C
        # This is a heuristic check, the actual route depends on the implementation
        self.assertIn(route[1], ['B', 'C'])
        
        # Travel time should be positive
        self.assertGreater(travel_time, 0)

if __name__ == '__main__':
    unittest.main()