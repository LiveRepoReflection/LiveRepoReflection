import unittest
from traffic_events import aggregate_events

class TrafficEventsTest(unittest.TestCase):
    def setUp(self):
        # Configuration parameters for event detection
        self.radius = 5.0         # in kilometers
        self.time_window = 300      # in seconds (5 minutes)
        self.min_incidents = 2
        self.confidence_threshold = 0.5

    def test_empty_input(self):
        # Test with no incident reports
        reports = []
        events = aggregate_events(reports, self.radius, self.time_window, self.min_incidents, self.confidence_threshold)
        self.assertEqual(events, [])

    def test_single_incident_no_event(self):
        # Single incident should not form an event
        reports = [{
            'incident_id': 'inc1',
            'incident_type': 'accident',
            'location': (40.0, -74.0),
            'timestamp': 1609459200,
            'severity': 3,
            'source': 'sensorA',
            'confidence': 0.9
        }]
        events = aggregate_events(reports, self.radius, self.time_window, self.min_incidents, self.confidence_threshold)
        self.assertEqual(events, [])

    def test_valid_cluster_event(self):
        # Create a cluster of 3 incidents that are within the geographical and temporal thresholds.
        reports = [
            {
                'incident_id': 'inc1',
                'incident_type': 'accident',
                'location': (40.0, -74.0),
                'timestamp': 1609459200,
                'severity': 4,
                'source': 'sensorA',
                'confidence': 0.8
            },
            {
                'incident_id': 'inc2',
                'incident_type': 'accident',
                'location': (40.001, -74.001),
                'timestamp': 1609459210,
                'severity': 5,
                'source': 'sensorB',
                'confidence': 0.7
            },
            {
                'incident_id': 'inc3',
                'incident_type': 'road_closure',
                'location': (40.002, -74.002),
                'timestamp': 1609459220,
                'severity': 3,
                'source': 'sensorC',
                'confidence': 0.9
            }
        ]
        events = aggregate_events(reports, self.radius, self.time_window, self.min_incidents, self.confidence_threshold)
        self.assertEqual(len(events), 1)
        
        event = events[0]
        # Check incident_ids in the event match the reports provided
        self.assertCountEqual(event['incident_ids'], ['inc1', 'inc2', 'inc3'])
        # Check that start_time and end_time are correctly reflected
        self.assertEqual(event['start_time'], 1609459200)
        self.assertEqual(event['end_time'], 1609459220)
        # Most frequent incident type should be selected ('accident' appears twice)
        self.assertEqual(event['event_type'], 'accident')
        # Calculate expected centroid location (average of latitudes and longitudes)
        expected_lat = (40.0 + 40.001 + 40.002) / 3
        expected_lon = (-74.0 + -74.001 + -74.002) / 3
        self.assertAlmostEqual(event['location'][0], expected_lat, places=4)
        self.assertAlmostEqual(event['location'][1], expected_lon, places=4)
        # Check weighted severity based on confidence
        weighted_severity = (4 * 0.8 + 5 * 0.7 + 3 * 0.9) / (0.8 + 0.7 + 0.9)
        self.assertAlmostEqual(event['severity'], weighted_severity, places=4)
        # Verify that event_id is a non-empty string
        self.assertIsInstance(event['event_id'], str)
        self.assertTrue(len(event['event_id']) > 0)

    def test_multiple_clusters(self):
        # Create two separate clusters that should form two distinct events.
        reports = [
            # Cluster 1
            {
                'incident_id': 'inc1',
                'incident_type': 'accident',
                'location': (40.0, -74.0),
                'timestamp': 1609459200,
                'severity': 4,
                'source': 'sensorA',
                'confidence': 0.8
            },
            {
                'incident_id': 'inc2',
                'incident_type': 'accident',
                'location': (40.001, -74.001),
                'timestamp': 1609459220,
                'severity': 3,
                'source': 'sensorB',
                'confidence': 0.85
            },
            # Cluster 2
            {
                'incident_id': 'inc3',
                'incident_type': 'congestion',
                'location': (41.0, -75.0),
                'timestamp': 1609459300,
                'severity': 2,
                'source': 'sensorC',
                'confidence': 0.95
            },
            {
                'incident_id': 'inc4',
                'incident_type': 'congestion',
                'location': (41.002, -75.002),
                'timestamp': 1609459310,
                'severity': 2,
                'source': 'sensorD',
                'confidence': 0.9
            }
        ]
        events = aggregate_events(reports, self.radius, self.time_window, self.min_incidents, self.confidence_threshold)
        self.assertEqual(len(events), 2)
        
        # Identify clusters by incident_ids
        cluster1 = next(e for e in events if set(e['incident_ids']) == {'inc1', 'inc2'})
        cluster2 = next(e for e in events if set(e['incident_ids']) == {'inc3', 'inc4'})
        self.assertEqual(cluster1['event_type'], 'accident')
        self.assertEqual(cluster2['event_type'], 'congestion')

    def test_event_confidence_threshold(self):
        # Test that events not meeting the minimum average confidence threshold are discarded.
        reports = [
            {
                'incident_id': 'inc1',
                'incident_type': 'accident',
                'location': (40.0, -74.0),
                'timestamp': 1609459200,
                'severity': 4,
                'source': 'sensorA',
                'confidence': 0.2
            },
            {
                'incident_id': 'inc2',
                'incident_type': 'accident',
                'location': (40.0005, -74.0005),
                'timestamp': 1609459210,
                'severity': 5,
                'source': 'sensorB',
                'confidence': 0.3
            }
        ]
        events = aggregate_events(reports, self.radius, self.time_window, self.min_incidents, confidence_threshold=0.5)
        self.assertEqual(events, [])

if __name__ == '__main__':
    unittest.main()