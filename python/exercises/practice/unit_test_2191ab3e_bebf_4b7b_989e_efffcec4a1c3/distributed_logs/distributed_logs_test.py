import unittest
import time
from distributed_logs import ingest_log, query_logs, clear_logs

class DistributedLogsTest(unittest.TestCase):
    def setUp(self):
        clear_logs()
        # Prepare sample logs
        self.log_entries = [
            {
                "timestamp": 1609459200000,
                "service_name": "auth_service",
                "log_level": "INFO",
                "message": "User login successful",
                "trace_id": "trace_1",
                "metadata": {"ip": "192.168.1.1", "region": "us-east"}
            },
            {
                "timestamp": 1609459201000,
                "service_name": "auth_service",
                "log_level": "ERROR",
                "message": "User login failed",
                "trace_id": "trace_2",
                "metadata": {"ip": "192.168.1.2", "region": "us-west"}
            },
            {
                "timestamp": 1609459202000,
                "service_name": "payment_service",
                "log_level": "WARN",
                "message": "Payment delayed",
                "trace_id": "trace_3",
                "metadata": {"order_id": 1234, "amount": 99.99}
            },
            {
                "timestamp": 1609459203000,
                "service_name": "inventory_service",
                "log_level": "INFO",
                "message": "Inventory updated for product 5678",
                "trace_id": None,
                "metadata": {"product_id": 5678}
            },
            {
                "timestamp": 1609459204000,
                "service_name": "auth_service",
                "log_level": "DEBUG",
                "message": "Detailed auth debug message",
                "trace_id": "trace_4",
                "metadata": {}
            },
            {
                "timestamp": 1609459205000,
                "service_name": "payment_service",
                "log_level": "ERROR",
                "message": "Payment failed due to insufficient funds",
                "trace_id": "trace_5",
                "metadata": {"order_id": 1235, "reason": "insufficient funds"}
            }
        ]
        for log in self.log_entries:
            ingest_log(log)

    def test_ingestion_and_query_by_service(self):
        # Query logs for auth_service
        result = query_logs(service_name="auth_service")
        self.assertEqual(len(result), 3)
        for log in result:
            self.assertEqual(log["service_name"], "auth_service")

    def test_query_by_timestamp_range(self):
        # Query logs between 1609459201000 and 1609459203000 inclusive
        result = query_logs(timestamp_range=(1609459201000, 1609459203000))
        expected_timestamps = {1609459201000, 1609459202000, 1609459203000}
        result_timestamps = set(log["timestamp"] for log in result)
        self.assertEqual(result_timestamps, expected_timestamps)

    def test_query_by_log_level(self):
        # Query logs with log_level ERROR and WARN
        result = query_logs(log_level=["ERROR", "WARN"])
        expected_levels = {"ERROR", "WARN"}
        for log in result:
            self.assertIn(log["log_level"], expected_levels)
        self.assertEqual(len(result), 3)

    def test_query_by_message_contains(self):
        # Case-insensitive search: 'login'
        result = query_logs(message_contains="login")
        self.assertEqual(len(result), 2)
        for log in result:
            self.assertIn("login".lower(), log["message"].lower())

    def test_query_by_trace_id(self):
        # Query log with trace_id "trace_3"
        result = query_logs(trace_id="trace_3")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["trace_id"], "trace_3")

    def test_query_by_metadata_filter_exact_match(self):
        # Query logs where metadata "ip" equals "192.168.1.1"
        result = query_logs(metadata_filter={"ip": "192.168.1.1"})
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["metadata"].get("ip"), "192.168.1.1")

    def test_query_by_metadata_filter_null_value(self):
        # Query logs where metadata has key "nonexistent" with null value,
        # meaning the log does not have that key.
        result = query_logs(metadata_filter={"nonexistent": None})
        # All logs that do not have the key "nonexistent" should be returned.
        # In our sample, all logs do not contain 'nonexistent'
        self.assertEqual(len(result), len(self.log_entries))

    def test_pagination(self):
        # Query all logs with page_size 2, then check pagination results.
        result_page_1 = query_logs(page=1, page_size=2)
        result_page_2 = query_logs(page=2, page_size=2)
        result_page_3 = query_logs(page=3, page_size=2)
        self.assertEqual(len(result_page_1), 2)
        self.assertEqual(len(result_page_2), 2)
        self.assertEqual(len(result_page_3), 2)
        all_logs = result_page_1 + result_page_2 + result_page_3
        self.assertEqual(len(all_logs), len(self.log_entries))
        # Ensure no duplicates by checking unique timestamps
        timestamps = [log["timestamp"] for log in all_logs]
        self.assertEqual(len(set(timestamps)), len(timestamps))

    def test_combined_filters(self):
        # Query logs from auth_service with log_level ERROR in a timestamp range,
        # having a message that contains "failed"
        result = query_logs(
            service_name="auth_service",
            log_level=["ERROR"],
            timestamp_range=(1609459200000, 1609459205000),
            message_contains="failed"
        )
        self.assertEqual(len(result), 1)
        log = result[0]
        self.assertEqual(log["service_name"], "auth_service")
        self.assertEqual(log["log_level"], "ERROR")
        self.assertIn("failed", log["message"].lower())

    def test_no_matching_logs(self):
        # Query with criteria that match no logs.
        result = query_logs(
            service_name="nonexistent_service",
            message_contains="this should not exist"
        )
        self.assertEqual(len(result), 0)

if __name__ == '__main__':
    unittest.main()