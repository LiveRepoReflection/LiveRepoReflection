import unittest
from unittest.mock import patch, MagicMock
import logging
import sys
from io import StringIO
from saga_orchestrator import execute_saga, TransactionStep

class TestSagaOrchestrator(unittest.TestCase):
    @patch('requests.post')
    def test_successful_saga(self, mock_post):
        # Configure the mock to return a successful response
        mock_response = MagicMock()
        mock_response.json.return_value = True
        mock_post.return_value = mock_response

        # Create a simple saga with two steps
        saga = [
            TransactionStep("service1", "http://service1/commit", "http://service1/compensate", {"action": "create"}),
            TransactionStep("service2", "http://service2/commit", "http://service2/compensate", {"action": "update"})
        ]
        
        # Execute the saga
        result = execute_saga(saga, "txn-123")
        
        # Verify the result
        self.assertTrue(result)
        
        # Verify that the commit endpoints were called with correct parameters
        expected_calls = [
            unittest.mock.call("http://service1/commit", json={"transaction_id": "txn-123", "data": {"action": "create"}}),
            unittest.mock.call("http://service2/commit", json={"transaction_id": "txn-123", "data": {"action": "update"}})
        ]
        self.assertEqual(mock_post.call_args_list, expected_calls)

    @patch('requests.post')
    def test_failed_commit_with_compensation(self, mock_post):
        # Configure the mock to simulate a failed commit on the second service
        def side_effect(url, json):
            mock_response = MagicMock()
            if url == "http://service1/commit":
                mock_response.json.return_value = True
            elif url == "http://service2/commit":
                mock_response.json.return_value = False
            elif url == "http://service1/compensate":
                mock_response.json.return_value = True
            return mock_response
        
        mock_post.side_effect = side_effect

        # Create a simple saga with two steps
        saga = [
            TransactionStep("service1", "http://service1/commit", "http://service1/compensate", {"action": "create"}),
            TransactionStep("service2", "http://service2/commit", "http://service2/compensate", {"action": "update"})
        ]
        
        # Execute the saga
        result = execute_saga(saga, "txn-123")
        
        # Verify the result
        self.assertFalse(result)
        
        # Verify that the commit and compensate endpoints were called with correct parameters
        expected_calls = [
            unittest.mock.call("http://service1/commit", json={"transaction_id": "txn-123", "data": {"action": "create"}}),
            unittest.mock.call("http://service2/commit", json={"transaction_id": "txn-123", "data": {"action": "update"}}),
            unittest.mock.call("http://service1/compensate", json={"transaction_id": "txn-123", "data": {"action": "create"}})
        ]
        self.assertEqual(mock_post.call_args_list, expected_calls)

    @patch('requests.post')
    def test_network_error_during_commit(self, mock_post):
        # Configure the mock to simulate a network error on the second service
        def side_effect(url, json):
            if url == "http://service1/commit":
                mock_response = MagicMock()
                mock_response.json.return_value = True
                return mock_response
            elif url == "http://service2/commit":
                raise Exception("Network error")
            elif url == "http://service1/compensate":
                mock_response = MagicMock()
                mock_response.json.return_value = True
                return mock_response
        
        mock_post.side_effect = side_effect

        # Create a simple saga with two steps
        saga = [
            TransactionStep("service1", "http://service1/commit", "http://service1/compensate", {"action": "create"}),
            TransactionStep("service2", "http://service2/commit", "http://service2/compensate", {"action": "update"})
        ]
        
        # Execute the saga
        result = execute_saga(saga, "txn-123")
        
        # Verify the result
        self.assertFalse(result)
        
        # Verify that compensation was called for service1
        expected_calls = [
            unittest.mock.call("http://service1/commit", json={"transaction_id": "txn-123", "data": {"action": "create"}}),
            unittest.mock.call("http://service2/commit", json={"transaction_id": "txn-123", "data": {"action": "update"}}),
            unittest.mock.call("http://service1/compensate", json={"transaction_id": "txn-123", "data": {"action": "create"}})
        ]
        self.assertEqual(len(mock_post.call_args_list), 3)
        self.assertEqual(mock_post.call_args_list[0], expected_calls[0])
        self.assertEqual(mock_post.call_args_list[2], expected_calls[2])

    @patch('requests.post')
    def test_compensation_failure(self, mock_post):
        # Configure the mock to simulate a failed commit on service2 and a failed compensation on service1
        def side_effect(url, json):
            mock_response = MagicMock()
            if url == "http://service1/commit":
                mock_response.json.return_value = True
            elif url == "http://service2/commit":
                mock_response.json.return_value = False
            elif url == "http://service1/compensate":
                raise Exception("Compensation failed")
            return mock_response
        
        mock_post.side_effect = side_effect

        # Set up logging capture
        log_capture = StringIO()
        handler = logging.StreamHandler(log_capture)
        logger = logging.getLogger()
        logger.addHandler(handler)
        previous_level = logger.level
        logger.setLevel(logging.ERROR)

        # Create a simple saga with two steps
        saga = [
            TransactionStep("service1", "http://service1/commit", "http://service1/compensate", {"action": "create"}),
            TransactionStep("service2", "http://service2/commit", "http://service2/compensate", {"action": "update"})
        ]
        
        # Execute the saga
        result = execute_saga(saga, "txn-123")
        
        # Verify the result
        self.assertFalse(result)
        
        # Verify that the commit and compensate endpoints were called
        expected_calls = [
            unittest.mock.call("http://service1/commit", json={"transaction_id": "txn-123", "data": {"action": "create"}}),
            unittest.mock.call("http://service2/commit", json={"transaction_id": "txn-123", "data": {"action": "update"}}),
            unittest.mock.call("http://service1/compensate", json={"transaction_id": "txn-123", "data": {"action": "create"}})
        ]
        self.assertEqual(len(mock_post.call_args_list), 3)
        self.assertEqual(mock_post.call_args_list[0], expected_calls[0])
        self.assertEqual(mock_post.call_args_list[1], expected_calls[1])
        self.assertEqual(mock_post.call_args_list[2], expected_calls[2])
        
        # Verify that the error was logged
        log_content = log_capture.getvalue()
        self.assertIn("Failed to compensate", log_content)
        
        # Restore the logger
        logger.removeHandler(handler)
        logger.setLevel(previous_level)

    @patch('requests.post')
    def test_multiple_services_saga(self, mock_post):
        # Configure the mock to simulate a successful saga with multiple services
        mock_response = MagicMock()
        mock_response.json.return_value = True
        mock_post.return_value = mock_response

        # Create a saga with several steps
        saga = [
            TransactionStep("service1", "http://service1/commit", "http://service1/compensate", {"action": "create"}),
            TransactionStep("service2", "http://service2/commit", "http://service2/compensate", {"action": "update"}),
            TransactionStep("service3", "http://service3/commit", "http://service3/compensate", {"action": "delete"}),
            TransactionStep("service4", "http://service4/commit", "http://service4/compensate", {"action": "process"})
        ]
        
        # Execute the saga
        result = execute_saga(saga, "txn-456")
        
        # Verify the result
        self.assertTrue(result)
        
        # Verify that all commit endpoints were called with correct parameters
        expected_calls = [
            unittest.mock.call("http://service1/commit", json={"transaction_id": "txn-456", "data": {"action": "create"}}),
            unittest.mock.call("http://service2/commit", json={"transaction_id": "txn-456", "data": {"action": "update"}}),
            unittest.mock.call("http://service3/commit", json={"transaction_id": "txn-456", "data": {"action": "delete"}}),
            unittest.mock.call("http://service4/commit", json={"transaction_id": "txn-456", "data": {"action": "process"}})
        ]
        self.assertEqual(mock_post.call_args_list, expected_calls)

    @patch('requests.post')
    def test_fail_in_middle_with_compensation(self, mock_post):
        # Configure the mock to simulate a failed commit in the middle with compensation
        def side_effect(url, json):
            mock_response = MagicMock()
            if url == "http://service1/commit" or url == "http://service2/commit":
                mock_response.json.return_value = True
            elif url == "http://service3/commit":
                mock_response.json.return_value = False
            else:  # All compensate calls
                mock_response.json.return_value = True
            return mock_response
        
        mock_post.side_effect = side_effect

        # Create a saga with several steps
        saga = [
            TransactionStep("service1", "http://service1/commit", "http://service1/compensate", {"action": "create"}),
            TransactionStep("service2", "http://service2/commit", "http://service2/compensate", {"action": "update"}),
            TransactionStep("service3", "http://service3/commit", "http://service3/compensate", {"action": "delete"}),
            TransactionStep("service4", "http://service4/commit", "http://service4/compensate", {"action": "process"})
        ]
        
        # Execute the saga
        result = execute_saga(saga, "txn-789")
        
        # Verify the result
        self.assertFalse(result)
        
        # Verify that the appropriate commit and compensate endpoints were called
        expected_calls = [
            unittest.mock.call("http://service1/commit", json={"transaction_id": "txn-789", "data": {"action": "create"}}),
            unittest.mock.call("http://service2/commit", json={"transaction_id": "txn-789", "data": {"action": "update"}}),
            unittest.mock.call("http://service3/commit", json={"transaction_id": "txn-789", "data": {"action": "delete"}}),
            unittest.mock.call("http://service2/compensate", json={"transaction_id": "txn-789", "data": {"action": "update"}}),
            unittest.mock.call("http://service1/compensate", json={"transaction_id": "txn-789", "data": {"action": "create"}})
        ]
        self.assertEqual(mock_post.call_args_list, expected_calls)

if __name__ == '__main__':
    unittest.main()