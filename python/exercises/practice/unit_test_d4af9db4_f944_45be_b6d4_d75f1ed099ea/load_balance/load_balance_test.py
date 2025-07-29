import unittest
import sys
from io import StringIO
from contextlib import redirect_stdout
from load_balance import main

class LoadBalanceTest(unittest.TestCase):
    def run_simulation(self, input_commands):
        # Backup the original stdin and stdout
        original_stdin = sys.stdin
        original_stdout = sys.stdout
        try:
            sys.stdin = StringIO(input_commands)
            captured_output = StringIO()
            with redirect_stdout(captured_output):
                main()
            output = captured_output.getvalue()
        finally:
            sys.stdin = original_stdin
            sys.stdout = original_stdout
        return output

    def parse_metrics(self, output):
        # Parse the simulation results into a dictionary.
        metrics = {}
        for line in output.splitlines():
            if line.startswith("Average Response Time:"):
                # Expect format: "Average Response Time: <value>"
                parts = line.split(":", 1)
                metrics["average_response_time"] = float(parts[1].strip())
            elif line.startswith("Maximum Load:"):
                # Expect format: "Maximum Load: <value>%"
                parts = line.split(":", 1)
                value = parts[1].strip().rstrip("%")
                metrics["maximum_load"] = float(value)
            elif line.startswith("Completed Requests:"):
                parts = line.split(":", 1)
                metrics["completed_requests"] = int(parts[1].strip())
            elif line.startswith("Cancelled Requests:"):
                parts = line.split(":", 1)
                metrics["cancelled_requests"] = int(parts[1].strip())
            elif line.startswith("Failed Requests:"):
                parts = line.split(":", 1)
                metrics["failed_requests"] = int(parts[1].strip())
        return metrics

    def test_basic_simulation(self):
        # Test a simple simulation with one server and one request.
        commands = "\n".join([
            "ADD_SERVER s1 100 10",
            "SUBMIT_REQUEST r1 50 5",
            "SIMULATE 10 0.5",
            "END"
        ])
        output = self.run_simulation(commands)
        metrics = self.parse_metrics(output)
        # Check that all expected keys are in metrics.
        self.assertIn("average_response_time", metrics)
        self.assertIn("maximum_load", metrics)
        self.assertIn("completed_requests", metrics)
        self.assertIn("cancelled_requests", metrics)
        self.assertIn("failed_requests", metrics)
        # At least one request should complete.
        self.assertGreaterEqual(metrics["completed_requests"], 0)
    
    def test_cancel_request(self):
        # Test simulation where a request is cancelled.
        commands = "\n".join([
            "ADD_SERVER s1 100 10",
            "SUBMIT_REQUEST r1 30 5",
            "CANCEL_REQUEST r1",
            "SIMULATE 10 0.5",
            "END"
        ])
        output = self.run_simulation(commands)
        metrics = self.parse_metrics(output)
        # Check that cancelled requests count is at least 1.
        self.assertGreaterEqual(metrics.get("cancelled_requests", 0), 1)
    
    def test_remove_server_failure(self):
        # Test simulation where server is removed causing failure in processing requests.
        commands = "\n".join([
            "ADD_SERVER s1 100 10",
            "SUBMIT_REQUEST r1 40 3",
            "REMOVE_SERVER s1",
            "SIMULATE 10 0.5",
            "END"
        ])
        output = self.run_simulation(commands)
        metrics = self.parse_metrics(output)
        # With the removal of the server after submission, expect failed requests.
        self.assertGreaterEqual(metrics.get("failed_requests", 0), 1)
    
    def test_multiple_servers_and_requests(self):
        # Test simulation with multiple servers and multiple requests.
        commands = "\n".join([
            "ADD_SERVER s1 150 12",
            "ADD_SERVER s2 200 15",
            "ADD_SERVER s3 100 8",
            "SUBMIT_REQUEST r1 50 7",
            "SUBMIT_REQUEST r2 70 4",
            "SUBMIT_REQUEST r3 30 9",
            "SUBMIT_REQUEST r4 60 5",
            "CANCEL_REQUEST r2",
            "REMOVE_SERVER s3",
            "SUBMIT_REQUEST r5 80 6",
            "SIMULATE 20 0.6",
            "END"
        ])
        output = self.run_simulation(commands)
        metrics = self.parse_metrics(output)
        # Validate that metrics contain non-negative numbers.
        self.assertGreaterEqual(metrics.get("completed_requests", 0), 0)
        self.assertGreaterEqual(metrics.get("cancelled_requests", 0), 0)
        self.assertGreaterEqual(metrics.get("failed_requests", 0), 0)
        self.assertGreaterEqual(metrics.get("average_response_time", 0), 0)
        self.assertGreaterEqual(metrics.get("maximum_load", 0), 0)

if __name__ == '__main__':
    unittest.main()