import unittest
from skyline_merge import skyline_merge

class TestSkylineMerger(unittest.TestCase):
    def setUp(self):
        # Create a new instance before each test
        self.merger = skyline_merge.SkylineMerger()

    def test_empty_skyline(self):
        # No building added, skyline should be empty.
        self.assertEqual(self.merger.get_skyline(), [])

    def test_single_building(self):
        # One building should produce a skyline with a start and ending point.
        self.merger.add_building(2, 9, 10)
        expected = [[2, 10], [9, 0]]
        self.assertEqual(self.merger.get_skyline(), expected)

    def test_overlapping_buildings(self):
        # Classic skyline test case.
        buildings = [
            (2, 9, 10),
            (3, 7, 15),
            (5, 12, 12),
            (15, 20, 10),
            (19, 24, 8)
        ]
        for left, right, height in buildings:
            self.merger.add_building(left, right, height)
        expected = [[2, 10], [3, 15], [7, 12], [12, 0], [15, 10], [20, 8], [24, 0]]
        self.assertEqual(self.merger.get_skyline(), expected)

    def test_same_boundaries_different_heights(self):
        # Two buildings with identical boundaries, the taller should dominate.
        self.merger.add_building(1, 3, 3)
        self.merger.add_building(1, 3, 4)
        expected = [[1, 4], [3, 0]]
        self.assertEqual(self.merger.get_skyline(), expected)

    def test_non_overlapping_buildings(self):
        # Buildings that do not overlap should produce separate segments.
        self.merger.add_building(1, 2, 1)
        self.merger.add_building(3, 4, 1)
        expected = [[1, 1], [2, 0], [3, 1], [4, 0]]
        self.assertEqual(self.merger.get_skyline(), expected)

    def test_building_with_no_effect(self):
        # Adding a building that is completely inside an existing building with a lower height.
        self.merger.add_building(2, 9, 10)
        self.merger.add_building(3, 8, 5)
        expected = [[2, 10], [9, 0]]
        self.assertEqual(self.merger.get_skyline(), expected)

    def test_inner_building_changes_skyline(self):
        # Adding a building inside another that actually changes the skyline.
        self.merger.add_building(1, 10, 5)
        self.merger.add_building(2, 5, 8)
        expected = [[1, 5], [2, 8], [5, 5], [10, 0]]
        self.assertEqual(self.merger.get_skyline(), expected)

    def test_multiple_complex_additions(self):
        # Add multiple buildings in a random order to test comprehensive merging.
        buildings = [
            (5, 15, 12),
            (2, 10, 8),
            (11, 13, 10),
            (7, 17, 15),
            (20, 25, 8),
            (19, 22, 12)
        ]
        for left, right, height in buildings:
            self.merger.add_building(left, right, height)
        
        # Expected skyline computed manually:
        # Start with building (2,10,8) gives [2,8]
        # Building (5,15,12) overrides height from 5 to 15: [5,12]
        # Building (7,17,15) further increases height from 7 till 17: 
        #    thus [7,15]
        # At 15, skyline drops from (15,12) due to disappearance of building 5,15,12, but (7,17,15) still active until 17.
        # So drop happens after 17: so [17,0] if no other building, but then building (11,13,10) is fully inside 7,17,15 so no effect.
        # Next, building (19,22,12) kicks in after gap: so we have [19,12] then building (20,25,8) adjusts: but since (19,22,12) is taller until 22,
        # then at 22, drop to 8 continuing until 25.
        # Final expected merge:
        # For clarity, we construct the timeline:
        # 2: height 8 (from building (2,10,8))
        # 5: height becomes 12 (from building (5,15,12))
        # 7: height becomes 15 (from building (7,17,15))
        # 10: building (2,10,8) ends, but still [7,17,15] active so no change.
        # 15: building (5,15,12) ends, no change.
        # 17: building (7,17,15) ends, drop to 0.
        # 19: building (19,22,12) starts, so height becomes 12.
        # 20: building (20,25,8) starts but doesn't change skyline as 12 > 8.
        # 22: building (19,22,12) ends, drop to 8 (from building (20,25,8)).
        # 25: building (20,25,8) ends, drop to 0.
        #
        # So expected:
        expected = [[2, 8], [5, 12], [7, 15], [17, 0], [19, 12], [22, 8], [25, 0]]
        self.assertEqual(self.merger.get_skyline(), expected)

if __name__ == '__main__':
    unittest.main()