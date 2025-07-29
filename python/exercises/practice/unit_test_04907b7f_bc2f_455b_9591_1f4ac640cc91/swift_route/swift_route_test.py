import unittest
from swift_route import solve_delivery_problem

class TestSwiftRoute(unittest.TestCase):
    def check_output_structure(self, result):
        # The result should be a dict with keys "trucks" and "total_cost"
        self.assertIsInstance(result, dict)
        self.assertIn("trucks", result)
        self.assertIn("total_cost", result)
        self.assertIsInstance(result["trucks"], list)
        self.assertIsInstance(result["total_cost"], float)
        for truck in result["trucks"]:
            self.assertIn("route", truck)
            self.assertIn("packages", truck)
            self.assertIsInstance(truck["route"], list)
            self.assertGreaterEqual(len(truck["route"]), 2)  # Must have at least a start and end city
            self.assertEqual(truck["route"][0], truck["route"][-1])  # Must return to starting city
            self.assertIsInstance(truck["packages"], list)
            for delivery in truck["packages"]:
                self.assertIsInstance(delivery, tuple)
                self.assertEqual(len(delivery), 3)
                source, dest, num = delivery
                self.assertIsInstance(source, int)
                self.assertIsInstance(dest, int)
                self.assertIsInstance(num, int)

    def test_basic_scenario(self):
        cities = {1: 1000, 2: 500, 3: 750}
        road_network = [(1, 2, 150), (1, 3, 200), (2, 3, 100)]
        delivery_demands = [(1, 2, 200), (2, 3, 300), (1, 3, 150)]
        truck_capacity = 300
        truck_cost = 1000.0
        distance_cost_per_unit = 2.0

        result = solve_delivery_problem(cities, road_network, delivery_demands, truck_capacity, truck_cost, distance_cost_per_unit)
        self.check_output_structure(result)

    def test_minimal_scenario(self):
        # Two cities with a single delivery that fits within one truck.
        cities = {1: 500, 2: 500}
        road_network = [(1, 2, 100)]
        delivery_demands = [(1, 2, 150)]
        truck_capacity = 200
        truck_cost = 800.0
        distance_cost_per_unit = 3.0

        result = solve_delivery_problem(cities, road_network, delivery_demands, truck_capacity, truck_cost, distance_cost_per_unit)
        self.check_output_structure(result)

    def test_multiple_trucks(self):
        # Multiple trucks are needed because total delivery demand exceeds a single truck's capacity.
        cities = {1: 1200, 2: 800, 3: 900, 4: 1000}
        road_network = [(1, 2, 100), (2, 3, 120), (3, 4, 150), (1, 4, 400), (2, 4, 200)]
        delivery_demands = [(1, 3, 250), (1, 4, 350), (2, 4, 300), (3, 1, 200)]
        truck_capacity = 300
        truck_cost = 1500.0
        distance_cost_per_unit = 2.5

        result = solve_delivery_problem(cities, road_network, delivery_demands, truck_capacity, truck_cost, distance_cost_per_unit)
        self.check_output_structure(result)

        # Verify that the total packages delivered equals the total requested.
        requested_packages = sum([req[2] for req in delivery_demands])
        delivered_packages = sum([delivery[2] for truck in result["trucks"] for delivery in truck["packages"]])
        self.assertEqual(requested_packages, delivered_packages)

    def test_warehouse_capacity_respected(self):
        # This scenario tests that no warehouse receives more packages than it can handle.
        cities = {1: 300, 2: 300, 3: 300}
        road_network = [(1, 2, 50), (2, 3, 70), (1, 3, 120)]
        delivery_demands = [(1, 2, 150), (2, 3, 100), (3, 1, 80)]
        truck_capacity = 200
        truck_cost = 1000.0
        distance_cost_per_unit = 1.5

        result = solve_delivery_problem(cities, road_network, delivery_demands, truck_capacity, truck_cost, distance_cost_per_unit)
        self.check_output_structure(result)

        # Calculate incoming packages for each warehouse.
        incoming = {city: 0 for city in cities}
        for truck in result["trucks"]:
            for delivery in truck["packages"]:
                source, dest, num = delivery
                incoming[dest] += num
        for city, capacity in cities.items():
            self.assertLessEqual(incoming[city], capacity)

if __name__ == "__main__":
    unittest.main()