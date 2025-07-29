import unittest
from meeting_scheduler.meeting_scheduler import meeting_scheduler

class MeetingSchedulerTest(unittest.TestCase):
    def test_sample_meeting(self):
        # Provided example test case from the problem description
        employees = {
            1: [(0, 4), (8, 12)],
            2: [(2, 6), (10, 14)],
            3: [(0, 2), (4, 6)],
            4: [(10, 12)]
        }
        hierarchy = {
            1: [2, 3],
            2: [4],
            3: []
        }
        attendees = [1, 2, 4]
        duration = 2
        expected = (10, 12)
        self.assertEqual(meeting_scheduler(employees, hierarchy, attendees, duration), expected)

    def test_no_common_availability(self):
        # Test case where no meeting slot exists because attendees have no overlapping intervals
        employees = {
            1: [(0, 4)],
            2: [(5, 8)]
        }
        hierarchy = {
            1: [],
            2: []
        }
        attendees = [1, 2]
        duration = 2
        expected = None
        self.assertEqual(meeting_scheduler(employees, hierarchy, attendees, duration), expected)

    def test_interruption_score_optimization(self):
        # Test case where two valid meeting slots exist but they have different interruption scores.
        # The scheduler should pick the slot with the lower interruption score, even if it's not the absolute earliest.
        employees = {
            1: [(0, 3), (5, 9)],
            2: [(1, 4), (6, 10)],
            3: [(2, 5), (8, 12)]  # Non-attendee and descendant of 1
        }
        hierarchy = {
            1: [3],
            2: [],
            3: []
        }
        attendees = [1, 2]
        duration = 2
        # Intersection of first intervals: (1,3) has duration 2 -> overlaps with employee 3 interval (2,5): interruption score 1.
        # Intersection of second intervals: (6,9) -> meeting slot can be (6,8) of duration 2, which does not overlap with employee 3's intervals (2,5) and (8,12) (overlap only at minute 8 is excluded since end of meeting is exclusive).
        # Thus, (6,8) yields an interruption score of 0, and should be selected.
        expected = (6, 8)
        self.assertEqual(meeting_scheduler(employees, hierarchy, attendees, duration), expected)

    def test_tie_break_earliest_slot(self):
        # Test case where two available meeting slots have equal interruption scores.
        # The scheduler should pick the earliest meeting slot.
        employees = {
            1: [(0, 5), (10, 15)],
            2: [(2, 7), (12, 17)],
            3: [(1, 6)],
            4: [(10, 13)],
            5: [(0, 20)]
        }
        hierarchy = {
            1: [3, 5],
            2: [4],
            3: [],
            4: [],
            5: []
        }
        attendees = [1, 2]
        duration = 3
        # Two common intervals:
        #   Intersection of (0,5) & (2,7) is (2,5) -> meeting slot (2,5) duration 3.
        #   Intersection of (10,15) & (12,17) is (12,15) -> meeting slot (12,15) duration 3.
        # Both slots yield the same total interruption score (employee 3, descendant of 1, interrupts on slot (2,5) and employee 5 interrupts both, and descendant of 2, employee 4, interrupts (12,15)).
        # Since scores tie and (2,5) is earlier, expected output is (2,5).
        expected = (2, 5)
        self.assertEqual(meeting_scheduler(employees, hierarchy, attendees, duration), expected)

    def test_edge_case_exact_fit(self):
        # Test when the meeting duration exactly fits an available slot.
        employees = {
            1: [(10, 13)],
            2: [(10, 13)],
            3: [(8, 12)]
        }
        hierarchy = {
            1: [3],
            2: [],
            3: []
        }
        attendees = [1, 2]
        duration = 3  # The slot (10,13) fits exactly
        expected = (10, 13)
        self.assertEqual(meeting_scheduler(employees, hierarchy, attendees, duration), expected)

if __name__ == '__main__':
    unittest.main()