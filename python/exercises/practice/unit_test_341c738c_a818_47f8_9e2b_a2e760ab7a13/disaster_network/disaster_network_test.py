import unittest
from disaster_network import design_response_network

class DisasterNetworkTest(unittest.TestCase):
    def test_basic_case(self):
        cities = [(0, 0, 1000, 15), (10, 0, 500, 10), (5, 5, 750, 20)]
        depots = [(0, 10, 30), (10, 10, 25)]
        cost_per_unit = 1.0
        
        solution = design_response_network(cities, depots, cost_per_unit)
        
        # Test that all cities are included in the solution
        self.assertEqual(set(solution.keys()), {0, 1, 2})
        
        # Test that all cities' demands are met
        city_resources = [0, 0, 0]
        for city_idx, depot_allocation in solution.items():
            for depot_idx, amount in depot_allocation.items():
                city_resources[city_idx] += amount
        
        self.assertEqual(city_resources[0], 15)  # City 0 demand
        self.assertEqual(city_resources[1], 10)  # City 1 demand
        self.assertEqual(city_resources[2], 20)  # City 2 demand
        
        # Test depot capacity constraints
        depot_usage = [0, 0]
        for city_idx, depot_allocation in solution.items():
            for depot_idx, amount in depot_allocation.items():
                depot_usage[depot_idx] += amount
        
        self.assertLessEqual(depot_usage[0], 30)  # Depot 0 capacity
        self.assertLessEqual(depot_usage[1], 25)  # Depot 1 capacity

    def test_single_city_single_depot(self):
        cities = [(5, 5, 1000, 20)]
        depots = [(10, 10, 30)]
        cost_per_unit = 1.5
        
        solution = design_response_network(cities, depots, cost_per_unit)
        
        self.assertEqual(len(solution), 1)
        self.assertIn(0, solution)
        self.assertEqual(sum(solution[0].values()), 20)

    def test_multiple_cities_single_depot(self):
        cities = [(0, 0, 500, 10), (10, 10, 800, 15), (20, 20, 1200, 25)]
        depots = [(15, 15, 60)]
        cost_per_unit = 2.0
        
        solution = design_response_network(cities, depots, cost_per_unit)
        
        # Check all cities are served
        self.assertEqual(set(solution.keys()), {0, 1, 2})
        
        # Check all demands are met
        city_resources = [0, 0, 0]
        for city_idx, depot_allocation in solution.items():
            for depot_idx, amount in depot_allocation.items():
                city_resources[city_idx] += amount
        
        self.assertEqual(city_resources[0], 10)
        self.assertEqual(city_resources[1], 15)
        self.assertEqual(city_resources[2], 25)
        
        # Check depot capacity is not exceeded
        depot_usage = 0
        for city_idx, depot_allocation in solution.items():
            for depot_idx, amount in depot_allocation.items():
                depot_usage += amount
        
        self.assertLessEqual(depot_usage, 60)

    def test_single_city_multiple_depots(self):
        cities = [(50, 50, 2000, 40)]
        depots = [(30, 30, 25), (60, 60, 20), (40, 70, 10)]
        cost_per_unit = 0.5
        
        solution = design_response_network(cities, depots, cost_per_unit)
        
        # Check the city is served
        self.assertIn(0, solution)
        
        # Check demand is met
        total_resources = sum(solution[0].values())
        self.assertEqual(total_resources, 40)
        
        # Check depot capacities are not exceeded
        depot_usage = [0, 0, 0]
        for depot_idx, amount in solution[0].items():
            depot_usage[depot_idx] += amount
        
        self.assertLessEqual(depot_usage[0], 25)
        self.assertLessEqual(depot_usage[1], 20)
        self.assertLessEqual(depot_usage[2], 10)

    def test_large_case(self):
        # Create a larger test case
        cities = []
        for i in range(10):
            x = (i % 5) * 10
            y = (i // 5) * 10
            population = (i + 1) * 500
            demand = (i % 5) + 5
            cities.append((x, y, population, demand))
        
        depots = []
        for i in range(4):
            x = (i % 2) * 40 + 10
            y = (i // 2) * 40 + 10
            capacity = (i + 1) * 10
            depots.append((x, y, capacity))
        
        cost_per_unit = 1.0
        
        solution = design_response_network(cities, depots, cost_per_unit)
        
        # Check all cities are served
        self.assertEqual(len(solution), 10)
        
        # Check all demands are met
        city_resources = [0] * 10
        for city_idx, depot_allocation in solution.items():
            for depot_idx, amount in depot_allocation.items():
                city_resources[city_idx] += amount
        
        for i in range(10):
            expected_demand = (i % 5) + 5
            self.assertEqual(city_resources[i], expected_demand)
        
        # Check depot capacities are not exceeded
        depot_usage = [0] * 4
        for city_idx, depot_allocation in solution.items():
            for depot_idx, amount in depot_allocation.items():
                depot_usage[depot_idx] += amount
        
        for i in range(4):
            expected_capacity = (i + 1) * 10
            self.assertLessEqual(depot_usage[i], expected_capacity)

    def test_edge_cases(self):
        # Test with maximum demand and minimum capacity
        cities = [(0, 0, 1000, 50)]
        depots = [(10, 10, 50)]
        cost_per_unit = 1.0
        
        solution = design_response_network(cities, depots, cost_per_unit)
        
        self.assertEqual(len(solution), 1)
        self.assertEqual(sum(solution[0].values()), 50)

        # Test with cities and depots at the same location
        cities = [(25, 25, 1000, 15), (50, 50, 2000, 20)]
        depots = [(25, 25, 15), (75, 75, 20)]
        cost_per_unit = 2.0
        
        solution = design_response_network(cities, depots, cost_per_unit)
        
        # City 0 should get resources from depot 0 (same location)
        self.assertIn(0, solution)
        self.assertIn(0, solution[0])
        
        # Total resources should match demands
        self.assertEqual(sum(solution[0].values()), 15)
        self.assertEqual(sum(solution[1].values()), 20)

    def test_validate_optimization(self):
        # This test validates the optimization aspect (both cost and delay minimization)
        cities = [(0, 0, 1000, 10), (10, 0, 500, 10), (0, 10, 750, 10)]
        depots = [(0, 5, 15), (5, 0, 15)]
        cost_per_unit = 1.0
        
        solution = design_response_network(cities, depots, cost_per_unit)
        
        # Calculate total cost of solution
        total_cost = 0
        max_delay = 0
        
        for city_idx, depot_allocation in solution.items():
            city_x, city_y = cities[city_idx][0], cities[city_idx][1]
            
            city_min_distance = float('inf')
            for depot_idx, amount in depot_allocation.items():
                depot_x, depot_y = depots[depot_idx][0], depots[depot_idx][1]
                
                distance = ((city_x - depot_x) ** 2 + (city_y - depot_y) ** 2) ** 0.5
                total_cost += distance * amount * cost_per_unit
                
                if amount > 0:
                    city_min_distance = min(city_min_distance, distance)
            
            max_delay = max(max_delay, city_min_distance)
        
        # We can't easily check for exact optimal cost, but we can check the solution is valid
        # and total cost is reasonable (less than a naive solution)
        naive_max_cost = 30 * 20  # Worst case: max distance * total demand
        self.assertLess(total_cost, naive_max_cost)
        
        # Similarly for delay, we check it's less than the maximum possible delay
        max_possible_delay = 20  # Diagonal of a 10x10 grid = ~14.14
        self.assertLess(max_delay, max_possible_delay)

if __name__ == '__main__':
    unittest.main()