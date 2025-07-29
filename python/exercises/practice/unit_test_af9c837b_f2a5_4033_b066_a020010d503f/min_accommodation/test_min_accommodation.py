import unittest
from min_accommodation import min_cost_accommodation

class TestMinAccommodation(unittest.TestCase):
    def test_single_hotel_sufficient_capacity(self):
        num_attendees = 100
        num_days = 3
        hotels = [
            {
                'id': 1,
                'daily_capacities': [150, 150, 150],
                'daily_rates': [100.0, 100.0, 100.0],
                'fixed_cost': 500.0
            }
        ]
        expected = (100.0 * 3 * 100) + 500.0
        self.assertEqual(min_cost_accommodation(num_attendees, num_days, hotels), expected)

    def test_multiple_hotels_optimal_combination(self):
        num_attendees = 200
        num_days = 2
        hotels = [
            {
                'id': 1,
                'daily_capacities': [100, 100],
                'daily_rates': [50.0, 50.0],
                'fixed_cost': 1000.0
            },
            {
                'id': 2,
                'daily_capacities': [150, 150],
                'daily_rates': [60.0, 60.0],
                'fixed_cost': 800.0
            }
        ]
        # Optimal: 100 in hotel1 + 100 in hotel2
        expected = (50.0*2*100 + 1000.0) + (60.0*2*100 + 800.0)
        self.assertEqual(min_cost_accommodation(num_attendees, num_days, hotels), expected)

    def test_insufficient_capacity(self):
        num_attendees = 500
        num_days = 3
        hotels = [
            {
                'id': 1,
                'daily_capacities': [100, 100, 100],
                'daily_rates': [50.0, 50.0, 50.0],
                'fixed_cost': 500.0
            },
            {
                'id': 2,
                'daily_capacities': [150, 150, 150],
                'daily_rates': [60.0, 60.0, 60.0],
                'fixed_cost': 700.0
            }
        ]
        self.assertEqual(min_cost_accommodation(num_attendees, num_days, hotels), -1)

    def test_varying_daily_capacities(self):
        num_attendees = 150
        num_days = 4
        hotels = [
            {
                'id': 1,
                'daily_capacities': [200, 100, 200, 100],
                'daily_rates': [30.0, 30.0, 30.0, 30.0],
                'fixed_cost': 1000.0
            },
            {
                'id': 2,
                'daily_capacities': [50, 200, 50, 200],
                'daily_rates': [40.0, 40.0, 40.0, 40.0],
                'fixed_cost': 800.0
            }
        ]
        # Must use both hotels due to daily capacity constraints
        expected = (30.0*4*100 + 1000.0) + (40.0*4*50 + 800.0)
        self.assertEqual(min_cost_accommodation(num_attendees, num_days, hotels), expected)

    def test_zero_attendees(self):
        num_attendees = 0
        num_days = 5
        hotels = [
            {
                'id': 1,
                'daily_capacities': [100, 100, 100, 100, 100],
                'daily_rates': [50.0, 50.0, 50.0, 50.0, 50.0],
                'fixed_cost': 1000.0
            }
        ]
        self.assertEqual(min_cost_accommodation(num_attendees, num_days, hotels), 0.0)

    def test_no_hotels(self):
        num_attendees = 100
        num_days = 3
        hotels = []
        self.assertEqual(min_cost_accommodation(num_attendees, num_days, hotels), -1)

    def test_large_inputs(self):
        num_attendees = 10000
        num_days = 7
        hotels = [
            {
                'id': 1,
                'daily_capacities': [10000] * 7,
                'daily_rates': [10.0] * 7,
                'fixed_cost': 5000.0
            },
            {
                'id': 2,
                'daily_capacities': [5000] * 7,
                'daily_rates': [9.0] * 7,
                'fixed_cost': 3000.0
            }
        ]
        # Optimal: 5000 in each hotel
        expected = (10.0*7*5000 + 5000.0) + (9.0*7*5000 + 3000.0)
        self.assertEqual(min_cost_accommodation(num_attendees, num_days, hotels), expected)

if __name__ == '__main__':
    unittest.main()