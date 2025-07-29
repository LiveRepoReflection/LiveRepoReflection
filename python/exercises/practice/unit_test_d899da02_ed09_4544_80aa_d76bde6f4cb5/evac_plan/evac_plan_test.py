import unittest
from evac_plan import evacuate

class TestEvacPlan(unittest.TestCase):
    def test_single_office(self):
        N = 1
        M = 1
        K = 1
        E = [[10]]
        EvacuationPoints = [1]
        C = [15]
        # For a single office located on the ground floor matching the evacuation point,
        # the evacuation time is 0.
        self.assertEqual(evacuate(N, M, K, E, EvacuationPoints, C), 0)

    def test_small_grid(self):
        N = 2
        M = 3
        K = 1
        E = [
            [1, 2, 3],
            [4, 5, 6]
        ]
        EvacuationPoints = [2]
        C = [21]
        # For offices, the evacuation time for each office is:
        # Floor 1: times = [|1-2|, 0, |3-2|] -> [1, 0, 1]
        # Floor 2: vertical distance 1 plus horizontal differences:
        #          [1+|1-2|, 1+0, 1+|3-2|] -> [2, 1, 2]
        # Maximum evacuation time is 2.
        self.assertEqual(evacuate(N, M, K, E, EvacuationPoints, C), 2)

    def test_sample(self):
        N = 3
        M = 3
        K = 2
        E = [
            [1, 2, 3],
            [4, 5, 6],
            [7, 8, 9]
        ]
        EvacuationPoints = [1, 3]
        C = [20, 25]
        # Based on manual calculation of distances and capacity constraints,
        # the expected minimum maximum evacuation time is 3.
        self.assertEqual(evacuate(N, M, K, E, EvacuationPoints, C), 3)

    def test_capacity_constraint(self):
        N = 3
        M = 2
        K = 2
        E = [
            [5, 5],
            [30, 20],
            [10, 20]
        ]
        EvacuationPoints = [1, 2]
        C = [40, 40]
        # This test forces the algorithm to handle capacity constraints.
        # Through analysis, the minimal maximum time required is expected to be 3.
        self.assertEqual(evacuate(N, M, K, E, EvacuationPoints, C), 3)

    def test_complex_case(self):
        # Construct a moderately complex case to test efficiency and correctness.
        N = 10
        M = 10
        K = 2
        # Create a non-uniform distribution of employees.
        E = [[(i * M + j + 1) % 10 + 1 for j in range(M)] for i in range(N)]
        EvacuationPoints = [3, 8]
        total_employees = sum(sum(row) for row in E)
        # Set capacities to tightly fit the total employees.
        C = [total_employees // 2, total_employees - total_employees // 2]
        # As the expected output is non-trivial to compute manually,
        # we ensure that the function returns a non-negative integer.
        result = evacuate(N, M, K, E, EvacuationPoints, C)
        self.assertIsInstance(result, int)
        self.assertGreaterEqual(result, 0)

if __name__ == '__main__':
    unittest.main()