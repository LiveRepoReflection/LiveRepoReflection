import unittest
from time import time
from log_anomaly import CentralAnalysisSystem

class TestCentralAnalysisSystem(unittest.TestCase):
    def setUp(self):
        self.system = CentralAnalysisSystem(anomaly_threshold=0.5)

    def test_basic_anomaly_detection(self):
        current_time = int(time() * 1000)
        logs = [
            {
                "timestamp": current_time,
                "service_name": "auth-service",
                "log_level": "INFO",
                "message": "test",
                "metrics": {"cpu_usage": 0.9}
            }
        ]
        
        anomalies = self.system.process_logs(logs)
        self.assertEqual(len(anomalies), 1)
        self.assertEqual(anomalies[0]["service_name"], "auth-service")
        self.assertEqual(anomalies[0]["metric_name"], "cpu_usage")
        self.assertAlmostEqual(anomalies[0]["current_value"], 0.9)
        self.assertAlmostEqual(anomalies[0]["historical_average"], 0.0)
        self.assertAlmostEqual(anomalies[0]["difference"], 0.9)

    def test_no_anomaly_within_threshold(self):
        current_time = int(time() * 1000)
        logs = [
            {
                "timestamp": current_time,
                "service_name": "auth-service",
                "log_level": "INFO",
                "message": "test",
                "metrics": {"cpu_usage": 0.2}
            }
        ]
        
        anomalies = self.system.process_logs(logs)
        self.assertEqual(len(anomalies), 0)

    def test_sliding_window(self):
        base_time = int(time() * 1000)
        logs = [
            {
                "timestamp": base_time - 70000,  # Outside window
                "service_name": "auth-service",
                "log_level": "INFO",
                "message": "old",
                "metrics": {"cpu_usage": 0.9}
            },
            {
                "timestamp": base_time,  # Inside window
                "service_name": "auth-service",
                "log_level": "INFO",
                "message": "current",
                "metrics": {"cpu_usage": 0.2}
            }
        ]
        
        anomalies = self.system.process_logs(logs)
        self.assertEqual(len(anomalies), 0)  # Only the 0.2 value should be considered

    def test_multiple_metrics(self):
        current_time = int(time() * 1000)
        logs = [
            {
                "timestamp": current_time,
                "service_name": "auth-service",
                "log_level": "INFO",
                "message": "test",
                "metrics": {
                    "cpu_usage": 0.9,
                    "memory_usage": 0.95,
                    "latency": 1.0
                }
            }
        ]
        
        anomalies = self.system.process_logs(logs)
        self.assertEqual(len(anomalies), 3)  # Should detect anomalies for all metrics
        metrics = set(anomaly["metric_name"] for anomaly in anomalies)
        self.assertEqual(metrics, {"cpu_usage", "memory_usage", "latency"})

    def test_multiple_services(self):
        current_time = int(time() * 1000)
        logs = [
            {
                "timestamp": current_time,
                "service_name": "auth-service",
                "log_level": "INFO",
                "message": "test",
                "metrics": {"cpu_usage": 0.9}
            },
            {
                "timestamp": current_time,
                "service_name": "payment-service",
                "log_level": "INFO",
                "message": "test",
                "metrics": {"cpu_usage": 0.95}
            }
        ]
        
        anomalies = self.system.process_logs(logs)
        self.assertEqual(len(anomalies), 2)
        services = set(anomaly["service_name"] for anomaly in anomalies)
        self.assertEqual(services, {"auth-service", "payment-service"})

    def test_historical_average_update(self):
        current_time = int(time() * 1000)
        # First update
        logs1 = [
            {
                "timestamp": current_time,
                "service_name": "auth-service",
                "log_level": "INFO",
                "message": "test",
                "metrics": {"cpu_usage": 1.0}
            }
        ]
        self.system.process_logs(logs1)
        
        # Second update with same high value
        logs2 = [
            {
                "timestamp": current_time + 1000,
                "service_name": "auth-service",
                "log_level": "INFO",
                "message": "test",
                "metrics": {"cpu_usage": 1.0}
            }
        ]
        anomalies = self.system.process_logs(logs2)
        
        # The difference should be smaller due to updated historical average
        self.assertLess(anomalies[0]["difference"], 1.0)

    def test_invalid_metrics(self):
        current_time = int(time() * 1000)
        logs = [
            {
                "timestamp": current_time,
                "service_name": "auth-service",
                "log_level": "INFO",
                "message": "test",
                "metrics": {"cpu_usage": "invalid"}  # String instead of float
            }
        ]
        
        # Should not raise exception
        anomalies = self.system.process_logs(logs)
        self.assertEqual(len(anomalies), 0)

    def test_empty_metrics(self):
        current_time = int(time() * 1000)
        logs = [
            {
                "timestamp": current_time,
                "service_name": "auth-service",
                "log_level": "INFO",
                "message": "test",
                "metrics": {}
            }
        ]
        
        # Should not raise exception
        anomalies = self.system.process_logs(logs)
        self.assertEqual(len(anomalies), 0)

    def test_timestamp_ordering(self):
        current_time = int(time() * 1000)
        logs = [
            {
                "timestamp": current_time + 1000,  # Later timestamp
                "service_name": "auth-service",
                "log_level": "INFO",
                "message": "later",
                "metrics": {"cpu_usage": 0.2}
            },
            {
                "timestamp": current_time,  # Earlier timestamp
                "service_name": "auth-service",
                "log_level": "INFO",
                "message": "earlier",
                "metrics": {"cpu_usage": 0.9}
            }
        ]
        
        anomalies = self.system.process_logs(logs)
        if anomalies:  # If any anomalies are reported
            self.assertEqual(anomalies[0]["timestamp"], current_time + 1000)  # Most recent first

if __name__ == '__main__':
    unittest.main()