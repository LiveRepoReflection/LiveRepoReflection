import unittest
from conference_scheduler import schedule_conference

class TestConferenceScheduler(unittest.TestCase):
    def test_basic_scheduling(self):
        talks = [
            {"talk_id": 1, "capacity": 3, "preferred_attendees": {1, 2, 3}},
            {"talk_id": 2, "capacity": 2, "preferred_attendees": {4, 5}}
        ]
        attendees = [
            {"attendee_id": 1, "preferred_talks": [1], "affinity_group_id": 1},
            {"attendee_id": 2, "preferred_talks": [1], "affinity_group_id": 1},
            {"attendee_id": 3, "preferred_talks": [1], "affinity_group_id": 2},
            {"attendee_id": 4, "preferred_talks": [2], "affinity_group_id": 3},
            {"attendee_id": 5, "preferred_talks": [2], "affinity_group_id": 3}
        ]
        affinity_groups = {1: 2, 2: 1, 3: 2}
        k = 5
        
        result = schedule_conference(talks, attendees, affinity_groups, k)
        self.assertEqual(len(result[1]), 3)
        self.assertEqual(len(result[2]), 2)
        self.assertTrue({1, 2}.issubset(result[1]))
        self.assertTrue({4, 5}.issubset(result[2]))

    def test_capacity_constraints(self):
        talks = [
            {"talk_id": 1, "capacity": 1, "preferred_attendees": {1, 2}}
        ]
        attendees = [
            {"attendee_id": 1, "preferred_talks": [1], "affinity_group_id": 1},
            {"attendee_id": 2, "preferred_talks": [1], "affinity_group_id": 1}
        ]
        affinity_groups = {1: 2}
        k = 5
        
        result = schedule_conference(talks, attendees, affinity_groups, k)
        self.assertEqual(len(result[1]), 1)

    def test_affinity_group_priority(self):
        talks = [
            {"talk_id": 1, "capacity": 3, "preferred_attendees": {1, 2, 3, 4}},
            {"talk_id": 2, "capacity": 1, "preferred_attendees": {3}}
        ]
        attendees = [
            {"attendee_id": 1, "preferred_talks": [1], "affinity_group_id": 1},
            {"attendee_id": 2, "preferred_talks": [1], "affinity_group_id": 1},
            {"attendee_id": 3, "preferred_talks": [1, 2], "affinity_group_id": 2},
            {"attendee_id": 4, "preferred_talks": [1], "affinity_group_id": 3}
        ]
        affinity_groups = {1: 2, 2: 1, 3: 1}
        k = 10
        
        result = schedule_conference(talks, attendees, affinity_groups, k)
        self.assertTrue({1, 2}.issubset(result[1]))

    def test_no_solution_possible(self):
        talks = [
            {"talk_id": 1, "capacity": 1, "preferred_attendees": {1, 2}}
        ]
        attendees = [
            {"attendee_id": 1, "preferred_talks": [1], "affinity_group_id": 1},
            {"attendee_id": 2, "preferred_talks": [1], "affinity_group_id": 1},
            {"attendee_id": 3, "preferred_talks": [1], "affinity_group_id": 1}
        ]
        affinity_groups = {1: 3}
        k = 5
        
        result = schedule_conference(talks, attendees, affinity_groups, k)
        self.assertEqual(len(result[1]), 1)

    def test_large_input_performance(self):
        talks = [{"talk_id": i, "capacity": 10, "preferred_attendees": set(range(100))} for i in range(100)]
        attendees = [{"attendee_id": i, "preferred_talks": list(range(100)), "affinity_group_id": i%10} for i in range(100)]
        affinity_groups = {i: 10 for i in range(10)}
        k = 5
        
        result = schedule_conference(talks, attendees, affinity_groups, k)
        self.assertTrue(all(len(assignment) <= 10 for assignment in result.values()))

if __name__ == '__main__':
    unittest.main()