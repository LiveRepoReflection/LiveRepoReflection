import unittest
import math
from edge_router_placement import optimize_router_placement


class EdgeRouterPlacementTest(unittest.TestCase):
    def test_simple_case(self):
        """Basic test with a small input where a solution is possible."""
        user_locations = [
            (40.7128, -74.0060),  # New York
            (34.0522, -118.2437),  # Los Angeles
            (41.8781, -87.6298),   # Chicago
            (29.7604, -95.3698),   # Houston
            (37.7749, -122.4194),  # San Francisco
        ]
        potential_router_locations = [
            (40.0, -75.0),         # Near New York
            (35.0, -118.0),        # Near Los Angeles
            (40.0, -88.0),         # Near Chicago
        ]
        k = 2
        max_latency = 500  # ms
        router_capacity = 3
        propagation_delay_factor = 0.2  # ms/km
        router_cost = 1000
        
        result = optimize_router_placement(
            user_locations,
            potential_router_locations,
            k,
            max_latency,
            router_capacity,
            propagation_delay_factor,
            router_cost
        )
        
        # Validate result is the right type and length
        self.assertIsInstance(result, list)
        self.assertLessEqual(len(result), k)
        
        # Validate each router index is valid
        for idx in result:
            self.assertGreaterEqual(idx, 0)
            self.assertLess(idx, len(potential_router_locations))

        # Validate all users are covered
        self.assertTrue(self._all_users_covered(
            user_locations,
            [potential_router_locations[idx] for idx in result],
            max_latency,
            propagation_delay_factor
        ))
        
        # Validate router capacity is not exceeded
        self.assertTrue(self._router_capacity_respected(
            user_locations,
            [potential_router_locations[idx] for idx in result],
            router_capacity,
            max_latency,
            propagation_delay_factor
        ))

    def test_no_solution_possible(self):
        """Test case where no solution is possible within constraints."""
        user_locations = [
            (40.7128, -74.0060),  # New York
            (34.0522, -118.2437),  # Los Angeles - far from other locations
        ]
        potential_router_locations = [
            (40.0, -75.0),  # Near New York
        ]
        k = 1
        max_latency = 100  # Very strict latency requirement
        router_capacity = 2
        propagation_delay_factor = 0.2  # ms/km
        router_cost = 1000
        
        result = optimize_router_placement(
            user_locations,
            potential_router_locations,
            k,
            max_latency,
            router_capacity,
            propagation_delay_factor,
            router_cost
        )
        
        # No solution possible should return empty list
        self.assertEqual(result, [])

    def test_capacity_constraints(self):
        """Test case where capacity constraints require more routers."""
        user_locations = [
            (40.7128, -74.0060),  # New York
            (40.7129, -74.0061),  # Very close to New York
            (40.7130, -74.0062),  # Very close to New York
            (40.7131, -74.0063),  # Very close to New York
            (40.7132, -74.0064),  # Very close to New York
        ]
        potential_router_locations = [
            (40.71, -74.00),      # Near all users
            (40.72, -74.01),      # Near all users
            (40.73, -74.02),      # Near all users
        ]
        k = 3
        max_latency = 50  # ms
        router_capacity = 2  # Only 2 users per router
        propagation_delay_factor = 0.2  # ms/km
        router_cost = 1000
        
        result = optimize_router_placement(
            user_locations,
            potential_router_locations,
            k,
            max_latency,
            router_capacity,
            propagation_delay_factor,
            router_cost
        )
        
        # We should need at least 3 routers to handle 5 users with capacity 2
        self.assertGreaterEqual(len(result), 3)

    def test_edge_case_k_equals_m(self):
        """Test when K equals M (can place routers at all potential locations)."""
        user_locations = [
            (40.7128, -74.0060),  # New York
            (34.0522, -118.2437),  # Los Angeles
            (41.8781, -87.6298),   # Chicago
        ]
        potential_router_locations = [
            (40.0, -75.0),         # Near New York
            (35.0, -118.0),        # Near Los Angeles
            (42.0, -88.0),         # Near Chicago
        ]
        k = 3  # Can use all potential locations
        max_latency = 200  # ms
        router_capacity = 1  # Only 1 user per router
        propagation_delay_factor = 0.2  # ms/km
        router_cost = 1000
        
        result = optimize_router_placement(
            user_locations,
            potential_router_locations,
            k,
            max_latency,
            router_capacity,
            propagation_delay_factor,
            router_cost
        )
        
        # Solution should include all locations if needed for coverage and capacity
        self.assertEqual(len(result), 3)
        self.assertTrue(set(result) == set(range(3)))

    def test_edge_case_k_equals_zero(self):
        """Test when K = 0 (no routers can be placed)."""
        user_locations = [
            (40.7128, -74.0060),  # New York
        ]
        potential_router_locations = [
            (40.0, -75.0),  # Near New York
        ]
        k = 0  # Cannot place any routers
        max_latency = 200  # ms
        router_capacity = 1
        propagation_delay_factor = 0.2  # ms/km
        router_cost = 1000
        
        result = optimize_router_placement(
            user_locations,
            potential_router_locations,
            k,
            max_latency,
            router_capacity,
            propagation_delay_factor,
            router_cost
        )
        
        # No solution possible with K = 0 should return empty list
        self.assertEqual(result, [])

    def test_large_input(self):
        """Test with a larger number of users and potential locations."""
        # Generate 200 users in a grid pattern
        user_locations = []
        for i in range(20):
            for j in range(10):
                user_locations.append((40.0 + 0.01 * i, -74.0 - 0.01 * j))
        
        # Generate 50 potential router locations
        potential_router_locations = []
        for i in range(10):
            for j in range(5):
                potential_router_locations.append((40.0 + 0.05 * i, -74.0 - 0.05 * j))
        
        k = 20
        max_latency = 300  # ms
        router_capacity = 15
        propagation_delay_factor = 0.2  # ms/km
        router_cost = 1000
        
        result = optimize_router_placement(
            user_locations,
            potential_router_locations,
            k,
            max_latency,
            router_capacity,
            propagation_delay_factor,
            router_cost
        )
        
        # Validate result
        self.assertIsInstance(result, list)
        self.assertLessEqual(len(result), k)
        
        # Check if all router indices are valid
        for idx in result:
            self.assertGreaterEqual(idx, 0)
            self.assertLess(idx, len(potential_router_locations))

    def test_minimum_routers_used(self):
        """Test that the algorithm minimizes the number of routers used."""
        user_locations = [
            (40.7128, -74.0060),  # New York
            (40.7129, -74.0061),  # Very close to New York
            (40.7130, -74.0062),  # Very close to New York
        ]
        potential_router_locations = [
            (40.71, -74.00),      # Near all users
            (40.72, -74.01),      # Near all users
            (40.73, -74.02),      # Near all users
        ]
        k = 3  # Allow up to 3 routers
        max_latency = 50  # ms
        router_capacity = 3  # Can handle all users
        propagation_delay_factor = 0.2  # ms/km
        router_cost = 1000
        
        result = optimize_router_placement(
            user_locations,
            potential_router_locations,
            k,
            max_latency,
            router_capacity,
            propagation_delay_factor,
            router_cost
        )
        
        # One router should be enough given the capacity and proximity
        self.assertEqual(len(result), 1)

    def _haversine_distance(self, loc1, loc2):
        """Calculate the great-circle distance between two points."""
        # Earth radius in kilometers
        R = 6371.0
        
        # Convert latitude and longitude from degrees to radians
        lat1 = math.radians(loc1[0])
        lon1 = math.radians(loc1[1])
        lat2 = math.radians(loc2[0])
        lon2 = math.radians(loc2[1])
        
        # Haversine formula
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        distance = R * c
        
        return distance

    def _all_users_covered(self, users, routers, max_latency, prop_delay_factor):
        """Check if all users are covered by at least one router within max_latency."""
        for user in users:
            min_latency = float('inf')
            for router in routers:
                distance = self._haversine_distance(user, router)
                latency = distance * prop_delay_factor
                min_latency = min(min_latency, latency)
            
            if min_latency > max_latency:
                return False
        
        return True

    def _router_capacity_respected(self, users, routers, capacity, max_latency, prop_delay_factor):
        """Check if router capacity constraints are respected."""
        # Assign each user to the nearest router
        router_assignments = [0] * len(routers)
        
        for user in users:
            min_latency = float('inf')
            nearest_router_idx = -1
            
            for i, router in enumerate(routers):
                distance = self._haversine_distance(user, router)
                latency = distance * prop_delay_factor
                
                if latency <= max_latency and latency < min_latency:
                    min_latency = latency
                    nearest_router_idx = i
            
            if nearest_router_idx == -1:
                return False  # User not covered by any router
                
            router_assignments[nearest_router_idx] += 1
            
            if router_assignments[nearest_router_idx] > capacity:
                return False  # Router capacity exceeded
        
        return True


if __name__ == '__main__':
    unittest.main()