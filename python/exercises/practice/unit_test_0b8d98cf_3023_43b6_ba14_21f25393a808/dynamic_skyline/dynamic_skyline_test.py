import unittest
from dynamic_skyline import SkylineManager

class TestSkylineManager(unittest.TestCase):
    def setUp(self):
        self.sm = SkylineManager()

    def test_empty_skyline(self):
        # No buildings added; expect empty skyline.
        self.assertEqual(self.sm.get_skyline(), [])

    def test_single_building(self):
        # Add one building and check its skyline.
        self.sm.add_building(2, 9, 10)
        self.assertEqual(self.sm.get_skyline(), [(2, 10), (9, 0)])

    def test_overlapping_buildings(self):
        # First building: (2,9,10) and second overlapping building: (3,7,15)
        self.sm.add_building(2, 9, 10)
        self.sm.add_building(3, 7, 15)
        # Skyline timeline:
        # [2,3): height 10, [3,7): height 15, [7,9): height 10.
        self.assertEqual(self.sm.get_skyline(), [(2, 10), (3, 15), (7, 10), (9, 0)])

    def test_multiple_buildings(self):
        # Add multiple buildings forming a complex skyline.
        self.sm.add_building(2, 9, 10)
        self.sm.add_building(3, 7, 15)
        self.sm.add_building(5, 12, 12)
        self.sm.add_building(15, 20, 10)
        self.sm.add_building(19, 24, 8)
        # Expected skyline:
        # From 2 to 3: height 10 (only building (2,9,10)),
        # 3 to 7: height 15 (building (3,7,15) dominates),
        # 7 to 12: height 12 (building (5,12,12) after (3,7,15) ends, but also (2,9,10) until 9),
        # then gap and new buildings.
        expected = [(2, 10), (3, 15), (7, 12), (12, 0), (15, 10), (20, 8), (24, 0)]
        self.assertEqual(self.sm.get_skyline(), expected)

    def test_removal_building(self):
        # Add multiple buildings and then remove one.
        self.sm.add_building(2, 9, 10)
        self.sm.add_building(3, 7, 15)
        self.sm.add_building(5, 12, 12)
        self.sm.add_building(15, 20, 10)
        self.sm.add_building(19, 24, 8)
        # Remove the building (3,7,15).
        self.sm.remove_building(3, 7, 15)
        # After removal, buildings: (2,9,10), (5,12,12), (15,20,10), (19,24,8)
        # For group one:
        # [2,5): height 10, [5,9): max(10,12)=12, [9,12): height 12 then drop to 0 at 12.
        # Group two remains unchanged.
        expected = [(2, 10), (5, 12), (12, 0), (15, 10), (20, 8), (24, 0)]
        self.assertEqual(self.sm.get_skyline(), expected)

    def test_multiple_operations(self):
        # Test a series of additions and removals.
        self.sm.add_building(1, 5, 11)
        self.sm.add_building(2, 7, 6)
        self.sm.add_building(3, 9, 13)
        # Expected skyline after three additions:
        # [1,3): height 11, [3,9): height 13, then drop to 0 at 9.
        expected1 = [(1, 11), (3, 13), (9, 0)]
        self.assertEqual(self.sm.get_skyline(), expected1)

        # Remove the building (3,9,13):
        self.sm.remove_building(3, 9, 13)
        # Remaining buildings: (1,5,11) and (2,7,6)
        # For x in [1,2): height 11; [2,5): height 11; [5,7): height 6; drop to 0 at 7.
        expected2 = [(1, 11), (5, 6), (7, 0)]
        self.assertEqual(self.sm.get_skyline(), expected2)

        # Add a new building (4,8,7):
        self.sm.add_building(4, 8, 7)
        # Now remaining buildings: (1,5,11), (2,7,6), (4,8,7)
        # For x in [1,2): height 11; [2,4): height 11; at x=4, building (1,5,11) is still active,
        # so from [4,5): height remains 11; at 5, building (1,5,11) ends, so new height is max(6,7)=7;
        # [5,7): height 7; at 7, building (2,7,6) ends; [7,8): height 7; drop to 0 at 8.
        expected3 = [(1, 11), (5, 7), (8, 0)]
        self.assertEqual(self.sm.get_skyline(), expected3)

if __name__ == '__main__':
    unittest.main()