import unittest
from microgrid_opt import allocate_resources

class MicrogridOptTest(unittest.TestCase):
    def test_zero_demand(self):
        # Scenario: No consumer demand, and no renewable generation.
        timestamp = 1
        grid_price = 0.5
        solar_generation = 0
        wind_generation = 0
        demands = {'house1': 0, 'house2': 0}
        battery_state = 50
        battery_capacity = 100
        max_charge_rate = 10
        max_grid_power = 50

        result = allocate_resources(timestamp, grid_price, solar_generation, wind_generation,
                                    demands, battery_state, battery_capacity,
                                    max_charge_rate, max_grid_power)
        self.assertIn('grid_power', result)
        self.assertIn('battery_charge_rate', result)
        self.assertIn('consumer_power', result)

        # With zero demand, grid power and supplied consumer power should be zero.
        self.assertEqual(result['grid_power'], 0)
        self.assertEqual(result['battery_charge_rate'], 0)
        for consumer, alloc in result['consumer_power'].items():
            self.assertEqual(alloc, 0)

    def test_full_generation_demand_met(self):
        # Scenario: Renewable generation well exceeds consumer demand,
        # so all consumer demand is met without drawing from the grid.
        timestamp = 2
        grid_price = 1.0
        solar_generation = 20
        wind_generation = 10
        demands = {'cons1': 5, 'cons2': 8}
        battery_state = 30
        battery_capacity = 100
        max_charge_rate = 10
        max_grid_power = 50

        result = allocate_resources(timestamp, grid_price, solar_generation, wind_generation,
                                    demands, battery_state, battery_capacity,
                                    max_charge_rate, max_grid_power)
        # Check that each consumer's demand is fully satisfied.
        for consumer, demand in demands.items():
            self.assertAlmostEqual(result['consumer_power'].get(consumer, 0), demand, places=5)
        
        # When renewables suffice, no grid power should be used.
        self.assertEqual(result['grid_power'], 0)
        # Extra renewable energy might be used to charge the battery, so ensure the charge rate is within limits.
        self.assertGreaterEqual(result['battery_charge_rate'], 0)
        self.assertLessEqual(result['battery_charge_rate'], max_charge_rate)

    def test_insufficient_renewable_use_battery_and_grid(self):
        # Scenario: No renewable generation, so to meet consumer demand,
        # the system must use battery discharge and possibly limited grid power.
        timestamp = 3
        grid_price = 10.0  # High grid price should incentivize battery use.
        solar_generation = 0
        wind_generation = 0
        demands = {'cons1': 15}
        battery_state = 20  # Battery has stored energy available.
        battery_capacity = 50
        max_charge_rate = 10
        max_grid_power = 30

        result = allocate_resources(timestamp, grid_price, solar_generation, wind_generation,
                                    demands, battery_state, battery_capacity,
                                    max_charge_rate, max_grid_power)
        # Consumer demand should be satisfied.
        self.assertAlmostEqual(result['consumer_power'].get('cons1', 0), 15, places=5)
        # Grid power must be non-negative and not exceed the maximum allowed.
        self.assertGreaterEqual(result['grid_power'], 0)
        self.assertLessEqual(result['grid_power'], max_grid_power)
        # Expecting battery discharge when grid power is expensive.
        self.assertLessEqual(result['battery_charge_rate'], 0)
        self.assertLessEqual(abs(result['battery_charge_rate']), max_charge_rate)

    def test_invalid_negative_input(self):
        # Scenario: Negative grid price is invalid and should cause an error.
        timestamp = 4
        grid_price = -1.0  # Invalid negative value.
        solar_generation = 10
        wind_generation = 5
        demands = {'cons1': 5}
        battery_state = 20
        battery_capacity = 50
        max_charge_rate = 10
        max_grid_power = 30

        with self.assertRaises(ValueError):
            allocate_resources(timestamp, grid_price, solar_generation, wind_generation,
                               demands, battery_state, battery_capacity,
                               max_charge_rate, max_grid_power)

if __name__ == '__main__':
    unittest.main()