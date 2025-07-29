import unittest
from delivery_routes import optimize_routes
import math

def haversine(coord1, coord2):
    """
    Calculate the distance between two points on Earth using the Haversine formula.
    """
    lat1, lon1 = coord1
    lat2, lon2 = coord2
    R = 6371  # Radius of Earth in kilometers

    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])

    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))

    return R * c

class DeliveryRoutesTest(unittest.TestCase):
    def check_solution_validity(self, hubs, delivery_points, max_vehicle_capacity, solution):
        """Helper to validate the solution against all constraints"""
        # Create a lookup for delivery points
        dp_lookup = {dp[0]: dp for dp in delivery_points}
        
        # Check that all served delivery points exist
        served_points = set()
        for hub_id, routes in solution.items():
            for route in routes:
                for point_id in route:
                    self.assertIn(point_id, dp_lookup, f"Non-existent delivery point {point_id} in solution")
                    served_points.add(point_id)
        
        # Check if any delivery point is served by more than one route
        self.assertEqual(len(served_points), sum(len(points) for routes in solution.values() for points in routes), 
                         "Some delivery points are served by multiple vehicles")

        # Check hub constraints
        for hub_id, routes in solution.items():
            # Find the hub
            hub = next((h for h in hubs if h[0] == hub_id), None)
            self.assertIsNotNone(hub, f"Solution references non-existent hub {hub_id}")
            
            # Check vehicle limit
            self.assertLessEqual(len(routes), hub[3], f"Hub {hub_id} exceeds vehicle limit. Has {len(routes)} routes but only {hub[3]} vehicles.")
            
            # Check capacity constraints and routes
            total_hub_demand = 0
            for route_idx, route in enumerate(routes):
                route_demand = 0
                for point_id in route:
                    point = dp_lookup[point_id]
                    route_demand += point[2]  # Add demand
                
                # Check route capacity
                self.assertLessEqual(route_demand, max_vehicle_capacity, 
                                   f"Route {route_idx} from hub {hub_id} exceeds vehicle capacity. Demand: {route_demand}, Capacity: {max_vehicle_capacity}")
                
                total_hub_demand += route_demand
            
            # Check total hub capacity
            self.assertLessEqual(total_hub_demand, hub[2], 
                               f"Hub {hub_id} exceeds total capacity. Total demand: {total_hub_demand}, Hub capacity: {hub[2]}")

    def calculate_total_distance(self, hubs, delivery_points, solution):
        """Calculate the total distance of all routes in the solution"""
        hub_lookup = {h[0]: h[1] for h in hubs}  # Map hub_id to location
        dp_lookup = {dp[0]: dp[1] for dp in delivery_points}  # Map point_id to location
        
        total_distance = 0
        for hub_id, routes in solution.items():
            hub_location = hub_lookup[hub_id]
            
            for route in routes:
                if not route:  # Skip empty routes
                    continue
                
                # Distance from hub to first delivery point
                distance = haversine(hub_location, dp_lookup[route[0]])
                
                # Add distances between consecutive delivery points
                for i in range(len(route) - 1):
                    distance += haversine(dp_lookup[route[i]], dp_lookup[route[i+1]])
                
                # Add distance from last delivery point back to hub
                distance += haversine(dp_lookup[route[-1]], hub_location)
                
                total_distance += distance
                
        return total_distance

    def test_small_example(self):
        # Example from the question
        hubs = [
            (0, (37.7749, -122.4194), 1000, 2),  # Hub 0: San Francisco, capacity 1000, 2 vehicles
            (1, (34.0522, -118.2437), 500, 1)   # Hub 1: Los Angeles, capacity 500, 1 vehicle
        ]

        delivery_points = [
            (0, (37.7833, -122.4090), 100),  # Point 0: Demand 100
            (1, (37.7950, -122.4028), 150),  # Point 1: Demand 150
            (2, (37.7730, -122.4312), 200),  # Point 2: Demand 200
            (3, (34.0600, -118.2300), 250),  # Point 3: Demand 250
            (4, (34.0400, -118.2500), 300)   # Point 4: Demand 300
        ]

        max_vehicle_capacity = 400
        
        solution = optimize_routes(hubs, delivery_points, max_vehicle_capacity)
        
        # Check that solution is not empty
        self.assertIsNotNone(solution)
        self.assertIsInstance(solution, dict)
        
        # Check solution validity
        self.check_solution_validity(hubs, delivery_points, max_vehicle_capacity, solution)
        
        # Calculate distance (not checking actual value, just ensuring calculation works)
        total_distance = self.calculate_total_distance(hubs, delivery_points, solution)
        self.assertGreaterEqual(total_distance, 0)

    def test_single_hub(self):
        # Test with a single hub and multiple delivery points
        hubs = [
            (0, (40.7128, -74.0060), 1000, 3),  # New York City
        ]

        delivery_points = [
            (0, (40.7282, -73.7949), 200),  # Point 0
            (1, (40.7300, -74.0100), 150),  # Point 1
            (2, (40.7000, -74.0200), 300),  # Point 2
            (3, (40.6892, -74.0445), 250),  # Point 3
            (4, (40.7500, -73.9800), 200),  # Point 4
            (5, (40.7400, -74.0300), 100),  # Point 5
        ]

        max_vehicle_capacity = 400
        
        solution = optimize_routes(hubs, delivery_points, max_vehicle_capacity)
        
        self.assertIsNotNone(solution)
        self.check_solution_validity(hubs, delivery_points, max_vehicle_capacity, solution)

    def test_capacity_constraints(self):
        # Test with tight capacity constraints
        hubs = [
            (0, (51.5074, -0.1278), 600, 2),  # London
        ]

        delivery_points = [
            (0, (51.5100, -0.1300), 300),  # Point 0
            (1, (51.5200, -0.1400), 300),  # Point 1
            (2, (51.5000, -0.1200), 300),  # Point 2
            (3, (51.5150, -0.1250), 300),  # Point 3
        ]

        max_vehicle_capacity = 300  # Each vehicle can only handle one delivery point
        
        solution = optimize_routes(hubs, delivery_points, max_vehicle_capacity)
        
        self.assertIsNotNone(solution)
        self.check_solution_validity(hubs, delivery_points, max_vehicle_capacity, solution)
        
        # Check that not all delivery points can be served due to hub capacity constraint
        total_served = sum(len(points) for routes in solution.values() for points in routes)
        self.assertLessEqual(total_served, 2)  # Only 2 out of 4 points can be served

    def test_multiple_hubs_overlapping_regions(self):
        # Test with multiple hubs serving overlapping regions
        hubs = [
            (0, (48.8566, 2.3522), 500, 1),  # Paris
            (1, (48.8500, 2.3400), 500, 1),  # Also close to Paris
        ]

        delivery_points = [
            (0, (48.8600, 2.3500), 100),  # Point 0
            (1, (48.8650, 2.3550), 200),  # Point 1
            (2, (48.8400, 2.3300), 150),  # Point 2
            (3, (48.8700, 2.3600), 250),  # Point 3
            (4, (48.8450, 2.3350), 300),  # Point 4
        ]

        max_vehicle_capacity = 500
        
        solution = optimize_routes(hubs, delivery_points, max_vehicle_capacity)
        
        self.assertIsNotNone(solution)
        self.check_solution_validity(hubs, delivery_points, max_vehicle_capacity, solution)

    def test_insufficient_capacity(self):
        # Test when total hub capacity is less than total demand
        hubs = [
            (0, (41.8781, -87.6298), 300, 1),  # Chicago
        ]

        delivery_points = [
            (0, (41.8800, -87.6300), 100),  # Point 0
            (1, (41.8850, -87.6350), 150),  # Point 1
            (2, (41.8700, -87.6250), 200),  # Point 2
            (3, (41.8900, -87.6400), 250),  # Point 3
        ]

        max_vehicle_capacity = 400
        
        solution = optimize_routes(hubs, delivery_points, max_vehicle_capacity)
        
        self.assertIsNotNone(solution)
        self.check_solution_validity(hubs, delivery_points, max_vehicle_capacity, solution)
        
        # Check that not all delivery points are served due to insufficient capacity
        total_served = sum(len(points) for routes in solution.values() for points in routes)
        self.assertLess(total_served, 4)

    def test_large_random_case(self):
        import random
        random.seed(42)  # For reproducible tests
        
        # Generate a medium-sized test case (not too large for unit test)
        num_hubs = 5
        num_points = 100
        
        # Generate random hubs
        hubs = []
        for i in range(num_hubs):
            lat = random.uniform(35.0, 42.0)
            lon = random.uniform(-120.0, -70.0)
            capacity = random.randint(1000, 5000)
            vehicles = random.randint(3, 10)
            hubs.append((i, (lat, lon), capacity, vehicles))
        
        # Generate random delivery points
        delivery_points = []
        for i in range(num_points):
            lat = random.uniform(35.0, 42.0)
            lon = random.uniform(-120.0, -70.0)
            demand = random.randint(50, 500)
            delivery_points.append((i, (lat, lon), demand))
        
        max_vehicle_capacity = 1000
        
        solution = optimize_routes(hubs, delivery_points, max_vehicle_capacity)
        
        self.assertIsNotNone(solution)
        self.check_solution_validity(hubs, delivery_points, max_vehicle_capacity, solution)

if __name__ == '__main__':
    unittest.main()