import unittest
import time

from sensor_anomaly import AnomalyDetector

class SensorAnomalyTest(unittest.TestCase):
    def setUp(self):
        # Initialize the anomaly detector with a fixed historical window and threshold.
        # Assume window_size defines how many past readings per sensor are maintained
        # and threshold defines the minimum anomaly score needed to trigger an alert.
        self.detector = AnomalyDetector(window_size=5, threshold=2.0)

    def test_normal_behavior(self):
        # Feed a series of normal readings for a sensor and verify no anomaly is reported.
        sensor_id = "sensor_normal"
        base_time = int(time.time())
        normal_readings = [10.0, 10.1, 9.9, 10.2, 10.0, 10.1, 10.05]
        alerts = []
        for i, value in enumerate(normal_readings):
            timestamp = base_time + i
            alert = self.detector.process_reading(sensor_id, timestamp, value)
            if alert is not None:
                alerts.append(alert)
        self.assertEqual(len(alerts), 0, msg="No alerts should be generated for normal behavior")

    def test_spike_detection(self):
        # Feed several normal readings and then a sudden spike; expect an anomaly alert.
        sensor_id = "sensor_spike"
        base_time = int(time.time())
        # Normal readings to fill initial historical window.
        for i, value in enumerate([20.0, 20.1, 19.9, 20.0, 20.05]):
            timestamp = base_time + i
            self.detector.process_reading(sensor_id, timestamp, value)
        # Introduce an anomalous spike.
        spike_timestamp = base_time + 6
        spike_value = 30.0
        alert = self.detector.process_reading(sensor_id, spike_timestamp, spike_value)
        self.assertIsNotNone(alert, msg="A spike should have generated an alert")
        # Check that the alert has the correct sensor_id, timestamp and value.
        self.assertEqual(alert[0], sensor_id)
        self.assertEqual(alert[1], spike_timestamp)
        self.assertEqual(alert[2], spike_value)
        self.assertGreaterEqual(alert[3], 2.0, msg="Anomaly score should meet or exceed the threshold")

    def test_cold_start(self):
        # Test the behavior when historical data is not available (cold start).
        sensor_id = "sensor_cold"
        base_time = int(time.time())
        # Provide fewer than required historical readings.
        # Even if an anomalous reading is provided, the detector may bootstrap and not generate an alert.
        for i, value in enumerate([50.0, 50.1]):
            timestamp = base_time + i
            alert = self.detector.process_reading(sensor_id, timestamp, value)
            self.assertIsNone(alert, msg="Cold start: insufficient data should not generate an alert")
        # Now provide enough data and then a spike.
        for i, value in enumerate([50.0, 50.05, 50.1], start=2):  # total 5 readings now
            timestamp = base_time + i
            self.detector.process_reading(sensor_id, timestamp, value)
        spike_timestamp = base_time + 6
        spike_value = 55.0
        alert = self.detector.process_reading(sensor_id, spike_timestamp, spike_value)
        # With sufficient historical data, an anomalous reading should trigger an alert.
        self.assertIsNotNone(alert, msg="Cold start sensor, after bootstrapping, should detect anomaly on spike")
        self.assertEqual(alert[0], sensor_id)

    def test_missing_data(self):
        # Test that the detector handles missing or None values gracefully.
        sensor_id = "sensor_missing"
        base_time = int(time.time())
        readings = [15.0, None, 15.1, 15.05, None, 15.0]
        alerts = []
        for i, value in enumerate(readings):
            timestamp = base_time + i
            try:
                alert = self.detector.process_reading(sensor_id, timestamp, value)
                # We expect that None values are either skipped internally or do not trigger alerts.
                if alert is not None:
                    alerts.append(alert)
            except Exception as e:
                self.fail(f"Processing missing data (None value) should not raise exception: {e}")
        # Under normal conditions, no anomalies should be triggered by missing data.
        self.assertEqual(len(alerts), 0, msg="Missing data should be handled gracefully without false alerts")
        
    def test_multiple_sensors(self):
        # Test the detection mechanism when handling multiple sensors concurrently.
        base_time = int(time.time())
        sensor_ids = ["s1", "s2", "s3"]
        normal_values = {
            "s1": [100.0, 100.1, 99.9, 100.0, 100.05],
            "s2": [200.0, 200.2, 199.8, 200.0, 200.1],
            "s3": [300.0, 300.1, 299.9, 300.0, 300.2]
        }
        alert_counts = {s: 0 for s in sensor_ids}
        
        # First, feed normal data to all sensors.
        for t in range(5):
            for sensor in sensor_ids:
                value = normal_values[sensor][t]
                alert = self.detector.process_reading(sensor, base_time + t, value)
                if alert is not None:
                    alert_counts[sensor] += 1
        # No alerts should be generated in normal conditions.
        for sensor in sensor_ids:
            self.assertEqual(alert_counts[sensor], 0, msg=f"No alert expected for sensor {sensor} under normal conditions")
        
        # Now inject an anomaly for sensor s2.
        spike_timestamp = base_time + 6
        spike_value = 210.0  # Significant deviation for sensor s2.
        alert = self.detector.process_reading("s2", spike_timestamp, spike_value)
        self.assertIsNotNone(alert, msg="Sensor s2 should trigger an alert for anomalous spike")
        self.assertEqual(alert[0], "s2")
        # For s1 and s3, even if we send slightly off normal values, no alerts.
        no_alert = self.detector.process_reading("s1", spike_timestamp, 100.2)
        self.assertIsNone(no_alert, msg="Sensor s1 should not trigger an alert for normal fluctuation")
        no_alert = self.detector.process_reading("s3", spike_timestamp, 300.05)
        self.assertIsNone(no_alert, msg="Sensor s3 should not trigger an alert for normal fluctuation")

if __name__ == '__main__':
    unittest.main()