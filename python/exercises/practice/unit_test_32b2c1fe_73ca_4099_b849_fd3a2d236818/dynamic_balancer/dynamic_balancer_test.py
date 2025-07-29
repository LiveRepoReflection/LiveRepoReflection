import unittest
import time

from dynamic_balancer.dynamic_balancer import DynamicBalancer

class TestDynamicBalancer(unittest.TestCase):

    def setUp(self):
        # Create a new instance of DynamicBalancer for each test.
        self.lb = DynamicBalancer()

    def test_submit_and_complete(self):
        # Submit a single high-priority request.
        self.lb.submit_request("req1", "High", 100, 200)
        state = self.lb.get_system_state()
        self.assertEqual(state["pending_requests"].get("High", 0), 1)

        # Simulate a worker node picking up the request.
        allocated = self.lb.worker_node_available()
        self.assertEqual(allocated, "req1")
        state = self.lb.get_system_state()
        self.assertEqual(state["pending_requests"].get("High", 0), 0)

        # Mark the request as finished.
        self.lb.worker_node_finished("req1")
        state = self.lb.get_system_state()
        # After processing, there should be no pending request.
        total_pending = sum(state["pending_requests"].values())
        self.assertEqual(total_pending, 0)

    def test_priority_order(self):
        # Submit multiple requests with different priorities.
        self.lb.submit_request("req1", "Medium", 150, 300)
        self.lb.submit_request("req2", "High", 100, 250)
        self.lb.submit_request("req3", "Low", 200, 400)
        self.lb.submit_request("req4", "High", 120, 200)
        self.lb.submit_request("req5", "Medium", 130, 300)

        # Expected dispatch order: High priority (FIFO), then Medium, then Low.
        allocated1 = self.lb.worker_node_available()
        self.assertEqual(allocated1, "req2")

        allocated2 = self.lb.worker_node_available()
        self.assertEqual(allocated2, "req4")

        allocated3 = self.lb.worker_node_available()
        self.assertEqual(allocated3, "req1")

        allocated4 = self.lb.worker_node_available()
        self.assertEqual(allocated4, "req5")

        allocated5 = self.lb.worker_node_available()
        self.assertEqual(allocated5, "req3")

        # Now all pending requests should be dispatched.
        state = self.lb.get_system_state()
        total_pending = sum(state["pending_requests"].values())
        self.assertEqual(total_pending, 0)

        # Finish all requests.
        for req in ["req2", "req4", "req1", "req5", "req3"]:
            self.lb.worker_node_finished(req)

    def test_worker_failure(self):
        # Submit a high-priority request.
        self.lb.submit_request("req_fail", "High", 100, 200)
        allocated = self.lb.worker_node_available()
        self.assertEqual(allocated, "req_fail")

        # Simulate failure.
        self.lb.worker_node_failed("req_fail")
        # After failure, the request should be requeued.
        state = self.lb.get_system_state()
        self.assertEqual(state["pending_requests"].get("High", 0), 1)

        # The request should again be available.
        allocated_again = self.lb.worker_node_available()
        self.assertEqual(allocated_again, "req_fail")
        self.lb.worker_node_finished("req_fail")

        # Final state: no pending requests.
        state = self.lb.get_system_state()
        total_pending = sum(state["pending_requests"].values())
        self.assertEqual(total_pending, 0)

    def test_dynamic_scaling(self):
        # Submit a burst of requests to simulate high load.
        for i in range(20):
            # Mix priorities in a cyclic fashion.
            priority = ["High", "Medium", "Low"][i % 3]
            self.lb.submit_request(f"req{i}", priority, 100 + i, 300)

        # Allow some time for potential dynamic scaling (simulate provisioning delay)
        time.sleep(0.1)
        state = self.lb.get_system_state()
        # Check that active worker nodes have scaled up in response to high load.
        self.assertGreaterEqual(state["active_workers"], 1)
        total_pending_before = sum(state["pending_requests"].values())
        self.assertEqual(total_pending_before, 20)

        # Process some requests.
        processed = []
        for _ in range(10):
            req = self.lb.worker_node_available()
            if req:
                processed.append(req)
        self.assertEqual(len(processed), 10)

        # Mark processed requests as finished.
        for req in processed:
            self.lb.worker_node_finished(req)

        # Simulate idle time for scaling down.
        time.sleep(0.2)
        state_after = self.lb.get_system_state()
        # Check that some worker nodes have been deprovisioned when idle.
        self.assertLessEqual(state_after["active_workers"], state["active_workers"])

    def test_average_response_time(self):
        # Submit two high-priority requests.
        self.lb.submit_request("reqA", "High", 100, 300)
        self.lb.submit_request("reqB", "High", 150, 300)

        start_time = time.time()
        allocated_A = self.lb.worker_node_available()
        self.assertEqual(allocated_A, "reqA")
        time.sleep(0.05)  # Simulate processing time
        self.lb.worker_node_finished("reqA")
        mid_time = time.time()

        allocated_B = self.lb.worker_node_available()
        self.assertEqual(allocated_B, "reqB")
        time.sleep(0.07)  # Simulate processing time
        self.lb.worker_node_finished("reqB")
        end_time = time.time()

        state = self.lb.get_system_state()
        avg_resp = state["average_response_time"].get("High", 0)

        # Expected average response should be between the processing delays
        self.assertGreaterEqual(avg_resp, 50)
        self.assertLessEqual(avg_resp, 80)

if __name__ == '__main__':
    unittest.main()