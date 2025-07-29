import unittest
from train_schedule import schedule_trains

class TestTrainSchedule(unittest.TestCase):
    def test_single_train(self):
        # Single train on a simple 2-station network without maintenance.
        N = 2
        M = 1
        tracks = [
            (1, 2, 100, 100)  # (station1, station2, length in km, max_speed in km/h)
        ]
        K = 1
        # A single train departing at time 0 with a preferred arrival at 200 minutes.
        trains = [
            (1, 2, 0, 200)
        ]
        a = 10  # acceleration (km/h/minute)
        d = 10  # deceleration (km/h/minute)
        C = 2   # station capacity
        maintenance_schedules = []
        
        # get_speed_limit: constant speed limit for the track.
        def get_speed_limit(station1, station2, time):
            # Since there is only one track, simply return its max_speed.
            return 100
        
        result = schedule_trains(N, M, tracks, K, trains, a, d, C, maintenance_schedules, get_speed_limit)
        self.assertEqual(len(result), 1)
        # The arrival time must be at least the departure time and within the allowed range.
        self.assertGreaterEqual(result[0], trains[0][2])
        self.assertLessEqual(result[0], 2880)
    
    def test_multiple_trains_no_maintenance(self):
        # Two trains on a 3-station network with a capacity constraint at the middle station.
        N = 3
        M = 2
        tracks = [
            (1, 2, 50, 80),   # Track from station 1 to station 2
            (2, 3, 70, 100)   # Track from station 2 to station 3
        ]
        K = 2
        # Two trains departing at different times.
        trains = [
            (1, 3, 0, 150),
            (1, 3, 10, 160)
        ]
        a = 5   # acceleration
        d = 5   # deceleration
        C = 1   # Only one train allowed at a station at a time
        maintenance_schedules = []
        
        # get_speed_limit: returns the track's max speed from the tracks definition.
        def get_speed_limit(station1, station2, time):
            for s1, s2, length, max_speed in tracks:
                if (s1 == station1 and s2 == station2) or (s1 == station2 and s2 == station1):
                    return max_speed
            return 50
        
        result = schedule_trains(N, M, tracks, K, trains, a, d, C, maintenance_schedules, get_speed_limit)
        self.assertEqual(len(result), 2)
        # Both arrival times must be valid and non-decreasing because no overtaking is allowed.
        self.assertGreaterEqual(result[0], trains[0][2])
        self.assertGreaterEqual(result[1], trains[1][2])
        self.assertLessEqual(result[0], result[1])
    
    def test_track_maintenance(self):
        # Single train encountering a maintenance window on its track.
        N = 2
        M = 1
        tracks = [
            (1, 2, 100, 120)
        ]
        K = 1
        # Train departs at 50 minutes. A maintenance period exists on the track.
        trains = [
            (1, 2, 50, 180)
        ]
        a = 5
        d = 5
        C = 2
        # Maintenance on the only track from time 40 to 100 minutes.
        maintenance_schedules = [
            (1, 2, 40, 100)
        ]
        
        # get_speed_limit: Always return the provided max speed when track is available.
        def get_speed_limit(station1, station2, time):
            return 120
        
        result = schedule_trains(N, M, tracks, K, trains, a, d, C, maintenance_schedules, get_speed_limit)
        self.assertEqual(len(result), 1)
        # Since maintenance delays the travel, the actual arrival time should be significantly later than the departure time.
        self.assertGreaterEqual(result[0], 100)
        self.assertGreaterEqual(result[0], trains[0][2])
    
    def test_dynamic_speed_limit(self):
        # Single train on a network where the speed limit changes based on time.
        N = 2
        M = 1
        tracks = [
            (1, 2, 50, 100)
        ]
        K = 1
        trains = [
            (1, 2, 0, 120)
        ]
        a = 5
        d = 5
        C = 2
        maintenance_schedules = []
        
        # Dynamic speed limit: lower speed limit before time 30 and higher afterwards.
        def get_speed_limit(station1, station2, time):
            if time < 30:
                return 50
            else:
                return 100
        
        result = schedule_trains(N, M, tracks, K, trains, a, d, C, maintenance_schedules, get_speed_limit)
        self.assertEqual(len(result), 1)
        self.assertGreaterEqual(result[0], trains[0][2])
        self.assertLessEqual(result[0], 2880)

if __name__ == '__main__':
    unittest.main()