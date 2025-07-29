import unittest
from optimal_logistics import min_vehicles

class OptimalLogisticsTest(unittest.TestCase):
    def test_single_customer_possible(self):
        N = 1
        K = 3
        graph = [
            (0, 1, 10, {"van", "truck", "drone"}),
            (1, 0, 10, {"van", "truck", "drone"})
        ]
        D = [15]  # deadline for customer zone 1
        V = [50]  # package volume for customer zone 1
        T = 20    # max travel time capacity per vehicle
        C = 100   # package volume capacity per vehicle
        vehicle_types = ["van", "truck", "drone"]
        expected = 1
        result = min_vehicles(N, K, graph, D, V, T, C, vehicle_types)
        self.assertEqual(result, expected)

    def test_single_customer_impossible_deadline(self):
        N = 1
        K = 3
        graph = [
            (0, 1, 20, {"van", "truck", "drone"}),
            (1, 0, 20, {"van", "truck", "drone"})
        ]
        D = [15]  # deadline too strict
        V = [50]
        T = 25
        C = 100
        vehicle_types = ["van", "truck", "drone"]
        expected = -1
        result = min_vehicles(N, K, graph, D, V, T, C, vehicle_types)
        self.assertEqual(result, expected)

    def test_multiple_customers_split_delivery(self):
        N = 3
        K = 3
        graph = [
            (0, 1, 10, {"van", "drone"}),
            (1, 0, 10, {"van", "drone"}),
            (0, 2, 15, {"truck", "van"}),
            (2, 0, 15, {"truck", "van"}),
            (1, 2, 5, {"van"}),
            (2, 1, 5, {"van"}),
            (1, 3, 12, {"drone"}),
            (3, 1, 12, {"drone"}),
            (2, 3, 8, {"truck", "van"}),
            (3, 2, 8, {"truck", "van"})
        ]
        # Deadlines for zones 1,2,3 respectively.
        D = [30, 35, 40]
        # Package volumes for zones 1,2,3 respectively.
        V = [50, 60, 70]
        T = 60
        C = 150
        vehicle_types = ["van", "truck", "drone"]
        # Expected solution requires splitting deliveries among vehicles.
        # Based on constraints, assume the optimal solution uses 2 vehicles.
        expected = 2
        result = min_vehicles(N, K, graph, D, V, T, C, vehicle_types)
        self.assertEqual(result, expected)

    def test_vehicle_type_mismatch(self):
        N = 1
        K = 2
        graph = [
            (0, 1, 10, {"truck"}),   # Only truck is allowed
            (1, 0, 10, {"truck"})
        ]
        D = [20]
        V = [50]
        T = 20
        C = 60
        vehicle_types = ["van", "van"]  # No truck available
        expected = -1
        result = min_vehicles(N, K, graph, D, V, T, C, vehicle_types)
        self.assertEqual(result, expected)

    def test_complex_network(self):
        N = 4
        K = 4
        graph = [
            (0, 1, 5, {"van", "truck"}),
            (1, 0, 5, {"van", "truck"}),
            (1, 2, 10, {"van"}),
            (2, 1, 10, {"van"}),
            (0, 3, 20, {"drone", "van"}),
            (3, 0, 20, {"drone", "van"}),
            (3, 4, 15, {"van", "drone"}),
            (4, 3, 15, {"van", "drone"}),
            (2, 4, 5, {"van"}),
            (4, 2, 5, {"van"})
        ]
        # Deadlines for zones 1-4
        D = [30, 40, 50, 45]
        V = [20, 30, 40, 50]
        T = 50
        C = 90
        vehicle_types = ["van", "truck", "drone", "van"]
        # An optimal heuristic might schedule deliveries in 2 vehicles.
        expected = 2
        result = min_vehicles(N, K, graph, D, V, T, C, vehicle_types)
        self.assertEqual(result, expected)

    def test_volume_constraint(self):
        N = 3
        K = 3
        graph = [
            (0, 1, 10, {"van"}),
            (1, 0, 10, {"van"}),
            (0, 2, 10, {"van"}),
            (2, 0, 10, {"van"}),
            (0, 3, 10, {"van"}),
            (3, 0, 10, {"van"})
        ]
        D = [20, 20, 20]
        V = [50, 60, 70]  # Every node volume combination exceeds a vehicle's capacity if paired
        T = 30
        C = 100    # Each vehicle can deliver at most volume 100
        vehicle_types = ["van", "van", "van"]
        # Each customer must be served by a separate vehicle, so optimal = 3.
        expected = 3
        result = min_vehicles(N, K, graph, D, V, T, C, vehicle_types)
        self.assertEqual(result, expected)

    def test_disconnected_customer(self):
        N = 1
        K = 2
        graph = []  # No connection from warehouse to customer zone 1
        D = [20]
        V = [50]
        T = 30
        C = 100
        vehicle_types = ["van", "truck"]
        # With no connection, delivery is impossible.
        expected = -1
        result = min_vehicles(N, K, graph, D, V, T, C, vehicle_types)
        self.assertEqual(result, expected)

if __name__ == '__main__':
    unittest.main()