import unittest
from datetime import datetime, timedelta
import json
from unittest.mock import patch, MagicMock

class TestEventAnalytics(unittest.TestCase):
    def setUp(self):
        self.sample_events = [
            {
                "device_id": "device1",
                "timestamp": int((datetime.now() - timedelta(hours=1)).timestamp()),
                "type": "temperature",
                "value": 25.5,
                "location": {"latitude": 34.0522, "longitude": -118.2437},
                "metadata": {"unit": "celsius"}
            },
            {
                "device_id": "device2",
                "timestamp": int((datetime.now() - timedelta(hours=2)).timestamp()),
                "type": "temperature",
                "value": 26.5,
                "location": {"latitude": 34.0523, "longitude": -118.2438},
                "metadata": {"unit": "celsius"}
            },
            {
                "device_id": "device1",
                "timestamp": int((datetime.now() - timedelta(hours=3)).timestamp()),
                "type": "pressure",
                "value": 1013.25,
                "location": {"latitude": 34.0522, "longitude": -118.2437},
                "metadata": {"unit": "hPa"}
            }
        ]

    def test_average_by_time_window(self):
        with patch('event_analytics.EventAnalytics') as MockEventAnalytics:
            mock_analytics = MockEventAnalytics.return_value
            start_time = int((datetime.now() - timedelta(hours=4)).timestamp())
            end_time = int(datetime.now().timestamp())
            
            mock_analytics.get_average_by_time_window.return_value = 25.5
            
            result = mock_analytics.get_average_by_time_window(
                device_id="device1",
                event_type="temperature",
                start_time=start_time,
                end_time=end_time
            )
            
            self.assertEqual(result, 25.5)
            mock_analytics.get_average_by_time_window.assert_called_once_with(
                device_id="device1",
                event_type="temperature",
                start_time=start_time,
                end_time=end_time
            )

    def test_top_k_devices(self):
        with patch('event_analytics.EventAnalytics') as MockEventAnalytics:
            mock_analytics = MockEventAnalytics.return_value
            start_time = int((datetime.now() - timedelta(hours=4)).timestamp())
            end_time = int(datetime.now().timestamp())
            
            expected_result = [("device1", 10), ("device2", 5)]
            mock_analytics.get_top_k_devices.return_value = expected_result
            
            result = mock_analytics.get_top_k_devices(
                k=2,
                event_type="temperature",
                start_time=start_time,
                end_time=end_time
            )
            
            self.assertEqual(result, expected_result)
            mock_analytics.get_top_k_devices.assert_called_once_with(
                k=2,
                event_type="temperature",
                start_time=start_time,
                end_time=end_time
            )

    def test_geospatial_aggregation(self):
        with patch('event_analytics.EventAnalytics') as MockEventAnalytics:
            mock_analytics = MockEventAnalytics.return_value
            start_time = int((datetime.now() - timedelta(hours=4)).timestamp())
            end_time = int(datetime.now().timestamp())
            
            mock_analytics.get_geospatial_average.return_value = 26.0
            
            result = mock_analytics.get_geospatial_average(
                event_type="temperature",
                min_lat=34.0,
                max_lat=35.0,
                min_lon=-119.0,
                max_lon=-118.0,
                start_time=start_time,
                end_time=end_time
            )
            
            self.assertEqual(result, 26.0)
            mock_analytics.get_geospatial_average.assert_called_once_with(
                event_type="temperature",
                min_lat=34.0,
                max_lat=35.0,
                min_lon=-119.0,
                max_lon=-118.0,
                start_time=start_time,
                end_time=end_time
            )

    def test_invalid_time_window(self):
        with patch('event_analytics.EventAnalytics') as MockEventAnalytics:
            mock_analytics = MockEventAnalytics.return_value
            start_time = int((datetime.now() + timedelta(hours=1)).timestamp())
            end_time = int((datetime.now() - timedelta(hours=1)).timestamp())
            
            mock_analytics.get_average_by_time_window.side_effect = ValueError("Invalid time window")
            
            with self.assertRaises(ValueError):
                mock_analytics.get_average_by_time_window(
                    device_id="device1",
                    event_type="temperature",
                    start_time=start_time,
                    end_time=end_time
                )

    def test_invalid_geospatial_bounds(self):
        with patch('event_analytics.EventAnalytics') as MockEventAnalytics:
            mock_analytics = MockEventAnalytics.return_value
            start_time = int((datetime.now() - timedelta(hours=4)).timestamp())
            end_time = int(datetime.now().timestamp())
            
            mock_analytics.get_geospatial_average.side_effect = ValueError("Invalid geographical bounds")
            
            with self.assertRaises(ValueError):
                mock_analytics.get_geospatial_average(
                    event_type="temperature",
                    min_lat=35.0,
                    max_lat=34.0,
                    min_lon=-118.0,
                    max_lon=-119.0,
                    start_time=start_time,
                    end_time=end_time
                )

    def test_invalid_k_value(self):
        with patch('event_analytics.EventAnalytics') as MockEventAnalytics:
            mock_analytics = MockEventAnalytics.return_value
            start_time = int((datetime.now() - timedelta(hours=4)).timestamp())
            end_time = int(datetime.now().timestamp())
            
            mock_analytics.get_top_k_devices.side_effect = ValueError("Invalid k value")
            
            with self.assertRaises(ValueError):
                mock_analytics.get_top_k_devices(
                    k=0,
                    event_type="temperature",
                    start_time=start_time,
                    end_time=end_time
                )

if __name__ == '__main__':
    unittest.main()