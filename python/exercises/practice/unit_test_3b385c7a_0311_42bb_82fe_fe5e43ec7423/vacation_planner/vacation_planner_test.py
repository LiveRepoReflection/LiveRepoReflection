import unittest
from vacation_planner import optimize_vacation_plan

class VacationPlannerTest(unittest.TestCase):
    def test_basic_vacation(self):
        N = 3
        flights = [
            (0, 1, 100, 10),  # city1, city2, cost, happiness
            (1, 2, 150, 15),
            (2, 0, 200, 20)
        ]
        hotels = [
            (0, 50, 5),  # city, cost_per_night, happiness_per_night
            (1, 60, 6),
            (2, 70, 7)
        ]
        activities = [
            (0, "Beach", 30, 8),  # city, activity_name, cost, happiness
            (1, "Sightseeing", 40, 10),
            (2, "Museum", 35, 9)
        ]
        start_city = 0
        budget = 500
        duration = 3
        min_stay = 2
        happiness_threshold = 30
        cities_to_visit = {1}

        result = optimize_vacation_plan(
            N, flights, hotels, activities,
            start_city, budget, duration,
            min_stay, happiness_threshold,
            cities_to_visit
        )

        self.assertIsNotNone(result)
        self.assertGreater(len(result), 0)
        
    def test_impossible_budget(self):
        N = 2
        flights = [(0, 1, 1000, 10)]
        hotels = [(0, 100, 5), (1, 100, 5)]
        activities = [(0, "Activity", 50, 5), (1, "Activity", 50, 5)]
        
        result = optimize_vacation_plan(
            N, flights, hotels, activities,
            0, 100, 3, 2, 20, {1}
        )
        
        self.assertEqual(result, [])

    def test_impossible_happiness_threshold(self):
        N = 2
        flights = [(0, 1, 100, 1)]
        hotels = [(0, 50, 1), (1, 50, 1)]
        activities = [(0, "Activity", 50, 1), (1, "Activity", 50, 1)]
        
        result = optimize_vacation_plan(
            N, flights, hotels, activities,
            0, 1000, 3, 2, 100, {1}
        )
        
        self.assertEqual(result, [])

    def test_complex_vacation(self):
        N = 4
        flights = [
            (0, 1, 100, 10), (1, 2, 150, 15),
            (2, 3, 120, 12), (3, 0, 200, 20),
            (1, 3, 180, 18), (2, 0, 160, 16)
        ]
        hotels = [
            (0, 50, 5), (1, 60, 6),
            (2, 70, 7), (3, 80, 8)
        ]
        activities = [
            (0, "Beach", 30, 8),
            (1, "Sightseeing", 40, 10),
            (2, "Museum", 35, 9),
            (3, "Mountain", 45, 11)
        ]
        
        result = optimize_vacation_plan(
            N, flights, hotels, activities,
            0, 1000, 7, 4, 100, {1, 2, 3}
        )
        
        self.assertIsNotNone(result)
        self.assertGreater(len(result), 0)
        
        # Verify structure of returned actions
        for action in result:
            self.assertIsInstance(action, tuple)
            self.assertIn(action[0], ["flight", "hotel", "activity"])
            
            if action[0] == "flight":
                self.assertEqual(len(action), 3)
            elif action[0] == "hotel":
                self.assertEqual(len(action), 3)
                self.assertIsInstance(action[2], int)
            elif action[0] == "activity":
                self.assertEqual(len(action), 3)
                self.assertIsInstance(action[2], str)

    def test_no_valid_path(self):
        N = 3
        flights = [(0, 1, 100, 10)]  # No way to reach city 2
        hotels = [(0, 50, 5), (1, 60, 6), (2, 70, 7)]
        activities = [
            (0, "Activity", 30, 8),
            (1, "Activity", 40, 10),
            (2, "Activity", 35, 9)
        ]
        
        result = optimize_vacation_plan(
            N, flights, hotels, activities,
            0, 1000, 5, 3, 50, {2}
        )
        
        self.assertEqual(result, [])

    def test_exact_duration(self):
        N = 2
        flights = [(0, 1, 100, 10), (1, 0, 100, 10)]
        hotels = [(0, 50, 5), (1, 60, 6)]
        activities = [
            (0, "Activity", 30, 8),
            (1, "Activity", 40, 10)
        ]
        
        result = optimize_vacation_plan(
            N, flights, hotels, activities,
            0, 500, 4, 3, 30, {1}
        )
        
        if result:
            total_days = 0
            for action in result:
                if action[0] == "hotel":
                    total_days += action[2]
                elif action[0] == "flight":
                    total_days += 1
            
            self.assertEqual(total_days, 4)

    def test_minimum_stay_requirement(self):
        N = 2
        flights = [(0, 1, 100, 10), (1, 0, 100, 10)]
        hotels = [(0, 50, 5), (1, 60, 6)]
        activities = [
            (0, "Activity", 30, 8),
            (1, "Activity", 40, 10)
        ]
        
        result = optimize_vacation_plan(
            N, flights, hotels, activities,
            0, 500, 5, 4, 30, {1}
        )
        
        if result:
            total_hotel_nights = 0
            for action in result:
                if action[0] == "hotel":
                    total_hotel_nights += action[2]
            
            self.assertGreaterEqual(total_hotel_nights, 4)

    def test_budget_constraint(self):
        N = 2
        flights = [(0, 1, 100, 10), (1, 0, 100, 10)]
        hotels = [(0, 50, 5), (1, 60, 6)]
        activities = [
            (0, "Activity", 30, 8),
            (1, "Activity", 40, 10)
        ]
        budget = 300
        
        result = optimize_vacation_plan(
            N, flights, hotels, activities,
            0, budget, 4, 2, 30, {1}
        )
        
        if result:
            total_cost = 0
            for action in result:
                if action[0] == "flight":
                    for f in flights:
                        if f[0] == action[1] and f[1] == action[2]:
                            total_cost += f[2]
                elif action[0] == "hotel":
                    for h in hotels:
                        if h[0] == action[1]:
                            total_cost += h[1] * action[2]
                elif action[0] == "activity":
                    for a in activities:
                        if a[0] == action[1] and a[1] == action[2]:
                            total_cost += a[2]
            
            self.assertLessEqual(total_cost, budget)

if __name__ == '__main__':
    unittest.main()