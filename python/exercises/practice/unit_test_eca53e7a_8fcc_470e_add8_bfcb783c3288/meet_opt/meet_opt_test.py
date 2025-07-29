import unittest
from datetime import datetime, timedelta
import pytz

from meet_opt import schedule_meeting

def isoformat(dt):
    return dt.isoformat()

class TestMeetOpt(unittest.TestCase):
    def setUp(self):
        # Common time window for tests
        self.time_window = ("2024-12-01T00:00:00+00:00", "2024-12-01T23:59:59+00:00")
        self.meeting_duration = 60  # minutes

    def test_empty_employee_list(self):
        employee_data = []
        department_data = []
        result = schedule_meeting(employee_data, department_data, self.meeting_duration, self.time_window)
        self.assertEqual(result, [])

    def test_insufficient_department_representation(self):
        # Two employees, but department requirement not met.
        employee_data = [
            {
                "employee_id": 1,
                "department_id": 1,
                "timezone": "America/Los_Angeles",
                "availability": [
                    ("2024-12-01T07:00:00-08:00", "2024-12-01T09:00:00-08:00")
                ]
            }
        ]
        department_data = [
            {"department_id": 1, "required_attendees": 1},
            {"department_id": 2, "required_attendees": 1}
        ]
        result = schedule_meeting(employee_data, department_data, self.meeting_duration, self.time_window)
        self.assertEqual(result, [])

    def test_basic_schedule(self):
        # Two departments:
        # Department 1 requires 1 employee; Department 2 requires 2 employees.
        # Create employees across different time zones with overlapping intervals.
        employee_data = [
            {
                "employee_id": 1,
                "department_id": 1,
                "timezone": "America/Los_Angeles",  # PST: offset -08:00
                "availability": [
                    # 07:00-09:00 PST => 15:00-17:00 UTC
                    ("2024-12-01T07:00:00-08:00", "2024-12-01T09:00:00-08:00")
                ]
            },
            {
                "employee_id": 2,
                "department_id": 1,
                "timezone": "Europe/London",  # UTC+0
                "availability": [
                    # 15:00-18:00 UTC
                    ("2024-12-01T15:00:00+00:00", "2024-12-01T18:00:00+00:00")
                ]
            },
            {
                "employee_id": 3,
                "department_id": 2,
                "timezone": "Asia/Tokyo",  # UTC+9
                "availability": [
                    # 23:00-01:00 JST => 14:00-16:00 UTC
                    ("2024-12-01T23:00:00+09:00", "2024-12-02T01:00:00+09:00")
                ]
            },
            {
                "employee_id": 4,
                "department_id": 2,
                "timezone": "Europe/London",  # UTC+0
                "availability": [
                    # 14:00-16:00 UTC
                    ("2024-12-01T14:00:00+00:00", "2024-12-01T16:00:00+00:00")
                ]
            },
            {
                "employee_id": 5,
                "department_id": 2,
                "timezone": "America/Los_Angeles",  # PST: offset -08:00
                "availability": [
                    # 06:00-08:00 PST => 14:00-16:00 UTC
                    ("2024-12-01T06:00:00-08:00", "2024-12-01T08:00:00-08:00")
                ]
            }
        ]
        department_data = [
            {"department_id": 1, "required_attendees": 1},
            {"department_id": 2, "required_attendees": 2}
        ]
        result = schedule_meeting(employee_data, department_data, self.meeting_duration, self.time_window)
        # The minimal valid meeting should consist of 1 from department 1 and 2 from department 2.
        # The only possible overlapping meeting window is from 15:00 to 16:00 UTC.
        # Check that returned employee ids meet department requirements.
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 3)
        dept1_ids = {e["employee_id"] for e in employee_data if e["department_id"] == 1}
        dept2_ids = {e["employee_id"] for e in employee_data if e["department_id"] == 2}
        count_dept1 = sum(1 for emp_id in result if emp_id in dept1_ids)
        count_dept2 = sum(1 for emp_id in result if emp_id in dept2_ids)
        self.assertGreaterEqual(count_dept1, 1)
        self.assertGreaterEqual(count_dept2, 2)
        # Check returned ids are sorted in ascending order.
        self.assertEqual(result, sorted(result))

    def test_priority_attendees_inclusion(self):
        # Test when priority attendees are provided.
        employee_data = [
            {
                "employee_id": 1,
                "department_id": 1,
                "timezone": "Europe/London",
                "availability": [
                    ("2024-12-01T10:00:00+00:00", "2024-12-01T12:00:00+00:00")
                ]
            },
            {
                "employee_id": 2,
                "department_id": 2,
                "timezone": "Europe/London",
                "availability": [
                    ("2024-12-01T10:00:00+00:00", "2024-12-01T13:00:00+00:00")
                ]
            },
            {
                "employee_id": 3,
                "department_id": 2,
                "timezone": "Europe/London",
                "availability": [
                    ("2024-12-01T09:30:00+00:00", "2024-12-01T12:30:00+00:00")
                ]
            },
            {
                "employee_id": 4,
                "department_id": 2,
                "timezone": "Europe/London",
                "availability": [
                    ("2024-12-01T11:00:00+00:00", "2024-12-01T14:00:00+00:00")
                ]
            }
        ]
        department_data = [
            {"department_id": 1, "required_attendees": 1},
            {"department_id": 2, "required_attendees": 2}
        ]
        priority_attendees = [1, 2]
        result = schedule_meeting(employee_data, department_data, self.meeting_duration, self.time_window, priority_attendees)
        # Check that priority attendees are included if possible.
        for emp_id in priority_attendees:
            self.assertIn(emp_id, result)
        # Check overall department representation
        dept1_ids = {e["employee_id"] for e in employee_data if e["department_id"] == 1}
        dept2_ids = {e["employee_id"] for e in employee_data if e["department_id"] == 2}
        count_dept1 = sum(1 for emp_id in result if emp_id in dept1_ids)
        count_dept2 = sum(1 for emp_id in result if emp_id in dept2_ids)
        self.assertGreaterEqual(count_dept1, 1)
        self.assertGreaterEqual(count_dept2, 2)
        self.assertEqual(result, sorted(result))

    def test_no_overlapping_availability(self):
        # Create a scenario where there is no overlapping window that meets meeting duration.
        employee_data = [
            {
                "employee_id": 1,
                "department_id": 1,
                "timezone": "America/Los_Angeles",
                "availability": [
                    ("2024-12-01T07:00:00-08:00", "2024-12-01T07:30:00-08:00")
                ]
            },
            {
                "employee_id": 2,
                "department_id": 2,
                "timezone": "Europe/London",
                "availability": [
                    ("2024-12-01T15:00:00+00:00", "2024-12-01T15:30:00+00:00")
                ]
            }
        ]
        department_data = [
            {"department_id": 1, "required_attendees": 1},
            {"department_id": 2, "required_attendees": 1}
        ]
        result = schedule_meeting(employee_data, department_data, self.meeting_duration, self.time_window)
        self.assertEqual(result, [])

if __name__ == "__main__":
    unittest.main()