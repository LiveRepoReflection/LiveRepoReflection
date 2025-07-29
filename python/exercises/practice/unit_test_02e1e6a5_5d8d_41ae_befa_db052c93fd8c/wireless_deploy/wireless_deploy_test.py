import math
import unittest
from wireless_deploy import solve

def euclidean_distance(p, q):
    return math.sqrt((p[0] - q[0]) ** 2 + (p[1] - q[1]) ** 2)

class TestWirelessDeploy(unittest.TestCase):
    def validate_solution(self, customer_locations, obstacle_locations, R, D, C, B, aps):
        # Check that no AP is placed on an obstacle
        for ap in aps:
            self.assertNotIn(ap, obstacle_locations, "AP placed on an obstacle.")
        # Check that APs satisfy the minimum distance constraint
        for i in range(len(aps)):
            for j in range(i + 1, len(aps)):
                self.assertGreaterEqual(euclidean_distance(aps[i], aps[j]), D - 1e-6,
                                        "AP interference constraint violated.")
        # Check that every customer is covered by at least one AP
        for cust in customer_locations:
            covered = any(euclidean_distance(cust, ap) <= R + 1e-6 for ap in aps)
            self.assertTrue(covered, f"Customer {cust} is not covered by any AP.")
        # Check that the total cost does not exceed the budget
        total_cost = len(aps) * C
        self.assertLessEqual(total_cost, B, "Total cost exceeds the budget.")

    def test_single_customer(self):
        customer_locations = [(100, 100)]
        obstacle_locations = []
        R = 50
        D = 10
        C = 100
        B = 150
        aps = solve(len(customer_locations), customer_locations, len(obstacle_locations), obstacle_locations, R, D, C, B)
        self.assertIsInstance(aps, list, "Result should be a list.")
        self.assertGreater(len(aps), 0, "At least one AP must be deployed.")
        self.validate_solution(customer_locations, obstacle_locations, R, D, C, B, aps)

    def test_multiple_customers_covered_by_one_ap(self):
        customer_locations = [(100, 100), (105, 102), (98, 97), (103, 99)]
        obstacle_locations = []
        R = 10
        D = 5
        C = 200
        B = 250
        aps = solve(len(customer_locations), customer_locations, len(obstacle_locations), obstacle_locations, R, D, C, B)
        self.assertIsInstance(aps, list, "Result should be a list.")
        self.assertEqual(len(aps), 1, "All customers should be covered by one AP.")
        self.validate_solution(customer_locations, obstacle_locations, R, D, C, B, aps)

    def test_obstacle_avoidance(self):
        customer_locations = [(10, 10), (20, 10), (10, 20), (20, 20)]
        obstacle_locations = [(15, 15)]
        R = 10
        D = 5
        C = 150
        B = 300
        aps = solve(len(customer_locations), customer_locations, len(obstacle_locations), obstacle_locations, R, D, C, B)
        self.assertIsInstance(aps, list, "Result should be a list.")
        self.assertGreater(len(aps), 0, "At least one AP should be deployed.")
        for ap in aps:
            self.assertNotEqual(ap, (15, 15), "AP should not be placed on an obstacle.")
        self.validate_solution(customer_locations, obstacle_locations, R, D, C, B, aps)

    def test_budget_exceeded(self):
        customer_locations = [(0, 0), (500, 500), (1000, 1000)]
        obstacle_locations = []
        R = 100
        D = 10
        C = 500
        B = 500  # Only enough budget for 1 AP, which is insufficient to cover all customers
        aps = solve(len(customer_locations), customer_locations, len(obstacle_locations), obstacle_locations, R, D, C, B)
        self.assertEqual(aps, [], "Should return an empty list when the budget is insufficient.")

    def test_interference_constraint(self):
        customer_locations = [(0, 0), (0, 300), (300, 0), (300, 300)]
        obstacle_locations = []
        R = 150
        D = 100
        C = 100
        B = 500
        aps = solve(len(customer_locations), customer_locations, len(obstacle_locations), obstacle_locations, R, D, C, B)
        self.assertIsInstance(aps, list, "Result should be a list.")
        self.assertGreaterEqual(len(aps), 2, "More than one AP should be deployed to cover dispersed customers.")
        self.validate_solution(customer_locations, obstacle_locations, R, D, C, B, aps)

    def test_edge_case_no_customers(self):
        customer_locations = []
        obstacle_locations = []
        R = 50
        D = 10
        C = 100
        B = 100
        aps = solve(len(customer_locations), customer_locations, len(obstacle_locations), obstacle_locations, R, D, C, B)
        self.assertEqual(aps, [], "No AP should be deployed when there are no customers.")

if __name__ == "__main__":
    unittest.main()