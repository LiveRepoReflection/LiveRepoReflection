import unittest
from evacuation_plan import evacuation_time

class TestEvacuationPlan(unittest.TestCase):
    def test_single_safe_zone(self):
        n = 4
        roads = [(0, 1, 10), (0, 2, 5), (1, 2, 15), (1, 3, 20), (2, 3, 10)]
        residents = [5, 10, 8, 0]
        safe_zones = [3]
        self.assertEqual(evacuation_time(n, roads, residents, safe_zones), 1)

    def test_multiple_safe_zones(self):
        n = 5
        roads = [(0, 1, 5), (1, 2, 10), (2, 3, 15), (3, 4, 20), (0, 4, 10)]
        residents = [20, 0, 0, 0, 0]
        safe_zones = [2, 4]
        self.assertEqual(evacuation_time(n, roads, residents, safe_zones), 2)

    def test_impossible_evacuation(self):
        n = 3
        roads = [(0, 1, 10)]
        residents = [5, 10, 15]
        safe_zones = [0]
        self.assertEqual(evacuation_time(n, roads, residents, safe_zones), -1)

    def test_large_capacity(self):
        n = 3
        roads = [(0, 1, 1000000), (1, 2, 1000000)]
        residents = [1000000, 0, 0]
        safe_zones = [2]
        self.assertEqual(evacuation_time(n, roads, residents, safe_zones), 1)

    def test_complex_network(self):
        n = 6
        roads = [
            (0, 1, 15), (0, 2, 10), (1, 2, 5),
            (1, 3, 20), (2, 4, 25), (3, 4, 10),
            (3, 5, 30), (4, 5, 15)
        ]
        residents = [30, 0, 0, 0, 0, 0]
        safe_zones = [5]
        self.assertEqual(evacuation_time(n, roads, residents, safe_zones), 2)

    def test_no_residents(self):
        n = 3
        roads = [(0, 1, 10), (1, 2, 10)]
        residents = [0, 0, 0]
        safe_zones = [2]
        self.assertEqual(evacuation_time(n, roads, residents, safe_zones), 0)

    def test_direct_evacuation(self):
        n = 2
        roads = [(0, 1, 50)]
        residents = [50, 0]
        safe_zones = [1]
        self.assertEqual(evacuation_time(n, roads, residents, safe_zones), 1)

if __name__ == '__main__':
    unittest.main()