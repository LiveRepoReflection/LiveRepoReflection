import unittest
from unittest.mock import patch
from xact_coord import TransactionCoordinator

class TestTransactionCoordinator(unittest.TestCase):

    def setUp(self):
        # Initialize the TransactionCoordinator with a timeout and max_retries parameter.
        self.coordinator = TransactionCoordinator(timeout=1.0, max_retries=2)

    @patch('xact_coord.TransactionCoordinator.send_request')
    def test_successful_commit(self, mock_send):
        # Simulate all service operations ("prepare" and "commit") succeeding.
        def side_effect(service_url, transaction_id, command):
            return True
        mock_send.side_effect = side_effect

        services = [
            {'url': 'http://inventory-service', 'operations': ['prepare', 'commit']},
            {'url': 'http://payment-service', 'operations': ['prepare', 'commit']},
            {'url': 'http://shipping-service', 'operations': ['prepare', 'commit']},
        ]

        result = self.coordinator.coordinate_transaction(services, transaction_id="txn123")
        self.assertEqual(result['status'], 'committed')
        # Verify that each operation was attempted.
        expected_calls = sum(len(s['operations']) for s in services)
        self.assertEqual(mock_send.call_count, expected_calls)

    @patch('xact_coord.TransactionCoordinator.send_request')
    def test_prepare_failure_triggers_rollback(self, mock_send):
        # Simulate failure in the "prepare" phase for one service, triggering a full rollback.
        def side_effect(service_url, transaction_id, command):
            if service_url == 'http://payment-service' and command == 'prepare':
                return False
            return True
        mock_send.side_effect = side_effect

        services = [
            {'url': 'http://inventory-service', 'operations': ['prepare', 'commit']},
            {'url': 'http://payment-service', 'operations': ['prepare', 'commit']},
            {'url': 'http://shipping-service', 'operations': ['prepare', 'commit']},
        ]

        result = self.coordinator.coordinate_transaction(services, transaction_id="txn124")
        self.assertEqual(result['status'], 'rolledback')
        # Check that rollback operation was eventually attempted.
        rollback_called = any(call.args[2] == 'rollback' for call in mock_send.call_args_list)
        self.assertTrue(rollback_called)

    @patch('xact_coord.TransactionCoordinator.send_request')
    def test_commit_failure_after_prepare(self, mock_send):
        # Simulate a failure in the "commit" phase after successful "prepare" stages.
        def side_effect(service_url, transaction_id, command):
            if service_url == 'http://shipping-service' and command == 'commit':
                return False
            return True
        mock_send.side_effect = side_effect

        services = [
            {'url': 'http://inventory-service', 'operations': ['prepare', 'commit']},
            {'url': 'http://payment-service', 'operations': ['prepare', 'commit']},
            {'url': 'http://shipping-service', 'operations': ['prepare', 'commit']},
        ]

        result = self.coordinator.coordinate_transaction(services, transaction_id="txn125")
        self.assertEqual(result['status'], 'rolledback')
        rollback_called = any(call.args[2] == 'rollback' for call in mock_send.call_args_list)
        self.assertTrue(rollback_called)

    @patch('xact_coord.TransactionCoordinator.send_request')
    def test_timeout_retry(self, mock_send):
        # Simulate temporary timeouts causing failures on the first call, followed by success on retry.
        call_counts = {}
        def side_effect(service_url, transaction_id, command):
            key = (service_url, command)
            call_counts[key] = call_counts.get(key, 0) + 1
            # Fail the first attempt, succeed on subsequent attempts.
            if call_counts[key] == 1:
                return False
            return True
        mock_send.side_effect = side_effect

        services = [
            {'url': 'http://inventory-service', 'operations': ['prepare', 'commit']},
            {'url': 'http://payment-service', 'operations': ['prepare', 'commit']},
        ]
        
        result = self.coordinator.coordinate_transaction(services, transaction_id="txn126")
        self.assertEqual(result['status'], 'committed')
        # Verify that retries occurred.
        self.assertTrue(any(count > 1 for count in call_counts.values()))

    @patch('xact_coord.TransactionCoordinator.send_request')
    def test_idempotency_duplicate_requests(self, mock_send):
        # Simulate duplicate requests for idempotent operations.
        def side_effect(service_url, transaction_id, command):
            return True
        mock_send.side_effect = side_effect

        services = [
            {'url': 'http://inventory-service', 'operations': ['prepare', 'prepare', 'commit']},
            {'url': 'http://payment-service', 'operations': ['prepare', 'commit', 'commit']},
        ]

        result = self.coordinator.coordinate_transaction(services, transaction_id="txn127")
        self.assertEqual(result['status'], 'committed')
        expected_calls = sum(len(s['operations']) for s in services)
        self.assertEqual(mock_send.call_count, expected_calls)

if __name__ == '__main__':
    unittest.main()