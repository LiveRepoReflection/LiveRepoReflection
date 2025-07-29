import unittest
from conference_schedule.scheduler import schedule_conference

class ConferenceScheduleTest(unittest.TestCase):
    def setUp(self):
        # Common talks and rooms for use in multiple tests
        self.talks = [
            {'id': 1, 'startTime': 540, 'endTime': 600, 'expectedAttendance': 100, 'keywords': ['AI', 'ML']},
            {'id': 2, 'startTime': 540, 'endTime': 600, 'expectedAttendance': 80, 'keywords': ['Data Science', 'Statistics']},
            {'id': 3, 'startTime': 600, 'endTime': 660, 'expectedAttendance': 120, 'keywords': ['AI', 'Robotics']},
            {'id': 4, 'startTime': 600, 'endTime': 660, 'expectedAttendance': 90, 'keywords': ['Cloud', 'Security']},
            {'id': 5, 'startTime': 660, 'endTime': 720, 'expectedAttendance': 70, 'keywords': ['AI', 'Robotics', 'Data Mining']},
            {'id': 6, 'startTime': 700, 'endTime': 760, 'expectedAttendance': 110, 'keywords': ['Big Data', 'Analytics']},
        ]
        self.rooms = [{'id': 'A'}, {'id': 'B'}]
        self.conferenceDuration = 720  # e.g., 12 hours from minute 0 to 720
        self.K = 4
        self.penaltyFactor = 0.5

    def get_talk_by_id(self, talks, talk_id):
        for talk in talks:
            if talk['id'] == talk_id:
                return talk
        return None

    def validate_room_schedule(self, room_schedule, talks_dict):
        """Ensure that talks in a room do not overlap and are sorted by start time."""
        last_end = -1
        for talk_id in room_schedule:
            talk = talks_dict.get(talk_id)
            self.assertIsNotNone(talk, f"Talk id {talk_id} not found in provided talks")
            self.assertGreaterEqual(talk['startTime'], last_end,
                                    f"Talk id {talk_id} starts before previous talk ended.")
            last_end = talk['endTime']

    def test_empty_talks(self):
        talks = []
        rooms = [{'id': 'R1'}, {'id': 'R2'}]
        schedule = schedule_conference(talks, rooms, self.conferenceDuration, self.K, self.penaltyFactor)
        # Expect each room to have an empty schedule
        for room in rooms:
            self.assertIn(room['id'], schedule)
            self.assertEqual(schedule[room['id']], [])

    def test_single_talk(self):
        talks = [
            {'id': 10, 'startTime': 300, 'endTime': 360, 'expectedAttendance': 50, 'keywords': ['Networking']}
        ]
        rooms = [{'id': 'Main'}]
        schedule = schedule_conference(talks, rooms, self.conferenceDuration, self.K, self.penaltyFactor)
        self.assertIn('Main', schedule)
        self.assertEqual(schedule['Main'], [10])

    def test_non_overlapping_schedule(self):
        # Use the common self.talks
        schedule = schedule_conference(self.talks, self.rooms, self.conferenceDuration, self.K, self.penaltyFactor)
        # Build a dictionary for quick access to talk data by id.
        talks_dict = {talk['id']: talk for talk in self.talks}

        # Check that all scheduled talks exist in the provided talk list.
        scheduled_ids = set()
        for room in self.rooms:
            room_id = room['id']
            self.assertIn(room_id, schedule, f"Room {room_id} missing from schedule.")
            for talk_id in schedule[room_id]:
                self.assertIn(talk_id, talks_dict, f"Talk id {talk_id} scheduled in room {room_id} but not in input talks.")
                scheduled_ids.add(talk_id)

            # Ensure the talks in the room are sorted by startTime and do not overlap.
            self.validate_room_schedule(schedule[room_id], talks_dict)

        # Ensure each talk is scheduled at most once.
        self.assertEqual(len(scheduled_ids), len(set(scheduled_ids)), "Duplicate talk assignments found.")

    def test_overlapping_talks_across_rooms(self):
        # Construct talks that overlap in time.
        talks = [
            {'id': 20, 'startTime': 480, 'endTime': 540, 'expectedAttendance': 100, 'keywords': ['Cloud']},
            {'id': 21, 'startTime': 480, 'endTime': 540, 'expectedAttendance': 90, 'keywords': ['Security']},
            {'id': 22, 'startTime': 480, 'endTime': 540, 'expectedAttendance': 80, 'keywords': ['Cloud', 'ML']},
            {'id': 23, 'startTime': 540, 'endTime': 600, 'expectedAttendance': 110, 'keywords': ['Data']},
        ]
        rooms = [{'id': 'X'}, {'id': 'Y'}]
        schedule = schedule_conference(talks, rooms, self.conferenceDuration, self.K, self.penaltyFactor)
        talks_dict = {talk['id']: talk for talk in talks}

        # For overlapping talks within the same timeslot across different rooms,
        # ensure that they don't violate the room overlapping constraint.
        for room in rooms:
            room_id = room['id']
            self.assertIn(room_id, schedule, f"Room {room_id} missing from schedule.")
            self.validate_room_schedule(schedule[room_id], talks_dict)

    def test_full_schedule_constraints(self):
        # Use a more complex scenario including multiple time intervals.
        talks = [
            {'id': 31, 'startTime': 480, 'endTime': 540, 'expectedAttendance': 150, 'keywords': ['AI', 'ML']},
            {'id': 32, 'startTime': 480, 'endTime': 540, 'expectedAttendance': 130, 'keywords': ['Data', 'Science']},
            {'id': 33, 'startTime': 540, 'endTime': 600, 'expectedAttendance': 160, 'keywords': ['AI', 'Robotics']},
            {'id': 34, 'startTime': 540, 'endTime': 600, 'expectedAttendance': 140, 'keywords': ['Big Data', 'Analytics']},
            {'id': 35, 'startTime': 600, 'endTime': 660, 'expectedAttendance': 120, 'keywords': ['Networking']},
            {'id': 36, 'startTime': 600, 'endTime': 660, 'expectedAttendance': 115, 'keywords': ['Security', 'Cloud']},
            {'id': 37, 'startTime': 660, 'endTime': 720, 'expectedAttendance': 100, 'keywords': ['Blockchain']},
            {'id': 38, 'startTime': 660, 'endTime': 720, 'expectedAttendance': 95,  'keywords': ['Cybersecurity']},
        ]
        rooms = [{'id': 'R1'}, {'id': 'R2'}, {'id': 'R3'}]
        schedule = schedule_conference(talks, rooms, self.conferenceDuration, self.K, self.penaltyFactor)
        talks_dict = {talk['id']: talk for talk in talks}

        # Validate each room's schedule for ordering and overlapping.
        for room in rooms:
            room_id = room['id']
            self.assertIn(room_id, schedule, f"Room {room_id} missing from schedule.")
            self.validate_room_schedule(schedule[room_id], talks_dict)

        # Verify that no talk is scheduled more than once.
        scheduled_talks = []
        for talk_ids in schedule.values():
            scheduled_talks.extend(talk_ids)
        self.assertEqual(len(scheduled_talks), len(set(scheduled_talks)),
                         "A talk appears multiple times in different rooms.")

        # Check that all scheduled talks fall within the conference duration.
        for talk_id in scheduled_talks:
            talk = talks_dict[talk_id]
            self.assertGreaterEqual(talk['startTime'], 0)
            self.assertLessEqual(talk['endTime'], self.conferenceDuration)

if __name__ == '__main__':
    unittest.main()