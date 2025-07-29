import unittest
from exit_placement import min_new_exits

class ExitPlacementTest(unittest.TestCase):
    def test_example_case(self):
        # Provided example test case
        N = 3
        hub_locations = [10, 30, 50]
        service_ranges = [5, 10, 15]
        M = 5
        town_locations = [5, 20, 40, 60, 70]
        expected = 2
        result = min_new_exits(N, hub_locations, service_ranges, M, town_locations)
        self.assertEqual(result, expected)

    def test_all_towns_served(self):
        # Every town falls within the service range of some existing hub.
        N = 2
        hub_locations = [10, 50]
        service_ranges = [15, 20]
        M = 4
        town_locations = [5, 20, 40, 60]
        # Town at 5 is covered by hub 10 (abs(5-10)=5<=15)
        # Town at 20 is covered by hub 10 (abs(20-10)=10<=15)
        # Town at 40 is covered by hub 50 (abs(40-50)=10<=20)
        # Town at 60 is covered by hub 50 (abs(60-50)=10<=20)
        expected = 0
        result = min_new_exits(N, hub_locations, service_ranges, M, town_locations)
        self.assertEqual(result, expected)

    def test_edge_on_boundary(self):
        # Towns exactly on the edge of a hub's range.
        N = 2
        hub_locations = [100, 200]
        service_ranges = [50, 50]
        M = 4
        town_locations = [50, 150, 250, 201]
        # Town 50 is 50 away from hub 100 and is covered.
        # Town 150 is 50 away from hub 100 or 50 away from hub 200 and is covered.
        # Town 250 is 50 away from hub 200 and is covered.
        # Town 201 is 1 away from hub 200 and is covered.
        expected = 0
        result = min_new_exits(N, hub_locations, service_ranges, M, town_locations)
        self.assertEqual(result, expected)

    def test_new_exits_required(self):
        # Some towns require new exits
        N = 3
        hub_locations = [100, 300, 500]
        service_ranges = [30, 40, 50]
        M = 6
        town_locations = [20, 90, 350, 480, 560, 600]
        # Analysis:
        # Town 20: Nearest hub 100 distance 80 > 30, new exit needed.
        # Town 90: Nearest hub 100 distance 10 <= 30, served.
        # Town 350: Nearest hub 300 or 500, distance 50 which is > 40 for hub 300, and 150 > 50 for hub 500, new exit needed.
        # Town 480: Nearest hub 500 distance 20 <= 50, served.
        # Town 560: Nearest hub 500 distance 60 > 50, new exit needed.
        # Town 600: Nearest hub 500 distance 100 > 50, new exit needed.
        expected = 4
        result = min_new_exits(N, hub_locations, service_ranges, M, town_locations)
        self.assertEqual(result, expected)

    def test_large_gap_between_hubs_and_towns(self):
        # Test case with large differences: many towns far from any hubs.
        N = 2
        hub_locations = [0, 1000]
        service_ranges = [10, 10]
        M = 5
        town_locations = [50, 150, 300, 700, 950]
        # None will be served by the existing hubs, all require new exits.
        expected = 5
        result = min_new_exits(N, hub_locations, service_ranges, M, town_locations)
        self.assertEqual(result, expected)

if __name__ == '__main__':
    unittest.main()