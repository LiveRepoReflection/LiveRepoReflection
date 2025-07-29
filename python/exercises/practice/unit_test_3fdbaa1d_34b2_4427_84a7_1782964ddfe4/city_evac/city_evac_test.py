import unittest
from city_evac import min_evacuation_time

class CityEvacTest(unittest.TestCase):
    def test_no_population(self):
        # Single node that is also a safe zone, no one to evacuate.
        N = 1
        edges = []
        population = [0]
        safe_zones = [(0, 0)]
        # Already safe and no one to evacuate, expect time 0.
        self.assertEqual(min_evacuation_time(N, edges, population, safe_zones), 0)

    def test_single_edge_sufficient_capacity(self):
        # Two nodes: node 1 has 10 people, safe zone at node 0 with capacity 10.
        # One edge from 1 to 0 with travel time 5 and capacity 15.
        N = 2
        edges = [(1, 0, 5, 15)]
        population = [0, 10]
        safe_zones = [(0, 10)]
        # All 10 evacuees can move at once taking 5 time units.
        self.assertEqual(min_evacuation_time(N, edges, population, safe_zones), 5)

    def test_single_edge_insufficient_road_capacity(self):
        # Two nodes: node 1 has 15 people, safe zone at node 0 with capacity 15.
        # One edge from 1 to 0 with travel time 5 and capacity 5.
        N = 2
        edges = [(1, 0, 5, 5)]
        population = [0, 15]
        safe_zones = [(0, 15)]
        # With edge capacity of 5, evacuees must be split into three batches:
        # Batch 1 departs at time 0 and arrives at time 5,
        # Batch 2 departs at time 1 and arrives at time 6,
        # Batch 3 departs at time 2 and arrives at time 7.
        # Hence, the evacuation is complete at time 7.
        self.assertEqual(min_evacuation_time(N, edges, population, safe_zones), 7)

    def test_multiple_paths_and_safe_zones(self):
        # Four nodes:
        # - Node 0 and node 3 are safe zones with capacities 10 each.
        # - Node 1 has 10 people and node 2 has 5 people.
        # Two possible routes to safe zones.
        N = 4
        # Edges: (source, destination, travel time, road capacity)
        edges = [
            (1, 0, 2, 5),  # Primary route from node 1 to safe zone at 0.
            (1, 3, 3, 3),  # Alternative route from node 1 to safe zone at 3.
            (2, 0, 4, 10), # Direct route from node 2 to safe zone at 0.
            (2, 3, 2, 2)   # Direct route from node 2 to safe zone at 3.
        ]
        population = [0, 10, 5, 0]
        safe_zones = [(0, 10), (3, 10)]
        # An optimal strategy might use both routes:
        # For node 1, send 5 via (1,0) arriving at time 2 and 5 via (1,3) arriving at time 3.
        # For node 2, send all 5 via the faster route (2,3) arriving at time 2 (if capacity allows)
        # or split between routes if necessary.
        # The overall evacuation is complete by time 4.
        self.assertEqual(min_evacuation_time(N, edges, population, safe_zones), 4)

    def test_unreachable_safe_zone(self):
        # Two nodes: node 1 has 10 people, safe zone at node 0 with capacity 10.
        # But there is no edge connecting node 1 to node 0.
        N = 2
        edges = []  # No road from node 1 to node 0.
        population = [0, 10]
        safe_zones = [(0, 10)]
        self.assertEqual(min_evacuation_time(N, edges, population, safe_zones), -1)

    def test_inadequate_safe_zone_capacity(self):
        # Three nodes: node 1 and node 2 have populations, but safe zones' total capacity is insufficient.
        N = 3
        edges = [
            (1, 0, 3, 10),
            (2, 0, 4, 10)
        ]
        population = [0, 8, 5]  # Total population = 13
        safe_zones = [(0, 12)]  # Capacity less than total population.
        self.assertEqual(min_evacuation_time(N, edges, population, safe_zones), -1)

if __name__ == '__main__':
    unittest.main()