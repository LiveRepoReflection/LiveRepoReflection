import unittest
import time
from load_balancer_sim import simulate_load_balancer

class TestLoadBalancerSim(unittest.TestCase):
    def setUp(self):
        # Base configuration for simulation tests.
        self.base_config = {
            "N": 5,
            "server_capacity": 10,
            "load_balancing_algorithm": "round_robin",
            "server_weights": [1, 1, 1, 1, 1],
            "queue_size": 5,
            "health_check_interval": 1,
            "request_arrival_rate": 10,  # requests per second
            "request_durations": [0.1] * 50,  # each request takes 0.1 seconds
            "simulation_time": 2  # run simulation for 2 seconds
        }

    def validate_metrics(self, metrics):
        # Validate general structure and types of metrics dictionary.
        self.assertIsInstance(metrics, dict)
        self.assertIn("avg_utilization", metrics)
        self.assertIn("avg_latency", metrics)
        self.assertIn("rejection_rate", metrics)
        self.assertIn("server_processed", metrics)
        self.assertIn("health_timeline", metrics)

        self.assertIsInstance(metrics["avg_utilization"], float)
        self.assertGreaterEqual(metrics["avg_utilization"], 0)
        self.assertLessEqual(metrics["avg_utilization"], 100)

        self.assertIsInstance(metrics["avg_latency"], float)
        self.assertGreaterEqual(metrics["avg_latency"], 0)

        self.assertIsInstance(metrics["rejection_rate"], float)
        self.assertGreaterEqual(metrics["rejection_rate"], 0)
        self.assertLessEqual(metrics["rejection_rate"], 100)

        self.assertIsInstance(metrics["server_processed"], dict)
        self.assertEqual(len(metrics["server_processed"]), self.base_config["N"])

        self.assertIsInstance(metrics["health_timeline"], list)
        for event in metrics["health_timeline"]:
            self.assertIn("time", event)
            self.assertIn("server_id", event)
            self.assertIn("status", event)
            self.assertIsInstance(event["time"], float)
            self.assertIsInstance(event["server_id"], int)
            self.assertTrue(event["status"] in ["down", "up"])

    def test_round_robin(self):
        config = self.base_config.copy()
        config["load_balancing_algorithm"] = "round_robin"
        metrics = simulate_load_balancer(config)
        self.validate_metrics(metrics)

    def test_least_connections(self):
        config = self.base_config.copy()
        config["load_balancing_algorithm"] = "least_connections"
        metrics = simulate_load_balancer(config)
        self.validate_metrics(metrics)

    def test_weighted_round_robin(self):
        config = self.base_config.copy()
        config["load_balancing_algorithm"] = "weighted_round_robin"
        # Use unbalanced weights to see effect on distribution.
        config["server_weights"] = [5, 1, 1, 1, 1]
        metrics = simulate_load_balancer(config)
        self.validate_metrics(metrics)

    def test_consistent_hashing(self):
        config = self.base_config.copy()
        config["load_balancing_algorithm"] = "consistent_hashing"
        metrics = simulate_load_balancer(config)
        self.validate_metrics(metrics)

    def test_no_queue(self):
        config = self.base_config.copy()
        # Set queue size to 0 to disable request queuing.
        config["queue_size"] = 0
        metrics = simulate_load_balancer(config)
        self.validate_metrics(metrics)
        # Since there is no queuing, expect possibility of higher rejection rate.
        self.assertGreaterEqual(metrics["rejection_rate"], 0)

    def test_high_load(self):
        config = self.base_config.copy()
        # Increase the arrival rate to simulate high load.
        config["request_arrival_rate"] = 100
        config["simulation_time"] = 3
        # Increase the request durations to simulate heavy processing.
        config["request_durations"] = [0.5] * 300
        metrics = simulate_load_balancer(config)
        self.validate_metrics(metrics)
        # Under high load, it is reasonable to expect some rejection.
        self.assertGreater(metrics["rejection_rate"], 0)

    def test_invalid_configuration(self):
        config = self.base_config.copy()
        # Provide an invalid configuration (e.g., negative server capacity)
        config["server_capacity"] = -5
        with self.assertRaises(ValueError):
            simulate_load_balancer(config)

if __name__ == '__main__':
    unittest.main()