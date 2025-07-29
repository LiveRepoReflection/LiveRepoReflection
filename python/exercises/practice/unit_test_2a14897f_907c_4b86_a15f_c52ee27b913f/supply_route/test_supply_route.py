import unittest
from supply_route.supply_route import optimize_routes

class TestSupplyRoute(unittest.TestCase):
    def test_basic_case(self):
        warehouses = [
            {'location': (34.0522, -118.2437), 'capacity': 100},
            {'location': (40.7128, -74.0060), 'capacity': 150}
        ]
        hubs = [
            {'location': (37.7749, -122.4194), 'demand': 60},
            {'location': (41.8781, -87.6298), 'demand': 80},
            {'location': (33.4484, -112.0740), 'demand': 40}
        ]
        travel_times = [
            [300, 2400, 180],
            [2400, 120, 2100]
        ]
        costs = [
            [1.0, 2.0, 1.5],
            [2.5, 1.5, 3.0]
        ]
        max_time = 360
        
        result, total_cost, feasible = optimize_routes(
            warehouses, hubs, travel_times, costs, max_time
        )
        
        self.assertTrue(feasible)
        self.assertEqual(total_cost, 240)
        self.assertEqual(result['San Francisco'], 'Los Angeles')
        self.assertEqual(result['Chicago'], 'New York')
        self.assertEqual(result['Phoenix'], 'Los Angeles')

    def test_capacity_constraint(self):
        warehouses = [
            {'location': (34.0522, -118.2437), 'capacity': 50},
            {'location': (40.7128, -74.0060), 'capacity': 150}
        ]
        hubs = [
            {'location': (37.7749, -122.4194), 'demand': 60},
            {'location': (41.8781, -87.6298), 'demand': 80},
            {'location': (33.4484, -112.0740), 'demand': 40}
        ]
        travel_times = [
            [300, 2400, 180],
            [2400, 120, 2100]
        ]
        costs = [
            [1.0, 2.0, 1.5],
            [2.5, 1.5, 3.0]
        ]
        max_time = 360
        
        _, _, feasible = optimize_routes(
            warehouses, hubs, travel_times, costs, max_time
        )
        self.assertFalse(feasible)

    def test_time_constraint(self):
        warehouses = [
            {'location': (34.0522, -118.2437), 'capacity': 100},
            {'location': (40.7128, -74.0060), 'capacity': 150}
        ]
        hubs = [
            {'location': (37.7749, -122.4194), 'demand': 60},
            {'location': (41.8781, -87.6298), 'demand': 80},
            {'location': (33.4484, -112.0740), 'demand': 40}
        ]
        travel_times = [
            [300, 2400, 180],
            [2400, 120, 2100]
        ]
        costs = [
            [1.0, 2.0, 1.5],
            [2.5, 1.5, 3.0]
        ]
        max_time = 200
        
        _, _, feasible = optimize_routes(
            warehouses, hubs, travel_times, costs, max_time
        )
        self.assertFalse(feasible)

    def test_large_input(self):
        warehouses = [{'location': (i, i), 'capacity': 100} for i in range(100)]
        hubs = [{'location': (i+0.5, i+0.5), 'demand': 1} for i in range(100)]
        travel_times = [[1 if i == j else 100 for j in range(100)] for i in range(100)]
        costs = [[1.0 for _ in range(100)] for _ in range(100)]
        max_time = 10
        
        result, total_cost, feasible = optimize_routes(
            warehouses, hubs, travel_times, costs, max_time
        )
        
        self.assertTrue(feasible)
        self.assertEqual(total_cost, 100)
        for i in range(100):
            self.assertEqual(result[f"Hub {i}"], f"Warehouse {i}")

    def test_empty_input(self):
        result, total_cost, feasible = optimize_routes([], [], [], [], 0)
        self.assertTrue(feasible)
        self.assertEqual(total_cost, 0)
        self.assertEqual(result, {})

if __name__ == '__main__':
    unittest.main()