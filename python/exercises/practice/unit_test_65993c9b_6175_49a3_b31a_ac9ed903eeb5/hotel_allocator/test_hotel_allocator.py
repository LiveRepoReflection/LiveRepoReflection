import unittest
from hotel_allocator import allocate_hotels

class TestHotelAllocator(unittest.TestCase):
    def test_basic_allocation(self):
        employees = [
            {"id": "e1", "department": "eng", "colleague_preferences": {"e2": 1}},
            {"id": "e2", "department": "eng", "colleague_preferences": {"e1": 1}},
            {"id": "e3", "department": "sales", "colleague_preferences": {}}
        ]
        hotels = [
            {"id": "h1", "capacity": 2, "rate_per_night": 100},
            {"id": "h2", "capacity": 1, "rate_per_night": 150}
        ]
        result = allocate_hotels(
            employees=employees,
            hotels=hotels,
            department_limit_per_hotel=2,
            affinity_penalty=10,
            num_nights=3,
            target_hotel_utilization=0.8,
            underutilization_penalty_per_employee=50,
            colleague_stay_together_bonus=5
        )
        
        self.assertIn("hotel_allocations", result)
        self.assertIn("total_cost", result)
        self.assertEqual(len(result["hotel_allocations"]), 2)
        
        # Check all employees are allocated
        allocated_employees = sum(len(v) for v in result["hotel_allocations"].values())
        self.assertEqual(allocated_employees, 3)

    def test_department_constraints(self):
        employees = [
            {"id": "e1", "department": "eng", "colleague_preferences": {}},
            {"id": "e2", "department": "eng", "colleague_preferences": {}},
            {"id": "e3", "department": "eng", "colleague_preferences": {}}
        ]
        hotels = [
            {"id": "h1", "capacity": 3, "rate_per_night": 100},
            {"id": "h2", "capacity": 3, "rate_per_night": 100}
        ]
        result = allocate_hotels(
            employees=employees,
            hotels=hotels,
            department_limit_per_hotel=2,
            affinity_penalty=10,
            num_nights=3,
            target_hotel_utilization=0.8,
            underutilization_penalty_per_employee=50,
            colleague_stay_together_bonus=5
        )
        
        # Verify department limit is respected
        for hotel, emps in result["hotel_allocations"].items():
            dept_counts = {}
            for e in emps:
                dept = next(emp["department"] for emp in employees if emp["id"] == e)
                dept_counts[dept] = dept_counts.get(dept, 0) + 1
            self.assertTrue(all(v <= 2 for v in dept_counts.values()))

    def test_affinity_optimization(self):
        employees = [
            {"id": "e1", "department": "eng", "colleague_preferences": {"e2": 5, "e3": -3}},
            {"id": "e2", "department": "eng", "colleague_preferences": {"e1": 5}},
            {"id": "e3", "department": "eng", "colleague_preferences": {"e1": -3}}
        ]
        hotels = [
            {"id": "h1", "capacity": 2, "rate_per_night": 100},
            {"id": "h2", "capacity": 1, "rate_per_night": 100}
        ]
        result = allocate_hotels(
            employees=employees,
            hotels=hotels,
            department_limit_per_hotel=2,
            affinity_penalty=10,
            num_nights=3,
            target_hotel_utilization=0.8,
            underutilization_penalty_per_employee=50,
            colleague_stay_together_bonus=5
        )
        
        # Verify e1 and e2 are together (positive affinity)
        allocations = result["hotel_allocations"]
        for hotel, emps in allocations.items():
            if "e1" in emps and "e2" in emps:
                break
        else:
            self.fail("Employees with positive affinity not allocated together")

    def test_underutilization_penalty(self):
        employees = [{"id": f"e{i}", "department": "eng", "colleague_preferences": {}} for i in range(5)]
        hotels = [
            {"id": "h1", "capacity": 3, "rate_per_night": 100},
            {"id": "h2", "capacity": 3, "rate_per_night": 100}
        ]
        result = allocate_hotels(
            employees=employees,
            hotels=hotels,
            department_limit_per_hotel=3,
            affinity_penalty=10,
            num_nights=3,
            target_hotel_utilization=0.9,
            underutilization_penalty_per_employee=50,
            colleague_stay_together_bonus=5
        )
        
        # Verify underutilization penalty is considered
        for hotel, emps in result["hotel_allocations"].items():
            if len(emps) < 2.7:  # 3 * 0.9
                self.assertGreater(result["total_cost"], 1500)  # base cost without penalty

    def test_insufficient_capacity(self):
        employees = [{"id": f"e{i}", "department": "eng", "colleague_preferences": {}} for i in range(5)]
        hotels = [
            {"id": "h1", "capacity": 2, "rate_per_night": 100},
            {"id": "h2", "capacity": 2, "rate_per_night": 100}
        ]
        with self.assertRaises(ValueError):
            allocate_hotels(
                employees=employees,
                hotels=hotels,
                department_limit_per_hotel=2,
                affinity_penalty=10,
                num_nights=3,
                target_hotel_utilization=0.8,
                underutilization_penalty_per_employee=50,
                colleague_stay_together_bonus=5
            )

if __name__ == "__main__":
    unittest.main()