import unittest
from billboard_placement import max_billboard_revenue

class BillboardPlacementTest(unittest.TestCase):
    def test_empty_locations(self):
        L = 100
        N = 0
        T = 10
        x = []
        r = []
        self.assertEqual(max_billboard_revenue(L, N, T, x, r), 0)

    def test_single_billboard(self):
        L = 50
        N = 1
        T = 10
        x = [25]
        r = [100]
        self.assertEqual(max_billboard_revenue(L, N, T, x, r), 100)

    def test_all_conflict(self):
        # All locations are too close together so only one can be chosen.
        L = 20
        N = 4
        T = 10
        x = [1, 2, 3, 4]
        r = [10, 20, 30, 40]
        # Only the billboard with the highest revenue (40) should be taken.
        self.assertEqual(max_billboard_revenue(L, N, T, x, r), 40)

    def test_exact_gap(self):
        # Billboards placed exactly T kilometers apart should all be selectable.
        L = 30
        N = 3
        T = 5
        x = [1, 6, 11]
        r = [10, 10, 10]
        self.assertEqual(max_billboard_revenue(L, N, T, x, r), 30)

    def test_unsorted_input(self):
        # Unsorted input should be processed correctly.
        L = 15
        N = 6
        T = 5
        x = [12, 2, 14, 3, 6, 9]
        r = [8, 5, 3, 4, 6, 5]
        # After sorting the x positions:
        # x becomes [2, 3, 6, 9, 12, 14] with corresponding r [5, 4, 6, 5, 8, 3].
        # With T = 5, the valid selections yield a maximum revenue of 14.
        self.assertEqual(max_billboard_revenue(L, N, T, x, r), 14)

    def test_complex_scenario(self):
        # This test verifies the dynamic determination of the optimal selection.
        L = 100
        N = 8
        T = 10
        x = [2, 15, 18, 30, 42, 55, 75, 95]
        r = [10, 50, 30, 40, 25, 80, 15, 60]
        # Expected result is computed via dynamic programming:
        # dp[7] = 60 (at x=95)
        # dp[6] = max(15 + 60, 60) = 75 (at x=75)
        # dp[5] = max(80 + 75, 75) = 155 (at x=55)
        # dp[4] = max(25 + 155, 155) = 180 (at x=42)
        # dp[3] = max(40 + 180, 180) = 220 (at x=30)
        # dp[2] = max(30 + 220, 220) = 250 (at x=18)
        # dp[1] = max(50 + 220, 250) = 270 (at x=15)
        # dp[0] = max(10 + 270, 270) = 280 (at x=2)
        expected = 280
        self.assertEqual(max_billboard_revenue(L, N, T, x, r), expected)

if __name__ == '__main__':
    unittest.main()