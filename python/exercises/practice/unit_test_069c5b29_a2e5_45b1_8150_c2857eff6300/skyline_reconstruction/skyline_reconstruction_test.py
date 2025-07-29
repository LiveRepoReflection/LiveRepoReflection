import unittest
from skyline_reconstruction import min_effort

class SkylineReconstructionTest(unittest.TestCase):
    # Test 1: Grid already matches the skyline.
    def test_already_matching(self):
        # Grid with 2 rows and 3 columns.
        # Skyline: From x=0 to x<2, target height = 3; from x=2 to x<3, target = 0.
        initial_grid = [
            [3, 3, 0],
            [3, 3, 0]
        ]
        skyline = [(0, 3), (2, 0)]
        construction_cost = 1
        max_height = 5
        # No change needed.
        expected_effort = 0
        self.assertEqual(min_effort(skyline, initial_grid, construction_cost, max_height), expected_effort)

    # Test 2: Basic modifications on a fully zero grid.
    def test_basic_modification(self):
        # Grid 2x3 all zeros.
        initial_grid = [
            [0, 0, 0],
            [0, 0, 0]
        ]
        skyline = [(0, 3), (2, 0)]
        construction_cost = 1
        max_height = 5
        # Target configuration:
        # Columns 0 and 1: target height 3; column 2: target height 0.
        # Effort: for col0: 2*|0-3| = 6, col1: 6, col2: 0. Total = 12.
        expected_effort = 12
        self.assertEqual(min_effort(skyline, initial_grid, construction_cost, max_height), expected_effort)

    # Test 3: Skyline extends beyond the provided grid (virtual column).
    def test_virtual_columns(self):
        # Grid 2x2.
        initial_grid = [
            [1, 2],
            [3, 4]
        ]
        # Skyline: from x=0 to x<3, target height 5; then x>=3 stops.
        skyline = [(0, 5), (3, 0)]
        construction_cost = 1
        max_height = 10
        # For grid:
        # Column 0 in grid: |1-5| + |3-5| = 4+2 = 6.
        # Column 1 in grid: |2-5| + |4-5| = 3+1 = 4.
        # Virtual column 2: assume 2 cells with initial height 0; cost = 2*|0-5| = 10.
        # Total effort = 6+4+10 = 20.
        expected_effort = 20
        self.assertEqual(min_effort(skyline, initial_grid, construction_cost, max_height), expected_effort)

    # Test 4: Skyline with repeated heights (consecutive segments with same target).
    def test_repeated_skyline_heights(self):
        # Grid 3x3 all cells set to 2.
        initial_grid = [
            [2, 2, 2],
            [2, 2, 2],
            [2, 2, 2]
        ]
        # Skyline: first segment from x=0 to x<1: height=2, second from x=1 to x<3: height=2, then stops.
        skyline = [(0, 2), (1, 2), (3, 0)]
        construction_cost = 1
        max_height = 5
        # Already matching configuration.
        expected_effort = 0
        self.assertEqual(min_effort(skyline, initial_grid, construction_cost, max_height), expected_effort)

    # Test 5: Complex modification with non-default construction cost.
    def test_complex_modification(self):
        # Grid 2x4.
        initial_grid = [
            [1, 4, 2, 2],
            [3, 3, 3, 3]
        ]
        # Skyline:
        # From x=0 to x<2: target height = 3 (covers columns 0 and 1)
        # From x=2 to x<4: target height = 5 (covers columns 2 and 3)
        # From x=4 to x<5: target height = 1 (virtual column 4)
        # Then stops.
        skyline = [(0, 3), (2, 5), (4, 1), (5, 0)]
        construction_cost = 3
        max_height = 10
        # Compute effort per column:
        # Column 0: grid cells: [1,3] -> |1-3| + |3-3| = 2+0 = 2.
        # Column 1: grid cells: [4,3] -> |4-3| + |3-3| = 1+0 = 1.
        # Column 2: grid cells: [2,3] -> |2-5| + |3-5| = 3+2 = 5.
        # Column 3: grid cells: [2,3] -> |2-5| + |3-5| = 3+2 = 5.
        # Virtual Column 4: assume 2 cells initially 0 -> 2*|0-1| = 2.
        # Total raw effort = 2+1+5+5+2 = 15; multiplied by construction_cost: 15*3 = 45.
        expected_effort = 45
        self.assertEqual(min_effort(skyline, initial_grid, construction_cost, max_height), expected_effort)

    # Test 6: Empty initial grid.
    def test_empty_initial_grid(self):
        # An empty grid: no rows.
        initial_grid = []
        skyline = [(0, 2), (2, 0)]
        construction_cost = 1
        max_height = 5
        # With an empty grid, assume no cells exist to modify.
        expected_effort = 0
        self.assertEqual(min_effort(skyline, initial_grid, construction_cost, max_height), expected_effort)

    # Test 7: Empty skyline should force all cells to 0.
    def test_empty_skyline(self):
        # Grid 2x2, all cells non-zero.
        initial_grid = [
            [5, 5],
            [5, 5]
        ]
        skyline = []
        construction_cost = 2
        max_height = 10
        # With an empty skyline, the target is interpreted as 0 for every cell.
        # Total effort = 4 cells * |5-0| * 2 = 4*5*2 = 40.
        expected_effort = 40
        self.assertEqual(min_effort(skyline, initial_grid, construction_cost, max_height), expected_effort)

if __name__ == '__main__':
    unittest.main()