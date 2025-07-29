import unittest
from traffic_predictor import predict_traffic_flow

class TestTrafficPredictor(unittest.TestCase):

    def test_single_segment_no_events(self):
        # Test with one road segment, no events, constant historical data.
        N = 2
        edges = [(0, 1, 100)]
        current_traffic = [(0, 1, 40)]
        historical_data = {(0, 1): [40] * 672}
        events = []
        time_slices = [10]
        
        expected = {
            (0, 1, 10): 40
        }
        result = predict_traffic_flow(N, edges, current_traffic, historical_data, events, time_slices)
        # Check for correct keys and that values do not exceed capacity or fall below 0.
        for key, volume in result.items():
            u, v, t = key
            capacity = next(capacity for (u2, v2, capacity) in edges if u2 == u and v2 == v)
            self.assertGreaterEqual(volume, 0)
            self.assertLessEqual(volume, capacity)
        self.assertEqual(result, expected)

    def test_multiple_segments_with_positive_event(self):
        # Test multiple segments with one event that increases traffic for roads starting from a given node.
        N = 3
        edges = [(0, 1, 150), (1, 2, 200), (0, 2, 100)]
        current_traffic = [(0, 1, 50), (1, 2, 80), (0, 2, 30)]
        historical_data = {
            (0, 1): [50] * 672,
            (1, 2): [80] * 672,
            (0, 2): [30] * 672
        }
        # Event affects node 0 between 5 and 15 minutes with a 20% increase.
        events = [(5, 15, 0, 0.2)]
        # Two time slices: one during the event and one after.
        time_slices = [10, 20]
        
        # Using a baseline prediction model:
        # If an event is active for the originating node:
        #   predicted = min(capacity, int(baseline * (1 + impact_factor)))
        # Else:
        #   predicted = baseline
        # where baseline is taken as the constant value from historical_data/current_traffic.
        expected = {
            (0, 1, 10): min(150, int(50 * 1.2)),  # event active at time 10 for road from node 0.
            (0, 2, 10): min(100, int(30 * 1.2)),
            (1, 2, 10): 80,  # not affected by event.
            (0, 1, 20): 50,  # event inactive.
            (0, 2, 20): 30,
            (1, 2, 20): 80
        }
        result = predict_traffic_flow(N, edges, current_traffic, historical_data, events, time_slices)
        for key, volume in result.items():
            u, v, t = key
            capacity = next(cap for (u2, v2, cap) in edges if u2 == u and v2 == v)
            self.assertGreaterEqual(volume, 0)
            self.assertLessEqual(volume, capacity)
        self.assertEqual(result, expected)
        
    def test_single_segment_with_negative_event(self):
        # Test with one road segment and a negative event that reduces traffic.
        N = 2
        edges = [(0, 1, 100)]
        current_traffic = [(0, 1, 90)]
        historical_data = {(0, 1): [90] * 672}
        # Event affecting node 0 with a -50% reduction (traffic expected to be halved) from time 0 to 30.
        events = [(0, 30, 0, -0.5)]
        time_slices = [10, 40]
        
        # Expected:
        # At time 10, event is active: predicted = max(0, min(100, int(90 * (1 - 0.5))) = 45.
        # At time 40, event inactive: predicted = 90.
        expected = {
            (0, 1, 10): min(100, int(90 * 0.5)),
            (0, 1, 40): 90
        }
        result = predict_traffic_flow(N, edges, current_traffic, historical_data, events, time_slices)
        for key, volume in result.items():
            u, v, t = key
            capacity = next(capacity for (u2, v2, capacity) in edges if u2 == u and v2 == v)
            self.assertGreaterEqual(volume, 0)
            self.assertLessEqual(volume, capacity)
        self.assertEqual(result, expected)

if __name__ == '__main__':
    unittest.main()