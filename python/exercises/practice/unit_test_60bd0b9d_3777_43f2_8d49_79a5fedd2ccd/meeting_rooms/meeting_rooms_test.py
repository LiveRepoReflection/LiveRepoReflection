import unittest
from meeting_rooms import meeting_rooms

class MeetingRoomsTest(unittest.TestCase):
    def test_no_busy_intervals(self):
        # All employees are free all day; meetings can be scheduled one after another in a single room.
        employees = [
            [],
            [],
            []
        ]
        meeting_requests = [
            ([0], 60),
            ([1, 2], 30),
            ([0, 2], 45)
        ]
        self.assertEqual(meeting_rooms(employees, meeting_requests), 1)

    def test_single_employee_forced_overlap(self):
        # Single employee with only one free slot [100,120].
        # Two meetings for this employee, each 20 minutes long, must both occur in the only available slot.
        employees = [
            [(0, 100), (120, 1440)]
        ]
        meeting_requests = [
            ([0], 20),
            ([0], 20)
        ]
        self.assertEqual(meeting_rooms(employees, meeting_requests), 2)

    def test_multi_employee_forced_overlap(self):
        # Two employees each with identical forced free slot [100,120].
        # Two meetings requiring both employees must be scheduled exactly in the only free interval.
        employees = [
            [(0, 100), (120, 1440)],
            [(0, 100), (120, 1440)]
        ]
        meeting_requests = [
            ([0, 1], 20),
            ([0, 1], 20)
        ]
        self.assertEqual(meeting_rooms(employees, meeting_requests), 2)

    def test_mixed_scenario(self):
        # Employees have multiple busy slots, yielding flexible free intervals.
        # An optimal scheduling can arrange the meetings sequentially.
        employees = [
            [(60, 90), (300, 400)],   # Employee 0: Free periods: [0,60], [90,300], [400,1440]
            [(0, 50), (200, 250)],     # Employee 1: Free periods: [50,200], [250,1440]
            [(100, 150)]              # Employee 2: Free periods: [0,100], [150,1440]
        ]
        meeting_requests = [
            ([0, 1], 30),
            ([1, 2], 40),
            ([0, 2], 20),
            ([0, 1, 2], 15)
        ]
        self.assertEqual(meeting_rooms(employees, meeting_requests), 1)

    def test_full_day_meeting(self):
        # Meeting spanning the full day with all employees free.
        employees = [[] for _ in range(4)]
        meeting_requests = [
            ([0, 1, 2, 3], 1440)
        ]
        self.assertEqual(meeting_rooms(employees, meeting_requests), 1)

    def test_complex_overlap(self):
        # Three employees with narrow free intervals:
        # Employee 0 free: [50,200]
        # Employee 1 free: [80,120]
        # Employee 2 free: [100,130]
        # Meeting A: ([0,1,2], 20) => Forced into [100,120]
        # Meeting B: ([0,1], 10)    => Flexible between [80,120]
        # Meeting C: ([1,2], 10)    => Forced into [100,120]
        # Meetings A and C must occur in the same fixed interval, requiring 2 rooms.
        employees = [
            [(0, 50), (200, 1440)],
            [(0, 80), (120, 1440)],
            [(0, 100), (130, 1440)]
        ]
        meeting_requests = [
            ([0, 1, 2], 20),
            ([0, 1], 10),
            ([1, 2], 10)
        ]
        self.assertEqual(meeting_rooms(employees, meeting_requests), 2)

if __name__ == '__main__':
    unittest.main()