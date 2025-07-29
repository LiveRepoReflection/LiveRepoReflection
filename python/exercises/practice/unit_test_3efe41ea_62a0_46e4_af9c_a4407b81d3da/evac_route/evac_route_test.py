import unittest
from evac_route import optimal_evacuation

class EvacuationRouteTest(unittest.TestCase):
    def test_simple_evacuation(self):
        locations = [(1, 100), (2, 50), (3, 75)]
        evacuation_centers = [(4, 150), (5, 100)]
        roads = [(1, 2, 10), (2, 3, 5), (1, 4, 15), (2, 4, 12), (3, 5, 8), (4, 5, 20)]
        
        result = optimal_evacuation(locations, evacuation_centers, roads)
        
        # Verify all residents are evacuated
        assigned_locations = set(result.keys())
        self.assertEqual(assigned_locations, {1, 2, 3})
        
        # Verify center capacities are not exceeded
        center_4_total = sum(loc[1] for loc in locations if loc[0] in result and result[loc[0]] == 4)
        center_5_total = sum(loc[1] for loc in locations if loc[0] in result and result[loc[0]] == 5)
        
        self.assertLessEqual(center_4_total, 150)
        self.assertLessEqual(center_5_total, 100)

    def test_insufficient_capacity(self):
        locations = [(1, 100), (2, 50), (3, 75)]
        evacuation_centers = [(4, 100), (5, 50)]  # Total capacity 150, need 225
        roads = [(1, 2, 10), (2, 3, 5), (1, 4, 15), (2, 4, 12), (3, 5, 8), (4, 5, 20)]
        
        result = optimal_evacuation(locations, evacuation_centers, roads)
        self.assertIsNone(result)

    def test_disconnected_graph(self):
        locations = [(1, 100), (2, 50), (3, 75)]
        evacuation_centers = [(4, 150), (5, 100)]
        roads = [(1, 2, 10), (1, 4, 15), (2, 4, 12), (4, 5, 20)]  # No path from 3 to any center
        
        result = optimal_evacuation(locations, evacuation_centers, roads)
        self.assertIsNone(result)

    def test_empty_inputs(self):
        # No locations
        self.assertEqual(optimal_evacuation([], [(1, 100)], [(1, 2, 5)]), {})
        
        # No centers
        self.assertIsNone(optimal_evacuation([(1, 50)], [], [(1, 2, 5)]))
        
        # No roads
        self.assertIsNone(optimal_evacuation([(1, 50)], [(2, 100)], []))

    def test_large_graph(self):
        # Create a larger test case
        locations = [(i, 10) for i in range(1, 101)]  # 100 locations with 10 residents each
        evacuation_centers = [(i, 200) for i in range(101, 106)]  # 5 centers with 200 capacity each
        
        # Create a grid-like graph
        roads = []
        for i in range(1, 101):
            # Connect each location to the next location
            if i < 100:
                roads.append((i, i+1, 5))
            # Connect each location to the location below it (in a 10x10 grid)
            if i <= 90:
                roads.append((i, i+10, 5))
        
        # Connect some locations to evacuation centers
        roads.extend([(1, 101, 10), (25, 102, 15), (50, 103, 10), (75, 104, 15), (100, 105, 10)])
        
        result = optimal_evacuation(locations, evacuation_centers, roads)
        
        # Verify all locations are assigned
        self.assertEqual(len(result), 100)
        
        # Verify center capacities are not exceeded
        center_counts = {}
        for center_id in range(101, 106):
            center_counts[center_id] = 0
            
        for loc_id, center_id in result.items():
            center_counts[center_id] += 10  # Each location has 10 residents
            
        for center_id, count in center_counts.items():
            self.assertLessEqual(count, 200)

    def test_optimal_assignment(self):
        locations = [(1, 100), (2, 50)]
        evacuation_centers = [(3, 150), (4, 150)]
        roads = [(1, 3, 10), (1, 4, 20), (2, 3, 30), (2, 4, 5)]
        
        # The optimal assignment would be: 
        # Location 1 (100 residents) to Center 3 (distance 10) = 1000
        # Location 2 (50 residents) to Center 4 (distance 5) = 250
        # Total evacuation time: 1250
        
        result = optimal_evacuation(locations, evacuation_centers, roads)
        
        # Calculate the total evacuation time
        evacuation_time = 0
        for loc_id, center_id in result.items():
            loc_pop = next(loc[1] for loc in locations if loc[0] == loc_id)
            relevant_roads = [r for r in roads if (r[0] == loc_id and r[1] == center_id) or 
                                               (r[0] == center_id and r[1] == loc_id)]
            if relevant_roads:
                evacuation_time += loc_pop * relevant_roads[0][2]
        
        self.assertLessEqual(evacuation_time, 1250)  # Should be optimal or close to optimal

    def test_zero_residents_or_capacity(self):
        # Location with zero residents
        locations = [(1, 0), (2, 50)]
        evacuation_centers = [(3, 100)]
        roads = [(1, 3, 10), (2, 3, 5)]
        
        result = optimal_evacuation(locations, evacuation_centers, roads)
        self.assertEqual(result, {1: 3, 2: 3})  # Still assign location 1 even though it has 0 residents
        
        # Center with zero capacity
        locations = [(1, 100), (2, 50)]
        evacuation_centers = [(3, 0), (4, 150)]
        roads = [(1, 3, 10), (1, 4, 20), (2, 3, 5), (2, 4, 10)]
        
        result = optimal_evacuation(locations, evacuation_centers, roads)
        self.assertEqual(set(result.values()), {4})  # Only center 4 should be used

if __name__ == '__main__':
    unittest.main()