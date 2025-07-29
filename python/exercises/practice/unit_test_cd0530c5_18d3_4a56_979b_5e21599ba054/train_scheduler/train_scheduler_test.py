import unittest
import math
from train_scheduler import schedule_trains

class TestTrainScheduler(unittest.TestCase):

    def setUp(self):
        # Define a helper to check if two float numbers are "close enough"
        self.epsilon = 1e-6

    def check_increasing(self, times):
        # Ensure each subsequent timestamp is strictly increasing
        for i in range(len(times) - 1):
            self.assertGreater(times[i+1], times[i] + self.epsilon, "Timestamps must be strictly increasing.")

    def check_earliest_departure(self, train, schedule):
        # Train: (departure_station, destination_station, earliest_departure_time, priority, route)
        earliest = train[2]
        self.assertGreaterEqual(schedule[0], earliest, "Train departure time must be >= earliest departure time.")

    def check_track_capacity_and_overtaking(self, tracks, trains, schedule):
        # For each track, compute occupancy intervals from schedule
        # Each train segment occupies time interval = [departure_time, departure_time + travel_time]
        # where travel_time = length/speed_limit based on matching track from track list.
        # For each track, if multiple trains use it, verify that at any moment, the count of overlapping intervals
        # does not exceed capacity, and that non-overtaking is maintained (if one train enters earlier, it must exit earlier)
        # Build a dictionary mapping (start, end) to track parameters for quick lookup.
        track_map = {}
        for t in tracks:
            # t: (start_station, end_station, capacity, length, speed_limit)
            key = (t[0], t[1])
            # In test cases, assume only one track exists for each pair.
            track_map[key] = t

        # For each track in track_map, collect occupancy intervals.
        occupancy = {}
        for train_idx, train in enumerate(trains):
            route = train[4]
            times = schedule[train_idx]
            for i in range(len(route)-1):
                key = (route[i], route[i+1])
                if key not in track_map:
                    continue  # This should be caught in the main schedule function as invalid.
                t_info = track_map[key]
                travel_time = t_info[3] / t_info[4]  # length/speed_limit
                start_time = times[i]
                end_time = times[i] + travel_time
                if key not in occupancy:
                    occupancy[key] = []
                occupancy[key].append((start_time, end_time))
        
        # Check capacity constraints with a sweep-line algorithm for each track.
        for key, intervals in occupancy.items():
            capacity = track_map[key][2]
            events = []
            for (s, e) in intervals:
                events.append((s, 1))
                events.append((e, -1))
            events.sort(key=lambda x: (x[0], x[1]))
            current = 0
            for time, delta in events:
                current += delta
                self.assertLessEqual(current, capacity, f"Capacity exceeded on track {key} at time {time}.")

            # Check non-overtaking constraint: after sorting by start time,
            # each train's end time must not exceed that of a train that started later.
            intervals_sorted = sorted(intervals, key=lambda x: x[0])
            for i in range(len(intervals_sorted) - 1):
                s1, e1 = intervals_sorted[i]
                s2, e2 = intervals_sorted[i+1]
                self.assertLessEqual(e1, e2 + self.epsilon, 
                    f"Non-overtaking violated on track {key}: train with start time {s1} exits after train with start time {s2}.")

    def test_basic_schedule(self):
        # Simple network with 3 stations and 2 tracks
        n = 3  # stations 0, 1, 2

        tracks = [
            # (start_station, end_station, capacity, length, speed_limit)
            (0, 1, 2, 60, 60),  # 60 km at 60 km/h -> 1 hour travel
            (1, 2, 2, 60, 60)
        ]

        trains = [
            # (departure_station, destination_station, earliest_departure_time, priority, route)
            (0, 2, 0.0, 10, [0, 1, 2]),
            (0, 2, 5.0, 5, [0, 1, 2])
        ]

        result = schedule_trains(n, tracks, trains)
        self.assertIsNotNone(result, "Schedule must be produced for valid input.")
        self.assertEqual(len(result), len(trains), "Schedule should have an entry for each train.")

        # Check each train's schedule validity:
        for idx, train in enumerate(trains):
            self.assertIn(idx, result, f"Train {idx} missing in schedule.")
            times = result[idx]
            self.assertEqual(len(times), len(train[4]), "Schedule length must match train route length.")
            self.check_increasing(times)
            self.check_earliest_departure(train, times)

        # Check track capacity and non-overtaking constraints:
        self.check_track_capacity_and_overtaking(tracks, trains, result)

    def test_multiple_tracks_parallel_edges(self):
        # Test with parallel tracks between two stations.
        n = 3
        tracks = [
            (0, 1, 1, 100, 50),  # travel time: 2.0 hours, capacity 1
            (0, 1, 2, 100, 50),  # travel time: 2.0 hours, capacity 2 (parallel edge)
            (1, 2, 2, 50, 50)    # travel time: 1.0 hour, capacity 2
        ]

        trains = [
            (0, 2, 0.0, 8, [0, 1, 2]),
            (0, 2, 1.0, 5, [0, 1, 2]),
            (0, 2, 2.0, 7, [0, 1, 2])
        ]

        result = schedule_trains(n, tracks, trains)
        self.assertIsNotNone(result, "A valid schedule should be found for parallel tracks scenario.")
        for idx, train in enumerate(trains):
            times = result[idx]
            self.assertEqual(len(times), len(train[4]), "Schedule length must match train route length.")
            self.check_increasing(times)
            self.check_earliest_departure(train, times)
        # For parallel edges, capacity check per edge is similar.
        self.check_track_capacity_and_overtaking(tracks, trains, result)

    def test_invalid_route(self):
        # Test where train's route references a non-existent track.
        n = 2
        tracks = [
            # Only track available is from 0 to 1
            (0, 1, 1, 50, 50)
        ]
        trains = [
            # This train's route is invalid because there is no track from 1 to 0.
            (0, 0, 0.0, 5, [0, 1, 0])
        ]
        result = schedule_trains(n, tracks, trains)
        self.assertIsNone(result, "Schedule should be None when route is invalid (missing track).")
    
    def test_edge_case_single_train(self):
        # Test with a single train where the schedule should simply adhere to earliest departure.
        n = 4
        tracks = [
            (0, 1, 1, 80, 80),
            (1, 2, 1, 40, 40),
            (2, 3, 1, 120, 60)
        ]
        trains = [
            (0, 3, 10.0, 10, [0, 1, 2, 3])
        ]
        result = schedule_trains(n, tracks, trains)
        self.assertIsNotNone(result, "Schedule must be produced for single train scenario.")
        times = result[0]
        self.assertEqual(len(times), 4)
        self.check_increasing(times)
        self.check_earliest_departure(trains[0], times)

        # Verify travel times equal to calculated travel times.
        expected_times = []
        # Track 0->1: 80/80 = 1.0 hour
        # Track 1->2: 40/40 = 1.0 hour
        # Track 2->3: 120/60 = 2.0 hours
        expected_intervals = [1.0, 1.0, 2.0]
        # The schedule may introduce additional waiting time to optimize weighted average travel time.
        # Therefore, we check that travel time is at least the minimum travel time.
        for i in range(1, len(times)):
            min_interval = expected_intervals[i-1]
            self.assertGreaterEqual(times[i] - times[i-1], min_interval - self.epsilon,
                "Segment travel time must be at least the minimum required by track speed limit.")

    def test_non_overtaking(self):
        # Test to explicitly check non-overtaking constraints on same track.
        n = 3
        tracks = [
            (0, 1, 2, 100, 50),   # travel time: 2.0 hours, capacity 2
            (1, 2, 2, 100, 50)    # travel time: 2.0 hours, capacity 2
        ]
        trains = [
            (0, 2, 0.0, 10, [0, 1, 2]),
            (0, 2, 0.0, 5, [0, 1, 2])
        ]
        result = schedule_trains(n, tracks, trains)
        self.assertIsNotNone(result, "Schedule should exist even with same earliest departure times.")
        for idx, train in enumerate(trains):
            times = result[idx]
            self.check_increasing(times)
            self.check_earliest_departure(train, times)
        self.check_track_capacity_and_overtaking(tracks, trains, result)

if __name__ == '__main__':
    unittest.main()