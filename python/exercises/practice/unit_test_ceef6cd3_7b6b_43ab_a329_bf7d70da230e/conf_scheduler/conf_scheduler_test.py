import unittest
from conf_scheduler import schedule_conference

class ConferenceSchedulerTest(unittest.TestCase):
    def test_simple_two_speakers_one_venue(self):
        speakers = {
            1: {
                'availability': [(0, 10)],
                'talk_duration': 3,
                'venue_requirement': 1
            },
            2: {
                'availability': [(0, 10)],
                'talk_duration': 4,
                'venue_requirement': 1
            }
        }
        venue_capacities = {1: 100}
        speaker_dependencies = [(2, 1)]  # speaker 2 depends on speaker 1
        speaker_capacities = {1: 50, 2: 60}
        conference_start_time = 0
        conference_end_time = 10

        expected = [(1, 0), (2, 3)]
        result = schedule_conference(
            speakers,
            venue_capacities,
            speaker_dependencies,
            speaker_capacities,
            conference_start_time,
            conference_end_time
        )
        self.assertEqual(result, expected)

    def test_no_valid_schedule_due_to_capacity(self):
        speakers = {
            1: {
                'availability': [(0, 5)],
                'talk_duration': 2,
                'venue_requirement': 1
            }
        }
        venue_capacities = {1: 40}
        speaker_dependencies = []
        speaker_capacities = {1: 50}  # requires more capacity than venue has
        conference_start_time = 0
        conference_end_time = 5

        expected = []
        result = schedule_conference(
            speakers,
            venue_capacities,
            speaker_dependencies,
            speaker_capacities,
            conference_start_time,
            conference_end_time
        )
        self.assertEqual(result, expected)

    def test_complex_dependencies(self):
        speakers = {
            1: {
                'availability': [(0, 20)],
                'talk_duration': 3,
                'venue_requirement': 1
            },
            2: {
                'availability': [(0, 20)],
                'talk_duration': 4,
                'venue_requirement': 1
            },
            3: {
                'availability': [(0, 20)],
                'talk_duration': 2,
                'venue_requirement': 1
            }
        }
        venue_capacities = {1: 100}
        speaker_dependencies = [(2, 1), (3, 2)]  # 3 depends on 2, 2 depends on 1
        speaker_capacities = {1: 50, 2: 60, 3: 40}
        conference_start_time = 0
        conference_end_time = 20

        result = schedule_conference(
            speakers,
            venue_capacities,
            speaker_dependencies,
            speaker_capacities,
            conference_start_time,
            conference_end_time
        )
        
        # Check if dependencies are respected
        speaker_times = {speaker: time for speaker, time in result}
        self.assertIn(1, speaker_times)
        self.assertIn(2, speaker_times)
        self.assertIn(3, speaker_times)
        self.assertLess(speaker_times[1], speaker_times[2])
        self.assertLess(speaker_times[2], speaker_times[3])

    def test_multiple_venues(self):
        speakers = {
            1: {
                'availability': [(0, 10)],
                'talk_duration': 3,
                'venue_requirement': 1
            },
            2: {
                'availability': [(0, 10)],
                'talk_duration': 3,
                'venue_requirement': 2
            }
        }
        venue_capacities = {1: 100, 2: 100}
        speaker_dependencies = []
        speaker_capacities = {1: 50, 2: 50}
        conference_start_time = 0
        conference_end_time = 10

        result = schedule_conference(
            speakers,
            venue_capacities,
            speaker_dependencies,
            speaker_capacities,
            conference_start_time,
            conference_end_time
        )
        
        # Both talks can happen simultaneously
        self.assertEqual(len(result), 2)
        times = [time for _, time in result]
        self.assertEqual(times[0], times[1])

    def test_limited_availability(self):
        speakers = {
            1: {
                'availability': [(0, 5), (10, 15)],  # split availability
                'talk_duration': 3,
                'venue_requirement': 1
            }
        }
        venue_capacities = {1: 100}
        speaker_dependencies = []
        speaker_capacities = {1: 50}
        conference_start_time = 0
        conference_end_time = 15

        result = schedule_conference(
            speakers,
            venue_capacities,
            speaker_dependencies,
            speaker_capacities,
            conference_start_time,
            conference_end_time
        )
        
        self.assertEqual(len(result), 1)
        _, start_time = result[0]
        self.assertTrue(
            (0 <= start_time <= 2) or  # fits in first slot
            (10 <= start_time <= 12)    # fits in second slot
        )

    def test_invalid_inputs(self):
        # Test with empty speakers
        with self.assertRaises(ValueError):
            schedule_conference(
                {},
                {1: 100},
                [],
                {},
                0,
                10
            )

        # Test with negative times
        with self.assertRaises(ValueError):
            schedule_conference(
                {1: {
                    'availability': [(-1, 5)],
                    'talk_duration': 3,
                    'venue_requirement': 1
                }},
                {1: 100},
                [],
                {1: 50},
                0,
                10
            )

        # Test with circular dependencies
        with self.assertRaises(ValueError):
            schedule_conference(
                {
                    1: {
                        'availability': [(0, 10)],
                        'talk_duration': 3,
                        'venue_requirement': 1
                    },
                    2: {
                        'availability': [(0, 10)],
                        'talk_duration': 3,
                        'venue_requirement': 1
                    }
                },
                {1: 100},
                [(1, 2), (2, 1)],  # circular dependency
                {1: 50, 2: 50},
                0,
                10
            )

if __name__ == '__main__':
    unittest.main()