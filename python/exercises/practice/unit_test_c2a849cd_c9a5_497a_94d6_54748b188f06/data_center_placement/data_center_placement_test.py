import unittest
import math
from data_center_placement.data_center_placement import select_data_centers

class DataCenterPlacementTest(unittest.TestCase):
    def compute_average_latency(self, selected_ids, locations, regions):
        # For each region, compute the minimum available latency from selected data centers.
        region_latency = {}
        for region_id, demand in regions:
            min_latency = float('inf')
            for loc in locations:
                loc_id, _, latency_profiles = loc
                if loc_id in selected_ids and region_id in latency_profiles:
                    min_latency = min(min_latency, latency_profiles[region_id])
            region_latency[region_id] = min_latency
        total_demand = sum(demand for _, demand in regions)
        weighted_latency = sum(demand * (lat if lat != float('inf') else 1e9) 
                               for (region_id, demand) in regions 
                               for lat in [region_latency[region_id]])
        average_latency = weighted_latency / total_demand if total_demand > 0 else float('inf')
        return average_latency

    def compute_total_cost(self, selected_ids, locations):
        cost = 0
        for loc in locations:
            loc_id, build_cost, _ = loc
            if loc_id in selected_ids:
                cost += build_cost
        return cost

    def test_single_location(self):
        locations = [
            (1, 500, {"us-east": 30, "us-west": 70}),
        ]
        regions = [
            ("us-east", 1000),
            ("us-west", 500)
        ]
        budget = 1000
        latency_threshold = 50
        selected = select_data_centers(locations, regions, budget, latency_threshold)
        total_cost = self.compute_total_cost(selected, locations)
        self.assertLessEqual(total_cost, budget, "Total build cost exceeds budget")
        average_latency = self.compute_average_latency(selected, locations, regions)
        self.assertLessEqual(average_latency, latency_threshold, "Average latency exceeds threshold")
        # In this simple scenario, the only data center should be chosen.
        self.assertEqual(selected, [1])

    def test_no_solution_due_to_budget(self):
        locations = [
            (1, 1200, {"us-east": 30}),
            (2, 1500, {"us-east": 20})
        ]
        regions = [
            ("us-east", 1000)
        ]
        budget = 1000  # Not enough budget to build any center.
        latency_threshold = 50
        selected = select_data_centers(locations, regions, budget, latency_threshold)
        self.assertEqual(selected, [], "Expected no solution due to insufficient budget")

    def test_no_solution_due_to_latency(self):
        locations = [
            (1, 500, {"us-east": 100}),
            (2, 300, {"us-east": 90})
        ]
        regions = [
            ("us-east", 1000)
        ]
        budget = 1000
        latency_threshold = 50  # Latency constraint cannot be met.
        selected = select_data_centers(locations, regions, budget, latency_threshold)
        self.assertEqual(selected, [], "Expected no solution due to latency constraint violation")

    def test_multiple_locations(self):
        locations = [
            (1, 400, {"us-east": 40, "us-west": 80}),
            (2, 600, {"us-east": 35, "us-west": 75, "eu-central": 90}),
            (3, 300, {"eu-central": 50, "asia": 120}),
            (4, 500, {"us-west": 60, "asia": 110}),
        ]
        regions = [
            ("us-east", 1000),
            ("us-west", 800),
            ("eu-central", 600),
            ("asia", 400)
        ]
        budget = 1500
        latency_threshold = 70
        selected = select_data_centers(locations, regions, budget, latency_threshold)
        total_cost = self.compute_total_cost(selected, locations)
        self.assertLessEqual(total_cost, budget, "Total build cost exceeds budget")
        average_latency = self.compute_average_latency(selected, locations, regions)
        self.assertLessEqual(average_latency, latency_threshold, "Average latency exceeds threshold")
        # Verify that selected locations exist in the provided list.
        available_ids = {loc[0] for loc in locations}
        for loc_id in selected:
            self.assertIn(loc_id, available_ids)

    def test_multiple_valid_solutions(self):
        locations = [
            (1, 400, {"region1": 40, "region2": 80}),
            (2, 500, {"region1": 30, "region2": 90}),
            (3, 300, {"region1": 50, "region2": 70}),
        ]
        regions = [
            ("region1", 500),
            ("region2", 500)
        ]
        budget = 1000
        latency_threshold = 60
        selected = select_data_centers(locations, regions, budget, latency_threshold)
        total_cost = self.compute_total_cost(selected, locations)
        self.assertLessEqual(total_cost, budget, "Total build cost exceeds budget")
        average_latency = self.compute_average_latency(selected, locations, regions)
        self.assertLessEqual(average_latency, latency_threshold, "Average latency exceeds threshold")
        # Verify that selected IDs are among the candidate locations.
        available_ids = {1, 2, 3}
        for loc_id in selected:
            self.assertIn(loc_id, available_ids)

if __name__ == '__main__':
    unittest.main()